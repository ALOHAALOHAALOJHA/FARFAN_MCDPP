"""
Certificate Integration Example
================================

Demonstrates how to integrate certificate generation with the actual F.A.R.F.A.N.
calibration system, including:
- Loading calibration config from COHORT_2024
- Computing layer scores
- Generating certificates with real evidence trails
- Storing certificates for audit trails
"""

import json
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


def example_integration_with_cohort_2024():
    print("=" * 80)
    print("Integration Example: Certificate Generation with COHORT_2024 Config")
    print("=" * 80)

    calibration_dir = Path(__file__).parent.parent
    fusion_weights_path = calibration_dir / "COHORT_2024_fusion_weights.json"
    layer_assignment_path = calibration_dir / "COHORT_2024_layer_assignment.py"

    print(f"\nLoading calibration config from:")
    print(f"  - {fusion_weights_path.name}")
    print(f"  - {layer_assignment_path.name}")

    generator = CertificateGenerator(config_dir=calibration_dir)

    print("\nSimulating executor execution for D3_Q2_FinancialSustainabilityEvaluator...")

    layer_scores = {
        "@b": compute_base_quality_score(),
        "@chain": compute_chain_score(),
        "@q": compute_question_appropriateness_score(),
        "@d": compute_dimension_alignment_score(),
        "@p": compute_policy_area_fit_score(),
        "@C": compute_contract_compliance_score(),
        "@u": compute_document_quality_score(),
        "@m": compute_governance_maturity_score(),
    }

    print("\nLayer scores computed:")
    for layer, score in layer_scores.items():
        print(f"  {layer}: {score:.4f}")

    weights = {
        "@b": 0.17,
        "@chain": 0.13,
        "@q": 0.08,
        "@d": 0.07,
        "@p": 0.06,
        "@C": 0.08,
        "@u": 0.04,
        "@m": 0.04,
    }

    interaction_weights = {
        "@u,@chain": 0.13,
        "@chain,@C": 0.10,
        "@q,@d": 0.10,
    }

    evidence_trail = build_evidence_trail(layer_scores)

    computation_graph = {
        "nodes": [
            "phase1_structural_parser",
            "phase2_d3_q2_executor",
            "evidence_registry",
            "phase4_aggregator",
        ],
        "edges": [
            ["phase1_structural_parser", "phase2_d3_q2_executor"],
            ["phase2_d3_q2_executor", "evidence_registry"],
            ["evidence_registry", "phase4_aggregator"],
        ],
        "metadata": {
            "executor_class": "D3_Q2_FinancialSustainabilityEvaluator",
            "dimension": "D3",
            "question": "Q2",
            "phase": "phase_2",
        },
    }

    intrinsic_score = 0.84

    print("\nGenerating certificate...")

    certificate = generator.generate_certificate(
        instance_id="exec-d3q2-integration-example-001",
        method_id="farfan_pipeline.core.orchestrator.executors.D3_Q2_FinancialSustainabilityEvaluator",
        node_id="node_exec_d3_q2_001",
        context={
            "execution_id": "exec-integration-example-001",
            "document_id": "PDM-CALI-2024-001",
            "policy_unit_id": "MUNICIPALITY-CALI-2024",
            "dimension": "D3",
            "question": "Q2",
            "phase": "phase_2",
            "cohort": "COHORT_2024",
            "timestamp_start": "2024-12-15T16:30:00Z",
            "timestamp_end": "2024-12-15T16:30:15Z",
            "execution_time_ms": 15234.5,
        },
        intrinsic_score=intrinsic_score,
        layer_scores=layer_scores,
        weights=weights,
        interaction_weights=interaction_weights,
        evidence_trail=evidence_trail,
        computation_graph=computation_graph,
    )

    print(f"\n✓ Certificate generated successfully!")
    print(f"  Instance ID: {certificate.instance_id}")
    print(f"  Method ID: {certificate.method_id}")
    print(f"  Intrinsic Score: {certificate.intrinsic_score:.4f}")
    print(f"  Calibrated Score: {certificate.calibrated_score:.4f}")
    print(f"  Adjustment: {certificate.calibrated_score - certificate.intrinsic_score:+.4f}")
    print(f"  Timestamp: {certificate.timestamp}")

    print("\nValidation checks:")
    checks = certificate.validation_checks
    print(f"  ✓ Boundedness: {checks.boundedness['all_bounded']}")
    print(f"  ✓ Monotonicity: {checks.monotonicity['all_weights_non_negative']}")
    print(f"  ✓ Normalization: {checks.normalization['is_normalized']}")
    print(f"  ✓ Completeness: {checks.completeness['is_complete']}")

    print("\nFusion formula:")
    print(f"  Symbolic: {certificate.fusion_formula.symbolic}")
    print(f"  Computation steps: {len(certificate.fusion_formula.computation_trace)}")

    print("\nParameter provenance (sample):")
    for i, (param_name, prov) in enumerate(list(certificate.parameter_provenance.items())[:3]):
        print(f"  {param_name}:")
        print(f"    value: {prov.value}")
        print(f"    source: {prov.source}")
        print(f"    justification: {prov.justification[:60]}...")

    print("\nConfig hashes:")
    print(f"  Config hash: {certificate.config_hash[:32]}...")
    print(f"  Graph hash: {certificate.graph_hash[:32]}...")

    is_valid = generator.verify_certificate(certificate)
    print(f"\nSignature verification: {'✓ VALID' if is_valid else '✗ INVALID'}")

    output_path = Path("integration_example_certificate.json")
    with open(output_path, "w") as f:
        f.write(certificate.to_json())
    print(f"\nCertificate saved to: {output_path}")

    return certificate


