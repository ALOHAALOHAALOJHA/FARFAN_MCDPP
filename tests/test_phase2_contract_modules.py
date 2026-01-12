"""
Tests for Phase 2 Contract Modules

These tests verify the basic functionality of the contract enforcement mechanisms:
- Routing Contract
- Concurrency Determinism
- Runtime Contracts (precondition, postcondition, invariant)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add src to path for imports

from farfan_pipeline.phases.phase_2.contracts import (
    ConcurrencyContractViolation,
    ConcurrencyDeterminismVerifier,
    InvariantViolation,
    PostconditionViolation,
    PreconditionViolation,
    RoutingContractViolation,
    contract,
    enforce_routing_contract,
    invariant,
    postcondition,
    precondition,
    validate_exhaustive_registry,
)


class TestRoutingContract:
    """Tests for routing contract enforcement."""

    def test_enforce_routing_contract_success(self) -> None:
        """Test that valid routing passes contract."""

        @enforce_routing_contract
        def mock_router(self: object, payload: dict[str, str]) -> str:
            return "executor_instance"

        result = mock_router(None, {"contract_type": "test"})
        assert result == "executor_instance"

    def test_enforce_routing_contract_null_payload(self) -> None:
        """Test that None payload raises RoutingContractViolation."""

        @enforce_routing_contract
        def mock_router(self: object, payload: dict[str, str] | None) -> str:
            return "executor"

        with pytest.raises(RoutingContractViolation) as exc_info:
            mock_router(None, None)

        assert exc_info.value.error_code == "E2001"
        assert "NULL_PAYLOAD" in exc_info.value.violation_type

    def test_enforce_routing_contract_null_executor(self) -> None:
        """Test that None return raises RoutingContractViolation."""

        @enforce_routing_contract
        def mock_router(self: object, payload: dict[str, str]) -> str | None:
            return None

        with pytest.raises(RoutingContractViolation) as exc_info:
            mock_router(None, {"contract_type": "test"})

        assert exc_info.value.error_code == "E2001"
        assert "NULL_EXECUTOR" in exc_info.value.violation_type

    def test_validate_exhaustive_registry_success(self) -> None:
        """Test that complete registry passes validation."""
        registry = {"type_a": "executor_a", "type_b": "executor_b"}
        expected = {"type_a", "type_b"}

        validate_exhaustive_registry(registry, expected)

    def test_validate_exhaustive_registry_missing_types(self) -> None:
        """Test that incomplete registry raises RoutingContractViolation."""
        registry = {"type_a": "executor_a"}
        expected = {"type_a", "type_b", "type_c"}

        with pytest.raises(RoutingContractViolation) as exc_info:
            validate_exhaustive_registry(registry, expected)

        assert exc_info.value.error_code == "E2001"
        assert "INCOMPLETE_REGISTRY" in exc_info.value.violation_type


class TestRuntimeContracts:
    """Tests for precondition, postcondition, and invariant decorators."""

    def test_precondition_success(self) -> None:
        """Test that valid input passes precondition."""

        @precondition(lambda x: x > 0, "Input must be positive")
        def process(x: int) -> int:
            return x * 2

        result = process(5)
        assert result == 10

    def test_precondition_failure(self) -> None:
        """Test that invalid input raises PreconditionViolation."""

        @precondition(lambda x: x > 0, "Input must be positive")
        def process(x: int) -> int:
            return x * 2

        with pytest.raises(PreconditionViolation) as exc_info:
            process(-5)

        assert exc_info.value.error_code == "E2007"
        assert "Input must be positive" in exc_info.value.message

    def test_postcondition_success(self) -> None:
        """Test that valid output passes postcondition."""

        @postcondition(lambda result: result > 0, "Result must be positive")
        def process(x: int) -> int:
            return abs(x)

        result = process(-5)
        assert result == 5

    def test_postcondition_failure(self) -> None:
        """Test that invalid output raises PostconditionViolation."""

        @postcondition(lambda result: result > 0, "Result must be positive")
        def process(x: int) -> int:
            return x

        with pytest.raises(PostconditionViolation) as exc_info:
            process(-5)

        assert exc_info.value.error_code == "E2007"
        assert "Result must be positive" in exc_info.value.message

    def test_invariant_success(self) -> None:
        """Test that state invariant is maintained."""

        class Counter:
            def __init__(self) -> None:
                self.value = 0

            @invariant(lambda self: self.value >= 0, "Value must be non-negative")
            def increment(self) -> None:
                self.value += 1

        counter = Counter()
        counter.increment()
        assert counter.value == 1

    def test_invariant_failure_post(self) -> None:
        """Test that invariant violation after execution raises InvariantViolation."""

        class Counter:
            def __init__(self) -> None:
                self.value = 0

            @invariant(lambda self: self.value >= 0, "Value must be non-negative")
            def decrement(self) -> None:
                self.value -= 1

        counter = Counter()
        with pytest.raises(InvariantViolation) as exc_info:
            counter.decrement()

        assert exc_info.value.error_code == "E2007"
        assert "INVARIANT_POST" in exc_info.value.contract_type

    def test_contract_composition(self) -> None:
        """Test that composite contract decorator works."""

        @contract(
            pre=lambda x: x > 0,
            pre_msg="Input must be positive",
            post=lambda result: result > 0,
            post_msg="Result must be positive",
        )
        def process(x: int) -> int:
            return x * 2

        result = process(5)
        assert result == 10


class TestConcurrencyDeterminism:
    """Tests for concurrency determinism verification."""

    def test_concurrency_determinism_success(self) -> None:
        """Test that deterministic executor passes concurrency check."""

        class DeterministicExecutor:
            def run(self, payload: dict[str, int]) -> dict[str, int]:
                return {"result": payload["value"] * 2}

        verifier = ConcurrencyDeterminismVerifier(max_workers=2, seed=42)
        payloads = [{"value": i} for i in range(5)]

        result = verifier.verify(
            executor_factory=DeterministicExecutor, payloads=payloads, run_method="run"
        )

        assert result.contract_satisfied
        assert result.serial_snapshot.total_outputs == 5
        assert result.parallel_snapshot.total_outputs == 5

    def test_concurrency_determinism_failure(self) -> None:
        """Test that non-deterministic executor fails concurrency check."""
        import random

        class NonDeterministicExecutor:
            def run(self, payload: dict[str, int]) -> dict[str, float]:
                return {"result": payload["value"] * random.random()}

        verifier = ConcurrencyDeterminismVerifier(max_workers=2, seed=42)
        payloads = [{"value": i} for i in range(5)]

        with pytest.raises(ConcurrencyContractViolation) as exc_info:
            verifier.verify(
                executor_factory=NonDeterministicExecutor,
                payloads=payloads,
                run_method="run",
            )

        assert exc_info.value.error_code == "E2006"
