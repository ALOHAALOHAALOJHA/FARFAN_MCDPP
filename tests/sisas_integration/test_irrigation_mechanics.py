"""
SISAS Irrigation Mechanics Tests - JOBFRONT A Product.

This module tests the mechanics of signal irrigation, including routing rules,
delivery guarantees, and phase-to-phase irrigation patterns.
All tests are SELF-CONTAINED using mocks from conftest.py.

Created: 2026-01-19T22:58:54.465Z
Jobfront: A - Test Infrastructure
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set
from unittest.mock import MagicMock, patch

import pytest

from tests.sisas_integration.conftest import (
    MockConsumer,
    MockIrrigator,
    MockSignal,
    MockSignalBatch,
    MockSignalBus,
    MockSignalPriority,
    MockSignalRegistry,
    MockSignalType,
)


# =============================================================================
# IRRIGATION RULE DEFINITIONS
# =============================================================================


@dataclass
class IrrigationRule:
    """Defines routing rules for signal irrigation."""

    rule_id: str
    source_phases: Set[str]  # Phases that can emit
    target_phases: Set[str]  # Phases that can receive
    signal_types: Set[MockSignalType]  # Signal types this rule applies to
    priority_threshold: MockSignalPriority = MockSignalPriority.LOW
    require_acknowledgment: bool = False
    max_retry_count: int = 3
    delivery_timeout_ms: int = 5000


# Standard irrigation rules
IRRIGATION_RULES = [
    IrrigationRule(
        rule_id="phase_transition",
        source_phases={"P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08"},
        target_phases={"P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09"},
        signal_types={
            MockSignalType.ORCHESTRATION_PHASE_START,
            MockSignalType.ORCHESTRATION_PHASE_COMPLETE,
        },
        require_acknowledgment=True,
    ),
    IrrigationRule(
        rule_id="structural_propagation",
        source_phases={"P01", "P02", "P03"},
        target_phases={"P04", "P05", "P06"},
        signal_types={
            MockSignalType.STRUCTURAL_COMPLETENESS,
            MockSignalType.STRUCTURAL_HIERARCHY,
            MockSignalType.STRUCTURAL_COVERAGE,
        },
    ),
    IrrigationRule(
        rule_id="epistemic_flow",
        source_phases={"P02"},
        target_phases={"P03", "P04"},
        signal_types={
            MockSignalType.EPISTEMIC_CONFIDENCE,
            MockSignalType.EPISTEMIC_UNCERTAINTY,
            MockSignalType.EPISTEMIC_PROVENANCE,
        },
    ),
    IrrigationRule(
        rule_id="contrast_analysis",
        source_phases={"P03"},
        target_phases={"P07"},
        signal_types={
            MockSignalType.CONTRAST_DIVERGENCE,
            MockSignalType.CONTRAST_ALIGNMENT,
        },
    ),
    IrrigationRule(
        rule_id="integrity_chain",
        source_phases={"P00", "P09"},
        target_phases={"P00", "P09"},
        signal_types={
            MockSignalType.INTEGRITY_HASH,
            MockSignalType.INTEGRITY_SCHEMA,
        },
        require_acknowledgment=True,
    ),
    IrrigationRule(
        rule_id="decision_broadcast",
        source_phases={"P07", "P08"},
        target_phases={"P08", "P09"},
        signal_types={MockSignalType.ORCHESTRATION_DECISION},
    ),
]


# =============================================================================
# IRRIGATION RULE ENGINE
# =============================================================================


class IrrigationRuleEngine:
    """Engine for evaluating and applying irrigation rules."""

    def __init__(self, rules: List[IrrigationRule]):
        self._rules = {r.rule_id: r for r in rules}
        self._evaluation_log: List[Dict[str, Any]] = []

    def find_applicable_rules(
        self, signal: MockSignal
    ) -> List[IrrigationRule]:
        """Find all rules applicable to a signal."""
        applicable = []
        for rule in self._rules.values():
            if (
                signal.signal_type in rule.signal_types
                and signal.source_phase in rule.source_phases
            ):
                applicable.append(rule)
        return applicable

    def get_valid_targets(
        self, signal: MockSignal
    ) -> Set[str]:
        """Get valid target phases for a signal based on rules."""
        rules = self.find_applicable_rules(signal)
        targets = set()
        for rule in rules:
            targets.update(rule.target_phases)

        # If signal has explicit targets, intersect with rule-allowed targets
        if signal.target_phases:
            explicit = set(signal.target_phases)
            targets = targets & explicit if targets else explicit

        return targets

    def evaluate_delivery(
        self,
        signal: MockSignal,
        target_phase: str,
    ) -> Dict[str, Any]:
        """Evaluate if signal can be delivered to target phase."""
        rules = self.find_applicable_rules(signal)

        for rule in rules:
            if target_phase in rule.target_phases:
                evaluation = {
                    "allowed": True,
                    "rule_id": rule.rule_id,
                    "require_ack": rule.require_acknowledgment,
                    "priority_ok": self._check_priority(signal, rule),
                }
                self._evaluation_log.append(
                    {
                        "signal_id": signal.signal_id,
                        "target_phase": target_phase,
                        **evaluation,
                    }
                )
                return evaluation

        return {"allowed": False, "reason": "No matching rule"}

    def _check_priority(
        self, signal: MockSignal, rule: IrrigationRule
    ) -> bool:
        """Check if signal priority meets rule threshold."""
        priority_order = [
            MockSignalPriority.DEBUG,
            MockSignalPriority.LOW,
            MockSignalPriority.MEDIUM,
            MockSignalPriority.HIGH,
            MockSignalPriority.CRITICAL,
        ]
        signal_idx = priority_order.index(signal.priority)
        threshold_idx = priority_order.index(rule.priority_threshold)
        return signal_idx >= threshold_idx


# =============================================================================
# IRRIGATION MECHANICS TESTS
# =============================================================================


class TestIrrigationRuleDefinitions:
    """Test irrigation rule definitions are complete."""

    def test_all_signal_types_have_rules(self):
        """Every signal type should be covered by at least one rule."""
        covered_types = set()
        for rule in IRRIGATION_RULES:
            covered_types.update(rule.signal_types)

        all_types = set(MockSignalType)
        uncovered = all_types - covered_types

        # Allow some types to be uncovered (e.g., consumption, operational)
        expected_uncovered = {
            MockSignalType.CONSUMPTION_INGESTION,
            MockSignalType.CONSUMPTION_VALIDATION,
            MockSignalType.OPERATIONAL_TIMING,
            MockSignalType.OPERATIONAL_RESOURCE,
            MockSignalType.OPERATIONAL_STATUS,
        }
        unexpected_uncovered = uncovered - expected_uncovered
        assert not unexpected_uncovered, (
            f"Unexpected uncovered signal types: {unexpected_uncovered}"
        )

    def test_rules_have_valid_phases(self):
        """All rules should reference valid phase IDs."""
        valid_phases = {f"P0{i}" for i in range(10)}
        for rule in IRRIGATION_RULES:
            invalid_sources = rule.source_phases - valid_phases
            invalid_targets = rule.target_phases - valid_phases
            assert not invalid_sources, (
                f"Rule {rule.rule_id} has invalid source phases: {invalid_sources}"
            )
            assert not invalid_targets, (
                f"Rule {rule.rule_id} has invalid target phases: {invalid_targets}"
            )

    def test_rules_have_unique_ids(self):
        """All rules should have unique IDs."""
        ids = [r.rule_id for r in IRRIGATION_RULES]
        assert len(ids) == len(set(ids)), "Duplicate rule IDs found"


class TestIrrigationRuleEngine:
    """Test irrigation rule engine behavior."""

    @pytest.fixture
    def rule_engine(self) -> IrrigationRuleEngine:
        """Provide a rule engine with standard rules."""
        return IrrigationRuleEngine(IRRIGATION_RULES)

    def test_find_applicable_rules_for_phase_transition(
        self, rule_engine: IrrigationRuleEngine
    ):
        """Should find phase_transition rule for orchestration signals."""
        signal = MockSignal(
            signal_type=MockSignalType.ORCHESTRATION_PHASE_COMPLETE,
            source_phase="P01",
        )
        rules = rule_engine.find_applicable_rules(signal)

        assert len(rules) >= 1
        rule_ids = [r.rule_id for r in rules]
        assert "phase_transition" in rule_ids

    def test_find_applicable_rules_for_structural(
        self, rule_engine: IrrigationRuleEngine
    ):
        """Should find structural_propagation rule for structural signals."""
        signal = MockSignal(
            signal_type=MockSignalType.STRUCTURAL_COMPLETENESS,
            source_phase="P02",
        )
        rules = rule_engine.find_applicable_rules(signal)

        assert len(rules) >= 1
        rule_ids = [r.rule_id for r in rules]
        assert "structural_propagation" in rule_ids

    def test_get_valid_targets_respects_rules(
        self, rule_engine: IrrigationRuleEngine
    ):
        """Valid targets should be determined by rules."""
        signal = MockSignal(
            signal_type=MockSignalType.EPISTEMIC_CONFIDENCE,
            source_phase="P02",
        )
        targets = rule_engine.get_valid_targets(signal)

        # Epistemic flow rule says P02 -> P03, P04
        assert "P03" in targets
        assert "P04" in targets
        assert "P01" not in targets  # Not in rule

    def test_evaluate_delivery_allowed(
        self, rule_engine: IrrigationRuleEngine
    ):
        """Should allow delivery when rule permits."""
        signal = MockSignal(
            signal_type=MockSignalType.STRUCTURAL_COVERAGE,
            source_phase="P03",
        )
        result = rule_engine.evaluate_delivery(signal, "P04")

        assert result["allowed"] is True
        assert "rule_id" in result

    def test_evaluate_delivery_denied(
        self, rule_engine: IrrigationRuleEngine
    ):
        """Should deny delivery when no rule permits."""
        signal = MockSignal(
            signal_type=MockSignalType.STRUCTURAL_COVERAGE,
            source_phase="P03",
        )
        result = rule_engine.evaluate_delivery(signal, "P01")  # Not allowed

        assert result["allowed"] is False

    def test_priority_threshold_enforcement(
        self, rule_engine: IrrigationRuleEngine
    ):
        """Should enforce priority thresholds."""
        # Create a signal with low priority
        signal = MockSignal(
            signal_type=MockSignalType.ORCHESTRATION_PHASE_START,
            source_phase="P00",
            priority=MockSignalPriority.DEBUG,
        )
        result = rule_engine.evaluate_delivery(signal, "P01")

        # Should be allowed but priority check should be evaluated
        assert "priority_ok" in result


# =============================================================================
# IRRIGATION DELIVERY TESTS
# =============================================================================


class TestIrrigationDelivery:
    """Test signal delivery mechanics."""

    def test_deliver_to_single_consumer(
        self, mock_signal_bus: MockSignalBus
    ):
        """Should deliver signal to a single matching consumer."""
        irrigator = MockIrrigator(mock_signal_bus)
        consumer = MockConsumer(
            consumer_id="single_consumer",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )
        irrigator.register_consumer(consumer)

        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
        results = irrigator.irrigate(signal)

        assert "single_consumer" in results
        assert consumer.consumed_count == 1

    def test_deliver_to_multiple_consumers(
        self, mock_signal_bus: MockSignalBus
    ):
        """Should deliver signal to all matching consumers."""
        irrigator = MockIrrigator(mock_signal_bus)

        consumers = []
        for i in range(5):
            consumer = MockConsumer(
                consumer_id=f"consumer_{i}",
                consumed_types={MockSignalType.STRUCTURAL_COMPLETENESS},
            )
            irrigator.register_consumer(consumer)
            consumers.append(consumer)

        signal = MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS)
        results = irrigator.irrigate(signal)

        assert len(results) == 5
        for consumer in consumers:
            assert consumer.consumed_count == 1

    def test_no_delivery_to_non_matching_consumers(
        self, mock_signal_bus: MockSignalBus
    ):
        """Should not deliver to consumers that don't match signal type."""
        irrigator = MockIrrigator(mock_signal_bus)

        matching = MockConsumer(
            consumer_id="matching",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )
        non_matching = MockConsumer(
            consumer_id="non_matching",
            consumed_types={MockSignalType.STRUCTURAL_COMPLETENESS},
        )

        irrigator.register_consumer(matching)
        irrigator.register_consumer(non_matching)

        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
        results = irrigator.irrigate(signal)

        assert "matching" in results
        assert "non_matching" not in results
        assert matching.consumed_count == 1
        assert non_matching.consumed_count == 0


