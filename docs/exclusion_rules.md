# Exclusion Rules for Intrinsic Calibration

**Document Version**: 1.0.0  
**Last Updated**: 2025-12-04  
**Authority**: Doctrina SIN_CARRETA  
**Rubric Version**: 2.0.0

---

## Purpose

This document defines the comprehensive exclusion rules for determining which methods do **NOT** require intrinsic calibration (@b scores). These rules are machine-readable and implemented in `system/config/calibration/intrinsic_calibration_rubric.json`.

---

## Core Principle

> **Exclusion Criteria**: Methods are excluded from calibration if they are **non-analytical**, **non-semantic**, or **infrastructure-only**. All exclusions must be justified and traceable.

---

## Pattern-Based Exclusions

### 1. Magic Methods (Dunder Methods)

**Pattern**: `__<name>__`  
**Reason**: Python special methods that define object behavior, not analytical logic.

| Pattern | Regex | Reason | Examples |
|:--------|:------|:-------|:---------|
| `__init__` | `^__init__$` | Constructor - non-analytical | Object initialization |
| `__str__` | `^__str__$` | String representation - non-analytical | String conversion |
| `__repr__` | `^__repr__$` | String representation - non-analytical | Debug representation |
| `__eq__` | `^__eq__$` | Equality comparison - non-analytical | Equality check |
| `__hash__` | `^__hash__$` | Hash function - non-analytical | Hash computation |
| `__len__` | `^__len__$` | Length accessor - non-analytical | Length retrieval |

**Justification**: These methods implement Python's data model protocol but do not perform analytical computations.

---

### 2. Formatting and Presentation

**Pattern**: Methods with formatting/presentation semantics  
**Reason**: These transform data for display, not for analysis.

| Pattern | Regex | Reason | Examples |
|:--------|:------|:-------|:---------|
| `_format_` | `.*_format_.*` | Formatting utility - non-semantic | `_format_output`, `format_report` |
| `_log_` | `.*_log_.*` | Logging utility - non-semantic | `_log_error`, `log_event` |
| `_print_` | `.*_print_.*` | Print utility - non-semantic | `_print_results`, `print_summary` |

**Justification**: Presentation logic does not affect analytical results.

---

### 3. Serialization/Deserialization

**Pattern**: Methods that convert to/from standard formats  
**Reason**: Data transformation for I/O, not analytical computation.

| Pattern | Regex | Reason | Examples |
|:--------|:------|:-------|:---------|
| `to_string` | `.*to_string.*` | Serialization - non-semantic | `to_string`, `config_to_string` |
| `to_json` | `.*to_json.*` | Serialization - non-semantic | `to_json`, `export_to_json` |
| `to_dict` | `.*to_dict.*` | Serialization - non-semantic | `to_dict`, `convert_to_dict` |
| `from_json` | `.*from_json.*` | Deserialization - non-semantic | `from_json`, `load_from_json` |
| `from_dict` | `.*from_dict.*` | Deserialization - non-semantic | `from_dict`, `parse_from_dict` |

**Justification**: Serialization preserves data but does not compute analytical results.

---

### 4. AST Visitors

**Pattern**: Methods implementing visitor pattern for AST traversal  
**Reason**: Infrastructure for code parsing, not analytical computation.

| Pattern | Regex | Reason | Examples |
|:--------|:------|:-------|:---------|
| `visit_` | `^visit_.*` | AST visitor - non-analytical | `visit_FunctionDef`, `visit_ClassDef` |

**Justification**: Visitor methods traverse syntax trees but do not perform policy analysis.

---

## Conditional Exclusions

### 5. Private Utility in Utility Layer

**Condition**:
```python
method_name.startswith('_') AND 
layer == 'utility' AND 
NOT analytically_active
```

**Reason**: Private utility function - non-analytical

**Examples**:
- `_sanitize_input` in utility layer (excluded)
- `_compute_score` in analyzer layer (NOT excluded - analytically active)

**Justification**: Private utilities in the utility layer are infrastructure helpers. Private methods in analytical layers may still perform computation.

---

### 6. Pure Getters

