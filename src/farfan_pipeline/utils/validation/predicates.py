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
        question_schema: list[Any] | dict[str, Any] | None,
        chunk_schema: list[Any] | dict[str, Any] | None,
        question_id: str,
    ) -> ValidationResult:
        """
        Validate that question_schema and chunk_schema have valid types.

        Args:
            question_schema: Schema object (None, list, or dict)
            chunk_schema: Schema object (None, list, or dict)
            question_id: Question identifier for error context

        Returns:
            ValidationResult indicating if schema types are valid

        Raises:
            TypeError: If either schema has invalid type (not None, list, or dict)
            ValueError: If schemas are both lists with different lengths or both dicts with different keys
        """
        if question_schema is None and chunk_schema is None:
            return ValidationResult(
                is_valid=True,
                severity="INFO",
                message=f"Question {question_id} has valid schema types",
                context={
                    "question_id": question_id,
                    "question_schema_type": "None",
                    "chunk_schema_type": "None",
                },
            )

        errors = []

        if question_schema is not None and not isinstance(question_schema, list | dict):
            errors.append("question_schema has invalid type (not None, list, or dict)")

        if chunk_schema is not None and not isinstance(chunk_schema, list | dict):
            errors.append("chunk_schema has invalid type (not None, list, or dict)")

        if errors:
            raise TypeError(
                f"Question {question_id} has invalid schema types: {'; '.join(errors)}"
            )

        if (
            isinstance(question_schema, list)
            and isinstance(chunk_schema, list)
            and len(question_schema) != len(chunk_schema)
        ):
            raise ValueError(
                f"Question {question_id} schema length mismatch: "
                f"question_schema has {len(question_schema)} elements, "
                f"chunk_schema has {len(chunk_schema)} elements"
            )

        if isinstance(question_schema, dict) and isinstance(chunk_schema, dict):
            question_keys = set(question_schema.keys())
            chunk_keys = set(chunk_schema.keys())
            key_diff = question_keys.symmetric_difference(chunk_keys)
            if key_diff:
                sorted_diff = sorted(key_diff)
                raise ValueError(
                    f"Question {question_id} schema key mismatch: "
                    f"symmetric difference in keys: {sorted_diff}"
                )

        question_type = (
            "None"
            if question_schema is None
            else "list" if isinstance(question_schema, list) else "dict"
        )
        chunk_type = (
            "None"
            if chunk_schema is None
            else "list" if isinstance(chunk_schema, list) else "dict"
        )

        return ValidationResult(
            is_valid=True,
            severity="INFO",
            message=f"Question {question_id} has valid schema types",
            context={
                "question_id": question_id,
                "question_schema_type": question_type,
                "chunk_schema_type": chunk_type,
            },
        )

    @staticmethod
    def _validate_element_compatibility(
        question_elements: list[dict[str, Any]],
        chunk_elements: list[dict[str, Any]],
        question_id: str,
    ) -> int:
        """
        Validate compatibility between question elements and chunk elements.

        Validates type, required, and minimum fields for all element pairs.

        Args:
            question_elements: List of element dictionaries from question schema
            chunk_elements: List of element dictionaries from chunk schema
            question_id: Question identifier for error context

        Returns:
            Count of successfully validated element pairs

        Raises:
            ValueError: If element validation fails (type mismatch, required field missing,
                       or minimum threshold not met)
        """
        if not question_elements and not chunk_elements:
            return 0

        if len(question_elements) != len(chunk_elements):
            raise ValueError(
                f"Question {question_id}: element count mismatch - "
                f"question has {len(question_elements)} elements, "
                f"chunk has {len(chunk_elements)} elements"
            )

        validated_count = 0

        for idx, (q_elem, c_elem) in enumerate(
            zip(question_elements, chunk_elements, strict=True)
        ):
            if not isinstance(q_elem, dict) or not isinstance(c_elem, dict):
                raise ValueError(
                    f"Question {question_id}: element at index {idx} must be a dictionary"
                )

            # Type validation
            q_type = q_elem.get("type")
            c_type = c_elem.get("type")
            if q_type and c_type and q_type != c_type:
                raise ValueError(
                    f"Question {question_id}: element type mismatch at index {idx} - "
                    f"question expects type '{q_type}', chunk has type '{c_type}'"
                )

            # Required field validation
            q_required = q_elem.get("required", False)
            c_required = c_elem.get("required", False)
            if q_required and not c_required:
                raise ValueError(
                    f"Question {question_id}: required field mismatch at index {idx} - "
                    f"question requires element but chunk does not"
                )

            # Minimum field validation
            q_minimum = q_elem.get("minimum", 0)
            c_minimum = c_elem.get("minimum", 0)
            if c_minimum < q_minimum:
                element_type = q_elem.get("type", "unknown")
                raise ValueError(
                    f"Question {question_id}: minimum threshold not met at index {idx} - "
                    f"element type '{element_type}' requires minimum {q_minimum}, "
                    f"but chunk has minimum {c_minimum}"
                )

            validated_count += 1

        return validated_count

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
            question_schema_raw, chunk_schema_raw, question_id
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

        # Validate element compatibility if both schemas are lists of dicts
        validated_element_count = 0
        if (
            question_type == "list"
            and chunk_type == "list"
            and expected_elements
            and all(isinstance(e, dict) for e in expected_elements)
        ):
            chunk_elements = (
                chunk_schema_raw if isinstance(chunk_schema_raw, list) else []
            )
            if chunk_elements and all(isinstance(e, dict) for e in chunk_elements):
                try:
                    validated_element_count = (
                        ValidationPredicates._validate_element_compatibility(
                            expected_elements, chunk_elements, question_id
                        )
                    )
                except ValueError as e:
                    return ValidationResult(
                        is_valid=False,
                        severity="ERROR",
                        message=str(e),
                        context={
                            "question_id": question_id,
                            "schema_types": schema_types,
                        },
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
                "validated_element_count": validated_element_count,
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
