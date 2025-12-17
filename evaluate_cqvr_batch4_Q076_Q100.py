#!/usr/bin/env python3
"""
CQVR v2.0 Batch Evaluator for Q076-Q100 (Batch 4)
Generates individual CQVR evaluation reports and batch summary
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent / "src"))

from farfan_pipeline.phases.Phase_two.contract_validator_cqvr import (
    CQVRValidator,
    TriageDecision,
)


def load_contract(contract_path: Path) -> dict[str, Any]:
    """Load contract JSON file."""
    with open(contract_path, encoding="utf-8") as f:
        return json.load(f)


def generate_report_content(
    question_id: str,
    contract: dict[str, Any],
    validator: CQVRValidator,
) -> str:
    """Generate CQVR evaluation report content."""
    decision = validator.validate_contract(contract)
    score = decision.score
    
    status_emoji = {
        TriageDecision.PRODUCCION: "✅",
        TriageDecision.PARCHEAR: "⚠️",
        TriageDecision.REFORMULAR: "❌",
    }
    
    def status_check(value: float, threshold: float) -> str:
        return "✅ APROBADO" if value >= threshold else "❌ REPROBADO"
    
    def verdict_status(total: float) -> str:
        if total >= 80:
            return "✅ PRODUCCIÓN"
        elif total >= 60:
            return "⚠️ REQUIERE MEJORAS"
        else:
            return "❌ NO APTO"
    
    identity = contract.get("identity", {})
    base_slot = identity.get("base_slot", "UNKNOWN")
    question_global = identity.get("question_global", "?")
    
    report = f"""# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: {question_id}.v3.json
**Fecha**: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}  
**Evaluador**: CQVR Batch Evaluator (Batch 4)  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **{score.tier1_score:.1f}/{score.tier1_max:.0f}** | ≥35 | {status_check(score.tier1_score, 35)} |
| **TIER 2: Componentes Funcionales** | **{score.tier2_score:.1f}/{score.tier2_max:.0f}** | ≥20 | {status_check(score.tier2_score, 20)} |
| **TIER 3: Componentes de Calidad** | **{score.tier3_score:.1f}/{score.tier3_max:.0f}** | ≥8 | {status_check(score.tier3_score, 8)} |
| **TOTAL** | **{score.total_score:.1f}/{score.total_max:.0f}** | ≥80 | {verdict_status(score.total_score)} |

**VEREDICTO**: {status_emoji[decision.decision]} **{decision.decision.value}**

{decision.rationale}

---

## TIER 1: COMPONENTES CRÍTICOS - {score.tier1_score:.1f}/{score.tier1_max:.0f} pts

### A1. Coherencia Identity-Schema [{score.component_scores.get('A1', 0):.1f}/20 pts]

**Evaluación**:
```python
identity = {{
    "base_slot": "{base_slot}",
    "question_id": "{identity.get('question_id', 'UNKNOWN')}",
    "dimension_id": "{identity.get('dimension_id', 'UNKNOWN')}",
    "policy_area_id": "{identity.get('policy_area_id', 'UNKNOWN')}",
    "question_global": {question_global}
}}
```

**Análisis**: {'✅ Coherencia perfecta entre identity y output_schema' if score.component_scores.get('A1', 0) >= 15 else '⚠️ Requiere correcciones en identity-schema'}

---

### A2. Alineación Method-Assembly [{score.component_scores.get('A2', 0):.1f}/20 pts]

**Evaluación**:
- Método count: {contract.get('method_binding', {}).get('method_count', 0)}
- Métodos definidos: {len(contract.get('method_binding', {}).get('methods', []))}

**Análisis**: {'✅ Alineación correcta entre provides y assembly sources' if score.component_scores.get('A2', 0) >= 15 else '⚠️ Requiere revisión de method-assembly alignment'}

---

### A3. Integridad de Señales [{score.component_scores.get('A3', 0):.1f}/10 pts]

**Evaluación**:
```python
signal_requirements = {{
    "mandatory_signals": {len(contract.get('signal_requirements', {}).get('mandatory_signals', []))} señales,
    "minimum_signal_threshold": {contract.get('signal_requirements', {}).get('minimum_signal_threshold', 0.0)},
    "signal_aggregation": "{contract.get('signal_requirements', {}).get('signal_aggregation', 'unknown')}"
}}
```

