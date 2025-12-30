# Phase 0 and Orchestrator Wiring Specification

**Date**: 2025-12-12  
**Status**: ⚠️ **GAP ANALYSIS**  
**Repository**: ALEXEI-21/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL

---

## Executive Summary

This document analyzes the **current wiring** between Phase 0 (bootstrap/validation) and the Orchestrator, identifies **gaps**, and proposes **solutions** to achieve proper integration.

### Current State
- Phase 0 has robust bootstrap infrastructure in `canonic_phases/Phase_zero/`
- Orchestrator has a `_load_configuration` method (its "Phase 0")
- **MINIMAL INTEGRATION**: Only 3 imports (PROJECT_ROOT, safe_join)
- **NO RuntimeConfig propagation** to orchestrator
- **NO exit gate validation** before phase execution

### Target State
- RuntimeConfig flows from Factory → Orchestrator → Phases
- Orchestrator validates Phase 0 exit gates before executing Phase 1
- Bootstrap failures prevent orchestrator initialization
- Full observability of Phase 0 → Orchestrator handoff

---

## 1. Architecture Overview

### 1.1 Two "Phase 0" Concepts

The codebase has **two distinct "Phase 0" concepts**:

#### A. Phase_zero Module (Bootstrap Phase 0)
**Location**: `src/canonic_phases/Phase_zero/`  
**Purpose**: Pre-orchestrator validation and system initialization  
**Components**:
- `runtime_config.py` - Runtime mode configuration (PROD/DEV/EXPLORATORY)
- `bootstrap.py` - Dependency injection wiring
- `boot_checks.py` - Dependency validation
- `exit_gates.py` - Exit gate validators (4 gates)
- `main.py` - VerifiedPipelineRunner (full pipeline orchestration)
- `determinism.py` - RNG seeding

**Execution Context**: Runs **before** orchestrator is created  
**Exit Point**: Produces `CanonicalInput` for Phase 1

#### B. Orchestrator Phase 0 (Configuration Phase)
**Location**: `src/orchestration/orchestrator.py::_load_configuration` (line 1263)  
**Purpose**: Load questionnaire monolith and prepare aggregation settings  
**Components**:
- Reads `self._monolith_data` (canonical questionnaire)
- Computes monolith SHA-256 hash
- Validates question count
- Creates `AggregationSettings`

**Execution Context**: First phase in orchestrator's 11-phase pipeline  
**Exit Point**: Returns config dict for Phase 1

### 1.2 Current Interaction Model

```
┌─────────────────────────────────────────────────────────────┐
│                     CURRENT STATE                           │
└─────────────────────────────────────────────────────────────┘

Phase_zero/main.py (VerifiedPipelineRunner)
├── Bootstrap (RuntimeConfig, seeds, boot checks) ✓
├── Input Verification (PDF + Questionnaire hashing) ✓
├── Exit Gates (4 gates checked) ✓
└── Calls Phase 1 ingestion
    └── run_spc_ingestion() → execute_phase_1_with_full_contract()
        └── Returns CanonPolicyPackage (CPP)

CPP → CPPAdapter → PreprocessedDocument

PreprocessedDocument → Orchestrator (from Factory)
├── Phase 0: _load_configuration()  ← NO VALIDATION OF BOOTSTRAP
│   └── Load monolith, compute hash, check question count
├── Phase 1: _ingest_document()
├── Phase 2-10: Execution phases
└── Report generation

PROBLEM: Orchestrator doesn't know if Phase_zero bootstrap succeeded!
```

### 1.3 Wiring Gaps

| Component | Phase_zero Has | Orchestrator Uses | Gap |
|-----------|----------------|-------------------|-----|
| RuntimeConfig | ✅ Loaded from env | ❌ Not injected | Critical - no mode awareness |
| Bootstrap State | ✅ `_bootstrap_failed` flag | ❌ Not checked | Critical - can proceed despite failures |
| Exit Gates | ✅ 4 gates implemented | ❌ Not validated | Critical - no contract enforcement |
| Boot Checks | ✅ 6 checks (spacy, networkx, etc) | ❌ Not aware | Warning - may use missing dependencies |
| Seed Registry | ✅ 5 seeds (python, numpy, etc) | ⚠️  Partial - only via factory | Warning - determinism not validated |
| Error Tracking | ✅ `self.errors: List[str]` | ❌ Not accessible | Warning - errors lost |

