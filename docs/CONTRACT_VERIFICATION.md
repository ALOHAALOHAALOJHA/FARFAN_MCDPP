# Contract Verification System

## Overview

The Contract Verification System provides pre-execution validation of all 30 base executor contracts (D1-Q1 through D6-Q5) at factory initialization time. This ensures that:

1. All contract files exist and are valid JSON
2. Required fields are present for both v2 and v3 contract formats
3. JSON schemas are valid
4. All referenced method classes exist in the class registry
5. Contract structure matches expected patterns

## Architecture

### Components

#### 1. BaseExecutorWithContract
The base class for all contract-driven executors. It now includes:
- `verify_all_base_contracts()`: Class method that verifies all 30 contracts
- `_verify_single_contract()`: Validates a single contract file
- `_verify_v2_contract_fields()`: Validates v2 format requirements
- `_verify_v3_contract_fields()`: Validates v3 format requirements

#### 2. AnalysisPipelineFactory
The factory now calls contract verification during `_build_method_executor()`:
- Happens after class registry is built
- Occurs before method executor is returned
- Strict mode causes initialization failure on any contract errors

#### 3. Verification Utility
Standalone verification script at `src/farfan_pipeline/core/orchestrator/verify_contracts.py`:
```bash
python -m farfan_pipeline.core.orchestrator.verify_contracts [--strict] [--verbose] [--json]
```

## Contract File Locations

Contracts are searched in the following order:

1. `config/executor_contracts/{base_slot}.v3.json`
2. `config/executor_contracts/{base_slot}.json`
3. `config/executor_contracts/specialized/Q{number}.v3.json`
4. `config/executor_contracts/specialized/Q{number}.json`

Where `{number}` is calculated as: `(dimension - 1) * 5 + question`

Example mappings:
- D1-Q1 → Q001
- D2-Q3 → Q008
- D6-Q5 → Q030

## Validation Rules

### v2 Contract Format

Required fields:
- `method_inputs` (list): Array of method specifications
  - Each entry must have: `class`, `method`
  - Optional: `provides`, `args`, `priority`
- `assembly_rules` (list): Evidence assembly rules
- `validation_rules` (dict/list): Validation specifications

Method class validation:
- Each `class` in `method_inputs` must exist in the class registry
- Failure to find a class results in an error

### v3 Contract Format

Required top-level fields:
- `identity`: Contract identity information
  - `base_slot`: Must match the executor's base slot
- `method_binding`: Method orchestration configuration
  - Single-method mode: `class_name`, `method_name`
  - Multi-method mode: `methods` array with `class_name`, `method_name` per entry
- `evidence_assembly`: Evidence assembly configuration
  - `assembly_rules` (list): Assembly rules
- `validation_rules`: Validation specifications
- `question_context`: Question-specific context
  - `expected_elements`: List of expected evidence elements
- `error_handling`: Error handling configuration

Method class validation:
- All referenced `class_name` values must exist in class registry
- Applies to both single-method and multi-method modes

### Schema Validation

- v2 contracts validated against: `config/executor_contract.schema.json`
- v3 contracts validated against: `config/schemas/executor_contract.v3.schema.json`
- Schema validation is non-blocking (warnings only) if schema file is missing

## Usage

### Factory Integration (Automatic)

Contract verification happens automatically during factory initialization:

```python
from farfan_pipeline.core.orchestrator.factory import AnalysisPipelineFactory

factory = AnalysisPipelineFactory(
    questionnaire_path="path/to/questionnaire.json",
    strict_validation=True  # Fail on contract errors
)

bundle = factory.create_orchestrator()  # Verification happens here
```

If `strict_validation=True`, any contract errors will raise `ExecutorConstructionError`.

### Standalone Verification

Run verification independently:

```bash
# Basic verification
python -m farfan_pipeline.core.orchestrator.verify_contracts

# Strict mode (exit code 1 on errors)
python -m farfan_pipeline.core.orchestrator.verify_contracts --strict

# Verbose output
python -m farfan_pipeline.core.orchestrator.verify_contracts --verbose

# JSON output
python -m farfan_pipeline.core.orchestrator.verify_contracts --json

# Skip class registry (faster but incomplete)
python -m farfan_pipeline.core.orchestrator.verify_contracts --no-class-registry
```

### Programmatic Usage

