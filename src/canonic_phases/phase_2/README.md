# Phase 2 Executor Orchestration — Canonical Implementation

**Version:** 1.0.0  
**Effective Date:** 2025-12-18  
**Owner:** phase2_orchestration  
**Lifecycle:** ACTIVE

## Overview

Phase 2 is responsible for transforming validated Phase 0/1 outputs into 300 specialized executor contracts, validating them via CQVR, and orchestrating their execution with full determinism, concurrency control, and SISAS signal synchronization.

## Architecture

Phase 2 implements a 7-stage pipeline (A-G):

### Stage A: Argument Routing (`phase2_a_arg_router.py`)
- Routes incoming questions to appropriate method clusters
- Validates argument signatures against method contracts
- Ensures type safety and parameter completeness
- **Contract:** Routing Contract (RC) - exhaustive dispatch validation

### Stage B: Contract Carving (`phase2_b_carver.py`)
- Carves base contracts (Q001-Q030) into 300 specialized contracts (Q001-Q300)
- Applies Policy Area specific transformations (10 PAs)
- Generates doctoral-level narrative synthesis
- **Contract:** Carver 300-Delivery Contract - exactly 300 valid contracts

### Stage C: Contract Validation (`phase2_c_contract_validator_cqvr.py`)
- Validates contracts using CQVR rubric (Calidad, Quantum, Valor, Rigor)
- Enforces schema compliance (executor_config.schema.json, executor_output.schema.json)
- Gates contract progression to execution phase
- **Contract:** CQVR Gate Contract - minimum quality thresholds

### Stage D: Executor Configuration (`phase2_d_executor_config.py`)
- Loads runtime parameters (timeout, retry, memory limits)
- Applies environment-specific overrides
- Separates execution parameters (HOW) from calibration data (WHAT)
- **Contract:** Configuration Schema Contract - valid ExecutorConfig objects

### Stage E: SISAS Synchronization (`phase2_e_irrigation_synchronizer.py`)
- Synchronizes signal definitions from SISAS registry
- Maps signals to executor methods
- Validates signal-method compatibility
- **Contract:** SISAS Synchronization Contract - signal availability guarantees

### Stage F: Chunk Synchronization (`phase2_f_executor_chunk_synchronizer.py`)
- Coordinates executor execution across parallel chunks
- Ensures deterministic ordering despite concurrency
- Manages resource allocation and cleanup
- **Contract:** Chunk Synchronization Contract - permutation invariance

### Stage G: Orchestration (`phase2_g_synchronization.py`)
- Coordinates all 6 stages (A-F)
- Manages execution plan generation
- Enforces contract validation gates
- Provides observability and tracing
- **Contract:** Orchestration Contract - complete pipeline integrity

## Directory Structure