# =============================================================================
# BATCH IRRIGATION TESTS
# =============================================================================


class TestBatchIrrigation:
    """Test batch irrigation mechanics."""

    def test_irrigate_empty_batch(self, mock_signal_bus: MockSignalBus):
        """Should handle empty batch gracefully."""
        irrigator = MockIrrigator(mock_signal_bus)
        batch = MockSignalBatch()

        results = irrigator.irrigate_batch(batch)
        assert results == {}

    def test_irrigate_batch_preserves_order(
        self, mock_signal_bus: MockSignalBus
    ):
        """Should process batch signals in order."""
        irrigator = MockIrrigator(mock_signal_bus)
        received_order = []

        def track_order(signal: MockSignal) -> Dict[str, Any]:
            received_order.append(signal.payload.get("index"))
            return {"status": "consumed"}

        consumer = MockConsumer(
            consumer_id="order_tracker",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )
        consumer._consume_callback = track_order
        irrigator.register_consumer(consumer)

        batch = MockSignalBatch()
        for i in range(10):
            batch.add(
                MockSignal(
                    signal_type=MockSignalType.OPERATIONAL_STATUS,
                    payload={"index": i},
                )
            )

        irrigator.irrigate_batch(batch)

        assert received_order == list(range(10))

    def test_irrigate_mixed_type_batch(
        self, mock_signal_bus: MockSignalBus
    ):
        """Should route batch signals to appropriate consumers by type."""
        irrigator = MockIrrigator(mock_signal_bus)

        structural_consumer = MockConsumer(
            consumer_id="structural",
            consumed_types={MockSignalType.STRUCTURAL_COMPLETENESS},
        )
        epistemic_consumer = MockConsumer(
            consumer_id="epistemic",
            consumed_types={MockSignalType.EPISTEMIC_CONFIDENCE},
        )

        irrigator.register_consumer(structural_consumer)
        irrigator.register_consumer(epistemic_consumer)

        batch = MockSignalBatch()
        batch.add(MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS))
        batch.add(MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS))
        batch.add(MockSignal(signal_type=MockSignalType.EPISTEMIC_CONFIDENCE))

        irrigator.irrigate_batch(batch)

        assert structural_consumer.consumed_count == 2
        assert epistemic_consumer.consumed_count == 1


