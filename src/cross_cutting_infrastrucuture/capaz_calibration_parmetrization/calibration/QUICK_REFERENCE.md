# CalibrationOrchestrator - Quick Reference

**SENSITIVE - CALIBRATION SYSTEM CRITICAL**

## Import

```python
from calibration_parametrization_system import (
    CalibrationOrchestrator,
    CalibrationContext,
    CalibrationEvidence,
)
```

## Minimal Usage

```python
orchestrator = CalibrationOrchestrator()
result = orchestrator.calibrate(method_id="your.method.id")
print(result['final_score'])  # 0.0 - 1.0
```

## Full Usage

```python
result = orchestrator.calibrate(
    method_id="farfan_pipeline.core.executors.D1_Q1_Executor",
    context=CalibrationContext(
        question_id="Q001",
        dimension_id="DIM01",
        policy_area_id="PA01",
    ),
    evidence=CalibrationEvidence(
        intrinsic_scores={
            "base_layer_score": 0.85,
            "chain_layer_score": 0.78,
            "contract_layer_score": 0.92,
        },
        pdt_structure={
            "total_tokens": 15000,
            "blocks_found": {"Diagnóstico": {}, "Estratégica": {}, "PPI": {}, "Seguimiento": {}},
            "indicator_matrix_present": True,
            "ppi_matrix_present": True,
        },
        governance_artifacts={
            "version_tag": "COHORT_2024_v1.2.3",
            "config_hash": "a" * 64,
            "signature": "b" * 64,
        },
    ),
)
```

## Result Structure

```python
result = {
    "method_id": str,
    "role": str,                    # executor, ingest, utility, etc.
    "final_score": float,           # 0.0 - 1.0
    "layer_scores": {               # Only active layers
        "b": float,
        "chain": float,
        "q": float,
        # ...
    },
    "active_layers": [str],         # e.g., ["@b", "@chain", "@q", ...]
    "fusion_breakdown": {
        "final_score": float,
        "linear_sum": float,
        "interaction_sum": float,
        "linear_contributions": dict,
        "interaction_contributions": dict,
    },
    "certificate_metadata": {
        "certificate_id": str,      # 16-char hash prefix
        "certificate_hash": str,    # Full SHA256
        "timestamp": str,           # ISO 8601 UTC
        "cohort_id": "COHORT_2024",
        "authority": "Doctrina SIN_CARRETA",
        # ...
    },
    "validation": {
        "is_bounded": bool,
        "original_score": float,
        "clamped_score": float,
        "lower_bound": 0.0,
        "upper_bound": 1.0,
        "violation": str | None,
    },
}
```

## Layer System (8 Layers)

| Layer | Symbol | Description | Source |
|-------|--------|-------------|--------|
| Base | @b | Code quality | intrinsic_scores |
| Chain | @chain | Wiring quality | intrinsic_scores |
| Question | @q | Question fit | method_compatibility |
| Dimension | @d | Dimension fit | method_compatibility |
| Policy | @p | Policy fit | method_compatibility |
| Contract | @C | Contract compliance | intrinsic_scores |
| Unit | @u | Document quality | pdt_structure |
| Meta | @m | Governance | governance_artifacts |

## Role Requirements

| Role | Layers |
|------|--------|
| executor | All 8 layers |
| analyzer | All 8 layers |
| score | All 8 layers |
| core | All 8 layers |
| ingest | @b, @chain, @u, @m (4) |
| processor | @b, @chain, @u, @m (4) |
| extractor | @b, @chain, @u, @m (4) |
| orchestrator | @b, @chain, @m (3) |
| utility | @b, @chain, @m (3) |

## Fusion Formula

```
Cal(I) = Σ(a_ℓ · x_ℓ) + Σ(a_ℓk · min(x_ℓ, x_k))
```

**Linear**: Sum of (weight × layer_score) for active layers  
**Interaction**: Sum of (weight × min(layer1, layer2)) for active pairs  
**Final**: Linear + Interaction  
**Constraint**: All weights sum to 1.0, result ∈ [0,1]

## Common Patterns

### Pattern 1: Calibrate Executor

```python
result = orchestrator.calibrate(
    method_id="farfan_pipeline.core.executors.D1_Q1_Executor",
    context={"question_id": "Q001", "dimension_id": "DIM01"},
    evidence={"intrinsic_scores": {"base_layer_score": 0.85}},
)
```

### Pattern 2: Calibrate with PDT

```python
result = orchestrator.calibrate(
    method_id="farfan_pipeline.processing.ingest.Parser",
    evidence={
        "intrinsic_scores": {"base_layer_score": 0.80},
        "pdt_structure": {
            "total_tokens": 12000,
            "blocks_found": {"Diagnóstico": {}, "Estratégica": {}},
            "indicator_matrix_present": True,
        },
    },
)
```

### Pattern 3: Calibrate Utility (Minimal)

```python
result = orchestrator.calibrate(
    method_id="farfan_pipeline.utils.Helper"
)
# Uses defaults, detects utility role (3 layers)
```

## Accessing Results

```python
# Final score
score = result['final_score']

# Layer breakdown
for layer in result['active_layers']:
    layer_key = layer.lstrip('@')
    print(f"{layer}: {result['layer_scores'][layer_key]}")

# Fusion details
linear = result['fusion_breakdown']['linear_sum']
interaction = result['fusion_breakdown']['interaction_sum']
print(f"Cal(I) = {linear} + {interaction} = {score}")

# Certificate
cert_id = result['certificate_metadata']['certificate_id']
timestamp = result['certificate_metadata']['timestamp']

# Validation
if not result['validation']['is_bounded']:
    print(f"Score clamped: {result['validation']['original_score']}")
```

## Defaults

If evidence not provided:

| Layer | Default |
|-------|---------|
| @b | 0.5 |
| @chain | 0.7 |
| @q | 0.5 |
| @d | 0.5 |
| @p | 0.5 |
| @C | 0.8 |
| @u | 0.5 |
| @m | 0.5 |

## Testing

```bash
pytest tests/test_calibration_orchestrator.py -v
python -m src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_calibration_orchestrator_example
```

## Files

- **Implementation**: `COHORT_2024_calibration_orchestrator.py`
- **API Docs**: `COHORT_2024_calibration_orchestrator_README.md`
- **Examples**: `COHORT_2024_calibration_orchestrator_example.py`
- **Tests**: `tests/test_calibration_orchestrator.py`
- **Config**: `fusion_weights.json`, `COHORT_2024_intrinsic_calibration.json`

## Support

See full documentation: `COHORT_2024_calibration_orchestrator_README.md`  
See implementation index: `COHORT_2024_calibration_orchestrator_INDEX.md`  
See security policy: `SENSITIVE_CRITICAL_SYSTEM.md`
