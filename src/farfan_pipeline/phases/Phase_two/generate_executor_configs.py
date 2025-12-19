"""
Generate executor-specific configuration files for all 30+ D[1-6]Q[1-5] executors.

PHASE_LABEL: Phase 2

This script creates JSON configuration files with runtime parameters (HOW)
for each executor, ensuring NO hardcoded calibration values (WHAT).
"""

import json
from pathlib import Path
from typing import Dict, List, Any

# Executor metadata: (dimension, question, name, epistemic_mix, critical_methods)
EXECUTORS = [
    # Dimension 1: Diagnostics & Inputs
    ("D1", "Q1", "QuantitativeBaselineExtractor", ["semantic", "statistical", "normative"], 15),
    ("D1", "Q2", "ProblemDimensioningAnalyzer", ["bayesian", "statistical", "normative"], 12),
    ("D1", "Q3", "BudgetAllocationTracer", ["structural", "financial", "normative"], 13),
    ("D1", "Q4", "InstitutionalCapacityIdentifier", ["semantic", "structural"], 11),
    ("D1", "Q5", "ScopeJustificationValidator", ["temporal", "consistency", "normative"], 7),
    
    # Dimension 2: Activity Design
    ("D2", "Q1", "StructuredPlanningValidator", ["structural", "normative"], 7),
    ("D2", "Q2", "InterventionLogicInferencer", ["causal", "bayesian", "structural"], 11),
    ("D2", "Q3", "RootCauseLinkageAnalyzer", ["causal", "structural", "semantic"], 9),
    ("D2", "Q4", "RiskManagementAnalyzer", ["bayesian", "statistical", "normative"], 10),
    ("D2", "Q5", "StrategicCoherenceEvaluator", ["consistency", "normative", "structural"], 8),
    
    # Dimension 3: Products & Outputs
    ("D3", "Q1", "IndicatorQualityValidator", ["normative", "structural", "semantic"], 8),
    ("D3", "Q2", "TargetProportionalityAnalyzer", ["statistical", "financial", "normative"], 21),
    ("D3", "Q3", "TraceabilityValidator", ["structural", "semantic", "normative"], 22),
    ("D3", "Q4", "TechnicalFeasibilityEvaluator", ["financial", "normative", "statistical"], 10),
    ("D3", "Q5", "OutputOutcomeLinkageAnalyzer", ["causal", "structural", "semantic"], 9),
    
    # Dimension 4: Outcomes
    ("D4", "Q1", "OutcomeMetricsValidator", ["normative", "statistical", "semantic"], 8),
    ("D4", "Q2", "CausalChainValidator", ["causal", "structural", "consistency"], 10),
    ("D4", "Q3", "AmbitionJustificationAnalyzer", ["normative", "statistical", "semantic"], 9),
    ("D4", "Q4", "ProblemSolvencyEvaluator", ["causal", "bayesian", "normative"], 11),
    ("D4", "Q5", "VerticalAlignmentValidator", ["structural", "consistency", "normative"], 8),
    
    # Dimension 5: Impacts
    ("D5", "Q1", "LongTermVisionAnalyzer", ["semantic", "normative", "temporal"], 8),
    ("D5", "Q2", "CompositeMeasurementValidator", ["statistical", "normative", "semantic"], 10),
    ("D5", "Q3", "IntangibleMeasurementAnalyzer", ["semantic", "normative", "bayesian"], 9),
    ("D5", "Q4", "SystemicRiskEvaluator", ["bayesian", "causal", "normative"], 12),
    ("D5", "Q5", "RealismAndSideEffectsAnalyzer", ["causal", "bayesian", "normative"], 11),
    
    # Dimension 6: Theory of Change
    ("D6", "Q1", "ExplicitTheoryBuilder", ["causal", "structural", "semantic"], 15),
    ("D6", "Q2", "LogicalProportionalityValidator", ["structural", "consistency", "normative"], 10),
    ("D6", "Q3", "ValidationTestingAnalyzer", ["causal", "bayesian", "statistical"], 13),
    ("D6", "Q4", "FeedbackLoopAnalyzer", ["causal", "structural", "temporal"], 9),
    ("D6", "Q5", "ContextualAdaptabilityEvaluator", ["semantic", "normative", "causal"], 10),
]


def create_executor_config(
    dimension: str,
    question: str,
    name: str,
    epistemic_mix: List[str],
    expected_methods: int
) -> Dict[str, Any]:
    """
    Create configuration dict for an executor.
    
    Args:
        dimension: Dimension ID (D1-D6)
        question: Question ID (Q1-Q5)
        name: Executor class name suffix
        epistemic_mix: List of epistemic tags
        expected_methods: Expected number of methods
    
    Returns:
        Configuration dictionary
    """
    executor_id = f"{dimension}_{question}_{name}"
    
    # Base runtime parameters (HOW - parametrization)
    config = {
        "executor_id": executor_id,
        "dimension": dimension,
        "question": question,
        "role": "SCORE_Q",
        "required_layers": [
            "@b",      # BASE: Code quality
            "@chain",  # CHAIN: Method wiring
            "@q",      # QUESTION: Question appropriateness
            "@d",      # DIMENSION: Dimension alignment
            "@p",      # POLICY: Policy area fit
            "@C",      # CONGRUENCE: Contract compliance
            "@u",      # UNIT: Document quality
            "@m",      # META: Governance maturity
        ],
        "runtime_parameters": {
            "timeout_s": 300,
            "retry": 3,
            "temperature": 0.0,
            "max_tokens": 4096,
            "memory_limit_mb": 512,
            "enable_profiling": True,
        },
        "thresholds": {
            "min_quality_score": 0.5,
            "min_evidence_confidence": 0.6,
            "max_runtime_ms": 60000,
        },
        "epistemic_mix": epistemic_mix,
        "contextual_params": {
            "expected_methods": expected_methods,
            "critical_methods": [],
        },
    }
    
    # Dimension-specific adjustments
    if dimension in ["D5", "D6"]:
        # Complex causal analysis: higher timeout, more tokens
        config["runtime_parameters"]["timeout_s"] = 450
        config["runtime_parameters"]["max_tokens"] = 8192
        config["runtime_parameters"]["memory_limit_mb"] = 1024
    
    if dimension in ["D1", "D2"]:
        # Input/baseline analysis: stricter thresholds
        config["thresholds"]["min_evidence_confidence"] = 0.7
    
    return config


def generate_all_configs(output_dir: Path) -> None:
    """
    Generate configuration files for all executors.
    
    Args:
        output_dir: Directory to write config files
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        "metadata": {
            "description": "Executor configuration generation report",
            "total_executors": len(EXECUTORS),
        },
        "executors": []
    }
    
    for dimension, question, name, epistemic_mix, expected_methods in EXECUTORS:
        config = create_executor_config(
            dimension, question, name, epistemic_mix, expected_methods
        )
        
        executor_id = config["executor_id"]
        output_file = output_dir / f"{executor_id}.json"
        
        with open(output_file, "w") as f:
            json.dump(config, f, indent=2)
        
        report["executors"].append({
            "executor_id": executor_id,
            "config_file": str(output_file),
            "dimension": dimension,
            "question": question,
            "epistemic_mix": epistemic_mix,
        })
        
        print(f"✓ Generated config: {output_file}")
    
    # Write summary report
    report_file = output_dir / "generation_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Generated {len(EXECUTORS)} executor configs")
    print(f"✓ Report: {report_file}")


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "executor_configs"
    generate_all_configs(output_dir)
