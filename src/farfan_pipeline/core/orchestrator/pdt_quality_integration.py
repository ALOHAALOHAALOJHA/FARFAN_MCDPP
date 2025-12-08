"""
PDT Quality Integration for Signal Intelligence Layer
=====================================================

Integrates Unit Layer (@u) metrics (S/M/I/P scores) into pattern filtering
to enhance precision by prioritizing patterns from high-quality PDT sections.

This module provides:
1. PDT section quality computation from Unit Layer metrics
2. Pattern boosting based on PDT quality thresholds (e.g., I_struct>0.8)
3. Precision improvement correlation tracking with PDT quality

Integration Impact:
- Pattern prioritization: Boost patterns from high-quality sections
- Precision improvement: Correlate PDT quality with pattern accuracy
- Quality thresholds: I_struct>0.8 for excellent, >0.6 for good, >0.4 for acceptable
- S/M/P tracking: Incorporate structural, mandatory, and PPI metrics

Author: F.A.R.F.A.N Pipeline
Date: 2025-01-10
Module: PDT Quality Integration Layer
"""

from dataclasses import dataclass
from typing import Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


PDT_QUALITY_THRESHOLDS = {
    "I_struct_excellent": 0.8,
    "I_struct_good": 0.6,
    "I_struct_acceptable": 0.4,
    "S_structural_min": 0.5,
    "M_mandatory_min": 0.5,
    "P_ppi_min": 0.5,
}

BOOST_FACTORS = {
    "excellent": 1.5,
    "good": 1.2,
    "acceptable": 1.0,
    "poor": 0.8,
}


@dataclass
class PDTQualityMetrics:
    """
    Metrics for PDT quality integration with signal patterns.

    Tracks Unit Layer (@u) component scores and their impact on pattern filtering.
    """

    S_structural: float = 0.0
    M_mandatory: float = 0.0
    I_struct: float = 0.0
    I_link: float = 0.0
    I_logic: float = 0.0
    I_total: float = 0.0
    P_presence: float = 0.0
    P_struct: float = 0.0
    P_consistency: float = 0.0
    P_total: float = 0.0
    U_total: float = 0.0
    quality_level: str = "unknown"
    section_name: str = ""
    boost_factor: float = 1.0
    patterns_boosted: int = 0
    precision_improvement: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "S_structural": self.S_structural,
            "M_mandatory": self.M_mandatory,
            "I_struct": self.I_struct,
            "I_link": self.I_link,
            "I_logic": self.I_logic,
            "I_total": self.I_total,
            "P_presence": self.P_presence,
            "P_struct": self.P_struct,
            "P_consistency": self.P_consistency,
            "P_total": self.P_total,
            "U_total": self.U_total,
            "quality_level": self.quality_level,
            "section_name": self.section_name,
            "boost_factor": self.boost_factor,
            "patterns_boosted": self.patterns_boosted,
            "precision_improvement": self.precision_improvement,
        }


@dataclass
class PDTSectionQuality:
    """Quality metrics for a specific PDT section."""

    section_name: str
    metrics: PDTQualityMetrics
    pattern_count: int = 0
    boosted_pattern_count: int = 0


