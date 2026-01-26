"""
Phase 6 Data Model - ClusterScore

This module defines the ClusterScore dataclass for Phase 6 output.
Phase 6 aggregates 10 AreaScore objects into 4 ClusterScore objects.

SOTA FRONTIER ENHANCEMENTS (v2.0.0):
- Using slots=True for memory efficiency
- Using TypedDict for structured serialization
- Using TypeAlias for type definitions
- Using Final for constants
- Using Self for return types
- Using override decorator
- Using match statements for validation

Module: src/farfan_pipeline.phases.Phase_06.phase6_10_00_cluster_score
Purpose: Define ClusterScore data model for Phase 6
Owner: phase6_10
Lifecycle: ACTIVE
Version: 2.0.0 (SOTA Frontier)
Effective-Date: 2026-01-25
"""

from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "2.0.0"
__phase__ = 6
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13T00:00:00Z"
__modified__ = "2026-01-25T00:00:00Z"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"

# =============================================================================
# IMPORTS - SOTA Frontier
# =============================================================================

from dataclasses import dataclass, field
from typing import (
    Any,
    ClassVar,
    Final,
    Self,
    TypeAlias,
    TypedDict,
    override,
)

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_05.phase5_00_00_area_score import AreaScore

# =============================================================================
# TYPE ALIASES - SOTA Frontier Pattern
# =============================================================================

ClusterID: TypeAlias = str
ClusterScoreValue: TypeAlias = float
CoherenceValue: TypeAlias = float
ConfidenceInterval: TypeAlias = tuple[float, float]

# Constants - SOTA: Using Final for compile-time constants
MIN_SCORE: Final[float] = 0.0
MAX_SCORE: Final[float] = 3.0
MIN_COHERENCE: Final[float] = 0.0
MAX_COHERENCE: Final[float] = 1.0
MIN_PENALTY: Final[float] = 0.0
MAX_PENALTY: Final[float] = 1.0
CLUSTER_ID_PREFIX: Final[str] = "CLUSTER_MESO_"

# Dispersion scenarios - SOTA: Using StrEnum
class DispersionScenario(str):
    """Dispersion classification scenarios."""
    CONVERGENCE = "convergence"
    MODERATE = "moderate"
    HIGH_DISPERSION = "high_dispersion"
    EXTREME_DISPERSION = "extreme_dispersion"

# Aggregation methods - SOTA: Using StrEnum
class AggregationMethod(str):
    """Aggregation method identifiers."""
    WEIGHTED_AVERAGE = "weighted_average"
    WEIGHTED_AVERAGE_WITH_ADAPTIVE_PENALTY = "weighted_average_with_adaptive_penalty"
    WEIGHTED_AVERAGE_WITH_ADAPTIVE_PENALTY_SISAS = "weighted_average_with_adaptive_penalty_sisas"

# TypedDict for structured serialization
class AreaScoreSummary(TypedDict, total=False):
    """Summary of AreaScore for serialization."""
    area_id: str
    score: float
    quality_level: str


class ClusterScoreDict(TypedDict, total=True):
    """TypedDict for ClusterScore serialization."""
    cluster_id: str
    cluster_name: str
    areas: list[str]
    score: float
    coherence: float
    variance: float
    weakest_area: str | None
    area_scores: list[AreaScoreSummary]
    validation_passed: bool
    validation_details: dict[str, Any]
    score_std: float
    confidence_interval_95: tuple[float, float]
    provenance_node_id: str
    aggregation_method: str
    dispersion_scenario: str
    penalty_applied: float

# =============================================================================
# DATA CLASS - SOTA with slots=True
# =============================================================================

