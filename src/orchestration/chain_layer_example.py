"""
Chain Layer (@chain) Evaluator - Usage Example

Demonstrates how to use the ChainLayerEvaluator to validate
method chaining and orchestration through signature validation
against upstream outputs.
"""

from src.orchestration.chain_layer import (
    ChainLayerEvaluator,
    MethodSignature,
    UpstreamOutputs,
    create_default_chain_config
)


def example_perfect_chain():
    """Example: Perfect chain with all required inputs available."""
    print("=== Example 1: Perfect Chain ===")
    
    config = create_default_chain_config()
    evaluator = ChainLayerEvaluator(config)

    signature = MethodSignature(
        required_inputs=["policy_text", "dimension_id"],
        optional_inputs=["metadata", "context"],
        critical_optional=["context"],
        output_type="dict",
        output_range=[0.0, 1.0]
    )
    
    upstream = UpstreamOutputs(
        available_outputs={"policy_text", "dimension_id", "metadata", "context"},
        output_types={
            "policy_text": "str",
            "dimension_id": "str",
            "metadata": "dict",
            "context": "dict"
        }
    )

    result = evaluator.evaluate(signature, upstream)
    
    print(f"Chain Score: {result['chain_score']:.1f}")
    print(f"Validation Status: {result['validation_status']}")
    print(f"Available Ratio: {result['available_ratio']:.2f}")
    print(f"Missing Required: {result['missing_required']}")
    print(f"Missing Critical: {result['missing_critical']}")
    print(f"Warnings: {result['warnings']}")
    print()


def example_missing_required():
    """Example: Chain failure due to missing required inputs."""
    print("=== Example 2: Missing Required Inputs (Score: 0.0) ===")
    
    config = create_default_chain_config()
    evaluator = ChainLayerEvaluator(config)

    signature = MethodSignature(
        required_inputs=["policy_text", "dimension_id", "question_id"],
        optional_inputs=["metadata"],
        critical_optional=[],
        output_type="dict",
        output_range=None
    )
    
    upstream = UpstreamOutputs(
        available_outputs={"policy_text"},
        output_types={"policy_text": "str"}
    )

    result = evaluator.evaluate(signature, upstream)
    
    print(f"Chain Score: {result['chain_score']:.1f}")
    print(f"Validation Status: {result['validation_status']}")
    print(f"Missing Required: {result['missing_required']}")
    print()


def example_missing_critical():
    """Example: Missing critical optional inputs (Score: 0.3)."""
    print("=== Example 3: Missing Critical Optional (Score: 0.3) ===")
    
    config = create_default_chain_config()
    evaluator = ChainLayerEvaluator(config)

    signature = MethodSignature(
        required_inputs=["policy_text"],
        optional_inputs=["context", "embeddings", "metadata"],
        critical_optional=["context", "embeddings"],
        output_type="dict",
        output_range=None
    )
    
    upstream = UpstreamOutputs(
        available_outputs={"policy_text", "metadata"},
        output_types={"policy_text": "str", "metadata": "dict"}
    )

    result = evaluator.evaluate(signature, upstream)
    
    print(f"Chain Score: {result['chain_score']:.1f}")
    print(f"Validation Status: {result['validation_status']}")
    print(f"Missing Critical: {result['missing_critical']}")
    print()


def example_missing_optional():
    """Example: Missing only optional inputs (Score: 0.6 or 1.0)."""
    print("=== Example 4: Missing Optional Inputs ===")
    
    config = create_default_chain_config()
    evaluator = ChainLayerEvaluator(config)

    signature = MethodSignature(
        required_inputs=["policy_text"],
        optional_inputs=["metadata", "config"],
        critical_optional=[],
        output_type="dict",
        output_range=None
    )
    
    upstream = UpstreamOutputs(
        available_outputs={"policy_text"},
        output_types={"policy_text": "str"}
    )

    result = evaluator.evaluate(signature, upstream)
    
    print(f"Chain Score: {result['chain_score']:.1f}")
    print(f"Validation Status: {result['validation_status']}")
    print(f"Missing Optional: {result['missing_optional']}")
    print(f"Config allows missing optional: {result['config']['allow_missing_optional']}")
    print()


