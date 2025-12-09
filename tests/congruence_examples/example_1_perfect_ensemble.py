"""
Example 1: Perfect Ensemble - All Components Score 1.0

This example demonstrates a perfect ensemble where two methods have:
- Identical output ranges [0, 1]
- Complete semantic overlap
- Valid fusion rule with all inputs present

Result: C_play = 1.0 × 1.0 × 1.0 = 1.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from farfan_pipeline.core.calibration.congruence_layer import CongruenceLayerEvaluator


def main() -> None:
    print("=" * 80)
    print("Example 1: Perfect Ensemble (Specification Section 3.5.1)")
    print("=" * 80)
    print()
    
    method_registry = {
        "v_analyzer": {
            "output_range": [0.0, 1.0],
            "semantic_tags": {"coherence", "textual_quality"},
            "description": "Analyzes document coherence"
        },
        "v_validator": {
            "output_range": [0.0, 1.0],
            "semantic_tags": {"coherence", "textual_quality"},
            "description": "Validates textual quality"
        },
    }
    
    evaluator = CongruenceLayerEvaluator(method_registry)
    
    print("Method Ensemble: Q001")
    print("-" * 80)
    print("Methods: v_analyzer, v_validator")
    print()
    
    print("Step 1: Compute c_scale (Scale Congruence)")
    print("-" * 40)
    print(f"  v_analyzer output_range: {method_registry['v_analyzer']['output_range']}")
    print(f"  v_validator output_range: {method_registry['v_validator']['output_range']}")
    print("  Analysis: Both ranges are [0.0, 1.0] - IDENTICAL")
    c_scale = evaluator._compute_c_scale(["v_analyzer", "v_validator"])
    print(f"  → c_scale = {c_scale}")
    print()
    
    print("Step 2: Compute c_sem (Semantic Congruence)")
    print("-" * 40)
    print(f"  v_analyzer tags: {method_registry['v_analyzer']['semantic_tags']}")
    print(f"  v_validator tags: {method_registry['v_validator']['semantic_tags']}")
    print(f"  Intersection: {method_registry['v_analyzer']['semantic_tags']}")
    print(f"  Union: {method_registry['v_analyzer']['semantic_tags']}")
    print("  Jaccard index = |intersection| / |union| = 2/2 = 1.0")
    c_sem = evaluator._compute_c_sem(["v_analyzer", "v_validator"])
    print(f"  → c_sem = {c_sem}")
    print()
    
    print("Step 3: Compute c_fusion (Fusion Validity)")
    print("-" * 40)
    fusion_rule = "weighted_average"
    provided_inputs = {"v_analyzer", "v_validator"}
    print(f"  Fusion rule: {fusion_rule}")
    print(f"  Required inputs: ['v_analyzer', 'v_validator']")
    print(f"  Provided inputs: {provided_inputs}")
    print("  Analysis: Fusion rule present AND all inputs available")
    c_fusion = evaluator._compute_c_fusion(
        fusion_rule=fusion_rule,
        provided_inputs=provided_inputs,
        required_method_ids=["v_analyzer", "v_validator"]
    )
    print(f"  → c_fusion = {c_fusion}")
    print()
    
    print("Step 4: Compute C_play (Final Score)")
    print("-" * 40)
    c_play = evaluator.evaluate(
        method_ids=["v_analyzer", "v_validator"],
        subgraph_id="Q001",
        fusion_rule=fusion_rule,
        provided_inputs=provided_inputs
    )
    print(f"  C_play = c_scale × c_sem × c_fusion")
    print(f"  C_play = {c_scale} × {c_sem} × {c_fusion}")
    print(f"  → C_play = {c_play}")
    print()
    
    print("=" * 80)
    print("Result: PERFECT CONGRUENCE")
    print("=" * 80)
    print()
    print("Interpretation:")
    print("  This ensemble has perfect congruence across all dimensions:")
    print("  - Scale: Output ranges are identical")
    print("  - Semantic: Complete tag overlap")
    print("  - Fusion: Valid rule with all inputs present")
    print()
    print("  This is the ideal case for method ensembles in the SAAAAAA system.")
    print()


if __name__ == "__main__":
    main()
