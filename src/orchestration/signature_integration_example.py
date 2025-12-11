"""
Example integration of signature validation with orchestrator.

This module demonstrates how to integrate chain layer signature validation
into the execution pipeline for method calls.
"""

from typing import Any, Callable
import logging

from orchestration.signature_runtime_validator import (
    SignatureRuntimeValidator,
    get_runtime_validator,
)

logger = logging.getLogger(__name__)


class SignatureValidatedExecutor:
    """
    Example executor that validates method signatures at runtime.

    This demonstrates how to wrap method execution with signature validation
    to ensure contract compliance.
    """

    def __init__(
        self,
        validator: SignatureRuntimeValidator | None = None,
        apply_penalties: bool = True,
        raise_on_failure: bool = True,
    ) -> None:
        self.validator = validator or get_runtime_validator()
        self.apply_penalties = apply_penalties
        self.raise_on_failure = raise_on_failure
        self.execution_log: list[dict[str, Any]] = []

    def execute_method(
        self,
        method_id: str,
        method_callable: Callable,
        inputs: dict[str, Any],
        **kwargs: Any,
    ) -> tuple[Any, dict[str, Any]]:
        """
        Execute a method with signature validation.

        Args:
            method_id: Identifier for method signature
            method_callable: The actual method to call
            inputs: Input parameters for the method
            **kwargs: Additional arguments passed to method

        Returns:
            Tuple of (result, execution_metadata)
        """
        execution_metadata = {
            "method_id": method_id,
            "validation_passed": False,
            "penalty": 0.0,
            "validation_messages": [],
            "execution_status": "pending",
        }

        try:
            # Validate inputs before execution
            passed, penalty, messages = self.validator.validate_method_call(
                method_id=method_id,
                provided_inputs=inputs,
                raise_on_failure=self.raise_on_failure,
            )

            execution_metadata["validation_passed"] = passed
            execution_metadata["penalty"] = penalty
            execution_metadata["validation_messages"] = messages

            if not passed and self.raise_on_failure:
                execution_metadata["execution_status"] = "failed_validation"
                raise ValueError(f"Validation failed for {method_id}: {messages}")

            # Log warnings for missing critical optional
            if penalty > 0 and self.apply_penalties:
                logger.warning(
                    f"Method {method_id} has penalty {penalty} for missing inputs: "
                    f"{messages}"
                )

            # Execute the method
            logger.info(f"Executing method: {method_id}")
            result = method_callable(**inputs, **kwargs)

            # Validate output
            output_validation = self.validator.validate_output(method_id, result)
            if not output_validation["passed"]:
                logger.warning(
                    f"Output validation issues for {method_id}: "
                    f"{output_validation['soft_failures']}"
                )
                execution_metadata["validation_messages"].extend(
                    output_validation["soft_failures"]
                )

            execution_metadata["execution_status"] = "success"

            # Apply penalty to result if applicable (example)
            if self.apply_penalties and penalty > 0:
                execution_metadata["adjusted_confidence"] = (
                    self._apply_penalty_to_result(result, penalty)
                )

            return result, execution_metadata

        except Exception as e:
            execution_metadata["execution_status"] = "error"
            execution_metadata["error"] = str(e)
            logger.error(f"Execution failed for {method_id}: {e}")
            raise

        finally:
            # Log execution
            self.execution_log.append(execution_metadata)

    def _apply_penalty_to_result(self, result: Any, penalty: float) -> Any:
        """
        Apply penalty to result (example implementation).

        In a real system, this might adjust confidence scores or
        add penalty terms to the result structure.
        """
        if isinstance(result, dict) and "confidence" in result:
            original_confidence = result["confidence"]
            adjusted = max(0.0, original_confidence - penalty)
            logger.info(
                f"Adjusted confidence: {original_confidence:.3f} -> {adjusted:.3f} "
                f"(penalty: {penalty:.3f})"
            )
            return adjusted
        elif isinstance(result, (int, float)):
            return max(0.0, result - penalty)

        return result

    def get_execution_summary(self) -> dict[str, Any]:
        """Get summary of all method executions."""
        total_executions = len(self.execution_log)
        failed_validations = sum(
            1 for log in self.execution_log if not log["validation_passed"]
        )
        total_penalty = sum(log["penalty"] for log in self.execution_log)

        return {
            "total_executions": total_executions,
            "failed_validations": failed_validations,
            "success_rate": (
                (total_executions - failed_validations) / total_executions
                if total_executions > 0
                else 0.0
            ),
            "total_penalty": total_penalty,
            "average_penalty": (
                total_penalty / total_executions if total_executions > 0 else 0.0
            ),
            "execution_log": self.execution_log,
        }


def example_usage() -> None:
    """
    Example usage of signature-validated executor.
    """
    # Create validator
    executor = SignatureValidatedExecutor(
        apply_penalties=True, raise_on_failure=False  # Log but don't fail hard
    )

    # Example method
    def coherence_validator(
        extracted_text: str,
        question_id: str,
        reference_corpus: str | None = None,
        threshold: float = 0.5,
    ) -> float:
        """Example method implementation."""
        # Simulate coherence calculation
        base_score = 0.8
        if reference_corpus:
            base_score += 0.1  # Bonus for having reference corpus
        return min(1.0, base_score)

    # Execute with all inputs (no penalty)
    print("Example 1: Complete inputs")
    result1, metadata1 = executor.execute_method(
        method_id="coherence_validator",
        method_callable=coherence_validator,
        inputs={
            "extracted_text": "Policy text about economic development",
            "question_id": "D1-Q1",
            "reference_corpus": "Economic policy corpus",
        },
    )
    print(f"Result: {result1}")
    print(f"Penalty: {metadata1['penalty']}")
    print()

    # Execute without critical optional (penalty applied)
    print("Example 2: Missing critical optional input")
    result2, metadata2 = executor.execute_method(
        method_id="coherence_validator",
        method_callable=coherence_validator,
        inputs={
            "extracted_text": "Policy text about economic development",
            "question_id": "D1-Q1",
            # Missing reference_corpus (critical optional)
        },
    )
    print(f"Result: {result2}")
    print(f"Penalty: {metadata2['penalty']}")
    print(f"Messages: {metadata2['validation_messages']}")
    print()

    # Get execution summary
    summary = executor.get_execution_summary()
    print("Execution Summary:")
    print(f"Total executions: {summary['total_executions']}")
    print(f"Failed validations: {summary['failed_validations']}")
    print(f"Average penalty: {summary['average_penalty']:.3f}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    example_usage()
