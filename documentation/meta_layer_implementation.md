# Meta Layer (@m) Implementation

## Overview

The Meta Layer (@m) evaluates the operational fitness and governance compliance of methods within the F.A.R.F.A.N calibration system. It measures three core dimensions: **Transparency**, **Governance**, and **Cost**.

## Architecture

### Core Components

1. **MetaLayerConfig**: Configuration dataclass defining weights and requirements
2. **MetaLayerEvaluator**: Main evaluation engine
3. **Artifact Types**: TypedDict definitions for transparency, governance, and cost data
4. **Helper Functions**: Config hash generation and validation utilities

### Configuration

```python
@dataclass(frozen=True)
class MetaLayerConfig:
    w_transparency: float      # Weight for transparency (0.5 default)
    w_governance: float        # Weight for governance (0.4 default)
    w_cost: float             # Weight for cost (0.1 default)
    transparency_requirements: TransparencyRequirements
    governance_requirements: GovernanceRequirements
    cost_thresholds: CostThresholds
```

**Constraints:**
- Weights must sum to 1.0 (±1e-6 tolerance)
- All weights must be non-negative

**Default Configuration:**
```python
config = create_default_config()
# w_transparency=0.5, w_governance=0.4, w_cost=0.1
# threshold_fast=1.0s, threshold_acceptable=5.0s
# threshold_memory_normal=512MB
```

## Evaluation Dimensions

### 1. Transparency (m_transp)

Measures auditability and execution traceability.

**Discrete Scoring:**
- **1.0**: All 3 conditions met
- **0.7**: 2 of 3 conditions met
- **0.4**: 1 of 3 conditions met
- **0.0**: No conditions met

**Required Artifacts:**

#### Formula Export
- Must contain Choquet integral expansion
- Required terms: "Choquet", "Cal(I)", or "x_"
- Minimum 10 characters

```python
{
    "formula_export": "Cal(I) = 0.5*x_@b + 0.4*x_@chain + 0.1*min(x_@b, x_@chain)"
}
```

#### Trace Complete
- Must document execution steps
- Required markers: "step", "phase", or "method"
- Minimum 20 characters

```python
{
    "trace": "Phase 0: Validation -> Phase 1: Ingestion (step 1, step 2) -> Phase 2: Processing"
}
```

#### Logs Conform
- Must be valid JSON object
- Must contain all required fields from schema
- Schema location: `system/config/log_schema.json`

```python
{
    "logs": {
        "timestamp": "2024-12-09T00:00:00Z",
        "level": "INFO",
        "method_name": "D3Q3_Executor.execute",
        "phase": "SCORE_Q",
        "message": "Execution completed successfully"
    }
}
```

### 2. Governance (m_gov)

Evaluates adherence to SIN_CARRETA doctrine (determinism and versioning).

**Discrete Scoring:**
- **1.0**: All 3 conditions met
- **0.66**: 2 of 3 conditions met
- **0.33**: 1 of 3 conditions met
- **0.0**: No conditions met

**Required Artifacts:**

#### Version Tag
- Must not be "unknown", "1.0", or "0.0.0"
- Must be non-empty string
- Example: "v2.1.3", "2024-12-09-release"

```python
{
    "version_tag": "v2.1.3"
}
```

#### Config Hash
- Must be valid SHA256 hex string (64 characters)
- All characters must be valid hex (0-9, a-f)
- Generated via `compute_config_hash()`

```python
{
    "config_hash": "a3c7f8b2e1d4567890abcdef1234567890abcdef1234567890abcdef12345678"
}
```

#### Signature (Optional)
- HMAC of VerificationManifest
- Minimum 32 characters
- Only validated if `require_signature=True`

```python
{
    "signature": "hmac_sha256_signature_of_verification_manifest"
}
```

### 3. Cost (m_cost)

Measures computational efficiency.

**Continuous Scoring:**
- **1.0**: time < threshold_fast AND memory ≤ threshold_memory_normal
- **0.8**: threshold_fast ≤ time < threshold_acceptable AND memory ≤ threshold_memory_normal
- **0.5**: time ≥ threshold_acceptable OR memory > threshold_memory_normal
- **0.0**: Negative values (timeout/OOM indicator)

**Default Thresholds:**
- `threshold_fast`: 1.0 second
- `threshold_acceptable`: 5.0 seconds
- `threshold_memory_normal`: 512 MB

```python
{
    "execution_time_s": 0.8,
    "memory_usage_mb": 256.0
}
```

## Usage

### Basic Evaluation

