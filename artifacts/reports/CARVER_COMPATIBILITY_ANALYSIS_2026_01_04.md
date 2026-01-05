# ANÁLISIS DE COMPATIBILIDAD CARVER v3.0 vs CONTRACTS v4

**Archivo:** `CARVER_COMPATIBILITY_ANALYSIS_2026_01_04.md`  
**Fecha:** 2026-01-04  
**Ubicación CARVER:** `src/farfan_pipeline/phases/Phase_two/phase2_90_00_carver.py`  
**Versión CARVER:** 3.0.0-FULL-EXTRACTION (2347 líneas)

---

## RESUMEN EJECUTIVO

| Métrica | Valor |
|---------|-------|
| **Problemas Contractuales** | 8 |
| **Problemas de Código** | 5 |
| **Total Problemas** | 13 |
| **Severidad CRÍTICO** | 1 |
| **Severidad ALTO** | 5 |
| **Severidad MEDIO** | 7 |
| **Estado CARVER** | ⚠️ PARCIALMENTE FUNCIONAL |

---

## PARTE A: PROBLEMAS DE COMPATIBILIDAD CONTRACTUAL

### C1 [CRÍTICO] - `human_answer_structure` NO EXISTE

**Descripción:** CARVER v3.0 espera el campo `human_answer_structure` en el contrato, pero los contratos v4 NO tienen este campo.

**Código CARVER afectado:**
```python
# Línea 646
human_answer = contract.get("human_answer_structure", {})

# Múltiples extractores que devuelven {}:
extract_methodological_depth() → None/empty
extract_assembly_flow() → {}
extract_evidence_schema() → {}
extract_concrete_example() → {}
extract_template_variables() → {}
```

**Estructura esperada por CARVER:**
```json
{
  "human_answer_structure": {
    "methodological_depth": { "methods": [...] },
    "assembly_flow": { "step_1": "...", ... },
    "evidence_structure_schema": { ... },
    "concrete_example": { ... },
    "template_variable_bindings": { "variables": {...} }
  }
}
```

**Estructura real en CONTRACT v4:**
```json
{
  "contract_id": "D01_MUJER_GENERO_Q001_CONTRACT",
  "method_binding": { "orchestration_mode": "...", "execution_phases": {...} },
  "evidence_assembly": { "engine": "...", "assembly_rules": {...} },
  "fusion_strategies": { "n1": {...}, "n2": {...}, "n3": {...} }
}
```

**Impacto:** CARVER usa defaults vacíos para TODA la estructura de respuesta. No puede generar narrativa estructurada.

**Brecha relacionada:** B6 (sections no disponibles)

---

### C2 [ALTO] - `sections[]` para estructura de respuesta NO EXISTE

**Descripción:** CARVER espera un array `sections[]` dentro de `human_answer_structure` para estructurar la respuesta en secciones con headers.

**Código CARVER afectado:**
```python
# Línea ~500 (EnhancedContractInterpreter)
human_answer = contract.get("human_answer_structure", {})
sections = human_answer.get("sections", [])
```

**Estructura esperada:**
```json
{
  "sections": [
    {
      "section_id": "methodology",
      "header": "Metodología Aplicada",
      "required_elements": ["method_names", "epistemology"],
      "prose_template": "Se aplicaron los métodos {methods}..."
    }
  ]
}
```

**Impacto:** CARVER no puede usar templates de sección del contrato. Genera respuesta plana sin estructura.

**Brecha relacionada:** B6

---

### C3 [ALTO] - `confidence_interpretation` NO EXISTE

**Descripción:** CARVER espera un diccionario `confidence_interpretation` para traducir niveles numéricos de confianza a labels calibrados por pregunta.

**Código CARVER afectado:**
```python
# BayesianConfidenceEngine espera:
confidence_interpretation = contract.get("confidence_interpretation", {})
# Labels por defecto hardcodeados:
# 0.9+: "Alta confianza"
# 0.7-0.9: "Confianza moderada"
# <0.7: "Baja confianza"
```

