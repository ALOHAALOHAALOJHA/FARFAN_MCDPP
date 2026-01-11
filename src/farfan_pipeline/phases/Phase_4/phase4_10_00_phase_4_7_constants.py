"""
Phase 4-7 Canonical Constants
============================

This module contains all canonical constants for Phases 4-7 (Hierarchical Aggregation).
Following the F.A.R.F.A.N. canonical phase policy, constants are organized by:

1. Quality Levels: Thresholds for determining result quality
2. Aggregation Weights: Hierarchical weights for dimension/area/cluster/macro
3. Scoring Modalities: Score transformation rules
4. Dispersion Thresholds: Coherence and dispersion analysis constants
5. Constitutional Bounds: Permissible ranges for aggregation components
6. Metadata Keys: Standardized keys for provenance tracking

Author: F.A.R.F.A.N. Pipeline Team
Version: 1.0.0
Canonical Phase: Four-Five-Six-Seven (Hierarchical Aggregation)
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 4
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

# =============================================================================
# PHASE IDENTIFICATION
# =============================================================================

PHASE_ID = "PHASE_4_7"
PHASE_NAME = "Hierarchical Aggregation Pipeline"
PHASE_VERSION = "1.0.0"

PHASE_4_ID = "PHASE_4"
PHASE_4_NAME = "Dimension Aggregation"

PHASE_5_ID = "PHASE_5"
PHASE_5_NAME = "Area Policy Aggregation"

PHASE_6_ID = "PHASE_6"
PHASE_6_NAME = "Cluster Aggregation"

PHASE_7_ID = "PHASE_7"
PHASE_7_NAME = "Macro Evaluation"

# =============================================================================
# QUALITY LEVELS
# =============================================================================
# Thresholds for determining aggregated result quality levels

QUALITY_LEVEL_EXCELENTE = "EXCELENTE"
QUALITY_LEVEL_BUENO = "BUENO"
QUALITY_LEVEL_ACEPTABLE = "ACEPTABLE"
QUALITY_LEVEL_INSUFICIENTE = "INSUFICIENTE"

# Quality thresholds (macro score in [0, 3] scale)
QUALITY_THRESHOLD_EXCELENTE_MIN = 2.5
QUALITY_THRESHOLD_BUENO_MIN = 2.0
QUALITY_THRESHOLD_ACEPTABLE_MIN = 1.5
QUALITY_THRESHOLD_INSUFICIENTE_MAX = 1.5

# =============================================================================
# AGGREGATION WEIGHTS
# =============================================================================
# Hierarchical weights for the 4-level aggregation structure

# Macro Cluster Weights (PHASE_7)
MACRO_CLUSTER_SOCIAL_WEIGHT = 0.30
MACRO_CLUSTER_ECONOMIC_WEIGHT = 0.25
MACRO_CLUSTER_ENVIRONMENTAL_WEIGHT = 0.25
MACRO_CLUSTER_INSTITUTIONAL_WEIGHT = 0.20

MACRO_CLUSTER_WEIGHTS = {
    "SOCIAL": MACRO_CLUSTER_SOCIAL_WEIGHT,
    "ECONOMIC": MACRO_CLUSTER_ECONOMIC_WEIGHT,
    "ENVIRONMENTAL": MACRO_CLUSTER_ENVIRONMENTAL_WEIGHT,
    "INSTITUTIONAL": MACRO_CLUSTER_INSTITUTIONAL_WEIGHT,
}

# Area Weights (PHASE_6) - Default uniform distribution
# Can be overridden per-cluster
DEFAULT_AREA_WEIGHT = 1.0  # Will be normalized to 1/n

# Dimension Weights (PHASE_5) - Default uniform distribution
# Can be overridden per-area
DEFAULT_DIMENSION_WEIGHT = 1.0  # Will be normalized to 1/n

# =============================================================================
# SCORING MODALITIES
# =============================================================================
# Score ranges and transformations

# Primary score range
MIN_SCORE = 0.0
MAX_SCORE = 3.0
SCORE_RANGE = (MIN_SCORE, MAX_SCORE)

# Normalized score range (for compatibility with some algorithms)
MIN_NORMALIZED_SCORE = 0.0
MAX_NORMALIZED_SCORE = 1.0

# Score transformation modes
SCORE_MODE_RAW = "raw"  # Keep original [0, 3] range
SCORE_MODE_NORMALIZED = "normalized"  # Transform to [0, 1]
SCORE_MODE_PERCENT = "percent"  # Transform to [0, 100]

# =============================================================================
# DISPERSION THRESHOLDS
# =============================================================================
# Thresholds for coherence and dispersion analysis

# Coefficient of Variation (CV) thresholds
CV_CONVERGENCE_THRESHOLD = 0.15  # Low dispersion = convergence
CV_MODERATE_THRESHOLD = 0.40  # Moderate dispersion
CV_HIGH_THRESHOLD = 0.60  # High dispersion
# Above 0.60 = extreme dispersion

# Dispersion scenarios
DISPERSION_SCENARIO_CONVERGENCE = "convergence"
DISPERSION_SCENARIO_MODERATE = "moderate"
DISPERSION_SCENARIO_HIGH = "high_dispersion"
DISPERSION_SCENARIO_EXTREME = "extreme_dispersion"

# Coherence thresholds
COHERENCE_EXCELLENT = 0.90
COHERENCE_GOOD = 0.75
COHERENCE_ACCEPTABLE = 0.60
COHERENCE_POOR = 0.45

# Penalty weights for dispersion
PENALTY_WEIGHT_BASE = 0.3
PENALTY_MULTIPLIER_CONVERGENCE = 0.5
PENALTY_MULTIPLIER_MODERATE = 1.0
PENALTY_MULTIPLIER_HIGH = 1.5
PENALTY_MULTIPLIER_EXTREME = 2.0

# =============================================================================
# UNCERTAINTY QUANTIFICATION
# =============================================================================
# Bootstrap and uncertainty analysis constants

# Bootstrap settings
BOOTSTRAP_DEFAULT_ITERATIONS = 2000
BOOTSTRAP_MIN_ITERATIONS = 1000
BOOTSTRAP_MAX_ITERATIONS = 10000

# Confidence intervals
CONFIDENCE_LEVEL_95 = 0.95
CONFIDENCE_LEVEL_99 = 0.99
CONFIDENCE_LEVEL_DEFAULT = CONFIDENCE_LEVEL_95

# Convergence diagnostics
CONVERGENCE_MIN_SAMPLES = 1000
CONVERGENCE_MIN_ESS = 400  # Effective Sample Size
CONVERGENCE_MAX_GEWEKE_Z = 2.0
CONVERGENCE_MIN_P_VALUE = 0.01
CONVERGENCE_MAX_KS_STATISTIC = 0.05
CONVERGENCE_MAX_BIMODALITY = 2.0

# =============================================================================
# CONSTITUTIONAL BOUNDS
# =============================================================================
# Permissible ranges for aggregation components (Shapley values)

# Default bounds: ±20% of nominal weight
CONSTITUTIONAL_DEFAULT_VARIANCE = 0.20

# Bounds for each cluster
CONSTITUTIONAL_BOUNDS = {
    "SOCIAL": (0.24, 0.36),  # 0.30 ± 20%
    "ECONOMIC": (0.20, 0.30),  # 0.25 ± 20%
    "ENVIRONMENTAL": (0.20, 0.30),  # 0.25 ± 20%
    "INSTITUTIONAL": (0.16, 0.24),  # 0.20 ± 20%
}

# =============================================================================
# SIGNAL-ENRICHED AGGREGATION
# =============================================================================
# Constants for signal-based weight adjustments

# Critical score threshold for weight boosting
CRITICAL_SCORE_THRESHOLD = 0.4
CRITICAL_SCORE_BOOST_FACTOR = 1.2

# High signal pattern threshold
HIGH_SIGNAL_PATTERN_THRESHOLD = 15
HIGH_SIGNAL_BOOST_FACTOR = 1.05

# =============================================================================
# CHOQUET INTEGRAL
# =============================================================================
# Constants for Choquet aggregation

# k-additivity orders
CHOQUET_K_ADDITIVE_1 = 1  # Pure additive
CHOQUET_K_ADDITIVE_2 = 2  # Pairwise interactions
CHOQUET_K_ADDITIVE_3 = 3  # Three-way interactions
CHOQUET_K_ADDITIVE_DEFAULT = CHOQUET_K_ADDITIVE_2

# Interaction strength
CHOQUET_INTERACTION_NONE = 0.0  # Pure additive
CHOQUET_INTERACTION_CONSERVATIVE = 0.1  # Minimal interactions
CHOQUET_INTERACTION_MODERATE = 0.3  # Moderate interactions
CHOQUET_INTERACTION_STRONG = 0.5  # Strong interactions

# =============================================================================
# METADATA KEYS
# =============================================================================
# Standardized keys for provenance tracking and metadata

# Metadata key prefixes
META_PREFIX_AGGREGATION = "aggregation"
META_PREFIX_VALIDATION = "validation"
META_PREFIX_UNCERTAINTY = "uncertainty"
META_PREFIX_PROVENANCE = "provenance"
META_PREFIX_SIGNAL = "signal"

# Aggregation metadata keys
META_AGGREGATION_METHOD = f"{META_PREFIX_AGGREGATION}.method"
META_AGGREGATION_WEIGHTS = f"{META_PREFIX_AGGREGATION}.weights"
META_AGGREGATION_SCORES = f"{META_PREFIX_AGGREGATION}.scores"
META_AGGREGATION_DISPERSION = f"{META_PREFIX_AGGREGATION}.dispersion"
META_AGGREGATION_COHERENCE = f"{META_PREFIX_AGGREGATION}.coherence"

# Validation metadata keys
META_VALIDATION_HERMETICITY = f"{META_PREFIX_VALIDATION}.hermeticity"
META_VALIDATION_TRACEABILITY = f"{META_PREFIX_VALIDATION}.traceability"
META_VALIDATION_CONSTITUTIONAL = f"{META_PREFIX_VALIDATION}.constitutional"

# Uncertainty metadata keys
META_UNCERTAINTY_CI_LOWER = f"{META_PREFIX_UNCERTAINTY}.ci_lower"
META_UNCERTAINTY_CI_UPPER = f"{META_PREFIX_UNCERTAINTY}.ci_upper"
META_UNCERTAINTY_STD_ERROR = f"{META_PREFIX_UNCERTAINTY}.std_error"
META_UNCERTAINTY_METHOD = f"{META_PREFIX_UNCERTAINTY}.method"

# Provenance metadata keys
META_PROVENANCE_NODE_ID = f"{META_PREFIX_PROVENANCE}.node_id"
META_PROVENANCE_PARENT_ID = f"{META_PREFIX_PROVENANCE}.parent_id"
META_PROVENANCE_TIMESTAMP = f"{META_PREFIX_PROVENANCE}.timestamp"
META_PROVENANCE_SOURCE_PHASE = f"{META_PREFIX_PROVENANCE}.source_phase"

# =============================================================================
# POLICY AREA x DIMENSION MATRIX
# =============================================================================
# Expected PA×DIM coverage: 10 areas × 6 dimensions = 60 cells

# Policy Areas (10)
POLICY_AREAS = [
    "SOCIAL_PROTECTION",
    "ECONOMIC_DEVELOPMENT",
    "ENVIRONMENTAL sustainability",
    "GOVERNANCE",
    "HEALTH",
    "EDUCATION",
    "INFRASTRUCTURE",
    "LABOR",
    "HOUSING",
    "JUSTICE",
]

# Dimensions (6)
DIMENSIONS = [
    "DIM01",  # Placeholder for actual dimension names
    "DIM02",
    "DIM03",
    "DIM04",
    "DIM05",
    "DIM06",
]

# Expected PA×DIM coverage
EXPECTED_PA_DIM_CELLS = len(POLICY_AREAS) * len(DIMENSIONS)  # 60

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================
# Constants for hard validation enforcement

# Enable/disable strict validation
VALIDATION_STRICT_MODE = True

# Validation error messages
VALIDATION_ERROR_EMPTY_OUTPUT = "EMPTY_OUTPUT"
VALIDATION_ERROR_NOT_TRACEABLE = "NOT_TRACEABLE"
VALIDATION_ERROR_INVALID_SCORE = "INVALID_SCORE"
VALIDATION_ERROR_ZERO_MACRO = "ZERO_MACRO"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_quality_level(score: float) -> str:
    """
    Determine quality level from macro score.

    Args:
        score: Macro score in [0, 3] range

    Returns:
        Quality level string (EXCELENTE, BUENO, ACEPTABLE, INSUFICIENTE)
    """
    if score >= QUALITY_THRESHOLD_EXCELENTE_MIN:
        return QUALITY_LEVEL_EXCELENTE
    elif score >= QUALITY_THRESHOLD_BUENO_MIN:
        return QUALITY_LEVEL_BUENO
    elif score >= QUALITY_THRESHOLD_ACEPTABLE_MIN:
        return QUALITY_LEVEL_ACEPTABLE
    else:
        return QUALITY_LEVEL_INSUFICIENTE


def get_dispersion_scenario(cv: float) -> str:
    """
    Determine dispersion scenario from coefficient of variation.

    Args:
        cv: Coefficient of variation

    Returns:
        Dispersion scenario string
    """
    if cv < CV_CONVERGENCE_THRESHOLD:
        return DISPERSION_SCENARIO_CONVERGENCE
    elif cv < CV_MODERATE_THRESHOLD:
        return DISPERSION_SCENARIO_MODERATE
    elif cv < CV_HIGH_THRESHOLD:
        return DISPERSION_SCENARIO_HIGH
    else:
        return DISPERSION_SCENARIO_EXTREME


def get_adaptive_penalty(cv: float) -> float:
    """
    Calculate adaptive penalty based on dispersion.

    Args:
        cv: Coefficient of variation

    Returns:
        Adaptive penalty multiplier
    """
    scenario = get_dispersion_scenario(cv)
    if scenario == DISPERSION_SCENARIO_CONVERGENCE:
        return PENALTY_WEIGHT_BASE * PENALTY_MULTIPLIER_CONVERGENCE
    elif scenario == DISPERSION_SCENARIO_MODERATE:
        return PENALTY_WEIGHT_BASE * PENALTY_MULTIPLIER_MODERATE
    elif scenario == DISPERSION_SCENARIO_HIGH:
        return PENALTY_WEIGHT_BASE * PENALTY_MULTIPLIER_HIGH
    else:
        return PENALTY_WEIGHT_BASE * PENALTY_MULTIPLIER_EXTREME


def normalize_score(score: float) -> float:
    """
    Normalize score from [0, 3] to [0, 1].

    Args:
        score: Raw score in [0, 3]

    Returns:
        Normalized score in [0, 1]
    """
    return score / MAX_SCORE


def denormalize_score(normalized_score: float) -> float:
    """
    Denormalize score from [0, 1] to [0, 3].

    Args:
        normalized_score: Normalized score in [0, 1]

    Returns:
        Raw score in [0, 3]
    """
    return normalized_score * MAX_SCORE


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Phase identification
    "PHASE_ID",
    "PHASE_NAME",
    "PHASE_VERSION",
    "PHASE_4_ID",
    "PHASE_5_ID",
    "PHASE_6_ID",
    "PHASE_7_ID",
    # Quality levels
    "QUALITY_LEVEL_EXCELENTE",
    "QUALITY_LEVEL_BUENO",
    "QUALITY_LEVEL_ACEPTABLE",
    "QUALITY_LEVEL_INSUFICIENTE",
    "QUALITY_THRESHOLD_EXCELENTE_MIN",
    "QUALITY_THRESHOLD_BUENO_MIN",
    "QUALITY_THRESHOLD_ACEPTABLE_MIN",
    # Aggregation weights
    "MACRO_CLUSTER_WEIGHTS",
    "DEFAULT_AREA_WEIGHT",
    "DEFAULT_DIMENSION_WEIGHT",
    # Scoring modalities
    "MIN_SCORE",
    "MAX_SCORE",
    "SCORE_RANGE",
    # Dispersion thresholds
    "CV_CONVERGENCE_THRESHOLD",
    "CV_MODERATE_THRESHOLD",
    "CV_HIGH_THRESHOLD",
    "COHERENCE_EXCELLENT",
    "COHERENCE_GOOD",
    "COHERENCE_ACCEPTABLE",
    "COHERENCE_POOR",
    "Uncertainty quantification" "BOOTSTRAP_DEFAULT_ITERATIONS",
    "CONFIDENCE_LEVEL_DEFAULT",
    # Constitutional bounds
    "CONSTITUTIONAL_BOUNDS",
    # PA×DIM matrix
    "POLICY_AREAS",
    "DIMENSIONS",
    "EXPECTED_PA_DIM_CELLS",
    # Utility functions
    "get_quality_level",
    "get_dispersion_scenario",
    "get_adaptive_penalty",
    "normalize_score",
    "denormalize_score",
]
