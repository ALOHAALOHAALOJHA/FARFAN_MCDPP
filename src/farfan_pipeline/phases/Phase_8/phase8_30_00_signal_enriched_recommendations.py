"""
Module: src.farfan_pipeline.phases.Phase_8.phase8_30_00_signal_enriched_recommendations
Purpose: Signal-based enhancement for recommendation engine
Owner: phase8_core
Stage: 30 (Enrichment)
Order: 00
Type: ENR
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-05

Extends Phase 8 recommendation engine with signal-based enhancements for
context-aware, data-driven recommendations with enhanced precision and
determinism.

Enhancement Value:
- Signal-based rule matching using questionnaire patterns
- Signal-driven priority scoring for interventions
- Pattern-based intervention template selection
- Enhanced recommendation provenance with signal metadata

Integration: Used by RecommendationEngine to enhance rule evaluation
with signal intelligence.

Author: F.A.R.F.A.N Pipeline Team
"""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
            QuestionnaireSignalRegistry,
        )
    except ImportError:
        QuestionnaireSignalRegistry = Any  # type: ignore

logger = logging.getLogger(__name__)

# Default fallback values (replaced with actual values in production)
DEFAULT_POLICY_AREA = "PA01"
DEFAULT_QUESTION_FORMAT = "{:03d}"  # Format for question IDs

# Pattern/indicator thresholds for signal support
STRONG_PATTERN_THRESHOLD = 5  # Pattern count for strong support
STRONG_INDICATOR_THRESHOLD = 3  # Indicator count for strong support

# Priority scoring thresholds
CRITICAL_SCORE_THRESHOLD = 0.3  # Scores below this are critical
LOW_SCORE_THRESHOLD = 0.5  # Scores below this are low
CRITICAL_PRIORITY_BOOST = 0.3  # Priority boost for critical scores
LOW_PRIORITY_BOOST = 0.2  # Priority boost for low scores
INSUFFICIENT_QUALITY_BOOST = 0.2  # Boost for insufficient quality
ACTIONABILITY_PATTERN_THRESHOLD = 10  # Pattern count for actionability
ACTIONABILITY_INDICATOR_THRESHOLD = 5  # Indicator count for actionability
ACTIONABILITY_BOOST = 0.15  # Boost for high actionability

__all__ = [
    "SignalEnrichedRecommender",
    "enhance_rule_matching",
    "prioritize_interventions",
]


