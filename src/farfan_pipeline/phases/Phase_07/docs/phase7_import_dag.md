# Phase 7 Import DAG - Canonical Sequential Flow

## Generated: 2026-01-18
## Purpose: Document the deterministic import dependency graph for Phase 7

## DAG Structure

```
Phase 7 Import Dependency DAG (Topologically Sorted)
═══════════════════════════════════════════════════

Level 0 (Foundation - No Dependencies):
┌─────────────────────────────────────────────┐
│ phase7_10_00_phase_7_constants.py          │
│   - INPUT_CLUSTERS                          │
│   - CLUSTER_WEIGHTS                         │
│   - QUALITY_THRESHOLDS                      │
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
│ contracts/phase7_input_contract.py         │
│   - Phase7InputContract                     │
│   - validate() method                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ contracts/phase7_output_contract.py        │
│   - Phase7OutputContract                    │
│   - validate() method                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ contracts/phase7_mission_contract.py       │
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
Level 3 (Aggregation Logic):
┌─────────────────────────────────────────────┐
│ phase7_20_00_macro_aggregator.py           │
│   - MacroAggregator                         │
│   - Uses Phase7InputContract.validate()    │
│   - Uses Phase7OutputContract.validate()   │
│   - Imports: constants, macro_score,       │
│     systemic_gap_detector, contracts       │
└─────────────────────────────────────────────┘
                    │
                    │ all exported by
                    ▼
Level 4 (Public API):
┌─────────────────────────────────────────────┐
│ __init__.py                                 │
│   - Exports all public classes              │
│   - Exports all constants                   │
│   - Exports all contracts                   │
│   - Enforces contracts by default           │
└─────────────────────────────────────────────┘
```

## Import Matrix

| Module | Imports From | Exports To |
|--------|-------------|------------|
| phase7_10_00_phase_7_constants.py | (none - foundation) | macro_score, systemic_gap_detector, macro_aggregator, __init__ |
| phase7_10_00_macro_score.py | (none - foundation) | macro_aggregator, output_contract, __init__ |
| phase7_10_00_systemic_gap_detector.py | (none - foundation) | macro_aggregator, __init__ |
| contracts/phase7_input_contract.py | (none - TYPE_CHECKING only) | contracts/__init__, macro_aggregator |
| contracts/phase7_output_contract.py | (none - TYPE_CHECKING only) | contracts/__init__, macro_aggregator |
| contracts/phase7_mission_contract.py | (none) | contracts/__init__ |
| contracts/__init__.py | input_contract, output_contract, mission_contract | macro_aggregator, __init__ |
| phase7_20_00_macro_aggregator.py | constants, macro_score, systemic_gap_detector, contracts | __init__ |
| __init__.py | constants, macro_score, systemic_gap_detector, macro_aggregator, contracts | (public API) |

## Execution Order (Subphases)

### Stage 0: Infrastructure
1. **__init__.py** (order 0)
   - Type: INFRA
   - Purpose: Package initialization
   - Loads all submodules in correct order

### Stage 10: Configuration
1. **phase7_10_00_phase_7_constants.py** (order 0)
   - Type: CFG
   - Purpose: Foundation constants
   - Dependencies: None
   
2. **phase7_10_00_macro_score.py** (order 1)
   - Type: CFG
   - Purpose: Data model definition
   - Dependencies: constants (implicit)
   
3. **phase7_10_00_systemic_gap_detector.py** (order 2)
   - Type: CFG
   - Purpose: Gap detection logic
   - Dependencies: constants (implicit)

### Stage 20: Enforcement
1. **phase7_20_00_macro_aggregator.py** (order 0)
   - Type: ENF
   - Purpose: Main aggregation logic
   - Dependencies: constants, macro_score, systemic_gap_detector, contracts
   - **Enforces contracts by default**

## Contract Enforcement Flow

```
User imports Phase_07
        ↓
__init__.py loads contracts
        ↓
MacroAggregator.aggregate() called
        ↓
Phase7InputContract.validate() ← ENFORCED
        ↓
Perform aggregation
        ↓
Phase7OutputContract.validate() ← ENFORCED
        ↓
Return MacroScore
```

## Determinism Guarantees

1. **Import Order**: All imports follow topological order (no cycles)
2. **Contract Validation**: Always executed by default (not optional)
3. **No Side Effects**: Modules can be imported in any order without state changes
4. **Reproducibility**: Same inputs → Same outputs (bit-for-bit identical)

## Files Participating in Flow (By Default)

✅ All 5 Python files in Phase_07 participate:
- phase7_10_00_phase_7_constants.py
- phase7_10_00_macro_score.py
- phase7_10_00_systemic_gap_detector.py
- phase7_20_00_macro_aggregator.py
- __init__.py

✅ All 3 contract files participate:
- contracts/phase7_input_contract.py
- contracts/phase7_output_contract.py
- contracts/phase7_mission_contract.py
- contracts/__init__.py

## Canonical Path Verification

✅ No duplicate Phase 7 folders
✅ Only canonical path: `src/farfan_pipeline/phases/Phase_07/`
✅ All files in manifest match files on disk
✅ Manifest order corrected (constants first)
✅ Contracts enforced by default in flow

## Integration Points

### Upstream (Phase 6)
```python
from farfan_pipeline.phases.Phase_06 import ClusterScore
# Phase 6 produces 4 ClusterScore objects
```

### Downstream (Phase 8)
```python
from farfan_pipeline.phases.Phase_07 import MacroScore
# Phase 7 produces 1 MacroScore object
```

## Validation

Run this to verify the flow:
```bash
cd /home/runner/work/FARFAN_MCDPP/FARFAN_MCDPP
python3 -c "
import sys
sys.path.insert(0, 'src')
from farfan_pipeline.phases.Phase_07 import (
    MacroAggregator,
    Phase7InputContract,
    Phase7OutputContract,
)
print('✅ Phase 7 flow verified: All files participate by default')
"
```
