"""
Example 5: Three-Method Ensemble - Complex Scenario

This example demonstrates a realistic three-method ensemble with:
- Mixed output ranges (some identical, some convertible)
- Partial semantic overlap across all methods
- Valid fusion rule with all inputs present

Result: Computed step-by-step with detailed trace
"""

import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src")); from farfan_pipeline.core.calibration.congruence_layer import CongruenceLayerEvaluator


def main() -> None:
    print("=" * 80)
    print("Example 5: Three-Method Ensemble - Realistic Scenario")
    print("=" * 80)
    print()
    
    method_registry = {
        "structural_validator": {
            "output_range": [0.0, 1.0],
            "semantic_tags": {"validation", "structural", "document"},
            "description": "Validates document structure"
        },
        "content_analyzer": {
            "output_range": [0.0, 1.0],
            "semantic_tags": {"analysis", "content", "document"},
            "description": "Analyzes content quality"
        },
        "completeness_checker": {
            "output_range": [0.0, 0.95],
            "semantic_tags": {"validation", "completeness"},
            "description": "Checks document completeness"
        },
    }
    
    evaluator = CongruenceLayerEvaluator(method_registry)
    
    methods = ["structural_validator", "content_analyzer", "completeness_checker"]
    
    print("Method Ensemble: D3_Q5 (Comprehensive Document Analysis)")
    print("-" * 80)
    print(f"Methods: {', '.join(methods)}")
    print()
    
    for method_id in methods:
        info = method_registry[method_id]
        print(f"  {method_id}:")
        print(f"    Range: {info['output_range']}")
        print(f"    Tags: {info['semantic_tags']}")
        print(f"    Desc: {info['description']}")
    print()
    
    print("=" * 80)
    print("COMPUTATION TRACE")
    print("=" * 80)
    print()
    
    print("Step 1: Compute c_scale (Scale Congruence)")
    print("-" * 80)
    print("Comparing output ranges:")
    for method_id in methods:
        print(f"  {method_id}: {method_registry[method_id]['output_range']}")
    print()
    
    print("Analysis:")
    print("  • structural_validator: [0.0, 1.0]")
    print("  • content_analyzer: [0.0, 1.0]")
    print("  • completeness_checker: [0.0, 0.95]")
    print()
    print("  First two are identical, third is different")
    print("  BUT all ranges fall within [0, 1] → convertible")
    print()
    
    c_scale = evaluator._compute_c_scale(methods)
    print(f"  → c_scale = {c_scale}")
    print("    (0.8 because ranges are convertible but not all identical)")
    print()
    
    print("Step 2: Compute c_sem (Semantic Congruence)")
    print("-" * 80)
    
    tags_1 = method_registry['structural_validator']['semantic_tags']
    tags_2 = method_registry['content_analyzer']['semantic_tags']
    tags_3 = method_registry['completeness_checker']['semantic_tags']
    
    print("Semantic tags by method:")
    print(f"  structural_validator: {tags_1}")
    print(f"  content_analyzer: {tags_2}")
    print(f"  completeness_checker: {tags_3}")
    print()
    
    intersection = tags_1 & tags_2 & tags_3
    union = tags_1 | tags_2 | tags_3
    
    print("Set operations:")
    print(f"  Intersection (∩): {intersection}")
    print(f"  Union (∪): {union}")
    print()
    print(f"  Jaccard index = |intersection| / |union|")
    print(f"                = {len(intersection)} / {len(union)}")
    print(f"                = {len(intersection) / len(union):.3f}")
    print()
    
    c_sem = evaluator._compute_c_sem(methods)
    print(f"  → c_sem = {c_sem:.3f}")
    print()
    
    print("Step 3: Compute c_fusion (Fusion Validity)")
    print("-" * 80)
    
    fusion_rule = "weighted_average_3way"
    provided_inputs = {
        "structural_validator",
        "content_analyzer", 
        "completeness_checker"
    }
    
    print(f"Fusion configuration:")
    print(f"  Rule: {fusion_rule}")
    print(f"  Required methods: {methods}")
    print(f"  Provided inputs: {provided_inputs}")
    print()
    
    print("Analysis:")
    print("  ✓ Fusion rule is declared in Config")
    print("  ✓ All required method outputs are available")
    print()
    
    c_fusion = evaluator._compute_c_fusion(
        fusion_rule=fusion_rule,
        provided_inputs=provided_inputs,
        required_method_ids=methods
    )
    
    print(f"  → c_fusion = {c_fusion}")
    print("    (1.0 because rule exists and all inputs present)")
    print()
    
    print("Step 4: Compute C_play (Final Congruence Score)")
    print("-" * 80)
    
    c_play = evaluator.evaluate(
        method_ids=methods,
        subgraph_id="D3_Q5",
        fusion_rule=fusion_rule,
        provided_inputs=provided_inputs
    )
    
    print("Formula: C_play = c_scale × c_sem × c_fusion")
    print()
    print(f"  C_play = {c_scale} × {c_sem:.3f} × {c_fusion}")
    print(f"  C_play = {c_play:.3f}")
    print()
    
    print("=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print()
    print(f"C_play = {c_play:.3f}")
    print()
    
    print("Breakdown:")
    print(f"  • Scale congruence (c_scale):    {c_scale:.3f}")
    print(f"  • Semantic congruence (c_sem):   {c_sem:.3f}")
    print(f"  • Fusion validity (c_fusion):    {c_fusion:.3f}")
    print()
    
    print("Interpretation:")
    print("-" * 80)
    print()
    print("This ensemble has GOOD but not PERFECT congruence:")
    print()
    
    if c_scale < 1.0:
        print(f"  Scale ({c_scale}):")
        print("    • Some output ranges differ but are convertible")
        print("    • Minor normalization may be needed")
        print()
    
    if c_sem < 1.0:
        print(f"  Semantic ({c_sem:.3f}):")
        print("    • Limited semantic overlap across all three methods")
        print(f"    • Only '{intersection}' tags are common to all")
        print("    • Methods address related but distinct aspects")
        print()
    
    if c_fusion == 1.0:
        print(f"  Fusion ({c_fusion}):")
        print("    • Perfect - all requirements met")
        print("    • Valid fusion rule and complete inputs")
        print()
    
    overall_quality = "GOOD" if c_play >= 0.5 else "POOR"
    print(f"Overall Assessment: {overall_quality}")
    print()
    
    if c_play >= 0.5:
        print("This ensemble can be used effectively, though consider:")
        print("  1. Standardizing output ranges to [0,1]")
        print("  2. Ensuring semantic tags capture common ground")
        print("  3. Monitoring fusion performance in practice")
    else:
        print("This ensemble may have coordination issues:")
        print("  1. Review method selection for better semantic alignment")
        print("  2. Consider whether all methods are necessary")
        print("  3. Verify fusion rule is appropriate for these methods")
    print()


if __name__ == "__main__":
    main()
