# F.A.R.F.A.N Weight Tuning Guide

**How to Adjust Fusion Weights While Maintaining Normalization**

Version: 1.0.0  
Last Updated: 2024-12-16

---

## Table of Contents

1. [Overview](#overview)
2. [When to Adjust Weights](#when-to-adjust-weights)
3. [Normalization Constraint](#normalization-constraint)
4. [Tuning Procedures](#tuning-procedures)
5. [Weight Adjustment Patterns](#weight-adjustment-patterns)
6. [Validation and Testing](#validation-and-testing)
7. [Examples](#examples)
8. [Best Practices](#best-practices)

---

## Overview

The F.A.R.F.A.N Choquet integral fusion uses **8 linear weights** and **3 interaction weights** that must sum to **1.0**. This guide explains how to adjust weights while maintaining this normalization constraint.

### Current Weights (COHORT_2024)

**Linear Weights** (sum = 0.67):
```python
CHOQUET_WEIGHTS = {
    "@b": 0.17,      # Intrinsic quality (highest)
    "@chain": 0.13,  # Data flow integrity
    "@q": 0.08,      # Question appropriateness
    "@d": 0.07,      # Dimension alignment
    "@p": 0.06,      # Policy area fit
    "@C": 0.08,      # Contract compliance
    "@u": 0.04,      # Unit quality
    "@m": 0.04,      # Governance maturity
}
```

**Interaction Weights** (sum = 0.33):
```python
CHOQUET_INTERACTION_WEIGHTS = {
    ("@u", "@chain"): 0.13,    # Plan quality limits wiring
    ("@chain", "@C"): 0.10,    # Valid chain requires compliant contracts
    ("@q", "@d"): 0.10,        # Question fit synergizes with dimension alignment
}
```

**Total**: 0.67 + 0.33 = 1.00 ✓

---

## When to Adjust Weights

### Valid Reasons

1. **Empirical Recalibration**: New validation data reveals different importance rankings
2. **Cohort Migration**: Moving from COHORT_2024 → COHORT_2025 with new methods
3. **Domain Specialization**: Adapting weights for specific policy areas (e.g., PA01 vs PA10)
4. **Error Correction**: Fixing miscalibrated weights from previous cohort

### Invalid Reasons

❌ **Tuning per execution** — Violates SIN_CARRETA doctrine (calibration immutability)
❌ **Gaming scores** — Adjusting to artificially boost specific methods
❌ **Arbitrary preferences** — Personal opinions without empirical validation
❌ **Overfitting** — Optimizing for single PDT rather than general performance

---

## Normalization Constraint

### Mathematical Constraint

```
Σ_{l∈L} a_l + Σ_{(l,k)∈I} a_lk = 1.0

where:
  L = {@b, @u, @q, @d, @p, @C, @chain, @m}
  I = {(@u, @chain), (@chain, @C), (@q, @d)}
```

### Implications

- **Increases must be offset by decreases**: If you increase @b by 0.02, you must decrease other weights by 0.02 total
- **Cannot exceed 1.0**: All weights must be ≥ 0 and sum ≤ 1.0
- **Interaction weights are "expensive"**: Increasing an interaction weight reduces budget for all linear weights

---

## Tuning Procedures

### Procedure 1: Single Weight Adjustment

**Goal**: Increase/decrease one weight while keeping others proportional.

**Steps**:

1. Decide target weight change (e.g., increase @b from 0.17 to 0.20)
2. Compute delta: Δ = 0.20 - 0.17 = +0.03
3. Distribute -Δ proportionally across other weights
4. Verify normalization

**Formula**:
```python
def adjust_single_weight(
    weights: dict,
    target_layer: str,
    new_value: float
) -> dict:
    """
    Adjust single weight while maintaining normalization.
    
    Args:
        weights: Current weight dictionary
        target_layer: Layer to adjust (e.g., "@b")
        new_value: New weight value
    
    Returns:
        Updated weights (normalized)
    """
    old_value = weights[target_layer]
    delta = new_value - old_value
    
    # Remaining weight to redistribute
    remaining_sum = 1.0 - new_value
    
    # Current sum of other weights
    other_sum = sum(w for k, w in weights.items() if k != target_layer)
    
    # Scale other weights proportionally
    new_weights = {}
    for layer, weight in weights.items():
        if layer == target_layer:
            new_weights[layer] = new_value
        else:
            new_weights[layer] = weight * (remaining_sum / other_sum)
    
    # Verify
    assert abs(sum(new_weights.values()) - 1.0) < 1e-6
    
    return new_weights
```

**Example**:

```python
# Increase @b from 0.17 to 0.20 (+0.03)
# Decrease all others proportionally by 0.03 total

old_weights = {
    "@b": 0.17,
    "@chain": 0.13,
    "@q": 0.08,
    "@d": 0.07,
    "@p": 0.06,
    "@C": 0.08,
    "@u": 0.04,
    "@m": 0.04,
}

new_weights = adjust_single_weight(old_weights, "@b", 0.20)

# Result:
# {
#     "@b": 0.200,      # +0.03
#     "@chain": 0.126,  # -0.004 (proportional reduction)
#     "@q": 0.077,      # -0.003
#     "@d": 0.068,      # -0.002
#     "@p": 0.058,      # -0.002
#     "@C": 0.077,      # -0.003
#     "@u": 0.039,      # -0.001
#     "@m": 0.039,      # -0.001
# }
# Sum = 1.000 ✓
```

---

### Procedure 2: Pairwise Exchange

**Goal**: Transfer weight from layer A to layer B without affecting others.

**Steps**:

1. Decide transfer amount (e.g., move 0.02 from @u to @chain)
2. Decrease source by delta
3. Increase target by delta
4. Verify normalization

**Formula**:
```python
def transfer_weight(
    weights: dict,
    source_layer: str,
    target_layer: str,
    amount: float
) -> dict:
    """
    Transfer weight from source to target.
    
    Args:
        weights: Current weight dictionary
        source_layer: Layer to decrease
        target_layer: Layer to increase
        amount: Weight to transfer (positive)
    
    Returns:
        Updated weights
    """
    if weights[source_layer] < amount:
        raise ValueError(f"{source_layer} has insufficient weight to transfer")
    
    new_weights = weights.copy()
    new_weights[source_layer] -= amount
    new_weights[target_layer] += amount
    
    # Verify
    assert abs(sum(new_weights.values()) - 1.0) < 1e-6
    assert all(w >= 0 for w in new_weights.values())
    
    return new_weights
```

**Example**:

```python
# Move 0.02 from @u to @chain
# (strengthen data flow at expense of unit quality)

new_weights = transfer_weight(old_weights, "@u", "@chain", 0.02)

# Result:
# {
#     "@b": 0.17,
#     "@chain": 0.15,  # +0.02
#     "@q": 0.08,
#     "@d": 0.07,
#     "@p": 0.06,
#     "@C": 0.08,
#     "@u": 0.02,      # -0.02
#     "@m": 0.04,
# }
# Sum = 1.000 ✓
```

---

### Procedure 3: Group Adjustment

**Goal**: Adjust multiple weights simultaneously while maintaining ratios within a group.

**Steps**:

1. Define groups (e.g., contextual layers: @q, @d, @p)
2. Set group target sum
3. Scale group weights proportionally
4. Scale remaining weights to fill budget

**Formula**:
```python
def adjust_weight_group(
    weights: dict,
    group_layers: list,
    group_target_sum: float
) -> dict:
    """
    Adjust group of weights while maintaining internal ratios.
    
    Args:
        weights: Current weight dictionary
        group_layers: Layers in group (e.g., ["@q", "@d", "@p"])
        group_target_sum: Target sum for group
    
    Returns:
        Updated weights
    """
    # Current group sum
    group_sum = sum(weights[l] for l in group_layers)
    
    # Scale factor for group
    scale_factor = group_target_sum / group_sum
    
    # New weights
    new_weights = {}
    for layer, weight in weights.items():
        if layer in group_layers:
            new_weights[layer] = weight * scale_factor
        else:
            # Will be scaled later
            new_weights[layer] = weight
    
    # Scale non-group weights to fill remaining budget
    non_group_sum = sum(new_weights[l] for l in weights if l not in group_layers)
    remaining_budget = 1.0 - group_target_sum
    non_group_scale = remaining_budget / non_group_sum
    
    for layer in weights:
        if layer not in group_layers:
            new_weights[layer] *= non_group_scale
    
    # Verify
    assert abs(sum(new_weights.values()) - 1.0) < 1e-6
    
    return new_weights
```

**Example**:

```python
# Boost contextual layers (@q, @d, @p) from 0.21 to 0.25 total
# While maintaining their internal ratios (8:7:6)

contextual = ["@q", "@d", "@p"]
new_weights = adjust_weight_group(old_weights, contextual, 0.25)

# Result:
# Contextual group (before): 0.08 + 0.07 + 0.06 = 0.21
# Contextual group (after):  0.095 + 0.083 + 0.071 = 0.25 (ratios preserved)
# Other weights scaled down proportionally
```

---

### Procedure 4: Interaction Weight Adjustment

**Goal**: Adjust interaction weights while respecting normalization.

**Important**: Interaction weights are "expensive" — increasing an interaction by 0.01 requires decreasing linear weights by 0.01 total.

**Steps**:

1. Compute current linear sum and interaction sum
2. Adjust interaction weight
3. Redistribute change across linear weights
4. Verify normalization

**Formula**:
```python
def adjust_interaction_weight(
    linear_weights: dict,
    interaction_weights: dict,
    target_interaction: tuple,
    new_value: float
) -> tuple:
    """
    Adjust interaction weight while maintaining normalization.
    
    Args:
        linear_weights: Current linear weights
        interaction_weights: Current interaction weights
        target_interaction: Interaction tuple (e.g., ("@u", "@chain"))
        new_value: New interaction weight
    
    Returns:
        (new_linear_weights, new_interaction_weights)
    """
    old_value = interaction_weights[target_interaction]
    delta = new_value - old_value
    
    # Update interaction
    new_interaction = interaction_weights.copy()
    new_interaction[target_interaction] = new_value
    
    # Redistribute -delta across linear weights proportionally
    linear_sum = sum(linear_weights.values())
    scale_factor = (linear_sum - delta) / linear_sum
    
    new_linear = {
        layer: weight * scale_factor
        for layer, weight in linear_weights.items()
    }
    
    # Verify
    total = sum(new_linear.values()) + sum(new_interaction.values())
    assert abs(total - 1.0) < 1e-6
    
    return new_linear, new_interaction
```

**Example**:

```python
# Strengthen (@u, @chain) interaction from 0.13 to 0.15 (+0.02)
# Must reduce linear weights by 0.02 total

new_linear, new_interaction = adjust_interaction_weight(
    linear_weights=old_weights,
    interaction_weights={
        ("@u", "@chain"): 0.13,
        ("@chain", "@C"): 0.10,
        ("@q", "@d"): 0.10,
    },
    target_interaction=("@u", "@chain"),
    new_value=0.15
)

# Result:
# Linear sum reduced from 0.67 to 0.65 (all scaled proportionally)
# Interaction sum increased from 0.33 to 0.35
# Total = 1.00 ✓
```

---

## Weight Adjustment Patterns

### Pattern 1: Boost Core Quality (@b)

**Scenario**: Emphasize intrinsic method quality over contextual fit.

**Adjustment**:
- Increase @b: 0.17 → 0.20 (+0.03)
- Decrease contextual layers (@q, @d, @p): 0.21 → 0.18 (-0.03)

**Result**: Methods with strong fundamentals (@b) score higher, even if contextual fit is weaker.

---

### Pattern 2: Strengthen Chain Integrity

**Scenario**: Emphasize data flow correctness (detect broken chains earlier).

**Adjustment**:
- Increase @chain: 0.13 → 0.15 (+0.02)
- Increase (@chain, @C) interaction: 0.10 → 0.11 (+0.01)
- Decrease @u: 0.04 → 0.01 (-0.03)

**Result**: Broken chains have even more severe impact on final scores.

---

### Pattern 3: Context-Aware Specialization

**Scenario**: Prioritize question-dimension-policy fit for domain-specific analysis.

**Adjustment**:
- Increase @q, @d, @p: 0.21 → 0.28 (+0.07)
- Decrease @b: 0.17 → 0.14 (-0.03)
- Decrease @m: 0.04 → 0.00 (-0.04)

**Result**: Methods perfectly matched to context score higher, even with slightly weaker fundamentals.

---

### Pattern 4: Governance Emphasis

**Scenario**: Prioritize institutional quality for governance-focused evaluations.

**Adjustment**:
- Increase @m: 0.04 → 0.08 (+0.04)
- Decrease @u: 0.04 → 0.02 (-0.02)
- Decrease @p: 0.06 → 0.04 (-0.02)

**Result**: PDTs with strong governance frameworks score higher.

---

## Validation and Testing

### Validation Checklist

After adjusting weights, verify:

✅ **Normalization**: Sum of all weights = 1.0 (within 1e-6)
✅ **Non-negativity**: All weights ≥ 0.0
✅ **Bounded**: All weights ≤ 1.0
✅ **Monotonicity**: Increasing any layer score increases final score
✅ **Boundedness**: Cal(I) ∈ [0, 1] for all valid inputs

### Test Suite

```python
def validate_weights(linear_weights: dict, interaction_weights: dict) -> bool:
    """Comprehensive weight validation."""
    
    # 1. Normalization
    total = sum(linear_weights.values()) + sum(interaction_weights.values())
    assert abs(total - 1.0) < 1e-6, f"Weights sum to {total}, expected 1.0"
    
    # 2. Non-negativity
    all_weights = list(linear_weights.values()) + list(interaction_weights.values())
    assert all(w >= 0 for w in all_weights), "Negative weights detected"
    
    # 3. Boundedness
    assert all(w <= 1.0 for w in all_weights), "Weights exceed 1.0"
    
    # 4. Monotonicity (test with synthetic data)
    test_scores = {layer: 0.5 for layer in linear_weights}
    base_score = compute_choquet_score(test_scores, linear_weights, interaction_weights)
    
    for layer in test_scores:
        test_scores_higher = test_scores.copy()
        test_scores_higher[layer] = 0.6
        higher_score = compute_choquet_score(test_scores_higher, linear_weights, interaction_weights)
        assert higher_score >= base_score, f"Non-monotonic for {layer}"
    
    # 5. Boundedness (extremes)
    min_scores = {layer: 0.0 for layer in linear_weights}
    max_scores = {layer: 1.0 for layer in linear_weights}
    
    min_result = compute_choquet_score(min_scores, linear_weights, interaction_weights)
    max_result = compute_choquet_score(max_scores, linear_weights, interaction_weights)
    
    assert 0.0 <= min_result <= 1.0, f"Min score out of bounds: {min_result}"
    assert 0.0 <= max_result <= 1.0, f"Max score out of bounds: {max_result}"
    assert abs(max_result - 1.0) < 1e-6, f"Max score should be 1.0, got {max_result}"
    
    return True
```

### Empirical Validation

Test on validation set (≥50 PDTs):

```python
def validate_on_cohort(
    pdts: list,
    old_weights: dict,
    new_weights: dict
) -> dict:
    """
    Compare scores with old vs new weights.
    
    Returns:
        Validation metrics
    """
    old_scores = [score_pdt(pdt, old_weights) for pdt in pdts]
    new_scores = [score_pdt(pdt, new_weights) for pdt in pdts]
    
    # Correlation (should be high if change is conservative)
    correlation = np.corrcoef(old_scores, new_scores)[0, 1]
    
    # Rank changes (how many PDTs changed rank?)
    old_ranks = np.argsort(old_scores)
    new_ranks = np.argsort(new_scores)
    rank_changes = np.sum(old_ranks != new_ranks)
    
    # Score delta statistics
    deltas = np.array(new_scores) - np.array(old_scores)
    
    return {
        "correlation": correlation,
        "rank_changes": rank_changes,
        "rank_change_percent": 100 * rank_changes / len(pdts),
        "mean_delta": np.mean(deltas),
        "std_delta": np.std(deltas),
        "max_increase": np.max(deltas),
        "max_decrease": np.min(deltas),
    }

# Interpret:
# - correlation > 0.95: Conservative change (good)
# - rank_change_percent < 20%: Stable rankings
# - abs(mean_delta) < 0.05: No systematic bias
```

---

## Examples

### Example 1: Increase @b, Decrease @u

```python
# Current COHORT_2024 weights
current = {
    "@b": 0.17,
    "@chain": 0.13,
    "@q": 0.08,
    "@d": 0.07,
    "@p": 0.06,
    "@C": 0.08,
    "@u": 0.04,
    "@m": 0.04,
}

# Goal: Increase @b to 0.20, decrease @u to 0.01
new = current.copy()
new["@b"] = 0.20  # +0.03
new["@u"] = 0.01  # -0.03

# Check normalization
print(f"Sum = {sum(new.values())}")  # 1.0 ✓

# Validate
validate_weights(new, CHOQUET_INTERACTION_WEIGHTS)
```

### Example 2: Strengthen Interaction Term

```python
# Current
linear_current = {
    "@b": 0.17, "@chain": 0.13, "@q": 0.08, "@d": 0.07,
    "@p": 0.06, "@C": 0.08, "@u": 0.04, "@m": 0.04,
}
interaction_current = {
    ("@u", "@chain"): 0.13,
    ("@chain", "@C"): 0.10,
    ("@q", "@d"): 0.10,
}

# Goal: Strengthen (@u, @chain) to 0.15
linear_new, interaction_new = adjust_interaction_weight(
    linear_current,
    interaction_current,
    ("@u", "@chain"),
    0.15
)

# Result:
# Linear sum reduced from 0.67 to 0.65 (proportional scaling)
# Interaction: 0.15 + 0.10 + 0.10 = 0.35
# Total = 1.00 ✓
```

### Example 3: Policy Area Specialization

```python
# Create PA01-specific weights (gender equality emphasis)
# Increase governance (@m) for institutional analysis

pa01_weights = current.copy()
pa01_weights["@m"] = 0.08  # +0.04 (governance matters more)
pa01_weights["@p"] = 0.02  # -0.04 (less emphasis on cross-area fit)

# Validate
validate_weights(pa01_weights, CHOQUET_INTERACTION_WEIGHTS)

# Save as PA01-specific configuration
with open("calibration/COHORT_2024_weights_PA01.json", "w") as f:
    json.dump(pa01_weights, f, indent=2)
```

---

## Best Practices

### 1. Document All Changes

Every weight adjustment must be documented:

```json
{
  "change_log": [
    {
      "date": "2024-12-16",
      "cohort": "COHORT_2024",
      "change": "Increased @b from 0.17 to 0.20",
      "rationale": "Empirical validation showed @b had strongest correlation with expert assessments",
      "validation_metrics": {
        "correlation_old_new": 0.97,
        "rank_change_percent": 12.5,
        "mean_delta": 0.018
      }
    }
  ]
}
```

### 2. Use Version Control

All weight changes require cohort migration:

- COHORT_2024 → COHORT_2025
- New SHA-256 hash for configuration
- Updated COHORT_MANIFEST.json
- Git tag for traceability

### 3. Validate on Holdout Data

Never tune weights on the same data used for final evaluation:

- Training set (70%): Tune weights
- Validation set (15%): Check generalization
- Test set (15%): Final performance measurement

### 4. Conservative Changes

Prefer small adjustments (≤0.05 per weight) unless strong evidence supports larger changes.

### 5. Maintain Ratios

When adjusting groups, preserve internal ratios unless specifically changing emphasis within group.

### 6. Test Extremes

Verify behavior at boundary conditions:
- All layers at 0.0 (should give Cal(I) = 0.0)
- All layers at 1.0 (should give Cal(I) = 1.0)
- One layer at 1.0, others at 0.0 (should equal that layer's linear weight)

---

## Related Documentation

- [FUSION_FORMULA.md](./FUSION_FORMULA.md) - Mathematical details
- [LAYER_SYSTEM.md](./LAYER_SYSTEM.md) - Layer definitions
- [CONFIG_REFERENCE.md](./CONFIG_REFERENCE.md) - Configuration schemas
- [DETERMINISM.md](./DETERMINISM.md) - Calibration immutability doctrine

---

**Last Updated**: 2024-12-16  
**Version**: 1.0.0  
**Maintainers**: Policy Analytics Research Unit
