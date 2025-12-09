"""
Bayesian Uncertainty Quantification for Aggregation

This module implements rigorous uncertainty propagation for the aggregation pipeline.
It provides confidence intervals, epistemic/aleatoric decomposition, and sensitivity analysis.

Methods:
- Bootstrap resampling for empirical confidence intervals
- Bayesian error propagation for weighted averages
- Variance decomposition (epistemic vs aleatoric uncertainty)
- Monte Carlo sampling for non-linear aggregations

References:
- Efron, B. (1979). "Bootstrap methods: another look at the jackknife"
- Saltelli, A. et al. (2020). "Five ways to ensure that models serve society"
- Kendall, A. & Gal, Y. (2017). "What uncertainties do we need in Bayesian deep learning?"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UncertaintyMetrics:
    """
    Comprehensive uncertainty metrics for a score.
    
    Attributes:
        mean: Point estimate (expected value)
        std: Standard deviation
        variance: Variance
        confidence_interval_95: 95% CI tuple (lower, upper)
        confidence_interval_99: 99% CI tuple (lower, upper)
        epistemic_uncertainty: Model uncertainty (reducible with more data)
        aleatoric_uncertainty: Inherent data noise (irreducible)
        coefficient_of_variation: std/mean (relative uncertainty)
        skewness: Distribution asymmetry
        kurtosis: Distribution tail heaviness
        metadata: Additional diagnostic information
    """
    mean: float
    std: float
    variance: float
    confidence_interval_95: tuple[float, float]
    confidence_interval_99: tuple[float, float]
    epistemic_uncertainty: float
    aleatoric_uncertainty: float
    coefficient_of_variation: float
    skewness: float
    kurtosis: float
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def is_high_uncertainty(self, threshold: float = 0.3) -> bool:
        """Check if coefficient of variation exceeds threshold."""
        return self.coefficient_of_variation > threshold
    
    def dominant_uncertainty_type(self) -> str:
        """Identify whether epistemic or aleatoric dominates."""
        if self.epistemic_uncertainty > self.aleatoric_uncertainty * 1.2:
            return "epistemic"
        elif self.aleatoric_uncertainty > self.epistemic_uncertainty * 1.2:
            return "aleatoric"
        else:
            return "balanced"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "mean": self.mean,
            "std": self.std,
            "variance": self.variance,
            "confidence_interval_95": self.confidence_interval_95,
            "confidence_interval_99": self.confidence_interval_99,
            "epistemic_uncertainty": self.epistemic_uncertainty,
            "aleatoric_uncertainty": self.aleatoric_uncertainty,
            "coefficient_of_variation": self.coefficient_of_variation,
            "skewness": self.skewness,
            "kurtosis": self.kurtosis,
            "is_high_uncertainty": self.is_high_uncertainty(),
            "dominant_uncertainty": self.dominant_uncertainty_type(),
            "metadata": self.metadata,
        }


class BootstrapAggregator:
    """
    Bootstrap resampling for uncertainty quantification in aggregation.
    
    Bootstrap is a non-parametric method that works for any aggregation function,
    including non-linear operations like Choquet integrals.
    """
    
    def __init__(self, n_samples: int = 1000, random_seed: int = 42):
        """
        Initialize bootstrap aggregator.
        
        Args:
            n_samples: Number of bootstrap resamples
            random_seed: Fixed seed for reproducibility
        """
        self.n_samples = n_samples
        self.rng = np.random.RandomState(random_seed)
        logger.info(f"BootstrapAggregator initialized (n_samples={n_samples}, seed={random_seed})")
    
    def bootstrap_weighted_average(
        self,
        scores: list[float],
        weights: list[float] | None = None,
    ) -> UncertaintyMetrics:
        """
        Compute weighted average with bootstrap confidence intervals.
        
        Args:
            scores: List of input scores
            weights: Optional weights (default: uniform)
        
        Returns:
            UncertaintyMetrics with full uncertainty decomposition
        
        Raises:
            ValueError: If scores is empty or weights mismatch
        """
        if not scores:
            raise ValueError("Cannot bootstrap empty score list")
        
        scores_arr = np.array(scores, dtype=np.float64)
        n = len(scores_arr)
        
        if weights is None:
            weights_arr = np.ones(n) / n
        else:
            if len(weights) != n:
                raise ValueError(f"Weight count {len(weights)} != score count {n}")
            weights_arr = np.array(weights, dtype=np.float64)
            weights_arr = weights_arr / np.sum(weights_arr)  # Normalize
        
        # Bootstrap resampling
        resamples = np.zeros(self.n_samples)
        for i in range(self.n_samples):
            # Sample with replacement
            indices = self.rng.choice(n, size=n, replace=True)
            resample_scores = scores_arr[indices]
            resample_weights = weights_arr[indices]
            resample_weights = resample_weights / np.sum(resample_weights)
            
            resamples[i] = np.sum(resample_scores * resample_weights)
        
        # Compute statistics
        mean = np.mean(resamples)
        std = np.std(resamples, ddof=1)
        variance = std ** 2
        
        # Confidence intervals (percentile method)
        ci_95_lower = np.percentile(resamples, 2.5)
        ci_95_upper = np.percentile(resamples, 97.5)
        ci_99_lower = np.percentile(resamples, 0.5)
        ci_99_upper = np.percentile(resamples, 99.5)
        
        # Uncertainty decomposition
        # Epistemic: Uncertainty in the aggregation (reducible with more samples)
        epistemic_uncertainty = std
        
        # Aleatoric: Inherent variability in data (irreducible)
        aleatoric_uncertainty = np.std(scores_arr, ddof=1)
        
        # Coefficient of variation
        cv = std / mean if mean != 0.0 else float('inf')
        
        # Distribution shape
        skewness = stats.skew(resamples)
        kurtosis = stats.kurtosis(resamples)
        
        logger.debug(
            f"Bootstrap complete: mean={mean:.4f}, std={std:.4f}, "
            f"CI95=[{ci_95_lower:.4f}, {ci_95_upper:.4f}]"
        )
        
        return UncertaintyMetrics(
            mean=float(mean),
            std=float(std),
            variance=float(variance),
            confidence_interval_95=(float(ci_95_lower), float(ci_95_upper)),
            confidence_interval_99=(float(ci_99_lower), float(ci_99_upper)),
            epistemic_uncertainty=float(epistemic_uncertainty),
            aleatoric_uncertainty=float(aleatoric_uncertainty),
            coefficient_of_variation=float(cv),
            skewness=float(skewness),
            kurtosis=float(kurtosis),
            metadata={
                "n_scores": n,
                "n_bootstrap_samples": self.n_samples,
                "original_scores_mean": float(np.mean(scores_arr)),
                "original_scores_std": float(np.std(scores_arr, ddof=1)),
            },
        )


class BayesianPropagation:
    """
    Bayesian error propagation for analytical uncertainty quantification.
    
    For linear aggregations (weighted averages), we can compute uncertainty
    analytically without Monte Carlo sampling.
    """
    
    @staticmethod
    def propagate_weighted_average(
        scores: list[float],
        score_uncertainties: list[float],
        weights: list[float] | None = None,
    ) -> tuple[float, float]:
        """
        Analytical uncertainty propagation for weighted average.
        
        Formula:
            If Y = Σ w_i * X_i, then
            Var(Y) = Σ (w_i^2 * Var(X_i))  [assuming independence]
        
        Args:
            scores: List of score means
            score_uncertainties: List of score standard deviations
            weights: Optional weights (default: uniform)
        
        Returns:
            Tuple of (mean, std) for aggregated score
        
        Raises:
            ValueError: If input lists have mismatched lengths
        """
        n = len(scores)
        if len(score_uncertainties) != n:
            raise ValueError(
                f"Score count {n} != uncertainty count {len(score_uncertainties)}"
            )
        
        scores_arr = np.array(scores, dtype=np.float64)
        uncertainties_arr = np.array(score_uncertainties, dtype=np.float64)
        
        if weights is None:
            weights_arr = np.ones(n) / n
        else:
            if len(weights) != n:
                raise ValueError(f"Weight count {len(weights)} != score count {n}")
            weights_arr = np.array(weights, dtype=np.float64)
            weights_arr = weights_arr / np.sum(weights_arr)
        
        # Mean propagation
        mean = np.sum(weights_arr * scores_arr)
        
        # Variance propagation (assuming independence)
        variance = np.sum((weights_arr ** 2) * (uncertainties_arr ** 2))
        std = np.sqrt(variance)
        
        logger.debug(
            f"Bayesian propagation: mean={mean:.4f}, std={std:.4f} "
            f"(from {n} inputs)"
        )
        
        return float(mean), float(std)


class SensitivityAnalysis:
    """
    Sensitivity analysis for identifying influential inputs.
    
    Implements variance-based sensitivity analysis (Sobol indices) to quantify
    the contribution of each input to output variance.
    """
    
    @staticmethod
    def compute_sobol_indices(
        scores: list[float],
        weights: list[float],
        aggregation_func: callable = None,
        n_samples: int = 1000,
        random_seed: int = 42,
    ) -> dict[int, float]:
        """
        Compute first-order Sobol indices for weighted average.
        
        Sobol index S_i measures the fraction of output variance due to input i.
        
        Args:
            scores: Input scores
            weights: Input weights
            aggregation_func: Aggregation function (default: weighted average)
            n_samples: Monte Carlo samples for estimation
            random_seed: Reproducibility seed
        
        Returns:
            Dictionary mapping input index to Sobol index
        
        Note:
            For weighted average, Sobol index is proportional to weight^2 * var(score_i).
        """
        if aggregation_func is None:
            # Default: weighted average
            def aggregation_func(s, w):
                return np.sum(np.array(s) * np.array(w))
        
        n = len(scores)
        scores_arr = np.array(scores, dtype=np.float64)
        weights_arr = np.array(weights, dtype=np.float64)
        weights_arr = weights_arr / np.sum(weights_arr)
        
        rng = np.random.RandomState(random_seed)
        
        # Baseline output variance
        baseline_output = aggregation_func(scores_arr, weights_arr)
        
        # Perturb each input and measure output variance
        sobol_indices = {}
        for i in range(n):
            # Monte Carlo: sample score_i from distribution, hold others fixed
            perturbed_outputs = []
            for _ in range(n_samples):
                perturbed_scores = scores_arr.copy()
                # Perturb score_i (assume ±20% noise)
                noise = rng.normal(0, 0.2 * abs(scores_arr[i]))
                perturbed_scores[i] = scores_arr[i] + noise
                
                perturbed_output = aggregation_func(perturbed_scores, weights_arr)
                perturbed_outputs.append(perturbed_output)
            
            # Sobol index = Var(E[Y|X_i]) / Var(Y)
            # Approximated by: Var of perturbed outputs
            variance_due_to_i = np.var(perturbed_outputs, ddof=1)
            sobol_indices[i] = float(variance_due_to_i)
        
        # Normalize so sum = 1.0
        total_variance = sum(sobol_indices.values())
        if total_variance > 0:
            sobol_indices = {k: v / total_variance for k, v in sobol_indices.items()}
        
        logger.debug(f"Sobol indices: {sobol_indices}")
        return sobol_indices


def aggregate_with_uncertainty(
    scores: list[float],
    weights: list[float] | None = None,
    n_bootstrap: int = 1000,
    random_seed: int = 42,
) -> tuple[float, UncertaintyMetrics]:
    """
    Convenience function: Aggregate scores with full uncertainty quantification.
    
    Args:
        scores: Input scores
        weights: Optional weights (default: uniform)
        n_bootstrap: Number of bootstrap samples
        random_seed: Reproducibility seed
    
    Returns:
        Tuple of (point_estimate, uncertainty_metrics)
    """
    bootstrapper = BootstrapAggregator(n_samples=n_bootstrap, random_seed=random_seed)
    uncertainty = bootstrapper.bootstrap_weighted_average(scores, weights)
    
    # Point estimate: use mean from bootstrap
    point_estimate = uncertainty.mean
    
    return point_estimate, uncertainty


__all__ = [
    "UncertaintyMetrics",
    "BootstrapAggregator",
    "BayesianPropagation",
    "SensitivityAnalysis",
    "aggregate_with_uncertainty",
]
