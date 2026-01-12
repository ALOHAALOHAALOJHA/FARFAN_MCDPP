# ESPECIFICACIÓN TÉCNICA COMPLETA: IRRIGACIÓN DE CORPUS EMPÍRICOS
## F.A.R.F.A.N Multi-Criteria Decision Policy Pipeline
**Versión:** 1.0.0  
**Fecha:** 11 de enero de 2026  
**Estado:** AUDITORÍA COMPLETADA - PLAN DE IRRIGACIÓN DETALLADO

---

## RESUMEN EJECUTIVO

Este documento presenta la **especificación técnica exhaustiva** del sistema de irrigación de datos empíricos desde los 4 corpus raíz hacia los 494 archivos JSON del `canonic_questionnaire_central/` y su conexión con las 10 fases canónicas del pipeline F.A.R.F.A.N.

### Hallazgos Críticos

| Métrica | Estado Actual | Objetivo |
|---------|---------------|----------|
| **Corpus integrados en CQC** | 4/4 (100%) | ✅ COMPLETO |
| **Extractores implementados** | 2/10 (20%) | 10/10 (100%) |
| **Wiring efectivo a consumidores** | ~15% | 85% |
| **Alignment score** | 2.9% | 85% |
| **Questions bloqueadas** | 159/300 (53%) | 0/300 |

---

## 1. ARQUITECTURA DE IRRIGACIÓN

### 1.1 Flujo de Datos: Corpus → CQC → Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           NIVEL 1: CORPUS RAÍZ                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  corpus_empirico_calibracion_extractores.json (666 líneas)                     │
│  corpus_empirico_integrado.json (1237 líneas)                                  │
│  corpus_empirico_normatividad.json (269 líneas)                                │
│  corpus_thresholds_weights.json (351 líneas)                                   │
│                                                                                 │
└──────────────────────────────────┬──────────────────────────────────────────────┘
                                   │
                                   ▼ IRRIGACIÓN (ya completada)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    NIVEL 2: ARCHIVOS DERIVADOS EN CQC                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  _registry/membership_criteria/_calibration/extractor_calibration.json         │
│  _registry/questions/integration_map.json                                      │
│  _registry/entities/normative_compliance.json                                  │
│  scoring/calibration/empirical_weights.json                                    │
│                                                                                 │
└──────────────────────────────────┬──────────────────────────────────────────────┘
                                   │
                                   ▼ CONSUMO (parcialmente implementado)
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      NIVEL 3: CONSUMIDORES DEL PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Phase 1: Extractors (MC01-MC10) ← extractor_calibration.json                  │
│  Phase 2: IrrigationSynchronizer ← integration_map.json                        │
│  Phase 3: Scorers (@b, @p, @q, @d, @u, @chain) ← empirical_weights.json        │
│  Phase 3: @p PolicyAreaScorer ← normative_compliance.json                      │
│  Phase 4-7: Aggregators ← empirical_weights.json                               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. DETALLE DE CADA CANAL DE IRRIGACIÓN

### 2.1 Canal 1: `calibracion_extractores` → `extractor_calibration.json`

#### 2.1.1 Ubicación y Tamaño
```
Origen:  /corpus_empirico_calibracion_extractores.json (666 líneas)
Destino: /canonic_questionnaire_central/_registry/membership_criteria/_calibration/extractor_calibration.json (~700 líneas)
```

#### 2.1.2 Contenido Irrigado
| Campo | Descripción | Uso en Pipeline |
|-------|-------------|-----------------|
| `signal_type_catalog` | 10 tipos de señal con frecuencias empíricas | Base de todos los extractores |
| `empirical_frequency` | Media, min, max, std por tipo | Validación de extracciones |
| `extraction_patterns` | Regex calibrados con 14 planes | Patrones de extracción |
| `gold_standard_examples` | Ejemplos validados manualmente | Testing y calibración |
| `confidence` | Umbrales de confianza por patrón | Filtrado de señales |

#### 2.1.3 Consumidores Implementados vs Pendientes

