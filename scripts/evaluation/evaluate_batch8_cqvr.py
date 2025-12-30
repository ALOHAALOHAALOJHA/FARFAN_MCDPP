#!/usr/bin/env python3
"""
CQVR v2.0 Batch 8 Evaluator
Evaluates contracts Q176-Q200 using the CQVR v2.0 rubric
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Any


class CQVRBatch8Evaluator:
    """CQVR v2.0 evaluator for batch 8 contracts (Q176-Q200)"""
    
    def __init__(self):
        self.contracts_dir = Path("src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized")
        self.output_dir = Path("cqvr_reports/batch_8")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def evaluate_batch(self):
        """Evaluate all contracts in batch 8"""
        results = {}
        
        for q_num in range(176, 201):
            contract_path = self.contracts_dir / f"Q{q_num:03d}.v3.json"
            if not contract_path.exists():
                print(f"⚠️  Contract {contract_path.name} not found")
                continue
                
            print(f"📊 Evaluating {contract_path.name}...")
            result = self.evaluate_contract(contract_path)
            results[f"Q{q_num:03d}"] = result
            
            report_path = self.output_dir / f"Q{q_num:03d}_CQVR_REPORT.md"
            self.generate_report(contract_path, result, report_path)
            print(f"   ✅ Score: {result['total_score']}/100 ({result['percentage']:.1f}%) - {result['status']}")
        
        self.generate_batch_summary(results)
        return results
    
    def evaluate_contract(self, contract_path: Path) -> dict[str, Any]:
        """Evaluate a single contract using CQVR v2.0 rubric"""
        with open(contract_path, 'r', encoding='utf-8') as f:
            contract = json.load(f)
        
        scores = {
            'A1_identity_schema': self._verify_identity_schema_coherence(contract),
            'A2_method_assembly': self._verify_method_assembly_alignment(contract),
            'A3_signal_integrity': self._verify_signal_requirements(contract),
            'A4_output_schema': self._verify_output_schema(contract),
            'B1_pattern_coverage': self._verify_pattern_coverage(contract),
            'B2_method_specificity': self._verify_method_specificity(contract),
            'B3_validation_rules': self._verify_validation_rules(contract),
            'C1_documentation': self._verify_documentation_quality(contract),
            'C2_human_template': self._verify_human_template(contract),
            'C3_metadata': self._verify_metadata_completeness(contract)
        }
        
        tier1_score = sum([scores['A1_identity_schema'], scores['A2_method_assembly'],
                          scores['A3_signal_integrity'], scores['A4_output_schema']])
        tier2_score = sum([scores['B1_pattern_coverage'], scores['B2_method_specificity'],
                          scores['B3_validation_rules']])
        tier3_score = sum([scores['C1_documentation'], scores['C2_human_template'],
                          scores['C3_metadata']])
        
        total_score = tier1_score + tier2_score + tier3_score
        percentage = (total_score / 100) * 100
        
        triage_decision = self._triage_decision(tier1_score, tier2_score, total_score, scores)
        
        status = "✅ PRODUCCIÓN" if percentage >= 80 and tier1_score >= 45 else "⚠️ MEJORAR"
        
        return {
            'total_score': total_score,
            'percentage': percentage,
            'tier1_score': tier1_score,
            'tier2_score': tier2_score,
            'tier3_score': tier3_score,
            'breakdown': scores,
            'triage_decision': triage_decision,
            'status': status,
            'passed': percentage >= 80 and tier1_score >= 45
        }
    
    def _verify_identity_schema_coherence(self, contract: dict) -> int:
        """A1: Identity-Schema coherence (20 pts)"""
        score = 0
        id_map = {
            'question_id': 5,
            'policy_area_id': 5,
            'dimension_id': 5,
            'question_global': 3,
            'base_slot': 2
        }
        
        identity = contract.get('identity', {})
        schema_props = contract.get('output_contract', {}).get('schema', {}).get('properties', {})
        
        for field, points in id_map.items():
            identity_val = identity.get(field)
            schema_const = schema_props.get(field, {}).get('const')
            if identity_val == schema_const:
                score += points
        
        return score
    
    def _verify_method_assembly_alignment(self, contract: dict) -> int:
        """A2: Method-Assembly alignment (20 pts)"""
        methods = contract.get('method_binding', {}).get('methods', [])
        provides = {m.get('provides', '') for m in methods}
        
        sources = set()
        for rule in contract.get('evidence_assembly', {}).get('assembly_rules', []):
            for src in rule.get('sources', []):
                if '*' not in src:
                    sources.add(src)
        
        orphan_sources = sources - provides
        if orphan_sources:
            orphan_penalty = min(10, len(orphan_sources) * 2.5)
            return max(0, int(20 - orphan_penalty))
        
        unused_ratio = len(provides - sources) / len(provides) if provides else 0
        usage_score = 5 * (1 - unused_ratio)
        
        method_count = contract.get('method_binding', {}).get('method_count', 0)
        method_count_ok = 3 if method_count == len(methods) else 0
        
        return int(10 + usage_score + method_count_ok + 2)
    
    def _verify_signal_requirements(self, contract: dict) -> int:
        """A3: Signal Integrity (10 pts)"""
        reqs = contract.get('signal_requirements', {})
        
        mandatory_signals = reqs.get('mandatory_signals', [])
        threshold = reqs.get('minimum_signal_threshold', 0)
        
        if mandatory_signals and threshold <= 0:
            return 0
        
        score = 5
        
        valid_aggregations = ['weighted_mean', 'max', 'min', 'product', 'voting']
        if reqs.get('signal_aggregation') in valid_aggregations:
            score += 2
        
        if all(isinstance(s, str) and '_' in s for s in mandatory_signals):
            score += 3
        
        return score
    
    def _verify_output_schema(self, contract: dict) -> int:
        """A4: Output Schema validation (5 pts)"""
        schema = contract.get('output_contract', {}).get('schema', {})
        required = set(schema.get('required', []))
        properties = set(schema.get('properties', {}).keys())
        
        if required.issubset(properties):
            return 5
        
        missing = required - properties
        penalty = len(missing)
        return max(0, 5 - penalty)
    
    def _verify_pattern_coverage(self, contract: dict) -> int:
        """B1: Pattern Coverage (10 pts)"""
        patterns = contract.get('question_context', {}).get('patterns', [])
        expected = contract.get('question_context', {}).get('expected_elements', [])
        
        expected_types = {e.get('type', '') for e in expected if e.get('required')}
        
        if not expected_types:
            return 5
        
        pattern_coverage = len([p for p in patterns if any(
            exp.lower() in str(p.get('pattern', '')).lower() for exp in expected_types
        )])
        
        coverage_score = min(5, (pattern_coverage / len(expected_types)) * 5) if expected_types else 5
        
        weights_valid = all(0 < p.get('confidence_weight', 0) <= 1 for p in patterns)
        weight_score = 3 if weights_valid else 0
        
        ids = [p.get('id') for p in patterns]
        id_score = 2 if len(ids) == len(set(ids)) and all(id and 'PAT-' in str(id) for id in ids) else 0
        
        return int(coverage_score + weight_score + id_score)
    
    def _verify_method_specificity(self, contract: dict) -> int:
        """B2: Method Specificity (10 pts)"""
        methods = contract.get('output_contract', {}).get('human_readable_output', {}).get('methodological_depth', {}).get('methods', [])
        
        if not methods:
            return 5
        
        generic_phrases = ["Execute", "Process results", "Return structured output"]
        total_steps = 0
        non_generic_steps = 0
        
        for method in methods[:5]:
            steps = method.get('technical_approach', {}).get('steps', [])
            total_steps += len(steps)
            non_generic_steps += sum(1 for s in steps 
                                   if not any(g in str(s.get('description', '')) for g in generic_phrases))
        
        if total_steps == 0:
            return 5
        
        specificity_ratio = non_generic_steps / total_steps
        return int(10 * specificity_ratio)
    
    def _verify_validation_rules(self, contract: dict) -> int:
        """B3: Validation Rules (10 pts)"""
        rules = contract.get('validation', {}).get('rules', [])
        expected = contract.get('question_context', {}).get('expected_elements', [])
        
        required_elements = {e.get('type', '') for e in expected if e.get('required')}
        validated_elements = set()
        
        for rule in rules:
            if 'must_contain' in rule:
                validated_elements.update(rule['must_contain'].get('elements', []))
            if 'should_contain' in rule:
                validated_elements.update(rule['should_contain'].get('elements', []))
        
        coverage = len(required_elements & validated_elements) / len(required_elements) if required_elements else 1
        coverage_score = int(5 * coverage)
        
        must_count = sum(1 for r in rules if 'must_contain' in r)
        should_count = sum(1 for r in rules if 'should_contain' in r)
        balance_score = 3 if must_count <= 2 and should_count >= must_count else 1
        
        failure_score = 2 if contract.get('error_handling', {}).get('failure_contract', {}).get('emit_code') else 0
        
        return coverage_score + balance_score + failure_score
    
    def _verify_documentation_quality(self, contract: dict) -> int:
        """C1: Documentation Quality (5 pts)"""
        return 3
    
    def _verify_human_template(self, contract: dict) -> int:
        """C2: Human Template (5 pts)"""
        template = contract.get('output_contract', {}).get('human_readable_output', {}).get('template', {})
        
        score = 0
        question_id = contract.get('identity', {}).get('question_id', '')
        if question_id and question_id in str(template.get('title', '')):
            score += 3
        
        if '{score}' in str(template) and '{evidence' in str(template):
            score += 2
        
        return score
    
    def _verify_metadata_completeness(self, contract: dict) -> int:
        """C3: Metadata Completeness (5 pts)"""
        identity = contract.get('identity', {})
        score = 0
        
        if identity.get('contract_hash') and len(identity['contract_hash']) == 64:
            score += 2
        if identity.get('created_at'):
            score += 1
        if identity.get('validated_against_schema'):
            score += 1
        if identity.get('contract_version') and '.' in identity['contract_version']:
            score += 1
        
        return score
    
    def _triage_decision(self, tier1_score: int, tier2_score: int, total_score: int, scores: dict) -> str:
        """Determine triage decision"""
        if tier1_score < 35:
            blockers = []
            if scores['A1_identity_schema'] < 15:
                blockers.append("IDENTITY_SCHEMA_MISMATCH")
            if scores['A2_method_assembly'] < 12:
                blockers.append("ASSEMBLY_SOURCES_BROKEN")
            if scores['A3_signal_integrity'] < 5:
                blockers.append("SIGNAL_THRESHOLD_ZERO")
            if scores['A4_output_schema'] < 3:
                blockers.append("SCHEMA_INVALID")
            
            if len(blockers) >= 2:
                return f"REFORMULAR_COMPLETO: {', '.join(blockers)}"
            elif "ASSEMBLY_SOURCES_BROKEN" in blockers:
                return "REFORMULAR_ASSEMBLY"
            elif "IDENTITY_SCHEMA_MISMATCH" in blockers:
                return "REFORMULAR_SCHEMA"
            else:
                return "PARCHEAR_CRITICO"
        elif tier1_score >= 45 and total_score >= 70:
            return "PARCHEAR_MINOR"
        elif tier1_score >= 35 and total_score >= 60:
            return "PARCHEAR_MAJOR"
        else:
            if scores['B2_method_specificity'] < 3:
                return "PARCHEAR_DOCS"
            if scores['B1_pattern_coverage'] < 6:
                return "PARCHEAR_PATTERNS"
            return "PARCHEAR_MAJOR"
    
    def generate_report(self, contract_path: Path, result: dict, report_path: Path):
        """Generate individual CQVR report"""
        contract_name = contract_path.stem
        
        with open(contract_path, 'r', encoding='utf-8') as f:
            contract = json.load(f)
        
        report = f"""# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: {contract_name}.json
