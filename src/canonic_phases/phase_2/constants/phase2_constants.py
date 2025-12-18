"""
Module:  src.canonic_phases.phase_2.constants.phase2_constants
Purpose: Single source of truth for all Phase 2 constants (no runtime monolith reads)
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date:  2025-12-18

Contracts-Enforced:
    - ConstantsFreezeContract: No runtime IO for behavior determination
    - SingleSourceContract: All constants defined here, nowhere else

Determinism:
    Seed-Strategy: NOT_APPLICABLE (constants are static)
    State-Management:  Immutable module-level constants

Inputs:
    - None (compile-time only)

Outputs:
    - Constant values accessible via import

Failure-Modes:
    - ConstantRedefinition: ImportError — Constant defined elsewhere
    - RuntimeMonolithRead: ContractViolation — IO detected at runtime
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, FrozenSet, Dict, Tuple
import hashlib

# =============================================================================
# SECTION:  CARDINALITY INVARIANTS
# =============================================================================

CPP_CHUNK_COUNT: Final[int] = 60
"""
[INVARIANT] Phase 1 delivers exactly 60 CPP chunks.
Violation of this invariant indicates Phase 1 failure.
"""

MICRO_ANSWER_COUNT: Final[int] = 300
"""
[INVARIANT] Phase 2 produces exactly 300 micro-answers.
Derived from:  CPP_CHUNK_COUNT * SHARDS_PER_CHUNK
"""

SHARDS_PER_CHUNK:  Final[int] = 5
"""
[DERIVATION] 300 / 60 = 5 shards per chunk.
Each CPP chunk produces exactly 5 micro-answers.
"""

# Compile-time verification
assert CPP_CHUNK_COUNT * SHARDS_PER_CHUNK == MICRO_ANSWER_COUNT, (
    f"Cardinality invariant violated: {CPP_CHUNK_COUNT} * {SHARDS_PER_CHUNK} != {MICRO_ANSWER_COUNT}"
)

# =============================================================================
# SECTION: EXECUTOR REGISTRY
# =============================================================================

@dataclass(frozen=True, slots=True)
class ExecutorRegistryEntry:
    """Immutable executor registry entry."""
    canonical_name: str
    contract_types: FrozenSet[str]
    priority: int
    deterministic:  bool


EXECUTOR_REGISTRY:  Final[Dict[str, ExecutorRegistryEntry]] = {
    "contract_executor":  ExecutorRegistryEntry(
        canonical_name="ContractExecutor",
        contract_types=frozenset({"ContractPayload", "ValidationPayload"}),
        priority=1,
        deterministic=True,
    ),
    "analysis_executor": ExecutorRegistryEntry(
        canonical_name="AnalysisExecutor",
        contract_types=frozenset({"AnalysisPayload"}),
        priority=2,
        deterministic=True,
    ),
    "synthesis_executor": ExecutorRegistryEntry(
        canonical_name="SynthesisExecutor",
        contract_types=frozenset({"SynthesisPayload"}),
        priority=3,
        deterministic=True,
    ),
}

# =============================================================================
# SECTION:  SCHEMA VERSION CONTROL
# =============================================================================

@dataclass(frozen=True, slots=True)
class SchemaVersion:
    """Immutable schema version with content hash."""
    name: str
    version: str
    content_hash: str  # SHA-256 of schema content


SCHEMA_VERSIONS: Final[Dict[str, SchemaVersion]] = {
    "executor_config":  SchemaVersion(
        name="executor_config.schema.json",
        version="1.0.0",
        content_hash="",  # Populated by CI after schema freeze
    ),
    "executor_output": SchemaVersion(
        name="executor_output.schema.json",
        version="1.0.0",
        content_hash="",
    ),
    "calibration_policy": SchemaVersion(
        name="calibration_policy.schema.json",
        version="1.0.0",
        content_hash="",
    ),
    "synchronization_manifest": SchemaVersion(
        name="synchronization_manifest.schema.json",
        version="1.0.0",
        content_hash="",
    ),
}

# =============================================================================
# SECTION:  SISAS SYNCHRONIZATION POLICY
# =============================================================================

SISAS_SIGNAL_COVERAGE_THRESHOLD: Final[float] = 0.85
"""
[THRESHOLD] Minimum signal coverage ratio for SISAS synchronization.
Below this threshold, tasks are flagged for manual review.
"""

SISAS_IRRIGATION_LINK_MINIMUM:  Final[int] = 1
"""
[CONSTRAINT] Every CPP chunk must have at least this many irrigation links.
"""

SISAS_PRIORITY_WEIGHT_SIGNAL:  Final[float] = 0.6
"""
[WEIGHT] Signal-derived priority contribution to task weighting.
"""

SISAS_PRIORITY_WEIGHT_STATIC: Final[float] = 0.4
"""
[WEIGHT] Static priority contribution to task weighting.
"""

assert abs(SISAS_PRIORITY_WEIGHT_SIGNAL + SISAS_PRIORITY_WEIGHT_STATIC - 1.0) < 1e-9, (
    "Priority weights must sum to 1.0"
)

# =============================================================================
# SECTION:  DETERMINISM CONTROL
# =============================================================================

DEFAULT_RANDOM_SEED: Final[int] = 42
"""
[SEED] Default seed for all stochastic operations.
Override via environment variable PHASE2_RANDOM_SEED for testing.
"""

HASH_ALGORITHM: Final[str] = "sha256"
"""
[ALGORITHM] Hash algorithm for content hashing and contract verification.
"""

# =============================================================================
# SECTION: ERROR CODES
# =============================================================================

@dataclass(frozen=True, slots=True)
class ErrorCode:
    """Structured error code with taxonomy."""
    code: str
    category: str
    severity: str
    message_template: str


ERROR_CODES:  Final[Dict[str, ErrorCode]] = {
    "E2001": ErrorCode(
        code="E2001",
        category="ROUTING",
        severity="FATAL",
        message_template="No executor found for contract type: {contract_type}",
    ),
    "E2002": ErrorCode(
        code="E2002",
        category="CARVING",
        severity="FATAL",
        message_template="Carver output count mismatch: expected {expected}, got {actual}",
    ),
    "E2003": ErrorCode(
        code="E2003",
        category="VALIDATION",
        severity="FATAL",
        message_template="Contract validation failed: {contract_name} — {details}",
    ),
    "E2004": ErrorCode(
        code="E2004",
        category="SYNCHRONIZATION",
        severity="FATAL",
        message_template="SISAS synchronization failed: {reason}",
    ),
    "E2005": ErrorCode(
        code="E2005",
        category="SCHEMA",
        severity="FATAL",
        message_template="Schema validation failed for {schema_name}: {details}",
    ),
    "E2006": ErrorCode(
        code="E2006",
        category="DETERMINISM",
        severity="FATAL",
        message_template="Non-deterministic output detected: {details}",
    ),
    "E2007": ErrorCode(
        code="E2007",
        category="CONTRACT",
        severity="FATAL",
        message_template="Runtime contract violation: {contract} — {details}",
    ),
}

# =============================================================================
# SECTION:  FORBIDDEN PATTERNS (CI ENFORCEMENT)
# =============================================================================

FORBIDDEN_IMPORTS: Final[FrozenSet[str]] = frozenset({
    "questionnaire_monolith",
    "executors",  # Legacy module
    "batch_executor",
})

FORBIDDEN_RUNTIME_IO_PATTERNS: Final[FrozenSet[str]] = frozenset({
    "questionnaire_monolith.json",
    "monolith.json",
})
