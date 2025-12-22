#!/usr/bin/env python3
"""
Standalone test script for CalibrationPolicy v2.0

This bypasses package imports to test the calibration_policy module in isolation.
"""
import sys
sys.path.insert(0, 'src')

# Direct import without package structure
import importlib.util
import sys

# Load the module directly
spec = importlib.util.spec_from_file_location(
    "farfan_pipeline.phases.Phase_two.phase2_60_04_calibration_policy",
    "src/farfan_pipeline/phases/Phase_two/phase2_60_04_calibration_policy.py"
)

# Create module and add to sys.modules before execution (required for dataclasses)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

# Now we can use the module
QualityLabel = module.QualityLabel
MicroLevelThresholds = module.MicroLevelThresholds
LabelProbabilityMass = module.LabelProbabilityMass
CalibrationProvenance = module.CalibrationProvenance
CalibratedOutput = module.CalibratedOutput
CalibrationPolicy = module.CalibrationPolicy
MethodCalibrationResult = module.MethodCalibrationResult

import numpy as np

def test_micro_level_thresholds():
    """Test threshold validation."""
    print("Testing MicroLevelThresholds...")
    
    # Valid thresholds
    thresholds = MicroLevelThresholds(
        excelente=0.85,
        bueno=0.70,
        aceptable=0.55,
        insuficiente=0.0,
    )
    assert thresholds.excelente == 0.85
    print("  ✓ Valid thresholds work")
    
    # Invalid thresholds should raise
    try:
        bad_thresholds = MicroLevelThresholds(
            excelente=0.70,
            bueno=0.85,  # Wrong order!
            aceptable=0.55,
            insuficiente=0.0,
        )
        print("  ✗ Should have raised ValueError for non-monotonic thresholds")
        sys.exit(1)
    except ValueError as e:
        print(f"  ✓ Non-monotonic thresholds correctly rejected: {e}")

def test_label_probability_mass():
    """Test probability mass validation."""
    print("\nTesting LabelProbabilityMass...")
    
    # Valid probabilities
    probs = LabelProbabilityMass(
        excelente=0.1,
        bueno=0.3,
        aceptable=0.4,
        insuficiente=0.2,
    )
    assert abs(probs.excelente + probs.bueno + probs.aceptable + probs.insuficiente - 1.0) < 1e-6
    print("  ✓ Valid probability mass works")
    print(f"  ✓ Modal label: {probs.modal_label}")
    print(f"  ✓ Entropy: {probs.entropy:.4f}")
    
    # Invalid probabilities
    try:
        bad_probs = LabelProbabilityMass(
            excelente=0.5,
            bueno=0.5,
            aceptable=0.5,
            insuficiente=0.5,
        )
        print("  ✗ Should have raised ValueError for probabilities not summing to 1.0")
        sys.exit(1)
    except ValueError:
        print("  ✓ Invalid probability sum correctly rejected")

def test_calibration_policy():
    """Test CalibrationPolicy main functionality."""
    print("\nTesting CalibrationPolicy...")
    
    thresholds = MicroLevelThresholds(
        excelente=0.85, bueno=0.70, aceptable=0.55, insuficiente=0.0
    )
    weights = {"semantic": 0.35, "temporal": 0.25, "financial": 0.25, "structural": 0.15}
    
    policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=weights)
    print("  ✓ Policy initialized")
    
    # Test central calibration (no method delegation)
    output = policy.calibrate_method_output(
        question_id="Q001",
        method_id="test_method",
        raw_score=0.75,
        method_instance=None,
        posterior_samples=None,
    )
    
    assert isinstance(output, CalibratedOutput)
    assert isinstance(output.label, QualityLabel)
    assert 0.0 <= output.weight <= 1.0
    assert output.posterior_samples is not None
    assert len(output.posterior_samples) == 10000
    print(f"  ✓ Central calibration works: label={output.label.value}, weight={output.weight:.3f}")
    print(f"  ✓ Synthetic posterior generated: {len(output.posterior_samples)} samples")
    print(f"  ✓ Calibration source: {output.provenance.calibration_source}")
    
    # Test posterior propagation
    input_samples = np.random.beta(2, 5, size=10000)
    output2 = policy.calibrate_method_output(
        question_id="Q002",
        method_id="test_method",
        raw_score=0.60,
        posterior_samples=input_samples,
    )
    assert len(output2.posterior_samples) == len(input_samples)
    print(f"  ✓ Posterior propagation preserves sample count")
    
    # Test audit log
    assert len(policy.audit_log) == 2
    print(f"  ✓ Audit log captures all calibrations: {len(policy.audit_log)} entries")
    
    # Test JSON export
    export = policy.export_audit_log()
    assert len(export) == 2
    assert "provenance_hash" in export[0]
    assert "entropy" in export[0]
    print(f"  ✓ Audit log exports to valid JSON")

def test_method_delegation():
    """Test method delegation protocol."""
    print("\nTesting method delegation...")
    
    class MockCalibrableMethod:
        calibration_params = {"domain": "semantic", "output_semantics": "test"}
        
        def calibrate_output(self, raw_score, posterior_samples=None, context=None):
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
    print("  ✓ Protocol detection works")
    
    output = policy.calibrate_method_output(
        question_id="Q003",
        method_id="test_method",
        raw_score=0.75,
        method_instance=method_instance,
    )
    
    assert output.provenance.calibration_source == "method_delegation"
    assert output.provenance.method_class_name == "MockCalibrableMethod"
    print(f"  ✓ Method delegation works: source={output.provenance.calibration_source}")

def main():
    print("=" * 70)
    print("CalibrationPolicy v2.0 Standalone Tests")
    print("=" * 70)
    
    test_micro_level_thresholds()
    test_label_probability_mass()
    test_calibration_policy()
    test_method_delegation()
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)

if __name__ == "__main__":
    main()
