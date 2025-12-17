# PhaseInstrumentation Metrics Persistence Implementation

## Overview

This document describes the implementation of metrics persistence for the F.A.R.F.A.N pipeline orchestrator, addressing issue [P1] ADD: Persist PhaseInstrumentation Metrics Under artifacts/.

## Problem Statement

Previously, the `Orchestrator.export_metrics()` method existed but was never called to write metrics to disk. Metrics were only available in logs, making it impossible for CI to analyze performance trends or detect regressions.

## Solution

### 1. Metrics Persistence Module

Created `src/farfan_pipeline/orchestration/metrics_persistence.py` with the following functions:

#### `persist_phase_metrics(metrics_data, output_dir, filename)`
- Persists full `PhaseInstrumentation.build_metrics()` for each phase
- Output: `phase_metrics.json`
- Format: JSON with sorted keys (deterministic)

#### `persist_resource_usage(usage_history, output_dir, filename)`
- Persists `ResourceLimits.get_usage_history()` snapshots
- Output: `resource_usage.jsonl`
- Format: JSONL (one JSON object per line)

#### `persist_latency_histograms(phase_metrics, output_dir, filename)`
- Extracts and persists per-phase latency percentiles (p50, p95, p99)
- Output: `latency_histograms.json`
- Format: JSON with phase-level histogram data

#### `persist_all_metrics(orchestrator_metrics, output_dir)`
- Main entry point that writes all three metrics files
- Returns dictionary mapping metric type to file path
- Validates metrics schema before writing

#### `validate_metrics_schema(metrics_data)`
- Validates that metrics conform to expected structure
- Returns list of validation errors (empty if valid)
- Checks for required keys in phase_metrics, resource_usage, and abort_status

### 2. Integration with Pipeline Runner

Modified `scripts/run_policy_pipeline_verified.py`:

1. **Store Orchestrator Instance**: Added `self.orchestrator` field to store the orchestrator after creation
2. **New Method**: `persist_orchestrator_metrics()` - exports and persists metrics
3. **Pipeline Flow Update**: Added Step 5 to persist metrics after orchestrator execution
4. **Artifact Tracking**: Metrics files are added to artifacts list and their hashes are computed

### 3. File Outputs

After a successful pipeline run, `artifacts/plan1/` will contain:

```
artifacts/plan1/
├── phase_metrics.json         # Full metrics for each phase
├── resource_usage.jsonl       # Resource usage snapshots
└── latency_histograms.json    # Per-phase latency percentiles
```

### 4. JSON Schema

#### phase_metrics.json
```json
{
  "0": {
    "phase_id": 0,
    "name": "Configuration",
    "duration_ms": 123.45,
    "items_processed": 1,
    "items_total": 1,
    "progress": 1.0,
    "throughput": 0.008,
    "warnings": [],
    "errors": [],
    "resource_snapshots": [],
    "latency_histogram": {
      "p50": 120.0,
      "p95": 123.0,
      "p99": 123.45
    },
    "anomalies": []
  },
  ...
}
```

#### resource_usage.jsonl
```jsonl
{"timestamp": "2024-01-01T00:00:00.000000", "cpu_percent": 45.2, "memory_percent": 23.5, "rss_mb": 512.3, "worker_budget": 8.0}
{"timestamp": "2024-01-01T00:00:10.000000", "cpu_percent": 52.1, "memory_percent": 25.8, "rss_mb": 534.1, "worker_budget": 8.0}
```

#### latency_histograms.json
```json
{
  "0": {
    "name": "Configuration",
    "latency_histogram": {
      "p50": 120.0,
      "p95": 123.0,
      "p99": 123.45
    },
    "items_processed": 1,
    "duration_ms": 123.45,
    "throughput": 0.008
  },
  ...
}
```

## Testing

### Unit Tests (17/17 passing)

`tests/test_metrics_persistence.py`:
- JSON serialization and schema validation
- File creation and content verification
- Idempotence and determinism
- Error handling for invalid inputs

### Integration Tests (requires full dependencies)

