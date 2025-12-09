"""
Chain Layer Evaluator - Basic Usage Examples

Demonstrates basic usage of ChainLayerEvaluator for method chain validation.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from COHORT_2024_chain_layer import ChainLayerEvaluator


def example_basic_evaluation() -> None:
    """Example: Basic single method evaluation."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Method Evaluation")
    print("=" * 80)

    signatures = {
        "analyze_document": {
            "required_inputs": ["document", "config"],
            "optional_inputs": ["metadata", "cache"],
            "critical_optional": ["metadata"],
            "input_types": {"document": "str", "config": "dict"},
            "output_type": "dict",
        }
    }

    evaluator = ChainLayerEvaluator(signatures)

    print("\n1. Perfect score (all inputs present):")
    result = evaluator.evaluate(
        "analyze_document",
        provided_inputs={"document", "config", "metadata", "cache"},
    )
    print(f"   Score: {result['score']}")
    print(f"   Reason: {result['reason']}")

    print("\n2. Missing critical optional (score 0.3):")
    result = evaluator.evaluate(
        "analyze_document",
        provided_inputs={"document", "config"},
    )
    print(f"   Score: {result['score']}")
    print(f"   Reason: {result['reason']}")
    print(f"   Missing critical: {result['missing_critical']}")

    print("\n3. Missing required input (score 0.0):")
    result = evaluator.evaluate(
        "analyze_document",
        provided_inputs={"document"},
    )
    print(f"   Score: {result['score']}")
    print(f"   Reason: {result['reason']}")
    print(f"   Missing required: {result['missing_required']}")


def example_type_checking() -> None:
    """Example: Type checking with upstream outputs."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Type Checking")
    print("=" * 80)

    signatures = {
        "process_data": {
            "required_inputs": ["data", "threshold"],
            "optional_inputs": [],
            "critical_optional": [],
            "input_types": {"data": "list", "threshold": "float"},
            "output_type": "list",
        }
    }

    evaluator = ChainLayerEvaluator(signatures)

    print("\n1. Correct types (score 1.0):")
    result = evaluator.evaluate(
        "process_data",
        provided_inputs={"data", "threshold"},
        upstream_outputs={"data": "list", "threshold": "float"},
    )
    print(f"   Score: {result['score']}")
    print(f"   Warnings: {result['warnings']}")

    print("\n2. Soft type mismatch (score 0.8):")
    result = evaluator.evaluate(
        "process_data",
        provided_inputs={"data", "threshold"},
        upstream_outputs={"data": "tuple", "threshold": "int"},
    )
    print(f"   Score: {result['score']}")
    print(f"   Warnings: {result['warnings']}")

    print("\n3. Hard type mismatch (score 0.0):")
    result = evaluator.evaluate(
        "process_data",
        provided_inputs={"data", "threshold"},
        upstream_outputs={"data": "str", "threshold": "float"},
    )
    print(f"   Score: {result['score']}")
    print(f"   Schema violations: {result['schema_violations']}")


def example_discrete_scores() -> None:
    """Example: All discrete score levels."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Discrete Score Levels")
    print("=" * 80)

    signatures = {
        "method": {
            "required_inputs": ["required1", "required2"],
            "optional_inputs": ["opt1", "opt2", "opt3", "opt4"],
            "critical_optional": ["opt1"],
            "input_types": {"required1": "str", "required2": "int"},
            "output_type": "dict",
        }
    }

    evaluator = ChainLayerEvaluator(signatures)

    scenarios = [
        (
            "Score 1.0: All inputs present",
            {"required1", "required2", "opt1", "opt2", "opt3", "opt4"},
            None,
        ),
        (
            "Score 0.8: All contracts pass with soft warning",
            {"required1", "required2", "opt1", "opt2"},
            {"required1": "int", "required2": "int"},
        ),
        (
            "Score 0.6: Many optional missing (>50%)",
            {"required1", "required2", "opt1"},
            None,
        ),
        (
            "Score 0.3: Critical optional missing",
            {"required1", "required2"},
            None,
        ),
        (
            "Score 0.0: Required input missing",
            {"required1"},
            None,
        ),
    ]

    for description, provided, upstream in scenarios:
        result = evaluator.evaluate("method", provided, upstream)
        print(f"\n{description}:")
        print(f"   Score: {result['score']}")
        print(f"   Reason: {result['reason']}")


def main() -> None:
    """Run all examples."""
    example_basic_evaluation()
    example_type_checking()
    example_discrete_scores()
    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
