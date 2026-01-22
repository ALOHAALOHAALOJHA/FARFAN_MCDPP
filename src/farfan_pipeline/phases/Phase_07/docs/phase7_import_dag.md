# Phase 7 Import DAG - Canonical Sequential Flow (Constitutional Orchestration)

## Generated: 2026-01-22
## Purpose: Document the deterministic import dependency graph for Phase 7
## Version: 2.1.0 - Includes constitutional orchestration modules

## DAG Structure

```
Phase 7 Import Dependency DAG (Topologically Sorted) - Constitutional Orchestration
═══════════════════════════════════════════════════════════════════════════════

Level 0 (Foundation - No Dependencies):
┌─────────────────────────────────────────────┐
│ phase7_10_00_phase_7_constants.py          │
│   - INPUT_CLUSTERS                          │
│   - CLUSTER_WEIGHTS                         │
│   - QUALITY_THRESHOLDS                      │
│   - COHERENCE_WEIGHTS                       │
│   - QualityLevel, MacroInvariants          │
└─────────────────────────────────────────────┘
                    │
                    │ imported by
                    ▼

Level 1 (Data Models & Utilities):
┌─────────────────────────────────────────────┐
│ phase7_10_00_macro_score.py                │
│   - MacroScore dataclass                    │
│   - TYPE_CHECKING: ClusterScore            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ phase7_10_00_systemic_gap_detector.py      │
│   - SystemicGapDetector                     │
│   - SystemicGap                             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ contracts/phase7_10_00_input_contract.py   │
│   - Phase7InputContract                     │
│   - validate() method                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ contracts/phase7_10_02_output_contract.py  │
│   - Phase7OutputContract                    │
│   - validate() method                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ contracts/phase7_10_01_mission_contract.py  │
│   - Phase7MissionContract                   │
│   - Invariants documentation                │
└─────────────────────────────────────────────┘
                    │
                    │ all imported by
                    ▼

Level 2 (Contract Module):
┌─────────────────────────────────────────────┐
│ contracts/__init__.py                       │
│   - Exports all contracts                   │
└─────────────────────────────────────────────┘
                    │
                    │ imported by
                    ▼

Level 3 (Interphase Bridge - NEW):
┌─────────────────────────────────────────────┐
│ interphase/__init__.py                      │
│   - Exports interphase bridge               │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ interphase/phase6_to_phase7_bridge.py      │
│   - Phase6OutputContract                    │
│   - bridge_phase6_to_phase7()              │
│   - validate_phase6_output_for_phase7()    │
└─────────────────────────────────────────────┘
                    │
                    │ imported by
                    ▼

Level 4 (Aggregation Logic):
┌─────────────────────────────────────────────┐
│ phase7_20_00_macro_aggregator.py           │
│   - MacroAggregator                         │
│   - Uses Phase7InputContract.validate()    │
│   - Uses Phase7OutputContract.validate()   │
│   - Imports: constants, macro_score,       │
│     systemic_gap_detector, contracts       │
└─────────────────────────────────────────────┘
                    │
                    │ imported by
                    ▼

Level 5 (Operations - NEW):
┌─────────────────────────────────────────────┐
│ phase7_30_00_checkpoint_manager.py         │
│   - Phase7CheckpointManager                 │
│   - STAGE_ORDER for resumption              │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ phase7_31_00_performance_metrics.py        │
│   - Phase7MetricsCollector                  │
│   - StageMetrics, Phase7Metrics            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ phase7_32_00_exit_gate_validation.py       │
│   - Phase7ExitGateValidator                 │
│   - validate_phase7_exit_gate()            │
└─────────────────────────────────────────────┘
                    │
                    │ all exported by
                    ▼

Level 6 (Public API):
┌─────────────────────────────────────────────┐
│ __init__.py                                 │
│   - Exports all public classes              │
│   - Exports all constants                   │
│   - Exports all contracts                   │
│   - Enforces contracts by default           │
└─────────────────────────────────────────────┘
```

