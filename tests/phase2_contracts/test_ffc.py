"""
Test FFC - Failure Fallback Contract
Verifies: Typed errors trigger deterministic fallbacks
Graceful degradation guarantee
"""

import pytest
from pathlib import Path
from typing import Any

from cross_cutting_infrastructure.contractual.dura_lex.failure_fallback import (
    FailureFallbackContract,
)


class Phase2ExecutionError(Exception):
    """Phase 2 executor failure."""

    pass


class Phase2TimeoutError(Exception):
    """Phase 2 timeout failure."""

    pass


class TestFailureFallbackContract:
    """FFC: Deterministic fallback on failures."""

    def test_ffc_001_fallback_on_expected_exception(self) -> None:
        """FFC-001: Expected exception triggers fallback."""

        def failing_executor() -> dict[str, Any]:
            raise Phase2ExecutionError("Executor failed")

        fallback = {"status": "fallback", "score": 0.0, "evidence": []}
        result = FailureFallbackContract.execute_with_fallback(
            failing_executor, fallback, (Phase2ExecutionError,)
        )
        assert result == fallback

    def test_ffc_002_success_returns_result(self) -> None:
        """FFC-002: Successful execution returns actual result."""

        def working_executor() -> dict[str, Any]:
            return {"status": "success", "score": 0.85}

        fallback = {"status": "fallback"}
        result = FailureFallbackContract.execute_with_fallback(
            working_executor, fallback, (Phase2ExecutionError,)
        )
        assert result["status"] == "success"
        assert result["score"] == 0.85

    def test_ffc_003_unexpected_exception_propagates(self) -> None:
        """FFC-003: Unexpected exception propagates (not caught)."""

        def unexpected_failure() -> dict[str, Any]:
            raise ValueError("Unexpected error")

        fallback = {"status": "fallback"}
        with pytest.raises(ValueError, match="Unexpected error"):
            FailureFallbackContract.execute_with_fallback(
                unexpected_failure, fallback, (Phase2ExecutionError,)
            )

    def test_ffc_004_fallback_determinism(self) -> None:
        """FFC-004: Repeated failures produce identical fallbacks."""

        def always_fails() -> dict[str, Any]:
            raise Phase2ExecutionError("Always fails")

        fallback = {"status": "fallback", "error_code": "E001"}
        assert FailureFallbackContract.verify_fallback_determinism(
            always_fails, fallback, Phase2ExecutionError
        )

    def test_ffc_005_multiple_exception_types(self) -> None:
        """FFC-005: Multiple exception types handled."""

        def timeout_failure() -> dict[str, Any]:
            raise Phase2TimeoutError("Timeout")

        fallback = {"status": "timeout_fallback"}
        result = FailureFallbackContract.execute_with_fallback(
            timeout_failure, fallback, (Phase2ExecutionError, Phase2TimeoutError)
        )
        assert result == fallback

    def test_ffc_006_phase2_executor_fallback(self) -> None:
        """FFC-006: Phase 2 executor uses structured fallback."""

        def phase2_executor_stub() -> dict[str, Any]:
            raise Phase2ExecutionError("Contract violation: missing signal_pack")

        fallback_evidence = {
            "question_id": "Q001",
            "base_slot": "D1-Q1",
            "status": "fallback",
            "evidence": {"elements": [], "fallback_reason": "executor_failure"},
            "score": 0.0,
            "validation": {"passed": False, "errors": ["fallback_triggered"]},
        }
        result = FailureFallbackContract.execute_with_fallback(
            phase2_executor_stub, fallback_evidence, (Phase2ExecutionError,)
        )
        assert result["status"] == "fallback"
        assert result["score"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
