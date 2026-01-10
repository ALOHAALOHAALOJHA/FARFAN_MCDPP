"""Phase 3 Validation Module

Provides strict validation for Phase 3 scoring pipeline to prevent:
- Missing or incomplete micro-question results
- Out-of-bounds score values
- Invalid quality level enums
- Missing or null evidence
- Silent score corruption
"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 3
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"



from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "VALID_QUALITY_LEVELS",
    "ValidationCounters",
    "validate_and_clamp_score",
    "validate_evidence_presence",
    "validate_micro_results_input",
    "validate_quality_level",
]


VALID_QUALITY_LEVELS = frozenset({"EXCELENTE", "ACEPTABLE", "INSUFICIENTE", "NO_APLICABLE"})


@dataclass
class ValidationCounters:
    """Tracks validation failures during Phase 3 scoring."""

    total_questions: int = 0
    missing_evidence: int = 0
    out_of_bounds_scores: int = 0
    invalid_quality_levels: int = 0
    score_clamping_applied: int = 0
    quality_level_corrections: int = 0

    def log_summary(self) -> None:
        """Log validation summary."""
        logger.info(
            f"Phase 3 validation summary: total_questions={self.total_questions}, "
            f"missing_evidence={self.missing_evidence}, "
            f"out_of_bounds_scores={self.out_of_bounds_scores}, "
            f"invalid_quality_levels={self.invalid_quality_levels}, "
            f"score_clamping_applied={self.score_clamping_applied}, "
            f"quality_level_corrections={self.quality_level_corrections}"
        )

        if self.out_of_bounds_scores > 0:
            logger.warning(
                f"Phase 3: {self.out_of_bounds_scores} scores were out of bounds [0.0, 1.0]"
            )

        if self.invalid_quality_levels > 0:
            logger.warning(f"Phase 3: {self.invalid_quality_levels} quality levels were invalid")


def validate_micro_results_input(
    micro_results: list[Any],
    expected_count: int,
) -> None:
    """Validate micro-question results input before scoring.

    Args:
        micro_results: List of MicroQuestionRun objects from Phase 2
        expected_count: Expected number of questions (default: 305)

    Raises:
        ValueError: If input validation fails
    """
    if not micro_results:
        raise ValueError("Phase 3 input validation failed: micro_results list is empty")

    actual_count = len(micro_results)
    if actual_count != expected_count:
        logger.error(
            f"Phase 3 input validation failed: expected_count={expected_count}, "
            f"actual_count={actual_count}, difference={actual_count - expected_count}"
        )
        raise ValueError(
            f"Phase 3 input validation failed: Expected {expected_count} micro-question "
            f"results but got {actual_count}"
        )

    logger.info(f"Phase 3 input validation passed: question_count={actual_count}")


def validate_evidence_presence(
    evidence: Any,
    question_id: str,
    question_global: int,
    counters: ValidationCounters,
) -> bool:
    """Validate that evidence is present and not null.

    Args:
        evidence: Evidence object from MicroQuestionRun
        question_id: Question identifier
        question_global: Global question number
        counters: Validation counters to update

    Returns:
        True if evidence is valid, False otherwise
    """
    if evidence is None:
        counters.missing_evidence += 1
        logger.error(
            f"Phase 3 evidence validation failed: question_id={question_id}, "
            f"question_global={question_global}, reason=evidence is None"
        )
        return False

    return True


def validate_and_clamp_score(
    score: float | None,
    question_id: str,
    question_global: int,
    counters: ValidationCounters,
) -> float:
    """Validate score is in [0.0, 1.0] range and clamp if needed.

    Args:
        score: Raw score value
        question_id: Question identifier
        question_global: Global question number
        counters: Validation counters to update

    Returns:
        Clamped score in [0.0, 1.0] range
    """
    if score is None:
        logger.warning(
            f"Phase 3 score validation: score is None, defaulting to 0.0, "
            f"question_id={question_id}, question_global={question_global}"
        )
        return 0.0

    try:
        score_float = float(score)
    except (TypeError, ValueError) as e:
        counters.out_of_bounds_scores += 1
        logger.error(
            f"Phase 3 score validation failed: unconvertible type, "
            f"question_id={question_id}, question_global={question_global}, "
            f"score_type={type(score).__name__}, score_value={score!s}, error={e!s}"
        )
        return 0.0

    if score_float < 0.0 or score_float > 1.0:
        counters.out_of_bounds_scores += 1
        counters.score_clamping_applied += 1
        clamped = max(0.0, min(1.0, score_float))
        logger.warning(
            f"Phase 3 score clamping applied: question_id={question_id}, "
            f"question_global={question_global}, original_score={score_float}, "
            f"clamped_score={clamped}"
        )
        return clamped

    return score_float


def validate_quality_level(
    quality_level: str | None,
    question_id: str,
    question_global: int,
    counters: ValidationCounters,
) -> str:
    """Validate quality level is from valid enum set.

    Valid values: EXCELENTE, ACEPTABLE, INSUFICIENTE, NO_APLICABLE

    Args:
        quality_level: Quality level string
        question_id: Question identifier
        question_global: Global question number
        counters: Validation counters to update

    Returns:
        Validated quality level (corrected to INSUFICIENTE if invalid)
    """
    if quality_level is None:
        counters.invalid_quality_levels += 1
        counters.quality_level_corrections += 1
        logger.warning(
            f"Phase 3 quality level validation: None value, correcting to INSUFICIENTE, "
            f"question_id={question_id}, question_global={question_global}"
        )
        return "INSUFICIENTE"

    quality_str = str(quality_level).strip()

    if quality_str not in VALID_QUALITY_LEVELS:
        counters.invalid_quality_levels += 1
        counters.quality_level_corrections += 1
        logger.error(
            f"Phase 3 quality level validation failed: question_id={question_id}, "
            f"question_global={question_global}, invalid_value={quality_str}, "
            f"valid_values={list(VALID_QUALITY_LEVELS)}, corrected_to=INSUFICIENTE"
        )
        return "INSUFICIENTE"

    return quality_str
