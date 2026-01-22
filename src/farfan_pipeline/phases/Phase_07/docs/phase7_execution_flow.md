# Phase 7 Execution Flow (Constitutional Orchestration)

## Overview

Phase 7 implements the final aggregation tier of the F.A.R.F.A.N pipeline with **constitutional orchestration**. It synthesizes 4 MESO-level cluster scores into a single holistic MacroScore with comprehensive validation, checkpoint support, performance metrics, and exit gate validation.

## Version 2.1.0 - Constitutional Orchestration

This version includes:
- Interphase bridge for Phase 6→7 handoff validation
- Checkpoint/recovery support for resilience
- Performance metrics collection for observability
- Exit gate validation for Phase 8 compatibility
- Constitutional invariant enforcement
- SISAS signal emission for monitoring

## Topological Order

```
Stage 0: Infrastructure
├── __init__.py
└── PHASE_7_CONSTANTS.py
    ↓
Stage 5: Interphase Bridge (NEW)
├── interphase/__init__.py
└── interphase/phase6_to_phase7_bridge.py
    ↓
Stage 10: Configuration
├── phase7_10_00_phase_7_constants.py
├── phase7_10_00_macro_score.py
└── phase7_10_00_systemic_gap_detector.py
    ↓
Stage 20: Enforcement
└── phase7_20_00_macro_aggregator.py
    ↓
Stage 30: Operations (NEW)
├── phase7_30_00_checkpoint_manager.py
├── phase7_31_00_performance_metrics.py
└── phase7_32_00_exit_gate_validation.py
    ↓
Public API: __init__.py
```

## Module Responsibilities

### Stage 0: Infrastructure

#### `__init__.py`
- **Position**: Foundation (no dependencies)
- **Purpose**: Package initialization and public API exports
- **Exports**: All public classes, constants, and contracts

#### `PHASE_7_CONSTANTS.py`
- **Position**: Foundation (no dependencies)
- **Purpose**: Phase-level constants
- **Exports**: Phase-wide configuration values

### Stage 5: Interphase Bridge (CONSTITUTIONAL ORCHESTRATION)

#### `interphase/__init__.py`
- **Position**: Layer 1 (depends on interphase bridge)
- **Purpose**: Exports interphase bridge functionality
- **Exports**: `bridge_phase6_to_phase7`, `Phase6OutputContract`, `Phase6ToPhase7BridgeError`

#### `interphase/phase6_to_phase7_bridge.py`
- **Position**: Layer 1 (depends on Phase 6 types, contracts)
- **Purpose**: Explicit Phase 6 → Phase 7 handoff contract
- **Key Functions**:
  - `extract_from_cluster_scores()` - Extract Phase 6 output contract
  - `validate_phase6_output_for_phase7()` - Validate input
  - `bridge_phase6_to_phase7()` - Complete handoff transformation

### Stage 10: Configuration

#### `phase7_10_00_phase_7_constants.py`
- **Position**: Foundation (no dependencies)
- **Purpose**: Defines all constants, enumerations, and invariants
- **Exports**:
  - `CLUSTER_WEIGHTS`: Equal weights for 4 clusters (0.25 each)
  - `QUALITY_THRESHOLDS`: Classification thresholds
  - `COHERENCE_WEIGHTS`: Strategic/Operational/Institutional weights
  - `QualityLevel`, `MacroInvariants` classes

#### `phase7_10_00_macro_score.py`
- **Position**: Layer 2 (depends on constants)
- **Purpose**: Defines output data structure
- **Exports**: `MacroScore` dataclass
- **Invariants**:
  - Score ∈ [0.0, 3.0]
  - Coherence ∈ [0.0, 1.0]
  - Alignment ∈ [0.0, 1.0]
  - Valid quality levels only

#### `phase7_10_00_systemic_gap_detector.py`
- **Position**: Layer 2 (depends on constants)
- **Purpose**: Identifies policy areas with systemic gaps
- **Exports**: `SystemicGapDetector`, `SystemicGap` classes
- **Logic**:
  - Detects areas with scores < 1.65 (55% threshold)
  - Classifies severity: CRITICAL, SEVERE, MODERATE
  - Cross-cluster pattern analysis

