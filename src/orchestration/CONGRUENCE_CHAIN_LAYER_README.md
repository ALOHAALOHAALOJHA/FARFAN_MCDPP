# Congruence (@C) and Chain (@chain) Layer Evaluators

## Overview

This module implements two critical layer evaluators for the F.A.R.F.A.N. calibration system:

1. **Congruence Layer (@C)**: Evaluates method ensemble harmony through output range compatibility, semantic tag alignment, and fusion rule validity
2. **Chain Layer (@chain)**: Validates method chaining and orchestration through signature validation against upstream outputs

## Congruence Layer (@C)

### Purpose

The Congruence Layer evaluates how well methods work together in an ensemble by measuring three key aspects:

- **c_scale**: Output range compatibility between methods
- **c_sem**: Semantic tag alignment using Jaccard similarity
- **c_fusion**: Fusion rule validity for combining method outputs

The final congruence score is computed as: **C_play = c_scale × c_sem × c_fusion**

### Configuration

```python
from src.orchestration.congruence_layer import (
    CongruenceLayerConfig,
    create_default_congruence_config
)

config = CongruenceLayerConfig(
    w_scale=0.4,          # Weight for output scale compatibility
    w_semantic=0.35,      # Weight for semantic alignment
    w_fusion=0.25,        # Weight for fusion rule validity
    requirements={
        "require_output_range_compatibility": True,
        "require_semantic_alignment": True,
        "require_fusion_validity": True
    },
    thresholds={
        "min_jaccard_similarity": 0.3,          # Minimum semantic overlap
        "max_range_mismatch_ratio": 0.5,        # Maximum range mismatch
        "min_fusion_validity_score": 0.6        # Minimum fusion validity
    }
)
```

### Usage

```python
from src.orchestration.congruence_layer import (
    CongruenceLayerEvaluator,
    OutputRangeSpec,
    SemanticTagSet,
    FusionRule
)

evaluator = CongruenceLayerEvaluator(config)

# Define method specifications
current_range = OutputRangeSpec(min=0.0, max=1.0, output_type="float")
upstream_range = OutputRangeSpec(min=0.0, max=1.0, output_type="float")

current_tags = SemanticTagSet(
    tags={"causal", "temporal", "numeric"},
    description="Causal mechanism extraction"
)
upstream_tags = SemanticTagSet(
    tags={"causal", "temporal"},
    description="Policy text processing"
)

fusion = FusionRule(
    rule_type="aggregation",
    operator="weighted_avg",
    is_valid=True,
    description="Weighted average aggregation"
)

# Evaluate congruence
result = evaluator.evaluate(
    current_range, upstream_range,
    current_tags, upstream_tags,
    fusion, fusion_context={"input_count": 3, "weights": [0.5, 0.3, 0.2]}
)

print(f"C_play: {result['C_play']:.3f}")
print(f"c_scale: {result['c_scale']:.3f}")
print(f"c_sem: {result['c_sem']:.3f}")
print(f"c_fusion: {result['c_fusion']:.3f}")
```

### Metrics

#### c_scale (Output Range Compatibility)
- Measures overlap between output ranges of current and upstream methods
- Returns 0.0 for no overlap, 1.0 for perfect overlap
- Penalizes large range mismatches

#### c_sem (Semantic Alignment)
- Computes Jaccard similarity: |A ∩ B| / |A ∪ B|
- Returns 0.0 if similarity below threshold
- 1.0 indicates perfect tag overlap

#### c_fusion (Fusion Rule Validity)
- Validates fusion rule type and operator
- Checks weight configuration for weighted operations
- Returns 0.0 for invalid rules, 1.0 for valid rules

## Chain Layer (@chain)

### Purpose

The Chain Layer validates method chaining by ensuring that each method's signature requirements are met by upstream outputs. It implements discrete scoring based on validation failures:

- **0.0**: Missing required inputs (hard failure)
- **0.3**: Missing critical optional inputs
- **0.6**: Missing optional inputs (when penalized)
- **0.8**: Warnings present
- **1.0**: Perfect chain (all inputs available)

### Configuration

```python
from src.orchestration.chain_layer import (
    ChainLayerConfig,
    create_default_chain_config
)

config = ChainLayerConfig(
    validation_config={
        "strict_mode": False,
        "allow_missing_optional": True,
        "penalize_warnings": True
    },
    score_missing_required=0.0,
    score_missing_critical=0.3,
    score_missing_optional=0.6,
    score_warnings=0.8,
    score_perfect=1.0
)
```

