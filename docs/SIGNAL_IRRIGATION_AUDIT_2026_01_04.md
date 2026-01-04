# AUDITORÍA DE IRRIGACIÓN DE SEÑALES F.A.R.F.A.N
**Fecha:** 2026-01-04  
**Estado:** CRÍTICO - Requiere intervención arquitectónica  
**Autor:** Auditoría Sistemática Phase 6  

---

## 1. RESUMEN EJECUTIVO

### 1.1 Diagnóstico Principal
El sistema SISAS (Signal Irrigation Strategic Architecture System) **NO está consumiendo** los datos granulares disponibles en la estructura modular de `canonic_questionnaire_central/`. 

**Problema raíz:** SISAS carga datos exclusivamente desde `questionnaire_monolith.json` → `blocks.micro_questions`, ignorando:
- `policy_areas/PA*/questions.json` (datos específicos por sector)
- `cross_cutting/cross_cutting_themes.json` (8 temas transversales)
- `validations/interdependency_mapping.json` (reglas de dependencia inter-dimensional)
- `scoring/scoring_system.json` (definiciones de modalidades TYPE_A-F)

### 1.2 Impacto Cuantificado

| Métrica | Estado Actual | Estado Ideal | Brecha |
|---------|---------------|--------------|--------|
| Keywords por PA irrigados | 0 | 112+ por PA | 100% pérdida |
| Cross-cutting themes aplicados | 0 | 8 temas × 10 PA | 100% pérdida |
| Interdependency rules aplicadas | 0 | 7 reglas | 100% pérdida |
| Cluster coherence checks | 0 | 4 clusters | 100% pérdida |
| Policy-specific validations | Parcial | Completo | ~60% pérdida |

---

## 2. ARQUITECTURA ACTUAL (AS-IS)

### 2.1 Flujo de Datos Actual

```
┌─────────────────────────────────────────────────────────────────┐
│                     FUENTE DE DATOS                              │
│  canonic_questionnaire_central/questionnaire_monolith.json       │
│  (300 micro_questions con patterns, validations, expected_elems) │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CARGA SINGLETON                               │
│  phase2_10_00_factory.py → load_questionnaire()                  │
│  Único punto de carga en todo el codebase (verificado)           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SISAS SIGNAL REGISTRY                           │
│  signal_registry.py → QuestionnaireSignalRegistry                │
│  Extrae de questionnaire.data.blocks.micro_questions             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                 ┌───────────┼───────────┐
                 ▼           ▼           ▼
         ┌───────────┐ ┌───────────┐ ┌───────────┐
         │Chunking   │ │Micro      │ │Validation │
         │SignalPack │ │Answering  │ │SignalPack │
         │           │ │SignalPack │ │           │
         └───────────┘ └───────────┘ └───────────┘
```

### 2.2 Archivos Clave del Sistema Actual

| Archivo | Rol | LOC |
|---------|-----|-----|
| `phase2_10_00_factory.py` | Singleton loader del questionnaire | ~1800 |
| `signal_registry.py` | Registry central de señales | ~2262 |
| `signal_consumption.py` | Tracking de consumo con hash chain | ~500 |
| `signal_scoring_context.py` | Contexto de scoring | ~380 |
| `signal_context_scoper.py` | Scoping por contexto | ~265 |

### 2.3 Lo que SISAS SÍ extrae (del monolith)

```python
# signal_registry.py línea 1575-1600
def _get_question(self, question_id: str) -> dict[str, Any]:
    blocks = dict(self._questionnaire.data.get("blocks", {}))
    micro_questions = list(blocks.get("micro_questions", []))
    for q in micro_questions:
        if q.get("question_id") == question_id:
            return dict(q)
```

**Campos extraídos por pregunta:**
- `patterns` ✅ (con semantic_expansion, context_requirement, evidence_boost)
- `expected_elements` ✅
- `validations` ✅
- `failure_contract` ✅
- `scoring_modality` ✅
- `dimension_id` ✅
- `policy_area_id` ✅ (solo el ID, no los metadatos)

---

## 3. DATOS DISPONIBLES NO CONSUMIDOS

### 3.1 Estructura Modular Disponible