### Stage 20: Enforcement

#### `phase7_20_00_macro_aggregator.py`
- **Position**: Layer 3 (depends on all Stage 10 modules)
- **Purpose**: Main aggregation logic
- **Dependencies**:
  - Constants
  - MacroScore
  - SystemicGapDetector
  - ClusterScore (from Phase 6)
  - All contracts
- **Exports**: `MacroAggregator` class
- **Algorithm**:
  1. Validate input (4 ClusterScore objects) via Phase7InputContract
  2. Compute weighted average
  3. Calculate cross-cutting coherence (CCCA)
  4. Detect systemic gaps (SGD)
  5. Compute strategic alignment (SAS)
  6. Propagate uncertainty
  7. Classify quality level
  8. Assemble MacroScore output
  9. Validate output via Phase7OutputContract

### Stage 30: Operations (CONSTITUTIONAL ORCHESTRATION)

#### `phase7_30_00_checkpoint_manager.py`
- **Position**: Layer 4 (depends on none)
- **Purpose**: Checkpoint and recovery manager for Phase 7
- **Exports**: `Phase7CheckpointManager`, `CheckpointMetadata`
- **Key Features**:
  - `save_stage_checkpoint()` - Save checkpoint after stage completion
  - `get_resumption_point()` - Determine next stage to resume from
  - `clear_checkpoints()` - Cleanup after successful completion
  - `validate_checkpoint_integrity()` - Validate checkpoint file integrity

#### `phase7_31_00_performance_metrics.py`
- **Position**: Layer 4 (depends on none)
- **Purpose**: Performance metrics collector for Phase 7
- **Exports**: `Phase7MetricsCollector`, `StageMetrics`, `Phase7Metrics`
- **Key Features**:
  - `start_phase()` - Mark phase start
  - `track_stage()` - Context manager for stage tracking
  - `end_phase()` - Mark phase end and compute aggregates
  - `export_metrics()` - Export metrics to JSON file

#### `phase7_32_00_exit_gate_validation.py`
- **Position**: Layer 4 (depends on MacroScore, contracts)
- **Purpose**: Exit gate validation for Phase 8 compatibility
- **Exports**: `Phase7ExitGateValidator`, `validate_phase7_exit_gate()`
- **Key Features**:
  - Output contract validation (POST-7.1 through POST-7.7)
  - Quality level verification
  - Coherence and alignment bounds validation
  - Provenance traceability validation
  - Phase 8 compatibility certificate generation

