"""
Canonical Scoring Validators Module
====================================

Validation contracts and utilities aligned with Phase Three
(src/farfan_pipeline/phases/Phase_three/interface/).

This module provides validation for:
1. Entry contracts (MicroQuestionRun from Phase 2)
2. Exit contracts (ScoredMicroQuestion for Phase 4)
3. Scoring invariants (score ranges, quality levels)
4. Evidence structure validation

Validation Rules:
-----------------
[INV-SC-001] All scores must be in range [0.0, 1.0]
[INV-SC-002] Quality level must be deterministic from score
[INV-SC-003] Scoring metadata must include modality and threshold
[INV-SC-004] Normalized scores must be in range [0, 100]

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
Aligned with: Phase Three interface contracts v1.0.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Import quality levels and modalities
from ..modules.quality_levels import (
    VALID_QUALITY_LEVELS,
    determine_quality_level,
    is_valid_quality_level,
)
from ..modules.scoring_modalities import (
    ScoredResult,
    ScoringModality,
    get_all_modalities,
    is_valid_modality,
)

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


# =============================================================================
# VALIDATION ERRORS
# =============================================================================


class ScoringValidationError(Exception):
    """Base exception for scoring validation errors."""

    pass


class ScoreRangeError(ScoringValidationError):
    """Raised when score is outside valid range."""

    pass


class QualityLevelError(ScoringValidationError):
    """Raised when quality level is invalid."""

    pass


class EvidenceStructureError(ScoringValidationError):
    """Raised when evidence structure is invalid."""

    pass


class ModalityError(ScoringValidationError):
    """Raised when modality is invalid."""

    pass


class QuestionIdError(ScoringValidationError):
    """Raised when question_id format is invalid."""

    pass


# =============================================================================
# VALIDATION RESULT
# =============================================================================


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


# =============================================================================
# QUESTION ID VALIDATION
# =============================================================================


class QuestionIdValidator:
    """Validator for question_id format.

    Expected formats:
    - Simple: "Q001", "Q002", etc.
    - Full: "PA01-DIM01-Q001" (Policy-Dimension-Question)
    - Slot-based: "D1-Q1" (Dimension-Question)
    """

    # Regex patterns for question_id formats
    SIMPLE_PATTERN = re.compile(r"^Q\d{3}$")
    FULL_PATTERN = re.compile(r"^PA\d{2}-DIM\d{2}-Q\d{3}$")
    SLOT_PATTERN = re.compile(r"^D\d+-Q\d+$")

    @classmethod
    def validate(cls, question_id: str) -> ValidationResult:
        """Validate question_id format.

        Args:
            question_id: Question identifier string

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)

        if not isinstance(question_id, str):
            result.add_error(f"question_id must be string, got {type(question_id).__name__}")
            return result

        if not question_id:
            result.add_error("question_id cannot be empty")
            return result

        # Check if matches any valid pattern
        if (
            cls.SIMPLE_PATTERN.match(question_id)
            or cls.FULL_PATTERN.match(question_id)
            or cls.SLOT_PATTERN.match(question_id)
        ):
            return result

        result.add_error(
            f"question_id '{question_id}' does not match any valid format. "
            f"Expected: Q###, PA##-DIM##-Q###, or D#-Q#"
        )
        return result


# =============================================================================
# EVIDENCE VALIDATION
# =============================================================================


