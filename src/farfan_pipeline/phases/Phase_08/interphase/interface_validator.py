"""
Phase 8 Interface Validator
============================

Module: src.farfan_pipeline.phases.Phase_eight.interfaces.interface_validator
Purpose: Validates all inputs and outputs for Phase 8 - Recommendation Engine
Owner: phase8_interfaces
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-05

This module provides comprehensive validation for Phase 8 interface contracts,
ensuring data integrity at phase boundaries.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_08.phase8_20_00_recommendation_engine import (
        Recommendation,
        RecommendationSet,
    )

logger = logging.getLogger(__name__)

# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

# Valid PA identifiers (PA01-PA10)
VALID_PA_PATTERN = re.compile(r"^PA(0[1-9]|10)$")

# Valid DIM identifiers (DIM01-DIM06)
VALID_DIM_PATTERN = re.compile(r"^DIM0[1-6]$")

# Valid PA-DIM score key pattern
VALID_SCORE_KEY_PATTERN = re.compile(r"^PA(0[1-9]|10)-DIM0[1-6]$")

# Valid cluster identifiers (CL01-CL04)
VALID_CLUSTER_PATTERN = re.compile(r"^CL0[1-4]$")

# Score bounds
MICRO_SCORE_MIN = 0.0
MICRO_SCORE_MAX = 3.0

# Recommendation levels
VALID_LEVELS = frozenset({"MICRO", "MESO", "MACRO"})


# ============================================================================
# VALIDATION RESULT DATA STRUCTURES
# ============================================================================


@dataclass
class ValidationError:
    """Represents a single validation error."""

    code: str
    message: str
    field: str | None = None
    value: Any = None
    severity: str = "ERROR"  # ERROR, WARNING, INFO


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    validated_at: str | None = None

    @property
    def is_valid(self) -> bool:
        """Alias for valid property."""
        return self.valid

    def add_error(
        self,
        code: str,
        message: str,
        field: str | None = None,
        value: Any = None,
    ) -> None:
        """Add an error to the result."""
        self.errors.append(
            ValidationError(
                code=code,
                message=message,
                field=field,
                value=value,
                severity="ERROR",
            )
        )
        self.valid = False

    def add_warning(
        self,
        code: str,
        message: str,
        field: str | None = None,
        value: Any = None,
    ) -> None:
        """Add a warning to the result (doesn't invalidate)."""
        self.warnings.append(
            ValidationError(
                code=code,
                message=message,
                field=field,
                value=value,
                severity="WARNING",
            )
        )

    def merge(self, other: ValidationResult) -> None:
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.valid:
            self.valid = False


# ============================================================================
# PHASE 8 INTERFACE VALIDATOR
# ============================================================================


class Phase8InterfaceValidator:
    """
    Comprehensive validator for Phase 8 interface contracts.

    Validates:
    - Input contracts (analysis_results, policy_context, signal_data)
    - Output contracts (recommendations, metadata)
    - Inter-phase data integrity
    """

    def __init__(self, strict_mode: bool = True) -> None:
        """
        Initialize the validator.

        Args:
            strict_mode: If True, all validation errors are fatal.
                        If False, some errors become warnings.
        """
        self.strict_mode = strict_mode
        logger.info(f"Phase8InterfaceValidator initialized (strict_mode={strict_mode})")

    # ========================================================================
    # INPUT VALIDATION
    # ========================================================================

    def validate_inputs(
        self,
        analysis_results: dict[str, Any] | None = None,
        policy_context: dict[str, Any] | None = None,
        signal_data: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """
        Validate all Phase 8 input contracts.

        Args:
            analysis_results: P8-IN-001 - Aggregated scoring results
            policy_context: P8-IN-002 - Policy area context
            signal_data: P8-IN-003 - Optional signal enrichment data

        Returns:
            ValidationResult with any errors/warnings
        """
        result = ValidationResult(valid=True)

        # Validate required inputs
        if analysis_results is None:
            result.add_error(
                code="P8-VAL-IN-001",
                message="analysis_results is required but not provided",
                field="analysis_results",
            )
        else:
            result.merge(self.validate_analysis_results(analysis_results))

        if policy_context is None:
            result.add_error(
                code="P8-VAL-IN-002",
                message="policy_context is required but not provided",
                field="policy_context",
            )
        else:
            result.merge(self.validate_policy_context(policy_context))

        # Validate optional signal_data if provided
        if signal_data is not None:
            result.merge(self.validate_signal_data(signal_data))

        return result

    def validate_analysis_results(
        self,
        analysis_results: dict[str, Any],
    ) -> ValidationResult:
        """
        Validate the analysis_results input contract (P8-IN-001).

        Expected structure:
        {
            "micro_scores": {"PA01-DIM01": 1.5, ...},
            "cluster_data": {"CL01": {"score": 75.0, ...}, ...},
            "macro_data": {"macro_band": "SATISFACTORIO", ...}
        }
        """
        result = ValidationResult(valid=True)

        # Check for micro_scores
        micro_scores = analysis_results.get("micro_scores")
        if micro_scores is None:
            result.add_error(
                code="P8-VAL-IN-001-A",
                message="micro_scores is missing from analysis_results",
                field="analysis_results.micro_scores",
            )
        elif not isinstance(micro_scores, dict):
            result.add_error(
                code="P8-VAL-IN-001-B",
                message="micro_scores must be a dictionary",
                field="analysis_results.micro_scores",
                value=type(micro_scores).__name__,
            )
        else:
            result.merge(self._validate_micro_scores(micro_scores))

        # Check for cluster_data
        cluster_data = analysis_results.get("cluster_data")
        if cluster_data is None:
            result.add_error(
                code="P8-VAL-IN-001-C",
                message="cluster_data is missing from analysis_results",
                field="analysis_results.cluster_data",
            )
        elif not isinstance(cluster_data, dict):
            result.add_error(
                code="P8-VAL-IN-001-D",
                message="cluster_data must be a dictionary",
                field="analysis_results.cluster_data",
                value=type(cluster_data).__name__,
            )
        else:
            result.merge(self._validate_cluster_data(cluster_data))

        # Check for macro_data
        macro_data = analysis_results.get("macro_data")
        if macro_data is None:
            result.add_error(
                code="P8-VAL-IN-001-E",
                message="macro_data is missing from analysis_results",
                field="analysis_results.macro_data",
            )
        elif not isinstance(macro_data, dict):
            result.add_error(
                code="P8-VAL-IN-001-F",
                message="macro_data must be a dictionary",
                field="analysis_results.macro_data",
                value=type(macro_data).__name__,
            )
        else:
            result.merge(self._validate_macro_data(macro_data))

        return result

    def _validate_micro_scores(
        self,
        micro_scores: dict[str, float],
    ) -> ValidationResult:
        """Validate micro_scores structure and values."""
        result = ValidationResult(valid=True)

        for key, value in micro_scores.items():
            # Validate key format
            if not VALID_SCORE_KEY_PATTERN.match(key):
                result.add_error(
                    code="P8-VAL-MICRO-001",
                    message=f"Invalid score key format: {key}. Expected PA##-DIM##",
                    field=f"micro_scores.{key}",
                    value=key,
                )
                continue

            # Validate score value
            if not isinstance(value, (int, float)):
                result.add_error(
                    code="P8-VAL-MICRO-002",
                    message=f"Score value must be numeric for {key}",
                    field=f"micro_scores.{key}",
                    value=type(value).__name__,
                )
            elif not MICRO_SCORE_MIN <= value <= MICRO_SCORE_MAX:
                result.add_error(
                    code="P8-VAL-MICRO-003",
                    message=f"Score value {value} for {key} out of range [{MICRO_SCORE_MIN}, {MICRO_SCORE_MAX}]",
                    field=f"micro_scores.{key}",
                    value=value,
                )

        return result

    def _validate_cluster_data(
        self,
        cluster_data: dict[str, Any],
    ) -> ValidationResult:
        """Validate cluster_data structure."""
        result = ValidationResult(valid=True)

        for key, value in cluster_data.items():
            # Validate key format
            if not VALID_CLUSTER_PATTERN.match(key):
                result.add_error(
                    code="P8-VAL-CLUSTER-001",
                    message=f"Invalid cluster key format: {key}. Expected CL01-CL04",
                    field=f"cluster_data.{key}",
                    value=key,
                )
                continue

            # Validate cluster structure
            if not isinstance(value, dict):
                result.add_error(
                    code="P8-VAL-CLUSTER-002",
                    message=f"Cluster {key} data must be a dictionary",
                    field=f"cluster_data.{key}",
                    value=type(value).__name__,
                )
                continue

            # Check for required fields
            if "score" not in value:
                result.add_error(
                    code="P8-VAL-CLUSTER-003",
                    message=f"Cluster {key} missing required field 'score'",
                    field=f"cluster_data.{key}.score",
                )

        return result

    def _validate_macro_data(
        self,
        macro_data: dict[str, Any],
    ) -> ValidationResult:
        """Validate macro_data structure."""
        result = ValidationResult(valid=True)

        # Check for macro_band (optional but commonly expected)
        if "macro_band" not in macro_data:
            result.add_warning(
                code="P8-VAL-MACRO-001",
                message="macro_band not found in macro_data",
                field="macro_data.macro_band",
            )

        return result

    def validate_policy_context(
        self,
        policy_context: dict[str, Any],
    ) -> ValidationResult:
        """
        Validate the policy_context input contract (P8-IN-002).

        Expected structure:
        {
            "policy_area_id": "PA01",
            "dimension_id": "DIM01",
            "question_global": 1
        }
        """
        result = ValidationResult(valid=True)

        # Validate policy_area_id if present
        pa_id = policy_context.get("policy_area_id")
        if pa_id is not None and not VALID_PA_PATTERN.match(str(pa_id)):
            result.add_error(
                code="P8-VAL-CTX-001",
                message=f"Invalid policy_area_id format: {pa_id}",
                field="policy_context.policy_area_id",
                value=pa_id,
            )

        # Validate dimension_id if present
        dim_id = policy_context.get("dimension_id")
        if dim_id is not None and not VALID_DIM_PATTERN.match(str(dim_id)):
            result.add_error(
                code="P8-VAL-CTX-002",
                message=f"Invalid dimension_id format: {dim_id}",
                field="policy_context.dimension_id",
                value=dim_id,
            )

        return result

    def validate_signal_data(
        self,
        signal_data: dict[str, Any],
    ) -> ValidationResult:
        """
        Validate the optional signal_data input contract (P8-IN-003).
        """
        result = ValidationResult(valid=True)

        # Signal data is optional, so light validation
        if not isinstance(signal_data, dict):
            result.add_error(
                code="P8-VAL-SIG-001",
                message="signal_data must be a dictionary when provided",
                field="signal_data",
                value=type(signal_data).__name__,
            )

        return result

    # ========================================================================
    # OUTPUT VALIDATION
    # ========================================================================

    def validate_outputs(
        self,
        recommendations: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """
        Validate all Phase 8 output contracts.

        Args:
            recommendations: P8-OUT-001 - Generated recommendations by level
            metadata: P8-OUT-002 - Recommendation metadata

        Returns:
            ValidationResult with any errors/warnings
        """
        result = ValidationResult(valid=True)

        # Validate recommendations
        result.merge(self._validate_recommendations_output(recommendations))

        # Validate metadata if provided
        if metadata is not None:
            result.merge(self._validate_metadata_output(metadata))

        return result

    def _validate_recommendations_output(
        self,
        recommendations: dict[str, Any],
    ) -> ValidationResult:
        """Validate recommendations output contract (P8-OUT-001)."""
        result = ValidationResult(valid=True)

        if not isinstance(recommendations, dict):
            result.add_error(
                code="P8-VAL-OUT-001",
                message="recommendations must be a dictionary",
                field="recommendations",
                value=type(recommendations).__name__,
            )
            return result

        # Check for expected levels
        for level in VALID_LEVELS:
            if level not in recommendations:
                result.add_warning(
                    code="P8-VAL-OUT-002",
                    message=f"Expected level {level} not found in recommendations",
                    field=f"recommendations.{level}",
                )

        # Validate each level's RecommendationSet
        for level, rec_set in recommendations.items():
            if level not in VALID_LEVELS:
                result.add_warning(
                    code="P8-VAL-OUT-003",
                    message=f"Unknown recommendation level: {level}",
                    field=f"recommendations.{level}",
                    value=level,
                )
                continue

            result.merge(self._validate_recommendation_set(level, rec_set))

        return result

    def _validate_recommendation_set(
        self,
        level: str,
        rec_set: Any,
    ) -> ValidationResult:
        """Validate a single RecommendationSet."""
        result = ValidationResult(valid=True)

        # Handle both object and dict representations
        if hasattr(rec_set, "to_dict"):
            rec_dict = rec_set.to_dict()
        elif isinstance(rec_set, dict):
            rec_dict = rec_set
        else:
            result.add_error(
                code="P8-VAL-OUT-SET-001",
                message=f"RecommendationSet for {level} must be a dict or have to_dict()",
                field=f"recommendations.{level}",
                value=type(rec_set).__name__,
            )
            return result

        # Validate required fields
        required_fields = ["level", "recommendations", "generated_at"]
        for field_name in required_fields:
            if field_name not in rec_dict:
                result.add_error(
                    code="P8-VAL-OUT-SET-002",
                    message=f"RecommendationSet for {level} missing required field: {field_name}",
                    field=f"recommendations.{level}.{field_name}",
                )

        # Validate level matches
        if rec_dict.get("level") != level:
            result.add_error(
                code="P8-VAL-OUT-SET-003",
                message=f"RecommendationSet level mismatch: expected {level}, got {rec_dict.get('level')}",
                field=f"recommendations.{level}.level",
                value=rec_dict.get("level"),
            )

        return result

    def _validate_metadata_output(
        self,
        metadata: dict[str, Any],
    ) -> ValidationResult:
        """Validate metadata output contract (P8-OUT-002)."""
        result = ValidationResult(valid=True)

        if not isinstance(metadata, dict):
            result.add_error(
                code="P8-VAL-OUT-META-001",
                message="metadata must be a dictionary",
                field="metadata",
                value=type(metadata).__name__,
            )
            return result

        # Check for expected metadata fields
        expected_fields = ["generated_at", "total_rules_evaluated", "rules_matched"]
        for field_name in expected_fields:
            if field_name not in metadata:
                result.add_warning(
                    code="P8-VAL-OUT-META-002",
                    message=f"Expected metadata field missing: {field_name}",
                    field=f"metadata.{field_name}",
                )

        return result

    # ========================================================================
    # CONTRACT VALIDATION
    # ========================================================================

    def validate_input_contracts(
        self,
        contracts: dict[str, Any],
    ) -> ValidationResult:
        """
        Full contract validation for all inputs.

        Args:
            contracts: Dictionary of contract_id -> data

        Returns:
            ValidationResult
        """
        result = ValidationResult(valid=True)

        for contract_id, data in contracts.items():
            if contract_id == "P8-IN-001":
                result.merge(self.validate_analysis_results(data))
            elif contract_id == "P8-IN-002":
                result.merge(self.validate_policy_context(data))
            elif contract_id == "P8-IN-003":
                result.merge(self.validate_signal_data(data))
            else:
                result.add_warning(
                    code="P8-VAL-CONTRACT-001",
                    message=f"Unknown input contract: {contract_id}",
                    field=contract_id,
                )

        return result

    def validate_output_contracts(
        self,
        contracts: dict[str, Any],
    ) -> ValidationResult:
        """
        Full contract validation for all outputs.

        Args:
            contracts: Dictionary of contract_id -> data

        Returns:
            ValidationResult
        """
        result = ValidationResult(valid=True)

        for contract_id, data in contracts.items():
            if contract_id == "P8-OUT-001":
                result.merge(self._validate_recommendations_output(data))
            elif contract_id == "P8-OUT-002":
                result.merge(self._validate_metadata_output(data))
            else:
                result.add_warning(
                    code="P8-VAL-CONTRACT-002",
                    message=f"Unknown output contract: {contract_id}",
                    field=contract_id,
                )

        return result


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def validate_phase8_inputs(
    analysis_results: dict[str, Any] | None = None,
    policy_context: dict[str, Any] | None = None,
    signal_data: dict[str, Any] | None = None,
    strict_mode: bool = True,
) -> ValidationResult:
    """
    Convenience function to validate Phase 8 inputs.

    Args:
        analysis_results: Aggregated scoring results
        policy_context: Policy area context
        signal_data: Optional signal enrichment data
        strict_mode: Whether to use strict validation

    Returns:
        ValidationResult
    """
    validator = Phase8InterfaceValidator(strict_mode=strict_mode)
    return validator.validate_inputs(
        analysis_results=analysis_results,
        policy_context=policy_context,
        signal_data=signal_data,
    )


def validate_phase8_outputs(
    recommendations: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    strict_mode: bool = True,
) -> ValidationResult:
    """
    Convenience function to validate Phase 8 outputs.

    Args:
        recommendations: Generated recommendations
        metadata: Recommendation metadata
        strict_mode: Whether to use strict validation

    Returns:
        ValidationResult
    """
    validator = Phase8InterfaceValidator(strict_mode=strict_mode)
    return validator.validate_outputs(
        recommendations=recommendations,
        metadata=metadata,
    )


__all__ = [
    "Phase8InterfaceValidator",
    "ValidationResult",
    "ValidationError",
    "validate_phase8_inputs",
    "validate_phase8_outputs",
]
