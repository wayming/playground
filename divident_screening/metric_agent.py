#!/usr/bin/env python3
"""
Metric Agent — 独立的单指标提取模块 (4-step RAG pipeline)

Workflow:
    Step 1: LLM + Google Search → find PDF URL
    Step 2: Download PDF to local cache
    Step 3: PyMuPDF + ParentDocumentRetriever (Google Embeddings + FAISS) → relevant chunks
    Step 4: LLM + actual PDF text → extract metric

Public API:
    compute_metric(ticker, field, doc_hint) -> MetricResult
"""

import hashlib
import json
import os
import re
import datetime
import requests
import pprint
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict, Tuple

import google.genai as genai
import pymupdf, pdfplumber
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from logger import logger, set_ticker

MODEL_NAME = "gemini-3.1-flash-lite-preview"
EMBEDDING_MODEL = "models/gemini-embedding-2-preview"

TODAY = datetime.date.today()
THIS_YEAR = TODAY.year
LAST_YEAR = THIS_YEAR - 1

PDF_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pdf")
os.makedirs(PDF_CACHE_DIR, exist_ok=True)

MAX_CONTEXT_CHARS = 30_000
CHILD_CHUNK_SIZE = 500
CHILD_CHUNK_OVERLAP = 50
TOP_K_CHUNKS = 8
EMBED_WORKERS = 20


# ── Output schema ────────────────────────────────────────────────

class MetricResult(BaseModel):
    """Structured result returned by compute_metric()."""
    field: str
    value: Optional[float] = Field(default=None, description="Extracted numeric value")
    unit: str = Field(default="", description='Unit, e.g. "%", "Mt", "years", "AUD M"')
    period: str = Field(default="", description='Reporting period, e.g. "FY 2025"')
    source: str = Field(default="", description="URL or document the data was found in")
    raw_response: str = Field(default="", description="Raw LLM response for debugging")


# ── LLM / Embeddings setup ───────────────────────────────────────

def _get_api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", "")


def _get_llm_json() -> Optional[ChatGoogleGenerativeAI]:
    """LLM configured for JSON output (Step 1: search)."""
    api_key = _get_api_key()
    if not api_key:
        logger.warning("GEMINI_API_KEY not set")
        return None
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=api_key,
        temperature=0.1,
        max_output_tokens=4096,
        response_mime_type="application/json",
    )
    return llm.bind_tools([{"google_search": {}}])


def _get_llm_text() -> Optional[ChatGoogleGenerativeAI]:
    """LLM configured for JSON output (Step 4: extraction)."""
    api_key = _get_api_key()
    if not api_key:
        return None
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=api_key,
        temperature=0.1,
        max_output_tokens=8192,
        response_mime_type="application/json",
    )


def _get_embeddings() -> Optional[GoogleGenerativeAIEmbeddings]:
    api_key = _get_api_key()
    if not api_key:
        return None
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=api_key,
    )


# ── Shared helpers ────────────────────────────────────────────────

def _call_llm(prompt: str, llm) -> Optional[str]:
    """Send prompt to Gemini, return raw text content."""
    try:
        logger.debug(f"Prompt:\n{prompt}")
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content if hasattr(response, "content") else str(response)

        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict) and "text" in first:
                content = first["text"]
            else:
                content = str(first)
        elif isinstance(content, list):
            content = ""
            
        logger.debug(f"Response:\n{content}")
        return content
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None


def _parse_json(raw: str) -> dict:
    """Extract the first JSON object from raw text."""
    if not raw:
        return {}
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return {}
    try:
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error: {e}")
        return {}


def _safe_float(v) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ── Step 1: Search PDF URL ────────────────────────────────────────

