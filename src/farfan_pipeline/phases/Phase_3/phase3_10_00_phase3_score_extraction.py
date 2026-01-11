"""Phase 3 Scoring Implementation

Transforms Phase 2 micro-question execution results into scored results
ready for Phase 4 aggregation. Extracts scores from EvidenceNexus outputs
(completeness, overall_confidence) and maps to Phase 4 format.

Key Functions:
- extract_score_from_nexus: Get overall_confidence from EvidenceNexus result
- map_completeness_to_quality: Map completeness enum to quality_level
- transform_micro_result_to_scored: Convert MicroQuestionRun to ScoredMicroQuestion

NOTE: Phase 2 uses EvidenceNexus which returns:
- overall_confidence (0.0-1.0) → score
- completeness (complete/partial/insufficient/not_applicable) → quality_level
- validation dict (passed/errors/warnings) - no score field unless validation fails
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 3
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "extract_score_from_nexus",
    "map_completeness_to_quality",
]


def extract_score_from_nexus(result_data: dict[str, Any]) -> float:
    """Extract numeric score from Phase 2 EvidenceNexus result.

    Phase 2 uses EvidenceNexus which computes overall_confidence (0.0-1.0).
    This is the primary scoring metric from the evidence graph.

    Args:
        result_data: Full result dict from Phase 2 executor

    Returns:
        overall_confidence score (0.0-1.0), defaults to 0.0 if not found
    """
    # Primary: Get overall_confidence from nexus result
    confidence = result_data.get("overall_confidence")
    if confidence is not None:
        try:
            return float(confidence)
        except (TypeError, ValueError):
            logger.warning(f"Invalid overall_confidence type: {type(confidence)}")

    # Fallback: Check validation.score (only set when validation fails with score_zero policy)
    validation = result_data.get("validation", {})
    score = validation.get("score")
    if score is not None:
        try:
            return float(score)
        except (TypeError, ValueError):
            logger.warning(f"Invalid validation score type: {type(score)}")

    # Fallback: Use mean confidence from evidence elements
    evidence = result_data.get("evidence", {})
    if isinstance(evidence, dict):
        conf_scores = evidence.get("confidence_scores", {})
        mean_conf = conf_scores.get("mean")
        if mean_conf is not None:
            try:
                return float(mean_conf)
            except (TypeError, ValueError):
                pass

    # Default: 0.0
    return 0.0


def map_completeness_to_quality(completeness: str | None) -> str:
    """Map EvidenceNexus completeness enum to quality level.

    Completeness values from EvidenceNexus:
    - "complete" → "EXCELENTE"
    - "partial" → "ACEPTABLE"
    - "insufficient" → "INSUFICIENTE"
    - "not_applicable" → "NO_APLICABLE"

    Args:
        completeness: Completeness enum value from nexus result

    Returns:
        Quality level string for Phase 4 aggregation
    """
    if not completeness:
        return "INSUFICIENTE"

    completeness_lower = completeness.lower()

    mapping = {
        "complete": "EXCELENTE",
        "partial": "ACEPTABLE",
        "insufficient": "INSUFICIENTE",
        "not_applicable": "NO_APLICABLE",
    }

    return mapping.get(completeness_lower, "INSUFICIENTE")


def extract_score_from_evidence(evidence: dict[str, Any] | None) -> float:
    """DEPRECATED: Extract score from evidence dict (legacy).

    Use extract_score_from_nexus() instead. This function is kept for
    backward compatibility but doesn't align with EvidenceNexus architecture.

    Args:
        evidence: Evidence dict from MicroQuestionRun (may be None)

    Returns:
        Extracted score (0.0-1.0), defaults to 0.0 if not found
    """
    if not evidence:
        return 0.0

    # Try validation.score (only set when validation fails)
    validation = evidence.get("validation", {})
    score = validation.get("score")

    if score is not None:
        try:
            return float(score)
        except (TypeError, ValueError):
            logger.warning(f"Invalid score type in validation: {type(score)}")

    # Try confidence_scores.mean as fallback
    if isinstance(evidence, dict):
        conf_scores = evidence.get("confidence_scores", {})
        mean_conf = conf_scores.get("mean")
        if mean_conf is not None:
            try:
                return float(mean_conf)
            except (TypeError, ValueError):
                pass

    return 0.0


def extract_quality_level(evidence: dict[str, Any] | None, completeness: str | None = None) -> str:
    """Extract quality level from Phase 2 result.

    Args:
        evidence: Evidence dict from MicroQuestionRun (may be None)
        completeness: Completeness enum from nexus result (preferred)

    Returns:
        Quality level string, defaults to "INSUFICIENTE" if not found
    """
    # Primary: Map completeness if available
    if completeness:
        return map_completeness_to_quality(completeness)

    # Fallback: Check validation.quality_level (only set when validation fails)
    if evidence:
        validation = evidence.get("validation", {})
        quality = validation.get("quality_level")

        if quality is not None:
            return str(quality)

    return "INSUFICIENTE"


def transform_micro_result_to_scored(
    micro_result: Any,
) -> dict[str, Any]:
    """DEPRECATED: Transform MicroQuestionRun to ScoredMicroQuestion dict.

    NOTE: This function is deprecated and not used by the orchestrator.
    The orchestrator._score_micro_results_async() performs the transformation
    directly using extract_score_from_nexus() and map_completeness_to_quality().

    This function is kept for backward compatibility and testing purposes only.

    Args:
        micro_result: MicroQuestionRun from Phase 2

    Returns:
        Dict ready for ScoredMicroQuestion dataclass construction

    Deprecated:
        Use orchestrator._score_micro_results_async() for production.
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

    # DEPRECATED: Extract score and quality from evidence (legacy fallback)
    # Production code should use extract_score_from_nexus(metadata) instead
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
            "source": "legacy_fallback",
            "method": "extract_from_evidence",
        },
        "metadata": metadata,
        "error": error,
    }

    return scored
