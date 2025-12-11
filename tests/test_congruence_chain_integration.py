"""
Integration Tests for Congruence (@C) and Chain (@chain) Layer Evaluators

Tests the interaction between congruence and chain layer evaluators
in realistic pipeline scenarios.
"""

import pytest
from orchestration.congruence_layer import (
    CongruenceLayerEvaluator,
    OutputRangeSpec,
    SemanticTagSet,
    FusionRule,
    create_default_congruence_config
)
from orchestration.chain_layer import (
    ChainLayerEvaluator,
    MethodSignature,
    UpstreamOutputs,
    create_default_chain_config
)


class TestCongruenceChainIntegration:
    def test_executor_ensemble_with_chaining(self):
        """Test executor ensemble evaluation with chain validation."""
        congruence_config = create_default_congruence_config()
        chain_config = create_default_chain_config()
        
        congruence_eval = CongruenceLayerEvaluator(congruence_config)
        chain_eval = ChainLayerEvaluator(chain_config)

        executor_specs = {
            "CausalExtractor": {
                "signature": MethodSignature(
                    required_inputs=["policy_text", "dimension_id"],
                    optional_inputs=["context"],
                    critical_optional=["context"],
                    output_type="dict",
                    output_range=[0.0, 1.0]
                ),
                "range": OutputRangeSpec(min=0.0, max=1.0, output_type="dict"),
                "tags": SemanticTagSet(tags={"causal", "temporal"}, description=None)
            },
            "GoalAnalyzer": {
                "signature": MethodSignature(
                    required_inputs=["policy_text", "dimension_id"],
                    optional_inputs=["context"],
                    critical_optional=["context"],
                    output_type="dict",
                    output_range=[0.0, 1.0]
                ),
                "range": OutputRangeSpec(min=0.0, max=1.0, output_type="dict"),
                "tags": SemanticTagSet(tags={"causal", "goal-oriented"}, description=None)
            }
        }

        upstream = UpstreamOutputs(
            available_outputs={"policy_text", "dimension_id", "context"},
            output_types={"policy_text": "str", "dimension_id": "str", "context": "dict"}
        )

        chain_scores = {}
        for name, spec in executor_specs.items():
            result = chain_eval.evaluate(spec["signature"], upstream)
            chain_scores[name] = result["chain_score"]

        fusion = FusionRule(
            rule_type="aggregation",
            operator="weighted_avg",
            is_valid=True,
            description="Executor ensemble fusion"
        )
        
        congruence_result = congruence_eval.evaluate(
            executor_specs["CausalExtractor"]["range"],
            executor_specs["GoalAnalyzer"]["range"],
            executor_specs["CausalExtractor"]["tags"],
            executor_specs["GoalAnalyzer"]["tags"],
            fusion
        )

        assert all(score == 1.0 for score in chain_scores.values())
        assert congruence_result["C_play"] > 0.0
        assert congruence_result["c_scale"] == 1.0

    def test_pipeline_validation_sequence(self):
        """Test full pipeline validation with both evaluators."""
        chain_config = create_default_chain_config()
        chain_eval = ChainLayerEvaluator(chain_config)
        
        congruence_config = create_default_congruence_config()
        congruence_eval = CongruenceLayerEvaluator(congruence_config)

        method_signatures = [
            ("PolicyIngestor", MethodSignature(
                required_inputs=["raw_document"],
                optional_inputs=[],
                critical_optional=[],
                output_type="str",
                output_range=None
            )),
            ("PolicyProcessor", MethodSignature(
                required_inputs=["PolicyIngestor"],
                optional_inputs=["config"],
                critical_optional=[],
                output_type="dict",
                output_range=None
            )),
            ("CausalExtractor", MethodSignature(
                required_inputs=["PolicyProcessor"],
                optional_inputs=["semantic_model"],
                critical_optional=["semantic_model"],
                output_type="dict",
                output_range=[0.0, 1.0]
            ))
        ]

        chain_result = chain_eval.evaluate_chain_sequence(
            method_signatures,
            {"raw_document"}
        )

        assert chain_result["total_methods"] == 3
        assert chain_result["failed_methods"] >= 1

        processor_range = OutputRangeSpec(min=0.0, max=1.0, output_type="dict")
        extractor_range = OutputRangeSpec(min=0.0, max=1.0, output_type="dict")
        processor_tags = SemanticTagSet(tags={"text", "processing"}, description=None)
        extractor_tags = SemanticTagSet(tags={"causal", "temporal"}, description=None)
        
        fusion = FusionRule(
            rule_type="transformation",
            operator="normalize",
            is_valid=True,
            description=None
        )

        congruence_result = congruence_eval.evaluate(
            extractor_range, processor_range,
            extractor_tags, processor_tags,
            fusion
        )

        assert congruence_result["c_scale"] == 1.0
        assert congruence_result["c_sem"] == 0.0

    def test_ensemble_congruence_with_chain_failures(self):
        """Test congruence evaluation when chain validation fails."""
        chain_config = create_default_chain_config()
        chain_eval = ChainLayerEvaluator(chain_config)
        
        congruence_config = create_default_congruence_config()
        congruence_eval = CongruenceLayerEvaluator(congruence_config)

        signature = MethodSignature(
            required_inputs=["missing_input"],
            optional_inputs=[],
            critical_optional=[],
            output_type="dict",
            output_range=[0.0, 1.0]
        )
        
        upstream = UpstreamOutputs(
            available_outputs={"available_input"},
            output_types={}
        )

        chain_result = chain_eval.evaluate(signature, upstream)
        assert chain_result["chain_score"] == 0.0

        range1 = OutputRangeSpec(min=0.0, max=1.0, output_type="dict")
        range2 = OutputRangeSpec(min=0.0, max=1.0, output_type="dict")
        tags1 = SemanticTagSet(tags={"test"}, description=None)
        tags2 = SemanticTagSet(tags={"test"}, description=None)
        fusion = FusionRule(
            rule_type="aggregation",
            operator="sum",
            is_valid=True,
            description=None
        )

        congruence_result = congruence_eval.evaluate(
            range1, range2, tags1, tags2, fusion
        )
        
        assert congruence_result["C_play"] == 1.0

    def test_mixed_scores_aggregation(self):
        """Test aggregation of mixed chain and congruence scores."""
        chain_config = create_default_chain_config()
        chain_eval = ChainLayerEvaluator(chain_config)
        
        congruence_config = create_default_congruence_config()
        congruence_eval = CongruenceLayerEvaluator(congruence_config)

        methods = [
            {
                "signature": MethodSignature(
                    required_inputs=["input"],
                    optional_inputs=["context"],
                    critical_optional=["context"],
                    output_type="dict",
                    output_range=[0.0, 1.0]
                ),
                "range": OutputRangeSpec(min=0.0, max=1.0, output_type="dict"),
                "tags": SemanticTagSet(tags={"causal", "temporal"}, description=None)
            },
            {
                "signature": MethodSignature(
                    required_inputs=["input"],
                    optional_inputs=["metadata"],
                    critical_optional=[],
                    output_type="dict",
                    output_range=[0.0, 1.0]
                ),
                "range": OutputRangeSpec(min=0.0, max=1.0, output_type="dict"),
                "tags": SemanticTagSet(tags={"causal", "numeric"}, description=None)
            }
        ]

        upstream = UpstreamOutputs(
            available_outputs={"input"},
            output_types={"input": "str"}
        )

        chain_scores = []
        for method in methods:
            result = chain_eval.evaluate(method["signature"], upstream)
            chain_scores.append(result["chain_score"])

        fusion = FusionRule(
            rule_type="aggregation",
            operator="weighted_avg",
            is_valid=True,
            description=None
        )
        
        congruence_result = congruence_eval.evaluate(
            methods[0]["range"], methods[1]["range"],
            methods[0]["tags"], methods[1]["tags"],
            fusion
        )

        assert chain_scores[0] == 0.3
        assert chain_scores[1] == 1.0
        
        assert 0.0 < congruence_result["C_play"] < 1.0

        w_chain = 0.13
        w_congruence = 0.08
        
        combined_score = (
            (chain_scores[0] * w_chain) +
            (chain_scores[1] * w_chain) +
            (congruence_result["C_play"] * w_congruence)
        ) / (2 * w_chain + w_congruence)
        
        assert 0.0 <= combined_score <= 1.0

    def test_full_layer_evaluation_ensemble(self):
        """Test complete layer evaluation for an executor ensemble."""
        chain_config = create_default_chain_config()
        chain_eval = ChainLayerEvaluator(chain_config)
        
        congruence_config = create_default_congruence_config()
        congruence_eval = CongruenceLayerEvaluator(congruence_config)

        executors = [
            {
                "name": "D1_Q1_Executor",
                "signature": MethodSignature(
                    required_inputs=["policy_text", "dimension_id", "question_id"],
                    optional_inputs=["context", "metadata"],
                    critical_optional=["context"],
                    output_type="dict",
                    output_range=[0.0, 1.0]
                ),
                "range": OutputRangeSpec(min=0.0, max=1.0, output_type="dict"),
                "tags": SemanticTagSet(
                    tags={"causal", "temporal", "dimension_1"},
                    description="D1-Q1 executor"
                )
            },
            {
                "name": "D1_Q2_Executor",
                "signature": MethodSignature(
                    required_inputs=["policy_text", "dimension_id", "question_id"],
                    optional_inputs=["context", "metadata"],
                    critical_optional=["context"],
                    output_type="dict",
                    output_range=[0.0, 1.0]
                ),
                "range": OutputRangeSpec(min=0.0, max=1.0, output_type="dict"),
                "tags": SemanticTagSet(
                    tags={"causal", "numeric", "dimension_1"},
                    description="D1-Q2 executor"
                )
            },
            {
                "name": "D2_Q1_Executor",
                "signature": MethodSignature(
                    required_inputs=["policy_text", "dimension_id", "question_id"],
                    optional_inputs=["context", "metadata"],
                    critical_optional=["context"],
                    output_type="dict",
                    output_range=[0.0, 1.0]
                ),
                "range": OutputRangeSpec(min=0.0, max=1.0, output_type="dict"),
                "tags": SemanticTagSet(
                    tags={"goal-oriented", "strategic", "dimension_2"},
                    description="D2-Q1 executor"
                )
            }
        ]

        upstream = UpstreamOutputs(
            available_outputs={"policy_text", "dimension_id", "question_id", "context"},
            output_types={
                "policy_text": "str",
                "dimension_id": "str",
                "question_id": "str",
                "context": "dict"
            }
        )

        chain_results = {}
        for executor in executors:
            result = chain_eval.evaluate(executor["signature"], upstream)
            chain_results[executor["name"]] = {
                "chain_score": result["chain_score"],
                "status": result["validation_status"]
            }

        fusion = FusionRule(
            rule_type="aggregation",
            operator="weighted_avg",
            is_valid=True,
            description="Dimension-level fusion"
        )

        congruence_scores = {}
        for i in range(len(executors)):
            for j in range(i + 1, len(executors)):
                pair_key = f"{executors[i]['name']} <-> {executors[j]['name']}"
                result = congruence_eval.evaluate(
                    executors[i]["range"], executors[j]["range"],
                    executors[i]["tags"], executors[j]["tags"],
                    fusion
                )
                congruence_scores[pair_key] = result["C_play"]

        assert all(r["chain_score"] == 1.0 for r in chain_results.values())
        assert all(r["status"] == "perfect" for r in chain_results.values())
        
        d1_congruence = congruence_scores["D1_Q1_Executor <-> D1_Q2_Executor"]
        cross_dim_congruence = congruence_scores["D1_Q1_Executor <-> D2_Q1_Executor"]
        
        assert d1_congruence > cross_dim_congruence
