"""
Phase 6 Constants - Cluster Aggregation (MESO)

This module re-exports configuration from the unified scoring config
and defines cluster composition constants.

Module: src/farfan_pipeline/phases/Phase_06/PHASE_6_CONSTANTS.py
Purpose: Define constants for Phase 6
Owner: phase6_10
Lifecycle: ACTIVE
Version: 2.0.0
Effective-Date: 2026-01-16

CHANGELOG v2.0.0:
- Migrated scoring parameters to phase6_10_01_scoring_config.py
- This file now re-exports from unified config for backwards compatibility
- Cluster composition constants remain here (domain-specific, not scoring)

CHANGELOG v2.0.1:
- Made CLUSTER_COMPOSITION truly immutable using MappingProxyType
- Made CLUSTERS a tuple for immutability
"""
from __future__ import annotations

from types import MappingProxyType

__version__ = "2.0.1"
__phase__ = 6
__stage__ = 10
__order__ = 0
__author__ = "GNEA-Enforcement"
__created__ = "2025-01-09T00:00:00Z"
__modified__ = "2026-01-22T00:00:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

from farfan_pipeline.phases.Phase_06.phase6_10_01_scoring_config import (
    PHASE6_CONFIG,
    CoherenceQuality,
    DispersionScenario,
    COHERENCE_THRESHOLD_HIGH,
    COHERENCE_THRESHOLD_LOW,
    MAX_SCORE,
    MIN_SCORE,
    PENALTY_WEIGHT,
)

# Cluster identifiers (4 total) - immutable tuple
CLUSTERS = ("CLUSTER_MESO_1", "CLUSTER_MESO_2", "CLUSTER_MESO_3", "CLUSTER_MESO_4")

# Expected output count for Phase 6
EXPECTED_CLUSTER_SCORE_COUNT = 4

# Cluster composition (policy areas per cluster)
# IMMUTABLE: Uses MappingProxyType to prevent accidental modification
# Exponential benefit: Runtime guarantees of structural integrity
# - Prevents silent bugs from mutation
# - Enables safe sharing across threads
# - Compiler can optimize for read-only access
_CLUSTER_COMPOSITION_DICT = {
    "CLUSTER_MESO_1": ["PA01", "PA02", "PA03"],
    "CLUSTER_MESO_2": ["PA04", "PA05", "PA06"],
    "CLUSTER_MESO_3": ["PA07", "PA08"],
    "CLUSTER_MESO_4": ["PA09", "PA10"],
}
CLUSTER_COMPOSITION = MappingProxyType(_CLUSTER_COMPOSITION_DICT)

# Backwards compatibility exports
DISPERSION_THRESHOLDS = PHASE6_CONFIG.to_legacy_dispersion_thresholds()


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
        """Validate score is within bounds."""
        return MIN_SCORE <= score <= MAX_SCORE

    @staticmethod
    def validate_coherence_bounds(coherence):
        """Validate coherence is within [0.0, 1.0]."""
        return 0.0 <= coherence <= 1.0

    @staticmethod
    def validate_penalty_bounds(penalty):
        """Validate penalty is within [0.0, 1.0]."""
        return 0.0 <= penalty <= 1.0
