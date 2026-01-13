"""
Module: src.farfan_pipeline.phases.Phase_0.PHASE_0_CONSTANTS
Purpose: Canonical constants for Phase 0 - Validation, Hardening & Bootstrap
Owner: phase0_core
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-29

This module defines the authoritative stage taxonomy, module types, criticality
levels, and execution patterns for Phase 0 of the F.A.R.F.A.N pipeline.

Phase 0 is the FOUNDATION LAYER that executes BEFORE any analytical processing.
It guarantees:
    - Deterministic execution environment
    - Resource bounds enforcement
    - Configuration validation
    - Wiring integrity verification
    - Boot sequence orchestration
"""

from __future__ import annotations

from typing import Final

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2025-12-29"
__modified__ = "2026-01-07"

# =============================================================================
# PHASE IDENTIFICATION
# =============================================================================

PHASE_NUMBER: Final[int] = 0
PHASE_NAME: Final[str] = "Phase 0: Validation, Hardening & Bootstrap"
PHASE_LABEL: Final[str] = "Phase 0"
PHASE_CODENAME: Final[str] = "FOUNDATION"

# =============================================================================
# STAGE TAXONOMY
# =============================================================================
#
# Phase 0 uses a 7-stage architecture representing the temporal sequence
# of validation and initialization operations:
#
#   STAGE 00: Infrastructure (init, errors, protocols, constants)
#   STAGE 10: Environment Configuration (paths, config, logging)
#   STAGE 20: Determinism Enforcement (seeds, hashing, reproducibility)
#   STAGE 30: Resource Control (limits, watchdog, enforcement, metrics)
#   STAGE 40: Validation (input, schema, signature, coverage)
#   STAGE 50: Boot Sequence (checks, gates, wiring)
#   STAGE 90: Integration (main entry, runner, bootstrap orchestration)
#
# =============================================================================

# Stage 00: Infrastructure - Base errors, types, and initialization
STAGE_INFRASTRUCTURE: Final[int] = 0
STAGE_00_NAME: Final[str] = "Infrastructure"
STAGE_00_DESCRIPTION: Final[str] = "Base errors, types, protocols, package initialization"

# Stage 10: Environment Configuration - Paths, runtime config, logging
STAGE_ENVIRONMENT: Final[int] = 10
STAGE_10_NAME: Final[str] = "Environment Configuration"
STAGE_10_DESCRIPTION: Final[str] = "Paths resolution, runtime config, structured logging"

# Stage 20: Determinism Enforcement - Seeds, hashing, reproducibility
STAGE_DETERMINISM: Final[int] = 20
STAGE_20_NAME: Final[str] = "Determinism Enforcement"
STAGE_20_DESCRIPTION: Final[str] = "Seed management, hash computation, deterministic execution"

# Stage 30: Resource Control - Limits, watchdog, kernel enforcement, metrics
STAGE_RESOURCES: Final[int] = 30
STAGE_30_NAME: Final[str] = "Resource Control"
STAGE_30_DESCRIPTION: Final[str] = (
    "Hard resource limits, memory watchdog, kernel enforcement, performance metrics"
)

# Stage 40: Validation - Input, schema, signature validation
STAGE_VALIDATION: Final[int] = 40
STAGE_40_NAME: Final[str] = "Validation"
STAGE_40_DESCRIPTION: Final[str] = (
    "Input validation, schema monitoring, signature verification with security hardening"
)

# Stage 50: Boot Sequence - Checks, gates, wiring verification
STAGE_BOOT: Final[int] = 50
STAGE_50_NAME: Final[str] = "Boot Sequence"
STAGE_50_DESCRIPTION: Final[str] = (
    "Boot checks, exit gates, wiring verification with security handoff"
)

# Stage 90: Integration - Main entry, runner, bootstrap orchestration
STAGE_INTEGRATION: Final[int] = 90
STAGE_90_NAME: Final[str] = "Integration"
STAGE_90_DESCRIPTION: Final[str] = (
    "Main entry point, pipeline runner, and bootstrap orchestration with secure handoff"
)

# All valid stages
VALID_STAGES: Final[frozenset[int]] = frozenset(
    {
        STAGE_INFRASTRUCTURE,
        STAGE_ENVIRONMENT,
        STAGE_DETERMINISM,
        STAGE_RESOURCES,
        STAGE_VALIDATION,
        STAGE_BOOT,
        STAGE_INTEGRATION,
    }
)

# Stage metadata dictionary
STAGE_METADATA: Final[dict[int, dict[str, str]]] = {
    0: {"name": STAGE_00_NAME, "description": STAGE_00_DESCRIPTION},
    10: {"name": STAGE_10_NAME, "description": STAGE_10_DESCRIPTION},
    20: {"name": STAGE_20_NAME, "description": STAGE_20_DESCRIPTION},
    30: {"name": STAGE_30_NAME, "description": STAGE_30_DESCRIPTION},
    40: {"name": STAGE_40_NAME, "description": STAGE_40_DESCRIPTION},
    50: {"name": STAGE_50_NAME, "description": STAGE_50_DESCRIPTION},
    90: {"name": STAGE_90_NAME, "description": STAGE_90_DESCRIPTION},
}

