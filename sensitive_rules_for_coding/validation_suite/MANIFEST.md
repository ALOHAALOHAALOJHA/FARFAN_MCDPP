# Validation Suite Manifest

## Purpose

This validation suite provides comprehensive integrity checks for the F.A.R.F.A.N calibration system. It is marked **SENSITIVE** due to its critical role in maintaining system correctness and detecting configuration corruption.

## Classification

**Security Level**: SENSITIVE  
**Category**: Calibration Integrity & System Validation  
**Folder**: `sensitive_rules_for_coding/validation_suite/`

## Components

### Core Modules

1. **`validators.py`** (819 lines)
   - Contains all 6 validation functions
   - Pure Python, no external dependencies
   - Returns structured ValidationResult for each validator

2. **`runner.py`** (242 lines)
   - Automated test runner
   - Executes all validators in sequence
   - Generates comprehensive reports
   - CLI entry point

3. **`__init__.py`** (23 lines)
   - Public API exports
   - Clean module interface

4. **`__main__.py`** (5 lines)
   - CLI entry point for `python -m` execution

5. **`examples.py`** (251 lines)
   - Usage examples for all validators
   - Interactive example runner
   - Best practices demonstrations

### Documentation

1. **`README.md`**
   - Comprehensive usage guide
   - Validator descriptions
   - API reference
   - CLI documentation

2. **`MANIFEST.md`** (this file)
   - Component inventory
   - Security classification
   - Maintenance guidelines

### Tests

1. **`tests/test_validation_suite.py`** (420 lines)
   - Unit tests for all validators
   - Integration tests for runner
   - Test coverage for edge cases
   - Marked with `@pytest.mark.updated`

## Validators Inventory

| Validator | Purpose | Critical | Lines |
|-----------|---------|----------|-------|
| `validate_layer_completeness` | Verify all methods have required layers per role | Yes | ~115 |
| `validate_fusion_weights` | Check Choquet weight normalization (sum=1.0±1e-9) | Yes | ~140 |
| `validate_anti_universality` | Ensure no method is maximal everywhere | Yes | ~130 |
| `validate_intrinsic_calibration` | Validate @b layer schema correctness | Yes | ~120 |
| `validate_config_files` | Verify all COHORT_2024 JSONs load | Yes | ~85 |
| `validate_boundedness` | Check all scores in [0,1] | Yes | ~145 |

## Expected Files Structure

```
sensitive_rules_for_coding/validation_suite/
├── __init__.py
├── __main__.py
├── validators.py
├── runner.py
├── examples.py
├── README.md
├── MANIFEST.md
└── reports/  (created at runtime)
    └── *.json
```

## Configuration Dependencies

The validation suite expects the following directory structure:

```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/
├── calibration/
│   ├── COHORT_2024_canonical_method_inventory.json
│   ├── COHORT_2024_fusion_weights.json
│   ├── COHORT_2024_intrinsic_calibration.json
│   ├── COHORT_2024_layer_assignment.py
│   └── ...other COHORT_2024_*.json files
└── parametrization/
    └── COHORT_2024_*.json files
```

## Usage Patterns

### As Python Module
```python
from sensitive_rules_for_coding.validation_suite import run_all_validations
report = run_all_validations(verbose=True)
```

### As CLI Tool
```bash
python -m sensitive_rules_for_coding.validation_suite.runner --detailed
```

### In CI/CD Pipeline
```bash
python -m sensitive_rules_for_coding.validation_suite.runner --quiet
```

### Individual Validators
```python
from sensitive_rules_for_coding.validation_suite import validate_fusion_weights
result = validate_fusion_weights()
assert result["passed"]
```

## Error Categories

### Hard Failures (Validation Fails)
- Missing required layers for role
- Fusion weights sum ≠ 1.0 ± tolerance
- Negative weights (a_ℓ < 0 or a_ℓk < 0)
- Scores out of bounds [0,1]
- NaN or infinite values
- JSON parse errors
- Missing required schema fields
- Universal method detected

### Soft Warnings (Validation Passes)
- Missing recommended fields
- Stub files detected
- Unknown roles encountered
- Missing metadata
- Near-universal methods (>95% maximal)

## Security Considerations

### Why SENSITIVE?

1. **Core System Integrity**: Validates mathematical foundations of calibration
2. **Configuration Security**: Detects tampering or corruption
3. **Operational Safety**: Prevents deployment of invalid configurations
4. **Audit Trail**: Generates reports for compliance verification

### Access Control

- Read-only access to configuration files
- No modification of source data
- Report generation only
- No network access required

### Validation Reports

Reports may contain:
- Configuration file paths
- Error messages with system details
- Weight values and sums
- Method identifiers
- Performance metrics

**Storage**: Keep validation reports in `sensitive_rules_for_coding/validation_suite/reports/`

## Maintenance Guidelines

### When to Update

1. **Calibration Schema Changes**
   - Update `LAYER_REQUIREMENTS` in validators.py
   - Add new validators if needed
   - Update tests

2. **New Role Types**
   - Add to `LAYER_REQUIREMENTS` dict
   - Update documentation
   - Add test cases

3. **Tolerance Adjustments**
   - Modify default tolerance parameters
   - Document rationale
   - Update tests

4. **New COHORT Releases**
   - Verify compatibility with new COHORT files
   - Update file path patterns if needed
   - Run full validation suite

### Testing Requirements

- All validators must have unit tests
- Integration tests for runner
- Edge cases covered
- Test data in temporary directories
- Marked with `@pytest.mark.updated`

### Code Quality Standards

- Type hints for all functions
- Docstrings with Args, Returns, Raises
- No external dependencies (stdlib only)
- Python 3.12+ compatibility
- Follow F.A.R.F.A.N code conventions

## Performance Characteristics

- **Layer Completeness**: O(n) where n = number of methods
- **Fusion Weights**: O(k) where k = number of weights
- **Anti-Universality**: O(n×m) where n = methods, m = contexts
- **Intrinsic Calibration**: O(c) where c = components
- **Config Files**: O(f) where f = number of files
- **Boundedness**: O(s) where s = total scores

**Expected Runtime**: <5 seconds for typical configurations

## Integration Points

### With Calibration System
- Reads COHORT_2024 configuration files
- Validates layer assignments
- Checks weight normalization

### With Testing Framework
- pytest integration
- Test markers for CI/CD
- Test fixtures for temp data

### With CI/CD Pipeline
- Exit code 0 = pass, 1 = fail
- JSON reports for artifact storage
- Quiet mode for automated runs

## Version History

- **v1.0.0** (2025-01-30): Initial implementation
  - 6 core validators
  - CLI runner
  - Comprehensive test suite
  - Full documentation

## Contact & Support

For issues, questions, or contributions related to the validation suite:
- See main repository documentation
- Follow F.A.R.F.A.N contribution guidelines
- Maintain sensitivity classification

## License

Subject to the same license as the F.A.R.F.A.N project.
