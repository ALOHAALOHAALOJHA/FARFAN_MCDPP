#!/usr/bin/env python3
"""
CQVR v2.0 Batch Evaluation Script for Contracts Q026-Q050 (Batch 2)

This script evaluates 25 contracts using the CQVR v2.0 rubric and generates
individual evaluation reports following the same template as Batch 1.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent / "src"))

from farfan_pipeline.phases.Phase_two.contract_validator_cqvr import (
    CQVRValidator,
    ContractTriageDecision,
    TriageDecision,
)


CONTRACT_DIR = Path(__file__).parent / "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
REPORTS_DIR = Path(__file__).parent


def generate_detailed_report(
    contract_file: Path,
    contract: dict[str, Any],
    result: ContractTriageDecision
) -> str:
    question_id = contract.get("identity", {}).get("question_id", "UNKNOWN")
    
    status_icon = {
        TriageDecision.PRODUCCION: "✅",
        TriageDecision.PARCHEAR: "⚠️",
        TriageDecision.REFORMULAR: "❌"
    }
    
    icon = status_icon.get(result.decision, "❓")
    
    tier1_status = "✅ APROBADO" if result.score.tier1_score >= 35 else "❌ REPROBADO"
    tier2_status = "✅ APROBADO" if result.score.tier2_score >= 20 else "⚠️ BAJO"
    tier3_status = "✅ APROBADO" if result.score.tier3_score >= 8 else "⚠️ BAJO"
    total_status = "✅ PRODUCCIÓN" if result.score.total_score >= 80 else "⚠️ MEJORAR"
    
    verdict = ""
    if result.decision == TriageDecision.PRODUCCION:
        verdict = f"{icon} **CONTRATO APTO PARA PRODUCCIÓN**"
    elif result.decision == TriageDecision.PARCHEAR:
        verdict = f"{icon} **CONTRATO REQUIERE PARCHES** (parcheable)"
    else:
        verdict = f"{icon} **CONTRATO REQUIERE REFORMULACIÓN**"
    
    report = f"""# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: {contract_file.name}
**Fecha**: {datetime.now().strftime('%Y-%m-%d')}  
**Evaluador**: CQVR Batch Evaluator v2.0  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **{result.score.tier1_score:.1f}/{result.score.tier1_max:.0f}** | ≥35 | {tier1_status} |
| **TIER 2: Componentes Funcionales** | **{result.score.tier2_score:.1f}/{result.score.tier2_max:.0f}** | ≥20 | {tier2_status} |
| **TIER 3: Componentes de Calidad** | **{result.score.tier3_score:.1f}/{result.score.tier3_max:.0f}** | ≥8 | {tier3_status} |
| **TOTAL** | **{result.score.total_score:.1f}/{result.score.total_max:.0f}** | ≥80 | {total_status} |

**VEREDICTO**: {verdict}

El contrato {question_id}.v3.json alcanza {result.score.total_score:.1f}/100 puntos.

**Rationale**: {result.rationale}

---

## TIER 1: COMPONENTES CRÍTICOS - {result.score.tier1_score:.1f}/55 pts

### Desglose de Componentes

"""
    
    identity = contract.get("identity", {})
    output_schema = contract.get("output_contract", {}).get("schema", {})
    properties = output_schema.get("properties", {})
    
    report += f"""
#### A1. Coherencia Identity-Schema [20/20 pts máximo]

