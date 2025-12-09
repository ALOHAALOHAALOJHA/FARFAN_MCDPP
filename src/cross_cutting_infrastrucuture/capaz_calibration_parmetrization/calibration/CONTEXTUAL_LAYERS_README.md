# Contextual Layer Evaluators (@q, @d, @p)

**COHORT_2024 - REFACTOR_WAVE_2024_12**  
**Created**: 2024-12-15T00:00:00+00:00  
**Status**: SENSITIVE - Calibration System

## Overview

The contextual layer evaluators implement compatibility-based scoring for three critical calibration layers:

- **@q (Question Layer)**: Evaluates method compatibility with specific questions (Q001-Q300)
- **@d (Dimension Layer)**: Evaluates method compatibility with analytical dimensions (DIM01-DIM06)
- **@p (Policy Layer)**: Evaluates method compatibility with policy areas (PA01-PA10)

These layers enforce the **Anti-Universality Theorem**: No method can score >0.9 across all contexts simultaneously, ensuring analytical specialization.

## Architecture

### CompatibilityRegistry

Central registry that loads method compatibility data from `COHORT_2024_method_compatibility.json`.

**Key Features:**
- Loads and validates COHORT_2024 metadata
- Enforces anti-universality constraint on initialization
- Provides evaluation methods for all three contextual layers
- Returns 0.1 penalty for unmapped methods

**Usage:**
```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_contextual_layers import (
    CompatibilityRegistry
)

registry = CompatibilityRegistry()

# Evaluate question compatibility
score = registry.evaluate_question("pattern_extractor_v2", "Q001")  # → 1.0
score = registry.evaluate_question("pattern_extractor_v2", "Q999")  # → 0.1 (penalty)

# Evaluate dimension compatibility
score = registry.evaluate_dimension("pattern_extractor_v2", "DIM01")  # → 1.0

# Evaluate policy compatibility
score = registry.evaluate_policy("pattern_extractor_v2", "PA01")  # → 1.0
```

### Layer Evaluators

Three specialized evaluators wrap the registry:

#### QuestionEvaluator (@q)
```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_question_layer import (
    QuestionEvaluator
)

q_eval = QuestionEvaluator(registry)
score = q_eval.evaluate("method_id", "Q001")
```

#### DimensionEvaluator (@d)
```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_dimension_layer import (
    DimensionEvaluator
)

d_eval = DimensionEvaluator(registry)
score = d_eval.evaluate("method_id", "DIM01")
```

#### PolicyEvaluator (@p)
```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_policy_layer import (
    PolicyEvaluator
)

p_eval = PolicyEvaluator(registry)
score = p_eval.evaluate("method_id", "PA01")
```

### Factory Function

Create all three evaluators with a shared registry:

```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_contextual_layers import (
    create_contextual_evaluators
)

q_eval, d_eval, p_eval = create_contextual_evaluators()

# All evaluators share the same registry instance
assert q_eval.registry is d_eval.registry
assert d_eval.registry is p_eval.registry
```

## Priority Mapping

Compatibility scores map from priority levels defined in `COHORT_2024_method_compatibility.json`:

| Priority | Label | Score |
|----------|-------|-------|
| 3 | CRÍTICO (Critical) | 1.0 |
| 2 | IMPORTANTE (Important) | 0.7 |
| 1 | COMPLEMENTARIO (Complementary) | 0.3 |
| unmapped | NOT DECLARED | 0.1 (penalty) |

## Anti-Universality Theorem

**Constraint:** No method can have compatibility scores >0.9 across all questions, dimensions, and policies simultaneously.

**Enforcement:** 
- Validated on registry initialization
- Raises `ValueError` if any method violates the constraint
- Per-method validation available via `validate_method_universality()`

**Example Violation:**
```python
# This would raise ValueError during registry load
{
  "method_compatibility": {
    "universal_method": {
      "questions": {"Q001": 1.0, "Q002": 1.0, ...},  # All >0.9
      "dimensions": {"DIM01": 1.0, "DIM02": 1.0, ...},  # All >0.9
      "policies": {"PA01": 1.0, "PA02": 1.0, ...}  # All >0.9
    }
  }
}
# ValueError: Anti-Universality violation: Method 'universal_method' 
# has scores >0.9 across all contexts
```

**Valid Specialization:**
```python
{
  "method_compatibility": {
    "specialized_method": {
      "questions": {"Q001": 1.0, "Q031": 0.7, "Q091": 0.3},  # Max 1.0
      "dimensions": {"DIM01": 1.0, "DIM02": 0.7, "DIM03": 0.3},  # Max 1.0
      "policies": {"PA01": 1.0, "PA10": 0.7, "PA03": 0.3}  # Max 1.0
    }
  }
}
# Valid: Not all contexts have max scores simultaneously
```

## Data File Structure

### COHORT_2024_method_compatibility.json

```json
{
  "_cohort_metadata": {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12"
  },
  "method_compatibility": {
    "method_id": {
      "questions": {
        "Q001": 1.0,
        "Q031": 0.7,
        "Q091": 0.3
      },
      "dimensions": {
        "DIM01": 1.0,
        "DIM02": 0.7,
        "DIM03": 0.3
      },
      "policies": {
        "PA01": 1.0,
        "PA10": 0.7,
        "PA03": 0.3
      }
    }
  }
}
```

## Unmapped Method Penalty

