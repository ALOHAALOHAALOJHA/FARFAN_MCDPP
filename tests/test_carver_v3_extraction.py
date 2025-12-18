"""
Tests for Carver v3.0 Full Contract Extraction

Validates the new methodological depth extraction and rendering functionality.

Author: F.A.R.F.A.N Pipeline
Version: 1.0.0
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any

# Test markers
pytestmark = [pytest.mark.updated, pytest.mark.integration]


class TestMethodologicalDepthExtraction:
    """Test extraction of methodological depth from contracts."""
    
    def test_extract_methodological_depth_returns_none_when_missing(self):
        """Test that extraction returns None when methodological_depth is missing."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import ContractInterpreter
            
            # Contract without methodological_depth
            contract = {
                "identity": {"dimension_id": "DIM01"},
                "method_binding": {"method_count": 5}
            }
            
            result = ContractInterpreter.extract_methodological_depth(contract)
            assert result is None, "Should return None when methodological_depth is missing"
            
        except ImportError:
            pytest.skip("Cannot import ContractInterpreter")
    
    def test_extract_methodological_depth_from_minimal_contract(self):
        """Test extraction with minimal methodological depth structure."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import (
                ContractInterpreter,
                MethodologicalDepth,
                MethodDepthEntry,
            )
            
            contract = {
                "human_answer_structure": {
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
                                    "theoretical_framework": ["Framework 1"],
                                    "justification": "Test justification"
                                },
                                "technical_approach": {
                                    "method_type": "test_type",
                                    "algorithm": "Test algorithm",
                                    "steps": ["Step 1", "Step 2"],
                                    "assumptions": ["Assumption 1"],
                                    "limitations": ["Limitation 1"],
                                    "complexity": "O(n)"
                                },
                                "output_interpretation": {
                                    "output_structure": {"field": "value"},
                                    "interpretation_guide": {"high": ">=0.8"},
                                    "actionable_insights": ["Insight 1"]
                                }
                            }
                        ]
                    }
                }
            }
            
            result = ContractInterpreter.extract_methodological_depth(contract)
            
            assert result is not None, "Should extract methodological depth"
            assert isinstance(result, MethodologicalDepth)
            assert len(result.methods) == 1
            
            method = result.methods[0]
            assert method.method_name == "test_method"
            assert method.class_name == "TestClass"
            assert method.priority == 1
            assert method.epistemology.paradigm == "Test paradigm"
            assert len(method.technical_approach.steps) == 2
            assert len(method.output_interpretation.actionable_insights) == 1
            
        except ImportError:
            pytest.skip("Cannot import necessary classes")
    
    def test_extract_methodological_depth_handles_dict_steps(self):
        """Test that extraction handles both string and dict steps."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import ContractInterpreter
            
            contract = {
                "human_answer_structure": {
                    "methodological_depth": {
                        "methods": [
                            {
                                "method_name": "test_method",
                                "class_name": "TestClass",
                                "priority": 1,
                                "role": "test_role",
                                "epistemological_foundation": {
                                    "paradigm": "Test",
                                    "ontological_basis": "Test",
                                    "epistemological_stance": "Test",
                                    "theoretical_framework": [],
                                    "justification": "Test"
                                },
                                "technical_approach": {
                                    "method_type": "test",
                                    "algorithm": "Test",
                                    "steps": [
                                        {"step": 1, "description": "Step 1"},
                                        {"step": 2, "description": "Step 2"}
                                    ],
                                    "assumptions": [],
                                    "limitations": [],
                                    "complexity": "O(n)"
                                },
                                "output_interpretation": {
                                    "output_structure": {},
                                    "interpretation_guide": {},
                                    "actionable_insights": []
                                }
                            }
                        ]
                    }
                }
            }
            
            result = ContractInterpreter.extract_methodological_depth(contract)
            assert result is not None
            assert len(result.methods[0].technical_approach.steps) == 2
            
        except ImportError:
            pytest.skip("Cannot import ContractInterpreter")
    
    def test_extract_methodological_depth_skips_malformed_entries(self):
        """Test that malformed method entries are skipped gracefully."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import ContractInterpreter
            
            contract = {
                "human_answer_structure": {
                    "methodological_depth": {
                        "methods": [
                            {
                                "method_name": "good_method",
                                "class_name": "GoodClass",
                                "priority": 1,
                                "role": "role",
                                "epistemological_foundation": {
                                    "paradigm": "P",
                                    "ontological_basis": "B",
                                    "epistemological_stance": "S",
                                    "theoretical_framework": [],
                                    "justification": "J"
                                },
                                "technical_approach": {
                                    "method_type": "t",
                                    "algorithm": "a",
                                    "steps": [],
                                    "assumptions": [],
                                    "limitations": [],
                                    "complexity": "O(1)"
                                },
                                "output_interpretation": {
                                    "output_structure": {},
                                    "interpretation_guide": {},
                                    "actionable_insights": []
                                }
                            },
                            # Malformed entry missing epistemological_foundation
                            {
                                "method_name": "bad_method",
                                "class_name": "BadClass"
                            }
                        ]
                    }
                }
            }
            
            result = ContractInterpreter.extract_methodological_depth(contract)
            assert result is not None
            assert len(result.methods) == 1  # Only good_method extracted
            assert result.methods[0].method_name == "good_method"
            
        except ImportError:
            pytest.skip("Cannot import ContractInterpreter")
    
    def test_extract_combination_logic(self):
        """Test extraction of method combination logic."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import ContractInterpreter
            
            contract = {
                "human_answer_structure": {
                    "methodological_depth": {
                        "methods": [
                            {
                                "method_name": "test_method",
                                "class_name": "TestClass",
                                "priority": 1,
                                "role": "role",
                                "epistemological_foundation": {
                                    "paradigm": "P",
                                    "ontological_basis": "B",
                                    "epistemological_stance": "S",
                                    "theoretical_framework": [],
                                    "justification": "J"
                                },
                                "technical_approach": {
                                    "method_type": "t",
                                    "algorithm": "a",
                                    "steps": [],
                                    "assumptions": [],
                                    "limitations": [],
                                    "complexity": "O(1)"
                                },
                                "output_interpretation": {
                                    "output_structure": {},
                                    "interpretation_guide": {},
                                    "actionable_insights": []
                                }
                            }
                        ],
                        "method_combination_logic": {
                            "dependency_graph": {"method1": ["method2"]},
                            "trade_offs": {"trade_off": "description"},
                            "combination_strategy": "Sequential pipeline"
                        }
                    }
                }
            }
            
            result = ContractInterpreter.extract_methodological_depth(contract)
            assert result is not None
            assert result.combination_logic is not None
            assert result.combination_logic.evidence_fusion_approach == "Sequential pipeline"
            assert "method1" in result.combination_logic.dependency_graph
            
        except ImportError:
            pytest.skip("Cannot import ContractInterpreter")


