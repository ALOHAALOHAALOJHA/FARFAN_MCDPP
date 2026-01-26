# SISAS: Satellital Irrigation and Signals for Advanced Smart-data

## Complete Pipeline Architecture Reference

**Version**: 3.0.0 (SOTA Frontier)
**Status**: INDUSTRIAL VALIDATED
**Last Updated**: 2026-01-25
**Canonical Phase Alignment**: Orchestrator 11-Phase Model

---

## 1. Executive Summary

SISAS is a **crosscutting signal irrigation layer** that permeates the entire F.A.R.F.A.N pipeline. It provides:

- **Dynamic Configuration**: Signal-driven overrides for hardcoded parameters
- **Provenance Tracking**: Every result carries its signal source for auditability
- **Failure Contracts**: Signal-driven abort conditions at critical junctures
- **Registry Architecture**: Centralized signal management with per-policy-area granularity

**SOTA FRONTIER ENHANCEMENTS (v3.0.0)**:
- **Type Safety**: StrEnum for signal types, TypedDict for structured serialization
- **Memory Efficiency**: slots=True in dataclasses (30-40% memory reduction)
- **Pattern Matching**: Python 3.10+ match statements for signal categorization
- **Context Managers**: @contextmanager for audit trail management
- **Factory Functions**: Type-safe factory functions for signal creation
- **Modern Type Hints**: TypeAlias, Final, Self, override, ClassVar, Never

---

## 2. Canonical Pipeline Phases (Orchestrator Model)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                        F.A.R.F.A.N ORCHESTRATOR: 11 CANONICAL PHASES                        │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 0: VALIDACIÓN DE CONFIGURACIÓN                                          [sync] │   │
│  │ Method: _load_configuration                                                          │   │
│  │ SISAS: create_signal_registry() → QuestionnaireSignalRegistry                       │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                                  │
│                                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 1: INGESTIÓN DE DOCUMENTO                                                [sync] │   │
│  │ Method: _ingest_document                                                             │   │
│  │ SISAS: signal_pack.segmentation_rules → ChunkingStrategy                            │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                                  │
│                                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 2: MICRO PREGUNTAS                                                      [async] │   │
│  │ Method: _execute_micro_questions_async                                               │   │
│  │ ┌───────────────────────────────────────────────────────────────────────────────┐   │   │
│  │ │ SUBPHASE 2.1: Question Context Building                                       │   │   │
│  │ │ └── signal_registry.get(policy_area_id) → signal_pack                        │   │   │
│  │ ├───────────────────────────────────────────────────────────────────────────────┤   │   │
│  │ │ SUBPHASE 2.2: Pattern Extraction & Expansion                                  │   │   │
│  │ │ └── enriched_pack.get_patterns_for_context() → applicable_patterns           │   │   │
│  │ ├───────────────────────────────────────────────────────────────────────────────┤   │   │
│  │ │ SUBPHASE 2.3: Method Execution                                                │   │   │
│  │ │ └── common_kwargs["signal_pack"] = signal_pack                               │   │   │
│  │ ├───────────────────────────────────────────────────────────────────────────────┤   │   │
│  │ │ SUBPHASE 2.4: Evidence Assembly                                               │   │   │
│  │ │ └── EvidenceAssembler.assemble(signal_pack=signal_pack)                      │   │   │
│  │ │     └── trace["signal_provenance"] = {pack_id, policy_area, source_hash}     │   │   │
│  │ ├───────────────────────────────────────────────────────────────────────────────┤   │   │
│  │ │ SUBPHASE 2.5: Evidence Validation                                             │   │   │
│  │ │ └── EvidenceValidator.validate(failure_contract=failure_contract)            │   │   │
│  │ │     └── abort_conditions from signal_pack.failure_rules                      │   │   │
│  │ └───────────────────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                                  │
│                                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 3: SCORING MICRO                                                        [async] │   │
│  │ Method: _score_micro_results_async                                                   │   │
│  │ SISAS: MicroQuestionScorer(signal_registry=registry)                                │   │
│  │        └── result.signal_modality_source = "sisas" | "legacy"                       │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                                  │
│                                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 4: AGREGACIÓN DIMENSIONES                                               [async] │   │
│  │ Method: _aggregate_dimensions_async                                                  │   │
│  │ SISAS: DimensionAggregator(signal_registry=registry)                                │   │
│  │        └── AggregationSettings.from_monolith_or_registry(registry=registry)         │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                                  │
│                                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 5: AGREGACIÓN ÁREAS                                                     [async] │   │
│  │ Method: _aggregate_policy_areas_async                                                │   │
│  │ SISAS: AggregationSettings.sisas_source tracking                                    │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                                  │
│                                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 6: AGREGACIÓN CLÚSTERES                                                  [sync] │   │
│  │ Method: _aggregate_clusters                                                          │   │
│  │ SISAS: cluster_weights from AssemblySignalPack                                      │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                                  │
│                                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 7: EVALUACIÓN MACRO                                                      [sync] │   │
│  │ Method: _evaluate_macro                                                              │   │
│  │ SISAS: macro_cluster_weights from AssemblySignalPack                                │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                                  │
│                                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 8: RECOMENDACIONES                                                      [async] │   │
│  │ Method: _generate_recommendations                                                    │   │
│  │ SISAS: recommendation_signals (future integration point)                            │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                                  │
│                                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 9: ENSAMBLADO DE REPORTE                                                 [sync] │   │
│  │ Method: _assemble_report                                                             │   │
│  │ SISAS: Provenance aggregation from all phases                                       │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                                  │
│                                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ FASE 10: FORMATEO Y EXPORTACIÓN                                              [async] │   │
│  │ Method: _format_and_export                                                           │   │
│  │ SISAS: Export format signals, provenance manifest                                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. SISAS Integration Points by Canonical Phase

