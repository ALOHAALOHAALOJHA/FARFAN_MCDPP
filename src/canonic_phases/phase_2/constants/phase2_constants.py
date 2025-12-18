"""
Module: src.canonic_phases.phase_2.constants.phase2_constants
Purpose: Constants and configuration for Phase 2 processing
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# === CARDINALITY CONSTANTS ===

CPP_CHUNK_COUNT: Final[int] = 60
"""Expected number of CPP chunks from Phase 1."""

MICRO_ANSWER_COUNT: Final[int] = 300
"""Expected number of micro-answers produced by carving."""

SHARDS_PER_CHUNK: Final[int] = 5
"""Number of micro-answer shards per CPP chunk."""

# === DETERMINISM CONFIGURATION ===

DEFAULT_RANDOM_SEED: Final[int] = 42
"""Default seed for deterministic operations."""

HASH_ALGORITHM: Final[str] = "sha256"
"""Hash algorithm for content integrity verification."""

# === ERROR CODES ===

@dataclass(frozen=True)
class ErrorCode:
    """Error code definition."""
    code: str
    message_template: str


ERROR_CODES: Final[dict[str, ErrorCode]] = {
    "E2001": ErrorCode(
        code="E2001",
        message_template="No executor mapping found for contract_type: {contract_type}",
    ),
    "E2002": ErrorCode(
        code="E2002",
        message_template="Cardinality violation: expected {expected}, got {actual}",
    ),
    "E2003": ErrorCode(
        code="E2003",
        message_template="Validation failed: {details}",
    ),
    "E2004": ErrorCode(
        code="E2004",
        message_template="Provenance tracking failed: {details}",
    ),
}

# === EXECUTOR REGISTRY DEFINITION ===

@dataclass(frozen=True)
class ExecutorRegistryEntry:
    """Definition of an executor and its contract types."""
    executor_id: str
    contract_types: list[str]
    description: str


EXECUTOR_REGISTRY: Final[dict[str, ExecutorRegistryEntry]] = {
    "specialized_executor": ExecutorRegistryEntry(
        executor_id="specialized_executor",
        contract_types=["specialized_contract"],
        description="Handles specialized contract payloads",
    ),
    "general_executor": ExecutorRegistryEntry(
        executor_id="general_executor",
        contract_types=["general_contract"],
        description="Handles general contract payloads",
    ),
}
