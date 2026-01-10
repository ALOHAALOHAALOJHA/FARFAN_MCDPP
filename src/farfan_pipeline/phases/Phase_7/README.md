# Phase 7: Macro Evaluation

## Document Control

| Attribute | Value |
|-----------|-------|
| **Phase ID** | `PHASE-7-MACRO-EVALUATION` |
| **Canonical Name** | `phase_7_macro_evaluation` |
| **Status** | `ACTIVE` |
| **Version** | `1.0.0` |
| **Pipeline Position** | Phase 6 (Cluster) → **Phase 7** → Final Output |

---

## Phase Mission

**Phase 7** evaluates **4 ClusterScore** inputs from Phase 6 and produces a single **holistic MacroScore** representing the overall policy compliance assessment.

### Input/Output Contract

| Aspect | Specification |
|--------|---------------|
| **Input** | 4 ClusterScore (CLUSTER_MESO_1 through CLUSTER_MESO_4) |
| **Output** | 1 MacroScore (holistic evaluation) |
| **Invariant** | `output is not None` |
| **Score Range** | [0.0, 3.0] (3-point scale) |

---

## Macro Score Components

The MacroScore includes:

| Component | Description | Range |
|-----------|-------------|-------|
| **score** | Overall macro score | [0.0, 3.0] |
| **quality_level** | Quality classification | EXCELENTE \| BUENO \| ACEPTABLE \| INSUFICIENTE |
| **cross_cutting_coherence** | Cross-cluster coherence | [0.0, 1.0] |
| **systemic_gaps** | Identified policy gaps | List of area identifiers |
| **strategic_alignment** | Strategic alignment score | [0.0, 1.0] |
| **cluster_scores** | Detailed cluster breakdown | 4 cluster details |

---

## Quality Rubric

| Quality Level | Score Range (normalized) | Description |
|---------------|------------------------|-------------|
| **EXCELENTE** | ≥ 0.85 | Outstanding policy compliance |
| **BUENO** | ≥ 0.70 | Good compliance with minor gaps |
| **ACEPTABLE** | ≥ 0.55 | Acceptable with improvement areas |
| **INSUFICIENTE** | < 0.55 | Insufficient, requires intervention |

---

## Cross-Cutting Coherence

Phase 7 computes coherence across all clusters:

1. **Strategic coherence** (40%): Alignment with strategic objectives
2. **Operational coherence** (30%): Consistency in operational implementation
3. **Institutional coherence** (30%): Institutional capacity alignment

**Formula**: `coherence = 0.4×strategic + 0.3×operational + 0.3×institutional`

---

## Systemic Gaps

Systemic gaps are identified when:
- Policy area score < 0.55 (INSUFICIENTE threshold)
- Multiple areas in same cluster below threshold
- Cross-cluster misalignment detected

**Output**: List of area identifiers requiring intervention

---

## Strategic Alignment

Strategic alignment measures:
1. **Vertical alignment**: Local ↔ National policies
2. **Horizontal alignment**: Cross-policy consistency
3. **Temporal alignment**: Short-term ↔ Long-term planning

**Range**: [0.0, 1.0] where 1.0 = perfect alignment

---

## Related Files

- **Constants**: `PHASE_7_CONSTANTS.py`
- **Main Aggregator**: Located in Phase 4 (`aggregation.py::MacroAggregator`)
- **Validation**: `aggregation_validation.py::validate_phase7_output()`

---

## For More Information

See the [Phase 4-7 Aggregation Pipeline README](../Phase_4/README.md) for complete pipeline documentation.
