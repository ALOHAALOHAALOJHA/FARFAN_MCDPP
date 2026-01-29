"""
Phase 1 Interphase Bridge Package
==================================

This package provides explicit handoff contracts between Phase 0 and Phase 1.
The primary module defines the transformation from Phase 0 output (WiringComponents)
to Phase 1 input (CanonicalInput).

Version: 1.0.0
Author: F.A.R.F.A.N Core Architecture Team
"""

from farfan_pipeline.phases.Phase_01.interphase.phase0_to_phase1_bridge import (
    Phase0OutputContract,
    Phase0ToPhase1BridgeError,
    bridge_phase0_to_phase1,
    extract_from_wiring_components,
    transform_to_canonical_input,
)

__all__ = [
    "Phase0OutputContract",
    "Phase0ToPhase1BridgeError",
    "bridge_phase0_to_phase1",
    "extract_from_wiring_components",
    "transform_to_canonical_input",
]
