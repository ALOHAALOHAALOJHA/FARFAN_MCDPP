# COHORT 2024 Quick Reference

## Load Configurations

```python
from calibration_parametrization_system import get_calibration_config, get_parametrization_config

# Calibration
intrinsic_cal = get_calibration_config("intrinsic_calibration")
rubric = get_calibration_config("intrinsic_calibration_rubric")
questionnaire = get_calibration_config("questionnaire_monolith")
method_compat = get_calibration_config("method_compatibility")
fusion_weights = get_calibration_config("fusion_weights")
method_inventory = get_calibration_config("canonical_method_inventory")

# Parametrization
runtime_layers = get_parametrization_config("runtime_layers")
executor_config = get_parametrization_config("executor_config")
```

## Verify Cohort Metadata

```python
from calibration_parametrization_system import get_cohort_metadata

metadata = get_cohort_metadata()
assert metadata["cohort_id"] == "COHORT_2024"
assert metadata["wave_version"] == "REFACTOR_WAVE_2024_12"
```

## List Available Configs

```python
from calibration_parametrization_system import list_available_configs

configs = list_available_configs()
print("Calibration:", configs["calibration"])
print("Parametrization:", configs["parametrization"])
```

## Backward Compatibility

```python
from calibration_parametrization_system.import_adapters import ConfigPathAdapter

# Old path → COHORT_2024 automatically
config = ConfigPathAdapter.load_config(
    "system/config/calibration/intrinsic_calibration.json"
)
```

## File Locations

### Calibration
- `calibration/COHORT_2024_intrinsic_calibration.json`
- `calibration/COHORT_2024_intrinsic_calibration_rubric.json`
- `calibration/COHORT_2024_questionnaire_monolith.json`
- `calibration/COHORT_2024_method_compatibility.json`
- `calibration/COHORT_2024_fusion_weights.json`
- `calibration/COHORT_2024_canonical_method_inventory.json`
- `calibration/COHORT_2024_layer_assignment.py`
- `calibration/COHORT_2024_*_layer.py` (8 layer evaluators)
- `calibration/COHORT_2024_intrinsic_scoring.py`

### Parametrization
- `parametrization/COHORT_2024_runtime_layers.json`
- `parametrization/COHORT_2024_executor_config.json`
- `parametrization/COHORT_2024_executor_config.py`
- `parametrization/COHORT_2024_executor_profiler.py`

## Manifest

Audit trail: `COHORT_MANIFEST.json`
- 16 calibration files
- 4 parametrization files
- Original → New path mappings
- Cohort metadata for each file

## Metadata Structure

All files include:
```json
{
  "_cohort_metadata": {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12"
  }
}
```

## Path Mappings

| Original | COHORT_2024 | Category |
|----------|-------------|----------|
| `system/config/calibration/intrinsic_calibration.json` | `COHORT_2024_intrinsic_calibration.json` | Calibration |
| `system/config/calibration/runtime_layers.json` | `COHORT_2024_runtime_layers.json` | Parametrization |
| `config/json_files_ no_schemas/method_compatibility.json` | `COHORT_2024_method_compatibility.json` | Calibration |
| `config/json_files_ no_schemas/fusion_specification.json` | `COHORT_2024_fusion_weights.json` | Calibration |
| `src/farfan_pipeline/core/orchestrator/executor_config.py` | `COHORT_2024_executor_config.py` | Parametrization |

See `COHORT_MANIFEST.json` for complete mappings.
