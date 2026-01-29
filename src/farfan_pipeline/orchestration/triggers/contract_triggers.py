"""
Contract Triggers - Contract-level event triggers.

Provides triggers for contract lifecycle events with advanced features:
- Thread-safe registration and emission
- Bulk registration/deregistration
- Introspection and diagnostics
- Conditional trigger execution
- Metrics and timing
- Decorator-based registration
- Contract pattern matching (Q001-Q300 support)
"""

from typing import Optional, Dict, Any, Callable, List, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager
from functools import wraps
from enum import Enum
import logging
import threading
import time
import uuid
import re

from .trigger_registry import TriggerRegistry, TriggerEvent, TriggerContext

logger = logging.getLogger(__name__)


class TriggerState(str, Enum):
    """State of a registered trigger."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class ContractStage(str, Enum):
    """Contract execution stages."""
    LOADING = "loading"
    METHOD_INJECTING = "method_injecting"
    EXECUTING = "executing"
    VETO_CHECK = "veto_check"
    FUSION = "fusion"


class ContractOutcome(str, Enum):
    """Possible contract execution outcomes."""
    SUCCESS = "success"
    VETOED = "vetoed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ContractMetrics:
    """Metrics for contract trigger performance."""
    invocation_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    veto_count: int = 0
    fusion_count: int = 0
    total_execution_time_ms: float = 0.0
    methods_injected: int = 0
    last_invocation: Optional[datetime] = None
    last_error: Optional[str] = None
    last_contract_id: Optional[str] = None
    last_outcome: Optional[ContractOutcome] = None

    @property
    def avg_execution_time_ms(self) -> float:
        """Calculate average execution time."""
        if self.invocation_count == 0:
            return 0.0
        return self.total_execution_time_ms / self.invocation_count

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.invocation_count == 0:
            return 100.0
        return (self.success_count / self.invocation_count) * 100

    @property
    def veto_rate(self) -> float:
        """Calculate veto rate as percentage."""
        if self.invocation_count == 0:
            return 0.0
        return (self.veto_count / self.invocation_count) * 100


@dataclass
class ContractRegistration:
    """Extended registration info for a contract trigger."""
    registration_id: str
    event: TriggerEvent
    contract_id: str
    name: str
    priority: int
    state: TriggerState = TriggerState.ACTIVE
    condition: Optional[Callable[[TriggerContext], bool]] = None
    contract_pattern: Optional[str] = None  # Regex pattern for contract_id matching
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: ContractMetrics = field(default_factory=ContractMetrics)
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: Set[str] = field(default_factory=set)

    def matches_contract(self, contract_id: str) -> bool:
        """Check if contract_id matches this registration."""
        if self.contract_id == "*":
            return True
        if self.contract_pattern:
            return bool(re.match(self.contract_pattern, contract_id))
        return self.contract_id == contract_id


class ContractTriggers:
    """
    Manager for contract-level triggers.

    These triggers emit during contract execution:
    - Contract loading
    - Method injection
    - Contract execution
    - Veto check
    - Fusion

    Features:
    - Thread-safe operations
    - Conditional execution
    - Bulk operations
    - Metrics tracking
    - Contract pattern matching (regex support)
    - Q-range support (Q001-Q300)
    - Policy Area grouping
    - Introspection utilities
    - Context managers for scoped triggers
    """

    # Class-level event mapping for DRY registration
    _EVENT_MAP: Dict[str, TriggerEvent] = {
        "loading": TriggerEvent.CONTRACT_LOADING,
        "method_injecting": TriggerEvent.CONTRACT_METHOD_INJECTING,
        "executing": TriggerEvent.CONTRACT_EXECUTING,
        "veto_check": TriggerEvent.CONTRACT_VETO_CHECK,
        "fusion": TriggerEvent.CONTRACT_FUSION,
    }

    _STAGE_TO_EVENT: Dict[ContractStage, TriggerEvent] = {
        ContractStage.LOADING: TriggerEvent.CONTRACT_LOADING,
        ContractStage.METHOD_INJECTING: TriggerEvent.CONTRACT_METHOD_INJECTING,
        ContractStage.EXECUTING: TriggerEvent.CONTRACT_EXECUTING,
        ContractStage.VETO_CHECK: TriggerEvent.CONTRACT_VETO_CHECK,
        ContractStage.FUSION: TriggerEvent.CONTRACT_FUSION,
    }

    # Policy Area mapping (Q001-Q030 base × 10 PAs = Q001-Q300)
    _POLICY_AREAS = [
        "PA01_HEALTH", "PA02_EDUCATION", "PA03_ENVIRONMENT",
        "PA04_ECONOMY", "PA05_SOCIAL", "PA06_INFRASTRUCTURE",
        "PA07_GOVERNANCE", "PA08_SECURITY", "PA09_CULTURE",
        "PA10_TECHNOLOGY",
    ]

    def __init__(self, registry: Optional[TriggerRegistry] = None):
        """
        Initialize ContractTriggers.

        Args:
            registry: Optional TriggerRegistry instance (uses singleton if None)
        """
        from .trigger_registry import TriggerRegistry
        self._registry = registry or TriggerRegistry()
        self._lock = threading.RLock()
        self._registrations: Dict[str, ContractRegistration] = {}
        self._contract_registrations: Dict[str, Set[str]] = {}  # contract_id -> registration_ids
        self._event_registrations: Dict[TriggerEvent, Set[str]] = {}  # event -> registration_ids
        self._emission_history: List[Dict[str, Any]] = []
        self._max_history_size: int = 1000
        self._global_metrics = ContractMetrics()

    # ═══════════════════════════════════════════════════════════════════════════
    # CORE REGISTRATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _register_internal(
        self,
        event: TriggerEvent,
        contract_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        contract_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Internal registration with full feature support.

        Args:
            event: The trigger event type
            contract_id: The contract ID to scope the trigger (or "*" for all)
            callback: Function to call when trigger fires
            priority: Execution priority (higher = first)
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            contract_pattern: Optional regex pattern for contract_id matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        
        Technical Debt: Registered in TECHNICAL_DEBT_REGISTER.md
        Complexity: 27 - Refactoring scheduled Q2-Q3 2026
        """
        registration_id = str(uuid.uuid4())[:12]
        trigger_name = name or f"{event.name.lower()}_{contract_id}_{registration_id}"

        # Validate pattern if provided
        if contract_pattern:
            try:
                re.compile(contract_pattern)
            except re.error as e:
                logger.warning(f"Invalid contract pattern '{contract_pattern}': {e}")
                contract_pattern = None

        # Create registration record
        registration = ContractRegistration(
            registration_id=registration_id,
            event=event,
            contract_id=contract_id,
            name=trigger_name,
            priority=priority,
            condition=condition,
            contract_pattern=contract_pattern,
            metadata=metadata or {},
            tags=tags or set(),
        )

        # Create wrapped callback with metrics and condition
        @wraps(callback)
        def instrumented_callback(ctx: TriggerContext) -> None:
            with self._lock:
                reg = self._registrations.get(registration_id)
                if not reg or reg.state != TriggerState.ACTIVE:
                    return

            # Check contract_id match
            ctx_contract = getattr(ctx, 'contract_id', None) or ''
            if not registration.matches_contract(ctx_contract):
                return

            # Apply contract_id to context
            if contract_id != "*":
                ctx.contract_id = contract_id

            # Check condition
            if registration.condition is not None:
                try:
                    if not registration.condition(ctx):
                        logger.debug(f"Trigger '{trigger_name}' skipped: condition not met")
                        return
                except Exception as e:
                    logger.warning(f"Trigger '{trigger_name}' condition check failed: {e}")
                    return

            # Execute with timing
            start_time = time.perf_counter()
            try:
                callback(ctx)
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                with self._lock:
                    if registration_id in self._registrations:
                        reg = self._registrations[registration_id]
                        reg.metrics.invocation_count += 1
                        reg.metrics.success_count += 1
                        reg.metrics.total_execution_time_ms += elapsed_ms
                        reg.metrics.last_invocation = datetime.utcnow()
                        reg.metrics.last_contract_id = ctx_contract
                        reg.metrics.last_outcome = ContractOutcome.SUCCESS

                        # Track specific event metrics
                        if event == TriggerEvent.CONTRACT_METHOD_INJECTING:
                            reg.metrics.methods_injected += 1
                        elif event == TriggerEvent.CONTRACT_VETO_CHECK:
                            # Check if vetoed from payload
                            if ctx.payload.get("vetoed", False):
                                reg.metrics.veto_count += 1
                                reg.metrics.last_outcome = ContractOutcome.VETOED
                        elif event == TriggerEvent.CONTRACT_FUSION:
                            reg.metrics.fusion_count += 1

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"Trigger '{trigger_name}' failed after {elapsed_ms:.2f}ms: {e}")

                with self._lock:
                    if registration_id in self._registrations:
                        reg = self._registrations[registration_id]
                        reg.metrics.invocation_count += 1
                        reg.metrics.failure_count += 1
                        reg.metrics.total_execution_time_ms += elapsed_ms
                        reg.metrics.last_invocation = datetime.utcnow()
                        reg.metrics.last_error = str(e)
                        reg.metrics.last_outcome = ContractOutcome.FAILED
                raise

        # Register with underlying registry
        with self._lock:
            self._registry.register(
                event,
                instrumented_callback,
                priority=priority,
                name=trigger_name,
            )

            # Track registration
            self._registrations[registration_id] = registration

            # Index by contract_id
            if contract_id not in self._contract_registrations:
                self._contract_registrations[contract_id] = set()
            self._contract_registrations[contract_id].add(registration_id)

            # Index by event
            if event not in self._event_registrations:
                self._event_registrations[event] = set()
            self._event_registrations[event].add(registration_id)

        logger.debug(f"Registered contract trigger '{trigger_name}' for {event.value} on {contract_id}")
        return registration_id

    def on_contract_loading(
        self,
        contract_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        contract_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for contract loading.

        Args:
            contract_id: The contract ID (e.g., "Q001_PA01") or "*" for all
            callback: Function to call when contract loads
            priority: Execution priority (higher executes first)
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            contract_pattern: Optional regex pattern for contract matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.CONTRACT_LOADING,
            contract_id,
            callback,
            priority,
            name or f"contract_load_{contract_id}",
            condition,
            contract_pattern,
            metadata,
            tags,
        )

    def on_contract_method_injecting(
        self,
        contract_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        contract_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for method injection.

        Args:
            contract_id: The contract ID or "*" for all
            callback: Function to call when methods are injected
            priority: Execution priority
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            contract_pattern: Optional regex pattern for contract matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.CONTRACT_METHOD_INJECTING,
            contract_id,
            callback,
            priority,
            name or f"contract_inject_{contract_id}",
            condition,
            contract_pattern,
            metadata,
            tags,
        )

    def on_contract_executing(
        self,
        contract_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        contract_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for contract execution.

        Args:
            contract_id: The contract ID or "*" for all
            callback: Function to call when contract executes
            priority: Execution priority
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            contract_pattern: Optional regex pattern for contract matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.CONTRACT_EXECUTING,
            contract_id,
            callback,
            priority,
            name or f"contract_execute_{contract_id}",
            condition,
            contract_pattern,
            metadata,
            tags,
        )

    def on_contract_veto_check(
        self,
        contract_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        contract_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for veto check.

        Args:
            contract_id: The contract ID or "*" for all
            callback: Function to call during veto check
            priority: Execution priority
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            contract_pattern: Optional regex pattern for contract matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.CONTRACT_VETO_CHECK,
            contract_id,
            callback,
            priority,
            name or f"contract_veto_{contract_id}",
            condition,
            contract_pattern,
            metadata,
            tags,
        )

    def on_contract_fusion(
        self,
        contract_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        name: Optional[str] = None,
        condition: Optional[Callable[[TriggerContext], bool]] = None,
        contract_pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ) -> str:
        """
        Register callback for contract fusion.

        Args:
            contract_id: The contract ID or "*" for all
            callback: Function to call during fusion
            priority: Execution priority
            name: Optional trigger name
            condition: Optional predicate for conditional execution
            contract_pattern: Optional regex pattern for contract matching
            metadata: Optional metadata dict
            tags: Optional tags for categorization

        Returns:
            Registration ID
        """
        return self._register_internal(
            TriggerEvent.CONTRACT_FUSION,
            contract_id,
            callback,
            priority,
            name or f"contract_fusion_{contract_id}",
            condition,
            contract_pattern,
            metadata,
            tags,
        )

    def on_any_contract_event(
        self,
        contract_id: str,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        tags: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Register callback for ALL contract events for a contract ID.

        Args:
            contract_id: The contract ID or "*" for all
            callback: Function to call on any contract event
            priority: Execution priority
            tags: Optional tags for categorization

        Returns:
            List of registration IDs
        """
        reg_ids = []
        all_tags = (tags or set()) | {f"all_events_{contract_id}"}

        for event in self._EVENT_MAP.values():
            reg_id = self._register_internal(
                event, contract_id, callback, priority, tags=all_tags
            )
            reg_ids.append(reg_id)

        return reg_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # BULK REGISTRATION
    # ═══════════════════════════════════════════════════════════════════════════

    def register_contract_lifecycle(
        self,
        contract_id: str,
        on_loading: Optional[Callable[[TriggerContext], None]] = None,
        on_method_injecting: Optional[Callable[[TriggerContext], None]] = None,
        on_executing: Optional[Callable[[TriggerContext], None]] = None,
        on_veto_check: Optional[Callable[[TriggerContext], None]] = None,
        on_fusion: Optional[Callable[[TriggerContext], None]] = None,
        priority: int = 0,
        tags: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Register callbacks for all lifecycle events of a contract.

        Args:
            contract_id: The contract ID (e.g., "Q001_PA01")
            on_loading: Callback for contract loading
            on_method_injecting: Callback for method injection
            on_executing: Callback for execution
            on_veto_check: Callback for veto check
            on_fusion: Callback for fusion
            priority: Execution priority for all callbacks
            tags: Tags to apply to all registrations

        Returns:
            List of registration IDs
        """
        registration_ids = []
        lifecycle_tags = (tags or set()) | {f"lifecycle_{contract_id}"}

        if on_loading:
            reg_id = self.on_contract_loading(
                contract_id, on_loading, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        if on_method_injecting:
            reg_id = self.on_contract_method_injecting(
                contract_id, on_method_injecting, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        if on_executing:
            reg_id = self.on_contract_executing(
                contract_id, on_executing, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        if on_veto_check:
            reg_id = self.on_contract_veto_check(
                contract_id, on_veto_check, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        if on_fusion:
            reg_id = self.on_contract_fusion(
                contract_id, on_fusion, priority, tags=lifecycle_tags
            )
            registration_ids.append(reg_id)

        logger.info(f"Registered {len(registration_ids)} lifecycle triggers for {contract_id}")
        return registration_ids

    def register_question_range(
        self,
        q_start: int,
        q_end: int,
        event: TriggerEvent,
        callback: Callable[[TriggerContext], None],
        policy_area: Optional[str] = None,
        priority: int = 0,
        tags: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Register callback for a range of question contracts.

        Args:
            q_start: Start of Q range (e.g., 1 for Q001)
            q_end: End of Q range inclusive (e.g., 30 for Q030)
            event: The event to register for
            callback: Function to call
            policy_area: Optional PA filter (e.g., "PA01")
            priority: Execution priority
            tags: Optional tags

        Returns:
            List of registration IDs
        """
        reg_ids = []
        range_tags = (tags or set()) | {f"q_range_{q_start:03d}_{q_end:03d}"}

        for q_num in range(q_start, q_end + 1):
            if policy_area:
                contract_id = f"Q{q_num:03d}_{policy_area}"
                reg_id = self._register_internal(
                    event, contract_id, callback, priority, tags=range_tags
                )
                reg_ids.append(reg_id)
            else:
                # Register for all policy areas
                for pa in self._POLICY_AREAS:
                    pa_code = pa.split("_")[0]
                    contract_id = f"Q{q_num:03d}_{pa_code}"
                    reg_id = self._register_internal(
                        event, contract_id, callback, priority, tags=range_tags
                    )
                    reg_ids.append(reg_id)

        logger.info(f"Registered {len(reg_ids)} triggers for Q{q_start:03d}-Q{q_end:03d}")
        return reg_ids

    def register_policy_area(
        self,
        policy_area: str,
        event: TriggerEvent,
        callback: Callable[[TriggerContext], None],
        priority: int = 0,
        tags: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Register callback for all contracts in a policy area.

        Args:
            policy_area: The policy area code (e.g., "PA01")
            event: The event to register for
            callback: Function to call
            priority: Execution priority
            tags: Optional tags

        Returns:
            List of registration IDs
        """
        # Use pattern matching for efficiency
        pattern = f"Q\\d{{3}}_{policy_area}"
        pa_tags = (tags or set()) | {f"policy_area_{policy_area}"}

        reg_id = self._register_internal(
            event,
            "*",  # Wildcard
            callback,
            priority,
            name=f"{event.name.lower()}_{policy_area}_all",
            contract_pattern=pattern,
            tags=pa_tags,
        )
        return [reg_id]

    # ═══════════════════════════════════════════════════════════════════════════
    # EMISSION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _emit_internal(
        self,
        event: TriggerEvent,
        contract_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Internal emission with history tracking.

        Args:
            event: The event to emit
            contract_id: The contract ID
            payload: Optional payload data

        Returns:
            Number of triggers executed
        """
        context = TriggerContext(
            event=event,
            timestamp=datetime.utcnow(),
            contract_id=contract_id,
            payload=payload or {},
        )

        start_time = time.perf_counter()
        executed = self._registry.emit(event, context)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Update global metrics
        with self._lock:
            self._global_metrics.invocation_count += 1
            self._global_metrics.total_execution_time_ms += elapsed_ms
            self._global_metrics.last_invocation = datetime.utcnow()
            self._global_metrics.last_contract_id = contract_id

            if event == TriggerEvent.CONTRACT_METHOD_INJECTING:
                self._global_metrics.methods_injected += 1
            elif event == TriggerEvent.CONTRACT_VETO_CHECK:
                if (payload or {}).get("vetoed", False):
                    self._global_metrics.veto_count += 1
            elif event == TriggerEvent.CONTRACT_FUSION:
                self._global_metrics.fusion_count += 1

        # Record history
        history_entry = {
            "event": event.value,
            "contract_id": contract_id,
            "timestamp": context.timestamp.isoformat(),
            "triggers_executed": executed,
            "execution_time_ms": round(elapsed_ms, 2),
            "payload_keys": list((payload or {}).keys()),
        }

        with self._lock:
            self._emission_history.append(history_entry)
            if len(self._emission_history) > self._max_history_size:
                self._emission_history = self._emission_history[-self._max_history_size:]

        logger.debug(
            f"Emitted {event.value} for {contract_id}: "
            f"{executed} triggers in {elapsed_ms:.2f}ms"
        )
        return executed

    def emit_contract_loading(
        self, contract_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit contract loading event."""
        return self._emit_internal(TriggerEvent.CONTRACT_LOADING, contract_id, payload)

    def emit_contract_method_injecting(
        self, contract_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit method injection event."""
        return self._emit_internal(
            TriggerEvent.CONTRACT_METHOD_INJECTING, contract_id, payload
        )

    def emit_contract_executing(
        self, contract_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit contract execution event."""
        return self._emit_internal(TriggerEvent.CONTRACT_EXECUTING, contract_id, payload)

    def emit_contract_veto_check(
        self, contract_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit veto check event."""
        return self._emit_internal(TriggerEvent.CONTRACT_VETO_CHECK, contract_id, payload)

    def emit_contract_fusion(
        self, contract_id: str, payload: Optional[Dict[str, Any]] = None
    ) -> int:
        """Emit contract fusion event."""
        return self._emit_internal(TriggerEvent.CONTRACT_FUSION, contract_id, payload)

    def emit_contract_lifecycle(
        self,
        contract_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """
        Emit all lifecycle events for a contract in sequence.

        Args:
            contract_id: The contract ID
            payload: Payload to pass to all events

        Returns:
            Dict mapping event names to execution counts
        """
        results = {}
        results["loading"] = self.emit_contract_loading(contract_id, payload)
        results["method_injecting"] = self.emit_contract_method_injecting(contract_id, payload)
        results["executing"] = self.emit_contract_executing(contract_id, payload)
        results["veto_check"] = self.emit_contract_veto_check(contract_id, payload)
        results["fusion"] = self.emit_contract_fusion(contract_id, payload)
        return results

    # ═══════════════════════════════════════════════════════════════════════════
    # DEREGISTRATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def unregister(self, registration_id: str) -> bool:
        """
        Unregister a trigger by its registration ID.

        Args:
            registration_id: The registration ID returned from registration

        Returns:
            True if successfully unregistered
        """
        with self._lock:
            if registration_id not in self._registrations:
                return False

            reg = self._registrations[registration_id]

            # Remove from registry
            self._registry.unregister(reg.event, reg.name)

            # Remove from indices
            if reg.contract_id in self._contract_registrations:
                self._contract_registrations[reg.contract_id].discard(registration_id)
            if reg.event in self._event_registrations:
                self._event_registrations[reg.event].discard(registration_id)

            # Remove registration
            del self._registrations[registration_id]

        logger.debug(f"Unregistered trigger '{reg.name}'")
        return True

    def unregister_contract(self, contract_id: str) -> int:
        """
        Unregister all triggers for a specific contract.

        Args:
            contract_id: The contract ID

        Returns:
            Number of triggers unregistered
        """
        with self._lock:
            reg_ids = list(self._contract_registrations.get(contract_id, set()))

        count = 0
        for reg_id in reg_ids:
            if self.unregister(reg_id):
                count += 1

        logger.info(f"Unregistered {count} triggers for contract {contract_id}")
        return count

    def unregister_by_tag(self, tag: str) -> int:
        """
        Unregister all triggers with a specific tag.

        Args:
            tag: The tag to match

        Returns:
            Number of triggers unregistered
        """
        with self._lock:
            matching_ids = [
                reg_id
                for reg_id, reg in self._registrations.items()
                if tag in reg.tags
            ]

        count = 0
        for reg_id in matching_ids:
            if self.unregister(reg_id):
                count += 1

        logger.info(f"Unregistered {count} triggers with tag '{tag}'")
        return count

    def unregister_by_event(self, event: TriggerEvent) -> int:
        """
        Unregister all triggers for a specific event type.

        Args:
            event: The event type

        Returns:
            Number of triggers unregistered
        """
        with self._lock:
            reg_ids = list(self._event_registrations.get(event, set()))

        count = 0
        for reg_id in reg_ids:
            if self.unregister(reg_id):
                count += 1

        logger.info(f"Unregistered {count} triggers for event {event.value}")
        return count

    def unregister_policy_area(self, policy_area: str) -> int:
        """
        Unregister all triggers for a policy area.

        Args:
            policy_area: The policy area code (e.g., "PA01")

        Returns:
            Number of triggers unregistered
        """
        return self.unregister_by_tag(f"policy_area_{policy_area}")

    def clear_all(self) -> int:
        """
        Clear all registered contract triggers.

        Returns:
            Number of triggers cleared
        """
        with self._lock:
            count = len(self._registrations)
            reg_ids = list(self._registrations.keys())

        for reg_id in reg_ids:
            self.unregister(reg_id)

        logger.info(f"Cleared {count} contract triggers")
        return count

    # ═══════════════════════════════════════════════════════════════════════════
    # STATE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    def pause(self, registration_id: str) -> bool:
        """Pause a trigger (prevents execution but keeps registration)."""
        with self._lock:
            if registration_id in self._registrations:
                self._registrations[registration_id].state = TriggerState.PAUSED
                return True
        return False

    def resume(self, registration_id: str) -> bool:
        """Resume a paused trigger."""
        with self._lock:
            if registration_id in self._registrations:
                self._registrations[registration_id].state = TriggerState.ACTIVE
                return True
        return False

    def disable(self, registration_id: str) -> bool:
        """Disable a trigger."""
        with self._lock:
            if registration_id in self._registrations:
                self._registrations[registration_id].state = TriggerState.DISABLED
                return True
        return False

    def pause_contract(self, contract_id: str) -> int:
        """Pause all triggers for a contract."""
        with self._lock:
            reg_ids = self._contract_registrations.get(contract_id, set())
            count = 0
            for reg_id in reg_ids:
                if reg_id in self._registrations:
                    self._registrations[reg_id].state = TriggerState.PAUSED
                    count += 1
        return count

    def resume_contract(self, contract_id: str) -> int:
        """Resume all triggers for a contract."""
        with self._lock:
            reg_ids = self._contract_registrations.get(contract_id, set())
            count = 0
            for reg_id in reg_ids:
                if reg_id in self._registrations:
                    self._registrations[reg_id].state = TriggerState.ACTIVE
                    count += 1
        return count

    def pause_policy_area(self, policy_area: str) -> int:
        """Pause all triggers for a policy area."""
        with self._lock:
            count = 0
            for reg in self._registrations.values():
                if f"policy_area_{policy_area}" in reg.tags:
                    reg.state = TriggerState.PAUSED
                    count += 1
        return count

    def resume_policy_area(self, policy_area: str) -> int:
        """Resume all triggers for a policy area."""
        with self._lock:
            count = 0
            for reg in self._registrations.values():
                if f"policy_area_{policy_area}" in reg.tags:
                    reg.state = TriggerState.ACTIVE
                    count += 1
        return count

    # ═══════════════════════════════════════════════════════════════════════════
    # INTROSPECTION & DIAGNOSTICS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_registration(self, registration_id: str) -> Optional[ContractRegistration]:
        """Get registration details by ID."""
        with self._lock:
            return self._registrations.get(registration_id)

    def list_registrations(
        self,
        contract_id: Optional[str] = None,
        event: Optional[TriggerEvent] = None,
        tag: Optional[str] = None,
        state: Optional[TriggerState] = None,
        policy_area: Optional[str] = None,
    ) -> List[ContractRegistration]:
        """
        List registrations with optional filters.

        Args:
            contract_id: Filter by contract ID
            event: Filter by event type
            tag: Filter by tag
            state: Filter by state
            policy_area: Filter by policy area code

        Returns:
            List of matching registrations
        """
        with self._lock:
            results = list(self._registrations.values())

        if contract_id is not None:
            results = [r for r in results if r.contract_id == contract_id]
        if event is not None:
            results = [r for r in results if r.event == event]
        if tag is not None:
            results = [r for r in results if tag in r.tags]
        if state is not None:
            results = [r for r in results if r.state == state]
        if policy_area is not None:
            pa_tag = f"policy_area_{policy_area}"
            results = [r for r in results if pa_tag in r.tags or policy_area in r.contract_id]

        return results

    def get_metrics(self, registration_id: str) -> Optional[ContractMetrics]:
        """Get metrics for a specific registration."""
        with self._lock:
            reg = self._registrations.get(registration_id)
            return reg.metrics if reg else None

    def get_global_metrics(self) -> ContractMetrics:
        """Get global contract metrics."""
        with self._lock:
            return self._global_metrics

    def get_aggregated_metrics(
        self,
        contract_id: Optional[str] = None,
        policy_area: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get aggregated metrics across registrations.

        Args:
            contract_id: Optional filter by contract ID
            policy_area: Optional filter by policy area

        Returns:
            Aggregated metrics dict
        """
        registrations = self.list_registrations(
            contract_id=contract_id, policy_area=policy_area
        )

        total_invocations = sum(r.metrics.invocation_count for r in registrations)
        total_successes = sum(r.metrics.success_count for r in registrations)
        total_failures = sum(r.metrics.failure_count for r in registrations)
        total_time = sum(r.metrics.total_execution_time_ms for r in registrations)
        total_vetoes = sum(r.metrics.veto_count for r in registrations)
        total_fusions = sum(r.metrics.fusion_count for r in registrations)
        total_methods = sum(r.metrics.methods_injected for r in registrations)

        return {
            "registration_count": len(registrations),
            "total_invocations": total_invocations,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "success_rate": (total_successes / total_invocations * 100) if total_invocations > 0 else 100.0,
            "total_execution_time_ms": round(total_time, 2),
            "avg_execution_time_ms": round(total_time / total_invocations, 2) if total_invocations > 0 else 0.0,
            "total_vetoes": total_vetoes,
            "veto_rate": (total_vetoes / total_invocations * 100) if total_invocations > 0 else 0.0,
            "total_fusions": total_fusions,
            "total_methods_injected": total_methods,
        }

    def get_emission_history(
        self,
        limit: int = 100,
        contract_id: Optional[str] = None,
        event: Optional[TriggerEvent] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get emission history with optional filters.

        Args:
            limit: Maximum entries to return
            contract_id: Filter by contract ID
            event: Filter by event type

        Returns:
            List of history entries
        """
        with self._lock:
            history = list(self._emission_history)

        if contract_id is not None:
            history = [h for h in history if h.get("contract_id") == contract_id]
        if event is not None:
            history = [h for h in history if h.get("event") == event.value]

        return history[-limit:]

    def get_registered_contracts(self) -> List[str]:
        """Get list of all contracts with registered triggers."""
        with self._lock:
            return [
                contract_id
                for contract_id, reg_ids in self._contract_registrations.items()
                if reg_ids
            ]

    def get_registration_count(
        self,
        contract_id: Optional[str] = None,
        event: Optional[TriggerEvent] = None,
    ) -> int:
        """Get count of registrations with optional filters."""
        return len(self.list_registrations(contract_id=contract_id, event=event))

    def get_policy_area_stats(self) -> Dict[str, Dict[str, int]]:
        """Get registration statistics by policy area."""
        stats = {}
        for pa in self._POLICY_AREAS:
            pa_code = pa.split("_")[0]
            registrations = self.list_registrations(policy_area=pa_code)
            stats[pa_code] = {
                "registrations": len(registrations),
                "active": sum(1 for r in registrations if r.state == TriggerState.ACTIVE),
                "paused": sum(1 for r in registrations if r.state == TriggerState.PAUSED),
                "total_invocations": sum(r.metrics.invocation_count for r in registrations),
            }
        return stats

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the contract trigger system.

        Returns:
            Health status dict
        """
        with self._lock:
            active_count = sum(
                1 for r in self._registrations.values()
                if r.state == TriggerState.ACTIVE
            )
            paused_count = sum(
                1 for r in self._registrations.values()
                if r.state == TriggerState.PAUSED
            )
            disabled_count = sum(
                1 for r in self._registrations.values()
                if r.state == TriggerState.DISABLED
            )

            # Check for failing triggers
            failing_triggers = [
                r.name
                for r in self._registrations.values()
                if r.metrics.failure_count > 0 and r.metrics.success_rate < 90
            ]

            # Check high veto rate triggers
            high_veto_triggers = [
                r.name
                for r in self._registrations.values()
                if r.metrics.veto_rate > 50
            ]

            # Check Q coverage (Q001-Q030 base)
            covered_questions = set()
            for contract_id in self._contract_registrations.keys():
                if contract_id.startswith("Q"):
                    q_num = contract_id.split("_")[0]
                    covered_questions.add(q_num)
            expected_questions = {f"Q{num:03d}" for num in range(1, 31)}  # Q001-Q030

            uncovered_questions = sorted(expected_questions - covered_questions)

            return {
                "status": "healthy",
                "active_triggers": active_count,
                "paused_triggers": paused_count,
                "disabled_triggers": disabled_count,
                "failing_triggers": failing_triggers,
                "high_veto_triggers": high_veto_triggers,
                "uncovered_questions": uncovered_questions,
            }
