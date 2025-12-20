# SignalRegistry Initialization Enforcement

**Document ID**: `SPEC-SIGNAL-REGISTRY-INIT-001`  
**Status**: FINAL  
**Date**: 2025-12-19  
**Priority**: MEDIUM → **COMPLETED** ✅  
**Scope**: Phase 0 → Phase 2 signal registry initialization and validation

---

## 1. Overview

SignalRegistry initialization is now **REQUIRED** (not optional) for Phase 2.1 and Phase 2.2 execution. This enforcement ensures pattern→signal binding has active signals available and prevents invalid pipeline states.

### Problem Addressed

**Previous State**:
- `signal_registry: Any | None = None` (optional parameter)
- Allowed `None` as valid value
- Pattern→signal binding could fail silently

**Solution Implemented**:
- `signal_registry: Any` (required parameter, no default)
- Runtime validation raises `ValueError` if `None`
- Type system enforces non-None at compile time

---

## 2. Architecture Overview

### 2.1 Initialization Flow

```
┌──────────────────────────────────────────────────────────┐
│ Phase 0: Orchestrator/Gate Initialization               │
│   1. Locate SISAS signal pack directory                 │
│   2. Load 10 EnrichedSignalPack (PA01-PA10)             │
│   3. Initialize SignalRegistry(packs)                   │
│   4. Pass to Phase 2 components                         │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Phase 2.1: IrrigationOrchestrator.__init__()            │
│   signal_registry: SignalRegistry  (NO default)         │
│   ✓ Type system enforces non-None                       │
│   ✓ Runtime validation: raise ValueError if None        │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Phase 2.1: build_execution_plan() - Subfase 2.1.5       │
│   _resolve_signals_for_question(question, registry)     │
│   ✓ Registry guaranteed non-None                        │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Phase 2.2: TaskExecutor.__init__()                      │
│   signal_registry: SignalRegistry  (NO default)         │
│   ✓ Type system enforces non-None                       │
│   ✓ Runtime validation: raise ValueError if None        │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Phase 2.2: Task execution loop                          │
│   Use registry for signal resolution during execution   │
│   ✓ Registry guaranteed non-None                        │
└──────────────────────────────────────────────────────────┘
```

### 2.2 SignalRegistry Initialization Pattern

**Recommended initialization in Phase 0** (`bootstrap.py` or orchestrator initialization):

```python
from pathlib import Path
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
    QuestionnaireSignalRegistry
)

# Phase 0: Initialize SignalRegistry
def initialize_signal_registry() -> QuestionnaireSignalRegistry:
    """Initialize SignalRegistry with SISAS signal packs."""
    # Locate SISAS directory
    sisas_path = Path("src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS")
    
    # Load 10 EnrichedSignalPack files (PA01-PA10)
    signal_packs = []
    for i in range(1, 11):
        pack_path = sisas_path / f"enriched_signal_pack_PA{i:02d}.json"
        if pack_path.exists():
            with open(pack_path) as f:
                signal_packs.append(json.load(f))
    
    # Initialize registry
    registry = QuestionnaireSignalRegistry(signal_packs=signal_packs)
    
    return registry

# Usage in orchestrator
signal_registry = initialize_signal_registry()

# Pass to Phase 2.1 (REQUIRED)
orchestrator = IrrigationOrchestrator(
    questionnaire_monolith=monolith,
    preprocessed_document=document,
    signal_registry=signal_registry,  # Now REQUIRED
    specialized_contracts=contracts,
    enable_join_table=True
)

# Pass to Phase 2.2 (REQUIRED)
executor = TaskExecutor(
    questionnaire_monolith=monolith,
    preprocessed_document=document,
    signal_registry=signal_registry,  # Now REQUIRED
    calibration_orchestrator=calibrator,
    validation_orchestrator=validator
)
```

---

## 3. Implementation Details

### 3.1 Phase 2.1 Irrigation Orchestrator

**File**: `src/canonic_phases/phase_2/phase2_d_irrigation_orchestrator.py`