```
phase_2/
├── __init__.py                                    # Package exports
├── README.md                                      # This file
│
├── phase2_a_arg_router.py                         # Stage A: Routing
├── phase2_b_carver.py                             # Stage B: Carving
├── phase2_c_contract_validator_cqvr.py            # Stage C: Validation
├── phase2_d_executor_config.py                    # Stage D: Configuration
├── phase2_e_irrigation_synchronizer.py            # Stage E: SISAS Sync
├── phase2_f_executor_chunk_synchronizer.py        # Stage F: Chunk Sync
├── phase2_g_synchronization.py                    # Stage G: Orchestration
│
├── constants/
│   ├── __init__.py
│   └── phase2_constants.py                        # All Phase 2 constants
│
├── schemas/
│   ├── __init__.py
│   ├── executor_config.schema.json                # Runtime config schema
│   ├── executor_output.schema.json                # Output format schema
│   ├── calibration_policy.schema.json             # Calibration schema
│   └── synchronization_manifest.schema.json       # Sync manifest schema
│
├── executors/
│   ├── __init__.py
│   ├── base_executor_with_contract.py             # Abstract base executor
│   ├── phase2_executor_instrumentation_mixin.py   # Profiling mixin
│   ├── phase2_executor_profiler.py                # Performance profiling
│   ├── implementations/                           # Executor type implementations
│   │   └── __init__.py
│   └── tests/
│       ├── __init__.py
│       └── test_executor_contracts.py
│
├── contracts/
│   ├── __init__.py
│   ├── phase2_routing_contract.py                 # Routing validation
│   ├── phase2_concurrency_determinism.py          # Parallel==Serial
│   ├── phase2_context_immutability.py             # Context freeze
│   ├── phase2_permutation_invariance.py           # Order independence
│   ├── phase2_runtime_contracts.py                # Pre/post conditions
│   ├── phase2_compute_contract_hashes.py          # Hash reproducibility
│   ├── phase2_snapshot_contract.py                # State snapshots
│   ├── phase2_risk_certificate.py                 # Risk assessment
│   └── certificates/                              # Verification certificates
│       ├── CERTIFICATE_01_ROUTING_CONTRACT.md
│       ├── CERTIFICATE_02_CONCURRENCY_DETERMINISM.md
│       ├── CERTIFICATE_03_CONTEXT_IMMUTABILITY.md
│       ├── CERTIFICATE_04_PERMUTATION_INVARIANCE.md
│       ├── CERTIFICATE_05_RUNTIME_CONTRACTS.md
│       ├── CERTIFICATE_06_CONFIG_SCHEMA_VALIDITY.md
│       ├── CERTIFICATE_07_OUTPUT_SCHEMA_VALIDITY.md
│       ├── CERTIFICATE_08_CARVER_300_DELIVERY.md
│       ├── CERTIFICATE_09_CPP_TO_EXECUTOR_ALIGNMENT.md
│       ├── CERTIFICATE_10_SISAS_SYNCHRONIZATION.md
│       ├── CERTIFICATE_11_RESOURCE_PLANNING_DETERMINISM.md
│       ├── CERTIFICATE_12_PRECISION_TRACKING_INTEGRITY.md
│       ├── CERTIFICATE_13_METHOD_REGISTRY_COMPLETENESS.md
│       ├── CERTIFICATE_14_SIGNATURE_VALIDATION_STRICTNESS.md
│       └── CERTIFICATE_15_SOURCE_VALIDATION_STRICTNESS.md
│
├── orchestration/
│   ├── __init__.py
│   ├── phase2_method_registry.py                  # Method registration
│   ├── phase2_method_signature_validator.py       # Signature validation
│   ├── phase2_method_source_validator.py          # Source validation
│   ├── phase2_factory.py                          # Executor factory
│   ├── phase2_precision_tracking.py               # Precision metrics
│   ├── phase2_resource_aware_executor.py          # Resource-aware execution
│   ├── phase2_resource_manager.py                 # Resource allocation
│   ├── phase2_signature_types.py                  # Type definitions
│   └── phase2_task_planner.py                     # Execution planning
│
├── sisas/
│   ├── __init__.py
│   ├── phase2_signal_registry_adapter.py          # SISAS registry adapter
│   ├── phase2_signal_contract_validator.py        # Signal validation
│   ├── phase2_signal_consumption_integration.py   # Signal consumption
│   └── phase2_signal_quality_integration.py       # Quality metrics
│
├── tests/
│   ├── __init__.py
│   ├── test_phase2_naming_and_paths.py            # Naming enforcement
│   ├── test_phase2_router_contracts.py            # Routing tests
│   ├── test_phase2_carver_300_delivery.py         # Carver tests
│   ├── test_phase2_config_and_output_schemas.py   # Schema tests
│   ├── test_phase2_sisas_synchronization.py       # SISAS tests
│   ├── test_phase2_orchestrator_alignment.py      # Orchestration tests
│   ├── test_phase2_contracts_enforcement.py       # Contract tests
│   ├── test_phase2_resource_and_precision.py      # Resource tests
│   └── test_phase2_certificates_presence.py       # Certificate tests
│
└── tools/
    ├── __init__.py
    └── phase2_inventory_and_purge.py              # Maintenance utilities
```

## Naming Conventions

### Phase-Root Python Files
Pattern: `^phase2_[a-z]_[a-z0-9_]+\.py$`
- Examples: `phase2_a_arg_router.py`, `phase2_b_carver.py`
- Location: Directly under `phase_2/`

### Package-Internal Python Files
Pattern: `^[a-z][a-z0-9_]*\.py$`
- Examples: `base_executor_with_contract.py`, `phase2_routing_contract.py`
- Location: Inside subdirectories (executors/, contracts/, orchestration/, etc.)

### Schema Files
Pattern: `^[a-z][a-z0-9_]*\.schema\.json$`
- Examples: `executor_config.schema.json`
- Location: `schemas/`

### Certificate Files
Pattern: `^CERTIFICATE_[0-9]{2}_[A-Z][A-Z0-9_]*\.md$`
- Examples: `CERTIFICATE_01_ROUTING_CONTRACT.md`
- Location: `contracts/certificates/`

### Test Files
Pattern: `^test_phase2_[a-z0-9_]+\.py$`
- Examples: `test_phase2_carver_300_delivery.py`
- Location: `tests/`