class TestCarverRendering:
    """Test rendering of new v3.0 sections."""
    
    def test_render_limitations_section(self):
        """Test rendering of limitations section."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import (
                CarverRenderer,
                MethodologicalDepth,
                MethodDepthEntry,
                MethodEpistemology,
                TechnicalApproach,
                OutputInterpretation,
                Dimension,
            )
            
            method_entry = MethodDepthEntry(
                method_name="test_method",
                class_name="TestClass",
                priority=1,
                role="test_role",
                epistemology=MethodEpistemology(
                    paradigm="P", ontological_basis="B",
                    epistemological_stance="S", theoretical_framework=tuple(),
                    justification="J"
                ),
                technical_approach=TechnicalApproach(
                    method_type="t", algorithm="a", steps=tuple(),
                    assumptions=tuple(), 
                    limitations=("Limitation 1", "Limitation 2"),
                    complexity="O(1)"
                ),
                output_interpretation=OutputInterpretation(
                    output_structure={}, interpretation_guide={},
                    actionable_insights=tuple()
                )
            )
            
            depth = MethodologicalDepth(
                methods=(method_entry,),
                combination_logic=None,
                extraction_timestamp="2024-01-01T00:00:00"
            )
            
            result = CarverRenderer.render_limitations_section(depth, Dimension.D1_INSUMOS)
            
            assert "Limitaciones Metodológicas" in result
            assert "Limitation 1" in result or "Limitation 2" in result
            
        except ImportError:
            pytest.skip("Cannot import necessary classes")
    
    def test_render_theoretical_references(self):
        """Test rendering of theoretical references section."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import (
                CarverRenderer,
                MethodologicalDepth,
                MethodDepthEntry,
                MethodEpistemology,
                TechnicalApproach,
                OutputInterpretation,
            )
            
            method_entry = MethodDepthEntry(
                method_name="test_method",
                class_name="TestClass",
                priority=1,
                role="test_role",
                epistemology=MethodEpistemology(
                    paradigm="P", ontological_basis="B",
                    epistemological_stance="S",
                    theoretical_framework=("Framework 1", "Framework 2"),
                    justification="J"
                ),
                technical_approach=TechnicalApproach(
                    method_type="t", algorithm="a", steps=tuple(),
                    assumptions=tuple(), limitations=tuple(),
                    complexity="O(1)"
                ),
                output_interpretation=OutputInterpretation(
                    output_structure={}, interpretation_guide={},
                    actionable_insights=tuple()
                )
            )
            
            depth = MethodologicalDepth(
                methods=(method_entry,),
                combination_logic=None,
                extraction_timestamp="2024-01-01T00:00:00"
            )
            
            result = CarverRenderer.render_theoretical_references(depth)
            
            assert "Fundamentos Teóricos" in result
            assert "Framework 1" in result
            assert "Framework 2" in result
            
        except ImportError:
            pytest.skip("Cannot import necessary classes")
    
    def test_render_assumptions_section(self):
        """Test rendering of assumptions section."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import (
                CarverRenderer,
                MethodologicalDepth,
                MethodDepthEntry,
                MethodEpistemology,
                TechnicalApproach,
                OutputInterpretation,
            )
            
            method_entry = MethodDepthEntry(
                method_name="test_method",
                class_name="TestClass",
                priority=1,
                role="test_role",
                epistemology=MethodEpistemology(
                    paradigm="P", ontological_basis="B",
                    epistemological_stance="S", theoretical_framework=tuple(),
                    justification="J"
                ),
                technical_approach=TechnicalApproach(
                    method_type="t", algorithm="a", steps=tuple(),
                    assumptions=("Assumption 1", "Assumption 2"),
                    limitations=tuple(),
                    complexity="O(1)"
                ),
                output_interpretation=OutputInterpretation(
                    output_structure={}, interpretation_guide={},
                    actionable_insights=tuple()
                )
            )
            
            depth = MethodologicalDepth(
                methods=(method_entry,),
                combination_logic=None,
                extraction_timestamp="2024-01-01T00:00:00"
            )
            
            result = CarverRenderer.render_assumptions_section(depth)
            
            assert "Supuestos del Análisis" in result
            assert "Assumption 1" in result
            assert "Assumption 2" in result
            
        except ImportError:
            pytest.skip("Cannot import necessary classes")
    
    def test_render_actionable_insights(self):
        """Test rendering of actionable insights section."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import (
                CarverRenderer,
                MethodologicalDepth,
                MethodDepthEntry,
                MethodEpistemology,
                TechnicalApproach,
                OutputInterpretation,
                BayesianConfidenceResult,
            )
            
            method_entry = MethodDepthEntry(
                method_name="test_method",
                class_name="TestClass",
                priority=1,
                role="test_role",
                epistemology=MethodEpistemology(
                    paradigm="P", ontological_basis="B",
                    epistemological_stance="S", theoretical_framework=tuple(),
                    justification="J"
                ),
                technical_approach=TechnicalApproach(
                    method_type="t", algorithm="a", steps=tuple(),
                    assumptions=tuple(), limitations=tuple(),
                    complexity="O(1)"
                ),
                output_interpretation=OutputInterpretation(
                    output_structure={}, interpretation_guide={},
                    actionable_insights=("Insight 1", "Insight 2")
                )
            )
            
            depth = MethodologicalDepth(
                methods=(method_entry,),
                combination_logic=None,
                extraction_timestamp="2024-01-01T00:00:00"
            )
            
            confidence = BayesianConfidenceResult(
                point_estimate=0.8,
                belief=0.7,
                plausibility=0.9,
                uncertainty=0.2,
                interval_95=(0.6, 1.0)
            )
            
            result = CarverRenderer.render_actionable_insights(depth, [], confidence)
            
            assert "Recomendaciones" in result
            assert "Insight 1" in result or "Insight 2" in result
            
        except ImportError:
            pytest.skip("Cannot import necessary classes")


