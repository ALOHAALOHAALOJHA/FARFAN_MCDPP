# FORCING_ROUTE.md — Phase 4-7 Aggregation Pipeline

## Document Control

| Attribute | Value |
|-----------|-------|
| **Document ID** | `FORCING-P4-7-2025-12-18` |
| **Status** | `ENFORCED` |
| **Enforcement** | MANDATORY |

---

## 1. Execution Constraints

### 1.1 Sequential Execution Order

**MUST execute in this order:**

```
Phase 4 (Dimension) → Phase 5 (Area) → Phase 6 (Cluster) → Phase 7 (Macro)
```

**Rationale:** Each phase depends on the output of the previous phase.

### 1.2 Input Cardinality Requirements

| Phase | Input Requirement | Failure Mode |
|-------|------------------|--------------|
| Phase 4 | Exactly 300 `ScoredMicroQuestion` | `ValueError` |
| Phase 5 | Exactly 60 `DimensionScore` | `AggregationValidationError` |
| Phase 6 | Exactly 10 `AreaScore` | `AggregationValidationError` |
| Phase 7 | Exactly 4 `ClusterScore` | `AggregationValidationError` |

### 1.3 Output Cardinality Guarantees

| Phase | Output Guarantee | Validation |
|-------|-----------------|------------|
| Phase 4 | `len(output) == 60` | `validate_phase4_output()` |
| Phase 5 | `len(output) == 10` | `validate_phase5_output()` |
| Phase 6 | `len(output) == 4` | `validate_phase6_output()` |
| Phase 7 | `output is not None` | `validate_phase7_output()` |

---

## 2. Abort Conditions

### 2.1 Hard Aborts

The pipeline **MUST abort** on:

1. **Empty input:** Any phase receiving empty list
2. **Hermeticity violation:** Missing dimensions/areas/clusters
3. **Traceability failure:** Output not traceable to source
4. **Score bounds violation:** Score outside [0.0, 3.0]
5. **Zero macro score:** With valid non-zero inputs

### 2.2 Soft Warnings

The pipeline **MAY continue** with warnings on:

1. **Non-hermetic areas:** Missing dimensions (logs warning, uses available)
2. **High dispersion:** CV > 0.6 (applies stronger penalty)
3. **Signal registry unavailable:** Falls back to monolith weights

---

## 3. Weight Normalization

### 3.1 Invariant

**All weight sets MUST sum to 1.0:**

```python
abs(sum(weights) - 1.0) < 1e-6
```

### 3.2 Enforcement

```python
# Auto-normalize if needed
if abs(weight_sum - 1.0) > tolerance:
    weights = [w / weight_sum for w in weights]
```

---

## 4. Score Bounds

### 4.1 Input Range

- Phase 3 output: `score ∈ [0.0, 1.0]`
- Aggregation internal: `score ∈ [0.0, 3.0]`

### 4.2 Clamping

```python
clamped_score = max(0.0, min(3.0, score))
```

---

## 5. Hermeticity Rules

### 5.1 Dimension Hermeticity (Phase 4 → 5)

Each policy area MUST have exactly 6 dimensions:
- DIM01, DIM02, DIM03, DIM04, DIM05, DIM06

### 5.2 Area Hermeticity (Phase 5 → 6)

Each cluster MUST have its defined policy areas:
- Cluster 1: PA01, PA02, PA03
- Cluster 2: PA04, PA05, PA06
- Cluster 3: PA07, PA08
- Cluster 4: PA09, PA10

### 5.3 Cluster Hermeticity (Phase 6 → 7)

Macro MUST receive exactly 4 clusters:
- CLUSTER_MESO_1, CLUSTER_MESO_2, CLUSTER_MESO_3, CLUSTER_MESO_4

---

## 6. Provenance Requirements

### 6.1 Mandatory Provenance

Every aggregation operation MUST:
1. Create `ProvenanceNode` for output
2. Add edges from all inputs to output
3. Record operation type and weights

### 6.2 Traceability

Every output score MUST be traceable to:
- Source micro-questions (for DimensionScore)
- Source dimensions (for AreaScore)
- Source areas (for ClusterScore)
- Source clusters (for MacroScore)

---

## 7. Signal Priority

### 7.1 Preference Order

```
1. SISAS Signal Registry (preferred)
2. Questionnaire Monolith (fallback)
3. Equal weights (emergency fallback)
```

### 7.2 Source Tracking

```python
settings.sisas_source ∈ {"sisas_registry", "legacy_monolith", "legacy_fallback"}
```

---

## 8. Validation Checkpoints

### 8.1 Required Validations

| Checkpoint | Function | Timing |
|------------|----------|--------|
| Post-Phase 4 | `validate_phase4_output()` | After dimension aggregation |
| Post-Phase 5 | `validate_phase5_output()` | After area aggregation |
| Post-Phase 6 | `validate_phase6_output()` | After cluster aggregation |
| Post-Phase 7 | `validate_phase7_output()` | After macro evaluation |
| Final | `validate_full_aggregation_pipeline()` | Before return |

### 8.2 Contract Enforcement

```python
enforce_validation_or_fail(validation_results, allow_failure=False)
```

---

## 9. Performance Constraints

### 9.1 Time Budget

| Phase | Max Duration | Timeout Action |
|-------|-------------|----------------|
| Phase 4 | 30s | Abort |
| Phase 5 | 10s | Abort |
| Phase 6 | 5s | Abort |
| Phase 7 | 5s | Abort |

### 9.2 Memory Budget

| Component | Max Memory |
|-----------|------------|
| Provenance DAG | 100MB |
| Bootstrap samples | 50MB |
| Total pipeline | 500MB |

---

## 10. Determinism Requirements

### 10.1 Fixed Seeds

```python
RANDOM_SEED = 42
bootstrap_aggregator = BootstrapAggregator(n_samples=1000, random_seed=42)
```

### 10.2 Reproducibility

Same inputs MUST produce identical outputs across runs.

---

## 11. Error Handling

### 11.1 Exception Hierarchy

```
AggregationError (base)
├── ValidationError
│   ├── WeightValidationError
│   ├── ThresholdValidationError
│   └── HermeticityValidationError
├── CoverageError
└── AggregationValidationError
```

### 11.2 Recovery Strategy

1. Log error with full context
2. Attempt graceful degradation (if allowed)
3. Raise to orchestrator (if abort required)

---

## 12. Monitoring Points

### 12.1 Metrics to Emit

| Metric | Type | Phase |
|--------|------|-------|
| `aggregation.phase4.count` | Counter | Phase 4 |
| `aggregation.phase5.count` | Counter | Phase 5 |
| `aggregation.phase6.count` | Counter | Phase 6 |
| `aggregation.phase7.count` | Counter | Phase 7 |
| `aggregation.validation.failures` | Counter | All |
| `aggregation.coherence` | Gauge | Phase 6-7 |
| `aggregation.duration_ms` | Histogram | All |

### 12.2 Log Levels

| Event | Level |
|-------|-------|
| Phase start | INFO |
| Phase complete | INFO |
| Hermeticity warning | WARNING |
| Validation failure | ERROR |
| Abort | CRITICAL |

---

## END OF FORCING_ROUTE.md
