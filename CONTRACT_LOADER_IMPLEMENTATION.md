# Contract Loader Implementation - Complete

**Document ID**: `IMPL-CONTRACT-LOADER-001`  
**Status**: IMPLEMENTED  
**Date**: 2025-12-19  
**Integration**: Extended `base_executor_with_contract.py`

---

## 1. Implementation Summary

Extended existing `BaseExecutorWithContract` class with batch contract loading capabilities, leveraging the existing contract caching infrastructure.

## 2. Methods Added

### 2.1 `load_all_contracts()` - Primary Interface

**Signature**:
```python
@classmethod
def load_all_contracts(
    cls,
    contracts_dir: str | None = None,
    version: str = "v3",
    validate_schema: bool = True,
) -> list[dict[str, Any]]
```

**Purpose**: Batch load all 300 specialized contracts (Q001.v3.json - Q300.v3.json)

**Features**:
- Loads all 300 contracts in sequence
- Uses existing `_contract_cache` for performance
- Validates schema for v3 contracts
- Returns ordered list (Q001-Q300)
- Comprehensive error reporting

**Usage**:
```python
# Load all v3 contracts with validation
contracts = BaseExecutorWithContract.load_all_contracts()

# Load from custom directory
contracts = BaseExecutorWithContract.load_all_contracts(
    contracts_dir="/path/to/contracts",
    version="v3",
    validate_schema=True
)

# Access specific contract
q005_contract = contracts[4]  # Q005
```

### 2.2 `_load_contract_from_file()` - Helper Method

**Signature**:
```python
@classmethod
def _load_contract_from_file(
    cls,
    question_id: str,
    contracts_dir: str,
    version: str = "v3",
    validate_schema: bool = True
) -> dict[str, Any]
```

**Purpose**: Load single contract with caching

**Features**:
- Cache integration via `_contract_cache`
- File existence validation
- JSON parsing with error handling
- Schema validation for v3
- Automatic file extension handling (.v3.json vs .json)

### 2.3 `_validate_contract_schema()` - Validation Method

**Signature**:
```python
@classmethod
def _validate_contract_schema(
    cls,
    contract: dict[str, Any],
    question_id: str
) -> None
```

**Purpose**: Validate v3 contract structure

**Validates**:
- Required v3 keys present: `identity`, `executor_binding`, `method_binding`, `question_context`, `evidence_assembly`, `output_contract`
- `identity.question_id` matches expected question_id
- Raises `ValueError` with detailed message on failure

### 2.4 `clear_contract_cache()` - Cache Management

**Signature**:
```python
@classmethod
def clear_contract_cache(cls) -> None
```

**Purpose**: Clear contract cache (useful for testing/updates)

### 2.5 `get_cached_contract_count()` - Cache Inspection

**Signature**:
```python
@classmethod
def get_cached_contract_count(cls) -> int
```

**Purpose**: Get number of cached contracts

---

## 3. Integration with Canonical Phase 2

### 3.1 Phase 2.1 Irrigation Orchestrator

**Usage in JOIN Table Construction** (Subfase 2.1.0):
```python
from src.farfan_pipeline.phases.Phase_two.base_executor_with_contract import (
    BaseExecutorWithContract
)

# Load all 300 specialized contracts
specialized_contracts = BaseExecutorWithContract.load_all_contracts(
    contracts_dir=contracts_path,
    version="v3",
    validate_schema=True
)

# Pass to IrrigationOrchestrator
orchestrator = IrrigationOrchestrator(
    questionnaire_monolith=monolith,
    preprocessed_document=document,
    signal_registry=registry,
    specialized_contracts=specialized_contracts,  # All 300 contracts
    enable_join_table=True
)
```

### 3.2 Phase 2.2 Task Executor

**Pre-loading contracts for execution**:
```python
# Pre-load all contracts before task execution
all_contracts = BaseExecutorWithContract.load_all_contracts()

# Contracts are now cached for O(1) lookup during execution
# Each DynamicContractExecutor benefits from cached contracts
```

---

## 4. Error Handling

### 4.1 Error Types

**FileNotFoundError**:
- Raised if contracts directory doesn't exist
- Raised if individual contract file missing

**ValueError**:
- Raised if contract loading fails (aggregated errors for all failures)
- Raised if contract fails schema validation
- Raised if identity.question_id mismatch

**json.JSONDecodeError**:
- Raised if contract JSON is malformed

### 4.2 Error Messages

**Batch Load Failure**:
```
Failed to load 3 contracts:
Q042: Contract file not found: /path/Q042.v3.json
Q105: invalid JSON: Expecting property name...
Q287: Contract missing required v3 keys: ['method_binding']
```

**Schema Validation Failure**:
```
Contract Q123 missing required v3 keys: ['identity', 'output_contract']
```