**Estructura esperada:**
```json
{
  "confidence_interpretation": {
    "high": { "threshold": 0.85, "label": "Cumplimiento robusto" },
    "medium": { "threshold": 0.60, "label": "Cumplimiento parcial" },
    "low": { "threshold": 0.40, "label": "Cumplimiento insuficiente" }
  }
}
```

**Impacto:** Labels de confianza genéricos, no calibrados al dominio de política pública.

**Brecha relacionada:** B7

---

### C4 [ALTO] - `blocking_rules[]` NO EXISTE

**Descripción:** CARVER espera reglas de bloqueo que indican condiciones bajo las cuales la respuesta debe señalar incompletitud crítica.

**Código CARVER afectado:**
```python
blocking_rules = contract.get("blocking_rules", [])
# Usado en DoctoralRenderer para insertar advertencias
```

**Estructura esperada:**
```json
{
  "blocking_rules": [
    {
      "rule_id": "BR01",
      "condition": "no_quantitative_data",
      "message": "ALERTA: Sin datos cuantitativos no es posible evaluar cumplimiento."
    }
  ]
}
```

**Impacto:** CARVER no puede insertar advertencias contractuales cuando faltan datos críticos.

**Brecha relacionada:** B5

---

### C5 [MEDIO] - `identity` wrapper NO EXISTE

**Descripción:** CARVER busca un wrapper `identity` para extraer dimension, slot y policy area. Los contratos v4 tienen estos campos en root.

**Código CARVER afectado:**
```python
# Línea ~478
identity = contract.get("identity", {})
dimension_id = identity.get("dimension_id")  # Fallback works
```

**Estructura esperada por CARVER:**
```json
{
  "identity": {
    "dimension_id": "D1",
    "base_slot": "Q001",
    "policy_area_id": "PA01"
  }
}
```

**Estructura real en CONTRACT v4:**
```json
{
  "dimension_code": "D1",
  "question_id": "Q001",
  "policy_area": "D01_MUJER_GENERO"
}
```

**Impacto:** CARVER tiene fallbacks que funcionan, pero no es la estructura ideal.

---

### C6 [MEDIO] - `fusion_specification` vs `fusion_strategies`

**Descripción:** CARVER espera `fusion_specification` con `level_strategies`. Los contratos v4 tienen `fusion_strategies` con estructura diferente.

**Código CARVER afectado:**
```python
fusion_spec = contract.get("fusion_specification", {})
level_strategies = fusion_spec.get("level_strategies", {})
```

**Estructura real en CONTRACT v4:**
```json
{
  "fusion_strategies": { "n1": {...}, "n2": {...}, "n3": {...} },
  "n1_strategy_refined": { "name": "...", "operation": "..." },
  "n2_strategy_refined": { "name": "...", "operation": "..." },
  "n3_fusion_refined": { "name": "...", "formula": "..." }
}
```

**Impacto:** CARVER no extrae estrategias de fusión. Puede usar los campos `nX_strategy_refined` pero no los busca.

**Brecha relacionada:** B4

---

### C7 [MEDIO] - `sector_context` NO EXISTE

**Descripción:** CARVER espera contexto sectorial con keywords y cluster_id para contextualizar la respuesta.

**Código CARVER esperado:**
```python
sector_context = contract.get("sector_context", {})
sector_keywords = sector_context.get("keywords", [])
cluster_id = sector_context.get("cluster_id")
```

**Impacto:** CARVER no puede contextualizar respuesta por sector (Mujer, Empleo, Salud, etc.).

**Brecha relacionada:** B1, I9

---

### C8 [MEDIO] - `cross_cutting_context` NO EXISTE

**Descripción:** CARVER espera temas transversales aplicables a la pregunta.

