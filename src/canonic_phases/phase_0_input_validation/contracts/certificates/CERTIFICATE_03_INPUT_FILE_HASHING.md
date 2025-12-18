# Certificate 03: Input File Hashing

**Status**: ACTIVE  
**Timestamp**: 2025-12-18  
**Verification**: tests/phase_0/test_exit_gates.py::test_input_verification_gate  
**Evidence**: phase0_main.py, phase0_verified_pipeline_runner.py

## Assertion

Phase 0 computes SHA-256 hashes of input PDF and questionnaire files, ensuring
reproducible input validation and audit trail.

## Verification Method

Test validates InputContract hash format (64 hex characters) and integrity.

## Audit Trail

- phase0_main.py: Hash computation in VerifiedPipelineRunner
- phase0_verified_pipeline_runner.py: Input file hashing
- InputContract: Validates hash format and integrity
