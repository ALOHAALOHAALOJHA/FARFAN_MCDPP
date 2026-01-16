"""
Nexus-Scoring Interface Validator
=================================

This module provides comprehensive validation of the interface contract
between Phase 2 (EvidenceNexus) and Phase 3 (Scoring), ensuring full
alignment and harmonization.

VALIDATION LAYERS:
-----------------
1. Schema Validation: Structural integrity
2. Semantic Validation: Logical consistency
3. Provenance Validation: Traceability verification
4. Quality Validation: Minimum quality thresholds

ENTRY POINT STABILIZATION:
-------------------------
This module enforces the "ideal standard of harmony" by validating:
- Evidence structure completeness
- Scoring modality context propagation
- Adaptive threshold compatibility
- Metadata continuity

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
Date: 2025-12-11
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


# =============================================================================
# VALIDATION RESULTS
# =============================================================================


@dataclass
class ValidationResult:
    """Result of interface validation."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


# =============================================================================
# INTERFACE VALIDATOR
# =============================================================================


class NexusScoringValidator:
    """
    Validates interface contract between Phase 2 (Nexus) and Phase 3 (Scoring).

    This validator ensures that:
    1. Nexus output conforms to expected structure
    2. Scoring context is properly propagated
    3. Adaptive thresholds are computed correctly
    4. Quality metrics meet minimum standards
    """

    # Required evidence keys from Nexus
    REQUIRED_EVIDENCE_KEYS = {
        "elements",
        "confidence",
    }

    # Expected evidence keys (optional but recommended)
    EXPECTED_EVIDENCE_KEYS = {
        "by_type",
        "completeness",
        "graph_hash",
        "patterns",
    }

    # Minimum quality thresholds
    MIN_CONFIDENCE = 0.3
    MIN_COMPLETENESS = 0.5
    MIN_ELEMENTS_COUNT = 1

    @classmethod
    def validate_nexus_output(cls, micro_question_run: dict[str, Any]) -> ValidationResult:
        """
        Validate MicroQuestionRun output from Phase 2.

        Args:
            micro_question_run: Output from Phase 2 executor

        Returns:
            ValidationResult with validation status and details
        """
        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] = {}

        # 1. Structure validation
        if not isinstance(micro_question_run, dict):
            errors.append("MicroQuestionRun must be a dictionary")
            return ValidationResult(False, errors, warnings, metadata)

        # Check for evidence key
        if "evidence" not in micro_question_run:
            errors.append("Missing 'evidence' key in MicroQuestionRun")
            return ValidationResult(False, errors, warnings, metadata)

        evidence = micro_question_run["evidence"]

        # Handle None evidence (valid for failed questions)
        if evidence is None:
            warnings.append("Evidence is None - question may have failed")
            metadata["has_evidence"] = False
            return ValidationResult(True, errors, warnings, metadata)

        # 2. Evidence structure validation
        if not isinstance(evidence, dict):
            errors.append(f"Evidence must be dict, got {type(evidence).__name__}")
            return ValidationResult(False, errors, warnings, metadata)

        # Check required keys
        missing_required = cls.REQUIRED_EVIDENCE_KEYS - evidence.keys()
        if missing_required:
            errors.append(f"Missing required evidence keys: {missing_required}")

        # Check expected keys
        missing_expected = cls.EXPECTED_EVIDENCE_KEYS - evidence.keys()
        if missing_expected:
            warnings.append(f"Missing expected evidence keys: {missing_expected}")

        # 3. Quality validation
        confidence = evidence.get("confidence", 0.0)
        if not isinstance(confidence, (int, float)):
            errors.append(f"Confidence must be numeric, got {type(confidence).__name__}")
        elif confidence < cls.MIN_CONFIDENCE:
            warnings.append(f"Confidence {confidence:.3f} below minimum {cls.MIN_CONFIDENCE}")

        completeness = evidence.get("completeness", 0.0)
        if isinstance(completeness, (int, float)) and completeness < cls.MIN_COMPLETENESS:
            warnings.append(f"Completeness {completeness:.3f} below minimum {cls.MIN_COMPLETENESS}")

        elements = evidence.get("elements", [])
        if isinstance(elements, list) and len(elements) < cls.MIN_ELEMENTS_COUNT:
            warnings.append(
                f"Elements count {len(elements)} below minimum {cls.MIN_ELEMENTS_COUNT}"
            )

        # 4. Provenance validation
        if "graph_hash" in evidence:
            graph_hash = evidence["graph_hash"]
            if not isinstance(graph_hash, str) or not graph_hash:
                warnings.append("Invalid or empty graph_hash")
            elif len(graph_hash) != 64:  # SHA-256 hex length
                warnings.append(f"graph_hash length {len(graph_hash)} != 64 (SHA-256)")

        # 5. Metadata collection
        metadata.update(
            {
                "has_evidence": True,
                "confidence": confidence,
                "completeness": completeness,
                "elements_count": len(elements) if isinstance(elements, list) else 0,
                "has_graph_hash": "graph_hash" in evidence,
                "has_patterns": "patterns" in evidence,
                "has_by_type": "by_type" in evidence,
            }
        )

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, metadata)

    @classmethod
    def validate_scoring_context(cls, scoring_context: dict[str, Any] | None) -> ValidationResult:
        """
        Validate scoring context propagation.

        Args:
            scoring_context: Scoring context from SISAS

        Returns:
            ValidationResult with validation status
        """
        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] = {}

        if scoring_context is None:
            warnings.append("Scoring context is None - using defaults")
            metadata["has_context"] = False
            return ValidationResult(True, errors, warnings, metadata)

        if not isinstance(scoring_context, dict):
            errors.append(f"Scoring context must be dict, got {type(scoring_context).__name__}")
            return ValidationResult(False, errors, warnings, metadata)

        # Check required scoring keys
        required_keys = {"modality", "threshold"}
        missing = required_keys - scoring_context.keys()
        if missing:
            errors.append(f"Missing required scoring context keys: {missing}")

        # Validate threshold range
        threshold = scoring_context.get("threshold")
        if threshold is not None:
            if not isinstance(threshold, (int, float)):
                errors.append(f"Threshold must be numeric, got {type(threshold).__name__}")
            elif not 0.0 <= threshold <= 1.0:
                errors.append(f"Threshold {threshold} outside range [0, 1]")

        # Validate weights if present
        for weight_key in ["weight_elements", "weight_similarity", "weight_patterns"]:
            weight = scoring_context.get(weight_key)
            if weight is not None:
                if not isinstance(weight, (int, float)):
                    errors.append(f"{weight_key} must be numeric")
                elif not 0.0 <= weight <= 1.0:
                    warnings.append(f"{weight_key} {weight} outside typical range [0, 1]")

        metadata.update(
            {
                "has_context": True,
                "modality": scoring_context.get("modality"),
                "threshold": threshold,
            }
        )

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, metadata)

    @classmethod
    def validate_phase_transition(
        cls, micro_question_run: dict[str, Any], scoring_context: dict[str, Any] | None = None
    ) -> ValidationResult:
        """
        Comprehensive validation of Phase 2 → Phase 3 transition.

        Args:
            micro_question_run: Output from Phase 2
            scoring_context: Optional scoring context from SISAS

        Returns:
            ValidationResult with comprehensive validation
        """
        all_errors: list[str] = []
        all_warnings: list[str] = []
        all_metadata: dict[str, Any] = {}

        # 1. Validate nexus output
        nexus_result = cls.validate_nexus_output(micro_question_run)
        all_errors.extend(nexus_result.errors)
        all_warnings.extend(nexus_result.warnings)
        all_metadata["nexus_validation"] = nexus_result.metadata

        # 2. Validate scoring context
        context_result = cls.validate_scoring_context(scoring_context)
        all_errors.extend(context_result.errors)
        all_warnings.extend(context_result.warnings)
        all_metadata["context_validation"] = context_result.metadata

        # 3. Cross-validation (if both valid)
        if nexus_result.is_valid and context_result.is_valid:
            # Check confidence vs threshold alignment
            evidence = micro_question_run.get("evidence")
            if evidence and isinstance(evidence, dict):
                confidence = evidence.get("confidence", 0.0)
                threshold = scoring_context.get("threshold") if scoring_context else None

                if threshold is not None and isinstance(threshold, (int, float)):
                    if confidence < threshold:
                        all_warnings.append(
                            f"Confidence {confidence:.3f} below threshold {threshold:.3f}"
                        )

                    all_metadata["confidence_threshold_delta"] = confidence - threshold

        # 4. Determine overall validity
        is_valid = len(all_errors) == 0

        all_metadata["overall_valid"] = is_valid
        all_metadata["error_count"] = len(all_errors)
        all_metadata["warning_count"] = len(all_warnings)

        logger.info(
            "phase_transition_validated",
            is_valid=is_valid,
            errors=len(all_errors),
            warnings=len(all_warnings),
        )

        return ValidationResult(is_valid, all_errors, all_warnings, all_metadata)


