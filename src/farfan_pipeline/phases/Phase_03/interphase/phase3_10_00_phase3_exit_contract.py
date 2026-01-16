"""
Contract: Phase 3 Exit Contract
===============================

Defines the output types and postconditions for Phase 3 (Scoring).
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict
from ..primitives.phase3_10_00_quality_levels import QualityLevel

@dataclass
class ScoredMicroQuestion:
    """Represents a scored micro-question, ready for Phase 4 aggregation."""
    question_id: str
    question_global: int
    base_slot: str
    score: float                        # [0.0, 1.0] — INVARIANT
    normalized_score: float             # [0.0, 1.0] or [0, 100] depending on config
    quality_level: str                  # ∈ VALID_QUALITY_LEVELS — INVARIANT (String for broader compatibility)
    evidence: Any | None
    scoring_details: Dict[str, Any]     # Includes signal enrichment provenance
    metadata: Dict[str, Any]
    error: str | None
