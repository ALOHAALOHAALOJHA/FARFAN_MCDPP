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
            "sampling_engine": (
                "✓ disponible"
                if self.sampling_engine and self.sampling_engine.is_available()
                else "✗ no disponible"
            ),
            "diagnostics": (
                "✓ disponible"
                if self.diagnostics and self.diagnostics.is_available()
                else "✗ no disponible"
            ),
            "overall": "✓ disponible" if self.is_available() else "✗ no disponible",
        }

    # ========================================================================
    # OBSERVATION VALIDATION HELPER
    # ========================================================================

    def _validate_and_convert_observations(
        self,
        observations: list[float] | NDArray[np.floating[Any]],
        method_name: str,
    ) -> tuple[int, int, list[str]]:
        """
        Rigorously validate and convert observations to successes/trials.

        Args:
            observations: Raw observations array
            method_name: Name of calling method for error messages

        Returns:
            Tuple of (n_successes, n_trials, warnings_list)

        Raises:
            ValueError: If observations are invalid or empty
        """
        warnings_list: list[str] = []

        # Convert to numpy array
        obs_array = np.asarray(observations, dtype=np.float64)

        # CRITICAL: Check for empty observations
        if obs_array.size == 0:
            raise ValueError(f"{method_name}: observations array is empty")

        # CRITICAL: Filter NaN values
        nan_mask = np.isnan(obs_array)
        n_nan = int(np.sum(nan_mask))
        if n_nan > 0:
            warnings_list.append(f"Filtered {n_nan} NaN values from observations")
            self.logger.warning(f"{method_name}: {warnings_list[-1]}")
            obs_array = obs_array[~nan_mask]

        # CRITICAL: Filter Inf values
        inf_mask = np.isinf(obs_array)
        n_inf = int(np.sum(inf_mask))
        if n_inf > 0:
            warnings_list.append(f"Filtered {n_inf} Inf values from observations")
            self.logger.warning(f"{method_name}: {warnings_list[-1]}")
            obs_array = obs_array[~inf_mask]

        # Check if anything remains after filtering
        if obs_array.size == 0:
            raise ValueError(f"{method_name}: all observations were NaN or Inf")

        # VALIDATION: Check for non-binary values (warn but proceed)
        non_binary_mask = ~np.isin(obs_array, [0.0, 1.0])
        n_non_binary = int(np.sum(non_binary_mask))
        if n_non_binary > 0:
            warnings_list.append(
                f"{n_non_binary} non-binary values detected; "
                f"treating as fractional successes (sum={np.sum(obs_array):.2f})"
            )
            self.logger.warning(f"{method_name}: {warnings_list[-1]}")

        # VALIDATION: Check for negative values
        n_negative = int(np.sum(obs_array < 0))
        if n_negative > 0:
            raise ValueError(f"{method_name}: {n_negative} negative values in observations")

        # Convert to successes/trials
        n_successes = int(np.sum(obs_array))
        n_trials = len(obs_array)

        # Sanity check: successes can exceed trials with fractional values
        if n_successes > n_trials:
            warnings_list.append(
                f"n_successes ({n_successes}) > n_trials ({n_trials}) due to fractional values"
            )
            # Clip to valid range
            n_successes = n_trials

        return n_successes, n_trials, warnings_list

    # ========================================================================
    # HIGH-LEVEL PROCESS TRACING METHODS
    # ========================================================================

    def test_necessity_from_observations(
        self,
        observations: list[float] | NDArray[np.floating[Any]],
        prior: dict[str, float] | None = None,
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

        Raises:
            ValueError: If observations are empty or all invalid

        Beach's Hoop Test:
            - Prior: Beta(2, 1) favors necessity
            - Updates with evidence
            - High posterior = necessary condition likely met
        """
        # Rigorous observation validation
        n_successes, n_trials, obs_warnings = self._validate_and_convert_observations(
            observations, "test_necessity_from_observations"
        )

        if prior is None:
            # Use hoop test prior (favors necessity)
            prior_params = self.prior_builder.build_prior_for_evidence_type("hoop", rarity=0.5)
            prior_alpha = prior_params.alpha
            prior_beta = prior_params.beta
        else:
            prior_alpha = float(prior.get("alpha", 1.0))
            prior_beta = float(prior.get("beta", 1.0))

        # Sample posterior
        result = self.sampling_engine.sample_beta_binomial(
            n_successes=n_successes,
            n_trials=n_trials,
            prior_alpha=prior_alpha,
            prior_beta=prior_beta,
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
            "validation_warnings": obs_warnings,
        }

    def test_sufficiency_from_observations(
        self,
        observations: list[float] | NDArray[np.floating[Any]],
        prior: dict[str, float] | None = None,
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
        # Rigorous observation validation
        n_successes, n_trials, obs_warnings = self._validate_and_convert_observations(
            observations, "test_sufficiency_from_observations"
        )

        if prior is None:
            # Use smoking gun prior (favors sufficiency)
            prior_params = self.prior_builder.build_prior_for_evidence_type(
                "smoking_gun", rarity=0.7
            )
            prior_alpha = prior_params.alpha
            prior_beta = prior_params.beta
        else:
            prior_alpha = float(prior.get("alpha", 1.0))
            prior_beta = float(prior.get("beta", 1.0))

        # Sample posterior
        result = self.sampling_engine.sample_beta_binomial(
            n_successes=n_successes,
            n_trials=n_trials,
            prior_alpha=prior_alpha,
            prior_beta=prior_beta,
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
            "validation_warnings": obs_warnings,
        }

    def test_doubly_decisive(
        self,
        observations: list[float] | NDArray[np.floating[Any]],
        prior: dict[str, float] | None = None,
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

        Raises:
            ValueError: If observations are empty or all invalid

        Beach's Doubly Decisive Test:
            - Prior: Beta(3, 3) concentrated prior
            - Must meet both necessity and sufficiency criteria
            - Provides strongest possible confirmation
        """
        # Rigorous observation validation
        n_successes, n_trials, obs_warnings = self._validate_and_convert_observations(
            observations, "test_doubly_decisive"
        )

        if prior is None:
            prior_params = self.prior_builder.build_prior_for_evidence_type(
                "doubly_decisive", rarity=0.8
            )
            prior_alpha = prior_params.alpha
            prior_beta = prior_params.beta
        else:
            prior_alpha = float(prior.get("alpha", 1.0))
            prior_beta = float(prior.get("beta", 1.0))

        result = self.sampling_engine.sample_beta_binomial(
            n_successes=n_successes,
            n_trials=n_trials,
            prior_alpha=prior_alpha,
            prior_beta=prior_beta,
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
            "validation_warnings": obs_warnings,
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
        mode_valid = posterior_alpha > 1 and posterior_beta > 1 and total > 2
        mode = (posterior_alpha - 1) / (total - 2) if mode_valid else None
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

        Raises:
            ValueError: If level_names length doesn't match level_data length

        Hierarchical Model:
            - Population hyperpriors capture overall trend
            - Group-level parameters for each mechanism level
            - Partial pooling borrows strength across levels
        """
        # RIGOROUS VALIDATION: Handle empty level_data
        if len(level_data) == 0:
            self.logger.warning("Empty level_data provided to analyze_hierarchical_mechanisms")
            return {
                "levels": {},
                "overall_mean": 0.0,
                "overall_std": 0.0,
                "n_levels": 0,
                "all_converged": True,
                "warning": "empty_level_data",
            }

        if level_names is None:
            level_names = [f"level_{i}" for i in range(len(level_data))]

        # CRITICAL VALIDATION: level_names must match level_data length
        if len(level_names) != len(level_data):
            raise ValueError(
                f"level_names length ({len(level_names)}) must match "
                f"level_data length ({len(level_data)})"
            )

        # Sample hierarchical model
        results = self.sampling_engine.sample_hierarchical_beta(level_data)

        # Compile results using strict zip to catch any mismatch
        level_results = {}
        for i, (name, result) in enumerate(zip(level_names, results, strict=True)):
            level_results[name] = {
                "posterior_mean": result.posterior_mean,
                "posterior_std": result.posterior_std,
                "hdi_95": result.hdi_95,
                "converged": result.converged,
                "n_successes": level_data[i][0],
                "n_trials": level_data[i][1],
                "success_rate": (
                    level_data[i][0] / level_data[i][1] if level_data[i][1] > 0 else 0.0
                ),
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

    def validate_model(
        self,
        trace: Any,
        observed_data: NDArray[np.floating[Any]],
    ) -> dict[str, Any]:
        """
        Validate Bayesian model using posterior predictive checks.

        Args:
            trace: arviz.InferenceData with posterior samples
            observed_data: Observed data for validation

        Returns:
            Dictionary with validation results
        """
        # Posterior predictive check (mean)
        ppc_mean = self.diagnostics.posterior_predictive_check(
            trace, observed_data, test_statistic="mean"
        )

        # Posterior predictive check (std)
        ppc_std = self.diagnostics.posterior_predictive_check(
            trace, observed_data, test_statistic="std"
        )

        # Convergence check
        convergence = self.diagnostics.check_convergence(trace)

        overall_valid = ppc_mean.passed and ppc_std.passed and convergence.get("converged", False)

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
            "overall_valid": overall_valid,
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