### 3.1 FASE 0: Validación de Configuración

| Component | Signal Operation | Input | Output |
|-----------|------------------|-------|--------|
| `create_signal_registry()` | Registry instantiation | `questionnaire_monolith.json` | `QuestionnaireSignalRegistry` |
| Per-policy extraction | Pack creation | `monolith["blocks"]["policy_areas"]` | `Dict[str, SignalPack]` |
| Scoring signals | Signal extraction | `monolith["blocks"]["scoring"]` | `Dict[str, ScoringSignalPack]` |
| Assembly signals | Weight extraction | `monolith["blocks"]["aggregation"]` | `Dict[str, AssemblySignalPack]` |

**Code Location**: `core/orchestrator/factory.py` → `create_signal_registry()`

---

### 3.2 FASE 1: Ingestión de Documento

| Component | Signal Operation | Input | Output |
|-----------|------------------|-------|--------|
| `ChunkingStrategy` | Segmentation config | `signal_pack.segmentation_rules` | `SegmentationInfo` |
| `DocumentProcessor` | Metadata extraction | `signal_pack.metadata_schema` | `Document.metadata` |

**Signal Pack Fields Consumed**:
```
signal_pack.segmentation_rules = {
    "method": SegmentationMethod,    # REGEX|SENTENCE|PARAGRAPH|SEMANTIC
    "min_chunk_size": int,
    "max_chunk_size": int,
    "overlap": int,
    "separator_patterns": List[str]
}
```

---

### 3.3 FASE 2: Micro Preguntas (5 Subphases)

This is the **most signal-intensive phase** with 5 distinct subphases:

#### SUBPHASE 2.1: Question Context Building
| Input | Operation | Signal Consumed | Output |
|-------|-----------|-----------------|--------|
| `policy_area_id` | Registry lookup | `signal_registry.get()` | `signal_pack` |
| `policy_area_id` | Enriched lookup | `enriched_packs[policy_area_id]` | `enriched_pack` |

**Code Location**: `base_executor_with_contract.py` L327-335

#### SUBPHASE 2.2: Pattern Extraction
| Input | Operation | Signal Consumed | Output |
|-------|-----------|-----------------|--------|
| `enriched_pack` | Context filtering | `document_context` | `applicable_patterns` |
| `applicable_patterns` | Semantic expansion | `expansion_config` | `expanded_patterns` |

**Code Location**: `base_executor_with_contract.py` L348-358

#### SUBPHASE 2.3: Method Execution
| Input | Operation | Signal Consumed | Output |
|-------|-----------|-----------------|--------|
| `common_kwargs` | Signal injection | `signal_pack`, `enriched_pack` | Method inputs |

**Injected Fields**:
```python
common_kwargs = {
    "signal_pack": signal_pack,
    "enriched_pack": enriched_pack,
    "document_context": document_context,
    "question_patterns": applicable_patterns,
    ...
}
```

