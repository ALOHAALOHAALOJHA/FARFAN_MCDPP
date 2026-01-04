# POLÍTICA DE NOTACIÓN CANÓNICA F.A.R.F.A.N — DOCUMENTO DE APLICACIÓN FORZADA

**Versión**: 1.0.0  
**Fecha de Vigencia**: 2026-01-04  
**Estado**: OBLIGATORIO — APLICACIÓN INMEDIATA  
**Carácter**: VINCULANTE PARA TODO EL REPOSITORIO

---

## 1. DECLARACIÓN DE POLÍTICA

### 1.1 Alcance y Obligatoriedad

Este documento establece la **POLÍTICA OBLIGATORIA** para el uso de códigos, notación y nomenclatura en el sistema F.A.R.F.A.N. Su cumplimiento es **MANDATORIO** para:

- Todos los archivos JSON
- Todos los archivos Python
- Todos los documentos Markdown
- Toda documentación técnica
- Todos los contratos de ejecución

### 1.2 Fuente Única de Verdad

| Elemento | Archivo Canónico |
|----------|-----------------|
| Áreas de Política | `DECALOGO_POLICY_AREAS_CANONICAL.json` |
| Notación Completa | `CANONICAL_NOTATION_SPECIFICATION.md` |
| Mapeo P→PA | `DECALOGO_POLICY_AREAS_CANONICAL.json` |

---

## 2. CÓDIGOS CANÓNICOS OBLIGATORIOS

### 2.1 Áreas de Política — DECÁLOGO OFICIAL

| Código Canónico | Abreviatura Canónica | Nombre Oficial (ÚNICO PERMITIDO) |
|-----------------|---------------------|----------------------------------|
| `PA01` | `MUJ` | Derechos de las mujeres e igualdad de género |
| `PA02` | `VIO` | Prevención de la violencia y protección de la población frente al conflicto armado y la violencia generada por grupos delincuenciales organizados, asociada a economías ilegales |
| `PA03` | `AMB` | Ambiente sano, cambio climático, prevención y atención a desastres |
| `PA04` | `DESC` | Derechos económicos, sociales y culturales |
| `PA05` | `VIC` | Derechos de las víctimas y construcción de paz |
| `PA06` | `NIÑ` | Derecho al buen futuro de la niñez, adolescencia, juventud y entornos protectores |
| `PA07` | `TIE` | Tierras y territorios |
| `PA08` | `LID` | Líderes y lideresas, defensores y defensoras de derechos humanos, comunitarios, sociales, ambientales, de la tierra, el territorio y de la naturaleza |
| `PA09` | `PPL` | Crisis de derechos de personas privadas de la libertad |
| `PA10` | `MIG` | Migración transfronteriza |

### 2.2 CÓDIGOS PROHIBIDOS

Los siguientes códigos están **PROHIBIDOS** y deben ser reemplazados:

| PROHIBIDO | Reemplazo Canónico | Razón |
|-----------|-------------------|-------|
| `P1`, `P2`, ... `P10` | `PA01`, `PA02`, ... `PA10` | Notación legacy deprecada |
| `INFANCIA` | `NIÑ` | Código no canónico |
| `MUJER` | `MUJ` | Código no canónico |
| `SEGURIDAD` | `VIO` | Código no canónico |
| `VICTIMAS` | `VIC` | Código no canónico (sin tilde) |
| `ETNIAS` | ❌ ELIMINAR | PA06 no es etnias |
| `TRANSPARENCIA` | `TIE` | PA07 es Tierras |
| `OT-RIESGO` | `DESC` | PA04 es DESC |
| `AMBIENTE` | `AMB` | Mantener pero para PA03 |
| `D01_MUJER_GENERO` | `PA01` | Formato no canónico |

### 2.3 NOMBRES PROHIBIDOS

| PROHIBIDO | Correcto | Archivo(s) Violador(es) |
|-----------|----------|------------------------|
| "Equidad de género" | "Derechos de las mujeres e igualdad de género" | recommendation_rules.json |
| "PA01-Género" | "PA01 - Derechos de las mujeres e igualdad de género" | EPISTEMIC_METHOD_ASSIGNMENTS |
| "Grupos Étnicos" | N/A (PA06 es Niñez, no Etnias) | manifest.json |
| "Primera Infancia, Niñez..." | N/A (PA01 es Mujeres) | manifest.json |
| "Atención a víctimas" | "Derechos de las víctimas y construcción de paz" | recommendation_rules.json |
| "Niñez y juventud" | "Derecho al buen futuro de la niñez..." | recommendation_rules.json |

