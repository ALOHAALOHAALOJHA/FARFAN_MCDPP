"""Integration tests for calibration influence on execution and aggregation."""

import pytest
from unittest.mock import Mock, MagicMock
from farfan_pipeline.phases.Phase_two.calibration_policy import (
    CalibrationPolicy,
    create_default_policy,
)


@pytest.mark.integration
class TestCalibrationInfluenceOnExecution:
    """Test calibration impact on method execution."""
    
    def test_high_calibration_enables_full_weight(self) -> None:
        """Test that high calibration scores result in full weight."""
        policy = create_default_policy(strict_mode=False)
        
        high_calibration_score = 0.9
        
        should_execute, reason = policy.should_execute_method(
            "test_method", high_calibration_score
        )
        assert should_execute is True
        assert "EXCELLENT" in reason
        
        weight = policy.compute_adjusted_weight(1.0, high_calibration_score)
        assert weight.adjusted_weight == 1.0
        assert weight.adjustment_factor == 1.0
    
    def test_low_calibration_reduces_weight(self) -> None:
        """Test that low calibration scores reduce weight."""
        policy = create_default_policy(strict_mode=False)
        
        low_calibration_score = 0.5
        
        should_execute, reason = policy.should_execute_method(
            "test_method", low_calibration_score
        )
        assert should_execute is True
        
        weight = policy.compute_adjusted_weight(1.0, low_calibration_score)
        assert weight.adjusted_weight < 1.0
        assert weight.adjustment_factor == 0.7
        assert weight.quality_band == "ACCEPTABLE"
    
    def test_poor_calibration_strict_mode_blocks_execution(self) -> None:
        """Test that very low calibration blocks execution in strict mode."""
        policy = CalibrationPolicy(strict_mode=True)
        
        poor_calibration_score = 0.25
        
        should_execute, reason = policy.should_execute_method(
            "test_method", poor_calibration_score
        )
        assert should_execute is False
        assert "below threshold" in reason
    
    def test_poor_calibration_permissive_mode_allows_execution(self) -> None:
        """Test that very low calibration allows execution in permissive mode."""
        policy = CalibrationPolicy(strict_mode=False)
        
        poor_calibration_score = 0.25
        
        should_execute, reason = policy.should_execute_method(
            "test_method", poor_calibration_score
        )
        assert should_execute is True
        assert "non-strict" in reason


@pytest.mark.integration
class TestCalibrationInfluenceOnAggregation:
    """Test calibration impact on aggregation weights."""
    
    def test_calibration_weights_vary_by_score(self) -> None:
        """Test that calibration weights vary appropriately by score."""
        policy = create_default_policy()
        
        test_cases = [
            (0.95, 1.0, "EXCELLENT"),
            (0.75, 0.9, "GOOD"),
            (0.55, 0.7, "ACCEPTABLE"),
            (0.35, 0.4, "POOR"),
        ]
        
        for score, expected_factor, expected_band in test_cases:
            weight = policy.compute_adjusted_weight(1.0, score)
            assert weight.adjustment_factor == expected_factor
            assert weight.quality_band == expected_band
            assert weight.adjusted_weight == expected_factor
    
    def test_calibration_weights_scale_base_weight(self) -> None:
        """Test that calibration factors scale with base weight."""
        policy = create_default_policy()
        
        calibration_score = 0.7
        base_weights = [0.5, 1.0, 2.0]
        
        for base_weight in base_weights:
            weight = policy.compute_adjusted_weight(base_weight, calibration_score)
            expected = base_weight * 0.9
            assert abs(weight.adjusted_weight - expected) < 0.001


@pytest.mark.integration
class TestCalibrationMetricsTracking:
    """Test calibration metrics and tracking functionality."""
    
    def test_metrics_recording_and_retrieval(self) -> None:
        """Test that metrics are properly recorded and retrieved."""
        policy = create_default_policy()
        
        for i in range(10):
            policy.record_influence(
                phase_id=2,
                method_id=f"method_{i}",
                calibration_score=0.8,
                weight_adjustment=0.1,
                influenced_output=True,
            )
        
        summary = policy.get_metrics_summary()
        assert summary["total_metrics"] == 10
        assert summary["influenced_outputs"] == 10
        assert summary["influence_rate"] == 1.0
    
    def test_calibration_drift_detection_stable(self) -> None:
        """Test drift detection with stable calibration scores."""
        policy = create_default_policy()
        
        for i in range(60):
            policy.record_influence(
                phase_id=2,
                method_id=f"method_{i}",
                calibration_score=0.8 + (i % 2) * 0.01,
                weight_adjustment=0.0,
                influenced_output=False,
            )
        
        drift = policy.detect_drift(window_size=50)
        assert drift["drift_detected"] is False
    
    def test_calibration_drift_detection_unstable(self) -> None:
        """Test drift detection with unstable calibration scores."""
        policy = create_default_policy()
        
        for i in range(60):
            score = 0.5 if i % 2 == 0 else 0.95
            policy.record_influence(
                phase_id=2,
                method_id=f"method_{i}",
                calibration_score=score,
                weight_adjustment=0.0,
                influenced_output=False,
            )
        
        drift = policy.detect_drift(window_size=50, threshold=0.15)
        assert drift["drift_detected"] is True


