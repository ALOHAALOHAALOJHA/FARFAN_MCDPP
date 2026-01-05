# SESIÓN COMPLETA: AUDITORÍA DE IRRIGACIÓN F.A.R.F.A.N
**Fecha:** 2026-01-04  
**Tipo:** Auditoría Fase 6 - Signal Irrigation  
**Estado:** Documentación completa, pendiente implementación

---

# PARTE 1: CONTEXTO INICIAL

## 1.1 Estado Previo (de conversación anterior)
- Fases F0-F5 completadas con 100/100 health score
- Fase 6 enfocada en análisis de irrigación de señales
- 17 brechas identificadas (B1-B7 originales, I1-I10 nuevas)
- Brechas relacionadas con campos v4 no consumidos por NEXUS/CARVER

## 1.2 Solicitud del Usuario
> "PROCEDE IRRADIADO BAJO TUS PRINCIPIOS... INSERTAR MEJORAS QUIRURGICAS QUE HAGAN BOOST"

## 1.3 Corrección Crítica del Usuario
> "HOW ARE YOU ENSURING THAT THE IRRIGATION RECEIVED IS COMPLETELY ALIGNED WITH THE KIND OF QUESTION, THE DIMENSION, THE POLICY AREA AND THE EPISTEMIC NATURE OF THE CONTRACT?"

> "ANULA LOS CAMBIOS... TENEMOS 300 CONTRATOS... TIENES QUE CONSIDERAR UNA FORMULA QUE RESPETE LA GRANULARIDAD DE LOS CONTRATOS"

---

# PARTE 2: ANÁLISIS DE ARQUITECTURA

## 2.1 Flujo de Datos Descubierto

```
questionnaire_monolith.json
        ↓
phase2_10_00_factory.py (load_questionnaire - SINGLETON)
        ↓
QuestionnaireSignalRegistry (signal_registry.py)
        ↓
    ├── ChunkingSignalPack
    ├── MicroAnsweringSignalPack  
    ├── ValidationSignalPack
    ├── AssemblySignalPack
    └── ScoringSignalPack
        ↓
Phase Two Executors → Contracts
```

## 2.2 Estructura del Contract Generator

| Archivo | Propósito |
|---------|-----------|
| `contract_generator.py` | Orquestador para 300 contratos (30 × 10) |
| `contract_assembler.py` | Ensambla cada contrato con TYPE_STRATEGIES, TYPE_GATE_LOGIC |
| `input_registry.py` | Carga inputs - SECTOR_DEFINITIONS hardcodeado |
| `chain_composer.py` | Compone cadena epistémica |

## 2.3 Estructura Modular Descubierta

```
canonic_questionnaire_central/
├── questionnaire_monolith.json      ← SISAS carga SOLO esto
├── policy_areas/
│   ├── PA01_mujeres_genero/
│   │   ├── metadata.json            ← NO CONSUMIDO (112 keywords)
│   │   ├── keywords.json            ← NO CONSUMIDO
│   │   └── questions.json           ← 25K líneas, parcialmente en monolith
│   └── PA02-PA10/                   ← Mismo patrón
├── cross_cutting/
│   └── cross_cutting_themes.json    ← NO CONSUMIDO (8 temas)
├── validations/
│   └── interdependency_mapping.json ← NO CONSUMIDO (7 reglas)
├── scoring/
│   └── scoring_system.json          ← PARCIALMENTE CONSUMIDO
└── clusters/
    └── CL01-CL04/                   ← NO CONSUMIDO
```

---

# PARTE 3: HALLAZGOS CRÍTICOS

## 3.1 Problema Raíz
**SISAS extrae datos SOLO de `questionnaire_monolith.json` → `blocks.micro_questions`**

Código problemático en `signal_registry.py` línea 1575:
```python
def _get_question(self, question_id: str) -> dict[str, Any]:
    blocks = dict(self._questionnaire.data.get("blocks", {}))
    micro_questions = list(blocks.get("micro_questions", []))
    for q in micro_questions:
        if q.get("question_id") == question_id:
            return dict(q)
```

## 3.2 Datos NO Consumidos

### A. Policy Area Metadata (por cada PA)
```json
{
  "cluster_id": "CL02",
  "dimension_ids": ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"],
  "required_evidence_keys": ["official_stats", "official_documents", "third_party_research"],
  "keywords": ["género", "mujer", "mujeres", ...] // 112 items para PA01
}
```

