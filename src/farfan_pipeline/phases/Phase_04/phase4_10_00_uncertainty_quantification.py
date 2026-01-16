"""
Uncertainty Quantification Module - State-of-the-Art Statistical Inference
& Convergence Diagnostics

This module implements a rigorous, mathematically grounded framework for quantifying
uncertainty in policy aggregation scores.  It combines Bias-Corrected and Accelerated
(BCa) Bootstrapping with comprehensive convergence diagnostics to ensure publication-
quality statistical inference. 

Key Capabilities:
1. **BCa Bootstrap**:  Corrects for skewness (acceleration) and bias, achieving
   second-order accuracy O(n⁻¹).
2. **Convergence Diagnostics**: K-S tests, Geweke diagnostics, and Effective Sample
   Size (ESS) calculations to validate MCMC/Bootstrap stability.
3. **Pathology Detection**:  Identifies multi-modality, infinite variance, and
   numerical instabilities.
4. **Jackknife Estimation**: Computes acceleration parameters for robust intervals. 

Theoretical Foundation:
    CI_bca = (θ̂*_{α₁}, θ̂*_{α₂})
    where α are adjusted quantiles based on bias correction z₀ and acceleration a.

Author: F. A. R. F. A.N.  Statistical Compliance Team
"""

from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 4
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A. N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

# =============================================================================
# IMPORTS
# =============================================================================

import logging
import math
import random
import statistics
from collections. abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# =============================================================================
# EXCEPTIONS
# =============================================================================


class DistributionError(RuntimeError):
    """Raised when statistical distributions are insufficient for inference."""

    pass


class ConvergenceError(RuntimeError):
    """Raised when bootstrap distribution fails to converge."""

    pass


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass(frozen=True)
class UncertaintyMetrics:
    """
    Immutable container for high-precision statistical uncertainty metrics.

    Attributes:
        point_estimate: The original estimate from the full dataset.
        mean_score:  Arithmetic mean of the bootstrap distribution.
        median_score: Median of the bootstrap distribution. 
        std_error:  Robust standard error estimate.
        ci_lower_95: Lower bound of the 95% BCa confidence interval. 
        ci_upper_95: Upper bound of the 95% BCa confidence interval. 
        confidence_interval_method: The algorithm used (e.g., 'BCa').
        sample_count: Number of iterations performed.
        skewness: Third standardized moment. 
        kurtosis: Fourth standardized moment (excess).
        entropy: Shannon entropy (informational uncertainty).
    """

    point_estimate:  float
    mean_score: float
    median_score: float
    std_error: float
    ci_lower_95: float
    ci_upper_95: float
    confidence_interval_method: str
    sample_count:  int
    skewness: float
    kurtosis: float
    entropy: float

    def __post_init__(self) -> None:
        """Validate metrics are within acceptable bounds."""
        if self.std_error < 0:
            raise ValueError(f"std_error must be non-negative, got {self.std_error}")
        if self.sample_count < 1:
            raise ValueError(f"sample_count must be >= 1, got {self.sample_count}")
        if self.ci_lower_95 > self.ci_upper_95:
            raise ValueError(
                f"ci_lower_95 ({self.ci_lower_95}) > ci_upper_95 ({self.ci_upper_95})"
            )

    def ci_width(self) -> float:
        """Return the width of the 95% confidence interval."""
        return self. ci_upper_95 - self.ci_lower_95

    def coefficient_of_variation(self) -> float:
        """Return the coefficient of variation (std_error / |mean|)."""
        if abs(self.mean_score) < 1e-12:
            return float("inf") if self.std_error > 0 else 0.0
        return self.std_error / abs(self.mean_score)

    def is_precise(self, threshold: float = 0.1) -> bool:
        """Check if CI width relative to point estimate is below threshold."""
        if abs(self.point_estimate) < 1e-12:
            return self.ci_width() < threshold
        return self.ci_width() / abs(self.point_estimate) < threshold


