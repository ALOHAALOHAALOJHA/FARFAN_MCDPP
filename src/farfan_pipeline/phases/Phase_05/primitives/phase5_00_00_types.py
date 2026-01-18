"""
Phase 5 Core Types - Primitives Layer

This module defines core types and data structures for Phase 5.
Extends AreaScore with advanced synthesis, statistical, and comparative metrics.

Module: src/farfan_pipeline/phases/Phase_05/primitives/phase5_00_00_types.py
Layer: primitives
Dependencies: Phase 4 types only
"""
from __future__ import annotations

__version__ = "2.0.0"
__phase__ = 5
__stage__ = 0
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__layer__ = "primitives"
__dependencies__ = ["farfan_pipeline.phases.Phase_04.primitives.phase4_00_00_types"]

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, TypeAlias, runtime_checkable

# Type aliases
AreaID: TypeAlias = str  # e.g., "PA01", "PA02", ..., "PA10"
ClusterID: TypeAlias = str  # e.g., "CLUSTER_MESO_1", ...
Score: TypeAlias = float  # Range [0.0, 3.0]
QualityLevel: TypeAlias = str  # "EXCELENTE" | "BUENO" | "ACEPTABLE" | "INSUFICIENTE"


class AggregationStrategy(Enum):
    """Aggregation strategies for area scores."""

    WEIGHTED_AVERAGE = "weighted_average"
    ROBUST_MEAN = "robust_mean"  # Trimmed mean, resistant to outliers
    CHOQUET_INTEGRAL = "choquet_integral"  # Considers dimension interactions
    GEOMETRIC_MEAN = "geometric_mean"  # For multiplicative effects
    HARMONIC_MEAN = "harmonic_mean"  # For rate-like dimensions


class ValidationLevel(Enum):
    """Validation strictness levels."""

    STRICT = "strict"  # Fail on any violation
    MODERATE = "moderate"  # Fail on critical violations only
    PERMISSIVE = "permissive"  # Log warnings but don't fail


class SynthesisDepth(Enum):
    """Depth of synthesis analysis."""

    MINIMAL = "minimal"  # Basic aggregation only
    STANDARD = "standard"  # Include statistical metrics
    COMPREHENSIVE = "comprehensive"  # Full cross-cutting analysis
    FRONTIER = "frontier"  # All advanced features enabled


@runtime_checkable
class IAreaAggregator(Protocol):
    """Protocol for area aggregation implementations."""

    def aggregate(
        self,
        dimension_scores: list[Any],
        weights: dict[str, float] | None = None,
    ) -> Any:
        """Aggregate dimension scores into an area score."""
        ...

    def validate_inputs(
        self,
        dimension_scores: list[Any],
    ) -> tuple[bool, str]:
        """Validate input dimension scores."""
        ...


@runtime_checkable
class IStatisticalAnalyzer(Protocol):
    """Protocol for statistical analysis implementations."""

    def analyze(
        self,
        area_scores: list[Any],
    ) -> dict[str, Any]:
        """Perform statistical analysis on area scores."""
        ...

    def detect_anomalies(
        self,
        area_scores: list[Any],
    ) -> list[str]:
        """Detect anomalous area scores."""
        ...


@runtime_checkable
class ISynthesisEngine(Protocol):
    """Protocol for synthesis engine implementations."""

    def synthesize(
        self,
        area_scores: list[Any],
        dimension_scores: list[Any],
    ) -> dict[str, Any]:
        """Synthesize cross-cutting insights from area and dimension scores."""
        ...


@dataclass
class DimensionContribution:
    """
    Contribution of a dimension to an area score.

    Attributes:
        dimension_id: Dimension identifier
        weight: Normalized weight [0.0, 1.0]
        raw_score: Raw dimension score [0.0, 3.0]
        weighted_contribution: Weight × raw_score
        relative_importance: Contribution / area_score (0.0 = no impact, 1.0 = full area score)
        sensitivity: ∂(area_score)/∂(dimension_score) - how much area changes per dimension change
    """

    dimension_id: str
    weight: float
    raw_score: float
    weighted_contribution: float
    relative_importance: float = 0.0
    sensitivity: float = 0.0


