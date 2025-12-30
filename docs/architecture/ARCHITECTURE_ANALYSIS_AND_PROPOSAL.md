# Architecture Analysis and Proposal

## 1. Granular Analysis of Current Paths and Python Paths

An in-depth investigation of the repository structure (`src/` and `tests/`) reveals significant fragmentation, inconsistent naming conventions, and "kitchen sink" organization patterns.

### 1.1 Top-Level Namespace Pollution
The `src/` directory currently contains **10 top-level packages**, which pollutes the global Python namespace and makes installation/distribution difficult.

**Current Top-Level Packages:**
- `batch_concurrence/`
- `calibration/`
- `canonic_phases/` (Core logic)
- `core/` (Empty or redundant)
- `cross_cutting_infrastructure/` (Note: widely imported with a typo)
- `dashboard_atroz_/` (Trailing underscore)
- `farfan_pipeline/` (Intended package name per `setup.py` but underutilized)
- `methods_dispensary/` (Analysis methods)
- `ontology/`
- `orchestration/` (Core orchestration logic)

**Impact:**
- `sys.path` must include `src/` directly.
- Imports are verbose and disconnected (e.g., `from orchestration.orchestrator import ...` vs `from farfan.core import ...`).

### 1.2 Naming Inconsistencies (Labeling)
There is no consistent naming convention for directories or files.

- **Phases**:
  - `Phase_one` (Title Case, Number word)
  - `Phase_four_five_six_seven` (Extremely long, mixed numbers)
  - `Phase_zero`
- **Dashboard**:
  - `dashboard_atroz_` (Unnecessary trailing underscore)
- **Files**:
  - `contradiction_deteccion.py` (Spanglish/Typo)
  - `financiero_viabilidad_tablas copy.py` (Backup file committed)
  - `derek_beach.py` (Named after a person/author rather than functionality)

### 1.3 The "Infrastrucuture" Typo
A critical issue exists where the directory on disk is named `src/cross_cutting_infrastructure` (correct), but a vast number of imports (especially in tests) refer to `cross_cutting_infrastrucuture` (typo). This causes `ImportError` unless `sys.modules` is patched or the directory is symlinked.

**Evidence:**
- `tests/test_layer_metadata_completeness.py`: `from cross_cutting_infrastrucuture...`
- `tests/calibration/conftest.py`: `from cross_cutting_infrastrucuture...`

### 1.4 Test Organization
The `tests/` directory is partially mirrored (`tests/canonic_phases`) but largely cluttered with root-level files (`tests/choquet_tests.py`, `tests/test_phase0_complete.py`). This makes it hard to run subsets of tests or verify specific components.

---

## 2. Issues and Anti-Patterns

1.  **Multiple Roots**: There is no single source of truth for the package. `farfan_pipeline` exists but isn't the parent of `canonic_phases`.
2.  **Stringly Typed Paths**: `src/canonic_phases/Phase_zero/paths.py` contains complex logic to "guess" the project root because the structure is unstable.
3.  **Circular/Confused Dependencies**: `Phase_zero` tests import from `Phase_one` (`phase0_input_validation`).
4.  **Language Mixing**: File names like `financiero_viabilidad_tablas.py` mixed with `analyzer_one.py`.
5.  **Grouping**:
    - `methods_dispensary` contains everything from "Bayesian systems" to "Derek Beach" methods.
    - `orchestration` contains `orchestrator.py` but also `memory_safety.py`.

---

## 3. Proposed Final Architecture

The following architecture aligns with industrial best practices for **grouping** (by feature/layer), **foldering** (hierarchical), and **labeling** (snake_case, descriptive).

### 3.1 Root Package: `farfan`
All code moves under a single top-level package `farfan`.

```
src/
└── farfan/
    ├── __init__.py
    ├── core/                 # Core domain logic
    │   ├── __init__.py
    │   ├── orchestration/    # Was src/orchestration
    │   │   ├── engine.py     # Was orchestrator.py
    │   │   └── ...
    │   ├── config.py
    │   └── events.py
    ├── phases/               # Was src/canonic_phases
    │   ├── __init__.py
    │   ├── phase_00_config/  # Was Phase_zero
    │   ├── phase_01_ingestion/# Was Phase_one
    │   ├── phase_02_analysis/# Was Phase_two
    │   ├── phase_03_scoring/ # Was Phase_three
    │   ├── phase_04_aggregation/ # Was Phase_four_five_six_seven (split internally or kept)
    │   └── ...
    ├── analysis/             # Was src/methods_dispensary + src/calibration
    │   ├── __init__.py
    │   ├── methods/          # Specific analysis methods
    │   │   ├── bayesian.py
    │   │   └── contradiction.py # Renamed from contradiction_deteccion
    │   ├── calibration/      # Was src/calibration
    │   └── ontology/         # Was src/ontology
    ├── infrastructure/       # Was src/cross_cutting_infrastructure
    │   ├── __init__.py
    │   ├── sisas/
    │   └── contracts/
    ├── dashboard/            # Was src/dashboard_atroz_
    │   ├── __init__.py
    │   ├── app.py
    │   └── ingestion.py
    └── utils/                # Shared utilities
        ├── __init__.py
        ├── paths.py
        └── concurrency.py    # Was src/batch_concurrence
```

### 3.2 Key Changes

1.  **Standardized Labeling**:
    - `Phase_one` -> `phase_01_ingestion` (snake_case + numeric sortable + descriptive).
    - `dashboard_atroz_` -> `dashboard`.
    - `cross_cutting_infrastructure` -> `infrastructure`.
2.  **Grouping**:
    - All analysis methods (Derek Beach, Bayesian, etc.) move to `farfan.analysis.methods`.
    - All orchestration logic stays in `farfan.core.orchestration`.
3.  **Fixing Typos**:
    - `cross_cutting_infrastrucuture` -> `infrastructure`.
    - `contradiction_deteccion.py` -> `contradiction.py`.

---

## 4. Implementation Plan

### Step 1: Create Structure
Create the `src/farfan` directory tree.

### Step 2: Move and Rename
Move files to their new locations, renaming them to follow snake_case conventions.
- `src/orchestration/*` -> `src/farfan/core/orchestration/*`
- `src/canonic_phases/*` -> `src/farfan/phases/*`
- `src/methods_dispensary/*` -> `src/farfan/analysis/methods/*`
- `src/cross_cutting_infrastructure/*` -> `src/farfan/infrastructure/*`

### Step 3: Refactor Imports
This is the most critical step. Using `sed` or refactoring tools, update all imports.
- `from orchestration import ...` -> `from farfan.core.orchestration import ...`
- `from cross_cutting_infrastrucuture import ...` -> `from farfan.infrastructure import ...`
- `from canonic_phases.Phase_one import ...` -> `from farfan.phases.phase_01_ingestion import ...`

### Step 4: Fix Tests
Move `tests/` to mirror `src/farfan/` and update their imports.

### Step 5: Update Configuration
Update `setup.py` to point to `farfan` package. Update `pytest.ini` or scripts.

## 5. Summary of Benefits
- **Predictability**: Developers know exactly where to find code (Analysis? -> `farfan.analysis`).
- **Maintainability**: Typos are eliminated; naming is consistent.
- **Scalability**: New phases or tools have a clear home.
- **Pythonic**: Adheres to PEP 8 package naming standards.
