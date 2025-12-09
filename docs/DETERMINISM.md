# F.A.R.F.A.N Determinism - SIN_CARRETA Doctrine

**Absolute Separation of Calibration and Parametrization**

Version: 1.0.0  
Last Updated: 2024-12-16

---

## Table of Contents

1. [Overview](#overview)
2. [The SIN_CARRETA Doctrine](#the-sin_carreta-doctrine)
3. [Calibration vs. Parametrization](#calibration-vs-parametrization)
4. [Deterministic Execution](#deterministic-execution)
5. [Hashing and Integrity](#hashing-and-integrity)
6. [HMAC Signatures](#hmac-signatures)
7. [Reproducibility Guarantees](#reproducibility-guarantees)
8. [Implementation Details](#implementation-details)

---

## Overview

F.A.R.F.A.N implements **deterministic execution** with complete reproducibility guarantees. The same inputs always produce identical outputs, bit-for-bit. This is achieved through the **SIN_CARRETA doctrine** (Sistema de Integridad No-Compensable para Análisis de Reproducibilidad, Rastreabilidad y Trazabilidad Absoluta).

### Core Principles

1. **Absolute Separation**: Calibration data is immutable; execution parameters are traceable
2. **Content Addressing**: All inputs are SHA-256 hashed
3. **Deterministic RNG**: All stochastic operations use reproducible seeds
4. **UTC-Only Timestamps**: No timezone ambiguity
5. **Verification Manifests**: HMAC-SHA256 signatures prove integrity
6. **Zero Tolerance**: ANY deviation aborts execution

---

## The SIN_CARRETA Doctrine

### Doctrine Statement

> "Calibration defines WHAT the system is. Parametrization defines HOW the system runs. These must remain absolutely separate, with calibration immutable and parametrization traceable."

### Analogy: Engine vs. Rev Limit

**Calibration** (WHAT):
- Engine specifications (displacement, compression ratio, fuel type)
- Quality certificate (@b, @u, @q, etc.)
- Tested on a dynamometer
- **Immutable**: Changing compression ratio means building a new engine

**Parametrization** (HOW):
- Rev limit (max RPM)
- Fuel mixture richness
- Ignition timing advance
- **Mutable**: Can adjust rev limit without rebuilding engine

**Linkage**:
- Set rev limit too low (timeout_s=5) → engine stalls → **cost penalty** in @m (meta layer)
- Quality certificate does not change the rev limit itself
- Certificate may note "this engine requires ≥30s to reach optimal performance"

### In F.A.R.F.A.N

**Calibration** (WHAT it is):
```json
{
  "method_id": "D6_Q5_TheoryOfChange",
  "b_theory": 0.88,
  "b_impl": 0.91,
  "b_deploy": 0.85,
  "statistical_paradigm": "bayesian_inference",
  "min_data_points": 50,
  "theoretical_foundation": "Falleti & Lynch (2009) causal mechanisms"
}
```

**Parametrization** (HOW it runs):
```json
{
  "executor_id": "D6_Q5_TheoryOfChange",
  "timeout_s": 60,
  "max_memory_mb": 2048,
  "chunk_batch_size": 32,
  "seed_base": 42,
  "enable_logging": true
}
```

**Separation Enforcement**:
- Calibration files are content-addressed: `intrinsic_calibration.json` → SHA-256 hash
- Any change to calibration requires cohort migration (COHORT_2024 → COHORT_2025)
- Parametrization can vary per execution without invalidating calibration
- Verification manifest tracks both hashes separately

---

## Calibration vs. Parametrization

### Calibration (Immutable)

**What it includes**:
- Method quality scores (b_theory, b_impl, b_deploy)
- Layer weights for Choquet fusion
- Interaction term coefficients
- Question priorities
- Method-question mappings
- PDT structure requirements (S/M/I/P thresholds)

**Where it's stored**:
```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/
├── COHORT_2024_intrinsic_calibration_loader.json
├── COHORT_2024_fusion_weights.json
├── COHORT_2024_unit_layer.json
├── COHORT_2024_layer_coexistence.json
└── COHORT_2024_congruence_layer.json
```

**Change policy**:
- Requires cohort migration (major version bump)
- Validation on new data (≥50 PDTs)
- Governance approval
- SHA-256 hashes recorded in COHORT_MANIFEST.json

**Rationale**: Calibration defines the "ground truth" of method quality. Changing it mid-execution would be like changing the definition of a meter during a measurement — it invalidates comparability.

---

### Parametrization (Traceable)

**What it includes**:
- Execution timeouts (timeout_s)
- Memory limits (max_memory_mb)
- Batch sizes (chunk_batch_size)
- Random seeds (seed_base)
- Logging levels (enable_logging)
- Concurrency settings (max_workers)

**Where it's stored**:
```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/parametrization/
├── COHORT_2024_executor_config.json
└── COHORT_2024_executor_profiler.json
```

**Change policy**:
- Can vary per execution
- Must be recorded in verification manifest
- Different parameters may affect performance but not method quality scores
- Timeout violations penalize @m (governance/cost layer) but don't change @b

**Rationale**: Parametrization controls execution environment. A faster machine can use larger batch sizes; a slower one needs more time. This doesn't change what the method is, only how it runs.

---

## Deterministic Execution

### Seed Registry

All stochastic operations derive seeds from a master seed using SHA-256:

```python
def get_derived_seed(base_seed: int, operation_name: str) -> int:
    """
    Generate deterministic seed for specific operation.
    
    Args:
        base_seed: Master seed (from seed_registry)
        operation_name: Unique operation identifier
    
    Returns:
        Deterministic seed for this operation
    """
    hash_input = f"{base_seed}:{operation_name}".encode('utf-8')
    hash_digest = hashlib.sha256(hash_input).digest()
    return int.from_bytes(hash_digest[:4], byteorder='big')
```

**Usage**:
```python
# Phase 0: Initialize seed registry
seed_registry = {
    "phase0_validation": get_derived_seed(42, "phase0"),
    "phase1_chunking": get_derived_seed(42, "phase1_semantic_chunking"),
    "phase2_executor_D1Q1": get_derived_seed(42, "phase2_D1_Q1"),
    # ... 30 executors
    "phase3_layer_scoring": get_derived_seed(42, "phase3_scoring"),
}

# Phase 2: Executor uses its assigned seed
random.seed(seed_registry["phase2_executor_D1Q1"])
np.random.seed(seed_registry["phase2_executor_D1Q1"])

# All stochastic operations now deterministic
embedding = model.encode(text)  # Reproducible
sample = np.random.choice(candidates, size=10)  # Reproducible
```

### Scoped Seed Management

Seeds are automatically restored after scoped operations:

```python
from src.cross_cutting_infrastrucuture.contractual.dura_lex.deterministic_execution import DeterministicSeedManager

manager = DeterministicSeedManager(base_seed=42)

with manager.scoped_seed("operation1"):
    # All random operations use operation1's seed
    value1 = random.random()

with manager.scoped_seed("operation2"):
    # Different seed, deterministically derived
    value2 = random.random()

with manager.scoped_seed("operation1"):
    # Same seed as first operation1 scope
    value3 = random.random()

assert value1 == value3  # Reproducible
```

---

## Hashing and Integrity

### SHA-256 File Hashing

All inputs are hashed at Phase 0:

```python
import hashlib

def compute_file_hash(file_path: str) -> str:
    """
    Compute SHA-256 hash of file.
    
    Args:
        file_path: Path to file
    
    Returns:
        Hex-encoded SHA-256 hash
    """
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(65536):  # 64KB chunks
            hasher.update(chunk)
    return hasher.hexdigest()

# Phase 0 boot checks
input_hash = compute_file_hash("data/pdt_municipality_X.pdf")
questionnaire_hash = compute_file_hash("config/questionnaire_monolith.json")
calibration_hash = compute_file_hash("calibration/COHORT_2024_intrinsic.json")

# Store in verification manifest
manifest["input_artifacts"]["pdt_document"] = {
    "path": "data/pdt_municipality_X.pdf",
    "hash": input_hash,
    "hash_algorithm": "sha256",
}
```

### Content Addressing

Configuration files are referenced by hash:

```python
# Instead of:
config = load_config("calibration.json")  # Which version?

# Use:
config = load_config_by_hash("sha256:a1b2c3d4...")  # Unambiguous
```

**Benefits**:
- Prevents accidental configuration changes
- Enables cache invalidation (hash mismatch → recompute)
- Supports distributed execution (hash verification)
- Audit trail (which exact config was used?)

---

## HMAC Signatures

### Verification Manifest Signing

The final verification manifest is signed with HMAC-SHA256:

```python
import hmac
import hashlib
import json

def sign_manifest(manifest: dict, secret_key: str) -> str:
    """
    Generate HMAC-SHA256 signature for manifest.
    
    Args:
        manifest: Verification manifest dictionary
        secret_key: Secret key for HMAC
    
    Returns:
        Hex-encoded HMAC signature
    """
    # Canonical JSON (sorted keys, no whitespace)
    canonical = json.dumps(manifest, sort_keys=True, separators=(',', ':'))
    
    # HMAC-SHA256
    signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=canonical.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return signature

# Generate signature
manifest = {
    "version": "1.0",
    "timestamp_utc": "2024-12-16T10:30:00Z",
    "execution_hash": "abc123...",
    "calibration_hash": "def456...",
    "phases_completed": 11,
    # ... all execution metadata
}

signature = sign_manifest(manifest, secret_key="PRODUCTION_KEY")

# Verification
def verify_manifest(manifest: dict, signature: str, secret_key: str) -> bool:
    """Verify manifest signature."""
    expected_signature = sign_manifest(manifest, secret_key)
    return hmac.compare_digest(expected_signature, signature)

# Later: verify integrity
is_valid = verify_manifest(manifest, signature, "PRODUCTION_KEY")
if not is_valid:
    raise IntegrityError("Manifest signature invalid - possible tampering")
```

### Signature Use Cases

1. **Tamper Detection**: Any modification to manifest invalidates signature
2. **Authenticity**: Proves manifest was generated by authorized system
3. **Non-Repudiation**: Producer cannot deny generating this specific output
4. **Chain of Custody**: Signature proves manifest wasn't altered in transit

---

## Reproducibility Guarantees

### Theorem: Deterministic Execution Invariant

**Statement**: Given identical inputs and configuration, F.A.R.F.A.N produces bit-identical outputs.

**Formally**:
```
∀ inputs I, config C, seed S:
  execute(I, C, S) = execute(I, C, S)
```

**Proof Sketch**:

1. **Input Determinism**: All inputs are hashed (SHA-256)
   - Same file → same hash → same parsed content

2. **Seed Determinism**: All RNG operations use derived seeds
   - Same base seed → same derived seeds → same random sequences

3. **Execution Determinism**: All operations are deterministic given inputs and seeds
   - No system time dependencies (UTC only)
   - No network dependencies (offline execution)
   - No filesystem race conditions (single-threaded critical sections)

4. **Output Determinism**: All outputs are deterministically computed
   - No floating-point non-determinism (fixed NumPy/PyTorch settings)
   - No hash table iteration order (sorted keys everywhere)
   - No timestamp ambiguity (UTC ISO-8601 only)

Therefore: `execute(I, C, S) = execute(I, C, S)` ✓

---

### Reproducibility Levels

**Level 1: Same Machine, Same Run**
- Trivially reproducible (sanity check)

**Level 2: Same Machine, Different Time**
- Tests seed management
- Tests timestamp isolation
- **F.A.R.F.A.N guarantee**: ✓ Reproducible

**Level 3: Different Machine, Same OS**
- Tests floating-point determinism
- Tests library version dependencies
- **F.A.R.F.A.N guarantee**: ✓ Reproducible (with pinned dependencies)

**Level 4: Different OS**
- Tests cross-platform determinism
- May have minor floating-point differences (< 1e-10)
- **F.A.R.F.A.N guarantee**: ⚠ Reproducible within tolerance

**Level 5: Different Python Version**
- Major version changes may break determinism
- Minor version changes should be safe
- **F.A.R.F.A.N guarantee**: ❌ Not guaranteed (requires cohort migration)

---

## Implementation Details

### Phase 0 Determinism Checklist

```python
def phase0_determinism_checks() -> bool:
    """
    Verify determinism prerequisites before execution.
    
    Returns:
        True if all checks pass
    
    Raises:
        DeterminismError: If any check fails
    """
    checks = []
    
    # 1. PYTHONHASHSEED is set
    import os
    pythonhashseed = os.environ.get('PYTHONHASHSEED')
    if pythonhashseed != '0':
        checks.append(f"PYTHONHASHSEED not set to 0 (got {pythonhashseed})")
    
    # 2. NumPy deterministic mode
    import numpy as np
    np_seed = np.random.get_state()[1][0]
    if np_seed == 0:  # Unseeded
        checks.append("NumPy random state not initialized")
    
    # 3. No CUDA non-determinism (if GPU available)
    try:
        import torch
        if torch.cuda.is_available():
            if not torch.backends.cudnn.deterministic:
                checks.append("PyTorch CUDNN deterministic mode not enabled")
    except ImportError:
        pass  # PyTorch not available
    
    # 4. UTC timezone
    from datetime import datetime, timezone
    now = datetime.now()
    if now.tzinfo is None:
        checks.append("Datetime is not timezone-aware")
    
    # 5. Config files exist and are hashed
    config_files = [
        "calibration/COHORT_2024_intrinsic.json",
        "config/questionnaire_monolith.json",
    ]
    for config_file in config_files:
        if not os.path.exists(config_file):
            checks.append(f"Config file missing: {config_file}")
    
    if checks:
        raise DeterminismError(f"Determinism checks failed:\n" + "\n".join(f"  - {c}" for c in checks))
    
    return True
```

### Environment Setup

**Required environment variables**:
```bash
export PYTHONHASHSEED=0  # Deterministic hash() function
export CUDA_VISIBLE_DEVICES=-1  # Disable GPU (for full determinism)
export OMP_NUM_THREADS=1  # Single-threaded NumPy
export MKL_NUM_THREADS=1  # Single-threaded Intel MKL
```

**Python setup**:
```python
import random
import numpy as np

# Set all seeds
random.seed(42)
np.random.seed(42)

# Disable non-deterministic operations
import torch
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

---

### Floating-Point Determinism

**Challenge**: Floating-point operations may have different rounding on different hardware.

**Solution**: Use consistent computation order and avoid parallelism in critical paths.

```python
# BAD: Non-deterministic parallel reduction
results = Parallel(n_jobs=-1)(
    delayed(compute)(x) for x in data
)
total = sum(results)  # Order-dependent due to parallelism

# GOOD: Deterministic sequential reduction
results = [compute(x) for x in data]
total = sum(sorted(results))  # Sorted to ensure order
```

---

### Timestamp Determinism

**Rule**: All timestamps must be UTC, ISO-8601 format.

```python
from datetime import datetime, timezone

# BAD: Local timezone (ambiguous)
timestamp = datetime.now().isoformat()  # 2024-12-16T10:30:00

# GOOD: UTC explicit
timestamp = datetime.now(timezone.utc).isoformat()  # 2024-12-16T10:30:00+00:00
```

**Verification**:
```python
def validate_utc_timestamp(ts: str) -> bool:
    """Validate timestamp is UTC."""
    if not ts.endswith('Z') and not ts.endswith('+00:00'):
        raise ValueError(f"Timestamp must be UTC: {ts}")
    return True
```

---

## Verification Manifest Example

```json
{
  "version": "1.0",
  "timestamp_utc": "2024-12-16T10:30:00+00:00",
  "execution_metadata": {
    "base_seed": 42,
    "python_version": "3.12.0",
    "numpy_version": "1.26.0",
    "system": "Linux-6.2.0-x86_64"
  },
  "input_artifacts": {
    "pdt_document": {
      "path": "data/pdt_municipality_X.pdf",
      "hash": "sha256:a1b2c3d4e5f6...",
      "size_bytes": 2048576
    },
    "questionnaire": {
      "path": "config/questionnaire_monolith.json",
      "hash": "sha256:1a2b3c4d5e6f...",
      "size_bytes": 153600
    }
  },
  "calibration_artifacts": {
    "intrinsic_calibration": {
      "path": "calibration/COHORT_2024_intrinsic.json",
      "hash": "sha256:fedcba987654...",
      "cohort": "COHORT_2024"
    },
    "fusion_weights": {
      "path": "calibration/COHORT_2024_fusion_weights.json",
      "hash": "sha256:123abc456def...",
      "cohort": "COHORT_2024"
    }
  },
  "execution_trace": {
    "phases_completed": 11,
    "phases_failed": 0,
    "total_duration_s": 127.34,
    "seed_registry": {
      "phase0": 2891336453,
      "phase1_chunking": 3456789012,
      "phase2_D1_Q1": 1234567890
    }
  },
  "output_artifacts": {
    "micro_report": {
      "path": "output/micro_report.json",
      "hash": "sha256:999aaa888bbb...",
      "size_bytes": 524288
    },
    "verification_certificate": {
      "path": "output/certificate.json",
      "hash": "sha256:777ccc666ddd..."
    }
  },
  "integrity": {
    "algorithm": "hmac-sha256",
    "signature": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "signed_at_utc": "2024-12-16T10:32:15+00:00"
  }
}
```

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture overview
- [VALIDATION_GUIDE.md](./VALIDATION_GUIDE.md) - How to validate determinism
- [CONFIG_REFERENCE.md](./CONFIG_REFERENCE.md) - Configuration file schemas

---

**Last Updated**: 2024-12-16  
**Version**: 1.0.0  
**Maintainers**: Policy Analytics Research Unit
