"""Phase 2 Constants - Single Source of Truth.

This module contains all canonical constants for Phase 2 execution.
All values are immutable and represent architectural invariants.

CRITICAL: These constants define the Phase 2 execution contract.
Changes to these values require full regression testing.
"""

from __future__ import annotations

# Executor Contract Constants
EXPECTED_CONTRACT_COUNT: int = 300  # Q001-Q300
CONTRACT_VERSION: str = "v3"
CONTRACT_FILE_PATTERN: str = "Q{:03d}.v3.json"

# Chunk Constants
EXPECTED_CHUNK_COUNT: int = 60  # 10 PA × 6 DIM
POLICY_AREA_COUNT: int = 10     # PA01-PA10
DIMENSION_COUNT: int = 6        # DIM01-DIM06

# Task Constants
EXPECTED_TASK_COUNT: int = 300  # 1 task per executor contract

# Timeout Constants (seconds)
DEFAULT_EXECUTOR_TIMEOUT_S: int = 120
DEFAULT_PHASE_TIMEOUT_S: int = 3600
DEFAULT_TASK_TIMEOUT_S: int = 60

# Retry Constants
DEFAULT_RETRY_COUNT: int = 3
DEFAULT_RETRY_BACKOFF_S: int = 2

# Memory Limits (MB)
DEFAULT_MEMORY_LIMIT_MB: int = 2048
MAX_MEMORY_LIMIT_MB: int = 8192

# Quality Thresholds (CQVR Scores)
CQVR_TIER1_MAX: float = 55.0
CQVR_TIER2_MAX: float = 30.0
CQVR_TIER3_MAX: float = 15.0
CQVR_TOTAL_MAX: float = 100.0

# Production thresholds
CQVR_PRODUCCION_THRESHOLD: float = 80.0
CQVR_REFORMULAR_THRESHOLD: float = 60.0

# Directory Paths (relative to repository root)
CANONICAL_PHASE_2_DIR: str = "src/canonic_phases/phase_2"
LEGACY_PHASE_2_DIR: str = "src/farfan_pipeline/phases/Phase_two"
CONTRACT_DIR: str = "config/executor_contracts/specialized"
CONFIG_DIR: str = "config/executor_configs"

# Schema Versions
EXECUTOR_CONFIG_SCHEMA_VERSION: str = "1.0.0"
EXECUTOR_OUTPUT_SCHEMA_VERSION: str = "1.0.0"
CALIBRATION_POLICY_SCHEMA_VERSION: str = "1.0.0"
SYNCHRONIZATION_MANIFEST_SCHEMA_VERSION: str = "1.0.0"

# Logging Constants
LOG_CORRELATION_ID_HEADER: str = "X-Correlation-ID"
LOG_REQUEST_ID_HEADER: str = "X-Request-ID"

# Metrics Constants
METRICS_NAMESPACE: str = "farfan_phase2"
METRICS_SUBSYSTEM: str = "executor"

# Validation Constants
VALIDATE_BINDINGS: bool = True
VALIDATE_SCHEMAS: bool = True
FAIL_FAST_MODE: bool = True

__all__ = [
    "EXPECTED_CONTRACT_COUNT",
    "CONTRACT_VERSION",
    "CONTRACT_FILE_PATTERN",
    "EXPECTED_CHUNK_COUNT",
    "POLICY_AREA_COUNT",
    "DIMENSION_COUNT",
    "EXPECTED_TASK_COUNT",
    "DEFAULT_EXECUTOR_TIMEOUT_S",
    "DEFAULT_PHASE_TIMEOUT_S",
    "DEFAULT_TASK_TIMEOUT_S",
    "DEFAULT_RETRY_COUNT",
    "DEFAULT_RETRY_BACKOFF_S",
    "DEFAULT_MEMORY_LIMIT_MB",
    "MAX_MEMORY_LIMIT_MB",
    "CQVR_TIER1_MAX",
    "CQVR_TIER2_MAX",
    "CQVR_TIER3_MAX",
    "CQVR_TOTAL_MAX",
    "CQVR_PRODUCCION_THRESHOLD",
    "CQVR_REFORMULAR_THRESHOLD",
    "CANONICAL_PHASE_2_DIR",
    "LEGACY_PHASE_2_DIR",
    "CONTRACT_DIR",
    "CONFIG_DIR",
    "EXECUTOR_CONFIG_SCHEMA_VERSION",
    "EXECUTOR_OUTPUT_SCHEMA_VERSION",
    "CALIBRATION_POLICY_SCHEMA_VERSION",
    "SYNCHRONIZATION_MANIFEST_SCHEMA_VERSION",
    "LOG_CORRELATION_ID_HEADER",
    "LOG_REQUEST_ID_HEADER",
    "METRICS_NAMESPACE",
    "METRICS_SUBSYSTEM",
    "VALIDATE_BINDINGS",
    "VALIDATE_SCHEMAS",
    "FAIL_FAST_MODE",
]
