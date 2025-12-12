"""
Chain Layer Evaluator - Integration Example

Demonstrates integration with existing F.A.R.F.A.N infrastructure:
- MethodSignatureValidator integration
- Method registry integration
- Real method signature loading
- Production-ready validation patterns
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


def example_mock_signatures() -> None:
    """Example: Using mock signatures for testing."""
    print("=" * 80)
    print("EXAMPLE 1: Mock Signatures for Testing")
    print("=" * 80)

    mock_signatures = {
        "PolicyTextProcessor.extract_text": {
            "required_inputs": ["document"],
            "optional_inputs": ["config", "metadata"],
            "critical_optional": ["config"],
            "input_types": {"document": "str"},
            "output_type": "dict",
        },
        "SemanticAnalyzer.analyze_semantics": {
            "required_inputs": ["text", "ontology"],
            "optional_inputs": ["language_model", "threshold"],
            "critical_optional": ["language_model"],
            "input_types": {"text": "str", "ontology": "dict"},
            "output_type": "dict",
        },
        "DimensionScorer.compute_d1_score": {
            "required_inputs": ["semantic_features", "questions"],
            "optional_inputs": ["weights"],
            "critical_optional": [],
            "input_types": {"semantic_features": "dict", "questions": "list"},
            "output_type": "float",
        },
    }

    evaluator = ChainLayerEvaluator(mock_signatures)

    result = evaluator.validate_chain_sequence(
        method_sequence=[
            "PolicyTextProcessor.extract_text",
            "SemanticAnalyzer.analyze_semantics",
            "DimensionScorer.compute_d1_score",
        ],
        initial_inputs={"document", "ontology", "language_model", "questions"},
        method_outputs={
            "PolicyTextProcessor.extract_text": {"text"},
            "SemanticAnalyzer.analyze_semantics": {"semantic_features"},
            "DimensionScorer.compute_d1_score": {"score"},
        },
    )

    print(f"\nChain Quality: {result['chain_quality']}")
    print(f"Weakest Link: {result['weakest_link']}")
    print("\nMethod Scores:")
    for method_id, score in result["method_scores"].items():
        print(f"  {method_id}: {score}")


def example_json_signatures() -> None:
    """Example: Loading signatures from JSON file."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Loading Signatures from JSON")
    print("=" * 80)

    sample_json = {
        "signatures_version": "1.0.0",
        "methods": {
            "ingest_method": {
                "signature": {
                    "required_inputs": ["source"],
                    "optional_inputs": ["filters"],
                    "critical_optional": [],
                    "output_type": "dict",
                }
            },
            "process_method": {
                "signature": {
                    "required_inputs": ["data"],
                    "optional_inputs": ["config"],
                    "critical_optional": ["config"],
                    "output_type": "dict",
                }
            },
        },
    }

    signatures = {
        method_id: method_data["signature"]
        for method_id, method_data in sample_json["methods"].items()
    }

    evaluator = ChainLayerEvaluator(signatures)

    result = evaluator.evaluate("process_method", {"data"})
    print("\nEvaluation Result:")
    print(f"  Score: {result['score']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Missing Critical: {result['missing_critical']}")


