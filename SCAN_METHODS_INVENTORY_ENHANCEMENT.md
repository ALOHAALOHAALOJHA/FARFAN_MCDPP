# Scan Methods Inventory Enhancement

## Summary
Enhanced `scan_methods_inventory.py` with rule-based role/layer classification and D1Q1-D6Q5 executor detection.

## Changes Made

### 1. Role Classification Logic
Added enhanced `_classify_role()` method with keyword-based heuristics:

- **ingest**: parse, load, ingest, read_doc, extract_raw
- **processor**: process, transform, clean, normalize, aggregate
- **analyzer**: analyze, infer, calculate, compute, assess
- **extractor**: extract, identify, detect, find, locate
- **score**: score, grading, evaluate, rate, rank, measure
- **orchestrator**: orchestrate, pipeline, run_all, coordinate, execute_suite
- **executor**: execute with D[1-6]Q[1-5] pattern detection
- **core**: /core/ path detection or core in method name
- **utility**: fallback for all other methods

### 2. D1Q1-D6Q5 Executor Detection
- Added regex pattern: `r'D[1-6]_?Q[1-5]'` (case-insensitive)
- Scans both canonical_name and class_name
- Sets `is_executor=true` flag on matching methods
- Detects patterns like:
  - `D1Q1_Executor`, `D2_Q3_Analyzer`, `d3q5_method`
  - Valid dimensions: D1-D6
  - Valid questions: Q1-Q5

### 3. MethodMetadata Extension
Added new field:
```python
is_executor: bool = False
```

### 4. Statistics Enhancement
Added executor count to inventory statistics:
```python
"executor_count": sum(1 for m in methods if m.is_executor)
```

## Results
From scan of `src/farfan_pipeline/`:
- **Total methods**: 2,774
- **Executors detected**: 95 (with D1Q1-D6Q5 pattern)
- **Role distribution**:
  - utility: 1,044
  - core: 772
  - analyzer: 286
  - score: 166
  - extractor: 164
  - processor: 115
  - ingest: 107
  - executor: 95
  - orchestrator: 25

## Validation
- ✅ Syntax check passed
- ✅ Type checking (mypy) passed
- ✅ Linting (ruff + black) passed with minor complexity warnings
- ✅ Executor pattern detection validated
- ✅ All 9 roles properly mapped
- ✅ D1Q1-D6Q5 executors flagged correctly

## Output Format
Each method entry in `methods_inventory_raw.json` now includes:
```json
{
  "canonical_identifier": "core.orchestrator.executors.D1_Q1_QuantitativeBaselineExtractor.execute",
  "class_name": "D1_Q1_QuantitativeBaselineExtractor",
  "method_name": "execute",
  "role": "executor",
  "is_executor": true,
  ...
}
```

## Files Modified
- `scan_methods_inventory.py`: Enhanced classification logic
- `methods_inventory_raw.json`: Regenerated with new fields
