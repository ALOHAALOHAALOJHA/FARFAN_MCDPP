# COHORT 2024 Calibration & Parametrization System

## Overview

This directory contains all calibration and parametrization configuration files for the COHORT_2024 refactoring wave, with strict metadata tracking and auditable migration trails.

## Directory Structure

```
calibration_parametrization_system/
├── calibration/                    # Intrinsic calibration files
│   ├── COHORT_2024_intrinsic_calibration.json
│   ├── COHORT_2024_intrinsic_calibration_rubric.json
│   ├── COHORT_2024_questionnaire_monolith.json
│   ├── COHORT_2024_method_compatibility.json
│   ├── COHORT_2024_fusion_weights.json
│   ├── COHORT_2024_canonical_method_inventory.json
│   ├── COHORT_2024_layer_assignment.py
│   ├── COHORT_2024_layer_coexistence.py
│   ├── COHORT_2024_layer_computers.py
│   ├── COHORT_2024_layer_influence_model.py
│   ├── COHORT_2024_chain_layer.py
│   ├── COHORT_2024_congruence_layer.py
│   ├── COHORT_2024_meta_layer.py
│   ├── COHORT_2024_unit_layer.py
│   ├── COHORT_2024_intrinsic_scoring.py
│   └── COHORT_2024_intrinsic_calibration_loader.py
│
├── parametrization/                # Runtime parametrization files
│   ├── COHORT_2024_runtime_layers.json
│   ├── COHORT_2024_executor_config.json
│   ├── COHORT_2024_executor_config.py
│   └── COHORT_2024_executor_profiler.py
│
├── COHORT_MANIFEST.json            # Complete migration manifest
├── cohort_loader.py                # Configuration loader
├── import_adapters.py              # Backward compatibility adapters
├── migrate_cohort_2024.py          # Migration script
├── batch_migrate.py                # Batch migration utility
├── __init__.py                     # Public API
└── README.md                       # This file
```

## File Categories

### Calibration Files
Files that define intrinsic quality measures and layer evaluations:
- **intrinsic_calibration.json**: Base layer (@b) parameters with theory/impl/deploy components
- **intrinsic_calibration_rubric.json**: Exact formulas and Q1/Q2/Q3 decision automaton
- **questionnaire_monolith.json**: 300-question questionnaire (D1-D6 × PA01-PA10)
- **method_compatibility.json**: Method compatibility scores for Q/D/P combinations
- **fusion_weights.json**: Fusion specification with linear and interaction weights
- **canonical_method_inventory.json**: Complete inventory of ~2000 methods
- **layer_*.py**: Layer evaluator implementations (@chain, @u, @m, @C, etc.)
- **intrinsic_scoring.py**: Scoring formula implementations
- **intrinsic_calibration_loader.py**: Configuration loader utilities

### Parametrization Files
Files that control runtime behavior and execution parameters:
- **runtime_layers.json**: Runtime layer score computation parameters
- **executor_config.json**: Executor configuration parameters
- **executor_config.py**: ExecutorConfig dataclass
- **executor_profiler.py**: Performance profiling framework

## Usage

### Basic Loading

```python
from calibration_parametrization_system import (
    get_calibration_config,
    get_parametrization_config,
    get_cohort_metadata
)

# Load calibration configs
intrinsic_cal = get_calibration_config("intrinsic_calibration")
rubric = get_calibration_config("intrinsic_calibration_rubric")
questionnaire = get_calibration_config("questionnaire_monolith")
method_compat = get_calibration_config("method_compatibility")
fusion_weights = get_calibration_config("fusion_weights")
method_inventory = get_calibration_config("canonical_method_inventory")

# Load parametrization configs
runtime_layers = get_parametrization_config("runtime_layers")
executor_config = get_parametrization_config("executor_config")

# Verify cohort metadata
metadata = get_cohort_metadata()
assert metadata["cohort_id"] == "COHORT_2024"
assert metadata["wave_version"] == "REFACTOR_WAVE_2024_12"
```

### Advanced Loading

```python
from calibration_parametrization_system import CohortLoader

loader = CohortLoader()

# List available configs
calibration_files = loader.list_calibration_files()
parametrization_files = loader.list_parametrization_files()

# Load with explicit validation
config = loader.load_calibration("intrinsic_calibration")
assert "_cohort_metadata" in config

# Get original path mapping
original_path = loader.get_original_path(
    "calibration",
    "COHORT_2024_intrinsic_calibration.json"
)
print(f"Originally: {original_path}")
```

### Backward Compatibility

For existing code that references old paths:

```python
from calibration_parametrization_system.import_adapters import ConfigPathAdapter

# Automatically loads COHORT_2024 version
config = ConfigPathAdapter.load_config(
    "system/config/calibration/intrinsic_calibration.json"
)

# Get new path for old path
cohort_path = ConfigPathAdapter.get_cohort_path(
    "system/config/calibration/runtime_layers.json"
)
```

## Cohort Metadata

All COHORT_2024 files contain embedded metadata:

```json
{
  "_cohort_metadata": {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12"
  },
  "_metadata": {
    "version": "1.0.0",
    "description": "..."
  },
  ...
}
```

This metadata serves as a tracer to distinguish new production artifacts from legacy files.

## Migration Trail

`COHORT_MANIFEST.json` maintains a complete audit trail:
- Original file paths
- New COHORT_2024 paths
- File types and categories
- Cohort metadata
- SHA256 hashes (for content integrity)
- Migration timestamps

## Wave Separation Policy

**Purpose**: Strict separation between refactoring waves

**Enforcement**:
- All COHORT_2024 files have `COHORT_2024_` prefix
- All files have embedded `_cohort_metadata`
- SHA256 hashes track content integrity
- Original files preserved at source locations

**Traceability**:
- `COHORT_MANIFEST.json` tracks all migrations
- Original → New path mappings
- Category (calibration vs parametrization)
- File purpose documentation

**Forward Migration**:
- Future cohorts use same pattern
- Increment cohort_id (COHORT_2025, etc.)
- Maintain separate directories per cohort
- Preserve all historical cohorts

## Updating Configuration

To update a configuration file:

1. Edit the `COHORT_2024_*.json` file in `calibration/` or `parametrization/`
2. Update the embedded `_cohort_metadata.creation_date`
3. Update `COHORT_MANIFEST.json` with new SHA256 hash
4. Document changes in commit message with cohort reference

## Testing

```python
# Verify all configs load correctly
from calibration_parametrization_system import list_available_configs

configs = list_available_configs()
print("Calibration:", configs["calibration"])
print("Parametrization:", configs["parametrization"])

# Validate metadata
from calibration_parametrization_system import get_cohort_metadata

metadata = get_cohort_metadata()
assert metadata["cohort_id"] == "COHORT_2024"
```

## Future Cohorts

When creating COHORT_2025:

1. Create new directories: `calibration_parametrization_system_2025/`
2. Copy this structure
3. Update all prefixes: `COHORT_2024_` → `COHORT_2025_`
4. Update metadata: `cohort_id`, `wave_version`, `creation_date`
5. Create new `COHORT_MANIFEST.json`
6. Preserve `calibration_parametrization_system/` (COHORT_2024) as-is

This ensures complete historical preservation and zero ambiguity about which wave produced which artifacts.
