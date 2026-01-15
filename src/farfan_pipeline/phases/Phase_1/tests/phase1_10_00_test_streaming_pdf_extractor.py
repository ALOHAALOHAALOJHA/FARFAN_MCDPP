"""
Tests for StreamingPDFExtractor.

Purpose: Verify PDF extraction with resource management and truncation handling.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State:  ACTIVE
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from farfan_pipeline.phases.Phase_1.primitives.streaming_extractor import (
    StreamingPDFExtractor,
    PYMUPDF_AVAILABLE,
)
from farfan_pipeline.phases.Phase_1.phase1_02_00_phase_1_constants import PDF_EXTRACTION_CHAR_LIMIT


class TestStreamingPDFExtractorAvailability(unittest.TestCase):
    """Test PyMuPDF availability handling."""

    @patch(
        "farfan_pipeline.phases.Phase_1.primitives.streaming_extractor.PYMUPDF_AVAILABLE", False
    )
    def test_raises_runtime_error_when_pymupdf_not_available_stream(self):
        extractor = StreamingPDFExtractor(Path("dummy.pdf"))
        with self.assertRaises(RuntimeError) as ctx:
            list(extractor.extract_text_stream())
        self.assertIn("PyMuPDF", str(ctx.exception))

    @patch(
        "farfan_pipeline.phases.Phase_1.primitives.streaming_extractor.PYMUPDF_AVAILABLE", False
    )
    def test_raises_runtime_error_when_pymupdf_not_available_limit(self):
        extractor = StreamingPDFExtractor(Path("dummy. pdf"))
        with self.assertRaises(RuntimeError) as ctx:
            extractor.extract_with_limit()
        self.assertIn("PyMuPDF", str(ctx.exception))


@unittest.skipUnless(PYMUPDF_AVAILABLE, "PyMuPDF not installed")
class TestStreamingPDFExtractorWithMockPDF(unittest.TestCase):
    """Test extraction logic with mocked PDF document."""

    def setUp(self):
        """Create mock PDF structure."""
        self.mock_page1 = MagicMock()
        self.mock_page1.get_text.return_value = "Page one content.  " * 100  # 1800 chars

        self.mock_page2 = MagicMock()
        self.mock_page2.get_text.return_value = "Page two content. " * 100  # 1800 chars

        self.mock_page3 = MagicMock()
        self.mock_page3.get_text.return_value = "Page three content. " * 100  # 2000 chars

    @patch("farfan_pipeline.phases.Phase_1.primitives.streaming_extractor.fitz")
    def test_extract_text_stream_yields_pages(self, mock_fitz):
        mock_doc = MagicMock()
        mock_doc.__iter__ = lambda self: iter([self.mock_page1, self.mock_page2])
        mock_fitz.open.return_value = mock_doc

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake content")
            temp_path = Path(f.name)

        try:
            # Patch exists to return True
            with patch.object(Path, "exists", return_value=True):
                extractor = StreamingPDFExtractor(temp_path)
                pages = list(extractor.extract_text_stream())

            self.assertEqual(len(pages), 2)
            mock_doc.close.assert_called_once()
        finally:
            temp_path.unlink(missing_ok=True)

    @patch("farfan_pipeline.phases.Phase_1.primitives.streaming_extractor.fitz")
    def test_extract_with_limit_truncates_correctly(self, mock_fitz):
        mock_doc = MagicMock()
        # Capture pages from test instance scope
        pages = [self.mock_page1, self.mock_page2, self.mock_page3]
        mock_doc.__iter__.return_value = iter(pages)
        mock_fitz.open.return_value = mock_doc

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake content")
            temp_path = Path(f.name)

        try:
            with patch.object(Path, "exists", return_value=True):
                extractor = StreamingPDFExtractor(temp_path)
                text, processed, total = extractor.extract_with_limit(char_limit=3000)

            self.assertEqual(processed, 3000)
            self.assertEqual(total, 5700)  # 1900 + 1800 + 2000
            self.assertEqual(len(text), 3000)
            mock_doc.close.assert_called_once()
        finally:
            temp_path.unlink(missing_ok=True)

    @patch("farfan_pipeline.phases.Phase_1.primitives.streaming_extractor.fitz")
    def test_document_closed_on_iteration_exception(self, mock_fitz):
        mock_doc = MagicMock()
        mock_page_bad = MagicMock()
        mock_page_bad.get_text.side_effect = RuntimeError("PDF corruption")
        mock_doc.__iter__ = lambda self: iter([mock_page_bad])
        mock_fitz.open.return_value = mock_doc

        with tempfile.NamedTemporaryFile(suffix=". pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake content")
            temp_path = Path(f.name)

        try:
            with patch.object(Path, "exists", return_value=True):
                extractor = StreamingPDFExtractor(temp_path)
                with self.assertRaises(RuntimeError):
                    list(extractor.extract_text_stream())

            # Verify close was called despite exception
            mock_doc.close.assert_called_once()
        finally:
            temp_path.unlink(missing_ok=True)


class TestStreamingPDFExtractorConstants(unittest.TestCase):
    """Verify constant usage."""

    def test_default_char_limit_matches_constant(self):
        # Verify the default parameter value
        import inspect

        sig = inspect.signature(StreamingPDFExtractor.extract_with_limit)
        default = sig.parameters["char_limit"].default
        self.assertEqual(default, PDF_EXTRACTION_CHAR_LIMIT)


if __name__ == "__main__":
    unittest.main()