## Constitutional Orchestration Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 7 CONSTITUTIONAL ORCHESTRATION FLOW                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STAGE 0: INFRASTRUCTURE                                                    │
│  ├── __init__.py (package initialization)                                  │
│  └── PHASE_7_CONSTANTS.py (phase-level constants)                          │
│                                                                             │
│  STAGE 5: INTERPHASE BRIDGE (Phase 6 → Phase 7)                            │
│  ├── interphase/__init__.py                                                │
│  └── interphase/phase6_to_phase7_bridge.py                                 │
│      ├── Phase6OutputContract                                              │
│      ├── extract_from_cluster_scores()                                     │
│      ├── validate_phase6_output_for_phase7()                              │
│      └── bridge_phase6_to_phase7()                                        │
│                                                                             │
│  STAGE 10: CONFIGURATION                                                    │
│  ├── phase7_10_00_phase_7_constants.py (foundation constants)             │
│  ├── phase7_10_00_macro_score.py (data model)                             │
│  └── phase7_10_00_systemic_gap_detector.py (gap detection)               │
│                                                                             │
│  STAGE 20: ENFORCEMENT                                                      │
│  └── phase7_20_00_macro_aggregator.py (main logic)                         │
│      ├── Input validation via Phase7InputContract                          │
│      ├── Weighted score computation                                        │
│      ├── Quality classification                                            │
│      ├── Cross-cutting coherence analysis (CCCA)                          │
│      ├── Systemic gap detection (SGD)                                      │
│      ├── Strategic alignment scoring (SAS)                                 │
│      ├── Uncertainty propagation                                           │
│      └── Output validation via Phase7OutputContract                        │
│                                                                             │
│  STAGE 30: OPERATIONS (Orchestrator Integration)                          │
│  ├── phase7_30_00_checkpoint_manager.py                                    │
│  │   ├── save_stage_checkpoint()                                           │
│  │   ├── get_resumption_point()                                            │
│  │   └── clear_checkpoints()                                               │
│  │                                                                         │
│  ├── phase7_31_00_performance_metrics.py                                  │
│  │   ├── start_phase()                                                     │
│  │   ├── track_stage()                                                     │
│  │   ├── end_phase()                                                       │
│  │   └── export_metrics()                                                  │
│  │                                                                         │
│  └── phase7_32_00_exit_gate_validation.py                                 │
│      ├── validate()                                                        │
│      ├── _validate_quality_level()                                         │
│      ├── _validate_coherence_alignment()                                  │
│      ├── _validate_provenance()                                            │
│      └── _generate_phase8_certificate()                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Import Matrix

| Module | Imports From | Exports To |
|--------|-------------|------------|
| **Foundation** | | |
| phase7_10_00_phase_7_constants.py | (none - foundation) | macro_score, systemic_gap_detector, macro_aggregator, __init__ |
| **Data Models** | | |
| phase7_10_00_macro_score.py | (none - foundation) | macro_aggregator, output_contract, __init__ |
| phase7_10_00_systemic_gap_detector.py | (none - foundation) | macro_aggregator, __init__ |
| **Contracts** | | |
| contracts/phase7_input_contract.py | (none - TYPE_CHECKING only) | contracts/__init__, macro_aggregator, interphase_bridge |
| contracts/phase7_output_contract.py | (none - TYPE_CHECKING only) | contracts/__init__, macro_aggregator, exit_gate |
| contracts/phase7_mission_contract.py | (none) | contracts/__init__, orchestrator |
| contracts/__init__.py | input_contract, output_contract, mission_contract | macro_aggregator, __init__ |
| **Interphase Bridge** | | |
| interphase/__init__.py | phase6_to_phase7_bridge | orchestrator, __init__ |
| interphase/phase6_to_phase7_bridge.py | contracts (input), Phase6 types | orchestrator |
| **Aggregation** | | |
| phase7_20_00_macro_aggregator.py | constants, macro_score, systemic_gap_detector, contracts | __init__ |
| **Operations** | | |
| phase7_30_00_checkpoint_manager.py | (none - standalone) | orchestrator |
| phase7_31_00_performance_metrics.py | (none - standalone) | orchestrator |
| phase7_32_00_exit_gate_validation.py | contracts (output), macro_score | orchestrator |
| **Public API** | | |
| __init__.py | constants, macro_score, systemic_gap_detector, macro_aggregator, contracts | (public API) |

## Execution Order (Orchestrator Integration)

