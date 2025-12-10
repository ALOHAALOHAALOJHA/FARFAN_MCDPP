# Layer Metadata Integration - Quick Start

## Overview

Calibration certificates now embed **complete layer specification provenance**, including formulas, weights, and thresholds for all active layers used in calibration computation.

## What's New

### `LayerMetadata` Structure
```python
@dataclass(frozen=True)
class LayerMetadata:
    symbol: str              # e.g., "@b", "@chain"
    name: str                # e.g., "Base Theory Layer"
    description: str         # Layer purpose
    formula: str             # Computation formula
    weights: dict[str, Any]  # Component weights
    thresholds: dict[str, Any]  # Validation thresholds
```

### Certificate Enhancement
```python
@dataclass(frozen=True)
class CalibrationCertificate:
    # ... existing fields ...
    layer_metadata: dict[str, LayerMetadata]  # NEW FIELD
    # ... remaining fields ...
```

## Usage

```python
from certificate_generator import CertificateGenerator

generator = CertificateGenerator()
certificate = generator.generate_certificate(
    instance_id="exec-001",
    method_id="test.method",
    node_id="node_001",
    context={"test": True},
    intrinsic_score=0.85,
    layer_scores={"@b": 0.90, "@chain": 0.87},
    weights={"@b": 0.6, "@chain": 0.4},
)

# Access layer metadata
for layer_symbol, metadata in certificate.layer_metadata.items():
    print(f"{layer_symbol}: {metadata.name}")
    print(f"  Formula: {metadata.formula}")
    print(f"  Thresholds: {metadata.thresholds}")
```

## Benefits

✓ **Self-Documenting**: Certificates contain all computation specifications  
✓ **Reproducible**: Independent verification without external config files  
✓ **Auditable**: Complete provenance trail for governance compliance  
✓ **Secure**: Layer metadata protected by certificate HMAC signature  

## Documentation

See [LAYER_METADATA_INTEGRATION.md](./LAYER_METADATA_INTEGRATION.md) for complete documentation.

## Examples

Run the demonstration:
```bash
python certificate_examples/usage_example.py
```

See Example 5 for layer metadata demonstration.

## Testing

```bash
python test_layer_metadata_integration.py
```

All tests verify metadata generation, serialization, and signature protection.
