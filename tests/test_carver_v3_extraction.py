"""
Tests for Carver v3.0 Methodological Depth Extraction

Validates that Carver extracts full methodological context from contract v3,
including epistemological foundations, technical approaches, output interpretation,
and renders them correctly while maintaining backward compatibility.

Author: F.A.R.F.A.N Pipeline
Version: 1.0.0
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone

# Add src to path for imports
# Test markers
pytestmark = [pytest.mark.updated]


class TestCarverV3DataStructures:
    """Test v3 dataclasses are properly defined."""

    def test_method_epistemology_frozen(self):
        """Test MethodEpistemology is frozen."""
        from farfan_pipeline.phases.Phase_2.carver import MethodEpistemology

        epi = MethodEpistemology(
            paradigm="test",
            ontological_basis="test",
            epistemological_stance="test",
            theoretical_framework=["ref1"],
            justification="test",
        )

        # Should not be able to modify frozen dataclass
        with pytest.raises(AttributeError):
            epi.paradigm = "new_value"

    def test_technical_approach_frozen(self):
        """Test TechnicalApproach is frozen."""
        from farfan_pipeline.phases.Phase_2.carver import TechnicalApproach

        tech = TechnicalApproach(
            method_type="test",
            algorithm="test",
            steps=[],
            assumptions=["a1"],
            limitations=["l1"],
            complexity="O(n)",
        )

        with pytest.raises(AttributeError):
            tech.method_type = "new_value"

    def test_output_interpretation_frozen(self):
        """Test OutputInterpretation is frozen."""
        from farfan_pipeline.phases.Phase_2.carver import OutputInterpretation

        output = OutputInterpretation(
            output_structure={"key": "value"},
            interpretation_guide={"guide": "text"},
            actionable_insights=["insight1"],
        )

        with pytest.raises(AttributeError):
            output.output_structure = {}

    def test_method_depth_entry_complete(self):
        """Test MethodDepthEntry contains all required fields."""
        from farfan_pipeline.phases.Phase_2.carver import (
            MethodDepthEntry,
            MethodEpistemology,
            TechnicalApproach,
            OutputInterpretation,
        )

        epi = MethodEpistemology(
            paradigm="test_paradigm",
            ontological_basis="test_basis",
            epistemological_stance="test_stance",
            theoretical_framework=["ref1", "ref2"],
            justification="test_justification",
        )

        tech = TechnicalApproach(
            method_type="test_type",
            algorithm="test_algo",
            steps=[{"step": 1, "description": "test"}],
            assumptions=["assumption1"],
            limitations=["limitation1"],
            complexity="O(n)",
        )

        output = OutputInterpretation(
            output_structure={"key": "value"},
            interpretation_guide={"high": "interpretation"},
            actionable_insights=["insight1"],
        )

        entry = MethodDepthEntry(
            method_name="test_method",
            class_name="TestClass",
            priority=1,
            role="test_role",
            epistemology=epi,
            technical_approach=tech,
            output_interpretation=output,
        )

        assert entry.method_name == "test_method"
        assert entry.epistemology.paradigm == "test_paradigm"
        assert entry.technical_approach.method_type == "test_type"
        assert entry.output_interpretation.actionable_insights == ["insight1"]

    def test_methodological_depth_structure(self):
        """Test MethodologicalDepth contains methods and combination logic."""
        from farfan_pipeline.phases.Phase_2.carver import (
            MethodologicalDepth,
            MethodCombinationLogic,
        )

        combo = MethodCombinationLogic(
            dependency_graph={"method1": ["method2"]},
            trade_offs=["trade_off1"],
            evidence_fusion_approach="weighted_average",
        )

        depth = MethodologicalDepth(
            methods=[],
            combination_logic=combo,
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        assert depth.combination_logic is not None
        assert depth.combination_logic.evidence_fusion_approach == "weighted_average"


class TestContractInterpreterV3:
    """Test ContractInterpreter.extract_methodological_depth()."""

    def test_extract_methodological_depth_from_v3_contract(self):
        """Test extraction returns MethodologicalDepth with v3 contract."""
        from farfan_pipeline.phases.Phase_2.carver import ContractInterpreter

        # Mock v3 contract with methodological_depth
        contract = {
            "method_binding": {
                "methodological_depth": {
                    "methods": [
                        {
                            "method_name": "test_method",
                            "class_name": "TestClass",
                            "priority": 1,
                            "role": "test_role",
                            "epistemological_foundation": {
                                "paradigm": "test_paradigm",
                                "ontological_basis": "test_basis",
                                "epistemological_stance": "test_stance",
                                "theoretical_framework": ["ref1", "ref2"],
                                "justification": "test_justification",
                            },
                            "technical_approach": {
                                "method_type": "pattern_matching",
                                "algorithm": "regex_matching",
                                "steps": [
                                    {"step": 1, "description": "Parse input"},
                                    {"step": 2, "description": "Match patterns"},
                                ],
                                "assumptions": ["assumption1", "assumption2"],
                                "limitations": ["limitation1", "limitation2"],
                                "complexity": "O(n*p)",
                            },
                            "output_interpretation": {
                                "output_structure": {"matches": "list of matches"},
                                "interpretation_guide": {
                                    "high_confidence": ">=0.8",
                                    "low_confidence": "<0.5",
                                },
                                "actionable_insights": ["insight1", "insight2"],
                            },
                        }
                    ],
                    "method_combination_logic": {
                        "dependency_graph": {"method1": ["method2"]},
                        "trade_offs": ["trade_off1"],
                        "evidence_fusion_approach": "weighted_average",
                    },
                }
            }
        }

        result = ContractInterpreter.extract_methodological_depth(contract)

        assert result is not None
        assert len(result.methods) == 1
        assert result.methods[0].method_name == "test_method"
        assert result.methods[0].epistemology.paradigm == "test_paradigm"
        assert result.methods[0].technical_approach.algorithm == "regex_matching"
        assert len(result.methods[0].technical_approach.assumptions) == 2
        assert len(result.methods[0].technical_approach.limitations) == 2
        assert result.methods[0].output_interpretation.actionable_insights == [
            "insight1",
            "insight2",
        ]
        assert result.combination_logic is not None
        assert result.combination_logic.evidence_fusion_approach == "weighted_average"

    def test_extract_methodological_depth_backward_compatible(self):
        """Test extraction returns None for v2 contracts (backward compatible)."""
        from farfan_pipeline.phases.Phase_2.carver import ContractInterpreter

        # Mock v2 contract without methodological_depth
        contract_v2 = {
            "method_binding": {
                "orchestration_mode": "multi_method_pipeline",
                "method_count": 5,
                "methods": [{"method_name": "method1"}, {"method_name": "method2"}],
            }
        }

        result = ContractInterpreter.extract_methodological_depth(contract_v2)

        assert result is None

    def test_extract_methodological_depth_empty_methods(self):
        """Test extraction handles empty methods list gracefully."""
        from farfan_pipeline.phases.Phase_2.carver import ContractInterpreter

        contract = {"method_binding": {"methodological_depth": {"methods": []}}}

        result = ContractInterpreter.extract_methodological_depth(contract)

        assert result is not None
        assert len(result.methods) == 0
        assert result.combination_logic is None

    def test_extract_methodological_depth_no_combination_logic(self):
        """Test extraction handles missing combination_logic."""
        from farfan_pipeline.phases.Phase_2.carver import ContractInterpreter

        contract = {
            "method_binding": {
                "methodological_depth": {
                    "methods": [
                        {
                            "method_name": "test_method",
                            "class_name": "TestClass",
                            "priority": 1,
                            "role": "test_role",
                            "epistemological_foundation": {
                                "paradigm": "test",
                                "ontological_basis": "test",
                                "epistemological_stance": "test",
                                "theoretical_framework": [],
                                "justification": "test",
                            },
                            "technical_approach": {
                                "method_type": "test",
                                "algorithm": "test",
                                "steps": [],
                                "assumptions": [],
                                "limitations": [],
                                "complexity": "O(1)",
                            },
                            "output_interpretation": {
                                "output_structure": {},
                                "interpretation_guide": {},
                                "actionable_insights": [],
                            },
                        }
                    ]
                }
            }
        }

        result = ContractInterpreter.extract_methodological_depth(contract)

        assert result is not None
        assert result.combination_logic is None


class TestCarverRendererV3:
    """Test CarverRenderer v3 methods."""

    def test_render_limitations_section(self):
        """Test render_limitations_section produces correct output."""
        from farfan_pipeline.phases.Phase_2.carver import (
            CarverRenderer,
            MethodologicalDepth,
            MethodDepthEntry,
            MethodEpistemology,
            TechnicalApproach,
            OutputInterpretation,
        )

        epi = MethodEpistemology(
            paradigm="test",
            ontological_basis="test",
            epistemological_stance="test",
            theoretical_framework=[],
            justification="test",
        )

        tech1 = TechnicalApproach(
            method_type="test",
            algorithm="test",
            steps=[],
            assumptions=[],
            limitations=["Cannot detect implicit causality", "Limited to single sentences"],
            complexity="O(n)",
        )

        tech2 = TechnicalApproach(
            method_type="test",
            algorithm="test",
            steps=[],
            assumptions=[],
            limitations=["Requires large context window", "May miss nuances"],
            complexity="O(n)",
        )

        output = OutputInterpretation(
            output_structure={}, interpretation_guide={}, actionable_insights=[]
        )

        method1 = MethodDepthEntry(
            method_name="m1",
            class_name="C1",
            priority=1,
            role="r1",
            epistemology=epi,
            technical_approach=tech1,
            output_interpretation=output,
        )

        method2 = MethodDepthEntry(
            method_name="m2",
            class_name="C2",
            priority=2,
            role="r2",
            epistemology=epi,
            technical_approach=tech2,
            output_interpretation=output,
        )

        depth = MethodologicalDepth(
            methods=[method1, method2],
            combination_logic=None,
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        result = CarverRenderer.render_limitations_section(depth)

        assert "## Limitaciones" in result
        assert "Cannot detect implicit causality" in result
        assert "Limited to single sentences" in result
        assert "Requires large context window" in result
        assert "May miss nuances" in result

    def test_render_theoretical_references(self):
        """Test render_theoretical_references produces deduplicated output."""
        from farfan_pipeline.phases.Phase_2.carver import (
            CarverRenderer,
            MethodologicalDepth,
            MethodDepthEntry,
            MethodEpistemology,
            TechnicalApproach,
            OutputInterpretation,
        )

        epi1 = MethodEpistemology(
            paradigm="test",
            ontological_basis="test",
            epistemological_stance="test",
            theoretical_framework=["Ref A (2020)", "Ref B (2021)"],
            justification="test",
        )

        epi2 = MethodEpistemology(
            paradigm="test",
            ontological_basis="test",
            epistemological_stance="test",
            theoretical_framework=["Ref B (2021)", "Ref C (2022)"],  # Duplicate Ref B
            justification="test",
        )

        tech = TechnicalApproach(
            method_type="test",
            algorithm="test",
            steps=[],
            assumptions=[],
            limitations=[],
            complexity="O(1)",
        )

        output = OutputInterpretation(
            output_structure={}, interpretation_guide={}, actionable_insights=[]
        )

        method1 = MethodDepthEntry(
            method_name="m1",
            class_name="C1",
            priority=1,
            role="r1",
            epistemology=epi1,
            technical_approach=tech,
            output_interpretation=output,
        )

        method2 = MethodDepthEntry(
            method_name="m2",
            class_name="C2",
            priority=2,
            role="r2",
            epistemology=epi2,
            technical_approach=tech,
            output_interpretation=output,
        )

        depth = MethodologicalDepth(
            methods=[method1, method2],
            combination_logic=None,
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        result = CarverRenderer.render_theoretical_references(depth)

        assert "## Referencias Teóricas" in result
        assert "Ref A (2020)" in result
        assert "Ref C (2022)" in result
        # Ref B should appear only once (deduplicated)
        assert result.count("Ref B (2021)") == 1

    def test_render_actionable_insights(self):
        """Test render_actionable_insights produces correct output."""
        from farfan_pipeline.phases.Phase_2.carver import (
            CarverRenderer,
            MethodologicalDepth,
            MethodDepthEntry,
            MethodEpistemology,
            TechnicalApproach,
            OutputInterpretation,
        )

        epi = MethodEpistemology(
            paradigm="test",
            ontological_basis="test",
            epistemological_stance="test",
            theoretical_framework=[],
            justification="test",
        )

        tech = TechnicalApproach(
            method_type="test",
            algorithm="test",
            steps=[],
            assumptions=[],
            limitations=[],
            complexity="O(1)",
        )

        output1 = OutputInterpretation(
            output_structure={},
            interpretation_guide={},
            actionable_insights=["Insight 1: Check data quality", "Insight 2: Validate sources"],
        )

        output2 = OutputInterpretation(
            output_structure={},
            interpretation_guide={},
            actionable_insights=["Insight 3: Cross-reference findings"],
        )

        method1 = MethodDepthEntry(
            method_name="m1",
            class_name="C1",
            priority=1,
            role="r1",
            epistemology=epi,
            technical_approach=tech,
            output_interpretation=output1,
        )

        method2 = MethodDepthEntry(
            method_name="m2",
            class_name="C2",
            priority=2,
            role="r2",
            epistemology=epi,
            technical_approach=tech,
            output_interpretation=output2,
        )

        depth = MethodologicalDepth(
            methods=[method1, method2],
            combination_logic=None,
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        result = CarverRenderer.render_actionable_insights(depth)

        assert "## Insights Accionables" in result
        assert "Insight 1: Check data quality" in result
        assert "Insight 2: Validate sources" in result
        assert "Insight 3: Cross-reference findings" in result

    def test_render_assumptions_section(self):
        """Test render_assumptions_section produces deduplicated output."""
        from farfan_pipeline.phases.Phase_2.carver import (
            CarverRenderer,
            MethodologicalDepth,
            MethodDepthEntry,
            MethodEpistemology,
            TechnicalApproach,
            OutputInterpretation,
        )

        epi = MethodEpistemology(
            paradigm="test",
            ontological_basis="test",
            epistemological_stance="test",
            theoretical_framework=[],
            justification="test",
        )

        tech1 = TechnicalApproach(
            method_type="test",
            algorithm="test",
            steps=[],
            assumptions=["Assumption A", "Assumption B"],
            limitations=[],
            complexity="O(1)",
        )

        tech2 = TechnicalApproach(
            method_type="test",
            algorithm="test",
            steps=[],
            assumptions=["Assumption B", "Assumption C"],  # Duplicate B
            limitations=[],
            complexity="O(1)",
        )

        output = OutputInterpretation(
            output_structure={}, interpretation_guide={}, actionable_insights=[]
        )

        method1 = MethodDepthEntry(
            method_name="m1",
            class_name="C1",
            priority=1,
            role="r1",
            epistemology=epi,
            technical_approach=tech1,
            output_interpretation=output,
        )

        method2 = MethodDepthEntry(
            method_name="m2",
            class_name="C2",
            priority=2,
            role="r2",
            epistemology=epi,
            technical_approach=tech2,
            output_interpretation=output,
        )

        depth = MethodologicalDepth(
            methods=[method1, method2],
            combination_logic=None,
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        result = CarverRenderer.render_assumptions_section(depth)

        assert "## Supuestos Metodológicos" in result
        assert "Assumption A" in result
        assert "Assumption C" in result
        # Assumption B should appear only once (deduplicated)
        assert result.count("Assumption B") == 1


class TestCarverAnswerV3:
    """Test CarverAnswer with v3 fields."""

    def test_carver_answer_backward_compatible(self):
        """Test CarverAnswer works without v3 fields (backward compatible)."""
        from farfan_pipeline.phases.Phase_2.carver import (
            CarverAnswer,
            Dimension,
            BayesianConfidenceResult,
        )

        conf = BayesianConfidenceResult(
            point_estimate=0.75,
            belief=0.70,
            plausibility=0.80,
            uncertainty=0.10,
            interval_95=(0.65, 0.85),
        )

        answer = CarverAnswer(
            verdict="Test verdict",
            evidence_statements=["Evidence 1"],
            gap_statements=["Gap 1"],
            confidence_result=conf,
            confidence_statement="Confidence MEDIA-ALTA",
            question_text="Test question",
            dimension=Dimension.D1_INSUMOS,
            method_note="Test note",
        )

        assert answer.verdict == "Test verdict"
        assert answer.methodological_depth is None
        assert answer.limitations_statement is None
        assert answer.theoretical_references is None
        assert answer.assumptions_statement is None
        assert answer.actionable_insights is None

    def test_carver_answer_with_v3_fields(self):
        """Test CarverAnswer with v3 fields populated."""
        from farfan_pipeline.phases.Phase_2.carver import (
            CarverAnswer,
            Dimension,
            BayesianConfidenceResult,
            MethodologicalDepth,
        )

        conf = BayesianConfidenceResult(
            point_estimate=0.75,
            belief=0.70,
            plausibility=0.80,
            uncertainty=0.10,
            interval_95=(0.65, 0.85),
        )

        depth = MethodologicalDepth(
            methods=[],
            combination_logic=None,
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        answer = CarverAnswer(
            verdict="Test verdict",
            evidence_statements=["Evidence 1"],
            gap_statements=["Gap 1"],
            confidence_result=conf,
            confidence_statement="Confidence MEDIA-ALTA",
            question_text="Test question",
            dimension=Dimension.D1_INSUMOS,
            method_note="Test note",
            methodological_depth=depth,
            limitations_statement="Test limitations",
            theoretical_references=["Ref 1"],
            assumptions_statement="Test assumptions",
            actionable_insights=["Insight 1"],
        )

        assert answer.methodological_depth is not None
        assert answer.limitations_statement == "Test limitations"
        assert answer.theoretical_references == ["Ref 1"]
        assert answer.assumptions_statement == "Test assumptions"
        assert answer.actionable_insights == ["Insight 1"]


class TestDoctoralCarverSynthesizerV3:
    """Test DoctoralCarverSynthesizer with v3 contracts."""

    def test_synthesize_with_v3_contract(self):
        """Test synthesize extracts and renders v3 methodological depth."""
        from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

        synthesizer = DoctoralCarverSynthesizer()

        # Mock evidence
        evidence = {
            "elements": [
                {
                    "type": "fuentes_oficiales",
                    "value": "DANE 2020",
                    "confidence": 0.9,
                    "source_method": "test_method",
                }
            ]
        }

        # Mock v3 contract
        contract = {
            "identity": {"dimension_id": "DIM01", "base_slot": "D1-Q1"},
            "question_context": {
                "question_text": "Test question",
                "expected_elements": [
                    {"type": "fuentes_oficiales", "required": True, "minimum": 1}
                ],
            },
            "method_binding": {
                "method_count": 1,
                "orchestration_mode": "single",
                "methods": [{"method_name": "test_method"}],
                "methodological_depth": {
                    "methods": [
                        {
                            "method_name": "test_method",
                            "class_name": "TestClass",
                            "priority": 1,
                            "role": "test_role",
                            "epistemological_foundation": {
                                "paradigm": "Test paradigm",
                                "ontological_basis": "Test basis",
                                "epistemological_stance": "Test stance",
                                "theoretical_framework": ["Test reference (2020)"],
                                "justification": "Test justification",
                            },
                            "technical_approach": {
                                "method_type": "test_type",
                                "algorithm": "test_algo",
                                "steps": [],
                                "assumptions": ["Test assumption"],
                                "limitations": ["Test limitation"],
                                "complexity": "O(n)",
                            },
                            "output_interpretation": {
                                "output_structure": {},
                                "interpretation_guide": {},
                                "actionable_insights": ["Test insight"],
                            },
                        }
                    ]
                },
            },
        }

        result = synthesizer.synthesize(evidence, contract)

        # Check basic structure
        assert isinstance(result, str)
        assert "Test question" in result
        assert "## Respuesta" in result
        assert "## Evidencia" in result
        assert "## Confianza" in result

        # Check v3 sections are present
        assert "## Limitaciones" in result
        assert "Test limitation" in result
        assert "## Supuestos Metodológicos" in result
        assert "Test assumption" in result
        assert "## Insights Accionables" in result
        assert "Test insight" in result
        assert "## Referencias Teóricas" in result
        assert "Test reference (2020)" in result

    def test_synthesize_backward_compatible_v2(self):
        """Test synthesize works with v2 contracts without methodological_depth."""
        from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

        synthesizer = DoctoralCarverSynthesizer()

        # Mock evidence
        evidence = {
            "elements": [
                {
                    "type": "fuentes_oficiales",
                    "value": "DANE 2020",
                    "confidence": 0.9,
                    "source_method": "test_method",
                }
            ]
        }

        # Mock v2 contract (no methodological_depth)
        contract_v2 = {
            "identity": {"dimension_id": "DIM01", "base_slot": "D1-Q1"},
            "question_context": {
                "question_text": "Test question v2",
                "expected_elements": [
                    {"type": "fuentes_oficiales", "required": True, "minimum": 1}
                ],
            },
            "method_binding": {
                "method_count": 1,
                "orchestration_mode": "single",
                "methods": [{"method_name": "test_method"}],
            },
        }

        result = synthesizer.synthesize(evidence, contract_v2)

        # Check basic structure works
        assert isinstance(result, str)
        assert "Test question v2" in result
        assert "## Respuesta" in result
        assert "## Evidencia" in result
        assert "## Confianza" in result

        # Check v3 sections are NOT present (backward compatible)
        assert "## Limitaciones" not in result
        assert "## Supuestos Metodológicos" not in result
        assert "## Insights Accionables" not in result
        assert "## Referencias Teóricas" not in result

    def test_synthesize_structured_with_v3(self):
        """Test synthesize_structured returns CarverAnswer with v3 depth."""
        from farfan_pipeline.phases.Phase_2.carver import DoctoralCarverSynthesizer

        synthesizer = DoctoralCarverSynthesizer()

        # Mock evidence
        evidence = {
            "elements": [
                {
                    "type": "fuentes_oficiales",
                    "value": "Test source",
                    "confidence": 0.8,
                    "source_method": "test_method",
                }
            ]
        }

        # Mock v3 contract
        contract = {
            "identity": {"dimension_id": "DIM01", "base_slot": "D1-Q1"},
            "question_context": {"question_text": "Test question", "expected_elements": []},
            "method_binding": {
                "method_count": 1,
                "orchestration_mode": "single",
                "methods": [{"method_name": "test_method"}],
                "methodological_depth": {
                    "methods": [
                        {
                            "method_name": "test_method",
                            "class_name": "TestClass",
                            "priority": 1,
                            "role": "test_role",
                            "epistemological_foundation": {
                                "paradigm": "test",
                                "ontological_basis": "test",
                                "epistemological_stance": "test",
                                "theoretical_framework": [],
                                "justification": "test",
                            },
                            "technical_approach": {
                                "method_type": "test",
                                "algorithm": "test",
                                "steps": [],
                                "assumptions": [],
                                "limitations": [],
                                "complexity": "O(1)",
                            },
                            "output_interpretation": {
                                "output_structure": {},
                                "interpretation_guide": {},
                                "actionable_insights": [],
                            },
                        }
                    ]
                },
            },
        }

        result = synthesizer.synthesize_structured(evidence, contract)

        # Check structured answer
        assert result.methodological_depth is not None
        assert len(result.methodological_depth.methods) == 1
        assert result.methodological_depth.methods[0].method_name == "test_method"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
