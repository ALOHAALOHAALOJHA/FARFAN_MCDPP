# Validation Suite Index

## Quick Navigation

### 🚀 Getting Started
- [README.md](README.md) - Start here for comprehensive overview
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Copy-paste commands and code
- [examples.py](examples.py) - Interactive examples runner

### 📚 Documentation
- [README.md](README.md) - Full user guide and API reference
- [MANIFEST.md](MANIFEST.md) - System manifest and security classification
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference card
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical implementation details
- [INDEX.md](INDEX.md) - This file

### 💻 Implementation
- [validators.py](validators.py) - Core validation functions (6 validators)
- [runner.py](runner.py) - Automated test runner and CLI
- [__init__.py](__init__.py) - Public API exports
- [__main__.py](__main__.py) - CLI entry point
- [examples.py](examples.py) - Usage examples

### 🧪 Testing
- [tests/test_validation_suite.py](../../tests/test_validation_suite.py) - Test suite (21 tests)

## Validators Reference

| Validator | Purpose | File | Tests |
|-----------|---------|------|-------|
| `validate_layer_completeness` | All required layers present per role | [validators.py:32-115](validators.py#L32) | 4 tests |
| `validate_fusion_weights` | Normalization sum=1.0±1e-9 | [validators.py:118-204](validators.py#L118) | 3 tests |
| `validate_anti_universality` | No method maximal everywhere | [validators.py:207-306](validators.py#L207) | 3 tests |
| `validate_intrinsic_calibration` | Schema correctness | [validators.py:309-397](validators.py#L309) | 3 tests |
| `validate_config_files` | All COHORT_2024 JSONs load | [validators.py:400-480](validators.py#L400) | 2 tests |
| `validate_boundedness` | All scores in [0,1] | [validators.py:483-618](validators.py#L483) | 4 tests |

## Common Tasks

### Run Full Suite
```bash
# Verbose mode
python -m sensitive_rules_for_coding.validation_suite.runner

# Quiet mode (for CI/CD)
python -m sensitive_rules_for_coding.validation_suite.runner --quiet
```
📖 See: [QUICK_REFERENCE.md](QUICK_REFERENCE.md#one-line-commands)

### Run Individual Validator
```python
from sensitive_rules_for_coding.validation_suite import validate_fusion_weights
result = validate_fusion_weights()
```
📖 See: [README.md](README.md#validators)

### Run Tests
```bash
pytest tests/test_validation_suite.py -v
```
📖 See: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md#testing-coverage)

### Generate Report
```python
from sensitive_rules_for_coding.validation_suite import run_all_validations, save_report
report = run_all_validations()
save_report(report, "report.json")
```
📖 See: [README.md](README.md#running-the-full-suite)

### Run Examples
```bash
python -m sensitive_rules_for_coding.validation_suite.examples
```
📖 See: [examples.py](examples.py)

## File Descriptions

### Implementation Files

#### `validators.py` (819 lines)
Core validation logic. Contains:
- `ValidationResult` TypedDict
- `LAYER_REQUIREMENTS` constant
- 6 validation functions
- Pure Python, no external dependencies

**Key Functions**:
- `validate_layer_completeness(inventory_path, layer_assignment_path)`
- `validate_fusion_weights(fusion_weights_path, tolerance)`
- `validate_anti_universality(scores_data, scores_path)`
- `validate_intrinsic_calibration(calibration_path)`
- `validate_config_files(config_dir)`
- `validate_boundedness(scores_data, scores_path, min_bound, max_bound)`

#### `runner.py` (242 lines)
Automated test runner and CLI. Contains:
- `ValidationSuiteReport` TypedDict
- `run_all_validations()` - Execute all validators
- `save_report()` - Save to JSON
- `print_detailed_report()` - Console output
- `run_cli()` - CLI entry point

**Key Features**:
- Comprehensive reporting
- Progress tracking
- Exception handling
- CLI with argparse

#### `__init__.py` (23 lines)
Public API interface. Exports:
- All 6 validators
- `run_all_validations`
- `ValidationSuiteReport`

#### `__main__.py` (5 lines)
CLI entry point. Enables:
```bash
python -m sensitive_rules_for_coding.validation_suite.runner
```

#### `examples.py` (251 lines)
Usage examples. Contains:
- 7 example functions
- Interactive runner
- Best practices
- Common patterns

**Examples**:
1. Run single validator
2. Run full suite
3. Validate with scores
4. Validate fusion weights
5. Save and load report
6. Custom config directory
7. Check specific file

### Documentation Files

#### `README.md` (420 lines)
Comprehensive user guide:
- Validator descriptions
- Python API reference
- CLI documentation
- Usage examples
- Error handling
- CI/CD integration

**Sections**:
1. Overview
2. Validators (1-6)
3. Running the Full Suite
4. Report Structure
5. Integration with CI/CD
6. Error Handling
7. Development

#### `MANIFEST.md` (280 lines)
System manifest:
- Security classification
- Component inventory
- Dependencies
- Usage patterns
- Error categories
- Maintenance guidelines
- Version history

**Sections**:
1. Purpose
2. Classification
3. Components
4. Validators Inventory
5. Expected Files Structure
6. Configuration Dependencies
7. Usage Patterns
8. Error Categories
9. Security Considerations
10. Maintenance Guidelines

#### `QUICK_REFERENCE.md` (250 lines)
Quick reference card:
- One-line commands
- Copy-paste code
- Common issues & fixes
- Validator return structure
- File paths
- Expected values
- CI/CD examples

**Sections**:
1. One-Line Commands
2. Python API (Copy-Paste Ready)
3. Validation Checklist
4. Common Issues & Fixes
5. Validator Return Structure
6. Report Structure
7. File Paths (Defaults)
8. Expected Values
9. Layer Requirements by Role
10. CI/CD Integration

#### `IMPLEMENTATION_SUMMARY.md` (350 lines)
Technical implementation details:
- Deliverables
- Technical details
- Data structures
- Usage patterns
- Testing coverage
- Dependencies
- Performance
- Security

**Sections**:
1. Overview
2. Deliverables
3. Technical Details
4. Data Structures
5. Usage Patterns
6. Testing Coverage
7. File Inventory
8. Dependencies
9. Performance Characteristics
10. Security Classification
11. Success Criteria

#### `INDEX.md` (this file)
Navigation index:
- Quick navigation
- Validators reference
- Common tasks
- File descriptions
- Learning path

### Test Files

#### `tests/test_validation_suite.py` (420 lines)
Comprehensive test suite:
- 21 test cases
- 7 test classes
- Integration tests
- Marked with `@pytest.mark.updated`

**Test Classes**:
1. `TestLayerCompleteness` (4 tests)
2. `TestFusionWeights` (3 tests)
3. `TestAntiUniversality` (3 tests)
4. `TestIntrinsicCalibration` (3 tests)
5. `TestConfigFiles` (2 tests)
6. `TestBoundedness` (4 tests)
7. `TestRunAllValidations` (1 test)
8. `TestValidationSuiteIntegration` (1 test, marked)

## Learning Path

### 1. Beginner (New to Validation Suite)
1. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. Run examples: `python -m sensitive_rules_for_coding.validation_suite.examples`
3. Try one-line commands from quick reference
4. Review validator descriptions in [README.md](README.md#validators)

### 2. Intermediate (Using in Projects)
1. Read full [README.md](README.md)
2. Study [examples.py](examples.py) patterns
3. Learn to interpret validation results
4. Understand error categories in [MANIFEST.md](MANIFEST.md#error-categories)
5. Practice with individual validators

### 3. Advanced (Integration & CI/CD)
1. Study [runner.py](runner.py) implementation
2. Review [MANIFEST.md](MANIFEST.md) for system architecture
3. Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details
4. Integrate into CI/CD pipeline
5. Customize for specific use cases

### 4. Expert (Contributing & Maintenance)
1. Deep dive into [validators.py](validators.py) implementation
2. Review [tests/test_validation_suite.py](../../tests/test_validation_suite.py)
3. Understand [LAYER_REQUIREMENTS](validators.py#L15)
4. Follow [maintenance guidelines](MANIFEST.md#maintenance-guidelines)
5. Contribute new validators or enhancements

## Troubleshooting

### Where do I start?
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for immediate usage  
→ [README.md](README.md) for comprehensive guide

### How do I run validations?
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md#one-line-commands)

### Validation failed, now what?
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md#common-issues--fixes)  
→ [README.md](README.md#validators) for specific validator details

### How do I integrate with CI/CD?
→ [README.md](README.md#integration-with-cicd)  
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md#cicd-integration)

### Where are test cases?
→ [tests/test_validation_suite.py](../../tests/test_validation_suite.py)

### How do I add a new validator?
→ [MANIFEST.md](MANIFEST.md#maintenance-guidelines)  
→ Study existing validators in [validators.py](validators.py)

### What's the security classification?
→ [MANIFEST.md](MANIFEST.md#classification)  
→ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md#security-classification)

### Performance concerns?
→ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md#performance-characteristics)

## External References

### Related F.A.R.F.A.N Components
- `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/` - Configuration files
- `src/orchestration/method_signature_validator.py` - Related validator
- `sensitive_rules_for_coding/canonical_notation/notation_metods` - Layer notation spec

### Configuration Files
- `COHORT_2024_canonical_method_inventory.json` - Method inventory
- `COHORT_2024_fusion_weights.json` - Fusion weights
- `COHORT_2024_intrinsic_calibration.json` - Intrinsic calibration
- `COHORT_2024_layer_assignment.py` - Layer assignments

## Version Information

- **Current Version**: 1.0.0
- **Release Date**: 2025-01-30
- **Python Version**: 3.12+
- **Status**: Production Ready

## Contact & Support

For questions, issues, or contributions:
- Follow F.A.R.F.A.N contribution guidelines
- Maintain SENSITIVE classification
- See main repository documentation

## Legend

📖 Documentation  
💻 Implementation  
🧪 Testing  
🚀 Getting Started  
⚡ Quick Reference  
🔒 Security
