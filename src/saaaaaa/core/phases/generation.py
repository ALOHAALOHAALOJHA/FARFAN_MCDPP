"""
Phase Generation Shim
======================

This module provides compatibility mapping from legacy phase names to
the new canonical phase system.

Legacy auditors expect `generation` module. This currently maps to
Phase 2 (microquestions), though in the modern architecture, generation
happens across multiple phases.

For new code, use the canonical phase modules directly:
- phase0_input_validation
- phase1_spc_ingestion
- phase2_types
"""

# Re-export Phase 2 types as "generation"
from saaaaaa.core.phases.phase2_types import (
    Phase2QuestionResult,
    Phase2Result,
    validate_phase2_result,
)

__all__ = [
    "Phase2QuestionResult",
    "Phase2Result",
    "validate_phase2_result",
]
