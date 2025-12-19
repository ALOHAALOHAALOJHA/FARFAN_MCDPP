"""
Generate complete executor configuration files for all 30 D[1-6]Q[1-5] executors.

PHASE_LABEL: Phase 2

This script creates comprehensive JSON config files for each executor that separate:
- Calibration data (WHAT quality scores) → loaded from intrinsic_calibration.json
- Runtime parameters (HOW execution) → stored in executor_configs/{executor_id}.json

Ensures NO hardcoded calibration values in executor code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any

EXECUTOR_DEFINITIONS = [
    {
        "executor_id": "D1_Q1_QuantitativeBaselineExtractor",
        "dimension": "D1",
        "question": "Q1",
        "canonical_label": "Extracción de Línea Base Cuantitativa",
        "methods_count": 15,
        "epistemic_mix": ["semantic", "statistical", "normative"],
    },
    {
        "executor_id": "D1_Q2_ProblemDimensioningAnalyzer",
        "dimension": "D1",
        "question": "Q2",
        "canonical_label": "Dimensionamiento del Problema",
        "methods_count": 12,
        "epistemic_mix": ["bayesian", "statistical", "normative"],
    },
    {
        "executor_id": "D1_Q3_BudgetAllocationTracer",
        "dimension": "D1",
        "question": "Q3",
        "canonical_label": "Trazabilidad de Asignación Presupuestal",
        "methods_count": 13,
        "epistemic_mix": ["structural", "financial", "normative"],
    },
    {
        "executor_id": "D1_Q4_InstitutionalCapacityIdentifier",
        "dimension": "D1",
        "question": "Q4",
        "canonical_label": "Identificación de Capacidad Institucional",
        "methods_count": 11,
        "epistemic_mix": ["semantic", "structural"],
    },
    {
        "executor_id": "D1_Q5_ScopeJustificationValidator",
        "dimension": "D1",
        "question": "Q5",
        "canonical_label": "Validación de Justificación de Alcance",
        "methods_count": 7,
        "epistemic_mix": ["temporal", "consistency", "normative"],
    },
    {
        "executor_id": "D2_Q1_StructuredPlanningValidator",
        "dimension": "D2",
        "question": "Q1",
        "canonical_label": "Validación de Planificación Estructurada",
        "methods_count": 7,
        "epistemic_mix": ["structural", "normative"],
    },
    {
        "executor_id": "D2_Q2_InterventionLogicInferencer",
        "dimension": "D2",
        "question": "Q2",
        "canonical_label": "Inferencia de Lógica de Intervención",
        "methods_count": 11,
        "epistemic_mix": ["causal", "bayesian", "structural"],
    },
    {
        "executor_id": "D2_Q3_RootCauseLinkageAnalyzer",
        "dimension": "D2",
        "question": "Q3",
        "canonical_label": "Análisis de Vinculación a Causas Raíz",
        "methods_count": 9,
        "epistemic_mix": ["causal", "structural", "semantic"],
    },
    {
        "executor_id": "D2_Q4_RiskManagementAnalyzer",
        "dimension": "D2",
        "question": "Q4",
        "canonical_label": "Análisis de Gestión de Riesgos",
        "methods_count": 10,
        "epistemic_mix": ["bayesian", "statistical", "normative"],
    },
    {
        "executor_id": "D2_Q5_StrategicCoherenceEvaluator",
        "dimension": "D2",
        "question": "Q5",
        "canonical_label": "Evaluación de Coherencia Estratégica",
        "methods_count": 8,
        "epistemic_mix": ["consistency", "normative", "structural"],
    },
    {
        "executor_id": "D3_Q1_IndicatorQualityValidator",
        "dimension": "D3",
        "question": "Q1",
        "canonical_label": "Validación de Calidad de Indicadores",
        "methods_count": 8,
        "epistemic_mix": ["normative", "structural", "semantic"],
    },
    {
        "executor_id": "D3_Q2_TargetProportionalityAnalyzer",
        "dimension": "D3",
        "question": "Q2",
        "canonical_label": "DIM03_Q02_PRODUCT_TARGET_PROPORTIONALITY",
        "methods_count": 21,
        "epistemic_mix": ["statistical", "financial", "normative"],
    },
    {
        "executor_id": "D3_Q3_TraceabilityValidator",
        "dimension": "D3",
        "question": "Q3",
        "canonical_label": "DIM03_Q03_TRACEABILITY_BUDGET_ORG",
        "methods_count": 22,
        "epistemic_mix": ["structural", "semantic", "normative"],
    },
    {
        "executor_id": "D3_Q4_TechnicalFeasibilityEvaluator",
        "dimension": "D3",
        "question": "Q4",
        "canonical_label": "DIM03_Q04_TECHNICAL_FEASIBILITY",
        "methods_count": 10,
        "epistemic_mix": ["financial", "normative", "statistical"],
    },
    {
        "executor_id": "D3_Q5_OutputOutcomeLinkageAnalyzer",
        "dimension": "D3",
        "question": "Q5",
        "canonical_label": "DIM03_Q05_OUTPUT_OUTCOME_LINKAGE",
        "methods_count": 9,
        "epistemic_mix": ["causal", "structural", "semantic"],
    },
    {
        "executor_id": "D4_Q1_OutcomeMetricsValidator",
        "dimension": "D4",
        "question": "Q1",
        "canonical_label": "DIM04_Q01_OUTCOME_INDICATOR_COMPLETENESS",
        "methods_count": 8,
        "epistemic_mix": ["normative", "statistical", "semantic"],
    },
    {
        "executor_id": "D4_Q2_CausalChainValidator",
        "dimension": "D4",
        "question": "Q2",
        "canonical_label": "Validación de Cadena Causal",
        "methods_count": 10,
        "epistemic_mix": ["causal", "structural", "consistency"],
    },
    {
        "executor_id": "D4_Q3_AmbitionJustificationAnalyzer",
        "dimension": "D4",
        "question": "Q3",
        "canonical_label": "Análisis de Justificación de Ambición",
        "methods_count": 9,
        "epistemic_mix": ["normative", "statistical", "semantic"],
    },
    {
        "executor_id": "D4_Q4_ProblemSolvencyEvaluator",
        "dimension": "D4",
        "question": "Q4",
        "canonical_label": "Evaluación de Solvencia del Problema",
        "methods_count": 11,
        "epistemic_mix": ["causal", "bayesian", "normative"],
    },
    {
        "executor_id": "D4_Q5_VerticalAlignmentValidator",
        "dimension": "D4",
        "question": "Q5",
        "canonical_label": "Validación de Alineación Vertical",
        "methods_count": 8,
        "epistemic_mix": ["structural", "consistency", "normative"],
    },
    {
        "executor_id": "D5_Q1_LongTermVisionAnalyzer",
        "dimension": "D5",
        "question": "Q1",
        "canonical_label": "Análisis de Visión de Largo Plazo",
        "methods_count": 8,
        "epistemic_mix": ["semantic", "normative", "temporal"],
    },
    {
        "executor_id": "D5_Q2_CompositeMeasurementValidator",
        "dimension": "D5",
        "question": "Q2",
        "canonical_label": "DIM05_Q02_COMPOSITE_PROXY_VALIDITY",
        "methods_count": 10,
        "epistemic_mix": ["statistical", "normative", "semantic"],
    },
    {
        "executor_id": "D5_Q3_IntangibleMeasurementAnalyzer",
        "dimension": "D5",
        "question": "Q3",
        "canonical_label": "Análisis de Medición Intangible",
        "methods_count": 9,
        "epistemic_mix": ["semantic", "normative", "bayesian"],
    },
    {
        "executor_id": "D5_Q4_SystemicRiskEvaluator",
        "dimension": "D5",
        "question": "Q4",
        "canonical_label": "Evaluación de Riesgo Sistémico",
        "methods_count": 12,
        "epistemic_mix": ["bayesian", "causal", "normative"],
    },
    {
        "executor_id": "D5_Q5_RealismAndSideEffectsAnalyzer",
        "dimension": "D5",
        "question": "Q5",
        "canonical_label": "Análisis de Realismo y Efectos Colaterales",
        "methods_count": 11,
        "epistemic_mix": ["causal", "bayesian", "normative"],
    },
    {
        "executor_id": "D6_Q1_ExplicitTheoryBuilder",
        "dimension": "D6",
        "question": "Q1",
        "canonical_label": "Constructor de Teoría Explícita",
        "methods_count": 15,
        "epistemic_mix": ["causal", "structural", "semantic"],
    },
    {
        "executor_id": "D6_Q2_LogicalProportionalityValidator",
        "dimension": "D6",
        "question": "Q2",
        "canonical_label": "Validación de Proporcionalidad Lógica",
        "methods_count": 10,
        "epistemic_mix": ["structural", "consistency", "normative"],
    },
    {
        "executor_id": "D6_Q3_ValidationTestingAnalyzer",
        "dimension": "D6",
        "question": "Q3",
        "canonical_label": "Análisis de Pruebas de Validación",
        "methods_count": 13,
        "epistemic_mix": ["causal", "bayesian", "statistical"],
    },
    {
        "executor_id": "D6_Q4_FeedbackLoopAnalyzer",
        "dimension": "D6",
        "question": "Q4",
        "canonical_label": "Análisis de Bucles de Retroalimentación",
        "methods_count": 9,
        "epistemic_mix": ["causal", "structural", "temporal"],
    },
    {
        "executor_id": "D6_Q5_ContextualAdaptabilityEvaluator",
        "dimension": "D6",
        "question": "Q5",
        "canonical_label": "Evaluación de Adaptabilidad Contextual",
        "methods_count": 10,
        "epistemic_mix": ["semantic", "normative", "causal"],
    },
]


def generate_executor_config(executor_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate complete executor config with runtime parameters only.
    
    NO calibration values (quality scores) are stored here.
    Calibration data is loaded from intrinsic_calibration.json.
    """
    methods_count = executor_def["methods_count"]
    
    timeout_base = 300
    if methods_count > 15:
        timeout_base = 600
    elif methods_count > 20:
        timeout_base = 900
    
    memory_limit_base = 512
    if "causal" in executor_def["epistemic_mix"] or "bayesian" in executor_def["epistemic_mix"]:
        memory_limit_base = 1024
    
    config = {
        "executor_id": executor_def["executor_id"],
        "dimension": executor_def["dimension"],
        "question": executor_def["question"],
        "canonical_label": executor_def["canonical_label"],
        "role": "SCORE_Q",
        "required_layers": [
            "@b",
            "@chain",
            "@q",
            "@d",
            "@p",
            "@C",
            "@u",
            "@m"
        ],
        "runtime_parameters": {
            "timeout_s": timeout_base,
            "retry": 3,
            "temperature": 0.0,
            "max_tokens": 4096,
            "memory_limit_mb": memory_limit_base,
            "enable_profiling": True,
            "seed": 42
        },
        "thresholds": {
            "min_quality_score": 0.5,
            "min_evidence_confidence": 0.7,
            "max_runtime_ms": timeout_base * 1000
        },
        "epistemic_mix": executor_def["epistemic_mix"],
        "contextual_params": {
            "expected_methods": methods_count,
            "critical_methods": [],
            "dimension_label": f"DIM0{executor_def['dimension'][1]}",
            "question_label": executor_def["canonical_label"]
        }
    }
    
    return config


