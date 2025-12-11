"""
Tests for Chain Layer (@chain) Configuration and Evaluator
"""

import pytest
from orchestration.chain_layer import (
    ChainLayerConfig,
    ChainLayerEvaluator,
    MethodSignature,
    UpstreamOutputs,
    create_default_chain_config
)


class TestChainLayerConfig:
    def test_config_creation_valid(self):
        config = ChainLayerConfig(
            validation_config={
                "strict_mode": False,
                "allow_missing_optional": True,
                "penalize_warnings": True
            },
            score_missing_required=0.0,
            score_missing_critical=0.3,
            score_missing_optional=0.6,
            score_warnings=0.8,
            score_perfect=1.0
        )
        assert config.score_missing_required == 0.0
        assert config.score_missing_critical == 0.3
        assert config.score_perfect == 1.0

    def test_config_scores_range_validation(self):
        with pytest.raises(ValueError, match="must be in range"):
            ChainLayerConfig(
                validation_config={
                    "strict_mode": False,
                    "allow_missing_optional": True,
                    "penalize_warnings": True
                },
                score_missing_required=-0.1,
                score_missing_critical=0.3,
                score_missing_optional=0.6,
                score_warnings=0.8,
                score_perfect=1.0
            )

    def test_config_scores_ordering_validation(self):
        with pytest.raises(ValueError, match="strictly increasing"):
            ChainLayerConfig(
                validation_config={
                    "strict_mode": False,
                    "allow_missing_optional": True,
                    "penalize_warnings": True
                },
                score_missing_required=0.0,
                score_missing_critical=0.6,
                score_missing_optional=0.3,
                score_warnings=0.8,
                score_perfect=1.0
            )

    def test_default_config(self):
        config = create_default_chain_config()
        assert config.score_missing_required == 0.0
        assert config.score_missing_critical == 0.3
        assert config.score_missing_optional == 0.6
        assert config.score_warnings == 0.8
        assert config.score_perfect == 1.0
        assert config.validation_config["allow_missing_optional"] is True