```
canonic_questionnaire_central/
├── policy_areas/
│   ├── PA01_mujeres_genero/
│   │   ├── metadata.json       ← NO CONSUMIDO
│   │   ├── keywords.json       ← NO CONSUMIDO (112 keywords PA01)
│   │   └── questions.json      ← PARCIALMENTE DUPLICADO EN MONOLITH
│   ├── PA02_violencia_conflicto/
│   │   └── ... (mismo patrón × 10 PAs)
│   └── ...
├── cross_cutting/
│   ├── cross_cutting_themes.json     ← NO CONSUMIDO (8 temas)
│   └── theme_integration_framework.json
├── validations/
│   ├── interdependency_mapping.json  ← NO CONSUMIDO (reglas causales)
│   └── validation_templates.json
├── scoring/
│   └── scoring_system.json           ← PARCIALMENTE CONSUMIDO
├── clusters/
│   ├── CL01_seguridad_paz/
│   └── ... (4 clusters)
└── dimensions/
    ├── DIM01_INSUMOS/
    └── ... (6 dimensiones)
```

### 3.2 Datos Críticos NO Irrigados

#### A. Policy Area Metadata (`PA*/metadata.json`)
```json
{
  "cluster_id": "CL02",
  "dimension_ids": ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"],
  "required_evidence_keys": ["official_stats", "official_documents", "third_party_research"],
  "keywords": ["género", "mujer", "mujeres", "igualdad de género", ...] // 112 items
}
```
**Uso potencial:** 
- `keywords` → Mejorar pattern matching por sector
- `required_evidence_keys` → Validar fuentes de evidencia
- `cluster_id` → Aplicar reglas de coherencia de cluster

#### B. Cross-Cutting Themes (`cross_cutting_themes.json`)
```json
{
  "themes": [
    {
      "theme_id": "CC_ENFOQUE_DIFERENCIAL",
      "applies_to": {
        "dimensions": ["DIM01", "DIM02", ...],
        "policy_areas": ["PA01", "PA05", "PA06"]
      },
      "indicators": ["reconocimiento_grupos_especificos", ...],
      "validation_rules": {
        "required_for": ["PA01", "PA05", "PA06"],
        "optional_for": ["PA02", ...]
      }
    }
    // ... 8 temas totales
  ]
}
```
**Uso potencial:**
- Validar presencia de enfoques transversales por sector
- Aplicar pesos de scoring según aplicabilidad del tema
- Generar recomendaciones de mejora por enfoque faltante

#### C. Interdependency Mapping (`interdependency_mapping.json`)
```json
{
  "cross_dimension_validation_rules": {
    "rule_001": {
      "rule_id": "INTERDEP-001",
      "description": "Every activity (DIM02) must reference at least one diagnostic finding (DIM01)",
      "enforcement": "warning"
    }
    // ... 7 reglas
  },
  "circular_reasoning_detection": {
    "tautology_detection": {
      "patterns": ["lograr\\s+(.+?)\\s+mediante\\s+\\1\\b", ...]
    }
  }
}
```
**Uso potencial:**
- Detectar cadenas causales rotas (DIM01→DIM02→...→DIM06)
- Identificar razonamiento circular automáticamente
- Aplicar penalizaciones por incoherencia inter-dimensional

---

## 4. BRECHAS DE WIRING IDENTIFICADAS

### 4.1 Brecha W1: Keywords por Sector NO Irrigados

**Ubicación del problema:**
- `signal_registry.py` línea 1604: `_extract_indicators_for_pa()` solo extrae patterns con category="INDICADOR"
- NO extrae keywords de `policy_areas/PA*/keywords.json`

**Impacto:**
- Pattern matching limitado a ~15 patterns por pregunta
- Ignora 100+ keywords específicos por sector
- Reduce capacidad de detección semántica

**Código actual:**
```python
def _extract_indicators_for_pa(self, policy_area: str) -> list[str]:
    indicators = []
    blocks = dict(self._questionnaire.data.get("blocks", {}))
    micro_questions = blocks.get("micro_questions", [])
    for q in micro_questions:
        if q.get("policy_area_id") == policy_area:
            for pattern_obj in q.get("patterns", []):
                if pattern_obj.get("category") == "INDICADOR":
                    indicators.append(pattern_obj.get("pattern", ""))
    return sorted({i for i in indicators if i})
```

