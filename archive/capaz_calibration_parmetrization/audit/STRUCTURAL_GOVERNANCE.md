# COHORT_2024 Structural Governance

## Overview

This document defines the structural organization requirements for all calibration and parametrization files under COHORT_2024 governance. It ensures no ambiguity, duplication, or confusion between configuration files across refactoring waves.

## Directory Structure

```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/
├── calibration/                       # Calibration layer configurations
│   ├── COHORT_2024_intrinsic_calibration.json
│   ├── COHORT_2024_intrinsic_calibration_rubric.json
│   ├── COHORT_2024_fusion_weights.json
│   ├── COHORT_2024_method_compatibility.json
│   ├── COHORT_2024_layer_requirements.json
│   ├── COHORT_2024_canonical_method_inventory.json
│   ├── COHORT_2024_questionnaire_monolith.json
│   ├── COHORT_2024_*.py                # Calibration implementations
│   └── certificate_examples/          # Example certificates (preserved)
│
├── parametrization/                   # Runtime parametrization configs
│   ├── COHORT_2024_executor_config.json
│   ├── COHORT_2024_runtime_layers.json
│   └── COHORT_2024_*.py               # Parametrization implementations
│
├── evidence_traces/                   # Execution traces (archival)
├── validation_reports/                # Audit and validation reports
│
├── COHORT_MANIFEST.json               # Master manifest
├── structural_audit.py                # Audit script
├── cleanup_legacy_files.py            # Legacy cleanup script
├── reorganize_files.py                # File reorganization script
└── master_structural_audit.py         # Master orchestration script
```

## File Naming Convention

### Required Prefix
All configuration and implementation files MUST use the `COHORT_2024_` prefix:

- ✓ `COHORT_2024_intrinsic_calibration.json`
- ✓ `COHORT_2024_fusion_weights.json`
- ✗ `intrinsic_calibration.json` (legacy, must be deleted)
- ✗ `fusion_weights.json` (legacy, must be deleted)

### Exceptions
The following utility files do NOT require the prefix:
- `__init__.py`
- `certificate_generator.py`
- `certificate_validator.py`
- `validate_fusion_weights.py`
- `weight_validation_report.json`
- `chain_layer_tests.py`

## Required Configuration Files

### Calibration Subfolder
1. **COHORT_2024_intrinsic_calibration.json**
   - Purpose: Base layer (@b) calibration parameters
   - Authority: Intrinsic calibration specification

2. **COHORT_2024_fusion_weights.json**
   - Purpose: Choquet integral fusion weights
   - Authority: Three-pillar calibration system

3. **COHORT_2024_method_compatibility.json**
   - Purpose: Method compatibility scores
   - Authority: Method registry system

4. **COHORT_2024_layer_requirements.json**
   - Purpose: Layer dependencies and requirements
   - Authority: Layer computation framework

5. **COHORT_2024_intrinsic_calibration_rubric.json**
   - Purpose: Calibration rubric and decision automaton
   - Authority: Calibration governance

6. **COHORT_2024_canonical_method_inventory.json**
   - Purpose: Complete method inventory
   - Authority: Method registry

7. **COHORT_2024_questionnaire_monolith.json**
   - Purpose: 300-question questionnaire
   - Authority: Question layer specification

### Parametrization Subfolder
1. **COHORT_2024_executor_config.json**
   - Purpose: Executor runtime configuration
   - Authority: Execution framework

2. **COHORT_2024_runtime_layers.json**
   - Purpose: Runtime layer computation parameters
   - Authority: Layer execution system

## Legacy File Policy

### Identification
Legacy files are identified by:
1. **Missing COHORT_2024 prefix** on configuration files
2. **Duplicate names** (e.g., both `fusion_weights.json` and `COHORT_2024_fusion_weights.json`)
3. **Evidence trace artifacts** from previous waves

### Deletion Policy
Legacy files MUST be deleted when:
1. A corresponding COHORT_2024 version exists
2. They create ambiguity or confusion
3. They are from previous refactoring waves

### Examples for Deletion
- `calibration/fusion_weights.json` → DELETE (superseded by `COHORT_2024_fusion_weights.json`)
- `trace_examples/calibration_trace_example.json` → DELETE (legacy evidence trace)
- Any file with `farfan_pipeline.core.calibration` in path → DELETE (old structure)

## Audit Scripts

### 1. Structural Audit (`structural_audit.py`)
**Purpose**: Verify organizational compliance

**Usage**:
```bash
python structural_audit.py
```

**Checks**:
- All required files present with COHORT_2024 prefix
- Files in correct subfolders (calibration/ vs parametrization/)
- No legacy files remaining
- No unlabeled duplicates
- No misplaced artifacts

**Output**: `validation_reports/structural_audit_report.json`

### 2. Legacy Cleanup (`cleanup_legacy_files.py`)
**Purpose**: Remove legacy files from previous waves

**Usage**:
```bash
# Dry run (preview only)
python cleanup_legacy_files.py

# Live execution (actually deletes)
python cleanup_legacy_files.py --execute
```

**Actions**:
- Deletes unlabeled configuration files
- Removes duplicate legacy versions
- Preserves utility scripts
- Generates deletion report

**Output**: `validation_reports/legacy_cleanup_report.json`

### 3. File Reorganization (`reorganize_files.py`)
**Purpose**: Create missing files and fix structure

**Usage**:
```bash
# Dry run
python reorganize_files.py

# Live execution
python reorganize_files.py --execute
```

**Actions**:
- Creates missing required files
- Ensures proper directory structure
- Generates configuration from existing data
- Validates file placement

**Output**: `validation_reports/reorganization_report.json`

### 4. Master Audit (`master_structural_audit.py`)
**Purpose**: Complete end-to-end audit and remediation

**Usage**:
```bash
# Dry run (full preview)
python master_structural_audit.py

# Live execution (applies all changes)
python master_structural_audit.py --execute
```

**Workflow**:
1. **Phase 1**: Initial structural audit
2. **Phase 2**: File reorganization
3. **Phase 3**: Legacy cleanup
4. **Phase 4**: Final verification

**Output**: `validation_reports/master_audit_report.json`

## Compliance Checklist

### Before Deployment
- [ ] All configuration files have COHORT_2024 prefix
- [ ] All files in correct subfolders (calibration/ or parametrization/)
- [ ] No legacy files remaining (run `cleanup_legacy_files.py --execute`)
- [ ] All required configuration files present
- [ ] No duplicate or contradictory files
- [ ] Structural audit passes (run `master_structural_audit.py`)

### After Deployment
- [ ] Master audit report generated
- [ ] No issues in final verification phase
- [ ] COHORT_MANIFEST.json updated
- [ ] All import paths reference COHORT_2024 files
- [ ] Evidence traces archived appropriately

## Enforcement

### Automated Checks
The following must pass before code commit:
1. `python structural_audit.py` (exit code 0)
2. All required files present
3. No legacy files in calibration/ or parametrization/

### Manual Review
Periodic audits should verify:
1. No new unlabeled files introduced
2. Import statements reference correct COHORT_2024 files
3. No parallel configuration systems exist

## Future Wave Policy

When migrating to COHORT_2025 or later:
1. Create new files with COHORT_XXXX prefix
2. Preserve COHORT_2024 files for rollback capability
3. Update COHORT_MANIFEST.json with new wave
4. Run structural audit to verify separation
5. After validation period, archive COHORT_2024 files

## Contact

For questions about structural governance:
- Authority: COHORT_2024 Governance Protocol
- Documentation: This file (STRUCTURAL_GOVERNANCE.md)
- Audit Tools: `structural_audit.py`, `master_structural_audit.py`
