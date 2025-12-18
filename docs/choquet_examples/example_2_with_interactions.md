# Choquet Aggregator Example 2: With Interaction Terms

## Scenario
Aggregating three calibration layers WITH interaction terms to capture synergies.

## Configuration
```python
config = ChoquetConfig(
    linear_weights={
        "@b": 0.35,
        "@chain": 0.30,
        "@q": 0.25
    },
    interaction_weights={
        ("@b", "@chain"): 0.10,   # Synergy: base quality + chain quality
        ("@chain", "@q"): 0.05    # Synergy: chain + question relevance
    },
    normalize_weights=False,
    validate_boundedness=True
)
```

## Input Layer Scores
```python
layer_scores = {
    "@b": 0.80,      # Base layer
    "@chain": 0.70,  # Chain layer
    "@q": 0.85       # Question layer
}
```

## Step-by-Step Computation

### Step 1: Compute Linear Sum
Formula: `linear_sum = Σ(aₗ·xₗ)`

Expand for each layer:
```
linear_sum = a[@b] · x[@b] + a[@chain] · x[@chain] + a[@q] · x[@q]
           = 0.35 · 0.80 + 0.30 · 0.70 + 0.25 · 0.85
           = 0.2800 + 0.2100 + 0.2125
           = 0.7025
```

Per-layer contributions:
- `@b`: 0.35 × 0.80 = 0.2800
- `@chain`: 0.30 × 0.70 = 0.2100
- `@q`: 0.25 × 0.85 = 0.2125

### Step 2: Compute Interaction Sum
Formula: `interaction_sum = Σ(aₗₖ·min(xₗ,xₖ))`

#### Interaction 1: (@b, @chain)
```
contribution₁ = a[@b,@chain] · min(x[@b], x[@chain])
              = 0.10 · min(0.80, 0.70)
              = 0.10 · 0.70
              = 0.0700
```

Rationale: Base quality (0.80) and chain quality (0.70) synergize. The interaction 
is limited by the weaker component (chain), hence min(0.80, 0.70) = 0.70.

#### Interaction 2: (@chain, @q)
```
contribution₂ = a[@chain,@q] · min(x[@chain], x[@q])
              = 0.05 · min(0.70, 0.85)
              = 0.05 · 0.70
              = 0.0350
```

Rationale: Chain quality (0.70) and question relevance (0.85) synergize. Limited
by the weaker chain component, hence min(0.70, 0.85) = 0.70.

#### Total Interaction Sum
```
interaction_sum = contribution₁ + contribution₂
                = 0.0700 + 0.0350
                = 0.1050
```

Per-interaction contributions:
- `(@b, @chain)`: 0.0700
- `(@chain, @q)`: 0.0350

### Step 3: Compute Final Calibration Score
Formula: `Cal(I) = linear_sum + interaction_sum`

```
Cal(I) = 0.7025 + 0.1050
       = 0.8075
```

### Step 4: Validate Boundedness
Check: `0.0 ≤ Cal(I) ≤ 1.0`

```
0.0 ≤ 0.8075 ≤ 1.0  ✓
```

Boundedness constraint satisfied.

## Result Summary
```
Subject: "ExampleMethodWithSynergies"
Calibration Score: 0.8075
Linear Contribution: 0.7025
Interaction Contribution: 0.1050
Validation: PASSED
```

## Breakdown
```json
{
    "per_layer_contributions": {
        "@b": 0.2800,
        "@chain": 0.2100,
        "@q": 0.2125
    },
    "per_interaction_contributions": {
        ("@b", "@chain"): 0.0700,
        ("@chain", "@q"): 0.0350
    },
    "per_layer_rationales": {
        "@b": "Layer @b: weight=0.3500 × score=0.8000 = 0.2800",
        "@chain": "Layer @chain: weight=0.3000 × score=0.7000 = 0.2100",
        "@q": "Layer @q: weight=0.2500 × score=0.8500 = 0.2125"
    },
    "per_interaction_rationales": {
        ("@b", "@chain"): "Interaction (@b, @chain): weight=0.1000 × min(0.8000, 0.7000) = 0.0700",
        ("@chain", "@q"): "Interaction (@chain, @q): weight=0.0500 × min(0.7000, 0.8500) = 0.0350"
    }
}
```

## Interpretation

### Without Interactions (Hypothetical)
If we only used linear aggregation:
```
Cal(I)_linear = 0.7025
```

### With Interactions (Actual)
```
Cal(I)_choquet = 0.8075
```

### Synergy Bonus
```
Synergy = Cal(I)_choquet - Cal(I)_linear
        = 0.8075 - 0.7025
        = 0.0750  (7.5 percentage points)
```

### Key Insights
1. **(@b, @chain) synergy contributes 0.0700**: Strong base implementation quality 
   enhances chain dependency quality. This interaction captures the principle that 
   well-implemented code propagates quality through its dependencies.

2. **(@chain, @q) synergy contributes 0.0350**: Good chain quality amplifies 
   question relevance. Methods with solid dependencies are better positioned to 
   address domain questions effectively.

3. **Total synergy bonus: +7.5%**: The method benefits significantly from 
   complementarity between layers, which a simple weighted average would miss.

4. **Bottleneck identification**: Both interactions are limited by @chain (0.70), 
   suggesting that improving chain quality would have multiplicative benefits 
   across the system.

## Comparison with Weighted Average

### Weighted Average (No Interactions)
```python
weighted_avg = (0.35 + 0.30 + 0.25 + 0.10 + 0.05)  # Redistribute interaction weights
             = 1.05  # Need to renormalize

# Renormalized weights
w_b = 0.35 / 1.05 = 0.3333
w_chain = 0.30 / 1.05 = 0.2857
w_q = 0.25 / 1.05 = 0.2381
w_interaction_redistributed = 0.15 / 1.05 = 0.1429

# Assuming equal redistribution
score_wa = 0.3333 * 0.80 + 0.2857 * 0.70 + 0.2381 * 0.85
         = 0.2666 + 0.2000 + 0.2024
         = 0.6690
```

### Choquet Integral (With Interactions)
```
score_choquet = 0.8075
```

### Difference
```
Δ = 0.8075 - 0.6690 = 0.1385 (+20.7%)
```

The Choquet integral captures **20.7% more value** by modeling synergies that 
weighted averages cannot represent. This demonstrates the power of interaction 
terms for multi-dimensional quality assessment.