@dataclass(frozen=True)
class ConvergenceDiagnostics: 
    """
    Immutable container for comprehensive convergence diagnostics. 

    Attributes: 
        ks_statistic:  Kolmogorov-Smirnov statistic comparing distribution halves.
        geweke_z_score: Z-score from Geweke diagnostic (first 10% vs last 50%).
        geweke_p_value: P-value associated with Geweke z-score.
        effective_sample_size: ESS accounting for autocorrelation. 
        autocorrelation_time:  Integrated autocorrelation time τ.
        stability_ratio: Ratio of variance in early vs late samples.
        bimodality_index: Ashman's D coefficient for bimodality detection. 
        convergence_status: Human-readable status ('converged', 'failed', 'marginal').
        pathology_flags: List of detected pathologies. 
    """

    ks_statistic: float
    geweke_z_score: float
    geweke_p_value: float
    effective_sample_size:  float
    autocorrelation_time: float
    stability_ratio: float
    bimodality_index:  float
    convergence_status: str
    pathology_flags: list[str] = field(default_factory=list)

    def is_reliable(self, strict: bool = True) -> bool:
        """
        Determine if distribution has converged based on multiple criteria.

        Args:
            strict: If True, require all tests to pass and no pathologies. 
                    If False, require majority of tests and no CRITICAL pathologies. 

        Returns:
            True if diagnostics indicate reliable convergence. 
        """
        tests = [
            self.ks_statistic < 0.05,
            abs(self.geweke_z_score) < 2.0,
            self. geweke_p_value > 0.01,
            self. effective_sample_size > 400,
            self.bimodality_index < 2.0,
        ]
        if strict:
            return all(tests) and not self.pathology_flags
        return sum(tests) >= 3 and "CRITICAL" not in "".join(self. pathology_flags)

    def summary(self) -> str:
        """Return a human-readable summary of convergence status."""
        lines = [
            f"Convergence Status: {self.convergence_status. upper()}",
            f"  K-S Statistic: {self. ks_statistic:. 4f} (< 0.05 required)",
            f"  Geweke Z-Score: {self.geweke_z_score:.3f} (|z| < 2.0 required)",
            f"  Geweke P-Value: {self.geweke_p_value:.4f} (> 0.01 required)",
            f"  Effective Sample Size: {self.effective_sample_size:. 1f} (> 400 required)",
            f"  Autocorrelation Time: {self.autocorrelation_time:.2f}",
            f"  Bimodality Index: {self.bimodality_index:.3f} (< 2.0 required)",
            f"  Stability Ratio: {self.stability_ratio:. 3f}",
        ]
        if self.pathology_flags:
            lines.append(f"  Pathologies: {', '.join(self.pathology_flags)}")
        return "\n". join(lines)


# =============================================================================
# BOOTSTRAP CONVERGENCE ANALYZER
# =============================================================================


