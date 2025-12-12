# Phase 1 Circuit Breaker - Aggressively Preventive Failure Protection

## Overview

The Phase 1 Circuit Breaker is an aggressively preventive failure protection system designed to ensure Phase 1 can ONLY execute when ALL critical conditions are met. Unlike graceful degradation, this system fails fast and loud when problems are detected.

## Design Philosophy

### Aggressively Preventive ≠ Graceful Degradation

**Traditional Graceful Degradation:**
- Attempts to continue with reduced functionality when dependencies are missing
- May produce partial or degraded results
- Can violate constitutional invariants silently

**Our Aggressively Preventive Approach:**
- Validates ALL dependencies BEFORE execution starts
- Fails immediately if any critical condition is not met
- NO PARTIAL EXECUTION - either complete success or complete failure
- Clear, actionable error messages

### Circuit Breaker States

```
┌─────────┐
│ CLOSED  │ ← All checks passed, normal operation
└────┬────┘
     │ Failure detected
     ▼
┌─────────┐
│  OPEN   │ ← Critical failure, execution BLOCKED
└────┬────┘
     │ Manual recovery attempt
     ▼
┌──────────┐
│HALF-OPEN │ ← Testing if conditions restored (future use)
└──────────┘
```

## Components

### 1. Pre-flight Checks

Executed BEFORE Phase 1 starts:

#### Python Version Check
- **Requirement**: Python 3.10+
- **Failure**: CRITICAL - execution blocked
- **Fix**: Upgrade Python

#### Critical Dependencies
- **langdetect**: Language detection (SP0)
- **spaCy**: NLP processing (SP1/SP2/SP3)
- **PyMuPDF (fitz)**: PDF extraction (SP0/SP1)
- **pydantic**: Contract validation
- **numpy**: Numerical operations

All must be present and importable.

#### Optional Dependencies (Warnings Only)
- **SISAS**: Signal enrichment system
- **derek_beach**: Causal analysis (SP5/SP7)
- **teoria_cambio**: DAG validation (SP6)

Missing optional dependencies generate warnings but don't block execution.

#### Resource Checks
- **Memory**: ≥2GB available (CRITICAL)
- **Disk Space**: ≥1GB free (CRITICAL)
- **CPU**: Monitored for warnings if >80% usage

#### File System
- Write permissions in working directory (CRITICAL)

### 2. Subphase Checkpoints

Constitutional invariant validation at critical boundaries:

#### SP4 Checkpoint (PA×DIM Segmentation)
Validates:
- Exactly 60 chunks generated
- All chunks are `Chunk` instances
- All chunk_ids are unique
- Complete PA×DIM coverage

**Why Critical**: SP4 establishes the constitutional 60-chunk invariant. If this fails, all downstream processing is invalid.

#### SP11 Checkpoint (SmartChunk Generation)
Validates:
- Exactly 60 SmartChunks generated
- All are `SmartChunk` instances
- All chunk_ids are unique
- All have required enrichment metadata (causal_graph, temporal_markers)

**Why Critical**: SP11 is the final transformation before validation. Must maintain the 60-chunk invariant with full enrichment.

#### SP13 Checkpoint (Integrity Validation)
Validates:
- Validation status is "VALID"
- Chunk count is exactly 60
- Zero violations detected

**Why Critical**: SP13 is the validation gate. If this fails, the entire Phase 1 output is invalid.

## Usage

### Basic Usage

```python
from canonic_phases.Phase_one.phase1_spc_ingestion_full import (
    execute_phase_1_with_full_contract
)
from canonic_phases.Phase_one.phase0_input_validation import CanonicalInput

# Circuit breaker is automatically invoked
cpp = execute_phase_1_with_full_contract(canonical_input)
```

### Manual Pre-flight Check