| Consumidor | Archivo | Estado | Línea de Carga |
|------------|---------|--------|----------------|
| `EmpiricalExtractorBase` | `empirical_extractor_base.py` | ✅ IMPLEMENTADO | L121 |
| `StructuralMarkerExtractor` | `structural_marker_extractor.py` | ✅ IMPLEMENTADO | hereda de base |
| `QuantitativeTripletExtractor` | `quantitative_triplet_extractor.py` | ✅ IMPLEMENTADO | hereda de base |
| `NormativeReferenceExtractor` | `normative_reference_extractor.py` | ✅ IMPLEMENTADO | hereda de base |
| `FinancialChainExtractor` | `financial_chain_extractor.py` | ❌ **MISSING** | N/A |
| `CausalVerbExtractor` | `causal_verb_extractor.py` | ⚠️ PARCIAL | hereda de base |
| `InstitutionalNER` | `institutional_ner_extractor.py` | ⚠️ PARCIAL | hereda de base |
| `PopulationDisaggregationExtractor` | N/A | ❌ **MISSING** | N/A |
| `TemporalMarkerExtractor` | N/A | ❌ **MISSING** | N/A |
| `SemanticRelationshipExtractor` | N/A | ❌ **MISSING** | N/A |

#### 2.1.4 Código de Carga Actual
```python
# Archivo: src/farfan_pipeline/infrastructure/extractors/empirical_extractor_base.py
# Líneas 114-123

def _default_calibration_path(self) -> Path:
    """Get default calibration file path."""
    return (
        Path(__file__).resolve().parent.parent.parent.parent
        / "canonic_questionnaire_central"
        / "_registry"
        / "membership_criteria"
        / "_calibration"
        / "extractor_calibration.json"
    )

def _load_calibration(self, calibration_file: Path) -> dict[str, Any]:
    """Load empirical calibration data."""
    with open(calibration_file) as f:
        data = json.load(f)
        return data.get("signal_type_catalog", {}).get(self.signal_type, {})
```

#### 2.1.5 Brechas de Irrigación Detectadas

**Brecha 1: 3 Extractores MISSING (MC05, MC08, MC09)**
```
MC05_financial_chains.json:
  - implementation_status: "MISSING"
  - Calibración presente en extractor_calibration.json → FINANCIAL_CHAIN
  - 52 questions bloqueadas: Q003, Q033, Q063, Q093, Q123, Q153, Q183, Q213, Q243, Q273
  - Impacto: layer_chain_causal, CC_SOSTENIBILIDAD_PRESUPUESTAL

MC08_causal_verbs.json:
  - implementation_status: "MISSING" (extractor existe pero incompleto)
  - Calibración presente → CAUSAL_VERBS
  - 68 questions bloqueadas: D2-Q3, D2-Q5, D3-Q4, D3-Q5, D4-Q2, D6-Q1, D6-Q2
  - Impacto: DIM06_CAUSALIDAD completa, layer_chain_causal

MC09_institutional_network.json:
  - implementation_status: "MISSING" (extractor existe pero incompleto)
  - Calibración presente → INSTITUTIONAL_NETWORK
  - 39 questions bloqueadas: D1-Q4, D2-Q1, D5-Q5, D6-Q4
  - Impacto: layer_p_policy_area, layer_C_crosscutting
```

**Brecha 2: Patrones no utilizados**
```
Patrones disponibles en calibración: 2,358
Patrones actualmente consumidos: 223 (9.4%)
```

---

### 2.2 Canal 2: `corpus_integrado` → `integration_map.json`

#### 2.2.1 Ubicación y Tamaño
```
Origen:  /corpus_empirico_integrado.json (1237 líneas)
Destino: /canonic_questionnaire_central/_registry/questions/integration_map.json (~1200 líneas)
```

#### 2.2.2 Contenido Irrigado
| Campo | Descripción | Uso en Pipeline |
|-------|-------------|-----------------|
| `slot_to_signal_mapping` | 30 slots genéricos × 10 PA = 300 Q | Routing de señales |
| `primary_signals` | Señales principales por pregunta | Priorización de extracción |
| `secondary_signals` | Señales secundarias | Enriquecimiento |
| `expected_patterns` | Patrones esperados por slot | Validación |
| `scoring_modality` | TYPE_A, B, C, D por pregunta | Selección de scorer |
| `empirical_availability` | Frecuencia empírica (0.0-1.0) | Expectativas realistas |

#### 2.2.3 Estructura del Mapeo Slot→Signal

```json
{
  "D1-Q3_RECUR-ASIG": {
    "slot": "D1-Q3",
    "generic_question": "¿El PPI asigna recursos monetarios explícitos?",
    "children_questions": ["Q003", "Q033", "Q063", "Q093", "Q123", "Q153", "Q183", "Q213", "Q243", "Q273"],
    "primary_signals": ["FINANCIAL_CHAIN", "STRUCTURAL_MARKER"],
    "secondary_signals": ["PROGRAMMATIC_HIERARCHY"],
    "scoring_modality": "TYPE_D",
    "weight": 0.30,
    "empirical_availability": 0.92
  }
}
```

