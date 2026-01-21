# SISAS - ESPECIFICACIÓN FINAL CONSOLIDADA
## Sistema de Irrigación de Señales de Análisis Semántico

**Versión:** 1.0.0
**Fecha:** 2026-01-21
**Estado:** CANÓNICO

---

## 1. RESUMEN EJECUTIVO

### 1.1 Alcance

Esta especificación define la integración completa del sistema SISAS con:
- **476 ítems de información** irrigables
- **10 fases** de procesamiento (P00-P09)
- **17 consumers** distribuidos por fase
- **10 extractores** (MC01-MC10)
- **24 tipos de señales**
- **8 vehículos** de procesamiento

### 1.2 Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FARFAN/SISAS ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Phase 0   │───▶│   Phase 1   │───▶│   Phase 2   │───▶│   Phase 3   │ │
│  │  Bootstrap  │    │ Extraction  │    │ Enrichment  │    │ Validation  │ │
│  │  2 signals  │    │ 10 signals  │    │  3 signals  │    │  3 signals  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │                  │         │
│         ▼                  ▼                  ▼                  ▼         │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              SignalDistributionOrchestrator (SDO)                   │  │
│  │                                                                     │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │  Gate 1  │─▶│  Gate 2  │─▶│  Gate 3  │─▶│  Gate 4  │           │  │
│  │  │  Scope   │  │  Value   │  │Capability│  │ Channel  │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│         │                  │                  │                  │         │
│         ▼                  ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Phase 4   │───▶│   Phase 5   │───▶│   Phase 6   │───▶│  Phase 7-9  │ │
│  │Micro Score  │    │ Meso Score  │    │ Macro Score │    │ Aggregation │ │
│  │  1 signal   │    │  1 signal   │    │  1 signal   │    │  3 signals  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    17 CONSUMERS (por fase)                          │  │
│  │  P0: 2 │ P1: 2 │ P2: 4 │ P3: 2 │ P4: 1 │ P5: 1 │ P6: 1 │ P7-9: 4   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                     476 ÍTEMS IRRIGABLES                            │  │
│  │  Questions: 300 │ PA: 10 │ DIM: 6 │ CL: 4 │ CC: 9 │ Patterns: 142   │  │
│  │  MESO: 4 │ MACRO: 1                                                 │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. CONTEO DE 476 ÍTEMS

### 2.1 Desglose Completo

| Categoría | Cantidad | Detalle |
|-----------|----------|---------|
| Micro Questions | 300 | 30 base × 10 PA |
| Policy Areas | 10 | PA01-PA10 |
| Dimensions | 6 | DIM01-DIM06 |
| Clusters | 4 | CL01-CL04 |
| Cross-Cutting Themes | 9 | CC01-CC09 |
| Meso Questions | 4 | MESO_1-MESO_4 |
| Macro Question | 1 | MACRO_1 |
| Patterns (irrigables) | 142 | Excluye MARGINAL |
| **TOTAL** | **476** | |

### 2.2 Exclusiones

Los siguientes ítems NO se cuentan en los 476:
- Patterns con `irrigability = "MARGINAL"`: ~35 patrones
- Items con `irrigability = "External"`: ~10 items
- Items deprecated o archivados

### 2.3 Fórmula de Verificación

```python
TOTAL = (
    300 +  # Micro Questions (30 × 10 PA)
    10 +   # Policy Areas
    6 +    # Dimensions
    4 +    # Clusters
    9 +    # Cross-Cutting Themes
    4 +    # Meso Questions
    1 +    # Macro Question
    142    # Patterns (irrigables)
)
assert TOTAL == 476
```

---

## 3. SECUENCIA POR EVENTO

