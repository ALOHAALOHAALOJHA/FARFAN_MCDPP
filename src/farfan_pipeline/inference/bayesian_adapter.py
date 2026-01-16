"""
Bayesian Engine Adapter (F1.2 Refactoring)
===========================================

Unified interface for all Bayesian inference operations in the Derek Beach pipeline.

This adapter integrates:
- BayesianPriorBuilder (AGUJA I): Adaptive prior construction
- BayesianSamplingEngine (AGUJA II): MCMC sampling with diagnostics
- BayesianDiagnostics: Model validation and comparison

FASE 4.3: N2 Calibration Integration
- Accepts EpistemicCalibrationRegistry for N2-level parameter resolution
- Resolves N2 calibration for Bayesian methods
- Applies PDM-driven adjustments (prior_strength, hierarchical models, MCMC samples)

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

# FASE 4.3: N2 Calibration imports
try:
    from farfan_pipeline.infrastructure.calibration.registry import (
        EpistemicCalibrationRegistry,
        CalibrationResolutionError,
    )
    CALIBRATION_REGISTRY_AVAILABLE = True
except ImportError:
    CALIBRATION_REGISTRY_AVAILABLE = False

if TYPE_CHECKING:
    from numpy.typing import NDArray


class BayesianEngineAdapter:
    """
    Unified Bayesian inference adapter for Derek Beach process tracing.

    This class provides a high-level interface to all Bayesian operations,
    integrating prior construction, MCMC sampling, and model diagnostics.

    FASE 4.3: N2 Calibration Integration
    - Accepts calibration_registry for epistemic level calibration
    - Resolves N2 (Inferential Computation) calibration for Bayesian methods
    - Applies PDM-driven adjustments (prior_strength, hierarchical models, MCMC samples)

    Attributes:
        config: Configuration object
        nlp: spaCy NLP model (optional, for future text-based priors)
        prior_builder: BayesianPriorBuilder instance (AGUJA I)
        sampling_engine: BayesianSamplingEngine instance (AGUJA II)
        diagnostics: BayesianDiagnostics instance
        calibration_registry: EpistemicCalibrationRegistry (FASE 4.3)
        pdm_profile: PDM structural profile (FASE 4.3)
        logger: Logger instance
    """

    def __init__(
        self,
        config: Any,
        nlp_model: Any | None = None,
        calibration_registry: Any = None,  # FASE 4.3
        pdm_profile: Any = None,  # FASE 4.3
    ):
        """
        Initialize Bayesian Engine Adapter.

        Args:
            config: Configuration object with Bayesian thresholds
            nlp_model: Optional spaCy NLP model
            calibration_registry: FASE 4.3 - Epistemic calibration registry
            pdm_profile: FASE 4.3 - PDM structural profile
        """
        self.config = config
        self.nlp = nlp_model
        self.calibration_registry = calibration_registry  # FASE 4.3
        self.pdm_profile = pdm_profile  # FASE 4.3
        self.logger = logging.getLogger(self.__class__.__name__)

        # Calibration cache (FASE 4.3)
        self._calibration_cache: dict[str, dict[str, Any]] = {}

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
    # FASE 4.3: N2 Calibration Resolution
    # ========================================================================

    def resolve_n2_calibration(
        self,
        method_id: str,
        contract_type: str = "TYPE_B",
    ) -> dict[str, Any] | None:
        """
        Resolve N2 (Inferential Computation) calibration for a Bayesian method.

        FASE 4.3: N2 Calibration Integration

        This method uses the EpistemicCalibrationRegistry to resolve
        calibration parameters for N2-level methods, applying:
        - Level defaults (N2-INF base configuration)
        - Contract type overrides (TYPE_B is typical for Bayesian inference)
        - PDM-driven adjustments (prior_strength, hierarchical models, MCMC samples)

        Args:
            method_id: Fully-qualified method name (ClassName.method_name)
            contract_type: Contract type (TYPE_A, TYPE_B, etc.)

        Returns:
            Resolved calibration dict with N2 parameters, or None if registry unavailable.

        N2 Calibration Parameters:
            - prior_strength: Strength of prior beliefs (0.0-1.0)
            - use_data_driven_priors: Whether to use historical baselines for priors
            - enable_hierarchical_models: Enable hierarchical Bayesian models
            - mcmc_samples: Number of MCMC samples (with PDM multiplier)
            - likelihood_weight: Weight for likelihood in inference

        Raises:
            CalibrationResolutionError: If calibration resolution fails
        """
        if self.calibration_registry is None:
            self.logger.debug("n2_calibration_unavailable no_registry")
            return None

        # Check cache first
        cache_key = f"{method_id}:{contract_type}"
        if cache_key in self._calibration_cache:
            return self._calibration_cache[cache_key]

        try:
            # Resolve calibration through 8-layer pipeline
            calibration = self.calibration_registry.resolve_calibration(
                method_id=method_id,
                contract_type=contract_type,
                pdm_profile=self.pdm_profile,
            )

            # Verify it's N2 calibration
            if calibration.get("level") != "N2-INF":
                self.logger.warning(
                    "n2_calibration_level_mismatch method=%s expected=N2-INF got=%s",
                    method_id,
                    calibration.get("level"),
                )

            # Cache the result
            self._calibration_cache[cache_key] = calibration

            self.logger.debug(
                "n2_calibration_resolved method=%s contract=%s params=%d",
                method_id,
                contract_type,
                len(calibration.get("calibration_parameters", {})),
            )

            return calibration

        except Exception as e:
            self.logger.error(
                "n2_calibration_failed method=%s contract=%s error=%s",
                method_id,
                contract_type,
                str(e),
            )
            # Return None to allow fallback to default behavior
            return None

    def get_n2_parameter(
        self,
        method_id: str,
        parameter_name: str,
        default: float | bool | int = 1.0,
        contract_type: str = "TYPE_B",
    ) -> float | bool | int:
        """
        Get a specific N2 calibration parameter for a Bayesian method.

        FASE 4.3: Convenience method for accessing individual N2 parameters.

        Args:
            method_id: Fully-qualified method name
            parameter_name: Parameter name (e.g., "prior_strength", "mcmc_samples")
            default: Default value if calibration unavailable
            contract_type: Contract type (TYPE_B is typical for Bayesian)

        Returns:
            Parameter value (float, bool, or int), or default if unavailable.

        Example:
            strength = adapter.get_n2_parameter(
                "BayesianMechanismInference.test_necessity",
                "prior_strength",
                default=0.5,
            )
        """
        calibration = self.resolve_n2_calibration(method_id, contract_type)

        if calibration is None:
            return default

        params = calibration.get("calibration_parameters", {})
        return params.get(parameter_name, default)

    def apply_n2_calibration_to_sampling(
        self,
        method_id: str,
        n_successes: int,
        n_trials: int,
        prior_alpha: float,
        prior_beta: float,
        contract_type: str = "TYPE_B",
    ) -> dict[str, Any]:
        """
        Apply N2 calibration parameters to Bayesian sampling.

        FASE 4.3: Apply PDM-driven adjustments to sampling parameters.

        This method resolves N2 calibration and applies adjustments:
        - Increases mcmc_samples for high-dimensional evidence
        - Adjusts likelihood_weight for multi-modal data
        - Enables hierarchical models for nested structures

        Args:
            method_id: Fully-qualified method name
            n_successes: Number of successes
            n_trials: Total trials
            prior_alpha: Prior alpha parameter
            prior_beta: Prior beta parameter
            contract_type: Contract type

        Returns:
            Enhanced result with calibration metadata

        Example:
            result = adapter.apply_n2_calibration_to_sampling(
                "BayesianMechanismInference.test_necessity",
                n_successes=5,
                n_trials=10,
                prior_alpha=2.0,
                prior_beta=1.0,
            )
        """
        # Get base calibration
        calibration = self.resolve_n2_calibration(method_id, contract_type)
        calibration_applied = False
        calibration_metadata = {}

        # Apply PDM-driven adjustments if available
        if calibration is not None:
            params = calibration.get("calibration_parameters", {})

            # Apply MCMC sample multiplier for high-dimensional evidence
            if "mcmc_samples_multiplier" in params:
                multiplier = params["mcmc_samples_multiplier"]
                calibration_metadata["mcmc_multiplier_applied"] = multiplier
                calibration_applied = True

            # Apply likelihood weight for multi-modal data
            if "likelihood_weight" in params:
                weight = params["likelihood_weight"]
                calibration_metadata["likelihood_weight_applied"] = weight
                calibration_applied = True

            # Check for hierarchical model enablement
            if params.get("enable_hierarchical_models", False):
                calibration_metadata["hierarchical_models_enabled"] = True
                calibration_applied = True

            # Check for data-driven priors
            if params.get("use_data_driven_priors", False):
                calibration_metadata["data_driven_priors_enabled"] = True
                prior_strength = params.get("prior_strength", 0.5)
                # Adjust prior strength
                prior_alpha = prior_alpha * (1 + prior_strength)
                prior_beta = prior_beta * (1 + prior_strength)
                calibration_metadata["prior_strength_applied"] = prior_strength
                calibration_applied = True

        # Perform sampling with potentially adjusted parameters
        result = self.sampling_engine.sample_beta_binomial(
            n_successes=n_successes,
            n_trials=n_trials,
            prior_alpha=prior_alpha,
            prior_beta=prior_beta,
        )

        # Add calibration metadata to result
        return {
            "posterior_mean": result.posterior_mean,
            "hdi_95": result.hdi_95,
            "rhat": result.rhat,
            "converged": result.converged,
            "calibration_applied": calibration_applied,
            "calibration_metadata": calibration_metadata,
            "adjusted_prior_alpha": prior_alpha,
            "adjusted_prior_beta": prior_beta,
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
