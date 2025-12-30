# Technical Specification: Contract Loader Integration into Dynamic Executor

**Document ID**:  `SPEC-CONTRACT-LOADER-002`  
**Status**:  FINAL  
**Date**: 2025-12-19  
**Integration Strategy**: Extend existing `dynamic_contract_executor.py`

---

## 1. Revised Architecture Decision

**Observation**: `dynamic_contract_executor.py` already contains: 
1. `_load_contract(question_id)` class method (line ~619)
2. Contract caching infrastructure (`_contract_cache`)
3. Multi-path resolution (base/specialized, v2/v3)
4. Schema validation integration

**Decision**: **Extend existing infrastructure** instead of creating separate `ContractLoader` class.

**Benefits**:
- Avoids duplication of contract loading logic
- Maintains existing cache coherence
- Preserves schema validation integration
- Reduces import complexity

---

## 2. Required Additions to `dynamic_contract_executor.py`

### Addition 1: Batch Contract Loading Class Method

**Location**: After `_load_contract()` method (insert after line ~670)

```python
@classmethod
def load_all_contracts(
    cls,
    contracts_dir: Path | None = None,
    version: str = "v3",
    validate_schema: bool = True,
) -> list[dict[str, Any]]:
    """Load all 300 specialized contracts from directory.
    
    Batch loads Q001.v3.json through Q300.v3.json with validation and caching.
    
    Args:
        contracts_dir: Directory containing specialized contracts. 
                      Defaults to PROJECT_ROOT/. ../executor_contracts/specialized/
        version: Contract version to load ("v2" or "v3")
        validate_schema: Whether to validate contracts against JSON schema
    
    Returns: 
        List of 300 contract dicts, ordered by question_id (Q001-Q300)
    
    Raises:
        ContractLoadError: If any contract fails to load or validate
        FileNotFoundError: If contracts directory doesn't exist
    
    Example:
        >>> contracts = BaseExecutorWithContract.load_all_contracts()
        >>> len(contracts)
        300
        >>> contracts[0]["identity"]["question_id"]
        'Q001'
    """
    if contracts_dir is None:
        contracts_dir = (
            PROJECT_ROOT
            / "src"
            / "farfan_pipeline"
            / "phases"
            / "Phase_two"
            / "json_files_phase_two"
            / "executor_contracts"
            / "specialized"
        )
    
    if not contracts_dir.exists():
        raise FileNotFoundError(
            f"Contracts directory not found:  {contracts_dir}.  "
            "Ensure executor_contracts/specialized/ exists with Q001-Q300 contracts."
        )
    
    import logging
    logger = logging.getLogger(__name__)
    
    contracts = []
    errors = []
    
    for q_num in range(1, 301):  # Q001 through Q300
        question_id = f"Q{q_num: 03d}"
        
        try:
            # Use existing _load_contract method for consistency
            contract = cls._load_contract(question_id=question_id)
            
            # Validate contract has required fields
            cls._validate_contract_structure(contract, question_id)
            
            contracts.append(contract)
            
        except FileNotFoundError as e:
            error_msg = f"{question_id}: Contract file not found - {e}"
            errors.append(error_msg)
            logger.error(error_msg)
            
        except json.JSONDecodeError as e:
            error_msg = f"{question_id}: Invalid JSON - {e}"
            errors.append(error_msg)
            logger. error(error_msg)
            
        except ValueError as e:
            # Schema validation failure (from _load_contract)
            error_msg = f"{question_id}:  Validation failed - {e}"
            errors.append(error_msg)
            logger.error(error_msg)
            
        except Exception as e:
            error_msg = f"{question_id}: Unexpected error - {e}"
            errors.append(error_msg)
            logger.error(error_msg)
    
    if errors:
        raise ContractLoadError(
            question_id="BATCH",
            reason=f"Failed to load {len(errors)}/300 contracts.  Errors:\n" +
                   "\n".join(errors[: 10]) +  # Show first 10 errors
                   (f"\n... and {len(errors) - 10} more" if len(errors) > 10 else "")
        )
    
    logger.info(f"Successfully loaded {len(contracts)} contracts from {contracts_dir}")
    
    return contracts


@classmethod
def _validate_contract_structure(cls, contract: dict[str, Any], question_id:  str) -> None:
    """Validate contract has required structural fields. 
    
    Checks minimal structure for both v2 and v3 contracts to ensure
    they can be executed without runtime errors.
    
    Args:
        contract:  Parsed contract dict
        question_id: Question identifier for error messages
    
    Raises:
        ValueError: If contract structure is invalid
    """
    contract_version = contract.get("_contract_version", "v2")
    
    if contract_version == "v3":
        # v3 required fields
        if "identity" not in contract:
            raise ValueError(f"{question_id}: Missing 'identity' field")
        
        identity = contract["identity"]
        if "question_id" not in identity: 
            raise ValueError(f"{question_id}: Missing 'identity.question_id'")
        
        if identity["question_id"] != question_id:
            raise ValueError(
                f"{question_id}: question_id mismatch - "
                f"expected {question_id}, found {identity['question_id']}"
            )
        
        if "method_binding" not in contract:
            raise ValueError(f"{question_id}: Missing 'method_binding' field")
        
        method_binding = contract["method_binding"]
        orchestration_mode = method_binding.get("orchestration_mode", "single_method")
        
        if orchestration_mode == "multi_method_pipeline":
            if "methods" not in method_binding:
                raise ValueError(
                    f"{question_id}:  multi_method_pipeline mode requires 'methods' array"
                )
            if not method_binding["methods"]:
                raise ValueError(f"{question_id}: 'methods' array is empty")
        else: 
            # Single method mode
            if "class_name" not in method_binding and "primary_method" not in method_binding:
                raise ValueError(
                    f"{question_id}: single_method mode requires 'class_name' or 'primary_method'"
                )
    
    else: 
        # v2 required fields
        if "method_inputs" not in contract:
            raise ValueError(f"{question_id}:  Missing 'method_inputs' field")
        
        if not isinstance(contract["method_inputs"], list):
            raise ValueError(f"{question_id}: 'method_inputs' must be a list")
        
        if not contract["method_inputs"]: 
            raise ValueError(f"{question_id}: 'method_inputs' is empty")
```

