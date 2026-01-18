"""
Phase 5 Statistical Primitives

This module provides statistical analysis functions and metrics computation
for Phase 5 area aggregation and synthesis.

Module: src/farfan_pipeline/phases/Phase_05/primitives/phase5_00_00_statistical_primitives.py
Layer: primitives
Dependencies: phase5_00_00_types
"""
from __future__ import annotations

__version__ = "2.0.0"
__phase__ = 5
__stage__ = 0
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__layer__ = "primitives"

import logging
import math
from typing import Any

from farfan_pipeline.phases.Phase_05.primitives.phase5_00_00_types import (
    StatisticalMetrics,
)

logger = logging.getLogger(__name__)


def compute_statistical_metrics(scores: list[float]) -> StatisticalMetrics:
    """
    Compute comprehensive statistical metrics for a list of scores.

    Args:
        scores: List of scores to analyze

    Returns:
        StatisticalMetrics object with all computed metrics
    """
    if not scores:
        logger.warning("Empty scores list provided to compute_statistical_metrics")
        return StatisticalMetrics()

    n = len(scores)
    sorted_scores = sorted(scores)

    # Basic metrics
    mean = sum(scores) / n
    min_score = min(scores)
    max_score = max(scores)
    score_range = max_score - min_score

    # Median
    if n % 2 == 0:
        median = (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
    else:
        median = sorted_scores[n // 2]

    # Variance and standard deviation
    variance = sum((x - mean) ** 2 for x in scores) / n
    std_dev = math.sqrt(variance)

    # Coefficient of variation (normalized dispersion)
    cv = (std_dev / mean) if mean != 0 else 0.0

    # Percentiles
    p25_idx = int(n * 0.25)
    p75_idx = int(n * 0.75)
    percentile_25 = sorted_scores[p25_idx]
    percentile_75 = sorted_scores[p75_idx]
    iqr = percentile_75 - percentile_25

    # Skewness (third moment)
    if std_dev > 0:
        skewness = sum((x - mean) ** 3 for x in scores) / (n * std_dev ** 3)
    else:
        skewness = 0.0

    # Kurtosis (fourth moment)
    if std_dev > 0:
        kurtosis = sum((x - mean) ** 4 for x in scores) / (n * std_dev ** 4) - 3.0
    else:
        kurtosis = 0.0

    return StatisticalMetrics(
        mean=mean,
        median=median,
        std_dev=std_dev,
        variance=variance,
        min_score=min_score,
        max_score=max_score,
        range=score_range,
        coefficient_of_variation=cv,
        skewness=skewness,
        kurtosis=kurtosis,
        percentile_25=percentile_25,
        percentile_75=percentile_75,
        iqr=iqr,
    )


def compute_correlation(scores1: list[float], scores2: list[float]) -> float:
    """
    Compute Pearson correlation coefficient between two score lists.

    Args:
        scores1: First list of scores
        scores2: Second list of scores

    Returns:
        Correlation coefficient in [-1.0, 1.0]
    """
    if len(scores1) != len(scores2) or not scores1:
        logger.warning("Invalid inputs for correlation computation")
        return 0.0

    n = len(scores1)
    mean1 = sum(scores1) / n
    mean2 = sum(scores2) / n

    numerator = sum((scores1[i] - mean1) * (scores2[i] - mean2) for i in range(n))

    sum_sq1 = sum((x - mean1) ** 2 for x in scores1)
    sum_sq2 = sum((x - mean2) ** 2 for x in scores2)

    denominator = math.sqrt(sum_sq1 * sum_sq2)

    if denominator == 0:
        return 0.0

    return numerator / denominator


def detect_outliers_iqr(
    scores: list[float],
    multiplier: float = 1.5,
) -> list[int]:
    """
    Detect outliers using the IQR (Interquartile Range) method.

    Args:
        scores: List of scores
        multiplier: IQR multiplier (default: 1.5 for mild outliers)

    Returns:
        List of indices of outlier scores
    """
    if len(scores) < 4:
        return []

    sorted_scores = sorted(scores)
    n = len(sorted_scores)

    # Compute Q1, Q3, IQR
    q1 = sorted_scores[int(n * 0.25)]
    q3 = sorted_scores[int(n * 0.75)]
    iqr = q3 - q1

    # Compute bounds
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr

    # Find outliers
    outliers = []
    for i, score in enumerate(scores):
        if score < lower_bound or score > upper_bound:
            outliers.append(i)

    return outliers


def detect_outliers_zscore(
    scores: list[float],
    threshold: float = 3.0,
) -> list[int]:
    """
    Detect outliers using the Z-score method.

    Args:
        scores: List of scores
        threshold: Z-score threshold (default: 3.0)

    Returns:
        List of indices of outlier scores
    """
    if len(scores) < 2:
        return []

    mean = sum(scores) / len(scores)
    variance = sum((x - mean) ** 2 for x in scores) / len(scores)
    std_dev = math.sqrt(variance)

    if std_dev == 0:
        return []

    outliers = []
    for i, score in enumerate(scores):
        z_score = abs((score - mean) / std_dev)
        if z_score > threshold:
            outliers.append(i)

    return outliers


def compute_robust_mean(
    scores: list[float],
    trim_percent: float = 0.1,
) -> float:
    """
    Compute trimmed mean (robust to outliers).

    Args:
        scores: List of scores
        trim_percent: Percentage to trim from each end (default: 10%)

    Returns:
        Robust mean value
    """
    if not scores:
        return 0.0

    n = len(scores)
    trim_count = int(n * trim_percent)

    if trim_count * 2 >= n:
        # Not enough data to trim, return regular mean
        return sum(scores) / n

    sorted_scores = sorted(scores)
    trimmed = sorted_scores[trim_count : n - trim_count]

    return sum(trimmed) / len(trimmed)


def compute_weighted_median(
    scores: list[float],
    weights: list[float],
) -> float:
    """
    Compute weighted median.

    Args:
        scores: List of scores
        weights: List of weights (must sum to 1.0)

    Returns:
        Weighted median value
    """
    if not scores or len(scores) != len(weights):
        logger.warning("Invalid inputs for weighted median")
        return 0.0

    # Sort by score, keeping weights aligned
    paired = sorted(zip(scores, weights), key=lambda x: x[0])

    cumulative_weight = 0.0
    for score, weight in paired:
        cumulative_weight += weight
        if cumulative_weight >= 0.5:
            return score

    # Fallback (should not reach here if weights sum to 1.0)
    return paired[-1][0]


def compute_entropy(scores: list[float], bins: int = 10) -> float:
    """
    Compute Shannon entropy of score distribution.

    Higher entropy = more uniform distribution
    Lower entropy = more concentrated distribution

    Args:
        scores: List of scores
        bins: Number of bins for histogram (default: 10)

    Returns:
        Entropy value (non-negative)
    """
    if not scores:
        return 0.0

    # Create histogram
    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        return 0.0

    bin_width = (max_score - min_score) / bins
    histogram = [0] * bins

    for score in scores:
        bin_idx = int((score - min_score) / bin_width)
        bin_idx = min(bin_idx, bins - 1)  # Handle edge case
        histogram[bin_idx] += 1

    # Compute entropy
    n = len(scores)
    entropy = 0.0
    for count in histogram:
        if count > 0:
            p = count / n
            entropy -= p * math.log2(p)

    return entropy


def compute_gini_coefficient(scores: list[float]) -> float:
    """
    Compute Gini coefficient (inequality measure).

    0.0 = perfect equality (all scores the same)
    1.0 = maximum inequality

    Args:
        scores: List of scores

    Returns:
        Gini coefficient in [0.0, 1.0]
    """
    if not scores:
        return 0.0

    sorted_scores = sorted(scores)
    n = len(sorted_scores)

    cumulative_sum = sum((i + 1) * score for i, score in enumerate(sorted_scores))
    total_sum = sum(sorted_scores)

    if total_sum == 0:
        return 0.0

    gini = (2 * cumulative_sum) / (n * total_sum) - (n + 1) / n

    return gini


def compute_consistency_score(scores: list[float]) -> float:
    """
    Compute consistency score (inverse of coefficient of variation).

    1.0 = perfect consistency (no variation)
    0.0 = maximum inconsistency

    Args:
        scores: List of scores

    Returns:
        Consistency score in [0.0, 1.0]
    """
    if not scores:
        return 1.0

    mean = sum(scores) / len(scores)

    if mean == 0:
        return 1.0

    variance = sum((x - mean) ** 2 for x in scores) / len(scores)
    std_dev = math.sqrt(variance)

    cv = std_dev / mean

    # Convert CV to consistency score (inverse relationship)
    # Use exponential decay: consistency = exp(-cv)
    consistency = math.exp(-cv)

    return consistency


__all__ = [
    "compute_statistical_metrics",
    "compute_correlation",
    "detect_outliers_iqr",
    "detect_outliers_zscore",
    "compute_robust_mean",
    "compute_weighted_median",
    "compute_entropy",
    "compute_gini_coefficient",
    "compute_consistency_score",
]
