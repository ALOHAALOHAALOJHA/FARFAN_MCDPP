# ANÁLISIS DE CORRECCIONES COMUNES - CONTRATOS F.A.R.F.A.N v4.0

## 📊 RESUMEN EJECUTIVO

**Contratos analizados:** 10 de 16 pendientes  
**Errores comunes identificados:** 13 patrones  
**Frecuencia crítica (≥90%):** 7 patrones  
**Frecuencia alta (50-89%):** 2 patrones  
**Frecuencia media (10-49%):** 4 patrones

---

## 🔴 ERRORES CRÍTICOS DE ALTA FRECUENCIA (≥90%)

### 1. **fusion_strategy_mismatch** (100% - 10/10)
**Severidad:** CRÍTICO  
**Descripción:** Falta `fusion_specification.contract_type` o estrategias no coinciden con tipo de contrato.

**Corrección común aplicable:** ✅ SÍ (con filtro de tipo)
- **Filtro de pertinencia:** Verificar `identity.contract_type` antes de aplicar
- **Acción:** Agregar `fusion_specification.contract_type` y ajustar `level_strategies` según tipo:
  - TYPE_A: `N1: semantic_corroboration`, `N2: dempster_shafer`
  - TYPE_B: `N1: concat`, `N2: bayesian_update`
  - TYPE_C: `N1: graph_construction`, `N2: topological_overlay`
  - TYPE_D: `N1: concat`, `N2: weighted_mean`
  - TYPE_E: `N1: concat`, `N2: weighted_mean`

**Riesgo:** BAJO - Corrección determinística basada en tipo

---

### 2. **incorrect_dependencies** (100% - 10/10)
**Severidad:** CRÍTICO  
**Descripción:** `dependencies` incorrectas en fases (no usan nombres de fases).

**Corrección común aplicable:** ✅ SÍ (universal)
- **Filtro de pertinencia:** Verificar estructura de `execution_phases`
- **Acción:** Corregir `dependencies`:
  - `phase_A_construction.dependencies`: `[]` (siempre vacío)
  - `phase_B_computation.dependencies`: `["phase_A_construction"]`
  - `phase_C_litigation.dependencies`: `["phase_A_construction", "phase_B_computation"]`

**Riesgo:** BAJO - Corrección universal y determinística

---

### 3. **missing_asymmetry** (100% - 10/10)
**Severidad:** CRÍTICO  
**Descripción:** Falta `asymmetry_principle` en `phase_C_litigation`.

**Corrección común aplicable:** ✅ SÍ (universal)
- **Filtro de pertinencia:** Verificar que existe `phase_C_litigation`
- **Acción:** Agregar `asymmetry_principle` con texto estándar:
  ```json
  "asymmetry_principle": "ASIMETRÍA EXPLÍCITA: N3 can invalidate resultados de N1/N2 mediante veto gates con confidence_multiplier = 0.0, bloqueando completamente hallazgos que N1/N2 aceptarían. Mientras N1 extrae [hechos] y N2 [evalúa/infiere], N3 aplica criterios de falsación popperiana. CANNOT invalidate N3: N1 y N2 no pueden vetar decisiones de N3, solo pueden proporcionar datos que N3 evalúa"
  ```
  - Ajustar texto según tipo de contrato (hechos específicos del dominio)

**Riesgo:** MEDIO - Requiere ajuste semántico según tipo de contrato

---

### 4. **method_count_mismatch** (100% - 10/10)
**Severidad:** CRÍTICO  
**Descripción:** `method_count` no coincide con suma de métodos en fases.

**Corrección común aplicable:** ✅ SÍ (universal)
- **Filtro de pertinencia:** Calcular automáticamente
- **Acción:** Recalcular `method_count`:
  ```python
  method_count = len(phase_A.methods) + len(phase_B.methods) + len(phase_C.methods)
  ```

**Riesgo:** BAJO - Cálculo determinístico

---

### 5. **missing_traceability** (100% - 10/10)
**Severidad:** ALTO  
**Descripción:** Falta `refactoring_history` o `prohibitions` en `traceability`.

