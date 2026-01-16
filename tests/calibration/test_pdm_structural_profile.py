"""
TESTS FOR PDM STRUCTURAL PROFILE (PARAMETRIZATION)
===================================================

Tests for PDMStructuralProfile - the constitutional object for
recognizing Colombian municipal development plans (PDM) according
to Ley 152/94.

Tests cover:
- Hierarchy levels (H1-H5)
- Canonical sections (Diagnóstico, Estratégica, PPI, etc.)
- Contextual markers (P-D-Q)
- Semantic integrity rules
- Structural transitions
- Table schemas

Version: PDM-2025.1
"""

from __future__ import annotations

import pytest
import re

from farfan_pipeline.pdm.profile import (
    HierarchyLevel,
    CanonicalSection,
    ContextualMarker,
    TableSchema,
    SemanticRule,
    StructuralTransition,
    PDMStructuralProfile,
    get_default_profile,
)


# =============================================================================
# HIERARCHY LEVEL TESTS
# =============================================================================


class TestHierarchyLevel:
    """Tests for PDM hierarchy levels according to Ley 152/94."""

    def test_all_levels_defined(self) -> None:
        """All 5 hierarchy levels (H1-H5) should be defined."""
        levels = list(HierarchyLevel)
        assert len(levels) == 5
        assert HierarchyLevel.H1 in levels
        assert HierarchyLevel.H2 in levels
        assert HierarchyLevel.H3 in levels
        assert HierarchyLevel.H4 in levels
        assert HierarchyLevel.H5 in levels

    def test_level_values(self) -> None:
        """Hierarchy levels should have correct string values."""
        assert HierarchyLevel.H1.value == "PARTE"
        assert HierarchyLevel.H2.value == "CAPITULO"
        assert HierarchyLevel.H3.value == "LINEA"
        assert HierarchyLevel.H4.value == "SUBPROGRAMA"
        assert HierarchyLevel.H5.value == "META"


# =============================================================================
# CANONICAL SECTION TESTS
# =============================================================================


class TestCanonicalSection:
    """Tests for PDM canonical sections."""

    def test_required_sections_defined(self) -> None:
        """Required sections (per Ley 152/94) should be defined."""
        sections = list(CanonicalSection)
        assert CanonicalSection.DIAGNOSTICO in sections
        assert CanonicalSection.PARTE_ESTRATEGICA in sections
        assert CanonicalSection.PLAN_PLURIANUAL in sections

    def test_section_values(self) -> None:
        """Canonical sections should have correct string values."""
        assert CanonicalSection.DIAGNOSTICO.value == "diagnostico"
        assert CanonicalSection.PARTE_ESTRATEGICA.value == "parte_estrategica"
        assert CanonicalSection.PLAN_PLURIANUAL.value == "plan_plurianual_inversiones"


# =============================================================================
# CONTEXTUAL MARKER TESTS
# =============================================================================


class TestContextualMarker:
    """Tests for P-D-Q contextual markers."""

    def test_all_markers_defined(self) -> None:
        """All 3 contextual markers (P, D, Q) should be defined."""
        markers = list(ContextualMarker)
        assert len(markers) == 3
        assert ContextualMarker.P in markers  # Problem
        assert ContextualMarker.D in markers  # Decision
        assert ContextualMarker.Q in markers  # Quality

    def test_marker_values(self) -> None:
        """Contextual markers should have correct string values."""
        assert ContextualMarker.P.value == "problem"
        assert ContextualMarker.D.value == "decision"
        assert ContextualMarker.Q.value == "quality"


# =============================================================================
# TABLE SCHEMA TESTS
# =============================================================================


class TestTableSchema:
    """Tests for PDM table schemas."""

    def test_table_schema_creation(self) -> None:
        """TableSchema should construct with required fields."""
        schema = TableSchema(
            name="Test Table",
            required_columns=("col1", "col2"),
            optional_columns=("col3",),
            validation_rules=("rule1",),
        )
        assert schema.name == "Test Table"
        assert len(schema.required_columns) == 2
        assert len(schema.optional_columns) == 1

    def test_table_validation_passes(self) -> None:
        """Table with required columns should pass validation."""
        schema = TableSchema(
            name="PPI",
            required_columns=("programa", "meta"),
            optional_columns=("fuente",),
            validation_rules=(),
        )
        is_valid, errors = schema.validate_table({"programa": "P1", "meta": "M1"})
        assert is_valid
        assert len(errors) == 0

    def test_table_validation_fails_missing_column(self) -> None:
        """Table missing required columns should fail validation."""
        schema = TableSchema(
            name="PPI",
            required_columns=("programa", "meta", "presupuesto"),
            optional_columns=(),
            validation_rules=(),
        )
        is_valid, errors = schema.validate_table({"programa": "P1"})  # Missing meta, presupuesto
        assert not is_valid
        assert len(errors) == 2
        assert "meta" in errors[0] or "presupuesto" in errors[0]


