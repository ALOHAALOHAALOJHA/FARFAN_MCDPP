"""
Phase 0 Input Contract
======================

**Contract ID:** PHASE0-INPUT-CONTRACT-001
**Version:** 1.0.0
**Date:** 2026-01-13
**Status:** ACTIVE

Overview
--------
Phase 0 is the **initial phase** of the F.A.R.F.A.N pipeline and therefore
receives NO inputs from any previous phase. Instead, Phase 0 receives inputs
directly from the **user/external system**.

Input Sources
-------------
Phase 0 inputs originate from:
1. **User-provided paths** to documents and configuration files
2. **Environment variables** for runtime configuration
3. **System resources** (filesystem, memory, CPU)

User-Provided Inputs
--------------------
The following inputs must be provided by the user/calling system:

1. **PDF Document Path**
   - Type: Path (filesystem path)
   - Required: Yes
   - Description: Path to the policy document PDF to be analyzed
   - Validation: Must exist, be readable, and be a valid PDF
   - Example: `/data/input/policy_document.pdf`

2. **Run Identifier**
   - Type: str
   - Required: Yes
   - Description: Unique identifier for this pipeline execution
   - Validation: Must be filesystem-safe, no special characters
   - Example: `run_2026_01_13_001`

3. **Questionnaire Path** (Optional)
   - Type: Path | None
   - Required: No
   - Description: Path to questionnaire monolith JSON
   - Default: Canonical questionnaire from package
   - Example: `/data/config/custom_questionnaire.json`

Environment Variables
---------------------
Runtime configuration via environment variables:

1. **SAAAAAA_RUNTIME_MODE**
   - Values: `prod` | `dev` | `exploratory`
   - Default: `prod`
   - Description: Execution mode controlling enforcement strictness

2. **ENFORCE_RESOURCES**
   - Values: `true` | `false`
   - Default: `false`
   - Description: Enable kernel-level resource enforcement

3. **RESOURCE_MEMORY_MB**
   - Type: int
   - Default: 2048
   - Description: Memory limit in megabytes

4. **RESOURCE_CPU_SECONDS**
   - Type: int
   - Default: 300
   - Description: CPU time limit in seconds

No Phase-to-Phase Input Contract
---------------------------------
**IMPORTANT:** Phase 0 does NOT implement an inter-phase input contract
because there is no previous phase. The concept of phase-to-phase data
transfer only applies starting from Phase 1 → Phase 2.

Dataclass Definition
--------------------
See `phase0_40_00_input_validation.py` for the complete `Phase0Input`
dataclass definition:

```python
@dataclass
class Phase0Input:
    pdf_path: Path
    run_id: str
    questionnaire_path: Path | None = None
```

Validation Rules
----------------
1. `pdf_path` must exist on filesystem
2. `pdf_path` must be readable by current process
3. `pdf_path` must be a valid PDF (checked via PyMuPDF)
4. `run_id` must be non-empty and filesystem-safe
5. `run_id` must not contain SQL injection patterns
6. `questionnaire_path` (if provided) must exist and be valid JSON

Security Constraints
--------------------
Per 2026-01-07 security hardening:
- Path traversal detection (reject '..')
- Null byte injection prevention (reject '\\x00')
- SQL injection pattern detection
- Strict type validation at construction time

Contract Verification
---------------------
Input validation is performed by:
- `Phase0InputValidator` (pydantic-based runtime validation)
- `phase0_40_00_input_validation.py` module
- `phase0_50_00_boot_checks.py` pre-flight checks

Failure Modes
-------------
If inputs are invalid, Phase 0 will:
1. Raise `DataContractError` with explicit error message
2. Log validation failure details
3. Terminate execution immediately (fail-fast)
4. Return exit code 1

Related Contracts
-----------------
- `phase0_mission_contract.py` - Defines Phase 0 internal execution
- `phase0_output_contract.py` - Defines Phase 0 output to Phase 1

References
----------
- PHASE_0_MANIFEST.json
- phase0_40_00_input_validation.py
- GLOBAL_NAMING_POLICY.md

---
**END OF CONTRACT**
"""
