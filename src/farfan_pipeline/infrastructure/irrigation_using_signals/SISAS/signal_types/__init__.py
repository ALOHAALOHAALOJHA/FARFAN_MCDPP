# -*- coding: utf-8 -*-
"""
SISAS Signals Module

Este módulo expone los tipos de señales del sistema SISAS que están
activamente implementados y en uso.

NOTA: Las señales de orquestación (orchestration.py) fueron eliminadas
porque no estaban siendo utilizadas por ningún componente del sistema.

Exports:
    - 17 clases de señales activas
    - SignalRegistry para introspección y factory
"""

# Registry first
from .registry import SignalRegistry

# Structural signals
from .types.structural import (
    StructuralAlignmentSignal,
    SchemaConflictSignal,
    CanonicalMappingSignal,
    AlignmentStatus
)

# Integrity signals
from .types.integrity import (
    EventPresenceSignal,
    EventCompletenessSignal,
    DataIntegritySignal,
    PresenceStatus,
    CompletenessLevel
)

# Epistemic signals
from .types.epistemic import (
    AnswerDeterminacySignal,
    AnswerSpecificitySignal,
    EmpiricalSupportSignal,
    MethodApplicationSignal,
    DeterminacyLevel,
    SpecificityLevel,
    EmpiricalSupportLevel
)

# Contrast signals
from .types.contrast import (
    DecisionDivergenceSignal,
    ConfidenceDropSignal,
    TemporalContrastSignal,
    DivergenceType,
    DivergenceSeverity
)

# Operational signals
from .types.operational import (
    ExecutionAttemptSignal,
    FailureModeSignal,
    LegacyActivitySignal,
    LegacyDependencySignal,
    ExecutionStatus,
    FailureMode
)

# Consumption signals
from .types.consumption import (
    FrequencySignal,
    TemporalCouplingSignal,
    ConsumerHealthSignal
)

__all__ = [
    # Registry
    "SignalRegistry",

    # Structural signals
    "StructuralAlignmentSignal",
    "SchemaConflictSignal",
    "CanonicalMappingSignal",
    "AlignmentStatus",

    # Integrity signals
    "EventPresenceSignal",
    "EventCompletenessSignal",
    "DataIntegritySignal",
    "PresenceStatus",
    "CompletenessLevel",

    # Epistemic signals
    "AnswerDeterminacySignal",
    "AnswerSpecificitySignal",
    "EmpiricalSupportSignal",
    "MethodApplicationSignal",
    "DeterminacyLevel",
    "SpecificityLevel",
    "EmpiricalSupportLevel",

    # Contrast signals
    "DecisionDivergenceSignal",
    "ConfidenceDropSignal",
    "TemporalContrastSignal",
    "DivergenceType",
    "DivergenceSeverity",

    # Operational signals
    "ExecutionAttemptSignal",
    "FailureModeSignal",
    "LegacyActivitySignal",
    "LegacyDependencySignal",
    "ExecutionStatus",
    "FailureMode",

    # Consumption signals
    "FrequencySignal",
    "TemporalCouplingSignal",
    "ConsumerHealthSignal",
]