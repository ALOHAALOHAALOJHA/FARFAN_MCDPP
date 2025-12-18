# Phase 2: Inference Phase (`phase_2`)

**STATUS**: ACTIVE

Phase 2 implements the executor-driven inference layer that transforms canonical
policy packages (CPP) into evidence-backed analytical outputs through 300
specialized executor contracts.

## Canonical Path

```
CANONICAL_ROOT: src/canonic_phases/phase_2/
ALTERNATIVE_PATHS: FORBIDDEN
LEGACY_PATHS: DELETE_ON_DISCOVERY
```

## Architecture Overview

Phase 2 follows a 7-stage pipeline architecture:

### STAGE_A: Routing (`phase2_a_arg_router.py`)
Argument routing with strict validation, special route handlers, and comprehensive
metrics. Handles 30+ special routes for high-traffic methods.

### STAGE_B: Carving (`phase2_b_carver.py`)
Doctoral-level narrative synthesis with Raymond Carver minimalist style. Implements
evidence-based analysis with explicit causal reasoning and calibrated uncertainty.

### STAGE_C: Validation (`phase2_c_contract_validator_cqvr.py`)
Contract Quality, Validity, Reliability validation with three-tier scoring system.
Implements triage decisions (PRODUCCION, REFORMULAR, PARCHEAR).

### STAGE_D: Configuration (`phase2_d_executor_config.py`)
Runtime parametrization for executor execution (HOW parameters only).
Separates runtime config from calibration values (WHAT quality).

### STAGE_E: SISAS Synchronization (`phase2_e_irrigation_synchronizer.py`)
Question→Chunk→Task→Plan coordination implementing the irrigation synchronization
pattern. Generates deterministic ExecutionPlan with 300 tasks.

### STAGE_F: Chunk Synchronization (`phase2_f_executor_chunk_synchronizer.py`)
Executor-chunk binding with canonical JOIN table. Validates 1:1 mapping between
300 executor contracts and 60 document chunks.

### STAGE_G: Orchestration (`phase2_g_synchronization.py`)
Top-level orchestration coordinating all synchronization layers with full
observability and deterministic execution guarantees.

## Directory Structure

```
phase_2/
├── __init__.py                                    # [EXPORT_GATE]
├── README.md                                      # [SPECIFICATION_DOCUMENT]
│
├── phase2_a_arg_router.py                         # [STAGE_A: ROUTING]
├── phase2_b_carver.py                             # [STAGE_B: CARVING]
├── phase2_c_contract_validator_cqvr.py            # [STAGE_C: VALIDATION]
├── phase2_d_executor_config.py                    # [STAGE_D: CONFIGURATION]
├── phase2_e_irrigation_synchronizer.py            # [STAGE_E: SISAS_SYNC]
├── phase2_f_executor_chunk_synchronizer.py        # [STAGE_F: CHUNK_SYNC]
├── phase2_g_synchronization.py                    # [STAGE_G: ORCHESTRATION]
│
├── constants/
│   ├── __init__.py
│   └── phase2_constants.py                        # [SINGLE_SOURCE_OF_TRUTH]
│
├── schemas/
│   ├── __init__.py
│   ├── executor_config.schema.json                # [SCHEMA_VERSION: 1.0.0]
│   ├── executor_output.schema.json                # [SCHEMA_VERSION: 1.0.0]
│   ├── calibration_policy.schema.json             # [SCHEMA_VERSION: 1.0.0]
│   └── synchronization_manifest.schema.json       # [SCHEMA_VERSION: 1.0.0]
│
└── executors/
    ├── __init__.py
    ├── base_executor_with_contract.py             # [ABC_DEFINITION]
    ├── phase2_executor_instrumentation_mixin.py   # [CROSS_CUTTING]
    ├── phase2_executor_profiler.py                # [OBSERVABILITY]
    └── implementations/
        └── __init__.py
```

## Key Invariants

- 300 executor contracts (Q001-Q300)
- 60 document chunks (10 PA × 6 DIM)
- Deterministic task generation with stable ordering
- 1:1 executor-chunk binding validation
- Full observability with correlation_id tracking
- Separation of runtime config from calibration values

## Integration Points

**Input**: `CanonPolicyPackage` from Phase 1
**Output**: Evidence-backed analytical results for Phase 3

## References

- `FORCING_ROUTE.md` - Architectural constraints
- Legacy location: `src/farfan_pipeline/phases/Phase_two/`
