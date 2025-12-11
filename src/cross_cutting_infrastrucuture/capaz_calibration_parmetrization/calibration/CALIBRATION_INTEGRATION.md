# Calibration Integration Documentation

## Overview

The calibration system is now fully integrated into the executor execution flow. All D[1-6]Q[1-5] executors automatically calibrate methods before execution.

## Architecture

### Components

1. **CalibrationOrchestrator** (`calibration_orchestrator.py`)
   - Main orchestrator for method calibration
   - Loads intrinsic scores from JSON
   - Implements multi-layer scoring (currently base layer only)
   - Enforces 0.7 threshold with MethodBelowThresholdError gate

2. **CalibrationResult** (dataclass)
   - Contains final score, layer scores, timestamp
   - Includes breakdown of intrinsic scores (b_theory, b_impl, b_deploy)
   - Convertible to dict for serialization

3. **MethodBelowThresholdError** (exception)
   - Raised when method score < 0.7 (default threshold)
   - Contains method_id, score, and threshold
   - Halts execution to prevent low-quality method usage

4. **IntrinsicCalibrationLoader** (helper class)
   - Loads COHORT_2024_intrinsic_calibration.json
   - Caches JSON for performance
   - Filters excluded methods (calibration_status == "excluded")

### Integration Points

#### BaseExecutor (executors.py)

- **__init__**: Accepts `calibration_orchestrator` parameter
- **_execute_method**: Calls `calibrate()` before method execution
- **_log_calibration_trace**: Logs structured calibration breakdown
- **_inject_calibration_metadata**: Adds calibration results to execution output

#### BaseExecutorWithContract (base_executor_with_contract.py)

- **__init__**: Already accepted `calibration_orchestrator`
- **_execute_v2**: Calibrates each method in v2 contracts
- **_execute_v3**: Calibrates methods in both multi-method and single-method modes
- **result assembly**: Adds `calibration_metadata` to all executor outputs

## Execution Flow

```
1. Executor.execute() called with context
2. For each method:
   a. CalibrationOrchestrator.calibrate(method_id, context, evidence)
   b. Load intrinsic_score from JSON (base layer @b)
   c. Calculate final_score (currently = base_score)
   d. If score < 0.7: raise MethodBelowThresholdError
   e. Store CalibrationResult in executor.calibration_results
   f. Log structured calibration trace
   g. Execute method via MethodExecutor
3. Inject calibration metadata into final result
```

## Output Structure

All executor outputs now include:

```python
{
    "executor_id": "D1-Q1",
    "raw_evidence": {...},
    "metadata": {
        "calibration_results": {
            "Class.method": {
                "method_id": "Class.method",
                "final_score": 0.82,
                "layer_scores": {"@b": 0.82},
                "timestamp": "2024-12-15T10:30:00Z",
                "breakdown": {
                    "b_theory": 0.85,
                    "b_impl": 0.78,
                    "b_deploy": 0.80
                }
            }
        }
    },
    "execution_metrics": {
        "calibration_summary": {
            "total_methods": 15,
            "average_score": 0.78,
            "min_score": 0.72,
            "max_score": 0.89
        }
    }
}
```

## Logging

Calibration produces structured logs:

```
INFO [D1-Q1] Calibration: TextMiningEngine.diagnose_critical_links → 0.825 (layers: @b=0.825)
INFO [CALIBRATION_TRACE] TextMiningEngine.diagnose_critical_links: final=0.825, base=0.825
ERROR [D1-Q1] Method Class.method FAILED calibration threshold: score=0.650, threshold=0.700
```

## Configuration

### Default Threshold

The default threshold is **0.7** (70%). This can be configured:

```python
orchestrator = CalibrationOrchestrator(
    intrinsic_json_path="path/to/calibration.json",
    default_threshold=0.7,
    enable_threshold_gate=True
)
```

### Threshold Gate

The threshold gate can be disabled for testing:

```python
orchestrator = CalibrationOrchestrator(
    enable_threshold_gate=False  # Methods execute regardless of score
)
```

## Intrinsic Calibration JSON

Located at: `calibration/COHORT_2024_intrinsic_calibration.json`

Structure:
```json
{
  "methods": {
    "Module.Class.method": {
      "intrinsic_score": 0.825,
      "calibration_status": "computed",
      "breakdown": {
        "b_theory": 0.85,
        "b_impl": 0.78,
        "b_deploy": 0.80
      }
    }
  }
}
```

## Future Extensions

The architecture supports additional calibration layers:

- **@u**: Unit layer (PDT structure quality)
- **@q**: Question layer (question-specific context)
- **@d**: Dimension layer (dimension alignment)
- **@p**: Policy layer (policy context)
- **@C**: Congruence layer (method compatibility)
- **@chain**: Chain layer (input availability)
- **@m**: Meta layer (operational stability)

These will be integrated in future iterations with Choquet integral aggregation.

## Error Handling

### MethodBelowThresholdError

When a method fails calibration:
1. Error logged with score and threshold
2. ExecutorFailure raised with context
3. Execution halts to prevent cascade failures
4. Error includes method_id for debugging

### Missing Calibration Data

When method not in JSON:
1. Default score of 0.5 used
2. Warning logged
3. Execution continues (not a fatal error)

### Excluded Methods

Methods with `calibration_status: "excluded"`:
1. Return score of 0.0
2. Fail threshold if gate enabled
3. Should not be used in executors
