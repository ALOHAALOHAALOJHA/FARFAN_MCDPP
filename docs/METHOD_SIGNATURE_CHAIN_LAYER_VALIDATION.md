# Method Signature Chain Layer Validation

## Overview

The Method Signature Chain Layer Validation system provides comprehensive signature governance for the F.A.R.F.A.N mechanistic policy analysis pipeline. It ensures that all methods in the analysis chain have properly defined signatures with appropriate input/output contracts.

## Architecture

### Input Classification

Method inputs are classified into three categories:

1. **Required Inputs** (`required_inputs`)
   - **MUST** be present at runtime
   - **Hard failure** if missing
   - System raises exception and halts execution
   - Example: `extracted_text`, `question_id`

2. **Optional Inputs** (`optional_inputs`)
   - Nice to have but not mandatory
   - **No penalty** if missing
   - Method should have sensible defaults
   - Example: `context`, `language`, `threshold`

3. **Critical Optional Inputs** (`critical_optional`)
   - Should be present for optimal results
   - **Penalty applied** if missing (default: 0.1 per input)
   - Does not cause hard failure
   - Must be subset of `optional_inputs`
   - Example: `reference_corpus`, `ontology`

### Signature Schema

Each method signature must contain:

```json
{
  "method_id": {
    "signature": {
      "required_inputs": ["input1", "input2"],
      "optional_inputs": ["opt1", "opt2"],
      "critical_optional": ["opt1"],
      "output_type": "float|dict|list|str|int|bool",
      "output_range": [min, max] | null,
      "description": "Method description"
    }
  }
}
```

### Required Fields

- `required_inputs`: List of mandatory input parameters
- `output_type`: Expected output type

### Recommended Fields

- `optional_inputs`: List of optional input parameters
- `critical_optional`: Subset of optional inputs that should ideally be provided
- `output_range`: For numeric outputs, valid range as `[min, max]`
- `description`: Human-readable description of method purpose

## Files

### Core Implementation

- **`config/json_files_ no_schemas/method_signatures.json`**
  - Central registry of all method signatures
  - Version controlled schema
  - Currently at version 2.0.0 with chain layer validation

- **`src/farfan_pipeline/core/orchestrator/method_signature_validator.py`**
  - Core validation logic
  - Signature completeness checking
  - Validation report generation

- **`src/farfan_pipeline/core/orchestrator/signature_runtime_validator.py`**
  - Runtime validation during execution
  - Input/output validation
  - Penalty calculation for missing critical optional inputs

### Scripts

- **`scripts/validate_method_signatures.py`**
  - CLI tool for signature validation
  - Generates comprehensive validation reports
  - Exit codes: 0 = success, 1 = validation failures

### Output

- **`signature_validation_report.json`**
  - Generated validation report
  - Contains detailed validation results
  - Statistics and summary information

## Usage

### Validating Signatures

```bash
# Validate all signatures and generate report
python scripts/validate_method_signatures.py

# Validate specific signatures file
python scripts/validate_method_signatures.py path/to/signatures.json output_report.json
```

### Adding New Method Signatures

1. Edit `config/json_files_ no_schemas/method_signatures.json`
2. Add method entry with complete signature:

```json
"my_new_method": {
  "signature": {
    "required_inputs": ["extracted_text", "question_id"],
    "optional_inputs": ["reference_corpus", "threshold"],
    "critical_optional": ["reference_corpus"],
    "output_type": "float",
    "output_range": [0.0, 1.0],
    "description": "My new analysis method"
  }
}
```

3. Validate signatures:

```bash
python scripts/validate_method_signatures.py
```

### Runtime Validation

```python
from farfan_pipeline.core.orchestrator.signature_runtime_validator import (
    validate_method_call
)

# Validate method call
passed, penalty, messages = validate_method_call(
    method_id="coherence_validator",
    provided_inputs={
        "extracted_text": "policy text",
        "question_id": "D1-Q1"
        # Missing "reference_corpus" (critical optional) -> penalty of 0.1
    },
    raise_on_failure=True  # Raise exception on hard failures
)

print(f"Validation passed: {passed}")
print(f"Penalty: {penalty}")
print(f"Messages: {messages}")
```

### Penalty Calculation

```python
from farfan_pipeline.core.orchestrator.signature_runtime_validator import (
    SignatureRuntimeValidator
)

validator = SignatureRuntimeValidator(
    penalty_for_missing_critical=0.15  # Custom penalty
)

result = validator.validate_inputs("method_id", inputs_dict)
penalty = validator.calculate_penalty(result)

# Penalty calculation:
# - Hard failures: 1.0 (maximum)
# - Missing critical optional: 0.15 per input (configurable)
# - Soft failures: 0.05 per failure
# - Total penalty capped at 1.0
```

