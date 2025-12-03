# Methods Inventory System

## Overview

The Methods Inventory System provides comprehensive AST-based method scanning with canonical identifier enforcement, role classification, and epistemological tagging for the FARFAN pipeline. It integrates with the existing `src/farfan_pipeline/core/method_inventory.py` type system while providing an extended scanning workflow.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     METHODS INVENTORY WORKFLOW                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [scan_methods_inventory.py]                                    │
│           │                                                     │
│           │  AST Parsing + Role Classification                  │
│           │  Epistemological Rubric + Deduplication             │
│           ↓                                                     │
│  [methods_inventory_raw.json]                                   │
│           │                                                     │
│           │  2093 methods, 9 roles, epistemology tags           │
│           ↓                                                     │
│  [verify_inventory.py]                                          │
│           │                                                     │
│           │  12 verification tests                              │
│           ↓                                                     │
│  ✓ VERIFICATION PASSED                                          │
│                                                                 │
│  Integration Layer:                                             │
│  • src/farfan_pipeline/core/method_inventory_types.py          │
│  • src/farfan_pipeline/core/method_inventory.py                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Files

### 1. `scan_methods_inventory.py`
**Purpose**: Main AST scanner that traverses `src/farfan_pipeline/` and generates the inventory.

**Key Features**:
- Recursively scans all Python files in the pipeline
- Extracts ALL methods with canonical identifier format: `module.Class.method`
- Classifies methods by role using extended LAYER_REQUIREMENTS table
- Applies epistemological rubric to set calibration/parametrization flags
- Handles duplicate function definitions by appending line numbers (`@L{line_number}`)
- Filters nested functions (only top-level class methods and module functions)
- Verifies critical methods (derek_beach.py, aggregation.py, executors.py)

**Usage**:
```bash
# Direct execution
python scan_methods_inventory.py

# Via CLI entrypoint (after pip install -e .)
farfan-scan-inventory

# Output
methods_inventory_raw.json
```

**Output**: `methods_inventory_raw.json` (1.2MB, 2093 methods)

**Failure Conditions**:
- Aborts if fewer than 200 methods found (insufficient coverage)
- Aborts if critical pipeline methods cannot be located
- Exits with non-zero status code on failure

### 2. `methods_inventory_raw.json`
**Purpose**: Complete inventory of all pipeline methods in JSON format.

**Schema Structure**:
```json
{
  "metadata": {
    "total_methods": 2093,
    "scan_timestamp": null,
    "source_directory": "src/farfan_pipeline"
  },
  "layer_requirements": {
    "ingest": {
      "description": "Data ingestion and document parsing",
      "typical_patterns": ["parse", "load", "read", "extract_raw", "ingest"]
    },
    "processor": {
      "description": "Data transformation and processing",
      "typical_patterns": ["process", "transform", "clean", "normalize", "aggregate"]
    },
    "analyzer": {
      "description": "Analysis and inference operations",
      "typical_patterns": ["analyze", "infer", "calculate", "compute", "assess"]
    },
    "extractor": {
      "description": "Feature and information extraction",
      "typical_patterns": ["extract", "identify", "detect", "find", "locate"]
    },
    "score": {
      "description": "Scoring and evaluation methods",
      "typical_patterns": ["score", "evaluate", "rate", "rank", "measure"]
    },
    "utility": {
      "description": "Helper and utility functions",
      "typical_patterns": ["_format", "_helper", "_validate", "_check", "_get", "_set"]
    },
    "orchestrator": {
      "description": "Workflow orchestration and coordination",
      "typical_patterns": ["orchestrate", "coordinate", "run", "execute_suite", "build"]
    },
    "core": {
      "description": "Core framework methods",
      "typical_patterns": ["__init__", "setup", "initialize", "configure"]
    },
    "executor": {
      "description": "Executor pattern implementations",
      "typical_patterns": ["execute", "run_executor", "perform", "apply"]
    }
  },
  "methods": [
    {
      "canonical_identifier": "module.Class.method",
      "module_path": "farfan_pipeline.analysis.derek_beach",
      "class_name": "BeachEvidentialTest",
      "method_name": "classify_test",
      "role": "analyzer",
      "requiere_calibracion": true,
      "requiere_parametrizacion": true,
      "is_async": false,
      "is_property": false,
      "is_classmethod": false,
      "is_staticmethod": false,
      "line_number": 123,
      "source_file": "src/farfan_pipeline/analysis/derek_beach.py",
      "epistemology_tags": ["evaluative_judgment", "transformation"]
    }
  ],
  "statistics": {
    "by_role": {
      "core": 1041,
      "utility": 279,
      "executor": 160,
      "analyzer": 148,
      "extractor": 121,
      "score": 95,
      "ingest": 93,
      "orchestrator": 87,
      "processor": 69
    },
    "by_file": {
      "derek_beach.py": 181,
      "aggregation.py": 48,
      "executors.py": 42,
      "...": "..."
    },
    "requiring_calibration": 227,
    "requiring_parametrization": 198
  }
}
```

