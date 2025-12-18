# Phase 2 Constants Module

## Overview

This module provides the single source of truth for all Phase 2 constants, implementing the **Constants Freeze Contract** to ensure no runtime IO determines behavior.

## Location

```
src/canonic_phases/phase_2/constants/phase2_constants.py
```

## Design Principles

1. **No Runtime IO**: All constants are defined at module load time
2. **Immutability**: All data structures use `Final`, `frozen=True`, and `frozenset`
3. **Type Safety**: Strict type annotations with dataclasses
4. **Compile-Time Verification**: Assertions verify invariants at import time
5. **Single Source of Truth**: No constant redefinition across codebase

## Constants Categories

### 1. Cardinality Invariants

- `CPP_CHUNK_COUNT = 60`: Number of CPP chunks from Phase 1
- `MICRO_ANSWER_COUNT = 300`: Total micro-answers produced by Phase 2
- `SHARDS_PER_CHUNK = 5`: Micro-answers per CPP chunk

**Invariant**: `CPP_CHUNK_COUNT * SHARDS_PER_CHUNK == MICRO_ANSWER_COUNT`

### 2. Executor Registry

Defines executor configuration with frozen dataclasses:

```python
EXECUTOR_REGISTRY: Dict[str, ExecutorRegistryEntry] = {
    "contract_executor": ExecutorRegistryEntry(
        canonical_name="ContractExecutor",
        contract_types=frozenset({"ContractPayload", "ValidationPayload"}),
        priority=1,
        deterministic=True,
    ),
    # ... more executors
}
```

### 3. Schema Version Control

Tracks JSON schema versions with content hashes:

```python
SCHEMA_VERSIONS: Dict[str, SchemaVersion] = {
    "executor_config": SchemaVersion(
        name="executor_config.schema.json",
        version="1.0.0",
        content_hash="",  # Populated by CI
    ),
    # ... more schemas
}
```

### 4. SISAS Synchronization Policy

- `SISAS_SIGNAL_COVERAGE_THRESHOLD = 0.85`: Minimum signal coverage
- `SISAS_IRRIGATION_LINK_MINIMUM = 1`: Minimum irrigation links per chunk
- `SISAS_PRIORITY_WEIGHT_SIGNAL = 0.6`: Signal-derived priority weight
- `SISAS_PRIORITY_WEIGHT_STATIC = 0.4`: Static priority weight

**Invariant**: Weights sum to 1.0

### 5. Determinism Control

- `DEFAULT_RANDOM_SEED = 42`: Seed for stochastic operations
- `HASH_ALGORITHM = "sha256"`: Hash algorithm for verification

### 6. Error Codes

Structured error taxonomy with frozen dataclasses:

```python
ERROR_CODES: Dict[str, ErrorCode] = {
    "E2001": ErrorCode(
        code="E2001",
        category="ROUTING",
        severity="FATAL",
        message_template="No executor found for contract type: {contract_type}",
    ),
    # ... E2002-E2007
}
```

### 7. Forbidden Patterns

CI-enforced restrictions:

- `FORBIDDEN_IMPORTS`: Modules that must not be imported
- `FORBIDDEN_RUNTIME_IO_PATTERNS`: File patterns that trigger violations

## Usage

```python
from canonic_phases.phase_2.constants import (
    CPP_CHUNK_COUNT,
    MICRO_ANSWER_COUNT,
    EXECUTOR_REGISTRY,
    ERROR_CODES,
)

# Use constants directly
if chunk_count != CPP_CHUNK_COUNT:
    raise ValueError(f"Expected {CPP_CHUNK_COUNT} chunks")

# Access error messages
error = ERROR_CODES["E2001"]
message = error.message_template.format(contract_type="InvalidType")
```

## Testing

Run validation tests:

```bash
pytest tests/test_phase2_constants.py -v
```

Or use the standalone validation script:

```bash
python3 << EOF
import sys
sys.path.insert(0, 'src')
from canonic_phases.phase_2.constants import CPP_CHUNK_COUNT
assert CPP_CHUNK_COUNT == 60
print("✓ Constants module validated")
EOF
```

## Contract Compliance

This module enforces:

- **ConstantsFreezeContract**: No runtime file access
- **SingleSourceContract**: All Phase 2 constants defined here
- **ImmutabilityContract**: All structures frozen or Final
- **DeterminismContract**: Fixed seeds and reproducible behavior

## Version History

- **1.0.0** (2025-12-18): Initial implementation
  - Cardinality invariants (60 CPP chunks → 300 micro-answers)
  - Executor registry with 3 executors
  - SISAS synchronization policy
  - 7 error codes (E2001-E2007)
  - Forbidden pattern enforcement