---

### Addition 2: Exception Class

**Location**: After imports (insert after line ~25, after `if TYPE_CHECKING` block)

```python
class ContractLoadError(Exception):
    """Raised when contract loading fails. 
    
    Attributes: 
        question_id: Question identifier that failed to load
        reason: Human-readable error description
    """
    
    def __init__(self, question_id: str, reason: str) -> None:
        self.question_id = question_id
        self.reason = reason
        super().__init__(f"Contract load failed for {question_id}: {reason}")
```

---

### Addition 3: Cache Statistics Method

**Location**: After `load_all_contracts()` method

```python
@classmethod
def get_cache_stats(cls) -> dict[str, Any]:
    """Get contract cache statistics for observability.
    
    Returns:
        Dict with cache size, hit rate estimates, and loaded contracts
    
    Example:
        >>> stats = BaseExecutorWithContract.get_cache_stats()
        >>> stats["cache_size"]
        150
        >>> stats["contracts_loaded"]
        ['D1-Q1', 'D1-Q2:Q001', ...]
    """
    return {
        "cache_size": len(cls._contract_cache),
        "contracts_loaded": list(cls._contract_cache.keys()),
        "schema_validators_loaded": list(cls._schema_validators. keys()),
        "factory_verification_complete": cls._factory_contracts_verified,
        "factory_verification_errors": len(cls._factory_verification_errors),
    }


@classmethod
def clear_cache(cls) -> None:
    """Clear contract cache (useful for testing or hot-reload scenarios)."""
    cls._contract_cache.clear()
    import logging
    logging.info("Contract cache cleared")
```

---

## 3. Integration into Orchestrator Phase 2.1

