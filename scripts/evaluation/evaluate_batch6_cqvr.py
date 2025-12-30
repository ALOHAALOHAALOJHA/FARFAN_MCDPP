#!/usr/bin/env python3
"""
CQVR v2.0 Batch Evaluator for Contracts Q126-Q150
Evaluates 25 contracts in batch 6 according to the CQVR v2.0 rubric.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class CQVRBatch6Evaluator:
    """Evaluates contracts Q126-Q150 using CQVR v2.0 criteria"""
    
    def __init__(self):
        self.contracts_dir = Path('src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized')
        self.reports_dir = Path('cqvr_reports/batch6')
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def evaluate_contract(self, contract_path: Path) -> Dict:
        """Evaluate a single contract according to CQVR v2.0 rubric"""
        with open(contract_path, 'r', encoding='utf-8') as f:
            contract = json.load(f)
        
        scores = {}
        
        # TIER 1: COMPONENTES CRÍTICOS (55 puntos)
        scores['A1_identity_schema'] = self._verify_identity_schema_coherence(contract)
        scores['A2_method_assembly'] = self._verify_method_assembly_alignment(contract)
        scores['A3_signal_integrity'] = self._verify_signal_requirements(contract)
        scores['A4_output_schema'] = self._verify_output_schema(contract)
        
        tier1_score = sum([
            scores['A1_identity_schema'],
            scores['A2_method_assembly'],
            scores['A3_signal_integrity'],
            scores['A4_output_schema']
        ])
        
        # TIER 2: COMPONENTES FUNCIONALES (30 puntos)
        scores['B1_pattern_coverage'] = self._verify_pattern_coverage(contract)
        scores['B2_method_specificity'] = self._verify_method_specificity(contract)
        scores['B3_validation_rules'] = self._verify_validation_rules(contract)
        
        tier2_score = sum([
            scores['B1_pattern_coverage'],
            scores['B2_method_specificity'],
            scores['B3_validation_rules']
        ])
        
        # TIER 3: COMPONENTES DE CALIDAD (15 puntos)
        scores['C1_documentation'] = self._verify_documentation_quality(contract)
        scores['C2_human_template'] = self._verify_human_template(contract)
        scores['C3_metadata'] = self._verify_metadata_completeness(contract)
        
        tier3_score = sum([
            scores['C1_documentation'],
            scores['C2_human_template'],
            scores['C3_metadata']
        ])
        
        total_score = tier1_score + tier2_score + tier3_score
        
        return {
            'contract_id': contract['identity']['question_id'],
            'scores': scores,
            'tier1_score': tier1_score,
            'tier2_score': tier2_score,
            'tier3_score': tier3_score,
            'total_score': total_score,
            'percentage': total_score,
            'verdict': self._get_verdict(tier1_score, tier2_score, tier3_score, total_score),
            'contract': contract
        }
    
    def _verify_identity_schema_coherence(self, contract: Dict) -> int:
        """A1. Coherencia Identity-Schema [20 puntos]"""
        score = 0
        identity = contract.get('identity', {})
        schema_props = contract.get('output_contract', {}).get('schema', {}).get('properties', {})
        
        id_map = {
            'question_id': 5,
            'policy_area_id': 5,
            'dimension_id': 5,
            'question_global': 3,
            'base_slot': 2
        }
        
        for field, points in id_map.items():
            identity_val = identity.get(field)
            schema_const = schema_props.get(field, {}).get('const')
            if identity_val == schema_const:
                score += points
        
        return score
    
    def _verify_method_assembly_alignment(self, contract: Dict) -> int:
        """A2. Alineación Method-Assembly [20 puntos]"""
        methods = contract.get('method_binding', {}).get('methods', [])
        provides = {m.get('provides') for m in methods if m.get('provides')}
        
        assembly_rules = contract.get('evidence_assembly', {}).get('assembly_rules', [])
        sources = set()
        for rule in assembly_rules:
            sources.update(rule.get('sources', []))
        
        # Penalización severa por sources huérfanos
        orphan_sources = sources - provides
        if orphan_sources:
            orphan_penalty = min(10, len(orphan_sources) * 2.5)
            return max(0, int(20 - orphan_penalty))
        
        # Score completo si no hay huérfanos
        unused_ratio = len(provides - sources) / len(provides) if provides else 0
        usage_score = 5 * (1 - unused_ratio)
        
        method_count_ok = 3 if contract.get('method_binding', {}).get('method_count') == len(methods) else 0
        
        return int(10 + usage_score + method_count_ok + 2)
    
    def _verify_signal_requirements(self, contract: Dict) -> int:
        """A3. Integridad de Señales [10 puntos]"""
        reqs = contract.get('signal_requirements', {})
        
        # Verificación bloqueante
        mandatory_signals = reqs.get('mandatory_signals', [])
        threshold = reqs.get('minimum_signal_threshold', 0)
        
        if mandatory_signals and threshold <= 0:
            return 0  # FALLO TOTAL
        
        score = 5  # Pasó verificación crítica
        
        # Verificaciones adicionales
        valid_aggregations = ['weighted_mean', 'max', 'min', 'product', 'voting']
        if reqs.get('signal_aggregation') in valid_aggregations:
            score += 2
        
        # Signals bien formadas
        if all(isinstance(s, str) and '_' in s for s in mandatory_signals):
            score += 3
        
        return score
    
    def _verify_output_schema(self, contract: Dict) -> int:
        """A4. Validación de Output Schema [5 puntos]"""
        schema = contract.get('output_contract', {}).get('schema', {})
        required = set(schema.get('required', []))
        properties = set(schema.get('properties', {}).keys())
        
        if required.issubset(properties):
            return 5
        
        missing = required - properties
        penalty = len(missing)
        return max(0, 5 - penalty)
    
    def _verify_pattern_coverage(self, contract: Dict) -> int:
        """B1. Coherencia de Patrones [10 puntos]"""
        patterns = contract.get('question_context', {}).get('patterns', [])
        expected = contract.get('question_context', {}).get('expected_elements', [])
        
        if not patterns:
            return 0
        
        # Cobertura de elementos esperados
        expected_types = {e.get('type') for e in expected if e.get('required')}
        pattern_coverage = len([p for p in patterns if any(
            str(exp).lower() in str(p.get('pattern', '')).lower() for exp in expected_types
        )]) if expected_types else len(patterns)
        
        coverage_score = min(5, (pattern_coverage / max(len(expected_types), 1)) * 5)
        
        # Validar confidence weights
        weights_valid = all(0 < p.get('confidence_weight', 0) <= 1 for p in patterns)
        weight_score = 3 if weights_valid else 0
        
        # IDs únicos
        ids = [p.get('id') for p in patterns]
        id_score = 2 if len(ids) == len(set(ids)) and all(id and 'PAT-' in str(id) for id in ids) else 0
        
        return int(coverage_score + weight_score + id_score)
    
    def _verify_method_specificity(self, contract: Dict) -> int:
        """B2. Especificidad Metodológica [10 puntos]"""
        methods = contract.get('output_contract', {}).get('human_readable_output', {}).get('methodological_depth', {}).get('methods', [])
        
        if not methods:
            return 5  # Score neutral si no hay methodological_depth
        
        generic_phrases = ["Execute", "Process results", "Return structured output"]
        total_steps = 0
        non_generic_steps = 0
        
        for method in methods[:5]:
            steps = method.get('technical_approach', {}).get('steps', [])
            total_steps += len(steps)
            non_generic_steps += sum(1 for s in steps 
                                     if not any(g in s.get('description', '') for g in generic_phrases))
        
        specificity_ratio = non_generic_steps / total_steps if total_steps > 0 else 0.5
        return int(10 * specificity_ratio)
    
    def _verify_validation_rules(self, contract: Dict) -> int:
        """B3. Reglas de Validación [10 puntos]"""
        rules = contract.get('validation', {}).get('rules', [])
        expected = contract.get('question_context', {}).get('expected_elements', [])
        
        if not rules:
            return 0
        
        required_elements = {e.get('type') for e in expected if e.get('required')}
        validated_elements = set()
        
        for rule in rules:
            if 'must_contain' in rule:
                validated_elements.update(rule['must_contain'].get('elements', []))
            if 'should_contain' in rule:
                validated_elements.update(rule['should_contain'].get('elements', []))
        
        coverage = len(required_elements & validated_elements) / len(required_elements) if required_elements else 1
        coverage_score = int(5 * coverage)
        
        # Balance must vs should
        must_count = sum(1 for r in rules if 'must_contain' in r)
        should_count = sum(1 for r in rules if 'should_contain' in r)
        balance_score = 3 if must_count <= 2 and should_count >= must_count else 1
        
        # Failure contract
        failure_score = 2 if contract.get('error_handling', {}).get('failure_contract', {}).get('emit_code') else 0
        
        return coverage_score + balance_score + failure_score
    
    def _verify_documentation_quality(self, contract: Dict) -> int:
        """C1. Documentación Epistemológica [5 puntos]"""
        return 3  # Score neutral
    
    def _verify_human_template(self, contract: Dict) -> int:
        """C2. Template Human-Readable [5 puntos]"""
        template = contract.get('output_contract', {}).get('human_readable_output', {}).get('template', {})
        
        score = 0
        question_id = contract['identity']['question_id']
        if question_id in str(template.get('title', '')):
            score += 3
        
        if '{score}' in str(template) and '{evidence' in str(template):
            score += 2
        
        return score
    
    def _verify_metadata_completeness(self, contract: Dict) -> int:
        """C3. Metadatos y Trazabilidad [5 puntos]"""
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
    
    def _get_verdict(self, tier1: int, tier2: int, tier3: int, total: int) -> Dict:
        """Determine verdict based on tier scores"""
        if tier1 < 35:
            return {
                'decision': 'REFORMULAR',
                'reason': f'Tier 1 ({tier1}/55) < 35 - Critical components fail',
                'status': '❌'
            }
        elif tier1 >= 45 and total >= 70:
            return {
                'decision': 'PARCHEAR_MINOR',
                'reason': 'Minor patches needed',
                'status': '✅' if total >= 80 else '⚠️'
            }
        elif tier1 >= 35 and total >= 60:
            return {
                'decision': 'PARCHEAR_MAJOR',
                'reason': 'Major patches needed',
                'status': '⚠️'
            }
        else:
            return {
                'decision': 'REFORMULAR',
                'reason': 'Below minimum thresholds',
                'status': '❌'
            }
    
    def generate_report(self, result: Dict) -> str:
        """Generate CQVR report for a single contract"""
        contract_id = result['contract_id']
        scores = result['scores']
        tier1 = result['tier1_score']
        tier2 = result['tier2_score']
        tier3 = result['tier3_score']
        total = result['total_score']
        verdict = result['verdict']
        
        report = f"""# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: {contract_id}.v3.json
