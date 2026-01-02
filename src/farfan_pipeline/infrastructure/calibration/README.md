# Calibration Layer Architecture Documentation

## Overview

This document describes the calibration layer infrastructure implemented as part of JOB FRONT 1 (JF1-CAL-ARCH-2026-01-02).

## Purpose

The calibration layer provides foundational types and data structures for calibration within the F.A.R.F.A.N epistemic regime. It operates **within** the existing epistemic framework, not parallel to it.

## Architecture

### Module Structure

```
src/farfan_pipeline/infrastructure/calibration/
├── __init__.py                  # Public API (Facade pattern)
├── calibration_core.py          # Core types and dataclasses
└── type_defaults.py             # Type-specific calibration defaults

tests/calibration/
├── test_calibration_core_adversarial.py     # Core invariant tests
├── test_calibration_integration.py          # Integration workflows
└── test_type_defaults_adversarial.py        # Type defaults tests
```

### Core Types

#### CalibrationPhase (Enum)
Defines the phase in which calibration applies:
- `INGESTION` - Data ingestion phase
- `PHASE_2_COMPUTATION` - Phase 2 computation

#### CalibrationBounds (frozen dataclass)
Immutable bounds for a calibration parameter:
- `min_value: float` - Minimum allowed value
- `max_value: float` - Maximum allowed value
- `default_value: float` - Default value (must be within bounds)
- `unit: str` - Unit of measurement

**Validation:** `__post_init__` enforces default ∈ [min, max]

#### CalibrationParameter (frozen dataclass)
Single calibration parameter with full provenance:
- `name: str` - Parameter name
- `value: float` - Parameter value
- `bounds: CalibrationBounds` - Value bounds
- `rationale: str` - Justification (non-empty)
- `source_evidence: str` - Source file path (must start with `src/` or `artifacts/`)
- `calibration_date: datetime` - When parameter was calibrated
- `validity_days: int` - How long parameter is valid

**Methods:**
- `is_valid_at(check_date: datetime) -> bool` - Check if parameter is still valid
- `content_hash() -> str` - SHA-256 hash for integrity verification

**Validation:** 
- Value must be within bounds
- Rationale cannot be empty
- Source evidence must reference repo paths

#### CalibrationLayer (frozen dataclass)
Complete calibration configuration for a contract:
- `unit_of_analysis_id: str` - Municipality or entity ID
- `phase: CalibrationPhase` - Which phase this applies to
- `contract_type_code: str` - TYPE_A, TYPE_B, etc.
- `prior_strength: CalibrationParameter`
- `veto_threshold: CalibrationParameter`
- `chunk_size: CalibrationParameter`
- `extraction_coverage_target: CalibrationParameter`
- `created_at: datetime` - When layer was created
- `schema_version: str` - Schema version (1.0.0)

**Methods:**
- `manifest_hash() -> str` - SHA-256 hash of entire layer

### Type-Specific Defaults

The `type_defaults.py` module provides type-specific calibration defaults derived from `artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json`.

#### get_type_defaults(contract_type_code: str) -> dict[str, CalibrationBounds]

Loads calibration defaults for a contract type. Uses **flyweight pattern** with LRU cache.

Returns dictionary with keys:
- `n1_ratio` - N1 (empirical) layer ratio bounds
- `n2_ratio` - N2 (inferential) layer ratio bounds
- `n3_ratio` - N3 (audit) layer ratio bounds
- `veto_threshold` - Veto threshold bounds
- `prior_strength` - Prior strength bounds

**Type-Specific Behavior:**
- **TYPE_A (Semantic)**: Balanced ratios, N2 dominates
- **TYPE_B (Bayesian)**: Stronger priors (2.0 vs 1.0)
- **TYPE_C (Causal)**: Strong N3 for graph validation
- **TYPE_D (Financial)**: Most lenient veto (0.10 max)
- **TYPE_E (Logical)**: Strictest veto (0.01 min), NO averaging

#### Prohibited Operations

```python
PROHIBITED_OPERATIONS: dict[str, frozenset[str]] = {
    "TYPE_A": frozenset({"weighted_mean", "concat_only"}),
    "TYPE_B": frozenset({"weighted_mean", "simple_concat"}),
    "TYPE_C": frozenset({"concat_only", "weighted_mean"}),
    "TYPE_D": frozenset({"concat_only", "simple_concat"}),
    "TYPE_E": frozenset({"weighted_mean", "average", "mean", "avg"}),
}
```

**CRITICAL:** TYPE_E prohibits ALL forms of averaging because it uses AND logic (minimum confidence, not averaging).

#### is_operation_prohibited(contract_type_code: str, operation: str) -> bool

Checks if an operation is prohibited for a contract type. Case-insensitive and checks substrings.

## Design Patterns

### 1. Flyweight Pattern
Type defaults are cached via `@lru_cache(maxsize=5)` to prevent redundant file I/O and object creation.

### 2. Facade Pattern
`__init__.py` provides a single entry point that hides internal complexity:
```python
from .calibration_core import (
    CalibrationBounds,
    CalibrationLayer,
    CalibrationParameter,
    CalibrationPhase,
)
from .type_defaults import (
    PROHIBITED_OPERATIONS,
    get_type_defaults,
    is_operation_prohibited,
)
```

