# Phase 2: Deterministic Executor Orchestration for Reproducible Policy Analysis

**A Contract-Driven Multi-Method Synthesis Architecture with Signal-Irrigated Evidence Assembly**

*F.A.R.F.A.N Mechanistic Policy Pipeline*  
Version 3.1.0 | December 2025

---

## Abstract

Phase 2 constitutes the analytical core of the F.A.R.F.A.N deterministic policy pipeline, implementing contract-driven executor orchestration with Signal-Irrigated Smart Augmentation System (SISAS) integration. This module transforms 60-chunk Canonical Policy Packages into 300 evidence-rich analytical responses through a five-stage transformation pipeline guaranteeing bitwise-identical reproducibility. The architecture comprises 29 Python modules organized in strict alphabetical sequence (a–z, aa–ac), each labeled with `PHASE_LABEL: Phase 2` for provenance tracking. This document specifies the complete technical architecture, execution semantics, signal irrigation mechanics, and formal verification properties required for peer-reviewed computational social science.

**Keywords**: deterministic orchestration, contract-driven execution, signal irrigation, multi-method synthesis, evidence provenance, reproducible policy analysis

---

## 1. Introduction

### 1.1 Phase Position in Pipeline

```
┌──────────┐   ┌──────────┐   ┌────────────┐   ┌──────────┐   ┌────────────┐   ┌──────────┐
│ Phase 0  │ → │ Phase 1  │ → │  PHASE 2   │ → │ Phase 3  │ → │ Phase 4-7  │ → │ Phase 8-9│
│ Config   │   │ Ingestion│   │ Execution  │   │ Scoring  │   │ Aggregation│   │ Reports  │
└──────────┘   └──────────┘   └────────────┘   └──────────┘   └────────────┘   └──────────┘
                    │               ▲
                    │               │
                    └───────────────┘
                    60 chunks → 300 responses
```

### 1.2 Input/Output Contract

**Input** (from Phase 1):
- `CanonPolicyPackage`: 60 preprocessed document chunks
- `questionnaire_monolith.json`: 300 analytical questions
- `SignalRegistry`: SISAS signal specifications

**Output** (to Phase 3):
- `ExecutorResults`: 300 `Phase2QuestionResult` objects
- Each result contains: synthesized narrative, evidence graph, confidence scores, gap analysis, provenance metadata

### 1.3 Core Guarantees

| Property | Guarantee | Verification |
|----------|-----------|--------------|
| **Determinism** | Bitwise-identical outputs for identical inputs | SHA-256 comparison across runs |
| **Reproducibility** | Same results on any compliant Python 3.12+ environment | Cross-platform test suite |
| **Traceability** | Complete lineage from source chunk to synthesized claim | Provenance DAG with SHA-256 nodes |
| **Completeness** | All 300 contracts executed; no silent failures | Execution manifest with checksums |

---

## 2. Theoretical Framework

### 2.1 Contract Formalism

**Definition 2.1 (Executor Contract)**: An executor contract $C_i$ is a quintuple:

$$C_i = \langle I, M, E, O, T \rangle$$

Where:
- $I$: Identity specification with unique $Q_i \in \{Q001, \ldots, Q300\}$
- $M$: Method binding to implementations $m_j \in \mathcal{M}$ (methods dispensary)
- $E$: Evidence assembly rules specifying graph construction strategies
- $O$: Output contract defining `Phase2QuestionResult` schema
- $T$: Traceability metadata with SHA-256 content hash

**Theorem 2.1 (Contract Determinism)**: Given identical inputs $(CPP, C_i, \sigma)$ where $\sigma=42$ is the random seed, execution produces bitwise-identical outputs across computational environments.

*Proof*: All stochastic operations use seeded RNG. Contract specifications are immutable (SHA-256 verified). Execution order is deterministic (priority fields). □

### 2.2 Signal Irrigation Model

**Definition 2.2 (Signal Irrigation)**: The SISAS system implements a publish-subscribe pattern where:

$$\text{Signal}: S = \langle id, type, content, source, confidence \rangle$$

Signals flow from questionnaire patterns through the `SignalRegistry` to executor contexts, enriching method execution with contextual evidence.