**Fecha**: {datetime.now().strftime('%Y-%m-%d')}  
**Evaluador**: CQVR Batch 6 Evaluator  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **{tier1}/55** | ≥35 | {'✅ APROBADO' if tier1 >= 35 else '❌ REPROBADO'} |
| **TIER 2: Componentes Funcionales** | **{tier2}/30** | ≥20 | {'✅ APROBADO' if tier2 >= 20 else '❌ REPROBADO'} |
| **TIER 3: Componentes de Calidad** | **{tier3}/15** | ≥8 | {'✅ APROBADO' if tier3 >= 8 else '❌ REPROBADO'} |
| **TOTAL** | **{total}/100** | ≥80 | {'✅ PRODUCCIÓN' if total >= 80 else '⚠️ MEJORAR'} |

**VEREDICTO**: {verdict['status']} **{verdict['decision']}**

{verdict['reason']}

---

## DESGLOSE DETALLADO

### TIER 1: COMPONENTES CRÍTICOS - {tier1}/55 pts

#### A1. Coherencia Identity-Schema [{scores['A1_identity_schema']}/20 pts]
Verificación de coherencia entre campos de identity y output_contract.schema.

#### A2. Alineación Method-Assembly [{scores['A2_method_assembly']}/20 pts]
Verificación de que assembly_rules.sources existen en method_binding.methods[].provides.

