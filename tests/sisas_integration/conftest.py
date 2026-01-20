"""
SISAS Integration Test Fixtures - JOBFRONT A Product.

This module provides all shared fixtures and mocks for SISAS integration testing.
All fixtures are SELF-CONTAINED and do not depend on external SISAS implementation.

Created: 2026-01-19T22:58:54.465Z
Jobfront: A - Test Infrastructure
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Set
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# MOCK SIGNAL TYPES (Self-contained, no external imports)
# =============================================================================


class MockSignalType(str, Enum):
    """Mock signal types for testing."""

    # Structural signals
    STRUCTURAL_COMPLETENESS = "structural.completeness"
    STRUCTURAL_HIERARCHY = "structural.hierarchy"
    STRUCTURAL_COVERAGE = "structural.coverage"

    # Epistemic signals
    EPISTEMIC_CONFIDENCE = "epistemic.confidence"
    EPISTEMIC_UNCERTAINTY = "epistemic.uncertainty"
    EPISTEMIC_PROVENANCE = "epistemic.provenance"

    # Operational signals
    OPERATIONAL_TIMING = "operational.timing"
    OPERATIONAL_RESOURCE = "operational.resource"
    OPERATIONAL_STATUS = "operational.status"

    # Contrast signals
    CONTRAST_DIVERGENCE = "contrast.divergence"
    CONTRAST_ALIGNMENT = "contrast.alignment"

    # Consumption signals
    CONSUMPTION_INGESTION = "consumption.ingestion"
    CONSUMPTION_VALIDATION = "consumption.validation"

    # Integrity signals
    INTEGRITY_HASH = "integrity.hash"
    INTEGRITY_SCHEMA = "integrity.schema"

    # Orchestration signals
    ORCHESTRATION_PHASE_START = "orchestration.phase_start"
    ORCHESTRATION_PHASE_COMPLETE = "orchestration.phase_complete"
    ORCHESTRATION_DECISION = "orchestration.decision"


class MockSignalPriority(str, Enum):
    """Signal priority levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    DEBUG = "DEBUG"


# =============================================================================
# MOCK SIGNAL DATACLASSES
# =============================================================================