### B. Cross-Cutting Themes (8 temas)
```json
{
  "theme_id": "CC_ENFOQUE_DIFERENCIAL",
  "applies_to": {
    "dimensions": ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"],
    "policy_areas": ["PA01", "PA05", "PA06"]
  },
  "indicators": ["reconocimiento_grupos_especificos", ...],
  "validation_rules": {
    "required_for": ["PA01", "PA05", "PA06"],
    "optional_for": ["PA02", ...]
  }
}
```

### C. Interdependency Mapping (7 reglas)
```json
{
  "cross_dimension_validation_rules": {
    "INTERDEP-001": "Every activity (DIM02) must reference at least one diagnostic finding (DIM01)",
    "INTERDEP-002": "Every product (DIM03) must be traceable to at least one activity (DIM02)",
    ...
  },
  "circular_reasoning_detection": {
    "tautology_detection": {
      "patterns": ["lograr\\s+(.+?)\\s+mediante\\s+\\1\\b", ...]
    }
  }
}
```

## 3.3 Brechas de Wiring (5 identificadas)

| ID | Brecha | Ubicación | Impacto |
|----|--------|-----------|---------|
| W1 | Keywords por sector NO irrigados | `_extract_indicators_for_pa()` solo extrae INDICADOR | Pattern matching limitado |
| W2 | Cross-cutting themes NO aplicados | Ningún consumidor en SISAS | No validación de enfoques |
| W3 | Interdependency rules NO ejecutadas | Ningún consumidor implementado | Cadenas causales no verificadas |
| W4 | Contract Generator NO consume datos granulares | `_build_sector_definitions()` hardcodeado | Contratos sin datos específicos |
| W5 | Scoring Context incompleto | Defaults si no encuentra modalidad | Scoring genérico |

## 3.4 Impacto Cuantificado

| Métrica | Actual | Ideal | Pérdida |
|---------|--------|-------|---------|
| Keywords por PA irrigados | 0 | 112+ | 100% |
| Cross-cutting themes aplicados | 0 | 8 × 10 PA | 100% |
| Interdependency rules aplicadas | 0 | 7 | 100% |
| Cluster coherence checks | 0 | 4 | 100% |

---

# PARTE 4: ARQUITECTURA OBJETIVO

## 4.1 Flujo de Datos Objetivo

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
└─────────────────────────────────────────────────────────────────────────────┘
```

## 4.2 Nuevos SignalPacks Propuestos

### CrossCuttingValidationPack
```python
@dataclass(frozen=True)
class CrossCuttingValidationPack:
    applicable_themes: list[str]
    required_indicators: dict[str, list[str]]
    validation_rules: dict[str, ValidationRule]
    theme_weights: dict[str, float]
```

### InterdependencyValidationPack
```python
@dataclass(frozen=True)
class InterdependencyValidationPack:
    dimension_flow: dict[str, list[str]]
    causal_chain_requirements: list[CausalChainTemplate]
    circular_reasoning_patterns: list[str]
    scoring_adjustments: dict[str, float]
```

### EnhancedSectorContext
```python
@dataclass(frozen=True)
class EnhancedSectorContext:
    sector_id: str
    canonical_name: str
    cluster_id: str
    keywords: list[str]  # 100+ keywords
    required_evidence_keys: list[str]
    applicable_cross_cutting_themes: list[str]
```

---

# PARTE 5: PLAN DE IMPLEMENTACIÓN

## 5.1 Fases de Implementación

| Fase | Objetivo | Archivos | Estimación | Prioridad |
|------|----------|----------|------------|-----------|
| 1 | Extender InputRegistry | `input_registry.py` | 2-3h | ALTA |
| 2 | Extender SignalRegistry | `signal_registry.py` | 4-6h | ALTA |
| 3 | Loader modular en Factory | `phase2_10_00_factory.py` | 3-4h | MEDIA |
| 4 | Contract Generator enriquecido | `contract_assembler.py` | 4-5h | MEDIA |
| 5 | Validadores consumidores | Phase 8 & 9 | 6-8h | BAJA |

## 5.2 Fase 1: Extensión de InputRegistry

```python
# input_registry.py - NUEVO MÉTODO
def _load_modular_sector_data(self) -> dict[str, EnhancedSectorContext]:
    """Load enriched sector data from canonic_questionnaire_central/policy_areas/"""
    result = {}
    for sector_id, sector_data in SECTOR_DEFINITIONS.items():
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

