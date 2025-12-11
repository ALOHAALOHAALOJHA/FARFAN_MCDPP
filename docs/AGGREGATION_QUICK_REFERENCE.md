# Aggregation Quick Reference Guide

## Overview

Quick reference for using enhanced aggregation system with contracts.

## Basic Usage

### 1. Dimension Aggregation (Phase 4)

```python
from canonic_phases.Phase_four_five_six_seven import DimensionAggregator

# Initialize
agg = DimensionAggregator(
    monolith=questionnaire_monolith,
    abort_on_insufficient=True,
    enable_sota_features=True
)

# Aggregate 5 micro questions → 1 dimension score
dimension_scores = agg.run(scored_micro_questions, config)
```

### 2. Area Aggregation (Phase 5)

```python
from canonic_phases.Phase_four_five_six_seven import AreaPolicyAggregator

# Initialize
agg = AreaPolicyAggregator(
    monolith=questionnaire_monolith,
    abort_on_insufficient=True
)

# Aggregate 6 dimensions → 1 area score
area_scores = agg.run(dimension_scores, config)
```

### 3. Cluster Aggregation (Phase 6)

```python
from canonic_phases.Phase_four_five_six_seven import ClusterAggregator

# Initialize
agg = ClusterAggregator(
    monolith=questionnaire_monolith,
    abort_on_insufficient=True
)

# Aggregate areas → cluster scores (4 MESO)
cluster_scores = agg.run(area_scores, config)
```

### 4. Macro Aggregation (Phase 7)

```python
from canonic_phases.Phase_four_five_six_seven import MacroAggregator

# Initialize
agg = MacroAggregator(
    monolith=questionnaire_monolith,
    abort_on_insufficient=True
)

# Aggregate 4 clusters → holistic evaluation
macro_score = agg.run(cluster_scores, config)
```

---

## Enhanced Usage with Contracts

### Confidence Interval Tracking

```python
from canonic_phases.Phase_four_five_six_seven import (
    DimensionAggregator,
    enhance_aggregator
)

# Create base aggregator
base_agg = DimensionAggregator(monolith=monolith)

# Enhance with confidence intervals
enhanced = enhance_aggregator(base_agg, "dimension", enable_contracts=True)

# Aggregate with CI
scores = [1.5, 2.0, 2.5, 2.0, 1.8]
weights = [0.2, 0.2, 0.2, 0.2, 0.2]

aggregated, ci = enhanced.aggregate_with_confidence(scores, weights, confidence_level=0.95)

print(f"Score: {aggregated:.2f}")
print(f"95% CI: [{ci.lower_bound:.2f}, {ci.upper_bound:.2f}]")
print(f"Method: {ci.method}")
```

### Enhanced Hermeticity Diagnosis

```python
from canonic_phases.Phase_four_five_six_seven import (
    AreaPolicyAggregator,
    enhance_aggregator
)

# Create base aggregator
base_agg = AreaPolicyAggregator(monolith=monolith)

# Enhance with diagnosis
enhanced = enhance_aggregator(base_agg, "area", enable_contracts=True)

# Diagnose hermeticity
actual_dims = {"DIM01", "DIM02", "DIM03", "DIM04"}  # Missing DIM05, DIM06
expected_dims = {"DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"}

diagnosis = enhanced.diagnose_hermeticity(actual_dims, expected_dims, "PA01")

if not diagnosis.is_hermetic:
    print(f"Severity: {diagnosis.severity}")
    print(f"Missing: {diagnosis.missing_ids}")
    print(f"Remediation: {diagnosis.remediation_hint}")
```

### Adaptive Penalty for Coherence

```python
from canonic_phases.Phase_four_five_six_seven import (
    ClusterAggregator,
    enhance_aggregator
)

# Create base aggregator
base_agg = ClusterAggregator(monolith=monolith)

# Enhance with adaptive penalty
enhanced = enhance_aggregator(base_agg, "cluster", enable_contracts=True)

# Compute dispersion metrics
scores = [2.0, 2.1, 2.0, 2.05]  # High convergence

metrics = enhanced.compute_dispersion_metrics(scores)

print(f"Scenario: {metrics.scenario}")  # "convergence"
print(f"CV: {metrics.coefficient_of_variation:.4f}")
print(f"Mean: {metrics.mean:.2f}")
print(f"Std Dev: {metrics.std_dev:.4f}")

# Get adaptive penalty
penalty = enhanced.adaptive_penalty(metrics)
print(f"Penalty: {penalty:.2f}")  # 0.15 for convergence (0.3 * 0.5)
```

