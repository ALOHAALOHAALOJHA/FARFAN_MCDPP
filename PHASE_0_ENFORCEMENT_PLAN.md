# Phase 0 Enforcement Plan
**Objective**: Achieve 100% compliance with P00-EN v2.0 specification  
**Current Status**: 68/100 (Partial Compliance)  
**Target**: 95/100 (Full Compliance with documented deviations)

---

## Phase 1: Critical Structural Fixes (2-3 days)

### Task 1.1: Create Unified Phase 0 Orchestrator
**Priority**: 🔴 CRITICAL  
**Effort**: 4 hours  
**File**: Create `src/canonic_phases/Phase_zero/verified_pipeline_runner.py`

**Actions**:
```python
# Extract from main.py lines 106-641
class VerifiedPipelineRunner:
    """Phase 0 orchestrator implementing P00-EN v2.0 contract."""
    
    def __init__(self, plan_pdf_path, artifacts_dir, questionnaire_path):
        """P0.0: Bootstrap - Initialize runtime config, seed registry, manifest builder."""
        pass
    
    def verify_input(self) -> bool:
        """P0.1: Input Verification - Hash PDF and questionnaire."""
        pass
    
    def run_boot_checks(self) -> bool:
        """P0.2: Boot Checks - Validate dependencies in PROD/DEV mode."""
        pass
    
    def initialize_determinism(self) -> bool:
        """P0.3: Determinism - Seed all RNGs (python, numpy, quantum, etc.)."""
        pass
    
    async def run_phase_zero(self) -> bool:
        """Execute complete Phase 0 with strict exit gates."""
        # Gate 1: Bootstrap
        if not self._check_bootstrap_gate():
            return False
        
        # Gate 2: Input Verification
        if not self._check_input_verification_gate():
            return False
        
        # Gate 3: Boot Checks
        if not self._check_boot_checks_gate():
            return False
        
        # Gate 4: Determinism
        if not self._check_determinism_gate():
            return False
        
        return True  # Phase 0 SUCCESS
```

**Validation**:
- [ ] All 4 gates execute in order
- [ ] `self.errors` checked after each gate
- [ ] `_bootstrap_failed` propagates correctly
- [ ] Failure manifest generated on any gate failure

---

### Task 1.2: Implement Explicit Exit Gates
**Priority**: 🔴 CRITICAL  
**Effort**: 2 hours  
**File**: Create `src/canonic_phases/Phase_zero/exit_gates.py`

**Actions**:
```python
from dataclasses import dataclass
from typing import Protocol

class Phase0Runner(Protocol):
    """Protocol for Phase 0 runner interface."""
    errors: list[str]
    _bootstrap_failed: bool
    runtime_config: RuntimeConfig | None
    seed_snapshot: dict[str, int]

@dataclass
class GateResult:
    """Result of a Phase 0 exit gate check."""
    passed: bool
    gate_name: str
    reason: str | None = None

def check_bootstrap_gate(runner: Phase0Runner) -> GateResult:
    """Gate 1: Bootstrap configuration loaded successfully."""
    if runner._bootstrap_failed:
        return GateResult(False, "bootstrap", "Bootstrap failed during init")
    if runner.errors:
        return GateResult(False, "bootstrap", f"Errors present: {runner.errors}")
    if runner.runtime_config is None:
        return GateResult(False, "bootstrap", "Runtime config not loaded")
    return GateResult(True, "bootstrap")

def check_input_verification_gate(runner: Phase0Runner) -> GateResult:
    """Gate 2: Input files hashed and verified."""
    if not hasattr(runner, 'input_pdf_sha256'):
        return GateResult(False, "input_verification", "PDF not hashed")
    if not hasattr(runner, 'questionnaire_sha256'):
        return GateResult(False, "input_verification", "Questionnaire not hashed")
    if runner.errors:
        return GateResult(False, "input_verification", f"Errors: {runner.errors}")
    return GateResult(True, "input_verification")

def check_boot_checks_gate(runner: Phase0Runner) -> GateResult:
    """Gate 3: Boot checks passed (or warned in DEV)."""
    if runner.errors:
        return GateResult(False, "boot_checks", f"Errors: {runner.errors}")
    return GateResult(True, "boot_checks")

def check_determinism_gate(runner: Phase0Runner) -> GateResult:
    """Gate 4: Deterministic seeds applied to all RNGs."""
    if not hasattr(runner, 'seed_snapshot'):
        return GateResult(False, "determinism", "Seed snapshot not created")
    
    REQUIRED_SEEDS = ["python", "numpy"]
    missing = [s for s in REQUIRED_SEEDS if runner.seed_snapshot.get(s) is None]
    if missing:
        return GateResult(False, "determinism", f"Missing seeds: {missing}")
    
    if runner.errors:
        return GateResult(False, "determinism", f"Errors: {runner.errors}")
    
    return GateResult(True, "determinism")
```

