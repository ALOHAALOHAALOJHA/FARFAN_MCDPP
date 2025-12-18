"""
Module: src.canonic_phases.phase_2.constants.phase2_constants
Purpose: Single source of truth for all Phase 2 constants and configuration
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - ConstantImmutability: All constants frozen at module load time
    - TypeSafety: All constants properly typed

Determinism:
    Seed-Strategy: NOT_APPLICABLE
    State-Management: Constants are immutable singletons

Inputs:
    - None: Constants loaded at module import time

Outputs:
    - PHASE2_CONSTANTS: Final[Dict[str, Any]] — Frozen constant dictionary

Failure-Modes:
    - ImportError: Module cannot be imported — critical system failure
"""
from __future__ import annotations

from typing import Final, FrozenSet, Tuple

# ============================================================================
# PHASE 2 PIPELINE CONFIGURATION
# ============================================================================

PHASE_2_VERSION: Final[str] = "1.0.0"
PHASE_2_EFFECTIVE_DATE: Final[str] = "2025-12-18"
PHASE_2_OWNER: Final[str] = "phase2_orchestration"

# ============================================================================
# CONTRACT CARVING CONFIGURATION
# ============================================================================

# Base questions (Q001-Q030)
BASE_QUESTION_COUNT: Final[int] = 30
BASE_QUESTION_MIN: Final[int] = 1
BASE_QUESTION_MAX: Final[int] = 30

# Policy Areas (10 total)
POLICY_AREA_COUNT: Final[int] = 10
POLICY_AREA_IDS: Final[Tuple[str, ...]] = tuple(f"PA{i:02d}" for i in range(1, 11))

# Expanded contracts (Q001-Q300 = 30 base × 10 PAs)
EXPANDED_CONTRACT_COUNT: Final[int] = 300
EXPANDED_CONTRACT_MIN: Final[int] = 1
EXPANDED_CONTRACT_MAX: Final[int] = 300

# Contract carving validation
CARVER_EXPECTED_OUTPUT_COUNT: Final[int] = 300
CARVER_MINIMUM_QUALITY_SCORE: Final[float] = 0.75

# ============================================================================
# CQVR VALIDATION THRESHOLDS
# ============================================================================

CQVR_CALIDAD_MIN: Final[float] = 0.70  # Minimum quality score
CQVR_QUANTUM_MIN: Final[float] = 0.65  # Minimum quantum score
CQVR_VALOR_MIN: Final[float] = 0.70    # Minimum value score
CQVR_RIGOR_MIN: Final[float] = 0.75    # Minimum rigor score

CQVR_AGGREGATE_MIN: Final[float] = 0.70  # Minimum aggregate CQVR score
CQVR_GATE_PASSING_THRESHOLD: Final[float] = 0.70

# ============================================================================
# EXECUTOR CONFIGURATION DEFAULTS
# ============================================================================

DEFAULT_TIMEOUT_S: Final[float] = 300.0  # 5 minutes
DEFAULT_RETRY_COUNT: Final[int] = 3
DEFAULT_TEMPERATURE: Final[float] = 0.0  # Deterministic by default
DEFAULT_MAX_TOKENS: Final[int] = 4096
DEFAULT_MEMORY_LIMIT_MB: Final[int] = 2048
DEFAULT_ENABLE_PROFILING: Final[bool] = True

# ============================================================================
# CONCURRENCY AND PARALLELISM
# ============================================================================

MAX_PARALLEL_EXECUTORS: Final[int] = 10
MAX_PARALLEL_CHUNKS: Final[int] = 5
CHUNK_SIZE_DEFAULT: Final[int] = 60  # 300 contracts / 5 chunks

# Determinism enforcement
REQUIRE_FIXED_SEED: Final[bool] = True
DEFAULT_SEED: Final[int] = 42

# ============================================================================
# ROUTING CONFIGURATION
# ============================================================================

# Method dispatch validation
STRICT_ARGUMENT_VALIDATION: Final[bool] = True
ALLOW_KWARGS_FORWARDING: Final[bool] = True
FAIL_ON_MISSING_REQUIRED: Final[bool] = True
FAIL_ON_UNEXPECTED_ARGS: Final[bool] = True

# Special route count (high-traffic methods with explicit handlers)
SPECIAL_ROUTE_COUNT_MIN: Final[int] = 30

# ============================================================================
# SISAS INTEGRATION
# ============================================================================

SISAS_REGISTRY_PATH: Final[str] = "src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS"
SISAS_SIGNAL_TIMEOUT_S: Final[float] = 10.0
SISAS_REQUIRED_SIGNALS: Final[FrozenSet[str]] = frozenset({
    "signal_consumption",
    "signal_quality_metrics",
    "signal_contract_validator",
})

