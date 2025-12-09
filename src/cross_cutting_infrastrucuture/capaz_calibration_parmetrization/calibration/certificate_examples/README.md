# Calibration Certificate System

## Overview

The Calibration Certificate Generation system provides complete audit trails for method calibration in the F.A.R.F.A.N. policy analysis pipeline. Each certificate is a cryptographically signed document that captures:

- **Full computation trace**: Step-by-step computation showing how the calibrated score is derived
- **Parameter provenance**: Source file, line, and justification for every parameter
- **Evidence trail**: All evidence used in layer score computations
- **Validation checks**: Boundedness, monotonicity, normalization, and completeness
- **Reproducibility**: SHA256 hashes of config files and computation graph
- **Integrity**: HMAC-SHA256 signature proving certificate has not been tampered with

## Certificate Structure

### Fields

```python
@dataclass(frozen=True)
class CalibrationCertificate:
    certificate_version: str           # Certificate schema version (1.0.0)
    instance_id: str                   # Unique identifier for this execution
    method_id: str                     # Full method identifier
    node_id: str                       # Computation graph node identifier
    context: dict[str, Any]            # Execution context (document_id, dimension, etc.)
    intrinsic_score: float             # Base intrinsic quality score [0,1]
    layer_scores: dict[str, float]     # Scores for each layer (@b, @chain, @q, etc.)
    calibrated_score: float            # Final calibrated score after fusion
    fusion_formula: FusionFormula      # Symbolic, expanded, and traced computation
    parameter_provenance: dict[str, ParameterProvenance]  # Source of each parameter
    evidence_trail: dict[str, Any]     # Evidence used in layer computations
    config_hash: str                   # SHA256 of all config files
    graph_hash: str                    # SHA256 of computation graph structure
    validation_checks: ValidationChecks # Boundedness, monotonicity, etc.
    timestamp: str                     # ISO 8601 UTC timestamp
    validator_version: str             # Certificate generator version
    signature: str                     # HMAC-SHA256 signature
```

### Fusion Formula

The fusion formula captures the complete computation:

```python
@dataclass(frozen=True)
class FusionFormula:
    symbolic: str                      # "Σ(aₗ·xₗ) + Σ(aₗₖ·min(xₗ,xₖ))"
    expanded: str                      # Actual formula with numeric weights
    computation_trace: list[dict]      # Step-by-step computation log
```

**Computation Trace** includes:
- Step number
- Operation performed
- Input values (layer, score, weight)
- Result of operation
- Cumulative score

### Parameter Provenance

Each parameter (weight) includes full provenance:

```python
@dataclass(frozen=True)
class ParameterProvenance:
    value: float                       # Parameter value
    source: str                        # Source file and location
    justification: str                 # Human-readable explanation
```

Example:
```json
{
  "a_@b": {
    "value": 0.17,
    "source": "COHORT_2024_fusion_weights.json:weights",
    "justification": "Linear weight for layer @b from COHORT_2024 fusion specification"
  }
}
```

### Validation Checks

Four categories of validation:

1. **Boundedness**: All scores in [0,1]
2. **Monotonicity**: All weights ≥ 0 (non-decreasing)
3. **Normalization**: Sum of weights = 1.0 (within tolerance)
4. **Completeness**: All required layers present, no extras

## Usage

### Basic Certificate Generation

```python
from certificate_generator import CertificateGenerator

generator = CertificateGenerator()

certificate = generator.generate_certificate(
    instance_id="exec-d1q1-20241215-001",
    method_id="farfan_pipeline.core.orchestrator.executors.D1_Q1_TerritorialCoherenceEvaluator",
    node_id="node_exec_d1_q1_001",
    context={
        "document_id": "PDM-BOG-2024-001",
        "dimension": "D1",
        "question": "Q1",
    },
    intrinsic_score=0.87,
    layer_scores={
        "@b": 0.92,
        "@chain": 0.88,
        "@q": 0.85,
        "@d": 0.90,
        "@p": 0.83,
        "@C": 0.89,
        "@u": 0.78,
        "@m": 0.81,
    },
    weights={
        "@b": 0.17,
        "@chain": 0.13,
        "@q": 0.08,
        "@d": 0.07,
        "@p": 0.06,
        "@C": 0.08,
        "@u": 0.04,
        "@m": 0.04,
    },
    interaction_weights={
        "@u,@chain": 0.13,
        "@chain,@C": 0.10,
        "@q,@d": 0.10,
    },
    evidence_trail={
        "@b": {
            "source": "intrinsic_calibration_rubric.json",
            "components": {...},
        },
    },
    computation_graph={
        "nodes": ["parser", "executor", "aggregator"],
        "edges": [["parser", "executor"], ["executor", "aggregator"]],
    },
)
```

### Certificate Verification

```python
is_valid = generator.verify_certificate(certificate)
if is_valid:
    print("✓ Certificate signature is valid")
else:
    print("✗ Certificate has been tampered with")
```

### Export to JSON

```python
# Export certificate to JSON
json_str = certificate.to_json(indent=2)

# Save to file
with open("certificate.json", "w") as f:
    f.write(json_str)
```

### Custom Configuration

```python
from pathlib import Path

generator = CertificateGenerator(
    config_dir=Path("path/to/config"),
    secret_key=b"your-secret-key-here"
)
```

## Certificate Examples

This directory contains sample certificates:

