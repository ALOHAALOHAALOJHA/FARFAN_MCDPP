# GUÍA DE ARQUEOLOGÍA INVERSA PARA REFACTORIZACIÓN CANÓNICA

## Propósito
Esta guía documenta el proceso metodológico para alinear estructuras de datos **hardcodeadas en Python** con el **JSON canónico** (`questionnaire_monolith.json`). Aplica a todos los métodos del dispensario (`src/methods_dispensary/`) que son consumidos por los Executors.

---

## FASE 0: INVENTARIO DE OBJETIVOS

### 0.1 Identificar Archivo Target
```bash
# Listar todos los archivos del dispensario
ls -la src/methods_dispensary/

# Archivos conocidos:
# - analyzer_one.py      ← MunicipalOntology, SemanticAnalyzer, etc.
# - analyzer_two.py      ← (verificar estructuras hardcodeadas)
# - extractor_*.py       ← (verificar estructuras hardcodeadas)
# - scorer_*.py          ← (verificar estructuras hardcodeadas)
```

### 0.2 Identificar Estructuras Hardcodeadas
Buscar patrones de código que indiquen datos embebidos:

```python
# PATRÓN 1: Diccionarios literales con strings
self.value_chain_links = {
    "diagnostic_planning": ValueChainLink(...)  # ← HARDCODEADO
}

# PATRÓN 2: Listas literales de keywords
instruments=["territorial_diagnosis", "stakeholder_mapping"]  # ← HARDCODEADO

# PATRÓN 3: Dataclasses con defaults fijos
@dataclass
class ValueChainLink:
    name: str
    instruments: list[str]  # ← Los valores vienen hardcodeados
```

---

## FASE 1: LEER EL JSON CANÓNICO

### 1.1 Estructura Base del JSON
```bash
# Ver estructura de alto nivel
cat canonic_questionnaire_central/questionnaire_monolith.json | python3 -c "
import json, sys
m = json.load(sys.stdin)
print('KEYS PRINCIPALES:', list(m.keys()))
print('BLOCKS:', list(m.get('blocks', {}).keys()))
print('CANONICAL_NOTATION:', list(m.get('canonical_notation', {}).keys()))
"
```

### 1.2 Extraer las 30 Preguntas Base (6 dimensiones × 5 preguntas)
```bash
cat canonic_questionnaire_central/questionnaire_monolith.json | python3 -c "
import json, sys
m = json.load(sys.stdin)
qs = m['blocks']['micro_questions'][:30]
for q in qs:
    print(f\"{q['question_id']} | {q['dimension_id']} | {q['base_slot']} | {[e['type'] for e in q.get('expected_elements',[])]}\")
"
```

### 1.3 Resultado Esperado - Estructura Jerárquica
```
NIVEL 0: dimension_id (DIM01-DIM06)     = Dict Key en Python
NIVEL 1: base_slot (D1-Q1 a D6-Q5)      = Keyword Argument #1
NIVEL 2: variable analítica             = Keyword Argument Secundario
NIVEL 3: expected_elements[].type       = Elementos de Lista (criterios de membresía)
```

---

## FASE 2: MAPEO PYTHON ↔ JSON

### 2.1 Tabla de Equivalencias Sintácticas

| Constructo Python | Campo JSON | Ejemplo |
|-------------------|------------|---------|
| `dict_key` | `dimension_id` | `"DIM01"` |
| `name=` (kwarg) | `dimensions[].name` | `"DIAGNÓSTICO"` |
| `instruments=[]` | `expected_elements[].type` | `["cobertura_territorial", ...]` |
| `mediators=[]` | `patterns[].category` | `["identificacion", ...]` |
| `outputs=[]` | `expected_elements[type="formato_*"]` | `["formato_tabular", ...]` |
| `outcomes=[]` | `expected_elements[type="impacto_*"]` | `["impacto_definido", ...]` |
| `bottlenecks=[]` | `failure_contract.abort_if[]` | `["sin_fuentes", ...]` |
| `conversion_rates={}` | `scoring.modality_definitions[].threshold` | `0.75` |
| `capacity_constraints={}` | `validations[].minimum_required` | `3` |

