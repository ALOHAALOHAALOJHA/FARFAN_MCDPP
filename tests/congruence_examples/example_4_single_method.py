"""
Example 4: Single Method - Edge Case

This example demonstrates the single method edge case where
C_play always returns 1.0 regardless of other factors.

Result: C_play = 1.0 (by definition)
"""

import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src")); from farfan_pipeline.core.calibration.congruence_layer import CongruenceLayerEvaluator


def main() -> None:
    print("=" * 80)
    print("Example 4: Single Method Edge Case")
    print("=" * 80)
    print()
    
    method_registry = {
        "standalone_analyzer": {
            "output_range": [0.0, 100.0],
            "semantic_tags": {"analysis"},
            "description": "Standalone analysis method"
        },
    }
    
    evaluator = CongruenceLayerEvaluator(method_registry)
    
    print("Method Ensemble: Q123 (Single Method)")
    print("-" * 80)
    print("Methods: standalone_analyzer")
    print()
    
    print("Analysis:")
    print("-" * 40)
    print("  Single method ensembles have C_play = 1.0 by definition")
    print("  Rationale:")
    print("    - No inter-method conflicts possible")
    print("    - No fusion needed")
    print("    - Scale/semantic congruence not applicable")
    print()
    
    c_play = evaluator.evaluate(
        method_ids=["standalone_analyzer"],
        subgraph_id="Q123",
        fusion_rule=None,
        provided_inputs=set()
    )
    
    print(f"  → C_play = {c_play}")
    print()
    
    print("=" * 80)
    print("Result: AUTOMATIC CONGRUENCE")
    print("=" * 80)
    print()
    print("Interpretation:")
    print("  Single methods always have perfect congruence (1.0) because:")
    print("  - There are no other methods to conflict with")
    print("  - No fusion/aggregation is needed")
    print("  - All congruence components are trivially satisfied")
    print()
    print("  This is the simplest valid ensemble configuration.")
    print()
    
    print("Testing with extreme values:")
    print("-" * 40)
    
    method_registry_extreme = {
        "extreme_method": {
            "output_range": [-1000.0, 1000.0],
            "semantic_tags": [],
        },
    }
    evaluator_extreme = CongruenceLayerEvaluator(method_registry_extreme)
    
    c_play_extreme = evaluator_extreme.evaluate(
        method_ids=["extreme_method"],
        subgraph_id="Q999",
        fusion_rule=None,
        provided_inputs=set()
    )
    
    print(f"  Even with extreme range [-1000, 1000]: C_play = {c_play_extreme}")
    print(f"  Even with empty semantic tags: C_play = {c_play_extreme}")
    print(f"  Even with no fusion rule: C_play = {c_play_extreme}")
    print()


if __name__ == "__main__":
    main()
