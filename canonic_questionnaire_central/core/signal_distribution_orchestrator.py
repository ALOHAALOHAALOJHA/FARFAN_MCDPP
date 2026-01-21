"""
Signal Distribution Orchestrator (SDO)

SOTA Event-Driven Architecture for SISAS:
- Pub/Sub pattern with scope-based routing
- Capability matching for consumer eligibility
- Value gating with empirical thresholds
- Deduplication via content hashing
- Dead Letter Queue for failed signals
- Full audit trail for observability

This is the HEART of the TRUE signal system - replacing the static data loader
with an active pub/sub engine.

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

from .signal import Signal, SignalScope, SignalType

logger = logging.getLogger(__name__)


class DeadLetterReason(str, Enum):
    """Reasons a signal ends up in dead letter queue."""
    
    INVALID_SCOPE = "INVALID_SCOPE"
    DUPLICATE = "DUPLICATE"
    LOW_VALUE = "LOW_VALUE"
    NO_CONSUMER = "NO_CONSUMER"
    CAPABILITY_MISMATCH = "CAPABILITY_MISMATCH"
    HANDLER_ERROR = "HANDLER_ERROR"
    VALIDATION_FAILED = "VALIDATION_FAILED"


@dataclass
class Consumer:
    """
    A registered consumer of signals.
    
    Consumers declare:
    - What scopes they listen to
    - What capabilities they have
    - A handler function to process signals
    """
    
    consumer_id: str
    scopes: List[SignalScope]
    capabilities: Set[str]
    handler: Callable[[Signal], None]
    enabled: bool = True
    signals_processed: int = 0
    errors: int = 0
    
    def can_handle(self, signal: Signal) -> tuple[bool, str]:
        """
        Check if this consumer can handle a signal.
        
        Returns (can_handle, reason_if_not).
        """
        # Check scope match
        scope_match = any(
            signal.scope.matches(consumer_scope) 
            for consumer_scope in self.scopes
        )
        if not scope_match:
            return False, "SCOPE_MISMATCH"
        
        # Check capabilities
        required = set(signal.capabilities_required)
        if not required.issubset(self.capabilities):
            missing = required - self.capabilities
            return False, f"MISSING_CAPABILITIES: {missing}"
        
        return True, "OK"


@dataclass
class DeadLetter:
    """A signal that failed to be delivered."""
    
    dead_letter_id: str
    signal: Signal
    reason: DeadLetterReason
    detail: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dead_letter_id": self.dead_letter_id,
            "signal": self.signal.to_dict(),
            "reason": self.reason.value,
            "detail": self.detail,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AuditEntry:
    """Audit trail entry for signal operations."""
    
    entry_id: str
    action: str  # DISPATCHED, DELIVERED, REJECTED, DEAD_LETTERED
    signal_id: str
    signal_type: str
    consumer_id: Optional[str]
    detail: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "action": self.action,
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "consumer_id": self.consumer_id,
            "detail": self.detail,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class RoutingRules:
    """Configuration for signal routing."""

    # Minimum empirical availability for non-enrichment signals
    empirical_availability_min: float = 0.30

    # Signal types allowed per phase
    phase_routing: Dict[str, List[str]] = field(default_factory=dict)

    # Required capabilities per signal type
    capabilities_required: Dict[str, List[str]] = field(default_factory=dict)

    # Dead letter configuration
    dead_letter_enabled: bool = True
    dead_letter_path: str = "_registry/dead_letter/"

    # Deduplication window (signals with same hash within this many seconds are dupes)
    dedup_window_seconds: int = 300

    # Gate rules for 4-gate validation
    gate_rules: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RoutingRules:
        # Support both old 'routing' key and new 'phase_signal_alignment' key
        phase_routing = data.get("phase_signal_alignment", data.get("routing", {}))

        # Get dead_letter config from routing_rules or top-level
        dead_letter_config = data.get("routing_rules", {}).get("dead_letter", data.get("dead_letter", {}))

        return cls(
            empirical_availability_min=data.get("thresholds", {}).get("empirical_availability_min", 0.30),
            phase_routing=phase_routing,
            capabilities_required=data.get("capability_requirements", data.get("capabilities_required", {})),
            dead_letter_enabled=dead_letter_config.get("enabled", True),
            dead_letter_path=dead_letter_config.get("path", "_registry/dead_letter/"),
            dedup_window_seconds=data.get("routing_rules", {}).get("deduplication", {}).get("window_seconds", data.get("dedup_window_seconds", 300)),
            gate_rules=data.get("gate_rules", {})
        )


class SignalDistributionOrchestrator:
    """
    The Signal Distribution Orchestrator (SDO) is the pub/sub engine.
    
    Responsibilities:
    1. Accept signals from producers (extractors, phases)
    2. Validate signals (scope, value, integrity)
    3. Deduplicate based on content hash
    4. Route to eligible consumers based on scope + capabilities
    5. Dead letter undeliverable signals
    6. Maintain full audit trail
    
    This is the TRUE signal system - active routing, not passive loading.
    """
    
    def __init__(self, rules_path: Optional[str] = None, rules: Optional[RoutingRules] = None):
        """
        Initialize SDO with routing rules.
        
        Args:
            rules_path: Path to irrigation_validation_rules.json
            rules: Pre-loaded RoutingRules (alternative to path)
        """
        if rules:
            self.rules = rules
        elif rules_path:
            self.rules = self._load_rules(rules_path)
        else:
            self.rules = RoutingRules()
        
        # Consumer registry
        self.consumers: Dict[str, Consumer] = {}
        
        # Signal cache for deduplication
        self._signal_cache: Dict[str, tuple[Signal, datetime]] = {}
        
        # Dead letter queue
        self._dead_letters: List[DeadLetter] = []
        
        # Audit log
        self._audit_log: List[AuditEntry] = []
        
        # Metrics
        self._metrics = {
            "signals_dispatched": 0,
            "signals_delivered": 0,
            "signals_rejected": 0,
            "signals_deduplicated": 0,
            "dead_letters": 0,
            "consumer_errors": 0
        }
        
        logger.info("SignalDistributionOrchestrator initialized", extra={
            "rules": {
                "empirical_min": self.rules.empirical_availability_min,
                "phases_configured": len(self.rules.phase_routing),
                "dead_letter_enabled": self.rules.dead_letter_enabled
            }
        })
    
    def _load_rules(self, path: str) -> RoutingRules:
        """Load routing rules from JSON file."""
        try:
            with open(path) as f:
                data = json.load(f)
            return RoutingRules.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load rules from {path}: {e}, using defaults")
            return RoutingRules()
    
    # =========================================================================
    # CONSUMER REGISTRATION
    # =========================================================================
    
    def register_consumer(
        self,
        consumer_id: str,
        scopes: List[Dict[str, str]],
        capabilities: List[str],
        handler: Callable[[Signal], None]
    ) -> None:
        """
        Register a consumer to receive signals.
        
        Args:
            consumer_id: Unique identifier for the consumer
            scopes: List of scope dicts that this consumer listens to
            capabilities: List of capability strings this consumer has
            handler: Callable that processes signals
        """
        scope_objects = [SignalScope(**s) for s in scopes]
        
        consumer = Consumer(
            consumer_id=consumer_id,
            scopes=scope_objects,
            capabilities=set(capabilities),
            handler=handler
        )
        
        self.consumers[consumer_id] = consumer
        
        logger.info(f"Consumer registered: {consumer_id}", extra={
            "scopes": [s.to_dict() for s in scope_objects],
            "capabilities": capabilities
        })
    
    def unregister_consumer(self, consumer_id: str) -> bool:
        """Unregister a consumer."""
        if consumer_id in self.consumers:
            del self.consumers[consumer_id]
            logger.info(f"Consumer unregistered: {consumer_id}")
            return True
        return False

    # =========================================================================
    # 4-GATE VALIDATION SYSTEM
    # =========================================================================

    def _validate_gate_1_scope_alignment(self, signal: Signal) -> tuple[bool, List[str]]:
        """
        Gate 1: Scope Alignment Validation

        Validates:
        - SCOPE-001: Valid Phase
        - SCOPE-002: Valid Policy Area
        - SCOPE-003: Signal Type Phase Alignment

        Returns (is_valid, errors)
        """
        errors = []

        # SCOPE-001: Valid Phase
        valid_phases = ['phase_0', 'phase_1', 'phase_2', 'phase_3', 'phase_4',
                       'phase_5', 'phase_6', 'phase_7', 'phase_8', 'phase_9']
        if signal.scope.phase not in valid_phases:
            errors.append(f"INVALID_PHASE: {signal.scope.phase} not in {valid_phases}")

        # SCOPE-002: Valid Policy Area
        valid_pas = ['PA01', 'PA02', 'PA03', 'PA04', 'PA05', 'PA06', 'PA07',
                    'PA08', 'PA09', 'PA10', 'ALL', 'CROSS_CUTTING']
        if hasattr(signal.scope, 'policy_area') and signal.scope.policy_area:
            if signal.scope.policy_area not in valid_pas:
                errors.append(f"INVALID_POLICY_AREA: {signal.scope.policy_area} not in {valid_pas}")

        # SCOPE-003: Signal Type Phase Alignment
        if not self._validate_scope_routing(signal):
            signal_type_value = signal.signal_type.value if isinstance(signal.signal_type, SignalType) else signal.signal_type
            errors.append(f"SIGNAL_TYPE_PHASE_MISMATCH: {signal_type_value} not allowed in {signal.scope.phase}")

        return len(errors) == 0, errors

    def _validate_gate_2_value_add(self, signal: Signal) -> tuple[bool, List[str]]:
        """
        Gate 2: Value Add Validation

        Validates:
        - VALUE-001: Empirical Availability Threshold (>= 0.30 or enrichment)
        - VALUE-002: Valid Range (0.0 <= availability <= 1.0)

        Returns (is_valid, errors)
        """
        errors = []
        warnings = []

        # VALUE-002: Valid Range (CRITICAL)
        if hasattr(signal, 'empirical_availability'):
            if not (0.0 <= signal.empirical_availability <= 1.0):
                errors.append(f"INVALID_AVAILABILITY_RANGE: {signal.empirical_availability} not in [0.0, 1.0]")

            # VALUE-001: Empirical Availability Threshold (WARNING)
            is_enrichment = getattr(signal, 'enrichment', False) or getattr(signal, 'is_enrichment', False)
            if not is_enrichment and signal.empirical_availability < 0.30:
                warnings.append(f"LOW_EMPIRICAL_AVAILABILITY: {signal.empirical_availability} < 0.30")

        return len(errors) == 0, errors + warnings

    def _validate_gate_3_capability(self, signal: Signal) -> tuple[bool, List[str]]:
        """
        Gate 3: Capability Validation

        Validates:
        - CAP-001: At least one consumer has required capabilities
        - CAP-002: At least one eligible consumer exists

        Returns (is_valid, errors)
        """
        errors = []
        warnings = []

        # CAP-002: Check if at least one eligible consumer exists
        eligible_consumers = []
        for consumer_id, consumer in self.consumers.items():
            if consumer.enabled:
                can_handle, reason = consumer.can_handle(signal)
                if can_handle:
                    eligible_consumers.append(consumer_id)

        if not eligible_consumers:
            warnings.append(f"NO_ELIGIBLE_CONSUMER: No consumer can handle signal {signal.signal_id}")

        # CAP-001: Validate capability matching (checked in consumer.can_handle)
        # If we have eligible consumers, capabilities are satisfied

        return len(errors) == 0, errors + warnings

    def _validate_gate_4_irrigation_channel(self, signal: Signal) -> tuple[bool, List[str]]:
        """
        Gate 4: Irrigation Channel Validation (Post-Dispatch)

        Validates:
        - CHANNEL-001: Signal was routed
        - CHANNEL-002: At least one consumer received
        - CHANNEL-003: Audit entry created

        Returns (is_valid, errors)

        Note: This gate is applied AFTER dispatch.
        """
        errors = []
        warnings = []

        # CHANNEL-001: Signal was routed
        if not getattr(signal, '_routed', False):
            warnings.append("SIGNAL_NOT_ROUTED: Signal has not been routed yet")

        # CHANNEL-002: At least one consumer received
        consumers = getattr(signal, '_consumers', [])
        if not consumers:
            warnings.append("NO_CONSUMER_RECEIVED: No consumer has received this signal")

        # CHANNEL-003: Audit entry created (check if signal_id in audit trail)
        has_audit = any(entry.signal_id == signal.signal_id for entry in self._audit_trail)
        if not has_audit:
            errors.append(f"NO_AUDIT_ENTRY: No audit entry for signal {signal.signal_id}")

        return len(errors) == 0, errors + warnings

    def validate_all_gates(self, signal: Signal, post_dispatch: bool = False) -> tuple[bool, Dict[str, List[str]]]:
        """
        Validate signal through all 4 gates.

        Args:
            signal: Signal to validate
            post_dispatch: If True, includes Gate 4 (post-dispatch validation)

        Returns:
            (all_valid, gate_errors) where gate_errors is dict of gate -> error_list
        """
        gate_errors = {}

        # Gate 1: Scope Alignment
        valid_1, errors_1 = self._validate_gate_1_scope_alignment(signal)
        if errors_1:
            gate_errors["gate_1_scope_alignment"] = errors_1

        # Gate 2: Value Add
        valid_2, errors_2 = self._validate_gate_2_value_add(signal)
        if errors_2:
            gate_errors["gate_2_value_add"] = errors_2

        # Gate 3: Capability
        valid_3, errors_3 = self._validate_gate_3_capability(signal)
        if errors_3:
            gate_errors["gate_3_capability"] = errors_3

        # Gate 4: Irrigation Channel (only if post-dispatch)
        if post_dispatch:
            valid_4, errors_4 = self._validate_gate_4_irrigation_channel(signal)
            if errors_4:
                gate_errors["gate_4_irrigation_channel"] = errors_4

        all_valid = len(gate_errors) == 0
        return all_valid, gate_errors

    # =========================================================================
    # SIGNAL DISPATCH (THE CORE)
    # =========================================================================

    def dispatch(self, signal: Signal) -> bool:
        """
        Dispatch a signal through the system.
        
        This is the main entry point for all signals.
        
        Returns True if signal was delivered to at least one consumer.
        """
        self._metrics["signals_dispatched"] += 1
        
        # 1. VALIDATE
        is_valid, errors = signal.validate()
        if not is_valid:
            self._dead_letter(signal, DeadLetterReason.VALIDATION_FAILED, "; ".join(errors))
            self._audit("REJECTED", signal, detail=f"Validation failed: {errors}")
            self._metrics["signals_rejected"] += 1
            return False
        
        # 2. SCOPE VALIDATION against routing rules
        if not self._validate_scope_routing(signal):
            self._dead_letter(signal, DeadLetterReason.INVALID_SCOPE, 
                            f"Type {signal.signal_type} not allowed in {signal.scope.phase}")
            self._audit("REJECTED", signal, detail="Invalid scope/type combination")
            self._metrics["signals_rejected"] += 1
            return False
        
        # 3. DEDUPLICATION
        content_hash = signal.content_hash()
        if self._is_duplicate(content_hash):
            self._audit("DEDUPLICATED", signal, detail=f"Hash collision: {content_hash[:16]}")
            self._metrics["signals_deduplicated"] += 1
            return False  # Not an error, just skipped
        
        # 4. VALUE GATE (skip for enrichment signals)
        if not signal.enrichment:
            if signal.empirical_availability < self.rules.empirical_availability_min:
                self._dead_letter(signal, DeadLetterReason.LOW_VALUE,
                                f"availability={signal.empirical_availability} < {self.rules.empirical_availability_min}")
                self._audit("REJECTED", signal, detail="Below empirical threshold")
                self._metrics["signals_rejected"] += 1
                return False
        
        # 5. ROUTE TO CONSUMERS
        delivered_to = []
        for consumer_id, consumer in self.consumers.items():
            if not consumer.enabled:
                continue
            
            can_handle, reason = consumer.can_handle(signal)
            if not can_handle:
                continue
            
            # Deliver
            try:
                consumer.handler(signal)
                consumer.signals_processed += 1
                delivered_to.append(consumer_id)
                self._audit("DELIVERED", signal, consumer_id=consumer_id)
            except Exception as e:
                consumer.errors += 1
                self._metrics["consumer_errors"] += 1
                logger.error(f"Consumer {consumer_id} error: {e}", exc_info=True)
                self._dead_letter(signal, DeadLetterReason.HANDLER_ERROR, 
                                f"Consumer {consumer_id}: {e}")
        
        # 6. HANDLE NO CONSUMERS
        if not delivered_to:
            self._dead_letter(signal, DeadLetterReason.NO_CONSUMER,
                            f"No consumer for scope={signal.scope.to_dict()}")
            self._audit("DEAD_LETTERED", signal, detail="No eligible consumers")
            return False
        
        # 7. CACHE for deduplication
        self._signal_cache[content_hash] = (signal, datetime.now(timezone.utc))
        signal._routed = True
        signal._consumers = delivered_to
        
        self._metrics["signals_delivered"] += 1
        
        logger.debug(f"Signal {signal.signal_id} delivered to {delivered_to}")
        return True
    
    def dispatch_batch(self, signals: List[Signal]) -> Dict[str, int]:
        """
        Dispatch multiple signals.
        
        Returns counts of delivered/rejected/deduplicated.
        """
        results = {"delivered": 0, "rejected": 0, "deduplicated": 0}
        
        for signal in signals:
            before_dedup = self._metrics["signals_deduplicated"]
            success = self.dispatch(signal)
            
            if success:
                results["delivered"] += 1
            elif self._metrics["signals_deduplicated"] > before_dedup:
                results["deduplicated"] += 1
            else:
                results["rejected"] += 1
        
        return results
    
    # =========================================================================
    # VALIDATION & ROUTING HELPERS
    # =========================================================================
    
    def _validate_scope_routing(self, signal: Signal) -> bool:
        """Check if signal type is allowed in its declared phase."""
        phase = signal.scope.phase
        allowed_types = self.rules.phase_routing.get(phase, [])
        
        # If no rules for this phase, allow all
        if not allowed_types:
            return True
        
        signal_type_value = signal.signal_type.value if isinstance(signal.signal_type, SignalType) else signal.signal_type
        return signal_type_value in allowed_types
    
    def _is_duplicate(self, content_hash: str) -> bool:
        """Check if a signal with this hash was recently processed."""
        if content_hash not in self._signal_cache:
            return False
        
        _, timestamp = self._signal_cache[content_hash]
        age_seconds = (datetime.now(timezone.utc) - timestamp).total_seconds()
        
        if age_seconds > self.rules.dedup_window_seconds:
            # Old entry, remove and allow
            del self._signal_cache[content_hash]
            return False
        
        return True
    
    # =========================================================================
    # DEAD LETTER QUEUE
    # =========================================================================
    
    def _dead_letter(self, signal: Signal, reason: DeadLetterReason, detail: str = "") -> None:
        """Send a signal to the dead letter queue."""
        if not self.rules.dead_letter_enabled:
            return
        
        dl = DeadLetter(
            dead_letter_id=str(uuid4()),
            signal=signal,
            reason=reason,
            detail=detail,
            timestamp=datetime.now(timezone.utc)
        )
        
        self._dead_letters.append(dl)
        self._metrics["dead_letters"] += 1
        
        # Persist to disk
        self._persist_dead_letter(dl)
        
        logger.warning(f"Signal {signal.signal_id} dead-lettered: {reason.value} - {detail}")
    
    def _persist_dead_letter(self, dl: DeadLetter) -> None:
        """Persist dead letter to disk."""
        try:
            dl_path = Path(self.rules.dead_letter_path)
            dl_path.mkdir(parents=True, exist_ok=True)
            
            file_path = dl_path / f"{dl.dead_letter_id}.json"
            with open(file_path, 'w') as f:
                json.dump(dl.to_dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to persist dead letter: {e}")
    
    def get_dead_letters(self, reason: Optional[DeadLetterReason] = None) -> List[DeadLetter]:
        """Get dead letters, optionally filtered by reason."""
        if reason is None:
            return self._dead_letters.copy()
        return [dl for dl in self._dead_letters if dl.reason == reason]
    
    def replay_dead_letter(self, dead_letter_id: str) -> bool:
        """Attempt to replay a dead-lettered signal."""
        for dl in self._dead_letters:
            if dl.dead_letter_id == dead_letter_id:
                # Remove from dead letters
                self._dead_letters.remove(dl)
                # Re-dispatch
                return self.dispatch(dl.signal)
        return False
    
    # =========================================================================
    # AUDIT TRAIL
    # =========================================================================
    
    def _audit(self, action: str, signal: Signal, consumer_id: str = None, detail: str = "") -> None:
        """Record an audit entry."""
        entry = AuditEntry(
            entry_id=str(uuid4()),
            action=action,
            signal_id=signal.signal_id,
            signal_type=signal.signal_type.value if isinstance(signal.signal_type, SignalType) else str(signal.signal_type),
            consumer_id=consumer_id,
            detail=detail,
            timestamp=datetime.now(timezone.utc)
        )
        self._audit_log.append(entry)
    
    def get_audit_log(self, signal_id: Optional[str] = None) -> List[AuditEntry]:
        """Get audit entries, optionally filtered by signal ID."""
        if signal_id is None:
            return self._audit_log.copy()
        return [e for e in self._audit_log if e.signal_id == signal_id]
    
    # =========================================================================
    # METRICS & OBSERVABILITY
    # =========================================================================
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics."""
        return {
            **self._metrics,
            "consumers_registered": len(self.consumers),
            "consumers_enabled": sum(1 for c in self.consumers.values() if c.enabled),
            "cache_size": len(self._signal_cache),
            "audit_log_size": len(self._audit_log)
        }
    
    def get_consumer_stats(self) -> Dict[str, Dict[str, int]]:
        """Get per-consumer statistics."""
        return {
            cid: {
                "signals_processed": c.signals_processed,
                "errors": c.errors,
                "enabled": c.enabled
            }
            for cid, c in self.consumers.items()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the orchestrator."""
        dead_letter_rate = (
            self._metrics["dead_letters"] / self._metrics["signals_dispatched"]
            if self._metrics["signals_dispatched"] > 0 else 0
        )
        
        error_rate = (
            self._metrics["consumer_errors"] / self._metrics["signals_delivered"]
            if self._metrics["signals_delivered"] > 0 else 0
        )
        
        return {
            "status": "HEALTHY" if dead_letter_rate < 0.1 and error_rate < 0.05 else "DEGRADED",
            "dead_letter_rate": round(dead_letter_rate, 4),
            "error_rate": round(error_rate, 4),
            "consumers_healthy": sum(1 for c in self.consumers.values() if c.enabled and c.errors == 0),
            "consumers_total": len(self.consumers),
            "metrics": self.get_metrics()
        }
    
    # =========================================================================
    # CLEANUP
    # =========================================================================
    
    def clear_cache(self) -> int:
        """Clear the signal cache. Returns number of entries cleared."""
        count = len(self._signal_cache)
        self._signal_cache.clear()
        return count
    
    def clear_audit_log(self) -> int:
        """Clear the audit log. Returns number of entries cleared."""
        count = len(self._audit_log)
        self._audit_log.clear()
        return count
