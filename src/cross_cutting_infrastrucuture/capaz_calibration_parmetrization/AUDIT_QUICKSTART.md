# COHORT_2024 Structural Audit - Quick Start Guide

## Overview
This guide provides quick instructions for auditing and maintaining the structural integrity of COHORT_2024 calibration and parametrization files.

## Quick Commands

### 1. Run Complete Audit (Dry Run)
Preview all issues and proposed changes without modifying files:

```bash
cd src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization
python master_structural_audit.py
```

### 2. Run Complete Audit (Live Execution)
Execute all remediation steps and delete legacy files:

```bash
cd src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization
python master_structural_audit.py --execute
```

### 3. Check Structural Compliance Only
Just verify structure without making changes:

```bash
cd src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization
python structural_audit.py
```

### 4. Delete Legacy Files Only
Clean up legacy files from previous waves:

```bash
# Preview deletions
python cleanup_legacy_files.py

# Execute deletions
python cleanup_legacy_files.py --execute
```

### 5. Create Missing Files
Generate missing configuration files:

```bash
# Preview actions
python reorganize_files.py

# Execute actions
python reorganize_files.py --execute
```

## What Each Script Does

### `master_structural_audit.py` (RECOMMENDED)
**Complete end-to-end audit and remediation**

**Phases**:
1. Initial structural audit → Identify all issues
2. File reorganization → Create missing files
3. Legacy cleanup → Delete old files
4. Final verification → Confirm compliance

**When to use**: 
- First time setup
- After major refactoring
- Periodic compliance checks

**Output**: `validation_reports/master_audit_report.json`

---

### `structural_audit.py`
**Read-only structural verification**

**Checks**:
- ✓ All required files present
- ✓ Correct COHORT_2024 prefixes
- ✓ Proper subfolder placement
- ✓ No legacy duplicates
- ✓ No misplaced artifacts

**When to use**:
- Quick compliance check
- CI/CD validation
- Before code commit

**Output**: `validation_reports/structural_audit_report.json`

---

### `cleanup_legacy_files.py`
**Legacy file deletion**

**Actions**:
- Deletes unlabeled configuration files
- Removes duplicate versions
- Preserves utility scripts
- Archives evidence traces

**When to use**:
- After migration from previous wave
- Cleaning up after refactoring
- Removing duplicate files

**Output**: `validation_reports/legacy_cleanup_report.json`

---

### `reorganize_files.py`
**File creation and reorganization**

**Actions**:
- Creates missing required files
- Generates configuration from data
- Ensures directory structure
- Validates file placement

**When to use**:
- Setting up new environment
- After structural changes
- Creating missing configs

**Output**: `validation_reports/reorganization_report.json`

## Typical Workflows

### First Time Setup
```bash
# 1. Run master audit in dry-run to preview
python master_structural_audit.py

# 2. Review the master_audit_report.json
cat validation_reports/master_audit_report.json

# 3. If satisfied, execute live
python master_structural_audit.py --execute

# 4. Verify compliance
python structural_audit.py
```

### Regular Compliance Check
```bash
# Quick verification (should pass with exit code 0)
python structural_audit.py
```

### After Adding New Files
```bash
# 1. Run audit to check for issues
python structural_audit.py

# 2. If unlabeled files detected, review and rename
# 3. Re-run audit to verify
python structural_audit.py
```

### Cleaning Up After Migration
```bash
# 1. Preview deletions
python cleanup_legacy_files.py

# 2. Review what will be deleted
# 3. Execute cleanup
python cleanup_legacy_files.py --execute

# 4. Verify structure
python structural_audit.py
```

## Understanding Audit Reports

### Success Indicators
✓ No issues found
✓ All required files present
✓ COHORT_2024 files: [expected count]
✓ Legacy files: 0
✓ Unlabeled files: 0
✓ Duplicate files: 0

### Warning Signs
⚠ Legacy files detected: X
⚠ Unlabeled files: X
⚠ Duplicate files: X
⚠ Misplaced files: X

### Critical Issues
✗ Required file missing: [filename]
✗ MISPLACED: File in wrong subfolder
✗ DUPLICATE: Multiple versions exist

## Output Reports Location

All reports are saved to:
```
validation_reports/
├── master_audit_report.json       # Complete audit results
├── structural_audit_report.json   # Structure verification
├── legacy_cleanup_report.json     # Cleanup actions
└── reorganization_report.json     # Reorganization actions
```

## Integration with CI/CD

### Pre-commit Hook
```bash
#!/bin/bash
cd src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization
python structural_audit.py
exit $?
```

### GitHub Actions
```yaml
- name: Verify COHORT_2024 Structure
  run: |
    cd src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization
    python structural_audit.py
```

## Troubleshooting

### "Required file missing"
**Solution**: Run `python reorganize_files.py --execute` to create missing files

### "Legacy files detected"
**Solution**: Run `python cleanup_legacy_files.py --execute` to remove old files

### "Unlabeled files"
**Solution**: Rename files to include `COHORT_2024_` prefix or add to preserve list

### "Duplicate files"
**Solution**: Delete legacy versions, keep only COHORT_2024 prefixed files

### "Misplaced files"
**Solution**: Move files to correct subfolder (calibration/ or parametrization/)

## Safety Features

### Dry Run by Default
All scripts run in dry-run mode by default:
- No files are modified or deleted
- All actions are previewed
- Use `--execute` flag for live execution

### Countdown Warning
Live execution mode includes 3-5 second countdown:
- Allows cancellation with Ctrl+C
- Prevents accidental deletions
- Provides time to review command

### Comprehensive Logging
All actions are logged in JSON reports:
- Full audit trail
- Rollback information
- Change tracking

## Best Practices

1. **Always run dry-run first**: Preview changes before executing
2. **Review reports**: Check JSON reports for detailed information
3. **Backup before execute**: Keep backup of files before live execution
4. **Run after changes**: Execute audit after any structural changes
5. **Regular checks**: Run compliance check regularly (weekly/monthly)
6. **Document exceptions**: Update preserve list for legitimate exceptions

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│  COHORT_2024 Structural Audit - Command Reference       │
├─────────────────────────────────────────────────────────┤
│  Complete Audit:                                        │
│    python master_structural_audit.py                    │
│    python master_structural_audit.py --execute          │
│                                                          │
│  Quick Check:                                           │
│    python structural_audit.py                           │
│                                                          │
│  Clean Legacy:                                          │
│    python cleanup_legacy_files.py [--execute]           │
│                                                          │
│  Create Files:                                          │
│    python reorganize_files.py [--execute]               │
│                                                          │
│  Reports:                                               │
│    validation_reports/*.json                            │
└─────────────────────────────────────────────────────────┘
```

## Support

For issues or questions:
- See: `STRUCTURAL_GOVERNANCE.md` for detailed policies
- Check: `validation_reports/` for detailed audit results
- Review: `COHORT_MANIFEST.json` for file inventory
