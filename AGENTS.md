# F.A.R.F.A.N Developer Guide

## Setup
```bash
python3.12 -m venv farfan-env        # Virtual env (see .gitignore for convention)
source farfan-env/bin/activate       # Activate
pip install -e .                     # Install package + dependencies
```

## Commands
- **Build**: N/A (interpreted Python)
- **Lint**: `ruff check farfan_core/` or `mypy farfan_core/farfan_core/core/` (strict type checking)
- **Test**: `pytest -m "updated and not outdated" -v` (run current tests) or `pytest tests/` (all)
- **Dev Server**: `python farfan_core/farfan_core/api/api_server.py` or `farfan_core-api` (FastAPI on port 8000)

## Tech Stack
- **Language**: Python 3.12
- **Core**: FastAPI (API), Pydantic (validation), transformers/sentence-transformers (NLP)
- **Analysis**: PyMC (Bayesian), scikit-learn, NetworkX, spaCy
- **Quality**: pytest, ruff (linter), mypy (type checker), black (formatter)

## Architecture
**Layered**: `core/` (orchestration) → `processing/` (ingestion) → `analysis/` (methods)  
**Pipeline**: 9-phase deterministic policy analysis (Phase 0 validation → Phase 1-9 processing)  
**Structure**: Package at `farfan_core/farfan_core/`, entry point: `farfan_core/entrypoint/main.py`

## Conventions
- Strict typing (mypy strict mode, Pyright strict)
- No comments unless complex logic
- Contract-based architecture with TypedDict boundaries
- 100-char line length (ruff)
- Deterministic execution (fixed seeds, reproducible)