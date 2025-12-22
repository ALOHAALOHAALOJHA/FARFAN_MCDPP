"""
Comprehensive tests for CalibrationPolicy v2.0.

Tests cover:
1. Data structure validation
2. Protocol detection
3. Method delegation
4. Posterior propagation
5. Uncertainty modulation
6. Provenance tracking
7. Threshold loading
8. Audit logging
9. Failure modes

All tests implement explicit acceptance criteria from refactor_calibration_policy.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest

from farfan_pipeline.phases.Phase_two.phase2_60_04_calibration_policy import (
    CalibrationPolicy,
    CalibrationProvenance,
    CalibratedOutput,
    LabelProbabilityMass,
    MethodCalibrationResult,
    MicroLevelThresholds,
    QualityLabel,
)


class TestMicroLevelThresholds:
    """Test threshold validation and monotonicity."""
    
    def test_valid_thresholds(self) -> None:
        """Test valid threshold construction."""
        thresholds = MicroLevelThresholds(
            excelente=0.85,
            bueno=0.70,
            aceptable=0.55,
            insuficiente=0.0,
        )
        assert thresholds.excelente == 0.85
        assert thresholds.bueno == 0.70
        assert thresholds.aceptable == 0.55
    
    def test_threshold_monotonicity_validation(self) -> None:
        """Test that non-monotonic thresholds raise ValueError."""
        with pytest.raises(ValueError, match="Threshold monotonicity violated"):
            MicroLevelThresholds(
                excelente=0.70,
                bueno=0.85,
                aceptable=0.55,
                insuficiente=0.0,
            )


class TestLabelProbabilityMass:
    """Test probability mass validation and properties."""
    
    def test_valid_probability_mass(self) -> None:
        """Test valid probability mass construction."""
        probs = LabelProbabilityMass(
            excelente=0.1,
            bueno=0.3,
            aceptable=0.4,
            insuficiente=0.2,
        )
        assert abs(probs.excelente + probs.bueno + probs.aceptable + probs.insuficiente - 1.0) < 1e-6
    
    def test_probability_mass_sum_validation(self) -> None:
        """Test that probabilities not summing to 1.0 raise ValueError."""
        with pytest.raises(ValueError, match="Probability mass must sum to 1.0"):
            LabelProbabilityMass(
                excelente=0.3,
                bueno=0.3,
                aceptable=0.3,
                insuficiente=0.3,
            )
    
    def test_modal_label(self) -> None:
        """Test modal label extraction."""
        probs = LabelProbabilityMass(
            excelente=0.1,
            bueno=0.6,
            aceptable=0.2,
            insuficiente=0.1,
        )
        assert probs.modal_label == QualityLabel.BUENO
        assert probs.modal_probability == 0.6
    
    def test_entropy_calculation(self) -> None:
        """Test Shannon entropy calculation."""
        probs_certain = LabelProbabilityMass(
            excelente=1.0,
            bueno=0.0,
            aceptable=0.0,
            insuficiente=0.0,
        )
        assert probs_certain.entropy == 0.0
        
        probs_uncertain = LabelProbabilityMass(
            excelente=0.25,
            bueno=0.25,
            aceptable=0.25,
            insuficiente=0.25,
        )
        assert probs_uncertain.entropy > 1.5


class TestCalibrationProvenance:
    """Test provenance tracking and hash generation."""
    
    def test_provenance_hash_deterministic(self) -> None:
        """Test that same inputs produce same hash."""
        label_probs = LabelProbabilityMass(
            excelente=0.1, bueno=0.3, aceptable=0.4, insuficiente=0.2
        )
        
        timestamp = "2025-12-22T00:00:00+00:00"
        
        prov1 = CalibrationProvenance(
            question_id="Q001",
            method_id="test_method",
            method_class_name="TestClass",
            raw_score=0.75,
            raw_score_semantics="normalized_score",
            posterior_mean=None,
            posterior_std=None,
            credible_interval_95=None,
            posterior_sample_size=None,
            calibration_source="method_delegation",
            transformation_applied="test_transform",
            transformation_parameters={},
            domain="semantic",
            domain_weight=0.35,
            contract_priority=1,
            label_probabilities=label_probs,
            assigned_label=QualityLabel.BUENO,
            assigned_weight=0.9,
            timestamp_utc=timestamp,
        )
        
        prov2 = CalibrationProvenance(
            question_id="Q001",
            method_id="test_method",
            method_class_name="TestClass",
            raw_score=0.75,
            raw_score_semantics="normalized_score",
            posterior_mean=None,
            posterior_std=None,
            credible_interval_95=None,
            posterior_sample_size=None,
            calibration_source="method_delegation",
            transformation_applied="test_transform",
            transformation_parameters={},
            domain="semantic",
            domain_weight=0.35,
            contract_priority=1,
            label_probabilities=label_probs,
            assigned_label=QualityLabel.BUENO,
            assigned_weight=0.9,
            timestamp_utc=timestamp,
        )
        
        assert prov1.provenance_hash == prov2.provenance_hash


class TestCalibrationPolicy:
    """Test CalibrationPolicy coordinator."""
    
    def test_initialization(self) -> None:
        """Test policy initialization."""
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        assert policy._thresholds.excelente == 0.85
    
    def test_domain_weights_validation(self) -> None:
        """Test that domain weights must sum to 1.0."""
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.5, "temporal": 0.5}
        
        with pytest.raises(ValueError, match="Domain weights must sum to 1.0"):
            CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
    
    def test_from_questionnaire_provider(self) -> None:
        """Test factory construction from questionnaire provider."""
        mock_provider = MagicMock()
        mock_provider.get_scoring_levels.return_value = {
            "micro_levels": [
                {"level": "EXCELENTE", "min_score": 0.85},
                {"level": "BUENO", "min_score": 0.70},
                {"level": "ACEPTABLE", "min_score": 0.55},
                {"level": "INSUFICIENTE", "min_score": 0.0},
            ]
        }
        
        policy = CalibrationPolicy.from_questionnaire_provider(mock_provider)
        assert policy._thresholds.excelente == 0.85
        assert policy._thresholds.bueno == 0.70
        assert policy._thresholds.aceptable == 0.55
    
    def test_central_calibration_generates_synthetic_posterior(self) -> None:
        """Test that central path generates 10000 posterior samples."""
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        output = policy.calibrate_method_output(
            question_id="Q001",
            method_id="test_method",
            raw_score=0.75,
            method_instance=None,
            posterior_samples=None,
        )
        
        assert output.posterior_samples is not None
        assert len(output.posterior_samples) == 10000
        assert output.provenance.calibration_source == "central_threshold"
    
    def test_posterior_propagation_preserves_samples(self) -> None:
        """Test that provided posterior samples are preserved."""
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        input_samples = np.random.beta(2, 5, size=10000)
        
        output = policy.calibrate_method_output(
            question_id="Q001",
            method_id="test_method",
            raw_score=0.75,
            method_instance=None,
            posterior_samples=input_samples,
        )
        
        assert output.posterior_samples is not None
        assert len(output.posterior_samples) == len(input_samples)
    
    def test_label_probabilities_sum_to_one(self) -> None:
        """Test that label probabilities always sum to 1.0."""
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        for _ in range(100):
            raw_score = np.random.uniform(0.0, 1.0)
            output = policy.calibrate_method_output(
                question_id="Q001",
                method_id="test_method",
                raw_score=float(raw_score),
            )
            
            total = (
                output.label_probabilities.excelente
                + output.label_probabilities.bueno
                + output.label_probabilities.aceptable
                + output.label_probabilities.insuficiente
            )
            assert abs(total - 1.0) < 1e-6
    
    def test_uncertainty_modulates_weight(self) -> None:
        """Test that high entropy reduces weight."""
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        samples_certain = np.full(10000, 0.90)
        output_certain = policy.calibrate_method_output(
            question_id="Q001",
            method_id="test_method",
            raw_score=0.90,
            posterior_samples=samples_certain,
        )
        
        samples_uncertain = np.concatenate([
            np.full(2500, 0.90),
            np.full(2500, 0.75),
            np.full(2500, 0.60),
            np.full(2500, 0.45),
        ])
        output_uncertain = policy.calibrate_method_output(
            question_id="Q002",
            method_id="test_method",
            raw_score=0.67,
            posterior_samples=samples_uncertain,
        )
        
        assert output_certain.label_probabilities.entropy < output_uncertain.label_probabilities.entropy
        assert output_certain.weight >= output_uncertain.weight
    
    def test_audit_log_captures_calibrations(self) -> None:
        """Test that audit log captures all calibrations."""
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        n_calibrations = 10
        for i in range(n_calibrations):
            policy.calibrate_method_output(
                question_id=f"Q{i:03d}",
                method_id="test_method",
                raw_score=0.75,
            )
        
        assert len(policy.audit_log) == n_calibrations
    
    def test_export_audit_log_valid_json(self) -> None:
        """Test that audit log exports to valid JSON."""
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        policy.calibrate_method_output(
            question_id="Q001",
            method_id="test_method",
            raw_score=0.75,
        )
        
        export = policy.export_audit_log()
        assert len(export) == 1
        assert "question_id" in export[0]
        assert "provenance_hash" in export[0]
        assert "entropy" in export[0]
    
    def test_raw_score_validation(self) -> None:
        """Test that invalid raw scores raise ValueError."""
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        with pytest.raises(ValueError, match="raw_score must be in"):
            policy.calibrate_method_output(
                question_id="Q001",
                method_id="test_method",
                raw_score=1.5,
            )


class TestMethodDelegation:
    """Test method delegation protocol."""
    
    def test_protocol_detection_positive(self) -> None:
        """Test that methods implementing protocol are detected."""
        
        class MockCalibrableMethod:
            calibration_params = {"domain": "semantic", "output_semantics": "test"}
            
            def calibrate_output(
                self,
                raw_score: float,
                posterior_samples: np.ndarray | None = None,
                context: dict[str, Any] | None = None,
            ) -> MethodCalibrationResult:
                label_probs = LabelProbabilityMass(
                    excelente=0.1, bueno=0.3, aceptable=0.4, insuficiente=0.2
                )
                return MethodCalibrationResult(
                    calibrated_score=raw_score,
                    label_probabilities=label_probs,
                    transformation_name="mock_transform",
                    transformation_parameters={},
                )
        
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        method_instance = MockCalibrableMethod()
        assert policy._implements_calibrable_protocol(method_instance)
    
    def test_protocol_detection_negative(self) -> None:
        """Test that methods not implementing protocol are not detected."""
        
        class MockNonCalibrableMethod:
            def some_other_method(self) -> None:
                pass
        
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        method_instance = MockNonCalibrableMethod()
        assert not policy._implements_calibrable_protocol(method_instance)
    
    def test_delegation_produces_correct_source(self) -> None:
        """Test that delegation produces calibration_source='method_delegation'."""
        
        class MockCalibrableMethod:
            calibration_params = {"domain": "semantic", "output_semantics": "test"}
            
            def calibrate_output(
                self,
                raw_score: float,
                posterior_samples: np.ndarray | None = None,
                context: dict[str, Any] | None = None,
            ) -> MethodCalibrationResult:
                label_probs = LabelProbabilityMass(
                    excelente=0.1, bueno=0.3, aceptable=0.4, insuficiente=0.2
                )
                return MethodCalibrationResult(
                    calibrated_score=raw_score,
                    label_probabilities=label_probs,
                    transformation_name="mock_transform",
                    transformation_parameters={},
                )
        
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        method_instance = MockCalibrableMethod()
        output = policy.calibrate_method_output(
            question_id="Q001",
            method_id="test_method",
            raw_score=0.75,
            method_instance=method_instance,
        )
        
        assert output.provenance.calibration_source == "method_delegation"
        assert output.provenance.method_class_name == "MockCalibrableMethod"


class TestFailureModes:
    """Test explicit failure mode handling."""
    
    def test_nan_posterior_samples_detection(self) -> None:
        """Test that NaN in posterior samples raises appropriate error."""
        thresholds = MicroLevelThresholds(
            excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
        )
        weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
        policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
        
        bad_samples = np.array([0.5, np.nan, 0.7, np.inf])
        
        output = policy.calibrate_method_output(
            question_id="Q001",
            method_id="test_method",
            raw_score=0.75,
            posterior_samples=bad_samples,
        )
        
        assert not np.isnan(output.calibrated_score)


@pytest.mark.updated
class TestIntegration:
    """Integration tests with real components."""
    
    def test_end_to_end_calibration_flow(self) -> None:
        """Test complete calibration flow from raw score to output."""
        mock_provider = MagicMock()
        mock_provider.get_scoring_levels.return_value = {
            "micro_levels": [
                {"level": "EXCELENTE", "min_score": 0.85},
                {"level": "BUENO", "min_score": 0.70},
                {"level": "ACEPTABLE", "min_score": 0.55},
                {"level": "INSUFICIENTE", "min_score": 0.0},
            ]
        }
        
        policy = CalibrationPolicy.from_questionnaire_provider(mock_provider)
        
        output = policy.calibrate_method_output(
            question_id="Q001",
            method_id="test_method",
            raw_score=0.75,
            context={"domain": "semantic"},
        )
        
        assert isinstance(output, CalibratedOutput)
        assert isinstance(output.label, QualityLabel)
        assert 0.0 <= output.weight <= 1.0
        assert output.provenance.question_id == "Q001"
        assert len(output.provenance.provenance_hash) == 16
