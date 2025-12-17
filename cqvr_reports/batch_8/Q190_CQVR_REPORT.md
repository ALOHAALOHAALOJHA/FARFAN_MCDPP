# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: Q190.v3.json
**Fecha**: 2025-12-17  
**Evaluador**: CQVR Batch 8 Evaluator  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **40/55** | ≥35 | ✅ APROBADO |
| **TIER 2: Componentes Funcionales** | **10/30** | ≥20 | ❌ REPROBADO |
| **TIER 3: Componentes de Calidad** | **10/15** | ≥8 | ✅ APROBADO |
| **TOTAL** | **60/100** | ≥80 | ⚠️ MEJORAR |

**VEREDICTO**: ⚠️ MEJORAR

**Decisión de Triage**: PARCHEAR_MAJOR

---

## TIER 1: COMPONENTES CRÍTICOS - 40/55 pts ✅

### A1. Coherencia Identity-Schema [20/20 pts] ✅

**Identity fields**:
```json
{
  "base_slot": "D2-Q5",
  "question_id": "Q190",
  "dimension_id": "DIM02",
  "policy_area_id": "PA06",
  "question_global": 190
}
```

**Output Schema const values**:
```json
{
  "base_slot": "D2-Q5",
  "question_id": "Q190",
  "dimension_id": "DIM02",
  "policy_area_id": "PA06",
  "question_global": 190
}
```

---

### A2. Alineación Method-Assembly [15/20 pts] ✅

**Method Count**: 8  
**Actual Methods**: 8

**Provides** (8 methods):
- contradiction_detection.detect_logical_incompatibilities
- contradiction_detection.calculate_coherence_metrics
- contradiction_detection.calculate_objective_alignment
- contradiction_detection.calculate_graph_fragmentation
- operationalizationauditor.audit_sequence_logic
- bayesianmechanisminference.calculate_coherence_factor
- pdet_analysis.score_causal_coherence
- adaptivepriorcalculator.calculate_likelihood_adaptativo


---

### A3. Integridad de Señales [0/10 pts] ❌

**Mandatory Signals**: 5  
**Threshold**: 0.0  
**Aggregation**: weighted_mean

---

### A4. Validación de Output Schema [5/5 pts] ✅

**Required fields**: 5  
**Defined properties**: 10

---

## TIER 2: COMPONENTES FUNCIONALES - 10/30 pts ❌

### B1. Coherencia de Patrones [5/10 pts]

**Pattern count**: 6  
**Expected elements**: 2

### B2. Especificidad Metodológica [0/10 pts]

**Methodological depth**: Present

### B3. Reglas de Validación [5/10 pts]

**Validation rules**: 0

---

## TIER 3: COMPONENTES DE CALIDAD - 10/15 pts ✅

### C1. Documentación Epistemológica [3/5 pts]

### C2. Template Human-Readable [2/5 pts]

### C3. Metadatos y Trazabilidad [5/5 pts]

**Contract hash**: fca65e85c83a3917...  
**Created at**: 2025-11-28T03:50:31.877743+00:00  
**Contract version**: 3.0.0

---

## CONCLUSIÓN

El contrato Q190.v3 obtiene **60/100 puntos** (**60.0%**).

**Estado**: ⚠️ MEJORAR  
**Decisión**: PARCHEAR_MAJOR

---

**Generado**: 2025-12-17T09:30:08.174169Z  
**Auditor**: CQVR Batch 8 Evaluator v1.0  
**Rúbrica**: CQVR v2.0