class SignalEnrichedRecommender:
    """Signal-enriched recommender for Phase 8 with pattern-based matching.
    
    Enhances recommendation engine with signal intelligence for better
    rule matching, priority scoring, and intervention selection.
    
    Attributes:
        signal_registry: Optional signal registry for signal access
        enable_pattern_matching: Enable signal-based pattern matching
        enable_priority_scoring: Enable signal-driven priority scoring
    """
    
    def __init__(
        self,
        signal_registry: QuestionnaireSignalRegistry | None = None,
        enable_pattern_matching: bool = True,
        enable_priority_scoring: bool = True,
    ) -> None:
        """Initialize signal-enriched recommender.
        
        Args:
            signal_registry: Optional signal registry for signal access
            enable_pattern_matching: Enable pattern matching feature
            enable_priority_scoring: Enable priority scoring feature
        """
        self.signal_registry = signal_registry
        self.enable_pattern_matching = enable_pattern_matching
        self.enable_priority_scoring = enable_priority_scoring
        
        logger.info(
            f"SignalEnrichedRecommender initialized: "
            f"registry={'enabled' if signal_registry else 'disabled'}, "
            f"pattern_match={enable_pattern_matching}, "
            f"priority_score={enable_priority_scoring}"
        )
    
    def enhance_rule_condition(
        self,
        rule_id: str,
        condition: dict[str, Any],
        score_data: dict[str, Any],
    ) -> tuple[bool, dict[str, Any]]:
        """Enhance rule condition evaluation with signal-based pattern matching.
        
        Uses signal patterns to improve rule matching accuracy and provide
        additional context for condition evaluation.
        
        Args:
            rule_id: Rule identifier
            condition: Rule condition dict
            score_data: Score data to evaluate against
            
        Returns:
            Tuple of (condition_met, evaluation_details)
        """
        if not self.enable_pattern_matching:
            return False, {"enhancement": "disabled"}
        
        evaluation_details: dict[str, Any] = {
            "rule_id": rule_id,
            "base_condition": condition,
            "enhancements": [],
        }
        
        condition_met = False
        
        try:
            # Extract condition parameters
            field = condition.get("field", "")
            operator = condition.get("operator", "")
            threshold = condition.get("value", 0.0)
            
            # Get actual value from score_data
            actual_value = score_data.get(field, 0.0)
            
            # Basic evaluation
            if operator == "lt":
                base_met = actual_value < threshold
            elif operator == "lte":
                base_met = actual_value <= threshold
            elif operator == "gt":
                base_met = actual_value > threshold
            elif operator == "gte":
                base_met = actual_value >= threshold
            elif operator == "eq":
                base_met = actual_value == threshold
            else:
                base_met = False
            
            evaluation_details["base_evaluation"] = {
                "met": base_met,
                "actual_value": actual_value,
                "threshold": threshold,
                "operator": operator,
            }
            
            # Signal-based enhancement: Check if patterns support this condition
            if self.signal_registry and base_met:
                try:
                    # Try to get related signals
                    # In production, extract actual policy_area from score_data
                    signal_pack = self.signal_registry.get_micro_answering_signals(
                        f"Q{int(score_data.get('question_global', 1)):03d}"
                    )
                    
                    # Check if condition field matches signal patterns
                    pattern_count = len(signal_pack.patterns) if hasattr(signal_pack, 'patterns') else 0
                    indicator_count = len(signal_pack.indicators) if hasattr(signal_pack, 'indicators') else 0
                    
                    # Add confidence boost if signals support the condition
                    if pattern_count > 5:  # Strong pattern support
                        evaluation_details["enhancements"].append({
                            "type": "pattern_support",
                            "pattern_count": pattern_count,
                            "confidence_boost": 0.1,
                        })
                    
                    if indicator_count > 3:  # Strong indicator support
                        evaluation_details["enhancements"].append({
                            "type": "indicator_support",
                            "indicator_count": indicator_count,
                            "confidence_boost": 0.05,
                        })
                    
                except Exception as e:
                    logger.debug(f"Signal enhancement failed for rule {rule_id}: {e}")
            
            condition_met = base_met
            evaluation_details["final_result"] = condition_met
            
        except Exception as e:
            logger.warning(f"Failed to enhance rule condition for {rule_id}: {e}")
            evaluation_details["error"] = str(e)
            condition_met = False
        
        return condition_met, evaluation_details
    
    def compute_intervention_priority(
        self,
        recommendation: dict[str, Any],
        score_data: dict[str, Any],
    ) -> tuple[float, dict[str, Any]]:
        """Compute intervention priority using signal-driven scoring.
        
        Analyzes recommendation and score data with signal intelligence to
        determine intervention priority for resource allocation.
        
        Args:
            recommendation: Recommendation dict with intervention details
            score_data: Score data for context
            
        Returns:
            Tuple of (priority_score, priority_details)
        """
        if not self.enable_priority_scoring:
            return 0.5, {"priority": "disabled"}
        
        priority_details: dict[str, Any] = {
            "factors": [],
            "base_priority": 0.5,
        }
        
        priority_score = 0.5  # Neutral base
        
        try:
            # Factor 1: Score severity (lower scores = higher priority)
            actual_score = score_data.get("score", 0.5)
            if actual_score < 0.3:
                severity_boost = 0.3  # Critical priority
                priority_details["factors"].append({
                    "type": "critical_score",
                    "score": actual_score,
                    "boost": severity_boost,
                })
                priority_score += severity_boost
            elif actual_score < 0.5:
                severity_boost = 0.2  # High priority
                priority_details["factors"].append({
                    "type": "low_score",
                    "score": actual_score,
                    "boost": severity_boost,
                })
                priority_score += severity_boost
            
            # Factor 2: Quality level
            quality_level = score_data.get("quality_level", "")
            if quality_level == "INSUFICIENTE":
                quality_boost = 0.2
                priority_details["factors"].append({
                    "type": "insufficient_quality",
                    "quality": quality_level,
                    "boost": quality_boost,
                })
                priority_score += quality_boost
            
            # Factor 3: Signal-based pattern density (more patterns = more actionable)
            if self.signal_registry:
                try:
                    question_id = f"Q{int(score_data.get('question_global', 1)):03d}"
                    signal_pack = self.signal_registry.get_micro_answering_signals(question_id)
                    
                    pattern_count = len(signal_pack.patterns) if hasattr(signal_pack, 'patterns') else 0
                    indicator_count = len(signal_pack.indicators) if hasattr(signal_pack, 'indicators') else 0
                    
                    # High pattern/indicator density suggests actionability
                    if pattern_count > 10 and indicator_count > 5:
                        actionability_boost = 0.15
                        priority_details["factors"].append({
                            "type": "high_actionability",
                            "pattern_count": pattern_count,
                            "indicator_count": indicator_count,
                            "boost": actionability_boost,
                        })
                        priority_score += actionability_boost
                    
                except Exception as e:
                    logger.debug(f"Signal-based priority scoring failed: {e}")
            
            # Clamp priority to [0.0, 1.0]
            priority_score = max(0.0, min(1.0, priority_score))
            priority_details["final_priority"] = priority_score
            
        except Exception as e:
            logger.warning(f"Failed to compute intervention priority: {e}")
            priority_details["error"] = str(e)
            priority_score = 0.5
        
        return priority_score, priority_details
    
    def select_intervention_template(
        self,
        problem_type: str,
        score_data: dict[str, Any],
    ) -> tuple[str | None, dict[str, Any]]:
        """Select intervention template using signal-based pattern analysis.
        
        Uses signal patterns to identify the most appropriate intervention
        template for the identified problem.
        
        Args:
            problem_type: Type of problem identified
            score_data: Score data for context
            
        Returns:
            Tuple of (template_id, selection_details)
        """
        selection_details: dict[str, Any] = {
            "problem_type": problem_type,
            "candidates": [],
        }
        
        template_id = None
        
        try:
            # Map problem types to template patterns
            template_mapping = {
                "insufficient_baseline": "intervention_baseline",
                "weak_causal_links": "intervention_causality",
                "missing_indicators": "intervention_measurement",
                "low_coverage": "intervention_coverage",
                "inconsistent_data": "intervention_quality",
            }
            
            # Base template selection
            template_id = template_mapping.get(problem_type, "intervention_generic")
            selection_details["base_template"] = template_id
            
            # Signal-based refinement
            if self.signal_registry:
                try:
                    question_id = f"Q{int(score_data.get('question_global', 1)):03d}"
                    signal_pack = self.signal_registry.get_micro_answering_signals(question_id)
                    
                    # Analyze signal patterns to refine template choice
                    patterns = signal_pack.patterns if hasattr(signal_pack, 'patterns') else []
                    
                    # Check for specific pattern types that suggest template refinement
                    temporal_patterns = [p for p in patterns if 'temporal' in str(p).lower()]
                    causal_patterns = [p for p in patterns if 'caus' in str(p).lower() or 'efect' in str(p).lower()]
                    
                    if len(temporal_patterns) > 3:
                        selection_details["candidates"].append({
                            "template": "intervention_temporal",
                            "reason": "high_temporal_pattern_density",
                            "count": len(temporal_patterns),
                        })
                        # Refine template for temporal focus
                        if problem_type in ["insufficient_baseline", "missing_indicators"]:
                            template_id = "intervention_temporal"
                    
                    if len(causal_patterns) > 3:
                        selection_details["candidates"].append({
                            "template": "intervention_causality",
                            "reason": "high_causal_pattern_density",
                            "count": len(causal_patterns),
                        })
                        # Refine template for causal focus
                        if problem_type in ["weak_causal_links", "inconsistent_data"]:
                            template_id = "intervention_causality"
                    
                except Exception as e:
                    logger.debug(f"Signal-based template selection failed: {e}")
            
            selection_details["selected_template"] = template_id
            
        except Exception as e:
            logger.warning(f"Failed to select intervention template: {e}")
            selection_details["error"] = str(e)
            template_id = "intervention_generic"
        
        return template_id, selection_details
    
    def enrich_recommendation(
        self,
        recommendation: dict[str, Any],
        evaluation_details: dict[str, Any],
        priority_details: dict[str, Any],
        template_details: dict[str, Any],
    ) -> dict[str, Any]:
        """Enrich recommendation with signal-based metadata.
        
        Adds signal provenance and enhancement details to recommendation
        for full transparency and reproducibility.
        
        Args:
            recommendation: Base recommendation dict
            evaluation_details: Rule evaluation details
            priority_details: Priority scoring details
            template_details: Template selection details
            
        Returns:
            Enriched recommendation dict
        """
        enriched = {
            **recommendation,
            "signal_enrichment": {
                "enabled": True,
                "registry_available": self.signal_registry is not None,
                "evaluation": evaluation_details,
                "priority": priority_details,
                "template_selection": template_details,
            },
        }
        
        return enriched