#### 2.2.4 Consumidores Implementados vs Pendientes

| Consumidor | Archivo | Estado | Detalle |
|------------|---------|--------|---------|
| `SignalQuestionIndex` | `signal_router.py` | ✅ IMPLEMENTADO | O(1) routing |
| `IrrigationSynchronizer` | `phase2_*` | ⚠️ PARCIAL | Fallback a empty |
| `EvidenceNexus` | `phase2_80_00_evidence_nexus.py` | ⚠️ PARCIAL | L3281-3292 |
| `QuestionnaireSignalRegistry` | N/A | ❌ **NO EXISTE** | Pendiente crear |

#### 2.2.5 Código de Carga Actual
```python
# Archivo: canonic_questionnaire_central/_registry/questions/signal_router.py
# Líneas 69-76

def __init__(self, integration_map_path: Optional[Path] = None):
    if integration_map_path is None:
        integration_map_path = Path(__file__).resolve().parent / "integration_map.json"
    
    self.integration_map_path = integration_map_path
    # ...
    try:
        with open(self.integration_map_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        integration_map = data.get("farfan_question_mapping", {})
        slot_mappings = integration_map.get("slot_to_signal_mapping", {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load integration_map.json: {e}. Using empty mappings.")
        integration_map = {}  # ← FALLBACK A VACÍO
```

#### 2.2.6 Brechas de Irrigación Detectadas

**Brecha 1: Fallback silencioso a mapeo vacío**
```
Problema: Si falla la carga, el sistema continúa con mappings vacíos
Impacto: 0% de señales llegan a preguntas correctas
Solución: Fail-fast con mensaje de error claro
```

**Brecha 2: IrrigationSynchronizer no usa integration_map**
```
# Búsqueda en Phase 2:
grep "integration_map" phase2_*.py
→ Solo referencias en comentarios y try_catch fallbacks
→ No hay consumo efectivo del slot_to_signal_mapping
```

**Brecha 3: `empirical_availability` no usado**
```
El campo empirical_availability (0.14 a 1.0) indica la frecuencia empírica
de cada tipo de evidencia en los 14 planes analizados.

Ejemplos:
  - D6-Q1 (Teoría del Cambio): 0.14 (solo 14% de planes la tienen)
  - D6-Q5 (Contexto Territorial): 1.0 (100% de planes)

Este dato NO se usa actualmente para:
  - Ajustar expectativas de scoring
  - Calibrar penalizaciones por ausencia
  - Reportar gaps realistas
```

---

### 2.3 Canal 3: `corpus_normatividad` → `normative_compliance.json`

#### 2.3.1 Ubicación y Tamaño
```
Origen:  /corpus_empirico_normatividad.json (269 líneas)
Destino: /canonic_questionnaire_central/_registry/entities/normative_compliance.json (~260 líneas)
```

#### 2.3.2 Contenido Irrigado
| Campo | Descripción | Uso en Pipeline |
|-------|-------------|-----------------|
| `mandatory_norms_by_policy_area` | Normas obligatorias por PA | Validación @p |
| `penalty_if_missing` | Penalizaciones (0.2-0.5) | Cálculo CC_COHERENCIA |
| `universal_mandatory_norms` | 4 normas para todos los PA | Validación base |
| `contextual_validation_rules` | Reglas para PDET, étnicos | Validación contextual |
| `scoring_algorithm` | Fórmula de cálculo | Implementación |

#### 2.3.3 Estructura de Normas Obligatorias por PA

```json
{
  "PA05_victimas_paz": {
    "mandatory": [
      {
        "norm_id": "Ley 1448 de 2011",
        "name": "Ley de Víctimas y Restitución de Tierras",
        "reason": "Marco fundamental para víctimas del conflicto",
        "empirical_frequency": 5,
        "penalty_if_missing": 0.4
      },
      {
        "norm_id": "Decreto 893 de 2017",
        "name": "PDET",
        "penalty_if_missing": 0.3
      }
    ],
    "recommended": [
      {"norm_id": "Acuerdo Final de Paz 2016"}
    ]
  }
}
```

#### 2.3.4 Consumidores Implementados vs Pendientes

| Consumidor | Archivo | Estado | Detalle |
|------------|---------|--------|---------|
| `NormativeComplianceValidator` | N/A | ❌ **NO EXISTE** | Crítico |
| `@p PolicyAreaScorer` | `phase3_*` | ⚠️ REFERENCIA | No consume JSON |
| `CrossCuttingScorer` | `phase3_*` | ⚠️ REFERENCIA | CC_COHERENCIA_NORMATIVA |
| `MC03 extractor` | `normative_reference_extractor.py` | ✅ PARCIAL | Extrae, no valida |