---

## 3. REPORTE DE VIOLACIONES DETECTADAS

### 3.1 Violaciones CRÍTICAS (Prioridad P0)

| # | Archivo | Tipo de Violación | Código Incorrecto | Código Correcto | Línea(s) |
|---|---------|-------------------|-------------------|-----------------|----------|
| **1** | `meso_questions.json` | Uso de código legacy | `P1`, `P5`, `P6` en policy_areas | `PA01`, `PA05`, `PA06` | 31, 40, 78 |
| **2** | `meso_questions.json` | Uso de código legacy | `P2`, `P3`, `P7`, `P4`, `P8`, `P9`, `P10` | `PA02`, `PA03`, `PA07`, `PA04`, `PA08`, `PA09`, `PA10` | Múltiples |
| **3** | `clusters/CL02_grupos_poblacionales/metadata.json` | Uso de código legacy | `P1` | `PA01` | 11 |
| **4** | `clusters/CL04_derechos_sociales_crisis/metadata.json` | Uso de código legacy | `P10` | `PA10` | 12 |
| **5** | `niveles_abstraccion.json` | Uso de código legacy | `P1`, `P10`, etc. | `PA01`, `PA10`, etc. | 34, 75, 177, 420 |

### 3.2 Violaciones SEMÁNTICAS (Prioridad P1)

| # | Archivo | Tipo de Violación | Valor Incorrecto | Valor Correcto |
|---|---------|-------------------|------------------|----------------|
| **6** | `manifest.json` | Código corto incorrecto PA01 | `"code": "INFANCIA"` | `"code": "MUJ"` |
| **7** | `manifest.json` | Código corto incorrecto PA02 | `"code": "SEGURIDAD"` | `"code": "VIO"` |
| **8** | `manifest.json` | Código corto incorrecto PA03 | `"code": "VICTIMAS"` | `"code": "AMB"` (PA03 es Ambiente) |
| **9** | `manifest.json` | Código corto incorrecto PA04 | `"code": "OT-RIESGO"` | `"code": "DESC"` |
| **10** | `manifest.json` | Código corto incorrecto PA05 | `"code": "MUJER"` | `"code": "VIC"` |
| **11** | `manifest.json` | Código corto incorrecto PA06 | `"code": "ETNIAS"` | `"code": "NIÑ"` |
| **12** | `manifest.json` | Código corto incorrecto PA07 | `"code": "TRANSPARENCIA"` | `"code": "TIE"` |

### 3.3 Violaciones de NOMENCLATURA (Prioridad P2)

| # | Archivo | Tipo de Violación | Valor Incorrecto | Valor Correcto |
|---|---------|-------------------|------------------|----------------|
| **13** | `EPISTEMIC_METHOD_ASSIGNMENTS_Q001_Q030.json` | Nombre abreviado PA01 | `"PA01-Género"` | `"PA01 - Derechos de las mujeres..."` |
| **14** | `recommendation_rules.json` | Nombre incorrecto PA01 | `"Equidad de género"` | `"Derechos de las mujeres e igualdad de género"` |
| **15** | `recommendation_rules.json` | Nombre incorrecto PA05 | `"Atención a víctimas"` | `"Derechos de las víctimas y construcción de paz"` |
| **16** | `recommendation_rules.json` | Nombre incorrecto PA06 | `"Niñez y juventud"` | `"Derecho al buen futuro de la niñez..."` |
| **17** | `manifest.json` | Nombre incorrecto PA01 | `"Primera Infancia, Niñez..."` | `"Derechos de las mujeres e igualdad de género"` ← YA CORREGIDO |

### 3.4 Violaciones de FORMATO (Prioridad P3)

| # | Archivo | Tipo de Violación | Formato Incorrecto | Formato Correcto |
|---|---------|-------------------|-------------------|------------------|
| **18** | `EXECUTOR_CONTRACTS_300_FINAL.json` | Formato no canónico | `"D01_MUJER_GENERO"` | `"PA01"` o `"PA01_Q001"` |
| **19** | `canonical_notation.json` | Legacy ID presente | `"legacy_id": "P1"` | Eliminar o marcar deprecado |
| **20** | `questionnaire_monolith.json` | Legacy ID en policy_areas | `"legacy_id": "P1"` | Eliminar o marcar deprecado |

