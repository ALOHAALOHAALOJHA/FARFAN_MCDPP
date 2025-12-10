# COHORT_2024 Calibration Inventories - File Manifest

**Version:** 1.0.0  
**Cohort:** COHORT_2024  
**Wave:** REFACTOR_WAVE_2024_12  
**Created:** 2024-12-15

## Purpose

This manifest documents all files in the calibration inventory system, their purpose, dependencies, and integration points.

## Directory: system/config/calibration/inventories/

### Documentation Files (5 files)

| File | Lines | Purpose | Target Audience |
|------|-------|---------|-----------------|
| **INDEX.md** | ~250 | Directory structure and navigation guide | All users |
| **README.md** | ~400 | Comprehensive system documentation | All users |
| **QUICK_START.md** | ~150 | Quick start guide with examples | New users |
| **SYSTEM_OVERVIEW.md** | ~700 | Complete technical architecture | Developers, architects |
| **MANIFEST.md** | ~200 | This file - complete file listing | Maintainers |

### Core Python Scripts (4 files)

#### 1. scan_methods_inventory.py
- **Lines:** ~300
- **Purpose:** Scans codebase to discover all methods
- **Output:** COHORT_2024_canonical_method_inventory.json
- **Dependencies:** ast, json, pathlib, datetime
- **External Dependencies:** None
- **Configurable:** src_dirs list (default: ['src', 'tests'])
- **Execution Time:** 3-5 minutes on typical codebase

**Key Classes:**
- `MethodSignature` - Dataclass for method metadata
- `MethodInventoryScanner` - Main scanner class

**Key Functions:**
- `scan_directory()` - Recursively scans directory
- `_scan_file()` - Parses single Python file
- `_classify_role()` - Classifies method role
- `_detect_layers()` - Detects layer annotations

#### 2. method_signature_extractor.py
- **Lines:** ~350
- **Purpose:** Extracts parametrization specifications
- **Output:** COHORT_2024_method_signatures.json
- **Dependencies:** ast, json, pathlib, datetime
- **Input Required:** COHORT_2024_canonical_method_inventory.json
- **Execution Time:** 5-10 minutes

**Key Classes:**
- `MethodSignatureExtractor` - Main extractor class

**Key Functions:**
- `extract_all_signatures()` - Processes all methods
- `_extract_method_signature()` - Extracts single signature
- `_parse_signature()` - Parses AST function signature
- `_get_type_annotation()` - Extracts type hints

#### 3. calibration_coverage_validator.py
- **Lines:** ~350
- **Purpose:** Generates calibration coverage matrix
- **Output:** COHORT_2024_calibration_coverage_matrix.json
- **Dependencies:** ast, json, pathlib, datetime, collections
- **Input Required:** 
  - COHORT_2024_canonical_method_inventory.json
  - COHORT_2024_intrinsic_calibration.json
  - COHORT_2024_method_compatibility.json
- **Execution Time:** 3-5 minutes

**Key Classes:**
- `CalibrationCoverageValidator` - Main validator class

**Key Functions:**
- `generate_coverage_matrix()` - Creates complete matrix
- `_check_layer_calibration()` - Checks single layer status
- `_avg_scores()` - Calculates average scores

#### 4. consolidate_calibration_inventories.py
- **Lines:** ~400
- **Purpose:** Orchestrates complete consolidation process
- **Output:** All artifacts + summary report + log file
- **Dependencies:** json, logging, pathlib, datetime
- **Internal Dependencies:** All 3 scripts above
- **Execution Time:** 15-20 minutes

**Key Classes:**
- `CalibrationInventoryConsolidator` - Main orchestrator class

**Key Functions:**
- `consolidate_all()` - Runs complete process
- `_run_scanner()` - Executes scanner
- `_run_signature_extractor()` - Executes extractor
- `_run_coverage_validator()` - Executes validator
- `_generate_summary_report()` - Creates markdown report

### Package Files (1 file)

#### __init__.py
- **Lines:** ~15
- **Purpose:** Package initialization and metadata
- **Exports:** Version info, cohort ID, wave version

### Utility Scripts (2 files)

#### run_consolidation.sh
- **Lines:** ~60
- **Purpose:** Shell wrapper for consolidation
- **Usage:** `./run_consolidation.sh`
- **Features:** Version check, error handling, output formatting

#### test_inventory_system.py
- **Lines:** ~250
- **Purpose:** Validates system before consolidation
- **Usage:** `python3 test_inventory_system.py`
- **Tests:** Directory structure, scripts, configs, imports, source dirs

### Generated Artifacts (5 files - gitignored)

#### COHORT_2024_canonical_method_inventory.json
- **Size:** 2-5 MB
- **Format:** JSON
- **Structure:**
  ```json
  {
    "_cohort_metadata": {...},
    "metadata": {
      "total_methods": 2000,
      "scan_timestamp": "..."
    },
    "methods": {
      "MODULE:CLASS.METHOD@LAYER": {...}
    }
  }
  ```
- **Update Frequency:** Daily during active development

#### COHORT_2024_method_signatures.json
- **Size:** 1-3 MB
- **Format:** JSON
- **Structure:**
  ```json
  {
    "_cohort_metadata": {...},
    "metadata": {
      "total_signatures": 2000
    },
    "signatures": {
      "MODULE:CLASS.METHOD@LAYER": {
        "required_inputs": [...],
        "optional_inputs": [...],
        "output_type": "..."
      }
    }
  }
  ```
- **Update Frequency:** With inventory updates