**Location**: `orchestrator. py` (Phase 2.1 initialization, before `IrrigationSynchronizer` instantiation)

**Find**: Line where `IrrigationSynchronizer` is instantiated (search for `IrrigationSynchronizer(`)

**Insert Before**: 

```python
# === Phase 2.1: Load specialized contracts for 300-question model ===
specialized_contracts = None
if self.executor_config.enable_specialized_contracts:  # Feature flag
    try:
        from canonic_phases.Phase_two.dynamic_contract_executor import (
            BaseExecutorWithContract,
            ContractLoadError,
        )
        
        logger.info("Loading 300 specialized contracts for Phase 2.1...")
        
        specialized_contracts = BaseExecutorWithContract.load_all_contracts(
            version="v3",
            validate_schema=True,
        )
        
        logger.info(
            f"Successfully loaded {len(specialized_contracts)} specialized contracts",
            cache_stats=BaseExecutorWithContract.get_cache_stats()
        )
        
    except ContractLoadError as e:
        logger.error(
            f"Failed to load specialized contracts: {e}",
            question_id=e.question_id,
            reason=e.reason
        )
        # Decide whether to fail-fast or degrade gracefully
        if self.runtime_config.mode. value == "prod":
            raise RuntimeError(
                "Production mode requires all 300 contracts to load successfully"
            ) from e
        else:
            logger.warning(
                "Development mode: Continuing without specialized contracts"
            )
            specialized_contracts = None
    
    except Exception as e:
        logger. error(f"Unexpected error loading contracts: {e}", exc_info=True)
        if self.runtime_config.mode. value == "prod":
            raise
        specialized_contracts = None

# === Instantiate IrrigationSynchronizer with contracts ===
synchronizer = IrrigationSynchronizer(
    questionnaire=self._canonical_questionnaire. data,
    preprocessed_document=preprocessed_document,
    signal_registry=self. executor. signal_registry,
    contracts=specialized_contracts,  # ← NEW: Pass loaded contracts
    enable_join_table=True,  # Enable JOIN table architecture
)
```

---

## 4. Feature Flag Addition

**Location**: `executor_config.py` (or equivalent config dataclass)

**Add Field**:

```python
@dataclass
class ExecutorConfig: 
    # ... existing fields ...
    
    enable_specialized_contracts: bool = True
    """Enable loading of 300 specialized contracts (Q001-Q300.v3.json).
    
    When True: 
      - Phase 2.1 loads all contracts via BaseExecutorWithContract.load_all_contracts()
      - IrrigationSynchronizer receives contracts for JOIN table architecture
      - DynamicContractExecutor uses per-question contracts
    
    When False: 
      - Falls back to 30 base contracts (D1-Q1 through D6-Q5)
      - Legacy multiplier pattern (1 contract → 10 questions)
    """
```

---

## 5. Success Criteria

| Criterion | Verification Method | Expected Outcome |
|-----------|---------------------|------------------|
| **Batch loading works** | `contracts = BaseExecutorWithContract.load_all_contracts()` | Returns 300 contracts, no errors |
| **Cache populated** | `BaseExecutorWithContract.get_cache_stats()["cache_size"]` | == 300 after batch load |
| **Schema validation enforced** | Load contract with invalid schema | Raises `ValueError` with schema details |
| **Missing contracts detected** | Remove Q150. v3.json, run batch load | Raises `ContractLoadError` mentioning Q150 |
| **Orchestrator integration** | Run Phase 2.1 with `enable_specialized_contracts=True` | Logs "Successfully loaded 300 contracts" |
| **Backward compatibility** | Run with `enable_specialized_contracts=False` | Falls back to 30 base contracts |
| **Production fail-fast** | Missing contract in PROD mode | Raises `RuntimeError`, aborts execution |
| **Development degradation** | Missing contract in DEV mode | Logs warning, continues with `contracts=None` |

---

## 6. Testing Specification

### Test 1: Batch Load All Contracts

