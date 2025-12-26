# PLAN DE CORRECCIONES COMUNES CON VALIDATOR GOVERNANCE LAYER (VGL)

## 🎯 PRINCIPIO RECTOR

> **Las correcciones comunes solo pueden tocar infraestructura epistemológica, nunca semántica sustantiva.**

**Traducción operativa:**
- ✅ **Lo estructural se normaliza** (dependencies, counts, placeholders)
- 🔒 **Lo epistemológico-decisional se protege** (métodos N1, gate_logic, roles)
- ⏸️ **Lo interpretativo se congela** para análisis caso a caso

---

## 📋 TAXONOMÍA DE CORRECCIONES

### Clase 1: STRUCTURAL (Infraestructura)
**Características:**
- Sin impacto semántico
- Determinísticas
- No introducen supuestos nuevos
- **Automation:** AUTO permitido

**Reglas incluidas:**
- `incorrect_dependencies`
- `method_count_mismatch`
- `missing_cross_layer_fusion`
- `missing_placeholders`
- `r1_sources_issue`
- `incorrect_requires`

### Clase 2: EPISTEMIC (Epistemología sin supuestos nuevos)
**Características:**
- Afectan epistemología pero no introducen supuestos nuevos
- Requieren validación de contexto (tipo de contrato)
- **Automation:** SEMI_AUTO con guards

**Reglas incluidas:**
- `fusion_strategy_mismatch` (requiere contract_type explícito)
- `r2_merge_strategy_issue` (requiere contract_type explícito)
- `missing_asymmetry` (requiere asymmetry_domain_note)
- `missing_argumentative_roles` (requiere contract_type, no sobrescribir)

### Clase 3: SEMANTIC (Semántica sustantiva)
**Características:**
- Afectan significado o decisiones
- Requieren análisis experto
- **Automation:** MANUAL únicamente

**Reglas incluidas:**
- `gate_logic_issues` (solo estructura, nunca semántica)
- `empty_phase_A` (NO CORREGIR, solo flag)

---

## 🔐 GUARDS IMPLEMENTADOS

### Guard 1: Contract-Type Guard
**Función:** Bloquea correcciones que asumen tipo sin `identity.contract_type` explícito.

**Aplica a:**
- `fusion_strategy_mismatch`
- `r2_merge_strategy_issue`
- `missing_argumentative_roles`

**Acción:** BLOCK_CORRECTION si `identity.contract_type` es NULL

---

### Guard 2: N1 Protection Rule
**Función:** Previene inserción automática de métodos N1.

**Aplica a:**
- `empty_phase_A`

**Acción:** BLOCK_AND_FLAG con `requires_epistemic_completion`

**Razón:** Un método N1 agregado automáticamente equivale a introducir evidencia no evaluada (inaceptable epistemológicamente).

---

### Guard 3: Gate Logic Guard
**Función:** Asegura que correcciones de `gate_logic` sean solo estructurales.

**Acciones permitidas:**
- ✅ `ADD_MISSING_CONDITION_STRUCTURE`
- ✅ `NORMALIZE_CONFIDENCE_MULTIPLIER_RANGE`

**Acciones prohibidas:**
- ❌ `MODIFY_TRIGGER_SEMANTICS`
- ❌ `RENAME_EXISTING_TRIGGERS`
- ❌ `DELETE_CONDITIONS`

**Acción:** BLOCK_CORRECTION si viola

---

### Guard 4: Asymmetry Semantic Guard
**Función:** Previene texto genérico sin anclaje de dominio.

**Aplica a:**
- `missing_asymmetry`

**Condición:** Requiere `asymmetry_domain_note` no NULL

**Acción:** DOWNGRADE_AUTOMATION de AUTO → SEMI_AUTO

**Salvaguarda:** Preserva diferenciación por contrato y espacio para debate futuro.

---

### Guard 5: Argumentative Role Guard
**Función:** Previene sobrescritura de roles argumentativos existentes.

**Aplica a:**
- `missing_argumentative_roles`

**Restricciones:**
- ❌ `overwrite_existing_roles`: False
- ❌ `modify_narrative_weight`: False

**Acción:** BLOCK_CORRECTION si viola

**Salvaguarda:** Evita que contratos conceptualmente distintos terminen "sonando igual".

---

## 🚦 MATRIZ DE DECISIÓN

| Regla | Clase | Automation | Guard Requerido | Riesgo Aplanamiento |
|-------|-------|------------|-----------------|---------------------|
| `incorrect_dependencies` | STRUCTURAL | AUTO | Ninguno | ✅ NINGUNO |
| `method_count_mismatch` | STRUCTURAL | AUTO | Ninguno | ✅ NINGUNO |
| `missing_cross_layer_fusion` | STRUCTURAL | AUTO | Ninguno | ✅ NINGUNO |
| `missing_placeholders` | STRUCTURAL | AUTO | Ninguno | ✅ NINGUNO |
| `r1_sources_issue` | STRUCTURAL | AUTO | Ninguno | ✅ NINGUNO |
| `incorrect_requires` | STRUCTURAL | AUTO | Ninguno | ✅ NINGUNO |
| `fusion_strategy_mismatch` | EPISTEMIC | SEMI_AUTO | Contract-Type | ⚠️ BAJO |
| `r2_merge_strategy_issue` | EPISTEMIC | SEMI_AUTO | Contract-Type | ⚠️ BAJO |
| `missing_asymmetry` | EPISTEMIC | SEMI_AUTO | Asymmetry | ⚠️ MEDIO |
| `missing_argumentative_roles` | EPISTEMIC | SEMI_AUTO | Argumentative Role | ⚠️ MEDIO |
| `gate_logic_issues` | SEMANTIC | MANUAL | Gate Logic | 🔴 ALTO |
| `empty_phase_A` | SEMANTIC | MANUAL | N1 Protection | 🔴 ALTO |

