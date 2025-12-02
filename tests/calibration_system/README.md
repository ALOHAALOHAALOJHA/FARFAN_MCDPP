# Calibration System Validation Suite

Comprehensive all-or-nothing quality gate for the calibration system.

## Overview

This test suite validates the integrity, consistency, and performance of the entire calibration system. **ALL tests must pass** for the system to be considered production-ready. A single failure blocks deployment.

## Test Suites

### 1. Inventory Consistency (`test_inventory_consistency.py`)

**Purpose:** Verifies all methods are consistently defined across JSON inventories.

**Validates:**
- `executors_methods.json` has correct structure
- Exactly 30 executors present (D1-Q1 through D6-Q5)
- All methods have required fields (class, method)
- No duplicate methods within executors
- All executor methods have calibration entries in `intrinsic_calibration.json`
- All calibrations have valid `status` field

**Failure Impact:** Inconsistent inventories cause runtime errors and calibration mismatches.

### 2. Layer Correctness (`test_layer_correctness.py`)

**Purpose:** Validates architectural integrity with 8 required layers.

**Validates:**
- All 8 layers defined: ingestion, extraction, transformation, validation, aggregation, scoring, reporting, meta
- Each of 30 executors has methods in all 8 layers
- `LAYER_REQUIREMENTS` mapping exists and is complete
- Layer execution order is acyclic
- No orphan layers in execution sequence

**Failure Impact:** Missing layers break the execution pipeline.

### 3. Intrinsic Coverage (`test_intrinsic_coverage.py`)

**Purpose:** Ensures ≥80% of methods have computed calibrations.

**Validates:**
- At least 80% of all methods have `status='computed'`
- All 30 executors have at least one method with `status='computed'`
- No executor is entirely excluded or manual
- Excluded methods have documented reasons
- Error status methods are tracked

**Failure Impact:** Low coverage means system relies on defaults or fails at runtime.

### 4. AST Extraction Accuracy (`test_ast_extraction_accuracy.py`)

**Purpose:** Validates extracted method signatures match actual source code.

**Validates:**
- Signatures can be extracted from source via AST parsing
- Executor methods exist in source code
- Stored signatures match actual signatures
- Signature mismatch rate ≤ 5%
- Private methods are properly identified

**Failure Impact:** Signature mismatches cause method execution failures.

### 5. Orchestrator Runtime (`test_orchestrator_runtime.py`)

**Purpose:** Tests correct layer evaluation and aggregation with real contexts.

**Validates:**
- Layers execute in correct order
- Calibration context resolution works without errors
- Method execution can be simulated
- Aggregation and scoring methods present
- No circular dependencies between layers

**Failure Impact:** Runtime errors prevent policy analysis execution.

### 6. No Hardcoded Calibrations (`test_no_hardcoded_calibrations.py`)

**Purpose:** Scans for magic numbers in calibration-sensitive code.

**Validates:**
- No hardcoded thresholds, weights, scores in source
- All calibration parameters externalized to config
- Proper use of `calibration_registry`
- No inline Bayesian priors
- Only allowed constants (0, 1, 0.5) permitted

**Failure Impact:** Hardcoded values prevent systematic calibration and violate "SIN CARRETA" principle.

### 7. Performance Benchmarks (`test_performance_benchmarks.py`)

**Purpose:** Validates load times and calibration speed meet requirements.

**Validates:**
- Load `intrinsic_calibration.json` < 1 second
- Calibrate 30 executors < 5 seconds  
- Calibrate 200 methods < 30 seconds
- File size < 10 MB
- Dictionary lookup performance

**Failure Impact:** Slow performance degrades user experience and prevents real-time calibration.

## Running Tests

### Run All Tests

```bash
pytest tests/calibration_system/ -v
```

### Run Specific Test Suite

```bash
pytest tests/calibration_system/test_inventory_consistency.py -v
pytest tests/calibration_system/test_layer_correctness.py -v
pytest tests/calibration_system/test_intrinsic_coverage.py -v
pytest tests/calibration_system/test_ast_extraction_accuracy.py -v
pytest tests/calibration_system/test_orchestrator_runtime.py -v
pytest tests/calibration_system/test_no_hardcoded_calibrations.py -v
pytest tests/calibration_system/test_performance_benchmarks.py -v
```

### Generate Failure Report Manually