### 3. `verify_inventory.py`
**Purpose**: Standalone verification script (no pytest dependency).

**Verification Tests**:
1. ✓ **Minimum method count**: Verifies at least 200 methods (found 2093)
2. ✓ **Critical files present**: Ensures derek_beach.py, aggregation.py, executors.py, executors_contract.py
3. ✓ **Critical method patterns**: Confirms patterns like "derek_beach", "aggregation", "executors"
4. ✓ **All roles present**: Validates all 9 roles in inventory
5. ✓ **Calibration flags set**: Ensures methods flagged for calibration (227) and parametrization (198)
6. ✓ **Canonical identifier format**: Validates `module.Class.method` format
7. ✓ **Epistemology tags present**: Confirms 41.71% coverage (873/2093 methods)
8. ✓ **derek_beach methods complete**: Validates 181 methods including required patterns
9. ✓ **aggregation classes present**: Confirms DimensionAggregator, ClusterAggregator, AreaPolicyAggregator
10. ✓ **executor methods present**: Validates executor implementations
11. ✓ **No duplicate canonical IDs**: Ensures uniqueness (duplicates resolved via @L line numbers)
12. ✓ **LAYER_REQUIREMENTS complete**: Validates 9-layer classification table

**Usage**:
```bash
# Direct execution
python verify_inventory.py

# Via CLI entrypoint (after pip install -e .)
farfan-verify-inventory

# Exit codes
0 = All tests passed
1 = One or more tests failed
```

**Output Example**:
```
======================================================================
INVENTORY COMPLETENESS VERIFICATION
======================================================================

PASS: Minimum method count
      ✓ Method count: 2093 >= 200

PASS: Critical files present
      ✓ All 4 critical files present

...

======================================================================
RESULTS: 12 passed, 0 failed
======================================================================

✓✓✓ ALL TESTS PASSED ✓✓✓
```

## CLI Entrypoints

The system provides two CLI entrypoints defined in `pyproject.toml`:

```toml
[project.scripts]
farfan-scan-inventory = "scan_methods_inventory:main"
farfan-verify-inventory = "verify_inventory:main"
```

**Installation**:
```bash
pip install -e .
```

**Usage**:
```bash
# Scan and generate inventory
farfan-scan-inventory

# Verify inventory completeness
farfan-verify-inventory

# Combined workflow
farfan-scan-inventory && farfan-verify-inventory
```

## Scanner Workflow

### Phase 1: AST Parsing
1. Recursively discover all `*.py` files in `src/farfan_pipeline/`
2. Parse each file into an AST using `ast.parse()`
3. Extract module path from file path (e.g., `src/farfan_pipeline/analysis/derek_beach.py` → `farfan_pipeline.analysis.derek_beach`)

### Phase 2: Method Extraction
1. Traverse AST to find all `ClassDef`, `FunctionDef`, and `AsyncFunctionDef` nodes
2. Extract top-level methods only (skip nested functions)
3. Build canonical identifier: `{module_path}.{ClassName}.{method_name}` or `{module_path}.{function_name}`
4. Capture metadata: line number, decorators (property, classmethod, staticmethod), async status

### Phase 3: Role Classification
The scanner classifies methods into 9 roles using heuristics:

1. **Method name patterns**: `parse` → ingest, `score` → score, `execute` → executor
2. **Class name patterns**: `*Executor` → executor, `*Analyzer` → analyzer
3. **Private methods**: Methods starting with `_` → utility
4. **Special methods**: `__init__`, `__repr__` → core
5. **Default**: If no patterns match → core

