# Choquet Aggregator Example 4: Boundary Cases and Edge Conditions

## Scenario
Testing behavior at boundary conditions and extreme inputs.

---

## Case 1: All Scores = 0 (Worst Case)

### Configuration
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.5, "@chain": 0.3, "@q": 0.2},
    interaction_weights={("@b", "@chain"): 0.1},
    normalize_weights=False
)
```

### Input
```python
layer_scores = {"@b": 0.0, "@chain": 0.0, "@q": 0.0}
```

### Computation

#### Linear Sum
```
linear_sum = 0.5 · 0.0 + 0.3 · 0.0 + 0.2 · 0.0
           = 0.0
```

#### Interaction Sum
```
interaction_sum = 0.1 · min(0.0, 0.0)
                = 0.1 · 0.0
                = 0.0
```

#### Final Score
```
Cal(I) = 0.0 + 0.0 = 0.0
```

### Validation
```
0.0 ≤ 0.0 ≤ 1.0  ✓
```

**Result**: Perfect lower bound. Method with zero quality scores correctly yields Cal(I) = 0.

---

## Case 2: All Scores = 1 (Perfect Case)

### Configuration
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.3},
    interaction_weights={},
    normalize_weights=False
)
```

### Input
```python
layer_scores = {"@b": 1.0, "@chain": 1.0, "@q": 1.0}
```

### Computation

#### Linear Sum
```
linear_sum = 0.4 · 1.0 + 0.3 · 1.0 + 0.3 · 1.0
           = 0.4 + 0.3 + 0.3
           = 1.0
```

#### Interaction Sum
```
interaction_sum = 0.0  (no interactions defined)
```

#### Final Score
```
Cal(I) = 1.0 + 0.0 = 1.0
```

### Validation
```
0.0 ≤ 1.0 ≤ 1.0  ✓
```

**Result**: Perfect upper bound. Method with perfect scores yields Cal(I) = 1.0 when weights sum to 1.0.

---

## Case 3: Single Layer Dominates

### Configuration
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.95, "@chain": 0.03, "@q": 0.02},
    interaction_weights={},
    normalize_weights=False
)
```

### Input
```python
layer_scores = {
    "@b": 0.50,      # Dominant layer, mediocre score
    "@chain": 1.00,  # Perfect score, tiny weight
    "@q": 1.00       # Perfect score, tiny weight
}
```

### Computation

#### Linear Sum
```
linear_sum = 0.95 · 0.50 + 0.03 · 1.00 + 0.02 · 1.00
           = 0.4750 + 0.0300 + 0.0200
           = 0.5250
```

#### Final Score
```
Cal(I) = 0.5250
```

### Interpretation
Despite two layers having perfect scores (1.0), the overall calibration is only 
0.525 because the dominant layer (@b with 95% weight) has a mediocre score (0.50).

**Lesson**: Weight distribution critically determines which layers matter. A single 
highly-weighted layer can dominate the aggregate score.

---

## Case 4: Extreme Asymmetry in Interactions

### Configuration
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.5, "@chain": 0.5},
    interaction_weights={("@b", "@chain"): 0.3},
    normalize_weights=False,
    validate_boundedness=False  # Disable to see raw behavior
)
```

### Input
```python
layer_scores = {"@b": 1.0, "@chain": 0.0}
```

### Computation

#### Linear Sum
```
linear_sum = 0.5 · 1.0 + 0.5 · 0.0
           = 0.5 + 0.0
           = 0.5
```

#### Interaction Sum
```
interaction_sum = 0.3 · min(1.0, 0.0)
                = 0.3 · 0.0
                = 0.0
```

**Key Insight**: The interaction term vanishes because min(1.0, 0.0) = 0.0.
Synergy requires BOTH components to have non-zero scores.

#### Final Score
```
Cal(I) = 0.5 + 0.0 = 0.5
```

### Interpretation
Even though @b is perfect (1.0), the interaction with @chain contributes nothing
because @chain is zero. This correctly models the principle that **synergies require
mutual presence** — a perfect base layer cannot synergize with an absent chain.

---

## Case 5: Exactly at Upper Bound (Edge Case)

