"""
Tests for metric_agent module (4-step RAG pipeline).

Tests cover:
- MetricResult Pydantic model
- Prompt builders (search + extraction)
- JSON parsing and _safe_float helpers
- Each pipeline step mocked independently
- _retrieve_relevant_chunks with a real tiny PDF + mocked embeddings
- _download_pdf with mocked requests
- Full compute_metric orchestration with all steps mocked
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metric_agent import (
    MetricResult,
    compute_metric,
    compute_metrics,
    _build_search_prompt,
    _build_extraction_prompt,
    _build_batch_extraction_prompt,
    _parse_json,
    _safe_float,
    _search_pdf_url,
    _download_pdf,
    _load_pdf_pages,
    _retrieve_relevant_chunks,
    _extract_metric,
    _extract_metrics_batch,
    _fallback_first_pages,
)


# ── MetricResult ──────────────────────────────────────────────────

class TestMetricResult(unittest.TestCase):

    def test_defaults(self):
        r = MetricResult(field="ROE")
        self.assertIsNone(r.value)
        self.assertEqual(r.unit, "")
        self.assertEqual(r.period, "")

    def test_full_construction(self):
        r = MetricResult(
            field="Reserves Life", value=5.17, unit="years",
            period="FY 2025", source="https://example.com/report.pdf",
        )
        self.assertEqual(r.value, 5.17)
        self.assertEqual(r.unit, "years")

    def test_serialization_roundtrip(self):
        r = MetricResult(field="CET1", value=12.5, unit="%", period="FY 2025")
        r2 = MetricResult(**r.model_dump())
        self.assertEqual(r, r2)

    def test_null_value(self):
        r = MetricResult(field="Missing", value=None)
        self.assertIsNone(r.model_dump()["value"])


# ── Helpers ───────────────────────────────────────────────────────

class TestParseJson(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(_parse_json('{"a": 1}')["a"], 1)

    def test_embedded_in_text(self):
        raw = 'blah\n{"x": 42}\nend'
        self.assertEqual(_parse_json(raw)["x"], 42)

    def test_empty(self):
        self.assertEqual(_parse_json(""), {})
        self.assertEqual(_parse_json(None), {})

    def test_invalid(self):
        self.assertEqual(_parse_json("{broken!!!"), {})

    def test_no_json(self):
        self.assertEqual(_parse_json("just text"), {})


class TestSafeFloat(unittest.TestCase):

    def test_int(self):
        self.assertEqual(_safe_float(42), 42.0)

    def test_float(self):
        self.assertEqual(_safe_float(3.14), 3.14)

    def test_string(self):
        self.assertEqual(_safe_float("12.5"), 12.5)

    def test_none(self):
        self.assertIsNone(_safe_float(None))

    def test_invalid(self):
        self.assertIsNone(_safe_float("N/A"))


# ── Prompt builders ───────────────────────────────────────────────

class TestBuildSearchPrompt(unittest.TestCase):

    def test_contains_ticker(self):
        p = _build_search_prompt("BHP", "Reserves Life", "annual report")
        self.assertIn("BHP", p)

    def test_contains_doc_hint(self):
        hint = "Search BHP 2025 Annual Report Ore Reserves table"
        p = _build_search_prompt("BHP", "Reserves Life", hint)
        self.assertIn(hint, p)

    def test_json_schema(self):
        p = _build_search_prompt("CBA", "CET1", "Pillar 3")
        self.assertIn('"url"', p)


class TestBuildExtractionPrompt(unittest.TestCase):

    def test_contains_context(self):
        ctx = "Iron Ore Reserves: 1360 Mt"
        p = _build_extraction_prompt("BHP", "Reserves Life", "hint", ctx)
        self.assertIn(ctx, p)

    def test_contains_field_and_ticker(self):
        p = _build_extraction_prompt("RIO", "FCF Yield", "hint", "text")
        self.assertIn("RIO", p)
        self.assertIn("FCF Yield", p)

    def test_has_few_shot(self):
        p = _build_extraction_prompt("FMG", "X", "hint", "text")
        self.assertIn("5.17", p)

    def test_json_schema(self):
        p = _build_extraction_prompt("BHP", "X", "hint", "text")
        for key in ('"field"', '"value"', '"unit"', '"period"', '"source"'):
            self.assertIn(key, p)


# ── Step 1: Search PDF URL ────────────────────────────────────────

class TestSearchPdfUrl(unittest.TestCase):

    def test_returns_url(self):
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(
            content='{"url": "https://bhp.com/report.pdf"}'
        )
        url = _search_pdf_url("BHP", "Reserves Life", "hint", llm)
        self.assertEqual(url, "https://bhp.com/report.pdf")

    def test_empty_url(self):
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(content='{"url": ""}')
        self.assertIsNone(_search_pdf_url("BHP", "X", "hint", llm))

    def test_llm_failure(self):
        llm = MagicMock()
        llm.invoke.side_effect = Exception("API down")
        self.assertIsNone(_search_pdf_url("BHP", "X", "hint", llm))


# ── Step 2: Download PDF ─────────────────────────────────────────

class TestDownloadPdf(unittest.TestCase):

    @patch("metric_agent.requests.get")
    def test_successful_download(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "application/pdf"}
        mock_resp.content = b"%PDF-1.4 fake pdf content " + b"x" * 1000
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        path = _download_pdf("https://example.com/report.pdf")
        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))

        # Cleanup
        if path and os.path.exists(path):
            os.remove(path)

    @patch("metric_agent.requests.get")
    def test_not_pdf(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "text/html"}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        path = _download_pdf("https://example.com/page.html")
        self.assertIsNone(path)

    @patch("metric_agent.requests.get")
    def test_network_error(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        self.assertIsNone(_download_pdf("https://example.com/report.pdf"))

    def test_cached_file(self):
        """If file already exists in cache, don't re-download."""
        # Create a fake cached file
        import hashlib
        url = "https://example.com/cached-test.pdf"
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        cached_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "pdf", f"{url_hash}.pdf"
        )
        os.makedirs(os.path.dirname(cached_path), exist_ok=True)
        with open(cached_path, "wb") as f:
            f.write(b"x" * 2000)

        path = _download_pdf(url)
        self.assertEqual(path, cached_path)

        os.remove(cached_path)