### Strategic Alignment Metrics

```python
from canonic_phases.Phase_four_five_six_seven import (
    MacroAggregator,
    enhance_aggregator
)

# Create base aggregator
base_agg = MacroAggregator(monolith=monolith)

# Enhance with strategic alignment
enhanced = enhance_aggregator(base_agg, "macro", enable_contracts=True)

# Compute strategic alignment
alignment = enhanced.compute_strategic_alignment(
    cluster_scores=cluster_scores,
    area_scores=area_scores,
    dimension_scores=dimension_scores
)

print(f"PA×DIM Coverage: {len(alignment.pa_dim_coverage)}/60")
print(f"Coverage Rate: {alignment.coverage_rate*100:.1f}%")
print(f"Cluster Coherence: {alignment.cluster_coherence_mean:.3f} ± {alignment.cluster_coherence_std:.3f}")
print(f"Systemic Gaps: {alignment.systemic_gaps}")
print(f"Balance Score: {alignment.balance_score:.3f}")

# Identify weakest dimensions
for dim_id, score in alignment.weakest_dimensions:
    print(f"  {dim_id}: {score:.2f}")
```

---

## Direct Contract Usage

### Create and Use Contracts

```python
from cross_cutting_infrastrucuiture.contractual.dura_lex.aggregation_contract import (
    create_aggregation_contract
)

# Create contract
contract = create_aggregation_contract("dimension", abort_on_violation=False)

# Validate weight normalization
weights = [0.2, 0.2, 0.2, 0.2, 0.2]
is_valid = contract.validate_weight_normalization(weights)

if not is_valid:
    violations = contract.get_violations()
    for v in violations:
        print(f"[{v.severity}] {v.invariant_id}: {v.message}")

# Validate score bounds
score = 2.5
is_valid = contract.validate_score_bounds(score)

# Validate convexity
inputs = [1.0, 2.0, 3.0]
aggregated = 2.0
is_valid = contract.validate_convexity(aggregated, inputs)

# Check hermeticity
actual = {"Q1", "Q2", "Q3", "Q4", "Q5"}
expected = {"Q1", "Q2", "Q3", "Q4", "Q5"}
is_valid = contract.validate_hermeticity(actual, expected)
```

---

## Contract Invariants

| ID       | Invariant               | Formula                          | Severity | Levels       |
|----------|-------------------------|----------------------------------|----------|--------------|
| AGG-001  | Weight Normalization    | Σ(w) = 1.0 ± 1e-6                | CRITICAL | All          |
| AGG-002  | Score Bounds            | 0.0 ≤ score ≤ 3.0                | HIGH     | All          |
| AGG-003  | Coherence Bounds        | 0.0 ≤ coherence ≤ 1.0            | MEDIUM   | Cluster+     |
| AGG-004  | Hermeticity             | No gaps/overlaps/duplicates      | Variable | All          |
| AGG-006  | Convexity               | min(in) ≤ agg ≤ max(in)          | HIGH     | All          |

---

## Dispersion Scenarios

| Scenario          | CV Range    | Penalty Multiplier | Penalty Value |
|-------------------|-------------|--------------------|---------------|
| Convergence       | CV < 0.15   | 0.5×               | 0.15          |
| Moderate          | CV < 0.40   | 1.0×               | 0.30          |
| High Dispersion   | CV < 0.60   | 1.5×               | 0.45          |
| Extreme Dispersion| CV ≥ 0.60   | 2.0×               | 0.60          |

*Base penalty = 0.3*

---

## Common Patterns

### Pattern 1: Full Pipeline with Contracts

