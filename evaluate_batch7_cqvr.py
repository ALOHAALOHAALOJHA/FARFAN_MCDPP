#!/usr/bin/env python3
"""
CQVR v2.0 Batch Evaluator for Q151-Q175
Generates individual evaluation reports for each contract in batch 7.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Import the CQVR validator
sys.path.insert(0, str(Path(__file__).parent / "src"))
from farfan_pipeline.phases.Phase_two.phase2_g_contract_validator_cqvr import (
    CQVRValidator,
    TriageDecision,
)


def generate_cqvr_report(
    contract_path: Path, contract: dict[str, Any], validator: CQVRValidator
) -> str:
    """Generate a detailed CQVR v2.0 evaluation report for a contract."""
    
    question_id = contract.get("identity", {}).get("question_id", "UNKNOWN")
    
    triage_result = validator.validate_contract(contract)
    score = triage_result.score
    
    status_emoji = {
        TriageDecision.PRODUCCION: "✅",
        TriageDecision.PARCHEAR: "⚠️",
        TriageDecision.REFORMULAR: "❌"
    }
    
    tier1_status = "✅ APROBADO" if score.tier1_score >= 35 else "❌ REPROBADO"
    tier2_status = "✅ APROBADO" if score.tier2_score >= 20 else "❌ REPROBADO"
    tier3_status = "✅ APROBADO" if score.tier3_score >= 8 else "❌ REPROBADO"
    total_status = "✅ PRODUCCIÓN" if score.total_score >= 80 else "⚠️ MEJORAR" if score.total_score >= 60 else "❌ REFORMULAR"
    
    report = f"""# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: {question_id}.v3.json
**Fecha**: {datetime.now().strftime('%Y-%m-%d')}  
**Evaluador**: CQVR Batch Evaluator v2.0  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **{score.tier1_score:.1f}/55** | ≥35 | {tier1_status} |
| **TIER 2: Componentes Funcionales** | **{score.tier2_score:.1f}/30** | ≥20 | {tier2_status} |
| **TIER 3: Componentes de Calidad** | **{score.tier3_score:.1f}/15** | ≥8 | {tier3_status} |
| **TOTAL** | **{score.total_score:.1f}/100** | ≥80 | {total_status} |

**VEREDICTO**: {status_emoji[triage_result.decision]} **{triage_result.decision.value}**

{triage_result.rationale}

---

## TIER 1: COMPONENTES CRÍTICOS - {score.tier1_score:.1f}/55 pts {tier1_status}

### A1. Coherencia Identity-Schema [{score.component_scores.get('A1', 0):.1f}/20 pts]

**Evaluación de coherencia entre identity y output_contract.schema:**
"""
    
    identity = contract.get("identity", {})
    output_schema = contract.get("output_contract", {}).get("schema", {})
    properties = output_schema.get("properties", {})
    
    fields_to_check = ["question_id", "policy_area_id", "dimension_id", "question_global", "base_slot"]
    
    for field in fields_to_check:
        identity_value = identity.get(field)
        schema_value = properties.get(field, {}).get("const")
        match_status = "✅" if identity_value == schema_value else "❌"
        report += f"\n- {match_status} `{field}`: identity={identity_value}, schema={schema_value}"
    
    report += f"""

**Resultado**: {score.component_scores.get('A1', 0):.1f}/20 pts

---

### A2. Alineación Method-Assembly [{score.component_scores.get('A2', 0):.1f}/20 pts]

**Evaluación de alineación entre method_binding.methods y assembly_rules.sources:**
"""
    
    methods = contract.get("method_binding", {}).get("methods", [])
    assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
    
    provides_set = {m.get("provides", "") for m in methods if m.get("provides")}
    sources_set = set()
    for rule in assembly_rules:
        for source in rule.get("sources", []):
            if isinstance(source, str):
                sources_set.add(source)
            elif isinstance(source, dict):
                sources_set.add(source.get("namespace", ""))
    
    sources_set = {s for s in sources_set if s and not s.startswith("*.")}
    
    orphans = sources_set - provides_set
    unused = provides_set - sources_set
    
    report += f"""