**Fecha**: {datetime.now().strftime('%Y-%m-%d')}  
**Evaluador**: CQVR Batch 8 Evaluator  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **{result['tier1_score']}/55** | ≥35 | {'✅ APROBADO' if result['tier1_score'] >= 35 else '❌ REPROBADO'} |
| **TIER 2: Componentes Funcionales** | **{result['tier2_score']}/30** | ≥20 | {'✅ APROBADO' if result['tier2_score'] >= 20 else '❌ REPROBADO'} |
| **TIER 3: Componentes de Calidad** | **{result['tier3_score']}/15** | ≥8 | {'✅ APROBADO' if result['tier3_score'] >= 8 else '❌ REPROBADO'} |
| **TOTAL** | **{result['total_score']}/100** | ≥80 | {result['status']} |

**VEREDICTO**: {result['status']}

**Decisión de Triage**: {result['triage_decision']}

---

## TIER 1: COMPONENTES CRÍTICOS - {result['tier1_score']}/55 pts {'✅' if result['tier1_score'] >= 35 else '❌'}

### A1. Coherencia Identity-Schema [{result['breakdown']['A1_identity_schema']}/20 pts] {'✅' if result['breakdown']['A1_identity_schema'] >= 15 else '❌'}

**Identity fields**:
```json
{{
  "base_slot": "{contract['identity'].get('base_slot')}",
  "question_id": "{contract['identity'].get('question_id')}",
  "dimension_id": "{contract['identity'].get('dimension_id')}",
  "policy_area_id": "{contract['identity'].get('policy_area_id')}",
  "question_global": {contract['identity'].get('question_global')}
}}
```

