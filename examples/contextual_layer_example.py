"""
Example usage of contextual layer evaluators (@q, @d, @p).

This example demonstrates:
1. Loading the compatibility registry
2. Evaluating individual contextual layers
3. Evaluating all contextual layers at once
4. Checking Anti-Universality Theorem compliance
"""

from pathlib import Path

from farfan_pipeline.core.calibration.compatibility import (
    CompatibilityRegistry,
    ContextualLayerEvaluator,
)


def main():
    config_path = Path("config/json_files_ no_schemas/method_compatibility.json")

    print("=" * 60)
    print("Contextual Layer Evaluators Example")
    print("=" * 60)

    print("\n1. Loading compatibility registry...")
    registry = CompatibilityRegistry(config_path)
    print(f"   Loaded {len(registry.mappings)} methods")

    print("\n2. Creating evaluator...")
    evaluator = ContextualLayerEvaluator(registry)

    print("\n3. Evaluating individual layers for 'pattern_extractor_v2':")
    method_id = "pattern_extractor_v2"

    q_score = evaluator.evaluate_question(method_id, "Q001")
    print(f"   @q (Question Q001): {q_score}")

    d_score = evaluator.evaluate_dimension(method_id, "DIM01")
    print(f"   @d (Dimension DIM01): {d_score}")

    p_score = evaluator.evaluate_policy(method_id, "PA01")
    print(f"   @p (Policy PA01): {p_score}")

    print("\n4. Evaluating all contextual layers at once:")
    scores = evaluator.evaluate_all_contextual(
        method_id="pattern_extractor_v2",
        question_id="Q031",
        dimension="DIM02",
        policy_area="PA10",
    )
    print(f"   Question Q031: {scores['q']}")
    print(f"   Dimension DIM02: {scores['d']}")
    print(f"   Policy PA10: {scores['p']}")

    print("\n5. Testing undeclared compatibility (returns 0.1 penalty):")
    scores = evaluator.evaluate_all_contextual(
        method_id="pattern_extractor_v2",
        question_id="Q999",
        dimension="DIM99",
        policy_area="PA99",
    )
    print(f"   Question Q999: {scores['q']} (penalty)")
    print(f"   Dimension DIM99: {scores['d']} (penalty)")
    print(f"   Policy PA99: {scores['p']} (penalty)")

    print("\n6. Checking Anti-Universality Theorem:")
    try:
        results = registry.validate_anti_universality(threshold=0.9)
        print("   ✓ All methods comply with Anti-Universality Theorem")
        for method_id, is_compliant in results.items():
            print(f"     - {method_id}: {'✓' if is_compliant else '✗'}")
    except ValueError as e:
        print(f"   ✗ Violation detected: {e}")

    print("\n7. Getting compatibility mapping directly:")
    mapping = registry.get("pattern_extractor_v2")
    print(f"   Method: {mapping.method_id}")
    print(f"   Questions: {len(mapping.questions)}")
    print(f"   Dimensions: {len(mapping.dimensions)}")
    print(f"   Policies: {len(mapping.policies)}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
