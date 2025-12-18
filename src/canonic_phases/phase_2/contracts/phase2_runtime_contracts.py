"""
Module: src.canonic_phases.phase_2.contracts.phase2_runtime_contracts
Purpose: Runtime contract decorators for preconditions, postconditions, and invariants
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


def precondition(check: Callable[..., bool], message: str) -> Callable[[F], F]:
    """
    Decorator to enforce preconditions on function execution.

    Args:
        check: Function that takes the same arguments as the decorated function
               and returns True if precondition is satisfied
        message: Error message to display if precondition fails

    Returns:
        Decorated function that validates preconditions

    Raises:
        AssertionError: If precondition check fails
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not check(*args, **kwargs):
                raise AssertionError(f"Precondition failed: {message}")
            return func(*args, **kwargs)
        return wrapper  # type: ignore
    return decorator


def postcondition(check: Callable[[Any], bool], message: str) -> Callable[[F], F]:
    """
    Decorator to enforce postconditions on function execution.

    Args:
        check: Function that takes the result of the decorated function
               and returns True if postcondition is satisfied
        message: Error message to display if postcondition fails

    Returns:
        Decorated function that validates postconditions

    Raises:
        AssertionError: If postcondition check fails
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            if not check(result):
                raise AssertionError(f"Postcondition failed: {message}")
            return result
        return wrapper  # type: ignore
    return decorator


def invariant(check: Callable[..., bool], message: str) -> Callable[[F], F]:
    """
    Decorator to enforce invariants on class methods.

    Args:
        check: Function that takes self and returns True if invariant holds
        message: Error message to display if invariant fails

    Returns:
        Decorated method that validates invariants before and after execution

    Raises:
        AssertionError: If invariant check fails
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            if not check(self):
                raise AssertionError(f"Invariant failed (before): {message}")
            result = func(self, *args, **kwargs)
            if not check(self):
                raise AssertionError(f"Invariant failed (after): {message}")
            return result
        return wrapper  # type: ignore
    return decorator
