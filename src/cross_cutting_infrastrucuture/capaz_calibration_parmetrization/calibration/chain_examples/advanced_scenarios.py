"""
Chain Layer Evaluator - Advanced Scenarios

Demonstrates advanced usage patterns including:
- Integration with MethodSignatureValidator
- Real-world policy analysis chains
- Performance optimization
- Error handling
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from canonic_phases.Phase_zero.paths import PROJECT_ROOT
except ImportError:
    PROJECT_ROOT = Path(__file__).resolve().parents[4]

src_root = PROJECT_ROOT / "src"
src_root_str = str(src_root)
if src_root_str not in sys.path:
    sys.path.insert(0, src_root_str)

from COHORT_2024_chain_layer import ChainLayerEvaluator


def example_farfan_pipeline() -> None:
    """Example: F.A.R.F.A.N policy analysis pipeline chain."""
    print("=" * 80)
    print("EXAMPLE 1: F.A.R.F.A.N Policy Analysis Pipeline")
    print("=" * 80)

    signatures = {
        "phase1_document_ingestion": {
            "required_inputs": ["policy_document_path", "municipality_id"],
            "optional_inputs": ["encoding", "page_range", "metadata"],
            "critical_optional": ["municipality_id"],
            "output_type": "dict",
        },
        "phase2_structural_parsing": {
            "required_inputs": ["raw_document"],
            "optional_inputs": ["ontology", "parser_config"],
            "critical_optional": ["ontology"],
            "output_type": "dict",
        },
        "phase3_semantic_analysis": {
            "required_inputs": ["structured_document", "ontology"],
            "optional_inputs": ["language_model", "confidence_threshold"],
            "critical_optional": ["language_model"],
            "output_type": "dict",
        },
        "phase4_dimension_scoring_d1": {
            "required_inputs": ["semantic_features", "questionnaire"],
            "optional_inputs": ["weights", "aggregation_method"],
            "critical_optional": [],
            "output_type": "dict",
        },
        "phase5_cross_dimension_analysis": {
            "required_inputs": ["dimension_scores"],
            "optional_inputs": ["interaction_weights", "choquet_config"],
            "critical_optional": ["interaction_weights"],
            "output_type": "dict",
        },
        "phase6_causal_inference": {
            "required_inputs": ["dimensional_analysis"],
            "optional_inputs": ["causal_model", "evidence_threshold"],
            "critical_optional": ["causal_model"],
            "output_type": "dict",
        },
        "phase7_report_generation": {
            "required_inputs": ["analysis_results"],
            "optional_inputs": ["report_template", "format", "language"],
            "critical_optional": [],
            "output_type": "str",
        },
    }

    evaluator = ChainLayerEvaluator(signatures)

    print("\nScenario 1: Complete pipeline with all critical inputs")
    result = evaluator.validate_chain_sequence(
        method_sequence=[
            "phase1_document_ingestion",
            "phase2_structural_parsing",
            "phase3_semantic_analysis",
            "phase4_dimension_scoring_d1",
            "phase5_cross_dimension_analysis",
            "phase6_causal_inference",
            "phase7_report_generation",
        ],
        initial_inputs={
            "policy_document_path",
            "municipality_id",
            "ontology",
            "language_model",
            "questionnaire",
            "interaction_weights",
            "causal_model",
        },
        method_outputs={
            "phase1_document_ingestion": {"raw_document"},
            "phase2_structural_parsing": {"structured_document"},
            "phase3_semantic_analysis": {"semantic_features"},
            "phase4_dimension_scoring_d1": {"dimension_scores"},
            "phase5_cross_dimension_analysis": {"dimensional_analysis"},
            "phase6_causal_inference": {"analysis_results"},
            "phase7_report_generation": {"report"},
        },
    )

    print(f"\n  Overall Chain Quality: {result['chain_quality']}")
    print(f"  Weakest Link: {result['weakest_link']}")
    print("\n  Phase-by-Phase Analysis:")
    for method_id, score in result["method_scores"].items():
        phase_name = method_id.replace("_", " ").title()
        status = "✓" if score == 1.0 else "⚠" if score >= 0.8 else "✗"
        print(f"    {status} {phase_name}: {score}")


def example_parallel_chains() -> None:
    """Example: Multiple parallel chains (e.g., D1-D6 analysis)."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Parallel Dimension Chains")
    print("=" * 80)

    base_signature = {
        "required_inputs": ["document", "dimension_questions"],
        "optional_inputs": ["weights", "model"],
        "critical_optional": ["weights"],
        "output_type": "dict",
    }

    signatures = {
        f"analyze_dimension_d{i}": base_signature.copy() for i in range(1, 7)
    }

    evaluator = ChainLayerEvaluator(signatures)

    print("\nScenario: Parallel execution of D1-D6 chains")
    dimension_chains = [f"analyze_dimension_d{i}" for i in range(1, 7)]

    initial_inputs = {"document", "dimension_questions", "weights", "model"}

    results = []
    for dimension in dimension_chains:
        result = evaluator.evaluate(dimension, initial_inputs)
        results.append((dimension, result["score"]))

    print("\n  Dimension Analysis Scores:")
    for dimension, score in results:
        dim_num = dimension.split("_")[-1].upper()
        status = "✓" if score == 1.0 else "⚠" if score >= 0.8 else "✗"
        print(f"    {status} {dim_num}: {score}")

    avg_quality = sum(s for _, s in results) / len(results)
    min_quality = min(s for _, s in results)
    print(f"\n  Average Quality: {avg_quality:.2f}")
    print(f"  Minimum Quality (Weakest): {min_quality:.2f}")