**Evaluación de campos críticos**:
"""
    
    fields_to_check = {
        "question_id": ("question_id", 5),
        "policy_area_id": ("policy_area_id", 5),
        "dimension_id": ("dimension_id", 5),
        "question_global": ("question_global", 3),
        "base_slot": ("base_slot", 2)
    }
    
    a1_score = 0.0
    for field, (name, pts) in fields_to_check.items():
        identity_val = identity.get(field)
        schema_val = properties.get(field, {}).get("const")
        match = "✅" if identity_val == schema_val else "❌"
        a1_score += pts if identity_val == schema_val else 0
        report += f"- {match} `{field}`: identity={identity_val}, schema={schema_val} [{pts} pts]\n"
    
    report += f"\n**Score A1**: {a1_score}/20 pts\n"
    
    method_binding = contract.get("method_binding", {})
    methods = method_binding.get("methods", [])
    evidence_assembly = contract.get("evidence_assembly", {})
    assembly_rules = evidence_assembly.get("assembly_rules", [])
    
    provides_set = {m.get("provides", "") for m in methods if m.get("provides")}
    sources_set = set()
    for rule in assembly_rules:
        for source in rule.get("sources", []):
            if isinstance(source, str) and not source.startswith("*."):
                sources_set.add(source)
    
    orphans = sources_set - provides_set
    
    report += f"""
#### A2. Alineación Method-Assembly [20/20 pts máximo]

**Evaluación**:
- Method count: {len(methods)} métodos declarados
- Provides declarations: {len(provides_set)} namespaces
- Assembly sources: {len(sources_set)} referencias
- Orphan sources: {len(orphans)} {'❌' if orphans else '✅'}
"""
    
    if orphans:
        report += f"  - Orphans: {list(orphans)[:5]}\n"
    
    a2_score_estimate = 20 - len(orphans) * 2 if len(orphans) < 10 else 0
    report += f"\n**Score A2**: ~{max(0, a2_score_estimate)}/20 pts\n"
    
    signal_reqs = contract.get("signal_requirements", {})
    mandatory_signals = signal_reqs.get("mandatory_signals", [])
    threshold = signal_reqs.get("minimum_signal_threshold", 0.0)
    
    report += f"""
#### A3. Integridad de Señales [10/10 pts máximo]

**Evaluación**:
- Mandatory signals: {len(mandatory_signals)} señales
- Signal threshold: {threshold}
- Status: {'✅ PASS' if threshold > 0 or not mandatory_signals else '❌ BLOCKER'}
"""
    
    if mandatory_signals and threshold <= 0:
        report += "\n**⚠️ BLOCKER CRÍTICO**: threshold = 0 con mandatory_signals definidas\n"
    
    a3_score = 10 if (threshold > 0 or not mandatory_signals) else 0
    report += f"\n**Score A3**: {a3_score}/10 pts\n"
    
    required = output_schema.get("required", [])
    all_defined = all(f in properties for f in required)
    
    report += f"""
#### A4. Validación de Output Schema [5/5 pts máximo]

**Evaluación**:
- Required fields: {len(required)}
- All fields defined: {'✅ YES' if all_defined else '❌ NO'}
"""
    
    if not all_defined:
        missing = [f for f in required if f not in properties]
        report += f"  - Missing: {missing}\n"
    
    a4_score = 5 if all_defined else max(0, 5 - len([f for f in required if f not in properties]))
    report += f"\n**Score A4**: {a4_score}/5 pts\n"
    
    report += f"""
---

## TIER 2: COMPONENTES FUNCIONALES - {result.score.tier2_score:.1f}/30 pts

### Desglose de Componentes

#### B1. Coherencia de Patrones [10/10 pts máximo]
"""
    
    question_context = contract.get("question_context", {})
    patterns = question_context.get("patterns", [])
    expected_elements = question_context.get("expected_elements", [])
    
    report += f"""
- Patterns defined: {len(patterns)}
- Expected elements: {len(expected_elements)}
- Pattern IDs unique: {'✅' if len(set(p.get('id', '') for p in patterns if isinstance(p, dict))) == len(patterns) else '❌'}
"""
    
    report += f"""
#### B2. Especificidad Metodológica [10/10 pts máximo]
"""
    
    methodological_depth = contract.get("methodological_depth", {})
    md_methods = methodological_depth.get("methods", [])
    
    report += f"""
- Methods documented: {len(md_methods)}
- Status: {'✅ Documented' if md_methods else '⚠️ Not documented'}
"""
    
    report += f"""
#### B3. Reglas de Validación [10/10 pts máximo]
"""
    
    validation_rules = contract.get("validation_rules", {})
    rules = validation_rules.get("rules", [])
    
    report += f"""