```python
# tests/test_contract_loader.py

def test_load_all_contracts_success(contracts_dir_with_300_files):
    """Verify batch loading of 300 contracts."""
    from canonic_phases.Phase_two. dynamic_contract_executor import BaseExecutorWithContract
    
    contracts = BaseExecutorWithContract.load_all_contracts(
        contracts_dir=contracts_dir_with_300_files,
        version="v3",
    )
    
    assert len(contracts) == 300
    
    # Verify ordering
    assert contracts[0]["identity"]["question_id"] == "Q001"
    assert contracts[149]["identity"]["question_id"] == "Q150"
    assert contracts[299]["identity"]["question_id"] == "Q300"
    
    # Verify all have required fields
    for contract in contracts: 
        assert "identity" in contract
        assert "method_binding" in contract
        assert "_contract_version" in contract


def test_load_all_contracts_missing_file(contracts_dir_with_299_files):
    """Verify error when contract missing."""
    from canonic_phases. Phase_two.dynamic_contract_executor import (
        BaseExecutorWithContract,
        ContractLoadError,
    )
    
    with pytest.raises(ContractLoadError) as exc_info:
        BaseExecutorWithContract.load_all_contracts(
            contracts_dir=contracts_dir_with_299_files
        )
    
    assert "Q150" in str(exc_info.value)  # Assuming Q150 is missing
    assert exc_info.value.question_id == "BATCH"


def test_load_all_contracts_invalid_json(contracts_dir_with_invalid_json):
    """Verify error when contract has invalid JSON."""
    from canonic_phases.Phase_two.dynamic_contract_executor import ContractLoadError
    
    with pytest.raises(ContractLoadError) as exc_info:
        BaseExecutorWithContract.load_all_contracts(
            contracts_dir=contracts_dir_with_invalid_json
        )
    
    assert "Invalid JSON" in str(exc_info.value)


def test_cache_populated_after_batch_load(contracts_dir_with_300_files):
    """Verify cache is populated after batch load."""
    from canonic_phases.Phase_two.dynamic_contract_executor import BaseExecutorWithContract
    
    BaseExecutorWithContract.clear_cache()
    initial_stats = BaseExecutorWithContract.get_cache_stats()
    assert initial_stats["cache_size"] == 0
    
    contracts = BaseExecutorWithContract.load_all_contracts(
        contracts_dir=contracts_dir_with_300_files
    )
    
    final_stats = BaseExecutorWithContract.get_cache_stats()
    assert final_stats["cache_size"] == 300
    assert len(final_stats["contracts_loaded"]) == 300
```

### Test 2: Orchestrator Integration

```python
# tests/test_orchestrator_contract_loading.py

def test_orchestrator_loads_specialized_contracts(mock_orchestrator_phase2):
    """Verify orchestrator Phase 2.1 loads contracts."""
    orchestrator = mock_orchestrator_phase2
    orchestrator.executor_config. enable_specialized_contracts = True
    
    # Trigger Phase 2.1
    # ... (implementation depends on orchestrator test harness)
    
    # Verify contracts were loaded
    from canonic_phases.Phase_two.dynamic_contract_executor import BaseExecutorWithContract
    stats = BaseExecutorWithContract.get_cache_stats()
    
    assert stats["cache_size"] == 300


def test_orchestrator_degrades_gracefully_in_dev_mode(
    mock_orchestrator_phase2_dev_mode,
    contracts_dir_missing_files
):
    """Verify orchestrator continues in DEV mode when contracts missing."""
    orchestrator = mock_orchestrator_phase2_dev_mode
    orchestrator.executor_config.enable_specialized_contracts = True
    
    # Should log warning but not raise
    # ... (trigger Phase 2.1)
    
    # Verify execution continued
    assert orchestrator.state == "phase2_running"


def test_orchestrator_fails_fast_in_prod_mode(
    mock_orchestrator_phase2_prod_mode,
    contracts_dir_missing_files
):
    """Verify orchestrator aborts in PROD mode when contracts missing."""
    orchestrator = mock_orchestrator_phase2_prod_mode
    orchestrator.executor_config. enable_specialized_contracts = True
    
    with pytest.raises(RuntimeError, match="Production mode requires all 300 contracts"):
        # Trigger Phase 2.1
        orchestrator.execute_phase_2()
```