---

## 📝 REGISTRO DE IMPACTO EPISTEMOLÓGICO

Toda corrección aplicada debe dejar huella:

```json
{
  "rule_id": "missing_cross_layer_fusion",
  "correction_class": "STRUCTURAL",
  "automation_level": "AUTO",
  "fields_modified": ["cross_layer_fusion.N3_to_N1"],
  "epistemic_impact": "NONE",
  "timestamp": "2025-01-12T14:32:00Z"
}
```

Si `epistemic_impact != "NONE"`, el contrato queda marcado:
```json
{
  "requires_epistemic_review": true,
  "epistemic_review_hooks": {
    "auto_corrected_fields": ["dependencies", "method_count"],
    "protected_fields": ["contract_type", "phase_A.methods", "gate_logic"],
    "review_required_for": ["missing_asymmetry"]
  }
}
```

---

## 🎯 PLAN DE EJECUCIÓN

### Fase 1: Correcciones Estructurales (AUTO)
**Objetivo:** Reducir errores críticos en ~40-50%

**Reglas aplicables:**
1. `incorrect_dependencies`
2. `method_count_mismatch`
3. `missing_cross_layer_fusion`
4. `missing_placeholders`
5. `r1_sources_issue`
6. `incorrect_requires`

**Criterio de éxito:** 100% de contratos con estas correcciones aplicadas sin errores.

---

### Fase 2: Correcciones Epistémicas (SEMI_AUTO)
**Objetivo:** Reducir errores críticos adicionales en ~20-30%

**Reglas aplicables:**
1. `fusion_strategy_mismatch` (con Contract-Type Guard)
2. `r2_merge_strategy_issue` (con Contract-Type Guard)
3. `missing_asymmetry` (con Asymmetry Guard - requiere domain_note)
4. `missing_argumentative_roles` (con Argumentative Role Guard)

**Criterio de éxito:** ≥95% de contratos con tipo explícito corregidos.

---

### Fase 3: Correcciones Semánticas (MANUAL)
**Objetivo:** Identificar y flaggear para revisión experta

**Reglas aplicables:**
1. `gate_logic_issues` → Validación de estructura únicamente
2. `empty_phase_A` → Flag `requires_epistemic_completion`

**Criterio de éxito:** 100% de contratos con flags apropiados, 0% con correcciones automáticas incorrectas.

---

## 🔍 VALIDACIÓN POST-CORRECCIÓN

### Checklist de Validación:
1. ✅ ¿Se aplicaron solo correcciones STRUCTURAL en AUTO?
2. ✅ ¿Todas las correcciones EPISTEMIC tienen guards validados?
3. ✅ ¿Ninguna corrección SEMANTIC fue automática?
4. ✅ ¿Todos los contratos tienen `epistemic_review_hooks`?
5. ✅ ¿El validador pasa después de correcciones?

### Criterio de Aprobación:
- ✅ 0 violaciones de guards
- ✅ 0 correcciones SEMANTIC automáticas
- ✅ 100% de contratos con hooks de revisión
- ✅ ≥80% reducción de errores críticos

---

## 🛡️ META-REGLA SUPREMA

```python
META_RULE = {
    "id": "NO_EPISTEMIC_FLATTENING",
    "statement": "The validator SHALL NOT reduce epistemological diversity across contracts through automatic corrections.",
    "enforced_by": [
        "N1_protection_guard",
        "gate_logic_guard",
        "asymmetry_guard",
        "argumentative_role_guard"
    ],
    "violation_action": "HARD_FAIL"
}
```

**Traducción:** El validador NO PUEDE reducir la diversidad epistemológica entre contratos mediante correcciones automáticas.

**Enforcement:** Cualquier corrección que viole esta regla es bloqueada automáticamente.

---

## 📊 MÉTRICAS DE ÉXITO

### Métricas Cuantitativas:
- **Reducción de errores críticos:** ≥80%
- **Contratos con correcciones AUTO:** 100% de elegibles
- **Violaciones de guards:** 0
- **Correcciones SEMANTIC automáticas:** 0

### Métricas Cualitativas:
- **Preservación de diversidad epistemológica:** ✅ Verificado por guards
- **Trazabilidad de correcciones:** ✅ 100% con logs
- **Puntos de reentrada para debate:** ✅ 100% con hooks

---

## 🎓 LECCIONES DE Q014

Las discusiones profundas como Q014 son posibles porque:
1. ✅ No se agregaron métodos N1 automáticamente
2. ✅ Se respetó el tipo de contrato (TYPE_E)
3. ✅ Se preservó la capacidad de debate sobre métodos
4. ✅ Se documentó explícitamente la justificación

**El VGL asegura que esto se preserve en correcciones masivas.**

---

## ✅ CONCLUSIÓN

Con el VGL implementado:
- ✅ Puedes corregir en masa sin perder riqueza epistemológica
- ✅ Tienes salvaguardas formales contra aplanamiento
- ✅ Mantienes trazabilidad completa de impacto
- ✅ Preservas puntos de reentrada para debate experto

**En una frase:** Estás consolidando la infraestructura para que las discusiones profundas sean posibles, no eliminándolas.

