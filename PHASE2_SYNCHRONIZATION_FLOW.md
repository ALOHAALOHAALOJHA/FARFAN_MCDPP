# PHASE 2: SYNCHRONIZATION FLOW DIAGRAM
## 60 Chunks → 300 Contracts → 300 Tasks → SISAS Integration

**Date**: 2025-12-18  
**Status**: ✅ VERIFIED

---

## COMPLETE SYNCHRONIZATION FLOW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PHASE 1: SPC INGESTION                         │
│                                                                         │
│  PDF Document → Preprocessing → Chunking → CanonPolicyPackage          │
│                                                                         │
│  Output: 60 chunks (10 PA × 6 DIM)                                     │
│  - PA01-PA10 (Policy Areas)                                            │
│  - DIM01-DIM06 (Dimensions)                                            │
│  - Each chunk: {chunk_id, policy_area_id, dimension_id, text}         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       CHUNK MATRIX CONSTRUCTION                          │
│                     (synchronization.py: ChunkMatrix)                    │
│                                                                         │
│  60 chunks organized by coordinates:                                    │
│                                                                         │
│        DIM01    DIM02    DIM03    DIM04    DIM05    DIM06              │
│  PA01    ■        ■        ■        ■        ■        ■                │
│  PA02    ■        ■        ■        ■        ■        ■                │
│  PA03    ■        ■        ■        ■        ■        ■                │
│  PA04    ■        ■        ■        ■        ■        ■                │
│  PA05    ■        ■        ■        ■        ■        ■                │
│  PA06    ■        ■        ■        ■        ■        ■                │
│  PA07    ■        ■        ■        ■        ■        ■                │
│  PA08    ■        ■        ■        ■        ■        ■                │
│  PA09    ■        ■        ■        ■        ■        ■                │
│  PA10    ■        ■        ■        ■        ■        ■                │
│                                                                         │
│  Each ■ = 1 chunk with text content                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    300 EXECUTOR CONTRACTS LOADED                         │
│          (executor_contracts/specialized/Q001-Q300.v3.json)             │
│                                                                         │
│  Each contract defines:                                                 │
│  - question_id: Q001-Q300                                              │
│  - policy_area_id: PA01-PA10                                           │
│  - dimension_id: DIM01-DIM06                                           │
│  - method_binding.methods[]: List of analytical methods                │
│  - patterns[]: Search patterns                                         │
│  - expected_elements[]: Output requirements                            │
│                                                                         │
│  Example: Q001.v3.json                                                 │
│  {                                                                     │
│    "identity": {                                                       │
│      "question_id": "Q001",                                            │
│      "policy_area_id": "PA01",                                         │
│      "dimension_id": "DIM01",                                          │
│      "base_slot": "D1-Q1"  ← legacy, ignored                          │
│    },                                                                  │
│    "method_binding": {                                                 │
│      "methods": [                                                      │
│        {"class_name": "TextMiningEngine", "method_name": "...", ...}, │
│        {"class_name": "IndustrialPolicyProcessor", ...},              │
│        ...                                                             │
│      ]                                                                 │
│    }                                                                   │
│  }                                                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     QUESTIONNAIRE MONOLITH LOADED                        │
│                (canonic_questionnaire_central/questionnaire_monolith)    │
│                                                                         │
│  300 questions with metadata:                                           │
│  - id or question_id: Q001-Q300                                        │
│  - dimension_id: DIM01-DIM06                                           │
│  - policy_area_id: PA01-PA10                                           │
│  - question_text: Natural language question                            │
│  - patterns[]: Search patterns                                         │
│  - expected_elements[]: Output structure                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    IRRIGATION SYNCHRONIZER                               │
│              (irrigation_synchronizer.py: IrrigationSynchronizer)        │
│                                                                         │
│  1. Load 300 questions from monolith                                   │
│  2. Match each question to its chunk via (PA, DIM) coordinates         │
│  3. Generate 300 tasks (1 per question)                                │
│  4. Create ExecutionPlan with deterministic plan_id                    │
│  5. Compute integrity_hash (Blake3) for verification                   │
│  6. Emit SISAS signal with plan metadata                               │
│                                                                         │
│  Task Generation:                                                       │
│    for question in questions:                                          │
│      chunk = chunk_matrix.get_chunk(                                   │
│        question.policy_area_id,                                        │
│        question.dimension_id                                           │
│      )                                                                 │
│      task = Task(                                                      │
│        task_id=f"{question.question_id}_{PA}_{chunk_id}",            │
│        question_id=question.question_id,  # Q001-Q300                 │
│        policy_area=question.policy_area_id,                           │
│        dimension=question.dimension_id,                               │
│        chunk_id=chunk.chunk_id,                                       │
│        chunk_index=chunk.index,                                       │
│        question_text=question.question_text                           │
│      )                                                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXECUTION PLAN (300 TASKS)                       │
│                                                                         │
│  ExecutionPlan:                                                         │
│  - plan_id: "plan_20251218_..."  (deterministic)                      │
│  - tasks: [Task1, Task2, ..., Task300]                                │
│  - chunk_count: 60                                                     │
│  - question_count: 300                                                 │
│  - integrity_hash: "abc123..."  (Blake3)                              │
│  - correlation_id: UUID for tracking                                   │
│                                                                         │
│  Each Task:                                                            │
│  - task_id: "Q001_PA01_chunk-001"                                     │
│  - question_id: "Q001"  ← KEY: Used for contract loading              │
│  - policy_area: "PA01"                                                 │
│  - dimension: "DIM01"                                                  │
│  - chunk_id: "PA01-DIM01"                                             │
│  - chunk_index: 0                                                      │
│  - question_text: "..."                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          SISAS SIGNAL EMISSION                           │
│              (irrigation_synchronizer.py: emit_sisas_signal())           │
│                                                                         │
│  Signal Data:                                                           │
│  {                                                                     │
│    "plan_id": "plan_20251218_...",                                     │
│    "task_count": 300,                                                  │
│    "chunk_matrix": {                                                   │
│      "rows": ["PA01", "PA02", ..., "PA10"],                           │
│      "cols": ["DIM01", "DIM02", ..., "DIM06"],                        │
│      "cells": {...}  # PA × DIM chunk mappings                        │
│    },                                                                  │
│    "integrity_hash": "abc123...",                                     │
│    "timestamp": 1734567890.123                                        │
│  }                                                                     │
│                                                                         │
│  → Sent to SISAS (Satellital Irrigation Smart Adaptive System)         │
│  ← SISAS returns adjusted irrigation parameters                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR EXECUTION                           │
│              (orchestrator.py: _execute_micro_questions_async)           │
│                                                                         │
│  For each Task in ExecutionPlan.tasks:                                 │
│                                                                         │
│  1. Extract question_id from Task                                      │
│     question_id = task.question_id  # e.g., "Q001"                    │
│                                                                         │
│  2. Lookup full question data from monolith                            │
│     question = _lookup_question_from_plan_task(task, config)          │
│     # Returns question dict with all metadata                          │
│                                                                         │
│  3. Get question ID for contract loading                               │
│     qid = question.get("id") or question.get("question_id")           │
│     # qid = "Q001"                                                     │
│                                                                         │
│  4. Instantiate GenericContractExecutor                                │
│     executor = GenericContractExecutor(                                │
│       question_id=qid,  # "Q001"                                      │
│       method_executor=self.executor,                                   │
│       signal_registry=...,                                            │
│       config=self.executor_config,                                    │
│       questionnaire_provider=self._canonical_questionnaire,           │
│       calibration_orchestrator=...,                                   │
│       enriched_packs=...                                              │
│     )                                                                  │
│                                                                         │
│  5. Execute task                                                       │
│     result = executor.execute(                                         │
│       document=document,                                               │
│       method_executor=self.executor,                                   │
│       question_context={...}                                          │
│     )                                                                  │
│                                                                         │
│  6. Collect CarverAnswer                                               │
│     results.append(MicroQuestionRun(...))                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    GENERIC CONTRACT EXECUTOR                             │
│          (executors/generic_contract_executor.py)                        │
│                                                                         │
│  def __init__(self, question_id, ...):                                 │
│    self._question_id = question_id  # "Q001"                          │
│                                                                         │
│  def execute(self, **kwargs):                                          │
│    # Load contract from specialized/ directory                         │
│    contract = self._load_contract(question_id=self._question_id)      │
│    # Reads: executor_contracts/specialized/Q001.v3.json                │
│                                                                         │
│    # Extract methods from contract                                     │
│    methods = contract["method_binding"]["methods"]                     │
│                                                                         │
│    # Execute each method via MethodExecutor                            │
│    for method in methods:                                              │
│      result = method_executor.execute(                                 │
│        class_name=method["class_name"],                                │
│        method_name=method["method_name"],                              │
│        arguments=...                                                   │
│      )                                                                 │
│                                                                         │
│    # Assemble evidence via EvidenceNexus                               │
│    evidence_graph = EvidenceNexus.build_graph(results)                │
│                                                                         │
│    # Synthesize narrative via DoctoralCarverSynthesizer                │
│    carver_answer = DoctoralCarverSynthesizer.synthesize(              │
│      evidence=evidence_graph,                                          │
│      question=question_context,                                        │
│      confidence=...                                                    │
│    )                                                                   │
│                                                                         │
│    return carver_answer                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       300 CARVER ANSWERS GENERATED                       │
│                                                                         │
│  Each CarverAnswer contains:                                            │
│  - response_text: PhD-level analytical response                        │
│  - confidence: float [0.0, 1.0]                                        │
│  - evidence_citations: List[str] (node IDs from evidence graph)       │
│  - gap_analysis: Dict[str, Any] (dimensional gaps)                    │
│  - metadata: Dict[str, Any] (execution metrics)                        │
│                                                                         │
│  Output: ExecutorResults for Phase 3 Scoring                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                               PHASE 3 →
```

---

## KEY SYNCHRONIZATION POINTS

### 1. Chunk-to-Question Mapping

**Mechanism**: `ChunkMatrix.get_chunk(policy_area_id, dimension_id)`

**Invariant**: Each (PA, DIM) coordinate has exactly 1 chunk

**Example**:
- Question Q001 has policy_area_id="PA01", dimension_id="DIM01"
- ChunkMatrix.get_chunk("PA01", "DIM01") returns chunk with matching coordinates
- Task links question Q001 to this chunk

### 2. Question-to-Contract Mapping

**Mechanism**: `GenericContractExecutor(question_id)`

**Invariant**: Each question_id (Q001-Q300) has exactly 1 contract file

**Example**:
- Question ID: "Q001"
- Contract file: `executor_contracts/specialized/Q001.v3.json`
- GenericContractExecutor loads this file automatically

### 3. Task-to-Execution Mapping

**Mechanism**: Orchestrator iterates ExecutionPlan.tasks

**Invariant**: Each task executed exactly once (ignoring retries)

**Example**:
- Task: {task_id="Q001_PA01_chunk-001", question_id="Q001", ...}
- Orchestrator: Creates GenericContractExecutor(question_id="Q001")
- Executor: Loads Q001.v3.json, executes methods, returns CarverAnswer

---

## SYNCHRONIZATION VERIFICATION

### Audit Points

1. ✅ **60 chunks** in ChunkMatrix (10 PA × 6 DIM)
2. ✅ **300 contracts** in specialized/ directory
3. ✅ **300 questions** in monolith
4. ✅ **300 tasks** in ExecutionPlan
5. ✅ **Task.question_id** format: Q001-Q300
6. ✅ **Contract.identity.question_id** format: Q001-Q300
7. ✅ **Question.id** format: Q001-Q300
8. ✅ **GenericContractExecutor** uses question_id for loading
9. ✅ **No hardcoded executor dictionary** in orchestrator
10. ✅ **SISAS signal** emitted with plan metadata

### Verification Commands

```bash
# Run audit script
python3.12 audit_phase2_wiring.py

# Check contract count
ls src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/*.v3.json | wc -l

# Check GenericContractExecutor exists
ls src/farfan_pipeline/phases/Phase_two/executors/generic_contract_executor.py

# Check executors.py deleted
ls src/farfan_pipeline/phases/Phase_two/executors/executors.py  # Should error

# Run Dura Lex tests
python3.12 run_phase2_duralex_tests.py
```

---

## IMPORTANT NOTES

### Question ID Format Consistency

All three sources MUST use the same question_id format:

1. **Contracts**: `identity.question_id = "Q001"`
2. **Monolith**: `question.id = "Q001"` or `question.question_id = "Q001"`
3. **Tasks**: `task.question_id = "Q001"`

If these don't match, orchestrator cannot find questions or contracts.

### Legacy Fields Ignored

Contracts still have `executor_binding.executor_class = "D1_Q1_Executor"` but this is **completely ignored** by GenericContractExecutor. Only `identity.question_id` is used.

### SISAS Coordination

SISAS signal is emitted AFTER ExecutionPlan generation but BEFORE task execution. This allows SISAS to adjust irrigation parameters before processing begins.

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-18  
**Verified By**: audit_phase2_wiring.py