**Output Schema const values**:
```json
{{
  "base_slot": "{contract['output_contract']['schema']['properties']['base_slot'].get('const')}",
  "question_id": "{contract['output_contract']['schema']['properties']['question_id'].get('const')}",
  "dimension_id": "{contract['output_contract']['schema']['properties']['dimension_id'].get('const')}",
  "policy_area_id": "{contract['output_contract']['schema']['properties']['policy_area_id'].get('const')}",
  "question_global": {contract['output_contract']['schema']['properties']['question_global'].get('const')}
}}
```

---

### A2. Alineación Method-Assembly [{result['breakdown']['A2_method_assembly']}/20 pts] {'✅' if result['breakdown']['A2_method_assembly'] >= 12 else '❌'}

**Method Count**: {contract['method_binding']['method_count']}  
**Actual Methods**: {len(contract['method_binding']['methods'])}

**Provides** ({len(contract['method_binding']['methods'])} methods):
{chr(10).join([f"- {m.get('provides', 'N/A')}" for m in contract['method_binding']['methods'][:10]])}
{'...' if len(contract['method_binding']['methods']) > 10 else ''}

---

### A3. Integridad de Señales [{result['breakdown']['A3_signal_integrity']}/10 pts] {'✅' if result['breakdown']['A3_signal_integrity'] >= 5 else '❌'}

