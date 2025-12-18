# Phase 2 JSON Schema Implementation - Technical Documentation

**Version:** 1.0.0  
**Effective Date:** 2025-12-18  
**JSON Schema Draft:** 2020-12  
**Issue Reference:** #17

## Overview

This document provides technical documentation for the Phase 2 JSON Schema specifications implemented for the F.A.R.F.A.N Mechanistic Policy Pipeline. These schemas define the data contracts for the Micro-Question Execution Layer.

## Schema Specifications

### 7.1 ExecutorConfig Schema

**Location:** `src/farfan_pipeline/phases/Phase_two/schemas/executor_config.schema.json`

**Purpose:** Defines runtime configuration for Phase 2 executors, specifying how they execute tasks, manage resources, and enforce contracts.

**Key Properties:**

```json
{
  "schema_version": "1.0.0",
  "executor_id": "text_mining_executor",        // snake_case, 3-64 chars
  "executor_class": "TextMiningExecutor",       // PascalCase, ends with "Executor"
  "contract_types": ["TextMiningPayload"],      // PascalCase, ends with "Payload"
  "determinism": {
    "is_deterministic": true,
    "seed_strategy": "PARAMETERIZED",           // FIXED, PARAMETERIZED, NOT_APPLICABLE
    "default_seed": 42
  },
  "resource_limits": {
    "max_memory_mb": 2048,                      // 64-65536 MB
    "max_cpu_seconds": 300,                     // 1-86400 seconds
    "max_concurrent_tasks": 10                  // 1-1000 tasks
  },
  "contracts": [                                 // Dura Lex contracts
    {
      "contract_name": "RoutingContract",
      "enforcement_level": "FATAL"              // FATAL, WARNING, DISABLED
    }
  ],
  "created_at": "2025-12-18T20:00:00Z",
  "content_hash": "a3f2b8c9..."                 // SHA-256 hash (64 hex chars)
}
```

**Validation Rules:**
- `executor_id`: Must match `^[a-z][a-z0-9_]{2,63}$`
- `executor_class`: Must match `^[A-Z][a-zA-Z0-9]+Executor$`
- `contract_types`: Each must match `^[A-Z][a-zA-Z0-9]+Payload$`
- `resource_limits`: All values must be within specified ranges
- `content_hash`: Must be 64 lowercase hex characters (SHA-256)

**Dura Lex Contracts:**
1. `RoutingContract`: Ensures correct routing to executors
2. `ConcurrencyDeterminism`: Guarantees deterministic concurrent execution
3. `ContextImmutability`: Enforces context immutability
4. `PermutationInvariance`: Ensures order-independent results
5. `RuntimeContracts`: Validates runtime behavior
6. `SnapshotContract`: Ensures consistent state snapshots

### 7.2 ExecutorOutput Schema

**Location:** `src/farfan_pipeline/phases/Phase_two/schemas/executor_output.schema.json`

**Purpose:** Defines the output format for Phase 2 executor execution results, capturing both successful executions and errors with full provenance.

**Key Properties:**

```json
{
  "schema_version": "1.0.0",
  "task_id": "a1b2c3d4e5f6g7h8",               // 16-char hex
  "chunk_id": "CPP_PA01_DIM1_001",             // Source chunk identifier
  "shard_index": 0,                             // 0-4
  "executor_id": "text_mining_executor",
  "success": true,
  "result": {                                   // Present if success=true
    "content": "Analysis text...",
    "content_hash": "b4c5d6e7...",             // SHA-256 (64 hex)
    "pa_code": "PA01",                         // Policy Area code
    "dim_code": "DIM1",                        // Dimension code
    "metadata": {...}                          // Additional metadata
  },
  "error": {                                    // Present if success=false
    "error_code": "E0042",                     // Pattern: E[0-9]{4}
    "error_category": "VALIDATION",            // ROUTING, CARVING, etc.
    "message": "Error description",
    "stack_trace": "Full stack trace"
  },
  "timestamp": "2025-12-18T20:15:30Z",
  "duration_ms": 1245,
  "provenance": {
    "phase": "phase_2",                        // Constant
    "stage": "execution",                      // routing, carving, execution, synchronization
    "seed": 42,
    "config_hash": "a3f2b8c9...",             // SHA-256 of config
    "code_version": "v1.2.3"
  },
  "contracts_verified": [
    {
      "contract_name": "RoutingContract",
      "status": "PASSED",                      // PASSED, FAILED, SKIPPED
      "details": "Details..."
    }
  ]
}
```