### 3.1 Flujo de Eventos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SECUENCIA DE EVENTOS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. CANONICAL_DATA_LOADED                                                   │
│     ├── Trigger: Archivo cargado por vehicle                               │
│     ├── Payload: {file_path, file_type, sha256, size}                      │
│     └── Consumers: phase_00_bootstrap_consumer                              │
│                                                                             │
│  2. SIGNAL_GENERATED                                                        │
│     ├── Trigger: Extractor genera señal                                    │
│     ├── Payload: {signal_id, signal_type, scope, provenance}               │
│     └── Consumers: Según scope.phase                                        │
│                                                                             │
│  3. GATE_VALIDATION_STARTED                                                 │
│     ├── Trigger: SDO recibe señal                                          │
│     ├── Gates: [Scope, Value, Capability, Channel]                         │
│     └── Result: PASS | FAIL                                                 │
│                                                                             │
│  4. SIGNAL_DISPATCHED                                                       │
│     ├── Trigger: Señal pasa todos los gates                                │
│     ├── Payload: {signal_id, target_consumers, timestamp}                  │
│     └── Audit: Registrado en audit_log                                      │
│                                                                             │
│  5. SIGNAL_DELIVERED                                                        │
│     ├── Trigger: Consumer recibe señal                                     │
│     ├── Payload: {signal_id, consumer_id, delivery_time}                   │
│     └── Acknowledgment: Consumer confirma recepción                         │
│                                                                             │
│  6. SIGNAL_PROCESSED                                                        │
│     ├── Trigger: Consumer procesa señal                                    │
│     ├── Payload: {signal_id, consumer_id, result, duration_ms}             │
│     └── Output: Puede generar nuevas señales                                │
│                                                                             │
│  7. PHASE_COMPLETED                                                         │
│     ├── Trigger: Todos los signals de fase procesados                      │
│     ├── Payload: {phase_id, signals_count, success_rate}                   │
│     └── Next: Iniciar siguiente fase                                        │
│                                                                             │
│  8. IRRIGATION_COMPLETED                                                    │
│     ├── Trigger: Todas las fases completadas                               │
│     ├── Payload: {total_signals, total_items, coverage}                    │
│     └── Report: Generar reporte final                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Matriz de Eventos por Fase

| Fase | Eventos Entrada | Eventos Salida | Signals Generados |
|------|-----------------|----------------|-------------------|
| P00 | CANONICAL_DATA_LOADED | PHASE_COMPLETED | 2 |
| P01 | PHASE_COMPLETED(P00) | PHASE_COMPLETED | 10 (MC01-MC10) |
| P02 | PHASE_COMPLETED(P01) | PHASE_COMPLETED | 3 |
| P03 | PHASE_COMPLETED(P02) | PHASE_COMPLETED | 3 |
| P04 | PHASE_COMPLETED(P03) | PHASE_COMPLETED | 1 (×300) |
| P05 | PHASE_COMPLETED(P04) | PHASE_COMPLETED | 1 (×60) |
| P06 | PHASE_COMPLETED(P05) | PHASE_COMPLETED | 1 (×10) |
| P07 | PHASE_COMPLETED(P06) | PHASE_COMPLETED | 1 (×4) |
| P08 | PHASE_COMPLETED(P07) | PHASE_COMPLETED | 1 |
| P09 | PHASE_COMPLETED(P08) | IRRIGATION_COMPLETED | 1 |

---

## 4. CONSUMIDORES POR FASE

### 4.1 Inventario Completo de 17 Consumers

#### Phase 0: Bootstrap (2 consumers)

| Consumer ID | Capabilities | Signal Types |
|-------------|--------------|--------------|
| `phase_00_bootstrap_consumer` | STATIC_LOAD, SIGNAL_PACK, BOOTSTRAP, CONFIG_LOAD, PHASE_MONITORING | SIGNAL_PACK, STATIC_LOAD |
| `phase_00_providers_consumer` | PROVIDER_INIT, DEPENDENCY_INJECTION, PHASE_MONITORING | STATIC_LOAD |

#### Phase 1: Extraction (2 consumers)

