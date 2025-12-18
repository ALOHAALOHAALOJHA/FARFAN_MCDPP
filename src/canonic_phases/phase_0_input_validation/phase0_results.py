"""Phase 0 Result Contract

Defines the Phase0Result dataclass that encapsulates all Phase 0 outputs
and ensures handoff readiness to Phase 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Phase0Result:
    """Result of Phase 0 execution, ready for handoff to Phase 1.
    
    This immutable dataclass captures all validated inputs, runtime configuration,
    and execution state from Phase 0. All fields are required and validated through
    exit gates before construction.
    
    Attributes:
        runtime_config: Validated runtime configuration with mode and policies
        input_pdf_sha256: SHA-256 hash of the input policy document
        questionnaire_sha256: SHA-256 hash of the questionnaire definition
        seed_snapshot: Deterministic seed values applied to all RNGs
        boot_check_results: Results of all boot-time dependency checks
        gate_results: Results of all 7 mandatory exit gates
        artifacts_dir: Directory path for Phase 0 artifacts
        execution_id: Unique identifier for this pipeline execution
        claims: List of all claims made during Phase 0 for audit trail
    """
    
    runtime_config: Any
    input_pdf_sha256: str
    questionnaire_sha256: str
    seed_snapshot: dict[str, int]
    boot_check_results: dict[str, bool]
    gate_results: list[dict[str, Any]]
    artifacts_dir: Path
    execution_id: str
    claims: list[dict[str, Any]]
    
    def __post_init__(self) -> None:
        """Validate Phase0Result integrity after construction."""
        # Validate SHA-256 hashes
        if len(self.input_pdf_sha256) != 64:
            raise ValueError(f"Invalid PDF SHA-256 length: {len(self.input_pdf_sha256)}")
        if len(self.questionnaire_sha256) != 64:
            raise ValueError(
                f"Invalid questionnaire SHA-256 length: {len(self.questionnaire_sha256)}"
            )
        
        # Validate all exit gates passed
        if not all(gr.get("passed", False) for gr in self.gate_results):
            failed_gates = [gr.get("gate_name", "unknown") 
                          for gr in self.gate_results if not gr.get("passed", False)]
            raise ValueError(f"Phase 0 exit gates failed: {failed_gates}")
        
        # Validate execution ID is present
        if not self.execution_id:
            raise ValueError("Execution ID is required")
        
        # Validate artifacts directory exists
        if not self.artifacts_dir.exists():
            raise ValueError(f"Artifacts directory does not exist: {self.artifacts_dir}")