def example_executor_chain() -> None:
    """Example: Validating executor chain (D1_Q1 → D2_Q3 → etc.)."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Executor Chain Validation")
    print("=" * 80)

    executor_signatures = {
        "D1_Q1_Resource_Allocation_Executor": {
            "required_inputs": ["policy_document", "municipality_data", "questionnaire"],
            "optional_inputs": ["weights", "thresholds"],
            "critical_optional": ["weights"],
            "input_types": {
                "policy_document": "dict",
                "municipality_data": "dict",
                "questionnaire": "dict",
            },
            "output_type": "dict",
        },
        "D2_Q3_Governance_Structure_Executor": {
            "required_inputs": ["policy_document", "municipality_data", "questionnaire"],
            "optional_inputs": ["weights", "historical_data"],
            "critical_optional": ["weights"],
            "input_types": {
                "policy_document": "dict",
                "municipality_data": "dict",
                "questionnaire": "dict",
            },
            "output_type": "dict",
        },
        "aggregator": {
            "required_inputs": ["d1_results", "d2_results"],
            "optional_inputs": ["fusion_weights"],
            "critical_optional": ["fusion_weights"],
            "input_types": {"d1_results": "dict", "d2_results": "dict"},
            "output_type": "dict",
        },
    }

    evaluator = ChainLayerEvaluator(executor_signatures)

    result = evaluator.validate_chain_sequence(
        method_sequence=[
            "D1_Q1_Resource_Allocation_Executor",
            "D2_Q3_Governance_Structure_Executor",
            "aggregator",
        ],
        initial_inputs={
            "policy_document",
            "municipality_data",
            "questionnaire",
            "weights",
            "fusion_weights",
        },
        method_outputs={
            "D1_Q1_Resource_Allocation_Executor": {"d1_results"},
            "D2_Q3_Governance_Structure_Executor": {"d2_results"},
            "aggregator": {"final_analysis"},
        },
    )

    print(f"\nExecutor Chain Quality: {result['chain_quality']}")
    print("\nExecutor Scores:")
    for method_id, score in result["method_scores"].items():
        executor_name = method_id.split("_Executor")[0]
        print(f"  {executor_name}: {score}")

    if result["chain_quality"] < 1.0:
        print(f"\nWeakest Link: {result['weakest_link']}")
        weakest_result = result["individual_results"][result["weakest_link"]]
        print(f"Reason: {weakest_result['reason']}")


def example_validation_report() -> None:
    """Example: Generating validation report for chain."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Chain Validation Report")
    print("=" * 80)

    signatures = {
        "step_1": {
            "required_inputs": ["input"],
            "optional_inputs": ["opt1", "opt2"],
            "critical_optional": ["opt1"],
            "output_type": "dict",
        },
        "step_2": {
            "required_inputs": ["data"],
            "optional_inputs": ["config"],
            "critical_optional": ["config"],
            "output_type": "dict",
        },
        "step_3": {
            "required_inputs": ["processed"],
            "optional_inputs": [],
            "critical_optional": [],
            "output_type": "dict",
        },
    }

    evaluator = ChainLayerEvaluator(signatures)

    result = evaluator.validate_chain_sequence(
        method_sequence=["step_1", "step_2", "step_3"],
        initial_inputs={"input", "data", "processed"},
        method_outputs={
            "step_1": {"out1"},
            "step_2": {"out2"},
            "step_3": {"out3"},
        },
    )

    print("\n" + "=" * 60)
    print("CHAIN VALIDATION REPORT")
    print("=" * 60)
    print(f"\nOverall Chain Quality: {result['chain_quality']:.2f}")
    print(f"Total Methods: {len(result['method_scores'])}")
    print(f"Weakest Link: {result['weakest_link']}")

    print("\n" + "-" * 60)
    print("Method-by-Method Analysis:")
    print("-" * 60)

    for method_id in ["step_1", "step_2", "step_3"]:
        score = result["method_scores"][method_id]
        details = result["individual_results"][method_id]

        status = "✓ PASS" if score >= 0.8 else "⚠ WARN" if score >= 0.6 else "✗ FAIL"
        print(f"\n{method_id}: {score:.2f} {status}")
        print(f"  Reason: {details['reason']}")

        if details["missing_required"]:
            print(f"  Missing Required: {details['missing_required']}")
        if details["missing_critical"]:
            print(f"  Missing Critical: {details['missing_critical']}")
        if details["missing_optional"]:
            print(f"  Missing Optional: {details['missing_optional']}")
        if details["warnings"]:
            print(f"  Warnings: {details['warnings']}")
        if details["schema_violations"]:
            print(f"  Schema Violations: {details['schema_violations']}")

    print("\n" + "=" * 60)
    print("END REPORT")
    print("=" * 60)


def example_dynamic_chain_building() -> None:
    """Example: Dynamically building and validating chains."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Dynamic Chain Building")
    print("=" * 80)

    signatures = {
        "load": {"required_inputs": ["path"], "optional_inputs": [], "critical_optional": [], "output_type": "dict"},
        "clean": {"required_inputs": ["raw"], "optional_inputs": ["rules"], "critical_optional": [], "output_type": "dict"},
        "normalize": {"required_inputs": ["cleaned"], "optional_inputs": [], "critical_optional": [], "output_type": "dict"},
        "validate": {"required_inputs": ["normalized"], "optional_inputs": ["schema"], "critical_optional": ["schema"], "output_type": "bool"},
        "save": {"required_inputs": ["data"], "optional_inputs": ["format"], "critical_optional": [], "output_type": "bool"},
    }

    evaluator = ChainLayerEvaluator(signatures)

    available_inputs = {"path", "schema"}
    chain = []
    outputs_map = {}

    steps = [
        ("load", {"raw"}),
        ("clean", {"cleaned"}),
        ("normalize", {"normalized"}),
        ("validate", {"validated"}),
        ("save", {"saved"}),
    ]

    print("\nBuilding chain dynamically:")
    for method, outputs in steps:
        print(f"  Adding: {method}")
        chain.append(method)
        outputs_map[method] = outputs

        result = evaluator.validate_chain_sequence(
            method_sequence=chain,
            initial_inputs=available_inputs,
            method_outputs=outputs_map,
        )

        if result["chain_quality"] < 0.8:
            print(f"    ⚠ Quality dropped to {result['chain_quality']}")
            print(f"    Weakest: {result['weakest_link']}")

        available_inputs.update(outputs)

    print(f"\nFinal Chain Quality: {result['chain_quality']}")


def main() -> None:
    """Run all integration examples."""
    example_mock_signatures()
    example_json_signatures()
    example_executor_chain()
    example_validation_report()
    example_dynamic_chain_building()
    print("\n" + "=" * 80)
    print("All integration examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