| Consumer ID | Capabilities | Signal Types |
|-------------|--------------|--------------|
| `phase_01_extraction_consumer` | EXTRACTION, STRUCTURAL_PARSING, TRIPLET_EXTRACTION, NUMERIC_PARSING, NORMATIVE_LOOKUP, HIERARCHY_PARSING, FINANCIAL_ANALYSIS, POPULATION_PARSING, TEMPORAL_PARSING, CAUSAL_ANALYSIS, NER, SEMANTIC_ANALYSIS, CITATION_PARSING, TREE_CONSTRUCTION, DEMOGRAPHIC_ANALYSIS, DATE_NORMALIZATION, VERB_EXTRACTION, INSTITUTIONAL_RECOGNITION, RELATIONSHIP_EXTRACTION, PHASE_MONITORING | MC01-MC10 |
| `phase_01_enrichment_consumer` | SIGNAL_ENRICHMENT, CPP_INGESTION, DOCUMENT_PARSING, CHUNKING, PHASE_MONITORING | SIGNAL_PACK, STATIC_LOAD |

#### Phase 2: Enrichment (4 consumers)

| Consumer ID | Capabilities | Signal Types |
|-------------|--------------|--------------|
| `phase_02_enrichment_consumer` | ENRICHMENT, PATTERN_MATCHING, KEYWORD_EXTRACTION, ENTITY_RECOGNITION, PHASE_MONITORING | PATTERN_ENRICHMENT, KEYWORD_ENRICHMENT, ENTITY_ENRICHMENT |
| `phase_02_contract_consumer` | CONTRACT_EXECUTION, METHOD_BINDING, N1_N2_N3_N4_PIPELINE, PHASE_MONITORING | PATTERN_ENRICHMENT |
| `phase_02_evidence_consumer` | EVIDENCE_COLLECTION, NEXUS_BUILDING, PHASE_MONITORING | ENTITY_ENRICHMENT |
| `phase_02_executor_consumer` | EXECUTOR, METHOD_INJECTION, DYNAMIC_DISPATCH, PHASE_MONITORING | PATTERN_ENRICHMENT, KEYWORD_ENRICHMENT |

#### Phase 3: Validation (2 consumers)

| Consumer ID | Capabilities | Signal Types |
|-------------|--------------|--------------|
| `phase_03_validation_consumer` | VALIDATION, NORMATIVE_CHECK, ENTITY_CHECK, COHERENCE_CHECK, INTERDEPENDENCY_VALIDATION, PHASE_MONITORING | NORMATIVE_VALIDATION, ENTITY_VALIDATION, COHERENCE_VALIDATION |
| `phase_03_scoring_consumer` | SCORING, SIGNAL_ENRICHED_SCORING, QUALITY_ASSESSMENT, PHASE_MONITORING | COHERENCE_VALIDATION |

#### Phase 4-6: Scoring (3 consumers)

| Consumer ID | Capabilities | Signal Types |
|-------------|--------------|--------------|
| `phase_04_micro_consumer` | SCORING, MICRO_LEVEL, CHOQUET_INTEGRAL, QUESTION_SCORING, PHASE_MONITORING | MICRO_SCORE |
| `phase_05_meso_consumer` | SCORING, MESO_LEVEL, DIMENSION_AGGREGATION, PHASE_MONITORING | MESO_SCORE |
| `phase_06_macro_consumer` | SCORING, MACRO_LEVEL, POLICY_AREA_AGGREGATION, PHASE_MONITORING | MACRO_SCORE |

#### Phase 7-9: Aggregation & Report (4 consumers)

| Consumer ID | Capabilities | Signal Types |
|-------------|--------------|--------------|
| `phase_07_meso_aggregation_consumer` | AGGREGATION, MESO_LEVEL, CLUSTER_AGGREGATION, WEIGHTED_AVERAGE, PHASE_MONITORING | MESO_AGGREGATION |
| `phase_08_macro_aggregation_consumer` | AGGREGATION, MACRO_LEVEL, HOLISTIC_ASSESSMENT, RECOMMENDATION_ENGINE, SIGNAL_ENRICHED, PHASE_MONITORING | MACRO_AGGREGATION |
| `phase_09_report_consumer` | REPORT_GENERATION, ASSEMBLY, EXPORT, VISUALIZATION, PHASE_MONITORING | REPORT_ASSEMBLY |

---

## 5. ALINEACIÓN VOCABULARIO/CAPACIDADES

### 5.1 Referencia: signal_capability_map.json

Ubicación: `canonic_questionnaire_central/_registry/capabilities/signal_capability_map.json`

