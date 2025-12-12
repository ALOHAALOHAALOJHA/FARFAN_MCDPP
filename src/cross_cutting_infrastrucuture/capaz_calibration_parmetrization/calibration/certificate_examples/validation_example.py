"""
Certificate Validation Usage Examples
======================================

Demonstrates validation, analysis, and comparison of calibration certificates.
"""

from pathlib import Path
import sys

try:
    from canonic_phases.Phase_zero.paths import PROJECT_ROOT
except ImportError:
    PROJECT_ROOT = Path(__file__).resolve().parents[4]

src_root = PROJECT_ROOT / "src"
src_root_str = str(src_root)
if src_root_str not in sys.path:
    sys.path.append(src_root_str)

from certificate_generator import CertificateGenerator
from certificate_validator import (
    CertificateValidator,
    CertificateAnalyzer,
    CertificateComparator,
    load_certificate_from_json,
)


def example_1_validate_certificate():
    print("=" * 80)
    print("Example 1: Validate Certificate")
    print("=" * 80)

    generator = CertificateGenerator()

    certificate = generator.generate_certificate(
        instance_id="validate-test-001",
        method_id="test.executor.D1_Q1",
        node_id="node_001",
        context={"test": True},
        intrinsic_score=0.85,
        layer_scores={
            "@b": 0.92,
            "@chain": 0.88,
            "@q": 0.85,
            "@d": 0.90,
            "@p": 0.83,
            "@C": 0.89,
            "@u": 0.78,
            "@m": 0.81,
        },
        weights={
            "@b": 0.17,
            "@chain": 0.13,
            "@q": 0.08,
            "@d": 0.07,
            "@p": 0.06,
            "@C": 0.08,
            "@u": 0.04,
            "@m": 0.04,
        },
        interaction_weights={
            "@u,@chain": 0.13,
            "@chain,@C": 0.10,
            "@q,@d": 0.10,
        },
    )

    validator = CertificateValidator()
    report = validator.validate_certificate(certificate)

    print(f"\nValidation Result: {'✓ VALID' if report.is_valid else '✗ INVALID'}")
    print(f"Errors: {len(report.errors)}")
    print(f"Warnings: {len(report.warnings)}")

    if report.errors:
        print("\nErrors:")
        for error in report.errors:
            print(f"  - {error}")

    if report.warnings:
        print("\nWarnings:")
        for warning in report.warnings:
            print(f"  - {warning}")

    print("\nInfo:")
    for key, value in report.info.items():
        print(f"  {key}: {value}")


def example_2_analyze_certificate():
    print("\n" + "=" * 80)
    print("Example 2: Analyze Certificate")
    print("=" * 80)

    generator = CertificateGenerator()

    certificate = generator.generate_certificate(
        instance_id="analyze-test-001",
        method_id="test.executor.D2_Q3",
        node_id="node_002",
        context={"document_id": "PDM-001"},
        intrinsic_score=0.75,
        layer_scores={
            "@b": 0.88,
            "@chain": 0.82,
            "@q": 0.78,
            "@d": 0.85,
            "@p": 0.72,
            "@C": 0.80,
            "@u": 0.68,
            "@m": 0.74,
        },
        weights={
            "@b": 0.17,
            "@chain": 0.13,
            "@q": 0.08,
            "@d": 0.07,
            "@p": 0.06,
            "@C": 0.08,
            "@u": 0.04,
            "@m": 0.04,
        },
        interaction_weights={
            "@u,@chain": 0.13,
            "@chain,@C": 0.10,
            "@q,@d": 0.10,
        },
    )

    analysis = CertificateAnalyzer.analyze_certificate(certificate)

    print("\nBasic Info:")
    for key, value in analysis["basic_info"].items():
        print(f"  {key}: {value}")

    print("\nScores:")
    for key, value in analysis["scores"].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    print("\nLayer Statistics:")
    layer_stats = analysis["layer_statistics"]
    print(f"  Count: {layer_stats['count']}")
    print(f"  Mean: {layer_stats['mean']:.4f}")
    print(f"  Min: {layer_stats['min']:.4f}")
    print(f"  Max: {layer_stats['max']:.4f}")
    print(f"  Range: {layer_stats['range']:.4f}")

    print("\nWeight Statistics:")
    print(f"  Linear weights: {analysis['weight_statistics']['linear']['count']} " f"(sum={analysis['weight_statistics']['linear']['sum']:.4f})")
    print(
        f"  Interaction weights: {analysis['weight_statistics']['interaction']['count']} "
        f"(sum={analysis['weight_statistics']['interaction']['sum']:.4f})"
    )

    print("\nValidation Summary:")
    for key, value in analysis["validation_summary"].items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value}")


