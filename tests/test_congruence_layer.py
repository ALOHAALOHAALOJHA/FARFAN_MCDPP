"""
Tests for Congruence Layer (@C) Configuration and Evaluator
"""

import pytest
from orchestration.congruence_layer import (
    CongruenceLayerConfig,
    CongruenceLayerEvaluator,
    OutputRangeSpec,
    SemanticTagSet,
    FusionRule,
    create_default_congruence_config
)


class TestCongruenceLayerConfig:
    def test_config_creation_valid(self):
        config = CongruenceLayerConfig(
            w_scale=0.4,
            w_semantic=0.35,
            w_fusion=0.25,
            requirements={
                "require_output_range_compatibility": True,
                "require_semantic_alignment": True,
                "require_fusion_validity": True
            },
            thresholds={
                "min_jaccard_similarity": 0.3,
                "max_range_mismatch_ratio": 0.5,
                "min_fusion_validity_score": 0.6
            }
        )
        assert config.w_scale == 0.4
        assert config.w_semantic == 0.35
        assert config.w_fusion == 0.25

    def test_config_weights_sum_validation(self):
        with pytest.raises(ValueError, match="must sum to 1.0"):
            CongruenceLayerConfig(
                w_scale=0.5,
                w_semantic=0.3,
                w_fusion=0.1,
                requirements={
                    "require_output_range_compatibility": True,
                    "require_semantic_alignment": True,
                    "require_fusion_validity": True
                },
                thresholds={
                    "min_jaccard_similarity": 0.3,
                    "max_range_mismatch_ratio": 0.5,
                    "min_fusion_validity_score": 0.6
                }
            )

    def test_config_negative_weights_validation(self):
        with pytest.raises(ValueError, match="must be non-negative"):
            CongruenceLayerConfig(
                w_scale=0.6,
                w_semantic=0.5,
                w_fusion=-0.1,
                requirements={
                    "require_output_range_compatibility": True,
                    "require_semantic_alignment": True,
                    "require_fusion_validity": True
                },
                thresholds={
                    "min_jaccard_similarity": 0.3,
                    "max_range_mismatch_ratio": 0.5,
                    "min_fusion_validity_score": 0.6
                }
            )

    def test_default_config(self):
        config = create_default_congruence_config()
        assert config.w_scale == 0.4
        assert config.w_semantic == 0.35
        assert config.w_fusion == 0.25
        assert config.requirements["require_output_range_compatibility"] is True
        assert config.thresholds["min_jaccard_similarity"] == 0.3