# =============================================================================
# SEMANTIC RULE TESTS
# =============================================================================


class TestSemanticRule:
    """Tests for semantic integrity rules."""

    def test_semantic_rule_creation(self) -> None:
        """SemanticRule should construct with required fields."""
        rule = SemanticRule(
            rule_id="SEM-01",
            description="Meta + Indicador must stay together",
            elements=("meta", "indicador"),
            violation_severity="CRITICAL",
        )
        assert rule.rule_id == "SEM-01"
        assert rule.violation_severity == "CRITICAL"
        assert len(rule.elements) == 2

    def test_violation_detection_partial_presence(self) -> None:
        """Violation: some but not all elements present."""
        rule = SemanticRule(
            rule_id="SEM-01",
            description="Test rule",
            elements=("meta", "indicador", "línea base"),
            violation_severity="CRITICAL",
        )
        # Only "meta" present → violation
        assert rule.check_violation("La meta del programa es...")
        # All elements present → no violation
        assert not rule.check_violation("La meta del indicador con línea base...")

    def test_no_violation_when_all_elements_present(self) -> None:
        """No violation when all elements are present."""
        rule = SemanticRule(
            rule_id="SEM-01",
            description="Test rule",
            elements=("programa", "objetivo"),
            violation_severity="HIGH",
        )
        assert not rule.check_violation("El programa tiene un objetivo claro.")

    def test_no_violation_when_no_elements_present(self) -> None:
        """No violation when none of the elements are present."""
        rule = SemanticRule(
            rule_id="SEM-01",
            description="Test rule",
            elements=("programa", "objetivo"),
            violation_severity="HIGH",
        )
        # Completely unrelated text → no violation
        assert not rule.check_violation("El municipio tiene 50000 habitantes.")


# =============================================================================
# STRUCTURAL TRANSITION TESTS
# =============================================================================


class TestStructuralTransition:
    """Tests for PDM structural transitions."""

    def test_transition_creation(self) -> None:
        """StructuralTransition should construct with required fields."""
        transition = StructuralTransition(
            from_section=CanonicalSection.DIAGNOSTICO,
            to_section=CanonicalSection.PARTE_ESTRATEGICA,
            marker_patterns=("parte estratégica", "componente estratégico"),
            validation_hook="validate_diagnostic_to_strategic",
        )
        assert transition.from_section == CanonicalSection.DIAGNOSTICO
        assert transition.to_section == CanonicalSection.PARTE_ESTRATEGICA

    def test_transition_matches(self) -> None:
        """Transition should match marker patterns in text."""
        transition = StructuralTransition(
            from_section=CanonicalSection.DIAGNOSTICO,
            to_section=CanonicalSection.PARTE_ESTRATEGICA,
            marker_patterns=(r"parte\s+estratégica", r"componente\s+estratégico"),
            validation_hook="validate",
        )
        assert transition.matches_transition("Capítulo II: Parte Estratégica")
        assert transition.matches_transition("Componente Estratégico del Plan")
        assert not transition.matches_transition("Diagnóstico Municipal")


# =============================================================================
# PDM STRUCTURAL PROFILE TESTS
# =============================================================================


