# Phase 2: Micro-Answer Execution (`phase_2`)

**STATUS:** IN PROGRESS - Canonical refactoring from `farfan_pipeline.phases.Phase_two`

Phase 2 transforms 60 chunks (from Phase 1) into 300 micro-answers through deterministic executor orchestration:

- **Input:** 60 chunks (10 PA × 6 DIM) from Phase 1 CPP
- **Output:** 300 micro-answers (30 base questions × 10 policy areas)
- **Constitutional invariant:** Exactly 300 outputs (cardinality: 60→300)
- **Execution model:** Task-based with retry logic and evidence tracking

## Architecture

### Directory Structure

```
phase_2/
├── constants/
│   └── phase2_constants.py          # Frozen constants (NUM_MICRO_ANSWERS=300)
├── schemas/
│   ├── micro_answer_schema.json     # MicroAnswer output schema
│   ├── execution_plan_schema.json   # ExecutionPlan schema (60→300 mapping)
│   ├── executor_contract_schema.json # ExecutorContract specification
│   └── phase2_output_schema.json    # Phase2Output package schema
├── contracts/
│   ├── certificates/                # 15 contract certificates (CERTIFICATE_01-15)
│   ├── phase2_input_contract.py     # Input validation contract
│   ├── phase2_output_contract.py    # Output validation contract
│   ├── phase2_cardinality_contract.py # 60→300 cardinality enforcement
│   ├── phase2_evidence_contract.py  # Evidence tracking contract
│   ├── phase2_retry_contract.py     # Retry logic contract
│   ├── phase2_cqvr_contract.py      # CQVR quality gate contract
│   ├── phase2_sisas_contract.py     # SISAS synchronization contract
│   └── phase2_executor_contract.py  # Executor binding contract
├── orchestration/
│   ├── phase2_orchestrator.py       # Main orchestration logic
│   ├── phase2_task_scheduler.py     # Task scheduling and distribution
│   ├── phase2_retry_handler.py      # Retry logic with exponential backoff
│   ├── phase2_evidence_tracker.py   # Evidence collection and validation
│   ├── phase2_quality_gate.py       # Quality validation gates
│   ├── phase2_metrics_collector.py  # Execution metrics collection
│   ├── phase2_error_handler.py      # Error handling and recovery
│   ├── phase2_progress_reporter.py  # Progress reporting (every 50 tasks)
│   └── phase2_cardinality_validator.py # Cardinality validation
├── executors/
│   ├── base_executor_with_contract.py # Base executor with contract enforcement
│   └── implementations/              # Specific executor implementations (30)
├── sisas/
│   ├── irrigation_synchronizer.py   # SISAS signal irrigation (60→300)
│   ├── signal_mapper.py             # Signal mapping utilities
│   └── join_table.py                # Join table for signal synchronization
├── tests/
│   ├── test_phase2_carver_300_delivery.py # Tests carver delivers exactly 300
│   ├── test_phase2_cardinality_invariant.py # Tests 60→300 invariant
│   ├── test_phase2_sisas_synchronization.py # Tests SISAS integration
│   ├── test_phase2_contracts_enforcement.py # Tests contract decorators
│   ├── test_phase2_executor_integration.py # Tests executor contracts
│   ├── test_phase2_retry_logic.py   # Tests retry with backoff
│   ├── test_phase2_evidence_tracking.py # Tests evidence collection
│   ├── test_phase2_orchestrator_alignment.py # Tests orchestration
│   └── test_phase2_certificates_presence.py # Tests 15 certificates exist
├── tools/
│   └── phase2_validation_tools.py   # Validation and debugging tools
├── phase2_a_arg_router.py           # Argument routing with exhaustive coverage
├── phase2_b_carver.py               # Carver producing exactly 300 outputs
├── phase2_c_execution_planner.py    # Execution plan generation
├── phase2_d_batch_executor.py       # Batch execution with parallelization
└── phase2_e_irrigation_synchronizer.py # SISAS irrigation (60→300)
```

## Key Components

### 1. Constants (`constants/phase2_constants.py`)

Frozen constants with cardinality assertions:

```python
NUM_CHUNKS: Final[int] = 60
NUM_BASE_QUESTIONS: Final[int] = 30
NUM_POLICY_AREAS: Final[int] = 10
NUM_MICRO_ANSWERS: Final[int] = 300

assert NUM_MICRO_ANSWERS == NUM_BASE_QUESTIONS * NUM_POLICY_AREAS
assert NUM_CHUNKS == NUM_POLICY_AREAS * NUM_DIMENSIONS
```

### 2. Router (`phase2_a_arg_router.py`)

Exhaustive argument routing with:
- No silent defaults
- Strict validation
- Full traceability
- 30+ special route handlers

### 3. Carver (`phase2_b_carver.py`)