## Mandatory File Headers

Every `.py` file must begin with:

```python
"""
Module: src.canonic_phases.phase_2.<subpackage>.<module_name>
Purpose: <ONE SENTENCE - what this module does>
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced: 
    - <ContractName1>: <one-line description>
    - <ContractName2>: <one-line description>

Determinism: 
    Seed-Strategy: <FIXED|PARAMETERIZED|NOT_APPLICABLE>
    State-Management: <description of state handling>

Inputs:
    - <InputName>: <Type> — <description>

Outputs:
    - <OutputName>: <Type> — <description>

Failure-Modes: 
    - <FailureMode1>: <ErrorType> — <when this occurs>
    - <FailureMode2>: <ErrorType> — <when this occurs>
"""
from __future__ import annotations
```

## Contracts Enforced

All Phase 2 modules enforce the following contracts:

1. **Routing Contract (RC):** All method dispatches validated against registry
2. **Concurrency Determinism Contract (CDC):** Parallel execution == Serial execution under fixed seed
3. **Context Immutability Contract (CIC):** Context objects never modified after creation
4. **Permutation Invariance Contract (PIC):** Set-based operations independent of order
5. **Runtime Contracts (RTC):** Pre/post conditions validated at method boundaries
6. **Config Schema Contract (CSC):** All ExecutorConfig objects schema-valid
7. **Output Schema Contract (OSC):** All executor outputs schema-valid
8. **Carver 300-Delivery Contract:** Exactly 300 valid contracts generated
9. **CPP-to-Executor Alignment Contract:** CPP outputs match executor inputs
10. **SISAS Synchronization Contract:** All required signals available
11. **Resource Planning Determinism Contract:** Resource allocation reproducible
12. **Precision Tracking Integrity Contract:** Metrics never drift
13. **Method Registry Completeness Contract:** All methods registered
14. **Signature Validation Strictness Contract:** No silent parameter drops
15. **Source Validation Strictness Contract:** All sources validated

## Usage

### Basic Execution

```python
from src.canonic_phases.phase_2 import phase2_g_synchronization

# Initialize orchestrator
orchestrator = phase2_g_synchronization.Phase2Orchestrator()

# Execute Phase 2 pipeline
result = orchestrator.execute(
    cpp_output=phase1_result,
    environment="production",
    seed=42
)
```

### Contract Validation

```python
from src.canonic_phases.phase_2.contracts import phase2_routing_contract

# Validate routing
routing_contract.validate_dispatch(
    method_name="analyze_causal_mechanism",
    args={"question": "Q001", "policy_area": "PA01"}
)
```

### SISAS Integration

```python
from src.canonic_phases.phase_2.sisas import phase2_signal_registry_adapter

# Load signals
signal_adapter = phase2_signal_registry_adapter.SISASAdapter()
signals = signal_adapter.load_signals_for_question("Q001")
```

## Verification

### Run Naming Tests
```bash
pytest src/canonic_phases/phase_2/tests/test_phase2_naming_and_paths.py -v
```

### Run Contract Tests
```bash
pytest src/canonic_phases/phase_2/tests/test_phase2_contracts_enforcement.py -v
```

### Run Full Test Suite
```bash
pytest src/canonic_phases/phase_2/tests/ -v
```

### Verify No Legacy Artifacts
```bash
find . -name "batch_executor.py" -o -name "batch_generate_all_configs.py"
# Should return empty
```

## Migration from Legacy Locations

This canonical implementation replaces scattered Phase 2 files from:
- `src/farfan_pipeline/phases/Phase_two/` (deleted)
- `src/orchestration/` (legacy, preserved for compatibility)
- `src/farfan_pipeline/orchestration/` (shared infrastructure, preserved)

All new Phase 2 development must occur in `src/canonic_phases/phase_2/`.

## References

- [PHASE_2_COMPLETE_AUDIT_SUMMARY.md](../../PHASE_2_COMPLETE_AUDIT_SUMMARY.md)
- [PHASE_2_FIXES_COMPLETED.md](../../PHASE_2_FIXES_COMPLETED.md)
- [CARVER_INTEGRATION_SUMMARY.md](../../CARVER_INTEGRATION_SUMMARY.md)
- [PHASE2_EXECUTOR_CONTRACTS_FINAL_DEEP_CHECK_2025-12-18.md](../../artifacts/reports/PHASE2_EXECUTOR_CONTRACTS_FINAL_DEEP_CHECK_2025-12-18.md)

## License

Proprietary - F.A.R.F.A.N Pipeline Team