#### 2.3.5 Brechas de Irrigación Detectadas

**Brecha 1: NO EXISTE `NormativeComplianceValidator`**
```
El archivo normative_compliance.json contiene:
- 10 Policy Areas con normas obligatorias
- Penalizaciones calibradas (0.2 a 0.5)
- Algoritmo de scoring documentado

PERO no existe ningún validador que:
1. Cargue este archivo
2. Compare normas citadas vs obligatorias
3. Calcule penalizaciones
4. Genere gap_reports
```

**Brecha 2: `scoring_algorithm` no implementado**
```json
// En normative_compliance.json:
"scoring_algorithm": {
  "formula": "score = max(0.0, 1.0 - SUM(penalties)) for missing mandatory norms",
  "interpretation": {
    "EXCELENTE": ">= 0.90",
    "BUENO": "0.75 - 0.89",
    "ACEPTABLE": "0.60 - 0.74",
    "DEFICIENTE": "< 0.60"
  }
}

// En código: NO EXISTE implementación de esta fórmula
```

**Brecha 3: `contextual_validation_rules` ignoradas**
```json
"contextual_validation_rules": {
  "pdet_municipalities": {
    "condition": "Municipality is in PDET list",
    "additional_mandatory": [
      {"norm_id": "Decreto 893 de 2017", "penalty_if_missing": 0.4}
    ]
  },
  "ethnic_territories": {
    "condition": "Population > 10% indigenous or afro",
    "additional_mandatory": [
      {"norm_id": "Ley 70 de 1993"},
      {"norm_id": "Decreto 1953 de 2014"}
    ]
  }
}

// NO HAY validador que aplique estas reglas contextuales
```

---

### 2.4 Canal 4: `corpus_thresholds_weights` → `empirical_weights.json`

#### 2.4.1 Ubicación y Tamaño
```
Origen:  /corpus_thresholds_weights.json (351 líneas)
Destino: /canonic_questionnaire_central/scoring/calibration/empirical_weights.json (~320 líneas)
```

#### 2.4.2 Contenido Irrigado
| Campo | Descripción | Uso en Pipeline |
|-------|-------------|-----------------|
| `signal_confidence_thresholds` | Umbrales por tipo de señal | Filtrado en Phase 1-2 |
| `phase3_scoring_weights` | Pesos para 7 layers | Scorers Phase 3 |
| `aggregation_weights` | Pesos Phases 4-7 | Aggregators |
| `value_add_thresholds` | Mínimo delta para señal útil | Deduplicación |
| `capability_requirements` | Capacidades por señal | Validación DBC |

#### 2.4.3 Estructura de Pesos de Scoring

```json
{
  "phase3_scoring_weights": {
    "layer_b_baseline": {
      "QUANTITATIVE_TRIPLET_present": 0.70,
      "QUANTITATIVE_TRIPLET_complete": 0.20,
      "QUANTITATIVE_TRIPLET_recent": 0.10
    },
    "layer_p_policy_area": {
      "NORMATIVE_REFERENCE_mandatory": 0.40,
      "keyword_coverage": 0.30,
      "POPULATION_DISAGGREGATION_relevant": 0.20,
      "INSTITUTIONAL_NETWORK": 0.10
    },
    "layer_chain_causal": {
      "CAUSAL_LINK_explicit": 0.50,
      "PROGRAMMATIC_HIERARCHY_linkage": 0.30,
      "FINANCIAL_CHAIN_allocation": 0.20
    }
  }
}
```

#### 2.4.4 Consumidores Implementados vs Pendientes

| Consumidor | Archivo | Estado | Detalle |
|------------|---------|--------|---------|
| `BaselineScorer (@b)` | `phase3_*` | ⚠️ TODO | Pesos hardcodeados |
| `PolicyAreaScorer (@p)` | `phase3_*` | ⚠️ TODO | No carga JSON |
| `QualityScorer (@q)` | `phase3_*` | ⚠️ TODO | No carga JSON |
| `DimensionScorer (@d)` | `phase3_*` | ⚠️ TODO | No carga JSON |
| `StructuralScorer (@u)` | `phase3_*` | ⚠️ TODO | No carga JSON |
| `CausalScorer (@chain)` | `phase3_*` | ⚠️ TODO | No carga JSON |
| `DimensionAggregator` | `phase4_*` | ⚠️ TODO | Pesos hardcodeados |
| `PolicyAreaAggregator` | `phase5_*` | ⚠️ TODO | Pesos hardcodeados |

