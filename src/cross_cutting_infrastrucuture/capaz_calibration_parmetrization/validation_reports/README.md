# Calibration Validation Reports

This directory contains validation reports for COHORT 2024 calibration system integrity checks.

## Report Types

### 1. Detailed Reports (JSON)
**File**: `*_detailed.json`

Complete validation results including:
- Summary statistics (total checks, passed, failed, warnings)
- Per-file results with error details
- Status codes per validated item
- Full error message listings

**Example**: `sample_validation_report_detailed.json`

### 2. Summary Reports (JSON)
**File**: `*_summary.json`

Condensed validation overview including:
- Summary statistics only
- Overall pass/fail status
- Critical failure counts per file
- No detailed error listings

**Example**: `sample_validation_report_summary.json`

### 3. Text Reports (TXT)
**File**: `*_critical_failures.txt`

Human-readable format with:
- Executive summary
- Detailed results per file
- Critical failure analysis
- Actionable recommendations
- Next steps guidance

**Example**: `sample_validation_report_critical_failures.txt`

## Validation Checks

### Layer Completeness
- Validates all required layers are present per role
- Checks approved justifications for missing layers
- Role-specific requirements:
  - `SCORE_Q`: 8 layers (`@b`, `@chain`, `@q`, `@d`, `@p`, `@C`, `@u`, `@m`)
  - `INGEST_PDM`, `STRUCTURE`, `EXTRACT`, `AGGREGATE`, `REPORT`, `META_TOOL`, `TRANSFORM`: 4 layers (`@b`, `@chain`, `@u`, `@m`)

**Critical**: Missing layers without approved justifications

### Fusion Weights
- Validates non-negativity: `a_ℓ ≥ 0`, `a_ℓk ≥ 0`
- Validates normalization: `sum(linear) + sum(interaction) = 1.0 ± 1e-9`
- Per-role validation for all 8 roles

**Critical**: Negative weights or normalization violations

### Anti-Universality
- Enforces no method has maximal compatibility everywhere
- Constraint: `min(x_@q, x_@d, x_@p) < 0.9`
- Prevents "universal methods" that claim expertise in all areas

**Critical**: Methods with `min ≥ 0.9`

### Intrinsic Calibration Schema
- Required keys: `b_theory`, `b_impl`, `b_deploy`, `status`
- Scores bounded: `[0, 1]`
- Valid statuses: `{computed, pending, excluded, none}`
- Forbidden keys: `_temp`, `_debug`, `internal_state`

**Critical**: Missing keys, out-of-bounds scores, invalid status

### Score Boundedness
- All calibration scores in `[0, 1]`
- Validates across all scoring components
- Type checking (numeric values required)

**Critical**: Any score outside `[0, 1]`

## Sample Reports

### `sample_validation_report_detailed.json`
Shows validation with 2 failures and 1 warning:
- Fusion weights: Reference-only file
- Method compatibility: Anti-universality violation
- Questionnaire: Reference-only (warning)

### `sample_validation_report_summary.json`
Condensed version of the same validation run showing only critical failures.

### `sample_validation_report_passed.json`
Complete successful validation with all 150 checks passed.

### `sample_validation_report_critical_failures.txt`
Comprehensive text report with 15 failures across multiple categories:
- Layer completeness violations (2)
- Fusion weight violations (3)
- Anti-universality violations (6)
- Schema violations (4)
- Environment warnings (3)

Includes detailed analysis and remediation steps.

## Generating Reports

### From Python
```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration_validator import (
    CalibrationValidator
)

validator = CalibrationValidator()

# Run validation
report = validator.validate_config_files(pillar="all")

# Generate detailed JSON report
validator.generate_validation_report(
    report, 
    "validation_reports/my_validation.json",
    format="detailed"
)

# Generate summary JSON report
validator.generate_validation_report(
    report,
    "validation_reports/my_validation_summary.json", 
    format="summary"
)

# Generate text report
validator.generate_validation_report(
    report,
    "validation_reports/my_validation.txt",
    format="detailed"
)
```

### Convenience Function
```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration_validator import (
    validate_all_pillars
)

report = validate_all_pillars()
print(f"Status: {report['validation_summary']}")
```

## Interpreting Results

### Status Codes
- `PASSED`: All checks passed (failed=0)
- `FAILED`: One or more checks failed (failed>0)

### Per-Item Status
- `OK`: Item passed validation
- `FAILED`: Item failed one or more checks
- `REFERENCE_ONLY`: Stub file, full validation skipped

### Error Severity
1. **Critical Failures**: Violations that break system contracts
   - Layer completeness without justification
   - Fusion weight normalization violations
   - Anti-universality violations
   - Schema compliance failures
   - Out-of-bounds scores

2. **Warnings**: Issues that should be addressed but don't break contracts
   - Reference-only files
   - Missing optional configurations
   - Suboptimal parameter choices

## Remediation Workflow

1. **Run Validation**
   ```python
   validator = CalibrationValidator()
   report = validator.validate_config_files(pillar="all")
   ```

2. **Review Failures**
   - Check `report["validation_summary"]["failed"]` count
   - Examine `report["results"][file]["errors"]` for each file

3. **Fix Issues**
   - Layer completeness: Add missing layers or approved justifications
   - Fusion weights: Adjust weights to satisfy constraints
   - Anti-universality: Reduce max compatibility scores
   - Schema: Fix missing keys, bounds, or status values

4. **Re-run Validation**
   - Repeat until `report["validation_summary"]["failed"] == 0`

5. **Document Exceptions**
   - Any approved deviations must be documented in method configs
   - Use `justifications` field for layer exceptions

## Continuous Validation

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
python -c "
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration_validator import validate_all_pillars
report = validate_all_pillars()
if report['validation_summary']['failed'] > 0:
    print('VALIDATION FAILED')
    exit(1)
"
```

### CI/CD Integration
```yaml
# .github/workflows/validate.yml
name: Calibration Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run calibration validation
        run: |
          python -m pytest tests/test_calibration_validators.py -v
```

## File Naming Convention

- `{timestamp}_validation_report_detailed.json`: Detailed JSON report
- `{timestamp}_validation_report_summary.json`: Summary JSON report  
- `{timestamp}_validation_report.txt`: Text report
- `sample_*.{json,txt}`: Example reports for reference

Example: `2024-12-15T14-22-18_validation_report_detailed.json`

## Version History

- **v1.0.0** (2024-12-15): Initial implementation
  - Layer completeness validation
  - Fusion weight validation
  - Anti-universality validation
  - Intrinsic calibration schema validation
  - Score boundedness validation
  - Three-pillar config file validation
  - Comprehensive report generation
