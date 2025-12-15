"""
Audit Trail System - Examples and Usage

Demonstrates usage of the audit trail system for calibration verification.
"""


from audit_trail import (
    generate_manifest,
    verify_manifest,
    reconstruct_score,
    validate_determinism,
    StructuredAuditLogger,
    TraceGenerator,
    create_trace_example,
)


def example_basic_manifest_generation():
    """Example: Generate a basic verification manifest"""
    print("=" * 70)
    print("Example 1: Basic Manifest Generation")
    print("=" * 70)
    
    manifest = generate_manifest(
        calibration_scores={
            "FIN:BayesianNumericalAnalyzer.analyze_numeric_pattern@Q": 0.8004,
            "POL:BayesianEvidenceScorer.compute_bayesian_score@Q": 0.8567,
            "DER:BayesianMechanismInference.infer_mechanism@C": 0.7821,
        },
        config_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        retry=3,
        timeout_s=300.0,
        temperature=0.7,
        thresholds={
            "min_confidence": 0.7,
            "min_evidence": 0.6,
            "min_coherence": 0.65,
        },
        random_seed=123456,
        numpy_seed=789012,
        seed_version="sha256_v1",
        micro_scores=[0.75, 0.78, 0.82, 0.85, 0.88],
        dimension_scores={
            "DIM01": 0.82,
            "DIM02": 0.89,
            "DIM03": 0.76,
            "DIM04": 0.84,
            "DIM05": 0.78,
            "DIM06": 0.81,
        },
        area_scores={
            "PA01": 0.83,
            "PA02": 0.87,
            "PA03": 0.79,
            "PA04": 0.85,
        },
        macro_score=0.8166666666666667,
        validator_version="2.0.0",
        secret_key="test_secret_key_do_not_use_in_production",
    )
    
    print("✓ Manifest generated")
    print(f"  Timestamp: {manifest.timestamp}")
    print(f"  Validator version: {manifest.validator_version}")
    print(f"  Calibration count: {len(manifest.calibration_scores)}")
    print(f"  Macro score: {manifest.results.macro_score}")
    print(f"  Signature: {manifest.signature[:32]}...")
    print()
    
    return manifest


def example_manifest_verification(manifest):
    """Example: Verify manifest signature"""
    print("=" * 70)
    print("Example 2: Manifest Verification")
    print("=" * 70)
    
    valid = verify_manifest(manifest, "test_secret_key_do_not_use_in_production")
    
    print(f"✓ Signature verification: {'VALID' if valid else 'INVALID'}")
    
    invalid = verify_manifest(manifest, "wrong_key")
    print(f"✓ Wrong key verification: {'VALID' if invalid else 'INVALID (expected)'}")
    print()
    
    return valid


def example_score_reconstruction(manifest):
    """Example: Reconstruct score from manifest"""
    print("=" * 70)
    print("Example 3: Score Reconstruction")
    print("=" * 70)
    
    reconstructed = reconstruct_score(manifest)
    original = manifest.results.macro_score
    
    print(f"  Original macro score: {original}")
    print(f"  Reconstructed score:  {reconstructed}")
    print(f"  Difference:           {abs(original - reconstructed)}")
    print(f"✓ Reconstruction {'PASSED' if abs(original - reconstructed) < 1e-6 else 'FAILED'}")
    print()


def example_determinism_validation():
    """Example: Validate determinism across runs"""
    print("=" * 70)
    print("Example 4: Determinism Validation")
    print("=" * 70)
    
    manifest1 = generate_manifest(
        calibration_scores={"method1": 0.8, "method2": 0.9},
        config_hash="abc123",
        retry=3,
        timeout_s=300.0,
        temperature=0.7,
        thresholds={"threshold1": 0.7},
        random_seed=42,
        numpy_seed=42,
        seed_version="sha256_v1",
        micro_scores=[0.8, 0.9],
        dimension_scores={"DIM01": 0.85},
        area_scores={"PA01": 0.85},
        macro_score=0.85,
        validator_version="2.0.0",
        secret_key="test_key",
    )
    
    manifest2 = generate_manifest(
        calibration_scores={"method1": 0.8, "method2": 0.9},
        config_hash="abc123",
        retry=3,
        timeout_s=300.0,
        temperature=0.7,
        thresholds={"threshold1": 0.7},
        random_seed=42,
        numpy_seed=42,
        seed_version="sha256_v1",
        micro_scores=[0.8, 0.9],
        dimension_scores={"DIM01": 0.85},
        area_scores={"PA01": 0.85},
        macro_score=0.85,
        validator_version="2.0.0",
        secret_key="test_key",
    )
    
    deterministic = validate_determinism(manifest1, manifest2)
    
    print(f"✓ Same seeds, same config, same results: {'DETERMINISTIC' if deterministic else 'NON-DETERMINISTIC'}")
    
    manifest3 = generate_manifest(
        calibration_scores={"method1": 0.8, "method2": 0.9},
        config_hash="abc123",
        retry=3,
        timeout_s=300.0,
        temperature=0.7,
        thresholds={"threshold1": 0.7},
        random_seed=99,
        numpy_seed=99,
        seed_version="sha256_v1",
        micro_scores=[0.75, 0.85],
        dimension_scores={"DIM01": 0.80},
        area_scores={"PA01": 0.80},
        macro_score=0.80,
        validator_version="2.0.0",
        secret_key="test_key",
    )
    
    non_deterministic = validate_determinism(manifest1, manifest3)
    print(f"✓ Different seeds, different results: {'ALLOWS VARIATION' if not non_deterministic else 'UNEXPECTED'}")
    print()


