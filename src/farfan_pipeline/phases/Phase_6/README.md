# Phase 6: Cluster Aggregation (MESO)

## Document Control

| Attribute | Value |
|-----------|-------|
| **Phase ID** | `PHASE-6-CLUSTER-AGGREGATION` |
| **Canonical Name** | `phase_6_cluster_aggregation` |
| **Status** | `ACTIVE` |
| **Version** | `1.0.0` |
| **Pipeline Position** | Phase 5 (Area) → **Phase 6** → Phase 7 (Macro) |

---

## Phase Mission

**Phase 6** aggregates **10 AreaScore** outputs from Phase 5 into **4 ClusterScore** values (one for each MESO cluster).

### Input/Output Contract

| Aspect | Specification |
|--------|---------------|
| **Input** | 10 AreaScore (PA01 through PA10) |
| **Output** | 4 ClusterScore (CLUSTER_MESO_1 through CLUSTER_MESO_4) |
| **Invariant** | `len(output) == 4` |
| **Score Range** | [0.0, 3.0] (3-point scale) |

---

## Cluster Composition

| Cluster | Policy Areas | Count |
|---------|--------------|-------|
| CLUSTER_MESO_1 | PA01, PA02, PA03 | 3 |
| CLUSTER_MESO_2 | PA04, PA05, PA06 | 3 |
| CLUSTER_MESO_3 | PA07, PA08 | 2 |
| CLUSTER_MESO_4 | PA09, PA10 | 2 |

---

## Adaptive Penalty

Phase 6 applies an **adaptive penalty** based on score dispersion:

1. **Calculate dispersion metrics** (CV, DI, quartiles)
2. **Classify scenario**: convergence | moderate | high | extreme
3. **Apply penalty factor**: `adjusted_score = weighted_score × penalty_factor`
4. **Analyze coherence** and identify weakest area

### Dispersion Scenarios

| Scenario | CV Range | Penalty |
|----------|----------|---------|
| Convergence | CV < 0.2 | None (factor = 1.0) |
| Moderate | 0.2 ≤ CV < 0.4 | Light (factor = 0.95) |
| High | 0.4 ≤ CV < 0.6 | Medium (factor = 0.85) |
| Extreme | CV ≥ 0.6 | Heavy (factor = 0.70) |

---

## Coherence Analysis

Phase 6 computes:
- **Within-cluster coherence**: Consistency of area scores
- **Weakest area identification**: Lowest scoring area in cluster
- **Strategic gap detection**: Areas below threshold

---

## Related Files

- **Constants**: `PHASE_6_CONSTANTS.py`
- **Main Aggregator**: Located in Phase 4 (`aggregation.py::ClusterAggregator`)
- **Adaptive Scoring**: `adaptive_meso_scoring.py`
- **Validation**: `aggregation_validation.py::validate_phase6_output()`

---

## For More Information

See the [Phase 4-7 Aggregation Pipeline README](../Phase_4/README.md) for complete pipeline documentation.