**Validation**:
- [ ] Each gate returns `GateResult` with clear pass/fail
- [ ] Gates are **independent** (can be tested in isolation)
- [ ] Failure reasons are actionable for operators

---

### Task 1.3: Fix Determinism Sequencing
**Priority**: 🔴 CRITICAL  
**Effort**: 1 hour  
**Files**: Modify `verified_pipeline_runner.py`

**Current Issue**: Seeding happens in `__init__` (before input verification and boot checks).

**Fix**:
```python
def __init__(self, ...):
    # ... config, paths, manifest ...
    self.seed_registry = get_global_seed_registry()
    self.seed_snapshot = {}  # Initialize empty
    # DO NOT call _initialize_determinism_context() here

async def run_phase_zero(self) -> bool:
    # ... Gates 1-3 ...
    
    # P0.3: Determinism Context (AFTER boot checks pass)
    self.seed_snapshot = self._initialize_determinism_context()
    
    # Gate 4: Validate seeding succeeded
    if not self._check_determinism_gate():
        return False
    
    return True
```

**Validation**:
- [ ] Seeding happens **after** boot checks
- [ ] `seed_snapshot` populated before Gate 4
- [ ] Python and NumPy RNGs are seeded before Phase 1

---

## Phase 2: Module Consolidation (1 day)

### Task 2.1: Consolidate Determinism Modules
**Priority**: 🟡 HIGH  
**Effort**: 3 hours

**Actions**:
1. Create `src/canonic_phases/Phase_zero/determinism.py`
2. Merge:
   - `determinism_helpers.py` → `determinism.py` (seed derivation)
   - `seed_factory.py` → `determinism.py` (seed generation)
   - `deterministic_execution.py` → Delete (unused context manager)
3. Keep `orchestration/seed_registry.py` as global registry

**Result**: Single source of truth for all determinism logic.

---

### Task 2.2: Consolidate Contract Files
**Priority**: 🟡 HIGH  
**Effort**: 2 hours

**Actions**:
1. Create `src/canonic_phases/Phase_zero/contracts/`
2. Move:
   - `contracts.py` → `contracts/__init__.py`
   - `contracts_runtime.py` → `contracts/runtime.py`
   - `core_contracts.py` → `contracts/core.py`
   - `enhanced_contracts.py` → `contracts/enhanced.py`

---

## Phase 3: Enhanced Validation (1 day)

### Task 3.1: Add Comprehensive Seed Validation
**Priority**: 🟡 HIGH  
**Effort**: 2 hours

**Current**: Only validates `python` seed.  
**Fix**: Validate all 5 seeds from registry.

```python
def _validate_all_seeds(self, seeds: dict[str, int]) -> bool:
    """Validate all required seeds are present."""
    REQUIRED_SEEDS = ["python", "numpy", "quantum", "neuromorphic", "meta_learner"]
    missing = [s for s in REQUIRED_SEEDS if seeds.get(s) is None]
    
    if missing:
        error_msg = f"Missing required seeds: {missing}"
        self.log_claim("error", "determinism", error_msg)
        self.errors.append(error_msg)
        self._bootstrap_failed = True
        return False
    
    return True
```

**Validation**:
- [ ] Test with incomplete seed registry
- [ ] Verify error messages are actionable
- [ ] Confirm `_bootstrap_failed` set correctly

---

### Task 3.2: Add Hash Validation (Optional)
**Priority**: 🟢 MEDIUM  
**Effort**: 1 hour

**Enhancement**: Compare computed hashes against known-good values.

```python
def verify_input(self, expected_hashes: dict[str, str] | None = None) -> bool:
    """Verify input files and optionally validate against expected hashes."""
    # ... existing hash computation ...
    
    if expected_hashes:
        if self.input_pdf_sha256 != expected_hashes.get("pdf"):
            self.errors.append(f"PDF hash mismatch")
            return False
        if self.questionnaire_sha256 != expected_hashes.get("questionnaire"):
            self.errors.append(f"Questionnaire hash mismatch")
            return False
    
    return True
```

---

## Phase 4: Documentation & Testing (1 day)

### Task 4.1: Add Phase 0 Unit Tests
**Priority**: 🟡 HIGH  
**Effort**: 4 hours  
**File**: Create `tests/canonic_phases/test_phase_zero.py`

