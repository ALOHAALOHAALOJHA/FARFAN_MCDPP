"""
Canonical Quality Levels Module
================================

Quality level enumeration and scoring thresholds aligned with
Phase Three (src/farfan_pipeline/phases/Phase_three/primitives/quality_levels.py).

This module provides the canonical quality assessment levels used across
the questionnaire central and Phase 3 scoring.

Alignment Contract:
-------------------
Quality levels and thresholds MUST match Phase Three primitives exactly:
- EXCELENTE: score >= 0.85 (Spanish form, matches Phase 3 usage)
- BUENO: score >= 0.70 (Spanish form, new canonical)
- ACEPTABLE: score >= 0.55 (Spanish form, matches Phase 3 usage)
- INSUFICIENTE: score < 0.55 (Spanish form, matches Phase 3 usage)

Note: Phase 3 also has English variants (EXCELLENT, GOOD, ADEQUATE, POOR)
but the canonical scoring uses Spanish forms for consistency.

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
Aligned with: Phase Three primitives v1.0.0
"""

from __future__ import annotations

from enum import Enum
from typing import Final

# =============================================================================
# QUALITY LEVEL ENUMERATION
# =============================================================================


class QualityLevel(Enum):
    """Canonical quality assessment levels (Spanish).

    Aligned with Phase Three quality_levels.py:
    - EXCELENTE matches EXCELLENT in Phase 3
    - BUENO matches GOOD in Phase 3
    - ACEPTABLE matches ADEQUATE in Phase 3
    - INSUFICIENTE matches POOR in Phase 3

    The Spanish forms are canonical for questionnaire central.
    """

    EXCELENTE = "EXCELENTE"  # >= 0.85
    BUENO = "BUENO"  # >= 0.70
    ACEPTABLE = "ACEPTABLE"  # >= 0.55
    INSUFICIENTE = "INSUFICIENTE"  # < 0.55
    NO_APLICABLE = "NO_APLICABLE"  # Not applicable
    ERROR = "ERROR"  # Scoring error occurred


# =============================================================================
# SCORING THRESHOLDS
# =============================================================================

# Threshold values (MUST match Phase Three)
THRESHOLD_EXCELENTE: Final[float] = 0.85
THRESHOLD_BUENO: Final[float] = 0.70
THRESHOLD_ACEPTABLE: Final[float] = 0.55
THRESHOLD_INSUFICIENTE: Final[float] = 0.0

# Valid quality levels for validation
VALID_QUALITY_LEVELS: Final[tuple[str, ...]] = tuple(level.value for level in QualityLevel)


# =============================================================================
# QUALITY LEVEL DETERMINATION
# =============================================================================


def determine_quality_level(score: float) -> str:
    """Determine quality level from normalized score.

    Args:
        score: Normalized score in range [0.0, 1.0]

    Returns:
        Quality level string from VALID_QUALITY_LEVELS

    Raises:
        ValueError: If score is not in [0.0, 1.0]
    """
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"Score must be in [0.0, 1.0], got {score}")

    if score >= THRESHOLD_EXCELENTE:
        return QualityLevel.EXCELENTE.value
    elif score >= THRESHOLD_BUENO:
        return QualityLevel.BUENO.value
    elif score >= THRESHOLD_ACEPTABLE:
        return QualityLevel.ACEPTABLE.value
    else:
        return QualityLevel.INSUFICIENTE.value


def determine_quality_level_from_completeness(completeness: str | None) -> str:
    """Map EvidenceNexus completeness to quality level.

    Aligned with Phase Three phase3_score_extraction.py:
    - "complete" → "EXCELENTE"
    - "partial" → "ACEPTABLE"
    - "insufficient" → "INSUFICIENTE"
    - "not_applicable" → "NO_APLICABLE"

    Args:
        completeness: Completeness enum from EvidenceNexus

    Returns:
        Quality level string
    """
    if not completeness:
        return QualityLevel.INSUFICIENTE.value

    completeness_lower = completeness.lower()

    mapping = {
        "complete": QualityLevel.EXCELENTE.value,
        "partial": QualityLevel.ACEPTABLE.value,
        "insufficient": QualityLevel.INSUFICIENTE.value,
        "not_applicable": QualityLevel.NO_APLICABLE.value,
    }

    return mapping.get(completeness_lower, QualityLevel.INSUFICIENTE.value)


def is_valid_quality_level(level: str) -> bool:
    """Check if quality level is valid.

    Args:
        level: Quality level string to validate

    Returns:
        True if level is in VALID_QUALITY_LEVELS
    """
    return level in VALID_QUALITY_LEVELS


def get_color_for_quality(level: str) -> str:
    """Get color code for quality level.

    Aligned with scoring_system.json colors:
    - EXCELENTE: green
    - BUENO: blue
    - ACEPTABLE: yellow
    - INSUFICIENTE: red

    Args:
        level: Quality level string

    Returns:
        Color name string
    """
    colors = {
        QualityLevel.EXCELENTE.value: "green",
        QualityLevel.BUENO.value: "blue",
        QualityLevel.ACEPTABLE.value: "yellow",
        QualityLevel.INSUFICIENTE.value: "red",
        QualityLevel.NO_APLICABLE.value: "gray",
        QualityLevel.ERROR.value: "black",
    }
    return colors.get(level, "gray")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enum
    "QualityLevel",
    # Constants
    "THRESHOLD_EXCELENTE",
    "THRESHOLD_BUENO",
    "THRESHOLD_ACEPTABLE",
    "THRESHOLD_INSUFICIENTE",
    "VALID_QUALITY_LEVELS",
    # Functions
    "determine_quality_level",
    "determine_quality_level_from_completeness",
    "is_valid_quality_level",
    "get_color_for_quality",
]
