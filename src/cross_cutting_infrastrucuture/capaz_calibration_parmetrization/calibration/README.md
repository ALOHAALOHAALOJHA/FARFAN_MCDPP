# COHORT_2024 Calibration Inventories

This directory contains the authoritative calibration inventory system for the COHORT_2024 calibration framework.

## Overview

The calibration inventory system provides three critical artifacts that track the complete state of method calibration across the F.A.R.F.A.N pipeline:

1. **Canonical Method Inventory** - Complete registry of all methods
2. **Method Signatures** - Parametrization specifications  
3. **Calibration Coverage Matrix** - Layer-wise calibration status

## Directory Structure

```
system/config/calibration/inventories/
├── README.md                                           # This file
├── consolidate_calibration_inventories.py             # Main orchestrator script
├── scan_methods_inventory.py                          # Method discovery scanner
├── method_signature_extractor.py                      # Parametrization analyzer
├── calibration_coverage_validator.py                  # Coverage matrix generator
├── COHORT_2024_canonical_method_inventory.json        # Output: Method inventory
├── COHORT_2024_method_signatures.json                 # Output: Signatures
├── COHORT_2024_calibration_coverage_matrix.json       # Output: Coverage matrix
└── COHORT_2024_consolidation_summary.md               # Output: Summary report
```

## Artifacts

### 1. COHORT_2024_canonical_method_inventory.json

**Purpose:** Complete inventory of all methods in the codebase (target: 1995+ methods)

**Structure:**
```json
{
  "_cohort_metadata": {
    "cohort_id": "COHORT_2024",
    "creation_date": "...",
    "wave_version": "REFACTOR_WAVE_2024_12"
  },
  "metadata": {
    "scan_timestamp": "...",
    "total_methods": 2000,
    "scanned_directories": ["src", "tests"]
  },
  "methods": {
    "MODULE:CLASS.METHOD@LAYER": {
      "method_id": "CLASS.METHOD",
      "module_path": "...",
      "class_name": "...",
      "method_name": "...",
      "role": "SCORE_Q|INGEST_PDM|STRUCTURE|...",
      "layers": ["@b", "@q", "@d", ...],
      "file_path": "...",
      "line_number": 123,
      "docstring": "...",
      "parameters": [...],
      "returns": "..."
    }
  }
}
```

**Method Notation:** `MODULE:CLASS.METHOD@LAYER`
- Example: `farfan_pipeline.core.calibration:CalibrationOrchestrator.calibrate@b,chain,u,m`

**Role Classifications:**
- `SCORE_Q` - Question scoring methods
- `INGEST_PDM` - Policy document ingestion
- `STRUCTURE` - Structuring/organization
- `EXTRACT` - Data extraction
- `AGGREGATE` - Aggregation methods
- `REPORT` - Reporting/output
- `META_TOOL` - Meta-analysis tools
- `TRANSFORM` - Transformation methods

### 2. COHORT_2024_method_signatures.json

**Purpose:** Detailed parametrization specifications for each method

**Structure:**
```json
{
  "_cohort_metadata": {...},
  "metadata": {
    "extraction_timestamp": "...",
    "total_signatures": 2000
  },
  "signatures": {
    "MODULE:CLASS.METHOD@LAYER": {
      "required_inputs": [
        {
          "name": "param1",
          "type": "str",
          "description": "..."
        }
      ],
      "optional_inputs": [
        {
          "name": "param2",
          "type": "int",
          "default": 10,
          "description": "..."
        }
      ],
      "output_type": "Dict[str, Any]",
      "method_id": "CLASS.METHOD",
      "role": "SCORE_Q",
      "layers": ["@b", "@q", "@d"]
    }
  }
}
```

### 3. COHORT_2024_calibration_coverage_matrix.json

**Purpose:** Cross-reference of all methods with their calibration status across 8 layers

