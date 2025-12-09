"""
Certificate Generation Usage Examples
======================================

Demonstrates how to use the CertificateGenerator to create calibration certificates
with complete audit trails.
"""

from pathlib import Path
from certificate_generator import CertificateGenerator, CalibrationCertificate


def example_1_executor_certificate():
    print("=" * 80)
    print("Example 1: Generate Certificate for Executor (D1_Q1)")
    print("=" * 80)

    generator = CertificateGenerator()

    certificate = generator.generate_certificate(
        instance_id="exec-d1q1-20241215-001",
        method_id="farfan_pipeline.core.orchestrator.executors.D1_Q1_TerritorialCoherenceEvaluator",
        node_id="node_exec_d1_q1_001",
        context={
            "execution_id": "exec-20241215-143022-uuid-abc123",
            "document_id": "PDM-BOG-2024-001",
            "policy_unit_id": "MUNICIPALITY-BOGOTA-2024",
            "dimension": "D1",
            "question": "Q1",
            "phase": "phase_2",
            "cohort": "COHORT_2024",
        },
        intrinsic_score=0.87,
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
        evidence_trail={
            "@b": {
                "source": "intrinsic_calibration_rubric.json",
                "components": {
                    "statistical_validity": 0.94,
                    "logical_consistency": 0.91,
                    "appropriate_assumptions": 0.89,
                },
            },
            "@chain": {
                "source": "method_compatibility.json",
                "evidence": [
                    "Executor properly chains with Phase 1 structural parsers",
                    "Evidence registry populated correctly",
                    "Contract validation passes",
                ],
            },
        },
        computation_graph={
            "nodes": ["phase1_parser", "d1_q1_executor", "aggregator"],
            "edges": [["phase1_parser", "d1_q1_executor"], ["d1_q1_executor", "aggregator"]],
        },
    )

    print(f"\nCertificate generated successfully!")
    print(f"Instance ID: {certificate.instance_id}")
    print(f"Method ID: {certificate.method_id}")
    print(f"Calibrated Score: {certificate.calibrated_score:.4f}")
    print(f"Timestamp: {certificate.timestamp}")
    print(f"Signature: {certificate.signature[:32]}...")

    print("\nValidation Checks:")
    print(f"  All Bounded: {certificate.validation_checks.boundedness['all_bounded']}")
    print(f"  All Weights Non-negative: {certificate.validation_checks.monotonicity['all_weights_non_negative']}")
    print(f"  Normalized: {certificate.validation_checks.normalization['is_normalized']}")
    print(f"  Complete: {certificate.validation_checks.completeness['is_complete']}")

    is_valid = generator.verify_certificate(certificate)
    print(f"\nSignature verification: {'✓ VALID' if is_valid else '✗ INVALID'}")

    output_path = Path("executor_certificate_example.json")
    with open(output_path, "w") as f:
        f.write(certificate.to_json())
    print(f"\nCertificate saved to: {output_path}")

    return certificate


def example_2_analyzer_certificate():
    print("\n" + "=" * 80)
    print("Example 2: Generate Certificate for Analyzer (TeoriaCambio)")
    print("=" * 80)

    generator = CertificateGenerator()

    certificate = generator.generate_certificate(
        instance_id="analyzer-teoria-cambio-20241215-002",
        method_id="farfan_pipeline.methods_dispensary.teoria_cambio.TeoriaCambioAnalyzer",
        node_id="node_analyzer_tc_002",
        context={
            "execution_id": "exec-20241215-153045-uuid-def456",
            "document_id": "PDM-MED-2024-002",
            "policy_unit_id": "MUNICIPALITY-MEDELLIN-2024",
            "analysis_type": "theory_of_change",
            "phase": "phase_2",
            "cohort": "COHORT_2024",
        },
        intrinsic_score=0.79,
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
        evidence_trail={
            "@b": {
                "source": "intrinsic_calibration_rubric.json",
                "components": {
                    "statistical_validity": 0.88,
                    "logical_consistency": 0.84,
                    "appropriate_assumptions": 0.82,
                },
            },
            "@d": {
                "source": "dimension_alignment_validator",
                "dimensions_covered": ["D1", "D2", "D3", "D4"],
                "evidence_count": 22,
                "relevance_score": 0.81,
            },
        },
        computation_graph={
            "nodes": ["document_parser", "teoria_cambio_analyzer", "causal_dag_builder", "monte_carlo_sim"],
            "edges": [
                ["document_parser", "teoria_cambio_analyzer"],
                ["teoria_cambio_analyzer", "causal_dag_builder"],
                ["teoria_cambio_analyzer", "monte_carlo_sim"],
            ],
        },
    )

    print(f"\nCertificate generated successfully!")
    print(f"Instance ID: {certificate.instance_id}")
    print(f"Method ID: {certificate.method_id}")
    print(f"Calibrated Score: {certificate.calibrated_score:.4f}")

    print("\nFusion Formula:")
    print(f"  Symbolic: {certificate.fusion_formula.symbolic}")
    print(f"  Computation steps: {len(certificate.fusion_formula.computation_trace)}")

    print("\nParameter Provenance (sample):")
    for param_name in list(certificate.parameter_provenance.keys())[:3]:
        prov = certificate.parameter_provenance[param_name]
        print(f"  {param_name}: {prov.value} (from {prov.source})")

    is_valid = generator.verify_certificate(certificate)
    print(f"\nSignature verification: {'✓ VALID' if is_valid else '✗ INVALID'}")

    return certificate


