# COHORT_2024 Calibration Inventory System - Complete Overview

## Executive Summary

The COHORT_2024 Calibration Inventory System provides comprehensive tracking and validation of the 8-layer calibration framework across all methods in the F.A.R.F.A.N policy analysis pipeline. This system consolidates three critical artifacts that serve as the authoritative source of truth for method discovery, parametrization analysis, and calibration coverage.

**Target:** 1995+ methods with complete layer-wise calibration tracking  
**Wave:** REFACTOR_WAVE_2024_12  
**Location:** `system/config/calibration/inventories/`

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COHORT_2024 CALIBRATION SYSTEM                   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
        ┌──────────────────────────────────────────────────┐
        │   Calibration Inventory Consolidation System     │
        │   (system/config/calibration/inventories/)       │
        └──────────────────────────────────────────────────┘
                                   │
        ┌──────────────┬───────────┴──────────┬────────────────┐
        ▼              ▼                      ▼                ▼
  ┌──────────┐  ┌──────────┐         ┌──────────┐     ┌──────────┐
  │  Scanner │  │Signature │         │ Coverage │     │Consolidate│
  │  Script  │  │Extractor │         │Validator │     │   Script  │
  └──────────┘  └──────────┘         └──────────┘     └──────────┘
        │              │                      │                │
        ▼              ▼                      ▼                ▼
  ┌──────────┐  ┌──────────┐         ┌──────────┐     ┌──────────┐
  │ Artifact │  │ Artifact │         │ Artifact │     │ Summary  │
  │    1     │  │    2     │         │    3     │     │  Report  │
  └──────────┘  └──────────┘         └──────────┘     └──────────┘
  Canonical     Method               Coverage          Markdown
  Inventory     Signatures           Matrix            Statistics