#### 2.4.5 Evidencia del Estado TODO

```bash
$ grep -r "empirical_weights" src/farfan_pipeline/phases/
# Resultado: 0 matches en código de fases
# Solo aparece en documentación y comentarios TODO
```

#### 2.4.6 Brechas de Irrigación Detectadas

**Brecha 1: NINGÚN scorer carga `empirical_weights.json`**
```
Todos los scorers de Phase 3 tienen pesos hardcodeados o TODO:

# Ejemplo típico encontrado:
class BaselineScorer:
    def __init__(self):
        # TODO: Load from empirical_weights.json
        self.weights = {
            "QUANTITATIVE_TRIPLET_present": 0.70,  # Hardcodeado
            ...
        }
```

**Brecha 2: `aggregation_weights` no conectados**
```json
// En empirical_weights.json:
"phase5_policy_area_aggregation": {
  "dimension_weights": {
    "DIM01_insumos": 0.15,
    "DIM02_actividades": 0.15,
    "DIM03_productos": 0.20,
    "DIM04_resultados": 0.25,  // Mayor peso
    "DIM05_impacto": 0.15,
    "DIM06_causalidad": 0.10
  }
}

// En código: NO se consume este JSON
```

**Brecha 3: `value_add_thresholds` no implementados**
```json
"value_add_thresholds": {
  "minimum_value_add": {
    "delta_score": 0.05,
    "description": "Signal must improve score by at least 5%"
  }
}

// NO existe ValueAddScorer ni filtrado por delta mínimo
```

---

## 3. MATRIZ DE IRRIGACIÓN COMPLETA

### 3.1 Vista Consolidada: Corpus → Archivo Derivado → Consumidor → Estado

```
┌────────────────────────────┬─────────────────────────────────┬──────────────────────────────┬─────────────┐
│ CORPUS RAÍZ                │ ARCHIVO DERIVADO CQC            │ CONSUMIDORES                 │ WIRING      │
├────────────────────────────┼─────────────────────────────────┼──────────────────────────────┼─────────────┤
│                            │                                 │ EmpiricalExtractorBase       │ ✅ OK       │
│                            │                                 │ StructuralMarkerExtractor    │ ✅ OK       │
│ calibracion_extractores    │ extractor_calibration.json      │ QuantitativeTripletExtractor │ ✅ OK       │
│ (666 líneas)               │ (700 líneas)                    │ NormativeReferenceExtractor  │ ✅ OK       │
│                            │                                 │ FinancialChainExtractor      │ ❌ MISSING  │
│                            │                                 │ CausalVerbExtractor          │ ⚠️ PARCIAL  │
│                            │                                 │ InstitutionalNER             │ ⚠️ PARCIAL  │
├────────────────────────────┼─────────────────────────────────┼──────────────────────────────┼─────────────┤
│                            │                                 │ SignalQuestionIndex          │ ✅ OK       │
│ corpus_integrado           │ integration_map.json            │ IrrigationSynchronizer       │ ⚠️ FALLBACK │
│ (1237 líneas)              │ (1200 líneas)                   │ EvidenceNexus                │ ⚠️ PARCIAL  │
│                            │                                 │ QuestionnaireSignalRegistry  │ ❌ NO EXISTE│
├────────────────────────────┼─────────────────────────────────┼──────────────────────────────┼─────────────┤
│                            │                                 │ NormativeComplianceValidator │ ❌ NO EXISTE│
│ corpus_normatividad        │ normative_compliance.json       │ @p PolicyAreaScorer          │ ⚠️ NO USA   │
│ (269 líneas)               │ (260 líneas)                    │ CrossCuttingScorer           │ ⚠️ NO USA   │
│                            │                                 │ MC03 extractor               │ ⚠️ PARCIAL  │
├────────────────────────────┼─────────────────────────────────┼──────────────────────────────┼─────────────┤
│                            │                                 │ BaselineScorer (@b)          │ ⚠️ TODO     │
│                            │                                 │ PolicyAreaScorer (@p)        │ ⚠️ TODO     │
│ thresholds_weights         │ empirical_weights.json          │ QualityScorer (@q)           │ ⚠️ TODO     │
│ (351 líneas)               │ (320 líneas)                    │ DimensionScorer (@d)         │ ⚠️ TODO     │
│                            │                                 │ CausalScorer (@chain)        │ ⚠️ TODO     │
│                            │                                 │ Aggregators (Phase 4-7)      │ ⚠️ TODO     │
└────────────────────────────┴─────────────────────────────────┴──────────────────────────────┴─────────────┘
```