def example_3_verify_certificate():
    print("\n" + "=" * 80)
    print("Example 3: Verify Certificate Signature")
    print("=" * 80)

    generator = CertificateGenerator()

    certificate = generator.generate_certificate(
        instance_id="test-verify-001",
        method_id="test.method",
        node_id="node_test_001",
        context={"test": True},
        intrinsic_score=0.75,
        layer_scores={"@b": 0.80, "@chain": 0.70},
        weights={"@b": 0.6, "@chain": 0.4},
    )

    print(f"Certificate generated: {certificate.instance_id}")
    print(f"Original signature: {certificate.signature[:32]}...")

    is_valid = generator.verify_certificate(certificate)
    print(f"\nOriginal certificate verification: {'✓ VALID' if is_valid else '✗ INVALID'}")

    print("\nAttempting to tamper with certificate...")
    tampered_dict = certificate.to_dict()
    tampered_dict["calibrated_score"] = 0.99

    from dataclasses import replace

    tampered_certificate = replace(certificate, calibrated_score=0.99)

    is_valid_tampered = generator.verify_certificate(tampered_certificate)
    print(f"Tampered certificate verification: {'✓ VALID' if is_valid_tampered else '✗ INVALID (expected)'}")


def example_4_config_and_graph_hashes():
    print("\n" + "=" * 80)
    print("Example 4: Config and Graph Hashing")
    print("=" * 80)

    generator = CertificateGenerator()

    certificate1 = generator.generate_certificate(
        instance_id="hash-test-001",
        method_id="test.method",
        node_id="node_001",
        context={"execution": 1},
        intrinsic_score=0.75,
        layer_scores={"@b": 0.80},
        weights={"@b": 1.0},
        computation_graph={"nodes": ["A", "B"], "edges": [["A", "B"]]},
    )

    certificate2 = generator.generate_certificate(
        instance_id="hash-test-002",
        method_id="test.method",
        node_id="node_002",
        context={"execution": 2},
        intrinsic_score=0.75,
        layer_scores={"@b": 0.80},
        weights={"@b": 1.0},
        computation_graph={"nodes": ["A", "B"], "edges": [["A", "B"]]},
    )

    certificate3 = generator.generate_certificate(
        instance_id="hash-test-003",
        method_id="test.method",
        node_id="node_003",
        context={"execution": 3},
        intrinsic_score=0.75,
        layer_scores={"@b": 0.80},
        weights={"@b": 1.0},
        computation_graph={"nodes": ["A", "C"], "edges": [["A", "C"]]},
    )

    print(f"Certificate 1 config_hash: {certificate1.config_hash[:16]}...")
    print(f"Certificate 2 config_hash: {certificate2.config_hash[:16]}...")
    print(f"Config hashes match: {certificate1.config_hash == certificate2.config_hash}")

    print(f"\nCertificate 1 graph_hash: {certificate1.graph_hash[:16]}...")
    print(f"Certificate 2 graph_hash: {certificate2.graph_hash[:16]}...")
    print(f"Graph hashes match (same graph): {certificate1.graph_hash == certificate2.graph_hash}")

    print(f"\nCertificate 3 graph_hash: {certificate3.graph_hash[:16]}...")
    print(f"Graph hashes match (different graph): {certificate1.graph_hash == certificate3.graph_hash}")


if __name__ == "__main__":
    example_1_executor_certificate()
    example_2_analyzer_certificate()
    example_3_verify_certificate()
    example_4_config_and_graph_hashes()

    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