**Corrección común aplicable:** ✅ SÍ (universal)
- **Filtro de pertinencia:** Verificar estructura de `traceability`
- **Acción:** Agregar campos faltantes:
  ```json
  "refactoring_history": [
    {
      "from_version": "3.0.0",
      "to_version": "4.0.0-epistemological",
      "date": "[fecha actual]",
      "changes": ["Epistemological stratification", "..."],
      "epistemological_framework": {
        "N1": "Empirismo positivista",
        "N2": "Bayesianismo subjetivista",
        "N3": "Falsacionismo popperiano",
        "N4": "Reflexividad crítica"
      }
    }
  ],
  "prohibitions": {
    "v3_recovery": "FORBIDDEN",
    "v3_migration": "FORBIDDEN",
    "v3_reference": "FORBIDDEN",
    "non_epistemological_mode": "FORBIDDEN"
  }
  ```

**Riesgo:** BAJO - Estructura estándar

---

### 6. **missing_argumentative_roles** (100% - 10/10)
**Severidad:** ALTO  
**Descripción:** Falta `N1_roles` o `N3_roles` en `argumentative_roles`.

**Corrección común aplicable:** ✅ SÍ (con filtro de tipo)
- **Filtro de pertinencia:** Verificar tipo de contrato para roles específicos
- **Acción:** Agregar roles faltantes:
  ```json
  "N1_roles": [
    {
      "role": "EMPIRICAL_BASIS",
      "description": "Base empírica de [tipo de hechos]",
      "narrative_weight": "high"
    }
  ],
  "N3_roles": [
    {
      "role": "ROBUSTNESS_QUALIFIER",
      "description": "[Descripción según tipo]",
      "narrative_weight": "critical",
      "triggers_veto": true
    },
    {
      "role": "REFUTATIONAL_SIGNAL",
      "description": "[Descripción según tipo]",
      "narrative_weight": "critical",
      "triggers_veto": true
    }
  ]
  ```
  - Para TYPE_D: agregar `FINANCIAL_CONSTRAINT`
  - Para TYPE_E: agregar `LOGICAL_INCONSISTENCY`

**Riesgo:** MEDIO - Requiere ajuste según tipo de contrato

---

### 7. **empty_phase_A** (90% - 9/10)
**Severidad:** CRÍTICO  
**Descripción:** `phase_A_construction.methods` está vacío.

**Corrección común aplicable:** ❌ NO (requiere análisis específico)
- **Razón:** Cada contrato necesita métodos N1 específicos según su dominio y pregunta
- **Acción manual requerida:** Identificar método N1 apropiado según:
  - Tipo de contrato (TYPE_A/B/C/D/E)
  - Pregunta específica (Q014, Q015, etc.)
  - Disponibilidad de métodos en dispensario

**Riesgo:** ALTO - Corrección específica por contrato

---

### 8. **missing_cross_layer_fusion** (90% - 9/10)
**Severidad:** CRÍTICO  
**Descripción:** Falta `N3_to_N1` o relaciones incorrectas en `cross_layer_fusion`.

**Corrección común aplicable:** ✅ SÍ (universal)
- **Filtro de pertinencia:** Verificar estructura completa
- **Acción:** Agregar/Corregir relaciones:
  ```json
  "N3_to_N1": {
    "relationship": "N3 can BLOCK or INVALIDATE N1 facts",
    "effect": "Failed validation removes invalid facts from graph",
    "data_flow": "veto_propagation",
    "asymmetry": "N1 CANNOT invalidate N3"
  }
  ```
  - Verificar que todas las relaciones requeridas existen

**Riesgo:** BAJO - Estructura estándar

---

## 🟡 ERRORES DE FRECUENCIA MEDIA (50-89%)

### 9. **missing_placeholders** (60% - 6/10)
**Severidad:** ALTO  
**Descripción:** Falta `placeholders` en `S1_verdict.template`.

**Corrección común aplicable:** ✅ SÍ (universal)
- **Filtro de pertinencia:** Verificar que existe `S1_verdict.template`
- **Acción:** Agregar `placeholders`:
  ```json
  "placeholders": [
    "verdict_statement",
    "final_confidence_pct",
    "confidence_label",
    "method_count",
    "audit_count",
    "blocked_count"
  ]
  ```

**Riesgo:** BAJO - Lista estándar

---

### 10. **r1_sources_issue** (50% - 5/10)
**Severidad:** CRÍTICO  
**Descripción:** `R1.sources` no coincide con `provides` de `phase_A`.

**Corrección común aplicable:** ✅ SÍ (universal)
- **Filtro de pertinencia:** Verificar que `phase_A.methods` no está vacío
- **Acción:** Recolectar todos los `provides` de `phase_A.methods` y agregarlos a `R1.sources`

**Riesgo:** BAJO - Cálculo determinístico

---

## 🟠 ERRORES DE FRECUENCIA BAJA (10-49%)

