"""
Module: phase2_60_03_signature_runtime_validator
PHASE_LABEL: Phase 2
Sequence: M

"""

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 2
__stage__ = 60
__order__ = 3
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "HIGH"
__execution_pattern__ = "Per-Task"



"""
Runtime Signature Validation for Chain Layer

Provides runtime validation of method calls against signature definitions:
- Validates required inputs are present (hard failure if missing)
- Warns about missing critical optional inputs (penalty but no hard failure)
- Tracks optional input usage
- Validates output types and ranges

This module integrates with the orchestrator to ensure method calls comply
with chain layer signature contracts.
"""

import logging
from pathlib import Path
from typing import Any, TypedDict

from orchestration.method_signature_validator import (
    MethodSignatureValidator,
)

logger = logging.getLogger(__name__)


class ValidationResult(TypedDict):
    passed: bool
    hard_failures: list[str]
    soft_failures: list[str]
    warnings: list[str]
    missing_critical_optional: list[str]


class SignatureRuntimeValidator:
    """
    Runtime validator for method signatures in the analysis chain.

    Enforces signature contracts at runtime:
    - Required inputs: MUST be present, raises exception if missing
    - Critical optional: Should be present, logs warning and applies penalty
    - Optional inputs: Nice to have, no penalty
    """

    def __init__(
        self,
        signatures_path: Path | str | None = None,
        strict_mode: bool = True,
        penalty_for_missing_critical: float = 0.1,
    ) -> None:
        if signatures_path is None:
            signatures_path = Path("config/json_files_ no_schemas/method_signatures.json")

        self.validator = MethodSignatureValidator(signatures_path)
        self.validator.load_signatures()
        self.strict_mode = strict_mode
        self.penalty_for_missing_critical = penalty_for_missing_critical
        self._validation_stats: dict[str, dict[str, int]] = {}

    def validate_inputs(self, method_id: str, provided_inputs: dict[str, Any]) -> ValidationResult:
        """
        Validate that provided inputs match method signature requirements.

        Args:
            method_id: Identifier for the method
            provided_inputs: Dictionary of input parameters provided to method

        Returns:
            ValidationResult with passed status and any failures/warnings
        """
        hard_failures = []
        soft_failures = []
        warnings = []
        missing_critical_optional = []

        # Get method signature
        signature = self.validator.get_method_signature(method_id)
        if signature is None:
            if self.strict_mode:
                hard_failures.append(f"Method signature not found for: {method_id}")
            else:
                warnings.append(f"Method signature not found for: {method_id}")

            return ValidationResult(
                passed=len(hard_failures) == 0,
                hard_failures=hard_failures,
                soft_failures=soft_failures,
                warnings=warnings,
                missing_critical_optional=missing_critical_optional,
            )

        # Check required inputs
        required_inputs = signature.get("required_inputs", [])
        for required_input in required_inputs:
            if required_input not in provided_inputs:
                hard_failures.append(
                    f"Required input '{required_input}' missing for method {method_id}"
                )
            elif provided_inputs[required_input] is None:
                hard_failures.append(
                    f"Required input '{required_input}' is None for method {method_id}"
                )

        # Check critical optional inputs
        critical_optional = signature.get("critical_optional", [])
        for critical_input in critical_optional:
            if critical_input not in provided_inputs or provided_inputs[critical_input] is None:
                missing_critical_optional.append(critical_input)
                soft_failures.append(
                    f"Critical optional input '{critical_input}' missing for method {method_id} "
                    f"(penalty: {self.penalty_for_missing_critical})"
                )

        # Track optional inputs usage (for statistics)
        optional_inputs = signature.get("optional_inputs", [])
        provided_optional = [
            inp
            for inp in optional_inputs
            if inp in provided_inputs and provided_inputs[inp] is not None
        ]

        if len(provided_optional) < len(optional_inputs):
            missing_optional = set(optional_inputs) - set(provided_optional)
            warnings.append(f"Optional inputs not provided: {missing_optional}")

        # Record validation stats
        if method_id not in self._validation_stats:
            self._validation_stats[method_id] = {
                "calls": 0,
                "hard_failures": 0,
                "soft_failures": 0,
            }

        self._validation_stats[method_id]["calls"] += 1
        if hard_failures:
            self._validation_stats[method_id]["hard_failures"] += 1
        if soft_failures:
            self._validation_stats[method_id]["soft_failures"] += 1

        passed = len(hard_failures) == 0

        return ValidationResult(
            passed=passed,
            hard_failures=hard_failures,
            soft_failures=soft_failures,
            warnings=warnings,
            missing_critical_optional=missing_critical_optional,
        )

    def validate_output(self, method_id: str, output: Any) -> ValidationResult:
        """
        Validate that method output matches signature specification.

        Args:
            method_id: Identifier for the method
            output: Output value from method execution

        Returns:
            ValidationResult with passed status and any failures/warnings
        """
        hard_failures = []
        soft_failures = []
        warnings = []

        signature = self.validator.get_method_signature(method_id)
        if signature is None:
            warnings.append(f"Method signature not found for output validation: {method_id}")
            return ValidationResult(
                passed=True,
                hard_failures=[],
                soft_failures=[],
                warnings=warnings,
                missing_critical_optional=[],
            )

        # Validate output type
        expected_type = signature.get("output_type", "Any")
        if expected_type != "Any":
            actual_type = type(output).__name__
            if actual_type != expected_type:
                # Try some common conversions
                type_map = {
                    "float": (float, int),
                    "int": (int,),
                    "str": (str,),
                    "list": (list, tuple),
                    "dict": (dict,),
                    "bool": (bool,),
                }

                if expected_type in type_map:
                    if not isinstance(output, type_map[expected_type]):
                        soft_failures.append(
                            f"Output type mismatch for {method_id}: "
                            f"expected {expected_type}, got {actual_type}"
                        )
                else:
                    warnings.append(
                        f"Cannot validate output type for {method_id}: "
                        f"expected {expected_type}, got {actual_type}"
                    )

        # Validate output range
        output_range = signature.get("output_range")
        if output_range is not None and isinstance(output, (int, float)):
            min_val, max_val = output_range
            if not (min_val <= output <= max_val):
                soft_failures.append(
                    f"Output value {output} out of range [{min_val}, {max_val}] "
                    f"for method {method_id}"
                )

        passed = len(hard_failures) == 0

        return ValidationResult(
            passed=passed,
            hard_failures=hard_failures,
            soft_failures=soft_failures,
            warnings=warnings,
            missing_critical_optional=[],
        )

    def calculate_penalty(self, validation_result: ValidationResult) -> float:
        """
        Calculate penalty score based on validation failures.

        Args:
            validation_result: Result from validate_inputs

        Returns:
            Penalty value (0.0 = no penalty, higher = more severe)
        """
        penalty = 0.0

        # Hard failures result in maximum penalty
        if validation_result["hard_failures"]:
            return 1.0

        # Apply penalty for missing critical optional inputs
        num_missing_critical = len(validation_result["missing_critical_optional"])
        penalty += num_missing_critical * self.penalty_for_missing_critical

        # Soft failures add smaller penalty
        penalty += len(validation_result["soft_failures"]) * 0.05

        return min(penalty, 1.0)  # Cap at 1.0

    def get_validation_stats(self) -> dict[str, dict[str, int]]:
        """Get validation statistics for all methods."""
        return self._validation_stats.copy()

    def validate_method_call(
        self,
        method_id: str,
        provided_inputs: dict[str, Any],
        raise_on_failure: bool = True,
    ) -> tuple[bool, float, list[str]]:
        """
        Convenience method to validate a method call.

        Args:
            method_id: Method identifier
            provided_inputs: Input parameters
            raise_on_failure: Whether to raise exception on hard failures

        Returns:
            Tuple of (passed, penalty, messages)

        Raises:
            ValueError: If validation fails and raise_on_failure is True
        """
        result = self.validate_inputs(method_id, provided_inputs)
        penalty = self.calculate_penalty(result)

        messages = []
        if result["hard_failures"]:
            messages.extend(result["hard_failures"])
            if raise_on_failure:
                raise ValueError(
                    f"Method call validation failed for {method_id}:\n"
                    + "\n".join(result["hard_failures"])
                )

        if result["soft_failures"]:
            messages.extend(result["soft_failures"])
            for msg in result["soft_failures"]:
                logger.warning(msg)

        if result["warnings"]:
            messages.extend(result["warnings"])
            for msg in result["warnings"]:
                logger.debug(msg)

        return result["passed"], penalty, messages


# Global validator instance
_runtime_validator: SignatureRuntimeValidator | None = None


def get_runtime_validator(
    signatures_path: Path | str | None = None, strict_mode: bool = True
) -> SignatureRuntimeValidator:
    """Get or create global runtime validator instance."""
    global _runtime_validator

    if _runtime_validator is None:
        _runtime_validator = SignatureRuntimeValidator(
            signatures_path=signatures_path, strict_mode=strict_mode
        )

    return _runtime_validator


def validate_method_call(
    method_id: str, provided_inputs: dict[str, Any], raise_on_failure: bool = True
) -> tuple[bool, float, list[str]]:
    """
    Convenience function to validate a method call using global validator.

    Args:
        method_id: Method identifier
        provided_inputs: Input parameters
        raise_on_failure: Whether to raise exception on hard failures

    Returns:
        Tuple of (passed, penalty, messages)
    """
    validator = get_runtime_validator()
    return validator.validate_method_call(method_id, provided_inputs, raise_on_failure)
