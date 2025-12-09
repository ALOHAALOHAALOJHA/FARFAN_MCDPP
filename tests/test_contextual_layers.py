"""
Tests for Contextual Layer Evaluators (@q, @d, @p)

Tests CompatibilityRegistry loading, evaluation methods, penalty application,
and anti-universality validation.
"""

import json
import pytest
from pathlib import Path
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_contextual_layers import (
    CompatibilityRegistry,
    QuestionEvaluator,
    DimensionEvaluator,
    PolicyEvaluator,
    create_contextual_evaluators,
)


@pytest.fixture
def compatibility_config_path():
    """Path to COHORT_2024_method_compatibility.json."""
    return Path(__file__).parent.parent / (
        "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/"
        "calibration/COHORT_2024_method_compatibility.json"
    )


@pytest.fixture
def registry(compatibility_config_path):
    """Create CompatibilityRegistry instance."""
    return CompatibilityRegistry(compatibility_config_path)


@pytest.fixture
def temp_compatibility_config(tmp_path):
    """Create temporary compatibility config for testing."""
    config = {
        "_cohort_metadata": {
            "cohort_id": "COHORT_2024",
            "creation_date": "2024-12-15T00:00:00+00:00",
            "wave_version": "REFACTOR_WAVE_2024_12"
        },
        "method_compatibility": {
            "test_method_high": {
                "questions": {"Q001": 1.0, "Q002": 0.7},
                "dimensions": {"DIM01": 0.8, "DIM02": 0.7},
                "policies": {"PA01": 0.7, "PA02": 0.5}
            },
            "test_method_low": {
                "questions": {"Q001": 0.3},
                "dimensions": {"DIM01": 0.3},
                "policies": {"PA01": 0.3}
            }
        }
    }
    
    config_path = tmp_path / "test_compatibility.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
        
    return config_path


@pytest.fixture
def temp_universal_violation_config(tmp_path):
    """Create config that violates anti-universality."""
    config = {
        "_cohort_metadata": {
            "cohort_id": "COHORT_2024",
            "creation_date": "2024-12-15T00:00:00+00:00",
            "wave_version": "REFACTOR_WAVE_2024_12"
        },
        "method_compatibility": {
            "universal_method": {
                "questions": {"Q001": 1.0, "Q002": 1.0},
                "dimensions": {"DIM01": 1.0, "DIM02": 1.0},
                "policies": {"PA01": 1.0, "PA02": 1.0}
            }
        }
    }
    
    config_path = tmp_path / "universal_violation.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
        
    return config_path