- Validation rules: {len(rules)}
- Status: {'✅ Configured' if rules else '❌ Missing'}
"""
    
    report += f"""
---

## TIER 3: COMPONENTES DE CALIDAD - {result.score.tier3_score:.1f}/15 pts

### Desglose de Componentes

#### C1. Documentación Epistemológica [5/5 pts máximo]
- Epistemological foundation: {'✅ Present' if methodological_depth.get('epistemological_foundation') else '⚠️ Missing'}

#### C2. Template Human-Readable [5/5 pts máximo]
"""
    
    template = contract.get("output_contract", {}).get("human_readable_output", {}).get("template", {})
    report += f"- Template configured: {'✅ YES' if template else '❌ NO'}\n"
    
    report += f"""
#### C3. Metadatos y Trazabilidad [5/5 pts máximo]
"""
    
    contract_hash = identity.get("contract_hash", "")
    created_at = identity.get("created_at", "")
    traceability = contract.get("traceability", {})
    source_hash = traceability.get("source_hash", "")
    
    report += f"""
- Contract hash: {'✅' if contract_hash and len(contract_hash) == 64 else '❌'}
- Created at: {'✅' if created_at else '❌'}
- Source hash: {'✅' if source_hash and not source_hash.startswith('TODO') else '⚠️'}
"""
    
    report += f"""
---

## BLOCKERS Y WARNINGS

### Blockers Críticos ({len(result.blockers)})
"""
    
    if result.blockers:
        for blocker in result.blockers:
            report += f"- ❌ {blocker}\n"
    else:
        report += "- ✅ No hay blockers críticos\n"
    
    report += f"""
### Warnings ({len(result.warnings)})
"""
    
    if result.warnings:
        for warning in result.warnings[:10]:
            report += f"- ⚠️ {warning}\n"
        if len(result.warnings) > 10:
            report += f"- ... y {len(result.warnings) - 10} warnings más\n"
    else:
        report += "- ✅ No hay warnings\n"
    
    report += f"""
---

## RECOMENDACIONES

"""
    
    if result.recommendations:
        for rec in result.recommendations:
            priority = rec.get("priority", "MEDIUM")
            component = rec.get("component", "")
            issue = rec.get("issue", "")
            fix = rec.get("fix", "")
            impact = rec.get("impact", "")
            
            report += f"""### {priority}: {component}
- **Issue**: {issue}
- **Fix**: {fix}
- **Impact**: {impact}

"""
    else:
        if result.decision == TriageDecision.PRODUCCION:
            report += "✅ No se requieren mejoras. El contrato está listo para producción.\n"
        else:
            report += f"""
Para mejorar el score:
1. Resolver blockers críticos listados arriba
2. Mejorar componentes con score bajo en Tier 1
3. Completar documentación metodológica si falta
"""
    
    report += f"""
---

## SCORE BREAKDOWN DETALLADO

| Componente | Score | Max | Percentage |
|-----------|-------|-----|------------|
| A1: Identity-Schema | {a1_score:.1f} | 20 | {a1_score/20*100:.1f}% |
| A2: Method-Assembly | ~{max(0, a2_score_estimate):.1f} | 20 | {max(0, a2_score_estimate)/20*100:.1f}% |
| A3: Signal Integrity | {a3_score:.1f} | 10 | {a3_score/10*100:.1f}% |
| A4: Output Schema | {a4_score:.1f} | 5 | {a4_score/5*100:.1f}% |
| **Tier 1 Total** | **{result.score.tier1_score:.1f}** | **55** | **{result.score.tier1_percentage:.1f}%** |
| Tier 2 | {result.score.tier2_score:.1f} | 30 | {result.score.tier2_percentage:.1f}% |
| Tier 3 | {result.score.tier3_score:.1f} | 15 | {result.score.tier3_percentage:.1f}% |
| **TOTAL** | **{result.score.total_score:.1f}** | **100** | **{result.score.total_percentage:.1f}%** |

---

