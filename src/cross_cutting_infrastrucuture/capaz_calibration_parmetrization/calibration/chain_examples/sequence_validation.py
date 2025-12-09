"""
Chain Layer Evaluator - Sequence Validation Examples

Demonstrates chain sequence validation and weakest link analysis.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from COHORT_2024_chain_layer import ChainLayerEvaluator


def example_simple_chain() -> None:
    """Example: Simple 3-method chain validation."""
    print("=" * 80)
    print("EXAMPLE 1: Simple Chain Validation")
    print("=" * 80)

    signatures = {
        "load_data": {
            "required_inputs": ["file_path"],
            "optional_inputs": ["encoding"],
            "critical_optional": [],
            "output_type": "dict",
        },
        "transform_data": {
            "required_inputs": ["raw_data"],
            "optional_inputs": ["config"],
            "critical_optional": [],
            "output_type": "dict",
        },
        "save_results": {
            "required_inputs": ["processed_data"],
            "optional_inputs": ["output_path", "format"],
            "critical_optional": [],
            "output_type": "bool",
        },
    }

    evaluator = ChainLayerEvaluator(signatures)

    result = evaluator.validate_chain_sequence(
        method_sequence=["load_data", "transform_data", "save_results"],
        initial_inputs={"file_path", "encoding", "config", "output_path"},
        method_outputs={
            "load_data": {"raw_data"},
            "transform_data": {"processed_data"},
            "save_results": {"success"},
        },
    )

    print("\nChain Validation Results:")
    print(f"  Chain Quality: {result['chain_quality']}")
    print(f"  Weakest Link: {result['weakest_link']}")
    print("\nIndividual Method Scores:")
    for method_id, score in result["method_scores"].items():
        print(f"  {method_id}: {score}")
        reason = result["individual_results"][method_id]["reason"]
        print(f"    → {reason}")


def example_broken_chain() -> None:
    """Example: Chain with missing dependencies."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Broken Chain (Missing Dependencies)")
    print("=" * 80)

    signatures = {
        "step_a": {
            "required_inputs": ["input"],
            "optional_inputs": [],
            "critical_optional": [],
            "output_type": "dict",
        },
        "step_b": {
            "required_inputs": ["data_from_a", "external_config"],
            "optional_inputs": [],
            "critical_optional": [],
            "output_type": "dict",
        },
        "step_c": {
            "required_inputs": ["data_from_b"],
            "optional_inputs": [],
            "critical_optional": [],
            "output_type": "dict",
        },
    }

    evaluator = ChainLayerEvaluator(signatures)

    result = evaluator.validate_chain_sequence(
        method_sequence=["step_a", "step_b", "step_c"],
        initial_inputs={"input"},
        method_outputs={
            "step_a": {"data_from_a"},
            "step_b": {"data_from_b"},
            "step_c": {"final_result"},
        },
    )

    print("\nChain Validation Results:")
    print(f"  Chain Quality: {result['chain_quality']}")
    print(f"  Weakest Link: {result['weakest_link']}")
    print("\nIndividual Method Scores:")
    for method_id, score in result["method_scores"].items():
        print(f"  {method_id}: {score}")
        reason = result["individual_results"][method_id]["reason"]
        print(f"    → {reason}")
        if score == 0.0:
            missing = result["individual_results"][method_id]["missing_required"]
            print(f"    → Missing required: {missing}")


