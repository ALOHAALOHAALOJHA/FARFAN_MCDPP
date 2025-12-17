"""Tests for calibration policy system."""

import pytest
from farfan_pipeline.phases.Phase_two.calibration_policy import (
    CalibrationPolicy,
    CalibrationWeight,
    create_default_policy,
)


class TestCalibrationPolicy:
    """Test calibration policy decisions."""
    
    def test_quality_band_classification(self) -> None:
        """Test quality band classification using FARFAN MICRO_LEVELS."""
        policy = create_default_policy()
        
        # FARFAN-canonical bands: EXCELENTE (0.85+), BUENO (0.70-0.85), ACEPTABLE (0.55-0.70), INSUFICIENTE (<0.55)
        assert policy.get_quality_band(0.95) == "EXCELENTE"
        assert policy.get_quality_band(0.85) == "EXCELENTE"
        assert policy.get_quality_band(0.80) == "BUENO"
        assert policy.get_quality_band(0.70) == "BUENO"
        assert policy.get_quality_band(0.65) == "ACEPTABLE"
        assert policy.get_quality_band(0.55) == "ACEPTABLE"
        assert policy.get_quality_band(0.50) == "INSUFICIENTE"
        assert policy.get_quality_band(0.30) == "INSUFICIENTE"
    
    def test_method_execution_decision_strict_mode(self) -> None:
        """Test method execution decisions in strict mode."""
        policy = CalibrationPolicy(strict_mode=True)
        
        should_execute, reason = policy.should_execute_method("method_1", 0.85)
        assert should_execute is True
        assert "EXCELENTE" in reason
        
        should_execute, reason = policy.should_execute_method("method_2", 0.45)
        assert should_execute is False
        assert "below threshold" in reason
        
        should_execute, reason = policy.should_execute_method("method_3", None)
        assert should_execute is True
        assert "No calibration data" in reason
    
    def test_method_execution_decision_permissive_mode(self) -> None:
        """Test method execution decisions in permissive mode."""
        policy = CalibrationPolicy(strict_mode=False)
        
        should_execute, reason = policy.should_execute_method("method_1", 0.45)
        assert should_execute is True
        assert "non-strict" in reason
    
    def test_weight_adjustment_excellent(self) -> None:
        """Test weight adjustment for EXCELENTE calibration (FARFAN)."""
        policy = create_default_policy()
        
        result = policy.compute_adjusted_weight(
            base_weight=1.0,
            calibration_score=0.9,
            method_id="test_method",
        )
        
        assert isinstance(result, CalibrationWeight)
        assert result.base_weight == 1.0
        assert result.calibration_score == 0.9
        assert result.quality_band == "EXCELENTE"
        assert result.adjustment_factor == 1.0
        assert result.adjusted_weight == 1.0
    
    def test_weight_adjustment_good(self) -> None:
        """Test weight adjustment for BUENO calibration (FARFAN)."""
        policy = create_default_policy()
        
        result = policy.compute_adjusted_weight(
            base_weight=1.0,
            calibration_score=0.75,
        )
        
        assert result.quality_band == "BUENO"
        assert result.adjustment_factor == 0.9
        assert result.adjusted_weight == 0.9
    
    def test_weight_adjustment_acceptable(self) -> None:
        """Test weight adjustment for ACEPTABLE calibration (FARFAN)."""
        policy = create_default_policy()
        
        result = policy.compute_adjusted_weight(
            base_weight=1.0,
            calibration_score=0.60,
        )
        
        assert result.quality_band == "ACEPTABLE"
        assert result.adjustment_factor == 0.75
        assert result.adjusted_weight == 0.75
    
    def test_weight_adjustment_poor(self) -> None:
        """Test weight adjustment for INSUFICIENTE calibration (FARFAN)."""
        policy = create_default_policy()
        
        result = policy.compute_adjusted_weight(
            base_weight=1.0,
            calibration_score=0.40,
        )
        
        assert result.quality_band == "INSUFICIENTE"
        assert result.adjustment_factor == 0.40
        assert result.adjusted_weight == 0.40
    
    def test_weight_adjustment_no_calibration(self) -> None:
        """Test weight adjustment when calibration data unavailable."""
        policy = create_default_policy()
        
        result = policy.compute_adjusted_weight(
            base_weight=1.0,
            calibration_score=None,
        )
        
        assert result.quality_band == "UNKNOWN"
        assert result.adjustment_factor == 1.0
        assert result.adjusted_weight == 1.0
    
    def test_method_selection_single_candidate(self) -> None:
        """Test method selection with single candidate."""
        policy = create_default_policy()
        
        candidates = {"method_1": 0.8}
        selected, score, reason = policy.select_best_method(candidates)
        
        assert selected == "method_1"
        assert score == 0.8
        assert "Only one candidate" in reason
    
    def test_method_selection_multiple_candidates(self) -> None:
        """Test method selection with multiple candidates."""
        policy = create_default_policy()
        
        candidates = {
            "method_1": 0.5,
            "method_2": 0.9,
            "method_3": 0.7,
        }
        selected, score, reason = policy.select_best_method(candidates)
        
        assert selected == "method_2"
        assert score == 0.9
        assert "margin" in reason
    
    def test_method_selection_no_candidates(self) -> None:
        """Test method selection with no candidates raises error."""
        policy = create_default_policy()
        
        with pytest.raises(ValueError, match="No candidate methods"):
            policy.select_best_method({})
    
    def test_influence_recording(self) -> None:
        """Test recording calibration influence."""
        policy = create_default_policy()
        
        policy.record_influence(
            phase_id=2,
            method_id="test_method",
            calibration_score=0.85,
            weight_adjustment=0.1,
            influenced_output=True,
            extra_data="test",
        )
        
        metrics = policy.export_metrics()
        assert len(metrics) == 1
        assert metrics[0]["method_id"] == "test_method"
        assert metrics[0]["calibration_score"] == 0.85
        assert metrics[0]["influenced_output"] is True
    
    def test_drift_detection_insufficient_data(self) -> None:
        """Test drift detection with insufficient data."""
        policy = create_default_policy()
        
        for i in range(10):
            policy.record_influence(
                phase_id=2,
                method_id=f"method_{i}",
                calibration_score=0.8,
                weight_adjustment=0.0,
                influenced_output=False,
            )
        
        drift = policy.detect_drift(window_size=50)
        assert drift["drift_detected"] is False
        assert "Insufficient data" in drift["reason"]
    
    def test_drift_detection_stable_scores(self) -> None:
        """Test drift detection with stable scores."""
        policy = create_default_policy()
        
        for i in range(100):
            policy.record_influence(
                phase_id=2,
                method_id=f"method_{i}",
                calibration_score=0.8 + (i % 3) * 0.01,  # Very small variation
                weight_adjustment=0.0,
                influenced_output=False,
            )
        
        drift = policy.detect_drift(window_size=50, threshold=0.15)
        assert drift["drift_detected"] is False
        assert drift["mean_score"] > 0.79
        assert drift["std_score"] < 0.02
    
    def test_drift_detection_high_variance(self) -> None:
        """Test drift detection with high variance."""
        policy = create_default_policy()
        
        for i in range(100):
            score = 0.5 if i % 2 == 0 else 0.9
            policy.record_influence(
                phase_id=2,
                method_id=f"method_{i}",
                calibration_score=score,
                weight_adjustment=0.0,
                influenced_output=False,
            )
        
        drift = policy.detect_drift(window_size=50, threshold=0.15)
        assert drift["drift_detected"] is True
        assert drift["std_score"] > 0.1
    
    def test_metrics_summary(self) -> None:
        """Test metrics summary generation."""
        policy = create_default_policy()
        
        for i in range(20):
            policy.record_influence(
                phase_id=i % 3,
                method_id=f"method_{i}",
                calibration_score=0.7 + (i % 4) * 0.1,
                weight_adjustment=0.1,
                influenced_output=i % 2 == 0,
            )
        
        summary = policy.get_metrics_summary()
        
        assert summary["total_metrics"] == 20
        assert "mean_calibration_score" in summary
        assert "influenced_outputs" in summary
        assert summary["influence_rate"] == 0.5
        assert "by_phase" in summary
        assert "by_quality_band" in summary
    
    def test_custom_thresholds(self) -> None:
        """Test custom quality band thresholds (for method-specific calibration)."""
        # Example: Method-specific logit calibration might need different bands
        custom_bands = {
            "HIGH": (0.9, 1.0),
            "MEDIUM": (0.7, 0.9),
            "LOW": (0.5, 0.7),
            "VERY_LOW": (0.0, 0.5),
        }
        
        policy = CalibrationPolicy(custom_thresholds=custom_bands)
        
        assert policy.get_quality_band(0.95) == "HIGH"
        assert policy.get_quality_band(0.85) == "MEDIUM"
        assert policy.get_quality_band(0.6) == "LOW"
        assert policy.get_quality_band(0.3) == "VERY_LOW"
    
    def test_custom_adjustment_factors(self) -> None:
        """Test custom weight adjustment factors (for method-specific calibration)."""
        # Example: Method-specific factors for CDAFFramework logit calibration
        custom_factors = {
            "EXCELENTE": 1.0,
            "BUENO": 0.8,
            "ACEPTABLE": 0.5,
            "INSUFICIENTE": 0.2,
        }
        
        policy = CalibrationPolicy(custom_factors=custom_factors)
        
        result = policy.compute_adjusted_weight(1.0, 0.75)  # BUENO range
        assert result.adjustment_factor == 0.8
        assert result.adjusted_weight == 0.8
    
    def test_weight_serialization(self) -> None:
        """Test CalibrationWeight serialization."""
        policy = create_default_policy()
        
        weight = policy.compute_adjusted_weight(1.0, 0.85)
        weight_dict = weight.to_dict()
        
        assert isinstance(weight_dict, dict)
        assert "base_weight" in weight_dict
        assert "calibration_score" in weight_dict
        assert "adjusted_weight" in weight_dict
        assert "quality_band" in weight_dict