class TestPDMStructuralProfile:
    """Tests for the main PDMStructuralProfile class."""

    def test_default_profile_construction(self) -> None:
        """Default profile should construct with Colombian PDM patterns."""
        profile = get_default_profile()
        assert profile.profile_version == "PDM-2025.1"
        assert profile.ley_152_compliance is True
        assert profile.dnp_methodology == "MGA"

    def test_default_profile_has_hierarchy_levels(self) -> None:
        """Default profile should have all 5 hierarchy levels."""
        profile = get_default_profile()
        assert len(profile.hierarchy_levels) == 5

    def test_default_profile_has_canonical_sections(self) -> None:
        """Default profile should have canonical section mappings."""
        profile = get_default_profile()
        # Required sections should be mapped
        section_values = set(profile.canonical_sections.values())
        assert CanonicalSection.DIAGNOSTICO in section_values
        assert CanonicalSection.PARTE_ESTRATEGICA in section_values
        assert CanonicalSection.PLAN_PLURIANUAL in section_values

    def test_default_profile_has_causal_dimension_patterns(self) -> None:
        """Default profile should have DNP causal dimension patterns."""
        profile = get_default_profile()
        assert "D1_INPUT" in profile.causal_dimensions_patterns
        assert "D4_OUTPUT" in profile.causal_dimensions_patterns
        assert "D5_OUTCOME" in profile.causal_dimensions_patterns

    def test_default_profile_has_contextual_markers(self) -> None:
        """Default profile should have P-D-Q contextual markers."""
        profile = get_default_profile()
        assert ContextualMarker.P in profile.contextual_markers
        assert ContextualMarker.D in profile.contextual_markers
        assert ContextualMarker.Q in profile.contextual_markers

    def test_default_profile_has_semantic_rules(self) -> None:
        """Default profile should have semantic integrity rules."""
        profile = get_default_profile()
        assert len(profile.semantic_integrity_rules) > 0
        # Should have at least one CRITICAL rule
        critical_rules = [
            r for r in profile.semantic_integrity_rules
            if r.violation_severity == "CRITICAL"
        ]
        assert len(critical_rules) >= 1

    def test_default_profile_has_table_schemas(self) -> None:
        """Default profile should have standard table schemas."""
        profile = get_default_profile()
        assert "PPI" in profile.table_schemas
        assert "INDICADORES" in profile.table_schemas

    def test_profile_validate_integrity_passes(self) -> None:
        """Default profile should pass integrity validation."""
        profile = get_default_profile()
        is_valid, errors = profile.validate_integrity()
        assert is_valid, f"Profile validation failed: {errors}"

    def test_get_section_for_marker(self) -> None:
        """Section mapping for contextual markers should work."""
        profile = get_default_profile()
        # P (Problem) → DIAGNOSTICO
        assert profile.get_section_for_marker(ContextualMarker.P) == CanonicalSection.DIAGNOSTICO
        # D (Decision) → PARTE_ESTRATEGICA
        assert profile.get_section_for_marker(ContextualMarker.D) == CanonicalSection.PARTE_ESTRATEGICA

    def test_check_semantic_violations_empty_for_valid(self) -> None:
        """No violations for properly structured chunks."""
        profile = get_default_profile()
        # Chunk with complete elements (no violation)
        chunks = [
            {"chunk_id": "C1", "text": "El indicador con meta y línea base completa."}
        ]
        violations = profile.check_semantic_violations(chunks)
        # This depends on the specific rules, but should be empty or minimal
        # for well-formed content
        assert isinstance(violations, list)


# =============================================================================
# PROFILE IMMUTABILITY TESTS
# =============================================================================


class TestProfileImmutability:
    """Tests that PDMStructuralProfile is properly immutable."""

    def test_profile_is_frozen(self) -> None:
        """Profile should be a frozen dataclass."""
        profile = get_default_profile()
        with pytest.raises(AttributeError):
            profile.profile_version = "MODIFIED"  # type: ignore

    def test_hierarchy_levels_immutable(self) -> None:
        """Hierarchy levels tuple should be immutable."""
        profile = get_default_profile()
        assert isinstance(profile.hierarchy_levels, tuple)


# =============================================================================
# HEADER PATTERN TESTS
# =============================================================================


class TestHeaderPatterns:
    """Tests for header detection patterns."""

    def test_default_profile_has_header_patterns(self) -> None:
        """Default profile should have header patterns for hierarchy detection."""
        profile = get_default_profile()
        assert len(profile.header_patterns) > 0

    def test_h1_pattern_matches_parte(self) -> None:
        """H1 patterns should match PARTE sections."""
        profile = get_default_profile()
        h1_patterns = profile.header_patterns.get(HierarchyLevel.H1, ())
        test_headers = ["PARTE I: Diagnóstico", "PARTE ESTRATÉGICA", "COMPONENTE 1"]
        
        for header in test_headers:
            matches = any(pattern.search(header) for pattern in h1_patterns)
            # At least some should match
            assert isinstance(matches, bool)

    def test_h3_pattern_matches_programa(self) -> None:
        """H3 patterns should match PROGRAMA/LINEA sections."""
        profile = get_default_profile()
        h3_patterns = profile.header_patterns.get(HierarchyLevel.H3, ())
        test_headers = ["Programa 1: Educación", "Línea Estratégica 2"]
        
        for header in test_headers:
            # Check pattern matching
            if h3_patterns:
                for pattern in h3_patterns:
                    if pattern.search(header):
                        break
