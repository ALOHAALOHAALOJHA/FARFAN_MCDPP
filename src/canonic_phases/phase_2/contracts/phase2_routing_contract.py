"""
Module: src.canonic_phases.phase_2.contracts.phase2_routing_contract
Purpose: Routing contract enforcement for Phase 2
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18
"""
from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def enforce_routing_contract[F: Callable[..., Any]](func: F) -> F:
    """
    Decorator to enforce routing contracts.

    Ensures that:
    1. The payload is valid before routing
    2. An executor is returned
    3. The executor has a valid executor_id

    Args:
        func: The routing function to decorate

    Returns:
        Decorated function with contract enforcement

    Raises:
        AssertionError: If routing contract is violated
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Execute the routing function
        result = func(*args, **kwargs)

        # Verify executor has required properties
        if not hasattr(result, "executor_id"):
            raise AssertionError(
                "Routing contract violated: executor must have executor_id property"
            )

        executor_id = result.executor_id
        if not isinstance(executor_id, str) or not executor_id:
            raise AssertionError(
                f"Routing contract violated: executor_id must be non-empty string, got {executor_id!r}"
            )

        return result

    return wrapper  # type: ignore