### 4.2 Brecha W2: Cross-Cutting Themes NO Aplicados

**Ubicación del problema:**
- Archivo `cross_cutting/__init__.py` tiene funciones `get_cross_cutting_themes()` 
- NINGÚN consumidor en SISAS o Phase Two

**Impacto:**
- No se valida presencia de enfoques transversales obligatorios
- Scoring no considera coherencia temática
- Recomendaciones no incluyen enfoques faltantes

### 4.3 Brecha W3: Interdependency Rules NO Ejecutadas

**Ubicación del problema:**
- `interdependency_mapping.json` contiene 7 reglas de validación inter-dimensional
- NINGÚN consumidor implementado

**Impacto:**
- No se detectan cadenas causales rotas
- Razonamiento circular no identificado automáticamente
- Coherencia dimensional no validada

### 4.4 Brecha W4: Contract Generator NO Consume Datos Granulares

**Ubicación del problema:**
- `input_registry.py` línea 1038: `_build_sector_definitions()` solo usa `SECTOR_DEFINITIONS` hardcodeado
- NO carga `policy_areas/PA*/questions.json`

**Código actual:**
```python
def _build_sector_definitions(self) -> dict[str, SectorDefinition]:
    result: dict[str, SectorDefinition] = {}
    for sector_id, sector_data in SECTOR_DEFINITIONS.items():  # HARDCODED!
        result[sector_id] = SectorDefinition(
            sector_id=sector_id,
            canonical_name=sector_data["canonical_name"],
        )
    return result
```

### 4.5 Brecha W5: Scoring Context Incompleto

**Ubicación del problema:**
- `signal_scoring_context.py` tiene defaults si no encuentra modalidad
- NO consume `scoring/scoring_system.json` completo

---

## 5. ECOSISTEMA IDEAL (TO-BE)

### 5.1 Arquitectura Objetivo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FUENTES DE DATOS MODULARES                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  canonic_questionnaire_central/                                              │
│  ├── questionnaire_monolith.json (300 micro_questions) ─────────┐            │
│  ├── policy_areas/PA*/                                          │            │
│  │   ├── metadata.json (keywords, cluster_id, evidence_keys) ──┼──┐         │
│  │   └── questions.json (30 preguntas específicas por sector) ──┼──┤         │
│  ├── cross_cutting/cross_cutting_themes.json (8 temas) ─────────┼──┤         │
│  ├── validations/interdependency_mapping.json (7 reglas) ───────┼──┤         │
│  └── scoring/scoring_system.json (TYPE_A-F definitions) ────────┼──┤         │
└─────────────────────────────────────────────────────────────────┼──┼─────────┘
                                                                   │  │
                                                                   ▼  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MODULAR QUESTIONNAIRE LOADER                            │
│  phase2_10_00_factory.py → load_modular_questionnaire()                      │
│  ├── Carga monolith (base)                                                   │
│  ├── Enriquece con policy_areas/PA*/metadata.json                            │
│  ├── Carga cross_cutting_themes                                              │
│  ├── Carga interdependency_mapping                                           │
│  └── Carga scoring_system completo                                           │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENHANCED SISAS SIGNAL REGISTRY                            │
│  signal_registry.py → EnhancedQuestionnaireSignalRegistry                    │
│  ├── _get_question() → Enriquecido con sector metadata                       │
│  ├── _get_cross_cutting_context() → NEW                                      │
│  ├── _get_interdependency_rules() → NEW                                      │
│  └── _get_cluster_coherence_requirements() → NEW                             │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Enhanced        │ │ CrossCutting    │ │ Interdependency │
│ MicroAnswering  │ │ ValidationPack  │ │ ValidationPack  │
│ SignalPack      │ │ (NEW)           │ │ (NEW)           │
│ + keywords      │ │                 │ │                 │
│ + cluster_ctx   │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONTRACT GENERATOR                                   │
│  contract_generator/ → Consume datos granulares                              │
│  ├── input_registry.py → _build_sector_definitions_from_modular()            │
│  └── contract_assembler.py → Inyecta cross_cutting + interdependency         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Nuevos SignalPacks Propuestos