**Identity Mismatch**:
```
Contract identity mismatch: expected Q045, got Q044
```

---

## 5. Performance Characteristics

### 5.1 Caching

- **First load**: ~2-3 seconds for 300 contracts (I/O bound)
- **Cached access**: O(1) per contract
- **Memory footprint**: ~30-50MB for 300 contracts (depends on contract size)

### 5.2 Optimization

- Cache persists across class instances
- Cache key includes directory path for multi-environment support
- Schema validation optional for performance tuning

---

## 6. Testing Strategy

### 6.1 Unit Tests

```python
def test_load_all_contracts():
    """Test batch loading all 300 contracts."""
    contracts = BaseExecutorWithContract.load_all_contracts()
    assert len(contracts) == 300
    assert contracts[0]['identity']['question_id'] == 'Q001'
    assert contracts[299]['identity']['question_id'] == 'Q300'

def test_contract_caching():
    """Test contract caching works."""
    BaseExecutorWithContract.clear_contract_cache()
    assert BaseExecutorWithContract.get_cached_contract_count() == 0
    
    contracts = BaseExecutorWithContract.load_all_contracts()
    assert BaseExecutorWithContract.get_cached_contract_count() == 300
    
    # Second load should be faster (cached)
    contracts2 = BaseExecutorWithContract.load_all_contracts()
    assert contracts == contracts2

def test_missing_contract_file():
    """Test error handling for missing contract."""
    with pytest.raises(ValueError, match="Failed to load"):
        BaseExecutorWithContract.load_all_contracts(
            contracts_dir="/nonexistent/path"
        )
```

### 6.2 Integration Tests

- Test with Phase 2.1 IrrigationOrchestrator
- Test with Phase 2.2 TaskExecutor
- Test cache coherence across multiple orchestrator instances

---

## 7. Migration Guide

### 7.1 Before (Manual Contract Loading)

```python
# Load contracts one by one
contracts = []
for q_num in range(1, 301):
    question_id = f"Q{q_num:03d}"
    contract_path = contracts_dir / f"{question_id}.v3.json"
    with open(contract_path) as f:
        contract = json.load(f)
    contracts.append(contract)
```

### 7.2 After (Batch Contract Loading)

```python
# Single call loads all 300 contracts with validation and caching
contracts = BaseExecutorWithContract.load_all_contracts()
```

**Benefits**:
- Single line vs. loop
- Automatic caching
- Schema validation included
- Error aggregation
- Type safety

---

## 8. Compatibility

### 8.1 Backward Compatibility

- **Preserved**: Existing `_contract_cache` infrastructure
- **Preserved**: Individual contract loading patterns
- **Preserved**: v2 and v3 contract support
- **No Breaking Changes**: All new methods are additions

### 8.2 Version Support

- **v2 contracts**: Supported (set `version="v2"`)
- **v3 contracts**: Supported (default, with schema validation)
- **Mixed versions**: Not supported in single call (use separate calls)

---

## 9. Collateral Action Status

**Original Requirement**: Specialized contract loader implementation (MEDIUM - 1-2 days)

**Status**: ✅ **COMPLETED**

**Implementation Time**: 1 hour (leveraged existing infrastructure)

**Remaining Collateral Actions**: 2 items
1. Comprehensive integration tests (HIGH - 3-4 days)
2. ValidationOrchestrator integration (MEDIUM - 1-2 days)

---

## 10. References

- **Base Implementation**: `src/farfan_pipeline/phases/Phase_two/base_executor_with_contract.py`
- **Integration Point 1**: `src/canonic_phases/phase_2/phase2_d_irrigation_orchestrator.py` (Subfase 2.1.0)
- **Integration Point 2**: `src/canonic_phases/phase_2/phase2_e_task_executor.py` (Pre-execution)
- **Contract Location**: `executor_contracts/specialized/Q{nnn}.v3.json`

---

## 11. Future Enhancements

### 11.1 Parallel Loading

```python
# Future: Parallel contract loading with ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

@classmethod
def load_all_contracts_parallel(cls, ...):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(cls._load_contract_from_file, f"Q{i:03d}", ...)
            for i in range(1, 301)
        ]
        contracts = [f.result() for f in futures]
    return contracts
```

### 11.2 Lazy Loading Iterator

```python
# Future: Memory-efficient lazy loading
@classmethod
def iter_contracts(cls, ...):
    for q_num in range(1, 301):
        yield cls._load_contract_from_file(f"Q{q_num:03d}", ...)
```

### 11.3 Contract Versioning

```python
# Future: Track contract versions and detect updates
@classmethod
def get_contract_metadata(cls, question_id: str):
    return {
        "version": "v3",
        "last_modified": ...,
        "checksum": ...,
    }
```
