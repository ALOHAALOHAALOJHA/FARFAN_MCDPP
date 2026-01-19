"""
Phase 7 Constants - Macro Evaluation

This module defines constants and configuration for Phase 7 of the FARFAN pipeline:
Macro Evaluation (4 ClusterScore → 1 MacroScore).

Module: src/farfan_pipeline/phases/Phase_07/PHASE_7_CONSTANTS.py
Purpose: Define constants for Phase 7
Owner: phase7_10
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-01-09
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 7
__stage__ = 10
__order__ = 0
__author__ = "GNEA-Enforcement"
__created__ = "2025-01-09T00:00:00Z"
__modified__ = "2025-01-09T00:00:00Z"
__criticality__ = "CRITICAL"
__execution_pattern__ = "Per-Task"

from enum import Enum

# Input clusters (4 total)
INPUT_CLUSTERS = ["CLUSTER_MESO_1", "CLUSTER_MESO_2", "CLUSTER_MESO_3", "CLUSTER_MESO_4"]

# Expected output count for Phase 7
EXPECTED_MACRO_SCORE_COUNT = 1

# Score bounds (3-point scale)
MIN_SCORE = 0.0
MAX_SCORE = 3.0

# Cross-cutting coherence thresholds
COHERENCE_THRESHOLD_EXCELLENT = 0.85
COHERENCE_THRESHOLD_GOOD = 0.70
COHERENCE_THRESHOLD_ACCEPTABLE = 0.55

# Strategic alignment thresholds
ALIGNMENT_THRESHOLD_HIGH = 0.8
ALIGNMENT_THRESHOLD_MEDIUM = 0.6
ALIGNMENT_THRESHOLD_LOW = 0.4


class QualityLevel(Enum):
    """Quality levels for macro evaluation."""

    EXCELENTE = "EXCELENTE"
    BUENO = "BUENO"
    ACEPTABLE = "ACEPTABLE"
    INSUFICIENTE = "INSUFICIENTE"


# Quality level thresholds (normalized to [0,1])
QUALITY_THRESHOLDS = {"EXCELENTE": 0.85, "BUENO": 0.70, "ACEPTABLE": 0.55, "INSUFICIENTE": 0.0}


# Systemic gap identifiers
SYSTEMIC_GAP_THRESHOLD = 0.55  # Scores below this indicate gaps


class MacroInvariants:
    """Invariant checks for Phase 7 output."""

    @staticmethod
    def validate_single_output(macro_score):
        """Validate that exactly 1 macro score is produced."""
        return macro_score is not None

    @staticmethod
    def validate_bounds(score):
        """Validate score is within [0.0, 3.0]."""
        return MIN_SCORE <= score <= MAX_SCORE

    @staticmethod
    def validate_coherence(coherence):
        """Validate coherence is within [0.0, 1.0]."""
        return 0.0 <= coherence <= 1.0

    @staticmethod
    def validate_strategic_alignment(alignment):
        """Validate strategic alignment is within [0.0, 1.0]."""
        return 0.0 <= alignment <= 1.0

    @staticmethod
    def determine_quality_level(normalized_score):
        """Determine quality level based on normalized score."""
        if normalized_score >= QUALITY_THRESHOLDS["EXCELENTE"]:
            return QualityLevel.EXCELENTE
        elif normalized_score >= QUALITY_THRESHOLDS["BUENO"]:
            return QualityLevel.BUENO
        elif normalized_score >= QUALITY_THRESHOLDS["ACEPTABLE"]:
            return QualityLevel.ACEPTABLE
        else:
            return QualityLevel.INSUFICIENTE


# Macro evaluation weights
CLUSTER_WEIGHTS = {
    "CLUSTER_MESO_1": 0.25,
    "CLUSTER_MESO_2": 0.25,
    "CLUSTER_MESO_3": 0.25,
    "CLUSTER_MESO_4": 0.25,
}


# Cross-cutting coherence calculation parameters
COHERENCE_WEIGHT_STRATEGIC = 0.4
COHERENCE_WEIGHT_OPERATIONAL = 0.3
COHERENCE_WEIGHT_INSTITUTIONAL = 0.3
