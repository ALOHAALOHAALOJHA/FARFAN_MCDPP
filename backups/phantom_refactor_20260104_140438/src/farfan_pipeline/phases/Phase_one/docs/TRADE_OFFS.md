# Phase 1 Design Trade-offs

**Document:** TRADE_OFFS.md  
**Version:** 1.0.0  
**Date:** 2026-01-04  
**Status:** ACTIVE

---

## 1. Memory-Bounded Extraction vs. Audit Accuracy

### Decision

After truncation occurs in `StreamingPDFExtractor. extract_with_limit()`, the code **continues iterating through all remaining pages** solely to count `total_length`.

### Trade-off Analysis

| Factor | Memory-First Approach | Audit-First Approach (Current) |
|--------|----------------------|-------------------------------|
| Memory Usage | O(limit) | O(limit) for text, O(n_pages) for iteration |
| Audit Accuracy | Estimated total | Exact total |
| Time Complexity | O(pages_to_limit) | O(all_pages) |
| Use Case Fit | Real-time streaming | Batch processing with audit requirements |

### Rationale

For the FARFAN pipeline's use case (batch processing of government policy PDFs with mandatory audit trails), **audit accuracy takes precedence** over early termination. The `TruncationAudit. loss_ratio` field is used downstream to: 
1. Flag documents that may have incomplete analysis
2. Trigger manual review workflows for high-loss documents
3. Provide evidence for reproducibility audits

### Alternative Considered

Sampling-based estimation:  After truncation, sample every Nth page and extrapolate.  Rejected because:
- Adds complexity with marginal benefit
- Typical PDFs (50-200 pages) complete iteration in milliseconds
- Estimation error could mislead downstream decisions

### Future Consideration

If processing PDFs >10M chars becomes common, consider:
```python
# Optional early termination for very large documents
if truncated and total_length > LARGE_DOC_THRESHOLD: 
    estimated_remaining = (total_length / pages_processed) * (total_pages - pages_processed)
    total_length += int(estimated_remaining)
    break
```

---

## 2. Magic Number `3.0` for Semantic Confidence Normalization

### Decision

Raw semantic scores are normalized by dividing by `SEMANTIC_SCORE_MAX_EXPECTED = 3.0`.

### Composition of Raw Score

| Component | Range | Source |
|-----------|-------|--------|
| Policy Area keywords | 0.0 - 1.0 | PA dictionary match |
| Dimension keywords | 0.0 - 1.0 | DIM dictionary match |
| Signal boost | 0.0 - 1.0 | Priority term weighting |
| **Total** | **0.0 - 3.0** | Sum |

### Rationale

- Scores above 3.0 are theoretically possible with edge-case stacking but rare
- Capping at 1.0 (`min(1.0, score / 3.0)`) prevents outlier distortion
- The normalized value represents "confidence relative to maximum expected match quality"

---

## 3. `subphase_results` Mixed Key Types

### Decision

`subphase_results` uses: 
- **Integer keys 0-15**:  Mandatory subphase outputs
- **String keys**:  Cross-cutting metadata (`'truncation_audit'`, `'irrigation_map'`, `'final_rankings'`)

### Rationale

- Subphase validation checks only integer keys 0-15
- String-keyed metadata is stored in separate serialization fields
- Avoids artificial nesting that would complicate access patterns
- No iteration assumes integer-only keys

---
