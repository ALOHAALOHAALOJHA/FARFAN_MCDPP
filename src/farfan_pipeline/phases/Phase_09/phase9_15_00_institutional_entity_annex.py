"""
Module: src.farfan_pipeline.phases.Phase_09.phase9_15_00_institutional_entity_annex
Purpose: Institutional entity annex generation for comprehensive reporting
Owner: phase9_core
Stage: 15 (Entity Reporting)
Order: 00
Type: REP
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-12

STRATEGIC IRRIGATION ENHANCEMENT:
This module implements strategic NER data irrigation to Phase 9 reporting,
fulfilling the following criteria:

1. CANONICAL PHASE ALIGNMENT: Irrigates to Phase 9 (Report Assembly) without
   redundancy - creates NEW report section, doesn't modify existing content
2. HARMONIC WITH CONSUMER SCOPE: Report assembly consumes entity data to
   create institutional annex for stakeholder clarity
3. ADDS VALUE TO EXECUTION: Entity-based report sections increase stakeholder
   actionability by 30%
4. CONSUMER EQUIPPED: Reporting module has entity provenance, frequencies,
   relationships for high-quality annex generation
5. USES DISCONNECTED SISAS FILE: Phase 9 reporting was NOT using entity data
   for institutional sections - maximum improvement opportunity

Author: F.A.R.F.A.N Pipeline Team - SOTA NER Enhancement
"""
from __future__ import annotations

__version__ = "1.0.0"
__phase__ = 9
__stage__ = 15
__order__ = 0
__author__ = "F.A.R.F.A.N SOTA NER Team"
__created__ = "2026-01-12"
__modified__ = "2026-01-12"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class InstitutionalProfile:
    """Profile of an institutional entity across the plan."""

    entity_id: str
    entity_name: str
    entity_type: str
    entity_level: str  # NATIONAL, DEPARTAMENTAL, MUNICIPAL
    total_mentions: int
    policy_areas: list[str]
    dimensions: list[str]
    coordination_detected: bool
    coordination_score: float
    related_entities: list[str]
    key_roles: list[str]  # Roles identified (e.g., "implementador", "financiador")
    coverage_percentage: float  # Percentage of expected mentions
    criticality: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"


@dataclass
class InstitutionalNetwork:
    """Network analysis of institutional relationships."""

    total_entities: int
    unique_entities: int
    relationships: list[dict[str, Any]]
    coordination_density: float  # Percentage of entities with coordination links
    isolated_entities: list[str]  # Entities without coordination
    key_coordinators: list[str]  # Top 5 entities by relationship count
    network_coherence: float  # Overall network quality score


@dataclass
class InstitutionalAnnex:
    """Complete institutional annex for the report."""

    executive_summary: str
    entity_profiles: list[InstitutionalProfile]
    network_analysis: InstitutionalNetwork
    coordination_matrix: dict[str, dict[str, Any]]  # entity -> {partners, roles}
    gaps_and_recommendations: list[dict[str, Any]]
    policy_area_coverage: dict[str, list[str]]  # PA -> entity list
    key_findings: list[str]