# ── Step 3: RAG Retrieval ─────────────────────────────────────────

def _create_test_pdf(path: str, pages: dict):
    """Create a tiny PDF with specific text on each page."""
    doc = pymupdf.open()
    for page_num in sorted(pages.keys()):
        page = doc.new_page()
        page.insert_text((72, 72), pages[page_num])
    doc.save(path)
    doc.close()


class TestLoadPdfPages(unittest.TestCase):

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        _create_test_pdf(self.tmpfile.name, {
            1: "Page 1: Introduction to BHP Annual Report",
            2: "Page 2: Ore Reserves table\nIron Ore 1360 Mt\nProduction 263 Mt",
            3: "Page 3: Financial Summary\nRevenue $50B",
        })

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_extracts_all_pages(self):
        docs = _load_pdf_pages(self.tmpfile.name)
        self.assertEqual(len(docs), 3)

    def test_page_metadata(self):
        docs = _load_pdf_pages(self.tmpfile.name)
        self.assertEqual(docs[0].metadata["page"], 1)
        self.assertEqual(docs[1].metadata["page"], 2)

    def test_content_preserved(self):
        docs = _load_pdf_pages(self.tmpfile.name)
        self.assertIn("Ore Reserves", docs[1].page_content)
        self.assertIn("1360", docs[1].page_content)


