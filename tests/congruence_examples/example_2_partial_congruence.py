"""
Example 2: Partial Congruence - Mixed Scores

This example demonstrates an ensemble with partial congruence:
- Different but compatible output ranges (convertible to [0,1])
- Partial semantic overlap
- Valid fusion rule but missing some inputs

Result: C_play = 0.8 × 0.333 × 0.5 = 0.133
"""

import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src")); from farfan_pipeline.core.calibration.congruence_layer import CongruenceLayerEvaluator


def main() -> None:
    print("=" * 80)
    print("Example 2: Partial Congruence")
    print("=" * 80)
    print()
    
    method_registry = {
        "structural_analyzer": {
            "output_range": [0.0, 0.8],
            "semantic_tags": {"quality", "structural", "document_analysis"},
            "description": "Analyzes document structure"
        },
        "numerical_validator": {
            "output_range": [0.2, 1.0],
            "semantic_tags": {"quality", "numerical", "validation"},
            "description": "Validates numerical content"
        },
    }
    
    evaluator = CongruenceLayerEvaluator(method_registry)
    
    print("Method Ensemble: Q042")
    print("-" * 80)
    print("Methods: structural_analyzer, numerical_validator")
    print()
    
    print("Step 1: Compute c_scale (Scale Congruence)")
    print("-" * 40)
    print(f"  structural_analyzer: {method_registry['structural_analyzer']['output_range']}")
    print(f"  numerical_validator: {method_registry['numerical_validator']['output_range']}")
    print("  Analysis: Ranges are DIFFERENT but both within [0,1]")
    print("  Both are convertible to normalized [0,1] scale")
    c_scale = evaluator._compute_c_scale(["structural_analyzer", "numerical_validator"])
    print(f"  → c_scale = {c_scale} (convertible penalty)")
    print()
    
    print("Step 2: Compute c_sem (Semantic Congruence)")
    print("-" * 40)
    tags_a = method_registry['structural_analyzer']['semantic_tags']
    tags_b = method_registry['numerical_validator']['semantic_tags']
    print(f"  structural_analyzer: {tags_a}")
    print(f"  numerical_validator: {tags_b}")
    intersection = tags_a & tags_b
    union = tags_a | tags_b
    print(f"  Intersection: {intersection}")
    print(f"  Union: {union}")
    print(f"  Jaccard = |{intersection}| / |{union}| = {len(intersection)}/{len(union)}")
    c_sem = evaluator._compute_c_sem(["structural_analyzer", "numerical_validator"])
    print(f"  → c_sem = {c_sem:.3f}")
    print()
    
    print("Step 3: Compute c_fusion (Fusion Validity)")
    print("-" * 40)
    fusion_rule = "TYPE_B"
    provided_inputs = {"structural_analyzer"}
    required = ["structural_analyzer", "numerical_validator"]
    print(f"  Fusion rule: {fusion_rule} (present in Config)")
    print(f"  Required inputs: {required}")
    print(f"  Provided inputs: {provided_inputs}")
    print("  Analysis: Valid fusion rule BUT missing 'numerical_validator'")
    c_fusion = evaluator._compute_c_fusion(
        fusion_rule=fusion_rule,
        provided_inputs=provided_inputs,
        required_method_ids=required
    )
    print(f"  → c_fusion = {c_fusion} (partial inputs)")
    print()
    
    print("Step 4: Compute C_play (Final Score)")
    print("-" * 40)
    c_play = evaluator.evaluate(
        method_ids=["structural_analyzer", "numerical_validator"],
        subgraph_id="Q042",
        fusion_rule=fusion_rule,
        provided_inputs=provided_inputs
    )
    print(f"  C_play = c_scale × c_sem × c_fusion")
    print(f"  C_play = {c_scale} × {c_sem:.3f} × {c_fusion}")
    print(f"  → C_play = {c_play:.3f}")
    print()
    
    print("=" * 80)
    print("Result: PARTIAL CONGRUENCE")
    print("=" * 80)
    print()
    print("Interpretation:")
    print("  This ensemble has partial congruence:")
    print(f"  - Scale (0.8): Ranges are compatible but not identical")
    print(f"  - Semantic ({c_sem:.3f}): Only 'quality' tag is shared")
    print(f"  - Fusion (0.5): Valid rule but missing some inputs")
    print()
    print("  Impact: The low C_play score indicates this ensemble may have")
    print("  coordination issues. Consider:")
    print("  1. Ensuring all method outputs available before fusion")
    print("  2. Using methods with more semantic overlap")
    print("  3. Normalizing output ranges to identical scales")
    print()


if __name__ == "__main__":
    main()
