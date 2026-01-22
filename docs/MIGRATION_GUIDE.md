# F.A.R.F.A.N Migration Guide

## Overview

This guide helps you migrate existing code to the new import standards and Python path configuration.

---

## What Changed?

### Before (Previous State)

1. **`farfan_pipeline` was a namespace package** (no `__init__.py`)
2. **Inconsistent PYTHONPATH** configuration
3. **Mixed import patterns** (absolute, relative, deprecated paths)

### After (Current State)

1. **`farfan_pipeline` is now a regular package** (with `__init__.py`)
2. **Standardized PYTHONPATH** configuration
3. **Clear import standards** documented in `docs/IMPORT_GOVERNANCE.md`

---

## Quick Start

### 1. Activate the Environment

```bash
# Option A: Using the activation script
source scripts/activate.sh

# Option B: Using direnv (recommended)
# Install direnv first, then:
direnv allow
```

### 2. Verify Your Setup

```bash
# Run the path audit script
python3 scripts/path_audit.py

# Test imports manually
python3 -c "from farfan_pipeline.orchestration import UnifiedOrchestrator; print('OK')"
python3 -c "from canonic_questionnaire_central import CQCLoader; print('OK')"
```

---

## Code Migration

### Step 1: Update Deprecated Imports

```python
# ❌ OLD - Deprecated import
from farfan_pipeline.analysis.factory import load_json, write_text_file

# ✅ NEW - Use infrastructure/dependencies
from farfan_pipeline.infrastructure.dependencies import get_dependency
json_loader = get_dependency("json")
```

### Step 2: Standardize Import Style

```python
# ❌ OLD - Mixed styles
from factory import create_executor
from farfan_pipeline.phases.Phase_02 import BaseExecutorWithContract
from ..core import UnitOfAnalysis

# ✅ NEW - Consistent absolute imports
from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import create_executor
from farfan_pipeline.phases.Phase_02 import BaseExecutorWithContract
from farfan_pipeline.core import UnitOfAnalysis
```

### Step 3: Fix Relative Imports

```python
# ❌ OLD - Too many levels
from ....phases.Phase_00 import ensure_list_return

# ✅ NEW - Absolute import
from farfan_pipeline.phases.Phase_00 import ensure_list_return
```

---

## File-by-File Migration

### Files That Need Updates

Use this command to find files with old imports:

```bash
# Find files with deprecated imports
grep -r "from farfan_pipeline.analysis" src/ --include="*.py"

# Find files with bare relative imports
grep -r "^from [^.]" src/farfan_pipeline/phases/ --include="*.py"
```

### Common Patterns

#### Pattern 1: Importing from analysis.factory

**Before:**
```python
from farfan_pipeline.analysis.factory import load_json, write_text_file
```

**After:**
```python
from farfan_pipeline.infrastructure.dependencies import get_dependency

json_ops = get_dependency("json")
json_ops.load_json(...)
```

#### Pattern 2: Importing from retry_handler

**Before:**
```python
from farfan_pipeline.analysis.retry_handler import DependencyType
```

**After:**
```python
from farfan_pipeline.infrastructure.dependencies import DependencyType
```

---

## Testing Your Changes

### 1. Run the Import Validator

```bash
python3 scripts/validate_imports.py
```

### 2. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_orchestration.py

# Run with coverage
pytest --cov=src/farfan_pipeline
```

### 3. Check Linting

```bash
# Check import ordering
ruff check --select I .

# Auto-fix import ordering
ruff check --select I --fix .
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'farfan_pipeline'"

**Solution:** Activate the environment:
```bash
source scripts/activate.sh
```

### Issue: "ModuleNotFoundError: No module named 'canonic_questionnaire_central'"

**Solution:** Ensure both `src/` and root are in PYTHONPATH:
```bash
export PYTHONPATH="$(pwd)/src:$(pwd):${PYTHONPATH}"
```

### Issue: Tests pass locally but fail in CI

**Solution:** Update your CI configuration to include PYTHONPATH setup:
```yaml
# .github/workflows/test.yml
- name: Run tests
  env:
    PYTHONPATH: ${{ github.workspace }}/src:${{ github.workspace }}
  run: pytest
```

---

## IDE Configuration

### VS Code

Create or update `.vscode/settings.json`:

```json
{
  "python.analysis.extraPaths": [
    "${workspaceFolder}/src",
    "${workspaceFolder}"
  ],
  "python.envFile": "${workspaceFolder}/.env"
}
```

### PyCharm

1. Open Settings → Project → Python Interpreter
2. Click the gear icon → Show All
3. Select your interpreter → Show paths
4. Add `src/` and project root to the paths

---

## Rollback Plan

If you encounter issues after migration:

1. **Restore previous state:**
   ```bash
   git checkout HEAD -- src/farfan_pipeline/__init__.py
   ```

2. **Report the issue** with:
   - File that failed
   - Import statement that failed
   - Error message

---

## Additional Resources

- **Import Governance:** `docs/IMPORT_GOVERNANCE.md`
- **Path Audit Tool:** `scripts/path_audit.py`
- **Import Validator:** `scripts/validate_imports.py`

---

*Last updated: 2026-01-21*