# =============================================================================
# MODULE TYPES
# =============================================================================

TYPE_INFRASTRUCTURE: Final[str] = "INFRA"
TYPE_CONFIG: Final[str] = "CFG"
TYPE_VALIDATOR: Final[str] = "VAL"
TYPE_ENFORCER: Final[str] = "ENF"
TYPE_UTILITY: Final[str] = "UTIL"
TYPE_ORCHESTRATOR: Final[str] = "ORCH"
TYPE_ENTRY: Final[str] = "ENTRY"

VALID_MODULE_TYPES: Final[frozenset[str]] = frozenset(
    {
        TYPE_INFRASTRUCTURE,
        TYPE_CONFIG,
        TYPE_VALIDATOR,
        TYPE_ENFORCER,
        TYPE_UTILITY,
        TYPE_ORCHESTRATOR,
        TYPE_ENTRY,
    }
)

# =============================================================================
# CRITICALITY LEVELS
# =============================================================================

CRITICALITY_CRITICAL: Final[str] = "CRITICAL"
CRITICALITY_HIGH: Final[str] = "HIGH"
CRITICALITY_MEDIUM: Final[str] = "MEDIUM"
CRITICALITY_LOW: Final[str] = "LOW"

VALID_CRITICALITY_LEVELS: Final[frozenset[str]] = frozenset(
    {
        CRITICALITY_CRITICAL,
        CRITICALITY_HIGH,
        CRITICALITY_MEDIUM,
        CRITICALITY_LOW,
    }
)

# =============================================================================
# EXECUTION PATTERNS
# =============================================================================

PATTERN_SINGLETON: Final[str] = "Singleton"
PATTERN_ON_DEMAND: Final[str] = "On-Demand"
PATTERN_BOOT_ONCE: Final[str] = "Boot-Once"
PATTERN_CONTINUOUS: Final[str] = "Continuous"

VALID_EXECUTION_PATTERNS: Final[frozenset[str]] = frozenset(
    {
        PATTERN_SINGLETON,
        PATTERN_ON_DEMAND,
        PATTERN_BOOT_ONCE,
        PATTERN_CONTINUOUS,
    }
)

# =============================================================================
# RESOURCE LIMITS (Phase 0 Defaults)
# =============================================================================

DEFAULT_MEMORY_MB: Final[int] = 2048
DEFAULT_CPU_SECONDS: Final[int] = 300
DEFAULT_DISK_MB: Final[int] = 500
DEFAULT_FILE_DESCRIPTORS: Final[int] = 1024
WATCHDOG_THRESHOLD_PERCENT: Final[int] = 90
WATCHDOG_CHECK_INTERVAL_S: Final[float] = 1.0

# =============================================================================
# DETERMINISM DEFAULTS
# =============================================================================

DEFAULT_SEED: Final[int] = 42
SEED_STRATEGY: Final[str] = "FIXED"
HASH_ALGORITHM: Final[str] = "blake3"

# =============================================================================
# VALIDATION THRESHOLDS
# =============================================================================

MIN_COVERAGE_PERCENT: Final[float] = 80.0
MAX_VALIDATION_ERRORS: Final[int] = 0
SCHEMA_STRICT_MODE: Final[bool] = True

# =============================================================================
# MODULE MANIFEST (Canonical file mapping)
# =============================================================================
#
# This manifest defines the canonical mapping from legacy filenames to the
# new phase0_{STAGE}_{ORDER}_{name}.py format.
#
# Format: (stage, order, canonical_name, legacy_name, type, criticality)
#
# =============================================================================

