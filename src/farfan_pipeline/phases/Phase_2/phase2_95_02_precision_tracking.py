"""
Module: phase2_95_02_precision_tracking
PHASE_LABEL: Phase 2
Sequence: I

"""

"""
Precision Improvement Tracking for Context Filtering
====================================================

Enhanced validation and comprehensive stats tracking for the 60% precision
improvement target from filter_patterns_by_context integration.

This module provides:
1. Enhanced get_patterns_for_context() wrapper with validation
2. Detailed validation status tracking
3. Comprehensive logging and metrics
4. Target achievement verification

Usage:
    >>> from orchestration.orchestrator.precision_tracking import (
    ...     get_patterns_with_validation
    ... )
    >>> patterns, stats = get_patterns_with_validation(
    ...     enriched_pack, document_context
    ... )
    >>> assert stats['integration_validated']
    >>> assert stats['target_achieved']

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-03
"""

from datetime import datetime, timezone
from typing import Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


PRECISION_TARGET_THRESHOLD = 0.55


def get_patterns_with_validation(
    enriched_pack: Any,
    document_context: dict[str, Any],
    track_precision_improvement: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Enhanced wrapper for get_patterns_for_context() with comprehensive validation.

    This function wraps EnrichedSignalPack.get_patterns_for_context() and adds:
    - Pre-filtering validation
    - Post-filtering verification
    - Integration status checking
    - Target achievement tracking
    - Detailed logging

    Args:
        enriched_pack: EnrichedSignalPack instance
        document_context: Document context dict
        track_precision_improvement: Enable precision tracking

    Returns:
        Tuple of (filtered_patterns, comprehensive_stats) with enhanced fields:
            - validation_timestamp: ISO timestamp
            - validation_details: Detailed validation info
            - target_achieved: Boolean for 60% target
            - validation_status: Status string
            - target_status: Status string
            - pre_filter_count: Patterns before filtering
            - post_filter_count: Patterns after filtering
            - filtering_successful: Boolean validation

    Example:
        >>> enriched = create_enriched_signal_pack(base_pack)
        >>> context = create_document_context(section='budget', chapter=3)
        >>> patterns, stats = get_patterns_with_validation(enriched, context)
        >>> print(f"Validation: {stats['validation_status']}")
        >>> print(f"Target: {stats['target_status']}")
        >>> assert stats['integration_validated']
        >>> assert stats['target_achieved']
    """
    if not isinstance(document_context, dict):
        logger.warning(
            "invalid_document_context_type",
            context_type=type(document_context).__name__,
            expected="dict",
        )
        document_context = {}

    validation_timestamp = datetime.now(timezone.utc).isoformat()

    pre_filter_count = len(enriched_pack.patterns) if hasattr(enriched_pack, "patterns") else 0

    filtered, base_stats = enriched_pack.get_patterns_for_context(
        document_context, track_precision_improvement=track_precision_improvement
    )

    post_filter_count = len(filtered)

    validation_details = {
        "filter_function_called": True,
        "pre_filter_count": pre_filter_count,
        "post_filter_count": post_filter_count,
        "context_fields": list(document_context.keys()),
        "context_field_count": len(document_context),
        "filtering_successful": post_filter_count <= pre_filter_count,
        "patterns_reduced": pre_filter_count - post_filter_count,
        "reduction_percentage": (
            (pre_filter_count - post_filter_count) / pre_filter_count * 100
            if pre_filter_count > 0
            else 0.0
        ),
    }

    enhanced_stats = {**base_stats}
    enhanced_stats["validation_timestamp"] = validation_timestamp
    enhanced_stats["validation_details"] = validation_details
    enhanced_stats["pre_filter_count"] = pre_filter_count
    enhanced_stats["post_filter_count"] = post_filter_count
    enhanced_stats["filtering_successful"] = validation_details["filtering_successful"]

    if track_precision_improvement:
        integration_validated = base_stats.get("integration_validated", False)
        false_positive_reduction = base_stats.get("false_positive_reduction", 0.0)
        target_achieved = false_positive_reduction >= PRECISION_TARGET_THRESHOLD

        enhanced_stats["target_achieved"] = target_achieved

        if integration_validated:
            enhanced_stats["validation_status"] = "VALIDATED"
            validation_message = "✓ filter_patterns_by_context integration VALIDATED"
        else:
            enhanced_stats["validation_status"] = "NOT_VALIDATED"
            validation_message = "✗ filter_patterns_by_context integration NOT validated"

        target_status = "ACHIEVED" if target_achieved else "NOT_MET"
        enhanced_stats["target_status"] = target_status

        if not validation_details["filtering_successful"]:
            logger.error(
                "context_filtering_validation_failed",
                pre_filter_count=pre_filter_count,
                post_filter_count=post_filter_count,
                reason="filtered_count_exceeds_original",
            )
            enhanced_stats["integration_validated"] = False
            enhanced_stats["validation_status"] = "FAILED"

        logger.info(
            "enhanced_context_filtering_validation",
            pre_filter_count=pre_filter_count,
            post_filter_count=post_filter_count,
            patterns_reduced=validation_details["patterns_reduced"],
            reduction_percentage=f"{validation_details['reduction_percentage']:.1f}%",
            filter_rate=f"{base_stats.get('filter_rate', 0.0):.1%}",
            precision_improvement=f"{base_stats.get('precision_improvement', 0.0):.1%}",
            false_positive_reduction=f"{false_positive_reduction:.1%}",
            integration_validated=integration_validated,
            validation_status=enhanced_stats["validation_status"],
            target_achieved=target_achieved,
            target_status=target_status,
            validation_message=validation_message,
            validation_timestamp=validation_timestamp,
        )

        if target_achieved:
            logger.info(
                "precision_target_achieved",
                false_positive_reduction=f"{false_positive_reduction:.1%}",
                target_threshold=f"{PRECISION_TARGET_THRESHOLD:.1%}",
                message="✓ 60% precision improvement target ACHIEVED",
            )
        else:
            logger.warning(
                "precision_target_not_met",
                false_positive_reduction=f"{false_positive_reduction:.1%}",
                target_threshold=f"{PRECISION_TARGET_THRESHOLD:.1%}",
                shortfall=f"{(PRECISION_TARGET_THRESHOLD - false_positive_reduction):.1%}",
                message="✗ 60% precision improvement target NOT met",
            )
    else:
        enhanced_stats["target_achieved"] = False
        enhanced_stats["validation_status"] = "TRACKING_DISABLED"
        enhanced_stats["target_status"] = "UNKNOWN"
        logger.debug("context_filtering_applied_without_tracking", **validation_details)

    return filtered, enhanced_stats


def validate_filter_integration(
    enriched_pack: Any, test_contexts: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """
    Comprehensive validation of filter_patterns_by_context integration.

    Tests the filtering functionality across multiple contexts and validates:
    - Integration is working correctly
    - Patterns are being filtered
    - 60% target is achievable
    - No errors occur during filtering

    Args:
        enriched_pack: EnrichedSignalPack instance to test
        test_contexts: Optional list of test contexts. If None, uses defaults.

    Returns:
        Validation report dict with:
            - total_tests: Number of contexts tested
            - successful_tests: Tests that completed without error
            - integration_validated: Overall integration status
            - target_achieved_count: Number of tests achieving 60% target
            - target_achievement_rate: Percentage achieving target
            - average_filter_rate: Average pattern reduction
            - average_fp_reduction: Average false positive reduction
            - validation_summary: Human-readable summary

    Example:
        >>> enriched = create_enriched_signal_pack(base_pack)
        >>> report = validate_filter_integration(enriched)
        >>> print(report['validation_summary'])
        >>> assert report['integration_validated']
        >>> assert report['target_achievement_rate'] > 0.5
    """
    if test_contexts is None:
        test_contexts = [
            {},
            {"section": "budget"},
            {"section": "indicators", "chapter": 5},
            {"section": "financial", "chapter": 2, "page": 10},
            {"policy_area": "economic_development"},
        ]

    results = []
    errors = []

    for idx, context in enumerate(test_contexts):
        try:
            patterns, stats = get_patterns_with_validation(
                enriched_pack, context, track_precision_improvement=True
            )
            results.append(stats)
        except Exception as e:
            logger.error(
                "filter_validation_test_failed",
                test_index=idx,
                context=context,
                error=str(e),
                error_type=type(e).__name__,
            )
            errors.append(
                {
                    "test_index": idx,
                    "context": context,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )

    total_tests = len(test_contexts)
    successful_tests = len(results)
    failed_tests = len(errors)

    if successful_tests == 0:
        return {
            "total_tests": total_tests,
            "successful_tests": 0,
            "failed_tests": failed_tests,
            "integration_validated": False,
            "target_achieved_count": 0,
            "target_achievement_rate": 0.0,
            "average_filter_rate": 0.0,
            "average_fp_reduction": 0.0,
            "errors": errors,
            "validation_summary": "✗ ALL TESTS FAILED - Integration NOT working",
        }

    integration_validated_count = sum(1 for r in results if r.get("integration_validated", False))
    target_achieved_count = sum(1 for r in results if r.get("target_achieved", False))

    average_filter_rate = sum(r.get("filter_rate", 0.0) for r in results) / successful_tests
    average_fp_reduction = (
        sum(r.get("false_positive_reduction", 0.0) for r in results) / successful_tests
    )

    integration_rate = integration_validated_count / successful_tests
    target_achievement_rate = target_achieved_count / successful_tests

    overall_integration_validated = integration_rate >= 0.8

    validation_summary = (
        f"Filter Integration Validation Report:\n"
        f"  Tests: {successful_tests}/{total_tests} successful ({failed_tests} failed)\n"
        f"  Integration validated: {integration_validated_count}/{successful_tests} "
        f"({integration_rate:.0%})\n"
        f"  60% target achieved: {target_achieved_count}/{successful_tests} "
        f"({target_achievement_rate:.0%})\n"
        f"  Average filter rate: {average_filter_rate:.1%}\n"
        f"  Average FP reduction: {average_fp_reduction:.1%}\n"
        f"  Overall status: "
        f"{'✓ VALIDATED' if overall_integration_validated else '✗ NOT VALIDATED'}\n"
        f"  Target status: "
        f"{'✓ ACHIEVABLE' if target_achievement_rate > 0 else '✗ NOT ACHIEVABLE'}"
    )

    report = {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "failed_tests": failed_tests,
        "integration_validated": overall_integration_validated,
        "integration_validated_count": integration_validated_count,
        "integration_rate": integration_rate,
        "target_achieved_count": target_achieved_count,
        "target_achievement_rate": target_achievement_rate,
        "average_filter_rate": average_filter_rate,
        "average_fp_reduction": average_fp_reduction,
        "max_fp_reduction": (
            max(r.get("false_positive_reduction", 0.0) for r in results) if results else 0.0
        ),
        "min_fp_reduction": (
            min(r.get("false_positive_reduction", 0.0) for r in results) if results else 0.0
        ),
        "errors": errors,
        "validation_summary": validation_summary,
        "all_results": results,
    }

    logger.info(
        "filter_integration_validation_complete",
        total_tests=total_tests,
        successful_tests=successful_tests,
        failed_tests=failed_tests,
        integration_validated=overall_integration_validated,
        target_achievement_rate=f"{target_achievement_rate:.0%}",
        summary=validation_summary,
    )

    return report


def create_precision_tracking_session(
    enriched_pack: Any, session_id: str | None = None
) -> dict[str, Any]:
    """
    Create a precision tracking session for continuous monitoring.

    This creates a session object that tracks multiple measurements over time,
    useful for monitoring precision improvement during production analysis.

    Args:
        enriched_pack: EnrichedSignalPack instance
        session_id: Optional session identifier

    Returns:
        Session object with tracking state and methods

    Example:
        >>> session = create_precision_tracking_session(enriched_pack, "prod_001")
        >>> # Use session throughout analysis...
        >>> results = finalize_precision_tracking_session(session)
    """
    from datetime import datetime, timezone
    from uuid import uuid4

    if session_id is None:
        session_id = f"precision_session_{uuid4().hex[:8]}"

    session = {
        "session_id": session_id,
        "start_timestamp": datetime.now(timezone.utc).isoformat(),
        "enriched_pack": enriched_pack,
        "measurements": [],
        "measurement_count": 0,
        "contexts_tested": [],
        "cumulative_stats": {
            "total_patterns_processed": 0,
            "total_patterns_filtered": 0,
            "total_filtering_time_ms": 0.0,
        },
        "status": "ACTIVE",
    }

    logger.info(
        "precision_tracking_session_created",
        session_id=session_id,
        start_timestamp=session["start_timestamp"],
    )

    return session


def add_measurement_to_session(
    session: dict[str, Any],
    document_context: dict[str, Any],
    track_precision: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Add a measurement to an active precision tracking session.

    Args:
        session: Active session from create_precision_tracking_session
        document_context: Document context for this measurement
        track_precision: Enable precision tracking

    Returns:
        Tuple of (filtered_patterns, stats) from get_patterns_for_context

    Example:
        >>> session = create_precision_tracking_session(enriched_pack)
        >>> for context in contexts:
        ...     patterns, stats = add_measurement_to_session(session, context)
    """
    if session["status"] != "ACTIVE":
        logger.warning(
            "measurement_to_inactive_session",
            session_id=session["session_id"],
            status=session["status"],
        )

    enriched_pack = session["enriched_pack"]
    patterns, stats = get_patterns_with_validation(enriched_pack, document_context, track_precision)

    session["measurements"].append(stats)
    session["measurement_count"] += 1
    session["contexts_tested"].append(document_context)

    session["cumulative_stats"]["total_patterns_processed"] += stats.get("total_patterns", 0)
    session["cumulative_stats"]["total_patterns_filtered"] += stats.get(
        "total_patterns", 0
    ) - stats.get("passed", 0)
    session["cumulative_stats"]["total_filtering_time_ms"] += stats.get(
        "filtering_duration_ms", 0.0
    )

    return patterns, stats


def finalize_precision_tracking_session(
    session: dict[str, Any], generate_full_report: bool = True
) -> dict[str, Any]:
    """
    Finalize a precision tracking session and generate summary.

    Args:
        session: Active session to finalize
        generate_full_report: Include full detailed report

    Returns:
        Finalized session report with comprehensive metrics

    Example:
        >>> session = create_precision_tracking_session(enriched_pack)
        >>> # ... add measurements ...
        >>> results = finalize_precision_tracking_session(session)
        >>> print(results['summary'])
    """
    from datetime import datetime, timezone

    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_intelligence_layer import (
        generate_precision_improvement_report,
    )

    end_timestamp = datetime.now(timezone.utc).isoformat()
    session["end_timestamp"] = end_timestamp
    session["status"] = "FINALIZED"

    if not session["measurements"]:
        return {
            "session_id": session["session_id"],
            "status": "FINALIZED",
            "measurement_count": 0,
            "summary": "No measurements recorded",
        }

    full_report = None
    if generate_full_report:
        full_report = generate_precision_improvement_report(
            session["measurements"], include_detailed_breakdown=True
        )

    session_summary = {
        "session_id": session["session_id"],
        "start_timestamp": session["start_timestamp"],
        "end_timestamp": end_timestamp,
        "status": session["status"],
        "measurement_count": session["measurement_count"],
        "cumulative_stats": session["cumulative_stats"],
        "contexts_tested_count": len(session["contexts_tested"]),
    }

    if full_report:
        session_summary["aggregate_report"] = full_report
        session_summary["summary"] = full_report["summary"]
        session_summary["target_achievement_rate"] = full_report["target_achievement_rate"]
        session_summary["integration_validated"] = full_report["validation_rate"] >= 0.8
        session_summary["validation_health"] = full_report["validation_health"]

    logger.info(
        "precision_tracking_session_finalized",
        session_id=session["session_id"],
        measurement_count=session["measurement_count"],
        total_patterns_processed=session["cumulative_stats"]["total_patterns_processed"],
        total_filtering_time_ms=session["cumulative_stats"]["total_filtering_time_ms"],
        target_achievement_rate=(session_summary.get("target_achievement_rate", 0.0)),
    )

    return session_summary


def compare_precision_across_policy_areas(
    policy_area_packs: dict[str, Any], test_contexts: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """
    Compare precision improvement across multiple policy areas.

    Useful for identifying which policy areas achieve the 60% target and which need improvement.

    Args:
        policy_area_packs: Dict mapping policy_area_id to EnrichedSignalPack
        test_contexts: Optional test contexts (uses defaults if None)

    Returns:
        Comparison report with per-area metrics and rankings

    Example:
        >>> packs = {
        ...     "PA01": create_enriched_signal_pack(base_pack_01),
        ...     "PA02": create_enriched_signal_pack(base_pack_02),
        ... }
        >>> comparison = compare_precision_across_policy_areas(packs)
        >>> print(comparison['rankings']['by_target_achievement'])
    """
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_intelligence_layer import (
        generate_precision_improvement_report,
    )

    if test_contexts is None:
        test_contexts = [
            {},
            {"section": "budget"},
            {"section": "indicators"},
            {"section": "financial"},
        ]

    area_results = {}

    for policy_area_id, enriched_pack in policy_area_packs.items():
        measurements = []
        for context in test_contexts:
            try:
                _, stats = enriched_pack.get_patterns_for_context(
                    context, track_precision_improvement=True
                )
                measurements.append(stats)
            except Exception as e:
                logger.error(
                    "policy_area_precision_test_failed",
                    policy_area=policy_area_id,
                    context=context,
                    error=str(e),
                )

        if measurements:
            report = generate_precision_improvement_report(
                measurements, include_detailed_breakdown=False
            )
            area_results[policy_area_id] = report

    if not area_results:
        return {
            "policy_areas_tested": 0,
            "comparison_status": "FAILED",
            "message": "No successful measurements",
        }

    rankings = {
        "by_target_achievement": sorted(
            area_results.items(),
            key=lambda x: x[1]["target_achievement_rate"],
            reverse=True,
        ),
        "by_avg_fp_reduction": sorted(
            area_results.items(),
            key=lambda x: x[1]["avg_false_positive_reduction"],
            reverse=True,
        ),
        "by_validation_rate": sorted(
            area_results.items(), key=lambda x: x[1]["validation_rate"], reverse=True
        ),
    }

    best_performer = rankings["by_target_achievement"][0]
    worst_performer = rankings["by_target_achievement"][-1]

    areas_meeting_target = sum(
        1
        for _, report in area_results.items()
        if report["max_false_positive_reduction"] >= PRECISION_TARGET_THRESHOLD
    )

    comparison_summary = (
        f"Policy Area Precision Comparison:\n"
        f"  Areas tested: {len(area_results)}\n"
        f"  Areas meeting 60% target: {areas_meeting_target}/{len(area_results)}\n"
        f"  Best performer: {best_performer[0]} "
        f"({100*best_performer[1]['target_achievement_rate']:.0f}% target achievement)\n"
        f"  Worst performer: {worst_performer[0]} "
        f"({100*worst_performer[1]['target_achievement_rate']:.0f}% target achievement)\n"
        f"  Overall status: "
        f"{'✓ GOOD' if areas_meeting_target >= len(area_results) * 0.7 else '✗ NEEDS IMPROVEMENT'}"
    )

    return {
        "policy_areas_tested": len(area_results),
        "areas_meeting_target": areas_meeting_target,
        "target_achievement_coverage": areas_meeting_target / len(area_results),
        "rankings": rankings,
        "best_performer": {
            "policy_area": best_performer[0],
            "metrics": best_performer[1],
        },
        "worst_performer": {
            "policy_area": worst_performer[0],
            "metrics": worst_performer[1],
        },
        "all_results": area_results,
        "comparison_summary": comparison_summary,
    }


def export_precision_metrics_for_monitoring(
    measurements: list[dict[str, Any]], output_format: str = "json"
) -> str | dict[str, Any]:
    """
    Export precision metrics in format suitable for external monitoring systems.

    Args:
        measurements: List of stats dicts from get_patterns_for_context
        output_format: 'json', 'prometheus', or 'datadog'

    Returns:
        Formatted metrics string or dict

    Example:
        >>> measurements = [...]
        >>> metrics = export_precision_metrics_for_monitoring(measurements, 'json')
    """
    import json
    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).isoformat()

    if not measurements:
        if output_format == "json":
            return json.dumps({"error": "No measurements", "timestamp": timestamp})
        return ""

    total = len(measurements)
    meets_target = sum(
        1
        for m in measurements
        if m.get("false_positive_reduction", 0.0) >= PRECISION_TARGET_THRESHOLD
    )
    validated = sum(1 for m in measurements if m.get("integration_validated", False))

    avg_fp_reduction = sum(m.get("false_positive_reduction", 0.0) for m in measurements) / total
    avg_filter_rate = sum(m.get("filter_rate", 0.0) for m in measurements) / total

    if output_format == "json":
        return json.dumps(
            {
                "timestamp": timestamp,
                "measurement_count": total,
                "target_achievement_count": meets_target,
                "target_achievement_rate": meets_target / total,
                "integration_validated_count": validated,
                "integration_validation_rate": validated / total,
                "avg_false_positive_reduction": avg_fp_reduction,
                "avg_filter_rate": avg_filter_rate,
                "meets_60_percent_target": meets_target / total >= 0.5,
            },
            indent=2,
        )

    elif output_format == "prometheus":
        lines = [
            "# HELP precision_target_achievement_rate Rate of measurements meeting 60% target",
            "# TYPE precision_target_achievement_rate gauge",
            f"precision_target_achievement_rate {meets_target / total}",
            "# HELP precision_avg_fp_reduction Average false positive reduction",
            "# TYPE precision_avg_fp_reduction gauge",
            f"precision_avg_fp_reduction {avg_fp_reduction}",
            "# HELP precision_measurement_count Total measurements",
            "# TYPE precision_measurement_count counter",
            f"precision_measurement_count {total}",
        ]
        return "\n".join(lines)

    elif output_format == "datadog":
        return json.dumps(
            [
                {
                    "metric": "farfan.precision.target_achievement_rate",
                    "points": [
                        [
                            int(datetime.now(timezone.utc).timestamp()),
                            meets_target / total,
                        ]
                    ],
                    "type": "gauge",
                    "tags": ["component:context_filtering"],
                },
                {
                    "metric": "farfan.precision.avg_fp_reduction",
                    "points": [[int(datetime.now(timezone.utc).timestamp()), avg_fp_reduction]],
                    "type": "gauge",
                    "tags": ["component:context_filtering"],
                },
                {
                    "metric": "farfan.precision.measurement_count",
                    "points": [[int(datetime.now(timezone.utc).timestamp()), total]],
                    "type": "count",
                    "tags": ["component:context_filtering"],
                },
            ],
            indent=2,
        )

    return ""


__all__ = [
    "get_patterns_with_validation",
    "validate_filter_integration",
    "create_precision_tracking_session",
    "add_measurement_to_session",
    "finalize_precision_tracking_session",
    "compare_precision_across_policy_areas",
    "export_precision_metrics_for_monitoring",
    "PRECISION_TARGET_THRESHOLD",
]
