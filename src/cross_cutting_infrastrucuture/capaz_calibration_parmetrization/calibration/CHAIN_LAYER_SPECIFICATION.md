# Chain Layer (@chain) Evaluator - Technical Specification

**COHORT_2024** - Chain Layer Implementation  
**Version**: 1.0.0  
**Created**: 2024-12-15

## Overview

The Chain Layer Evaluator implements discrete scoring logic for method chain validation, ensuring proper method wiring and orchestration in the F.A.R.F.A.N policy analysis pipeline.

## Discrete Scoring Logic

The evaluator assigns one of five discrete scores based on contract compliance:

### Score 1.0 (Perfect)
- **Condition**: All inputs present AND no warnings
- **Requirements**:
  - All required inputs available
  - All critical optional inputs available
  - No type mismatches
  - No warnings
- **Use Case**: Ideal chain configuration

### Score 0.8 (Good with Warnings)
- **Condition**: All contracts pass AND warnings exist
- **Requirements**:
  - All required inputs available
  - All critical optional inputs available
  - Soft type warnings present (e.g., int→float)
- **Use Case**: Functional but not optimal

### Score 0.6 (Degraded)
- **Condition**: missing_optional AND many_missing (ratio>0.5) OR soft_schema_violation
- **Requirements**:
  - All required inputs available
  - All critical optional inputs available
  - Many optional inputs missing (>50%)
  - OR soft schema violations
- **Use Case**: Reduced functionality

### Score 0.3 (Critical Missing)
- **Condition**: missing_critical (critical optional missing)
- **Requirements**:
  - All required inputs available
  - One or more critical optional inputs missing
  - No hard violations
- **Use Case**: Significant functionality loss

### Score 0.0 (Failed)
- **Condition**: missing_required (hard mismatch)
- **Types**:
  - Schema incompatible (hard type mismatch)
  - Required input unavailable
  - Method signature not found
- **Use Case**: Cannot execute

## Input Classification

### Required Inputs
- **Definition**: MUST be present for method execution
- **Failure**: Hard failure (score 0.0) if missing
- **Example**: `document`, `config`

### Optional Inputs
- **Definition**: Nice to have, no penalty if missing
- **Failure**: No immediate penalty, affects score only if many missing (>50%)
- **Example**: `cache`, `debug_mode`

### Critical Optional Inputs
- **Definition**: Important but not strictly required
- **Failure**: Soft failure (score 0.3) if missing
- **Example**: `metadata`, `model`, `weights`
- **Note**: Must be subset of optional_inputs

## Schema Compatibility

### Hard Incompatibility (Score 0.0)
Incompatible types that cannot be coerced:
- `list` ↔ `str`
- `dict` ↔ `str`
- `list` ↔ `dict`
- etc.

### Soft Incompatibility (Score 0.6-0.8)
Compatible types with warnings:
- `int` ↔ `float`
- `list` ↔ `tuple`

### Full Compatibility (No penalty)
- Exact type match
- `Any` type (accepts anything)
- `None` (type not specified)

## Chain Sequence Validation

### Weakest Link Principle
Chain quality is determined by the weakest link:
```
chain_quality = min(method_scores)
```

### Input Propagation
Outputs from upstream methods become available to downstream methods:
```python
validate_chain_sequence(
    method_sequence=["method_a", "method_b", "method_c"],
    initial_inputs={"input1", "input2"},
    method_outputs={
        "method_a": {"output_a"},
        "method_b": {"output_b"},
        "method_c": {"output_c"},
    }
)
```

After `method_a` executes, `output_a` becomes available to `method_b` and `method_c`.

## API Reference

### ChainLayerEvaluator

```python
class ChainLayerEvaluator:
    def __init__(
        self, 
        method_signatures: dict[str, dict[str, Any]] | None = None
    ) -> None
```

**Parameters**:
- `method_signatures`: Dict mapping method_id to signature metadata

**Signature Format**:
```python
{
    "method_id": {
        "required_inputs": ["input1", "input2"],
        "optional_inputs": ["opt1", "opt2"],
        "critical_optional": ["opt1"],
        "input_types": {"input1": "str", "input2": "dict"},
        "output_type": "dict"
    }
}
```

### evaluate()

```python
def evaluate(
    self,
    method_id: str,
    provided_inputs: set[str],
    upstream_outputs: dict[str, str] | None = None,
) -> ChainEvaluationResult
```

**Parameters**:
- `method_id`: Method identifier
- `provided_inputs`: Set of available input names
- `upstream_outputs`: Optional dict mapping input_name → output_type

**Returns**: `ChainEvaluationResult` with:
- `score`: float (0.0, 0.3, 0.6, 0.8, or 1.0)
- `reason`: str explaining the score
- `missing_required`: list[str]
- `missing_critical`: list[str]
- `missing_optional`: list[str]
- `warnings`: list[str]
- `schema_violations`: list[str]

### validate_chain_sequence()

```python
def validate_chain_sequence(
    self,
    method_sequence: list[str],
    initial_inputs: set[str],
    method_outputs: dict[str, set[str]] | None = None,
) -> ChainSequenceResult
```

**Parameters**:
- `method_sequence`: Ordered list of method_ids
- `initial_inputs`: Initial set of available inputs
- `method_outputs`: Optional dict mapping method_id → output names

**Returns**: `ChainSequenceResult` with:
- `method_scores`: dict[str, float]
- `individual_results`: dict[str, ChainEvaluationResult]
- `chain_quality`: float (minimum score)
- `weakest_link`: str | None

