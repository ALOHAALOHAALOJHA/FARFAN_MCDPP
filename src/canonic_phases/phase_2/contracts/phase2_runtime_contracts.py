"""
Module: src.canonic_phases.phase_2.contracts.phase2_runtime_contracts
Purpose: Design-by-Contract primitives for runtime enforcement
Owner: phase2_orchestration
Lifecycle:  ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - Precondition: Input validation before execution
    - Postcondition: Output validation after execution
    - Invariant: State consistency throughout execution

Determinism:
    Seed-Strategy: NOT_APPLICABLE
    State-Management: Stateless decorators

Inputs:
    - condition: Callable[[...], bool] — Predicate to check
    - message: str — Error message on violation

Outputs:
    - Decorated function with contract enforcement

Failure-Modes:
    - PreconditionViolation: RuntimeContractViolation — Input invalid
    - PostconditionViolation: RuntimeContractViolation — Output invalid
    - InvariantViolation: RuntimeContractViolation — State corrupted
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Final, ParamSpec, TypeVar

logger: Final = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


# === EXCEPTION TAXONOMY ===


@dataclass(frozen=True)
class RuntimeContractViolation(Exception):
    """Base exception for runtime contract violations."""

    error_code: str
    contract_type: str  # PRECONDITION, POSTCONDITION, INVARIANT
    function_name: str
    message: str

    def __str__(self) -> str:
        return (
            f"[{self.error_code}] {self.contract_type}_VIOLATION in "
            f"{self.function_name}: {self.message}"
        )


class PreconditionViolation(RuntimeContractViolation):
    """Raised when precondition fails."""

    pass


class PostconditionViolation(RuntimeContractViolation):
    """Raised when postcondition fails."""

    pass


class InvariantViolation(RuntimeContractViolation):
    """Raised when invariant fails."""

    pass


# === CONTRACT DECORATORS ===


def precondition(
    condition: Callable[..., bool],
    message: str,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator enforcing precondition on function inputs.

    SUCCESS_CRITERIA:
        - condition(*args, **kwargs) returns True

    FAILURE_MODES:
        - PreconditionViolation: condition returns False

    Args:
        condition: Predicate receiving same args as decorated function
        message: Error message on violation

    Returns:
        Decorated function with precondition enforcement
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if not condition(*args, **kwargs):
                raise PreconditionViolation(
                    error_code="E2007",
                    contract_type="PRECONDITION",
                    function_name=func.__qualname__,
                    message=message,
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def postcondition(
    condition: Callable[[R], bool],
    message: str,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator enforcing postcondition on function output.

    SUCCESS_CRITERIA:
        - condition(result) returns True

    FAILURE_MODES:
        - PostconditionViolation: condition returns False

    Args:
        condition: Predicate receiving function result
        message: Error message on violation

    Returns:
        Decorated function with postcondition enforcement
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            if not condition(result):
                raise PostconditionViolation(
                    error_code="E2007",
                    contract_type="POSTCONDITION",
                    function_name=func.__qualname__,
                    message=message,
                )
            return result

        return wrapper

    return decorator


def invariant(
    condition: Callable[[Any], bool],
    message: str,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator enforcing invariant on object state before and after execution.

    SUCCESS_CRITERIA:
        - condition(self) returns True before execution
        - condition(self) returns True after execution

    FAILURE_MODES:
        - InvariantViolation: condition returns False at any checkpoint

    Args:
        condition: Predicate receiving self (first argument)
        message: Error message on violation

    Returns:
        Decorated method with invariant enforcement
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Extract self (assumes method)
            if not args:
                raise RuntimeContractViolation(
                    error_code="E2007",
                    contract_type="INVARIANT",
                    function_name=func.__qualname__,
                    message="Invariant decorator requires method with self",
                )

            self_obj = args[0]

            # Check invariant before
            if not condition(self_obj):
                raise InvariantViolation(
                    error_code="E2007",
                    contract_type="INVARIANT_PRE",
                    function_name=func.__qualname__,
                    message=f"Invariant violated BEFORE execution: {message}",
                )

            result = func(*args, **kwargs)

            # Check invariant after
            if not condition(self_obj):
                raise InvariantViolation(
                    error_code="E2007",
                    contract_type="INVARIANT_POST",
                    function_name=func.__qualname__,
                    message=f"Invariant violated AFTER execution: {message}",
                )

            return result

        return wrapper

    return decorator


# === CONTRACT COMPOSITION ===


def contract(
    pre: Callable[..., bool] | None = None,
    pre_msg: str = "Precondition failed",
    post: Callable[[R], bool] | None = None,
    post_msg: str = "Postcondition failed",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Composite decorator applying both precondition and postcondition.

    Args:
        pre: Precondition predicate (optional)
        pre_msg: Precondition error message
        post: Postcondition predicate (optional)
        post_msg: Postcondition error message

    Returns:
        Decorated function with both contracts enforced
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        wrapped = func
        if post is not None:
            wrapped = postcondition(post, post_msg)(wrapped)
        if pre is not None:
            wrapped = precondition(pre, pre_msg)(wrapped)
        return wrapped

    return decorator
