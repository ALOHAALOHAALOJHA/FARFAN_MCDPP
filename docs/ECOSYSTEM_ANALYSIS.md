# F.A.R.F.A.N Ecosystem Analysis & Surgical Improvements
# =====================================================

**Date:** 2026-01-21
**Scope:** Import patterns, factory alignment, dependency injection, and ecosystem integration

---

## Executive Summary

This document analyzes the F.A.R.F.A.N ecosystem following the recent path/PYTHONPATH overhaul and proposes surgical improvements for alignment across all modules.

---

## 1. Current Ecosystem State

### 1.1 Package Structure (Post-Overhaul)

```
src/farfan_pipeline/
├── __init__.py              ✅ NOW: Regular package with exports
├── orchestration/
│   ├── __init__.py          ✅ Well-structured
│   ├── factory.py           ✅ UnifiedFactory (single source of truth)
│   ├── orchestrator.py      ✅ UnifiedOrchestrator
│   ├── method_registry.py   ⚠️  Stub - needs real implementation
│   └── ...
├── phases/
│   ├── __init__.py          ✅ NOW: Exports PhaseID, PhaseStatus
│   ├── Phase_00/            ✅ Foundation phase
│   ├── Phase_02/
│   │   ├── __init__.py      ✅ Exports key classes
│   │   ├── phase2_10_00_factory.py  ⚠️  DEPRECATED - redirects to UnifiedFactory
│   │   └── ...
│   └── ...
├── methods/
│   ├── __init__.py          ✅ NOW: Exports analyzer classes
│   ├── analyzer_one.py
│   ├── derek_beach.py
│   └── ...
├── core/
│   ├── __init__.py          ✅ NOW: Exports CategoriaCausal, types
│   └── types.py             ✅ Core enumerations
├── calibration/
│   ├── __init__.py          ✅ NOW: Exports CalibrationResult, PDPCalibrator
│   └── ...
├── infrastructure/
│   ├── __init__.py          ✅ Well-structured
│   ├── dependencies.py      ✅ SINGLE SOURCE OF TRUTH for dependencies
│   └── ...
└── ...

canonic_questionnaire_central/   ✅ Top-level package (works from root)
```

---

## 2. Key Findings

### 2.1 Import Pattern Analysis

| Pattern | Count | Status | Notes |
|---------|-------|--------|-------|
| `from farfan_pipeline.orchestration` | 402 files | ✅ Good | Absolute imports working |
| `from canonic_questionnaire_central` | 45 files | ✅ Good | Top-level imports working |
| `from . import` | 7 files | ✅ Good | Relative imports within packages |
| `from .. import` | 1 file | ⚠️ Review | Parent imports - ensure no circular deps |

### 2.2 Factory Pattern Alignment

**Current State:**
- `orchestration/factory.py`: ✅ UnifiedFactory (SINGLE SOURCE OF TRUTH)
- `phases/Phase_02/phase2_10_00_factory.py`: ⚠️ DEPRECATED - redirects to UnifiedFactory
- Legacy functions in `orchestration/factory.py`: ✅ Provide backward compatibility

**Issue:** Some files may still import from the deprecated factory.

### 2.3 Method Registry State

**Current State:**
- `orchestration/method_registry.py`: ⚠️ STUB - Doesn't actually instantiate classes
- `methods/` directory: ✅ Contains 17 analyzer modules
- `METHODS_TO_QUESTIONS_AND_FILES.json`: ✅ 237 methods mapped

**Issue:** MethodRegistry is a stub that doesn't integrate with actual methods.

### 2.4 Infrastructure Dependencies

**Current State:**
- `infrastructure/dependencies.py`: ✅ SINGLE SOURCE OF TRUTH
- Deprecated `analysis.factory` imports: ❌ Still present in some files

**Issue:** Some files still import from deprecated `farfan_pipeline.analysis.factory`.

---

## 3. Surgical Improvements

### 3.1 Phase 2 Factory Alignment