#### A3. Integridad de Señales [{scores['A3_signal_integrity']}/10 pts]
Verificación de signal_requirements con threshold > 0.

#### A4. Output Schema [{scores['A4_output_schema']}/5 pts]
Verificación de que todos los campos required están definidos en properties.

### TIER 2: COMPONENTES FUNCIONALES - {tier2}/30 pts

#### B1. Coherencia de Patrones [{scores['B1_pattern_coverage']}/10 pts]
Verificación de coverage, confidence weights e IDs únicos.

#### B2. Especificidad Metodológica [{scores['B2_method_specificity']}/10 pts]
Verificación de que los steps no son genéricos.

#### B3. Reglas de Validación [{scores['B3_validation_rules']}/10 pts]
Verificación de rules, must_contain, should_contain y failure_contract.

### TIER 3: COMPONENTES DE CALIDAD - {tier3}/15 pts

#### C1. Documentación Epistemológica [{scores['C1_documentation']}/5 pts]
Verificación de paradigma, justificación y referencias.

#### C2. Template Human-Readable [{scores['C2_human_template']}/5 pts]
Verificación de referencias correctas y placeholders válidos.

#### C3. Metadatos y Trazabilidad [{scores['C3_metadata']}/5 pts]
Verificación de contract_hash, timestamps y versionado.