**Classification Heuristics**:
```python
# Pattern matching (case-insensitive)
if "score" in method_name.lower():
    role = "score"
elif "parse" in method_name.lower() or "load" in method_name.lower():
    role = "ingest"
elif "analyze" in method_name.lower():
    role = "analyzer"
elif "extract" in method_name.lower():
    role = "extractor"
elif "process" in method_name.lower() or "transform" in method_name.lower():
    role = "processor"
elif "execute" in method_name.lower():
    role = "executor"
elif "orchestrate" in method_name.lower() or "coordinate" in method_name.lower():
    role = "orchestrator"
elif method_name.startswith("_"):
    role = "utility"
else:
    role = "core"
```

### Phase 4: Epistemological Rubric
The scanner applies an epistemological rubric to classify methods:

**Epistemology Tags**:
- **evaluative_judgment**: Methods that score/evaluate/assess/judge/validate
- **transformation**: Methods that calculate/compute/infer/estimate/analyze/transform
- **statistical**: Methods involving probability/likelihood/confidence/threshold
- **causal**: Methods dealing with causal relationships
- **bayesian**: Methods using Bayesian inference
- **normative**: Score-role methods applying normative standards
- **structural**: Ingest-role methods parsing structural data
- **semantic**: Extractor-role methods extracting semantic meaning
- **constructive**: Methods that build/create/generate
- **consistency**: Methods that check/verify/assert
- **descriptive**: Methods that format/render/export

**Calibration Flags**:
```python
# requiere_calibracion = True if:
# - Method is evaluative (score/evaluate/assess), OR
# - Method is statistical AND has direct impact (analyzer/processor/score/executor role)
# - Excludes utility methods and special methods (__init__, __repr__, __str__)

# requiere_parametrizacion = True if:
# - Method is transformation (calculate/compute/transform), OR
# - Method is statistical, OR
# - Method role is analyzer
# - Excludes utility methods and special methods
```

### Phase 5: Deduplication
If multiple methods have the same canonical identifier (e.g., due to monkeypatching or conditional definitions):
1. Detect duplicates by counting occurrences
2. Append line number to canonical ID: `module.Class.method@L123`
3. Ensure all IDs are unique

### Phase 6: Verification
Before writing output:
1. **Coverage check**: Abort if fewer than 200 methods found
2. **Critical method check**: Verify methods from derek_beach.py, aggregation.py, executors.py are present
3. **Pattern verification**: Ensure critical patterns like "derek_beach", "aggregation", "executors" exist

### Phase 7: Output Generation
Generate `methods_inventory_raw.json` with:
- Metadata (total count, source directory)
- Layer requirements table
- Full method list with all metadata
- Statistics (by role, by file, calibration counts)

## Canonical ID Format

All methods follow the strict format: **`module.Class.method`**

### Format Rules

1. **Module-level functions**: `{module_path}.{function_name}`
   - Example: `farfan_pipeline.utils.helpers.format_date`

2. **Class methods**: `{module_path}.{ClassName}.{method_name}`
   - Example: `farfan_pipeline.analysis.derek_beach.BeachEvidentialTest.classify_test`

3. **Nested classes**: `{module_path}.{OuterClass}.{InnerClass}.{method_name}`
   - Example: `farfan_pipeline.core.types.Config.Nested.validate`

4. **Duplicate resolution**: `{canonical_id}@L{line_number}`
   - Example: `farfan_pipeline.entrypoint.main.cli@L543`

### Module Path Derivation

Module paths are derived from file paths relative to `src/`:
```
src/farfan_pipeline/analysis/derek_beach.py
→ farfan_pipeline.analysis.derek_beach

src/farfan_pipeline/core/orchestrator/executors.py
→ farfan_pipeline.core.orchestrator.executors
```

## Output File Schemas

### MethodMetadata Schema

