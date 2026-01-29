"""
Phase 7 Interphase Bridge Package
==================================

This package provides explicit handoff contracts between Phase 6 and Phase 7.

The primary module defines the transformation from Phase 6 output (ClusterScore list)
to Phase 7 input (validated cluster scores for macro aggregation).

Version: 1.0.0
Author: F.A.R.F.A.N Core Architecture Team
"""

from farfan_pipeline.phases.Phase_07.interphase.phase6_to_phase7_bridge import (
    Phase6OutputContract,
    Phase6ToPhase7BridgeError,
    bridge_phase6_to_phase7,
    extract_from_cluster_scores,
    validate_phase6_output_for_phase7,
)

__all__ = [
    "Phase6OutputContract",
    "Phase6ToPhase7BridgeError",
    "bridge_phase6_to_phase7",
    "extract_from_cluster_scores",
    "validate_phase6_output_for_phase7",
]
