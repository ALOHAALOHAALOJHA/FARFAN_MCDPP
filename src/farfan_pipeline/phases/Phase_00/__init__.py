"""
Phase 0: Validation, Hardening & Bootstrap
==========================================

The foundational layer of the F.A.R.F.A.N pipeline that executes before any
analytical computation. It guarantees a deterministic, resource-bounded, and
validated environment.
"""

from .phase0_90_01_verified_pipeline_runner import VerifiedPipelineRunner
from .phase0_40_00_input_validation import (
    Phase0Input,
    CanonicalInput,
    Phase0ValidationContract,
    validate_phase0_input,
)
from .phase0_50_01_exit_gates import GateResult, check_all_gates

__all__ = [
    "VerifiedPipelineRunner",
    "Phase0Input",
    "CanonicalInput",
    "Phase0ValidationContract",
    "validate_phase0_input",
    "GateResult",
    "check_all_gates",
]
