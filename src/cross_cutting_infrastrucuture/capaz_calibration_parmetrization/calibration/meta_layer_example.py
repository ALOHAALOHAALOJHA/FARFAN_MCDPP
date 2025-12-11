"""
Meta Layer (@m) Evaluator - Usage Example

Demonstrates how to use the MetaLayerEvaluator to evaluate
method transparency, governance, and cost metrics.
"""

from orchestration.meta_layer import (
    MetaLayerConfig,
    MetaLayerEvaluator,
    TransparencyArtifacts,
    GovernanceArtifacts,
    CostMetrics,
    create_default_config,
    compute_config_hash
)


def example_full_compliance():
    config = create_default_config()
    evaluator = MetaLayerEvaluator(config)

    transparency_artifacts: TransparencyArtifacts = {
        "formula_export": "Cal(I) = 0.5*x_@b + 0.4*x_@chain + 0.1*Choquet_interaction",
        "trace": "Phase 0: Validation -> Phase 1: Ingestion (step 1, step 2) -> Phase 2: Processing",
        "logs": {
            "timestamp": "2024-12-09T00:00:00Z",
            "level": "INFO",
            "method_name": "D3Q3_Executor.execute",
            "phase": "SCORE_Q",
            "message": "Execution completed successfully"
        }
    }

    governance_artifacts: GovernanceArtifacts = {
        "version_tag": "v2.1.3",
        "config_hash": "a" * 64,
        "signature": None
    }

    cost_metrics: CostMetrics = {
        "execution_time_s": 0.8,
        "memory_usage_mb": 256.0
    }

    log_schema = {
        "required": ["timestamp", "level", "method_name", "phase", "message"]
    }

    result = evaluator.evaluate(
        transparency_artifacts,
        governance_artifacts,
        cost_metrics,
        log_schema
    )

    print("Full Compliance Example:")
    print(f"  Overall Score: {result['score']:.3f}")
    print(f"  Transparency: {result['m_transparency']:.3f}")
    print(f"  Governance: {result['m_governance']:.3f}")
    print(f"  Cost: {result['m_cost']:.3f}")
    return result


def example_partial_compliance():
    config = create_default_config()
    evaluator = MetaLayerEvaluator(config)

    transparency_artifacts: TransparencyArtifacts = {
        "formula_export": "Cal(I) = expanded Choquet integral formula",
        "trace": None,
        "logs": {
            "timestamp": "2024-12-09T00:00:00Z",
            "level": "INFO",
            "method_name": "test_method",
            "phase": "test",
            "message": "test"
        }
    }

    governance_artifacts: GovernanceArtifacts = {
        "version_tag": "v1.5.0",
        "config_hash": "b" * 64,
        "signature": None
    }

    cost_metrics: CostMetrics = {
        "execution_time_s": 3.5,
        "memory_usage_mb": 400.0
    }

    log_schema = {
        "required": ["timestamp", "level", "method_name", "phase", "message"]
    }

    result = evaluator.evaluate(
        transparency_artifacts,
        governance_artifacts,
        cost_metrics,
        log_schema
    )

    print("\nPartial Compliance Example:")
    print(f"  Overall Score: {result['score']:.3f}")
    print(f"  Transparency: {result['m_transparency']:.3f} (2/3 conditions)")
    print(f"  Governance: {result['m_governance']:.3f} (2/3 conditions)")
    print(f"  Cost: {result['m_cost']:.3f} (acceptable but not fast)")
    return result


def example_poor_compliance():
    config = create_default_config()
    evaluator = MetaLayerEvaluator(config)

    transparency_artifacts: TransparencyArtifacts = {
        "formula_export": None,
        "trace": None,
        "logs": None
    }

    governance_artifacts: GovernanceArtifacts = {
        "version_tag": "unknown",
        "config_hash": "",
        "signature": None
    }

    cost_metrics: CostMetrics = {
        "execution_time_s": 8.0,
        "memory_usage_mb": 1024.0
    }

    result = evaluator.evaluate(
        transparency_artifacts,
        governance_artifacts,
        cost_metrics,
        None
    )

    print("\nPoor Compliance Example:")
    print(f"  Overall Score: {result['score']:.3f}")
    print(f"  Transparency: {result['m_transparency']:.3f} (0/3 conditions)")
    print(f"  Governance: {result['m_governance']:.3f} (0/3 conditions)")
    print(f"  Cost: {result['m_cost']:.3f} (exceeds thresholds)")
    return result


def example_config_hash_generation():
    config_data = {
        "method_name": "D3Q3_Executor",
        "parameters": {
            "threshold": 0.8,
            "max_iterations": 100
        },
        "seed": 42,
        "version": "v2.1.3"
    }

    config_hash = compute_config_hash(config_data)
    print(f"\nConfig Hash Example:")
    print(f"  Config: {config_data}")
    print(f"  SHA256 Hash: {config_hash}")
    return config_hash


if __name__ == "__main__":
    example_full_compliance()
    example_partial_compliance()
    example_poor_compliance()
    example_config_hash_generation()
