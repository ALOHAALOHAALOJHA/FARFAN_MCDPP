# Audit Trail System

Comprehensive audit trail system for calibration verification with cryptographic signatures, determinism validation, and structured logging.

## Overview

The audit trail system provides:
- **VerificationManifest**: Captures all calibration inputs, parameters, and results
- **HMAC Signatures**: Tamper detection using HMAC-SHA256
- **Score Reconstruction**: Verify computation determinism
- **Determinism Validation**: Check reproducibility (identical inputs → identical outputs)
- **Structured JSON Logging**: Time-series logs with rotation and compression
- **Operation Tracing**: Record mathematical operations with stack traces

## Architecture

```
audit_trail.py
├── VerificationManifest (dataclass)
│   ├── calibration_scores: {method_id: Cal(I), ...}
│   ├── parametrization: {config_hash, retry, timeout_s, temperature, thresholds}
│   ├── determinism_seeds: {random_seed, numpy_seed, seed_version}
│   ├── results: {micro_scores, dimension_scores, area_scores, macro_score}
│   ├── timestamp: ISO-8601 UTC
│   ├── validator_version: str
│   ├── signature: HMAC-SHA256 hex
│   └── trace: [OperationTrace, ...]
│
├── Functions
│   ├── generate_manifest() - Create signed manifest
│   ├── verify_manifest() - Verify HMAC signature
│   ├── reconstruct_score() - Replay computation
│   └── validate_determinism() - Check reproducibility
│
├── StructuredAuditLogger
│   ├── JSON logging with {timestamp, level, component, message, metadata}
│   ├── Daily rotation (midnight UTC)
│   └── 30-day retention with compression
│
└── TraceGenerator
    ├── Intercept math operations
    ├── Record {operation, inputs, output, stack_trace}
    └── Store in manifest.trace
```

## Usage

### 1. Generate Verification Manifest

```python
from src.cross_cutting_infrastrucuture.contractual.dura_lex.audit_trail import (
    generate_manifest
)

manifest = generate_manifest(
    calibration_scores={
        "FIN:BayesianNumericalAnalyzer.analyze_numeric_pattern@Q": 0.8004,
        "POL:BayesianEvidenceScorer.compute_bayesian_score@Q": 0.8567,
        "DER:BayesianMechanismInference.infer_mechanism@C": 0.7821,
    },
    config_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    retry=3,
    timeout_s=300.0,
    temperature=0.7,
    thresholds={
        "min_confidence": 0.7,
        "min_evidence": 0.6,
        "min_coherence": 0.65,
    },
    random_seed=123456,
    numpy_seed=789012,
    seed_version="sha256_v1",
    micro_scores=[0.75, 0.78, 0.82, 0.85, 0.88],
    dimension_scores={
        "DIM01": 0.82,
        "DIM02": 0.89,
        "DIM03": 0.76,
        "DIM04": 0.84,
        "DIM05": 0.78,
        "DIM06": 0.81,
    },
    area_scores={
        "PA01": 0.83,
        "PA02": 0.87,
        "PA03": 0.79,
        "PA04": 0.85,
    },
    macro_score=0.8166666666666667,
    validator_version="2.0.0",
    secret_key="your_hmac_secret_key",
)

# Save manifest
with open("verification_manifest.json", "w") as f:
    f.write(manifest.to_json())
```

### 2. Verify Manifest Signature

```python
from src.cross_cutting_infrastrucuture.contractual.dura_lex.audit_trail import (
    verify_manifest,
    VerificationManifest
)

# Load manifest
with open("verification_manifest.json") as f:
    data = json.load(f)
    manifest = VerificationManifest.from_dict(data)

# Verify signature
is_valid = verify_manifest(manifest, "your_hmac_secret_key")

if is_valid:
    print("✓ Manifest signature is valid - no tampering detected")
else:
    print("✗ Manifest signature is INVALID - possible tampering!")
```

### 3. Reconstruct Score

```python
from src.cross_cutting_infrastrucuture.contractual.dura_lex.audit_trail import (
    reconstruct_score
)

# Reconstruct macro score from dimension scores
reconstructed = reconstruct_score(manifest)
original = manifest.results.macro_score

if abs(reconstructed - original) < 1e-6:
    print(f"✓ Score reconstruction matches: {reconstructed}")
else:
    print(f"✗ Score mismatch! Original: {original}, Reconstructed: {reconstructed}")
```