## CONCLUSIÓN

{verdict}

**Generado**: {datetime.now().isoformat()}  
**Auditor**: CQVR Batch Evaluator v2.0  
**Rúbrica**: CQVR v2.0
"""
    
    return report


def evaluate_batch_2() -> dict[str, Any]:
    validator = CQVRValidator()
    
    results = {
        "batch": 2,
        "start_question": "Q026",
        "end_question": "Q050",
        "total_contracts": 25,
        "evaluated_at": datetime.now().isoformat(),
        "contracts": []
    }
    
    print("=" * 80)
    print("CQVR v2.0 Batch 2 Evaluation")
    print("Contracts: Q026-Q050 (25 contracts)")
    print("=" * 80)
    print()
    
    for q_num in range(26, 51):
        contract_file = CONTRACT_DIR / f"Q{q_num:03d}.v3.json"
        
        if not contract_file.exists():
            print(f"⚠️  {contract_file.name} - NOT FOUND")
            continue
        
        try:
            with open(contract_file, "r", encoding="utf-8") as f:
                contract = json.load(f)
            
            result = validator.validate_contract(contract)
            
            status_icon = {
                TriageDecision.PRODUCCION: "✅",
                TriageDecision.PARCHEAR: "⚠️",
                TriageDecision.REFORMULAR: "❌"
            }
            icon = status_icon.get(result.decision, "❓")
            
            print(f"{icon} {contract_file.name:20s} | "
                  f"Score: {result.score.total_score:5.1f}/100 | "
                  f"T1: {result.score.tier1_score:4.1f}/55 | "
                  f"Decision: {result.decision.value}")
            
            report_content = generate_detailed_report(contract_file, contract, result)
            report_file = REPORTS_DIR / f"Q{q_num:03d}_CQVR_EVALUATION_REPORT.md"
            
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            results["contracts"].append({
                "question_id": f"Q{q_num:03d}",
                "file": contract_file.name,
                "score": result.score.total_score,
                "tier1_score": result.score.tier1_score,
                "tier2_score": result.score.tier2_score,
                "tier3_score": result.score.tier3_score,
                "decision": result.decision.value,
                "blockers": len(result.blockers),
                "warnings": len(result.warnings),
                "report_file": report_file.name
            })
            
        except Exception as e:
            print(f"❌ {contract_file.name} - ERROR: {e}")
            results["contracts"].append({
                "question_id": f"Q{q_num:03d}",
                "file": contract_file.name,
                "error": str(e)
            })
    
    print()
    print("=" * 80)
    print("BATCH 2 SUMMARY")
    print("=" * 80)
    
    successful = [c for c in results["contracts"] if "error" not in c]
    produccion = [c for c in successful if c["decision"] == "PRODUCCION"]
    parchear = [c for c in successful if c["decision"] == "PARCHEAR"]
    reformular = [c for c in successful if c["decision"] == "REFORMULAR"]
    
    print(f"Total evaluated: {len(successful)}/{results['total_contracts']}")
    print(f"✅ PRODUCCIÓN: {len(produccion)} ({len(produccion)/len(successful)*100:.1f}%)")
    print(f"⚠️  PARCHEAR: {len(parchear)} ({len(parchear)/len(successful)*100:.1f}%)")
    print(f"❌ REFORMULAR: {len(reformular)} ({len(reformular)/len(successful)*100:.1f}%)")
    
    if successful:
        avg_score = sum(c["score"] for c in successful) / len(successful)
        avg_tier1 = sum(c["tier1_score"] for c in successful) / len(successful)
        print(f"\nAverage score: {avg_score:.1f}/100")
        print(f"Average Tier 1: {avg_tier1:.1f}/55")
    
    summary_file = REPORTS_DIR / "BATCH2_CQVR_SUMMARY.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Summary saved to: {summary_file}")
    print(f"✅ Individual reports generated: {len(successful)} files")
    
    return results


if __name__ == "__main__":
    results = evaluate_batch_2()
    sys.exit(0 if results["contracts"] else 1)
