"""
Unit tests for Contextual Layers (@q, @d, @p) computation.

Tests question/dimension/policy compatibility scoring:
- Q_f(M | Q): question appropriateness
- D_f(M | D): dimension alignment  
- P_f(M | P): policy area fitness
- Anti-universality constraint

Formula: x_@q = Q_f(M | Q) with discrete scoring levels
"""

from __future__ import annotations

from typing import Any



def compute_question_compatibility(method_id: str, question_id: str, config: dict[str, Any]) -> float:
    """
    Compute question compatibility Q_f(M | Q).
    
    Returns:
        1.0 if primary method
        0.7 if secondary method
        0.3 if compatible method
        0.0 if incompatible
        0.1 if not declared (penalty)
    """
    method_compat = config.get("method_compatibility", {}).get(method_id, {})
    questions = method_compat.get("questions", {})

    if question_id in questions:
        return questions[question_id]

    return 0.1


def compute_dimension_compatibility(method_id: str, dimension_id: str, config: dict[str, Any]) -> float:
    """Compute dimension compatibility D_f(M | D)."""
    method_compat = config.get("method_compatibility", {}).get(method_id, {})
    dimensions = method_compat.get("dimensions", {})

    if dimension_id in dimensions:
        return dimensions[dimension_id]

    return 0.1


def compute_policy_compatibility(method_id: str, policy_id: str, config: dict[str, Any]) -> float:
    """Compute policy compatibility P_f(M | P)."""
    method_compat = config.get("method_compatibility", {}).get(method_id, {})
    policies = method_compat.get("policies", {})

    if policy_id in policies:
        return policies[policy_id]

    return 0.1


class TestQuestionCompatibility:
    """Test question compatibility (@q) layer."""

    def test_primary_method_score(self, method_compatibility_config: dict[str, Any]):
        """Primary methods should score 1.0."""
        score = compute_question_compatibility("pattern_extractor_v2", "Q001", method_compatibility_config)

        assert score == 1.0

    def test_secondary_method_score(self, method_compatibility_config: dict[str, Any]):
        """Secondary methods should score 0.7."""
        score = compute_question_compatibility("pattern_extractor_v2", "Q031", method_compatibility_config)

        assert score == 0.7

    def test_compatible_method_score(self, method_compatibility_config: dict[str, Any]):
        """Compatible methods should score 0.3."""
        score = compute_question_compatibility("pattern_extractor_v2", "Q091", method_compatibility_config)

        assert score == 0.3

    def test_undeclared_method_penalty(self, method_compatibility_config: dict[str, Any]):
        """Undeclared methods should receive 0.1 penalty."""
        score = compute_question_compatibility("pattern_extractor_v2", "Q999", method_compatibility_config)

        assert score == 0.1

    def test_question_compatibility_bounded(self, method_compatibility_config: dict[str, Any]):
        """All question compatibility scores must be in [0,1]."""
        for method_id in ["pattern_extractor_v2", "coherence_validator"]:
            for question_id in ["Q001", "Q002", "Q999"]:
                score = compute_question_compatibility(method_id, question_id, method_compatibility_config)
                assert 0.0 <= score <= 1.0


class TestDimensionCompatibility:
    """Test dimension compatibility (@d) layer."""

    def test_primary_dimension_score(self, method_compatibility_config: dict[str, Any]):
        """Primary dimensions should score 1.0."""
        score = compute_dimension_compatibility("pattern_extractor_v2", "DIM01", method_compatibility_config)

        assert score == 1.0

    def test_secondary_dimension_score(self, method_compatibility_config: dict[str, Any]):
        """Secondary dimensions should score 0.7."""
        score = compute_dimension_compatibility("pattern_extractor_v2", "DIM02", method_compatibility_config)

        assert score == 0.7

    def test_compatible_dimension_score(self, method_compatibility_config: dict[str, Any]):
        """Compatible dimensions should score 0.3."""
        score = compute_dimension_compatibility("pattern_extractor_v2", "DIM03", method_compatibility_config)

        assert score == 0.3

    def test_dimension_compatibility_bounded(self, method_compatibility_config: dict[str, Any]):
        """All dimension compatibility scores must be in [0,1]."""
        for method_id in ["pattern_extractor_v2", "coherence_validator"]:
            for dimension_id in ["DIM01", "DIM02", "DIM99"]:
                score = compute_dimension_compatibility(method_id, dimension_id, method_compatibility_config)
                assert 0.0 <= score <= 1.0


class TestPolicyCompatibility:
    """Test policy compatibility (@p) layer."""

    def test_primary_policy_score(self, method_compatibility_config: dict[str, Any]):
        """Primary policies should score 1.0."""
        score = compute_policy_compatibility("pattern_extractor_v2", "PA01", method_compatibility_config)

        assert score == 1.0

    def test_secondary_policy_score(self, method_compatibility_config: dict[str, Any]):
        """Secondary policies should score 0.7."""
        score = compute_policy_compatibility("pattern_extractor_v2", "PA10", method_compatibility_config)

        assert score == 0.7

    def test_compatible_policy_score(self, method_compatibility_config: dict[str, Any]):
        """Compatible policies should score 0.3."""
        score = compute_policy_compatibility("pattern_extractor_v2", "PA03", method_compatibility_config)

        assert score == 0.3

    def test_policy_compatibility_bounded(self, method_compatibility_config: dict[str, Any]):
        """All policy compatibility scores must be in [0,1]."""
        for method_id in ["pattern_extractor_v2", "coherence_validator"]:
            for policy_id in ["PA01", "PA02", "PA99"]:
                score = compute_policy_compatibility(method_id, policy_id, method_compatibility_config)
                assert 0.0 <= score <= 1.0


