# Choquet Aggregator Examples

This directory contains worked examples demonstrating the Choquet aggregator's
behavior across various scenarios, from basic calculations to edge cases.

## Overview

The Choquet integral is a non-linear aggregation operator that extends weighted
averages by incorporating interaction terms. It's particularly valuable for
multi-layer calibration systems where layers exhibit synergies or complementarities.

### Formula
```
Cal(I) = Σ(aₗ·xₗ) + Σ(aₗₖ·min(xₗ,xₖ))
         ︸━━━━━━━   ︸━━━━━━━━━━━━━━━
         Linear      Interaction
         Terms       Terms
```

Where:
- `xₗ`: Score for layer l ∈ [0,1]
- `aₗ`: Linear weight for layer l
- `aₗₖ`: Interaction weight for layer pair (l,k)
- `Cal(I)`: Calibration score ∈ [0,1]

## Examples

### [Example 1: Basic Calculation](example_1_basic_calculation.md)
**Focus**: Linear aggregation without interactions

- 3 layers: @b, @chain, @q
- No interaction terms
- Shows step-by-step computation
- Demonstrates per-layer contribution breakdown

**Key Learning**: How to compute the linear component and interpret layer contributions.

---

### [Example 2: With Interactions](example_2_with_interactions.md)
**Focus**: Full Choquet integral with synergy terms

- 3 layers with 2 interaction pairs
- Demonstrates min(xₗ,xₖ) computation
- Shows synergy bonus calculation
- Compares with weighted average baseline

**Key Learning**: How interactions capture complementarities between layers, and
why Choquet outperforms simple weighted averaging.

---

### [Example 3: Normalization](example_3_normalization.md)
**Focus**: Automatic weight normalization

- Unnormalized input weights
- Demonstrates linear weight normalization
- Shows interaction weight scaling
- Illustrates boundedness enforcement

**Key Learning**: Why normalization is critical for ensuring Cal(I) ∈ [0,1], and
how the aggregator automatically handles raw weights.

---

### [Example 4: Boundary Cases](example_4_boundary_cases.md)
**Focus**: Edge conditions and extreme inputs

Covers 7 scenarios:
1. All scores = 0 (worst case)
2. All scores = 1 (perfect case)
3. Single layer dominates
4. Extreme asymmetry in interactions
5. Exactly at upper bound
6. Negative scores (invalid input)
7. Empty interactions (weighted average)

**Key Learning**: How the aggregator behaves at boundaries, handles invalid inputs,
and degenerates to simpler forms in special cases.

---

## Quick Reference: Common Patterns

### Pattern 1: Simple Weighted Average
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.5, "@chain": 0.3, "@q": 0.2},
    interaction_weights={},  # No interactions
    normalize_weights=True
)
```
**Use Case**: You don't need interaction modeling, just want structured config.

### Pattern 2: Pairwise Synergies
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.4, "@chain": 0.3, "@q": 0.3},
    interaction_weights={
        ("@b", "@chain"): 0.1,  # Base-chain synergy
        ("@chain", "@q"): 0.05  # Chain-question synergy
    },
    normalize_weights=True
)
```
**Use Case**: Model specific complementarities between adjacent layers.

### Pattern 3: Dense Interactions
```python
layers = ["@b", "@chain", "@q", "@d"]
interaction_weight = 0.02

config = ChoquetConfig(
    linear_weights={l: 0.25 for l in layers},
    interaction_weights={
        (layers[i], layers[j]): interaction_weight
        for i in range(len(layers))
        for j in range(i+1, len(layers))
    },
    normalize_weights=True
)
```
**Use Case**: Capture systemic complementarity across all layer pairs.

### Pattern 4: Conservative (No Normalization)
```python
config = ChoquetConfig(
    linear_weights={"@b": 0.5, "@chain": 0.5},
    interaction_weights={},
    normalize_weights=False,  # Exact control
    validate_boundedness=True  # Strict validation
)
```
**Use Case**: You've pre-calculated optimal weights and want exact behavior.

---

## Mathematical Properties

### 1. Boundedness
**Property**: `0.0 ≤ Cal(I) ≤ 1.0` for all valid inputs

**Enforcement**:
- Weight normalization: `Σ(aₗ) = 1.0`
- Interaction constraint: `Σ(aₗₖ) ≤ 0.5 × Σ(aₗ)`
- Input clamping: `xₗ ∈ [0,1]`
- Output clamping: Final safety net

### 2. Monotonicity
**Property**: If `xₗ' ≥ xₗ` for all l, then `Cal(I)' ≥ Cal(I)`

**Proof Sketch**:
- Linear terms: `Σ(aₗ·xₗ')` ≥ `Σ(aₗ·xₗ)` since aₗ ≥ 0
- Interaction terms: `min(xₗ', xₖ')` ≥ `min(xₗ, xₖ)` (min is monotone)
- Therefore: `Cal(I)'` ≥ `Cal(I)`

### 3. Normalized Weights
**Property**: After normalization, `Σ(aₗ_normalized) = 1.0`