#### A. CrossCuttingValidationPack
```python
@dataclass(frozen=True)
class CrossCuttingValidationPack:
    """Signal pack for cross-cutting theme validation."""
    applicable_themes: list[str]  # Temas que aplican a este PA
    required_indicators: dict[str, list[str]]  # Por tema
    validation_rules: dict[str, ValidationRule]
    theme_weights: dict[str, float]  # Peso en scoring
```

#### B. InterdependencyValidationPack
```python
@dataclass(frozen=True)
class InterdependencyValidationPack:
    """Signal pack for inter-dimensional validation."""
    dimension_flow: dict[str, list[str]]  # Dependencias
    causal_chain_requirements: list[CausalChainTemplate]
    circular_reasoning_patterns: list[str]  # Regex para detectar
    scoring_adjustments: dict[str, float]  # Bonus/penalty
```

#### C. EnhancedSectorContext
```python
@dataclass(frozen=True)
class EnhancedSectorContext:
    """Enriched sector context for contract generation."""
    sector_id: str
    canonical_name: str
    cluster_id: str
    keywords: list[str]  # 100+ keywords
    required_evidence_keys: list[str]
    applicable_cross_cutting_themes: list[str]
```

---

## 6. PLAN DE IMPLEMENTACIÓN

### 6.1 Fase 1: Extensión de InputRegistry (Prioridad ALTA)

**Objetivo:** Que `input_registry.py` cargue datos modulares

**Cambios requeridos:**

```python
# input_registry.py - NUEVO MÉTODO
def _load_modular_sector_data(self) -> dict[str, EnhancedSectorContext]:
    """Load enriched sector data from canonic_questionnaire_central/policy_areas/"""
    result = {}
    for sector_id, sector_data in SECTOR_DEFINITIONS.items():
        # Load from modular structure
        pa_folder = f"PA{sector_id[-2:]}_*"
        metadata_path = CANONIC_QC / "policy_areas" / pa_folder / "metadata.json"
        keywords_path = CANONIC_QC / "policy_areas" / pa_folder / "keywords.json"
        
        metadata = json.load(metadata_path)
        keywords = json.load(keywords_path).get("keywords", [])
        
        result[sector_id] = EnhancedSectorContext(
            sector_id=sector_id,
            canonical_name=sector_data["canonical_name"],
            cluster_id=metadata.get("cluster_id"),
            keywords=keywords,
            required_evidence_keys=metadata.get("required_evidence_keys", []),
            applicable_cross_cutting_themes=self._get_applicable_themes(sector_id),
        )
    return result
```

**Estimación:** 2-3 horas

### 6.2 Fase 2: Extensión de SignalRegistry (Prioridad ALTA)

**Objetivo:** Que `signal_registry.py` exponga datos granulares

**Cambios requeridos:**

1. Nuevo método `get_sector_keywords(policy_area: str) -> list[str]`
2. Nuevo método `get_cross_cutting_context(policy_area: str) -> CrossCuttingValidationPack`
3. Nuevo método `get_interdependency_rules(dimension_id: str) -> InterdependencyValidationPack`
4. Enriquecer `MicroAnsweringSignalPack` con `sector_keywords` y `cross_cutting_themes`

**Estimación:** 4-6 horas

### 6.3 Fase 3: Loader Modular en Factory (Prioridad MEDIA)

**Objetivo:** Que `phase2_10_00_factory.py` cargue estructura modular

**Cambios requeridos:**

```python
# phase2_10_00_factory.py - NUEVO MÉTODO
def _load_modular_questionnaire_extensions(self) -> ModularExtensions:
    """Load cross-cutting, interdependency, and sector-specific data."""
    return ModularExtensions(
        cross_cutting_themes=self._load_cross_cutting_themes(),
        interdependency_rules=self._load_interdependency_mapping(),
        sector_metadata=self._load_all_sector_metadata(),
        scoring_definitions=self._load_scoring_system(),
    )
```

**Estimación:** 3-4 horas

### 6.4 Fase 4: Contract Generator Enriquecido (Prioridad MEDIA)

**Objetivo:** Que contratos generados incluyan datos granulares