def main():
    """Generate all 30 executor config files."""
    output_dir = Path(__file__).parent / "executor_configs"
    output_dir.mkdir(exist_ok=True)
    
    print(f"Generating {len(EXECUTOR_DEFINITIONS)} executor config files...")
    
    for executor_def in EXECUTOR_DEFINITIONS:
        config = generate_executor_config(executor_def)
        output_file = output_dir / f"{executor_def['executor_id']}.json"
        
        with open(output_file, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ {executor_def['executor_id']}.json")
    
    template_config = {
        "executor_id": "D{X}_Q{Y}_ExecutorName",
        "dimension": "D{X}",
        "question": "Q{Y}",
        "canonical_label": "Human-readable label",
        "role": "SCORE_Q",
        "required_layers": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],
        "runtime_parameters": {
            "timeout_s": 300,
            "retry": 3,
            "temperature": 0.0,
            "max_tokens": 4096,
            "memory_limit_mb": 512,
            "enable_profiling": True,
            "seed": 42
        },
        "thresholds": {
            "min_quality_score": 0.5,
            "min_evidence_confidence": 0.7,
            "max_runtime_ms": 300000
        },
        "epistemic_mix": ["semantic", "statistical", "normative"],
        "contextual_params": {
            "expected_methods": 10,
            "critical_methods": [],
            "dimension_label": "DIM0X",
            "question_label": "Label"
        }
    }
    
    template_file = output_dir / "executor_config_template.json"
    with open(template_file, "w") as f:
        json.dump(template_config, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ executor_config_template.json")
    print(f"\n✅ Generated {len(EXECUTOR_DEFINITIONS)} executor configs + 1 template")
    print(f"📁 Output directory: {output_dir}")
    print("\n⚠️  IMPORTANT: These files contain ONLY runtime parameters (HOW).")
    print("    Calibration data (WHAT quality scores) is loaded from:")
    print("    - src/cross_cutting_infrastructure/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json")
    print("    - canonic_questionnaire_central/questionnaire_monolith.json")


if __name__ == "__main__":
    main()
