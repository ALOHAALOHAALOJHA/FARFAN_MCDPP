# Congruence Layer (@C) Examples

This directory contains worked examples demonstrating the Congruence Layer Evaluator for method ensembles in the F.A.R.F.A.N (SAAAAAA) system.

## Overview

The Congruence Layer (@C) evaluates how well methods in an ensemble can work together, computing:

```
C_play(G | ctx) = c_scale · c_sem · c_fusion
```

Where:
- **c_scale**: Scale congruence - output range compatibility
- **c_sem**: Semantic congruence - Jaccard index of semantic tags  
- **c_fusion**: Fusion validity - rule presence and input availability

## Examples

### Example 1: Perfect Ensemble
**File**: `example_1_perfect_ensemble.py`

Demonstrates ideal congruence where all components score 1.0:
- Identical output ranges [0, 1]
- Complete semantic overlap
- Valid fusion rule with all inputs

**Result**: C_play = 1.0

**Run**: `python tests/congruence_examples/example_1_perfect_ensemble.py`

---

### Example 2: Partial Congruence  
**File**: `example_2_partial_congruence.py`

Shows realistic scenario with mixed scores:
- Compatible but different ranges (both in [0,1])
- Partial semantic overlap
- Valid fusion but missing inputs

**Result**: C_play ≈ 0.133

**Run**: `python tests/congruence_examples/example_2_partial_congruence.py`

---

### Example 3: Incompatible Ensemble
**File**: `example_3_incompatible_ensemble.py`

Demonstrates invalid ensemble configuration:
- Incompatible ranges [0,1] vs [0,10000]
- No semantic overlap
- No fusion rule declared

**Result**: C_play = 0.0 (INVALID)

**Run**: `python tests/congruence_examples/example_3_incompatible_ensemble.py`

---

### Example 4: Single Method Edge Case
**File**: `example_4_single_method.py`

Shows special case for single-method ensembles:
- Always returns 1.0 regardless of other factors
- No fusion needed
- No inter-method conflicts possible

**Result**: C_play = 1.0 (by definition)

**Run**: `python tests/congruence_examples/example_4_single_method.py`

---

### Example 5: Three-Method Ensemble
**File**: `example_5_three_method_ensemble.py`

Complex realistic scenario with detailed trace:
- Three methods with mixed characteristics
- Step-by-step computation breakdown
- Comprehensive interpretation

**Result**: Computed with full trace

**Run**: `python tests/congruence_examples/example_5_three_method_ensemble.py`

---

## Running All Examples

```bash
# Run all examples in sequence
for ex in tests/congruence_examples/example_*.py; do
    python "$ex"
    echo ""
    echo "Press Enter to continue..."
    read
done
```

Or individually:
```bash
python tests/congruence_examples/example_1_perfect_ensemble.py
python tests/congruence_examples/example_2_partial_congruence.py
python tests/congruence_examples/example_3_incompatible_ensemble.py
python tests/congruence_examples/example_4_single_method.py
python tests/congruence_examples/example_5_three_method_ensemble.py
```

## Understanding the Output

Each example provides:

1. **Configuration**: Method metadata (ranges, tags, descriptions)
2. **Step-by-step computation**:
   - c_scale calculation with range analysis
   - c_sem calculation with Jaccard index
   - c_fusion calculation with input checking
3. **Final score**: C_play = c_scale × c_sem × c_fusion
4. **Interpretation**: What the score means and recommendations

## Key Concepts

### c_scale (Scale Congruence)
- **1.0**: All output ranges identical
- **0.8**: All ranges within [0,1] or convertible
- **0.0**: Incompatible ranges

### c_sem (Semantic Congruence)
Uses Jaccard index: `|intersection| / |union|` of semantic tags
- **1.0**: Complete overlap
- **0.0-1.0**: Partial overlap
- **0.0**: No overlap

### c_fusion (Fusion Validity)
- **1.0**: Fusion rule present AND all inputs available
- **0.5**: Fusion rule present BUT some inputs missing
- **0.0**: No fusion rule declared

### Special Cases
- **Single method**: Always returns 1.0
- **Empty ensemble**: Returns 1.0
- **Missing metadata**: Components default to 0.0

## References

- **Specification**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/mathematical_foundations_capax_system.md`
  - Section 3.5: Interplay Congruence Layer @C
  - Definition 3.5.1: Ensemble validity formulas

- **Implementation**: `src/farfan_pipeline/core/calibration/congruence_layer.py`

- **Tests**: `tests/congruence_layer_tests.py`