class EvidenceValidator:
    """Validator for evidence structure from Phase 2 EvidenceNexus.

    Aligned with Phase Three ScoringValidator.
    """

    REQUIRED_KEYS = {"elements", "confidence"}
    OPTIONAL_KEYS = {"by_type", "completeness", "graph_hash", "patterns"}

    @classmethod
    def validate(cls, evidence: dict[str, Any]) -> ValidationResult:
        """Validate evidence structure.

        Args:
            evidence: Evidence dict from Phase 2

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)

        # Check type
        if not isinstance(evidence, dict):
            result.add_error(f"Evidence must be dict, got {type(evidence).__name__}")
            return result

        # Check required keys
        missing = cls.REQUIRED_KEYS - evidence.keys()
        if missing:
            result.add_error(f"Missing required keys: {missing}")
            return result

        # Validate elements
        elements = evidence.get("elements")
        if not isinstance(elements, list):
            result.add_error(f"'elements' must be list, got {type(elements).__name__}")

        # Validate confidence
        confidence = evidence.get("confidence")
        if not isinstance(confidence, (int, float)):
            result.add_error(f"'confidence' must be numeric, got {type(confidence).__name__}")
        elif not 0.0 <= confidence <= 1.0:
            result.add_error(f"'confidence' must be in [0, 1], got {confidence}")

        # Validate optional keys if present
        completeness = evidence.get("completeness")
        if completeness is not None:
            valid_completeness = ["complete", "partial", "insufficient", "not_applicable"]
            if completeness not in valid_completeness:
                result.add_warning(
                    f"Unusual completeness value: {completeness}. "
                    f"Expected one of: {valid_completeness}"
                )

        return result


# =============================================================================
# SCORE VALIDATION
# =============================================================================


class ScoreValidator:
    """Validator for scored results.

    Enforces invariants:
    [INV-SC-001] All scores must be in range [0.0, 1.0]
    [INV-SC-004] Normalized scores must be in range [0, 100]
    """

    @classmethod
    def validate_score(cls, score: float, field_name: str = "score") -> ValidationResult:
        """Validate a single score value.

        Args:
            score: Score value to validate
            field_name: Name of the field for error messages

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)

        if not isinstance(score, (int, float)):
            result.add_error(f"{field_name} must be numeric, got {type(score).__name__}")
            return result

        if not 0.0 <= score <= 1.0:
            result.add_error(f"{field_name} must be in [0.0, 1.0], got {score}")

        return result

    @classmethod
    def validate_normalized_score(
        cls, normalized_score: float, field_name: str = "normalized_score"
    ) -> ValidationResult:
        """Validate normalized score value.

        Args:
            normalized_score: Normalized score value (0-100)
            field_name: Name of the field for error messages

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)

        if not isinstance(normalized_score, (int, float)):
            result.add_error(f"{field_name} must be numeric, got {type(normalized_score).__name__}")
            return result

        if not 0.0 <= normalized_score <= 100.0:
            result.add_error(f"{field_name} must be in [0, 100], got {normalized_score}")

        return result


# =============================================================================
# QUALITY LEVEL VALIDATION
# =============================================================================


class QualityLevelValidator:
    """Validator for quality levels.

    Enforces invariants:
    [INV-SC-002] Quality level must be deterministic from score
    """

    @classmethod
    def validate_quality_level(cls, quality_level: str) -> ValidationResult:
        """Validate quality level string.

        Args:
            quality_level: Quality level string

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)

        if not isinstance(quality_level, str):
            result.add_error(f"quality_level must be string, got {type(quality_level).__name__}")
            return result

        if not is_valid_quality_level(quality_level):
            result.add_error(
                f"Invalid quality_level: '{quality_level}'. "
                f"Expected one of: {VALID_QUALITY_LEVELS}"
            )

        return result

    @classmethod
    def validate_score_quality_consistency(
        cls, score: float, quality_level: str
    ) -> ValidationResult:
        """Validate that quality level matches score (invariant check).

        Args:
            score: Score value
            quality_level: Quality level string

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)

        # Calculate expected quality level
        expected = determine_quality_level(score)

        if quality_level != expected:
            result.add_warning(
                f"Quality level inconsistency: score {score:.3f} suggests "
                f"'{expected}', but got '{quality_level}'"
            )

        return result


# =============================================================================
# SCORED RESULT VALIDATION (Complete)
# =============================================================================


class ScoredResultValidator:
    """Complete validator for ScoredResult.

    Validates all invariants for a scored result.
    """

    @classmethod
    def validate(cls, result: ScoredResult) -> ValidationResult:
        """Validate a complete ScoredResult.

        Args:
            result: ScoredResult to validate

        Returns:
            ValidationResult with validation status
        """
        overall_result = ValidationResult(is_valid=True)

        # Validate score [INV-SC-001]
        score_result = ScoreValidator.validate_score(result.score)
        overall_result.errors.extend(score_result.errors)
        overall_result.warnings.extend(score_result.warnings)
        if not score_result.is_valid:
            overall_result.is_valid = False

        # Validate normalized score [INV-SC-004]
        norm_result = ScoreValidator.validate_normalized_score(result.normalized_score)
        overall_result.errors.extend(norm_result.errors)
        overall_result.warnings.extend(norm_result.warnings)
        if not norm_result.is_valid:
            overall_result.is_valid = False

        # Validate quality level
        quality_result = QualityLevelValidator.validate_quality_level(result.quality_level)
        overall_result.errors.extend(quality_result.errors)
        overall_result.warnings.extend(quality_result.warnings)
        if not quality_result.is_valid:
            overall_result.is_valid = False

        # Validate score-quality consistency [INV-SC-002]
        consistency_result = QualityLevelValidator.validate_score_quality_consistency(
            result.score, result.quality_level
        )
        overall_result.warnings.extend(consistency_result.warnings)

        # Validate modality [INV-SC-003]
        if not is_valid_modality(result.modality):
            overall_result.add_error(
                f"Invalid modality: '{result.modality}'. "
                f"Expected one of: {get_all_modalities()}"
            )

        return overall_result


# =============================================================================
# METADATA VALIDATION
# =============================================================================


class MetadataValidator:
    """Validator for scoring metadata.

    Enforces invariants:
    [INV-SC-003] Scoring metadata must include modality and threshold
    """

    REQUIRED_KEYS = {"modality", "threshold"}
    OPTIONAL_KEYS = {
        "component_scores",
        "aggregation",
        "weights",
        "temporal_bonus",
        "coverage_bonus",
        "institutional_bonus",
    }

    @classmethod
    def validate(cls, metadata: dict[str, Any]) -> ValidationResult:
        """Validate scoring metadata.

        Args:
            metadata: Scoring metadata dict

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)

        if not isinstance(metadata, dict):
            result.add_error(f"metadata must be dict, got {type(metadata).__name__}")
            return result

        # Check required keys [INV-SC-003]
        missing = cls.REQUIRED_KEYS - metadata.keys()
        if missing:
            result.add_error(f"Missing required metadata keys: {missing}")

        # Validate modality if present
        modality = metadata.get("modality")
        if modality is not None and not is_valid_modality(modality):
            result.add_error(f"Invalid metadata modality: '{modality}'")

        # Validate threshold if present
        threshold = metadata.get("threshold")
        if threshold is not None:
            if not isinstance(threshold, (int, float)):
                result.add_error(
                    f"metadata.threshold must be numeric, got {type(threshold).__name__}"
                )
            elif not 0.0 <= threshold <= 1.0:
                result.add_error(f"metadata.threshold must be in [0, 1], got {threshold}")

        return result


