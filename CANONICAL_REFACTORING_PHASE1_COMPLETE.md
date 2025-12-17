# Canonical Refactoring Phase 1: Complete

## Executive Summary

Successfully refactored CalibrationPolicy to be FARFAN-sensitive following the canonical refactoring methodology. No CalibrationOrchestrator was created per ADR. All constants extracted from questionnaire_monolith.json and frozen at import time. Zero runtime JSON dependencies.

## Architectural Decisions (ADR)

### Decision 1: No CalibrationOrchestrator

**Status**: IMPLEMENTED

**Decision**: Do NOT create a CalibrationOrchestrator. CalibrationPolicy is a **wiring layer** that injects canonical constants, not a centralized router.

**Rationale**:
- Avoids single point of failure
- Prevents coupling between methods and questions
- Enables method-specific calibration (e.g., CDAFFramework logit transformation)
- Follows "inject constants, don't dispatch dynamically" principle

**Alternative Considered**: Method-aware orchestrator that routes by question_id → **REJECTED** as it reintroduces coupling

### Decision 2: Extract → Normalize → Freeze Pattern

**Status**: IMPLEMENTED

**Pattern Applied**:
1. **Extract**: Located canonical elements in derek_beach.py, questionnaire structure docs
2. **Normalize**: Converted to Python constants with explicit names and types
3. **Freeze**: Loaded at module import with quality gates, NO runtime JSON

**Results**:
- `src/farfan_pipeline/core/canonical_specs.py` created
- 11,766 characters of canonical constants
- 8 quality gates validate integrity at import
- Zero runtime file I/O

## Implementation Details

### File: `src/farfan_pipeline/core/canonical_specs.py`

**Purpose**: Single source of truth for all FARFAN constants

**Contents**:

#### 1. Policy Areas (CANON_POLICY_AREAS)
```python
CANON_POLICY_AREAS: Final[dict[str, str]] = {
    "PA01": "Educación",
    "PA02": "Salud",
    # ... PA03-PA10
}
```
- Source: questionnaire_monolith.json
- Validation: Exactly 10 policy areas, all keys start with "PA"

#### 2. MICRO_LEVELS
```python
MICRO_LEVELS: Final[dict[str, float]] = {
    "EXCELENTE": 0.85,
    "BUENO": 0.70,
    "ACEPTABLE": 0.55,
    "INSUFICIENTE": 0.00,
}
```
- Source: derek_beach.py lines 97-102
- Validation: Monotonic decreasing
- Used by: CalibrationPolicy, DEREK_BEACH methods

#### 3. Derived Thresholds
```python
# Formula: (ACEPTABLE + BUENO) / 2
ALIGNMENT_THRESHOLD: Final[float] = 0.625

# Formula: 1 - quality_level
RISK_THRESHOLDS: Final[dict[str, float]] = {
    "excellent": 0.15,
    "good": 0.30,
    "acceptable": 0.45,
}
```

#### 4. CDAF Calibration Parameters
```python
CDAF_CALIBRATION_PARAMS: Final[dict[str, float]] = {
    "alpha": -2.0,  # Logit intercept
    "beta": 4.0,    # Logit slope
}

CDAF_DOMAIN_WEIGHTS: Final[dict[str, float]] = {
    "semantic": 0.35,
    "temporal": 0.25,
    "financial": 0.25,
    "structural": 0.15,
}
```
- Source: derek_beach.py CDAFFramework (lines 6575-6586)
- Validation: Domain weights sum to 1.0

#### 5. Bayes Factors
```python
BAYES_FACTORS: Final[dict[str, tuple[float, float]]] = {
    "straw": (2.0, 4.0),
    "hoop": (8.0, 12.0),
    "smoking": (8.0, 12.0),
    "doubly": (20.0, 30.0),
}
```
- Source: Beach & Pedersen evidential test typology

#### 6. PDT/PDM Structure Patterns
```python
PDT_SECTION_PATTERNS: Final[list[str]] = [
    r"^#{1,3}\s+",              # Markdown headers
    r"^\d+\.\s+[A-ZÑÁÉÍÓÚ]",   # Numbered sections
    # ...
]

CAUSAL_CHAIN_ORDER: Final[dict[str, int]] = {
    "insumos": 0,
    "actividades": 1,
    "productos": 2,
    "resultados": 3,
    "efectos": 4,
    "impactos": 5,
}
```
- Source: reporte_unit_of_analysis structure
- Used by: Semantic chunking, causal distance calculations

### File: `src/farfan_pipeline/phases/Phase_two/calibration_policy.py`

**Changes**:

#### Before (Generic)
```python
QUALITY_BANDS = {
    "EXCELLENT": (0.8, 1.0),
    "GOOD": (0.6, 0.8),
    "ACCEPTABLE": (0.4, 0.6),
    "POOR": (0.0, 0.4),
}
```

#### After (FARFAN-Sensitive)
```python
from farfan_pipeline.core.canonical_specs import MICRO_LEVELS

QUALITY_BANDS = {
    "EXCELENTE": (MICRO_LEVELS["EXCELENTE"], 1.0),
    "BUENO": (MICRO_LEVELS["BUENO"], MICRO_LEVELS["EXCELENTE"]),
    "ACEPTABLE": (MICRO_LEVELS["ACEPTABLE"], MICRO_LEVELS["BUENO"]),
    "INSUFICIENTE": (MICRO_LEVELS["INSUFICIENTE"], MICRO_LEVELS["ACEPTABLE"]),
}
```

**Weight Adjustment Factors**:
- EXCELENTE: 1.0 (no downweight)
- BUENO: 0.90 (10% downweight)
- ACEPTABLE: 0.75 (25% downweight)
- INSUFICIENTE: 0.40 (60% downweight)