1. **`example_executor_certificate.json`**: Certificate for a Phase 2 executor (D1_Q1)
   - All 8 layers evaluated
   - Full computation trace with 12 steps
   - Complete evidence trail for each layer
   - All validation checks passing

2. **`example_analyzer_certificate.json`**: Certificate for Theory of Change analyzer
   - Cross-dimensional analysis
   - Complex computation graph
   - Multiple policy areas covered

3. **`usage_example.py`**: Python script demonstrating:
   - Certificate generation
   - Signature verification
   - Tampering detection
   - Config/graph hashing

## Layers and Weights

The COHORT_2024 calibration system uses 8 layers:

| Layer | Description | Weight |
|-------|-------------|--------|
| @b | Code quality (base theory) | 0.17 |
| @chain | Method wiring/orchestration | 0.13 |
| @q | Question appropriateness | 0.08 |
| @d | Dimension alignment | 0.07 |
| @p | Policy area fit | 0.06 |
| @C | Contract compliance | 0.08 |
| @u | Document quality | 0.04 |
| @m | Governance maturity | 0.04 |

**Interaction weights** (Choquet integral):
- (@u, @chain): 0.13 - Document quality synergy with orchestration
- (@chain, @C): 0.10 - Orchestration synergy with contract compliance
- (@q, @d): 0.10 - Question appropriateness synergy with dimension alignment

Total: 0.67 (linear) + 0.33 (interaction) = 1.00

## Fusion Formula

The calibrated score is computed using a Choquet integral:

```
Cal(I) = Σ(aₗ·xₗ) + Σ(aₗₖ·min(xₗ,xₖ))
```

Where:
- `aₗ` = linear weight for layer ℓ
- `xₗ` = score for layer ℓ
- `aₗₖ` = interaction weight for layers ℓ and k
- `min(xₗ,xₖ)` = minimum score (captures synergy)

**Properties**:
- Bounded: Cal(I) ∈ [0,1]
- Monotonic: ∂Cal/∂xₗ ≥ 0 for all ℓ
- Normalized: Σ(aₗ) + Σ(aₗₖ) = 1.0

## Security and Integrity

### HMAC Signature

Each certificate is signed using HMAC-SHA256:

```python
signature = HMAC-SHA256(secret_key, canonical_json(certificate_data))
```

The signature:
- Proves certificate integrity (not tampered)
- Verifies authenticity (signed by trusted generator)
- Uses deterministic JSON serialization (sorted keys)

### Config and Graph Hashing

**Config Hash** (SHA256):
- Combines all config files (fusion_weights.json, layer_assignment.py, intrinsic_calibration.json)
- Ensures reproducibility across runs with same config

**Graph Hash** (SHA256):
- Hashes computation graph structure (nodes, edges)
- Detects changes in method wiring/orchestration

### Tampering Detection

Any modification to the certificate will invalidate the signature:

```python
# Original certificate
is_valid = generator.verify_certificate(certificate)
# => True

# Tampered certificate (score changed)
tampered = replace(certificate, calibrated_score=0.99)
is_valid = generator.verify_certificate(tampered)
# => False
```

## Integration with F.A.R.F.A.N.

Certificates can be integrated into the pipeline at multiple points:

1. **Executor Level**: Generate certificate after each executor completes
2. **Aggregation Level**: Generate certificate for aggregated scores
3. **Audit Trail**: Store certificates in evidence registry
4. **Reporting**: Include certificate summaries in final reports

Example integration:

```python
from canonic_phases.Phase_two.executors import D1_Q1_TerritorialCoherenceEvaluator
from certificate_generator import CertificateGenerator

executor = D1_Q1_TerritorialCoherenceEvaluator()
result = executor.execute(context)

# Generate certificate
generator = CertificateGenerator()
certificate = generator.generate_certificate(
    instance_id=f"exec-{executor.class_name}-{timestamp}",
    method_id=executor.method_id,
    node_id=executor.node_id,
    context=context,
    intrinsic_score=result["intrinsic_score"],
    layer_scores=result["layer_scores"],
    weights=executor.weights,
    interaction_weights=executor.interaction_weights,
    evidence_trail=result["evidence"],
    computation_graph=executor.computation_graph,
)

# Store certificate
evidence_registry.store_certificate(certificate)
```

## File Locations

```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/
├── certificate_generator.py              # Main generator implementation
├── certificate_examples/
│   ├── README.md                         # This file
│   ├── example_executor_certificate.json # Sample executor certificate
│   ├── example_analyzer_certificate.json # Sample analyzer certificate
│   └── usage_example.py                  # Usage examples script
├── COHORT_2024_fusion_weights.json       # Weight specifications
├── COHORT_2024_layer_assignment.py       # Layer assignments
└── COHORT_2024_intrinsic_calibration.json # Intrinsic scoring config
```

## Version History

- **1.0.0** (2024-12-15): Initial release
  - Full audit trail support
  - HMAC-SHA256 signatures
  - Config and graph hashing
  - Validation checks
  - Parameter provenance tracking

## References

- **COHORT_2024 Specification**: `COHORT_MANIFEST.json`
- **Fusion Weights**: `COHORT_2024_fusion_weights.json`
- **Layer System**: `COHORT_2024_layer_assignment.py`
- **Intrinsic Calibration**: `COHORT_2024_intrinsic_calibration_rubric.json`
