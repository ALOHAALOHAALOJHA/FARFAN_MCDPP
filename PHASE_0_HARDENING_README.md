# Phase 0 Validation Hardening (P1)

## Overview

This document describes the hardening enhancements made to Phase 0 validation as part of P1 requirements. The goal is to ensure the orchestrator never runs with broken prerequisites by validating questionnaire integrity, method registry completeness, and smoke testing critical method categories.

## New Validation Gates

Phase 0 validation has been extended from 4 to 7 gates:

### Original Gates (1-4)
1. **Bootstrap** - Runtime config loaded, artifacts dir created
2. **Input Verification** - PDF and questionnaire hashed (SHA-256)
3. **Boot Checks** - Dependencies validated
4. **Determinism** - RNG seeds applied

### New Gates (5-7) - P1 Hardening
5. **Questionnaire Integrity** - SHA256 validation against known-good value
6. **Method Registry** - Expected method count validation (416 methods)
7. **Smoke Tests** - Sample methods from major categories (ingest, scoring, aggregation)

## Configuration

### Environment Variables

```bash
# Questionnaire Integrity (Gate 5)
EXPECTED_QUESTIONNAIRE_SHA256="<64-char-hex-hash>"

# Method Registry (Gate 6)
EXPECTED_METHOD_COUNT="416"

# Runtime Mode (affects all gates)
SAAAAAA_RUNTIME_MODE="prod"  # or "dev" or "exploratory"
```

### Computing Questionnaire Hash

```bash
# Compute SHA256 hash of questionnaire
sha256sum canonic_questionnaire_central/questionnaire_monolith.json

# Or using Python
python3 -c "import hashlib, json; \
    data = json.load(open('canonic_questionnaire_central/questionnaire_monolith.json')); \
    print(hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest())"
```

## Behavior by Mode

### PROD Mode (Strict)
- **Gate 5 Failure**: Hard failure if hash mismatch detected
- **Gate 6 Failure**: Hard failure if method count < 416 or any failed classes
- **Gate 7 Failure**: Hard failure if smoke tests fail
- **Orchestrator**: Refuses to initialize if any gate fails

### DEV Mode (Permissive)
- **Gate 5 Failure**: Warning logged, execution continues
- **Gate 6 Failure**: Warning logged if failed classes, continues in degraded mode
- **Gate 7 Failure**: Warning logged, execution continues with degraded capabilities
- **Orchestrator**: Initializes with warnings for degraded prerequisites

### Legacy Mode (No Expected Hash)
- **Gate 5**: Passes with warning if EXPECTED_QUESTIONNAIRE_SHA256 not set
- Backward compatible with existing deployments

## Integration with Orchestrator

### Phase0ValidationResult Enforcement

The orchestrator enforces Phase 0 validation at two points:

1. **During `__init__`**:
   ```python
   if phase0_validation is not None and not phase0_validation.all_passed:
       raise RuntimeError(f"Phase 0 exit gates failed: {failed_gates}")
   ```

2. **During `_load_configuration`**:
   ```python
   # Re-validates questionnaire hash
   if monolith_hash.lower() != expected_hash.lower():
       raise RuntimeError("Questionnaire integrity check failed")
   
   # Re-validates method count
   if registered_count < EXPECTED_METHOD_COUNT:
       raise RuntimeError("Method registry validation failed")
   ```

### Example Usage

```python
from canonic_phases.Phase_zero.exit_gates import check_all_gates
from orchestration.orchestrator import Orchestrator, Phase0ValidationResult

# Run Phase 0 validation
all_passed, gate_results = check_all_gates(phase0_runner)

# Create validation result
validation = Phase0ValidationResult(
    all_passed=all_passed,
    gate_results=gate_results,
    validation_time=datetime.utcnow().isoformat()
)

# Initialize orchestrator (will fail if validation failed)
orchestrator = Orchestrator(
    method_executor=executor,
    questionnaire=questionnaire,
    executor_config=config,
    phase0_validation=validation,  # Required for hardened mode
    runtime_config=runtime_config
)
```

## Machine-Readable Error Reporting

All gate failures produce machine-readable error reports for CI/CD integration:

```python
# Get gate result as dictionary
gate_dict = gate_result.to_dict()
# {
#     "passed": false,
#     "gate_name": "questionnaire_integrity",
#     "gate_id": 5,
#     "reason": "Questionnaire hash mismatch: expected abc123..., got def456..."
# }

# Serialize to JSON for CI
import json
json.dumps([r.to_dict() for r in gate_results], indent=2)
```

## Testing

### Unit Tests (20 tests)

```bash
# Run all hardened validation unit tests
pytest tests/test_phase0_hardened_validation.py -v

# Run specific test suite
pytest tests/test_phase0_hardened_validation.py::TestQuestionnaireIntegrityGate -v
```