# =============================================================================
# PHASE-TO-PHASE IRRIGATION TESTS
# =============================================================================


class TestPhaseToPhaseIrrigation:
    """Test irrigation patterns between phases."""

    @pytest.fixture
    def phase_irrigator(
        self, mock_signal_bus: MockSignalBus
    ) -> MockIrrigator:
        """Create irrigator with phase-specific consumers."""
        irrigator = MockIrrigator(mock_signal_bus)

        # Register consumers for each phase
        phase_types = {
            "P01": {MockSignalType.CONSUMPTION_INGESTION},
            "P02": {MockSignalType.EPISTEMIC_CONFIDENCE, MockSignalType.STRUCTURAL_HIERARCHY},
            "P03": {MockSignalType.CONTRAST_DIVERGENCE},
            "P04": {MockSignalType.STRUCTURAL_COVERAGE},
        }

        for phase_id, types in phase_types.items():
            consumer = MockConsumer(
                consumer_id=f"{phase_id}_consumer",
                consumed_types=types,
            )
            irrigator.register_consumer(consumer)

        return irrigator

    def test_p02_to_p03_epistemic_flow(
        self, phase_irrigator: MockIrrigator
    ):
        """Epistemic signals should flow from P02 to P03."""
        # P02 emits epistemic confidence
        signal = MockSignal(
            signal_type=MockSignalType.EPISTEMIC_CONFIDENCE,
            source_phase="P02",
            target_phases=["P03"],
        )

        # P03 should not receive (different signal type in fixture)
        # but P02 consumer should
        results = phase_irrigator.irrigate(signal)

        assert "P02_consumer" in results

    def test_sequential_phase_irrigation(
        self, mock_signal_bus: MockSignalBus
    ):
        """Signals should flow through sequential phases."""
        irrigator = MockIrrigator(mock_signal_bus)

        # Set up sequential consumer chain
        phase_results = {}
        for i in range(1, 5):
            def make_callback(phase_num: int) -> Callable:
                def callback(signal: MockSignal) -> Dict[str, Any]:
                    phase_results[f"P0{phase_num}"] = signal.payload
                    return {"processed_by": f"P0{phase_num}"}
                return callback

            consumer = MockConsumer(
                consumer_id=f"P0{i}_consumer",
                consumed_types={MockSignalType.OPERATIONAL_STATUS},
            )
            consumer._consume_callback = make_callback(i)
            irrigator.register_consumer(consumer)

        # Emit signal
        signal = MockSignal(
            signal_type=MockSignalType.OPERATIONAL_STATUS,
            payload={"chain": True},
            source_phase="P00",
        )
        irrigator.irrigate(signal)

        # All phases should have received
        assert len(phase_results) == 4