**Code Location**: `base_executor_with_contract.py` L364-379

#### SUBPHASE 2.4: Evidence Assembly
| Input | Operation | Signal Consumed | Output |
|-------|-----------|-----------------|--------|
| `method_outputs` | Assembly | `signal_pack` | `assembled` |
| `signal_pack` | Provenance | `pack_id, source_hash` | `trace["signal_provenance"]` |

**Code Locations**:
- L419: `EvidenceAssembler.assemble(method_outputs, assembly_rules, signal_pack=signal_pack)`
- L711: `EvidenceAssembler.assemble(method_outputs, assembly_rules, signal_pack=signal_pack)`

**Output Schema**:
```python
assembled = {
    "evidence": {...},
    "trace": {
        "signal_provenance": {
            "pack_id": "PACK_PA01_v2.1",
            "policy_area": "PA01",
            "version": "2.1",
            "source_hash": "abc123def456"
        }
    }
}
```

#### SUBPHASE 2.5: Evidence Validation
| Input | Operation | Signal Consumed | Output |
|-------|-----------|-----------------|--------|
| `evidence` | Validation | `failure_contract` | `validation_result` |
| `failure_contract` | Abort check | `signal_pack.failure_rules` | `abort_triggered` |

**Code Locations**:
- L460: `EvidenceValidator.validate(evidence, validation_rules_object, failure_contract=failure_contract)`
- L720: `EvidenceValidator.validate(evidence, validation_rules_object, failure_contract=failure_contract)`

**Failure Contract Schema**:
```python
failure_contract = {
    "abort_if": ["missing_required_element", "confidence_below_threshold"],
    "severity_levels": {"missing_required_element": "CRITICAL"},
    "fallback_behavior": "score_zero" | "propagate" | "abort"
}
```

---

### 3.4 FASE 3: Scoring Micro

| Component | Signal Operation | Input | Output |
|-----------|------------------|-------|--------|
| `score_question()` | Registry injection | `signal_registry` | `ScoredResult` |
| `MicroQuestionScorer` | Modality lookup | `registry.get_scoring_signals()` | `ScoringSignalPack` |
| Result fields | Source tracking | `source_hash` | `signal_modality_source` |

**Code Location**: `analysis/scoring.py` L794-833

```python
def score_question(
    question_id: str,
    question_global: int,
    modality_str: str,
    evidence_dict: dict,
    signal_registry: "QuestionnaireSignalRegistry | None" = None,  # SISAS
) -> ScoredResult:
    scorer = MicroQuestionScorer(signal_registry=signal_registry)
    result = scorer.apply_scoring_modality(...)
    return result
```

**ScoredResult SISAS Fields**:
```python
ScoredResult = {
    "raw_score": float,
    "adjusted_score": float,
    "quality_level": QualityLevel,
    "signal_source_hash": str | None,          # SISAS provenance
    "signal_modality_source": "sisas" | "legacy"  # Source tracking
}
```

---

### 3.5 FASE 4-6: Aggregation Phases

| FASE | Component | Signal Operation | Output Field |
|------|-----------|------------------|--------------|
| 4 | `DimensionAggregator` | `from_monolith_or_registry()` | `sisas_source` |
| 5 | Policy aggregation | Weight lookup | `source_hash` |
| 6 | Cluster aggregation | `cluster_weights` | Cluster scores |

**Code Location**: `processing/aggregation.py` L659-700

```python
class DimensionAggregator:
    def __init__(
        self,
        monolith: dict | None = None,
        signal_registry: "QuestionnaireSignalRegistry | None" = None,
        ...
    ):
        # SISAS auto-detection with fallback
        if aggregation_settings is not None:
            self.aggregation_settings = aggregation_settings
        elif signal_registry is not None or monolith is not None:
            self.aggregation_settings = AggregationSettings.from_monolith_or_registry(
                monolith=monolith,
                registry=signal_registry,
                level="MACRO_1"
            )
        else:
            self.aggregation_settings = AggregationSettings.from_monolith(None)
```

**AggregationSettings SISAS Fields**:
```python
AggregationSettings = {
    "dimension_question_weights": Dict,
    "policy_area_dimension_weights": Dict,
    "source_hash": str | None,
    "sisas_source": "signal_registry" | "legacy_monolith" | "legacy_fallback"
}
```