- **Method count**: {len(methods)} (declared: {contract.get("method_binding", {}).get("method_count", 0)})
- **Provides defined**: {len(provides_set)}
- **Sources referenced**: {len(sources_set)}
- **Orphan sources** (not in provides): {len(orphans)}
- **Unused methods** (not in sources): {len(unused)}
"""
    
    if orphans:
        report += f"\n⚠️ **Orphan sources**: {list(orphans)[:3]}"
    if unused and len(unused) > len(provides_set) * 0.3:
        report += f"\n⚠️ **Many unused methods**: {len(unused)}/{len(provides_set)}"
    
    report += f"""

**Resultado**: {score.component_scores.get('A2', 0):.1f}/20 pts

---

### A3. Integridad de Señales [{score.component_scores.get('A3', 0):.1f}/10 pts]

**Evaluación de signal_requirements:**
"""
    
    signal_req = contract.get("signal_requirements", {})
    mandatory = signal_req.get("mandatory_signals", [])
    threshold = signal_req.get("minimum_signal_threshold", 0.0)
    aggregation = signal_req.get("signal_aggregation", "")
    
    report += f"""
- **Mandatory signals**: {len(mandatory)} defined
- **Minimum threshold**: {threshold}
- **Aggregation method**: {aggregation}
"""
    
    if mandatory and threshold <= 0:
        report += "\n❌ **BLOCKER**: threshold=0 with mandatory signals (allows zero-strength signals)"
    elif mandatory and threshold > 0:
        report += f"\n✅ Threshold properly configured: {threshold}"
    
    report += f"""

**Resultado**: {score.component_scores.get('A3', 0):.1f}/10 pts

---

### A4. Validación de Output Schema [{score.component_scores.get('A4', 0):.1f}/5 pts]

**Evaluación de output_contract.schema:**
"""
    
    required = output_schema.get("required", [])
    properties = output_schema.get("properties", {})
    
    all_defined = all(field in properties for field in required)
    missing = [f for f in required if f not in properties]
    
    report += f"""
- **Required fields**: {len(required)}
- **All defined in properties**: {"✅ Yes" if all_defined else f"❌ No (missing: {missing})"}
- **Source hash**: {contract.get("traceability", {}).get("source_hash", "")[:20]}...
"""
    
    report += f"""

**Resultado**: {score.component_scores.get('A4', 0):.1f}/5 pts

---

### TIER 1 SUBTOTAL: {score.tier1_score:.1f}/55 pts ({score.tier1_percentage:.1f}%)

**Estado**: {tier1_status}

---

## TIER 2: COMPONENTES FUNCIONALES - {score.tier2_score:.1f}/30 pts {tier2_status}

### B1. Coherencia de Patrones [{score.component_scores.get('B1', 0):.1f}/10 pts]

**Evaluación de patterns y expected_elements:**
"""
    
    patterns = contract.get("question_context", {}).get("patterns", [])
    expected = contract.get("question_context", {}).get("expected_elements", [])
    
    report += f"""
- **Patterns defined**: {len(patterns)}
- **Expected elements**: {len(expected)}
- **Required elements**: {len([e for e in expected if e.get("required")])}
"""
    
    confidence_weights = [p.get("confidence_weight") for p in patterns if isinstance(p, dict)]
    if confidence_weights:
        valid = all(0 <= w <= 1 for w in confidence_weights if w is not None)
        report += f"\n- **Confidence weights valid**: {'✅ Yes' if valid else '❌ No'}"
    
    report += f"""

**Resultado**: {score.component_scores.get('B1', 0):.1f}/10 pts

---

### B2. Especificidad Metodológica [{score.component_scores.get('B2', 0):.1f}/10 pts]

**Evaluación de methodological_depth:**
"""
    
    methodological = contract.get("methodological_depth", {})
    depth_methods = methodological.get("methods", [])
    
    report += f"""
- **Methods documented**: {len(depth_methods)}
- **Epistemological foundations**: {sum(1 for m in depth_methods if m.get("epistemological_foundation"))}
- **Technical approaches**: {sum(1 for m in depth_methods if m.get("technical_approach"))}
"""
    
    report += f"""

**Resultado**: {score.component_scores.get('B2', 0):.1f}/10 pts

---

### B3. Reglas de Validación [{score.component_scores.get('B3', 0):.1f}/10 pts]

