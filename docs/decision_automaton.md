# Intrinsic Calibration Decision Automaton

**Document Version**: 1.0.0  
**Last Updated**: 2025-12-04  
**Authority**: Doctrina SIN_CARRETA  
**Rubric Version**: 2.0.0

---

## Purpose

This document defines the **3-Question Decision Automaton** (Q1/Q2/Q3) that determines whether a method requires intrinsic calibration (@b scores). The automaton is machine-readable and implemented in `system/config/calibration/intrinsic_calibration_rubric.json`.

---

## Core Logic

```
requires_calibration = (Q1 OR Q2 OR Q3) AND NOT excluded
```

Where:
- **Q1**: Is the method analytically active?
- **Q2**: Is the method parametric?
- **Q3**: Is the method safety-critical?
- **excluded**: Matches exclusion patterns (see `exclusion_rules.md`)

---

## Decision Flow Diagram

```
┌─────────────────────────────────────────────┐
│  Method Calibration Decision Automaton      │
└─────────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Check Exclusions     │
        │  (See exclusion_rules)│
        └───────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
    Excluded               Not Excluded
        │                       │
        ▼                       ▼
   EXCLUDE              ┌───────────┐
                        │  Test Q1  │
                        └───────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                  YES                  NO
                    │                   │
                    │                   ▼
                    │             ┌───────────┐
                    │             │  Test Q2  │
                    │             └───────────┘
                    │                   │
                    │         ┌─────────┴─────────┐
                    │         │                   │
                    │       YES                  NO
                    │         │                   │
                    │         │                   ▼
                    │         │             ┌───────────┐
                    │         │             │  Test Q3  │
                    │         │             └───────────┘
                    │         │                   │
                    │         │         ┌─────────┴─────────┐
                    │         │         │                   │
                    │         │       YES                  NO
                    │         │         │                   │
                    └─────────┴─────────┘                   ▼
                              │                        EXCLUDE
                              ▼
                    REQUIRE CALIBRATION
```

---

## Q1: Analytically Active

### Question
**"Can this method change what is true in the pipeline (transform, derive, or synthesize)?"**

### Rationale
Methods using these verbs modify data state or generate new insights, directly impacting the analytical chain.

### Indicators

#### Primary Analytical Verbs
```
compute, calculate, score, evaluate, analyze, assess,
rank, weight, normalize, calibrate, adjust, infer,
predict, estimate, measure
```

#### Generative ETL Verbs
```
generate, create, extract, transform, build, construct,
process, aggregate, merge, split, join, combine
```

### Decision Rule
```python
Q1 = (
    any(verb in method_name.lower() for verb in primary_analytical_verbs) OR
    any(verb in method_name.lower() for verb in generative_etl_verbs) OR
    any(verb in docstring.lower() for verb in primary_analytical_verbs[:5])
)
```

**Result**: YES → Requires calibration

### Examples

| Method | Verdict | Matched Indicator |
|:-------|:--------|:------------------|
| `compute_score` | Q1=YES | Verb: "compute" in method_name |
| `calculate_weight` | Q1=YES | Verb: "calculate" in method_name |
| `transform_data` | Q1=YES | Verb: "transform" in method_name |
| `aggregate_results` | Q1=YES | Verb: "aggregate" in method_name |
| `evaluate_policy` | Q1=YES | Verb: "evaluate" in method_name |
| `get_name` | Q1=NO | No analytical verb |

---

## Q2: Parametric

### Question
**"Does it encode assumptions or knobs that matter?"**

### Rationale
Methods that set boundaries, load configurations, or apply thresholds introduce subjective parameters that must be calibrated.

### Indicators

#### Parametric Verbs
```
configure, set, tune, initialize, setup, load, apply
```

#### Parametric Keywords (in docstring)
```
threshold, prior, weight, parameter, coefficient, model,
rule, heuristic, assumption, criterion, config, limit
```

#### Critical Layers
```
analyzer, processor, executor
```

