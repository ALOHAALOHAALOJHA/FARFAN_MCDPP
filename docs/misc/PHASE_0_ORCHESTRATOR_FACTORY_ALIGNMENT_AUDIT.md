# PHASE 0: ORCHESTRATOR-FACTORY ALIGNMENT AUDIT

**Date**: 2025-12-30  
**Auditor**: Claude (Anthropic)  
**Scope**: Full alignment audit between Orchestrator, Factory, and Phase 0 dynamic flow  
**Severity Classification**: CRITICAL, HIGH, MEDIUM, LOW

---

## EXECUTIVE SUMMARY

This audit identified **12 critical gaps** and **8 medium-priority inconsistencies** between the orchestrator, factory, and Phase 0 flow. The primary issues center around:

1. **Signature Mismatches**: Orchestrator `__init__` expects different parameters than Factory provides
2. **Import Path Fragmentation**: Multiple import paths for the same components
3. **Gate Validation Gaps**: Exit gates 5-7 require attributes not initialized in VerifiedPipelineRunner
4. **Duplicate Code**: Two `cli()` functions and two `run()` methods in phase0_90_00_main.py
5. **Factory-Orchestrator DI Mismatch**: Constructor parameters don't align

---

## CRITICAL FINDINGS (Must Fix)

### C-01: Orchestrator Constructor Signature Mismatch

**Location**: `src/farfan_pipeline/orchestration/orchestrator.py` (lines 1297-1309)  
**Factory Location**: `src/farfan_pipeline/phases/Phase_two/phase2_10_00_factory.py` (lines 1111-1118)

**Issue**: The Orchestrator expects `questionnaire: CanonicalQuestionnaire` as a constructor parameter, but Factory passes it with inconsistent naming:

```python
# Orchestrator expects (orchestrator.py:1302):
def __init__(
    self,
    method_executor: MethodExecutor,
    questionnaire: CanonicalQuestionnaire,  # Named parameter
    executor_config: ExecutorConfig,
    ...
)

# Factory passes (phase2_10_00_factory.py:1112-1118):
orchestrator = Orchestrator(
    questionnaire=self._canonical_questionnaire,  # ✓ Matches
    method_executor=self._method_executor,         # ✓ Matches
    executor_config=executor_config,               # ✓ Matches
    validation_constants=validation_constants,    # ✗ NOT IN ORCHESTRATOR SIGNATURE
    signal_registry=self._signal_registry,        # ✗ NOT IN ORCHESTRATOR SIGNATURE
)
```

**Impact**: Factory will fail at runtime if `validation_constants` and `signal_registry` kwargs are passed to Orchestrator.

**Remediation**:
```python
# Option A: Add missing parameters to Orchestrator.__init__
def __init__(
    self,
    method_executor: MethodExecutor,
    questionnaire: CanonicalQuestionnaire,
    executor_config: ExecutorConfig,
    runtime_config: RuntimeConfig | None = None,
    phase0_validation: Phase0ValidationResult | None = None,
    validation_constants: dict[str, Any] | None = None,  # ADD
    signal_registry: Any | None = None,  # ADD (already present via method_executor)
    ...
)

# Option B: Remove extra kwargs from Factory._build_orchestrator()
orchestrator = Orchestrator(
    method_executor=self._method_executor,  # Already contains signal_registry
    questionnaire=self._canonical_questionnaire,
    executor_config=executor_config,
    # Remove: validation_constants, signal_registry (use method_executor's registry)
)
```

---

### C-02: Exit Gates 5-7 Missing Required Attributes

**Location**: `src/farfan_pipeline/phases/Phase_zero/phase0_50_01_exit_gates.py`  
**Protocol**: Lines 34-45 (Phase0Runner Protocol)

**Issue**: Exit gates 5-7 require `method_executor` and `questionnaire` attributes on the runner, but `VerifiedPipelineRunner` in `phase0_90_02_bootstrap.py` doesn't initialize these:

```python
# Protocol expects (phase0_50_01_exit_gates.py:43-44):
class Phase0Runner(Protocol):
    method_executor: Any | None
    questionnaire: Any | None

# But VerifiedPipelineRunner doesn't set these:
class VerifiedPipelineRunner:
    def __init__(self, ...):
        # Missing: self.method_executor = None
        # Missing: self.questionnaire = None
```

**Impact**: Gates 5 (questionnaire_integrity), 6 (method_registry), and 7 (smoke_tests) will always fail because they check `runner.method_executor` which doesn't exist.