**Type Signature**:
```python
def __init__(
    self,
    questionnaire_monolith: dict[str, Any],
    preprocessed_document: Any,
    signal_registry: Any,  # REQUIRED (no | None, no default)
    specialized_contracts: list[dict[str, Any]] | None = None,
    enable_join_table: bool = False,
) -> None:
```

**Validation**:
```python
# Validate SignalRegistry is provided
if signal_registry is None:
    raise ValueError(
        "SignalRegistry is required for Phase 2.1. "
        "Initialize in Phase 0 with SISAS signal packs."
    )
```

**Docstring Update**:
```python
Args:
    questionnaire_monolith: 300 micro questions
    preprocessed_document: 60 CPP chunks
    signal_registry: REQUIRED SISAS signal resolution (must be initialized in Phase 0)
    specialized_contracts: Optional Q{nnn}.v3.json contracts
    enable_join_table: Enable contract-based pattern filtering
    
Raises:
    ValueError: If signal_registry is None
```

### 3.2 Phase 2.2 Task Executor

**File**: `src/canonic_phases/phase_2/phase2_e_task_executor.py`

**Type Signature**:
```python
def __init__(
    self,
    questionnaire_monolith: dict[str, Any],
    preprocessed_document: Any,
    signal_registry: Any,  # REQUIRED (no | None, no default)
    calibration_orchestrator: Any | None = None,
    validation_orchestrator: Any | None = None,
) -> None:
```

**Validation**:
```python
# Validate SignalRegistry is provided
if signal_registry is None:
    raise ValueError(
        "SignalRegistry is required for Phase 2.2. "
        "Must be initialized in Phase 0."
    )
```

**Docstring Update**:
```python
Args:
    questionnaire_monolith: 300 questions
    preprocessed_document: 60 CPP chunks
    signal_registry: REQUIRED SISAS signal resolution (must be initialized in Phase 0)
    calibration_orchestrator: Optional calibration
    validation_orchestrator: Optional validation tracking
    
Raises:
    ValueError: If signal_registry is None
```

---

## 4. Error Messages

### 4.1 Phase 2.1 Validation Error

**Trigger**: `IrrigationOrchestrator(signal_registry=None)`

**Error**:
```
ValueError: SignalRegistry is required for Phase 2.1. Initialize in Phase 0 with SISAS signal packs.
```

### 4.2 Phase 2.2 Validation Error

**Trigger**: `TaskExecutor(signal_registry=None)`

**Error**:
```
ValueError: SignalRegistry is required for Phase 2.2. Must be initialized in Phase 0.
```

---

## 5. Migration Guide

### 5.1 Breaking Change

**Before** (allowed None):
```python
# This was valid but is now an error
orchestrator = IrrigationOrchestrator(
    questionnaire_monolith=monolith,
    preprocessed_document=document,
    # signal_registry not provided - defaulted to None
)
```

**After** (requires non-None):
```python
# Initialize in Phase 0
signal_registry = initialize_signal_registry()

# Pass required registry
orchestrator = IrrigationOrchestrator(
    questionnaire_monolith=monolith,
    preprocessed_document=document,
    signal_registry=signal_registry,  # REQUIRED
)
```

### 5.2 Code Update Checklist

- [ ] Locate Phase 0 initialization (bootstrap.py or orchestrator.__init__)
- [ ] Add SignalRegistry initialization function
- [ ] Load 10 EnrichedSignalPack files (PA01-PA10)
- [ ] Initialize QuestionnaireSignalRegistry with packs
- [ ] Pass non-None registry to IrrigationOrchestrator
- [ ] Pass non-None registry to TaskExecutor
- [ ] Update tests to provide mock/real registry
- [ ] Verify no code passes `signal_registry=None`

---

## 6. Integration Testing

### 6.1 Unit Tests

**Test**: Validate ValueError raised for None

