"""
Tests for PDM Structural Profile.

Validates PDM structural recognition according to Ley 152/94.
"""

import pytest

from farfan_pipeline.infrastructure.parametrization.pdm_structural_profile import (
    CanonicalSection,
    ContextualMarker,
    HierarchyLevel,
    PDMStructuralProfile,
    SemanticRule,
    StructuralTransition,
    TableSchema,
    get_default_profile,
)


class TestHierarchyLevel:
    """Test hierarchy level enum."""

    def test_hierarchy_levels_exist(self):
        """Verify all 5 hierarchy levels exist."""
        assert HierarchyLevel.H1.value == "PARTE"
        assert HierarchyLevel.H2.value == "CAPITULO"
        assert HierarchyLevel.H3.value == "LINEA"
        assert HierarchyLevel.H4.value == "SUBPROGRAMA"
        assert HierarchyLevel.H5.value == "META"


class TestCanonicalSection:
    """Test canonical sections enum."""

    def test_canonical_sections_exist(self):
        """Verify required canonical sections exist."""
        assert CanonicalSection.DIAGNOSTICO.value == "diagnostico"
        assert CanonicalSection.PARTE_ESTRATEGICA.value == "parte_estrategica"
        assert CanonicalSection.PLAN_PLURIANUAL.value == "plan_plurianual_inversiones"


class TestContextualMarker:
    """Test P-D-Q contextual markers."""

    def test_pdq_markers_exist(self):
        """Verify P-D-Q markers exist."""
        assert ContextualMarker.P.value == "problem"
        assert ContextualMarker.D.value == "decision"
        assert ContextualMarker.Q.value == "quality"


class TestTableSchema:
    """Test table schema validation."""

    def test_table_schema_creation(self):
        """Test creating a table schema."""
        schema = TableSchema(
            name="PPI",
            required_columns=("programa", "proyecto", "año_1"),
            optional_columns=("fuente",),
            validation_rules=("sum_years == total",),
        )

        assert schema.name == "PPI"
        assert "programa" in schema.required_columns
        assert "fuente" in schema.optional_columns

    def test_table_schema_validation(self):
        """Test table schema validation."""
        schema = TableSchema(
            name="Test",
            required_columns=("col1", "col2"),
            optional_columns=(),
            validation_rules=(),
        )

        # Valid table
        valid_table = {"col1": "value1", "col2": "value2"}
        is_valid, errors = schema.validate_table(valid_table)
        assert is_valid
        assert len(errors) == 0

        # Invalid table (missing column)
        invalid_table = {"col1": "value1"}
        is_valid, errors = schema.validate_table(invalid_table)
        assert not is_valid
        assert len(errors) > 0


class TestSemanticRule:
    """Test semantic integrity rules."""

    def test_semantic_rule_creation(self):
        """Test creating a semantic rule."""
        rule = SemanticRule(
            rule_id="SEM-01",
            description="Test rule",
            elements=("meta", "indicador"),
            violation_severity="CRITICAL",
        )

        assert rule.rule_id == "SEM-01"
        assert rule.violation_severity == "CRITICAL"

    def test_semantic_rule_violation_detection(self):
        """Test violation detection."""
        rule = SemanticRule(
            rule_id="SEM-01",
            description="Meta + Indicador must stay together",
            elements=("meta", "indicador", "línea base"),
            violation_severity="CRITICAL",
        )

        # No violation (all present)
        text_complete = "La meta es 100. El indicador es X. La línea base es 50."
        assert not rule.check_violation(text_complete)

        # No violation (none present)
        text_none = "Este es un texto sin elementos."
        assert not rule.check_violation(text_none)

        # Violation (partial presence)
        text_partial = "La meta es 100. El indicador es X."
        assert rule.check_violation(text_partial)


class TestStructuralTransition:
    """Test structural transitions."""

    def test_transition_matching(self):
        """Test transition pattern matching."""
        transition = StructuralTransition(
            from_section=CanonicalSection.DIAGNOSTICO,
            to_section=CanonicalSection.PARTE_ESTRATEGICA,
            marker_patterns=(r"parte\s+estratégica", r"objetivos?\s+estratégicos?"),
            validation_hook="validate_diagnostic_to_strategic",
        )

        assert transition.matches_transition("PARTE ESTRATÉGICA")
        assert transition.matches_transition("Objetivos estratégicos")
        assert not transition.matches_transition("Plan de inversiones")


