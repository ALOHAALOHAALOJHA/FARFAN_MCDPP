"""
Phase Zero: Input Validation
=============================

Phase 0 of the F.A.R.F.A.N pipeline responsible for validating and normalizing
input documents before they enter the main processing pipeline.

This phase ensures that all inputs meet the required preconditions for
downstream phases.

CANONICAL LOCATION: Phase 0 validation contract is in Phase_one/phase0_input_validation.py
This __init__ re-exports for backward compatibility.
"""

# Re-export Phase 0 validation components from their canonical location
from canonic_phases.Phase_one.phase0_input_validation import (
    Phase0Input,
    CanonicalInput,
    Phase0ValidationContract,
    PHASE0_VERSION,
)

__all__ = [
    "Phase0Input",
    "CanonicalInput",
    "Phase0ValidationContract",
    "PHASE0_VERSION",
]