## Validation Report Structure

```json
{
  "validation_timestamp": "2025-01-11T12:00:00Z",
  "signatures_version": "2.0.0",
  "total_methods": 18,
  "valid_methods": 16,
  "invalid_methods": 2,
  "incomplete_methods": 3,
  "methods_with_warnings": 5,
  "validation_details": {
    "method_id": {
      "is_valid": true,
      "missing_fields": [],
      "issues": [],
      "warnings": ["Missing recommended field: output_range"]
    }
  },
  "summary": {
    "completeness_rate": 88.89,
    "methods_with_required_fields": 16,
    "most_common_required_inputs": [
      ["extracted_text", 12],
      ["question_id", 10]
    ],
    "output_type_distribution": {
      "float": 8,
      "dict": 7,
      "list": 3
    }
  }
}
```

## Integration Points

### Orchestrator Integration

The signature validator integrates with the orchestrator to validate method calls:

```python
from farfan_pipeline.core.orchestrator.signature_runtime_validator import (
    get_runtime_validator
)

# In orchestrator or executor
validator = get_runtime_validator()

# Before method execution
passed, penalty, messages = validator.validate_method_call(
    method_id="evidence_assembler",
    provided_inputs=inputs,
    raise_on_failure=True
)

# Execute method
result = method(**inputs)

# After method execution
output_validation = validator.validate_output(method_id, result)
```

### Calibration System Integration

Signatures can be used by the calibration system to ensure consistent method contracts:

```python
from farfan_pipeline.core.orchestrator.method_signature_validator import (
    MethodSignatureValidator
)

validator = MethodSignatureValidator("config/json_files_ no_schemas/method_signatures.json")
validator.load_signatures()

# Check if method has complete signature
is_complete = validator.check_signature_completeness("my_method")

# Get method signature
signature = validator.get_method_signature("my_method")
```

## Best Practices

### Defining Signatures

1. **Be Explicit**: Always declare all inputs, even if optional
2. **Classify Correctly**: 
   - Use `required_inputs` for truly mandatory parameters
   - Use `critical_optional` for parameters that significantly impact quality
   - Use `optional_inputs` for convenience parameters
3. **Document Ranges**: Always specify `output_range` for numeric outputs
4. **Keep Updated**: Update signatures when method contracts change

### Runtime Usage

1. **Fail Fast**: Use `raise_on_failure=True` for critical validation
2. **Log Penalties**: Track penalties for missing critical optional inputs
3. **Monitor Stats**: Use `get_validation_stats()` to track validation patterns
4. **Non-Strict Mode**: Use in development for gradual signature adoption

## Testing

Run tests for signature validation:

```bash
# Test static validation
pytest tests/core/test_method_signature_validator.py -v

# Test runtime validation
pytest tests/core/test_signature_runtime_validator.py -v

# Run all signature tests
pytest tests/core/test_*signature*.py -v
```

## Validation Rules

### Input Validation Rules

1. `required_inputs` must be a list
2. All required inputs must be provided at runtime
3. Required inputs cannot be `None`
4. `optional_inputs` must be a list
5. `critical_optional` must be subset of `optional_inputs`
6. All input names must be strings

### Output Validation Rules

1. `output_type` must be a string
2. `output_type` should be one of: `float`, `int`, `dict`, `list`, `str`, `bool`, `tuple`, `Any`
3. `output_range` must be `null` or `[min, max]` array
4. If `output_range` specified, `min < max`
5. Numeric outputs validated against range

### Signature Completeness Rules

1. **Required Fields**: `required_inputs`, `output_type`
2. **Recommended Fields**: `optional_inputs`, `critical_optional`, `output_range`
3. **Optional Fields**: `description`
4. Unknown fields generate warnings

## Error Handling

### Hard Failures (Exception Raised)

- Missing required input at runtime
- Required input is `None`
- Invalid signature structure (when `raise_on_failure=True`)

### Soft Failures (Penalty Applied)

- Missing critical optional input (penalty: configurable, default 0.1)
- Output type mismatch (penalty: 0.05)
- Output out of range (penalty: 0.05)

### Warnings (Logged Only)

- Missing optional inputs
- Missing recommended fields in signature
- Unknown output type
- Signature not found (in non-strict mode)

## Version History

- **v2.0.0**: Chain layer validation with input classification
- **v1.0.0**: Basic signature registry

## Future Enhancements

1. Automatic signature inference from AST
2. Signature drift detection across versions
3. Integration with OpenTelemetry tracing
4. Signature-based dependency analysis
5. Automated test generation from signatures
6. Contract-first development tooling
