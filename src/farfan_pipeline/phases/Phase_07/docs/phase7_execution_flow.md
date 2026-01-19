# Phase 7 Execution Flow

## Overview

Phase 7 implements the final aggregation tier of the F.A.R.F.A.N pipeline, synthesizing 4 MESO-level cluster scores into a single holistic MacroScore.

## Topological Order

```
1. phase7_10_00_phase_7_constants.py
   ↓
2. phase7_10_00_macro_score.py (depends on constants)
   ↓
3. phase7_10_00_systemic_gap_detector.py (depends on constants)
   ↓
4. phase7_20_00_macro_aggregator.py (depends on all above)
   ↓
5. __init__.py (exports public API)
```

## Module Responsibilities

### 1. Constants Module (`phase7_10_00_phase_7_constants.py`)
- **Position**: Foundation (no dependencies)
- **Purpose**: Defines all constants, enumerations, and invariants
- **Exports**:
  - `CLUSTER_WEIGHTS`: Equal weights for 4 clusters (0.25 each)
  - `QUALITY_THRESHOLDS`: Classification thresholds
  - `COHERENCE_WEIGHTS`: Strategic/Operational/Institutional weights
  - `MacroInvariants`, `QualityLevel` classes

### 2. MacroScore Data Model (`phase7_10_00_macro_score.py`)
- **Position**: Layer 2 (depends on constants)
- **Purpose**: Defines output data structure
- **Dependencies**: Constants module
- **Exports**: `MacroScore` dataclass
- **Invariants**:
  - Score ∈ [0.0, 3.0]
  - Coherence ∈ [0.0, 1.0]
  - Alignment ∈ [0.0, 1.0]
  - Valid quality levels only

### 3. Systemic Gap Detector (`phase7_10_00_systemic_gap_detector.py`)
- **Position**: Layer 2 (depends on constants)
- **Purpose**: Identifies policy areas with systemic gaps
- **Dependencies**: Constants module
- **Exports**: `SystemicGapDetector`, `SystemicGap` classes
- **Logic**:
  - Detects areas with scores < 1.65 (55% threshold)
  - Classifies severity: CRITICAL, SEVERE, MODERATE
  - Cross-cluster pattern analysis

### 4. Macro Aggregator (`phase7_20_00_macro_aggregator.py`)
- **Position**: Layer 3 (depends on all above)
- **Purpose**: Main aggregation logic
- **Dependencies**:
  - Constants
  - MacroScore
  - SystemicGapDetector
  - ClusterScore (from Phase 6)
- **Exports**: `MacroAggregator` class
- **Algorithm**:
  1. Validate input (4 ClusterScore objects)
  2. Compute weighted average
  3. Calculate cross-cutting coherence (CCCA)
  4. Detect systemic gaps (SGD)
  5. Compute strategic alignment (SAS)
  6. Propagate uncertainty
  7. Classify quality level
  8. Assemble MacroScore output

### 5. Package Façade (`__init__.py`)
- **Position**: Public API layer
- **Purpose**: Exports public interface
- **Exports**: All public classes and constants

## Execution Sequence

### Input Contract
```
PRE-7.1: len(cluster_scores) == 4
PRE-7.2: All CLUSTER_MESO_1..4 present
PRE-7.3: All scores ∈ [0.0, 3.0]
PRE-7.4: Valid provenance from Phase 6
PRE-7.5: No duplicate clusters
PRE-7.6: Coherence and dispersion metrics present
```

### Processing Steps

#### Step 1: Weighted Averaging
```python
macro_score = Σ(weight[cluster_i] × score[cluster_i])
# Equal weights: 0.25 each
```

#### Step 2: Cross-Cutting Coherence Analysis (CCCA)
```python
strategic = 1.0 - variance(scores) / max_variance
operational = mean(pairwise_similarities)
institutional = min(cluster_coherences)
coherence = 0.4×strategic + 0.3×operational + 0.3×institutional
```

#### Step 3: Systemic Gap Detection (SGD)
```python
for cluster in clusters:
    if cluster.score < threshold:
        detect_gaps(cluster)
        classify_severity(cluster)
```

