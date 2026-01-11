"""
Phase 1 Protocols - Abstract Interfaces.

Purpose: Define contracts for Phase 1 components to enable testing and substitution.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State:  ACTIVE
"""

from collections.abc import Generator
from pathlib import Path
from typing import Any, Protocol


class PDFExtractorProtocol(Protocol):
    """Protocol for PDF text extraction implementations."""

    def extract_text_stream(self) -> Generator[str, None, None]:
        """Yield text page by page."""
        ...

    def extract_with_limit(self, char_limit: int) -> tuple[str, int, int]:
        """
        Extract text up to character limit.

        Returns:
            Tuple of (extracted_text, processed_chars, total_chars)
        """
        ...


class TruncationAuditProtocol(Protocol):
    """Protocol for truncation audit records."""

    total_chars: int
    processed_chars: int
    chars_lost: int
    loss_ratio: float
    limit_applied: int
    was_truncated: bool

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        ...

    def log_if_truncated(self) -> None:
        """Log warning if truncation occurred."""
        ...


class ChunkProtocol(Protocol):
    """Protocol for chunk representations."""

    chunk_id: str
    policy_area_id: str
    dimension_id: str
    text: str
    assignment_method: str
    semantic_confidence: float


class Phase1ExecutorProtocol(Protocol):
    """Protocol for Phase 1 execution."""

    def execute(self, pdf_path: Path) -> list[Any]:
        """Execute Phase 1 pipeline and return SmartChunks."""
        ...