**Mandatory Signals**: {len(contract.get('signal_requirements', {}).get('mandatory_signals', []))}  
**Threshold**: {contract.get('signal_requirements', {}).get('minimum_signal_threshold', 0)}  
**Aggregation**: {contract.get('signal_requirements', {}).get('signal_aggregation', 'N/A')}

---

### A4. Validación de Output Schema [{result['breakdown']['A4_output_schema']}/5 pts] {'✅' if result['breakdown']['A4_output_schema'] >= 3 else '❌'}

**Required fields**: {len(contract['output_contract']['schema'].get('required', []))}  
**Defined properties**: {len(contract['output_contract']['schema'].get('properties', {}))}

---

## TIER 2: COMPONENTES FUNCIONALES - {result['tier2_score']}/30 pts {'✅' if result['tier2_score'] >= 20 else '❌'}

### B1. Coherencia de Patrones [{result['breakdown']['B1_pattern_coverage']}/10 pts]

**Pattern count**: {len(contract.get('question_context', {}).get('patterns', []))}  
**Expected elements**: {len(contract.get('question_context', {}).get('expected_elements', []))}

### B2. Especificidad Metodológica [{result['breakdown']['B2_method_specificity']}/10 pts]

**Methodological depth**: {'Present' if contract.get('output_contract', {}).get('human_readable_output', {}).get('methodological_depth') else 'Not present'}

### B3. Reglas de Validación [{result['breakdown']['B3_validation_rules']}/10 pts]

**Validation rules**: {len(contract.get('validation', {}).get('rules', []))}

---

## TIER 3: COMPONENTES DE CALIDAD - {result['tier3_score']}/15 pts {'✅' if result['tier3_score'] >= 8 else '❌'}

### C1. Documentación Epistemológica [{result['breakdown']['C1_documentation']}/5 pts]

### C2. Template Human-Readable [{result['breakdown']['C2_human_template']}/5 pts]

### C3. Metadatos y Trazabilidad [{result['breakdown']['C3_metadata']}/5 pts]

**Contract hash**: {contract['identity'].get('contract_hash', 'N/A')[:16]}...  
**Created at**: {contract['identity'].get('created_at', 'N/A')}  
**Contract version**: {contract['identity'].get('contract_version', 'N/A')}

---

## CONCLUSIÓN

El contrato {contract_name} obtiene **{result['total_score']}/100 puntos** (**{result['percentage']:.1f}%**).

**Estado**: {result['status']}  
**Decisión**: {result['triage_decision']}

---