---

## MATRIZ DE DECISIÓN

| Tier 1 Score | Total Score | DECISIÓN |
|-------------|------------|----------|
| {tier1}/55 ({tier1/55*100:.1f}%) | {total}/100 ({total}%) | **{verdict['decision']}** |

---

## CONCLUSIÓN

El contrato {contract_id}.v3.json obtiene **{total}/100 puntos** ({total}%).

**Estado**: {verdict['status']} {verdict['decision']}
**Razón**: {verdict['reason']}

---

**Generado**: {datetime.now().isoformat()}Z  
**Batch**: 6 (Q126-Q150)  
**Rúbrica**: CQVR v2.0
"""
        return report
    
    def evaluate_batch(self) -> Dict:
        """Evaluate all contracts in batch 6 (Q126-Q150)"""
        results = []
        
        for qnum in range(126, 151):
            contract_path = self.contracts_dir / f"Q{qnum:03d}.v3.json"
            
            if not contract_path.exists():
                print(f"⚠️  Contract {contract_path.name} not found, skipping...")
                continue
            
            print(f"Evaluating {contract_path.name}...")
            result = self.evaluate_contract(contract_path)
            results.append(result)
            
            # Generate individual report
            report = self.generate_report(result)
            report_path = self.reports_dir / f"{result['contract_id']}_CQVR_EVALUATION_REPORT.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"  ✅ {result['contract_id']}: {result['total_score']}/100 - {result['verdict']['decision']}")
        
        return {
            'batch': 6,
            'range': 'Q126-Q150',
            'total_contracts': len(results),
            'results': results
        }
    
    def generate_batch_summary(self, batch_results: Dict) -> str:
        """Generate summary report for entire batch"""
        results = batch_results['results']
        
        total_contracts = len(results)
        avg_total = sum(r['total_score'] for r in results) / total_contracts if total_contracts > 0 else 0
        avg_tier1 = sum(r['tier1_score'] for r in results) / total_contracts if total_contracts > 0 else 0
        avg_tier2 = sum(r['tier2_score'] for r in results) / total_contracts if total_contracts > 0 else 0
        avg_tier3 = sum(r['tier3_score'] for r in results) / total_contracts if total_contracts > 0 else 0
        
        production_ready = sum(1 for r in results if r['total_score'] >= 80)
        needs_minor = sum(1 for r in results if 70 <= r['total_score'] < 80)
        needs_major = sum(1 for r in results if 60 <= r['total_score'] < 70)
        needs_reformulate = sum(1 for r in results if r['total_score'] < 60 or r['tier1_score'] < 35)
        
        summary = f"""# 📊 BATCH 6 CQVR EVALUATION SUMMARY