#### Step 4: Strategic Alignment Scoring (SAS)
```python
vertical = alignment(MESO_1, MESO_2)      # Legal ↔ Implementation
horizontal = mean_pairwise_alignment()     # Cross-cluster
temporal = alignment(MESO_3, MESO_4)       # Monitoring ↔ Planning
alignment = (vertical + horizontal + temporal) / 3
```

#### Step 5: Quality Classification
```python
if normalized_score >= 0.85: EXCELENTE
elif normalized_score >= 0.70: BUENO
elif normalized_score >= 0.55: ACEPTABLE
else: INSUFICIENTE
```

#### Step 6: Uncertainty Propagation
```python
variance = Σ(weight²[i] × std²[i])
std = sqrt(variance)
CI_95 = [score - 1.96×std, score + 1.96×std]
```

### Output Contract
```
POST-7.1: Output is valid MacroScore
POST-7.2: score ∈ [0.0, 3.0]
POST-7.3: Valid quality_level
POST-7.4: coherence ∈ [0.0, 1.0]
POST-7.5: alignment ∈ [0.0, 1.0]
POST-7.6: Provenance references all 4 input clusters
POST-7.7: Valid area identifiers in systemic_gaps
```

## Contract Validation

### Input Validation
Implemented in: `contracts/phase7_input_contract.py`
- Function: `validate_phase7_input(cluster_scores)`
- Raises: `ValueError` on violation

### Mission Validation
Implemented in: `contracts/phase7_mission_contract.py`
- Validates: Weight normalization, invariants
- Runs: On module import

### Output Validation
Implemented in: `contracts/phase7_output_contract.py`
- Function: `validate_phase7_output(macro_score, input_cluster_ids)`
- Raises: `ValueError` on violation

## Integration Points

### Upstream (Phase 6)
```python
from farfan_pipeline.phases.Phase_06 import ClusterScore

# Phase 6 produces 4 ClusterScore objects
cluster_scores: list[ClusterScore] = phase6_output
```

### Downstream (Phase 8)
```python
from farfan_pipeline.phases.Phase_07 import MacroScore

# Phase 7 produces 1 MacroScore object
macro_score: MacroScore = phase7_output
# Phase 8 consumes this for recommendations
```

## Error Handling

### Precondition Violations
- Input count ≠ 4 → `ValueError`
- Missing clusters → `ValueError`
- Score out of bounds → `ValueError`

### Invariant Violations
- Weight sum ≠ 1.0 → Auto-normalize with warning
- Invalid quality level → `ValueError`
- Coherence/alignment out of bounds → Clamp with warning

## Performance Characteristics

- **Time Complexity**: O(n) where n = 10 (total policy areas)
- **Space Complexity**: O(n) for provenance tracking
- **Execution Time**: ~5-10ms typical
- **Memory Overhead**: ~5MB

## Determinism Guarantee

Phase 7 is fully deterministic:
- No random number generation
- No external API calls
- No file I/O during execution
- Fixed-weight aggregation
- Deterministic float operations

**Same inputs → Same outputs (bit-for-bit identical)**

## Provenance Tracking

Every MacroScore includes:
- `evaluation_id`: Unique identifier
- `provenance_node_id`: DAG node reference
- `cluster_scores`: Full input history
- `evaluation_timestamp`: UTC timestamp
- `pipeline_version`: Version used

## Testing Strategy

### Unit Tests
- Test each module independently
- Mock dependencies
- Validate invariants

### Integration Tests
- Test Phase 6 → Phase 7 flow
- Validate contracts
- Test error handling

### Property Tests
- Convexity: min(inputs) ≤ output ≤ max(inputs)
- Monotonicity: Higher inputs → Higher output
- Idempotence: Identical inputs → output = input
- Boundedness: Output always in [0, 3]

## Documentation Generated
- This file: `phase7_execution_flow.md`
- Import DAG: `phase7_import_dag.png` (to be generated)
- Anomalies: `phase7_anomalies.md` (to be generated)
- Audit checklist: `phase7_audit_checklist.md` (to be generated)
