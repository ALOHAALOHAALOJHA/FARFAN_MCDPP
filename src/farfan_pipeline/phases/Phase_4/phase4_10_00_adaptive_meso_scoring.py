"""
Adaptive Meso-Level Scoring Module

This module implements enhanced, adaptive scoring mechanisms for cluster (meso-level)
aggregation that address the audit findings:

1. Adaptive penalty weights based on scenario characteristics (dispersion vs convergence)
2. Non-linear penalty scaling for extreme dispersion cases
3. Strengthened penalties for high-dispersion scenarios
4. Maintained mathematical correctness (100%)

Mathematical Foundation:
-----------------------
The adaptive scoring mechanism uses a context-sensitive penalty function that
adjusts based on:
- Coefficient of Variation (CV): Relative dispersion measure
- Dispersion Index (DI): Normalized range measure
- Score distribution shape: Convergence vs dispersion pattern

Formula:
    adjusted_score = weighted_score × penalty_factor

Where penalty_factor is computed adaptively using:
    penalty_factor = 1.0 - penalty_strength
    penalty_strength = base_penalty × sensitivity_multiplier × shape_factor

    base_penalty: Derived from normalized standard deviation
    sensitivity_multiplier: Adaptive [0.8-2.0] based on CV and DI
    shape_factor: Non-linear scaling [1.0-2.5] for extreme cases
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AdaptiveScoringConfig:
    """Configuration for adaptive scoring behavior."""

    max_score: float = 3.0

    # Base penalty weight (replaces fixed PENALTY_WEIGHT=0.3)
    base_penalty_weight: float = 0.35

    # Convergence thresholds (low dispersion)
    convergence_cv_threshold: float = 0.15
    convergence_di_threshold: float = 0.20

    # Dispersion thresholds (high dispersion)
    high_dispersion_cv_threshold: float = 0.40
    extreme_dispersion_cv_threshold: float = 0.60

    # Sensitivity multipliers
    convergence_multiplier: float = 0.5  # Reduce penalty for convergence
    moderate_multiplier: float = 1.0  # Normal penalty
    high_dispersion_multiplier: float = 1.5  # Increase penalty
    extreme_dispersion_multiplier: float = 2.0  # Strong penalty

    # Non-linear scaling factors for extreme cases
    extreme_shape_factor: float = 1.8  # Exponential scaling
    bimodal_penalty_boost: float = 1.3  # Additional penalty for bimodal


@dataclass
class ScoringMetrics:
    """Computed scoring metrics for analysis."""

    mean: float
    variance: float
    std_dev: float
    coefficient_variation: float
    dispersion_index: float
    normalized_std: float
    scenario_type: str  # "convergence", "moderate", "high_dispersion", "extreme_dispersion"
    shape_classification: str  # "uniform", "clustered", "bimodal", "dispersed"


class AdaptiveMesoScoring:
    """
    Adaptive scoring mechanism for meso-level cluster aggregation.

    This class implements mathematically-sound, adaptive penalty mechanisms
    that are sensitive to different dispersion and convergence scenarios.
    """

    def __init__(self, config: AdaptiveScoringConfig | None = None) -> None:
        """
        Initialize adaptive scoring.

        Args:
            config: Optional configuration (uses defaults if not provided)
        """
        self.config = config or AdaptiveScoringConfig()

    def compute_metrics(self, scores: list[float]) -> ScoringMetrics:
        """
        Compute comprehensive scoring metrics.

        Args:
            scores: List of policy area scores [0-3]

        Returns:
            ScoringMetrics with all computed values
        """
        if not scores:
            raise ValueError("Empty scores list")

        n = len(scores)

        # Basic statistics
        mean = sum(scores) / n
        variance = sum((s - mean) ** 2 for s in scores) / n
        std_dev = variance**0.5

        # Coefficient of variation (relative dispersion)
        cv = std_dev / mean if mean > 0 else 0.0

        # Dispersion index (normalized range)
        score_range = max(scores) - min(scores) if scores else 0.0
        dispersion_index = score_range / self.config.max_score

        # Normalized standard deviation
        normalized_std = std_dev / self.config.max_score

        # Classify scenario type based on CV and DI
        if (
            cv < self.config.convergence_cv_threshold
            and dispersion_index < self.config.convergence_di_threshold
        ):
            scenario_type = "convergence"
        elif cv < self.config.high_dispersion_cv_threshold:
            scenario_type = "moderate"
        elif cv < self.config.extreme_dispersion_cv_threshold:
            scenario_type = "high_dispersion"
        else:
            scenario_type = "extreme_dispersion"

        # Classify shape
        shape_classification = self._classify_distribution_shape(scores, mean, std_dev)

        return ScoringMetrics(
            mean=mean,
            variance=variance,
            std_dev=std_dev,
            coefficient_variation=cv,
            dispersion_index=dispersion_index,
            normalized_std=normalized_std,
            scenario_type=scenario_type,
            shape_classification=shape_classification,
        )

    def _classify_distribution_shape(self, scores: list[float], mean: float, std_dev: float) -> str:
        """
        Classify the distribution shape of scores.

        Classifications:
        - uniform: Scores evenly distributed
        - clustered: Scores tightly grouped
        - bimodal: Two distinct clusters
        - dispersed: Wide spread of scores

        Args:
            scores: List of scores
            mean: Mean of scores
            std_dev: Standard deviation

        Returns:
            Shape classification string
        """
        if len(scores) < 3:
            return "insufficient_data"

        # Check for clustering
        within_1std = sum(1 for s in scores if abs(s - mean) <= std_dev)
        clustering_ratio = within_1std / len(scores)

        if clustering_ratio > 0.85:
            return "clustered"

        # Check for bimodal pattern
        sorted_scores = sorted(scores)
        n = len(sorted_scores)

        # Detect gap in middle
        if n >= 4:
            midpoint = n // 2
            gap_size = sorted_scores[midpoint] - sorted_scores[midpoint - 1]
            avg_gap = (max(scores) - min(scores)) / (n - 1) if n > 1 else 0

            if gap_size > 2 * avg_gap:
                return "bimodal"

        # Check for uniform distribution
        gaps = [sorted_scores[i + 1] - sorted_scores[i] for i in range(n - 1)]
        if gaps:
            gap_variance = sum((g - sum(gaps) / len(gaps)) ** 2 for g in gaps) / len(gaps)
            if gap_variance < 0.1:
                return "uniform"

        return "dispersed"

    def compute_adaptive_penalty_factor(
        self, metrics: ScoringMetrics
    ) -> tuple[float, dict[str, Any]]:
        """
        Compute adaptive penalty factor based on scenario characteristics.

        This is the core improvement over the fixed PENALTY_WEIGHT=0.3 approach.

        Algorithm:
        1. Determine sensitivity multiplier based on scenario type
        2. Apply shape-based adjustments for extreme cases
        3. Compute non-linear penalty for high dispersion
        4. Return penalty factor bounded to [0, 1]

        Args:
            metrics: ScoringMetrics from compute_metrics

        Returns:
            Tuple of (penalty_factor, computation_details)
        """
        # Step 1: Determine base penalty from normalized std
        base_penalty = metrics.normalized_std * self.config.base_penalty_weight

        # Step 2: Select sensitivity multiplier based on scenario
        if metrics.scenario_type == "convergence":
            sensitivity_multiplier = self.config.convergence_multiplier
        elif metrics.scenario_type == "moderate":
            sensitivity_multiplier = self.config.moderate_multiplier
        elif metrics.scenario_type == "high_dispersion":
            sensitivity_multiplier = self.config.high_dispersion_multiplier
        else:  # extreme_dispersion
            sensitivity_multiplier = self.config.extreme_dispersion_multiplier

        # Step 3: Apply shape-based adjustments
        shape_factor = 1.0

        if metrics.shape_classification == "bimodal":
            # Bimodal distributions indicate policy inconsistency - add penalty
            shape_factor = self.config.bimodal_penalty_boost
        elif metrics.scenario_type == "extreme_dispersion":
            # Apply non-linear scaling for extreme cases
            # Use exponential scaling: factor = 1 + (DI ^ extreme_shape_factor)
            shape_factor = 1.0 + (metrics.dispersion_index**self.config.extreme_shape_factor)
        elif metrics.dispersion_index > 0.7:
            # Moderate non-linear scaling for high dispersion
            shape_factor = 1.0 + (0.3 * metrics.dispersion_index)

        # Step 4: Compute final penalty strength
        penalty_strength = base_penalty * sensitivity_multiplier * shape_factor

        # Step 5: Compute penalty factor (bounded to [0, 1])
        # Ensure we don't go below 0.5 (max 50% penalty) for stability
        penalty_factor = max(0.5, min(1.0, 1.0 - penalty_strength))

        # Computation details for transparency
        details = {
            "base_penalty": base_penalty,
            "sensitivity_multiplier": sensitivity_multiplier,
            "shape_factor": shape_factor,
            "penalty_strength": penalty_strength,
            "penalty_factor": penalty_factor,
            "scenario_type": metrics.scenario_type,
            "shape_classification": metrics.shape_classification,
            "bounded_to_min": penalty_factor == 0.5,
            "bounded_to_max": penalty_factor == 1.0,
        }

        return penalty_factor, details

    def compute_adjusted_score(
        self, scores: list[float], weights: list[float] | None = None
    ) -> tuple[float, dict[str, Any]]:
        """
        Compute adjusted cluster score with adaptive penalties.

        This is the main entry point that replaces the current ClusterAggregator
        scoring logic with adaptive mechanisms.

        Args:
            scores: List of policy area scores [0-3]
            weights: Optional weights (defaults to equal weights)

        Returns:
            Tuple of (adjusted_score, computation_details)

        Raises:
            ValueError: If inputs are invalid
        """
        if not scores:
            raise ValueError("Empty scores list")

        # Validate and set weights
        if weights is None:
            weights = [1.0 / len(scores)] * len(scores)

        if len(weights) != len(scores):
            raise ValueError(f"Weight length mismatch: {len(weights)} != {len(scores)}")

        weight_sum = sum(weights)
        if abs(weight_sum - 1.0) > 1e-6:
            raise ValueError(f"Weights don't sum to 1.0: {weight_sum:.6f}")

        # Compute weighted score
        weighted_score = sum(s * w for s, w in zip(scores, weights, strict=True))

        # Compute metrics
        metrics = self.compute_metrics(scores)

        # Compute adaptive penalty factor
        penalty_factor, penalty_details = self.compute_adaptive_penalty_factor(metrics)

        # Apply penalty
        adjusted_score = weighted_score * penalty_factor

        # Compute coherence (for compatibility with existing code)
        if len(scores) <= 1:
            coherence = 1.0
        else:
            coherence = max(0.0, 1.0 - metrics.normalized_std)

        # Full computation details
        details = {
            "scores": scores,
            "weights": weights,
            "weighted_score": weighted_score,
            "metrics": {
                "mean": metrics.mean,
                "variance": metrics.variance,
                "std_dev": metrics.std_dev,
                "cv": metrics.coefficient_variation,
                "dispersion_index": metrics.dispersion_index,
                "normalized_std": metrics.normalized_std,
                "scenario_type": metrics.scenario_type,
                "shape_classification": metrics.shape_classification,
            },
            "penalty_computation": penalty_details,
            "adjusted_score": adjusted_score,
            "coherence": coherence,
            "improvement_over_fixed": self._compute_improvement_metric(
                weighted_score, adjusted_score, metrics
            ),
        }

        logger.debug(
            f"Adaptive scoring: weighted={weighted_score:.4f}, "
            f"penalty_factor={penalty_factor:.4f}, adjusted={adjusted_score:.4f}, "
            f"scenario={metrics.scenario_type}"
        )

        return adjusted_score, details

    def _compute_improvement_metric(
        self, weighted_score: float, adjusted_score: float, metrics: ScoringMetrics
    ) -> dict[str, Any]:
        """
        Compute improvement metric vs fixed penalty approach.

        Args:
            weighted_score: Base weighted score
            adjusted_score: Adjusted score with adaptive penalty
            metrics: Scoring metrics

        Returns:
            Dictionary with improvement analysis
        """
        # Compute what the old fixed approach would have done
        old_penalty_factor = 1.0 - (metrics.normalized_std * 0.3)
        old_adjusted_score = weighted_score * old_penalty_factor

        # Compare
        score_difference = adjusted_score - old_adjusted_score
        penalty_difference = (1.0 - old_penalty_factor) - (
            1.0 - (adjusted_score / weighted_score if weighted_score > 0 else 0)
        )

        return {
            "old_fixed_approach": {
                "penalty_factor": old_penalty_factor,
                "adjusted_score": old_adjusted_score,
            },
            "new_adaptive_approach": {
                "penalty_factor": adjusted_score / weighted_score if weighted_score > 0 else 0,
                "adjusted_score": adjusted_score,
            },
            "score_difference": score_difference,
            "penalty_difference": penalty_difference,
            "is_more_lenient": score_difference > 0.01,
            "is_stricter": score_difference < -0.01,
        }

    def get_sensitivity_analysis(
        self, scores: list[float], weights: list[float] | None = None
    ) -> dict[str, Any]:
        """
        Perform sensitivity analysis for a given score set.

        This method provides detailed analysis of how the adaptive mechanism
        responds to the specific scenario characteristics.

        Args:
            scores: List of policy area scores
            weights: Optional weights

        Returns:
            Dictionary with comprehensive sensitivity analysis
        """
        adjusted_score, details = self.compute_adjusted_score(scores, weights)

        # Test variations to show sensitivity
        metrics = self.compute_metrics(scores)

        # Analyze sensitivity to small perturbations
        perturbations = []
        for i, score in enumerate(scores):
            for delta in [-0.2, -0.1, 0.1, 0.2]:
                if 0 <= score + delta <= self.config.max_score:
                    perturbed = scores.copy()
                    perturbed[i] = score + delta
                    perturbed_score, _ = self.compute_adjusted_score(perturbed, weights)
                    perturbations.append(
                        {
                            "position": i,
                            "delta": delta,
                            "original_score": score,
                            "perturbed_score": perturbed_score,
                            "impact": perturbed_score - adjusted_score,
                        }
                    )

        return {
            "base_analysis": details,
            "sensitivity_to_perturbations": {
                "max_positive_impact": max((p["impact"] for p in perturbations), default=0),
                "max_negative_impact": min((p["impact"] for p in perturbations), default=0),
                "avg_abs_impact": (
                    sum(abs(p["impact"]) for p in perturbations) / len(perturbations)
                    if perturbations
                    else 0
                ),
                "perturbations": perturbations[:5],  # Sample
            },
            "robustness_metrics": {
                "scenario_stability": (
                    "stable" if metrics.coefficient_variation < 0.3 else "unstable"
                ),
                "penalty_proportionality": details["penalty_computation"]["penalty_strength"],
                "adaptive_advantage": details["improvement_over_fixed"]["score_difference"],
            },
        }


def create_adaptive_scorer(
    base_penalty_weight: float = 0.35, extreme_shape_factor: float = 1.8
) -> AdaptiveMesoScoring:
    """
    Factory function to create AdaptiveMesoScoring instance.

    Args:
        base_penalty_weight: Base penalty weight (default 0.35, slightly higher than old 0.3)
        extreme_shape_factor: Non-linear scaling factor for extreme cases

    Returns:
        Configured AdaptiveMesoScoring instance
    """
    config = AdaptiveScoringConfig(
        base_penalty_weight=base_penalty_weight, extreme_shape_factor=extreme_shape_factor
    )
    return AdaptiveMesoScoring(config)