**Código CARVER esperado:**
```python
cross_cutting = contract.get("cross_cutting_context", {})
applicable_themes = cross_cutting.get("themes", [])
```

**Impacto:** CARVER no menciona temas transversales (género, ambiental, étnico-racial) en la narrativa.

**Brecha relacionada:** I9

---

## PARTE B: PROBLEMAS DE CALIDAD DE CÓDIGO

### D1 [ALTO] - CLASE `MethodEpistemology` DEFINIDA DOS VECES

**Ubicación:**
- Primera definición: Línea ~230 (dataclass simple)
- Segunda definición: Línea ~640+ (dataclass extendida)

**Código problemático:**
```python
# Primera versión (simple):
@dataclass
class MethodEpistemology:
    paradigm: str
    ontological_basis: str
    epistemological_stance: str
    theoretical_framework: List[str]
    justification: str

# Segunda versión (extendida, sobrescribe):
@dataclass
class MethodEpistemology:
    method_name: str
    class_name: str
    priority: int
    role: str
    paradigm: str
    # ... más campos
```

**Impacto:** La segunda definición sobrescribe la primera. Cualquier código que use la primera estructura fallará silenciosamente.

---

### D2 [ALTO] - MÉTODO `extract_methodological_depth` DEFINIDO DOS VECES

**Ubicación:**
- Primera definición: Línea 556 (retorna `Optional[MethodologicalDepth]`)
- Segunda definición: Línea 639 (retorna `MethodologicalDepth`)

**Código problemático:**
```python
# Primera versión (línea 556):
@classmethod
def extract_methodological_depth(cls, contract: Dict) -> Optional[MethodologicalDepth]:
    """Extrae profundidad metodológica del contrato v3..."""
    method_binding = contract.get("method_binding", {})
    methodological_depth_raw = method_binding.get("methodological_depth")
    ...

# Segunda versión (línea 639) - SOBRESCRIBE:
@classmethod  
def extract_methodological_depth(cls, contract: Dict) -> MethodologicalDepth:
    """v3.0: Extrae la profundidad metodológica COMPLETA..."""
    human_answer = contract.get("human_answer_structure", {})
    ...
```

**Impacto:** Solo la segunda versión es ejecutada. La primera es código muerto.

---

### D3 [MEDIO] - CLASE `MethodologicalDepth` DEFINIDA DOS VECES

**Ubicación:**
- Primera definición: ~Línea 290 (versión simple)
- Segunda definición: ~Línea 630 (versión extendida)

**Impacto:** Similar a D1, la segunda sobrescribe la primera.

---

### D4 [MEDIO] - IMPORTS NO USADOS / DUPLICADOS

**Descripción:** El archivo tiene 2347 líneas con múltiples imports que pueden no estar todos en uso.

**Recomendación:** Ejecutar `ruff check --select=F401` para identificar imports no usados.

---

### D5 [MEDIO] - FALTA DE TESTS UNITARIOS

**Descripción:** No hay tests dedicados para CARVER en el directorio `tests/`.

**Impacto:** Cambios a CARVER no tienen cobertura de regresión.

---

## PARTE C: PROBLEMA DE UBICACIÓN DE FASE

### P1 [MEDIO] - CARVER ESTÁ EN PHASE_TWO PERO DEBERÍA ESTAR EN PHASE_THREE

**Situación actual:**
```
Phase_two/
├── phase2_00_00_init.py          # Stage 00: Init
├── phase2_10_00_factory.py       # Stage 10: Factory
├── phase2_20_00_loader.py        # Stage 20: Loader
├── phase2_60_00_base_executor_with_contract.py  # Stage 60: Executor
├── phase2_90_00_carver.py        # Stage 90: CARVER ← AQUÍ
```

**Problema conceptual:**
- Phase_two = **Generación de Contratos + Ejecución de Métodos**
- Phase_three = **Scoring + Validación + Síntesis**

