"""Orchestrator utilities with contract validation on import.

PHASE_LABEL: Phase 2
PHASE_COMPONENT: Phase 2 Orchestration Utilities
PHASE_ROLE: Provides import interface for Phase 2 orchestration components
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# NEW: Evidence processing - REAL PATH: canonic_phases.Phase_two.evidence_nexus
# Replaces evidence_assembler, evidence_validator, evidence_registry
from canonic_phases.Phase_two.evidence_nexus import (
    EvidenceNexus,
    EvidenceGraph,
    EvidenceNode,
    process_evidence,
)

# NEW: Narrative synthesis - REAL PATH: canonic_phases.Phase_two.carver
from canonic_phases.Phase_two.carver import (
    DoctoralCarverSynthesizer,
    CarverAnswer,
)

# Executor config - REAL PATH: canonic_phases.Phase_two.executor_config
from canonic_phases.Phase_two.executor_config import ExecutorConfig

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
