"""
Aggregation Validation Module - Hard Validation for Phases 4-7

This module provides strict validation to ensure the aggregation pipeline
produces non-trivial, traceable results. It prevents silent failures and
enforces score range constraints and traceability invariants.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_04.primitives.phase4_00_00_types import (
        DimensionScore,
    )
    from farfan_pipeline.phases.Phase_04.phase4_30_00_aggregation import (
        ScoredResult,
    )
    from farfan_pipeline.phases.Phase_05.phase5_00_00_area_score import AreaScore
    from farfan_pipeline.phases.Phase_06.phase6_10_00_cluster_score import ClusterScore
    from farfan_pipeline.phases.Phase_07.phase7_10_00_macro_score import MacroScore


@dataclass
class ValidationResult:
    """Result of aggregation validation."""

    passed: bool
    phase: str
    error_message: str = ""
    details: dict[str, Any] | None = None


class AggregationValidationError(Exception):
    """Raised when aggregation validation fails."""


def validate_phase4_output(
    dimension_scores: list[DimensionScore],
    input_scored_results: list[ScoredResult],
) -> ValidationResult:
    """
    Validate Phase 4 (Dimension Aggregation) output.

    Requirements:
    - Must produce non-empty dimension scores
    - Each dimension score must trace to source micro-questions
    - Score values must be within the valid range [0, 3]
    """
    if not dimension_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 4 (Dimension Aggregation)",
            error_message=(
                "Dimension aggregation returned an empty list. "
                "No dimensions were aggregated."
            ),
            details={"input_count": len(input_scored_results), "output_count": 0},
        )

    non_traceable: list[str] = []
    invalid_scores: list[tuple[str, float]] = []

    for dim_score in dimension_scores:
        if not dim_score.contributing_questions:
            non_traceable.append(f"{dim_score.dimension_id}/{dim_score.area_id}")

        if dim_score.score < 0 or dim_score.score > 3:
            invalid_scores.append(
                (f"{dim_score.dimension_id}/{dim_score.area_id}", dim_score.score)
            )

    if non_traceable:
        return ValidationResult(
            passed=False,
            phase="Phase 4 (Dimension Aggregation)",
            error_message=(
                "Dimension scores not traceable to source micro-questions: "
                f"{non_traceable[:5]}"
            ),
            details={"non_traceable_count": len(non_traceable), "examples": non_traceable[:5]},
        )

    if invalid_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 4 (Dimension Aggregation)",
            error_message=(
                "Invalid dimension scores (outside [0, 3] range): "
                f"{invalid_scores[:5]}"
            ),
            details={"invalid_count": len(invalid_scores), "examples": invalid_scores[:5]},
        )

    return ValidationResult(
        passed=True,
        phase="Phase 4 (Dimension Aggregation)",
        details={
            "dimension_count": len(dimension_scores),
            "input_count": len(input_scored_results),
            "traceable": True,
        },
    )


def validate_phase5_output(
    area_scores: list[AreaScore],
    input_dimension_scores: list[DimensionScore],
) -> ValidationResult:
    """
    Validate Phase 5 (Area Policy Aggregation) output.
    """
    if not area_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 5 (Area Policy Aggregation)",
            error_message=(
                "Area aggregation returned an empty list. "
                "No policy areas were aggregated."
            ),
            details={"input_count": len(input_dimension_scores), "output_count": 0},
        )

    non_traceable: list[str] = []
    invalid_scores: list[tuple[str, float]] = []

    for area_score in area_scores:
        if not area_score.dimension_scores:
            non_traceable.append(area_score.area_id)

        if area_score.score < 0 or area_score.score > 3:
            invalid_scores.append((area_score.area_id, area_score.score))

    if non_traceable:
        return ValidationResult(
            passed=False,
            phase="Phase 5 (Area Policy Aggregation)",
            error_message=(
                "Area scores not traceable to dimension scores: "
                f"{non_traceable[:5]}"
            ),
            details={"non_traceable_count": len(non_traceable), "examples": non_traceable[:5]},
        )

    if invalid_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 5 (Area Policy Aggregation)",
            error_message=(
                "Invalid area scores (outside [0, 3] range): "
                f"{invalid_scores[:5]}"
            ),
            details={"invalid_count": len(invalid_scores), "examples": invalid_scores[:5]},
        )

    return ValidationResult(
        passed=True,
        phase="Phase 5 (Area Policy Aggregation)",
        details={
            "area_count": len(area_scores),
            "input_count": len(input_dimension_scores),
            "traceable": True,
        },
    )


def validate_phase6_output(
    cluster_scores: list[ClusterScore],
    input_area_scores: list[AreaScore],
) -> ValidationResult:
    """
    Validate Phase 6 (Cluster Aggregation) output.
    """
    if not cluster_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 6 (Cluster Aggregation)",
            error_message=(
                "Cluster aggregation returned an empty list. "
                "No clusters were aggregated."
            ),
            details={"input_count": len(input_area_scores), "output_count": 0},
        )

    non_traceable: list[str] = []
    invalid_scores: list[tuple[str, float]] = []

    for cluster_score in cluster_scores:
        if not cluster_score.area_scores:
            non_traceable.append(cluster_score.cluster_id)

        if cluster_score.score < 0 or cluster_score.score > 3:
            invalid_scores.append((cluster_score.cluster_id, cluster_score.score))

    if non_traceable:
        return ValidationResult(
            passed=False,
            phase="Phase 6 (Cluster Aggregation)",
            error_message=(
                "Cluster scores not traceable to area scores: "
                f"{non_traceable[:5]}"
            ),
            details={"non_traceable_count": len(non_traceable), "examples": non_traceable[:5]},
        )

    if invalid_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 6 (Cluster Aggregation)",
            error_message=(
                "Invalid cluster scores (outside [0, 3] range): "
                f"{invalid_scores[:5]}"
            ),
            details={"invalid_count": len(invalid_scores), "examples": invalid_scores[:5]},
        )

    return ValidationResult(
        passed=True,
        phase="Phase 6 (Cluster Aggregation)",
        details={
            "cluster_count": len(cluster_scores),
            "input_count": len(input_area_scores),
            "traceable": True,
        },
    )


def validate_phase7_output(
    macro_score: MacroScore,
    input_cluster_scores: list[ClusterScore],
    input_area_scores: list[AreaScore],
    input_dimension_scores: list[DimensionScore],
) -> ValidationResult:
    """
    Validate Phase 7 (Macro Evaluation) output.
    """
    has_valid_inputs = (
        input_cluster_scores
        and input_area_scores
        and input_dimension_scores
        and any(cs.score > 0 for cs in input_cluster_scores)
    )

    if has_valid_inputs and macro_score.score == 0:
        return ValidationResult(
            passed=False,
            phase="Phase 7 (Macro Evaluation)",
            error_message=(
                "Macro score is zero despite valid non-zero inputs. "
                "This indicates a broken aggregation chain."
            ),
            details={
                "macro_score": macro_score.score,
                "cluster_count": len(input_cluster_scores),
                "area_count": len(input_area_scores),
                "dimension_count": len(input_dimension_scores),
                "non_zero_clusters": sum(1 for cs in input_cluster_scores if cs.score > 0),
            },
        )

    if not macro_score.cluster_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 7 (Macro Evaluation)",
            error_message=(
                "Macro score not traceable to cluster scores (empty cluster_scores list)."
            ),
            details={"macro_score": macro_score.score, "cluster_scores_count": 0},
        )

    if macro_score.score < 0 or macro_score.score > 3:
        return ValidationResult(
            passed=False,
            phase="Phase 7 (Macro Evaluation)",
            error_message=(
                "Invalid macro score (outside [0, 3] range): "
                f"{macro_score.score}"
            ),
            details={"macro_score": macro_score.score},
        )

    if not (0 <= macro_score.cross_cutting_coherence <= 1):
        return ValidationResult(
            passed=False,
            phase="Phase 7 (Macro Evaluation)",
            error_message=(
                "Invalid cross-cutting coherence (outside [0, 1] range): "
                f"{macro_score.cross_cutting_coherence}"
            ),
            details={"coherence": macro_score.cross_cutting_coherence},
        )

    if not (0 <= macro_score.strategic_alignment <= 1):
        return ValidationResult(
            passed=False,
            phase="Phase 7 (Macro Evaluation)",
            error_message=(
                "Invalid strategic alignment (outside [0, 1] range): "
                f"{macro_score.strategic_alignment}"
            ),
            details={"alignment": macro_score.strategic_alignment},
        )

    return ValidationResult(
        passed=True,
        phase="Phase 7 (Macro Evaluation)",
        details={
            "macro_score": macro_score.score,
            "quality_level": macro_score.quality_level,
            "coherence": macro_score.cross_cutting_coherence,
            "alignment": macro_score.strategic_alignment,
            "systemic_gaps_count": len(macro_score.systemic_gaps),
            "traceable": True,
        },
    )


def validate_full_aggregation_pipeline(
    dimension_scores: list[DimensionScore],
    area_scores: list[AreaScore],
    cluster_scores: list[ClusterScore],
    macro_score: MacroScore,
    input_scored_results: list[ScoredResult],
) -> tuple[bool, list[ValidationResult]]:
    """
    Validate the entire aggregation pipeline (Phases 4-7).
    """
    validation_results: list[ValidationResult] = []

    validation_results.append(validate_phase4_output(dimension_scores, input_scored_results))
    validation_results.append(validate_phase5_output(area_scores, dimension_scores))
    validation_results.append(validate_phase6_output(cluster_scores, area_scores))
    validation_results.append(
        validate_phase7_output(macro_score, cluster_scores, area_scores, dimension_scores)
    )

    all_passed = all(result.passed for result in validation_results)
    return all_passed, validation_results


def enforce_validation_or_fail(
    validation_results: list[ValidationResult],
    allow_failure: bool = False,
) -> None:
    """
    Enforce validation results or raise exception.
    """
    failed_results = [r for r in validation_results if not r.passed]

    if failed_results and not allow_failure:
        error_messages = []
        for result in failed_results:
            error_messages.append(
                f"{result.phase}: {result.error_message}\n  Details: {result.details}"
            )

        full_error = (
            f"Aggregation validation failed at {len(failed_results)} phase(s):\n\n"
            + "\n\n".join(error_messages)
        )

        raise AggregationValidationError(full_error)