**Análisis**: {'✅ Threshold > 0 con mandatory_signals' if score.component_scores.get('A3', 0) >= 5 else '❌ BLOCKER: threshold debe ser > 0'}

---

### A4. Validación de Output Schema [{score.component_scores.get('A4', 0):.1f}/5 pts]

**Evaluación**:
- Required fields: {len(contract.get('output_contract', {}).get('schema', {}).get('required', []))}
- Properties defined: {len(contract.get('output_contract', {}).get('schema', {}).get('properties', {}))}

**Análisis**: {'✅ Schema bien definido' if score.component_scores.get('A4', 0) >= 3 else '⚠️ Requiere mejoras en schema'}

---

## TIER 2: COMPONENTES FUNCIONALES - {score.tier2_score:.1f}/{score.tier2_max:.0f} pts

### B1. Coherencia de Patrones [{score.component_scores.get('B1', 0):.1f}/10 pts]

**Evaluación**:
- Patrones definidos: {len(contract.get('question_context', {}).get('patterns', []))}
- Expected elements: {len(contract.get('question_context', {}).get('expected_elements', []))}

**Análisis**: {'✅ Cobertura adecuada de patrones' if score.component_scores.get('B1', 0) >= 7 else '⚠️ Requiere más patrones'}

---

### B2. Especificidad Metodológica [{score.component_scores.get('B2', 0):.1f}/10 pts]

**Análisis**: {'✅ Documentación metodológica completa' if score.component_scores.get('B2', 0) >= 7 else '⚠️ Requiere documentación más específica'}

---

### B3. Reglas de Validación [{score.component_scores.get('B3', 0):.1f}/10 pts]

**Evaluación**:
- Validation rules: {len(contract.get('validation_rules', {}).get('rules', []))}
- NA policy: "{contract.get('validation_rules', {}).get('na_policy', 'not_set')}"

**Análisis**: {'✅ Validation rules correctas' if score.component_scores.get('B3', 0) >= 7 else '⚠️ Requiere mejoras en validation rules'}

---

## TIER 3: COMPONENTES DE CALIDAD - {score.tier3_score:.1f}/{score.tier3_max:.0f} pts

### C1. Documentación Epistemológica [{score.component_scores.get('C1', 0):.1f}/5 pts]

**Análisis**: {'✅ Documentación epistemológica robusta' if score.component_scores.get('C1', 0) >= 3 else '⚠️ Requiere documentación epistemológica'}

---

### C2. Template Human-Readable [{score.component_scores.get('C2', 0):.1f}/5 pts]

**Análisis**: {'✅ Template bien definido' if score.component_scores.get('C2', 0) >= 3 else '⚠️ Requiere mejoras en template'}

---

### C3. Metadatos y Trazabilidad [{score.component_scores.get('C3', 0):.1f}/5 pts]

**Evaluación**:
- contract_hash: {"✅ Presente" if identity.get('contract_hash') else "❌ Faltante"}
- created_at: {"✅ Presente" if identity.get('created_at') else "❌ Faltante"}
- source_hash: {"✅ Presente" if not contract.get('traceability', {}).get('source_hash', '').startswith('TODO') else "⚠️ Placeholder"}

---

## SCORECARD FINAL

| Tier | Score | Max | Percentage |
|------|-------|-----|------------|
| **TIER 1** | **{score.tier1_score:.1f}** | **{score.tier1_max:.0f}** | **{score.tier1_percentage:.1f}%** |
| **TIER 2** | **{score.tier2_score:.1f}** | **{score.tier2_max:.0f}** | **{score.tier2_percentage:.1f}%** |
| **TIER 3** | **{score.tier3_score:.1f}** | **{score.tier3_max:.0f}** | **{score.tier3_percentage:.1f}%** |
| **TOTAL** | **{score.total_score:.1f}** | **{score.total_max:.0f}** | **{score.total_percentage:.1f}%** |

---

## MATRIZ DE DECISIÓN CQVR

```
TIER 1 Score: {score.tier1_score:.1f}/{score.tier1_max:.0f} ({score.tier1_percentage:.1f}%) {status_check(score.tier1_score, 35)}
TIER 2 Score: {score.tier2_score:.1f}/{score.tier2_max:.0f} ({score.tier2_percentage:.1f}%) {status_check(score.tier2_score, 20)}
TOTAL Score:  {score.total_score:.1f}/{score.total_max:.0f} ({score.total_percentage:.1f}%)  {verdict_status(score.total_score)}

DECISIÓN: {status_emoji[decision.decision]} {decision.decision.value}
```

