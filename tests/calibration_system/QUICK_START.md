# Calibration Validation Quick Start

## Run All Tests (Requires pytest)

```bash
pytest tests/calibration_system/ -v
```

## Manual Verification (No pytest required)

```bash
python3 tests/calibration_system/manual_verification.py
```

## Expected Output

### ✅ All Tests Pass

```
============================================================
SUMMARY
============================================================
✅ PASS: executors_methods
✅ PASS: intrinsic_calibration
✅ PASS: inventory_consistency
✅ PASS: layer_coverage
✅ PASS: failure_simulation

============================================================
✅ ALL CHECKS PASSED - System appears ready
============================================================
```

### ❌ Tests Fail

```
============================================================
SUMMARY
============================================================
✅ PASS: executors_methods
❌ FAIL: intrinsic_calibration
❌ FAIL: inventory_consistency
❌ FAIL: layer_coverage
✅ PASS: failure_simulation

============================================================
❌ SOME CHECKS FAILED - System NOT ready
============================================================
```

## Quick Fixes

### Empty intrinsic_calibration.json

```bash
# Run calibration triage
python system/config/calibration/intrinsic_calibration_triage.py
```

### Missing layer fields

Add `"layer": "extraction"` to each method in `executors_methods.json`:

```json
{
  "class": "BayesianNumericalAnalyzer",
  "method": "evaluate_policy_metric",
  "layer": "extraction"
}
```

Valid layers:
- `ingestion`
- `extraction`
- `transformation`
- `validation`
- `aggregation`
- `scoring`
- `reporting`
- `meta`

### Test Individual Suites

```bash
# Test 1: Inventory
pytest tests/calibration_system/test_inventory_consistency.py -v

# Test 2: Layers
pytest tests/calibration_system/test_layer_correctness.py -v

# Test 3: Coverage
pytest tests/calibration_system/test_intrinsic_coverage.py -v

# Test 4: AST
pytest tests/calibration_system/test_ast_extraction_accuracy.py -v

# Test 5: Runtime
pytest tests/calibration_system/test_orchestrator_runtime.py -v

# Test 6: No Hardcoded
pytest tests/calibration_system/test_no_hardcoded_calibrations.py -v

# Test 7: Performance
pytest tests/calibration_system/test_performance_benchmarks.py -v
```

## Manually Test Failure Detection

### 1. Break inventory (should fail)

```bash
# Backup first
cp system/config/calibration/intrinsic_calibration.json /tmp/backup.json

# Remove a method from intrinsic_calibration.json
# Run test - should FAIL
pytest tests/calibration_system/test_inventory_consistency.py -v

# Restore
mv /tmp/backup.json system/config/calibration/intrinsic_calibration.json
```

### 2. Add hardcoded score (should fail)

```bash
# Add to any non-test file: score = 0.75
# Run test - should FAIL
pytest tests/calibration_system/test_no_hardcoded_calibrations.py -v

# Remove the line
```

### 3. Remove executor (should fail)

```bash
# Backup first
cp src/farfan_pipeline/core/orchestrator/executors_methods.json /tmp/backup.json

# Remove one executor from executors_methods.json
# Run test - should FAIL with "Expected 30 executors, found 29"
pytest tests/calibration_system/test_inventory_consistency.py -v

# Restore
mv /tmp/backup.json src/farfan_pipeline/core/orchestrator/executors_methods.json
```

## CI/CD Status

Check GitHub Actions for workflow status:

```
.github/workflows/calibration-validation.yml
```

## Full Documentation

See `tests/calibration_system/README.md` for complete documentation.
