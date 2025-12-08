# COHORT 2024 Calibration & Parametrization System - Index

## Quick Start
- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - API cheat sheet
- **Usage Examples**: [USAGE_EXAMPLES.py](USAGE_EXAMPLES.py) - Runnable examples
- **Full Documentation**: [README.md](README.md) - Complete guide
- **Migration Summary**: [../COHORT_2024_MIGRATION_SUMMARY.md](../COHORT_2024_MIGRATION_SUMMARY.md) - Implementation details

## Core Files

### Audit & Metadata
- `COHORT_MANIFEST.json` - Complete migration manifest with audit trail
  - 16 calibration files tracked
  - 4 parametrization files tracked
  - Original → New path mappings
  - Cohort metadata for each file

### Loaders & Adapters
- `cohort_loader.py` - `CohortLoader` class for configuration loading
- `import_adapters.py` - `ConfigPathAdapter` for backward compatibility
- `__init__.py` - Public API (get_calibration_config, get_parametrization_config)

### Migration Tools
- `migrate_cohort_2024.py` - Main migration script with metadata embedding
- `batch_migrate.py` - Batch migration utility

### Documentation
- `README.md` - Full documentation
- `QUICK_REFERENCE.md` - API quick reference
- `USAGE_EXAMPLES.py` - Comprehensive usage examples
- `INDEX.md` - This file

## Calibration Files (16 total)

### Configuration Files (JSON)
1. `COHORT_2024_intrinsic_calibration.json` - Base layer (@b) parameters
   - Theory/Impl/Deploy components
   - Role requirements
   - Weight specifications

2. `COHORT_2024_intrinsic_calibration_rubric.json` - Canonical rubric
   - Exact formulas (b_theory, b_impl, b_deploy)
   - Q1/Q2/Q3 decision automaton
   - Exclusion criteria

3. `COHORT_2024_questionnaire_monolith.json` - 300-question structure
   - Dimensions: D1-D6 (INSUMOS → CAUSALIDAD)
   - Policy Areas: PA01-PA10
   - Question blocks and patterns

4. `COHORT_2024_method_compatibility.json` - Method compatibility scores
   - Question compatibility
   - Dimension alignment
   - Policy area fitness

5. `COHORT_2024_fusion_weights.json` - Fusion specification
   - Linear weights (a_ℓ)
   - Interaction weights (a_ℓk)
   - Role-specific parameters

6. `COHORT_2024_canonical_method_inventory.json` - Method inventory
   - ~2000 methods
   - Executor catalog
   - Role assignments

### Implementation Files (Python)
7. `COHORT_2024_layer_assignment.py` - Layer requirements and Choquet weights
8. `COHORT_2024_layer_coexistence.py` - Layer coexistence validation
9. `COHORT_2024_layer_computers.py` - Layer score computations
10. `COHORT_2024_layer_influence_model.py` - Layer influence modeling
11. `COHORT_2024_chain_layer.py` - @chain evaluator
12. `COHORT_2024_congruence_layer.py` - Congruence evaluator
13. `COHORT_2024_meta_layer.py` - @m evaluator
14. `COHORT_2024_unit_layer.py` - @u evaluator
15. `COHORT_2024_intrinsic_scoring.py` - Scoring formulas
16. `COHORT_2024_intrinsic_calibration_loader.py` - Config loader utilities

## Parametrization Files (4 total)

### Configuration Files (JSON)
1. `COHORT_2024_runtime_layers.json` - Runtime layer parameters
   - Chain/Quality/Density/Provenance/Coverage/Uncertainty/Mechanism
   - Base scores and factors

2. `COHORT_2024_executor_config.json` - Executor configuration
   - Default settings
   - Resource limits

### Implementation Files (Python)
3. `COHORT_2024_executor_config.py` - ExecutorConfig dataclass
   - max_tokens, temperature, timeout_s, retry, seed
   - Type validation