### compute_chain_quality()

```python
def compute_chain_quality(
    self, 
    method_scores: dict[str, float]
) -> float
```

**Parameters**:
- `method_scores`: Dict mapping method_id → score

**Returns**: float (minimum score - weakest link)

## Usage Patterns

### Pattern 1: Pre-Execution Validation

```python
# Before executing pipeline
result = evaluator.validate_chain_sequence(
    method_sequence=pipeline_methods,
    initial_inputs=available_data,
    method_outputs=output_mapping
)

if result['chain_quality'] >= 0.8:
    execute_pipeline()
else:
    fix_weakest_link(result['weakest_link'])
```

### Pattern 2: Weakest Link Optimization

```python
# Identify and fix weakest link
result = evaluator.validate_chain_sequence(...)

while result['chain_quality'] < 0.8:
    weakest = result['weakest_link']
    weakest_result = result['individual_results'][weakest]
    
    # Provide missing critical inputs
    for input_name in weakest_result['missing_critical']:
        available_data.add(input_name)
    
    # Re-evaluate
    result = evaluator.validate_chain_sequence(...)
```

### Pattern 3: Conditional Branch Validation

```python
# Validate different branches
branch_a_result = evaluator.validate_chain_sequence(
    method_sequence=branch_a_methods, ...
)
branch_b_result = evaluator.validate_chain_sequence(
    method_sequence=branch_b_methods, ...
)

# Choose best branch
if branch_a_result['chain_quality'] > branch_b_result['chain_quality']:
    execute_branch_a()
else:
    execute_branch_b()
```

## Integration

### With MethodSignatureValidator

```python
from COHORT_2024_chain_layer import create_evaluator_from_validator

evaluator = create_evaluator_from_validator(
    "path/to/method_signatures.json"
)
```

### With Method Registry

```python
from method_registry import MethodRegistry

registry = MethodRegistry()
signatures = load_signatures_from_registry(registry)
evaluator = ChainLayerEvaluator(signatures)
```

## Testing

Comprehensive test coverage in `chain_layer_tests.py`:

### Test Categories
1. **Discrete Scoring**: All score levels (0.0, 0.3, 0.6, 0.8, 1.0)
2. **Schema Compatibility**: Hard/soft type checking
3. **Chain Sequence**: Multi-method validation
4. **Weakest Link**: Identification and computation
5. **Edge Cases**: Empty inputs, unknown methods
6. **Integration**: Realistic pipeline scenarios

### Run Tests
```bash
pytest chain_layer_tests.py -v
```

## Examples

Complete examples in `chain_examples/`:

1. **basic_usage.py**: Fundamental operations
2. **sequence_validation.py**: Chain validation
3. **advanced_scenarios.py**: Real-world patterns
4. **integration_example.py**: Infrastructure integration

### Run Examples
```bash
python chain_examples/basic_usage.py
python chain_examples/sequence_validation.py
python chain_examples/advanced_scenarios.py
python chain_examples/integration_example.py
```

## Performance Characteristics

### Time Complexity
- **Single evaluation**: O(n) where n = total inputs
- **Chain sequence**: O(m × n) where m = methods, n = inputs
- **Type checking**: O(t) where t = typed inputs

### Space Complexity
- **Evaluator**: O(s) where s = signature count
- **Results**: O(m) where m = method count

### Optimization Tips
1. Cache evaluator instances (signature loading)
2. Reuse provided_inputs sets
3. Batch validate parallel chains
4. Skip type checking if not needed

## Architecture Decisions

### Immutable Scoring
Scores are discrete, not continuous, for:
- Clear thresholds for decision-making
- Consistent interpretation across teams
- Traceable audit trails

### Weakest Link Principle
Chain quality = min(scores) because:
- Conservative safety principle
- Focus on bottlenecks
- Incentivizes fixing weak links

### TypedDict Results
All results use TypedDict for:
- Type safety
- IDE autocomplete
- Contract enforcement

## Error Handling

### Missing Signatures
```python
result = evaluator.evaluate("unknown_method", ...)
# Returns: score=0.0, reason="missing_required: no signature found"
```

### Invalid Inputs
```python
result = evaluator.evaluate("method", set())
# Returns: score=0.0 if required inputs missing
```

### Type Errors
```python
result = evaluator.evaluate(
    "method",
    provided_inputs,
    upstream_outputs={"input": "incompatible_type"}
)
# Returns: score=0.0 with schema_violations
```

## Future Extensions

### Planned Features
1. Probabilistic scoring (confidence intervals)
2. Cost-based optimization (input acquisition costs)
3. Parallel chain validation
4. Graph-based dependency resolution
5. Auto-fix suggestions

### Backwards Compatibility
All future extensions maintain:
- Discrete scoring levels
- TypedDict result format
- Weakest link principle

## References

### Related Components
- `method_signature_validator.py`: Signature validation
- `COHORT_2024_layer_assignment.py`: Layer system
- `method_registry.py`: Method management
- `COHORT_2024_layer_computers.py`: Score computation

### Documentation
- `README.md`: Package overview
- `QUICK_REFERENCE.md`: API cheat sheet
- `chain_examples/README.md`: Example guide

## Version History

### 1.0.0 (2024-12-15)
- Initial implementation
- Discrete scoring (0.0, 0.3, 0.6, 0.8, 1.0)
- Chain sequence validation
- Weakest link computation
- Schema compatibility checking
- Comprehensive test suite
- Example library

---

**COHORT_2024** - Part of F.A.R.F.A.N Calibration & Parametrization System