def enhance_rule_matching(
    signal_registry: QuestionnaireSignalRegistry | None,
    rule_id: str,
    condition: dict[str, Any],
    score_data: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    """Convenience function for signal-enhanced rule matching.
    
    Creates a temporary SignalEnrichedRecommender and evaluates condition.
    
    Args:
        signal_registry: Signal registry instance (optional)
        rule_id: Rule identifier
        condition: Rule condition to evaluate
        score_data: Score data for evaluation
        
    Returns:
        Tuple of (condition_met, evaluation_details)
    """
    recommender = SignalEnrichedRecommender(signal_registry=signal_registry)
    return recommender.enhance_rule_condition(
        rule_id=rule_id,
        condition=condition,
        score_data=score_data,
    )


def prioritize_interventions(
    signal_registry: QuestionnaireSignalRegistry | None,
    recommendations: list[dict[str, Any]],
    score_data: dict[str, Any],
) -> list[tuple[dict[str, Any], float, dict[str, Any]]]:
    """Prioritize interventions using signal-driven scoring.
    
    Args:
        signal_registry: Signal registry instance (optional)
        recommendations: List of recommendation dicts
        score_data: Score data for context
        
    Returns:
        List of tuples: (recommendation, priority_score, priority_details)
    """
    recommender = SignalEnrichedRecommender(signal_registry=signal_registry)
    
    prioritized = []
    for rec in recommendations:
        priority_score, priority_details = recommender.compute_intervention_priority(
            recommendation=rec,
            score_data=score_data,
        )
        prioritized.append((rec, priority_score, priority_details))
    
    # Sort by priority score (descending)
    prioritized.sort(key=lambda x: x[1], reverse=True)
    
    return prioritized