#### COHORT_2024_calibration_coverage_matrix.json
- **Size:** 3-8 MB
- **Format:** JSON
- **Structure:**
  ```json
  {
    "_cohort_metadata": {...},
    "statistics": {...},
    "coverage_matrix": {
      "MODULE:CLASS.METHOD@LAYER": {
        "calibration_status": {
          "@b": "computed|pending",
          ...
        },
        "layer_scores": {
          "@b": 0.85,
          ...
        }
      }
    }
  }
  ```
- **Update Frequency:** After calibration runs

#### COHORT_2024_consolidation_summary.md
- **Size:** 10-20 KB
- **Format:** Markdown
- **Content:** Statistics, coverage percentages, per-layer and per-role breakdowns
- **Update Frequency:** With artifact generation

#### calibration_consolidation.log
- **Size:** 50-200 KB
- **Format:** Plain text log
- **Content:** Detailed execution trace with timestamps, errors, warnings
- **Update Frequency:** Each consolidation run

## File Dependencies

### Dependency Graph

```
scan_methods_inventory.py
    │
    ├─► COHORT_2024_canonical_method_inventory.json
    │
    └─► method_signature_extractor.py
            │
            ├─► COHORT_2024_method_signatures.json
            │
            └─► calibration_coverage_validator.py
                    │
                    ├─► COHORT_2024_intrinsic_calibration.json (external)
                    ├─► COHORT_2024_method_compatibility.json (external)
                    │
                    └─► COHORT_2024_calibration_coverage_matrix.json

consolidate_calibration_inventories.py
    │
    ├─► scan_methods_inventory.py
    ├─► method_signature_extractor.py
    ├─► calibration_coverage_validator.py
    │
    ├─► All JSON artifacts
    ├─► COHORT_2024_consolidation_summary.md
    └─► calibration_consolidation.log
```

### External Dependencies

**Source Calibration Configs:**
- `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json`
- `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_method_compatibility.json`

**Source Code:**
- `src/` - Main source directory
- `tests/` - Test directory

## Version Control

### Tracked Files (13 files)
All documentation, scripts, and utilities are tracked in git:
- 5 documentation files (.md)
- 4 core scripts (.py)
- 1 package file (__init__.py)
- 2 utility files (.sh, .py)
- 1 manifest file (this file)

### Ignored Files (5 files)
Generated artifacts are gitignored (see .gitignore):
- COHORT_2024_canonical_method_inventory.json
- COHORT_2024_method_signatures.json
- COHORT_2024_calibration_coverage_matrix.json
- COHORT_2024_consolidation_summary.md
- calibration_consolidation.log

## File Counts

```
Total files in directory:        18 (13 tracked + 5 generated)
Documentation:                    6 (.md files)
Python scripts:                   6 (.py files)
Shell scripts:                    1 (.sh file)
Generated artifacts:              5 (JSON + MD + log)
```

## Size Estimates

```
Source Code:
  Python scripts:                 ~1,500 lines total
  Documentation:                  ~2,000 lines total
  
Generated Artifacts:
  JSON files:                     6-16 MB total
  Markdown report:                10-20 KB
  Log file:                       50-200 KB
  
Total directory size:             6-20 MB (with artifacts)
```

## Integration Points

### Input Sources
1. **Codebase:** src/, tests/ directories
2. **Calibration Configs:** COHORT_2024_intrinsic_calibration.json, method_compatibility.json
3. **Layer Requirements:** COHORT_2024_layer_requirements.json

### Output Consumers
1. **Calibration Orchestrator:** src/orchestration/calibration_orchestrator.py
2. **Test Suite:** tests/calibration/
3. **Documentation Systems:** Various markdown generators
4. **Analysis Tools:** Custom analysis scripts

### Runtime Integration
- Package import: `from system.config.calibration.inventories import ...`
- CLI execution: `python3 consolidate_calibration_inventories.py`
- Shell wrapper: `./run_consolidation.sh`

## Maintenance Schedule

### Daily (During Active Development)
- Re-run consolidation after significant code changes
- Check log file for errors
- Validate artifact generation

### Weekly
- Full consolidation run
- Review coverage matrix statistics
- Update documentation if needed

### Before Major Releases
- Complete consolidation
- Validate all 3 artifacts
- Review coverage percentages
- Update version numbers

## Quality Metrics

### Code Quality
- **Typing:** Full type hints with mypy strict compliance
- **Documentation:** Comprehensive docstrings
- **Error Handling:** Try-except blocks with logging
- **Modularity:** Single responsibility principle

### Output Quality
- **Completeness:** All methods discovered and analyzed
- **Accuracy:** Correct role/layer classifications
- **Consistency:** Uniform JSON structure across artifacts
- **Traceability:** Full metadata and timestamps

### Performance
- **Scanner:** < 5 minutes for 2000+ methods
- **Extractor:** < 10 minutes for 2000+ signatures
- **Validator:** < 5 minutes for coverage matrix
- **Total:** < 20 minutes end-to-end

## Change Log

### Version 1.0.0 (2024-12-15)
- Initial implementation
- All core scripts implemented
- Complete documentation suite
- Integration with COHORT_2024 calibration system

### Planned Future Enhancements
- Parallel processing for faster scanning
- Incremental updates (only scan changed files)
- Web dashboard for coverage visualization
- Real-time monitoring integration
- Automated regression detection

## Support and Contact

**Documentation Issues:** Check README.md and SYSTEM_OVERVIEW.md  
**Script Errors:** Review calibration_consolidation.log  
**Integration Questions:** See SYSTEM_OVERVIEW.md integration section  
**Validation:** Run test_inventory_system.py before consolidation

---

**Manifest Version:** 1.0.0  
**Last Updated:** 2024-12-15  
**Maintained By:** F.A.R.F.A.N Calibration Team  
**Repository:** COHORT_2024 Calibration Framework
