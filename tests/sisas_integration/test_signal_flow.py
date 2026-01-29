"""
SISAS Signal Flow Tests - JOBFRONT A Product.

This module tests end-to-end signal flow through the SISAS system,
including emission, routing, consumption, and cross-phase propagation.
All tests are SELF-CONTAINED using mocks from conftest.py.

Created: 2026-01-19T22:58:54.465Z
Jobfront: A - Test Infrastructure
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import List

import pytest

from tests.sisas_integration.conftest import (
    MockConsumer,
    MockIrrigator,
    MockOrchestratorContext,
    MockSignal,
    MockSignalBatch,
    MockSignalBus,
    MockSignalPriority,
    MockSignalType,
    assert_signal_consumed,
    assert_signal_not_consumed,
    create_test_signal_chain,
)


# =============================================================================
# SIGNAL EMISSION TESTS
# =============================================================================


class TestSignalEmission:
    """Test signal emission to the bus."""

    def test_emit_single_signal(self, mock_signal_bus: MockSignalBus):
        """Single signal should be emittable."""
        signal = MockSignal(
            signal_type=MockSignalType.OPERATIONAL_STATUS,
            payload={"status": "OK"},
        )
        signal_id = mock_signal_bus.emit(signal)
        assert signal_id == signal.signal_id
        assert mock_signal_bus.stats["emit_count"] == 1

    def test_emit_multiple_signals(self, mock_signal_bus: MockSignalBus):
        """Multiple signals should be emittable."""
        for i in range(10):
            signal = MockSignal(payload={"index": i})
            mock_signal_bus.emit(signal)
        assert mock_signal_bus.stats["emit_count"] == 10
        assert mock_signal_bus.stats["total_signals"] == 10

    def test_emit_preserves_signal_data(self, mock_signal_bus: MockSignalBus):
        """Emitted signal data should be preserved."""
        payload = {"key": "value", "nested": {"data": [1, 2, 3]}}
        signal = MockSignal(
            signal_type=MockSignalType.STRUCTURAL_COMPLETENESS,
            payload=payload,
            source_phase="P02",
            target_phases=["P03", "P04"],
        )
        mock_signal_bus.emit(signal)

        retrieved = mock_signal_bus.get_signals_by_type(
            MockSignalType.STRUCTURAL_COMPLETENESS
        )[0]
        assert retrieved.payload == payload
        assert retrieved.source_phase == "P02"
        assert retrieved.target_phases == ["P03", "P04"]

    def test_emit_triggers_subscribers(self, mock_signal_bus: MockSignalBus):
        """Emitting should trigger registered subscribers."""
        received_signals = []

        def callback(signal: MockSignal):
            received_signals.append(signal)

        mock_signal_bus.subscribe(MockSignalType.OPERATIONAL_STATUS, callback)
        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
        mock_signal_bus.emit(signal)

        assert len(received_signals) == 1
        assert received_signals[0].signal_id == signal.signal_id

    def test_emit_does_not_trigger_unrelated_subscribers(
        self, mock_signal_bus: MockSignalBus
    ):
        """Emitting should not trigger unrelated subscribers."""
        received_signals = []

        def callback(signal: MockSignal):
            received_signals.append(signal)

        mock_signal_bus.subscribe(MockSignalType.STRUCTURAL_COMPLETENESS, callback)
        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
        mock_signal_bus.emit(signal)

        assert len(received_signals) == 0


# =============================================================================
# SIGNAL CONSUMPTION TESTS
# =============================================================================


class TestSignalConsumption:
    """Test signal consumption from the bus."""

    def test_consume_signal(self, mock_signal_bus: MockSignalBus):
        """Signal should be consumable."""
        signal = MockSignal()
        mock_signal_bus.emit(signal)

        consumed = mock_signal_bus.consume(signal.signal_id, "consumer_1")
        assert consumed is not None
        assert "consumer_1" in consumed.consumed_by
        assert mock_signal_bus.stats["consume_count"] == 1

    def test_consume_nonexistent_signal(self, mock_signal_bus: MockSignalBus):
        """Consuming nonexistent signal should return None."""
        result = mock_signal_bus.consume("nonexistent_id", "consumer_1")
        assert result is None

    def test_multiple_consumers_same_signal(self, mock_signal_bus: MockSignalBus):
        """Multiple consumers should be able to consume the same signal."""
        signal = MockSignal()
        mock_signal_bus.emit(signal)

        mock_signal_bus.consume(signal.signal_id, "consumer_1")
        mock_signal_bus.consume(signal.signal_id, "consumer_2")
        mock_signal_bus.consume(signal.signal_id, "consumer_3")

        consumed = mock_signal_bus._signals[signal.signal_id]
        assert len(consumed.consumed_by) == 3
        assert "consumer_1" in consumed.consumed_by
        assert "consumer_2" in consumed.consumed_by
        assert "consumer_3" in consumed.consumed_by

    def test_consume_tracks_history(self, mock_signal_bus: MockSignalBus):
        """Consumption should be tracked in history."""
        signal = MockSignal()
        mock_signal_bus.emit(signal)
        mock_signal_bus.consume(signal.signal_id, "consumer_1")

        history = mock_signal_bus._history
        consume_entries = [h for h in history if h["action"] == "consume"]
        assert len(consume_entries) == 1
        assert consume_entries[0]["signal_id"] == signal.signal_id
        assert consume_entries[0]["consumer_id"] == "consumer_1"


# =============================================================================
# SIGNAL ROUTING TESTS
# =============================================================================


class TestSignalRouting:
    """Test signal routing by type and phase."""

    def test_get_signals_by_type(self, mock_signal_bus: MockSignalBus):
        """Should retrieve signals by type."""
        # Emit mixed signal types
        mock_signal_bus.emit(MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS))
        mock_signal_bus.emit(MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS))
        mock_signal_bus.emit(MockSignal(signal_type=MockSignalType.EPISTEMIC_CONFIDENCE))

        structural = mock_signal_bus.get_signals_by_type(
            MockSignalType.STRUCTURAL_COMPLETENESS
        )
        epistemic = mock_signal_bus.get_signals_by_type(MockSignalType.EPISTEMIC_CONFIDENCE)

        assert len(structural) == 2
        assert len(epistemic) == 1

    def test_get_signals_for_phase(self, mock_signal_bus: MockSignalBus):
        """Should retrieve signals targeted at a phase."""
        mock_signal_bus.emit(MockSignal(target_phases=["P03"]))
        mock_signal_bus.emit(MockSignal(target_phases=["P03", "P04"]))
        mock_signal_bus.emit(MockSignal(target_phases=["P05"]))
        mock_signal_bus.emit(MockSignal(target_phases=[]))  # Broadcast

        phase_3_signals = mock_signal_bus.get_signals_for_phase("P03")
        phase_5_signals = mock_signal_bus.get_signals_for_phase("P05")

        # P03 gets: targeted to P03 (2) + broadcast (1)
        assert len(phase_3_signals) == 3
        # P05 gets: targeted to P05 (1) + broadcast (1)
        assert len(phase_5_signals) == 2

    def test_broadcast_signal_reaches_all_phases(self, mock_signal_bus: MockSignalBus):
        """Broadcast signal (empty target_phases) should be available to all phases."""
        broadcast = MockSignal(target_phases=[])
        mock_signal_bus.emit(broadcast)

        for i in range(10):
            phase_signals = mock_signal_bus.get_signals_for_phase(f"P0{i}")
            assert len(phase_signals) == 1


# =============================================================================
# SIGNAL IRRIGATION TESTS
# =============================================================================


class TestSignalIrrigation:
    """Test signal irrigation to consumers."""

    def test_irrigator_distributes_to_matching_consumers(
        self, mock_irrigator: MockIrrigator
    ):
        """Irrigator should distribute signal to matching consumers."""
        consumer = MockConsumer(
            consumer_id="test_consumer",
            consumed_types={MockSignalType.STRUCTURAL_COMPLETENESS},
        )
        mock_irrigator.register_consumer(consumer)

        signal = MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS)
        results = mock_irrigator.irrigate(signal)

        assert "test_consumer" in results
        assert consumer.consumed_count == 1

    def test_irrigator_skips_non_matching_consumers(self, mock_irrigator: MockIrrigator):
        """Irrigator should skip consumers that don't match signal type."""
        consumer = MockConsumer(
            consumer_id="structural_consumer",
            consumed_types={MockSignalType.STRUCTURAL_COMPLETENESS},
        )
        mock_irrigator.register_consumer(consumer)

        signal = MockSignal(signal_type=MockSignalType.EPISTEMIC_CONFIDENCE)
        results = mock_irrigator.irrigate(signal)

        assert "structural_consumer" not in results
        assert consumer.consumed_count == 0

    def test_irrigator_distributes_to_multiple_consumers(
        self, mock_irrigator: MockIrrigator
    ):
        """Irrigator should distribute to all matching consumers."""
        consumer1 = MockConsumer(
            consumer_id="consumer_1",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )
        consumer2 = MockConsumer(
            consumer_id="consumer_2",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )
        consumer3 = MockConsumer(
            consumer_id="consumer_3",
            consumed_types={MockSignalType.STRUCTURAL_COMPLETENESS},
        )

        mock_irrigator.register_consumer(consumer1)
        mock_irrigator.register_consumer(consumer2)
        mock_irrigator.register_consumer(consumer3)

        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
        results = mock_irrigator.irrigate(signal)

        assert len(results) == 2
        assert "consumer_1" in results
        assert "consumer_2" in results
        assert "consumer_3" not in results

    def test_irrigate_batch(self, mock_irrigator: MockIrrigator):
        """Irrigator should handle batch irrigation."""
        consumer = MockConsumer(
            consumer_id="batch_consumer",
            consumed_types={
                MockSignalType.STRUCTURAL_COMPLETENESS,
                MockSignalType.EPISTEMIC_CONFIDENCE,
            },
        )
        mock_irrigator.register_consumer(consumer)

        batch = MockSignalBatch()
        batch.add(MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS))
        batch.add(MockSignal(signal_type=MockSignalType.EPISTEMIC_CONFIDENCE))
        batch.add(MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS))

        results = mock_irrigator.irrigate_batch(batch)

        assert len(results) == 3
        assert consumer.consumed_count == 2  # Only 2 match

    def test_irrigation_stats(self, mock_irrigator: MockIrrigator):
        """Irrigator should track statistics."""
        consumer = MockConsumer(
            consumer_id="stats_consumer",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )
        mock_irrigator.register_consumer(consumer)

        for _ in range(5):
            signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
            mock_irrigator.irrigate(signal)

        stats = mock_irrigator.irrigation_stats
        assert stats["total_irrigations"] == 5
        assert stats["registered_consumers"] == 1


