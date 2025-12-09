# Layer Versioning and Comparison System

**Status**: ✅ Implementation Complete  
**COHORT**: COHORT_2024  
**Wave**: REFACTOR_WAVE_2024_12

## Overview

The Layer Versioning System provides comprehensive tooling for tracking, comparing, and validating layer formula changes across COHORT versions. It enables semantic diff generation, threshold violation detection, migration impact assessment, and governance rule enforcement for calibration layer evolution.

## Core Components

### 1. LayerMetadataRegistry

Central registry for layer metadata across COHORT versions.

**Purpose**: Load and manage layer metadata from COHORT files to enable version comparison and evolution tracking.

```python
from layer_versioning import LayerMetadataRegistry

registry = LayerMetadataRegistry("path/to/calibration/")

cohorts = registry.list_cohorts()
layers = registry.list_layers("COHORT_2024")
metadata = registry.get_layer_metadata("COHORT_2024", "@u")
```

**Features**:
- Automatic discovery of COHORT layer files
- Metadata extraction from `COHORT_METADATA` blocks
- Cross-version comparison support
- Weight and formula tracking

### 2. FormulaChangeDetector

Detects formula modifications requiring new COHORT version.

**Purpose**: Enforce governance rule: **formula changes REQUIRE new COHORT**.

```python
from layer_versioning import FormulaChangeDetector

detector = FormulaChangeDetector(registry)
changes = detector.detect_formula_changes("COHORT_2024", "COHORT_2025")

for change in changes:
    print(f"{change['layer_symbol']}: {change['change_type']}")
    print(f"Requires new COHORT: {change['requires_new_cohort']}")
```

**Change Classification**:
- `aggregation_method_change`: Switch between geometric_mean, weighted_sum, etc.
- `component_count_change`: Addition/removal of formula components
- `gating_added`/`gating_removed`: Gate control modifications
- `formula_modification`: General formula changes

**Validation Rules**:
- Formula changes within same COHORT → VIOLATION
- Aggregation method changes → Breaking change, requires deprecation
- Component structure changes → Requires new COHORT

### 3. WeightDiffAnalyzer

Analyzes weight changes with ±0.05 threshold violation detection.

**Purpose**: Highlight significant weight changes requiring review and approval.

```python
from layer_versioning import WeightDiffAnalyzer, DiffThresholds

thresholds = DiffThresholds(
    weight_warning=0.05,
    weight_critical=0.10
)

analyzer = WeightDiffAnalyzer(registry, thresholds)
changes = analyzer.analyze_weight_changes("COHORT_2024", "COHORT_2025", "@u")

for change in changes:
    if change["exceeds_threshold"]:
        print(f"⚠️  {change['parameter']}: Δ={change['delta']:+.4f}")
```

**Threshold Levels**:
- **Warning**: |Δ| ≥ 0.05 (default) - Requires review
- **Critical**: |Δ| ≥ 0.10 (default) - Requires governance approval

**Output Formats**:
- Structured `WeightChange` TypedDict
- Human-readable diff reports with threshold highlights
- Percentage change calculations

### 4. MigrationImpactAssessor

Estimates calibration score drift during COHORT upgrades.

**Purpose**: Assess migration impact and provide risk-based recommendations.

```python
from layer_versioning import MigrationImpactAssessor

assessor = MigrationImpactAssessor(registry, weight_analyzer, formula_detector)
impact = assessor.assess_migration_impact("COHORT_2024", "COHORT_2025")

print(f"Risk Level: {impact['risk_level']}")
print(f"Affected Layers: {impact['affected_layers']}")
print(f"Estimated Drift: {impact['estimated_score_drift']}")
```

**Risk Levels**:
- **MINIMAL**: Drift < 0.03 - Standard testing sufficient
- **LOW**: 0.03 ≤ Drift < 0.08 - Review and smoke tests
- **MODERATE**: 0.08 ≤ Drift < 0.15 - Recalibration and integration tests
- **HIGH**: Drift ≥ 0.15 - Full recalibration, regression tests, phased rollout

**Drift Estimation**:
- Formula changes: ±0.20 estimated drift (high impact)
- Weight threshold violations: drift = max_delta × 0.5
- Minor weight changes: drift = max_delta × 0.3

**Generated Recommendations**:
- Recalibration requirements
- Testing strategies (smoke, integration, regression)
- Deployment approaches (phased, canary)
- Documentation needs

### 5. LayerEvolutionValidator

Enforces governance rules for layer evolution.

**Purpose**: Validate that layer changes comply with calibration governance policies.

