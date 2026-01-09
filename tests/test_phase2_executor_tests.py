"""
Test suite for executor calibration integration.

PHASE_LABEL: Phase 2

Tests verify:
1. All 30+ executors are instrumented with calibration calls
2. Calibration data (WHAT) is loaded from intrinsic_calibration.json
3. Runtime parameters (HOW) are loaded from ExecutorConfig
4. No hardcoded calibration values in executor code
5. Layer assignments are correct (role:SCORE_Q with all 8 layers)
6. Choquet integral aggregation works correctly
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List

import pytest

from executor_calibration_integration import (
    CalibrationIntegration,
    CalibrationContext,
    CalibrationMetrics,
    CalibrationResult,
    instrument_executor,
    get_executor_config,
    EXECUTOR_REQUIRED_LAYERS,
    LAYER_WEIGHTS,
    INTERACTION_WEIGHTS,
)


# Test data: all 30 executor IDs
ALL_EXECUTOR_IDS = [
    "D1_Q1_QuantitativeBaselineExtractor",
    "D1_Q2_ProblemDimensioningAnalyzer",
    "D1_Q3_BudgetAllocationTracer",
    "D1_Q4_InstitutionalCapacityIdentifier",
    "D1_Q5_ScopeJustificationValidator",
    "D2_Q1_StructuredPlanningValidator",
    "D2_Q2_InterventionLogicInferencer",
    "D2_Q3_RootCauseLinkageAnalyzer",
    "D2_Q4_RiskManagementAnalyzer",
    "D2_Q5_StrategicCoherenceEvaluator",
    "D3_Q1_IndicatorQualityValidator",
    "D3_Q2_TargetProportionalityAnalyzer",
    "D3_Q3_TraceabilityValidator",
    "D3_Q4_TechnicalFeasibilityEvaluator",
    "D3_Q5_OutputOutcomeLinkageAnalyzer",
    "D4_Q1_OutcomeMetricsValidator",
    "D4_Q2_CausalChainValidator",
    "D4_Q3_AmbitionJustificationAnalyzer",
    "D4_Q4_ProblemSolvencyEvaluator",
    "D4_Q5_VerticalAlignmentValidator",
    "D5_Q1_LongTermVisionAnalyzer",
    "D5_Q2_CompositeMeasurementValidator",
    "D5_Q3_IntangibleMeasurementAnalyzer",
    "D5_Q4_SystemicRiskEvaluator",
    "D5_Q5_RealismAndSideEffectsAnalyzer",
    "D6_Q1_ExplicitTheoryBuilder",
    "D6_Q2_LogicalProportionalityValidator",
    "D6_Q3_ValidationTestingAnalyzer",
    "D6_Q4_FeedbackLoopAnalyzer",
    "D6_Q5_ContextualAdaptabilityEvaluator",
]


class TestExecutorCalibrationIntegration:
    """Test suite for calibration integration system."""
    
    def test_all_executors_count(self):
        """Verify we have exactly 30 executors."""
        assert len(ALL_EXECUTOR_IDS) == 30, \
            f"Expected 30 executors, found {len(ALL_EXECUTOR_IDS)}"
    
    def test_executor_id_format(self):
        """Verify all executor IDs follow D[1-6]_Q[1-5]_Name format."""
        import re
        pattern = re.compile(r"^D[1-6]_Q[1-5]_\w+$")
        
        for executor_id in ALL_EXECUTOR_IDS:
            assert pattern.match(executor_id), \
                f"Executor ID {executor_id} does not match expected format"
    
    def test_calibration_integration_initialization(self):
        """Test CalibrationIntegration can be initialized."""
        integration = CalibrationIntegration()
        
        assert integration.calibration_data is not None
        assert integration.questionnaire_data is not None
        assert isinstance(integration.calibration_data, dict)
        assert isinstance(integration.questionnaire_data, dict)
    
    def test_layer_requirements(self):
        """Verify all executors require the correct 8 layers."""
        expected_layers = {"@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"}
        actual_layers = set(EXECUTOR_REQUIRED_LAYERS)
        
        assert actual_layers == expected_layers, \
            f"Layer mismatch: expected {expected_layers}, got {actual_layers}"
    
    def test_layer_weights_sum(self):
        """Verify layer weights + interaction weights sum to ~1.0."""
        linear_sum = sum(LAYER_WEIGHTS.values())
        interaction_sum = sum(INTERACTION_WEIGHTS.values())
        total = linear_sum + interaction_sum
        
        assert abs(total - 1.0) < 0.01, \
            f"Weights should sum to 1.0, got {total}"
    
    def test_instrument_executor_basic(self):
        """Test basic executor instrumentation."""
        context = {
            "document_text": "Test document",
            "policy_area": "PA01",
            "unit_id": "test_unit"
        }
        
        result = instrument_executor(
            executor_id="D3_Q2_TargetProportionalityAnalyzer",
            context=context,
            runtime_ms=1500.0,
            memory_mb=256.0,
            methods_executed=21,
            methods_succeeded=21
        )
        
        assert isinstance(result, CalibrationResult)
        assert result.method_id == "farfan_pipeline.core.orchestrator.executors.D3_Q2_TargetProportionalityAnalyzer"
        assert result.context.dimension == "D3"
        assert result.context.question == "Q2"
        assert result.metrics.runtime_ms == 1500.0
        assert result.metrics.memory_mb == 256.0
        assert 0.0 <= result.quality_score <= 1.0
        assert len(result.layer_scores) == 8
        assert result.aggregation_method == "choquet"
    
    def test_quality_score_calculation(self):
        """Test quality score calculation for various executors."""
        integration = CalibrationIntegration()
        
        for executor_id in ALL_EXECUTOR_IDS[:5]:  # Test first 5
            parts = executor_id.split("_")
            dimension = parts[0]
            question = parts[1]
            
            context = CalibrationContext(
                question=question,
                dimension=dimension,
                executor_class=executor_id
            )
            
            quality_score, layer_scores = integration.calculate_quality_score(
                f"farfan_pipeline.core.orchestrator.executors.{executor_id}",
                context
            )
            
            assert 0.0 <= quality_score <= 1.0, \
                f"Quality score {quality_score} out of range for {executor_id}"
            assert len(layer_scores) == 8, \
                f"Expected 8 layer scores, got {len(layer_scores)} for {executor_id}"
    
    def test_executor_config_loading(self):
        """Test loading executor-specific configuration."""
        config = get_executor_config(
            executor_id="D3_Q2_TargetProportionalityAnalyzer",
            dimension="D3",
            question="Q2"
        )
        
        assert config["executor_id"] == "D3_Q2_TargetProportionalityAnalyzer"
        assert config["dimension"] == "D3"
        assert config["question"] == "Q2"
        assert config["role"] == "SCORE_Q"
        assert len(config["required_layers"]) == 8
        assert "layer_weights" in config
        assert "interaction_weights" in config
    
    def test_no_hardcoded_calibration_values(self):
        """Verify no hardcoded calibration values in executor code."""
        executors_file = Path(__file__).resolve().parent / "executors.py"
        
        with open(executors_file) as f:
            content = f.read()
        
        # Check that calibration-related constants are NOT defined
        forbidden_patterns = [
            "QUALITY_SCORE =",
            "CALIBRATION_VALUE =",
            "BASE_SCORE =",
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in content, \
                f"Found hardcoded calibration pattern: {pattern}"
    
    def test_calibration_parametrization_separation(self):
        """Verify calibration and parametrization are properly separated."""
        # Calibration data should NOT contain runtime parameters
        integration = CalibrationIntegration()
        calibration_data = integration.calibration_data
        
        forbidden_runtime_keys = ["timeout_s", "retry", "temperature", "max_tokens"]
        
        def check_dict_recursive(d: Dict, path: str = "") -> None:
            for key, value in d.items():
                current_path = f"{path}.{key}" if path else key
                assert key not in forbidden_runtime_keys, \
                    f"Found runtime parameter {key} in calibration data at {current_path}"
                if isinstance(value, dict):
                    check_dict_recursive(value, current_path)
        
        check_dict_recursive(calibration_data)
    
    def test_executor_config_files_exist(self):
        """Verify executor config files exist for sample executors."""
        config_dir = Path(__file__).resolve().parent / "executor_configs"
        
        sample_executors = [
            "D1_Q1_QuantitativeBaselineExtractor",
            "D3_Q2_TargetProportionalityAnalyzer",
            "D6_Q1_ExplicitTheoryBuilder",
        ]
        
        for executor_id in sample_executors:
            config_file = config_dir / f"{executor_id}.json"
            assert config_file.exists(), \
                f"Config file not found: {config_file}"
            
            with open(config_file) as f:
                config = json.load(f)
            
            assert config["executor_id"] == executor_id
            assert "runtime_parameters" in config
            assert "thresholds" in config
            assert "required_layers" in config
    
    def test_calibration_report_completeness(self):
        """Verify calibration report documents all 30 executors."""
        report_file = Path(__file__).resolve().parent / "executor_calibration_report.json"
        
        with open(report_file) as f:
            report = json.load(f)
        
        assert report["metadata"]["total_executors"] == 30
        assert len(report["executors"]) == 30
        
        reported_ids = {e["executor_id"] for e in report["executors"]}
        expected_ids = set(ALL_EXECUTOR_IDS)
        
        assert reported_ids == expected_ids, \
            f"Report missing executors: {expected_ids - reported_ids}"
    
    def test_layer_score_retrieval(self):
        """Test retrieving individual layer scores."""
        integration = CalibrationIntegration()
        context = CalibrationContext(
            question="Q2",
            dimension="D3",
            executor_class="D3_Q2_TargetProportionalityAnalyzer"
        )
        
        for layer in EXECUTOR_REQUIRED_LAYERS:
            score = integration.get_layer_score(layer, context)
            assert 0.0 <= score <= 1.0, \
                f"Layer {layer} score {score} out of range"
    
    def test_choquet_aggregation(self):
        """Test Choquet integral aggregation."""
        integration = CalibrationIntegration()
        context = CalibrationContext(
            question="Q2",
            dimension="D3",
            executor_class="D3_Q2_TargetProportionalityAnalyzer"
        )
        
        quality_score, layer_scores = integration.calculate_quality_score(
            "farfan_pipeline.core.orchestrator.executors.D3_Q2_TargetProportionalityAnalyzer",
            context
        )
        
        # Verify Choquet components
        linear_sum = sum(
            LAYER_WEIGHTS.get(layer, 0.0) * score
            for layer, score in layer_scores.items()
        )
        
        interaction_sum = 0.0
        for (l1, l2), weight in INTERACTION_WEIGHTS.items():
            if l1 in layer_scores and l2 in layer_scores:
                interaction_sum += weight * min(layer_scores[l1], layer_scores[l2])
        
        expected_score = linear_sum + interaction_sum
        
        assert abs(quality_score - expected_score) < 0.01, \
            f"Choquet aggregation mismatch: {quality_score} != {expected_score}"


class TestExecutorInstrumentation:
    """Test individual executor instrumentation."""
    
    @pytest.mark.parametrize("executor_id", ALL_EXECUTOR_IDS)
    def test_executor_instrumentation(self, executor_id: str):
        """Test instrumentation for each executor."""
        parts = executor_id.split("_")
        dimension = parts[0]
        question = parts[1]
        
        context = {
            "document_text": "Test document",
            "policy_area": "PA01",
            "unit_id": "test_unit"
        }
        
        result = instrument_executor(
            executor_id=executor_id,
            context=context,
            runtime_ms=1000.0,
            memory_mb=128.0,
            methods_executed=10,
            methods_succeeded=10
        )
        
        assert result.context.dimension == dimension
        assert result.context.question == question
        assert result.quality_score >= 0.0
        assert result.quality_score <= 1.0
        assert len(result.layers_used) == 8


class TestConfigurationLoading:
    """Test configuration loading from multiple sources."""
    
    def test_config_hierarchy_cli_env_json(self):
        """Test config loading hierarchy: CLI > ENV > JSON."""
        # This would test the actual ExecutorConfig class
        # which should load from CLI args, then ENV vars, then JSON files
        # Placeholder for actual implementation
        pass
    
    def test_executor_config_schema(self):
        """Test executor config files follow correct schema."""
        config_dir = Path(__file__).resolve().parent / "executor_configs"
        template_file = config_dir / "executor_config_template.json"
        
        if not template_file.exists():
            pytest.skip("Template file not found")
        
        with open(template_file) as f:
            template = json.load(f)
        
        required_keys = [
            "executor_id",
            "dimension",
            "question",
            "role",
            "required_layers",
            "runtime_parameters",
            "thresholds",
            "epistemic_mix",
            "contextual_params"
        ]
        
        for key in required_keys:
            assert key in template, f"Template missing required key: {key}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