@dataclass
class MockSignal:
    """Mock signal for testing."""

    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: MockSignalType = MockSignalType.OPERATIONAL_STATUS
    payload: Dict[str, Any] = field(default_factory=dict)
    source_phase: str = "P00"
    target_phases: List[str] = field(default_factory=list)
    priority: MockSignalPriority = MockSignalPriority.MEDIUM
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    ttl_seconds: int = 3600
    consumed_by: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize signal to dictionary."""
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type.value,
            "payload": self.payload,
            "source_phase": self.source_phase,
            "target_phases": self.target_phases,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "ttl_seconds": self.ttl_seconds,
            "consumed_by": list(self.consumed_by),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockSignal":
        """Deserialize signal from dictionary."""
        return cls(
            signal_id=data.get("signal_id", str(uuid.uuid4())),
            signal_type=MockSignalType(data.get("signal_type", "operational.status")),
            payload=data.get("payload", {}),
            source_phase=data.get("source_phase", "P00"),
            target_phases=data.get("target_phases", []),
            priority=MockSignalPriority(data.get("priority", "MEDIUM")),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(timezone.utc),
            metadata=data.get("metadata", {}),
            ttl_seconds=data.get("ttl_seconds", 3600),
            consumed_by=set(data.get("consumed_by", [])),
        )


@dataclass
class MockSignalBatch:
    """Batch of signals for testing."""

    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signals: List[MockSignal] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add(self, signal: MockSignal) -> None:
        """Add signal to batch."""
        self.signals.append(signal)

    def __len__(self) -> int:
        return len(self.signals)

    def __iter__(self):
        return iter(self.signals)


# =============================================================================
# MOCK SIGNAL BUS
# =============================================================================


class MockSignalBus:
    """Mock signal bus for testing signal routing."""

    def __init__(self):
        self._signals: Dict[str, MockSignal] = {}
        self._subscribers: Dict[MockSignalType, List[Callable]] = {}
        self._history: List[Dict[str, Any]] = []
        self._emit_count: int = 0
        self._consume_count: int = 0

    def emit(self, signal: MockSignal) -> str:
        """Emit a signal to the bus."""
        self._signals[signal.signal_id] = signal
        self._emit_count += 1
        self._history.append(
            {
                "action": "emit",
                "signal_id": signal.signal_id,
                "signal_type": signal.signal_type.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Notify subscribers
        if signal.signal_type in self._subscribers:
            for callback in self._subscribers[signal.signal_type]:
                try:
                    callback(signal)
                except Exception:
                    pass  # Swallow errors in tests

        return signal.signal_id

    def consume(
        self, signal_id: str, consumer_id: str
    ) -> Optional[MockSignal]:
        """Consume a signal from the bus."""
        signal = self._signals.get(signal_id)
        if signal:
            signal.consumed_by.add(consumer_id)
            self._consume_count += 1
            self._history.append(
                {
                    "action": "consume",
                    "signal_id": signal_id,
                    "consumer_id": consumer_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        return signal

    def subscribe(
        self, signal_type: MockSignalType, callback: Callable[[MockSignal], None]
    ) -> None:
        """Subscribe to a signal type."""
        if signal_type not in self._subscribers:
            self._subscribers[signal_type] = []
        self._subscribers[signal_type].append(callback)

    def get_signals_by_type(self, signal_type: MockSignalType) -> List[MockSignal]:
        """Get all signals of a given type."""
        return [s for s in self._signals.values() if s.signal_type == signal_type]

    def get_signals_for_phase(self, phase_id: str) -> List[MockSignal]:
        """Get all signals targeted at a phase."""
        return [
            s
            for s in self._signals.values()
            if phase_id in s.target_phases or not s.target_phases
        ]

    def clear(self) -> None:
        """Clear all signals."""
        self._signals.clear()
        self._history.clear()
        self._emit_count = 0
        self._consume_count = 0

    @property
    def stats(self) -> Dict[str, int]:
        """Get bus statistics."""
        return {
            "total_signals": len(self._signals),
            "emit_count": self._emit_count,
            "consume_count": self._consume_count,
            "subscriber_count": sum(len(s) for s in self._subscribers.values()),
        }


# =============================================================================
# MOCK SIGNAL REGISTRY
# =============================================================================


class MockSignalRegistry:
    """Mock signal registry for testing."""

    def __init__(self):
        self._registered_types: Set[MockSignalType] = set()
        self._type_schemas: Dict[MockSignalType, Dict[str, Any]] = {}
        self._validators: Dict[MockSignalType, Callable] = {}

    def register_type(
        self,
        signal_type: MockSignalType,
        schema: Optional[Dict[str, Any]] = None,
        validator: Optional[Callable] = None,
    ) -> None:
        """Register a signal type."""
        self._registered_types.add(signal_type)
        if schema:
            self._type_schemas[signal_type] = schema
        if validator:
            self._validators[signal_type] = validator

    def is_registered(self, signal_type: MockSignalType) -> bool:
        """Check if a signal type is registered."""
        return signal_type in self._registered_types

    def validate_signal(self, signal: MockSignal) -> bool:
        """Validate a signal against its schema."""
        if signal.signal_type not in self._registered_types:
            return False
        if signal.signal_type in self._validators:
            return self._validators[signal.signal_type](signal)
        return True

    def get_all_types(self) -> Set[MockSignalType]:
        """Get all registered signal types."""
        return self._registered_types.copy()


# =============================================================================
# MOCK CONSUMER PROTOCOL
# =============================================================================


class MockConsumerProtocol(Protocol):
    """Protocol for signal consumers."""

    consumer_id: str
    consumed_types: Set[MockSignalType]

    def consume(self, signal: MockSignal) -> Dict[str, Any]:
        """Consume a signal and return result."""
        ...

    def can_consume(self, signal: MockSignal) -> bool:
        """Check if consumer can handle signal."""
        ...


@dataclass
class MockConsumer:
    """Mock consumer implementation for testing."""

    consumer_id: str
    consumed_types: Set[MockSignalType] = field(default_factory=set)
    _consumed_signals: List[MockSignal] = field(default_factory=list)
    _consume_callback: Optional[Callable[[MockSignal], Dict[str, Any]]] = None

    def consume(self, signal: MockSignal) -> Dict[str, Any]:
        """Consume a signal."""
        self._consumed_signals.append(signal)
        if self._consume_callback:
            return self._consume_callback(signal)
        return {"status": "consumed", "signal_id": signal.signal_id}

    def can_consume(self, signal: MockSignal) -> bool:
        """Check if can consume signal type."""
        return signal.signal_type in self.consumed_types

    @property
    def consumed_count(self) -> int:
        """Get count of consumed signals."""
        return len(self._consumed_signals)

    @property
    def consumed_signals(self) -> List[MockSignal]:
        """Get list of consumed signals."""
        return self._consumed_signals.copy()


# =============================================================================
# MOCK IRRIGATOR
# =============================================================================


class MockIrrigator:
    """Mock irrigator for testing signal distribution."""

    def __init__(self, bus: MockSignalBus):
        self._bus = bus
        self._consumers: Dict[str, MockConsumer] = {}
        self._irrigation_log: List[Dict[str, Any]] = []

    def register_consumer(self, consumer: MockConsumer) -> None:
        """Register a consumer."""
        self._consumers[consumer.consumer_id] = consumer

    def irrigate(self, signal: MockSignal) -> Dict[str, Any]:
        """Irrigate signal to appropriate consumers."""
        results = {}
        for consumer_id, consumer in self._consumers.items():
            if consumer.can_consume(signal):
                try:
                    result = consumer.consume(signal)
                    results[consumer_id] = result
                    self._irrigation_log.append(
                        {
                            "signal_id": signal.signal_id,
                            "consumer_id": consumer_id,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "result": result,
                        }
                    )
                except Exception as e:
                    # Log error but continue with other consumers
                    results[consumer_id] = {"error": str(e), "status": "failed"}
                    self._irrigation_log.append(
                        {
                            "signal_id": signal.signal_id,
                            "consumer_id": consumer_id,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "error": str(e),
                        }
                    )
        return results

    def irrigate_batch(self, batch: MockSignalBatch) -> Dict[str, List[Dict[str, Any]]]:
        """Irrigate a batch of signals."""
        results = {}
        for signal in batch:
            results[signal.signal_id] = self.irrigate(signal)
        return results

    @property
    def irrigation_stats(self) -> Dict[str, int]:
        """Get irrigation statistics."""
        return {
            "total_irrigations": len(self._irrigation_log),
            "registered_consumers": len(self._consumers),
        }


# =============================================================================
# MOCK ORCHESTRATOR CONTEXT
# =============================================================================


@dataclass
class MockPhaseContext:
    """Mock phase execution context."""

    phase_id: str
    phase_name: str
    status: str = "PENDING"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    signals_emitted: List[str] = field(default_factory=list)
    signals_consumed: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MockOrchestratorContext:
    """Mock orchestrator context for testing SISAS integration."""

    def __init__(self):
        self._phases: Dict[str, MockPhaseContext] = {}
        self._current_phase: Optional[str] = None
        self._signal_bus = MockSignalBus()
        self._execution_log: List[Dict[str, Any]] = []

        # Initialize phases P00-P09
        for i in range(10):
            phase_id = f"P0{i}"
            self._phases[phase_id] = MockPhaseContext(
                phase_id=phase_id,
                phase_name=f"Phase {i}",
            )

    def start_phase(self, phase_id: str) -> None:
        """Start a phase."""
        if phase_id in self._phases:
            self._phases[phase_id].status = "RUNNING"
            self._phases[phase_id].started_at = datetime.now(timezone.utc)
            self._current_phase = phase_id

            # Emit phase start signal
            signal = MockSignal(
                signal_type=MockSignalType.ORCHESTRATION_PHASE_START,
                payload={"phase_id": phase_id},
                source_phase=phase_id,
            )
            self._signal_bus.emit(signal)
            self._phases[phase_id].signals_emitted.append(signal.signal_id)

    def complete_phase(self, phase_id: str, success: bool = True) -> None:
        """Complete a phase."""
        if phase_id in self._phases:
            self._phases[phase_id].status = "COMPLETED" if success else "FAILED"
            self._phases[phase_id].completed_at = datetime.now(timezone.utc)

            # Emit phase complete signal
            signal = MockSignal(
                signal_type=MockSignalType.ORCHESTRATION_PHASE_COMPLETE,
                payload={"phase_id": phase_id, "success": success},
                source_phase=phase_id,
            )
            self._signal_bus.emit(signal)
            self._phases[phase_id].signals_emitted.append(signal.signal_id)

    def emit_signal(self, signal: MockSignal) -> str:
        """Emit a signal from current phase."""
        if self._current_phase:
            signal.source_phase = self._current_phase
            self._phases[self._current_phase].signals_emitted.append(signal.signal_id)
        return self._signal_bus.emit(signal)

    def get_phase(self, phase_id: str) -> Optional[MockPhaseContext]:
        """Get phase context."""
        return self._phases.get(phase_id)

    @property
    def signal_bus(self) -> MockSignalBus:
        """Get signal bus."""
        return self._signal_bus


# =============================================================================
# PYTEST FIXTURES
# =============================================================================


@pytest.fixture
def mock_signal_bus() -> MockSignalBus:
    """Provide a fresh mock signal bus."""
    return MockSignalBus()


@pytest.fixture
def mock_signal_registry() -> MockSignalRegistry:
    """Provide a mock signal registry with all types registered."""
    registry = MockSignalRegistry()
    for signal_type in MockSignalType:
        registry.register_type(signal_type)
    return registry


@pytest.fixture
def mock_signal_factory() -> Callable[..., MockSignal]:
    """Provide a factory function for creating mock signals."""

    def factory(
        signal_type: MockSignalType = MockSignalType.OPERATIONAL_STATUS,
        payload: Optional[Dict[str, Any]] = None,
        source_phase: str = "P00",
        target_phases: Optional[List[str]] = None,
        priority: MockSignalPriority = MockSignalPriority.MEDIUM,
    ) -> MockSignal:
        return MockSignal(
            signal_type=signal_type,
            payload=payload or {},
            source_phase=source_phase,
            target_phases=target_phases or [],
            priority=priority,
        )

    return factory


@pytest.fixture
def mock_consumer_factory() -> Callable[..., MockConsumer]:
    """Provide a factory function for creating mock consumers."""

    def factory(
        consumer_id: str,
        consumed_types: Optional[Set[MockSignalType]] = None,
    ) -> MockConsumer:
        return MockConsumer(
            consumer_id=consumer_id,
            consumed_types=consumed_types or {MockSignalType.OPERATIONAL_STATUS},
        )

    return factory


@pytest.fixture
def mock_irrigator(mock_signal_bus: MockSignalBus) -> MockIrrigator:
    """Provide a mock irrigator."""
    return MockIrrigator(mock_signal_bus)


@pytest.fixture
def mock_orchestrator_context() -> MockOrchestratorContext:
    """Provide a mock orchestrator context."""
    return MockOrchestratorContext()


@pytest.fixture
def sample_signal_batch(mock_signal_factory) -> MockSignalBatch:
    """Provide a sample batch of signals."""
    batch = MockSignalBatch()
    batch.add(mock_signal_factory(MockSignalType.STRUCTURAL_COMPLETENESS, {"score": 0.95}))
    batch.add(mock_signal_factory(MockSignalType.EPISTEMIC_CONFIDENCE, {"confidence": 0.87}))
    batch.add(mock_signal_factory(MockSignalType.OPERATIONAL_STATUS, {"status": "OK"}))
    return batch


@pytest.fixture
def phase_consumer_map() -> Dict[str, Set[MockSignalType]]:
    """Provide mapping of phases to consumed signal types."""
    return {
        "P00": {MockSignalType.ORCHESTRATION_PHASE_START},
        "P01": {MockSignalType.CONSUMPTION_INGESTION, MockSignalType.STRUCTURAL_COMPLETENESS},
        "P02": {
            MockSignalType.EPISTEMIC_CONFIDENCE,
            MockSignalType.EPISTEMIC_PROVENANCE,
            MockSignalType.STRUCTURAL_HIERARCHY,
        },
        "P03": {MockSignalType.EPISTEMIC_CONFIDENCE, MockSignalType.CONTRAST_DIVERGENCE},
        "P04": {MockSignalType.STRUCTURAL_COVERAGE, MockSignalType.EPISTEMIC_UNCERTAINTY},
        "P05": {MockSignalType.STRUCTURAL_COVERAGE},
        "P06": {MockSignalType.STRUCTURAL_COVERAGE},
        "P07": {MockSignalType.CONTRAST_ALIGNMENT},
        "P08": {MockSignalType.ORCHESTRATION_DECISION},
        "P09": {MockSignalType.ORCHESTRATION_PHASE_COMPLETE, MockSignalType.INTEGRITY_HASH},
    }


# =============================================================================
# TEST UTILITIES
# =============================================================================


def create_test_signal_chain(
    signal_factory: Callable[..., MockSignal],
    chain_length: int = 5,
) -> List[MockSignal]:
    """Create a chain of signals for testing flow."""
    signals = []
    signal_types = list(MockSignalType)
    for i in range(chain_length):
        signal = signal_factory(
            signal_type=signal_types[i % len(signal_types)],
            payload={"step": i, "chain_id": str(uuid.uuid4())[:8]},
            source_phase=f"P0{i % 10}",
        )
        signals.append(signal)
    return signals


def assert_signal_consumed(
    signal: MockSignal,
    consumer_id: str,
    msg: str = "",
) -> None:
    """Assert that a signal was consumed by a specific consumer."""
    assert consumer_id in signal.consumed_by, (
        f"Signal {signal.signal_id} was not consumed by {consumer_id}. "
        f"Consumed by: {signal.consumed_by}. {msg}"
    )


def assert_signal_not_consumed(
    signal: MockSignal,
    consumer_id: str,
    msg: str = "",
) -> None:
    """Assert that a signal was NOT consumed by a specific consumer."""
    assert consumer_id not in signal.consumed_by, (
        f"Signal {signal.signal_id} was unexpectedly consumed by {consumer_id}. {msg}"
    )
