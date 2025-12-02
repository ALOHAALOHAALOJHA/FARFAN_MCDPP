# Import Contract Validator

Validates and enforces architectural import contracts for the F.A.R.F.A.N pipeline.

## Overview

This validator implements a comprehensive architectural boundary enforcement system that:

1. **Runs import-linter programmatically** via `lint-imports --config pyproject.toml`
2. **Performs AST-based import analysis** on violation-prone modules
3. **Detects violations** of all 7 architectural contracts
4. **Generates detailed reports** with specific remediation strategies
5. **Fails validation** (exit code 1) if any contract is violated

## Contracts Enforced

### 1. Core (excluding orchestrator) must not import analysis/processing/api
- **Source**: `farfan_pipeline.core.calibration`, `farfan_pipeline.core.wiring`
- **Forbidden**: `farfan_pipeline.analysis`, `farfan_pipeline.processing`, `farfan_pipeline.api`

### 2. Core orchestrator must not import analysis
- **Source**: `farfan_pipeline.core.orchestrator`
- **Forbidden**: `farfan_pipeline.analysis`
- **Current Violation**: `core/orchestrator/core.py:38` imports `analysis.recommendation_engine`

### 3. Processing layer cannot import orchestrator
- **Source**: `farfan_pipeline.processing`
- **Forbidden**: `farfan_pipeline.core.orchestrator`

### 4. Analysis layer cannot import orchestrator
- **Source**: `farfan_pipeline.analysis`
- **Forbidden**: `farfan_pipeline.core.orchestrator`
- **Current Violation**: `analysis/report_assembly.py:574` imports `core.orchestrator.factory`

### 5. Analysis depends on core but not infrastructure
- **Source**: `farfan_pipeline.analysis`
- **Forbidden**: `farfan_pipeline.infrastructure`

### 6. Infrastructure must not pull orchestrator
- **Source**: `farfan_pipeline.infrastructure`
- **Forbidden**: `farfan_pipeline.core.orchestrator`

### 7. API layer only calls orchestrator entry points
- **Source**: `farfan_pipeline.api`
- **Forbidden**: `farfan_pipeline.processing`, `farfan_pipeline.analysis`, `farfan_pipeline.utils`
- **Current Violations**:
  - `api/api_server.py:48` imports `analysis.recommendation_engine`
  - `api/pipeline_connector.py:286` imports `processing.spc_ingestion`
  - `api/pipeline_connector.py:287` imports `utils.spc_adapter`

### 8. Utils stay leaf modules
- **Source**: `farfan_pipeline.utils`
- **Forbidden**: `farfan_pipeline.core.orchestrator`, `farfan_pipeline.processing`, `farfan_pipeline.analysis`
- **Current Violation**: `utils/cpp_adapter.py:25` imports `core.orchestrator.core`

## Usage

### Run Validation

```bash
python import_contract_validator.py
```

### Exit Codes

- **0**: All contracts satisfied
- **1**: Contract violations detected

### Output

The validator generates:

1. **Console output** with summary and violation details
2. **LAYER_VIOLATION_REPORT.md** with:
   - Violation summary
   - Detailed violation information (file, line, import statement)
   - Contract violated
   - Specific remediation strategies
   - Architectural guidelines

## Implementation Details

### AST Import Analysis

The validator uses Python's `ast` module to:

- Parse Python source files
- Extract import statements (both `import` and `from...import`)
- Handle relative imports correctly (e.g., `from ...analysis` resolved to absolute paths)
- Track import levels for accurate resolution

### Relative Import Resolution

```python
# Source: farfan_pipeline.core.orchestrator.core
# Import: from ...analysis.recommendation_engine import X
# Level: 3
# Resolved: farfan_pipeline.analysis.recommendation_engine
```

The resolver:
1. Gets the source module path
2. Goes up `level` directories
3. Appends the imported module name
4. Checks against forbidden patterns

### Violation-Prone Modules

The validator specifically analyzes:

- `src/farfan_pipeline/core/orchestrator/` (all files)
- `src/farfan_pipeline/processing/aggregation.py`
- `src/farfan_pipeline/utils/` (all files)
- `src/farfan_pipeline/analysis/` (all files)
- `src/farfan_pipeline/api/` (all files)

## Remediation Strategies

### Orchestrator → Analysis

**Problem**: Orchestrator directly imports analysis components.

**Solutions**:
- **Interface Extraction**: Extract analysis interfaces to core layer
- **Factory Pattern**: Use factory in core to instantiate analysis components
- **Registry Pattern**: Register analysis handlers via registry mechanism

### Utils → Core

**Problem**: Utils imports from core/orchestrator.

**Solutions**:
- **Keep Utils Lean**: Utils should be leaf modules with no domain dependencies
- **Extract to Core**: Move shared data structures to core.contracts

### Analysis → Orchestrator

**Problem**: Analysis imports from orchestrator.

**Solutions**:
- **Dependency Inversion**: Move shared interfaces to core.contracts
- **Signal-Based Decoupling**: Use flux signal system for communication

### API Bypassing Orchestrator

**Problem**: API directly imports processing/analysis/utils.

**Solutions**:
- **API Layer Isolation**: API should only call orchestrator entry points
- **Facade Pattern**: Create orchestrator facades exposing only necessary operations

## Architectural Guidelines

### Allowed Dependencies

```
API Layer
  ↓ (calls entry points only)
Core Orchestrator
  ↓
Processing ← → Analysis
  ↓           ↓
Core (calibration, wiring)
  ↓
Utils (leaf layer)
```

### Forbidden Dependencies

- ❌ Orchestrator → Analysis
- ❌ Processing → Orchestrator
- ❌ Analysis → Orchestrator
- ❌ Utils → Core/Processing/Analysis
- ❌ API → Processing/Analysis/Utils (bypass orchestrator)

## Integration

### CI/CD Integration

Add to `.github/workflows/`:

```yaml
- name: Validate Import Contracts
  run: python import_contract_validator.py
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python import_contract_validator.py
if [ $? -ne 0 ]; then
    echo "Import contract validation failed!"
    exit 1
fi
```

## Maintenance

### Adding New Contracts

Edit `ImportContractValidator.CONTRACTS` in `import_contract_validator.py`:

```python
{
    "name": "New Contract Name",
    "source_patterns": ["farfan_pipeline.module"],
    "forbidden_patterns": ["farfan_pipeline.forbidden"],
}
```

### Adding Violation-Prone Modules

Edit `ImportContractValidator.VIOLATION_PRONE_MODULES`:

```python
VIOLATION_PRONE_MODULES = [
    "src/farfan_pipeline/your/module",
]
```

## Troubleshooting

### Syntax Errors in Source Files

The validator may encounter syntax errors in files with malformed code. These are logged as warnings and the file is skipped.

### False Positives

If a violation is incorrectly flagged, check:

1. Import level resolution (relative vs absolute)
2. Module name matching (partial vs exact)
3. Contract source patterns

### import-linter Not Found

Ensure import-linter is installed:

```bash
pip install import-linter
```

Or use the command directly:

```bash
lint-imports --config pyproject.toml
```

## Files

- **import_contract_validator.py**: Main validator implementation
- **LAYER_VIOLATION_REPORT.md**: Generated violation report (gitignored)
- **pyproject.toml**: Contract definitions in `[tool.importlinter]` section

## Status

**Current Status**: ❌ 6 violations detected across 4 contracts

The codebase currently has architectural violations that need remediation. See `LAYER_VIOLATION_REPORT.md` for detailed information and remediation strategies.
