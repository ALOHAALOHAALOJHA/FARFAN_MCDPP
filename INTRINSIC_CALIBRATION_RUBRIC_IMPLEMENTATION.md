# Intrinsic Calibration Rubric Implementation

**Version**: 2.0.0  
**Date**: 2025-12-04  
**Status**: Complete - Implementation Only

---

## Overview

This document describes the complete implementation of the intrinsic calibration rubric and scoring system with exact formulas, exclusion patterns, and Q1/Q2/Q3 decision automaton.

---

## Implemented Components

### 1. Enhanced Rubric with Exact Formulas

**Location**: `system/config/calibration/intrinsic_calibration_rubric.json`

#### b_theory Formula
```
b_theory = 0.4 * statistical_validity + 0.3 * logical_consistency + 0.3 * appropriate_assumptions
```

**Components**:
- **statistical_validity** (0.4): Keywords: {bayesian, probability, regression, likelihood}
  - ≥2 keywords → 1.0
  - ==1 keyword → 0.6
  - ==0 keywords → 0.2

- **logical_consistency** (0.3): Documentation quality
  - Complete (>100 chars + params + returns) → 1.0
  - Good (>50 chars + params OR returns) → 0.7
  - Basic (>20 chars) → 0.4
  - Minimal → 0.1

- **appropriate_assumptions** (0.3): Keywords: {assum, constraint, precondition}
  - ≥1 keyword → 0.8
  - ==0 keywords → 0.3

#### b_impl Formula
```
b_impl = 0.35 * test_coverage + 0.25 * type_annotations + 0.25 * error_handling + 0.15 * documentation
```

**Components**:
- **test_coverage** (0.35): ≥80% → 1.0, linear below
  - Fallback: has_test_file → 0.5, no_test → 0.2

- **type_annotations** (0.25): Formula: `(typed_params / total_params) * 0.7 + (0.3 if return_type else 0)`
  - Full typing → 1.0
  - No typing → 0.0

- **error_handling** (0.25): try/except coverage
  - Comprehensive (try/except + validation) → 1.0
  - Good (try/except OR validation) → 0.7
  - Basic → 0.3

- **documentation** (0.15): Formula: `(0.4 if length>50 else 0.1) + (0.3 if params else 0) + (0.2 if returns else 0) + (0.1 if examples else 0)`
  - Complete → 1.0
  - Minimal → 0.1

#### b_deploy Formula
```
b_deploy = 0.4 * validation_runs + 0.35 * stability_coefficient + 0.25 * failure_rate
```

**Components**:
- **validation_runs** (0.4): ≥20 projects → 1.0, linear below
  - Fallback: layer_maturity_baseline

- **stability_coefficient** (0.35): CV < 0.1 → 1.0, scaled: `max(0, 1.0 - cv/0.5)`
  - Fallback: layer_maturity_baseline * 0.9

- **failure_rate** (0.25): < 1% → 1.0, exponential decay: `exp(-rate/5.0)`
  - Fallback: layer_maturity_baseline * 0.85

**Layer Maturity Baselines**:
- orchestrator: 0.7
- processor: 0.6
- analyzer: 0.5
- ingestion: 0.6
- executor: 0.5
- utility: 0.6
- unknown: 0.3

---

### 2. Exclusion Patterns

**Location**: `system/config/calibration/intrinsic_calibration_rubric.json` → `exclusion_criteria`

#### Pattern-Based Exclusions
- `__init__`, `__str__`, `__repr__`, `__eq__`, `__hash__`, `__len__` - Magic methods
- `_format_`, `_log_`, `_print_` - Formatting utilities
- `to_json`, `to_dict`, `from_json`, `from_dict`, `to_string` - Serialization
- `visit_*` - AST visitors

#### Conditional Exclusions
- **Private utility in utility layer**: `method_name.startswith('_') AND layer == 'utility' AND NOT analytically_active`
- **Pure getter**: `method_name.startswith('get_') AND return_type in ['str', 'Path', 'bool'] AND NOT analytically_active`

---

### 3. Decision Automaton (Q1/Q2/Q3)

**Location**: `system/config/calibration/intrinsic_calibration_rubric.json` → `decision_automaton`

**Logic**: `requires_calibration = (Q1 OR Q2 OR Q3) AND NOT excluded`

#### Q1: Analytically Active
"Can this method change what is true in the pipeline?"

**Indicators**:
- Primary analytical verbs: compute, calculate, score, evaluate, analyze, assess, rank, weight, normalize, calibrate, adjust, infer, predict, estimate, measure
- Generative ETL verbs: generate, create, extract, transform, build, construct, process, aggregate, merge, split, join, combine

**Decision**: YES if any verb in method_name OR docstring

#### Q2: Parametric
"Does it encode assumptions or knobs that matter?"

