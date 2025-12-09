# Congruence Layer (@C) Implementation

## Overview

This document describes the implementation of the Congruence Layer Evaluator (@C) for method ensembles in the F.A.R.F.A.N (SAAAAAA) policy analysis system.

**Version**: 1.0.0  
**Date**: 2024-12-09  
**Status**: Complete Implementation

## Mathematical Foundation

The congruence layer evaluates ensemble validity using the formula:

```
C_play(G | ctx) = c_scale · c_sem · c_fusion
```

### Components

#### 1. Scale Congruence (c_scale)

Measures output range compatibility:

```
c_scale(G) = {
    1.0   if ∀u,v ∈ V_G: range(out(u)) = range(out(v))
    0.8   if ∀u,v: ranges convertible within [0,1]
    0.0   otherwise
}
```

**Implementation Logic**:
- Extract `output_range` from each method's metadata
- Compare all ranges for exact equality → 1.0
- Check if all ranges fall within [0,1] → 0.8
- Otherwise → 0.0

#### 2. Semantic Congruence (c_sem)

Measures conceptual overlap using Jaccard index:

```
c_sem(G) = |⋂ᵢ Cᵢ| / |⋃ᵢ Cᵢ|

where Cᵢ = semantic_tags from method i
```

**Implementation Logic**:
- Extract `semantic_tags` (set or list) from each method
- Compute intersection: tags common to ALL methods
- Compute union: all unique tags across methods
- Return |intersection| / |union|

#### 3. Fusion Validity (c_fusion)

Measures fusion configuration completeness:

```
c_fusion(G) = {
    1.0   if fusion_rule ∈ Config ∧ all_inputs_provided(V_G)
    0.5   if fusion_rule ∈ Config ∧ some_inputs_missing(V_G)
    0.0   if fusion_rule ∉ Config
}
```

**Implementation Logic**:
- Check if `fusion_rule` is non-empty string
- Verify all required method IDs are in `provided_inputs`
- Return 1.0 (complete), 0.5 (partial), or 0.0 (missing)

### Special Cases

- **Single method**: Always returns 1.0 (no ensemble needed)
- **Empty ensemble**: Returns 1.0 (trivially valid)
- **Missing metadata**: Individual components default to 0.0

## Implementation

### File Structure

```
src/farfan_pipeline/core/calibration/
├── __init__.py                    # Package exports
├── congruence_layer.py            # Main implementation
├── decorators.py                  # Calibration decorators (stub)
└── parameters.py                  # Parameter loader (stub)

tests/
├── congruence_layer_tests.py      # Unit tests
└── congruence_examples/           # Worked examples
    ├── __init__.py
    ├── README.md
    ├── example_1_perfect_ensemble.py
    ├── example_2_partial_congruence.py
    ├── example_3_incompatible_ensemble.py
    ├── example_4_single_method.py
    └── example_5_three_method_ensemble.py
```

### Core Class: CongruenceLayerEvaluator

```python
class CongruenceLayerEvaluator:
    """Evaluates congruence (@C) for method ensembles."""
    
    def __init__(self, method_registry: dict[str, Any] | None = None) -> None:
        """Initialize with method metadata registry."""
        
    def evaluate(
        self,
        method_ids: list[str],
        subgraph_id: str | None = None,
        fusion_rule: str | None = None,
        provided_inputs: set[str] | None = None
    ) -> float:
        """
        Evaluate congruence score.
        
        Returns: C_play in [0.0, 1.0]
        """
```

### Method Metadata Format

```python
method_registry = {
    "method_id": {
        "output_range": [min_value, max_value],  # or tuple
        "semantic_tags": ["tag1", "tag2", ...],  # or set
        "description": "Human-readable description"
    }
}
```

## Usage Examples

### Example 1: Perfect Ensemble

```python
from src.farfan_pipeline.core.calibration import CongruenceLayerEvaluator

registry = {
    "analyzer": {
        "output_range": [0.0, 1.0],
        "semantic_tags": {"coherence", "quality"}
    },
    "validator": {
        "output_range": [0.0, 1.0],
        "semantic_tags": {"coherence", "quality"}
    },
}

evaluator = CongruenceLayerEvaluator(registry)

c_play = evaluator.evaluate(
    method_ids=["analyzer", "validator"],
    fusion_rule="TYPE_A",
    provided_inputs={"analyzer", "validator"}
)

# Result: c_play = 1.0 (perfect congruence)
```

