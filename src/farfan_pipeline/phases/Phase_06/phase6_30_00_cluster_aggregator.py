"""
Phase 6 Cluster Aggregator - Main Orchestrator

This module implements the main cluster aggregation logic for Phase 6,
synthesizing 10 Policy Area scores into 4 MESO-level Cluster scores with
adaptive penalty based on dispersion analysis.

SISAS INTEGRATION v2.0:
- Consumes uncertainty signals from Phase 5
- Uses confidence signals to adjust cluster weights
- Integrates integrity validation signals into aggregation
- Event-driven irrigation from SISAS event bus

Inputs: 10 AreaScore objects (PA01-PA10) from Phase 5
Outputs: 4 ClusterScore objects (CLUSTER_MESO_1 to CLUSTER_MESO_4)

Mathematical Framework:
    raw_score = Σ(weight_i × area_score_i) for areas in cluster
    penalty_factor = adaptive_penalty(dispersion_metrics)
    signal_adjustment = apply_signal_modifiers(signals)
    final_score = raw_score × penalty_factor × signal_adjustment

Module: src/farfan_pipeline/phases/Phase_06/phase6_30_00_cluster_aggregator.py
Phase: 6 (Cluster Aggregation - MESO)
Stage: 30
Owner: phase6_30
Version: 2.0.0 (SISAS-Enhanced)
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "2.0.0"
__phase__ = 6
__stage__ = 30
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13"
__modified__ = "2026-01-25"
__criticality__ = "CRITICAL"
__execution_pattern__ = "Event-Driven"

import logging
from typing import Any, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_05.phase5_00_00_area_score import AreaScore

try:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import Signal
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import BusRegistry
    SISAS_AVAILABLE = True
except ImportError:
    Signal = None  # type: ignore
    BusRegistry = None  # type: ignore
    SISAS_AVAILABLE = False

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
from farfan_pipeline.phases.Phase_06.contracts.phase6_10_00_input_contract import (
    Phase6InputContract,
)
from farfan_pipeline.phases.Phase_06.contracts.phase6_10_02_output_contract import (
    Phase6OutputContract,
)

logger = logging.getLogger(__name__)


# =============================================================================
# SISAS INTEGRATION DATA STRUCTURES
# =============================================================================

@dataclass
class ClusterSignalContext:
    """
    Signal context for cluster aggregation.

    Captures SISAS signals that influence cluster scoring:
    - Uncertainty signals from Phase 5
    - Confidence signals from area scoring
    - Integrity signals from validation
    """
    cluster_id: str
    uncertainty_signals: dict[str, float] = field(default_factory=dict)
    confidence_signals: dict[str, float] = field(default_factory=dict)
    integrity_signals: dict[str, float] = field(default_factory=dict)
    signal_count: int = 0
    aggregate_confidence: float = 1.0

    def compute_signal_adjustment(self) -> float:
        """
        Compute signal-based adjustment factor for cluster score.

        Returns:
            Adjustment factor in [0.8, 1.2] where:
            - < 1.0: Signals suggest reducing score (low confidence, high uncertainty)
            - 1.0: Neutral (no strong signals)
            - > 1.0: Signals support increasing score (high confidence, validated)
        """
        if not self.uncertainty_signals and not self.confidence_signals:
            return 1.0

        # Uncertainty penalty: higher uncertainty -> lower adjustment
        uncertainty_penalty = 0.0
        if self.uncertainty_signals:
            avg_uncertainty = sum(self.uncertainty_signals.values()) / len(self.uncertainty_signals)
            uncertainty_penalty = min(0.15, avg_uncertainty * 0.3)

        # Confidence boost: higher confidence -> higher adjustment
        confidence_boost = 0.0
        if self.confidence_signals:
            avg_confidence = sum(self.confidence_signals.values()) / len(self.confidence_signals)
            confidence_boost = min(0.1, avg_confidence * 0.15)

        # Integrity adjustment
        integrity_adjustment = 0.0
        if self.integrity_signals:
            avg_integrity = sum(self.integrity_signals.values()) / len(self.integrity_signals)
            if avg_integrity < 0.7:
                integrity_adjustment = -0.1
            elif avg_integrity > 0.9:
                integrity_adjustment = 0.05

        # Combine adjustments
        adjustment = 1.0 - uncertainty_penalty + confidence_boost + integrity_adjustment

        # Bound to reasonable range
        return max(0.8, min(1.2, adjustment))


# =============================================================================
# MAIN CLASS
# =============================================================================


class ClusterAggregator:
    """
    Phase 6 Cluster Aggregation Engine - SISAS Enhanced.

    Aggregates 10 Policy Area scores into 4 MESO-level Cluster scores
    with adaptive penalty based on intra-cluster dispersion.

    SISAS ENHANCEMENTS (v2.0):
    - Consumes uncertainty signals from Phase 5 via SISAS event bus
    - Uses confidence signals to adjust cluster weights dynamically
    - Integrates integrity validation signals into aggregation
    - Event-driven irrigation from SISAS vehicles

    This class implements the complete Phase 6 transformation:
    - Input validation
    - Cluster routing and grouping
    - Signal-based weight adjustment
    - Weighted mean computation
    - Dispersion analysis
    - Adaptive penalty application
    - Signal adjustment factor
    - ClusterScore construction
    """

    def __init__(
        self,
        monolith: dict[str, Any] | None = None,
        abort_on_insufficient: bool = True,
        scoring_config: AdaptiveScoringConfig | None = None,
        enforce_contracts: bool = True,
        contract_mode: str = "strict",
        enable_sisas: bool = True,
        bus_registry: BusRegistry | None = None,
    ):
        """
        Initialize ClusterAggregator.

        Args:
            monolith: Questionnaire monolith (optional, for future weight customization)
            abort_on_insufficient: Whether to raise on validation failures
            scoring_config: Optional custom scoring configuration
            enforce_contracts: Whether to invoke input/output contracts
            contract_mode: Contract enforcement mode: "strict" | "warn" | "disabled"
            enable_sisas: Enable SISAS signal integration (default: True)
            bus_registry: Optional SISAS bus registry for signal consumption
        """
        self.monolith = monolith or {}
        self.abort_on_insufficient = abort_on_insufficient
        self.enforce_contracts = enforce_contracts
        self.contract_mode = contract_mode
        self.adaptive_scoring = AdaptiveMesoScoring(scoring_config)
        self.enable_sisas = enable_sisas and SISAS_AVAILABLE
        self.bus_registry = bus_registry

        # SISAS signal storage
        self._signal_contexts: dict[str, ClusterSignalContext] = {}
        self._received_signals: list[Signal] = []

        # Load cluster weights (equal weights for now)
        self.cluster_weights = self._initialize_cluster_weights()

        # Subscribe to SISAS buses if enabled
        if self.enable_sisas and self.bus_registry:
            self._subscribe_to_sisas_buses()

        logger.info(
            f"ClusterAggregator v2.0 initialized for Phase 6 "
            f"(sisas_enabled={self.enable_sisas}, enforce_contracts={enforce_contracts}, "
            f"contract_mode={contract_mode})"
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

    # ========================================================================
    # SISAS INTEGRATION METHODS
    # ========================================================================

    def _subscribe_to_sisas_buses(self) -> None:
        """Subscribe to SISAS event buses for Phase 5 uncertainty signals."""
        if not self.bus_registry:
            return

        try:
            # Subscribe to uncertainty bus for Phase 5 signals
            uncertainty_bus = self.bus_registry.get_bus("uncertainty_bus")
            if uncertainty_bus:
                uncertainty_bus.subscribe(self._consume_uncertainty_signal)
                logger.info("Subscribed to uncertainty_bus for Phase 5 signals")

            # Subscribe to confidence bus for area scoring signals
            confidence_bus = self.bus_registry.get_bus("confidence_bus")
            if confidence_bus:
                confidence_bus.subscribe(self._consume_confidence_signal)
                logger.info("Subscribed to confidence_bus for area scoring signals")

        except Exception as exc:
            logger.warning(f"Failed to subscribe to SISAS buses: {exc}")

    def _consume_uncertainty_signal(self, signal: Signal) -> dict[str, Any]:
        """
        Consume uncertainty signal from Phase 5.

        Extracts uncertainty information and stores it for cluster aggregation.
        """
        try:
            # Extract cluster and area information from signal context
            cluster_id = getattr(signal.context, "node_id", "UNKNOWN") if signal.context else "UNKNOWN"

            # Extract uncertainty value
            uncertainty_value = 0.0
            if hasattr(signal, "value") and isinstance(signal.value, dict):
                uncertainty_value = signal.value.get("uncertainty_score", 0.0)
            elif isinstance(signal.value, (int, float)):
                uncertainty_value = float(signal.value)

            # Store in signal context
            if cluster_id not in self._signal_contexts:
                self._signal_contexts[cluster_id] = ClusterSignalContext(cluster_id=cluster_id)

            # Determine which area this signal belongs to
            area_id = signal.metadata.get("area_id") if hasattr(signal, "metadata") else None
            if area_id:
                self._signal_contexts[cluster_id].uncertainty_signals[area_id] = uncertainty_value

            self._received_signals.append(signal)

            logger.debug(
                f"Consumed uncertainty signal for {cluster_id}/{area_id}: "
                f"uncertainty={uncertainty_value:.3f}"
            )

            return {
                "consumed": True,
                "cluster_id": cluster_id,
                "area_id": area_id,
                "uncertainty": uncertainty_value,
            }

        except Exception as exc:
            logger.warning(f"Error consuming uncertainty signal: {exc}")
            return {"consumed": False, "error": str(exc)}

    def _consume_confidence_signal(self, signal: Signal) -> dict[str, Any]:
        """
        Consume confidence signal from area scoring.

        Extracts confidence information and stores it for weight adjustment.
        """
        try:
            cluster_id = getattr(signal.context, "node_id", "UNKNOWN") if signal.context else "UNKNOWN"

            # Extract confidence value
            confidence_value = 1.0
            if hasattr(signal, "value") and isinstance(signal.value, dict):
                confidence_value = signal.value.get("confidence", 1.0)
            elif isinstance(signal.value, (int, float)):
                confidence_value = float(signal.value)

            # Store in signal context
            if cluster_id not in self._signal_contexts:
                self._signal_contexts[cluster_id] = ClusterSignalContext(cluster_id=cluster_id)

            area_id = signal.metadata.get("area_id") if hasattr(signal, "metadata") else None
            if area_id:
                self._signal_contexts[cluster_id].confidence_signals[area_id] = confidence_value

            self._received_signals.append(signal)

            logger.debug(
                f"Consumed confidence signal for {cluster_id}/{area_id}: "
                f"confidence={confidence_value:.3f}"
            )

            return {
                "consumed": True,
                "cluster_id": cluster_id,
                "area_id": area_id,
                "confidence": confidence_value,
            }

        except Exception as exc:
            logger.warning(f"Error consuming confidence signal: {exc}")
            return {"consumed": False, "error": str(exc)}

    def _get_signal_adjustment_for_cluster(
        self, cluster_id: str, area_scores: list[AreaScore]
    ) -> float:
        """
        Get signal-based adjustment factor for a cluster.

        Args:
            cluster_id: Cluster identifier
            area_scores: List of area scores in this cluster

        Returns:
            Adjustment factor in [0.8, 1.2]
        """
        if not self.enable_sisas or not self._signal_contexts:
            return 1.0

        # Get or create signal context for this cluster
        signal_context = self._signal_contexts.get(cluster_id)
        if not signal_context:
            # Extract uncertainty from area scores if no signals received
            signal_context = ClusterSignalContext(cluster_id=cluster_id)
            for area in area_scores:
                if hasattr(area, "uncertainty") and area.uncertainty:
                    signal_context.uncertainty_signals[area.area_id] = area.uncertainty
                if hasattr(area, "confidence") and area.confidence:
                    signal_context.confidence_signals[area.area_id] = area.confidence

        return signal_context.compute_signal_adjustment()

    def _adjust_weights_with_signals(
        self, cluster_id: str, base_weights: dict[str, float]
    ) -> dict[str, float]:
        """
        Adjust cluster weights based on SISAS confidence signals.

        Areas with higher confidence get slightly higher weights.
        """
        if not self.enable_sisas:
            return base_weights

        signal_context = self._signal_contexts.get(cluster_id)
        if not signal_context or not signal_context.confidence_signals:
            return base_weights

        # Compute confidence-based adjustments
        adjusted_weights = {}
        total_confidence = sum(signal_context.confidence_signals.values())

        for area_id, base_weight in base_weights.items():
            confidence = signal_context.confidence_signals.get(area_id, 1.0)
            # Boost weight by confidence proportionally
            confidence_factor = 1.0 + (confidence - 1.0) * 0.2  # Max ±20% adjustment
            adjusted_weights[area_id] = base_weight * confidence_factor

        # Renormalize to sum to 1.0
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            adjusted_weights = {
                area_id: weight / total_weight
                for area_id, weight in adjusted_weights.items()
            }

        logger.debug(
            f"Adjusted weights for {cluster_id} based on confidence signals: "
            f"{adjusted_weights}"
        )

        return adjusted_weights

    def get_sisas_status(self) -> dict[str, Any]:
        """
        Get SISAS integration status for monitoring.

        Returns:
            Dictionary with SISAS status information
        """
        return {
            "sisas_enabled": self.enable_sisas,
            "sisas_available": SISAS_AVAILABLE,
            "bus_registry_connected": self.bus_registry is not None,
            "signal_contexts_count": len(self._signal_contexts),
            "signals_received": len(self._received_signals),
            "clusters_with_signals": list(self._signal_contexts.keys()),
            "aggregate_confidence": (
                sum(sc.aggregate_confidence for sc in self._signal_contexts.values()) /
                len(self._signal_contexts) if self._signal_contexts else 1.0
            ),
        }

    # ========================================================================
    # CORE AGGREGATION METHODS
    # ========================================================================

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

        SISAS ENHANCED: Incorporates signal-based adjustments from SISAS event bus.

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

        # Get base weights for this cluster
        base_weights = self.cluster_weights[cluster_id]

        # SISAS: Adjust weights based on confidence signals
        weights = self._adjust_weights_with_signals(cluster_id, base_weights)

        # Compute weighted mean (raw score)
        raw_score = self._compute_weighted_mean(cluster_areas, weights)

        # Compute dispersion metrics
        area_score_values = [area.score for area in cluster_areas]
        metrics = self.adaptive_scoring.compute_metrics(area_score_values)

        # Compute adaptive penalty
        penalty_factor, penalty_details = self.adaptive_scoring.compute_adaptive_penalty_factor(metrics)
        penalty_applied = 1.0 - penalty_factor

        # Apply penalty to get adjusted score
        adjusted_score = raw_score * penalty_factor

        # SISAS: Get signal-based adjustment factor
        signal_adjustment = self._get_signal_adjustment_for_cluster(cluster_id, cluster_areas)

        # Apply signal adjustment to get final score
        final_score = adjusted_score * signal_adjustment
        final_score = max(MIN_SCORE, min(MAX_SCORE, final_score))  # Clamp to bounds

        # Compute coherence and variance
        coherence = self._compute_coherence(cluster_areas, final_score)
        variance = metrics.variance

        # Identify weakest area
        weakest_area = min(cluster_areas, key=lambda a: a.score).area_id

        # Compute standard deviation (uncertainty propagation)
        score_std = self._propagate_uncertainty(cluster_areas, weights)

        # SISAS enhancement metadata
        sisas_metadata = {}
        if self.enable_sisas:
            sisas_metadata = {
                "signal_adjustment": round(signal_adjustment, 4),
                "weights_adjusted": weights != base_weights,
                "signal_context": self._signal_contexts.get(cluster_id).__dict__ if cluster_id in self._signal_contexts else None,
            }

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
                **sisas_metadata,  # SISAS enhancement
            },
            score_std=score_std,
            confidence_interval_95=(
                max(MIN_SCORE, final_score - 1.96 * score_std),
                min(MAX_SCORE, final_score + 1.96 * score_std),
            ),
            provenance_node_id=f"cluster_{cluster_id}_{len(cluster_areas)}_areas",
            aggregation_method="weighted_average_with_adaptive_penalty_sisas",  # SISAS enhanced
            dispersion_scenario=metrics.scenario_type,
            penalty_applied=penalty_applied,
        )

        # Enhanced logging with SISAS information
        log_msg = (
            f"Cluster {cluster_id}: raw={raw_score:.3f}, "
            f"penalty={penalty_factor:.3f}, signal_adj={signal_adjustment:.3f}, "
            f"final={final_score:.3f}, scenario={metrics.scenario_type}"
        )
        if self.enable_sisas and signal_adjustment != 1.0:
            log_msg += f" [SISAS: adjustment={signal_adjustment:.3f}]"
        logger.info(log_msg)

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
