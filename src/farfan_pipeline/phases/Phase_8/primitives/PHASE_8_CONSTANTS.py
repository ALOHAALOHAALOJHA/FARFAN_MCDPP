"""
Module: src.farfan_pipeline.phases.Phase_eight.primitives.PHASE_8_CONSTANTS
Purpose: Global constants for Phase 8 - Recommendation Engine
Owner: phase8_core
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-05

This module centralizes all constants for Phase 8 following the GNEA
(Global Nomenclature Enforcement Architecture) standards.

All constants are immutable (Final) and organized by category.
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
TYPE_VALIDATOR: Final[str] = "VAL"
TYPE_INTERFACE: Final[str] = "INTF"

VALID_MODULE_TYPES: Final[frozenset[str]] = frozenset(
    {
        TYPE_ENGINE,
        TYPE_ADAPTER,
        TYPE_ENRICHER,
        TYPE_UTILITY,
        TYPE_VALIDATOR,
        TYPE_INTERFACE,
    }
)

# ============================================================================
# CRITICALITY LEVELS
# ============================================================================

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

# ============================================================================
# EXECUTION PATTERNS
# ============================================================================

PATTERN_ON_DEMAND: Final[str] = "On-Demand"
PATTERN_STREAMING: Final[str] = "Streaming"
PATTERN_BATCH: Final[str] = "Batch"

VALID_EXECUTION_PATTERNS: Final[frozenset[str]] = frozenset(
    {
        PATTERN_ON_DEMAND,
        PATTERN_STREAMING,
        PATTERN_BATCH,
    }
)

# ============================================================================
# RECOMMENDATION CONSTANTS
# ============================================================================

MAX_RECOMMENDATIONS_PER_AREA: Final[int] = 10
MIN_CONFIDENCE_THRESHOLD: Final[float] = 0.6
SIGNAL_WEIGHT_DEFAULT: Final[float] = 1.0

# Score thresholds
MICRO_SCORE_THRESHOLD_DEFAULT: Final[float] = 1.65
MESO_SCORE_BAND_LOW: Final[float] = 55.0
MESO_SCORE_BAND_HIGH: Final[float] = 75.0
MACRO_SCORE_THRESHOLD_DEFAULT: Final[float] = 65.0

# Variance thresholds
VARIANCE_LOW_THRESHOLD: Final[float] = 0.08
VARIANCE_HIGH_THRESHOLD: Final[float] = 0.18

# ============================================================================
# SCORE BOUNDS
# ============================================================================

MICRO_SCORE_MIN: Final[float] = 0.0
MICRO_SCORE_MAX: Final[float] = 3.0
MESO_SCORE_MIN: Final[float] = 0.0
MESO_SCORE_MAX: Final[float] = 100.0
MACRO_SCORE_MIN: Final[float] = 0.0
MACRO_SCORE_MAX: Final[float] = 100.0

# ============================================================================
# RECOMMENDATION LEVELS
# ============================================================================

LEVEL_MICRO: Final[str] = "MICRO"
LEVEL_MESO: Final[str] = "MESO"
LEVEL_MACRO: Final[str] = "MACRO"

VALID_LEVELS: Final[frozenset[str]] = frozenset(
    {
        LEVEL_MICRO,
        LEVEL_MESO,
        LEVEL_MACRO,
    }
)

# ============================================================================
# SCORE BANDS (MESO/MACRO)
# ============================================================================

BAND_BAJO: Final[str] = "BAJO"
BAND_MEDIO: Final[str] = "MEDIO"
BAND_ALTO: Final[str] = "ALTO"
BAND_SATISFACTORIO: Final[str] = "SATISFACTORIO"
BAND_INSUFICIENTE: Final[str] = "INSUFICIENTE"

VALID_SCORE_BANDS: Final[frozenset[str]] = frozenset(
    {
        BAND_BAJO,
        BAND_MEDIO,
        BAND_ALTO,
        BAND_SATISFACTORIO,
        BAND_INSUFICIENTE,
    }
)

# ============================================================================
# VARIANCE LEVELS
# ============================================================================

VARIANCE_BAJA: Final[str] = "BAJA"
VARIANCE_MEDIA: Final[str] = "MEDIA"
VARIANCE_ALTA: Final[str] = "ALTA"

VALID_VARIANCE_LEVELS: Final[frozenset[str]] = frozenset(
    {
        VARIANCE_BAJA,
        VARIANCE_MEDIA,
        VARIANCE_ALTA,
    }
)

# ============================================================================
# HORIZON TYPES
# ============================================================================

HORIZON_T0: Final[str] = "T0"
HORIZON_T1: Final[str] = "T1"
HORIZON_T2: Final[str] = "T2"
HORIZON_T3: Final[str] = "T3"

VALID_HORIZONS: Final[frozenset[str]] = frozenset(
    {
        HORIZON_T0,
        HORIZON_T1,
        HORIZON_T2,
        HORIZON_T3,
    }
)

# ============================================================================
# VERIFICATION TYPES
# ============================================================================

VERIFICATION_DOCUMENT: Final[str] = "DOCUMENT"
VERIFICATION_SYSTEM_STATE: Final[str] = "SYSTEM_STATE"
VERIFICATION_METRIC: Final[str] = "METRIC"
VERIFICATION_ATTESTATION: Final[str] = "ATTESTATION"

VALID_VERIFICATION_TYPES: Final[frozenset[str]] = frozenset(
    {
        VERIFICATION_DOCUMENT,
        VERIFICATION_SYSTEM_STATE,
        VERIFICATION_METRIC,
        VERIFICATION_ATTESTATION,
    }
)

# ============================================================================
# CLUSTER IDENTIFIERS
# ============================================================================

CLUSTER_CL01: Final[str] = "CL01"
CLUSTER_CL02: Final[str] = "CL02"
CLUSTER_CL03: Final[str] = "CL03"
CLUSTER_CL04: Final[str] = "CL04"

VALID_CLUSTERS: Final[frozenset[str]] = frozenset(
    {
        CLUSTER_CL01,
        CLUSTER_CL02,
        CLUSTER_CL03,
        CLUSTER_CL04,
    }
)

# ============================================================================
# POLICY AREA CONSTANTS
# ============================================================================

POLICY_AREAS_COUNT: Final[int] = 10
DIMENSIONS_COUNT: Final[int] = 6
QUESTIONS_PER_PA: Final[int] = 30
TOTAL_MICRO_QUESTIONS: Final[int] = POLICY_AREAS_COUNT * QUESTIONS_PER_PA  # 300

# ============================================================================
# ENHANCED FEATURES (v2.0 Rules)
# ============================================================================

REQUIRED_ENHANCED_FEATURES: Final[frozenset[str]] = frozenset(
    {
        "template_parameterization",
        "execution_logic",
        "measurable_indicators",
        "unambiguous_time_horizons",
        "testable_verification",
        "cost_tracking",
        "authority_mapping",
    }
)

# ============================================================================
# SIGNAL ENRICHMENT CONSTANTS
# ============================================================================

STRONG_PATTERN_THRESHOLD: Final[int] = 5
STRONG_INDICATOR_THRESHOLD: Final[int] = 3
CRITICAL_SCORE_THRESHOLD: Final[float] = 0.3
LOW_SCORE_THRESHOLD: Final[float] = 0.5
CRITICAL_PRIORITY_BOOST: Final[float] = 0.3
LOW_PRIORITY_BOOST: Final[float] = 0.2
INSUFFICIENT_QUALITY_BOOST: Final[float] = 0.2
ACTIONABILITY_PATTERN_THRESHOLD: Final[int] = 10
ACTIONABILITY_INDICATOR_THRESHOLD: Final[int] = 5
ACTIONABILITY_BOOST: Final[float] = 0.15

# ============================================================================
# DETERMINISM
# ============================================================================

DEFAULT_SEED: Final[int] = 42
SEED_STRATEGY: Final[str] = "FIXED"

# ============================================================================
# FILE PATHS (Relative to Phase 8)
# ============================================================================

RULES_PATH_ENHANCED: Final[str] = "json_phase_eight/recommendation_rules_enhanced.json"
RULES_PATH_SIMPLE: Final[str] = "json_phase_eight/recommendation_rules.json"
SCHEMA_PATH: Final[str] = "rules/recommendation_rules.schema.json"

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Phase identification
    "PHASE_NUMBER",
    "PHASE_NAME",
    "PHASE_LABEL",
    "PHASE_CODENAME",
    # Stages
    "STAGE_BASE",
    "STAGE_INIT",
    "STAGE_ENGINE",
    "STAGE_ENRICHMENT",
    "VALID_STAGES",
    "STAGE_METADATA",
    # Module types
    "TYPE_ENGINE",
    "TYPE_ADAPTER",
    "TYPE_ENRICHER",
    "TYPE_UTILITY",
    "TYPE_VALIDATOR",
    "TYPE_INTERFACE",
    "VALID_MODULE_TYPES",
    # Criticality
    "CRITICALITY_CRITICAL",
    "CRITICALITY_HIGH",
    "CRITICALITY_MEDIUM",
    "CRITICALITY_LOW",
    "VALID_CRITICALITY_LEVELS",
    # Execution patterns
    "PATTERN_ON_DEMAND",
    "PATTERN_STREAMING",
    "PATTERN_BATCH",
    "VALID_EXECUTION_PATTERNS",
    # Recommendation constants
    "MAX_RECOMMENDATIONS_PER_AREA",
    "MIN_CONFIDENCE_THRESHOLD",
    "SIGNAL_WEIGHT_DEFAULT",
    "MICRO_SCORE_THRESHOLD_DEFAULT",
    "MESO_SCORE_BAND_LOW",
    "MESO_SCORE_BAND_HIGH",
    "MACRO_SCORE_THRESHOLD_DEFAULT",
    "VARIANCE_LOW_THRESHOLD",
    "VARIANCE_HIGH_THRESHOLD",
    # Score bounds
    "MICRO_SCORE_MIN",
    "MICRO_SCORE_MAX",
    "MESO_SCORE_MIN",
    "MESO_SCORE_MAX",
    "MACRO_SCORE_MIN",
    "MACRO_SCORE_MAX",
    # Levels
    "LEVEL_MICRO",
    "LEVEL_MESO",
    "LEVEL_MACRO",
    "VALID_LEVELS",
    # Score bands
    "BAND_BAJO",
    "BAND_MEDIO",
    "BAND_ALTO",
    "BAND_SATISFACTORIO",
    "BAND_INSUFICIENTE",
    "VALID_SCORE_BANDS",
    # Variance levels
    "VARIANCE_BAJA",
    "VARIANCE_MEDIA",
    "VARIANCE_ALTA",
    "VALID_VARIANCE_LEVELS",
    # Horizons
    "HORIZON_T0",
    "HORIZON_T1",
    "HORIZON_T2",
    "HORIZON_T3",
    "VALID_HORIZONS",
    # Verification types
    "VERIFICATION_DOCUMENT",
    "VERIFICATION_SYSTEM_STATE",
    "VERIFICATION_METRIC",
    "VERIFICATION_ATTESTATION",
    "VALID_VERIFICATION_TYPES",
    # Clusters
    "CLUSTER_CL01",
    "CLUSTER_CL02",
    "CLUSTER_CL03",
    "CLUSTER_CL04",
    "VALID_CLUSTERS",
    # Policy areas
    "POLICY_AREAS_COUNT",
    "DIMENSIONS_COUNT",
    "QUESTIONS_PER_PA",
    "TOTAL_MICRO_QUESTIONS",
    # Enhanced features
    "REQUIRED_ENHANCED_FEATURES",
    # Signal enrichment
    "STRONG_PATTERN_THRESHOLD",
    "STRONG_INDICATOR_THRESHOLD",
    "CRITICAL_SCORE_THRESHOLD",
    "LOW_SCORE_THRESHOLD",
    "CRITICAL_PRIORITY_BOOST",
    "LOW_PRIORITY_BOOST",
    "INSUFFICIENT_QUALITY_BOOST",
    "ACTIONABILITY_PATTERN_THRESHOLD",
    "ACTIONABILITY_INDICATOR_THRESHOLD",
    "ACTIONABILITY_BOOST",
    # Determinism
    "DEFAULT_SEED",
    "SEED_STRATEGY",
    # File paths
    "RULES_PATH_ENHANCED",
    "RULES_PATH_SIMPLE",
    "SCHEMA_PATH",
]
