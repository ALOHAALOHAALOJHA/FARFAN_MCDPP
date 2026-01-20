"""
SISAS Validation Gates Module

Four gates that every signal must pass:
1. ScopeAlignmentGate - Validates phase/policy_area/slot alignment
2. ValueAddGate - Validates empirical_availability threshold
3. CapabilityGate - Validates consumer capability matching
4. IrrigationChannelGate - Validates successful dispatch

Author:  FARFAN Pipeline Team
Version: 1.0.0
"""

from .scope_alignment_gate import ScopeAlignmentGate, ScopeAlignmentResult
from .value_add_gate import ValueAddGate, ValueAddResult
from .capability_gate import CapabilityGate, CapabilityResult
from .irrigation_channel_gate import IrrigationChannelGate, IrrigationResult
from .gate_orchestrator import GateOrchestrator, GateOrchestratorResult

__all__ = [
    "ScopeAlignmentGate",
    "ScopeAlignmentResult",
    "ValueAddGate",
    "ValueAddResult",
    "CapabilityGate",
    "CapabilityResult",
    "IrrigationChannelGate",
    "IrrigationResult",
    "GateOrchestrator",
    "GateOrchestratorResult",
]
