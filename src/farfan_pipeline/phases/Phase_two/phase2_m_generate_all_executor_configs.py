"""
Generate executor configuration files for all 30 D[1-6]Q[1-5] executors.

Creates individual JSON config files with runtime parameters (HOW)
for each executor, ensuring NO hardcoded calibration values (WHAT).
"""

import json
from pathlib import Path
from typing import Dict, List, Any

# Define all 30 executors with their metadata
EXECUTORS = [
    # D1: DIAGNOSTICS & INPUTS
    ("D1_Q1_QuantitativeBaselineExtractor", "D1", "Q1", ["structural", "statistical", "semantic"], 15),
    ("D1_Q2_ProblemDimensioningAnalyzer", "D1", "Q2", ["bayesian", "statistical", "normative"], 12),
    ("D1_Q3_BudgetAllocationTracer", "D1", "Q3", ["structural", "financial", "normative"], 13),
    ("D1_Q4_InstitutionalCapacityIdentifier", "D1", "Q4", ["semantic", "structural"], 11),
    ("D1_Q5_ScopeJustificationValidator", "D1", "Q5", ["temporal", "consistency", "structural"], 7),
    
    # D2: ACTIVITY DESIGN
    ("D2_Q1_StructuredPlanningValidator", "D2", "Q1", ["structural", "normative"], 7),
    ("D2_Q2_InterventionLogicInferencer", "D2", "Q2", ["causal", "bayesian", "structural"], 11),
    ("D2_Q3_RootCauseLinkageAnalyzer", "D2", "Q3", ["causal", "bayesian", "semantic"], 9),
    ("D2_Q4_RiskManagementAnalyzer", "D2", "Q4", ["bayesian", "statistical", "normative"], 10),
    ("D2_Q5_StrategicCoherenceEvaluator", "D2", "Q5", ["normative", "consistency", "statistical"], 8),
    
    # D3: PRODUCTS & OUTPUTS
    ("D3_Q1_IndicatorQualityValidator", "D3", "Q1", ["normative", "semantic", "structural"], 8),
    ("D3_Q2_TargetProportionalityAnalyzer", "D3", "Q2", ["structural", "financial", "bayesian"], 21),
    ("D3_Q3_TraceabilityValidator", "D3", "Q3", ["structural", "semantic", "normative"], 22),
    ("D3_Q4_TechnicalFeasibilityEvaluator", "D3", "Q4", ["structural", "causal", "statistical"], 26),
    ("D3_Q5_OutputOutcomeLinkageAnalyzer", "D3", "Q5", ["causal", "bayesian", "semantic"], 25),
    
    # D4: RESULTS & OUTCOMES
    ("D4_Q1_OutcomeMetricsValidator", "D4", "Q1", ["semantic", "temporal", "statistical"], 17),
    ("D4_Q2_CausalChainValidator", "D4", "Q2", ["causal", "bayesian", "structural"], 8),
    ("D4_Q3_AmbitionJustificationAnalyzer", "D4", "Q3", ["bayesian", "statistical"], 8),
    ("D4_Q4_ProblemSolvencyEvaluator", "D4", "Q4", ["normative", "consistency"], 7),
    ("D4_Q5_VerticalAlignmentValidator", "D4", "Q5", ["normative", "structural"], 6),
    
    # D5: IMPACTS
    ("D5_Q1_LongTermVisionAnalyzer", "D5", "Q1", ["causal", "temporal", "semantic"], 8),
    ("D5_Q2_CompositeMeasurementValidator", "D5", "Q2", ["bayesian", "statistical", "normative"], 14),
    ("D5_Q3_IntangibleMeasurementAnalyzer", "D5", "Q3", ["semantic", "normative"], 7),
    ("D5_Q4_SystemicRiskEvaluator", "D5", "Q4", ["bayesian", "causal", "statistical"], 9),
    ("D5_Q5_RealismAndSideEffectsAnalyzer", "D5", "Q5", ["causal", "bayesian", "normative"], 9),
    
    # D6: CAUSAL THEORY
    ("D6_Q1_ExplicitTheoryBuilder", "D6", "Q1", ["causal", "structural", "semantic"], 10),
    ("D6_Q2_LogicalProportionalityValidator", "D6", "Q2", ["normative", "causal", "statistical"], 8),
    ("D6_Q3_ValidationTestingAnalyzer", "D6", "Q3", ["bayesian", "causal", "statistical"], 9),
    ("D6_Q4_FeedbackLoopAnalyzer", "D6", "Q4", ["causal", "temporal", "structural"], 8),
    ("D6_Q5_ContextualAdaptabilityEvaluator", "D6", "Q5", ["semantic", "normative", "contextual"], 8),
]


def generate_executor_config(
    executor_id: str,
    dimension: str,
    question: str,
    epistemic_mix: List[str],
    expected_methods: int
) -> Dict[str, Any]:
    """Generate configuration for a single executor."""
    
    # Base config template
    config = {
        "executor_id": executor_id,
        "dimension": dimension,
        "question": question,
        "canonical_label": f"DIM{dimension[1:].zfill(2)}_Q{question[1:].zfill(2)}_{executor_id.split('_', 2)[2].upper()}",
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
            "enable_profiling": True
        },
        "thresholds": {
            "min_quality_score": 0.5,
            "min_evidence_confidence": 0.6,
            "max_runtime_ms": 60000
        },
        "epistemic_mix": epistemic_mix,
        "contextual_params": {
            "expected_methods": expected_methods,
            "critical_methods": []
        },
        "calibration_settings": {
            "enabled": True,
            "capture_runtime_metrics": True,
            "capture_memory_metrics": True,
            "store_results": True
        }
    }
    
    return config


def main():
    """Generate all executor configuration files."""
    output_dir = Path(__file__).parent / "executor_configs"
    output_dir.mkdir(exist_ok=True)
    
    generated_count = 0
    
    for executor_id, dimension, question, epistemic_mix, expected_methods in EXECUTORS:
        config = generate_executor_config(
            executor_id, dimension, question, epistemic_mix, expected_methods
        )
        
        output_file = output_dir / f"{executor_id}.json"
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Generated: {output_file.name}")
        generated_count += 1
    
    print(f"\nTotal configs generated: {generated_count}")
    print(f"Expected: 30")
    print(f"Status: {'✓ COMPLETE' if generated_count == 30 else '✗ INCOMPLETE'}")


if __name__ == "__main__":
    main()
