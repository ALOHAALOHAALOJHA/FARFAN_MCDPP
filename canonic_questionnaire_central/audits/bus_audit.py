"""
Bus Audit System for SISAS

Provides comprehensive auditing, monitoring, and health analysis for both:
- Signal Distribution Orchestrator (SDO) - Main pub/sub bus
- Legacy SignalBus system - Category-based message buses

This module extends the existing audit trail patterns with bus-specific
metrics, correlation tracking, and sophisticated health monitoring.

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

from __future__ import annotations

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from .signal import Signal, SignalType, SignalScope
    from .signal_distribution_orchestrator import (
        SignalDistributionOrchestrator,
        Consumer,
        DeadLetter,
        DeadLetterReason,
        AuditEntry as SDOAuditEntry
    )

logger = logging.getLogger(__name__)


# =============================================================================
# BUS TYPE ENUMERATION
# =============================================================================

class BusSystemType(str, Enum):
    """Types of bus systems in SISAS."""
    SDO = "sdo"  # Signal Distribution Orchestrator (main system)
    LEGACY = "legacy"  # Legacy category-based bus


class LegacyBusType(str, Enum):
    """Legacy bus categories."""
    STRUCTURAL = "structural_bus"
    INTEGRITY = "integrity_bus"
    EPISTEMIC = "epistemic_bus"
    CONTRAST = "contrast_bus"
    OPERATIONAL = "operational_bus"
    CONSUMPTION = "consumption_bus"
    ORCHESTRATION = "orchestration_bus"
    UNIVERSAL = "universal_bus"


class BusAuditEventType(str, Enum):
    """Types of bus audit events."""
    # Signal lifecycle events
    SIGNAL_PUBLISHED = "SIGNAL_PUBLISHED"
    SIGNAL_DELIVERED = "SIGNAL_DELIVERED"
    SIGNAL_REJECTED = "SIGNAL_REJECTED"
    SIGNAL_DEDUPLICATED = "SIGNAL_DEDUPLICATED"
    SIGNAL_DEAD_LETTERED = "SIGNAL_DEAD_LETTERED"

    # Consumer events
    CONSUMER_REGISTERED = "CONSUMER_REGISTERED"
    CONSUMER_UNREGISTERED = "CONSUMER_UNREGISTERED"
    CONSUMER_ENABLED = "CONSUMER_ENABLED"
    CONSUMER_DISABLED = "CONSUMER_DISABLED"
    CONSUMER_ERROR = "CONSUMER_ERROR"

    # Bus events
    BUS_CREATED = "BUS_CREATED"
    BUS_HEALTH_CHECK = "BUS_HEALTH_CHECK"
    BUS_BACKPRESSURE = "BUS_BACKPRESSURE"
    BUS_OVERFLOW = "BUS_OVERFLOW"

    # Gate validation events (SDO)
    GATE_VALIDATION = "GATE_VALIDATION"
    GATE_PASSED = "GATE_PASSED"
    GATE_FAILED = "GATE_FAILED"

    # Correlation events
    SIGNAL_CORRELATION = "SIGNAL_CORRELATION"
    CAUSALITY_CHAIN = "CAUSALITY_CHAIN"


# =============================================================================
# BUS AUDIT ENTRY
# =============================================================================

@dataclass
class BusAuditEntry:
    """
    Comprehensive audit entry for bus operations.

    Extends the SDO AuditEntry pattern with bus-specific context,
    correlation tracking, and health metrics.
    """

    # Identity
    entry_id: str
    timestamp: datetime
    event_type: BusAuditEventType

    # Bus context
    bus_system: BusSystemType
    bus_name: Optional[str] = None  # e.g., "structural_bus" for legacy

    # Signal context
    signal_id: Optional[str] = None
    signal_type: Optional[str] = None
    signal_hash: Optional[str] = None  # Content hash for deduplication tracking

    # Consumer context
    consumer_id: Optional[str] = None
    consumer_capabilities: Optional[List[str]] = None

    # Event details
    detail: str = ""
    reason: Optional[str] = None  # For rejections, dead letters
    gate_name: Optional[str] = None  # For gate events

    # Correlation
    correlation_id: Optional[str] = None  # Links related audit entries
    parent_signal_id: Optional[str] = None  # For derived signals
    causality_chain: Optional[List[str]] = None  # Full chain of signal IDs

    # Metrics
    execution_time_ms: Optional[float] = None
    queue_depth: Optional[int] = None
    backpressure_ratio: Optional[float] = None

    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Blockchain-style chaining for integrity
    previous_hash: str = "GENESIS"
    entry_hash: str = field(init=False)

    def __post_init__(self):
        """Compute entry hash after initialization."""
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        self.entry_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA-256 hash for tamper detection."""
        data = {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "bus_system": self.bus_system.value,
            "bus_name": self.bus_name,
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "signal_hash": self.signal_hash,
            "consumer_id": self.consumer_id,
            "detail": self.detail,
            "reason": self.reason,
            "gate_name": self.gate_name,
            "correlation_id": self.correlation_id,
            "previous_hash": self.previous_hash,
        }
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify entry hasn't been tampered with."""
        return self._compute_hash() == self.entry_hash

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "bus_system": self.bus_system.value,
            "bus_name": self.bus_name,
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "signal_hash": self.signal_hash,
            "consumer_id": self.consumer_id,
            "consumer_capabilities": self.consumer_capabilities,
            "detail": self.detail,
            "reason": self.reason,
            "gate_name": self.gate_name,
            "correlation_id": self.correlation_id,
            "parent_signal_id": self.parent_signal_id,
            "causality_chain": self.causality_chain,
            "execution_time_ms": self.execution_time_ms,
            "queue_depth": self.queue_depth,
            "backpressure_ratio": self.backpressure_ratio,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BusAuditEntry:
        """Deserialize from dictionary."""
        return cls(
            entry_id=data["entry_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            event_type=BusAuditEventType(data["event_type"]),
            bus_system=BusSystemType(data["bus_system"]),
            bus_name=data.get("bus_name"),
            signal_id=data.get("signal_id"),
            signal_type=data.get("signal_type"),
            signal_hash=data.get("signal_hash"),
            consumer_id=data.get("consumer_id"),
            consumer_capabilities=data.get("consumer_capabilities"),
            detail=data.get("detail", ""),
            reason=data.get("reason"),
            gate_name=data.get("gate_name"),
            correlation_id=data.get("correlation_id"),
            parent_signal_id=data.get("parent_signal_id"),
            causality_chain=data.get("causality_chain"),
            execution_time_ms=data.get("execution_time_ms"),
            queue_depth=data.get("queue_depth"),
            backpressure_ratio=data.get("backpressure_ratio"),
            metadata=data.get("metadata", {}),
            previous_hash=data.get("previous_hash", "GENESIS"),
        )


# =============================================================================
# BUS AUDIT TRAIL
# =============================================================================

class BusAuditTrail:
    """
    Immutable audit trail for bus operations with blockchain-style chaining.

    Provides comprehensive tracking of all bus events with:
    - Integrity verification via hash chaining
    - Correlation tracking for signal relationships
    - Query capabilities for analysis
    - Persistence to disk
    """

    def __init__(
        self,
        trail_id: str,
        bus_system: BusSystemType,
        bus_name: Optional[str] = None,
        max_memory_entries: int = 10000,
        persist_path: Optional[Path] = None
    ):
        self._trail_id = trail_id
        self._bus_system = bus_system
        self._bus_name = bus_name
        self._max_memory_entries = max_memory_entries
        self._persist_path = persist_path

        self._entries: List[BusAuditEntry] = []
        self._entry_count = 0
        self._genesis_hash = self._create_genesis_hash()
        self._last_hash = self._genesis_hash

        # Indexes for efficient queries
        self._by_signal: Dict[str, List[int]] = defaultdict(list)
        self._by_consumer: Dict[str, List[int]] = defaultdict(list)
        self._by_event_type: Dict[BusAuditEventType, List[int]] = defaultdict(list)
        self._by_correlation: Dict[str, List[int]] = defaultdict(list)

        # Load existing trail if persist_path exists
        if persist_path and persist_path.exists():
            self._load_from_disk()

    def _create_genesis_hash(self) -> str:
        """Create genesis hash for the trail."""
        genesis_data = {
            "trail_id": self._trail_id,
            "bus_system": self._bus_system.value,
            "bus_name": self._bus_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
        }
        json_str = json.dumps(genesis_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def append(self, entry: BusAuditEntry) -> None:
        """
        Append a new entry to the audit trail.

        Args:
            entry: BusAuditEntry to append
        """
        # Set previous hash
        entry.previous_hash = self._last_hash
        entry.entry_hash = entry._compute_hash()

        # Add to entries
        idx = len(self._entries)
        self._entries.append(entry)
        self._last_hash = entry.entry_hash
        self._entry_count += 1

        # Update indexes
        if entry.signal_id:
            self._by_signal[entry.signal_id].append(idx)
        if entry.consumer_id:
            self._by_consumer[entry.consumer_id].append(idx)
        self._by_event_type[entry.event_type].append(idx)
        if entry.correlation_id:
            self._by_correlation[entry.correlation_id].append(idx)

        # Persist if configured
        if self._persist_path:
            self._persist_entry(entry)

    def create_entry(
        self,
        event_type: BusAuditEventType,
        **kwargs
    ) -> BusAuditEntry:
        """
        Create and append a new audit entry.

        Args:
            event_type: Type of event
            **kwargs: Additional entry fields

        Returns:
            Created BusAuditEntry
        """
        entry = BusAuditEntry(
            entry_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            bus_system=self._bus_system,
            bus_name=self._bus_name,
            **kwargs
        )
        self.append(entry)
        return entry

    def verify_chain(self) -> bool:
        """
        Verify integrity of the entire audit trail.

        Returns:
            True if trail is valid and unmodified
        """
        prev_hash = self._genesis_hash
        for entry in self._entries:
            if not entry.verify_integrity():
                logger.error(f"Entry {entry.entry_id} failed integrity check")
                return False
            if entry.previous_hash != prev_hash:
                logger.error(
                    f"Chain broken at {entry.entry_id}: "
                    f"expected {prev_hash}, got {entry.previous_hash}"
                )
                return False
            prev_hash = entry.entry_hash
        return True

    def get_by_signal(self, signal_id: str) -> List[BusAuditEntry]:
        """Get all entries for a specific signal."""
        indices = self._by_signal.get(signal_id, [])
        return [self._entries[i] for i in indices]

    def get_by_consumer(self, consumer_id: str) -> List[BusAuditEntry]:
        """Get all entries for a specific consumer."""
        indices = self._by_consumer.get(consumer_id, [])
        return [self._entries[i] for i in indices]

    def get_by_event_type(self, event_type: BusAuditEventType) -> List[BusAuditEntry]:
        """Get all entries of a specific event type."""
        indices = self._by_event_type.get(event_type, [])
        return [self._entries[i] for i in indices]

    def get_by_correlation(self, correlation_id: str) -> List[BusAuditEntry]:
        """Get all entries with a specific correlation ID."""
        indices = self._by_correlation.get(correlation_id, [])
        return [self._entries[i] for i in indices]

    def get_signal_lifecycle(self, signal_id: str) -> Dict[str, Any]:
        """
        Get the complete lifecycle trace for a signal.

        Returns:
            Dict with lifecycle information including all events,
            consumers that received it, and final disposition
        """
        entries = self.get_by_signal(signal_id)
        if not entries:
            return {"signal_id": signal_id, "found": False}

        return {
            "signal_id": signal_id,
            "found": True,
            "first_seen": entries[0].timestamp,
            "last_seen": entries[-1].timestamp,
            "event_count": len(entries),
            "event_types": [e.event_type.value for e in entries],
            "consumers": list(set(e.consumer_id for e in entries if e.consumer_id)),
            "final_disposition": entries[-1].event_type.value,
            "entries": [e.to_dict() for e in entries],
        }

    def get_causality_chain(self, signal_id: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """
        Reconstruct the causality chain for a signal.

        Args:
            signal_id: Starting signal ID
            max_depth: Maximum chain depth to traverse

        Returns:
            List of signal lifecycle dicts forming the chain
        """
        chain = []
        visited = set()
        current_id = signal_id

        for _ in range(max_depth):
            if current_id in visited:
                break
            visited.add(current_id)

            lifecycle = self.get_signal_lifecycle(current_id)
            if not lifecycle["found"]:
                break

            chain.append(lifecycle)

            # Find parent signal
            entries = self.get_by_signal(current_id)
            parent_id = None
            for e in entries:
                if e.parent_signal_id:
                    parent_id = e.parent_signal_id
                    break

            if not parent_id:
                break

            current_id = parent_id

        return chain

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for the audit trail."""
        if not self._entries:
            return {
                "trail_id": self._trail_id,
                "bus_system": self._bus_system.value,
                "bus_name": self._bus_name,
                "total_entries": 0,
            }

        # Count by event type
        by_event = defaultdict(int)
        for entry in self._entries:
            by_event[entry.event_type.value] += 1

        # Count unique signals and consumers
        unique_signals = len(self._by_signal)
        unique_consumers = len(self._by_consumer)

        # Success/error rates
        published = by_event.get(BusAuditEventType.SIGNAL_PUBLISHED.value, 0)
        delivered = by_event.get(BusAuditEventType.SIGNAL_DELIVERED.value, 0)
        rejected = by_event.get(BusAuditEventType.SIGNAL_REJECTED.value, 0)
        dead_lettered = by_event.get(BusAuditEventType.SIGNAL_DEAD_LETTERED.value, 0)

        success_rate = delivered / published if published > 0 else 0
        rejection_rate = rejected / published if published > 0 else 0

        return {
            "trail_id": self._trail_id,
            "bus_system": self._bus_system.value,
            "bus_name": self._bus_name,
            "total_entries": len(self._entries),
            "unique_signals": unique_signals,
            "unique_consumers": unique_consumers,
            "chain_verified": self.verify_chain(),
            "by_event_type": dict(by_event),
            "success_rate": success_rate,
            "rejection_rate": rejection_rate,
            "dead_letter_count": dead_lettered,
        }

    def export_to_file(self, output_path: Path, format: str = "json") -> None:
        """Export audit trail to file."""
        if format == "json":
            data = {
                "trail_id": self._trail_id,
                "bus_system": self._bus_system.value,
                "bus_name": self._bus_name,
                "genesis_hash": self._genesis_hash,
                "entry_count": self._entry_count,
                "entries": [e.to_dict() for e in self._entries],
                "chain_verified": self.verify_chain(),
                "statistics": self.get_statistics(),
            }

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

        elif format == "jsonl":
            with open(output_path, "w") as f:
                for entry in self._entries:
                    f.write(json.dumps(entry.to_dict(), default=str) + "\n")

        logger.info(f"Exported {len(self._entries)} entries to {output_path}")

    def _persist_entry(self, entry: BusAuditEntry) -> None:
        """Persist single entry to disk."""
        if not self._persist_path:
            return

        with open(self._persist_path, "a") as f:
            f.write(json.dumps(entry.to_dict(), default=str) + "\n")

    def _load_from_disk(self) -> None:
        """Load entries from persisted file."""
        if not self._persist_path or not self._persist_path.exists():
            return

        try:
            with open(self._persist_path, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entry = BusAuditEntry.from_dict(data)
                        # Recompute hash and chain
                        entry.previous_hash = self._last_hash
                        entry.entry_hash = entry._compute_hash()

                        idx = len(self._entries)
                        self._entries.append(entry)
                        self._last_hash = entry.entry_hash
                        self._entry_count += 1

                        # Update indexes
                        if entry.signal_id:
                            self._by_signal[entry.signal_id].append(idx)
                        if entry.consumer_id:
                            self._by_consumer[entry.consumer_id].append(idx)
                        self._by_event_type[entry.event_type].append(idx)
                        if entry.correlation_id:
                            self._by_correlation[entry.correlation_id].append(idx)

            logger.info(f"Loaded {len(self._entries)} entries from {self._persist_path}")
        except Exception as e:
            logger.error(f"Failed to load audit trail from {self._persist_path}: {e}")


# =============================================================================
# BUS AUDIT MANAGER
# =============================================================================

class BusAuditManager:
    """
    Central manager for all bus audit trails.

    Manages audit trails for:
    - SDO (Signal Distribution Orchestrator)
    - All legacy buses (structural, integrity, epistemic, etc.)

    Provides unified interface for bus auditing across the entire SISAS system.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the bus audit manager.

        Args:
            base_path: Base directory for audit persistence
        """
        self._base_path = base_path
        self._trails: Dict[str, BusAuditTrail] = {}

        # Initialize SDO trail
        self._sdo_trail: Optional[BusAuditTrail] = None

        # Initialize legacy bus trails
        self._legacy_trails: Dict[LegacyBusType, BusAuditTrail] = {}

        logger.info("BusAuditManager initialized")

    def get_sdo_trail(self) -> BusAuditTrail:
        """Get or create the SDO audit trail."""
        if self._sdo_trail is None:
            persist_path = None
            if self._base_path:
                persist_path = self._base_path / "sdo_audit.jsonl"

            self._sdo_trail = BusAuditTrail(
                trail_id="sdo_main",
                bus_system=BusSystemType.SDO,
                bus_name="SignalDistributionOrchestrator",
                max_memory_entries=10000,
                persist_path=persist_path
            )
        return self._sdo_trail

    def get_legacy_trail(self, bus_type: LegacyBusType) -> BusAuditTrail:
        """Get or create a legacy bus audit trail."""
        if bus_type not in self._legacy_trails:
            persist_path = None
            if self._base_path:
                persist_path = self._base_path / f"{bus_type.value}_audit.jsonl"

            trail = BusAuditTrail(
                trail_id=f"legacy_{bus_type.value}",
                bus_system=BusSystemType.LEGACY,
                bus_name=bus_type.value,
                max_memory_entries=5000,
                persist_path=persist_path
            )
            self._legacy_trails[bus_type] = trail
        return self._legacy_trails[bus_type]

    def get_all_trails(self) -> List[BusAuditTrail]:
        """Get all audit trails."""
        trails = []
        if self._sdo_trail:
            trails.append(self._sdo_trail)
        trails.extend(self._legacy_trails.values())
        return trails

    def get_system_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive health report for all bus systems.

        Returns:
            Dict with health metrics for all buses
        """
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "buses": {},
            "summary": {
                "total_buses": 0,
                "healthy_buses": 0,
                "degraded_buses": 0,
                "total_signals_processed": 0,
                "total_errors": 0,
            }
        }

        all_trails = self.get_all_trails()

        for trail in all_trails:
            stats = trail.get_statistics()
            bus_key = f"{trail._bus_system.value}:{trail._bus_name}"

            # Determine health status
            health = self._assess_bus_health(stats)

            report["buses"][bus_key] = {
                "health": health["status"],
                "statistics": stats,
                "health_metrics": health,
            }

            # Update summary
            report["summary"]["total_buses"] += 1
            if health["status"] == "HEALTHY":
                report["summary"]["healthy_buses"] += 1
            else:
                report["summary"]["degraded_buses"] += 1

            report["summary"]["total_signals_processed"] += stats.get("total_entries", 0)

        return report

    def _assess_bus_health(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess health of a bus based on statistics.

        Returns:
            Dict with health status and metrics
        """
        health = {
            "status": "HEALTHY",
            "issues": [],
            "metrics": {}
        }

        by_event = stats.get("by_event_type", {})
        published = by_event.get(BusAuditEventType.SIGNAL_PUBLISHED.value, 0)
        delivered = by_event.get(BusAuditEventType.SIGNAL_DELIVERED.value, 0)
        rejected = by_event.get(BusAuditEventType.SIGNAL_REJECTED.value, 0)
        dead_lettered = by_event.get(BusAuditEventType.SIGNAL_DEAD_LETTERED.value, 0)
        errors = by_event.get(BusAuditEventType.CONSUMER_ERROR.value, 0)

        # Calculate rates
        delivery_rate = delivered / published if published > 0 else 1.0
        rejection_rate = rejected / published if published > 0 else 0.0
        error_rate = errors / delivered if delivered > 0 else 0.0

        health["metrics"] = {
            "delivery_rate": delivery_rate,
            "rejection_rate": rejection_rate,
            "error_rate": error_rate,
            "dead_letter_count": dead_lettered
        }

        # Assess health
        if delivery_rate < 0.8:
            health["status"] = "DEGRADED"
            health["issues"].append(f"Low delivery rate: {delivery_rate:.1%}")

        if rejection_rate > 0.1:
            health["status"] = "DEGRADED"
            health["issues"].append(f"High rejection rate: {rejection_rate:.1%}")

        if error_rate > 0.05:
            health["status"] = "DEGRADED"
            health["issues"].append(f"High error rate: {error_rate:.1%}")

        if dead_lettered > published * 0.05:
            health["status"] = "CRITICAL"
            health["issues"].append(f"High dead letter count: {dead_lettered}")

        # Check chain integrity
        if not stats.get("chain_verified", True):
            health["status"] = "CRITICAL"
            health["issues"].append("Audit chain integrity verification failed")

        return health

    def export_all_reports(self, output_dir: Path) -> None:
        """Export all audit trails and health report."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export individual trails
        for trail in self.get_all_trails():
            output_path = output_dir / f"{trail._trail_id}_audit.json"
            trail.export_to_file(output_path)

        # Export health report
        health_report = self.get_system_health_report()
        health_path = output_dir / "bus_health_report.json"
        with open(health_path, "w") as f:
            json.dump(health_report, f, indent=2, default=str)

        logger.info(f"Exported all bus audit reports to {output_dir}")


# =============================================================================
# SDO AUDIT BRIDGE
# =============================================================================

class SDOAuditBridge:
    """
    Bridge between SDO's internal audit and the BusAuditSystem.

    Integrates with SignalDistributionOrchestrator to provide
    comprehensive bus-level auditing while maintaining SDO's
    existing audit mechanisms.
    """

    def __init__(self, sdo: 'SignalDistributionOrchestrator', audit_manager: BusAuditManager):
        """
        Initialize the SDO audit bridge.

        Args:
            sdo: SignalDistributionOrchestrator instance
            audit_manager: BusAuditManager instance
        """
        self._sdo = sdo
        self._audit_manager = audit_manager
        self._trail = audit_manager.get_sdo_trail()

        # Store original SDO methods for wrapping
        self._original_audit = sdo._audit
        self._original_dispatch = sdo.dispatch

        # Wrap SDO's audit method
        sdo._audit = self._audit_wrapper

        logger.info("SDOAuditBridge initialized and connected to SDO")

    def _audit_wrapper(
        self,
        action: str,
        signal: 'Signal',
        consumer_id: str = None,
        detail: str = ""
    ) -> None:
        """
        Wrapper for SDO's internal _audit method.

        Extends SDO's audit with bus-level tracking.
        """
        # Call original SDO audit
        self._original_audit(action, signal, consumer_id, detail)

        # Map SDO action to bus event type
        event_type_map = {
            "DISPATCHED": BusAuditEventType.SIGNAL_PUBLISHED,
            "DELIVERED": BusAuditEventType.SIGNAL_DELIVERED,
            "REJECTED": BusAuditEventType.SIGNAL_REJECTED,
            "DEAD_LETTERED": BusAuditEventType.SIGNAL_DEAD_LETTERED,
            "DEDUPLICATED": BusAuditEventType.SIGNAL_DEDUPLICATED,
        }

        event_type = event_type_map.get(action, BusAuditEventType.SIGNAL_PUBLISHED)

        # Extract correlation info from signal
        correlation_id = getattr(signal, 'correlation_id', None)
        parent_id = None
        if signal.provenance:
            parent_id = signal.provenance.parent_signal_id

        # Create bus audit entry
        self._trail.create_entry(
            event_type=event_type,
            signal_id=signal.signal_id,
            signal_type=signal.signal_type.value if hasattr(signal.signal_type, 'value') else str(signal.signal_type),
            signal_hash=signal.content_hash(),
            consumer_id=consumer_id,
            detail=detail or action,
            correlation_id=correlation_id,
            parent_signal_id=parent_id,
            metadata={
                "sdo_action": action,
                "scope": signal.scope.to_dict() if signal.scope else None,
                "empirical_availability": getattr(signal, 'empirical_availability', None),
                "enrichment": getattr(signal, 'enrichment', False),
            }
        )

    def audit_gate_validation(
        self,
        signal: 'Signal',
        gate_name: str,
        passed: bool,
        errors: List[str] = None
    ) -> None:
        """
        Audit a gate validation event.

        Args:
            signal: Signal being validated
            gate_name: Name of the gate (e.g., "gate_1_scope_alignment")
            passed: Whether the signal passed the gate
            errors: List of errors if validation failed
        """
        self._trail.create_entry(
            event_type=BusAuditEventType.GATE_PASSED if passed else BusAuditEventType.GATE_FAILED,
            signal_id=signal.signal_id,
            signal_type=signal.signal_type.value if hasattr(signal.signal_type, 'value') else str(signal.signal_type),
            gate_name=gate_name,
            detail=f"Gate {gate_name}: {'PASSED' if passed else 'FAILED'}",
            reason="; ".join(errors) if errors else None,
            metadata={
                "gate_name": gate_name,
                "validation_errors": errors or [],
            }
        )

    def audit_consumer_registration(
        self,
        consumer_id: str,
        scopes: List['SignalScope'],
        capabilities: List[str],
        registered: bool = True
    ) -> None:
        """Audit consumer registration/unregistration."""
        self._trail.create_entry(
            event_type=BusAuditEventType.CONSUMER_REGISTERED if registered else BusAuditEventType.CONSUMER_UNREGISTERED,
            consumer_id=consumer_id,
            detail=f"Consumer {consumer_id}: {'registered' if registered else 'unregistered'}",
            consumer_capabilities=capabilities,
            metadata={
                "scopes": [s.to_dict() for s in scopes] if scopes else [],
                "capabilities": capabilities,
            }
        )

    def get_signal_flow_trace(self, signal_id: str) -> Dict[str, Any]:
        """
        Get complete trace of signal flow through SDO.

        Combines SDO audit log with bus audit trail.
        """
        # Get SDO audit entries
        sdo_entries = self._sdo.get_audit_log(signal_id)

        # Get bus audit entries
        bus_entries = self._trail.get_by_signal(signal_id)

        return {
            "signal_id": signal_id,
            "sdo_audit": [e.to_dict() for e in sdo_entries],
            "bus_audit": [e.to_dict() for e in bus_entries],
            "lifecycle": self._trail.get_signal_lifecycle(signal_id),
        }


# =============================================================================
# LEGACY BUS AUDIT BRIDGE
# =============================================================================

class LegacyBusAuditBridge:
    """
    Bridge for legacy bus system auditing.

    Integrates with the legacy SignalBus system to provide
    comprehensive bus-level auditing.
    """

    def __init__(self, audit_manager: BusAuditManager):
        """
        Initialize the legacy bus audit bridge.

        Args:
            audit_manager: BusAuditManager instance
        """
        self._audit_manager = audit_manager
        self._bridges: Dict[LegacyBusType, Any] = {}

        logger.info("LegacyBusAuditBridge initialized")

    def connect_bus(self, bus_type: LegacyBusType, bus_instance: Any) -> None:
        """
        Connect audit to a legacy bus instance.

        Args:
            bus_type: Type of the bus
            bus_instance: The SignalBus instance
        """
        trail = self._audit_manager.get_legacy_trail(bus_type)
        self._bridges[bus_type] = {"bus": bus_instance, "trail": trail}

        # Wrap the bus's publish method
        original_publish = bus_instance.publish

        def audited_publish(signal, publisher_vehicle, publication_contract):
            result = original_publish(signal, publisher_vehicle, publication_contract)

            # Audit the publish attempt
            trail.create_entry(
                event_type=BusAuditEventType.SIGNAL_PUBLISHED if result[0] else BusAuditEventType.SIGNAL_REJECTED,
                signal_id=getattr(signal, 'signal_id', str(uuid4())),
                signal_type=getattr(signal, 'signal_type', 'UNKNOWN'),
                detail=result[1],
                reason=None if result[0] else result[1],
                metadata={
                    "publisher_vehicle": publisher_vehicle,
                    "message_id": result[1] if result[0] else None,
                    "queue_depth": len(getattr(bus_instance, '_queue', {}).queue) if hasattr(bus_instance, '_queue') else None,
                }
            )

            return result

        bus_instance.publish = audited_publish

        logger.info(f"Connected audit bridge to legacy bus: {bus_type.value}")

    def get_bus_statistics(self, bus_type: LegacyBusType) -> Dict[str, Any]:
        """Get statistics for a specific legacy bus."""
        if bus_type not in self._bridges:
            return {"error": f"Bus {bus_type.value} not connected"}

        bridge = self._bridges[bus_type]
        trail = bridge["trail"]
        bus = bridge["bus"]

        return {
            "bus_type": bus_type.value,
            "bus_statistics": bus.get_stats() if hasattr(bus, 'get_stats') else {},
            "audit_statistics": trail.get_statistics(),
        }


# =============================================================================
# GLOBAL AUDIT MANAGER
# =============================================================================

_global_bus_audit_manager: Optional[BusAuditManager] = None


def get_bus_audit_manager(base_path: Optional[Path] = None) -> BusAuditManager:
    """Get or create the global bus audit manager."""
    global _global_bus_audit_manager
    if _global_bus_audit_manager is None:
        audit_path = base_path or Path("_registry/bus_audit")
        audit_path.mkdir(parents=True, exist_ok=True)
        _global_bus_audit_manager = BusAuditManager(audit_path)
    return _global_bus_audit_manager