def _build_search_prompt(ticker: str, field: str, doc_hint: str) -> str:
    return f"""\
#######################################################
# Role
You are a financial document search specialist for ASX-listed companies.

# Task
Find the direct PDF URL for the document described below.
Today is {TODAY}. Only consider documents from {LAST_YEAR} to {TODAY}.

Ticker: {ticker}
Search guidance: {doc_hint}

# Steps
1. Use Google Search to find the investor relations page for {ticker}.
2. Locate the most relevant PDF document (annual report, quarterly report,
   investor presentation, etc.)
3. Return the direct PDF link.

# Output
Provide the URL in the following format
{{"url": "<direct PDF URL or empty string if not found>"}}

# Constraints
- Must be a real, verifiable URL. Do NOT fabricate URLs.
- Prefer direct PDF links (ending in .pdf) over HTML pages.
- If no PDF can be found, return {{"url": ""}}.
#######################################################
"""


def _search_pdf_url(ticker: str, field: str, doc_hint: str, llm) -> Optional[str]:
    """Step 1: Ask LLM to find the PDF URL via Google Search."""
    prompt = _build_search_prompt(ticker, field, doc_hint)
    raw = _call_llm(prompt, llm)
    if not raw:
        logger.warning("Step 1: no response from LLM")
        return None

    data = _parse_json(raw)
    url = data.get("url", "")
    if url:
        logger.info(f"Step 1: found PDF URL → {url}")
        return url

    logger.warning(f"Step 1: no PDF URL found. Raw: {raw[:200]}")
    return None


# ── Step 2: Download PDF ──────────────────────────────────────────

def _download_pdf(url: str) -> Optional[str]:
    """Step 2: Download PDF to local cache. Returns file path or None."""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    cached_path = os.path.join(PDF_CACHE_DIR, f"{url_hash}.pdf")

    if os.path.exists(cached_path) and os.path.getsize(cached_path) > 1000:
        logger.info(f"Step 2: using cached PDF → {cached_path}")
        return cached_path

    logger.info(f"Step 2: downloading {url}")
    try:
        resp = requests.get(url, timeout=60, headers={
            "User-Agent": "Mozilla/5.0 (compatible; ASXScorer/1.0)"
        })
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")
        if "pdf" not in content_type and not url.lower().endswith(".pdf"):
            logger.warning(f"Step 2: not a PDF (Content-Type: {content_type})")
            return None

        with open(cached_path, "wb") as f:
            f.write(resp.content)

        logger.info(f"Step 2: saved PDF ({len(resp.content)} bytes) → {cached_path}")
        return cached_path

    except Exception as e:
        logger.error(f"Step 2: download failed: {e}")
        return None


# ── Step 3: RAG Retrieval ─────────────────────────────────────────

def _extract_tables_from_pdf(pdf_path: str) -> List[Document]:
    """Extract tables as structured text blocks."""
    docs = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for t_idx, table in enumerate(tables):
                if not table:
                    continue

                # 转成结构化文本
                rows = []
                for row in table:
                    clean_row = [str(cell).strip() if cell else "" for cell in row]
                    rows.append(" | ".join(clean_row))

                table_text = "\n".join(rows)

                if len(table_text) < 50:
                    continue

                docs.append(Document(
                    page_content=f"[TABLE]\n{table_text}",
                    metadata={
                        "page": i + 1,
                        "type": "table",
                        "table_id": t_idx
                    }
                ))
    logger.info(f"Step 3: extracted {len(docs)} tables")
    return docs

def _load_pdf_pages(pdf_path: str) -> List[Document]:
    """Extract text from each page as a LangChain Document."""
    docs = []
    with pymupdf.open(pdf_path) as pdf:
        for i, page in enumerate(pdf):
            text = page.get_text()
            if text.strip():
                docs.append(Document(
                    page_content=text,
                    metadata={"page": i + 1, "source": pdf_path},
                ))

    table_docs = _extract_tables_from_pdf(pdf_path)
    
    logger.info(f"Step 3: extracted {len(docs)} pages from PDF")
    return docs + table_docs


