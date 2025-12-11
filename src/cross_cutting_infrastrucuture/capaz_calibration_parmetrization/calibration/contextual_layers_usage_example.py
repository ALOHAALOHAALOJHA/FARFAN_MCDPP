"""
Contextual Layer Evaluators - Usage Examples

COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00

Demonstrates usage of @q, @d, @p layer evaluators with CompatibilityRegistry.
"""

from pathlib import Path
from cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_contextual_layers import (
    CompatibilityRegistry,
    QuestionEvaluator,
    DimensionEvaluator,
    PolicyEvaluator,
    create_contextual_evaluators,
)


def example_1_basic_registry_usage():
    """Example 1: Basic CompatibilityRegistry usage."""
    print("\n=== Example 1: Basic CompatibilityRegistry Usage ===\n")
    
    registry = CompatibilityRegistry()
    
    print(f"Registry loaded. Methods in registry: {len(registry.list_methods())}")
    print(f"Methods: {registry.list_methods()}\n")
    
    method_id = "pattern_extractor_v2"
    
    score_q = registry.evaluate_question(method_id, "Q001")
    print(f"Question Score (Q001): {score_q}")
    
    score_d = registry.evaluate_dimension(method_id, "DIM01")
    print(f"Dimension Score (DIM01): {score_d}")
    
    score_p = registry.evaluate_policy(method_id, "PA01")
    print(f"Policy Score (PA01): {score_p}\n")
    
    unmapped_score = registry.evaluate_question(method_id, "Q999")
    print(f"Unmapped Question (Q999): {unmapped_score} (penalty applied)")


def example_2_using_evaluators():
    """Example 2: Using specialized evaluators."""
    print("\n=== Example 2: Using Specialized Evaluators ===\n")
    
    registry = CompatibilityRegistry()
    
    q_eval = QuestionEvaluator(registry)
    d_eval = DimensionEvaluator(registry)
    p_eval = PolicyEvaluator(registry)
    
    method_id = "coherence_validator"
    
    score_q = q_eval.evaluate(method_id, "Q001")
    score_d = d_eval.evaluate(method_id, "DIM01")
    score_p = p_eval.evaluate(method_id, "PA01")
    
    print(f"Method: {method_id}")
    print(f"  @q (Q001): {score_q}")
    print(f"  @d (DIM01): {score_d}")
    print(f"  @p (PA01): {score_p}")


def example_3_factory_function():
    """Example 3: Using factory function."""
    print("\n=== Example 3: Using Factory Function ===\n")
    
    q_eval, d_eval, p_eval = create_contextual_evaluators()
    
    print("All evaluators created from factory.")
    print(f"Shared registry: {q_eval.registry is d_eval.registry is p_eval.registry}\n")
    
    method_id = "pattern_extractor_v2"
    context = ("Q031", "DIM02", "PA10")
    
    score_q = q_eval.evaluate(method_id, context[0])
    score_d = d_eval.evaluate(method_id, context[1])
    score_p = p_eval.evaluate(method_id, context[2])
    
    print(f"Context: {context}")
    print(f"  @q: {score_q}")
    print(f"  @d: {score_d}")
    print(f"  @p: {score_p}")


def example_4_full_method_compatibility():
    """Example 4: Getting full compatibility mapping."""
    print("\n=== Example 4: Full Method Compatibility ===\n")
    
    registry = CompatibilityRegistry()
    method_id = "pattern_extractor_v2"
    
    compat = registry.get_method_compatibility(method_id)
    
    if compat:
        print(f"Method: {method_id}\n")
        
        print("Question Compatibility:")
        for q_id, score in compat["questions"].items():
            print(f"  {q_id}: {score}")
        
        print("\nDimension Compatibility:")
        for d_id, score in compat["dimensions"].items():
            print(f"  {d_id}: {score}")
        
        print("\nPolicy Compatibility:")
        for p_id, score in compat["policies"].items():
            print(f"  {p_id}: {score}")
    else:
        print(f"Method {method_id} not found in registry")