# =============================================================================
# BATCH VALIDATION
# =============================================================================


def validate_batch(results: list[ScoredResult]) -> ValidationResult:
    """Validate a batch of scored results.

    Args:
        results: List of ScoredResult to validate

    Returns:
        Combined ValidationResult for the batch
    """
    overall_result = ValidationResult(is_valid=True)

    for i, result in enumerate(results):
        result_validation = ScoredResultValidator.validate(result)

        if not result_validation.is_valid:
            overall_result.is_valid = False

        # Add index to errors for traceability
        for error in result_validation.errors:
            overall_result.add_error(f"[{i}] {error}")

        for warning in result_validation.warnings:
            overall_result.add_warning(f"[{i}] {warning}")

    # Add summary
    if overall_result.errors:
        logger.warning(
            "batch_validation_failed",
            total=len(results),
            failed=len(overall_result.errors),
            errors=overall_result.errors[:5],  # First 5 errors
        )

    return overall_result


# =============================================================================
# PDET CONTEXT VALIDATION
# =============================================================================


class PDETContextValidator:
    """Validator for PDET enrichment context in scoring.

    Validates that PDET municipality context is properly structured
    and relevant to the scoring context.
    """

    REQUIRED_CONTEXT_KEYS = {"municipalities", "subregions", "policy_area_mappings"}
    OPTIONAL_CONTEXT_KEYS = {"relevant_pillars", "territorial_coverage", "enrichment_metadata"}

    @classmethod
    def validate_pdet_context(cls, pdet_context: dict[str, Any]) -> ValidationResult:
        """Validate PDET context structure.

        Args:
            pdet_context: PDET context dict from enrichment

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)

        if not isinstance(pdet_context, dict):
            result.add_error(f"pdet_context must be dict, got {type(pdet_context).__name__}")
            return result

        # Validate municipalities
        municipalities = pdet_context.get("municipalities", [])
        if not isinstance(municipalities, list):
            result.add_error(f"'municipalities' must be list, got {type(municipalities).__name__}")

        # Validate subregions
        subregions = pdet_context.get("subregions", [])
        if not isinstance(subregions, list):
            result.add_error(f"'subregions' must be list, got {type(subregions).__name__}")

        # Validate territorial coverage if present
        if "territorial_coverage" in pdet_context:
            coverage = pdet_context["territorial_coverage"]
            if not isinstance(coverage, (int, float)):
                result.add_error(
                    f"'territorial_coverage' must be numeric, got {type(coverage).__name__}"
                )
            elif not 0.0 <= coverage <= 1.0:
                result.add_error(f"'territorial_coverage' must be in [0, 1], got {coverage}")

        # Validate relevant pillars if present
        if "relevant_pillars" in pdet_context:
            pillars = pdet_context["relevant_pillars"]
            if not isinstance(pillars, list):
                result.add_error(f"'relevant_pillars' must be list, got {type(pillars).__name__}")

        return result

    @classmethod
    def validate_enriched_result(cls, enriched_result: dict[str, Any]) -> ValidationResult:
        """Validate enriched scored result with PDET context.

        Args:
            enriched_result: EnrichedScoredResult as dict

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)

        if not isinstance(enriched_result, dict):
            result.add_error(f"enriched_result must be dict, got {type(enriched_result).__name__}")
            return result

        # Check required fields
        required_fields = {"base_result", "pdet_context", "enrichment_applied"}
        missing = required_fields - enriched_result.keys()
        if missing:
            result.add_error(f"Missing required fields: {missing}")
            return result

        # Validate base result exists
        base_result = enriched_result.get("base_result")
        if base_result is None:
            result.add_error("'base_result' cannot be None")

        # Validate PDET context
        pdet_context = enriched_result.get("pdet_context")
        if pdet_context is not None:
            context_validation = cls.validate_pdet_context(pdet_context)
            result.errors.extend(context_validation.errors)
            result.warnings.extend(context_validation.warnings)
            if not context_validation.is_valid:
                result.is_valid = False

        # Validate gate validation status if enrichment applied
        if enriched_result.get("enrichment_applied", False):
            gate_status = enriched_result.get("gate_validation_status", {})
            if not isinstance(gate_status, dict):
                result.add_warning("'gate_validation_status' should be dict")
            else:
                # Check expected gates
                expected_gates = {
                    "gate_1_scope",
                    "gate_2_value_add",
                    "gate_3_capability",
                    "gate_4_channel",
                }
                missing_gates = expected_gates - gate_status.keys()
                if missing_gates:
                    result.add_warning(f"Missing gate validation for: {missing_gates}")

        # Validate territorial adjustment
        if "territorial_adjustment" in enriched_result:
            adjustment = enriched_result["territorial_adjustment"]
            if not isinstance(adjustment, (int, float)):
                result.add_error(
                    f"'territorial_adjustment' must be numeric, got {type(adjustment).__name__}"
                )
            elif (
                adjustment < 0.0 or adjustment > 0.16
            ):  # max_total_adjustment from scoring_system.json
                result.add_warning(
                    f"'territorial_adjustment' outside configured range [0, 0.16]: {adjustment}"
                )

        return result


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Exceptions
    "ScoringValidationError",
    "ScoreRangeError",
    "QualityLevelError",
    "EvidenceStructureError",
    "ModalityError",
    "QuestionIdError",
    # Result
    "ValidationResult",
    # Validators
    "QuestionIdValidator",
    "EvidenceValidator",
    "ScoreValidator",
    "QualityLevelValidator",
    "ScoredResultValidator",
    "MetadataValidator",
    "PDETContextValidator",
    # Batch
    "validate_batch",
]