## 5.3 Fase 2: Extensión de SignalRegistry

Nuevos métodos requeridos:
1. `get_sector_keywords(policy_area: str) -> list[str]`
2. `get_cross_cutting_context(policy_area: str) -> CrossCuttingValidationPack`
3. `get_interdependency_rules(dimension_id: str) -> InterdependencyValidationPack`
4. Enriquecer `MicroAnsweringSignalPack` con `sector_keywords` y `cross_cutting_themes`

---

# PARTE 6: PRINCIPIOS APLICADOS

## 6.1 Principio de Irrigación Útil
> "Irrigación si y solo si la información irrigada es útil"

- NO irrigar datos que no serán consumidos
- Cada dato irrigado debe tener consumidor definido
- Validar consumo con hash chains

## 6.2 Principio de Granularidad
> "Respetar la granularidad de 300 contratos (30 preguntas × 10 sectores)"

- Datos de PA01 solo van a contratos Q*_PA01
- Cross-cutting themes aplicados según `applies_to.policy_areas`
- Interdependency rules aplicadas según `dimension_id`

## 6.3 Principio de Trazabilidad
> "Cada señal debe ser rastreable a su fuente"

- Mantener `sync_source` en cada contrato
- Hash chains de consumo existentes
- Logs estructurados con `source_file` y `line_number`

## 6.4 Principio de Singleton
> "Una sola carga, una sola fuente de verdad"

- `load_questionnaire()` sigue siendo único punto de carga
- Extensiones modulares se cargan UNA VEZ en factory
- Cache inmutable después de construcción

---

# PARTE 7: ARCHIVOS CLAVE ANALIZADOS

## 7.1 Archivos de SISAS

| Archivo | LOC | Rol |
|---------|-----|-----|
| `signal_registry.py` | 2262 | Registry central de señales |
| `signal_consumption.py` | 500 | Tracking con hash chain |
| `signal_scoring_context.py` | 380 | Contexto de scoring |
| `signal_context_scoper.py` | 265 | Scoping por contexto |
| `signals.py` | 1017 | SignalPack base |

## 7.2 Archivos de Contract Generator

| Archivo | LOC | Rol |
|---------|-----|-----|
| `contract_generator.py` | ~400 | Orquestador 300 contratos |
| `contract_assembler.py` | ~900 | Ensamblador con TYPE strategies |
| `input_registry.py` | 1238 | Carga inputs (SECTOR_DEFINITIONS hardcoded) |
| `chain_composer.py` | - | Composición de cadena epistémica |

## 7.3 Archivos de Questionnaire Central

| Archivo | Contenido |
|---------|-----------|
| `questionnaire_monolith.json` | 300 micro_questions, blocks, scoring |
| `modular_manifest.json` | Manifest de estructura modular |
| `questionnaire_index.json` | Índice por dimension/PA |
| `policy_areas/PA*/questions.json` | ~25K líneas por PA, 30 preguntas |
| `policy_areas/PA*/metadata.json` | Keywords, cluster_id, evidence_keys |
| `cross_cutting/cross_cutting_themes.json` | 8 temas transversales |
| `validations/interdependency_mapping.json` | 7 reglas de dependencia |
| `scoring/scoring_system.json` | TYPE_A-F definitions |

---

# PARTE 8: VERIFICACIONES REALIZADAS

## 8.1 Comparación Monolith vs Modular

```bash
# Ejecutado durante la sesión
=== QUESTIONNAIRE_MONOLITH.JSON STRUCTURE ===
Top-level keys: ['canonical_notation', 'blocks', 'generated_at', ...]
Blocks keys: ['macro_question', 'meso_questions', 'micro_questions', ...]
micro_questions count: 300
First question keys: ['base_slot', 'cluster_id', 'dimension_id', 'expected_elements', 
                      'failure_contract', 'method_sets', 'patterns', ...]

=== PA01/QUESTIONS.JSON STRUCTURE ===
Top-level keys: ['policy_area_id', 'policy_area_metadata', 'question_count', 'questions']
questions count: 30
First question keys: [..., 'method_sets_source', 'method_sets_sync_timestamp']  # EXTRAS!
```

## 8.2 Datos Exclusivos de Estructura Modular

