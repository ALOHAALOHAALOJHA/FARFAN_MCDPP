"""
Contract: QualityLevel Enum
===========================

Provides the canonical QualityLevel enum used across Phase 3 and Phase 4.
Extracted from legacy scoring.py.
"""

from enum import Enum


class QualityLevel(Enum):
    """Quality assessment levels aligned with calibration thresholds."""

    EXCELLENT = "EXCELLENT"  # ≥ 0.85
    GOOD = "GOOD"  # ≥ 0.70
    ADEQUATE = "ADEQUATE"  # ≥ 0.50
    POOR = "POOR"  # < 0.50
    INSUFFICIENTE = "INSUFICIENTE"  # For fallback compatibility
    NO_APLICABLE = "NO_APLICABLE"
    ACEPTABLE = "ACEPTABLE"  # Spanish alias for ADEQUATE/GOOD sometimes used in legacy
