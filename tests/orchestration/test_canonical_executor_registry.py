"""Tests for canonical phase executor registry."""

from farfan_pipeline.orchestration.canonical_executors import (
    build_canonical_phase_executors,
)
from farfan_pipeline.orchestration.orchestrator import PhaseID


def test_canonical_executor_registry_complete() -> None:
    executors = build_canonical_phase_executors()

    expected = {
        PhaseID.PHASE_2,
        PhaseID.PHASE_3,
        PhaseID.PHASE_4,
        PhaseID.PHASE_5,
        PhaseID.PHASE_6,
        PhaseID.PHASE_7,
        PhaseID.PHASE_8,
        PhaseID.PHASE_9,
    }

    assert set(executors.keys()) == expected

    for executor in executors.values():
        assert hasattr(executor, "validate_input")
        assert hasattr(executor, "execute")
        assert hasattr(executor, "validate_output")