# ============================================================================
# SCHEMA PATHS
# ============================================================================

SCHEMA_DIR: Final[str] = "src/canonic_phases/phase_2/schemas"
EXECUTOR_CONFIG_SCHEMA: Final[str] = f"{SCHEMA_DIR}/executor_config.schema.json"
EXECUTOR_OUTPUT_SCHEMA: Final[str] = f"{SCHEMA_DIR}/executor_output.schema.json"
CALIBRATION_POLICY_SCHEMA: Final[str] = f"{SCHEMA_DIR}/calibration_policy.schema.json"
SYNCHRONIZATION_MANIFEST_SCHEMA: Final[str] = f"{SCHEMA_DIR}/synchronization_manifest.schema.json"

# ============================================================================
# CONTRACT VALIDATION
# ============================================================================

# Contract hash algorithm
CONTRACT_HASH_ALGORITHM: Final[str] = "sha256"

# Context immutability
ENFORCE_CONTEXT_FREEZE: Final[bool] = True
CONTEXT_MODIFICATION_IS_ERROR: Final[bool] = True

# Permutation invariance
ENFORCE_PERMUTATION_INVARIANCE: Final[bool] = True
SET_BASED_OPERATIONS_ONLY: Final[bool] = True

# Runtime contracts
ENFORCE_PRECONDITIONS: Final[bool] = True
ENFORCE_POSTCONDITIONS: Final[bool] = True
ENFORCE_INVARIANTS: Final[bool] = True

# ============================================================================
# RESOURCE MANAGEMENT
# ============================================================================

RESOURCE_TRACKING_ENABLED: Final[bool] = True
MEMORY_TRACKING_INTERVAL_S: Final[float] = 1.0
CPU_TRACKING_INTERVAL_S: Final[float] = 1.0

# Resource limits
MAX_MEMORY_MB_PER_EXECUTOR: Final[int] = 4096
MAX_CPU_PERCENT_PER_EXECUTOR: Final[float] = 100.0
MAX_TOTAL_MEMORY_MB: Final[int] = 16384

# ============================================================================
# PRECISION TRACKING
# ============================================================================

PRECISION_METRICS_ENABLED: Final[bool] = True
PRECISION_DRIFT_THRESHOLD: Final[float] = 1e-10
PRECISION_VALIDATION_POINTS: Final[int] = 100

# ============================================================================
# LOGGING AND OBSERVABILITY
# ============================================================================

ENABLE_STRUCTURED_LOGGING: Final[bool] = True
LOG_LEVEL_DEFAULT: Final[str] = "INFO"
LOG_LEVEL_CONTRACTS: Final[str] = "DEBUG"
LOG_LEVEL_EXECUTION: Final[str] = "INFO"

ENABLE_TRACING: Final[bool] = True
ENABLE_METRICS: Final[bool] = True
ENABLE_PROFILING: Final[bool] = True

# ============================================================================
# FILE NAMING PATTERNS (for validation)
# ============================================================================

# Phase-root file pattern: phase2_[a-z]_[a-z0-9_]+.py
PHASE_ROOT_FILE_PATTERN: Final[str] = r"^phase2_[a-z]_[a-z0-9_]+\.py$"

# Package-internal file pattern: [a-z][a-z0-9_]*.py
PACKAGE_INTERNAL_PATTERN: Final[str] = r"^[a-z][a-z0-9_]*\.py$"

# Schema file pattern: [a-z][a-z0-9_]*.schema.json
SCHEMA_FILE_PATTERN: Final[str] = r"^[a-z][a-z0-9_]*\.schema\.json$"

# Certificate file pattern: CERTIFICATE_[0-9]{2}_[A-Z][A-Z0-9_]*.md
CERTIFICATE_FILE_PATTERN: Final[str] = r"^CERTIFICATE_[0-9]{2}_[A-Z][A-Z0-9_]*\.md$"

# Test file pattern: test_phase2_[a-z0-9_]+.py
TEST_FILE_PATTERN: Final[str] = r"^test_phase2_[a-z0-9_]+\.py$"

# ============================================================================
# FORBIDDEN LEGACY ARTIFACTS
# ============================================================================

FORBIDDEN_FILE_NAMES: Final[FrozenSet[str]] = frozenset({
    "executors.py",
    "batch_executor.py",
    "batch_generate_all_configs.py",
    "EXECUTOR_CALIBRATION_INTEGRATION_README.md",
    "INTEGRATION_IMPLEMENTATION_SUMMARY.md",
    "create_all_executor_configs.sh",
})

FORBIDDEN_FILE_PATTERNS: Final[Tuple[str, ...]] = (
    r".*_v\d+\.py$",       # version suffixes
    r".*_final.*\.py$",    # "final" in name
    r".*_old.*\.py$",      # "old" in name
    r".*_backup.*\.py$",   # backup files
)

