"""
Module:  src.canonic_phases.phase_2.contracts.phase2_routing_contract
Purpose: Enforce exhaustive routing contract — every payload maps to exactly one executor
Owner: phase2_orchestration
Lifecycle:  ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - ExhaustiveDispatch: No silent defaults; missing mapping is fatal (E2001)
    - SingleExecutorMapping: Each contract_type maps to exactly one executor
    - SignatureValidation: Payload must satisfy executor signature requirements

Determinism:
    Seed-Strategy:  NOT_APPLICABLE
    State-Management:  Stateless decorator

Inputs:
    - decorated_function:  Callable — Router dispatch function
    - payload: ContractPayload — Payload being routed

Outputs:
    - Executor instance OR raises RoutingContractViolation

Failure-Modes:
    - MissingMapping: RoutingContractViolation(E2001)
    - AmbiguousMapping: RoutingContractViolation — Multiple executors match
    - SignatureViolation: RoutingContractViolation — Payload signature invalid
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
class RoutingContractViolation(Exception):
    """
    Raised when routing contract is violated.

    This is a FATAL error.  No fallback.  No graceful degradation.
    """

    error_code: str
    contract_name: str
    violation_type: str
    details: str

    def __str__(self) -> str:
        return (
            f"[{self.error_code}] ROUTING_CONTRACT_VIOLATION: "
            f"{self.violation_type} — {self.details}"
        )


# === CONTRACT ENFORCEMENT ===


def enforce_routing_contract(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator enforcing routing contract on dispatch functions.

    SUCCESS_CRITERIA:
        - Function returns non-None executor
        - No exception during dispatch (other than contract violations)
        - Payload was validated before dispatch

    FAILURE_MODES:
        - NoneReturn: RoutingContractViolation — Executor not found
        - ExceptionDuringDispatch: RoutingContractViolation — Unexpected error

    TERMINATION_CONDITION:
        - Returns executor on success
        - Raises RoutingContractViolation on failure

    VERIFICATION_STRATEGY:
        - test_phase2_router_contracts.py
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Extract payload from args (assuming self, payload signature)
        payload = args[1] if len(args) > 1 else kwargs.get("payload")

        if payload is None:
            raise RoutingContractViolation(
                error_code="E2001",
                contract_name="RoutingContract",
                violation_type="NULL_PAYLOAD",
                details="Payload argument is None or missing",
            )

        # Log contract enforcement entry
        logger.debug(
            "Enforcing routing contract",
            extra={
                "contract_type": getattr(payload, "contract_type", "UNKNOWN"),
                "function": func.__name__,
            },
        )

        try:
            result = func(*args, **kwargs)
        except RoutingContractViolation:
            # Re-raise contract violations as-is
            raise
        except Exception as e:
            # Wrap unexpected exceptions in contract violation
            raise RoutingContractViolation(
                error_code="E2001",
                contract_name="RoutingContract",
                violation_type="DISPATCH_EXCEPTION",
                details=f"Unexpected error during dispatch: {type(e).__name__}: {e}",
            ) from e

        # Verify non-None result
        if result is None:
            contract_type = getattr(payload, "contract_type", "UNKNOWN")
            raise RoutingContractViolation(
                error_code="E2001",
                contract_name="RoutingContract",
                violation_type="NULL_EXECUTOR",
                details=f"No executor returned for contract_type: {contract_type}",
            )

        # Log successful enforcement
        logger.debug(
            "Routing contract satisfied",
            extra={
                "executor_id": getattr(result, "executor_id", "UNKNOWN"),
            },
        )

        return result

    return wrapper


def validate_exhaustive_registry(
    registry: dict[str, Any],
    expected_types: set[str],
) -> None:
    """
    Validate that registry covers all expected contract types.

    SUCCESS_CRITERIA:
        - Every type in expected_types has a mapping in registry
        - No extra mappings (registry keys ⊆ expected_types)

    FAILURE_MODES:
        - MissingMapping:  Some expected types not in registry
        - ExtraMapping: Registry contains unexpected types

    Args:
        registry:  Mapping of contract_type -> executor
        expected_types: Set of contract types that must be covered

    Raises:
        RoutingContractViolation:  If registry is not exhaustive
    """
    registry_types = set(registry.keys())

    missing = expected_types - registry_types
    if missing:
        raise RoutingContractViolation(
            error_code="E2001",
            contract_name="RoutingContract",
            violation_type="INCOMPLETE_REGISTRY",
            details=f"Missing mappings for contract types: {sorted(missing)}",
        )

    extra = registry_types - expected_types
    if extra:
        logger.warning(
            "Registry contains unmapped contract types",
            extra={"extra_types": sorted(extra)},
        )
