# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: Q183.v3.json
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
  "base_slot": "D1-Q3",
  "question_id": "Q183",
  "dimension_id": "DIM01",
  "policy_area_id": "PA06",
  "question_global": 183
}
```

**Output Schema const values**:
```json
{
  "base_slot": "D1-Q3",
  "question_id": "Q183",
  "dimension_id": "DIM01",
  "policy_area_id": "PA06",
  "question_global": 183
}
```

---

### A2. Alineación Method-Assembly [15/20 pts] ✅

**Method Count**: 13  
**Actual Methods**: 13

**Provides** (13 methods):
- financial_audit.trace_financial_allocation
- financial_audit.process_financial_table
- financial_audit.match_program_to_node
- financial_audit.match_goal_to_budget
- financial_audit.perform_counterfactual_budget_check
- financial_audit.calculate_sufficiency
- pdet_analysis.analyze_financial_feasibility
- pdet_analysis.extract_budget_for_pillar
- pdet_analysis.identify_funding_source
- pdet_analysis.classify_tables
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
**Expected elements**: 3

### B2. Especificidad Metodológica [0/10 pts]

**Methodological depth**: Present

### B3. Reglas de Validación [5/10 pts]

**Validation rules**: 0

---

## TIER 3: COMPONENTES DE CALIDAD - 10/15 pts ✅

### C1. Documentación Epistemológica [3/5 pts]

### C2. Template Human-Readable [2/5 pts]

### C3. Metadatos y Trazabilidad [5/5 pts]

**Contract hash**: 557dc959f12e8583...  
**Created at**: 2025-11-28T03:50:31.855498+00:00  
**Contract version**: 3.0.0

---

## CONCLUSIÓN

El contrato Q183.v3 obtiene **60/100 puntos** (**60.0%**).

**Estado**: ⚠️ MEJORAR  
**Decisión**: PARCHEAR_MAJOR

---

**Generado**: 2025-12-17T09:30:08.166854Z  
**Auditor**: CQVR Batch 8 Evaluator v1.0  
**Rúbrica**: CQVR v2.0
