# ESPECIFICACIÓN TÉCNICA EXHAUSTIVA
## Normalización de SIGNALS y Operaciones Colaterales
### SISAS + canonic_questionnaire_central + Fases Canónicas

**Versión**:  1.0.0  
**Fecha**: 2026-01-04  
**Estado**:  BORRADOR PARA REVISIÓN TÉCNICA  
**Alcance**: Determinismo, integridad referencial, wiring, contratos de interfaz

---

## ÍNDICE

1. [Síntesis de hallazgos cruzados](#1-síntesis-de-hallazgos-cruzados)
2. [Principios normativos innegociables](#2-principios-normativos-innegociables)
3. [BLOQUE A:  Normalización de canonic_questionnaire_central](#3-bloque-a-normalización-de-canonic_questionnaire_central)
4. [BLOQUE B: Contrato técnico de SIGNALS](#4-bloque-b-contrato-técnico-de-signals)
5. [BLOQUE C: Normalización de wiring SISAS](#5-bloque-c-normalización-de-wiring-sisas)
6. [BLOQUE D:  Operaciones en fases canónicas](#6-bloque-d-operaciones-en-fases-canónicas)
7. [BLOQUE E: Sincronización de métodos (governance)](#7-bloque-e-sincronización-de-métodos-governance)
8. [BLOQUE F:  Verificación y auditoría continua](#8-bloque-f-verificación-y-auditoría-continua)
9. [Orden de ejecución y dependencias](#9-orden-de-ejecución-y-dependencias)
10. [Apéndices técnicos](#10-apéndices-técnicos)

---

## 1. SÍNTESIS DE HALLAZGOS CRUZADOS

### 1.1 Coincidencias confirmadas (ambas auditorías + evidencia repo)

| Hallazgo | Auditoría Agente A | Auditoría SISAS | Estado en repo |
|----------|-------------------|-----------------|----------------|
| V2 monolito operativo | ✓ | ✓ | Confirmado:  300 micro, 4 meso, 1 macro |
| V3 es stub/manifest | ✓ | ✓ | Confirmado:  0 blocks, solo referencias modulares |
| Meso usa P1.. P10 (legacy) | ✓ | ✓ | Confirmado en `meso_questions. json` y monolito |
| `provenance` no en schema | ✓ (solo Q285) | ✓ (sistémico) | **50+ ocurrencias** en monolito, no solo Q285 |
| 300/300 tienen method_sets | ✓ | ✓ | Confirmado |
| scoring_modalities vinculados | ✓ | ✓ | Confirmado vía `scoring_definition_ref` |

### 1.2 Hallazgos adicionales (auditoría SISAS, no cubiertos por Agente A)

| Hallazgo | Severidad | Impacto |
|----------|-----------|---------|
| Imports a `cross_cutting_infrastructure.*` no resolubles | CRÍTICO | SISAS no importable en packaging actual |
| `SignalRegistryPort` vs implementación:  mismatch firmas | ALTO | Type checking falla, contratos rotos |
| `signal_loader. py` duplica `signal_registry.py` | MEDIO | Dos sources of truth para patrones |
| `get_git_sha()` introduce no-determinismo ambiental | MEDIO | Hashes de packs no reproducibles entre máquinas |
| Circuit breaker usa reloj (aceptable operacional) | BAJO | No afecta identidad si se separa correctamente |
| Phase 1 llama `analyze_coverage_gaps(list)` con firma `dict` | ALTO | Error silencioso o excepción |
| `signal_wiring_fixes.py` tiene placeholder vacío | ALTO | Fix declarado pero no implementado |

### 1.3 Discrepancias entre auditorías

| Tema | Agente A | SISAS Audit | Resolución |
|------|----------|-------------|------------|
| `provenance` en Q285 | "Solo Q285 tiene extra" | Sistémico (50+) | **SISAS es correcto**:  problema de schema, no de dato aislado |
| Meso IDs | "Actualizar meso_questions.json" | + actualizar monolito v2 | **Ambos necesarios** (monolito tiene copia embebida) |
| V3 fix | "Compilar o cambiar schema" | Igual | Coincidencia |

---

## 2. PRINCIPIOS NORMATIVOS INNEGOCIABLES

### 2.1 Single Source of Truth ejecutable

```
REGLA: El runtime carga ÚNICAMENTE: 
  - questionnaire_monolith.json (V2, operativo), O
  - questionnaire_monolith_v3_compiled.json (futuro, si se implementa compilación)
  
PROHIBIDO:  Cargar stub V3 como si tuviera blocks. 
```

### 2.2 Determinismo fuerte por contrato

```python
# IDENTIDAD (invariante)
signal_pack_id = hash(canonical_json(core_fields))

# CORE_FIELDS incluye: 
- question_id, dimension_id, policy_area_id, cluster_id
- patterns[], method_sets[], validations, scoring_context, semantic_context
- source_hash (del monolito)

# CORE_FIELDS excluye:
- generated_at, timestamps, trace_id, latency_ms, any telemetry

# CANONICAL_JSON: 
json. dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

### 2.3 Integridad referencial total

```
IDs CANÓNICOS (únicos, inmutables):
- Preguntas:     Q001.. Q300
- Dimensiones:   DIM01..DIM06
- Policy Areas: PA01..PA10
- Clusters:     CL01..CL04
- Meso:          MESO_1..MESO_4
- Macro:        MACRO_1

IDs LEGACY (solo para compatibilidad, nunca como PK):
- P1..P10 → mapea a PA01..PA10
- fiscal, salud, etc. → mapea a PA01..PA10
```

### 2.4 Separación estricta identidad vs telemetría

```
IDENTIDAD (afecta hash, debe ser reproducible):
  - Contenido de patrones, métodos, validaciones, scoring, semantic
  - Source file hashes
  
TELEMETRÍA (no afecta hash, puede variar):
  - Timestamps de ejecución
  - Latencias, conteos de retry
  - IDs de traza
  - Estados de circuit breaker
```

---

## 3. BLOQUE A: NORMALIZACIÓN DE canonic_questionnaire_central

### A.1 CC-ID-001 — Normalizar IDs Meso a PA01..PA10

**Ubicación del problema**:
- `canonic_questionnaire_central/meso_questions.json`
- `canonic_questionnaire_central/questionnaire_monolith.json` (líneas ~2060-2200, bloque meso)

**Transformación requerida**: 

```json
// ANTES (incorrecto)
{
  "question_id": "MESO_1",
  "question_text": "¿Cómo se integran los programas en ['P2','P3','P7'].. .",
  "policy_areas": ["P2", "P3", "P7"]
}

// DESPUÉS (correcto)
{
  "question_id": "MESO_1",
  "question_text": "¿Cómo se integran los programas en ['PA02','PA03','PA07']...",
  "policy_areas": ["PA02", "PA03", "PA07"]
}
```

**Archivos a modificar**: 
1. `meso_questions.json`: 4 preguntas MESO
2. `questionnaire_monolith. json`: bloque `blocks. meso_questions`

**Mapeo completo**:
| Legacy | Canónico | Nombre |
|--------|----------|--------|
| P1 | PA01 | Derechos de las mujeres e igualdad de género |
| P2 | PA02 | Prevención de la violencia y protección de la población frente al conflicto armado y la violencia generada por grupos delincuenciales organizados, asociada a economías ilegales |
| P3 | PA03 | Ambiente sano, cambio climático, prevención y atención a desastres |
| P4 | PA04 | Derechos económicos, sociales y culturales |
| P5 | PA05 | Derechos de las víctimas y construcción de paz |
| P6 | PA06 | Derecho al buen futuro de la niñez, adolescencia, juventud y entornos protectores |
| P7 | PA07 | Tierras y territorios |
| P8 | PA08 | Líderes y lideresas, defensores y defensoras de derechos humanos, comunitarios, sociales, ambientales, de la tierra, el territorio y de la naturaleza |
| P9 | PA09 | Crisis de derechos de personas privadas de la libertad |
| P10 | PA10 | Migración transfronteriza |

**Criterios de aceptación**: 
- [ ] `grep -E '"P[0-9]+"' meso_questions.json` retorna 0 matches
- [ ] `grep -E '"P[0-9]+"' questionnaire_monolith.json | grep -v legacy_id` retorna 0 matches
- [ ] Validación referencial: todos los `policy_areas[*]` existen en `canonical_notation. policy_areas`

**Verificación**: 
```python
def verify_cc_id_001():
    with open("meso_questions.json") as f:
        meso = json.load(f)
    
    valid_pas = {f"PA{i: 02d}" for i in range(1, 11)}
    
    for q in meso["meso_questions"]: 
        for pa in q. get("policy_areas", []):
            assert pa in valid_pas, f"Invalid PA:  {pa} in {q['question_id']}"
            assert not pa.startswith("P") or pa.startswith("PA"), f"Legacy ID found: {pa}"
```

---

### A.2 CC-SCHEMA-001 — Permitir `provenance` en PatternItem

**Ubicación del problema**: 
- `canonic_questionnaire_central/questionnaire_schema.json`
- Definición `PatternItem` tiene `additionalProperties: false`
- Monolito tiene `provenance` en 50+ patrones

**Cambio requerido en schema**:

```json
// En definitions.PatternItem. oneOf[0]. properties (y oneOf[1] si existe):
{
  "provenance": {
    "oneOf": [
      { "type": "null" },
      {
        "type":  "object",
        "properties": {
          "source": { "type":  "string" },
          "version": { "type":  "string" },
          "extracted_from": { "type":  "string" },
          "extraction_date": { "type":  "string", "format": "date" },
          "confidence": { "type":  "number", "minimum": 0, "maximum": 1 }
        },
        "additionalProperties": true
      }
    ]
  }
}
```

**Criterios de aceptación**:
- [ ] `jsonschema. validate(monolith, schema)` pasa sin errores de `provenance`
- [ ] Patrones existentes no requieren modificación
- [ ] `provenance` es opcional (puede ser null o ausente)

**Verificación**: 
```python
def verify_cc_schema_001():
    import jsonschema
    
    with open("questionnaire_schema. json") as f:
        schema = json.load(f)
    with open("questionnaire_monolith.json") as f:
        monolith = json.load(f)
    
    # Debe pasar sin ValidationError
    jsonschema.validate(monolith, schema)
```

---

### A.3 CC-V3-001 — Definir semántica de V3 stub

**Problema**: `questionnaire_monolith_v3.json` falla validación contra schema V2 porque es un manifest, no un monolito.

**Decisión arquitectónica (elegir UNA)**:

**Opción A (recomendada): V3 es build manifest**
- Crear `questionnaire_schema_v3_manifest.json` que valide estructura de manifest
- `questionnaire_monolith_v3.json` se valida contra ese schema
- Pipeline nunca carga V3 directamente; si se desea V3, se compila primero

**Opción B: V3 se compila a monolito**
- Script `compile_v3_monolith.py` materializa blocks desde módulos
- Output: `questionnaire_monolith_v3_compiled.json`
- Este sí se valida contra schema V2

**Criterios de aceptación**:
- [ ] V3 stub nunca se carga como runtime substrate
- [ ] Si Opción A:  nuevo schema v3 manifest existe y V3 lo pasa
- [ ] Si Opción B: compiled existe y pasa schema v2

---

### A.4 CC-SCORING-001 — Materialización de scoring_system

**Ubicación**:  `canonic_questionnaire_central/scoring/scoring_system.json`

**Estado actual**: El archivo define modalidades (`TYPE_A`, `MACRO_HOLISTIC`, `MESO_INTEGRATION`, etc.) con thresholds, weights, y failure codes.  Las preguntas referencian vía `scoring_definition_ref`.

**Problema detectado**:  La materialización en SISAS (`signal_scoring_context. py`) usa defaults si no encuentra la modalidad. 

**Especificación de normalización**:

```python
# En ScoringModalityContext.extract_scoring_context():

def extract_scoring_context(self, question_data:  dict) -> ScoringContextPack:
    modality = question_data.get("scoring_modality")
    ref = question_data. get("scoring_definition_ref")
    
    if not modality or not ref:
        raise SignalExtractionError(
            code="SCORING_REF_MISSING",
            question_id=question_data. get("question_id"),
            message="scoring_modality and scoring_definition_ref are required"
        )
    
    # Materializar desde scoring_system.json
    scoring_def = self._resolve_scoring_definition(ref)
    
    if scoring_def is None: 
        raise SignalExtractionError(
            code="SCORING_DEF_NOT_FOUND",
            ref=ref,
            available=list(self. scoring_system.keys())
        )
    
    return ScoringContextPack(
        modality=modality,
        definition_ref=ref,
        thresholds=scoring_def["thresholds"],
        weights=scoring_def. get("weights", {}),
        failure_codes=scoring_def.get("failure_codes", []),
        aggregation_strategy=scoring_def. get("aggregation", "weighted_average")
    )
```

**Criterios de aceptación**:
- [ ] Nunca hay scoring con modalidad "default" silencioso
- [ ] Si `scoring_definition_ref` no existe en scoring_system.json → error trazable
- [ ] 300/300 preguntas tienen materialización válida

---

### A.5 CC-SEMANTIC-001 — Estructura de semantic_layers

**Ubicación**: `questionnaire_monolith. json`, bloque `blocks.semantic_layers`

**Estado actual** (evidencia del repo):
```json
"semantic_layers": {
  "embedding_strategy": {
    "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "dimensions": 384,
    "normalization": "L2"
  },
  "disambiguation_rules": { ... },
  "cross_references": { ... }
}
```

**Especificación para SISAS**: 
- `SignalSemanticContext` debe extraer: 
  1. `embedding_strategy` → configuración (no embeddings, solo config)
  2. `disambiguation_rules` → reglas de desambiguación por pregunta/PA
  3. `cross_references` → links semánticos explícitos

**Criterios de aceptación**:
- [ ] Semantic context nunca genera embeddings en tiempo de extracción (es lazy)
- [ ] Reglas de desambiguación son deterministas (mismo input → mismo output)

---

## 4. BLOQUE B: CONTRATO TÉCNICO DE SIGNALS

### B.1 SIG-PACK-001 — Estructura canónica de SignalPack

**Definición formal (TypedDict/Pydantic)**:

```python
from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class MatchType(str, Enum):
    REGEX = "REGEX"
    LITERAL = "LITERAL"
    SEMANTIC = "SEMANTIC"
    HYBRID = "HYBRID"

class Specificity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class PatternSignal(BaseModel):
    """Señal de patrón extraída del monolito."""
    pattern_id: str = Field(... , description="ID único del patrón")
    pattern:  str = Field(..., description="Expresión del patrón")
    match_type:  MatchType
    category: str
    specificity:  Specificity
    confidence_weight: float = Field(ge=0.0, le=1.0)
    context_scope: Optional[str] = None
    context_requirement: Optional[str] = None
    semantic_expansion: List[str] = Field(default_factory=list)
    provenance: Optional[dict] = None

class MethodSignal(BaseModel):
    """Señal de método de ejecución."""
    method_id: str
    class_name: str
    function_name: str
    method_type: str  # "extraction", "validation", "scoring", "aggregation"
    priority: int = Field(ge=1, le=10)
    depends_on_patterns: List[str] = Field(default_factory=list)
    produces_elements: List[str] = Field(default_factory=list)
    failure_mode: str = "raise"  # "raise", "skip", "default"

class ValidationSignal(BaseModel):
    """Señal de validación."""
    validation_id: str
    rule_type: str  # "required", "format", "range", "cross_field"
    target_field: str
    condition: str
    failure_code: str
    severity: str  # "error", "warning", "info"

class ScoringSignal(BaseModel):
    """Señal de scoring."""
    modality: str
    definition_ref:  str
    thresholds: dict
    weights: dict
    failure_codes: List[str]
    aggregation_strategy:  str

class SemanticSignal(BaseModel):
    """Señal semántica."""
    embedding_config: dict  # Solo config, no embeddings
    disambiguation_rules:  List[dict]
    cross_references:  List[str]

class SignalPack(BaseModel):
    """Pack completo de señales para una pregunta."""
    # Identidad canónica
    question_id: str = Field(..., regex=r"^Q\d{3}$")
    question_global:  str
    dimension_id:  str = Field(..., regex=r"^DIM\d{2}$")
    policy_area_id:  str = Field(..., regex=r"^PA\d{2}$")
    cluster_id: str = Field(..., regex=r"^CL\d{2}$")
    base_slot: int = Field(ge=1, le=300)
    
    # Señales
    patterns: List[PatternSignal]
    methods: List[MethodSignal]
    validations: List[ValidationSignal]
    scoring: ScoringSignal
    semantic: SemanticSignal
    
    # Provenance global
    source_file: str
    monolith_hash: str  # SHA256 del monolito
    schema_version: str
    extraction_version: str
    
    # Identidad derivada (calculada, no almacenada)
    @property
    def signal_pack_id(self) -> str:
        """Hash determinista del contenido."""
        core = {
            "question_id": self. question_id,
            "patterns": [p.dict(exclude={"provenance"}) for p in self. patterns],
            "methods": [m. dict() for m in self. methods],
            "validations": [v.dict() for v in self.validations],
            "scoring": self.scoring.dict(),
            "semantic":  self.semantic.dict(),
            "monolith_hash":  self.monolith_hash
        }
        canonical = json.dumps(core, sort_keys=True, separators=(",", ": "))
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]
```

**Criterios de aceptación**: 
- [ ] Todos los campos requeridos están presentes
- [ ] `signal_pack_id` es reproducible dado el mismo monolito
- [ ] Cambio en cualquier patrón/método/validation/scoring → cambia `signal_pack_id`

---

### B. 2 SIG-PORTS-001 — Interfaz SignalRegistryPort normalizada

**Problema actual** (evidencia):
```python
# En ports.py:
class SignalRegistryPort(Protocol):
    def get_validation_signals(self, level: str) -> Any:  ...  # ← level, no question_id
    def get_scoring_signals(self) -> Any: ...  # ← sin parámetros

# En signal_registry.py (implementación real):
def get_validation_signals(self, question_id: str) -> ValidationSpecificationsPack:  ...
def get_scoring_signals(self, question_id: str) -> ScoringContextPack: ... 
```

**Especificación corregida**: 

```python
from typing import Protocol, Optional
from abc import abstractmethod

class SignalRegistryPort(Protocol):
    """Puerto para acceso a señales del cuestionario."""
    
    @abstractmethod
    def get_chunking_signals(self) -> ChunkingSignalsPack: 
        """Señales para segmentación de chunks (global)."""
        ...
    
    @abstractmethod
    def get_micro_answering_signals(self, question_id: str) -> MicroAnsweringSignalPack:
        """Señales para responder una pregunta micro específica."""
        ... 
    
    @abstractmethod
    def get_validation_signals(self, question_id: str) -> ValidationSpecificationsPack:
        """Señales de validación para una pregunta específica."""
        ... 
    
    @abstractmethod
    def get_scoring_signals(self, question_id: str) -> ScoringContextPack:
        """Señales de scoring para una pregunta específica."""
        ... 
    
    @abstractmethod
    def get_assembly_signals(self, level_id: str) -> AssemblySignalsPack:
        """Señales para agregación a nivel superior. 
        
        Args:
            level_id: ID canónico del nivel (DIM01-06, PA01-10, CL01-04, MESO_1-4, MACRO_1)
        """
        ...
    
    @abstractmethod
    def get_semantic_signals(self, question_id: str) -> SemanticContextPack:
        """Señales semánticas para una pregunta específica."""
        ...
    
    @abstractmethod
    def get_method_signals(self, question_id: str) -> MethodMetadataPack: 
        """Señales de métodos de ejecución para una pregunta."""
        ... 
    
    # Introspección
    @abstractmethod
    def get_source_hash(self) -> str:
        """Hash del monolito fuente."""
        ... 
    
    @abstractmethod
    def list_question_ids(self) -> list[str]:
        """Lista de todos los question_ids disponibles."""
        ... 
```

**Criterios de aceptación**:
- [ ] Port y implementación tienen firmas idénticas
- [ ] `mypy --strict` pasa sin errores de tipo
- [ ] Todos los métodos que requieren `question_id` lo reciben explícitamente

---

### B.3 SIG-HASH-001 — Algoritmo de hashing determinista

**Especificación formal**:

```python
import hashlib
import json
from typing import Any

def canonical_json(obj: Any) -> str:
    """Serialización JSON canónica para hashing determinista. 
    
    Garantías:
    - Orden de claves estable (sort_keys=True)
    - Separadores sin espacios
    - Unicode preservado (ensure_ascii=False)
    - Recursivo en estructuras anidadas
    """
    return json. dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str  # Fallback para tipos no serializables
    )

def compute_signal_pack_id(pack: SignalPack) -> str:
    """Calcula ID determinista de un SignalPack. 
    
    Campos incluidos (identity):
    - question_id, dimension_id, policy_area_id, cluster_id
    - patterns (sin provenance), methods, validations, scoring, semantic
    - monolith_hash
    
    Campos excluidos (telemetry):
    - timestamps, trace_ids, latency metrics
    - provenance en patterns (es metadata, no contenido)
    """
    core_fields = {
        "question_id": pack.question_id,
        "dimension_id":  pack.dimension_id,
        "policy_area_id":  pack.policy_area_id,
        "cluster_id":  pack.cluster_id,
        "patterns": [
            {k: v for k, v in p.dict().items() if k != "provenance"}
            for p in pack.patterns
        ],
        "methods":  [m.dict() for m in pack.methods],
        "validations": [v.dict() for v in pack.validations],
        "scoring": pack.scoring.dict(),
        "semantic":  pack.semantic.dict(),
        "monolith_hash":  pack.monolith_hash
    }
    
    canonical = canonical_json(core_fields)
    full_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
    return full_hash[:16]  # Prefijo de 16 chars para legibilidad

def compute_monolith_hash(monolith_path: str) -> str:
    """Hash del archivo monolito completo."""
    with open(monolith_path, "rb") as f:
        return hashlib. sha256(f. read()).hexdigest()
```

**Criterios de aceptación**:
- [ ] Dos ejecuciones en la misma máquina → mismo hash
- [ ] Dos máquinas con mismo monolito → mismo hash
- [ ] Cambio en un patrón → hash diferente
- [ ] Cambio en timestamp de telemetría → hash igual

---

## 5. BLOQUE C: NORMALIZACIÓN DE WIRING SISAS

### C. 1 SISAS-NAMESPACE-001 — Resolver imports no resolubles

**Problema crítico**:
```python
# En signal_registry.py, signal_consumption.py, etc.: 
from cross_cutting_infrastructure.irrigation_using_signals. SISAS import ... 
from canonic_phases.Phase_two import ...

# Pero el repo real tiene:
src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/
src/farfan_pipeline/phases/Phase_two/
```

**Estrategia A (preferida): Refactor de imports**

Cambiar todos los imports a usar el namespace real:

```python
# ANTES (incorrecto)
from cross_cutting_infrastructure.irrigation_using_signals. SISAS.signals import SignalPack

# DESPUÉS (correcto)
from farfan_pipeline. infrastructure.irrigation_using_signals.SISAS.signals import SignalPack
```

**Archivos a modificar**:
```
src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/
├── __init__.py                      # 35+ imports a corregir
├── signal_registry.py               # imports internos
├── signal_consumption.py
├── signal_consumption_integration.py
├── signal_context_scoper.py
├── signal_contract_validator.py
├── signal_enhancement_integrator.py
├── signal_evidence_extractor.py
├── signal_intelligence_layer.py
├── signal_loader.py
├── signal_method_metadata. py
├── signal_quality_metrics.py
├── signal_resolution. py
├── signal_scoring_context.py
├── signal_semantic_context.py
├── signal_semantic_expander.py
├── signal_validation_specs.py
├── signal_wiring_fixes.py
└── signals. py
```

**Script de refactor**:
```bash
#!/bin/bash
# refactor_sisas_imports.sh

find src/farfan_pipeline -name "*.py" -exec sed -i \
  -e 's/from cross_cutting_infrastructure\./from farfan_pipeline./g' \
  -e 's/from canonic_phases\./from farfan_pipeline.phases./g' \
  -e 's/import cross_cutting_infrastructure\./import farfan_pipeline./g' \
  {} \;
```

**Estrategia B (compatibilidad): Shim package**

Crear alias en src/: 
```
src/
├── cross_cutting_infrastructure/
│   ├── __init__.py  # from farfan_pipeline import *
│   └── irrigation_using_signals/
│       ├── __init__.py
│       └── SISAS/
│           └── __init__.py  # from farfan_pipeline. infrastructure...  import *
└── canonic_phases/
    ├── __init__.py
    └── ... 
```

**Criterios de aceptación**:
- [ ] `python -c "from farfan_pipeline.infrastructure. irrigation_using_signals.SISAS import SignalRegistry"` funciona
- [ ] `pytest tests/` pasa sin errores de import
- [ ] `mypy src/farfan_pipeline` pasa

---

### C. 2 SISAS-LOADER-001 — Deprecar signal_loader. py

**Problema**:  `signal_loader.py` duplica funcionalidad de `signal_registry.py` y usa `get_git_sha()` que introduce no-determinismo.

**Especificación**:

1. **Marcar como deprecated** (no eliminar aún):
```python
# signal_loader.py
import warnings

warnings.warn(
    "signal_loader is deprecated. Use QuestionnaireSignalRegistry from signal_registry.py",
    DeprecationWarning,
    stacklevel=2
)
```

2. **Eliminar `get_git_sha()`** de cualquier ruta de identidad:
```python
# ANTES
def build_signal_pack(... ):
    return SignalPack(
        .. .,
        source_version=get_git_sha()  # ← NO DETERMINISTA
    )

# DESPUÉS
def build_signal_pack(...):
    return SignalPack(
        ...,
        source_version=monolith_hash  # ← DETERMINISTA
    )
```

3. **Migrar consumidores** a `QuestionnaireSignalRegistry`

**Criterios de aceptación**:
- [ ] `grep -r "get_git_sha" src/` retorna 0 en rutas de identidad
- [ ] `grep -r "signal_loader" src/` retorna solo deprecated usage

---

### C. 3 SISAS-WIRING-001 — Implementar placeholder en signal_wiring_fixes.py

**Problema**:
```python
# En signal_wiring_fixes.py
def integrate_context_scoping_in_registry(registry, context_scoper):
    """Production-ready fix for context scoping integration."""
    return []  # ← PLACEHOLDER VACÍO
```

**Especificación**:

```python
def integrate_context_scoping_in_registry(
    registry: QuestionnaireSignalRegistry,
    context_scoper: SignalContextScoper,
    context_requirements: dict[str, str]
) -> list[ScopedSignalPack]: 
    """Integra context scoping en el registry. 
    
    Args:
        registry:  Registry con señales raw
        context_scoper: Scoper con reglas de filtrado
        context_requirements: Mapeo question_id → context requerido
    
    Returns:
        Lista de SignalPacks filtrados por contexto
    
    Raises: 
        SignalScopingError: Si no se puede determinar el contexto
    """
    scoped_packs = []
    
    for question_id in registry.list_question_ids():
        raw_pack = registry. get_micro_answering_signals(question_id)
        context_req = context_requirements. get(question_id, "default")
        
        # Filtrar patrones por contexto
        scoped_patterns = context_scoper.filter_patterns(
            patterns=raw_pack. patterns,
            context=context_req
        )
        
        if not scoped_patterns and raw_pack.patterns:
            # Logging de degradación (no silencioso)
            logger.warning(
                f"All patterns filtered for {question_id} with context {context_req}"
            )
        
        scoped_pack = raw_pack.copy(update={"patterns": scoped_patterns})
        scoped_packs.append(scoped_pack)
    
    return scoped_packs
```

**Criterios de aceptación**:
- [ ] Función retorna lista no vacía cuando hay patrones aplicables
- [ ] Degradación (filtrado total) queda registrada en logs
- [ ] Test coverage para escenarios:  all-pass, partial-filter, all-filtered

---

### C.4 SISAS-DETERMINISM-001 — Separar identidad de telemetría

**Problema**: timestamps y circuit breaker state afectan comportamiento pero no deben afectar identidad.

**Especificación arquitectónica**: 

```python
class SignalPack(BaseModel):
    # IDENTITY FIELDS (participan en hash)
    question_id: str
    patterns: list[PatternSignal]
    methods: list[MethodSignal]
    # ... 
    
    # TELEMETRY FIELDS (excluidos de hash)
    class Telemetry(BaseModel):
        extracted_at: datetime
        extraction_latency_ms: float
        cache_hit: bool
        circuit_breaker_state: str
    
    telemetry: Optional[Telemetry] = None
    
    def compute_identity_hash(self) -> str:
        """Hash solo de campos de identidad."""
        identity_fields = self.dict(exclude={"telemetry"})
        return hashlib. sha256(
            canonical_json(identity_fields).encode()
        ).hexdigest()[:16]
```

**Criterios de aceptación**: 
- [ ] `pack1. telemetry != pack2.telemetry` pero `pack1.compute_identity_hash() == pack2.compute_identity_hash()`
- [ ] Tests demuestran invariancia de hash ante cambios de timestamp

---

## 6. BLOQUE D: OPERACIONES EN FASES CANÓNICAS

### D.1 PH1-ENRICH-001 — Phase One enrichment corregido

**Problema actual** (evidencia):
```python
# En Phase_one/signal_enrichment.py
coverage_gaps = analyze_coverage_gaps(list(... ))  # ← firma espera dict, recibe list
```

**Especificación corregida**: 

```python
# signal_enrichment.py

def enrich_with_signals(
    chunks: list[Chunk],
    registry: SignalRegistryPort
) -> list[EnrichedChunk]: 
    """Enriquece chunks con señales del cuestionario. 
    
    Garantías:
    - 300/300 preguntas tienen señales (o error explícito)
    - Cada enriquecimiento tiene provenance trazable
    - Degradación queda registrada, nunca silenciosa
    """
    enriched = []
    coverage_by_pa:  dict[str, CoverageMetrics] = {}
    
    for chunk in chunks:
        # Obtener señales por cada pregunta en el chunk
        for question_id in chunk.question_ids:
            try:
                pack = registry.get_micro_answering_signals(question_id)
                
                # Registrar cobertura
                pa = pack.policy_area_id
                if pa not in coverage_by_pa:
                    coverage_by_pa[pa] = CoverageMetrics(policy_area=pa)
                coverage_by_pa[pa].add_question(question_id, pack)
                
            except SignalNotFoundError as e:
                # NUNCA silencioso
                logger.error(f"Signal missing for {question_id}: {e}")
                raise PhaseOneEnrichmentError(
                    question_id=question_id,
                    reason="signal_not_found",
                    details=str(e)
                )
        
        enriched.append(EnrichedChunk(chunk=chunk, signals=... ))
    
    # Análisis de gaps (con tipo correcto)
    gaps = analyze_coverage_gaps(coverage_by_pa)  # ← dict, no list
    
    if gaps. has_critical_gaps: 
        raise PhaseOneEnrichmentError(
            reason="critical_coverage_gaps",
            gaps=gaps. critical_gaps
        )
    
    return enriched
```

**Criterios de aceptación**:
- [ ] `analyze_coverage_gaps` recibe `dict[str, CoverageMetrics]`
- [ ] 300/300 cobertura o error explícito
- [ ] Tests de regresión para el bug actual

---

### D.2 PH2-SYNC-001 — Phase Two sincronización con hashes de ruleset

**Especificación**: 

```python
# En phase2_40_00_synchronization.py

@dataclass
class ChunkSyncState:
    chunk_id: str
    content_hash: str
    
    # NUEVO: hashes de señales
    ruleset_hash: str  # Hash del monolito
    signal_pack_hash: str  # Hash del pack aplicable
    
    def is_stale(self, current_ruleset_hash: str) -> bool:
        """Detecta si el chunk está desactualizado por cambio de reglas."""
        return self.ruleset_hash != current_ruleset_hash

def synchronize_chunks(
    chunks: list[Chunk],
    registry: SignalRegistryPort
) -> SyncResult:
    """Sincroniza chunks con invalidación por cambio de reglas."""
    
    current_ruleset_hash = registry.get_source_hash()
    
    for chunk in chunks: 
        cached_state = cache.get(chunk. chunk_id)
        
        if cached_state and cached_state.is_stale(current_ruleset_hash):
            logger.info(f"Invalidating {chunk.chunk_id}:  ruleset changed")
            cache.invalidate(chunk.chunk_id)
            cached_state = None
        
        if not cached_state: 
            # Recalcular
            ... 
```

**Criterios de aceptación**:
- [ ] Cambio en monolito → invalidación de cache de chunks
- [ ] Log explícito de invalidaciones
- [ ] Tests con monoliths diferentes demuestran invalidación

---

### D.3 PH3-SCORING-001 — Phase Three scoring con materialización

**Especificación**: 

```python
# En phase3_signal_enriched_scoring.py

def score_with_signals(
    response: Response,
    registry:  SignalRegistryPort
) -> ScoringResult:
    """Scoring con materialización obligatoria de modalidad."""
    
    question_id = response.question_id
    
    # Obtener scoring context (ya materializado)
    scoring_pack = registry.get_scoring_signals(question_id)
    
    # Validar que la modalidad existe
    if not scoring_pack.modality:
        raise ScoringError(
            code="MODALITY_MISSING",
            question_id=question_id
        )
    
    if not scoring_pack. thresholds:
        raise ScoringError(
            code="THRESHOLDS_MISSING",
            question_id=question_id,
            modality=scoring_pack.modality
        )
    
    # Aplicar scoring con umbrales explícitos
    raw_score = compute_raw_score(response, scoring_pack)
    
    # Determinar nivel según thresholds
    level = determine_level(raw_score, scoring_pack.thresholds)
    
    # Verificar failure codes
    if level < scoring_pack.thresholds.get("minimum", 0):
        failure_code = scoring_pack.failure_codes[0] if scoring_pack. failure_codes else "F-GENERIC"
        return ScoringResult(
            question_id=question_id,
            score=raw_score,
            level=level,
            passed=False,
            failure_code=failure_code
        )
    
    return ScoringResult(
        question_id=question_id,
        score=raw_score,
        level=level,
        passed=True
    )
```

**Criterios de aceptación**: 
- [ ] Nunca hay scoring con modalidad/thresholds default silenciosos
- [ ] Failure codes trazables
- [ ] 300/300 preguntas tienen scoring path definido

---

## 7. BLOQUE E: SINCRONIZACIÓN DE MÉTODOS (GOVERNANCE)

### E.1 GOV-METHODS-001 — Sincronizar 240 métodos

**Archivos**:
- `canonic_questionnaire_central/governance/METHODS_TO_QUESTIONS_AND_FILES.json`
- `canonic_questionnaire_central/governance/METHODS_OPERACIONALIZACION.json`

**Estado actual** (evidencia):
- `METHODS_TO_QUESTIONS_AND_FILES.json`: ~240 métodos con mapeo a questions y files
- `METHODS_OPERACIONALIZACION.json`: ~240 métodos con operacionalización

**Especificación de sincronización**: 

```python
def verify_method_synchronization():
    """Verifica que ambos archivos tengan exactamente los mismos métodos."""
    
    with open("METHODS_TO_QUESTIONS_AND_FILES.json") as f:
        mtqf = json.load(f)
    with open("METHODS_OPERACIONALIZACION.json") as f:
        mop = json.load(f)
    
    methods_mtqf = set(mtqf. get("methods", {}).keys())
    methods_mop = set(mop. get("methods", {}).keys())
    
    # Exactamente los mismos
    assert methods_mtqf == methods_mop, (
        f"Method mismatch:\n"
        f"  Only in MTQF: {methods_mtqf - methods_mop}\n"
        f"  Only in MOP: {methods_mop - methods_mtqf}"
    )
    
    # Exactamente 240
    assert len(methods_mtqf) == 240, f"Expected 240 methods, got {len(methods_mtqf)}"
    
    return True
```

**Criterios de aceptación**: 
- [ ] Ambos archivos tienen exactamente 240 métodos
- [ ] Los sets de method IDs son idénticos
- [ ] Validación corre en CI

---

## 8. BLOQUE F: VERIFICACIÓN Y AUDITORÍA CONTINUA

### F. 1 AUD-SCHEMA-001 — Validación de monolito vs schema

```python
# tests/audit/test_schema_validation.py

def test_monolith_v2_passes_schema():
    """Monolito V2 debe pasar validación de schema."""
    with open("canonic_questionnaire_central/questionnaire_schema.json") as f:
        schema = json.load(f)
    with open("canonic_questionnaire_central/questionnaire_monolith. json") as f:
        monolith = json.load(f)
    
    # No debe lanzar ValidationError
    jsonschema.validate(monolith, schema)

def test_v3_stub_is_not_validated_as_v2():
    """V3 stub no debe intentar validarse como V2."""
    with open("canonic_questionnaire_central/questionnaire_monolith_v3.json") as f:
        v3 = json.load(f)
    
    # V3 es manifest, no tiene blocks
    assert "blocks" not in v3 or v3["blocks"] is None
```

### F.2 AUD-REFINT-001 — Integridad referencial

```python
def test_referential_integrity():
    """Todas las referencias cruzadas son válidas."""
    with open("questionnaire_monolith.json") as f:
        monolith = json.load(f)
    
    valid_pas = {f"PA{i: 02d}" for i in range(1, 11)}
    valid_dims = {f"DIM{i:02d}" for i in range(1, 7)}
    valid_cls = {f"CL{i:02d}" for i in range(1, 5)}
    
    for q in monolith["blocks"]["micro_questions"]:
        assert q["policy_area_id"] in valid_pas
        assert q["dimension_id"] in valid_dims
        assert q["cluster_id"] in valid_cls
    
    # Meso también usa IDs canónicos
    for meso in monolith["blocks"]. get("meso_questions", []):
        for pa in meso. get("policy_areas", []):
            assert pa in valid_pas, f"Invalid PA in meso: {pa}"
```

### F.3 AUD-SIGNALS-001 — Cobertura de irrigación

```python
def test_signal_irrigation_complete():
    """300/300 preguntas tienen señales extraíbles."""
    registry = create_signal_registry()
    
    question_ids = [