**MIN_EXECUTION_THRESHOLD**: 0.50 (below ACEPTABLE with safety margin)

## Test Results

### All 35 Tests Pass ✅

**Unit Tests** (21):
- `test_quality_band_classification` - FARFAN thresholds correct
- `test_method_execution_decision_strict_mode` - Blocks below 0.50
- `test_weight_adjustment_*` - All bands use correct factors
- `test_custom_thresholds` - Method-specific calibration supported
- `test_drift_detection_*` - Monitoring works with FARFAN bands

**Integration Tests** (14):
- `test_high_calibration_enables_full_weight` - EXCELENTE = 1.0x
- `test_low_calibration_reduces_weight` - INSUFICIENTE = 0.4x
- `test_calibration_weights_vary_by_score` - All bands differentiated
- `test_no_fake_calibration_claims` - Real 60% weight difference
- `test_calibration_weights_always_applied` - No silent drops

**Regression Prevention**: All tests updated to use Spanish canonical names and FARFAN thresholds.

## Quality Gates Validated

From `canonical_specs.validate_canonical_specs()`:

1. ✅ `policy_areas_count`: Exactly 10 policy areas
2. ✅ `policy_areas_format`: All keys start with "PA"
3. ✅ `dimensions_count`: Exactly 6 dimensions
4. ✅ `dimensions_format`: All keys start with "DIM"
5. ✅ `micro_levels_monotonic`: EXCELENTE > BUENO > ACEPTABLE > INSUFICIENTE
6. ✅ `alignment_threshold`: Equals 0.625
7. ✅ `domain_weights_sum`: Sums to 1.0
8. ✅ `causal_chain_sequential`: Ordinal positions 0-5

## Traceability

Every constant includes provenance comments:

```python
# Source: derek_beach.py MICRO_LEVELS (lines 97-102)
# Used by: DEREK_BEACH methods, CDAFFramework, BayesianMechanismInference
# Traceable to: Beach's evidential quality standards

# Formula: (ACEPTABLE + BUENO) / 2
# Rationale: Midpoint between acceptable and good quality
ALIGNMENT_THRESHOLD: Final[float] = 0.625
```

## Definition of Done ✅

Per architectural guidance:

- [x] No `open(...questionnaire...)` or runtime JSON dependency
- [x] Policy areas live in **one canonical module** (canonical_specs.py)
- [x] Methods can import from canonical module (no duplication)
- [x] **Quality gates** validate thresholds, monotonicity, cardinalities
- [x] Changes are **deterministic, traceable, auditable**
- [x] Constants + formulas (no arbitrary hardcodes)

## Compatibility Verification

### DEREK_BEACH Methods

| Constant | canonical_specs.py | derek_beach.py | Status |
|----------|-------------------|----------------|--------|
| EXCELENTE | 0.85 | 0.85 | ✅ Match |
| BUENO | 0.70 | 0.70 | ✅ Match |
| ACEPTABLE | 0.55 | 0.55 | ✅ Match |
| INSUFICIENTE | 0.00 | 0.00 | ✅ Match |
| ALIGNMENT_THRESHOLD | 0.625 | (ACEPTABLE+BUENO)/2 = 0.625 | ✅ Match |
| CDAF alpha | -2.0 | -2.0 (line 6576) | ✅ Match |
| CDAF beta | 4.0 | 4.0 (line 6577) | ✅ Match |

### Questionnaire Structure

| Element | canonical_specs.py | questionnaire_monolith.json | Status |
|---------|-------------------|----------------------------|--------|
| Policy Areas | 10 (PA01-PA10) | 10 areas | ✅ Match |
| Dimensions | 6 (DIM01-DIM06) | 6 dimensions | ✅ Match |
| Base Questions | 30 (6×5) | 30 micro questions | ✅ Match |

## Next Phase Recommendations

Per architectural guidance, apply same pattern to:

### Priority 1: policy_processor.py
**Goal**: Remove questionnaire dependencies, add capability metadata

**Steps**:
1. Inventory hardcodes: method-to-question mappings, policy area lists
2. Move to canonical_specs or method capability declarations
3. Replace question_id-based selection with capability matching
4. Add `requires`, `produces`, `strengths/limits` metadata to each method

### Priority 2: semantic_chunking_policy.py
**Goal**: Canonical segmentation patterns

**Steps**:
1. Extract delimiters, transitions, pair-preservation rules
2. Use PDT_SECTION_PATTERNS from canonical_specs
3. Add quality gates: min sections detected, chunk size ranges
4. Ensure pairs preserved (indicator+baseline+goal, cost+source, BPIN+description)

### Priority 3: financiero_viabilidad_tablas.py
**Goal**: Canonical table/header/format constants

**Steps**:
1. Extract table headers, column formats, financial patterns
2. Define consistency checks (PPI columns, sum validations)
3. Add robust parsing with tolerance for separators
4. Quality gates: regex compile, min columns detected

## Files Modified

- **Created**: `src/farfan_pipeline/core/canonical_specs.py` (11,766 chars)
- **Modified**: `src/farfan_pipeline/phases/Phase_two/calibration_policy.py` (+47/-56 lines)
- **Modified**: `tests/test_calibration_policy.py` (+40/-40 lines)
- **Modified**: `tests/test_calibration_integration.py` (+38/-38 lines)

**Commit**: `2f6a5b3` - CANONICAL REFACTORING: Align CalibrationPolicy with FARFAN MICRO_LEVELS

## References

- Architectural Guidance: PR Comment #3665755393
- GUIA_ARQUEOLOGIA_INVERSA_REFACTORIZACION.md - Methodology
- DEREK_BEACH source: src/farfan_pipeline/methods/derek_beach.py
- Original issue: [P2] ADD: Make Calibration Results Influence Execution and Aggregation
