"""
Tests for Meta Layer (@m) Configuration and Evaluator
"""

import pytest
from src.orchestration.meta_layer import (
    MetaLayerConfig,
    MetaLayerEvaluator,
    TransparencyArtifacts,
    GovernanceArtifacts,
    CostMetrics,
    create_default_config,
    compute_config_hash
)


class TestMetaLayerConfig:
    def test_config_creation_valid(self):
        config = MetaLayerConfig(
            w_transparency=0.5,
            w_governance=0.4,
            w_cost=0.1,
            transparency_requirements={
                "require_formula_export": True,
                "require_trace_complete": True,
                "require_logs_conform": True
            },
            governance_requirements={
                "require_version_tag": True,
                "require_config_hash": True,
                "require_signature": False
            },
            cost_thresholds={
                "threshold_fast": 1.0,
                "threshold_acceptable": 5.0,
                "threshold_memory_normal": 512.0
            }
        )
        assert config.w_transparency == 0.5
        assert config.w_governance == 0.4
        assert config.w_cost == 0.1

    def test_config_weights_sum_validation(self):
        with pytest.raises(ValueError, match="must sum to 1.0"):
            MetaLayerConfig(
                w_transparency=0.5,
                w_governance=0.3,
                w_cost=0.1,
                transparency_requirements={
                    "require_formula_export": True,
                    "require_trace_complete": True,
                    "require_logs_conform": True
                },
                governance_requirements={
                    "require_version_tag": True,
                    "require_config_hash": True,
                    "require_signature": False
                },
                cost_thresholds={
                    "threshold_fast": 1.0,
                    "threshold_acceptable": 5.0,
                    "threshold_memory_normal": 512.0
                }
            )

    def test_config_negative_weights_validation(self):
        with pytest.raises(ValueError, match="must be non-negative"):
            MetaLayerConfig(
                w_transparency=0.6,
                w_governance=0.5,
                w_cost=-0.1,
                transparency_requirements={
                    "require_formula_export": True,
                    "require_trace_complete": True,
                    "require_logs_conform": True
                },
                governance_requirements={
                    "require_version_tag": True,
                    "require_config_hash": True,
                    "require_signature": False
                },
                cost_thresholds={
                    "threshold_fast": 1.0,
                    "threshold_acceptable": 5.0,
                    "threshold_memory_normal": 512.0
                }
            )

    def test_default_config(self):
        config = create_default_config()
        assert config.w_transparency == 0.5
        assert config.w_governance == 0.4
        assert config.w_cost == 0.1
        assert config.transparency_requirements["require_formula_export"] is True
        assert config.governance_requirements["require_version_tag"] is True
        assert config.cost_thresholds["threshold_fast"] == 1.0


