# Phase 2 — Executor Orchestration (Canonical Specification)

| Field | Value |
|-------|-------|
| Status | ACTIVE |
| Version | 1.0.0 |
| Phase Name | Executor Orchestration |
| Entry Point | `canonic_phases.phase_2` |
| Contract Version | 3.0.0 |

## Overview

Phase 2 orchestrates the execution of 300 specialized executor contracts (Q001-Q300) to transform
Canonical Policy Packages (CPP) into evidence-rich analytical outputs. Each contract binds to
multiple methodological approaches from the methods dispensary.

## Core Invariants

- **Contract Count**: Exactly 300 executor contracts (30 base questions × 10 policy areas)
- **Naming Convention**: All phase-root files follow `phase2_[a-z]_[a-z0-9_]+.py` pattern
- **Deterministic Execution**: Fixed random seed (PHASE2_RANDOM_SEED=42)
- **Schema Compliance**: All contracts validated against `executor_contract.v3.schema.json`
- **Forbidden Legacy Artifacts**: No `executors.py`, `batch_executor.py`, `batch_generate_all_configs.py`

## Architecture

### Executor Contract Structure

Each contract (Q001.v3.json - Q300.v3.json) contains:

- **Identity**: Question ID, dimension, policy area, version, hash
- **Executor Binding**: Class name and module path
- **Method Binding**: Orchestration mode, method count, method pipeline
- **Theoretical Framework**: Academic foundations and references
- **Technical Approach**: Algorithms, limitations, validation
- **Assembly Flow**: 5-step transformation pipeline
- **Output Interpretation**: Actionable insights and evidence

### Directory Structure

```
phase_2/
├── README.md (this file)
├── schemas/
│   └── *.schema.json (JSON Schema definitions)
├── contracts/
│   └── certificates/
│       └── CERTIFICATE_*.md (15 certification documents)
├── tests/
│   └── test_phase2_*.py (phase 2 test suite)
└── phase2_*.py (canonical phase 2 modules)
```

## Naming Conventions

### Phase-Root Files
- Pattern: `phase2_[a-z]_[a-z0-9_]+.py`
- Example: `phase2_a_orchestrator.py`, `phase2_b_validator.py`
- Forbidden: Any files not matching this pattern (except `__init__.py`)

### Contract Files
- Location: Must be in designated contract directory
- Pattern: `Q[0-9]{3}.v3.json`
- Range: Q001 through Q300

## Execution Model

### Multi-Method Pipeline

Each executor contract specifies a `multi_method_pipeline` orchestration mode:

1. **Method Discovery**: Load methods from dispensary based on contract bindings
2. **Priority Ordering**: Execute methods in priority sequence (1, 2, 3, ...)
3. **Evidence Assembly**: Aggregate outputs from all methods
4. **Confidence Calibration**: Apply Bayesian inference for uncertainty quantification
5. **Response Synthesis**: Generate doctoral-level narrative with explicit citations

### Determinism Guarantees

- All random operations seeded with `PHASE2_RANDOM_SEED`
- Contract execution order is deterministic
- Method invocation follows strict priority ordering
- Output artifacts are reproducible given same inputs

## Quality Gates

### Naming Enforcement
- All phase-root files must match naming pattern
- Legacy artifacts (executors.py, batch_executor.py) forbidden
- Phase 2 files must reside in canonical root only

### Schema Validation
- All JSON schemas must be valid Draft 2020-12 schemas
- All contracts must validate against schema
- Schema changes require version increment

### Forbidden Imports
- No imports from `questionnaire_monolith`
- No imports from legacy `executors` module
- No imports from `batch_executor`

### Certificate Compliance
- Exactly 15 certificates must exist
- All certificates must have Status: ACTIVE
- Required fields: Status, Effective Date, Verification Method

## Integration Points

### Inputs (from Phase 1)
- `CanonPolicyPackage`: 60-chunk PA×DIM grid
- Signal enrichment metadata
- Structural validation results

### Outputs (to Phase 3)
- Executor results with evidence traces
- Method execution metadata
- Confidence calibrations
- Gap analysis reports

## Testing Strategy

### Unit Tests
- Individual executor contract validation
- Method binding verification
- Schema compliance checks

### Integration Tests
- End-to-end executor orchestration
- Multi-method pipeline execution
- Determinism verification (run tests twice)

### Enforcement Tests
- Naming convention compliance
- Legacy artifact detection
- Canonical root verification
- Certificate count validation

## References

- Executor contracts: `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/`
- Methods dispensary: `src/methods_dispensary/`
- Contract schema: See `schemas/` directory
- Phase 1 CPP structure: `src/canonic_phases/phase_1_cpp_ingestion/README.md`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-18 | Initial canonical specification |
