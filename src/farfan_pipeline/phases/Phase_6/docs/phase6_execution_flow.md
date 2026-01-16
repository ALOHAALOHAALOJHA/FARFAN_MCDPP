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

### Stage 3: Cluster Aggregation (stage=30) ✅ IMPLEMENTED

**File**: `phase6_30_00_cluster_aggregator.py`

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

## Hermeticity Model & Cluster Routing

### Design Decision: area_id-Based Routing

Phase 6 uses **static area_id membership** for cluster routing, NOT the `cluster_id` field on `AreaScore` objects.

#### Routing Logic (Actual)

```python
# From phase6_30_00_cluster_aggregator.py
def aggregate_cluster(self, cluster_id: str, area_scores: list[AreaScore]):
    expected_areas = CLUSTER_COMPOSITION[cluster_id]  # Static lookup
    cluster_areas = [
        area for area in area_scores
        if area.area_id in expected_areas  # Match by area_id
        # NOTE: area.cluster_id is NOT checked
    ]
```

#### Why This Matters

- **Single Source of Truth**: `CLUSTER_COMPOSITION` defines membership authoritatively.
- **Determinism**: Same `area_id` always routes to the same cluster.
- **Decoupling**: Phase 6 does not depend on Phase 5 setting `cluster_id`.
- **Debugging**: Membership is statically inspectable.

#### Implications

| Scenario                                        | Behavior                                |
|-------------------------------------------------|-----------------------------------------|
| AreaScore(area_id="PA01", cluster_id=None)      | Routes to CLUSTER_MESO_1 ✅             |
| AreaScore(area_id="PA01", cluster_id="..._1")   | Routes to CLUSTER_MESO_1 ✅             |
| AreaScore(area_id="PA01", cluster_id="..._2")   | Routes to CLUSTER_MESO_1 ✅ (ignored)   |
| AreaScore(area_id="PA99", cluster_id="..._1")   | Not routed (PA99 not in any cluster)    |

#### Input Contract Behavior

The input contract issues a **warning** (not an error) for missing `cluster_id`. Aggregation proceeds regardless.

#### Canonical Cluster Membership

| Cluster          | Policy Areas        | Count |
|------------------|---------------------|-------|
| CLUSTER_MESO_1   | PA01, PA02, PA03    | 3     |
| CLUSTER_MESO_2   | PA04, PA05, PA06    | 3     |
| CLUSTER_MESO_3   | PA07, PA08          | 2     |
| CLUSTER_MESO_4   | PA09, PA10          | 2     |

Defined in: `phase6_10_00_phase_6_constants.py` → `CLUSTER_COMPOSITION`

## Invariants Enforced

Throughout execution, Phase 6 maintains these invariants (see `contracts/phase6_mission_contract.py`):

1. **I1: Output Count** - Exactly 4 cluster scores produced
2. **I2: Cluster IDs** - All cluster IDs in {CLUSTER_MESO_1, CLUSTER_MESO_2, CLUSTER_MESO_3, CLUSTER_MESO_4}
3. **I3: Hermeticity** - Each cluster contains exactly its designated policy areas
4. **I4: Score Bounds** - All scores in [0.0, 3.0]
5. **I5: Coherence Bounds** - All coherence values in [0.0, 1.0]
6. **I6: Penalty Bounds** - All penalty values in [0.0, 1.0]

## Error Handling & Contract Enforcement

Phase 6 implements Design by Contract (DbC) with configurable enforcement:

### Contract Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| `strict` (default) | Raise `ValueError` on any contract violation | Production, CI/CD |
| `warn` | Log warnings but continue execution | Development, debugging |
| `disabled` | Skip contract validation entirely | Performance testing |

### Configuration

```python
from farfan_pipeline.phases.Phase_6 import ClusterAggregator

# Strict mode (default) - fail fast on contract violations
agg = ClusterAggregator(enforce_contracts=True, contract_mode="strict")

# Warn mode - log violations but continue
agg = ClusterAggregator(contract_mode="warn")

# Disabled - skip contract validation
agg = ClusterAggregator(contract_mode="disabled")
```

### Contract Invocation Points

- **Precondition (Phase6InputContract)**: invoked at start of `aggregate()`; validates 10 AreaScores, PA01–PA10 coverage, score bounds. Failure in strict mode raises `ValueError`.
- **Postcondition (Phase6OutputContract)**: invoked at end of `aggregate()`; validates 4 ClusterScores, cluster IDs, hermeticity. Failure in strict mode raises `ValueError`.

### Error Types

| Error | Cause | Resolution |
|-------|-------|-----------|
| `ValueError("Phase6InputContract failed")` | Missing areas, wrong count, out-of-bounds scores | Fix Phase 5 output |
| `ValueError("Phase6OutputContract failed")` | Wrong cluster count, hermeticity violation | Internal bug - report |
| `HermeticityError` (legacy) | Internal validation failure | Same as input contract failure |

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

**Current**:  FULLY IMPLEMENTED ✅
- ✅ Constants defined (`phase6_10_00_phase_6_constants.py`)
- ✅ Data models created (`phase6_10_00_cluster_score.py`)
- ✅ Adaptive penalty mechanism migrated (`phase6_20_00_adaptive_meso_scoring.py`)
- ✅ Contracts defined (`contracts/phase6_*.py`)
- ✅ Main aggregator implemented (`phase6_30_00_cluster_aggregator.py`, 390 lines)

**Verification:**
```bash
PYTHONPATH=src:$PYTHONPATH python3 -c "from farfan_pipeline.phases.Phase_6 import ClusterAggregator; print('✅ ClusterAggregator available')"
```

**Next Steps**:
1. Migrate tests from tests/phase_6/
2. Generate import DAG visualization