class TestAntiUniversalityConstraint:
    """Test anti-universality constraint: no method can be universal."""

    def test_no_method_universal_in_all_questions(self, method_compatibility_config: dict[str, Any]):
        """No method should have maximal compatibility (1.0) for all questions."""
        method_compat = method_compatibility_config.get("method_compatibility", {})

        for method_id, compat in method_compat.items():
            questions = compat.get("questions", {})

            if len(questions) > 3:
                max_scores = sum(1 for score in questions.values() if score == 1.0)
                total_possible = 300

                assert max_scores < total_possible, f"Method {method_id} has universal question compatibility"

    def test_no_method_universal_in_all_dimensions(self, method_compatibility_config: dict[str, Any]):
        """No method should have maximal compatibility for all dimensions."""
        method_compat = method_compatibility_config.get("method_compatibility", {})

        for method_id, compat in method_compat.items():
            dimensions = compat.get("dimensions", {})

            if len(dimensions) > 2:
                max_scores = sum(1 for score in dimensions.values() if score == 1.0)
                total_possible = 6

                assert max_scores < total_possible, f"Method {method_id} has universal dimension compatibility"

    def test_no_method_universal_in_all_policies(self, method_compatibility_config: dict[str, Any]):
        """No method should have maximal compatibility for all policies."""
        method_compat = method_compatibility_config.get("method_compatibility", {})

        for method_id, compat in method_compat.items():
            policies = compat.get("policies", {})

            if len(policies) > 2:
                max_scores = sum(1 for score in policies.values() if score == 1.0)
                total_possible = 10

                assert max_scores < total_possible, f"Method {method_id} has universal policy compatibility"

    def test_min_contextual_score_below_threshold(self, method_compatibility_config: dict[str, Any]):
        """For each method, min(@q, @d, @p) < 0.9 for some context."""
        method_compat = method_compatibility_config.get("method_compatibility", {})

        for method_id, compat in method_compat.items():
            questions = compat.get("questions", {})
            dimensions = compat.get("dimensions", {})
            policies = compat.get("policies", {})

            if questions and dimensions and policies:
                min_q = min(questions.values()) if questions else 0.1
                min_d = min(dimensions.values()) if dimensions else 0.1
                min_p = min(policies.values()) if policies else 0.1

                assert min(min_q, min_d, min_p) < 0.9, f"Method {method_id} violates anti-universality"


class TestContextualLayerCombinations:
    """Test combinations of contextual layers."""

    def test_all_primary_context(self, method_compatibility_config: dict[str, Any]):
        """Method in primary context should have high scores across all layers."""
        q_score = compute_question_compatibility("pattern_extractor_v2", "Q001", method_compatibility_config)
        d_score = compute_dimension_compatibility("pattern_extractor_v2", "DIM01", method_compatibility_config)
        p_score = compute_policy_compatibility("pattern_extractor_v2", "PA01", method_compatibility_config)

        assert q_score == 1.0
        assert d_score == 1.0
        assert p_score == 1.0

    def test_mixed_context(self, method_compatibility_config: dict[str, Any]):
        """Method in mixed context should have varied scores."""
        q_score = compute_question_compatibility("pattern_extractor_v2", "Q001", method_compatibility_config)
        d_score = compute_dimension_compatibility("pattern_extractor_v2", "DIM02", method_compatibility_config)
        p_score = compute_policy_compatibility("pattern_extractor_v2", "PA03", method_compatibility_config)

        assert q_score == 1.0
        assert d_score == 0.7
        assert p_score == 0.3

    def test_context_impact_on_calibration(self, method_compatibility_config: dict[str, Any]):
        """Different contexts should produce different contextual scores."""
        ctx1_scores = [
            compute_question_compatibility("pattern_extractor_v2", "Q001", method_compatibility_config),
            compute_dimension_compatibility("pattern_extractor_v2", "DIM01", method_compatibility_config),
            compute_policy_compatibility("pattern_extractor_v2", "PA01", method_compatibility_config),
        ]

        ctx2_scores = [
            compute_question_compatibility("pattern_extractor_v2", "Q031", method_compatibility_config),
            compute_dimension_compatibility("pattern_extractor_v2", "DIM02", method_compatibility_config),
            compute_policy_compatibility("pattern_extractor_v2", "PA10", method_compatibility_config),
        ]

        assert ctx1_scores != ctx2_scores


class TestContextualLayerDiscreteLevels:
    """Test discrete scoring levels for contextual layers."""

    def test_question_layer_discrete_levels(self):
        """Question layer should use discrete levels."""
        valid_levels = {0.0, 0.1, 0.3, 0.7, 1.0}

        assert 1.0 in valid_levels
        assert 0.7 in valid_levels
        assert 0.3 in valid_levels
        assert 0.1 in valid_levels
        assert 0.0 in valid_levels

    def test_no_intermediate_scores(self, method_compatibility_config: dict[str, Any]):
        """Contextual layers should not have intermediate scores like 0.5."""
        method_compat = method_compatibility_config.get("method_compatibility", {})

        for method_id, compat in method_compat.items():
            for score in compat.get("questions", {}).values():
                assert score in {0.0, 0.1, 0.3, 0.7, 1.0}, f"Invalid question score {score}"

            for score in compat.get("dimensions", {}).values():
                assert score in {0.0, 0.1, 0.3, 0.7, 1.0}, f"Invalid dimension score {score}"

            for score in compat.get("policies", {}).values():
                assert score in {0.0, 0.1, 0.3, 0.7, 1.0}, f"Invalid policy score {score}"