### Criterios de Decisión:
- {'✅' if score.tier1_score >= 35 else '❌'} Tier 1 ≥ 35/55 (63.6%) → **{score.tier1_score:.1f}/55 ({score.tier1_percentage:.1f}%)**
- {'✅' if score.tier2_score >= 20 else '❌'} Tier 2 ≥ 20/30 (66.7%) → **{score.tier2_score:.1f}/30 ({score.tier2_percentage:.1f}%)**
- {'✅' if score.total_score >= 80 else '❌'} Total ≥ 80/100 → **{score.total_score:.1f}/100**

---

## BLOCKERS IDENTIFICADOS

{chr(10).join(f"- ❌ {blocker}" for blocker in decision.blockers) if decision.blockers else "✅ No se identificaron blockers críticos"}

---

## ADVERTENCIAS

{chr(10).join(f"- ⚠️ {warning}" for warning in decision.warnings) if decision.warnings else "✅ No se identificaron advertencias"}

---

## RECOMENDACIONES

{chr(10).join(f"### {i+1}. {rec.get('title', 'Recomendación')}{chr(10)}{rec.get('description', '')}{chr(10)}" for i, rec in enumerate(decision.recommendations)) if decision.recommendations else "No se requieren acciones adicionales en este momento."}

---

## CONCLUSIÓN

### Veredicto Final: {status_emoji[decision.decision]} **{decision.decision.value}**

**Justificación**:
- Score total: {score.total_score:.1f}/100 ({score.total_percentage:.1f}%)
- Tier 1 (Crítico): {score.tier1_score:.1f}/55 ({score.tier1_percentage:.1f}%)
- Tier 2 (Funcional): {score.tier2_score:.1f}/30 ({score.tier2_percentage:.1f}%)
- Tier 3 (Calidad): {score.tier3_score:.1f}/15 ({score.tier3_percentage:.1f}%)

{decision.rationale}

---

**Firma Digital CQVR**:  
Hash: `{score.total_score:.0f}/100-T1:{score.tier1_score:.0f}-T2:{score.tier2_score:.0f}-T3:{score.tier3_score:.0f}-{decision.decision.value}`  
Timestamp: `{datetime.now(timezone.utc).isoformat()}`  
Evaluator: `CQVR-Batch-Evaluator-v2.0`  
Status: `{status_emoji[decision.decision]} {decision.decision.value}`
"""
    
    return report


def main() -> None:
    """Main execution function."""
    contracts_dir = Path("src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized")
    output_dir = Path("artifacts/cqvr_reports/batch4_Q076_Q100")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    start_q = 76
    end_q = 100
    
    validator = CQVRValidator()
    results = []
    
    print(f"🔍 CQVR v2.0 Batch Evaluator - Batch 4 (Q{start_q:03d}-Q{end_q:03d})")
    print(f"📂 Contracts directory: {contracts_dir}")
    print(f"📁 Output directory: {output_dir}")
    print("=" * 80)
    
    for q_num in range(start_q, end_q + 1):
        question_id = f"Q{q_num:03d}"
        contract_path = contracts_dir / f"{question_id}.v3.json"
        
        if not contract_path.exists():
            print(f"⚠️  {question_id}: Contract file not found")
            continue
        
        try:
            print(f"\n📋 Evaluating {question_id}...")
            contract = load_contract(contract_path)
            decision = validator.validate_contract(contract)
            score = decision.score
            
            report_content = generate_report_content(question_id, contract, validator)
            
            report_path = output_dir / f"{question_id}_CQVR_EVALUATION_REPORT.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            status_emoji = {
                TriageDecision.PRODUCCION: "✅",
                TriageDecision.PARCHEAR: "⚠️",
                TriageDecision.REFORMULAR: "❌",
            }
            
            print(f"   {status_emoji[decision.decision]} {decision.decision.value}")
            print(f"   Score: {score.total_score:.1f}/100 (T1:{score.tier1_score:.1f}/55, T2:{score.tier2_score:.1f}/30, T3:{score.tier3_score:.1f}/15)")
            print(f"   Report: {report_path.name}")
            
            results.append({
                "question_id": question_id,
                "decision": decision.decision.value,
                "total_score": score.total_score,
                "tier1_score": score.tier1_score,
                "tier2_score": score.tier2_score,
                "tier3_score": score.tier3_score,
                "blockers_count": len(decision.blockers),
                "warnings_count": len(decision.warnings),
            })
            
        except Exception as e:
            print(f"❌ {question_id}: Error during evaluation - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print(f"✅ Batch evaluation complete: {len(results)}/{end_q - start_q + 1} contracts evaluated")
    
    summary_path = output_dir / "BATCH4_SUMMARY.md"
    generate_summary_report(results, summary_path, start_q, end_q)
    print(f"📊 Summary report: {summary_path}")
    
    summary_json_path = output_dir / "BATCH4_SUMMARY.json"
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"📄 JSON summary: {summary_json_path}")


def generate_summary_report(results: list[dict], output_path: Path, start_q: int, end_q: int) -> None:
    """Generate batch summary report."""
    total_contracts = len(results)
    produccion_count = sum(1 for r in results if r["decision"] == "PRODUCCION")
    parchear_count = sum(1 for r in results if r["decision"] == "PARCHEAR")
    reformular_count = sum(1 for r in results if r["decision"] == "REFORMULAR")
    
    avg_total = sum(r["total_score"] for r in results) / total_contracts if total_contracts > 0 else 0
    avg_tier1 = sum(r["tier1_score"] for r in results) / total_contracts if total_contracts > 0 else 0
    avg_tier2 = sum(r["tier2_score"] for r in results) / total_contracts if total_contracts > 0 else 0
    avg_tier3 = sum(r["tier3_score"] for r in results) / total_contracts if total_contracts > 0 else 0
    
    total_blockers = sum(r["blockers_count"] for r in results)
    total_warnings = sum(r["warnings_count"] for r in results)
    
    summary = f"""# 📊 CQVR v2.0 Batch 4 Summary Report
