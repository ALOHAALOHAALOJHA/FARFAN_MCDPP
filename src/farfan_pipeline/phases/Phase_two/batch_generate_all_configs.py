"""
Batch generate all 30 executor config files with proper separation.

CRITICAL: These files contain ONLY runtime parameters (HOW).
NO calibration values (quality scores) are stored here.
"""

import json
from pathlib import Path

configs = {
    "D1_Q3_BudgetAllocationTracer": {"D": "D1", "Q": "Q3", "label": "Trazabilidad de Asignación Presupuestal", "methods": 13, "epistemic": ["structural", "financial", "normative"]},
    "D1_Q4_InstitutionalCapacityIdentifier": {"D": "D1", "Q": "Q4", "label": "Identificación de Capacidad Institucional", "methods": 11, "epistemic": ["semantic", "structural"]},
    "D1_Q5_ScopeJustificationValidator": {"D": "D1", "Q": "Q5", "label": "Validación de Justificación de Alcance", "methods": 7, "epistemic": ["temporal", "consistency", "normative"]},
    "D2_Q1_StructuredPlanningValidator": {"D": "D2", "Q": "Q1", "label": "Validación de Planificación Estructurada", "methods": 7, "epistemic": ["structural", "normative"]},
    "D2_Q2_InterventionLogicInferencer": {"D": "D2", "Q": "Q2", "label": "Inferencia de Lógica de Intervención", "methods": 11, "epistemic": ["causal", "bayesian", "structural"]},
    "D2_Q3_RootCauseLinkageAnalyzer": {"D": "D2", "Q": "Q3", "label": "Análisis de Vinculación a Causas Raíz", "methods": 9, "epistemic": ["causal", "structural", "semantic"]},
    "D2_Q4_RiskManagementAnalyzer": {"D": "D2", "Q": "Q4", "label": "Análisis de Gestión de Riesgos", "methods": 10, "epistemic": ["bayesian", "statistical", "normative"]},
    "D2_Q5_StrategicCoherenceEvaluator": {"D": "D2", "Q": "Q5", "label": "Evaluación de Coherencia Estratégica", "methods": 8, "epistemic": ["consistency", "normative", "structural"]},
    "D3_Q1_IndicatorQualityValidator": {"D": "D3", "Q": "Q1", "label": "Validación de Calidad de Indicadores", "methods": 8, "epistemic": ["normative", "structural", "semantic"]},
    "D3_Q3_TraceabilityValidator": {"D": "D3", "Q": "Q3", "label": "DIM03_Q03_TRACEABILITY_BUDGET_ORG", "methods": 22, "epistemic": ["structural", "semantic", "normative"]},
    "D3_Q4_TechnicalFeasibilityEvaluator": {"D": "D3", "Q": "Q4", "label": "DIM03_Q04_TECHNICAL_FEASIBILITY", "methods": 10, "epistemic": ["financial", "normative", "statistical"]},
    "D3_Q5_OutputOutcomeLinkageAnalyzer": {"D": "D3", "Q": "Q5", "label": "DIM03_Q05_OUTPUT_OUTCOME_LINKAGE", "methods": 9, "epistemic": ["causal", "structural", "semantic"]},
    "D4_Q1_OutcomeMetricsValidator": {"D": "D4", "Q": "Q1", "label": "DIM04_Q01_OUTCOME_INDICATOR_COMPLETENESS", "methods": 8, "epistemic": ["normative", "statistical", "semantic"]},
    "D4_Q2_CausalChainValidator": {"D": "D4", "Q": "Q2", "label": "Validación de Cadena Causal", "methods": 10, "epistemic": ["causal", "structural", "consistency"]},
    "D4_Q3_AmbitionJustificationAnalyzer": {"D": "D4", "Q": "Q3", "label": "Análisis de Justificación de Ambición", "methods": 9, "epistemic": ["normative", "statistical", "semantic"]},
    "D4_Q4_ProblemSolvencyEvaluator": {"D": "D4", "Q": "Q4", "label": "Evaluación de Solvencia del Problema", "methods": 11, "epistemic": ["causal", "bayesian", "normative"]},
    "D4_Q5_VerticalAlignmentValidator": {"D": "D4", "Q": "Q5", "label": "Validación de Alineación Vertical", "methods": 8, "epistemic": ["structural", "consistency", "normative"]},
    "D5_Q1_LongTermVisionAnalyzer": {"D": "D5", "Q": "Q1", "label": "Análisis de Visión de Largo Plazo", "methods": 8, "epistemic": ["semantic", "normative", "temporal"]},
    "D5_Q2_CompositeMeasurementValidator": {"D": "D5", "Q": "Q2", "label": "DIM05_Q02_COMPOSITE_PROXY_VALIDITY", "methods": 10, "epistemic": ["statistical", "normative", "semantic"]},
    "D5_Q3_IntangibleMeasurementAnalyzer": {"D": "D5", "Q": "Q3", "label": "Análisis de Medición Intangible", "methods": 9, "epistemic": ["semantic", "normative", "bayesian"]},
    "D5_Q4_SystemicRiskEvaluator": {"D": "D5", "Q": "Q4", "label": "Evaluación de Riesgo Sistémico", "methods": 12, "epistemic": ["bayesian", "causal", "normative"]},
    "D5_Q5_RealismAndSideEffectsAnalyzer": {"D": "D5", "Q": "Q5", "label": "Análisis de Realismo y Efectos Colaterales", "methods": 11, "epistemic": ["causal", "bayesian", "normative"]},
    "D6_Q2_LogicalProportionalityValidator": {"D": "D6", "Q": "Q2", "label": "Validación de Proporcionalidad Lógica", "methods": 10, "epistemic": ["structural", "consistency", "normative"]},
    "D6_Q3_ValidationTestingAnalyzer": {"D": "D6", "Q": "Q3", "label": "Análisis de Pruebas de Validación", "methods": 13, "epistemic": ["causal", "bayesian", "statistical"]},
    "D6_Q4_FeedbackLoopAnalyzer": {"D": "D6", "Q": "Q4", "label": "Análisis de Bucles de Retroalimentación", "methods": 9, "epistemic": ["causal", "structural", "temporal"]},
    "D6_Q5_ContextualAdaptabilityEvaluator": {"D": "D6", "Q": "Q5", "label": "Evaluación de Adaptabilidad Contextual", "methods": 10, "epistemic": ["semantic", "normative", "causal"]},
}

