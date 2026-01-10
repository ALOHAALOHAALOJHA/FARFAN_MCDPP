"""
Quality Levels Primitive - Phase 4-7
=====================================

This module provides quality level determination primitives for the
hierarchical aggregation pipeline. It defines quality thresholds and
provides functions to classify aggregated scores into quality levels.

Quality Levels:
    - EXCELENTE: Score >= 2.5 (High quality, robust aggregation)
    - BUENO: Score >= 2.0 (Good quality, reliable aggregation)
    - ACEPTABLE: Score >= 1.5 (Acceptable quality, usable with caution)
    - INSUFICIENTE: Score < 1.5 (Insufficient quality, requires review)

Author: F.A.R.F.A.N. Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from ..PHASE_4_7_CONSTANTS import (
    MAX_SCORE,
    MIN_SCORE,
    QUALITY_LEVEL_ACEPTABLE,
    QUALITY_LEVEL_BUENO,
    QUALITY_LEVEL_EXCELENTE,
    QUALITY_LEVEL_INSUFICIENTE,
    QUALITY_THRESHOLD_ACEPTABLE_MIN,
    QUALITY_THRESHOLD_BUENO_MIN,
    QUALITY_THRESHOLD_EXCELENTE_MIN,
)

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """
    Enumeration of quality levels for aggregated scores.

    The quality level indicates the reliability and robustness of the
    aggregation process and the resulting score.
    """

    EXCELENTE = QUALITY_LEVEL_EXCELENTE
    BUENO = QUALITY_LEVEL_BUENO
    ACEPTABLE = QUALITY_LEVEL_ACEPTABLE
    INSUFICIENTE = QUALITY_LEVEL_INSUFICIENTE

    def __str__(self) -> str:
        return self.value

    @property
    def is_sufficient(self) -> bool:
        """Check if quality level is sufficient for use."""
        return self != QualityLevel.INSUFICIENTE

    @property
    def is_good(self) -> bool:
        """Check if quality level is good or better."""
        return self in (QualityLevel.BUENO, QualityLevel.EXCELENTE)

    @property
    def is_excellent(self) -> bool:
        """Check if quality level is excellent."""
        return self == QualityLevel.EXCELENTE


@dataclass(frozen=True)
class QualityLevelThresholds:
    """
    Immutable container for quality level thresholds.

    Attributes:
        excelente_min: Minimum score for EXCELENTE level
        bueno_min: Minimum score for BUENO level
        aceptable_min: Minimum score for ACEPTABLE level
        min_score: Minimum possible score
        max_score: Maximum possible score
    """

    excelente_min: float = QUALITY_THRESHOLD_EXCELENTE_MIN
    bueno_min: float = QUALITY_THRESHOLD_BUENO_MIN
    aceptable_min: float = QUALITY_THRESHOLD_ACEPTABLE_MIN
    min_score: float = MIN_SCORE
    max_score: float = MAX_SCORE

    def validate(self) -> bool:
        """
        Validate that thresholds are properly ordered.

        Returns:
            True if thresholds are valid (min < aceptable < bueno < excelente < max)
        """
        return (
            self.min_score
            < self.aceptable_min
            < self.bueno_min
            < self.excelente_min
            < self.max_score
        )


# Default thresholds instance
DEFAULT_THRESHOLDS = QualityLevelThresholds()


def determine_quality_level(
    score: float,
    thresholds: QualityLevelThresholds | None = None,
) -> QualityLevel:
    """
    Determine quality level from aggregated score.

    Args:
        score: Aggregated score (typically in [0, 3] range)
        thresholds: Optional custom thresholds (uses default if None)

    Returns:
        QualityLevel enum value

    Raises:
        ValueError: If score is outside valid range
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    # Validate score range
    if not (thresholds.min_score <= score <= thresholds.max_score):
        logger.warning(
            f"Score {score:.4f} outside valid range [{thresholds.min_score}, {thresholds.max_score}]. "
            f"Clamping for quality determination."
        )
        score = max(thresholds.min_score, min(thresholds.max_score, score))

    # Determine quality level
    if score >= thresholds.excelente_min:
        return QualityLevel.EXCELENTE
    elif score >= thresholds.bueno_min:
        return QualityLevel.BUENO
    elif score >= thresholds.aceptable_min:
        return QualityLevel.ACEPTABLE
    else:
        return QualityLevel.INSUFICIENTE


def determine_quality_level_str(
    score: float,
    thresholds: QualityLevelThresholds | None = None,
) -> str:
    """
    Determine quality level as string from aggregated score.

    Args:
        score: Aggregated score (typically in [0, 3] range)
        thresholds: Optional custom thresholds (uses default if None)

    Returns:
        Quality level string (e.g., "EXCELENTE", "BUENO")
    """
    return determine_quality_level(score, thresholds).value


def get_quality_score_delta(
    score: float,
    target_level: QualityLevel,
    thresholds: QualityLevelThresholds | None = None,
) -> float:
    """
    Calculate the delta between score and target quality level threshold.

    Positive delta means score is above threshold (good).
    Negative delta means score is below threshold (needs improvement).

    Args:
        score: Current aggregated score
        target_level: Target quality level
        thresholds: Optional custom thresholds (uses default if None)

    Returns:
        Delta score (can be positive or negative)
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    if target_level == QualityLevel.EXCELENTE:
        threshold = thresholds.excelente_min
    elif target_level == QualityLevel.BUENO:
        threshold = thresholds.bueno_min
    elif target_level == QualityLevel.ACEPTABLE:
        threshold = thresholds.aceptable_min
    else:
        threshold = thresholds.min_score

    return score - threshold


def get_quality_improvement_needed(
    score: float,
    target_level: QualityLevel,
    thresholds: QualityLevelThresholds | None = None,
) -> float | None:
    """
    Calculate improvement needed to reach target quality level.

    Returns None if score already meets or exceeds target level.

    Args:
        score: Current aggregated score
        target_level: Target quality level
        thresholds: Optional custom thresholds (uses default if None)

    Returns:
        Required improvement (positive float), or None if already at target
    """
    delta = get_quality_score_delta(score, target_level, thresholds)
    if delta >= 0:
        return None
    return -delta


def format_quality_report(
    score: float,
    quality_level: QualityLevel | None = None,
    thresholds: QualityLevelThresholds | None = None,
) -> str:
    """
    Format a human-readable quality report.

    Args:
        score: Aggregated score
        quality_level: Optional pre-computed quality level
        thresholds: Optional custom thresholds

    Returns:
        Formatted quality report string
    """
    if quality_level is None:
        quality_level = determine_quality_level(score, thresholds)

    report = f"Score: {score:.4f} / {MAX_SCORE:.1f}\n"
    report += f"Quality Level: {quality_level.value}\n"

    # Add improvement suggestions for insufficient quality
    if quality_level == QualityLevel.INSUFICIENTE:
        improvement = get_quality_improvement_needed(score, QualityLevel.ACEPTABLE, thresholds)
        if improvement is not None:
            report += f"Improvement needed for ACEPTABLE: +{improvement:.4f}\n"

    return report


# Export all public functions and classes
__all__ = [
    "DEFAULT_THRESHOLDS",
    "QualityLevel",
    "QualityLevelThresholds",
    "determine_quality_level",
    "determine_quality_level_str",
    "format_quality_report",
    "get_quality_improvement_needed",
    "get_quality_score_delta",
]
