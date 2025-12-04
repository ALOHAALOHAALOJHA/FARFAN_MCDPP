#!/usr/bin/env python3
"""
Validation Predicates - Precondition Checks for Execution
=========================================================

Provides reusable predicates for validating preconditions before
executing analysis steps.

Author: Integration Team - Agent 3
Version: 1.0.0
Python: 3.10+
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    """Result of a validation check."""

    is_valid: bool
    severity: str  # ERROR, WARNING, INFO
    message: str
    context: dict[str, Any]


class ValidationPredicates:
    """
    Collection of validation predicates for precondition checking.

    These predicates verify that all required preconditions are met
    before executing specific analysis steps.
    """

    @staticmethod
    def verify_scoring_preconditions(
        question_spec: dict[str, Any], execution_results: dict[str, Any], plan_text: str
    ) -> ValidationResult:
        """
        Verify preconditions for TYPE_A scoring modality.

        PRECONDITIONS for TYPE_A (Binary presence/absence):
        - question_spec must have expected_elements list
        - execution_results must be non-empty dict
        - plan_text must be non-empty string

        Args:
            question_spec: Question specification from rubric
            execution_results: Results from execution pipeline
            plan_text: Full plan document text

        Returns:
            ValidationResult indicating if preconditions are met
        """
        errors = []

        # Check question_spec has expected_elements
        if not isinstance(question_spec, dict):
            errors.append("question_spec must be a dictionary")
        elif "expected_elements" not in question_spec:
            errors.append("question_spec must have 'expected_elements' field")
        elif not isinstance(question_spec.get("expected_elements"), list):
            errors.append("expected_elements must be a list")
        elif len(question_spec.get("expected_elements", [])) == 0:
            errors.append("expected_elements cannot be empty")

        # Check execution_results
        if not isinstance(execution_results, dict):
            errors.append("execution_results must be a dictionary")
        elif len(execution_results) == 0:
            errors.append("execution_results cannot be empty")

        # Check plan_text
        if not isinstance(plan_text, str):
            errors.append("plan_text must be a string")
        elif len(plan_text.strip()) == 0:
            errors.append("plan_text cannot be empty")

        if errors:
            return ValidationResult(
                is_valid=False,
                severity="ERROR",
                message="; ".join(errors),
                context={
                    "question_id": question_spec.get("id", "UNKNOWN"),
                    "errors": errors,
                },
            )

        return ValidationResult(
            is_valid=True,
            severity="INFO",
            message="All scoring preconditions met",
            context={
                "question_id": question_spec.get("id"),
                "expected_elements_count": len(
                    question_spec.get("expected_elements", [])
                ),
                "execution_results_keys": list(execution_results.keys()),
            },
        )

    @staticmethod
    def _validate_expected_elements_types(
        question_schema: str, chunk_schema: str, question_id: str
    ) -> ValidationResult:
        """
        Validate that question_schema and chunk_schema have valid types.

        Args:
            question_schema: Classified type of question_schema ("None", "list", "dict", "invalid")
            chunk_schema: Classified type of chunk_schema ("None", "list", "dict", "invalid")
            question_id: Question identifier for error context

        Returns:
            ValidationResult indicating if schema types are valid

        Raises:
            TypeError: If either schema has invalid type (not None, list, or dict)
        """
        errors = []

        if question_schema == "invalid":
            errors.append("question_schema has invalid type (not None, list, or dict)")

        if chunk_schema == "invalid":
            errors.append("chunk_schema has invalid type (not None, list, or dict)")

        if errors:
            raise TypeError(
                f"Question {question_id} has invalid schema types: {'; '.join(errors)}"
            )

        return ValidationResult(
            is_valid=True,
            severity="INFO",
            message=f"Question {question_id} has valid schema types",
            context={
                "question_id": question_id,
                "question_schema_type": question_schema,
                "chunk_schema_type": chunk_schema,
            },
        )

    @staticmethod
    def _validate_element_compatibility(
        question_schema: str, chunk_schema: str, question_id: str
    ) -> ValidationResult:
        """
        Validate compatibility between question_schema and chunk_schema types.

        Args:
            question_schema: Classified type of question_schema ("None", "list", "dict", "invalid")
            chunk_schema: Classified type of chunk_schema ("None", "list", "dict", "invalid")
            question_id: Question identifier for error context

        Returns:
            ValidationResult indicating if schemas are compatible
        """
        warnings = []

        if question_schema == "None" and chunk_schema != "None":
            warnings.append("question_schema is None but chunk_schema is not")

        if question_schema != "None" and chunk_schema == "None":
            warnings.append("chunk_schema is None but question_schema is not")

        if question_schema == "list" and chunk_schema == "dict":
            warnings.append(
                "question_schema is list but chunk_schema is dict (potential structure mismatch)"
            )

        if question_schema == "dict" and chunk_schema == "list":
            warnings.append(
                "question_schema is dict but chunk_schema is list (potential structure mismatch)"
            )

        if warnings:
            return ValidationResult(
                is_valid=True,
                severity="WARNING",
                message=f"Question {question_id} has schema compatibility warnings: {'; '.join(warnings)}",
                context={
                    "question_id": question_id,
                    "question_schema_type": question_schema,
                    "chunk_schema_type": chunk_schema,
                    "warnings": warnings,
                },
            )

        return ValidationResult(
            is_valid=True,
            severity="INFO",
            message=f"Question {question_id} schemas are compatible",
            context={
                "question_id": question_id,
                "question_schema_type": question_schema,
                "chunk_schema_type": chunk_schema,
            },
        )

    @staticmethod
    def verify_expected_elements(
        question_spec: dict[str, Any], cuestionario_data: dict[str, Any] | None = None
    ) -> ValidationResult:
        """
        Verify that expected_elements are defined correctly.

        Args:
            question_spec: Question specification from rubric
            cuestionario_data: Full cuestionario metadata

        Returns:
            ValidationResult indicating if expected_elements are valid
        """
        question_id = question_spec.get("id", "UNKNOWN")

        expected_elements = question_spec.get("expected_elements")
        question_schema_raw = expected_elements
        chunk_schema_raw = question_spec.get("chunk_schema")

        if question_schema_raw is None:
            question_type = "None"
        elif isinstance(question_schema_raw, list):
            question_type = "list"
        elif isinstance(question_schema_raw, dict):
            question_type = "dict"
        else:
            question_type = "invalid"

        if chunk_schema_raw is None:
            chunk_type = "None"
        elif isinstance(chunk_schema_raw, list):
            chunk_type = "list"
        elif isinstance(chunk_schema_raw, dict):
            chunk_type = "dict"
        else:
            chunk_type = "invalid"

        schema_types = (question_type, chunk_type)

        ValidationPredicates._validate_expected_elements_types(
            schema_types[0], schema_types[1], question_id
        )

        compatibility_validation = ValidationPredicates._validate_element_compatibility(
            schema_types[0], schema_types[1], question_id
        )

        if question_type == "None":
            return ValidationResult(
                is_valid=False,
                severity="WARNING",
                message=f"Question {question_id} has no expected_elements defined",
                context={"question_id": question_id, "schema_types": schema_types},
            )

        if (
            question_type == "list"
            and expected_elements is not None
            and len(expected_elements) == 0
        ):
            return ValidationResult(
                is_valid=False,
                severity="WARNING",
                message=f"Question {question_id} has empty expected_elements",
                context={"question_id": question_id, "schema_types": schema_types},
            )

        element_count = None
        if question_type == "list" and expected_elements is not None:
            element_count = len(expected_elements)

        return ValidationResult(
            is_valid=True,
            severity="INFO",
            message=f"Question {question_id} has valid expected_elements",
            context={
                "question_id": question_id,
                "expected_elements": expected_elements,
                "count": element_count,
                "schema_types": schema_types,
                "compatibility_check": compatibility_validation.context,
            },
        )

    @staticmethod
    def verify_execution_context(
        question_id: str, policy_area: str, dimension: str
    ) -> ValidationResult:
        """
        Verify execution context parameters are valid.

        Args:
            question_id: Canonical question ID (P#-D#-Q#)
            policy_area: Policy area (P1-P10)
            dimension: Dimension (D1-D6)

        Returns:
            ValidationResult indicating if context is valid
        """
        errors = []

        # Validate question_id format
        if not question_id or not isinstance(question_id, str):
            errors.append("question_id must be a non-empty string")
        elif not question_id.startswith("P"):
            errors.append(f"question_id '{question_id}' must start with 'P'")

        # Validate policy_area
        if not policy_area or not isinstance(policy_area, str):
            errors.append("policy_area must be a non-empty string")
        elif not policy_area.startswith("P"):
            errors.append(f"policy_area '{policy_area}' must start with 'P'")
        else:
            try:
                area_num = int(policy_area[1:])
                if not (1 <= area_num <= 10):
                    errors.append(f"policy_area '{policy_area}' must be P1-P10")
            except ValueError:
                errors.append(f"Invalid policy_area format: '{policy_area}'")

        # Validate dimension
        if not dimension or not isinstance(dimension, str):
            errors.append("dimension must be a non-empty string")
        elif not dimension.startswith("D"):
            errors.append(f"dimension '{dimension}' must start with 'D'")
        else:
            try:
                dim_num = int(dimension[1:])
                if not (1 <= dim_num <= 6):
                    errors.append(f"dimension '{dimension}' must be D1-D6")
            except ValueError:
                errors.append(f"Invalid dimension format: '{dimension}'")

        if errors:
            return ValidationResult(
                is_valid=False,
                severity="ERROR",
                message="; ".join(errors),
                context={
                    "question_id": question_id,
                    "policy_area": policy_area,
                    "dimension": dimension,
                    "errors": errors,
                },
            )

        return ValidationResult(
            is_valid=True,
            severity="INFO",
            message="Execution context is valid",
            context={
                "question_id": question_id,
                "policy_area": policy_area,
                "dimension": dimension,
            },
        )

    @staticmethod
    def verify_producer_availability(
        producer_name: str, producers_dict: dict[str, Any]
    ) -> ValidationResult:
        """
        Verify that a producer module is available and initialized.

        Args:
            producer_name: Name of the producer (e.g., 'derek_beach')
            producers_dict: Dictionary of initialized producers

        Returns:
            ValidationResult indicating if producer is available
        """
        if producer_name not in producers_dict:
            return ValidationResult(
                is_valid=False,
                severity="ERROR",
                message=f"Producer '{producer_name}' not found in initialized producers",
                context={
                    "producer_name": producer_name,
                    "available_producers": list(producers_dict.keys()),
                },
            )

        producer = producers_dict[producer_name]

        # Check if producer is initialized
        if isinstance(producer, dict):
            status = producer.get("status")
            if status != "initialized":
                return ValidationResult(
                    is_valid=False,
                    severity="ERROR",
                    message=f"Producer '{producer_name}' status is '{status}'",
                    context={
                        "producer_name": producer_name,
                        "status": status,
                        "error": producer.get("error"),
                    },
                )

        return ValidationResult(
            is_valid=True,
            severity="INFO",
            message=f"Producer '{producer_name}' is available and initialized",
            context={"producer_name": producer_name, "status": "initialized"},
        )
