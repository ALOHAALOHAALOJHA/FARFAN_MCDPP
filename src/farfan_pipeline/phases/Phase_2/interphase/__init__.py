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

Version: 1.0.0
Date: 2026-01-13
Author: F.A.R.F.A.N Core Architecture Team
"""
from __future__ import annotations

from typing import Final, Protocol, runtime_checkable

__all__ = [
    "Phase2EntryProtocol",
    "Phase2ExitProtocol",
    "PHASE2_RECEIVES_FROM",
    "PHASE2_DELIVERS_TO",
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
