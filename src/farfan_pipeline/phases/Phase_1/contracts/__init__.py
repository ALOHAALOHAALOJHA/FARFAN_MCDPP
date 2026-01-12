"""Phase 1 Contracts - Execution Contracts and Constitutional Invariants.

This package contains the formal contracts governing Phase 1 execution:
- Mission Contract: Weight-based execution specification
- Input Contract: Phase 0 → Phase 1 interface preconditions
- Output Contract: Phase 1 → Phase 2 interface postconditions
- Constitutional Contract: 60-chunk invariant enforcement
"""

from __future__ import annotations

from farfan_pipeline.phases.Phase_1.contracts.phase1_constitutional_contract import (
    EXPECTED_CHUNK_COUNT,
    EXPECTED_DIMENSION_COUNT,
    EXPECTED_POLICY_AREA_COUNT,
    PADimCoverage,
    get_padim_coverage_matrix,
    validate_constitutional_invariant,
)
from farfan_pipeline.phases.Phase_1.contracts.phase1_input_contract import (
    PHASE1_INPUT_PRECONDITIONS,
    Phase1InputPrecondition,
    validate_phase1_input_contract,
)
from farfan_pipeline.phases.Phase_1.contracts.phase1_mission_contract import (
    PHASE1_SUBPHASE_WEIGHTS,
    SubphaseWeight,
    WeightTier,
    validate_mission_contract,
)
from farfan_pipeline.phases.Phase_1.contracts.phase1_output_contract import (
    PHASE1_OUTPUT_POSTCONDITIONS,
    Phase1OutputPostcondition,
    validate_phase1_output_contract,
)

__all__ = [
    # Mission Contract
    "PHASE1_SUBPHASE_WEIGHTS",
    "SubphaseWeight",
    "WeightTier",
    "validate_mission_contract",
    # Input Contract
    "PHASE1_INPUT_PRECONDITIONS",
    "Phase1InputPrecondition",
    "validate_phase1_input_contract",
    # Output Contract
    "PHASE1_OUTPUT_POSTCONDITIONS",
    "Phase1OutputPostcondition",
    "validate_phase1_output_contract",
    # Constitutional Contract
    "EXPECTED_CHUNK_COUNT",
    "EXPECTED_DIMENSION_COUNT",
    "EXPECTED_POLICY_AREA_COUNT",
    "PADimCoverage",
    "get_padim_coverage_matrix",
    "validate_constitutional_invariant",
]
