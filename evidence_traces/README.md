# Evidence Traces Directory

This directory stores computational provenance traces for calibration system operations.

## Purpose

Evidence traces provide **auditable records** of calibration computations, enabling:
- Verification of mathematical correctness
- Debugging of unexpected scores
- Compliance with transparency requirements
- Reproducibility validation

## Directory Structure

```
evidence_traces/
├── base_layer/        # Base layer (@b) computation traces
├── chain_layer/       # Chain layer (@chain) validation traces
└── fusion/            # Choquet fusion aggregation traces
```

## Trace Format

Each trace file is a JSON document following this schema:

```json
{
  "method_id": "farfan_pipeline.core.executors.D1Q1_Executor",
  "layer": "@b",
  "timestamp": "2024-12-10T12:34:56Z",
  "input": {
    "b_theory": 0.85,
    "b_impl": 0.78,
    "b_deploy": 0.92
  },
  "computation_steps": [
    {
      "step": 1,
      "operation": "weighted_sum",
      "formula": "0.4 * b_theory",
      "value": 0.34
    },
    {
      "step": 2,
      "operation": "weighted_sum",
      "formula": "0.35 * b_impl",
      "value": 0.273
    },
    {
      "step": 3,
      "operation": "weighted_sum",
      "formula": "0.25 * b_deploy",
      "value": 0.23
    }
  ],
  "output": 0.843,
  "validation": {
    "bounds_check": "PASS",
    "expected_range": [0, 1]
  }
}
```

## Trace Generation

Traces are automatically generated during calibration when `trace_evidence=True`:

```python
from calibration.COHORT_2024_calibration_orchestrator import CalibrationOrchestrator

orchestrator = CalibrationOrchestrator()
result = orchestrator.calibrate(
    method_id="D1Q1_Executor",
    trace_evidence=True,  # Enable trace generation
    trace_output_dir="evidence_traces/"
)
```

## Trace Naming Convention

Traces follow this naming pattern:

```
{layer}/{method_id}_{timestamp}.json
```

Examples:
- `base_layer/D1Q1_Executor_20241210_123456.json`
- `fusion/pattern_extractor_v2_20241210_140523.json`

## Maintenance

### Retention Policy

- Keep traces for **30 days** by default
- Archive critical method traces permanently
- Rotate logs automatically via cleanup script

### Cleanup

Remove traces older than 30 days:

```bash
find evidence_traces/ -name "*.json" -mtime +30 -delete
```

## Gap Status

⚠️  **Current Status**: Evidence tracing infrastructure created but not yet integrated

**Next Steps** (from CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md GAP-1):
1. Implement trace logging in each layer evaluator
2. Add trace generation to CalibrationOrchestrator.calibrate()
3. Create validation script to verify trace completeness
4. Generate sample traces for all 30 D1Q1-D6Q5 executors

## References

- Gap analysis: `docs/CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md` (Section 5.1 GAP-1)
- Calibration orchestrator: `src/.../calibration/COHORT_2024_calibration_orchestrator.py`
