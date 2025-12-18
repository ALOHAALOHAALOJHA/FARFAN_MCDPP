"""
Module: src.canonic_phases.phase_2.contracts.phase2_runtime_contracts
Purpose: Runtime contract decorators for Phase 2
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18
"""
from __future__ import annotations

from typing import Callable, Any, TypeVar
from functools import wraps

T = TypeVar("T")


def precondition(check: Callable[..., bool], message: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to enforce preconditions on function execution.
    
    Args:
        check: Function that returns True if precondition is met
        message: Error message to display if precondition fails
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if not check(*args, **kwargs):
                raise AssertionError(f"Precondition failed: {message}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def postcondition(check: Callable[[T], bool], message: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to enforce postconditions on function execution.
    
    Args:
        check: Function that returns True if postcondition is met
        message: Error message to display if postcondition fails
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result = func(*args, **kwargs)
            if not check(result):
                raise AssertionError(f"Postcondition failed: {message}")
            return result
        return wrapper
    return decorator