```bash
python tests/calibration_system/generate_failure_report.py \
  --test1 success \
  --test2 success \
  --test3 failure \
  --test4 success \
  --test5 success \
  --test6 failure \
  --test7 success \
  --output calibration_system_failure_report.md
```

## CI/CD Integration

The validation suite runs automatically in GitHub Actions via `.github/workflows/calibration-validation.yml`.

### Workflow Triggers

- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Manual workflow dispatch
- Nightly at 3:00 AM UTC

### Quality Gate Behavior

- **All tests pass:** ✅ Merge allowed
- **Any test fails:** ❌ **MERGE BLOCKED**

The workflow:
1. Runs all 7 test suites independently
2. Generates comprehensive failure report
3. Posts results to PR comments
4. Blocks merge if any test fails
5. Uploads test results and reports as artifacts

## Fixing Failures

### Inventory Consistency Failures

```bash
# Re-sync method inventories
python system/config/calibration/intrinsic_calibration_triage.py

# Verify executor definitions
python -c "import json; print(json.dumps(json.load(open('src/farfan_pipeline/core/orchestrator/executors_methods.json')), indent=2))" | grep executor_id
```

### Layer Correctness Failures

```bash
# Audit layer coverage per executor
python scripts/audit_layer_coverage.py  # If script exists

# Manually verify each executor has all 8 layers
grep -A5 "class D._Q._" src/farfan_pipeline/core/orchestrator/executors.py
```

### Intrinsic Coverage Failures

```bash
# Run calibration triage to compute missing calibrations
python system/config/calibration/intrinsic_calibration_triage.py

# Check coverage stats
python -c "import json; cal=json.load(open('system/config/calibration/intrinsic_calibration.json')); computed=[k for k,v in cal.items() if v.get('status')=='computed']; print(f'{len(computed)} computed')"
```

### Hardcoded Calibration Failures

```bash
# Find hardcoded values (example)
grep -rn "threshold\s*=\s*[0-9.]\+" src/farfan_pipeline/ --include="*.py" | grep -v test | grep -v config

# Move to calibration_registry.py or intrinsic_calibration.json
```

### Performance Failures

```bash
# Profile JSON loading
python -m cProfile -s cumtime -c "import json; json.load(open('system/config/calibration/intrinsic_calibration.json'))"

# Check file size
du -h system/config/calibration/intrinsic_calibration.json
```

## Manual Verification Testing

To manually verify the system responds correctly to failures:

### 1. Break Inventory Consistency

```bash
# Temporarily remove a method from intrinsic_calibration.json
# Run test, verify it fails
pytest tests/calibration_system/test_inventory_consistency.py -v
```

### 2. Break Layer Coverage

```bash
# Comment out a layer in one executor's method list
# Run test, verify it fails
pytest tests/calibration_system/test_layer_correctness.py -v
```

### 3. Add Hardcoded Score

```bash
# Add "score = 0.75" to a non-test file
# Run test, verify it fails
pytest tests/calibration_system/test_no_hardcoded_calibrations.py -v
```

## Dependencies

- `pytest >= 7.0`
- `pytest-cov >= 4.0`
- `pytest-timeout >= 2.1`

Install:

```bash
pip install pytest pytest-cov pytest-timeout
```

## Architecture

```
tests/calibration_system/
├── __init__.py                          # Package marker
├── README.md                            # This file
├── test_inventory_consistency.py        # Test 1
├── test_layer_correctness.py            # Test 2
├── test_intrinsic_coverage.py           # Test 3
├── test_ast_extraction_accuracy.py      # Test 4
├── test_orchestrator_runtime.py         # Test 5
├── test_no_hardcoded_calibrations.py    # Test 6
├── test_performance_benchmarks.py       # Test 7
└── generate_failure_report.py           # Report generator
```

## Success Criteria

**System is production-ready when:**

1. ✅ All 30 executors consistently defined
2. ✅ All executors have all 8 layers
3. ✅ ≥80% methods have computed calibrations
4. ✅ All 30 executors have ≥1 computed method
5. ✅ Signature mismatch ≤5%
6. ✅ No hardcoded calibration values
7. ✅ Performance within limits

**If any criterion fails:** ❌ **NOT READY FOR PRODUCTION**

## Support

- Review test failures in GitHub Actions artifacts
- Check `calibration_system_failure_report.md` for specific remediation steps
- Consult `AGENTS.md` for calibration system architecture
- Examine source code in `tests/calibration_system/` for test logic
