"""
Phase 2 Contracts Package
==========================

PHASE_LABEL: Phase 2
Module: contracts/__init__.py
Purpose: Contract definitions for Phase 2 input, execution, and output

This package provides the formal contracts that define Phase 2 behavior:
- Input contract: Preconditions from Phase 1
- Mission contract: Execution flow and dependencies
- Output contract: Postconditions for Phase 3

Version: 1.0.0
"""
from __future__ import annotations

__version__ = "1.0.0"
__phase__ = 2

from farfan_pipeline.phases.Phase_02.contracts.phase2_input_contract import (
    Phase2InputContractError,
    Phase2InputPreconditions,
    Phase2InputValidator,
    verify_phase2_input_contract,
)
from farfan_pipeline.phases.Phase_02.contracts.phase2_mission_contract import (
    ExecutionStage,
    ModuleNode,
    PHASE2_TOPOLOGICAL_ORDER,
    Phase2ExecutionFlow,
    get_topological_sort,
    verify_dag_acyclicity,
    verify_phase2_mission_contract,
)
from farfan_pipeline.phases.Phase_02.contracts.phase2_output_contract import (
    Phase2Output,
    Phase2OutputContractError,
    Phase2OutputPostconditions,
    Phase2OutputValidator,
    Phase2Result,
    Phase3CompatibilityCertificate,
    generate_phase3_compatibility_certificate,
    verify_phase2_output_contract,
)

__all__ = [
    # Input contract
    "Phase2InputPreconditions",
    "Phase2InputValidator",
    "Phase2InputContractError",
    "verify_phase2_input_contract",
    # Mission contract
    "ExecutionStage",
    "ModuleNode",
    "PHASE2_TOPOLOGICAL_ORDER",
    "Phase2ExecutionFlow",
    "verify_dag_acyclicity",
    "get_topological_sort",
    "verify_phase2_mission_contract",
    # Output contract
    "Phase2OutputPostconditions",
    "Phase2OutputValidator",
    "Phase2OutputContractError",
    "Phase2Result",
    "Phase2Output",
    "Phase3CompatibilityCertificate",
    "generate_phase3_compatibility_certificate",
    "verify_phase2_output_contract",
]