def compute_base_quality_score() -> float:
    components = {
        "statistical_validity": 0.89,
        "logical_consistency": 0.86,
        "appropriate_assumptions": 0.84,
    }
    score = 0.4 * components["statistical_validity"] + 0.3 * components["logical_consistency"] + 0.3 * components["appropriate_assumptions"]
    return round(score, 4)


def compute_chain_score() -> float:
    checks = {
        "input_contract_satisfied": True,
        "output_contract_satisfied": True,
        "evidence_flow_validated": True,
        "phase_transition_valid": True,
    }
    score = sum(checks.values()) / len(checks)
    return round(score * 0.85, 4)


def compute_question_appropriateness_score() -> float:
    return 0.82


def compute_dimension_alignment_score() -> float:
    return 0.87


def compute_policy_area_fit_score() -> float:
    return 0.79


def compute_contract_compliance_score() -> float:
    return 0.84


def compute_document_quality_score() -> float:
    components = {"text_clarity": 0.81, "structure_completeness": 0.77, "metadata_quality": 0.76}
    return round(sum(components.values()) / len(components), 4)


def compute_governance_maturity_score() -> float:
    components = {"institutional_capacity": 0.80, "transparency_level": 0.76, "participation_mechanisms": 0.78}
    return round(sum(components.values()) / len(components), 4)


