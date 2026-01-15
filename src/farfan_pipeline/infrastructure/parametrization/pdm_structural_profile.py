"""
PDM Structural Profile - Constitutional object for PDM structural recognition.

This module defines the structural profile for Colombian municipal development plans (PDM)
according to Ley 152/94. This profile is MANDATORY for Phase 1 execution.

CONSTITUTIONAL REQUIREMENTS:
- This profile does NOT alter FARFAN architecture (60 chunks, 10 PA, 6 Dimensions)
- This profile DOES redefine internal document structure interpretation
- Absence of this profile → Phase 1 ABORT with PrerequisiteError

Author: FARFAN Engineering Team
Version: PDM-2025.1
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal, Pattern


class HierarchyLevel(Enum):
    """
    Hierarchy levels according to Ley 152/94.

    Colombian municipal development plans follow a strict hierarchy:
    - H1: PARTE (Strategic Part, Diagnostic, etc.)
    - H2: CAPITULO (Chapter / Strategic Axis)
    - H3: LINEA (Strategic Line / Program)
    - H4: SUBPROGRAMA (Subprogram / Project)
    - H5: META (Goal / Indicator)
    """
    H1 = "PARTE"
    H2 = "CAPITULO"
    H3 = "LINEA"
    H4 = "SUBPROGRAMA"
    H5 = "META"


class CanonicalSection(Enum):
    """
    Canonical sections in PDM according to Ley 152/94.

    Every PDM must contain:
    - DIAGNOSTICO: Diagnostic analysis (current state)
    - PARTE_ESTRATEGICA: Strategic part (objectives, programs)
    - PLAN_PLURIANUAL: Pluriannual investment plan (PPI)
    - PLAN_FINANCIERO: Financial plan (optional but common)
    - SEGUIMIENTO: Monitoring and evaluation (optional)
    """
    DIAGNOSTICO = "diagnostico"
    PARTE_ESTRATEGICA = "parte_estrategica"
    PLAN_PLURIANUAL = "plan_plurianual_inversiones"
    PLAN_FINANCIERO = "plan_financiero"
    SEGUIMIENTO = "seguimiento_evaluacion"


class ContextualMarker(Enum):
    """
    P-D-Q markers for contextual classification.

    PDM content can be classified as:
    - P (Problem): Diagnostic, problems, gaps
    - D (Decision): Programs, projects, goals, decisions
    - Q (Quality): Indicators, metrics, baselines, targets
    """
    P = "problem"      # Diagnóstico, problemática
    D = "decision"     # Programa, proyecto, meta
    Q = "quality"      # Indicador, producto, resultado


@dataclass(frozen=True)
class TableSchema:
    """
    Schema for structured tables in PDM.

    PDM documents contain structured tables (PPI, Indicators, etc.)
    that must be detected and validated.
    """
    name: str
    required_columns: tuple[str, ...]
    optional_columns: tuple[str, ...]
    validation_rules: tuple[str, ...]

    def validate_table(self, table_data: dict) -> tuple[bool, list[str]]:
        """Validate table data against schema."""
        errors = []

        # Check required columns
        for col in self.required_columns:
            if col not in table_data:
                errors.append(f"Missing required column: {col}")

        return (len(errors) == 0, errors)


@dataclass(frozen=True)
class SemanticRule:
    """
    Semantic integrity rule for PDM content.

    Defines elements that must stay together (e.g., Meta + Indicador + Línea Base).
    Violation of CRITICAL rules → Phase 1 abort.
    """
    rule_id: str
    description: str
    elements: tuple[str, ...]
    violation_severity: Literal["CRITICAL", "HIGH", "STANDARD"]

    def check_violation(self, chunk_content: str) -> bool:
        """
        Check if rule is violated in chunk content.

        A rule is violated if some but not all elements are present.
        """
        elements_present = [elem in chunk_content for elem in self.elements]

        # If some but not all elements present → violation
        if any(elements_present) and not all(elements_present):
            return True

        return False


@dataclass(frozen=True)
class StructuralTransition:
    """
    Verifiable transition between PDM sections.

    Defines how to detect transitions (e.g., Diagnóstico → Estrategia)
    and validate structural coherence.
    """
    from_section: CanonicalSection
    to_section: CanonicalSection
    marker_patterns: tuple[str, ...]
    validation_hook: str  # Name of validation function

    def matches_transition(self, text: str) -> bool:
        """Check if text matches any transition pattern."""
        return any(re.search(pattern, text, re.IGNORECASE)
                  for pattern in self.marker_patterns)


@dataclass(frozen=True)
class PDMStructuralProfile:
    """
    CONSTITUTIONAL STRUCTURAL PROFILE for PDM documents.

    This profile defines how to interpret the internal structure of Colombian
    municipal development plans (PDM) according to Ley 152/94.

    CRITICAL: This profile is MANDATORY for Phase 1 execution.
    Absence → PrerequisiteError → ABORT Phase 1.

    SCOPE:
    - Does NOT alter: 60-chunk invariant, PA×Dim grid, FARFAN architecture
    - DOES define: Internal hierarchy, section boundaries, semantic rules,
                   causal patterns, table schemas

    Version: PDM-2025.1
    Compliance: Ley 152/94
    Methodology: MGA (Metodología General Ajustada) - DNP
    """

    # ==================== JERARQUÍA NORMATIVA ====================
    hierarchy_levels: tuple[HierarchyLevel, ...] = (
        HierarchyLevel.H1,
        HierarchyLevel.H2,
        HierarchyLevel.H3,
        HierarchyLevel.H4,
        HierarchyLevel.H5,
    )

    # ==================== SECCIONES CANÓNICAS ====================
    canonical_sections: dict[str, CanonicalSection] = field(default_factory=dict)
    # Mapping: section_name → CanonicalSection enum
    # Example: {"Parte I: Diagnóstico": CanonicalSection.DIAGNOSTICO}

    # ==================== PATRONES DE ENCABEZADO ====================
    header_patterns: dict[HierarchyLevel, tuple[Pattern, ...]] = field(
        default_factory=dict
    )
    # Example: H3 → [r"^\d+\.\d+\s+Programa:", r"^Línea\s+Estratégica\s+\d+"]

    # ==================== TRANSICIONES ESTRUCTURALES ====================
    transitions: tuple[StructuralTransition, ...] = field(default_factory=tuple)
    # Verifiable transitions: Diagnóstico → Estrategia → PPI → Seguimiento

    # ==================== CADENA DE VALOR DNP ====================
    causal_dimensions_patterns: dict[str, tuple[str, ...]] = field(
        default_factory=dict
    )
    # Mapping: CausalDimension → PDM-specific text patterns
    # Example: D1_INPUT → ("insumo", "recurso asignado", "presupuesto")
    #          D4_OUTPUT → ("producto", "entregable", "bien o servicio")
    #          D5_OUTCOME → ("resultado", "efecto", "cambio en población")

    # ==================== MARCADORES P-D-Q ====================
    contextual_markers: dict[ContextualMarker, tuple[str, ...]] = field(
        default_factory=dict
    )
    # Example: P → ("problemática", "situación actual", "brecha identificada")
    #          D → ("objetivo", "meta", "programa", "proyecto")
    #          Q → ("indicador", "métrica", "línea base", "meta cuantitativa")

    # ==================== LÍMITES SEMÁNTICOS ====================
    semantic_integrity_rules: tuple[SemanticRule, ...] = field(default_factory=tuple)
    # Non-separation rules:
    # - Meta + Indicador + Línea base + Meta cuantitativa (atomic unit)
    # - Programa + Objetivo + Subprogramas (hierarchy preserved)
    # - Diagnóstico sectorial + Árbol de problemas (causal context)

    # ==================== ESQUEMAS TABULARES ====================
    table_schemas: dict[str, TableSchema] = field(default_factory=dict)
    # Example: "PPI" → TableSchema(
    #         required_columns=("programa", "proyecto", "año_1", "año_2", ...),
    #         validation_rules=("sum_years == total_presupuesto",)
    #     )

    # ==================== METADATOS ====================
    profile_version: str = "PDM-2025.1"
    ley_152_compliance: bool = True
    dnp_methodology: str = "MGA"
    created_at: datetime = field(default_factory=datetime.now)

    def validate_integrity(self) -> tuple[bool, list[str]]:
        """
        Validate profile structural integrity.

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Check 1: Required canonical sections
        required_sections = {
            CanonicalSection.DIAGNOSTICO,
            CanonicalSection.PARTE_ESTRATEGICA,
            CanonicalSection.PLAN_PLURIANUAL,
        }
        section_values = set(self.canonical_sections.values())

        if not required_sections.issubset(section_values):
            missing = required_sections - section_values
            errors.append(f"Missing required canonical sections: {missing}")

        # Check 2: Structural transitions defined
        if len(self.transitions) == 0:
            errors.append("No structural transitions defined")

        # Check 3: CRITICAL semantic rules present
        critical_rules = [
            r for r in self.semantic_integrity_rules
            if r.violation_severity == "CRITICAL"
        ]
        if len(critical_rules) == 0:
            errors.append("No CRITICAL semantic rules defined")

        # Check 4: Causal dimension patterns defined
        if len(self.causal_dimensions_patterns) == 0:
            errors.append("No causal dimension patterns defined")

        # Check 5: Header patterns for hierarchy levels
        if len(self.header_patterns) == 0:
            errors.append("No header patterns for hierarchy levels")

        return (len(errors) == 0, errors)

    def get_section_for_marker(self, marker: ContextualMarker) -> CanonicalSection | None:
        """
        Determine which canonical section typically contains a marker type.

        Mapping:
        - P (Problem) → DIAGNOSTICO
        - D (Decision) → PARTE_ESTRATEGICA
        - Q (Quality) → Can be in PARTE_ESTRATEGICA or PLAN_PLURIANUAL
        """
        if marker == ContextualMarker.P:
            return CanonicalSection.DIAGNOSTICO
        elif marker == ContextualMarker.D:
            return CanonicalSection.PARTE_ESTRATEGICA
        elif marker == ContextualMarker.Q:
            return CanonicalSection.PARTE_ESTRATEGICA  # Default to strategic

        return None

    def check_semantic_violations(self, chunks: list[dict]) -> list[str]:
        """
        Check for semantic integrity violations across chunks.

        Returns:
            List of violation descriptions
        """
        violations = []

        for rule in self.semantic_integrity_rules:
            if rule.violation_severity == "CRITICAL":
                for chunk in chunks:
                    content = chunk.get("text", "")
                    if rule.check_violation(content):
                        violations.append(
                            f"CRITICAL: Rule {rule.rule_id} violated in chunk {chunk.get('chunk_id')}"
                        )

        return violations