## Contracts Q{start_q:03d}-Q{end_q:03d}

**Date**: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}  
**Evaluator**: CQVR Batch Evaluator v2.0  
**Total Contracts**: {total_contracts}

---

## EXECUTIVE SUMMARY

| Metric | Count | Percentage |
|--------|-------|------------|
| ✅ **PRODUCCIÓN** | {produccion_count} | {produccion_count/total_contracts*100:.1f}% |
| ⚠️ **PARCHEAR** | {parchear_count} | {parchear_count/total_contracts*100:.1f}% |
| ❌ **REFORMULAR** | {reformular_count} | {reformular_count/total_contracts*100:.1f}% |

---

## AVERAGE SCORES

| Tier | Average Score | Max | Percentage |
|------|---------------|-----|------------|
| **Tier 1** | {avg_tier1:.1f} | 55 | {avg_tier1/55*100:.1f}% |
| **Tier 2** | {avg_tier2:.1f} | 30 | {avg_tier2/30*100:.1f}% |
| **Tier 3** | {avg_tier3:.1f} | 15 | {avg_tier3/15*100:.1f}% |
| **TOTAL** | {avg_total:.1f} | 100 | {avg_total:.1f}% |

---

## ISSUES SUMMARY

- 🚫 **Total Blockers**: {total_blockers}
- ⚠️ **Total Warnings**: {total_warnings}

---

## DETAILED RESULTS

| Question ID | Decision | Total Score | T1 | T2 | T3 | Blockers | Warnings |
|-------------|----------|-------------|----|----|----|---------|---------| 
{chr(10).join(f"| {r['question_id']} | {r['decision']} | {r['total_score']:.1f}/100 | {r['tier1_score']:.1f}/55 | {r['tier2_score']:.1f}/30 | {r['tier3_score']:.1f}/15 | {r['blockers_count']} | {r['warnings_count']} |" for r in results)}

---

## RECOMMENDATIONS

### High Priority
- Contracts with REFORMULAR decision require complete rebuild
- Contracts with blockers need immediate attention

### Medium Priority
- Contracts with PARCHEAR decision can be fixed with targeted improvements
- Address all warnings to improve contract quality

### Low Priority
- Contracts with PRODUCCIÓN decision are ready for deployment
- Consider optimizations for contracts scoring below 90/100

---

**Generated**: {datetime.now(timezone.utc).isoformat()}  
**Batch**: Q{start_q:03d}-Q{end_q:03d}  
**Tool**: CQVR Batch Evaluator v2.0
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":
    main()
