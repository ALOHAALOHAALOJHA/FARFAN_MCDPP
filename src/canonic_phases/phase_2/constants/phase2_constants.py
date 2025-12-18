"""
Module: src.canonic_phases.phase_2.constants.phase2_constants
Purpose: Immutable constants for Phase 2 processing
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - ConstantsFreezeContract: All values are immutable
    - CardinalityInvariant: CPP_CHUNK_COUNT * SHARDS_PER_CHUNK == MICRO_ANSWER_COUNT

Determinism:
    State-Management: Immutable constants only

Architecture:
    - Phase 1 outputs 60 chunks (10 Policy Areas × 6 Dimensions)
    - Phase 2 processes 300 micro-answers (60 chunks × 5 shards per chunk)
    - No runtime reads from questionnaire_monolith.json permitted
"""
from __future__ import annotations

CPP_CHUNK_COUNT: int = 60

SHARDS_PER_CHUNK: int = 5

MICRO_ANSWER_COUNT: int = 300

FORBIDDEN_IMPORTS: list[str] = [
    "questionnaire_monolith",
    "canonic_questionnaire_central.questionnaire_monolith",
]

FORBIDDEN_RUNTIME_IO_PATTERNS: list[str] = [
    r'open\s*\([^)]*monolith',
    r'Path\s*\([^)]*monolith',
    r'read.*monolith',
    r'load.*monolith',
]
