"""
Module: src.farfan_pipeline.phases.Phase_two.PHASE_2_CONSTANTS
Purpose: Global constants for Phase 2 - Executor Contract Factory
Owner: phase2_core
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-30
"""
from __future__ import annotations

from typing import Final

__version__ = "1.0.0"
__phase__ = 2

# ============================================================================
# PHASE IDENTIFICATION
# ============================================================================

PHASE_NUMBER: Final[int] = 2
PHASE_NAME: Final[str] = "Phase 2: Executor Contract Factory"
PHASE_LABEL: Final[str] = f"Phase {PHASE_NUMBER}"
PHASE_CODENAME: Final[str] = "FACTORY"

# ============================================================================
# STAGE DEFINITIONS
# ============================================================================

STAGE_INFRASTRUCTURE: Final[int] = 0
STAGE_FACTORY: Final[int] = 10
STAGE_REGISTRY: Final[int] = 20
STAGE_DISPENSARY: Final[int] = 30
STAGE_EXECUTOR: Final[int] = 40
STAGE_ORCHESTRATION: Final[int] = 50

VALID_STAGES: Final[frozenset[int]] = frozenset({
    STAGE_INFRASTRUCTURE,
    STAGE_FACTORY,
    STAGE_REGISTRY,
    STAGE_DISPENSARY,
    STAGE_EXECUTOR,
    STAGE_ORCHESTRATION,
})

STAGE_METADATA: Final[dict[int, dict[str, str]]] = {
    0: {"name": "Infrastructure", "description": "Package init, types, errors"},
    10: {"name": "Factory", "description": "Contract factory and builders"},
    20: {"name": "Registry", "description": "Class and method registries"},
    30: {"name": "Dispensary", "description": "Method implementations"},
    40: {"name": "Executor", "description": "Contract executors"},
    50: {"name": "Orchestration", "description": "Pipeline orchestration"},
}

# ============================================================================
# MODULE TYPES
# ============================================================================

TYPE_FACTORY: Final[str] = "FAC"
TYPE_REGISTRY: Final[str] = "REG"
TYPE_EXECUTOR: Final[str] = "EXE"
TYPE_DISPATCHER: Final[str] = "DIS"
TYPE_UTILITY: Final[str] = "UTIL"

VALID_MODULE_TYPES: Final[frozenset[str]] = frozenset({
    TYPE_FACTORY,
    TYPE_REGISTRY,
    TYPE_EXECUTOR,
    TYPE_DISPATCHER,
    TYPE_UTILITY,
})

# ============================================================================
# CRITICALITY LEVELS
# ============================================================================

CRITICALITY_CRITICAL: Final[str] = "CRITICAL"
CRITICALITY_HIGH: Final[str] = "HIGH"
CRITICALITY_MEDIUM: Final[str] = "MEDIUM"
CRITICALITY_LOW: Final[str] = "LOW"

VALID_CRITICALITY_LEVELS: Final[frozenset[str]] = frozenset({
    CRITICALITY_CRITICAL,
    CRITICALITY_HIGH,
    CRITICALITY_MEDIUM,
    CRITICALITY_LOW,
})

# ============================================================================
# EXECUTION PATTERNS
# ============================================================================

PATTERN_SINGLETON: Final[str] = "Singleton"
PATTERN_ON_DEMAND: Final[str] = "On-Demand"
PATTERN_FACTORY: Final[str] = "Factory"

VALID_EXECUTION_PATTERNS: Final[frozenset[str]] = frozenset({
    PATTERN_SINGLETON,
    PATTERN_ON_DEMAND,
    PATTERN_FACTORY,
})

# ============================================================================
# CONTRACT CONSTANTS
# ============================================================================

TOTAL_CONTRACTS: Final[int] = 300
BASE_QUESTIONS: Final[int] = 30
POLICY_AREAS: Final[int] = 10
METHODS_PER_CONTRACT: Final[int] = 8

# ============================================================================
# DETERMINISM
# ============================================================================

DEFAULT_SEED: Final[int] = 42
SEED_STRATEGY: Final[str] = "FIXED"
HASH_ALGORITHM: Final[str] = "blake3"

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "PHASE_NUMBER",
    "PHASE_NAME",
    "PHASE_LABEL",
    "PHASE_CODENAME",
    "VALID_STAGES",
    "STAGE_METADATA",
    "VALID_MODULE_TYPES",
    "VALID_CRITICALITY_LEVELS",
    "VALID_EXECUTION_PATTERNS",
    "TOTAL_CONTRACTS",
    "BASE_QUESTIONS",
    "POLICY_AREAS",
    "METHODS_PER_CONTRACT",
    "DEFAULT_SEED",
    "SEED_STRATEGY",
    "HASH_ALGORITHM",
]
