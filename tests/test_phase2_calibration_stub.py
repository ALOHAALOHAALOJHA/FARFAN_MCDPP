"""Tests for Phase 2 executor calibration integration stub.

Verifies:
1. CalibrationResult is properly returned
2. Contract preconditions are enforced
3. Contract postconditions are satisfied
4. get_executor_config returns valid configuration
5. Stub implementation is deterministic
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# Import executor_calibration_integration directly without __init__.py
spec = importlib.util.spec_from_file_location(
    "executor_calibration_integration",
    Path(__file__).resolve().parent.parent / "src" / "farfan_pipeline" / "phases" / "Phase_two" / "phase2_95_03_executor_calibration_integration.py"
)
assert spec is not None and spec.loader is not None
executor_calibration_integration = importlib.util.module_from_spec(spec)
sys.modules["executor_calibration_integration"] = executor_calibration_integration
spec.loader.exec_module(executor_calibration_integration)

CalibrationMetrics = executor_calibration_integration.CalibrationMetrics
CalibrationResult = executor_calibration_integration.CalibrationResult
instrument_executor = executor_calibration_integration.instrument_executor
get_executor_config = executor_calibration_integration.get_executor_config


class TestInstrumentExecutor:
    """Test instrument_executor stub implementation."""
    
    def test_instrument_executor_returns_calibration_result(self) -> None:
        """Test that instrument_executor returns CalibrationResult."""
        result = instrument_executor(
            executor_id="test_executor",
            context={"test": "context"},
            runtime_ms=100.0,
            memory_mb=50.0,
            methods_executed=5,
            methods_succeeded=4,
        )
        
        assert isinstance(result, CalibrationResult)
        assert result.quality_score >= 0.0
        assert result.quality_score <= 1.0
    
    def test_precondition_non_empty_executor_id(self) -> None:
        """Test that empty executor_id raises ValueError."""
        with pytest.raises(ValueError, match="executor_id cannot be empty"):
            instrument_executor(
                executor_id="",
                context={},
                runtime_ms=100.0,
                memory_mb=50.0,
                methods_executed=5,
                methods_succeeded=5,
            )
    
    def test_precondition_non_negative_runtime(self) -> None:
        """Test that negative runtime_ms raises ValueError."""
        with pytest.raises(ValueError, match="runtime_ms must be non-negative"):
            instrument_executor(
                executor_id="test",
                context={},
                runtime_ms=-1.0,
                memory_mb=50.0,
                methods_executed=5,
                methods_succeeded=5,
            )
    
    def test_precondition_non_negative_memory(self) -> None:
        """Test that negative memory_mb raises ValueError."""
        with pytest.raises(ValueError, match="memory_mb must be non-negative"):
            instrument_executor(
                executor_id="test",
                context={},
                runtime_ms=100.0,
                memory_mb=-1.0,
                methods_executed=5,
                methods_succeeded=5,
            )
    
    def test_precondition_succeeded_not_exceeding_executed(self) -> None:
        """Test that methods_succeeded cannot exceed methods_executed."""
        with pytest.raises(ValueError, match="methods_succeeded.*cannot exceed.*methods_executed"):
            instrument_executor(
                executor_id="test",
                context={},
                runtime_ms=100.0,
                memory_mb=50.0,
                methods_executed=5,
                methods_succeeded=10,
            )
    
    def test_postcondition_quality_score_in_range(self) -> None:
        """Test postcondition: quality_score is in [0, 1]."""
        result = instrument_executor(
            executor_id="test",
            context={},
            runtime_ms=100.0,
            memory_mb=50.0,
            methods_executed=5,
            methods_succeeded=5,
        )
        
        assert result.quality_score >= 0.0
        assert result.quality_score <= 1.0
    
    def test_postcondition_metrics_match_input(self) -> None:
        """Test postcondition: metrics match input values."""
        result = instrument_executor(
            executor_id="test",
            context={},
            runtime_ms=123.45,
            memory_mb=67.89,
            methods_executed=10,
            methods_succeeded=8,
        )
        
        assert result.metrics.runtime_ms == 123.45
        assert result.metrics.memory_mb == 67.89
        assert result.metrics.methods_executed == 10
        assert result.metrics.methods_succeeded == 8
    
    def test_deterministic_for_same_inputs(self) -> None:
        """Test that stub returns same result for same inputs."""
        params = {
            "executor_id": "test",
            "context": {"key": "value"},
            "runtime_ms": 100.0,
            "memory_mb": 50.0,
            "methods_executed": 5,
            "methods_succeeded": 5,
        }
        
        result1 = instrument_executor(**params)
        result2 = instrument_executor(**params)
        
        assert result1.quality_score == result2.quality_score
        assert result1.aggregation_method == result2.aggregation_method


class TestGetExecutorConfig:
    """Test get_executor_config stub implementation."""
    
    def test_returns_valid_config_dict(self) -> None:
        """Test that get_executor_config returns valid configuration."""
        config = get_executor_config("test_executor", "D1", "Q1")
        
        assert isinstance(config, dict)
        assert len(config) > 0
    
    def test_config_has_required_keys(self) -> None:
        """Test that config contains expected runtime parameters."""
        config = get_executor_config("test_executor", "D1", "Q1")
        
        # Conservative defaults should be present
        assert "timeout_seconds" in config
        assert "max_retries" in config
        assert "memory_limit_mb" in config
    
    def test_precondition_non_empty_executor_id(self) -> None:
        """Test that empty executor_id raises ValueError."""
        with pytest.raises(ValueError, match="executor_id cannot be empty"):
            get_executor_config("", "D1", "Q1")
    
    def test_precondition_non_empty_dimension(self) -> None:
        """Test that empty dimension raises ValueError."""
        with pytest.raises(ValueError, match="dimension cannot be empty"):
            get_executor_config("test", "", "Q1")
    
    def test_precondition_non_empty_question(self) -> None:
        """Test that empty question raises ValueError."""
        with pytest.raises(ValueError, match="question cannot be empty"):
            get_executor_config("test", "D1", "")
    
    def test_deterministic_for_same_inputs(self) -> None:
        """Test that stub returns same config for same inputs."""
        config1 = get_executor_config("test", "D1", "Q1")
        config2 = get_executor_config("test", "D1", "Q1")
        
        assert config1 == config2


class TestCalibrationMetrics:
    """Test CalibrationMetrics dataclass."""
    
    def test_metrics_creation(self) -> None:
        """Test that CalibrationMetrics can be created."""
        metrics = CalibrationMetrics(
            runtime_ms=100.0,
            memory_mb=50.0,
            methods_executed=5,
            methods_succeeded=4,
        )
        
        assert metrics.runtime_ms == 100.0
        assert metrics.memory_mb == 50.0
        assert metrics.methods_executed == 5
        assert metrics.methods_succeeded == 4


class TestCalibrationResult:
    """Test CalibrationResult dataclass."""
    
    def test_result_creation(self) -> None:
        """Test that CalibrationResult can be created."""
        metrics = CalibrationMetrics(100.0, 50.0, 5, 4)
        result = CalibrationResult(
            quality_score=0.85,
            layer_scores={"layer1": 0.9, "layer2": 0.8},
            layers_used=["layer1", "layer2"],
            aggregation_method="test",
            metrics=metrics,
        )
        
        assert result.quality_score == 0.85
        assert len(result.layer_scores) == 2
        assert len(result.layers_used) == 2
        assert result.aggregation_method == "test"
        assert result.metrics is metrics