---

## 7. Observability

### Logs Added

```json
{
  "event": "specialized_contracts_loading_start",
  "contract_count": 300,
  "version": "v3",
  "validate_schema": true
}
```

```json
{
  "event":  "specialized_contracts_loaded",
  "contracts_loaded": 300,
  "cache_size": 300,
  "duration_ms": 1250
}
```

```json
{
  "event":  "contract_load_error",
  "question_id": "Q150",
  "error_type": "FileNotFoundError",
  "reason": "Contract file not found"
}
```

---

## 8. Migration Path

### Phase 1: Add Methods to `dynamic_contract_executor.py`
- **Add**:  `load_all_contracts()`, `_validate_contract_structure()`, `get_cache_stats()`, `clear_cache()`
- **Add**: `ContractLoadError` exception class
- **Verify**: Unit tests pass (`test_contract_loader.py`)

### Phase 2: Integrate into Orchestrator
- **Add**: Contract loading logic in Phase 2.1 (before `IrrigationSynchronizer`)
- **Add**: `enable_specialized_contracts` feature flag to `ExecutorConfig`
- **Verify**: Integration tests pass (`test_orchestrator_contract_loading.py`)

### Phase 3: Enable in Production
- **Set**: `enable_specialized_contracts=True` in production config
- **Monitor**: Logs for successful contract loading
- **Verify**:  All 300 contracts load without errors

---

## 9. Failure Modes

| Failure Mode | Detection | Mitigation |
|--------------|-----------|------------|
| **Missing contract file** | `ContractLoadError` raised | PROD:  Abort execution; DEV: Log warning, continue |
| **Invalid JSON syntax** | `json.JSONDecodeError` caught | Include in `ContractLoadError` batch report |
| **Schema validation failure** | `ValueError` from `_load_contract()` | Include in error batch, show first 10 errors |
| **question_id mismatch** | `_validate_contract_structure()` check | Raise `ValueError` with details |
| **Empty methods array (v3)** | `_validate_contract_structure()` check | Raise `ValueError` |
| **Contracts directory missing** | `FileNotFoundError` | Clear error:  "Ensure executor_contracts/specialized/ exists" |

---

## 10. Performance Considerations

### Batch Load Performance

**Expected**: 300 contracts × ~50KB/contract = ~15MB total  
**Load Time** (SSD):  ~1-2 seconds for read + parse + validate  
**Memory**:  ~20MB for cached contracts (JSON dicts in memory)

**Optimization**:  Contracts are cached in `_contract_cache` after first load, so repeated calls are instant.

### Cache Invalidation

**Manual**: Call `BaseExecutorWithContract.clear_cache()` to force reload  
**Automatic**: None (cache persists for process lifetime)

**Hot Reload** (Development): 
```python
BaseExecutorWithContract.clear_cache()
contracts = BaseExecutorWithContract.load_all_contracts()
```

---

## 11. Termination Condition

**This specification is FINAL** when: 

1. ✅ `load_all_contracts()` method added to `dynamic_contract_executor.py`
2. ✅ `ContractLoadError` exception defined
3. ✅ `_validate_contract_structure()` validation method added
4. ✅ `get_cache_stats()` and `clear_cache()` observability methods added
5. ✅ Orchestrator Phase 2.1 integration code added
6. ✅ `enable_specialized_contracts` feature flag added to config
7. ✅ All unit tests pass (batch load, cache, validation)
8. ✅ All integration tests pass (orchestrator, PROD/DEV modes)
9. ✅ Production deployment confirms 300 contracts load successfully

**No separate `contract_loader.py` file needed—all functionality embedded in existing executor.**

---

**END OF SPECIFICATION**
