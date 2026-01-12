"""
Cross-Cutting Theme Entity Mapper.

Maps institutional entities to cross-cutting themes to validate thematic coverage
and identify gaps in institutional participation across transversal policy themes.

Cross-Cutting Themes (from FARFAN framework):
1. CC_ENFOQUE_DIFERENCIAL (Differential Approach)
2. CC_ENFOQUE_TERRITORIAL (Territorial Approach)
3. CC_ENFOQUE_ÉTNICO (Ethnic Approach)
4. CC_PERSPECTIVA_DE_GÉNERO (Gender Perspective)
5. CC_DERECHOS_HUMANOS (Human Rights)
6. CC_INTEROPERABILIDAD (Interoperability)
7. CC_SOSTENIBILIDAD (Sustainability)
8. CC_PARTICIPACIÓN_CIUDADANA (Citizen Participation)

This module fulfills irrigation criteria:
- Maps NER entities to cross-cutting themes
- Validates institutional theme coverage
- Identifies gaps where key institutions are missing from themes
- Provides maximum granularity for theme-institution analysis

Author: F.A.R.F.A.N SOTA NER Enhancement Team
Version: 1.0.0
Date: 2026-01-12
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EntityThemeMapping:
    """Mapping of an entity to a cross-cutting theme."""

    entity_id: str
    entity_name: str
    theme_id: str
    theme_name: str
    relevance_score: float  # 0.0-1.0, based on entity role and mentions
    evidence: dict[str, Any]


@dataclass
class ThemeCoverage:
    """Coverage analysis for a cross-cutting theme."""

    theme_id: str
    theme_name: str
    expected_entities: list[str]  # Entities that should address this theme
    detected_entities: list[str]  # Entities actually detected for this theme
    missing_entities: list[str]  # Critical entities not addressing theme
    coverage_percentage: float
    gaps: list[dict[str, Any]]


class CrossCuttingThemeEntityMapper:
    """
    Maps institutional entities to cross-cutting themes.

    Uses entity registry and domain knowledge to:
    1. Identify which institutions should address each cross-cutting theme
    2. Validate that expected institutions are present in entity extraction
    3. Calculate theme coverage percentages
    4. Identify gaps where key institutions are missing

    Value Proposition:
    - Traditional approach: Cross-cutting themes evaluated in isolation
    - With Entity Mapping: "CC_ENFOQUE_DIFERENCIAL covered by ICBF (3 mentions),
      Consejería Presidencial (2 mentions), but missing MinSalud (gap)"
    """

    # Expected entities for each cross-cutting theme
    THEME_ENTITY_EXPECTATIONS = {
        "CC_ENFOQUE_DIFERENCIAL": {
            "name": "Enfoque Diferencial",
            "description": "Differential approach for vulnerable populations",
            "expected_entities": [
                "ICBF",  # Children and families
                "Instituto Colombiano de Bienestar Familiar",
                "Consejería Presidencial",
                "Ministerio del Interior",
                "Defensoría del Pueblo",
                "Personería",
            ],
            "policy_areas": ["PA02", "PA03", "PA04", "PA08"],  # Violence, Education, Social Rights, Victims
        },
        "CC_ENFOQUE_TERRITORIAL": {
            "name": "Enfoque Territorial",
            "description": "Territorial development approach",
            "expected_entities": [
                "DNP",
                "Departamento Nacional de Planeación",
                "Secretaría de Planeación",
                "Alcaldía Municipal",
                "Gobernación",
                "IGAC",
                "Instituto Geográfico Agustín Codazzi",
                "Concejo Municipal",
            ],
            "policy_areas": ["PA01", "PA04", "PA05", "PA09"],  # Territory, Infrastructure, Economy, Institutional
        },
        "CC_ENFOQUE_ÉTNICO": {
            "name": "Enfoque Étnico",
            "description": "Ethnic communities and indigenous peoples",
            "expected_entities": [
                "Ministerio del Interior",
                "Consejería Presidencial",
                "Defensoría del Pueblo",
                "Alcaldía Municipal",
                "Gobernación",
            ],
            "policy_areas": ["PA02", "PA04", "PA06", "PA08"],  # Violence, Social Rights, Environment, Victims
        },
        "CC_PERSPECTIVA_DE_GÉNERO": {
            "name": "Perspectiva de Género",
            "description": "Gender perspective and women's rights",
            "expected_entities": [
                "ICBF",
                "Ministerio de Salud",
                "MinSalud",
                "Consejería Presidencial",
                "Comisaría de Familia",
                "Secretaría de la Mujer",
                "Personería",
            ],
            "policy_areas": ["PA02", "PA03", "PA04", "PA07"],  # Violence, Education, Social Rights, Security
        },
        "CC_DERECHOS_HUMANOS": {
            "name": "Derechos Humanos",
            "description": "Human rights protection and promotion",
            "expected_entities": [
                "Defensoría del Pueblo",
                "Personería",
                "Fiscalía",
                "Fiscalía General",
                "Procuraduría",
                "Ministerio del Interior",
                "Alcaldía Municipal",
            ],
            "policy_areas": ["PA02", "PA07", "PA08", "PA09"],  # Violence, Security, Victims, Institutional
        },
        "CC_INTEROPERABILIDAD": {
            "name": "Interoperabilidad",
            "description": "Institutional interoperability and data sharing",
            "expected_entities": [
                "DNP",
                "DANE",
                "Departamento Administrativo Nacional de Estadística",
                "MinTIC",
                "Ministerio de Tecnologías de la Información",
                "Secretaría de Planeación",
                "Contraloría",
                "Alcaldía Municipal",
            ],
            "policy_areas": ["PA01", "PA09", "PA10"],  # Territory, Institutional, Technology
        },
        "CC_SOSTENIBILIDAD": {
            "name": "Sostenibilidad",
            "description": "Environmental and economic sustainability",
            "expected_entities": [
                "MinAmbiente",
                "Ministerio de Ambiente",
                "CAR",
                "Corporación Autónoma Regional",
                "IDEAM",
                "DNP",
                "Secretaría de Ambiente",
                "Secretaría de Planeación",
            ],
            "policy_areas": ["PA01", "PA05", "PA06"],  # Territory, Economy, Environment
        },
        "CC_PARTICIPACIÓN_CIUDADANA": {
            "name": "Participación Ciudadana",
            "description": "Citizen participation and social control",
            "expected_entities": [
                "Alcaldía Municipal",
                "Concejo Municipal",
                "Personería",
                "Veeduría Ciudadana",
                "Contraloría",
                "Defensoría del Pueblo",
                "Junta de Acción Comunal",
            ],
            "policy_areas": ["PA01", "PA07", "PA09"],  # Territory, Security, Institutional
        },
    }

    def __init__(self, entity_registry_path: Path | None = None):
        """
        Initialize cross-cutting theme entity mapper.

        Args:
            entity_registry_path: Path to entity registry (optional)
        """
        self.entity_registry = {}

        if entity_registry_path is None:
            entity_registry_path = (
                Path(__file__).resolve().parent.parent
                / "_registry"
                / "entities"
            )

        self._load_entity_registry(entity_registry_path)

        logger.info(
            f"CrossCuttingThemeEntityMapper initialized with "
            f"{len(self.entity_registry)} entities from registry"
        )

    def _load_entity_registry(self, registry_path: Path):
        """Load entity registry."""
        if not registry_path.exists():
            logger.warning(f"Entity registry not found at {registry_path}")
            return

        entity_files = [
            "institutions.json",
            "normative.json",
            "populations.json",
            "territorial.json",
            "international.json",
        ]

        for filename in entity_files:
            filepath = registry_path / filename
            if filepath.exists():
                with open(filepath) as f:
                    data = json.load(f)
                    entities = data.get("entities", {})
                    self.entity_registry.update(entities)

        logger.info(f"Loaded {len(self.entity_registry)} entities from registry")

    def map_entities_to_themes(
        self, extracted_entities: list[dict[str, Any]]
    ) -> dict[str, list[EntityThemeMapping]]:
        """
        Map extracted entities to cross-cutting themes.

        Args:
            extracted_entities: List of entities from NER extraction

        Returns:
            Dict mapping theme_id to list of EntityThemeMapping
        """
        theme_mappings = defaultdict(list)

        # Create entity name to entity data mapping
        extracted_entity_map = {
            e.get("canonical_name", ""): e for e in extracted_entities
        }

        for theme_id, theme_data in self.THEME_ENTITY_EXPECTATIONS.items():
            expected_entities = theme_data["expected_entities"]

            for expected_entity_name in expected_entities:
                # Check if this expected entity was extracted
                for extracted_name, extracted_data in extracted_entity_map.items():
                    if self._entity_matches(expected_entity_name, extracted_name):
                        # Calculate relevance score
                        relevance_score = self._calculate_relevance_score(
                            extracted_data, theme_data
                        )

                        mapping = EntityThemeMapping(
                            entity_id=extracted_data.get("entity_id", ""),
                            entity_name=extracted_name,
                            theme_id=theme_id,
                            theme_name=theme_data["name"],
                            relevance_score=relevance_score,
                            evidence={
                                "mentions": extracted_data.get("total_mentions", 0),
                                "policy_areas": extracted_data.get("policy_areas", []),
                                "confidence": extracted_data.get("confidence", 0.0),
                            },
                        )

                        theme_mappings[theme_id].append(mapping)

        return dict(theme_mappings)

    def analyze_theme_coverage(
        self, extracted_entities: list[dict[str, Any]]
    ) -> dict[str, ThemeCoverage]:
        """
        Analyze cross-cutting theme coverage.

        Args:
            extracted_entities: List of entities from NER extraction

        Returns:
            Dict mapping theme_id to ThemeCoverage analysis
        """
        theme_coverage = {}

        # Get entity mappings
        theme_mappings = self.map_entities_to_themes(extracted_entities)

        for theme_id, theme_data in self.THEME_ENTITY_EXPECTATIONS.items():
            expected_entities = theme_data["expected_entities"]
            mappings = theme_mappings.get(theme_id, [])

            detected_entities = [m.entity_name for m in mappings]

            # Find missing critical entities
            missing_entities = [
                e for e in expected_entities
                if not any(self._entity_matches(e, d) for d in detected_entities)
            ]

            # Calculate coverage percentage
            coverage_percentage = (
                len(detected_entities) / len(expected_entities) * 100
                if expected_entities
                else 0.0
            )

            # Identify specific gaps
            gaps = []
            if missing_entities:
                for missing in missing_entities:
                    gaps.append({
                        "entity": missing,
                        "severity": "HIGH" if self._is_critical_entity(missing, theme_id) else "MEDIUM",
                        "recommendation": f"Incorporar {missing} en {theme_data['name']}",
                    })

            coverage = ThemeCoverage(
                theme_id=theme_id,
                theme_name=theme_data["name"],
                expected_entities=expected_entities,
                detected_entities=detected_entities,
                missing_entities=missing_entities,
                coverage_percentage=coverage_percentage,
                gaps=gaps,
            )

            theme_coverage[theme_id] = coverage

        return theme_coverage

    def generate_theme_coverage_report(
        self, extracted_entities: list[dict[str, Any]]
    ) -> str:
        """
        Generate human-readable theme coverage report.

        Args:
            extracted_entities: List of entities from NER extraction

        Returns:
            Formatted report string
        """
        coverage_analysis = self.analyze_theme_coverage(extracted_entities)

        report_lines = [
            "=" * 80,
            "ANÁLISIS DE COBERTURA DE TEMAS TRANSVERSALES",
            "=" * 80,
            "",
        ]

        for theme_id, coverage in coverage_analysis.items():
            report_lines.extend([
                f"Tema: {coverage.theme_name} ({theme_id})",
                f"Cobertura: {coverage.coverage_percentage:.1f}%",
                f"Entidades Detectadas: {len(coverage.detected_entities)} de {len(coverage.expected_entities)}",
                "",
            ])

            if coverage.detected_entities:
                report_lines.append("  ✓ Entidades Detectadas:")
                for entity in coverage.detected_entities:
                    report_lines.append(f"    - {entity}")
                report_lines.append("")

            if coverage.missing_entities:
                report_lines.append("  ✗ Entidades Faltantes:")
                for entity in coverage.missing_entities:
                    report_lines.append(f"    - {entity}")
                report_lines.append("")

            if coverage.gaps:
                report_lines.append("  ⚠ Brechas Identificadas:")
                for gap in coverage.gaps:
                    report_lines.append(
                        f"    - [{gap['severity']}] {gap['recommendation']}"
                    )
                report_lines.append("")

            report_lines.append("-" * 80)
            report_lines.append("")

        # Summary statistics
        avg_coverage = sum(c.coverage_percentage for c in coverage_analysis.values()) / len(coverage_analysis)
        total_gaps = sum(len(c.gaps) for c in coverage_analysis.values())

        report_lines.extend([
            "RESUMEN EJECUTIVO:",
            f"  - Cobertura promedio: {avg_coverage:.1f}%",
            f"  - Total brechas identificadas: {total_gaps}",
            f"  - Temas analizados: {len(coverage_analysis)}",
            "",
            "=" * 80,
        ])

        return "\n".join(report_lines)

    def _entity_matches(self, expected: str, extracted: str) -> bool:
        """Check if extracted entity matches expected entity."""
        expected_lower = expected.lower()
        extracted_lower = extracted.lower()

        # Direct match
        if expected_lower == extracted_lower:
            return True

        # Contains match
        if expected_lower in extracted_lower or extracted_lower in expected_lower:
            return True

        # Acronym match (e.g., "ICBF" matches "Instituto Colombiano de Bienestar Familiar")
        if len(expected_lower) <= 10 and len(extracted_lower) <= 10:
            # Check if it's an acronym match
            expected_acronym = "".join([w[0] for w in expected.split() if len(w) > 2])
            extracted_acronym = "".join([w[0] for w in extracted.split() if len(w) > 2])
            if expected_acronym.lower() == extracted_acronym.lower():
                return True

        return False

    def _calculate_relevance_score(
        self, entity_data: dict[str, Any], theme_data: dict[str, Any]
    ) -> float:
        """Calculate relevance score for entity-theme mapping."""
        score = 0.0

        # Factor 1: Entity confidence
        confidence = entity_data.get("confidence", 0.0)
        score += confidence * 0.3

        # Factor 2: Mention frequency
        mentions = entity_data.get("total_mentions", 0)
        mention_score = min(1.0, mentions / 10.0)  # Normalize to 0-1
        score += mention_score * 0.3

        # Factor 3: Policy area overlap
        entity_pas = set(entity_data.get("policy_areas", []))
        theme_pas = set(theme_data.get("policy_areas", []))
        overlap = len(entity_pas.intersection(theme_pas))
        pa_score = overlap / len(theme_pas) if theme_pas else 0.0
        score += pa_score * 0.4

        return min(1.0, score)

    def _is_critical_entity(self, entity_name: str, theme_id: str) -> bool:
        """Determine if entity is critical for theme."""
        # Critical entities by theme
        critical_entities = {
            "CC_ENFOQUE_DIFERENCIAL": ["ICBF", "Consejería Presidencial"],
            "CC_ENFOQUE_TERRITORIAL": ["DNP", "Alcaldía Municipal"],
            "CC_ENFOQUE_ÉTNICO": ["Ministerio del Interior", "Defensoría del Pueblo"],
            "CC_PERSPECTIVA_DE_GÉNERO": ["ICBF", "Ministerio de Salud"],
            "CC_DERECHOS_HUMANOS": ["Defensoría del Pueblo", "Personería"],
            "CC_INTEROPERABILIDAD": ["DNP", "DANE"],
            "CC_SOSTENIBILIDAD": ["MinAmbiente", "CAR"],
            "CC_PARTICIPACIÓN_CIUDADANA": ["Alcaldía Municipal", "Personería"],
        }

        theme_critical = critical_entities.get(theme_id, [])
        return any(self._entity_matches(crit, entity_name) for crit in theme_critical)


# Convenience functions


def analyze_cross_cutting_themes(
    extracted_entities: list[dict[str, Any]]
) -> dict[str, ThemeCoverage]:
    """
    Convenience function to analyze cross-cutting theme coverage.

    Args:
        extracted_entities: List of entities from NER extraction

    Returns:
        Dict mapping theme_id to ThemeCoverage
    """
    mapper = CrossCuttingThemeEntityMapper()
    return mapper.analyze_theme_coverage(extracted_entities)


def generate_theme_report(extracted_entities: list[dict[str, Any]]) -> str:
    """
    Convenience function to generate theme coverage report.

    Args:
        extracted_entities: List of entities from NER extraction

    Returns:
        Formatted report string
    """
    mapper = CrossCuttingThemeEntityMapper()
    return mapper.generate_theme_coverage_report(extracted_entities)


__all__ = [
    "CrossCuttingThemeEntityMapper",
    "EntityThemeMapping",
    "ThemeCoverage",
    "analyze_cross_cutting_themes",
    "generate_theme_report",
]