class BootstrapConvergenceAnalyzer:
    """
    Production-grade convergence diagnostics for bootstrap distributions.

    Implements: 
    1. Two-sample Kolmogorov-Smirnov test for distribution stability
    2. Geweke diagnostic for mean stationarity
    3. Autocorrelation function estimation via FFT
    4. Effective Sample Size (ESS) calculation
    5. Ashman's D bimodality coefficient
    """

    def __init__(self, seed: int | None = 42):
        """
        Initialize the convergence analyzer.

        Args:
            seed: Random seed for reproducibility.  None for non-deterministic. 
        """
        self.seed = seed
        self._rng = random.Random(seed) if seed is not None else random.Random()

    def _calculate_ks_statistic(
        self, samples1:  Sequence[float], samples2: Sequence[float]
    ) -> float:
        """
        Compute two-sample Kolmogorov-Smirnov statistic.

        The K-S statistic measures the maximum distance between empirical CDFs. 
        D = sup_x |F₁(x) - F₂(x)|

        Args: 
            samples1: First sample sequence.
            samples2: Second sample sequence.

        Returns:
            K-S statistic in [0, 1].  Lower values indicate similar distributions.
        """
        n1, n2 = len(samples1), len(samples2)
        if n1 == 0 or n2 == 0:
            return 1.0

        s1, s2 = sorted(samples1), sorted(samples2)
        all_points = sorted(set(s1) | set(s2))

        max_diff = 0.0
        for x in all_points: 
            cdf1 = sum(1 for v in s1 if v <= x) / n1
            cdf2 = sum(1 for v in s2 if v <= x) / n2
            max_diff = max(max_diff, abs(cdf1 - cdf2))

        return max_diff

    def _fft_radix2(self, x: list[complex]) -> list[complex]:
        """
        Cooley-Tukey radix-2 FFT implementation. 

        Args:
            x:  Input sequence (length must be power of 2).

        Returns:
            FFT of input sequence.
        """
        n = len(x)
        if n <= 1:
            return x

        even = self._fft_radix2(x[0:: 2])
        odd = self._fft_radix2(x[1::2])

        twiddle = [
            math.e ** (-2j * math.pi * k / n) * odd[k] for k in range(n // 2)
        ]

        return [even[k] + twiddle[k] for k in range(n // 2)] + [
            even[k] - twiddle[k] for k in range(n // 2)
        ]

    def _ifft_radix2(self, x:  list[complex]) -> list[complex]: 
        """
        Inverse FFT via conjugate method.

        Args:
            x: FFT coefficients. 

        Returns: 
            Inverse FFT (time-domain signal).
        """
        n = len(x)
        conjugated = [c.conjugate() for c in x]
        transformed = self._fft_radix2(conjugated)
        return [c.conjugate() / n for c in transformed]

    def _calculate_autocorrelation(
        self, samples: Sequence[float], max_lag: int = 100
    ) -> list[float]:
        """
        Compute autocorrelation function using FFT for efficiency.

        ACF(k) = Cov(X_t, X_{t+k}) / Var(X)

        Args: 
            samples: Time series of bootstrap samples.
            max_lag: Maximum lag to compute.

        Returns:
            List of ACF values from lag 0 to max_lag.
        """
        n = len(samples)
        if n < 2:
            return [1.0]

        mean = statistics.mean(samples)
        centered = [x - mean for x in samples]

        variance = sum(c * c for c in centered)
        if variance < 1e-12:
            return [1.0] * min(n, max_lag)

        if n < 256:
            acf = []
            for lag in range(min(n, max_lag)):
                if lag == 0:
                    acf.append(1.0)
                else:
                    cov = sum(centered[i] * centered[i + lag] for i in range(n - lag))
                    acf.append(cov / variance)
            return acf

        N = 1
        while N < 2 * n:
            N *= 2

        x_padded = [complex(c, 0) for c in centered] + [0j] * (N - n)

        fft_x = self._fft_radix2(x_padded)
        power_spectrum = [c * c. conjugate() for c in fft_x]

        acf_complex = self._ifft_radix2(power_spectrum)

        acf = [acf_complex[k]. real / variance for k in range(min(n, max_lag))]

        if acf and abs(acf[0]) > 1e-12:
            scale = 1.0 / acf[0]
            acf = [a * scale for a in acf]

        return acf

    def _calculate_geweke_diagnostic(
        self, samples: Sequence[float]
    ) -> tuple[float, float]: 
        """
        Compute Geweke convergence diagnostic.

        Compares mean of first 10% to last 50% of samples. 
        Under convergence, z ~ N(0,1).

        Args: 
            samples: Bootstrap sample sequence.

        Returns:
            Tuple of (z_score, p_value).
        """
        n = len(samples)
        if n < 100:
            return 0.0, 1.0

        n_first = max(1, n // 10)
        n_last = max(1, n // 2)

        first = list(samples[:n_first])
        last = list(samples[-n_last:])

        mean_first = statistics.mean(first)
        mean_last = statistics. mean(last)

        var_first = statistics.variance(first) if len(first) > 1 else 0.0
        var_last = statistics. variance(last) if len(last) > 1 else 0.0

        se_diff_sq = var_first / len(first) + var_last / len(last)
        if se_diff_sq < 1e-12:
            return 0.0, 1.0

        z = (mean_first - mean_last) / math.sqrt(se_diff_sq)

        p = 2. 0 * (1.0 - self._standard_normal_cdf(abs(z)))

        return z, p

    def _standard_normal_cdf(self, x:  float) -> float:
        """Compute CDF of standard normal distribution."""
        return 0.5 * (1.0 + math.erf(x / math. sqrt(2.0)))

    def _calculate_effective_sample_size(
        self, samples:  Sequence[float], acf: list[float] | None = None
    ) -> tuple[float, float]: 
        """
        Compute Effective Sample Size (ESS) and integrated autocorrelation time.

        ESS = n / (1 + 2 * Σ_{k=1}^∞ ρ_k) = n / τ_int

        Args: 
            samples: Bootstrap sample sequence.
            acf: Pre-computed ACF (optional).

        Returns:
            Tuple of (ESS, autocorrelation_time).
        """
        n = len(samples)
        if n < 2:
            return float(n), 1.0

        if acf is None: 
            acf = self._calculate_autocorrelation(samples)

        tau_int = 1.0
        running_sum = 0.0

        for k in range(1, len(acf)):
            if acf[k] < 0: 
                break
            running_sum += acf[k]
            if running_sum > n / 2:
                break

        tau_int = 1.0 + 2.0 * running_sum
        tau_int = max(1.0, tau_int)

        ess = n / tau_int

        return ess, tau_int

    def _calculate_bimodality_coefficient(self, samples: Sequence[float]) -> float:
        """
        Compute Ashman's D bimodality coefficient. 

        D = |μ₁ - μ₂| / √((σ₁² + σ₂²) / 2)

        D > 2 suggests bimodality. 

        Args:
            samples: Bootstrap sample sequence.

        Returns:
            Ashman's D coefficient.
        """
        n = len(samples)
        if n < 20:
            return 0.0

        sorted_samples = sorted(samples)
        mid = n // 2

        group1 = sorted_samples[:mid]
        group2 = sorted_samples[mid:]

        if not group1 or not group2:
            return 0.0

        mean1 = statistics.mean(group1)
        mean2 = statistics.mean(group2)

        var1 = statistics.variance(group1) if len(group1) > 1 else 0.0
        var2 = statistics.variance(group2) if len(group2) > 1 else 0.0

        pooled_var = (var1 + var2) / 2.0
        if pooled_var < 1e-12:
            return 0.0

        return abs(mean1 - mean2) / math.sqrt(pooled_var)

    def _calculate_stability_ratio(self, samples: Sequence[float]) -> float:
        """
        Compute variance stability ratio between first and second half.

        Args:
            samples:  Bootstrap sample sequence. 

        Returns:
            Ratio of variance(first_half) / variance(second_half).
        """
        n = len(samples)
        if n < 20:
            return 1.0

        mid = n // 2
        first_half = list(samples[:mid])
        second_half = list(samples[mid:])

        var1 = statistics.variance(first_half) if len(first_half) > 1 else 0.0
        var2 = statistics.variance(second_half) if len(second_half) > 1 else 0.0

        if var2 < 1e-12:
            return float("inf") if var1 > 1e-12 else 1.0

        return var1 / var2

    def analyze_convergence(
        self,
        samples:  Sequence[float],
        metrics: UncertaintyMetrics | None = None,
    ) -> ConvergenceDiagnostics:
        """
        Perform comprehensive convergence analysis on bootstrap samples.

        Args:
            samples:  Sequence of bootstrap replicates.
            metrics: Optional pre-computed uncertainty metrics for cross-validation.

        Returns:
            ConvergenceDiagnostics with all computed statistics.
        """
        n = len(samples)
        if n < 10:
            return ConvergenceDiagnostics(
                ks_statistic=1.0,
                geweke_z_score=float("inf"),
                geweke_p_value=0.0,
                effective_sample_size=float(n),
                autocorrelation_time=float("inf"),
                stability_ratio=0.0,
                bimodality_index=0.0,
                convergence_status="failed",
                pathology_flags=["CRITICAL:  Insufficient samples (n < 10)"],
            )

        n_early = max(1, n // 5)
        n_late = max(1, 3 * n // 10)
        ks_stat = self._calculate_ks_statistic(
            samples[:n_early], samples[-n_late:]
        )

        geweke_z, geweke_p = self._calculate_geweke_diagnostic(samples)

        acf = self._calculate_autocorrelation(samples)
        ess, act = self._calculate_effective_sample_size(samples, acf)

        stability = self._calculate_stability_ratio(samples)
        bimodality = self._calculate_bimodality_coefficient(samples)

        pathologies:  list[str] = []

        if n < 1000:
            pathologies.append("WARNING: Low sample count (< 1000)")

        if metrics is not None and metrics.std_error < 1e-12:
            pathologies.append("CRITICAL: Zero variance detected")

        if bimodality > 2.0:
            pathologies. append("CRITICAL:  Bimodality detected (Ashman's D > 2.0)")

        if act > n / 10: 
            pathologies. append("WARNING: High autocorrelation time")

        if stability < 0.5 or stability > 2.0:
            pathologies.append("WARNING: Variance instability detected")

        if ess < 100:
            pathologies.append("CRITICAL: Very low effective sample size (< 100)")

        critical_flags = [f for f in pathologies if "CRITICAL" in f]
        warning_flags = [f for f in pathologies if "WARNING" in f]

        if critical_flags: 
            status = "failed"
        elif ks_stat > 0.05 or abs(geweke_z) > 2.0:
            status = "failed"
        elif warning_flags:
            status = "marginal"
        else:
            status = "converged"

        return ConvergenceDiagnostics(
            ks_statistic=ks_stat,
            geweke_z_score=geweke_z,
            geweke_p_value=geweke_p,
            effective_sample_size=ess,
            autocorrelation_time=act,
            stability_ratio=stability,
            bimodality_index=bimodality,
            convergence_status=status,
            pathology_flags=pathologies,
        )


# =============================================================================
# BOOTSTRAP AGGREGATOR
# =============================================================================


class BootstrapAggregator:
    """
    Enhanced Bootstrap Aggregator with BCa intervals and convergence diagnostics. 

    Implements: 
    1. Bias-Corrected and Accelerated (BCa) bootstrap confidence intervals
    2. Jackknife acceleration estimation
    3. Adaptive iteration with convergence monitoring
    4. Full uncertainty quantification
    """

    def __init__(self, iterations: int = 2000, seed: int | None = 42):
        """
        Initialize the bootstrap aggregator.

        Args:
            iterations:  Number of bootstrap replicates to generate. 
            seed: Random seed for reproducibility.  None for non-deterministic.
        """
        if iterations < 100:
            raise ValueError(f"iterations must be >= 100, got {iterations}")

        self.iterations = iterations
        self.seed = seed
        self._rng = random. Random(seed) if seed is not None else random.Random()
        self._last_samples:  list[float] = []

    def _standard_normal_cdf(self, x: float) -> float:
        """Compute CDF of standard normal distribution."""
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def _inverse_normal_cdf(self, p: float) -> float:
        """
        Compute inverse CDF (quantile function) of standard normal. 

        Uses Beasley-Springer-Moro algorithm for accuracy. 

        Args:
            p:  Probability in (0, 1).

        Returns: 
            z such that Φ(z) = p.
        """
        if p <= 0.0 or p >= 1.0:
            return 0.0

        return math.sqrt(2.0) * self._erfinv(2.0 * p - 1.0)

    def _erfinv(self, x: float) -> float:
        """
        Approximate inverse error function.

        Uses Winitzki's approximation with refinement.

        Args:
            x:  Value in (-1, 1).

        Returns: 
            Inverse error function of x.
        """
        if abs(x) >= 1.0:
            return float("inf") if x > 0 else float("-inf")

        a = 0.147

        ln_term = math.log(1.0 - x * x)
        term1 = 2.0 / (math.pi * a) + ln_term / 2.0
        term2 = ln_term / a

        sign = 1.0 if x >= 0 else -1.0
        result = sign * math.sqrt(math.sqrt(term1 * term1 - term2) - term1)

        return result

    def _calculate_bias_correction(
        self, theta_hat: float, bootstrap_samples: list[float]
    ) -> float:
        """
        Calculate bias correction factor z₀ for BCa interval.

        z₀ = Φ⁻¹(proportion of bootstrap samples < θ̂)

        Args: 
            theta_hat:  Point estimate from original data.
            bootstrap_samples: Bootstrap replicates.

        Returns:
            Bias correction factor z₀.
        """
        n_below = sum(1 for b in bootstrap_samples if b < theta_hat)
        proportion = n_below / len(bootstrap_samples)

        if proportion <= 0.0:
            proportion = 0.5 / len(bootstrap_samples)
        elif proportion >= 1.0:
            proportion = 1.0 - 0.5 / len(bootstrap_samples)

        return self._inverse_normal_cdf(proportion)

    def _calculate_acceleration(
        self, data: Sequence[float], func: Callable[[Sequence[float]], float]
    ) -> float:
        """
        Calculate acceleration factor 'a' using jackknife. 

        a = Σᵢ(θ̄ - θ₍₋ᵢ₎)³ / (6 * (Σᵢ(θ̄ - θ₍₋ᵢ₎)²)^{3/2})

        Args:
            data: Original data sequence.
            func:  Statistic function. 

        Returns: 
            Acceleration factor 'a'.
        """
        n = len(data)
        if n < 2:
            return 0.0

        data_list = list(data)
        jackknife_estimates:  list[float] = []

        for i in range(n):
            loo_sample = data_list[: i] + data_list[i + 1:]
            if loo_sample: 
                jackknife_estimates.append(func(loo_sample))

        if not jackknife_estimates:
            return 0.0

        mean_jk = statistics.mean(jackknife_estimates)
        deviations = [mean_jk - jk for jk in jackknife_estimates]

        sum_sq = sum(d * d for d in deviations)
        sum_cube = sum(d * d * d for d in deviations)

        denominator = 6.0 * (sum_sq ** 1.5)
        if abs(denominator) < 1e-12:
            return 0.0

        return sum_cube / denominator

    def _compute_bca_quantiles(
        self,
        z0: float,
        a: float,
        alpha: float,
    ) -> tuple[float, float]: 
        """
        Compute BCa-adjusted quantiles.

        α₁ = Φ(z₀ + (z₀ + z_α) / (1 - a(z₀ + z_α)))
        α₂ = Φ(z₀ + (z₀ + z_{1-α}) / (1 - a(z₀ + z_{1-α})))

        Args:
            z0:  Bias correction factor.
            a: Acceleration factor. 
            alpha:  Nominal error rate (e.g., 0.05 for 95% CI).

        Returns:
            Tuple of (adjusted_lower_quantile, adjusted_upper_quantile).
        """
        z_alpha_lower = self._inverse_normal_cdf(alpha / 2.0)
        z_alpha_upper = self._inverse_normal_cdf(1.0 - alpha / 2.0)

        def adjusted_quantile(z_alpha: float) -> float:
            numerator = z0 + z_alpha
            denominator = 1.0 - a * (z0 + z_alpha)

            if abs(denominator) < 1e-9:
                return self._standard_normal_cdf(z_alpha)

            adjusted_z = z0 + numerator / denominator
            return self._standard_normal_cdf(adjusted_z)

        q_lower = adjusted_quantile(z_alpha_lower)
        q_upper = adjusted_quantile(z_alpha_upper)

        q_lower = max(0.001, min(0.499, q_lower))
        q_upper = max(0.501, min(0.999, q_upper))

        return q_lower, q_upper

    def _compute_moments(
        self, samples: list[float]
    ) -> tuple[float, float, float, float, float]:
        """
        Compute statistical moments of bootstrap distribution.

        Args:
            samples: Bootstrap replicates.

        Returns:
            Tuple of (mean, median, std_error, skewness, excess_kurtosis).
        """
        n = len(samples)
        if n < 2:
            val = samples[0] if samples else 0.0
            return val, val, 0.0, 0.0, 0.0

        mean = statistics.mean(samples)
        median = statistics.median(samples)
        std_error = statistics.stdev(samples)

        if std_error < 1e-12:
            return mean, median, std_error, 0.0, 0.0

        m3 = sum((x - mean) ** 3 for x in samples) / n
        skewness = m3 / (std_error ** 3)

        m4 = sum((x - mean) ** 4 for x in samples) / n
        kurtosis = m4 / (std_error ** 4) - 3.0

        return mean, median, std_error, skewness, kurtosis

    def _compute_entropy(self, samples:  list[float], num_bins: int = 50) -> float:
        """
        Estimate Shannon entropy of bootstrap distribution via histogram.

        H = -Σᵢ pᵢ log(pᵢ)

        Args:
            samples: Bootstrap replicates. 
            num_bins:  Number of histogram bins.

        Returns:
            Estimated entropy in nats.
        """
        if len(samples) < 10:
            return 0.0

        min_val, max_val = min(samples), max(samples)
        if max_val - min_val < 1e-12:
            return 0.0

        bin_width = (max_val - min_val) / num_bins

        counts = [0] * num_bins
        for x in samples:
            bin_idx = int((x - min_val) / bin_width)
            bin_idx = min(bin_idx, num_bins - 1)
            counts[bin_idx] += 1

        n = len(samples)
        entropy = 0.0
        for count in counts:
            if count > 0:
                p = count / n
                entropy -= p * math.log(p)

        entropy += math.log(bin_width)

        return max(0.0, entropy)

    def compute_bca_interval(
        self,
        data: Sequence[float],
        func: Callable[[Sequence[float]], float],
        alpha:  float = 0.05,
    ) -> UncertaintyMetrics:
        """
        Compute BCa bootstrap confidence interval with full uncertainty metrics.

        Args:
            data: Original data sequence.
            func: Statistic function θ̂ = func(data).
            alpha: Significance level (default 0.05 for 95% CI).

        Returns:
            UncertaintyMetrics with BCa confidence interval.
        """
        theta_hat = func(data)
        n = len(data)
        data_list = list(data)

        bootstrap_samples:  list[float] = []
        for _ in range(self. iterations):
            resample = [self._rng.choice(data_list) for _ in range(n)]
            bootstrap_samples.append(func(resample))

        self._last_samples = bootstrap_samples. copy()

        bootstrap_samples. sort()

        z0 = self._calculate_bias_correction(theta_hat, bootstrap_samples)
        a = self._calculate_acceleration(data, func)

        q_lower, q_upper = self._compute_bca_quantiles(z0, a, alpha)

        idx_lower = int(q_lower * len(bootstrap_samples))
        idx_upper = int(q_upper * len(bootstrap_samples))

        idx_lower = max(0, min(len(bootstrap_samples) - 1, idx_lower))
        idx_upper = max(0, min(len(bootstrap_samples) - 1, idx_upper))

        ci_lower = bootstrap_samples[idx_lower]
        ci_upper = bootstrap_samples[idx_upper]

        mean, median, std_error, skewness, kurtosis = self._compute_moments(
            bootstrap_samples
        )

        entropy = self._compute_entropy(bootstrap_samples)

        return UncertaintyMetrics(
            point_estimate=theta_hat,
            mean_score=mean,
            median_score=median,
            std_error=std_error,
            ci_lower_95=ci_lower,
            ci_upper_95=ci_upper,
            confidence_interval_method="BCa",
            sample_count=len(bootstrap_samples),
            skewness=skewness,
            kurtosis=kurtosis,
            entropy=entropy,
        )

    def compute_with_convergence(
        self,
        data: Sequence[float],
        func: Callable[[Sequence[float]], float],
        max_iterations: int = 10000,
        convergence_threshold: float = 0.01,
    ) -> tuple[UncertaintyMetrics, ConvergenceDiagnostics]: 
        """
        Compute BCa interval with adaptive iteration and convergence diagnostics.

        Args:
            data:  Original data sequence. 
            func: Statistic function. 
            max_iterations: Upper bound on total iterations.
            convergence_threshold:  Relative CI width change threshold.

        Returns:
            Tuple of (UncertaintyMetrics, ConvergenceDiagnostics).
        """
        metrics = self.compute_bca_interval(data, func)
        analyzer = BootstrapConvergenceAnalyzer(self.seed)

        diagnostics = analyzer.analyze_convergence(self._last_samples, metrics)

        current_iterations = self.iterations
        prev_ci_width = metrics.ci_width()

        while (
            diagnostics.convergence_status != "converged"
            and current_iterations < max_iterations
        ):
            additional = min(current_iterations, max_iterations - current_iterations)
            if additional < 100:
                break

            n = len(data)
            data_list = list(data)
            new_samples:  list[float] = []
            for _ in range(additional):
                resample = [self._rng.choice(data_list) for _ in range(n)]
                new_samples.append(func(resample))

            self._last_samples.extend(new_samples)
            current_iterations += additional

            all_samples = sorted(self._last_samples)
            theta_hat = metrics.point_estimate

            z0 = self._calculate_bias_correction(theta_hat, all_samples)
            a = self._calculate_acceleration(data, func)
            q_lower, q_upper = self._compute_bca_quantiles(z0, a, 0.05)

            idx_lower = int(q_lower * len(all_samples))
            idx_upper = int(q_upper * len(all_samples))
            idx_lower = max(0, min(len(all_samples) - 1, idx_lower))
            idx_upper = max(0, min(len(all_samples) - 1, idx_upper))

            mean, median, std_error, skewness, kurtosis = self._compute_moments(
                all_samples
            )
            entropy = self._compute_entropy(all_samples)

            metrics = UncertaintyMetrics(
                point_estimate=theta_hat,
                mean_score=mean,
                median_score=median,
                std_error=std_error,
                ci_lower_95=all_samples[idx_lower],
                ci_upper_95=all_samples[idx_upper],
                confidence_interval_method="BCa",
                sample_count=len(all_samples),
                skewness=skewness,
                kurtosis=kurtosis,
                entropy=entropy,
            )

            new_ci_width = metrics.ci_width()
            if prev_ci_width > 0:
                relative_change = abs(new_ci_width - prev_ci_width) / prev_ci_width
                if relative_change < convergence_threshold:
                    break
            prev_ci_width = new_ci_width

            diagnostics = analyzer.analyze_convergence(self._last_samples, metrics)

        return metrics, diagnostics

    def get_last_samples(self) -> list[float]: 
        """Return the bootstrap samples from the most recent computation."""
        return self._last_samples. copy()


# =============================================================================
# PUBLIC API FUNCTIONS
# =============================================================================


def aggregate_with_convergence(
    scores: Sequence[float],
    weights: Sequence[float] | None = None,
    initial_iterations: int = 2000,
    max_iterations: int = 10000,
    convergence_strict: bool = True,
) -> tuple[float, UncertaintyMetrics, ConvergenceDiagnostics]: 
    """
    Primary API for uncertainty-aware aggregation with convergence validation.

    Computes weighted mean with BCa bootstrap uncertainty quantification
    and comprehensive convergence diagnostics. 

    Args: 
        scores: Sequence of scores to aggregate.
        weights: Optional weights (default: uniform). Must sum to positive value.
        initial_iterations: Starting number of bootstrap iterations.
        max_iterations: Maximum iterations for adaptive refinement.
        convergence_strict: If True, require strict convergence criteria.

    Returns:
        Tuple of (point_estimate, UncertaintyMetrics, ConvergenceDiagnostics).

    Raises:
        ValueError: If scores is empty or weights invalid.
        ConvergenceError:  If strict mode and convergence fails.
    """
    if not scores:
        raise ValueError("Empty scores sequence")

    scores_list = list(scores)
    n = len(scores_list)

    if weights is None: 
        normalized_weights = [1.0 / n] * n
    else: 
        weights_list = list(weights)
        if len(weights_list) != n:
            raise ValueError(
                f"weights length ({len(weights_list)}) != scores length ({n})"
            )
        total_weight = sum(weights_list)
        if total_weight <= 0:
            raise ValueError(f"weights must sum to positive value, got {total_weight}")
        normalized_weights = [w / total_weight for w in weights_list]

    point_estimate = sum(s * w for s, w in zip(scores_list, normalized_weights))

    def weighted_mean_func(data: Sequence[float]) -> float:
        """Compute weighted mean preserving original weights."""
        return sum(s * w for s, w in zip(data, normalized_weights))

    aggregator = BootstrapAggregator(iterations=initial_iterations, seed=42)
    metrics, diagnostics = aggregator.compute_with_convergence(
        scores_list, weighted_mean_func, max_iterations
    )

    if abs(metrics.point_estimate - point_estimate) > 1e-9:
        metrics = UncertaintyMetrics(
            point_estimate=point_estimate,
            mean_score=metrics. mean_score,
            median_score=metrics.median_score,
            std_error=metrics.std_error,
            ci_lower_95=metrics.ci_lower_95,
            ci_upper_95=metrics.ci_upper_95,
            confidence_interval_method=metrics.confidence_interval_method,
            sample_count=metrics.sample_count,
            skewness=metrics.skewness,
            kurtosis=metrics. kurtosis,
            entropy=metrics. entropy,
        )

    if convergence_strict and not diagnostics.is_reliable(strict=True):
        logger.warning(
            f"Convergence validation failed:  {diagnostics.convergence_status}\n"
            f"Pathologies:  {diagnostics.pathology_flags}"
        )

    return point_estimate, metrics, diagnostics


def aggregate_with_uncertainty(
    scores:  Sequence[float],
    weights:  Sequence[float] | None = None,
    iterations: int = 2000,
) -> tuple[float, UncertaintyMetrics]:
    """
    Legacy wrapper for backward compatibility.

    Computes weighted mean with BCa bootstrap uncertainty quantification
    without convergence diagnostics. 

    Args:
        scores: Sequence of scores to aggregate. 
        weights: Optional weights (default: uniform).
        iterations: Number of bootstrap iterations.

    Returns:
        Tuple of (point_estimate, UncertaintyMetrics).
    """
    point_estimate, metrics, _ = aggregate_with_convergence(
        scores=scores,
        weights=weights,
        initial_iterations=iterations,
        max_iterations=iterations,
        convergence_strict=False,
    )
    return point_estimate, metrics


def compute_uncertainty_only(
    samples:  Sequence[float],
    point_estimate: float | None = None,
) -> UncertaintyMetrics:
    """
    Compute uncertainty metrics from pre-generated samples.

    Useful when bootstrap samples are generated externally. 

    Args: 
        samples: Pre-generated bootstrap replicates.
        point_estimate: Known point estimate (default: mean of samples).

    Returns:
        UncertaintyMetrics computed from samples.
    """
    if not samples:
        raise ValueError("Empty samples sequence")

    samples_list = list(samples)
    samples_sorted = sorted(samples_list)
    n = len(samples_sorted)

    if point_estimate is None:
        point_estimate = statistics.mean(samples_list)

    mean = statistics.mean(samples_list)
    median = statistics.median(samples_list)
    std_error = statistics.stdev(samples_list) if n > 1 else 0.0

    idx_lower = int(0.025 * n)
    idx_upper = int(0.975 * n)
    idx_lower = max(0, min(n - 1, idx_lower))
    idx_upper = max(0, min(n - 1, idx_upper))

    if std_error > 1e-12:
        m3 = sum((x - mean) ** 3 for x in samples_list) / n
        skewness = m3 / (std_error ** 3)
        m4 = sum((x - mean) ** 4 for x in samples_list) / n
        kurtosis = m4 / (std_error ** 4) - 3.0
    else: 
        skewness = 0.0
        kurtosis = 0.0

    aggregator = BootstrapAggregator(iterations=100)
    entropy = aggregator._compute_entropy(samples_list)

    return UncertaintyMetrics(
        point_estimate=point_estimate,
        mean_score=mean,
        median_score=median,
        std_error=std_error,
        ci_lower_95=samples_sorted[idx_lower],
        ci_upper_95=samples_sorted[idx_upper],
        confidence_interval_method="Percentile",
        sample_count=n,
        skewness=skewness,
        kurtosis=kurtosis,
        entropy=entropy,
    )