```

## Three Critical Artifacts

### Artifact 1: Canonical Method Inventory
**File:** `COHORT_2024_canonical_method_inventory.json`

Complete registry of all discovered methods with:
- **Full Notation:** `MODULE:CLASS.METHOD@LAYER` format
- **Role Classification:** SCORE_Q, INGEST_PDM, STRUCTURE, EXTRACT, AGGREGATE, REPORT, META_TOOL, TRANSFORM
- **Layer Annotations:** Which of the 8 layers (@b, @q, @d, @p, @C, @chain, @u, @m) apply
- **Source Metadata:** File path, line number, docstring, parameters

**Example Entry:**
```json
"farfan_pipeline.core.calibration:CalibrationOrchestrator.calibrate@b,chain,u,m": {
  "method_id": "CalibrationOrchestrator.calibrate",
  "module_path": "farfan_pipeline.core.calibration",
  "class_name": "CalibrationOrchestrator",
  "method_name": "calibrate",
  "role": "SCORE_Q",
  "layers": ["@b", "@chain", "@u", "@m"],
  "file_path": "src/farfan_pipeline/core/calibration.py",
  "line_number": 156,
  "docstring": "Calibrates method with 8-layer system...",
  "parameters": ["subject", "evidence", "context"],
  "returns": "CalibrationResult"
}
```

### Artifact 2: Method Signatures
**File:** `COHORT_2024_method_signatures.json`

Detailed parametrization specifications with:
- **required_inputs:** Mandatory parameters with types and descriptions
- **optional_inputs:** Optional parameters with defaults
- **output_type:** Return type annotation
- **Integration info:** Role and layer associations

**Example Entry:**
```json
"farfan_pipeline.core.calibration:CalibrationOrchestrator.calibrate@b,chain,u,m": {
  "required_inputs": [
    {
      "name": "subject",
      "type": "CalibrationSubject",
      "description": "Method to calibrate with role and context"
    },
    {
      "name": "evidence",
      "type": "EvidenceStore",
      "description": "Evidence data for calibration"
    }
  ],
  "optional_inputs": [
    {
      "name": "context",
      "type": "Dict[str, Any]",
      "default": {},
      "description": "Additional context information"
    }
  ],
  "output_type": "CalibrationResult",
  "method_id": "CalibrationOrchestrator.calibrate",
  "role": "SCORE_Q",
  "layers": ["@b", "@chain", "@u", "@m"]
}
```

### Artifact 3: Calibration Coverage Matrix
**File:** `COHORT_2024_calibration_coverage_matrix.json`

Comprehensive layer-wise calibration status with:
- **Layer Scores:** Actual computed scores for each of 8 layers
- **Calibration Status:** `computed` vs `pending` for each layer
- **Overall Status:** `fully_calibrated`, `partially_calibrated`, `not_calibrated`
- **Statistics:** Coverage percentages per layer and per role

**Example Entry:**
```json
"farfan_pipeline.core.calibration:CalibrationOrchestrator.calibrate@b,chain,u,m": {
  "method_id": "CalibrationOrchestrator.calibrate",
  "role": "SCORE_Q",
  "required_layers": ["@b", "@chain", "@u", "@m"],
  "calibration_status": {
    "@b": "computed",
    "@q": "pending",
    "@d": "pending",
    "@p": "pending",
    "@C": "pending",
    "@chain": "computed",
    "@u": "computed",
    "@m": "computed"
  },
  "layer_scores": {
    "@b": 0.85,
    "@q": null,
    "@d": null,
    "@p": null,
    "@C": null,
    "@chain": 0.92,
    "@u": 0.78,
    "@m": 0.88
  },
  "overall_status": "partially_calibrated"
}
```

## The 8-Layer Calibration Framework

| Layer | Symbol | Name | Description | Data Source |
|-------|--------|------|-------------|-------------|
| 1 | `@b` | Base Layer | Intrinsic code quality (theory, implementation, deployment) | intrinsic_calibration.json |
| 2 | `@q` | Question Layer | Compatibility with questionnaire questions | method_compatibility.json |
| 3 | `@d` | Dimension Layer | Compatibility with policy dimensions | method_compatibility.json |
| 4 | `@p` | Policy Layer | Compatibility with policy areas | method_compatibility.json |
| 5 | `@C` | Congruence Layer | Cross-method consistency | congruence layer scripts |
| 6 | `@chain` | Chain Layer | Pipeline/workflow compatibility | chain layer scripts |
| 7 | `@u` | Unit Layer | Test coverage and validation | unit layer scripts |
| 8 | `@m` | Meta Layer | Meta-analysis capabilities | meta layer scripts |

## Role-Based Layer Requirements

Different method roles require different layers:

| Role | Required Layers |
|------|-----------------|
| **SCORE_Q** | All 8 layers (@b, @q, @d, @p, @C, @chain, @u, @m) |
| **INGEST_PDM** | @b, @chain, @u, @m |
| **STRUCTURE** | @b, @chain, @u, @m |
| **EXTRACT** | @b, @chain, @u, @m |
| **AGGREGATE** | @b, @chain, @u, @m |
| **REPORT** | @b, @chain, @u, @m |
| **META_TOOL** | @b, @chain, @u, @m |
| **TRANSFORM** | @b, @chain, @u, @m |

## Component Scripts

### 1. scan_methods_inventory.py
**Purpose:** Discovers all methods in codebase

**Process:**
1. Recursively scans configured directories (src/, tests/)
2. Parses Python files using AST
3. Extracts methods with class/module context
4. Classifies roles based on name/docstring analysis
5. Detects layer annotations in docstrings
6. Generates MODULE:CLASS.METHOD@LAYER notation
7. Outputs canonical inventory JSON

**Output:** `COHORT_2024_canonical_method_inventory.json`

### 2. method_signature_extractor.py
**Purpose:** Analyzes method parametrization

**Process:**
1. Loads canonical inventory
2. For each method, parses source file AST
3. Extracts parameter types, defaults, descriptions
4. Identifies required vs optional inputs
5. Extracts return type annotations
6. Cross-references with docstrings
7. Outputs signature specifications

**Output:** `COHORT_2024_method_signatures.json`

### 3. calibration_coverage_validator.py
**Purpose:** Validates calibration completeness

**Process:**
1. Loads canonical inventory
2. Loads intrinsic_calibration.json (@b layer data)
3. Loads method_compatibility.json (@q, @d, @p layer data)
4. For each method, checks all 8 layers
5. Determines if layer score is computed or pending
6. Calculates coverage statistics
7. Generates comprehensive coverage matrix

**Output:** `COHORT_2024_calibration_coverage_matrix.json`

### 4. consolidate_calibration_inventories.py
**Purpose:** Orchestrates complete process

**Process:**
1. Runs scanner → generates Artifact 1
2. Runs signature extractor → generates Artifact 2
3. Runs coverage validator → generates Artifact 3
4. Generates summary report with statistics
5. Creates log file with execution trace

**Outputs:** 
- All 3 artifacts
- `COHORT_2024_consolidation_summary.md`
- `calibration_consolidation.log`

## Usage Patterns

### Initial Setup
```bash
cd system/config/calibration/inventories
python3 consolidate_calibration_inventories.py
```

### Incremental Updates
```bash
# After adding new methods
python3 scan_methods_inventory.py