class TestOutputScaleCompatibility:
    def test_perfect_overlap(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
        upstream = OutputRangeSpec(min=0.0, max=1.0, output_type="float")

        score = evaluator.evaluate_output_scale_compatibility(current, upstream)
        assert score == 1.0

    def test_partial_overlap(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
        upstream = OutputRangeSpec(min=0.5, max=1.5, output_type="float")

        score = evaluator.evaluate_output_scale_compatibility(current, upstream)
        assert 0.0 < score < 1.0

    def test_no_overlap(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
        upstream = OutputRangeSpec(min=2.0, max=3.0, output_type="float")

        score = evaluator.evaluate_output_scale_compatibility(current, upstream)
        assert score == 0.0

    def test_type_mismatch(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
        upstream = OutputRangeSpec(min=0.0, max=1.0, output_type="int")

        score = evaluator.evaluate_output_scale_compatibility(current, upstream)
        assert score == 0.0

    def test_zero_span(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current = OutputRangeSpec(min=0.5, max=0.5, output_type="float")
        upstream = OutputRangeSpec(min=0.0, max=1.0, output_type="float")

        score = evaluator.evaluate_output_scale_compatibility(current, upstream)
        assert score == 0.0


class TestSemanticAlignment:
    def test_perfect_match(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current = SemanticTagSet(tags={"causal", "temporal", "numeric"}, description=None)
        upstream = SemanticTagSet(tags={"causal", "temporal", "numeric"}, description=None)

        score = evaluator.evaluate_semantic_alignment(current, upstream)
        assert score == 1.0

    def test_partial_overlap(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current = SemanticTagSet(tags={"causal", "temporal"}, description=None)
        upstream = SemanticTagSet(tags={"causal", "numeric"}, description=None)

        score = evaluator.evaluate_semantic_alignment(current, upstream)
        assert 0.0 < score < 1.0
        assert abs(score - (1.0 / 3.0)) < 0.01

    def test_no_overlap(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current = SemanticTagSet(tags={"causal"}, description=None)
        upstream = SemanticTagSet(tags={"numeric"}, description=None)

        score = evaluator.evaluate_semantic_alignment(current, upstream)
        assert score == 0.0

    def test_empty_tags(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current = SemanticTagSet(tags=set(), description=None)
        upstream = SemanticTagSet(tags={"causal"}, description=None)

        score = evaluator.evaluate_semantic_alignment(current, upstream)
        assert score == 0.0

    def test_below_threshold(self):
        config = CongruenceLayerConfig(
            w_scale=0.4,
            w_semantic=0.35,
            w_fusion=0.25,
            requirements={
                "require_output_range_compatibility": True,
                "require_semantic_alignment": True,
                "require_fusion_validity": True
            },
            thresholds={
                "min_jaccard_similarity": 0.5,
                "max_range_mismatch_ratio": 0.5,
                "min_fusion_validity_score": 0.6
            }
        )
        evaluator = CongruenceLayerEvaluator(config)

        current = SemanticTagSet(tags={"causal", "temporal"}, description=None)
        upstream = SemanticTagSet(tags={"causal", "numeric", "spatial"}, description=None)

        score = evaluator.evaluate_semantic_alignment(current, upstream)
        assert score == 0.0


class TestFusionRuleValidity:
    def test_valid_aggregation_rule(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        fusion = FusionRule(
            rule_type="aggregation",
            operator="weighted_avg",
            is_valid=True,
            description=None
        )

        score = evaluator.evaluate_fusion_rule_validity(fusion)
        assert score == 1.0

    def test_invalid_rule(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        fusion = FusionRule(
            rule_type="aggregation",
            operator="weighted_avg",
            is_valid=False,
            description=None
        )

        score = evaluator.evaluate_fusion_rule_validity(fusion)
        assert score == 0.0

    def test_unknown_rule_type(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        fusion = FusionRule(
            rule_type="unknown",
            operator="custom",
            is_valid=True,
            description=None
        )

        score = evaluator.evaluate_fusion_rule_validity(fusion)
        assert score == 0.5

    def test_weighted_avg_with_context(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        fusion = FusionRule(
            rule_type="aggregation",
            operator="weighted_avg",
            is_valid=True,
            description=None
        )
        context = {"input_count": 3, "weights": [0.5, 0.3, 0.2]}

        score = evaluator.evaluate_fusion_rule_validity(fusion, context)
        assert score == 1.0

    def test_weighted_avg_mismatched_weights(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        fusion = FusionRule(
            rule_type="aggregation",
            operator="weighted_avg",
            is_valid=True,
            description=None
        )
        context = {"input_count": 3, "weights": [0.5, 0.3]}

        score = evaluator.evaluate_fusion_rule_validity(fusion, context)
        assert score < 1.0
        assert score >= 0.7

    def test_weighted_avg_invalid_sum(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        fusion = FusionRule(
            rule_type="aggregation",
            operator="weighted_avg",
            is_valid=True,
            description=None
        )
        context = {"input_count": 3, "weights": [0.5, 0.3, 0.3]}

        score = evaluator.evaluate_fusion_rule_validity(fusion, context)
        assert score < 1.0
        assert score >= 0.8

    def test_zero_inputs(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        fusion = FusionRule(
            rule_type="aggregation",
            operator="weighted_avg",
            is_valid=True,
            description=None
        )
        context = {"input_count": 0, "weights": []}

        score = evaluator.evaluate_fusion_rule_validity(fusion, context)
        assert score == 0.0


class TestCongruenceLayerEvaluation:
    def test_perfect_congruence(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current_range = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
        upstream_range = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
        current_tags = SemanticTagSet(tags={"causal", "temporal"}, description=None)
        upstream_tags = SemanticTagSet(tags={"causal", "temporal"}, description=None)
        fusion = FusionRule(
            rule_type="aggregation",
            operator="weighted_avg",
            is_valid=True,
            description=None
        )

        result = evaluator.evaluate(
            current_range, upstream_range,
            current_tags, upstream_tags,
            fusion
        )

        assert result["C_play"] == 1.0
        assert result["c_scale"] == 1.0
        assert result["c_sem"] == 1.0
        assert result["c_fusion"] == 1.0

    def test_zero_congruence(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current_range = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
        upstream_range = OutputRangeSpec(min=2.0, max=3.0, output_type="float")
        current_tags = SemanticTagSet(tags={"causal"}, description=None)
        upstream_tags = SemanticTagSet(tags={"numeric"}, description=None)
        fusion = FusionRule(
            rule_type="aggregation",
            operator="invalid",
            is_valid=False,
            description=None
        )

        result = evaluator.evaluate(
            current_range, upstream_range,
            current_tags, upstream_tags,
            fusion
        )

        assert result["C_play"] == 0.0
        assert result["c_scale"] == 0.0
        assert result["c_sem"] == 0.0
        assert result["c_fusion"] == 0.0

    def test_partial_congruence(self):
        config = create_default_congruence_config()
        evaluator = CongruenceLayerEvaluator(config)

        current_range = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
        upstream_range = OutputRangeSpec(min=0.5, max=1.5, output_type="float")
        current_tags = SemanticTagSet(tags={"causal", "temporal"}, description=None)
        upstream_tags = SemanticTagSet(tags={"causal", "numeric"}, description=None)
        fusion = FusionRule(
            rule_type="aggregation",
            operator="sum",
            is_valid=True,
            description=None
        )

        result = evaluator.evaluate(
            current_range, upstream_range,
            current_tags, upstream_tags,
            fusion
        )

        assert 0.0 < result["C_play"] < 1.0
        assert 0.0 < result["c_scale"] < 1.0
        assert 0.0 < result["c_sem"] < 1.0
        assert result["c_fusion"] == 1.0
        assert "weights" in result
        assert "thresholds" in result
