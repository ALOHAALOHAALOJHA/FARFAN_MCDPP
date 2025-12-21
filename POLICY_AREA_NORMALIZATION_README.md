# Policy Area Normalization - README

## Overview

This directory contains scripts and documentation for the **Total Normalization** performed to fix the policy area ordering error in the F.A.R.F.A.N system (Issue #368).

## Background

### The Problem

The questionnaire monolith originally contained a critical ordering error where the 10 policy areas (PA01-PA10) were arranged in the wrong sequence:

**ERRONEOUS ORDER**: PA01 → **PA10** → PA02 → PA03 → PA04 → PA05 → PA06 → PA07 → PA08 → PA09

This error was introduced during automated generation and propagated to:
- 270 out of 300 executor contracts (Q031-Q300)
- The canonical `policy_areas_and_dimensions.json` reference file

### The Solution

The questionnaire monolith was corrected to the canonical order:

**CANONICAL ORDER**: PA01 → PA02 → PA03 → PA04 → PA05 → PA06 → PA07 → PA08 → PA09 → PA10

However, the "collateral damage" remained: 270 contracts and the canonical reference file still had the old erroneous mappings.

## What Was Fixed

### 1. Executor Contracts (270 files)
- **Location**: `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/`
- **Files updated**: Q031.v3.json through Q300.v3.json
- **Changes per file**:
  - `identity.policy_area_id` updated
  - All `question_context.patterns[*].policy_area` entries updated
  - `output_contract.schema.properties.policy_area_id.const` updated
  - `contract_hash` recomputed
  - `updated_at` timestamp updated

### 2. Canonical Reference File
- **Location**: `sensitive_rules_for_coding/policy_areas_and_dimensions.json`
- **Changes**: All 10 policy area mappings corrected to canonical ordering

### 3. Backups Created
- `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized_backup_pre_normalization/`
- `sensitive_rules_for_coding/policy_areas_and_dimensions.json.backup_pre_normalization`

## Scripts

### 1. normalize_executor_contracts.py
**Purpose**: Normalize all 300 executor contracts to canonical policy area ordering

**Usage**:
```bash
python3 normalize_executor_contracts.py
```

**What it does**:
1. Creates backup of all 300 contracts
2. Updates policy_area_id in 270 contracts
3. Recomputes contract hashes
4. Updates timestamps
5. Generates audit report

**Output**: `EXECUTOR_CONTRACTS_NORMALIZATION_REPORT.json`

### 2. validate_policy_area_normalization.py
**Purpose**: Comprehensive validation of normalization across all system components

**Usage**:
```bash
python3 validate_policy_area_normalization.py
```

**What it validates**:
1. Questionnaire monolith has correct PA ordering (300 questions)
2. All executor contracts have correct policy_area_id (300 contracts)
3. Internal consistency within each contract
4. Alignment between monolith and contracts

**Exit code**: 0 = all checks pass, 1 = validation failed

### 3. update_canonical_policy_areas.py
**Purpose**: Update the canonical policy_areas_and_dimensions.json file

**Usage**:
```bash
python3 update_canonical_policy_areas.py
```

**What it does**:
1. Creates backup of original file
2. Generates canonical policy area mappings
3. Updates the file with correct ordering
4. Updates metadata

### 4. quick_check_policy_areas.py
**Purpose**: Quick verification utility for ongoing monitoring

**Usage**:
```bash
python3 quick_check_policy_areas.py
```

**What it checks**:
- Key contracts (Q001, Q030, Q031, Q060, Q061, Q271, Q300)
- Reports PASS/FAIL with details

## Canonical Ordering

| Policy Area | Question Range | Question Count |
|-------------|----------------|----------------|
| PA01        | Q001-Q030      | 30             |
| PA02        | Q031-Q060      | 30             |
| PA03        | Q061-Q090      | 30             |
| PA04        | Q091-Q120      | 30             |
| PA05        | Q121-Q150      | 30             |
| PA06        | Q151-Q180      | 30             |
| PA07        | Q181-Q210      | 30             |
| PA08        | Q211-Q240      | 30             |
| PA09        | Q241-Q270      | 30             |
| PA10        | Q271-Q300      | 30             |

## Formula

For any question number `q` (1-300):
```
policy_area_number = ⌈q / 30⌉
policy_area_id = f"PA{policy_area_number:02d}"
```

Examples:
- Q001 → PA01 (⌈1/30⌉ = 1)
- Q031 → PA02 (⌈31/30⌉ = 2)
- Q271 → PA10 (⌈271/30⌉ = 10)

## Verification

### Quick Check
```bash
python3 quick_check_policy_areas.py
```

### Full Validation
```bash
python3 validate_policy_area_normalization.py
```

### Manual Inspection
```bash
# Check a specific contract
python3 -c "
import json
with open('src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Q031.v3.json') as f:
    data = json.load(f)
    print(f'Q031 policy_area_id: {data[\"identity\"][\"policy_area_id\"]}')
"
# Expected output: Q031 policy_area_id: PA02
```

### Verify Canonical File
```bash
python3 -c "
import json
with open('sensitive_rules_for_coding/policy_areas_and_dimensions.json') as f:
    data = json.load(f)
    pa02 = data['policy_areas']['PA02']
    print(f'PA02 questions: {pa02[\"questions\"][:3]} ... {pa02[\"questions\"][-3:]}')
"
# Expected output: PA02 questions: ['Q031', 'Q032', 'Q033'] ... ['Q058', 'Q059', 'Q060']
```

## Documentation

- **TOTAL_NORMALIZATION_SUMMARY.md**: Comprehensive summary of the normalization
- **EXECUTOR_CONTRACTS_NORMALIZATION_REPORT.json**: Detailed audit trail of all 270 changes

## Impact Analysis

### Zero Breaking Changes
- Question IDs remain unchanged (Q001-Q300)
- Contract file names remain unchanged
- Contract structure unchanged
- Only `policy_area_id` values corrected to match canonical ordering

### Components Affected
1. ✅ Questionnaire monolith (already fixed prior to this work)
2. ✅ Executor contracts (270 normalized)
3. ✅ Canonical policy areas (fixed)
4. ⚠️ Downstream code that may hardcode old PA mappings (verify manually)

## Timeline

- **2025-11-28**: Original contracts generated with erroneous PA mapping
- **2025-12-21**: Questionnaire monolith corrected (Issue #368 opened)
- **2025-12-21**: Total normalization executed (this work)
  - 270 contracts normalized
  - Canonical file updated
  - All validations pass

## Status

✅ **COMPLETE** - All system components normalized and validated

## Maintenance

To verify normalization status anytime:
```bash
python3 quick_check_policy_areas.py
```

To add new contracts, ensure they follow the canonical ordering formula.

## Support

For questions about the normalization:
1. Read `TOTAL_NORMALIZATION_SUMMARY.md`
2. Review `EXECUTOR_CONTRACTS_NORMALIZATION_REPORT.json`
3. Run validation scripts

## License

Part of the F.A.R.F.A.N system (Proprietary)
