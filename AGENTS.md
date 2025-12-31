# F.A.R.F.A.N AI Agent Instructions

**Document:** AGENTS.md  
**Version:** 2.0.0  
**Date:** 2025-12-30  
**Status:** MANDATORY  
**Compliance:** GNEA (Global Nomenclature Enforcement Architecture)

---

## ⚠️ CRITICAL: READ BEFORE ANY FILE OPERATION

This document establishes **MANDATORY** rules for AI agents working in this repository.
**Violations will pollute the codebase.** Reference: `GLOBAL_NAMING_POLICY.md` (GNEA v2.0.0)

---

## 1. ABSOLUTE PROHIBITIONS

### 🚫 NEVER CREATE FILES IN ROOT DIRECTORY
The following file types are **FORBIDDEN** in the repository root:
- Python scripts (`*.py`) except: `RUN_PIPELINE.py`, `setup.py`, `_install_deps.py`
- JSON data files (`*.json`)
- Shell scripts (`*.sh`) except: `install.sh`, `run_pipeline.sh`
- Markdown files (`*.md`) except: `README.md`, `README.ES.md`, `CHANGELOG.md`, `AGENTS.md`, `DEPENDENCIES.md`, `GLOBAL_NAMING_POLICY.md`

### 🚫 FORBIDDEN DIRECTORY NAMES
Never create directories named: `temp`, `tmp`, `backup`, `old`, `misc`, `other`, `stuff`, `things`, `new`, `test` (root level)

### 🚫 FORBIDDEN FILE PATTERNS
- `*_backup.py`, `*_old.py`, `*_new.py`, `*_temp.py`
- `copy_of_*`, `test_*` (outside `tests/` directories)
- Numbered versions like `script_v2.py`, `module_2.py`

---

## 2. WHERE TO PUT FILES

### Scripts → `scripts/`
```
scripts/
├── audit/          # audit_*.py
├── validation/     # validate_*.py, check_*.py
├── transformation/ # transform_*.py, convert_*.py
├── evaluation/     # evaluate_*.py, assess_*.py
├── generation/     # generate_*.py, create_*.py
└── misc/           # Other utility scripts
```

### Data/JSON → `artifacts/`
```
artifacts/
├── data/           # JSON data files, mappings
│   ├── contracts/  # Contract definitions
│   └── methods/    # Method configurations
└── reports/        # Generated reports
    ├── audit/      # Audit reports
    └── cqvr/       # CQVR evaluation reports
```

### Documentation → `docs/`
```
docs/
├── architecture/   # System design docs
├── implementation/ # Implementation details
├── phase_specs/    # Phase specifications
└── reports/        # Analysis reports (markdown)
```

### Phase Code → `src/farfan_pipeline/phases/Phase_{name}/`
Each phase MUST have:
- `PHASE_{N}_MANIFEST.json` - Phase manifest
- `PHASE_{N}_CONSTANTS.py` - Phase constants
- `__init__.py` - Package init
- `tests/` - Phase tests
- `contracts/` - Phase contracts
- `docs/` - Phase documentation

---

## 3. NAMING CONVENTIONS

### Phase Modules (STRICT)
Pattern: `phase{N}_{SS}_{OO}_{name}.py`
- `{N}` = Phase number (0-9)
- `{SS}` = Stage (00, 10, 20, ..., 90)
- `{OO}` = Order within stage (00, 01, 02, ...)
- `{name}` = lowercase_with_underscores

✅ `phase2_10_00_factory.py`  
✅ `phase0_40_01_schema_monitor.py`  
❌ `factory.py`  
❌ `Phase2Factory.py`

### Contracts (STRICT)
Pattern: `Q{NNN}_{policy_area}_executor_contract.json`
- `{NNN}` = Zero-padded question number (001-300)
- `{policy_area}` = lowercase policy area identifier

✅ `Q001_fiscal_executor_contract.json`  
❌ `contract_1.json`

### Documentation
Pattern: `{CATEGORY}_{TOPIC}.md` (uppercase for formal docs)

✅ `PHASE_2_ARCHITECTURE.md`  
✅ `CQVR_EVALUATION_REPORT.md`  
❌ `notes.md`

---

## 4. PHASE STRUCTURE REQUIREMENTS

Every phase directory MUST follow this structure:
```
src/farfan_pipeline/phases/Phase_{name}/
├── PHASE_{N}_MANIFEST.json    # ✅ MANDATORY
├── PHASE_{N}_CONSTANTS.py     # ✅ MANDATORY
├── __init__.py                # ✅ MANDATORY
├── tests/                     # ✅ MANDATORY
├── contracts/                 # ✅ MANDATORY
└── docs/                      # ✅ MANDATORY
```

### Existing Phases
- `Phase_zero` - Validation & Bootstrap (Phase 0)
- `Phase_two` - Executor Contract Factory (Phase 2)
- `Phase_eight` - Recommendation Engine (Phase 8)
- `Phase_nine` - Report Generation (Phase 9)

---

## 5. BEFORE CREATING ANY FILE

**ASK YOURSELF:**
1. Does this file already exist? → **Search first**
2. Is this the correct directory? → **Check Section 2**
3. Does the name follow conventions? → **Check Section 3**
4. Am I polluting root? → **STOP if yes**

**VALIDATION COMMAND:**
```bash
# Check root pollution
ls *.py *.json *.sh *.md 2>/dev/null | wc -l
# Should be ≤ 12 files
```

---

## 6. DEVELOPER QUICK REFERENCE

### Setup
```bash
python3.12 -m venv farfan-env
source farfan-env/bin/activate
pip install -e .
```

### Commands
- **Lint**: `ruff check farfan_core/`
- **Type Check**: `mypy farfan_core/farfan_core/core/`
- **Test**: `pytest tests/` or `pytest -m "updated and not outdated" -v`
- **Dev Server**: `python farfan_core/farfan_core/api/api_server.py`

### Tech Stack
- Python 3.12, FastAPI, Pydantic, transformers
- PyMC (Bayesian), scikit-learn, NetworkX, spaCy
- pytest, ruff, mypy, black

### Code Style
- Strict typing (mypy/Pyright strict mode)
- No comments unless complex logic
- 100-char line length
- Deterministic execution (seed=42)

---

## 7. SYNCHRONIZATION RULES

### Critical Files (MUST stay synchronized)
- `METHODS_TO_QUESTIONS_AND_FILES.json` ↔ `METHODS_OPERACIONALIZACION.json`
  - Both MUST have exactly **240 methods**
  - Never create partial versions

### Contract-Method Alignment
- 30 base questions × 10 policy areas = **300 contracts**
- 240 methods in dispensary
- All contracts must reference valid methods

---

## 8. COMMIT MESSAGE FORMAT

```
{type}: {description}

Types: feat, fix, refactor, docs, test, chore
```

Examples:
- `feat: Add Phase 8 recommendation engine`
- `fix: Correct contract binding for Q015`
- `docs: Update GNEA compliance documentation`

---

## ENFORCEMENT

This policy is enforced by:
1. Pre-commit hooks (planned)
2. CI/CD validation (planned)
3. **AI Agent self-compliance** (ACTIVE)

**Reference:** `GLOBAL_NAMING_POLICY.md` for complete GNEA specification.

---

*Last updated: 2025-12-30 by GNEA compliance restructuring*