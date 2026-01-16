"""
Phase 2 Interphase Package
==========================

PHASE_LABEL: Phase 2
Module: interphase/__init__.py
Purpose: Interface definitions and protocols for inter-phase communication

This package contains:
1. Entry contract: What Phase 2 expects from Phase 1
2. Exit contract: What Phase 2 delivers to Phase 3
3. Protocol definitions for phase boundaries
4. Phase1 → Phase2 Adapter for structural compatibility
5. Phase2 → Phase3 Adapter for structural compatibility

Version: 1.1.0
Date: 2026-01-13
Author: F.A.R.F.A.N Core Architecture Team
"""
from __future__ import annotations

from typing import Final, Protocol, runtime_checkable

# Import Phase 1 → Phase 2 adapter components
from farfan_pipeline.phases.Phase_02.interphase.phase1_phase2_adapter import (
    Phase1OutputProtocol,
    Phase2InputBundle,
    adapt_phase1_to_phase2,
    validate_adaptation as validate_p1_to_p2_adaptation,
    extract_chunks,
    extract_schema_version,
    DEFAULT_SCHEMA_VERSION,
    ADAPTER_VERSION as P1_P2_ADAPTER_VERSION,
)

# Import Phase 2 → Phase 3 adapter components
from farfan_pipeline.phases.Phase_02.interphase.phase2_phase3_adapter import (
    Phase2ResultProtocol,
    MicroQuestionRun,
    AdaptationResult,
    adapt_phase2_to_phase3,
    adapt_single_result,
    validate_adaptation as validate_p2_to_p3_adaptation,
    transform_question_id,
    reverse_transform_question_id,
    derive_dimension,
    derive_base_slot,
    derive_question_global,
    ADAPTER_VERSION as P2_P3_ADAPTER_VERSION,
)

__all__ = [
    # Protocols
    "Phase2EntryProtocol",
    "Phase2ExitProtocol",
    "Phase1OutputProtocol",
    "Phase2ResultProtocol",
    # Constants
    "PHASE2_RECEIVES_FROM",
    "PHASE2_DELIVERS_TO",
    "DEFAULT_SCHEMA_VERSION",
    "P1_P2_ADAPTER_VERSION",
    "P2_P3_ADAPTER_VERSION",
    # Phase 1 → Phase 2 Adapter
    "Phase2InputBundle",
    "adapt_phase1_to_phase2",
    "validate_p1_to_p2_adaptation",
    "extract_chunks",
    "extract_schema_version",
    # Phase 2 → Phase 3 Adapter
    "MicroQuestionRun",
    "AdaptationResult",
    "adapt_phase2_to_phase3",
    "adapt_single_result",
    "validate_p2_to_p3_adaptation",
    "transform_question_id",
    "reverse_transform_question_id",
    "derive_dimension",
    "derive_base_slot",
    "derive_question_global",
]


# Phase boundaries
PHASE2_RECEIVES_FROM: Final[str] = "Phase_1"
PHASE2_DELIVERS_TO: Final[str] = "Phase_3"


@runtime_checkable
class Phase2EntryProtocol(Protocol):
    """Protocol defining what Phase 2 expects from Phase 1 output."""
    
    @property
    def canon_policy_package(self) -> dict:
        """The CanonPolicyPackage from Phase 1 ingestion."""
        ...
    
    @property
    def chunks(self) -> list[dict]:
        """Preprocessed document chunks."""
        ...
    
    @property
    def metadata(self) -> dict:
        """Document metadata including structure analysis."""
        ...


@runtime_checkable
class Phase2ExitProtocol(Protocol):
    """Protocol defining what Phase 2 delivers to Phase 3."""
    
    @property
    def execution_results(self) -> dict:
        """Results from 300 contract executions."""
        ...
    
    @property
    def evidence_graph(self) -> dict:
        """Evidence nexus graph for scoring."""
        ...
    
    @property
    def narrative_synthesis(self) -> dict:
        """Carver-synthesized narrative responses."""
        ...
    
    @property
    def provenance(self) -> dict:
        """Complete provenance chain."""
        ...