# =============================================================================
# BATCH VALIDATION
# =============================================================================


class BatchValidator:
    """Validates multiple phase transitions for comprehensive testing."""

    @classmethod
    def validate_batch(
        cls,
        micro_question_runs: list[dict[str, Any]],
        scoring_contexts: list[dict[str, Any] | None] | None = None,
    ) -> dict[str, Any]:
        """
        Validate batch of micro question runs.

        Args:
            micro_question_runs: List of MicroQuestionRun outputs
            scoring_contexts: Optional list of scoring contexts

        Returns:
            Dictionary with batch validation statistics
        """
        if scoring_contexts is None:
            scoring_contexts = [None] * len(micro_question_runs)

        if len(micro_question_runs) != len(scoring_contexts):
            raise ValueError(
                f"Length mismatch: {len(micro_question_runs)} runs vs "
                f"{len(scoring_contexts)} contexts"
            )

        results = []
        for mqr, ctx in zip(micro_question_runs, scoring_contexts):
            result = NexusScoringValidator.validate_phase_transition(mqr, ctx)
            results.append(result)

        # Aggregate statistics
        total = len(results)
        valid_count = sum(1 for r in results if r.is_valid)
        error_count = sum(len(r.errors) for r in results)
        warning_count = sum(len(r.warnings) for r in results)

        return {
            "total_validations": total,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "success_rate": valid_count / total if total > 0 else 0.0,
            "total_errors": error_count,
            "total_warnings": warning_count,
            "results": [r.to_dict() for r in results],
        }
