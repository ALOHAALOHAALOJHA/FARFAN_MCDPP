"""
Phase Zero: Input Validation
=============================

Phase 0 of the F.A.R.F.A.N pipeline responsible for validating and normalizing
input documents before they enter the main processing pipeline.

This phase ensures that all inputs meet the required preconditions for
downstream phases.

CANONICAL LOCATION: Phase 0 validation contract is in Phase_one/phase0_input_validation.py
Access via explicit imports to avoid heavy dependency loading.
"""

def __getattr__(name):
    """Lazy import to avoid loading heavy Phase_one dependencies at import time."""
    if name in ("Phase0Input", "CanonicalInput", "Phase0ValidationContract", "PHASE0_VERSION"):
        from canonic_phases.Phase_one.phase0_input_validation import (
            Phase0Input,
            CanonicalInput,
            Phase0ValidationContract,
            PHASE0_VERSION,
        )
        globals()[name] = locals()[name]
        return locals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "Phase0Input",
    "CanonicalInput",
    "Phase0ValidationContract",
    "PHASE0_VERSION",
]
