"""
Example: Layer Evaluator Details

Demonstrates individual layer evaluator behavior and score computation.
"""

from pathlib import Path
from src.orchestration.calibration_orchestrator import (
    CalibrationOrchestrator,
    LayerID,
)


def example_layer_evaluator_details():
    """Demonstrate layer evaluator details."""
    print("=" * 70)
    print("EXAMPLE: Layer Evaluator Details")
    print("=" * 70)
    
    config_dir = Path("src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration")
    orchestrator = CalibrationOrchestrator.from_config_dir(config_dir)
    print("✓ CalibrationOrchestrator initialized")
    
    method_id = "test.method.executor"
    
    print(f"\n{'-' * 70}")
    print(f"Layer-by-Layer Evaluation for: {method_id}")
    print(f"{'-' * 70}")
    
    print(f"\n{LayerID.BASE.value} - Base Quality Layer:")
    base_score = orchestrator.base_evaluator.evaluate(method_id)
    print(f"  Evaluates: b_theory, b_impl, b_deploy")
    print(f"  Score: {base_score:.4f}")
    
    print(f"\n{LayerID.CHAIN.value} - Chain Compatibility Layer:")
    chain_score = orchestrator.chain_evaluator.evaluate(method_id)
    print(f"  Evaluates: method wiring compatibility")
    print(f"  Score: {chain_score:.4f}")
    
    pdt_structure = {
        "chunk_count": 60,
        "completeness": 0.85,
        "structure_quality": 0.9
    }
    
    print(f"\n{LayerID.UNIT.value} - Unit/Document Quality Layer:")
    unit_score = orchestrator.unit_evaluator.evaluate(pdt_structure)
    print(f"  Evaluates: document structure quality")
    print(f"  Input: chunk_count={pdt_structure['chunk_count']}, "
          f"completeness={pdt_structure['completeness']}")
    print(f"  Score: {unit_score:.4f}")
    
    print(f"\n{LayerID.QUESTION.value} - Question Appropriateness Layer:")
    question_score = orchestrator.question_evaluator.evaluate(method_id, "Q001")
    print(f"  Evaluates: method appropriateness for question Q001")
    print(f"  Score: {question_score:.4f}")
    
    print(f"\n{LayerID.DIMENSION.value} - Dimension Alignment Layer:")
    dimension_score = orchestrator.dimension_evaluator.evaluate(method_id, "D1")
    print(f"  Evaluates: method alignment with dimension D1")
    print(f"  Score: {dimension_score:.4f}")
    
    print(f"\n{LayerID.POLICY.value} - Policy Area Fit Layer:")
    policy_score = orchestrator.policy_evaluator.evaluate(method_id, "PA1")
    print(f"  Evaluates: method fit for policy area PA1")
    print(f"  Score: {policy_score:.4f}")
    
    print(f"\n{LayerID.CONGRUENCE.value} - Contract Compliance Layer:")
    congruence_score = orchestrator.congruence_evaluator.evaluate(method_id)
    print(f"  Evaluates: contract compliance")
    print(f"  Score: {congruence_score:.4f}")
    
    print(f"\n{LayerID.META.value} - Meta/Governance Layer:")
    meta_score = orchestrator.meta_evaluator.evaluate(method_id)
    print(f"  Evaluates: governance quality")
    print(f"  Score: {meta_score:.4f}")
    
    print("\n" + "=" * 70)
    print("Layer Score Summary")
    print("=" * 70)
    
    layer_scores = {
        LayerID.BASE: base_score,
        LayerID.CHAIN: chain_score,
        LayerID.UNIT: unit_score,
        LayerID.QUESTION: question_score,
        LayerID.DIMENSION: dimension_score,
        LayerID.POLICY: policy_score,
        LayerID.CONGRUENCE: congruence_score,
        LayerID.META: meta_score,
    }
    
    for layer_id, score in layer_scores.items():
        bar_length = int(score * 40)
        bar = "█" * bar_length + "░" * (40 - bar_length)
        print(f"  {layer_id.value:10} {bar} {score:.4f}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    example_layer_evaluator_details()