### 11. **r2_merge_strategy_issue** (30% - 3/10)
**Severidad:** CRÍTICO  
**Descripción:** `R2.merge_strategy` no coincide con tipo de contrato.

**Corrección común aplicable:** ✅ SÍ (con filtro de tipo)
- **Filtro de pertinencia:** Verificar `contract_type`
- **Acción:** Corregir según tipo:
  - TYPE_A: `semantic_triangulation`
  - TYPE_B: `bayesian_update`
  - TYPE_C: `topological_overlay`
  - TYPE_D/E: `weighted_mean`

**Riesgo:** BAJO - Corrección determinística

---

### 12. **incorrect_requires** (10% - 1/10)
**Severidad:** CRÍTICO  
**Descripción:** Métodos N2 no tienen `requires: ["raw_facts"]`.

**Corrección común aplicable:** ✅ SÍ (universal)
- **Filtro de pertinencia:** Verificar que método es N2-INF
- **Acción:** Agregar `requires: ["raw_facts"]` a todos los métodos N2

**Riesgo:** BAJO - Corrección universal

---

### 13. **gate_logic_issues** (10% - 1/10)
**Severidad:** CRÍTICO  
**Descripción:** `gate_logic` falta condiciones o `confidence_multiplier < 0.5`.

**Corrección común aplicable:** ⚠️ PARCIAL (requiere validación)
- **Filtro de pertinencia:** Verificar que existe `gate_logic` y tiene al menos 2 condiciones
- **Acción:** Asegurar que:
  - Al menos 2 condiciones en `gate_logic`
  - Al menos 1 condición con `confidence_multiplier: 0.0`
  - Todas las condiciones tienen `trigger`, `scope`, `confidence_multiplier`

**Riesgo:** MEDIO - Requiere validación de lógica de negocio

---

## 📋 PLAN DE CORRECCIÓN COMÚN

### Fase 1: Correcciones Universales (Riesgo BAJO)
1. ✅ `incorrect_dependencies` - Corrección universal
2. ✅ `method_count_mismatch` - Cálculo automático
3. ✅ `missing_cross_layer_fusion` - Estructura estándar
4. ✅ `missing_placeholders` - Lista estándar
5. ✅ `r1_sources_issue` - Cálculo automático
6. ✅ `incorrect_requires` - Corrección universal

### Fase 2: Correcciones por Tipo (Riesgo MEDIO)
7. ✅ `fusion_strategy_mismatch` - Requiere identificar tipo
8. ✅ `r2_merge_strategy_issue` - Requiere identificar tipo
9. ✅ `missing_argumentative_roles` - Requiere identificar tipo y ajustar roles

### Fase 3: Correcciones Semánticas (Riesgo MEDIO)
10. ⚠️ `missing_asymmetry` - Requiere ajuste semántico según tipo
11. ⚠️ `gate_logic_issues` - Requiere validación de lógica

### Fase 4: Correcciones Específicas (Riesgo ALTO)
12. ❌ `empty_phase_A` - Requiere análisis específico por contrato
13. ⚠️ `missing_traceability` - Estructura estándar pero requiere fecha/contexto

---

## ⚠️ FILTROS DE PERTINENCIA

### Filtros Críticos (NO aplicar corrección sin verificar):
1. **Tipo de contrato:** Verificar `identity.contract_type` antes de aplicar correcciones específicas por tipo
2. **Estructura existente:** Verificar que la estructura base existe antes de agregar campos
3. **Métodos N1:** NO agregar métodos N1 genéricos sin análisis específico
4. **Lógica de negocio:** NO modificar `gate_logic` sin entender el propósito del contrato

### Filtros de Validación:
1. **Pre-corrección:** Ejecutar validador antes de aplicar correcciones comunes
2. **Post-corrección:** Ejecutar validador después de cada lote de correcciones
3. **Rollback:** Mantener backup antes de aplicar correcciones masivas

---

## 🎯 RECOMENDACIÓN FINAL

**Aplicar correcciones comunes en 3 fases:**

1. **Fase 1 (Automática):** Aplicar correcciones universales de riesgo BAJO a todos los contratos pendientes
2. **Fase 2 (Semi-automática):** Aplicar correcciones por tipo con validación de tipo de contrato
3. **Fase 3 (Manual):** Revisar y corregir `empty_phase_A` y ajustes semánticos específicos

**Criterio de éxito:** Reducir errores críticos en ≥80% de los contratos antes de correcciones específicas.


