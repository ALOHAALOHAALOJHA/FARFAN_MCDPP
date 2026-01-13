# Phase 6 Execution Flow

## Document Control

| Attribute | Value |
|-----------|-------|
| **Document ID** | `PHASE6-EXEC-FLOW-2026-01-13` |
| **Version** | `1.0.0` |
| **Status** | `ACTIVE` |
| **Last Updated** | 2026-01-13 |

## Overview

Phase 6 implements the MESO-level cluster aggregation, transforming 10 Policy Area scores into 4 Cluster scores with adaptive penalty based on dispersion analysis.

**Compression Ratio**: 10:4 (2.5:1)

## Execution Sequence

### Stage 1: Constants & Configuration (stage=10)

**Files**:
- `phase6_10_00_phase_6_constants.py`
- `phase6_10_00_cluster_score.py`

**Actions**:
1. Load cluster composition definitions
2. Load dispersion thresholds
3. Load penalty weights
4. Define ClusterScore data model

**Output**: Configuration loaded, data models ready

### Stage 2: Adaptive Penalty Mechanism (stage=20)

**File**: `phase6_20_00_adaptive_meso_scoring.py`

**Actions**:
1. Analyze score distribution within each cluster
2. Compute dispersion metrics:
   - Coefficient of Variation (CV)
   - Dispersion Index (DI)
   - Variance
3. Classify dispersion scenario:
   - **Convergence** (CV < 0.2): Low penalty (0.5x)
   - **Moderate** (CV < 0.4): Normal penalty (1.0x)
   - **High** (CV < 0.6): Increased penalty (1.5x)
   - **Extreme** (CV ≥ 0.6): Strong penalty (2.0x)
4. Compute adaptive penalty factor
5. Apply non-linear scaling for extreme cases

**Output**: Penalty factors for each cluster

### Stage 3: Cluster Aggregation (stage=30) [TO BE IMPLEMENTED]

**File**: `phase6_30_00_cluster_aggregator.py` (pending)

**Actions**:
1. **Input Validation** (via `contracts/phase6_input_contract.py`):
   - Verify 10 AreaScore objects present
   - Verify all policy areas covered
   - Verify each area has 6 dimensions
   - Verify score bounds [0.0, 3.0]

2. **Grouping**:
   - Group AreaScores by cluster_id
   - CLUSTER_MESO_1: PA01, PA02, PA03
   - CLUSTER_MESO_2: PA04, PA05, PA06
   - CLUSTER_MESO_3: PA07, PA08
   - CLUSTER_MESO_4: PA09, PA10

3. **Per-Cluster Processing**:
   For each cluster:
   a. Extract area scores
   b. Compute weighted average (base score)
   c. Compute dispersion metrics (via adaptive_meso_scoring)
   d. Apply adaptive penalty:
      ```
      final_score = base_score * (1.0 - penalty_strength)
      ```
   e. Compute coherence metric
   f. Identify weakest area
   g. Create ClusterScore object

4. **Output Validation** (via `contracts/phase6_output_contract.py`):
   - Verify 4 ClusterScore objects produced
   - Verify cluster IDs correct
   - Verify hermeticity (correct policy areas per cluster)
   - Verify score bounds
   - Verify coherence computed
   - Generate Phase 7 compatibility certificate

**Output**: List of 4 ClusterScore objects

## Data Flow Diagram

```
Phase 5 Output (10 AreaScores)
    ↓
┌───────────────────────────────────────┐
│ Phase 6 Input Contract Validation    │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ Group by Cluster Assignment           │
│ - CLUSTER_MESO_1: 3 areas             │
│ - CLUSTER_MESO_2: 3 areas             │
│ - CLUSTER_MESO_3: 2 areas             │
│ - CLUSTER_MESO_4: 2 areas             │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ For Each Cluster:                     │
│   1. Compute base score (weighted avg)│
│   2. Analyze dispersion (CV, DI, var) │
│   3. Classify scenario (convergence   │
│      /moderate/high/extreme)          │
│   4. Apply adaptive penalty           │
│   5. Compute coherence                │
│   6. Create ClusterScore              │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ Phase 6 Output Contract Validation    │
└───────────────────────────────────────┘
    ↓
Phase 6 Output (4 ClusterScores) → Phase 7
```

## Invariants Enforced

Throughout execution, Phase 6 maintains these invariants (see `contracts/phase6_mission_contract.py`):

1. **I1: Output Count** - Exactly 4 cluster scores produced
2. **I2: Cluster IDs** - All cluster IDs in {CLUSTER_MESO_1, CLUSTER_MESO_2, CLUSTER_MESO_3, CLUSTER_MESO_4}
3. **I3: Hermeticity** - Each cluster contains exactly its designated policy areas
4. **I4: Score Bounds** - All scores in [0.0, 3.0]
5. **I5: Coherence Bounds** - All coherence values in [0.0, 1.0]
6. **I6: Penalty Bounds** - All penalty values in [0.0, 1.0]

## Error Handling

Phase 6 uses fail-fast validation:
- Input contract violations → raise ValueError immediately
- Missing policy areas → raise HermeticityError
- Score out of bounds → clamp and log warning
- Invalid cluster composition → raise ConfigurationError

## Provenance Tracking

Each ClusterScore includes:
- `provenance_node_id`: Unique identifier in global DAG
- `aggregation_method`: "weighted_average" or "choquet"
- `dispersion_scenario`: Classification of internal dispersion
- `penalty_applied`: Exact penalty value applied

## Performance Characteristics

- **Time Complexity**: O(n) where n = number of policy areas (10)
- **Space Complexity**: O(n) for storing area scores
- **Determinism**: 100% - same inputs always produce same outputs

## Dependencies

**Upstream** (Phase 5):
- Requires: 10 AreaScore objects
- Contract: `phase6_input_contract.py`

**Downstream** (Phase 7):
- Produces: 4 ClusterScore objects
- Contract: `phase6_output_contract.py`
- Compatibility certificate available

## Testing Strategy

1. **Unit Tests** (tests/):
   - Test dispersion classification
   - Test adaptive penalty calculation
   - Test cluster grouping logic

2. **Integration Tests** (tests/):
   - Test full Phase 6 execution with mock Phase 5 output
   - Test contract validation (input/output)
   - Test invariant enforcement

3. **Adversarial Tests** (tests/phase_6/):
   - Test extreme dispersion scenarios
   - Test boundary conditions (min/max scores)
   - Test malformed inputs

## Configuration

Phase 6 behavior is controlled by constants in `phase6_10_00_phase_6_constants.py`:

- `CLUSTER_COMPOSITION`: Policy area assignments
- `DISPERSION_THRESHOLDS`: CV cutoffs for scenario classification
- `PENALTY_WEIGHT`: Base penalty multiplier
- `COHERENCE_THRESHOLD_LOW/HIGH`: Coherence quality thresholds

No runtime configuration required - all parameters are compile-time constants.

## Status

**Current**: Partially implemented
- ✅ Constants defined
- ✅ Data models created
- ✅ Adaptive penalty mechanism migrated
- ✅ Contracts defined
- ⚠️  Main aggregator pending implementation

**Next Steps**:
1. Implement `phase6_30_00_cluster_aggregator.py`
2. Extract remaining logic from Phase 4 integration files
3. Migrate tests from tests/phase_6/
4. Generate import DAG visualization