**Remediation**: Add missing attributes to `VerifiedPipelineRunner.__init__()`:
```python
# In phase0_90_02_bootstrap.py:
self.method_executor: Any | None = None
self.questionnaire: Any | None = None
```

---

### C-03: Duplicate `cli()` and `run()` Definitions

**Location**: `src/farfan_pipeline/phases/Phase_zero/phase0_90_00_main.py`

**Issue**: File contains two definitions of `cli()` (lines 643 and 1769) and two definitions of `run()` (lines 458 and 1637). This is a syntax error in Python.

**Impact**: The second definition shadows the first, causing unexpected behavior.

**Remediation**: Remove duplicate definitions. Keep only the complete implementation (lines 1637-1716 for `run()` and lines 1769-1825 for `cli()`).

---

### C-04: Import Path Fragmentation

**Issue**: Same components are imported from different paths across files:

| Component | Correct Path | Used Paths |
|-----------|--------------|------------|
| `RuntimeConfig` | `canonic_phases.Phase_zero.phase0_10_01_runtime_config` | Also imported as `from farfan_pipeline.phases.Phase_zero...` |
| `GateResult` | `canonic_phases.Phase_zero.phase0_50_01_exit_gates` | Multiple aliased imports |
| `CanonicalQuestionnaire` | `orchestration.factory` | Also from `phase2_10_00_factory` |

**Impact**: Module loading inconsistencies, potential type mismatches, increased memory usage.

**Remediation**: Standardize on `canonic_phases` prefix for Phase_zero imports:
```python
# Standard imports for Phase 0 components:
from canonic_phases.Phase_zero.phase0_10_01_runtime_config import RuntimeConfig, RuntimeMode
from canonic_phases.Phase_zero.phase0_50_01_exit_gates import GateResult, check_all_gates
```

---

### C-05: Factory Singleton Pattern Violation Risk

**Location**: `src/farfan_pipeline/phases/Phase_two/phase2_10_00_factory.py` (lines 640-705)

**Issue**: `_load_canonical_questionnaire()` uses class-level singleton tracking, but concurrent factory instances could cause race conditions:

```python
class AnalysisPipelineFactory:
    _questionnaire_loaded = False  # Class-level state
    _questionnaire_instance: CanonicalQuestionnaire | None = None
```

**Impact**: In concurrent scenarios, multiple loads could occur before singleton flag is set.

**Remediation**: Add thread-safe locking:
```python
import threading

class AnalysisPipelineFactory:
    _questionnaire_lock = threading.Lock()
    _questionnaire_loaded = False
    _questionnaire_instance: CanonicalQuestionnaire | None = None

    def _load_canonical_questionnaire(self) -> None:
        with self._questionnaire_lock:
            if self._questionnaire_loaded:
                self._canonical_questionnaire = self._questionnaire_instance
                return
            # ... rest of loading logic
            self._questionnaire_loaded = True
```

---

### C-06: Phase0ValidationResult Not Passed from VerifiedPipelineRunner

**Location**: Orchestrator expects `phase0_validation: Phase0ValidationResult | None` (orchestrator.py:1303)

**Issue**: The `VerifiedPipelineRunner` in `phase0_90_02_bootstrap.py` never creates or passes `Phase0ValidationResult` to the factory/orchestrator chain. The exit gates in `phase0_50_01_exit_gates.py` produce `GateResult` objects, but these are never packaged into `Phase0ValidationResult`.

**Impact**: Orchestrator validation of Phase 0 gates is bypassed. The `if phase0_validation is not None:` check in orchestrator always takes the `None` path.

**Remediation**: After `check_all_gates()` in bootstrap, create and pass `Phase0ValidationResult`:
```python
# In phase0_90_02_bootstrap.py after run_phase_zero():
from farfan_pipeline.orchestration.orchestrator import Phase0ValidationResult

all_passed, gate_results = check_all_gates(self)
phase0_validation = Phase0ValidationResult(
    all_passed=all_passed,
    gate_results=gate_results,
    validation_time=datetime.utcnow().isoformat()
)
# Pass to factory for injection into Orchestrator
```

---

### C-07: GenericContractExecutor Undefined Reference

**Location**: `src/farfan_pipeline/orchestration/orchestrator.py` (lines 2319-2330, 2471-2480)

**Issue**: `GenericContractExecutor` is used but never imported. The file imports `DynamicContractExecutor` from `phase2_60_00_base_executor_with_contract` but uses `GenericContractExecutor`:

```python
# Import (line 70):
from farfan_pipeline.phases.Phase_two.phase2_60_00_base_executor_with_contract import DynamicContractExecutor

# Usage (lines 2319-2330):
instance = GenericContractExecutor(  # ✗ NOT IMPORTED
    method_executor=self.executor,
    ...
)
```