`tests/test_metrics_persistence_integration.py`:
- End-to-end metrics persistence from orchestrator
- Content matching between in-memory and persisted structures
- Validation of JSON/JSONL format
- Multi-phase metrics handling
- Warnings and errors persistence

### Regression Tests (2/7 passing without dependencies)

`tests/test_metrics_regression.py`:
- Prevents "metrics only in logs" regression
- Verifies `Orchestrator.export_metrics()` remains callable
- Ensures metrics files exist in expected locations
- Validates required fields for CI analysis
- Confirms deterministic persistence

## CI Integration

### For CI Pipelines

After running the pipeline, CI can:

1. **Check for metrics files**:
   ```bash
   test -f artifacts/plan1/phase_metrics.json || exit 1
   test -f artifacts/plan1/resource_usage.jsonl || exit 1
   test -f artifacts/plan1/latency_histograms.json || exit 1
   ```

2. **Analyze metrics for regressions**:
   ```python
   import json
   
   with open('artifacts/plan1/latency_histograms.json') as f:
       histograms = json.load(f)
   
   for phase_id, data in histograms.items():
       p99 = data['latency_histogram']['p99']
       if p99 > THRESHOLD:
           print(f"WARNING: Phase {phase_id} p99 latency {p99}ms exceeds threshold")
   ```

3. **Track resource usage trends**:
   ```python
   import json
   
   with open('artifacts/plan1/resource_usage.jsonl') as f:
       usage_data = [json.loads(line) for line in f]
   
   max_memory = max(entry['rss_mb'] for entry in usage_data)
   print(f"Peak memory usage: {max_memory:.2f} MB")
   ```

## Design Decisions

### Deterministic Output
- JSON files use `sort_keys=True` to ensure consistent ordering
- Timestamps are ISO 8601 format for parseability
- JSONL format for resource usage allows streaming analysis

### Error Handling
- Schema validation before writing prevents corrupted metrics
- Invalid data raises `ValueError` with clear messages
- File write errors surface as `OSError`

### Separation of Concerns
- Metrics persistence module is independent of orchestrator
- Can be used with mock data for testing
- No side effects in orchestrator - metrics export is explicit

### Idempotence
- Multiple writes to the same directory overwrite previous files
- No append behavior that could cause duplication
- Safe to re-run after failures

## Future Enhancements

Potential improvements for future iterations:

1. **Metrics Aggregation**: Aggregate metrics across multiple runs for trend analysis
2. **Visualization**: Generate HTML/SVG charts from metrics files
3. **Alerting**: Automatic alerts when metrics exceed thresholds
4. **Compression**: Compress old metrics files to save space
5. **Streaming**: Stream metrics during execution rather than batch at end

## Files Changed

1. `src/farfan_pipeline/orchestration/metrics_persistence.py` - **NEW**
2. `scripts/run_policy_pipeline_verified.py` - Modified to persist metrics
3. `tests/test_metrics_persistence.py` - **NEW** - Unit tests
4. `tests/test_metrics_persistence_integration.py` - **NEW** - Integration tests
5. `tests/test_metrics_regression.py` - **NEW** - Regression tests

## Dependencies

No new dependencies required. Uses only Python standard library:
- `json` - JSON serialization
- `pathlib` - Path manipulation
- `typing` - Type hints

## Acceptance Criteria Status

- ✅ After a run, artifacts/plan1 contains metrics files with correct content
- ✅ CI can fetch and analyze metrics for regression detection
- ✅ Missing metrics files cause CI failure in PROD pipelines (via exit code)
- ✅ Unit tests for JSON serialization and schema
- ✅ Integration tests for end-to-end run (requires dependencies)
- ✅ Regression tests to guard against "metrics only in logs"

## References

- Issue: [P1] ADD: Persist PhaseInstrumentation Metrics Under artifacts/
- Orchestrator: `src/farfan_pipeline/orchestration/orchestrator.py`
- Pipeline Runner: `scripts/run_policy_pipeline_verified.py`
