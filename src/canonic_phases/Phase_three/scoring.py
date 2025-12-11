"""Phase 3 Scoring Implementation

Transforms Phase 2 micro-question execution results into scored results
ready for Phase 4 aggregation. Extracts validation scores from evidence
and maps policy areas/dimensions for hierarchical aggregation.

Key Functions:
- extract_score_from_evidence: Get validation score from Phase 2 evidence
- transform_to_scored_result: Convert MicroQuestionRun to ScoredMicroQuestion
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "extract_score_from_evidence",
    "extract_quality_level",
    "transform_micro_result_to_scored",
]


def extract_score_from_evidence(evidence: dict[str, Any] | None) -> float:
    """Extract numeric score from Phase 2 evidence validation.
    
    Phase 2 executors compute validation scores during execution.
    This function extracts the pre-computed score from the evidence dict.
    
    Args:
        evidence: Evidence dict from MicroQuestionRun (may be None)
        
    Returns:
        Extracted score (0.0-1.0), defaults to 0.0 if not found
    """
    if not evidence:
        return 0.0
    
    validation = evidence.get("validation", {})
    score = validation.get("score")
    
    if score is None:
        return 0.0
    
    try:
        return float(score)
    except (TypeError, ValueError):
        logger.warning(f"Invalid score type in validation: {type(score)}")
        return 0.0


def extract_quality_level(evidence: dict[str, Any] | None) -> str:
    """Extract quality level from Phase 2 evidence validation.
    
    Args:
        evidence: Evidence dict from MicroQuestionRun (may be None)
        
    Returns:
        Quality level string, defaults to "INSUFICIENTE" if not found
    """
    if not evidence:
        return "INSUFICIENTE"
    
    validation = evidence.get("validation", {})
    quality = validation.get("quality_level")
    
    if quality is None:
        return "INSUFICIENTE"
    
    return str(quality)


def transform_micro_result_to_scored(
    micro_result: Any,
) -> dict[str, Any]:
    """Transform MicroQuestionRun to ScoredMicroQuestion dict.
    
    Extracts:
    - question_id, question_global, base_slot from micro_result
    - score and quality_level from evidence.validation
    - policy_area and dimension from metadata
    - evidence dict for Phase 4 aggregation
    
    Args:
        micro_result: MicroQuestionRun from Phase 2
        
    Returns:
        Dict ready for ScoredMicroQuestion dataclass construction
    """
    question_id = getattr(micro_result, "question_id", None)
    question_global = getattr(micro_result, "question_global", 0)
    base_slot = getattr(micro_result, "base_slot", "UNKNOWN")
    metadata = getattr(micro_result, "metadata", {})
    evidence_obj = getattr(micro_result, "evidence", None)
    error = getattr(micro_result, "error", None)
    
    # Extract evidence dict (Evidence dataclass or dict)
    if hasattr(evidence_obj, "__dict__"):
        evidence = evidence_obj.__dict__
    elif isinstance(evidence_obj, dict):
        evidence = evidence_obj
    else:
        evidence = {}
    
    # Extract score and quality from validation
    score = extract_score_from_evidence(evidence)
    quality_level = extract_quality_level(evidence)
    
    # Build scored result dict
    scored = {
        "question_id": question_id,
        "question_global": question_global,
        "base_slot": base_slot,
        "score": score,
        "normalized_score": score,  # Already normalized 0.0-1.0
        "quality_level": quality_level,
        "evidence": evidence_obj,  # Keep original Evidence object
        "scoring_details": {
            "source": "phase2_validation",
            "method": "extract",
        },
        "metadata": metadata,
        "error": error,
    }
    
    return scored
