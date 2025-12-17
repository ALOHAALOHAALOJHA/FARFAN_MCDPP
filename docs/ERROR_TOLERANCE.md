# Error Tolerance and Partial Result Handling

## Overview

The F.A.R.F.A.N pipeline now supports controlled degradation instead of all-or-nothing failure. This enables the pipeline to complete with partial results while maintaining precise accounting of question-level failures.

## Key Features

### 1. Per-Phase Error Tracking

Phases 2 (Micro Questions) and 3 (Scoring) track:
- Total questions processed
- Successful question executions
- Failed question executions
- Current failure rate
- Threshold exceeded status

### 2. Configurable Failure Thresholds

Default threshold: **10% per phase**

The pipeline can tolerate up to 10% failures per phase while still producing valid results.

### 3. Runtime Mode-Aware Behavior

#### PRODUCTION / CI Mode
- **Strict enforcement**: Requires failure rate ≤ 10%
- Phase marked as failed if threshold exceeded
- Pipeline aborts on threshold breach

#### DEV / EXPLORATORY Mode
- **Lenient enforcement**: Allows partial success
- Requires at least 50% success rate
- Pipeline continues with partial results
- Useful for debugging and development

### 4. Transparent Error Reporting

Reports include:
- Error tolerance metrics per phase
- Current failure rates
- Success/failure classification
- Partial success indication (DEV mode)
- Runtime mode context

## Implementation Details

### ErrorTolerance Class

```python
@dataclass
class ErrorTolerance:
    phase_id: int
    max_failure_rate: float = 0.10
    total_questions: int = 0
    failed_questions: int = 0
    successful_questions: int = 0
    
    def record_success(self) -> None: ...
    def record_failure(self) -> None: ...
    def current_failure_rate(self) -> float: ...
    def threshold_exceeded(self) -> bool: ...
    def can_mark_success(self, runtime_mode: RuntimeMode | None) -> bool: ...
```

### Phase 2 Integration

Phase 2 execution now:
1. Initializes error tracker with total question count
2. Records success/failure for each question execution
3. Checks threshold after each failure
4. Aborts in PRODUCTION mode if threshold exceeded
5. Logs summary statistics on completion

### Phase 3 Integration

Phase 3 scoring now:
1. Initializes error tracker with total result count
2. Records success/failure for each scoring operation
3. Checks threshold after each failure
4. Aborts in PRODUCTION mode if threshold exceeded
5. Logs summary statistics on completion

### Manifest Generation

The `_assemble_report` method now includes:
- `error_tolerance`: Per-phase error metrics
- `pipeline_success`: Overall pipeline success flag
- `partial_success`: DEV mode partial success indicator
- `runtime_mode`: Current runtime mode

## Usage Examples

### Example 1: Production Pipeline with 5% Failures

```python
# 95 questions succeed, 5 fail
# Failure rate: 5% (within threshold)
# Result: Pipeline succeeds, all results valid
```

**Report Output:**
```json
{
  "pipeline_success": true,
  "error_tolerance": {
    "2": {
      "phase_id": 2,
      "current_failure_rate": 0.05,
      "threshold_exceeded": false,
      "successful_questions": 95,
      "failed_questions": 5
    }
  },
  "runtime_mode": "PRODUCTION"
}
```

### Example 2: Production Pipeline with 15% Failures

```python
# 85 questions succeed, 15 fail
# Failure rate: 15% (exceeds threshold)
# Result: Pipeline aborts, phase marked as failed
```

**Behavior:**
- Phase 2 logs error on threshold breach
- AbortRequested exception raised
- Subsequent phases do not execute
- Report marks phase as failed

### Example 3: DEV Pipeline with 60% Success

```python
# 60 questions succeed, 40 fail
# Failure rate: 40% (exceeds production threshold)
# Result: Pipeline continues, partial success marked
```

**Report Output:**
```json
{
  "pipeline_success": false,
  "partial_success": true,
  "error_tolerance": {
    "2": {
      "phase_id": 2,
      "current_failure_rate": 0.40,
      "threshold_exceeded": true,
      "successful_questions": 60,
      "failed_questions": 40
    }
  },
  "runtime_mode": "DEV"
}
```

## Configuration

### Setting Runtime Mode

```python
from canonic_phases.Phase_zero.runtime_config import RuntimeConfig, RuntimeMode

# Production mode (strict)
config = RuntimeConfig(mode=RuntimeMode.PRODUCTION)

# Development mode (lenient)
config = RuntimeConfig(mode=RuntimeMode.DEV)

# Exploratory mode (lenient)
config = RuntimeConfig(mode=RuntimeMode.EXPLORATORY)

# CI mode (strict)
config = RuntimeConfig(mode=RuntimeMode.CI)
```

### Adjusting Failure Threshold

The default 10% threshold can be adjusted:

```python
orchestrator._error_tolerance[2].max_failure_rate = 0.05  # 5% threshold
orchestrator._error_tolerance[3].max_failure_rate = 0.15  # 15% threshold
```

## Testing

### Unit Tests

Located in `tests/test_error_tolerance.py`:
- Threshold computation
- Success classification
- Runtime mode behavior
- Edge cases (zero questions, all failures, etc.)

Run with:
```bash
pytest tests/test_error_tolerance.py -v
```

### Integration Tests

Located in `tests/test_error_tolerance_integration.py`:
- Phase 2 error tolerance with mock executors
- Phase 3 error tolerance with mock scoring
- Manifest generation with error metrics
- Regression tests for silent failures

Run with:
```bash
pytest tests/test_error_tolerance_integration.py -v -m integration
```

## Monitoring and Debugging

### Log Messages

Error tolerance logs include:
- Per-question success/failure
- Cumulative failure rates
- Threshold breach warnings
- Phase completion summaries

Example log output:
```
Phase 2 completed: 92/100 questions succeeded, failure rate: 8.00%
```

### Error Tolerance Report

Access error tolerance state:
```python
error_report = orchestrator._error_tolerance[2].to_dict()
print(error_report)
```

Output:
```python
{
    'phase_id': 2,
    'max_failure_rate': 0.10,
    'total_questions': 100,
    'failed_questions': 8,
    'successful_questions': 92,
    'current_failure_rate': 0.08,
    'threshold_exceeded': False
}
```

## Migration Guide

### Existing Pipelines

No changes required for existing pipelines:
- Default behavior maintains 10% threshold
- PRODUCTION mode enforces strict compliance
- Existing error handling preserved

### New Pipelines

Recommended configuration:
1. Use RuntimeConfig to set appropriate mode
2. Monitor error tolerance metrics in reports
3. Adjust thresholds based on use case
4. Use DEV mode for initial development
5. Switch to PRODUCTION for production deployments

## Best Practices

1. **Use PRODUCTION mode for CI/CD**: Ensures failures are caught
2. **Use DEV mode for debugging**: Allows investigation of partial failures
3. **Monitor error tolerance metrics**: Track failure rates over time
4. **Investigate threshold breaches**: High failure rates indicate systemic issues
5. **Set appropriate thresholds**: Balance tolerance with quality requirements

## Limitations

1. **Phase-level tracking only**: Error tolerance applies to phases 2 and 3 only
2. **No question-specific thresholds**: All questions share the same threshold
3. **No adaptive thresholds**: Thresholds are static per execution
4. **Memory overhead**: Full result sets retained even with failures

## Future Enhancements

Potential improvements:
- Per-dimension error thresholds
- Adaptive threshold adjustment based on question difficulty
- Error pattern analysis and reporting
- Automatic retry logic for transient failures
- Error tolerance for additional phases
