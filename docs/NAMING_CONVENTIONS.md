# Naming Convention Enforcement - Implementation Summary

## Overview

This document describes the naming convention enforcement system implemented for the F.A.R.F.A.N Phase 2 stabilization.

## Naming Rules

### Rule 3.1.1: Phase-Root Python Files

**Pattern:** `^phase2_[a-z]_[a-z0-9_]+\.py$`

**Location:** Root of phase directories (e.g., `src/canonic_phases/phase_2/`)

**Valid Examples:**
- `phase2_a_arg_router.py`
- `phase2_b_carver.py`
- `phase2_c_evidence_nexus.py`

**Invalid Examples:**
- `arg_router.py` (missing phase2_ prefix)
- `Phase2Router.py` (wrong case)
- `phase2-router.py` (hyphen instead of underscore)

### Rule 3.1.2: Package-Internal Python Files

**Pattern:** `^[a-z][a-z0-9_]*\.py$`

**Locations:**
- `executors/`
- `contracts/`
- `orchestration/`
- `sisas/`
- `constants/`
- `tests/`
- `tools/`

**Valid Examples:**
- `base_executor_with_contract.py`
- `phase2_routing_contract.py`
- `executor_config.py`

**Invalid Examples:**
- `BaseExecutor.py` (wrong case)
- `routing-contract.py` (hyphen instead of underscore)

### Rule 3.1.3: Schema Files

**Pattern:** `^[a-z][a-z0-9_]*\.schema\.json$`

**Location:** `schemas/`, `system/config/`

**Valid Examples:**
- `executor_config.schema.json`
- `validation_rules.schema.json`

**Invalid Examples:**
- `ExecutorConfig.json` (missing .schema., wrong case)
- `executor_config.json` (missing .schema.)

### Rule 3.1.4: Certificate Files

**Pattern:** `^CERTIFICATE_[0-9]{2}_[A-Z][A-Z0-9_]*\.md$`

**Location:** `contracts/certificates/`

**Valid Examples:**
- `CERTIFICATE_01_ROUTING_CONTRACT.md`
- `CERTIFICATE_15_ORCHESTRATOR_TRANSCRIPT.md`

**Invalid Examples:**
- `certificate_01.md` (wrong case)
- `CERT_01.md` (wrong prefix)
- `CERTIFICATE_P3_01.md` (letters in number field)

### Rule 3.1.5: Test Files

**Pattern:** `^test_phase2_[a-z0-9_]+\.py$`

**Locations:** `tests/`, `executors/tests/`

**Valid Examples:**
- `test_phase2_carver_300_delivery.py`
- `test_phase2_executor_contracts_cqvr_gate.py`

**Invalid Examples:**
- `test_carver.py` (missing phase2_)
- `phase2_test_carver.py` (wrong prefix order)

## Implementation

### Tools

1. **`scripts/validate_naming_conventions.py`**
   - Validates all files against naming conventions
   - Supports legacy exemptions via `.naming_exemptions`
   - Can be run in CI mode to block PRs

2. **`.naming_exemptions`**
   - Lists 33 legacy files exempt from rules
   - Should NEVER be modified to add new files
   - Only updated when legacy files are renamed

3. **`.github/workflows/naming-conventions.yml`**
   - CI workflow that runs on every PR
   - Blocks PRs with new naming violations
   - Allows legacy files (via exemptions)

### Usage

**Local Validation:**
```bash
# Check compliance (with legacy exemptions)
python scripts/validate_naming_conventions.py

# Strict mode (no exemptions, shows all violations)
python scripts/validate_naming_conventions.py --strict

# Report only (doesn't exit with error)
python scripts/validate_naming_conventions.py --report-only
```

**CI Integration:**
The GitHub workflow automatically runs on:
- Push to main/develop
- Pull requests to main/develop
- Changes to Python files, schema files, or certificates

## Legacy Files

### Current Status

**33 files** are currently exempt from naming conventions:
- 17 Phase_two Python files
- 1 schema file
- 15 Phase 3 certificate files

See `.naming_exemptions` for the complete list.

### Remediation Plan

**Phase 1: Stabilization (Current)**
- ✅ Enforce naming conventions for NEW files
- ✅ Create exemption list for legacy files
- ✅ Add CI enforcement

**Phase 2: Migration (Future)**
- Create `src/canonic_phases/phase_2/` structure
- Gradually migrate files with proper naming
- Update imports across codebase
- Remove from exemption list as files are migrated

**Phase 3: Complete Enforcement (Future)**
- Remove all exemptions
- Enable strict mode in CI
- Update documentation

## Compliance Status

### New Files
✅ **ENFORCED** - All new files MUST comply with naming conventions

### Legacy Files
⚠️ **EXEMPTED** - 33 legacy files are temporarily exempt

### CI Status
✅ **ACTIVE** - Naming convention checks run on every PR

## File Header Template

**Note:** Section 3.2 of the requirements specifies a mandatory file header template.

Every `.py` file MUST begin with a docstring following this structure:

```python
"""
Module: src.canonic_phases.phase_2.{module_name}

{Brief description of what this module does}

This module implements {specific functionality} for Phase 2 of the F.A.R.F.A.N
pipeline. It follows the canonical Phase 2 architecture.

Key Features:
- Feature 1: Description
- Feature 2: Description

Compliance:
- Naming: Rule 3.1.X
- Header: Rule 3.2
- Contract: Executor Contract v3.0
"""
```

### Header Components

1. **Module Path** (Line 2): Full dotted path to the module
2. **Brief Description** (Line 4): One-line summary
3. **Detailed Description** (Lines 6+): Comprehensive explanation
4. **Key Features**: Bulleted list of main capabilities
5. **Compliance Markers**: References to applicable rules

### Validation

File headers are validated using:

```bash
# Check file headers
python scripts/validate_file_headers.py

# Report only (non-blocking)
python scripts/validate_file_headers.py --report-only
```

### Template

A complete template is available at:
- `docs/PHASE2_FILE_TEMPLATE.py`

This template shows:
- Proper module docstring structure
- Import organization (standard → third-party → local)
- Class and function documentation
- Type hints and annotations
- Compliance markers

## File Header Template

## Testing

**Test Coverage:**
- ✅ Validator correctly identifies violations
- ✅ Exemption system works correctly
- ✅ CI workflow executes properly
- ✅ All new files comply with rules

**Validation:**
```bash
# Run local validation
python scripts/validate_naming_conventions.py

# Should output: ✅ All naming conventions validated successfully
```

## References

- Issue: IV - SECTION 3: NAMING CONVENTION ENFORCEMENT
- Validator: `scripts/validate_naming_conventions.py`
- CI Workflow: `.github/workflows/naming-conventions.yml`
- Exemptions: `.naming_exemptions`

## Maintenance

### Adding New Exemptions (Discouraged)

**DO NOT** add new files to exemptions unless absolutely necessary. New files should always comply.

If you must add an exemption:
1. Document the reason
2. Create a remediation plan
3. Add to `.naming_exemptions`

### Removing Exemptions (Encouraged)

When renaming a legacy file:
1. Rename the file following the convention
2. Update all imports
3. Remove from `.naming_exemptions`
4. Test thoroughly
5. Submit PR

---

**Status:** ACTIVE  
**Last Updated:** 2025-12-18  
**Maintainer:** F.A.R.F.A.N Core Team
