# Calibration System Audit - Quick Reference

## One-Command Audit

```bash
cd src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization
python run_complete_audit.py
```

**Output**: `artifacts/audit_reports/LATEST_AUDIT_SUMMARY.txt`

## What Gets Audited

### ✅ Method Inventory (1995+ methods)
- Which methods have intrinsic calibration
- Which layers each method requires
- Calibration status (computed/excluded/pending)

### ✅ Layer Completeness Matrix (8 layers × all methods)
- `@b` Base Layer (intrinsic scores)
- `@chain` Chain Layer (data flow position)
- `@q` Question Layer (question compatibility)
- `@d` Dimension Layer (dimension compatibility)
- `@p` Policy Layer (policy compatibility)
- `@C` Congruence Layer (ensemble coherence)
- `@u` Unit Layer (PDT quality)
- `@m` Meta Layer (governance/transparency)

### ✅ Evaluator Implementation Status
- File exists?
- Compute method present?
- Production logic or stub?
- Integration with orchestrator?

### ✅ Parameter Migration Status
- Hardcoded numeric literals detected
- File:line citations provided
- Suggested fixes generated
- Compliance percentage calculated

## Quick Commands

### Run Individual Audits

```bash
# Full calibration audit
python comprehensive_calibration_audit.py

# Layer implementation check
python layer_implementation_verifier.py

# Parameter scan
python hardcoded_parameter_scanner.py
```

### Check Latest Results

```bash
# Summary
cat artifacts/audit_reports/LATEST_AUDIT_SUMMARY.txt

# Full report (requires jq)
cat artifacts/audit_reports/MASTER_AUDIT_REPORT_*.json | jq '.compliance_status'

# Critical findings only
cat artifacts/audit_reports/MASTER_AUDIT_REPORT_*.json | jq '.critical_findings'
```

## Understanding Results

### Compliance Status

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ `compliant` | All layers implemented, no critical issues | Maintain status |
| ⚠️ `acceptable_with_warnings` | Minor issues, system functional | Address warnings |
| ❌ `non_compliant` | Critical gaps present | **Immediate action required** |

### Layer Quality Scores

| Score | Status | Description |
|-------|--------|-------------|
| 0.8-1.0 | ✅ Good | Fully implemented with production logic |
| 0.4-0.7 | ⚠️ Partial | Exists but incomplete or has issues |
| 0.0-0.3 | ❌ Poor | Stub or missing |

### Violation Severity

| Severity | Description | Priority |
|----------|-------------|----------|
| 🔴 Critical | Weights, thresholds in (0,1) range | Fix immediately |
| 🟠 High | Parameter keywords detected | Fix soon |
| 🟡 Medium | Numeric in scoring context | Address in sprint |
| 🟢 Low | Other numeric literals | Nice to have |

## Common Issues & Fixes

### Issue: Missing Layer Evaluator

```
❌ Layer @q not found
```

**Fix**: Create `COHORT_2024_question_layer.py` with:
```python
def evaluate_question_score(method_id, question_id, compatibility_data):
    # Production implementation here
    return score
```

### Issue: Stub Implementation

```
⚠️ Layer @d has stub (raises NotImplementedError)
```

**Fix**: Replace stub in `COHORT_2024_dimension_layer.py`:
```python
# Remove:
raise NotImplementedError

# Add production logic:
compatibility = compatibility_data.get(method_id, {}).get(dimension_id, 0.5)
return compatibility
```

### Issue: Hardcoded Parameter

```
🔴 src/scorer.py:42 threshold = 0.65
```

**Fix**:
```python
# Before:
threshold = 0.65

# After:
from config_loader import load_config
config = load_config()
threshold = config['threshold']
```

## File Locations

### Audit Scripts
```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/
├── run_complete_audit.py                    # Master runner
├── comprehensive_calibration_audit.py       # Method inventory
├── layer_implementation_verifier.py         # Layer verification
└── hardcoded_parameter_scanner.py           # Parameter scan
```

### Layer Evaluators
```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/
├── COHORT_2024_intrinsic_scoring.py         # @b
├── COHORT_2024_chain_layer.py               # @chain
├── COHORT_2024_question_layer.py            # @q
├── COHORT_2024_dimension_layer.py           # @d
├── COHORT_2024_policy_layer.py              # @p
├── COHORT_2024_congruence_layer.py          # @C
├── COHORT_2024_unit_layer.py                # @u
└── COHORT_2024_meta_layer.py                # @m
```