When a method or context is not declared in the compatibility registry, a penalty score of **0.1** is returned.

**Scenarios:**
1. Method not in registry: `registry.evaluate_question("unknown_method", "Q001")` → 0.1
2. Context not declared for method: `registry.evaluate_question("known_method", "Q999")` → 0.1
3. Empty context mapping: Method in registry but no questions declared → 0.1

**Design Rationale:** 
- Prevents silent failures (method not erroring but receiving 0.0)
- Penalizes incomplete calibration data
- Enforces explicit declaration of all method-context relationships

## Integration with Calibration System

The contextual layers integrate into the 8-layer calibration system:

```
Full Layer Stack:
├── @b (Base/Intrinsic)
├── @chain (Method Wiring)
├── @q (Question) ◄── Contextual Layer Evaluator
├── @d (Dimension) ◄── Contextual Layer Evaluator
├── @p (Policy) ◄── Contextual Layer Evaluator
├── @C (Contract Compliance)
├── @u (Unit/Document Quality)
└── @m (Meta/Governance)
```

**Usage in Choquet Integral:**
```python
registry = CompatibilityRegistry()
q_eval = QuestionEvaluator(registry)
d_eval = DimensionEvaluator(registry)
p_eval = PolicyEvaluator(registry)

# For method M in context (Q, D, P)
x_q = q_eval.evaluate(method_id, question_id)
x_d = d_eval.evaluate(method_id, dimension_id)
x_p = p_eval.evaluate(method_id, policy_id)

# These feed into Choquet integral with other layers
# Cal(I) = Σ(a_ℓ × x_ℓ) + Σ(a_ℓk × min(x_ℓ, x_k))
```

## Files

| File | Purpose |
|------|---------|
| `COHORT_2024_contextual_layers.py` | Main implementation (CompatibilityRegistry + evaluators) |
| `COHORT_2024_question_layer.py` | Reference stub for @q evaluator |
| `COHORT_2024_dimension_layer.py` | Reference stub for @d evaluator |
| `COHORT_2024_policy_layer.py` | Reference stub for @p evaluator |
| `COHORT_2024_method_compatibility.json` | Compatibility data source |
| `CONTEXTUAL_LAYERS_README.md` | This documentation |

## Testing

Comprehensive test suite in `tests/test_contextual_layers.py`:

```bash
pytest tests/test_contextual_layers.py -v
```

**Test Coverage:**
- Registry initialization and validation
- COHORT_2024 metadata validation
- Anti-universality enforcement
- Score evaluation for all three layers
- Penalty application for unmapped methods
- Factory function
- Real-world integration scenarios

## Governance

**Doctrina SIN_CARRETA Compliance:**
- WHAT (Calibration): Compatibility scores defined in JSON
- HOW (Parametrization): N/A (static calibration layer)
- Separation: Strict adherence to calibration-only role

**Determinism:**
- No randomness or stochastic elements
- Pure function evaluation: same inputs → same outputs
- Registry loaded once, immutable during evaluation

**Auditability:**
- All scores traceable to `COHORT_2024_method_compatibility.json`
- Anti-universality violations caught at load time
- Penalty application logged and explicit

## Migration Path

For future cohorts (COHORT_2025, etc.):

1. Copy `COHORT_2024_method_compatibility.json` → `COHORT_2025_method_compatibility.json`
2. Update `_cohort_metadata.cohort_id` to `COHORT_2025`
3. Update compatibility scores as needed
4. Validate anti-universality constraint
5. Update registry default path in `CompatibilityRegistry.__init__()`

**No code changes required** - only data file updates.

## API Reference

### CompatibilityRegistry

```python
class CompatibilityRegistry:
    UNMAPPED_PENALTY: float = 0.1
    ANTI_UNIVERSALITY_THRESHOLD: float = 0.9
    
    def __init__(self, config_path: Path | str | None = None)
    def evaluate_question(self, method_id: str, question_id: str) -> float
    def evaluate_dimension(self, method_id: str, dimension_id: str) -> float
    def evaluate_policy(self, method_id: str, policy_id: str) -> float
    def get_method_compatibility(self, method_id: str) -> CompatibilityMapping | None
    def validate_method_universality(self, method_id: str) -> tuple[bool, str]
    def list_methods(self) -> list[str]
    def get_metadata(self) -> dict[str, Any]
```

### QuestionEvaluator

```python
class QuestionEvaluator:
    def __init__(self, registry: CompatibilityRegistry)
    def evaluate(self, method_id: str, question_id: str) -> float
```

### DimensionEvaluator

```python
class DimensionEvaluator:
    def __init__(self, registry: CompatibilityRegistry)
    def evaluate(self, method_id: str, dimension_id: str) -> float
```

### PolicyEvaluator

```python
class PolicyEvaluator:
    def __init__(self, registry: CompatibilityRegistry)
    def evaluate(self, method_id: str, policy_id: str) -> float
```

### Factory

```python
def create_contextual_evaluators(
    config_path: Path | str | None = None
) -> tuple[QuestionEvaluator, DimensionEvaluator, PolicyEvaluator]
```

## Support

For questions or issues:
1. Review this documentation
2. Check `mathematical_foundations_capax_system.md` for theoretical foundations
3. Inspect `COHORT_2024_method_compatibility.json` for current compatibility data
4. Run test suite for validation: `pytest tests/test_contextual_layers.py -v`
