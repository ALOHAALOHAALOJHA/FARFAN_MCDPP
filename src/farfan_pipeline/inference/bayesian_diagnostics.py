"""
Bayesian Diagnostics
====================

Model validation and comparison tools for Bayesian inference.

This module provides comprehensive diagnostics for Bayesian models:
- Model comparison (WAIC, LOO-CV)
- Posterior predictive checks
- Prior sensitivity analysis
- Convergence visualization

Phase 2 SOTA Enhancement - 2026-01-07

Theoretical Foundation:
    Gelman et al. (2013): Bayesian Data Analysis (Chapter 7).
    Vehtari, Gelman, Gabry (2017): Practical Bayesian model evaluation using LOO-CV.
    Watanabe (2010): Asymptotic equivalence of Bayes cross validation and WAIC.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

try:
    import arviz as az

    ARVIZ_AVAILABLE = True
except ImportError:
    ARVIZ_AVAILABLE = False
    az = Any  # type: ignore[misc, assignment]


@dataclass
class ModelComparison:
    """Results from model comparison"""

    model_name: str = ""
    waic: float = 0.0
    waic_se: float = 0.0
    loo: float = 0.0
    loo_se: float = 0.0
    p_waic: float = 0.0
    p_loo: float = 0.0
    warning: bool = False
    warning_msg: str = ""


@dataclass
class PosteriorPredictiveCheck:
    """Results from posterior predictive check"""

    test_statistic: str = ""
    observed_value: float = 0.0
    predicted_mean: float = 0.0
    predicted_std: float = 0.0
    p_value: float = 0.0
    passed: bool = True
    message: str = ""


class BayesianDiagnostics:
    """
    Comprehensive diagnostics for Bayesian models.

    Provides model validation, comparison, and sensitivity analysis
    tools for process tracing Bayesian inference.

    Attributes:
        logger: Logger instance
    """

    def __init__(self):
        """Initialize Bayesian Diagnostics."""
        self.logger = logging.getLogger(self.__class__.__name__)

        if not ARVIZ_AVAILABLE:
            self.logger.warning(
                "arviz not available. Model diagnostics will be limited. "
                "Install with: pip install arviz>=0.17.0"
            )

    def is_available(self) -> bool:
        """Check if arviz is available."""
        return ARVIZ_AVAILABLE

    def compare_models(self, traces: dict[str, Any], ic: str = "waic") -> list[ModelComparison]:
        """
        Compare multiple Bayesian models using information criteria.

        Args:
            traces: Dictionary mapping model names to arviz.InferenceData objects
            ic: Information criterion ('waic' or 'loo')

        Returns:
            List of ModelComparison objects sorted by IC (best first)

        Information Criteria:
            - WAIC: Widely Applicable Information Criterion
            - LOO: Leave-One-Out Cross-Validation

        Notes:
            Lower IC values indicate better models.
            Standard errors allow for uncertainty quantification.
        """
        if not ARVIZ_AVAILABLE:
            self.logger.error("arviz not available for model comparison")
            return []

        if not traces:
            self.logger.warning("No models provided for comparison")
            return []

        results = []

        for name, trace in traces.items():
            try:
                # Compute WAIC
                waic = az.waic(trace)
                waic_value = float(waic.elpd_waic)
                waic_se = float(waic.se)
                p_waic = float(waic.p_waic)

                # Compute LOO-CV
                loo = az.loo(trace)
                loo_value = float(loo.elpd_loo)
                loo_se = float(loo.se)
                p_loo = float(loo.p_loo)

                # Check for warnings (high pareto k values)
                warning = bool(loo.warning)
                warning_msg = ""
                if warning:
                    warning_msg = "High Pareto k values detected - LOO may be unreliable"

                comparison = ModelComparison(
                    model_name=name,
                    waic=waic_value,
                    waic_se=waic_se,
                    loo=loo_value,
                    loo_se=loo_se,
                    p_waic=p_waic,
                    p_loo=p_loo,
                    warning=warning,
                    warning_msg=warning_msg,
                )

                results.append(comparison)

            except Exception as e:
                self.logger.error(f"Error comparing model {name}: {e}")
                continue

        # Sort by chosen IC (lower is better)
        if ic == "waic":
            results.sort(key=lambda x: x.waic)
        else:
            results.sort(key=lambda x: x.loo)

        self.logger.info(f"Compared {len(results)} models using {ic.upper()}")
        return results

    def posterior_predictive_check(
        self, trace: Any, observed_data: NDArray[np.floating[Any]], test_statistic: str = "mean"
    ) -> PosteriorPredictiveCheck:
        """
        Perform posterior predictive check.

        Compares observed data to data simulated from posterior predictive distribution.

        Args:
            trace: arviz.InferenceData with posterior_predictive samples
            observed_data: Observed data array
            test_statistic: Statistic to check ('mean', 'std', 'min', 'max')

        Returns:
            PosteriorPredictiveCheck with test results

        Interpretation:
            p_value ≈ 0.5: Good model fit
            p_value < 0.05 or > 0.95: Potential model misspecification
        """
        if not ARVIZ_AVAILABLE:
            self.logger.error("arviz not available for posterior predictive check")
            return PosteriorPredictiveCheck(
                test_statistic=test_statistic,
                passed=False,
                message="arviz not available",
            )

        try:
            # Get posterior predictive samples
            if not hasattr(trace, "posterior_predictive"):
                self.logger.warning("No posterior_predictive in trace")
                return PosteriorPredictiveCheck(
                    test_statistic=test_statistic,
                    passed=False,
                    message="No posterior predictive samples",
                )

            # Extract first variable from posterior_predictive
            var_name = list(trace.posterior_predictive.data_vars)[0]
            pp_samples = trace.posterior_predictive[var_name].values

            # Flatten posterior predictive samples
            pp_flat = pp_samples.reshape(-1, pp_samples.shape[-1])

            # Compute test statistic for observed data
            if test_statistic == "mean":
                obs_stat = float(np.mean(observed_data))
                pp_stats = np.mean(pp_flat, axis=1)
            elif test_statistic == "std":
                obs_stat = float(np.std(observed_data, ddof=1))
                pp_stats = np.std(pp_flat, axis=1, ddof=1)
            elif test_statistic == "min":
                obs_stat = float(np.min(observed_data))
                pp_stats = np.min(pp_flat, axis=1)
            elif test_statistic == "max":
                obs_stat = float(np.max(observed_data))
                pp_stats = np.max(pp_flat, axis=1)
            else:
                raise ValueError(f"Unknown test statistic: {test_statistic}")

            # Compute p-value (proportion of pp stats more extreme than observed)
            p_value = float(np.mean(pp_stats >= obs_stat))

            # Two-tailed test
            p_value = min(p_value, 1 - p_value) * 2

            # Check if passed (p-value in reasonable range)
            passed = 0.05 < p_value < 0.95

            message = "Good model fit" if passed else "Potential model misspecification"

            return PosteriorPredictiveCheck(
                test_statistic=test_statistic,
                observed_value=obs_stat,
                predicted_mean=float(np.mean(pp_stats)),
                predicted_std=float(np.std(pp_stats, ddof=1)),
                p_value=p_value,
                passed=passed,
                message=message,
            )

        except Exception as e:
            self.logger.error(f"Error in posterior predictive check: {e}")
            return PosteriorPredictiveCheck(
                test_statistic=test_statistic,
                passed=False,
                message=f"Error: {e!s}",
            )

    def check_convergence(self, trace: Any, var_names: list[str] | None = None) -> dict[str, Any]:
        """
        Check convergence diagnostics for MCMC sampling.

        Args:
            trace: arviz.InferenceData object
            var_names: Variable names to check (None = all)

        Returns:
            Dictionary with convergence diagnostics

        Diagnostics:
            - R-hat: Should be < 1.05 for convergence
            - ESS: Should be > 400 for reliable inference
            - MCSE: Monte Carlo Standard Error
        """
        if not ARVIZ_AVAILABLE:
            return {"error": "arviz not available"}

        try:
            # Compute R-hat
            rhat = az.rhat(trace, var_names=var_names)
            rhat_dict = {var: float(rhat[var].values) for var in rhat.data_vars}

            # Compute ESS
            ess = az.ess(trace, var_names=var_names)
            ess_dict = {var: float(ess[var].values) for var in ess.data_vars}

            # Compute MCSE (Monte Carlo Standard Error)
            mcse = az.mcse(trace, var_names=var_names)
            mcse_dict = {var: float(mcse[var].values) for var in mcse.data_vars}

            # Check convergence for each variable
            converged = {}
            warnings_list = []

            for var in rhat_dict:
                var_converged = True

                if rhat_dict[var] >= 1.05:
                    var_converged = False
                    warnings_list.append(f"{var}: R-hat={rhat_dict[var]:.3f} >= 1.05")

                if ess_dict[var] < 400:
                    var_converged = False
                    warnings_list.append(f"{var}: ESS={ess_dict[var]:.0f} < 400")

                converged[var] = var_converged

            all_converged = all(converged.values())

            return {
                "converged": all_converged,
                "rhat": rhat_dict,
                "ess": ess_dict,
                "mcse": mcse_dict,
                "warnings": warnings_list,
                "variables_converged": converged,
            }

        except Exception as e:
            self.logger.error(f"Error checking convergence: {e}")
            return {"error": str(e)}

    def prior_sensitivity_analysis(
        self,
        model_func: Any,
        data: dict[str, Any],
        prior_configs: list[dict[str, float]],
    ) -> dict[str, Any]:
        """
        Perform prior sensitivity analysis.

        Tests how posterior changes with different prior specifications.

        Args:
            model_func: Function that builds PyMC model given prior config
            data: Observed data dictionary
            prior_configs: List of prior configuration dictionaries

        Returns:
            Dictionary with sensitivity analysis results

        Interpretation:
            If posteriors change dramatically with priors, data is weak.
            If posteriors are stable, data dominates prior.
        """
        if not ARVIZ_AVAILABLE:
            return {"error": "arviz not available"}

        results = []

        for i, config in enumerate(prior_configs):
            try:
                # Build and sample model with this prior configuration
                trace = model_func(data, config)

                # Extract posterior summaries
                summary = az.summary(trace)

                results.append(
                    {
                        "prior_config": config,
                        "posterior_mean": {
                            var: float(summary.loc[var, "mean"]) for var in summary.index
                        },
                        "posterior_sd": {
                            var: float(summary.loc[var, "sd"]) for var in summary.index
                        },
                    }
                )

            except Exception as e:
                self.logger.error(f"Error in prior config {i}: {e}")
                continue

        # Compute variance of posteriors across priors
        if len(results) > 1:
            var_names = list(results[0]["posterior_mean"].keys())
            sensitivity = {}

            for var in var_names:
                means = [r["posterior_mean"][var] for r in results]
                sensitivity[var] = {
                    "mean_range": (min(means), max(means)),
                    "variance": float(np.var(means, ddof=1)),
                    "coefficient_of_variation": (
                        float(np.std(means, ddof=1) / abs(np.mean(means)))
                        if np.mean(means) != 0
                        else float("inf")
                    ),
                }

            return {"results": results, "sensitivity": sensitivity, "n_configs": len(results)}
        else:
            return {"results": results, "n_configs": len(results)}

    def plot_diagnostics(
        self, trace: Any, var_names: list[str] | None = None, output_path: str | None = None
    ) -> bool:
        """
        Generate diagnostic plots for MCMC sampling.

        Creates:
        - Trace plots
        - Autocorrelation plots
        - Posterior distributions

        Args:
            trace: arviz.InferenceData object
            var_names: Variables to plot (None = all)
            output_path: Path to save figure

        Returns:
            True if successful, False otherwise
        """
        if not ARVIZ_AVAILABLE:
            self.logger.error("arviz not available for plotting")
            return False

        try:
            import matplotlib.pyplot as plt

            # Create diagnostic plots
            az.plot_trace(trace, var_names=var_names)

            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches="tight")
                self.logger.info(f"Diagnostic plots saved to {output_path}")
            else:
                plt.show()

            plt.close()
            return True

        except ImportError:
            self.logger.warning("matplotlib not available for plotting")
            return False
        except Exception as e:
            self.logger.error(f"Error generating plots: {e}")
            return False

    def summary_report(self, trace: Any, var_names: list[str] | None = None) -> dict[str, Any]:
        """
        Generate comprehensive summary report.

        Args:
            trace: arviz.InferenceData object
            var_names: Variables to summarize (None = all)

        Returns:
            Dictionary with comprehensive diagnostics

        Includes:
            - Posterior statistics (mean, std, HDI)
            - Convergence diagnostics (R-hat, ESS)
            - Model comparison metrics (if applicable)
        """
        if not ARVIZ_AVAILABLE:
            return {"error": "arviz not available"}

        try:
            # Get posterior summary
            summary = az.summary(trace, var_names=var_names)

            # Convert to dictionary
            summary_dict = {}
            for var in summary.index:
                summary_dict[var] = {
                    "mean": float(summary.loc[var, "mean"]),
                    "sd": float(summary.loc[var, "sd"]),
                    "hdi_3%": float(summary.loc[var, "hdi_3%"]),
                    "hdi_97%": float(summary.loc[var, "hdi_97%"]),
                    "mcse_mean": float(summary.loc[var, "mcse_mean"]),
                    "ess_bulk": float(summary.loc[var, "ess_bulk"]),
                    "ess_tail": float(summary.loc[var, "ess_tail"]),
                    "r_hat": float(summary.loc[var, "r_hat"]),
                }

            # Add convergence check
            convergence = self.check_convergence(trace, var_names=var_names)

            return {
                "summary": summary_dict,
                "convergence": convergence,
                "n_variables": len(summary_dict),
            }

        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return {"error": str(e)}