### Decision Rule
```python
Q2 = (
    any(verb in method_name.lower() for verb in parametric_verbs) OR
    any(keyword in docstring.lower() for keyword in parametric_keywords) OR
    layer in critical_layers
)
```

**Result**: YES → Requires calibration

### Examples

| Method | Verdict | Matched Indicator |
|:-------|:--------|:------------------|
| `set_threshold` | Q2=YES | Verb: "set" + keyword: "threshold" |
| `configure_model` | Q2=YES | Verb: "configure" |
| `apply_weight` | Q2=YES | Verb: "apply" + keyword: "weight" |
| `initialize_prior` | Q2=YES | Verb: "initialize" + keyword: "prior" |
| `process_data` (in analyzer) | Q2=YES | Layer: analyzer (critical) |
| `format_output` | Q2=NO | No parametric indicators |

---

## Q3: Safety-Critical

### Question
**"Would a bug/misuse materially mislead an evaluation?"**

### Rationale
Methods explicitly designed to gate-keep, audit, or verify are the highest risk if they fail silently.

### Indicators

#### Safety Verbs
```
validate, verify, check, audit, test, ensure,
assert, monitor, log, record
```

#### Critical Layers
```
analyzer, processor, orchestrator
```

#### Evaluative Return Types
```
float, int, dict, list, bool
```

#### Special Rule
Exclude simple getters: `get_*` methods returning `str`, `Path`, or `bool` are NOT safety-critical unless they match a safety verb.

### Decision Rule
```python
Q3 = (
    any(verb in method_name.lower() for verb in safety_verbs) OR
    layer in critical_layers OR
    return_type in evaluative_return_types
) AND NOT (
    method_name.startswith('get_') AND 
    return_type in ['str', 'Path', 'bool'] AND
    not any(verb in method_name.lower() for verb in safety_verbs)
)
```

**Result**: YES → Requires calibration

### Examples

| Method | Verdict | Matched Indicator |
|:-------|:--------|:------------------|
| `validate_input` | Q3=YES | Verb: "validate" |
| `verify_scores` | Q3=YES | Verb: "verify" |
| `check_threshold` | Q3=YES | Verb: "check" |
| `audit_results` | Q3=YES | Verb: "audit" |
| `get_score() -> float` | Q3=YES | Return type: float (evaluative) |
| `get_name() -> str` | Q3=NO | Simple getter (excluded by special rule) |

---

## Combined Decision Matrix

| Q1 (Analytical) | Q2 (Parametric) | Q3 (Safety) | Excluded | **Decision** |
|:---------------:|:---------------:|:-----------:|:--------:|:------------:|
| NO | NO | NO | - | **EXCLUDE** |
| YES | - | - | NO | **CALIBRATE** |
| - | YES | - | NO | **CALIBRATE** |
| - | - | YES | NO | **CALIBRATE** |
| YES | YES | YES | NO | **CALIBRATE** |
| ANY | ANY | ANY | YES | **EXCLUDE** |

**Note**: "-" means don't care (other questions determine result)

---

## Traceability and Evidence

### Machine-Readable Evidence

Every decision produces evidence:

```json
{
  "triage_evidence": {
    "q1_analytically_active": {
      "result": true,
      "matched_verbs_in_name": ["compute"],
      "matched_verbs_in_doc": []
    },
    "q2_parametric": {
      "result": false,
      "matched_keywords": [],
      "matched_verbs": [],
      "layer_is_critical": false
    },
    "q3_safety_critical": {
      "result": false,
      "matched_safety_verbs": [],
      "layer_is_critical": false,
      "return_type_is_evaluative": true
    },
    "decision_rule": "requires_calibration = (q1 OR q2 OR q3) AND NOT excluded"
  }
}
```

### Reproducibility

All decisions are:
1. **Deterministic**: Same method → same decision
2. **Traceable**: Evidence shows which indicators matched
3. **Auditable**: Machine-readable JSON evidence
4. **Reversible**: Can reconstruct decision from evidence

---

## Edge Cases and Clarifications

### Edge Case 1: Private Analytical Methods

```python
def _compute_internal_score(self, data):
    # Private but analytical
```

