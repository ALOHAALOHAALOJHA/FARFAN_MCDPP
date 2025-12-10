# F.A.R.F.A.N Scripts Directory

Utility scripts for F.A.R.F.A.N calibration system validation and maintenance.

## Available Scripts

### validate_calibration_system.py

Validates the calibration system against expected products, quality metrics, and mathematical constraints.

**Usage:**
```bash
python scripts/validate_calibration_system.py [--output OUTPUT_PATH]
```

**What it validates:**
- ✅ Configuration files (7 JSON files)
- ✅ Fusion weight constraints (sum to 1.0, non-negative)
- ✅ Implementation files (11 Python modules)
- ✅ Test coverage (9 test files)
- ⚠️  Evidence infrastructure (trace directories)
- ⚠️  Artifact generation (certificates, cache, validation reports)
- ✅ Documentation completeness (5 markdown files)

**Output:**
- Console summary with pass/fail/warning counts
- JSON report at `artifacts/validation/calibration_validation_report.json`

**Exit codes:**
- `0`: All critical checks passed (PRODUCTION_READY or OPERATIONAL_WITH_WARNINGS)
- `1`: Some critical checks failed (NEEDS_ATTENTION or NOT_READY)

**Example:**
```bash
$ python scripts/validate_calibration_system.py
============================================================
CALIBRATION SYSTEM VALIDATION
============================================================
Timestamp: 2024-12-10T02:09:06.330049
Based on: docs/CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md

=== Validating Configuration Files ===
  COHORT_2024_intrinsic_calibration.json: ✅
  ...

============================================================
VALIDATION SUMMARY
============================================================
Total Checks: 39
✅ Passed: 34 (87.2%)
❌ Failed: 0 (0.0%)
⚠️  Warnings: 5 (12.8%)

✅ All critical checks passed - Some warnings need attention
```

## Addressing Warnings

The validation script may report warnings for empty directories:

- `evidence_traces/base_layer/` - Evidence traces for base layer calibration
- `evidence_traces/chain_layer/` - Evidence traces for chain layer validation
- `evidence_traces/fusion/` - Evidence traces for Choquet fusion
- `artifacts/certificates/` - Calibration certificates for methods
- `artifacts/calibration_cache/` - Runtime calibration cache

These directories are created but await evidence generation from calibration runs.

## Integration with CI/CD

Add to CI pipeline:

```yaml
- name: Validate Calibration System
  run: python scripts/validate_calibration_system.py
```

This ensures calibration system integrity on every commit.

## References

- Gap analysis: `docs/CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md`
- Calibration guide: `docs/CALIBRATION_GUIDE.md`
- Mathematical foundations: `docs/mathematical_foundations_capax_system.md`