**Indicators**:
- Parametric verbs: configure, set, tune, initialize, setup, load, apply
- Parametric keywords: threshold, prior, weight, parameter, coefficient, model, rule, heuristic, assumption, criterion, config, limit
- Critical layers: analyzer, processor, executor

**Decision**: YES if (verb in method_name) OR (keyword in docstring) OR (layer in critical_layers)

#### Q3: Safety-Critical
"Would a bug/misuse materially mislead an evaluation?"

**Indicators**:
- Safety verbs: validate, verify, check, audit, test, ensure, assert, monitor, log, record
- Critical layers: analyzer, processor, orchestrator
- Evaluative return types: float, int, dict, list, bool

**Decision**: YES if (safety_verb in method_name) OR (layer in critical_layers) OR (return_type in evaluative_return_types) UNLESS simple_getter

---

### 4. Scoring Implementation

**Location**: `src/farfan_pipeline/core/calibration/intrinsic_scoring.py`

**Module Functions**:
- `compute_statistical_validity()` - Statistical keyword matching
- `compute_logical_consistency()` - Documentation quality
- `compute_appropriate_assumptions()` - Assumption keyword matching
- `compute_b_theory()` - Weighted combination
- `compute_test_coverage_score()` - Test file detection + fallback
- `compute_type_annotations_score()` - Type hint analysis
- `compute_error_handling_score()` - try/except detection
- `compute_documentation_score()` - Docstring completeness
- `compute_b_impl()` - Weighted combination
- `compute_validation_runs_score()` - Layer maturity fallback
- `compute_stability_coefficient_score()` - Layer maturity * 0.9
- `compute_failure_rate_score()` - Layer maturity * 0.85
- `compute_b_deploy()` - Weighted combination

**All functions return**: `(score: float, evidence: Dict[str, Any])`

**Evidence includes**:
- Exact formula used
- Component weights
- Matched keywords/patterns
- Computation trace
- Rule applied

---

### 5. Integration with Triage

**Location**: `src/farfan_pipeline/core/calibration/rigorous_calibration_triage.py`

**Updated to**:
1. Import scoring functions from `intrinsic_scoring` module
2. Apply Q1/Q2/Q3 decision automaton
3. Generate traceable evidence for all decisions
4. Produce machine-readable calibration profiles

**Process**:
1. **Pass 1**: `triage_pass1_requires_calibration()` - Q1/Q2/Q3 decision
2. **Pass 2**: Compute b_theory, b_impl, b_deploy using `intrinsic_scoring` module
3. **Pass 3**: Generate calibration entry with full evidence trail

---

### 6. Documentation

#### Exclusion Rules Documentation
**Location**: `docs/exclusion_rules.md`

**Contents**:
- Pattern-based exclusions with regex
- Conditional exclusions with logic
- Decision flow diagram
- Examples of excluded and included methods
- Machine-readable schema reference

#### Decision Automaton Documentation
**Location**: `docs/decision_automaton.md`

**Contents**:
- Complete Q1/Q2/Q3 definitions
- Decision flow diagram
- Indicator lists with rationale
- Edge cases and clarifications
- Examples and test coverage
- Machine-readable schema reference

---

### 7. Test Coverage

**Location**: `tests/test_intrinsic_scoring.py`

**Test Classes**:
- `TestStatisticalValidity` - Keyword matching (3 tests)
- `TestLogicalConsistency` - Documentation quality (4 tests)
- `TestAppropriateAssumptions` - Assumption keywords (2 tests)
- `TestBTheoryFormula` - Exact formula verification (1 test)
- `TestTypeAnnotationsScore` - Type hint scoring (3 tests)
- `TestDocumentationScore` - Docstring scoring (2 tests)
- `TestBImplFormula` - Exact formula verification (1 test)
- `TestBDeployFormula` - Exact formula verification (2 tests)
- `TestFormulaTraceability` - Evidence completeness (3 tests)

**Total**: 21 test methods

---

## File Manifest

### Configuration Files
1. `system/config/calibration/intrinsic_calibration_rubric.json` - Enhanced rubric v2.0.0
2. `src/farfan_pipeline/core/calibration/intrinsic_calibration_rubric.json` - Copy for module use

### Implementation Files
3. `src/farfan_pipeline/core/calibration/intrinsic_scoring.py` - Scoring implementation (new)
4. `src/farfan_pipeline/core/calibration/rigorous_calibration_triage.py` - Updated to use intrinsic_scoring

### Documentation Files
5. `docs/exclusion_rules.md` - Exclusion patterns documentation (new)
6. `docs/decision_automaton.md` - Q1/Q2/Q3 decision logic documentation (new)
7. `INTRINSIC_CALIBRATION_RUBRIC_IMPLEMENTATION.md` - This file (new)

### Test Files
8. `tests/test_intrinsic_scoring.py` - Scoring formula tests (new)

---

## Formulas Summary

### b_theory = 0.4·statistical_validity + 0.3·logical_consistency + 0.3·appropriate_assumptions

