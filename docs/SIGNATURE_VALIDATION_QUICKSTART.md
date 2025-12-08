# Method Signature Validation Quickstart

## 5-Minute Setup

### 1. Validate Existing Signatures

```bash
python scripts/validate_method_signatures.py
```

This will generate `signature_validation_report.json` with validation results.

### 2. Check Your Report

```bash
cat signature_validation_report.json | jq '.summary'
```

Look for:
- `completeness_rate`: Should be > 90%
- `invalid_methods`: Should be 0
- `methods_with_warnings`: Review these

### 3. Add a New Method Signature

Edit `config/json_files_ no_schemas/method_signatures.json`:

```json
{
  "my_analyzer": {
    "signature": {
      "required_inputs": ["extracted_text", "question_id"],
      "optional_inputs": ["reference_corpus", "threshold"],
      "critical_optional": ["reference_corpus"],
      "output_type": "float",
      "output_range": [0.0, 1.0],
      "description": "Analyzes policy text coherence"
    }
  }
}
```

### 4. Use Runtime Validation

```python
from farfan_pipeline.core.orchestrator.signature_runtime_validator import (
    validate_method_call
)

# Validate method inputs
passed, penalty, messages = validate_method_call(
    method_id="my_analyzer",
    provided_inputs={
        "extracted_text": "policy text",
        "question_id": "D1-Q1"
        # Missing reference_corpus -> penalty of 0.1
    },
    raise_on_failure=True
)

if not passed:
    print(f"Validation failed: {messages}")
else:
    print(f"Penalty for missing inputs: {penalty}")
```

## Input Classification Quick Reference

| Type | Behavior | Penalty | Example |
|------|----------|---------|---------|
| **required_inputs** | MUST be present | Hard failure (1.0) | `extracted_text`, `question_id` |
| **critical_optional** | Should be present | Soft failure (0.1 per input) | `reference_corpus`, `ontology` |
| **optional_inputs** | Nice to have | No penalty (0.0) | `threshold`, `context` |

## Validation Report Keys

```json
{
  "total_methods": 18,           // Total methods in registry
  "valid_methods": 16,            // Methods with complete signatures
  "invalid_methods": 2,           // Methods missing required fields
  "incomplete_methods": 3,        // Methods missing recommended fields
  "methods_with_warnings": 5,     // Methods with non-critical issues
  "summary": {
    "completeness_rate": 88.89   // Percentage of valid methods
  }
}
```

## Common Issues

### Issue: Method has no signature

**Fix:** Add signature to `method_signatures.json`:

```json
"method_id": {
  "signature": {
    "required_inputs": ["input1"],
    "output_type": "dict"
  }
}
```

### Issue: Missing required field

**Fix:** Add missing `required_inputs` or `output_type`:

```json
{
  "required_inputs": ["text"],      // Required
  "output_type": "float"             // Required
}
```

### Issue: Critical optional not in optional_inputs

**Fix:** Ensure critical_optional is subset of optional_inputs:

```json
{
  "optional_inputs": ["corpus", "threshold"],
  "critical_optional": ["corpus"]    // Must be in optional_inputs
}
```

### Issue: Invalid output_range

**Fix:** Use `[min, max]` format or `null`:

```json
{
  "output_range": [0.0, 1.0]  // Good
}
```

## Integration Examples

### Example 1: Basic Validation

```python
validator = SignatureRuntimeValidator()

result = validator.validate_inputs(
    "evidence_assembler",
    {"extracted_text": "text", "question_id": "Q1"}
)

print(f"Passed: {result['passed']}")
print(f"Issues: {result['hard_failures']}")
```

### Example 2: With Penalty Calculation

```python
validator = SignatureRuntimeValidator(penalty_for_missing_critical=0.15)

result = validator.validate_inputs("my_method", inputs)
penalty = validator.calculate_penalty(result)

# Adjust score based on penalty
final_score = original_score * (1 - penalty)
```

### Example 3: Output Validation

```python
validator = SignatureRuntimeValidator()

# Validate method result
output_result = validator.validate_output("my_method", 0.85)

if output_result['soft_failures']:
    print(f"Output issues: {output_result['soft_failures']}")
```

## Testing

```bash
# Test signature validator
pytest tests/core/test_method_signature_validator.py -v

# Test runtime validator
pytest tests/core/test_signature_runtime_validator.py -v
```

## Next Steps

1. Read full documentation: `docs/METHOD_SIGNATURE_CHAIN_LAYER_VALIDATION.md`
2. Review example integration: `src/farfan_pipeline/core/orchestrator/signature_integration_example.py`
3. Run example: `python src/farfan_pipeline/core/orchestrator/signature_integration_example.py`