**Issue:** The `phase2_10_00_factory.py` is deprecated but its exports should be accessible from the main package `__init__.py`.

**Improvement:** Update `phases/Phase_02/__init__.py` to provide clear deprecation warnings while redirecting to UnifiedFactory.

### 3.2 Method Registry Integration

**Issue:** `method_registry.py` is a stub that doesn't actually work.

**Improvement:** Implement proper method registry that integrates with:
- `METHODS_TO_QUESTIONS_AND_FILES.json`
- `METHODS_OPERACIONALIZACION.json`
- Actual method classes in `farfan_pipeline.methods/`

### 3.3 Core Types Alignment

**Issue:** Core types are scattered across `core/types.py` and `data_models/unit_of_analysis.py`.

**Improvement:** The `core/__init__.py` correctly exports from both locations, but we should document this clearly.

### 3.4 Calibration Integration

**Issue:** Calibration module exports may not be visible from main package.

**Improvement:** Ensure calibration exports are accessible via `farfan_pipeline.calibration`.

### 3.5 SISAS Integration

**Issue:** SISAS (Signal Irrigation System) is isolated in `infrastructure/irrigation_using_signals/`.

**Improvement:** Document the integration path and ensure `sisas/__init__.py` exports the public API.

---

## 4. Dependency Layer Separation

**Current State:** Well-defined in `infrastructure/dependencies.py`

**Layers:**
1. NLP: transformers, spacy, sentence-transformers
2. Bayesian: pymc, pytensor
3. PDF: fitz, pdfplumber, pypdf, img2table, tabula
4. API: fastapi, flask

**Status:** ✅ Import linter contracts enforce separation

---

## 5. Recommendations

### 5.1 Immediate Actions

1. ✅ **Completed:** Create `__init__.py` files across all packages
2. ✅ **Completed:** Update `pyproject.toml` with PYTHONPATH configuration
3. ✅ **Completed:** Create environment setup scripts
4. ✅ **Completed:** Create import governance documentation

### 5.2 Next Steps

1. **Implement real MethodRegistry** that integrates with JSON mappings
2. **Audit deprecated imports** from `analysis.factory`
3. **Document calibration exports** in main package
4. **Create SISAS integration guide**
5. **Add type hints** to all public APIs

### 5.3 Long-term

1. Move `canonic_questionnaire_central` to `src/` for consistency
2. Consider consolidating all phases under a single API
3. Implement dependency injection container
4. Add performance monitoring for factory operations

---

## 6. File-by-File Changes Summary

| File | Change | Status |
|------|--------|--------|
| `src/farfan_pipeline/__init__.py` | Created with exports | ✅ |
| `src/farfan_pipeline/methods/__init__.py` | Created with exports | ✅ |
| `src/farfan_pipeline/phases/__init__.py` | Created with exports | ✅ |
| `src/farfan_pipeline/core/__init__.py` | Updated with exports | ✅ |
| `src/farfan_pipeline/calibration/__init__.py` | Created with exports | ✅ |
| `pyproject.toml` | Added pythonpath config | ✅ |
| `scripts/activate.sh` | Created environment script | ✅ |
| `.envrc` | Created direnv config | ✅ |
| `.vscode/settings.json` | Created VS Code config | ✅ |
| `docs/IMPORT_GOVERNANCE.md` | Created import guide | ✅ |
| `docs/MIGRATION_GUIDE.md` | Created migration guide | ✅ |
| `scripts/path_audit.py` | Created audit tool | ✅ |
| `scripts/validate_imports.py` | Created validator | ✅ |

---

## 7. Verification

All imports verified working:
```bash
✅ from farfan_pipeline.orchestration import UnifiedOrchestrator
✅ from canonic_questionnaire_central import CQCLoader
✅ import farfan_pipeline (version: 1.0.0)
✅ from farfan_pipeline.core import CategoriaCausal
```

---

*Last updated: 2026-01-21*
