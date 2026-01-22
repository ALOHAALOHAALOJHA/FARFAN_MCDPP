"""
SISAS Event Trigger Optimization Module

Provides enhanced event triggers for fine-grained signal emission.
These triggers are ADDITIVE to the core orchestrator signals.

Trigger Types:
1. SubPhase Triggers - Emit signals within phase execution
2. Contract Triggers - Emit signals during contract execution
3. Extraction Triggers - Emit signals during MC extraction
4. Validation Triggers - Emit signals during gate validation

Features:
- Thread-safe registration and emission
- Priority-based execution ordering
- Conditional trigger execution
- Circuit breakers for fault tolerance
- Comprehensive metrics and diagnostics
- Bulk registration/deregistration
- Decorator-based registration
- Context managers for scoped triggers

Author: FARFAN Pipeline Team
Version: 2.0.0
"""

from .trigger_registry import (
    # Core classes
    TriggerRegistry,
    TriggerEvent,
    TriggerContext,
    TriggerCallback,
    TriggerCondition,
    TriggerState,
    TriggerMetrics,
    RegisteredTrigger,
    CircuitBreakerConfig,
    # Enums
    EventCategory,
    EVENT_CATEGORIES,
    # Module-level functions
    get_registry,
    register_trigger,
    emit_trigger,
    on_event,
)
from .subphase_triggers import SubPhaseTriggers
from .contract_triggers import ContractTriggers
from .extraction_triggers import ExtractionTriggers

__version__ = "2.0.0"

__all__ = [
    # Core Registry
    "TriggerRegistry",
    "TriggerEvent",
    "TriggerContext",
    "TriggerCallback",
    "TriggerCondition",
    "TriggerState",
    "TriggerMetrics",
    "RegisteredTrigger",
    "CircuitBreakerConfig",
    # Enums and mappings
    "EventCategory",
    "EVENT_CATEGORIES",
    # Convenience functions
    "get_registry",
    "register_trigger",
    "emit_trigger",
    "on_event",
    # Specialized managers
    "SubPhaseTriggers",
    "ContractTriggers",
    "ExtractionTriggers",
]


def get_all_managers(
    registry: TriggerRegistry = None,
) -> dict:
    """
    Factory function to get all trigger managers.

    Args:
        registry: Optional shared registry (uses singleton if None)

    Returns:
        Dict with all manager instances
    """
    reg = registry or get_registry()
    return {
        "subphase": SubPhaseTriggers(reg),
        "contract": ContractTriggers(reg),
        "extraction": ExtractionTriggers(reg),
    }


class TriggerFacade:
    """
    Unified facade for all trigger operations.

    Provides a single entry point for registering and emitting
    triggers across all domains (phase, contract, extraction).
    """

    def __init__(self, registry: TriggerRegistry = None):
        """Initialize with optional shared registry."""
        self._registry = registry or get_registry()
        self._subphase = SubPhaseTriggers(self._registry)
        self._contract = ContractTriggers(self._registry)
        self._extraction = ExtractionTriggers(self._registry)

    @property
    def registry(self) -> TriggerRegistry:
        """Access the underlying registry."""
        return self._registry

    @property
    def subphase(self) -> SubPhaseTriggers:
        """Access subphase triggers."""
        return self._subphase

    @property
    def contract(self) -> ContractTriggers:
        """Access contract triggers."""
        return self._contract

    @property
    def extraction(self) -> ExtractionTriggers:
        """Access extraction triggers."""
        return self._extraction

    def health_check(self) -> dict:
        """Combined health check across all managers."""
        return {
            "registry": self._registry.health_check(),
            "subphase": self._subphase.health_check(),
            "extraction": self._extraction.health_check(),
            "contract": {
                "registrations": len(self._contract._registry._triggers_by_id),
            },
        }

    def clear_all(self) -> dict:
        """Clear all triggers from all managers."""
        return {
            "subphase": self._subphase.clear_all(),
            "extraction": self._extraction.clear_all(),
            "registry": (self._registry.clear(), 0)[1],
        }

    def __repr__(self) -> str:
        return f"<TriggerFacade registry={len(self._registry)}>"