---

## 4. Complete Signal Circulation Matrix

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              SISAS SIGNAL CIRCULATION MATRIX                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                   │
│  SIGNAL SOURCE              TRANSFORMATION                    CONSUMER                           │
│  ═══════════════════════════════════════════════════════════════════════════════════════════════  │
│                                                                                                   │
│  questionnaire_monolith.json                                                                      │
│       │                                                                                           │
│       ├──[FASE 0]──► create_signal_registry() ──► QuestionnaireSignalRegistry                    │
│       │                                                │                                          │
│       │                                                ├──► _packs: Dict[policy_area, SignalPack] │
│       │                                                ├──► _scoring_signals: Dict[q_id, Pack]    │
│       │                                                └──► _assembly_signals: Dict[level, Pack]  │
│       │                                                                                           │
│  ═══════════════════════════════════════════════════════════════════════════════════════════════  │
│                                                                                                   │
│  SignalRegistry                                                                                   │
│       │                                                                                           │
│       ├──[FASE 1]──► segmentation_rules ──► ChunkingStrategy ──► Document chunks                 │
│       │                                                                                           │
│       ├──[FASE 2.1]──► get(policy_area_id) ──► signal_pack                                       │
│       │                                            │                                              │
│       ├──[FASE 2.3]──────────────────────────────► common_kwargs["signal_pack"]                  │
│       │                                            │                                              │
│       ├──[FASE 2.4]──────────────────────────────► EvidenceAssembler.assemble(signal_pack)       │
│       │                                            │                                              │
│       │                                            └──► trace["signal_provenance"]               │
│       │                                                    │                                      │
│       │                                                    ├── pack_id                            │
│       │                                                    ├── policy_area                        │
│       │                                                    ├── version                            │
│       │                                                    └── source_hash                        │
│       │                                                                                           │
│       ├──[FASE 2.5]──► failure_rules ──► failure_contract ──► EvidenceValidator.validate()       │
│       │                                                         │                                 │
│       │                                                         └──► abort_triggered             │
│       │                                                                                           │
│       ├──[FASE 3]──► get_scoring_signals() ──► MicroQuestionScorer                               │
│       │                                            │                                              │
│       │                                            └──► ScoredResult                             │
│       │                                                    │                                      │
│       │                                                    ├── signal_source_hash                │
│       │                                                    └── signal_modality_source            │
│       │                                                                                           │
│       ├──[FASE 4]──► get_assembly_signals("MACRO_1") ──► DimensionAggregator                     │
│       │                                                      │                                    │
│       │                                                      └──► AggregationSettings            │
│       │                                                              │                            │
│       │                                                              ├── sisas_source            │
│       │                                                              └── source_hash             │
│       │                                                                                           │
│       ├──[FASE 5-6]──► policy_area_weights, cluster_weights                                      │
│       │                                                                                           │
│       ├──[FASE 7]──► macro_cluster_weights                                                       │
│       │                                                                                           │
│       └──[FASE 9-10]──► provenance aggregation ──► Report.signal_manifest                        │
│                                                                                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Signal Pack Data Structures

### 5.1 QuestionnaireSignalRegistry

```
QuestionnaireSignalRegistry
├── _packs: Dict[str, SignalPack]
│   └── key: policy_area_id (e.g., "PA01", "PA02")
├── _scoring_signals: Dict[str, ScoringSignalPack]
│   └── key: question_id
├── _assembly_signals: Dict[str, AssemblySignalPack]
│   └── key: level (e.g., "MESO_1", "MACRO_1")
│
└── Methods:
    ├── get(policy_area_id) → SignalPack | None
    ├── get_scoring_signals(question_id) → ScoringSignalPack | None
    ├── get_assembly_signals(level) → AssemblySignalPack | None
    ├── keys() → List[str]
    └── __contains__(policy_area_id) → bool
```

### 5.2 SignalPack (Per Policy Area)

