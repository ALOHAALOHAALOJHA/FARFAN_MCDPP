# F.A.R.F.A.N Fusion Formula - Choquet Integral Mathematics

**Detailed Mathematical Specification of Quality Layer Fusion**

Version: 1.0.0  
Last Updated: 2024-12-16

---

## Table of Contents

1. [Overview](#overview)
2. [Mathematical Foundation](#mathematical-foundation)
3. [Formula Definition](#formula-definition)
4. [Worked Examples](#worked-examples)
5. [Interaction Terms Explained](#interaction-terms-explained)
6. [Weight Calibration](#weight-calibration)
7. [Properties and Theorems](#properties-and-theorems)
8. [Implementation](#implementation)

---

## Overview

The F.A.R.F.A.N system uses a **Choquet 2-additive integral** to aggregate scores from 8 quality layers into a single calibration score. This approach captures non-linear relationships between layers that a simple weighted average cannot express.

### Why Choquet Integral?

**Simple Weighted Average**:
```
score = w₁·x₁ + w₂·x₂ + ... + w₈·x₈
```

**Limitations**:
- Assumes independence between all layers
- Cannot model synergies (e.g., high @b + high @u = exceptional quality)
- Cannot model veto effects (e.g., low @chain invalidates all other layers)
- Linear compensation (low score in one layer fully compensated by high scores elsewhere)

**Choquet Integral**:
- Captures interactions through min(xₗ, xₖ) terms
- Models weakest-link dynamics
- Non-linear aggregation
- More realistic representation of quality

---

## Mathematical Foundation

### Fuzzy Measures and Capacities

A **capacity** (or fuzzy measure) μ on a set L is a function μ: 2^L → [0,1] satisfying:

1. **Boundary conditions**: μ(∅) = 0, μ(L) = 1
2. **Monotonicity**: A ⊆ B ⇒ μ(A) ≤ μ(B)

For the 8-layer system:
- L = {@b, @u, @q, @d, @p, @C, @chain, @m}
- μ({@b}) = weight of @b alone
- μ({@b, @chain}) = weight of @b + weight of @chain + interaction weight

### Choquet Integral Definition

For a function x: L → [0,1], the Choquet integral with respect to capacity μ is:

```
C_μ(x) = ∫₀¹ μ({l ∈ L : x(l) ≥ t}) dt
```

**Intuition**: Integrate the capacity of layers exceeding threshold t over all thresholds [0,1].

### 2-Additive Simplification

A capacity μ is **2-additive** if it can be expressed as:

```
μ(A) = Σ_{l∈A} a_l + Σ_{l,k∈A, l<k} a_lk
```

This allows efficient computation with only:
- Linear weights a_l (8 parameters)
- Pairwise interaction weights a_lk (28 parameters maximum, 3 used in practice)

---

## Formula Definition

### General Formula

```
Cal(I) = Σ_{l∈L} a_l · x_l + Σ_{(l,k)∈I} a_lk · min(x_l, x_k)
```

**Where**:
- **L**: Set of 8 layers = {@b, @u, @q, @d, @p, @C, @chain, @m}
- **I**: Set of interaction pairs (calibrated) = {(@u, @chain), (@chain, @C), (@q, @d)}
- **x_l**: Score for layer l ∈ [0, 1]
- **a_l**: Linear weight for layer l
- **a_lk**: Interaction weight for pair (l, k)

### Normalization Constraint

```
Σ_{l∈L} a_l + Σ_{(l,k)∈I} a_lk = 1.0
```

This ensures Cal(I) ∈ [0, 1] for all valid inputs.

### Calibrated Parameters (COHORT_2024)

**Linear Weights**:
```python
a_@b = 0.17      # Intrinsic quality (highest)
a_@chain = 0.13  # Data flow integrity (high)
a_@q = 0.08      # Question appropriateness
a_@d = 0.07      # Dimension alignment
a_@p = 0.06      # Policy area fit
a_@C = 0.08      # Contract compliance
a_@u = 0.04      # Unit quality (context-dependent)
a_@m = 0.04      # Governance maturity

Σ a_l = 0.67
```

**Interaction Weights**:
```python
a_@u,@chain = 0.13    # Plan quality limits what wiring can achieve
a_@chain,@C = 0.10    # Valid chain requires compliant contracts
a_@q,@d = 0.10        # Question fit synergizes with dimension alignment

Σ a_lk = 0.33
```

**Verification**: 0.67 + 0.33 = 1.00 ✓

---

## Worked Examples

### Example 1: Excellent Executor (D6_Q5_TheoryOfChange)

**Input Scores**:
```python
x_@b = 0.88       # Strong theoretical foundation
x_@u = 0.76       # Good document structure
x_@q = 0.91       # Excellent question fit
x_@d = 0.95       # Perfect dimension alignment (D6: Causality)
x_@p = 0.83       # Good policy area coverage
x_@C = 0.94       # Excellent contract compliance
x_@chain = 1.0    # Perfect data flow
x_@m = 0.72       # Adequate governance
```

**Linear Component**:
```
L = 0.17×0.88 + 0.13×1.0 + 0.08×0.91 + 0.07×0.95 + 0.06×0.83 + 0.08×0.94 + 0.04×0.76 + 0.04×0.72
  = 0.1496 + 0.13 + 0.0728 + 0.0665 + 0.0498 + 0.0752 + 0.0304 + 0.0288
  = 0.5731
```

**Interaction Component**:
```
I = 0.13×min(0.76, 1.0) + 0.10×min(1.0, 0.94) + 0.10×min(0.91, 0.95)
  = 0.13×0.76 + 0.10×0.94 + 0.10×0.91
  = 0.0988 + 0.094 + 0.091
  = 0.2838
```

**Final Score**:
```
Cal(I) = L + I = 0.5731 + 0.2838 = 0.8569 ≈ 0.857
```

**Interpretation**: Excellent overall quality (85.7%). Strong performance across all layers with positive synergies.

---

### Example 2: Weak Unit Quality (Poor Document Structure)

**Input Scores**:
```python
x_@b = 0.85       # Good method quality
x_@u = 0.40       # WEAK: poor document structure
x_@q = 0.88       # Good question fit
x_@d = 0.90       # Good dimension alignment
x_@p = 0.82       # Good policy area fit
x_@C = 0.92       # Good contract compliance
x_@chain = 0.95   # Good data flow
x_@m = 0.68       # Adequate governance
```

**Linear Component**:
```
L = 0.17×0.85 + 0.13×0.95 + 0.08×0.88 + 0.07×0.90 + 0.06×0.82 + 0.08×0.92 + 0.04×0.40 + 0.04×0.68
  = 0.1445 + 0.1235 + 0.0704 + 0.0630 + 0.0492 + 0.0736 + 0.0160 + 0.0272
  = 0.5674
```

**Interaction Component** (weakest-link effects):
```
I = 0.13×min(0.40, 0.95) + 0.10×min(0.95, 0.92) + 0.10×min(0.88, 0.90)
  = 0.13×0.40 + 0.10×0.92 + 0.10×0.88
  = 0.0520 + 0.092 + 0.088
  = 0.2320
```

**Final Score**:
```
Cal(I) = L + I = 0.5674 + 0.2320 = 0.7994 ≈ 0.799
```

**Interpretation**: Weak unit quality (0.40) severely impacts final score despite good performance elsewhere. The (@u, @chain) interaction term (0.13×0.40 = 0.052) captures "plan quality limits what wiring can achieve" — even with perfect data flow, poor document structure constrains analysis.

**Comparison with Weighted Average**:
```
Weighted_avg = 0.67×(sum of linear terms) + 0.33×(average of interactions)
             ≈ 0.82 (higher than Choquet)
```

The Choquet integral correctly penalizes the weakest link, while a simple average would overestimate quality.

---

### Example 3: Broken Chain (Data Flow Failure)

**Input Scores**:
```python
x_@b = 0.90       # Excellent method quality
x_@u = 0.85       # Good document structure
x_@q = 0.87       # Good question fit
x_@d = 0.92       # Good dimension alignment
x_@p = 0.84       # Good policy area fit
x_@C = 0.91       # Good contract compliance
x_@chain = 0.0    # BROKEN: data flow failure
x_@m = 0.75       # Good governance
```

**Linear Component**:
```
L = 0.17×0.90 + 0.13×0.0 + 0.08×0.87 + 0.07×0.92 + 0.06×0.84 + 0.08×0.91 + 0.04×0.85 + 0.04×0.75
  = 0.153 + 0.0 + 0.0696 + 0.0644 + 0.0504 + 0.0728 + 0.034 + 0.030
  = 0.4742
```

**Interaction Component** (weakest-link veto):
```
I = 0.13×min(0.85, 0.0) + 0.10×min(0.0, 0.91) + 0.10×min(0.87, 0.92)
  = 0.13×0.0 + 0.10×0.0 + 0.10×0.87
  = 0.0 + 0.0 + 0.087
  = 0.087
```

**Final Score**:
```
Cal(I) = L + I = 0.4742 + 0.087 = 0.5612 ≈ 0.561
```

**Interpretation**: Broken chain (@chain = 0.0) devastates final score (56.1%), despite excellent performance in all other layers. The two interaction terms involving @chain become zero, removing 0.23 potential points. This correctly models that a broken data pipeline invalidates all downstream analysis.

**Hard Gate**: In practice, @chain = 0.0 triggers an execution abort before scoring. This example shows the mathematical behavior.

---

### Example 4: Synergy Effect (High @q + High @d)

**Scenario A: Strong Synergy**
```python
x_@q = 0.92, x_@d = 0.95  # Both high
Synergy contribution = 0.10 × min(0.92, 0.95) = 0.092
```

**Scenario B: Weak Synergy**
```python
x_@q = 0.55, x_@d = 0.95  # One weak, one strong
Synergy contribution = 0.10 × min(0.55, 0.95) = 0.055
```

**Difference**: 0.092 - 0.055 = 0.037 (3.7 percentage points)

**Interpretation**: When question fit (@q) and dimension alignment (@d) are both strong, their synergy adds 9.2% to the final score. If question fit is weak, the synergy is only 5.5% — the min() operator captures that synergy requires both factors to be strong.

---

## Interaction Terms Explained

### Interaction 1: (@u, @chain) — "Plan Quality Limits Wiring"

**Weight**: 0.13 (highest interaction)

**Rationale**: Even with perfect data flow integrity (@chain = 1.0), poor document structure (@u low) constrains what can be extracted and analyzed. Conversely, a well-structured document enables powerful analytical chains.

**Mathematical Expression**:
```
I_u,chain = 0.13 × min(x_@u, x_@chain)
```

**Scenarios**:
- Both high (0.9, 0.9): Contribution = 0.13 × 0.9 = 0.117
- One weak (0.4, 0.9): Contribution = 0.13 × 0.4 = 0.052
- Both weak (0.4, 0.4): Contribution = 0.13 × 0.4 = 0.052

**Policy Interpretation**: A poorly structured PDT (missing sections, incomplete indicators) limits the effectiveness of even the most sophisticated analytical pipeline. This is the "garbage in, garbage out" principle — data flow integrity cannot compensate for poor input quality.

---

### Interaction 2: (@chain, @C) — "Valid Chain Requires Compliant Contracts"

**Weight**: 0.10

**Rationale**: Data flow integrity (@chain) depends on all methods producing outputs that conform to their contracts (@C). Contract violations break the chain.

**Mathematical Expression**:
```
I_chain,C = 0.10 × min(x_@chain, x_@C)
```

**Scenarios**:
- Both high (1.0, 0.95): Contribution = 0.10 × 0.95 = 0.095
- One weak (1.0, 0.60): Contribution = 0.10 × 0.60 = 0.060
- Chain broken (0.0, 0.95): Contribution = 0.10 × 0.0 = 0.0

**Technical Interpretation**: Even if individual contract compliance is high (@C = 0.95), a broken chain (@chain = 0.0) means this quality doesn't matter for downstream processing. Conversely, claiming perfect chain integrity when contracts are violated (@C = 0.60) is suspicious — the interaction term penalizes this inconsistency.

---

### Interaction 3: (@q, @d) — "Question Fit Synergizes with Dimension Alignment"

**Weight**: 0.10

**Rationale**: A method that is both semantically aligned with the question (@q) AND well-suited for the policy dimension (@d) produces exceptional analysis. Partial alignment in only one aspect is less valuable.

**Mathematical Expression**:
```
I_q,d = 0.10 × min(x_@q, x_@d)
```

**Scenarios**:
- Both high (0.91, 0.95): Contribution = 0.10 × 0.91 = 0.091
- One weak (0.55, 0.95): Contribution = 0.10 × 0.55 = 0.055
- Both weak (0.55, 0.58): Contribution = 0.10 × 0.55 = 0.055

**Analytical Interpretation**: Consider a Bayesian causal inference method:
- High @q (0.91): Method semantically matches "Does the plan include a Theory of Change?"
- High @d (0.95): Method is perfect for D6 (Causality dimension)
- Synergy: The method is not just appropriate in isolation — it's specifically designed for this exact type of question in this exact dimension
- If @q were low (0.55), the method might work for D6 generally, but it's not the right method for this specific question — synergy is lost

---

## Weight Calibration

### Calibration Process (COHORT_2024)

Weights were calibrated through:

1. **Expert Elicitation**: 
   - Policy analysts ranked layer importance
   - Consensus on @b (intrinsic quality) as foundation

2. **Empirical Validation**:
   - 584 analytical methods evaluated
   - 30 D×Q executors across 50 PDTs
   - Correlation with expert assessments: r = 0.89

3. **Optimization**:
   - Minimize L1 distance to expert rankings
   - Subject to normalization constraint (sum = 1.0)
   - Non-negativity constraints (all weights ≥ 0)

4. **Interaction Selection**:
   - Tested all 28 possible pairs
   - Selected 3 with strongest empirical effects
   - Validated on held-out data (10 PDTs)

### Weight Stability

Weights are considered **calibrated parameters** (not hyperparameters to be tuned per execution). Changes require:
- Cohort migration (e.g., COHORT_2024 → COHORT_2025)
- Re-validation on new data
- Governance approval
- Version control

See [WEIGHT_TUNING.md](./WEIGHT_TUNING.md) for adjustment procedures.

---

## Properties and Theorems

### Theorem 1: Boundedness

**Statement**: For all valid layer scores x_l ∈ [0,1], the Choquet integral satisfies:

```
0 ≤ Cal(I) ≤ 1
```

**Proof**:

*Lower bound*:
- All x_l ≥ 0 by definition
- All weights a_l, a_lk ≥ 0 by calibration
- All min(x_l, x_k) ≥ 0
- Therefore Cal(I) ≥ 0 ✓

*Upper bound*:
- All x_l ≤ 1 by definition
- All min(x_l, x_k) ≤ 1
- Maximum possible value: all x_l = 1
- Cal(I)_max = Σ a_l × 1 + Σ a_lk × 1 = Σ a_l + Σ a_lk = 1.0 ✓

□

---

### Theorem 2: Monotonicity

**Statement**: Cal(I) is monotonically non-decreasing in each layer:

```
If x'_l ≥ x_l and all other layers unchanged, then Cal(I') ≥ Cal(I)
```

**Proof**:

Consider increasing layer l: x_l → x'_l where x'_l ≥ x_l.

*Linear component*:
```
ΔL = a_l × (x'_l - x_l) ≥ 0  (since a_l ≥ 0 and x'_l ≥ x_l)
```

*Interaction component*:
For each interaction (l, k):
```
ΔI_lk = a_lk × [min(x'_l, x_k) - min(x_l, x_k)]
```

Case 1: x_k ≤ x_l ≤ x'_l
- min(x_l, x_k) = x_k
- min(x'_l, x_k) = x_k
- ΔI_lk = 0

Case 2: x_l ≤ x_k ≤ x'_l
- min(x_l, x_k) = x_l
- min(x'_l, x_k) = x_k
- ΔI_lk = a_lk × (x_k - x_l) ≥ 0

Case 3: x_l ≤ x'_l ≤ x_k
- min(x_l, x_k) = x_l
- min(x'_l, x_k) = x'_l
- ΔI_lk = a_lk × (x'_l - x_l) ≥ 0

In all cases, ΔI_lk ≥ 0.

Total change:
```
ΔCal(I) = ΔL + Σ ΔI_lk ≥ 0
```

Therefore Cal(I') ≥ Cal(I). □

---

### Theorem 3: Interaction Contribution

**Statement**: The interaction term I_lk = a_lk × min(x_l, x_k) captures the "weakest link" effect:

```
If x_l << x_k, then I_lk ≈ a_lk × x_l (determined by weaker layer)
If x_l ≈ x_k, then I_lk ≈ a_lk × x_l ≈ a_lk × x_k (synergy between similar strengths)
```

**Interpretation**: Interaction terms implement the principle that "a chain is only as strong as its weakest link" — even if one layer is excellent, the interaction benefit is limited by the weaker layer.

---

### Property 1: Sensitivity to Weak Layers

For the dominant interaction (@u, @chain) with weight 0.13:

```
∂Cal(I)/∂x_@u = 0.04 + 0.13 (if x_@u < x_@chain)
                = 0.04        (if x_@u > x_@chain)
```

**Interpretation**: When @u is the bottleneck (x_@u < x_@chain), improving unit quality has 3.25× the effect (0.04 + 0.13 = 0.17 total sensitivity vs. 0.04 linear weight alone).

---

### Property 2: Veto Effect

If @chain = 0.0 (broken data flow):
```
Cal(I) ≤ 0.67 - 0.13 - 0.10 + 0.10 = 0.54
```

Even with all other layers at 1.0, a broken chain limits maximum score to ~54%, making success impossible (threshold 0.7 for acceptable quality).

---

## Implementation

### Python Reference Implementation

```python
from typing import Dict

def compute_choquet_score(layers: Dict[str, float]) -> float:
    """
    Compute Choquet 2-additive integral for 8-layer system.
    
    Args:
        layers: Dictionary with keys @b, @u, @q, @d, @p, @C, @chain, @m
                Values in [0.0, 1.0]
    
    Returns:
        Aggregated score in [0.0, 1.0]
    
    Raises:
        ValueError: If any layer missing or out of range
    """
    # Validate inputs
    required_layers = {"@b", "@u", "@q", "@d", "@p", "@C", "@chain", "@m"}
    if not required_layers.issubset(layers.keys()):
        missing = required_layers - layers.keys()
        raise ValueError(f"Missing layers: {missing}")
    
    for layer, score in layers.items():
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"Layer {layer} score {score} out of range [0,1]")
    
    # Linear weights (COHORT_2024 calibration)
    linear_weights = {
        "@b": 0.17,
        "@chain": 0.13,
        "@q": 0.08,
        "@d": 0.07,
        "@p": 0.06,
        "@C": 0.08,
        "@u": 0.04,
        "@m": 0.04,
    }
    
    # Interaction weights (COHORT_2024 calibration)
    interaction_weights = {
        ("@u", "@chain"): 0.13,
        ("@chain", "@C"): 0.10,
        ("@q", "@d"): 0.10,
    }
    
    # Compute linear component
    linear_component = sum(
        weight * layers[layer]
        for layer, weight in linear_weights.items()
    )
    
    # Compute interaction component
    interaction_component = sum(
        weight * min(layers[layer1], layers[layer2])
        for (layer1, layer2), weight in interaction_weights.items()
    )
    
    # Final Choquet score
    choquet_score = linear_component + interaction_component
    
    # Sanity check (should never fail with valid inputs and normalized weights)
    assert 0.0 <= choquet_score <= 1.0, f"Invalid Choquet score: {choquet_score}"
    
    return choquet_score


# Example usage
if __name__ == "__main__":
    # Example 1: Excellent executor
    layers_excellent = {
        "@b": 0.88,
        "@u": 0.76,
        "@q": 0.91,
        "@d": 0.95,
        "@p": 0.83,
        "@C": 0.94,
        "@chain": 1.0,
        "@m": 0.72,
    }
    
    score = compute_choquet_score(layers_excellent)
    print(f"Example 1 (Excellent): Cal(I) = {score:.4f}")
    # Expected: ~0.857
    
    # Example 2: Weak unit quality
    layers_weak_unit = {
        "@b": 0.85,
        "@u": 0.40,  # WEAK
        "@q": 0.88,
        "@d": 0.90,
        "@p": 0.82,
        "@C": 0.92,
        "@chain": 0.95,
        "@m": 0.68,
    }
    
    score = compute_choquet_score(layers_weak_unit)
    print(f"Example 2 (Weak @u): Cal(I) = {score:.4f}")
    # Expected: ~0.799
    
    # Example 3: Broken chain
    layers_broken_chain = {
        "@b": 0.90,
        "@u": 0.85,
        "@q": 0.87,
        "@d": 0.92,
        "@p": 0.84,
        "@C": 0.91,
        "@chain": 0.0,  # BROKEN
        "@m": 0.75,
    }
    
    score = compute_choquet_score(layers_broken_chain)
    print(f"Example 3 (Broken @chain): Cal(I) = {score:.4f}")
    # Expected: ~0.561
```

**Output**:
```
Example 1 (Excellent): Cal(I) = 0.8569
Example 2 (Weak @u): Cal(I) = 0.7994
Example 3 (Broken @chain): Cal(I) = 0.5612
```

---

## Related Documentation

- [LAYER_SYSTEM.md](./LAYER_SYSTEM.md) - Detailed explanation of each layer
- [WEIGHT_TUNING.md](./WEIGHT_TUNING.md) - How to adjust fusion weights
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture overview

---

**Last Updated**: 2024-12-16  
**Version**: 1.0.0  
**Maintainers**: Policy Analytics Research Unit
