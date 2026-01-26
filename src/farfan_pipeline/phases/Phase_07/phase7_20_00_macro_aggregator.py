from __future__ import annotations

"""
Phase 7 Macro Aggregator - Holistic Evaluation

This module implements the MacroAggregator for Phase 7, which aggregates
4 ClusterScore objects into 1 MacroScore with cross-cutting coherence analysis,
systemic gap detection, and strategic alignment metrics.

Module: src/farfan_pipeline/phases/Phase_07/phase7_20_00_macro_aggregator.py
Purpose: Implement macro-level aggregation logic
Owner: phase7_20
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-13
"""

# METADATA
__version__ = "2.1.0"  # SISAS irrigation integration
__phase__ = 7
__stage__ = 20
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13T00:00:00Z"
__modified__ = "2026-01-25T00:00:00Z"
__criticality__ = "CRITICAL"
__execution_pattern__ = "Per-Task"

import logging
import statistics
from typing import Any, TYPE_CHECKING
from datetime import datetime
from uuid import uuid4

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_02.registries.questionnaire_signal_registry import (
        QuestionnaireSignalRegistry,
    )
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.consumers.phase7.phase7_meso_consumer import (
        AggregatedInsights,
        Phase7MesoConsumer,
    )

from farfan_pipeline.phases.Phase_06.phase6_10_00_cluster_score import ClusterScore
from farfan_pipeline.phases.Phase_07.phase7_10_00_macro_score import MacroScore
from farfan_pipeline.phases.Phase_07.phase7_10_00_phase_7_constants import (
    CLUSTER_WEIGHTS,
    COHERENCE_WEIGHT_STRATEGIC,
    COHERENCE_WEIGHT_OPERATIONAL,
    COHERENCE_WEIGHT_INSTITUTIONAL,
    QUALITY_THRESHOLDS,
    SYSTEMIC_GAP_THRESHOLD,
    INPUT_CLUSTERS,
    MAX_SCORE,
    MIN_SCORE,
)
from farfan_pipeline.phases.Phase_07.phase7_10_00_systemic_gap_detector import (
    SystemicGapDetector,
)
# Import contracts to enforce validation by default
from farfan_pipeline.phases.Phase_07.contracts import (
    Phase7InputContract,
    Phase7OutputContract,
)

logger = logging.getLogger(__name__)


# =============================================================================
# SISAS IRRIGATION INTEGRATION CONSTANTS
# =============================================================================

# Coherence adjustment range from SISAS irrigation variance
COHERENCE_ADJUSTMENT_MIN = 0.85  # Minimum adjustment (high irrigation variance)
COHERENCE_ADJUSTMENT_MAX = 1.0   # No adjustment (uniform irrigation)

# Gap severity amplification from SISAS divergence signals
GAP_SEVERITY_AMPLIFIER_MIN = 1.0  # No amplification
GAP_SEVERITY_AMPLIFIER_MAX = 2.0  # Maximum amplification (critical divergences)

# Irrigation health weight in cluster details
IRRIGATION_HEALTH_WEIGHT = 0.15  # Weight of irrigation health in final score adjustment


