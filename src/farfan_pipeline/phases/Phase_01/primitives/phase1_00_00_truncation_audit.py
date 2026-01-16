"""
Truncation Audit Module for Phase 1 SP1 Preprocessing.

Purpose: Provide auditable evidence of text truncation during ingestion.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State:  ACTIVE
"""

import logging
from dataclasses import dataclass
from typing import Any

from ..phase1_02_00_phase_1_constants import PHASE1_LOGGER_NAME

logger = logging.getLogger(PHASE1_LOGGER_NAME)


@dataclass
class TruncationAudit:
    """
    Audit record for text truncation.

    Attributes:
        total_chars:  Total number of characters in original source.
        processed_chars: Number of characters retained after truncation.
        chars_lost:  Number of characters lost (total - processed).
        loss_ratio:  Ratio of lost characters to total (0.0 to 1.0).
        limit_applied: The character limit that was applied.
        was_truncated: Boolean flag indicating if truncation occurred.
    """

    total_chars: int
    processed_chars: int
    chars_lost: int
    loss_ratio: float
    limit_applied: int
    was_truncated: bool

    @classmethod
    def create(cls, raw_text_len: int, processed_text_len: int, limit: int) -> "TruncationAudit":
        """Create a truncation audit record."""
        chars_lost = max(0, raw_text_len - processed_text_len)
        loss_ratio = chars_lost / raw_text_len if raw_text_len > 0 else 0.0
        was_truncated = chars_lost > 0

        return cls(
            total_chars=raw_text_len,
            processed_chars=processed_text_len,
            chars_lost=chars_lost,
            loss_ratio=loss_ratio,
            limit_applied=limit,
            was_truncated=was_truncated,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_chars": self.total_chars,
            "processed_chars": self.processed_chars,
            "chars_lost": self.chars_lost,
            "loss_ratio": self.loss_ratio,
            "limit_applied": self.limit_applied,
            "was_truncated": self.was_truncated,
        }

    def log_if_truncated(self) -> None:
        """Log a warning if truncation occurred."""
        if self.was_truncated:
            logger.warning(
                f"TRUNCATION AUDIT:  Document truncated. "
                f"Lost {self.chars_lost} chars ({self.loss_ratio:.2%}). "
                f"Processed:  {self.processed_chars}/{self.total_chars}. "
                f"Limit: {self.limit_applied}"
            )
        else:
            logger.info("TRUNCATION AUDIT: No truncation occurred.")
