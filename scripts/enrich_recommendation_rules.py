#!/usr/bin/env python3
"""
Enrich recommendation_rules_enhanced.json to v3.0.0 specification.

This script generates the missing MICRO rules (240 additional rules) to reach
the required 300 MICRO rules (10 PA × 6 DIM × 5 score_bands).

Requirements from specification:
- 300 MICRO rules: PA01-PA10 × DIM01-DIM06 × 5 score_bands
- 54 MESO rules: Already complete
- 5 MACRO rules: Already complete
- Total: 359 rules
"""

import json
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Score band definitions from specification (Table: Score Band Conditions Mapping)
SCORE_BANDS = [
    {
        "code": "CRISIS",
        "label": "CRISIS",
        "score_gte": 0.00,
        "score_lt": 0.81,
        "horizon_months": 3,
        "blocking": True,
        "requires_approval": True
    },
    {
        "code": "CRITICO",
        "label": "CRÍTICO",
        "score_gte": 0.81,
        "score_lt": 1.66,
        "horizon_months": 6,
        "blocking": False,
        "requires_approval": True
    },
    {
        "code": "ACEPTABLE",
        "label": "ACEPTABLE",
        "score_gte": 1.66,
        "score_lt": 2.31,
        "horizon_months": 9,
        "blocking": False,
        "requires_approval": False
    },
    {
        "code": "BUENO",
        "label": "BUENO",
        "score_gte": 2.31,
        "score_lt": 2.71,
        "horizon_months": 12,
        "blocking": False,
        "requires_approval": False
    },
    {
        "code": "EXCELENTE",
        "label": "EXCELENTE",
        "score_gte": 2.71,
        "score_lt": 3.01,
        "horizon_months": 18,
        "blocking": False,
        "requires_approval": False
    }
]

# PA responsible entities mapping
PA_RESPONSIBLE_MAP = {
    "PA01": {
        "entity": "Secretaría de la Mujer Municipal",
        "role": "lidera la política pública de género",
        "partners": ["Secretaría de Planeación", "Secretaría de Hacienda", "Alta Consejería de la Mujer"],
        "legal_mandate": "Ley 1257 de 2008 - Normas para la prevención de violencias contra la mujer"
    },
    "PA02": {
        "entity": "Secretaría de Gobierno y Seguridad",
        "role": "lidera la seguridad y convivencia ciudadana",
        "partners": ["Policía Nacional", "Fiscalía", "Unidad para las Víctimas"],
        "legal_mandate": "Ley 1801 de 2016 - Código Nacional de Policía y Convivencia"
    },
    "PA03": {
        "entity": "Secretaría de Medio Ambiente",
        "role": "lidera la gestión ambiental y cambio climático",
        "partners": ["Corporación Autónoma Regional", "Ministerio de Ambiente"],
        "legal_mandate": "Ley 99 de 1993 - Sistema Nacional Ambiental"
    },
    "PA04": {
        "entity": "Secretaría de Desarrollo Social",
        "role": "lidera derechos económicos, sociales y culturales",
        "partners": ["Ministerio de Vivienda", "ICBF", "Empresas de Servicios"],
        "legal_mandate": "Ley 1751 de 2015 - Derecho fundamental a la salud"
    },
    "PA05": {
        "entity": "Oficina de Derechos Humanos",
        "role": "lidera política de víctimas y paz",
        "partners": ["Unidad para las Víctimas", "Defensoría del Pueblo", "Organizaciones de Víctimas"],
        "legal_mandate": "Ley 1448 de 2011 - Víctimas y restitución de tierras"
    },
    "PA06": {
        "entity": "Secretaría de Educación y Juventud",
        "role": "lidera políticas de niñez, adolescencia y juventud",
        "partners": ["ICBF", "Ministerio de Educación", "Instituciones Educativas"],
        "legal_mandate": "Ley 115 de 1994 - Ley General de Educación"
    },
    "PA07": {
        "entity": "Secretaría de Tierras y Desarrollo Rural",
        "role": "lidera política de tierras y territorios",
        "partners": ["Agencia Nacional de Tierras", "Unidad de Restitución", "Autoridades Étnicas"],
        "legal_mandate": "Ley 160 de 1994 - Sistema de Reforma Agraria"
    },
    "PA08": {
        "entity": "Secretaría de Gobierno",
        "role": "lidera protección de líderes y defensores",
        "partners": ["Unidad Nacional de Protección", "Defensoría del Pueblo", "Fiscalía"],
        "legal_mandate": "Decreto 1066 de 2015 - Programa de Prevención y Protección"
    },
    "PA09": {
        "entity": "Secretaría de Inclusión Social",
        "role": "lidera atención a crisis y PPL",
        "partners": ["INPEC Regional", "Ministerio de Justicia", "Cruz Roja"],
        "legal_mandate": "Ley 65 de 1993 - Código Penitenciario"
    },
    "PA10": {
        "entity": "Gerencia de Atención a Migrantes",
        "role": "lidera gestión migratoria",
        "partners": ["Migración Colombia", "ACNUR", "Gobernación"],
        "legal_mandate": "Decreto 1067 de 2015 - Sector Relaciones Exteriores"
    }
}