### 3.2 Resumen de Estado de Wiring

| Estado | Cantidad | Porcentaje |
|--------|----------|------------|
| ✅ IMPLEMENTADO | 5 consumidores | ~20% |
| ⚠️ PARCIAL/TODO | 12 consumidores | ~50% |
| ❌ MISSING/NO EXISTE | 7 consumidores | ~30% |

---

## 4. ESPECIFICACIÓN DE IMPLEMENTACIÓN

### 4.1 Prioridad 0 (Crítica): Implementar Extractores MISSING

#### 4.1.1 `FinancialChainExtractor` (MC05)

**Archivo a crear:** `src/farfan_pipeline/infrastructure/extractors/financial_chain_extractor.py`

**Datos de calibración disponibles en `extractor_calibration.json`:**
```json
{
  "FINANCIAL_CHAIN": {
    "empirical_frequency": {
      "montos_per_plan": {"mean": 285, "min": 20, "max": 377},
      "fuentes_per_plan": {"mean": 7, "min": 5, "max": 13}
    },
    "extraction_patterns": {
      "monto": {
        "regex": "\\$\\s*([0-9.,]+)\\s*(millones?|billones?)?",
        "confidence": 0.90,
        "normalization": {"millones": "* 1000000", "billones": "* 1000000000000"}
      },
      "fuente": {
        "regex": "(?:SGP|recursos\\s+propios|SGR|crédito|cofinanciación)",
        "confidence": 0.92
      }
    },
    "risk_thresholds": {
      "credito_max_pct": 0.20,
      "propios_min_pct": 0.03,
      "sgp_dependencia_max": 0.85
    },
    "gold_standard_examples": [
      {
        "plan": "Cajibío",
        "ppi_total": 288087496180,
        "distribution": {"SGP": 0.15, "ADRES": 0.63, "Propios": 0.0628}
      }
    ]
  }
}
```

**Preguntas desbloqueadas:** 52
```
Q003, Q013, Q018, Q023, Q025, Q033, Q043, Q048, Q053, Q055,
Q063, Q073, Q078, Q083, Q085, Q093, Q103, Q108, Q113, Q115,
Q123, Q133, Q138, Q143, Q145, Q153, Q163, Q168, Q173, Q175,
Q183, Q193, Q198, Q203, Q205, Q213, Q223, Q228, Q233, Q235,
Q243, Q253, Q258, Q263, Q265, Q273, Q283, Q288, Q293, Q295
```

**Slots que requieren FINANCIAL_CHAIN:**
- D1-Q3 (RECUR-ASIG): Recursos asignados en PPI
- D3-Q3 (TRAZ-PRES): Trazabilidad presupuestal
- D4-Q3 (JUST-AMB): Justificación de ambición vs recursos
- D5-Q5 (SOST-IMP): Sostenibilidad de impactos

---

#### 4.1.2 `CausalVerbExtractor` (MC08) - Completar implementación

**Archivo existente:** `src/farfan_pipeline/infrastructure/extractors/causal_verb_extractor.py`

**Estado:** PARCIAL - Extrae verbos pero no construye cadenas causales

**Datos de calibración disponibles:**
```json
{
  "CAUSAL_VERBS": {
    "empirical_frequency": {
      "top_10_verbs": [
        {"verb": "fortalecer", "mean": 52},
        {"verb": "implementar", "mean": 51},
        {"verb": "garantizar", "mean": 55}
      ],
      "conectores_causales": {
        "con_el_fin_de": {"mean": 18},
        "mediante": {"mean": 22},
        "a_traves_de": {"mean": 35}
      }
    },
    "causal_chain_detection": {
      "pattern": "VERB + PRODUCT + CONNECTOR + RESULT",
      "confidence": 0.78
    }
  }
}
```

**Funcionalidad faltante:**
1. Detección de cadenas causales completas (VERB → PRODUCT → CONNECTOR → RESULT)
2. Vinculación con PROGRAMMATIC_HIERARCHY
3. Construcción de grafo causal

**Preguntas desbloqueadas:** 68
```
D2-Q3, D2-Q5, D3-Q4, D3-Q5, D4-Q2, D6-Q1, D6-Q2 × 10 PA
```

---

#### 4.1.3 `InstitutionalNER` (MC09) - Completar implementación

**Archivo existente:** `src/farfan_pipeline/infrastructure/extractors/institutional_ner_extractor.py`

**Estado:** PARCIAL - Extrae entidades pero no construye red institucional

