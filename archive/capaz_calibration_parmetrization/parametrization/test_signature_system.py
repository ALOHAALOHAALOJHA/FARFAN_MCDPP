#!/usr/bin/env python3
"""
Integration Test for Signature-Based Parametrization Analysis System

Tests all components:
- Method signature extraction
- Hardcoded parameter detection
- Signature analysis
- Query API
- Validation

Usage:
    python test_signature_system.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from textwrap import dedent


def create_test_file(test_dir: Path) -> Path:
    test_code = dedent("""
        from typing import Dict, List, Any

        DEFAULT_THRESHOLD = 0.75
        MAX_ITERATIONS = 100

        class TestAnalyzer:
            def __init__(self, config: Dict[str, Any]) -> None:
                self.config = config

            def calculate_probability(self, data: List[float], threshold: float = 0.5) -> float:
                '''Calculate probability from data. Returns value between 0 and 1.'''
                cutoff = 0.8
                min_value = 0.0
                max_value = 1.0
                return min(max(sum(data) / len(data), min_value), max_value)

            def analyze_with_confidence(
                self,
                text: str,
                confidence_threshold: float = 0.7,
                alpha: float = 0.05,
                beta: float = 1.0
            ) -> Dict[str, Any]:
                '''Analyze text with confidence estimation.'''
                default_temperature = 0.8
                max_tokens = 1000
                return {"confidence": 0.9, "result": "analyzed"}

            def _private_helper(self, x: int) -> int:
                '''This should be ignored (private method).'''
                return x * 2

        def standalone_function(param1: str, param2: int = 10) -> bool:
            '''A standalone function.'''
            timeout = 30
            return True
    """)

    test_file = test_dir / "test_module.py"
    test_file.write_text(test_code)
    return test_file


def test_extraction(test_dir: Path) -> bool:
    print("=" * 70)
    print("TEST 1: Method Signature Extraction")
    print("=" * 70)

    from method_signature_extractor import MethodSignatureExtractor

    extractor = MethodSignatureExtractor(test_dir)
    extractor.scan_repository(include_patterns=["*.py"])

    print(f"✓ Scanned files")
    print(f"✓ Found {len(extractor.signatures)} signatures")

    expected_methods = [
        "test_module.TestAnalyzer.calculate_probability",
        "test_module.TestAnalyzer.analyze_with_confidence",
        "test_module.standalone_function",
    ]

    for method in expected_methods:
        if method in extractor.signatures:
            print(f"✓ Found expected method: {method}")
        else:
            print(f"✗ Missing expected method: {method}")
            return False

    sig = extractor.signatures["test_module.TestAnalyzer.calculate_probability"]
    if "data" in sig.required_inputs:
        print("✓ Correctly identified required input: data")
    else:
        print("✗ Failed to identify required input")
        return False

    if "threshold" in sig.optional_inputs:
        print("✓ Correctly identified optional input: threshold")
    else:
        print("✗ Failed to identify optional input")
        return False

    if sig.hardcoded_parameters:
        print(f"✓ Detected {len(sig.hardcoded_parameters)} hardcoded parameters")
    else:
        print("✗ Failed to detect hardcoded parameters")
        return False

    print("\n✅ Extraction test passed\n")
    return True


def test_analysis(test_dir: Path) -> bool:
    print("=" * 70)
    print("TEST 2: Signature Analysis")
    print("=" * 70)

    from method_signature_extractor import MethodSignatureExtractor
    from signature_analyzer import SignatureAnalyzer

    extractor = MethodSignatureExtractor(test_dir)
    extractor.scan_repository(include_patterns=["*.py"])

    analyzer = SignatureAnalyzer(extractor.signatures)

    output_ranges = analyzer.analyze_output_ranges()
    if output_ranges:
        print(f"✓ Analyzed output ranges for {len(output_ranges)} methods")
    else:
        print("⚠ No output ranges inferred (this may be OK)")

    patterns = analyzer.detect_parameter_patterns()
    print(f"✓ Detected parameter patterns:")
    for pattern_type, params in patterns.items():
        if params:
            print(f"  - {pattern_type}: {len(params)} parameters")

    priorities = analyzer.generate_migration_priority()
    if priorities:
        print(f"✓ Generated {len(priorities)} migration priorities")
    else:
        print("✗ Failed to generate migration priorities")
        return False

    print("\n✅ Analysis test passed\n")
    return True


def test_export_and_validation(test_dir: Path) -> bool:
    print("=" * 70)
    print("TEST 3: Export and Validation")
    print("=" * 70)

    from method_signature_extractor import MethodSignatureExtractor
    from validate_signatures import SignatureValidator

    extractor = MethodSignatureExtractor(test_dir)
    extractor.scan_repository(include_patterns=["*.py"])

    output_path = test_dir / "test_signatures.json"
    extractor.export_signatures(output_path)

    if output_path.exists():
        print(f"✓ Exported signatures to {output_path.name}")
    else:
        print("✗ Failed to export signatures")
        return False

    validator = SignatureValidator(output_path)
    is_valid = validator.validate()

    if is_valid:
        print("✓ Validation passed")
    else:
        print("✗ Validation failed")
        print("Errors:")
        for error in validator.errors:
            print(f"  - {error}")
        return False

    print("\n✅ Export and validation test passed\n")
    return True


def test_query_api(test_dir: Path) -> bool:
    print("=" * 70)
    print("TEST 4: Query API")
    print("=" * 70)

    from method_signature_extractor import MethodSignatureExtractor
    from signature_query_api import SignatureDatabase, Signature

    extractor = MethodSignatureExtractor(test_dir)
    extractor.scan_repository(include_patterns=["*.py"])

    output_path = test_dir / "test_signatures.json"
    extractor.export_signatures(output_path)

    db = SignatureDatabase.load(output_path)
    print(f"✓ Loaded database with {len(db.signatures)} signatures")

    sig = db.get_signature("test_module.TestAnalyzer.calculate_probability")
    if sig:
        print(f"✓ Retrieved signature: {sig.normalized_name}")
    else:
        print("✗ Failed to retrieve signature")
        return False

    results = db.find_by_method_name("calculate", exact=False)
    if results:
        print(f"✓ Found {len(results)} methods matching 'calculate'")
    else:
        print("✗ Failed to find methods by name")
        return False

    results = db.find_by_class("TestAnalyzer")
    if results:
        print(f"✓ Found {len(results)} methods in TestAnalyzer class")
    else:
        print("✗ Failed to find methods by class")
        return False

    stats = db.get_statistics()
    print(f"✓ Generated statistics:")
    print(f"  - Total signatures: {stats['total_signatures']}")
    print(f"  - Class methods: {stats['class_methods']}")

    print("\n✅ Query API test passed\n")
    return True


def run_all_tests() -> int:
    print("\n" + "=" * 70)
    print("SIGNATURE SYSTEM INTEGRATION TESTS")
    print("=" * 70 + "\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        test_file = create_test_file(test_dir)
        print(f"Created test file: {test_file}\n")

        tests = [
            ("Extraction", test_extraction),
            ("Analysis", test_analysis),
            ("Export & Validation", test_export_and_validation),
            ("Query API", test_query_api),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            try:
                if test_func(test_dir):
                    passed += 1
                else:
                    failed += 1
                    print(f"❌ {test_name} test FAILED\n")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name} test FAILED with exception:")
                print(f"   {e}\n")
                import traceback
                traceback.print_exc()

        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Passed: {passed}/{len(tests)}")
        print(f"Failed: {failed}/{len(tests)}")
        print("=" * 70)

        if failed == 0:
            print("\n✅ ALL TESTS PASSED\n")
            return 0
        else:
            print(f"\n❌ {failed} TEST(S) FAILED\n")
            return 1


def main() -> int:
    try:
        return run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
