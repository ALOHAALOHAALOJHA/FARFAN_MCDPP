"""
Phase 5 Comparative Analytics Primitives

This module provides comparative analysis functions for cross-area benchmarking,
ranking, and relative performance assessment.

Module: src/farfan_pipeline/phases/Phase_05/primitives/phase5_00_00_comparative_analytics.py
Layer: primitives
Dependencies: phase5_00_00_types, phase5_00_00_statistical_primitives
"""
from __future__ import annotations

__version__ = "2.0.0"
__phase__ = 5
__stage__ = 0
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__layer__ = "primitives"

import logging
from typing import Any

from farfan_pipeline.phases.Phase_05.primitives.phase5_00_00_types import (
    ComparativeMetrics,
)

logger = logging.getLogger(__name__)


def compute_comparative_metrics(
    area_id: str,
    area_score: float,
    all_scores: list[float],
    cluster_scores: list[float] | None = None,
) -> ComparativeMetrics:
    """
    Compute comparative metrics for an area relative to all other areas.

    Args:
        area_id: Area identifier
        area_score: Score for the area
        all_scores: List of all area scores (including this one)
        cluster_scores: Optional list of scores within the same cluster

    Returns:
        ComparativeMetrics object
    """
    if not all_scores:
        logger.warning(f"No scores provided for comparative analysis of {area_id}")
        return ComparativeMetrics()

    n = len(all_scores)

    # Compute rank (1 = best)
    sorted_scores = sorted(all_scores, reverse=True)
    rank = sorted_scores.index(area_score) + 1

    # Compute percentile
    percentile = (n - rank + 1) / n * 100

    # Compute global statistics
    global_mean = sum(all_scores) / n
    global_variance = sum((x - global_mean) ** 2 for x in all_scores) / n
    global_std = global_variance ** 0.5

    # Deviation from mean
    deviation_from_mean = area_score - global_mean

    # Z-score
    if global_std > 0:
        z_score = deviation_from_mean / global_std
    else:
        z_score = 0.0

    # Count comparisons
    better_than_count = sum(1 for s in all_scores if area_score > s)
    worse_than_count = sum(1 for s in all_scores if area_score < s)

    # Cluster metrics (if provided)
    cluster_rank = 0
    cluster_percentile = 0.0
    if cluster_scores and len(cluster_scores) > 1:
        cluster_sorted = sorted(cluster_scores, reverse=True)
        cluster_rank = cluster_sorted.index(area_score) + 1
        cluster_percentile = (len(cluster_scores) - cluster_rank + 1) / len(cluster_scores) * 100

    return ComparativeMetrics(
        rank=rank,
        percentile=percentile,
        deviation_from_mean=deviation_from_mean,
        z_score=z_score,
        better_than_count=better_than_count,
        worse_than_count=worse_than_count,
        cluster_rank=cluster_rank,
        cluster_percentile=cluster_percentile,
    )


def rank_areas(
    area_scores: dict[str, float],
    descending: bool = True,
) -> list[tuple[str, float, int]]:
    """
    Rank all areas by score.

    Args:
        area_scores: Dict mapping area_id to score
        descending: If True, rank 1 = highest score (default: True)

    Returns:
        List of (area_id, score, rank) tuples
    """
    sorted_items = sorted(
        area_scores.items(),
        key=lambda x: x[1],
        reverse=descending,
    )

    return [(area_id, score, idx + 1) for idx, (area_id, score) in enumerate(sorted_items)]


def compute_relative_gaps(
    area_scores: dict[str, float],
) -> dict[str, dict[str, float]]:
    """
    Compute pairwise gaps between all areas.

    Args:
        area_scores: Dict mapping area_id to score

    Returns:
        Nested dict: {area_id_1: {area_id_2: gap, ...}, ...}
        gap = score_1 - score_2 (positive = area_1 is better)
    """
    gaps = {}

    for area_id_1, score_1 in area_scores.items():
        gaps[area_id_1] = {}
        for area_id_2, score_2 in area_scores.items():
            if area_id_1 != area_id_2:
                gaps[area_id_1][area_id_2] = score_1 - score_2

    return gaps


def identify_peers(
    area_id: str,
    area_score: float,
    all_scores: dict[str, float],
    tolerance: float = 0.2,
) -> list[str]:
    """
    Identify peer areas with similar scores.

    Args:
        area_id: Target area identifier
        area_score: Score for the target area
        all_scores: Dict mapping all area_ids to scores
        tolerance: Score difference tolerance (default: 0.2)

    Returns:
        List of peer area_ids (excluding the target area)
    """
    peers = []

    for other_id, other_score in all_scores.items():
        if other_id != area_id:
            if abs(area_score - other_score) <= tolerance:
                peers.append(other_id)

    return peers