---

## 2. Detailed Wiring Analysis

### 2.1 Phase_zero Import Analysis

**File**: `src/orchestration/orchestrator.py`

```python
# Lines 34-35: Only Phase_zero imports
from canonic_phases.Phase_zero.paths import PROJECT_ROOT
from canonic_phases.Phase_zero.paths import safe_join

# Line 1326: Duplicate import inside method
from canonic_phases.Phase_zero.paths import PROJECT_ROOT
```

**Assessment**:
- ✅ Path resolution utilities imported
- ❌ NO RuntimeConfig import
- ❌ NO bootstrap module import
- ❌ NO exit_gates module import
- ❌ NO boot_checks module import

### 2.2 Orchestrator.__init__ Analysis

**Current Signature** (lines 882-892):
```python
def __init__(
    self,
    method_executor: MethodExecutor,
    questionnaire: CanonicalQuestionnaire,
    executor_config: ExecutorConfig,
    calibration_orchestrator: Any | None = None,
    resource_limits: ResourceLimits | None = None,
    resource_snapshot_interval: int = 10,
    recommendation_engine_port: RecommendationEnginePort | None = None,
    processor_bundle: Any | None = None,
) -> None:
```

**Missing Parameters**:
- `runtime_config: RuntimeConfig | None = None`
- `phase0_validation: Phase0ValidationResult | None = None`
- `bootstrap_state: BootstrapState | None = None`

### 2.3 Factory Analysis

**File**: `src/orchestration/factory.py`

**Findings**:
- ❌ Factory does NOT import any Phase_zero modules
- ❌ Factory does NOT load RuntimeConfig
- ❌ Factory does NOT validate Phase 0 bootstrap
- ⚠️  Factory creates Orchestrator without Phase 0 context

**Expected Flow** (NOT IMPLEMENTED):
```python
# factory.py - Expected but missing
from canonic_phases.Phase_zero.runtime_config import RuntimeConfig, get_runtime_config
from canonic_phases.Phase_zero.exit_gates import check_all_gates, GateResult

def build_orchestrator(...):
    # 1. Load RuntimeConfig
    runtime_config = get_runtime_config()
    
    # 2. Validate Phase 0 completion (if running after Phase_zero/main.py)
    #    OR ensure Phase 0 gates will be checked before execution
    
    # 3. Pass RuntimeConfig to Orchestrator
    orchestrator = Orchestrator(
        method_executor=executor,
        questionnaire=questionnaire,
        executor_config=config,
        runtime_config=runtime_config,  # ← MISSING
        ...
    )
    
    return orchestrator
```

### 2.4 Exit Gate Integration

**Phase_zero Implementation** (exit_gates.py):
```python
def check_all_gates(runner: Phase0Runner) -> tuple[bool, list[GateResult]]:
    """Check all 4 Phase 0 exit gates in sequence."""
    gates = [
        check_bootstrap_gate,        # Gate 1
        check_input_verification_gate,  # Gate 2
        check_boot_checks_gate,      # Gate 3
        check_determinism_gate,      # Gate 4
    ]
    # ... implementation
```

**Orchestrator Integration** (MISSING):
```python
# orchestrator.py - Expected but NOT IMPLEMENTED
def _validate_phase0_prerequisites(self) -> bool:
    """Validate Phase 0 exit gates before executing Phase 1."""
    if not hasattr(self, 'phase0_validation'):
        logger.warning("Phase 0 validation not available - assuming success")
        return True
    
    all_passed, results = self.phase0_validation
    if not all_passed:
        logger.error("Phase 0 exit gates failed", results=results)
        return False
    
    return True
```

---

## 3. Impact Analysis

### 3.1 Current Behavior (Broken Contract)

**Scenario**: Phase_zero bootstrap fails but orchestrator runs anyway