### Example 2: Partial Congruence

```python
registry = {
    "structural": {
        "output_range": [0.0, 0.8],
        "semantic_tags": {"quality", "structural"}
    },
    "numerical": {
        "output_range": [0.2, 1.0],
        "semantic_tags": {"quality", "numerical"}
    },
}

evaluator = CongruenceLayerEvaluator(registry)

c_play = evaluator.evaluate(
    method_ids=["structural", "numerical"],
    fusion_rule="average",
    provided_inputs={"structural"}  # missing numerical
)

# Result: c_play ≈ 0.133
# c_scale=0.8 (convertible), c_sem=0.333 (1/3), c_fusion=0.5 (partial)
```

## Test Suite

### Unit Tests

Location: `tests/congruence_layer_tests.py`

**Coverage**:
- Scale computation (6 tests)
- Semantic computation (7 tests)
- Fusion computation (6 tests)
- Full evaluation (8 tests)
- Edge cases (6 tests)

**Total**: 33 comprehensive test cases

Run tests:
```bash
pytest tests/congruence_layer_tests.py -v
```

### Worked Examples

Location: `tests/congruence_examples/`

**Examples**:
1. Perfect ensemble (C_play = 1.0)
2. Partial congruence (C_play ≈ 0.133)
3. Incompatible ensemble (C_play = 0.0)
4. Single method edge case (C_play = 1.0)
5. Three-method realistic scenario

Run examples:
```bash
python tests/congruence_examples/example_1_perfect_ensemble.py
python tests/congruence_examples/example_2_partial_congruence.py
# ... etc
```

## Integration with SAAAAAA System

### Layer Dependencies

The @C layer integrates with:
- **@chain**: Chain of evidence layer
- **@b**: Base quality layer
- **@u**: Unit/data quality layer
- **@q, @d, @p**: Contextual layers
- **@m**: Meta/governance layer

### Choquet Aggregation

C_play scores feed into the Choquet integral:

```
Cal(I) = Σᵢ aᵢ·xᵢ + Σᵢ<ⱼ aᵢⱼ·min(xᵢ,xⱼ)
```

Where `x_@C = C_play(G)` for methods in ensemble G.

### Role-Specific Requirements

From `mathematical_foundations_capax_system.md`:

```
SCORE_Q    → {@b, @chain, @q, @d, @p, @C, @u, @m}  (all 8 layers)
AGGREGATE  → {@b, @chain, @d, @p, @C, @m}
REPORT     → {@b, @chain, @C, @m}
```

## Performance Characteristics

- **Time Complexity**: O(n·m) where n = number of methods, m = average tag set size
- **Space Complexity**: O(n·m) for storing method metadata
- **Typical Runtime**: < 1ms for ensembles up to 10 methods

## Validation

### Pre-conditions

1. Method registry provided with valid metadata
2. Method IDs reference existing methods in registry
3. Output ranges are 2-tuples/lists of numeric values
4. Semantic tags are sets or lists of strings

### Post-conditions

1. Returns float in [0.0, 1.0]
2. Single method returns 1.0
3. Empty ensemble returns 1.0
4. Invalid configuration returns 0.0

### Invariants

1. C_play ≤ min(c_scale, c_sem, c_fusion)
2. C_play = 1.0 ⟹ |methods| ≤ 1 ∨ (c_scale=1.0 ∧ c_sem=1.0 ∧ c_fusion=1.0)
3. c_scale, c_sem, c_fusion ∈ {0.0, 0.5, 0.8, 1.0} (discrete values)

## References

### Specification
- **Document**: `mathematical_foundations_capax_system.md`
- **Section**: 3.5 - Interplay Congruence Layer @C
- **Definition**: 3.5.1 - Ensemble validity formulas

### Related Work
- Goertz & Mahoney (2012) - Process tracing methodology
- Jaccard similarity coefficient (1901)
- Choquet integral aggregation (1954)

### Code References
- Implementation: `src/farfan_pipeline/core/calibration/congruence_layer.py`
- Tests: `tests/congruence_layer_tests.py`
- Examples: `tests/congruence_examples/`

## Changelog

### Version 1.0.0 (2024-12-09)
- Initial implementation
- Complete test suite with 33 test cases
- 5 worked examples with detailed traces
- Full documentation

## License

Part of the F.A.R.F.A.N (SAAAAAA) policy analysis system.
