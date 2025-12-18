"""Orchestrator utilities with contract validation on import."""

from __future__ import annotations

from typing import TYPE_CHECKING

# NEW: Evidence processing - REAL PATH: canonic_phases.Phase_two.phase2_h_evidence_nexus
# Replaces evidence_assembler, evidence_validator, evidence_registry
from canonic_phases.Phase_two.phase2_h_evidence_nexus import (
    EvidenceNexus,
    EvidenceGraph,
    EvidenceNode,
    process_evidence,
)

# NEW: Narrative synthesis - REAL PATH: canonic_phases.Phase_two.phase2_f_carver
from canonic_phases.Phase_two.phase2_f_carver import (
    DoctoralCarverSynthesizer,
    CarverAnswer,
)

# Executor config - REAL PATH: canonic_phases.Phase_two.phase2_i_executor_config
from canonic_phases.Phase_two.phase2_i_executor_config import ExecutorConfig

__all__ = [
    # NEW: Evidence processing (EvidenceNexus)
    "EvidenceNexus",
    "EvidenceGraph",
    "EvidenceNode",
    "process_evidence",
    # NEW: Narrative synthesis (Carver)
    "DoctoralCarverSynthesizer",
    "CarverAnswer",
    # Orchestration core
    "Orchestrator",
    "MethodExecutor",
    "Evidence",
    "AbortSignal",
    "AbortRequested",
    "ResourceLimits",
    "PhaseInstrumentation",
    "PhaseResult",
    "MicroQuestionRun",
    "ScoredMicroQuestion",
    "ExecutorConfig",
]
