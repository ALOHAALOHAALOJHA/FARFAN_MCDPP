"""Phase 2: Analysis & Question Execution - Contract-Driven Processing.

This phase implements contract-driven question execution with evidence assembly,
narrative synthesis, and SISAS integration for deterministic policy analysis.

Architecture:
- 309 individual question contracts (Q001-Q309.v3.json)
- BaseExecutorWithContract loads contracts by question_id
- NO hardcoded D1Q1-D6Q5 executor classes
- Direct contract execution without class intermediaries
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Evidence processing - EvidenceNexus for causal graph construction
from canonic_phases.Phase_two.evidence_nexus import (
    EvidenceNexus,
    EvidenceGraph,
    EvidenceNode,
    process_evidence,
)

# Narrative synthesis - Doctoral Carver for PhD-level responses
from canonic_phases.Phase_two.carver import (
    DoctoralCarverSynthesizer,
    CarverAnswer,
)

# Executor configuration and base class
from canonic_phases.Phase_two.executors.executor_config import ExecutorConfig
from canonic_phases.Phase_two.executors.base_executor_with_contract import (
    BaseExecutorWithContract,
)

__all__ = [
    # Evidence processing (EvidenceNexus)
    "EvidenceNexus",
    "EvidenceGraph",
    "EvidenceNode",
    "process_evidence",
    # Narrative synthesis (Carver)
    "DoctoralCarverSynthesizer",
    "CarverAnswer",
    # Executor configuration
    "ExecutorConfig",
    "BaseExecutorWithContract",
]