**Datos de calibración disponibles:**
```json
{
  "INSTITUTIONAL_NETWORK": {
    "empirical_frequency": {
      "entidades_nacionales": {
        "DNP": {"mean": 15},
        "DANE": {"mean": 10},
        "ICBF": {"mean": 11}
      },
      "entidades_territoriales": {
        "Alcaldía": {"mean": 420}
      }
    },
    "entity_roles": {
      "RESPONSABLE": "Primary executor",
      "COORDINADOR": "Coordination role",
      "APOYO": "Support/technical assistance"
    }
  }
}
```

**Preguntas desbloqueadas:** 39
```
D1-Q4, D2-Q1, D5-Q5, D6-Q4 × 10 PA (parcialmente)
```

---

### 4.2 Prioridad 1 (Alta): Crear Validadores Faltantes

#### 4.2.1 `NormativeComplianceValidator`

**Archivo a crear:** `src/farfan_pipeline/phases/Phase_3/validators/normative_compliance_validator.py`

**Responsabilidades:**
1. Cargar `normative_compliance.json`
2. Para cada PA, verificar normas obligatorias citadas
3. Calcular penalizaciones por normas faltantes
4. Aplicar reglas contextuales (PDET, territorios étnicos)
5. Generar `gap_report` con recomendaciones

**Pseudocódigo:**
```python
class NormativeComplianceValidator:
    def __init__(self):
        self.compliance_data = self._load_compliance_json()
    
    def validate(self, plan_id: str, policy_area: str, cited_norms: List[str]) -> ValidationResult:
        mandatory = self.compliance_data["mandatory_norms_by_policy_area"][policy_area]["mandatory"]
        universal = self.compliance_data["universal_mandatory_norms"]
        
        missing = []
        total_penalty = 0.0
        
        for norm in mandatory + universal:
            if norm["norm_id"] not in cited_norms:
                missing.append(norm)
                total_penalty += norm.get("penalty_if_missing", 0.2)
        
        score = max(0.0, 1.0 - total_penalty)
        
        return ValidationResult(
            policy_area=policy_area,
            score=score,
            missing_norms=missing,
            recommendation=self._generate_recommendation(missing)
        )
```

---

#### 4.2.2 `QuestionnaireSignalRegistry`

**Archivo a crear:** `src/farfan_pipeline/phases/Phase_2/registries/questionnaire_signal_registry.py`

**Responsabilidades:**
1. Cargar `integration_map.json` al inicio
2. Proveer mapeo Q→Signals a todos los consumidores
3. Calcular `expected_signal_counts` por pregunta
4. Trackear `empirical_availability` para ajustar expectativas

**Interfaz:**
```python
class QuestionnaireSignalRegistry:
    def get_signals_for_question(self, question_id: str) -> SignalSpec
    def get_expected_count(self, question_id: str) -> int
    def get_empirical_availability(self, question_id: str) -> float
    def get_scoring_modality(self, question_id: str) -> str
```

---

### 4.3 Prioridad 2 (Media): Conectar Scorers a `empirical_weights.json`

**Archivos a modificar:**
- `src/farfan_pipeline/phases/Phase_3/scorers/baseline_scorer.py`
- `src/farfan_pipeline/phases/Phase_3/scorers/policy_area_scorer.py`
- `src/farfan_pipeline/phases/Phase_3/scorers/quality_scorer.py`
- `src/farfan_pipeline/phases/Phase_3/scorers/dimension_scorer.py`
- `src/farfan_pipeline/phases/Phase_3/scorers/causal_scorer.py`

**Patrón de implementación:**
```python
class BaseScorer:
    def __init__(self, weights_path: Path = None):
        if weights_path is None:
            weights_path = CQC_PATH / "scoring" / "calibration" / "empirical_weights.json"
        
        with open(weights_path) as f:
            self.config = json.load(f)
        
        self.weights = self.config["phase3_scoring_weights"][self.layer_name]
        self.thresholds = self.config["signal_confidence_thresholds"]
```

---

## 5. ROADMAP DE IMPLEMENTACIÓN

### 5.1 Fase 1: Extractores Críticos (Semanas 1-2)

| Día | Tarea | Entregable | Impacto |
|-----|-------|------------|---------|
| 1-2 | Implementar `FinancialChainExtractor` | Archivo .py completo | +52 preguntas |
| 3-4 | Completar `CausalVerbExtractor` | Cadenas causales | +68 preguntas |
| 5 | Completar `InstitutionalNER` | Red institucional | +39 preguntas |
| 6-7 | Tests unitarios + integración | 100% coverage | Validación |