**Evaluación de validation_rules:**
"""
    
    validation = contract.get("validation_rules", {})
    rules = validation.get("rules", [])
    failure = contract.get("error_handling", {}).get("failure_contract", {})
    
    report += f"""
- **Validation rules**: {len(rules)}
- **Failure contract defined**: {'✅ Yes' if failure.get("emit_code") else '❌ No'}
"""
    
    report += f"""

**Resultado**: {score.component_scores.get('B3', 0):.1f}/10 pts

---

### TIER 2 SUBTOTAL: {score.tier2_score:.1f}/30 pts ({score.tier2_percentage:.1f}%)

**Estado**: {tier2_status}

---

## TIER 3: COMPONENTES DE CALIDAD - {score.tier3_score:.1f}/15 pts {tier3_status}

### C1. Documentación Epistemológica [{score.component_scores.get('C1', 0):.1f}/5 pts]

**Evaluación de calidad de documentación metodológica.**

**Resultado**: {score.component_scores.get('C1', 0):.1f}/5 pts

---

### C2. Template Human-Readable [{score.component_scores.get('C2', 0):.1f}/5 pts]

**Evaluación de plantillas de salida legible.**

**Resultado**: {score.component_scores.get('C2', 0):.1f}/5 pts

---

### C3. Metadatos y Trazabilidad [{score.component_scores.get('C3', 0):.1f}/5 pts]

**Evaluación de metadatos:**
"""
    
    report += f"""
- **Contract hash**: {'✅' if identity.get('contract_hash') and len(identity.get('contract_hash', '')) == 64 else '❌'}
- **Created at**: {'✅' if identity.get('created_at') else '❌'}
- **Contract version**: {'✅' if identity.get('contract_version') else '❌'}
- **Source hash**: {'✅' if contract.get('traceability', {}).get('source_hash', '').startswith('TODO') == False else '⚠️ Placeholder'}
"""
    
    report += f"""

**Resultado**: {score.component_scores.get('C3', 0):.1f}/5 pts

---

### TIER 3 SUBTOTAL: {score.tier3_score:.1f}/15 pts ({score.tier3_percentage:.1f}%)

**Estado**: {tier3_status}

---

## SCORECARD FINAL

| Tier | Score | Max | Percentage | Estado |
|------|-------|-----|------------|--------|
| **TIER 1: Críticos** | {score.tier1_score:.1f} | 55 | {score.tier1_percentage:.1f}% | {tier1_status} |
| **TIER 2: Funcionales** | {score.tier2_score:.1f} | 30 | {score.tier2_percentage:.1f}% | {tier2_status} |
| **TIER 3: Calidad** | {score.tier3_score:.1f} | 15 | {score.tier3_percentage:.1f}% | {tier3_status} |
| **TOTAL** | **{score.total_score:.1f}** | **100** | **{score.total_percentage:.1f}%** | {total_status} |

---

## MATRIZ DE DECISIÓN CQVR

**DECISIÓN**: {status_emoji[triage_result.decision]} **{triage_result.decision.value}**

{triage_result.rationale}

---

## BLOCKERS Y WARNINGS

### Blockers Críticos ({len(triage_result.blockers)})
"""
    
    if triage_result.blockers:
        for blocker in triage_result.blockers:
            report += f"\n- ❌ {blocker}"
    else:
        report += "\n- ✅ No blockers detected"
    
    report += f"""

### Warnings ({len(triage_result.warnings)})
"""
    
    if triage_result.warnings:
        for warning in triage_result.warnings[:10]:
            report += f"\n- ⚠️ {warning}"
        if len(triage_result.warnings) > 10:
            report += f"\n- ... and {len(triage_result.warnings) - 10} more warnings"
    else:
        report += "\n- ✅ No warnings"
    
    report += f"""

---

## RECOMENDACIONES

"""
    
    if triage_result.recommendations:
        for i, rec in enumerate(triage_result.recommendations[:5], 1):
            report += f"""
