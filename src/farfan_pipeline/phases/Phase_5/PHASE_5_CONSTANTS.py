"""
Phase 5 Constants - Policy Area Aggregation

This module defines constants and configuration for Phase 5 of the FARFAN pipeline:
Policy Area Aggregation (60 DimensionScore → 10 AreaScore).

Module: src/farfan_pipeline/phases/Phase_5/PHASE_5_CONSTANTS.py
Purpose: Define constants for Phase 5
Owner: phase5_10
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-01-09
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 5
__stage__ = 10
__order__ = 0
__author__ = "GNEA-Enforcement"
__created__ = "2025-01-09T00:00:00Z"
__modified__ = "2025-01-09T00:00:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

from enum import Enum

# Policy Area identifiers (10 total)
POLICY_AREAS = ["PA01", "PA02", "PA03", "PA04", "PA05", "PA06", "PA07", "PA08", "PA09", "PA10"]

# Expected output count for Phase 5
EXPECTED_AREA_SCORE_COUNT = 10

# Dimensions per policy area (hermeticity requirement)
DIMENSIONS_PER_AREA = 6

# Dimension identifiers for hermeticity validation
DIMENSION_IDS = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]

# Cluster assignments (for Phase 6 transition)
CLUSTER_ASSIGNMENTS = {
    "CLUSTER_MESO_1": ["PA01", "PA02", "PA03"],
    "CLUSTER_MESO_2": ["PA04", "PA05", "PA06"],
    "CLUSTER_MESO_3": ["PA07", "PA08"],
    "CLUSTER_MESO_4": ["PA09", "PA10"],
}

# Score bounds (3-point scale)
MIN_SCORE = 0.0
MAX_SCORE = 3.0

# Hermeticity validation tolerance
HERMETICITY_TOLERANCE = 1e-6


class QualityLevel(Enum):
    """Quality levels for area scores."""

    EXCELENTE = "EXCELENTE"
    BUENO = "BUENO"
    ACEPTABLE = "ACEPTABLE"
    INSUFICIENTE = "INSUFICIENTE"


# Quality level thresholds (normalized)
QUALITY_THRESHOLDS = {"EXCELENTE": 0.85, "BUENO": 0.70, "ACEPTABLE": 0.55, "INSUFICIENTE": 0.0}


# Phase 5 validation invariants
class Phase5Invariants:
    """Invariant checks for Phase 5 output."""

    @staticmethod
    def validate_count(area_scores):
        """Validate that exactly 10 area scores are produced."""
        return len(area_scores) == EXPECTED_AREA_SCORE_COUNT

    @staticmethod
    def validate_hermeticity(area_score):
        """Validate that all 6 dimensions are present."""
        return len(area_score.dimension_scores) == DIMENSIONS_PER_AREA

    @staticmethod
    def validate_bounds(score):
        """Validate score is within [0.0, 3.0]."""
        return MIN_SCORE <= score <= MAX_SCORE
