"""
Congruence Layer Evaluator Tests

Test suite for CongruenceLayerEvaluator with comprehensive coverage of:
- c_scale computation
- c_sem computation via Jaccard index
- c_fusion computation
- C_play aggregation
- Edge cases (single method, empty ensemble, missing data)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from farfan_pipeline.core.calibration.congruence_layer import CongruenceLayerEvaluator


class TestCScaleComputation:
    """Test scale congruence computation"""
    
    def test_identical_ranges_returns_1_0(self) -> None:
        """All methods with identical output ranges should return 1.0"""
        registry = {
            "method_a": {"output_range": [0.0, 1.0], "semantic_tags": ["quality"]},
            "method_b": {"output_range": [0.0, 1.0], "semantic_tags": ["quality"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_scale = evaluator._compute_c_scale(["method_a", "method_b"])
        assert c_scale == 1.0
    
    def test_all_in_0_1_convertible_returns_0_8(self) -> None:
        """Methods with ranges all within [0,1] should return 0.8"""
        registry = {
            "method_a": {"output_range": [0.0, 0.5], "semantic_tags": ["quality"]},
            "method_b": {"output_range": [0.2, 0.9], "semantic_tags": ["quality"]},
            "method_c": {"output_range": [0.0, 1.0], "semantic_tags": ["quality"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_scale = evaluator._compute_c_scale(["method_a", "method_b", "method_c"])
        assert c_scale == 0.8
    
    def test_incompatible_ranges_returns_0_0(self) -> None:
        """Methods with incompatible ranges (outside [0,1]) should return 0.0"""
        registry = {
            "method_a": {"output_range": [0.0, 1.0], "semantic_tags": ["quality"]},
            "method_b": {"output_range": [0.0, 100.0], "semantic_tags": ["quality"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_scale = evaluator._compute_c_scale(["method_a", "method_b"])
        assert c_scale == 0.0
    
    def test_missing_output_range_returns_0_0(self) -> None:
        """Missing output_range metadata should return 0.0"""
        registry = {
            "method_a": {"output_range": [0.0, 1.0], "semantic_tags": ["quality"]},
            "method_b": {"semantic_tags": ["quality"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_scale = evaluator._compute_c_scale(["method_a", "method_b"])
        assert c_scale == 0.0
    
    def test_single_method_returns_1_0(self) -> None:
        """Single method should return 1.0"""
        registry = {
            "method_a": {"output_range": [0.0, 100.0], "semantic_tags": ["quality"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_scale = evaluator._compute_c_scale(["method_a"])
        assert c_scale == 1.0
    
    def test_empty_list_returns_1_0(self) -> None:
        """Empty method list should return 1.0"""
        evaluator = CongruenceLayerEvaluator({})
        
        c_scale = evaluator._compute_c_scale([])
        assert c_scale == 1.0


class TestCSemComputation:
    """Test semantic congruence computation"""
    
    def test_identical_tags_returns_1_0(self) -> None:
        """Methods with identical semantic tags should return 1.0"""
        registry = {
            "method_a": {
                "output_range": [0.0, 1.0],
                "semantic_tags": ["coherence", "quality", "textual"]
            },
            "method_b": {
                "output_range": [0.0, 1.0],
                "semantic_tags": ["coherence", "quality", "textual"]
            },
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_sem = evaluator._compute_c_sem(["method_a", "method_b"])
        assert c_sem == 1.0
    
    def test_partial_overlap_jaccard_index(self) -> None:
        """Methods with partial tag overlap should return Jaccard index"""
        registry = {
            "method_a": {
                "output_range": [0.0, 1.0],
                "semantic_tags": ["coherence", "quality"]
            },
            "method_b": {
                "output_range": [0.0, 1.0],
                "semantic_tags": ["quality", "validation"]
            },
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_sem = evaluator._compute_c_sem(["method_a", "method_b"])
        intersection = {"quality"}
        union = {"coherence", "quality", "validation"}
        expected = len(intersection) / len(union)
        assert abs(c_sem - expected) < 1e-6
    
    def test_no_overlap_returns_0_0(self) -> None:
        """Methods with no tag overlap should return 0.0"""
        registry = {
            "method_a": {
                "output_range": [0.0, 1.0],
                "semantic_tags": ["coherence", "textual"]
            },
            "method_b": {
                "output_range": [0.0, 1.0],
                "semantic_tags": ["numerical", "structural"]
            },
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_sem = evaluator._compute_c_sem(["method_a", "method_b"])
        assert c_sem == 0.0
    
    def test_empty_tags_returns_0_0(self) -> None:
        """Methods with empty tags should return 0.0"""
        registry = {
            "method_a": {"output_range": [0.0, 1.0], "semantic_tags": []},
            "method_b": {"output_range": [0.0, 1.0], "semantic_tags": []},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_sem = evaluator._compute_c_sem(["method_a", "method_b"])
        assert c_sem == 0.0
    
    def test_single_method_returns_1_0(self) -> None:
        """Single method should return 1.0"""
        registry = {
            "method_a": {"output_range": [0.0, 1.0], "semantic_tags": ["quality"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_sem = evaluator._compute_c_sem(["method_a"])
        assert c_sem == 1.0
    
    def test_three_methods_jaccard(self) -> None:
        """Test Jaccard with three methods"""
        registry = {
            "method_a": {"output_range": [0.0, 1.0], "semantic_tags": ["a", "b", "c"]},
            "method_b": {"output_range": [0.0, 1.0], "semantic_tags": ["b", "c", "d"]},
            "method_c": {"output_range": [0.0, 1.0], "semantic_tags": ["c", "d", "e"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_sem = evaluator._compute_c_sem(["method_a", "method_b", "method_c"])
        intersection = {"c"}
        union = {"a", "b", "c", "d", "e"}
        expected = len(intersection) / len(union)
        assert abs(c_sem - expected) < 1e-6


class TestCFusionComputation:
    """Test fusion validity computation"""
    
    def test_fusion_rule_present_all_inputs_returns_1_0(self) -> None:
        """Fusion rule with all inputs present should return 1.0"""
        evaluator = CongruenceLayerEvaluator({})
        
        c_fusion = evaluator._compute_c_fusion(
            fusion_rule="TYPE_A",
            provided_inputs={"method_a", "method_b"},
            required_method_ids=["method_a", "method_b"]
        )
        assert c_fusion == 1.0
    
    def test_fusion_rule_present_missing_inputs_returns_0_5(self) -> None:
        """Fusion rule with missing inputs should return 0.5"""
        evaluator = CongruenceLayerEvaluator({})
        
        c_fusion = evaluator._compute_c_fusion(
            fusion_rule="weighted_average",
            provided_inputs={"method_a"},
            required_method_ids=["method_a", "method_b"]
        )
        assert c_fusion == 0.5
    
    def test_no_fusion_rule_returns_0_0(self) -> None:
        """No fusion rule should return 0.0"""
        evaluator = CongruenceLayerEvaluator({})
        
        c_fusion = evaluator._compute_c_fusion(
            fusion_rule=None,
            provided_inputs={"method_a", "method_b"},
            required_method_ids=["method_a", "method_b"]
        )
        assert c_fusion == 0.0
    
    def test_empty_fusion_rule_returns_0_0(self) -> None:
        """Empty fusion rule string should return 0.0"""
        evaluator = CongruenceLayerEvaluator({})
        
        c_fusion = evaluator._compute_c_fusion(
            fusion_rule="",
            provided_inputs={"method_a", "method_b"},
            required_method_ids=["method_a", "method_b"]
        )
        assert c_fusion == 0.0
    
    def test_no_provided_inputs_returns_0_5(self) -> None:
        """Valid fusion rule but no provided inputs should return 0.5"""
        evaluator = CongruenceLayerEvaluator({})
        
        c_fusion = evaluator._compute_c_fusion(
            fusion_rule="TYPE_B",
            provided_inputs=set(),
            required_method_ids=["method_a", "method_b"]
        )
        assert c_fusion == 0.5
    
    def test_extra_inputs_returns_1_0(self) -> None:
        """Extra inputs beyond required should return 1.0"""
        evaluator = CongruenceLayerEvaluator({})
        
        c_fusion = evaluator._compute_c_fusion(
            fusion_rule="TYPE_A",
            provided_inputs={"method_a", "method_b", "method_c"},
            required_method_ids=["method_a", "method_b"]
        )
        assert c_fusion == 1.0


class TestCPlayEvaluation:
    """Test full C_play evaluation"""
    
    def test_perfect_ensemble_returns_1_0(self) -> None:
        """Perfect ensemble (all 1.0 components) should return 1.0"""
        registry = {
            "analyzer": {
                "output_range": [0.0, 1.0],
                "semantic_tags": ["coherence", "textual_quality"]
            },
            "validator": {
                "output_range": [0.0, 1.0],
                "semantic_tags": ["coherence", "textual_quality"]
            },
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_play = evaluator.evaluate(
            method_ids=["analyzer", "validator"],
            subgraph_id="Q001",
            fusion_rule="TYPE_A",
            provided_inputs={"analyzer", "validator"}
        )
        assert c_play == 1.0
    
    def test_example_from_spec(self) -> None:
        """Test example from specification (Section 3.5.1)"""
        registry = {
            "v_analyzer": {
                "output_range": [0.0, 1.0],
                "semantic_tags": {"coherence", "textual_quality"}
            },
            "v_validator": {
                "output_range": [0.0, 1.0],
                "semantic_tags": {"coherence", "textual_quality"}
            },
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_play = evaluator.evaluate(
            method_ids=["v_analyzer", "v_validator"],
            subgraph_id="Q001",
            fusion_rule="weighted_average",
            provided_inputs={"v_analyzer", "v_validator"}
        )
        
        assert c_play == 1.0
    
    def test_partial_congruence(self) -> None:
        """Test ensemble with partial congruence"""
        registry = {
            "method_a": {
                "output_range": [0.0, 0.8],
                "semantic_tags": ["quality", "structural"]
            },
            "method_b": {
                "output_range": [0.2, 1.0],
                "semantic_tags": ["quality", "numerical"]
            },
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_play = evaluator.evaluate(
            method_ids=["method_a", "method_b"],
            fusion_rule="TYPE_B",
            provided_inputs={"method_a"}
        )
        
        c_scale = 0.8
        c_sem = 1.0 / 3.0
        c_fusion = 0.5
        expected = c_scale * c_sem * c_fusion
        
        assert abs(c_play - expected) < 1e-6
    
    def test_single_method_returns_1_0(self) -> None:
        """Single method ensemble should return 1.0"""
        registry = {
            "method_a": {
                "output_range": [0.0, 100.0],
                "semantic_tags": ["anything"]
            },
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_play = evaluator.evaluate(
            method_ids=["method_a"],
            fusion_rule=None,
            provided_inputs=set()
        )
        assert c_play == 1.0
    
    def test_empty_ensemble_returns_1_0(self) -> None:
        """Empty ensemble should return 1.0"""
        evaluator = CongruenceLayerEvaluator({})
        
        c_play = evaluator.evaluate(
            method_ids=[],
            fusion_rule=None,
            provided_inputs=set()
        )
        assert c_play == 1.0
    
    def test_method_not_in_registry_single(self) -> None:
        """Single method not in registry should return 1.0"""
        evaluator = CongruenceLayerEvaluator({})
        
        c_play = evaluator.evaluate(
            method_ids=["unknown_method"],
            fusion_rule="TYPE_A",
            provided_inputs={"unknown_method"}
        )
        assert c_play == 1.0
    
    def test_multiplication_formula(self) -> None:
        """Verify C_play = c_scale * c_sem * c_fusion"""
        registry = {
            "m1": {
                "output_range": [0.0, 0.5],
                "semantic_tags": ["tag_a", "tag_b"]
            },
            "m2": {
                "output_range": [0.3, 0.9],
                "semantic_tags": ["tag_b", "tag_c"]
            },
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_scale_expected = 0.8
        c_sem_expected = 1.0 / 3.0
        c_fusion_expected = 0.5
        
        c_play = evaluator.evaluate(
            method_ids=["m1", "m2"],
            fusion_rule="average",
            provided_inputs={"m1"}
        )
        
        expected = c_scale_expected * c_sem_expected * c_fusion_expected
        assert abs(c_play - expected) < 1e-6


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_none_provided_inputs_treated_as_empty_set(self) -> None:
        """None for provided_inputs should be treated as empty set"""
        registry = {
            "m1": {"output_range": [0.0, 1.0], "semantic_tags": ["a"]},
            "m2": {"output_range": [0.0, 1.0], "semantic_tags": ["a"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_play = evaluator.evaluate(
            method_ids=["m1", "m2"],
            fusion_rule="TYPE_A",
            provided_inputs=None
        )
        
        assert c_play == 0.5
    
    def test_invalid_output_range_format(self) -> None:
        """Invalid output_range format should result in c_scale = 0.0"""
        registry = {
            "m1": {"output_range": [0.0, 1.0], "semantic_tags": ["a"]},
            "m2": {"output_range": "invalid", "semantic_tags": ["a"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_play = evaluator.evaluate(
            method_ids=["m1", "m2"],
            fusion_rule="TYPE_A",
            provided_inputs={"m1", "m2"}
        )
        
        assert c_play == 0.0
    
    def test_semantic_tags_as_list(self) -> None:
        """semantic_tags as list should be converted to set"""
        registry = {
            "m1": {"output_range": [0.0, 1.0], "semantic_tags": ["a", "b"]},
            "m2": {"output_range": [0.0, 1.0], "semantic_tags": ["b", "c"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_sem = evaluator._compute_c_sem(["m1", "m2"])
        
        intersection = {"b"}
        union = {"a", "b", "c"}
        expected = len(intersection) / len(union)
        assert abs(c_sem - expected) < 1e-6
    
    def test_tuple_output_range(self) -> None:
        """Tuple output_range should work like list"""
        registry = {
            "m1": {"output_range": (0.0, 1.0), "semantic_tags": ["a"]},
            "m2": {"output_range": (0.0, 1.0), "semantic_tags": ["a"]},
        }
        evaluator = CongruenceLayerEvaluator(registry)
        
        c_scale = evaluator._compute_c_scale(["m1", "m2"])
        assert c_scale == 1.0
    
    def test_no_method_registry(self) -> None:
        """Evaluator with no method registry should handle gracefully"""
        evaluator = CongruenceLayerEvaluator()
        
        c_play = evaluator.evaluate(
            method_ids=["m1", "m2"],
            fusion_rule="TYPE_A",
            provided_inputs={"m1", "m2"}
        )
        
        assert c_play == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