# ============================================================================
# CANONICAL PATHS
# ============================================================================

CANONICAL_ROOT: Final[str] = "src/canonic_phases/phase_2"
LEGACY_PHASE_TWO_DIR: Final[str] = "src/farfan_pipeline/phases/Phase_two"

# ============================================================================
# CERTIFICATE CONFIGURATION
# ============================================================================

REQUIRED_CERTIFICATES: Final[Tuple[str, ...]] = (
    "CERTIFICATE_01_ROUTING_CONTRACT",
    "CERTIFICATE_02_CONCURRENCY_DETERMINISM",
    "CERTIFICATE_03_CONTEXT_IMMUTABILITY",
    "CERTIFICATE_04_PERMUTATION_INVARIANCE",
    "CERTIFICATE_05_RUNTIME_CONTRACTS",
    "CERTIFICATE_06_CONFIG_SCHEMA_VALIDITY",
    "CERTIFICATE_07_OUTPUT_SCHEMA_VALIDITY",
    "CERTIFICATE_08_CARVER_300_DELIVERY",
    "CERTIFICATE_09_CPP_TO_EXECUTOR_ALIGNMENT",
    "CERTIFICATE_10_SISAS_SYNCHRONIZATION",
    "CERTIFICATE_11_RESOURCE_PLANNING_DETERMINISM",
    "CERTIFICATE_12_PRECISION_TRACKING_INTEGRITY",
    "CERTIFICATE_13_METHOD_REGISTRY_COMPLETENESS",
    "CERTIFICATE_14_SIGNATURE_VALIDATION_STRICTNESS",
    "CERTIFICATE_15_SOURCE_VALIDATION_STRICTNESS",
)

CERTIFICATE_COUNT: Final[int] = 15

# ============================================================================
# VALIDATION GATES
# ============================================================================

# Gates that must pass before proceeding
GATE_ROUTING_VALIDATION: Final[str] = "ROUTING_VALIDATION"
GATE_CARVER_300_DELIVERY: Final[str] = "CARVER_300_DELIVERY"
GATE_CQVR_THRESHOLD: Final[str] = "CQVR_THRESHOLD"
GATE_CONFIG_SCHEMA: Final[str] = "CONFIG_SCHEMA"
GATE_OUTPUT_SCHEMA: Final[str] = "OUTPUT_SCHEMA"
GATE_SISAS_SYNC: Final[str] = "SISAS_SYNC"
GATE_RESOURCE_ALLOCATION: Final[str] = "RESOURCE_ALLOCATION"
GATE_CONTRACT_VALIDATION: Final[str] = "CONTRACT_VALIDATION"

ALL_GATES: Final[Tuple[str, ...]] = (
    GATE_ROUTING_VALIDATION,
    GATE_CARVER_300_DELIVERY,
    GATE_CQVR_THRESHOLD,
    GATE_CONFIG_SCHEMA,
    GATE_OUTPUT_SCHEMA,
    GATE_SISAS_SYNC,
    GATE_RESOURCE_ALLOCATION,
    GATE_CONTRACT_VALIDATION,
)

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_LEGACY_ARTIFACT_FOUND: Final[str] = "LEGACY_ARTIFACT_FOUND: Forbidden legacy file exists"
ERROR_NAMING_VIOLATION: Final[str] = "NAMING_VIOLATION: File name does not match canonical pattern"
ERROR_PATH_VIOLATION: Final[str] = "PATH_VIOLATION: Phase 2 file outside canonical root"
ERROR_CONTRACT_VIOLATION: Final[str] = "CONTRACT_VIOLATION: Contract enforcement failed"
ERROR_IMPORT_BROKEN: Final[str] = "IMPORT_BROKEN: Import statement cannot resolve"

# ============================================================================
# FROZEN CONSTANT DICTIONARY (for external access)
# ============================================================================

PHASE2_CONSTANTS: Final[dict[str, object]] = {
    "PHASE_2_VERSION": PHASE_2_VERSION,
    "BASE_QUESTION_COUNT": BASE_QUESTION_COUNT,
    "POLICY_AREA_COUNT": POLICY_AREA_COUNT,
    "EXPANDED_CONTRACT_COUNT": EXPANDED_CONTRACT_COUNT,
    "CQVR_AGGREGATE_MIN": CQVR_AGGREGATE_MIN,
    "DEFAULT_TIMEOUT_S": DEFAULT_TIMEOUT_S,
    "DEFAULT_SEED": DEFAULT_SEED,
    "MAX_PARALLEL_EXECUTORS": MAX_PARALLEL_EXECUTORS,
    "CANONICAL_ROOT": CANONICAL_ROOT,
    "CERTIFICATE_COUNT": CERTIFICATE_COUNT,
}