```python
from canonic_phases.Phase_one.phase1_circuit_breaker import (
    run_preflight_check,
    get_circuit_breaker
)

# Run pre-flight check
result = run_preflight_check()

if result.passed:
    print("✓ All checks passed")
else:
    # Get diagnostic report
    cb = get_circuit_breaker()
    print(cb.get_diagnostic_report())
    
    # See critical failures
    for failure in result.critical_failures:
        print(f"✗ {failure}")
```

### Checkpoint Validation

```python
from canonic_phases.Phase_one.phase1_circuit_breaker import SubphaseCheckpoint

checkpoint = SubphaseCheckpoint()

# Validate output at a subphase boundary
passed, errors = checkpoint.validate_checkpoint(
    subphase_num=4,
    output=pa_dim_chunks,
    expected_type=list,
    validators=[
        lambda x: (len(x) == 60, "Must have exactly 60 chunks"),
        lambda x: (all(isinstance(c, Chunk) for c in x), "All must be Chunk instances"),
    ]
)

if not passed:
    raise Phase1FatalError(f"SP4 checkpoint failed: {errors}")
```

## Error Messages

### Example: Missing Dependency

```
✗ PHASE 1 FATAL ERROR: Phase 1 pre-flight checks FAILED. 1 critical failures detected.
Circuit breaker is OPEN. Execution cannot proceed.

================================================================================
PHASE 1 CIRCUIT BREAKER - DIAGNOSTIC REPORT
================================================================================
State: OPEN
Overall Result: FAIL

DEPENDENCY CHECKS:
  ✓ python (v3.12)
  ✗ langdetect
      Error: ModuleNotFoundError: No module named 'langdetect'
      Fix: Install with: pip install langdetect
  ✓ spacy (v3.7.2)
  ✓ fitz (v1.23.8)

CRITICAL FAILURES:
  ✗ Missing critical dependency: langdetect (Language detection for SP0)
================================================================================
```

### Example: Insufficient Memory

```
✗ PHASE 1 FATAL ERROR: Phase 1 pre-flight checks FAILED. 1 critical failures detected.

RESOURCE CHECKS:
  ✗ memory: 1.20 GB available (need 2.00 GB)
  ✓ disk: 50.00 GB available (need 1.00 GB)

CRITICAL FAILURES:
  ✗ Insufficient memory: 1.20 GB available, 2.00 GB required
```

### Example: Checkpoint Failure

```
✗ PHASE 1 FATAL ERROR: SP4 CHECKPOINT FAILED: Constitutional invariant violated.
Errors: ['SP4: Must have exactly 60 chunks, got 59']
```

## Diagnostic Report

The circuit breaker generates a comprehensive diagnostic report:

```
================================================================================
PHASE 1 CIRCUIT BREAKER - DIAGNOSTIC REPORT
================================================================================
State: CLOSED
Timestamp: 2025-12-11T04:30:15.123456Z
Overall Result: PASS

SYSTEM INFORMATION:
  platform: Linux-5.15.0-1034-azure-x86_64-with-glibc2.35
  python_version: 3.12.0
  cpu_count: 4
  total_memory_gb: 16.0

DEPENDENCY CHECKS:
  ✓ python (v3.12)
  ✓ langdetect (v1.0.9)
  ✓ spacy (v3.7.2)
  ✓ fitz (v1.23.8)
  ✓ pydantic (v2.5.0)
  ✓ numpy (v1.26.4)
  ⚠ SISAS
      Error: ModuleNotFoundError: No module named 'cross_cutting_infrastrucuture'
      Fix: Install SISAS infrastructure

RESOURCE CHECKS:
  ✓ memory: 8.45 GB available (need 2.00 GB)
  ✓ disk: 50.23 GB available (need 1.00 GB)
  ✓ cpu: 15.2% usage (80.0 percent available)

WARNINGS:
  ⚠ Optional dependency missing: SISAS (Signal enrichment system).
     Some features will be limited.
================================================================================
```

## Troubleshooting

### Circuit Breaker is OPEN - Dependencies Missing

**Symptom**: Phase 1 fails immediately with "Circuit breaker is OPEN"

