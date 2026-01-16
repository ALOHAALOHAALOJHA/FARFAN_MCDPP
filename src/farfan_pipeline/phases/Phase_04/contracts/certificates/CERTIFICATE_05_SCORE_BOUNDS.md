# Certificate 05: Score Bounds [0.0, 3.0]

**Status:** ACTIVE  
**Timestamp:** 2025-12-18  
**Phase:** All Phases (4-7)  
**Requirement ID:** INV-P4-7-BOUNDS

## Requirement Specification

All aggregated scores across Phases 4-7 MUST be within the valid range **[0.0, 3.0]** representing the 3-point F.A.R.F.A.N evaluation scale.

**Mathematical Invariant:**
```
for all scores s in {dimension_scores, area_scores, cluster_scores, macro_score}:
    0.0 ≤ s.score ≤ 3.0
```

## Verification Method

**Test:** `tests/phase_4_7/test_counts_and_bounds.py::TestCountsAndBounds::test_score_bounds`

**Validation Functions:** All phase validation functions check score bounds

## Evidence

1. **Code Location:** `src/canonic_phases/phase_4_7_aggregation_pipeline/aggregation.py::AggregationSettings`
2. **Validation Enforcement:** Each phase validator checks score ranges
3. **Test Results:** Bounds tests verify scores in valid range, rejection of out-of-bounds

## Compliance Status

✅ **COMPLIANT** - All scores constrained to [0.0, 3.0] range.

---

**Signature:** Phase 4-7 Aggregation Pipeline v1.0.0
