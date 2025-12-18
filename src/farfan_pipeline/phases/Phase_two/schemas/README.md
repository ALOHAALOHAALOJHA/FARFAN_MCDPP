# Phase 2 JSON Schema Specifications

This directory contains JSON Schema specifications for Phase 2 (Micro-Question Execution Layer) of the F.A.R.F.A.N Mechanistic Policy Pipeline.

## Schema Version

All schemas in this directory implement **JSON Schema Draft 2020-12** and are versioned as **1.0.0** with an effective date of **2025-12-18**.

## Schema Files

### 1. executor_config.schema.json

**Purpose:** Runtime configuration schema for Phase 2 executors.

**Key Features:**
- Defines executor identity (executor_id, executor_class)
- Specifies contract payload types handled
- Controls determinism behavior (seed strategy)
- Sets resource limits (memory, CPU, concurrency)
- Enforces Dura Lex contracts with configurable enforcement levels
- Includes content integrity verification via SHA-256 hash

**Required Fields:**
- `schema_version`: Must be "1.0.0"
- `executor_id`: snake_case identifier (3-64 chars)
- `executor_class`: PascalCase class name ending with "Executor"
- `contract_types`: Array of payload types (PascalCase, ending with "Payload")
- `determinism`: Object with is_deterministic flag and seed_strategy
- `resource_limits`: CPU, memory, and concurrency constraints
- `created_at`: ISO-8601 timestamp

**Optional Fields:**
- `contracts`: Array of Dura Lex contracts with enforcement levels
- `content_hash`: SHA-256 hash for integrity verification

### 2. executor_output.schema.json

**Purpose:** Output schema for Phase 2 executor execution results.

**Key Features:**
- Captures task execution status and results
- Maintains provenance chain (chunk_id → task_id → result)
- Provides structured error reporting
- Records contract verification results
- Ensures deterministic execution tracking via seed

**Required Fields:**
- `schema_version`: Must be "1.0.0"
- `task_id`: 16-character hex identifier
- `chunk_id`: Source CPP chunk identifier
- `executor_id`: Executor that produced this result
- `success`: Boolean execution status
- `timestamp`: ISO-8601 execution timestamp
- `provenance`: Phase, stage, and seed information

**Optional Fields:**
- `shard_index`: Shard within chunk (0-4)
- `error`: Error details if success=false
- `result`: Execution result if success=true
- `duration_ms`: Execution time in milliseconds
- `contracts_verified`: Array of contract verification results

### 3. synchronization_manifest.schema.json

**Purpose:** SISAS synchronization manifest mapping CPP chunks to executor tasks.

**Key Features:**
- Enforces strict cardinality invariants (60 chunks → 300 tasks)
- Maps each chunk to exactly 5 shards
- Integrates SISAS signal priorities
- Validates surjection and provenance
- Ensures coverage threshold compliance (0.85 minimum)

**Required Fields:**
- `schema_version`: Must be "1.0.0"
- `manifest_id`: 32-character hex identifier
- `created_at`: ISO-8601 timestamp
- `cardinality`: Invariant definitions (60/300/5)
- `chunk_mappings`: Array of exactly 60 chunk-to-task mappings
- `sisas_integration`: Signal registry and coverage information
- `verification`: Surjection, cardinality, and provenance checks

**Invariants:**
- Exactly 60 input chunks (const)
- Exactly 300 output tasks (const)
- Exactly 5 shards per chunk (const)
- Surjection verified = true (const)
- Cardinality verified = true (const)
- Provenance verified = true (const)
- Coverage threshold = 0.85 (const)

### 4. calibration_policy.schema.json

**Purpose:** Calibration policy for executor behavior tuning.

**Key Features:**
- Defines quality thresholds (precision, recall, confidence, coverage)
- Establishes action bands based on quality scores
- References canonical methodological sources
- Supports weight modifiers for adaptive behavior
- Date-stamped policy identification

**Required Fields:**
- `schema_version`: Must be "1.0.0"
- `policy_id`: Format "CAL-YYYY-MM-DD-{8-char hex}"
- `effective_date`: ISO-8601 date
- `thresholds`: Minimum quality thresholds (0-1 range)
- `bands`: Array of quality bands with actions

**Optional Fields:**
- `derivation_source`: Reference to canonical source
- `content_hash`: SHA-256 integrity hash

## Usage

### Validation

To validate a JSON file against a schema:

```python
import json
from jsonschema import validate

# Load schema
with open('schemas/executor_config.schema.json') as f:
    schema = json.load(f)

# Load data
with open('config.json') as f:
    data = json.load(f)

# Validate
validate(instance=data, schema=schema)
```

### Example Files

Example template files for each schema are available in the `examples/` subdirectory.

## Integration Points

### Phase 2 Components

- **executor_config.py**: Runtime configuration loader
- **base_executor_with_contract.py**: Base executor class
- **batch_executor.py**: Batch execution orchestration
- **irrigation_synchronizer.py**: SISAS integration
- **calibration_policy.py**: Quality threshold enforcement

### Dura Lex Contracts

The following Dura Lex contracts are referenced in executor configurations:

1. **RoutingContract**: Ensures correct routing to executors
2. **ConcurrencyDeterminism**: Guarantees deterministic concurrent execution
3. **ContextImmutability**: Enforces context immutability during execution
4. **PermutationInvariance**: Ensures order-independent results
5. **RuntimeContracts**: Validates runtime behavior contracts
6. **SnapshotContract**: Ensures consistent state snapshots

Enforcement levels:
- `FATAL`: Violations halt execution
- `WARNING`: Violations are logged but execution continues
- `DISABLED`: Contract checking is disabled

## Version History

- **1.0.0** (2025-12-18): Initial schema specifications
  - ExecutorConfig schema
  - ExecutorOutput schema
  - SynchronizationManifest schema
  - CalibrationPolicy schema

## References

- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12/schema
- F.A.R.F.A.N Architecture: See `docs/design/ARCHITECTURE.md`
- Phase 2 Audit Report: See `PHASE_2_AUDIT_REPORT.md`
- Dura Lex Contracts: See `src/farfan_pipeline/infrastructure/contractual/dura_lex/`

## Maintenance

These schemas are canonical specifications. Any modifications must:

1. Maintain backward compatibility within the same major version
2. Update the schema version appropriately (semver)
3. Document changes in this README
4. Update corresponding example files
5. Validate all existing instances against the updated schema
