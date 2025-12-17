# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: Q195.v3.json
**Fecha**: 2025-12-17  
**Evaluador**: CQVR Batch 8 Evaluator  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **50/55** | ≥35 | ✅ APROBADO |
| **TIER 2: Componentes Funcionales** | **15/30** | ≥20 | ❌ REPROBADO |
| **TIER 3: Componentes de Calidad** | **10/15** | ≥8 | ✅ APROBADO |
| **TOTAL** | **75/100** | ≥80 | ⚠️ MEJORAR |

**VEREDICTO**: ⚠️ MEJORAR

**Decisión de Triage**: PARCHEAR_MINOR

---

## TIER 1: COMPONENTES CRÍTICOS - 50/55 pts ✅

### A1. Coherencia Identity-Schema [20/20 pts] ✅

**Identity fields**:
```json
{
  "base_slot": "D3-Q5",
  "question_id": "Q195",
  "dimension_id": "DIM03",
  "policy_area_id": "PA06",
  "question_global": 195
}
```

**Output Schema const values**:
```json
{
  "base_slot": "D3-Q5",
  "question_id": "Q195",
  "dimension_id": "DIM03",
  "policy_area_id": "PA06",
  "question_global": 195
}
```

---

### A2. Alineación Method-Assembly [15/20 pts] ✅

**Method Count**: 25  
**Actual Methods**: 25

**Provides** (25 methods):
- pdet_analysis.identify_confounders
- pdet_analysis.effect_to_dict
- pdet_analysis.scenario_to_dict
- pdet_analysis.simulate_intervention
- pdet_analysis.generate_recommendations
- pdet_analysis.identify_causal_nodes
- bayesiancounterfactualauditor.evaluate_factual
- bayesiancounterfactualauditor.evaluate_counterfactual
- causal_extraction.assess_financial_consistency
- bayesianmechanisminference.infer_activity_sequence
...

---

### A3. Integridad de Señales [10/10 pts] ✅

**Mandatory Signals**: 5  
**Threshold**: 0.5  
**Aggregation**: weighted_mean

---

### A4. Validación de Output Schema [5/5 pts] ✅

**Required fields**: 5  
**Defined properties**: 10

---

## TIER 2: COMPONENTES FUNCIONALES - 15/30 pts ❌

### B1. Coherencia de Patrones [5/10 pts]

**Pattern count**: 6  
**Expected elements**: 2

### B2. Especificidad Metodológica [0/10 pts]

**Methodological depth**: Present

### B3. Reglas de Validación [10/10 pts]

**Validation rules**: 3

---

## TIER 3: COMPONENTES DE CALIDAD - 10/15 pts ✅

### C1. Documentación Epistemológica [3/5 pts]

### C2. Template Human-Readable [2/5 pts]

### C3. Metadatos y Trazabilidad [5/5 pts]

**Contract hash**: 1dfa37c6ac35bf3b...  
**Created at**: 2025-11-28T03:50:31.898846+00:00  
**Contract version**: 3.0.0

---

## CONCLUSIÓN

El contrato Q195.v3 obtiene **75/100 puntos** (**75.0%**).

**Estado**: ⚠️ MEJORAR  
**Decisión**: PARCHEAR_MINOR

---

**Generado**: 2025-12-17T14:45:14.473596Z  
**Auditor**: CQVR Batch 8 Evaluator v1.0  
**Rúbrica**: CQVR v2.0
