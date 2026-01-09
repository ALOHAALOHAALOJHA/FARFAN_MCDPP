"""
Bayesian Engine Adapter (F1.2 Refactoring)
===========================================

Unified interface for all Bayesian inference operations in the Derek Beach pipeline.

This adapter integrates:
- BayesianPriorBuilder (AGUJA I): Adaptive prior construction
- BayesianSamplingEngine (AGUJA II): MCMC sampling with diagnostics
- BayesianDiagnostics: Model validation and comparison

Phase 2 SOTA Enhancement - 2026-01-07

Architecture:
    This is the main entry point for all Bayesian operations. It provides a
    high-level interface that hides implementation details and provides
    consistent error handling, logging, and graceful degradation.

Integration Points:
    - derek_beach.py lines 66-71: REFACTORED_BAYESIAN_AVAILABLE check
    - derek_beach.py lines 4523-4530: BayesianMechanismInference initialization
    - derek_beach.py lines 4949-4951: Necessity testing

Theoretical Foundation:
    Beach, D., & Pedersen, R. B. (2024). Bayesian Process Tracing.
    Goertz & Mahoney (2012): A Tale of Two Cultures (Set theory + Bayesian).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np

from .bayesian_diagnostics import BayesianDiagnostics
from .bayesian_prior_builder import BayesianPriorBuilder, PriorParameters
from .bayesian_sampling_engine import BayesianSamplingEngine, SamplingResult

if TYPE_CHECKING:
    from numpy.typing import NDArray


class BayesianEngineAdapter:
    """
    Unified Bayesian inference adapter for Derek Beach process tracing.

    This class provides a high-level interface to all Bayesian operations,
    integrating prior construction, MCMC sampling, and model diagnostics.

    Attributes:
        config: Configuration object
        nlp: spaCy NLP model (optional, for future text-based priors)
        prior_builder: BayesianPriorBuilder instance (AGUJA I)
        sampling_engine: BayesianSamplingEngine instance (AGUJA II)
        diagnostics: BayesianDiagnostics instance
        logger: Logger instance
    """

    def __init__(self, config: Any, nlp_model: Any | None = None):
        """
        Initialize Bayesian Engine Adapter.

        Args:
            config: Configuration object with Bayesian thresholds
            nlp_model: Optional spaCy NLP model
        """
        self.config = config
        self.nlp = nlp_model
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize components
        try:
            self.prior_builder = BayesianPriorBuilder(config)
            self.sampling_engine = BayesianSamplingEngine(config)
            self.diagnostics = BayesianDiagnostics()

            self.logger.info("BayesianEngineAdapter initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing BayesianEngineAdapter: {e}")
            raise

    def is_available(self) -> bool:
        """
        Check if all Bayesian components are available.

        Returns:
            True if all components initialized successfully
        """
        return (
            self.prior_builder is not None
            and self.sampling_engine is not None
            and self.sampling_engine.is_available()
            and self.diagnostics is not None
        )

    def get_component_status(self) -> dict[str, str]:
        """
        Get status of all Bayesian components.

        Returns:
            Dictionary mapping component names to status strings
        """
        return {
            "prior_builder": "✓ disponible" if self.prior_builder else "✗ no disponible",
            "sampling_engine": "✓ disponible"
            if self.sampling_engine and self.sampling_engine.is_available()
            else "✗ no disponible",
            "diagnostics": "✓ disponible" if self.diagnostics and self.diagnostics.is_available() else "✗ no disponible",
            "overall": "✓ disponible" if self.is_available() else "✗ no disponible",
        }

    # ========================================================================
    # HIGH-LEVEL PROCESS TRACING METHODS
    # ========================================================================

    def test_necessity_from_observations(
        self, observations: list[float] | NDArray[np.floating[Any]], prior: dict[str, float] | None = None
    ) -> dict[str, Any]:
        """
        Test necessity condition using Bayesian inference.

        Implements Beach's hoop test: necessary but not sufficient condition.
        If evidence is absent, hypothesis fails (like failing to jump through hoop).

        Args:
            observations: List of binary observations (0/1) or success counts
            prior: Prior parameters {'alpha': float, 'beta': float}
                   If None, uses hoop test prior

        Returns:
            Dictionary with posterior statistics and necessity assessment

        Beach's Hoop Test:
            - Prior: Beta(2, 1) favors necessity
            - Updates with evidence
            - High posterior = necessary condition likely met
        """
        if prior is None:
            # Use hoop test prior (favors necessity)
            prior_params = self.prior_builder.build_prior_for_evidence_type("hoop", rarity=0.5)
            prior_alpha = prior_params.alpha
            prior_beta = prior_params.beta
        else:
            prior_alpha = float(prior.get("alpha", 1.0))
            prior_beta = float(prior.get("beta", 1.0))

        # Convert observations to successes/trials
        obs_array = np.asarray(observations, dtype=np.float64)
        n_successes = int(np.sum(obs_array))
        n_trials = len(obs_array)

        # Sample posterior
        result = self.sampling_engine.sample_beta_binomial(
            n_successes=n_successes, n_trials=n_trials, prior_alpha=prior_alpha, prior_beta=prior_beta
        )

        # Assess necessity: high posterior mean suggests necessary condition met
        necessity_threshold = 0.7  # Beach's threshold for necessity
        necessity_met = result.posterior_mean >= necessity_threshold

        return {
            "test_type": "necessity_hoop",
            "posterior_mean": result.posterior_mean,
            "hdi_95": result.hdi_95,
            "rhat": result.rhat,
            "converged": result.converged,
            "necessity_met": necessity_met,
            "necessity_threshold": necessity_threshold,
            "n_successes": n_successes,
            "n_trials": n_trials,
            "evidence_strength": "strong" if necessity_met else "weak",
        }

    def test_sufficiency_from_observations(
        self, observations: list[float] | NDArray[np.floating[Any]], prior: dict[str, float] | None = None
    ) -> dict[str, Any]:
        """
        Test sufficiency condition using Bayesian inference.

        Implements Beach's smoking gun test: sufficient but not necessary.
        If evidence is present, hypothesis is strongly confirmed.

        Args:
            observations: List of binary observations (0/1)
            prior: Prior parameters (if None, uses smoking gun prior)

        Returns:
            Dictionary with posterior statistics and sufficiency assessment

        Beach's Smoking Gun Test:
            - Prior: Beta(1, 2) favors sufficiency
            - Strong evidence if posterior is high
            - Presence of evidence confirms hypothesis
        """
        if prior is None:
            # Use smoking gun prior (favors sufficiency)
            prior_params = self.prior_builder.build_prior_for_evidence_type("smoking_gun", rarity=0.7)
            prior_alpha = prior_params.alpha
            prior_beta = prior_params.beta
        else:
            prior_alpha = float(prior.get("alpha", 1.0))
            prior_beta = float(prior.get("beta", 1.0))

        # Convert observations
        obs_array = np.asarray(observations, dtype=np.float64)
        n_successes = int(np.sum(obs_array))
        n_trials = len(obs_array)

        # Sample posterior
        result = self.sampling_engine.sample_beta_binomial(
            n_successes=n_successes, n_trials=n_trials, prior_alpha=prior_alpha, prior_beta=prior_beta
        )

        # Assess sufficiency: high posterior with rare evidence = strong confirmation
        sufficiency_threshold = 0.8  # Higher threshold for sufficiency
        sufficiency_met = result.posterior_mean >= sufficiency_threshold

        return {
            "test_type": "sufficiency_smoking_gun",
            "posterior_mean": result.posterior_mean,
            "hdi_95": result.hdi_95,
            "rhat": result.rhat,
            "converged": result.converged,
            "sufficiency_met": sufficiency_met,
            "sufficiency_threshold": sufficiency_threshold,
            "n_successes": n_successes,
            "n_trials": n_trials,
            "evidence_strength": "very_strong" if sufficiency_met else "moderate",
        }

    def test_doubly_decisive(
        self, observations: list[float] | NDArray[np.floating[Any]], prior: dict[str, float] | None = None
    ) -> dict[str, Any]:
        """
        Test both necessity and sufficiency (doubly decisive test).

        Beach's strongest evidential test: necessary AND sufficient.
        Passing this test provides very strong confirmation.

        Args:
            observations: List of binary observations (0/1)
            prior: Prior parameters (if None, uses doubly decisive prior)

        Returns:
            Dictionary with comprehensive test results

        Beach's Doubly Decisive Test:
            - Prior: Beta(3, 3) concentrated prior
            - Must meet both necessity and sufficiency criteria
            - Provides strongest possible confirmation
        """
        if prior is None:
            prior_params = self.prior_builder.build_prior_for_evidence_type("doubly_decisive", rarity=0.8)
            prior_alpha = prior_params.alpha
            prior_beta = prior_params.beta
        else:
            prior_alpha = float(prior.get("alpha", 1.0))
            prior_beta = float(prior.get("beta", 1.0))

        obs_array = np.asarray(observations, dtype=np.float64)
        n_successes = int(np.sum(obs_array))
        n_trials = len(obs_array)

        result = self.sampling_engine.sample_beta_binomial(
            n_successes=n_successes, n_trials=n_trials, prior_alpha=prior_alpha, prior_beta=prior_beta
        )

        # Doubly decisive requires very high posterior (> 0.9)
        decisive_threshold = 0.9
        test_passed = result.posterior_mean >= decisive_threshold

        return {
            "test_type": "doubly_decisive",
            "posterior_mean": result.posterior_mean,
            "hdi_95": result.hdi_95,
            "rhat": result.rhat,
            "converged": result.converged,
            "test_passed": test_passed,
            "decisive_threshold": decisive_threshold,
            "n_successes": n_successes,
            "n_trials": n_trials,
            "evidence_strength": "decisive" if test_passed else "inconclusive",
        }

    def update_prior_with_evidence(
        self, prior_alpha: float, prior_beta: float, evidence_count: int, success_count: int
    ) -> dict[str, float]:
        """
        Bayesian update with Beta-Binomial conjugacy.

        Performs incremental Bayesian updating for process tracing evidence accumulation.

        Args:
            prior_alpha: Prior alpha parameter
            prior_beta: Prior beta parameter
            evidence_count: Total number of observations
            success_count: Number of successes

        Returns:
            Dictionary with posterior parameters and statistics

        Conjugate Update:
            Posterior ~ Beta(alpha + successes, beta + failures)
        """
        posterior_alpha = prior_alpha + success_count
        posterior_beta = prior_beta + (evidence_count - success_count)

        # Compute posterior statistics
        total = posterior_alpha + posterior_beta
        mean = posterior_alpha / total
        mode = (posterior_alpha - 1) / (total - 2) if posterior_alpha > 1 and posterior_beta > 1 and total > 2 else None
        variance = (posterior_alpha * posterior_beta) / (total**2 * (total + 1))

        return {
            "alpha": float(posterior_alpha),
            "beta": float(posterior_beta),
            "mean": float(mean),
            "mode": float(mode) if mode is not None else None,
            "variance": float(variance),
            "std": float(np.sqrt(variance)),
        }

    # ========================================================================
    # HIERARCHICAL MULTI-LEVEL ANALYSIS
    # ========================================================================

    def analyze_hierarchical_mechanisms(
        self, level_data: list[tuple[int, int]], level_names: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Analyze causal mechanisms across multiple levels (micro-meso-macro).

        Implements hierarchical Bayesian model with partial pooling for
        robust inference across policy analysis levels.

        Args:
            level_data: List of (successes, trials) for each level
            level_names: Names for each level (e.g., ['micro', 'meso', 'macro'])

        Returns:
            Dictionary with hierarchical analysis results

        Hierarchical Model:
            - Population hyperpriors capture overall trend
            - Group-level parameters for each mechanism level
            - Partial pooling borrows strength across levels
        """
        if level_names is None:
            level_names = [f"level_{i}" for i in range(len(level_data))]

        # Sample hierarchical model
        results = self.sampling_engine.sample_hierarchical_beta(level_data)

        # Compile results
        level_results = {}
        for i, (name, result) in enumerate(zip(level_names, results)):
            level_results[name] = {
                "posterior_mean": result.posterior_mean,
                "posterior_std": result.posterior_std,
                "hdi_95": result.hdi_95,
                "converged": result.converged,
                "n_successes": level_data[i][0],
                "n_trials": level_data[i][1],
                "success_rate": level_data[i][0] / level_data[i][1] if level_data[i][1] > 0 else 0.0,
            }

        # Compute overall mechanism strength (average across levels)
        posterior_means = [r.posterior_mean for r in results]
        overall_mean = float(np.mean(posterior_means))

        if len(results) <= 1:
            overall_std = 0.0
        else:
            overall_std = float(np.std(posterior_means, ddof=1))

        return {
            "levels": level_results,
            "overall_mean": overall_mean,
            "overall_std": overall_std,
            "n_levels": len(level_data),
            "all_converged": all(r.converged for r in results),
        }

    # ========================================================================
    # MODEL COMPARISON AND DIAGNOSTICS
    # ========================================================================

    def compare_causal_models(self, model_traces: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Compare multiple causal mechanism models.

        Args:
            model_traces: Dictionary mapping model names to traces

        Returns:
            List of model comparison results sorted by quality

        Uses:
            - WAIC: Widely Applicable Information Criterion
            - LOO-CV: Leave-One-Out Cross-Validation
        """
        comparisons = self.diagnostics.compare_models(model_traces, ic="waic")

        return [
            {
                "model_name": c.model_name,
                "waic": c.waic,
                "waic_se": c.waic_se,
                "loo": c.loo,
                "loo_se": c.loo_se,
                "warning": c.warning,
                "warning_msg": c.warning_msg,
            }
            for c in comparisons
        ]

    def validate_model(self, trace: Any, observed_data: NDArray[np.floating[Any]]) -> dict[str, Any]:
        """
        Validate Bayesian model using posterior predictive checks.

        Args:
            trace: arviz.InferenceData with posterior samples
            observed_data: Observed data for validation

        Returns:
            Dictionary with validation results
        """
        # Posterior predictive check (mean)
        ppc_mean = self.diagnostics.posterior_predictive_check(trace, observed_data, test_statistic="mean")

        # Posterior predictive check (std)
        ppc_std = self.diagnostics.posterior_predictive_check(trace, observed_data, test_statistic="std")

        # Convergence check
        convergence = self.diagnostics.check_convergence(trace)

        return {
            "ppc_mean": {
                "p_value": ppc_mean.p_value,
                "passed": ppc_mean.passed,
                "message": ppc_mean.message,
            },
            "ppc_std": {
                "p_value": ppc_std.p_value,
                "passed": ppc_std.passed,
                "message": ppc_std.message,
            },
            "convergence": convergence,
            "overall_valid": ppc_mean.passed and ppc_std.passed and convergence.get("converged", False),
        }

    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================

    def get_beach_prior(self, evidence_type: str, rarity: float = 0.5) -> PriorParameters:
        """
        Get Beach's test-specific prior.

        Args:
            evidence_type: One of ['straw_in_wind', 'hoop', 'smoking_gun', 'doubly_decisive']
            rarity: Evidence rarity (0=common, 1=rare)

        Returns:
            PriorParameters configured for Beach's test type
        """
        return self.prior_builder.build_prior_for_evidence_type(evidence_type, rarity=rarity)

    def sample_with_prior(
        self, n_successes: int, n_trials: int, prior_params: PriorParameters
    ) -> SamplingResult:
        """
        Sample posterior given data and prior.

        Args:
            n_successes: Number of successes
            n_trials: Total trials
            prior_params: Prior specification

        Returns:
            SamplingResult with posterior samples
        """
        return self.sampling_engine.sample_beta_binomial(
            n_successes=n_successes,
            n_trials=n_trials,
            prior_alpha=prior_params.alpha,
            prior_beta=prior_params.beta,
        )

    def get_summary(self, result: SamplingResult) -> str:
        """
        Get human-readable summary of sampling result.

        Args:
            result: SamplingResult to summarize

        Returns:
            Formatted string summary
        """
        summary = self.sampling_engine.get_sampling_summary(result)

        return (
            f"Posterior: mean={summary['posterior']['mean']:.3f}, "
            f"95% HDI=[{summary['posterior']['hdi_95']['lower']:.3f}, "
            f"{summary['posterior']['hdi_95']['upper']:.3f}], "
            f"R-hat={summary['diagnostics']['rhat']:.3f}, "
            f"ESS={summary['diagnostics']['ess_bulk']:.0f}, "
            f"converged={summary['diagnostics']['converged']}"
        )