class TestRetrieveRelevantChunks(unittest.TestCase):

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        _create_test_pdf(self.tmpfile.name, {
            1: "Page 1: Corporate governance and board members list",
            2: "Page 2: Ore Reserves Proved Probable\nIron Ore 1360 Mt\nCopper 12 Mt",
            3: "Page 3: Production volume 263 Mt iron ore shipped",
            4: "Page 4: Sustainability and environmental report",
            5: "Page 5: Tax reconciliation and statutory accounts",
        })

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    @patch("metric_agent._get_embeddings")
    def test_fallback_when_no_embeddings(self, mock_emb):
        mock_emb.return_value = None
        text = _retrieve_relevant_chunks(self.tmpfile.name, "Reserves Life", "hint")
        self.assertTrue(len(text) > 0)

    def test_fallback_first_pages(self):
        text = _fallback_first_pages(self.tmpfile.name)
        self.assertIn("Corporate governance", text)
        self.assertIn("Ore Reserves", text)


# ── Step 4: Extract Metric ────────────────────────────────────────

class TestExtractMetric(unittest.TestCase):

    def test_successful_extraction(self):
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(
            content='{"field": "Reserves Life", "value": 5.17, '
                    '"unit": "years", "period": "FY 2025", '
                    '"source": "page 42"}'
        )
        result = _extract_metric(
            "BHP", "Reserves Life", "hint",
            "Iron Ore Reserves 1360 Mt, Production 263 Mt",
            "https://bhp.com/ar.pdf", llm,
        )
        self.assertEqual(result.value, 5.17)
        self.assertEqual(result.unit, "years")
        self.assertIn("bhp.com", result.source)
        self.assertIn("page 42", result.source)

    def test_null_value(self):
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(
            content='{"field": "X", "value": null, "unit": "", "period": "", "source": ""}'
        )
        result = _extract_metric("BHP", "X", "hint", "no data", None, llm)
        self.assertIsNone(result.value)

    def test_llm_failure(self):
        llm = MagicMock()
        llm.invoke.side_effect = Exception("timeout")
        result = _extract_metric("BHP", "X", "hint", "text", None, llm)
        self.assertIsNone(result.value)


# ── Full Pipeline ─────────────────────────────────────────────────