**Computation**:
```
aₗ_normalized = aₗ / Σ(aₗ)
```

### 4. Interaction Limit
**Property**: `min(xₗ, xₖ)` ≤ `min(xₗ, xₖ)` (tautology, but key constraint)

**Implication**: Interaction contribution is bounded by the weaker layer, ensuring
synergy doesn't artificially inflate scores beyond reasonable bounds.

---

## Usage Guidelines

### When to Use Choquet Aggregation

**✅ Use When**:
- Layers exhibit complementarity (e.g., good base + good chain > sum of parts)
- You need to model synergies between quality dimensions
- Linear weighted averaging is too simplistic
- You want interpretable interaction terms

**❌ Don't Use When**:
- Layers are truly independent (no interactions)
- You need extreme computational efficiency (Choquet is ~2x slower than WA)
- Configuration complexity isn't justified by modeling needs
- Simple weighted average suffices for your domain

### Configuration Best Practices

1. **Always enable normalization** unless you have specific reasons not to:
   ```python
   normalize_weights=True  # Default, safest
   ```

2. **Start with no interactions**, then add selectively:
   ```python
   interaction_weights={}  # Baseline
   ```
   
   Measure if interactions improve calibration accuracy before adding complexity.

3. **Use moderate interaction weights** (typically 0.05-0.15):
   ```python
   interaction_weights={("@b", "@chain"): 0.10}  # Reasonable
   ```
   
   Too large → risk of boundedness violations.
   Too small → minimal synergy capture.

4. **Validate boundedness in development**, disable in production:
   ```python
   validate_boundedness=True   # Dev/test
   validate_boundedness=False  # Prod (rely on clamping)
   ```

5. **Document your weights** with rationale:
   ```python
   # Weights based on expert consensus 2024-12-15
   linear_weights={
       "@b": 0.40,     # Base quality: foundational, highest weight
       "@chain": 0.30, # Chain quality: critical for propagation
       "@q": 0.30      # Question relevance: domain-specific
   }
   ```

---

## Troubleshooting

### Issue: Cal(I) always equals 1.0
**Diagnosis**: All input scores are 1.0, or weights don't sum correctly.

**Solution**: Check input layer_scores. If intentionally perfect, this is correct.

---

### Issue: CalibrationConfigError: Boundedness violation
**Diagnosis**: Weights don't satisfy boundedness constraint.

**Solution**: Enable normalization:
```python
config = ChoquetConfig(..., normalize_weights=True)
```

---

### Issue: Interaction terms contribute 0.0
**Diagnosis**: One layer in each pair has score ≈ 0.

**Solution**: This is correct behavior. Synergy requires both layers to be non-zero.
Check if zero scores are expected.

---

### Issue: Results differ from weighted average
**Diagnosis**: Interaction terms are contributing (expected behavior).

**Solution**: This is correct if interactions are defined. To verify:
```python
# Check breakdown
print(f"Linear: {result.breakdown.linear_contribution:.4f}")
print(f"Interaction: {result.breakdown.interaction_contribution:.4f}")
```

If interaction_contribution > 0, Choquet will differ from weighted average.

---

## References

### Academic
- Choquet, G. (1954). "Theory of capacities". Annales de l'institut Fourier, 5, 131-295.
- Grabisch, M. (1995). "Fuzzy integral in multicriteria decision making". Fuzzy Sets and Systems, 69(3), 279-298.
- Marichal, J.-L. (2000). "An axiomatic approach of the discrete Choquet integral as a tool to aggregate interacting criteria". IEEE Transactions on Fuzzy Systems, 8(6), 800-807.

### Related F.A.R.F.A.N Documentation
- `COHORT_2024_layer_assignment.py`: Layer definition and role requirements
- `COHORT_2024_fusion_weights.json`: Default weight configurations
- `calibration/mathematical_foundations_capax_system.md`: Theoretical foundations

### Code
- `choquet_aggregator.py`: Main implementation
- `choquet_tests.py`: Property-based test suite
- `aggregation.py`: Integration with existing aggregation pipeline

---

## Contributing

When adding new examples:

1. **Follow naming convention**: `example_N_description.md`
2. **Include sections**:
   - Scenario (what's being demonstrated)
   - Configuration (concrete code)
   - Step-by-step computation (show your work)
   - Interpretation (why it matters)
3. **Provide concrete numbers**: No hand-waving, actual calculations
4. **Link to related examples**: Build on previous concepts
5. **Add to this README**: Update table of contents

### Example Template
```markdown
# Choquet Aggregator Example N: Title

## Scenario
[What this example demonstrates]

## Configuration
```python
config = ChoquetConfig(...)
```

## Input Layer Scores
```python
layer_scores = {...}
```

## Step-by-Step Computation
[Detailed calculation with formulas]

## Result Summary
[Final score and key metrics]

## Interpretation
[What this means, lessons learned]
```

---

## License

These examples are part of the F.A.R.F.A.N project. See main repository LICENSE.