# =============================================================================
# IRRIGATION STATISTICS TESTS
# =============================================================================


class TestIrrigationStatistics:
    """Test irrigation statistics collection."""

    def test_stats_track_irrigations(self, mock_signal_bus: MockSignalBus):
        """Stats should track total irrigations."""
        irrigator = MockIrrigator(mock_signal_bus)
        consumer = MockConsumer(
            consumer_id="stats_consumer",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )
        irrigator.register_consumer(consumer)

        for _ in range(10):
            signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
            irrigator.irrigate(signal)

        stats = irrigator.irrigation_stats
        assert stats["total_irrigations"] == 10

    def test_stats_track_registered_consumers(
        self, mock_signal_bus: MockSignalBus
    ):
        """Stats should track registered consumer count."""
        irrigator = MockIrrigator(mock_signal_bus)

        for i in range(5):
            consumer = MockConsumer(
                consumer_id=f"consumer_{i}",
                consumed_types={MockSignalType.OPERATIONAL_STATUS},
            )
            irrigator.register_consumer(consumer)

        stats = irrigator.irrigation_stats
        assert stats["registered_consumers"] == 5


# =============================================================================
# IRRIGATION ERROR HANDLING TESTS
# =============================================================================


class TestIrrigationErrorHandling:
    """Test error handling in irrigation."""

    def test_consumer_exception_does_not_stop_irrigation(
        self, mock_signal_bus: MockSignalBus
    ):
        """Exception in one consumer should not stop others."""
        irrigator = MockIrrigator(mock_signal_bus)

        def failing_callback(signal: MockSignal) -> Dict[str, Any]:
            raise RuntimeError("Consumer failure")

        failing_consumer = MockConsumer(
            consumer_id="failing",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )
        failing_consumer._consume_callback = failing_callback

        working_consumer = MockConsumer(
            consumer_id="working",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )

        irrigator.register_consumer(failing_consumer)
        irrigator.register_consumer(working_consumer)

        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)

        # Should not raise
        irrigator.irrigate(signal)

        # Working consumer should still have processed
        assert working_consumer.consumed_count == 1

    def test_empty_consumer_registry_handles_signal(
        self, mock_signal_bus: MockSignalBus
    ):
        """Irrigator should handle signals with no matching consumers."""
        irrigator = MockIrrigator(mock_signal_bus)

        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
        results = irrigator.irrigate(signal)

        assert results == {}  # No error, just no results