### 4. Validate Determinism

```python
from src.cross_cutting_infrastrucuture.contractual.dura_lex.audit_trail import (
    validate_determinism
)

# Compare two manifests from runs with same seeds
is_deterministic = validate_determinism(manifest1, manifest2)

if is_deterministic:
    print("✓ Deterministic: Same inputs produced same outputs")
else:
    print("✗ Non-deterministic: Outputs differ despite same inputs")
```

### 5. Structured Logging

```python
from src.cross_cutting_infrastrucuture.contractual.dura_lex.audit_trail import (
    StructuredAuditLogger
)

logger = StructuredAuditLogger(log_dir="logs/calibration", component="calibration")

# Log events
logger.log("INFO", "Calibration started", {"phase": "initialization"})
logger.log("INFO", "Processing complete", {"phase": "execution", "score": 0.85})
logger.log("WARNING", "Low confidence", {"confidence": 0.62, "threshold": 0.7})

# Log manifest events
logger.log_manifest_generation(manifest, success=True)
logger.log_verification(manifest, verified=True)
logger.log_determinism_check(manifest1, manifest2, deterministic=True)
```

### 6. Operation Tracing

```python
from src.cross_cutting_infrastrucuture.contractual.dura_lex.audit_trail import (
    TraceGenerator
)

# Trace operations during calibration
with TraceGenerator(enabled=True) as tracer:
    # Your calibration code here
    result = compute_score(evidence=0.85, confidence=0.9)
    tracer.trace_operation("compute_score", {"evidence": 0.85, "confidence": 0.9}, result)
    
    aggregated = aggregate_dimensions([0.8, 0.9, 0.7])
    tracer.trace_operation("aggregate_dimensions", {"scores": [0.8, 0.9, 0.7]}, aggregated)
    
    # Get traces for manifest
    traces = tracer.get_traces()

# Include traces in manifest
manifest = generate_manifest(
    # ... other parameters ...
    trace=traces,
)
```

## Data Structures

### VerificationManifest

```python
@dataclass
class VerificationManifest:
    calibration_scores: dict[str, CalibrationScore]
    parametrization: ParametrizationConfig
    determinism_seeds: DeterminismSeeds
    results: ResultsBundle
    timestamp: str
    validator_version: str
    signature: str
    trace: list[OperationTrace]
```

### CalibrationScore

```python
@dataclass(frozen=True)
class CalibrationScore:
    method_id: str          # e.g., "FIN:BayesianNumericalAnalyzer.analyze_numeric_pattern@Q"
    score: float            # Cal(I) score
    confidence: float       # Confidence level
    timestamp: str          # ISO-8601 UTC
    metadata: dict[str, Any]
```

### ParametrizationConfig

```python
@dataclass(frozen=True)
class ParametrizationConfig:
    config_hash: str                    # SHA256 of configuration
    retry: int                          # Retry count
    timeout_s: float                    # Timeout in seconds
    temperature: float                  # Temperature parameter
    thresholds: dict[str, float]        # Threshold configuration
    additional_params: dict[str, Any]   # Extra parameters
```

### DeterminismSeeds

```python
@dataclass(frozen=True)
class DeterminismSeeds:
    random_seed: int            # Python random seed
    numpy_seed: int             # NumPy seed
    seed_version: str           # Seed algorithm version
    base_seed: int | None       # Base seed
    policy_unit_id: str | None  # Policy unit identifier
    correlation_id: str | None  # Correlation ID
```

### ResultsBundle

```python
@dataclass(frozen=True)
class ResultsBundle:
    micro_scores: list[float]           # Question-level scores
    dimension_scores: dict[str, float]  # DIM01-DIM06 scores
    area_scores: dict[str, float]       # PA01-PA10 scores
    macro_score: float                  # Overall score
    metadata: dict[str, Any]
```

### OperationTrace

```python
@dataclass(frozen=True)
class OperationTrace:
    operation: str              # Operation name
    inputs: dict[str, Any]      # Input values
    output: Any                 # Output value
    stack_trace: list[str]      # Code path
    timestamp: str              # ISO-8601 UTC
```

## Log Format

Structured JSON logs with the following schema:

```json
{
  "timestamp": "2024-12-09T12:00:00.000Z",
  "level": "INFO",
  "component": "calibration",
  "message": "Manifest generation completed",
  "metadata": {
    "validator_version": "2.0.0",
    "calibration_count": 3,
    "macro_score": 0.8166666666666667,
    "success": true
  }
}
```

## Log Files

Logs are stored in `logs/calibration/` with daily rotation:

```
logs/calibration/
├── audit_20241209.log         # General audit events
├── verification_20241209.log  # Verification events
├── determinism_20241209.log   # Determinism checks
└── audit_20241208.log.gz      # Compressed older logs
```

## Configuration

Logging configuration in `logging_config.json`:

```json
{
  "version": 1,
  "handlers": {
    "audit_file": {
      "class": "logging.handlers.TimedRotatingFileHandler",
      "filename": "logs/calibration/audit.log",
      "when": "midnight",
      "interval": 1,
      "backupCount": 30
    }
  }
}
```

## Security

### HMAC Secret Management

**DO NOT** commit HMAC secrets to version control!

Use environment variables:
```bash
export VERIFICATION_HMAC_SECRET="your_secure_secret_key"
```

Or load from secure configuration:
```python
import os
secret_key = os.environ.get("VERIFICATION_HMAC_SECRET")
if not secret_key:
    raise ValueError("VERIFICATION_HMAC_SECRET not set")
```

### Signature Algorithm

- **Algorithm**: HMAC-SHA256
- **Input**: Canonical JSON (sorted keys, no whitespace)
- **Output**: Hex-encoded signature (64 characters)
- **Verification**: Constant-time comparison (`hmac.compare_digest`)

## Examples

See `audit_trail_examples.py` for complete examples:

```bash
python src/cross_cutting_infrastrucuture/contractual/dura_lex/audit_trail_examples.py
```

See `trace_examples/` directory for example trace files:
- `example_traces.json` - Basic operation traces
- `calibration_trace_example.json` - Complete calibration run
- `determinism_trace_example.json` - Determinism validation

## Integration

### With Orchestrator

```python
from src.orchestration.orchestrator import Orchestrator
from src.cross_cutting_infrastrucuture.contractual.dura_lex.audit_trail import (
    generate_manifest,
    TraceGenerator,
    StructuredAuditLogger
)

class OrchestorWithAudit(Orchestrator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = StructuredAuditLogger(component="orchestrator")
        self.tracer = TraceGenerator(enabled=True)
    
    def execute(self):
        with self.tracer:
            results = super().execute()
            
            # Generate manifest
            manifest = generate_manifest(
                calibration_scores=self.get_calibration_scores(),
                # ... other parameters from execution ...
                trace=self.tracer.get_traces()
            )
            
            # Log and verify
            self.logger.log_manifest_generation(manifest, success=True)
            
            return results, manifest
```

### With Calibration Registry

```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.cohort_loader import CohortLoader
from src.cross_cutting_infrastrucuture.contractual.dura_lex.audit_trail import (
    CalibrationScore
)

def load_calibration_with_audit(method_id: str) -> CalibrationScore:
    loader = CohortLoader()
    cal_data = loader.load_calibration("intrinsic_calibration")
    
    return CalibrationScore(
        method_id=method_id,
        score=cal_data[method_id]["score"],
        confidence=cal_data[method_id]["confidence"],
        timestamp=datetime.now(timezone.utc).isoformat()
    )
```

## Testing

Run unit tests:
```bash
pytest tests/test_audit_trail.py -v
```

## Performance

- **Manifest generation**: ~1-5ms (excluding signature)
- **HMAC signature**: ~0.5-2ms (depends on manifest size)
- **Verification**: ~0.5-2ms
- **Log write**: ~0.1-1ms (async I/O)
- **Trace capture**: ~0.05-0.2ms per operation

## Limitations

- Manifest signature verifies structure but not semantic correctness
- Score reconstruction assumes simple mean aggregation
- Determinism validation requires exact floating-point matches
- Log rotation at midnight UTC (configurable)
- Trace depth limited to 5 stack frames (configurable)

## References

- HMAC: RFC 2104
- SHA-256: FIPS 180-4
- ISO-8601: Date and time format
- JSON: RFC 8259