**Irrigation Equation**:
$$\text{EnrichedContext}_i = \text{BaseContext}_i \cup \bigcup_{s \in S_i} \text{resolve}(s)$$

Where $S_i$ are signals matching question $Q_i$'s requirements.

---

## 3. Module Architecture

### 3.1 Complete Module Inventory (29 Modules)

Phase 2 comprises **29 Python modules** organized in strict alphabetical sequence. Each module contains `PHASE_LABEL: Phase 2` in its docstring header (first 20 lines).

#### 3.1.1 Core Pipeline Layer (a–f)

| Seq | Module | Purpose | Input | Output |
|-----|--------|---------|-------|--------|
| **a** | `phase2_a_arg_router.py` | Type-safe argument routing using signature inspection. Routes kwargs to executor methods with 30+ special cases. Fails fast on missing required parameters. | `Dict[str, Any]` kwargs | Validated argument dict |
| **b** | `phase2_b_base_executor_with_contract.py` | Abstract base class implementing contract lifecycle: load, validate, execute, collect. Manages 300 contract bindings with SHA-256 verification. | Contract path, chunks | Method outputs |
| **c** | `phase2_c_carver.py` | Doctoral narrative synthesizer implementing Raymond Carver minimalist style. Generates prose with mandatory evidence citations, gap analysis, and calibrated confidence intervals. | EvidenceGraph, contract | CarverAnswer (narrative) |
| **d** | `phase2_d_calibration_policy.py` | 8-layer calibration policy hierarchy: global → dimension → policy_area → contract. Computes calibrated weights for Choquet integral fusion. | Layer scores | Calibrated weights |
| **e** | `phase2_e_contract_validator_cqvr.py` | Contract Quality Validation Registry. Validates contracts against `executor_contract.v3.schema.json`. Computes CQVR scores (Calibration, Quality, Validation, Reliability). | Contract JSON | CQVR score + tier |
| **f** | `phase2_f_evidence_nexus.py` | Graph-native evidence assembly engine. Constructs DAG from method outputs, infers causal/support/contradiction edges, applies Dempster-Shafer belief propagation. | Method outputs | EvidenceGraph |

#### 3.1.2 Validation & Metrics Layer (g–i)

| Seq | Module | Purpose | Input | Output |
|-----|--------|---------|-------|--------|
| **g** | `phase2_g_method_signature_validator.py` | Validates method signatures against chain layer requirements. Classifies inputs as required/optional/critical-optional. Enforces output type and range specifications. | Method signatures | ValidationResult |
| **h** | `phase2_h_metrics_persistence.py` | Persists `PhaseInstrumentation` telemetry to `artifacts/` for CI analysis and regression detection. Writes JSON metrics per phase. | Metrics dict | File path |
| **i** | `phase2_i_precision_tracking.py` | Tracks numerical precision across floating-point operations. Detects precision loss and stability issues in Bayesian computations. | Numeric values | Precision report |

#### 3.1.3 Resource Management Layer (j–l)

| Seq | Module | Purpose | Input | Output |
|-----|--------|---------|-------|--------|
| **j** | `phase2_j_resource_integration.py` | Integrates resource limits with executor lifecycle. Coordinates memory/CPU monitoring with execution flow. | Resource config | Integrated executor |
| **k** | `phase2_k_resource_aware_executor.py` | Executor implementation with adaptive resource management. Adjusts batch sizes and parallelism based on available resources. | Task, limits | Execution result |
| **l** | `phase2_l_resource_manager.py` | Central resource manager enforcing memory (≤2GB) and time (≤5000ms) limits. Implements circuit breaker pattern for resource exhaustion. | Limits config | ResourceManager |

#### 3.1.4 Runtime Validation Layer (m–o)

| Seq | Module | Purpose | Input | Output |
|-----|--------|---------|-------|--------|
| **m** | `phase2_m_signature_runtime_validator.py` | Runtime validation of method signatures during execution. Catches signature drift between contract and implementation. | Method, args | Validation status |
| **n** | `phase2_n_task_planner.py` | Deterministic task planning and scheduling. Generates execution order respecting priority constraints and resource availability. | Tasks, resources | Execution schedule |
| **o** | `phase2_o_methods_registry.py` | Lazy-loading methods registry with TTL-based caching. Instantiates dispensary classes only when first method is called. Manages 240+ methods across 40 classes. | Class/method name | Callable |

