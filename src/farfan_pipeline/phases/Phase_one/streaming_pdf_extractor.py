"""
Streaming PDF Text Extraction with Bounded Memory.

Purpose: Extract PDF text without loading entire document into memory.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State: ACTIVE
"""

from typing import Generator, Optional, Tuple
import logging
from pathlib import Path

# Use PyMuPDF if available
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

logger = logging.getLogger(__name__)

class StreamingPDFExtractor:
    """
    Extracts text from PDFs in a streaming fashion to minimize memory usage.
    """

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path

    def extract_text_stream(self, chunk_size_pages: int = 10) -> Generator[str, None, None]:
        """
        Yields text from the PDF page by page or in chunks of pages.

        Args:
            chunk_size_pages: Number of pages to process before yielding (not strictly used here,
                              we yield per page for simplicity and max granularity).
        """
        if not PYMUPDF_AVAILABLE:
            raise RuntimeError("PyMuPDF (fitz) is not installed. Cannot extract PDF text.")

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        try:
            doc = fitz.open(self.pdf_path)
            for page in doc:
                yield page.get_text()
            doc.close()
        except Exception as e:
            logger.error(f"Error during streaming PDF extraction: {e}")
            raise

    def extract_with_limit(self, char_limit: int = 1000000) -> Tuple[str, int, int]:
        """
        Extract text up to a character limit.

        Returns:
            Tuple containing:
            - Extracted text (str)
            - Total characters extracted (int) (effectively processed_chars)
            - Total characters in document (int) (estimated if truncated, exact if not)

        Note: Calculating 'Total characters in document' exactly requires reading the whole file,
        which defeats the purpose of streaming if we just want to stop early.
        However, for the audit trail, we might want to know the total size.

        If we want STRICT bounded memory, we can't load everything to count.
        But for the audit trail (SPEC-001), we need 'total_chars'.

        Compromise:
        1. Extract until limit is reached.
        2. If limit reached, continue iterating to just COUNT remaining length without storing.
        """
        if not PYMUPDF_AVAILABLE:
            raise RuntimeError("PyMuPDF (fitz) is not installed. Cannot extract PDF text.")

        text_builder = []
        current_length = 0
        total_length = 0
        truncated = False

        try:
            doc = fitz.open(self.pdf_path)

            for page in doc:
                page_text = page.get_text()
                page_len = len(page_text)
                total_length += page_len

                if not truncated:
                    if current_length + page_len <= char_limit:
                        text_builder.append(page_text)
                        current_length += page_len
                    else:
                        # Take partial text to hit exact limit
                        remaining = char_limit - current_length
                        text_builder.append(page_text[:remaining])
                        current_length += remaining
                        truncated = True
                        # Continue loop just to count total_length
                else:
                    # Already truncated, just counting total_length
                    pass

            doc.close()

            return "".join(text_builder), current_length, total_length

        except Exception as e:
            logger.error(f"Error in extract_with_limit: {e}")
            raise