class TestComputeMetric(unittest.TestCase):

    @patch("metric_agent._get_llm_text")
    @patch("metric_agent._get_llm_json")
    def test_no_api_key(self, mock_json, mock_text):
        mock_json.return_value = None
        mock_text.return_value = None
        result = compute_metric("BHP", "Reserves Life", "hint")
        self.assertIsNone(result.value)
        self.assertIn("not available", result.raw_response)

    @patch("metric_agent._extract_metric")
    @patch("metric_agent._retrieve_relevant_chunks")
    @patch("metric_agent._download_pdf")
    @patch("metric_agent._search_pdf_url")
    @patch("metric_agent._get_llm_text")
    @patch("metric_agent._get_llm_json")
    def test_full_pipeline(self, mock_json, mock_text,
                           mock_search, mock_download, mock_retrieve, mock_extract):
        mock_json.return_value = MagicMock()
        mock_text.return_value = MagicMock()
        mock_search.return_value = "https://bhp.com/ar.pdf"
        mock_download.return_value = "/tmp/test.pdf"
        mock_retrieve.return_value = "Reserves 1360 Mt, Production 263 Mt"
        mock_extract.return_value = MetricResult(
            field="Reserves Life", value=5.17, unit="years",
            period="FY 2025", source="https://bhp.com/ar.pdf",
        )

        result = compute_metric("BHP", "Reserves Life", "annual report")
        self.assertEqual(result.value, 5.17)

        mock_search.assert_called_once()
        mock_download.assert_called_once_with("https://bhp.com/ar.pdf")
        mock_retrieve.assert_called_once()
        mock_extract.assert_called_once()

    @patch("metric_agent._extract_metric")
    @patch("metric_agent._search_pdf_url")
    @patch("metric_agent._get_llm_text")
    @patch("metric_agent._get_llm_json")
    def test_graceful_no_pdf(self, mock_json, mock_text, mock_search, mock_extract):
        """When no PDF is found, Step 4 still runs with empty context."""
        mock_json.return_value = MagicMock()
        mock_text.return_value = MagicMock()
        mock_search.return_value = None
        mock_extract.return_value = MetricResult(field="X", value=None)

        result = compute_metric("BHP", "X", "hint")
        mock_extract.assert_called_once()
        context_arg = mock_extract.call_args[0][3]
        self.assertEqual(context_arg, "")

    @patch("metric_agent._extract_metric")
    @patch("metric_agent._download_pdf")
    @patch("metric_agent._search_pdf_url")
    @patch("metric_agent._get_llm_text")
    @patch("metric_agent._get_llm_json")
    def test_graceful_download_fail(self, mock_json, mock_text,
                                     mock_search, mock_download, mock_extract):
        """When download fails, Step 4 still runs with empty context."""
        mock_json.return_value = MagicMock()
        mock_text.return_value = MagicMock()
        mock_search.return_value = "https://example.com/report.pdf"
        mock_download.return_value = None
        mock_extract.return_value = MetricResult(field="X")

        compute_metric("BHP", "X", "hint")
        context_arg = mock_extract.call_args[0][3]
        self.assertEqual(context_arg, "")

    @patch("metric_agent._extract_metric")
    @patch("metric_agent._retrieve_relevant_chunks")
    @patch("metric_agent._download_pdf")
    @patch("metric_agent._search_pdf_url")
    @patch("metric_agent._get_llm_text")
    @patch("metric_agent._get_llm_json")
    def test_ticker_normalized(self, mock_json, mock_text,
                                mock_search, mock_download, mock_retrieve, mock_extract):
        mock_json.return_value = MagicMock()
        mock_text.return_value = MagicMock()
        mock_search.return_value = None
        mock_extract.return_value = MetricResult(field="ROE")

        compute_metric("cba.ax", "ROE", "hint")

        search_call_ticker = mock_search.call_args[0][0]
        self.assertEqual(search_call_ticker, "CBA")


# ── Batch Extraction Prompt ────────────────────────────────────────

class TestBuildBatchExtractionPrompt(unittest.TestCase):

    def test_contains_all_fields(self):
        fields = ["Iron Ore Proved Reserves", "Copper Annual Production"]
        p = _build_batch_extraction_prompt("BHP", fields, "hint", "text")
        for f in fields:
            self.assertIn(f, p)

    def test_contains_ticker(self):
        p = _build_batch_extraction_prompt("RIO", ["X"], "hint", "text")
        self.assertIn("RIO", p)

    def test_contains_context(self):
        ctx = "Reserves 1360 Mt"
        p = _build_batch_extraction_prompt("BHP", ["X"], "hint", ctx)
        self.assertIn(ctx, p)


# ── Step 4b: Batch Extract ────────────────────────────────────────