class TestSignatureValidation:
    def test_all_required_inputs_available(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signature = MethodSignature(
            required_inputs=["policy_text", "dimension_id"],
            optional_inputs=["context"],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )
        upstream = UpstreamOutputs(
            available_outputs={"policy_text", "dimension_id", "metadata"},
            output_types={}
        )

        result = evaluator.validate_signature_against_upstream(signature, upstream)
        assert result["score"] == 1.0
        assert result["validation_status"] == "perfect"
        assert len(result["missing_required"]) == 0

    def test_missing_required_input(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signature = MethodSignature(
            required_inputs=["policy_text", "dimension_id"],
            optional_inputs=["context"],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )
        upstream = UpstreamOutputs(
            available_outputs={"policy_text"},
            output_types={}
        )

        result = evaluator.validate_signature_against_upstream(signature, upstream)
        assert result["score"] == 0.0
        assert result["validation_status"] == "failed_missing_required"
        assert "dimension_id" in result["missing_required"]

    def test_missing_critical_optional(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signature = MethodSignature(
            required_inputs=["policy_text"],
            optional_inputs=["context", "metadata"],
            critical_optional=["context"],
            output_type="dict",
            output_range=None
        )
        upstream = UpstreamOutputs(
            available_outputs={"policy_text", "metadata"},
            output_types={}
        )

        result = evaluator.validate_signature_against_upstream(signature, upstream)
        assert result["score"] == 0.3
        assert result["validation_status"] == "failed_missing_critical"
        assert "context" in result["missing_critical"]

    def test_missing_optional_only(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signature = MethodSignature(
            required_inputs=["policy_text"],
            optional_inputs=["context", "metadata"],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )
        upstream = UpstreamOutputs(
            available_outputs={"policy_text"},
            output_types={}
        )

        result = evaluator.validate_signature_against_upstream(signature, upstream)
        assert result["score"] == 1.0
        assert result["validation_status"] == "perfect"
        assert len(result["missing_optional"]) == 2

    def test_missing_optional_with_penalty(self):
        config = ChainLayerConfig(
            validation_config={
                "strict_mode": False,
                "allow_missing_optional": False,
                "penalize_warnings": True
            },
            score_missing_required=0.0,
            score_missing_critical=0.3,
            score_missing_optional=0.6,
            score_warnings=0.8,
            score_perfect=1.0
        )
        evaluator = ChainLayerEvaluator(config)

        signature = MethodSignature(
            required_inputs=["policy_text"],
            optional_inputs=["context", "metadata"],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )
        upstream = UpstreamOutputs(
            available_outputs={"policy_text"},
            output_types={}
        )

        result = evaluator.validate_signature_against_upstream(signature, upstream)
        assert result["score"] == 0.6
        assert result["validation_status"] == "passed_missing_optional"

    def test_available_ratio_calculation(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signature = MethodSignature(
            required_inputs=["policy_text", "dimension_id"],
            optional_inputs=["context", "metadata"],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )
        upstream = UpstreamOutputs(
            available_outputs={"policy_text", "context"},
            output_types={}
        )

        result = evaluator.validate_signature_against_upstream(signature, upstream)
        assert result["available_ratio"] == 0.5


class TestChainLayerEvaluation:
    def test_perfect_chain(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signature = MethodSignature(
            required_inputs=["policy_text"],
            optional_inputs=["metadata"],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )
        upstream = UpstreamOutputs(
            available_outputs={"policy_text", "metadata"},
            output_types={"policy_text": "str", "metadata": "dict"}
        )

        result = evaluator.evaluate(signature, upstream)
        assert result["chain_score"] == 1.0
        assert result["validation_status"] == "perfect"
        assert len(result["missing_required"]) == 0
        assert len(result["warnings"]) == 0

    def test_failed_chain_missing_required(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signature = MethodSignature(
            required_inputs=["policy_text", "dimension_id"],
            optional_inputs=[],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )
        upstream = UpstreamOutputs(
            available_outputs={"metadata"},
            output_types={}
        )

        result = evaluator.evaluate(signature, upstream)
        assert result["chain_score"] == 0.0
        assert result["validation_status"] == "failed_missing_required"
        assert len(result["missing_required"]) == 2

    def test_chain_with_warnings(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signature = MethodSignature(
            required_inputs=["policy_text"],
            optional_inputs=["context", "metadata"],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )
        upstream = UpstreamOutputs(
            available_outputs={"policy_text"},
            output_types={}
        )

        result = evaluator.evaluate(signature, upstream)
        assert "config" in result
        assert "score_thresholds" in result
        assert result["available_ratio"] < 1.0


class TestChainSequenceEvaluation:
    def test_simple_sequence(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signatures = [
            ("method1", MethodSignature(
                required_inputs=["input_data"],
                optional_inputs=[],
                critical_optional=[],
                output_type="dict",
                output_range=None
            )),
            ("method2", MethodSignature(
                required_inputs=["method1"],
                optional_inputs=[],
                critical_optional=[],
                output_type="dict",
                output_range=None
            )),
            ("method3", MethodSignature(
                required_inputs=["method1", "method2"],
                optional_inputs=[],
                critical_optional=[],
                output_type="dict",
                output_range=None
            ))
        ]
        initial_inputs = {"input_data"}

        result = evaluator.evaluate_chain_sequence(signatures, initial_inputs)
        assert result["sequence_score"] == 1.0
        assert result["failed_methods"] == 0
        assert result["total_methods"] == 3
        assert "method1" in result["final_available_outputs"]
        assert "method2" in result["final_available_outputs"]
        assert "method3" in result["final_available_outputs"]

    def test_sequence_with_failures(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signatures = [
            ("method1", MethodSignature(
                required_inputs=["missing_input"],
                optional_inputs=[],
                critical_optional=[],
                output_type="dict",
                output_range=None
            )),
            ("method2", MethodSignature(
                required_inputs=["method1"],
                optional_inputs=[],
                critical_optional=[],
                output_type="dict",
                output_range=None
            ))
        ]
        initial_inputs = {"input_data"}

        result = evaluator.evaluate_chain_sequence(signatures, initial_inputs)
        assert result["sequence_score"] < 1.0
        assert result["failed_methods"] >= 1

    def test_sequence_with_branching(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signatures = [
            ("method1", MethodSignature(
                required_inputs=["input_data"],
                optional_inputs=[],
                critical_optional=[],
                output_type="dict",
                output_range=None
            )),
            ("method2a", MethodSignature(
                required_inputs=["method1"],
                optional_inputs=[],
                critical_optional=[],
                output_type="dict",
                output_range=None
            )),
            ("method2b", MethodSignature(
                required_inputs=["method1"],
                optional_inputs=[],
                critical_optional=[],
                output_type="dict",
                output_range=None
            )),
            ("method3", MethodSignature(
                required_inputs=["method2a", "method2b"],
                optional_inputs=[],
                critical_optional=[],
                output_type="dict",
                output_range=None
            ))
        ]
        initial_inputs = {"input_data"}

        result = evaluator.evaluate_chain_sequence(signatures, initial_inputs)
        assert result["sequence_score"] == 1.0
        assert result["failed_methods"] == 0
        assert "method3" in result["final_available_outputs"]

    def test_sequence_with_critical_optional(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        signatures = [
            ("method1", MethodSignature(
                required_inputs=["input_data"],
                optional_inputs=["context"],
                critical_optional=["context"],
                output_type="dict",
                output_range=None
            )),
            ("method2", MethodSignature(
                required_inputs=["method1"],
                optional_inputs=[],
                critical_optional=[],
                output_type="dict",
                output_range=None
            ))
        ]
        initial_inputs = {"input_data"}

        result = evaluator.evaluate_chain_sequence(signatures, initial_inputs)
        assert result["sequence_score"] < 1.0
        assert result["method_results"][0]["score"] == 0.3
        assert result["method_results"][0]["status"] == "failed_missing_critical"

    def test_empty_sequence(self):
        config = create_default_chain_config()
        evaluator = ChainLayerEvaluator(config)

        result = evaluator.evaluate_chain_sequence([], {"input_data"})
        assert result["sequence_score"] == 0.0
        assert result["total_methods"] == 0
        assert result["failed_methods"] == 0
