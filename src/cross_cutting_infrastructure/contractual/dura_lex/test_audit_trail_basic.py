"""
Basic integration test for audit trail system.

Run with: python test_audit_trail_basic.py
"""

import json
from pathlib import Path

from audit_trail import (
    generate_manifest,
    verify_manifest,
    reconstruct_score,
    validate_determinism,
    StructuredAuditLogger,
    TraceGenerator,
    VerificationManifest,
)


def test_manifest_generation():
    """Test basic manifest generation"""
    print("Testing manifest generation...", end=" ")
    
    manifest = generate_manifest(
        calibration_scores={
            "method1": 0.8,
            "method2": 0.9,
        },
        config_hash="test_hash",
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
    
    assert manifest.signature != ""
    assert len(manifest.calibration_scores) == 2
    assert manifest.results.macro_score == 0.85
    
    print("✓ PASSED")
    return manifest


def test_signature_verification(manifest):
    """Test signature verification"""
    print("Testing signature verification...", end=" ")
    
    valid = verify_manifest(manifest, "test_key")
    assert valid is True
    
    invalid = verify_manifest(manifest, "wrong_key")
    assert invalid is False
    
    print("✓ PASSED")


def test_score_reconstruction(manifest):
    """Test score reconstruction"""
    print("Testing score reconstruction...", end=" ")
    
    reconstructed = reconstruct_score(manifest)
    
    assert abs(reconstructed - manifest.results.macro_score) < 1e-6
    
    print("✓ PASSED")


def test_determinism_validation():
    """Test determinism validation"""
    print("Testing determinism validation...", end=" ")
    
    manifest1 = generate_manifest(
        calibration_scores={"m1": 0.8},
        config_hash="hash1",
        retry=3,
        timeout_s=300.0,
        temperature=0.7,
        thresholds={"t1": 0.7},
        random_seed=42,
        numpy_seed=42,
        seed_version="v1",
        micro_scores=[0.8],
        dimension_scores={"D1": 0.8},
        area_scores={"A1": 0.8},
        macro_score=0.8,
        validator_version="2.0.0",
        secret_key="key",
    )
    
    manifest2 = generate_manifest(
        calibration_scores={"m1": 0.8},
        config_hash="hash1",
        retry=3,
        timeout_s=300.0,
        temperature=0.7,
        thresholds={"t1": 0.7},
        random_seed=42,
        numpy_seed=42,
        seed_version="v1",
        micro_scores=[0.8],
        dimension_scores={"D1": 0.8},
        area_scores={"A1": 0.8},
        macro_score=0.8,
        validator_version="2.0.0",
        secret_key="key",
    )
    
    deterministic = validate_determinism(manifest1, manifest2)
    assert deterministic is True
    
    print("✓ PASSED")


def test_structured_logging():
    """Test structured logging"""
    print("Testing structured logging...", end=" ")
    
    log_dir = Path("logs/calibration")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = StructuredAuditLogger(log_dir=log_dir, component="test")
    logger.log("INFO", "Test message", {"key": "value"})
    
    print("✓ PASSED")


def test_trace_generation():
    """Test operation trace generation"""
    print("Testing trace generation...", end=" ")
    
    with TraceGenerator(enabled=True) as tracer:
        tracer.trace_operation("test_op", {"input": 1}, 2)
        traces = tracer.get_traces()
    
    assert len(traces) == 1
    assert traces[0].operation == "test_op"
    assert traces[0].inputs == {"input": 1}
    assert traces[0].output == 2
    
    print("✓ PASSED")


def test_serialization():
    """Test manifest serialization"""
    print("Testing manifest serialization...", end=" ")
    
    manifest = generate_manifest(
        calibration_scores={"m1": 0.8},
        config_hash="hash",
        retry=3,
        timeout_s=300.0,
        temperature=0.7,
        thresholds={"t1": 0.7},
        random_seed=42,
        numpy_seed=42,
        seed_version="v1",
        micro_scores=[0.8],
        dimension_scores={"D1": 0.8},
        area_scores={"A1": 0.8},
        macro_score=0.8,
        validator_version="2.0.0",
        secret_key="key",
    )
    
    json_str = manifest.to_json()
    data = json.loads(json_str)
    
    reconstructed = VerificationManifest.from_dict(data)
    
    assert reconstructed.results.macro_score == manifest.results.macro_score
    assert reconstructed.signature == manifest.signature
    
    print("✓ PASSED")


def run_all_tests():
    """Run all basic tests"""
    print("\n" + "=" * 70)
    print("AUDIT TRAIL BASIC INTEGRATION TESTS")
    print("=" * 70 + "\n")
    
    try:
        manifest = test_manifest_generation()
        test_signature_verification(manifest)
        test_score_reconstruction(manifest)
        test_determinism_validation()
        test_structured_logging()
        test_trace_generation()
        test_serialization()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70 + "\n")
        
        return True
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