def example_conditional_chains() -> None:
    """Example: Chains with conditional branches."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Conditional Chain Branches")
    print("=" * 80)

    signatures = {
        "classify_document": {
            "required_inputs": ["document"],
            "optional_inputs": ["classifier"],
            "critical_optional": [],
            "output_type": "str",
        },
        "process_type_a": {
            "required_inputs": ["document", "type_a_config"],
            "optional_inputs": [],
            "critical_optional": [],
            "output_type": "dict",
        },
        "process_type_b": {
            "required_inputs": ["document", "type_b_config"],
            "optional_inputs": [],
            "critical_optional": [],
            "output_type": "dict",
        },
        "merge_results": {
            "required_inputs": ["processed_data"],
            "optional_inputs": [],
            "critical_optional": [],
            "output_type": "dict",
        },
    }

    evaluator = ChainLayerEvaluator(signatures)

    print("\nBranch A: Document classified as Type A")
    result_a = evaluator.validate_chain_sequence(
        method_sequence=["classify_document", "process_type_a", "merge_results"],
        initial_inputs={"document", "type_a_config"},
        method_outputs={
            "classify_document": {"document_type"},
            "process_type_a": {"processed_data"},
            "merge_results": {"final_result"},
        },
    )
    print(f"  Chain Quality: {result_a['chain_quality']}")

    print("\nBranch B: Document classified as Type B")
    result_b = evaluator.validate_chain_sequence(
        method_sequence=["classify_document", "process_type_b", "merge_results"],
        initial_inputs={"document", "type_b_config"},
        method_outputs={
            "classify_document": {"document_type"},
            "process_type_b": {"processed_data"},
            "merge_results": {"final_result"},
        },
    )
    print(f"  Chain Quality: {result_b['chain_quality']}")


def example_error_handling() -> None:
    """Example: Handling missing signatures and invalid data."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Error Handling")
    print("=" * 80)

    signatures = {
        "valid_method": {
            "required_inputs": ["input"],
            "optional_inputs": [],
            "critical_optional": [],
            "output_type": "dict",
        }
    }

    evaluator = ChainLayerEvaluator(signatures)

    print("\n1. Unknown method (not in registry):")
    result = evaluator.evaluate("unknown_method", {"input"})
    print(f"   Score: {result['score']}")
    print(f"   Reason: {result['reason']}")
    print(f"   Warnings: {result['warnings']}")

    print("\n2. Chain with missing method:")
    result = evaluator.validate_chain_sequence(
        method_sequence=["valid_method", "unknown_method"],
        initial_inputs={"input"},
        method_outputs={"valid_method": {"output"}},
    )
    print(f"   Chain Quality: {result['chain_quality']}")
    print(f"   Weakest Link: {result['weakest_link']}")


def example_optimization_patterns() -> None:
    """Example: Optimization patterns for large chains."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Optimization Patterns")
    print("=" * 80)

    signatures = {
        f"step_{i:02d}": {
            "required_inputs": ["input"],
            "optional_inputs": ["config"],
            "critical_optional": [],
            "output_type": "dict",
        }
        for i in range(1, 21)
    }

    evaluator = ChainLayerEvaluator(signatures)

    print("\nLarge chain (20 methods):")
    method_sequence = [f"step_{i:02d}" for i in range(1, 21)]

    result = evaluator.validate_chain_sequence(
        method_sequence=method_sequence,
        initial_inputs={"input", "config"},
        method_outputs={method: {f"output_{method}"} for method in method_sequence},
    )

    print(f"  Chain Quality: {result['chain_quality']}")
    print(f"  Total Methods: {len(result['method_scores'])}")
    print(f"  Average Score: {sum(result['method_scores'].values()) / len(result['method_scores']):.2f}")
    print(f"  Weakest Link: {result['weakest_link']}")

    perfect_methods = sum(1 for s in result["method_scores"].values() if s == 1.0)
    print(f"  Perfect Methods: {perfect_methods}/{len(result['method_scores'])}")


def main() -> None:
    """Run all advanced examples."""
    example_farfan_pipeline()
    example_parallel_chains()
    example_conditional_chains()
    example_error_handling()
    example_optimization_patterns()
    print("\n" + "=" * 80)
    print("All advanced examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