```python
from src.orchestration.meta_layer import (
    MetaLayerEvaluator,
    create_default_config
)

config = create_default_config()
evaluator = MetaLayerEvaluator(config)

result = evaluator.evaluate(
    transparency_artifacts={
        "formula_export": "Cal(I) = expanded Choquet formula",
        "trace": "Phase execution trace",
        "logs": {...}
    },
    governance_artifacts={
        "version_tag": "v2.1.3",
        "config_hash": "a" * 64,
        "signature": None
    },
    cost_metrics={
        "execution_time_s": 0.8,
        "memory_usage_mb": 256.0
    },
    log_schema={"required": ["timestamp", "level", "method_name", "phase", "message"]}
)

print(f"Overall Score: {result['score']:.3f}")
print(f"Transparency: {result['m_transparency']:.3f}")
print(f"Governance: {result['m_governance']:.3f}")
print(f"Cost: {result['m_cost']:.3f}")
```

### Config Hash Generation

```python
from src.orchestration.meta_layer import compute_config_hash

config_data = {
    "method_name": "D3Q3_Executor",
    "parameters": {"threshold": 0.8},
    "seed": 42,
    "version": "v2.1.3"
}

config_hash = compute_config_hash(config_data)
# Returns: SHA256 hex string (64 chars)
```

### Custom Configuration

```python
from src.orchestration.meta_layer import MetaLayerConfig, MetaLayerEvaluator

config = MetaLayerConfig(
    w_transparency=0.6,
    w_governance=0.3,
    w_cost=0.1,
    transparency_requirements={
        "require_formula_export": True,
        "require_trace_complete": True,
        "require_logs_conform": False  # Relaxed requirement
    },
    governance_requirements={
        "require_version_tag": True,
        "require_config_hash": True,
        "require_signature": True  # Strict requirement
    },
    cost_thresholds={
        "threshold_fast": 0.5,  # Stricter
        "threshold_acceptable": 2.0,  # Stricter
        "threshold_memory_normal": 256.0  # Stricter
    }
)

evaluator = MetaLayerEvaluator(config)
```

## Integration with Calibration System

### VerificationManifest Integration

The Meta Layer integrates with `VerificationManifest` for governance artifacts:

```python
from src.orchestration.verification_manifest import VerificationManifest
from src.orchestration.meta_layer import MetaLayerEvaluator, create_default_config

manifest = VerificationManifest(hmac_secret="secret")
manifest.set_success(True)
manifest.set_pipeline_hash("pipeline_hash_here")
manifest.set_environment()
manifest_data = manifest.build()

governance_artifacts = {
    "version_tag": manifest_data["version"],
    "config_hash": manifest_data.get("pipeline_hash", ""),
    "signature": manifest_data.get("integrity_hmac")
}

evaluator = MetaLayerEvaluator(create_default_config())
# ... evaluate with governance_artifacts
```

### Log Schema Validation

Schema location: `system/config/log_schema.json`

Required fields:
- `timestamp` (ISO 8601 format)
- `level` (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `method_name` (fully qualified)
- `phase` (pipeline phase identifier)
- `message` (log content)

Optional fields:
- `execution_time_ms`
- `memory_mb`
- `correlation_id`
- `seed`
- `error`
- `metadata`

## Scoring Formula

Final meta layer score:

```
x_@m(I) = w_transparency * m_transp + w_governance * m_gov + w_cost * m_cost
```

Where:
- `w_transparency = 0.5` (default)
- `w_governance = 0.4` (default)
- `w_cost = 0.1` (default)
- `m_transp ∈ {0.0, 0.4, 0.7, 1.0}` (discrete)
- `m_gov ∈ {0.0, 0.33, 0.66, 1.0}` (discrete)
- `m_cost ∈ {0.0, 0.5, 0.8, 1.0}` (discrete)

## Examples

See `src/orchestration/meta_layer_example.py` for:
- Full compliance example (score ≈ 1.0)
- Partial compliance example (score ≈ 0.7)
- Poor compliance example (score ≈ 0.05)
- Config hash generation example

## Testing

Run tests:
```bash
pytest tests/test_meta_layer.py -v
```

Test coverage:
- Config validation
- Transparency evaluation (all score levels)
- Governance evaluation (all score levels)
- Cost evaluation (all score levels)
- Full evaluation with weighted aggregation
- Config hash generation and determinism

## References

- Mathematical Foundations: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/mathematical_foundations_capax_system.md` (Section 3.6, CAPA 7)
- COHORT_2024 Reference: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_meta_layer.py`
- Verification Manifest: `src/orchestration/verification_manifest.py`