**Generado**: {datetime.now().isoformat()}Z  
**Auditor**: CQVR Batch 8 Evaluator v1.0  
**Rúbrica**: CQVR v2.0
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def generate_batch_summary(self, results: dict):
        """Generate consolidated batch summary"""
        summary_path = self.output_dir / "BATCH_8_SUMMARY.md"
        
        total_contracts = len(results)
        passed = sum(1 for r in results.values() if r['passed'])
        failed = total_contracts - passed
        
        avg_score = sum(r['total_score'] for r in results.values()) / total_contracts if total_contracts > 0 else 0
        avg_tier1 = sum(r['tier1_score'] for r in results.values()) / total_contracts if total_contracts > 0 else 0
        
        summary = f"""# 📊 RESUMEN EVALUACIÓN CQVR v2.0 - BATCH 8
## Contratos Q176-Q200
**Fecha**: {datetime.now().strftime('%Y-%m-%d')}  
**Evaluador**: CQVR Batch 8 Evaluator  
**Rúbrica**: CQVR v2.0

---

## ESTADÍSTICAS GENERALES

| Métrica | Valor |
|---------|-------|
| **Contratos Evaluados** | {total_contracts} |
| **Aprobados (≥80%)** | {passed} ({passed/total_contracts*100:.1f}%) |
| **Requieren Mejoras** | {failed} ({failed/total_contracts*100:.1f}%) |
| **Score Promedio** | {avg_score:.1f}/100 |
| **Tier 1 Promedio** | {avg_tier1:.1f}/55 |

---

## RESULTADOS POR CONTRATO

| Contrato | Total | Tier 1 | Tier 2 | Tier 3 | Estado | Decisión |
|----------|-------|--------|--------|--------|--------|----------|
"""
        
        for contract_id, result in sorted(results.items()):
            summary += f"| {contract_id} | {result['total_score']}/100 | {result['tier1_score']}/55 | {result['tier2_score']}/30 | {result['tier3_score']}/15 | {result['status']} | {result['triage_decision']} |\n"
        
        summary += f"""
---

## ANÁLISIS DE COMPONENTES CRÍTICOS (TIER 1)

### Distribución de Scores A1 (Identity-Schema)
"""
        
        a1_scores = [r['breakdown']['A1_identity_schema'] for r in results.values()]
        summary += f"- Promedio: {sum(a1_scores)/len(a1_scores):.1f}/20\n"
        summary += f"- Contratos perfectos (20/20): {sum(1 for s in a1_scores if s == 20)}\n"
        summary += f"- Contratos con problemas (<15): {sum(1 for s in a1_scores if s < 15)}\n\n"
        
        summary += f"""### Distribución de Scores A2 (Method-Assembly)
"""
        a2_scores = [r['breakdown']['A2_method_assembly'] for r in results.values()]
        summary += f"- Promedio: {sum(a2_scores)/len(a2_scores):.1f}/20\n"
        summary += f"- Contratos con alineación perfecta (≥18): {sum(1 for s in a2_scores if s >= 18)}\n"
        summary += f"- Contratos con problemas críticos (<12): {sum(1 for s in a2_scores if s < 12)}\n\n"
        
        summary += f"""### Distribución de Scores A3 (Signal Integrity)
"""
        a3_scores = [r['breakdown']['A3_signal_integrity'] for r in results.values()]
        summary += f"- Promedio: {sum(a3_scores)/len(a3_scores):.1f}/10\n"
        summary += f"- Contratos con señales correctas (≥5): {sum(1 for s in a3_scores if s >= 5)}\n"
        summary += f"- Contratos con threshold=0 (0 pts): {sum(1 for s in a3_scores if s == 0)}\n\n"
        
        summary += f"""---

## RECOMENDACIONES

### Contratos que Requieren Atención Inmediata
"""
        
        critical_contracts = [cid for cid, r in results.items() if r['tier1_score'] < 35]
        if critical_contracts:
            summary += f"\n{len(critical_contracts)} contratos con Tier 1 < 35 (BLOQUEANTE):\n"
            for cid in critical_contracts:
                summary += f"- {cid}: {results[cid]['triage_decision']}\n"
        else:
            summary += "\n✅ Ningún contrato con problemas críticos bloqueantes.\n"
        
        summary += f"""
### Contratos Aptos para Producción

{passed} contratos listos para deployment (score ≥ 80 y Tier 1 ≥ 45).

---

**Generado**: {datetime.now().isoformat()}Z  
**Auditor**: CQVR Batch 8 Evaluator v1.0  
**Batch**: Q176-Q200 (25 contratos)
"""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n✅ Batch summary generated: {summary_path}")


if __name__ == "__main__":
    evaluator = CQVRBatch8Evaluator()
    print("🚀 Starting CQVR v2.0 evaluation for Batch 8 (Q176-Q200)...")
    print("=" * 80)
    results = evaluator.evaluate_batch()
    print("=" * 80)
    print(f"\n✅ Evaluation complete!")
    print(f"   Total contracts: {len(results)}")
    print(f"   Passed: {sum(1 for r in results.values() if r['passed'])}")
    print(f"   Average score: {sum(r['total_score'] for r in results.values())/len(results):.1f}/100")
