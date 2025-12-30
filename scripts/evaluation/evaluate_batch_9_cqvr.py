#!/usr/bin/env python3
"""
CQVR v2.0 Batch Evaluation Script - Batch 9 (Q201-Q225)
Evaluates 25 contracts using the CQVR v2.0 rubric and generates detailed reports.
"""
import json
import sys
from pathlib import Path
from typing import Any
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from farfan_pipeline.phases.Phase_two.json_files_phase_two.executor_contracts.cqvr_validator import (
    CQVRValidator,
    ContractRemediation
)


def format_score_bar(score: int, max_score: int, width: int = 20) -> str:
    """Create a visual progress bar for scores"""
    filled = int((score / max_score) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {score}/{max_score}"


def format_tier_status(score: int, max_score: int, threshold: int) -> str:
    """Format tier status with emoji"""
    if score >= threshold:
        return f"✅ {score}/{max_score}"
    else:
        return f"❌ {score}/{max_score}"


def generate_contract_report(contract_path: Path, validator: CQVRValidator) -> dict[str, Any]:
    """Generate detailed CQVR report for a single contract"""
    with open(contract_path) as f:
        contract = json.load(f)
    
    report = validator.validate_contract(contract)
    report['contract_id'] = contract['identity']['question_id']
    report['contract_path'] = str(contract_path)
    
    return report


def generate_markdown_report(contract_id: str, report: dict[str, Any]) -> str:
    """Generate markdown report for a single contract"""
    scores = report['breakdown']
    
    md = f"""# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: {contract_id}.v3.json
**Fecha**: {datetime.now().strftime('%Y-%m-%d')}  
**Evaluador**: CQVR Batch Evaluation System  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **{report['tier1_score']}/55** | ≥35 | {format_tier_status(report['tier1_score'], 55, 35)} |
| **TIER 2: Componentes Funcionales** | **{report['tier2_score']}/30** | ≥20 | {format_tier_status(report['tier2_score'], 30, 20)} |
| **TIER 3: Componentes de Calidad** | **{report['tier3_score']}/15** | ≥8 | {format_tier_status(report['tier3_score'], 15, 8)} |
| **TOTAL** | **{report['total_score']}/100** | ≥80 | {'✅ **PRODUCCIÓN**' if report['passed'] else '❌ **REQUIERE CORRECCIÓN**'} |

**VEREDICTO**: {'✅ **CONTRATO APTO PARA PRODUCCIÓN**' if report['passed'] else '⚠️ **REQUIERE MEJORAS**'}

**Triage Decision**: `{report['triage_decision']}`

El contrato {contract_id}.v3.json alcanza {report['total_score']}/100 puntos ({report['percentage']:.1f}%).

---

## TIER 1: COMPONENTES CRÍTICOS - {report['tier1_score']}/55 pts

### A1. Coherencia Identity-Schema [{scores['A1_identity_schema']}/20 pts]
{format_score_bar(scores['A1_identity_schema'], 20)}

**Evaluación**: {'✅ PERFECTO' if scores['A1_identity_schema'] == 20 else ('✅ APROBADO' if scores['A1_identity_schema'] >= 15 else '❌ CRÍTICO')}

Verifica que los campos de identity coincidan exactamente con los const del output_contract.schema.

### A2. Alineación Method-Assembly [{scores['A2_method_assembly']}/20 pts]
{format_score_bar(scores['A2_method_assembly'], 20)}

**Evaluación**: {'✅ PERFECTO' if scores['A2_method_assembly'] == 20 else ('✅ APROBADO' if scores['A2_method_assembly'] >= 12 else '❌ CRÍTICO')}

Verifica que todas las sources en assembly_rules existan en method_binding.provides.

### A3. Integridad de Señales [{scores['A3_signal_integrity']}/10 pts]
{format_score_bar(scores['A3_signal_integrity'], 10)}

**Evaluación**: {'✅ PERFECTO' if scores['A3_signal_integrity'] == 10 else ('✅ APROBADO' if scores['A3_signal_integrity'] >= 5 else '❌ CRÍTICO')}

Verifica que el minimum_signal_threshold sea > 0 cuando hay mandatory_signals.

### A4. Validación de Output Schema [{scores['A4_output_schema']}/5 pts]
{format_score_bar(scores['A4_output_schema'], 5)}

**Evaluación**: {'✅ PERFECTO' if scores['A4_output_schema'] == 5 else ('✅ APROBADO' if scores['A4_output_schema'] >= 3 else '❌ CRÍTICO')}

Verifica que todos los campos required tengan definición en properties.

---

## TIER 2: COMPONENTES FUNCIONALES - {report['tier2_score']}/30 pts

### B1. Coherencia de Patrones [{scores['B1_pattern_coverage']}/10 pts]
{format_score_bar(scores['B1_pattern_coverage'], 10)}

### B2. Especificidad Metodológica [{scores['B2_method_specificity']}/10 pts]
{format_score_bar(scores['B2_method_specificity'], 10)}

### B3. Reglas de Validación [{scores['B3_validation_rules']}/10 pts]
{format_score_bar(scores['B3_validation_rules'], 10)}

---

## TIER 3: COMPONENTES DE CALIDAD - {report['tier3_score']}/15 pts

### C1. Documentación Epistemológica [{scores['C1_documentation']}/5 pts]
{format_score_bar(scores['C1_documentation'], 5)}

### C2. Template Human-Readable [{scores['C2_human_template']}/5 pts]
{format_score_bar(scores['C2_human_template'], 5)}

### C3. Metadatos y Trazabilidad [{scores['C3_metadata']}/5 pts]
{format_score_bar(scores['C3_metadata'], 5)}

---

## RECOMENDACIONES

"""
    
    # Add recommendations based on triage decision
    if report['triage_decision'].startswith('REFORMULAR'):
        md += """
### ⚠️ ACCIÓN REQUERIDA: REFORMULAR COMPLETO

Este contrato tiene fallos críticos en Tier 1 que requieren reformulación completa.
No se recomienda parchear; es mejor regenerar desde el questionnaire monolith.
"""
    elif report['triage_decision'] == 'PARCHEAR_MAJOR':
        md += """
### ⚠️ ACCIÓN REQUERIDA: PARCHEAR (MAJOR)

Este contrato requiere correcciones significativas en componentes críticos.
Aplicar ContractRemediation para resolver automáticamente los problemas estructurales.
"""
    elif report['triage_decision'] == 'PARCHEAR_MINOR':
        md += """
### ✅ ACCIÓN SUGERIDA: PARCHEAR (MINOR)

Este contrato está cerca del umbral de producción. Correcciones menores pueden optimizarlo.
"""
    else:
        md += """
### ✅ LISTO PARA PRODUCCIÓN

Este contrato cumple todos los requisitos de calidad para deployment.
"""
    
    # Add specific issues
    md += "\n### Detalles por Componente:\n\n"
    
    if scores['A1_identity_schema'] < 20:
        md += "- **A1 (Identity-Schema)**: Discrepancias detectadas en campos de identity vs schema\n"
    if scores['A2_method_assembly'] < 20:
        md += "- **A2 (Method-Assembly)**: Sources huérfanos o provides sin uso detectados\n"
    if scores['A3_signal_integrity'] < 10:
        md += "- **A3 (Signal Integrity)**: Problemas con signal threshold o aggregation\n"
    if scores['A4_output_schema'] < 5:
        md += "- **A4 (Output Schema)**: Campos required sin definición en properties\n"
    
    md += "\n---\n\n**Generado automáticamente por CQVR Batch Evaluation System**\n"
    
    return md


def main():
    """Main batch evaluation routine"""
    print("=" * 80)
    print("CQVR v2.0 BATCH EVALUATION - BATCH 9 (Q201-Q225)")
    print("=" * 80)
    print()
    
    # Setup paths
    base_path = Path(__file__).parent
    contracts_dir = base_path / "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
    reports_dir = base_path / "cqvr_batch_9_reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Initialize validator
    validator = CQVRValidator()
    
    # Contracts to evaluate
    contract_range = range(201, 226)  # Q201-Q225
    
    # Results tracking
    all_reports = []
    passed_count = 0
    failed_count = 0
    
    print(f"Evaluating {len(list(contract_range))} contracts (Q201-Q225)...")
    print()
    
    # Evaluate each contract
    for i in contract_range:
        contract_id = f"Q{i:03d}"
        contract_path = contracts_dir / f"{contract_id}.v3.json"
        
        if not contract_path.exists():
            print(f"⚠️  {contract_id}: File not found, skipping")
            continue
        
        print(f"Evaluating {contract_id}...", end=" ")
        
        try:
            report = generate_contract_report(contract_path, validator)
            all_reports.append(report)
            
            # Generate individual report
            md_report = generate_markdown_report(contract_id, report)
            report_path = reports_dir / f"{contract_id}_CQVR_EVALUATION.md"
            report_path.write_text(md_report)
            
            # Print result
            status = "✅ PASS" if report['passed'] else "❌ FAIL"
            print(f"{status} ({report['total_score']}/100, {report['percentage']:.1f}%)")
            
            if report['passed']:
                passed_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed_count += 1
    
    print()
    print("=" * 80)
    print("BATCH EVALUATION COMPLETE")
    print("=" * 80)
    print()
    
    # Generate summary statistics
    if all_reports:
        avg_score = sum(r['total_score'] for r in all_reports) / len(all_reports)
        avg_tier1 = sum(r['tier1_score'] for r in all_reports) / len(all_reports)
        avg_tier2 = sum(r['tier2_score'] for r in all_reports) / len(all_reports)
        avg_tier3 = sum(r['tier3_score'] for r in all_reports) / len(all_reports)
        
        print(f"Contracts Evaluated: {len(all_reports)}")
        print(f"Passed (≥80/100):    {passed_count} ({passed_count/len(all_reports)*100:.1f}%)")
        print(f"Failed (<80/100):    {failed_count} ({failed_count/len(all_reports)*100:.1f}%)")
        print()
        print(f"Average Scores:")
        print(f"  Total:  {avg_score:.1f}/100")
        print(f"  Tier 1: {avg_tier1:.1f}/55")
        print(f"  Tier 2: {avg_tier2:.1f}/30")
        print(f"  Tier 3: {avg_tier3:.1f}/15")
        print()
        
        # Generate executive summary
        generate_executive_summary(all_reports, reports_dir, passed_count, failed_count)
        
        print(f"Individual reports saved to: {reports_dir}")
        print(f"Executive summary: {reports_dir / 'BATCH_9_EXECUTIVE_SUMMARY.md'}")
        
        return 0 if failed_count == 0 else 1
    else:
        print("No contracts were evaluated.")
        return 1


def generate_executive_summary(reports: list[dict], output_dir: Path, passed: int, failed: int):
    """Generate executive summary for the entire batch"""
    
    avg_score = sum(r['total_score'] for r in reports) / len(reports)
    avg_tier1 = sum(r['tier1_score'] for r in reports) / len(reports)
    avg_tier2 = sum(r['tier2_score'] for r in reports) / len(reports)
    avg_tier3 = sum(r['tier3_score'] for r in reports) / len(reports)
    
    md = f"""# 📊 CQVR v2.0 BATCH 9 EXECUTIVE SUMMARY
## Contracts Q201-Q225

**Evaluation Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Batch**: 9/12 (Contracts Q201-Q225)  
**Total Contracts**: {len(reports)}

---

## OVERALL RESULTS

| Metric | Value |
|--------|-------|
| **Contracts Evaluated** | {len(reports)} |
| **Passed (≥80/100)** | {passed} ({passed/len(reports)*100:.1f}%) |
| **Failed (<80/100)** | {failed} ({failed/len(reports)*100:.1f}%) |
| **Average Total Score** | {avg_score:.1f}/100 |
| **Average Tier 1** | {avg_tier1:.1f}/55 |
| **Average Tier 2** | {avg_tier2:.1f}/30 |
| **Average Tier 3** | {avg_tier3:.1f}/15 |

---

## DETAILED BREAKDOWN

| Contract ID | Total Score | Tier 1 | Tier 2 | Tier 3 | Status | Triage |
|-------------|-------------|--------|--------|--------|--------|--------|
"""
    
    for report in sorted(reports, key=lambda r: r['contract_id']):
        status = "✅ PASS" if report['passed'] else "❌ FAIL"
        md += f"| {report['contract_id']} | {report['total_score']}/100 | {report['tier1_score']}/55 | {report['tier2_score']}/30 | {report['tier3_score']}/15 | {status} | {report['triage_decision']} |\n"
    
    md += "\n---\n\n## TRIAGE DISTRIBUTION\n\n"
    
    # Count triage decisions
    triage_counts: dict[str, int] = {}
    for report in reports:
        decision = report['triage_decision']
        triage_counts[decision] = triage_counts.get(decision, 0) + 1
    
    for decision, count in sorted(triage_counts.items(), key=lambda x: -x[1]):
        md += f"- **{decision}**: {count} contracts ({count/len(reports)*100:.1f}%)\n"
    
    md += "\n---\n\n## RECOMMENDATIONS\n\n"
    
    if failed > 0:
        md += f"""
### ⚠️ ACTION REQUIRED

{failed} contracts failed to meet the 80/100 threshold. Recommended actions:

1. **Review Individual Reports**: Check detailed CQVR reports in this directory
2. **Apply Remediation**: Use ContractRemediation for structural fixes
3. **Re-evaluate**: Run batch evaluation again after corrections
4. **Manual Review**: For REFORMULAR cases, consider regeneration from monolith
"""
    else:
        md += """
### ✅ BATCH APPROVED

All contracts in Batch 9 meet the production quality threshold (≥80/100).
Ready for integration into the main pipeline.
"""
    
    md += """

---

## NEXT STEPS

1. Review contracts with score < 80/100
2. Apply automated remediation where applicable
3. Manually fix critical issues in REFORMULAR cases
4. Re-run batch evaluation
5. Update contract versions and timestamps
6. Generate final certification report

---

**Generated by CQVR Batch Evaluation System**
"""
    
    summary_path = output_dir / "BATCH_9_EXECUTIVE_SUMMARY.md"
    summary_path.write_text(md)


if __name__ == "__main__":
    sys.exit(main())