```json
{
  "signal_capability_requirements": {
    "MC01_STRUCTURAL": {"required": ["TABLE_PARSING"], "optional": []},
    "MC02_QUANTITATIVE": {"required": ["NUMERIC_PARSING"], "optional": ["TABLE_PARSING"]},
    "MC03_NORMATIVE": {"required": ["NER_EXTRACTION"], "optional": []},
    "MC04_PROGRAMMATIC": {"required": [], "optional": ["GRAPH_CONSTRUCTION"]},
    "MC05_FINANCIAL": {"required": ["NUMERIC_PARSING", "FINANCIAL_ANALYSIS"], "optional": ["TABLE_PARSING"]},
    "MC06_POPULATION": {"required": [], "optional": ["NER_EXTRACTION", "SEMANTIC_PROCESSING"]},
    "MC07_TEMPORAL": {"required": ["TEMPORAL_REASONING"], "optional": []},
    "MC08_CAUSAL": {"required": ["CAUSAL_INFERENCE", "GRAPH_CONSTRUCTION"], "optional": ["SEMANTIC_PROCESSING"]},
    "MC09_INSTITUTIONAL": {"required": ["NER_EXTRACTION"], "optional": []},
    "MC10_SEMANTIC": {"required": ["SEMANTIC_PROCESSING", "GRAPH_CONSTRUCTION"], "optional": []},
    "COHERENCE_VALIDATION": {"required": ["INTERDEPENDENCY_VALIDATION"], "optional": ["CAUSAL_INFERENCE"]}
  }
}
```

### 5.2 Referencia: SISAS_IRRIGATION_SPEC.json

Ubicación: `canonic_questionnaire_central/_registry/SISAS_IRRIGATION_SPEC.json`

Este archivo contiene 21 unidades de irrigación organizadas en 4 grupos:
- **CORE_DATA**: 5 unidades
- **REGISTRY_DATA**: 6 unidades
- **DOMAIN_DATA**: 3 unidades
- **OPERATIONAL_DATA**: 7 unidades

---

## 6. VALIDACIÓN DE INTEGRIDAD

### 6.1 Checklist de Validación

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CHECKLIST DE VALIDACIÓN                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CONTEO DE ÍTEMS                                                            │
│  ☐ Total ítems = 476                                                        │
│  ☐ Micro Questions = 300                                                    │
│  ☐ Policy Areas = 10                                                        │
│  ☐ Dimensions = 6                                                           │
│  ☐ Clusters = 4                                                             │
│  ☐ Cross-Cutting = 9                                                        │
│  ☐ Meso Questions = 4                                                       │
│  ☐ Macro Question = 1                                                       │
│  ☐ Patterns (no MARGINAL) = 142                                             │
│                                                                             │
│  CONSUMERS                                                                  │
│  ☐ Total consumers = 17                                                     │
│  ☐ Todos registrados en SDO                                                 │
│  ☐ Todos tienen scopes válidos                                              │
│  ☐ Todos tienen capabilities declaradas                                     │
│                                                                             │
│  EXTRACTORS                                                                 │
│  ☐ Total extractors = 10 (MC01-MC10)                                        │
│  ☐ Todos conectados a SDO                                                   │
│  ☐ Todos emiten signal_type correcto                                        │
│                                                                             │
│  SIGNAL TYPES                                                               │
│  ☐ Total signal types = 24                                                  │
│  ☐ Todos tienen capabilities_required definidos                             │
│  ☐ Todos tienen phase alignment                                             │
│                                                                             │
│  GATES                                                                      │
│  ☐ Gate 1 (Scope) configurado                                               │
│  ☐ Gate 2 (Value) configurado con threshold 0.30                            │
│  ☐ Gate 3 (Capability) configurado                                          │
│  ☐ Gate 4 (Channel) configurado                                             │
│                                                                             │
│  ORCHESTRATOR                                                               │
│  ☐ UnifiedOrchestrator es único                                             │
│  ☐ SISAS integration habilitada                                             │
│  ☐ Factory conectada                                                        │
│  ☐ Todas las fases ejecutables                                              │
│                                                                             │
│  IMPORTS                                                                    │
│  ☐ 0 imports de orchestration.orchestrator                                  │
│  ☐ 0 imports de cross_cutting_infrastructure                                │
│  ☐ Todos usan farfan_pipeline.*                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. ARCHIVOS CANÓNICOS

