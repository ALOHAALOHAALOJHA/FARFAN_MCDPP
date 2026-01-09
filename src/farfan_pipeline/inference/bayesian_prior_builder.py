"""
Bayesian Prior Builder (AGUJA I)
=================================

Adaptive prior construction based on evidence strength and type.

This module implements Beach's (2017, 2024) test-specific priors for process tracing:
- Straw-in-wind: Weak, diffuse priors
- Hoop test: Priors favoring necessity
- Smoking gun: Priors favoring sufficiency
- Doubly decisive: Strong, concentrated priors

Phase 2 SOTA Enhancement - 2026-01-07

Theoretical Foundation:
    Beach, D. (2017). Process-Tracing Methods in Social Science.
    Beach, D., & Pedersen, R. B. (2024). Bayesian Process Tracing.
    Gelman, A. (2006). Prior distributions for variance parameters.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray


@dataclass
class PriorParameters:
    """Container for Bayesian prior parameters"""

    distribution: Literal["beta", "normal", "gamma", "uniform"] = "beta"
    alpha: float = 1.0
    beta: float = 1.0
    mu: float = 0.0
    sigma: float = 1.0
    lower: float = 0.0
    upper: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HierarchicalPrior:
    """Hierarchical prior specification for multi-level analysis"""

    population_alpha: float = 2.0
    population_beta: float = 2.0
    group_priors: list[PriorParameters] = field(default_factory=list)
    n_groups: int = 0


class BayesianPriorBuilder:
    """
    Constructs adaptive Bayesian priors based on evidence characteristics.

    This class implements Beach's test-specific priors for process tracing,
    adjusting for evidence rarity and hierarchical structure.

    Attributes:
        config: Configuration object with Bayesian thresholds
        logger: Logger instance
        default_alpha: Default alpha for Beta priors
        default_beta: Default beta for Beta priors
    """

    def __init__(self, config: Any):
        """
        Initialize Bayesian Prior Builder.

        Args:
            config: Configuration object with get() method for Bayesian thresholds
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        # Load default prior parameters from config
        bayesian_thresholds = getattr(config, "bayesian_thresholds", {})
        if hasattr(bayesian_thresholds, "prior_alpha"):
            self.default_alpha = float(bayesian_thresholds.prior_alpha)
        else:
            self.default_alpha = float(config.get("bayesian_thresholds.prior_alpha", 1.0))

        if hasattr(bayesian_thresholds, "prior_beta"):
            self.default_beta = float(bayesian_thresholds.prior_beta)
        else:
            self.default_beta = float(config.get("bayesian_thresholds.prior_beta", 1.0))

        self.logger.info(
            f"BayesianPriorBuilder initialized with defaults: "
            f"alpha={self.default_alpha:.2f}, beta={self.default_beta:.2f}"
        )

    def build_prior_for_evidence_type(
        self,
        evidence_type: Literal["straw_in_wind", "hoop", "smoking_gun", "doubly_decisive"],
        rarity: float = 0.5,
    ) -> PriorParameters:
        """
        Build prior based on Beach's evidential test types.

        Args:
            evidence_type: Type of process tracing test
            rarity: Evidence rarity score (0=common, 1=rare). Must be in [0, 1].

        Returns:
            PriorParameters with appropriate distribution and parameters

        Raises:
            ValueError: If rarity is outside [0, 1] bounds

        Beach's Test Types:
            - Straw-in-wind: Weak confirmation (α≈1.5, β≈1.5)
            - Hoop test: Necessary but not sufficient (α≈2, β≈1)
            - Smoking gun: Sufficient but not necessary (α≈1, β≈2)
            - Doubly decisive: Necessary and sufficient (α≈3, β≈3)
        """
        # RIGOROUS VALIDATION: Rarity must be bounded probability-like value
        if not isinstance(rarity, (int, float)):
            raise TypeError(f"rarity must be numeric, got {type(rarity).__name__}")
        if not np.isfinite(rarity):
            raise ValueError(f"rarity must be finite, got {rarity}")
        if not 0.0 <= rarity <= 1.0:
            raise ValueError(
                f"rarity must be in [0, 1] (0=common, 1=rare), got {rarity}"
            )

        # Base priors per Beach (2017, 2024)
        base_priors = {
            "straw_in_wind": PriorParameters(
                distribution="beta",
                alpha=1.5,
                beta=1.5,
                metadata={"test_type": "weak_confirmation", "certainty": "low"},
            ),
            "hoop": PriorParameters(
                distribution="beta",
                alpha=2.0,
                beta=1.0,
                metadata={"test_type": "necessity", "certainty": "medium"},
            ),
            "smoking_gun": PriorParameters(
                distribution="beta",
                alpha=1.0,
                beta=2.0,
                metadata={"test_type": "sufficiency", "certainty": "medium"},
            ),
            "doubly_decisive": PriorParameters(
                distribution="beta",
                alpha=3.0,
                beta=3.0,
                metadata={"test_type": "necessity_and_sufficiency", "certainty": "high"},
            ),
        }

        prior = base_priors.get(
            evidence_type,
            PriorParameters(
                distribution="beta",
                alpha=self.default_alpha,
                beta=self.default_beta,
                metadata={"test_type": "unknown"},
            ),
        )

        # Adjust for rarity (rare evidence = stronger prior concentration)
        # Rarity increases both alpha and beta, making prior more concentrated
        # Mathematical guarantee: rarity in [0,1] => factor in [1,2] => alpha,beta remain positive
        rarity_factor = 1.0 + rarity
        prior.alpha *= rarity_factor
        prior.beta *= rarity_factor

        prior.metadata["rarity"] = float(rarity)
        prior.metadata["rarity_adjusted"] = True

        self.logger.debug(
            f"Built prior for {evidence_type}: "
            f"Beta({prior.alpha:.2f}, {prior.beta:.2f}), rarity={rarity:.2f}"
        )

        return prior

    def build_hierarchical_prior(
        self,
        group_sizes: list[int],
        overall_alpha: float = 2.0,
        overall_beta: float = 2.0,
    ) -> HierarchicalPrior:
        """
        Build hierarchical prior for multi-level analysis (micro-meso-macro).

        Implements hierarchical Bayesian model for nested causal structures:
        - Population level: Overall prior for all groups
        - Group level: Priors for each causal mechanism level

        Args:
            group_sizes: Number of observations per group (must be non-negative)
            overall_alpha: Population-level alpha parameter (must be > 0)
            overall_beta: Population-level beta parameter (must be > 0)

        Returns:
            HierarchicalPrior with population and group-level parameters

        Raises:
            ValueError: If group_sizes contains negative values or alpha/beta <= 0

        Example:
            # Three-level hierarchy: micro, meso, macro
            prior = builder.build_hierarchical_prior([10, 20, 30])
            # Returns hierarchical prior with 3 groups
        """
        # RIGOROUS VALIDATION: Population parameters must be positive for Beta
        if not isinstance(overall_alpha, (int, float)) or not np.isfinite(overall_alpha):
            raise TypeError(f"overall_alpha must be finite numeric, got {overall_alpha}")
        if not isinstance(overall_beta, (int, float)) or not np.isfinite(overall_beta):
            raise TypeError(f"overall_beta must be finite numeric, got {overall_beta}")
        if overall_alpha <= 0:
            raise ValueError(
                f"overall_alpha must be > 0 for valid Beta distribution, got {overall_alpha}"
            )
        if overall_beta <= 0:
            raise ValueError(
                f"overall_beta must be > 0 for valid Beta distribution, got {overall_beta}"
            )

        n_groups = len(group_sizes)

        if n_groups == 0:
            self.logger.warning("No groups specified for hierarchical prior")
            return HierarchicalPrior(
                population_alpha=overall_alpha, population_beta=overall_beta, n_groups=0
            )

        # RIGOROUS VALIDATION: All group sizes must be non-negative integers
        for i, size in enumerate(group_sizes):
            if not isinstance(size, (int, np.integer)):
                raise TypeError(
                    f"group_sizes[{i}] must be integer, got {type(size).__name__}"
                )
            if size < 0:
                raise ValueError(
                    f"group_sizes[{i}] must be non-negative, got {size}"
                )

        # Compute total with guaranteed non-negative result
        total_size = sum(group_sizes)

        # CRITICAL FIX: Handle zero total size (all groups empty)
        # Use uniform weights when no observations exist
        if total_size == 0:
            self.logger.warning(
                "All group sizes are zero; using uniform weighting for hierarchical prior"
            )

        # Distribute population prior across groups
        # Each group gets fraction of population concentration
        group_priors = []
        for i, size in enumerate(group_sizes):
            # Weight by group size (larger groups get more concentrated priors)
            # Safe division: fallback to uniform weight when total_size == 0
            weight = size / total_size if total_size > 0 else 1.0 / n_groups

            # Ensure group parameters remain positive (minimum floor)
            # Mathematical guarantee: weight in [0, 1], overall_* > 0
            # But weighted alpha/beta can approach 0, so apply floor
            min_param = 0.01  # Minimum parameter to avoid degenerate priors
            group_alpha = max(overall_alpha * weight, min_param)
            group_beta = max(overall_beta * weight, min_param)

            group_prior = PriorParameters(
                distribution="beta",
                alpha=group_alpha,
                beta=group_beta,
                metadata={
                    "group_id": i,
                    "group_size": size,
                    "weight": weight,
                },
            )
            group_priors.append(group_prior)

        hierarchical_prior = HierarchicalPrior(
            population_alpha=overall_alpha,
            population_beta=overall_beta,
            group_priors=group_priors,
            n_groups=n_groups,
        )

        self.logger.info(
            f"Built hierarchical prior: {n_groups} groups, "
            f"population Beta({overall_alpha:.2f}, {overall_beta:.2f})"
        )

        return hierarchical_prior

    def build_adaptive_prior(
        self,
        historical_data: list[float] | NDArray[np.floating[Any]] | None = None,
        confidence: float = 0.5,
    ) -> PriorParameters:
        """
        Build adaptive prior from historical data using empirical Bayes.

        Uses method of moments to estimate Beta parameters from historical
        posterior estimates, with rigorous handling of edge cases.

        Args:
            historical_data: Previous posterior estimates (should be in [0, 1])
            confidence: Confidence in historical data (0=ignore, 1=full weight)

        Returns:
            PriorParameters learned from historical data

        Raises:
            ValueError: If confidence is outside [0, 1]

        Notes:
            - If no historical data, returns default weakly informative prior
            - NaN/Inf values are filtered from historical data
            - Values outside (0, 1) are clipped with warning
            - Method of moments failure falls back to default prior
        """
        # RIGOROUS VALIDATION: Confidence must be in [0, 1]
        if not isinstance(confidence, (int, float)):
            raise TypeError(f"confidence must be numeric, got {type(confidence).__name__}")
        if not np.isfinite(confidence):
            raise ValueError(f"confidence must be finite, got {confidence}")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                f"confidence must be in [0, 1], got {confidence}"
            )

        if historical_data is None or len(historical_data) == 0:
            self.logger.info("No historical data, using default prior")
            return PriorParameters(
                distribution="beta",
                alpha=self.default_alpha,
                beta=self.default_beta,
                metadata={"adaptive": False, "source": "default"},
            )

        # Convert to numpy array with rigorous cleaning
        data = np.asarray(historical_data, dtype=np.float64)

        # CRITICAL: Filter out NaN and Inf values
        finite_mask = np.isfinite(data)
        n_invalid = np.sum(~finite_mask)
        if n_invalid > 0:
            self.logger.warning(
                f"Filtered {n_invalid} non-finite values from historical data"
            )
            data = data[finite_mask]

        if len(data) == 0:
            self.logger.warning("All historical data was non-finite, using default prior")
            return PriorParameters(
                distribution="beta",
                alpha=self.default_alpha,
                beta=self.default_beta,
                metadata={"adaptive": False, "source": "default", "reason": "all_non_finite"},
            )

        # CRITICAL: Handle values outside (0, 1) for Beta distribution
        n_out_of_bounds = np.sum((data <= 0) | (data >= 1))
        if n_out_of_bounds > 0:
            self.logger.warning(
                f"{n_out_of_bounds} values outside (0, 1) clipped for Beta estimation"
            )
            # Clip to open interval (0, 1) - Beta is undefined at boundaries
            epsilon = 1e-6
            data = np.clip(data, epsilon, 1.0 - epsilon)

        # Estimate Beta parameters using method of moments
        mean = float(np.mean(data))
        # Use n-1 for unbiased variance, but handle n=1 case
        if len(data) > 1:
            var = float(np.var(data, ddof=1))
        else:
            # Single observation: use small default variance
            var = 0.01
            self.logger.debug("Single observation, using default variance 0.01")

        # Method of moments for Beta distribution
        # mean = alpha / (alpha + beta)
        # var = (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
        # Solving: common = mean * (1 - mean) / var - 1
        # alpha = mean * common, beta = (1 - mean) * common
        
        fallback_reason = None
        alpha_final = self.default_alpha
        beta_final = self.default_beta

        if var > 0 and 0 < mean < 1:
            common = mean * (1 - mean) / var - 1

            # CRITICAL FIX: Method of moments can produce negative parameters
            # This happens when var > mean * (1 - mean), i.e., overdispersion
            if common > 0:
                alpha_empirical = mean * common
                beta_empirical = (1 - mean) * common

                # Verify parameters are positive (mathematical guarantee if common > 0)
                if alpha_empirical > 0 and beta_empirical > 0:
                    # Blend with default prior using confidence weight
                    alpha_final = (
                        confidence * alpha_empirical
                        + (1 - confidence) * self.default_alpha
                    )
                    beta_final = (
                        confidence * beta_empirical
                        + (1 - confidence) * self.default_beta
                    )
                else:
                    fallback_reason = "computed_params_non_positive"
            else:
                # common <= 0 indicates overdispersion beyond Beta support
                fallback_reason = "overdispersion"
                self.logger.warning(
                    f"Historical data variance ({var:.4f}) exceeds Beta maximum "
                    f"({mean * (1 - mean):.4f}); using default prior"
                )
        elif var == 0:
            fallback_reason = "zero_variance"
            self.logger.debug("Zero variance in historical data, using default prior")
        else:
            fallback_reason = "mean_at_boundary"
            self.logger.debug(f"Mean at boundary ({mean}), using default prior")

        prior = PriorParameters(
            distribution="beta",
            alpha=float(alpha_final),
            beta=float(beta_final),
            metadata={
                "adaptive": fallback_reason is None,
                "source": "empirical_bayes" if fallback_reason is None else "default",
                "fallback_reason": fallback_reason,
                "n_observations": len(data),
                "n_filtered": int(n_invalid),
                "historical_mean": float(mean),
                "historical_var": float(var),
                "confidence": float(confidence),
            },
        )

        self.logger.info(
            f"Built adaptive prior from {len(data)} observations: "
            f"Beta({alpha_final:.2f}, {beta_final:.2f})"
            + (f" [fallback: {fallback_reason}]" if fallback_reason else "")
        )

        return prior

    def build_weakly_informative_prior(self, center: float = 0.5, concentration: float = 2.0) -> PriorParameters:
        """
        Build weakly informative prior (Gelman recommendation).

        Balances between uninformative (α=1, β=1) and strongly informative priors.
        Useful when little is known about the causal mechanism.

        Args:
            center: Prior mean (0-1)
            concentration: Total concentration (higher = more informative)

        Returns:
            PriorParameters for weakly informative Beta prior
        """
        if not 0 <= center <= 1:
            raise ValueError(f"Center must be in [0,1], got {center}")
        if concentration <= 0:
            raise ValueError(f"Concentration must be positive, got {concentration}")

        # Convert center and concentration to alpha, beta
        alpha = center * concentration
        beta = (1 - center) * concentration

        return PriorParameters(
            distribution="beta",
            alpha=float(alpha),
            beta=float(beta),
            metadata={
                "weakly_informative": True,
                "center": float(center),
                "concentration": float(concentration),
            },
        )

    def build_skeptical_prior(self, strength: float = 0.8) -> PriorParameters:
        """
        Build skeptical prior that disfavors causal links.

        Useful for conservative analysis where causal claims require strong evidence.

        Args:
            strength: Skepticism strength (0=neutral, 1=highly skeptical)

        Returns:
            PriorParameters biased toward null hypothesis
        """
        if not 0 <= strength <= 1:
            raise ValueError(f"Strength must be in [0,1], got {strength}")

        # Skeptical prior: β > α (favors low probabilities)
        alpha = 1.0
        beta = 1.0 + strength * 4.0  # β ranges from 1 to 5

        return PriorParameters(
            distribution="beta",
            alpha=float(alpha),
            beta=float(beta),
            metadata={
                "skeptical": True,
                "strength": float(strength),
                "bias": "null_hypothesis",
            },
        )

    def build_optimistic_prior(self, strength: float = 0.8) -> PriorParameters:
        """
        Build optimistic prior that favors causal links.

        Useful when theory strongly predicts causal relationship.

        Args:
            strength: Optimism strength (0=neutral, 1=highly optimistic)

        Returns:
            PriorParameters biased toward alternative hypothesis
        """
        if not 0 <= strength <= 1:
            raise ValueError(f"Strength must be in [0,1], got {strength}")

        # Optimistic prior: α > β (favors high probabilities)
        alpha = 1.0 + strength * 4.0  # α ranges from 1 to 5
        beta = 1.0

        return PriorParameters(
            distribution="beta",
            alpha=float(alpha),
            beta=float(beta),
            metadata={
                "optimistic": True,
                "strength": float(strength),
                "bias": "alternative_hypothesis",
            },
        )

    def get_prior_summary(self, prior: PriorParameters) -> dict[str, Any]:
        """
        Get summary statistics for prior distribution.

        Args:
            prior: PriorParameters to summarize

        Returns:
            Dictionary with mean, mode, variance, etc.
        """
        if prior.distribution == "beta":
            alpha, beta = prior.alpha, prior.beta
            total = alpha + beta

            mean = alpha / total
            if alpha > 1 and beta > 1:
                mode = (alpha - 1) / (total - 2)
            else:
                mode = None

            variance = (alpha * beta) / (total**2 * (total + 1))

            return {
                "distribution": "beta",
                "alpha": float(alpha),
                "beta": float(beta),
                "mean": float(mean),
                "mode": float(mode) if mode is not None else None,
                "variance": float(variance),
                "std": float(np.sqrt(variance)),
                "metadata": prior.metadata,
            }

        elif prior.distribution == "normal":
            return {
                "distribution": "normal",
                "mu": float(prior.mu),
                "sigma": float(prior.sigma),
                "mean": float(prior.mu),
                "variance": float(prior.sigma**2),
                "std": float(prior.sigma),
                "metadata": prior.metadata,
            }

        else:
            return {
                "distribution": prior.distribution,
                "parameters": {
                    "alpha": prior.alpha,
                    "beta": prior.beta,
                    "mu": prior.mu,
                    "sigma": prior.sigma,
                },
                "metadata": prior.metadata,
            }