@dataclass
class StatisticalMetrics:
    """
    Statistical metrics for area scores.

    Attributes:
        mean: Mean score across dimensions
        median: Median score
        std_dev: Standard deviation
        variance: Variance
        min_score: Minimum dimension score
        max_score: Maximum dimension score
        range: max - min
        coefficient_of_variation: std_dev / mean (normalized dispersion)
        skewness: Distribution asymmetry
        kurtosis: Distribution tail heaviness
        percentile_25: 25th percentile
        percentile_75: 75th percentile
        iqr: Interquartile range (P75 - P25)
    """

    mean: float = 0.0
    median: float = 0.0
    std_dev: float = 0.0
    variance: float = 0.0
    min_score: float = 0.0
    max_score: float = 0.0
    range: float = 0.0
    coefficient_of_variation: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0
    percentile_25: float = 0.0
    percentile_75: float = 0.0
    iqr: float = 0.0


@dataclass
class ComparativeMetrics:
    """
    Comparative metrics relative to other areas.

    Attributes:
        rank: Rank among all areas (1 = best)
        percentile: Percentile rank (0-100)
        deviation_from_mean: score - global_mean
        z_score: (score - global_mean) / global_std
        better_than_count: Number of areas this area outperforms
        worse_than_count: Number of areas this area underperforms
        cluster_rank: Rank within assigned cluster
        cluster_percentile: Percentile within cluster
    """

    rank: int = 0
    percentile: float = 0.0
    deviation_from_mean: float = 0.0
    z_score: float = 0.0
    better_than_count: int = 0
    worse_than_count: int = 0
    cluster_rank: int = 0
    cluster_percentile: float = 0.0


@dataclass
class CrossCuttingInsights:
    """
    Cross-cutting insights spanning multiple dimensions/areas.

    Attributes:
        strength_areas: Policy areas above excellence threshold
        weakness_areas: Policy areas below acceptable threshold
        improvement_opportunities: Areas with highest potential for improvement
        risk_factors: Areas with high variance or declining trends
        synergies: Dimension pairs with strong positive correlation
        conflicts: Dimension pairs with strong negative correlation
        outlier_dimensions: Dimensions significantly deviating from expected
        consistency_score: Overall consistency across dimensions [0.0, 1.0]
    """

    strength_areas: list[str] = field(default_factory=list)
    weakness_areas: list[str] = field(default_factory=list)
    improvement_opportunities: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    synergies: list[tuple[str, str, float]] = field(default_factory=list)
    conflicts: list[tuple[str, str, float]] = field(default_factory=list)
    outlier_dimensions: list[str] = field(default_factory=list)
    consistency_score: float = 1.0


@dataclass
class SensitivityAnalysis:
    """
    Sensitivity analysis for area scores.

    Attributes:
        dimension_sensitivities: Map of dimension_id → sensitivity coefficient
        most_influential_dimension: Dimension with highest impact
        least_influential_dimension: Dimension with lowest impact
        weight_robustness: How robust the score is to weight changes [0.0, 1.0]
        perturbation_stability: Score stability under small perturbations [0.0, 1.0]
    """

    dimension_sensitivities: dict[str, float] = field(default_factory=dict)
    most_influential_dimension: str = ""
    least_influential_dimension: str = ""
    weight_robustness: float = 1.0
    perturbation_stability: float = 1.0


