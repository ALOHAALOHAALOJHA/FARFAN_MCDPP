"""
F.A.R.F.A.N Orchestration Module
================================

Public API for the orchestration layer.

EXPORTS:
    - Orchestrator, MethodExecutor, Phase0ValidationResult
    - Calibration types (when available)

Note: Calibration types imports are optional. If calibration_types module
      is not available, only core orchestration classes are exported.
"""

# Try to import calibration types if available
try:
    from farfan_pipeline.calibration.pdm_calibrator import CalibrationResult
    _has_calibration_types = True
except ImportError:
    _has_calibration_types = False

# Always export core orchestration classes
from farfan_pipeline.orchestration.orchestrator import (
    Orchestrator,
    MethodExecutor,
    Phase0ValidationResult,
    GateResult,
)

__all__ = [
    # Core orchestration
    "Orchestrator",
    "MethodExecutor",
    "Phase0ValidationResult",
    "GateResult",
]

# Add calibration types if available
if _has_calibration_types:
    __all__.append("CalibrationResult")
