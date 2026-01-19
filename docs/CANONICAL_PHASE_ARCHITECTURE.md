# Canonical Phase Architecture: F.A.R.F.A.N. Policy Pipeline 0-9

> **Document Control**
>
> | Attribute | Value |
> |-----------|-------|
> | **Document Identifier** | `ARCH-CANONICAL-001` |
> | **Status** | `ACTIVE` |
> | **Version** | `1.0.0` |
> | **Last Updated** | 2026-01-17 |
> | **Pipeline Position** | System-Wide Specification |

---

## Executive Summary

This document specifies the **canonical architecture** for the F.A.R.F.A.N. (Framework for Applied Risk and Fact Assessment Network) Policy Pipeline, a **governed, socio-technical system** for policy evaluation. The pipeline comprises **10 phases (0-9)** organized as a **modular, layered, stateful, and inspectable** system with explicit interfaces, control surfaces, and feedback mechanisms.

### Architectural Posture

- **Layered**: Strategic → Analytical → Decision → Operational → Evaluative
- **Modular**: Each phase is a separable unit with explicit contracts
- **Stateful**: Phases transition policy artifacts between defined states
- **Governed**: Decision rights, veto points, and escalation paths are explicit
- **Inspectable**: Every phase produces audit-worthy artifacts

### Core Architectural Components

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        F.A.R.F.A.N. CANONICAL ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────────────────┐  │
│  │  Phase 0        │    │  Phase 1-3      │    │  Phase 4-7                │  │
│  │  BOOTSTRAP      │───▶│  INGESTION      │───▶│  AGGREGATION PYRAMID      │  │
│  │  7 Exit Gates   │    │  300 Contracts  │    │  300→60→10→4→1            │  │
│  └─────────────────┘    └─────────────────┘    └───────────────────────────┘  │
│           │                       │                        │                   │
│           ▼                       ▼                        ▼                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────────────────┐  │
│  │  Phase 8        │    │  Phase 9        │    │  SISAS                    │  │
│  │  RECOMMENDATION │    │  REPORTING      │    │  Signal Bus System        │  │
│  │  Engine v3.0    │    │  Templates      │    │  (Cross-Cutting)          │  │
│  └─────────────────┘    └─────────────────┘    └───────────────────────────┘  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                     ORCHESTRATION & FACTORY LAYER                       │   │
│  │  ┌──────────────────┐         ┌──────────────────────────────────┐     │   │
│  │  │ AnalysisPipeline │────────▶│  Orchestrator                     │     │   │
│  │  │ Factory          │   DI    │  - MethodExecutor (348 methods)  │     │   │
│  │  │ - Canonical Q    │         │  - SignalRegistry (v2.0)         │     │   │
│  │  │ - SeedRegistry   │         │  - ExecutorConfig                │     │   │
│  │  │ - Phase0Valid    │         │  - RuntimeConfig                 │     │   │
│  │  └──────────────────┘         └──────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Phase 0: Bootstrap](#phase-0-bootstrap)
3. [Phase 1: Document Chunking](#phase-1-document-chunking)
4. [Phase 2: Evidence Extraction](#phase-2-evidence-extraction)
5. [Phase 3: Scoring](#phase-3-scoring)
6. [Phase 4: Dimension Aggregation](#phase-4-dimension-aggregation)
7. [Phase 5: Area Aggregation](#phase-5-area-aggregation)
8. [Phase 6: Cluster Aggregation](#phase-6-cluster-aggregation)
9. [Phase 7: Macro Evaluation](#phase-7-macro-evaluation)
10. [Phase 8: Recommendation Engine](#phase-8-recommendation-engine)
11. [Phase 9: Reporting](#phase-9-reporting)
12. [Orchestration Layer](#orchestration-layer)
13. [Factory Pattern](#factory-pattern)
14. [SISAS Integration](#sisas-integration)
15. [Contracts System](#contracts-system)
16. [Cross-Cutting Concerns](#cross-cutting-concerns)
17. [Architecture Change Log](#architecture-change-log)

---

## 1. System Architecture

### 1.1 Architectural Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DECISION LAYER                                      │
│  (Policy recommendations, quality classifications, intervention priorities)   │
├─────────────────────────────────────────────────────────────────────────────┤
│                          EVALUATIVE LAYER                                    │
│  (Macro scores, coherence analysis, gap detection, alignment metrics)       │
├─────────────────────────────────────────────────────────────────────────────┤
│                          OPERATIONAL LAYER                                   │
│  (Cluster aggregation, area synthesis, dimension reduction)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                          ANALYTICAL LAYER                                    │
│  (Evidence extraction, pattern matching, scoring execution)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                          STRATEGIC LAYER                                     │
│  (Questionnaire loading, signal registry construction, method injection)    │
├─────────────────────────────────────────────────────────────────────────────┤
│                          FOUNDATION LAYER                                    │
│  (Bootstrap validation, system readiness, determinism enforcement)          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow Invariants

```
                    ┌─────────────────────────────────────┐
                    │         POLICY DOCUMENT              │
                    │         (PDF Input)                  │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │   Phase 0: Bootstrap Validation    │
                    │   [Input: PDF → Output: Validated]  │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INGESTION CORRIDOR (Phases 1-3)                      │
│                                                                             │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐             │
│   │  Phase 1     │─────▶│  Phase 2     │─────▶│  Phase 3     │             │
│   │  Chunking    │ 60  │  Evidence    │ 300 │  Scoring     │             │
│   │  (10×6=60)   │chunks│  Extraction  │scores│  (0-3 scale) │             │
│   └──────────────┘      └──────────────┘      └──────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AGGREGATION PYRAMID (Phases 4-7)                        │
│                                                                             │
│   Phase 4: 300 → 60  (Dimension Aggregation, Choquet Integral)              │
│       │                                                                     │
│       ▼                                                                     │
│   Phase 5: 60 → 10   (Area Aggregation, Weighted Mean)                      │
│       │                                                                     │
│       ▼                                                                     │
│   Phase 6: 10 → 4    (Cluster Aggregation, Adaptive Penalty)                │
│       │                                                                     │
│       ▼                                                                     │
│   Phase 7: 4 → 1     (Macro Evaluation, CCCA/SGD/SAS)                       │
│                                                                             │
│   Total Compression: 300:1                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │   Phase 8: Recommendation Engine    │
                    │   (MICRO/MESO/MACRO recommendations)│
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │   Phase 9: Report Generation        │
                    │   (Executive + Technical Deep Dive) │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │        POLICY EVALUATION REPORT     │
                    │    (HTML/PDF with recommendations)   │
                    └─────────────────────────────────────┘
```

---

## Phase 0: Bootstrap

### Phase Identifier and Name
- **ID**: `PHASE-0-BOOTSTRAP`
- **Canonical Name**: `phase_0_bootstrap`
- **Codename**: `BOOTSTRAP`

### System Function
Validates system readiness, enforces determinism, and ensures all prerequisites are met before pipeline execution. Implements **7 exit gates** that must be passed for the system to enter operational state.

### Policy State In / Policy State Out
- **Input**: `RawInput` (PDF document + questionnaire paths)
- **Output**: `Phase0ValidationResult` (validated system state)
- **State Transition**: `UNVALIDATED` → `READY`

### Primary Artifacts Produced
| Artifact | Type | Description |
|----------|------|-------------|
| Exit Gate Results | `GateResult[]` | Results from 7 validation gates |
| Runtime Config | `RuntimeConfig` | System configuration (PROD/DEV/TEST) |
| Seed Registry | `SeedRegistry` | Determinism enforcement singleton |
| SHA256 Hashes | `HashManifest` | Input integrity verification |

### Decision Rights and Accountability
- **Authority**: `AnalysisPipelineFactory`
- **Veto Points**: Each of 7 exit gates can block execution
- **Escalation**: Gate failures → `FactoryError` (strict mode) or warning (non-strict)

### Upstream Dependencies
- None (Phase 0 is the entry point)

### Downstream Obligations
- **Phase 1**: Receives validated document and configuration
- **Orchestrator**: Receives `Phase0ValidationResult` for runtime validation

### Known Failure Modes / Risk Concentrations
| Failure Mode | Trigger | Mitigation |
|--------------|---------|------------|
| Python version incompatibility | `PYTHON_VERSION < 3.10` | Fail fast in P0.2 |
| Missing dependencies | Import errors | Fail fast in P0.2 |
| Questionnaire hash mismatch | SHA256 verification | `IntegrityError` |
| Determinism violation | RNG not seeded | Fail in P0.3 |

### Instrumentation & Metrics
- Gate pass/fail rates
- Bootstrap duration
- Seed initialization status

---

## Phase 1: Document Chunking

### Phase Identifier and Name
- **ID**: `PHASE-1-DOCUMENT-CHUNKING`
- **Canonical Name**: `phase_1_document_chunking`
- **Codename**: `CHUNKER`

### System Function
Decomposes input PDF document into **60 canonical chunks** corresponding to the matrix structure of **10 Policy Areas × 6 Causal Dimensions**. Enforces the **constitutional invariant** that exactly 60 chunks must be produced.

### Policy State In / Policy State Out
- **Input**: `PreprocessedDocument` (validated PDF)
- **Output**: `ChunkedDocument` (60 chunks with metadata)
- **State Transition**: `VALIDATED` → `CHUNKED`

### Primary Artifacts Produced
| Artifact | Type | Description |
|----------|------|-------------|
| Document Chunks | `DocumentChunk[]` | 60 chunks (10 PA × 6 DIM) |
| Chunk Manifest | `ChunkManifest` | Matrix coordinates (PAxx-DIMyy) |
| Completeness Report | `CompletenessReport` | 60×60 matrix coverage validation |

### Decision Rights and Accountability
- **Authority**: `Orchestrator`
- **Veto Points**: Chunk count ≠ 60 → `ValueError`
- **Contract Enforcement**: `CP-1.1` (Matrix Coordinates), `CP-1.2` (Manifest Validation)

### Upstream Dependencies
- **Phase 0**: Validated document and system state

### Downstream Obligations
- **Phase 2**: Provides chunks for evidence extraction
- **Orchestrator**: Maintains chunk provenance chain

### Known Failure Modes / Risk Concentrations
| Failure Mode | Trigger | Mitigation |
|--------------|---------|------------|
| Chunk count violation | `len(chunks) != 60` | Constitutional invariant error |
| Missing PA/DIM | Incomplete matrix | Fail fast validation |
| Text extraction failure | PDF corruption | Graceful degradation with warning |

### Instrumentation & Metrics
- Chunk distribution by PA/DIM
- Average chunk length
- Matrix completeness score

---

## Phase 2: Evidence Extraction

### Phase Identifier and Name
- **ID**: `PHASE-2-EVIDENCE-EXTRACTION`
- **Canonical Name**: `phase_2_evidence_extraction`
- **Codename**: `EXTRACTOR`

### System Function
Extracts evidence from 60 document chunks using **30 BaseExecutor classes** with **pattern matching** against **300+ signal contracts**. Implements the **Method Dispensary Pattern** where ~20 monolith classes provide 348+ methods to executors.

### Policy State In / Policy State Out
- **Input**: `ChunkedDocument` (60 chunks)
- **Output**: `EvidenceBundle` (300 evidence items)
- **State Transition**: `CHUNKED` → `EXTRACTED`

### Primary Artifacts Produced
| Artifact | Type | Description |
|----------|------|-------------|
| Evidence Items | `EvidenceItem[]` | 300 items (30 Q × 10 PA) |
| Signal Consumption Proofs | `SignalConsumptionProof[]` | Pattern match tracking |
| Executor Results | `ExecutorResult[]` | Results from 30 executors |

### Decision Rights and Accountability
- **Authority**: `MethodExecutor` (via `AnalysisPipelineFactory`)
- **Veto Points**: Contract validation failures, executor construction errors
- **Contract Enforcement**: `CP-2.1` (Evidence Structure), `CP-2.2` (Consumption Tracking)

### Upstream Dependencies
- **Phase 1**: Chunked document
- **Factory**: `QuestionnaireSignalRegistry`, `MethodExecutor`, enriched signal packs

### Downstream Obligations
- **Phase 3**: Provides evidence for scoring
- **SISAS**: Publishes consumption signals to bus

### Known Failure Modes / Risk Concentrations
| Failure Mode | Trigger | Mitigation |
|--------------|---------|------------|
| Pattern match failure | No signal matches | Zero score with evidence |
| Executor construction | Missing methods | `ExecutorConstructionError` |
| Contract violation | Invalid evidence | Skip with warning |

### Instrumentation & Metrics
- Evidence extraction rate
- Pattern match statistics
- Executor execution duration

### Phase 2 Architecture: Method Dispensary Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    METHOD DISPENSARY PATTERN                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ANALYSIS PIPELINE FACTORY                        │   │
│  │  ┌────────────────┐      ┌──────────────────────────────────┐       │   │
│  │  │ Canonical Q    │─────▶│ QuestionnaireSignalRegistry v2.0  │       │   │
│  │  │ (Monolith)     │      │ - 300+ contracts loaded           │       │   │
│  │  └────────────────┘      └──────────────────────────────────┘       │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ MethodExecutor (348 verified methods)                       │   │   │
│  │  │                                                             │   │   │
│  │  │  MethodRegistry (canonical injection)                       │   │   │
│  │  │  ├── PDETMunicipalPlanAnalyzer (52 methods)                 │   │   │
│  │  │  ├── CausalExtractor (28 methods)                           │   │   │
│  │  │  ├── FinancialAuditor (13 methods)                          │   │   │
│  │  │  ├── BayesianMechanismInference (14 methods)                │   │   │
│  │  │  ├── TextMiningEngine (8 methods)                           │   │   │
│  │  │  └── [...] 15 more monolith classes                         │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ ExtendedArgRouter (30+ special routes)                        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │ DI                                     │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    30 BASE EXECUTOR CLASSES                         │   │
│  │  (Each receives EnrichedSignalPack + MethodExecutor)                │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │   │
│  │  │ D1-Q1           │  │ D3-Q2           │  │ D6-Q5           │       │   │
│  │  │ QuantBaseline   │  │ TargetProp      │  │ ValidationTest  │       │   │
│  │  │ (17 methods)    │  │ (24 methods)    │  │ (8 methods)     │       │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘       │   │
│  │         ...                   ...                   ...              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 3: Scoring

### Phase Identifier and Name
- **ID**: `PHASE-3-SCORING`
- **Canonical Name**: `phase_3_scoring`
- **Codename**: `SCORER`

### System Function
Converts extracted evidence into **normalized scores on a 3-point scale** (0.0 to 3.0) using the **SISAS Signal Enriched Scoring** system. Each of the 300 evidence items is scored based on evidence presence, quality, and completeness.

### Policy State In / Policy State Out
- **Input**: `EvidenceBundle` (300 evidence items)
- **Output**: `ScoreMatrix` (300 scores × metadata)
- **State Transition**: `EXTRACTED` → `SCORED`

### Primary Artifacts Produced
| Artifact | Type | Description |
|----------|------|-------------|
| Micro Scores | `MicroScore[]` | 300 scores (Q001-Q300) |
| Score Metadata | `ScoreMetadata` | Confidence, provenance, quality flags |
| Scoring Report | `ScoringReport` | Distribution statistics |

### Decision Rights and Accountability
- **Authority**: `ScoringEngine`
- **Veto Points**: Invalid score ranges (< 0 or > 3)
- **Contract Enforcement**: `CP-3.1` (Score Domain), `CP-3.2` (Metadata Completeness)

### Upstream Dependencies
- **Phase 2**: Evidence bundle
- **SISAS**: Signal enrichment, context scoping

### Downstream Obligations
- **Phase 4**: Provides micro scores for aggregation
- **Phase 8**: Provides scores for recommendation generation

### Known Failure Modes / Risk Concentrations
| Failure Mode | Trigger | Mitigation |
|--------------|---------|------------|
| Score out of bounds | `score < 0 or score > 3` | Clamp and warn |
| Missing evidence | No evidence for question | Default to 0 |
| Context mismatch | Signal scope violation | Skip signal |

### Instrumentation & Metrics
- Score distribution (0-3 range)
- Evidence-to-score conversion rate
- Missing data percentage

---

## Phase 4: Dimension Aggregation

### Phase Identifier and Name
- **ID**: `PHASE-4-DIMENSION-AGGREGATION`
- **Canonical Name**: `phase_4_dimension_aggregation`
- **Codename**: `DIM_AGG`

### System Function
Aggregates **300 micro scores into 60 dimension scores** using the **Choquet Integral** for non-linear aggregation that accounts for interaction between dimensions within each policy area.

**Compression Ratio**: 5:1 (300 → 60)

### Policy State In / Policy State Out
- **Input**: `MicroScore[]` (300 scores)
- **Output**: `DimensionScore[]` (60 scores: 10 PA × 6 DIM)
- **State Transition**: `SCORED` → `DIMENSION_AGGREGATED`

### Primary Artifacts Produced
| Artifact | Type | Description |
|----------|------|-------------|
| Dimension Scores | `DimensionScore[]` | 60 scores (D001-D060) |
| Choquet Weights | `ChoquetWeightMatrix` | Non-additive weights |
| Dispersion Metrics | `DispersionMetrics` | CV, DI, quartiles per dimension |

### Decision Rights and Accountability
- **Authority**: `DimensionAggregator`
- **Veto Points**: Dimension count ≠ 60, score domain violations
- **Contract Enforcement**: `CP-4.1` (Dimension Count), `CP-4.2` (Choquet Integral)

### Upstream Dependencies
- **Phase 3**: 300 micro scores

### Downstream Obligations
- **Phase 5**: Provides 60 dimension scores for area aggregation

### Known Failure Modes / Risk Concentrations
| Failure Mode | Trigger | Mitigation |
|--------------|---------|------------|
| Dimension count mismatch | `len(scores) != 60` | Constitutional invariant error |
| Choquet convergence | Weights not normalized | Re-normalize with warning |
| High dispersion | `CV > 0.6` | Flag for review |

### Instrumentation & Metrics
- Compression ratio (300:60)
- Dispersion by dimension
- Choquet integral convergence

---

## Phase 5: Area Aggregation

### Phase Identifier and Name
- **ID**: `PHASE-5-AREA-AGGREGATION`
- **Canonical Name**: `phase_5_area_aggregation`
- **Codename**: `AREA_AGG`

### System Function
Aggregates **60 dimension scores into 10 policy area scores** using weighted arithmetic mean. Each policy area (PA01-PA10) receives 6 dimension scores (DIM01-DIM06).

**Compression Ratio**: 6:1 (60 → 10)

### Policy State In / Policy State Out
- **Input**: `DimensionScore[]` (60 scores)
- **Output**: `AreaScore[]` (10 scores: PA01-PA10)
- **State Transition**: `DIMENSION_AGGREGATED` → `AREA_AGGREGATED`

### Primary Artifacts Produced
| Artifact | Type | Description |
|----------|------|-------------|
| Area Scores | `AreaScore[]` | 10 scores (PA01-PA10) |
| Area Weights | `AreaWeightMatrix` | Dimension weights per area |
| Quality Levels | `QualityLevel[]` | EXCELENTE/BUENO/ACEPTABLE/INSUFICIENTE |

### Decision Rights and Accountability
- **Authority**: `AreaAggregator`
- **Veto Points**: Area count ≠ 10
- **Contract Enforcement**: `CP-5.1` (Area Coverage), `CP-5.2` (Weight Normalization)

### Upstream Dependencies
- **Phase 4**: 60 dimension scores

### Downstream Obligations
- **Phase 6**: Provides 10 area scores for cluster aggregation

### Known Failure Modes / Risk Concentrations
| Failure Mode | Trigger | Mitigation |
|--------------|---------|------------|
| Area count mismatch | `len(scores) != 10` | Constitutional invariant error |
| Weight sum ≠ 1.0 | Normalization error | Re-normalize |
| Zero dimensions | Area with no dimensions | Skip area with warning |

### Instrumentation & Metrics
- Compression ratio (60:10)
- Area score distribution
| Weight normalization status

---

## Phase 6: Cluster Aggregation

### Phase Identifier and Name
- **ID**: `PHASE-6-CLUSTER-AGGREGATION`
- **Canonical Name**: `phase_6_cluster_aggregation`
- **Codename**: `CLUSTER_AGG`

### System Function
Aggregates **10 policy area scores into 4 MESO-level cluster scores** with the **Adaptive Penalty Framework (APF)** that applies score corrections when intra-cluster dispersion exceeds thresholds.

**Compression Ratio**: 2.5:1 (10 → 4)

### Cluster Topology
| Cluster | Policy Areas | Thematic Focus |
|---------|--------------|----------------|
| CLUSTER_MESO_1 | PA01, PA02, PA03 | Legal & Institutional Framework |
| CLUSTER_MESO_2 | PA04, PA05, PA06 | Implementation & Operational Capacity |
| CLUSTER_MESO_3 | PA07, PA08 | Monitoring & Evaluation Systems |
| CLUSTER_MESO_4 | PA09, PA10 | Strategic Planning & Sustainability |

### Policy State In / Policy State Out
- **Input**: `AreaScore[]` (10 scores)
- **Output**: `ClusterScore[]` (4 scores: MESO_1-4)
- **State Transition**: `AREA_AGGREGATED` → `CLUSTER_AGGREGATED`

### Primary Artifacts Produced
| Artifact | Type | Description |
|----------|------|-------------|
| Cluster Scores | `ClusterScore[]` | 4 scores (MESO_1-4) |
| Penalty Factors | `PenaltyFactor[]` | Adaptive penalty (0.70-1.00) |
| Dispersion Analysis | `ClusterDispersion[]` | CV, DI, IQR per cluster |
| Coherence Metrics | `CoherenceMetrics[]` | Within-cluster coherence |

### Adaptive Penalty Framework
| CV Range | Scenario | Penalty Factor | Interpretation |
|----------|----------|----------------|----------------|
| < 0.20 | CONVERGENCE | 1.00 | Coherent implementation |
| 0.20-0.39 | MODERATE | 0.95 | Minor inconsistencies |
| 0.40-0.59 | HIGH | 0.85 | Significant gaps |
| ≥ 0.60 | EXTREME | 0.70 | Systemic failure |

### Decision Rights and Accountability
- **Authority**: `ClusterAggregator`
- **Veto Points**: Cluster count ≠ 4, penalty out of bounds
- **Contract Enforcement**: `CP-6.1` (Cluster Coverage), `CP-6.2` (Penalty Bounds)

### Upstream Dependencies
- **Phase 5**: 10 area scores

### Downstream Obligations
- **Phase 7**: Provides 4 cluster scores for macro evaluation

### Known Failure Modes / Risk Concentrations
| Failure Mode | Trigger | Mitigation |
|--------------|---------|------------|
| Cluster count mismatch | `len(scores) != 4` | Constitutional invariant error |
| Penalty out of bounds | `factor < 0.7 or > 1.0` | Clamp to valid range |
| Empty cluster | No areas assigned | Fatal error |

### Instrumentation & Metrics
- Compression ratio (10:4)
- Penalty distribution
- Dispersion statistics

---

## Phase 7: Macro Evaluation

### Phase Identifier and Name
- **ID**: `PHASE-7-MACRO-EVALUATION`
- **Canonical Name**: `phase_7_macro_evaluation`
- **Codename**: `MACRO_EVAL`

### System Function
Synthesizes **4 MESO-level cluster scores into a single holistic MacroScore** with **Cross-Cutting Coherence Analysis (CCCA)**, **Systemic Gap Detection (SGD)**, and **Strategic Alignment Scoring (SAS)**.

**Compression Ratio**: 4:1 (4 → 1)

### Policy State In / Policy State Out
- **Input**: `ClusterScore[]` (4 scores)
- **Output**: `MacroScore` (1 holistic score)
- **State Transition**: `CLUSTER_AGGREGATED` → `MACRO_EVALUATED`

### Primary Artifacts Produced
| Artifact | Type | Description |
|----------|------|-------------|
| Macro Score | `MacroScore` | Single holistic score [0-3] |
| Quality Classification | `QualityLevel` | EXCELENTE/BUENO/ACEPTABLE/INSUFICIENTE |
| Cross-Cutting Coherence | `CoherenceBreakdown` | Strategic/Operational/Institutional |
| Systemic Gaps | `List[str]` | Policy areas requiring intervention |
| Strategic Alignment | `AlignmentBreakdown` | Vertical/Horizontal/Temporal |

### Quality Classification Rubric (Normalized)
| Quality Level | Range | 3-Point Range | Description |
|---------------|-------|---------------|-------------|
| EXCELENTE | ≥ 0.85 | ≥ 2.55 | Outstanding policy compliance |
| BUENO | 0.70-0.84 | 2.10-2.54 | Good compliance with minor gaps |
| ACEPTABLE | 0.55-0.69 | 1.65-2.09 | Acceptable with improvement areas |
| INSUFICIENTE | < 0.55 | < 1.65 | Insufficient, requires intervention |

### Decision Rights and Accountability
- **Authority**: `MacroEvaluator`
- **Veto Points**: Output not singleton, score out of bounds
- **Contract Enforcement**: `CP-7.1` (Singleton Output), `CP-7.2` (Score Domain)

### Upstream Dependencies
- **Phase 6**: 4 cluster scores

### Downstream Obligations
- **Phase 8**: Provides macro score for recommendations
- **Phase 9**: Provides macro evaluation for reporting

### Known Failure Modes / Risk Concentrations
| Failure Mode | Trigger | Mitigation |
|--------------|---------|------------|
| Non-singleton output | `len(scores) != 1` | Fatal architectural error |
| Coherence calculation | Division by zero | Fallback to default |
| Gap detection | All areas flagged | Review threshold calibration |

### Instrumentation & Metrics
- Final compression ratio (300:1)
- Coherence indices
- Gap severity distribution

---

## Phase 8: Recommendation Engine

### Phase Identifier and Name
- **ID**: `PHASE-8-RECOMMENDATION-ENGINE`
- **Canonical Name**: `phase_8_recommendation_engine`
- **Codename**: `RECOMMENDER`

### System Function
Generates **evidence-based policy recommendations** at three levels (MICRO, MESO, MACRO) using an **exponentially enhanced v3.0 engine** with 5 optimization windows delivering **4.5×10¹² x** value multiplier through:
- Schema-driven validation (120x)
- Generic rule engine (∞ scalability)
- Template compilation (200x)
- Memoized validation (6,250x)
- Generative testing (30,000x)

### Policy State In / Policy State Out
- **Input**: `ScoreMatrix` + `MacroScore` + quality levels
- **Output**: `RecommendationSet[]` (MICRO/MESO/MACRO)
- **State Transition**: `MACRO_EVALUATED` → `RECOMMENDATIONS_GENERATED`

### Primary Artifacts Produced
| Artifact | Type | Description |
|----------|------|-------------|
| MICRO Recommendations | `RecommendationSet` | Dimension-level (300 rules) |
| MESO Recommendations | `RecommendationSet` | Cluster-level recommendations |
| MACRO Recommendations | `RecommendationSet` | Strategic recommendations |
| Recommendation Metadata | `RecMetadata` | Priority, urgency, evidence links |

### Decision Rights and Accountability
- **Authority**: `RecommendationEngine`
- **Veto Points**: Invalid rules, missing context
- **Contract Enforcement**: `CP-8.1` (Rule Schema), `CP-8.2` (Template Safety)

### Upstream Dependencies
- **Phase 3**: Micro scores
- **Phase 6**: Cluster scores
- **Phase 7**: Macro score and quality level

### Downstream Obligations
- **Phase 9**: Provides recommendations for report inclusion

### Known Failure Modes / Risk Concentrations
| Failure Mode | Trigger | Mitigation |
|--------------|---------|------------|
| Rule validation failure | Schema violation | Skip rule with warning |
| Template rendering | Missing variable | Use default value |
| Cache invalidation | Rule changed | Clear validation cache |

### Instrumentation & Metrics
- Recommendations generated per level
- Rule match statistics
- Template render performance

---

## Phase 9: Reporting

### Phase Identifier and Name
- **ID**: `PHASE-9-REPORTING`
- **Canonical Name**: `phase_9_reporting`
- **Codename**: `REPORTER`

### System Function
Assembles **comprehensive policy evaluation reports** with multiple output formats using Jinja2 templates. Generates executive dashboards and technical deep-dive reports with all evaluation artifacts.

### Policy State In / Policy State Out
- **Input**: `MacroScore` + `RecommendationSet[]` + all phase artifacts
- **Output**: `EvaluationReport` (HTML/PDF)
- **State Transition**: `RECOMMENDATIONS_GENERATED` → `REPORT_COMPLETE`

### Primary Artifacts Produced
| Artifact | Type | Description |
|----------|------|-------------|
| Executive Dashboard | `HTML` | High-level summary for decision makers |
| Technical Deep Dive | `HTML` | Detailed analysis for technical review |
| Institutional Annex | `PDF` | Entity-specific findings |
| Report Metadata | `ReportMetadata` | Generation timestamp, version, hashes |

### Report Templates
| Template | Purpose | Audience |
|----------|---------|----------|
| `executive_dashboard.html.j2` | Strategic summary | Policy makers |
| `technical_deep_dive.html.j2` | Detailed analysis | Technical reviewers |
| `report_enhanced.html.j2` | Full evaluation | Comprehensive review |

### Decision Rights and Accountability
- **Authority**: `ReportGenerator`
- **Veto Points**: Missing required artifacts, template errors
- **Contract Enforcement**: `CP-9.1` (Artifact Completeness), `CP-9.2` (Template Safety)

### Upstream Dependencies
- **All Phases 0-8**: Complete evaluation artifacts
- **Factory**: Configuration, provenance metadata

### Downstream Obligations
- None (Phase 9 is terminal)

### Known Failure Modes / Risk Concentrations
| Failure Mode | Trigger | Mitigation |
|--------------|---------|------------|
| Template error | Invalid Jinja2 syntax | Use fallback template |
| Missing artifact | Phase output unavailable | Include placeholder |
| PDF generation | Rendering failure | Output HTML only |

### Instrumentation & Metrics
- Report generation duration
| Template render time
| Artifact completeness

---

## Orchestration Layer

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATION LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Orchestrator                                 │   │
│  │                                                                     │   │
│  │  Dependencies (injected via Factory):                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │ 1. method_executor: MethodExecutor                          │    │   │
│  │  │    - method_registry: MethodRegistry (348 methods)          │    │   │
│  │  │    - arg_router: ExtendedArgRouter                          │    │   │
│  │  │    - signal_registry: QuestionnaireSignalRegistry v2.0      │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │ 2. questionnaire: CanonicalQuestionnaire                    │    │   │
│  │  │    - 300 questions, 10 PA, 6 DIM, 4 MESO, 1 MACRO          │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │ 3. executor_config: ExecutorConfig                          │    │   │
│  │  │    - max_tokens, retries, timeouts                          │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │ 4. runtime_config: RuntimeConfig | None                     │    │   │
│  │  │    - mode: PROD | DEV | TEST                                │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │ 5. phase0_validation: Phase0ValidationResult | None        │    │   │
│  │  │    - all_passed, gate_results                               │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │ Coordinates Phase Execution           │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Phase Execution Sequence                         │   │
│  │                                                                     │   │
│  │  Phase 0 (Bootstrap) ──▶ Phase 1-3 (Ingestion) ──▶ Phase 4-7       │   │
│  │       │                       │                      │               │   │
│  │       │                       │                      │               │   │
│  │       ▼                       ▼                      ▼               │   │
│  │  Phase 0Validation        Evidence Extraction    Aggregation         │   │
│  │  (7 Exit Gates)          (30 Executors)        Pyramid             │   │
│  │                                                                     │   │
│  │                          │                      │                   │   │
│  │                          └──────────┬───────────┘                   │   │
│  │                                     │                               │   │
│  │                                     ▼                               │   │
│  │                          Phase 8 (Recommendations)                  │   │
│  │                                     │                               │   │
│  │                                     ▼                               │   │
│  │                          Phase 9 (Reporting)                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Orchestrator Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Phase Coordination | Execute phases in correct order |
| Contract Enforcement | Verify phase handoff contracts |
| Error Handling | Manage failures, retries, rollbacks |
| Provenance Tracking | Maintain audit trail across phases |
| Resource Management | Control memory, compute, I/O |
| State Management | Maintain pipeline state machine |

---

## Factory Pattern

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ANALYSIS PIPELINE FACTORY                                │
│              (SINGLE AUTHORITATIVE CONSTRUCTION BOUNDARY)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Entry Point:                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ factory = AnalysisPipelineFactory(                                  │   │
│  │     questionnaire_path="path/to/questionnaire.json",                │   │
│  │     expected_hash="abc123...",                                      │   │
│  │     seed_for_determinism=42,                                        │   │
│  │     run_phase0_validation=True,                                    │   │
│  │ )                                                                   │   │
│  │ bundle = factory.create_orchestrator()                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │ Construction Sequence (10 steps)       │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   Step 0: Phase 0 Validation                        │   │
│  │   - Run Phase 0 boot checks (7 gates)                              │   │
│  │   - Return Phase0ValidationResult                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              Step 1: Load Canonical Questionnaire                   │   │
│  │   - SINGLETON ENFORCEMENT (load once, cache forever)                │   │
│  │   - SHA-256 integrity verification                                  │   │
│  │   - Returns: CanonicalQuestionnaire (immutable)                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │           Step 2: Build Signal Registry (v2.0)                      │   │
│  │   - create_signal_registry(questionnaire)                          │   │
│  │   - Load 300+ contracts from canonical source                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         Step 3: Build Enriched Signal Packs                         │   │
│  │   - Semantic expansion + context filtering                          │   │
│  │   - One pack per policy area (PA01-PA10)                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         Step 4: Initialize Seed Registry                             │   │
│  │   - SeedRegistry.initialize(master_seed=42)                         │   │
│  │   - Enables deterministic RNG                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │       Step 5: Build Method Executor (348 methods)                    │   │
│  │   - MethodRegistry with canonical method injection                  │   │
│  │   - ExtendedArgRouter for argument routing                          │   │
│  │   - Verify all 30 executor contracts before execution               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │      Step 6: Load Phase 1 Validation Constants                      │   │
│  │   - P01_EXPECTED_CHUNK_COUNT = 60                                   │   │
│  │   - Hard contracts for chunk validation                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │          Step 7: Get or Create ExecutorConfig                       │   │
│  │   - Operational parameters (max_tokens, retries, timeouts)          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         Step 8: Build Orchestrator (Full DI)                        │   │
│  │   Orchestrator(                                                       │   │
│  │       method_executor=method_executor,                                │   │
│  │       questionnaire=questionnaire,                                    │   │
│  │       executor_config=executor_config,                                │   │
│  │       runtime_config=runtime_config,                                  │   │
│  │       phase0_validation=phase0_validation,                            │   │
│  │   )                                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              Step 9: Assemble Provenance Metadata                    │   │
│  │   - construction_timestamp_utc                                       │   │
│  │   - canonical_sha256                                                  │   │
│  │   - signal_registry_version = "2.0"                                  │   │
│  │   - phase0_validation_passed                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │           Step 10: Build ProcessorBundle                            │   │
│  │   - Immutable bundle with all dependencies                          │   │
│  │   - Validates bundle integrity on creation                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Factory Principles

1. **FACTORY PATTERN**: AnalysisPipelineFactory is the ONLY place that instantiates:
   - Orchestrator, MethodExecutor, QuestionnaireSignalRegistry, BaseExecutor instances
   - NO other module should directly instantiate these classes

2. **DEPENDENCY INJECTION**: All components receive dependencies via `__init__`:
   - Orchestrator receives: method_executor, questionnaire, executor_config, runtime_config, phase0_validation
   - MethodExecutor receives: method_registry, arg_router, signal_registry
   - BaseExecutor (30 classes) receive: enriched_signal_pack, method_executor, config

3. **CANONICAL MONOLITH CONTROL**:
   - `load_questionnaire()` called ONCE by factory only (singleton + integrity hash)
   - Orchestrator uses `self.questionnaire` object, NEVER file paths
   - Search codebase: NO other `load_questionnaire()` calls should exist

4. **SIGNAL REGISTRY CONTROL**:
   - `create_signal_registry(questionnaire)` - from canonical source ONLY
   - Registry injected into MethodExecutor, NOT accessed globally

5. **ENRICHED SIGNAL PACK INJECTION**:
   - Factory builds EnrichedSignalPack per executor (semantic expansion + context filtering)
   - Each BaseExecutor receives its specific pack, NOT full registry

6. **DETERMINISM**:
   - SeedRegistry singleton initialized by factory for reproducibility
   - ExecutorConfig encapsulates operational params

7. **PHASE 1 HARD CONTRACTS**:
   - Validation constants (P01_EXPECTED_CHUNK_COUNT=60) loaded by factory
   - Injected into Orchestrator for Phase 1 chunk validation
   - Execution FAILS if contracts violated

8. **PHASE 0 INTEGRATION**:
   - RuntimeConfig loaded from environment (or passed explicitly)
   - Phase 0 boot checks validate system dependencies
   - Phase 0 exit gates (7 gates) ensure all prerequisites are met

---

## SISAS Integration

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              SISAS - SIGNAL INTELLIGENCE SEMANTIC ARCHITECTURE SYSTEM       │
│                         (Cross-Cutting Infrastructure)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         SIGNAL BUS SYSTEM                            │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │   │
│  │  │ STRUCTURAL  │  │ INTEGRITY   │  │ EPISTEMIC   │                │   │
│  │  │ BUS         │  │ BUS         │  │ BUS         │                │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │   │
│  │  │ CONTRAST    │  │ OPERATIONAL │  │ CONSUMPTION │                │   │
│  │  │ BUS         │  │ BUS         │  │ BUS         │                │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                │   │
│  │                                                                     │   │
│  │  Features:                                                          │   │
│  │  - Priority queue for processing                                    │   │
│  │  - Backpressure mechanism                                           │   │
│  │  - Dead letter queue for failed messages                            │   │
│  │  - Circuit breaker for problematic consumers                        │   │
│  │  - Real-time metrics and aggregated stats                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │ Signal Flow                             │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      VEHICLES (Publishers)                           │   │
│  │                                                                     │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │   │
│  │  │ SignalLoader     │  │ SignalIrrigator  │  │ SignalEnhancer  │  │   │
│  │  │ (Load patterns)  │  │ (Inject signals) │  │ (Semantic exp)  │  │   │
│  │  └──────────────────┘  └──────────────────┘  └─────────────────┘  │   │
│  │  ┌──────────────────┐  ┌──────────────────┐                         │   │
│  │  │ EvidenceExtractor │  │ QualityMetrics   │                         │   │
│  │  │ (Pattern match)  │  │ (Signal quality) │                         │   │
│  │  └──────────────────┘  └──────────────────┘                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     CONSUMERS (Subscribers)                          │   │
│  │                                                                     │   │
│  │  Phase 0: Bootstrap (wiring, providers)                            │   │
│  │  Phase 1: Signal Enrichment                                        │   │
│  │  Phase 2: Contract/Evidence/Factory/Executor Consumers               │   │
│  │  Phase 3: Signal Enriched Scoring                                  │   │
│  │  Phase 7: MESO Consumer                                            │   │
│  │  Phase 8: Signal Enriched Recommendations                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         SIGNAL REGISTRY                              │   │
│  │  (QuestionnaireSignalRegistry v2.0)                                 │   │
│  │                                                                     │   │
│  │  - 300+ contracts loaded from canonical questionnaire              │   │
│  │  - Per-policy-area signal packs (PA01-PA10)                        │   │
│  │  - Semantic expansion capabilities                                  │   │
│  │  - Context filtering by scope                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### SISAS Signal Categories

| Category | Bus | Description | Example Signals |
|----------|-----|-------------|-----------------|
| STRUCTURAL | structural_bus | Document structure signals | Section headers, tables |
| INTEGRITY | integrity_bus | Data quality signals | Completeness, consistency |
| EPISTEMIC | epistemic_bus | Knowledge signals | Causal links, goals |
| CONTRAST | contrast_bus | Comparative signals | Before/after, with/without |
| OPERATIONAL | operational_bus | Implementation signals | Budgets, timelines |
| CONSUMPTION | consumption_bus | Pattern consumption tracking | Match counts, evidence yield |

### SISAS Integration Points

| Phase | Integration Point | Purpose |
|-------|-------------------|---------|
| Phase 0 | `phase0_90_02_bootstrap.py` | Bootstrap wiring, providers |
| Phase 1 | `phase1_13_00_cpp_ingestion.py` | Signal enrichment for chunking |
| Phase 2 | `phase2_contract_consumer.py` | Contract-based signal routing |
| Phase 2 | `phase2_evidence_consumer.py` | Evidence extraction signals |
| Phase 2 | `phase2_factory_consumer.py` | Factory signal integration |
| Phase 3 | `phase3_10_00_signal_enriched_scoring.py` | Signal-based scoring |
| Phase 7 | `phase7_meso_consumer.py` | MESO-level signal consumption |
| Phase 8 | `phase8_30_00_signal_enriched_recommendations.py` | Recommendation signals |

---

## Contracts System

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        300+ CONTRACTS SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Contract Distribution:                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Phase 0: 0 contracts (validation only)                             │   │
│  │  Phase 1: 0 contracts (structural validation)                       │   │
│  │  Phase 2: ~300 contracts (Q001-Q300 × PA01-PA10)                    │   │
│  │  Phase 3-9: Derived from Phase 2 contracts                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Contract Structure (Phase 2 Example):                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Q001_PA01_contract_v4.json                                          │   │
│  │  {                                                                  │   │
│  │    "question_id": "Q001",                                           │   │
│  │    "policy_area": "PA01",                                           │   │
│  │    "dimension": "DIM01",                                            │   │
│  │    "version": 4,                                                    │   │
│  │    "signals": [...],                                                │   │
│  │    "patterns": [...],                                               │   │
│  │    "evidence_requirements": {...},                                   │   │
│  │    "scoring_rules": {...}                                            │   │
│  │  }                                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Contract Location:                                                         │
│  src/farfan_pipeline/phases/Phase_02/generated_contracts/                    │
│    ├── Q001_PA01_contract_v4.json                                           │
│    ├── Q001_PA02_contract_v4.json                                           │
│    ├── ...                                                                  │
│    ├── Q300_PA10_contract_v4.json                                           │
│    └── (~300 files)                                                         │
│                                                                             │
│  Chain Reports (Provenance):                                                │
│  src/farfan_pipeline/phases/Phase_*/contracts/                               │
│    ├── phase0_chain_report.json                                             │
│    ├── phase1_chain_report.json                                             │
│    ├── phase2_chain_report.json                                             │
│    ├── phase4_chain_report.json                                             │
│    ├── phase5_chain_report.json                                             │
│    ├── phase6_chain_report.json                                             │
│    └── phase8_chain_report.json                                             │
│                                                                             │
│  Certificates (Compliance):                                                  │
│  src/farfan_pipeline/phases/Phase_02/contracts/certificates/                  │
│    ├── CERTIFICATE_DURALEX_00_SUMMARY.json                                  │
│    ├── CERTIFICATE_DURALEX_01_BMC.json                                      │
│    ├── ...                                                                  │
│    └── CERTIFICATE_PHASE3_COMPATIBILITY.json                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Contract Schema

```json
{
  "$schema": "contract_schema.json",
  "type": "object",
  "properties": {
    "question_id": {"type": "string", "pattern": "^Q[0-9]{3}$"},
    "policy_area": {"type": "string", "pattern": "^PA[0-9]{2}$"},
    "dimension": {"type": "string", "pattern": "^DIM[0-9]{2}$"},
    "version": {"type": "integer", "minimum": 1},
    "signals": {
      "type": "array",
      "items": {"$ref": "#/definitions/signal"}
    },
    "patterns": {
      "type": "array",
      "items": {"$ref": "#/definitions/pattern"}
    },
    "evidence_requirements": {
      "type": "object",
      "properties": {
        "min_evidence_count": {"type": "integer"},
        "required_element_types": {"type": "array"},
        "context_scope": {"type": "string"}
      }
    },
    "scoring_rules": {
      "type": "object",
      "properties": {
        "scoring_method": {"type": "string"},
        "weight": {"type": "number"},
        "threshold": {"type": "number"}
      }
    }
  },
  "required": ["question_id", "policy_area", "dimension", "version"],
  "definitions": {
    "signal": {
      "type": "object",
      "properties": {
        "signal_id": {"type": "string"},
        "category": {"enum": ["STRUCTURAL", "INTEGRITY", "EPISTEMIC", "CONTRAST", "OPERATIONAL", "CONSUMPTION"]},
        "pattern_text": {"type": "string"},
        "context_requirement": {"type": "object"}
      }
    },
    "pattern": {
      "type": "object",
      "properties": {
        "pattern_id": {"type": "string"},
        "pattern": {"type": "string"},
        "element_type": {"type": "string"},
        "context_scope": {"type": "string"}
      }
    }
  }
}
```

---

## Cross-Cutting Concerns

### 1. Assumptions and Invariants

**System Invariants:**
1. **Chunk Count**: Phase 1 MUST produce exactly 60 chunks (10 PA × 6 DIM)
2. **Score Domain**: All scores are in [0.0, 3.0] range
3. **Compression Ratio**: Total pipeline compression is 300:1
4. **Singleton Questionnaire**: Canonical questionnaire loaded exactly once
5. **Determinism**: RNG seeded via SeedRegistry for reproducibility

**Architectural Assumptions:**
1. Input PDF is machine-readable and contains structured text
2. Questionnaire JSON is valid and conforms to schema
3. Python 3.10+ runtime environment
4. Sufficient memory for loading all contracts (~300 JSON files)
5. Network access (optional) for LLM-based pattern enhancement

### 2. Normative vs. Analytical Separation

**Normative Components** (Value Judgments):
- Quality classification thresholds (EXCELENTE/BUENO/ACEPTABLE/INSUFICIENTE)
- Penalty function calibration (CV thresholds)
- Strategic priorities (cluster weights)
- Recommendation priorities

**Analytical Components** (Value-Free):
- Aggregation algorithms (Choquet integral, weighted mean)
- Score calculations
- Dispersion metrics (CV, DI, IQR)
- Coherence indices

**Separation Enforcement:**
- Normative parameters are configurable via `ExecutorConfig`
- Analytical calculations are deterministic and invariant
- All value judgments are documented in configuration files

### 3. Scalability and Reuse

**Reusable Components:**
- `MethodExecutor` (348 methods, applicable to any policy domain)
- `SignalBus` (category-agnostic pub/sub system)
- `AggregationPipeline` (Phase 4-7, domain-independent)
- `RecommendationEngine` (schema-driven, any rule set)

**Domain-Specific Components:**
- Questionnaire (300 questions, specific to policy framework)
- Contracts (300+ patterns, domain-encoded)
- Quality thresholds (policy-specific calibration)

### 4. Auditability and Traceability

**Provenance Tracking:**
- W3C PROV-DM compliance for all phases
- Entity-Activity-Agent model
- Immutable provenance records with SHA-256 hashes
- Complete derivation chains from input to output

**Audit Artifacts:**
- Phase chain reports (JSON provenance documents)
- Execution logs with timestamps
- Consumption proofs (pattern match tracking)
- Bundle validation records

### 5. Failure Containment

**Phase-Level Isolation:**
- Each phase has explicit preconditions and postconditions
- Contract violations halt execution at phase boundaries
- No state leakage between phases

**Error Handling Strategy:**
| Error Type | Phase 0-3 | Phase 4-7 | Phase 8-9 |
|------------|-----------|-----------|-----------|
| Input Invalid | Fail Fast | Skip + Warn | Fallback |
| Contract Violation | Halt | Halt | Skip |
| Executor Failure | Retry | Retry | Skip |
| Template Error | N/A | N/A | Fallback |

---

## Architecture Change Log

### Version 1.0.0 (2026-01-17)

**Structural Changes:**
- Initial canonical architecture specification
- 10 phases (0-9) with explicit contracts
- SISAS integration documented
- Factory pattern with DI established

**Interface Changes:**
- `ProcessorBundle` as canonical DI container
- `Phase0ValidationResult` for bootstrap validation
- `CanonicalQuestionnaire` immutable wrapper

**Governance Changes:**
- Exit gates for Phase 0 (7 gates)
- Contract enforcement via Design by Contract
- Precondition/postcondition validation per phase

**Rationale:**
This architecture establishes the foundation for a governed, auditable policy evaluation pipeline with explicit phase boundaries, clear interfaces, and comprehensive traceability.

---

## Appendix: Quick Reference

### Phase Summary Matrix

| Phase | Input | Output | Compression | Key Algorithm |
|-------|-------|--------|-------------|----------------|
| 0 | Raw PDF | Validated State | N/A | 7 Exit Gates |
| 1 | Validated Doc | 60 Chunks | N/A | Matrix Decomposition |
| 2 | 60 Chunks | 300 Evidence | N/A | Pattern Matching |
| 3 | 300 Evidence | 300 Scores | N/A | Signal Enriched Scoring |
| 4 | 300 Scores | 60 Dims | 5:1 | Choquet Integral |
| 5 | 60 Dims | 10 Areas | 6:1 | Weighted Mean |
| 6 | 10 Areas | 4 Clusters | 2.5:1 | Adaptive Penalty |
| 7 | 4 Clusters | 1 Macro | 4:1 | CCCA/SGD/SAS |
| 8 | All Scores | Recs | N/A | Rule Engine v3.0 |
| 9 | All Artifacts | Report | N/A | Template Rendering |

### Contact Points

| Architectural Concern | Lead Component | Document |
|-----------------------|----------------|----------|
| Factory Pattern | `AnalysisPipelineFactory` | `phase2_10_00_factory.py` |
| Orchestration | `Orchestrator` | `orchestration/orchestrator.py` |
| SISAS | `SignalBus` | `SISAS/core/bus.py` |
| Contracts | `ContractSchema` | `SISAS/schemas/contract_schema.json` |
| Method Dispensary | `MethodExecutor` | `orchestration/method_registry.py` |

---

*Document Version: 1.0.0*
*Last Updated: 2026-01-17*
*Maintained by: F.A.R.F.A.N. Architecture Team*
*License: Internal Use Only*