## Constitutional Orchestration Execution Sequence

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 7 CONSTITUTIONAL ORCHESTRATION                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INPUT: 4 ClusterScore objects from Phase 6                                 │
│  OUTPUT: 1 MacroScore object (validated for Phase 8)                        │
│  RATIO: 4:1 compression (final)                                               │
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ STAGE 1: METRICS COLLECTOR INITIALIZATION                                  ║ │
│  ║   Phase7MetricsCollector(plan_id, cluster_count=4)                       ║ │
│  ║   └── start_phase()                                                      ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                   ↓                                          │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ STAGE 2: CHECKPOINT MANAGER INITIALIZATION                                ║ │
│  ║   Phase7CheckpointManager(checkpoint_dir, plan_id)                       ║ │
│  ║   ├── Check for resumption point                                         ║ │
│  ║   └── Load checkpoint if exists                                          ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                   ↓                                          │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ STAGE 3: INPUT VALIDATION (Interphase Bridge)                            ║ │
│  ║   bridge_phase6_to_phase7(cluster_scores)                                ║ │
│  ║   ├── extract_from_cluster_scores()                                      ║ │
│  ║   ├── validate_phase6_output_for_phase7()                                 ║ │
│  ║   │   └── Phase7InputContract.validate()                                 ║ │
│  ║   └── Return validated_cluster_scores, bridge_contract                     ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                   ↓                                          │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ STAGE 4: SISAS SIGNAL: PHASE STARTED                                     ║ │
│  ║   _emit_phase_signal("P07", "STARTED", {plan_id, cluster_count})        ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                   ↓                                          │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ STAGE 5-11: MACRO AGGREGATION (with metrics tracking)                    ║ │
│  ║   with metrics_collector.track_stage("P7_MACRO_AGGREGATION"):           ║ │
│  ║       MacroAggregator.aggregate(validated_cluster_scores)                ║ │
│  ║       ├── Weighted score computation                                      ║ │
│  ║       ├── Quality classification                                           ║ │
│  ║       ├── Cross-cutting coherence analysis (CCCA)                         ║ │
│  ║       ├── Systemic gap detection (SGD)                                    ║ │
│  ║       ├── Strategic alignment scoring (SAS)                               ║ │
│  ║       ├── Uncertainty propagation                                         ║ │
│  ║       └── Phase7OutputContract.validate()                                 ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                   ↓                                          │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ STAGE 12: CONSTITUTIONAL INVARIANTS VALIDATION                           ║ │
│  ║   ├── INV-7.1: Cluster weights sum to 1.0                                ║ │
│  ║   ├── INV-7.3: Score domain [0.0, 3.0]                                     ║ │
│  ║   └── INV-7.4: Coherence weights sum to 1.0                                ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                   ↓                                          │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ STAGE 13: EXIT GATE VALIDATION (Phase 8 Compatibility)                   ║ │
│  ║   validate_phase7_exit_gate(macro_score, input_cluster_ids)               ║ │
│  ║       ├── Output contract validation (POST-7.1 through POST-7.7)         ║ │
│  ║       ├── Quality level verification                                       ║ │
│  ║       ├── Coherence and alignment bounds                                  ║ │
│  ║       ├── Provenance traceability                                         ║ │
│  ║       └── Phase 8 compatibility certificate                                ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                   ↓                                          │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ STAGE 14: CHECKPOINT CLEANUP                                               ║ │
│  ║   checkpoint_manager.clear_checkpoints()                                  ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                   ↓                                          │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ STAGE 15: METRICS FINALIZATION                                             ║ │
│  ║   metrics_collector.end_phase(macro_score_info)                          ║ │
│  ║       ├── Compute aggregate statistics                                     ║ │
│  ║       └── Export metrics to JSON file                                     ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                   ↓                                          │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ STAGE 16: SISAS SIGNAL: PHASE COMPLETED                                   ║ │
│  ║   _emit_phase_signal("P07", "COMPLETED", {...})                           ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                   ↓                                          │
│  RETURN: MacroScore (validated for Phase 8 consumption)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Contract Validation

### Input Contract (via Interphase Bridge)
Implemented in: `interphase/phase6_to_phase7_bridge.py`
- Function: `validate_phase6_output_for_phase7(cluster_scores)`
- Raises: `Phase6ToPhase7BridgeError` on violation
- Validates:
  - PRE-7.1: Exactly 4 ClusterScores
  - PRE-7.2: All CLUSTER_MESO_1 through CLUSTER_MESO_4 present
  - PRE-7.3: All scores ∈ [0.0, 3.0]
  - PRE-7.4: Valid provenance from Phase 6
  - PRE-7.5: No duplicate clusters
  - PRE-7.6: Coherence and dispersion metrics present

### Mission Validation
Implemented in: `contracts/phase7_mission_contract.py`
- Validates: Weight normalization, invariants
- Runs: On module import
- Checks:
  - INV-7.1: Cluster weights sum to 1.0
  - INV-7.2: Quality thresholds are properly ordered
  - INV-7.3: Score domain [0.0, 3.0]
  - INV-7.4: Coherence weights sum to 1.0

### Output Validation
Implemented in: `phase7_20_00_macro_aggregator.py` (MacroAggregator.aggregate)
- Function: Phase7OutputContract.validate() (enforced by default)
- Raises: ValueError on violation
- Validates:
  - POST-7.1: Output is valid MacroScore
  - POST-7.2: Score ∈ [0.0, 3.0]
  - POST-7.3: Valid quality_level
  - POST-7.4: Coherence ∈ [0.0, 1.0]
  - POST-7.5: Alignment ∈ [0.0, 1.0]
  - POST-7.6: Provenance references all 4 input clusters
  - POST-7.7: Valid area identifiers in systemic_gaps

