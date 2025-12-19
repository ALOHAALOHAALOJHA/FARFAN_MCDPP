"""
Module: src.canonic_phases.phase_2.phase2_a_arg_router
Purpose: Route contract payloads to appropriate executors with exhaustive dispatch
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18
Python-Version: 3.12+ (uses PEP 695 generic syntax)

Contracts-Enforced:
    - RoutingContract: Every contract type maps to exactly one executor
    - ExhaustiveDispatch: No silent defaults; missing mapping is fatal
    - SignatureValidation: Payload signature verified before dispatch

Determinism:
    Seed-Strategy: NOT_APPLICABLE (deterministic dispatch)
    State-Management: Stateless router; no mutable state

Inputs:
    - payload: ContractPayload — Typed payload with contract_type field
    - registry: ExecutorRegistry — Mapping of contract types to executors

Outputs:
    - executor: Executor — Selected executor instance
    - OR raises RoutingError with E2001

Failure-Modes:
    - MissingMapping: RoutingError(E2001) — No executor for contract type
    - SignatureViolation: ValidationError — Payload fails signature check
    - RegistryCorruption: RegistryError — Registry state invalid
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final, NoReturn, Protocol, TypeVar

from .constants.phase2_constants import ERROR_CODES, EXECUTOR_REGISTRY
from .contracts.phase2_routing_contract import enforce_routing_contract
from .contracts.phase2_runtime_contracts import postcondition, precondition

logger: Final = logging.getLogger(__name__)

# === TYPE DEFINITIONS ===

PayloadT = TypeVar("PayloadT", bound="ContractPayload")
ResultT = TypeVar("ResultT", bound="ExecutorResult")


class ContractPayload(Protocol):
    """Protocol defining contract payload interface."""

    @property
    def contract_type(self) -> str:
        """Return the contract type identifier."""
        ...

    @property
    def chunk_id(self) -> str:
        """Return the originating chunk identifier."""
        ...

    def validate(self) -> bool:
        """Validate payload integrity."""
        ...


class ExecutorResult(Protocol):
    """Protocol defining executor result interface."""

    @property
    def task_id(self) -> str:
        """Return the task identifier."""
        ...

    @property
    def chunk_id(self) -> str:
        """Return the originating chunk identifier."""
        ...

    @property
    def success(self) -> bool:
        """Return execution success status."""
        ...


class Executor(Protocol[PayloadT, ResultT]):
    """Protocol defining executor interface."""

    def run(self, payload: PayloadT) -> ResultT:
        """Execute the payload and return result."""
        ...

    @property
    def executor_id(self) -> str:
        """Return the executor identifier."""
        ...


# === EXCEPTION TAXONOMY ===

@dataclass
class RoutingError(Exception):
    """Raised when routing fails."""
    error_code: str
    contract_type: str
    message: str

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


@dataclass
class ValidationError(Exception):
    """Raised when validation fails."""
    error_code: str
    details: str


class RegistryError(Exception):
    """Raised when executor registry is invalid."""
    pass


# === ROUTER IMPLEMENTATION ===

class ArgRouter[PayloadT: "ContractPayload", ResultT: "ExecutorResult"]:
    """
    Route contract payloads to executors with exhaustive dispatch.

    SUCCESS_CRITERIA:
        - Every valid contract_type routes to exactly one executor
        - Invalid contract_type raises RoutingError(E2001)
        - Payload validation occurs before dispatch

    FAILURE_MODES:
        - MissingMapping: RoutingError(E2001)
        - ValidationFailure: ValidationError

    TERMINATION_CONDITION:
        - Returns Executor on success
        - Raises exception on failure

    VERIFICATION_STRATEGY:
        - test_phase2_router_contracts.py exhaustive dispatch tests
    """

    def __init__(
        self,
        executor_registry: dict[str, type[Executor[PayloadT, ResultT]]],
    ) -> None:
        """
        Initialize router with executor registry.

        Args:
            executor_registry: Mapping of contract_type -> Executor class
        """
        self._registry: Final = executor_registry
        self._validate_registry()

    def _validate_registry(self) -> None:
        """Validate registry completeness at construction time."""
        # Verify all expected contract types have mappings
        expected_flat = set()
        for entry in EXECUTOR_REGISTRY.values():
            expected_flat.update(entry.contract_types)

        missing = expected_flat - set(self._registry.keys())
        if missing:
            raise RegistryError(
                f"Registry incomplete. Missing mappings for: {missing}"
            )

    @precondition(lambda self, payload: payload.validate(), "Payload must be valid")
    @postcondition(lambda result: result is not None, "Must return executor")
    @enforce_routing_contract
    def route(self, payload: PayloadT) -> Executor[PayloadT, ResultT]:
        """
        Route payload to appropriate executor.

        Args:
            payload: Contract payload to route

        Returns:
            Executor instance for the payload's contract type

        Raises:
            RoutingError: If no mapping exists for contract_type
            ValidationError: If payload validation fails
        """
        contract_type = payload.contract_type

        logger.info(
            "Routing payload",
            extra={
                "contract_type": contract_type,
                "chunk_id": payload.chunk_id,
            }
        )

        executor_class = self._registry.get(contract_type)

        if executor_class is None:
            self._raise_missing_mapping(contract_type)

        return executor_class()

    def _raise_missing_mapping(self, contract_type: str) -> NoReturn:
        """Raise RoutingError for missing mapping."""
        error = ERROR_CODES["E2001"]
        raise RoutingError(
            error_code=error.code,
            contract_type=contract_type,
            message=error.message_template.format(contract_type=contract_type),
        )