def identify_outliers(
    area_scores: dict[str, float],
    method: str = "zscore",
    threshold: float = 2.0,
) -> list[str]:
    """
    Identify outlier areas.

    Args:
        area_scores: Dict mapping area_id to score
        method: Outlier detection method ("zscore" or "iqr")
        threshold: Threshold for outlier detection

    Returns:
        List of outlier area_ids
    """
    if not area_scores:
        return []

    scores = list(area_scores.values())

    if method == "zscore":
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        std = variance ** 0.5

        if std == 0:
            return []

        outliers = []
        for area_id, score in area_scores.items():
            z_score = abs((score - mean) / std)
            if z_score > threshold:
                outliers.append(area_id)

        return outliers

    elif method == "iqr":
        sorted_scores = sorted(scores)
        n = len(sorted_scores)

        q1 = sorted_scores[int(n * 0.25)]
        q3 = sorted_scores[int(n * 0.75)]
        iqr = q3 - q1

        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        outliers = []
        for area_id, score in area_scores.items():
            if score < lower_bound or score > upper_bound:
                outliers.append(area_id)

        return outliers

    else:
        logger.warning(f"Unknown outlier detection method: {method}")
        return []


def compute_cluster_statistics(
    cluster_assignments: dict[str, str],
    area_scores: dict[str, float],
) -> dict[str, dict[str, float]]:
    """
    Compute statistics for each cluster.

    Args:
        cluster_assignments: Dict mapping area_id to cluster_id
        area_scores: Dict mapping area_id to score

    Returns:
        Dict mapping cluster_id to statistics dict
    """
    # Group scores by cluster
    cluster_scores: dict[str, list[float]] = {}

    for area_id, cluster_id in cluster_assignments.items():
        if cluster_id not in cluster_scores:
            cluster_scores[cluster_id] = []
        if area_id in area_scores:
            cluster_scores[cluster_id].append(area_scores[area_id])

    # Compute statistics for each cluster
    statistics = {}

    for cluster_id, scores in cluster_scores.items():
        if not scores:
            continue

        n = len(scores)
        mean = sum(scores) / n
        variance = sum((x - mean) ** 2 for x in scores) / n
        std = variance ** 0.5

        statistics[cluster_id] = {
            "count": n,
            "mean": mean,
            "std": std,
            "min": min(scores),
            "max": max(scores),
            "range": max(scores) - min(scores),
        }

    return statistics


def compute_performance_tiers(
    area_scores: dict[str, float],
    tier_count: int = 3,
) -> dict[str, str]:
    """
    Assign areas to performance tiers.

    Args:
        area_scores: Dict mapping area_id to score
        tier_count: Number of tiers (default: 3 for high/medium/low)

    Returns:
        Dict mapping area_id to tier label
    """
    if not area_scores or tier_count < 2:
        return {}

    sorted_items = sorted(area_scores.items(), key=lambda x: x[1], reverse=True)
    n = len(sorted_items)
    tier_size = n // tier_count

    tier_labels = [f"Tier_{i+1}" for i in range(tier_count)]

    tier_assignments = {}

    for idx, (area_id, _) in enumerate(sorted_items):
        tier_idx = min(idx // tier_size, tier_count - 1)
        tier_assignments[area_id] = tier_labels[tier_idx]

    return tier_assignments


def compute_gap_to_excellence(
    area_score: float,
    excellence_threshold: float = 2.55,  # 85% of 3.0
) -> dict[str, float]:
    """
    Compute gap to excellence threshold.

    Args:
        area_score: Score for the area
        excellence_threshold: Excellence threshold (default: 2.55 = 85% of 3.0)

    Returns:
        Dict with gap analysis
    """
    gap = excellence_threshold - area_score

    return {
        "current_score": area_score,
        "excellence_threshold": excellence_threshold,
        "gap": max(0.0, gap),
        "gap_percentage": max(0.0, gap / excellence_threshold * 100),
        "is_excellent": area_score >= excellence_threshold,
    }


def compute_improvement_potential(
    area_score: float,
    dimension_scores: list[float],
    max_score: float = 3.0,
) -> dict[str, float]:
    """
    Compute improvement potential for an area.

    Args:
        area_score: Current area score
        dimension_scores: List of dimension scores
        max_score: Maximum possible score (default: 3.0)

    Returns:
        Dict with improvement potential metrics
    """
    if not dimension_scores:
        return {
            "current_score": area_score,
            "max_potential": max_score,
            "improvement_potential": max_score - area_score,
            "utilization_rate": area_score / max_score if max_score > 0 else 0.0,
        }

    # Identify weakest dimensions (biggest improvement opportunities)
    weakest_score = min(dimension_scores)
    strongest_score = max(dimension_scores)

    # Theoretical maximum if all dimensions reach current best
    theoretical_max = sum(max(dimension_scores) for _ in dimension_scores) / len(dimension_scores)

    return {
        "current_score": area_score,
        "max_potential": max_score,
        "theoretical_max": theoretical_max,
        "improvement_potential": max_score - area_score,
        "quick_win_potential": theoretical_max - area_score,
        "utilization_rate": area_score / max_score if max_score > 0 else 0.0,
        "weakest_dimension_score": weakest_score,
        "strongest_dimension_score": strongest_score,
        "dimension_gap": strongest_score - weakest_score,
    }


__all__ = [
    "compute_comparative_metrics",
    "rank_areas",
    "compute_relative_gaps",
    "identify_peers",
    "identify_outliers",
    "compute_cluster_statistics",
    "compute_performance_tiers",
    "compute_gap_to_excellence",
    "compute_improvement_potential",
]
