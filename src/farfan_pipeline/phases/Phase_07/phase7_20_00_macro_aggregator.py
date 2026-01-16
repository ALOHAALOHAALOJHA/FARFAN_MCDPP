from __future__ import annotations

"""
Phase 7 Macro Aggregator - Holistic Evaluation

This module implements the MacroAggregator for Phase 7, which aggregates
4 ClusterScore objects into 1 MacroScore with cross-cutting coherence analysis,
systemic gap detection, and strategic alignment metrics.

Module: src/farfan_pipeline/phases/Phase_7/phase7_20_00_macro_aggregator.py
Purpose: Implement macro-level aggregation logic
Owner: phase7_20
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-13
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 7
__stage__ = 20
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13T00:00:00Z"
__modified__ = "2026-01-13T00:00:00Z"
__criticality__ = "CRITICAL"
__execution_pattern__ = "Per-Task"

import logging
import statistics
from typing import Any
from datetime import datetime
from uuid import uuid4

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

logger = logging.getLogger(__name__)


class MacroAggregator:
    """
    Phase 7 Macro Aggregator.
    
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
    """
    
    def __init__(
        self,
        cluster_weights: dict[str, float] | None = None,
        enable_gap_detection: bool = True,
        enable_coherence_analysis: bool = True,
        enable_alignment_scoring: bool = True,
    ):
        """
        Initialize MacroAggregator.
        
        Args:
            cluster_weights: Custom weights for clusters (default: equal weights)
            enable_gap_detection: Whether to detect systemic gaps
            enable_coherence_analysis: Whether to compute cross-cutting coherence
            enable_alignment_scoring: Whether to compute strategic alignment
        """
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
    
    def aggregate(self, cluster_scores: list[ClusterScore]) -> MacroScore:
        """
        Aggregate cluster scores into macro score.
        
        Args:
            cluster_scores: List of 4 ClusterScore objects
            
        Returns:
            MacroScore: Holistic evaluation
            
        Raises:
            ValueError: If preconditions are violated
        """
        # Validate preconditions
        self._validate_input(cluster_scores)
        
        # Step 1: Compute weighted mean score
        raw_score = self._compute_weighted_score(cluster_scores)
        
        # Step 2: Normalize score
        score_normalized = raw_score / 3.0
        
        # Step 3: Classify quality
        quality_level = self._classify_quality(score_normalized)
        
        # Step 4: Cross-cutting coherence analysis
        coherence, coherence_breakdown = self._compute_coherence(cluster_scores)
        
        # Step 5: Systemic gap detection
        systemic_gaps, gap_severity = self._detect_gaps(cluster_scores)
        
        # Step 6: Strategic alignment scoring
        alignment, alignment_breakdown = self._compute_alignment(cluster_scores)
        
        # Step 7: Uncertainty propagation
        score_std, ci_95 = self._propagate_uncertainty(cluster_scores)
        
        # Step 8: Assemble cluster details
        cluster_details = self._assemble_cluster_details(cluster_scores)
        
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
            pipeline_version="1.0.0",
        )
        
        logger.info(
            f"Macro aggregation complete: score={raw_score:.3f}, "
            f"quality={quality_level}, coherence={coherence:.3f}, "
            f"alignment={alignment:.3f}, gaps={len(systemic_gaps)}"
        )
        
        return macro_score
    
    def _validate_input(self, cluster_scores: list[ClusterScore]) -> None:
        """Validate input preconditions."""
        # PRE-7.1: Exactly 4 cluster scores
        if len(cluster_scores) != 4:
            raise ValueError(f"Expected 4 ClusterScores, got {len(cluster_scores)}")
        
        # PRE-7.2: All required clusters present
        present_clusters = {cs.cluster_id for cs in cluster_scores}
        expected_clusters = set(INPUT_CLUSTERS)
        if present_clusters != expected_clusters:
            missing = expected_clusters - present_clusters
            extra = present_clusters - expected_clusters
            raise ValueError(
                f"Cluster mismatch. Missing: {missing}, Extra: {extra}"
            )
        
        # PRE-7.3: Score bounds validation
        for cs in cluster_scores:
            if not (MIN_SCORE <= cs.score <= MAX_SCORE):
                raise ValueError(
                    f"ClusterScore {cs.cluster_id} score out of bounds: {cs.score}"
                )
    
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