class TestCompatibilityRegistry:
    """Tests for CompatibilityRegistry."""
    
    def test_registry_loads_from_default_path(self):
        """Test registry loads from default COHORT_2024 location."""
        registry = CompatibilityRegistry()
        assert registry is not None
        metadata = registry.get_metadata()
        assert metadata["cohort_id"] == "COHORT_2024"
        
    def test_registry_loads_from_custom_path(self, temp_compatibility_config):
        """Test registry loads from custom path."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        assert "test_method_high" in registry.list_methods()
        assert "test_method_low" in registry.list_methods()
        
    def test_registry_validates_cohort_metadata(self, tmp_path):
        """Test registry validates COHORT_2024 metadata."""
        config = {
            "_cohort_metadata": {
                "cohort_id": "INVALID_COHORT"
            },
            "method_compatibility": {}
        }
        
        config_path = tmp_path / "invalid_cohort.json"
        with open(config_path, "w") as f:
            json.dump(config, f)
            
        with pytest.raises(ValueError, match="Invalid cohort_id"):
            CompatibilityRegistry(config_path)
            
    def test_registry_rejects_missing_metadata(self, tmp_path):
        """Test registry rejects config without metadata."""
        config = {"method_compatibility": {}}
        
        config_path = tmp_path / "no_metadata.json"
        with open(config_path, "w") as f:
            json.dump(config, f)
            
        with pytest.raises(ValueError, match="Missing _cohort_metadata"):
            CompatibilityRegistry(config_path)
            
    def test_anti_universality_validation_on_load(
        self, temp_universal_violation_config
    ):
        """Test anti-universality is validated on load."""
        with pytest.raises(ValueError, match="Anti-Universality violation"):
            CompatibilityRegistry(temp_universal_violation_config)
            
    def test_evaluate_question_returns_correct_score(
        self, temp_compatibility_config
    ):
        """Test evaluate_question returns declared score."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        score = registry.evaluate_question("test_method_high", "Q001")
        assert score == 1.0
        
        score = registry.evaluate_question("test_method_high", "Q002")
        assert score == 0.7
        
    def test_evaluate_question_returns_penalty_for_unmapped(
        self, temp_compatibility_config
    ):
        """Test evaluate_question returns 0.1 penalty for unmapped."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        score = registry.evaluate_question("test_method_high", "Q999")
        assert score == 0.1
        
        score = registry.evaluate_question("nonexistent_method", "Q001")
        assert score == 0.1
        
    def test_evaluate_dimension_returns_correct_score(
        self, temp_compatibility_config
    ):
        """Test evaluate_dimension returns declared score."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        score = registry.evaluate_dimension("test_method_high", "DIM01")
        assert score == 0.8
        
    def test_evaluate_dimension_returns_penalty_for_unmapped(
        self, temp_compatibility_config
    ):
        """Test evaluate_dimension returns 0.1 penalty for unmapped."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        score = registry.evaluate_dimension("test_method_high", "DIM99")
        assert score == 0.1
        
    def test_evaluate_policy_returns_correct_score(
        self, temp_compatibility_config
    ):
        """Test evaluate_policy returns declared score."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        score = registry.evaluate_policy("test_method_high", "PA01")
        assert score == 0.7
        
    def test_evaluate_policy_returns_penalty_for_unmapped(
        self, temp_compatibility_config
    ):
        """Test evaluate_policy returns 0.1 penalty for unmapped."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        score = registry.evaluate_policy("test_method_high", "PA99")
        assert score == 0.1
        
    def test_get_method_compatibility_returns_full_mapping(
        self, temp_compatibility_config
    ):
        """Test get_method_compatibility returns complete mapping."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        compat = registry.get_method_compatibility("test_method_high")
        
        assert compat is not None
        assert "questions" in compat
        assert "dimensions" in compat
        assert "policies" in compat
        assert compat["questions"]["Q001"] == 1.0
        
    def test_get_method_compatibility_returns_none_for_unknown(
        self, temp_compatibility_config
    ):
        """Test get_method_compatibility returns None for unknown method."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        compat = registry.get_method_compatibility("unknown_method")
        assert compat is None
        
    def test_validate_method_universality_accepts_valid_method(
        self, temp_compatibility_config
    ):
        """Test validate_method_universality accepts valid methods."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        is_valid, msg = registry.validate_method_universality("test_method_high")
        assert is_valid
        assert msg == "Valid"
        
    def test_list_methods_returns_all_methods(self, temp_compatibility_config):
        """Test list_methods returns all registered methods."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        methods = registry.list_methods()
        assert "test_method_high" in methods
        assert "test_method_low" in methods
        assert len(methods) == 2


class TestQuestionEvaluator:
    """Tests for QuestionEvaluator."""
    
    def test_question_evaluator_returns_correct_score(
        self, temp_compatibility_config
    ):
        """Test QuestionEvaluator.evaluate returns correct score."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        evaluator = QuestionEvaluator(registry)
        
        score = evaluator.evaluate("test_method_high", "Q001")
        assert score == 1.0
        
        score = evaluator.evaluate("test_method_high", "Q002")
        assert score == 0.7
        
    def test_question_evaluator_applies_penalty(self, temp_compatibility_config):
        """Test QuestionEvaluator applies 0.1 penalty for unmapped."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        evaluator = QuestionEvaluator(registry)
        
        score = evaluator.evaluate("test_method_high", "Q999")
        assert score == 0.1


class TestDimensionEvaluator:
    """Tests for DimensionEvaluator."""
    
    def test_dimension_evaluator_returns_correct_score(
        self, temp_compatibility_config
    ):
        """Test DimensionEvaluator.evaluate returns correct score."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        evaluator = DimensionEvaluator(registry)
        
        score = evaluator.evaluate("test_method_high", "DIM01")
        assert score == 0.8
        
        score = evaluator.evaluate("test_method_high", "DIM02")
        assert score == 0.7
        
    def test_dimension_evaluator_applies_penalty(
        self, temp_compatibility_config
    ):
        """Test DimensionEvaluator applies 0.1 penalty for unmapped."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        evaluator = DimensionEvaluator(registry)
        
        score = evaluator.evaluate("test_method_high", "DIM99")
        assert score == 0.1


class TestPolicyEvaluator:
    """Tests for PolicyEvaluator."""
    
    def test_policy_evaluator_returns_correct_score(
        self, temp_compatibility_config
    ):
        """Test PolicyEvaluator.evaluate returns correct score."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        evaluator = PolicyEvaluator(registry)
        
        score = evaluator.evaluate("test_method_high", "PA01")
        assert score == 0.7
        
        score = evaluator.evaluate("test_method_high", "PA02")
        assert score == 0.5
        
    def test_policy_evaluator_applies_penalty(self, temp_compatibility_config):
        """Test PolicyEvaluator applies 0.1 penalty for unmapped."""
        registry = CompatibilityRegistry(temp_compatibility_config)
        evaluator = PolicyEvaluator(registry)
        
        score = evaluator.evaluate("test_method_high", "PA99")
        assert score == 0.1


