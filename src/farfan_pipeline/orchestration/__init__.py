"""
F.A.R.F.A.N Orchestration Module
================================

Public API for the orchestration layer.

EXPORTS:
    - Calibration types for calibrate_method() API
    
Note: Orchestrator is imported from orchestrator.py directly to avoid
      circular import issues with complex dependencies.
"""
from farfan_pipeline.orchestration.calibration_types import (
    LayerId,
    ROLE_LAYER_REQUIREMENTS,
    VALID_ROLES,
    CalibrationSubject,
    CalibrationEvidenceContext,
    CalibrationResult,
)

__all__ = [
    # Calibration types
    "LayerId",
    "ROLE_LAYER_REQUIREMENTS",
    "VALID_ROLES",
    "CalibrationSubject",
    "CalibrationEvidenceContext",
    "CalibrationResult",
]
