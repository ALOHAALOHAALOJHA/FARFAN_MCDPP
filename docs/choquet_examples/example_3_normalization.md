# Choquet Aggregator Example 3: Weight Normalization

## Scenario
Demonstrating automatic weight normalization to ensure boundedness.

## Initial Configuration (Unnormalized)
```python
config = ChoquetConfig(
    linear_weights={
        "@b": 4.0,      # Raw weight
        "@chain": 3.0,
        "@q": 2.0,
        "@d": 1.0
    },
    interaction_weights={
        ("@b", "@chain"): 1.5,
        ("@q", "@d"): 0.5
    },
    normalize_weights=True,  # Enable normalization
    validate_boundedness=True
)
```

## Input Layer Scores
```python
layer_scores = {
    "@b": 0.90,
    "@chain": 0.85,
    "@q": 0.75,
    "@d": 0.80
}
```

## Step-by-Step Normalization

### Step 1: Normalize Linear Weights
Formula: `aₗ_normalized = aₗ / Σ(aₗ)`

#### Calculate Sum
```
Σ(aₗ) = 4.0 + 3.0 + 2.0 + 1.0 = 10.0
```

#### Normalize Each Weight
```
a[@b]_norm = 4.0 / 10.0 = 0.40
a[@chain]_norm = 3.0 / 10.0 = 0.30
a[@q]_norm = 2.0 / 10.0 = 0.20
a[@d]_norm = 1.0 / 10.0 = 0.10
```

Verification: `0.40 + 0.30 + 0.20 + 0.10 = 1.00` ✓

### Step 2: Normalize Interaction Weights
Interaction weights are constrained to ensure boundedness:
```
Σ(aₗₖ) ≤ min(Σ(aₗ_norm), 1.0) × 0.5
```

#### Calculate Constraint
```
max_allowed = min(1.00, 1.0) × 0.5 = 0.50
```

#### Check Raw Interaction Sum
```
Σ(aₗₖ) = 1.5 + 0.5 = 2.0
```

Since `2.0 > 0.50`, we need to scale down:

#### Scale Factor
```
scale_factor = max_allowed / Σ(aₗₖ)
             = 0.50 / 2.0
             = 0.25
```

#### Normalized Interaction Weights
```
a[@b,@chain]_norm = 1.5 × 0.25 = 0.375
a[@q,@d]_norm = 0.5 × 0.25 = 0.125
```

Verification: `0.375 + 0.125 = 0.50` ✓

## Computation with Normalized Weights

### Step 3: Compute Linear Sum
Formula: `linear_sum = Σ(aₗ_norm·xₗ)`

```
linear_sum = 0.40 · 0.90 + 0.30 · 0.85 + 0.20 · 0.75 + 0.10 · 0.80
           = 0.3600 + 0.2550 + 0.1500 + 0.0800
           = 0.8450
```

Per-layer contributions:
- `@b`: 0.40 × 0.90 = 0.3600
- `@chain`: 0.30 × 0.85 = 0.2550
- `@q`: 0.20 × 0.75 = 0.1500
- `@d`: 0.10 × 0.80 = 0.0800

### Step 4: Compute Interaction Sum
Formula: `interaction_sum = Σ(aₗₖ_norm·min(xₗ,xₖ))`

#### Interaction 1: (@b, @chain)
```
contribution₁ = 0.375 · min(0.90, 0.85)
              = 0.375 · 0.85
              = 0.3188
```

#### Interaction 2: (@q, @d)
```
contribution₂ = 0.125 · min(0.75, 0.80)
              = 0.125 · 0.75
              = 0.0938
```

#### Total
```
interaction_sum = 0.3188 + 0.0938 = 0.4126
```

### Step 5: Compute Final Score
```
Cal(I) = linear_sum + interaction_sum
       = 0.8450 + 0.4126
       = 1.2576
```

**WARNING**: This exceeds 1.0! This shows why normalization is critical.

### Step 6: Apply Boundedness Clamping
Since `Cal(I) > 1.0`, the aggregator clamps to [0,1]:
```
Cal(I)_clamped = min(1.0, 1.2576) = 1.0000
```

## Result Summary
```
Subject: "HighPerformingMethod"
Calibration Score: 1.0000 (clamped from 1.2576)
Linear Contribution: 0.8450
Interaction Contribution: 0.4126
Validation: WARNING (exceeded upper bound, clamped)
```

## Breakdown
```json
{
    "normalized_linear_weights": {
        "@b": 0.40,
        "@chain": 0.30,
        "@q": 0.20,
        "@d": 0.10
    },
    "normalized_interaction_weights": {
        ("@b", "@chain"): 0.375,
        ("@q", "@d"): 0.125
    },
    "per_layer_contributions": {
        "@b": 0.3600,
        "@chain": 0.2550,
        "@q": 0.1500,
        "@d": 0.0800
    },
    "per_interaction_contributions": {
        ("@b", "@chain"): 0.3188,
        ("@q", "@d"): 0.0938
    }
}
```

## Key Lessons

### 1. Weight Normalization Preserves Ratios
Original ratios:
```
@b : @chain : @q : @d = 4 : 3 : 2 : 1
```

Normalized ratios:
```
@b : @chain : @q : @d = 0.4 : 0.3 : 0.2 : 0.1 = 4 : 3 : 2 : 1 ✓
```

The relative importance is preserved.

### 2. Interaction Scaling Prevents Overflow
Without scaling interactions (raw sum = 2.0), we would have:
```
Cal(I)_unscaled ≈ 0.8450 + (raw_interactions) → potential overflow
```

With scaling (scaled sum = 0.50), we constrain:
```
Cal(I) ≤ 1.0 (approximately, modulo edge cases)
```

### 3. Clamping as Last Resort
Even with normalization, edge cases (all scores ≈ 1.0, strong interactions) can
exceed bounds. The aggregator applies final clamping:
```python
calibration_score = max(0.0, min(1.0, calibration_score))
```

This ensures contractual guarantee: `0.0 ≤ Cal(I) ≤ 1.0`

### 4. When to Use Normalization

#### Enable (`normalize_weights=True`):
- Weights are arbitrary/not pre-normalized
- Configuration comes from user input
- Robustness against misconfiguration is critical

#### Disable (`normalize_weights=False`):
- Weights are already carefully normalized
- You want exact control over weight distribution
- Debugging/testing specific weight combinations

## Comparison: With vs. Without Normalization

### Without Normalization (Raw Weights)
```
linear_sum = 4.0·0.90 + 3.0·0.85 + 2.0·0.75 + 1.0·0.80
           = 3.60 + 2.55 + 1.50 + 0.80
           = 8.45

interaction_sum = 1.5·min(0.90,0.85) + 0.5·min(0.75,0.80)
                = 1.5·0.85 + 0.5·0.75
                = 1.275 + 0.375
                = 1.65

Cal(I) = 8.45 + 1.65 = 10.10 ❌ INVALID (> 1.0)
```

This would raise `CalibrationConfigError` if `validate_boundedness=True`.

### With Normalization (Normalized Weights)
```
Cal(I) = 0.8450 + 0.4126 = 1.2576 → clamp to 1.0000 ✓
```

While still requiring clamping in this extreme case, normalization brings the 
score much closer to a valid range and prevents gross violations.

## Recommendation
Always use `normalize_weights=True` unless you have a specific reason not to.
The performance cost is negligible, and the safety benefit is substantial.
