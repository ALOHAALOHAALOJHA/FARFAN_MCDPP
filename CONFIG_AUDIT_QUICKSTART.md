# Configuration Audit Quick Start Guide

Fast reference for running configuration audits and fixing violations.

## TL;DR

```bash
# Run full audit (dry-run mode)
python scripts/run_config_audit.py --dry-run

# Review reports
cat violations_audit.md
cat config_consolidation_report.md
cat config_reference_validation.md

# Execute consolidation
python scripts/run_config_audit.py
```

## Common Tasks

### 1. Find Hardcoded Calibration Values

```bash
python scripts/audit_calibration_config.py
# Output: violations_audit.md
```

**What it finds**:
- Hardcoded thresholds, weights, scores
- Magic numbers in calibration logic
- Untracked configuration constants

### 2. Find Duplicate Config Files

```bash
python scripts/consolidate_config.py --dry-run
# Output: config_consolidation_report.md
```

**What it finds**:
- Multiple files with same name
- Files with identical content
- Legacy configuration files

### 3. Validate Code References

```bash
python scripts/validate_config_references.py
# Output: config_reference_validation.md
```

**What it finds**:
- Legacy path references
- Canonical path usage
- Missing imports

## Fix Common Violations

### Fix: Hardcoded Threshold

**Before**:
```python
def filter_results(items):
    THRESHOLD = 0.75  # ❌ Hardcoded
    return [item for item in items if item.score > THRESHOLD]
```

**After**:
```python
def filter_results(items, config):
    threshold = config["filter_threshold"]  # ✓ From config
    return [item for item in items if item.score > threshold]
```

### Fix: Legacy Path Reference

**Before**:
```python
config_path = "config/intrinsic_calibration.json"  # ❌ Legacy
```

**After**:
```python
config_path = "system/config/calibration/intrinsic_calibration.json"  # ✓ Canonical
```

### Fix: Direct File Loading

**Before**:
```python
with open("config/settings.json") as f:  # ❌ Direct file access
    config = json.load(f)
```

**After**:
```python
from system.config.config_manager import ConfigManager  # ✓ Config manager
config = ConfigManager().get_config("settings")
```

## Report Summary

### violations_audit.md

- Lists all hardcoded calibration values
- Groups by severity (HIGH/MEDIUM/LOW)
- Shows file, line number, and context

**Action**: Refactor HIGH severity violations first

### config_consolidation_report.md

- Shows duplicate configuration files
- Lists archival actions
- Validates canonical file structure

**Action**: Update code to use canonical paths

### config_reference_validation.md

- Shows legacy path references
- Lists canonical references
- Provides migration guidance

**Action**: Update legacy references to canonical

### config_audit_summary.md

- Unified summary of all audits
- Overall status
- Next steps

**Action**: Use as checklist for remediation

## Canonical Structure

Always use:
```
system/config/
├── calibration/
│   ├── intrinsic_calibration.json       # Method scores
│   ├── intrinsic_calibration_rubric.json # Scoring rules
│   ├── runtime_layers.json               # Layer config
│   └── unit_transforms.json              # Unit transforms
└── executor_config.json                  # Executor settings
```

## Severity Guide

### HIGH - Fix Immediately
- Thresholds affecting decisions
- Statistical weights
- Model coefficients
- Baseline scores

### MEDIUM - Fix Soon
- Intermediate scores
- Ratio calculations
- Non-critical thresholds

### LOW - Optional
- Initialization values (0.0, 1.0)
- Small constants (1, 2, 100)
- Formatting parameters

## Quick Commands

```bash
# Full audit pipeline
python scripts/run_config_audit.py

# Individual audits
python scripts/audit_calibration_config.py
python scripts/consolidate_config.py
python scripts/validate_config_references.py

# Dry-run mode (preview only)
python scripts/run_config_audit.py --dry-run
python scripts/consolidate_config.py --dry-run
```

## Verification

After fixes:
```bash
# Re-run audit
python scripts/run_config_audit.py --dry-run

# Check for remaining violations
grep -r "THRESHOLD\|WEIGHT\|SCORE" src/ --include="*.py" | grep "= [0-9]"

# Verify config loading
python -c "from system.config.config_manager import ConfigManager; print(ConfigManager().get_config('calibration/intrinsic_calibration')['_metadata'])"
```

## Need Help?

1. Read full documentation: `CONFIG_AUDIT_README.md`
2. Check examples in `system/config/example_usage.py`
3. Review existing config files in `system/config/calibration/`