#### 3.1.5 Executor Infrastructure Layer (p–s)

| Seq | Module | Purpose | Input | Output |
|-----|--------|---------|-------|--------|
| **p** | `phase2_p_executor_profiler.py` | Performance profiling capturing execution time, memory peak, serialization overhead, and method call counts. Uses psutil for accurate RSS tracking. | Executor context | ExecutorMetrics |
| **q** | `phase2_q_executor_instrumentation_mixin.py` | Observability mixin injecting calibration hooks into executor lifecycle. Computes per-layer scores during execution. | Execution events | CalibrationResult |
| **r** | `phase2_r_executor_calibration_integration.py` | Calibration integration stub connecting runtime metrics to quality scores. Deterministic for identical inputs. | Runtime metrics | Quality scores |
| **s** | `phase2_s_executor_config.py` | Executor configuration management with conservative defaults. Manages timeouts, memory limits, batch sizes, and seed specification. | Config files | ExecutorConfig |

#### 3.1.6 Synchronization Layer (t–v)

| Seq | Module | Purpose | Input | Output |
|-----|--------|---------|-------|--------|
| **t** | `phase2_t_irrigation_synchronizer.py` | **Core SISAS integration point**. Orchestrates 60-chunk → 300-task transformation. Builds ChunkMatrix, generates ExecutionPlan with BLAKE3 integrity hash. Coordinates signal irrigation per task. | CPP, SignalRegistry | ExecutionPlan |
| **u** | `phase2_u_synchronization.py` | ChunkMatrix construction and ExecutionPlan generation. Implements deterministic task ordering with correlation_id propagation through all 10 phases. | Chunks, questions | ChunkMatrix |
| **v** | `phase2_v_executor_chunk_synchronizer.py` | Executor-chunk JOIN table manager. Ensures 1:1 binding between executors and chunks. Generates verification manifests for audit trail. | Executors, chunks | JOIN table |

#### 3.1.7 Factory & Registry Layer (w–z)

| Seq | Module | Purpose | Input | Output |
|-----|--------|---------|-------|--------|
| **w** | `phase2_w_factory.py` | **Single authority boundary** for dependency injection. Loads CanonicalQuestionnaire (once, verified). Constructs SignalRegistry, MethodExecutor, and EnrichedSignalPack per executor. | Config paths | Injected dependencies |
| **x** | `phase2_x_class_registry.py` | Dynamic class registry mapping orchestrator-facing names to import paths. Supports 40+ dispensary classes with 240+ methods. | Class name | Import path |
| **y** | `phase2_y_schema_validation.py` | Schema compatibility validation between question and chunk schemas. Detects type heterogeneity and structural mismatches. | Schemas | Compatibility report |
| **z** | `phase2_z_generic_contract_executor.py` | **Universal executor** replacing 300 hardcoded classes. Loads contract dynamically by question_id from `executor_contracts/specialized/Q{i:03d}.v3.json`. | question_id | Phase2QuestionResult |

#### 3.1.8 Extended Modules (aa–ac)

| Seq | Module | Purpose | Input | Output |
|-----|--------|---------|-------|--------|
| **aa** | `phase2_aa_method_source_validator.py` | AST-based source code validator. Builds source map of all classes/methods in pipeline for contract verification. | Source paths | Source map |
| **ab** | `phase2_ab_resource_alerts.py` | Resource threshold alerting system. Emits warnings when memory/CPU approach limits. Integrates with circuit breaker. | Resource metrics | Alerts |
| **ac** | `phase2_ac_executor_tests.py` | Executor test suite with calibration coverage. Validates contract instrumentation and CQVR compliance. | Test fixtures | Test results |

### 3.2 Module Dependency Graph

