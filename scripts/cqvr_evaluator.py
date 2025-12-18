#!/usr/bin/env python3
"""
CQVR Batch Evaluator - Contract Quality Validation and Remediation
Evaluates batches of executor contracts using CQVR v2.0 rubric
"""
import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from farfan_pipeline.phases.Phase_two.phase2_g_contract_validator_cqvr import (
    CQVRValidator,
    ContractTriageDecision,
    TriageDecision,
)


@dataclass
class BatchConfig:
    """Configuration for contract batch evaluation"""

    batch_number: int
    start_question: int
    end_question: int
    contracts_dir: Path
    output_dir: Path


BATCH_CONFIGS = {
    1: BatchConfig(
        batch_number=1,
        start_question=1,
        end_question=25,
        contracts_dir=Path(
            "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
        ),
        output_dir=Path("reports/cqvr_batch_1"),
    ),
}


class CQVRBatchEvaluator:
    """Batch evaluator for CQVR v2.0 contract validation"""

    def __init__(self, config: BatchConfig):
        self.config = config
        self.validator = CQVRValidator()
        self.results: list[tuple[str, ContractTriageDecision, dict[str, Any]]] = []

    def evaluate_batch(self) -> None:
        """Evaluate all contracts in the batch"""
        print(f"\n{'='*80}")
        print(f"CQVR Batch {self.config.batch_number} Evaluation")
        print(f"Evaluating Q{self.config.start_question:03d}-Q{self.config.end_question:03d}")
        print(f"{'='*80}\n")

        for q_num in range(self.config.start_question, self.config.end_question + 1):
            contract_id = f"Q{q_num:03d}"
            contract_path = self.config.contracts_dir / f"{contract_id}.v3.json"

            if not contract_path.exists():
                print(f"⚠️  {contract_id}: Contract file not found at {contract_path}")
                continue

            print(f"Evaluating {contract_id}...", end=" ")
            try:
                with open(contract_path, "r", encoding="utf-8") as f:
                    contract = json.load(f)

                decision = self.validator.validate_contract(contract)
                self.results.append((contract_id, decision, contract))
                
                status_icon = self._get_status_icon(decision.decision)
                print(f"{status_icon} {decision.score.total_score:.1f}/100")

            except Exception as e:
                print(f"❌ ERROR: {e}")
                continue

        print(f"\n{'='*80}")
        print(f"Evaluation Complete: {len(self.results)} contracts processed")
        print(f"{'='*80}\n")

    def _get_status_icon(self, decision: TriageDecision) -> str:
        """Get status icon for decision"""
        if decision == TriageDecision.PRODUCCION:
            return "✅"
        elif decision == TriageDecision.PARCHEAR:
            return "⚠️"
        else:
            return "❌"

    def generate_reports(self) -> None:
        """Generate all reports: individual and consolidated"""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate individual reports
        print("Generating individual contract reports...")
        for contract_id, decision, contract in self.results:
            self._generate_individual_report(contract_id, decision, contract)

        # Generate batch summary
        print("Generating batch summary...")
        self._generate_batch_summary()

        print(f"\n✅ All reports generated in: {self.config.output_dir}")

    def _generate_individual_report(
        self, contract_id: str, decision: ContractTriageDecision, contract: dict[str, Any]
    ) -> None:
        """Generate individual contract evaluation report"""
        report_path = self.config.output_dir / f"{contract_id}_CQVR_REPORT.md"

        score = decision.score
        identity = contract.get("identity", {})

        report = f"""# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: {contract_id}.v3.json
**Fecha**: {datetime.now().strftime("%Y-%m-%d")}  
**Evaluador**: CQVR Batch Evaluator v2.0  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **{score.tier1_score:.1f}/{score.tier1_max}** | ≥35 | {'✅ APROBADO' if score.tier1_score >= 35 else '❌ REPROBADO'} |
| **TIER 2: Componentes Funcionales** | **{score.tier2_score:.1f}/{score.tier2_max}** | ≥20 | {'✅ APROBADO' if score.tier2_score >= 20 else '❌ REPROBADO'} |
| **TIER 3: Componentes de Calidad** | **{score.tier3_score:.1f}/{score.tier3_max}** | ≥8 | {'✅ APROBADO' if score.tier3_score >= 8 else '❌ REPROBADO'} |
| **TOTAL** | **{score.total_score:.1f}/{score.total_max}** | ≥80 | {'✅ PRODUCCIÓN' if score.total_score >= 80 else '⚠️ MEJORAR'} |

**DECISIÓN DE TRIAGE**: **{decision.decision.value}**

**VEREDICTO**: {self._get_verdict_text(decision)}

---

## IDENTIDAD DEL CONTRATO

```json
{{
    "base_slot": "{identity.get('base_slot', 'N/A')}",
    "question_id": "{identity.get('question_id', 'N/A')}",
    "dimension_id": "{identity.get('dimension_id', 'N/A')}",
    "policy_area_id": "{identity.get('policy_area_id', 'N/A')}",
    "cluster_id": "{identity.get('cluster_id', 'N/A')}",
    "question_global": {identity.get('question_global', 'N/A')},
    "contract_version": "{identity.get('contract_version', 'N/A')}",
    "created_at": "{identity.get('created_at', 'N/A')}",
    "updated_at": "{identity.get('updated_at', 'N/A')}"
}}
```

---

## RATIONALE

{decision.rationale}

---

## DESGLOSE DETALLADO

### TIER 1: COMPONENTES CRÍTICOS - {score.tier1_score:.1f}/{score.tier1_max} pts

{self._generate_tier1_breakdown(decision, contract)}

### TIER 2: COMPONENTES FUNCIONALES - {score.tier2_score:.1f}/{score.tier2_max} pts

{self._generate_tier2_breakdown(decision, contract)}

### TIER 3: COMPONENTES DE CALIDAD - {score.tier3_score:.1f}/{score.tier3_max} pts

{self._generate_tier3_breakdown(decision, contract)}

---

## BLOCKERS CRÍTICOS

{self._format_blockers(decision.blockers)}

---

## ADVERTENCIAS

{self._format_warnings(decision.warnings)}

---

## RECOMENDACIONES

{self._format_recommendations(decision.recommendations)}

---

## PRÓXIMOS PASOS

{self._generate_next_steps(decision)}
"""

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

    def _get_verdict_text(self, decision: ContractTriageDecision) -> str:
        """Generate verdict text based on decision"""
        if decision.is_production_ready():
            return "✅ **CONTRATO LISTO PARA PRODUCCIÓN**"
        elif decision.can_be_patched():
            return f"⚠️ **CONTRATO REQUIERE PARCHES** ({len(decision.blockers)} blockers)"
        else:
            return f"❌ **CONTRATO REQUIERE REFORMULACIÓN** ({len(decision.blockers)} blockers críticos)"

    def _generate_tier1_breakdown(
        self, decision: ContractTriageDecision, contract: dict[str, Any]
    ) -> str:
        """Generate Tier 1 detailed breakdown"""
        identity = contract.get("identity", {})
        schema_props = contract.get("output_contract", {}).get("schema", {}).get("properties", {})
        
        # A1: Identity-Schema
        a1_details = "#### A1. Coherencia Identity-Schema (20 pts máx)\n\n"
        a1_details += "| Campo | Identity | Schema | Match |\n"
        a1_details += "|-------|----------|--------|-------|\n"
        
        fields = ["question_id", "policy_area_id", "dimension_id", "question_global", "base_slot"]
        for field in fields:
            id_val = identity.get(field, "N/A")
            schema_val = schema_props.get(field, {}).get("const", "N/A")
            match = "✅" if id_val == schema_val else "❌"
            a1_details += f"| {field} | {id_val} | {schema_val} | {match} |\n"
        
        # A2: Method-Assembly
        methods = contract.get("method_binding", {}).get("methods", [])
        assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
        
        a2_details = f"\n#### A2. Alineación Method-Assembly (20 pts máx)\n\n"
        a2_details += f"- **Métodos definidos**: {len(methods)}\n"
        a2_details += f"- **Reglas de ensamblaje**: {len(assembly_rules)}\n"
        
        if methods:
            provides_set = {m.get("provides", "") for m in methods if m.get("provides")}
            a2_details += f"- **Namespaces provistos**: {len(provides_set)}\n"
        
        # A3: Signal Requirements
        signal_req = contract.get("signal_requirements", {})
        threshold = signal_req.get("minimum_signal_threshold", 0.0)
        mandatory = signal_req.get("mandatory_signals", [])
        
        a3_details = f"\n#### A3. Requisitos de Señal (10 pts máx)\n\n"
        a3_details += f"- **Threshold mínimo**: {threshold}\n"
        a3_details += f"- **Señales obligatorias**: {len(mandatory)}\n"
        a3_details += f"- **Agregación**: {signal_req.get('signal_aggregation', 'N/A')}\n"
        
        if mandatory and threshold <= 0:
            a3_details += "\n⚠️ **CRÍTICO**: threshold=0 con señales obligatorias!\n"
        
        # A4: Output Schema
        schema = contract.get("output_contract", {}).get("schema", {})
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        a4_details = f"\n#### A4. Esquema de Salida (5 pts máx)\n\n"
        a4_details += f"- **Campos requeridos**: {len(required)}\n"
        a4_details += f"- **Propiedades definidas**: {len(properties)}\n"
        
        return a1_details + a2_details + a3_details + a4_details

    def _generate_tier2_breakdown(
        self, decision: ContractTriageDecision, contract: dict[str, Any]
    ) -> str:
        """Generate Tier 2 detailed breakdown"""
        patterns = contract.get("question_context", {}).get("patterns", [])
        expected = contract.get("question_context", {}).get("expected_elements", [])
        validation_rules = contract.get("validation_rules", {}).get("rules", [])
        
        breakdown = f"#### B1. Cobertura de Patrones (10 pts máx)\n\n"
        breakdown += f"- **Patrones definidos**: {len(patterns)}\n"
        breakdown += f"- **Elementos esperados**: {len(expected)}\n"
        
        breakdown += f"\n#### B2. Especificidad Metodológica (10 pts máx)\n\n"
        methods = contract.get("methodological_depth", {}).get("methods", [])
        breakdown += f"- **Métodos documentados**: {len(methods)}\n"
        
        breakdown += f"\n#### B3. Reglas de Validación (10 pts máx)\n\n"
        breakdown += f"- **Reglas definidas**: {len(validation_rules)}\n"
        
        return breakdown

    def _generate_tier3_breakdown(
        self, decision: ContractTriageDecision, contract: dict[str, Any]
    ) -> str:
        """Generate Tier 3 detailed breakdown"""
        identity = contract.get("identity", {})
        template = contract.get("output_contract", {}).get("human_readable_output", {}).get("template", {})
        
        breakdown = f"#### C1. Calidad de Documentación (5 pts máx)\n\n"
        methods = contract.get("methodological_depth", {}).get("methods", [])
        breakdown += f"- **Métodos con documentación epistemológica**: {len(methods)}\n"
        
        breakdown += f"\n#### C2. Template Legible (5 pts máx)\n\n"
        breakdown += f"- **Template título**: {bool(template.get('title'))}\n"
        breakdown += f"- **Template resumen**: {bool(template.get('summary'))}\n"
        
        breakdown += f"\n#### C3. Completitud de Metadata (5 pts máx)\n\n"
        breakdown += f"- **Contract hash**: {bool(identity.get('contract_hash'))}\n"
        breakdown += f"- **Created at**: {bool(identity.get('created_at'))}\n"
        breakdown += f"- **Version**: {identity.get('contract_version', 'N/A')}\n"
        
        return breakdown

    def _format_blockers(self, blockers: list[str]) -> str:
        """Format blockers list"""
        if not blockers:
            return "✅ **No se encontraron blockers críticos**\n"
        
        result = f"❌ **{len(blockers)} blocker(s) detectado(s)**:\n\n"
        for i, blocker in enumerate(blockers, 1):
            result += f"{i}. {blocker}\n"
        return result

    def _format_warnings(self, warnings: list[str]) -> str:
        """Format warnings list"""
        if not warnings:
            return "✅ **No se encontraron advertencias**\n"
        
        result = f"⚠️ **{len(warnings)} advertencia(s)**:\n\n"
        for i, warning in enumerate(warnings, 1):
            result += f"{i}. {warning}\n"
        return result

    def _format_recommendations(self, recommendations: list[dict[str, Any]]) -> str:
        """Format recommendations list"""
        if not recommendations:
            return "ℹ️ **No hay recomendaciones adicionales**\n"
        
        result = f"💡 **{len(recommendations)} recomendación(es)**:\n\n"
        for i, rec in enumerate(recommendations, 1):
            result += f"{i}. **[{rec.get('priority', 'MEDIUM')}]** {rec.get('component', 'N/A')}: "
            result += f"{rec.get('issue', 'N/A')}\n"
            result += f"   - **Fix**: {rec.get('fix', 'N/A')}\n"
            result += f"   - **Impact**: {rec.get('impact', 'N/A')}\n\n"
        return result

    def _generate_next_steps(self, decision: ContractTriageDecision) -> str:
        """Generate next steps based on decision"""
        if decision.is_production_ready():
            return """
### ✅ PRODUCCIÓN

Este contrato está listo para deployment:
1. Realizar revisión final de calidad
2. Ejecutar tests de integración
3. Desplegar a producción
"""
        elif decision.can_be_patched():
            return f"""
### ⚠️ PARCHEO REQUERIDO

Este contrato requiere correcciones menores antes de producción:
1. Resolver los {len(decision.blockers)} blocker(s) identificados
2. Aplicar las recomendaciones sugeridas
3. Re-ejecutar CQVR para verificar mejoras
4. Si score >= 80, aprobar para producción
"""
        else:
            return f"""
### ❌ REFORMULACIÓN REQUERIDA

Este contrato requiere trabajo sustancial:
1. Analizar los {len(decision.blockers)} blocker(s) críticos
2. Considerar regeneración desde monolito
3. Revisar alineación method-assembly
4. Validar coherencia identity-schema
5. Re-ejecutar CQVR post-reformulación
"""

    def _generate_batch_summary(self) -> None:
        """Generate consolidated batch summary report"""
        summary_path = self.config.output_dir / "BATCH_1_SUMMARY.md"

        # Calculate statistics
        total_evaluated = len(self.results)
        scores = [d.score.total_score for _, d, _ in self.results]
        avg_score = sum(scores) / len(scores) if scores else 0

        production_ready = sum(
            1 for _, d, _ in self.results if d.decision == TriageDecision.PRODUCCION
        )
        need_patches = sum(
            1 for _, d, _ in self.results if d.decision == TriageDecision.PARCHEAR
        )
        need_reformulation = sum(
            1 for _, d, _ in self.results if d.decision == TriageDecision.REFORMULAR
        )

        # Collect critical issues
        critical_findings = self._analyze_critical_findings()

        # Generate table
        results_table = self._generate_results_table()

        summary = f"""# 📊 BATCH 1 SUMMARY (Q001-Q025)

**Fecha de Evaluación**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Rúbrica**: CQVR v2.0  
**Evaluador**: CQVR Batch Evaluator

---

## RESUMEN ESTADÍSTICO

### Statistics
- **Total Evaluated**: {total_evaluated}
- **Average Score**: {avg_score:.1f}/100
- **Production Ready**: {production_ready}
- **Need Major Patches**: {need_patches}
- **Need Reformulation**: {need_reformulation}

### Distribución por Decisión

| Decisión | Cantidad | Porcentaje |
|----------|----------|------------|
| ✅ PRODUCCIÓN | {production_ready} | {(production_ready/total_evaluated*100):.1f}% |
| ⚠️ PARCHEAR | {need_patches} | {(need_patches/total_evaluated*100):.1f}% |
| ❌ REFORMULAR | {need_reformulation} | {(need_reformulation/total_evaluated*100):.1f}% |

---

## RESULTADOS INDIVIDUALES

{results_table}

---

## HALLAZGOS CRÍTICOS

{critical_findings}

---

## RECOMENDACIONES DE REMEDIACIÓN

{self._generate_remediation_recommendations()}

---

## MÉTRICAS DE CALIDAD

### Tier 1 (Componentes Críticos - 55 pts)
{self._generate_tier_stats(1)}

### Tier 2 (Componentes Funcionales - 30 pts)
{self._generate_tier_stats(2)}

### Tier 3 (Componentes de Calidad - 15 pts)
{self._generate_tier_stats(3)}

---

## CONCLUSIONES

{self._generate_conclusions(production_ready, need_patches, need_reformulation, total_evaluated)}
"""

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)

    def _generate_results_table(self) -> str:
        """Generate results table for all contracts"""
        table = "| Contract | Tier 1 | Tier 2 | Tier 3 | Total | Decision | Critical Issues |\n"
        table += "|----------|--------|--------|--------|-------|----------|-----------------|"

        for contract_id, decision, _ in self.results:
            score = decision.score
            critical_count = len(decision.blockers)
            critical_preview = ", ".join(decision.blockers[:2]) if decision.blockers else "None"
            if len(decision.blockers) > 2:
                critical_preview += f" (+{len(decision.blockers) - 2} more)"

            decision_text = decision.decision.value
            decision_icon = self._get_status_icon(decision.decision)

            table += f"\n| {contract_id}.v3 | {score.tier1_score:.0f}/{score.tier1_max:.0f} | "
            table += f"{score.tier2_score:.0f}/{score.tier2_max:.0f} | "
            table += f"{score.tier3_score:.0f}/{score.tier3_max:.0f} | "
            table += f"{score.total_score:.0f}/{score.total_max:.0f} | "
            table += f"{decision_icon} {decision_text} | {critical_preview} |"

        return table

    def _analyze_critical_findings(self) -> str:
        """Analyze and summarize critical findings across all contracts"""
        findings = []

        # Analyze blockers
        all_blockers = []
        for _, decision, _ in self.results:
            all_blockers.extend(decision.blockers)

        # Count specific issues
        orphan_sources_count = sum(1 for b in all_blockers if "orphan" in b.lower() or "assembly" in b.lower())
        signal_zero_count = sum(1 for b in all_blockers if "signal" in b.lower() and "0" in b)
        identity_mismatch_count = sum(1 for b in all_blockers if "identity" in b.lower() and "mismatch" in b.lower())
        schema_issues_count = sum(1 for b in all_blockers if "schema" in b.lower() and "required" in b.lower())

        if orphan_sources_count > 0:
            findings.append(f"1. **{orphan_sources_count} contratos** tienen sources de ensamblaje huérfanos (no en provides)")
        
        if signal_zero_count > 0:
            findings.append(f"2. **{signal_zero_count} contratos** tienen signal threshold = 0 (permite señales sin fuerza)")
        
        if identity_mismatch_count > 0:
            findings.append(f"3. **{identity_mismatch_count} contratos** tienen desajustes identity-schema")
        
        if schema_issues_count > 0:
            findings.append(f"4. **{schema_issues_count} contratos** tienen campos required sin definición en properties")

        # Add Tier 1 failures
        tier1_failures = sum(1 for _, d, _ in self.results if d.score.tier1_score < 35)
        if tier1_failures > 0:
            findings.append(f"5. **{tier1_failures} contratos** no alcanzan umbral Tier 1 (35 pts)")

        if not findings:
            return "✅ **No se encontraron problemas críticos generalizados**"

        return "\n".join(findings)

    def _generate_remediation_recommendations(self) -> str:
        """Generate remediation recommendations based on findings"""
        recommendations = []

        # Analyze what needs fixing
        reformulation_contracts = [
            cid for cid, d, _ in self.results if d.decision == TriageDecision.REFORMULAR
        ]
        patch_contracts = [
            cid for cid, d, _ in self.results if d.decision == TriageDecision.PARCHEAR
        ]

        if reformulation_contracts:
            recommendations.append(f"""
### 🔴 Alta Prioridad: Reformulación ({len(reformulation_contracts)} contratos)

Contratos que requieren regeneración desde monolito:
{', '.join(reformulation_contracts)}

**Acción**: Crear PRs de reformulación usando el generador de contratos v3.""")

        if patch_contracts:
            recommendations.append(f"""
### 🟡 Media Prioridad: Parcheo ({len(patch_contracts)} contratos)

Contratos que pueden corregirse con parches:
{', '.join(patch_contracts)}

**Acción**: Crear PRs de corrección enfocados en blockers específicos.""")

        if not recommendations:
            recommendations.append("✅ **Todos los contratos están listos para producción**")

        return "\n".join(recommendations)

    def _generate_tier_stats(self, tier: int) -> str:
        """Generate statistics for a specific tier"""
        if tier == 1:
            scores = [d.score.tier1_score for _, d, _ in self.results]
            max_score = 55
        elif tier == 2:
            scores = [d.score.tier2_score for _, d, _ in self.results]
            max_score = 30
        else:
            scores = [d.score.tier3_score for _, d, _ in self.results]
            max_score = 15

        avg = sum(scores) / len(scores) if scores else 0
        min_score = min(scores) if scores else 0
        max_score_achieved = max(scores) if scores else 0

        return f"""
- **Promedio**: {avg:.1f}/{max_score} ({avg/max_score*100:.1f}%)
- **Mínimo**: {min_score:.1f}/{max_score}
- **Máximo**: {max_score_achieved:.1f}/{max_score}
"""

    def _generate_conclusions(
        self, production: int, patches: int, reformulation: int, total: int
    ) -> str:
        """Generate conclusions based on results"""
        production_rate = (production / total * 100) if total > 0 else 0
        
        if production_rate >= 80:
            status = "✅ **EXCELENTE**"
            assessment = "La mayoría de contratos están listos para producción."
        elif production_rate >= 60:
            status = "✅ **BUENO**"
            assessment = "La mayoría de contratos requieren solo parches menores."
        elif production_rate >= 40:
            status = "⚠️ **ACEPTABLE**"
            assessment = "Aproximadamente la mitad de contratos necesitan trabajo significativo."
        else:
            status = "❌ **REQUIERE ATENCIÓN**"
            assessment = "La mayoría de contratos requieren reformulación o parches mayores."

        return f"""
### Estado General del Batch 1: {status}

{assessment}

**Tasa de aprobación para producción**: {production_rate:.1f}%

### Próximos pasos:
1. Revisar contratos que requieren reformulación
2. Aplicar parches a contratos que lo necesiten
3. Re-evaluar contratos modificados
4. Preparar deployment de contratos aprobados
"""


