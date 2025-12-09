# Chain Layer (@chain) - Quick Reference

**One-page reference for ChainLayerEvaluator**

## Import

```python
from COHORT_2024_chain_layer import (
    ChainLayerEvaluator,
    ChainEvaluationResult,
    ChainSequenceResult,
    create_evaluator_from_validator,
)
```

## Discrete Scores

| Score | Condition | Meaning |
|-------|-----------|---------|
| 1.0 | All inputs present, no warnings | Perfect |
| 0.8 | All contracts pass, warnings exist | Good |
| 0.6 | Many optional missing (>50%) OR soft violation | Degraded |
| 0.3 | Critical optional missing | Critical |
| 0.0 | Missing required OR hard schema incompatible | Failed |

## Quick Start

```python
# Create evaluator
signatures = {
    "method_id": {
        "required_inputs": ["req1", "req2"],
        "optional_inputs": ["opt1", "opt2"],
        "critical_optional": ["opt1"],
        "input_types": {"req1": "str", "req2": "dict"},
        "output_type": "dict",
    }
}
evaluator = ChainLayerEvaluator(signatures)

# Evaluate single method
result = evaluator.evaluate("method_id", {"req1", "req2", "opt1"})
print(result["score"])  # 1.0, 0.8, 0.6, 0.3, or 0.0

# Validate chain
chain_result = evaluator.validate_chain_sequence(
    method_sequence=["method_a", "method_b", "method_c"],
    initial_inputs={"input1", "input2"},
    method_outputs={
        "method_a": {"output_a"},
        "method_b": {"output_b"},
    }
)
print(chain_result["chain_quality"])  # min(method_scores)
print(chain_result["weakest_link"])   # method with lowest score
```

## Input Types

| Type | Required? | Missing → |
|------|-----------|-----------|
| **required_inputs** | Yes | 0.0 |
| **critical_optional** | No, but important | 0.3 |
| **optional_inputs** | No | 0.6 (if >50% missing) |

## Schema Compatibility

| From → To | Result |
|-----------|--------|
| Exact match | ✓ No warning |
| int ↔ float | ⚠ Soft warning (0.8) |
| list ↔ tuple | ⚠ Soft warning (0.8) |
| list ↔ str | ✗ Hard violation (0.0) |
| Any ↔ anything | ✓ No warning |

## Common Patterns

### Pre-execution validation
```python
if evaluator.validate_chain_sequence(...)["chain_quality"] >= 0.8:
    execute_pipeline()
```

### Fix weakest link
```python
result = evaluator.validate_chain_sequence(...)
weakest = result["weakest_link"]
missing = result["individual_results"][weakest]["missing_critical"]
# Provide missing inputs, re-evaluate
```

### Load from file
```python
evaluator = create_evaluator_from_validator("signatures.json")
```

## ChainEvaluationResult

```python
{
    "score": 0.8,                    # Discrete score
    "reason": "...",                  # Explanation
    "missing_required": [],           # Required inputs missing
    "missing_critical": [],           # Critical optional missing
    "missing_optional": ["opt2"],     # Optional missing
    "warnings": ["Soft type..."],     # Warnings
    "schema_violations": []           # Hard violations
}
```

## ChainSequenceResult

```python
{
    "method_scores": {                # Individual scores
        "method_a": 1.0,
        "method_b": 0.8,
        "method_c": 1.0,
    },
    "individual_results": {...},      # Detailed results
    "chain_quality": 0.8,             # min(method_scores)
    "weakest_link": "method_b"        # Lowest scorer
}
```

## Examples

```bash
# Basic usage
python chain_examples/basic_usage.py

# Chain validation
python chain_examples/sequence_validation.py

# Advanced patterns
python chain_examples/advanced_scenarios.py

# Integration
python chain_examples/integration_example.py
```

## Tests

```bash
pytest chain_layer_tests.py -v
```

## Key Principles

1. **Discrete scoring**: Always 0.0, 0.3, 0.6, 0.8, or 1.0
2. **Weakest link**: chain_quality = min(method_scores)
3. **Type safety**: All results use TypedDict
4. **Traceable**: Every score has a reason

---

**See**: `CHAIN_LAYER_SPECIFICATION.md` for full documentation