### Configuration Files
```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/
├── COHORT_2024_intrinsic_calibration.json          # Method calibrations
├── COHORT_2024_canonical_method_inventory.json     # Method catalog
├── COHORT_2024_layer_requirements.json             # Layer specs
└── COHORT_2024_method_compatibility.json           # Compatibility scores
```

### Audit Reports
```
artifacts/audit_reports/
├── MASTER_AUDIT_REPORT_{timestamp}.json     # Complete results
├── LATEST_AUDIT_SUMMARY.txt                 # Human-readable summary
├── canonical_method_inventory_{timestamp}.json
├── calibration_completeness_matrix_{timestamp}.json
├── verification_report_{timestamp}.json
└── parameter_compliance_{timestamp}.json
```

## Reading the Matrix

### Calibration Completeness Matrix

```json
{
  "method_name": {
    "@b": true,      // ✅ Has intrinsic score
    "@chain": false, // ❌ Chain not computed
    "@q": false,     // ❌ Question not computed
    "@d": false,     // ❌ Dimension not computed
    "@p": false,     // ❌ Policy not computed
    "@C": false,     // ❌ Congruence not computed
    "@u": false,     // ❌ Unit not computed
    "@m": false      // ❌ Meta not computed
  }
}
```

**Interpretation**: Only base layer (@b) computed, all contextual layers missing.

### Expected Pattern for SCORE_Q Methods

```json
{
  "executor_method": {
    "@b": true,      // ✅ Required
    "@chain": true,  // ✅ Required
    "@q": true,      // ✅ Required
    "@d": true,      // ✅ Required
    "@p": true,      // ✅ Required
    "@C": true,      // ✅ Required
    "@u": true,      // ✅ Required
    "@m": true       // ✅ Required
  }
}
```

## Workflow

### Initial Setup
```bash
# 1. Run audit
python run_complete_audit.py

# 2. Check summary
cat artifacts/audit_reports/LATEST_AUDIT_SUMMARY.txt

# 3. Identify critical issues
cat artifacts/audit_reports/MASTER_AUDIT_REPORT_*.json | jq '.critical_findings'
```

### Fix Cycle
```bash
# 1. Fix issues (implement layers, migrate parameters)

# 2. Re-run audit
python run_complete_audit.py

# 3. Verify improvements
diff LATEST_AUDIT_SUMMARY.txt previous_summary.txt

# 4. Repeat until compliant
```

### Continuous Monitoring
```bash
# Add to crontab (weekly)
0 0 * * 0 cd /project && python run_complete_audit.py && mail -s "Calibration Audit" team@example.com < artifacts/audit_reports/LATEST_AUDIT_SUMMARY.txt
```

## Exit Codes

| Code | Status | Meaning |
|------|--------|---------|
| 0 | Success | Compliant or acceptable |
| 1 | Warning | Non-compliant (critical issues) |
| 2 | Error | Audit failed to run |

## CI/CD Integration

```yaml
# .github/workflows/audit.yml
name: Calibration Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run audit
        run: python src/.../run_complete_audit.py
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: audit-report
          path: artifacts/audit_reports/LATEST_AUDIT_SUMMARY.txt
```

## Troubleshooting

### "Module not found"
```bash
# Ensure you're in correct directory
pwd  # Should end in capaz_calibration_parmetrization

# Or run with full path
python src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/run_complete_audit.py
```

### "No violations found" (but there should be)
```bash
# Check if scanning correct directory
python hardcoded_parameter_scanner.py

# Verify src/ directory exists
ls -la src/
```

### "JSON decode error"
```bash
# Validate JSON files
cat calibration/COHORT_2024_intrinsic_calibration.json | jq '.' > /dev/null
```

## Key Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Methods Calibrated | 100% | Check report | TBD |
| Layers Implemented | 8/8 | Check report | TBD |
| Layer Quality Avg | > 0.8 | Check report | TBD |
| Parameter Compliance | > 90% | Check report | TBD |

## Next Steps

1. ✅ Run initial audit: `python run_complete_audit.py`
2. 📊 Review `LATEST_AUDIT_SUMMARY.txt`
3. 🔴 Fix critical issues first
4. 🟠 Address high severity issues
5. 🟡 Plan medium severity fixes
6. ✅ Re-audit and verify
7. 🔄 Integrate into CI/CD

---

**Quick Help**: Check `COMPREHENSIVE_AUDIT_README.md` for detailed documentation.