def compute_pdt_section_quality(
    section_name: str,
    pdt_structure: Any | None = None,
    unit_layer_scores: dict[str, Any] | None = None,
) -> PDTQualityMetrics:
    """
    Compute PDT quality metrics for a section from Unit Layer evaluation.

    Args:
        section_name: Name of PDT section (e.g., "Diagnóstico", "PPI")
        pdt_structure: Optional PDTStructure with extracted data
        unit_layer_scores: Optional pre-computed Unit Layer scores

    Returns:
        PDTQualityMetrics with S/M/I/P component scores
    """
    metrics = PDTQualityMetrics(section_name=section_name)

    if unit_layer_scores:
        components = unit_layer_scores.get("components", {})
        metrics.S_structural = components.get("S", 0.0)
        metrics.M_mandatory = components.get("M", 0.0)
        metrics.I_struct = components.get("I_struct", 0.0)
        metrics.I_link = components.get("I_link", 0.0)
        metrics.I_logic = components.get("I_logic", 0.0)
        metrics.I_total = components.get("I", 0.0)
        metrics.P_presence = components.get("P_presence", 0.0)
        metrics.P_struct = components.get("P_struct", 0.0)
        metrics.P_consistency = components.get("P_consistency", 0.0)
        metrics.P_total = components.get("P", 0.0)
        metrics.U_total = unit_layer_scores.get("score", 0.0)
    elif pdt_structure:
        from farfan_pipeline.core.calibration.config import UnitLayerConfig
        from farfan_pipeline.core.calibration.unit_layer import UnitLayerEvaluator

        config = UnitLayerConfig()
        evaluator = UnitLayerEvaluator(config)
        layer_score = evaluator.evaluate(pdt_structure)

        components = layer_score.components
        metrics.S_structural = components.get("S", 0.0)
        metrics.M_mandatory = components.get("M", 0.0)
        metrics.I_struct = components.get("I_struct", 0.0)
        metrics.I_link = components.get("I_link", 0.0)
        metrics.I_logic = components.get("I_logic", 0.0)
        metrics.I_total = components.get("I", 0.0)
        metrics.P_presence = components.get("P_presence", 0.0)
        metrics.P_struct = components.get("P_struct", 0.0)
        metrics.P_consistency = components.get("P_consistency", 0.0)
        metrics.P_total = components.get("P", 0.0)
        metrics.U_total = layer_score.score

    I_struct = metrics.I_struct
    if I_struct >= PDT_QUALITY_THRESHOLDS["I_struct_excellent"]:
        metrics.quality_level = "excellent"
        metrics.boost_factor = BOOST_FACTORS["excellent"]
    elif I_struct >= PDT_QUALITY_THRESHOLDS["I_struct_good"]:
        metrics.quality_level = "good"
        metrics.boost_factor = BOOST_FACTORS["good"]
    elif I_struct >= PDT_QUALITY_THRESHOLDS["I_struct_acceptable"]:
        metrics.quality_level = "acceptable"
        metrics.boost_factor = BOOST_FACTORS["acceptable"]
    else:
        metrics.quality_level = "poor"
        metrics.boost_factor = BOOST_FACTORS["poor"]

    logger.info(
        "pdt_quality_computed",
        section=section_name,
        I_struct=I_struct,
        quality_level=metrics.quality_level,
        boost_factor=metrics.boost_factor,
    )

    return metrics


