"""
Module: src.farfan_pipeline.phases.Phase_eight.PHASE_8_CONSTANTS
Purpose: Global constants for Phase 8 - Recommendation Engine
Owner: phase8_core
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-30
"""

from __future__ import annotations

from typing import Final

__version__ = "1.0.0"
__phase__ = 8

# ============================================================================
# PHASE IDENTIFICATION
# ============================================================================

PHASE_NUMBER: Final[int] = 8
PHASE_NAME: Final[str] = "Phase 8: Recommendation Engine"
PHASE_LABEL: Final[str] = f"Phase {PHASE_NUMBER}"
PHASE_CODENAME: Final[str] = "RECOMMENDER"

# ============================================================================
# STAGE DEFINITIONS
# ============================================================================

STAGE_BASE: Final[int] = 0
STAGE_INIT: Final[int] = 10
STAGE_ENGINE: Final[int] = 20
STAGE_ENRICHMENT: Final[int] = 30

VALID_STAGES: Final[frozenset[int]] = frozenset(
    {
        STAGE_BASE,
        STAGE_INIT,
        STAGE_ENGINE,
        STAGE_ENRICHMENT,
    }
)

STAGE_METADATA: Final[dict[int, dict[str, str]]] = {
    0: {"name": "Base", "description": "Package init and types"},
    10: {"name": "Init", "description": "Initialization and configuration"},
    20: {"name": "Engine", "description": "Recommendation engine core"},
    30: {"name": "Enrichment", "description": "Signal-enriched recommendations"},
}

# ============================================================================
# MODULE TYPES
# ============================================================================

TYPE_ENGINE: Final[str] = "ENG"
TYPE_ADAPTER: Final[str] = "ADP"
TYPE_ENRICHER: Final[str] = "ENR"
TYPE_UTILITY: Final[str] = "UTIL"

VALID_MODULE_TYPES: Final[frozenset[str]] = frozenset(
    {
        TYPE_ENGINE,
        TYPE_ADAPTER,
        TYPE_ENRICHER,
        TYPE_UTILITY,
    }
)

# ============================================================================
# CRITICALITY LEVELS
# ============================================================================

CRITICALITY_CRITICAL: Final[str] = "CRITICAL"
CRITICALITY_HIGH: Final[str] = "HIGH"
CRITICALITY_MEDIUM: Final[str] = "MEDIUM"

VALID_CRITICALITY_LEVELS: Final[frozenset[str]] = frozenset(
    {
        CRITICALITY_CRITICAL,
        CRITICALITY_HIGH,
        CRITICALITY_MEDIUM,
    }
)

# ============================================================================
# EXECUTION PATTERNS
# ============================================================================

PATTERN_ON_DEMAND: Final[str] = "On-Demand"
PATTERN_STREAMING: Final[str] = "Streaming"

VALID_EXECUTION_PATTERNS: Final[frozenset[str]] = frozenset(
    {
        PATTERN_ON_DEMAND,
        PATTERN_STREAMING,
    }
)

# ============================================================================
# RECOMMENDATION CONSTANTS
# ============================================================================

MAX_RECOMMENDATIONS_PER_AREA: Final[int] = 10
MIN_CONFIDENCE_THRESHOLD: Final[float] = 0.6
SIGNAL_WEIGHT_DEFAULT: Final[float] = 1.0

# ============================================================================
# DETERMINISM
# ============================================================================

DEFAULT_SEED: Final[int] = 42
SEED_STRATEGY: Final[str] = "FIXED"

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
    "MAX_RECOMMENDATIONS_PER_AREA",
    "MIN_CONFIDENCE_THRESHOLD",
    "SIGNAL_WEIGHT_DEFAULT",
    "DEFAULT_SEED",
    "SEED_STRATEGY",
]
