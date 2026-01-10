# Phase 5: Policy Area Aggregation

## Document Control

| Attribute | Value |
|-----------|-------|
| **Phase ID** | `PHASE-5-POLICY-AREA-AGGREGATION` |
| **Canonical Name** | `phase_5_policy_area_aggregation` |
| **Status** | `ACTIVE` |
| **Version** | `1.0.0` |
| **Pipeline Position** | Phase 4 (Dimension) → **Phase 5** → Phase 6 (Cluster) |

---

## Phase Mission

**Phase 5** aggregates **60 DimensionScore** outputs from Phase 4 into **10 AreaScore** values (one for each policy area PA01-PA10).

### Input/Output Contract

| Aspect | Specification |
|--------|---------------|
| **Input** | 60 DimensionScore (6 dimensions × 10 policy areas) |
| **Output** | 10 AreaScore (PA01 through PA10) |
| **Invariant** | `len(output) == 10` |
| **Score Range** | [0.0, 3.0] (3-point scale) |

---

## Hermeticity Requirements

Each policy area MUST have exactly 6 dimensions:
- DIM01, DIM02, DIM03, DIM04, DIM05, DIM06

**Validation**: `HermeticityDiagnosis` checks for missing dimensions and applies graceful degradation if configured.

---

## Cluster Assignments

Policy areas are assigned to clusters for Phase 6:

| Cluster | Policy Areas |
|---------|--------------|
| CLUSTER_MESO_1 | PA01, PA02, PA03 |
| CLUSTER_MESO_2 | PA04, PA05, PA06 |
| CLUSTER_MESO_3 | PA07, PA08 |
| CLUSTER_MESO_4 | PA09, PA10 |

---

## Related Files

- **Constants**: `PHASE_5_CONSTANTS.py`
- **Main Aggregator**: Located in Phase 4 (`aggregation.py::AreaPolicyAggregator`)
- **Validation**: `aggregation_validation.py::validate_phase5_output()`

---

## For More Information

See the [Phase 4-7 Aggregation Pipeline README](../Phase_4/README.md) for complete pipeline documentation.
