# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: Q196.v3.json
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
  "base_slot": "D4-Q1",
  "question_id": "Q196",
  "dimension_id": "DIM04",
  "policy_area_id": "PA06",
  "question_global": 196
}
```

**Output Schema const values**:
```json
{
  "base_slot": "D4-Q1",
  "question_id": "Q196",
  "dimension_id": "DIM04",
  "policy_area_id": "PA06",
  "question_global": 196
}
```

---

### A2. Alineación Method-Assembly [15/20 pts] ✅

**Method Count**: 16  
**Actual Methods**: 16

**Provides** (16 methods):
- pdet_analysis.extract_entities_syntax
- pdet_analysis.extract_entities_ner
- causal_extraction.calculate_language_specificity
- causal_extraction.calculate_composite_likelihood
- causal_extraction.calculate_semantic_distance
- temporallogicverifier.classify_temporal_type
- pdet_analysis.score_indicators
- pdet_analysis.find_outcome_mentions
- pdet_analysis.score_temporal_consistency
- causal_extraction.extract_goals
...

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

**Pattern count**: 9  
**Expected elements**: 4

### B2. Especificidad Metodológica [0/10 pts]

**Methodological depth**: Present

### B3. Reglas de Validación [5/10 pts]

**Validation rules**: 0

---

## TIER 3: COMPONENTES DE CALIDAD - 10/15 pts ✅

### C1. Documentación Epistemológica [3/5 pts]

### C2. Template Human-Readable [2/5 pts]

### C3. Metadatos y Trazabilidad [5/5 pts]

**Contract hash**: 46b6de02046a73c2...  
**Created at**: 2025-11-28T03:50:31.903464+00:00  
**Contract version**: 3.0.0

---

## CONCLUSIÓN

El contrato Q196.v3 obtiene **60/100 puntos** (**60.0%**).

**Estado**: ⚠️ MEJORAR  
**Decisión**: PARCHEAR_MAJOR

---

**Generado**: 2025-12-17T09:30:08.183149Z  
**Auditor**: CQVR Batch 8 Evaluator v1.0  
**Rúbrica**: CQVR v2.0