class TestExtractMetricsBatch(unittest.TestCase):

    def test_successful_batch(self):
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(
            content=json.dumps({
                "Iron Ore Proved Reserves": {"value": 1360, "unit": "Mt", "period": "FY 2025", "source": "p42"},
                "Iron Ore Annual Production": {"value": 263, "unit": "Mt", "period": "FY 2025", "source": "p50"},
            })
        )
        fields = ["Iron Ore Proved Reserves", "Iron Ore Annual Production"]
        results = _extract_metrics_batch("BHP", fields, "hint", "text", "https://bhp.com/ar.pdf", llm)

        self.assertEqual(len(results), 2)
        self.assertEqual(results["Iron Ore Proved Reserves"].value, 1360.0)
        self.assertEqual(results["Iron Ore Annual Production"].value, 263.0)
        self.assertIn("bhp.com", results["Iron Ore Proved Reserves"].source)

    def test_partial_results(self):
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(
            content=json.dumps({
                "Iron Ore Proved Reserves": {"value": 1360, "unit": "Mt", "period": "FY 2025", "source": ""},
                "Copper Proved Reserves": {"value": None, "unit": "", "period": "", "source": ""},
            })
        )
        fields = ["Iron Ore Proved Reserves", "Copper Proved Reserves"]
        results = _extract_metrics_batch("BHP", fields, "hint", "text", None, llm)

        self.assertEqual(results["Iron Ore Proved Reserves"].value, 1360.0)
        self.assertIsNone(results["Copper Proved Reserves"].value)

    def test_llm_failure_returns_empty_results(self):
        llm = MagicMock()
        llm.invoke.side_effect = Exception("timeout")
        fields = ["X", "Y"]
        results = _extract_metrics_batch("BHP", fields, "hint", "text", None, llm)

        self.assertEqual(len(results), 2)
        self.assertIsNone(results["X"].value)
        self.assertIsNone(results["Y"].value)

    def test_missing_field_in_response(self):
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(
            content='{"X": {"value": 42, "unit": "", "period": "FY 2025", "source": ""}}'
        )
        results = _extract_metrics_batch("BHP", ["X", "Y"], "hint", "text", None, llm)
        self.assertEqual(results["X"].value, 42.0)
        self.assertIsNone(results["Y"].value)


# ── Batch Pipeline ────────────────────────────────────────────────

class TestComputeMetrics(unittest.TestCase):

    @patch("metric_agent._get_llm_text")
    @patch("metric_agent._get_llm_json")
    def test_no_api_key(self, mock_json, mock_text):
        mock_json.return_value = None
        mock_text.return_value = None
        results = compute_metrics("BHP", ["X", "Y"], "hint")
        self.assertEqual(len(results), 2)
        self.assertIn("not available", results["X"].raw_response)

    @patch("metric_agent._extract_metrics_batch")
    @patch("metric_agent._retrieve_relevant_chunks")
    @patch("metric_agent._download_pdf")
    @patch("metric_agent._search_pdf_url")
    @patch("metric_agent._get_llm_text")
    @patch("metric_agent._get_llm_json")
    def test_full_batch_pipeline(self, mock_json, mock_text,
                                  mock_search, mock_download, mock_retrieve, mock_extract):
        mock_json.return_value = MagicMock()
        mock_text.return_value = MagicMock()
        mock_search.return_value = "https://bhp.com/ar.pdf"
        mock_download.return_value = "/tmp/test.pdf"
        mock_retrieve.return_value = "Reserves 1360 Mt"
        mock_extract.return_value = {
            "X": MetricResult(field="X", value=1360),
            "Y": MetricResult(field="Y", value=263),
        }

        results = compute_metrics("BHP", ["X", "Y"], "hint")
        self.assertEqual(results["X"].value, 1360)
        self.assertEqual(results["Y"].value, 263)

        mock_search.assert_called_once()
        mock_download.assert_called_once()
        mock_retrieve.assert_called_once()
        mock_extract.assert_called_once()

    @patch("metric_agent._extract_metrics_batch")
    @patch("metric_agent._search_pdf_url")
    @patch("metric_agent._get_llm_text")
    @patch("metric_agent._get_llm_json")
    def test_no_pdf_still_extracts(self, mock_json, mock_text, mock_search, mock_extract):
        mock_json.return_value = MagicMock()
        mock_text.return_value = MagicMock()
        mock_search.return_value = None
        mock_extract.return_value = {"X": MetricResult(field="X")}

        compute_metrics("BHP", ["X"], "hint")
        context_arg = mock_extract.call_args[0][3]
        self.assertEqual(context_arg, "")

    def test_empty_fields_returns_empty(self):
        results = compute_metrics("BHP", [], "hint")
        self.assertEqual(results, {})


def run_tests():
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
