"""
SISAS Signal Types Module

Exports all signal type classes organized by category.
"""

# Import all types to make them available via this module
from .structural import (
    StructuralAlignmentSignal,
    SchemaConflictSignal,
    CanonicalMappingSignal,
    AlignmentStatus
)

from .integrity import (
    EventPresenceSignal,
    EventCompletenessSignal,
    DataIntegritySignal,
    PresenceStatus,
    CompletenessLevel
)

from .epistemic import (
    AnswerDeterminacySignal,
    AnswerSpecificitySignal,
    EmpiricalSupportSignal,
    MethodApplicationSignal,
    DeterminacyLevel,
    SpecificityLevel,
    EmpiricalSupportLevel
)

from .contrast import (
    DecisionDivergenceSignal,
    ConfidenceDropSignal,
    TemporalContrastSignal,
    DivergenceType,
    DivergenceSeverity
)

from .operational import (
    ExecutionAttemptSignal,
    FailureModeSignal,
    LegacyActivitySignal,
    LegacyDependencySignal,
    ExecutionStatus,
    FailureMode
)

from .consumption import (
    FrequencySignal,
    TemporalCouplingSignal,
    ConsumerHealthSignal
)

__all__ = [
    # Structural
    "StructuralAlignmentSignal",
    "SchemaConflictSignal",
    "CanonicalMappingSignal",
    "AlignmentStatus",
    # Integrity
    "EventPresenceSignal",
    "EventCompletenessSignal",
    "DataIntegritySignal",
    "PresenceStatus",
    "CompletenessLevel",
    # Epistemic
    "AnswerDeterminacySignal",
    "AnswerSpecificitySignal",
    "EmpiricalSupportSignal",
    "MethodApplicationSignal",
    "DeterminacyLevel",
    "SpecificityLevel",
    "EmpiricalSupportLevel",
    # Contrast
    "DecisionDivergenceSignal",
    "ConfidenceDropSignal",
    "TemporalContrastSignal",
    "DivergenceType",
    "DivergenceSeverity",
    # Operational
    "ExecutionAttemptSignal",
    "FailureModeSignal",
    "LegacyActivitySignal",
    "LegacyDependencySignal",
    "ExecutionStatus",
    "FailureMode",
    # Consumption
    "FrequencySignal",
    "TemporalCouplingSignal",
    "ConsumerHealthSignal",
]
