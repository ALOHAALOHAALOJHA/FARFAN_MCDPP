"""
Module: src.canonic_phases.phase_2.constants
Purpose: Phase 2 immutable constants and configuration
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18
"""
from __future__ import annotations

from .phase2_constants import (
    CPP_CHUNK_COUNT,
    MICRO_ANSWER_COUNT,
    SHARDS_PER_CHUNK,
    FORBIDDEN_IMPORTS,
    FORBIDDEN_RUNTIME_IO_PATTERNS,
)

__all__ = [
    "CPP_CHUNK_COUNT",
    "MICRO_ANSWER_COUNT",
    "SHARDS_PER_CHUNK",
    "FORBIDDEN_IMPORTS",
    "FORBIDDEN_RUNTIME_IO_PATTERNS",
]
