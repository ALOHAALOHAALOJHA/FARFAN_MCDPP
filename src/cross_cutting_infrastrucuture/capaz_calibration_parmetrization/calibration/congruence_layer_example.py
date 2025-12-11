"""
Congruence Layer (@C) Evaluator - Usage Example

Demonstrates how to use the CongruenceLayerEvaluator to evaluate
method ensemble harmony through output range compatibility,
semantic tag alignment, and fusion rule validity.
"""

from orchestration.congruence_layer import (
    CongruenceLayerEvaluator,
    OutputRangeSpec,
    SemanticTagSet,
    FusionRule,
    create_default_congruence_config
)


def example_perfect_congruence():
    """Example: Perfect congruence between methods."""
    print("=== Example 1: Perfect Congruence ===")
    
    config = create_default_congruence_config()
    evaluator = CongruenceLayerEvaluator(config)

    current_range = OutputRangeSpec(
        min=0.0,
        max=1.0,
        output_type="float"
    )
    upstream_range = OutputRangeSpec(
        min=0.0,
        max=1.0,
        output_type="float"
    )
    current_tags = SemanticTagSet(
        tags={"causal", "temporal", "numeric"},
        description="Causal mechanism extraction with temporal and numeric analysis"
    )
    upstream_tags = SemanticTagSet(
        tags={"causal", "temporal", "numeric"},
        description="Policy text processing with causal and temporal features"
    )
    fusion = FusionRule(
        rule_type="aggregation",
        operator="weighted_avg",
        is_valid=True,
        description="Weighted average aggregation of upstream outputs"
    )
    fusion_context = {
        "input_count": 3,
        "weights": [0.5, 0.3, 0.2]
    }

    result = evaluator.evaluate(
        current_range, upstream_range,
        current_tags, upstream_tags,
        fusion, fusion_context
    )

    print(f"C_play (Overall): {result['C_play']:.3f}")
    print(f"c_scale (Range Compatibility): {result['c_scale']:.3f}")
    print(f"c_sem (Semantic Alignment): {result['c_sem']:.3f}")
    print(f"c_fusion (Fusion Validity): {result['c_fusion']:.3f}")
    print()


def example_partial_congruence():
    """Example: Partial congruence with some misalignment."""
    print("=== Example 2: Partial Congruence ===")
    
    config = create_default_congruence_config()
    evaluator = CongruenceLayerEvaluator(config)

    current_range = OutputRangeSpec(
        min=0.0,
        max=1.0,
        output_type="float"
    )
    upstream_range = OutputRangeSpec(
        min=0.3,
        max=1.5,
        output_type="float"
    )
    current_tags = SemanticTagSet(
        tags={"causal", "temporal"},
        description="Causal and temporal analysis"
    )
    upstream_tags = SemanticTagSet(
        tags={"causal", "numeric", "spatial"},
        description="Multi-dimensional policy analysis"
    )
    fusion = FusionRule(
        rule_type="aggregation",
        operator="sum",
        is_valid=True,
        description="Simple summation"
    )

    result = evaluator.evaluate(
        current_range, upstream_range,
        current_tags, upstream_tags,
        fusion
    )

    print(f"C_play (Overall): {result['C_play']:.3f}")
    print(f"c_scale (Range Compatibility): {result['c_scale']:.3f}")
    print(f"c_sem (Semantic Alignment): {result['c_sem']:.3f}")
    print(f"c_fusion (Fusion Validity): {result['c_fusion']:.3f}")
    print()


