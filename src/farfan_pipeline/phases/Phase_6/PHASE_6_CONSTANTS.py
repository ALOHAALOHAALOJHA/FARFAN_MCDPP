"""
Phase 6 Constants - Cluster Aggregation (MESO)

This module defines constants and configuration for Phase 6 of the FARFAN pipeline:
Cluster Aggregation (10 AreaScore → 4 ClusterScore).

Module: src/farfan_pipeline/phases/Phase_6/PHASE_6_CONSTANTS.py
Purpose: Define constants for Phase 6
Owner: phase6_10
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-01-09
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 6
__stage__ = 10
__order__ = 0
__author__ = "GNEA-Enforcement"
__created__ = "2025-01-09T00:00:00Z"
__modified__ = "2025-01-09T00:00:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

from enum import Enum


# Cluster identifiers (4 total)
CLUSTERS = ["CLUSTER_MESO_1", "CLUSTER_MESO_2", "CLUSTER_MESO_3", "CLUSTER_MESO_4"]

# Expected output count for Phase 6
EXPECTED_CLUSTER_SCORE_COUNT = 4

# Cluster composition (policy areas per cluster)
CLUSTER_COMPOSITION = {
    "CLUSTER_MESO_1": ["PA01", "PA02", "PA03"],
    "CLUSTER_MESO_2": ["PA04", "PA05", "PA06"],
    "CLUSTER_MESO_3": ["PA07", "PA08"],
    "CLUSTER_MESO_4": ["PA09", "PA10"],
}

# Score bounds (3-point scale)
MIN_SCORE = 0.0
MAX_SCORE = 3.0

# Dispersion metrics thresholds
DISPERSION_THRESHOLDS = {
    "CV_CONVERGENCE": 0.2,  # Coefficient of variation < 0.2 = convergence
    "CV_MODERATE": 0.4,  # CV < 0.4 = moderate dispersion
    "CV_HIGH": 0.6,  # CV < 0.6 = high dispersion
    "CV_EXTREME": 1.0,  # CV >= 0.6 = extreme dispersion
}

# Adaptive penalty weights
PENALTY_WEIGHT = 0.3

# Coherence thresholds
COHERENCE_THRESHOLD_LOW = 0.5
COHERENCE_THRESHOLD_HIGH = 0.8


class DispersionScenario(Enum):
    """Dispersion classification scenarios."""

    CONVERGENCE = "convergence"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


# Phase 6 validation invariants
class Phase6Invariants:
    """Invariant checks for Phase 6 output."""

    @staticmethod
    def validate_count(cluster_scores):
        """Validate that exactly 4 cluster scores are produced."""
        return len(cluster_scores) == EXPECTED_CLUSTER_SCORE_COUNT

    @staticmethod
    def validate_cluster_hermeticity(cluster_score):
        """Validate that all expected policy areas are present."""
        cluster_id = cluster_score.cluster_id
        expected_areas = CLUSTER_COMPOSITION.get(cluster_id, [])
        return len(cluster_score.area_scores) == len(expected_areas)

    @staticmethod
    def validate_bounds(score):
        """Validate score is within [0.0, 3.0]."""
        return MIN_SCORE <= score <= MAX_SCORE

    @staticmethod
    def classify_dispersion(cv):
        """Classify dispersion scenario based on coefficient of variation."""
        if cv < DISPERSION_THRESHOLDS["CV_CONVERGENCE"]:
            return DispersionScenario.CONVERGENCE
        elif cv < DISPERSION_THRESHOLDS["CV_MODERATE"]:
            return DispersionScenario.MODERATE
        elif cv < DISPERSION_THRESHOLDS["CV_HIGH"]:
            return DispersionScenario.HIGH
        else:
            return DispersionScenario.EXTREME