**statistical_validity**:
- Keywords: {bayesian, probability, regression, likelihood}
- ≥2 keywords → 1.0, ==1 → 0.6, ==0 → 0.2

**logical_consistency**:
- Complete docs (>100, params, returns) → 1.0
- Good docs (>50, params OR returns) → 0.7
- Basic docs (>20) → 0.4, Minimal → 0.1

**appropriate_assumptions**:
- Keywords: {assum, constraint, precondition}
- ≥1 keyword → 0.8, ==0 → 0.3

### b_impl = 0.35·test_coverage + 0.25·type_annotations + 0.25·error_handling + 0.15·documentation

**test_coverage**: ≥80% → 1.0 (linear), fallback: has_test=0.5, no_test=0.2

**type_annotations**: `(typed_params/total) * 0.7 + (0.3 if return_type else 0)`

**error_handling**: comprehensive=1.0, good=0.7, basic=0.3

**documentation**: `(0.4 if len>50 else 0.1) + (0.3 if params) + (0.2 if returns) + (0.1 if examples)`

### b_deploy = 0.4·validation_runs + 0.35·stability_coefficient + 0.25·failure_rate

**validation_runs**: ≥20 → 1.0 (linear), fallback: layer_maturity

**stability_coefficient**: CV<0.1 → 1.0, `max(0, 1.0-cv/0.5)`, fallback: layer_maturity*0.9

**failure_rate**: <1% → 1.0, `exp(-rate/5.0)`, fallback: layer_maturity*0.85

---

## Decision Automaton Summary

### Logic
```
requires_calibration = (Q1 OR Q2 OR Q3) AND NOT excluded
```

### Q1: Analytically Active
Verbs: {compute, calculate, score, evaluate, analyze, assess, rank, weight, normalize, calibrate, adjust, infer, predict, estimate, measure, generate, create, extract, transform, build, construct, process, aggregate, merge, split, join, combine}

### Q2: Parametric
Verbs: {configure, set, tune, initialize, setup, load, apply}
Keywords: {threshold, prior, weight, parameter, coefficient, model, rule, heuristic, assumption, criterion, config, limit}
Layers: {analyzer, processor, executor}

### Q3: Safety-Critical
Verbs: {validate, verify, check, audit, test, ensure, assert, monitor, log, record}
Layers: {analyzer, processor, orchestrator}
Return types: {float, int, dict, list, bool}

---

## Exclusion Patterns Summary

### Pattern Exclusions
- Magic methods: `__init__`, `__str__`, `__repr__`, `__eq__`, `__hash__`, `__len__`
- Formatting: `_format_`, `_log_`, `_print_`
- Serialization: `to_json`, `to_dict`, `from_json`, `from_dict`, `to_string`
- AST: `visit_*`

### Conditional Exclusions
- Private utility: `_method` in utility layer AND NOT analytical
- Pure getter: `get_method` returning str/Path/bool AND NOT analytical

---

## Traceability and Reproducibility

**All scores include**:
1. Exact formula used
2. Component weights
3. Matched patterns/keywords
4. Computation trace
5. Rule applied
6. Rubric version

**Example evidence structure**:
```json
{
  "formula": "b_theory = 0.4*stat + 0.3*logic + 0.3*assumptions",
  "weights": {"statistical_validity": 0.4, ...},
  "components": {
    "statistical_validity": {
      "score": 0.6,
      "rule_applied": "moderate_statistical",
      "keywords_matched": ["probability"],
      "keyword_count": 1
    },
    ...
  },
  "computation": "0.4*0.6 + 0.3*0.7 + 0.3*0.8 = 0.69",
  "final_score": 0.69
}
```

---

## Implementation Status

✅ **Complete**:
1. Enhanced rubric with exact formulas (v2.0.0)
2. Exclusion patterns (15 patterns + 2 conditional rules)
3. Q1/Q2/Q3 decision automaton
4. Scoring implementation (`intrinsic_scoring.py`)
5. Integration with triage system
6. Documentation (`exclusion_rules.md`, `decision_automaton.md`)
7. Test coverage (21 tests)

---

## Next Steps (NOT IMPLEMENTED)

The following steps are documented but NOT implemented as per instructions:

1. Run tests to validate formulas
2. Run build to verify integration
3. Run lint to check code quality
4. Generate intrinsic_calibration.json using triage system
5. Validate generated calibration against rubric

---

## References

- **Specification**: `CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md`
- **Policy**: `CALIBRATION_INTRINSIC_POLICY.md`
- **Rubric**: `system/config/calibration/intrinsic_calibration_rubric.json`
- **Implementation**: `src/farfan_pipeline/core/calibration/intrinsic_scoring.py`
- **Triage**: `src/farfan_pipeline/core/calibration/rigorous_calibration_triage.py`
- **Tests**: `tests/test_intrinsic_scoring.py`
