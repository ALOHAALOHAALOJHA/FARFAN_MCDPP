# Calibration Certificates Directory

This directory stores calibration certificates for F.A.R.F.A.N methods.

## Purpose

Certificates provide **official attestations** of method calibration quality, containing:
- Final calibration score
- Layer-by-layer breakdown
- Fusion computation details
- Cryptographic signature
- Validation status

## Certificate Format

Each certificate is a JSON document following this schema:

```json
{
  "certificate_id": "uuid-v4",
  "method_id": "farfan_pipeline.core.executors.D1Q1_Executor",
  "cohort": "COHORT_2024",
  "role": "SCORE_Q",
  "calibration_timestamp": "2024-12-10T12:34:56Z",
  "final_score": 0.856,
  "layer_scores": {
    "@b": 0.843,
    "@chain": 0.92,
    "@q": 0.88,
    "@d": 0.85,
    "@p": 0.85,
    "@C": 0.90,
    "@u": 0.75,
    "@m": 0.65
  },
  "fusion_breakdown": {
    "linear_contribution": 0.723,
    "interaction_contribution": 0.133,
    "total": 0.856
  },
  "signature": {
    "sha256": "abc123...",
    "authority": "COHORT_2024_calibration_orchestrator",
    "verifiable": true
  },
  "validation": {
    "bounds_check": "PASS",
    "monotonicity_check": "PASS",
    "constraint_satisfaction": "PASS"
  }
}
```

## Certificate Generation

Generate certificates using the certificate generator:

```python
from calibration.certificate_generator import CertificateGenerator

generator = CertificateGenerator(cohort="COHORT_2024")
cert = generator.generate_certificate(
    method_id="D1Q1_Executor",
    calibration_result=result
)
generator.save_certificate(cert, output_dir="artifacts/certificates/")
```

## Certificate Naming Convention

Certificates follow this naming pattern:

```
{method_id}_certificate.json
```

Examples:
- `D1Q1_Executor_certificate.json`
- `pattern_extractor_v2_certificate.json`
- `coherence_validator_certificate.json`

## Certificate Validation

Validate certificates using the certificate validator:

```python
from calibration.certificate_validator import CertificateValidator

validator = CertificateValidator()
result = validator.validate_certificate("D1Q1_Executor_certificate.json")

if result.is_valid:
    print(f"✅ Certificate valid")
else:
    print(f"❌ Certificate invalid: {result.errors}")
```

## Expected Certificates

### Critical Executors (30 total)

All D1Q1-D6Q5 executors should have certificates:

```
D1Q1_Executor_certificate.json
D1Q2_Executor_certificate.json
D1Q3_Executor_certificate.json
D1Q4_Executor_certificate.json
D1Q5_Executor_certificate.json
...
D6Q1_Executor_certificate.json
D6Q2_Executor_certificate.json
D6Q3_Executor_certificate.json
D6Q4_Executor_certificate.json
D6Q5_Executor_certificate.json
```

### Core Utilities

Key utility methods should also have certificates:
- `pattern_extractor_v2_certificate.json`
- `coherence_validator_certificate.json`
- `semantic_analyzer_certificate.json`

## Gap Status

⚠️  **Current Status**: Certificate generator exists but certificates not yet generated

**Next Steps** (from CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md GAP-3):
1. Run certificate generation for all 30 D1Q1-D6Q5 executors
2. Generate certificates for critical utility methods
3. Create certificate index: `INDEX.json`
4. Implement certificate validation in CI pipeline

## References

- Gap analysis: `docs/CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md` (Section 5.1 GAP-3)
- Certificate generator: `src/.../calibration/certificate_generator.py`
- Certificate validator: `src/.../calibration/certificate_validator.py`