```
[Phase_zero/main.py]
1. Bootstrap: RuntimeConfig fails to load (missing env vars)
2. _bootstrap_failed = True
3. errors = ["RuntimeConfig validation failed"]
4. verify_input() returns False
5. generate_verification_manifest(success=False)
6. return False

BUT IF ORCHESTRATOR IS CALLED DIRECTLY (bypassing main.py):
[Factory → Orchestrator]
1. Factory creates Orchestrator (no Phase 0 validation)
2. Orchestrator._load_configuration() runs
3. Phase 1-10 execute DESPITE bootstrap failure
4. Results are INVALID (wrong runtime mode, missing dependencies, etc.)
```

### 3.2 Severity Assessment

| Issue | Severity | Impact |
|-------|----------|--------|
| No RuntimeConfig propagation | 🔴 **CRITICAL** | Orchestrator can't enforce PROD mode restrictions |
| No bootstrap validation | 🔴 **CRITICAL** | Invalid execution despite Phase 0 failures |
| No exit gate checking | 🔴 **CRITICAL** | Contract violations not detected |
| No boot check awareness | 🟡 **HIGH** | May use missing dependencies (e.g., spaCy, NetworkX) |
| No error propagation | 🟡 **HIGH** | Phase 0 errors lost, poor debugging |
| No determinism validation | 🟡 **MEDIUM** | Seeds may not be applied correctly |

### 3.3 Risk Scenarios

**Risk 1**: Production execution in DEV mode
- Phase_zero bootstrap sets RuntimeMode.DEV (via env var)
- Orchestrator created without knowing mode
- Phases execute with PROD-forbidden fallbacks enabled
- Results are scientifically invalid but reported as valid

**Risk 2**: Missing dependency execution
- Boot checks detect spaCy model missing
- Phase_zero logs warning but orchestrator unaware
- Phase 3 (scoring) attempts to use spaCy
- Crash or fallback to lower-quality scoring
- Results have degraded quality without clear indication

**Risk 3**: Non-deterministic execution
- Phase_zero determinism gate fails (missing numpy seed)
- Orchestrator proceeds anyway
- Phase 2 (micro questions) uses unseeded RNG
- Results are non-reproducible despite determinism claims

---

## 4. Proposed Solution

### 4.1 Design Principles

1. **Single Responsibility**: Phase_zero owns bootstrap, Orchestrator owns execution
2. **Fail-Fast**: Phase 0 failures MUST prevent orchestrator execution
3. **Explicit Contracts**: RuntimeConfig and exit gates as typed interfaces
4. **Dependency Injection**: Factory wires Phase 0 artifacts into Orchestrator
5. **Observability**: All wiring points emit structured logs

### 4.2 Architecture Changes

#### Change 1: Add RuntimeConfig to Orchestrator

**File**: `src/orchestration/orchestrator.py`

```python
# Add import
from canonic_phases.Phase_zero.runtime_config import RuntimeConfig, RuntimeMode

class Orchestrator:
    def __init__(
        self,
        method_executor: MethodExecutor,
        questionnaire: CanonicalQuestionnaire,
        executor_config: ExecutorConfig,
        runtime_config: RuntimeConfig | None = None,  # ← NEW
        calibration_orchestrator: Any | None = None,
        resource_limits: ResourceLimits | None = None,
        resource_snapshot_interval: int = 10,
        recommendation_engine_port: RecommendationEnginePort | None = None,
        processor_bundle: Any | None = None,
    ) -> None:
        """Initialize orchestrator."""
        validate_phase_definitions(self.FASES, self.__class__)
        
        self.executor = method_executor
        self._canonical_questionnaire = questionnaire
        self._monolith_data = dict(questionnaire.data)
        self.executor_config = executor_config
        self.runtime_config = runtime_config  # ← NEW: Store for phase execution
        
        # Validate runtime mode if provided
        if self.runtime_config is not None:
            logger.info(
                "orchestrator_runtime_mode",
                mode=self.runtime_config.mode.value,
                strict=self.runtime_config.is_strict_mode()
            )
        else:
            logger.warning("orchestrator_no_runtime_config")
        
        # ... rest of init
```