# =============================================================================
# CROSS-PHASE SIGNAL FLOW TESTS
# =============================================================================


class TestCrossPhaseSignalFlow:
    """Test signal flow across phases."""

    def test_signal_chain_propagation(
        self, mock_signal_bus: MockSignalBus, mock_signal_factory
    ):
        """Signals should propagate through a chain of phases."""
        # Create a chain: P01 -> P02 -> P03 -> P04
        signals = []
        phases = ["P01", "P02", "P03", "P04"]

        for i, phase in enumerate(phases):
            next_phases = [phases[i + 1]] if i < len(phases) - 1 else []
            signal = mock_signal_factory(
                signal_type=MockSignalType.OPERATIONAL_STATUS,
                payload={"step": i, "phase": phase},
                source_phase=phase,
                target_phases=next_phases,
            )
            mock_signal_bus.emit(signal)
            signals.append(signal)

        # Verify chain
        for i, phase in enumerate(phases[1:], 1):
            phase_signals = mock_signal_bus.get_signals_for_phase(phase)
            # Each phase should see the signal targeted at it
            assert any(
                s.payload.get("step") == i - 1 for s in phase_signals
            ), f"Phase {phase} missing expected signal"

    def test_orchestrator_context_signal_flow(
        self, mock_orchestrator_context: MockOrchestratorContext
    ):
        """Orchestrator context should manage signal flow correctly."""
        ctx = mock_orchestrator_context

        # Start and complete a phase
        ctx.start_phase("P00")
        assert ctx.get_phase("P00").status == "RUNNING"
        assert len(ctx.get_phase("P00").signals_emitted) == 1  # Phase start signal

        ctx.complete_phase("P00", success=True)
        assert ctx.get_phase("P00").status == "COMPLETED"
        assert len(ctx.get_phase("P00").signals_emitted) == 2  # + Phase complete signal

    def test_phase_transition_signals(
        self, mock_orchestrator_context: MockOrchestratorContext
    ):
        """Phase transitions should emit appropriate signals."""
        ctx = mock_orchestrator_context

        # Execute phases P00 -> P01 -> P02
        for phase in ["P00", "P01", "P02"]:
            ctx.start_phase(phase)
            ctx.complete_phase(phase, success=True)

        # Check signal bus for orchestration signals
        start_signals = ctx.signal_bus.get_signals_by_type(
            MockSignalType.ORCHESTRATION_PHASE_START
        )
        complete_signals = ctx.signal_bus.get_signals_by_type(
            MockSignalType.ORCHESTRATION_PHASE_COMPLETE
        )

        assert len(start_signals) == 3
        assert len(complete_signals) == 3


