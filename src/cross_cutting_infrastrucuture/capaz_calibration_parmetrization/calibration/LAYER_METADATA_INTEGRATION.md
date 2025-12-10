# Layer Metadata Integration in Calibration Certificates

**Version:** 1.0.0  
**Date:** 2024-12-15  
**Authority:** F.A.R.F.A.N. Calibration System

---

## Overview

The Layer Metadata Integration extends the CalibrationCertificate system to embed complete layer specification provenance directly into certificates. This enhancement provides self-documenting certificates that enable independent reproducibility verification without requiring external configuration files.

## Purpose

### Audit Trail Enhancement
- **Complete Provenance**: Each certificate now contains the exact formulas, weights, and thresholds used for all active layers during calibration
- **Self-Documentation**: Certificates are fully self-contained with no external dependencies for verification
- **Reproducibility**: Independent auditors can verify computations using only the certificate data

### Governance Benefits
- **Transparency**: All layer computation specifications are explicitly documented
- **Traceability**: Full audit trail from raw scores to calibrated output
- **Version Control**: Layer specifications are locked in each certificate for historical comparison

---

## Architecture

### New Data Structure: `LayerMetadata`

```python
@dataclass(frozen=True)
class LayerMetadata:
    symbol: str              # Layer symbol (e.g., "@b", "@chain")
    name: str                # Human-readable layer name
    description: str         # Layer purpose and scope
    formula: str             # Mathematical formula for layer computation
    weights: dict[str, Any]  # Component weights used in computation
    thresholds: dict[str, Any]  # Thresholds and validation rules
```

### Updated Certificate Structure

The `CalibrationCertificate` now includes:

```python
@dataclass(frozen=True)
class CalibrationCertificate:
    # ... existing fields ...
    layer_metadata: dict[str, LayerMetadata]  # NEW: Complete layer specifications
    # ... remaining fields ...
```

---

## Layer Definitions

The system includes complete metadata for all 8 calibration layers:

### 1. **@b - Base Theory Layer**
- **Formula**: `b = 0.40·b_theory + 0.35·b_impl + 0.25·b_deploy`
- **Purpose**: Code quality and theoretical soundness
- **Weights**: Theory (0.40), Implementation (0.35), Deployment (0.25)
- **Thresholds**: min_score_SCORE_Q (0.7), required_coverage (0.8)

### 2. **@chain - Chain Layer**
- **Formula**: `chain = discrete({0.0, 0.3, 0.6, 0.8, 1.0})`
- **Purpose**: Method wiring and orchestration integrity
- **Weights**: Discrete level mapping based on contract satisfaction
- **Thresholds**: missing_optional_ratio (0.5), no_cycles_allowed

### 3. **@q - Question Layer**
- **Formula**: `q = compatibility_score(method_id, question_id)`
- **Purpose**: Question appropriateness and alignment
- **Weights**: Priority-based (CRÍTICO: 1.0, IMPORTANTE: 0.7, COMPLEMENTARIO: 0.3)
- **Thresholds**: unmapped_penalty (0.1), anti_universality (0.9)

### 4. **@d - Dimension Layer**
- **Formula**: `d = compatibility_score(method_id, dimension_id)`
- **Purpose**: Dimensional analysis alignment
- **Weights**: Priority-based mapping (same as @q)
- **Thresholds**: required_coverage (0.75), anti_universality (0.9)

### 5. **@p - Policy Layer**
- **Formula**: `p = compatibility_score(method_id, policy_id)`
- **Purpose**: Policy area fit and domain alignment
- **Weights**: Priority-based mapping (same as @q, @d)
- **Thresholds**: required_domain_match (0.6), anti_universality (0.9)

### 6. **@C - Contract Layer**
- **Formula**: `C_play = 0.4·c_scale + 0.35·c_sem + 0.25·c_fusion`
- **Purpose**: Contract compliance and specification adherence
- **Weights**: Scale (0.4), Semantic (0.35), Fusion (0.25)
- **Thresholds**: min_jaccard_similarity (0.3), strict_typing_required

### 7. **@u - Unit Layer**
- **Formula**: `U = geometric_mean(S, M, gated(I), gated(P)) × (1 - penalty)`
- **Purpose**: Document quality and completeness (PDT structure)
- **Weights**: Complex multi-component structure (see documentation)
- **Thresholds**: gate_threshold_I (0.5), anti_gaming (0.7)

### 8. **@m - Meta Layer**
- **Formula**: `m = 0.40·transparency + 0.35·governance + 0.25·cost_efficiency`
- **Purpose**: Governance maturity and process quality
- **Weights**: Transparency (0.40), Governance (0.35), Cost (0.25)
- **Thresholds**: required_governance_score (0.5), min_transparency (0.6)

---

## Usage

### Generating Certificates with Layer Metadata

```python
from certificate_generator import CertificateGenerator

generator = CertificateGenerator()

certificate = generator.generate_certificate(
    instance_id="exec-001",
    method_id="farfan_pipeline.core.executors.D1_Q1_Evaluator",
    node_id="node_001",
    context={"execution_id": "exec-001"},
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
)

# Access layer metadata
for layer_symbol, metadata in certificate.layer_metadata.items():
    print(f"{layer_symbol} - {metadata.name}")
    print(f"  Formula: {metadata.formula}")
    print(f"  Thresholds: {metadata.thresholds}")
```

