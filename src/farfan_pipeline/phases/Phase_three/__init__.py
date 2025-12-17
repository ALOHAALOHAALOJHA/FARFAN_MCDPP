"""Phase 3 - Scoring Module

This module handles transformation of Phase 2 execution results
into scored results ready for Phase 4 aggregation.

Key Functions:
- Extract validation scores from Phase 2 evidence
- Transform MicroQuestionRun to ScoredMicroQuestion
- Map policy areas and dimensions for aggregation
- Validate input counts, evidence presence, score bounds
"""

from farfan_pipeline.phases.Phase_three.validation import (
    VALID_QUALITY_LEVELS,
    ValidationCounters,
    validate_micro_results_input,
    validate_and_clamp_score,
    validate_quality_level,
    validate_evidence_presence,
)

__all__ = [
    "VALID_QUALITY_LEVELS",
    "ValidationCounters",
    "validate_micro_results_input",
    "validate_and_clamp_score",
    "validate_quality_level",
    "validate_evidence_presence",
]