def main():
    """Main entry point for batch evaluator"""
    parser = argparse.ArgumentParser(
        description="CQVR Batch Evaluator - Evaluate executor contracts in batches"
    )
    parser.add_argument(
        "--batch",
        type=int,
        choices=list(BATCH_CONFIGS.keys()),
        required=True,
        help="Batch number to evaluate (1 = Q001-Q025)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Override output directory",
    )

    args = parser.parse_args()

    # Get batch configuration
    config = BATCH_CONFIGS[args.batch]
    
    # Override output dir if specified
    if args.output_dir:
        config.output_dir = args.output_dir

    # Make paths absolute
    base_dir = Path(__file__).parent.parent
    config.contracts_dir = base_dir / config.contracts_dir
    config.output_dir = base_dir / config.output_dir

    print(f"\n{'='*80}")
    print(f"CQVR Batch Evaluator v2.0")
    print(f"{'='*80}")
    print(f"Batch: {config.batch_number}")
    print(f"Contracts: Q{config.start_question:03d} - Q{config.end_question:03d}")
    print(f"Input: {config.contracts_dir}")
    print(f"Output: {config.output_dir}")
    print(f"{'='*80}\n")

    # Create evaluator and run
    evaluator = CQVRBatchEvaluator(config)
    evaluator.evaluate_batch()
    evaluator.generate_reports()

    print(f"\n{'='*80}")
    print("✅ Batch evaluation complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