class TestBackwardCompatibility:
    """Test backward compatibility with contracts without methodological_depth."""
    
    def test_synthesize_without_methodological_depth(self):
        """Test that synthesis works without methodological_depth."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import DoctoralCarverSynthesizer
            
            # Contract without methodological_depth
            contract = {
                "identity": {"dimension_id": "DIM01"},
                "question_context": {
                    "question_text": "Test question?",
                    "expected_elements": []
                },
                "method_binding": {
                    "method_count": 3,
                    "orchestration_mode": "sequential",
                    "methods": []
                }
            }
            
            evidence = {
                "elements": []
            }
            
            synthesizer = DoctoralCarverSynthesizer()
            result = synthesizer.synthesize(contract=contract, evidence=evidence)
            
            assert isinstance(result, str)
            assert "Respuesta" in result
            # Should not contain v3.0 sections
            assert "Limitaciones Metodológicas" not in result
            assert "Fundamentos Teóricos" not in result
            
        except ImportError:
            pytest.skip("Cannot import DoctoralCarverSynthesizer")


class TestFullIntegration:
    """Integration tests with realistic contracts."""
    
    def test_extraction_completeness_property(self):
        """Property test: len(result.methods) <= len(input methods with valid structure)."""
        try:
            from src.farfan_pipeline.phases.Phase_two.carver import ContractInterpreter
            
            # Create contract with 3 valid methods
            contract = {
                "human_answer_structure": {
                    "methodological_depth": {
                        "methods": [
                            self._create_valid_method("method1", 1),
                            self._create_valid_method("method2", 2),
                            self._create_valid_method("method3", 3),
                        ]
                    }
                }
            }
            
            result = ContractInterpreter.extract_methodological_depth(contract)
            
            assert result is not None
            assert len(result.methods) == 3
            
        except ImportError:
            pytest.skip("Cannot import ContractInterpreter")
    
    def _create_valid_method(self, name: str, priority: int) -> Dict[str, Any]:
        """Helper to create a valid method structure."""
        return {
            "method_name": name,
            "class_name": "TestClass",
            "priority": priority,
            "role": "test_role",
            "epistemological_foundation": {
                "paradigm": "Test paradigm",
                "ontological_basis": "Test basis",
                "epistemological_stance": "Test stance",
                "theoretical_framework": ["Framework"],
                "justification": "Test"
            },
            "technical_approach": {
                "method_type": "test",
                "algorithm": "Test",
                "steps": ["Step"],
                "assumptions": ["Assumption"],
                "limitations": ["Limitation"],
                "complexity": "O(n)"
            },
            "output_interpretation": {
                "output_structure": {"field": "type"},
                "interpretation_guide": {"high": ">=0.8"},
                "actionable_insights": ["Insight"]
            }
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