class TestPDMStructuralProfile:
    """Test PDM structural profile."""

    def test_profile_creation(self):
        """Test creating a minimal profile."""
        profile = PDMStructuralProfile(
            canonical_sections={
                "Diagnóstico": CanonicalSection.DIAGNOSTICO,
                "Estrategia": CanonicalSection.PARTE_ESTRATEGICA,
                "PPI": CanonicalSection.PLAN_PLURIANUAL,
            },
            transitions=(
                StructuralTransition(
                    from_section=CanonicalSection.DIAGNOSTICO,
                    to_section=CanonicalSection.PARTE_ESTRATEGICA,
                    marker_patterns=("estrategia",),
                    validation_hook="test",
                ),
            ),
            semantic_integrity_rules=(
                SemanticRule(
                    rule_id="TEST",
                    description="Test",
                    elements=("a", "b"),
                    violation_severity="CRITICAL",
                ),
            ),
            causal_dimensions_patterns={"D1": ("test",)},
            header_patterns={HierarchyLevel.H1: (r"^PARTE",)},
        )

        assert profile.profile_version == "PDM-2025.1"
        assert profile.ley_152_compliance is True
        assert profile.dnp_methodology == "MGA"

    def test_profile_validation_success(self):
        """Test profile validation with valid profile."""
        profile = PDMStructuralProfile(
            canonical_sections={
                "Diagnóstico": CanonicalSection.DIAGNOSTICO,
                "Estrategia": CanonicalSection.PARTE_ESTRATEGICA,
                "PPI": CanonicalSection.PLAN_PLURIANUAL,
            },
            transitions=(
                StructuralTransition(
                    from_section=CanonicalSection.DIAGNOSTICO,
                    to_section=CanonicalSection.PARTE_ESTRATEGICA,
                    marker_patterns=("test",),
                    validation_hook="test",
                ),
            ),
            semantic_integrity_rules=(
                SemanticRule(
                    rule_id="TEST",
                    description="Test",
                    elements=("a",),
                    violation_severity="CRITICAL",
                ),
            ),
            causal_dimensions_patterns={"D1": ("test",)},
            header_patterns={HierarchyLevel.H1: (r"test",)},
        )

        is_valid, errors = profile.validate_integrity()
        assert is_valid
        assert len(errors) == 0

    def test_profile_validation_failure_missing_sections(self):
        """Test profile validation fails with missing sections."""
        profile = PDMStructuralProfile(
            canonical_sections={},  # Missing required sections
            transitions=(
                StructuralTransition(
                    from_section=CanonicalSection.DIAGNOSTICO,
                    to_section=CanonicalSection.PARTE_ESTRATEGICA,
                    marker_patterns=("test",),
                    validation_hook="test",
                ),
            ),
            semantic_integrity_rules=(
                SemanticRule(
                    rule_id="TEST",
                    description="Test",
                    elements=("a",),
                    violation_severity="CRITICAL",
                ),
            ),
        )

        is_valid, errors = profile.validate_integrity()
        assert not is_valid
        assert any("Missing required canonical sections" in err for err in errors)

    def test_get_section_for_marker(self):
        """Test mapping markers to sections."""
        profile = get_default_profile()

        assert profile.get_section_for_marker(ContextualMarker.P) == CanonicalSection.DIAGNOSTICO
        assert (
            profile.get_section_for_marker(ContextualMarker.D)
            == CanonicalSection.PARTE_ESTRATEGICA
        )
        assert (
            profile.get_section_for_marker(ContextualMarker.Q)
            == CanonicalSection.PARTE_ESTRATEGICA
        )


class TestDefaultProfile:
    """Test default PDM profile."""

    def test_default_profile_exists(self):
        """Test that default profile can be loaded."""
        profile = get_default_profile()
        assert profile is not None
        assert isinstance(profile, PDMStructuralProfile)

    def test_default_profile_valid(self):
        """Test that default profile is valid."""
        profile = get_default_profile()
        is_valid, errors = profile.validate_integrity()
        assert is_valid, f"Default profile invalid: {errors}"

    def test_default_profile_has_required_sections(self):
        """Test default profile has required canonical sections."""
        profile = get_default_profile()

        section_values = set(profile.canonical_sections.values())
        assert CanonicalSection.DIAGNOSTICO in section_values
        assert CanonicalSection.PARTE_ESTRATEGICA in section_values
        assert CanonicalSection.PLAN_PLURIANUAL in section_values

    def test_default_profile_has_hierarchy_patterns(self):
        """Test default profile has hierarchy patterns."""
        profile = get_default_profile()

        assert len(profile.header_patterns) > 0
        assert HierarchyLevel.H1 in profile.header_patterns
        assert HierarchyLevel.H2 in profile.header_patterns
        assert HierarchyLevel.H3 in profile.header_patterns

    def test_default_profile_has_causal_patterns(self):
        """Test default profile has causal dimension patterns."""
        profile = get_default_profile()

        assert len(profile.causal_dimensions_patterns) > 0
        assert "D1_INPUT" in profile.causal_dimensions_patterns
        assert "D4_OUTPUT" in profile.causal_dimensions_patterns
        assert "D5_OUTCOME" in profile.causal_dimensions_patterns

    def test_default_profile_has_semantic_rules(self):
        """Test default profile has semantic integrity rules."""
        profile = get_default_profile()

        assert len(profile.semantic_integrity_rules) > 0

        # At least one CRITICAL rule
        critical_rules = [
            r for r in profile.semantic_integrity_rules if r.violation_severity == "CRITICAL"
        ]
        assert len(critical_rules) > 0

    def test_default_profile_has_table_schemas(self):
        """Test default profile has table schemas."""
        profile = get_default_profile()

        assert len(profile.table_schemas) > 0
        assert "PPI" in profile.table_schemas
        assert "INDICADORES" in profile.table_schemas

    def test_default_profile_has_transitions(self):
        """Test default profile has structural transitions."""
        profile = get_default_profile()

        assert len(profile.transitions) > 0

        # Should have at least diagnostic → strategic transition
        has_diag_to_strat = any(
            t.from_section == CanonicalSection.DIAGNOSTICO
            and t.to_section == CanonicalSection.PARTE_ESTRATEGICA
            for t in profile.transitions
        )
        assert has_diag_to_strat


class TestPDMMetadataIntegration:
    """Test PDM metadata integration with Phase 1 models."""

    def test_pdm_metadata_import(self):
        """Test that PDMMetadata can be imported from phase1_models."""
        try:
            from farfan_pipeline.phases.Phase_1.phase1_03_00_models import PDMMetadata

            assert PDMMetadata is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PDMMetadata: {e}")

    def test_pdm_metadata_in_smart_chunk(self):
        """Test that SmartChunk has pdm_metadata field."""
        try:
            from farfan_pipeline.phases.Phase_1.phase1_03_00_models import SmartChunk

            # Check field exists
            assert hasattr(SmartChunk, "__dataclass_fields__")
            fields = SmartChunk.__dataclass_fields__
            assert "pdm_metadata" in fields
        except ImportError as e:
            pytest.fail(f"Failed to import SmartChunk: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
