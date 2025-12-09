# F.A.R.F.A.N Pipeline Dependencies

## Core Dependencies

### Required for Phase 1 Execution

These dependencies are **required** for the Phase 1 SPC Ingestion pipeline to function:

- **pydantic** (>= 2.0): Used for contract validation in Phase 0 and throughout the pipeline
  - `phase0_input_validation.py`: Input/output contract validation
  - SISAS modules: Signal validation and contract enforcement

### Optional Dependencies

These dependencies enhance functionality but are not strictly required (graceful degradation):

- **langdetect**: Language detection in SP0 (Sub-Phase 0)
- **spacy**: Advanced NLP preprocessing in SP1 (Sub-Phase 1)
- **PyMuPDF (fitz)**: PDF text extraction
- **methods_dispensary.derek_beach**: Causal analysis (BeachEvidentialTest)
- **methods_dispensary.teoria_cambio**: DAG validation for Theory of Change

## Python Path Setup

To use the pipeline modules, ensure the `src` directory is in your Python path:

```bash
export PYTHONPATH=/path/to/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/src:$PYTHONPATH
```

Or when running Python scripts:

```bash
cd /path/to/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL
PYTHONPATH=src python3 your_script.py
```

## Import Structure

The project follows a clean package structure with proper `__init__.py` files:

```
src/
├── __init__.py
├── canonic_phases/
│   ├── __init__.py
│   ├── Phase_zero/__init__.py
│   ├── Phase_one/__init__.py
│   ├── Phase_two/__init__.py
│   ├── Phase_three/__init__.py
│   ├── Phase_four_five_six_seven/__init__.py
│   ├── Phase_eight/__init__.py
│   └── Phase_nine/__init__.py
└── cross_cutting_infrastrucuture/
    ├── __init__.py
    ├── irrigation_using_signals/
    │   ├── __init__.py
    │   └── SISAS/__init__.py
    ├── capaz_calibration_parmetrization/
    └── contractual/
```

## Verification

To verify the Phase 1 structure and imports:

```python
from canonic_phases.Phase_one import phase1_spc_ingestion_full

# Check PADimGridSpecification
grid_spec = phase1_spc_ingestion_full.PADimGridSpecification
print(f"Policy Areas: {len(grid_spec.POLICY_AREAS)}")  # Expected: 10
print(f"Dimensions: {len(grid_spec.DIMENSIONS)}")      # Expected: 6
print(f"Total Chunks: {len(grid_spec.POLICY_AREAS) * len(grid_spec.DIMENSIONS)}")  # Expected: 60
```

## Installation Notes

To install the required dependencies:

```bash
pip install pydantic langdetect spacy PyMuPDF
python -m spacy download en_core_web_sm  # If using spacy
```

## Constitutional Invariants

Phase 1 enforces strict constitutional invariants as defined in the FORCING ROUTE document:

1. **CARDINALIDAD ABSOLUTA**: Exactly 60 chunks in all critical stages (SP4, SP11, SP14, CPP, Adapter)
2. **COBERTURA COMPLETA**: All 60 combinations PA01-PA10 × DIM01-DIM06 must be present without duplicates
3. **FORMATO ESTRICTO**: All chunk_ids must match regex: `^PA(0[1-9]|10)-DIM0[1-6]$`
4. **UNICIDAD**: No duplicate chunk_ids in any stage
5. **SLA PROVENANCE**: provenance_completeness >= 0.8 (minimum 80%)
6. **SLA STRUCTURAL**: structural_consistency >= 0.85 (minimum 85%)

These invariants are non-negotiable and failure to meet any of them results in immediate pipeline termination.