def get_default_profile() -> PDMStructuralProfile:
    """
    Get default PDM structural profile with Colombian standard patterns.

    This profile is based on empirical analysis of Colombian PDM documents
    and DNP (Departamento Nacional de Planeación) guidelines.

    Returns:
        PDMStructuralProfile with standard Colombian PDM patterns
    """

    # Canonical sections mapping
    canonical_sections = {
        "Parte General": CanonicalSection.DIAGNOSTICO,
        "Parte Estratégica": CanonicalSection.PARTE_ESTRATEGICA,
        "Plan Plurianual de Inversiones": CanonicalSection.PLAN_PLURIANUAL,
        "Plan de Inversiones": CanonicalSection.PLAN_PLURIANUAL,
        "PPI": CanonicalSection.PLAN_PLURIANUAL,
        "Plan Financiero": CanonicalSection.PLAN_FINANCIERO,
        "Seguimiento y Evaluación": CanonicalSection.SEGUIMIENTO,
    }

    # Header patterns for hierarchy detection
    header_patterns = {
        HierarchyLevel.H1: (
            re.compile(r"^PARTE\s+[IVX]+", re.IGNORECASE),
            re.compile(r"^COMPONENTE\s+\d+", re.IGNORECASE),
        ),
        HierarchyLevel.H2: (
            re.compile(r"^CAP[IÍ]TULO\s+\d+", re.IGNORECASE),
            re.compile(r"^EJE\s+ESTRAT[ÉE]GICO\s+\d+", re.IGNORECASE),
            re.compile(r"^\d+\.\s+[A-ZÁÉÍÓÚÑ]", re.IGNORECASE),
        ),
        HierarchyLevel.H3: (
            re.compile(r"^L[IÍ]NEA\s+ESTRAT[ÉE]GICA", re.IGNORECASE),
            re.compile(r"^PROGRAMA\s+\d+", re.IGNORECASE),
            re.compile(r"^\d+\.\d+\s+[A-ZÁÉÍÓÚÑ]", re.IGNORECASE),
        ),
        HierarchyLevel.H4: (
            re.compile(r"^SUBPROGRAMA", re.IGNORECASE),
            re.compile(r"^PROYECTO", re.IGNORECASE),
            re.compile(r"^\d+\.\d+\.\d+\s+[A-ZÁÉÍÓÚÑ]", re.IGNORECASE),
        ),
        HierarchyLevel.H5: (
            re.compile(r"^META\s+\d+", re.IGNORECASE),
            re.compile(r"^INDICADOR", re.IGNORECASE),
            re.compile(r"^L[IÍ]NEA\s+BASE", re.IGNORECASE),
        ),
    }

    # Structural transitions
    transitions = (
        StructuralTransition(
            from_section=CanonicalSection.DIAGNOSTICO,
            to_section=CanonicalSection.PARTE_ESTRATEGICA,
            marker_patterns=(
                r"parte\s+estrat[ée]gica",
                r"componente\s+estrat[ée]gico",
                r"objetivos?\s+estrat[ée]gicos?",
            ),
            validation_hook="validate_diagnostic_to_strategic",
        ),
        StructuralTransition(
            from_section=CanonicalSection.PARTE_ESTRATEGICA,
            to_section=CanonicalSection.PLAN_PLURIANUAL,
            marker_patterns=(
                r"plan\s+plurianual\s+de\s+inversiones",
                r"ppi",
                r"plan\s+de\s+inversiones",
            ),
            validation_hook="validate_strategic_to_ppi",
        ),
    )

    # Causal dimension patterns (DNP value chain)
    causal_dimensions_patterns = {
        "D1_INPUT": (
            "insumo",
            "recurso",
            "presupuesto",
            "asignación",
            "financiamiento",
            "talento humano",
        ),
        "D2_ACTIVITY": (
            "actividad",
            "acción",
            "tarea",
            "intervención",
            "implementación",
        ),
        "D3_PROCESS": (
            "proceso",
            "gestión",
            "administración",
            "coordinación",
            "seguimiento",
        ),
        "D4_OUTPUT": (
            "producto",
            "entregable",
            "bien",
            "servicio prestado",
            "unidad entregada",
        ),
        "D5_OUTCOME": (
            "resultado",
            "efecto",
            "cambio",
            "mejora",
            "población beneficiada",
            "impacto en",
        ),
        "D6_IMPACT": (
            "impacto",
            "transformación",
            "desarrollo sostenible",
            "bienestar",
            "calidad de vida",
        ),
    }

    # Contextual markers (P-D-Q)
    contextual_markers = {
        ContextualMarker.P: (
            "problemática",
            "situación actual",
            "brecha",
            "déficit",
            "necesidad insatisfecha",
            "diagnóstico",
            "análisis situacional",
        ),
        ContextualMarker.D: (
            "objetivo",
            "meta",
            "programa",
            "proyecto",
            "estrategia",
            "línea de acción",
            "decisión",
        ),
        ContextualMarker.Q: (
            "indicador",
            "métrica",
            "línea base",
            "meta cuantitativa",
            "medición",
            "valor esperado",
            "fuente de verificación",
        ),
    }

    # Semantic integrity rules
    semantic_integrity_rules = (
        SemanticRule(
            rule_id="SEM-01-CRITICAL",
            description="Meta + Indicador + Línea Base must stay together",
            elements=("meta", "indicador", "línea base"),
            violation_severity="CRITICAL",
        ),
        SemanticRule(
            rule_id="SEM-02-HIGH",
            description="Programa + Objetivo + Subprogramas hierarchy preserved",
            elements=("programa", "objetivo", "subprograma"),
            violation_severity="HIGH",
        ),
        SemanticRule(
            rule_id="SEM-03-HIGH",
            description="Indicador + Fórmula + Fuente verification",
            elements=("indicador", "fórmula", "fuente"),
            violation_severity="HIGH",
        ),
        SemanticRule(
            rule_id="SEM-04-STANDARD",
            description="Proyecto + Monto + Fuente financiamiento",
            elements=("proyecto", "monto", "fuente"),
            violation_severity="STANDARD",
        ),
    )

    # Table schemas
    table_schemas = {
        "PPI": TableSchema(
            name="Plan Plurianual de Inversiones",
            required_columns=("programa", "proyecto", "año_1", "año_2", "año_3", "año_4"),
            optional_columns=("fuente", "responsable", "total"),
            validation_rules=("sum(años) == total", "all(montos) >= 0"),
        ),
        "INDICADORES": TableSchema(
            name="Matriz de Indicadores",
            required_columns=("indicador", "linea_base", "meta", "fuente"),
            optional_columns=("formula", "responsable", "periodicidad"),
            validation_rules=("meta != linea_base", "fuente not empty"),
        ),
        "PROGRAMAS": TableSchema(
            name="Estructura Programática",
            required_columns=("eje", "programa", "objetivo"),
            optional_columns=("subprogramas", "proyectos", "presupuesto"),
            validation_rules=("objetivo not empty",),
        ),
    }

    return PDMStructuralProfile(
        hierarchy_levels=(
            HierarchyLevel.H1,
            HierarchyLevel.H2,
            HierarchyLevel.H3,
            HierarchyLevel.H4,
            HierarchyLevel.H5,
        ),
        canonical_sections=canonical_sections,
        header_patterns=header_patterns,
        transitions=transitions,
        causal_dimensions_patterns=causal_dimensions_patterns,
        contextual_markers=contextual_markers,
        semantic_integrity_rules=semantic_integrity_rules,
        table_schemas=table_schemas,
        profile_version="PDM-2025.1",
        ley_152_compliance=True,
        dnp_methodology="MGA",
    )
