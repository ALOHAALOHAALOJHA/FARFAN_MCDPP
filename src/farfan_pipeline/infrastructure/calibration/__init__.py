"""
Calibration Infrastructure - Epistemic System v4.0.0
=======================================================

CONSTITUCIÓN DEL SISTEMA:
    Este módulo implementa la ÚNICA forma de calibración para FARFAN v4,
    excepto para Fase 1 (ingestión) que usa Phase1PDMCalibrator.

INVARIANTES CONSTITUCIONALES (CI):
    CI-01: Exactamente 300 contratos JSON v4
    CI-02: Zero clases ejecutoras legacy (D#Q#_Executor)
    CI-03: INMUTABILIDAD EPISTÉMICA - Level nunca cambia post-init
    CI-04: ASIMETRÍA POPPERIANA - N3 puede vetar N1/N2, nunca al revés
    CI-05: SEPARACIÓN CALIBRACIÓN-NIVEL - PDM ajusta parámetros, no nivel

ARQUITECTURA EPISTÉMICA (N0-N4):
    N0-INFRA: Infraestructura (sin juicio analítico)
    N1-EMP:   Extracción empírica (positivista)
    N2-INF:   Inferencia computacional (bayesiana/constructivista)
    N3-AUD:   Auditoría/falsación (popperiano) - PUEDE VETAR N1/N2
    N4-META:  Meta-análisis del proceso
"""

from __future__ import annotations

# =============================================================================
# FASE 1: PDM CALIBRATOR (MANTENER - Exclusión a la constitución)
# =============================================================================

from .pdm_calibrator import (
    Phase1PDMCalibrator,
)


# =============================================================================
# EPISTEMIC CALIBRATION CORE (v4.0.0 - SISTEMA ÚNICO para Fase 2+)
# =============================================================================

from .calibration_core import (
    ValidationError,
    CalibrationBoundsError,
    ClosedInterval,
    EpistemicLevel,
    OUTPUT_TYPE_BY_LEVEL,
    FUSION_BEHAVIOR_BY_LEVEL,
    validate_epistemic_level,
    validate_output_type_for_level,
    validate_fusion_behavior_for_level,
)

from .epistemic_core import (
    EpistemicLevelLiteral,
    PDMSensitivity,
    N0InfrastructureCalibration,
    N1EmpiricalCalibration,
    N2InferentialCalibration,
    N3AuditCalibration,
    N4MetaCalibration,
    create_calibration,
    get_default_calibration_for_level,
)

from .registry import (
    EpistemicCalibrationRegistry,
    CalibrationResolutionError,
    create_registry,
    MockPDMProfile,
)

from .type_defaults import (
    get_type_defaults,
    get_all_type_defaults,
    is_operation_permitted,
    is_operation_prohibited,
    get_contract_type_for_question,
    get_fusion_strategy,
    validate_fusion_strategy_for_type,
)


# =============================================================================
# EXPORTS - SOLO LO ESENCIAL
# =============================================================================

__all__ = [
    # === FASE 1: PDM Calibrator ===
    "Phase1PDMCalibrator",

    # === EPISTEMIC CORE ===
    "ValidationError",
    "CalibrationBoundsError",
    "ClosedInterval",
    "EpistemicLevel",
    "OUTPUT_TYPE_BY_LEVEL",
    "FUSION_BEHAVIOR_BY_LEVEL",
    "validate_epistemic_level",
    "validate_output_type_for_level",
    "validate_fusion_behavior_for_level",

    # === Calibration Classes ===
    "EpistemicLevelLiteral",
    "PDMSensitivity",
    "N0InfrastructureCalibration",
    "N1EmpiricalCalibration",
    "N2InferentialCalibration",
    "N3AuditCalibration",
    "N4MetaCalibration",
    "create_calibration",
    "get_default_calibration_for_level",

    # === Registry ===
    "EpistemicCalibrationRegistry",
    "CalibrationResolutionError",
    "create_registry",
    "MockPDMProfile",

    # === Type Defaults ===
    "get_type_defaults",
    "get_all_type_defaults",
    "is_operation_permitted",
    "is_operation_prohibited",
    "get_contract_type_for_question",
    "get_fusion_strategy",
    "validate_fusion_strategy_for_type",
]