@pytest.mark.integration
class TestCalibrationEndToEnd:
    """End-to-end tests for calibration system."""
    
    def test_calibration_flow_through_execution(self) -> None:
        """Test complete calibration flow through execution."""
        policy = CalibrationPolicy(strict_mode=False)
        
        methods_with_scores = {
            "method_excellent": 0.9,
            "method_good": 0.7,
            "method_acceptable": 0.5,
            "method_poor": 0.3,
        }
        
        executed_methods = []
        weights = {}
        
        for method_id, cal_score in methods_with_scores.items():
            should_exec, _ = policy.should_execute_method(method_id, cal_score)
            
            if should_exec:
                executed_methods.append(method_id)
                weight = policy.compute_adjusted_weight(1.0, cal_score, method_id)
                weights[method_id] = weight.adjusted_weight
                
                policy.record_influence(
                    phase_id=2,
                    method_id=method_id,
                    calibration_score=cal_score,
                    weight_adjustment=1.0 - weight.adjusted_weight,
                    influenced_output=weight.adjusted_weight != 1.0,
                )
        
        assert len(executed_methods) == 4
        assert weights["method_excellent"] == 1.0
        assert weights["method_good"] < weights["method_excellent"]
        assert weights["method_acceptable"] < weights["method_good"]
        assert weights["method_poor"] < weights["method_acceptable"]
        
        summary = policy.get_metrics_summary()
        assert summary["total_metrics"] == 4
        assert summary["influenced_outputs"] == 3
    
    def test_no_fake_calibration_claims(self) -> None:
        """Test that calibration influence is real, not fake."""
        policy = create_default_policy()
        
        high_score_weight = policy.compute_adjusted_weight(1.0, 0.9)
        low_score_weight = policy.compute_adjusted_weight(1.0, 0.4)
        
        assert high_score_weight.adjusted_weight == 1.0
        assert low_score_weight.adjusted_weight == 0.7
        
        weight_difference = high_score_weight.adjusted_weight - low_score_weight.adjusted_weight
        assert abs(weight_difference - 0.3) < 0.001
        
        policy.record_influence(
            phase_id=2,
            method_id="high_method",
            calibration_score=0.9,
            weight_adjustment=0.0,
            influenced_output=False,
        )
        
        policy.record_influence(
            phase_id=2,
            method_id="low_method",
            calibration_score=0.4,
            weight_adjustment=0.6,
            influenced_output=True,
        )
        
        metrics = policy.export_metrics()
        assert len(metrics) == 2
        
        high_metric = next(m for m in metrics if m["method_id"] == "high_method")
        low_metric = next(m for m in metrics if m["method_id"] == "low_method")
        
        assert high_metric["influenced_output"] is False
        assert low_metric["influenced_output"] is True
        assert low_metric["weight_adjustment"] > 0


@pytest.mark.regression
class TestCalibrationRegressionPrevention:
    """Regression tests to prevent silent dropping of calibration."""
    
    def test_calibration_weights_always_applied(self) -> None:
        """Test that calibration weights are always applied when scores present."""
        policy = create_default_policy()
        
        calibration_scores = [0.9, 0.7, 0.5, 0.3]
        
        for score in calibration_scores:
            weight = policy.compute_adjusted_weight(1.0, score)
            
            assert weight.calibration_score == score
            assert weight.base_weight == 1.0
            assert weight.adjusted_weight > 0.0
            
            if score >= 0.8:
                assert weight.adjusted_weight == 1.0
            elif score >= 0.6:
                assert weight.adjusted_weight == 0.9
            elif score >= 0.4:
                assert weight.adjusted_weight == 0.7
            else:
                assert weight.adjusted_weight == 0.4
    
    def test_calibration_influence_always_recorded(self) -> None:
        """Test that calibration influence is always recorded."""
        policy = create_default_policy()
        
        initial_count = len(policy.export_metrics())
        assert initial_count == 0
        
        policy.record_influence(
            phase_id=2,
            method_id="test_method",
            calibration_score=0.7,
            weight_adjustment=0.1,
            influenced_output=True,
        )
        
        final_count = len(policy.export_metrics())
        assert final_count == 1
    
    def test_drift_detection_never_silent(self) -> None:
        """Test that drift detection never silently fails."""
        policy = create_default_policy()
        
        for i in range(100):
            score = 0.3 + (i % 10) * 0.05
            policy.record_influence(
                phase_id=2,
                method_id=f"method_{i}",
                calibration_score=score,
                weight_adjustment=0.0,
                influenced_output=False,
            )
        
        drift = policy.detect_drift(window_size=50)
        
        assert "drift_detected" in drift
        assert "mean_score" in drift
        assert "std_score" in drift
        assert drift["window_size"] == 50
        assert drift["total_metrics"] == 50
