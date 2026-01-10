"""
Phase 4 Territorial Context Integration
========================================

Bold, creative, sophisticated integration of PDET territorial context into
Phase 4 hierarchical aggregation while maintaining strict determinism and
total alignment with canonic phases.

This module bridges Phase 3 (Scoring) enriched with PDET context to Phase 4
(Aggregation) by providing territorial-aware weight adjustments and dispersion
interpretation that respect the mathematical rigor of the FARFAN pipeline.

Architectural Principles:
------------------------
1. **Determinism**: Same inputs always produce same outputs
2. **Phase Alignment**: Respects Phase 3 scoring contracts and Phase 4 aggregation logic
3. **Territorial Intelligence**: PDET context informs aggregation without breaking phase boundaries
4. **Mathematical Soundness**: All adjustments preserve aggregation invariants

Integration Pattern:
-------------------
Phase 3 (Scoring) → PDET Enrichment → Enhanced Metadata → Phase 4 (Aggregation)
                                                              ↓
                                          Territorial-Aware Weight Adjustment
                                                              ↓
                                            Context-Sensitive Dispersion Analysis

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
Aligned with: Phase 3 v1.0.0, Phase 4-7 v1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from .pdet_scoring_enrichment import EnrichedScoredResult, PDETScoringContext

logger = logging.getLogger(__name__)


# =============================================================================
# TERRITORIAL AGGREGATION CONTEXT
# =============================================================================


class TerritorialRelevance(Enum):
    """Classification of territorial relevance for aggregation."""

    CRITICAL = "CRITICAL"  # Coverage >= 70%, adjustment >= 0.12
    HIGH = "HIGH"  # Coverage >= 50%, adjustment >= 0.08
    MODERATE = "MODERATE"  # Coverage >= 25%, adjustment >= 0.05
    LOW = "LOW"  # Coverage < 25%, adjustment < 0.05
    NONE = "NONE"  # No PDET enrichment applied


@dataclass
class TerritorialAggregationContext:
    """
    Territorial context for Phase 4 aggregation operations.

    This data structure carries PDET-enriched scoring metadata into Phase 4
    aggregation, enabling territorial-aware weight adjustments and dispersion
    analysis while maintaining phase separation.
    """

    # Question-level enrichment metadata
    question_id: str
    policy_area: str

    # PDET context summary
    territorial_coverage: float
    relevant_pillars: List[str]
    territorial_adjustment: float

    # Enriched quality assessment
    base_quality_level: str
    enriched_quality_level: Optional[str]

    # Territorial relevance classification
    relevance: TerritorialRelevance

    # Aggregation hints (deterministic, derived from context)
    weight_multiplier: float = 1.0  # [0.8, 1.2] - adjustment for aggregation weights
    dispersion_sensitivity: float = 1.0  # [0.5, 1.5] - sensitivity to score dispersion

    # Provenance
    enrichment_timestamp: Optional[str] = None
    gates_passed: Dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_enriched_result(
        cls, question_id: str, policy_area: str, enriched_result: EnrichedScoredResult
    ) -> "TerritorialAggregationContext":
        """
        Create aggregation context from Phase 3 enriched result.

        This is the deterministic bridge from Phase 3 to Phase 4.
        """
        # Classify territorial relevance
        coverage = enriched_result.pdet_context.territorial_coverage
        adjustment = enriched_result.territorial_adjustment

        if coverage >= 0.70 and adjustment >= 0.12:
            relevance = TerritorialRelevance.CRITICAL
            weight_multiplier = 1.2  # Boost weight for critical territories
            dispersion_sensitivity = 0.7  # More tolerant of dispersion
        elif coverage >= 0.50 and adjustment >= 0.08:
            relevance = TerritorialRelevance.HIGH
            weight_multiplier = 1.15
            dispersion_sensitivity = 0.8
        elif coverage >= 0.25 and adjustment >= 0.05:
            relevance = TerritorialRelevance.MODERATE
            weight_multiplier = 1.05
            dispersion_sensitivity = 0.9
        elif adjustment > 0.0:
            relevance = TerritorialRelevance.LOW
            weight_multiplier = 1.0
            dispersion_sensitivity = 1.0
        else:
            relevance = TerritorialRelevance.NONE
            weight_multiplier = 1.0
            dispersion_sensitivity = 1.0

        return cls(
            question_id=question_id,
            policy_area=policy_area,
            territorial_coverage=coverage,
            relevant_pillars=enriched_result.pdet_context.relevant_pillars,
            territorial_adjustment=adjustment,
            base_quality_level=enriched_result.base_result.quality_level,
            enriched_quality_level=enriched_result.enriched_quality_level,
            relevance=relevance,
            weight_multiplier=weight_multiplier,
            dispersion_sensitivity=dispersion_sensitivity,
            enrichment_timestamp=enriched_result.pdet_context.enrichment_metadata.get("timestamp"),
            gates_passed=enriched_result.gate_validation_status,
        )


# =============================================================================
# TERRITORIAL-AWARE AGGREGATION ADAPTER
# =============================================================================


class TerritorialAggregationAdapter:
    """
    Adapts Phase 4 aggregation operations with territorial intelligence.

    This adapter maintains strict determinism while enabling PDET context
    to inform aggregation decisions. It operates as a pure function transformer:
    given the same territorial context, it always produces the same adjustments.

    Design Philosophy:
    -----------------
    - **Non-invasive**: Works alongside existing Phase 4 aggregators
    - **Deterministic**: Pure mathematical transformations
    - **Aligned**: Respects Phase 3/4 contracts and invariants
    - **Traceable**: All adjustments are logged and auditable
    """

    def __init__(
        self,
        enable_weight_adjustment: bool = True,
        enable_dispersion_adjustment: bool = True,
        strict_determinism: bool = True,
    ):
        """
        Initialize territorial aggregation adapter.

        Args:
            enable_weight_adjustment: Apply territorial weight multipliers
            enable_dispersion_adjustment: Adjust dispersion sensitivity
            strict_determinism: Enforce deterministic operation (recommended)
        """
        self._enable_weight_adjustment = enable_weight_adjustment
        self._enable_dispersion_adjustment = enable_dispersion_adjustment
        self._strict_determinism = strict_determinism

        # Audit trail for transparency
        self._adjustment_log: List[Dict[str, Any]] = []

    def adjust_dimension_weights(
        self,
        base_weights: Dict[str, float],
        territorial_contexts: Dict[str, TerritorialAggregationContext],
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        Apply territorial-aware adjustments to dimension-level aggregation weights.

        This method adjusts weights for questions within a dimension based on their
        territorial relevance, maintaining weight normalization (sum = 1.0).

        Algorithm:
        1. Apply weight multipliers based on territorial relevance
        2. Normalize to ensure sum = 1.0 (preserves aggregation invariants)
        3. Log adjustments for auditability

        Args:
            base_weights: Original question weights {question_id: weight}
            territorial_contexts: PDET contexts {question_id: context}

        Returns:
            Tuple of (adjusted_weights, metadata)
        """
        if not self._enable_weight_adjustment:
            return base_weights, {"adjusted": False}

        adjusted_weights = {}
        total_adjustment = 0.0
        adjustments_made = {}

        # Apply territorial multipliers
        for question_id, base_weight in base_weights.items():
            context = territorial_contexts.get(question_id)

            if context and context.relevance != TerritorialRelevance.NONE:
                # Apply weight multiplier
                adjusted_weight = base_weight * context.weight_multiplier
                adjusted_weights[question_id] = adjusted_weight
                total_adjustment += adjusted_weight

                adjustments_made[question_id] = {
                    "base_weight": base_weight,
                    "multiplier": context.weight_multiplier,
                    "relevance": context.relevance.value,
                    "coverage": context.territorial_coverage,
                }
            else:
                # No adjustment
                adjusted_weights[question_id] = base_weight
                total_adjustment += base_weight

        # Normalize to maintain sum = 1.0 (critical for aggregation invariants)
        if total_adjustment > 0:
            normalized_weights = {
                qid: weight / total_adjustment for qid, weight in adjusted_weights.items()
            }
        else:
            normalized_weights = base_weights

        metadata = {
            "adjusted": len(adjustments_made) > 0,
            "adjustments": adjustments_made,
            "normalization_factor": total_adjustment if total_adjustment > 0 else 1.0,
        }

        # Log for audit trail
        self._adjustment_log.append(
            {"operation": "dimension_weight_adjustment", "metadata": metadata}
        )

        return normalized_weights, metadata

    def interpret_dispersion_with_context(
        self,
        coefficient_variation: float,
        dispersion_index: float,
        territorial_contexts: Dict[str, TerritorialAggregationContext],
    ) -> Tuple[str, float, Dict[str, Any]]:
        """
        Interpret score dispersion with territorial context awareness.

        In PDET territories, higher dispersion may be expected and acceptable due to:
        - Diverse municipality characteristics within subregions
        - Varying implementation stages across territories
        - Legitimate regional variations in policy application

        This method adjusts dispersion thresholds based on territorial context,
        maintaining deterministic classification.

        Args:
            coefficient_variation: CV of scores
            dispersion_index: Normalized range of scores
            territorial_contexts: Question-level PDET contexts

        Returns:
            Tuple of (scenario_type, adjusted_penalty, metadata)
        """
        if not self._enable_dispersion_adjustment:
            # Standard interpretation without territorial context
            return self._standard_dispersion_interpretation(coefficient_variation, dispersion_index)

        # Calculate average dispersion sensitivity from territorial contexts
        sensitivities = [
            ctx.dispersion_sensitivity
            for ctx in territorial_contexts.values()
            if ctx.relevance != TerritorialRelevance.NONE
        ]

        if not sensitivities:
            # No territorial context, use standard interpretation
            return self._standard_dispersion_interpretation(coefficient_variation, dispersion_index)

        avg_sensitivity = sum(sensitivities) / len(sensitivities)

        # Adjust CV thresholds based on territorial sensitivity
        # Lower sensitivity = higher tolerance for dispersion
        adjusted_cv_convergence = 0.15 / avg_sensitivity
        adjusted_cv_moderate = 0.40 / avg_sensitivity
        adjusted_cv_high = 0.60 / avg_sensitivity

        # Classify scenario with adjusted thresholds
        if coefficient_variation <= adjusted_cv_convergence:
            scenario = "convergence"
            penalty_factor = 0.8  # Mild penalty
        elif coefficient_variation <= adjusted_cv_moderate:
            scenario = "moderate_dispersion"
            penalty_factor = 1.0  # Standard penalty
        elif coefficient_variation <= adjusted_cv_high:
            scenario = "high_dispersion"
            penalty_factor = 1.3  # Elevated penalty
        else:
            scenario = "extreme_dispersion"
            penalty_factor = 1.5  # Strong penalty

        # Apply territorial sensitivity to penalty
        context_adjusted_penalty = penalty_factor * avg_sensitivity

        metadata = {
            "territorial_contexts_count": len(sensitivities),
            "avg_dispersion_sensitivity": avg_sensitivity,
            "adjusted_thresholds": {
                "convergence": adjusted_cv_convergence,
                "moderate": adjusted_cv_moderate,
                "high": adjusted_cv_high,
            },
            "base_penalty": penalty_factor,
            "context_adjusted_penalty": context_adjusted_penalty,
        }

        return scenario, context_adjusted_penalty, metadata

    def _standard_dispersion_interpretation(
        self, coefficient_variation: float, dispersion_index: float
    ) -> Tuple[str, float, Dict[str, Any]]:
        """Standard dispersion interpretation without territorial context."""
        if coefficient_variation <= 0.15:
            return "convergence", 0.8, {"method": "standard"}
        elif coefficient_variation <= 0.40:
            return "moderate_dispersion", 1.0, {"method": "standard"}
        elif coefficient_variation <= 0.60:
            return "high_dispersion", 1.3, {"method": "standard"}
        else:
            return "extreme_dispersion", 1.5, {"method": "standard"}

    def get_adjustment_report(self) -> Dict[str, Any]:
        """Get comprehensive report of all adjustments made."""
        return {
            "total_adjustments": len(self._adjustment_log),
            "adjustments": self._adjustment_log,
            "configuration": {
                "weight_adjustment_enabled": self._enable_weight_adjustment,
                "dispersion_adjustment_enabled": self._enable_dispersion_adjustment,
                "strict_determinism": self._strict_determinism,
            },
        }