# =============================================================================
# SIGNAL PRIORITY FLOW TESTS
# =============================================================================


class TestSignalPriorityFlow:
    """Test signal flow respecting priority."""

    def test_critical_signals_processed(self, mock_signal_bus: MockSignalBus):
        """Critical signals should be emitted and available."""
        critical = MockSignal(
            signal_type=MockSignalType.INTEGRITY_HASH,
            priority=MockSignalPriority.CRITICAL,
            payload={"error": "hash_mismatch"},
        )
        mock_signal_bus.emit(critical)

        signals = mock_signal_bus.get_signals_by_type(MockSignalType.INTEGRITY_HASH)
        assert len(signals) == 1
        assert signals[0].priority == MockSignalPriority.CRITICAL

    def test_mixed_priority_signals(self, mock_signal_bus: MockSignalBus):
        """Mixed priority signals should all be stored."""
        priorities = [
            MockSignalPriority.CRITICAL,
            MockSignalPriority.HIGH,
            MockSignalPriority.MEDIUM,
            MockSignalPriority.LOW,
            MockSignalPriority.DEBUG,
        ]

        for priority in priorities:
            signal = MockSignal(
                signal_type=MockSignalType.OPERATIONAL_STATUS,
                priority=priority,
            )
            mock_signal_bus.emit(signal)

        all_signals = mock_signal_bus.get_signals_by_type(
            MockSignalType.OPERATIONAL_STATUS
        )
        assert len(all_signals) == 5