# After updating signatures
python3 method_signature_extractor.py

# After running calibrations
python3 calibration_coverage_validator.py
```

### Integration with Calibration Pipeline
```python
from system.config.calibration.inventories.calibration_coverage_validator import (
    CalibrationCoverageValidator
)

# Load coverage matrix
validator = CalibrationCoverageValidator(
    inventory_path=Path("COHORT_2024_canonical_method_inventory.json"),
    intrinsic_calibration_path=Path("..."),
    method_compatibility_path=Path("...")
)

coverage_matrix = validator.generate_coverage_matrix()

# Find methods needing calibration
for method_id, data in coverage_matrix['coverage_matrix'].items():
    if data['overall_status'] == 'not_calibrated':
        print(f"TODO: Calibrate {method_id}")
```

## Data Flow

```
Codebase (src/, tests/)
    │
    ▼
[scan_methods_inventory.py]
    │
    ▼
Artifact 1: canonical_method_inventory.json
    │
    ├─────────────────────────────────┐
    ▼                                 ▼
[method_signature_extractor.py]    [calibration_coverage_validator.py]
    │                                 │
    │                                 ├── intrinsic_calibration.json
    │                                 └── method_compatibility.json
    ▼                                 ▼
Artifact 2: method_signatures.json  Artifact 3: calibration_coverage_matrix.json
    │                                 │
    └─────────────┬───────────────────┘
                  ▼
         [consolidate_calibration_inventories.py]
                  │
                  ▼
         COHORT_2024_consolidation_summary.md
```

## Integration Points

### Source Calibration Configurations
Located: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/`

Key files:
- `COHORT_2024_intrinsic_calibration.json` - Base layer (@b) rubric and scores
- `COHORT_2024_method_compatibility.json` - Contextual layer (@q, @d, @p) scores
- `COHORT_2024_layer_requirements.json` - Role-based layer requirements
- `COHORT_2024_fusion_weights.json` - Choquet aggregation weights

### Calibration Orchestrator
Main runtime: `src/orchestration/calibration_orchestrator.py`

The orchestrator uses these inventories to:
1. Determine which layers to compute for a given method/role
2. Load pre-computed scores from calibration configs
3. Execute calibration computations for pending layers
4. Aggregate scores using Choquet fusion

### Test Suite
Location: `tests/calibration/`

Tests validate:
- Inventory completeness (all methods discovered)
- Signature correctness (types match implementations)
- Coverage accuracy (scores correctly mapped)
- Integration with orchestrator

## Maintenance

### When to Regenerate

**Always regenerate after:**
- Adding new Python files/modules
- Adding new methods to existing classes
- Changing method signatures
- Running new calibration computations
- Updating layer configurations