```
                                    ┌─────────────────────────────┐
                                    │      PHASE 1 OUTPUT         │
                                    │  CanonPolicyPackage (60)    │
                                    └─────────────┬───────────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             │                             │
                    ▼                             ▼                             ▼
            ┌───────────────┐             ┌───────────────┐             ┌───────────────┐
            │ t: Irrigation │◄────────────│ u: ChunkMatrix│◄────────────│ v: JOIN Table │
            │  Synchronizer │             │  Construction │             │   Manager     │
            └───────┬───────┘             └───────────────┘             └───────────────┘
                    │
                    │ ExecutionPlan (300 tasks)
                    ▼
            ┌───────────────┐
            │ w: DI Factory │────────────┐
            │ (authority)   │            │
            └───────┬───────┘            │
                    │                    │
        ┌───────────┼───────────┐        │
        │           │           │        │
        ▼           ▼           ▼        ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│x: ClassReg│ │o: Methods │ │ SISAS     │ │s: Config  │
│           │ │  Registry │ │ Signals   │ │           │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
      │             │             │             │
      └──────┬──────┴──────┬──────┴──────┬──────┘
             │             │             │
             ▼             ▼             ▼
      ┌─────────────────────────────────────────┐
      │        z: Generic Contract Executor      │
      │        ┌─────────────────────────────┐  │
      │        │ For each Q001...Q300:       │  │
      │        │  1. Load contract (e)       │  │
      │        │  2. Validate CQVR           │  │
      │        │  3. Route args (a)          │  │
      │        │  4. Execute methods (b)     │  │
      │        │  5. Profile (p, q, r)       │  │
      │        │  6. Collect outputs         │  │
      │        └─────────────────────────────┘  │
      └───────────────────┬─────────────────────┘
                          │
                          ▼ Method outputs
      ┌─────────────────────────────────────────┐
      │        f: Evidence Nexus                 │
      │        ┌─────────────────────────────┐  │
      │        │ 1. Ingest evidence nodes    │  │
      │        │ 2. Construct DAG            │  │
      │        │ 3. Infer edges (Bayesian)   │  │
      │        │ 4. Validate acyclicity      │  │
      │        │ 5. Belief propagation (D-S) │  │
      │        └─────────────────────────────┘  │
      └───────────────────┬─────────────────────┘
                          │
                          ▼ EvidenceGraph
      ┌─────────────────────────────────────────┐
      │        c: Doctoral Carver                │
      │        ┌─────────────────────────────┐  │
      │        │ 1. Interpret contract       │  │
      │        │ 2. Analyze gaps             │  │
      │        │ 3. Calibrate confidence (d) │  │
      │        │ 4. Render narrative         │  │
      │        │ 5. Enforce citations        │  │
      │        └─────────────────────────────┘  │
      └───────────────────┬─────────────────────┘
                          │
                          ▼
      ┌─────────────────────────────────────────┐
      │      PHASE 3 INPUT: ExecutorResults      │
      │      300 × Phase2QuestionResult          │
      └─────────────────────────────────────────┘
```

---

## 4. Signal Irrigation Architecture (SISAS)

### 4.1 SISAS Overview

The **Signal-Irrigated Smart Augmentation System (SISAS)** provides contextual enrichment to executor methods through a declarative signal specification framework. SISAS operates as a cross-cutting infrastructure layer, residing in `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/`.

### 4.2 SISAS Module Inventory

| Module | Purpose |
|--------|---------|
| `signals.py` | Core signal definitions and type specifications |
| `signal_registry.py` | Central registry mapping signals to questions |
| `signal_loader.py` | Loads signals from questionnaire_monolith |
| `signal_resolution.py` | Resolves signal requirements to concrete values |
| `signal_consumption.py` | Tracks signal consumption by executors |
| `signal_consumption_integration.py` | Integrates consumption metrics with telemetry |
| `signal_contract_validator.py` | Validates signal contracts against specs |
| `signal_validation_specs.py` | Signal validation specifications |
| `signal_semantic_context.py` | Semantic context extraction from signals |
| `signal_semantic_expander.py` | Expands signals with semantic enrichment |
| `signal_context_scoper.py` | Scopes signals to execution context |
| `signal_evidence_extractor.py` | Extracts evidence from resolved signals |
| `signal_enhancement_integrator.py` | Integrates enhancements into executor flow |
| `signal_intelligence_layer.py` | AI-augmented signal processing |
| `signal_method_metadata.py` | Method-level signal metadata |
| `signal_quality_metrics.py` | Signal quality scoring |
| `signal_scoring_context.py` | Context for signal-aware scoring |
| `signal_wiring_fixes.py` | Wiring corrections and patches |
| `pdt_quality_integration.py` | PDT quality integration with signals |

