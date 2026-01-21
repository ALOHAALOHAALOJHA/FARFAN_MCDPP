"""
F.A.R.F.A.N Analysis Phases
============================

All pipeline phases from Phase_00 through Phase_09.

Phase Overview:
---------------
- Phase_00: Input validation and preprocessing
- Phase_01: Document ingestion and parsing
- Phase_02: Question execution and evidence assembly
- Phase_03: Semantic processing
- Phase_04: Causal analysis
- Phase_05: Bayesian inference
- Phase_06: Validation and verification
- Phase_07: Result aggregation
- Phase_08: Narrative synthesis
- Phase_09: Output formatting

Usage:
------
    from farfan_pipeline.phases import PhaseID, PhaseStatus
    from farfan_pipeline.phases.Phase_02 import BaseExecutorWithContract
"""

from farfan_pipeline.orchestration.orchestrator import PhaseID, PhaseStatus

__all__ = [
    "PhaseID",
    "PhaseStatus",
]
