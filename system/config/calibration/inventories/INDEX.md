# COHORT_2024 Calibration Inventories - File Index

## Directory Structure

```
system/config/calibration/inventories/
├── Documentation
│   ├── INDEX.md                           ← This file
│   ├── README.md                          ← Main documentation
│   ├── QUICK_START.md                     ← Quick start guide
│   └── SYSTEM_OVERVIEW.md                 ← Complete system overview
│
├── Core Scripts
│   ├── __init__.py                        ← Package initialization
│   ├── scan_methods_inventory.py          ← Method discovery scanner
│   ├── method_signature_extractor.py      ← Parametrization analyzer
│   ├── calibration_coverage_validator.py  ← Coverage matrix generator
│   └── consolidate_calibration_inventories.py  ← Main orchestrator
│
├── Utilities
│   └── run_consolidation.sh               ← Shell wrapper for consolidation
│
└── Generated Artifacts (gitignored)
    ├── COHORT_2024_canonical_method_inventory.json      ← Artifact 1
    ├── COHORT_2024_method_signatures.json               ← Artifact 2
    ├── COHORT_2024_calibration_coverage_matrix.json     ← Artifact 3
    ├── COHORT_2024_consolidation_summary.md             ← Summary report
    └── calibration_consolidation.log                    ← Execution log
```

## File Descriptions

### Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| **INDEX.md** | Directory structure and file guide | All users |
| **README.md** | Comprehensive documentation | All users |
| **QUICK_START.md** | Quick start guide | New users |
| **SYSTEM_OVERVIEW.md** | Complete technical overview | Developers, architects |

### Core Scripts

| File | Purpose | Output | Dependencies |
|------|---------|--------|--------------|
| **scan_methods_inventory.py** | Discovers all methods in codebase | Artifact 1 | None |
| **method_signature_extractor.py** | Extracts parametrization specs | Artifact 2 | Artifact 1 |
| **calibration_coverage_validator.py** | Generates coverage matrix | Artifact 3 | Artifact 1, source configs |
| **consolidate_calibration_inventories.py** | Orchestrates all scripts | All artifacts + summary | All above |

### Generated Artifacts

| File | Description | Size (approx) | Update Frequency |
|------|-------------|---------------|------------------|
| **COHORT_2024_canonical_method_inventory.json** | Complete method inventory (1995+ methods) | 2-5 MB | Daily/weekly |
| **COHORT_2024_method_signatures.json** | Parametrization specifications | 1-3 MB | Daily/weekly |
| **COHORT_2024_calibration_coverage_matrix.json** | Layer-wise calibration status | 3-8 MB | After calibrations |
| **COHORT_2024_consolidation_summary.md** | Statistics and summary report | 10-20 KB | With artifacts |
| **calibration_consolidation.log** | Detailed execution log | 50-200 KB | With artifacts |

## Quick Navigation

### For First-Time Users
1. Start with **QUICK_START.md**
2. Run `./run_consolidation.sh`
3. Review `COHORT_2024_consolidation_summary.md`

### For Developers
1. Read **SYSTEM_OVERVIEW.md** for architecture
2. Review core scripts for implementation details
3. Check **README.md** for API and integration points

### For Maintenance
1. Check **README.md** maintenance section
2. Review regeneration schedule
3. Validate artifacts against quality metrics

### For Troubleshooting
1. Check **QUICK_START.md** troubleshooting section
2. Review `calibration_consolidation.log`
3. Consult **SYSTEM_OVERVIEW.md** for detailed diagnostics

## Usage Patterns

### Complete Consolidation
```bash
python3 consolidate_calibration_inventories.py
# OR
./run_consolidation.sh
```

### Individual Scripts
```bash
python3 scan_methods_inventory.py                  # Generate Artifact 1
python3 method_signature_extractor.py              # Generate Artifact 2
python3 calibration_coverage_validator.py          # Generate Artifact 3
```

### Programmatic Access
```python
from system.config.calibration.inventories import (
    consolidate_calibration_inventories
)
# Or import individual scanner/extractor/validator classes
```

## Key Concepts

### Method Notation
Format: `MODULE:CLASS.METHOD@LAYER`  
Example: `farfan_pipeline.core:Orchestrator.calibrate@b,chain,u,m`

### Role Classifications
- SCORE_Q - Question scoring
- INGEST_PDM - Document ingestion
- STRUCTURE - Data structuring
- EXTRACT - Data extraction
- AGGREGATE - Aggregation
- REPORT - Reporting
- META_TOOL - Meta tools
- TRANSFORM - Transformations

### 8 Layers
- @b - Base (intrinsic quality)
- @q - Question compatibility
- @d - Dimension compatibility
- @p - Policy compatibility
- @C - Congruence
- @chain - Chain compatibility
- @u - Unit testing
- @m - Meta analysis

### Calibration Status
- `computed` - Layer score calculated
- `pending` - Layer score needs calculation
- `fully_calibrated` - All 8 layers computed
- `partially_calibrated` - Some layers computed
- `not_calibrated` - No layers computed

## Integration Points

### Source Configs
Location: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/`

Files:
- COHORT_2024_intrinsic_calibration.json
- COHORT_2024_method_compatibility.json
- COHORT_2024_layer_requirements.json
- COHORT_2024_fusion_weights.json

### Calibration Runtime
Main orchestrator: `src/orchestration/calibration_orchestrator.py`

### Test Suite
Location: `tests/calibration/`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-12-15 | Initial implementation |

## Related Documentation

- Layer versioning: `src/orchestration/LAYER_VERSIONING_README.md`
- Unit layer: `src/orchestration/UNIT_LAYER_README.md`
- Calibration orchestrator: `src/orchestration/calibration_orchestrator.py`
- Chain layer: `CHAIN_LAYER_SPECIFICATION.md`

---

*COHORT_2024 Calibration Inventory System*  
*Part of REFACTOR_WAVE_2024_12*