#### Change 2: Factory Integration

**File**: `src/orchestration/factory.py`

```python
# Add imports
from canonic_phases.Phase_zero.runtime_config import RuntimeConfig, get_runtime_config

# In factory build method
def build_orchestrator(
    questionnaire: CanonicalQuestionnaire,
    method_executor: MethodExecutor,
    executor_config: ExecutorConfig,
    **kwargs
) -> Orchestrator:
    """Build orchestrator with Phase 0 integration."""
    
    # Load RuntimeConfig (singleton, cached after first call)
    runtime_config = get_runtime_config()
    
    orchestrator = Orchestrator(
        method_executor=method_executor,
        questionnaire=questionnaire,
        executor_config=executor_config,
        runtime_config=runtime_config,  # ← NEW: Wire Phase 0 config
        **kwargs
    )
    
    return orchestrator
```

#### Change 3: Phase 0 Validation Interface

**File**: `src/orchestration/orchestrator.py`

```python
from canonic_phases.Phase_zero.exit_gates import GateResult

@dataclass
class Phase0ValidationResult:
    """Result of Phase 0 exit gate validation.
    
    Attributes:
        all_passed: True if all 4 gates passed
        gate_results: List of GateResult objects (one per gate)
        validation_time: Timestamp of validation
    """
    all_passed: bool
    gate_results: list[GateResult]
    validation_time: str
    
    def get_failed_gates(self) -> list[GateResult]:
        """Get list of failed gates."""
        return [g for g in self.gate_results if not g.passed]


class Orchestrator:
    def __init__(
        self,
        # ... existing params
        phase0_validation: Phase0ValidationResult | None = None,  # ← NEW
    ) -> None:
        """Initialize orchestrator."""
        # ... existing init
        
        # Store Phase 0 validation result
        self.phase0_validation = phase0_validation
        
        # Validate Phase 0 if result provided
        if phase0_validation is not None:
            if not phase0_validation.all_passed:
                failed = phase0_validation.get_failed_gates()
                raise RuntimeError(
                    f"Cannot initialize orchestrator: "
                    f"Phase 0 gates failed: {[g.gate_name for g in failed]}"
                )
            logger.info(
                "phase0_validation_passed",
                gates_checked=len(phase0_validation.gate_results),
                validation_time=phase0_validation.validation_time
            )
```

#### Change 4: Orchestrator Phase 0 Method Integration

**File**: `src/orchestration/orchestrator.py`

```python
def _load_configuration(self) -> dict[str, Any]:
    """FASE 0: Load configuration.
    
    This is Orchestrator's Phase 0, which validates the questionnaire monolith.
    It should NOT be confused with Phase_zero bootstrap (pre-orchestrator).
    
    Phase_zero (bootstrap) must complete BEFORE orchestrator is created.
    This method (_load_configuration) runs as the FIRST orchestrator phase.
    """
    self._ensure_not_aborted()
    instrumentation = self._phase_instrumentation[0]
    start = time.perf_counter()
    
    # Validate that Phase_zero bootstrap completed successfully
    # (This check happens if phase0_validation was passed to __init__)
    if self.phase0_validation is not None and not self.phase0_validation.all_passed:
        raise RuntimeError(
            "Phase_zero bootstrap did not complete successfully. "
            "Cannot proceed with orchestrator Phase 0."
        )
    
    # Check runtime mode restrictions
    if self.runtime_config is not None:
        mode = self.runtime_config.mode
        if mode == RuntimeMode.PROD:
            # In PROD mode, enforce strict validation
            logger.info("orchestrator_phase0_prod_mode")
        elif mode == RuntimeMode.DEV:
            logger.warning("orchestrator_phase0_dev_mode")
        else:  # EXPLORATORY
            logger.warning("orchestrator_phase0_exploratory_mode")
    
    # Existing Phase 0 logic (monolith loading)
    monolith = _normalize_monolith_for_hash(self._monolith_data)
    monolith_hash = hashlib.sha256(
        json.dumps(monolith, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        .encode("utf-8")
    ).hexdigest()
    
    # ... rest of existing logic
    
    return {
        "monolith": monolith,
        "monolith_sha256": monolith_hash,
        "micro_questions": micro_questions,
        "meso_questions": meso_questions,
        "macro_question": macro_question,
        "_aggregation_settings": aggregation_settings,
        "_runtime_mode": self.runtime_config.mode.value if self.runtime_config else None,  # ← NEW
    }
```

