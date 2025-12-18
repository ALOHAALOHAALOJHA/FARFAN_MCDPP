"""
Module: src.canonic_phases.phase_2.constants.phase2_constants
Purpose: Constants for Phase 2 contract enforcement
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Constants used across Phase 2 contract modules for determinism,
error codes, and cryptographic operations.
"""
from __future__ import annotations

from typing import Final

# === ERROR CODES ===
ERROR_CODES: Final[dict[str, str]] = {
    "E2001": "ROUTING_CONTRACT_VIOLATION - Executor routing failed",
    "E2002": "PAYLOAD_VALIDATION_FAILURE - Invalid payload structure",
    "E2003": "EXECUTOR_NOT_FOUND - No executor for contract type",
    "E2004": "AMBIGUOUS_MAPPING - Multiple executors match",
    "E2005": "SIGNATURE_MISMATCH - Payload signature invalid",
    "E2006": "CONCURRENCY_DETERMINISM_VIOLATION - Parallel != Serial",
    "E2007": "RUNTIME_CONTRACT_VIOLATION - Pre/Post/Invariant failed",
    "E2008": "REGISTRY_INCOMPLETE - Missing contract type mappings",
    "E2009": "INVARIANT_CORRUPTION - State consistency violated",
}

# === DETERMINISM CONFIGURATION ===
DEFAULT_RANDOM_SEED: Final[int] = 42

# === CRYPTOGRAPHIC CONFIGURATION ===
HASH_ALGORITHM: Final[str] = "sha256"

# === CONCURRENCY CONFIGURATION ===
DEFAULT_MAX_WORKERS: Final[int] = 4
CONCURRENCY_TIMEOUT_SECONDS: Final[int] = 300

# === VALIDATION THRESHOLDS ===
MAX_PAYLOAD_SIZE_BYTES: Final[int] = 10 * 1024 * 1024  # 10MB
MAX_EXECUTOR_REGISTRY_SIZE: Final[int] = 1000
