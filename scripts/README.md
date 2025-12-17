# F.A.R.F.A.N Scripts Directory

Utility scripts for F.A.R.F.A.N calibration system validation, contract quality evaluation, and maintenance.

## Available Scripts

### cqvr_evaluator.py

**LATEST** - Complete CQVR (Contract Quality Validation and Remediation) evaluator with all scoring functions, decision logic, and comprehensive reporting.

**Features:**
- ✅ 10 core scoring functions with explicit `Tuple[int, List[str]]` return signatures
- ✅ Deterministic decision engine (PRODUCCION, PARCHEAR, REFORMULAR)
- ✅ JSON reports (machine-readable)
- ✅ Rich console output (human-readable tables)
- ✅ Single contract, batch (25), or all (300) contract evaluation
- ✅ Comprehensive error handling
- ✅ 41 unit tests (100% pass rate)

**Usage:**
```bash
# Single contract
python scripts/cqvr_evaluator.py --contract path/to/contract.json --output-dir reports/cqvr

# Batch processing (25 contracts)
python scripts/cqvr_evaluator.py --batch 1 --output-dir reports/cqvr  # Q001-Q025
python scripts/cqvr_evaluator.py --batch 2 --output-dir reports/cqvr  # Q026-Q050
# ... up to batch 12

# All 300 contracts
python scripts/cqvr_evaluator.py --all --output-dir reports/cqvr

# JSON only (no console output)
python scripts/cqvr_evaluator.py --all --output-dir reports/cqvr --json-only
```

**Scoring Rubric (100 points):**
- **Tier 1**: Critical Components (55 pts)
  - A1: Identity-Schema Coherence (20 pts)
  - A2: Method-Assembly Alignment (20 pts)
  - A3: Signal Requirements (10 pts)
  - A4: Output Schema (5 pts)
- **Tier 2**: Functional Components (30 pts)
  - B1: Pattern Coverage (10 pts)
  - B2: Method Specificity (10 pts)
  - B3: Validation Rules (10 pts)
- **Tier 3**: Quality Components (15 pts)
  - C1: Documentation Quality (5 pts)
  - C2: Human Template (5 pts)
  - C3: Metadata Completeness (5 pts)

**Decision Matrix:**
- `PRODUCCION`: Tier 1 ≥ 45, Total ≥ 80, 0 blockers
- `PARCHEAR`: Tier 1 ≥ 35, Total ≥ 70, ≤ 2 blockers
- `REFORMULAR`: Otherwise

**Output:**
```
CQVR Evaluation Summary     
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric             ┃ Value    ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Total Evaluated    │ 300      │
│ Average Score      │ 66.8/100 │
│ Production Ready   │ 27       │
│ Need Patches       │ 61       │
│ Need Reformulation │ 212      │
└────────────────────┴──────────┘
```

**Testing:**
```bash
pytest tests/test_cqvr_evaluator.py -v -m updated
```

**Documentation:** See `docs/CQVR_EVALUATOR.md`

### cqvr_batch_evaluator.py

**NEW** - Batch contract quality evaluator using CQVR v2.0 rubric. Evaluates executor contracts and generates comprehensive reports.

**Usage:**
```bash
python scripts/cqvr_batch_evaluator.py \
  --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
  --threshold 40 \
  [--contracts Q001.v3.json Q002.v3.json] \
  [--output-dir cqvr_reports] \
  [--fail-below-threshold]
```

**Options:**
- `--contracts-dir`: Directory containing contract JSON files (required)
- `--threshold`: Minimum quality score threshold 0-100 (default: 40)
- `--contracts`: Specific contracts to evaluate (default: all)
- `--output-dir`: Output directory for reports (default: cqvr_reports)
- `--fail-below-threshold`: Exit with error code if any contract fails

**Outputs:**
- `cqvr_evaluation_report.json` - Detailed JSON report with scores
- `cqvr_evaluation_report.md` - Markdown summary report
- `cqvr_dashboard.html` - Interactive HTML dashboard

**Exit codes:**
- `0`: All contracts passed threshold
- `1`: One or more contracts below threshold (with `--fail-below-threshold`)

**Example:**
```bash
$ python scripts/cqvr_batch_evaluator.py \
    --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
    --threshold 40
    
🔍 Evaluating 310 contracts...
📊 Output directory: cqvr_reports
📏 Threshold: 40/100

============================================================
📊 EVALUATION COMPLETE
============================================================
Total contracts: 310
Passed: 308 ✅
Failed: 2 ❌
Pass rate: 99.4%
```

**CI/CD Integration:**
- Automatically runs on contract changes via `.github/workflows/cqvr-validation.yml`
- See `docs/CQVR_CICD_INTEGRATION.md` and `docs/CQVR_QUICK_REFERENCE.md` for details

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

### Calibration System Validation
```yaml
- name: Validate Calibration System
  run: python scripts/validate_calibration_system.py
```

### Contract Quality Validation (CQVR)
```yaml
- name: Evaluate Contract Quality
  run: |
    python scripts/cqvr_batch_evaluator.py \
      --contracts-dir src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized \
      --threshold 40 \
      --fail-below-threshold
```

This ensures both calibration system integrity and contract quality on every commit.

## References

### Calibration System
- Gap analysis: `docs/CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md`
- Calibration guide: `docs/CALIBRATION_GUIDE.md`
- Mathematical foundations: `docs/mathematical_foundations_capax_system.md`

### Contract Quality (CQVR)
- Integration guide: `docs/CQVR_CICD_INTEGRATION.md`
- Quick reference: `docs/CQVR_QUICK_REFERENCE.md`
- GitHub workflow: `.github/workflows/cqvr-validation.yml`