### Exit Gate Validation
Implemented in: `phase7_32_00_exit_gate_validation.py`
- Function: `validate_phase7_exit_gate(macro_score, input_cluster_ids)`
- Raises: ValueError on violation
- Validates:
  - GATE-1: Output contract validation (POST-7.1 through POST-7.7)
  - GATE-2: Quality level assignment validation
  - GATE-3: Coherence and alignment bounds validation
  - GATE-4: Provenance traceability validation
  - GATE-5: Phase 8 compatibility validation

## Integration Points

### Upstream (Phase 6)
```python
from farfan_pipeline.phases.Phase_06 import ClusterScore

# Phase 6 produces 4 ClusterScore objects
cluster_scores: list[ClusterScore] = phase6_output

# Interphase bridge ensures contract compliance
from farfan_pipeline.phases.Phase_07.interphase import bridge_phase6_to_phase7
validated_scores, contract = bridge_phase6_to_phase7(cluster_scores)
```

### Downstream (Phase 8)
```python
from farfan_pipeline.phases.Phase_07 import MacroScore

# Phase 7 produces 1 MacroScore object
macro_score: MacroScore = phase7_output

# Exit gate ensures Phase 8 compatibility
from farfan_pipeline.phases.Phase_07.phase7_32_00_exit_gate_validation import validate_phase7_exit_gate
result = validate_phase7_exit_gate(macro_score, input_cluster_ids)
certificate = result.certificate  # Phase 8 compatibility certificate
```

## Error Handling

### Precondition Violations
- Input count ≠ 4 → `Phase6ToPhase7BridgeError`
- Missing clusters → `Phase6ToPhase7BridgeError`
- Score out of bounds → `Phase6ToPhase7BridgeError`
- Invalid cluster composition → `Phase6ToPhase7BridgeError`

### Invariant Violations
- Weight sum ≠ 1.0 → Auto-normalize with warning
- Invalid quality level → `ValueError`
- Coherence/alignment out of bounds → Clamp with warning

### Exit Gate Violations
- Output contract violation → `ValueError`
- Quality level mismatch → Constitutional invariant violation
- Provenance traceability failure → Warning in non-strict mode

## Performance Characteristics

- **Time Complexity**: O(n) where n = 10 (total policy areas)
- **Space Complexity**: O(n) for provenance tracking
- **Execution Time**: ~5-10ms typical
- **Memory Overhead**: ~5MB (without metrics)
- **Metrics Overhead**: ~1-2MB (with performance tracking)

## Determinism Guarantee

Phase 7 is fully deterministic:
- No random number generation
- No external API calls
- No file I/O during execution (except checkpoint/metrics export)
- Fixed-weight aggregation
- Deterministic float operations

**Same inputs → Same outputs (bit-for-bit identical)**

## Constitutional Orchestration Features

| Feature | Status | Module | Benefit |
|---------|--------|--------|---------|
| **Interphase Bridge** | ✅ Enabled | interphase/phase6_to_phase7_bridge.py | Explicit handoff validation |
| **Checkpoint Recovery** | ✅ Enabled | phase7_30_00_checkpoint_manager.py | Mid-execution recovery |
| **Performance Metrics** | ✅ Enabled | phase7_31_00_performance_metrics.py | Timing/memory tracking |
| **Exit Gate Validation** | ✅ Enabled | phase7_32_00_exit_gate_validation.py | Phase 8 compatibility |
| **Constitutional Invariants** | ✅ Enabled | contracts/phase7_10_01_mission_contract.py | Invariant enforcement |
| **SISAS Signals** | ✅ Enabled | orchestrator._emit_phase_signal() | Phase progress signals |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-18 | Initial execution flow documentation (5 modules) |
| 2.0.0 | 2026-01-22 | Added constitutional orchestration stages |
| 2.1.0 | 2026-01-22 | Complete constitutional orchestration with all stages |