```python
from layer_versioning import LayerEvolutionValidator

validator = LayerEvolutionValidator(registry, formula_detector, weight_analyzer)
is_valid, violations = validator.validate_evolution("COHORT_2024", "COHORT_2025")

if not is_valid:
    for violation in violations:
        print(f"❌ {violation}")
```

**Enforced Rules**:
1. Formula changes require new COHORT version
2. Layer removal requires deprecation cycle
3. Critical weight changes (|Δ| ≥ 0.10) require governance approval
4. Breaking changes must be documented
5. Layer dependencies must remain valid

**Validation Reports**:
- Pass/fail status
- Detailed violation descriptions
- Governance compliance assessment

## Usage Patterns

### Basic Comparison

```python
from pathlib import Path
from layer_versioning import create_versioning_tools

calibration_dir = Path("path/to/calibration/")
registry, detector, analyzer, assessor, validator = create_versioning_tools(
    calibration_dir
)

from_cohort = "COHORT_2024"
to_cohort = "COHORT_2025"

print(detector.validate_formula_evolution(from_cohort, to_cohort))
print(analyzer.generate_diff_report(from_cohort, to_cohort, "@u"))
print(assessor.generate_migration_report(from_cohort, to_cohort))
print(validator.generate_validation_report(from_cohort, to_cohort))
```

### Comprehensive Audit Workflow

```python
print("[1/4] Formula Change Detection...")
formula_changes = detector.detect_formula_changes(from_cohort, to_cohort)

print("[2/4] Weight Diff Analysis...")
for layer in registry.list_layers(from_cohort):
    changes = analyzer.analyze_weight_changes(from_cohort, to_cohort, layer)
    print(analyzer.generate_diff_report(from_cohort, to_cohort, layer))

print("[3/4] Migration Impact Assessment...")
impact = assessor.assess_migration_impact(from_cohort, to_cohort)
print(assessor.generate_migration_report(from_cohort, to_cohort))

print("[4/4] Evolution Validation...")
is_valid, violations = validator.validate_evolution(from_cohort, to_cohort)
```

### Custom Thresholds

```python
from layer_versioning import DiffThresholds

custom_thresholds = DiffThresholds(
    weight_warning=0.03,
    weight_critical=0.08,
    score_drift_low=0.02,
    score_drift_moderate=0.05,
    score_drift_high=0.10
)

analyzer = WeightDiffAnalyzer(registry, custom_thresholds)
```

## TypedDict Contracts

### LayerMetadata

```python
class LayerMetadata(TypedDict):
    cohort_id: str
    layer_symbol: str
    layer_name: str
    formula: str
    weights: dict[str, float | dict[str, float]]
    components: dict[str, str]
    creation_date: str
    wave_version: str
    implementation_status: str
    lines_of_code: int | None
```

### WeightChange

```python
class WeightChange(TypedDict):
    parameter: str
    old_value: float
    new_value: float
    delta: float
    delta_pct: float
    exceeds_threshold: bool
```

### FormulaChange

```python
class FormulaChange(TypedDict):
    layer_symbol: str
    old_formula: str
    new_formula: str
    change_type: str
    requires_new_cohort: bool
```

### MigrationImpact

```python
class MigrationImpact(TypedDict):
    from_cohort: str
    to_cohort: str
    affected_layers: list[str]
    estimated_score_drift: dict[str, float]
    risk_level: str
    breaking_changes: list[str]
    recommendations: list[str]
```

## Governance Rules

### Formula Evolution

**Rule 1**: Formula changes REQUIRE new COHORT version.

**Rationale**: Formula changes alter score semantics and require recalibration.

**Enforcement**: `FormulaChangeDetector.validate_formula_evolution()`

**Example Violation**:
```
❌ Formula changes detected within same COHORT COHORT_2024.
   Formula changes REQUIRE new COHORT version.
```

### Weight Changes

**Rule 2**: Weight changes ≥0.05 require explicit review.

**Rationale**: Significant weight shifts impact calibration balance.

**Enforcement**: `WeightDiffAnalyzer` with threshold detection

**Example**:
```
⚠️  THRESHOLD VIOLATIONS (|Δ| ≥ 0.05):
  S.B_cov    0.5000 → 0.5500  (+0.0500, +10.0%)
```

**Rule 3**: Weight changes ≥0.10 require governance approval.

**Rationale**: Critical changes with high migration risk.

**Enforcement**: `LayerEvolutionValidator.validate_evolution()`

### Layer Lifecycle

**Rule 4**: Layer removal requires deprecation cycle.

**Rationale**: Breaking change requiring migration support.

**Enforcement**: `LayerEvolutionValidator` detects removed layers

**Example Violation**:
```
❌ Layer removal detected: {'@old_layer'}.
   Layers cannot be removed without deprecation cycle.
```