```python
from farfan_pipeline.core.orchestrator.base_executor_with_contract import (
    BaseExecutorWithContract
)
from farfan_pipeline.core.orchestrator.class_registry import build_class_registry

# Build class registry
class_registry = build_class_registry()

# Verify all contracts
result = BaseExecutorWithContract.verify_all_base_contracts(
    class_registry=class_registry
)

if not result["passed"]:
    print(f"Verification failed with {len(result['errors'])} errors:")
    for error in result["errors"]:
        print(f"  - {error}")
else:
    print(f"All {len(result['verified_contracts'])} contracts verified successfully")
```

## Verification Result Format

The verification methods return a dictionary with:

```python
{
    "passed": bool,              # True if all contracts valid
    "total_contracts": int,      # Always 30 for full verification
    "errors": [str],             # List of error messages
    "warnings": [str],           # List of warning messages
    "verified_contracts": [str]  # List of base_slot IDs that passed
}
```

### Error Format

Errors are prefixed with the base slot identifier:

```
[D1-Q1] Contract file not found. Tried: ...
[D2-Q3] method_inputs[2]: class 'MissingClass' not found in class registry
[D3-Q5] Missing required field: validation_rules
```

### Warning Format

Warnings indicate non-critical issues:

```
[D1-Q1] Contract structure is v3 but file naming suggests v2
[D4-Q2] Schema file not found: config/schemas/executor_contract.v3.schema.json. Skipping schema validation.
```

## Caching

Verification results are cached at the class level:
- `_factory_contracts_verified`: Boolean flag
- `_factory_verification_errors`: List of errors from last verification

Subsequent calls return cached results immediately.

To reset cache (for testing):
```python
BaseExecutorWithContract._factory_contracts_verified = False
BaseExecutorWithContract._factory_verification_errors = []
```

## Error Handling

### Strict Mode (Default in Factory)

With `strict_validation=True`:
- Contract errors raise `ExecutorConstructionError`
- Factory initialization fails
- Pipeline cannot start

### Non-Strict Mode

With `strict_validation=False`:
- Errors are logged but not raised
- Factory initialization continues
- Pipeline may fail during execution if contracts are invalid

## Testing

Test suite located at `tests/core/orchestrator/test_contract_verification.py`:

```bash
pytest tests/core/orchestrator/test_contract_verification.py -v
```

Test coverage includes:
- All contracts verification
- Error accumulation
- Caching behavior
- Missing files
- v2/v3 field validation
- Method class registry lookup
- Base slot to Q number calculation

## Performance

Verification is fast and happens only once at factory initialization:
- ~30ms for all 30 contracts (with class registry)
- ~5ms for cached results
- No runtime overhead during execution

## Logging

Verification emits structured logs at different levels:

```python
logger.info("contract_verification_start verifying_30_base_contracts")
logger.info("contract_verification_passed verified=30 warnings=0")
logger.error("contract_verification_failed errors=3 warnings=1")
logger.error("contract_error: [D1-Q1] Missing required field: method_inputs")
logger.warning("contract_warning: [D2-Q1] Schema validation skipped")
```

## Integration Points

1. **Factory (`factory.py`)**:
   - Called in `_build_method_executor()`
   - After class registry built
   - Before method executor stored

2. **BaseExecutorWithContract (`base_executor_with_contract.py`)**:
   - Verification logic
   - Contract loading
   - Field validation

3. **ClassRegistry (`class_registry.py`)**:
   - Provides method class types
   - Used to validate class existence

## Future Enhancements

Potential improvements:
1. Parallel contract verification for faster startup
2. Contract diff reporting between versions
3. Contract migration tools (v2 → v3)
4. Integration with CI/CD for contract validation
5. Contract coverage metrics (which methods are actually used)

## Troubleshooting

### "Contract file not found"
- Check that contract exists in `config/executor_contracts/specialized/`
- Verify Q number calculation: `(dimension-1)*5 + question`
- Ensure file has correct extension (`.json` or `.v3.json`)

### "class 'X' not found in class registry"
- Check `class_registry.py` for class mapping
- Verify import path in `_CLASS_PATHS`
- Ensure module is importable
- Check for missing dependencies

### "Schema validation failed"
- Review contract structure against schema
- Check for missing required fields
- Verify data types (list vs dict, etc.)
- Compare with working contract

### "Verification failed in non-strict mode"
- Check logs for specific errors
- Consider running with `--json` for structured output
- Use standalone verification tool for detailed diagnostics
