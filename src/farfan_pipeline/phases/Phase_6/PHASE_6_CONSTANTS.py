"""
Phase 6 Constants - Cluster Aggregation (MESO)

This module re-exports constants from the implementation module for backward compatibility
and standardized naming conventions.

Module: src/farfan_pipeline/phases/Phase_6/PHASE_6_CONSTANTS.py
Purpose: Constants re-export for Phase 6
Owner: phase6_00
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-13
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 6
__stage__ = 0
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13T00:00:00Z"
__modified__ = "2026-01-13T00:00:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

# Re-export all constants from the implementation module
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
