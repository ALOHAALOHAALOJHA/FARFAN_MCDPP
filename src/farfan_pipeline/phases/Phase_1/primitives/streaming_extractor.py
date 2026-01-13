"""
Streaming PDF Text Extraction with Bounded Memory. 

Purpose: Extract PDF text without loading entire document into memory.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State: ACTIVE

SPEC-001: Enforces character limit with audit trail.
SPEC-003: Streaming extraction minimizes memory footprint.
"""

from typing import Generator, Tuple
import logging
from pathlib import Path

from ..PHASE_1_CONSTANTS import PDF_EXTRACTION_CHAR_LIMIT, PHASE1_LOGGER_NAME

try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

logger = logging.getLogger(PHASE1_LOGGER_NAME)


class StreamingPDFExtractor: 
    """
    Extracts text from PDFs in a streaming fashion to minimize memory usage.
    
    Resource Management:
        All PDF document handles are guaranteed to be closed via try/finally blocks,
        even when exceptions occur during iteration.
    """

    def __init__(self, pdf_path: Path) -> None:
        self.pdf_path = pdf_path

    def extract_text_stream(self) -> Generator[str, None, None]: 
        """
        Yields text from the PDF page by page, minimizing memory usage. 
        
        Raises:
            RuntimeError: If PyMuPDF is not installed. 
            FileNotFoundError: If PDF file does not exist.
        """
        if not PYMUPDF_AVAILABLE:
            raise RuntimeError("PyMuPDF (fitz) is not installed.  Cannot extract PDF text.")

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        doc = None
        try: 
            doc = fitz.open(self.pdf_path)
            try:
                for page in doc:
                    yield page.get_text()
            finally:
                doc.close()
        except Exception:
            logger.exception(f"Error during streaming PDF extraction from {self.pdf_path}")
            raise

    def extract_with_limit(
        self, 
        char_limit: int = PDF_EXTRACTION_CHAR_LIMIT
    ) -> Tuple[str, int, int]:
        """
        Extract text up to a character limit. 

        Args:
            char_limit: Maximum characters to extract. Defaults to PDF_EXTRACTION_CHAR_LIMIT.

        Returns:
            Tuple containing: 
            - Extracted text (str)
            - Total characters extracted/processed (int)
            - Total characters in document (int)

        Raises: 
            RuntimeError: If PyMuPDF is not installed.
            FileNotFoundError: If PDF file does not exist. 

        Note:
            DESIGN TRADE-OFF (see docs/TRADE_OFFS.md):
            After truncation, iteration continues to count total_length for audit accuracy.
            This is a deliberate trade-off:  audit completeness vs. early termination.
            For extremely large PDFs (>10M chars), consider sampling-based estimation.
        """
        if not PYMUPDF_AVAILABLE:
            raise RuntimeError("PyMuPDF (fitz) is not installed. Cannot extract PDF text.")

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        text_builder:  list[str] = []
        current_length = 0
        total_length = 0
        truncated = False

        doc = None
        try:
            doc = fitz.open(self.pdf_path)
            try:
                for page in doc:
                    page_text = page.get_text()
                    page_len = len(page_text)
                    total_length += page_len

                    if not truncated:
                        if current_length + page_len <= char_limit: 
                            text_builder.append(page_text)
                            current_length += page_len
                        else:
                            remaining = char_limit - current_length
                            text_builder.append(page_text[:remaining])
                            current_length += remaining
                            truncated = True
                    # After truncation:  continue counting total_length only
            finally:
                doc.close()

            return "".join(text_builder), current_length, total_length

        except Exception: 
            logger.exception(f"Error in extract_with_limit for {self.pdf_path}")
            raise