```bash
=== PA01 POLICY_AREA_METADATA (NOT IN MONOLITH) ===
cluster_id: CL02
dimension_ids: [6 items]
required_evidence_keys: [3 items]
keywords: [112 items]
  Sample: ['género', 'mujer', 'mujeres', 'igualdad de género', 'equidad de género']...

=== CROSS_CUTTING_THEMES.JSON ===
themes count: 8
First theme keys: ['theme_id', 'name', 'description', 'i18n', 'applies_to', 'indicators', 'validation_rules']
  applies_to: {'dimensions': ['DIM01', ...], 'policy_areas': ['PA01', 'PA05', 'PA06']}

=== INTERDEPENDENCY_MAPPING.JSON ===
Top-level keys: ['dimension_flow', 'causal_chain_templates', 'cross_dimension_validation_rules', ...]
```

---

# PARTE 9: PRÓXIMOS PASOS

## 9.1 Acciones Pendientes (Requieren Permiso)

1. **[REQUIERE PERMISO]** Modificar `input_registry.py` para cargar datos modulares
2. **[REQUIERE PERMISO]** Extender `signal_registry.py` con nuevos métodos
3. **[REQUIERE PERMISO]** Regenerar 300 contratos con datos granulares

## 9.2 Tests de Validación a Implementar

```bash
# Verificar que keywords se irrigan
pytest -k "test_sector_keywords_irrigated" -v

# Verificar cross-cutting themes aplicados
pytest -k "test_cross_cutting_themes_applied" -v

# Verificar interdependency rules ejecutadas
pytest -k "test_interdependency_validation" -v
```

## 9.3 Métricas de Éxito

- `keywords_per_sector`: > 100 para cada PA
- `cross_cutting_themes_validated`: 8 temas × PAs aplicables
- `interdependency_rules_executed`: 7 reglas por evaluación

---

# PARTE 10: DOCUMENTOS GENERADOS

1. **Este documento:** `docs/SESSION_IRRIGATION_AUDIT_COMPLETE_2026_01_04.md`
2. **Auditoría formal:** `docs/SIGNAL_IRRIGATION_AUDIT_2026_01_04.md`

---

# APÉNDICE: CÓDIGO CLAVE IDENTIFICADO

## A.1 Punto de Carga Singleton (phase2_10_00_factory.py)

```python
def _load_canonical_questionnaire(self) -> None:
    """Load canonical questionnaire with singleton enforcement and integrity check.
    
    CRITICAL REQUIREMENTS:
    1. This is the ONLY place in the codebase that calls load_questionnaire()
    2. Must enforce singleton pattern (only load once)
    3. Must verify SHA-256 hash for integrity
    """
    if AnalysisPipelineFactory._questionnaire_loaded:
        if AnalysisPipelineFactory._questionnaire_instance is not None:
            self._canonical_questionnaire = AnalysisPipelineFactory._questionnaire_instance
            return
    
    questionnaire = load_questionnaire(self._questionnaire_path)
    AnalysisPipelineFactory._questionnaire_loaded = True
    AnalysisPipelineFactory._questionnaire_instance = questionnaire
```

## A.2 Extracción de Preguntas (signal_registry.py)

```python
def _get_question(self, question_id: str) -> dict[str, Any]:
    """Get question by ID from questionnaire."""
    blocks = dict(self._questionnaire.data.get("blocks", {}))
    micro_questions = list(blocks.get("micro_questions", []))
    
    for q in micro_questions:
        if isinstance(q, dict) and q.get("question_id") == question_id:
            return dict(q)
    raise QuestionNotFoundError(question_id)
```

## A.3 Sector Definitions Hardcodeado (input_registry.py)

```python
SECTOR_DEFINITIONS: dict[str, dict[str, str]] = {
    "PA01": {
        "canonical_id": "PA01",
        "canonical_name": "Derechos de las mujeres e igualdad de género",
    },
    # ... PA02-PA10
}

def _build_sector_definitions(self) -> dict[str, SectorDefinition]:
    result: dict[str, SectorDefinition] = {}
    for sector_id, sector_data in SECTOR_DEFINITIONS.items():  # HARDCODED!
        result[sector_id] = SectorDefinition(
            sector_id=sector_id,
            canonical_name=sector_data["canonical_name"],
        )
    return result
```

---

**FIN DE LA SESIÓN DE AUDITORÍA**

*Documento generado: 2026-01-04*
*Próxima acción: Obtener permiso para implementar Fase 1*