**Frequency:**
- Daily during active development
- Weekly during maintenance
- Before major releases
- After refactoring waves

### Validation Checklist

✅ Total methods ≥ 1995  
✅ Parametrization coverage ≥ 95%  
✅ All roles represented  
✅ Layer annotations present  
✅ Coverage matrix statistics valid  
✅ No parsing errors in log  
✅ Summary report generated  

### Quality Metrics

**Completeness:**
- Method discovery rate: % of actual methods found
- Signature extraction rate: % of methods with full signatures
- Calibration coverage: % of methods fully calibrated

**Accuracy:**
- Role classification accuracy: % correctly classified
- Layer annotation accuracy: % correct layer assignments
- Score mapping accuracy: % scores correctly loaded

**Performance:**
- Scan time: < 5 minutes for full codebase
- Extraction time: < 10 minutes
- Validation time: < 5 minutes
- Total consolidation: < 20 minutes

## Troubleshooting

### Issue: "0 methods discovered"
**Cause:** Scanner can't find source directories  
**Fix:** Verify src/ exists, check scanner src_dirs config

### Issue: "Signature extraction failed"
**Cause:** Source files moved or deleted since inventory scan  
**Fix:** Re-run scanner first, then extractor

### Issue: "Coverage shows 0% calibration"
**Cause:** No calibration computations run yet (normal for first run)  
**Fix:** Run layer-specific calibration scripts, then re-consolidate

### Issue: "Import errors during consolidation"
**Cause:** Missing dependencies or incorrect PYTHONPATH  
**Fix:** Ensure virtual env active, install dependencies

### Issue: "JSON parsing errors"
**Cause:** Malformed source calibration configs  
**Fix:** Validate source JSON files, check for syntax errors

## Extension Points

### Adding New Layers
1. Update `LAYER_SYMBOLS` in validators
2. Add layer definition to `LAYER_NAMES`
3. Update coverage validator logic
4. Update documentation

### Adding New Roles
1. Update `ROLE_KEYWORDS` in scanner
2. Add role requirements to `ROLE_LAYER_REQUIREMENTS`
3. Update role-based statistics
4. Update documentation

### Custom Analysis Scripts
Create scripts following pattern:
```python
from pathlib import Path
import json

# Load artifact
with open('COHORT_2024_canonical_method_inventory.json') as f:
    inventory = json.load(f)

# Analyze
for method_id, data in inventory['methods'].items():
    # Custom analysis logic
    pass
```

## References

### Documentation
- **Main README:** `system/config/calibration/inventories/README.md`
- **Quick Start:** `system/config/calibration/inventories/QUICK_START.md`
- **This Document:** `system/config/calibration/inventories/SYSTEM_OVERVIEW.md`

### Source Code
- **Scanner:** `scan_methods_inventory.py`
- **Extractor:** `method_signature_extractor.py`
- **Validator:** `calibration_coverage_validator.py`
- **Orchestrator:** `consolidate_calibration_inventories.py`

### Related Systems
- **Calibration Framework:** `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/`
- **Orchestrator:** `src/orchestration/calibration_orchestrator.py`
- **Layer Implementations:** Various layer-specific scripts
- **Tests:** `tests/calibration/`

### Standards
- **Notation:** MODULE:CLASS.METHOD@LAYER
- **Layer Symbols:** @b, @q, @d, @p, @C, @chain, @u, @m
- **Roles:** SCORE_Q, INGEST_PDM, STRUCTURE, EXTRACT, AGGREGATE, REPORT, META_TOOL, TRANSFORM
- **Status Values:** computed, pending, fully_calibrated, partially_calibrated, not_calibrated

---

**Version:** 1.0.0  
**Cohort:** COHORT_2024  
**Wave:** REFACTOR_WAVE_2024_12  
**Last Updated:** 2024-12-15  
**Authority:** F.A.R.F.A.N Calibration Team