**Validation Rules:**
- `task_id`: Must match `^[a-f0-9]{16}$`
- `shard_index`: Must be 0-4
- `error_code`: Must match `^E[0-9]{4}$`
- `error_category`: Must be one of 7 predefined categories
- `provenance.phase`: Must be "phase_2" (constant)
- `provenance.stage`: Must be one of 4 predefined stages

### 7.3 SynchronizationManifest Schema

**Location:** `src/farfan_pipeline/phases/Phase_two/schemas/synchronization_manifest.schema.json`

**Purpose:** Defines the SISAS synchronization manifest that maps CPP chunks to executor tasks, enforcing strict cardinality invariants.

**Key Properties:**

```json
{
  "schema_version": "1.0.0",
  "manifest_id": "f1e2d3c4b5a6978869584736251a0b9c",  // 32-char hex
  "created_at": "2025-12-18T20:00:00Z",
  "cardinality": {                              // INVARIANTS
    "input_chunks": 60,                        // Constant
    "output_tasks": 300,                       // Constant
    "shards_per_chunk": 5                      // Constant
  },
  "chunk_mappings": [                          // Array of exactly 60 items
    {
      "chunk_id": "CPP_PA01_DIM1_001",
      "pa_code": "PA01",
      "dim_code": "DIM1",
      "tasks": [                               // Array of exactly 5 items
        {
          "task_id": "a1b2c3d4e5f6g7h8",
          "shard_index": 0,                    // 0-4
          "executor_id": "text_mining_executor",
          "priority": 0.95,                    // 0.0-1.0
          "signal_annotations": ["SISAS_SIGNAL_001"]
        }
      ],
      "sisas_signals": {
        "irrigation_links": ["Q001_Q005_LINK"],
        "coverage_score": 0.92,                // 0.0-1.0
        "quality_indicators": ["HIGH_PRECISION"]
      }
    }
  ],
  "sisas_integration": {
    "registry_version": "1.2.0",
    "coverage_threshold": 0.85,                // Constant
    "total_signals_applied": 127,
    "chunks_below_threshold": []
  },
  "verification": {
    "surjection_verified": true,               // Constant (must be true)
    "cardinality_verified": true,              // Constant (must be true)
    "provenance_verified": true,               // Constant (must be true)
    "manifest_hash": "c4d5e6f7..."            // SHA-256 (64 hex)
  }
}
```

**Validation Rules:**
- `manifest_id`: Must match `^[a-f0-9]{32}$`
- `cardinality.input_chunks`: Must be 60 (constant)
- `cardinality.output_tasks`: Must be 300 (constant)
- `cardinality.shards_per_chunk`: Must be 5 (constant)
- `chunk_mappings`: Must have exactly 60 items
- Each `chunk_mappings[].tasks`: Must have exactly 5 items
- Each `tasks[].shard_index`: Must be 0-4
- Each `tasks[].priority`: Must be 0.0-1.0
- `sisas_integration.coverage_threshold`: Must be 0.85 (constant)
- `verification.surjection_verified`: Must be true (constant)
- `verification.cardinality_verified`: Must be true (constant)
- `verification.provenance_verified`: Must be true (constant)

**Mathematical Invariant:**
```
60 chunks × 5 shards/chunk = 300 tasks
```

### 7.4 CalibrationPolicy Schema

