# Calibration System Validation - Comprehensive Quality Gate

## Executive Summary

A comprehensive all-or-nothing validation suite has been implemented to ensure the calibration system meets production-ready standards. This system enforces strict quality gates where **ANY single test failure blocks deployment**.

## Validation Architecture

### 7 Critical Test Suites

1. **Inventory Consistency** - Ensures all methods are defined across all JSON files
2. **Layer Correctness** - Validates 30 executors have all 8 architectural layers
3. **Intrinsic Coverage** - Verifies ≥80% methods have computed calibrations + all executors operational
4. **AST Extraction Accuracy** - Compares extracted signatures vs actual source code
5. **Orchestrator Runtime** - Tests layer evaluation and aggregation with real contexts
6. **No Hardcoded Calibrations** - Scans for magic numbers in calibration-sensitive code
7. **Performance Benchmarks** - Measures load times and calibration speed

### Quality Gate Rules

```
IF ANY test fails:
  → Generate calibration_system_failure_report.md
  → Mark system as 'NOT READY FOR PRODUCTION'
  → BLOCK merge in CI/CD
  → ABORT deployment
```

## File Structure

```
tests/calibration_system/
├── __init__.py                          # Package initialization
├── README.md                            # Detailed test documentation
├── manual_verification.py               # Manual verification script
├── generate_failure_report.py           # Failure report generator
├── test_inventory_consistency.py        # Test 1: Method inventory sync
├── test_layer_correctness.py            # Test 2: 8-layer architecture
├── test_intrinsic_coverage.py           # Test 3: ≥80% coverage
├── test_ast_extraction_accuracy.py      # Test 4: Signature validation
├── test_orchestrator_runtime.py         # Test 5: Runtime integrity
├── test_no_hardcoded_calibrations.py    # Test 6: No magic numbers
└── test_performance_benchmarks.py       # Test 7: Speed requirements

.github/workflows/
└── calibration-validation.yml           # CI/CD integration

system/config/calibration/
├── intrinsic_calibration.json           # Method calibrations (MUST be populated)
└── intrinsic_calibration_triage.py      # Calibration computation script

src/farfan_pipeline/core/orchestrator/
└── executors_methods.json               # 30 executors × methods inventory
```

## Running Validation

### Local Development

```bash
# Run all validation tests
pytest tests/calibration_system/ -v

# Run specific test suite
pytest tests/calibration_system/test_inventory_consistency.py -v

# Manual verification (no pytest required)
python3 tests/calibration_system/manual_verification.py

# Generate failure report manually
python tests/calibration_system/generate_failure_report.py \
  --test1 success --test2 failure --test3 success \
  --test4 success --test5 success --test6 failure --test7 success \
  --output calibration_system_failure_report.md
```

### CI/CD Integration

The validation suite runs automatically on:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Manual workflow dispatch
- Nightly at 3:00 AM UTC

**Merge is blocked if ANY test fails.**

## Test Details

### Test 1: Inventory Consistency

**Validates:**
- `executors_methods.json` has 30 executors (D1-Q1 through D6-Q5)
- All methods have `class` and `method` fields
- No duplicate methods within executors
- All executor methods exist in `intrinsic_calibration.json`
- All calibrations have valid `status` field

**Failure Impact:** Runtime errors, calibration mismatches

### Test 2: Layer Correctness

**Validates:**
- All 8 layers defined: ingestion, extraction, transformation, validation, aggregation, scoring, reporting, meta
- Each executor has methods in ALL 8 layers
- `LAYER_REQUIREMENTS` mapping complete
- Layer execution order is acyclic
- No orphan layers

**Failure Impact:** Broken execution pipeline

### Test 3: Intrinsic Coverage

**Validates:**
- ≥80% of all methods have `status='computed'`
- All 30 executors have ≥1 method with `status='computed'`
- No executor entirely excluded/manual
- Excluded methods documented

**Failure Impact:** System relies on defaults, fails at runtime

### Test 4: AST Extraction Accuracy

**Validates:**
- Method signatures can be extracted via AST parsing
- Executor methods exist in source code
- Stored signatures match actual signatures
- Signature mismatch rate ≤5%

**Failure Impact:** Method execution failures

### Test 5: Orchestrator Runtime

**Validates:**
- Layers execute in correct order
- Calibration context resolution works
- Method execution can be simulated
- No circular dependencies

**Failure Impact:** Runtime errors prevent execution

### Test 6: No Hardcoded Calibrations

**Validates:**
- No hardcoded thresholds, weights, scores
- All calibration parameters externalized
- Proper use of `calibration_registry`
- Only allowed constants (0, 1, 0.5) permitted

**Failure Impact:** Violates "SIN CARRETA" principle, prevents systematic calibration

### Test 7: Performance Benchmarks

**Validates:**
- Load `intrinsic_calibration.json` < 1 second
- Calibrate 30 executors < 5 seconds
- Calibrate 200 methods < 30 seconds
- File size < 10 MB

**Failure Impact:** Poor user experience

## Current Status

Based on manual verification:

```
✅ PASS: executors_methods.json structure (30 executors, 355 total methods)
❌ FAIL: intrinsic_calibration.json (empty - needs population)
❌ FAIL: inventory_consistency (243 methods missing calibration)
❌ FAIL: layer_coverage (methods missing 'layer' field)
✅ PASS: failure_simulation (detection working correctly)
```

**Status: NOT READY FOR PRODUCTION**

## Remediation Steps

### 1. Populate intrinsic_calibration.json

```bash
# Run calibration triage to compute intrinsic scores
python system/config/calibration/intrinsic_calibration_triage.py
```

