"""
Phase 8 Primitives Package
===========================

This package contains all primitive types, constants, and foundational
definitions for Phase 8 - Recommendation Engine.

Contents:
- PHASE_8_CONSTANTS: All phase-level constants and configuration
- PHASE_8_TYPES: Type definitions and data structures
- PHASE_8_ENUMS: Enumeration types

According to GNEA (Global Nomenclature Enforcement Architecture), all primitives
and constants MUST be centralized in this package to ensure consistency and
prevent duplication.
"""

from .PHASE_8_CONSTANTS import (
    # Criticality levels
    CRITICALITY_CRITICAL,
    CRITICALITY_HIGH,
    CRITICALITY_MEDIUM,
    # Determinism
    DEFAULT_SEED,
    # Recommendation constants
    MAX_RECOMMENDATIONS_PER_AREA,
    MIN_CONFIDENCE_THRESHOLD,
    # Execution patterns
    PATTERN_ON_DEMAND,
    PATTERN_STREAMING,
    PHASE_CODENAME,
    PHASE_LABEL,
    PHASE_NAME,
    # Phase identification
    PHASE_NUMBER,
    SEED_STRATEGY,
    SIGNAL_WEIGHT_DEFAULT,
    # Stage definitions
    STAGE_BASE,
    STAGE_ENGINE,
    STAGE_ENRICHMENT,
    STAGE_INIT,
    STAGE_METADATA,
    TYPE_ADAPTER,
    # Module types
    TYPE_ENGINE,
    TYPE_ENRICHER,
    TYPE_UTILITY,
    VALID_CRITICALITY_LEVELS,
    VALID_EXECUTION_PATTERNS,
    VALID_MODULE_TYPES,
    VALID_STAGES,
)
from .PHASE_8_ENUMS import (
    HorizonType,
    Level,
    QualityLevel,
    ScoreBand,
    VarianceLevel,
    VerificationFormat,
)
from .PHASE_8_TYPES import (
    # Input types
    AnalysisResultsInput,
    ClusterKey,
    # Score types
    MicroScoreKey,
    PolicyContextInput,
    # Recommendation types
    RecommendationLevel,
    # Threshold types
    ScoreThreshold,
    SignalDataInput,
    VerificationType,
)

__all__ = [
    # Constants
    "PHASE_NUMBER",
    "PHASE_NAME",
    "PHASE_LABEL",
    "PHASE_CODENAME",
    "STAGE_BASE",
    "STAGE_INIT",
    "STAGE_ENGINE",
    "STAGE_ENRICHMENT",
    "VALID_STAGES",
    "STAGE_METADATA",
    "TYPE_ENGINE",
    "TYPE_ADAPTER",
    "TYPE_ENRICHER",
    "TYPE_UTILITY",
    "VALID_MODULE_TYPES",
    "CRITICALITY_CRITICAL",
    "CRITICALITY_HIGH",
    "CRITICALITY_MEDIUM",
    "VALID_CRITICALITY_LEVELS",
    "PATTERN_ON_DEMAND",
    "PATTERN_STREAMING",
    "VALID_EXECUTION_PATTERNS",
    "MAX_RECOMMENDATIONS_PER_AREA",
    "MIN_CONFIDENCE_THRESHOLD",
    "SIGNAL_WEIGHT_DEFAULT",
    "DEFAULT_SEED",
    "SEED_STRATEGY",
    # Types
    "AnalysisResultsInput",
    "PolicyContextInput",
    "SignalDataInput",
    "MicroScoreKey",
    "ClusterKey",
    "ScoreThreshold",
    "RecommendationLevel",
    "VerificationType",
    # Enums
    "Level",
    "ScoreBand",
    "VarianceLevel",
    "QualityLevel",
    "HorizonType",
    "VerificationFormat",
]
