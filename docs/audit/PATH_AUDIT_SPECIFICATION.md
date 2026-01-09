# 🔧 F.A.R. F.A.N Path Audit & Repair Specification Guide

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Path Infrastructure Architecture](#2-path-infrastructure-architecture)
3. [Critical Path Files & Their Roles](#3-critical-path-files--their-roles)
4. [Common Path Issues & Repairs](#4-common-path-issues--repairs)
5. [Python Path (PYTHONPATH) Configuration](#5-python-path-pythonpath-configuration)
6. [Path Audit Checklist](#6-path-audit-checklist)
7. [Repair Procedures](#7-repair-procedures)
8. [Best Practices & Standards](#8-best-practices--standards)

---

## 1. Executive Summary

The F.A.R. F.A.N project uses a **centralized path management system** located in `phase0_10_00_paths.py`. This is the **single source of truth** for all path operations.

The project structure uses:

| Component | Path |
|-----------|------|
| **Package Root** | `src/farfan_pipeline/` |
| **Path Module** | `src/farfan_pipeline/phases/Phase_zero/phase0_10_00_paths.py` |
| **Re-export Utility** | `src/farfan_pipeline/utils/paths.py` |
| **Project Root Marker** | `pyproject.toml` |

---

## 2. Path Infrastructure Architecture

### 2.1 Project Root Detection Strategy

```python
# name: project_root_detection.py
from pathlib import Path

def _detect_project_root() -> Path:
    """
    Multi-strategy project root detection:

    1. PRIMARY: Search for pyproject.toml (walk up from file location)
    2. SECONDARY: Search for src/farfan_pipeline + setup.py layout
    3. FALLBACK: Relative path calculation (3 levels up)
    """
    current = Path(__file__).resolve().parent

    # Strategy 1: Find pyproject.toml
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
        # Strategy 2: Legacy layout
        if (
            ((parent / "src" / "farfan_pipeline").exists() or
             (parent / "src" / "farfan_core").exists())
            and (parent / "setup.py").exists()
        ):
            return parent

    # Strategy 3: Fallback
    return current.parent.parent.parent
```

### 2.2 Directory Constants

The system defines these **critical path constants** (from `phase0_10_00_paths.py`):

```python
# name: path_constants.py
from pathlib import Path
from typing import Final

# Core directories
PROJECT_ROOT: Final[Path] = _detect_project_root()
SRC_DIR: Final[Path] = PROJECT_ROOT / "src"
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
TESTS_DIR: Final[Path] = PROJECT_ROOT / "tests"
CONFIG_DIR: Final[Path] = PROJECT_ROOT / "canonic_questionnaire_central"

# Questionnaire paths
QUESTIONNAIRE_FILE: Final[Path] = CONFIG_DIR / "questionnaire_monolith.json"
QUESTIONNAIRE_ROOT: Final[Path] = CONFIG_DIR
QUESTIONNAIRE_ENTRY_POINT: Final[Path] = CONFIG_DIR / "questionnaire_monolith.json"
QUESTIONNAIRE_INDEX_FILE: Final[Path] = CONFIG_DIR / "index/index.json"
QUESTIONNAIRE_GOVERNANCE_FILE: Final[Path] = CONFIG_DIR / "governance/governance.json"
QUESTIONNAIRE_VALIDATION_TEMPLATES_FILE: Final[Path] = CONFIG_DIR / "validations/validation_templates.json"
```

---

## 3. Critical Path Files & Their Roles

### 3.1 Primary Path Module

**Location:** `src/farfan_pipeline/phases/Phase_zero/phase0_10_00_paths.py`

```python
"""
Central path resolution for all F.A.R. F.A.N directories.

CRITICALITY: CRITICAL
EXECUTION PATTERN: Singleton (module-level constants)

Exports:
- PROJECT_ROOT, SRC_DIR, DATA_DIR, TESTS_DIR, CONFIG_DIR
- proj_root(), src_dir(), data_dir(), tmp_dir(), build_dir(), cache_dir(), reports_dir()
- is_within(), safe_join(), normalize_unicode(), normalize_case()
- validate_read_path(), validate_write_path()
- get_env_path(), get_workdir(), get_tmpdir(), get_reports_dir()
"""
```

### 3.2 Re-export Module (Convenience Import)

**Location:** `src/farfan_pipeline/utils/paths.py`

```python
"""Path helpers (single source of truth).

Re-exported from `farfan_pipeline.phases.Phase_zero.phase0_10_00_paths`.
"""
from farfan_pipeline.phases.Phase_zero.phase0_10_00_paths import (
    PROJECT_ROOT,
    SRC_DIR,
    DATA_DIR,
    # ... all other exports
)
```

---

## 4. Common Path Issues & Repairs

### 4.1 ❌ Issue: Hardcoded Absolute Paths

**BAD (found in scripts):**
```python
# scripts/audit/part1_empirical_alignment_audit_sota.py
ROOT = Path("/Users/recovered/FARFAN_MPP")  # ❌ HARDCODED!
```

**✅ REPAIR:**
```python
from farfan_pipeline.utils.paths import PROJECT_ROOT
ROOT = PROJECT_ROOT  # ✅ Dynamic detection
```

### 4.2 ❌ Issue: Manual sys.path Manipulation

**BAD (found in multiple scripts):**
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))  # ❌ Fragile
```

**✅ REPAIR:**
```python
# Option 1: Use proper package installation
# pip install -e .

# Option 2: If script MUST manipulate path, use relative to file
import sys
from pathlib import Path

# Robust detection
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent  # Adjust levels as needed

if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))
```

### 4.3 ❌ Issue: Incorrect Import Paths

**BAD (deprecated):**
```python
from canonic_phases.Phase_zero import paths  # ❌ Old package name
```

**✅ REPAIR:**
```python
from farfan_pipeline.phases.Phase_zero.phase0_10_00_paths import PROJECT_ROOT  # ✅
# OR use the utility re-export:
from farfan_pipeline.utils.paths import PROJECT_ROOT  # ✅ Preferred
```

### 4.4 ❌ Issue: Path Traversal Vulnerabilities

**BAD:**
```python
user_path = Path(user_input)  # ❌ Unvalidated
file_path = DATA_DIR / user_path
```

**✅ REPAIR:**
```python
from farfan_pipeline.utils.paths import safe_join, validate_read_path

# Safe path construction
file_path = safe_join(DATA_DIR, user_input)  # ✅ Blocks traversal

# Validate before use
validate_read_path(file_path)  # ✅ Raises PathError if invalid
```

---

## 5. Python Path (PYTHONPATH) Configuration

### 5.1 Package Structure

From `pyproject.toml`:
```toml
[tool.setuptools.packages.find]
where = ["src"]
include = [
    "farfan_pipeline*",
    # Legacy compatibility shims
    "canonic_phases",
    "orchestration",
    "cross_cutting_infrastructure",
    "methods_dispensary",
    "dashboard_atroz_",
]
```

### 5.2 Correct PYTHONPATH Setup

#### For Development:
```bash
# From project root
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"

# Or install in editable mode (RECOMMENDED)
pip install -e .
```

#### For Scripts:
```bash
# run_pipeline.sh already sets this:
export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"
```

#### For Tests:
```bash
# Run from project root
PYTHONPATH=src pytest tests/
```

### 5.3 Import Hierarchy

```
✅ CORRECT Import Paths:
───────────────────────────────────────────────────
from farfan_pipeline.phases.Phase_zero.phase0_10_00_paths import PROJECT_ROOT
from farfan_pipeline.utils.paths import safe_join
from farfan_pipeline.infrastructure.calibration import CalibrationCore

❌ DEPRECATED Import Paths (still work via shims):
───────────────────────────────────────────────────
from canonic_phases.Phase_zero import paths  # Legacy shim
from methods_dispensary.derek_beach import DerekBeach  # Legacy shim
```

---

## 6. Path Audit Checklist

### 6.1 Pre-Audit Verification

Run these commands from project root:

```bash
# 1. Verify pyproject.toml exists (primary marker)
ls -la pyproject.toml

# 2. Verify src structure
ls -la src/farfan_pipeline/

# 3. Verify path module exists
ls -la src/farfan_pipeline/phases/Phase_zero/phase0_10_00_paths.py

# 4. Check for hardcoded paths
grep -r "Path(\"/Users" --include="*.py" .
grep -r "Path(\"/home" --include="*.py" .
grep -r 'C:\\\\' --include="*.py" .
```

### 6.2 Automated Audit Script

Use the automated audit script located at `scripts/audit/path_audit.py`:

```bash
# Run from project root
python scripts/audit/path_audit.py
```

The script checks for:
- Hardcoded absolute paths
- Deprecated import paths
- Manual sys.path manipulation
- Inappropriate use of `os.getcwd()`

---

## 7. Repair Procedures

### 7.1 Fixing Broken Imports

Search and replace patterns for import fixes:

```python
# Old pattern -> New pattern
REPLACEMENTS = {
    "from canonic_phases.Phase_zero.paths import":
        "from farfan_pipeline.utils.paths import",

    "from canonic_phases.Phase_zero import paths":
        "from farfan_pipeline.utils import paths",

    "from src.farfan_pipeline":
        "from farfan_pipeline",

    "import canonic_phases":
        "import farfan_pipeline.phases",
}
```

### 7.2 Fixing Hardcoded Paths

```python
# BEFORE (hardcoded):
ROOT = Path("/Users/recovered/FARFAN_MPP")
CQC_ROOT = ROOT / "canonic_questionnaire_central"
PLANS_ROOT = ROOT / "data" / "plans"

# AFTER (dynamic):
from farfan_pipeline.utils.paths import PROJECT_ROOT, CONFIG_DIR, DATA_DIR

ROOT = PROJECT_ROOT
CQC_ROOT = CONFIG_DIR  # Already defined as canonic_questionnaire_central
PLANS_ROOT = DATA_DIR / "plans"
```

### 7.3 Fixing Test Path Setup

**Location:** `tests/conftest.py`

```python
"""
Pytest configuration - ensures correct path setup
"""
import sys
from pathlib import Path

# Ensure src is in path for test discovery
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC_DIR = _REPO_ROOT / "src"

if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# Also ensure repo root for legacy imports
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
```

---

## 8. Best Practices & Standards

### 8.1 Path Construction Rules

| Rule | Example |
|------|---------|
| **Always use `pathlib.Path`** | `Path("data") / "file.json"` |
| **Never string concatenation** | ❌ `"/data/" + filename` |
| **Use constants from paths module** | `from farfan_pipeline.utils.paths import DATA_DIR` |
| **Validate user-provided paths** | `validate_read_path(user_path)` |
| **Use `safe_join` for untrusted input** | `safe_join(base, *parts)` |

### 8.2 Import Standards

```python
# ✅ PREFERRED: Use utility re-export
from farfan_pipeline.utils.paths import (
    PROJECT_ROOT,
    DATA_DIR,
    CONFIG_DIR,
    safe_join,
    validate_read_path,
)

# ✅ ACCEPTABLE: Direct import from source
from farfan_pipeline.phases.Phase_zero.phase0_10_00_paths import PROJECT_ROOT

# ❌ AVOID: Legacy shims (deprecated)
from canonic_phases.Phase_zero import paths
```

### 8.3 Error Classes

The path module defines these exceptions for proper error handling:

```python
from farfan_pipeline.utils.paths import (
    PathError,                   # Base exception
    PathTraversalError,          # Path escape attempt detected
    PathNotFoundError,           # Path does not exist
    PathOutsideWorkspaceError,   # Path outside allowed workspace
    UnnormalizedPathError,       # Path not properly normalized
)
```

### 8.4 Environment Variable Accessors

```python
from farfan_pipeline.utils.paths import (
    get_env_path,      # Get path from environment variable
    get_workdir,       # Get current working directory (validated)
    get_tmpdir,        # Get temp directory (project-local)
    get_reports_dir,   # Get reports output directory
)
```

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────────────┐
│  F.A.R. F.A.N PATH QUICK REFERENCE                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  IMPORT:                                                         │
│    from farfan_pipeline.utils.paths import PROJECT_ROOT         │
│                                                                  │
│  CONSTANTS:                                                      │
│    PROJECT_ROOT  → Repository root                              │
│    SRC_DIR       → src/ directory                               │
│    DATA_DIR      → data/ directory                              │
│    CONFIG_DIR    → canonic_questionnaire_central/               │
│    TESTS_DIR     → tests/ directory                             │
│                                                                  │
│  FUNCTIONS:                                                      │
│    safe_join(base, *parts) → Safe path construction             │
│    validate_read_path(p)   → Validate before reading            │
│    validate_write_path(p)  → Validate before writing            │
│    is_within(base, child)  → Check containment                  │
│                                                                  │
│  PYTHONPATH:                                                     │
│    export PYTHONPATH="$PWD/src:$PYTHONPATH"                     │
│    OR: pip install -e .                                         │
│                                                                  │
│  RUN TESTS:                                                      │
│    PYTHONPATH=src pytest tests/                                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Phase 1: Audit (Week 1)
- [ ] Run automated audit script
- [ ] Document all hardcoded paths
- [ ] Identify deprecated import patterns
- [ ] Create issue list with file:line references

### Phase 2: Repair (Week 2-3)
- [ ] Fix hardcoded paths in scripts/
- [ ] Update deprecated imports across codebase
- [ ] Remove manual sys.path manipulations
- [ ] Update test configurations

### Phase 3: Validation (Week 4)
- [ ] Re-run audit script (should pass clean)
- [ ] Execute full test suite
- [ ] Verify all scripts work with dynamic paths
- [ ] Update documentation

### Phase 4: Enforcement (Ongoing)
- [ ] Add path audit to pre-commit hooks
- [ ] Document path standards in CONTRIBUTING.md
- [ ] Train team on centralized path management
- [ ] Regular quarterly audits

---

## Related Documentation

- **Path Module Source:** `src/farfan_pipeline/phases/Phase_zero/phase0_10_00_paths.py`
- **Utility Re-export:** `src/farfan_pipeline/utils/paths.py`
- **Package Configuration:** `pyproject.toml`
- **Test Configuration:** `tests/conftest.py`
- **Audit Script:** `scripts/audit/path_audit.py`

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-09 | Claude | Initial comprehensive specification |

---

## Support & Contact

For questions or issues related to path management:
1. Review this specification guide
2. Check the path module source code
3. Run the automated audit script
4. Create an issue in the GitHub repository

**Remember:** The path module is the **single source of truth**. Always import from `farfan_pipeline.utils.paths` or the primary module directly.
