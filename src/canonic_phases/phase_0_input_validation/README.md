# Phase 0: Input Validation — Canonical Specification

## Abstract

Phase 0 validates and bootstraps the F.A.R.F.A.N pipeline under deterministic, audit-ready guarantees. It enforces runtime mode policy (PROD/DEV/EXPLORATORY), executes boot checks, computes input hashes, applies deterministic seeds, validates questionnaire integrity, and validates seven exit gates before handoff to Phase 1.

This canonical specification defines the architectural contracts, execution order, validation points, and governance artifacts for Phase 0.

## 1. Architecture and Execution Order

Phase 0 follows a strict sequential execution model:

1. **Load Runtime Config**: Parse environment variables and enforce fallback policies
2. **Run Boot Checks**: Validate dependencies (spaCy, calibration files, validators)
3. **Hash Inputs**: Compute SHA-256 of PDF and questionnaire for audit trail
4. **Apply Deterministic Seeds**: Initialize all RNGs (random, numpy, torch) with fixed seeds
5. **Validate Exit Gates**: Execute 7 mandatory gates ensuring initialization integrity
6. **Construct Phase0Result**: Package validated state for Phase 1 handoff

### Key Functions

- `get_runtime_config()`: Load and validate runtime configuration
- `run_boot_checks(config)`: Execute boot-time dependency checks
- `initialize_determinism_from_registry(seed_dict)`: Apply deterministic seeds
- `check_all_gates(runner)`: Validate all 7 exit gates
- `Phase0Result(...)`: Construct immutable handoff object

## 2. Runtime Mode and Fallback Policy

Runtime modes control fallback behavior and validation strictness:

- **PROD**: Strict validation, Category A/C fallbacks forbidden
- **DEV**: Relaxed validation, warnings instead of failures
- **EXPLORATORY**: Experimental features enabled

### Fallback Categorization

**Category A (Critical - System Integrity)**
- `ALLOW_CONTRADICTION_FALLBACK`: Forbidden in PROD
- `ALLOW_VALIDATOR_DISABLE`: Forbidden in PROD
- `ALLOW_EXECUTION_ESTIMATES`: Forbidden in PROD

**Category C (Development - Convenience)**
- `ALLOW_DEV_INGESTION_FALLBACKS`: Forbidden in PROD
- `ALLOW_AGGREGATION_DEFAULTS`: Forbidden in PROD

Enforcement: `FallbackPolicyContract.enforce_prod_policy(config)`

## 3. Exit Gates (7 Mandatory)

All exit gates must pass before Phase 0 completion:

1. **Bootstrap**: Runtime config loaded, artifacts dir created
2. **Input Verification**: PDF and questionnaire SHA-256 computed
3. **Boot Checks**: Dependencies validated (fatal in PROD, warn in DEV)
4. **Determinism**: All required seeds applied to RNGs
5. **Questionnaire Integrity**: SHA-256 validation against known-good
6. **Method Registry**: Expected method count validation
7. **Smoke Tests**: Sample methods from major categories execute successfully

Validation: `ExitGatesContract.validate(gate_results)`

## 4. Orchestrator Transcript Alignment

Phase 0 implementation aligns with orchestrator execution transcript:

```
[Phase 0 Start] → [Load Config] → [Boot Checks] → [Hash Inputs] → 
[Apply Seeds] → [Gate 1: Bootstrap] → [Gate 2: Input Verification] → 
[Gate 3: Boot Checks] → [Gate 4: Determinism] → [Gate 5: Questionnaire] → 
[Gate 6: Method Registry] → [Gate 7: Smoke Tests] → [Phase0Result] → 
[Phase 0 Complete]
```

All function names and execution sequence match orchestrator log output.

## 5. Contracts and Certificates

### Contract Modules

- `BootstrapContract`: Validates bootstrap initialization
- `InputContract`: Validates input file hashing
- `ExitGatesContract`: Validates all 7 gates passed
- `FallbackPolicyContract`: Enforces PROD fallback policies

