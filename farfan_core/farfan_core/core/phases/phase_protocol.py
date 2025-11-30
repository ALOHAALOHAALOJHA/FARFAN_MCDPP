"""
Phase Contract Protocol - Constitutional Constraint System
===========================================================

This module implements the constitutional constraint framework where each phase:

1. Has an EXPLICIT input contract (typed, validated)
2. Has an EXPLICIT output contract (typed, validated)
3. Communicates ONLY through these contracts (no side channels)
4. Is enforced by validators (runtime contract checking)
5. Is tracked in the verification manifest (full traceability)

Design Principles:
------------------
- **Single Entry Point**: Each phase accepts exactly ONE input type
- **Single Exit Point**: Each phase produces exactly ONE output type
- **No Bypass**: The orchestrator enforces sequential execution
- **Verifiable**: All contracts are validated and logged
- **Deterministic**: Same input → same output (modulo controlled randomness)

Phase Structure:
----------------
phase0_input_validation:
    Input: Phase0Input (raw PDF path + run_id)
    Output: CanonicalInput (validated, hashed, ready)

phase1_spc_ingestion:
    Input: CanonicalInput
    Output: CanonPolicyPackage (60 chunks, PA×DIM structured)

phase1_to_phase2_adapter:
    Input: CanonPolicyPackage
    Output: PreprocessedDocument (chunked mode)

phase2_microquestions:
    Input: PreprocessedDocument
    Output: Phase2Result (305 questions answered)

Author: F.A.R.F.A.N Architecture Team
Date: 2025-01-19
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, ValidationError

# Type variables for generic phase contracts
TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


@dataclass
class PhaseInvariant:
    """An invariant that must hold for a phase."""

    name: str
    description: str
    check: callable  # Function that returns bool
    error_message: str


@dataclass
class PhaseMetadata:
    """Metadata for a phase execution."""

    phase_name: str
    started_at: str
    finished_at: str | None = None
    duration_ms: float | None = None
    success: bool = False
    error: str | None = None


@dataclass
class ContractValidationResult:
    """Result of validating a contract."""

    passed: bool
    contract_type: str  # "input" or "output"
    phase_name: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validation_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class PhaseContract(ABC, Generic[TInput, TOutput]):
    """
    Abstract base class for phase contracts.

    Each phase must implement:
    1. Input contract validation
    2. Output contract validation
    3. Invariant checking
    4. Phase execution logic

    This enforces the constitutional constraint that phases communicate
    ONLY through validated contracts.
    """

    def __init__(self, phase_name: str):
        """
        Initialize phase contract.

        Args:
            phase_name: Canonical name of the phase (e.g., "phase0_input_validation")
        """
        self.phase_name = phase_name
        self.invariants: list[PhaseInvariant] = []
        self.metadata: PhaseMetadata | None = None

    @abstractmethod
    def validate_input(self, input_data: Any) -> ContractValidationResult:
        """
        Validate input contract.

        Args:
            input_data: Input to validate

        Returns:
            ContractValidationResult with validation status
        """
        pass

    @abstractmethod
    def validate_output(self, output_data: Any) -> ContractValidationResult:
        """
        Validate output contract.

        Args:
            output_data: Output to validate

        Returns:
            ContractValidationResult with validation status
        """
        pass

    @abstractmethod
    async def execute(self, input_data: TInput) -> TOutput:
        """
        Execute the phase logic.

        Args:
            input_data: Validated input conforming to input contract

        Returns:
            Output conforming to output contract

        Raises:
            ValueError: If input contract validation fails
            RuntimeError: If phase execution fails
        """
        pass

    def add_invariant(
        self,
        name: str,
        description: str,
        check: callable,
        error_message: str,
    ) -> None:
        """
        Add an invariant to this phase.

        Args:
            name: Invariant name
            description: Human-readable description
            check: Function that returns bool (True = invariant holds)
            error_message: Error message if invariant fails
        """
        self.invariants.append(
            PhaseInvariant(
                name=name,
                description=description,
                check=check,
                error_message=error_message,
            )
        )

    def check_invariants(self, data: Any) -> tuple[bool, list[str]]:
        """
        Check all invariants for this phase.

        Args:
            data: Data to check invariants against

        Returns:
            Tuple of (all_passed, failed_invariant_messages)
        """
        failed_messages = []
        for inv in self.invariants:
            try:
                if not inv.check(data):
                    failed_messages.append(f"{inv.name}: {inv.error_message}")
            except Exception as e:
                failed_messages.append(f"{inv.name}: Exception during check: {e}")

        return len(failed_messages) == 0, failed_messages

    async def run(self, input_data: TInput) -> tuple[TOutput, PhaseMetadata]:
        """
        Run the complete phase with validation and invariant checking.

        This is the ONLY way to execute a phase - it enforces:
        1. Input validation
        2. Invariant checking (pre-execution if applicable)
        3. Phase execution
        4. Output validation
        5. Invariant checking (post-execution)
        6. Metadata recording

        Args:
            input_data: Input to the phase

        Returns:
            Tuple of (output_data, phase_metadata)

        Raises:
            ValueError: If contract validation fails
            RuntimeError: If invariants fail or execution fails
        """
        started_at = datetime.now(timezone.utc)
        metadata = PhaseMetadata(
            phase_name=self.phase_name,
            started_at=started_at.isoformat(),
        )

        try:
            # 1. Validate input contract
            input_validation = self.validate_input(input_data)
            if not input_validation.passed:
                error_msg = f"Input contract validation failed: {input_validation.errors}"
                metadata.error = error_msg
                metadata.success = False
                raise ValueError(error_msg)

            # 2. Execute phase
            output_data = await self.execute(input_data)

            # 3. Validate output contract
            output_validation = self.validate_output(output_data)
            if not output_validation.passed:
                error_msg = f"Output contract validation failed: {output_validation.errors}"
                metadata.error = error_msg
                metadata.success = False
                raise ValueError(error_msg)

            # 4. Check invariants
            invariants_passed, failed_invariants = self.check_invariants(output_data)
            if not invariants_passed:
                error_msg = f"Phase invariants failed: {failed_invariants}"
                metadata.error = error_msg
                metadata.success = False
                raise RuntimeError(error_msg)

            # Success
            metadata.success = True
            return output_data, metadata

        except Exception as e:
            metadata.error = str(e)
            metadata.success = False
            raise

        finally:
            finished_at = datetime.now(timezone.utc)
            metadata.finished_at = finished_at.isoformat()
            metadata.duration_ms = (
                finished_at - started_at
            ).total_seconds() * 1000
            self.metadata = metadata


@dataclass
class PhaseArtifact:
    """An artifact produced by a phase."""

    artifact_name: str
    artifact_path: Path
    sha256: str
    size_bytes: int
    created_at: str


class PhaseManifestBuilder:
    """
    Builds the phase-explicit section of the verification manifest.

    Each phase execution is recorded with:
    - Input/output contract hashes
    - Invariants checked
    - Artifacts produced
    - Timing information
    """

    def __init__(self):
        """Initialize manifest builder."""
        self.phases: dict[str, dict[str, Any]] = {}

    def record_phase(
        self,
        phase_name: str,
        metadata: PhaseMetadata,
        input_validation: ContractValidationResult,
        output_validation: ContractValidationResult,
        invariants_checked: list[str],
        artifacts: list[PhaseArtifact],
    ) -> None:
        """
        Record a phase execution in the manifest.

        Args:
            phase_name: Name of the phase
            metadata: Phase execution metadata
            input_validation: Input contract validation result
            output_validation: Output contract validation result
            invariants_checked: List of invariant names that were checked
            artifacts: List of artifacts produced by this phase
        """
        self.phases[phase_name] = {
            "status": "success" if metadata.success else "failed",
            "started_at": metadata.started_at,
            "finished_at": metadata.finished_at,
            "duration_ms": metadata.duration_ms,
            "input_contract": {
                "validation_passed": input_validation.passed,
                "errors": input_validation.errors,
                "warnings": input_validation.warnings,
            },
            "output_contract": {
                "validation_passed": output_validation.passed,
                "errors": output_validation.errors,
                "warnings": output_validation.warnings,
            },
            "invariants_checked": invariants_checked,
            "invariants_satisfied": metadata.success,
            "artifacts": [
                {
                    "name": a.artifact_name,
                    "path": str(a.artifact_path),
                    "sha256": a.sha256,
                    "size_bytes": a.size_bytes,
                }
                for a in artifacts
            ],
            "error": metadata.error,
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Convert manifest to dictionary.

        Returns:
            Dictionary representation of the phase manifest
        """
        return {
            "phases": self.phases,
            "total_phases": len(self.phases),
            "successful_phases": sum(
                1 for p in self.phases.values() if p["status"] == "success"
            ),
            "failed_phases": sum(
                1 for p in self.phases.values() if p["status"] == "failed"
            ),
        }

    def save(self, output_path: Path) -> None:
        """
        Save manifest to JSON file.

        Args:
            output_path: Path to save manifest
        """
        with open(output_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


def compute_contract_hash(contract_data: Any) -> str:
    """
    Compute SHA256 hash of a contract's data.

    Args:
        contract_data: Contract data (dict, dataclass, or Pydantic model)

    Returns:
        Hex-encoded SHA256 hash
    """
    # Convert to dict if needed
    if hasattr(contract_data, "dict"):
        # Pydantic model
        data_dict = contract_data.dict()
    elif hasattr(contract_data, "__dataclass_fields__"):
        # Dataclass
        data_dict = asdict(contract_data)
    elif isinstance(contract_data, dict):
        data_dict = contract_data
    else:
        raise TypeError(f"Cannot hash contract data of type {type(contract_data)}")

    # Serialize to JSON with sorted keys for determinism
    json_str = json.dumps(data_dict, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


__all__ = [
    "PhaseContract",
    "PhaseInvariant",
    "PhaseMetadata",
    "ContractValidationResult",
    "PhaseArtifact",
    "PhaseManifestBuilder",
    "compute_contract_hash",
]