# =============================================================================
# CONVENIENCE FUNCTIONS FOR PHASE 4 INTEGRATION
# =============================================================================


def create_territorial_contexts_from_enriched_results(
    enriched_results: Dict[str, EnrichedScoredResult], policy_area: str
) -> Dict[str, TerritorialAggregationContext]:
    """
    Convert Phase 3 enriched results to Phase 4 aggregation contexts.

    This is the primary integration point between phases.

    Args:
        enriched_results: {question_id: EnrichedScoredResult}
        policy_area: Policy area code

    Returns:
        {question_id: TerritorialAggregationContext}
    """
    contexts = {}

    for question_id, enriched_result in enriched_results.items():
        if enriched_result.enrichment_applied:
            contexts[question_id] = TerritorialAggregationContext.from_enriched_result(
                question_id=question_id, policy_area=policy_area, enriched_result=enriched_result
            )

    return contexts


def create_territorial_adapter(
    enable_weight_adjustment: bool = True, enable_dispersion_adjustment: bool = True
) -> TerritorialAggregationAdapter:
    """Factory function for creating territorial aggregation adapter."""
    return TerritorialAggregationAdapter(
        enable_weight_adjustment=enable_weight_adjustment,
        enable_dispersion_adjustment=enable_dispersion_adjustment,
        strict_determinism=True,  # Always enforce determinism
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "TerritorialRelevance",
    # Data structures
    "TerritorialAggregationContext",
    # Adapter
    "TerritorialAggregationAdapter",
    # Convenience functions
    "create_territorial_contexts_from_enriched_results",
    "create_territorial_adapter",
]
