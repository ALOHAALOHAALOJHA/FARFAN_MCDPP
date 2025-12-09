# F.A.R.F.A.N Calibration Validation Suite

## Overview

Comprehensive validation suite for the F.A.R.F.A.N calibration system. This suite implements critical integrity checks to ensure the calibration system maintains mathematical correctness, schema compliance, and operational soundness.

## Validators

### 1. `validate_layer_completeness`
**Purpose**: Verify all methods have required layers per role.

**Checks**:
- All methods have `layers` field
- Layers match role requirements (executor needs all 8 layers: @b, @chain, @q, @d, @p, @C, @u, @m)
- No missing required layers for any role

**Usage**:
```python
from sensitive_rules_for_coding.validation_suite import validate_layer_completeness

result = validate_layer_completeness(
    inventory_path="path/to/COHORT_2024_canonical_method_inventory.json"
)
print(result["passed"])
```

### 2. `validate_fusion_weights`
**Purpose**: Validate Choquet fusion weight normalization.

**Checks**:
- Linear weights sum + interaction weights sum = 1.0 ± 1e-9
- All weights are non-negative (a_ℓ ≥ 0, a_ℓk ≥ 0)
- Proper JSON structure and required keys present

**Formula**: `Cal(I) = Σ(a_ℓ · x_ℓ) + Σ(a_ℓk · min(x_ℓ, x_k))`

**Usage**:
```python
from sensitive_rules_for_coding.validation_suite import validate_fusion_weights

result = validate_fusion_weights(
    fusion_weights_path="path/to/COHORT_2024_fusion_weights.json",
    tolerance=1e-9
)
```

### 3. `validate_anti_universality`
**Purpose**: Ensure no method is maximal everywhere (anti-universality principle).

**Checks**:
- No method has perfect score (1.0) across all contexts
- Methods show variation across dimensions/questions
- No method dominates universally

**Rationale**: Universal optimality would indicate calibration collapse or overfitting.

**Usage**:
```python
from sensitive_rules_for_coding.validation_suite import validate_anti_universality

# With pre-loaded data
result = validate_anti_universality(scores_data=scores_dict)

# With file path
result = validate_anti_universality(scores_path="path/to/scores.json")
```

### 4. `validate_intrinsic_calibration`
**Purpose**: Validate intrinsic calibration (@b layer) schema correctness.

**Checks**:
- Required fields present (base_layer, components)
- Weight sums are valid (must equal 1.0)
- All required components present: b_theory, b_impl, b_deploy
- Subcomponent weights normalized

**Usage**:
```python
from sensitive_rules_for_coding.validation_suite import validate_intrinsic_calibration

result = validate_intrinsic_calibration(
    calibration_path="path/to/COHORT_2024_intrinsic_calibration.json"
)
```

### 5. `validate_config_files`
**Purpose**: Validate all COHORT_2024 JSON files load successfully.

**Checks**:
- All COHORT_2024_*.json files parse without errors
- Required metadata fields present (_cohort_metadata)
- No JSON syntax errors

**Usage**:
```python
from sensitive_rules_for_coding.validation_suite import validate_config_files

result = validate_config_files(
    config_dir="src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization"
)
```

### 6. `validate_boundedness`
**Purpose**: Validate all scores are bounded in [0, 1].

**Checks**:
- All scores ≥ 0.0
- All scores ≤ 1.0
- No NaN or infinite values
- Handles nested score structures

**Usage**:
```python
from sensitive_rules_for_coding.validation_suite import validate_boundedness

result = validate_boundedness(
    scores_data=scores_dict,
    min_bound=0.0,
    max_bound=1.0
)
```

## Running the Full Suite

### Python API

```python
from sensitive_rules_for_coding.validation_suite import run_all_validations, save_report

# Run all validations
report = run_all_validations(
    config_dir="src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization",
    scores_data=None,  # Optional: provide scores data
    scores_path=None,  # Optional: or path to scores file
    verbose=True
)

# Check overall status
if report["overall_passed"]:
    print("All validations passed!")
else:
    print(f"Failed validators: {report['summary']['failed_validators']}")

# Save report
save_report(report, output_path="validation_report.json")
```

### Command Line

```bash
# Run with defaults
python -m sensitive_rules_for_coding.validation_suite.runner

# Specify configuration directory
python -m sensitive_rules_for_coding.validation_suite.runner \
    --config-dir src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization

# Include scores file for anti-universality and boundedness checks
python -m sensitive_rules_for_coding.validation_suite.runner \
    --scores-path path/to/scores.json \
    --output validation_report.json \
    --detailed

# Quiet mode
python -m sensitive_rules_for_coding.validation_suite.runner --quiet
```

### CLI Options

- `--config-dir`: Configuration directory (default: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization`)
- `--scores-path`: Optional path to scores file
- `--output`: Output report path (default: `validation_suite_report.json`)
- `--detailed`: Print detailed report to console
- `--quiet`: Suppress progress messages

## Report Structure

The validation suite generates a comprehensive report:

```json
{
  "execution_timestamp": "2025-01-30T12:00:00.000000Z",
  "total_validators": 6,
  "passed_validators": 6,
  "failed_validators": 0,
  "validation_results": {
    "layer_completeness": {
      "validator_name": "validate_layer_completeness",
      "passed": true,
      "errors": [],
      "warnings": [],
      "details": {}
    },
    ...
  },
  "summary": {
    "overall_status": "PASS",
    "pass_rate": "6/6",
    "total_errors": 0,
    "total_warnings": 0,
    "failed_validators": []
  },
  "overall_passed": true
}
```

## Integration with CI/CD

Add to your CI pipeline:

```bash
# Run validation suite as part of CI
python -m sensitive_rules_for_coding.validation_suite.runner --quiet
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "Validation suite failed!"
    exit 1
fi
```

## Validation Result Schema

Each validator returns a `ValidationResult`:

```python
class ValidationResult(TypedDict):
    validator_name: str       # Validator identifier
    passed: bool             # True if all checks passed
    errors: list[str]        # Critical errors (cause failure)
    warnings: list[str]      # Non-critical warnings
    details: dict[str, Any]  # Detailed validation data
```

## Error Handling

- **Hard Failures**: Missing required fields, invalid weight sums, out-of-bounds scores
- **Soft Warnings**: Missing recommended fields, stub files detected, unknown roles
- **Exceptions**: Caught and reported as validation failures with exception details

## Sensitivity and Security

This validation suite is marked **SENSITIVE** because:
1. Validates core calibration system integrity
2. Detects configuration corruption or tampering
3. Ensures mathematical soundness of aggregation
4. Guards against calibration collapse

Store validation reports in `sensitive_rules_for_coding/validation_suite/reports/`.

## Development

### Running Tests

```bash
pytest tests/test_validation_suite.py -v
```

### Adding New Validators

1. Add validator function to `validators.py`
2. Return `ValidationResult` with proper structure
3. Add to validator list in `runner.py`
4. Write tests in `tests/test_validation_suite.py`
5. Update this README

## Dependencies

- Python 3.12+
- Standard library only (json, pathlib, datetime, typing)
- No external dependencies for core validators

## Maintenance

- Review validators when calibration schema changes
- Update `LAYER_REQUIREMENTS` if role requirements change
- Adjust tolerance values if numerical precision requirements change
- Keep tests synchronized with validator implementations