CARVER es un **sintetizador de narrativa doctoral**. Su función es:
1. Tomar evidencia ejecutada
2. Generar respuesta estructurada con prosa académica
3. Incluir metodología, brechas, confianza

Esto es **síntesis**, no ejecución. Debería estar en Phase_three.

**Impacto:**
- Phase_two tiene demasiadas responsabilidades
- El flujo de datos es confuso
- CARVER se importa desde Phase_two en lugar de Phase_three

---

## MATRIZ DE IMPACTO

| ID | Tipo | Severidad | Esfuerzo | Dependencias |
|----|------|-----------|----------|--------------|
| C1 | Contractual | CRÍTICO | 4h | Requiere schema v5 |
| C2 | Contractual | ALTO | 2h | Depende de C1 |
| C3 | Contractual | ALTO | 2h | Independiente |
| C4 | Contractual | ALTO | 2h | Independiente |
| C5 | Contractual | MEDIO | 1h | Refactor menor |
| C6 | Contractual | MEDIO | 2h | Mapear a nX_strategy_refined |
| C7 | Contractual | MEDIO | 2h | Agregar sector_context |
| C8 | Contractual | MEDIO | 2h | Agregar cross_cutting |
| D1 | Código | ALTO | 1h | Unificar clases |
| D2 | Código | ALTO | 1h | Eliminar duplicado |
| D3 | Código | MEDIO | 0.5h | Unificar clases |
| D4 | Código | MEDIO | 0.5h | ruff --fix |
| D5 | Código | MEDIO | 4h | Escribir tests |
| P1 | Ubicación | MEDIO | 2h | Mover a Phase_three |

**Esfuerzo total estimado:** 25-28 horas

---

## RECOMENDACIONES

### OPCIÓN A: Actualizar Contratos a Schema v5 (RECOMENDADO)

Agregar a cada contrato:
```json
{
  "human_answer_structure": {
    "methodological_depth": { ... },
    "assembly_flow": { ... },
    "sections": [ ... ],
    "evidence_structure_schema": { ... }
  },
  "confidence_interpretation": { ... },
  "blocking_rules": [ ... ],
  "sector_context": { ... },
  "cross_cutting_context": { ... }
}
```

**Pros:** CARVER funciona sin cambios de código  
**Contras:** Requiere regenerar 300 contratos

### OPCIÓN B: Refactorizar CARVER para Schema v4

Modificar CARVER para usar:
- `method_binding.execution_phases` en lugar de `methodological_depth`
- `fusion_strategies` + `nX_strategy_refined` en lugar de `fusion_specification`
- `evidence_assembly.assembly_rules` en lugar de `assembly_flow`

**Pros:** No requiere cambios a contratos  
**Contras:** CARVER pierde capacidades (sections, confidence_interpretation)

### OPCIÓN C: Híbrido (PRAGMÁTICO)

1. Fijar problemas de código (D1-D4) → 3 horas
2. Mover CARVER a Phase_three (P1) → 2 horas
3. Agregar campos mínimos a contratos:
   - `confidence_interpretation` → 1 hora
   - `blocking_rules` → 1 hora
4. Mapear campos existentes en CARVER:
   - `fusion_strategies` → `nX_strategy_refined` → 2 horas
   - `identity` fallback ya funciona → 0 horas

**Total Opción C:** 9 horas para estado funcional

---

## CONCLUSIÓN

CARVER v3.0 está diseñado para un schema de contrato que **no existe** en el sistema actual. Los contratos v4 tienen una estructura diferente que CARVER no consume correctamente.

**Decisión requerida:**
1. ¿Extender contratos (Opción A)?
2. ¿Refactorizar CARVER (Opción B)?
3. ¿Solución híbrida (Opción C)?

**Antes de mover CARVER a Phase_three**, se recomienda resolver al menos los problemas de código (D1-D4) para tener una base limpia.

---

*Generado: 2026-01-04*