def example_complex_pipeline() -> None:
    """Example: Complex multi-stage analysis pipeline."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Complex Analysis Pipeline")
    print("=" * 80)

    signatures = {
        "ingest_documents": {
            "required_inputs": ["source_path"],
            "optional_inputs": ["batch_size", "filters"],
            "critical_optional": ["filters"],
            "output_type": "list",
        },
        "preprocess": {
            "required_inputs": ["documents"],
            "optional_inputs": ["clean_html", "normalize", "remove_stopwords"],
            "critical_optional": ["normalize"],
            "output_type": "list",
        },
        "extract_features": {
            "required_inputs": ["preprocessed_docs"],
            "optional_inputs": ["feature_type", "vectorizer"],
            "critical_optional": ["feature_type"],
            "output_type": "dict",
        },
        "analyze": {
            "required_inputs": ["features"],
            "optional_inputs": ["model", "threshold", "metadata"],
            "critical_optional": ["model"],
            "output_type": "dict",
        },
        "generate_report": {
            "required_inputs": ["analysis_results"],
            "optional_inputs": ["template", "format", "include_charts"],
            "critical_optional": [],
            "output_type": "str",
        },
    }

    evaluator = ChainLayerEvaluator(signatures)

    result = evaluator.validate_chain_sequence(
        method_sequence=[
            "ingest_documents",
            "preprocess",
            "extract_features",
            "analyze",
            "generate_report",
        ],
        initial_inputs={
            "source_path",
            "filters",
            "normalize",
            "feature_type",
            "model",
            "template",
        },
        method_outputs={
            "ingest_documents": {"documents"},
            "preprocess": {"preprocessed_docs"},
            "extract_features": {"features"},
            "analyze": {"analysis_results"},
            "generate_report": {"report"},
        },
    )

    print("\nChain Validation Results:")
    print(f"  Chain Quality: {result['chain_quality']}")
    print(f"  Weakest Link: {result['weakest_link']}")
    print("\nIndividual Method Scores:")
    for method_id, score in result["method_scores"].items():
        short_name = method_id.replace("_", " ").title()
        print(f"  {short_name}: {score}")
        reason = result["individual_results"][method_id]["reason"]
        print(f"    → {reason}")


def example_weakest_link_analysis() -> None:
    """Example: Identifying and fixing weakest link."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Weakest Link Analysis")
    print("=" * 80)

    signatures = {
        "method_a": {
            "required_inputs": ["x"],
            "optional_inputs": ["opt1"],
            "critical_optional": [],
            "output_type": "dict",
        },
        "method_b": {
            "required_inputs": ["y"],
            "optional_inputs": ["opt2", "opt3"],
            "critical_optional": ["opt2"],
            "output_type": "dict",
        },
        "method_c": {
            "required_inputs": ["z"],
            "optional_inputs": [],
            "critical_optional": [],
            "output_type": "dict",
        },
    }

    evaluator = ChainLayerEvaluator(signatures)

    print("\nScenario 1: Initial chain (has weakest link)")
    result1 = evaluator.validate_chain_sequence(
        method_sequence=["method_a", "method_b", "method_c"],
        initial_inputs={"x", "y", "z"},
        method_outputs={
            "method_a": {"out_a"},
            "method_b": {"out_b"},
            "method_c": {"out_c"},
        },
    )

    print(f"  Chain Quality: {result1['chain_quality']}")
    print(f"  Weakest Link: {result1['weakest_link']}")
    for method_id, score in result1["method_scores"].items():
        marker = " ← WEAKEST" if method_id == result1["weakest_link"] else ""
        print(f"    {method_id}: {score}{marker}")

    print("\nScenario 2: After fixing weakest link (providing opt2)")
    result2 = evaluator.validate_chain_sequence(
        method_sequence=["method_a", "method_b", "method_c"],
        initial_inputs={"x", "y", "z", "opt1", "opt2"},
        method_outputs={
            "method_a": {"out_a"},
            "method_b": {"out_b"},
            "method_c": {"out_c"},
        },
    )

    print(f"  Chain Quality: {result2['chain_quality']}")
    print(f"  Weakest Link: {result2['weakest_link']}")
    for method_id, score in result2["method_scores"].items():
        marker = " ← WEAKEST" if method_id == result2["weakest_link"] else ""
        print(f"    {method_id}: {score}{marker}")

    improvement = result2["chain_quality"] - result1["chain_quality"]
    print(f"\n  Quality Improvement: +{improvement:.1f}")


def main() -> None:
    """Run all examples."""
    example_simple_chain()
    example_broken_chain()
    example_complex_pipeline()
    example_weakest_link_analysis()
    print("\n" + "=" * 80)
    print("All sequence validation examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
