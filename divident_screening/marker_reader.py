#!/usr/bin/env python3
"""
Read a PDF with marker-pdf and output Markdown/JSON.

Strategies:
  --cpu           Force models onto CPU (frees VRAM entirely)
  --workers N     Parallel workers (CPU-only, uses spawn multiprocessing)

Without flags: single-process GPU mode (default marker behavior).
"""

import argparse
import json
import subprocess
import sys
import time
import os
import gc
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import torch
import fitz  # PyMuPDF

MARKER_CONFIG = {
    "languages": ["en"],
    "extract_images": False,
    "output_format": "markdown",
    "force_ocr": False,
    "paginate_output": True,
}

CHUNK_SIZE = 40
OVERLAP = 2
TEMP_DIR = "data/pdf/temp_chunks"


def get_chunks(pdf_path: str) -> list:
    """Split PDF into chunks, return list of (path, start_page, end_page)."""
    doc = fitz.open(pdf_path)
    total = len(doc)
    os.makedirs(TEMP_DIR, exist_ok=True)

    chunks = []
    for start in range(0, total, CHUNK_SIZE):
        end = min(start + CHUNK_SIZE + OVERLAP, total)
        path = os.path.join(TEMP_DIR, f"chunk_{start}_{end}.pdf")
        sub = fitz.open()
        sub.insert_pdf(doc, from_page=start, to_page=end - 1)
        sub.save(path)
        sub.close()
        chunks.append((path, start, end))
        if end == total:
            break
    doc.close()
    return chunks


def _convert_chunk_subprocess(chunk_path: str, out_path: str, fmt: str) -> None:
    """
    Run marker conversion in a completely independent subprocess.

    Avoids the 'daemonic processes cannot have children' problem because
    subprocess.run() creates a non-daemon OS process that is free to
    spawn its own child processes (as pdftext does internally).
    """
    config_repr = repr({**MARKER_CONFIG, "output_format": fmt})
    script = f"""\
import os, sys, json
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

config = {config_repr}
cp = ConfigParser(config)
converter = PdfConverter(
    config=cp.generate_config_dict(),
    artifact_dict=create_model_dict(),
    processor_list=cp.get_processors(),
    renderer=cp.get_renderer(),
)
rendered = converter({chunk_path!r})

if {fmt!r} == "json":
    result = json.dumps(rendered.children, ensure_ascii=False, default=str)
else:
    text, _, _ = text_from_rendered(rendered)
    result = text

with open({out_path!r}, "w", encoding="utf-8") as f:
    f.write(result)
"""
    proc = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Worker failed on {chunk_path}:\n{proc.stderr[-2000:]}"
        )


def run_serial(chunks: list, fmt: str, use_cpu: bool):
    """Single-process mode: load models once, process chunks sequentially."""
    if use_cpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    from marker.config.parser import ConfigParser
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered

    print("Initializing models...", file=sys.stderr)
    config = {**MARKER_CONFIG, "output_format": fmt}
    config_parser = ConfigParser(config)
    model_dict = create_model_dict()
    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=model_dict,
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
    )

    results = []
    for i, (chunk_path, start, end) in enumerate(chunks):
        print(f"--- Chunk {i+1}/{len(chunks)}: pages {start}-{end} ---", file=sys.stderr)
        rendered = converter(chunk_path)
        if fmt == "json":
            results.append(rendered.children)
        else:
            text, _, _ = text_from_rendered(rendered)
            results.append(text)
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        os.remove(chunk_path)

    return results


def run_parallel(chunks: list, fmt: str, workers: int):
    """
    Multi-process mode: each chunk runs as an independent subprocess.

    Uses ThreadPoolExecutor to manage concurrency — threads just wait
    for subprocesses, so GIL is not an issue. Each subprocess is a
    full OS process (not daemon), free to spawn its own children.
    """
    print(f"Launching up to {workers} parallel workers (subprocess, CPU-only)...",
          file=sys.stderr)

    out_dir = os.path.join(TEMP_DIR, "out")
    os.makedirs(out_dir, exist_ok=True)

    out_paths = [os.path.join(out_dir, f"result_{i}.txt") for i in range(len(chunks))]

    def do_one(idx: int) -> int:
        chunk_path, start, end = chunks[idx]
        _convert_chunk_subprocess(chunk_path, out_paths[idx], fmt)
        os.remove(chunk_path)
        return idx

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(do_one, i): i for i in range(len(chunks))}
        for future in as_completed(futures):
            idx = future.result()
            _, start, end = chunks[idx]
            done = sum(1 for f in futures if not f.running())
            print(f"  completed chunk {idx+1} (pages {start}-{end}), "
                  f"{done}/{len(chunks)} done", file=sys.stderr)

    results = []
    for p in out_paths:
        with open(p, "r", encoding="utf-8") as f:
            results.append(f.read())
        os.remove(p)

    if os.path.exists(out_dir) and not os.listdir(out_dir):
        os.rmdir(out_dir)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Read a PDF with marker-pdf (GPU or parallel CPU)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # GPU (default, single process)
  python marker_reader.py report.pdf -o report.md

  # CPU single process (when VRAM is insufficient)
  python marker_reader.py report.pdf --cpu -o report.md

  # CPU parallel (maximize throughput with RAM/CPU)
  python marker_reader.py report.pdf --cpu --workers 4 -o report.md
""",
    )
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("-o", "--output", help="Write output to file instead of stdout")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--cpu", action="store_true", help="Force CPU-only (no VRAM needed)")
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of parallel workers (implies --cpu, default: 1)")
    args = parser.parse_args()

    if args.workers > 1:
        args.cpu = True

    fmt = "json" if args.json else "markdown"
    device = "CPU" if args.cpu else "GPU"
    print(f"Mode: {device}, workers={args.workers}, format={fmt}", file=sys.stderr)

    print(f"Splitting {args.pdf} into chunks...", file=sys.stderr)
    chunks = get_chunks(args.pdf)
    print(f"  {len(chunks)} chunks (chunk_size={CHUNK_SIZE}, overlap={OVERLAP})", file=sys.stderr)

    t0 = time.time()

    if args.workers > 1:
        results = run_parallel(chunks, fmt, args.workers)
    else:
        results = run_serial(chunks, fmt, args.cpu)

    elapsed = time.time() - t0
    print(f"Total processing time: {elapsed:.1f}s", file=sys.stderr)

    if args.json:
        output = json.dumps(results, ensure_ascii=False, indent=2, default=str)
    else:
        output = "\n\n".join(results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)

    if os.path.exists(TEMP_DIR) and not os.listdir(TEMP_DIR):
        os.rmdir(TEMP_DIR)


if __name__ == "__main__":
    main()