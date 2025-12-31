"""
Module: src.farfan_pipeline.phases.Phase_two.PHASE_2_CONSTANTS
Purpose: Global constants for Phase 2 - Orchestration and Execution
Owner: phase2_core
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-30
"""
from __future__ import annotations

from typing import Final

__version__ = "1.0.0"
__phase__ = 2

__all__ = [
    "__version__",
    "__phase__",
    "PHASE_NUMBER",
    "PHASE_NAME",
    "PHASE_LABEL",
    "STAGE_BASE",
    "STAGE_TESTING",
    "STAGE_INIT",
    "STAGE_VALIDATION",
    "STAGE_RESOURCES",
    "STAGE_SYNC",
    "STAGE_ORCHESTRATION",
    "STAGE_EXECUTION",
    "STAGE_RESERVED",
    "STAGE_ANALYSIS",
    "STAGE_SYNTHESIS",
    "STAGE_TELEMETRY",
    "VALID_STAGES",
    "TYPE_AUTHORITY",
    "TYPE_REGISTRY",
    "TYPE_CONFIG",
    "TYPE_VALIDATOR",
    "TYPE_MANAGER",
    "TYPE_EXECUTOR",
    "TYPE_ORCHESTRATOR",
]

# ============================================================================
# PHASE IDENTIFICATION
# ============================================================================

PHASE_NUMBER: Final[int] = 2
PHASE_NAME: Final[str] = "Phase 2: Orchestration and Execution"
PHASE_LABEL: Final[str] = f"Phase {PHASE_NUMBER}"

# ============================================================================
# STAGE DEFINITIONS
# ============================================================================

STAGE_BASE: Final[int] = 0
STAGE_TESTING: Final[int] = 9
STAGE_INIT: Final[int] = 10
STAGE_VALIDATION: Final[int] = 20
STAGE_RESOURCES: Final[int] = 30
STAGE_SYNC: Final[int] = 40
STAGE_ORCHESTRATION: Final[int] = 50
STAGE_EXECUTION: Final[int] = 60
STAGE_RESERVED: Final[int] = 70
STAGE_ANALYSIS: Final[int] = 80
STAGE_SYNTHESIS: Final[int] = 90
STAGE_TELEMETRY: Final[int] = 95

VALID_STAGES: Final[set[int]] = {
    STAGE_BASE,
    STAGE_TESTING,
    STAGE_INIT,
    STAGE_VALIDATION,
    STAGE_RESOURCES,
    STAGE_SYNC,
    STAGE_ORCHESTRATION,
    STAGE_EXECUTION,
    STAGE_ANALYSIS,
    STAGE_SYNTHESIS,
    STAGE_TELEMETRY,
}

# ============================================================================
# MODULE TYPES
# ============================================================================

TYPE_AUTHORITY: Final[str] = "AUTH"
TYPE_REGISTRY: Final[str] = "REG"
TYPE_CONFIG: Final[str] = "CFG"
TYPE_VALIDATOR: Final[str] = "VAL"
TYPE_MANAGER: Final[str] = "MGR"
TYPE_EXECUTOR: Final[str] = "EXEC"
TYPE_ORCHESTRATOR: Final[str] = "ORCH"
TYPE_ANALYZER: Final[str] = "ANAL"
TYPE_SYNTHESIZER: Final[str] = "SYNT"
TYPE_PROFILER: Final[str] = "PROF"
TYPE_UTILITY: Final[str] = "UTIL"

VALID_MODULE_TYPES: Final[set[str]] = {
    TYPE_AUTHORITY,
    TYPE_REGISTRY,
    TYPE_CONFIG,
    TYPE_VALIDATOR,
    TYPE_MANAGER,
    TYPE_EXECUTOR,
    TYPE_ORCHESTRATOR,
    TYPE_ANALYZER,
    TYPE_SYNTHESIZER,
    TYPE_PROFILER,
    TYPE_UTILITY,
}

# ============================================================================
# CRITICALITY LEVELS
# ============================================================================

CRITICALITY_CRITICAL: Final[str] = "CRITICAL"
CRITICALITY_HIGH: Final[str] = "HIGH"
CRITICALITY_MEDIUM: Final[str] = "MEDIUM"
CRITICALITY_LOW: Final[str] = "LOW"

VALID_CRITICALITY_LEVELS: Final[set[str]] = {
    CRITICALITY_CRITICAL,
    CRITICALITY_HIGH,
    CRITICALITY_MEDIUM,
    CRITICALITY_LOW,
}

# ============================================================================
# EXECUTION PATTERNS
# ============================================================================

PATTERN_SINGLETON: Final[str] = "Singleton"
PATTERN_PER_TASK: Final[str] = "Per-Task"
PATTERN_CONTINUOUS: Final[str] = "Continuous"
PATTERN_ON_DEMAND: Final[str] = "On-Demand"
PATTERN_PARALLEL: Final[str] = "Parallel"

VALID_EXECUTION_PATTERNS: Final[set[str]] = {
    PATTERN_SINGLETON,
    PATTERN_PER_TASK,
    PATTERN_CONTINUOUS,
    PATTERN_ON_DEMAND,
    PATTERN_PARALLEL,
}

# ============================================================================
# RESOURCE LIMITS
# ============================================================================

MAX_MEMORY_MB: Final[int] = 4096
MAX_CPU_PERCENT: Final[float] = 80.0
TIMEOUT_SECONDS: Final[int] = 300
EXECUTION_ITERATIONS: Final[int] = 300

# ============================================================================
# DETERMINISM
# ============================================================================

DEFAULT_SEED: Final[int] = 42
SEED_STRATEGY: Final[str] = "FIXED"

# ============================================================================
# PHASE 2 SPECIFIC CONSTANTS
# ============================================================================

CHUNK_SIZE: Final[int] = 10
MAX_TASKS: Final[int] = 300
IRRIGATION_BATCH_SIZE: Final[int] = 50
EVIDENCE_THRESHOLD: Final[float] = 0.7
CALIBRATION_WINDOW: Final[int] = 10
