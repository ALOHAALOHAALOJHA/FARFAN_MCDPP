"""
Phase 0 Output Contract
=======================

**Contract ID:** PHASE0-OUTPUT-CONTRACT-001
**Version:** 1.0.0
**Date:** 2026-01-13
**Status:** ACTIVE

Overview
--------
Phase 0 produces a **validated, canonical execution environment** ready for
Phase 1 to begin document ingestion and analysis. The primary output is the
`CanonicalInput` dataclass containing all validated inputs and metadata.

Primary Output: CanonicalInput
-------------------------------
The `CanonicalInput` dataclass is the main product of Phase 0. It contains:

**Identity Fields**
- `document_id: str` - Unique identifier for the policy document
- `run_id: str` - Unique identifier for this pipeline execution

**Input Artifacts (Validated & Immutable)**
- `pdf_path: Path` - Validated path to policy document PDF
- `pdf_sha256: str` - SHA-256 hash of PDF (64-char hex string)
- `pdf_size_bytes: int` - File size in bytes (must be > 0)
- `pdf_page_count: int` - Number of pages in PDF (must be > 0)

**Questionnaire Artifacts**
- `questionnaire_path: Path` - Validated path to questionnaire JSON
- `questionnaire_sha256: str` - SHA-256 hash of questionnaire (64-char hex)

**Metadata**
- `created_at: datetime` - UTC timestamp of validation
- `phase0_version: str` - Schema version (e.g., "1.0.0")

**Validation Results**
- `validation_passed: bool` - Must be True for valid output
- `validation_errors: list[str]` - Empty if validation passed
- `validation_warnings: list[str]` - Non-critical warnings (may be non-empty)

CanonicalInput Definition
--------------------------
```python
@dataclass
class CanonicalInput:
    # Identity
    document_id: str
    run_id: str
    
    # Input artifacts (immutable, validated)
    pdf_path: Path
    pdf_sha256: str
    pdf_size_bytes: int
    pdf_page_count: int
    
    # Questionnaire (required)
    questionnaire_path: Path
    questionnaire_sha256: str
    
    # Metadata
    created_at: datetime
    phase0_version: str
    
    # Validation results
    validation_passed: bool
    validation_errors: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)
```

Secondary Output: WiringComponents
-----------------------------------
Phase 0 also produces `WiringComponents`, a container with all initialized
pipeline components:

```python
@dataclass
class WiringComponents:
    provider: QuestionnaireResourceProvider
    signal_client: SignalClient
    signal_registry: SignalRegistry
    executor_config: ExecutorConfig
    factory: CoreModuleFactory
    arg_router: ExtendedArgRouter
    class_registry: dict[str, type]
    validator: WiringValidator
    calibration_orchestrator: CalibrationOrchestrator | None
    flags: WiringFeatureFlags
    init_hashes: dict[str, str]
```

Tertiary Output: EnforcementMetrics
------------------------------------
Resource usage metrics collected during Phase 0:

```python
@dataclass
class EnforcementMetrics:
    peak_memory_mb: float
    total_cpu_seconds: float
    file_descriptors_used: int
    watchdog_triggers: int
    execution_time_seconds: float
```

Output Postconditions
---------------------
Phase 0 guarantees the following postconditions:

**POST-001: Validation Success**
```
∀ output: output.validation_passed == True
```

**POST-002: PDF Integrity**
```
∀ output:
    output.pdf_path.exists() ∧
    output.pdf_size_bytes > 0 ∧
    output.pdf_page_count > 0 ∧
    len(output.pdf_sha256) == 64 ∧
    hash(pdf_path) == output.pdf_sha256
```

**POST-003: Questionnaire Integrity**
```
∀ output:
    output.questionnaire_path.exists() ∧
    len(output.questionnaire_sha256) == 64 ∧
    is_valid_json(questionnaire_path)
```

**POST-004: Timestamp Validity**
```
∀ output:
    output.created_at.tzinfo == timezone.utc ∧
    output.created_at <= current_time
```

**POST-005: No Critical Errors**
```
∀ output:
    output.validation_errors == [] ∨
    output.validation_passed == False
```

**POST-006: Component Initialization**
```
∀ wiring_components:
    wiring_components.provider is not None ∧
    wiring_components.signal_client is not None ∧
    wiring_components.factory is not None ∧
    wiring_components.arg_router is not None ∧
    len(wiring_components.class_registry) > 0
```

Determinism Guarantees
----------------------
Phase 0 guarantees bitwise-identical outputs for identical inputs:

**DET-001: Hash Stability**
```
∀ input1, input2 where input1 == input2:
    hash(phase0_output(input1)) == hash(phase0_output(input2))
```

**DET-002: Timestamp Exclusion**
```
When comparing outputs for determinism:
    exclude: created_at, execution_time_seconds
    include: all other fields
```

**DET-003: Seed Consistency**
```
∀ executions with same base_seed:
    derived_seeds identical across runs
```

Resource Guarantees
-------------------
If resource enforcement is enabled (`ENFORCE_RESOURCES=true`):

**RES-001: Memory Bounded**
```
∀ execution:
    memory_used ≤ RLIMIT_AS (default: 2048 MB)
```

**RES-002: CPU Time Bounded**
```
∀ execution:
    cpu_time ≤ RLIMIT_CPU (default: 300 seconds)
```

**RES-003: File Descriptors Bounded**
```
∀ execution:
    open_files ≤ RLIMIT_NOFILE (default: 1024)
```

Handoff Protocol to Phase 1
----------------------------
Phase 0 hands off to Phase 1 by:

1. **Producing CanonicalInput**
   - All fields validated
   - All hashes computed
   - All paths verified

2. **Producing WiringComponents**
   - All components initialized
   - All dependencies resolved
   - All contracts bound

3. **Logging Handoff Event**
   ```json
   {
     "event": "phase0_complete",
     "document_id": "...",
     "run_id": "...",
     "validation_passed": true,
     "phase0_version": "1.0.0",
     "handoff_time": "2026-01-13T00:00:00Z"
   }
   ```

4. **Setting Phase 1 Preconditions**
   - Configuration frozen (immutable)
   - Resource limits active
   - Determinism enforced
   - Logging initialized

Phase 1 Requirements
---------------------
Phase 1 MUST:
1. Accept `CanonicalInput` as its input contract
2. NOT modify any Phase 0 configuration
3. Respect resource limits set by Phase 0
4. Use deterministic seeds from Phase 0
5. Log using structured logger from Phase 0

Phase 1 MAY:
1. Add Phase 1-specific configuration
2. Create Phase 1-specific resources
3. Extend (but not override) Phase 0 initialization

Validation of Output
--------------------
Phase 0 validates its own output before handoff:

```python
class Phase0ValidationContract(PhaseContract[Phase0Input, CanonicalInput]):
    def validate_output(self, output: CanonicalInput) -> ContractValidationResult:
        errors = []
        
        # POST-001: Validation must pass
        if not output.validation_passed:
            errors.append("validation_passed must be True")
        
        # POST-002: PDF integrity
        if not output.pdf_path.exists():
            errors.append("pdf_path must exist")
        if output.pdf_size_bytes <= 0:
            errors.append("pdf_size_bytes must be > 0")
        if output.pdf_page_count <= 0:
            errors.append("pdf_page_count must be > 0")
        if len(output.pdf_sha256) != 64:
            errors.append("pdf_sha256 must be 64 characters")
        
        # POST-003: Questionnaire integrity
        if not output.questionnaire_path.exists():
            errors.append("questionnaire_path must exist")
        if len(output.questionnaire_sha256) != 64:
            errors.append("questionnaire_sha256 must be 64 characters")
        
        # POST-004: Timestamp validity
        if output.created_at.tzinfo != timezone.utc:
            errors.append("created_at must be UTC")
        
        # POST-005: No errors if validation passed
        if output.validation_passed and output.validation_errors:
            errors.append("validation_errors must be empty if validation_passed")
        
        return ContractValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=[]
        )
```

Failure Modes
-------------
Phase 0 output contract is violated if:
1. `validation_passed == False` (validation failed)
2. `pdf_path` does not exist
3. `pdf_sha256` does not match actual hash
4. `questionnaire_path` does not exist
5. Any postcondition is violated

On contract violation, Phase 0 will:
1. Log violation details
2. Raise `DataContractError`
3. Terminate execution
4. Return exit code 1

Compatibility with Phase 1
---------------------------
This contract is compatible with Phase 1 input contract version ≥ 1.0.0.

**Compatibility Matrix:**
| Phase 0 Output | Phase 1 Input | Compatible |
|----------------|---------------|------------|
| v1.0.0         | v1.0.0        | ✓          |
| v1.0.0         | v1.1.0        | ✓          |
| v1.1.0         | v1.0.0        | ?          |

Related Contracts
-----------------
- `phase0_input_contract.py` - Phase 0 user inputs
- `phase0_mission_contract.py` - Phase 0 internal execution
- Phase 1 Input Contract (in Phase_1/ directory)

References
----------
- phase0_40_00_input_validation.py (CanonicalInput definition)
- phase0_90_02_bootstrap.py (WiringComponents definition)
- phase0_30_00_resource_controller.py (EnforcementMetrics definition)
- PHASE_0_MANIFEST.json

---
**END OF CONTRACT**
"""
