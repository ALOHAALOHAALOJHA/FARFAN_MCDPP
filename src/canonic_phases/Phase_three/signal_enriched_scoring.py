"""Phase 3 Signal-Enriched Scoring Module

Extends Phase 3 scoring with signal-based enhancements for increased rigor
and determinism. Provides signal-driven threshold adjustments and quality
mapping with full provenance tracking.

Enhancement Value:
- Signal-based threshold adaptation based on question complexity
- Signal-driven quality level validation
- Enhanced scoring provenance with signal metadata
- Deterministic, byte-reproducible scoring with signal context

Integration: Used by orchestrator._score_micro_results_async() to enhance
basic scoring with signal intelligence.

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from cross_cutting_infrastrucuture.irrigation_using_signals.SISAS.signal_registry import (
            QuestionnaireSignalRegistry,
        )
    except ImportError:
        QuestionnaireSignalRegistry = Any  # type: ignore

logger = logging.getLogger(__name__)

__all__ = [
    "SignalEnrichedScorer",
    "get_signal_adjusted_threshold",
    "get_signal_quality_validation",
]


class SignalEnrichedScorer:
    """Signal-enriched scorer for Phase 3 with deterministic enhancements.
    
    Adds signal intelligence to basic Phase 3 scoring without changing
    core scoring logic. All enhancements are additive and optional.
    
    Attributes:
        signal_registry: Optional signal registry for signal-driven scoring
        enable_threshold_adjustment: Enable signal-based threshold tuning
        enable_quality_validation: Enable signal-based quality validation
    """
    
    def __init__(
        self,
        signal_registry: QuestionnaireSignalRegistry | None = None,
        enable_threshold_adjustment: bool = True,
        enable_quality_validation: bool = True,
    ) -> None:
        """Initialize signal-enriched scorer.
        
        Args:
            signal_registry: Optional signal registry for signal access
            enable_threshold_adjustment: Enable threshold adjustment feature
            enable_quality_validation: Enable quality validation feature
        """
        self.signal_registry = signal_registry
        self.enable_threshold_adjustment = enable_threshold_adjustment
        self.enable_quality_validation = enable_quality_validation
        
        logger.info(
            f"SignalEnrichedScorer initialized: "
            f"registry={'enabled' if signal_registry else 'disabled'}, "
            f"threshold_adj={enable_threshold_adjustment}, "
            f"quality_val={enable_quality_validation}"
        )
    
    def adjust_threshold_for_question(
        self,
        question_id: str,
        base_threshold: float,
        score: float,
        metadata: dict[str, Any],
    ) -> tuple[float, dict[str, Any]]:
        """Adjust scoring threshold based on signal-driven question complexity.
        
        Uses signal registry to determine question complexity and adjust
        thresholds accordingly. More complex questions get slightly lower
        thresholds to account for increased difficulty.
        
        Args:
            question_id: Question identifier (e.g., "Q001")
            base_threshold: Base threshold from scoring system
            score: Computed score for the question
            metadata: Question metadata dict
            
        Returns:
            Tuple of (adjusted_threshold, adjustment_details)
        """
        if not self.enable_threshold_adjustment or not self.signal_registry:
            return base_threshold, {"adjustment": "none", "reason": "disabled_or_no_registry"}
        
        adjustment_details: dict[str, Any] = {
            "base_threshold": base_threshold,
            "adjustments": [],
        }
        
        adjusted = base_threshold
        
        try:
            # Get micro answering signals for question
            signal_pack = self.signal_registry.get_micro_answering_signals(question_id)
            
            # Adjust based on pattern complexity (more patterns = more complex)
            pattern_count = len(signal_pack.patterns) if hasattr(signal_pack, 'patterns') else 0
            if pattern_count > 15:  # High pattern complexity
                adjustment = -0.05  # Lower threshold slightly
                adjusted = max(0.3, adjusted + adjustment)
                adjustment_details["adjustments"].append({
                    "type": "high_pattern_complexity",
                    "pattern_count": pattern_count,
                    "adjustment": adjustment,
                })
            
            # Adjust based on indicator count (more indicators = more specific)
            indicator_count = len(signal_pack.indicators) if hasattr(signal_pack, 'indicators') else 0
            if indicator_count > 10:  # High indicator specificity
                adjustment = 0.03  # Raise threshold slightly for specificity
                adjusted = min(0.9, adjusted + adjustment)
                adjustment_details["adjustments"].append({
                    "type": "high_indicator_specificity",
                    "indicator_count": indicator_count,
                    "adjustment": adjustment,
                })
            
            # Adjust based on evidence quality from metadata
            completeness = metadata.get("completeness", "").lower()
            if completeness == "complete":
                adjustment = 0.02  # Slight bonus for complete evidence
                adjusted = min(0.9, adjusted + adjustment)
                adjustment_details["adjustments"].append({
                    "type": "complete_evidence",
                    "completeness": completeness,
                    "adjustment": adjustment,
                })
            
            adjustment_details["adjusted_threshold"] = adjusted
            adjustment_details["total_adjustment"] = adjusted - base_threshold
            
            logger.debug(
                f"Threshold adjusted for {question_id}: "
                f"{base_threshold:.3f} → {adjusted:.3f} "
                f"(Δ={adjusted - base_threshold:+.3f})"
            )
            
        except Exception as e:
            logger.warning(
                f"Failed to adjust threshold for {question_id}: {e}. "
                f"Using base threshold {base_threshold:.3f}"
            )
            adjustment_details["error"] = str(e)
            adjusted = base_threshold
        
        return adjusted, adjustment_details
    
    def validate_quality_level(
        self,
        question_id: str,
        quality_level: str,
        score: float,
        completeness: str | None,
    ) -> tuple[str, dict[str, Any]]:
        """Validate and potentially adjust quality level using signal intelligence.
        
        Uses signal-based heuristics to ensure quality level is consistent
        with score, completeness, and question characteristics.
        
        Args:
            question_id: Question identifier
            quality_level: Computed quality level from Phase 3
            score: Numeric score (0.0-1.0)
            completeness: Completeness enum from EvidenceNexus
            
        Returns:
            Tuple of (validated_quality_level, validation_details)
        """
        if not self.enable_quality_validation:
            return quality_level, {"validation": "disabled"}
        
        validation_details: dict[str, Any] = {
            "original_quality": quality_level,
            "score": score,
            "completeness": completeness,
            "checks": [],
        }
        
        validated = quality_level
        
        try:
            # Check 1: Score-quality consistency
            if score >= 0.8 and quality_level in ["INSUFICIENTE", "NO_APLICABLE"]:
                validation_details["checks"].append({
                    "check": "score_quality_consistency",
                    "issue": "high_score_low_quality",
                    "action": "promote_quality",
                })
                validated = "ACEPTABLE"  # Promote to at least ACEPTABLE
                logger.info(
                    f"Quality promoted for {question_id}: "
                    f"{quality_level} → {validated} (high score {score:.3f})"
                )
            
            # Check 2: Completeness-quality alignment
            if completeness == "complete" and quality_level == "INSUFICIENTE":
                validation_details["checks"].append({
                    "check": "completeness_quality_alignment",
                    "issue": "complete_evidence_low_quality",
                    "action": "promote_quality",
                })
                validated = "ACEPTABLE"  # At least ACEPTABLE for complete evidence
                logger.info(
                    f"Quality promoted for {question_id}: "
                    f"{quality_level} → {validated} (complete evidence)"
                )
            
            # Check 3: Low score validation
            if score < 0.3 and quality_level == "EXCELENTE":
                validation_details["checks"].append({
                    "check": "low_score_validation",
                    "issue": "low_score_high_quality",
                    "action": "demote_quality",
                })
                validated = "ACEPTABLE"  # Demote to ACEPTABLE
                logger.info(
                    f"Quality demoted for {question_id}: "
                    f"{quality_level} → {validated} (low score {score:.3f})"
                )
            
            validation_details["validated_quality"] = validated
            validation_details["adjusted"] = validated != quality_level
            
        except Exception as e:
            logger.warning(
                f"Failed to validate quality for {question_id}: {e}. "
                f"Using original quality {quality_level}"
            )
            validation_details["error"] = str(e)
            validated = quality_level
        
        return validated, validation_details
    
    def enrich_scoring_details(
        self,
        question_id: str,
        base_scoring_details: dict[str, Any],
        threshold_adjustment: dict[str, Any],
        quality_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Enrich scoring details with signal provenance.
        
        Adds signal-based metadata to scoring details for full transparency
        and reproducibility.
        
        Args:
            question_id: Question identifier
            base_scoring_details: Base scoring details from Phase 3
            threshold_adjustment: Threshold adjustment details
            quality_validation: Quality validation details
            
        Returns:
            Enriched scoring details dict
        """
        enriched = {
            **base_scoring_details,
            "signal_enrichment": {
                "enabled": True,
                "registry_available": self.signal_registry is not None,
                "threshold_adjustment": threshold_adjustment,
                "quality_validation": quality_validation,
            },
        }
        
        return enriched