### Configuration
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.6, "@chain": 0.4},
    interaction_weights={("@b", "@chain"): 0.4},
    normalize_weights=False,
    validate_boundedness=True
)
```

### Input
```python
layer_scores = {"@b": 1.0, "@chain": 1.0}
```

### Computation

#### Linear Sum
```
linear_sum = 0.6 · 1.0 + 0.4 · 1.0 = 1.0
```

#### Interaction Sum
```
interaction_sum = 0.4 · min(1.0, 1.0)
                = 0.4 · 1.0
                = 0.4
```

#### Raw Sum
```
Cal(I)_raw = 1.0 + 0.4 = 1.4  ❌ Exceeds 1.0
```

### Boundedness Validation
Since `validate_boundedness=True`, this raises:
```
CalibrationConfigError: Boundedness violation: Cal(I)=1.4000 not in [0,1]
```

### Solution 1: Reduce Interaction Weight
```python
interaction_weights={("@b", "@chain"): 0.0}  # No interaction
```

Then: `Cal(I) = 1.0 + 0.0 = 1.0` ✓

### Solution 2: Enable Normalization
```python
normalize_weights=True
```

The normalization will scale down interaction weights to ensure boundedness.

### Solution 3: Clamp Output
```python
validate_boundedness=False
```

The aggregator will clamp: `Cal(I) = min(1.0, 1.4) = 1.0`

---

## Case 6: Negative Scores (Invalid Input)

### Configuration
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.5, "@chain": 0.5},
    interaction_weights={}
)
```

### Input (Invalid)
```python
layer_scores = {"@b": -0.3, "@chain": 0.8}
```

### Behavior
The aggregator detects the out-of-range score and logs a warning:
```
WARNING: Layer @b score -0.3 outside [0,1], clamping
```

Then clamps to valid range:
```
x[@b]_clamped = max(0.0, min(1.0, -0.3)) = 0.0
```

### Computation
```
linear_sum = 0.5 · 0.0 + 0.5 · 0.8 = 0.4
Cal(I) = 0.4
```

**Lesson**: The aggregator is defensive against invalid inputs, clamping scores
to [0,1] rather than failing. This ensures robustness but may mask upstream bugs.

---

## Case 7: Empty Interactions (Degenerates to Weighted Average)

### Configuration
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.3, "@chain": 0.3, "@q": 0.4},
    interaction_weights={},  # No interactions
    normalize_weights=False
)
```

### Input
```python
layer_scores = {"@b": 0.7, "@chain": 0.6, "@q": 0.8}
```

### Computation

#### Linear Sum
```
linear_sum = 0.3 · 0.7 + 0.3 · 0.6 + 0.4 · 0.8
           = 0.21 + 0.18 + 0.32
           = 0.71
```

#### Interaction Sum
```
interaction_sum = 0.0
```

#### Final Score
```
Cal(I) = 0.71
```

### Observation
With `interaction_weights={}`, the Choquet integral reduces to a standard
weighted average:
```
Cal(I) = Σ(wₗ · xₗ) = weighted_average
```

**Use Case**: If you don't need interaction modeling, you can use ChoquetAggregator
with empty interactions as a drop-in replacement for weighted averaging, gaining
the benefits of structured configuration and validation.

---

## Summary Table

| Case | Scores | Weights | Interactions | Cal(I) | Valid? | Notes |
|------|--------|---------|--------------|--------|--------|-------|
| 1 | All 0.0 | Uniform | Single | 0.0000 | ✓ | Perfect lower bound |
| 2 | All 1.0 | Normalized | None | 1.0000 | ✓ | Perfect upper bound |
| 3 | Mixed | Skewed | None | 0.5250 | ✓ | Dominant layer effect |
| 4 | Asymmetric | Equal | Strong | 0.5000 | ✓ | Interaction vanishes |
| 5 | All 1.0 | Unnormalized | Strong | 1.4000 | ❌ | Exceeds bound |
| 6 | Negative | Equal | None | 0.4000 | ⚠️ | Clamped to [0,1] |
| 7 | Mixed | Uniform | None | 0.7100 | ✓ | Degenerates to WA |

**Key Takeaways**:
1. Choquet aggregator handles boundary cases gracefully
2. Normalization prevents most bound violations
3. Interactions require mutual non-zero scores to contribute
4. Without interactions, Choquet = weighted average
5. Defensive clamping prevents catastrophic failures from bad inputs