### {i}. {rec.get('component', 'N/A')} - Prioridad {rec.get('priority', 'MEDIUM')}
- **Issue**: {rec.get('issue', 'N/A')}
- **Fix**: {rec.get('fix', 'N/A')}
- **Impact**: {rec.get('impact', 'N/A')}
"""
    else:
        if triage_result.decision == TriageDecision.PRODUCCION:
            report += "\n✅ No se requieren mejoras adicionales. El contrato cumple con todos los criterios de producción."
        elif triage_result.decision == TriageDecision.PARCHEAR:
            report += "\n⚠️ Se requieren correcciones menores. Ver blockers y warnings arriba."
        else:
            report += "\n❌ Se requiere reformulación completa. Tier 1 por debajo del umbral crítico."
    
    report += f"""

---

## CONCLUSIÓN

El contrato {question_id}.v3.json ha sido evaluado bajo la rúbrica CQVR v2.0:

- **Score total**: {score.total_score:.1f}/100 ({score.total_percentage:.1f}%)
- **Decisión**: {triage_result.decision.value}
- **Blockers críticos**: {len(triage_result.blockers)}
- **Warnings**: {len(triage_result.warnings)}

**Estado final**: {status_emoji[triage_result.decision]} {triage_result.decision.value}

---

**Generado**: {datetime.now().isoformat()}  
**Evaluador**: CQVR Batch Evaluator v2.0  
**Rúbrica**: CQVR v2.0 (100 puntos)
"""
    
    return report


def main():
    """Evaluate contracts Q151-Q175 and generate reports."""
    
    contracts_dir = Path(
        "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
    )
    
    output_dir = Path("cqvr_reports_batch7")
    output_dir.mkdir(exist_ok=True)
    
    validator = CQVRValidator()
    
    results = []
    
    for i in range(151, 176):
        contract_path = contracts_dir / f"Q{i}.v3.json"
        
        if not contract_path.exists():
            print(f"⚠️  Contract not found: {contract_path}")
            continue
        
        print(f"Evaluating {contract_path.name}...", end=" ")
        
        try:
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            
            validator.blockers = []
            validator.warnings = []
            validator.recommendations = []
            
            triage = validator.validate_contract(contract)
            
            score_components = {
                "A1": validator.verify_identity_schema_coherence(contract),
                "A2": validator.verify_method_assembly_alignment(contract),
                "A3": validator.verify_signal_requirements(contract),
                "A4": validator.verify_output_schema(contract),
                "B1": validator.verify_pattern_coverage(contract),
                "B2": validator.verify_method_specificity(contract),
                "B3": validator.verify_validation_rules(contract),
                "C1": validator.verify_documentation_quality(contract),
                "C2": validator.verify_human_template(contract),
                "C3": validator.verify_metadata_completeness(contract),
            }
            triage.score.component_scores = score_components
            
            report = generate_cqvr_report(contract_path, contract, validator)
            
            output_path = output_dir / f"Q{i}_CQVR_EVALUATION_REPORT.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            
            decision_emoji = {
                TriageDecision.PRODUCCION: "✅",
                TriageDecision.PARCHEAR: "⚠️",
                TriageDecision.REFORMULAR: "❌"
            }
            
            print(f"{decision_emoji[triage.decision]} {triage.score.total_score:.1f}/100 - {triage.decision.value}")
            
            results.append({
                "question_id": f"Q{i}",
                "score": triage.score.total_score,
                "decision": triage.decision.value,
                "tier1": triage.score.tier1_score,
                "tier2": triage.score.tier2_score,
                "tier3": triage.score.tier3_score,
                "blockers": len(triage.blockers),
                "warnings": len(triage.warnings)
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "question_id": f"Q{i}",
                "error": str(e)
            })
    
    summary_path = output_dir / "BATCH7_SUMMARY.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Evaluation complete!")
    print(f"   Reports generated in: {output_dir}/")
    print(f"   Summary: {summary_path}")
    
    production_ready = sum(1 for r in results if r.get("decision") == "PRODUCCION")
    patchable = sum(1 for r in results if r.get("decision") == "PARCHEAR")
    reformulate = sum(1 for r in results if r.get("decision") == "REFORMULAR")
    
    print(f"\n📊 Batch 7 Summary:")
    print(f"   ✅ Production Ready: {production_ready}/25")
    print(f"   ⚠️  Patchable: {patchable}/25")
    print(f"   ❌ Reformulate: {reformulate}/25")


if __name__ == "__main__":
    main()
