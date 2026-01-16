# FARFAN Pipeline Layer Architecture

## Overview

The FARFAN pipeline follows a strict layered architecture to ensure separation of concerns and maintainability. This document describes the architectural boundaries and import rules enforced by import-linter.

## Architecture Layers

### 1. Calibration Layer (`farfan_pipeline.calibration`)
- **Purpose**: Core calibration logic and type defaults
- **Cannot Import**: Analysis layers (Phase_04, Phase_06)
- **Can Import**: Utils, data models
- **Status**: ✅ Isolated

### 2. Orchestration Layer (`farfan_pipeline.orchestration`)
- **Purpose**: Pipeline orchestration and CLI
- **Cannot Import**: Specific phase implementations (except via registry)
- **Can Import**: Wiring, calibration, infrastructure
- **Status**: ✅ Isolated

### 3. Processing Layer (`farfan_pipeline.phases.Phase_02`)
- **Purpose**: Data processing and task execution
- **Cannot Import**: Orchestrator (to prevent circular dependencies)
- **Can Import**: Methods, infrastructure, utils
- **Status**: ✅ Isolated

### 4. Analysis Layer (`farfan_pipeline.phases.Phase_04`)
- **Purpose**: Analysis and evidence aggregation
- **Cannot Import**: Orchestrator, infrastructure (direct)
- **Can Import**: Methods, calibration, utils
- **Status**: ✅ Isolated

### 5. Infrastructure Layer (`farfan_pipeline.infrastructure`)
- **Purpose**: Cross-cutting infrastructure (signals, extractors)
- **Cannot Import**: Orchestrator
- **Can Import**: Utils, data models
- **Status**: ✅ Isolated

### 6. Methods Layer (`farfan_pipeline.methods`)
- **Purpose**: Analytical methods and algorithms
- **Cannot Import**: Phases, orchestrator
- **Can Import**: Infrastructure (for document processing)
- **Status**: ⚠️ Partial violation (PDF libraries)

### 7. Utils Layer (`farfan_pipeline.utils`)
- **Purpose**: Shared utilities
- **Cannot Import**: Any business logic layers
- **Can Import**: Only standard libraries and data models
- **Status**: ✅ Isolated

### 8. Dashboard Layer (`farfan_pipeline.dashboard_atroz_`)
- **Purpose**: Web dashboard (Flask-based)
- **Cannot Import**: Pipeline internals (Phase_02, Phase_04)
- **Can Import**: Infrastructure (signals), orchestration entry points
- **Status**: ✅ Isolated

### 9. API Layer (`farfan_pipeline.api`)
- **Purpose**: REST API server (FastAPI-based)
- **Cannot Import**: Dashboard (Flask isolation)
- **Can Import**: Orchestration entry points
- **Status**: ✅ New, isolated

## Dependency Layer Isolation

### NLP vs Bayesian Layers
- **NLP Libraries**: `transformers`, `sentence_transformers`, `spacy`
- **Bayesian Libraries**: `pymc`, `pytensor`, `arviz`
- **Rule**: These should remain isolated to avoid dependency conflicts
- **Status**: ⚠️ Not enforced (would require significant refactoring)

### PDF Processing Centralization
- **PDF Libraries**: `fitz` (PyMuPDF), `pdfplumber`, `pypdf`, `img2table`, `tabula`
- **Rule**: Should only be imported in `farfan_pipeline.infrastructure.extractors`
- **Current Violations**:
  - `farfan_pipeline.methods.derek_beach` imports `fitz`
  - `farfan_pipeline.methods.financiero_viabilidad_tablas` imports `img2table`, `tabula`
  - `farfan_pipeline.phases.Phase_01` modules import `fitz`
- **Status**: ⚠️ Known violation - requires refactoring

### Framework Isolation
- **Flask**: Used only in dashboard
- **FastAPI**: Used only in API layer
- **Rule**: These frameworks should never mix
- **Status**: ✅ Enforced

## Import Linter Contracts

The following contracts are defined in `pyproject.toml`:

1. ✅ **Core (excluding orchestrator) must not import analysis**
2. ✅ **Core orchestrator must not import analysis**
3. ✅ **Processing layer cannot import orchestrator**
4. ✅ **Analysis layer cannot import orchestrator**
5. ✅ **Analysis depends on core but not infrastructure**
6. ✅ **Infrastructure must not pull orchestrator**
7. ✅ **API layer only calls orchestrator entry points**
8. ✅ **Utils stay leaf modules**
9. ⚠️ **PDF libraries only in document_processor infrastructure** (BROKEN)
10. ✅ **Flask (dashboard) isolated from FastAPI (pipeline API)**
11. ✅ **Dashboard module does not import pipeline internals**

## Running Import Linter

To check import violations locally:

```bash
# Install import-linter
pip install import-linter

# Run from project root
PYTHONPATH=src:$PYTHONPATH lint-imports
```

## CI/CD Integration

Import-linter runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

See `.github/workflows/import-linter.yml` for configuration.

## Known Issues and Future Work

### Issue 1: PDF Library Imports (Priority: Medium)
**Problem**: PDF libraries are imported directly in methods and phases rather than being centralized in infrastructure.

**Impact**: Makes it harder to swap PDF processing implementations and violates single responsibility.

**Solution**: Create a facade in `farfan_pipeline.infrastructure.extractors.pdf_facade` that wraps all PDF operations, then update all imports to use the facade.

**Estimated Effort**: 2-3 days

### Issue 2: NLP/Bayesian Isolation (Priority: Low)
**Problem**: No enforcement of separation between NLP and Bayesian libraries.

**Impact**: Potential for dependency conflicts if both layers evolve independently.

**Solution**: Add contracts to prevent cross-imports between semantic_* and bayesian_* modules.

**Estimated Effort**: 1 day (if no current violations exist)

## References

- [Import Linter Documentation](https://import-linter.readthedocs.io/)
- [Layered Architecture Pattern](https://en.wikipedia.org/wiki/Multitier_architecture)
- FARFAN Project: `pyproject.toml` (import linter configuration)
