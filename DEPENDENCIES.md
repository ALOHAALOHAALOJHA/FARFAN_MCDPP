# F.A.R.F.A.N Pipeline Dependencies

## Core Dependencies

### REQUIRED for Phase 1 Maximum Performance

The F.A.R.F.A.N pipeline enforces **ZERO TOLERANCE** for missing dependencies required by the dura_lex contract system. These are MANDATORY for ensuring:
- Deterministic execution (as per FORCING ROUTE)
- Maximum performance
- Full contract enforcement
- Idempotency guarantees
- Complete traceability

Install all at once with:
```bash
pip install -r requirements-phase1.txt
```

#### 1. pydantic (>= 2.0) - **REQUIRED**
**Purpose**: Runtime contract validation throughout the dura_lex system

**Used in**:
- Phase 0: `phase0_input_validation.py` - Input/output contract validation with StrictModel pattern
- SISAS modules: Signal validation and contract enforcement  
- Dura_lex: `contracts_runtime.py` - All runtime contract validators
- Used throughout pipeline for maximum performance and deterministic execution

**Consequence if missing**: Pipeline will FAIL immediately on import with clear error message

#### 2. numpy (>= 1.24.0) - **REQUIRED**
**Purpose**: Deterministic operations and numerical stability

**Used in**:
- Dura_lex: `deterministic_execution.py` - DeterministicSeedManager for reproducible execution
- Required for FORCING ROUTE compliance (deterministic execution requirement)

**Consequence if missing**: Deterministic execution cannot be guaranteed

#### 3. spacy (>= 3.0.0) - **REQUIRED for SP1**
**Purpose**: Advanced NLP preprocessing

**Used in**:
- Phase 1, SP1: Advanced preprocessing, tokenization, segmentation
- FORCING ROUTE [EXEC-SP1-001] through [EXEC-SP1-011]

**Consequence if missing**: Cannot execute SP1 preprocessing (FORCING ROUTE FATAL)

#### 4. langdetect (>= 1.0.9) - **REQUIRED for SP0**
**Purpose**: Language detection

**Used in**:
- Phase 1, SP0: Language detection
- FORCING ROUTE [EXEC-SP0-001] through [EXEC-SP0-005]

**Consequence if missing**: Cannot execute SP0 language detection (FORCING ROUTE FATAL)

#### 5. PyMuPDF (>= 1.23.0) - **REQUIRED for PDF Processing**
**Purpose**: PDF text extraction

**Used in**:
- Phase 0: PDF reading and validation
- FORCING ROUTE [PRE-003] PDF path validation

**Consequence if missing**: Cannot process PDF inputs (FORCING ROUTE FATAL)

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
└── cross_cutting_infrastrucuture/  # Note: intentional typo in folder name
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