**Decision**: Q1=YES → **CALIBRATE**  
**Reason**: Privacy doesn't override analytical nature

---

### Edge Case 2: Getters Returning Scores

```python
def get_score(self) -> float:
    return self._cached_score
```

**Decision**: Q3=YES → **CALIBRATE**  
**Reason**: Returns evaluative type (float), even though named "get_*"

---

### Edge Case 3: Utility Layer Processors

```python
# In utility layer
def process_data(self, raw_data):
    return cleaned_data
```

**Decision**: Q1=YES → **CALIBRATE**  
**Reason**: "process" is an ETL verb (generative)

---

### Edge Case 4: Logging with Side Effects

```python
def log_and_validate(self, data):
    logger.info("Validating...")
    return self.validate(data)
```

**Decision**: Q3=YES → **CALIBRATE**  
**Reason**: Contains "validate" (safety verb), logging is secondary

---

## Validation and Testing

### Test Suite

**Location**: `tests/calibration_system/test_decision_automaton.py`

Tests include:
1. **Q1 Tests**: Verify all analytical verbs trigger Q1
2. **Q2 Tests**: Verify parametric indicators trigger Q2
3. **Q3 Tests**: Verify safety indicators trigger Q3
4. **Exclusion Tests**: Verify excluded patterns bypass Q1/Q2/Q3
5. **Edge Case Tests**: Verify all documented edge cases

### Coverage

The test suite ensures:
- 100% verb coverage (all listed verbs tested)
- 100% keyword coverage (all listed keywords tested)
- All edge cases documented and tested

---

## Machine-Readable Schema

The decision automaton is encoded in:
```
system/config/calibration/intrinsic_calibration_rubric.json
└── decision_automaton
    ├── logic: "requires_calibration = (Q1 OR Q2 OR Q3) AND NOT excluded"
    └── questions
        ├── Q1
        │   ├── indicators
        │   │   ├── primary_analytical_verbs[]
        │   │   ├── generative_etl_verbs[]
        │   │   └── check_locations[]
        │   └── decision
        ├── Q2
        │   ├── indicators
        │   │   ├── parametric_verbs[]
        │   │   ├── parametric_keywords[]
        │   │   ├── critical_layers[]
        │   │   └── check_locations[]
        │   └── decision
        └── Q3
            ├── indicators
            │   ├── safety_verbs[]
            │   ├── critical_layers[]
            │   ├── evaluative_return_types[]
            │   ├── exclude_simple_getters
            │   └── check_locations[]
            └── decision
```

---

## Implementation

### Core Function

```python
def triage_pass1_requires_calibration(
    method_info: Dict[str, Any], 
    rubric: Dict[str, Any]
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Apply Q1/Q2/Q3 decision automaton.
    
    Returns: (requires_calibration, reason, evidence_dict)
    """
    # Load decision rules from rubric
    triggers = rubric['decision_automaton']['questions']
    exclusions = rubric['exclusion_criteria']
    
    # Check exclusions first
    if matches_exclusion(method_info, exclusions):
        return False, exclusion_reason, exclusion_evidence
    
    # Apply Q1/Q2/Q3
    q1 = check_q1_analytical(method_info, triggers['Q1'])
    q2 = check_q2_parametric(method_info, triggers['Q2'])
    q3 = check_q3_safety_critical(method_info, triggers['Q3'])
    
    # Decision logic
    if q1 or q2 or q3:
        return True, build_reason(q1, q2, q3), build_evidence(q1, q2, q3)
    else:
        return False, "Non-analytical utility function", build_evidence(q1, q2, q3)
```

---

## References

- **Rubric**: `system/config/calibration/intrinsic_calibration_rubric.json`
- **Exclusion Rules**: `docs/exclusion_rules.md`
- **Implementation**: `src/farfan_pipeline/core/calibration/rigorous_calibration_triage.py`
- **Policy**: `CALIBRATION_INTRINSIC_POLICY.md`
- **Tests**: `tests/calibration_system/test_decision_automaton.py`