def example_5_anti_universality_check():
    """Example 5: Anti-Universality validation."""
    print("\n=== Example 5: Anti-Universality Validation ===\n")
    
    registry = CompatibilityRegistry()
    
    methods = registry.list_methods()
    print(f"Validating {len(methods)} methods for anti-universality...\n")
    
    for method_id in methods:
        is_valid, msg = registry.validate_method_universality(method_id)
        
        if not is_valid:
            print(f"❌ {method_id}: {msg}")
        else:
            compat = registry.get_method_compatibility(method_id)
            if compat:
                max_scores = {
                    "questions": max(compat["questions"].values()) if compat["questions"] else 0.0,
                    "dimensions": max(compat["dimensions"].values()) if compat["dimensions"] else 0.0,
                    "policies": max(compat["policies"].values()) if compat["policies"] else 0.0,
                }
                print(f"✓ {method_id}: Max scores = {max_scores}")


def example_6_penalty_demonstration():
    """Example 6: Penalty application demonstration."""
    print("\n=== Example 6: Penalty Application ===\n")
    
    registry = CompatibilityRegistry()
    method_id = "pattern_extractor_v2"
    
    print(f"Method: {method_id}")
    print(f"Penalty value: {CompatibilityRegistry.UNMAPPED_PENALTY}\n")
    
    print("Declared contexts (should return configured scores):")
    print(f"  Q001: {registry.evaluate_question(method_id, 'Q001')}")
    print(f"  DIM01: {registry.evaluate_dimension(method_id, 'DIM01')}")
    print(f"  PA01: {registry.evaluate_policy(method_id, 'PA01')}\n")
    
    print("Unmapped contexts (should return 0.1 penalty):")
    print(f"  Q999: {registry.evaluate_question(method_id, 'Q999')}")
    print(f"  DIM99: {registry.evaluate_dimension(method_id, 'DIM99')}")
    print(f"  PA99: {registry.evaluate_policy(method_id, 'PA99')}\n")
    
    print("Nonexistent method (should return 0.1 penalty):")
    print(f"  unknown_method + Q001: {registry.evaluate_question('unknown_method', 'Q001')}")


def example_7_metadata_inspection():
    """Example 7: Inspecting COHORT metadata."""
    print("\n=== Example 7: COHORT Metadata ===\n")
    
    registry = CompatibilityRegistry()
    metadata = registry.get_metadata()
    
    print("COHORT Metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")


def example_8_integration_with_calibration():
    """Example 8: Integration with 8-layer calibration system."""
    print("\n=== Example 8: Integration with Calibration System ===\n")
    
    q_eval, d_eval, p_eval = create_contextual_evaluators()
    
    method_id = "pattern_extractor_v2"
    context = {
        "question_id": "Q001",
        "dimension_id": "DIM01",
        "policy_id": "PA01"
    }
    
    print(f"Evaluating method: {method_id}")
    print(f"Context: {context}\n")
    
    layer_scores = {
        "@q": q_eval.evaluate(method_id, context["question_id"]),
        "@d": d_eval.evaluate(method_id, context["dimension_id"]),
        "@p": p_eval.evaluate(method_id, context["policy_id"]),
    }
    
    print("Contextual Layer Scores:")
    for layer, score in layer_scores.items():
        print(f"  {layer}: {score}")
    
    print("\nThese scores would feed into the Choquet integral with:")
    print("  @b (base), @chain, @C (contract), @u (unit), @m (meta)")
    print("\nFinal calibration score: Cal(I) = Σ(a_ℓ × x_ℓ) + Σ(a_ℓk × min(x_ℓ, x_k))")


def main():
    """Run all examples."""
    print("=" * 70)
    print("Contextual Layer Evaluators - Usage Examples")
    print("COHORT_2024 - REFACTOR_WAVE_2024_12")
    print("=" * 70)
    
    try:
        example_1_basic_registry_usage()
        example_2_using_evaluators()
        example_3_factory_function()
        example_4_full_method_compatibility()
        example_5_anti_universality_check()
        example_6_penalty_demonstration()
        example_7_metadata_inspection()
        example_8_integration_with_calibration()
        
        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