def _embed_single(client: genai.Client, text: str) -> List[float]:
    """Embed a single text using the Google genai SDK directly."""
    r = client.models.embed_content(model=EMBEDDING_MODEL, contents=text)
    return r.embeddings[0].values


def _build_faiss_index(
    chunks: List[Document],
    embeddings: GoogleGenerativeAIEmbeddings,
    progress_fn=None,
) -> Optional[FAISS]:
    """
    Build a FAISS index with concurrent embedding.

    gemini-embedding-2-preview returns only 1 vector per embed_documents()
    call regardless of input size, so we bypass LangChain and call the
    google.genai SDK directly with ThreadPoolExecutor for parallelism.
    The LangChain embeddings object is kept for similarity_search queries.
    """
    if not chunks:
        return None

    api_key = _get_api_key()
    if not api_key:
        return None
    client = genai.Client(api_key=api_key)

    texts = [c.page_content for c in chunks]
    metadatas = [c.metadata for c in chunks]

    vectors: List[Optional[List[float]]] = [None] * len(texts)
    done_count = 0

    with ThreadPoolExecutor(max_workers=EMBED_WORKERS) as executor:
        future_to_idx = {
            executor.submit(_embed_single, client, t): i
            for i, t in enumerate(texts)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            vectors[idx] = future.result()
            done_count += 1
            if progress_fn and done_count % 100 == 0:
                progress_fn(done_count, len(texts))

    if progress_fn:
        progress_fn(len(texts), len(texts))

    text_embeddings = [(texts[i], vectors[i]) for i in range(len(texts))]
    return FAISS.from_embeddings(
        text_embeddings=text_embeddings,
        embedding=embeddings,
        metadatas=metadatas,
    )


def _split_pages_to_chunks(parent_docs: List[Document]) -> List[Document]:
    """Split parent page documents into child chunks, preserving parent_page metadata."""
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHILD_CHUNK_SIZE,
        chunk_overlap=CHILD_CHUNK_OVERLAP,
    )
    all_chunks = []
    for parent in parent_docs:
        children = child_splitter.split_documents([parent])
        for child in children:
            child.metadata["parent_page"] = parent.metadata.get("page", 0)
        all_chunks.extend(children)
    return all_chunks


def _search_parent_pages(
    vectorstore: FAISS,
    query: str,
    parent_docs: List[Document],
    k: int = TOP_K_CHUNKS,
) -> List[Document]:
    """Search FAISS for child chunks, return deduplicated parent pages."""
    results = vectorstore.similarity_search_with_score(query, k=k)

    table_hits = []
    text_hits = []
    seen = set()

    for doc, score in results:
        page = doc.metadata.get("parent_page") or doc.metadata.get("page")

        if page in seen:
            continue
        seen.add(page)

        parent = next(
            (p for p in parent_docs if p.metadata.get("page") == page),
            None
        )

        if not parent:
            continue

        if "[TABLE]" in parent.page_content or parent.metadata.get("type") == "table":
            table_hits.append(parent)
        else:
            text_hits.append(parent)

    # 👉 优先用表格
    return table_hits[:5] + text_hits[:3]