**Test Coverage**:
- 5 tests for Gate 5 (Questionnaire Integrity)
- 6 tests for Gate 6 (Method Registry)
- 4 tests for Gate 7 (Smoke Tests)
- 3 tests for All Gates Integration
- 2 tests for Machine-Readable Errors

### Integration Tests (Pending)

```bash
# Integration tests require full dependency installation
pip install -r requirements.txt
pytest tests/test_phase0_damaged_artifacts.py -v

# Skip integration tests in CI (if dependencies unavailable)
SKIP_INTEGRATION_TESTS=1 pytest tests/ -v
```

**Integration Test Coverage** (To be implemented):
- Corrupted questionnaire detection
- Missing method detection
- Failed smoke test detection
- End-to-end orchestrator initialization failures

## Validation Flow

```
┌─────────────────────────────────────────────────┐
│ Phase 0 Bootstrap                               │
│ - Load RuntimeConfig                            │
│ - Create artifacts directory                    │
│ - Hash PDF and questionnaire                    │
│ - Apply RNG seeds                               │
└────────────────┬────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────┐
│ Exit Gates Validation (Fail-Fast)              │
│                                                 │
│ Gate 1: Bootstrap        ✓                     │
│ Gate 2: Input Verify     ✓                     │
│ Gate 3: Boot Checks      ✓                     │
│ Gate 4: Determinism      ✓                     │
│ Gate 5: Quest. Integrity ✓  (NEW - P1)        │
│ Gate 6: Method Registry  ✓  (NEW - P1)        │
│ Gate 7: Smoke Tests      ✓  (NEW - P1)        │
└────────────────┬────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────┐
│ Orchestrator Initialization                     │
│ - Validates Phase0ValidationResult              │
│ - Re-checks questionnaire hash                  │
│ - Re-checks method count                        │
│ - Logs all validation events                    │
└────────────────┬────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────┐
│ Pipeline Execution (11 phases)                  │
│ - Phase 0: Configuration                        │
│ - Phase 1-10: Analysis pipeline                 │
└─────────────────────────────────────────────────┘
```

## Logging

All validation events are logged with structured data:

### Successful Validation
```python
logger.info(
    "questionnaire_integrity_verified",
    hash=monolith_hash[:16] + "...",
    category="phase0_validation"
)

logger.info(
    "method_registry_validated",
    registered=416,
    failed=0,
    category="phase0_validation"
)
```

### Failed Validation (PROD)
```python
logger.error(
    "Questionnaire integrity check failed: "
    "expected SHA256 abc123..., got def456..."
)

logger.error(
    "Method registry validation failed: "
    "expected 416 methods, got 200"
)
```

### Degraded Mode (DEV)
```python
logger.warning(
    "DEV mode: Method registry has 16 failed classes: "
    "['BrokenClass1', 'BrokenClass2', 'BrokenClass3']"
)
```

## Backward Compatibility

The hardening changes maintain backward compatibility:

1. **Legacy Mode**: If `EXPECTED_QUESTIONNAIRE_SHA256` is not set, Gate 5 passes with a warning
2. **Optional Validation**: Phase0ValidationResult is optional (for now)
3. **Degraded Mode**: DEV mode allows execution with warnings instead of hard failures
4. **Method Count**: Uses environment variable with sensible default (416)

## Regression Prevention

To prevent future relaxations of Phase 0 criteria:

1. **Gate Count Validation**: `get_gate_summary()` expects exactly 7 gates
2. **Fail-Fast Enforcement**: `check_all_gates()` stops at first failure
3. **Orchestrator Enforcement**: `__init__` and `_load_configuration` validate prerequisites
4. **Test Coverage**: 20 unit tests + integration tests ensure behavior is locked in

## Future Enhancements

1. **Configurable Smoke Tests**: Allow custom smoke test method lists
2. **Performance Benchmarks**: Add timing metrics for validation gates
3. **Chaos Engineering**: Random failure injection for resilience testing
4. **Validation Cache**: Cache validation results for repeated runs
5. **Detailed Diagnostics**: Add `--diagnose` flag for detailed validation reports

## References

- **Specification**: P00-EN v2.0 + P1 Hardening Requirements
- **Issue**: [P1] HARDEN: Phase 0 Validation (Methods, Questionnaire, Structure)
- **Implementation**: `src/farfan_pipeline/phases/Phase_zero/exit_gates.py`
- **Tests**: `tests/test_phase0_hardened_validation.py`

## Authors

- F.A.R.F.A.N Phase 0 Compliance Team
- Version: 2.0.0 (P1 Hardening)
- Date: 2025-12-17
