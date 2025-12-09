# Validation Suite Quick Reference

## One-Line Commands

```bash
# Run full suite (verbose)
python -m sensitive_rules_for_coding.validation_suite.runner

# Run full suite (quiet, for CI/CD)
python -m sensitive_rules_for_coding.validation_suite.runner --quiet

# Run with scores file
python -m sensitive_rules_for_coding.validation_suite.runner --scores-path path/to/scores.json

# Generate detailed report
python -m sensitive_rules_for_coding.validation_suite.runner --detailed --output report.json

# Run examples
python -m sensitive_rules_for_coding.validation_suite.examples
```

## Python API (Copy-Paste Ready)

### Run All Validators
```python
from sensitive_rules_for_coding.validation_suite import run_all_validations
report = run_all_validations(verbose=True)
print(f"Status: {report['summary']['overall_status']}")
```

### Individual Validators

```python
from sensitive_rules_for_coding.validation_suite import *

# Layer completeness
result = validate_layer_completeness()

# Fusion weights
result = validate_fusion_weights(tolerance=1e-9)

# Anti-universality
result = validate_anti_universality(scores_data=my_scores)

# Intrinsic calibration
result = validate_intrinsic_calibration()

# Config files
result = validate_config_files()

# Boundedness
result = validate_boundedness(scores_data=my_scores)
```

### Check Results
```python
if result["passed"]:
    print("✓ Validation passed")
else:
    print("✗ Validation failed")
    for error in result["errors"]:
        print(f"  - {error}")
```

## Validation Checklist

- [ ] Layer completeness: All methods have required layers
- [ ] Fusion weights: Sum = 1.0 ± 1e-9
- [ ] Anti-universality: No method maximal everywhere
- [ ] Intrinsic calibration: Schema correct, weights normalized
- [ ] Config files: All COHORT_2024 JSONs load
- [ ] Boundedness: All scores in [0, 1]

## Common Issues & Fixes

### Issue: Missing layers
**Error**: `Method X missing layers: {'@q', '@d'}`  
**Fix**: Add missing layers to method's layer assignment

### Issue: Fusion weights don't sum to 1.0
**Error**: `Fusion weights sum to 1.05, expected 1.0`  
**Fix**: Renormalize linear and interaction weights

### Issue: Negative weight
**Error**: `Negative linear weight: u = -0.1`  
**Fix**: Ensure all weights are non-negative

### Issue: Score out of bounds
**Error**: `Score above maximum at path: value = 1.5`  
**Fix**: Clip or recalculate scores to [0, 1] range

### Issue: Universal method
**Error**: `Method X is maximal (1.0) across all 30 contexts`  
**Fix**: Review calibration parameters, ensure variation

### Issue: JSON parse error
**Error**: `JSON parse error in file.json: Expecting value`  
**Fix**: Validate JSON syntax, check for trailing commas

## Validator Return Structure

```python
{
    "validator_name": str,
    "passed": bool,
    "errors": list[str],
    "warnings": list[str],
    "details": dict[str, Any]
}
```

## Report Structure

```python
{
    "execution_timestamp": str,
    "total_validators": int,
    "passed_validators": int,
    "failed_validators": int,
    "validation_results": dict[str, ValidationResult],
    "summary": {
        "overall_status": "PASS" | "FAIL",
        "pass_rate": str,
        "total_errors": int,
        "total_warnings": int,
        "failed_validators": list[str]
    },
    "overall_passed": bool
}
```

## File Paths (Defaults)

```python
# Configuration directory
"src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization"

# Inventory
"calibration/COHORT_2024_canonical_method_inventory.json"

# Fusion weights
"calibration/COHORT_2024_fusion_weights.json"

# Intrinsic calibration
"calibration/COHORT_2024_intrinsic_calibration.json"

# Layer assignment
"calibration/COHORT_2024_layer_assignment.py"
```

## Expected Values

| Parameter | Expected Value | Tolerance |
|-----------|----------------|-----------|
| Fusion weights sum | 1.0 | ±1e-9 |
| Score bounds | [0.0, 1.0] | Exact |
| Executor layers | 8 layers | Exact |
| Analyzer layers | 8 layers | Exact |
| Utility layers | 3 layers | Exact |

## Layer Requirements by Role

```python
"executor": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],  # 8 layers
"analyzer": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],  # 8 layers
"score":    ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"],  # 8 layers
"ingest":   ["@b", "@chain", "@u", "@m"],                           # 4 layers
"utility":  ["@b", "@chain", "@m"],                                 # 3 layers
```

## Exit Codes

- `0`: All validations passed
- `1`: One or more validations failed

## Timing Guidelines

| Operation | Expected Time |
|-----------|---------------|
| Single validator | <1 second |
| Full suite (no scores) | <2 seconds |
| Full suite (with scores) | <5 seconds |
| Config file loading | <1 second |

## Import Shortcuts

```python
# Import everything
from sensitive_rules_for_coding.validation_suite import *

# Import runner only
from sensitive_rules_for_coding.validation_suite.runner import run_all_validations

# Import specific validators
from sensitive_rules_for_coding.validation_suite.validators import (
    validate_layer_completeness,
    validate_fusion_weights
)
```

## Debugging Tips

1. **Use verbose mode**: See progress and details
   ```python
   report = run_all_validations(verbose=True)
   ```

2. **Check details field**: Contains specific info
   ```python
   print(result["details"])
   ```

3. **Save report to JSON**: Easier to inspect
   ```python
   from sensitive_rules_for_coding.validation_suite.runner import save_report
   save_report(report, "debug_report.json")
   ```

4. **Run individual validators**: Isolate issues
   ```python
   result = validate_fusion_weights()
   ```

5. **Check warnings**: May indicate underlying issues
   ```python
   for warning in result["warnings"]:
       print(warning)
   ```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run Validation Suite
  run: |
    python -m sensitive_rules_for_coding.validation_suite.runner --quiet
    if [ $? -ne 0 ]; then
      echo "Validation failed"
      exit 1
    fi
```

### GitLab CI
```yaml
validate:
  script:
    - python -m sensitive_rules_for_coding.validation_suite.runner --quiet
  artifacts:
    paths:
      - validation_suite_report.json
```

### Pre-commit Hook
```bash
#!/bin/bash
python -m sensitive_rules_for_coding.validation_suite.runner --quiet
exit $?
```
