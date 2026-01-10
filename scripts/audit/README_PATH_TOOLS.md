# Path Audit and Repair Tools

This directory contains automated tools for auditing and repairing path-related issues in the F.A.R. F.A.N codebase.

## Tools Overview

### 1. `path_audit.py` - Path Auditor

Scans the codebase for common path-related issues.

**Usage:**
```bash
# Run from project root
python scripts/audit/path_audit.py

# Verbose output
python scripts/audit/path_audit.py --verbose

# JSON output for CI/CD
python scripts/audit/path_audit.py --json

# Filter by severity
python scripts/audit/path_audit.py --severity high

# Exclude patterns
python scripts/audit/path_audit.py --exclude backups --exclude tests/legacy

# Specify custom root directory
python scripts/audit/path_audit.py --root /path/to/project
```

**Detects:**
- ❌ Hardcoded absolute paths (Unix and Windows)
- ❌ Deprecated import patterns (`canonic_phases` → `farfan_pipeline`)
- ❌ Manual `sys.path` manipulation
- ❌ Inappropriate use of `os.getcwd()`
- ❌ String concatenation for paths
- ❌ Using `os.path.join` instead of `Path /` operator
- ❌ Fragile relative path navigation (`../../`)
- ❌ Unresolved `__file__` usage (missing `.resolve()`)

**Exit codes:**
- `0` - No issues found (or only low/medium severity)
- `1` - High-severity issues found

**Example output:**
```
❌ PATH AUDIT ISSUES FOUND

================================================================================

🔴 HIGH SEVERITY (2 issues)

  scripts/analysis.py:15
    Type: hardcoded_path
    Message: Hardcoded absolute Unix path detected
    Code: ROOT = Path("/Users/myuser/FARFAN_MPP")

🟡 MEDIUM SEVERITY (5 issues)

  tests/test_phase0.py:3
    Type: deprecated_import
    Message: Deprecated import (use farfan_pipeline instead)
    Code: from canonic_phases.Phase_zero import paths

================================================================================

Total issues: 7
  High: 2
  Medium: 5
  Low: 0
Files scanned: 877
```

**JSON Output:**
```bash
python scripts/audit/path_audit.py --json --severity high
```

Returns structured JSON for CI/CD integration:
```json
{
  "summary": {
    "total_issues": 22,
    "files_scanned": 877,
    "high_severity": 22,
    "medium_severity": 77,
    "low_severity": 213
  },
  "issues": [...]
}
```

---

### 2. `path_repair.py` - Path Repair Utility

Provides automated fixes for common path issues.

**Usage:**
```bash
# Dry run (default) - shows what would be fixed
python scripts/audit/path_repair.py

# Apply fixes
python scripts/audit/path_repair.py --fix

# Apply fixes with backup files
python scripts/audit/path_repair.py --fix --backup

# Aggressive mode (includes os.path.join and __file__ fixes)
python scripts/audit/path_repair.py --fix --backup --aggressive

# Verbose output
python scripts/audit/path_repair.py --fix --verbose
```

**Repairs:**
- ✅ **Automated (always):** Deprecated import patterns
- ✅ **Automated (--aggressive):** `os.path.join` to `Path /` operator
- ✅ **Automated (--aggressive):** `Path(__file__)` to `Path(__file__).resolve()`
- 💡 **Suggestions:** Hardcoded paths (requires manual review)

**Example workflow:**
```bash
# Step 1: Check what would be fixed
python scripts/audit/path_repair.py

# Step 2: Review the proposed changes

# Step 3: Apply fixes with backup
python scripts/audit/path_repair.py --fix --backup

# Step 4: Run audit to verify
python scripts/audit/path_audit.py

# Step 5: If satisfied, remove backups
find . -name "*.bak" -type f -delete
```

**Example output:**
```
================================================================================
REPAIR MODE - Changes will be applied
Backup files will be created (.bak)
================================================================================

Processing: scripts/analysis.py
  Fixed 2 import(s) in scripts/analysis.py

Processing: tests/test_phase0.py
  Fixed 1 import(s) in tests/test_phase0.py

================================================================================
📝 IMPORT FIXES (APPLIED)
================================================================================

scripts/analysis.py (2 changes)
  from canonic_phases\.Phase_zero\.paths import → from farfan_pipeline.utils.paths import (1x)
  from canonic_phases\.Phase_zero import paths → from farfan_pipeline.utils import paths (1x)

================================================================================
💡 MANUAL REVIEW REQUIRED - Hardcoded Paths
================================================================================

scripts/analysis.py:15
  Original: ROOT = Path("/Users/myuser/FARFAN_MPP")
  Suggestion: Replace with: from farfan_pipeline.utils.paths import PROJECT_ROOT
```

---

## Typical Workflow

### Initial Audit

1. **Run the auditor:**
   ```bash
   python scripts/audit/path_audit.py --verbose > path_audit_report.txt
   ```

2. **Review the report:**
   ```bash
   cat path_audit_report.txt
   ```

3. **Categorize issues:**
   - High-severity: Must fix immediately
   - Medium-severity: Fix in next sprint
   - Low-severity: Technical debt

### Automated Repair

1. **Dry run to preview changes:**
   ```bash
   python scripts/audit/path_repair.py
   ```

2. **Apply automated fixes:**
   ```bash
   python scripts/audit/path_repair.py --fix --backup
   ```

3. **Verify fixes:**
   ```bash
   python scripts/audit/path_audit.py
   ```

4. **Run tests:**
   ```bash
   PYTHONPATH=src pytest tests/
   ```

### Manual Fixes

For issues that require manual intervention (hardcoded paths, complex sys.path manipulations):

1. **Review suggestions from repair tool**
2. **Follow the specification guide:** `docs/audit/PATH_AUDIT_SPECIFICATION.md`
3. **Common fixes:**

   **Before:**
   ```python
   ROOT = Path("/Users/myuser/FARFAN_MPP")
   DATA = ROOT / "data"
   ```

   **After:**
   ```python
   from farfan_pipeline.utils.paths import PROJECT_ROOT, DATA_DIR
   ROOT = PROJECT_ROOT
   DATA = DATA_DIR
   ```

---

## Integration with CI/CD

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
echo "Running path audit..."
python scripts/audit/path_audit.py
if [ $? -ne 0 ]; then
    echo "Path audit failed. Fix issues before committing."
    exit 1
fi
```

### GitHub Actions

Add to `.github/workflows/audit.yml`:
```yaml
name: Path Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: '3.9'
      - name: Run path audit
        run: python scripts/audit/path_audit.py
```

---

## Troubleshooting

### "Could not find project root"

The tools auto-detect the project root by looking for `pyproject.toml`. If this fails:
```bash
python scripts/audit/path_audit.py --root /path/to/FARFAN_MPP
```

### "Permission denied"

Make scripts executable:
```bash
chmod +x scripts/audit/path_audit.py
chmod +x scripts/audit/path_repair.py
```

### False Positives

Some patterns may be flagged incorrectly. Review the specification guide for guidance:
```bash
less docs/audit/PATH_AUDIT_SPECIFICATION.md
```

---

## Related Documentation

- **Full Specification:** `docs/audit/PATH_AUDIT_SPECIFICATION.md`
- **Path Module Source:** `src/farfan_pipeline/phases/Phase_zero/phase0_10_00_paths.py`
- **Utility Re-export:** `src/farfan_pipeline/utils/paths.py`

---

## Support

For issues or questions:
1. Review `docs/audit/PATH_AUDIT_SPECIFICATION.md`
2. Check the path module source code
3. Create a GitHub issue with the audit report attached
