"""
Module: src.canonic_phases.phase_2.contracts.phase2_concurrency_determinism
Purpose: Enforce that parallel execution yields identical outputs to serial execution
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - ConcurrencyDeterminism: parallel(inputs, seed) == serial(inputs, seed)
    - OrderIndependence: Output set semantics preserved under reordering

Determinism:
    Seed-Strategy:  PARAMETERIZED — same seed required for verification
    State-Management: Capture output hashes for comparison

Inputs:
    - executor:  Executor — Executor under test
    - payloads: List[Payload] — Test payloads
    - seed:  int — Determinism seed

Outputs:
    - verification_result: ConcurrencyVerificationResult

Failure-Modes:
    - OutputMismatch: ConcurrencyContractViolation — Parallel != Serial
    - HashCollision: ConcurrencyContractViolation — Different content, same hash
"""
from __future__ import annotations

import hashlib
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Final, TypeVar

from ..constants.phase2_constants import DEFAULT_RANDOM_SEED, HASH_ALGORITHM

T = TypeVar("T")


# === DATA STRUCTURES ===


@dataclass(frozen=True)
class ExecutionSnapshot:
    """Immutable snapshot of execution outputs for comparison."""

    output_hashes: tuple[str, ...]
    total_outputs: int
    seed_used: int
    execution_mode: str  # "SERIAL" or "PARALLEL"

    def content_hash(self) -> str:
        """Compute aggregate hash for comparison."""
        combined = "|".join(sorted(self.output_hashes))
        return hashlib.new(HASH_ALGORITHM, combined.encode()).hexdigest()


@dataclass(frozen=True)
class ConcurrencyVerificationResult:
    """Result of concurrency determinism verification."""

    contract_satisfied: bool
    serial_snapshot: ExecutionSnapshot
    parallel_snapshot: ExecutionSnapshot
    mismatched_indices: tuple[int, ...] = field(default_factory=tuple)
    details: str = ""


# === EXCEPTION TAXONOMY ===


@dataclass(frozen=True)
class ConcurrencyContractViolation(Exception):
    """Raised when concurrency determinism contract is violated."""

    error_code: str
    contract_name: str
    serial_hash: str
    parallel_hash: str
    details: str

    def __str__(self) -> str:
        return (
            f"[{self.error_code}] CONCURRENCY_CONTRACT_VIOLATION: "
            f"Serial hash {self.serial_hash[:16]}... != "
            f"Parallel hash {self.parallel_hash[:16]}...  — {self.details}"
        )


# === CONTRACT ENFORCEMENT ===


class ConcurrencyDeterminismVerifier:
    """
    Verify that executor produces identical outputs in serial vs parallel execution.

    SUCCESS_CRITERIA:
        - hash(serial_outputs) == hash(parallel_outputs) under same seed
        - Output count identical
        - Per-output hashes match (order-independent comparison)

    FAILURE_MODES:
        - OutputCountMismatch: Different number of outputs
        - ContentMismatch: Same count but different content hashes
        - OrderDependence: Content depends on execution order

    TERMINATION_CONDITION:
        - Both serial and parallel execution complete
        - Comparison computed

    VERIFICATION_STRATEGY:
        - test_phase2_contracts_enforcement.py::test_concurrency_determinism
    """

    def __init__(
        self,
        max_workers: int = 4,
        seed: int = DEFAULT_RANDOM_SEED,
    ) -> None:
        self._max_workers = max_workers
        self._seed = seed

    def verify(
        self,
        executor_factory: Callable[[], Any],
        payloads: Sequence[Any],
        run_method: str = "run",
    ) -> ConcurrencyVerificationResult:
        """
        Execute payloads serially and in parallel, compare outputs.

        Args:
            executor_factory:  Callable that creates executor instance (for isolation)
            payloads:  Sequence of payloads to execute
            run_method: Name of executor method to call

        Returns:
            ConcurrencyVerificationResult with comparison details

        Raises:
            ConcurrencyContractViolation: If outputs differ
        """
        # Serial execution
        serial_snapshot = self._execute_serial(executor_factory, payloads, run_method)

        # Parallel execution
        parallel_snapshot = self._execute_parallel(executor_factory, payloads, run_method)

        # Compare snapshots
        return self._compare_snapshots(serial_snapshot, parallel_snapshot)

    def _execute_serial(
        self,
        executor_factory: Callable[[], Any],
        payloads: Sequence[Any],
        run_method: str,
    ) -> ExecutionSnapshot:
        """Execute payloads serially and capture output hashes."""
        executor = executor_factory()
        method = getattr(executor, run_method)

        output_hashes: list[str] = []
        for payload in payloads:
            result = method(payload)
            result_hash = self._hash_output(result)
            output_hashes.append(result_hash)

        return ExecutionSnapshot(
            output_hashes=tuple(output_hashes),
            total_outputs=len(output_hashes),
            seed_used=self._seed,
            execution_mode="SERIAL",
        )

    def _execute_parallel(
        self,
        executor_factory: Callable[[], Any],
        payloads: Sequence[Any],
        run_method: str,
    ) -> ExecutionSnapshot:
        """Execute payloads in parallel and capture output hashes."""

        def execute_one(payload: Any) -> str:
            executor = executor_factory()
            method = getattr(executor, run_method)
            result = method(payload)
            return self._hash_output(result)

        with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
            output_hashes = list(pool.map(execute_one, payloads))

        return ExecutionSnapshot(
            output_hashes=tuple(output_hashes),
            total_outputs=len(output_hashes),
            seed_used=self._seed,
            execution_mode="PARALLEL",
        )

    def _hash_output(self, output: Any) -> str:
        """Compute deterministic hash of output."""
        # Convert output to canonical string representation
        if hasattr(output, "content_hash"):
            return output.content_hash
        elif hasattr(output, "__dict__"):
            canonical = str(sorted(output.__dict__.items()))
        else:
            canonical = str(output)
        return hashlib.new(HASH_ALGORITHM, canonical.encode()).hexdigest()

    def _compare_snapshots(
        self,
        serial: ExecutionSnapshot,
        parallel: ExecutionSnapshot,
    ) -> ConcurrencyVerificationResult:
        """Compare serial and parallel execution snapshots."""
        # Check count
        if serial.total_outputs != parallel.total_outputs:
            raise ConcurrencyContractViolation(
                error_code="E2006",
                contract_name="ConcurrencyDeterminism",
                serial_hash=serial.content_hash(),
                parallel_hash=parallel.content_hash(),
                details=(
                    f"Output count mismatch: serial={serial.total_outputs}, "
                    f"parallel={parallel.total_outputs}"
                ),
            )

        # Check per-output hashes (order-independent via sorted comparison)
        serial_sorted = sorted(serial.output_hashes)
        parallel_sorted = sorted(parallel.output_hashes)

        mismatched: list[int] = []
        for i, (s, p) in enumerate(zip(serial_sorted, parallel_sorted, strict=True)):
            if s != p:
                mismatched.append(i)

        if mismatched:
            raise ConcurrencyContractViolation(
                error_code="E2006",
                contract_name="ConcurrencyDeterminism",
                serial_hash=serial.content_hash(),
                parallel_hash=parallel.content_hash(),
                details=f"Content mismatch at indices:  {mismatched}",
            )

        return ConcurrencyVerificationResult(
            contract_satisfied=True,
            serial_snapshot=serial,
            parallel_snapshot=parallel,
            mismatched_indices=(),
            details="Concurrency determinism verified",
        )