### Usage

```python
from src.orchestration.chain_layer import (
    ChainLayerEvaluator,
    MethodSignature,
    UpstreamOutputs
)

evaluator = ChainLayerEvaluator(config)

# Define method signature
signature = MethodSignature(
    required_inputs=["policy_text", "dimension_id"],
    optional_inputs=["metadata", "context"],
    critical_optional=["context"],
    output_type="dict",
    output_range=[0.0, 1.0]
)

# Define upstream outputs
upstream = UpstreamOutputs(
    available_outputs={"policy_text", "dimension_id", "context"},
    output_types={
        "policy_text": "str",
        "dimension_id": "str",
        "context": "dict"
    }
)

# Evaluate chain
result = evaluator.evaluate(signature, upstream)

print(f"Chain Score: {result['chain_score']:.1f}")
print(f"Status: {result['validation_status']}")
print(f"Missing Required: {result['missing_required']}")
print(f"Missing Critical: {result['missing_critical']}")
```

### Chain Sequence Evaluation

The evaluator can also validate entire method sequences:

```python
method_signatures = [
    ("PolicyIngestor", signature1),
    ("PolicyProcessor", signature2),
    ("CausalExtractor", signature3),
    ("ScoreAggregator", signature4)
]

initial_inputs = {"raw_policy_document"}

result = evaluator.evaluate_chain_sequence(method_signatures, initial_inputs)

print(f"Sequence Score: {result['sequence_score']:.2f}")
print(f"Failed Methods: {result['failed_methods']}/{result['total_methods']}")
```

### Validation Statuses

- **failed_missing_required**: One or more required inputs are missing (score: 0.0)
- **failed_missing_critical**: One or more critical optional inputs are missing (score: 0.3)
- **passed_missing_optional**: Optional inputs missing but allowed (score: 0.6)
- **passed_with_warnings**: Minor issues detected (score: 0.8)
- **perfect**: All inputs available, no issues (score: 1.0)

## Integration with Calibration System

Both evaluators integrate with the F.A.R.F.A.N. calibration system:

### Layer Assignment

```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_layer_assignment import (
    LAYER_REQUIREMENTS,
    CHOQUET_WEIGHTS
)

# Methods requiring @C and @chain layers
"analyzer": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]
"executor": ["@b", "@chain", "@q", "@d", "@p", "@C", "@u", "@m"]
```

### Weight Configuration

```python
CHOQUET_WEIGHTS = {
    "@chain": 0.13,
    "@C": 0.08,
    # ... other layers
}

CHOQUET_INTERACTION_WEIGHTS = {
    ("@chain", "@C"): 0.10,
    # ... other interactions
}
```

## File Structure

```
src/orchestration/
├── congruence_layer.py              # Congruence Layer implementation
├── chain_layer.py                   # Chain Layer implementation
├── congruence_layer_example.py      # Usage examples for @C
├── chain_layer_example.py           # Usage examples for @chain
└── CONGRUENCE_CHAIN_LAYER_README.md # This file

tests/
├── test_congruence_layer.py         # Congruence Layer tests
└── test_chain_layer.py              # Chain Layer tests

src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/
├── COHORT_2024_congruence_layer.py  # COHORT_2024 reference
└── COHORT_2024_chain_layer.py       # COHORT_2024 reference
```

## Examples

See example files for detailed usage:
- `congruence_layer_example.py` - 5 comprehensive examples for @C layer
- `chain_layer_example.py` - 8 comprehensive examples for @chain layer

Run examples:
```bash
python src/orchestration/congruence_layer_example.py
python src/orchestration/chain_layer_example.py
```

## Testing

Run tests with pytest:
```bash
pytest tests/test_congruence_layer.py -v
pytest tests/test_chain_layer.py -v
```

## Technical Details

### Type Safety
Both evaluators use TypedDict for strict type checking and contract enforcement.

### Determinism
All calculations are deterministic with no random components, ensuring reproducible results.

### Performance
- Congruence evaluation: O(n) for n semantic tags
- Chain validation: O(m) for m required/optional inputs
- Sequence evaluation: O(k·m) for k methods with m inputs each

### Error Handling
- Invalid configurations raise ValueError at construction
- Missing inputs are tracked and reported
- Type mismatches generate warnings

## References

- Canonical Notation: `sensitive_rules_for_coding/canonical_notation/notation_metods`
- Layer Assignment: `COHORT_2024_layer_assignment.py`
- Method Signature Validation: `method_signature_validator.py`