class MacroAggregator:
    """
    Phase 7 Macro Aggregator with SISAS Irrigation Integration.
    
    Aggregates 4 ClusterScore objects into a single holistic MacroScore.
    
    Contract:
        Input:  4 ClusterScore (CLUSTER_MESO_1 through CLUSTER_MESO_4)
        Output: 1 MacroScore (holistic evaluation)
        
    Features:
        - Weighted averaging of cluster scores (equal weights by default)
        - Cross-cutting coherence analysis (strategic, operational, institutional)
        - Systemic gap detection across all policy areas
        - Strategic alignment scoring (vertical, horizontal, temporal)
        - Quality classification based on normalized score
        - Uncertainty propagation from cluster scores
        - SISAS signal registry integration for dynamic weight consumption
        - SISAS irrigation signal integration for coherence adjustment
        - Divergence-amplified gap severity from irrigation signals
        - Provenance tracking for SISAS-sourced configurations
    
    SISAS Irrigation Integration (v2.1):
        When a Phase7MesoConsumer is provided, the aggregator will:
        1. Apply coherence adjustment based on irrigation variance across clusters
        2. Amplify gap severity based on divergence signals detected
        3. Track per-cluster irrigation health in cluster_details
        4. Include irrigation provenance (correlation_ids) for audit traceability
    """
    
    def __init__(
        self,
        cluster_weights: dict[str, float] | None = None,
        enable_gap_detection: bool = True,
        enable_coherence_analysis: bool = True,
        enable_alignment_scoring: bool = True,
        signal_registry: "QuestionnaireSignalRegistry | None" = None,
        irrigation_consumer: "Phase7MesoConsumer | None" = None,
    ):
        """
        Initialize MacroAggregator.
        
        Args:
            cluster_weights: Custom weights for clusters (default: equal weights)
            enable_gap_detection: Whether to detect systemic gaps
            enable_coherence_analysis: Whether to compute cross-cutting coherence
            enable_alignment_scoring: Whether to compute strategic alignment
            signal_registry: Optional SISAS QuestionnaireSignalRegistry for dynamic
                weight consumption and provenance tracking
            irrigation_consumer: Optional Phase7MesoConsumer providing aggregated
                irrigation insights for coherence adjustment and gap amplification
        """
        # SISAS integration
        self.signal_registry = signal_registry
        self.sisas_source: str = "legacy_constant"  # Track weight source
        self.sisas_provenance: dict[str, Any] = {}  # Provenance from SISAS
        
        # SISAS irrigation integration
        self.irrigation_consumer = irrigation_consumer
        self._irrigation_payload: dict[str, Any] | None = None
        
        # Load weights from SISAS if registry provided, otherwise use static weights
        if signal_registry is not None:
            self.cluster_weights = self._load_weights_from_sisas(signal_registry)
        else:
            self.cluster_weights = cluster_weights or CLUSTER_WEIGHTS.copy()
        
        self.enable_gap_detection = enable_gap_detection
        self.enable_coherence_analysis = enable_coherence_analysis
        self.enable_alignment_scoring = enable_alignment_scoring
        self.gap_detector = SystemicGapDetector() if enable_gap_detection else None
        
        # Validate weights sum to 1.0
        weight_sum = sum(self.cluster_weights.values())
        if abs(weight_sum - 1.0) > 1e-6:
            logger.warning(f"Cluster weights sum to {weight_sum}, normalizing to 1.0")
            self.cluster_weights = {
                k: v / weight_sum for k, v in self.cluster_weights.items()
            }
        
        logger.info(
            f"MacroAggregator v2.1 initialized: "
            f"sisas_registry={'enabled' if signal_registry else 'disabled'}, "
            f"irrigation_consumer={'enabled' if irrigation_consumer else 'disabled'}"
        )
    
    def _load_irrigation_payload(self) -> dict[str, Any] | None:
        """
        Load irrigation payload from Phase7MesoConsumer if available.
        
        Returns:
            Dictionary with irrigation metrics or None if unavailable.
        """
        if self.irrigation_consumer is None:
            return None
        
        try:
            payload = self.irrigation_consumer.get_macro_aggregator_payload()
            logger.debug(
                f"Loaded irrigation payload: signals={payload.get('signals_processed', 0)}, "
                f"coherence_adj={payload.get('coherence_adjustment', 1.0):.3f}"
            )
            return payload
        except Exception as e:
            logger.warning(f"Failed to load irrigation payload: {e}")
            return None
    
    def _get_coherence_adjustment(self) -> float:
        """
        Get coherence adjustment factor from irrigation signals.
        
        High variance in cluster irrigation health indicates structural
        coherence issues, resulting in a lower adjustment factor.
        
        Returns:
            Adjustment factor [0.85, 1.0]
        """
        if self._irrigation_payload is None:
            return COHERENCE_ADJUSTMENT_MAX
        
        adjustment = self._irrigation_payload.get("coherence_adjustment", COHERENCE_ADJUSTMENT_MAX)
        return max(COHERENCE_ADJUSTMENT_MIN, min(COHERENCE_ADJUSTMENT_MAX, adjustment))
    
    def _get_gap_severity_amplifier(self) -> float:
        """
        Get gap severity amplifier from divergence signals.
        
        Critical divergences detected in irrigation signals amplify
        the severity of detected systemic gaps.
        
        Returns:
            Amplifier factor [1.0, 2.0]
        """
        if self._irrigation_payload is None:
            return GAP_SEVERITY_AMPLIFIER_MIN
        
        amplifier = self._irrigation_payload.get("gap_severity_amplifier", GAP_SEVERITY_AMPLIFIER_MIN)
        return max(GAP_SEVERITY_AMPLIFIER_MIN, min(GAP_SEVERITY_AMPLIFIER_MAX, amplifier))
    
    def _load_weights_from_sisas(
        self, registry: "QuestionnaireSignalRegistry"
    ) -> dict[str, float]:
        """
        Load cluster weights from SISAS signal registry.
        
        Attempts to fetch AssemblySignalPack for MACRO_1 level.
        Falls back to CLUSTER_WEIGHTS constant if SISAS data unavailable.
        
        Args:
            registry: QuestionnaireSignalRegistry instance
            
        Returns:
            Dictionary of cluster_id -> weight
        """
        try:
            # Attempt to get assembly signals for MACRO level
            assembly_pack = registry.get_assembly_signals("MACRO_1")
            
            if assembly_pack is not None:
                cluster_weights = getattr(assembly_pack, "cluster_weights", None)
                if cluster_weights and isinstance(cluster_weights, dict):
                    # Validate required clusters present
                    required = set(INPUT_CLUSTERS)
                    found = set(cluster_weights.keys())
                    if required.issubset(found):
                        self.sisas_source = "sisas_registry"
                        self.sisas_provenance = {
                            "pack_id": getattr(assembly_pack, "pack_id", "unknown"),
                            "source_hash": getattr(assembly_pack, "source_hash", "unknown"),
                            "level": "MACRO_1",
                        }
                        logger.info(
                            f"Loaded cluster weights from SISAS registry: "
                            f"pack_id={self.sisas_provenance.get('pack_id')}"
                        )
                        return {k: cluster_weights[k] for k in INPUT_CLUSTERS}
                    else:
                        logger.warning(
                            f"SISAS cluster_weights missing required clusters: "
                            f"{required - found}, falling back to constants"
                        )
            
            logger.debug("SISAS assembly signals not available, using constant weights")
            
        except Exception as e:
            logger.warning(f"SISAS weight loading failed: {e}, using constant weights")
        
        # Fallback to static constants
        self.sisas_source = "legacy_constant"
        return CLUSTER_WEIGHTS.copy()
    
    def aggregate(self, cluster_scores: list[ClusterScore]) -> MacroScore:
        """
        Aggregate cluster scores into macro score with SISAS irrigation integration.
        
        Args:
            cluster_scores: List of 4 ClusterScore objects
            
        Returns:
            MacroScore: Holistic evaluation with SISAS-enriched metrics
            
        Raises:
            ValueError: If preconditions are violated
        """
        # Validate preconditions
        self._validate_input(cluster_scores)
        
        # =======================================================================
        # SISAS IRRIGATION INTEGRATION: Load irrigation payload if available
        # =======================================================================
        self._irrigation_payload = self._load_irrigation_payload()
        irrigation_enabled = self._irrigation_payload is not None
        
        # Step 1: Compute weighted mean score
        raw_score = self._compute_weighted_score(cluster_scores)
        
        # Step 2: Normalize score
        score_normalized = raw_score / 3.0
        
        # Step 3: Classify quality
        quality_level = self._classify_quality(score_normalized)
        
        # Step 4: Cross-cutting coherence analysis
        coherence, coherence_breakdown = self._compute_coherence(cluster_scores)
        
        # =======================================================================
        # SISAS: Apply coherence adjustment from irrigation variance
        # =======================================================================
        if irrigation_enabled:
            coherence_adjustment = self._get_coherence_adjustment()
            adjusted_coherence = coherence * coherence_adjustment
            coherence_breakdown["sisas_adjustment"] = {
                "original_coherence": round(coherence, 4),
                "adjustment_factor": round(coherence_adjustment, 4),
                "adjusted_coherence": round(adjusted_coherence, 4),
                "irrigation_variance_detected": coherence_adjustment < 1.0,
            }
            coherence = adjusted_coherence
        
        # Step 5: Systemic gap detection
        systemic_gaps, gap_severity = self._detect_gaps(cluster_scores)
        
        # =======================================================================
        # SISAS: Amplify gap severity from divergence signals
        # =======================================================================
        if irrigation_enabled and systemic_gaps:
            gap_amplifier = self._get_gap_severity_amplifier()
            if gap_amplifier > 1.0:
                # Upgrade severity levels based on amplifier
                severity_upgrade = {
                    "LOW": "MODERATE" if gap_amplifier > 1.3 else "LOW",
                    "MODERATE": "SEVERE" if gap_amplifier > 1.5 else "MODERATE",
                    "SEVERE": "CRITICAL" if gap_amplifier > 1.7 else "SEVERE",
                    "CRITICAL": "CRITICAL",
                }
                gap_severity = {
                    area: severity_upgrade.get(sev, sev)
                    for area, sev in gap_severity.items()
                }
                logger.info(
                    f"SISAS gap amplification applied: amplifier={gap_amplifier:.2f}"
                )
        
        # Step 6: Strategic alignment scoring
        alignment, alignment_breakdown = self._compute_alignment(cluster_scores)
        
        # Step 7: Uncertainty propagation
        score_std, ci_95 = self._propagate_uncertainty(cluster_scores)
        
        # Step 8: Assemble cluster details with SISAS provenance
        cluster_details = self._assemble_cluster_details(cluster_scores)
        cluster_details["sisas_provenance"] = {
            "source": self.sisas_source,
            "weights_from": self.sisas_provenance if self.sisas_provenance else "constants",
        }
        
        # =======================================================================
        # SISAS: Add per-cluster irrigation health and correlation chain
        # =======================================================================
        if irrigation_enabled:
            cluster_irrigation = self._irrigation_payload.get("cluster_metrics", {})
            cluster_details["irrigation_integration"] = {
                "enabled": True,
                "signals_processed": self._irrigation_payload.get("signals_processed", 0),
                "coherence_adjustment": self._get_coherence_adjustment(),
                "gap_severity_amplifier": self._get_gap_severity_amplifier(),
                "overall_irrigation_health": self._irrigation_payload.get("overall_health", 0.0),
                "per_cluster_health": {
                    cid: metrics.get("irrigation_health", 0.0)
                    for cid, metrics in cluster_irrigation.items()
                },
                "phase_correlation_id": self._irrigation_payload.get("phase_correlation_id"),
                "integrity_violations": self._irrigation_payload.get("integrity_violations_count", 0),
                "divergences_detected": self._irrigation_payload.get("divergences_count", 0),
            }
            
            # Apply irrigation health weight to final score adjustment
            irrigation_health = self._irrigation_payload.get("overall_health", 1.0)
            score_adjustment = 1.0 - ((1.0 - irrigation_health) * IRRIGATION_HEALTH_WEIGHT)
            cluster_details["irrigation_integration"]["score_adjustment"] = round(score_adjustment, 4)
            
        else:
            cluster_details["irrigation_integration"] = {
                "enabled": False,
                "reason": "No irrigation_consumer provided",
            }
        
        # Step 9: Generate evaluation ID and provenance
        evaluation_id = f"EVAL_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
        provenance_node_id = f"PROV_MACRO_{uuid4().hex[:8]}"
        
        # Step 10: Construct MacroScore
        macro_score = MacroScore(
            evaluation_id=evaluation_id,
            score=min(MAX_SCORE, max(MIN_SCORE, raw_score)),  # Clamp to bounds
            score_normalized=score_normalized,
            quality_level=quality_level,
            cross_cutting_coherence=coherence,
            coherence_breakdown=coherence_breakdown,
            systemic_gaps=systemic_gaps,
            gap_severity=gap_severity,
            strategic_alignment=alignment,
            alignment_breakdown=alignment_breakdown,
            cluster_scores=cluster_scores,
            cluster_details=cluster_details,
            score_std=score_std,
            confidence_interval_95=ci_95,
            provenance_node_id=provenance_node_id,
            aggregation_method="weighted_average",
            evaluation_timestamp=datetime.utcnow().isoformat() + "Z",
            pipeline_version="2.1.0",  # SISAS irrigation integration
        )
        
        # Validate output contract
        input_cluster_ids = {cs.cluster_id for cs in cluster_scores}
        is_valid, error_message = Phase7OutputContract.validate(macro_score, input_cluster_ids)
        if not is_valid:
            raise ValueError(f"Phase 7 output contract violation: {error_message}")
        
        # Enhanced logging with SISAS metrics
        logger.info(
            f"Macro aggregation complete: score={raw_score:.3f}, "
            f"quality={quality_level}, coherence={coherence:.3f}, "
            f"alignment={alignment:.3f}, gaps={len(systemic_gaps)}, "
            f"sisas_irrigation={'enabled' if irrigation_enabled else 'disabled'}"
        )
        
        return macro_score
    
    def _validate_input(self, cluster_scores: list[ClusterScore]) -> None:
        """
        Validate input preconditions using Phase7InputContract.
        
        Enforces all preconditions by default as part of the canonical flow.
        """
        is_valid, error_message = Phase7InputContract.validate(cluster_scores)
        if not is_valid:
            raise ValueError(f"Phase 7 input contract violation: {error_message}")
    
    def _compute_weighted_score(self, cluster_scores: list[ClusterScore]) -> float:
        """Compute weighted average of cluster scores."""
        weighted_sum = sum(
            self.cluster_weights[cs.cluster_id] * cs.score
            for cs in cluster_scores
        )
        return weighted_sum
    
    def _classify_quality(self, normalized_score: float) -> str:
        """Classify quality level based on normalized score."""
        if normalized_score >= QUALITY_THRESHOLDS["EXCELENTE"]:
            return "EXCELENTE"
        elif normalized_score >= QUALITY_THRESHOLDS["BUENO"]:
            return "BUENO"
        elif normalized_score >= QUALITY_THRESHOLDS["ACEPTABLE"]:
            return "ACEPTABLE"
        else:
            return "INSUFICIENTE"
    
    def _compute_coherence(
        self, cluster_scores: list[ClusterScore]
    ) -> tuple[float, dict[str, Any]]:
        """Compute cross-cutting coherence analysis."""
        if not self.enable_coherence_analysis:
            return 0.0, {}
        
        scores = [cs.score for cs in cluster_scores]
        
        # Strategic coherence: variance-based
        variance = statistics.variance(scores) if len(scores) > 1 else 0.0
        max_variance = 0.75  # Theoretical max for [0,3] with 4 values
        strategic = max(0.0, 1.0 - variance / max_variance)
        
        # Operational coherence: pairwise similarity
        similarities = []
        for i, c1 in enumerate(cluster_scores):
            for c2 in cluster_scores[i + 1 :]:
                sim = 1.0 - abs(c1.score - c2.score) / 3.0
                similarities.append(sim)
        operational = statistics.mean(similarities) if similarities else 1.0
        
        # Institutional coherence: minimum within-cluster coherence
        institutional = min(cs.coherence for cs in cluster_scores)
        
        # Weighted combination
        overall = (
            COHERENCE_WEIGHT_STRATEGIC * strategic
            + COHERENCE_WEIGHT_OPERATIONAL * operational
            + COHERENCE_WEIGHT_INSTITUTIONAL * institutional
        )
        
        breakdown = {
            "strategic_coherence": strategic,
            "operational_coherence": operational,
            "institutional_coherence": institutional,
            "inter_cluster_variance": variance,
        }
        
        return overall, breakdown
    
    def _detect_gaps(
        self, cluster_scores: list[ClusterScore]
    ) -> tuple[list[str], dict[str, str]]:
        """Detect systemic gaps across all policy areas."""
        if not self.enable_gap_detection or not self.gap_detector:
            return [], {}
        
        # Collect all policy areas with scores below threshold
        gaps = []
        severity = {}
        
        for cs in cluster_scores:
            # Check weakest area in cluster
            if cs.weakest_area and cs.score < SYSTEMIC_GAP_THRESHOLD:
                area_id = cs.weakest_area
                if area_id not in gaps:
                    gaps.append(area_id)
                    
                    # Determine severity based on score
                    if cs.score < 1.0:  # < 33%
                        severity[area_id] = "CRITICAL"
                    elif cs.score < 1.35:  # < 45%
                        severity[area_id] = "SEVERE"
                    else:
                        severity[area_id] = "MODERATE"
        
        return gaps, severity
    
    def _compute_alignment(
        self, cluster_scores: list[ClusterScore]
    ) -> tuple[float, dict[str, Any]]:
        """Compute strategic alignment scoring."""
        if not self.enable_alignment_scoring:
            return 0.0, {}
        
        score_map = {cs.cluster_id: cs.score for cs in cluster_scores}
        
        # Vertical alignment: MESO_1 (legal) ↔ MESO_2 (implementation)
        vertical = 1.0 - abs(
            score_map["CLUSTER_MESO_1"] - score_map["CLUSTER_MESO_2"]
        ) / 3.0
        
        # Horizontal alignment: all pairwise similarities
        scores = list(score_map.values())
        pairwise_sims = []
        for i in range(len(scores)):
            for j in range(i + 1, len(scores)):
                pairwise_sims.append(1.0 - abs(scores[i] - scores[j]) / 3.0)
        horizontal = statistics.mean(pairwise_sims) if pairwise_sims else 1.0
        
        # Temporal alignment: MESO_3 (monitoring) ↔ MESO_4 (planning)
        temporal = 1.0 - abs(
            score_map["CLUSTER_MESO_3"] - score_map["CLUSTER_MESO_4"]
        ) / 3.0
        
        # Overall alignment
        overall = (vertical + horizontal + temporal) / 3.0
        
        breakdown = {
            "vertical_alignment": vertical,
            "horizontal_alignment": horizontal,
            "temporal_alignment": temporal,
        }
        
        return overall, breakdown
    
    def _propagate_uncertainty(
        self, cluster_scores: list[ClusterScore]
    ) -> tuple[float, tuple[float, float]]:
        """Propagate uncertainty from cluster scores to macro score."""
        # Variance propagation for weighted linear combination
        variance = sum(
            (self.cluster_weights[cs.cluster_id] ** 2) * (cs.score_std ** 2)
            for cs in cluster_scores
        )
        std = variance ** 0.5
        
        # Compute macro score for CI center
        macro_score = self._compute_weighted_score(cluster_scores)
        
        # 95% confidence interval (1.96 * std for normal distribution)
        ci_lower = max(MIN_SCORE, macro_score - 1.96 * std)
        ci_upper = min(MAX_SCORE, macro_score + 1.96 * std)
        
        return std, (ci_lower, ci_upper)
    
    def _assemble_cluster_details(
        self, cluster_scores: list[ClusterScore]
    ) -> dict[str, Any]:
        """Assemble summary details for each cluster."""
        details = {}
        for cs in cluster_scores:
            details[cs.cluster_id] = {
                "score": cs.score,
                "coherence": cs.coherence,
                "variance": cs.variance,
                "weakest_area": cs.weakest_area,
                "dispersion_scenario": cs.dispersion_scenario,
                "penalty_applied": cs.penalty_applied,
                "areas": cs.areas,
            }
        return details
