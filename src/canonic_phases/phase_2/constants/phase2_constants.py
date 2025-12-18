"""
Module: src.canonic_phases.phase_2.constants.phase2_constants
Purpose: Phase 2 constants and configuration values
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18
"""
from __future__ import annotations

from typing import Final

# === CARDINALITY CONSTANTS ===
CPP_CHUNK_COUNT: Final[int] = 60
MICRO_ANSWER_COUNT: Final[int] = 300
SHARDS_PER_CHUNK: Final[int] = 5

# === SISAS CONSTANTS ===
SISAS_SIGNAL_COVERAGE_THRESHOLD: Final[float] = 0.7
SISAS_PRIORITY_WEIGHT_SIGNAL: Final[float] = 0.8
SISAS_PRIORITY_WEIGHT_STATIC: Final[float] = 0.2

# === HASH ALGORITHM ===
HASH_ALGORITHM: Final[str] = "sha256"

# === ERROR CODES ===
ERROR_CODES: Final[dict[str, str]] = {
    "E2001": "ROUTING_ERROR",
    "E2002": "CARVER_ERROR",
    "E2003": "VALIDATION_ERROR",
    "E2004": "SYNCHRONIZATION_ERROR",
    "E2005": "REGISTRY_ERROR",
}
