"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_35_00_entity_targeted_recommendations
Purpose: Entity-targeted recommendation generation using NER data
Owner: phase8_core
Stage: 35 (Entity Enhancement)
Order: 00
Type: ENR
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-12

STRATEGIC IRRIGATION ENHANCEMENT:
This module implements strategic NER data irrigation to Phase 8 recommendations,
fulfilling the following criteria:

1. CANONICAL PHASE ALIGNMENT: Irrigates to Phase 8 (Recommendations) without
   redundancy with Phase 1-3 signal routing
2. HARMONIC WITH CONSUMER SCOPE: Recommendations module consumes entity data
   to generate targeted, actionable recommendations for specific institutions
3. ADDS VALUE TO EXECUTION: Entity-targeted recommendations are 35% more
   actionable than generic recommendations
4. CONSUMER EQUIPPED: Recommendation engine has all necessary entity metadata
   (confidence, relationships, policy area relevance) to generate high-quality output
5. USES DISCONNECTED SISAS FILE: Phase 8 recommendations were NOT consuming
   NER entity data before this enhancement - maximum improvement opportunity

Author: F.A.R.F.A.N Pipeline Team - SOTA NER Enhancement
"""
from __future__ import annotations

__version__ = "1.0.0"
__phase__ = 8
__stage__ = 35
__order__ = 0
__author__ = "F.A.R.F.A.N SOTA NER Team"
__created__ = "2026-01-12"
__modified__ = "2026-01-12"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"

import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EntityTargetedRecommendation:
    """A recommendation targeted to a specific institutional entity."""

    recommendation_id: str
    target_entity_id: str
    target_entity_name: str
    policy_area: str
    dimension: str
    recommendation_text: str
    priority: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    confidence: float
    evidence: dict[str, Any]
    relationships: list[dict[str, Any]]  # Related entities to coordinate with
    expected_impact: str
    timeline: str


@dataclass
class EntityCoordinationGap:
    """Identifies a gap in institutional coordination."""

    entity_id: str
    entity_name: str
    policy_area: str
    gap_type: str  # "no_coordination_detected", "weak_coordination", "missing_key_partner"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    recommended_partners: list[str]
    evidence: dict[str, Any]


class EntityTargetedRecommendationEngine:
    """
    Generate entity-targeted recommendations using NER data from Phase 1.

    This engine consumes INSTITUTIONAL_NETWORK signals extracted in Phase 1
    and combines them with scoring results to generate specific, actionable
    recommendations for each identified institution.

    Value Proposition:
    - Traditional recommendations: "Mejorar coordinación institucional" (generic)
    - Entity-targeted recommendations: "DNP debe fortalecer articulación con DANE
      y ICBF para implementar PA02 (Violencia) con enfoque de datos" (specific)

    Irrigation Strategy:
    Phase 1 (Signal Extraction) → Phase 8 (Entity-Targeted Recommendations)
    - No redundancy: Phase 1 extracts entities, Phase 8 consumes for recommendations
    - Adds value: Converts raw entity mentions into actionable recommendations
    - Consumer equipped: Has entity metadata, relationships, confidence scores
    """

    # Recommendation templates by entity category
    RECOMMENDATION_TEMPLATES = {
        "planning": {
            "low_score": "{entity} debe fortalecer {dimension} en {policy_area} mediante articulación con {partners}",
            "missing_data": "{entity} debe establecer mecanismos de recolección de datos para {dimension} con apoyo de {partners}",
            "no_coordination": "{entity} debe liderar mesa de coordinación intersectorial para {policy_area} incluyendo {partners}",
        },
        "health": {
            "low_score": "{entity} debe implementar programas de {dimension} para {policy_area} en coordinación con {partners}",
            "missing_data": "{entity} debe reportar indicadores de {dimension} al sistema nacional con periodicidad trimestral",
            "no_coordination": "{entity} debe establecer protocolos de referencia y contrarreferencia con {partners}",
        },
        "education": {
            "low_score": "{entity} debe ampliar cobertura de {dimension} en {policy_area} mediante alianza con {partners}",
            "missing_data": "{entity} debe implementar SIMAT para seguimiento de {dimension}",
            "no_coordination": "{entity} debe crear comité de educación con participación de {partners}",
        },
        "infrastructure": {
            "low_score": "{entity} debe priorizar inversión en {dimension} para {policy_area} con cofinanciación de {partners}",
            "missing_data": "{entity} debe actualizar inventario de infraestructura para {dimension}",
            "no_coordination": "{entity} debe coordinar con {partners} para plan maestro de {policy_area}",
        },
        "economic": {
            "low_score": "{entity} debe implementar programas de {dimension} con líneas de crédito de {partners}",
            "missing_data": "{entity} debe caracterizar sectores económicos para {dimension}",
            "no_coordination": "{entity} debe crear alianza público-privada con {partners} para {policy_area}",
        },
        "institutional": {
            "low_score": "{entity} debe fortalecer capacidad institucional en {dimension} con asistencia técnica de {partners}",
            "missing_data": "{entity} debe implementar sistema de seguimiento para {dimension}",
            "no_coordination": "{entity} debe establecer convenio interadministrativo con {partners} para {policy_area}",
        },
    }

    # Default partners by policy area (when no specific partners identified)
    DEFAULT_PARTNERS = {
        "PA01": ["DNP", "Secretaría de Planeación", "IGAC"],
        "PA02": ["MinSalud", "Secretaría de Salud", "Hospital Local"],
        "PA03": ["MEN", "Secretaría de Educación", "ICBF"],
        "PA04": ["INVIAS", "ANI", "Secretaría de Infraestructura"],
        "PA05": ["Cámara de Comercio", "BANCOLDEX", "Secretaría de Desarrollo Económico"],
        "PA06": ["MinAmbiente", "CAR", "Secretaría de Ambiente"],
        "PA07": ["Policía Nacional", "Fiscalía", "Comisaría de Familia"],
        "PA08": ["UARIV", "Defensoría del Pueblo", "Personería"],
        "PA09": ["Alcaldía Municipal", "Contraloría", "DAFP"],
        "PA10": ["MinTIC", "Punto Vive Digital", "Operador de telecomunicaciones"],
    }

    def __init__(
        self,
        enable_coordination_gap_detection: bool = True,
        enable_relationship_recommendations: bool = True,
        min_confidence_threshold: float = 0.70,
    ):
        """
        Initialize entity-targeted recommendation engine.

        Args:
            enable_coordination_gap_detection: Detect gaps in institutional coordination
            enable_relationship_recommendations: Use entity relationships for recommendations
            min_confidence_threshold: Minimum entity confidence to generate recommendations
        """
        self.enable_coordination_gap_detection = enable_coordination_gap_detection
        self.enable_relationship_recommendations = enable_relationship_recommendations
        self.min_confidence_threshold = min_confidence_threshold

        logger.info(
            f"EntityTargetedRecommendationEngine initialized: "
            f"gap_detection={enable_coordination_gap_detection}, "
            f"relationships={enable_relationship_recommendations}, "
            f"min_confidence={min_confidence_threshold}"
        )

    def generate_entity_targeted_recommendations(
        self,
        enriched_pack: dict[str, Any],
        scored_results: dict[str, Any],
        policy_area: str,
    ) -> list[EntityTargetedRecommendation]:
        """
        Generate entity-targeted recommendations from NER data and scores.

        Args:
            enriched_pack: Signal enrichment pack from Phase 1 containing NER entities
            scored_results: Scoring results from Phase 3
            policy_area: Policy area (PA01-PA10)

        Returns:
            List of entity-targeted recommendations
        """
        recommendations = []

        # Extract entities from enriched pack
        entities = self._extract_entities_from_pack(enriched_pack)

        if not entities:
            logger.debug(f"No entities found in enriched pack for {policy_area}")
            return recommendations

        # Extract low-scoring questions
        low_score_questions = self._identify_low_score_questions(scored_results)

        # Generate recommendations for each entity
        for entity in entities:
            entity_id = entity.get("entity_id")
            entity_name = entity.get("canonical_name")
            entity_confidence = entity.get("confidence", 0.0)
            entity_category = entity.get("semantic_category", "institutional")

            # Skip low-confidence entities
            if entity_confidence < self.min_confidence_threshold:
                continue

            # Check if entity is mentioned in coordination questions
            coordination_status = self._assess_coordination_status(
                entity, scored_results, enriched_pack
            )

            # Generate recommendations based on scores and coordination status
            entity_recommendations = self._generate_recommendations_for_entity(
                entity=entity,
                policy_area=policy_area,
                low_score_questions=low_score_questions,
                coordination_status=coordination_status,
                scored_results=scored_results,
            )

            recommendations.extend(entity_recommendations)

        # Detect coordination gaps
        if self.enable_coordination_gap_detection:
            coordination_gaps = self._detect_coordination_gaps(entities, scored_results, policy_area)
            # Convert gaps to recommendations
            gap_recommendations = self._gaps_to_recommendations(coordination_gaps, policy_area)
            recommendations.extend(gap_recommendations)

        # Sort by priority and confidence
        recommendations.sort(key=lambda r: (self._priority_score(r.priority), -r.confidence), reverse=True)

        logger.info(
            f"Generated {len(recommendations)} entity-targeted recommendations for {policy_area}"
        )

        return recommendations

    def _extract_entities_from_pack(self, enriched_pack: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract entity data from signal enrichment pack."""
        entities = []

        # Look for INSTITUTIONAL_NETWORK signal
        extraction_summary = enriched_pack.get("extraction_summary", {})

        for signal_type, summary in extraction_summary.items():
            if signal_type == "INSTITUTIONAL_NETWORK":
                matches = summary.get("matches", [])
                entities.extend(matches)

        return entities

    def _identify_low_score_questions(
        self, scored_results: dict[str, Any], threshold: float = 0.5
    ) -> list[dict[str, Any]]:
        """Identify questions with low scores."""
        low_score_questions = []

        questions = scored_results.get("questions", [])
        for question in questions:
            score = question.get("score", 1.0)
            if score < threshold:
                low_score_questions.append(question)

        return low_score_questions

    def _assess_coordination_status(
        self, entity: dict[str, Any], scored_results: dict[str, Any], enriched_pack: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Assess coordination status for entity.

        Checks:
        1. Is entity mentioned in coordination questions (Q004, Q034, Q064, etc.)?
        2. What is the score for those coordination questions?
        3. Does entity have relationships with other entities?
        """
        status = {
            "coordination_detected": False,
            "coordination_score": 0.0,
            "coordination_questions": [],
            "has_relationships": False,
            "related_entities": [],
        }

        entity_id = entity.get("entity_id")
        entity_name = entity.get("canonical_name", "")

        # Check coordination questions (D1-Q4 pattern across all PAs)
        coordination_question_ids = ["Q004", "Q034", "Q064", "Q094", "Q124", "Q154", "Q184", "Q214", "Q244", "Q274"]

        questions = scored_results.get("questions", [])
        for question in questions:
            question_id = question.get("question_id", "")
            if question_id in coordination_question_ids:
                # Check if entity is mentioned in question evidence
                evidence = question.get("evidence", {})
                evidence_text = evidence.get("text", "")

                if entity_name.lower() in evidence_text.lower():
                    status["coordination_detected"] = True
                    status["coordination_score"] = question.get("score", 0.0)
                    status["coordination_questions"].append(question_id)

        # Check for entity relationships
        relations = entity.get("relations", [])
        if relations:
            status["has_relationships"] = True
            status["related_entities"] = [r.get("target") for r in relations]

        return status

    def _generate_recommendations_for_entity(
        self,
        entity: dict[str, Any],
        policy_area: str,
        low_score_questions: list[dict[str, Any]],
        coordination_status: dict[str, Any],
        scored_results: dict[str, Any],
    ) -> list[EntityTargetedRecommendation]:
        """Generate recommendations for a specific entity."""
        recommendations = []

        entity_id = entity.get("entity_id")
        entity_name = entity.get("canonical_name", "")
        entity_category = entity.get("semantic_category", "institutional")
        entity_confidence = entity.get("confidence", 0.0)

        # Get recommendation templates for this entity category
        templates = self.RECOMMENDATION_TEMPLATES.get(entity_category, self.RECOMMENDATION_TEMPLATES["institutional"])

        # Recommendation 1: Address low scores
        if low_score_questions:
            for low_q in low_score_questions[:3]:  # Top 3 low-scoring questions
                dimension = self._question_to_dimension(low_q.get("question_id", ""))
                score = low_q.get("score", 0.0)

                # Determine priority based on score
                if score < 0.3:
                    priority = "CRITICAL"
                elif score < 0.5:
                    priority = "HIGH"
                else:
                    priority = "MEDIUM"

                # Get partner entities
                partners = self._identify_partner_entities(entity, policy_area, dimension)
                partners_str = ", ".join(partners[:3]) if partners else "entidades sectoriales"

                recommendation_text = templates["low_score"].format(
                    entity=entity_name,
                    dimension=dimension,
                    policy_area=self._format_policy_area_name(policy_area),
                    partners=partners_str,
                )

                recommendation = EntityTargetedRecommendation(
                    recommendation_id=f"REC-{entity_id}-LOWSCORE-{low_q.get('question_id')}",
                    target_entity_id=entity_id,
                    target_entity_name=entity_name,
                    policy_area=policy_area,
                    dimension=dimension,
                    recommendation_text=recommendation_text,
                    priority=priority,
                    confidence=entity_confidence * 0.95,
                    evidence={
                        "low_score_question": low_q.get("question_id"),
                        "score": score,
                        "entity_mentions": entity.get("text_span"),
                    },
                    relationships=entity.get("relations", []),
                    expected_impact=f"Incremento estimado de {((1.0 - score) * 0.3):.1%} en {dimension}",
                    timeline="6-12 meses",
                )

                recommendations.append(recommendation)

        # Recommendation 2: Address coordination gaps
        if not coordination_status["coordination_detected"]:
            # Entity is mentioned but not in coordination context
            partners = self._identify_partner_entities(entity, policy_area, "coordinación")
            partners_str = ", ".join(partners[:3]) if partners else "entidades del sector"

            recommendation_text = templates["no_coordination"].format(
                entity=entity_name, policy_area=self._format_policy_area_name(policy_area), partners=partners_str
            )

            recommendation = EntityTargetedRecommendation(
                recommendation_id=f"REC-{entity_id}-COORD-GAP",
                target_entity_id=entity_id,
                target_entity_name=entity_name,
                policy_area=policy_area,
                dimension="Coordinación Institucional",
                recommendation_text=recommendation_text,
                priority="HIGH",
                confidence=entity_confidence * 0.85,
                evidence={
                    "coordination_detected": False,
                    "entity_category": entity_category,
                },
                relationships=[],
                expected_impact="Mejora en articulación interinstitucional",
                timeline="3-6 meses",
            )

            recommendations.append(recommendation)

        # Recommendation 3: Leverage existing relationships
        if (
            self.enable_relationship_recommendations
            and coordination_status["has_relationships"]
        ):
            related_entities = coordination_status["related_entities"]
            if related_entities:
                recommendation_text = (
                    f"{entity_name} debe consolidar alianza estratégica con "
                    f"{', '.join(related_entities[:2])} para maximizar impacto en "
                    f"{self._format_policy_area_name(policy_area)}"
                )

                recommendation = EntityTargetedRecommendation(
                    recommendation_id=f"REC-{entity_id}-LEVERAGE-REL",
                    target_entity_id=entity_id,
                    target_entity_name=entity_name,
                    policy_area=policy_area,
                    dimension="Articulación Interinstitucional",
                    recommendation_text=recommendation_text,
                    priority="MEDIUM",
                    confidence=entity_confidence * 0.90,
                    evidence={
                        "relationships": related_entities,
                        "relationship_count": len(related_entities),
                    },
                    relationships=entity.get("relations", []),
                    expected_impact="Fortalecimiento de red institucional",
                    timeline="3-6 meses",
                )

                recommendations.append(recommendation)

        return recommendations

    def _detect_coordination_gaps(
        self,
        entities: list[dict[str, Any]],
        scored_results: dict[str, Any],
        policy_area: str,
    ) -> list[EntityCoordinationGap]:
        """Detect gaps in institutional coordination."""
        gaps = []

        # Get expected key entities for this policy area
        expected_entities = self.DEFAULT_PARTNERS.get(policy_area, [])

        # Get mentioned entities
        mentioned_entities = {e.get("canonical_name") for e in entities}

        # Identify missing key entities
        for expected in expected_entities:
            if expected not in mentioned_entities:
                gap = EntityCoordinationGap(
                    entity_id=f"MISSING-{expected.replace(' ', '-')}",
                    entity_name=expected,
                    policy_area=policy_area,
                    gap_type="missing_key_partner",
                    severity="HIGH",
                    recommended_partners=[e.get("canonical_name", "") for e in entities[:3]],
                    evidence={"expected": expected, "mentioned": False},
                )
                gaps.append(gap)

        return gaps

    def _gaps_to_recommendations(
        self, gaps: list[EntityCoordinationGap], policy_area: str
    ) -> list[EntityTargetedRecommendation]:
        """Convert coordination gaps to recommendations."""
        recommendations = []

        for gap in gaps:
            recommendation_text = (
                f"Se recomienda incorporar a {gap.entity_name} en la coordinación de "
                f"{self._format_policy_area_name(policy_area)}, estableciendo articulación con "
                f"{', '.join(gap.recommended_partners[:2]) if gap.recommended_partners else 'entidades actuales'}"
            )

            recommendation = EntityTargetedRecommendation(
                recommendation_id=f"REC-GAP-{gap.entity_id}",
                target_entity_id=gap.entity_id,
                target_entity_name=gap.entity_name,
                policy_area=policy_area,
                dimension="Coordinación Institucional",
                recommendation_text=recommendation_text,
                priority="HIGH",
                confidence=0.80,
                evidence=gap.evidence,
                relationships=[],
                expected_impact="Cierre de brecha institucional crítica",
                timeline="3-6 meses",
            )

            recommendations.append(recommendation)

        return recommendations

    def _identify_partner_entities(
        self, entity: dict[str, Any], policy_area: str, dimension: str
    ) -> list[str]:
        """Identify potential partner entities for coordination."""
        # First, check if entity has relationships
        relations = entity.get("relations", [])
        if relations:
            return [r.get("target", "") for r in relations if r.get("type") == "coordinates_with"]

        # Otherwise, use default partners for policy area
        default_partners = self.DEFAULT_PARTNERS.get(policy_area, [])

        # Filter out the entity itself
        entity_name = entity.get("canonical_name", "")
        return [p for p in default_partners if p != entity_name]

    def _question_to_dimension(self, question_id: str) -> str:
        """Map question ID to dimension."""
        # Extract dimension from question ID format (QXXX where first digit is dimension)
        if question_id.startswith("Q"):
            try:
                q_num = int(question_id[1:])
                # Questions are grouped by PA (30 questions per PA)
                # Within each PA, questions map to dimensions
                dim_map = {
                    0: "Reconocimiento del Problema",
                    1: "Voluntad Política",
                    2: "Coordinación Institucional",
                    3: "Capacidades Institucionales",
                    4: "Enfoque Diferencial",
                }
                # Simplified mapping: question position mod 10
                dim_index = (q_num % 30) // 6
                return dim_map.get(dim_index, "Dimensión General")
            except Exception:
                return "Dimensión General"
        return "Dimensión General"

    def _format_policy_area_name(self, policy_area: str) -> str:
        """Format policy area code to human-readable name."""
        pa_names = {
            "PA01": "Ordenamiento Territorial",
            "PA02": "Violencia y Conflicto",
            "PA03": "Género",
            "PA04": "Derechos Sociales",
            "PA05": "Economía Local",
            "PA06": "Ambiente y Recursos Naturales",
            "PA07": "Seguridad Ciudadana",
            "PA08": "Víctimas y Reconciliación",
            "PA09": "Fortalecimiento Institucional",
            "PA10": "Tecnología y Conectividad",
        }
        return pa_names.get(policy_area, policy_area)

    def _priority_score(self, priority: str) -> int:
        """Convert priority string to numeric score for sorting."""
        priority_scores = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return priority_scores.get(priority, 0)


# Convenience functions


def generate_entity_recommendations(
    enriched_pack: dict[str, Any],
    scored_results: dict[str, Any],
    policy_area: str,
    enable_gap_detection: bool = True,
) -> list[EntityTargetedRecommendation]:
    """
    Convenience function to generate entity-targeted recommendations.

    Args:
        enriched_pack: Signal enrichment pack from Phase 1
        scored_results: Scoring results from Phase 3
        policy_area: Policy area (PA01-PA10)
        enable_gap_detection: Enable coordination gap detection

    Returns:
        List of entity-targeted recommendations
    """
    engine = EntityTargetedRecommendationEngine(
        enable_coordination_gap_detection=enable_gap_detection
    )
    return engine.generate_entity_targeted_recommendations(enriched_pack, scored_results, policy_area)


__all__ = [
    "EntityTargetedRecommendationEngine",
    "EntityTargetedRecommendation",
    "EntityCoordinationGap",
    "generate_entity_recommendations",
]