class TestTransparencyEvaluation:
    def test_full_transparency_score(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        artifacts: TransparencyArtifacts = {
            "formula_export": "Cal(I) = 0.5*x_@b + 0.3*Choquet_term",
            "trace": "Phase 0 validation step 1 method execution",
            "logs": {
                "timestamp": "2024-12-09T00:00:00Z",
                "level": "INFO",
                "method_name": "test",
                "phase": "test",
                "message": "test"
            }
        }
        
        log_schema = {
            "required": ["timestamp", "level", "method_name", "phase", "message"]
        }
        
        score = evaluator.evaluate_transparency(artifacts, log_schema)
        assert score == 1.0

    def test_partial_transparency_score_2_of_3(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        artifacts: TransparencyArtifacts = {
            "formula_export": "Choquet integral expanded formula Cal(I)",
            "trace": "Phase 1 step execution trace method call",
            "logs": None
        }
        
        score = evaluator.evaluate_transparency(artifacts, None)
        assert score == 0.7

    def test_partial_transparency_score_1_of_3(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        artifacts: TransparencyArtifacts = {
            "formula_export": None,
            "trace": "Valid trace with step and phase markers",
            "logs": None
        }
        
        score = evaluator.evaluate_transparency(artifacts, None)
        assert score == 0.4

    def test_zero_transparency_score(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        artifacts: TransparencyArtifacts = {
            "formula_export": None,
            "trace": None,
            "logs": None
        }
        
        score = evaluator.evaluate_transparency(artifacts, None)
        assert score == 0.0


class TestGovernanceEvaluation:
    def test_full_governance_score(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        artifacts: GovernanceArtifacts = {
            "version_tag": "v2.1.3",
            "config_hash": "a" * 64,
            "signature": None
        }
        
        score = evaluator.evaluate_governance(artifacts)
        assert score == 1.0

    def test_partial_governance_score_2_of_3(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        artifacts: GovernanceArtifacts = {
            "version_tag": "v1.5.0",
            "config_hash": "",
            "signature": None
        }
        
        score = evaluator.evaluate_governance(artifacts)
        assert score == 0.66

    def test_partial_governance_score_1_of_3(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        artifacts: GovernanceArtifacts = {
            "version_tag": "unknown",
            "config_hash": "b" * 64,
            "signature": None
        }
        
        score = evaluator.evaluate_governance(artifacts)
        assert score == 0.66

    def test_zero_governance_score(self):
        config = MetaLayerConfig(
            w_transparency=0.5,
            w_governance=0.4,
            w_cost=0.1,
            transparency_requirements={
                "require_formula_export": True,
                "require_trace_complete": True,
                "require_logs_conform": True
            },
            governance_requirements={
                "require_version_tag": True,
                "require_config_hash": True,
                "require_signature": True
            },
            cost_thresholds={
                "threshold_fast": 1.0,
                "threshold_acceptable": 5.0,
                "threshold_memory_normal": 512.0
            }
        )
        evaluator = MetaLayerEvaluator(config)
        
        artifacts: GovernanceArtifacts = {
            "version_tag": "unknown",
            "config_hash": "",
            "signature": None
        }
        
        score = evaluator.evaluate_governance(artifacts)
        assert score == 0.0

    def test_invalid_version_tags(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        for invalid_version in ["1.0", "unknown", "0.0.0", ""]:
            assert not evaluator._has_valid_version(invalid_version)


class TestCostEvaluation:
    def test_optimal_cost_score(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        metrics: CostMetrics = {
            "execution_time_s": 0.5,
            "memory_usage_mb": 256.0
        }
        
        score = evaluator.evaluate_cost(metrics)
        assert score == 1.0

    def test_acceptable_cost_score(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        metrics: CostMetrics = {
            "execution_time_s": 3.0,
            "memory_usage_mb": 400.0
        }
        
        score = evaluator.evaluate_cost(metrics)
        assert score == 0.8

    def test_poor_cost_score_time(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        metrics: CostMetrics = {
            "execution_time_s": 6.0,
            "memory_usage_mb": 256.0
        }
        
        score = evaluator.evaluate_cost(metrics)
        assert score == 0.5

    def test_poor_cost_score_memory(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        metrics: CostMetrics = {
            "execution_time_s": 0.5,
            "memory_usage_mb": 1024.0
        }
        
        score = evaluator.evaluate_cost(metrics)
        assert score == 0.5

    def test_negative_metrics_validation(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        metrics: CostMetrics = {
            "execution_time_s": -1.0,
            "memory_usage_mb": 256.0
        }
        
        score = evaluator.evaluate_cost(metrics)
        assert score == 0.0


class TestFullEvaluation:
    def test_perfect_score(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        transparency_artifacts: TransparencyArtifacts = {
            "formula_export": "Cal(I) = Choquet expanded formula",
            "trace": "Complete trace with phase and step markers",
            "logs": {
                "timestamp": "2024-12-09T00:00:00Z",
                "level": "INFO",
                "method_name": "test",
                "phase": "test",
                "message": "test"
            }
        }
        
        governance_artifacts: GovernanceArtifacts = {
            "version_tag": "v2.1.3",
            "config_hash": "a" * 64,
            "signature": None
        }
        
        cost_metrics: CostMetrics = {
            "execution_time_s": 0.8,
            "memory_usage_mb": 256.0
        }
        
        log_schema = {
            "required": ["timestamp", "level", "method_name", "phase", "message"]
        }
        
        result = evaluator.evaluate(
            transparency_artifacts,
            governance_artifacts,
            cost_metrics,
            log_schema
        )
        
        assert result["m_transparency"] == 1.0
        assert result["m_governance"] == 1.0
        assert result["m_cost"] == 1.0
        assert result["score"] == 1.0
        assert result["weights"]["w_transparency"] == 0.5
        assert result["weights"]["w_governance"] == 0.4
        assert result["weights"]["w_cost"] == 0.1

    def test_weighted_average_calculation(self):
        config = create_default_config()
        evaluator = MetaLayerEvaluator(config)
        
        transparency_artifacts: TransparencyArtifacts = {
            "formula_export": "Cal(I) x_@b",
            "trace": "trace step",
            "logs": None
        }
        
        governance_artifacts: GovernanceArtifacts = {
            "version_tag": "v1.0.0",
            "config_hash": "",
            "signature": None
        }
        
        cost_metrics: CostMetrics = {
            "execution_time_s": 6.0,
            "memory_usage_mb": 256.0
        }
        
        result = evaluator.evaluate(
            transparency_artifacts,
            governance_artifacts,
            cost_metrics,
            None
        )
        
        expected_score = 0.5 * 0.4 + 0.4 * 0.66 + 0.1 * 0.5
        assert abs(result["score"] - expected_score) < 1e-6


class TestConfigHash:
    def test_config_hash_generation(self):
        config_data = {
            "method": "test",
            "params": {"a": 1, "b": 2}
        }
        
        hash1 = compute_config_hash(config_data)
        assert len(hash1) == 64
        assert all(c in "0123456789abcdef" for c in hash1)

    def test_config_hash_deterministic(self):
        config_data = {
            "method": "test",
            "params": {"a": 1, "b": 2}
        }
        
        hash1 = compute_config_hash(config_data)
        hash2 = compute_config_hash(config_data)
        assert hash1 == hash2

    def test_config_hash_key_order_invariant(self):
        config1 = {"a": 1, "b": 2, "c": 3}
        config2 = {"c": 3, "a": 1, "b": 2}
        
        hash1 = compute_config_hash(config1)
        hash2 = compute_config_hash(config2)
        assert hash1 == hash2

    def test_config_hash_different_for_different_data(self):
        config1 = {"method": "test1"}
        config2 = {"method": "test2"}
        
        hash1 = compute_config_hash(config1)
        hash2 = compute_config_hash(config2)
        assert hash1 != hash2
