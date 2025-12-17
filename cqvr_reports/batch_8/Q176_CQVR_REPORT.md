# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: Q176.v3.json
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
  "base_slot": "D6-Q1",
  "question_id": "Q176",
  "dimension_id": "DIM06",
  "policy_area_id": "PA05",
  "question_global": 176
}
```

**Output Schema const values**:
```json
{
  "base_slot": "D6-Q1",
  "question_id": "Q176",
  "dimension_id": "DIM06",
  "policy_area_id": "PA05",
  "question_global": 176
}
```

---

### A2. Alineación Method-Assembly [15/20 pts] ✅

**Method Count**: 8  
**Actual Methods**: 8

**Provides** (8 methods):
- teoriacambio.construir_grafo_causal
- teoriacambio.validacion_completa
- teoriacambio.export_nodes
- reportingengine.generate_causal_diagram
- reportingengine.generate_causal_model_json
- advanceddagvalidator.export_nodes
- pdet_analysis.export_causal_network
- causal_extraction.extract_causal_hierarchy


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

**Contract hash**: cbf452304e2c6c52...  
**Created at**: 2025-11-28T03:50:31.746232+00:00  
**Contract version**: 3.0.0

---

## CONCLUSIÓN

El contrato Q176.v3 obtiene **60/100 puntos** (**60.0%**).

**Estado**: ⚠️ MEJORAR  
**Decisión**: PARCHEAR_MAJOR

---

**Generado**: 2025-12-17T09:30:08.158779Z  
**Auditor**: CQVR Batch 8 Evaluator v1.0  
**Rúbrica**: CQVR v2.0