@pytest.mark.integration
class TestCalibrationPolicyIntegration:
    """Integration tests for calibration policy."""
    
    def test_end_to_end_workflow(self) -> None:
        """Test complete calibration workflow."""
        policy = CalibrationPolicy(strict_mode=True)
        
        methods = {
            "method_a": 0.85,
            "method_b": 0.65,
            "method_c": 0.45,
        }
        
        selected, score, reason = policy.select_best_method(methods)
        assert selected == "method_a"
        
        should_exec, exec_reason = policy.should_execute_method(selected, score)
        assert should_exec is True
        
        weight = policy.compute_adjusted_weight(1.0, score, method_id=selected)
        assert weight.adjusted_weight == 1.0
        
        policy.record_influence(
            phase_id=2,
            method_id=selected,
            calibration_score=score,
            weight_adjustment=1.0 - weight.adjusted_weight,
            influenced_output=True,
        )
        
        summary = policy.get_metrics_summary()
        assert summary["total_metrics"] == 1
        assert summary["influenced_outputs"] == 1
    
    def test_progressive_degradation(self) -> None:
        """Test progressive calibration degradation detection (FARFAN)."""
        policy = create_default_policy()
        
        for i in range(100):
            degrading_score = 0.9 - (i * 0.005)
            policy.record_influence(
                phase_id=2,
                method_id="degrading_method",
                calibration_score=max(0.0, degrading_score),
                weight_adjustment=0.0,
                influenced_output=False,
            )
        
        drift = policy.detect_drift(window_size=50, threshold=0.1)
        
        assert drift["mean_score"] < 0.7
        summary = policy.get_metrics_summary()
        # FARFAN bands: Should see INSUFICIENTE or ACEPTABLE in degraded scores
        assert "INSUFICIENTE" in summary["by_quality_band"] or "ACEPTABLE" in summary["by_quality_band"]