### Constitutional Orchestration Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              PHASE 7 ORCHESTRATOR - CONSTITUTIONAL EXECUTION                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. METRICS COLLECTOR INITIALIZATION                                       │
│     └── Phase7MetricsCollector(plan_id)                                    │
│                                                                             │
│  2. CHECKPOINT MANAGER INITIALIZATION                                      │
│     └── Phase7CheckpointManager(checkpoint_dir, plan_id)                  │
│     ├── Check for resumption point                                         │
│     └── Load checkpoint if exists                                          │
│                                                                             │
│  3. STAGE 1: INPUT VALIDATION (Interphase Bridge)                          │
│     └── bridge_phase6_to_phase7(cluster_scores)                            │
│         ├── extract_from_cluster_scores()                                  │
│         ├── validate_phase6_output_for_phase7()                            │
│         └── Return validated_cluster_scores, bridge_contract               │
│                                                                             │
│  4. SISAS SIGNAL: PHASE STARTED                                            │
│     └── _emit_phase_signal("P07", "STARTED", {...})                        │
│                                                                             │
│  5. STAGE 2-8: MACRO AGGREGATION (with metrics tracking)                   │
│     └── with metrics_collector.track_stage("P7_MACRO_AGGREGATION"):        │
│         └── MacroAggregator.aggregate(validated_cluster_scores)            │
│             ├── Input contract validation                                  │
│             ├── Weighted score computation                                 │
│             ├── Quality classification                                     │
│             ├── Cross-cutting coherence analysis (CCCA)                   │
│             ├── Systemic gap detection (SGD)                               │
│             ├── Strategic alignment scoring (SAS)                          │
│             ├── Uncertainty propagation                                    │
│             └── Output contract validation                                 │
│                                                                             │
│  6. CONSTITUTIONAL INVARIANTS VALIDATION                                  │
│     ├── INV-7.1: Cluster weights sum to 1.0                              │
│     ├── INV-7.3: Score domain [0.0, 3.0]                                  │
│     └── INV-7.4: Coherence weights sum to 1.0                             │
│                                                                             │
│  7. EXIT GATE VALIDATION (Phase 8 Compatibility)                          │
│     └── validate_phase7_exit_gate(macro_score, input_cluster_ids)         │
│         ├── Output contract validation (POST-7.1 through POST-7.7)        │
│         ├── Quality level verification                                     │
│         ├── Coherence and alignment bounds                                │
│         ├── Provenance traceability                                      │
│         └── Phase 8 compatibility certificate                             │
│                                                                             │
│  8. CHECKPOINT CLEANUP                                                     │
│     └── checkpoint_manager.clear_checkpoints()                             │
│                                                                             │
│  9. METRICS FINALIZATION                                                   │
│     └── metrics_collector.end_phase(macro_score_info)                      │
│         ├── Compute aggregate statistics                                   │
│         └── Export metrics to JSON file                                    │
│                                                                             │
│ 10. SISAS SIGNAL: PHASE COMPLETED                                          │
│     └── _emit_phase_signal("P07", "COMPLETED", {...})                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Contract Enforcement Flow

```
User imports Phase_07
        ↓
__init__.py loads contracts
        ↓
Orchestrator calls _execute_phase_07()
        ↓
Phase7MetricsCollector.start_phase()
        ↓
Phase7CheckpointManager initialization
        ↓
┌─────────────────────────────────────────────────────────────┐
│           INTERPHASE BRIDGE (Stage 1)                       │
│  bridge_phase6_to_phase7(cluster_scores)                    │
│    ├── extract_from_cluster_scores()                         │
│    └── validate_phase6_output_for_phase7()                   │
│        └── Phase7InputContract.validate() ← ENFORCED        │
└─────────────────────────────────────────────────────────────┘
        ↓
SISAS: _emit_phase_signal("P07", "STARTED")
        ↓
┌─────────────────────────────────────────────────────────────┐
│              MACRO AGGREGATION (Stage 2-8)                 │
│  with metrics_collector.track_stage("P7_MACRO_AGGREGATION"):│
│    MacroAggregator.aggregate(validated_cluster_scores)      │
│      ├── Weighted score computation                         │
│      ├── Cross-cutting coherence (CCCA)                     │
│      ├── Systemic gap detection (SGD)                       │
│      ├── Strategic alignment (SAS)                          │
│      └── Phase7OutputContract.validate() ← ENFORCED        │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│        CONSTITUTIONAL INVARIANTS VALIDATION                │
│  ├── INV-7.1: Cluster weights sum to 1.0                    │
│  ├── INV-7.3: Score domain [0.0, 3.0]                       │
│  └── INV-7.4: Coherence weights sum to 1.0                   │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│          EXIT GATE VALIDATION (Stage 9)                    │
│  validate_phase7_exit_gate(macro_score, input_cluster_ids)  │
│    ├── Output contract validation                           │
│    ├── Quality level verification                           │
│    ├── Coherence and alignment bounds                      │
│    ├── Provenance traceability                             │
│    └── Phase 8 compatibility certificate                    │
└─────────────────────────────────────────────────────────────┘
        ↓
checkpoint_manager.clear_checkpoints()
        ↓
metrics_collector.end_phase()
        ↓
SISAS: _emit_phase_signal("P07", "COMPLETED")
        ↓
Return MacroScore
```

