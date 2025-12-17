#!/usr/bin/env python3
"""
CQVR v2.0 Batch 3 Evaluator - Contracts Q051 through Q075

Applies the CQVR v2.0 rubric to evaluate 25 contracts (Q051-Q075) and generates:
1. Individual evaluation reports for each contract
2. Batch summary report with statistics

Based on the CQVR v2.0 rubric specification and previous Q001/Q002 evaluation patterns.
"""

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


class CQVRBatch3Evaluator:
    """Evaluates Q051-Q075 contracts using CQVR v2.0 rubric."""
    
    def __init__(self, contracts_dir: Path, output_dir: Path):
        self.contracts_dir = contracts_dir
        self.output_dir = output_dir
        self.validator = CQVRValidator()
        self.results: dict[str, ContractTriageDecision] = {}
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def evaluate_batch(self, start: int = 51, end: int = 75) -> None:
        """Evaluate all contracts from Q{start} to Q{end}."""
        print(f"\n{'='*80}")
        print(f"CQVR v2.0 Batch 3 Evaluation: Q{start:03d} - Q{end:03d}")
        print(f"{'='*80}\n")
        
        for q_num in range(start, end + 1):
            question_id = f"Q{q_num:03d}"
            contract_path = self.contracts_dir / f"{question_id}.v3.json"
            
            if not contract_path.exists():
                print(f"⚠️  {question_id}: Contract file not found at {contract_path}")
                continue
            
            print(f"📊 Evaluating {question_id}...", end=" ")
            
            try:
                with open(contract_path, 'r', encoding='utf-8') as f:
                    contract = json.load(f)
                
                decision = self.validator.validate_contract(contract)
                
                # Populate component scores
                decision.score.component_scores['A1'] = self.validator.verify_identity_schema_coherence(contract)
                decision.score.component_scores['A2'] = self.validator.verify_method_assembly_alignment(contract)
                decision.score.component_scores['A3'] = self.validator.verify_signal_requirements(contract)
                decision.score.component_scores['A4'] = self.validator.verify_output_schema(contract)
                decision.score.component_scores['B1'] = self.validator.verify_pattern_coverage(contract)
                decision.score.component_scores['B2'] = self.validator.verify_method_specificity(contract)
                decision.score.component_scores['B3'] = self.validator.verify_validation_rules(contract)
                decision.score.component_scores['C1'] = self.validator.verify_documentation_quality(contract)
                decision.score.component_scores['C2'] = self.validator.verify_human_template(contract)
                decision.score.component_scores['C3'] = self.validator.verify_metadata_completeness(contract)
                
                self.results[question_id] = decision
                
                status_icon = self._get_status_icon(decision)
                print(f"{status_icon} {decision.score.total_score:.0f}/100 "
                      f"(T1: {decision.score.tier1_score:.0f}/55, "
                      f"T2: {decision.score.tier2_score:.0f}/30, "
                      f"T3: {decision.score.tier3_score:.0f}/15)")
                
                self._generate_individual_report(question_id, contract, decision)
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                continue
        
        self._generate_batch_summary()
        print(f"\n{'='*80}")
        print(f"✅ Batch evaluation complete. Reports saved to {self.output_dir}/")
        print(f"{'='*80}\n")
    
    def _get_status_icon(self, decision: ContractTriageDecision) -> str:
        """Get status icon based on decision."""
        if decision.decision == TriageDecision.PRODUCCION:
            return "✅"
        elif decision.decision == TriageDecision.PARCHEAR:
            return "⚠️"
        else:
            return "❌"
    
    def _generate_individual_report(
        self, 
        question_id: str, 
        contract: dict[str, Any], 
        decision: ContractTriageDecision
    ) -> None:
        """Generate individual CQVR evaluation report for a contract."""
        identity = contract.get("identity", {})
        base_slot = identity.get("base_slot", "N/A")
        dimension_id = identity.get("dimension_id", "N/A")
        policy_area_id = identity.get("policy_area_id", "N/A")
        
        report = self._build_report_markdown(
            question_id, base_slot, dimension_id, policy_area_id, decision
        )
        
        report_path = self.output_dir / f"{question_id}_CQVR_EVALUATION_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def _build_report_markdown(
        self,
        question_id: str,
        base_slot: str,
        dimension_id: str,
        policy_area_id: str,
        decision: ContractTriageDecision
    ) -> str:
        """Build markdown report for a contract evaluation."""
        score = decision.score
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        verdict_emoji = "✅" if decision.is_production_ready() else "⚠️" if decision.can_be_patched() else "❌"
        verdict_text = (
            "CONTRATO APTO PARA PRODUCCIÓN" if decision.is_production_ready()
            else "CONTRATO REQUIERE PARCHES" if decision.can_be_patched()
            else "CONTRATO REQUIERE REFORMULACIÓN"
        )
        
        report = f"""# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: {question_id}.v3.json
**Fecha**: {timestamp}  
**Evaluador**: CQVR Batch 3 Automated Evaluator  
**Rúbrica**: CQVR v2.0 (100 puntos)  
**Base Slot**: {base_slot}  
**Dimension**: {dimension_id}  
**Policy Area**: {policy_area_id}

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **{score.tier1_score:.0f}/55** | ≥35 | {'✅ APROBADO' if score.tier1_score >= 35 else '❌ REPROBADO'} |
| **TIER 2: Componentes Funcionales** | **{score.tier2_score:.0f}/30** | ≥20 | {'✅ APROBADO' if score.tier2_score >= 20 else '❌ REPROBADO'} |
| **TIER 3: Componentes de Calidad** | **{score.tier3_score:.0f}/15** | ≥8 | {'✅ APROBADO' if score.tier3_score >= 8 else '❌ REPROBADO'} |
| **TOTAL** | **{score.total_score:.0f}/100** | ≥80 | {'✅ PRODUCCIÓN' if score.total_score >= 80 else '⚠️ MEJORAR' if score.total_score >= 60 else '❌ REFORMULAR'} |

**VEREDICTO**: {verdict_emoji} **{verdict_text}**

{decision.rationale}

---

## TIER 1: COMPONENTES CRÍTICOS - {score.tier1_score:.0f}/55 pts ({score.tier1_percentage:.1f}%)

### A1. Coherencia Identity-Schema [20/20 pts max]
**Score**: {score.component_scores.get('A1', 0):.0f}/20

Verifica que los campos de identity coincidan exactamente con los const en output_contract.schema.

### A2. Alineación Method-Assembly [20/20 pts max]
**Score**: {score.component_scores.get('A2', 0):.0f}/20

Verifica que todos los sources en assembly_rules existan en method_binding.methods[].provides.

### A3. Integridad de Señales [10/10 pts max]
**Score**: {score.component_scores.get('A3', 0):.0f}/10

Verifica que minimum_signal_threshold > 0 si hay mandatory_signals.

### A4. Validación de Output Schema [5/5 pts max]
**Score**: {score.component_scores.get('A4', 0):.0f}/5

Verifica que todos los campos required estén definidos en properties.

---

## TIER 2: COMPONENTES FUNCIONALES - {score.tier2_score:.0f}/30 pts ({score.tier2_percentage:.1f}%)

### B1. Coherencia de Patrones [10/10 pts max]
**Score**: {score.component_scores.get('B1', 0):.0f}/10

Verifica que los patterns cubran los expected_elements, con confidence_weights válidos e IDs únicos.

### B2. Especificidad Metodológica [10/10 pts max]
**Score**: {score.component_scores.get('B2', 0):.0f}/10

Verifica que methodological_depth tenga documentación específica (no boilerplate).

### B3. Reglas de Validación [10/10 pts max]
**Score**: {score.component_scores.get('B3', 0):.0f}/10

Verifica que validation_rules cubran expected_elements y tengan failure_contract.

---

## TIER 3: COMPONENTES DE CALIDAD - {score.tier3_score:.0f}/15 pts ({score.tier3_percentage:.1f}%)

### C1. Documentación Epistemológica [5/5 pts max]
**Score**: {score.component_scores.get('C1', 0):.0f}/5

Verifica calidad de epistemological_foundation (paradigmas, justificaciones, referencias).

### C2. Template Human-Readable [5/5 pts max]
**Score**: {score.component_scores.get('C2', 0):.0f}/5

Verifica que el template tenga referencias correctas y placeholders dinámicos.

### C3. Metadatos y Trazabilidad [5/5 pts max]
**Score**: {score.component_scores.get('C3', 0):.0f}/5

Verifica completitud de metadatos (contract_hash, created_at, source_hash).

---

## BLOCKERS CRÍTICOS

"""
        
        if decision.blockers:
            report += f"**Total**: {len(decision.blockers)} blocker(s)\n\n"
            for i, blocker in enumerate(decision.blockers, 1):
                report += f"{i}. ❌ {blocker}\n"
        else:
            report += "✅ No hay blockers críticos identificados.\n"
        
        report += "\n---\n\n## ADVERTENCIAS\n\n"
        
        if decision.warnings:
            report += f"**Total**: {len(decision.warnings)} warning(s)\n\n"
            for i, warning in enumerate(decision.warnings, 1):
                report += f"{i}. ⚠️ {warning}\n"
        else:
            report += "✅ No hay advertencias.\n"
        
        report += "\n---\n\n## RECOMENDACIONES\n\n"
        
        if decision.recommendations:
            report += f"**Total**: {len(decision.recommendations)} recomendación(es)\n\n"
            for i, rec in enumerate(decision.recommendations, 1):
                report += f"### {i}. {rec['component']} - {rec['priority']}\n"
                report += f"**Issue**: {rec['issue']}\n\n"
                report += f"**Fix**: {rec['fix']}\n\n"
                report += f"**Impact**: {rec['impact']}\n\n"
        else:
            report += "✅ No hay recomendaciones adicionales.\n"
        
        report += f"""
---

## MATRIZ DE DECISIÓN CQVR

```
TIER 1 Score: {score.tier1_score:.0f}/55 ({score.tier1_percentage:.1f}%)
TIER 2 Score: {score.tier2_score:.0f}/30 ({score.tier2_percentage:.1f}%)
TIER 3 Score: {score.tier3_score:.0f}/15 ({score.tier3_percentage:.1f}%)
TOTAL Score:  {score.total_score:.0f}/100 ({score.total_percentage:.1f}%)

DECISIÓN: {decision.decision.value}
```

### Criterios de Decisión

| Condición | Umbral | Valor Actual | Estado |
|-----------|--------|--------------|--------|
| Tier 1 ≥ 35 (63.6%) | 35/55 | {score.tier1_score:.0f}/55 | {'✅' if score.tier1_score >= 35 else '❌'} |
| Tier 1 ≥ 45 (81.8%) | 45/55 | {score.tier1_score:.0f}/55 | {'✅' if score.tier1_score >= 45 else '❌'} |
| Total ≥ 80 | 80/100 | {score.total_score:.0f}/100 | {'✅' if score.total_score >= 80 else '❌'} |
| Blockers = 0 | 0 | {len(decision.blockers)} | {'✅' if len(decision.blockers) == 0 else '❌'} |

---

## CONCLUSIÓN

{self._generate_conclusion(decision)}

---

**Firma Digital CQVR**:  
Hash: `{score.total_score:.0f}/100-T1:{score.tier1_score:.0f}-T2:{score.tier2_score:.0f}-T3:{score.tier3_score:.0f}-{decision.decision.value}`  
Timestamp: `{datetime.now().isoformat()}`  
Evaluator: `CQVR-Batch3-Automated-Validator-v2.0`  
Status: `{decision.decision.value}`
"""
        
        return report
    
    def _generate_conclusion(self, decision: ContractTriageDecision) -> str:
        """Generate conclusion text based on decision."""
        score = decision.score
        
        if decision.decision == TriageDecision.PRODUCCION:
            return f"""
El contrato alcanza **{score.total_score:.0f}/100 puntos**, superando el umbral de 80 pts para producción.

**Puntos fuertes**:
- Tier 1 (Componentes Críticos): {score.tier1_score:.0f}/55 ({score.tier1_percentage:.1f}%)
- Tier 2 (Componentes Funcionales): {score.tier2_score:.0f}/30 ({score.tier2_percentage:.1f}%)
- Tier 3 (Componentes de Calidad): {score.tier3_score:.0f}/15 ({score.tier3_percentage:.1f}%)

**Veredicto**: ✅ **APTO PARA PRODUCCIÓN**

El contrato puede ser desplegado en el pipeline sin correcciones críticas.
"""
        elif decision.decision == TriageDecision.PARCHEAR:
            return f"""
El contrato alcanza **{score.total_score:.0f}/100 puntos**, con Tier 1 en {score.tier1_score:.0f}/55 ({score.tier1_percentage:.1f}%).

**Estado**:
- ⚠️ Tier 1 supera umbral mínimo (35 pts) pero está por debajo de producción (45 pts)
- ⚠️ Score total por debajo de 80 pts
- ⚠️ {len(decision.blockers)} blocker(s) identificados

**Veredicto**: ⚠️ **REQUIERE PARCHES**

El contrato puede ser corregido mediante parches puntuales. Aplicar las correcciones recomendadas 
para alcanzar el umbral de producción (80 pts).

**Próximos pasos**:
1. Resolver los {len(decision.blockers)} blockers críticos
2. Aplicar correcciones recomendadas
3. Re-evaluar con CQVR v2.0
"""
        else:
            return f"""
El contrato alcanza **{score.total_score:.0f}/100 puntos**, con Tier 1 en {score.tier1_score:.0f}/55 ({score.tier1_percentage:.1f}%).

**Estado**:
- ❌ Tier 1 por debajo de umbral crítico (35 pts)
- ❌ {len(decision.blockers)} blocker(s) críticos
- ❌ Contrato no ejecutable en estado actual

**Veredicto**: ❌ **REQUIERE REFORMULACIÓN**

El contrato tiene fallas estructurales que no pueden resolverse con parches. Se requiere 
regeneración desde el monolith o reconstrucción completa.

**Recomendación**: Regenerar contrato usando ContractGenerator con validación CQVR integrada.
"""
    
    def _generate_batch_summary(self) -> None:
        """Generate batch summary report with statistics."""
        if not self.results:
            print("⚠️  No results to summarize")
            return
        
        total_contracts = len(self.results)
        production_ready = sum(1 for d in self.results.values() if d.is_production_ready())
        patchable = sum(1 for d in self.results.values() if d.can_be_patched())
        requires_reformulation = sum(1 for d in self.results.values() if d.requires_reformulation())
        
        avg_total = sum(d.score.total_score for d in self.results.values()) / total_contracts
        avg_tier1 = sum(d.score.tier1_score for d in self.results.values()) / total_contracts
        avg_tier2 = sum(d.score.tier2_score for d in self.results.values()) / total_contracts
        avg_tier3 = sum(d.score.tier3_score for d in self.results.values()) / total_contracts
        
        max_score_contract = max(self.results.items(), key=lambda x: x[1].score.total_score)
        min_score_contract = min(self.results.items(), key=lambda x: x[1].score.total_score)
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        summary = f"""# 📊 CQVR v2.0 Batch 3 Summary Report
## Contracts Q051-Q075 Evaluation Results

**Date**: {timestamp}  
**Evaluator**: CQVR Batch 3 Automated Evaluator  
**Rubric**: CQVR v2.0 (100 points)  
**Total Contracts Evaluated**: {total_contracts}

---

## EXECUTIVE SUMMARY

| Metric | Value | Percentage |
|--------|-------|------------|
| **Production Ready** (≥80 pts) | {production_ready}/{total_contracts} | {production_ready/total_contracts*100:.1f}% |
| **Patchable** (60-79 pts) | {patchable}/{total_contracts} | {patchable/total_contracts*100:.1f}% |
| **Requires Reformulation** (<60 pts) | {requires_reformulation}/{total_contracts} | {requires_reformulation/total_contracts*100:.1f}% |

---

## SCORE STATISTICS

| Tier | Average Score | Max | Percentage |
|------|---------------|-----|------------|
| **Tier 1: Critical** | {avg_tier1:.1f}/55 | 55 | {avg_tier1/55*100:.1f}% |
| **Tier 2: Functional** | {avg_tier2:.1f}/30 | 30 | {avg_tier2/30*100:.1f}% |
| **Tier 3: Quality** | {avg_tier3:.1f}/15 | 15 | {avg_tier3/15*100:.1f}% |
| **TOTAL** | {avg_total:.1f}/100 | 100 | {avg_total:.1f}% |

**Best Performing Contract**: {max_score_contract[0]} ({max_score_contract[1].score.total_score:.0f}/100)  
**Lowest Performing Contract**: {min_score_contract[0]} ({min_score_contract[1].score.total_score:.0f}/100)

---

## DETAILED RESULTS

| Contract | Total | T1 | T2 | T3 | Decision | Blockers | Warnings |
|----------|-------|----|----|----|----|----------|----------|
"""
        
        for question_id in sorted(self.results.keys()):
            decision = self.results[question_id]
            score = decision.score
            status = "✅" if decision.is_production_ready() else "⚠️" if decision.can_be_patched() else "❌"
            
            summary += f"| {question_id} | {score.total_score:.0f} | {score.tier1_score:.0f} | {score.tier2_score:.0f} | {score.tier3_score:.0f} | {status} {decision.decision.value} | {len(decision.blockers)} | {len(decision.warnings)} |\n"
        
        summary += f"""
---

## COMMON ISSUES

### Blockers by Frequency
"""
        
        all_blockers = [b for d in self.results.values() for b in d.blockers]
        blocker_types = {}
        for blocker in all_blockers:
            blocker_type = blocker.split(':')[0] if ':' in blocker else 'Other'
            blocker_types[blocker_type] = blocker_types.get(blocker_type, 0) + 1
        
        if blocker_types:
            for blocker_type, count in sorted(blocker_types.items(), key=lambda x: x[1], reverse=True):
                summary += f"- **{blocker_type}**: {count} occurrences ({count/len(self.results)*100:.1f}% of contracts)\n"
        else:
            summary += "✅ No common blockers identified\n"
        
        summary += "\n### Warnings by Frequency\n"
        
        all_warnings = [w for d in self.results.values() for w in d.warnings]
        warning_types = {}
        for warning in all_warnings:
            warning_type = warning.split(':')[0] if ':' in warning else 'Other'
            warning_types[warning_type] = warning_types.get(warning_type, 0) + 1
        
        if warning_types:
            for warning_type, count in sorted(warning_types.items(), key=lambda x: x[1], reverse=True):
                summary += f"- **{warning_type}**: {count} occurrences ({count/len(self.results)*100:.1f}% of contracts)\n"
        else:
            summary += "✅ No common warnings identified\n"
        
        summary += f"""
---

## RECOMMENDATIONS FOR BATCH IMPROVEMENT

### High Priority Actions

1. **Address Common Blockers**: Focus on the most frequent blocker types identified above
2. **Standardize Documentation**: Ensure all contracts have specific (non-boilerplate) methodological depth
3. **Complete Traceability**: Calculate and add source_hash to all contracts with placeholders

### Score Distribution

```
Production Ready (80-100):  {production_ready:2d} contracts {'█' * int(production_ready/total_contracts*40)}
Patchable (60-79):         {patchable:2d} contracts {'█' * int(patchable/total_contracts*40)}
Needs Reformulation (<60):  {requires_reformulation:2d} contracts {'█' * int(requires_reformulation/total_contracts*40)}
```

### Quality Metrics

- **Average Quality**: {avg_total:.1f}% {'✅ Excellent' if avg_total >= 85 else '✅ Good' if avg_total >= 75 else '⚠️ Acceptable' if avg_total >= 65 else '❌ Needs Improvement'}
- **Consistency**: {(1 - (max_score_contract[1].score.total_score - min_score_contract[1].score.total_score)/100)*100:.1f}% (lower variation = more consistent)
- **Production Readiness**: {production_ready/total_contracts*100:.1f}% of batch ready for deployment

---

## CONCLUSION

Batch 3 (Q051-Q075) evaluation completed successfully with {total_contracts} contracts analyzed.

**Overall Assessment**: {"✅ BATCH APPROVED" if production_ready/total_contracts >= 0.8 else "⚠️ BATCH REQUIRES ATTENTION" if production_ready/total_contracts >= 0.6 else "❌ BATCH NEEDS SIGNIFICANT REWORK"}

**Next Steps**:
1. Review individual reports for contracts with decision != PRODUCCION
2. Apply recommended patches to patchable contracts
3. Regenerate contracts that require reformulation
4. Re-run CQVR validation after corrections

---

**Generated**: {datetime.now().isoformat()}  
**Tool**: CQVR Batch 3 Automated Evaluator v2.0  
**Rubric**: CQVR v2.0 (100 points)
"""
        
        summary_path = self.output_dir / "BATCH3_Q051_Q075_CQVR_SUMMARY.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n📈 Batch summary report generated: {summary_path}")


def main():
    """Main entry point for CQVR Batch 3 evaluation."""
    base_dir = Path(__file__).parent
    contracts_dir = base_dir / "src" / "farfan_pipeline" / "phases" / "Phase_two" / "json_files_phase_two" / "executor_contracts" / "specialized"
    output_dir = base_dir / "cqvr_reports" / "batch3_Q051_Q075"
    
    if not contracts_dir.exists():
        print(f"❌ Error: Contracts directory not found: {contracts_dir}")
        sys.exit(1)
    
    evaluator = CQVRBatch3Evaluator(contracts_dir, output_dir)
    evaluator.evaluate_batch(start=51, end=75)


if __name__ == "__main__":
    main()