**Tests Required**:
```python
def test_bootstrap_gate_fails_on_missing_config():
    """Gate 1 must fail if runtime config not loaded."""
    runner = VerifiedPipelineRunner(...)
    runner.runtime_config = None
    result = check_bootstrap_gate(runner)
    assert not result.passed

def test_input_verification_gate_fails_on_missing_hash():
    """Gate 2 must fail if PDF not hashed."""
    runner = VerifiedPipelineRunner(...)
    delattr(runner, 'input_pdf_sha256')
    result = check_input_verification_gate(runner)
    assert not result.passed

def test_determinism_gate_fails_on_missing_python_seed():
    """Gate 4 must fail if python seed not applied."""
    runner = VerifiedPipelineRunner(...)
    runner.seed_snapshot = {"numpy": 12345}  # Missing python
    result = check_determinism_gate(runner)
    assert not result.passed

def test_phase_zero_full_success():
    """Phase 0 must succeed when all gates pass."""
    runner = VerifiedPipelineRunner(...)
    success = await runner.run_phase_zero()
    assert success
    assert runner.errors == []
    assert not runner._bootstrap_failed
```

---

### Task 4.2: Update README
**Priority**: 🟢 MEDIUM  
**Effort**: 1 hour

**Additions to README.md**:
```markdown
## Phase 0: Pre-Execution Validation

Phase 0 implements strict validation with 4 exit gates:

1. **Bootstrap** (`P0.0`) - Runtime config, seed registry, manifest builder
2. **Input Verification** (`P0.1`) - SHA-256 hashing of PDF + questionnaire
3. **Boot Checks** (`P0.2`) - Dependency validation (PROD: fatal, DEV: warn)
4. **Determinism** (`P0.3`) - RNG seeding with mandatory python seed

**Exit Condition**: `self.errors` MUST be empty ∧ `_bootstrap_failed` = False

See `src/canonic_phases/Phase_zero/README.md` for detailed architecture.
```

---

## Success Criteria

### Objective Metrics
- [ ] **100% gate coverage**: All 4 gates explicitly checked
- [ ] **Zero test failures**: `pytest tests/canonic_phases/test_phase_zero.py -v`
- [ ] **Linting passes**: `ruff check src/canonic_phases/Phase_zero/`
- [ ] **Type checking**: `mypy src/canonic_phases/Phase_zero/ --strict`

### Specification Alignment
- [ ] Section 3.1 (Bootstrap): 95/100 (current: 85/100)
- [ ] Section 3.2 (Input Verification): 90/100 (current: 75/100)
- [ ] Section 3.3 (Boot Checks): 95/100 (current: 90/100)
- [ ] Section 3.4 (Determinism): 90/100 (current: 70/100)
- [ ] Section 4.1 (Exit Conditions): 95/100 (current: 40/100)

### Operator Experience
- [ ] Clear error messages on each gate failure
- [ ] Manifest correctly shows which gate failed
- [ ] No ambiguous "maybe it worked" states

---

## Timeline

| Phase | Duration | Blockers | Dependencies |
|-------|----------|----------|--------------|
| **Phase 1** (Critical) | 2-3 days | None | Requires specification review |
| **Phase 2** (Consolidation) | 1 day | Phase 1 complete | Refactored orchestrator |
| **Phase 3** (Validation) | 1 day | None | Can run in parallel with Phase 2 |
| **Phase 4** (Docs/Tests) | 1 day | Phase 1 complete | Full implementation ready |

**Total**: 5-6 days (1 sprint)

---

## Risk Mitigation

### Risk 1: Breaking Existing Pipeline
**Likelihood**: HIGH  
**Impact**: CRITICAL  
**Mitigation**:
- Keep `main.py` unchanged initially
- Create `verified_pipeline_runner.py` as new orchestrator
- Gradually migrate logic with feature flag: `USE_PHASE0_ORCHESTRATOR=true`

### Risk 2: Incomplete Seed Registry
**Likelihood**: MEDIUM  
**Impact**: MODERATE  
**Mitigation**:
- Add validation tests for seed registry before migration
- Document which components actually use quantum/neuromorphic/meta_learner seeds
- Add warnings if seeds are unused

---

## Approval Checklist

- [ ] Specification reviewed by core team
- [ ] Architecture changes approved
- [ ] Test plan reviewed
- [ ] Rollback plan documented
- [ ] Monitoring in place for Phase 0 failures

**Approved By**: _________________  
**Date**: _________________