## Contracts Q126-Q150

**Evaluation Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Total Contracts Evaluated**: {total_contracts}/25  
**Rúbrica**: CQVR v2.0

---

## AGGREGATE STATISTICS

| Tier | Average Score | Max Possible |
|------|--------------|--------------|
| **Tier 1 (Critical)** | {avg_tier1:.1f} | 55 |
| **Tier 2 (Functional)** | {avg_tier2:.1f} | 30 |
| **Tier 3 (Quality)** | {avg_tier3:.1f} | 15 |
| **TOTAL** | **{avg_total:.1f}** | **100** |

---

## DISTRIBUTION BY VERDICT

| Category | Count | Percentage |
|----------|-------|------------|
| ✅ Production Ready (≥80) | {production_ready} | {production_ready/total_contracts*100:.1f}% |
| ⚠️ Minor Patches (70-79) | {needs_minor} | {needs_minor/total_contracts*100:.1f}% |
| ⚠️ Major Patches (60-69) | {needs_major} | {needs_major/total_contracts*100:.1f}% |
| ❌ Reformulate (<60 or Tier1<35) | {needs_reformulate} | {needs_reformulate/total_contracts*100:.1f}% |

---

## INDIVIDUAL RESULTS

| Contract | Tier 1 | Tier 2 | Tier 3 | Total | Verdict |
|----------|--------|--------|--------|-------|---------|
"""
        
        for r in results:
            status_icon = r['verdict']['status']
            summary += f"| {r['contract_id']} | {r['tier1_score']}/55 | {r['tier2_score']}/30 | {r['tier3_score']}/15 | **{r['total_score']}/100** | {status_icon} {r['verdict']['decision']} |\n"
        
        summary += f"""
---

## RECOMMENDATIONS

### Production Ready ({production_ready} contracts)
These contracts can be deployed immediately.

### Needs Minor Patches ({needs_minor} contracts)
Focus on improving Tier 2 and Tier 3 components.

### Needs Major Patches ({needs_major} contracts)
Significant work needed on Tier 1 critical components.

### Needs Reformulation ({needs_reformulate} contracts)
Recommend regenerating from scratch using ContractGenerator.

---

**Report Generated**: {datetime.now().isoformat()}Z  
**Evaluator**: CQVR Batch 6 Evaluator v1.0
"""
        
        return summary


def main():
    """Main execution function"""
    print("=" * 80)
    print("CQVR v2.0 Batch 6 Evaluator")
    print("Evaluating contracts Q126-Q150")
    print("=" * 80)
    print()
    
    evaluator = CQVRBatch6Evaluator()
    batch_results = evaluator.evaluate_batch()
    
    print()
    print("=" * 80)
    print("Generating batch summary...")
    print("=" * 80)
    
    summary = evaluator.generate_batch_summary(batch_results)
    summary_path = evaluator.reports_dir / 'BATCH6_SUMMARY.md'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n✅ Batch summary saved to: {summary_path}")
    print(f"✅ Individual reports saved to: {evaluator.reports_dir}/")
    print(f"\nEvaluated {batch_results['total_contracts']} contracts")
    print(f"Average score: {sum(r['total_score'] for r in batch_results['results']) / batch_results['total_contracts']:.1f}/100")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
