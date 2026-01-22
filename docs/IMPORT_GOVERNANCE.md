# F.A.R.F.A.N Import Governance and Python Path Configuration

## Table of Contents
1. [Project Structure](#project-structure)
2. [Python Path Configuration](#python-path-configuration)
3. [Import Standards](#import-standards)
4. [Import Patterns](#import-patterns)
5. [Anti-Patterns](#anti-patterns)
6. [Migration Guide](#migration-guide)

---

## Project Structure

```
FARFAN_MCDPP/
├── src/
│   └── farfan_pipeline/          # Main package (regular package with __init__.py)
│       ├── __init__.py           # ✅ Now present
│       ├── orchestration/
│       ├── phases/
│       │   ├── Phase_00/
│       │   ├── Phase_02/
│       │   └── ...
│       ├── methods/
│       ├── core/
│       ├── calibration/
│       ├── infrastructure/
│       └── ...
├── canonic_questionnaire_central/  # Top-level package
├── tests/
├── scripts/
├── pyproject.toml
└── setup.py
```

---

## Python Path Configuration

### Development Environment

Your PYTHONPATH should include:

```bash
# Option 1: Add both src/ and root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src:$(pwd)"

# Option 2: Use the provided activation script
source scripts/activate.sh
```

### Configuration Files

**pyproject.toml** (already configured):
```toml
[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["."]  # Allows root-level imports
```

**setup.py** (already configured):
```python
setup(
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
```

---

## Import Standards

### 1. Absolute Imports (Preferred)

```python
# ✅ GOOD - Clear, unambiguous
from farfan_pipeline.orchestration import UnifiedOrchestrator
from farfan_pipeline.phases.Phase_02 import BaseExecutorWithContract
from farfan_pipeline.methods import TextMiningEngine
from canonic_questionnaire_central import CQCLoader

# ✅ GOOD - Specific imports
from farfan_pipeline.orchestration.orchestrator import (
    UnifiedOrchestrator,
    OrchestratorConfig,
)
```

### 2. Relative Imports (For intra-package use only)

```python
# ✅ GOOD - Within the same subpackage
from .orchestrator import UnifiedOrchestrator
from ..core import UnitOfAnalysis

# ⚠️ ONLY use when:
# - Importing within the same package (farfan_pipeline)
# - The import is local to the module
# - You want to avoid circular dependencies
```

### 3. Import Grouping

Organize imports in this order:

```python
# 1. Standard library imports
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

# 2. Third-party imports
import numpy as np
import pandas as pd
from pydantic import BaseModel

# 3. Local application imports (farfan_pipeline)
from farfan_pipeline.core import UnitOfAnalysis
from farfan_pipeline.orchestration import UnifiedOrchestrator

# 4. Local application imports (other top-level packages)
from canonic_questionnaire_central import CQCLoader
```

---

## Import Patterns

### Pattern 1: Importing from farfan_pipeline

```python
# ✅ Use absolute imports
from farfan_pipeline.orchestration import UnifiedOrchestrator
from farfan_pipeline.phases.Phase_02 import BaseExecutorWithContract
from farfan_pipeline.methods.analyzer_one import TextMiningEngine
```

### Pattern 2: Importing from canonic_questionnaire_central

```python
# ✅ Direct import (works from project root or with PYTHONPATH configured)
from canonic_questionnaire_central import CQCLoader, CQCConfig
from canonic_questionnaire_central.constants import POLICY_AREAS
```

### Pattern 3: Importing within phases

```python
# In farfan_pipeline/phases/Phase_02/some_module.py

# ✅ GOOD - Absolute import
from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import create_executor

# ✅ ALSO GOOD - Relative import (within same package)
from .phase2_10_00_factory import create_executor
from ..Phase_00.phase0_00_01_runtime_error_fixes import ensure_list_return
```

### Pattern 4: Conditional imports

```python
# ✅ GOOD - For optional dependencies
try:
    from farfan_pipeline.analysis.factory import load_spacy_model
except ImportError:
    # Fallback or error handling
    raise ImportError("Spacy not installed. Install with: pip install spacy")

# ✅ GOOD - For backward compatibility
try:
    from farfan_pipeline.calibration.pdm_calibrator import CalibrationResult
    _has_calibration = True
except ImportError:
    _has_calibration = False
```

---

## Anti-Patterns

### ❌ DON'T: Bare relative imports at module level

```python
# ❌ BAD - Ambiguous
from factory import create_executor  # Where is factory?
from .factory import create_executor  # Only if factory is sibling
```

### ❌ DON'T: Import from analysis module (deprecated)

```python
# ❌ BAD - analysis.factory is deprecated
from farfan_pipeline.analysis.factory import load_spacy_model

# ✅ GOOD - Use infrastructure/dependencies
from farfan_pipeline.infrastructure.dependencies import get_dependency
spacy = get_dependency("spacy")
```

### ❌ DON'T: Deep relative imports

```python
# ❌ BAD - Too many dots, hard to read
from ....phases.Phase_00 import something

# ✅ GOOD - Use absolute import
from farfan_pipeline.phases.Phase_00 import something
```

### ❌ DON'T: Mixed import styles

```python
# ❌ BAD - Inconsistent
from farfan_pipeline.orchestration import UnifiedOrchestrator
from .orchestrator import PhaseID  # Don't mix absolute and relative

# ✅ GOOD - Be consistent
from farfan_pipeline.orchestration import UnifiedOrchestrator, PhaseID
```

---

## Migration Guide

### For Existing Code

If you have existing code with old import patterns:

1. **Replace deprecated imports:**
   ```python
   # OLD
   from farfan_pipeline.analysis.factory import load_json

   # NEW
   from farfan_pipeline.infrastructure.dependencies import get_dependency
   json_loader = get_dependency("json")
   ```

2. **Add root to PYTHONPATH if needed:**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/src"
   ```

3. **Run the import validator:**
   ```bash
   python scripts/validate_imports.py
   ```

### For New Code

1. **Always use absolute imports** for cross-package imports
2. **Use relative imports** only within the same subpackage
3. **Follow import grouping** standards (stdlib → third-party → local)
4. **Run linters** before committing:
   ```bash
   ruff check --select I  # Check import ordering
   ```

---

## Verification

### Run path audit:
```bash
python3 scripts/path_audit.py
```

### Validate imports:
```bash
python3 scripts/validate_imports.py
```

### Test imports:
```python
# Test that all imports work
python -c "
from farfan_pipeline.orchestration import UnifiedOrchestrator
from farfan_pipeline.phases.Phase_02 import BaseExecutorWithContract
from canonic_questionnaire_central import CQCLoader
print('All imports successful!')
"
```

---

## Appendix: Complete Package Reference

### farfan_pipeline.*
| Module | Purpose |
|--------|---------|
| `orchestration` | Pipeline orchestration and coordination |
| `phases` | Analysis phases (Phase_00 through Phase_09) |
| `methods` | Epistemological methods (N1/N2/N3 levels) |
| `core` | Core types and canonical notation |
| `calibration` | Bayesian calibration and validation |
| `infrastructure` | Infrastructure services and dependencies |
| `api` | FastAPI endpoints |
| `utils` | Utility functions |
| `data_models` | Pydantic models |

### canonic_questionnaire_central.*
| Module | Purpose |
|--------|---------|
| `resolver` | Question resolution and routing |
| `constants` | Policy area constants |
| `core.signal` | Signal distribution system |
| `policy_areas` | Policy area definitions |

---

*Last updated: 2026-01-21*
*Version: 1.0.0*
