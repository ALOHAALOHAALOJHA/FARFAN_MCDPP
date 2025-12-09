"""
Example 3: Incompatible Ensemble - Zero Congruence

This example demonstrates an ensemble with no congruence:
- Incompatible output ranges (not convertible)
- No semantic overlap
- No fusion rule declared

Result: C_play = 0.0 × 0.0 × 0.0 = 0.0
"""

import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src")); from farfan_pipeline.core.calibration.congruence_layer import CongruenceLayerEvaluator


def main() -> None:
    print("=" * 80)
    print("Example 3: Incompatible Ensemble - Zero Congruence")
    print("=" * 80)
    print()
    
    method_registry = {
        "probability_estimator": {
            "output_range": [0.0, 1.0],
            "semantic_tags": {"bayesian", "probability", "confidence"},
            "description": "Estimates probability scores"
        },
        "count_extractor": {
            "output_range": [0.0, 10000.0],
            "semantic_tags": {"extraction", "counting", "frequency"},
            "description": "Extracts raw counts from text"
        },
    }
    
    evaluator = CongruenceLayerEvaluator(method_registry)
    
    print("Method Ensemble: Q099 (INVALID)")
    print("-" * 80)
    print("Methods: probability_estimator, count_extractor")
    print()
    
    print("Step 1: Compute c_scale (Scale Congruence)")
    print("-" * 40)
    print(f"  probability_estimator: {method_registry['probability_estimator']['output_range']}")
    print(f"  count_extractor: {method_registry['count_extractor']['output_range']}")
    print("  Analysis: Ranges are INCOMPATIBLE")
    print("  - [0, 1] is probability/normalized")
    print("  - [0, 10000] is raw count")
    print("  Cannot be directly combined without transformation")
    c_scale = evaluator._compute_c_scale(["probability_estimator", "count_extractor"])
    print(f"  → c_scale = {c_scale} (INCOMPATIBLE)")
    print()
    
    print("Step 2: Compute c_sem (Semantic Congruence)")
    print("-" * 40)
    tags_a = method_registry['probability_estimator']['semantic_tags']
    tags_b = method_registry['count_extractor']['semantic_tags']
    print(f"  probability_estimator: {tags_a}")
    print(f"  count_extractor: {tags_b}")
    intersection = tags_a & tags_b
    union = tags_a | tags_b
    print(f"  Intersection: {intersection}")
    print(f"  Union: {union}")
    print("  Analysis: NO OVERLAP in semantic domains")
    c_sem = evaluator._compute_c_sem(["probability_estimator", "count_extractor"])
    print(f"  → c_sem = {c_sem}")
    print()
    
    print("Step 3: Compute c_fusion (Fusion Validity)")
    print("-" * 40)
    fusion_rule = None
    provided_inputs = {"probability_estimator", "count_extractor"}
    required = ["probability_estimator", "count_extractor"]
    print(f"  Fusion rule: {fusion_rule}")
    print(f"  Required inputs: {required}")
    print(f"  Provided inputs: {provided_inputs}")
    print("  Analysis: NO FUSION RULE declared in Config")
    c_fusion = evaluator._compute_c_fusion(
        fusion_rule=fusion_rule,
        provided_inputs=provided_inputs,
        required_method_ids=required
    )
    print(f"  → c_fusion = {c_fusion}")
    print()
    
    print("Step 4: Compute C_play (Final Score)")
    print("-" * 40)
    c_play = evaluator.evaluate(
        method_ids=["probability_estimator", "count_extractor"],
        subgraph_id="Q099",
        fusion_rule=fusion_rule,
        provided_inputs=provided_inputs
    )
    print(f"  C_play = c_scale × c_sem × c_fusion")
    print(f"  C_play = {c_scale} × {c_sem} × {c_fusion}")
    print(f"  → C_play = {c_play}")
    print()
    
    print("=" * 80)
    print("Result: ZERO CONGRUENCE - INVALID ENSEMBLE")
    print("=" * 80)
    print()
    print("Interpretation:")
    print("  This ensemble is INVALID for the following reasons:")
    print()
    print("  1. Scale Incompatibility (c_scale = 0.0):")
    print("     - Cannot directly combine probability [0,1] with count [0,10000]")
    print("     - Would need explicit normalization/transformation")
    print()
    print("  2. Semantic Mismatch (c_sem = 0.0):")
    print("     - Methods address completely different domains")
    print("     - No conceptual overlap to enable meaningful fusion")
    print()
    print("  3. Missing Fusion Rule (c_fusion = 0.0):")
    print("     - No declared strategy for combining outputs")
    print("     - System cannot proceed without explicit fusion specification")
    print()
    print("  Recommendation: DO NOT USE THIS ENSEMBLE")
    print("  The C_play = 0.0 score signals that this configuration violates")
    print("  fundamental congruence requirements of the SAAAAAA system.")
    print()


if __name__ == "__main__":
    main()
