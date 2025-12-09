# Layer Versioning - Quick Reference

## One-Line Setup

```python
from calibration.layer_versioning import create_versioning_tools

registry, detector, analyzer, assessor, validator = create_versioning_tools("calibration/")
```

## Common Operations

### Load Layer Metadata

```python
from calibration.layer_versioning import LayerMetadataRegistry

registry = LayerMetadataRegistry("calibration/")
cohorts = registry.list_cohorts()
layers = registry.list_layers("COHORT_2024")
metadata = registry.get_layer_metadata("COHORT_2024", "@u")
```

### Detect Formula Changes

```python
detector = FormulaChangeDetector(registry)
changes = detector.detect_formula_changes("COHORT_2024", "COHORT_2025")
is_valid, violations = detector.validate_formula_evolution("COHORT_2024", "COHORT_2025")
```

### Analyze Weight Changes

```python
analyzer = WeightDiffAnalyzer(registry)
changes = analyzer.analyze_weight_changes("COHORT_2024", "COHORT_2025", "@u")
report = analyzer.generate_diff_report("COHORT_2024", "COHORT_2025", "@u")
```

### Assess Migration Impact

```python
assessor = MigrationImpactAssessor(registry, analyzer, detector)
impact = assessor.assess_migration_impact("COHORT_2024", "COHORT_2025")
report = assessor.generate_migration_report("COHORT_2024", "COHORT_2025")
```

### Validate Evolution

```python
validator = LayerEvolutionValidator(registry, detector, analyzer)
is_valid, violations = validator.validate_evolution("COHORT_2024", "COHORT_2025")
report = validator.generate_validation_report("COHORT_2024", "COHORT_2025")
```

## Thresholds

### Default

```python
DiffThresholds(
    weight_warning=0.05,
    weight_critical=0.10,
    score_drift_low=0.03,
    score_drift_moderate=0.08,
    score_drift_high=0.15
)
```

### Custom

```python
custom = DiffThresholds(weight_warning=0.03, weight_critical=0.08)
analyzer = WeightDiffAnalyzer(registry, custom)
```

## Risk Levels

| Level | Drift Range | Action Required |
|-------|-------------|-----------------|
| MINIMAL | < 0.03 | Standard testing |
| LOW | 0.03 - 0.08 | Smoke tests |
| MODERATE | 0.08 - 0.15 | Integration tests + recalibration |
| HIGH | ≥ 0.15 | Full regression + phased rollout |

## Formula Change Types

- `aggregation_method_change`: Switch between aggregation methods
- `component_count_change`: Add/remove formula components
- `gating_added`/`gating_removed`: Gate control changes
- `formula_modification`: General formula changes

## Governance Rules

1. **Formula changes REQUIRE new COHORT**
2. **Weight changes ≥0.05 require review**
3. **Weight changes ≥0.10 require governance approval**
4. **Layer removal requires deprecation cycle**

## TypedDict Quick Reference

```python
LayerMetadata: cohort_id, layer_symbol, formula, weights, components, ...
WeightChange: parameter, old_value, new_value, delta, exceeds_threshold
FormulaChange: layer_symbol, old_formula, new_formula, change_type, requires_new_cohort
MigrationImpact: from_cohort, to_cohort, affected_layers, risk_level, recommendations
```

## Comprehensive Audit (4-Step)

```python
tools = create_versioning_tools("calibration/")
registry, detector, analyzer, assessor, validator = tools

changes = detector.detect_formula_changes("COHORT_2024", "COHORT_2025")

for layer in registry.list_layers("COHORT_2024"):
    print(analyzer.generate_diff_report("COHORT_2024", "COHORT_2025", layer))

print(assessor.generate_migration_report("COHORT_2024", "COHORT_2025"))

print(validator.generate_validation_report("COHORT_2024", "COHORT_2025"))
```

## Examples File

See `layer_versioning_example.py` for 8 comprehensive examples.
