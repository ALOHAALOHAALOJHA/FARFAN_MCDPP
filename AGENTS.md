# Agent Development Guide

## Setup
```bash
python3.12 -m venv farfan-env
source farfan-env/bin/activate  # On Windows: farfan-env\Scripts\activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -e .
```

## Commands
- **Build**: `pip install -e .`
- **Lint**: `ruff check . && black --check . && mypy farfan_core/`
- **Test**: `python -m pytest tests/ -v --cov=farfan_core --cov-report=term-missing`
- **Dev Server**: `python farfan_core/farfan_core/api/api_server.py`

## Tech Stack
- **Language**: Python 3.12+
- **Core**: Deterministic 9-phase policy analysis pipeline with provenance tracking
- **NLP**: transformers, sentence-transformers, spacy
- **API**: Flask, FastAPI with JWT auth
- **Data**: pandas, numpy, scikit-learn, PyMuPDF
- **Testing**: pytest with property-based testing (hypothesis)

## Architecture
- `farfan_core/farfan_core/`: Main package with layered architecture
  - `core/`: Orchestrator, calibration, phase execution
  - `processing/`: SPC ingestion pipeline (canonical policy package)
  - `analysis/`: 7 producers for 300-question analysis (D1-D6 dimensions × PA01-PA10 areas)
  - `api/`: REST API server for dashboard integration
  - `flux/`: Signal system with memory:// and HTTP transport

## Code Style
- Type hints required (strict mypy/pyright enforcement)
- Line length: 100 chars (ruff)
- No comments unless complex logic requires explanation
- TypedDict for contracts with explicit pre/postconditions
- Deterministic execution: fixed seeds, explicit error handling