### 4.3 Signal Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SISAS SIGNAL IRRIGATION FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│ questionnaire_      │
│ monolith.json       │──────┐
│ (300 questions)     │      │
└─────────────────────┘      │
                             ▼
                    ┌─────────────────────┐
                    │   signal_loader.py  │
                    │   Parse signal_     │
                    │   requirements      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  signal_registry.py │
                    │  Build Q_id →       │
                    │  Signal[] mapping   │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│signal_semantic_ │  │signal_context_  │  │signal_evidence_ │
│context.py       │  │scoper.py        │  │extractor.py     │
│Extract semantic │  │Scope to current │  │Extract evidence │
│context          │  │execution        │  │patterns         │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                     │                     │
         └──────────┬──────────┴──────────┬──────────┘
                    │                     │
                    ▼                     ▼
         ┌─────────────────────┐  ┌─────────────────────┐
         │signal_resolution.py │  │signal_semantic_     │
         │Resolve to concrete  │  │expander.py          │
         │values               │  │Expand with synonyms │
         └──────────┬──────────┘  └──────────┬──────────┘
                    │                        │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │ signal_enhancement_ │
                    │ integrator.py       │
                    │ Build Enriched      │
                    │ SignalPack          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  phase2_w_factory   │
                    │  (DI Factory)       │
                    │  Inject into        │
                    │  executor context   │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Executor Q001   │  │ Executor Q002   │  │ Executor Q300   │
│ + SignalPack    │  │ + SignalPack    │  │ + SignalPack    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                     │                     │
         └──────────┬──────────┴──────────┬──────────┘
                    │                     │
                    ▼                     ▼
         ┌─────────────────────┐  ┌─────────────────────┐
         │signal_consumption.py│  │signal_quality_     │
         │Track consumption    │  │metrics.py          │
         │per executor         │  │Compute hit rate    │
         └─────────────────────┘  └─────────────────────┘
```

### 4.4 Signal Integration in Phase 2

The `phase2_t_irrigation_synchronizer.py` module is the **primary integration point** between SISAS and Phase 2 execution:

```python
# Simplified irrigation flow (phase2_t_irrigation_synchronizer.py)

def generate_execution_plan(cpp: CanonPolicyPackage, 
                            signal_registry: SignalRegistry) -> ExecutionPlan:
    """
    Subfase 2.1.0 - JOIN Table Construction (optional)
    Subfase 2.1.1 - Question Extraction (300 from monolith)
    Subfase 2.1.2 - Iteration Setup
    Subfase 2.1.3 - Chunk Routing (Q → Chunk via ChunkMatrix)
    Subfase 2.1.4 - Pattern Filtering
    Subfase 2.1.5 - Signal Resolution (SISAS integration point)
    Subfase 2.1.6 - Schema Validation
    Subfase 2.1.7 - Task Construction
    Subfase 2.1.8 - Plan Assembly
    """
    tasks = []
    for question in extract_questions(monolith):  # 300 questions
        chunk = route_to_chunk(question, chunk_matrix)  # Subfase 2.1.3
        
        # SISAS Integration (Subfase 2.1.5)
        signals = signal_registry.get_signals_for_chunk(
            chunk=chunk,
            requirements=question.signal_requirements
        )
        
        task = ExecutableTask(
            question_id=question.id,
            chunk=chunk,
            signals=signals,  # Enriched context
            patterns=filter_patterns(question)
        )
        tasks.append(task)
    
    return ExecutionPlan(
        tasks=sorted(tasks, key=lambda t: t.task_id),
        plan_id=sha256(serialize(tasks)),
        integrity_hash=blake3(tasks)
    )
```

### 4.5 Signal Hit Rate Invariant

**Invariant**: Signal hit rate ≥ 95%

```
Hit Rate = (Signals Resolved / Signals Required) × 100

If Hit Rate < 95%:
    - Log WARNING with unresolved signals
    - Continue execution (graceful degradation)
    - Mark result with reduced confidence
