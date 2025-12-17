# CQVR v2.0 Batch Evaluations - Documentation

## Overview

This document describes the CQVR (Contract Quality, Validation & Readiness) v2.0 evaluation system and batch evaluation process for executor contracts in the F.A.R.F.A.N pipeline.

## What is CQVR v2.0?

CQVR v2.0 is a comprehensive rubric-based evaluation system that assesses executor contracts across three tiers:

- **Tier 1: Critical Components** (55 pts) - Blocker issues that prevent execution
- **Tier 2: Functional Components** (30 pts) - Issues affecting quality but not execution
- **Tier 3: Quality Components** (15 pts) - Nice-to-have improvements for maintainability

**Total**: 100 points

## Batch Evaluations Completed

| Batch | Contracts | Status | Reports Location |
|-------|-----------|--------|------------------|
| Batch 1 | Q001-Q025 | ✅ Complete | N/A (manual evaluations) |
| Batch 2 | Q026-Q050 | ✅ Complete | N/A (manual evaluations) |
| **Batch 3** | **Q051-Q075** | ✅ **Complete** | `cqvr_reports/batch3_Q051_Q075/` |

## Batch 3 Results Summary

**Evaluation Date**: 2025-12-17  
**Script**: `evaluate_cqvr_batch3_Q051_Q075.py`

### Key Statistics

- **Total Contracts**: 25
- **Production Ready** (≥80 pts): 0 (0.0%)
- **Patchable** (60-79 pts): 0 (0.0%)
- **Requires Reformulation** (<60 pts): 25 (100.0%)
- **Average Score**: 61.3/100

### Critical Findings

**Universal Blocker**: All 25 contracts have `minimum_signal_threshold=0.0` with mandatory signals defined. This is a critical blocker that must be fixed before deployment.

**Required Fix**:
```json
// Before (BLOCKER):
"signal_requirements": {
  "mandatory_signals": [...],
  "minimum_signal_threshold": 0.0  // ❌ BLOCKER
}

// After (FIXED):
"signal_requirements": {
  "mandatory_signals": [...],
  "minimum_signal_threshold": 0.5  // ✅ FIXED
}
```

## CQVR v2.0 Rubric Components

### Tier 1: Critical Components (55 pts)

#### A1. Identity-Schema Coherence [20 pts]
Verifies that identity fields match exactly with const values in output_contract.schema.

**Checks**:
- `question_id` match (5 pts)
- `policy_area_id` match (5 pts)
- `dimension_id` match (5 pts)
- `question_global` match (3 pts)
- `base_slot` match (2 pts)

**Threshold**: ≥15/20 to be patchable

#### A2. Method-Assembly Alignment [20 pts]
Verifies that assembly_rules.sources only reference methods that exist in method_binding.methods[].provides.

**Checks**:
- 100% sources exist in provides (10 pts)
- ≥80% provides are used in sources (5 pts)
- method_count correct (3 pts)
- No invented namespaces (2 pts)

**Threshold**: ≥12/20 to be patchable

#### A3. Signal Integrity [10 pts] ⚠️ CRITICAL
Verifies signal configuration integrity.

**Checks**:
- threshold > 0 if mandatory_signals exist (5 pts) **BLOCKER**
- mandatory_signals well-formed (3 pts)
- aggregation method valid (2 pts)

**Threshold**: ≥5/10 (threshold MUST be > 0)

#### A4. Output Schema Validation [5 pts]
Verifies output schema completeness.

**Checks**:
- All required fields defined in properties (3 pts)
- Type consistency (2 pts)

**Threshold**: ≥3/5 to be patchable

### Tier 2: Functional Components (30 pts)

#### B1. Pattern Coverage [10 pts]
Verifies patterns cover expected_elements with valid metadata.

#### B2. Method Specificity [10 pts]
Verifies methodological documentation is specific (not boilerplate).

#### B3. Validation Rules [10 pts]
Verifies validation rules align with expected_elements.