def build_evidence_trail(layer_scores: dict[str, float]) -> dict:
    return {
        "@b": {
            "source": "intrinsic_calibration_rubric.json",
            "components": {
                "statistical_validity": 0.89,
                "logical_consistency": 0.86,
                "appropriate_assumptions": 0.84,
            },
            "formula": "0.4*statistical_validity + 0.3*logical_consistency + 0.3*appropriate_assumptions",
            "computation": f"0.4*0.89 + 0.3*0.86 + 0.3*0.84 = {layer_scores['@b']:.4f}",
            "evidence_count": 3,
        },
        "@chain": {
            "source": "method_compatibility.json",
            "evidence": [
                "Input contract validation passed",
                "Output contract validation passed",
                "Evidence flow to phase 4 aggregator verified",
                "Phase transition contracts satisfied",
            ],
            "checks_passed": 4,
            "checks_total": 4,
            "pass_rate": 1.0,
            "adjusted_score": layer_scores["@chain"],
        },
        "@q": {
            "source": "questionnaire_monolith.json",
            "question_id": "D3.Q2",
            "question_text": "Is financial sustainability adequately addressed?",
            "dimension": "D3",
            "semantic_similarity": 0.88,
            "question_match_score": 0.82,
            "evidence_keywords": ["financial", "sustainability", "budget", "resources", "viability"],
        },
        "@d": {
            "source": "dimension_alignment_validator",
            "target_dimension": "D3",
            "evidence_count": 18,
            "relevance_scores": [0.92, 0.89, 0.85, 0.84, 0.87],
            "mean_relevance": 0.87,
        },
        "@p": {
            "source": "policy_area_classifier",
            "primary_area": "financial_management",
            "secondary_areas": ["budget_planning", "resource_allocation"],
            "confidence": 0.79,
            "policy_keywords_matched": 12,
        },
        "@C": {
            "source": "contract_compliance_validator",
            "contracts_checked": [
                "AnalysisInputV2",
                "AnalysisOutputV2",
                "ExecutionContextV2",
                "EvidenceContract",
            ],
            "checks_passed": 17,
            "checks_total": 20,
            "compliance_rate": 0.85,
            "adjusted_score": layer_scores["@C"],
        },
        "@u": {
            "source": "document_quality_metrics",
            "text_clarity": 0.81,
            "structure_completeness": 0.77,
            "metadata_quality": 0.76,
            "completeness_checks": {
                "has_financial_section": True,
                "has_budget_tables": True,
                "has_temporal_data": True,
            },
        },
        "@m": {
            "source": "governance_maturity_evaluator",
            "institutional_capacity": 0.80,
            "transparency_level": 0.76,
            "participation_mechanisms": 0.78,
            "maturity_indicators": ["budget_transparency", "citizen_participation", "accountability_mechanisms"],
        },
    }


def example_batch_certificate_generation():
    print("\n" + "=" * 80)
    print("Batch Certificate Generation Example")
    print("=" * 80)

    generator = CertificateGenerator()

    executors = [
        ("D1_Q1", "TerritorialCoherenceEvaluator", "D1", "Q1"),
        ("D2_Q3", "SocialInclusionEvaluator", "D2", "Q3"),
        ("D3_Q2", "FinancialSustainabilityEvaluator", "D3", "Q2"),
        ("D4_Q4", "EnvironmentalImpactEvaluator", "D4", "Q4"),
        ("D5_Q1", "InstitutionalCapacityEvaluator", "D5", "Q1"),
    ]

    certificates = []

    for executor_id, executor_name, dimension, question in executors:
        print(f"\nGenerating certificate for {executor_id}_{executor_name}...")

        layer_scores = {
            "@b": 0.85 + (hash(executor_id) % 10) / 100,
            "@chain": 0.82 + (hash(executor_name) % 10) / 100,
            "@q": 0.78 + (hash(dimension) % 10) / 100,
            "@d": 0.84 + (hash(question) % 10) / 100,
            "@p": 0.76 + (hash(executor_id + dimension) % 10) / 100,
            "@C": 0.80 + (hash(executor_name + question) % 10) / 100,
            "@u": 0.72 + (hash(dimension + question) % 10) / 100,
            "@m": 0.75 + (hash(executor_id + executor_name) % 10) / 100,
        }

        certificate = generator.generate_certificate(
            instance_id=f"batch-{executor_id.lower()}-001",
            method_id=f"farfan_pipeline.core.orchestrator.executors.{executor_id}_{executor_name}",
            node_id=f"node_{executor_id.lower()}",
            context={
                "dimension": dimension,
                "question": question,
                "batch_id": "batch-001",
            },
            intrinsic_score=0.80,
            layer_scores=layer_scores,
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

        certificates.append(certificate)
        print(f"  ✓ Certificate {certificate.instance_id} generated (score: {certificate.calibrated_score:.4f})")

    print(f"\n✓ Generated {len(certificates)} certificates")

    batch_output_path = Path("batch_certificates.json")
    with open(batch_output_path, "w") as f:
        json.dump([cert.to_dict() for cert in certificates], f, indent=2, sort_keys=True)
    print(f"Batch certificates saved to: {batch_output_path}")

    return certificates


if __name__ == "__main__":
    example_integration_with_cohort_2024()
    example_batch_certificate_generation()

    print("\n" + "=" * 80)
    print("Integration examples completed successfully!")
    print("=" * 80)
