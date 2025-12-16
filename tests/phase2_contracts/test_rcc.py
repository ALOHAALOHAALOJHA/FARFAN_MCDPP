"""
Test RC - Routing Contract
Verifies: A* path is bitwise identical for same inputs
Request routing rules guarantee
"""
import pytest
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cross_cutting_infrastructure.contractual.dura_lex.routing_contract import (
    RoutingContract,
    RoutingInput,
)


class TestRoutingContract:
    """RC: Deterministic routing with lexicographical tie-breaking."""

    @pytest.fixture
    def routing_input(self) -> RoutingInput:
        """Phase 2 routing input."""
        return RoutingInput(
            context_hash="abc123def456",
            theta={"model_version": "v3", "policy_areas": 10},
            sigma={"corpus_hash": "hash1", "index_hash": "hash2"},
            budgets={"compute": 1000.0, "memory": 2048.0},
            seed=42,
        )

    def test_rcc_001_deterministic_route(self, routing_input: RoutingInput) -> None:
        """RCC-001: Same inputs produce identical route."""
        route1 = RoutingContract.compute_route(routing_input)
        route2 = RoutingContract.compute_route(routing_input)
        assert route1 == route2

    def test_rcc_002_route_verification(self, routing_input: RoutingInput) -> None:
        """RCC-002: Route verification passes for correct route."""
        route = RoutingContract.compute_route(routing_input)
        assert RoutingContract.verify(routing_input, route)

    def test_rcc_003_route_verification_fails_invalid(
        self, routing_input: RoutingInput
    ) -> None:
        """RCC-003: Route verification fails for incorrect route."""
        invalid_route = ["invalid_step_1", "invalid_step_2"]
        assert not RoutingContract.verify(routing_input, invalid_route)

    def test_rcc_004_different_inputs_different_routes(self) -> None:
        """RCC-004: Different inputs produce different routes."""
        input1 = RoutingInput(
            context_hash="context_a",
            theta={"version": "1"},
            sigma={"state": "a"},
            budgets={"budget": 100.0},
            seed=42,
        )
        input2 = RoutingInput(
            context_hash="context_b",
            theta={"version": "2"},
            sigma={"state": "b"},
            budgets={"budget": 200.0},
            seed=42,
        )
        route1 = RoutingContract.compute_route(input1)
        route2 = RoutingContract.compute_route(input2)
        assert route1 != route2

    def test_rcc_005_lexicographical_ordering(
        self, routing_input: RoutingInput
    ) -> None:
        """RCC-005: Route steps are lexicographically sorted."""
        route = RoutingContract.compute_route(routing_input)
        assert route == sorted(route)

    def test_rcc_006_route_is_list_of_strings(
        self, routing_input: RoutingInput
    ) -> None:
        """RCC-006: Route is a list of step IDs (strings)."""
        route = RoutingContract.compute_route(routing_input)
        assert isinstance(route, list)
        assert all(isinstance(step, str) for step in route)

    def test_rcc_007_input_serialization(self, routing_input: RoutingInput) -> None:
        """RCC-007: RoutingInput serializes deterministically."""
        bytes1 = routing_input.to_bytes()
        bytes2 = routing_input.to_bytes()
        assert bytes1 == bytes2

    def test_rcc_008_phase2_executor_routing(self) -> None:
        """RCC-008: Phase 2 executor routing is deterministic."""
        phase2_input = RoutingInput(
            context_hash="phase2_document_hash",
            theta={
                "executors": 30,
                "questions": 300,
                "policy_areas": 10,
                "dimensions": 6,
            },
            sigma={
                "questionnaire_hash": "monolith_hash",
                "signal_registry_hash": "sisas_hash",
            },
            budgets={"max_tasks": 300.0, "timeout_ms": 30000.0},
            seed=12345,
        )
        route1 = RoutingContract.compute_route(phase2_input)
        route2 = RoutingContract.compute_route(phase2_input)
        assert route1 == route2
        assert len(route1) == 5  # Default 5 steps in simulation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