**Solution**:
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install specific missing dependency
pip install langdetect
pip install spacy
pip install PyMuPDF
```

### Circuit Breaker is OPEN - Insufficient Memory

**Symptom**: Error about insufficient memory

**Solutions**:
1. Close other applications to free memory
2. Increase system memory
3. Run on a machine with more RAM

### Circuit Breaker is OPEN - Insufficient Disk Space

**Symptom**: Error about insufficient disk space

**Solutions**:
1. Free up disk space
2. Change working directory to location with more space

### Checkpoint Failure at SP4

**Symptom**: "SP4 CHECKPOINT FAILED: Must have exactly 60 chunks"

**Root Causes**:
- Document doesn't have enough content for 60-way segmentation
- PA×DIM segmentation algorithm bug
- Input validation bypassed

**Solution**:
- Check document size and content
- Review Phase 0 validation
- Check SP4 implementation logs

### Checkpoint Failure at SP11

**Symptom**: "SP11 CHECKPOINT FAILED: All chunks must have causal_graph"

**Root Causes**:
- SP5 (causal extraction) failed silently
- SmartChunk construction incomplete

**Solution**:
- Check SP5 logs for causal extraction issues
- Verify derek_beach availability
- Check SP11 implementation

### Checkpoint Failure at SP13

**Symptom**: "SP13 CHECKPOINT FAILED: Validation status must be VALID"

**Root Causes**:
- Constitutional invariant violated in earlier subphases
- Duplicate chunk_ids
- Missing PA×DIM combinations

**Solution**:
- Review SP4 and SP11 checkpoint results
- Check for subphase failures that were ignored
- Verify chunk_id generation logic

## Benefits

### 1. Eliminates Silent Failures
- No more "it ran but produced garbage"
- All failures are loud and clear
- Constitutional invariants enforced

### 2. Clear Error Messages
- Specific dependency names
- Version information
- Installation commands
- Remediation steps

### 3. Resource Protection
- Won't start if insufficient resources
- Prevents OOM kills
- Prevents disk full errors mid-execution

### 4. Constitutional Invariant Enforcement
- 60-chunk invariant verified at multiple points
- PA×DIM coverage validated
- Enrichment completeness checked

### 5. Diagnostic Information
- Comprehensive system information
- Dependency versions
- Resource availability
- Failure history

## Integration with Phase Protocol

The circuit breaker integrates seamlessly with Phase 1's contract-based architecture:

```python
class Phase1SPCIngestionFullContract:
    def __init__(self):
        # ...
        self.checkpoint_validator = SubphaseCheckpoint()
    
    def run(self, canonical_input: CanonicalInput) -> CanonPolicyPackage:
        # 1. Pre-flight checks (circuit breaker)
        preflight_result = run_preflight_check()
        if not preflight_result.passed:
            raise Phase1FatalError("Pre-flight checks failed")
        
        # 2. Execute subphases
        for sp in range(16):
            output = self._execute_subphase(sp, ...)
            
            # 3. Checkpoint validation at critical boundaries
            if sp in [4, 11, 13]:
                passed, errors = self.checkpoint_validator.validate_checkpoint(...)
                if not passed:
                    raise Phase1FatalError(f"SP{sp} checkpoint failed")
```

## Future Enhancements

### HALF-OPEN State
Implement recovery testing:
- After a failure, test if conditions have been restored
- Gradually resume operation if tests pass
- Fall back to OPEN if tests fail

### Adaptive Resource Requirements
- Adjust memory/disk requirements based on document size
- Dynamic threshold calculation
- Predictive resource estimation

### Failure History
- Track failure patterns
- Identify recurring issues
- Generate failure statistics

### Auto-Remediation
- Attempt to install missing dependencies
- Suggest system configuration changes
- Provide detailed recovery procedures

## References

- [Martin Fowler - Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- Phase 1 FORCING ROUTE specification
- Constitutional Invariants documentation
- Phase Contract Protocol documentation