**Location:** `src/farfan_pipeline/phases/Phase_two/schemas/calibration_policy.schema.json`

**Purpose:** Defines calibration policies for executor behavior tuning, specifying quality thresholds and action bands.

**Key Properties:**

```json
{
  "schema_version": "1.0.0",
  "policy_id": "CAL-2025-12-18-a1b2c3d4",     // Pattern: CAL-YYYY-MM-DD-{8 hex}
  "effective_date": "2025-12-18",
  "thresholds": {
    "precision_minimum": 0.85,                 // 0.0-1.0
    "recall_minimum": 0.80,                    // 0.0-1.0
    "confidence_minimum": 0.75,                // 0.0-1.0
    "coverage_minimum": 0.85                   // 0.0-1.0
  },
  "bands": [                                   // At least 1 band required
    {
      "band_id": "EXCELLENT",
      "lower_bound": 0.90,                     // 0.0-1.0
      "upper_bound": 1.0,                      // 0.0-1.0
      "action": "ACCEPT",                      // ACCEPT, REVIEW, REJECT, ESCALATE
      "weight_modifier": 1.2                   // 0.0-2.0 (default: 1.0)
    }
  ],
  "derivation_source": "derek_beach.MICRO_LEVELS",
  "content_hash": "d5e6f7a8..."               // SHA-256 (64 hex)
}
```

**Validation Rules:**
- `policy_id`: Must match `^CAL-[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]{8}$`
- `effective_date`: Must be valid ISO-8601 date
- All threshold values: Must be 0.0-1.0
- `bands`: Must have at least 1 item
- Each `bands[].lower_bound`: Must be 0.0-1.0
- Each `bands[].upper_bound`: Must be 0.0-1.0
- Each `bands[].action`: Must be ACCEPT, REVIEW, REJECT, or ESCALATE
- Each `bands[].weight_modifier`: Must be 0.0-2.0

## Integration Points

### Phase 2 Components Integration

```
┌─────────────────────────────────────────────────────┐
│ Phase 2 Micro-Question Execution Layer             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ExecutorConfig ──► base_executor_with_contract.py │
│       ↓                      ↓                      │
│  Determinism         Dura Lex Contracts            │
│  Resource Limits     Runtime Enforcement           │
│       ↓                      ↓                      │
│  ExecutorOutput ◄── batch_executor.py              │
│       ↓                      ↓                      │
│  Provenance Chain   Evidence Assembly              │
│       ↓                      ↓                      │
│  SynchronizationManifest ◄── irrigation_sync.py    │
│       ↓                      ↓                      │
│  60→300 Mapping     SISAS Signal Integration      │
│       ↓                      ↓                      │
│  CalibrationPolicy ──► calibration_policy.py       │
│       ↓                      ↓                      │
│  Quality Thresholds  Adaptive Behavior            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Code Integration Examples

**Loading and validating executor config:**

```python
from farfan_pipeline.phases.Phase_two.schemas import (
    validate_executor_config,
    load_schema
)

# Load config from file
with open('config.json') as f:
    config = json.load(f)

# Validate against schema
validate_executor_config(config)

# Use in executor
executor = TextMiningExecutor(config)
```

**Generating executor output:**

```python
from farfan_pipeline.phases.Phase_two.schemas import validate_executor_output
import hashlib

# Create output
output = {
    "schema_version": "1.0.0",
    "task_id": task_id,
    "chunk_id": chunk_id,
    "executor_id": executor_id,
    "success": True,
    "result": {
        "content": result_text,
        "content_hash": hashlib.sha256(result_text.encode()).hexdigest(),
        "pa_code": pa_code,
        "dim_code": dim_code,
    },
    "timestamp": datetime.now().isoformat(),
    "provenance": {
        "phase": "phase_2",
        "stage": "execution",
        "seed": seed,
    }
}

# Validate before saving
validate_executor_output(output)
```

## Validation Utilities

### Command-Line Validation

```bash
# Validate a JSON file against a schema
python src/farfan_pipeline/phases/Phase_two/schemas/validator.py \
    executor_config \
    path/to/config.json