```typescript
interface MethodMetadata {
  canonical_identifier: string;      // "module.Class.method" or "module.Class.method@L123"
  module_path: string;                // "farfan_pipeline.analysis.derek_beach"
  class_name: string | null;          // "BeachEvidentialTest" or null for functions
  method_name: string;                // "classify_test"
  role: string;                       // One of 9 roles (see LAYER_REQUIREMENTS)
  requiere_calibracion: boolean;      // True if method needs calibration
  requiere_parametrizacion: boolean;  // True if method needs parametrization
  is_async: boolean;                  // True for async def methods
  is_property: boolean;               // True for @property decorated methods
  is_classmethod: boolean;            // True for @classmethod decorated methods
  is_staticmethod: boolean;           // True for @staticmethod decorated methods
  line_number: number;                // Starting line number in source file
  source_file: string;                // Absolute or relative path to source file
  epistemology_tags: string[];        // List of epistemology tags
}
```

### Inventory Schema

```typescript
interface MethodInventory {
  metadata: {
    total_methods: number;
    scan_timestamp: string | null;
    source_directory: string;
  };
  layer_requirements: {
    [role: string]: {
      description: string;
      typical_patterns: string[];
    };
  };
  methods: MethodMetadata[];
  statistics: {
    by_role: { [role: string]: number };
    by_file: { [filename: string]: number };
    requiring_calibration: number;
    requiring_parametrization: number;
  };
}
```

## Integration with Core Types

The scanner integrates with existing type definitions in `src/farfan_pipeline/core/`:

### Type Mapping

| Scanner Type | Core Type | Notes |
|--------------|-----------|-------|
| `canonical_identifier` | `MethodId` | NewType wrapper around str |
| `MethodMetadata` | `MethodDescriptor` | Extended schema with epistemology |
| `role` | `role` field | Both use string classification |
| `requiere_calibracion` | Implied by `governance_flags` | Scanner provides explicit flag |
| `requiere_parametrizacion` | `signature.requiere_parametrizacion` | Direct mapping |
| `source_file` + `line_number` | `LocationInfo` | Structural equivalence |

### Integration Pattern

```python
from farfan_pipeline.core.method_inventory_types import (
    MethodId,
    MethodDescriptor,
    SignatureDescriptor,
    GovernanceFlags,
    LocationInfo,
)

# Convert scanner MethodMetadata to core MethodDescriptor
def to_method_descriptor(metadata: MethodMetadata) -> MethodDescriptor:
    method_id = MethodId(metadata.canonical_identifier)
    
    signature = SignatureDescriptor(
        args=[],  # Populate from AST analysis
        kwargs=[],
        returns="Any",
        accepts_executor_config=False,
        is_async=metadata.is_async,
        requiere_parametrizacion=metadata.requiere_parametrizacion,
    )
    
    governance_flags = GovernanceFlags(
        uses_yaml=False,  # Analyze from imports
        has_hardcoded_calibration=metadata.requiere_calibracion,
        has_hardcoded_timeout=False,
        suspicious_magic_numbers=[],
        is_executor_class="executor" in metadata.role.lower(),
    )
    
    location = LocationInfo(
        file_path=metadata.source_file,
        line_start=metadata.line_number,
        line_end=metadata.line_number,  # Could be improved with end_lineno
    )
    
    return MethodDescriptor(
        method_id=method_id,
        role=metadata.role.upper(),  # Convert to uppercase convention
        aggregation_level="UNKNOWN",  # Derive from role
        module=metadata.module_path,
        class_name=metadata.class_name,
        method_name=metadata.method_name,
        signature=signature,
        governance_flags=governance_flags,
        location=location,
    )
```

## Extended LAYER_REQUIREMENTS Table

The scanner uses a 9-layer classification system:

| Role | Description | Example Patterns | Coverage |
|------|-------------|------------------|----------|
| **ingest** | Data ingestion and document parsing | parse, load, read, extract_raw, ingest | 93 methods (4.4%) |
| **processor** | Data transformation and processing | process, transform, aggregate, clean, normalize | 69 methods (3.3%) |
| **analyzer** | Analysis and inference operations | analyze, infer, calculate, compute, assess | 148 methods (7.1%) |
| **extractor** | Feature and information extraction | extract, identify, detect, find, locate | 121 methods (5.8%) |
| **score** | Scoring and evaluation methods | score, evaluate, rate, rank, measure | 95 methods (4.5%) |
| **utility** | Helper and utility functions | _format, _helper, _validate, _check, _get, _set | 279 methods (13.3%) |
| **orchestrator** | Workflow orchestration and coordination | orchestrate, coordinate, run, execute_suite, build | 87 methods (4.2%) |
| **core** | Core framework methods | __init__, setup, initialize, configure | 1041 methods (49.7%) |
| **executor** | Executor pattern implementations | execute, run_executor, perform, apply | 160 methods (7.6%) |

