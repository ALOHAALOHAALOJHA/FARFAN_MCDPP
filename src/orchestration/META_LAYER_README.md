# Meta Layer (@m) - Quick Reference

## What is the Meta Layer?

The Meta Layer (@m) evaluates operational fitness and governance compliance of methods in the calibration system. It measures:

- **Transparency** (50%): Auditability and traceability
- **Governance** (40%): Version control and determinism
- **Cost** (10%): Computational efficiency

## Quick Start

```python
from src.orchestration.meta_layer import (
    MetaLayerEvaluator,
    create_default_config
)

evaluator = MetaLayerEvaluator(create_default_config())

result = evaluator.evaluate(
    transparency_artifacts={
        "formula_export": "Cal(I) = Choquet expanded formula",
        "trace": "Phase 0 -> Phase 1 -> Phase 2",
        "logs": {"timestamp": "...", "level": "INFO", ...}
    },
    governance_artifacts={
        "version_tag": "v2.1.3",
        "config_hash": "a" * 64,
        "signature": None
    },
    cost_metrics={
        "execution_time_s": 0.8,
        "memory_usage_mb": 256.0
    }
)

print(f"Score: {result['score']:.3f}")
```

## Scoring

### Transparency (m_transp)
- **1.0**: Formula + Trace + Logs (all 3)
- **0.7**: 2 of 3 conditions
- **0.4**: 1 of 3 conditions
- **0.0**: None

### Governance (m_gov)
- **1.0**: Version + ConfigHash + Signature (all 3)
- **0.66**: 2 of 3 conditions
- **0.33**: 1 of 3 conditions
- **0.0**: None

### Cost (m_cost)
- **1.0**: time < 1.0s AND memory ≤ 512MB (fast)
- **0.8**: time < 5.0s AND memory ≤ 512MB (acceptable)
- **0.5**: time ≥ 5.0s OR memory > 512MB (poor)
- **0.0**: timeout/OOM

## Files

- **Implementation**: `src/orchestration/meta_layer.py`
- **Tests**: `tests/test_meta_layer.py`
- **Example**: `src/orchestration/meta_layer_example.py`
- **Documentation**: `documentation/meta_layer_implementation.md`
- **Log Schema**: `system/config/log_schema.json`

## Run Example

```bash
python -m src.orchestration.meta_layer_example
```

## Run Tests

```bash
pytest tests/test_meta_layer.py -v
```

## Key Functions

```python
# Create default config
config = create_default_config()

# Create evaluator
evaluator = MetaLayerEvaluator(config)

# Evaluate transparency only
score = evaluator.evaluate_transparency(artifacts, log_schema)

# Evaluate governance only
score = evaluator.evaluate_governance(artifacts)

# Evaluate cost only
score = evaluator.evaluate_cost(metrics)

# Full evaluation
result = evaluator.evaluate(transp_arts, gov_arts, cost_metrics)

# Generate config hash
hash_str = compute_config_hash(config_dict)
```

## Artifact Requirements

### Formula Export
- Contains "Choquet", "Cal(I)", or "x_"
- Minimum 10 characters

### Trace
- Contains "step", "phase", or "method"
- Minimum 20 characters

### Logs
- Valid JSON with required fields
- Schema: `system/config/log_schema.json`

### Version Tag
- NOT "unknown", "1.0", or "0.0.0"
- Non-empty string

### Config Hash
- 64-character hex string (SHA256)
- Generated via `compute_config_hash()`

### Signature
- HMAC of VerificationManifest
- Minimum 32 characters
- Only checked if `require_signature=True`

## Integration Points

1. **VerificationManifest**: Provides governance artifacts
2. **Log Schema**: Validates structured logs
3. **Calibration System**: Contributes x_@m score to Cal(I)

## Formula

```
x_@m(I) = 0.5 * m_transp + 0.4 * m_gov + 0.1 * m_cost
```

Default weights: 50% transparency, 40% governance, 10% cost