### Certificates (15)

Governance artifacts documenting architectural decisions:

1. Runtime Mode Enforcement
2. Bootstrap Initialization
3. Input File Hashing
4. Boot Checks Execution
5. Determinism Seeds Applied
6. Questionnaire Integrity
7. Method Registry Validation
8. Smoke Tests Execution
9. Exit Gate Sequencing
10. Canonical Path Enforcement
11. Naming Convention Compliance
12. Phase0Result Handoff Readiness
13. Contract Module Structure
14. Academic README Alignment
15. Governance Artifacts Complete

All certificates located in `contracts/certificates/CERTIFICATE_*.md`.

## 6. Validation and Tests

Severe test suite validates Phase 0 integrity:

- **test_fallback_policy.py**: PROD policy enforcement
- **test_exit_gates.py**: All 7 gates pass correctly
- **test_determinism_seeds.py**: Seed stability and reproducibility
- **test_purge_paths.py**: Legacy path purge verification
- **test_transcript_alignment.py**: README-code alignment
- **test_phase0_result.py**: Phase0Result validation
- **test_contracts.py**: Contract module structure
- **test_governance.py**: Certificate completeness

Test location: `tests/phase_0/`

## 7. Module Structure

```
phase_0_input_validation/
├── __init__.py                          # Public API exports
├── README.md                            # This specification
├── phase0_runtime_config.py             # Runtime configuration
├── phase0_boot_checks.py                # Boot-time validation
├── phase0_paths.py                      # Path resolution
├── phase0_bootstrap.py                  # DI initialization
├── phase0_determinism.py                # Seed management
├── phase0_exit_gates.py                 # Exit gate validation
├── phase0_main.py                       # CLI entrypoint
├── phase0_verified_pipeline_runner.py   # Pipeline runner
├── phase0_results.py                    # Phase0Result dataclass
└── contracts/                           # Contract definitions
    ├── __init__.py
    ├── phase0_bootstrap_contract.py
    ├── phase0_input_contract.py
    ├── phase0_exit_gates_contract.py
    ├── phase0_fallback_policy_contract.py
    └── certificates/                    # Governance certificates
        ├── CERTIFICATE_01_*.md
        ├── CERTIFICATE_02_*.md
        └── ... (15 total)
```

## 8. Import Conventions

All Phase 0 imports use canonical path:

```python
from canonic_phases.phase_0_input_validation import (
    RuntimeConfig,
    RuntimeMode,
    get_runtime_config,
    BootCheckError,
    run_boot_checks,
    GateResult,
    check_all_gates,
    Phase0Result,
)
```

Legacy imports via `canonic_phases.Phase_zero` are deprecated.

## 9. CI Enforcement

CI gates ensure Phase 0 integrity:

1. **Legacy Import Check**: Fail if `Phase_zero` imports detected
2. **Naming Convention Check**: Enforce `phase0_` prefix and snake_case
3. **Purge Verification**: Ensure no non-canonical Phase 0 paths
4. **Test Suite**: Run all phase_0/ tests on every PR

## 10. References

### Internal Modules
- `phase0_runtime_config.py`: Lines 1-50 (fallback categories)
- `phase0_boot_checks.py`: Lines 14-80 (dependency validation)
- `phase0_exit_gates.py`: Lines 1-600 (7 gate implementations)
- `phase0_determinism.py`: Lines 1-200 (seed registry)
- `phase0_results.py`: Lines 1-70 (Phase0Result dataclass)

### External Dependencies
- Python 3.12+
- spacy>=3.7.0 (es_core_news_lg model)
- numpy>=1.24.0
- torch>=2.1.0

### Enforcement Points
- Contract validation in all entry points
- Gate validation before Phase 1 handoff
- CI checks on every commit

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-18  
**Status**: CANONICAL  
**Maintainer**: Phase 0 Compliance Team