### Tier 3: Quality Components (15 pts)

#### C1. Documentation Quality [5 pts]
Verifies epistemological foundation quality.

#### C2. Human-Readable Template [5 pts]
Verifies template correctness and placeholder usage.

#### C3. Metadata Completeness [5 pts]
Verifies metadata completeness (hashes, timestamps, versioning).

## Decision Matrix

| Condition | Decision | Action |
|-----------|----------|--------|
| Tier 1 < 35/55 | **REFORMULAR** | Regenerate from monolith |
| Tier 1 ≥ 35, Total < 60 | **REFORMULAR** | Regenerate broken components |
| Tier 1 ≥ 35, Total 60-79 | **PARCHEAR** | Apply targeted patches |
| Tier 1 ≥ 45, Total ≥ 80 | **PRODUCCIÓN** | Ready for deployment |

## How to Run Batch Evaluations

### Prerequisites

1. Python 3.12+
2. F.A.R.F.A.N repository cloned
3. Contracts exist in `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/`

### Run Batch 3 Evaluation

```bash
# From repository root
python3 evaluate_cqvr_batch3_Q051_Q075.py
```

This will:
1. Evaluate all 25 contracts (Q051-Q075)
2. Generate individual reports for each contract
3. Generate batch summary report
4. Save all reports to `cqvr_reports/batch3_Q051_Q075/`

### Create Evaluation for New Batch

To evaluate a new batch (e.g., Q076-Q100):

```python
# Copy evaluate_cqvr_batch3_Q051_Q075.py
# Modify the main() function:
evaluator.evaluate_batch(start=76, end=100)

# Update output directory:
output_dir = base_dir / "cqvr_reports" / "batch4_Q076_Q100"
```

## Report Structure

### Individual Contract Reports

Each contract gets a detailed markdown report with:

1. **Executive Summary**
   - Tier scores and percentages
   - Overall verdict (PRODUCCIÓN/PARCHEAR/REFORMULAR)
   - Decision rationale

2. **Tier Breakdowns**
   - Component-by-component scores
   - What each component checks

3. **Blockers Section**
   - Critical issues that must be fixed
   - Clear identification of blocking components

4. **Warnings Section**
   - Non-critical issues for improvement
   - Suggestions for optimization

5. **Recommendations Section**
   - Prioritized action items
   - Expected impact of fixes

6. **Decision Matrix**
   - Pass/fail criteria evaluation
   - Current values vs. thresholds

7. **Conclusion**
   - Summary assessment
   - Next steps
   - Production readiness status

### Batch Summary Report

The batch summary provides:

1. **Aggregate Statistics**
   - Distribution by decision type
   - Average scores per tier
   - Best/worst performing contracts

2. **Detailed Results Table**
   - All contracts with scores
   - Blocker and warning counts
   - Quick status overview

3. **Common Issues Analysis**
   - Most frequent blockers
   - Most frequent warnings
   - Patterns across the batch

4. **Recommendations**
   - Batch-level improvements
   - Systemic issues to address
   - Quality metrics

## Interpreting Results

### Production Ready (≥80 pts)
✅ Contract can be deployed immediately without corrections.

**Characteristics**:
- Tier 1 ≥ 45/55 (82%)
- Total ≥ 80/100
- No critical blockers
- All validation passes

**Example**: Target state after corrections

### Patchable (60-79 pts)
⚠️ Contract has issues but can be fixed with targeted patches.

**Characteristics**:
- Tier 1 ≥ 35/55 (64%)
- Total 60-79/100
- Few blockers (≤2)
- Structural integrity intact

**Action**: Apply recommended patches and re-evaluate

### Requires Reformulation (<60 pts)
❌ Contract has structural issues requiring regeneration.

**Characteristics**:
- Tier 1 < 35/55 OR Total < 60
- Multiple critical blockers
- Structural misalignment

