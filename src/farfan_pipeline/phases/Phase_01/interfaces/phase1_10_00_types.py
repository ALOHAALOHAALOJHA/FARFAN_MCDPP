"""
Phase 1 Type Definitions.

Purpose: Centralize type aliases and TypedDicts for Phase 1.
Owner Module: Phase 1 CPP Ingestion
Lifecycle State: ACTIVE
"""

from typing import Any, NotRequired, TypedDict


class TruncationAuditDict(TypedDict):
    """Serialized form of TruncationAudit."""

    total_chars: int
    processed_chars: int
    chars_lost: int
    loss_ratio: float
    limit_applied: int
    was_truncated: bool


class SubphaseResultDict(TypedDict):
    """Result from a single subphase execution."""

    subphase_id: int
    success: bool
    output: Any
    error: NotRequired[str]


class ChunkTraceability(TypedDict):
    """Traceability metadata for chunk assignment."""

    assignment_method: str
    semantic_confidence: float


# Type aliases
SpanMapping = dict[tuple[int, int], tuple[int, int]]
SignalScores = dict[str, float]
PolicyAreaRelevance = dict[str, float]