def _retrieve_relevant_chunks(pdf_path: str, field: str, doc_hint: str) -> str:
    """
    Step 3: Semantic search over PDF pages.

    Approach:
    - Split each page into child chunks (~500 chars)
    - Embed each chunk via Google Embeddings API (one at a time)
    - Build FAISS index from pre-computed vectors
    - Query → find top-K child chunks → return their parent pages (deduplicated)
    """
    embeddings = _get_embeddings()
    if embeddings is None:
        logger.warning("Step 3: embeddings not available, falling back to first pages")
        return _fallback_first_pages(pdf_path)

    parent_docs = _load_pdf_pages(pdf_path)
    if not parent_docs:
        logger.warning("Step 3: no text extracted from PDF")
        return ""

    try:
        all_chunks = _split_pages_to_chunks(parent_docs)
        logger.info(f"Step 3: split into {len(all_chunks)} child chunks, embedding one-by-one")

        def log_progress(done, total):
            logger.info(f"Step 3: embedded {done}/{total} chunks")

        vectorstore = _build_faiss_index(all_chunks, embeddings, progress_fn=log_progress)
        if vectorstore is None:
            logger.warning("Step 3: no chunks to embed")
            return _fallback_first_pages(pdf_path)

        query = f""" Find financial tables related to:
        {field}

        Focus on:
        - reserves
        - production
        - financial tables
        - numeric data

        {doc_hint}"""
        
        hit_pages = _search_parent_pages(vectorstore, query, parent_docs)

        if not hit_pages:
            logger.warning("Step 3: search returned no results, falling back")
            return _fallback_first_pages(pdf_path)

        text = "\n\n--- PAGE BREAK ---\n\n".join(doc.page_content for doc in hit_pages)
        if len(text) > MAX_CONTEXT_CHARS:
            text = text[:MAX_CONTEXT_CHARS]

        logger.info(f"Step 3: retrieved {len(hit_pages)} parent pages ({len(text)} chars)")
        return text

    except Exception as e:
        logger.error(f"Step 3: RAG retrieval failed: {e}")
        return _fallback_first_pages(pdf_path)


def _fallback_first_pages(pdf_path: str) -> str:
    """Fallback: return concatenated text of the first 10 pages."""
    docs = _load_pdf_pages(pdf_path)
    text = "\n\n".join(doc.page_content for doc in docs[:10])
    if len(text) > MAX_CONTEXT_CHARS:
        text = text[:MAX_CONTEXT_CHARS]
    return text


# ── Step 4: Extract Metric ────────────────────────────────────────

def _build_extraction_prompt(ticker: str, field: str, doc_hint: str, context_text: str) -> str:
    return f"""\
#######################################################
# Role
You are a financial data extraction specialist. You extract precise numeric
values from the document text provided below. You never fabricate numbers.

# CRITICAL RULES
- DO NOT guess
- DO NOT infer missing values
- DO NOT calculate unless ALL inputs are explicitly present
- ONLY extract values directly visible in the text or tables

# Task
Extract the metric **{field}** for **{ticker}** from the document text below.

# Search Guidance
{doc_hint}

# Document Text
```
{context_text}
```
# Instructions
1. Prefer values from TABLES over text
2. If multiple values exist, choose the most recent period
3. If unclear → return null

  "field"  : "{field}",
{{
  "field"  : "{field}",
  "value"  : <number or null if not found>,
  "unit"   : "<unit string, e.g. %, Mt, years, AUD M>",
  "period" : "<reporting period, e.g. FY 2025, H1 2025>",
  "source" : "<page number or section where the data was found>"
}}

# Few-shot Example
For ticker=BHP, field=Reserves Life:
  Reserves (P1+P2) = 1360 Mt, Production = 263 Mt
  RLI = 1360 / 263 = 5.17 years
  Output: {{"field": "Reserves Life", "value": 5.17, "unit": "years", "period": "FY 2025", "source": "Ore Reserves table, page 42"}}

# Constraints
- Only use data from the document text above.
- If the data is not present, set "value" to null.
- For percentages, output the number (45.5 means 45.5%).
- Convert monetary values to millions (AUD M) unless stated otherwise.
- Output ONLY the JSON object, no other text.
#######################################################
"""