class TestCreateContextualEvaluators:
    """Tests for create_contextual_evaluators factory."""
    
    def test_create_contextual_evaluators_returns_all_three(
        self, temp_compatibility_config
    ):
        """Test factory creates all three evaluators."""
        q_eval, d_eval, p_eval = create_contextual_evaluators(
            temp_compatibility_config
        )
        
        assert isinstance(q_eval, QuestionEvaluator)
        assert isinstance(d_eval, DimensionEvaluator)
        assert isinstance(p_eval, PolicyEvaluator)
        
    def test_create_contextual_evaluators_share_registry(
        self, temp_compatibility_config
    ):
        """Test all evaluators share the same registry instance."""
        q_eval, d_eval, p_eval = create_contextual_evaluators(
            temp_compatibility_config
        )
        
        assert q_eval.registry is d_eval.registry
        assert d_eval.registry is p_eval.registry
        
    def test_evaluators_work_correctly(self, temp_compatibility_config):
        """Test all evaluators work correctly from factory."""
        q_eval, d_eval, p_eval = create_contextual_evaluators(
            temp_compatibility_config
        )
        
        assert q_eval.evaluate("test_method_high", "Q001") == 1.0
        assert d_eval.evaluate("test_method_high", "DIM01") == 0.8
        assert p_eval.evaluate("test_method_high", "PA01") == 0.7


class TestRealWorldScenarios:
    """Integration tests with actual COHORT_2024 data."""
    
    def test_load_actual_cohort_config(self, registry):
        """Test loading actual COHORT_2024_method_compatibility.json."""
        assert registry is not None
        methods = registry.list_methods()
        assert len(methods) > 0
        
    def test_actual_methods_follow_anti_universality(self, registry):
        """Test actual methods follow anti-universality constraint."""
        methods = registry.list_methods()
        
        for method_id in methods:
            is_valid, msg = registry.validate_method_universality(method_id)
            assert is_valid, f"Method {method_id} violates anti-universality: {msg}"
            
    def test_score_ranges_are_valid(self, registry):
        """Test all scores in registry are in [0.0, 1.0]."""
        methods = registry.list_methods()
        
        for method_id in methods:
            compat = registry.get_method_compatibility(method_id)
            if compat is None:
                continue
                
            for context_type in ["questions", "dimensions", "policies"]:
                scores = compat.get(context_type, {})
                for ctx_id, score in scores.items():
                    assert 0.0 <= score <= 1.0, (
                        f"Invalid score {score} for {method_id} "
                        f"in {context_type}[{ctx_id}]"
                    )
                    
    def test_unmapped_always_returns_penalty(self, registry):
        """Test unmapped contexts always return 0.1 penalty."""
        methods = registry.list_methods()
        if not methods:
            pytest.skip("No methods in registry")
            
        method_id = methods[0]
        
        score = registry.evaluate_question(method_id, "Q_NONEXISTENT")
        assert score == 0.1
        
        score = registry.evaluate_dimension(method_id, "DIM_NONEXISTENT")
        assert score == 0.1
        
        score = registry.evaluate_policy(method_id, "PA_NONEXISTENT")
        assert score == 0.1