---

## 4. ACCIONES DE REMEDIACIÓN OBLIGATORIAS

### 4.1 Acción Inmediata Requerida

```bash
# ARCHIVOS QUE REQUIEREN CORRECCIÓN INMEDIATA:

1. canonic_questionnaire_central/meso_questions.json
   → Reemplazar P1→PA01, P2→PA02, ..., P10→PA10

2. canonic_questionnaire_central/niveles_abstraccion.json
   → Reemplazar todos los códigos Px por PAxx

3. canonic_questionnaire_central/clusters/*/metadata.json
   → Reemplazar Px por PAxx en todas las referencias

4. artifacts/manifests/manifest.json
   → Corregir todos los códigos cortos

5. src/farfan_pipeline/phases/Phase_eight/json_phase_eight/recommendation_rules*.json
   → Actualizar nombres de PA a los oficiales

6. artifacts/data/epistemic_inputs_v4/EPISTEMIC_METHOD_ASSIGNMENTS_Q001_Q030.json
   → Actualizar "PA01-Género" → formato oficial
```

### 4.2 Matriz de Priorización

| Prioridad | Descripción | Tiempo Máximo | Archivos |
|-----------|-------------|---------------|----------|
| **P0** | Códigos legacy (P1-P10) | 24 horas | meso_questions.json, niveles_abstraccion.json, clusters/ |
| **P1** | Códigos cortos incorrectos | 48 horas | manifest.json |
| **P2** | Nombres no oficiales | 72 horas | recommendation_rules*.json, EPISTEMIC_METHOD |
| **P3** | Formato no canónico | 1 semana | EXECUTOR_CONTRACTS |

---

## 5. MECANISMOS DE ENFORCEMENT

### 5.1 Validación Automática

```python
# REGLA: Ejecutar antes de cualquier commit

PROHIBITED_CODES = [
    "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10",
    "INFANCIA", "SEGURIDAD", "MUJER", "ETNIAS", "TRANSPARENCIA", "OT-RIESGO"
]

PROHIBITED_NAMES = [
    "Equidad de género",
    "Primera Infancia, Niñez",
    "Grupos Étnicos",
    "Ordenamiento Territorial"
]

def validate_canonical_notation(file_content: str) -> list[str]:
    violations = []
    for code in PROHIBITED_CODES:
        if code in file_content:
            violations.append(f"VIOLATION: Prohibited code '{code}' found")
    return violations
```

### 5.2 Workflow de Enforcement

```markdown
Pre-commit Hook:
1. Escanear todos los archivos modificados
2. Buscar códigos/nombres prohibidos
3. BLOQUEAR commit si hay violaciones
4. Reportar violaciones con línea y archivo
```

---

## 6. ANEXO: MAPEO COMPLETO DEPRECADO → CANÓNICO

| Deprecado | Canónico | Contexto |
|-----------|----------|----------|
| P1 | PA01 | Todas las referencias |
| P2 | PA02 | Todas las referencias |
| P3 | PA03 | Todas las referencias |
| P4 | PA04 | Todas las referencias |
| P5 | PA05 | Todas las referencias |
| P6 | PA06 | Todas las referencias |
| P7 | PA07 | Todas las referencias |
| P8 | PA08 | Todas las referencias |
| P9 | PA09 | Todas las referencias |
| P10 | PA10 | Todas las referencias |
| INFANCIA | MUJ | Código corto PA01 |
| SEGURIDAD | VIO | Código corto PA02 |
| VICTIMAS | VIC | Código corto PA05 |
| MUJER | MUJ | Código corto PA01 |
| ETNIAS | NIÑ | Código corto PA06 |
| TRANSPARENCIA | TIE | Código corto PA07 |
| OT-RIESGO | DESC | Código corto PA04 |
| AMBIENTE | AMB | Código corto PA03 (OK pero verificar contexto) |
| DESC | DESC | Código corto PA04 (OK) |
| MIGRANTES | MIG | Código corto PA10 |

---

**FIN DEL DOCUMENTO DE POLÍTICA**

*Cualquier violación de esta política detectada después de la fecha de vigencia será considerada un defecto de alta prioridad.*
