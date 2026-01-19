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

from .orchestration import (
    PhaseCompletionStatus,
    OrchestrationDecisionType,
    OrchestrationFinalStatus,
    BlockingStatus,
    PhaseStartSignal,
    PhaseCompleteSignal,
    PhaseProgressSignal,
    PhaseRetrySignal,
    OrchestrationInitializedSignal,
    OrchestrationCompleteSignal,
    OrchestrationDecisionSignal,
    ConstitutionalValidationSignal,
    DependencyGraphLoadedSignal,
    PhaseReadyToStartSignal,
    DependencyGraphUpdatedSignal,
    PhaseBlockedSignal,
    ParallelExecutionLimitSignal,
    PhaseDependencySatisfiedSignal,
    create_phase_start_signal,
    create_phase_complete_signal,
    create_orchestration_initialized_signal,
    create_orchestration_decision_signal,
    create_orchestration_complete_signal,
    create_phase_ready_to_start_signal,
    create_dependency_graph_updated_signal,
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
    # Orchestration
    "PhaseCompletionStatus",
    "OrchestrationDecisionType",
    "OrchestrationFinalStatus",
    "BlockingStatus",
    "PhaseStartSignal",
    "PhaseCompleteSignal",
    "PhaseProgressSignal",
    "PhaseRetrySignal",
    "OrchestrationInitializedSignal",
    "OrchestrationCompleteSignal",
    "OrchestrationDecisionSignal",
    "ConstitutionalValidationSignal",
    "DependencyGraphLoadedSignal",
    "PhaseReadyToStartSignal",
    "DependencyGraphUpdatedSignal",
    "PhaseBlockedSignal",
    "ParallelExecutionLimitSignal",
    "PhaseDependencySatisfiedSignal",
    "create_phase_start_signal",
    "create_phase_complete_signal",
    "create_orchestration_initialized_signal",
    "create_orchestration_decision_signal",
    "create_orchestration_complete_signal",
    "create_phase_ready_to_start_signal",
    "create_dependency_graph_updated_signal",
]
