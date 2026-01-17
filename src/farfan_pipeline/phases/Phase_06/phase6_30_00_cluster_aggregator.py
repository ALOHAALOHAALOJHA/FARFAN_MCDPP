"""
Phase 6 Cluster Aggregator - Main Orchestrator

This module implements the main cluster aggregation logic for Phase 6,
synthesizing 10 Policy Area scores into 4 MESO-level Cluster scores with
adaptive penalty based on dispersion analysis.

Inputs: 10 AreaScore objects (PA01-PA10) from Phase 5
Outputs: 4 ClusterScore objects (CLUSTER_MESO_1 to CLUSTER_MESO_4)

Mathematical Framework:
    raw_score = Σ(weight_i × area_score_i) for areas in cluster
    penalty_factor = adaptive_penalty(dispersion_metrics)
    final_score = raw_score × penalty_factor

Module: src/farfan_pipeline/phases/Phase_6/phase6_30_00_cluster_aggregator.py
Phase: 6 (Cluster Aggregation - MESO)
Stage: 30
Owner: phase6_30
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 6
__stage__ = 30
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13"
__modified__ = "2026-01-13"
__criticality__ = "CRITICAL"
__execution_pattern__ = "Per-Task"

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_05.phase5_00_00_area_score import AreaScore

from farfan_pipeline.phases.Phase_06.phase6_10_00_phase_6_constants import (
    CLUSTERS,
    CLUSTER_COMPOSITION,
    MIN_SCORE,
    MAX_SCORE,
)
from farfan_pipeline.phases.Phase_06.phase6_10_00_cluster_score import ClusterScore
from farfan_pipeline.phases.Phase_06.phase6_20_00_adaptive_meso_scoring import (
    AdaptiveMesoScoring,
    AdaptiveScoringConfig,
)
from farfan_pipeline.phases.Phase_06.contracts.phase6_input_contract import (
    Phase6InputContract,
)
from farfan_pipeline.phases.Phase_06.contracts.phase6_output_contract import (
    Phase6OutputContract,
)

logger = logging.getLogger(__name__)


class ClusterAggregator:
    """
    Phase 6 Cluster Aggregation Engine.

    Aggregates 10 Policy Area scores into 4 MESO-level Cluster scores
    with adaptive penalty based on intra-cluster dispersion.

    This class implements the complete Phase 6 transformation:
    - Input validation
    - Cluster routing and grouping
    - Weighted mean computation
    - Dispersion analysis
    - Adaptive penalty application
    - ClusterScore construction
    """

    def __init__(
        self,
        monolith: dict[str, Any] | None = None,
        abort_on_insufficient: bool = True,
        scoring_config: AdaptiveScoringConfig | None = None,
        enforce_contracts: bool = True,
        contract_mode: str = "strict",
    ):
        """
        Initialize ClusterAggregator.

        Args:
            monolith: Questionnaire monolith (optional, for future weight customization)
            abort_on_insufficient: Whether to raise on validation failures
            scoring_config: Optional custom scoring configuration
            enforce_contracts: Whether to invoke input/output contracts
            contract_mode: Contract enforcement mode: "strict" | "warn" | "disabled"
        """
        self.monolith = monolith or {}
        self.abort_on_insufficient = abort_on_insufficient
        self.enforce_contracts = enforce_contracts
        self.contract_mode = contract_mode
        self.adaptive_scoring = AdaptiveMesoScoring(scoring_config)

        # Load cluster weights (equal weights for now)
        self.cluster_weights = self._initialize_cluster_weights()

        logger.info(
            "ClusterAggregator initialized for Phase 6 "
            f"(enforce_contracts={enforce_contracts}, contract_mode={contract_mode})"
        )

    def _initialize_cluster_weights(self) -> dict[str, dict[str, float]]:
        """
        Initialize default cluster weights.

        Returns equal weights for all areas within each cluster:
        - 3-area clusters: 0.333 per area
        - 2-area clusters: 0.500 per area

        Returns:
            Dictionary mapping cluster_id -> {area_id: weight}
        """
        weights = {}
        for cluster_id, areas in CLUSTER_COMPOSITION.items():
            n_areas = len(areas)
            equal_weight = 1.0 / n_areas
            weights[cluster_id] = {area_id: equal_weight for area_id in areas}

        logger.debug(f"Initialized cluster weights: {weights}")
        return weights

    def _validate_input_contract(
        self, area_scores: list["AreaScore"]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Validate input via Phase6InputContract.
        """
        if not self.enforce_contracts or self.contract_mode == "disabled":
            return True, {"skipped": True, "reason": "contracts disabled"}

        valid, details = Phase6InputContract.validate(area_scores)

        for warning in details.get("warnings", []):
            logger.warning(f"Phase6InputContract warning: {warning}")

        if not valid:
            error_msg = f"Phase6InputContract failed: {details.get('errors', [])}"
            if self.contract_mode == "strict":
                logger.error(error_msg)
                raise ValueError(error_msg)
            elif self.contract_mode == "warn":
                logger.warning(error_msg)

        return valid, details

    def _validate_output_contract(
        self, cluster_scores: list["ClusterScore"]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Validate output via Phase6OutputContract.
        """
        if not self.enforce_contracts or self.contract_mode == "disabled":
            return True, {"skipped": True, "reason": "contracts disabled"}

        valid, details = Phase6OutputContract.validate(cluster_scores)

        for warning in details.get("warnings", []):
            logger.warning(f"Phase6OutputContract warning: {warning}")

        if not valid:
            error_msg = f"Phase6OutputContract failed: {details.get('errors', [])}"
            if self.contract_mode == "strict":
                logger.error(error_msg)
                raise ValueError(error_msg)
            elif self.contract_mode == "warn":
                logger.warning(error_msg)

        return valid, details

    def aggregate(self, area_scores: list[AreaScore]) -> list[ClusterScore]:
        """
        Aggregate 10 AreaScores into 4 ClusterScores with contract enforcement.

        Args:
            area_scores: List of 10 AreaScore objects from Phase 5

        Returns:
            List of 4 ClusterScore objects

        Raises:
            ValueError: If validation fails and contract_mode is strict
        """
        logger.info("Phase 6: Starting cluster aggregation")

        # Contract precondition
        input_valid, _ = self._validate_input_contract(area_scores)
        if input_valid:
            logger.debug("Phase6InputContract passed")

        # Legacy validation
        self._validate_input(area_scores)

        # Aggregate each cluster
        cluster_scores = []
        for cluster_id in CLUSTERS:
            logger.debug(f"Processing cluster: {cluster_id}")
            cluster_score = self.aggregate_cluster(cluster_id, area_scores)
            cluster_scores.append(cluster_score)

        # Contract postcondition
        output_valid, _ = self._validate_output_contract(cluster_scores)
        if output_valid:
            logger.debug("Phase6OutputContract passed")

        logger.info(
            f"Phase 6: Completed {len(cluster_scores)} cluster aggregations "
            f"(input_valid={input_valid}, output_valid={output_valid})"
        )
        return cluster_scores

    def aggregate_cluster(
        self,
        cluster_id: str,
        area_scores: list[AreaScore],
    ) -> ClusterScore:
        """
        Aggregate a single cluster from area scores.

        ROUTING BEHAVIOR:
        AreaScores are routed by `area_id` membership in `CLUSTER_COMPOSITION`
        (single source of truth). The `cluster_id` field on AreaScore is
        informational/provenance only and is not used for routing.

        Args:
            cluster_id: Cluster identifier
            area_scores: List of all AreaScore objects

        Returns:
            ClusterScore object for the cluster
        """
        expected_areas = CLUSTER_COMPOSITION[cluster_id]

        # Filter areas for this cluster
        cluster_areas = [
            area for area in area_scores
            if area.area_id in expected_areas
        ]

        # Validate we have all expected areas
        if len(cluster_areas) != len(expected_areas):
            found_ids = {a.area_id for a in cluster_areas}
            missing = set(expected_areas) - found_ids
            msg = f"Cluster {cluster_id}: Expected {len(expected_areas)} areas, found {len(cluster_areas)}. Missing: {missing}"
            logger.error(msg)
            if self.abort_on_insufficient:
                raise ValueError(msg)

        # Get weights for this cluster
        weights = self.cluster_weights[cluster_id]

        # Compute weighted mean (raw score)
        raw_score = self._compute_weighted_mean(cluster_areas, weights)

        # Compute dispersion metrics
        area_score_values = [area.score for area in cluster_areas]
        metrics = self.adaptive_scoring.compute_metrics(area_score_values)

        # Compute adaptive penalty
        penalty_factor, penalty_details = self.adaptive_scoring.compute_adaptive_penalty_factor(metrics)
        penalty_applied = 1.0 - penalty_factor

        # Apply penalty to get final score
        final_score = raw_score * penalty_factor
        final_score = max(MIN_SCORE, min(MAX_SCORE, final_score))  # Clamp to bounds

        # Compute coherence and variance
        coherence = self._compute_coherence(cluster_areas, final_score)
        variance = metrics.variance

        # Identify weakest area
        weakest_area = min(cluster_areas, key=lambda a: a.score).area_id

        # Compute standard deviation (uncertainty propagation)
        score_std = self._propagate_uncertainty(cluster_areas, weights)

        # Construct ClusterScore
        cluster_score = ClusterScore(
            cluster_id=cluster_id,
            cluster_name=self._get_cluster_name(cluster_id),
            areas=[area.area_id for area in cluster_areas],
            score=final_score,
            coherence=coherence,
            variance=variance,
            weakest_area=weakest_area,
            area_scores=cluster_areas,
            validation_passed=True,
            validation_details={
                "expected_areas": len(expected_areas),
                "actual_areas": len(cluster_areas),
                "all_present": len(cluster_areas) == len(expected_areas),
            },
            score_std=score_std,
            confidence_interval_95=(
                max(MIN_SCORE, final_score - 1.96 * score_std),
                min(MAX_SCORE, final_score + 1.96 * score_std),
            ),
            provenance_node_id=f"cluster_{cluster_id}_{len(cluster_areas)}_areas",
            aggregation_method="weighted_average_with_adaptive_penalty",
            dispersion_scenario=metrics.scenario_type,
            penalty_applied=penalty_applied,
        )

        logger.info(
            f"Cluster {cluster_id}: raw={raw_score:.3f}, "
            f"penalty={penalty_factor:.3f}, final={final_score:.3f}, "
            f"scenario={metrics.scenario_type}"
        )

        return cluster_score

    def _validate_input(self, area_scores: list[AreaScore]) -> None:
        """
        Validate input area scores meet Phase 6 preconditions.

        Args:
            area_scores: List of AreaScore objects

        Raises:
            ValueError: If validation fails
        """
        if len(area_scores) != 10:
            msg = f"Phase 6 requires exactly 10 AreaScore objects, got {len(area_scores)}"
            logger.error(msg)
            raise ValueError(msg)

        # Verify all PA01-PA10 are present
        area_ids = {area.area_id for area in area_scores}
        expected_ids = {f"PA{i:02d}" for i in range(1, 11)}
        if area_ids != expected_ids:
            missing = expected_ids - area_ids
            extra = area_ids - expected_ids
            msg = f"Phase 6: Invalid area IDs. Missing: {missing}, Extra: {extra}"
            logger.error(msg)
            raise ValueError(msg)

        # Verify all scores are in bounds
        for area in area_scores:
            if not (MIN_SCORE <= area.score <= MAX_SCORE):
                msg = f"Area {area.area_id} score {area.score} out of bounds [{MIN_SCORE}, {MAX_SCORE}]"
                logger.error(msg)
                raise ValueError(msg)

        logger.debug("Input validation passed: 10 areas with valid scores")

    def _compute_weighted_mean(
        self,
        areas: list[AreaScore],
        weights: dict[str, float]
    ) -> float:
        """
        Compute weighted arithmetic mean of area scores.

        Args:
            areas: List of AreaScore objects
            weights: Dictionary mapping area_id to weight

        Returns:
            Weighted mean score
        """
        weighted_sum = sum(weights[area.area_id] * area.score for area in areas)
        return weighted_sum

    def _compute_coherence(
        self,
        areas: list[AreaScore],
        cluster_score: float
    ) -> float:
        """
        Compute coherence metric for the cluster.

        Coherence measures how tightly clustered the area scores are.
        Higher coherence (closer to 1.0) indicates better alignment.

        Args:
            areas: List of AreaScore objects
            cluster_score: Computed cluster score

        Returns:
            Coherence metric [0.0, 1.0]
        """
        if not areas:
            return 0.0

        scores = [area.score for area in areas]
        mean = sum(scores) / len(scores)
        std = (sum((s - mean) ** 2 for s in scores) / len(scores)) ** 0.5
        cv = std / mean if mean > 0 else 0.0

        # Coherence is inverse of CV, normalized to [0, 1]
        # CV of 1.0 -> coherence of 0.0
        # CV of 0.0 -> coherence of 1.0
        coherence = max(0.0, 1.0 - cv)
        return coherence

    def _propagate_uncertainty(
        self,
        areas: list[AreaScore],
        weights: dict[str, float]
    ) -> float:
        """
        Propagate uncertainty from area scores to cluster score.

        Uses variance addition for independent weighted sum:
        Var(weighted_sum) = Σ(weight_i² × Var(score_i))

        Args:
            areas: List of AreaScore objects
            weights: Dictionary mapping area_id to weight

        Returns:
            Standard deviation of cluster score
        """
        variance_sum = 0.0
        for area in areas:
            w = weights[area.area_id]
            # Use score_std from area if available, otherwise estimate
            area_variance = (area.score_std ** 2) if hasattr(area, 'score_std') and area.score_std > 0 else 0.01
            variance_sum += (w ** 2) * area_variance

        return variance_sum ** 0.5

    def _get_cluster_name(self, cluster_id: str) -> str:
        """
        Get human-readable cluster name.

        Args:
            cluster_id: Cluster identifier (e.g., "CLUSTER_MESO_1")

        Returns:
            Human-readable name
        """
        names = {
            "CLUSTER_MESO_1": "Legal & Institutional Framework",
            "CLUSTER_MESO_2": "Implementation & Operational Capacity",
            "CLUSTER_MESO_3": "Monitoring & Evaluation Systems",
            "CLUSTER_MESO_4": "Strategic Planning & Sustainability",
        }
        return names.get(cluster_id, cluster_id)