def example_with_warnings():
    """Example: Chain with warnings (Score: 0.8)."""
    print("=== Example 5: Chain with Warnings (Score: 0.8) ===")
    
    config = create_default_chain_config()
    evaluator = ChainLayerEvaluator(config)

    signature = MethodSignature(
        required_inputs=["policy_text"],
        optional_inputs=["context", "metadata"],
        critical_optional=[],
        output_type="dict",
        output_range=None
    )
    
    upstream = UpstreamOutputs(
        available_outputs={"policy_text"},
        output_types={"policy_text": "str"}
    )

    result = evaluator.evaluate(signature, upstream)
    
    print(f"Chain Score: {result['chain_score']:.1f}")
    print(f"Validation Status: {result['validation_status']}")
    print(f"Warnings: {result['warnings']}")
    print()


def example_chain_sequence():
    """Example: Evaluating a sequence of chained methods."""
    print("=== Example 6: Chain Sequence Evaluation ===")
    
    config = create_default_chain_config()
    evaluator = ChainLayerEvaluator(config)

    method_signatures = [
        ("PolicyIngestor", MethodSignature(
            required_inputs=["raw_policy_document"],
            optional_inputs=[],
            critical_optional=[],
            output_type="str",
            output_range=None
        )),
        ("PolicyProcessor", MethodSignature(
            required_inputs=["PolicyIngestor"],
            optional_inputs=["processing_config"],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )),
        ("CausalExtractor", MethodSignature(
            required_inputs=["PolicyProcessor"],
            optional_inputs=["semantic_model"],
            critical_optional=["semantic_model"],
            output_type="dict",
            output_range=None
        )),
        ("GoalAnalyzer", MethodSignature(
            required_inputs=["PolicyProcessor", "CausalExtractor"],
            optional_inputs=["context"],
            critical_optional=[],
            output_type="dict",
            output_range=None
        )),
        ("ScoreAggregator", MethodSignature(
            required_inputs=["CausalExtractor", "GoalAnalyzer"],
            optional_inputs=["weights"],
            critical_optional=["weights"],
            output_type="float",
            output_range=[0.0, 1.0]
        ))
    ]
    
    initial_inputs = {"raw_policy_document"}

    result = evaluator.evaluate_chain_sequence(method_signatures, initial_inputs)
    
    print(f"Sequence Score: {result['sequence_score']:.2f}")
    print(f"Total Methods: {result['total_methods']}")
    print(f"Failed Methods: {result['failed_methods']}")
    print("\nIndividual Method Results:")
    for method_result in result["method_results"]:
        print(f"  {method_result['method_id']}: {method_result['score']:.1f} ({method_result['status']})")
    print(f"\nFinal Available Outputs: {len(result['final_available_outputs'])} outputs")
    print()


def example_strict_mode():
    """Example: Using strict validation mode."""
    print("=== Example 7: Strict Mode Validation ===")
    
    from src.orchestration.chain_layer import ChainLayerConfig
    
    strict_config = ChainLayerConfig(
        validation_config={
            "strict_mode": True,
            "allow_missing_optional": False,
            "penalize_warnings": True
        },
        score_missing_required=0.0,
        score_missing_critical=0.3,
        score_missing_optional=0.6,
        score_warnings=0.8,
        score_perfect=1.0
    )
    evaluator = ChainLayerEvaluator(strict_config)

    signature = MethodSignature(
        required_inputs=["policy_text"],
        optional_inputs=["metadata", "config"],
        critical_optional=[],
        output_type="dict",
        output_range=None
    )
    
    upstream = UpstreamOutputs(
        available_outputs={"policy_text"},
        output_types={"policy_text": "str"}
    )

    result = evaluator.evaluate(signature, upstream)
    
    print(f"Chain Score: {result['chain_score']:.1f}")
    print(f"Validation Status: {result['validation_status']}")
    print(f"Strict Mode: {result['config']['strict_mode']}")
    print(f"Allow Missing Optional: {result['config']['allow_missing_optional']}")
    print()


def example_score_thresholds():
    """Example: Understanding discrete score thresholds."""
    print("=== Example 8: Discrete Score Thresholds ===")
    
    config = create_default_chain_config()
    evaluator = ChainLayerEvaluator(config)

    signature = MethodSignature(
        required_inputs=["input"],
        optional_inputs=[],
        critical_optional=[],
        output_type="dict",
        output_range=None
    )
    
    upstream = UpstreamOutputs(
        available_outputs={"input"},
        output_types={}
    )

    result = evaluator.evaluate(signature, upstream)
    
    print("Score Thresholds:")
    for threshold_name, threshold_value in result["score_thresholds"].items():
        print(f"  {threshold_name}: {threshold_value:.1f}")
    print()


if __name__ == "__main__":
    example_perfect_chain()
    example_missing_required()
    example_missing_critical()
    example_missing_optional()
    example_with_warnings()
    example_chain_sequence()
    example_strict_mode()
    example_score_thresholds()
