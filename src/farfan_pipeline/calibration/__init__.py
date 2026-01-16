"""
Sistema de Calibración Epistémica FARFAN 2025.1

Este módulo proporciona acceso al sistema de calibración epistémica
de 5 niveles (N0-N4) con resolución de 8 capas.

Niveles Epistémicos:
    N0-INFRA: Infraestructura global (defaults)
    N1-EMP: Empírico (observacional)
    N2-INF: Inferencial (Bayesiano)
    N3-AUD: Auditoría (veto gate)
    N4-META: Meta-análisis

Contratos Epistémicos:
    TYPE_A: Semantic Triangulation
    TYPE_B: Bayesian Inference
    TYPE_C: Causal Inference
    TYPE_D: Financial Aggregation
    TYPE_E: Logical Consistency
    SUBTIPO_F: Hybrid/Fallback

Author: FARFAN Engineering Team
Version: 1.0.0
"""

from __future__ import annotations

# Core calibration classes (from epistemic_core.py)
from .epistemic_core import (
    PDMSensitivity,
    N0InfrastructureCalibration,
    N1EmpiricalCalibration,
    N2InferentialCalibration,
    N3AuditCalibration,
    N4MetaCalibration,
    create_calibration,
    get_default_calibration_for_level,
)

# Core utilities (from calibration_core.py)
from .calibration_core import (
    ValidationError,
    CalibrationBoundsError,
    ClosedInterval,
    EpistemicLevel,
    validate_epistemic_level,
)

# Registry
from .registry import EpistemicCalibrationRegistry, create_registry

# Type defaults
from .type_defaults import (
    get_type_defaults,
    get_all_type_defaults,
    get_all_fusion_strategies,
    get_fusion_strategy,
    validate_fusion_strategy_for_type,
    get_contract_type_for_question,
    is_operation_prohibited,
    is_operation_permitted,
)

# PDM calibrator
try:
    from .pdm_calibrator import Phase1PDMCalibrator
except ImportError:
    Phase1PDMCalibrator = None

__all__ = [
    # Core utilities
    "ValidationError",
    "CalibrationBoundsError",
    "ClosedInterval",
    "EpistemicLevel",
    "validate_epistemic_level",
    # Epistemic calibration classes
    "PDMSensitivity",
    "N0InfrastructureCalibration",
    "N1EmpiricalCalibration",
    "N2InferentialCalibration",
    "N3AuditCalibration",
    "N4MetaCalibration",
    "create_calibration",
    "get_default_calibration_for_level",
    # Registry
    "EpistemicCalibrationRegistry",
    "create_registry",
    # Type defaults
    "get_type_defaults",
    "get_all_type_defaults",
    "get_all_fusion_strategies",
    "get_fusion_strategy",
    "validate_fusion_strategy_for_type",
    "get_contract_type_for_question",
    "is_operation_prohibited",
    "is_operation_permitted",
    # PDM calibrator
    "Phase1PDMCalibrator",
]
