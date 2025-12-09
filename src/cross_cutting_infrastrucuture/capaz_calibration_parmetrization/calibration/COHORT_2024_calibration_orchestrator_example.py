"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00

SENSITIVE - CALIBRATION SYSTEM CRITICAL

CalibrationOrchestrator Usage Examples

Demonstrates typical calibration workflows for different method roles.
"""

from __future__ import annotations

from .COHORT_2024_calibration_orchestrator import (
    CalibrationContext,
    CalibrationEvidence,
    CalibrationOrchestrator,
)


def example_executor_calibration():
    print("=" * 70)
    print("Example 1: Executor Calibration (Full 8-Layer)")
    print("=" * 70)
    
    orchestrator = CalibrationOrchestrator()
    
    result = orchestrator.calibrate(
        method_id="farfan_pipeline.core.executors.D1_Q1_EquityAnalyzer",
        context=CalibrationContext(
            question_id="Q001",
            dimension_id="DIM01",
            policy_area_id="PA01",
        ),
        evidence=CalibrationEvidence(
            intrinsic_scores={
                "b_theory": 0.92,
                "b_impl": 0.88,
                "b_deploy": 0.85,
                "chain_layer_score": 0.80,
                "contract_layer_score": 0.95,
            },
            compatibility_registry={
                "D1_Q1_EquityAnalyzer": {
                    "questions": {"Q001": 1.0, "Q002": 0.7},
                    "dimensions": {"DIM01": 1.0, "DIM02": 0.6},
                    "policies": {"PA01": 1.0, "PA02": 0.5},
                }
            },
            pdt_structure={
                "total_tokens": 15000,
                "blocks_found": {
                    "Diagnóstico": {"tokens": 4000},
                    "Estratégica": {"tokens": 5000},
                    "PPI": {"tokens": 4000},
                    "Seguimiento": {"tokens": 2000},
                },
                "indicator_matrix_present": True,
                "ppi_matrix_present": True,
            },
            governance_artifacts={
                "version_tag": "COHORT_2024_v1.2.3",
                "config_hash": "a" * 64,
                "signature": "b" * 64,
            },
        ),
    )
    
    print(f"\nMethod ID: {result['method_id']}")
    print(f"Role: {result['role']}")
    print(f"Final Score: {result['final_score']:.4f}")
    print(f"\nActive Layers ({len(result['active_layers'])}):")
    for layer in result["active_layers"]:
        score = result["layer_scores"].get(layer.lstrip("@"), 0.0)
        print(f"  {layer}: {score:.4f}")
    
    print("\nFusion Breakdown:")
    print(f"  Linear Sum: {result['fusion_breakdown']['linear_sum']:.4f}")
    print(f"  Interaction Sum: {result['fusion_breakdown']['interaction_sum']:.4f}")
    
    print("\nCertificate:")
    cert = result["certificate_metadata"]
    print(f"  ID: {cert['certificate_id']}")
    print(f"  Timestamp: {cert['timestamp']}")
    print(f"  Authority: {cert['authority']}")
    
    print("\nValidation:")
    val = result["validation"]
    print(f"  Bounded: {val['is_bounded']}")
    print(f"  Range: [{val['lower_bound']}, {val['upper_bound']}]")
    
    return result


def example_ingest_calibration():
    print("\n" + "=" * 70)
    print("Example 2: Ingest Calibration (4-Layer)")
    print("=" * 70)
    
    orchestrator = CalibrationOrchestrator()
    
    result = orchestrator.calibrate(
        method_id="farfan_pipeline.processing.ingest.PDTParser",
        evidence=CalibrationEvidence(
            intrinsic_scores={
                "base_layer_score": 0.87,
                "chain_layer_score": 0.82,
            },
            pdt_structure={
                "total_tokens": 12000,
                "blocks_found": {
                    "Diagnóstico": {},
                    "Estratégica": {},
                    "PPI": {},
                },
                "indicator_matrix_present": False,
                "ppi_matrix_present": True,
            },
            governance_artifacts={
                "version_tag": "COHORT_2024_v1.1.0",
                "config_hash": "c" * 64,
            },
        ),
    )
    
    print(f"\nMethod ID: {result['method_id']}")
    print(f"Role: {result['role']}")
    print(f"Final Score: {result['final_score']:.4f}")
    print(f"\nActive Layers ({len(result['active_layers'])}):")
    for layer in result["active_layers"]:
        score = result["layer_scores"].get(layer.lstrip("@"), 0.0)
        print(f"  {layer}: {score:.4f}")
    
    return result


def example_utility_calibration():
    print("\n" + "=" * 70)
    print("Example 3: Utility Calibration (3-Layer, Minimal Evidence)")
    print("=" * 70)
    
    orchestrator = CalibrationOrchestrator()
    
    result = orchestrator.calibrate(
        method_id="farfan_pipeline.utils.StringNormalizer",
        evidence=CalibrationEvidence(
            intrinsic_scores={
                "base_layer_score": 0.75,
            },
        ),
    )
    
    print(f"\nMethod ID: {result['method_id']}")
    print(f"Role: {result['role']}")
    print(f"Final Score: {result['final_score']:.4f}")
    print(f"\nActive Layers ({len(result['active_layers'])}):")
    for layer in result["active_layers"]:
        score = result["layer_scores"].get(layer.lstrip("@"), 0.0)
        print(f"  {layer}: {score:.4f}")
    
    return result


def example_minimal_calibration():
    print("\n" + "=" * 70)
    print("Example 4: Minimal Calibration (All Defaults)")
    print("=" * 70)
    
    orchestrator = CalibrationOrchestrator()
    
    result = orchestrator.calibrate(
        method_id="farfan_pipeline.core.unknown_method.SomeMethod"
    )
    
    print(f"\nMethod ID: {result['method_id']}")
    print(f"Role: {result['role']}")
    print(f"Final Score: {result['final_score']:.4f}")
    print(f"Active Layers: {result['active_layers']}")
    
    return result


def example_score_comparison():
    print("\n" + "=" * 70)
    print("Example 5: Compare Multiple Methods")
    print("=" * 70)
    
    orchestrator = CalibrationOrchestrator()
    
    methods = [
        ("farfan_pipeline.core.executors.D1_Q1_Executor", "executor"),
        ("farfan_pipeline.processing.ingest.PDTParser", "ingest"),
        ("farfan_pipeline.utils.TextCleaner", "utility"),
        ("farfan_pipeline.orchestration.PhaseController", "orchestrator"),
    ]
    
    results = []
    for method_id, expected_role in methods:
        result = orchestrator.calibrate(
            method_id=method_id,
            evidence=CalibrationEvidence(
                intrinsic_scores={"base_layer_score": 0.85},
            ),
        )
        results.append((method_id, result))
        print(f"\n{method_id}")
        print(f"  Role: {result['role']} (expected: {expected_role})")
        print(f"  Score: {result['final_score']:.4f}")
        print(f"  Layers: {len(result['active_layers'])}")
    
    return results


def example_fusion_breakdown_analysis():
    print("\n" + "=" * 70)
    print("Example 6: Detailed Fusion Breakdown Analysis")
    print("=" * 70)
    
    orchestrator = CalibrationOrchestrator()
    
    result = orchestrator.calibrate(
        method_id="farfan_pipeline.core.executors.D2_Q3_Analyzer",
        context=CalibrationContext(
            question_id="Q031",
            dimension_id="DIM02",
            policy_area_id="PA03",
        ),
        evidence=CalibrationEvidence(
            intrinsic_scores={
                "base_layer_score": 0.90,
                "chain_layer_score": 0.85,
                "contract_layer_score": 0.88,
            },
            compatibility_registry={
                "D2_Q3_Analyzer": {
                    "questions": {"Q031": 0.95},
                    "dimensions": {"DIM02": 0.92},
                    "policies": {"PA03": 0.89},
                }
            },
            pdt_structure={
                "total_tokens": 18000,
                "blocks_found": {
                    "Diagnóstico": {},
                    "Estratégica": {},
                    "PPI": {},
                    "Seguimiento": {},
                },
                "indicator_matrix_present": True,
                "ppi_matrix_present": True,
            },
            governance_artifacts={
                "version_tag": "COHORT_2024_v1.3.0",
                "config_hash": "d" * 64,
                "signature": "e" * 64,
            },
        ),
    )
    
    print(f"\nMethod: {result['method_id']}")
    print(f"Role: {result['role']}")
    print(f"\n{'='*50}")
    print("LAYER SCORES")
    print("=" * 50)
    for layer in result["active_layers"]:
        layer_key = layer.lstrip("@")
        score = result["layer_scores"].get(layer_key, 0.0)
        print(f"{layer:8} = {score:.4f}")
    
    print(f"\n{'='*50}")
    print("FUSION COMPUTATION")
    print("=" * 50)
    
    fusion = result["fusion_breakdown"]
    print("\nLinear Contributions:")
    for layer, contrib in fusion["linear_contributions"].items():
        print(f"  {layer:8} → {contrib:.6f}")
    
    print(f"\nLinear Sum: {fusion['linear_sum']:.6f}")
    
    print("\nInteraction Contributions:")
    for pair, contrib in fusion["interaction_contributions"].items():
        print(f"  {pair:20} → {contrib:.6f}")
    
    print(f"\nInteraction Sum: {fusion['interaction_sum']:.6f}")
    
    print(f"\n{'='*50}")
    print(f"FINAL SCORE: {result['final_score']:.6f}")
    print("=" * 50)
    
    print(f"\nFormula: Cal(I) = {fusion['linear_sum']:.6f} + {fusion['interaction_sum']:.6f}")
    print(f"        Cal(I) = {result['final_score']:.6f}")
    
    return result


def example_boundedness_validation():
    print("\n" + "=" * 70)
    print("Example 7: Boundedness Validation")
    print("=" * 70)
    
    orchestrator = CalibrationOrchestrator()
    
    test_cases = [
        ("Low Score", {"base_layer_score": 0.2}),
        ("Medium Score", {"base_layer_score": 0.5}),
        ("High Score", {"base_layer_score": 0.95}),
    ]
    
    for label, intrinsic_scores in test_cases:
        result = orchestrator.calibrate(
            method_id="farfan_pipeline.test.method",
            evidence=CalibrationEvidence(intrinsic_scores=intrinsic_scores),
        )
        
        val = result["validation"]
        print(f"\n{label}:")
        print(f"  Score: {result['final_score']:.4f}")
        print(f"  Bounded: {val['is_bounded']}")
        print(f"  Original: {val['original_score']:.4f}")
        print(f"  Clamped: {val['clamped_score']:.4f}")
        if val["violation"]:
            print(f"  Violation: {val['violation']}")
    
    return None


if __name__ == "__main__":
    print("\nCOHORT_2024 CALIBRATION ORCHESTRATOR")
    print("Usage Examples\n")
    
    try:
        example_executor_calibration()
        example_ingest_calibration()
        example_utility_calibration()
        example_minimal_calibration()
        example_score_comparison()
        example_fusion_breakdown_analysis()
        example_boundedness_validation()
        
        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
