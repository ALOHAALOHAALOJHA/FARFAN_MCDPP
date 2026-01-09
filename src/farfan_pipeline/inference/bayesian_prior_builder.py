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
        self, evidence_type: Literal["straw_in_wind", "hoop", "smoking_gun", "doubly_decisive"], rarity: float = 0.5
    ) -> PriorParameters:
        """
        Build prior based on Beach's evidential test types.

        Args:
            evidence_type: Type of process tracing test
            rarity: Evidence rarity score (0=common, 1=rare)

        Returns:
            PriorParameters with appropriate distribution and parameters

        Beach's Test Types:
            - Straw-in-wind: Weak confirmation (α≈1.5, β≈1.5)
            - Hoop test: Necessary but not sufficient (α≈2, β≈1)
            - Smoking gun: Sufficient but not necessary (α≈1, β≈2)
            - Doubly decisive: Necessary and sufficient (α≈3, β≈3)
        """
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
        self, group_sizes: list[int], overall_alpha: float = 2.0, overall_beta: float = 2.0
    ) -> HierarchicalPrior:
        """
        Build hierarchical prior for multi-level analysis (micro-meso-macro).

        Implements hierarchical Bayesian model for nested causal structures:
        - Population level: Overall prior for all groups
        - Group level: Priors for each causal mechanism level

        Args:
            group_sizes: Number of observations per group
            overall_alpha: Population-level alpha parameter
            overall_beta: Population-level beta parameter

        Returns:
            HierarchicalPrior with population and group-level parameters

        Example:
            # Three-level hierarchy: micro, meso, macro
            prior = builder.build_hierarchical_prior([10, 20, 30])
            # Returns hierarchical prior with 3 groups
        """
        n_groups = len(group_sizes)

        if n_groups == 0:
            self.logger.warning("No groups specified for hierarchical prior")
            return HierarchicalPrior(
                population_alpha=overall_alpha, population_beta=overall_beta, n_groups=0
            )

        # Distribute population prior across groups
        # Each group gets fraction of population concentration
        group_priors = []
        for i, size in enumerate(group_sizes):
            # Weight by group size (larger groups get more concentrated priors)
            total_size = sum(group_sizes)
            weight = size / total_size if total_size > 0 else 1.0 / n_groups

            group_alpha = overall_alpha * weight
            group_beta = overall_beta * weight

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
        Build adaptive prior from historical data.

        Uses empirical Bayes approach to construct data-driven priors.
        Useful for self-reflective learning from past analyses.

        Args:
            historical_data: Previous posterior estimates
            confidence: Confidence in historical data (0=ignore, 1=full weight)

        Returns:
            PriorParameters learned from historical data

        Notes:
            If no historical data, returns default weakly informative prior.
        """
        if historical_data is None or len(historical_data) == 0:
            self.logger.info("No historical data, using default prior")
            return PriorParameters(
                distribution="beta",
                alpha=self.default_alpha,
                beta=self.default_beta,
                metadata={"adaptive": False, "source": "default"},
            )

        # Convert to numpy array
        data = np.asarray(historical_data, dtype=np.float64)

        # Estimate Beta parameters using method of moments
        mean = float(np.mean(data))
        var = float(np.var(data, ddof=1) if len(data) > 1 else 0.01)

        # Method of moments for Beta distribution
        # mean = alpha / (alpha + beta)
        # var = (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))
        if var > 0 and 0 < mean < 1:
            common = mean * (1 - mean) / var - 1
            alpha_empirical = mean * common
            beta_empirical = (1 - mean) * common

            # Adjust by confidence (blend with default prior)
            alpha_final = confidence * alpha_empirical + (1 - confidence) * self.default_alpha
            beta_final = confidence * beta_empirical + (1 - confidence) * self.default_beta
        else:
            # Fallback if variance too small or mean out of bounds
            alpha_final = self.default_alpha
            beta_final = self.default_beta

        prior = PriorParameters(
            distribution="beta",
            alpha=float(alpha_final),
            beta=float(beta_final),
            metadata={
                "adaptive": True,
                "source": "empirical_bayes",
                "n_observations": len(data),
                "historical_mean": float(mean),
                "historical_var": float(var),
                "confidence": float(confidence),
            },
        )

        self.logger.info(
            f"Built adaptive prior from {len(data)} observations: "
            f"Beta({alpha_final:.2f}, {beta_final:.2f})"
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