**Condition**:
```python
method_name.startswith('get_') AND 
return_type in ['str', 'Path', 'bool'] AND 
NOT analytically_active
```

**Reason**: Simple getter with no analytical logic

**Examples**:
- `get_name() -> str` (excluded)
- `get_file_path() -> Path` (excluded)
- `get_score() -> float` (NOT excluded - returns analytical result)

**Justification**: Simple property accessors don't perform computation. Getters returning numerical results may be analytical.

---

## Exclusion Decision Flow

```
Method requires calibration?
│
├─ Check pattern-based exclusions
│  ├─ Matches __<name>__ → EXCLUDE
│  ├─ Matches _format_|_log_|_print_ → EXCLUDE
│  ├─ Matches to_json|to_dict|from_json|from_dict → EXCLUDE
│  ├─ Matches visit_* → EXCLUDE
│  └─ No pattern match → Continue
│
├─ Check conditional exclusions
│  ├─ Private utility in utility layer AND NOT analytical → EXCLUDE
│  ├─ Pure getter (simple type) AND NOT analytical → EXCLUDE
│  └─ No conditional match → Continue
│
└─ Apply Q1/Q2/Q3 decision automaton
   ├─ Q1 (analytical) OR Q2 (parametric) OR Q3 (safety) → REQUIRE CALIBRATION
   └─ None of Q1/Q2/Q3 → EXCLUDE (non-analytical utility)
```

---

## Machine-Readable Implementation

Exclusion rules are defined in:
```
system/config/calibration/intrinsic_calibration_rubric.json
└── exclusion_criteria
    ├── patterns[] (pattern-based)
    └── conditional_rules{} (conditional)
```

### Pattern-Based Rules
```json
{
  "patterns": [
    {
      "pattern": "__init__",
      "reason": "Constructor - non-analytical",
      "regex": "^__init__$"
    }
  ]
}
```

### Conditional Rules
```json
{
  "conditional_rules": {
    "private_utility_in_utility_layer": {
      "condition": "method_name.startswith('_') AND layer == 'utility' AND NOT analytically_active",
      "reason": "Private utility function - non-analytical"
    }
  }
}
```

---

## Examples

### Excluded Methods

| Method | Layer | Reason | Rule Applied |
|:-------|:------|:-------|:-------------|
| `__init__` | any | Constructor | Pattern: `__init__` |
| `to_json` | any | Serialization | Pattern: `to_json` |
| `_format_output` | any | Formatting | Pattern: `_format_` |
| `_sanitize_input` | utility | Private utility | Conditional: private_utility |
| `get_name` | any | Simple getter | Conditional: pure_getter |

### NOT Excluded (Require Calibration)

| Method | Layer | Reason | Decision |
|:-------|:------|:-------|:---------|
| `compute_score` | analyzer | Q1: Analytical | Verb: compute |
| `set_threshold` | processor | Q2: Parametric | Verb: set + keyword: threshold |
| `validate_input` | processor | Q3: Safety | Verb: validate |
| `get_score` | analyzer | Q1: Analytical | Returns analytical result |
| `_compute_internal` | analyzer | Q1: Analytical | Private but analytical |

---

## Validation

### Automated Tests

**Test**: `tests/calibration_system/test_exclusion_rules.py`

Validates:
1. All pattern exclusions work correctly
2. Conditional exclusions correctly classify edge cases
3. No false positives (analytical methods excluded)
4. No false negatives (non-analytical methods included)

### Manual Review

- Annual audit of exclusion patterns
- Review new exclusions during PR process
- Update documentation when patterns change

---

## Policy Updates

**Amendment Process**:
1. Propose new exclusion pattern via GitHub issue
2. Justify with examples of affected methods
3. Update `intrinsic_calibration_rubric.json`
4. Update this documentation
5. Add test cases
6. Get calibration team approval

---

## References

- **Rubric**: `system/config/calibration/intrinsic_calibration_rubric.json`
- **Decision Automaton**: `docs/decision_automaton.md`
- **Policy**: `CALIBRATION_INTRINSIC_POLICY.md`
- **Implementation**: `src/farfan_pipeline/core/calibration/rigorous_calibration_triage.py`
