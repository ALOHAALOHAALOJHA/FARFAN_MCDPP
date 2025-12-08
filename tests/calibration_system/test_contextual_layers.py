"""
Tests for contextual layer evaluators (@q, @d, @p).

This test suite validates:
1. CompatibilityRegistry loading and validation
2. CompatibilityMapping scoring logic
3. Anti-Universality Theorem enforcement
4. ContextualLayerEvaluator evaluation methods
"""

import json
import tempfile
from pathlib import Path

import pytest

from farfan_pipeline.core.calibration.compatibility import (
    CompatibilityRegistry,
    ContextualLayerEvaluator,
)
from farfan_pipeline.core.calibration.data_structures import CompatibilityMapping


@pytest.fixture
def sample_compatibility_config():
    """Create a sample compatibility configuration."""
    return {
        "method_compatibility": {
            "pattern_extractor_v2": {
                "questions": {"Q001": 1.0, "Q031": 0.7, "Q091": 0.3},
                "dimensions": {"DIM01": 1.0, "DIM02": 0.7, "DIM03": 0.3},
                "policies": {"PA01": 1.0, "PA10": 0.7, "PA03": 0.3},
            },
            "coherence_validator": {
                "questions": {"Q001": 1.0, "Q002": 1.0},
                "dimensions": {"DIM01": 1.0, "DIM02": 0.7},
                "policies": {"PA01": 1.0, "PA02": 0.7},
            },
            "universal_method_violation": {
                "questions": {"Q001": 1.0, "Q002": 1.0, "Q003": 1.0},
                "dimensions": {"DIM01": 1.0, "DIM02": 1.0, "DIM03": 1.0},
                "policies": {"PA01": 1.0, "PA02": 1.0, "PA03": 1.0},
            },
        }
    }


