"""
Module: src.canonic_phases.phase_2
Purpose: Phase 2 canonical implementation - Argument routing and carving
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

This package provides the canonical Phase 2 implementation with:
- Exhaustive argument routing with contract enforcement
- Deterministic carving of 60 CPP chunks into 300 micro-answers
- Full provenance tracking and validation
- Strict cardinality contracts
"""
from __future__ import annotations

from .phase2_a_arg_router import (
    ArgRouter,
    ContractPayload,
    Executor,
    ExecutorResult,
    RegistryError,
    RoutingError,
    ValidationError,
)
from .phase2_b_carver import (
    Carver,
    CarverError,
    CPPChunk,
    MicroAnswer,
    ProvenanceError,
    carve_chunks,
)

__all__ = [
    # Router
    "ArgRouter",
    "CPPChunk",
    # Carver
    "Carver",
    "CarverError",
    "ContractPayload",
    "Executor",
    "ExecutorResult",
    "MicroAnswer",
    "ProvenanceError",
    "RegistryError",
    "RoutingError",
    "ValidationError",
    "carve_chunks",
]
