"""
Canonical Phase Executors
=========================

Registry of canonical phase executors for the orchestration system.
"""

from __future__ import annotations

from typing import Any, Dict, Protocol

from farfan_pipeline.orchestration.orchestrator import PhaseID


class PhaseExecutor(Protocol):
    """Protocol for phase executors."""
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the phase."""
        ...
    
    def execute(self, data: Any) -> Any:
        """Execute the phase with given data."""
        ...
    
    def validate_output(self, result: Any) -> bool:
        """Validate output data from the phase."""
        ...


class StubPhaseExecutor:
    """Stub implementation of phase executor for testing."""
    
    def __init__(self, phase_id: PhaseID):
        self.phase_id = phase_id
    
    def validate_input(self, data: Any) -> bool:
        """Stub input validation."""
        return True
    
    def execute(self, data: Any) -> Any:
        """Stub execution."""
        return {"phase_id": self.phase_id.value, "status": "completed"}
    
    def validate_output(self, result: Any) -> bool:
        """Stub output validation."""
        return True


def build_canonical_phase_executors() -> Dict[PhaseID, PhaseExecutor]:
    """
    Build registry of canonical phase executors.
    
    Returns:
        Dictionary mapping PhaseID to executor instances.
    """
    return {
        PhaseID.PHASE_2: StubPhaseExecutor(PhaseID.PHASE_2),
        PhaseID.PHASE_3: StubPhaseExecutor(PhaseID.PHASE_3),
        PhaseID.PHASE_4: StubPhaseExecutor(PhaseID.PHASE_4),
        PhaseID.PHASE_5: StubPhaseExecutor(PhaseID.PHASE_5),
        PhaseID.PHASE_6: StubPhaseExecutor(PhaseID.PHASE_6),
        PhaseID.PHASE_7: StubPhaseExecutor(PhaseID.PHASE_7),
        PhaseID.PHASE_8: StubPhaseExecutor(PhaseID.PHASE_8),
        PhaseID.PHASE_9: StubPhaseExecutor(PhaseID.PHASE_9),
    }


__all__ = [
    "PhaseExecutor",
    "StubPhaseExecutor",
    "build_canonical_phase_executors",
]