### 2. Add Layer Field to executors_methods.json

Each method entry needs a `layer` field:

```json
{
  "class": "BayesianNumericalAnalyzer",
  "method": "evaluate_policy_metric",
  "layer": "extraction"  // ADD THIS
}
```

### 3. Re-run Validation

```bash
pytest tests/calibration_system/ -v
```

## Manual Verification Testing

To verify the system correctly detects failures:

### Test 1: Break Inventory Consistency

```bash
# Remove a method from intrinsic_calibration.json
# Run: pytest tests/calibration_system/test_inventory_consistency.py -v
# Expected: Test should FAIL
```

### Test 2: Add Hardcoded Score

```bash
# In a non-test file, add: score = 0.75
# Run: pytest tests/calibration_system/test_no_hardcoded_calibrations.py -v
# Expected: Test should FAIL
```

### Test 3: Remove Executor

```bash
# Delete one executor from executors_methods.json
# Run: pytest tests/calibration_system/test_inventory_consistency.py -v
# Expected: Test should FAIL with "Expected 30 executors, found 29"
```

## Failure Report Format

When tests fail, `calibration_system_failure_report.md` is generated:

```markdown
# CALIBRATION SYSTEM FAILURE REPORT

**Generated:** 2024-12-02T12:00:00

## ❌ STATUS: NOT READY FOR PRODUCTION

**3 of 7 validation tests FAILED**

### Critical Failures

❌ **Test 1: Inventory Consistency**: failure
❌ **Test 3: Intrinsic Coverage (≥80%)**: failure
❌ **Test 6: No Hardcoded Calibrations**: failure
✅ **Test 2: Layer Correctness**: success
...

## Failure Analysis

### Test 1: Inventory Consistency

**Purpose:** Verifies all methods are consistently defined across JSON files
**Impact:** Inconsistent inventories cause runtime errors and calibration mismatches

**Remediation Steps:**
1. Ensure all methods in executors_methods.json exist in intrinsic_calibration.json
2. Remove orphaned calibration entries
3. Verify all 30 executors are properly defined

**Specific Failures:**
- `BayesianNumericalAnalyzer.evaluate_policy_metric`
  - Method missing from intrinsic_calibration.json
...
```

## Integration with Existing Systems

### Contract Verification Pipeline

The calibration validation runs in parallel with contract verification:

```
.github/workflows/
├── contract-verification.yml       # Existing contract tests
└── calibration-validation.yml      # New calibration tests
```

Both must pass for merge approval.

### Dependency Lockdown

Calibration tests respect the dependency lockdown policy:
- No external imports beyond stdlib + pytest
- Tests are pure Python with JSON parsing
- AST analysis uses stdlib `ast` module

## Success Criteria

System is production-ready when:

1. ✅ All 30 executors consistently defined
2. ✅ All executors have all 8 layers
3. ✅ ≥80% methods have computed calibrations
4. ✅ All 30 executors have ≥1 computed method
5. ✅ Signature mismatch ≤5%
6. ✅ No hardcoded calibration values
7. ✅ Performance within limits

**If any criterion fails: ❌ NOT READY FOR PRODUCTION**

## Monitoring and Alerts

### GitHub Actions

- ✅ Automated runs on push/PR
- ❌ Blocks merge on failure
- 📊 Uploads test results as artifacts
- 💬 Comments on PR with status

### Artifacts Generated

1. `test-results/*.xml` - JUnit XML test results
2. `calibration_system_failure_report.md` - Detailed failure analysis
3. `calibration-test-results` - Full pytest output

Retained for 30 days (90 days for failure reports).

## Dependencies

```bash
pip install pytest pytest-cov pytest-timeout
```

Or use existing:

```bash
pip install -r requirements-dev.txt
```

## Support and Troubleshooting

### Common Issues

**Issue:** "No module named pytest"
**Solution:** `pip install pytest` or use requirements-dev.txt

**Issue:** "intrinsic_calibration.json is empty"
**Solution:** Run `python system/config/calibration/intrinsic_calibration_triage.py`

**Issue:** "Methods missing 'layer' field"
**Solution:** Add `"layer": "extraction"` (or appropriate layer) to each method

**Issue:** "30 executors missing layers"
**Solution:** Ensure each executor has methods in all 8 layers

### Getting Help

1. Review `tests/calibration_system/README.md` for detailed docs
2. Check GitHub Actions artifacts for test output
3. Run manual verification: `python3 tests/calibration_system/manual_verification.py`
4. Examine failure report: `calibration_system_failure_report.md`
5. Consult `AGENTS.md` for calibration architecture

## Maintenance

### Adding New Tests

1. Create `tests/calibration_system/test_new_validation.py`
2. Follow existing test structure (class-based, pytest fixtures)
3. Add to `.github/workflows/calibration-validation.yml`
4. Update `generate_failure_report.py` with test metadata
5. Document in `tests/calibration_system/README.md`

### Updating Thresholds

To change quality thresholds:

```python
# In test_intrinsic_coverage.py
MIN_COVERAGE_PERCENT = 80.0  # Change to 85.0 for stricter enforcement

# In test_performance_benchmarks.py
MAX_LOAD_TIME_SECONDS = 1.0  # Change to 0.5 for faster requirement
```

## Changelog

### 2024-12-02 - Initial Implementation

- Created 7 comprehensive test suites
- Integrated with GitHub Actions CI/CD
- Added all-or-nothing quality gate
- Implemented failure report generation
- Added manual verification script
- Updated .gitignore for test artifacts

## License

Part of the F.A.R.F.A.N. Mechanistic Policy Pipeline project.
See project LICENSE file for details.
