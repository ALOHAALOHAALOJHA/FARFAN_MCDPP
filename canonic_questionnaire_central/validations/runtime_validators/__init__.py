"""
Runtime Validators Module

Implements the four validation gates for SISAS signal processing and data enrichment:
1. Scope Validator - Consumer authorization (Rule 1)
2. Value-Add Validator - Material improvement verification (Rule 2)
3. Capability Validator - Technical maturity check (Rule 3)
4. Channel Validator - Traceability and governance (Rule 4)
"""

from canonic_questionnaire_central.validations.runtime_validators.scope_validator import (
    ScopeValidator,
    SignalScope,
    ScopeLevel,
    ScopeValidationResult,
    PREDEFINED_SCOPES,
)

from canonic_questionnaire_central.validations.runtime_validators.value_add_validator import (
    ValueAddScorer,
    ValueAddMetrics,
    SignalDeduplicator,
)

from canonic_questionnaire_central.validations.runtime_validators.capability_validator import (
    CapabilityValidator,
    SignalCapability,
    CapabilityValidationResult,
    SignalConsumerProtocol,
)

from canonic_questionnaire_central.validations.runtime_validators.channel_validator import (
    ChannelValidator,
    DataFlow,
    ChannelType,
    ChannelStatus,
    ChannelValidationResult,
    FlowManifest,
)

__all__ = [
    # Scope Validator (Gate 1)
    "ScopeValidator",
    "SignalScope",
    "ScopeLevel",
    "ScopeValidationResult",
    "PREDEFINED_SCOPES",
    # Value-Add Validator (Gate 2)
    "ValueAddScorer",
    "ValueAddMetrics",
    "SignalDeduplicator",
    # Capability Validator (Gate 3)
    "CapabilityValidator",
    "SignalCapability",
    "CapabilityValidationResult",
    "SignalConsumerProtocol",
    # Channel Validator (Gate 4)
    "ChannelValidator",
    "DataFlow",
    "ChannelType",
    "ChannelStatus",
    "ChannelValidationResult",
    "FlowManifest",
]
