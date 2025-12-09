# Choquet Aggregator Example 1: Basic Calculation

## Scenario
Aggregating three calibration layers without interaction terms.

## Configuration
```python
config = ChoquetConfig(
    linear_weights={
        "@b": 0.4,
        "@chain": 0.3,
        "@q": 0.3
    },
    interaction_weights={},
    normalize_weights=False,
    validate_boundedness=True
)
```

## Input Layer Scores
```python
layer_scores = {
    "@b": 0.85,      # Base layer (intrinsic quality)
    "@chain": 0.75,  # Chain layer (dependency quality)
    "@q": 0.90       # Question layer (domain relevance)
}
```

## Step-by-Step Computation

### Step 1: Compute Linear Sum
Formula: `linear_sum = Σ(aₗ·xₗ)`

Expand for each layer:
```
linear_sum = a[@b] · x[@b] + a[@chain] · x[@chain] + a[@q] · x[@q]
           = 0.4 · 0.85 + 0.3 · 0.75 + 0.3 · 0.90
           = 0.3400 + 0.2250 + 0.2700
           = 0.8350
```

Per-layer contributions:
- `@b`: 0.4 × 0.85 = 0.3400
- `@chain`: 0.3 × 0.75 = 0.2250
- `@q`: 0.3 × 0.90 = 0.2700

### Step 2: Compute Interaction Sum
Formula: `interaction_sum = Σ(aₗₖ·min(xₗ,xₖ))`

Since `interaction_weights = {}`, we have:
```
interaction_sum = 0
```

No interaction terms defined.

### Step 3: Compute Final Calibration Score
Formula: `Cal(I) = linear_sum + interaction_sum`

```
Cal(I) = 0.8350 + 0.0000
       = 0.8350
```

### Step 4: Validate Boundedness
Check: `0.0 ≤ Cal(I) ≤ 1.0`

```
0.0 ≤ 0.8350 ≤ 1.0  ✓
```

Boundedness constraint satisfied.

## Result Summary
```
Subject: "ExampleMethod"
Calibration Score: 0.8350
Linear Contribution: 0.8350
Interaction Contribution: 0.0000
Validation: PASSED
```

## Breakdown
```json
{
    "per_layer_contributions": {
        "@b": 0.3400,
        "@chain": 0.2250,
        "@q": 0.2700
    },
    "per_interaction_contributions": {},
    "per_layer_rationales": {
        "@b": "Layer @b: weight=0.4000 × score=0.8500 = 0.3400",
        "@chain": "Layer @chain: weight=0.3000 × score=0.7500 = 0.2250",
        "@q": "Layer @q: weight=0.3000 × score=0.9000 = 0.2700"
    }
}
```

## Interpretation
The method achieves a high calibration score of **0.835**, driven primarily by:
1. Strong base layer quality (0.85)
2. Excellent question relevance (0.90)
3. Solid chain dependencies (0.75)

The base layer has the highest impact (40% weight), contributing 0.34 to the final score.
