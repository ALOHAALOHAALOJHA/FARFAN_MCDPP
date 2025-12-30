# Calibration Results Influence System

## Overview

This document describes the implementation of calibration results influence on execution and aggregation in the F.A.R.F.A.N pipeline. The system ensures that calibration scores demonstrably affect method selection, weighting, and aggregation outcomes.

## Design Principles

1. **Real Influence**: Calibration scores must have measurable impact on outputs
2. **No Fake Claims**: All logged calibration decisions must correspond to actual behavior changes
3. **Drift Detection**: System monitors calibration degradation over time
4. **Transparency**: Full diagnostic tracking and export capabilities

## Architecture

### 1. Calibration Policy System (`calibration_policy.py`)

The core policy engine that determines how calibration scores influence execution.

#### Quality Bands

| Band | Score Range | Weight Factor | Description |
|------|-------------|---------------|-------------|
| **EXCELLENT** | [0.8, 1.0] | 1.0 | Full weight, no downgrade |
| **GOOD** | [0.6, 0.8) | 0.9 | Minor downweight (10% reduction) |
| **ACCEPTABLE** | [0.4, 0.6) | 0.7 | Significant downweight (30% reduction) |
| **POOR** | [0.0, 0.4) | 0.4 | Major downweight (60% reduction) |

#### Execution Thresholds

- **Permissive Mode** (default): Execute all methods regardless of calibration
- **Strict Mode**: Reject methods below 0.3 calibration threshold

### 2. Integration Points

#### Phase 2: Execution (`base_executor_with_contract.py`)

Methods are evaluated for calibration before execution:

```python
if calibration_score < MIN_THRESHOLD and strict_mode:
    skip_method()  # Real skipping, not fake
else:
    weight = compute_adjusted_weight(base_weight, calibration_score)
    execute_with_weight(weight)  # Weight affects aggregation
```

**Key Changes:**
- Added `calibration_policy` parameter to executor initialization
- Calibration scores retrieved from `calibration_orchestrator`
- Policy consulted for execution decision
- Adjusted weights computed and stored
- Calibration metadata added to outputs

#### Orchestrator (`orchestrator.py`)

Orchestrator coordinates calibration policy across pipeline:

```python
calibration_policy = create_default_policy(strict_mode=runtime_config.is_strict_mode())
```

**Key Changes:**
- Added `calibration_policy` parameter to orchestrator
- Policy created based on runtime mode (strict/permissive)
- Policy passed to all executor instances
- Calibration metrics exported in orchestrator metrics

### 3. Calibration Metadata Flow

```
CalibrationOrchestrator.calibrate()
    ↓
    returns calibration_score (0.0-1.0)
    ↓
CalibrationPolicy.should_execute_method()
    ↓
    returns (bool, reason)
    ↓
CalibrationPolicy.compute_adjusted_weight()
    ↓
    returns CalibrationWeight{base, adjusted, factor, band}
    ↓
CalibrationPolicy.record_influence()
    ↓
    stores metrics for drift detection
    ↓
Executor output includes:
    - calibration_results: per-method scores
    - calibration_weights: per-method weight adjustments
    - calibration_summary: aggregate statistics
    ↓
Orchestrator.export_metrics()
    ↓
    includes calibration_metrics and calibration_detailed
```

## Verification Strategy

### Unit Tests (21 tests)

Located in `tests/test_calibration_policy.py`:

- Quality band classification
- Execution decisions (strict/permissive)
- Weight adjustments for all bands
- Method selection from alternatives
- Influence recording
- Drift detection (stable/unstable)
- Custom thresholds and factors

### Integration Tests (14 tests)

Located in `tests/test_calibration_integration.py`:

- **Execution Influence**: High/low/poor calibration impact
- **Aggregation Weights**: Weight scaling by score
- **Metrics Tracking**: Recording and retrieval
- **Drift Detection**: Stable and unstable scenarios
- **End-to-End Flow**: Complete calibration lifecycle
- **No Fake Claims**: Verified real weight differences
- **Regression Prevention**: Ensures influence never silently dropped

### Acceptance Criteria Validation

✅ **Low-calibration methods demonstrably change outputs**
- Weight factors: EXCELLENT=1.0, GOOD=0.9, ACCEPTABLE=0.7, POOR=0.4
- Strict mode blocks methods below 0.3 threshold
- All weight changes logged with reasons

✅ **Calibration drift over time detectable**
- `detect_drift()` method with configurable window and threshold
- Tracks mean, std, drift ratio
- Band distribution analysis

✅ **No fake calibration claims**
- All logged decisions correspond to actual weight adjustments
- Regression tests verify influence always applied
- Export includes detailed per-method tracking

## Usage Examples

### Basic Usage

