"""
SISAS Signal Type Validation Tests - JOBFRONT A Product.

This module tests signal type definitions, schemas, and validation rules.
All tests are SELF-CONTAINED using mocks from conftest.py.

Created: 2026-01-19T22:58:54.465Z
Jobfront: A - Test Infrastructure
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

import pytest

from tests.sisas_integration.conftest import (
    MockSignal,
    MockSignalBatch,
    MockSignalPriority,
    MockSignalRegistry,
    MockSignalType,
)


# =============================================================================
# SIGNAL TYPE ENUMERATION TESTS
# =============================================================================


class TestSignalTypeEnumeration:
    """Test signal type enumeration completeness and correctness."""

    def test_all_signal_types_have_category_prefix(self):
        """All signal types should have a category prefix (e.g., 'structural.')."""
        for signal_type in MockSignalType:
            assert "." in signal_type.value, (
                f"Signal type {signal_type.name} missing category prefix"
            )

    def test_signal_type_categories(self):
        """Verify all expected signal categories exist."""
        categories = set()
        for signal_type in MockSignalType:
            category = signal_type.value.split(".")[0]
            categories.add(category)

        expected_categories = {
            "structural",
            "epistemic",
            "operational",
            "contrast",
            "consumption",
            "integrity",
            "orchestration",
        }
        assert categories == expected_categories, (
            f"Missing categories: {expected_categories - categories}, "
            f"Extra categories: {categories - expected_categories}"
        )

    def test_signal_type_uniqueness(self):
        """All signal type values must be unique."""
        values = [st.value for st in MockSignalType]
        assert len(values) == len(set(values)), "Duplicate signal type values found"

    def test_structural_signal_types(self):
        """Verify structural signal types."""
        structural_types = [
            st for st in MockSignalType if st.value.startswith("structural.")
        ]
        assert len(structural_types) >= 3, "Expected at least 3 structural signal types"
        type_names = [st.name for st in structural_types]
        assert "STRUCTURAL_COMPLETENESS" in type_names
        assert "STRUCTURAL_HIERARCHY" in type_names
        assert "STRUCTURAL_COVERAGE" in type_names

    def test_epistemic_signal_types(self):
        """Verify epistemic signal types."""
        epistemic_types = [
            st for st in MockSignalType if st.value.startswith("epistemic.")
        ]
        assert len(epistemic_types) >= 3, "Expected at least 3 epistemic signal types"
        type_names = [st.name for st in epistemic_types]
        assert "EPISTEMIC_CONFIDENCE" in type_names
        assert "EPISTEMIC_UNCERTAINTY" in type_names
        assert "EPISTEMIC_PROVENANCE" in type_names

    def test_orchestration_signal_types(self):
        """Verify orchestration signal types for phase management."""
        orchestration_types = [
            st for st in MockSignalType if st.value.startswith("orchestration.")
        ]
        assert len(orchestration_types) >= 3, "Expected at least 3 orchestration signal types"
        type_names = [st.name for st in orchestration_types]
        assert "ORCHESTRATION_PHASE_START" in type_names
        assert "ORCHESTRATION_PHASE_COMPLETE" in type_names
        assert "ORCHESTRATION_DECISION" in type_names


# =============================================================================
# SIGNAL PRIORITY TESTS
# =============================================================================


class TestSignalPriority:
    """Test signal priority levels."""

    def test_all_priority_levels_exist(self):
        """Verify all expected priority levels exist."""
        expected_priorities = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "DEBUG"}
        actual_priorities = {p.name for p in MockSignalPriority}
        assert actual_priorities == expected_priorities

    def test_priority_ordering_convention(self):
        """Verify priority ordering follows convention (CRITICAL > HIGH > MEDIUM > LOW > DEBUG)."""
        priority_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "DEBUG"]
        for i, priority_name in enumerate(priority_order):
            assert hasattr(MockSignalPriority, priority_name), (
                f"Missing priority: {priority_name}"
            )


# =============================================================================
# SIGNAL DATACLASS TESTS
# =============================================================================


class TestMockSignalDataclass:
    """Test MockSignal dataclass behavior."""

    def test_signal_creation_with_defaults(self):
        """Signal should be creatable with minimal arguments."""
        signal = MockSignal()
        assert signal.signal_id is not None
        assert signal.signal_type == MockSignalType.OPERATIONAL_STATUS
        assert signal.payload == {}
        assert signal.source_phase == "P00"
        assert signal.target_phases == []
        assert signal.priority == MockSignalPriority.MEDIUM
        assert signal.timestamp is not None
        assert signal.ttl_seconds == 3600
        assert signal.consumed_by == set()

    def test_signal_creation_with_custom_values(self):
        """Signal should accept custom values."""
        custom_payload = {"score": 0.95, "dimension": "DIM01"}
        signal = MockSignal(
            signal_type=MockSignalType.STRUCTURAL_COMPLETENESS,
            payload=custom_payload,
            source_phase="P02",
            target_phases=["P03", "P04"],
            priority=MockSignalPriority.HIGH,
            ttl_seconds=7200,
        )
        assert signal.signal_type == MockSignalType.STRUCTURAL_COMPLETENESS
        assert signal.payload == custom_payload
        assert signal.source_phase == "P02"
        assert signal.target_phases == ["P03", "P04"]
        assert signal.priority == MockSignalPriority.HIGH
        assert signal.ttl_seconds == 7200

    def test_signal_id_uniqueness(self):
        """Each signal should have a unique ID."""
        signals = [MockSignal() for _ in range(100)]
        ids = [s.signal_id for s in signals]
        assert len(ids) == len(set(ids)), "Signal IDs are not unique"

    def test_signal_serialization_to_dict(self):
        """Signal should serialize to dictionary correctly."""
        signal = MockSignal(
            signal_type=MockSignalType.EPISTEMIC_CONFIDENCE,
            payload={"confidence": 0.87},
            source_phase="P02",
            target_phases=["P03"],
            priority=MockSignalPriority.HIGH,
        )
        d = signal.to_dict()

        assert d["signal_id"] == signal.signal_id
        assert d["signal_type"] == "epistemic.confidence"
        assert d["payload"] == {"confidence": 0.87}
        assert d["source_phase"] == "P02"
        assert d["target_phases"] == ["P03"]
        assert d["priority"] == "HIGH"
        assert "timestamp" in d
        assert d["ttl_seconds"] == 3600
        assert d["consumed_by"] == []

    def test_signal_serialization_is_json_compatible(self):
        """Serialized signal should be JSON-encodable."""
        signal = MockSignal(
            payload={"nested": {"value": [1, 2, 3]}},
        )
        d = signal.to_dict()
        # Should not raise
        json_str = json.dumps(d)
        assert len(json_str) > 0

    def test_signal_deserialization_from_dict(self):
        """Signal should deserialize from dictionary correctly."""
        original = MockSignal(
            signal_type=MockSignalType.CONTRAST_DIVERGENCE,
            payload={"divergence": 0.15},
            source_phase="P03",
            target_phases=["P04", "P05"],
        )
        d = original.to_dict()
        restored = MockSignal.from_dict(d)

        assert restored.signal_id == original.signal_id
        assert restored.signal_type == original.signal_type
        assert restored.payload == original.payload
        assert restored.source_phase == original.source_phase
        assert restored.target_phases == original.target_phases

    def test_signal_consumed_by_tracking(self):
        """Signal should track which consumers have consumed it."""
        signal = MockSignal()
        assert len(signal.consumed_by) == 0

        signal.consumed_by.add("consumer_1")
        assert "consumer_1" in signal.consumed_by

        signal.consumed_by.add("consumer_2")
        assert len(signal.consumed_by) == 2


# =============================================================================
# SIGNAL BATCH TESTS
# =============================================================================


class TestMockSignalBatch:
    """Test MockSignalBatch behavior."""

    def test_batch_creation(self):
        """Batch should be creatable with defaults."""
        batch = MockSignalBatch()
        assert batch.batch_id is not None
        assert len(batch) == 0
        assert batch.created_at is not None

    def test_batch_add_signal(self):
        """Batch should accept signals."""
        batch = MockSignalBatch()
        signal = MockSignal()
        batch.add(signal)
        assert len(batch) == 1

    def test_batch_multiple_signals(self):
        """Batch should handle multiple signals."""
        batch = MockSignalBatch()
        for i in range(10):
            batch.add(MockSignal(payload={"index": i}))
        assert len(batch) == 10

    def test_batch_iteration(self):
        """Batch should be iterable."""
        batch = MockSignalBatch()
        signals = [MockSignal(payload={"i": i}) for i in range(5)]
        for s in signals:
            batch.add(s)

        iterated = list(batch)
        assert len(iterated) == 5
        for i, s in enumerate(iterated):
            assert s.payload["i"] == i


# =============================================================================
# SIGNAL REGISTRY TESTS
# =============================================================================


class TestMockSignalRegistry:
    """Test MockSignalRegistry behavior."""

    def test_registry_creation(self):
        """Registry should be creatable."""
        registry = MockSignalRegistry()
        assert len(registry.get_all_types()) == 0

    def test_register_signal_type(self):
        """Registry should accept type registration."""
        registry = MockSignalRegistry()
        registry.register_type(MockSignalType.STRUCTURAL_COMPLETENESS)
        assert registry.is_registered(MockSignalType.STRUCTURAL_COMPLETENESS)
        assert not registry.is_registered(MockSignalType.EPISTEMIC_CONFIDENCE)

    def test_register_type_with_schema(self):
        """Registry should accept schema with type."""
        registry = MockSignalRegistry()
        schema = {
            "type": "object",
            "properties": {
                "score": {"type": "number", "minimum": 0, "maximum": 1},
            },
        }
        registry.register_type(MockSignalType.STRUCTURAL_COMPLETENESS, schema=schema)
        assert registry.is_registered(MockSignalType.STRUCTURAL_COMPLETENESS)

    def test_register_type_with_validator(self):
        """Registry should accept custom validator with type."""
        registry = MockSignalRegistry()

        def validator(signal: MockSignal) -> bool:
            return "score" in signal.payload

        registry.register_type(
            MockSignalType.STRUCTURAL_COMPLETENESS,
            validator=validator,
        )

        valid_signal = MockSignal(
            signal_type=MockSignalType.STRUCTURAL_COMPLETENESS,
            payload={"score": 0.95},
        )
        invalid_signal = MockSignal(
            signal_type=MockSignalType.STRUCTURAL_COMPLETENESS,
            payload={"other": "data"},
        )

        assert registry.validate_signal(valid_signal)
        assert not registry.validate_signal(invalid_signal)

    def test_validate_unregistered_type_fails(self):
        """Validation should fail for unregistered types."""
        registry = MockSignalRegistry()
        signal = MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS)
        assert not registry.validate_signal(signal)

    def test_get_all_types(self):
        """Registry should return all registered types."""
        registry = MockSignalRegistry()
        types_to_register = [
            MockSignalType.STRUCTURAL_COMPLETENESS,
            MockSignalType.EPISTEMIC_CONFIDENCE,
            MockSignalType.OPERATIONAL_STATUS,
        ]
        for st in types_to_register:
            registry.register_type(st)

        all_types = registry.get_all_types()
        assert all_types == set(types_to_register)


# =============================================================================
# SIGNAL VALIDATION RULE TESTS
# =============================================================================


class TestSignalValidationRules:
    """Test signal validation rules and constraints."""

    def test_signal_must_have_valid_type(self, mock_signal_registry):
        """Signal must have a valid registered type."""
        signal = MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS)
        assert mock_signal_registry.validate_signal(signal)

    def test_signal_payload_can_be_empty(self):
        """Signal payload can be empty."""
        signal = MockSignal(payload={})
        assert signal.payload == {}

    def test_signal_payload_accepts_nested_data(self):
        """Signal payload should accept nested data structures."""
        nested_payload = {
            "level1": {
                "level2": {
                    "level3": {"value": 42},
                },
            },
            "array": [1, 2, {"nested": True}],
        }
        signal = MockSignal(payload=nested_payload)
        assert signal.payload["level1"]["level2"]["level3"]["value"] == 42
        assert signal.payload["array"][2]["nested"] is True

    def test_signal_source_phase_format(self):
        """Source phase should follow P## format."""
        valid_phases = ["P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09"]
        for phase in valid_phases:
            signal = MockSignal(source_phase=phase)
            assert signal.source_phase == phase

    def test_signal_target_phases_can_be_multiple(self):
        """Signal can target multiple phases."""
        signal = MockSignal(target_phases=["P03", "P04", "P05"])
        assert len(signal.target_phases) == 3

    def test_signal_ttl_must_be_positive(self):
        """Signal TTL should be positive."""
        signal = MockSignal(ttl_seconds=1)
        assert signal.ttl_seconds > 0

    def test_signal_timestamp_is_timezone_aware(self):
        """Signal timestamp should be timezone-aware."""
        signal = MockSignal()
        assert signal.timestamp.tzinfo is not None


