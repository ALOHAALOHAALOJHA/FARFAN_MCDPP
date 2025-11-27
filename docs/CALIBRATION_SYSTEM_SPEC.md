# CENTRALIZED CALIBRATION SYSTEM SPECIFICATION
**Status**: ACTIVE | **Version**: 2.0 | **Authoritative Source**: YES

## 1. System Overview
The Centralized Calibration System is the single source of truth for method quality assessment and parameterization. It eliminates hardcoded values and disparate configuration files.

## 2. Architecture
### 2.1 Core Components (Singletons)
- **`CalibrationOrchestrator`**: Coordinates the calibration process.
- **`ParameterLoader`**: Loads execution parameters.
- **`IntrinsicCalibrationLoader`**: Loads intrinsic quality scores.

### 2.2 Configuration Files (Single Source of Truth)
- **`config/intrinsic_calibration.json`**: Defines `intrinsic_score` and `layer` type.
- **`config/method_parameters.json`**: Defines `threshold`, `alpha`, etc.
- **`config/calibration_config.py`**: Global constants.

## 3. Method Anchoring
All methods MUST use the `@calibrated_method` decorator or the singleton injection pattern.

```python
@calibrated_method("module.Class.method")
def method(self, data, **params):
    ...
```

## 4. Layer Determination
Layers are determined DYNAMICALLY based on the `layer` field in `intrinsic_calibration.json` mapping to `LAYER_REQUIREMENTS` in `src/saaaaaa/core/calibration/layer_requirements.py`.

## 5. Verification
- `tests/verify_anchoring.py`: Ensures anchoring.
- `tests/check_hardcoded.py`: Ensures no hardcoded values.
- `tests/test_no_parallel_systems.py`: Ensures uniqueness.