### 2.2 Las 30 Variables Analíticas Canónicas

| SLOT | VARIABLE | `expected_elements[].type` |
|------|----------|---------------------------|
| D1-Q1 | `calidad_informacion` | `cobertura_territorial_especificada, fuentes_oficiales, indicadores_cuantitativos, series_temporales_años` |
| D1-Q2 | `brechas_sesgos` | `cuantificacion_brecha, sesgos_reconocidos, vacios_explicitos` |
| D1-Q3 | `recursos_asignados` | `asignacion_explicita, suficiencia_justificada, trazabilidad_ppi_bpin` |
| D1-Q4 | `capacidad_institucional` | `cuellos_botella, datos_sistemas, gobernanza, procesos, talento_humano` |
| D1-Q5 | `restricciones` | `coherencia_demostrada, restricciones_legales, restricciones_presupuestales, restricciones_temporales` |
| D2-Q1 | `formato_operativo` | `columna_costo, columna_cronograma, columna_producto, columna_responsable, formato_tabular` |
| D2-Q2 | `instrumento_logica` | `instrumento_especificado, logica_causal_explicita, poblacion_objetivo_definida` |
| D2-Q3 | `vinculo_diagnostico` | `aborda_causa_raiz, vinculo_diagnostico_actividad` |
| D2-Q4 | `gestion_riesgos` | `mitigacion_propuesta, riesgos_identificados` |
| D2-Q5 | `secuenciacion` | `complementariedad_explicita, secuenciacion_logica` |
| D3-Q1 | `metas_producto` | `fuente_verificacion, linea_base_producto, meta_cuantitativa` |
| D3-Q2 | `dosificacion` | `dosificacion_definida, proporcionalidad_meta_brecha` |
| D3-Q3 | `trazabilidad` | `trazabilidad_organizacional, trazabilidad_presupuestal` |
| D3-Q4 | `factibilidad` | `coherencia_recursos, factibilidad_tecnica, realismo_plazos` |
| D3-Q5 | `conexion_producto_resultado` | `conexion_producto_resultado, mecanismo_causal_explicito` |
| D4-Q1 | `metrica_outcome` | `horizonte_temporal, linea_base_resultado, meta_resultado, metrica_outcome` |
| D4-Q2 | `cadena_causal` | `cadena_causal_explicita, condiciones_habilitantes, supuestos_identificados` |
| D4-Q3 | `evidencia_justificacion` | `evidencia_comparada, justificacion_capacidad, justificacion_recursos` |
| D4-Q4 | `criterios_exito` | `criterios_exito_definidos, vinculo_resultado_problema` |
| D4-Q5 | `alineacion_estrategica` | `alineacion_ods, alineacion_pnd` |
| D5-Q1 | `impacto_definido` | `impacto_definido, rezago_temporal, ruta_transmision` |
| D5-Q2 | `validez_proxies` | `justifica_validez, usa_indices_compuestos, usa_proxies` |
| D5-Q3 | `limitaciones` | `documenta_validez, proxy_para_intangibles, reconoce_limitaciones` |
| D5-Q4 | `riesgos_sistemicos` | `alineacion_marcos, riesgos_sistemicos` |
| D5-Q5 | `realismo_efectos` | `analisis_realismo, efectos_no_deseados, hipotesis_limite` |
| D6-Q1 | `teoria_cambio` | `diagrama_causal, supuestos_verificables, teoria_cambio_explicita` |
| D6-Q2 | `logica_causal` | `evita_saltos_logicos, proporcionalidad_eslabones` |
| D6-Q3 | `pruebas_pilotos` | `propone_pilotos_o_pruebas, reconoce_inconsistencias` |
| D6-Q4 | `monitoreo_correccion` | `ciclos_aprendizaje, mecanismos_correccion, sistema_monitoreo` |
| D6-Q5 | `enfoque_contextual` | `analisis_contextual, enfoque_diferencial` |

---

## FASE 3: PATRÓN DE REFACTORIZACIÓN