def _extract_metric(
    ticker: str, field: str, doc_hint: str,
    context_text: str, source_url: Optional[str], llm,
) -> MetricResult:
    """Step 4: Ask LLM to extract the metric from actual document text."""
    prompt = _build_extraction_prompt(ticker, field, doc_hint, context_text)
    raw = _call_llm(prompt, llm)

    if not raw:
        logger.warning("Step 4: no response from LLM")
        return MetricResult(field=field, source=source_url or "", raw_response="")

    data = _parse_json(raw)
    if not data:
        logger.warning(f"Step 4: could not parse response")
        return MetricResult(field=field, source=source_url or "", raw_response=pprint(raw))

    source = source_url or ""
    doc_source = str(data.get("source", ""))
    if doc_source:
        source = f"{source} ({doc_source})" if source else doc_source

    return MetricResult(
        field=data.get("field", field),
        value=_safe_float(data.get("value")),
        unit=str(data.get("unit", "")),
        period=str(data.get("period", "")),
        source=source,
        raw_response=raw,
    )


# ── Step 4b: Batch Extract Metrics ────────────────────────────────

def _build_batch_extraction_prompt(
    ticker: str, fields: List[str], doc_hint: str, context_text: str,
) -> str:
    fields_list = "\n".join(f"  - {f}" for f in fields)
    fields_schema = "\n".join(f'    "{f}": {{"value": <number or null>, "unit": "<unit>", "period": "<period>", "source": "<source>"}},' for f in fields)
    return f"""\
# Role
You are a financial data extraction specialist. You extract precise numeric
values from the document text provided below. You never fabricate numbers.

# Task
Extract the following metrics for **{ticker}** from the document text below:
{fields_list}

# Search Guidance
{doc_hint}

# Document Text
```
{context_text}
```

# Instructions
1. Locate the relevant data for EACH metric in the document text above.
2. For reserves fields, use Proved + Probable reserves (NOT Mineral Resources).
3. For production fields, use Actual Attributable Production.
4. For EBITDA contribution, extract the percentage each commodity contributes to total Underlying EBITDA.
5. Output a single JSON object with ALL fields.

# Output Schema (strict JSON)
{{
{fields_schema}
}}

# Constraints
- Only use data from the document text above.
- If the data is not present for a field, set its "value" to null.
- For percentages, output the number (45.5 means 45.5%).
- Reserves in Mt, Production in Mt, EBITDA Contribution in %.
- Output ONLY the JSON object, no other text."""


def _extract_metrics_batch(
    ticker: str, fields: List[str], doc_hint: str,
    context_text: str, source_url: Optional[str], llm,
) -> Dict[str, MetricResult]:
    """Step 4b: Ask LLM to extract multiple metrics from document text in one call."""
    prompt = _build_batch_extraction_prompt(ticker, fields, doc_hint, context_text)
    raw = _call_llm(prompt, llm)

    results: Dict[str, MetricResult] = {}

    if not raw:
        logger.warning("Step 4b: no response from LLM")
        for f in fields:
            results[f] = MetricResult(field=f, source=source_url or "", raw_response="")
        return results

    data = _parse_json(raw)
    if not data:
        logger.warning("Step 4b: could not parse response")
        for f in fields:
            results[f] = MetricResult(field=f, source=source_url or "", raw_response=raw)
        return results

    for f in fields:
        field_data = data.get(f, {})
        if not isinstance(field_data, dict):
            field_data = {}

        source = source_url or ""
        doc_source = str(field_data.get("source", ""))
        if doc_source:
            source = f"{source} ({doc_source})" if source else doc_source

        results[f] = MetricResult(
            field=f,
            value=_safe_float(field_data.get("value")),
            unit=str(field_data.get("unit", "")),
            period=str(field_data.get("period", "")),
            source=source,
            raw_response=raw,
        )

    return results


# ── Public API ────────────────────────────────────────────────────