# =============================================================================
# SIGNAL FLOW ERROR HANDLING TESTS
# =============================================================================


class TestSignalFlowErrorHandling:
    """Test error handling in signal flow."""

    def test_subscriber_error_does_not_block_emit(self, mock_signal_bus: MockSignalBus):
        """Subscriber error should not block signal emission."""
        error_count = [0]

        def failing_callback(signal: MockSignal):
            error_count[0] += 1
            raise ValueError("Subscriber error")

        mock_signal_bus.subscribe(MockSignalType.OPERATIONAL_STATUS, failing_callback)
        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)

        # Should not raise
        signal_id = mock_signal_bus.emit(signal)

        assert signal_id is not None
        assert error_count[0] == 1  # Callback was called
        assert mock_signal_bus.stats["emit_count"] == 1

    def test_consumer_error_does_not_block_irrigation(
        self, mock_irrigator: MockIrrigator
    ):
        """Consumer error should not block other consumers."""

        def failing_consume(signal: MockSignal) -> dict:
            raise ValueError("Consumer error")

        consumer1 = MockConsumer(
            consumer_id="failing_consumer",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )
        consumer1._consume_callback = failing_consume

        consumer2 = MockConsumer(
            consumer_id="working_consumer",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )

        mock_irrigator.register_consumer(consumer1)
        mock_irrigator.register_consumer(consumer2)

        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
        results = mock_irrigator.irrigate(signal)

        # Consumer2 should still have processed
        assert consumer2.consumed_count == 1


# =============================================================================
# SIGNAL FLOW PERFORMANCE TESTS
# =============================================================================


class TestSignalFlowPerformance:
    """Test signal flow performance characteristics."""

    def test_high_volume_emission(self, mock_signal_bus: MockSignalBus):
        """Bus should handle high volume of signals."""
        num_signals = 1000
        start = time.time()

        for i in range(num_signals):
            signal = MockSignal(payload={"index": i})
            mock_signal_bus.emit(signal)

        elapsed = time.time() - start

        assert mock_signal_bus.stats["emit_count"] == num_signals
        assert elapsed < 5.0, f"Emission took too long: {elapsed}s"

    def test_high_volume_consumption(self, mock_signal_bus: MockSignalBus):
        """Bus should handle high volume of consumption."""
        num_signals = 1000
        signal_ids = []

        for i in range(num_signals):
            signal = MockSignal()
            mock_signal_bus.emit(signal)
            signal_ids.append(signal.signal_id)

        start = time.time()
        for signal_id in signal_ids:
            mock_signal_bus.consume(signal_id, "test_consumer")
        elapsed = time.time() - start

        assert mock_signal_bus.stats["consume_count"] == num_signals
        assert elapsed < 5.0, f"Consumption took too long: {elapsed}s"

    def test_bus_clear_performance(self, mock_signal_bus: MockSignalBus):
        """Bus clear should be efficient."""
        for i in range(1000):
            mock_signal_bus.emit(MockSignal())

        start = time.time()
        mock_signal_bus.clear()
        elapsed = time.time() - start

        assert mock_signal_bus.stats["total_signals"] == 0
        assert elapsed < 0.5, f"Clear took too long: {elapsed}s"