### 4.3 Integration Flow (After Changes)

```
┌─────────────────────────────────────────────────────────────┐
│                     TARGET STATE                            │
└─────────────────────────────────────────────────────────────┘

Phase_zero/main.py (VerifiedPipelineRunner)
├── Bootstrap (RuntimeConfig, seeds, boot checks) ✓
├── Input Verification (PDF + Questionnaire hashing) ✓
├── Exit Gates (4 gates checked) ✓
│   └── check_all_gates() → (all_passed, gate_results)
└── Calls Phase 1 ingestion (only if gates pass)
    └── run_spc_ingestion() → execute_phase_1_with_full_contract()
        └── Returns CanonPolicyPackage (CPP)

CPP → CPPAdapter → PreprocessedDocument

Factory.build_orchestrator()
├── Load RuntimeConfig (from Phase_zero) ✓
├── Validate Phase 0 completion (optional, if available) ✓
├── Create Orchestrator with:
│   ├── runtime_config=runtime_config  ← NEW
│   └── phase0_validation=validation   ← NEW (optional)
└── Return Orchestrator

Orchestrator
├── __init__ validates Phase 0 gates (if provided) ✓
│   └── Raises RuntimeError if gates failed
├── Phase 0: _load_configuration()
│   ├── Validates bootstrap completed ✓
│   ├── Enforces runtime mode ✓
│   └── Loads monolith
├── Phase 1-10: Execution phases
│   └── Can access self.runtime_config for mode-aware execution
└── Report generation

SUCCESS: Orchestrator has full Phase 0 context and enforces contracts!
```

---

## 5. Implementation Plan

### 5.1 Changes by File

#### File 1: `src/orchestration/orchestrator.py`
- [x] Add RuntimeConfig import
- [x] Add Phase0ValidationResult dataclass
- [x] Add runtime_config parameter to __init__
- [ ] Add phase0_validation parameter to __init__
- [ ] Add Phase 0 validation check in __init__
- [ ] Add runtime mode logging in __init__
- [ ] Add Phase 0 validation check in _load_configuration
- [ ] Add runtime mode to config dict return value

#### File 2: `src/orchestration/factory.py`
- [x] Add RuntimeConfig import
- [ ] Call get_runtime_config() in build method
- [ ] Pass runtime_config to Orchestrator.__init__
- [ ] (Optional) Accept phase0_validation parameter
- [ ] (Optional) Pass phase0_validation to Orchestrator.__init__

#### File 3: `tests/test_orchestrator_phase0_integration.py` (NEW)
- [ ] Create test file
- [ ] Test: Orchestrator accepts RuntimeConfig parameter
- [ ] Test: Orchestrator validates RuntimeConfig in __init__
- [ ] Test: Orchestrator fails if Phase 0 gates failed
- [ ] Test: Orchestrator logs runtime mode
- [ ] Test: _load_configuration includes runtime mode in config
- [ ] Test: Factory wires RuntimeConfig to Orchestrator

### 5.2 Testing Strategy

#### Unit Tests
1. **test_orchestrator_runtime_config_injection**
   - Create Orchestrator with RuntimeConfig
   - Verify self.runtime_config is set
   - Verify mode is logged

2. **test_orchestrator_phase0_validation_success**
   - Create Phase0ValidationResult with all_passed=True
   - Create Orchestrator with validation
   - Verify initialization succeeds

3. **test_orchestrator_phase0_validation_failure**
   - Create Phase0ValidationResult with all_passed=False
   - Attempt to create Orchestrator with validation
   - Verify RuntimeError is raised

4. **test_orchestrator_load_configuration_includes_mode**
   - Create Orchestrator with RuntimeConfig(mode=PROD)
   - Call _load_configuration()
   - Verify returned config has _runtime_mode="prod"