### 3.1 ANTES (Hardcodeado)
```python
class MunicipalOntology:
    def __init__(self) -> None:
        self.value_chain_links = {
            "diagnostic_planning": ValueChainLink(
                name="diagnostic_planning",
                instruments=["territorial_diagnosis", "stakeholder_mapping"],  # HARDCODEADO
                mediators=["technical_capacity", "participatory_processes"],   # HARDCODEADO
                ...
            ),
        }
```

### 3.2 DESPUÉS (Carga Dinámica desde JSON)
```python
from pathlib import Path
import json

QUESTIONNAIRE_PATH = Path(__file__).parent.parent.parent / "canonic_questionnaire_central" / "questionnaire_monolith.json"

class CanonicalOntology:
    """Ontología cargada dinámicamente desde questionnaire_monolith.json."""
    
    def __init__(self, questionnaire_path: Path = QUESTIONNAIRE_PATH) -> None:
        self._load_canonical_structure(questionnaire_path)
    
    def _load_canonical_structure(self, path: Path) -> None:
        with open(path, "r", encoding="utf-8") as f:
            monolith = json.load(f)
        
        self.dimensions: dict[str, DimensionContract] = {}
        self.variables: dict[str, VariableContract] = {}
        
        # Cargar dimensiones
        for dim_key, dim_data in monolith["canonical_notation"]["dimensions"].items():
            self.dimensions[dim_data["code"]] = DimensionContract(
                dimension_id=dim_data["code"],
                name=dim_data["name"],
                label=dim_data["label"],
            )
        
        # Cargar variables (primeras 30 preguntas = 6 dims × 5 vars)
        for q in monolith["blocks"]["micro_questions"][:30]:
            variable_name = self._slot_to_variable_name(q["base_slot"])
            self.variables[q["base_slot"]] = VariableContract(
                slot=q["base_slot"],
                dimension_id=q["dimension_id"],
                variable_name=variable_name,
                membership_criteria=[e["type"] for e in q.get("expected_elements", [])],
                patterns=[p.get("pattern", "") for p in q.get("patterns", [])],
            )
    
    def _slot_to_variable_name(self, slot: str) -> str:
        """Mapea D1-Q1 → calidad_informacion, etc."""
        SLOT_MAP = {
            "D1-Q1": "calidad_informacion",
            "D1-Q2": "brechas_sesgos",
            "D1-Q3": "recursos_asignados",
            "D1-Q4": "capacidad_institucional",
            "D1-Q5": "restricciones",
            "D2-Q1": "formato_operativo",
            "D2-Q2": "instrumento_logica",
            "D2-Q3": "vinculo_diagnostico",
            "D2-Q4": "gestion_riesgos",
            "D2-Q5": "secuenciacion",
            "D3-Q1": "metas_producto",
            "D3-Q2": "dosificacion",
            "D3-Q3": "trazabilidad",
            "D3-Q4": "factibilidad",
            "D3-Q5": "conexion_producto_resultado",
            "D4-Q1": "metrica_outcome",
            "D4-Q2": "cadena_causal",
            "D4-Q3": "evidencia_justificacion",
            "D4-Q4": "criterios_exito",
            "D4-Q5": "alineacion_estrategica",
            "D5-Q1": "impacto_definido",
            "D5-Q2": "validez_proxies",
            "D5-Q3": "limitaciones",
            "D5-Q4": "riesgos_sistemicos",
            "D5-Q5": "realismo_efectos",
            "D6-Q1": "teoria_cambio",
            "D6-Q2": "logica_causal",
            "D6-Q3": "pruebas_pilotos",
            "D6-Q4": "monitoreo_correccion",
            "D6-Q5": "enfoque_contextual",
        }
        return SLOT_MAP.get(slot, slot)


@dataclass
class DimensionContract:
    """Contrato de dimensión analítica."""
    dimension_id: str  # DIM01-DIM06
    name: str          # "DIAGNÓSTICO", "PRODUCTOS", etc.
    label: str         # "D", "P", etc.


@dataclass
class VariableContract:
    """Contrato de variable analítica (comprime una pregunta)."""
    slot: str                      # D1-Q1, D2-Q3, etc.
    dimension_id: str              # DIM01-DIM06
    variable_name: str             # calidad_informacion, formato_operativo, etc.
    membership_criteria: list[str] # expected_elements[].type del JSON
    patterns: list[str]            # patterns[].pattern del JSON (regex)
```