## Integration Points

### With COHORT Files

The system automatically discovers and parses:
- `COHORT_2024_unit_layer.py`
- `COHORT_2024_congruence_layer.py`
- `COHORT_2024_chain_layer.py`
- Future: `COHORT_2025_*.py`, `COHORT_2026_*.py`, etc.

**Required Structure** in COHORT files:
```python
COHORT_METADATA = {
    "cohort_id": "COHORT_2024",
    "layer_symbol": "@u",
    "layer_name": "Unit Layer",
    "formula": "U = geometric_mean(...) × (1 - penalty)",
    "weights": {
        "S": {"B_cov": 0.5, "H": 0.25, "O": 0.25},
        "M": {...}
    },
    "components": {
        "S": "Structural Compliance",
        "M": "Mandatory Sections"
    },
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12",
    "implementation_status": "complete",
    "lines_of_code": 490
}
```

### With Calibration Orchestrator

```python
from calibration.layer_versioning import create_versioning_tools
from calibration.COHORT_2024_calibration_orchestrator import CalibrationOrchestrator

tools = create_versioning_tools(Path("calibration/"))
registry, detector, analyzer, assessor, validator = tools

impact = assessor.assess_migration_impact("COHORT_2024", "COHORT_2025")

if impact["risk_level"] in ["HIGH", "MODERATE"]:
    print("⚠️  Migration requires recalibration")
    orchestrator = CalibrationOrchestrator()
```

## File Organization

```
calibration/
├── layer_versioning.py              # Core implementation
├── layer_versioning_example.py      # Usage examples
├── LAYER_VERSIONING_README.md       # This file
├── COHORT_2024_unit_layer.py        # Layer metadata source
├── COHORT_2024_congruence_layer.py  # Layer metadata source
├── COHORT_2024_chain_layer.py       # Layer metadata source
└── COHORT_2025_*.py                 # Future versions (when created)
```

## Testing Strategy

### Unit Tests

```python
def test_formula_change_detection():
    registry = LayerMetadataRegistry(calibration_dir)
    detector = FormulaChangeDetector(registry)
    changes = detector.detect_formula_changes("COHORT_2024", "COHORT_2025")
    assert all(c["requires_new_cohort"] for c in changes)

def test_weight_threshold_violation():
    analyzer = WeightDiffAnalyzer(registry)
    changes = analyzer.analyze_weight_changes("COHORT_2024", "COHORT_2025", "@u")
    violations = [c for c in changes if c["exceeds_threshold"]]
    assert all(abs(c["delta"]) >= 0.05 for c in violations)

def test_migration_risk_assessment():
    assessor = MigrationImpactAssessor(registry, analyzer, detector)
    impact = assessor.assess_migration_impact("COHORT_2024", "COHORT_2025")
    assert impact["risk_level"] in ["MINIMAL", "LOW", "MODERATE", "HIGH"]
```

### Integration Tests

```python
def test_comprehensive_audit():
    tools = create_versioning_tools(calibration_dir)
    registry, detector, analyzer, assessor, validator = tools
    
    is_valid, violations = validator.validate_evolution("COHORT_2024", "COHORT_2025")
    impact = assessor.assess_migration_impact("COHORT_2024", "COHORT_2025")
    
    if not is_valid:
        assert len(impact["breaking_changes"]) > 0
```

## Examples

See `layer_versioning_example.py` for comprehensive usage examples:

1. **Load Registry**: Discover and load COHORT metadata
2. **Detect Formula Changes**: Identify formula modifications
3. **Analyze Weight Changes**: Generate diff reports with threshold highlights
4. **Assess Migration Impact**: Estimate score drift and risk level
5. **Validate Evolution**: Enforce governance rules
6. **Custom Thresholds**: Configure sensitivity levels
7. **Cross-COHORT Comparison**: Compare metadata across versions
8. **Comprehensive Audit**: Full validation workflow

## Dependencies

- Python 3.12+
- No external dependencies (uses stdlib only)
- Integration with existing COHORT layer files

## Future Enhancements

1. **JSON Export**: Export comparison reports to structured JSON
2. **Visualization**: Generate diff visualizations for weight changes
3. **Automated Testing**: Integration with CI/CD for COHORT validation
4. **Historical Tracking**: Database of all COHORT transitions
5. **Regression Analysis**: Actual vs. estimated drift comparison
6. **Multi-Version Comparison**: Compare across 3+ COHORT versions
7. **Impact Simulation**: Monte Carlo simulation of score drift

## Authors

- Calibration Governance Team
- COHORT_2024 - REFACTOR_WAVE_2024_12

## License

Internal use only - F.A.R.F.A.N. Mechanistic Policy Pipeline
