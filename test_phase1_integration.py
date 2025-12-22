"""
Test Phase 1 Integration: Hierarchical Parameter Lookup
"""
import sys
import importlib.util

# Load module directly without package imports
spec = importlib.util.spec_from_file_location(
    "calibration_policy",
    "src/farfan_pipeline/phases/Phase_two/phase2_60_04_calibration_policy.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CalibrationPolicy = module.CalibrationPolicy
CalibrationParameters = module.CalibrationParameters
MicroLevelThresholds = module.MicroLevelThresholds

print("=" * 70)
print("Phase 1 Integration Tests: Hierarchical Parameter Lookup")
print("=" * 70)

# Create policy
thresholds = MicroLevelThresholds(
    excelente=0.85,
    bueno=0.70,
    aceptable=0.55,
    insuficiente=0.0,
)
default_weights = {
    "semantic": 0.35,
    "temporal": 0.25,
    "financial": 0.25,
    "structural": 0.15,
}
policy = CalibrationPolicy(thresholds=thresholds, default_domain_weights=default_weights)

print("\n1. Testing Global Parameters (Lowest Priority)")
print("-" * 70)
global_params = CalibrationParameters(confidence_threshold=0.6, random_seed=123)
policy.set_global_parameters(global_params)
result = policy.get_context_parameters("Q999")
print(f"  ✓ Global confidence_threshold: {result.confidence_threshold}")
print(f"  ✓ Global random_seed: {result.random_seed}")
assert result.confidence_threshold == 0.6
assert result.random_seed == 123

print("\n2. Testing Dimension Override")
print("-" * 70)
dim_params = CalibrationParameters(confidence_threshold=0.75, random_seed=456)
policy.set_dimension_parameters("DIM01", dim_params)
result = policy.get_context_parameters("Q999", dimension_id="DIM01")
print(f"  ✓ Dimension confidence_threshold: {result.confidence_threshold}")
print(f"  ✓ Dimension random_seed: {result.random_seed}")
assert result.confidence_threshold == 0.75
assert result.random_seed == 456

print("\n3. Testing Policy Area Override")
print("-" * 70)
pa_params = CalibrationParameters(confidence_threshold=0.8, random_seed=789)
policy.set_policy_area_parameters("PA05", pa_params)
result = policy.get_context_parameters("Q999", dimension_id="DIM01", policy_area_id="PA05")
print(f"  ✓ Policy Area confidence_threshold: {result.confidence_threshold}")
print(f"  ✓ Policy Area random_seed: {result.random_seed}")
assert result.confidence_threshold == 0.8
assert result.random_seed == 789

print("\n4. Testing Contract Override (Highest Priority)")
print("-" * 70)
contract_params = CalibrationParameters(confidence_threshold=0.95, random_seed=999)
policy.set_contract_parameters("Q001", contract_params)
result = policy.get_context_parameters("Q001", dimension_id="DIM01", policy_area_id="PA05")
print(f"  ✓ Contract confidence_threshold: {result.confidence_threshold}")
print(f"  ✓ Contract random_seed: {result.random_seed}")
assert result.confidence_threshold == 0.95
assert result.random_seed == 999

print("\n5. Testing Hierarchical Resolution Chain")
print("-" * 70)
result = policy.get_context_parameters("Q999", dimension_id="DIM01", policy_area_id="PA05")
assert result.confidence_threshold == 0.8
print(f"  ✓ Q999 + DIM01 + PA05 → PA params (confidence={result.confidence_threshold})")

result = policy.get_context_parameters("Q999", dimension_id="DIM01")
assert result.confidence_threshold == 0.75
print(f"  ✓ Q999 + DIM01 → Dimension params (confidence={result.confidence_threshold})")

result = policy.get_context_parameters("Q999")
assert result.confidence_threshold == 0.6
print(f"  ✓ Q999 only → Global params (confidence={result.confidence_threshold})")

result = policy.get_context_parameters("Q001", dimension_id="DIM01", policy_area_id="PA05")
assert result.confidence_threshold == 0.95
print(f"  ✓ Q001 + DIM01 + PA05 → Contract params (confidence={result.confidence_threshold})")

print("\n6. Testing Integration with calibrate_method_output")
print("-" * 70)
import numpy as np
output = policy.calibrate_method_output(
    question_id="Q999",
    method_id="test_method",
    raw_score=0.75,
    context={"dimension_id": "DIM01"}
)
print(f"  ✓ Calibration with dimension context: label={output.label}")
print(f"  ✓ Weight: {output.weight}")
print(f"  ✓ Posterior samples: {len(output.posterior_samples) if output.posterior_samples is not None else 0}")

output2 = policy.calibrate_method_output(
    question_id="Q999",
    method_id="test_method",
    raw_score=0.75,
    context={"dimension_id": "DIM01"}
)
if output.posterior_samples is not None and output2.posterior_samples is not None:
    samples_match = np.allclose(output.posterior_samples, output2.posterior_samples)
    print(f"  ✓ Reproducibility with dimension-specific seed: {samples_match}")
    assert samples_match, "Samples should be identical with same seed"

print("\n" + "=" * 70)
print("✓ ALL PHASE 1 INTEGRATION TESTS PASSED")
print("=" * 70)
print("\nPhase 1 Integration Complete:")
print("  • Hierarchical parameter lookup (global → dimension → PA → contract)")
print("  • Context-specific calibration parameters")
print("  • Integration with existing uncertainty propagation")
print("  • Reproducible posterior generation using hierarchical seeds")
