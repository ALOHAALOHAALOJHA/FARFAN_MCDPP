# PHASE 2: COMPREHENSIVE SPECIFICATION
## Question Execution & Analysis - F.A.R.F.A.N Mechanistic Pipeline

**Version**: 2.1.0  
**Date**: 2025-12-17  
**Status**: ✅ CONTRACT-DRIVEN EXECUTION  
**Repository**: victorelsalvadorveneco/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL

---

## TABLE OF CONTENTS

1. [Overview](#1-overview)
2. [Architectural Role](#2-architectural-role)
3. [Node Structure](#3-node-structure)
4. [Contracts & Types](#4-contracts--types)
5. [Execution Flow](#5-execution-flow)
6. [SISAS Integration](#6-sisas-integration)
7. [Error Handling](#7-error-handling)
8. [Integration Points](#8-integration-points)
9. [Testing & Verification](#9-testing--verification)
10. [File Manifest](#10-file-manifest)

---

## 1. OVERVIEW

### 1.1 Purpose

Phase 2 is the **Question Execution & Analysis Engine** that processes 309 questions through **direct contract-driven execution**. Each question has its own contract (Q001-Q309.v3.json) that defines methods, evidence assembly, and output requirements. It acts as the **Core Analytical Processor** that transforms policy document chunks into PhD-level analytical responses.

### 1.2 Core Responsibilities

1. ✅ **Contract-Driven Execution** - Direct loading of 309 contracts (Q001-Q309.v3.json)
2. ✅ **Method Orchestration** - Execute 240+ analytical methods via MethodExecutor
3. ✅ **Evidence Assembly** - Build causal evidence graphs with EvidenceNexus
4. ✅ **Narrative Synthesis** - Generate PhD-level responses via DoctoralCarverSynthesizer
5. ✅ **SISAS Integration** - Coordinate with satellital component for smart irrigation
6. ✅ **Schema Validation** - Validate question-chunk schema compatibility
7. ✅ **Execution Planning** - Generate deterministic execution plans
8. ✅ **Quality Scoring** - Capture runtime metrics and calibration scores
9. ✅ **Dura Lex Compliance** - 15 contractual tests with certificates

### 1.3 Design Principles

- **Contract-Driven**: ALL execution through individual JSON contracts (NO hardcoded executor classes)
- **Deterministic**: Same inputs produce identical outputs via ExecutionPlan with integrity_hash
- **Observable**: All operations logged with correlation_id tracking through 10 phases
- **Verifiable**: Evidence graphs ensure traceability of analytical claims + 15 Dura Lex certificates
- **Generic**: BaseExecutorWithContract handles ALL 300 questions dynamically via question_id

---

## 2. ARCHITECTURAL ROLE

### 2.1 Position in Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                         PIPELINE FLOW                            │
└──────────────────────────────────────────────────────────────────┘

[PHASE 0: BOOTSTRAP]
        ↓ CanonicalInput
[PHASE 1: INGESTION] 
        ↓ CanonPolicyPackage (60 chunks)
┌───────────────────────┐
│   PHASE 2: ANALYSIS   │ ← YOU ARE HERE
│   Question Execution  │
├───────────────────────┤
│ • Route 300 questions │
│ • Execute contracts   │
│ • Assemble evidence   │
│ • Synthesize answers  │
│ • SISAS coordination  │
└───────┬───────────────┘
        ↓ ExecutorResults (300 responses)
┌───────────────────────┐
│   PHASE 3: SCORING    │
│   Quality Assessment  │
└───────────────────────┘
```

### 2.2 Relationship to Other Phases

**Predecessor**: Phase 1 (SPC Ingestion)  
**Successor**: Phase 3 (Scoring & Aggregation)

**Contract Bridge**:
- **Consumes**: `CanonPolicyPackage` (60 chunks from Phase 1)
- **Produces**: `ExecutorResults` (300 analytical responses)
- **Enforcement**: Contract validators ensure format compliance at boundaries

### 2.3 Execution Model

Phase 2 operates on a **300-task execution model**:
- **30 base questions** (D1-D6, Q1-Q5): 6 dimensions × 5 questions
- **10 policy areas**: PA01-PA10 (territorial development categories)
- **Total tasks**: 30 × 10 = 300 question executions

Each task consists of:
1. Question routing via arg_router
2. Contract loading and validation
3. Method execution through MethodExecutor
4. Evidence assembly via EvidenceNexus
5. Narrative synthesis via DoctoralCarverSynthesizer
6. Result packaging with metadata

---

## 3. NODE STRUCTURE

### 3.1 Conceptual Nodes

Phase 2 consists of **5 logical nodes** executed sequentially per question:

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 2: NODE GRAPH                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  NODE 2.0       │
│  SYNCHRONIZATION│
├─────────────────┤
│ • Generate plan │
│ • Map Q→Chunk   │
│ • Build matrix  │
│ • SISAS signal  │
└────────┬────────┘
         │
         ↓ ExecutionPlan (300 tasks)
┌─────────────────┐
│  NODE 2.1       │
│  ROUTING        │
├─────────────────┤
│ • Load contract │
│ • Validate args │
│ • Route methods │
│ • Config params │
└────────┬────────┘
         │
         ↓ RoutedExecution
┌─────────────────┐
│  NODE 2.2       │
│  METHOD EXEC    │
├─────────────────┤
│ • Execute 240+  │
│   methods       │
│ • Capture time  │
│ • Track memory  │
│ • Handle errors │
└────────┬────────┘
         │
         ↓ MethodResults
┌─────────────────┐
│  NODE 2.3       │
│  EVIDENCE       │
├─────────────────┤
│ • Build graph   │
│ • Infer edges   │
│ • Validate cons.│
│ • Hash chain    │
└────────┬────────┘
         │
         ↓ EvidenceGraph
┌─────────────────┐
│  NODE 2.4       │
│  SYNTHESIS      │
├─────────────────┤
│ • Interpret     │
│ • Analyze gaps  │
│ • Calibrate conf│
│ • Render prose  │
└────────┬────────┘
         │
         ↓ CarverAnswer (PhD-level response)
```

### 3.2 Node 2.0: Synchronization & Planning

**Location**: `irrigation_synchronizer.py` (`IrrigationSynchronizer.build_with_chunk_matrix()`)

**Purpose**: Generate deterministic execution plan mapping questions to chunks with SISAS coordination

**Operations**:
1. Extract policy areas and dimensions from chunks
2. Build ChunkMatrix (PA × DIM mapping)
3. Generate 300 tasks with deterministic ordering
4. Compute ExecutionPlan with integrity_hash (Blake3)
5. Emit SISAS signal for smart irrigation coordination
6. Validate schema compatibility (schema_validation.py)

**Inputs**:
- `chunks: List[PolicyChunk]` (60 chunks from Phase 1)
- `questionnaire: Dict[str, Any]` (30 base questions)

**Outputs**:
- `ExecutionPlan` with 300 tasks, plan_id, integrity_hash
- Task structure: `{question_id, chunk_id, policy_area, dimension}`

**Exit Conditions**:
- Success: All 300 tasks generated, plan_id stable
- Failure: Schema mismatch, missing PA/DIM, integrity hash collision

### 3.3 Node 2.1: Contract Routing

**Location**: `arg_router.py` (`ExtendedArgRouter.route()`)

**Purpose**: Load contract, validate arguments, and route to appropriate executor

**Operations**:
1. Detect contract version (v2 vs v3) from file name and structure
2. Load executor-specific contract from `json_files_phase_two/executor_contracts/`
3. Validate required arguments against contract method_inputs
4. Handle special routes for high-traffic methods (30+ predefined)
5. Load ExecutorConfig (runtime parameters: timeout, retry, memory limits)
6. Fail-fast on missing arguments or unexpected parameters

**Inputs**:
- `question: Dict[str, Any]`
- `chunk: PolicyChunk`
- `contract_path: Path`

**Outputs**:
- `RoutedExecution` with validated args and executor reference
- `ExecutorConfig` with runtime parameters

**Exit Conditions**:
- Success: Args validated, executor class resolved
- Failure: ArgumentValidationError, missing contract, unsupported version

### 3.4 Node 2.2: Method Execution

**Location**: `executors/base_executor_with_contract.py` (`BaseExecutorWithContract.execute()`)

**Purpose**: Execute 240+ analytical methods through MethodExecutor

**Operations**:
1. Parse contract method_binding.methods (up to 15 methods per question)
2. Route each method through MethodExecutor with validated signatures
3. Capture runtime metrics (start_time, memory_usage)
4. Enforce resource limits (timeout, max_memory_mb)
5. Handle partial results on non-critical failures
6. Track calibration scores if calibration_orchestrator present

**Inputs**:
- `contract: Dict[str, Any]` (v2 or v3 format)
- `context: Dict[str, Any]` (chunk, questionnaire, config)

**Outputs**:
- `MethodResults` with outputs from each method
- Runtime metrics (execution_time_ms, memory_delta_mb)

**Exit Conditions**:
- Success: All methods executed or partial results acceptable
- Failure: Critical method failure, timeout exceeded, memory limit

### 3.5 Node 2.3: Evidence Assembly

**Location**: `evidence_nexus.py` (`EvidenceNexus.build_graph()`)

**Purpose**: Construct causal evidence graph with Bayesian inference

**Operations**:
1. Ingest method results as typed evidence nodes
2. Infer causal edges via Bayesian inference (Dempster-Shafer belief functions)
3. Detect graph cycles (must be acyclic for causal reasoning)
4. Compute SHA-256 content hashes for provenance
5. Validate consistency via graph-theoretic conflict detection
6. Build Merkle DAG with content-addressable storage

**Inputs**:
- `method_results: List[MethodResult]`
- `question_context: Dict[str, Any]`

**Outputs**:
- `EvidenceGraph` with nodes, edges, and confidence weights
- Hash chain for append-only verification

**Exit Conditions**:
- Success: Graph acyclic, all nodes hashed, consistency validated
- Failure: Cycle detected, hash collision, confidence calibration failure

### 3.6 Node 2.4: Narrative Synthesis

**Location**: `carver.py` (`DoctoralCarverSynthesizer.synthesize()`)

**Purpose**: Generate PhD-level analytical response with Carver-style minimalism

**Operations**:
1. Interpret contract semantics (ContractInterpreter)
2. Analyze dimensional gaps (D1-D6 strategies)
3. Compute Bayesian confidence intervals (calibrated)
4. Render prose with Rhetorical Structure Theory
5. Enforce invariants: ≥1 evidence per claim, gaps explicit, no adverbs
6. Generate macro synthesis with PA×DIM divergence analysis

**Inputs**:
- `evidence_graph: EvidenceGraph`
- `contract: Dict[str, Any]`
- `dimension: str` (D1-D6)

**Outputs**:
- `CarverAnswer` with response_text, confidence, evidence_citations, gap_analysis

**Exit Conditions**:
- Success: All claims cited, confidence calibrated, Carver style enforced
- Failure: Uncited claim, invalid confidence, style violation

---

## 4. CONTRACTS & TYPES

### 4.1 Contract Formats

Phase 2 supports **two contract versions**:

**Contract v2 (Legacy)**:
```json
{
  "question_id": "Q001",
  "method_inputs": [...],
  "assembly_rules": {...},
  "validation_rules": {...}
}
```

**Contract v3 (Current)**:
```json
{
  "identity": {"contract_id": "...", "version": "3.0.0"},
  "executor_binding": {"executor_class": "D1Q1_Executor_Contract"},
  "method_binding": {"methods": [...]},
  "question_context": {...},
  "evidence_assembly": {...},
  "output_contract": {...},
  "validation_rules": {...}
}
```

Version detection: `*.v3.json` → v3, else v2

### 4.2 Executor Classes

**30 executors** organized by dimension and question:

**D1 (Diagnostics & Inputs)**:
- `D1Q1_Executor_Contract`: Quantitative Baseline Extraction
- `D1Q2_Executor_Contract`: Problem Dimensioning Analysis
- `D1Q3_Executor_Contract`: Budget Allocation Tracing
- `D1Q4_Executor_Contract`: Institutional Capacity Identification
- `D1Q5_Executor_Contract`: Scope Justification Validation

**D2 (Activity Design)**:
- `D2Q1_Executor_Contract`: Structured Planning Validation
- `D2Q2_Executor_Contract`: Intervention Logic Inference
- `D2Q3_Executor_Contract`: Root Cause Linkage Analysis
- `D2Q4_Executor_Contract`: Risk Management Analysis
- `D2Q5_Executor_Contract`: Strategic Coherence Evaluation

**D3 (Products & Outputs)**:
- `D3Q1_Executor_Contract`: Indicator Quality Validation
- `D3Q2_Executor_Contract`: Target Proportionality Analysis
- `D3Q3_Executor_Contract`: Output Specification Validator
- `D3Q4_Executor_Contract`: Technical Feasibility Evaluation
- `D3Q5_Executor_Contract`: Output-Outcome Linkage Analysis

**D4 (Outcomes & Impact)**:
- `D4Q1_Executor_Contract`: Outcome Metrics Validation
- `D4Q2_Executor_Contract`: Causal Chain Validation
- `D4Q3_Executor_Contract`: Ambition Justification Analysis
- `D4Q4_Executor_Contract`: Problem Solvency Evaluation
- `D4Q5_Executor_Contract`: Vertical Alignment Validation

**D5 (Sustainability)**:
- `D5Q1_Executor_Contract`: Long-Term Vision Analysis
- `D5Q2_Executor_Contract`: Composite Measurement Validation
- `D5Q3_Executor_Contract`: Intangible Measurement Analysis
- `D5Q4_Executor_Contract`: Systemic Risk Evaluation
- `D5Q5_Executor_Contract`: Realism & Side Effects Analysis

**D6 (Context & Adaptation)**:
- `D6Q1_Executor_Contract`: Territorial Context Analysis
- `D6Q2_Executor_Contract`: Participatory Process Evaluation
- `D6Q3_Executor_Contract`: Equity & Inclusion Assessment
- `D6Q4_Executor_Contract`: Climate & Environment Integration
- `D6Q5_Executor_Contract`: Contextual Adaptability Evaluation

### 4.3 Key Data Structures

**ExecutionPlan**:
```python
@dataclass
class ExecutionPlan:
    plan_id: str  # Deterministic UUID
    tasks: List[Task]  # 300 tasks
    integrity_hash: str  # Blake3 hash
    metadata: Dict[str, Any]
```

**Task**:
```python
@dataclass
class Task:
    question_id: str  # Q001-Q030
    chunk_id: str  # PA01-DIM01, etc.
    policy_area: str  # PA01-PA10
    dimension: str  # DIM01-DIM06
```

**ExecutorConfig**:
```python
@dataclass
class ExecutorConfig:
    timeout_s: int
    retry_count: int
    memory_limit_mb: int
    temperature: float
    max_tokens: int
```

---

## 5. EXECUTION FLOW

### 5.1 End-to-End Flow

```
1. IrrigationSynchronizer.build_with_chunk_matrix()
   ├─ Extract PA/DIM from 60 chunks
   ├─ Build ChunkMatrix
   ├─ Generate 300 tasks
   ├─ Compute plan_id + integrity_hash
   └─ Emit SISAS signal

2. For each task in ExecutionPlan:
   ├─ ExtendedArgRouter.route()
   │  ├─ Load contract (v2/v3)
   │  ├─ Validate arguments
   │  └─ Load ExecutorConfig
   │
   ├─ BaseExecutorWithContract.execute()
   │  ├─ Parse method_binding
   │  ├─ Execute methods via MethodExecutor
   │  ├─ Capture metrics
   │  └─ Return MethodResults
   │
   ├─ EvidenceNexus.build_graph()
   │  ├─ Ingest evidence nodes
   │  ├─ Infer causal edges
   │  ├─ Validate consistency
   │  └─ Build hash chain
   │
   └─ DoctoralCarverSynthesizer.synthesize()
      ├─ Interpret contract
      ├─ Analyze gaps
      ├─ Compute confidence
      ├─ Render prose
      └─ Return CarverAnswer

3. Collect 300 CarverAnswers → ExecutorResults
```

### 5.2 Error Handling Strategy

**Fail-Fast Errors** (abort execution):
- Contract validation failure (missing fields, invalid schema)
- Argument validation failure (missing required args)
- Cyclic evidence graph (violates causality)
- Timeout exceeded (resource limit)

**Recoverable Errors** (log and continue):
- Non-critical method failure (partial results acceptable)
- Confidence calibration warning (use conservative default)
- Evidence node hash collision (regenerate with salt)

**Error Propagation**:
All errors tagged with correlation_id for tracing through 10 phases.

---

## 6. SISAS INTEGRATION

### 6.1 SISAS Overview

**SISAS** (Sistema de Irrigación Smart Adaptativo Satelital) is the **satellital component for smart irrigation** that coordinates chunk allocation across questions.

**Purpose**: Optimize document chunk distribution to ensure balanced coverage across all 300 questions.

### 6.2 Integration Points

**Signal Emission** (irrigation_synchronizer.py):
```python
# After generating ExecutionPlan
emit_sisas_signal(
    plan_id=plan.plan_id,
    task_count=300,
    chunk_matrix=chunk_matrix
)
```

**Signal Reception**:
SISAS monitors signals and adjusts irrigation parameters:
- Chunk rebalancing if policy area coverage is skewed
- Priority elevation for under-served dimensions
- Resource allocation based on executor load

### 6.3 Coordination Protocol

1. **Phase 2 → SISAS**: Emit plan_id + chunk_matrix
2. **SISAS → Phase 2**: Return adjusted irrigation parameters
3. **Phase 2**: Apply adjustments to task ordering
4. **SISAS**: Monitor execution metrics (time, memory) via Prometheus

**Observability**: All SISAS interactions logged with correlation_id.

---

## 7. ERROR HANDLING

### 7.1 Contract Validation Errors

**Trigger**: Invalid contract structure, missing fields, unsupported version

**Handler**: `BaseExecutorWithContract._load_contract()`

**Response**:
- Log error with contract_path, expected schema, actual schema
- Raise `ContractValidationError`
- Abort executor initialization

### 7.2 Argument Validation Errors

**Trigger**: Missing required argument, unexpected argument (no **kwargs)

**Handler**: `ExtendedArgRouter.validate_arguments()`

**Response**:
- Log error with method signature, provided args, missing args
- Raise `ArgumentValidationError`
- Abort method routing

### 7.3 Method Execution Errors

**Trigger**: Method raises exception, timeout exceeded, memory limit reached

**Handler**: `BaseExecutorWithContract.execute()`

**Response**:
- **Critical method**: Raise exception, abort executor
- **Non-critical method**: Log warning, return partial results
- **Timeout**: Log timeout, return results collected so far
- **Memory limit**: Raise `MemoryLimitExceeded`, abort

### 7.4 Evidence Graph Errors

**Trigger**: Cyclic graph, hash collision, consistency violation

**Handler**: `EvidenceNexus.build_graph()`

**Response**:
- **Cyclic graph**: Raise `CyclicEvidenceGraphError`, cannot perform causal inference
- **Hash collision**: Regenerate hash with salt, retry up to 3 times
- **Consistency violation**: Log warning, mark conflicting nodes

---

## 8. INTEGRATION POINTS

### 8.1 Inputs from Phase 1

**Consumed**:
- `CanonPolicyPackage` with 60 policy chunks
- Each chunk has: `chunk_id`, `policy_area_id`, `dimension_id`, `text`, `metadata`

**Contract Requirements**:
- All chunks must have valid PA01-PA10 and DIM01-DIM06 identifiers
- Text must be non-empty
- Metadata must include page range, section headers

### 8.2 Outputs to Phase 3

**Produced**:
- `ExecutorResults` with 300 CarverAnswers
- Each answer has: `response_text`, `confidence`, `evidence_citations`, `gap_analysis`, `metadata`

**Contract Requirements**:
- All 300 questions must have responses (partial acceptable with flag)
- Confidence must be in [0.0, 1.0]
- Evidence citations must reference valid nodes in graph
- Gap analysis must identify dimensional coverage gaps

### 8.3 Orchestrator Integration

**Wiring** (orchestrator.py):
```python
from canonic_phases.Phase_two import executors

# Executor instantiation
executor_class = getattr(executors, f"D{dim}Q{q}_Executor")
executor = executor_class(
    method_executor=self.method_executor,
    signal_registry=self.signal_registry,
    config=executor_config,
    questionnaire_provider=self.questionnaire_provider
)
```

**Execution**:
```python
result = executor.execute(context={
    "chunk": chunk,
    "questionnaire": questionnaire,
    "policy_area": policy_area
})
```

---

## 9. TESTING & VERIFICATION

### 9.1 Unit Tests

**Location**: `executors/executor_tests.py`

**Coverage**:
- Contract loading (v2 and v3 formats)
- Argument validation
- Method execution
- Evidence graph construction
- Carver synthesis

**Run**: `pytest executors/executor_tests.py -v`

### 9.2 Integration Tests

**Location**: `tests/test_executor_chunk_synchronization.py`, `tests/test_irrigation_synchronizer_join_table_integration.py`

**Coverage**:
- Full 300-task execution
- SISAS signal coordination
- Chunk matrix construction
- ExecutionPlan integrity

**Run**: `pytest tests/test_executor_chunk_synchronization.py -v`

### 9.3 Contract Validation

**Tool**: `contract_validator_cqvr.py`

**Purpose**: Validate all 300 contracts against CQVR (Completeness, Quality, Validity, Rigor) criteria

**Scoring**:
- Tier 1 (55 pts): Completeness (all required fields present)
- Tier 2 (30 pts): Quality (method appropriateness, evidence strategy)
- Tier 3 (15 pts): Rigor (validation rules, error handling)

**Triage Decisions**:
- `PRODUCCION`: Score ≥ 85, ready for production
- `PARCHEAR`: Score 70-84, needs minor fixes
- `REFORMULAR`: Score < 70, needs redesign

---

## 10. FILE MANIFEST

### 10.1 Core Execution Files

| File | Lines | Purpose | Dependencies |
|------|-------|---------|--------------|
| **arg_router.py** | 956 | Argument routing with 30+ special routes, strict validation | inspect, structlog |
| **carver.py** | 1873 | Doctoral-level narrative synthesis with Carver minimalism | statistics, re |
| **evidence_nexus.py** | 2678 | Unified evidence-to-answer engine with causal graphs | hashlib, networkx |
| **irrigation_synchronizer.py** | 2152 | Question→Chunk→Task→Plan coordination with SISAS | hashlib, Prometheus |
| **contract_validator_cqvr.py** | 670 | Contract triage with CQVR scoring (Completeness, Quality, Validity, Rigor) | dataclasses, enum |
| **schema_validation.py** | 505 | Four-subphase schema validation (classification, structural, semantic, orchestrator) | logging |
| **executor_chunk_synchronizer.py** | [relocated] | JOIN table builder for executor-chunk bindings | hashlib, json |
| **synchronization.py** | 301 | Chunk matrix utilities (PA/DIM extraction, validation) | hashlib, logging |

### 10.2 Executor Implementation Files (executors/ subfolder)

| File | Lines | Purpose | Dependencies |
|------|-------|---------|--------------|
| **executors/base_executor_with_contract.py** | 2025 | Base executor class with v2/v3 contract support | jsonschema, ABC |
| **executors/executors.py** | 216 | 30 executor classes (D1-D6, Q1-Q5) with get_base_slot() | base_executor_with_contract |
| **executors/executor_config.py** | 205 | Runtime config dataclass (timeout, retry, memory limits) | dataclasses |
| **executors/executor_instrumentation_mixin.py** | 159 | Mixin for automatic calibration instrumentation | time, psutil |
| **executors/executor_profiler.py** | 1237 | Profiler for capturing runtime metrics (time, memory) | time, tracemalloc |
| **executors/executor_tests.py** | 370 | Integration test suite for executors | pytest, unittest |
| **executors/__init__.py** | 145 | Module exports for all 30 executors | N/A |

### 10.3 Configuration & Scripts

| File | Lines | Purpose |
|------|-------|---------|
| **create_all_executor_configs.sh** | 103 | Bash script to generate all 30 executor config JSON files |
| **generate_all_executor_configs.py** | 138 | Python script to generate executor configs with metadata |
| **generate_all_executor_configs_complete.py** | 382 | Complete config generation with epistemic_mix, methods_count |
| **generate_executor_configs.py** | 179 | Minimal config generator for basic parameters |

### 10.4 Documentation

| File | Lines | Purpose |
|------|-------|---------|
| **EXECUTOR_CALIBRATION_INTEGRATION_README.md** | 352 | Calibration system integration guide (WHAT vs HOW separation) |
| **README.md** | [this file] | Comprehensive Phase 2 specification |

### 10.5 Data Files

| Directory | Purpose |
|-----------|---------|
| **json_files_phase_two/executor_contracts/** | 300 executor contract files (v2 and v3) |
| **json_files_phase_two/executor_factory_validation.json** | Factory validation report |
| **json_files_phase_two/executors_methods.json** | Method signatures for all executors |

### 10.6 Contracts (contracts/certificates/)

| Certificate | Purpose |
|-------------|---------|
| 15 compliance certificates documenting Phase 2 adherence to contractual standards (see Part 6) |

---

## SUMMARY

**Phase 2** is the analytical core of the F.A.R.F.A.N pipeline, processing 300 questions through contract-driven execution with evidence assembly and narrative synthesis. It coordinates with SISAS for smart irrigation, enforces strict schema validation, and produces PhD-level responses through the Doctoral Carver synthesizer.

**Key Metrics**:
- **30 executors** (D1-D6, Q1-Q5)
- **300 questions** (30 base × 10 policy areas)
- **240+ methods** (analytical techniques)
- **60 chunks** (policy document segments)
- **~15,000 lines of code**

**Status**: ✅ Canonicalized and frozen per DURA_LEX enforcement (2025-12-17)