# =============================================================================
# SIGNAL TYPE COMPATIBILITY TESTS
# =============================================================================


class TestSignalTypeCompatibility:
    """Test signal type compatibility and phase alignment."""

    @pytest.fixture
    def phase_signal_map(self) -> Dict[str, set]:
        """Map of phases to their expected signal types."""
        return {
            "P00": {MockSignalType.ORCHESTRATION_PHASE_START},
            "P01": {MockSignalType.CONSUMPTION_INGESTION},
            "P02": {MockSignalType.EPISTEMIC_CONFIDENCE, MockSignalType.STRUCTURAL_HIERARCHY},
            "P03": {MockSignalType.EPISTEMIC_CONFIDENCE, MockSignalType.CONTRAST_DIVERGENCE},
            "P04": {MockSignalType.STRUCTURAL_COVERAGE},
            "P05": {MockSignalType.STRUCTURAL_COVERAGE},
            "P06": {MockSignalType.STRUCTURAL_COVERAGE},
            "P07": {MockSignalType.CONTRAST_ALIGNMENT},
            "P08": {MockSignalType.ORCHESTRATION_DECISION},
            "P09": {MockSignalType.ORCHESTRATION_PHASE_COMPLETE},
        }

    def test_phase_signal_type_mapping_exists(self, phase_signal_map):
        """Every phase should have mapped signal types."""
        for phase_id in [f"P0{i}" for i in range(10)]:
            assert phase_id in phase_signal_map, f"Missing signal map for {phase_id}"
            assert len(phase_signal_map[phase_id]) > 0, f"Empty signal map for {phase_id}"

    def test_orchestration_signals_in_boundary_phases(self, phase_signal_map):
        """Orchestration signals should be in P00 and P09."""
        assert MockSignalType.ORCHESTRATION_PHASE_START in phase_signal_map["P00"]
        assert MockSignalType.ORCHESTRATION_PHASE_COMPLETE in phase_signal_map["P09"]

    def test_epistemic_signals_in_analysis_phases(self, phase_signal_map):
        """Epistemic signals should be in analysis phases (P02, P03)."""
        assert MockSignalType.EPISTEMIC_CONFIDENCE in phase_signal_map["P02"]
        assert MockSignalType.EPISTEMIC_CONFIDENCE in phase_signal_map["P03"]

    def test_structural_signals_in_aggregation_phases(self, phase_signal_map):
        """Structural signals should be in aggregation phases (P04-P06)."""
        for phase in ["P04", "P05", "P06"]:
            assert MockSignalType.STRUCTURAL_COVERAGE in phase_signal_map[phase]