def example_3_compare_certificates():
    print("\n" + "=" * 80)
    print("Example 3: Compare Two Certificates")
    print("=" * 80)

    generator = CertificateGenerator()

    cert1 = generator.generate_certificate(
        instance_id="compare-test-001",
        method_id="test.executor.D1_Q1",
        node_id="node_001",
        context={"version": "v1"},
        intrinsic_score=0.80,
        layer_scores={
            "@b": 0.85,
            "@chain": 0.82,
            "@q": 0.78,
            "@d": 0.81,
            "@p": 0.76,
            "@C": 0.80,
            "@u": 0.72,
            "@m": 0.75,
        },
        weights={
            "@b": 0.17,
            "@chain": 0.13,
            "@q": 0.08,
            "@d": 0.07,
            "@p": 0.06,
            "@C": 0.08,
            "@u": 0.04,
            "@m": 0.04,
        },
        interaction_weights={
            "@u,@chain": 0.13,
            "@chain,@C": 0.10,
            "@q,@d": 0.10,
        },
    )

    cert2 = generator.generate_certificate(
        instance_id="compare-test-002",
        method_id="test.executor.D1_Q1",
        node_id="node_001",
        context={"version": "v2"},
        intrinsic_score=0.82,
        layer_scores={
            "@b": 0.88,
            "@chain": 0.85,
            "@q": 0.80,
            "@d": 0.83,
            "@p": 0.78,
            "@C": 0.82,
            "@u": 0.74,
            "@m": 0.77,
        },
        weights={
            "@b": 0.17,
            "@chain": 0.13,
            "@q": 0.08,
            "@d": 0.07,
            "@p": 0.06,
            "@C": 0.08,
            "@u": 0.04,
            "@m": 0.04,
        },
        interaction_weights={
            "@u,@chain": 0.13,
            "@chain,@C": 0.10,
            "@q,@d": 0.10,
        },
    )

    comparison = CertificateComparator.compare_certificates(cert1, cert2)

    print("\nMetadata:")
    print(f"  Same method: {comparison['metadata']['same_method']}")
    print(f"  Cert 1 ID: {comparison['metadata']['cert1_id']}")
    print(f"  Cert 2 ID: {comparison['metadata']['cert2_id']}")

    print("\nScore Comparison:")
    score_comp = comparison["score_comparison"]
    print(f"  Intrinsic score diff: {score_comp['intrinsic_score_diff']:+.4f}")
    print(f"  Calibrated score diff: {score_comp['calibrated_score_diff']:+.4f}")

    print("\nLayer Comparison (top 5 changes):")
    layer_comp = comparison["layer_comparison"]
    sorted_layers = sorted(
        [(k, v) for k, v in layer_comp.items() if "diff" in v],
        key=lambda x: abs(x[1]["diff"]),
        reverse=True,
    )[:5]

    for layer, data in sorted_layers:
        print(f"  {layer}: {data['cert1']:.4f} → {data['cert2']:.4f} ({data['diff']:+.4f})")

    print("\nConfig Comparison:")
    print(f"  Same config: {comparison['config_comparison']['same_config']}")
    print(f"  Same graph: {comparison['config_comparison']['same_graph']}")


def example_4_invalid_certificate():
    print("\n" + "=" * 80)
    print("Example 4: Validate Invalid Certificate")
    print("=" * 80)

    generator = CertificateGenerator()

    certificate = generator.generate_certificate(
        instance_id="invalid-test-001",
        method_id="test.executor",
        node_id="node_001",
        context={},
        intrinsic_score=1.5,
        layer_scores={
            "@b": 0.92,
            "@chain": -0.10,
        },
        weights={
            "@b": 0.6,
            "@chain": 0.5,
        },
    )

    validator = CertificateValidator()
    report = validator.validate_certificate(certificate)

    print(f"\nValidation Result: {'✓ VALID' if report.is_valid else '✗ INVALID (expected)'}")
    print(f"Errors: {len(report.errors)}")

    if report.errors:
        print("\nErrors found:")
        for error in report.errors:
            print(f"  - {error}")


def example_5_load_and_validate_json():
    print("\n" + "=" * 80)
    print("Example 5: Load and Validate Certificate from JSON")
    print("=" * 80)

    examples_dir = Path(__file__).parent
    executor_cert_path = examples_dir / "example_executor_certificate.json"

    if not executor_cert_path.exists():
        print(f"Certificate file not found: {executor_cert_path}")
        return

    certificate = load_certificate_from_json(executor_cert_path)

    print(f"Loaded certificate: {certificate.instance_id}")
    print(f"Method: {certificate.method_id}")
    print(f"Timestamp: {certificate.timestamp}")

    validator = CertificateValidator()
    report = validator.validate_certificate(certificate)

    print(f"\nValidation Result: {'✓ VALID' if report.is_valid else '✗ INVALID'}")

    if report.errors:
        print("\nErrors:")
        for error in report.errors:
            print(f"  - {error}")

    if report.warnings:
        print("\nWarnings:")
        for warning in report.warnings:
            print(f"  - {warning}")

    analysis = CertificateAnalyzer.analyze_certificate(certificate)
    print(f"\nCalibrated score: {analysis['scores']['calibrated_score']:.4f}")
    print(f"Adjustment from intrinsic: {analysis['scores']['adjustment']:+.4f} ({analysis['scores']['adjustment_pct']:+.2f}%)")


if __name__ == "__main__":
    example_1_validate_certificate()
    example_2_analyze_certificate()
    example_3_compare_certificates()
    example_4_invalid_certificate()
    example_5_load_and_validate_json()

    print("\n" + "=" * 80)
    print("All validation examples completed!")
    print("=" * 80)