def get_signal_adjusted_threshold(
    signal_registry: QuestionnaireSignalRegistry | None,
    question_id: str,
    base_threshold: float,
    score: float,
    metadata: dict[str, Any],
) -> tuple[float, dict[str, Any]]:
    """Convenience function for signal-based threshold adjustment.
    
    Creates a temporary SignalEnrichedScorer and returns adjusted threshold.
    
    Args:
        signal_registry: Signal registry instance (optional)
        question_id: Question identifier
        base_threshold: Base threshold value
        score: Computed score
        metadata: Question metadata
        
    Returns:
        Tuple of (adjusted_threshold, adjustment_details)
    """
    scorer = SignalEnrichedScorer(signal_registry=signal_registry)
    return scorer.adjust_threshold_for_question(
        question_id=question_id,
        base_threshold=base_threshold,
        score=score,
        metadata=metadata,
    )


def get_signal_quality_validation(
    question_id: str,
    quality_level: str,
    score: float,
    completeness: str | None,
) -> tuple[str, dict[str, Any]]:
    """Convenience function for signal-based quality validation.
    
    Creates a temporary SignalEnrichedScorer and returns validated quality.
    
    Args:
        question_id: Question identifier
        quality_level: Original quality level
        score: Computed score
        completeness: Completeness enum
        
    Returns:
        Tuple of (validated_quality, validation_details)
    """
    scorer = SignalEnrichedScorer()
    return scorer.validate_quality_level(
        question_id=question_id,
        quality_level=quality_level,
        score=score,
        completeness=completeness,
    )