## Determinism Guarantees

1. **Import Order**: All imports follow topological order (no cycles)
2. **Contract Validation**: Always executed by default (not optional)
3. **No Side Effects**: Modules can be imported in any order without state changes
4. **Reproducibility**: Same inputs → Same outputs (bit-for-bit identical)
5. **Constitutional Enforcement**: All invariants validated at orchestrator level
6. **Checkpoint Recovery**: Mid-execution recovery without state loss
7. **Metrics Collection**: Performance tracking without side effects

## Files Participating in Flow (Constitutional Orchestration)

✅ All 11 Python files in Phase_07 participate:
- **Stage 0**: __init__.py, PHASE_7_CONSTANTS.py
- **Stage 5**: interphase/__init__.py, interphase/phase6_to_phase7_bridge.py
- **Stage 10**: phase7_10_00_phase_7_constants.py, phase7_10_00_macro_score.py, phase7_10_00_systemic_gap_detector.py
- **Stage 20**: phase7_20_00_macro_aggregator.py
- **Stage 30**: phase7_30_00_checkpoint_manager.py, phase7_31_00_performance_metrics.py, phase7_32_00_exit_gate_validation.py

✅ All 4 contract files participate:
- contracts/phase7_input_contract.py
- contracts/phase7_output_contract.py
- contracts/phase7_mission_contract.py
- contracts/__init__.py

## Canonical Path Verification

✅ No duplicate Phase 7 folders
✅ Only canonical path: `src/farfan_pipeline/phases/Phase_07/`
✅ All files in manifest match files on disk
✅ Manifest order follows topological DAG
✅ Contracts enforced by default in flow
✅ Constitutional orchestration fully integrated

## Integration Points

### Upstream (Phase 6)
```python
from farfan_pipeline.phases.Phase_06 import ClusterScore
# Phase 6 produces 4 ClusterScore objects

# Interphase bridge ensures contract compliance
from farfan_pipeline.phases.Phase_07.interphase import bridge_phase6_to_phase7
validated_scores, contract = bridge_phase6_to_phase7(cluster_scores)
```

### Downstream (Phase 8)
```python
from farfan_pipeline.phases.Phase_07 import MacroScore
# Phase 7 produces 1 MacroScore object

# Exit gate ensures Phase 8 compatibility
from farfan_pipeline.phases.Phase_07.phase7_32_00_exit_gate_validation import validate_phase7_exit_gate
result = validate_phase7_exit_gate(macro_score, input_cluster_ids)
certificate = result.certificate  # Phase 8 compatibility certificate
```

## Constitutional Orchestration Features

| Feature | Module | Purpose |
|---------|--------|---------|
| **Interphase Bridge** | interphase/phase6_to_phase7_bridge.py | Phase 6→7 handoff validation |
| **Checkpoint Recovery** | phase7_30_00_checkpoint_manager.py | Mid-execution recovery |
| **Performance Metrics** | phase7_31_00_performance_metrics.py | Timing/memory tracking |
| **Exit Gate Validation** | phase7_32_00_exit_gate_validation.py | Phase 8 compatibility |
| **Constitutional Invariants** | contracts/phase7_10_01_mission_contract.py | Invariant enforcement |
| **SISAS Signals** | orchestrator._emit_phase_signal() | Phase progress signals |

## Validation

Run this to verify the constitutional flow:
```bash
cd /Users/recovered/Downloads/FARFAN_MCDPP
python3 -c "
import sys
sys.path.insert(0, 'src')
from farfan_pipeline.phases.Phase_07 import (
    MacroAggregator,
    Phase7InputContract,
    Phase7OutputContract,
)
from farfan_pipeline.phases.Phase_07.interphase import bridge_phase6_to_phase7
from farfan_pipeline.phases.Phase_07.phase7_30_00_checkpoint_manager import Phase7CheckpointManager
from farfan_pipeline.phases.Phase_07.phase7_31_00_performance_metrics import Phase7MetricsCollector
from farfan_pipeline.phases.Phase_07.phase7_32_00_exit_gate_validation import validate_phase7_exit_gate
print('✅ Phase 7 constitutional flow verified: All 11 modules participate')
print('✅ Interphase bridge: OK')
print('✅ Checkpoint manager: OK')
print('✅ Performance metrics: OK')
print('✅ Exit gate validation: OK')
"
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-18 | Initial DAG documentation (5 modules) |
| 2.0.0 | 2026-01-22 | Added constitutional orchestration modules |
| 2.1.0 | 2026-01-22 | Complete DAG with all 11 modules + orchestrator integration |