# Available schema names:
# - executor_config
# - executor_output
# - synchronization_manifest
# - calibration_policy
```

### Programmatic Validation

```python
from farfan_pipeline.phases.Phase_two.schemas import (
    validate_file,
    validate_executor_config,
    ValidationError
)

# Validate specific type
try:
    validate_executor_config(config_data)
    print("✓ Config valid")
except ValidationError as e:
    print(f"✗ Validation failed: {e.message}")

# Validate file
try:
    validate_file('config.json', 'executor_config')
    print("✓ File valid")
except ValidationError as e:
    print(f"✗ Validation failed: {e.message}")
```

## Testing

### Running Tests

```bash
# Run schema validation tests
python tests/test_phase2_schemas.py
```

### Test Coverage

The test suite validates:
- ✅ All 4 schema files exist and are valid JSON
- ✅ Schema structures conform to JSON Schema Draft 2020-12
- ✅ All required fields are properly defined
- ✅ All 5 example files are valid JSON
- ✅ Example files conform to their schemas
- ✅ Cardinality invariants are correctly specified
- ✅ Verification constraints are enforced
- ✅ Pattern validations are correctly defined
- ✅ Validator module functions exist and are exportable

## Directory Structure

```
src/farfan_pipeline/phases/Phase_two/schemas/
├── README.md                                    # Schema documentation
├── __init__.py                                  # Package exports
├── validator.py                                 # Validation utilities
├── executor_config.schema.json                  # Config schema (7.1)
├── executor_output.schema.json                  # Output schema (7.2)
├── synchronization_manifest.schema.json         # Manifest schema (7.3)
├── calibration_policy.schema.json               # Policy schema (7.4)
└── examples/
    ├── executor_config.example.json             # Config example
    ├── executor_output.example.json             # Success output example
    ├── executor_output_error.example.json       # Error output example
    ├── synchronization_manifest.example.json    # Manifest example
    └── calibration_policy.example.json          # Policy example
```

## Version History

### Version 1.0.0 (2025-12-18)

**Initial Release**

- ExecutorConfig schema (Section 7.1)
- ExecutorOutput schema (Section 7.2)
- SynchronizationManifest schema (Section 7.3)
- CalibrationPolicy schema (Section 7.4)
- Validation utilities
- Example files for all schemas
- Comprehensive documentation

## References

- **Issue #17**: Original specification document
- **JSON Schema Draft 2020-12**: https://json-schema.org/draft/2020-12/schema
- **Phase 2 Audit Report**: `PHASE_2_AUDIT_REPORT.md`
- **F.A.R.F.A.N Architecture**: `docs/design/ARCHITECTURE.md`
- **Dura Lex Contracts**: `src/farfan_pipeline/infrastructure/contractual/dura_lex/`

## Maintenance Guidelines

### Schema Modifications

When modifying schemas:

1. **Version Management**: Increment version appropriately (semver)
2. **Backward Compatibility**: Maintain within same major version
3. **Documentation**: Update README.md and this document
4. **Examples**: Update example files to reflect changes
5. **Validation**: Run full test suite
6. **Migration**: Provide migration guide if breaking changes

### Adding New Schemas

To add a new schema:

1. Create schema file: `{name}.schema.json`
2. Add to `SCHEMA_FILES` in `validator.py`
3. Create validation function in `validator.py`
4. Export function in `__init__.py`
5. Create example file: `examples/{name}.example.json`
6. Add tests in `tests/test_phase2_schemas.py`
7. Document in README.md and this file

## Support

For questions or issues related to these schemas:

1. Check the README.md in the schemas directory
2. Review example files for usage patterns
3. Run validation utilities for error details
4. Consult Phase 2 architecture documentation
5. Open an issue on GitHub with the `phase-2` label

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-12-18  
**Maintained By:** F.A.R.F.A.N Development Team