```python
from canonic_phases.Phase_four_five_six_seven import (
    DimensionAggregator,
    AreaPolicyAggregator,
    ClusterAggregator,
    MacroAggregator,
)
from cross_cutting_infrastrucuiture.contractual.dura_lex.aggregation_contract import (
    create_aggregation_contract
)

# Initialize all aggregators with contracts
dim_agg = DimensionAggregator(monolith=monolith, enable_sota_features=True)
area_agg = AreaPolicyAggregator(monolith=monolith)
cluster_agg = ClusterAggregator(monolith=monolith)
macro_agg = MacroAggregator(monolith=monolith)

# Create contracts for validation
contracts = {
    "dimension": create_aggregation_contract("dimension"),
    "area": create_aggregation_contract("area"),
    "cluster": create_aggregation_contract("cluster"),
    "macro": create_aggregation_contract("macro"),
}

# Run pipeline
dimension_scores = dim_agg.run(scored_micro, config)
area_scores = area_agg.run(dimension_scores, config)
cluster_scores = cluster_agg.run(area_scores, config)
macro_score = macro_agg.run(cluster_scores, config)
```

### Pattern 2: Enhanced Pipeline with Full Diagnostics

```python
from canonic_phases.Phase_four_five_six_seven import (
    DimensionAggregator,
    enhance_aggregator
)

# Initialize and enhance all levels
dim_base = DimensionAggregator(monolith=monolith)
dim_enhanced = enhance_aggregator(dim_base, "dimension")

area_base = AreaPolicyAggregator(monolith=monolith)
area_enhanced = enhance_aggregator(area_base, "area")

cluster_base = ClusterAggregator(monolith=monolith)
cluster_enhanced = enhance_aggregator(cluster_base, "cluster")

macro_base = MacroAggregator(monolith=monolith)
macro_enhanced = enhance_aggregator(macro_base, "macro")

# Use enhanced features throughout
# ... (see individual examples above)
```

---

## Error Handling

### Graceful Degradation

```python
# Set abort_on_violation=False for graceful handling
contract = create_aggregation_contract("dimension", abort_on_violation=False)

# Validate without aborting
is_valid = contract.validate_weight_normalization(invalid_weights)

if not is_valid:
    # Get violations
    violations = contract.get_violations()
    
    # Log or handle
    for v in violations:
        logger.warning(f"{v.contract_id}: {v.message}")
    
    # Clear for next validation
    contract.clear_violations()
```

### Strict Enforcement

```python
# Set abort_on_violation=True for strict mode
contract = create_aggregation_contract("area", abort_on_violation=True)

try:
    contract.validate_hermeticity(actual, expected)
except ValueError as e:
    # Handle validation failure
    logger.error(f"Hermeticity violation: {e}")
    # Abort or remediate
```

---

## Testing

### Unit Test Example

```python
import pytest
from canonic_phases.Phase_four_five_six_seven import enhance_aggregator
from unittest.mock import Mock

def test_confidence_interval_tracking():
    """Test confidence interval computation."""
    base_mock = Mock()
    base_mock.calculate_weighted_average = Mock(return_value=2.0)
    base_mock.bootstrap_aggregator = None
    
    enhanced = enhance_aggregator(base_mock, "dimension", enable_contracts=False)
    
    scores = [1.5, 2.0, 2.5]
    aggregated, ci = enhanced.aggregate_with_confidence(scores)
    
    assert aggregated == 2.0
    assert ci.lower_bound <= aggregated <= ci.upper_bound
    assert 0.0 <= ci.lower_bound <= 3.0
    assert 0.0 <= ci.upper_bound <= 3.0
```

---

## Performance Considerations

- **Contracts**: Minimal overhead (~1-2% for validation)
- **Confidence Intervals**: Bootstrap (1000 samples) adds ~100ms
- **Dispersion Metrics**: Negligible overhead (<1ms)
- **Strategic Alignment**: O(n) where n = number of dimensions

---

## See Also

- [AGGREGATION_WIRING_VERIFICATION.md](./AGGREGATION_WIRING_VERIFICATION.md) - Complete wiring verification
- [AUDIT_MATHEMATICAL_SCORING_MACRO.md](../AUDIT_MATHEMATICAL_SCORING_MACRO.md) - Mathematical audit (29/29 checks)
- [aggregation_contract.py](../src/cross_cutting_infrastrucuture/contractual/dura_lex/aggregation_contract.py) - Contract implementation
- [aggregation_enhancements.py](../src/canonic_phases/Phase_four_five_six_seven/aggregation_enhancements.py) - Enhancement implementation

---

**Version**: 1.0  
**Last Updated**: 2025-12-11