**Total**: 2093 methods across 9 roles

## Statistics (Latest Scan)

```
Total Methods: 2093

Role Distribution:
  core:         1041 (49.7%)  - Core framework methods
  utility:       279 (13.3%)  - Helper and utility functions
  executor:      160 (7.6%)   - Executor pattern implementations
  analyzer:      148 (7.1%)   - Analysis and inference operations
  extractor:     121 (5.8%)   - Feature and information extraction
  score:          95 (4.5%)   - Scoring and evaluation methods
  ingest:         93 (4.4%)   - Data ingestion and document parsing
  orchestrator:   87 (4.2%)   - Workflow orchestration
  processor:      69 (3.3%)   - Data transformation and processing

Calibration Flags:
  Requiring calibration:      227 (10.8%)
  Requiring parametrization:  198 (9.5%)

Epistemology Tags:
  Tagged methods:  873 (41.71%)
  Untagged methods: 1220 (58.29%)

Top Tagged Categories:
  transformation:       198 methods
  evaluative_judgment:  227 methods
  statistical:          142 methods
  semantic:             121 methods
  descriptive:          95 methods
```

## Critical Methods Verified

The scanner has verified presence of methods from:

### derek_beach.py (181 methods)
- `BeachEvidentialTest.classify_test`
- `CDAFException._format_message`
- `EvidenceType.to_dict`
- `_load_config`, `_format_message`, `classify_test` patterns verified

### aggregation.py (48 methods)
- `DimensionAggregator.aggregate_dimension`
- `ClusterAggregator.aggregate_cluster`
- `AreaPolicyAggregator.aggregate_area_policy`
- All 3 required classes verified

### executors.py (42 methods)
- Executor implementations for D1-Q1 through D6-Q5
- `execute` methods verified
- Executor contract compliance confirmed

### executors_contract.py (30 methods)
- Contract definitions verified
- Interface methods present

## Verification Requirements

All verification tests must pass:

1. **Minimum coverage**: ≥200 methods (found 2093)
2. **Critical files**: All 4 critical files present
3. **Critical patterns**: All required patterns found
4. **Role completeness**: All 9 roles present
5. **Flag accuracy**: Both calibration and parametrization flags set
6. **ID format**: All canonical IDs properly formatted
7. **Tag coverage**: Epistemology tags present (>30% coverage)
8. **File integrity**: All critical file methods present
9. **Class integrity**: All aggregation classes present
10. **Executor integrity**: Executor methods present
11. **Uniqueness**: No duplicate canonical IDs
12. **Schema completeness**: LAYER_REQUIREMENTS table complete

**All 12 tests PASSED** ✓✓✓

## Usage Instructions

### Basic Workflow

```bash
# 1. Activate virtual environment
source farfan-env/bin/activate  # or farfan-env\Scripts\activate on Windows

# 2. Scan the codebase and generate inventory
python scan_methods_inventory.py
# Output: methods_inventory_raw.json

# 3. Verify the inventory
python verify_inventory.py
# Output: Verification report with 12 tests

# 4. Check results
# Exit code 0 = success, 1 = failure
echo $?  # Unix/Linux/macOS
echo %ERRORLEVEL%  # Windows
```

### CI/CD Integration

```yaml
# .github/workflows/inventory.yml
name: Methods Inventory Validation

on: [push, pull_request]

jobs:
  inventory:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -e .
      - name: Scan inventory
        run: python scan_methods_inventory.py
      - name: Verify inventory
        run: python verify_inventory.py
      - name: Upload inventory artifact
        uses: actions/upload-artifact@v3
        with:
          name: methods-inventory
          path: methods_inventory_raw.json
```

### Integration with Existing Workflow

```bash
# Combined with existing build/lint/test
pip install -e .
python scan_methods_inventory.py
python verify_inventory.py
ruff check . && black --check . && mypy farfan_core/
python -m pytest tests/ -v
```

### Programmatic Usage