def compute_metrics(ticker: str, fields: List[str], doc_hint: str) -> Dict[str, MetricResult]:
    """
    Extract multiple financial metrics in a single pipeline run.

    Steps 1-3 execute once (shared PDF). Step 4 extracts all fields
    in a single LLM call.

    Args:
        ticker:   Stock code, e.g. "BHP"
        fields:   List of metric names to extract
        doc_hint: Guidance on where/how to find the data

    Returns:
        Dict mapping field name -> MetricResult
    """
    ticker = ticker.upper().replace(".AX", "")
    set_ticker(ticker)
    logger.info(f"metric_agent: computing {len(fields)} fields for {ticker}: {fields}")

    if not fields:
        return {}

    llm_json = _get_llm_json()
    llm_text = _get_llm_text()
    if llm_json is None or llm_text is None:
        return {f: MetricResult(field=f, raw_response="LLM not available (no API key)") for f in fields}

    search_query = " ".join(fields[:3])
    pdf_url = _search_pdf_url(ticker, search_query, doc_hint, llm_json)

    pdf_path = _download_pdf(pdf_url) if pdf_url else None

    context = ""
    if pdf_path:
        combined_query = " ".join(fields) + " " + doc_hint
        context = _retrieve_relevant_chunks(pdf_path, combined_query, doc_hint)

    if not context:
        logger.warning("No PDF context available, Step 4b will attempt without document text")

    return _extract_metrics_batch(ticker, fields, doc_hint, context, pdf_url, llm_text)


def compute_metric(ticker: str, field: str, doc_hint: str) -> MetricResult:
    """
    Extract a single financial metric for an ASX stock via a 4-step pipeline.

    Steps:
        1. LLM + Google Search → find PDF URL
        2. Download PDF to local cache
        3. ParentDocumentRetriever (Google Embeddings + FAISS) → relevant chunks
        4. LLM + actual PDF text → extract metric

    Args:
        ticker:   Stock code, e.g. "BHP"
        field:    Metric name, e.g. "Reserves Life"
        doc_hint: Guidance on where/how to find the data, e.g.
                  "Search BHP 2025 Annual Report, Ore Reserves table.
                   RLI = Reserves / Production."

    Returns:
        MetricResult with the extracted value (value=None when not found).
    """
    ticker = ticker.upper().replace(".AX", "")
    set_ticker(ticker)
    logger.info(f"metric_agent: computing '{field}' for {ticker}")

    llm_json = _get_llm_json()
    llm_text = _get_llm_text()
    if llm_json is None or llm_text is None:
        return MetricResult(field=field, raw_response="LLM not available (no API key)")

    # Step 1: find PDF URL
    pdf_url = _search_pdf_url(ticker, field, doc_hint, llm_json)

    # Step 2: download PDF
    pdf_path = _download_pdf(pdf_url) if pdf_url else None

    # Step 3: RAG retrieve relevant chunks
    context = ""
    if pdf_path:
        context = _retrieve_relevant_chunks(pdf_path, field, doc_hint)

    if not context:
        logger.warning("No PDF context available, Step 4 will attempt without document text")

    # Step 4: extract metric from context
    return _extract_metric(ticker, field, doc_hint, context, pdf_url, llm_text)


# ── Test mode ─────────────────────────────────────────────────────