**Action**: Regenerate from monolith using ContractGenerator

## Common Issues and Fixes

### Issue 1: Signal Threshold = 0.0 (A3)
**Frequency**: 100% of Batch 3  
**Severity**: BLOCKER

**Problem**: Allows zero-strength signals to pass validation

**Fix**:
```json
"minimum_signal_threshold": 0.5  // Changed from 0.0
```

**Impact**: +10 pts (0 → 10 in A3)

### Issue 2: Missing Source Hash (C3)
**Frequency**: 100% of Batch 3  
**Severity**: WARNING

**Problem**: Breaks provenance chain

**Fix**: Calculate SHA256 of questionnaire_monolith.json
```python
import hashlib, json

with open('questionnaire_monolith.json', 'rb') as f:
    source_hash = hashlib.sha256(f.read()).hexdigest()

# Update contract
contract['traceability']['source_hash'] = source_hash
```

**Impact**: +3 pts

### Issue 3: Boilerplate Documentation (B2)
**Frequency**: 100% of Batch 3  
**Severity**: WARNING

**Problem**: Generic methodological depth

**Fix**: Enhance with specific technical details per method class
- Replace "Execute X" with operational steps
- Add specific complexity analysis (O(n*p), not O(n))
- Document real assumptions (not "input is valid")

**Impact**: Variable, up to +10 pts

## Validation Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Contract Generation (from monolith)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. CQVR Evaluation (automated)                              │
│    - Run evaluate_cqvr_batchX_QXXX_QYYY.py                  │
│    - Generate reports                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Review Reports                                            │
│    - Check batch summary                                    │
│    - Identify blockers                                      │
│    - Prioritize fixes                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Apply Corrections                                         │
│    - Fix critical blockers (A3: signal threshold)           │
│    - Apply recommended patches                              │
│    - Enhance documentation (optional)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Re-evaluate (automated)                                   │
│    - Run CQVR again                                         │
│    - Verify improvements                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Deployment (if score ≥ 80)                               │
│    - Merge to main branch                                   │
│    - Deploy to pipeline                                     │
└─────────────────────────────────────────────────────────────┘
```

## Tools and Scripts

| Tool | Purpose | Location |
|------|---------|----------|
| **CQVRValidator** | Core validation logic | `src/farfan_pipeline/phases/Phase_two/contract_validator_cqvr.py` |
| **Batch 3 Evaluator** | Q051-Q075 evaluation | `evaluate_cqvr_batch3_Q051_Q075.py` |
| **Rubric Specification** | Full rubric details | `src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Rubrica_CQVR_v2.md` |
| **Example Reports** | High-quality examples | `Q001_CQVR_EVALUATION_REPORT.md`, `Q002_CQVR_EVALUATION_REPORT.md` |

## Best Practices

1. **Run CQVR early**: Evaluate contracts immediately after generation
2. **Fix blockers first**: Address Tier 1 critical issues before optimizing
3. **Batch corrections**: Apply same fix to all affected contracts simultaneously
4. **Re-evaluate after fixes**: Always verify improvements with fresh evaluation
5. **Document changes**: Track what was fixed and impact on scores

## References

- [CQVR v2.0 Rubric Full Specification](src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Rubrica_CQVR_v2.md)
- [Q001 Evaluation Report (83/100)](Q001_CQVR_EVALUATION_REPORT.md)
- [Q002 Evaluation Report (85/100)](Q002_CQVR_EVALUATION_REPORT.md)
- [Q007 Transformation Report](Q007_CQVR_TRANSFORMATION_REPORT.md)

## Support

For questions or issues with CQVR evaluations:
1. Review the rubric specification
2. Check example reports for patterns
3. Examine individual contract reports for specific issues
4. Consult the batch summary for systemic patterns

---

**Last Updated**: 2025-12-17  
**Version**: CQVR v2.0  
**Batch 3 Status**: ✅ Complete (25/25 contracts evaluated)
