"""
SISAS Orchestrator Integration Tests - JOBFRONT A Product.

This module tests the integration between the orchestrator and SISAS,
ensuring proper signal flow during phase execution and lifecycle management.
All tests are SELF-CONTAINED using mocks from conftest.py.

Created: 2026-01-19T22:58:54.465Z
Jobfront: A - Test Infrastructure
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set
from unittest.mock import MagicMock, patch

import pytest

from tests.sisas_integration.conftest import (
    MockConsumer,
    MockIrrigator,
    MockOrchestratorContext,
    MockPhaseContext,
    MockSignal,
    MockSignalBatch,
    MockSignalBus,
    MockSignalPriority,
    MockSignalRegistry,
    MockSignalType,
)


# =============================================================================
# ORCHESTRATOR-SISAS INTEGRATION TYPES
# =============================================================================


class MockPhaseStatus(str, Enum):
    """Phase execution status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class MockPhaseResult:
    """Result of a phase execution."""

    phase_id: str
    status: MockPhaseStatus
    signals_emitted: List[str] = field(default_factory=list)
    signals_consumed: List[str] = field(default_factory=list)
    execution_time_ms: int = 0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MockPipelineContext:
    """Context for pipeline execution with SISAS integration."""

    pipeline_id: str
    phases: Dict[str, MockPhaseResult] = field(default_factory=dict)
    signal_bus: MockSignalBus = field(default_factory=MockSignalBus)
    irrigator: Optional[MockIrrigator] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_phase: Optional[str] = None

    def __post_init__(self):
        if self.irrigator is None:
            self.irrigator = MockIrrigator(self.signal_bus)
        # Initialize all phases
        for i in range(10):
            phase_id = f"P0{i}"
            self.phases[phase_id] = MockPhaseResult(
                phase_id=phase_id,
                status=MockPhaseStatus.PENDING,
            )


# =============================================================================
# SISAS-AWARE ORCHESTRATOR MOCK
# =============================================================================