```python
from pathlib import Path
import json

# Load inventory
with open("methods_inventory_raw.json") as f:
    inventory = json.load(f)

# Query methods
methods = inventory["methods"]

# Find all executor methods
executors = [m for m in methods if m["role"] == "executor"]
print(f"Found {len(executors)} executor methods")

# Find methods requiring calibration
needs_calibration = [m for m in methods if m["requiere_calibracion"]]
print(f"Found {len(needs_calibration)} methods requiring calibration")

# Find methods by file
derek_beach_methods = [m for m in methods if "derek_beach" in m["source_file"]]
print(f"derek_beach.py has {len(derek_beach_methods)} methods")

# Get statistics
stats = inventory["statistics"]
print(f"Total methods: {inventory['metadata']['total_methods']}")
print(f"By role: {stats['by_role']}")
```

## Troubleshooting

### Issue: Fewer than 200 methods found

**Cause**: Scanner not finding source files or parsing errors

**Solution**:
1. Verify `src/farfan_pipeline/` directory exists
2. Check for syntax errors in Python files
3. Review scanner output for error messages
4. Ensure virtual environment is activated

### Issue: Critical methods missing

**Cause**: Files renamed, moved, or not in expected location

**Solution**:
1. Verify critical files exist: `ls src/farfan_pipeline/analysis/derek_beach.py`
2. Check scanner patterns match your file structure
3. Update `verify_critical_methods()` in scanner if paths changed

### Issue: Duplicate canonical IDs

**Cause**: Multiple definitions with same name (monkeypatching, conditional definitions)

**Solution**:
- Scanner automatically resolves by appending line numbers (`@L123`)
- Verify deduplication in output: `grep "@L" methods_inventory_raw.json`

### Issue: Verification fails

**Cause**: Inventory incomplete or corrupted

**Solution**:
1. Re-run scanner: `python scan_methods_inventory.py`
2. Check file size: `ls -lh methods_inventory_raw.json` (should be ~1.2MB)
3. Validate JSON: `python -m json.tool methods_inventory_raw.json > /dev/null`
4. Review specific test failures in verification output

### Issue: Integration with core types fails

**Cause**: Type mismatch or missing fields

**Solution**:
1. Review type mapping in Integration section
2. Ensure scanner output includes all required fields
3. Add conversion functions as shown in Integration Pattern
4. Run type checker: `mypy scan_methods_inventory.py`

## Maintenance

### Updating LAYER_REQUIREMENTS

To add a new role:

1. Update `LAYER_REQUIREMENTS` dict in `scan_methods_inventory.py`:
```python
LAYER_REQUIREMENTS = {
    "new_role": {
        "description": "Role description",
        "typical_patterns": ["pattern1", "pattern2"],
    },
    # ... existing roles
}
```

2. Update classification logic in `_classify_role()`:
```python
def _classify_role(self, method_name: str, class_name: str | None) -> str:
    if "new_pattern" in method_name.lower():
        return "new_role"
    # ... existing logic
```

3. Update verification tests in `verify_inventory.py`:
```python
expected_roles = [
    "ingest", "processor", "analyzer", "extractor",
    "score", "utility", "orchestrator", "core", "executor",
    "new_role"  # Add new role
]
```

### Updating Epistemological Rubric

To add a new epistemology tag:

1. Update `_apply_epistemological_rubric()` in `scan_methods_inventory.py`:
```python
if "new_keyword" in method_lower:
    epi_tags.append("new_tag")
```

2. Document the tag in this README under "Epistemological Rubric"

### Updating Critical Methods

To add a new critical file:

1. Update `critical_files` list in `verify_critical_methods()`:
```python
critical_files = [
    "derek_beach.py",
    "aggregation.py",
    "executors.py",
    "executors_contract.py",
    "new_critical_file.py",  # Add here
]
```

2. Update verification test in `verify_inventory.py`

## References

- **Type System**: `src/farfan_pipeline/core/method_inventory_types.py`
- **Core Inventory**: `src/farfan_pipeline/core/method_inventory.py`
- **Calibration Artifacts**: `src/farfan_pipeline/artifacts/calibration/method_inventory.json`
- **AGENTS.md**: Build, lint, test commands
- **pyproject.toml**: CLI entrypoint definitions

## Version History

- **v1.0** (Current): Initial release with 2093 methods, 9 roles, 41.71% epistemology coverage
- Comprehensive verification suite with 12 tests
- Integration with core type system
- CLI entrypoints for automation