MODULE_MANIFEST: Final[tuple[tuple[int, int, str, str, str, str], ...]] = (
    # Stage 00: Infrastructure
    (0, 0, "init", "__init__", TYPE_INFRASTRUCTURE, CRITICALITY_LOW),
    (0, 1, "domain_errors", "domain_errors", TYPE_INFRASTRUCTURE, CRITICALITY_HIGH),
    (0, 2, "runtime_error_fixes", "runtime_error_fixes", TYPE_INFRASTRUCTURE, CRITICALITY_MEDIUM),
    (0, 3, "protocols", None, TYPE_INFRASTRUCTURE, CRITICALITY_CRITICAL),
    # Stage 10: Environment Configuration
    (10, 0, "paths", "paths", TYPE_CONFIG, CRITICALITY_CRITICAL),
    (10, 1, "runtime_config", "runtime_config", TYPE_CONFIG, CRITICALITY_CRITICAL),
    (10, 2, "json_logger", "json_logger", TYPE_CONFIG, CRITICALITY_HIGH),
    # Stage 20: Determinism Enforcement
    (20, 0, "seed_factory", "seed_factory", TYPE_ENFORCER, CRITICALITY_CRITICAL),
    (20, 1, "hash_utils", "hash_utils", TYPE_UTILITY, CRITICALITY_HIGH),
    (20, 2, "determinism", "determinism", TYPE_ENFORCER, CRITICALITY_CRITICAL),
    (20, 3, "determinism_helpers", "determinism_helpers", TYPE_UTILITY, CRITICALITY_HIGH),
    (
        20,
        4,
        "deterministic_execution",
        "deterministic_execution",
        TYPE_ENFORCER,
        CRITICALITY_CRITICAL,
    ),
    # Stage 30: Resource Control
    (30, 0, "resource_controller", "resource_controller", TYPE_ENFORCER, CRITICALITY_CRITICAL),
    (30, 1, "performance_metrics", None, TYPE_UTILITY, CRITICALITY_MEDIUM),
    # Stage 40: Validation
    (40, 0, "input_validation", "phase0_input_validation", TYPE_VALIDATOR, CRITICALITY_CRITICAL),
    (40, 1, "schema_monitor", "schema_monitor", TYPE_VALIDATOR, CRITICALITY_HIGH),
    (40, 2, "signature_validator", "signature_validator", TYPE_VALIDATOR, CRITICALITY_HIGH),
    (40, 3, "coverage_gate", "coverage_gate", TYPE_VALIDATOR, CRITICALITY_MEDIUM),
    # Stage 50: Boot Sequence
    (50, 0, "boot_checks", "boot_checks", TYPE_ORCHESTRATOR, CRITICALITY_CRITICAL),
    (50, 1, "exit_gates", "exit_gates", TYPE_ORCHESTRATOR, CRITICALITY_HIGH),
    # Stage 90: Integration
    (90, 0, "main", "main", TYPE_ENTRY, CRITICALITY_CRITICAL),
    (
        90,
        1,
        "verified_pipeline_runner",
        "verified_pipeline_runner",
        TYPE_ORCHESTRATOR,
        CRITICALITY_CRITICAL,
    ),
    (90, 2, "bootstrap", "bootstrap", TYPE_ORCHESTRATOR, CRITICALITY_CRITICAL),
    (90, 3, "wiring_validator", None, TYPE_VALIDATOR, CRITICALITY_CRITICAL),
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_canonical_filename(stage: int, order: int, name: str) -> str:
    """Generate canonical filename from stage, order, and name."""
    return f"phase0_{stage:02d}_{order:02d}_{name}.py"


def get_stage_modules(stage: int) -> list[tuple[int, int, str, str, str, str]]:
    """Get all modules belonging to a specific stage."""
    return [m for m in MODULE_MANIFEST if m[0] == stage]


def validate_module_name(filename: str) -> bool:
    """Validate that a filename follows the canonical format."""
    import re

    pattern = r"^phase0_\d{2}_\d{2}_[a-z][a-z0-9_]+\.py$"
    return bool(re.match(pattern, filename))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Phase identification
    "PHASE_NUMBER",
    "PHASE_NAME",
    "PHASE_LABEL",
    "PHASE_CODENAME",
    # Stages
    "STAGE_INFRASTRUCTURE",
    "STAGE_ENVIRONMENT",
    "STAGE_DETERMINISM",
    "STAGE_RESOURCES",
    "STAGE_VALIDATION",
    "STAGE_BOOT",
    "STAGE_INTEGRATION",
    "VALID_STAGES",
    "STAGE_METADATA",
    # Module types
    "TYPE_INFRASTRUCTURE",
    "TYPE_CONFIG",
    "TYPE_VALIDATOR",
    "TYPE_ENFORCER",
    "TYPE_UTILITY",
    "TYPE_ORCHESTRATOR",
    "TYPE_ENTRY",
    "VALID_MODULE_TYPES",
    # Criticality
    "CRITICALITY_CRITICAL",
    "CRITICALITY_HIGH",
    "CRITICALITY_MEDIUM",
    "CRITICALITY_LOW",
    "VALID_CRITICALITY_LEVELS",
    # Execution patterns
    "PATTERN_SINGLETON",
    "PATTERN_ON_DEMAND",
    "PATTERN_BOOT_ONCE",
    "PATTERN_CONTINUOUS",
    "VALID_EXECUTION_PATTERNS",
    # Resource limits
    "DEFAULT_MEMORY_MB",
    "DEFAULT_CPU_SECONDS",
    "DEFAULT_DISK_MB",
    "DEFAULT_FILE_DESCRIPTORS",
    "WATCHDOG_THRESHOLD_PERCENT",
    "WATCHDOG_CHECK_INTERVAL_S",
    # Determinism
    "DEFAULT_SEED",
    "SEED_STRATEGY",
    "HASH_ALGORITHM",
    # Validation
    "MIN_COVERAGE_PERCENT",
    "MAX_VALIDATION_ERRORS",
    "SCHEMA_STRICT_MODE",
    # Manifest
    "MODULE_MANIFEST",
    # Functions
    "get_canonical_filename",
    "get_stage_modules",
    "validate_module_name",
]
