# Phase 1 Anomalies and Remediation

**Audit Date**: 2026-01-15
**Auditor**: Jules

## 1. Sequential Integrity Violations

### 1.1 Orphaned Files
**Detected**:
- `interfaces/*.json` and duplicate protocol definitions.
- `contracts/phase1_10_00_...` (numbered versions of contracts).
- `primitives/phase1_10_00_...` (numbered versions of primitives).

**Remediation**:
- **Consolidated Contracts**: Deleted numbered `10_00` versions in favor of canonical `phase1_input_contract.py`, etc.
- **Consolidated Primitives**: Deleted numbered `10_00` and `00_00` versions. Kept `streaming_extractor.py` and `truncation_audit.py`.
- **Merged Interfaces**: Moved valid JSON contracts from `interfaces/` to `interphase/` and deleted `interfaces/`.

### 1.2 File Reclassification (Legacy Restoration)
**Detected**:
- `phase1_01_00_cpp_models.py` was located in `docs/legacy/` but actively imported by `phase1_13_00_cpp_ingestion.py`.
- This violated the "No Code Outside Graph" rule.

**Remediation**:
- Moved `phase1_01_00_cpp_models.py` back to root: `src/farfan_pipeline/phases/Phase_01/phase1_01_00_cpp_models.py`.
- Updated imports in `phase1_13_00_cpp_ingestion.py` to reference the local module.

### 1.3 Constants Consolidation
**Detected**:
- `phase1_02_00_phase_1_constants.py` existed alongside `PHASE_1_CONSTANTS.py` (root mandatory file).

**Remediation**:
- Merged content from `phase1_02_00...` into `PHASE_1_CONSTANTS.py`.
- Deleted `phase1_02_00_phase_1_constants.py`.
- Updated all imports to point to `PHASE_1_CONSTANTS`.

## 2. Foldering Standardization

**Compliance Check**:
- `contracts/` ✅ (Contains 3 canonical contracts + report)
- `docs/` ✅ (Contains execution flow, anomalies, legacy docs)
- `interphase/` ✅ (Contains protocols and JSON contracts)
- `primitives/` ✅ (Contains extraction/audit primitives)
- `tests/` ✅ (Contains unit/integration tests)
- `PHASE_1_MANIFEST.json` ✅
- `PHASE_1_CONSTANTS.py` ✅
- `README.md` ✅
- `__init__.py` ✅
- Numbered Source Files ✅ (`phase1_01_00`, `phase1_03_00`, ..., `phase1_13_00`)

## 3. Contract Rigidness

**Status**:
- `phase1_mission_contract.py`: Enforces weight-based execution (SP4, SP11, SP13 Critical).
- `phase1_input_contract.py`: Enforces PRE-001 to PRE-010.
- `phase1_output_contract.py`: Enforces POST-001 to POST-006 (60-chunk invariant).

## 4. Remaining Anomalies (Accepted)
- `tests/` contains files named `phase1_10_00_...` or `test_01_...` which don't strictly follow `phase1_XX_YY` but are acceptable for test organization.
- `docs/legacy/` still contains `Phase_one_Python_Files.pdf` (Documentation artifact).
