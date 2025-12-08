"""
Signature Validation Mixin for Executors

Provides a mixin class that can be added to executors to enable
automatic signature validation for method calls.
"""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from farfan_pipeline.core.orchestrator.signature_runtime_validator import (
    SignatureRuntimeValidator,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class SignatureValidationMixin:
    """
    Mixin to add signature validation capabilities to executor classes.

    Usage:
        class MyExecutor(SignatureValidationMixin, BaseExecutor):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.init_signature_validation()

            def execute(self, inputs):
                self._validate_method_inputs("my_method", inputs)
                result = self._execute_internal(inputs)
                self._validate_method_output("my_method", result)
                return result
    """

    def init_signature_validation(
        self,
        signatures_path: Path | str | None = None,
        strict_mode: bool = True,
        penalty_for_missing_critical: float = 0.1,
        apply_penalties: bool = True,
    ) -> None:
        """
        Initialize signature validation for this executor.

        Args:
            signatures_path: Path to method_signatures.json
            strict_mode: Raise exceptions for missing signatures
            penalty_for_missing_critical: Penalty for missing critical optional
            apply_penalties: Whether to apply penalties to results
        """
        self._signature_validator = SignatureRuntimeValidator(
            signatures_path=signatures_path,
            strict_mode=strict_mode,
            penalty_for_missing_critical=penalty_for_missing_critical,
        )
        self._apply_penalties = apply_penalties
        self._signature_validation_enabled = True
        logger.info(f"Signature validation initialized for {self.__class__.__name__}")

    def _validate_method_inputs(
        self, method_id: str, inputs: dict[str, Any], raise_on_failure: bool = True
    ) -> tuple[bool, float, list[str]]:
        """
        Validate method inputs against signature.

        Args:
            method_id: Method identifier
            inputs: Input parameters
            raise_on_failure: Whether to raise on validation failure

        Returns:
            Tuple of (passed, penalty, messages)
        """
        if not getattr(self, "_signature_validation_enabled", False):
            logger.warning("Signature validation not initialized")
            return True, 0.0, []

        try:
            passed, penalty, messages = self._signature_validator.validate_method_call(
                method_id=method_id,
                provided_inputs=inputs,
                raise_on_failure=raise_on_failure,
            )

            if not passed:
                logger.error(f"Input validation failed for {method_id}: {messages}")
            elif penalty > 0:
                logger.warning(
                    f"Input validation penalty {penalty} for {method_id}: {messages}"
                )

            return passed, penalty, messages

        except Exception as e:
            logger.error(f"Error during input validation for {method_id}: {e}")
            if raise_on_failure:
                raise
            return False, 1.0, [str(e)]

    def _validate_method_output(self, method_id: str, output: Any) -> ValidationResult:
        """
        Validate method output against signature.

        Args:
            method_id: Method identifier
            output: Output value to validate

        Returns:
            ValidationResult with validation details
        """
        if not getattr(self, "_signature_validation_enabled", False):
            logger.warning("Signature validation not initialized")
            return ValidationResult(
                passed=True,
                hard_failures=[],
                soft_failures=[],
                warnings=[],
                missing_critical_optional=[],
            )

        try:
            result = self._signature_validator.validate_output(method_id, output)

            if result["soft_failures"]:
                logger.warning(
                    f"Output validation issues for {method_id}: "
                    f"{result['soft_failures']}"
                )

            return result

        except Exception as e:
            logger.error(f"Error during output validation for {method_id}: {e}")
            return ValidationResult(
                passed=False,
                hard_failures=[str(e)],
                soft_failures=[],
                warnings=[],
                missing_critical_optional=[],
            )

    def _apply_validation_penalty(self, result: Any, penalty: float) -> Any:
        """
        Apply validation penalty to result.

        This is a default implementation that works for dict results with
        a 'confidence' field and numeric results. Override for custom behavior.

        Args:
            result: Method result
            penalty: Penalty value (0.0 to 1.0)

        Returns:
            Result with penalty applied
        """
        if not self._apply_penalties or penalty == 0.0:
            return result

        if isinstance(result, dict):
            # If result has confidence, apply penalty
            if "confidence" in result:
                original = result["confidence"]
                result["confidence"] = max(0.0, original - penalty)
                result["validation_penalty"] = penalty
                logger.info(
                    f"Applied penalty {penalty} to confidence: "
                    f"{original:.3f} -> {result['confidence']:.3f}"
                )
            # If result has score, apply penalty
            elif "score" in result:
                original = result["score"]
                result["score"] = max(0.0, original - penalty)
                result["validation_penalty"] = penalty
                logger.info(
                    f"Applied penalty {penalty} to score: "
                    f"{original:.3f} -> {result['score']:.3f}"
                )
        elif isinstance(result, (int, float)):
            # For numeric results, subtract penalty
            original = result
            result = max(0.0, result - penalty)
            logger.info(
                f"Applied penalty {penalty} to result: "
                f"{original:.3f} -> {result:.3f}"
            )

        return result

    def get_signature_validation_stats(self) -> dict[str, Any]:
        """Get validation statistics for this executor."""
        if not getattr(self, "_signature_validation_enabled", False):
            return {}

        return self._signature_validator.get_validation_stats()


class ValidatedMethodDecorator:
    """
    Decorator to add signature validation to individual methods.

    Usage:
        @ValidatedMethodDecorator("coherence_validator")
        def validate_coherence(self, extracted_text: str, question_id: str) -> float:
            # Method implementation
            return 0.85
    """

    def __init__(
        self, method_id: str, raise_on_failure: bool = True, apply_penalty: bool = True
    ) -> None:
        self.method_id = method_id
        self.raise_on_failure = raise_on_failure
        self.apply_penalty = apply_penalty
        self._validator: SignatureRuntimeValidator | None = None

    def __call__(self, func: Callable) -> Callable:
        """Wrap method with signature validation."""

        def wrapper(instance: Any, *args: Any, **kwargs: Any) -> Any:
            # Initialize validator if needed
            if self._validator is None:
                self._validator = SignatureRuntimeValidator()

            # Convert positional args to kwargs based on function signature
            import inspect

            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            # Skip 'self' parameter
            if params and params[0] == "self":
                params = params[1:]

            # Build inputs dict
            inputs = {}
            for i, arg in enumerate(args):
                if i < len(params):
                    inputs[params[i]] = arg
            inputs.update(kwargs)

            # Validate inputs
            passed, penalty, messages = self._validator.validate_method_call(
                method_id=self.method_id,
                provided_inputs=inputs,
                raise_on_failure=self.raise_on_failure,
            )

            if not passed and self.raise_on_failure:
                raise ValueError(
                    f"Signature validation failed for {self.method_id}: {messages}"
                )

            # Execute method
            result = func(instance, *args, **kwargs)

            # Validate output
            output_result = self._validator.validate_output(self.method_id, result)
            if output_result["soft_failures"]:
                logger.warning(
                    f"Output validation issues for {self.method_id}: "
                    f"{output_result['soft_failures']}"
                )

            # Apply penalty if configured
            if self.apply_penalty and penalty > 0:
                if isinstance(result, dict) and "confidence" in result:
                    result["confidence"] = max(0.0, result["confidence"] - penalty)
                    result["validation_penalty"] = penalty
                elif isinstance(result, (int, float)):
                    result = max(0.0, result - penalty)

            return result

        return wrapper
