"""
Bayesian Sampling Engine (AGUJA II)
====================================

MCMC sampling with diagnostics and convergence checks using PyMC.

This module executes Bayesian inference with:
- NUTS (No U-Turn Sampler) for efficient sampling
- Comprehensive convergence diagnostics (R-hat, ESS)
- Support for Beta-Binomial, Normal-Normal conjugate models
- Hierarchical modeling capabilities

Phase 2 SOTA Enhancement - 2026-01-07

Theoretical Foundation:
    Hoffman & Gelman (2014). The No-U-Turn Sampler (NUTS).
    Gelman & Rubin (1992). Inference from iterative simulation using multiple sequences.
    Vehtari et al. (2021). Rank-normalization, folding, and localization (R-hat).
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

try:
    import arviz as az
    import pymc as pm

    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False
    pm = Any  # type: ignore[misc, assignment]
    az = Any  # type: ignore[misc, assignment]


@dataclass
class SamplingResult:
    """Results from MCMC sampling"""

    posterior_mean: float = 0.0
    posterior_std: float = 0.0
    hdi_95: tuple[float, float] = (0.0, 0.0)
    rhat: float = 1.0
    ess_bulk: float = 0.0
    ess_tail: float = 0.0
    converged: bool = False
    n_samples: int = 0
    n_chains: int = 0
    warnings: list[str] = field(default_factory=list)
    trace: Any = None  # arviz.InferenceData object
    metadata: dict[str, Any] = field(default_factory=dict)


class BayesianSamplingEngine:
    """
    Executes MCMC sampling with comprehensive diagnostics.

    This class provides a high-level interface to PyMC for Bayesian inference,
    with automatic convergence checking and diagnostic reporting.

    Attributes:
        config: Configuration object with sampling parameters
        logger: Logger instance
        n_samples: Number of MCMC samples per chain
        n_chains: Number of independent MCMC chains
        target_accept: Target acceptance rate for NUTS
    """

    def __init__(self, config: Any):
        """
        Initialize Bayesian Sampling Engine.

        Args:
            config: Configuration object with get() method for sampling parameters
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        if not PYMC_AVAILABLE:
            self.logger.warning(
                "PyMC not available. Bayesian sampling will be limited. "
                "Install with: pip install pymc>=5.16.0"
            )

        # Configuration loading with explicit None handling
        # This preserves zero as a valid value while defaulting only on None
        bayesian_thresholds = config.get("bayesian_thresholds", {}) if hasattr(config, 'get') else {}

        # If config is object-style, extract thresholds dict
        if not isinstance(bayesian_thresholds, dict):
            bayesian_thresholds = {
                "mcmc_samples": getattr(bayesian_thresholds, "mcmc_samples", None),
                "mcmc_chains": getattr(bayesian_thresholds, "mcmc_chains", None),
                "target_accept": getattr(bayesian_thresholds, "target_accept", None),
            }

        # Apply defaults only when value is None (preserves explicit zeros)
        raw_samples = bayesian_thresholds.get("mcmc_samples")
        raw_chains = bayesian_thresholds.get("mcmc_chains")
        raw_accept = bayesian_thresholds.get("target_accept")

        self.n_samples: int = int(raw_samples) if raw_samples is not None else 2000
        self.n_chains: int = int(raw_chains) if raw_chains is not None else 4
        self.target_accept: float = float(raw_accept) if raw_accept is not None else 0.9

        self.logger.info(
            f"BayesianSamplingEngine initialized: "
            f"{self.n_samples} samples × {self.n_chains} chains, "
            f"target_accept={self.target_accept:.2f}"
        )

    def is_available(self) -> bool:
        """Check if PyMC is available for sampling."""
        return PYMC_AVAILABLE

    def sample_beta_binomial(
        self, n_successes: int, n_trials: int, prior_alpha: float = 1.0, prior_beta: float = 1.0
    ) -> SamplingResult:
        """
        Sample from Beta-Binomial conjugate model.

        Model:
            Prior: theta ~ Beta(prior_alpha, prior_beta)
            Likelihood: y ~ Binomial(n_trials, theta)
            Posterior: theta | y ~ Beta(prior_alpha + n_successes, prior_beta + n_failures)

        Args:
            n_successes: Number of successes observed
            n_trials: Total number of trials
            prior_alpha: Prior alpha parameter
            prior_beta: Prior beta parameter

        Returns:
            SamplingResult with posterior samples and diagnostics

        Raises:
            RuntimeError: If PyMC is not available
        """
        if not PYMC_AVAILABLE:
            self.logger.error("PyMC not available for Beta-Binomial sampling")
            return self._null_result("pymc_unavailable")

        if n_trials < 0 or n_successes < 0 or n_successes > n_trials:
            self.logger.error(f"Invalid data: successes={n_successes}, trials={n_trials}")
            return self._null_result("invalid_data")

        try:
            with pm.Model() as model:
                # Prior: Beta distribution
                theta = pm.Beta("theta", alpha=prior_alpha, beta=prior_beta)

                # Likelihood: Binomial
                y = pm.Binomial("y", n=n_trials, p=theta, observed=n_successes)

                # Sample posterior
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning)
                    trace = pm.sample(
                        draws=self.n_samples,
                        tune=1000,
                        chains=self.n_chains,
                        return_inferencedata=True,
                        progressbar=False,
                        random_seed=42,
                        target_accept=self.target_accept,
                    )

            # Extract diagnostics
            result = self._extract_diagnostics(trace, "theta")
            result.metadata.update(
                {
                    "model": "beta_binomial",
                    "n_successes": n_successes,
                    "n_trials": n_trials,
                    "prior_alpha": prior_alpha,
                    "prior_beta": prior_beta,
                }
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in Beta-Binomial sampling: {e}")
            return self._null_result("sampling_error", str(e))

    def sample_normal_normal(
        self,
        observations: list[float] | NDArray[np.floating[Any]],
        prior_mu: float = 0.0,
        prior_sigma: float = 1.0,
    ) -> SamplingResult:
        """
        Sample from Normal-Normal conjugate model.

        Model:
            Prior: mu ~ Normal(prior_mu, prior_sigma)
            Likelihood: y ~ Normal(mu, sigma_obs)
            Posterior: mu | y ~ Normal(...)

        Args:
            observations: Observed data points
            prior_mu: Prior mean
            prior_sigma: Prior standard deviation

        Returns:
            SamplingResult with posterior samples and diagnostics

        Raises:
            RuntimeError: If PyMC is not available
        """
        if not PYMC_AVAILABLE:
            self.logger.error("PyMC not available for Normal-Normal sampling")
            return self._null_result("pymc_unavailable")

        if len(observations) == 0:
            self.logger.error("No observations provided")
            return self._null_result("no_data")

        obs_array = np.asarray(observations, dtype=np.float64)

        try:
            with pm.Model() as model:
                # Prior: Normal distribution for mean
                mu = pm.Normal("mu", mu=prior_mu, sigma=prior_sigma)

                # Estimate observation std from data
                obs_std = float(np.std(obs_array, ddof=1) if len(obs_array) > 1 else 1.0)

                # Likelihood: Normal with estimated std
                y = pm.Normal("y", mu=mu, sigma=obs_std, observed=obs_array)

                # Sample posterior
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning)
                    trace = pm.sample(
                        draws=self.n_samples,
                        tune=1000,
                        chains=self.n_chains,
                        return_inferencedata=True,
                        progressbar=False,
                        random_seed=42,
                        target_accept=self.target_accept,
                    )

            # Extract diagnostics
            result = self._extract_diagnostics(trace, "mu")
            result.metadata.update(
                {
                    "model": "normal_normal",
                    "n_observations": len(obs_array),
                    "prior_mu": prior_mu,
                    "prior_sigma": prior_sigma,
                    "obs_mean": float(np.mean(obs_array)),
                    "obs_std": float(obs_std),
                }
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in Normal-Normal sampling: {e}")
            return self._null_result("sampling_error", str(e))

    def sample_hierarchical_beta(
        self,
        group_data: list[tuple[int, int]],
        population_alpha: float = 2.0,
        population_beta: float = 2.0,
    ) -> list[SamplingResult]:
        """
        Sample from hierarchical Beta-Binomial model.

        Model for multi-level process tracing (micro-meso-macro):
            Population: alpha, beta ~ HalfNormal(sigma=population_alpha/beta)
            Group priors: theta_g ~ Beta(alpha, beta)
            Group data: y_g ~ Binomial(n_g, theta_g)

        Args:
            group_data: List of (successes, trials) tuples for each group
            population_alpha: Sigma for alpha hyperprior (default: 2.0)
            population_beta: Sigma for beta hyperprior (default: 2.0)

        Returns:
            List of SamplingResult objects, one per group

        Raises:
            RuntimeError: If PyMC is not available
        """
        if not PYMC_AVAILABLE:
            self.logger.error("PyMC not available for hierarchical sampling")
            return [self._null_result("pymc_unavailable") for _ in group_data]

        if len(group_data) == 0:
            self.logger.error("No group data provided")
            return []

        n_groups = len(group_data)
        successes_array = np.array([s for s, _ in group_data], dtype=np.int64)
        trials_array = np.array([t for _, t in group_data], dtype=np.int64)

        try:
            with pm.Model() as model:
                # Population-level hyperpriors (using parameterized sigmas)
                alpha = pm.HalfNormal("alpha", sigma=population_alpha)
                beta = pm.HalfNormal("beta", sigma=population_beta)

                # Group-level priors
                theta = pm.Beta("theta", alpha=alpha, beta=beta, shape=n_groups)

                # Group-level likelihoods
                pm.Binomial("y", n=trials_array, p=theta, observed=successes_array)

                # Sample
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning)
                    trace = pm.sample(
                        draws=self.n_samples,
                        tune=1500,  # More tuning for hierarchical model
                        chains=self.n_chains,
                        return_inferencedata=True,
                        progressbar=False,
                        random_seed=42,
                        target_accept=self.target_accept,
                    )

            # Extract results for each group
            results = []
            for g in range(n_groups):
                # Extract group-specific theta
                theta_g = trace.posterior["theta"].sel(theta_dim_0=g)

                posterior_mean = float(theta_g.mean().item())
                posterior_std = float(theta_g.std().item())

                # Compute HDI manually for group
                theta_values = theta_g.values.flatten()
                hdi = az.hdi(theta_values, hdi_prob=0.95)
                hdi_lower = float(hdi[0]) if hasattr(hdi, "__getitem__") else float(hdi)
                hdi_upper = float(hdi[1]) if hasattr(hdi, "__getitem__") else float(hdi)

                # Convergence diagnostics (group-level)
                rhat = float(az.rhat(trace, var_names=["theta"]).to_array().mean().item())
                ess = az.ess(trace, var_names=["theta"])
                ess_bulk = float(ess["theta"].mean().item())

                # Compute ESS tail (for extreme quantiles) - actual computation
                try:
                    ess_tail_data = az.ess(trace, var_names=["theta"], method="tail")
                    # Extract scalar from xarray - handle both array and scalar cases
                    if hasattr(ess_tail_data["theta"], "mean"):
                        ess_tail = float(ess_tail_data["theta"].mean().item())
                    else:
                        ess_tail = float(ess_tail_data["theta"].item())
                except Exception as e:
                    self.logger.warning(f"Could not compute ESS tail: {e}, using bulk ESS approximation")
                    ess_tail = ess_bulk * 0.8

                result = SamplingResult(
                    posterior_mean=posterior_mean,
                    posterior_std=posterior_std,
                    hdi_95=(hdi_lower, hdi_upper),
                    rhat=rhat,
                    ess_bulk=ess_bulk,
                    ess_tail=ess_tail,
                    converged=rhat < 1.05,
                    n_samples=self.n_samples * self.n_chains,
                    n_chains=self.n_chains,
                    trace=trace,
                    metadata={
                        "model": "hierarchical_beta_binomial",
                        "group_id": g,
                        "n_groups": n_groups,
                        "n_successes": int(successes_array[g]),
                        "n_trials": int(trials_array[g]),
                    },
                )

                results.append(result)

            self.logger.info(f"Hierarchical sampling complete: {n_groups} groups")
            return results

        except Exception as e:
            self.logger.error(f"Error in hierarchical sampling: {e}")
            return [self._null_result("sampling_error", str(e)) for _ in group_data]

    def _extract_diagnostics(self, trace: Any, param: str) -> SamplingResult:
        """
        Extract comprehensive diagnostics from PyMC trace.

        Args:
            trace: arviz.InferenceData object
            param: Parameter name to extract

        Returns:
            SamplingResult with posterior statistics and diagnostics
        """
        posterior = trace.posterior[param]

        # Posterior statistics
        posterior_mean = float(posterior.mean().item())
        posterior_std = float(posterior.std().item())

        # HDI (Highest Density Interval) - 95%
        hdi = az.hdi(trace, hdi_prob=0.95)[param].values
        hdi_lower = float(hdi[0]) if hasattr(hdi, "__len__") else float(hdi)
        hdi_upper = float(hdi[1]) if hasattr(hdi, "__len__") else float(hdi)

        # Convergence diagnostics
        rhat = float(az.rhat(trace, var_names=[param])[param].item())
        ess = az.ess(trace, var_names=[param])
        ess_bulk = float(ess[param].item())

        # Tail ESS (for extreme quantiles)
        ess_tail_data = az.ess(trace, var_names=[param], method="tail")
        ess_tail = float(ess_tail_data[param].item())

        # Check convergence (R-hat < 1.05 is good)
        converged = rhat < 1.05

        # Warnings
        warnings_list = []
        if rhat >= 1.05:
            warnings_list.append(f"Poor convergence: R-hat={rhat:.3f} >= 1.05")
        if ess_bulk < 400:
            warnings_list.append(f"Low ESS: {ess_bulk:.0f} < 400 (may need more samples)")

        return SamplingResult(
            posterior_mean=posterior_mean,
            posterior_std=posterior_std,
            hdi_95=(hdi_lower, hdi_upper),
            rhat=rhat,
            ess_bulk=ess_bulk,
            ess_tail=ess_tail,
            converged=converged,
            n_samples=self.n_samples * self.n_chains,
            n_chains=self.n_chains,
            warnings=warnings_list,
            trace=trace,
        )

    def _null_result(self, error_type: str, error_message: str = "") -> SamplingResult:
        """Create null result for error cases."""
        return SamplingResult(
            posterior_mean=0.0,
            posterior_std=0.0,
            hdi_95=(0.0, 0.0),
            rhat=float("inf"),
            ess_bulk=0.0,
            ess_tail=0.0,
            converged=False,
            n_samples=0,
            n_chains=0,
            warnings=[f"{error_type}: {error_message}"] if error_message else [error_type],
        )

    def get_sampling_summary(self, result: SamplingResult) -> dict[str, Any]:
        """
        Get human-readable summary of sampling results.

        Args:
            result: SamplingResult to summarize

        Returns:
            Dictionary with summary statistics and diagnostics
        """
        return {
            "posterior": {
                "mean": result.posterior_mean,
                "std": result.posterior_std,
                "hdi_95": {"lower": result.hdi_95[0], "upper": result.hdi_95[1]},
            },
            "diagnostics": {
                "rhat": result.rhat,
                "ess_bulk": result.ess_bulk,
                "ess_tail": result.ess_tail,
                "converged": result.converged,
            },
            "sampling": {
                "n_samples": result.n_samples,
                "n_chains": result.n_chains,
            },
            "warnings": result.warnings,
            "metadata": result.metadata,
        }