output_dir = Path(__file__).parent / "executor_configs"

for eid, spec in configs.items():
    mc = spec["methods"]
    timeout = 300 if mc <= 15 else (600 if mc <= 20 else 900)
    mem = 1024 if ("causal" in spec["epistemic"] or "bayesian" in spec["epistemic"]) else 512
    
    config = {
        "executor_id": eid,
        "dimension": spec["D"],
        "question": spec["Q"],
        "canonical_label": spec["label"],
        "role": "SCORE_Q",
        "required_layers": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
        "runtime_parameters": {
            "timeout_s": timeout,
            "retry": 3,
            "temperature": 0.0,
            "max_tokens": 4096,
            "memory_limit_mb": mem,
            "enable_profiling": True,
            "seed": 42
        },
        "thresholds": {
            "min_quality_score": 0.5,
            "min_evidence_confidence": 0.7,
            "max_runtime_ms": timeout * 1000
        },
        "epistemic_mix": spec["epistemic"],
        "contextual_params": {
            "expected_methods": mc,
            "critical_methods": [],
            "dimension_label": f"DIM0{spec['D'][1]}",
            "question_label": spec["label"]
        }
    }
    
    with open(output_dir / f"{eid}.json", "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {eid}.json")

print(f"\\nCreated {len(configs)} config files in {output_dir}")
