"""
Contract: Phase 3 Entry Contract
================================

Defines the input types and preconditions for Phase 3 (Scoring).
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict

@dataclass
class MicroQuestionRun:
    """Represents a single micro-question execution result from Phase 2."""
    question_id: str                    # e.g., "PA01-DIM01-Q001"
    question_global: int                # e.g., 1
    base_slot: str                      # e.g., "D1-Q1"
    evidence: Any                       # EvidenceNexus output (Evidence object or dict)
    metadata: Dict[str, Any]            # Execution metadata
    error: Optional[str] = None         # Error message if failed
    duration_ms: Optional[float] = None # Execution duration in milliseconds
    aborted: bool = False               # Whether execution was aborted