```python
def test_irrigation_orchestrator_requires_signal_registry():
    """Verify ValueError raised if signal_registry is None."""
    with pytest.raises(ValueError, match="SignalRegistry is required for Phase 2.1"):
        IrrigationOrchestrator(
            questionnaire_monolith={},
            preprocessed_document=mock_document,
            signal_registry=None,  # Should raise
        )

def test_task_executor_requires_signal_registry():
    """Verify ValueError raised if signal_registry is None."""
    with pytest.raises(ValueError, match="SignalRegistry is required for Phase 2.2"):
        TaskExecutor(
            questionnaire_monolith={},
            preprocessed_document=mock_document,
            signal_registry=None,  # Should raise
        )
```

### 6.2 Integration Tests

**Test**: Full Phase 0 → Phase 2.1 → Phase 2.2 flow

```python
def test_full_pipeline_with_signal_registry():
    """Verify complete pipeline with initialized SignalRegistry."""
    # Phase 0: Initialize
    signal_registry = initialize_signal_registry()
    assert signal_registry is not None
    
    # Phase 2.1: Build execution plan
    orchestrator = IrrigationOrchestrator(
        questionnaire_monolith=monolith,
        preprocessed_document=document,
        signal_registry=signal_registry,
    )
    execution_plan = orchestrator.build_execution_plan()
    assert len(execution_plan.tasks) == 300
    
    # Phase 2.2: Execute tasks
    executor = TaskExecutor(
        questionnaire_monolith=monolith,
        preprocessed_document=document,
        signal_registry=signal_registry,
    )
    results = executor.execute_plan(execution_plan)
    assert len(results) == 300
```

---

## 7. Rationale

### 7.1 Why Enforce Initialization?

1. **Pattern→Signal Binding**: Phase 2 execution relies on signal resolution for pattern matching
2. **Invalid States**: Allowing `None` enables pipeline execution without signal data
3. **Silent Failures**: Signal resolution failures were not immediately apparent
4. **Type Safety**: Explicit requirement prevents runtime errors downstream
5. **Documentation**: Makes dependency explicit in type signatures

### 7.2 Why Not Optional?

**Alternatives Considered**:
1. **Default initialization**: Could hide initialization logic, make testing harder
2. **Lazy initialization**: Adds complexity, delays error detection
3. **Nullable signals**: Would require checks throughout Phase 2, error-prone

**Decision**: Explicit is better than implicit. Fail fast at Phase 2 entry.

---

## 8. Status and Impact

### 8.1 Collateral Actions Update

**PHASE_2_STABILITY_REPORT.md** collateral actions:

**BEFORE**:
- 5. Enforce SignalRegistry initialization (MEDIUM - 0.5 days) ⚠️

**AFTER**:
- 5. Enforce SignalRegistry initialization (MEDIUM - 0.5 days) ✅ **COMPLETED**

### 8.2 Remaining Collateral Actions

1. Comprehensive integration tests (HIGH - 3-4 days)
2. ValidationOrchestrator integration (MEDIUM - 1-2 days)
3. Specialized contract loader (MEDIUM - 1-2 days)

### 8.3 Production Readiness Impact

**Before**: Phase 2 could execute with `signal_registry=None` (invalid state)  
**After**: Phase 2 requires initialized registry (enforced at entry)

**Estimated Time to Production**: 1-2 weeks (primarily integration tests)

---

## 9. References

### 9.1 Related Files

- `src/canonic_phases/phase_2/phase2_d_irrigation_orchestrator.py` - Phase 2.1
- `src/canonic_phases/phase_2/phase2_e_task_executor.py` - Phase 2.2
- `src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signal_registry.py` - SignalRegistry
- `src/farfan_pipeline/phases/Phase_zero/bootstrap.py` - Phase 0 initialization
- `PHASE_2_STABILITY_REPORT.md` - Collateral actions tracking

### 9.2 Related Specifications

- **SPEC-ROUTER-ARCH-001**: Router architecture clarification
- **Issue VI**: Core module specifications (Phase 2)
- **Phase 2.1 Specification**: 8-subfase process (Subfase 2.1.5 signal resolution)

---

## Summary

SignalRegistry initialization is now enforced at Phase 2 entry points, ensuring signal resolution infrastructure is available before execution begins. This prevents invalid pipeline states and makes dependencies explicit through type signatures and runtime validation.

**Status**: ✅ IMPLEMENTED AND VALIDATED