### 7.1 Lista de Archivos Clave

| Archivo | Propósito | Estado |
|---------|-----------|--------|
| `src/farfan_pipeline/orchestration/__init__.py` | Public API | CANÓNICO |
| `src/farfan_pipeline/orchestration/orchestrator.py` | Único orquestador | CANÓNICO |
| `src/farfan_pipeline/orchestration/factory.py` | Factory única | CANÓNICO |
| `src/farfan_pipeline/orchestration/sisas_integration_hub.py` | Hub SISAS | CANÓNICO |
| `src/farfan_pipeline/orchestration/wiring_config.py` | Configuración cableado | CANÓNICO |
| `canonic_questionnaire_central/core/signal.py` | Definición Signal | CANÓNICO |
| `canonic_questionnaire_central/core/signal_distribution_orchestrator.py` | SDO | CANÓNICO |
| `canonic_questionnaire_central/_registry/SISAS_IRRIGATION_SPEC.json` | Spec irrigación | CANÓNICO |
| `canonic_questionnaire_central/_registry/capabilities/signal_capability_map.json` | Mapeo capacidades | CANÓNICO |
| `canonic_questionnaire_central/_registry/irrigation_validation_rules.json` | Reglas validación | CANÓNICO |
| `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/signal.py` | Signal types | CANÓNICO |
| `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/irrigation/irrigation_map.py` | Mapa irrigación | CANÓNICO |
| `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/irrigation/irrigation_executor.py` | Ejecutor | CANÓNICO |

---

## 8. NOTAS DE IMPLEMENTACIÓN

### 8.1 Orden de Implementación

1. **Primero**: Crear/actualizar `wiring_config.py` ✅
2. **Segundo**: Actualizar `orchestrator.py` con CONSUMER_CONFIGS completo ✅
3. **Tercero**: Actualizar `signal.py` con 24 tipos ✅
4. **Cuarto**: Crear `irrigation_map.py` con modelo de 476 ítems ✅
5. **Quinto**: Actualizar `sisas_integration_hub.py` para conectar todo ✅
6. **Sexto**: Actualizar `irrigation_executor.py` para ejecutar secuencia ✅
7. **Séptimo**: Validar con script completo ⏳

### 8.2 Dependencias Entre Componentes

```
wiring_config.py
       │
       ▼
orchestrator.py ◄──── CONSUMER_CONFIGS
       │
       ▼
sisas_integration_hub.py
       │
       ├──► SDO (signal_distribution_orchestrator.py)
       │
       ├──► Consumers (consumers/__init__.py)
       │
       ├──► Extractors (extractors/*.py)
       │
       └──► Vehicles (vehicles/*.py)
              │
              ▼
       irrigation_executor.py
              │
              ▼
       irrigation_map.py (476 items)
```

---

## 9. ESTADO DE IMPLEMENTACIÓN

### 9.1 Componentes Completados

- ✅ **SignalType enum** (24 tipos) - `signal.py`
- ✅ **IrrigationMap** con 476 items - `irrigation_map.py`
- ✅ **IrrigationExecutor** con event sequencing - `irrigation_executor.py`
- ✅ **PhaseExecutionResult** - `irrigation_executor.py`
- ✅ **4-Gate Validation System** - `signal_distribution_orchestrator.py`
- ✅ **irrigation_validation_rules.json** - Comprehensive rules
- ✅ **wiring_config.py** - Consumer/extractor wiring
- ✅ **Documentation** - SISAS_FILE_MAPPING.md

### 9.2 Próximos Pasos

1. Crear validation script completo
2. Ejecutar validación end-to-end
3. Verificar 476 items en runtime
4. Confirmar 17 consumers registrados
5. Validar 24 signal types operacionales

---

**Documento Mantenido Por:** FARFAN Pipeline Team
**Última Actualización:** 2026-01-21
**Versión:** 1.0.0
**Estado:** ✅ CANÓNICO
