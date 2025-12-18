"""
Tests for Phase 2 Argument Router contracts and exhaustive dispatch.

Run with: pytest tests/canonic_phases/phase_2/test_phase2_router_contracts.py -v
"""
from __future__ import annotations

import pytest
from typing import Dict, Type

from src.canonic_phases.phase_2.phase2_a_arg_router import (
    ArgRouter,
    ContractPayload,
    Executor,
    ExecutorResult,
    RoutingError,
    ValidationError,
    RegistryError,
)


# === TEST FIXTURES ===

class MockPayload:
    """Mock payload for testing."""
    
    def __init__(self, contract_type: str, chunk_id: str, valid: bool = True):
        self._contract_type = contract_type
        self._chunk_id = chunk_id
        self._valid = valid
    
    @property
    def contract_type(self) -> str:
        return self._contract_type
    
    @property
    def chunk_id(self) -> str:
        return self._chunk_id
    
    def validate(self) -> bool:
        return self._valid


class MockResult:
    """Mock executor result for testing."""
    
    def __init__(self, task_id: str, chunk_id: str, success: bool = True):
        self._task_id = task_id
        self._chunk_id = chunk_id
        self._success = success
    
    @property
    def task_id(self) -> str:
        return self._task_id
    
    @property
    def chunk_id(self) -> str:
        return self._chunk_id
    
    @property
    def success(self) -> bool:
        return self._success


class MockExecutor:
    """Mock executor for testing."""
    
    def __init__(self, executor_id: str = "test_executor"):
        self._executor_id = executor_id
    
    def run(self, payload: MockPayload) -> MockResult:
        return MockResult(
            task_id=f"task_{payload.chunk_id}",
            chunk_id=payload.chunk_id,
            success=True
        )
    
    @property
    def executor_id(self) -> str:
        return self._executor_id


@pytest.fixture
def valid_registry() -> Dict[str, Type[Executor]]:
    """Create a valid executor registry."""
    return {
        "specialized_contract": MockExecutor,
        "general_contract": MockExecutor,
    }


@pytest.fixture
def router(valid_registry: Dict[str, Type[Executor]]) -> ArgRouter:
    """Create a router with valid registry."""
    return ArgRouter(valid_registry)


# === TESTS ===

class TestRouterConstruction:
    """Test router construction and registry validation."""
    
    def test_construction_with_valid_registry(self, valid_registry: Dict[str, Type[Executor]]) -> None:
        """Router constructs successfully with valid registry."""
        router = ArgRouter(valid_registry)
        assert router is not None
    
    def test_construction_with_incomplete_registry(self) -> None:
        """Router raises RegistryError with incomplete registry."""
        incomplete_registry: Dict[str, Type[Executor]] = {
            "specialized_contract": MockExecutor,
            # Missing "general_contract"
        }
        
        with pytest.raises(RegistryError) as exc_info:
            ArgRouter(incomplete_registry)
        
        assert "incomplete" in str(exc_info.value).lower()
        assert "general_contract" in str(exc_info.value)


class TestRouting:
    """Test routing functionality."""
    
    def test_route_valid_payload_to_executor(self, router: ArgRouter) -> None:
        """Valid payload routes to correct executor."""
        payload = MockPayload("specialized_contract", "chunk_001")
        executor = router.route(payload)
        
        assert executor is not None
        assert hasattr(executor, "executor_id")
        assert isinstance(executor.executor_id, str)
    
    def test_route_unknown_contract_type(self, router: ArgRouter) -> None:
        """Unknown contract type raises RoutingError."""
        payload = MockPayload("unknown_contract", "chunk_001")
        
        with pytest.raises(RoutingError) as exc_info:
            router.route(payload)
        
        error = exc_info.value
        assert error.error_code == "E2001"
        assert error.contract_type == "unknown_contract"
        assert "unknown_contract" in error.message
    
    def test_route_invalid_payload(self, router: ArgRouter) -> None:
        """Invalid payload raises AssertionError from precondition."""
        payload = MockPayload("specialized_contract", "chunk_001", valid=False)
        
        with pytest.raises(AssertionError) as exc_info:
            router.route(payload)
        
        assert "precondition" in str(exc_info.value).lower()
    
    def test_exhaustive_dispatch_all_registry_types(self, router: ArgRouter) -> None:
        """All registered contract types can be routed."""
        contract_types = ["specialized_contract", "general_contract"]
        
        for contract_type in contract_types:
            payload = MockPayload(contract_type, f"chunk_{contract_type}")
            executor = router.route(payload)
            assert executor is not None
            assert executor.executor_id


class TestContractEnforcement:
    """Test contract enforcement on routing."""
    
    def test_routing_contract_enforced(self, router: ArgRouter) -> None:
        """Routing contract ensures executor has required properties."""
        payload = MockPayload("specialized_contract", "chunk_001")
        executor = router.route(payload)
        
        # Contract ensures executor_id exists and is valid
        assert hasattr(executor, "executor_id")
        assert isinstance(executor.executor_id, str)
        assert len(executor.executor_id) > 0


class TestErrorMessages:
    """Test error message quality and information."""
    
    def test_routing_error_contains_context(self, router: ArgRouter) -> None:
        """RoutingError contains full context for debugging."""
        payload = MockPayload("missing_type", "chunk_001")
        
        with pytest.raises(RoutingError) as exc_info:
            router.route(payload)
        
        error = exc_info.value
        assert error.error_code
        assert error.contract_type == "missing_type"
        assert error.message
        assert "missing_type" in str(error)


class TestStatelessness:
    """Test router statelessness."""
    
    def test_router_is_stateless(self, router: ArgRouter) -> None:
        """Multiple routing calls don't affect each other."""
        payload1 = MockPayload("specialized_contract", "chunk_001")
        payload2 = MockPayload("general_contract", "chunk_002")
        
        executor1 = router.route(payload1)
        executor2 = router.route(payload2)
        
        # Both succeed independently
        assert executor1 is not None
        assert executor2 is not None
        
        # Can route same payload again
        executor3 = router.route(payload1)
        assert executor3 is not None


# === INTEGRATION TESTS ===

class TestRouterIntegration:
    """Integration tests for router with realistic scenarios."""
    
    def test_route_multiple_payloads_in_sequence(self, router: ArgRouter) -> None:
        """Router handles multiple payloads in sequence."""
        payloads = [
            MockPayload("specialized_contract", f"chunk_{i:03d}")
            for i in range(10)
        ]
        
        executors = [router.route(p) for p in payloads]
        
        assert len(executors) == 10
        assert all(e is not None for e in executors)
        assert all(hasattr(e, "executor_id") for e in executors)