```python
from canonic_phases.Phase_two.calibration_policy import create_default_policy

# Create policy (permissive mode)
policy = create_default_policy(strict_mode=False)

# Check if method should execute
should_execute, reason = policy.should_execute_method("MethodA", 0.85)
# Returns: (True, "Calibration 0.850 (EXCELLENT) - executing")

# Compute adjusted weight
weight = policy.compute_adjusted_weight(
    base_weight=1.0,
    calibration_score=0.65,
    method_id="MethodA"
)
# Returns: CalibrationWeight(
#     base_weight=1.0,
#     adjusted_weight=0.9,
#     adjustment_factor=0.9,
#     quality_band="GOOD"
# )

# Record influence for drift tracking
policy.record_influence(
    phase_id=2,
    method_id="MethodA",
    calibration_score=0.65,
    weight_adjustment=0.1,
    influenced_output=True
)
```

### Orchestrator Integration

```python
from orchestration.orchestrator import Orchestrator
from canonic_phases.Phase_two.calibration_policy import CalibrationPolicy

# Create strict policy
calibration_policy = CalibrationPolicy(strict_mode=True)

# Initialize orchestrator
orchestrator = Orchestrator(
    method_executor=executor,
    questionnaire=questionnaire,
    executor_config=config,
    calibration_orchestrator=cal_orch,
    calibration_policy=calibration_policy,  # Explicit policy
)

# Run pipeline
results = await orchestrator.process_development_plan_async(pdf_path)

# Get calibration summary
cal_summary = orchestrator.get_calibration_summary()
print(f"Influenced outputs: {cal_summary['influenced_outputs']}")
print(f"Drift detected: {cal_summary['drift_analysis']['drift_detected']}")
```

## Configuration Options

### CalibrationPolicy Constructor

```python
CalibrationPolicy(
    strict_mode: bool = False,
    custom_thresholds: dict[str, tuple[float, float]] | None = None,
    custom_factors: dict[str, float] | None = None,
)
```

**Parameters:**
- `strict_mode`: Reject methods below 0.3 threshold
- `custom_thresholds`: Override default quality band ranges
- `custom_factors`: Override default weight adjustment factors

### Example Custom Configuration

```python
# More aggressive downweighting
custom_factors = {
    "EXCELLENT": 1.0,
    "GOOD": 0.8,      # 20% reduction instead of 10%
    "ACCEPTABLE": 0.5, # 50% reduction instead of 30%
    "POOR": 0.2,       # 80% reduction instead of 60%
}

policy = CalibrationPolicy(
    strict_mode=True,
    custom_factors=custom_factors
)
```

## Monitoring and Diagnostics

### Drift Detection

```python
drift_analysis = policy.detect_drift(
    window_size=50,     # Analyze last 50 metrics
    threshold=0.15      # Alert if std > 15% of mean
)

if drift_analysis["drift_detected"]:
    print(f"Drift ratio: {drift_analysis['drift_ratio']:.3f}")
    print(f"Band distribution: {drift_analysis['band_distribution']}")
```

### Metrics Export

```python
# Get summary statistics
summary = policy.get_metrics_summary()
print(f"Total methods: {summary['total_metrics']}")
print(f"Mean calibration: {summary['mean_calibration_score']:.3f}")
print(f"Influence rate: {summary['influence_rate']:.1%}")

# Export detailed metrics for external analysis
detailed_metrics = policy.export_metrics()
# Returns: list of CalibrationMetrics dicts with full provenance
```

### Orchestrator Metrics

```python
# Export complete orchestrator metrics including calibration
metrics = orchestrator.export_metrics()

# Access calibration section
cal_metrics = metrics["calibration_metrics"]
print(f"Influenced outputs: {cal_metrics['influenced_outputs']}")
print(f"Mean score: {cal_metrics['mean_calibration_score']:.3f}")
print(f"Drift detected: {cal_metrics['drift_analysis']['drift_detected']}")

# Get detailed per-method tracking
cal_detailed = metrics["calibration_detailed"]
for metric in cal_detailed:
    print(f"{metric['method_id']}: {metric['calibration_score']:.3f} ({metric['quality_band']})")
```

## Future Enhancements

1. **Adaptive Thresholds**: Learn optimal thresholds from historical performance
2. **Multi-Criteria Weighting**: Combine calibration with other quality signals
3. **Temporal Smoothing**: Reduce sensitivity to transient calibration fluctuations
4. **Alert System**: Proactive notifications for drift detection
5. **Visualization**: Dashboards showing calibration trends over time

## References

- Issue: [P2] ADD: Make Calibration Results Influence Execution and Aggregation
- Implementation PR: copilot/add-calibration-results-influence
- Module: `src/farfan_pipeline/phases/Phase_two/calibration_policy.py`
- Tests: `tests/test_calibration_policy.py`, `tests/test_calibration_integration.py`
