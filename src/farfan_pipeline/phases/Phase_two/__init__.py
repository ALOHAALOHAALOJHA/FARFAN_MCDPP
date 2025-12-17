"""Phase 2: Analysis & Question Execution - Contract-Driven Processing.

This phase implements contract-driven question execution with evidence assembly,
narrative synthesis, and SISAS integration for deterministic policy analysis.
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

# Executor implementations - Moved to executors/ subfolder
from canonic_phases.Phase_two.executors.executor_config import ExecutorConfig
from canonic_phases.Phase_two.executors import (
    D1Q1_Executor,
    D1Q2_Executor,
    D1Q3_Executor,
    D1Q4_Executor,
    D1Q5_Executor,
    D2Q1_Executor,
    D2Q2_Executor,
    D2Q3_Executor,
    D2Q4_Executor,
    D2Q5_Executor,
    D3Q1_Executor,
    D3Q2_Executor,
    D3Q3_Executor,
    D3Q4_Executor,
    D3Q5_Executor,
    D4Q1_Executor,
    D4Q2_Executor,
    D4Q3_Executor,
    D4Q4_Executor,
    D4Q5_Executor,
    D5Q1_Executor,
    D5Q2_Executor,
    D5Q3_Executor,
    D5Q4_Executor,
    D5Q5_Executor,
    D6Q1_Executor,
    D6Q2_Executor,
    D6Q3_Executor,
    D6Q4_Executor,
    D6Q5_Executor,
)

# Re-export executors module for backward compatibility with orchestrator
# (orchestrator imports "from canonic_phases.Phase_two import executors")
from canonic_phases.Phase_two import executors

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
    # Executors (30 total: D1-D6, Q1-Q5)
    "D1Q1_Executor",
    "D1Q2_Executor",
    "D1Q3_Executor",
    "D1Q4_Executor",
    "D1Q5_Executor",
    "D2Q1_Executor",
    "D2Q2_Executor",
    "D2Q3_Executor",
    "D2Q4_Executor",
    "D2Q5_Executor",
    "D3Q1_Executor",
    "D3Q2_Executor",
    "D3Q3_Executor",
    "D3Q4_Executor",
    "D3Q5_Executor",
    "D4Q1_Executor",
    "D4Q2_Executor",
    "D4Q3_Executor",
    "D4Q4_Executor",
    "D4Q5_Executor",
    "D5Q1_Executor",
    "D5Q2_Executor",
    "D5Q3_Executor",
    "D5Q4_Executor",
    "D5Q5_Executor",
    "D6Q1_Executor",
    "D6Q2_Executor",
    "D6Q3_Executor",
    "D6Q4_Executor",
    "D6Q5_Executor",
    # Module re-export for backward compatibility
    "executors",
]
