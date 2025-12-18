"""
Phase 2 Constants Module

Single source of truth for all Phase 2 configuration constants.
No runtime IO - all values are frozen at import time.

Usage:
    from canonic_phases.phase_2.constants.phase2_constants import (
        CPP_CHUNK_COUNT,
        MICRO_ANSWER_COUNT,
        EXECUTOR_REGISTRY,
        ERROR_CODES,
    )
"""
from __future__ import annotations

from .phase2_constants import (
    CPP_CHUNK_COUNT,
    MICRO_ANSWER_COUNT,
    SHARDS_PER_CHUNK,
    EXECUTOR_REGISTRY,
    ExecutorRegistryEntry,
    SCHEMA_VERSIONS,
    SchemaVersion,
    SISAS_SIGNAL_COVERAGE_THRESHOLD,
    SISAS_IRRIGATION_LINK_MINIMUM,
    SISAS_PRIORITY_WEIGHT_SIGNAL,
    SISAS_PRIORITY_WEIGHT_STATIC,
    DEFAULT_RANDOM_SEED,
    HASH_ALGORITHM,
    ERROR_CODES,
    ErrorCode,
    FORBIDDEN_IMPORTS,
    FORBIDDEN_RUNTIME_IO_PATTERNS,
)

__all__ = [
    "CPP_CHUNK_COUNT",
    "MICRO_ANSWER_COUNT",
    "SHARDS_PER_CHUNK",
    "EXECUTOR_REGISTRY",
    "ExecutorRegistryEntry",
    "SCHEMA_VERSIONS",
    "SchemaVersion",
    "SISAS_SIGNAL_COVERAGE_THRESHOLD",
    "SISAS_IRRIGATION_LINK_MINIMUM",
    "SISAS_PRIORITY_WEIGHT_SIGNAL",
    "SISAS_PRIORITY_WEIGHT_STATIC",
    "DEFAULT_RANDOM_SEED",
    "HASH_ALGORITHM",
    "ERROR_CODES",
    "ErrorCode",
    "FORBIDDEN_IMPORTS",
    "FORBIDDEN_RUNTIME_IO_PATTERNS",
]