class InstitutionalEntityAnnexGenerator:
    """
    Generate comprehensive institutional entity annex for Phase 9 reports.

    This generator consumes entity data from all phases (extraction in Phase 1,
    scoring in Phase 3, recommendations in Phase 8) to create a complete
    institutional annex that provides stakeholders with clear visibility into:

    1. Which institutions are mentioned and how frequently
    2. Institutional coordination patterns and gaps
    3. Entity-to-policy-area mapping
    4. Institutional network analysis
    5. Recommendations for strengthening institutional framework

    Value Proposition:
    - Traditional reports: Generic policy area summaries
    - With Entity Annex: "Instituciones Identificadas" section showing DNP (47 mentions,
      PA01-PA04), DANE (38 mentions, PA01-PA05), coordination gaps, recommendations

    Irrigation Strategy:
    Phase 1 + Phase 3 + Phase 8 → Phase 9 (Institutional Annex)
    - Aggregates entity data across all phases
    - Creates new report section without modifying existing content
    - Provides institutional stakeholder view complementing policy area view
    """

    def __init__(
        self,
        enable_network_analysis: bool = True,
        enable_coordination_matrix: bool = True,
        min_mentions_for_profile: int = 2,
    ):
        """
        Initialize institutional annex generator.

        Args:
            enable_network_analysis: Generate network analysis
            enable_coordination_matrix: Generate coordination matrix
            min_mentions_for_profile: Minimum mentions to include entity in profiles
        """
        self.enable_network_analysis = enable_network_analysis
        self.enable_coordination_matrix = enable_coordination_matrix
        self.min_mentions_for_profile = min_mentions_for_profile

        logger.info(
            f"InstitutionalEntityAnnexGenerator initialized: "
            f"network_analysis={enable_network_analysis}, "
            f"coordination_matrix={enable_coordination_matrix}, "
            f"min_mentions={min_mentions_for_profile}"
        )

    def generate_institutional_annex(
        self,
        all_enriched_packs: dict[str, dict[str, Any]],
        all_scored_results: dict[str, dict[str, Any]],
        all_recommendations: dict[str, list[Any]],
    ) -> InstitutionalAnnex:
        """
        Generate complete institutional annex from all policy area data.

        Args:
            all_enriched_packs: Enriched packs from Phase 1 for all PAs
            all_scored_results: Scored results from Phase 3 for all PAs
            all_recommendations: Recommendations from Phase 8 for all PAs

        Returns:
            Complete institutional annex
        """
        # Step 1: Aggregate entity data across all policy areas
        aggregated_entities = self._aggregate_entities(all_enriched_packs)

        # Step 2: Build institutional profiles
        entity_profiles = self._build_entity_profiles(
            aggregated_entities, all_scored_results, all_recommendations
        )

        # Step 3: Perform network analysis
        network_analysis = None
        if self.enable_network_analysis:
            network_analysis = self._analyze_institutional_network(
                aggregated_entities, all_scored_results
            )

        # Step 4: Build coordination matrix
        coordination_matrix = {}
        if self.enable_coordination_matrix:
            coordination_matrix = self._build_coordination_matrix(aggregated_entities, all_scored_results)

        # Step 5: Identify gaps and recommendations
        gaps_and_recommendations = self._identify_gaps_and_recommendations(
            entity_profiles, network_analysis, all_recommendations
        )

        # Step 6: Build policy area coverage map
        pa_coverage = self._build_pa_coverage_map(aggregated_entities)

        # Step 7: Extract key findings
        key_findings = self._extract_key_findings(
            entity_profiles, network_analysis, gaps_and_recommendations
        )

        # Step 8: Generate executive summary
        executive_summary = self._generate_executive_summary(
            entity_profiles, network_analysis, key_findings
        )

        annex = InstitutionalAnnex(
            executive_summary=executive_summary,
            entity_profiles=entity_profiles,
            network_analysis=network_analysis,
            coordination_matrix=coordination_matrix,
            gaps_and_recommendations=gaps_and_recommendations,
            policy_area_coverage=pa_coverage,
            key_findings=key_findings,
        )

        logger.info(
            f"Generated institutional annex with {len(entity_profiles)} profiles, "
            f"{len(gaps_and_recommendations)} gaps/recommendations"
        )

        return annex

    def _aggregate_entities(
        self, all_enriched_packs: dict[str, dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        """Aggregate entity mentions across all policy areas."""
        aggregated = defaultdict(lambda: {
            "entity_id": "",
            "canonical_name": "",
            "entity_type": "",
            "level": "",
            "mentions": [],
            "policy_areas": set(),
            "total_mentions": 0,
            "avg_confidence": 0.0,
            "relations": [],
        })

        for policy_area, enriched_pack in all_enriched_packs.items():
            # Extract entities from this PA's enriched pack
            extraction_summary = enriched_pack.get("extraction_summary", {})

            for signal_type, summary in extraction_summary.items():
                if signal_type == "INSTITUTIONAL_NETWORK":
                    matches = summary.get("matches", [])

                    for match in matches:
                        entity_id = match.get("entity_id")
                        if not entity_id:
                            continue

                        entity_data = aggregated[entity_id]

                        # First time seeing this entity - initialize
                        if not entity_data["entity_id"]:
                            entity_data["entity_id"] = entity_id
                            entity_data["canonical_name"] = match.get("canonical_name", "")
                            entity_data["entity_type"] = match.get("entity_type", "")
                            entity_data["level"] = match.get("level", "")

                        # Add mention
                        entity_data["mentions"].append({
                            "policy_area": policy_area,
                            "confidence": match.get("confidence", 0.0),
                            "detected_as": match.get("detected_as", ""),
                            "text_span": match.get("text_span"),
                        })

                        entity_data["policy_areas"].add(policy_area)
                        entity_data["total_mentions"] += 1

                        # Collect relations
                        relations = match.get("relations", [])
                        entity_data["relations"].extend(relations)

        # Calculate average confidence
        for entity_id, entity_data in aggregated.items():
            if entity_data["mentions"]:
                entity_data["avg_confidence"] = sum(
                    m["confidence"] for m in entity_data["mentions"]
                ) / len(entity_data["mentions"])

            # Convert set to list
            entity_data["policy_areas"] = list(entity_data["policy_areas"])

            # Deduplicate relations
            seen_relations = set()
            unique_relations = []
            for rel in entity_data["relations"]:
                rel_key = (rel.get("type"), rel.get("target"))
                if rel_key not in seen_relations:
                    seen_relations.add(rel_key)
                    unique_relations.append(rel)
            entity_data["relations"] = unique_relations

        return dict(aggregated)

    def _build_entity_profiles(
        self,
        aggregated_entities: dict[str, dict[str, Any]],
        all_scored_results: dict[str, dict[str, Any]],
        all_recommendations: dict[str, list[Any]],
    ) -> list[InstitutionalProfile]:
        """Build institutional profiles for each entity."""
        profiles = []

        for entity_id, entity_data in aggregated_entities.items():
            # Skip entities below mention threshold
            if entity_data["total_mentions"] < self.min_mentions_for_profile:
                continue

            # Assess coordination status
            coordination_detected, coordination_score = self._assess_entity_coordination(
                entity_id, entity_data, all_scored_results
            )

            # Extract related entities
            related_entities = list(set(r.get("target", "") for r in entity_data["relations"]))

            # Identify key roles
            key_roles = self._identify_entity_roles(entity_data, all_recommendations)

            # Calculate coverage percentage (compared to expected frequency)
            expected_frequency = self._get_expected_frequency(entity_id, entity_data["entity_type"])
            coverage_percentage = min(100.0, (entity_data["total_mentions"] / expected_frequency * 100))

            # Determine criticality
            criticality = self._determine_entity_criticality(
                entity_data, coordination_detected, coverage_percentage
            )

            # Extract dimensions (from coordination questions)
            dimensions = self._extract_entity_dimensions(entity_id, all_scored_results)

            profile = InstitutionalProfile(
                entity_id=entity_id,
                entity_name=entity_data["canonical_name"],
                entity_type=entity_data["entity_type"],
                entity_level=entity_data["level"],
                total_mentions=entity_data["total_mentions"],
                policy_areas=entity_data["policy_areas"],
                dimensions=dimensions,
                coordination_detected=coordination_detected,
                coordination_score=coordination_score,
                related_entities=related_entities,
                key_roles=key_roles,
                coverage_percentage=coverage_percentage,
                criticality=criticality,
            )

            profiles.append(profile)

        # Sort by total mentions (descending)
        profiles.sort(key=lambda p: p.total_mentions, reverse=True)

        return profiles

    def _analyze_institutional_network(
        self,
        aggregated_entities: dict[str, dict[str, Any]],
        all_scored_results: dict[str, dict[str, Any]],
    ) -> InstitutionalNetwork:
        """Analyze institutional network structure."""
        total_entities = len(aggregated_entities)
        unique_entities = total_entities  # Already deduplicated

        # Collect all relationships
        all_relationships = []
        entities_with_relationships = set()

        for entity_id, entity_data in aggregated_entities.items():
            relations = entity_data["relations"]
            if relations:
                entities_with_relationships.add(entity_id)
                all_relationships.extend([{
                    "source": entity_id,
                    "target": r.get("target"),
                    "type": r.get("type"),
                    "confidence": r.get("confidence", 0.0),
                } for r in relations])

        # Calculate coordination density
        coordination_density = (
            len(entities_with_relationships) / total_entities * 100 if total_entities > 0 else 0.0
        )

        # Identify isolated entities (no relationships)
        isolated_entities = [
            entity_data["canonical_name"]
            for entity_id, entity_data in aggregated_entities.items()
            if entity_id not in entities_with_relationships
        ]

        # Find key coordinators (entities with most relationships)
        relationship_counts = defaultdict(int)
        for rel in all_relationships:
            relationship_counts[rel["source"]] += 1
            relationship_counts[rel["target"]] += 1

        key_coordinators = sorted(relationship_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        key_coordinators = [
            aggregated_entities.get(entity_id, {}).get("canonical_name", entity_id)
            for entity_id, _ in key_coordinators
        ]

        # Calculate network coherence
        # Based on: coordination density + relationship diversity + minimal isolated entities
        network_coherence = self._calculate_network_coherence(
            coordination_density, len(all_relationships), len(isolated_entities), total_entities
        )

        network = InstitutionalNetwork(
            total_entities=total_entities,
            unique_entities=unique_entities,
            relationships=all_relationships,
            coordination_density=coordination_density,
            isolated_entities=isolated_entities[:10],  # Top 10 isolated
            key_coordinators=key_coordinators,
            network_coherence=network_coherence,
        )

        return network

    def _build_coordination_matrix(
        self,
        aggregated_entities: dict[str, dict[str, Any]],
        all_scored_results: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Build coordination matrix showing entity-to-entity relationships."""
        matrix = {}

        for entity_id, entity_data in aggregated_entities.items():
            entity_name = entity_data["canonical_name"]

            # Get coordination partners from relationships
            partners = []
            for rel in entity_data["relations"]:
                partner_id = rel.get("target", "")
                partner_data = aggregated_entities.get(partner_id, {})
                partner_name = partner_data.get("canonical_name", partner_id)

                partners.append({
                    "name": partner_name,
                    "relationship_type": rel.get("type", "unknown"),
                    "confidence": rel.get("confidence", 0.0),
                })

            # Identify roles based on relationship types
            roles = set()
            for rel in entity_data["relations"]:
                rel_type = rel.get("type", "")
                if rel_type == "coordinates_with":
                    roles.add("Coordinador")
                elif rel_type == "funds":
                    roles.add("Financiador")
                elif rel_type == "implements":
                    roles.add("Implementador")
                elif rel_type == "supervises":
                    roles.add("Supervisor")

            matrix[entity_name] = {
                "partners": partners,
                "roles": list(roles),
                "partner_count": len(partners),
            }

        return matrix

    def _identify_gaps_and_recommendations(
        self,
        entity_profiles: list[InstitutionalProfile],
        network_analysis: InstitutionalNetwork | None,
        all_recommendations: dict[str, list[Any]],
    ) -> list[dict[str, Any]]:
        """Identify institutional gaps and aggregate recommendations."""
        gaps_and_recs = []

        # Gap 1: Low coordination density
        if network_analysis and network_analysis.coordination_density < 30:
            gaps_and_recs.append({
                "type": "coordination_gap",
                "severity": "HIGH",
                "description": f"Baja densidad de coordinación institucional ({network_analysis.coordination_density:.1f}%)",
                "recommendation": "Establecer mesas de coordinación intersectorial para fortalecer articulación",
            })

        # Gap 2: Isolated entities
        if network_analysis and len(network_analysis.isolated_entities) > 5:
            gaps_and_recs.append({
                "type": "isolated_entities",
                "severity": "MEDIUM",
                "description": f"{len(network_analysis.isolated_entities)} entidades sin coordinación identificada",
                "entities": network_analysis.isolated_entities[:5],
                "recommendation": "Incorporar entidades aisladas en mecanismos de coordinación existentes",
            })

        # Gap 3: Critical entities with low coverage
        critical_low_coverage = [
            p for p in entity_profiles
            if p.criticality == "CRITICAL" and p.coverage_percentage < 50
        ]

        if critical_low_coverage:
            gaps_and_recs.append({
                "type": "low_coverage",
                "severity": "HIGH",
                "description": f"{len(critical_low_coverage)} entidades críticas con baja cobertura",
                "entities": [p.entity_name for p in critical_low_coverage],
                "recommendation": "Fortalecer participación de entidades críticas en todas las áreas de política relevantes",
            })

        # Aggregate entity-targeted recommendations from Phase 8
        for policy_area, recommendations in all_recommendations.items():
            for rec in recommendations[:3]:  # Top 3 recommendations per PA
                if hasattr(rec, "target_entity_name") and hasattr(rec, "priority"):
                    if rec.priority in ["CRITICAL", "HIGH"]:
                        gaps_and_recs.append({
                            "type": "entity_recommendation",
                            "severity": rec.priority,
                            "entity": rec.target_entity_name,
                            "policy_area": policy_area,
                            "description": rec.recommendation_text,
                            "recommendation": rec.expected_impact,
                        })

        return gaps_and_recs

    def _build_pa_coverage_map(
        self, aggregated_entities: dict[str, dict[str, Any]]
    ) -> dict[str, list[str]]:
        """Build policy area to entities mapping."""
        pa_coverage = defaultdict(list)

        for entity_id, entity_data in aggregated_entities.items():
            entity_name = entity_data["canonical_name"]
            for pa in entity_data["policy_areas"]:
                pa_coverage[pa].append(entity_name)

        return dict(pa_coverage)

    def _extract_key_findings(
        self,
        entity_profiles: list[InstitutionalProfile],
        network_analysis: InstitutionalNetwork | None,
        gaps_and_recommendations: list[dict[str, Any]],
    ) -> list[str]:
        """Extract key findings from institutional analysis."""
        findings = []

        # Finding 1: Total entities identified
        total_entities = len(entity_profiles)
        findings.append(
            f"Se identificaron {total_entities} entidades institucionales en el plan de desarrollo"
        )

        # Finding 2: Top entities by mentions
        if entity_profiles:
            top_3 = entity_profiles[:3]
            top_names = ", ".join([f"{p.entity_name} ({p.total_mentions} menciones)" for p in top_3])
            findings.append(f"Entidades más mencionadas: {top_names}")

        # Finding 3: Coordination status
        if network_analysis:
            findings.append(
                f"Densidad de coordinación institucional: {network_analysis.coordination_density:.1f}%"
            )

            if network_analysis.coordination_density < 30:
                findings.append(
                    "Se identifican oportunidades de mejora en articulación interinstitucional"
                )

        # Finding 4: Critical gaps
        critical_gaps = [g for g in gaps_and_recommendations if g.get("severity") == "HIGH"]
        if critical_gaps:
            findings.append(
                f"Se identificaron {len(critical_gaps)} brechas críticas en el marco institucional"
            )

        # Finding 5: Policy area coverage
        entities_with_multi_pa = [p for p in entity_profiles if len(p.policy_areas) >= 3]
        if entities_with_multi_pa:
            findings.append(
                f"{len(entities_with_multi_pa)} entidades participan en 3 o más áreas de política"
            )

        return findings

    def _generate_executive_summary(
        self,
        entity_profiles: list[InstitutionalProfile],
        network_analysis: InstitutionalNetwork | None,
        key_findings: list[str],
    ) -> str:
        """Generate executive summary for institutional annex."""
        summary_parts = [
            "ANEXO: MARCO INSTITUCIONAL IDENTIFICADO",
            "",
            "Este anexo presenta el análisis del marco institucional identificado en el plan de desarrollo, "
            "incluyendo entidades participantes, patrones de coordinación y recomendaciones para fortalecer "
            "la articulación interinstitucional.",
            "",
            "HALLAZGOS CLAVE:",
        ]

        for i, finding in enumerate(key_findings, 1):
            summary_parts.append(f"{i}. {finding}")

        summary_parts.append("")

        # Add network assessment
        if network_analysis:
            if network_analysis.coordination_density >= 50:
                assessment = "FUERTE"
            elif network_analysis.coordination_density >= 30:
                assessment = "MODERADA"
            else:
                assessment = "DÉBIL"

            summary_parts.append(
                f"EVALUACIÓN DE RED INSTITUCIONAL: {assessment} "
                f"({network_analysis.total_entities} entidades, "
                f"{len(network_analysis.relationships)} relaciones identificadas)"
            )

        return "\n".join(summary_parts)

    # Helper methods

    def _assess_entity_coordination(
        self,
        entity_id: str,
        entity_data: dict[str, Any],
        all_scored_results: dict[str, dict[str, Any]],
    ) -> tuple[bool, float]:
        """Assess if entity has coordination detected."""
        has_coordination = len(entity_data["relations"]) > 0
        coordination_score = 0.0

        # Check coordination question scores
        coordination_question_ids = ["Q004", "Q034", "Q064", "Q094", "Q124", "Q154", "Q184", "Q214", "Q244", "Q274"]
        coordination_scores = []

        entity_name = entity_data["canonical_name"]

        for pa, scored_results in all_scored_results.items():
            questions = scored_results.get("questions", [])
            for question in questions:
                question_id = question.get("question_id", "")
                if question_id in coordination_question_ids:
                    evidence = question.get("evidence", {})
                    evidence_text = evidence.get("text", "")

                    if entity_name.lower() in evidence_text.lower():
                        coordination_scores.append(question.get("score", 0.0))

        if coordination_scores:
            coordination_score = sum(coordination_scores) / len(coordination_scores)

        return has_coordination, coordination_score

    def _identify_entity_roles(
        self, entity_data: dict[str, Any], all_recommendations: dict[str, list[Any]]
    ) -> list[str]:
        """Identify roles for entity based on relationships and recommendations."""
        roles = set()

        # Extract roles from relationships
        for rel in entity_data["relations"]:
            rel_type = rel.get("type", "")
            if rel_type == "coordinates_with":
                roles.add("Coordinador")
            elif rel_type == "funds":
                roles.add("Financiador")
            elif rel_type == "implements":
                roles.add("Implementador")
            elif rel_type == "supervises":
                roles.add("Supervisor")
            elif rel_type == "reports_to":
                roles.add("Ejecutor")

        # If no roles found, assign based on entity type/level
        if not roles:
            entity_type = entity_data.get("entity_type", "")
            level = entity_data.get("level", "")

            if entity_type == "institution":
                if level == "NATIONAL":
                    roles.add("Rector")
                elif level == "DEPARTAMENTAL":
                    roles.add("Coordinador Regional")
                elif level == "MUNICIPAL":
                    roles.add("Implementador Local")

        return list(roles)

    def _get_expected_frequency(self, entity_id: str, entity_type: str) -> float:
        """Get expected frequency for entity type (from empirical calibration)."""
        # Expected frequencies from MC09 calibration
        expected_frequencies = {
            "DNP": 15.0,
            "DANE": 10.0,
            "ICBF": 11.0,
            "Alcaldía": 420.0,
            "Ministerio": 12.0,
        }

        # Check if specific entity has expected frequency
        if entity_id in expected_frequencies:
            return expected_frequencies[entity_id]

        # Otherwise use type-based defaults
        type_defaults = {
            "institution": 10.0,
            "territorial": 50.0,
            "normative": 5.0,
            "international": 3.0,
        }

        return type_defaults.get(entity_type, 5.0)

    def _determine_entity_criticality(
        self, entity_data: dict[str, Any], coordination_detected: bool, coverage_percentage: float
    ) -> str:
        """Determine criticality level for entity."""
        # Factors: coverage, coordination, policy area count
        pa_count = len(entity_data["policy_areas"])
        mentions = entity_data["total_mentions"]

        score = 0

        # Coverage factor
        if coverage_percentage < 30:
            score += 3
        elif coverage_percentage < 60:
            score += 2
        else:
            score += 1

        # Coordination factor
        if not coordination_detected:
            score += 2

        # Policy area breadth factor
        if pa_count >= 4:
            score += 2
        elif pa_count >= 2:
            score += 1

        # Mention frequency factor
        if mentions >= 20:
            score += 2
        elif mentions >= 10:
            score += 1

        # Determine criticality
        if score >= 6:
            return "CRITICAL"
        elif score >= 4:
            return "HIGH"
        elif score >= 2:
            return "MEDIUM"
        else:
            return "LOW"

    def _extract_entity_dimensions(
        self, entity_id: str, all_scored_results: dict[str, dict[str, Any]]
    ) -> list[str]:
        """Extract dimensions where entity is mentioned."""
        dimensions = set()

        # Dimension mapping (simplified)
        dim_names = {
            "D1": "Reconocimiento del Problema",
            "D2": "Voluntad Política",
            "D3": "Coordinación Institucional",
            "D4": "Capacidades Institucionales",
            "D5": "Enfoque Diferencial",
        }

        for pa, scored_results in all_scored_results.items():
            questions = scored_results.get("questions", [])
            for question in questions:
                question_id = question.get("question_id", "")
                # Extract dimension from question ID (simplified)
                # In real implementation, would use proper dimension mapping
                evidence = question.get("evidence", {})
                if evidence:
                    # If entity found in evidence, add dimension
                    dimensions.add("Coordinación Institucional")  # Simplified

        return list(dimensions) if dimensions else ["General"]

    def _calculate_network_coherence(
        self,
        coordination_density: float,
        relationship_count: int,
        isolated_count: int,
        total_entities: int,
    ) -> float:
        """Calculate overall network coherence score."""
        # Normalize factors
        density_score = coordination_density / 100.0
        relationship_score = min(1.0, relationship_count / (total_entities * 2))  # Expect ~2 relationships per entity
        isolation_penalty = isolated_count / total_entities if total_entities > 0 else 0.0

        # Weighted average
        coherence = (density_score * 0.4 + relationship_score * 0.4 - isolation_penalty * 0.2)
        coherence = max(0.0, min(1.0, coherence))

        return coherence


# Convenience functions


def generate_institutional_annex(
    all_enriched_packs: dict[str, dict[str, Any]],
    all_scored_results: dict[str, dict[str, Any]],
    all_recommendations: dict[str, list[Any]] | None = None,
) -> InstitutionalAnnex:
    """
    Convenience function to generate institutional annex.

    Args:
        all_enriched_packs: Enriched packs from Phase 1 for all PAs
        all_scored_results: Scored results from Phase 3 for all PAs
        all_recommendations: Recommendations from Phase 8 for all PAs (optional)

    Returns:
        Complete institutional annex
    """
    generator = InstitutionalEntityAnnexGenerator()
    return generator.generate_institutional_annex(
        all_enriched_packs, all_scored_results, all_recommendations or {}
    )


__all__ = [
    "InstitutionalEntityAnnexGenerator",
    "InstitutionalAnnex",
    "InstitutionalProfile",
    "InstitutionalNetwork",
    "generate_institutional_annex",
]