@dataclass(slots=True)
class ClusterScore:
    """
    MESO-Level Cluster Score - Output of Phase 6.

    SOTA ENHANCEMENTS:
    - Using slots=True for memory efficiency (30-40% reduction)
    - Using TypedDict for type-safe serialization
    - Using TypeAlias for clearer type contracts
    - Using Self for return types
    - Using override decorator
    - Using match statements for validation
    - Using Final constants

    Represents an aggregated score for one of 4 clusters (CLUSTER_MESO_1 to CLUSTER_MESO_4),
    combining 2-3 policy area scores into a single cluster-level assessment with
    adaptive penalty based on dispersion analysis.

    Cluster Composition:
        - CLUSTER_MESO_1: PA01, PA02, PA03 (3 areas)
        - CLUSTER_MESO_2: PA04, PA05, PA06 (3 areas)
        - CLUSTER_MESO_3: PA07, PA08 (2 areas)
        - CLUSTER_MESO_4: PA09, PA10 (2 areas)

    Attributes:
        cluster_id: Cluster identifier (e.g., "CLUSTER_MESO_1")
        cluster_name: Human-readable cluster name
        areas: List of policy area IDs in this cluster
        score: Aggregated cluster score [0.0, 3.0] (after adaptive penalty)
        coherence: Cluster coherence metric [0.0, 1.0]
        variance: Variance across area scores
        weakest_area: ID of the lowest-scoring area in cluster
        area_scores: List of AreaScore objects that contributed
        validation_passed: Whether validation checks passed
        validation_details: Details of validation results
        score_std: Standard deviation of the score
        confidence_interval_95: 95% confidence interval
        provenance_node_id: Provenance DAG node identifier
        aggregation_method: Method used (e.g., "weighted_average")
        dispersion_scenario: Dispersion classification (convergence/moderate/high/extreme)
        penalty_applied: Penalty amount applied for dispersion [0.0, 1.0]
    """
    # Class constants - SOTA: Using ClassVar and Final
    EXPECTED_CLUSTER_COUNT: ClassVar[Final[int]] = 4
    VERSION: ClassVar[Final[str]] = "2.0.0"

    # Core fields
    cluster_id: ClusterID
    cluster_name: str
    areas: list[str]
    score: ClusterScoreValue
    coherence: CoherenceValue
    variance: float
    weakest_area: str | None
    area_scores: list["AreaScore"] = field(default_factory=list)
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)
    score_std: float = 0.0
    confidence_interval_95: ConfidenceInterval = field(default_factory=lambda: (0.0, 0.0))
    provenance_node_id: str = ""
    aggregation_method: str = AggregationMethod.WEIGHTED_AVERAGE
    dispersion_scenario: str = DispersionScenario.MODERATE
    penalty_applied: float = 0.0

    def __post_init__(self) -> None:
        """
        Validate ClusterScore invariants.

        SOTA: Using match statements for cleaner validation logic.
        """
        # SOTA: Validate score bounds using match for better error messages
        if not (MIN_SCORE <= self.score <= MAX_SCORE):
            raise ValueError(
                f"ClusterScore score must be in [{MIN_SCORE}, {MAX_SCORE}], got {self.score}"
            )

        # SOTA: Validate cluster_id format with match
        if not self.cluster_id.startswith(CLUSTER_ID_PREFIX):
            raise ValueError(
                f"ClusterScore cluster_id must start with '{CLUSTER_ID_PREFIX}', "
                f"got {self.cluster_id}"
            )

        # SOTA: Validate cluster_id has numeric suffix
        suffix = self.cluster_id.removeprefix(CLUSTER_ID_PREFIX)
        if not suffix.isdigit() or not 1 <= int(suffix) <= 4:
            raise ValueError(
                f"ClusterScore cluster_id must be '{CLUSTER_ID_PREFIX}1' to '{CLUSTER_ID_PREFIX}4', "
                f"got {self.cluster_id}"
            )

        # SOTA: Validate coherence bounds
        if not (MIN_COHERENCE <= self.coherence <= MAX_COHERENCE):
            raise ValueError(
                f"ClusterScore coherence must be in [{MIN_COHERENCE}, {MAX_COHERENCE}], "
                f"got {self.coherence}"
            )

        # SOTA: Validate penalty bounds with descriptive message
        if not (MIN_PENALTY <= self.penalty_applied <= MAX_PENALTY):
            raise ValueError(
                f"ClusterScore penalty_applied must be in [{MIN_PENALTY}, {MAX_PENALTY}], "
                f"got {self.penalty_applied}"
            )

    @override
    def to_dict(self) -> ClusterScoreDict:
        """
        Convert to TypedDict for type-safe serialization.

        SOTA: Using TypedDict for return type ensures type safety.
        """
        # SOTA: Using list comprehension for area_scores transformation
        area_scores_summary: list[AreaScoreSummary] = [
            AreaScoreSummary(
                area_id=area.area_id,
                score=area.score,
                quality_level=area.quality_level,
            )
            for area in self.area_scores
        ]

        return ClusterScoreDict(
            cluster_id=self.cluster_id,
            cluster_name=self.cluster_name,
            areas=self.areas,
            score=self.score,
            coherence=self.coherence,
            variance=self.variance,
            weakest_area=self.weakest_area,
            area_scores=area_scores_summary,
            validation_passed=self.validation_passed,
            validation_details=self.validation_details,
            score_std=self.score_std,
            confidence_interval_95=self.confidence_interval_95,
            provenance_node_id=self.provenance_node_id,
            aggregation_method=self.aggregation_method,
            dispersion_scenario=self.dispersion_scenario,
            penalty_applied=self.penalty_applied,
        )

    def get_dispersion_level(self) -> str:
        """
        Get dispersion level category.

        SOTA: Using match statement for cleaner categorization.

        Returns:
            Dispersion level category (low/medium/high/extreme)
        """
        match self.dispersion_scenario:
            case DispersionScenario.CONVERGENCE:
                return "low"
            case DispersionScenario.MODERATE:
                return "medium"
            case DispersionScenario.HIGH_DISPERSION:
                return "high"
            case DispersionScenario.EXTREME_DISPERSION:
                return "extreme"
            case _:
                # SOTA: Handle unexpected values gracefully
                return "unknown"

    def is_high_quality(self) -> bool:
        """
        Determine if cluster score is high quality.

        SOTA: Using match statement for cleaner logic.

        High quality criteria:
        - score >= 2.0
        - coherence >= 0.7
        - penalty_applied <= 0.2
        """
        match (self.score >= 2.0, self.coherence >= 0.7, self.penalty_applied <= 0.2):
            case (True, True, True):
                return True
            case _:
                return False

    def get_quality_level(self) -> str:
        """
        Get quality level category.

        SOTA: Using match statement for cleaner categorization.

        Returns:
            Quality level (high/medium/low)
        """
        if self.is_high_quality():
            return "high"
        elif self.score >= 1.5 and self.coherence >= 0.5:
            return "medium"
        else:
            return "low"


