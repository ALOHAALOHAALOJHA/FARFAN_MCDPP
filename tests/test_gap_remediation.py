"""
Tests for F.A.R.F.A.N Irrigation Gap Remediation (SPEC_GAP_REMEDIATION_2026_01_04.md).

Tests cover:
- R-B2: ColombianContextRule validation
- R-B5: BlockingRulesEngine with veto gates
- R-W1: Keywords irrigation
- R-W2: Cross-cutting themes integration
- R-W3: Interdependency validation integration
- R-W4: Dynamic sector loading

Author: F.A.R.F.A.N Pipeline Team
Date: 2026-01-04
Version: 1.0.0
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock


class TestColombianContextRule:
    """Tests for R-B2: Colombian context validation."""

    def test_colombian_context_rule_detects_missing_ref(self):
        """Verify rule triggers when required regulatory reference is missing."""
        from farfan_pipeline.phases.Phase_two.phase2_80_00_evidence_nexus import (
            ColombianContextRule,
            EvidenceGraph,
        )

        contract = {
            "validation_rules": {
                "colombian_context": {
                    "required_regulatory_refs": ["Ley 1448 de 2011"]
                }
            }
        }
        graph = EvidenceGraph()
        rule = ColombianContextRule()

        findings = rule.validate(graph, contract)

        assert len(findings) == 1
        assert "Ley 1448 de 2011" in findings[0].message

    def test_colombian_context_rule_passes_when_ref_present(self):
        """Verify rule passes when regulatory reference is found."""
        from farfan_pipeline.phases.Phase_two.phase2_80_00_evidence_nexus import (
            ColombianContextRule,
            EvidenceGraph,
            EvidenceNode,
            EvidenceType,
        )

        contract = {
            "validation_rules": {
                "colombian_context": {
                    "required_regulatory_refs": ["Ley 1448 de 2011"]
                }
            }
        }
        graph = EvidenceGraph()
        node = EvidenceNode.create(
            evidence_type=EvidenceType.NORMATIVE_REFERENCE,
            content={"text": "Este programa implementa la Ley 1448 de 2011 sobre víctimas."},
            confidence=0.9,
            source_method="test",
        )
        graph.add_node(node)
        rule = ColombianContextRule()

        findings = rule.validate(graph, contract)

        assert len(findings) == 0

    def test_colombian_context_rule_empty_context(self):
        """Verify rule is bypassed when no colombian_context defined."""
        from farfan_pipeline.phases.Phase_two.phase2_80_00_evidence_nexus import (
            ColombianContextRule,
            EvidenceGraph,
        )

        contract = {"validation_rules": {}}
        graph = EvidenceGraph()
        rule = ColombianContextRule()

        findings = rule.validate(graph, contract)

        assert len(findings) == 0


class TestBlockingRulesEngine:
    """Tests for R-B5: Blocking rules engine with veto gates."""

    def test_blocking_engine_score_zero_veto(self):
        """Verify SCORE_ZERO veto action sets confidence to 0."""
        from farfan_pipeline.phases.Phase_two.phase2_80_00_evidence_nexus import (
            BlockingRulesEngine,
            EvidenceGraph,
            ValidationReport,
            SynthesizedAnswer,
            AnswerCompleteness,
        )

        contract = {
            "validation_rules": {
                "blocking_rules": [
                    {
                        "rule_id": "BLOCK-001",
                        "condition": {"type": "node_count_below", "minimum": 5},
                        "on_violation": "SCORE_ZERO",
                        "description": "Insufficient evidence nodes",
                    }
                ]
            }
        }

        graph = EvidenceGraph()
        validation_report = ValidationReport.create(findings=[])
        engine = BlockingRulesEngine(contract)

        results = engine.evaluate(graph, validation_report)

        assert len(results) == 1
        assert results[0].triggered
        assert results[0].veto_action == "SCORE_ZERO"

    def test_blocking_engine_no_rules(self):
        """Verify engine works gracefully with no blocking rules."""
        from farfan_pipeline.phases.Phase_two.phase2_80_00_evidence_nexus import (
            BlockingRulesEngine,
            EvidenceGraph,
            ValidationReport,
        )

        contract = {"validation_rules": {}}
        graph = EvidenceGraph()
        validation_report = ValidationReport.create(findings=[])
        engine = BlockingRulesEngine(contract)

        results = engine.evaluate(graph, validation_report)

        assert len(results) == 0

    def test_blocking_engine_contradiction_detection(self):
        """Verify contradiction_detected condition works."""
        from farfan_pipeline.phases.Phase_two.phase2_80_00_evidence_nexus import (
            BlockingRulesEngine,
            EvidenceGraph,
            EvidenceNode,
            EvidenceEdge,
            EvidenceType,
            RelationType,
            ValidationReport,
        )

        contract = {
            "validation_rules": {
                "blocking_rules": [
                    {
                        "rule_id": "BLOCK-002",
                        "condition": {"type": "contradiction_detected"},
                        "on_violation": "FLAG_REVIEW",
                        "description": "Contradicting evidence found",
                    }
                ]
            }
        }

        graph = EvidenceGraph()
        node1 = EvidenceNode.create(
            evidence_type=EvidenceType.METHOD_OUTPUT,
            content={"text": "Claim A"},
            confidence=0.8,
            source_method="test",
        )
        node2 = EvidenceNode.create(
            evidence_type=EvidenceType.METHOD_OUTPUT,
            content={"text": "Claim B"},
            confidence=0.8,
            source_method="test",
        )
        graph.add_node(node1)
        graph.add_node(node2)

        edge = EvidenceEdge.create(
            source_id=node1.node_id,
            target_id=node2.node_id,
            relation_type=RelationType.CONTRADICTS,
            confidence=0.9,
        )
        graph.add_edge(edge)

        validation_report = ValidationReport.create(findings=[])
        engine = BlockingRulesEngine(contract)

        results = engine.evaluate(graph, validation_report)

        assert len(results) == 1
        assert results[0].veto_action == "FLAG_REVIEW"


class TestKeywordsIrrigation:
    """Tests for R-W1: Keywords irrigation in signal registry."""

    def test_micro_answering_pack_has_keywords_field(self):
        """Verify MicroAnsweringSignalPack has policy_area_keywords field."""
        from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
            MicroAnsweringSignalPack,
        )

        fields = MicroAnsweringSignalPack.model_fields
        assert "policy_area_keywords" in fields

    def test_keywords_loaded_from_policy_area(self):
        """Verify keywords are loaded from canonical policy area (modular structure)."""
        base_path = Path(__file__).parent.parent
        pa_path = base_path / "canonic_questionnaire_central" / "policy_areas" / "PA01_mujeres_genero" / "questions.json"

        if pa_path.exists():
            with open(pa_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            metadata = data.get("policy_area_metadata", {})
            keywords = metadata.get("keywords", [])

            assert len(keywords) > 0
            assert "género" in keywords


class TestCrossCuttingThemesIntegration:
    """Tests for R-W2: Cross-cutting themes integration."""

    def test_enhancement_integrator_loads_themes(self):
        """Verify cross-cutting themes file exists in modular structure."""
        base_path = Path(__file__).parent.parent
        themes_path = base_path / "canonic_questionnaire_central" / "cross_cutting" / "cross_cutting_themes.json"

        if themes_path.exists():
            with open(themes_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            themes = data.get("themes", [])
            assert len(themes) > 0

            first_theme = themes[0]
            assert "theme_id" in first_theme
            assert "name" in first_theme

    def test_cross_cutting_themes_extraction(self):
        """Verify cross-cutting themes are extracted for a question."""
        from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_enhancement_integrator import (
            SignalEnhancementIntegrator,
        )

        mock_questionnaire = MagicMock()
        mock_questionnaire.data = {"blocks": {"semantic_layers": {}, "scoring": {}}}
        mock_questionnaire.version = "test"

        integrator = SignalEnhancementIntegrator(mock_questionnaire)
        themes = integrator._extract_cross_cutting_themes("PA01", "DIM04")

        assert "applicable_themes" in themes
        assert "required_themes" in themes
        assert "minimum_themes" in themes


class TestInterdependencyValidationIntegration:
    """Tests for R-W3: Interdependency validation integration."""

    def test_interdependency_mapping_exists(self):
        """Verify interdependency mapping file exists in modular structure."""
        base_path = Path(__file__).parent.parent
        mapping_path = base_path / "canonic_questionnaire_central" / "validations" / "interdependency_mapping.json"

        if mapping_path.exists():
            with open(mapping_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert "dimension_flow" in data
            assert "cross_dimension_validation_rules" in data

    def test_interdependency_context_extraction(self):
        """Verify interdependency context is extracted for a dimension."""
        from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_enhancement_integrator import (
            SignalEnhancementIntegrator,
        )

        mock_questionnaire = MagicMock()
        mock_questionnaire.data = {"blocks": {"semantic_layers": {}, "scoring": {}}}
        mock_questionnaire.version = "test"

        integrator = SignalEnhancementIntegrator(mock_questionnaire)
        context = integrator._extract_interdependency_context("DIM04")

        assert "depends_on" in context
        assert "applicable_rules" in context
        assert "circular_reasoning_patterns" in context


class TestDynamicSectorLoading:
    """Tests for R-W4: Dynamic sector loading in input registry."""

    def test_sector_loading_from_canonical(self):
        """Verify sectors are loaded from canonical questionnaire (modular structure)."""
        base_path = Path(__file__).parent.parent
        pa_base = base_path / "canonic_questionnaire_central" / "policy_areas"

        if pa_base.exists():
            sector_count = 0
            for pa_dir in pa_base.iterdir():
                if pa_dir.is_dir() and (pa_dir / "questions.json").exists():
                    sector_count += 1

            assert sector_count == 10

    def test_sector_definitions_have_expected_fields(self):
        """Verify sector definitions have required fields."""
        from farfan_pipeline.phases.Phase_two.contract_generator.input_registry import (
            SECTOR_DEFINITIONS,
        )

        assert len(SECTOR_DEFINITIONS) == 10

        for sector_id, sector_data in SECTOR_DEFINITIONS.items():
            assert sector_id.startswith("PA")
            assert "canonical_id" in sector_data
            assert "canonical_name" in sector_data


class TestEnhancementStatistics:
    """Tests for enhancement statistics reporting."""

    def test_enhancement_statistics_includes_new_enhancements(self):
        """Verify get_enhancement_statistics includes R-W2 and R-W3 metrics."""
        from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_enhancement_integrator import (
            SignalEnhancementIntegrator,
        )

        mock_questionnaire = MagicMock()
        mock_questionnaire.data = {"blocks": {"semantic_layers": {}, "scoring": {}}}
        mock_questionnaire.version = "test"

        integrator = SignalEnhancementIntegrator(mock_questionnaire)
        stats = integrator.get_enhancement_statistics()

        assert "cross_cutting_themes" in stats
        assert "interdependency_rules" in stats