@dataclass
class AreaScoreExtended:
    """
    Extended AreaScore with frontier-grade analytics.

    Extends the base AreaScore with:
    - Dimension-level contribution analysis
    - Statistical metrics
    - Comparative metrics (vs other areas)
    - Cross-cutting insights
    - Sensitivity analysis
    - Aggregation metadata

    This is the SOTA version of AreaScore used throughout Phase 5.
    """

    # Core attributes (from base AreaScore)
    area_id: str
    area_name: str
    score: float
    quality_level: str
    dimension_scores: list[Any] = field(default_factory=list)
    cluster_id: str | None = None

    # Validation
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)

    # Basic uncertainty
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))

    # Provenance
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"

    # SOTA Extensions: Dimension contributions
    dimension_contributions: list[DimensionContribution] = field(default_factory=list)

    # SOTA Extensions: Statistical metrics
    statistical_metrics: StatisticalMetrics = field(default_factory=StatisticalMetrics)

    # SOTA Extensions: Comparative metrics
    comparative_metrics: ComparativeMetrics = field(default_factory=ComparativeMetrics)

    # SOTA Extensions: Cross-cutting insights
    cross_cutting_insights: CrossCuttingInsights = field(default_factory=CrossCuttingInsights)

    # SOTA Extensions: Sensitivity analysis
    sensitivity_analysis: SensitivityAnalysis = field(default_factory=SensitivityAnalysis)

    # SOTA Extensions: Aggregation metadata
    aggregation_strategy: AggregationStrategy = AggregationStrategy.WEIGHTED_AVERAGE
    synthesis_depth: SynthesisDepth = SynthesisDepth.STANDARD
    computation_timestamp: str = ""


@dataclass
class Phase5SynthesisResult:
    """
    Complete synthesis result for Phase 5.

    Contains:
    - All 10 area scores with extended analytics
    - Global statistical summary
    - Cross-area comparative analysis
    - Policy recommendations
    - Quality assessment

    This is the primary output of Phase 5, consumed by Phase 6.
    """

    area_scores: list[AreaScoreExtended] = field(default_factory=list)

    # Global statistics
    global_mean: float = 0.0
    global_median: float = 0.0
    global_std: float = 0.0
    global_min: float = 0.0
    global_max: float = 0.0

    # Quality distribution
    quality_distribution: dict[str, int] = field(default_factory=dict)

    # Cluster statistics
    cluster_statistics: dict[str, dict[str, float]] = field(default_factory=dict)

    # Cross-area insights
    top_performing_areas: list[str] = field(default_factory=list)
    underperforming_areas: list[str] = field(default_factory=list)
    most_consistent_area: str = ""
    least_consistent_area: str = ""

    # Dimension-level insights
    best_performing_dimensions: list[str] = field(default_factory=list)
    worst_performing_dimensions: list[str] = field(default_factory=list)

    # Validation summary
    all_validations_passed: bool = True
    validation_summary: dict[str, Any] = field(default_factory=dict)

    # Provenance
    synthesis_timestamp: str = ""
    synthesis_version: str = "2.0.0"
    synthesis_depth: SynthesisDepth = SynthesisDepth.STANDARD


# Constants
MIN_SCORE = 0.0
MAX_SCORE = 3.0
MIN_WEIGHT = 0.0
MAX_WEIGHT = 1.0
WEIGHT_SUM_TOLERANCE = 1e-6

# Validation functions
def is_valid_score(score: float) -> bool:
    """Check if score is in valid range [0.0, 3.0]."""
    return MIN_SCORE <= score <= MAX_SCORE


def is_valid_weight(weight: float) -> bool:
    """Check if weight is in valid range [0.0, 1.0]."""
    return MIN_WEIGHT <= weight <= MAX_WEIGHT


def are_weights_normalized(weights: list[float]) -> bool:
    """Check if weights sum to 1.0 (within tolerance)."""
    if not weights:
        return False
    weight_sum = sum(weights)
    return abs(weight_sum - 1.0) < WEIGHT_SUM_TOLERANCE


__all__ = [
    # Type aliases
    "AreaID",
    "ClusterID",
    "Score",
    "QualityLevel",
    # Enums
    "AggregationStrategy",
    "ValidationLevel",
    "SynthesisDepth",
    # Protocols
    "IAreaAggregator",
    "IStatisticalAnalyzer",
    "ISynthesisEngine",
    # Data structures
    "DimensionContribution",
    "StatisticalMetrics",
    "ComparativeMetrics",
    "CrossCuttingInsights",
    "SensitivityAnalysis",
    "AreaScoreExtended",
    "Phase5SynthesisResult",
    # Constants
    "MIN_SCORE",
    "MAX_SCORE",
    "MIN_WEIGHT",
    "MAX_WEIGHT",
    "WEIGHT_SUM_TOLERANCE",
    # Validation functions
    "is_valid_score",
    "is_valid_weight",
    "are_weights_normalized",
]