def example_incompatible_methods():
    """Example: Incompatible methods with zero congruence."""
    print("=== Example 3: Incompatible Methods ===")
    
    config = create_default_congruence_config()
    evaluator = CongruenceLayerEvaluator(config)

    current_range = OutputRangeSpec(
        min=0.0,
        max=1.0,
        output_type="float"
    )
    upstream_range = OutputRangeSpec(
        min=5.0,
        max=10.0,
        output_type="float"
    )
    current_tags = SemanticTagSet(
        tags={"causal"},
        description="Causal analysis only"
    )
    upstream_tags = SemanticTagSet(
        tags={"numeric", "statistical"},
        description="Statistical numeric analysis"
    )
    fusion = FusionRule(
        rule_type="aggregation",
        operator="invalid_op",
        is_valid=False,
        description="Invalid fusion rule"
    )

    result = evaluator.evaluate(
        current_range, upstream_range,
        current_tags, upstream_tags,
        fusion
    )

    print(f"C_play (Overall): {result['C_play']:.3f}")
    print(f"c_scale (Range Compatibility): {result['c_scale']:.3f}")
    print(f"c_sem (Semantic Alignment): {result['c_sem']:.3f}")
    print(f"c_fusion (Fusion Validity): {result['c_fusion']:.3f}")
    print()


def example_individual_components():
    """Example: Evaluating individual congruence components."""
    print("=== Example 4: Individual Component Evaluation ===")
    
    config = create_default_congruence_config()
    evaluator = CongruenceLayerEvaluator(config)

    print("Component 1: Output Range Compatibility")
    current = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
    upstream = OutputRangeSpec(min=0.2, max=0.8, output_type="float")
    c_scale = evaluator.evaluate_output_scale_compatibility(current, upstream)
    print(f"  c_scale: {c_scale:.3f}")

    print("\nComponent 2: Semantic Tag Alignment")
    curr_tags = SemanticTagSet(tags={"causal", "temporal", "numeric"}, description=None)
    up_tags = SemanticTagSet(tags={"causal", "temporal"}, description=None)
    c_sem = evaluator.evaluate_semantic_alignment(curr_tags, up_tags)
    print(f"  c_sem (Jaccard): {c_sem:.3f}")

    print("\nComponent 3: Fusion Rule Validity")
    fusion = FusionRule(
        rule_type="aggregation",
        operator="choquet",
        is_valid=True,
        description="Choquet integral fusion"
    )
    c_fusion = evaluator.evaluate_fusion_rule_validity(fusion)
    print(f"  c_fusion: {c_fusion:.3f}")
    print()


def example_executor_ensemble():
    """Example: Evaluating congruence in an executor ensemble."""
    print("=== Example 5: Executor Ensemble Congruence ===")
    
    config = create_default_congruence_config()
    evaluator = CongruenceLayerEvaluator(config)

    executors = [
        {
            "name": "CausalExtractor",
            "range": OutputRangeSpec(min=0.0, max=1.0, output_type="float"),
            "tags": SemanticTagSet(tags={"causal", "temporal"}, description=None)
        },
        {
            "name": "GoalAnalyzer",
            "range": OutputRangeSpec(min=0.0, max=1.0, output_type="float"),
            "tags": SemanticTagSet(tags={"causal", "goal-oriented"}, description=None)
        },
        {
            "name": "TemporalAnalyzer",
            "range": OutputRangeSpec(min=0.0, max=1.0, output_type="float"),
            "tags": SemanticTagSet(tags={"temporal", "sequential"}, description=None)
        }
    ]

    fusion = FusionRule(
        rule_type="aggregation",
        operator="weighted_avg",
        is_valid=True,
        description="Executor ensemble aggregation"
    )
    
    fusion_context = {
        "input_count": 3,
        "weights": [0.4, 0.35, 0.25]
    }

    print("Pairwise congruence scores:")
    for i in range(len(executors) - 1):
        for j in range(i + 1, len(executors)):
            result = evaluator.evaluate(
                executors[i]["range"], executors[j]["range"],
                executors[i]["tags"], executors[j]["tags"],
                fusion, fusion_context
            )
            print(f"  {executors[i]['name']} <-> {executors[j]['name']}: {result['C_play']:.3f}")
    print()


if __name__ == "__main__":
    example_perfect_congruence()
    example_partial_congruence()
    example_incompatible_methods()
    example_individual_components()
    example_executor_ensemble()
