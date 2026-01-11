"""
Phase 6: Cluster Aggregation (MESO)

This module provides the Phase 6 aggregation components for the FARFAN pipeline.
Phase 6 aggregates 10 AreaScore outputs into 4 ClusterScore values.

Module: src/farfan_pipeline/phases/Phase_6/__init__.py
Purpose: Package façade for Phase 6
Owner: phase6_00
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-01-09
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 6
__stage__ = 0
__order__ = 0
__author__ = "GNEA-Enforcement"
__created__ = "2025-01-09T00:00:00Z"
__modified__ = "2025-01-09T00:00:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

from .phase6_10_00_phase_6_constants import (
    CLUSTER_COMPOSITION,
    CLUSTERS,
    COHERENCE_THRESHOLD_HIGH,
    COHERENCE_THRESHOLD_LOW,
    DISPERSION_THRESHOLDS,
    EXPECTED_CLUSTER_SCORE_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    PENALTY_WEIGHT,
    DispersionScenario,
    Phase6Invariants,
)

__all__ = [
    "CLUSTERS",
    "CLUSTER_COMPOSITION",
    "COHERENCE_THRESHOLD_HIGH",
    "COHERENCE_THRESHOLD_LOW",
    "DISPERSION_THRESHOLDS",
    "EXPECTED_CLUSTER_SCORE_COUNT",
    "MAX_SCORE",
    "MIN_SCORE",
    "PENALTY_WEIGHT",
    "DispersionScenario",
    "Phase6Invariants",
]
