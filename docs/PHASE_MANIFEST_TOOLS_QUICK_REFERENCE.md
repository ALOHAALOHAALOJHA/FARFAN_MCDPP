# Phase Manifest Tools - Quick Reference

## Overview
Tools to maintain consistency between phase manifests and the actual DAG (Directed Acyclic Graph) files.

## Quick Commands

### Check Consistency
```bash
python scripts/audit/reconcile_phase_manifests.py
```
**Purpose:** Verify all manifests match their DAG files  
**Output:** Color-coded console report + JSON audit file  
**Exit Code:** 0 if consistent, 1 if inconsistent

### Update Manifests
```bash
python scripts/audit/update_phase_manifests.py
```
**Purpose:** Automatically update all manifests to match current DAG files  
**Output:** Console progress report  
**Exit Code:** 0 if successful, 1 if errors

## Usage Examples

### Example 1: After Adding New Files
```bash
# 1. Add new Python files to phase directory
touch src/farfan_pipeline/phases/Phase_02/phase2_50_03_new_module.py

# 2. Update manifests
python scripts/audit/update_phase_manifests.py

# 3. Verify consistency
python scripts/audit/reconcile_phase_manifests.py
```

### Example 2: After Removing Files
```bash
# 1. Remove old files
rm src/farfan_pipeline/phases/Phase_04/obsolete_module.py

# 2. Update manifests
python scripts/audit/update_phase_manifests.py

# 3. Verify consistency
python scripts/audit/reconcile_phase_manifests.py
```

### Example 3: Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check if any phase files changed
if git diff --cached --name-only | grep -q "src/farfan_pipeline/phases/.*/.*\.py"; then
    echo "Phase files changed, verifying manifest consistency..."
    python scripts/audit/reconcile_phase_manifests.py
    if [ $? -ne 0 ]; then
        echo "ERROR: Manifests are inconsistent with DAG files!"
        echo "Run: python scripts/audit/update_phase_manifests.py"
        exit 1
    fi
fi
```

### Example 4: CI/CD Integration
```yaml
# .github/workflows/manifest-check.yml
name: Manifest Consistency Check

on: [push, pull_request]

jobs:
  check-manifests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check manifest-DAG consistency
        run: python scripts/audit/reconcile_phase_manifests.py
```

## Output Examples

### Consistent Phase (Success)
```
================================================================================
Phase_02 - ✓ CONSISTENT
================================================================================
✓ Manifest exists: farfan_pipeline/phases/Phase_02/PHASE_2_MANIFEST.json

Statistics:
  Files in directory:     42
  Files in manifest:      42
  Files in both:          42
  In dir, not in manifest: 0
  In manifest, not in dir: 0
```

### Inconsistent Phase (Needs Work)
```
================================================================================
Phase_04 - ✗ NEEDS RECONCILIATION
================================================================================
✓ Manifest exists: farfan_pipeline/phases/Phase_04/PHASE_4_MANIFEST.json

Statistics:
  Files in directory:     13
  Files in manifest:      11
  Files in both:          10
  In dir, not in manifest: 3
  In manifest, not in dir: 1

Files in directory but NOT in manifest:
  + phase4_10_00_new_module.py
  + phase4_20_00_another_module.py
  + phase4_30_00_third_module.py

Files in manifest but NOT in directory:
  - phase4_15_00_removed_module.py
```

## File Naming Convention

To ensure proper automatic classification, follow this pattern:

```
phaseX_YY_ZZ_descriptive_name.py
```

Where:
- `X` = Phase number (0-9)
- `YY` = Stage code (00, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95)
- `ZZ` = Sequence number within stage (00, 01, 02, ...)
- `descriptive_name` = Purpose of the module

### Stage Codes
- `00` - Infrastructure
- `10` - Configuration
- `20` - Enforcement
- `30` - Resource Management
- `40` - Validation
- `50` - Execution
- `60` - Integration
- `70` - Aggregation
- `80` - Evidence
- `90` - Orchestration
- `95` - Profiling/Metrics

### Examples
- `phase2_10_00_factory.py` - Phase 2, Configuration stage, Factory module
- `phase4_70_00_aggregation.py` - Phase 4, Aggregation stage, Core aggregation
- `phase0_90_02_bootstrap.py` - Phase 0, Orchestration stage, Bootstrap module

## Troubleshooting

### Issue: Script fails with "No module named X"
**Solution:** Run from repository root:
```bash
cd /path/to/FARFAN_MCDPP
python scripts/audit/reconcile_phase_manifests.py
```

### Issue: Manifest shows extra files that don't exist
**Solution:** Run the update script to sync:
```bash
python scripts/audit/update_phase_manifests.py
```

### Issue: New files not appearing in manifest
**Solution:** Ensure files follow naming convention, then update:
```bash
python scripts/audit/update_phase_manifests.py
```

### Issue: Want to exclude certain files from manifest
**Solution:** Move files to a subdirectory (e.g., `legacy/`, `tests/`, `docs/`)

## Advanced Usage

### Generate Only JSON Report (No Console Output)
```bash
python scripts/audit/reconcile_phase_manifests.py > /dev/null
cat artifacts/audits/phase_manifest_reconciliation_report.json
```

### Check Specific Phase
```python
from pathlib import Path
import json

phase_dir = Path("src/farfan_pipeline/phases/Phase_02")
manifest = phase_dir / "PHASE_2_MANIFEST.json"

with open(manifest) as f:
    data = json.load(f)
    print(f"Total modules: {data['statistics']['total_modules']}")
    print(f"Stages: {data['statistics']['stages']}")
```

### Programmatic Verification
```python
import subprocess
import sys

result = subprocess.run(
    ["python", "scripts/audit/reconcile_phase_manifests.py"],
    capture_output=True
)

if result.returncode == 0:
    print("✅ All manifests consistent")
else:
    print("❌ Manifests need reconciliation")
    sys.exit(1)
```

## Related Documentation
- Full report: `docs/phase_manifest_reconciliation_report.md`
- Audit data: `artifacts/audits/phase_manifest_reconciliation_report.json`
- Phase specs: `src/farfan_pipeline/phases/Phase_*/PHASE_*_MANIFEST.json`

## Support
For issues or questions, check:
1. This quick reference
2. The comprehensive report (`docs/phase_manifest_reconciliation_report.md`)
3. Script source code with inline documentation