### 3. Immutability
All dataclasses use `frozen=True` and `slots=True` for:
- Thread safety
- Prevention of accidental modification
- Memory efficiency
- Hash consistency

### 4. Provenance Tracking
Every `CalibrationParameter` requires:
- `rationale` - Why this value was chosen
- `source_evidence` - Where this came from
- `calibration_date` - When it was established
- `validity_days` - How long it's valid

### 5. Integrity Verification
SHA-256 hashing ensures calibration layers haven't been tampered with:
```python
hash1 = layer.manifest_hash()
# ... later ...
hash2 = layer.manifest_hash()
assert hash1 == hash2  # Deterministic
```

## Usage Examples

### Basic Usage

```python
from datetime import datetime, timezone
from src.farfan_pipeline.infrastructure.calibration import (
    CalibrationLayer,
    CalibrationParameter,
    CalibrationPhase,
    get_type_defaults,
    is_operation_prohibited,
)

# Load type-specific defaults
defaults = get_type_defaults("TYPE_A")

# Create a parameter
now = datetime.now(timezone.utc)
prior_strength = CalibrationParameter(
    name="prior_strength",
    value=defaults["prior_strength"].default_value,
    bounds=defaults["prior_strength"],
    rationale="Default prior for TYPE_A",
    source_evidence="artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json",
    calibration_date=now,
    validity_days=90,
)

# Create a calibration layer
layer = CalibrationLayer(
    unit_of_analysis_id="MUNI_11001",
    phase=CalibrationPhase.PHASE_2_COMPUTATION,
    contract_type_code="TYPE_A",
    prior_strength=prior_strength,
    veto_threshold=veto_threshold,
    chunk_size=chunk_size,
    extraction_coverage_target=extraction_coverage,
)

# Verify integrity
hash_value = layer.manifest_hash()
print(f"Layer hash: {hash_value}")

# Check prohibited operations
if is_operation_prohibited("TYPE_E", "weighted_mean"):
    raise RuntimeError("Cannot use weighted_mean with TYPE_E!")
```

### Type-Specific Validation

```python
# TYPE_E: Logical Consistency - strictest constraints
defaults_e = get_type_defaults("TYPE_E")
assert defaults_e["veto_threshold"].min_value == 0.01

# Verify no averaging is allowed
prohibited_ops = ["weighted_mean", "average", "mean", "avg"]
for op in prohibited_ops:
    assert is_operation_prohibited("TYPE_E", op)
```

## Invariants Enforced

### INV-CAL-FREEZE-001: Immutability
All calibration parameters are immutable post-construction. Enforced via `frozen=True`.

### INV-CAL-REGIME-001: Epistemic Regime Compliance
Calibration operates within the existing epistemic regime (N1-EMP, N2-INF, N3-AUD), not parallel to it.

### INV-CAL-AUDIT-001: Auditability
All parameters subject to N3-AUD verification. Full provenance tracked.

### INV-CAL-BOUNDS-001: Bounds Validation
All parameter values must be within their defined bounds. Validated in `__post_init__`.

### INV-CAL-PROVENANCE-001: Provenance Requirements
- Rationale cannot be empty
- Source evidence must reference repo paths (`src/` or `artifacts/`)

### INV-CAL-VALIDITY-001: Validity Window
Parameters have expiration dates. Check via `is_valid_at()`.

## Test Coverage

### Test Statistics
- **Total Tests:** 28
- **Core Adversarial:** 9 tests
- **Type Defaults:** 14 tests
- **Integration:** 5 tests
- **Pass Rate:** 100%

### Adversarial Test Philosophy
Tests are designed to **break** the implementation, not confirm it works:
- Attempt to create invalid bounds
- Try to violate immutability
- Test expired parameters
- Verify hash determinism
- Ensure prohibited operations are blocked

## Type Checking

All code passes `mypy --strict` with 0 errors:
```bash
mypy --strict src/farfan_pipeline/infrastructure/calibration/
# Success: no issues found in 3 source files
```

## Performance Characteristics

- **Type Defaults Loading:** O(1) after first load (LRU cache)
- **Parameter Validation:** O(1) at construction time
- **Hash Computation:** O(n) where n = number of parameters
- **Prohibited Operation Check:** O(k) where k = number of prohibited ops for type

## Future Extensions

This implementation is complete for JOB FRONT 1 but designed for extension:

### JF2: Calibration Integration
- Integrate calibration layer with executor contracts
- Apply calibration during Phase 2 computation

### JF3: Runtime Enforcement
- Add runtime checks for prohibited operations
- Integrate with Phase 2 executor factory

### JF4: Calibration Persistence
- Serialize/deserialize calibration layers
- Version control for calibration parameters

### JF5: Calibration Audit Trail
- Track all calibration changes
- Generate audit reports

### JF6: Calibration Optimization
- Auto-tune parameters based on results
- A/B testing framework for calibrations

## References

- **Specification:** JF1-CAL-ARCH-2026-01-02
- **Epistemic Foundation:** `artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json`
- **Phase 2 Architecture:** `src/farfan_pipeline/phases/Phase_two/`
- **Test Suite:** `tests/calibration/`

## Version History

- **1.0.0** (2026-01-02): Initial implementation
  - Core types (CalibrationBounds, CalibrationParameter, CalibrationLayer)
  - Type-specific defaults
  - Prohibited operations enforcement
  - Comprehensive test suite (28 tests)
  - Full mypy strict compliance