```
SignalPack
├── Identification
│   ├── pack_id: str              # "PACK_PA01_v2.1"
│   ├── policy_area: str          # "PA01"
│   ├── policy_area_id: str       # Alias
│   ├── version: str              # "2.1"
│   └── source_hash: str          # "abc123..."
│
├── Pattern Configuration
│   ├── patterns: List[str]       # Regex patterns
│   └── expected_elements: List[str]
│
├── Segmentation Rules
│   └── segmentation_rules: Dict
│       ├── method: SegmentationMethod
│       ├── min_chunk_size: int
│       ├── max_chunk_size: int
│       └── overlap: int
│
└── Failure Handling
    └── failure_rules: Dict
        ├── abort_if: List[str]
        ├── severity_levels: Dict[str, str]
        └── fallback_behavior: str
```

### 5.3 ScoringSignalPack

```
ScoringSignalPack
├── question_id: str
├── modality: ScoringModality     # TYPE_A..TYPE_F
├── modality_config: Dict
│   ├── threshold: float
│   ├── weight_elements: float
│   ├── weight_similarity: float
│   └── weight_patterns: float
└── source_hash: str
```

### 5.4 AssemblySignalPack

```
AssemblySignalPack
├── level: str                    # MESO_1, MESO_2, MACRO_1
├── dimension_weights: Dict[str, Dict[str, float]]
├── policy_area_weights: Dict[str, Dict[str, float]]
├── cluster_weights: Dict[str, Dict[str, float]]
└── source_hash: str
```

---

## 6. Code Integration Points Reference

| Canonical FASE | File | Line(s) | Signal Parameter |
|----------------|------|---------|------------------|
| 0 | `core/orchestrator/factory.py` | TBD | `create_signal_registry()` |
| 1 | `core/phases/ingestion.py` | TBD | `segmentation_rules` |
| 2.1 | `base_executor_with_contract.py` | 327-335 | `signal_registry.get()` |
| 2.2 | `base_executor_with_contract.py` | 348-358 | `enriched_pack.get_patterns_for_context()` |
| 2.3 | `base_executor_with_contract.py` | 364-379 | `common_kwargs["signal_pack"]` |
| 2.4 | `base_executor_with_contract.py` | 419, 711 | `signal_pack` → EvidenceAssembler |
| 2.5 | `base_executor_with_contract.py` | 460, 720 | `failure_contract` → EvidenceValidator |
| 3 | `analysis/scoring.py` | 794-833 | `signal_registry` → score_question() |
| 4 | `processing/aggregation.py` | 659-700 | `signal_registry` → DimensionAggregator |
| 5-6 | `processing/aggregation.py` | Various | `AggregationSettings.sisas_source` |

---

## 7. Backward Compatibility Guarantees

All SISAS parameters default to `None`, ensuring zero-impact migration:

| Parameter | Default | Behavior When None |
|-----------|---------|-------------------|
| `signal_registry` | `None` | Falls back to monolith extraction |
| `signal_pack` | `None` | No provenance tracking added |
| `failure_contract` | `None` | Standard validation (no signal abort) |
| `enriched_pack` | `None` | Uses base signal_pack patterns |

**Transition Method** (`AggregationSettings.from_monolith_or_registry`):
- If `registry` provided → Uses SISAS path (preferred)
- If only `monolith` provided → Uses legacy path
- If neither → Raises `ValueError`

---

## 8. Verification Status

```
================================================================================
✅ INDUSTRIAL VALIDATION: APPROVED (2025-12-07)
================================================================================

Test Suite: test_sisas_industrial.py
Total Tests: 36
Critical Passed: 31/31
Non-Critical Passed: 5/5
Failures: 0

Verified Integration Points:
✓ FASE 0: Signal registry creation
✓ FASE 2.1-2.3: Signal pack propagation through executor
✓ FASE 2.4: Evidence Assembly with provenance tracking
✓ FASE 2.5: Evidence Validation with failure contracts
✓ FASE 3: Scoring with signal registry injection
✓ FASE 4-6: Aggregation with transition method
✓ Real monolith integration
✓ Edge cases and fallback behavior
```

---

## 9. Related Files

| Component | File Path |
|-----------|-----------|
| Signal Registry | `core/orchestrator/signal_registry.py` |
| Signal Loader | `core/orchestrator/signal_loader.py` |
| Base Executor | `core/orchestrator/base_executor_with_contract.py` |
| Evidence Assembler | `core/orchestrator/evidence_assembler.py` |
| Evidence Validator | `core/orchestrator/evidence_validator.py` |
| Scoring | `analysis/scoring.py` |
| Aggregation | `processing/aggregation.py` |
| Industrial Tests | `test_sisas_industrial.py` |
