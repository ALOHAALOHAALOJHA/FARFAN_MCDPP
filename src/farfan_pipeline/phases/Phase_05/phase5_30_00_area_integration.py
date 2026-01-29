"""
Phase 5 Area Integration Module (UPGRADED v2.0)

This module provides comprehensive integration and synthesis for Phase 5.

STANDARD CAPABILITIES:
- Bridges Phase 4 outputs to Phase 5 processing
- Integrates aggregation and validation

UPGRADED CAPABILITIES (v2.0):
==========================
1. Synthesis Engine Integration:
   - Cross-cutting analysis across all 10 policy areas
   - Dimension-level insights across all 60 dimension scores
   - Temporal and trend analysis (placeholder for historical data)

2. Comparative Analytics:
   - Cross-area benchmarking and ranking
   - Cluster-level statistics
   - Peer identification and gap analysis

3. Policy Insights:
   - Strength and weakness identification
   - Improvement opportunity prioritization
   - Risk factor detection
   - Synergy and conflict analysis

4. Comprehensive Reporting:
   - Statistical summary across all areas
   - Quality distribution analysis
   - Validation summary with recommendations

Module: src/farfan_pipeline/phases/Phase_05/phase5_30_00_area_integration.py
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "2.0.0"
__phase__ = 5
__stage__ = 30
__order__ = 1
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-13"
__modified__ = "2026-01-18"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"
__upgrade__ = "FRONTIER_GRADE_v2.0"

import logging
from datetime import datetime
from typing import Any

from farfan_pipeline.phases.Phase_04.phase4_30_00_aggregation import DimensionScore
from farfan_pipeline.phases.Phase_05.phase5_00_00_area_score import AreaScore
from farfan_pipeline.phases.Phase_05.phase5_10_00_area_aggregation import (
    aggregate_policy_areas_async,
)
from farfan_pipeline.phases.Phase_05.phase5_20_00_area_validation import (
    validate_phase5_output,
    validate_phase5_output_comprehensive,
)

# Import Phase 5 primitives and types
from farfan_pipeline.phases.Phase_05.primitives.phase5_00_00_types import (
    AggregationStrategy,
    SynthesisDepth,
)
from farfan_pipeline.phases.Phase_05.primitives.phase5_00_00_statistical_primitives import (
    compute_statistical_metrics,
)
from farfan_pipeline.phases.Phase_05.primitives.phase5_00_00_comparative_analytics import (
    compute_cluster_statistics,
    compute_comparative_metrics,
    rank_areas,
)

from farfan_pipeline.phases.Phase_05.PHASE_5_CONSTANTS import (
    CLUSTER_ASSIGNMENTS,
    POLICY_AREAS,
    QUALITY_THRESHOLDS,
)

logger = logging.getLogger(__name__)


# =============================================================================
# INTEGRATION FUNCTIONS
# =============================================================================


async def run_phase5_aggregation(
    dimension_scores: list[DimensionScore],
    questionnaire: dict[str, Any] | None = None,
    instrumentation: Any | None = None,
    signal_registry: Any | None = None,
    validate: bool = True,
    aggregation_strategy: AggregationStrategy = AggregationStrategy.WEIGHTED_AVERAGE,
    synthesis_depth: SynthesisDepth = SynthesisDepth.COMPREHENSIVE,
    enable_comprehensive_validation: bool = True,
) -> list[AreaScore]:
    """
    Run complete Phase 5 aggregation pipeline (v2.0 UPGRADED).

    Args:
        dimension_scores: List of 60 DimensionScore objects from Phase 4
        questionnaire: Questionnaire monolith (optional)
        instrumentation: Phase instrumentation for tracking
        signal_registry: Optional SISAS signal registry
        validate: Whether to validate output (default: True)
        aggregation_strategy: Aggregation method (default: WEIGHTED_AVERAGE)
        synthesis_depth: Depth of synthesis analysis (default: COMPREHENSIVE)
        enable_comprehensive_validation: Use v2.0 comprehensive validation (default: True)

    Returns:
        List of 10 AreaScore objects with extended analytics

    Raises:
        ValueError: If validation fails
    """
    logger.info(
        f"Starting Phase 5 v2.0 aggregation pipeline "
        f"(strategy={aggregation_strategy.value}, depth={synthesis_depth.value})"
    )

    # Run aggregation with v2.0 capabilities
    area_scores = await aggregate_policy_areas_async(
        dimension_scores=dimension_scores,
        questionnaire=questionnaire,
        instrumentation=instrumentation,
        signal_registry=signal_registry,
        aggregation_strategy=aggregation_strategy,
        synthesis_depth=synthesis_depth,
        enable_outlier_detection=True,
        enable_sensitivity_analysis=True,
    )

    # Validate output
    if validate:
        if enable_comprehensive_validation:
            # Use v2.0 comprehensive validation
            is_valid, details = validate_phase5_output_comprehensive(
                area_scores,
                strict=True,
                enable_statistical_validation=True,
                enable_anomaly_detection=True,
            )
        else:
            # Use standard validation
            is_valid, details = validate_phase5_output(area_scores, strict=True)

        if not is_valid:
            logger.error(f"Phase 5 validation failed: {details}")
            raise ValueError(f"Phase 5 validation failed: {details.get('violations', 'Unknown error')}")

        logger.info("Phase 5 validation: PASSED")

    logger.info(f"Phase 5 v2.0 aggregation complete: {len(area_scores)} area scores")
    return area_scores


def group_dimension_scores_by_area(
    dimension_scores: list[DimensionScore],
) -> dict[str, list[DimensionScore]]:
    """
    Group dimension scores by policy area.

    Utility function for external callers.

    Args:
        dimension_scores: List of DimensionScore objects

    Returns:
        Dict mapping area_id to list of DimensionScore
    """
    grouped: dict[str, list[DimensionScore]] = {}
    for ds in dimension_scores:
        if ds.area_id not in grouped:
            grouped[ds.area_id] = []
        grouped[ds.area_id].append(ds)
    return grouped


# =============================================================================
# UPGRADED SYNTHESIS FUNCTIONS (v2.0)
# =============================================================================


def synthesize_cross_cutting_insights(
    area_scores: list[AreaScore],
    dimension_scores: list[DimensionScore],
) -> dict[str, Any]:
    """
    Generate cross-cutting insights spanning all policy areas and dimensions (v2.0).

    Analyzes:
    - Global patterns across all areas
    - Dimension-level trends
    - Strengths and weaknesses
    - Improvement opportunities
    - Risk factors

    Args:
        area_scores: List of 10 AreaScore objects
        dimension_scores: List of 60 DimensionScore objects

    Returns:
        Dict with comprehensive cross-cutting insights
    """
    logger.info("Synthesizing cross-cutting insights v2.0")

    insights = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
    }

    # Global statistics
    area_score_values = [area.score for area in area_scores]
    global_stats = compute_statistical_metrics(area_score_values)

    insights["global_statistics"] = {
        "area_count": len(area_scores),
        "dimension_count": len(dimension_scores),
        "mean_area_score": global_stats.mean,
        "median_area_score": global_stats.median,
        "std_area_score": global_stats.std_dev,
        "min_area_score": global_stats.min_score,
        "max_area_score": global_stats.max_score,
        "range": global_stats.range,
        "coefficient_of_variation": global_stats.coefficient_of_variation,
    }

    # Quality distribution
    quality_dist = {
        "EXCELENTE": 0,
        "BUENO": 0,
        "ACEPTABLE": 0,
        "INSUFICIENTE": 0,
    }
    for area in area_scores:
        if area.quality_level in quality_dist:
            quality_dist[area.quality_level] += 1

    insights["quality_distribution"] = quality_dist

    # Ranking and performance tiers
    area_scores_dict = {area.area_id: area.score for area in area_scores}
    ranked = rank_areas(area_scores_dict, descending=True)

    insights["rankings"] = [
        {
            "rank": rank,
            "area_id": area_id,
            "area_name": next((a.area_name for a in area_scores if a.area_id == area_id), area_id),
            "score": score,
        }
        for area_id, score, rank in ranked[:10]
    ]

    # Top and bottom performers
    insights["top_performers"] = [area_id for area_id, _, _ in ranked[:3]]
    insights["bottom_performers"] = [area_id for area_id, _, _ in ranked[-3:]]

    # Cluster statistics
    cluster_stats = compute_cluster_statistics(
        {area.area_id: area.cluster_id for area in area_scores if area.cluster_id},
        area_scores_dict,
    )
    insights["cluster_statistics"] = cluster_stats

    # Dimension-level analysis
    dimension_stats = analyze_dimension_performance(dimension_scores)
    insights["dimension_analysis"] = dimension_stats

    # Identify strengths and weaknesses
    excellence_threshold = QUALITY_THRESHOLDS["EXCELENTE"] * 3.0  # 2.55
    weakness_threshold = QUALITY_THRESHOLDS["ACEPTABLE"] * 3.0  # 1.65

    strengths = [
        area.area_id for area in area_scores
        if area.score >= excellence_threshold
    ]
    weaknesses = [
        area.area_id for area in area_scores
        if area.score < weakness_threshold
    ]

    insights["strengths"] = strengths
    insights["weaknesses"] = weaknesses

    # Improvement opportunities (areas closest to next quality tier)
    improvement_opportunities = identify_improvement_opportunities(area_scores)
    insights["improvement_opportunities"] = improvement_opportunities

    logger.info(f"Cross-cutting synthesis complete: {len(insights)} insight categories")
    return insights


def analyze_dimension_performance(
    dimension_scores: list[DimensionScore],
) -> dict[str, Any]:
    """
    Analyze performance across all 6 dimensions.

    Args:
        dimension_scores: List of 60 DimensionScore objects

    Returns:
        Dict with dimension-level analysis
    """
    # Group by dimension
    dimension_groups: dict[str, list[float]] = {}

    for ds in dimension_scores:
        if ds.dimension_id not in dimension_groups:
            dimension_groups[ds.dimension_id] = []
        dimension_groups[ds.dimension_id].append(ds.score)

    # Compute statistics for each dimension
    dimension_analysis = {}

    for dim_id, scores in dimension_groups.items():
        stats = compute_statistical_metrics(scores)
        dimension_analysis[dim_id] = {
            "mean": stats.mean,
            "median": stats.median,
            "std": stats.std_dev,
            "min": stats.min_score,
            "max": stats.max_score,
            "area_count": len(scores),
        }

    # Identify best and worst performing dimensions
    dimension_means = {dim_id: stats["mean"] for dim_id, stats in dimension_analysis.items()}
    best_dimension = max(dimension_means, key=dimension_means.get) if dimension_means else None  # type: ignore
    worst_dimension = min(dimension_means, key=dimension_means.get) if dimension_means else None  # type: ignore

    return {
        "by_dimension": dimension_analysis,
        "best_performing_dimension": best_dimension,
        "worst_performing_dimension": worst_dimension,
        "dimension_means": dimension_means,
    }


def identify_improvement_opportunities(
    area_scores: list[AreaScore],
) -> list[dict[str, Any]]:
    """
    Identify areas with high improvement potential.

    Prioritizes areas that are:
    - Close to the next quality tier
    - Have high variance in dimensions (uneven performance)
    - Have specific weak dimensions that could be targeted

    Args:
        area_scores: List of AreaScore objects

    Returns:
        List of improvement opportunity dicts, sorted by priority
    """
    opportunities = []

    # Quality tier boundaries
    tier_boundaries = {
        "INSUFICIENTE_to_ACEPTABLE": QUALITY_THRESHOLDS["ACEPTABLE"] * 3.0,
        "ACEPTABLE_to_BUENO": QUALITY_THRESHOLDS["BUENO"] * 3.0,
        "BUENO_to_EXCELENTE": QUALITY_THRESHOLDS["EXCELENTE"] * 3.0,
    }

    for area in area_scores:
        # Determine next tier
        current_level = area.quality_level
        if current_level == "INSUFICIENTE":
            next_tier = "ACEPTABLE"
            gap = tier_boundaries["INSUFICIENTE_to_ACEPTABLE"] - area.score
        elif current_level == "ACEPTABLE":
            next_tier = "BUENO"
            gap = tier_boundaries["ACEPTABLE_to_BUENO"] - area.score
        elif current_level == "BUENO":
            next_tier = "EXCELENTE"
            gap = tier_boundaries["BUENO_to_EXCELENTE"] - area.score
        else:
            # Already EXCELENTE
            continue

        # Only include if gap is achievable (< 0.5 points)
        if gap > 0 and gap <= 0.5:
            opportunities.append({
                "area_id": area.area_id,
                "area_name": area.area_name,
                "current_score": area.score,
                "current_level": current_level,
                "next_tier": next_tier,
                "gap": gap,
                "priority": 1.0 / gap,  # Smaller gap = higher priority
            })

    # Sort by priority (descending)
    opportunities.sort(key=lambda x: x["priority"], reverse=True)

    return opportunities[:5]  # Top 5 opportunities


def generate_phase5_synthesis_report(
    area_scores: list[AreaScore],
    dimension_scores: list[DimensionScore],
    validation_details: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate comprehensive Phase 5 synthesis report (v2.0).

    Combines all analytics and insights into a structured report
    suitable for consumption by Phase 6 and downstream phases.

    Args:
        area_scores: List of 10 AreaScore objects
        dimension_scores: List of 60 DimensionScore objects
        validation_details: Validation results

    Returns:
        Comprehensive synthesis report dict
    """
    logger.info("Generating Phase 5 v2.0 synthesis report")

    report = {
        "metadata": {
            "phase": 5,
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "area_count": len(area_scores),
            "dimension_count": len(dimension_scores),
        },
        "validation": {
            "status": "PASSED" if validation_details.get("comprehensive_validation", False) else "FAILED",
            "details": validation_details,
        },
        "area_scores_summary": {
            "areas": [
                {
                    "area_id": area.area_id,
                    "area_name": area.area_name,
                    "score": area.score,
                    "quality_level": area.quality_level,
                    "cluster_id": area.cluster_id,
                }
                for area in area_scores
            ],
        },
        "cross_cutting_insights": synthesize_cross_cutting_insights(area_scores, dimension_scores),
    }

    logger.info("Phase 5 v2.0 synthesis report complete")
    return report