```

---

## 5. Execution Semantics

### 5.1 Five-Stage Transformation Pipeline

#### Stage 1: Irrigation & Synchronization (t, u, v)

**Input**: CanonPolicyPackage (60 chunks), SignalRegistry  
**Output**: ExecutionPlan (300 tasks)

**Process**:
1. Build ChunkMatrix from 60 chunks (validate uniqueness)
2. Extract 300 questions from questionnaire_monolith
3. Route each question to its chunk via (dimension, policy_area) lookup
4. Resolve signals via SISAS for each question-chunk pair
5. Construct ExecutableTask with enriched context
6. Assemble ExecutionPlan with deterministic ordering
7. Compute plan_id (SHA-256) and integrity_hash (BLAKE3)

**Invariants**:
- Exactly 60 unique chunks
- Exactly 300 tasks generated
- plan_id deterministic for identical inputs

#### Stage 2: Contract Loading & Validation (z, e, b)

**Input**: ExecutionPlan  
**Output**: Validated contracts with method bindings

**Process**:
1. For each task, load contract from `specialized/Q{i:03d}.v3.json`
2. Verify SHA-256 matches manifest
3. Validate against JSON Schema (executor_contract.v3.schema.json)
4. Compute CQVR score
5. Extract method_binding (1–17 methods per contract)

**Invariants**:
- All 300 contracts load successfully
- CQVR score computed for each
- No schema violations

#### Stage 3: Method Execution (a, o, w, x, p, q, r, s)

**Input**: Validated contracts, enriched contexts  
**Output**: Method outputs with provenance

**Process**:
1. Factory (w) initializes dependencies (questionnaire, signal registry, method executor)
2. For each contract, for each method in priority order:
   a. Retrieve from MethodRegistry (o) via ClassRegistry (x)
   b. Route arguments via ArgRouter (a)
   c. Execute with seed=42
   d. Profile via ExecutorProfiler (p)
   e. Instrument via Mixin (q)
   f. Collect output with provenance

**Invariants**:
- Methods execute in ascending priority order
- All required arguments present
- Execution time ≤ 5000ms (99th percentile)

#### Stage 4: Evidence Assembly (f)

**Input**: Method outputs  
**Output**: EvidenceGraph

**Process**:
1. Transform outputs to EvidenceNode objects (SHA-256 hashed)
2. Construct DAG with causal/support/contradiction edges
3. Infer edge probabilities via Bayesian analysis
4. Validate acyclicity (topological sort)
5. Apply Dempster-Shafer belief propagation

**Invariants**:
- INV-001: All nodes have SHA-256 hash
- INV-002: Graph is acyclic
- INV-003: Beliefs in [0,1]

#### Stage 5: Narrative Synthesis (c, d)

**Input**: EvidenceGraph, contract  
**Output**: Phase2QuestionResult

**Process**:
1. Interpret contract semantics
2. Analyze evidence gaps
3. Calibrate confidence via CalibrationPolicy (d)
4. Render narrative in Carver style
5. Enforce citation completeness

**Invariants**:
- INV-004: Every claim has ≥1 citation
- INV-005: Confidence intervals calibrated (95% CI)

### 5.2 Determinism Properties

| Property | Implementation |
|----------|----------------|
| Random seed | `PHASE2_RANDOM_SEED=42` applied to Python RNG, NumPy, PyTorch |
| Execution order | Tasks sorted by task_id lexicographically |
| Dictionary iteration | `sorted(dict.items())` where order matters |
| Hash stability | SHA-256/BLAKE3 with deterministic serialization |
| Timestamp handling | UTC-only, ISO 8601 format |

---

## 6. Contract Architecture

### 6.1 Contract Enumeration Formula

```
Q_id = (dim - 1) × 50 + (q - 1) × 10 + pa

Where:
  dim ∈ {1, 2, 3, 4, 5, 6}     (D1–D6)
  q   ∈ {1, 2, 3, 4, 5}        (Q1–Q5 per dimension)
  pa  ∈ {1, 2, ..., 10}        (PA01–PA10)

Example:
  D3-Q4, PA07 → (3-1)×50 + (4-1)×10 + 7 = 100 + 30 + 7 = 137 → Q137