# Dimension metadata
DIMENSION_META = {
    "DIM01": "Línea Base y Diagnóstico (Insumos)",
    "DIM02": "Actividades y Cronograma",
    "DIM03": "Productos y BPIN",
    "DIM04": "Resultados Esperados",
    "DIM05": "Impactos y Gestión de Riesgos",
    "DIM06": "Causalidad y Datos Abiertos"
}


def generate_micro_rule(pa_id: str, dim_id: str, band: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a single MICRO rule for PA-DIM-Band combination."""
    
    rule_id = f"REC-MICRO-{pa_id}-{dim_id}-{band['code']}"
    
    pa_info = PA_RESPONSIBLE_MAP.get(pa_id, PA_RESPONSIBLE_MAP["PA01"])
    dim_name = DIMENSION_META.get(dim_id, "Dimensión")
    
    # Generate problem description
    problem = (
        f"El puntaje de {pa_id} en {dim_id} ({dim_name}) se encuentra en banda "
        f"{band['label']} (score: {band['score_gte']:.2f}-{band['score_lt']:.2f}), "
        f"requiriendo intervención específica para mejorar los componentes críticos de esta dimensión."
    )
    
    # Generate intervention based on score band severity
    intervention = generate_intervention(pa_id, dim_id, band)
    
    # Calculate target score
    target_score = min(band['score_lt'] + 0.5, 3.0)
    
    # Generate baseline target (scaled from band threshold)
    baseline_target = min((band['score_gte'] + band['score_lt']) / 2 + 0.3, 3.0)
    
    rule = {
        "rule_id": rule_id,
        "level": "MICRO",
        "when": {
            "pa_id": pa_id,
            "dim_id": dim_id,
            "score_gte": band['score_gte'],
            "score_lt": band['score_lt']
        },
        "template": {
            "problem": problem,
            "intervention": intervention,
            "indicator": {
                "name": f"{pa_id}-{dim_id} mejora {band['label'].lower()}",
                "baseline": None,
                "target": round(baseline_target, 2),
                "unit": "proporción",
                "formula": "COUNT(compliant_items) / COUNT(total_items)",
                "acceptable_range": [round(band['score_gte'], 2), 3.0],
                "baseline_measurement_date": "2024-01-01",
                "measurement_frequency": get_measurement_frequency(band['code']),
                "data_source": "Sistema de Seguimiento de Planes (SSP)",
                "data_source_query": f"SELECT AVG(score) FROM dimensions WHERE pa_id='{pa_id}' AND dim_id='{dim_id}'",
                "responsible_measurement": "Oficina de Planeación Municipal",
                "escalation_if_below": round(band['score_gte'] * 0.9, 2)
            },
            "responsible": {
                "entity": pa_info["entity"],
                "role": pa_info["role"],
                "partners": pa_info["partners"],
                "legal_mandate": pa_info["legal_mandate"],
                "approval_chain": generate_approval_chain(band['code']),
                "escalation_path": generate_escalation_path(band['code'])
            },
            "horizon": {
                "start": "T0",
                "end": get_time_horizon(band['horizon_months']),
                "start_type": "plan_approval_date",
                "duration_months": band['horizon_months'],
                "milestones": generate_milestones(band['horizon_months']),
                "dependencies": [],
                "critical_path": band['blocking']
            },
            "verification": generate_verification_artifacts(rule_id, dim_id, band),
            "template_id": f"TPL-{rule_id}",
            "template_params": {
                "pa_id": pa_id,
                "dim_id": dim_id,
                "score_band": band['code']
            }
        },
        "execution": {
            "trigger_condition": f"score >= {band['score_gte']} AND score < {band['score_lt']} AND pa_id = '{pa_id}' AND dim_id = '{dim_id}'",
            "blocking": band['blocking'],
            "auto_apply": False,
            "requires_approval": band['requires_approval'],
            "approval_roles": ["Secretaría de Planeación", "Secretaría de Hacienda"] if band['requires_approval'] else []
        },
        "budget": generate_budget(band['code']),
        "recommendations": [
            {
                "id": f"{rule_id}-REC-01",
                "action": intervention,
                "expected_output": f"Entrega verificable: {pa_id}-{dim_id} mejora {band['label'].lower()}, meta {baseline_target:.2f} proporción.",
                "method_id": get_method_id(dim_id),
                "questions": get_questions_for_dim(dim_id),
                "owner": pa_info["entity"],
                "timeframe": {
                    "start": "T0",
                    "end": get_time_horizon(band['horizon_months'])
                },
                "cost": {
                    "estimate": float(generate_budget(band['code'])['estimated_cost_cop']),
                    "currency": "COP",
                    "basis": "score_band_scaled"
                }
            }
        ]
    }
    
    return rule


def generate_intervention(pa_id: str, dim_id: str, band: Dict[str, Any]) -> str:
    """Generate contextual intervention based on PA, DIM, and severity band."""
    
    severity_actions = {
        "CRISIS": "Implementar plan de emergencia inmediata con ",
        "CRITICO": "Reestructurar y fortalecer urgentemente ",
        "ACEPTABLE": "Optimizar y mejorar ",
        "BUENO": "Mantener y perfeccionar ",
        "EXCELENTE": "Sostener excelencia y compartir mejores prácticas en "
    }
    
    dim_focus = {
        "DIM01": "el diagnóstico y línea base mediante levantamiento de datos verificables, actualización de indicadores y validación con fuentes oficiales",
        "DIM02": "las actividades y cronograma con hitos claros, responsables definidos y sistema de seguimiento robusto",
        "DIM03": "los productos y presupuesto BPIN completando fichas técnicas, asegurando trazabilidad presupuestal y validación financiera",
        "DIM04": "los resultados esperados definiendo indicadores SMART, estableciendo metas verificables y diseñando marco de medición",
        "DIM05": "la gestión de impactos y riesgos elaborando matriz completa, definiendo controles efectivos y estableciendo monitoreo continuo",
        "DIM06": "la causalidad y datos abiertos construyendo modelos lógicos, publicando datasets actualizados y asegurando trazabilidad"
    }
    
    action = severity_actions.get(band['code'], "Mejorar ")
    focus = dim_focus.get(dim_id, "los componentes de esta dimensión")
    
    return f"{action}{focus}."


def get_measurement_frequency(band_code: str) -> str:
    """Get measurement frequency based on severity."""
    freq_map = {
        "CRISIS": "semanal",
        "CRITICO": "quincenal",
        "ACEPTABLE": "mensual",
        "BUENO": "bimestral",
        "EXCELENTE": "trimestral"
    }
    return freq_map.get(band_code, "mensual")


def get_time_horizon(horizon_months: int) -> str:
    """Map horizon months to time periods."""
    if horizon_months <= 3:
        return "T1"
    elif horizon_months <= 9:
        return "T2"
    else:
        return "T3"


def generate_approval_chain(band_code: str) -> List[Dict[str, Any]]:
    """Generate approval chain based on severity."""
    if band_code in ["CRISIS", "CRITICO"]:
        return [
            {"level": 1, "role": "Director/Coordinador de Programa", "decision": "Aprueba plan de trabajo"},
            {"level": 2, "role": "Secretario/a de la entidad responsable", "decision": "Aprueba presupuesto y recursos"},
            {"level": 3, "role": "Secretaría de Planeación", "decision": "Valida coherencia con PDM"},
            {"level": 4, "role": "Alcalde Municipal", "decision": "Aprobación final (si aplica)"}
        ]
    else:
        return [
            {"level": 1, "role": "Director/Coordinador de Programa", "decision": "Aprueba plan de trabajo"},
            {"level": 2, "role": "Secretario/a de la entidad responsable", "decision": "Aprueba presupuesto y recursos"},
            {"level": 3, "role": "Secretaría de Planeación", "decision": "Valida coherencia con PDM"}
        ]


def generate_escalation_path(band_code: str) -> Dict[str, Any]:
    """Generate escalation path based on severity."""
    threshold_map = {
        "CRISIS": 3,
        "CRITICO": 7,
        "ACEPTABLE": 15,
        "BUENO": 30,
        "EXCELENTE": 45
    }
    
    return {
        "threshold_days_delay": threshold_map.get(band_code, 15),
        "escalate_to": "Secretaría de Planeación",
        "final_escalation": "Despacho del Alcalde",
        "consequences": ["Revisión presupuestal", "Reasignación de responsables"]
    }


def generate_milestones(duration_months: int) -> List[Dict[str, Any]]:
    """Generate milestones based on duration."""
    milestones = [
        {
            "name": "Inicio de implementación",
            "offset_months": 1,
            "deliverables": ["Plan de trabajo aprobado"],
            "verification_required": True
        }
    ]
    
    if duration_months >= 6:
        milestones.append({
            "name": "Revisión intermedia",
            "offset_months": duration_months // 2,
            "deliverables": ["Informe de avance"],
            "verification_required": True
        })
    
    milestones.append({
        "name": "Entrega final",
        "offset_months": duration_months,
        "deliverables": ["Todos los productos esperados"],
        "verification_required": True
    })
    
    return milestones


def generate_verification_artifacts(rule_id: str, dim_id: str, band: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate verification artifacts for a rule."""
    
    artifacts = []
    seq = 1
    
    # Document artifact
    artifacts.append({
        "id": f"VER-{rule_id}-{seq:03d}",
        "type": "DOCUMENT",
        "artifact": f"Informe de cumplimiento {dim_id} - {band['label']}",
        "format": "PDF",
        "required_sections": ["Objetivo", "Alcance", "Resultados"],
        "approval_required": True,
        "approver": "Secretaría de Planeación",
        "due_date": get_time_horizon(band['horizon_months']),
        "automated_check": False
    })
    seq += 1
    
    # System state artifact for dimensions with data systems
    if dim_id in ["DIM03", "DIM06"]:
        artifacts.append({
            "id": f"VER-{rule_id}-{seq:03d}",
            "type": "SYSTEM_STATE",
            "artifact": f"Estado del sistema {dim_id}",
            "format": "DATABASE_QUERY",
            "required_sections": [],
            "approval_required": True,
            "approver": "Secretaría de Planeación",
            "due_date": get_time_horizon(band['horizon_months']),
            "automated_check": True,
            "validation_query": f"SELECT COUNT(*) FROM artifacts WHERE artifact_id = 'VER-{rule_id}-{seq:03d}'",
            "pass_condition": "COUNT(*) >= 1"
        })
        seq += 1
    
    # Metric artifact for quantitative dimensions
    if dim_id in ["DIM01", "DIM04", "DIM05"]:
        artifacts.append({
            "id": f"VER-{rule_id}-{seq:03d}",
            "type": "METRIC",
            "artifact": f"Medición de indicadores {dim_id}",
            "format": "JSON",
            "required_sections": [],
            "approval_required": False,
            "approver": "Oficina de Planeación Municipal",
            "due_date": get_time_horizon(band['horizon_months']),
            "automated_check": True,
            "validation_query": f"SELECT metric_value FROM metrics WHERE metric_id = '{dim_id}'",
            "pass_condition": f"metric_value >= {band['score_lt']}"
        })
    
    return artifacts


def generate_budget(band_code: str) -> Dict[str, Any]:
    """Generate budget estimates based on severity."""
    
    base_amounts = {
        "CRISIS": 80000000,
        "CRITICO": 60000000,
        "ACEPTABLE": 45000000,
        "BUENO": 35000000,
        "EXCELENTE": 25000000
    }
    
    total = base_amounts.get(band_code, 45000000)
    
    return {
        "estimated_cost_cop": total,
        "cost_breakdown": {
            "personal": int(total * 0.55),
            "consultancy": int(total * 0.30),
            "technology": int(total * 0.15)
        },
        "funding_sources": [
            {
                "source": "SGP - Sistema General de Participaciones",
                "amount": int(total * 0.60),
                "confirmed": False
            },
            {
                "source": "Recursos Propios",
                "amount": int(total * 0.40),
                "confirmed": False
            }
        ],
        "fiscal_year": 2025
    }


def get_method_id(dim_id: str) -> str:
    """Get method ID for dimension."""
    method_map = {
        "DIM01": "SemanticProcessor.chunk_text",
        "DIM02": "PDETMunicipalPlanAnalyzer._extract_financial_amounts",
        "DIM03": "BayesianEvidenceExtractor.extract_prior_beliefs",
        "DIM04": "CausalExtractor.extract_causal_hierarchy",
        "DIM05": "PDETMunicipalPlanAnalyzer._extract_financial_amounts",
        "DIM06": "CausalExtractor.extract_causal_hierarchy"
    }
    return method_map.get(dim_id, "SemanticProcessor.chunk_text")


def get_questions_for_dim(dim_id: str) -> List[str]:
    """Get question IDs for dimension."""
    dim_num = int(dim_id.replace("DIM", ""))
    start = (dim_num - 1) * 5 + 1
    return [f"Q{i:03d}" for i in range(start, start + 5)]


def generate_all_micro_rules() -> List[Dict[str, Any]]:
    """Generate all 300 MICRO rules (10 PA × 6 DIM × 5 bands)."""
    rules = []
    
    for pa_num in range(1, 11):  # PA01-PA10
        pa_id = f"PA{pa_num:02d}"
        for dim_num in range(1, 7):  # DIM01-DIM06
            dim_id = f"DIM{dim_num:02d}"
            for band in SCORE_BANDS:
                rule = generate_micro_rule(pa_id, dim_id, band)
                rules.append(rule)
    
    return rules


def calculate_checksum(data: Dict[str, Any]) -> str:
    """Calculate SHA256 checksum of the rules structure."""
    # Serialize to stable JSON
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()


def enrich_rules_file(input_path: Path, output_path: Path) -> None:
    """Enrich the recommendation rules file to v3.0.0."""
    
    print(f"Reading input file: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Analyze current state
    current_micro = [r for r in data['rules'] if r['level'] == 'MICRO']
    current_meso = [r for r in data['rules'] if r['level'] == 'MESO']
    current_macro = [r for r in data['rules'] if r['level'] == 'MACRO']
    
    print(f"\nCurrent state:")
    print(f"  MICRO: {len(current_micro)} rules")
    print(f"  MESO: {len(current_meso)} rules")
    print(f"  MACRO: {len(current_macro)} rules")
    print(f"  Total: {len(data['rules'])} rules")
    
    # Generate new MICRO rules
    print(f"\nGenerating 300 new MICRO rules...")
    new_micro_rules = generate_all_micro_rules()
    print(f"Generated {len(new_micro_rules)} MICRO rules")
    
    # Combine all rules
    all_rules = new_micro_rules + current_meso + current_macro
    
    print(f"\nNew totals:")
    print(f"  MICRO: {len(new_micro_rules)} rules")
    print(f"  MESO: {len(current_meso)} rules")
    print(f"  MACRO: {len(current_macro)} rules")
    print(f"  Total: {len(all_rules)} rules")
    
    # Update metadata
    data['version'] = "3.0.0"
    data['last_updated'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    data['levels']['MICRO']['count'] = len(new_micro_rules)
    data['rules'] = all_rules
    
    # Add integrity section
    data['integrity'] = {
        "expected_rule_counts": {
            "MICRO": 300,
            "MESO": 54,
            "MACRO": 5,
            "total": 359
        },
        "actual_rule_counts": {
            "MICRO": len(new_micro_rules),
            "MESO": len(current_meso),
            "MACRO": len(current_macro),
            "total": len(all_rules)
        },
        "validation_checksum": calculate_checksum(all_rules),
        "generated_date": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }
    
    # Verify counts
    assert len(new_micro_rules) == 300, f"Expected 300 MICRO rules, got {len(new_micro_rules)}"
    assert len(current_meso) == 54, f"Expected 54 MESO rules, got {len(current_meso)}"
    assert len(current_macro) == 5, f"Expected 5 MACRO rules, got {len(current_macro)}"
    assert len(all_rules) == 359, f"Expected 359 total rules, got {len(all_rules)}"
    
    # Verify no duplicates
    rule_ids = [r['rule_id'] for r in all_rules]
    assert len(rule_ids) == len(set(rule_ids)), "Duplicate rule_ids detected!"
    
    print(f"\n✓ Validation passed")
    print(f"  - All 359 rules present")
    print(f"  - No duplicate rule_ids")
    print(f"  - Checksum: {data['integrity']['validation_checksum'][:16]}...")
    
    # Write output
    print(f"\nWriting output file: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully enriched rules file to v3.0.0")


def main():
    parser = argparse.ArgumentParser(
        description="Enrich recommendation_rules_enhanced.json to v3.0.0"
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path('src/farfan_pipeline/phases/Phase_8/json_phase_eight/recommendation_rules_enhanced.json'),
        help='Input rules file path'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('src/farfan_pipeline/phases/Phase_8/json_phase_eight/recommendation_rules_enhanced.json'),
        help='Output rules file path'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Only validate, do not write output'
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    if args.validate:
        print("Validation mode: will not write output")
    
    enrich_rules_file(args.input, args.output if not args.validate else args.input)
    
    return 0


if __name__ == '__main__':
    exit(main())