@pytest.fixture
def temp_config_file(sample_compatibility_config):
    """Create a temporary config file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_compatibility_config, f)
        temp_path = Path(f.name)

    yield temp_path

    temp_path.unlink()


@pytest.fixture
def registry(temp_config_file):
    """Create a CompatibilityRegistry instance."""
    return CompatibilityRegistry(temp_config_file)


@pytest.fixture
def evaluator(registry):
    """Create a ContextualLayerEvaluator instance."""
    return ContextualLayerEvaluator(registry)


class TestCompatibilityMapping:
    """Test CompatibilityMapping dataclass."""

    def test_get_question_score_existing(self):
        mapping = CompatibilityMapping(
            method_id="test_method",
            questions={"Q001": 1.0, "Q031": 0.7},
            dimensions={},
            policies={},
        )
        assert mapping.get_question_score("Q001") == 1.0
        assert mapping.get_question_score("Q031") == 0.7

    def test_get_question_score_missing_returns_penalty(self):
        mapping = CompatibilityMapping(
            method_id="test_method", questions={"Q001": 1.0}, dimensions={}, policies={}
        )
        assert mapping.get_question_score("Q999") == 0.1

    def test_get_dimension_score_existing(self):
        mapping = CompatibilityMapping(
            method_id="test_method",
            questions={},
            dimensions={"DIM01": 1.0, "DIM02": 0.7},
            policies={},
        )
        assert mapping.get_dimension_score("DIM01") == 1.0
        assert mapping.get_dimension_score("DIM02") == 0.7

    def test_get_dimension_score_missing_returns_penalty(self):
        mapping = CompatibilityMapping(
            method_id="test_method",
            questions={},
            dimensions={"DIM01": 1.0},
            policies={},
        )
        assert mapping.get_dimension_score("DIM99") == 0.1

    def test_get_policy_score_existing(self):
        mapping = CompatibilityMapping(
            method_id="test_method",
            questions={},
            dimensions={},
            policies={"PA01": 1.0, "PA10": 0.7},
        )
        assert mapping.get_policy_score("PA01") == 1.0
        assert mapping.get_policy_score("PA10") == 0.7

    def test_get_policy_score_missing_returns_penalty(self):
        mapping = CompatibilityMapping(
            method_id="test_method", questions={}, dimensions={}, policies={"PA01": 1.0}
        )
        assert mapping.get_policy_score("PA99") == 0.1

    def test_check_anti_universality_compliant(self):
        mapping = CompatibilityMapping(
            method_id="test_method",
            questions={"Q001": 1.0, "Q002": 0.7, "Q003": 0.3},
            dimensions={"DIM01": 1.0, "DIM02": 0.7, "DIM03": 0.3},
            policies={"PA01": 1.0, "PA02": 0.7, "PA03": 0.3},
        )
        assert mapping.check_anti_universality(threshold=0.9) is True

    def test_check_anti_universality_violation(self):
        mapping = CompatibilityMapping(
            method_id="universal_method",
            questions={"Q001": 1.0, "Q002": 1.0, "Q003": 1.0},
            dimensions={"DIM01": 1.0, "DIM02": 1.0, "DIM03": 1.0},
            policies={"PA01": 1.0, "PA02": 1.0, "PA03": 1.0},
        )
        assert mapping.check_anti_universality(threshold=0.9) is False

    def test_check_anti_universality_empty_mapping_compliant(self):
        mapping = CompatibilityMapping(
            method_id="test_method", questions={}, dimensions={}, policies={}
        )
        assert mapping.check_anti_universality(threshold=0.9) is True

    def test_check_anti_universality_custom_threshold(self):
        mapping = CompatibilityMapping(
            method_id="test_method",
            questions={"Q001": 0.8, "Q002": 0.8},
            dimensions={"DIM01": 0.8, "DIM02": 0.8},
            policies={"PA01": 0.8, "PA02": 0.8},
        )
        assert mapping.check_anti_universality(threshold=0.85) is True
        assert mapping.check_anti_universality(threshold=0.75) is False


class TestCompatibilityRegistry:
    """Test CompatibilityRegistry class."""

    def test_registry_loads_correctly(self, registry):
        assert len(registry.mappings) == 3
        assert "pattern_extractor_v2" in registry.mappings
        assert "coherence_validator" in registry.mappings

    def test_registry_get_existing_method(self, registry):
        mapping = registry.get("pattern_extractor_v2")
        assert mapping.method_id == "pattern_extractor_v2"
        assert mapping.get_question_score("Q001") == 1.0

    def test_registry_get_missing_method_returns_default(self, registry):
        mapping = registry.get("nonexistent_method")
        assert mapping.method_id == "nonexistent_method"
        assert mapping.get_question_score("Q001") == 0.1
        assert mapping.get_dimension_score("DIM01") == 0.1
        assert mapping.get_policy_score("PA01") == 0.1

    def test_registry_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            CompatibilityRegistry("/nonexistent/path.json")

    def test_registry_invalid_structure(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"invalid_key": {}}, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="method_compatibility"):
                CompatibilityRegistry(temp_path)
        finally:
            temp_path.unlink()

    def test_validate_anti_universality_all_compliant(self, temp_config_file):
        config = {
            "method_compatibility": {
                "method1": {
                    "questions": {"Q001": 1.0, "Q002": 0.7},
                    "dimensions": {"DIM01": 1.0, "DIM02": 0.7},
                    "policies": {"PA01": 1.0, "PA02": 0.7},
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)

        try:
            registry = CompatibilityRegistry(temp_path)
            results = registry.validate_anti_universality(threshold=0.9)
            assert results["method1"] is True
        finally:
            temp_path.unlink()

    def test_validate_anti_universality_violation_raises(self, registry):
        with pytest.raises(ValueError, match="Anti-Universality Theorem violated"):
            registry.validate_anti_universality(threshold=0.9)


class TestContextualLayerEvaluator:
    """Test ContextualLayerEvaluator class."""

    def test_evaluate_question_existing(self, evaluator):
        score = evaluator.evaluate_question("pattern_extractor_v2", "Q001")
        assert score == 1.0

        score = evaluator.evaluate_question("pattern_extractor_v2", "Q031")
        assert score == 0.7

    def test_evaluate_question_missing(self, evaluator):
        score = evaluator.evaluate_question("pattern_extractor_v2", "Q999")
        assert score == 0.1

    def test_evaluate_question_unknown_method(self, evaluator):
        score = evaluator.evaluate_question("unknown_method", "Q001")
        assert score == 0.1

    def test_evaluate_dimension_existing(self, evaluator):
        score = evaluator.evaluate_dimension("pattern_extractor_v2", "DIM01")
        assert score == 1.0

        score = evaluator.evaluate_dimension("pattern_extractor_v2", "DIM02")
        assert score == 0.7

    def test_evaluate_dimension_missing(self, evaluator):
        score = evaluator.evaluate_dimension("pattern_extractor_v2", "DIM99")
        assert score == 0.1

    def test_evaluate_dimension_unknown_method(self, evaluator):
        score = evaluator.evaluate_dimension("unknown_method", "DIM01")
        assert score == 0.1

    def test_evaluate_policy_existing(self, evaluator):
        score = evaluator.evaluate_policy("pattern_extractor_v2", "PA01")
        assert score == 1.0

        score = evaluator.evaluate_policy("pattern_extractor_v2", "PA10")
        assert score == 0.7

    def test_evaluate_policy_missing(self, evaluator):
        score = evaluator.evaluate_policy("pattern_extractor_v2", "PA99")
        assert score == 0.1

    def test_evaluate_policy_unknown_method(self, evaluator):
        score = evaluator.evaluate_policy("unknown_method", "PA01")
        assert score == 0.1

    def test_evaluate_all_contextual(self, evaluator):
        scores = evaluator.evaluate_all_contextual(
            method_id="pattern_extractor_v2",
            question_id="Q001",
            dimension="DIM01",
            policy_area="PA01",
        )

        assert scores["q"] == 1.0
        assert scores["d"] == 1.0
        assert scores["p"] == 1.0

    def test_evaluate_all_contextual_mixed_scores(self, evaluator):
        scores = evaluator.evaluate_all_contextual(
            method_id="pattern_extractor_v2",
            question_id="Q031",
            dimension="DIM02",
            policy_area="PA10",
        )

        assert scores["q"] == 0.7
        assert scores["d"] == 0.7
        assert scores["p"] == 0.7

    def test_evaluate_all_contextual_missing_values(self, evaluator):
        scores = evaluator.evaluate_all_contextual(
            method_id="pattern_extractor_v2",
            question_id="Q999",
            dimension="DIM99",
            policy_area="PA99",
        )

        assert scores["q"] == 0.1
        assert scores["d"] == 0.1
        assert scores["p"] == 0.1


class TestIntegrationScenarios:
    """Integration tests for realistic usage scenarios."""

    def test_multiple_methods_evaluation(self, evaluator):
        methods = ["pattern_extractor_v2", "coherence_validator"]
        question_id = "Q001"
        dimension = "DIM01"
        policy_area = "PA01"

        results = []
        for method_id in methods:
            scores = evaluator.evaluate_all_contextual(
                method_id=method_id,
                question_id=question_id,
                dimension=dimension,
                policy_area=policy_area,
            )
            results.append({"method": method_id, "scores": scores})

        assert len(results) == 2
        assert all(r["scores"]["q"] >= 0.1 for r in results)
        assert all(r["scores"]["d"] >= 0.1 for r in results)
        assert all(r["scores"]["p"] >= 0.1 for r in results)

    def test_compatibility_score_ranges(self, evaluator):
        valid_scores = {1.0, 0.7, 0.3, 0.1}

        score = evaluator.evaluate_question("pattern_extractor_v2", "Q001")
        assert score in valid_scores

        score = evaluator.evaluate_dimension("pattern_extractor_v2", "DIM01")
        assert score in valid_scores

        score = evaluator.evaluate_policy("pattern_extractor_v2", "PA01")
        assert score in valid_scores

    def test_registry_persistence(self, temp_config_file):
        registry1 = CompatibilityRegistry(temp_config_file)
        registry2 = CompatibilityRegistry(temp_config_file)

        mapping1 = registry1.get("pattern_extractor_v2")
        mapping2 = registry2.get("pattern_extractor_v2")

        assert mapping1.get_question_score("Q001") == mapping2.get_question_score(
            "Q001"
        )
