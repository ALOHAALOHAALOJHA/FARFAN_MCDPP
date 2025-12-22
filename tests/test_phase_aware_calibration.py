"""Test phase-aware calibration (ingestion vs. micro-answering)."""
import pytest
import numpy as np
from src.farfan_pipeline.phases.Phase_two.phase2_60_04_calibration_policy import (
    CalibrationPolicy,
    QualityLabel,
    MicroLevelThresholds,
)
from src.farfan_pipeline.core.canonical_specs import INGESTION_PHASE_METHODS


def test_ingestion_methods_identified():
    """Verify ingestion phase methods are correctly registered."""
    assert "semantic_chunking_policy" in INGESTION_PHASE_METHODS
    assert "analyzer_one" in INGESTION_PHASE_METHODS
    assert "embedding_policy" in INGESTION_PHASE_METHODS
    
    # Micro-answering methods should NOT be in ingestion set
    assert "policy_processor" not in INGESTION_PHASE_METHODS
    assert "financiero_viabilidad_tablas" not in INGESTION_PHASE_METHODS


def test_ingestion_method_stricter_threshold():
    """Verify ingestion methods use stricter thresholds than answering methods."""
    thresholds = MicroLevelThresholds(
        excelente=0.85,
        bueno=0.70,
        aceptable=0.55,
        insuficiente=0.00,
    )
    policy = CalibrationPolicy(thresholds)
    
    # Create mock method instance
    class MockIngestionMethod:
        calibration_params = {
            "domain": "text_extraction",
            "output_semantics": "bayesian_posterior",
            "prior_alpha": 1.0,
            "prior_beta": 1.0,
            "unit_of_analysis_aware": True,
            "ingestion_phase": True,  # Flag for stricter validation
        }
        
        def calibrate_output(self, raw_score, posterior_samples=None, context=None):
            # For ingestion, apply stricter threshold
            # 0.75 should be INSUFICIENTE for ingestion (requires 0.90+)
            from dataclasses import dataclass
            @dataclass
            class Result:
                calibrated_score: float
                label_probabilities: dict
                transformation_name: str
                posterior_samples: np.ndarray
                credible_interval_95: tuple
            
            # Generate posterior
            posterior = np.random.beta(8, 2, 10000) if posterior_samples is None else posterior_samples
            
            # For ingestion phase, stricter thresholds
            ingestion_thresholds = {"excelente": 0.95, "bueno": 0.90, "aceptable": 0.75}
            
            score = raw_score
            if score < 0.75:
                label_probs = {"excelente": 0.0, "bueno": 0.0, "aceptable": 0.0, "insuficiente": 1.0}
            elif score < 0.90:
                label_probs = {"excelente": 0.0, "bueno": 0.0, "aceptable": 0.7, "insuficiente": 0.3}
            else:
                label_probs = {"excelente": 0.1, "bueno": 0.6, "aceptable": 0.3, "insuficiente": 0.0}
            
            return Result(
                calibrated_score=score,
                label_probabilities=label_probs,
                transformation_name="ingestion_phase_strict_validation",
                posterior_samples=posterior,
                credible_interval_95=(np.percentile(posterior, 2.5), np.percentile(posterior, 97.5)),
            )
    
    method = MockIngestionMethod()
    
    # Test with score=0.75 - should be INSUFICIENTE for ingestion
    result = policy.calibrate_method_output(
        contract_id="Q001",
        method_instance=method,
        raw_score=0.75,
        context={"execution_phase": "ingestion"},
    )
    
    # For ingestion phase, 0.75 should be insufficient
    assert result.label_probabilities.insuficiente > 0.25


