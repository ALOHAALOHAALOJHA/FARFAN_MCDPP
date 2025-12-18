# 📊 REPORTE DE EVALUACIÓN CQVR v2.0
## Contrato: Q147.v3.json
**Fecha**: 2025-12-17  
**Evaluador**: CQVR Batch 6 Evaluator  
**Rúbrica**: CQVR v2.0 (100 puntos)

---

## RESUMEN EJECUTIVO

| Métrica | Score | Umbral | Estado |
|---------|-------|--------|--------|
| **TIER 1: Componentes Críticos** | **40/55** | ≥35 | ✅ APROBADO |
| **TIER 2: Componentes Funcionales** | **5/30** | ≥20 | ❌ REPROBADO |
| **TIER 3: Componentes de Calidad** | **10/15** | ≥8 | ✅ APROBADO |
| **TOTAL** | **55/100** | ≥80 | ⚠️ MEJORAR |

**VEREDICTO**: ❌ **REFORMULAR**

Below minimum thresholds

---

## DESGLOSE DETALLADO

### TIER 1: COMPONENTES CRÍTICOS - 40/55 pts

#### A1. Coherencia Identity-Schema [20/20 pts]
Verificación de coherencia entre campos de identity y output_contract.schema.

#### A2. Alineación Method-Assembly [15/20 pts]
Verificación de que assembly_rules.sources existen en method_binding.methods[].provides.

#### A3. Integridad de Señales [0/10 pts]
Verificación de signal_requirements con threshold > 0.

#### A4. Output Schema [5/5 pts]
Verificación de que todos los campos required están definidos en properties.

### TIER 2: COMPONENTES FUNCIONALES - 5/30 pts

#### B1. Coherencia de Patrones [5/10 pts]
Verificación de coverage, confidence weights e IDs únicos.

#### B2. Especificidad Metodológica [0/10 pts]
Verificación de que los steps no son genéricos.

#### B3. Reglas de Validación [0/10 pts]
Verificación de rules, must_contain, should_contain y failure_contract.

### TIER 3: COMPONENTES DE CALIDAD - 10/15 pts

#### C1. Documentación Epistemológica [3/5 pts]
Verificación de paradigma, justificación y referencias.

#### C2. Template Human-Readable [2/5 pts]
Verificación de referencias correctas y placeholders válidos.

#### C3. Metadatos y Trazabilidad [5/5 pts]
Verificación de contract_hash, timestamps y versionado.

---

## MATRIZ DE DECISIÓN

| Tier 1 Score | Total Score | DECISIÓN |
|-------------|------------|----------|
| 40/55 (72.7%) | 55/100 (55%) | **REFORMULAR** |

---

## CONCLUSIÓN

El contrato Q147.v3.json obtiene **55/100 puntos** (55%).

**Estado**: ❌ REFORMULAR
**Razón**: Below minimum thresholds

---

**Generado**: 2025-12-17T08:45:02.528173Z  
**Batch**: 6 (Q126-Q150)  
**Rúbrica**: CQVR v2.0