class SISASAwareOrchestrator:
    """Mock orchestrator with full SISAS integration for testing."""

    def __init__(self, context: MockPipelineContext):
        self._context = context
        self._phase_callbacks: Dict[str, List[Callable]] = {}
        self._signal_handlers: Dict[MockSignalType, Callable] = {}
        self._execution_log: List[Dict[str, Any]] = []

    def register_phase_callback(
        self,
        phase_id: str,
        event: str,
        callback: Callable[[MockPhaseResult], None],
    ) -> None:
        """Register callback for phase events."""
        key = f"{phase_id}:{event}"
        if key not in self._phase_callbacks:
            self._phase_callbacks[key] = []
        self._phase_callbacks[key].append(callback)

    def register_signal_handler(
        self,
        signal_type: MockSignalType,
        handler: Callable[[MockSignal], Dict[str, Any]],
    ) -> None:
        """Register handler for signal type."""
        self._signal_handlers[signal_type] = handler

    def start_pipeline(self) -> None:
        """Start the pipeline execution."""
        self._context.started_at = datetime.now(timezone.utc)

        # Emit pipeline start signal
        start_signal = MockSignal(
            signal_type=MockSignalType.ORCHESTRATION_PHASE_START,
            payload={"pipeline_id": self._context.pipeline_id, "event": "pipeline_start"},
            source_phase="P00",
            target_phases=["P00"],
            priority=MockSignalPriority.CRITICAL,
        )
        self._emit_signal(start_signal)

    def execute_phase(self, phase_id: str) -> MockPhaseResult:
        """Execute a single phase with SISAS integration."""
        if phase_id not in self._context.phases:
            raise ValueError(f"Unknown phase: {phase_id}")

        result = self._context.phases[phase_id]
        result.status = MockPhaseStatus.RUNNING
        self._context.current_phase = phase_id
        start_time = time.time()

        # Emit phase start signal
        start_signal = MockSignal(
            signal_type=MockSignalType.ORCHESTRATION_PHASE_START,
            payload={"phase_id": phase_id},
            source_phase=phase_id,
            priority=MockSignalPriority.HIGH,
        )
        signal_id = self._emit_signal(start_signal)
        result.signals_emitted.append(signal_id)

        # Invoke start callbacks
        self._invoke_callbacks(phase_id, "start", result)

        # Consume any signals targeted at this phase
        signals_for_phase = self._context.signal_bus.get_signals_for_phase(phase_id)
        for signal in signals_for_phase:
            if signal.signal_id not in result.signals_consumed:
                self._consume_signal(signal, phase_id)
                result.signals_consumed.append(signal.signal_id)

        # Mark phase complete
        result.status = MockPhaseStatus.COMPLETED
        result.execution_time_ms = int((time.time() - start_time) * 1000)

        # Emit phase complete signal
        complete_signal = MockSignal(
            signal_type=MockSignalType.ORCHESTRATION_PHASE_COMPLETE,
            payload={"phase_id": phase_id, "success": True},
            source_phase=phase_id,
            priority=MockSignalPriority.HIGH,
        )
        signal_id = self._emit_signal(complete_signal)
        result.signals_emitted.append(signal_id)

        # Invoke complete callbacks
        self._invoke_callbacks(phase_id, "complete", result)

        return result

    def execute_pipeline(
        self,
        phases: Optional[List[str]] = None,
    ) -> Dict[str, MockPhaseResult]:
        """Execute full pipeline or specified phases."""
        if phases is None:
            phases = [f"P0{i}" for i in range(10)]

        self.start_pipeline()

        for phase_id in phases:
            try:
                self.execute_phase(phase_id)
            except Exception as e:
                result = self._context.phases[phase_id]
                result.status = MockPhaseStatus.FAILED
                result.error = str(e)

        self._context.completed_at = datetime.now(timezone.utc)
        return self._context.phases

    def _emit_signal(self, signal: MockSignal) -> str:
        """Emit signal to the bus."""
        signal_id = self._context.signal_bus.emit(signal)
        self._execution_log.append({
            "action": "emit",
            "signal_id": signal_id,
            "signal_type": signal.signal_type.value,
            "phase": signal.source_phase,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return signal_id

    def _consume_signal(self, signal: MockSignal, consumer_id: str) -> None:
        """Consume signal from the bus."""
        self._context.signal_bus.consume(signal.signal_id, consumer_id)

        # Handle signal if handler registered
        if signal.signal_type in self._signal_handlers:
            handler = self._signal_handlers[signal.signal_type]
            handler(signal)

        self._execution_log.append({
            "action": "consume",
            "signal_id": signal.signal_id,
            "consumer": consumer_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def _invoke_callbacks(
        self,
        phase_id: str,
        event: str,
        result: MockPhaseResult,
    ) -> None:
        """Invoke registered callbacks for phase event."""
        key = f"{phase_id}:{event}"
        for callback in self._phase_callbacks.get(key, []):
            try:
                callback(result)
            except Exception:
                pass  # Don't let callback errors stop execution

    @property
    def execution_log(self) -> List[Dict[str, Any]]:
        """Get execution log."""
        return self._execution_log.copy()


# =============================================================================
# ORCHESTRATOR INTEGRATION TESTS
# =============================================================================


class TestOrchestratorSignalEmission:
    """Test orchestrator signal emission during execution."""

    @pytest.fixture
    def pipeline_context(self) -> MockPipelineContext:
        """Provide a fresh pipeline context."""
        return MockPipelineContext(pipeline_id="test_pipeline")

    @pytest.fixture
    def orchestrator(
        self, pipeline_context: MockPipelineContext
    ) -> SISASAwareOrchestrator:
        """Provide a SISAS-aware orchestrator."""
        return SISASAwareOrchestrator(pipeline_context)

    def test_pipeline_start_emits_signal(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Pipeline start should emit orchestration signal."""
        orchestrator.start_pipeline()

        signals = orchestrator._context.signal_bus.get_signals_by_type(
            MockSignalType.ORCHESTRATION_PHASE_START
        )
        assert len(signals) >= 1

        # First signal should be pipeline start
        start_signal = signals[0]
        assert start_signal.payload.get("event") == "pipeline_start"

    def test_phase_execution_emits_start_signal(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Phase execution should emit start signal."""
        orchestrator.execute_phase("P01")

        signals = orchestrator._context.signal_bus.get_signals_by_type(
            MockSignalType.ORCHESTRATION_PHASE_START
        )

        # Should have at least one signal from P01
        p01_signals = [s for s in signals if s.source_phase == "P01"]
        assert len(p01_signals) >= 1

    def test_phase_execution_emits_complete_signal(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Phase execution should emit complete signal."""
        orchestrator.execute_phase("P01")

        signals = orchestrator._context.signal_bus.get_signals_by_type(
            MockSignalType.ORCHESTRATION_PHASE_COMPLETE
        )

        # Should have complete signal from P01
        p01_signals = [s for s in signals if s.source_phase == "P01"]
        assert len(p01_signals) >= 1
        assert p01_signals[0].payload.get("success") is True

    def test_full_pipeline_emits_signals_for_all_phases(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Full pipeline should emit signals for all phases."""
        phases = ["P00", "P01", "P02"]
        orchestrator.execute_pipeline(phases)

        start_signals = orchestrator._context.signal_bus.get_signals_by_type(
            MockSignalType.ORCHESTRATION_PHASE_START
        )
        complete_signals = orchestrator._context.signal_bus.get_signals_by_type(
            MockSignalType.ORCHESTRATION_PHASE_COMPLETE
        )

        # Should have start and complete for each phase (plus pipeline start)
        assert len(start_signals) >= len(phases)
        assert len(complete_signals) >= len(phases)


# =============================================================================
# ORCHESTRATOR SIGNAL CONSUMPTION TESTS
# =============================================================================


class TestOrchestratorSignalConsumption:
    """Test orchestrator signal consumption during execution."""

    @pytest.fixture
    def pipeline_context(self) -> MockPipelineContext:
        """Provide a fresh pipeline context."""
        return MockPipelineContext(pipeline_id="test_pipeline")

    @pytest.fixture
    def orchestrator(
        self, pipeline_context: MockPipelineContext
    ) -> SISASAwareOrchestrator:
        """Provide a SISAS-aware orchestrator."""
        return SISASAwareOrchestrator(pipeline_context)

    def test_phase_consumes_targeted_signals(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Phase should consume signals targeted at it."""
        # Pre-emit a signal targeting P02
        signal = MockSignal(
            signal_type=MockSignalType.STRUCTURAL_HIERARCHY,
            payload={"hierarchy": "test"},
            source_phase="P01",
            target_phases=["P02"],
        )
        orchestrator._context.signal_bus.emit(signal)

        # Execute P02
        result = orchestrator.execute_phase("P02")

        # P02 should have consumed the signal
        assert signal.signal_id in result.signals_consumed

    def test_phase_consumes_broadcast_signals(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Phase should consume broadcast signals (empty target_phases)."""
        # Pre-emit a broadcast signal
        signal = MockSignal(
            signal_type=MockSignalType.OPERATIONAL_STATUS,
            payload={"status": "broadcast"},
            source_phase="P00",
            target_phases=[],  # Broadcast
        )
        orchestrator._context.signal_bus.emit(signal)

        # Execute P03
        result = orchestrator.execute_phase("P03")

        # P03 should have consumed the broadcast
        assert signal.signal_id in result.signals_consumed

    def test_signal_handler_invoked_on_consumption(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Registered signal handler should be invoked on consumption."""
        handled_signals = []

        def handler(signal: MockSignal) -> Dict[str, Any]:
            handled_signals.append(signal.signal_id)
            return {"handled": True}

        orchestrator.register_signal_handler(
            MockSignalType.EPISTEMIC_CONFIDENCE,
            handler,
        )

        # Pre-emit epistemic signal
        signal = MockSignal(
            signal_type=MockSignalType.EPISTEMIC_CONFIDENCE,
            payload={"confidence": 0.95},
            source_phase="P01",
            target_phases=["P02"],
        )
        orchestrator._context.signal_bus.emit(signal)

        # Execute P02
        orchestrator.execute_phase("P02")

        assert signal.signal_id in handled_signals


# =============================================================================
# ORCHESTRATOR LIFECYCLE TESTS
# =============================================================================


class TestOrchestratorLifecycle:
    """Test orchestrator lifecycle with SISAS integration."""

    @pytest.fixture
    def pipeline_context(self) -> MockPipelineContext:
        """Provide a fresh pipeline context."""
        return MockPipelineContext(pipeline_id="lifecycle_test")

    @pytest.fixture
    def orchestrator(
        self, pipeline_context: MockPipelineContext
    ) -> SISASAwareOrchestrator:
        """Provide a SISAS-aware orchestrator."""
        return SISASAwareOrchestrator(pipeline_context)

    def test_phase_callbacks_invoked(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Phase callbacks should be invoked at correct times."""
        events_received = []

        def on_start(result: MockPhaseResult):
            events_received.append(("start", result.phase_id, result.status.value))

        def on_complete(result: MockPhaseResult):
            events_received.append(("complete", result.phase_id, result.status.value))

        orchestrator.register_phase_callback("P01", "start", on_start)
        orchestrator.register_phase_callback("P01", "complete", on_complete)

        orchestrator.execute_phase("P01")

        assert ("start", "P01", "RUNNING") in events_received
        assert ("complete", "P01", "COMPLETED") in events_received

    def test_execution_log_tracks_signals(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Execution log should track all signal operations."""
        orchestrator.execute_pipeline(["P00", "P01"])

        log = orchestrator.execution_log
        assert len(log) > 0

        emit_entries = [e for e in log if e["action"] == "emit"]
        consume_entries = [e for e in log if e["action"] == "consume"]

        assert len(emit_entries) > 0  # Should have emitted signals
        assert all("signal_id" in e for e in emit_entries)

    def test_pipeline_completion_timestamp(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Pipeline should record completion timestamp."""
        orchestrator.execute_pipeline(["P00"])

        assert orchestrator._context.started_at is not None
        assert orchestrator._context.completed_at is not None
        assert orchestrator._context.completed_at > orchestrator._context.started_at


# =============================================================================
# ORCHESTRATOR-SISAS ALIGNMENT TESTS
# =============================================================================


class TestOrchestratorSISASAlignment:
    """Test alignment between orchestrator and SISAS subsystem."""

    @pytest.fixture
    def pipeline_context(self) -> MockPipelineContext:
        """Provide a fresh pipeline context."""
        return MockPipelineContext(pipeline_id="alignment_test")

    @pytest.fixture
    def orchestrator(
        self, pipeline_context: MockPipelineContext
    ) -> SISASAwareOrchestrator:
        """Provide a SISAS-aware orchestrator."""
        return SISASAwareOrchestrator(pipeline_context)

    def test_all_phases_emit_orchestration_signals(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Every phase should emit orchestration signals."""
        phases = [f"P0{i}" for i in range(5)]
        orchestrator.execute_pipeline(phases)

        for phase_id in phases:
            result = orchestrator._context.phases[phase_id]
            assert len(result.signals_emitted) >= 2, (
                f"Phase {phase_id} should emit at least start and complete signals"
            )

    def test_signal_bus_consistent_with_phase_results(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Signal bus state should match phase results."""
        orchestrator.execute_pipeline(["P00", "P01", "P02"])

        # Count signals in bus
        all_signals = orchestrator._context.signal_bus._signals

        # Count signals in phase results
        total_emitted = sum(
            len(r.signals_emitted)
            for r in orchestrator._context.phases.values()
        )

        # Bus should have at least as many signals as phases emitted
        # (could have more from pipeline start)
        assert len(all_signals) >= total_emitted

    def test_phase_order_reflected_in_signals(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Signal timestamps should reflect phase execution order."""
        phases = ["P00", "P01", "P02", "P03"]
        orchestrator.execute_pipeline(phases)

        # Get start signals for each phase
        start_signals = orchestrator._context.signal_bus.get_signals_by_type(
            MockSignalType.ORCHESTRATION_PHASE_START
        )

        # Filter to phase-specific starts (exclude pipeline start)
        phase_starts = [
            s for s in start_signals
            if s.payload.get("phase_id") in phases
        ]

        # Verify timestamps are in order
        if len(phase_starts) > 1:
            timestamps = [s.timestamp for s in phase_starts]
            assert timestamps == sorted(timestamps), (
                "Phase start signals should be in execution order"
            )


# =============================================================================
# ORCHESTRATOR ERROR HANDLING TESTS
# =============================================================================


class TestOrchestratorErrorHandling:
    """Test orchestrator error handling with SISAS."""

    @pytest.fixture
    def pipeline_context(self) -> MockPipelineContext:
        """Provide a fresh pipeline context."""
        return MockPipelineContext(pipeline_id="error_test")

    @pytest.fixture
    def orchestrator(
        self, pipeline_context: MockPipelineContext
    ) -> SISASAwareOrchestrator:
        """Provide a SISAS-aware orchestrator."""
        return SISASAwareOrchestrator(pipeline_context)

    def test_callback_error_does_not_stop_execution(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Callback errors should not stop phase execution."""

        def failing_callback(result: MockPhaseResult):
            raise RuntimeError("Callback failure")

        orchestrator.register_phase_callback("P01", "start", failing_callback)

        # Should not raise
        result = orchestrator.execute_phase("P01")

        # Phase should still complete
        assert result.status == MockPhaseStatus.COMPLETED

    def test_signal_handler_error_isolated(
        self, orchestrator: SISASAwareOrchestrator
    ):
        """Signal handler errors should not propagate."""

        def failing_handler(signal: MockSignal) -> Dict[str, Any]:
            raise RuntimeError("Handler failure")

        orchestrator.register_signal_handler(
            MockSignalType.OPERATIONAL_STATUS,
            failing_handler,
        )

        # Pre-emit signal
        signal = MockSignal(
            signal_type=MockSignalType.OPERATIONAL_STATUS,
            target_phases=["P01"],
        )
        orchestrator._context.signal_bus.emit(signal)

        # Should not raise during execution
        result = orchestrator.execute_phase("P01")
        assert result.status == MockPhaseStatus.COMPLETED


# =============================================================================
# ORCHESTRATOR PERFORMANCE TESTS
# =============================================================================


class TestOrchestratorPerformance:
    """Test orchestrator performance with SISAS."""

    def test_full_pipeline_execution_time(self):
        """Full pipeline should execute in reasonable time."""
        context = MockPipelineContext(pipeline_id="perf_test")
        orchestrator = SISASAwareOrchestrator(context)

        start = time.time()
        orchestrator.execute_pipeline()
        elapsed = time.time() - start

        # Full 10-phase pipeline should complete quickly with mocks
        assert elapsed < 2.0, f"Pipeline took too long: {elapsed}s"

    def test_high_signal_volume(self):
        """Orchestrator should handle high signal volume."""
        context = MockPipelineContext(pipeline_id="volume_test")
        orchestrator = SISASAwareOrchestrator(context)

        # Pre-emit many signals
        for i in range(100):
            signal = MockSignal(
                signal_type=MockSignalType.OPERATIONAL_STATUS,
                payload={"index": i},
                target_phases=["P01"],
            )
            context.signal_bus.emit(signal)

        # Execute phase that will consume all signals
        start = time.time()
        result = orchestrator.execute_phase("P01")
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Phase with 100 signals took too long: {elapsed}s"
        assert len(result.signals_consumed) == 100