**Impact**: `NameError: name 'GenericContractExecutor' is not defined` at runtime.

**Remediation**: Either:
1. Import `GenericContractExecutor`:
   ```python
   from farfan_pipeline.phases.Phase_two.phase2_60_00_base_executor_with_contract import GenericContractExecutor
   ```
2. Or use the imported `DynamicContractExecutor`:
   ```python
   instance = DynamicContractExecutor(...)
   ```

---

### C-08: Method Executor Signal Registry Requirement Mismatch

**Location**: `orchestrator.py` lines 1070-1113 vs `phase2_10_00_factory.py` lines 954-959

**Issue**: Orchestrator's `MethodExecutor.__init__()` expects:
```python
def __init__(
    self,
    dispatcher: Any | None = None,
    signal_registry: Any | None = None,
    method_registry: Any | None = None,
)
```

But Factory passes:
```python
method_executor = MethodExecutor(
    method_registry=method_registry,
    arg_router=arg_router,           # ✗ NOT IN SIGNATURE
    signal_registry=self._signal_registry,
)
```

**Impact**: `TypeError: __init__() got an unexpected keyword argument 'arg_router'`

**Remediation**: Add `arg_router` parameter to `MethodExecutor.__init__()`:
```python
def __init__(
    self,
    dispatcher: Any | None = None,
    signal_registry: Any | None = None,
    method_registry: Any | None = None,
    arg_router: Any | None = None,  # ADD
) -> None:
    ...
    self._router = arg_router or ExtendedArgRouter(registry)
```

---

## HIGH-PRIORITY FINDINGS (Should Fix)

### H-01: RuntimeMode.PRODUCTION vs RuntimeMode.PROD Inconsistency

**Location**: `orchestrator.py` lines 2429, 2435

**Issue**: Code references `RuntimeMode.PRODUCTION` but `RuntimeMode` enum uses `PROD`:
```python
# Usage in orchestrator.py:
if self.runtime_config.mode == RuntimeMode.PRODUCTION:  # ✗ Should be PROD

# Definition in phase0_10_01_runtime_config.py:
class RuntimeMode(Enum):
    PROD = "prod"
    DEV = "dev"
    EXPLORATORY = "exploratory"
```

**Remediation**: Change `RuntimeMode.PRODUCTION` to `RuntimeMode.PROD`.

---

### H-02: Missing `_validate_questionnaire_structure` Import

**Location**: `orchestrator.py` line 1311

**Issue**: Imports from `orchestration.questionnaire_validation` but the import in orchestrator might fail if path resolution doesn't work:
```python
from orchestration.questionnaire_validation import _validate_questionnaire_structure
```

**Impact**: Potential `ImportError` depending on PYTHONPATH.

**Remediation**: Use full path:
```python
from farfan_pipeline.orchestration.questionnaire_validation import _validate_questionnaire_structure
```

---

### H-03: Hardcoded Expected Counts Don't Match

**Location**: 
- `orchestrator.py:94-95`: `EXPECTED_QUESTION_COUNT = 305`, `EXPECTED_METHOD_COUNT = 416`
- `phase2_10_00_factory.py:1057-1063`: Default validation constants use `60` chunks

**Issue**: Question count expectation varies between files. AGENTS.md specifies 300 micro questions.

**Remediation**: Centralize constants in `PHASE_0_CONSTANTS.py`:
```python
EXPECTED_MICRO_QUESTION_COUNT: Final[int] = 300
EXPECTED_MESO_QUESTION_COUNT: Final[int] = 4
EXPECTED_MACRO_QUESTION_COUNT: Final[int] = 1
EXPECTED_TOTAL_QUESTION_COUNT: Final[int] = 305
EXPECTED_METHOD_COUNT: Final[int] = 416
```

---

### H-04: Bootstrap Module Location Confusion

**Issue**: Two different `VerifiedPipelineRunner` classes exist:
1. `phase0_90_00_main.py` - Contains full implementation with path/import verification
2. `phase0_90_02_bootstrap.py` - Contains Phase 0-specific implementation with gate checks

**Impact**: Unclear which runner to use; potential code divergence.

**Remediation**: Consolidate into single canonical runner in `phase0_90_02_bootstrap.py`, have `phase0_90_00_main.py` import and delegate.

---

## MEDIUM-PRIORITY FINDINGS (Nice to Fix)

### M-01: Phase 0 Stage Taxonomy Not Applied to Module Names

**Issue**: `PHASE_0_CONSTANTS.py` defines stage taxonomy but not all modules follow the `phase0_{STAGE}_{ORDER}_{name}.py` pattern consistently.

