"""
SISAS Event Trigger Optimization Module

Provides enhanced event triggers for fine-grained signal emission.
These triggers are ADDITIVE to the core orchestrator signals.

Trigger Types:
1. SubPhase Triggers - Emit signals within phase execution
2. Contract Triggers - Emit signals during contract execution
3. Extraction Triggers - Emit signals during MC extraction
4. Validation Triggers - Emit signals during gate validation

Author: FARFAN Pipeline Team
Version: 1.0.0
"""

from .trigger_registry import (
    TriggerRegistry,
    TriggerEvent,
    TriggerCallback,
    register_trigger,
    emit_trigger,
)
from .subphase_triggers import SubPhaseTriggers
from .contract_triggers import ContractTriggers
from .extraction_triggers import ExtractionTriggers

__all__ = [
    "TriggerRegistry",
    "TriggerEvent",
    "TriggerCallback",
    "register_trigger",
    "emit_trigger",
    "SubPhaseTriggers",
    "ContractTriggers",
    "ExtractionTriggers",
]
