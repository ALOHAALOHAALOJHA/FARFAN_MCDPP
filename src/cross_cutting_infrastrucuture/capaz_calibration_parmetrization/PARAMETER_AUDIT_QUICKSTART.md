# Parameter Audit Quick Start Guide

## 🚀 Run the Audit (1 Command)

```bash
cd /path/to/F.A.R.F.A.N
python src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/run_parameter_audit.py
```

**Output:** Reports in `artifacts/audit_reports/`

## 📊 What Gets Checked

| Category | Examples | Why It Matters |
|----------|----------|----------------|
| **Calibration Weights** | `weight = 0.35` | Must be in COHORT_2024 config for governance |
| **Calibration Scores** | `base_score = 0.65` | Core to method quality assessment |
| **Thresholds** | `threshold = 0.7` | Affects pass/fail decisions |
| **Runtime Params** | `timeout = 300` | Should be configurable |

## ✅ Passing Criteria

**PASS** = Zero CRITICAL violations

- All weights/scores in COHORT_2024 config files
- All executors load parameters from ExecutorConfig
- No hardcoded calibration values in core code

## 📁 Generated Reports

1. **`CERTIFICATION_SUMMARY.md`** - Start here! Overall status and guidance
2. **`violations_audit_report.md`** - Detailed violation list
3. **`executor_parameter_validation.md`** - Executor-specific issues
4. **`violations_audit_report.json`** - Machine-readable data

## 🔧 Fix Violations

### CRITICAL: Hardcoded Weight/Score

```python
# ❌ Before
weight = 0.35

# ✅ After
from farfan_pipeline.core.calibration.parameter_loader import get_parameter_loader
loader = get_parameter_loader()
weight = loader.get("component.weight", 0.35)
```

### HIGH: Hardcoded Threshold

```python
# ❌ Before
threshold = 0.7

# ✅ After
# 1. Add to COHORT_2024_intrinsic_calibration.json
# 2. Load via config
threshold = config.get("threshold", 0.7)
```

### MEDIUM: Hardcoded Timeout

```python
# ❌ Before
self.timeout = 300

# ✅ After
from canonic_phases.Phase_two.executor_config import ExecutorConfig
config = ExecutorConfig.load()
self.timeout = config.get('timeout', 300)
```

## 🎯 Quick Commands

```bash
# Verbose output
python run_parameter_audit.py --verbose

# Custom output directory
python run_parameter_audit.py --output-dir my/reports/

# Skip executor check (faster)
python run_parameter_audit.py --no-executor-check

# Help
python run_parameter_audit.py --help
```

## 🔍 Understand Results

### Exit Codes
- `0` = PASS ✅
- `1` = FAIL ❌

### Severity Levels

| Level | Count Field | Meaning | Blocks Certification? |
|-------|-------------|---------|----------------------|
| CRITICAL | `critical_violations` | Calibration weights/scores | ✅ YES |
| HIGH | `high_violations` | Thresholds/gates | ❌ NO |
| MEDIUM | `medium_violations` | Runtime parameters | ❌ NO |
| LOW | `low_violations` | Minor issues | ❌ NO |

## 📚 Configuration Files

These files define valid parameters:

```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/
├── calibration/
│   ├── COHORT_2024_intrinsic_calibration.json    # Weights, scores, thresholds
│   ├── COHORT_2024_fusion_weights.json           # Layer fusion parameters
│   ├── COHORT_2024_method_compatibility.json     # Compatibility scores
│   └── COHORT_2024_runtime_layers.json           # Runtime layer scores
└── parametrization/
    ├── COHORT_2024_executor_config.json          # Executor parameters
    └── COHORT_2024_runtime_layers.json           # Runtime configs
```

## 🚨 Common Issues

### "Scanner reports 0 files scanned"
**Fix:** Check that `src/` directory exists and contains Python files

### "Config file not found"
**Fix:** Ensure you're running from project root and COHORT_2024 files exist

### "Many false positives"
**Fix:** Check that exclusion patterns are working (test files should be excluded)

## 🔄 Remediation Workflow

1. **Run audit**: `python run_parameter_audit.py`
2. **Check `CERTIFICATION_SUMMARY.md`**: See overall status
3. **Review `violations_audit_report.md`**: Find specific violations
4. **Fix CRITICAL violations first**: Move values to config
5. **Re-run audit**: Verify fixes
6. **Repeat until PASS**: Continue until zero critical violations

## 💡 Best Practices

### ✅ DO
- Run audit before every commit
- Address CRITICAL violations immediately
- Put all calibration values in COHORT_2024 config
- Load parameters via `ExecutorConfig` or parameter loaders
- Document configuration changes

### ❌ DON'T
- Hardcode calibration weights in source code
- Use magic numbers for thresholds
- Hardcode timeouts in executors
- Skip audit checks in CI/CD

## 📞 Need Help?

1. **Full Documentation**: See `PARAMETER_AUDIT_README.md`
2. **Calibration System**: See `CALIBRATION_INTEGRATION.md`
3. **COHORT Manifest**: See `COHORT_MANIFEST.json`

## 🎓 Example Session

```bash
$ python run_parameter_audit.py
================================================================================
COMPREHENSIVE PARAMETER AUDIT
================================================================================
Source: /path/to/src
Config: /path/to/config
Output: /path/to/artifacts/audit_reports
================================================================================

>>> Phase 1: General Parameter Scan
--------------------------------------------------------------------------------
2024-12-15 10:30:00 - Loaded intrinsic calibration...
2024-12-15 10:30:01 - Loaded fusion weights...
2024-12-15 10:30:02 - Scan complete: 187 files, 12 violations

>>> Phase 2: Executor Parameter Validation
--------------------------------------------------------------------------------
2024-12-15 10:30:03 - Executor validation complete: 3 violations found

>>> Phase 3: Unified Report Generation
--------------------------------------------------------------------------------
2024-12-15 10:30:04 - Unified certification report: CERTIFICATION_SUMMARY.md

================================================================================
AUDIT COMPLETE
================================================================================
Files Scanned: 187
Violations: 12
Critical: 0
Executor Issues: 3
Status: ✅ CERTIFICATION PASSED
================================================================================
```

---

**Quick Reference Card**

```
┌─────────────────────────────────────────────────────────┐
│  F.A.R.F.A.N Parameter Audit Quick Reference            │
├─────────────────────────────────────────────────────────┤
│  RUN:    python run_parameter_audit.py                  │
│  CHECK:  artifacts/audit_reports/CERTIFICATION_SUMMARY.md│
│  PASS:   Zero CRITICAL violations                       │
│  FIX:    Move values → COHORT_2024 config files         │
│  VERIFY: Re-run audit                                   │
└─────────────────────────────────────────────────────────┘
```

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-15
