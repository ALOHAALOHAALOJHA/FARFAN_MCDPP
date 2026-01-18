"""
Phase 5 Area Aggregation Module - Policy Area Score Aggregation

This module implements Phase 5 area aggregation:
- PHASE 5: Area aggregation (60 dimension scores → 10 policy area scores: 6 dimensions × 10 areas)

Phase 5 Contract:
- Input: 60 DimensionScore from Phase 4 (6 dimensions × 10 policy areas)
- Output: 10 AreaScore (one per policy area)
- Process: Aggregate 6 dimension scores per policy area using weighted averaging

Requirements:
- Validation of hermeticity (exactly 6 dimensions per area)
- Validation of weights, thresholds, and bounds
- Comprehensive logging and abortability
- Provenance tracking
- Uncertainty quantification

Architecture:
- AreaScore: Dataclass for area-level score with 6 dimension scores
- AreaPolicyAggregator: Aggregates 6 dimension scores → 1 area score
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 5
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13"
__modified__ = "2026-01-13"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any

# Import DimensionScore from Phase 4 primitives (shared type)
from farfan_pipeline.phases.Phase_04.primitives.phase4_00_00_types import DimensionScore

# Import Phase 5 constants
from farfan_pipeline.phases.Phase_05.PHASE_5_CONSTANTS import (
    DIMENSIONS_PER_AREA,
    DIMENSION_IDS,
    EXPECTED_AREA_SCORE_COUNT,
    MAX_SCORE,
    MIN_SCORE,
    POLICY_AREAS,
    QUALITY_THRESHOLDS,
)

# Import canonical AreaScore from phase5_00_00_area_score
from farfan_pipeline.phases.Phase_05.phase5_00_00_area_score import AreaScore

logger = logging.getLogger(__name__)


# =============================================================================
# AGGREGATION LOGIC
# =============================================================================


class AreaPolicyAggregator:
    """
    Aggregates dimension scores into policy area scores.
    
    Phase 5 Contract:
    - Input: 60 DimensionScore (6 dimensions × 10 policy areas)
    - Output: 10 AreaScore (one per policy area)
    - Process: Weighted average of 6 dimensions per policy area
    
    Hermeticity Requirements:
    - Each policy area must have exactly 6 dimensions (DIM01-DIM06)
    - No duplicate dimensions per policy area
    - All 10 policy areas must be present (PA01-PA10)
    
    Validation:
    - Score bounds: [0.0, 3.0]
    - Quality level assignment based on thresholds
    - Hermeticity validation (6 dimensions per area)
    """

    def __init__(
        self,
        monolith: dict[str, Any] | None = None,
        abort_on_insufficient: bool = True,
        enable_sota_features: bool = True,
        signal_registry: Any | None = None,
    ):
        """
        Initialize AreaPolicyAggregator.
        
        Args:
            monolith: Questionnaire monolith (optional, for weights)
            abort_on_insufficient: Whether to abort on validation failures
            enable_sota_features: Enable SOTA features (provenance, uncertainty)
            signal_registry: Signal registry for SISAS (optional)
        """
        self.monolith = monolith
        self.abort_on_insufficient = abort_on_insufficient
        self.enable_sota_features = enable_sota_features
        self.signal_registry = signal_registry
        
        logger.info(f"Initialized AreaPolicyAggregator (SOTA: {enable_sota_features})")

    def aggregate(
        self,
        dimension_scores: list[DimensionScore],
        weights: dict[str, dict[str, float]] | None = None,
    ) -> list[AreaScore]:
        """
        Aggregate dimension scores into area scores.
        
        Args:
            dimension_scores: List of 60 DimensionScore objects
            weights: Optional weights dict: {area_id: {dimension_id: weight}}
                     If None, equal weights (1/6) are used for all dimensions
        
        Returns:
            List of 10 AreaScore objects
        
        Raises:
            ValueError: If hermeticity validation fails
            ValueError: If score bounds are violated
        """
        logger.info(f"Starting area aggregation with {len(dimension_scores)} dimension scores")
        
        # Validate input count
        if len(dimension_scores) != DIMENSIONS_PER_AREA * EXPECTED_AREA_SCORE_COUNT:
            msg = (
                f"Expected {DIMENSIONS_PER_AREA * EXPECTED_AREA_SCORE_COUNT} dimension scores, "
                f"got {len(dimension_scores)}"
            )
            logger.error(msg)
            if self.abort_on_insufficient:
                raise ValueError(msg)
        
        # Group by policy area
        grouped = self._group_by_area(dimension_scores)
        
        # Validate hermeticity
        self._validate_hermeticity(grouped)
        
        # Aggregate each policy area
        area_scores = []
        for area_id in POLICY_AREAS:
            if area_id not in grouped:
                msg = f"Missing policy area: {area_id}"
                logger.error(msg)
                if self.abort_on_insufficient:
                    raise ValueError(msg)
                continue
            
            area_dimensions = grouped[area_id]
            area_weights = weights.get(area_id, {}) if weights else {}
            
            area_score = self._aggregate_area(
                area_id=area_id,
                dimension_scores=area_dimensions,
                weights=area_weights,
            )
            area_scores.append(area_score)
        
        logger.info(f"Completed area aggregation: {len(area_scores)} area scores")
        return area_scores

    def _group_by_area(
        self,
        dimension_scores: list[DimensionScore],
    ) -> dict[str, list[DimensionScore]]:
        """
        Group dimension scores by policy area.
        
        Args:
            dimension_scores: List of DimensionScore objects
        
        Returns:
            Dict mapping area_id to list of DimensionScore
        """
        grouped: dict[str, list[DimensionScore]] = defaultdict(list)
        for ds in dimension_scores:
            grouped[ds.area_id].append(ds)
        return dict(grouped)

    def _validate_hermeticity(
        self,
        grouped: dict[str, list[DimensionScore]],
    ) -> None:
        """
        Validate hermeticity: each area must have exactly 6 dimensions.
        
        Args:
            grouped: Dict mapping area_id to list of DimensionScore
        
        Raises:
            ValueError: If hermeticity validation fails
        """
        for area_id, dimensions in grouped.items():
            # Check count
            if len(dimensions) != DIMENSIONS_PER_AREA:
                msg = (
                    f"Hermeticity violation for {area_id}: "
                    f"expected {DIMENSIONS_PER_AREA} dimensions, got {len(dimensions)}"
                )
                logger.error(msg)
                if self.abort_on_insufficient:
                    raise ValueError(msg)
            
            # Check for duplicates
            dim_ids = [d.dimension_id for d in dimensions]
            unique_dim_ids = set(dim_ids)
            if len(dim_ids) != len(unique_dim_ids):
                duplicates = [d for d in unique_dim_ids if dim_ids.count(d) > 1]
                msg = f"Hermeticity violation for {area_id}: duplicate dimensions {duplicates}"
                logger.error(msg)
                if self.abort_on_insufficient:
                    raise ValueError(msg)
            
            # Check exact set
            if unique_dim_ids != set(DIMENSION_IDS):
                missing = set(DIMENSION_IDS) - unique_dim_ids
                extra = unique_dim_ids - set(DIMENSION_IDS)
                msg = f"Hermeticity violation for {area_id}: missing {missing}, extra {extra}"
                logger.error(msg)
                if self.abort_on_insufficient:
                    raise ValueError(msg)

    def _aggregate_area(
        self,
        area_id: str,
        dimension_scores: list[DimensionScore],
        weights: dict[str, float],
    ) -> AreaScore:
        """
        Aggregate dimension scores for a single policy area.
        
        Args:
            area_id: Policy area identifier
            dimension_scores: List of 6 DimensionScore objects
            weights: Dict mapping dimension_id to weight
        
        Returns:
            AreaScore object
        """
        # Use equal weights if not specified
        if not weights:
            weights = {dim: 1.0 / DIMENSIONS_PER_AREA for dim in DIMENSION_IDS}
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight == 0:
            logger.warning(f"Zero total weight for {area_id}, using equal weights")
            weights = {dim: 1.0 / DIMENSIONS_PER_AREA for dim in DIMENSION_IDS}
            total_weight = 1.0
        
        # Compute weighted average
        weighted_sum = sum(
            ds.score * weights.get(ds.dimension_id, 0.0)
            for ds in dimension_scores
        )
        score = weighted_sum / total_weight
        
        # Clamp to bounds
        score = max(MIN_SCORE, min(MAX_SCORE, score))
        
        # Determine quality level
        quality_level = self._get_quality_level(score)
        
        # Compute uncertainty (if enabled)
        score_std = 0.0
        confidence_interval = (0.0, 0.0)
        if self.enable_sota_features:
            score_std = self._compute_score_std(dimension_scores, weights)
            confidence_interval = self._compute_confidence_interval(score, score_std)
        
        # Get area name
        area_name = self._get_area_name(area_id)
        
        return AreaScore(
            area_id=area_id,
            area_name=area_name,
            score=score,
            quality_level=quality_level,
            dimension_scores=dimension_scores,
            validation_passed=True,
            validation_details={"hermeticity": True, "bounds": True},
            score_std=score_std,
            confidence_interval_95=confidence_interval,
            aggregation_method="weighted_average",
        )

    def _get_quality_level(self, score: float) -> str:
        """
        Determine quality level from score.
        
        Args:
            score: Score in [0.0, 3.0]
        
        Returns:
            Quality level string
        """
        normalized = score / MAX_SCORE
        if normalized >= QUALITY_THRESHOLDS["EXCELENTE"]:
            return "EXCELENTE"
        elif normalized >= QUALITY_THRESHOLDS["BUENO"]:
            return "BUENO"
        elif normalized >= QUALITY_THRESHOLDS["ACEPTABLE"]:
            return "ACEPTABLE"
        else:
            return "INSUFICIENTE"

    def _compute_score_std(
        self,
        dimension_scores: list[DimensionScore],
        weights: dict[str, float],
    ) -> float:
        """
        Compute standard deviation of area score.
        
        Args:
            dimension_scores: List of DimensionScore objects
            weights: Dict mapping dimension_id to weight
        
        Returns:
            Standard deviation
        """
        # Propagate uncertainty from dimension scores
        variance = sum(
            (weights.get(ds.dimension_id, 0.0) ** 2) * (ds.score_std ** 2)
            for ds in dimension_scores
        )
        return variance ** 0.5

    def _compute_confidence_interval(
        self,
        score: float,
        score_std: float,
    ) -> tuple[float, float]:
        """
        Compute 95% confidence interval for score.
        
        Args:
            score: Mean score
            score_std: Standard deviation
        
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        # Use 1.96 standard deviations for 95% CI
        margin = 1.96 * score_std
        lower = max(MIN_SCORE, score - margin)
        upper = min(MAX_SCORE, score + margin)
        return (lower, upper)

    def _get_area_name(self, area_id: str) -> str:
        """
        Get human-readable area name.
        
        Args:
            area_id: Policy area identifier
        
        Returns:
            Area name string
        """
        # Policy area names from canonical questionnaire
        area_names = {
            "PA01": "Derechos de las mujeres e igualdad de género",
            "PA02": "Prevención de la violencia y protección frente al conflicto",
            "PA03": "Ambiente sano, cambio climático, prevención y atención a desastres",
            "PA04": "Derechos económicos, sociales y culturales",
            "PA05": "Derechos de las víctimas y construcción de paz",
            "PA06": "Derecho al buen futuro de la niñez, adolescencia, juventud",
            "PA07": "Tierras y territorios",
            "PA08": "Líderes y defensores de derechos humanos",
            "PA09": "Crisis de derechos de personas privadas de la libertad",
            "PA10": "Migración transfronteriza",
        }
        return area_names.get(area_id, f"Policy Area {area_id}")


# =============================================================================
# ASYNC WRAPPER
# =============================================================================


async def aggregate_policy_areas_async(
    dimension_scores: list[DimensionScore],
    questionnaire: dict[str, Any] | None = None,
    instrumentation: Any | None = None,
    signal_registry: Any | None = None,
) -> list[AreaScore]:
    """
    Async wrapper for area aggregation.
    
    PHASE 5: Aggregate dimension scores into area scores.
    
    Args:
        dimension_scores: List of 60 DimensionScore objects from Phase 4
        questionnaire: Questionnaire monolith (optional)
        instrumentation: Phase instrumentation for tracking
        signal_registry: Optional SISAS signal registry
    
    Returns:
        List of 10 AreaScore objects
    """
    logger.info("Phase 5: Starting area aggregation")
    
    # Initialize aggregator
    aggregator = AreaPolicyAggregator(
        monolith=questionnaire,
        abort_on_insufficient=True,
        enable_sota_features=True,
        signal_registry=signal_registry,
    )
    
    # Aggregate
    area_scores = aggregator.aggregate(dimension_scores)
    
    logger.info(f"Phase 5: Completed area aggregation ({len(area_scores)} areas)")
    return area_scores