def apply_pdt_quality_boost(
    patterns: list[dict[str, Any]],
    pdt_quality_map: dict[str, PDTQualityMetrics],
    document_context: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Apply PDT quality-based boosting to patterns.

    Prioritizes patterns from high-quality PDT sections by:
    1. Computing quality score for each pattern's source section
    2. Applying boost factor based on I_struct threshold
    3. Reordering patterns by boosted priority

    Args:
        patterns: List of pattern specifications
        pdt_quality_map: Map of section names to quality metrics
        document_context: Optional document context for section detection

    Returns:
        Tuple of (boosted_patterns, boost_stats)
    """
    boosted_patterns = []
    boost_stats = {
        "total_patterns": len(patterns),
        "boosted_count": 0,
        "excellent_quality": 0,
        "good_quality": 0,
        "acceptable_quality": 0,
        "poor_quality": 0,
        "unknown_quality": 0,
        "avg_boost_factor": 0.0,
        "max_boost_factor": 0.0,
    }

    current_section = None
    if document_context:
        current_section = document_context.get("section") or document_context.get(
            "pdt_section"
        )

    total_boost = 0.0

    for pattern in patterns:
        pattern_section = (
            pattern.get("pdt_section")
            or pattern.get("source_section")
            or current_section
        )

        boost_factor = 1.0
        quality_level = "unknown"

        if pattern_section and pattern_section in pdt_quality_map:
            quality_metrics = pdt_quality_map[pattern_section]
            boost_factor = quality_metrics.boost_factor
            quality_level = quality_metrics.quality_level

            boost_stats["boosted_count"] += 1

            if quality_level == "excellent":
                boost_stats["excellent_quality"] += 1
            elif quality_level == "good":
                boost_stats["good_quality"] += 1
            elif quality_level == "acceptable":
                boost_stats["acceptable_quality"] += 1
            elif quality_level == "poor":
                boost_stats["poor_quality"] += 1
        else:
            boost_stats["unknown_quality"] += 1

        boosted_pattern = pattern.copy()
        boosted_pattern["pdt_quality_boost"] = boost_factor
        boosted_pattern["pdt_quality_level"] = quality_level
        boosted_pattern["original_priority"] = pattern.get("priority", 1.0)
        boosted_pattern["boosted_priority"] = (
            pattern.get("priority", 1.0) * boost_factor
        )

        boosted_patterns.append(boosted_pattern)
        total_boost += boost_factor

        boost_stats["max_boost_factor"] = max(
            boost_factor, boost_stats["max_boost_factor"]
        )

    if len(patterns) > 0:
        boost_stats["avg_boost_factor"] = total_boost / len(patterns)

    boosted_patterns.sort(key=lambda p: p.get("boosted_priority", 1.0), reverse=True)

    logger.info(
        "pdt_quality_boost_applied",
        total=boost_stats["total_patterns"],
        boosted=boost_stats["boosted_count"],
        excellent=boost_stats["excellent_quality"],
        good=boost_stats["good_quality"],
        avg_boost=f"{boost_stats['avg_boost_factor']:.2f}",
    )

    return boosted_patterns, boost_stats


def track_pdt_precision_correlation(
    patterns_before: list[dict[str, Any]],
    patterns_after: list[dict[str, Any]],
    pdt_quality_map: dict[str, PDTQualityMetrics],
    precision_stats: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Track correlation between PDT quality thresholds and precision improvement.

    Measures:
    1. Precision improvement for patterns from high vs low quality sections
    2. Correlation coefficient between I_struct and pattern accuracy
    3. Threshold effectiveness (I_struct>0.8 vs others)

    Args:
        patterns_before: Patterns before quality boost
        patterns_after: Patterns after quality boost and filtering
        pdt_quality_map: Map of section quality metrics
        precision_stats: Optional precision statistics from filtering

    Returns:
        Dictionary with correlation metrics and insights
    """
    correlation_metrics = {
        "total_patterns_before": len(patterns_before),
        "total_patterns_after": len(patterns_after),
        "patterns_from_high_quality": 0,
        "patterns_from_low_quality": 0,
        "high_quality_retention_rate": 0.0,
        "low_quality_retention_rate": 0.0,
        "quality_correlation": 0.0,
        "I_struct_threshold_effectiveness": {},
        "precision_by_quality_level": {},
    }

    if not pdt_quality_map:
        return correlation_metrics

    quality_levels = {
        "excellent": [],
        "good": [],
        "acceptable": [],
        "poor": [],
        "unknown": [],
    }

    after_ids = {p.get("id") for p in patterns_after if p.get("id")}

    for pattern in patterns_before:
        pattern_section = pattern.get("pdt_section") or pattern.get("source_section")
        quality_level = "unknown"
        I_struct = 0.0

        if pattern_section and pattern_section in pdt_quality_map:
            metrics = pdt_quality_map[pattern_section]
            quality_level = metrics.quality_level
            I_struct = metrics.I_struct

        retained = pattern.get("id") in after_ids if pattern.get("id") else False

        quality_levels[quality_level].append(
            {"pattern": pattern, "I_struct": I_struct, "retained": retained}
        )

        if I_struct >= PDT_QUALITY_THRESHOLDS["I_struct_good"]:
            correlation_metrics["patterns_from_high_quality"] += 1
        else:
            correlation_metrics["patterns_from_low_quality"] += 1

    high_quality_retained = sum(
        1
        for qlist in [quality_levels["excellent"], quality_levels["good"]]
        for item in qlist
        if item["retained"]
    )
    high_quality_total = len(quality_levels["excellent"]) + len(quality_levels["good"])

    low_quality_retained = sum(
        1
        for qlist in [quality_levels["acceptable"], quality_levels["poor"]]
        for item in qlist
        if item["retained"]
    )
    low_quality_total = len(quality_levels["acceptable"]) + len(quality_levels["poor"])

    if high_quality_total > 0:
        correlation_metrics["high_quality_retention_rate"] = (
            high_quality_retained / high_quality_total
        )

    if low_quality_total > 0:
        correlation_metrics["low_quality_retention_rate"] = (
            low_quality_retained / low_quality_total
        )

    for level, items in quality_levels.items():
        if items:
            retained_count = sum(1 for item in items if item["retained"])
            retention_rate = retained_count / len(items)
            avg_I_struct = sum(item["I_struct"] for item in items) / len(items)

            correlation_metrics["precision_by_quality_level"][level] = {
                "total": len(items),
                "retained": retained_count,
                "retention_rate": retention_rate,
                "avg_I_struct": avg_I_struct,
            }

    if precision_stats:
        base_precision = precision_stats.get("baseline_precision", 0.4)
        final_precision = precision_stats.get("estimated_final_precision", 0.4)
        precision_gain = final_precision - base_precision

        correlation_metrics["precision_improvement"] = precision_gain
        correlation_metrics["pdt_quality_contribution"] = (
            precision_gain * correlation_metrics["high_quality_retention_rate"]
            if correlation_metrics["high_quality_retention_rate"] > 0
            else 0.0
        )

    threshold_metrics = {}
    for threshold_name, threshold_value in [
        ("I_struct>0.8", PDT_QUALITY_THRESHOLDS["I_struct_excellent"]),
        ("I_struct>0.6", PDT_QUALITY_THRESHOLDS["I_struct_good"]),
        ("I_struct>0.4", PDT_QUALITY_THRESHOLDS["I_struct_acceptable"]),
    ]:
        above_threshold = [
            item
            for qlist in quality_levels.values()
            for item in qlist
            if item["I_struct"] >= threshold_value
        ]
        below_threshold = [
            item
            for qlist in quality_levels.values()
            for item in qlist
            if item["I_struct"] < threshold_value
        ]

        above_retention = (
            sum(1 for item in above_threshold if item["retained"])
            / len(above_threshold)
            if above_threshold
            else 0.0
        )
        below_retention = (
            sum(1 for item in below_threshold if item["retained"])
            / len(below_threshold)
            if below_threshold
            else 0.0
        )

        threshold_metrics[threshold_name] = {
            "above_count": len(above_threshold),
            "below_count": len(below_threshold),
            "above_retention": above_retention,
            "below_retention": below_retention,
            "effectiveness": above_retention - below_retention,
        }

    correlation_metrics["I_struct_threshold_effectiveness"] = threshold_metrics

    if (
        correlation_metrics["high_quality_retention_rate"] > 0
        and correlation_metrics["low_quality_retention_rate"] > 0
    ):
        correlation_metrics["quality_correlation"] = (
            correlation_metrics["high_quality_retention_rate"]
            - correlation_metrics["low_quality_retention_rate"]
        )

    logger.info(
        "pdt_precision_correlation",
        high_quality_retention=f"{correlation_metrics['high_quality_retention_rate']:.2%}",
        low_quality_retention=f"{correlation_metrics['low_quality_retention_rate']:.2%}",
        quality_correlation=f"{correlation_metrics['quality_correlation']:.3f}",
    )

    return correlation_metrics


__all__ = [
    "PDTQualityMetrics",
    "PDTSectionQuality",
    "compute_pdt_section_quality",
    "apply_pdt_quality_boost",
    "track_pdt_precision_correlation",
    "PDT_QUALITY_THRESHOLDS",
    "BOOST_FACTORS",
]