4. `COHORT_2024_executor_profiler.py` - Performance profiling
   - Executor metrics
   - Method dispensary analytics
   - Bottleneck detection

## Layer System Reference

### 8-Layer Calibration System
- **@b** - Code quality (base theory, impl, deploy)
- **@chain** - Method wiring/orchestration
- **@q** - Question appropriateness
- **@d** - Dimension alignment
- **@p** - Policy area fit
- **@C** - Contract compliance
- **@u** - Document quality
- **@m** - Governance maturity

### Role Requirements
- **SCORE_Q**: All 8 layers
- **INGEST_PDM**: @b, @chain, @u, @m
- **STRUCTURE**: @b, @chain, @u, @m
- **EXTRACT**: @b, @chain, @u, @m
- **AGGREGATE**: @b, @chain, @u, @m
- **REPORT**: @b, @chain, @u, @m
- **META_TOOL**: @b, @chain, @u, @m
- **TRANSFORM**: @b, @chain, @u, @m

## Original → COHORT_2024 Mappings

### Calibration
```
system/config/calibration/intrinsic_calibration.json
  → calibration/COHORT_2024_intrinsic_calibration.json

system/config/calibration/intrinsic_calibration_rubric.json
  → calibration/COHORT_2024_intrinsic_calibration_rubric.json

system/config/questionnaire/questionnaire_monolith.json
  → calibration/COHORT_2024_questionnaire_monolith.json

config/json_files_ no_schemas/method_compatibility.json
  → calibration/COHORT_2024_method_compatibility.json

config/json_files_ no_schemas/fusion_specification.json
  → calibration/COHORT_2024_fusion_weights.json

scripts/inventory/canonical_method_inventory.json
  → calibration/COHORT_2024_canonical_method_inventory.json

src/farfan_pipeline/core/calibration/*.py
  → calibration/COHORT_2024_*.py
```

### Parametrization
```
system/config/calibration/runtime_layers.json
  → parametrization/COHORT_2024_runtime_layers.json

config/json_files_ no_schemas/executor_config.json
  → parametrization/COHORT_2024_executor_config.json

src/farfan_pipeline/core/orchestrator/executor_config.py
  → parametrization/COHORT_2024_executor_config.py

src/farfan_pipeline/core/orchestrator/executor_profiler.py
  → parametrization/COHORT_2024_executor_profiler.py
```

## API Reference

### Load Configurations
```python
from calibration_parametrization_system import (
    get_calibration_config,        # Load calibration config
    get_parametrization_config,    # Load parametrization config
    get_cohort_metadata,            # Get cohort metadata
    list_available_configs,         # List all configs
    CohortLoader,                   # Advanced loader class
)
```

### Backward Compatibility
```python
from calibration_parametrization_system.import_adapters import ConfigPathAdapter

# Automatically redirect old paths to COHORT_2024
config = ConfigPathAdapter.load_config("system/config/calibration/intrinsic_calibration.json")
```

## Metadata Structure

All COHORT_2024 files include:
```json
{
  "_cohort_metadata": {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12"
  }
}
```

## Statistics

- **Total Files**: 20 (16 calibration + 4 parametrization)
- **JSON Files**: 9
- **Python Files**: 11
- **Documentation Files**: 4
- **Migration Tools**: 2
- **Loader/Adapter Files**: 3

## Future Cohorts

When creating COHORT_2025:
1. Create new `calibration_parametrization_system_2025/` directory
2. Copy this structure
3. Update prefixes: `COHORT_2024_` → `COHORT_2025_`
4. Update metadata: cohort_id, wave_version, creation_date
5. Preserve `calibration_parametrization_system/` as-is

## Support

- **Issues**: Check COHORT_MANIFEST.json for original file paths
- **Migration**: Run `batch_migrate.py` to regenerate files
- **Testing**: Run `USAGE_EXAMPLES.py` to validate system
- **Documentation**: See README.md for complete guide

---

*COHORT 2024 - Strict wave separation with auditable migration trails*
