"""
Phase 7 Constants - Macro Evaluation

This module re-exports constants from the implementation module for backward compatibility
and standardized naming conventions.

Module: src/farfan_pipeline/phases/Phase_07/PHASE_7_CONSTANTS.py
Purpose: Constants re-export for Phase 7
Owner: phase7_10
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-20
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 7
__stage__ = 0
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-20T00:00:00Z"
__modified__ = "2026-01-20T00:00:00Z"
__criticality__ = "CRITICAL"
__execution_pattern__ = "Per-Task"

# Re-export all constants from the implementation module
from .phase7_10_00_phase_7_constants import (
    ALIGNMENT_THRESHOLD_HIGH,
    ALIGNMENT_THRESHOLD_LOW,
    ALIGNMENT_THRESHOLD_MEDIUM,
    CLUSTER_WEIGHTS,
    COHERENCE_THRESHOLD_ACCEPTABLE,
    COHERENCE_THRESHOLD_EXCELLENT,
    COHERENCE_THRESHOLD_GOOD,
    COHERENCE_WEIGHT_INSTITUTIONAL,
    COHERENCE_WEIGHT_OPERATIONAL,
    COHERENCE_WEIGHT_STRATEGIC,
    EXPECTED_MACRO_SCORE_COUNT,
    INPUT_CLUSTERS,
    MAX_SCORE,
    MIN_SCORE,
    MacroInvariants,
    QualityLevel,
    QUALITY_THRESHOLDS,
    SYSTEMIC_GAP_THRESHOLD,
)

__all__ = [
    "ALIGNMENT_THRESHOLD_HIGH",
    "ALIGNMENT_THRESHOLD_LOW",
    "ALIGNMENT_THRESHOLD_MEDIUM",
    "CLUSTER_WEIGHTS",
    "COHERENCE_THRESHOLD_ACCEPTABLE",
    "COHERENCE_THRESHOLD_EXCELLENT",
    "COHERENCE_THRESHOLD_GOOD",
    "COHERENCE_WEIGHT_INSTITUTIONAL",
    "COHERENCE_WEIGHT_OPERATIONAL",
    "COHERENCE_WEIGHT_STRATEGIC",
    "EXPECTED_MACRO_SCORE_COUNT",
    "INPUT_CLUSTERS",
    "MAX_SCORE",
    "MIN_SCORE",
    "MacroInvariants",
    "QualityLevel",
    "QUALITY_THRESHOLDS",
    "SYSTEMIC_GAP_THRESHOLD",
]