**Cambios requeridos:**

1. `contract_assembler.py` → `_build_question_context()` consume `sector_keywords`
2. Añadir sección `cross_cutting_requirements` en contratos
3. Añadir sección `interdependency_validations` en contratos

**Estimación:** 4-5 horas

### 6.5 Fase 5: Validadores Consumidores (Prioridad BAJA)

**Objetivo:** Phase 8 (Recommendations) y Phase 9 (Reports) consuman datos granulares

**Estimación:** 6-8 horas

---

## 7. PRINCIPIOS DE IMPLEMENTACIÓN

### 7.1 Principio de Irrigación Útil
> "Irrigación si y solo si la información irrigada es útil"

**Aplicación:**
- NO irrigar datos que no serán consumidos
- Cada dato irrigado debe tener consumidor definido
- Validar consumo con hash chains (ya implementado)

### 7.2 Principio de Granularidad
> "Respetar la granularidad de 300 contratos (30 preguntas × 10 sectores)"

**Aplicación:**
- Datos de PA01 solo van a contratos Q*_PA01
- Cross-cutting themes aplicados según `applies_to.policy_areas`
- Interdependency rules aplicadas según `dimension_id`

### 7.3 Principio de Trazabilidad
> "Cada señal debe ser rastreable a su fuente"

**Aplicación:**
- Mantener `sync_source` en cada contrato
- Hash chains de consumo existentes
- Logs estructurados con `source_file` y `line_number`

### 7.4 Principio de Singleton
> "Una sola carga, una sola fuente de verdad"

**Aplicación:**
- `load_questionnaire()` sigue siendo único punto de carga
- Extensiones modulares se cargan UNA VEZ en factory
- Cache inmutable después de construcción

---

## 8. VALIDACIÓN DE ÉXITO

### 8.1 Tests de Wiring
```bash
# Verificar que keywords se irrigan
pytest -k "test_sector_keywords_irrigated" -v

# Verificar cross-cutting themes aplicados
pytest -k "test_cross_cutting_themes_applied" -v

# Verificar interdependency rules ejecutadas
pytest -k "test_interdependency_validation" -v
```

### 8.2 Métricas de Consumo
- `keywords_per_sector`: Debe ser > 100 para cada PA
- `cross_cutting_themes_validated`: Debe ser 8 temas × PAs aplicables
- `interdependency_rules_executed`: Debe ser 7 reglas por evaluación

### 8.3 Auditoría de Contratos
```bash
# Verificar que contratos generados tienen datos granulares
python scripts/audit/verify_contract_granularity.py
```

---

## 9. RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Romper singleton de questionnaire | Alta | Crítico | Cargar extensiones modulares DENTRO del singleton |
| Inconsistencia monolith vs modular | Media | Alto | Sync bidireccional con validación de hash |
| Performance por carga adicional | Baja | Medio | Lazy loading + LRU cache existente |
| Contratos existentes incompatibles | Media | Alto | Regenerar todos los contratos post-cambio |

---

## 10. PRÓXIMOS PASOS INMEDIATOS

1. **[REQUIERE PERMISO]** Modificar `input_registry.py` para cargar datos modulares
2. **[REQUIERE PERMISO]** Extender `signal_registry.py` con nuevos métodos
3. **[REQUIERE PERMISO]** Regenerar 300 contratos con datos granulares

---

## APÉNDICE A: ARCHIVOS A MODIFICAR

| Archivo | Tipo de Cambio | Riesgo |
|---------|----------------|--------|
| `src/farfan_pipeline/phases/Phase_two/contract_generator/input_registry.py` | Extensión | Medio |
| `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signal_registry.py` | Extensión | Alto |
| `src/farfan_pipeline/phases/Phase_two/phase2_10_00_factory.py` | Extensión | Alto |
| `src/farfan_pipeline/phases/Phase_two/contract_generator/contract_assembler.py` | Extensión | Medio |

## APÉNDICE B: NUEVAS ESTRUCTURAS DE DATOS

Ver sección 5.2 para definiciones completas de:
- `CrossCuttingValidationPack`
- `InterdependencyValidationPack`
- `EnhancedSectorContext`

---

**Fin del documento de auditoría**