#### Integration Tests
5. **test_factory_wires_runtime_config**
   - Set SAAAAAA_RUNTIME_MODE=dev
   - Call factory build method
   - Verify Orchestrator has RuntimeConfig with mode=DEV

6. **test_phase0_to_orchestrator_flow**
   - Run Phase_zero bootstrap
   - Capture exit gate results
   - Create Orchestrator with results
   - Verify orchestrator has full Phase 0 context

---

## 6. Migration Path

### 6.1 Backward Compatibility

**Goal**: Ensure existing code continues to work during migration.

**Strategy**: Make all new parameters optional with sensible defaults.

```python
class Orchestrator:
    def __init__(
        self,
        # ... existing required params
        runtime_config: RuntimeConfig | None = None,  # ← OPTIONAL
        phase0_validation: Phase0ValidationResult | None = None,  # ← OPTIONAL
    ) -> None:
        """Initialize orchestrator.
        
        Args:
            runtime_config: Optional RuntimeConfig. If None, logs warning.
            phase0_validation: Optional Phase 0 validation result.
                              If None, assumes Phase 0 passed (legacy mode).
                              If provided and failed, raises RuntimeError.
        """
        # Existing code works (runtime_config=None)
        # New code can pass runtime_config
```

### 6.2 Deprecation Timeline

**Phase 1** (Current): Add optional parameters
- runtime_config is optional, None by default
- Log warning if None: "Runtime config not provided"
- No breaking changes

**Phase 2** (Next release): Deprecate None values
- Add deprecation warning if runtime_config=None
- Document that None will be unsupported in future

**Phase 3** (Future release): Make parameters required
- runtime_config becomes required
- Remove None defaults
- Update all callers to pass RuntimeConfig

---

## 7. Observability

### 7.1 Structured Logging

**Events to log**:

1. **orchestrator_runtime_config_injected**
   - mode: str (prod/dev/exploratory)
   - strict: bool
   - timestamp: ISO8601

2. **orchestrator_phase0_validation_checked**
   - all_passed: bool
   - gates_checked: int
   - failed_gates: List[str]
   - validation_time: ISO8601

3. **orchestrator_phase0_gate_failure**
   - gate_id: int
   - gate_name: str
   - reason: str
   - severity: str (critical)

4. **orchestrator_phase0_method_start**
   - monolith_hash: str (first 16 chars)
   - question_count: int
   - runtime_mode: str (if available)

### 7.2 Metrics

**Metrics to track**:
- `orchestrator_phase0_validation_passed` (counter)
- `orchestrator_phase0_validation_failed` (counter by gate_name)
- `orchestrator_runtime_mode` (gauge: prod=0, dev=1, exploratory=2)
- `orchestrator_init_duration_seconds` (histogram)

---

## 8. Conclusion

### 8.1 Summary

- **Current State**: Minimal Phase 0 → Orchestrator integration (3 imports)
- **Critical Gaps**: RuntimeConfig not propagated, exit gates not validated
- **Impact**: Contract violations possible, invalid execution not prevented
- **Solution**: Add RuntimeConfig and phase0_validation to Orchestrator.__init__
- **Strategy**: Backward-compatible optional parameters, gradual deprecation

### 8.2 Next Actions

1. ✅ Create audit report (DONE - this document)
2. [ ] Implement File 1 changes (orchestrator.py)
3. [ ] Implement File 2 changes (factory.py)
4. [ ] Write unit tests (6 tests minimum)
5. [ ] Run tests and validate changes
6. [ ] Update documentation (factory.py docstrings)
7. [ ] Create PR with changes
8. [ ] Code review and merge

### 8.3 Success Criteria

- ✅ Orchestrator has RuntimeConfig awareness
- ✅ Factory wires RuntimeConfig to Orchestrator
- ✅ Phase 0 validation failures prevent orchestrator initialization
- ✅ All tests pass (new + existing)
- ✅ No breaking changes to existing code
- ✅ Structured logging shows full Phase 0 → Orchestrator flow

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-12-12  
**Status**: Draft - Ready for Implementation