def test_rag(pdf_path: str, fields: List[str], doc_hint: str) -> None:
    """
    Test mode: skip all LLM calls, only test PDF splitting and RAG retrieval.

    Prints:
    - PDF page count and total chars
    - Child chunk count and sample
    - Retrieved pages per query with content preview
    """
    print(f"\n{'='*60}")
    print(f"TEST MODE — PDF: {pdf_path}")
    print(f"{'='*60}\n")

    parent_docs = _load_pdf_pages(pdf_path)
    total_chars = sum(len(d.page_content) for d in parent_docs)
    print(f"[Step 2] PDF loaded: {len(parent_docs)} pages, {total_chars:,} chars total\n")

    all_chunks = _split_pages_to_chunks(parent_docs)
    print(f"[Step 3a] Split into {len(all_chunks)} child chunks "
          f"(chunk_size={CHILD_CHUNK_SIZE}, overlap={CHILD_CHUNK_OVERLAP})\n")

    embeddings = _get_embeddings()
    if embeddings is None:
        print("[Step 3b] ERROR: embeddings not available (no GEMINI_API_KEY)")
        print("          Falling back to first 10 pages preview:\n")
        for doc in parent_docs[:10]:
            pg = doc.metadata.get("page", "?")
            preview = doc.page_content[:200].replace("\n", " ")
            print(f"  Page {pg}: {preview}...")
        return

    print(f"[Step 3b] Embedding {len(all_chunks)} chunks one-by-one...")

    def print_progress(done, total):
        print(f"  embedded {done}/{total}")

    vectorstore = _build_faiss_index(all_chunks, embeddings, progress_fn=print_progress)
    if vectorstore is None:
        print("[Step 3b] ERROR: no chunks to embed")
        return

    print(f"\n[Step 3c] FAISS index built. Running queries...\n")

    for field in fields:
        query = f"{field} {doc_hint}"
        print(f"{'─'*60}")
        print(f"Query: {field}")
        print(f"Full query: {query[:120]}...")
        results = vectorstore.similarity_search_with_score(query, k=TOP_K_CHUNKS)

        if not results:
            print("  → No results\n")
            continue

        hit_pages = []
        seen = set()
        print(f"  → {len(results)} chunks matched:\n")
        for rank, (chunk, score) in enumerate(results, 1):
            pg = chunk.metadata.get("parent_page", "?")
            preview = chunk.page_content[:150].replace("\n", " ")
            print(f"  #{rank} [page {pg}] score={score:.4f}")
            print(f"     {preview}...\n")
            if pg not in seen:
                seen.add(pg)
                hit_pages.append(pg)

        print(f"  → Unique parent pages: {hit_pages}\n")

    print(f"{'='*60}")
    print("TEST COMPLETE")
    print(f"{'='*60}")


# ── CLI ───────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Metric Agent — extract financial metrics from ASX company reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Single field
  python metric_agent.py -t BHP -f "Reserves Life" \\
      -hint "Search BHP 2025 Annual Report, Ore Reserves table."

  # Multiple fields (batch mode, shared PDF pipeline)
  python metric_agent.py -t BHP \\
      --fields "Iron Ore Proved Reserves" "Iron Ore Annual Production" \\
      -hint "Search BHP 2025 Annual Report, Ore Reserves and Production tables."

  # Test mode: test PDF splitting + RAG retrieval without LLM calls
  python metric_agent.py --test --pdf data/pdf/af71d2b9f457.pdf \\
      --fields "Iron Ore Proved Reserves" "Copper Annual Production" \\
      -hint "Ore Reserves table and Production summary"
""",
    )
    parser.add_argument("-t", "--ticker", help="ASX stock code, e.g. BHP")
    parser.add_argument("--test", action="store_true",
                        help="Test mode: skip LLM, only test PDF split + RAG retrieval")
    parser.add_argument("--pdf", help="Path to local PDF file (for --test mode)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--field", help='Single metric name, e.g. "Reserves Life"')
    group.add_argument("--fields", nargs="+", help="Multiple metric names (batch mode)")
    parser.add_argument("-hint", "--doc_hint", default="", help="Guidance on which document to search")
    parser.add_argument("-d", "--debug", action="store_true", help="开启调试日志")
    args = parser.parse_args()

    if args.debug:
        import logging
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    if args.test:
        if not args.pdf:
            parser.error("--test requires --pdf <path>")
        fields = args.fields or ([args.field] if args.field else ["Reserves Life"])
        test_rag(args.pdf, fields, args.doc_hint)
        return

    if not args.ticker:
        parser.error("-t/--ticker is required (unless using --test)")
    if not args.field and not args.fields:
        parser.error("-f/--field or --fields is required")

    if args.fields:
        results = compute_metrics(args.ticker, args.fields, args.doc_hint)
        output = {name: r.model_dump() for name, r in results.items()}
    else:
        result = compute_metric(args.ticker, args.field, args.doc_hint)
        output = result.model_dump()

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
