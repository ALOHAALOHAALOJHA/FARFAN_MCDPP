"""
PDET Context Enrichment for Scoring System
===========================================

Integrates PDET municipality context into scoring criteria and analysis,
validated through the four-gate validation framework.

This module provides:
1. PDET-aware scoring configuration
2. Territorial context for scoring adjustments
3. Four-gate validated enrichment
4. Policy area to PDET subregion mapping

Architecture:
-------------
- Uses EnrichmentOrchestrator for four-gate validation
- Applies territorial context to scoring modalities
- Adjusts thresholds based on municipality characteristics
- Tracks PDET pillars relevance in scoring metadata

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from canonic_questionnaire_central.colombia_context.enrichment_orchestrator import (
    EnrichmentOrchestrator,
    EnrichmentRequest,
)
from canonic_questionnaire_central.validations.runtime_validators import (
    SignalScope,
    SignalCapability,
    ScopeLevel,
)

from .scoring_modalities import ScoredResult
from .quality_levels import (
    determine_quality_level,
    THRESHOLD_EXCELENTE,
    THRESHOLD_BUENO,
    THRESHOLD_ACEPTABLE,
)

logger = logging.getLogger(__name__)


@dataclass
class PDETScoringContext:
    """PDET context for scoring enrichment."""

    municipalities: List[Dict[str, Any]] = field(default_factory=list)
    subregions: List[Dict[str, Any]] = field(default_factory=list)
    policy_area_mappings: Dict[str, Any] = field(default_factory=dict)
    relevant_pillars: List[str] = field(default_factory=list)
    territorial_coverage: float = 0.0
    enrichment_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnrichedScoredResult:
    """Scored result enriched with PDET context.

    Includes context-aware quality level that reflects territorial adjustments.
    The enriched_quality_level considers the adjusted threshold, providing
    semantic consistency between territorial leniency and quality assessment.
    """

    base_result: ScoredResult
    pdet_context: PDETScoringContext
    territorial_adjustment: float = 0.0
    enrichment_applied: bool = False
    enriched_quality_level: Optional[str] = None  # Context-aware quality level
    gate_validation_status: Dict[str, bool] = field(default_factory=dict)


class PDETScoringEnricher:
    """
    Enriches scoring with PDET municipality context.

    Validates enrichment through four gates:
    - Gate 1: Scope authorization
    - Gate 2: Value-add verification
    - Gate 3: Capability readiness
    - Gate 4: Channel authenticity
    """

    # PDET Data Constants (from pdet_municipalities.json overview)
    TOTAL_PDET_MUNICIPALITIES = 170
    TOTAL_PDET_SUBREGIONS = 16

    def __init__(
        self,
        orchestrator: Optional[EnrichmentOrchestrator] = None,
        enable_territorial_adjustment: bool = True,
        strict_mode: bool = True,
    ):
        """
        Initialize PDET scoring enricher.

        Args:
            orchestrator: EnrichmentOrchestrator instance (creates default if None)
            enable_territorial_adjustment: Apply territorial adjustments to scores
            strict_mode: Require all gates to pass
        """
        self._orchestrator = orchestrator or EnrichmentOrchestrator(
            strict_mode=strict_mode, enable_all_gates=True
        )
        self._enable_territorial_adjustment = enable_territorial_adjustment
        self._strict_mode = strict_mode

        # Configure scoring consumer scope
        self._scoring_scope = SignalScope(
            scope_name="Scoring System PDET Enrichment",
            scope_level=ScopeLevel.EVIDENCE_COLLECTION,
            allowed_signal_types=["ENRICHMENT_DATA", "*"],
            allowed_policy_areas=["*"],  # All policy areas
            min_confidence=0.50,
            max_signals_per_query=200,
        )

        # Declare scoring capabilities
        self._scoring_capabilities = [
            SignalCapability.SEMANTIC_PROCESSING,
            SignalCapability.TABLE_PARSING,
            SignalCapability.GRAPH_CONSTRUCTION,
        ]

    def enrich_scored_result(
        self,
        scored_result: ScoredResult,
        question_id: str,
        policy_area: str,
        requested_context: Optional[List[str]] = None,
    ) -> EnrichedScoredResult:
        """
        Enrich a scored result with PDET context.

        Args:
            scored_result: Base scoring result to enrich
            question_id: Question identifier
            policy_area: Policy area code (e.g., "PA01")
            requested_context: Specific context types to include

        Returns:
            EnrichedScoredResult with PDET context
        """
        if requested_context is None:
            requested_context = ["municipalities", "subregions", "policy_area_mappings"]

        # Create enrichment request
        request = EnrichmentRequest(
            consumer_id="scoring_system",
            consumer_scope=self._scoring_scope,
            consumer_capabilities=self._scoring_capabilities,
            target_policy_areas=[policy_area],
            target_questions=[question_id],
            requested_context=requested_context,
            metadata={
                "scoring_modality": scored_result.modality,
                "base_score": scored_result.score,
                "quality_level": scored_result.quality_level,
            },
        )

        # Perform enrichment through four gates
        enrichment_result = self._orchestrator.enrich(request)

        if not enrichment_result.success:
            logger.warning(
                f"PDET enrichment failed validation for {question_id} {policy_area}: "
                f"{enrichment_result.violations}"
            )
            # Return non-enriched result
            return EnrichedScoredResult(
                base_result=scored_result,
                pdet_context=PDETScoringContext(),
                enrichment_applied=False,
                gate_validation_status=enrichment_result.gate_status,
            )

        # Extract PDET context
        pdet_data = enrichment_result.enriched_data.get("data", {})
        pdet_context = PDETScoringContext(
            municipalities=pdet_data.get("municipalities", []),
            subregions=pdet_data.get("subregions", []),
            policy_area_mappings=pdet_data.get("policy_area_mappings", {}),
            relevant_pillars=self._extract_relevant_pillars(pdet_data, policy_area),
            territorial_coverage=self._calculate_territorial_coverage(pdet_data),
            enrichment_metadata={
                "request_id": enrichment_result.request_id,
                "timestamp": enrichment_result.timestamp,
                "gates_passed": enrichment_result.gate_status,
            },
        )

        # Calculate territorial adjustment
        territorial_adjustment = 0.0
        enriched_quality_level = None

        if self._enable_territorial_adjustment:
            territorial_adjustment = self._calculate_territorial_adjustment(
                scored_result, pdet_context, policy_area
            )

            # Calculate context-aware quality level
            base_threshold = scored_result.scoring_metadata.get("threshold", 0.65)
            adjusted_threshold = max(base_threshold - territorial_adjustment, 0.4)
            enriched_quality_level = self._calculate_enriched_quality_level(
                base_score=scored_result.score,
                adjusted_threshold=adjusted_threshold,
                territorial_adjustment=territorial_adjustment,
                pdet_context=pdet_context,
            )

        return EnrichedScoredResult(
            base_result=scored_result,
            pdet_context=pdet_context,
            territorial_adjustment=territorial_adjustment,
            enrichment_applied=True,
            enriched_quality_level=enriched_quality_level,
            gate_validation_status=enrichment_result.gate_status,
        )

    def _extract_relevant_pillars(self, pdet_data: Dict[str, Any], policy_area: str) -> List[str]:
        """Extract PDET pillars relevant to policy area."""
        pa_mappings = pdet_data.get("policy_area_mappings", {})

        # Get mapping for this policy area
        pa_key = f"{policy_area}_"
        for key, mapping in pa_mappings.items():
            if key.startswith(pa_key):
                return mapping.get("pdet_pillars", [])

        return []

    def _calculate_territorial_coverage(self, pdet_data: Dict[str, Any]) -> float:
        """Calculate territorial coverage score."""
        municipalities = pdet_data.get("municipalities", [])
        subregions = pdet_data.get("subregions", [])

        if not municipalities and not subregions:
            return 0.0

        # Calculate based on number of relevant municipalities (use class constant)
        muni_coverage = len(municipalities) / float(self.TOTAL_PDET_MUNICIPALITIES)

        # Calculate based on number of relevant subregions (use class constant)
        subregion_coverage = len(subregions) / float(self.TOTAL_PDET_SUBREGIONS)

        # Weighted average
        return (muni_coverage * 0.6) + (subregion_coverage * 0.4)

    def _calculate_territorial_adjustment(
        self, scored_result: ScoredResult, pdet_context: PDETScoringContext, policy_area: str
    ) -> float:
        """
        Calculate territorial adjustment based on PDET context.

        Adjustment factors:
        - High territorial coverage: +0.05 bonus
        - Relevant PDET pillars present: +0.03 per pillar (max +0.09)
        - TYPE_E modality (territorial): +0.02 bonus

        Total max adjustment: +0.16
        """
        adjustment = 0.0

        # Coverage bonus
        if pdet_context.territorial_coverage >= 0.5:
            adjustment += 0.05
        elif pdet_context.territorial_coverage >= 0.25:
            adjustment += 0.03

        # Pillar relevance bonus
        pillar_bonus = min(len(pdet_context.relevant_pillars) * 0.03, 0.09)
        adjustment += pillar_bonus

        # Modality bonus for territorial questions
        if scored_result.modality == "TYPE_E":
            adjustment += 0.02

        return adjustment

    def _calculate_enriched_quality_level(
        self,
        base_score: float,
        adjusted_threshold: float,
        territorial_adjustment: float,
        pdet_context: PDETScoringContext,
    ) -> str:
        """
        Calculate context-aware quality level reflecting territorial adjustments.

        This provides semantic consistency: when territorial context lowers the
        threshold (making scoring more lenient), the quality level reflects
        this contextual interpretation.

        Algorithm:
        1. For significant PDET relevance (adjustment >= 0.10): Apply proportional
           quality boost based on score's relationship to adjusted threshold
        2. For moderate PDET relevance (0.05 <= adjustment < 0.10): Apply modest boost
        3. For low PDET relevance (adjustment < 0.05): Use base quality level

        Args:
            base_score: Original score value [0.0, 1.0]
            adjusted_threshold: Threshold after territorial adjustment
            territorial_adjustment: Magnitude of adjustment applied
            pdet_context: PDET territorial context

        Returns:
            Enriched quality level string (EXCELENTE, BUENO, ACEPTABLE, INSUFICIENTE)
        """
        # Determine contextual boost based on PDET relevance
        if territorial_adjustment >= 0.10:
            # Significant PDET relevance: Strong contextual boost
            # Effective thresholds: EXCELENTE≥0.75, BUENO≥0.60, ACEPTABLE≥0.45
            if base_score >= 0.75:
                return "EXCELENTE"
            elif base_score >= 0.60:
                return "BUENO"
            elif base_score >= 0.45:
                return "ACEPTABLE"
            else:
                return "INSUFICIENTE"

        elif territorial_adjustment >= 0.05:
            # Moderate PDET relevance: Modest contextual boost
            # Effective thresholds: EXCELENTE≥0.80, BUENO≥0.65, ACEPTABLE≥0.50
            if base_score >= 0.80:
                return "EXCELENTE"
            elif base_score >= 0.65:
                return "BUENO"
            elif base_score >= 0.50:
                return "ACEPTABLE"
            else:
                return "INSUFICIENTE"

        else:
            # Low PDET relevance: Use standard quality determination
            return determine_quality_level(base_score)

    def apply_enrichment_to_config(
        self,
        base_config: ModalityConfig,
        pdet_context: PDETScoringContext,
        territorial_adjustment: float,
    ) -> ModalityConfig:
        """
        Create new modality config with PDET adjustments.

        Args:
            base_config: Original modality configuration
            pdet_context: PDET context
            territorial_adjustment: Calculated adjustment

        Returns:
            New ModalityConfig with adjusted threshold
        """
        # Adjust threshold based on territorial context
        # Lower threshold for high PDET coverage (more lenient)
        adjusted_threshold = max(
            base_config.threshold - territorial_adjustment, 0.4  # Minimum threshold
        )

        # Create new config (immutable dataclass)
        return ModalityConfig(
            modality=base_config.modality,
            threshold=adjusted_threshold,
            aggregation=base_config.aggregation,
            weights=base_config.weights,
            normalization=base_config.normalization,
            failure_code=base_config.failure_code,
        )

    def get_enrichment_summary(self, enriched_result: EnrichedScoredResult) -> Dict[str, Any]:
        """Get summary of PDET enrichment."""
        # Safely get threshold from metadata with default
        base_threshold = enriched_result.base_result.scoring_metadata.get("threshold", 0.0)

        return {
            "enrichment_applied": enriched_result.enrichment_applied,
            "gate_validation": enriched_result.gate_validation_status,
            "territorial_coverage": enriched_result.pdet_context.territorial_coverage,
            "municipalities_count": len(enriched_result.pdet_context.municipalities),
            "subregions_count": len(enriched_result.pdet_context.subregions),
            "relevant_pillars": enriched_result.pdet_context.relevant_pillars,
            "territorial_adjustment": enriched_result.territorial_adjustment,
            "base_score": enriched_result.base_result.score,
            "base_quality_level": enriched_result.base_result.quality_level,
            "enriched_quality_level": enriched_result.enriched_quality_level,
            "adjusted_threshold": (
                (base_threshold - enriched_result.territorial_adjustment)
                if enriched_result.enrichment_applied and base_threshold > 0
                else None
            ),
        }


def create_pdet_enricher(
    strict_mode: bool = True, enable_territorial_adjustment: bool = True
) -> PDETScoringEnricher:
    """
    Factory function to create PDET scoring enricher.

    Args:
        strict_mode: Require all four gates to pass
        enable_territorial_adjustment: Apply territorial adjustments

    Returns:
        Configured PDETScoringEnricher instance
    """
    return PDETScoringEnricher(
        orchestrator=None,  # Will create default
        enable_territorial_adjustment=enable_territorial_adjustment,
        strict_mode=strict_mode,
    )


__all__ = [
    "PDETScoringContext",
    "EnrichedScoredResult",
    "PDETScoringEnricher",
    "create_pdet_enricher",
]