def example_structured_logging():
    """Example: Structured logging"""
    print("=" * 70)
    print("Example 5: Structured Logging")
    print("=" * 70)
    
    logger = StructuredAuditLogger(log_dir="logs/calibration", component="test_audit")
    
    logger.log("INFO", "Starting calibration", {"phase": "initialization"})
    logger.log("INFO", "Calibration complete", {"phase": "completion", "score": 0.85})
    logger.log("WARNING", "Low confidence detected", {"confidence": 0.62, "threshold": 0.7})
    
    print("✓ Logs written to: logs/calibration/test_audit_*.log")
    print("  Log format: Structured JSON with timestamp, level, component, message, metadata")
    print()


def example_trace_generation():
    """Example: Operation trace generation"""
    print("=" * 70)
    print("Example 6: Operation Trace Generation")
    print("=" * 70)
    
    with TraceGenerator(enabled=True) as tracer:
        tracer.trace_operation(
            "compute_score",
            {"evidence": 0.85, "confidence": 0.9},
            0.765
        )
        
        tracer.trace_operation(
            "aggregate_dimensions",
            {"dim_scores": [0.8, 0.9, 0.7]},
            0.8
        )
        
        traces = tracer.get_traces()
    
    print(f"✓ Traced {len(traces)} operations")
    for i, trace in enumerate(traces, 1):
        print(f"  {i}. {trace.operation}: {trace.inputs} → {trace.output}")
    print()


def example_complete_workflow():
    """Example: Complete audit trail workflow"""
    print("=" * 70)
    print("Example 7: Complete Audit Trail Workflow")
    print("=" * 70)
    
    logger = StructuredAuditLogger(log_dir="logs/calibration", component="workflow")
    
    with TraceGenerator(enabled=True) as tracer:
        tracer.trace_operation("initialize", {"seed": 42}, None)
        tracer.trace_operation("compute", {"input": 0.85}, 0.8)
        
        traces = tracer.get_traces()
    
    manifest = generate_manifest(
        calibration_scores={"method1": 0.8},
        config_hash="abc",
        retry=3,
        timeout_s=300.0,
        temperature=0.7,
        thresholds={"t1": 0.7},
        random_seed=42,
        numpy_seed=42,
        seed_version="sha256_v1",
        micro_scores=[0.8],
        dimension_scores={"DIM01": 0.8},
        area_scores={"PA01": 0.8},
        macro_score=0.8,
        validator_version="2.0.0",
        secret_key="test_key",
        trace=traces,
    )
    
    logger.log_manifest_generation(manifest, success=True)
    
    verified = verify_manifest(manifest, "test_key")
    logger.log_verification(manifest, verified)
    
    print("✓ Complete workflow executed")
    print(f"  - Traces captured: {len(manifest.trace)}")
    print("  - Manifest generated with signature")
    print(f"  - Verification: {'PASSED' if verified else 'FAILED'}")
    print("  - Logs written to: logs/calibration/workflow_*.log")
    print()


def example_create_trace_files():
    """Example: Create trace example files"""
    print("=" * 70)
    print("Example 8: Create Trace Example Files")
    print("=" * 70)
    
    create_trace_example(output_dir="trace_examples")
    
    print("✓ Trace examples created in: trace_examples/")
    print("  - example_traces.json")
    print()


if __name__ == "__main__":
    print("\n")
    print("*" * 70)
    print("AUDIT TRAIL SYSTEM - EXAMPLES")
    print("*" * 70)
    print("\n")
    
    manifest = example_basic_manifest_generation()
    example_manifest_verification(manifest)
    example_score_reconstruction(manifest)
    example_determinism_validation()
    example_structured_logging()
    example_trace_generation()
    example_complete_workflow()
    example_create_trace_files()
    
    print("*" * 70)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
    print("*" * 70)
    print()
