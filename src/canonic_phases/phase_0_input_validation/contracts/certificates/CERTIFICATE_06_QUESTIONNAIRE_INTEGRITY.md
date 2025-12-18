# Certificate 06: Questionnaire Integrity

**Status**: ACTIVE  
**Timestamp**: 2025-12-18  
**Verification**: tests/phase_0/test_exit_gates.py::test_questionnaire_integrity_gate  
**Evidence**: phase0_exit_gates.py, phase0_bootstrap.py

## Assertion

Phase 0 validates questionnaire SHA-256 hash against known-good reference,
ensuring questionnaire definition has not been corrupted.

## Verification Method

Test validates Gate 5 (Questionnaire Integrity) passes with matching hash.

## Audit Trail

- phase0_exit_gates.py: Gate 5 (Questionnaire Integrity) validation
- phase0_bootstrap.py: Questionnaire loading
- InputContract: Hash validation