---

## FASE 4: CHECKLIST DE REFACTORIZACIÓN

### Para cada archivo del dispensario:

- [ ] **Paso 1**: Identificar clases con datos hardcodeados
- [ ] **Paso 2**: Listar todos los `dict` y `list` literales
- [ ] **Paso 3**: Mapear cada elemento a su equivalente JSON:
  - ¿Es `dimension_id`?
  - ¿Es `expected_elements[].type`?
  - ¿Es `patterns[].pattern`?
  - ¿Es `validations[]`?
  - ¿Es `scoring.modality_definitions[]`?
- [ ] **Paso 4**: Crear `@dataclass` para el contrato
- [ ] **Paso 5**: Implementar `_load_canonical_structure()`
- [ ] **Paso 6**: Reemplazar hardcoded → carga dinámica
- [ ] **Paso 7**: Agregar tests que validen contra JSON

---

## FASE 5: ARCHIVOS TARGET DEL DISPENSARIO

| Archivo | Clase/Estructura | Estado | Prioridad |
|---------|------------------|--------|-----------|
| `analyzer_one.py` | `MunicipalOntology` | 🔴 HARDCODEADO | P0 |
| `analyzer_one.py` | `ValueChainLink` | 🔴 HARDCODEADO | P0 |
| `analyzer_one.py` | `policy_domains` | 🔴 HARDCODEADO | P1 |
| `analyzer_one.py` | `cross_cutting_themes` | 🔴 HARDCODEADO | P1 |
| `analyzer_two.py` | (verificar) | ⚪ PENDIENTE | P2 |
| `extractor_*.py` | (verificar) | ⚪ PENDIENTE | P2 |
| `scorer_*.py` | (verificar) | ⚪ PENDIENTE | P2 |

---

## FASE 6: COMANDOS ÚTILES DE DIAGNÓSTICO

### 6.1 Encontrar todos los dict/list hardcodeados
```bash
grep -rn "= \[\"" src/methods_dispensary/ | head -20
grep -rn "= {\"" src/methods_dispensary/ | head -20
```

### 6.2 Verificar qué métodos usan qué estructuras
```bash
grep -rn "self\.value_chain" src/methods_dispensary/
grep -rn "self\.policy_domains" src/methods_dispensary/
grep -rn "self\.ontology\." src/methods_dispensary/
```

### 6.3 Verificar que el JSON tiene los campos esperados
```bash
cat canonic_questionnaire_central/questionnaire_monolith.json | python3 -c "
import json, sys
m = json.load(sys.stdin)
q = m['blocks']['micro_questions'][0]
print('CAMPOS DE UNA PREGUNTA:')
for k in sorted(q.keys()):
    print(f'  - {k}: {type(q[k]).__name__}')
"
```

---

## RESUMEN EJECUTIVO

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUEOLOGÍA INVERSA                          │
├─────────────────────────────────────────────────────────────────┤
│  1. IDENTIFICAR estructura hardcodeada en Python               │
│  2. LEER las 30 preguntas base del JSON                        │
│  3. MAPEAR cada elemento Python → campo JSON                   │
│  4. CREAR @dataclass para el contrato                          │
│  5. IMPLEMENTAR carga dinámica desde JSON                      │
│  6. VALIDAR con tests                                          │
└─────────────────────────────────────────────────────────────────┘

FÓRMULA CLAVE:
  expected_elements[].type  =  elementos de lista del kwarg Python
  
  JSON: {"type": "cobertura_territorial_especificada"}
    ↓
  Python: calidad_informacion=["cobertura_territorial_especificada", ...]
```

---

## AUTOR Y CONTEXTO
- **Fecha**: 2024-12-11
- **Contexto**: Refactorización de F.A.R.F.A.N para alineación canónica
- **Tiempo invertido en descubrimiento**: ~3 horas de gimnasia mental
- **Aplicable a**: Todos los archivos de `src/methods_dispensary/` que consumen los Executors