```

### 6.2 Contract Schema (v3)

```json
{
  "identity": {
    "question_id": "Q137",
    "base_slot": "D3-Q4",
    "dimension_id": "DIM03",
    "policy_area_id": "PA07",
    "contract_version": "3.0.0",
    "contract_hash": "<SHA-256>"
  },
  "method_binding": {
    "orchestration_mode": "multi_method_pipeline",
    "method_count": 12,
    "methods": [
      {"class_name": "TextMiningEngine", "method_name": "extract_patterns", "priority": 1},
      {"class_name": "CausalExtractor", "method_name": "infer_causality", "priority": 2},
      ...
    ]
  },
  "evidence_assembly": {
    "module": "phase2_f_evidence_nexus",
    "merge_strategy": "dempster_shafer"
  },
  "output_contract": {
    "schema": "Phase2QuestionResult.v1.schema.json"
  }
}
```

---

## 7. Validation & Compliance

### 7.1 Dura Lex Contractual Tests (15)

| ID | Assertion | Module | Threshold |
|----|-----------|--------|-----------|
| DL-01 | Contract schema conformance | e | 100% |
| DL-02 | Method binding completeness | o, x | 100% |
| DL-03 | Deterministic execution | z | SHA-256 match |
| DL-04 | Evidence graph acyclicity | f | 100% |
| DL-05 | Confidence calibration | c, d | 95% CI coverage ≥ 94% |
| DL-06 | Citation completeness | c | ≥1 per claim |
| DL-07 | Output schema conformance | z | 100% |
| DL-08 | Provenance integrity | f | SHA-256 verified |
| DL-09 | Execution time bounds | p | 99th pctl ≤ 5000ms |
| DL-10 | Memory footprint | l, k | Peak RSS ≤ 2GB |
| DL-11 | Contract immutability | e | Hash match |
| DL-12 | SISAS signal integrity | t | Hit rate ≥ 95% |
| DL-13 | Chunk synchronization | v | 60 chunks assigned |
| DL-14 | Priority ordering | a | Ascending |
| DL-15 | Error handling | all | No silent failures |

### 7.2 Verification Commands

```bash
# Verify all Phase 2 files have PHASE_LABEL
python verify_phase2_labels.py
# Exit 0 = compliant, Exit 1 = violations

# Run Dura Lex tests
pytest tests/dura_lex/ -m phase2 -v

# Validate contract integrity
python -m farfan_pipeline.phases.Phase_two.phase2_e_contract_validator_cqvr \
    --contracts executor_contracts/specialized/
```

---

## 8. Auxiliary Resources

### 8.1 Scripts Directory

| Script | Purpose |
|--------|---------|
| `scripts/generate_all_executor_configs.py` | Batch configuration generation |
| `scripts/generate_all_executor_configs_complete.py` | Complete config with all options |
| `scripts/generate_executor_configs.py` | Single config generator |
| `scripts/create_all_executor_configs.sh` | Shell automation wrapper |

### 8.2 Supporting Directories

| Directory | Contents |
|-----------|----------|
| `json_files_phase_two/` | Contract templates and schemas |
| `contracts/` | Runtime contract artifacts |
| `scripts/` | Generator scripts (auxiliary) |

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.1.0 | 2025-12-20 | Normalized 29 modules (a–z, aa–ac); added PHASE_LABEL to all; removed legacy duplicates; comprehensive SISAS documentation |
| 3.0.0 | 2025-12-17 | Contract-driven architecture; 300 Q contracts; CQVR validation |
| 2.0.0 | 2025-11-01 | Multi-method synthesis; EvidenceNexus |
| 1.0.0 | 2025-10-01 | Initial implementation |

---

## 10. References

1. Christensen, G., & Miguel, E. (2018). Transparency, reproducibility, and the credibility of economics research. *Journal of Economic Literature*, 56(3), 920-980.
2. Freese, J., & Peterson, D. (2017). Replication in social science. *Annual Review of Sociology*, 43, 147-165.
3. Meyer, B. (1992). Applying "design by contract". *Computer*, 25(10), 40-51.
4. Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press.
5. Shafer, G. (1976). *A mathematical theory of evidence*. Princeton University Press.

---

*Document generated: 2025-12-20*  
*Maintainer: F.A.R.F.A.N Policy Pipeline Team*  
*Verification: `python verify_phase2_labels.py`*  
*Inventory Hash: Computed at verification time*
