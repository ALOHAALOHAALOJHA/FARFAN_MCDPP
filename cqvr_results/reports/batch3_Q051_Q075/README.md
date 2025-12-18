# CQVR v2.0 Batch 3 Evaluation Results

## Overview

This directory contains the CQVR v2.0 evaluation results for Batch 3, covering contracts Q051 through Q075.

**Evaluation Date**: 2025-12-17  
**Total Contracts**: 25  
**Evaluator**: CQVR Batch 3 Automated Evaluator  
**Rubric**: CQVR v2.0 (100 points)

## Contents

- `BATCH3_Q051_Q075_CQVR_SUMMARY.md` - Aggregate summary report with statistics
- `Q051_CQVR_EVALUATION_REPORT.md` through `Q075_CQVR_EVALUATION_REPORT.md` - Individual contract evaluation reports (25 files)

## Evaluation Results Summary

| Metric | Value | Percentage |
|--------|-------|------------|
| **Production Ready** (≥80 pts) | 0/25 | 0.0% |
| **Patchable** (60-79 pts) | 0/25 | 0.0% |
| **Requires Reformulation** (<60 pts) | 25/25 | 100.0% |

### Score Statistics

| Tier | Average Score | Max | Percentage |
|------|---------------|-----|------------|
| **Tier 1: Critical** | 39.0/55 | 55 | 70.9% |
| **Tier 2: Functional** | 15.2/30 | 30 | 50.7% |
| **Tier 3: Quality** | 7.1/15 | 15 | 47.5% |
| **TOTAL** | 61.3/100 | 100 | 61.3% |

**Best Performing Contract**: Q061 (69/100)  
**Lowest Performing Contract**: Q051-Q075 except Q061 (61/100)

## Common Issues Identified

### Critical Blockers (100% of contracts)

**A3: Signal Threshold = 0.0**
- All 25 contracts have `minimum_signal_threshold=0.0` with `mandatory_signals` defined
- This allows zero-strength signals to pass validation, contradicting the "mandatory" concept
- **Fix Required**: Change `minimum_signal_threshold` from `0.0` to `0.5` in all contracts

### Common Warnings

1. **A2: Method-Assembly Usage** (100% of contracts) - Some methods not referenced in assembly rules
2. **A4: Source Hash Placeholder** (100% of contracts) - Traceability chain incomplete
3. **B2: Boilerplate Documentation** (100% of contracts) - Non-specific methodological depth
4. **C3: Missing Source Hash** (100% of contracts) - Provenance chain broken

## CQVR v2.0 Rubric

The evaluation uses the CQVR v2.0 rubric with 3 tiers:

### Tier 1: Critical Components (55 pts)
- **A1**: Identity-Schema Coherence (20 pts)
- **A2**: Method-Assembly Alignment (20 pts)
- **A3**: Signal Integrity (10 pts) ⚠️ **BLOCKER**
- **A4**: Output Schema Validation (5 pts)

### Tier 2: Functional Components (30 pts)
- **B1**: Pattern Coverage (10 pts)
- **B2**: Method Specificity (10 pts)
- **B3**: Validation Rules (10 pts)

### Tier 3: Quality Components (15 pts)
- **C1**: Documentation Quality (5 pts)
- **C2**: Human-Readable Template (5 pts)
- **C3**: Metadata Completeness (5 pts)

## Decision Matrix

| Tier 1 Score | Total Score | Decision |
|--------------|-------------|----------|
| < 35/55 (63%) | - | **REFORMULAR** |
| 35-44/55 | < 60 | **REFORMULAR** |
| 35-44/55 | 60-79 | **PARCHEAR** |
| ≥ 45/55 (82%) | ≥ 80 | **PRODUCCIÓN** |

## Next Steps

1. **Critical Fix Required**: Apply signal threshold correction to all 25 contracts
   ```json
   "minimum_signal_threshold": 0.5  // Changed from 0.0
   ```

2. **Optional Improvements**:
   - Calculate and add `source_hash` to traceability
   - Enhance methodological documentation to be more specific
   - Improve method usage in assembly rules

3. **Re-evaluation**: After corrections, re-run CQVR validation:
   ```bash
   python3 evaluate_cqvr_batch3_Q051_Q075.py
   ```

## How to Read Individual Reports

Each individual report contains:

1. **Executive Summary** - Overall scores and verdict
2. **Tier 1-3 Breakdown** - Detailed component scores
3. **Blockers** - Critical issues that must be fixed
4. **Warnings** - Non-critical issues for improvement
5. **Recommendations** - Specific actions to improve score
6. **Decision Matrix** - Pass/fail criteria evaluation
7. **Conclusion** - Summary and next steps

## Related Documentation

- `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Rubrica_CQVR_v2.md` - Full CQVR v2.0 rubric specification
- `Q001_CQVR_EVALUATION_REPORT.md` - Example of high-quality contract evaluation
- `Q002_CQVR_EVALUATION_REPORT.md` - Example of corrected contract evaluation

## Tool Information

**Script**: `evaluate_cqvr_batch3_Q051_Q075.py`  
**Validator**: `src/farfan_pipeline/phases/Phase_two/contract_validator_cqvr.py`  
**Version**: CQVR v2.0  
**Generated**: 2025-12-17T02:48:18.886376