### Analyzing Layer Metadata

```python
from certificate_validator import CertificateAnalyzer

analysis = CertificateAnalyzer.analyze_certificate(certificate)

# Layer metadata summary
metadata_summary = analysis["layer_metadata_summary"]
print(f"Layers documented: {metadata_summary['count']}")
print(f"Total formulas: {metadata_summary['total_formulas']}")
print(f"Total thresholds: {metadata_summary['total_thresholds']}")
```

---

## Certificate JSON Structure

Certificates now include the `layer_metadata` field in their JSON serialization:

```json
{
  "certificate_version": "1.0.0",
  "instance_id": "exec-001",
  "method_id": "farfan_pipeline.core.executors.D1_Q1_Evaluator",
  "intrinsic_score": 0.87,
  "layer_scores": {
    "@b": 0.92,
    "@chain": 0.88
  },
  "calibrated_score": 0.8845,
  "layer_metadata": {
    "@b": {
      "symbol": "@b",
      "name": "Base Theory Layer",
      "description": "Code quality and theoretical soundness",
      "formula": "b = 0.40·b_theory + 0.35·b_impl + 0.25·b_deploy",
      "weights": {
        "b_theory": 0.40,
        "b_impl": 0.35,
        "b_deploy": 0.25
      },
      "thresholds": {
        "min_score_SCORE_Q": 0.7,
        "required_coverage": 0.8
      }
    },
    "@chain": {
      "symbol": "@chain",
      "name": "Chain Layer",
      "description": "Method wiring and orchestration integrity",
      "formula": "chain = discrete({0.0, 0.3, 0.6, 0.8, 1.0})",
      "weights": { ... },
      "thresholds": { ... }
    }
  },
  "signature": "a1b2c3d4..."
}
```

---

## Security & Integrity

### Signature Protection
- Layer metadata is included in the HMAC signature computation
- Any tampering with formulas, weights, or thresholds invalidates the certificate
- Verification detects both data corruption and intentional modification

### Verification Process

```python
generator = CertificateGenerator()
is_valid = generator.verify_certificate(certificate)
# Returns False if layer_metadata has been tampered with
```

---

## Reproducibility Verification

Layer metadata enables complete reproducibility verification:

1. **Formula Verification**: Independent auditors can verify the exact computation formulas used
2. **Threshold Validation**: All threshold values are documented for validation checks
3. **Weight Transparency**: Component weights are fully specified and verifiable
4. **Self-Contained**: No external configuration files needed for verification

### Example Verification Workflow

```python
# 1. Load certificate (no external config needed)
cert = load_certificate_from_json("certificate.json")

# 2. Extract layer specifications
for layer_symbol, score in cert.layer_scores.items():
    metadata = cert.layer_metadata[layer_symbol]
    
    # 3. Verify formula, weights, and thresholds
    print(f"Layer {layer_symbol}:")
    print(f"  Score: {score}")
    print(f"  Formula: {metadata.formula}")
    print(f"  Thresholds: {metadata.thresholds}")
    
    # 4. Independent computation can now be performed
    # using the documented specifications
```

---

## Migration Notes

### Backward Compatibility
- Existing certificates without `layer_metadata` are supported via default empty dict
- The `load_certificate_from_json` function handles both old and new formats
- No breaking changes to existing certificate validation logic

### Updating Existing Code
```python
# Old code (still works)
cert = generator.generate_certificate(...)

# New code (with layer metadata)
cert = generator.generate_certificate(...)
for layer in cert.layer_metadata.values():
    print(f"Layer: {layer.name}, Formula: {layer.formula}")
```

---

## Testing

### Test Coverage
- `test_layer_metadata_integration.py`: Comprehensive test suite
- `certificate_examples/usage_example.py`: Example 5 demonstrates layer metadata
- All tests verify:
  - Metadata generation for all active layers
  - JSON serialization/deserialization
  - Signature protection
  - Reproducibility features

### Running Tests

```bash
# Run integration tests
python src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/test_layer_metadata_integration.py

# Run usage examples
python src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/certificate_examples/usage_example.py
```

---

## Benefits Summary

✓ **Enhanced Audit Trail**: Complete layer specification provenance in every certificate  
✓ **Self-Documentation**: Certificates are fully self-contained and interpretable  
✓ **Reproducibility**: Independent verification without external dependencies  
✓ **Transparency**: All formulas, weights, and thresholds explicitly documented  
✓ **Security**: Layer metadata protected by certificate signature  
✓ **Governance**: Full traceability for compliance and historical analysis  

---

## References

- **Certificate Generator**: `certificate_generator.py`
- **Certificate Validator**: `certificate_validator.py`
- **Layer Requirements**: `COHORT_2024_layer_requirements.json`
- **Layer Assignment**: `COHORT_2024_layer_assignment.py`
- **Usage Examples**: `certificate_examples/usage_example.py`
- **Test Suite**: `test_layer_metadata_integration.py`