Produces exactly 300 micro-answers:
- 30 base questions × 10 policy areas
- Raymond Carver minimalist style
- Evidence-backed assertions
- Bayesian confidence calibration
- Gap analysis with brutal honesty

### 4. SISAS Integration (`phase2_e_irrigation_synchronizer.py`)

Signal irrigation from 60 chunks to 300 tasks:
- Join table mapping
- Signal enrichment
- Metadata propagation
- 60→300 cardinality preservation

### 5. Contracts

Eight contract modules enforcing:
- **Input:** Valid CPP from Phase 1 (60 chunks)
- **Output:** Valid Phase2Output (300 micro-answers)
- **Cardinality:** Exactly 60→300 transformation
- **Evidence:** Non-null evidence tracking
- **Retry:** Exponential backoff (3 retries)
- **CQVR:** Quality gates
- **SISAS:** Signal synchronization
- **Executor:** Contract compliance

### 6. Certificates

15 certificates documenting:
- CERTIFICATE_01: Phase 2 input validation
- CERTIFICATE_02: Phase 2 output validation
- CERTIFICATE_03: Cardinality enforcement (60→300)
- CERTIFICATE_04: Router exhaustiveness
- CERTIFICATE_05: Carver 300-delivery guarantee
- CERTIFICATE_06: SISAS synchronization
- CERTIFICATE_07: Executor contract compliance
- CERTIFICATE_08: Retry logic correctness
- CERTIFICATE_09: Evidence tracking completeness
- CERTIFICATE_10: Quality gate enforcement
- CERTIFICATE_11: Error handling coverage
- CERTIFICATE_12: Metrics collection accuracy
- CERTIFICATE_13: Progress reporting fidelity
- CERTIFICATE_14: Determinism guarantee
- CERTIFICATE_15: Test suite completeness

## Entry Point

```python
from canonic_phases.phase_2 import execute_phase_2_with_full_contract

result = execute_phase_2_with_full_contract(
    cpp_input=phase1_output,  # 60 chunks from Phase 1
    execution_config=config,
)

# result.micro_answers: List[MicroAnswer]  # Exactly 300
# result.cardinality_report: CardinalityReport  # 60→300 verified
# result.quality_metrics: QualityMetrics
```

## Key Invariants

1. **Cardinality:** Exactly 300 micro-answers (30 questions × 10 PA)
2. **Input chunks:** Exactly 60 (10 PA × 6 DIM)
3. **Questions per PA:** Exactly 30 for each policy area
4. **Evidence:** Non-null evidence for each answer
5. **Retry:** Max 3 retries with exponential backoff
6. **SISAS:** 60→300 signal irrigation verified
7. **Contracts:** All 8 contracts enforced
8. **Certificates:** All 15 certificates present

## Testing

Run Phase 2 tests:

```bash
# All Phase 2 tests
pytest tests/test_phase2_*.py -v

# Cardinality test (300 delivery)
pytest src/canonic_phases/phase_2/tests/test_phase2_carver_300_delivery.py -v

# SISAS synchronization test (60→300)
pytest src/canonic_phases/phase_2/tests/test_phase2_sisas_synchronization.py -v

# Contract enforcement test
pytest src/canonic_phases/phase_2/tests/test_phase2_contracts_enforcement.py -v
```

## Migration Status

- [x] Directory structure created (12 directories)
- [x] Package `__init__.py` files (12 files)
- [x] Constants module with frozen values
- [x] JSON schemas (4 schemas, validated)
- [ ] Router module (`phase2_a_arg_router.py`)
- [ ] Carver module (`phase2_b_carver.py`)
- [ ] 8 contract modules
- [ ] SISAS integration
- [ ] 9 orchestration modules
- [ ] Executor base and implementations
- [ ] 15 certificates
- [ ] 9 test files
- [ ] CI workflow

## Legacy Artifacts

The following files in `src/farfan_pipeline/phases/Phase_two/` will be migrated or deprecated:

- `arg_router.py` → `phase2_a_arg_router.py` (simplified, canonical)
- `carver.py` → `phase2_b_carver.py` (cardinality-enforced)
- `irrigation_synchronizer.py` → `phase2_e_irrigation_synchronizer.py` (60→300 verified)
- `base_executor_with_contract.py` → `executors/base_executor_with_contract.py`
- `batch_executor.py` → `phase2_d_batch_executor.py`
- `evidence_nexus.py` → `orchestration/phase2_evidence_tracker.py`

## References

- Phase 1 canonical: `src/canonic_phases/phase_1_cpp_ingestion/`
- Phase 3 canonical: `src/canonic_phases/phase_3_scoring_transformation/`
- Contract framework: `src/farfan_pipeline/infrastructure/contractual/dura_lex/`
- SISAS system: `src/farfan_pipeline/infrastructure/irrigation_using_signals/`