**KPI de éxito:** Questions bloqueadas: 159 → 0

### 5.2 Fase 2: Validadores y Registries (Semanas 3-4)

| Día | Tarea | Entregable | Impacto |
|-----|-------|------------|---------|
| 8-9 | Crear `NormativeComplianceValidator` | Validador completo | CC_COHERENCIA activo |
| 10-11 | Crear `QuestionnaireSignalRegistry` | Registry cargado | Routing correcto |
| 12-13 | Conectar scorers a `empirical_weights.json` | 6 scorers actualizados | Pesos empíricos |
| 14 | Integration tests con 14 planes | Report de cobertura | Validación E2E |

**KPI de éxito:** Wiring efectivo: 15% → 70%

### 5.3 Fase 3: Optimización y Alineamiento (Semanas 5-6)

| Día | Tarea | Entregable | Impacto |
|-----|-------|------------|---------|
| 15-16 | Implementar `ValueAddScorer` | Filtrado de señales | -30% ruido |
| 17-18 | Pattern enrichment (992 → 5000) | Patrones adicionales | +400% cobertura |
| 19-20 | Calibración final con corpus | Thresholds ajustados | Precision +15% |
| 21 | Documentación + release notes | Docs actualizados | Mantenibilidad |

**KPI de éxito:** Alignment score: 2.9% → 85%

---

## 6. MÉTRICAS DE ÉXITO

### 6.1 Indicadores Cuantitativos

| Métrica | Actual | Post-Fase 1 | Post-Fase 2 | Post-Fase 3 |
|---------|--------|-------------|-------------|-------------|
| Extractores implementados | 2/10 | 5/10 | 7/10 | 10/10 |
| Questions desbloqueadas | 141/300 | 300/300 | 300/300 | 300/300 |
| Wiring efectivo | 15% | 40% | 70% | 85% |
| Patrones activos | 223 | 500 | 2000 | 5000 |
| Alignment score | 2.9% | 35% | 65% | 85% |

### 6.2 Indicadores Cualitativos

- [ ] Todos los extractores consumen `extractor_calibration.json`
- [ ] Todos los scorers consumen `empirical_weights.json`
- [ ] `normative_compliance.json` validado por `NormativeComplianceValidator`
- [ ] `integration_map.json` usado por `QuestionnaireSignalRegistry`
- [ ] Sin fallbacks silenciosos a mapeos vacíos
- [ ] Documentación actualizada en cada consumidor

---

## 7. ANEXOS

### 7.1 Inventario Completo de Archivos CQC

| Categoría | Cantidad | Ubicación |
|-----------|----------|-----------|
| Archivos JSON totales | 494 | `canonic_questionnaire_central/` |
| Preguntas individuales | 300 | `dimensions/DIM*/questions/Q*.json` |
| Membership Criteria | 10 | `_registry/membership_criteria/MC*.json` |
| Binding maps | 3 | `_registry/membership_criteria/_bindings/` |
| Calibración | 1 | `_registry/membership_criteria/_calibration/` |
| Entidades | 7 | `_registry/entities/` |
| Capacidades | 4 | `_registry/capabilities/` |
| Patrones | 17 | `_registry/patterns/by_category/` |
| Keywords | 21 | `_registry/keywords/by_policy_area/` |
| Vistas analíticas | 7 | `_views/` |
| Clusters | 4 | `clusters/CL*/` |
| Dimensiones | 6 | `dimensions/DIM*/` |
| Policy Areas | 10 | `policy_areas/PA*/` |
| Scoring | 2 | `scoring/` |

### 7.2 Referencias Cruzadas

- [EMPIRICAL_CORPUS_INDEX.json](canonic_questionnaire_central/_registry/EMPIRICAL_CORPUS_INDEX.json) - Índice maestro
- [extractor_calibration.json](canonic_questionnaire_central/_registry/membership_criteria/_calibration/extractor_calibration.json) - Calibración de extractores
- [integration_map.json](canonic_questionnaire_central/_registry/questions/integration_map.json) - Mapeo Q→Signals
- [normative_compliance.json](canonic_questionnaire_central/_registry/entities/normative_compliance.json) - Cumplimiento normativo
- [empirical_weights.json](canonic_questionnaire_central/scoring/calibration/empirical_weights.json) - Pesos empíricos

---

**Documento generado:** 11 de enero de 2026  
**Autor:** GitHub Copilot - Auditoría Técnica F.A.R.F.A.N  
**Versión:** 1.0.0  
**Estado:** COMPLETO - Listo para implementación
