# Chain Layer Evaluator - Examples

Comprehensive examples for the ChainLayerEvaluator (@chain) with discrete scoring.

## Overview

The Chain Layer Evaluator validates method wiring and orchestration in analysis chains using discrete scoring:

- **1.0**: All inputs present, no warnings (perfect)
- **0.8**: All contracts pass but warnings exist (soft violations)
- **0.6**: Many optional missing (>50%) OR soft schema violation
- **0.3**: Critical optional missing
- **0.0**: Missing required inputs OR hard schema incompatibility

## Examples

### 1. Basic Usage (`basic_usage.py`)

Fundamental operations and discrete score demonstrations:
- Single method evaluation
- Type checking with upstream outputs
- All discrete score levels (0.0, 0.3, 0.6, 0.8, 1.0)

**Run:**
```bash
python basic_usage.py
```

**Key Concepts:**
- Required vs optional vs critical optional inputs
- Hard vs soft type mismatches
- Score interpretation

### 2. Sequence Validation (`sequence_validation.py`)

Chain validation and weakest link analysis:
- Simple 3-method chains
- Broken chains (missing dependencies)
- Complex multi-stage pipelines
- Weakest link identification and fixing

**Run:**
```bash
python sequence_validation.py
```

**Key Concepts:**
- Chain quality = min(method_scores)
- Weakest link principle
- Input propagation through chains
- Dependency validation

### 3. Advanced Scenarios (`advanced_scenarios.py`)

Real-world patterns and optimizations:
- F.A.R.F.A.N policy analysis pipeline (7 phases)
- Parallel dimension chains (D1-D6)
- Conditional chain branches
- Error handling strategies
- Large chain optimization (20+ methods)

**Run:**
```bash
python advanced_scenarios.py
```

**Key Concepts:**
- Multi-phase analysis chains
- Parallel execution validation
- Conditional branching
- Error recovery
- Performance patterns

## Quick Start

```python
from COHORT_2024_chain_layer import ChainLayerEvaluator

# Define method signatures
signatures = {
    "analyze_document": {
        "required_inputs": ["document", "config"],
        "optional_inputs": ["metadata", "cache"],
        "critical_optional": ["metadata"],
        "input_types": {"document": "str", "config": "dict"},
        "output_type": "dict",
    }
}

# Create evaluator
evaluator = ChainLayerEvaluator(signatures)

# Evaluate single method
result = evaluator.evaluate(
    "analyze_document",
    provided_inputs={"document", "config", "metadata"}
)

print(f"Score: {result['score']}")
print(f"Reason: {result['reason']}")

# Validate chain sequence
chain_result = evaluator.validate_chain_sequence(
    method_sequence=["method_a", "method_b", "method_c"],
    initial_inputs={"input1", "input2"},
    method_outputs={
        "method_a": {"output_a"},
        "method_b": {"output_b"},
        "method_c": {"output_c"},
    }
)

print(f"Chain Quality: {chain_result['chain_quality']}")
print(f"Weakest Link: {chain_result['weakest_link']}")
```

## Discrete Scoring Logic

### Score 1.0 (Perfect)
- All required inputs present
- All critical optional inputs present
- No type mismatches
- No warnings

### Score 0.8 (Good with Warnings)
- All contracts satisfied
- Soft type warnings (e.g., int→float)
- All critical inputs present

### Score 0.6 (Degraded)
- Many optional inputs missing (ratio > 0.5)
- OR soft schema violations
- All required inputs present

### Score 0.3 (Critical Missing)
- Critical optional inputs missing
- All required inputs present
- No hard violations

### Score 0.0 (Failed)
- Missing required inputs
- OR hard schema incompatibility
- OR method signature not found

## Integration Patterns

### With MethodSignatureValidator

```python
from COHORT_2024_chain_layer import create_evaluator_from_validator

# Create from validator instance or path
evaluator = create_evaluator_from_validator(
    "path/to/method_signatures.json"
)
```

### With Real Pipeline

```python
# Load method signatures
signatures = load_method_signatures_from_registry()

# Create evaluator
evaluator = ChainLayerEvaluator(signatures)

# Validate before execution
result = evaluator.validate_chain_sequence(
    method_sequence=pipeline_methods,
    initial_inputs=available_data,
    method_outputs=method_output_mapping
)

if result['chain_quality'] >= 0.8:
    execute_pipeline()
else:
    handle_weakest_link(result['weakest_link'])
```

## Testing

Run the test suite:
```bash
pytest chain_layer_tests.py -v
```

Test coverage:
- Discrete scoring (all levels)
- Schema compatibility checking
- Chain sequence validation
- Weakest link computation
- Edge cases
- Integration scenarios

## Best Practices

1. **Always validate chains before execution**
   - Use `validate_chain_sequence()` to catch missing dependencies early

2. **Monitor weakest links**
   - Chain quality is determined by the weakest link
   - Focus optimization on low-scoring methods

3. **Provide critical optional inputs**
   - Score drops to 0.3 if critical optional inputs missing
   - Identify critical inputs in method signatures

4. **Handle type mismatches**
   - Soft mismatches (int/float) → warning (0.8)
   - Hard mismatches (list/str) → failure (0.0)

5. **Use method_outputs mapping**
   - Track what each method produces
   - Enables proper input propagation validation

## Architecture Notes

- **Immutable scoring**: Scores are discrete (0.0, 0.3, 0.6, 0.8, 1.0)
- **Weakest link principle**: Chain quality = min(method_scores)
- **Type-safe**: Full type checking with TypedDict results
- **Traceable**: Detailed reason for each score
- **Composable**: Integrates with existing validation infrastructure

## See Also

- `COHORT_2024_chain_layer.py` - Main implementation
- `chain_layer_tests.py` - Full test suite
- `method_signature_validator.py` - Signature validation
- `COHORT_2024_layer_assignment.py` - Layer system overview

---

**COHORT_2024** - Chain Layer (@chain) Evaluator  
Part of the F.A.R.F.A.N Calibration & Parametrization System
