"""
Contract Triggers - Contract-level event triggers.

Provides triggers for contract lifecycle events.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging

from .trigger_registry import TriggerRegistry, TriggerEvent, TriggerContext

logger = logging.getLogger(__name__)


class ContractTriggers:
    """
    Manager for contract-level triggers.

    These triggers emit during contract execution:
    - Contract loading
    - Method injection
    - Contract execution
    - Veto check
    - Fusion
    """

    def __init__(self, registry: Optional[TriggerRegistry] = None):
        """
        Initialize ContractTriggers.

        Args:
            registry: Optional TriggerRegistry instance (uses singleton if None)
        """
        from .trigger_registry import TriggerRegistry
        self._registry = registry or TriggerRegistry()

    def on_contract_loading(
        self,
        contract_id: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """Register callback for contract loading."""
        def wrapped_callback(ctx: TriggerContext):
            ctx.contract_id = contract_id
            callback(ctx)

        return self._registry.register(
            TriggerEvent.CONTRACT_LOADING,
            wrapped_callback,
            priority=priority,
            name=name or f"contract_load_{contract_id}",
        )

    def on_contract_method_injecting(
        self,
        contract_id: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """Register callback for method injection."""
        def wrapped_callback(ctx: TriggerContext):
            ctx.contract_id = contract_id
            callback(ctx)

        return self._registry.register(
            TriggerEvent.CONTRACT_METHOD_INJECTING,
            wrapped_callback,
            priority=priority,
            name=name or f"contract_inject_{contract_id}",
        )

    def on_contract_executing(
        self,
        contract_id: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """Register callback for contract execution."""
        def wrapped_callback(ctx: TriggerContext):
            ctx.contract_id = contract_id
            callback(ctx)

        return self._registry.register(
            TriggerEvent.CONTRACT_EXECUTING,
            wrapped_callback,
            priority=priority,
            name=name or f"contract_execute_{contract_id}",
        )

    def on_contract_veto_check(
        self,
        contract_id: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """Register callback for veto check."""
        def wrapped_callback(ctx: TriggerContext):
            ctx.contract_id = contract_id
            callback(ctx)

        return self._registry.register(
            TriggerEvent.CONTRACT_VETO_CHECK,
            wrapped_callback,
            priority=priority,
            name=name or f"contract_veto_{contract_id}",
        )

    def on_contract_fusion(
        self,
        contract_id: str,
        callback,
        priority: int = 0,
        name: str = None,
    ) -> str:
        """Register callback for contract fusion."""
        def wrapped_callback(ctx: TriggerContext):
            ctx.contract_id = contract_id
            callback(ctx)

        return self._registry.register(
            TriggerEvent.CONTRACT_FUSION,
            wrapped_callback,
            priority=priority,
            name=name or f"contract_fusion_{contract_id}",
        )

    def emit_contract_loading(self, contract_id: str, payload: Dict[str, Any] = None) -> int:
        """Emit contract loading event."""
        context = TriggerContext(
            event=TriggerEvent.CONTRACT_LOADING,
            timestamp=datetime.utcnow(),
            contract_id=contract_id,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.CONTRACT_LOADING, context)

    def emit_contract_method_injecting(self, contract_id: str, payload: Dict[str, Any] = None) -> int:
        """Emit method injection event."""
        context = TriggerContext(
            event=TriggerEvent.CONTRACT_METHOD_INJECTING,
            timestamp=datetime.utcnow(),
            contract_id=contract_id,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.CONTRACT_METHOD_INJECTING, context)

    def emit_contract_executing(self, contract_id: str, payload: Dict[str, Any] = None) -> int:
        """Emit contract execution event."""
        context = TriggerContext(
            event=TriggerEvent.CONTRACT_EXECUTING,
            timestamp=datetime.utcnow(),
            contract_id=contract_id,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.CONTRACT_EXECUTING, context)

    def emit_contract_veto_check(self, contract_id: str, payload: Dict[str, Any] = None) -> int:
        """Emit veto check event."""
        context = TriggerContext(
            event=TriggerEvent.CONTRACT_VETO_CHECK,
            timestamp=datetime.utcnow(),
            contract_id=contract_id,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.CONTRACT_VETO_CHECK, context)

    def emit_contract_fusion(self, contract_id: str, payload: Dict[str, Any] = None) -> int:
        """Emit contract fusion event."""
        context = TriggerContext(
            event=TriggerEvent.CONTRACT_FUSION,
            timestamp=datetime.utcnow(),
            contract_id=contract_id,
            payload=payload or {},
        )
        return self._registry.emit(TriggerEvent.CONTRACT_FUSION, context)
