# Contextual Layer Evaluators (@q, @d, @p)

## Overview

The Contextual Layer Evaluators system implements the three contextual layers from the calibration theoretical model:
- **@q**: Question compatibility
- **@d**: Dimension compatibility  
- **@p**: Policy area compatibility

These layers capture how well a method works in different execution contexts (Q, D, P).

## Architecture

### Core Components

1. **CompatibilityMapping** (`data_structures.py`)
   - Dataclass defining method compatibility scores
   - Methods: `get_question_score()`, `get_dimension_score()`, `get_policy_score()`
   - Validation: `check_anti_universality(threshold=0.9)`

2. **CompatibilityRegistry** (`compatibility.py`)
   - Loads compatibility mappings from JSON configuration
   - Returns default mapping (all 0.1 penalties) for unknown methods
   - Validates Anti-Universality Theorem across all methods

3. **ContextualLayerEvaluator** (`compatibility.py`)
   - Evaluates @q, @d, @p layers for specific method-context combinations
   - Methods: `evaluate_question()`, `evaluate_dimension()`, `evaluate_policy()`
   - Convenience: `evaluate_all_contextual()` returns all three scores

## Configuration

### method_compatibility.json Structure

```json
{
  "method_compatibility": {
    "method_id": {
      "questions": {
        "Q001": 1.0,
        "Q031": 0.7,
        "Q091": 0.3
      },
      "dimensions": {
        "DIM01": 1.0,
        "DIM03": 0.7
      },
      "policies": {
        "PA01": 1.0,
        "PA10": 0.7
      }
    }
  }
}
```

### Compatibility Score Semantics

| Score | Meaning | Usage |
|-------|---------|-------|
| 1.0 | **Primary** | Designed specifically for this context |
| 0.7 | **Secondary** | Works well, not optimal |
| 0.3 | **Compatible** | Can work, limited effectiveness |
| 0.1 | **Undeclared** | Penalty - not validated for this context |

## Anti-Universality Theorem

**Theorem**: No method can have average compatibility ≥ 0.9 across ALL contexts (Q, D, P) simultaneously.

**Rationale**: Forces methods to declare their specialization. Universal methods violate the principle that every method should have specific strengths and weaknesses.

**Validation**:
```python
# Computes avg(questions), avg(dimensions), avg(policies)
# Fails if ALL THREE averages ≥ threshold
mapping.check_anti_universality(threshold=0.9)
```

## Usage Examples

### Basic Evaluation

```python
from pathlib import Path
from farfan_pipeline.core.calibration.compatibility import (
    CompatibilityRegistry,
    ContextualLayerEvaluator,
)

# Load registry
config_path = Path("config/json_files_ no_schemas/method_compatibility.json")
registry = CompatibilityRegistry(config_path)

# Create evaluator
evaluator = ContextualLayerEvaluator(registry)

# Evaluate individual layers
q_score = evaluator.evaluate_question("pattern_extractor_v2", "Q001")
d_score = evaluator.evaluate_dimension("pattern_extractor_v2", "DIM01")
p_score = evaluator.evaluate_policy("pattern_extractor_v2", "PA01")

print(f"@q: {q_score}, @d: {d_score}, @p: {p_score}")
```

### Batch Evaluation

```python
# Evaluate all contextual layers at once
scores = evaluator.evaluate_all_contextual(
    method_id="pattern_extractor_v2",
    question_id="Q031",
    dimension="DIM02",
    policy_area="PA10"
)

print(f"Question: {scores['q']}")
print(f"Dimension: {scores['d']}")
print(f"Policy: {scores['p']}")
```

### Anti-Universality Validation

```python
# Validate all methods in registry
try:
    results = registry.validate_anti_universality(threshold=0.9)
    print("✓ All methods comply with Anti-Universality Theorem")
except ValueError as e:
    print(f"✗ Violation detected: {e}")
```

### Handling Unknown Methods

```python
# Unknown methods get default mapping (all 0.1 penalties)
mapping = registry.get("unknown_method")
score = mapping.get_question_score("Q001")  # Returns 0.1
```

## Integration with Calibration Pipeline

The contextual layer evaluators integrate with the full calibration pipeline:

```python
from farfan_pipeline.core.calibration import (
    CompatibilityRegistry,
    ContextualLayerEvaluator,
)

# In calibration orchestrator
registry = CompatibilityRegistry(config_path)
evaluator = ContextualLayerEvaluator(registry)

# During method calibration
ctx = Context(question_id="Q001", dimension_id="DIM01", policy_id="PA01", unit_quality=0.85)
method_id = "pattern_extractor_v2"

contextual_scores = evaluator.evaluate_all_contextual(
    method_id=method_id,
    question_id=ctx.question_id,
    dimension=ctx.dimension_id,
    policy_area=ctx.policy_id
)

x_q = contextual_scores['q']  # @q layer score
x_d = contextual_scores['d']  # @d layer score
x_p = contextual_scores['p']  # @p layer score
```

## Testing

Comprehensive test suite in `tests/calibration_system/test_contextual_layers.py`:

```bash
pytest tests/calibration_system/test_contextual_layers.py -v
```

Test coverage:
- ✓ CompatibilityMapping scoring logic
- ✓ Anti-Universality Theorem validation
- ✓ CompatibilityRegistry loading and error handling
- ✓ ContextualLayerEvaluator evaluation methods
- ✓ Integration scenarios

## File Locations

- **Implementation**: `src/farfan_pipeline/core/calibration/compatibility.py`
- **Data Structures**: `src/farfan_pipeline/core/calibration/data_structures.py`
- **Configuration**: `config/json_files_ no_schemas/method_compatibility.json`
- **Tests**: `tests/calibration_system/test_contextual_layers.py`
- **Example**: `examples/contextual_layer_example.py`

## Design Principles

1. **Explicit over Implicit**: Methods must declare their compatibility
2. **Penalty for Undeclared**: 0.1 score for missing declarations
3. **No Universal Methods**: Anti-Universality Theorem enforcement
4. **Immutable Mappings**: CompatibilityMapping is frozen dataclass
5. **Graceful Degradation**: Unknown methods get default mapping

## Future Enhancements

- [ ] Dynamic compatibility learning from historical performance
- [ ] Compatibility score interpolation for similar contexts
- [ ] Multi-version compatibility tracking
- [ ] Compatibility confidence intervals
- [ ] Context-specific penalty adjustments

## References

- Calibration System SUPERPROMPT: Section 4 (Contextual Layers)
- Three-Pillar Calibration System: Definition 1.2 (Context)
- Anti-Universality Theorem: Axiom 2.3