**Structure:**
```json
{
  "_cohort_metadata": {...},
  "metadata": {...},
  "statistics": {
    "total_methods": 2000,
    "fully_calibrated": 150,
    "partially_calibrated": 850,
    "not_calibrated": 1000,
    "calibration_percentage": 7.5,
    "per_layer_coverage": {
      "@b": {"computed": 500, "pending": 1500, "percentage": 25.0},
      "@q": {"computed": 200, "pending": 1800, "percentage": 10.0},
      ...
    },
    "per_role_coverage": {
      "SCORE_Q": {"total": 300, "calibrated": 50}
    }
  },
  "coverage_matrix": {
    "MODULE:CLASS.METHOD@LAYER": {
      "method_id": "CLASS.METHOD",
      "role": "SCORE_Q",
      "required_layers": ["@b", "@q", "@d", "@p", "@C", "@chain", "@u", "@m"],
      "calibration_status": {
        "@b": "computed",
        "@q": "pending",
        "@d": "pending",
        "@p": "pending",
        "@C": "pending",
        "@chain": "pending",
        "@u": "pending",
        "@m": "pending"
      },
      "layer_scores": {
        "@b": 0.7,
        "@q": null,
        ...
      },
      "overall_status": "partially_calibrated"
    }
  },
  "layer_definitions": {
    "@b": "Base Layer",
    "@q": "Question Layer",
    ...
  }
}
```

**Calibration Status Values:**
- `computed` - Layer score has been calculated
- `pending` - Layer score needs computation

**Overall Status:**
- `fully_calibrated` - All 8 layers computed
- `partially_calibrated` - Some layers computed
- `not_calibrated` - No layers computed

## 8-Layer Calibration System

| Symbol | Name | Description |
|--------|------|-------------|
| `@b` | Base Layer | Intrinsic quality of method code (theory, implementation, deployment) |
| `@q` | Question Layer | Compatibility with specific questionnaire questions |
| `@d` | Dimension Layer | Compatibility with policy dimensions |
| `@p` | Policy Layer | Compatibility with policy areas |
| `@C` | Congruence Layer | Cross-method consistency and coherence |
| `@chain` | Chain Layer | Method chaining and pipeline compatibility |
| `@u` | Unit Layer | Unit test coverage and validation status |
| `@m` | Meta Layer | Meta-analysis and reflection capabilities |

## Usage

### Full Consolidation

Run the complete consolidation process to generate all three artifacts:

```bash
python system/config/calibration/inventories/consolidate_calibration_inventories.py
```

This will:
1. Scan the codebase for all methods
2. Extract parametrization signatures
3. Generate calibration coverage matrix
4. Create summary report

### Individual Scripts

Run individual components as needed:

```bash
# 1. Scan methods only
python system/config/calibration/inventories/scan_methods_inventory.py

# 2. Extract signatures only (requires inventory)
python system/config/calibration/inventories/method_signature_extractor.py

# 3. Generate coverage matrix only (requires inventory)
python system/config/calibration/inventories/calibration_coverage_validator.py
```

### Integration with Calibration System

The inventories integrate with the calibration system located at:
```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/
├── COHORT_2024_intrinsic_calibration.json      # Base layer (@b) config
├── COHORT_2024_method_compatibility.json       # Contextual layer compatibility
├── COHORT_2024_layer_requirements.json         # Role-based layer requirements
└── ...
```

## Output

After running consolidation, you'll have:

1. **JSON Artifacts** - Three authoritative inventory files
2. **Summary Report** - Markdown report with statistics
3. **Log File** - `calibration_consolidation.log` with detailed execution trace

## Maintenance

### When to Regenerate

Regenerate inventories when:
- New methods are added to codebase
- Method signatures change
- Calibration scores are updated
- Layer requirements change

### Validation

Check inventory completeness:
- Total methods should be 1995+ 
- Parametrization coverage should approach 100%
- Review methods with `pending` calibration status

### Extending

To extend the system:
- **Add new layers:** Update `LAYER_SYMBOLS` in validators
- **Add new roles:** Update `ROLE_KEYWORDS` in scanner
- **Custom analysis:** Add new scripts following existing patterns

## References

- **Source Configs:** `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/`
- **Orchestrator:** `src/orchestration/calibration_orchestrator.py`
- **Tests:** `tests/calibration/`
- **Documentation:** `src/orchestration/UNIT_LAYER_README.md`, `LAYER_VERSIONING_README.md`

## Support

For issues or questions:
1. Check `calibration_consolidation.log` for detailed errors
2. Review `COHORT_2024_consolidation_summary.md` for statistics
3. Validate source calibration configs exist and are well-formed
4. Ensure Python 3.12+ and all dependencies installed

---

*Part of the COHORT_2024 Calibration Framework - REFACTOR_WAVE_2024_12*