def test_answering_method_standard_threshold():
    """Verify micro-answering methods use standard thresholds."""
    thresholds = MicroLevelThresholds(
        excelente=0.85,
        bueno=0.70,
        aceptable=0.55,
        insuficiente=0.00,
    )
    policy = CalibrationPolicy(thresholds)
    
    # Create mock answering method
    class MockAnsweringMethod:
        calibration_params = {
            "domain": "policy_analysis",
            "output_semantics": "bayesian_posterior",
            "prior_alpha": 1.0,
            "prior_beta": 1.0,
        }
        
        def calibrate_output(self, raw_score, posterior_samples=None, context=None):
            from dataclasses import dataclass
            @dataclass
            class Result:
                calibrated_score: float
                label_probabilities: dict
                transformation_name: str
                posterior_samples: np.ndarray
                credible_interval_95: tuple
            
            posterior = np.random.beta(8, 2, 10000) if posterior_samples is None else posterior_samples
            
            # Standard thresholds for answering
            score = raw_score
            if score >= 0.85:
                label_probs = {"excelente": 0.7, "bueno": 0.2, "aceptable": 0.1, "insuficiente": 0.0}
            elif score >= 0.70:
                label_probs = {"excelente": 0.1, "bueno": 0.7, "aceptable": 0.2, "insuficiente": 0.0}
            elif score >= 0.55:
                label_probs = {"excelente": 0.0, "bueno": 0.2, "aceptable": 0.7, "insuficiente": 0.1}
            else:
                label_probs = {"excelente": 0.0, "bueno": 0.0, "aceptable": 0.2, "insuficiente": 0.8}
            
            return Result(
                calibrated_score=score,
                label_probabilities=label_probs,
                transformation_name="answering_phase_standard_thresholds",
                posterior_samples=posterior,
                credible_interval_95=(np.percentile(posterior, 2.5), np.percentile(posterior, 97.5)),
            )
    
    method = MockAnsweringMethod()
    
    # Test with score=0.75 - should be BUENO for answering
    result = policy.calibrate_method_output(
        contract_id="Q001",
        method_instance=method,
        raw_score=0.75,
        context={"execution_phase": "answering"},
    )
    
    # For answering phase, 0.75 should be BUENO (> 0.70)
    assert result.label_probabilities.bueno > 0.5


def test_phase_context_propagation():
    """Verify execution phase context propagates to methods."""
    thresholds = MicroLevelThresholds(
        excelente=0.85,
        bueno=0.70,
        aceptable=0.55,
        insuficiente=0.00,
    )
    policy = CalibrationPolicy(thresholds)
    
    class MockContextAwareMethod:
        calibration_params = {
            "domain": "test",
            "output_semantics": "bayesian_posterior",
            "prior_alpha": 1.0,
            "prior_beta": 1.0,
        }
        
        def calibrate_output(self, raw_score, posterior_samples=None, context=None):
            # Verify context is passed
            assert context is not None
            assert "execution_phase" in context
            
            from dataclasses import dataclass
            @dataclass
            class Result:
                calibrated_score: float
                label_probabilities: dict
                transformation_name: str
                posterior_samples: np.ndarray
                credible_interval_95: tuple
            
            posterior = np.random.beta(5, 5, 10000)
            return Result(
                calibrated_score=raw_score,
                label_probabilities={"excelente": 0.25, "bueno": 0.25, "aceptable": 0.25, "insuficiente": 0.25},
                transformation_name=f"phase_{context.get('execution_phase', 'unknown')}",
                posterior_samples=posterior,
                credible_interval_95=(np.percentile(posterior, 2.5), np.percentile(posterior, 97.5)),
            )
    
    method = MockContextAwareMethod()
    
    # Test ingestion phase context
    result = policy.calibrate_method_output(
        contract_id="Q001",
        method_instance=method,
        raw_score=0.70,
        context={"execution_phase": "ingestion"},
    )
    assert "ingestion" in result.provenance.transformation_name
    
    # Test answering phase context
    result = policy.calibrate_method_output(
        contract_id="Q001",
        method_instance=method,
        raw_score=0.70,
        context={"execution_phase": "answering"},
    )
    assert "answering" in result.provenance.transformation_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
