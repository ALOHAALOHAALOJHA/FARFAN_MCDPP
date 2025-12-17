# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: Q009.v3.json
**Fecha**: 2025-12-17  
**Evaluador**: CQVR Batch Evaluator v2.0  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **39.0/55.0** | ≥35 | ✅ APROBADO |
| **TIER 2: Componentes Funcionales** | **15.0/30.0** | ≥20 | ❌ REPROBADO |
| **TIER 3: Componentes de Calidad** | **7.0/15.0** | ≥8 | ❌ REPROBADO |
| **TOTAL** | **61.0/100.0** | ≥80 | ⚠️ MEJORAR |

**DECISIÓN DE TRIAGE**: **REFORMULAR**

**VEREDICTO**: ❌ **CONTRATO REQUIERE REFORMULACIÓN** (1 blockers críticos)

---

## IDENTIDAD DEL CONTRATO

```json
{
    "base_slot": "D2-Q4",
    "question_id": "Q009",
    "dimension_id": "DIM02",
    "policy_area_id": "PA01",
    "cluster_id": "CL02",
    "question_global": 9,
    "contract_version": "3.0.0",
    "created_at": "2025-11-28T03:49:29.807482+00:00",
    "updated_at": "2025-12-16T04:42:57.352361+00:00"
}
```

---

## RATIONALE

Contract requires reformulation: Tier 1: 39.0/55.0 (70.9%) < threshold 35.0, Total: 61.0/100.0 (61.0%). Critical blockers: 1. Contract needs substantial rework.

---

## DESGLOSE DETALLADO

### TIER 1: COMPONENTES CRÍTICOS - 39.0/55.0 pts

#### A1. Coherencia Identity-Schema (20 pts máx)

| Campo | Identity | Schema | Match |
|-------|----------|--------|-------|
| question_id | Q009 | Q009 | ✅ |
| policy_area_id | PA01 | PA01 | ✅ |
| dimension_id | DIM02 | DIM02 | ✅ |
| question_global | 9 | 9 | ✅ |
| base_slot | D2-Q4 | D2-Q4 | ✅ |

#### A2. Alineación Method-Assembly (20 pts máx)

- **Métodos definidos**: 10
- **Reglas de ensamblaje**: 4
- **Namespaces provistos**: 10

#### A3. Requisitos de Señal (10 pts máx)

- **Threshold mínimo**: 0.0
- **Señales obligatorias**: 5
- **Agregación**: weighted_mean

⚠️ **CRÍTICO**: threshold=0 con señales obligatorias!

#### A4. Esquema de Salida (5 pts máx)

- **Campos requeridos**: 5
- **Propiedades definidas**: 10


### TIER 2: COMPONENTES FUNCIONALES - 15.0/30.0 pts

#### B1. Cobertura de Patrones (10 pts máx)

- **Patrones definidos**: 9
- **Elementos esperados**: 2

#### B2. Especificidad Metodológica (10 pts máx)

- **Métodos documentados**: 0

#### B3. Reglas de Validación (10 pts máx)

- **Reglas definidas**: 2


### TIER 3: COMPONENTES DE CALIDAD - 7.0/15.0 pts

#### C1. Calidad de Documentación (5 pts máx)

- **Métodos con documentación epistemológica**: 0

#### C2. Template Legible (5 pts máx)

- **Template título**: True
- **Template resumen**: True

#### C3. Completitud de Metadata (5 pts máx)

- **Contract hash**: True
- **Created at**: True
- **Version**: 3.0.0


---

## BLOCKERS CRÍTICOS

❌ **1 blocker(s) detectado(s)**:

1. A3: CRITICAL - minimum_signal_threshold=0.0 but mandatory_signals defined. This allows zero-strength signals to pass validation.


---

## ADVERTENCIAS

⚠️ **7 advertencia(s)**:

1. A2: Low method usage ratio: 0.0% (0/10)
2. A4: source_hash is placeholder or missing
3. B2: No methodological_depth.methods defined
4. B3: Required elements not in validation rules: {'mitigacion_propuesta', 'riesgos_identificados'}
5. C1: No methodological_depth for documentation check
6. C2: Template title does not reference base_slot or question_id
7. C3: source_hash is placeholder - breaks provenance chain


---

## RECOMENDACIONES

💡 **1 recomendación(es)**:

1. **[HIGH]** C3: Missing source_hash
   - **Fix**: Calculate SHA256 of questionnaire_monolith.json and update traceability.source_hash
   - **Impact**: +3 pts



---

## PRÓXIMOS PASOS


### ❌ REFORMULACIÓN REQUERIDA

Este contrato requiere trabajo sustancial:
1. Analizar los 1 blocker(s) críticos
2. Considerar regeneración desde monolito
3. Revisar alineación method-assembly
4. Validar coherencia identity-schema
5. Re-ejecutar CQVR post-reformulación

