# Configuration Hash Determinism and Runtime Mode Behavior

## Overview

This document describes the hardening of configuration hash computation and runtime mode enforcement in the F.A.R.F.A.N pipeline.

## Problem Statement

The pipeline previously lacked:
1. **Guaranteed deterministic hashing** of questionnaire monoliths
2. **Enforced runtime mode behaviors** (PROD/DEV/EXPLORATORY)
3. **Clear verification status** in output artifacts
4. **Test coverage** for hash stability and mode enforcement

## Solution

### 1. Hash Determinism (Issue #[P1])

#### Implemented Guarantees

The `_normalize_monolith_for_hash()` function now guarantees:

1. **MappingProxyType normalization**: All proxy types converted to standard dicts
2. **Recursive normalization**: All nested structures converted to canonical forms
3. **JSON serialization verification**: Fails fast on non-serializable content
4. **Sort-key ordering**: `json.dumps(sort_keys=True)` ensures dict order independence
5. **UTF-8 encoding**: Consistent Unicode handling across platforms

#### Hash Computation Contract

```python
monolith_sha256 = hashlib.sha256(
    json.dumps(
        normalized_monolith,
        sort_keys=True,           # Key order independence
        ensure_ascii=False,       # Preserve Unicode
        separators=(",", ":")     # Minimal whitespace
    ).encode("utf-8")
).hexdigest()
```

**INVARIANT**: Same logical monolith → Same hash across all runs/hosts/platforms

#### Test Coverage

- **Unit tests** (9 tests): Verify hash determinism with permutations, nested structures, Unicode, MappingProxyType
- **Integration tests** (2 tests): Verify orchestrator hash computation stability
- **Regression tests** (3 tests): Prevent hash algorithm changes

### 2. Runtime Mode Enforcement

#### Mode Behaviors

| Mode | Verification Status | Partial Results | Fail Fast | Logging Level |
|------|-------------------|-----------------|-----------|---------------|
| **PROD** | `verified` | ❌ Forbidden | ✅ Enabled | INFO |
| **DEV** | `development` | ✅ Allowed | ⚠️ Warn | WARNING |
| **EXPLORATORY** | `experimental` | ✅ Allowed | ❌ Disabled | DEBUG (verbose) |

#### Configuration Dictionary Extensions

Phase 0 `_load_configuration()` now returns:

```python
{
    "monolith_sha256": str,              # Deterministic hash
    "_runtime_mode": "prod"|"dev"|"exploratory",
    "_strict_mode": bool,                 # True if PROD + no fallbacks
    "_verification_status": "verified"|"development"|"experimental",
    "_allow_partial_results": bool,       # False only in PROD
    # ... existing fields ...
}
```

#### PROD Mode Enforcement

In PROD mode with question count mismatch:
```python
if runtime_mode == PROD and not allow_aggregation_defaults:
    raise RuntimeError("Question count mismatch in PROD mode")
```

#### Test Coverage

- **Runtime mode tests** (9 tests): Verify mode parsing, illegal combinations, flag enforcement
- **Integration tests** (10 tests): Verify orchestrator mode behaviors

### 3. strict_calibration Property

**Bug Fix**: Added missing `strict_calibration` property to `RuntimeConfig`

```python
@property
def strict_calibration(self) -> bool:
    """
    Returns True if strict calibration is required.
    PROD mode without ALLOW_MISSING_BASE_WEIGHTS.
    """
    return self.mode == RuntimeMode.PROD and not self.allow_missing_base_weights
```

This property was referenced in `__repr__()` and `boot_checks.py` but was not defined.

## Files Modified

1. **src/farfan_pipeline/phases/Phase_zero/runtime_config.py**
   - Added `strict_calibration` property
   - No other changes (existing functionality preserved)

2. **src/farfan_pipeline/orchestration/orchestrator.py**
   - Enhanced `_normalize_monolith_for_hash()` documentation
   - Enhanced `_load_configuration()` with mode-specific behaviors
   - Added verification status and allow_partial_results flags

## Files Added

1. **tests/test_configuration_hash_determinism.py** (21 tests)
   - Hash determinism unit tests
   - Runtime mode behavior tests
   - Regression prevention tests

2. **tests/test_orchestrator_mode_integration.py** (12 tests)
   - Orchestrator integration tests
   - Hash computation integration tests

## Test Results

All 56 tests pass (23 existing + 33 new):
- ✅ test_phase0_runtime_config.py: 23 passed
- ✅ test_configuration_hash_determinism.py: 21 passed
- ✅ test_orchestrator_mode_integration.py: 12 passed

## Backward Compatibility

All changes are **backward compatible**:
- Existing code continues to work unchanged
- New fields in config_dict are optional (prefixed with `_`)
- Default runtime mode remains PROD
- Hash computation produces identical results for existing monoliths

## Usage Examples

### Setting Runtime Mode

```bash
# Production (default)
export SAAAAAA_RUNTIME_MODE=prod

# Development
export SAAAAAA_RUNTIME_MODE=dev
export ALLOW_AGGREGATION_DEFAULTS=true

# Exploratory
export SAAAAAA_RUNTIME_MODE=exploratory
```

### Checking Verification Status

```python
config = orchestrator._load_configuration()
verification_status = config.get("_verification_status", "unknown")

if verification_status == "verified":
    # PROD mode output - safe for production use
    pass
elif verification_status == "development":
    # DEV mode output - for testing only
    pass
else:
    # EXPLORATORY mode output - experimental
    pass
```

### Verifying Hash Determinism

```python
# Hash should be identical across runs
config1 = orchestrator._load_configuration()
config2 = orchestrator._load_configuration()

assert config1["monolith_sha256"] == config2["monolith_sha256"]
```

## Future Work

1. **Manifest Integration**: Add `_verification_status` to CI manifest
2. **Dashboard Integration**: Display runtime mode in dashboard
3. **Audit Trail**: Log mode switches and verification status changes
4. **Performance**: Consider caching normalized monolith for repeated hash computations

## References

- Issue: [P1] HARDEN: Configuration Hash Determinism and RuntimeMode Behavior
- Related: Phase 0 runtime configuration system
- Related: Orchestrator configuration loading