### M-02: Missing Error Recovery in Exit Gates

**Issue**: `check_all_gates()` uses fail-fast, but no mechanism to skip failed gates or partial recovery in DEV mode.

### M-03: Calibration Parameters Reference Undefined Variable

**Location**: `phase0_90_00_main.py` line 1407

**Issue**: `calibrated_params` is referenced but the lines that populate it are commented out:
```python
# calibrated_params = param_loader.get(method_key)  # CALIBRATION DISABLED
required_coverage = calibrated_params.get(...)  # ✗ NameError
```

### M-04: Factory `build_processor` Alias Inconsistency

**Issue**: `build_processor` is aliased to `create_analysis_pipeline` in factory, but `phase0_90_00_main.py` imports it as:
```python
from orchestration.factory import build_processor
```

This works via the `orchestration/__init__.py` shim, but is fragile.

---

## REMEDIATION ACTION PLAN

### Phase 1: Critical Fixes (Blocking)

| ID | Action | File | Lines | Priority |
|----|--------|------|-------|----------|
| C-01 | Add `validation_constants` and `signal_registry` to Orchestrator or remove from Factory call | orchestrator.py, phase2_10_00_factory.py | 1297-1309, 1111-1118 | P0 |
| C-02 | Add `method_executor` and `questionnaire` attributes to `VerifiedPipelineRunner` | phase0_90_02_bootstrap.py | 78-125 | P0 |
| C-03 | Remove duplicate `cli()` and `run()` definitions | phase0_90_00_main.py | 643-708, 1637-1825 | P0 |
| C-07 | Import or alias `GenericContractExecutor` | orchestrator.py | 70 | P0 |
| C-08 | Add `arg_router` parameter to `MethodExecutor.__init__()` | orchestrator.py | 1073-1077 | P0 |

### Phase 2: High-Priority Fixes (This Sprint)

| ID | Action | File | Lines | Priority |
|----|--------|------|-------|----------|
| C-04 | Standardize imports to `canonic_phases.Phase_zero` prefix | Multiple | Multiple | P1 |
| C-05 | Add thread-safe locking to Factory singleton | phase2_10_00_factory.py | 440-445 | P1 |
| C-06 | Create and pass `Phase0ValidationResult` to Orchestrator | phase0_90_02_bootstrap.py | TBD | P1 |
| H-01 | Fix `RuntimeMode.PRODUCTION` → `RuntimeMode.PROD` | orchestrator.py | 2429, 2435 | P1 |
| H-02 | Fix `orchestration.questionnaire_validation` import | orchestrator.py | 1311 | P1 |
| H-03 | Centralize expected counts in `PHASE_0_CONSTANTS.py` | Multiple | Multiple | P1 |

### Phase 3: Medium-Priority Fixes (Next Sprint)

| ID | Action | Priority |
|----|--------|----------|
| M-03 | Fix `calibrated_params` undefined reference | P2 |
| M-04 | Stabilize `build_processor` import path | P2 |
| H-04 | Consolidate `VerifiedPipelineRunner` implementations | P2 |

---

## VERIFICATION CHECKLIST

After remediation, verify:

- [ ] `python -c "from orchestration.factory import build_processor; print(build_processor)"` succeeds
- [ ] `python -c "from farfan_pipeline.orchestration.orchestrator import Orchestrator, MethodExecutor"` succeeds
- [ ] `pytest tests/test_phase0*.py -v` passes
- [ ] All 7 exit gates can be evaluated without `AttributeError`
- [ ] Factory creates Orchestrator without `TypeError`
- [ ] No duplicate function definitions in any Phase 0 module

---

## APPENDIX: FILES AUDITED

1. `src/farfan_pipeline/orchestration/orchestrator.py` (3236 lines)
2. `src/farfan_pipeline/phases/Phase_two/phase2_10_00_factory.py` (1598 lines)
3. `src/farfan_pipeline/phases/Phase_zero/phase0_90_00_main.py` (1830 lines)
4. `src/farfan_pipeline/phases/Phase_zero/phase0_90_01_verified_pipeline_runner.py` (517 lines)
5. `src/farfan_pipeline/phases/Phase_zero/phase0_90_02_bootstrap.py` (1013 lines)
6. `src/farfan_pipeline/phases/Phase_zero/phase0_50_01_exit_gates.py` (669 lines)
7. `src/farfan_pipeline/phases/Phase_zero/PHASE_0_CONSTANTS.py` (330 lines)
8. `src/orchestration/__init__.py` (shim module)