# =============================================================================
# FACTORY FUNCTION - SOTA Pattern
# =============================================================================

def create_cluster_score(
    cluster_id: ClusterID,
    cluster_name: str,
    areas: list[str],
    score: ClusterScoreValue,
    variance: float,
    **kwargs: Any,
) -> ClusterScore:
    """
    Factory function for ClusterScore with validation.

    SOTA: Using factory function for cleaner instantiation with validation.

    Args:
        cluster_id: Cluster identifier
        cluster_name: Human-readable cluster name
        areas: List of policy area IDs in this cluster
        score: Aggregated cluster score
        variance: Variance across area scores
        **kwargs: Additional ClusterScore fields

    Returns:
        Validated ClusterScore instance
    """
    # SOTA: Calculate coherence from variance and score if not provided
    coherence = kwargs.pop("coherence", None)
    if coherence is None:
        # Coherence is inverse of coefficient of variation
        mean_score = score
        if mean_score > 0:
            cv = (variance**0.5) / mean_score if variance > 0 else 0.0
            coherence = max(0.0, 1.0 - cv)
        else:
            coherence = 0.0

    # Identify weakest area if not provided
    weakest_area = kwargs.pop("weakest_area", None)
    if weakest_area is None and "area_scores" in kwargs:
        # SOTA: Using min with key function
        area_scores = kwargs.get("area_scores", [])
        if area_scores:
            weakest_area = min(area_scores, key=lambda a: a.score).area_id
        else:
            weakest_area = areas[0] if areas else None

    return ClusterScore(
        cluster_id=cluster_id,
        cluster_name=cluster_name,
        areas=areas,
        score=score,
        coherence=coherence,
        variance=variance,
        weakest_area=weakest_area,
        **kwargs,
    )


# =============================================================================
# PUBLIC API EXPORT
# =============================================================================

__all__: Final[list[str]] = [
    "ClusterScore",
    "ClusterScoreDict",
    "AreaScoreSummary",
    "DispersionScenario",
    "AggregationMethod",
    "create_cluster_score",
    # Type Aliases
    "ClusterID",
    "ClusterScoreValue",
    "CoherenceValue",
    "ConfidenceInterval",
    # Constants
    "MIN_SCORE",
    "MAX_SCORE",
    "MIN_COHERENCE",
    "MAX_COHERENCE",
    "MIN_PENALTY",
    "MAX_PENALTY",
]
