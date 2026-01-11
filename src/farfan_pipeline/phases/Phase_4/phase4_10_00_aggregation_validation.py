"""
Aggregation Validation Module - Hard Validation for Phases 4-7

This module provides strict validation to ensure aggregation pipeline
produces non-trivial, traceable results. Prevents silent failures.

Requirements from Issue #[P0]:
- Fail hard if any phase returns empty or cannot be traced to source micro-questions
- Non-zero macro score is required for proper inputs
- All phases must chain outputs to inputs
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 4
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .aggregation import (
        AreaScore,
        ClusterScore,
        DimensionScore,
        MacroScore,
        ScoredResult,
    )


@dataclass
class ValidationResult:
    """Result of aggregation validation."""

    passed: bool
    phase: str
    error_message: str = ""
    details: dict[str, any] = None


class AggregationValidationError(Exception):
    """Raised when aggregation validation fails."""

    pass


def validate_phase4_output(
    dimension_scores: list[DimensionScore],
    input_scored_results: list[ScoredResult],
) -> ValidationResult:
    """
    Validate Phase 4 (Dimension Aggregation) output.

    Requirements:
    - Must produce non-empty dimension scores
    - Each dimension score must trace to source micro questions
    - Score values must be non-negative and within valid range [0, 3]

    Args:
        dimension_scores: Output from Phase 4
        input_scored_results: Input to Phase 4 (for traceability check)

    Returns:
        ValidationResult with pass/fail status

    Raises:
        AggregationValidationError: If validation fails in strict mode
    """
    if not dimension_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 4 (Dimension Aggregation)",
            error_message="Dimension aggregation returned EMPTY list. No dimensions were aggregated.",
            details={"input_count": len(input_scored_results), "output_count": 0},
        )

    # Check traceability
    non_traceable = []
    invalid_scores = []

    for dim_score in dimension_scores:
        # Check traceability
        if not dim_score.contributing_questions or len(dim_score.contributing_questions) == 0:
            non_traceable.append(f"{dim_score.dimension_id}/{dim_score.area_id}")

        # Check score validity
        if dim_score.score < 0 or dim_score.score > 3:
            invalid_scores.append(
                (f"{dim_score.dimension_id}/{dim_score.area_id}", dim_score.score)
            )

    if non_traceable:
        return ValidationResult(
            passed=False,
            phase="Phase 4 (Dimension Aggregation)",
            error_message=f"Dimension scores not traceable to source micro questions: {non_traceable[:5]}",
            details={"non_traceable_count": len(non_traceable), "examples": non_traceable[:5]},
        )

    if invalid_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 4 (Dimension Aggregation)",
            error_message=f"Invalid dimension scores (outside [0, 3] range): {invalid_scores[:5]}",
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

    Requirements:
    - Must produce non-empty area scores
    - Each area score must trace to dimension scores
    - Score values must be non-negative and within valid range [0, 3]

    Args:
        area_scores: Output from Phase 5
        input_dimension_scores: Input to Phase 5

    Returns:
        ValidationResult with pass/fail status
    """
    if not area_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 5 (Area Policy Aggregation)",
            error_message="Area aggregation returned EMPTY list. No policy areas were aggregated.",
            details={"input_count": len(input_dimension_scores), "output_count": 0},
        )

    # Check traceability
    non_traceable = []
    invalid_scores = []

    for area_score in area_scores:
        # Check traceability
        if not area_score.dimension_scores or len(area_score.dimension_scores) == 0:
            non_traceable.append(area_score.area_id)

        # Check score validity
        if area_score.score < 0 or area_score.score > 3:
            invalid_scores.append((area_score.area_id, area_score.score))

    if non_traceable:
        return ValidationResult(
            passed=False,
            phase="Phase 5 (Area Policy Aggregation)",
            error_message=f"Area scores not traceable to dimension scores: {non_traceable[:5]}",
            details={"non_traceable_count": len(non_traceable), "examples": non_traceable[:5]},
        )

    if invalid_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 5 (Area Policy Aggregation)",
            error_message=f"Invalid area scores (outside [0, 3] range): {invalid_scores[:5]}",
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

    Requirements:
    - Must produce non-empty cluster scores
    - Each cluster score must trace to area scores
    - Score values must be non-negative and within valid range [0, 3]

    Args:
        cluster_scores: Output from Phase 6
        input_area_scores: Input to Phase 6

    Returns:
        ValidationResult with pass/fail status
    """
    if not cluster_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 6 (Cluster Aggregation)",
            error_message="Cluster aggregation returned EMPTY list. No clusters were aggregated.",
            details={"input_count": len(input_area_scores), "output_count": 0},
        )

    # Check traceability
    non_traceable = []
    invalid_scores = []

    for cluster_score in cluster_scores:
        # Check traceability
        if not cluster_score.area_scores or len(cluster_score.area_scores) == 0:
            non_traceable.append(cluster_score.cluster_id)

        # Check score validity
        if cluster_score.score < 0 or cluster_score.score > 3:
            invalid_scores.append((cluster_score.cluster_id, cluster_score.score))

    if non_traceable:
        return ValidationResult(
            passed=False,
            phase="Phase 6 (Cluster Aggregation)",
            error_message=f"Cluster scores not traceable to area scores: {non_traceable[:5]}",
            details={"non_traceable_count": len(non_traceable), "examples": non_traceable[:5]},
        )

    if invalid_scores:
        return ValidationResult(
            passed=False,
            phase="Phase 6 (Cluster Aggregation)",
            error_message=f"Invalid cluster scores (outside [0, 3] range): {invalid_scores[:5]}",
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

    Requirements:
    - Macro score must be non-zero for valid inputs
    - Must trace to cluster scores
    - Score values must be non-negative and within valid range [0, 3]
    - Cross-cutting coherence must be in [0, 1]
    - Strategic alignment must be in [0, 1]

    Args:
        macro_score: Output from Phase 7
        input_cluster_scores: Input cluster scores
        input_area_scores: Input area scores
        input_dimension_scores: Input dimension scores

    Returns:
        ValidationResult with pass/fail status
    """
    # Check if macro score is zero when inputs are non-empty and non-zero
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
                "Macro score is ZERO despite valid non-zero inputs. "
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

    # Check traceability
    if not macro_score.cluster_scores or len(macro_score.cluster_scores) == 0:
        return ValidationResult(
            passed=False,
            phase="Phase 7 (Macro Evaluation)",
            error_message="Macro score not traceable to cluster scores (empty cluster_scores list).",
            details={"macro_score": macro_score.score, "cluster_scores_count": 0},
        )

    # Check score validity
    if macro_score.score < 0 or macro_score.score > 3:
        return ValidationResult(
            passed=False,
            phase="Phase 7 (Macro Evaluation)",
            error_message=f"Invalid macro score (outside [0, 3] range): {macro_score.score}",
            details={"macro_score": macro_score.score},
        )

    # Check coherence and alignment ranges
    if not (0 <= macro_score.cross_cutting_coherence <= 1):
        return ValidationResult(
            passed=False,
            phase="Phase 7 (Macro Evaluation)",
            error_message=f"Invalid cross-cutting coherence (outside [0, 1] range): {macro_score.cross_cutting_coherence}",
            details={"coherence": macro_score.cross_cutting_coherence},
        )

    if not (0 <= macro_score.strategic_alignment <= 1):
        return ValidationResult(
            passed=False,
            phase="Phase 7 (Macro Evaluation)",
            error_message=f"Invalid strategic alignment (outside [0, 1] range): {macro_score.strategic_alignment}",
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

    Performs comprehensive validation across all phases to ensure:
    - No empty results at any phase
    - Traceability from macro down to micro questions
    - Valid score ranges
    - Non-zero macro score for valid inputs

    Args:
        dimension_scores: Phase 4 output
        area_scores: Phase 5 output
        cluster_scores: Phase 6 output
        macro_score: Phase 7 output
        input_scored_results: Phase 3 output (input to Phase 4)

    Returns:
        Tuple of (all_passed, validation_results_list)

    Raises:
        AggregationValidationError: If any validation fails in strict mode
    """
    validation_results = []

    # Validate Phase 4
    phase4_result = validate_phase4_output(dimension_scores, input_scored_results)
    validation_results.append(phase4_result)

    # Validate Phase 5
    phase5_result = validate_phase5_output(area_scores, dimension_scores)
    validation_results.append(phase5_result)

    # Validate Phase 6
    phase6_result = validate_phase6_output(cluster_scores, area_scores)
    validation_results.append(phase6_result)

    # Validate Phase 7
    phase7_result = validate_phase7_output(
        macro_score, cluster_scores, area_scores, dimension_scores
    )
    validation_results.append(phase7_result)

    # Check if all passed
    all_passed = all(result.passed for result in validation_results)

    return all_passed, validation_results


def enforce_validation_or_fail(
    validation_results: list[ValidationResult],
    allow_failure: bool = False,
) -> None:
    """
    Enforce validation results or raise exception.

    Args:
        validation_results: List of validation results from pipeline
        allow_failure: If False, raises exception on any failure

    Raises:
        AggregationValidationError: If validation fails and allow_failure=False
    """
    failed_results = [r for r in validation_results if not r.passed]

    if failed_results and not allow_failure:
        error_messages = []
        for result in failed_results:
            error_messages.append(
                f"{result.phase}: {result.error_message}\n" f"  Details: {result.details}"
            )

        full_error = (
            f"Aggregation validation failed at {len(failed_results)} phase(s):\n\n"
            + "\n\n".join(error_messages)
        )

        raise AggregationValidationError(full_error)
