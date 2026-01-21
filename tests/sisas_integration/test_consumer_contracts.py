"""
SISAS Consumer Contract Compliance Tests - JOBFRONT A Product.

This module tests consumer contract compliance, ensuring consumers properly
implement required interfaces and honor signal contracts.
All tests are SELF-CONTAINED using mocks from conftest.py.

Created: 2026-01-19T22:58:54.465Z
Jobfront: A - Test Infrastructure
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Set
from unittest.mock import MagicMock

import pytest

from tests.sisas_integration.conftest import (
    MockConsumer,
    MockConsumerProtocol,
    MockIrrigator,
    MockSignal,
    MockSignalBus,
    MockSignalPriority,
    MockSignalType,
)


# =============================================================================
# CONSUMER CONTRACT DEFINITIONS
# =============================================================================


@dataclass
class ConsumerContract:
    """Defines the contract a consumer must fulfill."""

    consumer_id: str
    required_signal_types: Set[MockSignalType]
    optional_signal_types: Set[MockSignalType] = field(default_factory=set)
    must_acknowledge: bool = True
    max_processing_time_ms: int = 1000
    required_output_fields: List[str] = field(default_factory=list)
    phase_affinity: Optional[str] = None


# Phase-specific consumer contracts
PHASE_CONSUMER_CONTRACTS = {
    "P00_assembly_consumer": ConsumerContract(
        consumer_id="P00_assembly_consumer",
        required_signal_types={MockSignalType.ORCHESTRATION_PHASE_START},
        required_output_fields=["acknowledged", "timestamp"],
        phase_affinity="P00",
    ),
    "P01_extraction_consumer": ConsumerContract(
        consumer_id="P01_extraction_consumer",
        required_signal_types={
            MockSignalType.CONSUMPTION_INGESTION,
            MockSignalType.STRUCTURAL_COMPLETENESS,
        },
        optional_signal_types={MockSignalType.INTEGRITY_HASH},
        required_output_fields=["extracted_chunks", "chunk_count"],
        phase_affinity="P01",
    ),
    "P02_enrichment_consumer": ConsumerContract(
        consumer_id="P02_enrichment_consumer",
        required_signal_types={
            MockSignalType.EPISTEMIC_CONFIDENCE,
            MockSignalType.EPISTEMIC_PROVENANCE,
        },
        required_output_fields=["enriched_data", "confidence_scores"],
        phase_affinity="P02",
    ),
    "P02_factory_consumer": ConsumerContract(
        consumer_id="P02_factory_consumer",
        required_signal_types={MockSignalType.STRUCTURAL_HIERARCHY},
        required_output_fields=["executors_created", "binding_map"],
        phase_affinity="P02",
    ),
    "P03_validation_consumer": ConsumerContract(
        consumer_id="P03_validation_consumer",
        required_signal_types={MockSignalType.CONTRAST_DIVERGENCE},
        required_output_fields=["validation_result", "divergences"],
        phase_affinity="P03",
    ),
    "P04_dimension_consumer": ConsumerContract(
        consumer_id="P04_dimension_consumer",
        required_signal_types={
            MockSignalType.STRUCTURAL_COVERAGE,
            MockSignalType.EPISTEMIC_UNCERTAINTY,
        },
        required_output_fields=["dimension_scores", "coverage_map"],
        phase_affinity="P04",
    ),
    "P05_policy_area_consumer": ConsumerContract(
        consumer_id="P05_policy_area_consumer",
        required_signal_types={MockSignalType.STRUCTURAL_COVERAGE},
        required_output_fields=["policy_area_scores"],
        phase_affinity="P05",
    ),
    "P06_cluster_consumer": ConsumerContract(
        consumer_id="P06_cluster_consumer",
        required_signal_types={MockSignalType.STRUCTURAL_COVERAGE},
        required_output_fields=["cluster_scores"],
        phase_affinity="P06",
    ),
    "P07_macro_consumer": ConsumerContract(
        consumer_id="P07_macro_consumer",
        required_signal_types={MockSignalType.CONTRAST_ALIGNMENT},
        required_output_fields=["macro_score", "alignment_report"],
        phase_affinity="P07",
    ),
    "P08_recommendation_consumer": ConsumerContract(
        consumer_id="P08_recommendation_consumer",
        required_signal_types={MockSignalType.ORCHESTRATION_DECISION},
        required_output_fields=["recommendations", "priority_order"],
        phase_affinity="P08",
    ),
    "P09_report_consumer": ConsumerContract(
        consumer_id="P09_report_consumer",
        required_signal_types={
            MockSignalType.ORCHESTRATION_PHASE_COMPLETE,
            MockSignalType.INTEGRITY_HASH,
        },
        required_output_fields=["report_generated", "output_path"],
        phase_affinity="P09",
    ),
}


# =============================================================================
# CONTRACT-COMPLIANT MOCK CONSUMER
# =============================================================================


@dataclass
class ContractCompliantConsumer:
    """A consumer that follows its contract."""

    contract: ConsumerContract
    _consumed_signals: List[MockSignal] = field(default_factory=list)
    _compliance_violations: List[str] = field(default_factory=list)

    @property
    def consumer_id(self) -> str:
        return self.contract.consumer_id

    @property
    def consumed_types(self) -> Set[MockSignalType]:
        return self.contract.required_signal_types | self.contract.optional_signal_types

    def can_consume(self, signal: MockSignal) -> bool:
        """Check if consumer can handle signal type."""
        return signal.signal_type in self.consumed_types

    def consume(self, signal: MockSignal) -> Dict[str, Any]:
        """Consume a signal according to contract."""
        self._consumed_signals.append(signal)

        # Build compliant response
        response = {
            "status": "consumed",
            "signal_id": signal.signal_id,
            "consumer_id": self.consumer_id,
        }

        # Add required output fields
        for field_name in self.contract.required_output_fields:
            response[field_name] = self._generate_field_value(field_name, signal)

        # Add acknowledgment if required
        if self.contract.must_acknowledge:
            response["acknowledged"] = True
            response["timestamp"] = signal.timestamp.isoformat()

        return response

    def _generate_field_value(self, field_name: str, signal: MockSignal) -> Any:
        """Generate mock value for a required field."""
        mock_values = {
            "extracted_chunks": [],
            "chunk_count": 0,
            "enriched_data": {},
            "confidence_scores": {},
            "executors_created": 0,
            "binding_map": {},
            "validation_result": "PASSED",
            "divergences": [],
            "dimension_scores": {},
            "coverage_map": {},
            "policy_area_scores": {},
            "cluster_scores": {},
            "macro_score": 0.0,
            "alignment_report": {},
            "recommendations": [],
            "priority_order": [],
            "report_generated": True,
            "output_path": "/tmp/report.json",
        }
        return mock_values.get(field_name, None)

    @property
    def consumed_count(self) -> int:
        return len(self._consumed_signals)

    def validate_contract_compliance(self) -> List[str]:
        """Validate that consumer behavior complies with contract."""
        violations = []

        # Check that all required signal types were at least attempted
        consumed_types = {s.signal_type for s in self._consumed_signals}
        missing = self.contract.required_signal_types - consumed_types
        if missing:
            violations.append(
                f"Never received required signal types: {[m.value for m in missing]}"
            )

        return violations


# =============================================================================
# CONSUMER CONTRACT COMPLIANCE TESTS
# =============================================================================


class TestConsumerContractDefinitions:
    """Test consumer contract definitions are complete and valid."""

    def test_all_phases_have_contracts(self):
        """Every phase should have at least one consumer contract."""
        phases_with_contracts = set()
        for contract in PHASE_CONSUMER_CONTRACTS.values():
            if contract.phase_affinity:
                phases_with_contracts.add(contract.phase_affinity)

        expected_phases = {f"P0{i}" for i in range(10)}
        missing = expected_phases - phases_with_contracts
        assert not missing, f"Missing consumer contracts for phases: {missing}"

    def test_contracts_have_required_signal_types(self):
        """All contracts should have at least one required signal type."""
        for name, contract in PHASE_CONSUMER_CONTRACTS.items():
            assert len(contract.required_signal_types) > 0, (
                f"Contract {name} has no required signal types"
            )

    def test_contracts_have_unique_ids(self):
        """All contracts should have unique consumer IDs."""
        ids = [c.consumer_id for c in PHASE_CONSUMER_CONTRACTS.values()]
        assert len(ids) == len(set(ids)), "Duplicate consumer IDs found"

    def test_contracts_have_required_output_fields(self):
        """All contracts should specify required output fields."""
        for name, contract in PHASE_CONSUMER_CONTRACTS.items():
            assert len(contract.required_output_fields) > 0, (
                f"Contract {name} has no required output fields"
            )


# =============================================================================
# CONSUMER PROTOCOL COMPLIANCE TESTS
# =============================================================================


class TestConsumerProtocolCompliance:
    """Test that consumers comply with the consumer protocol."""

    def test_mock_consumer_has_consumer_id(self):
        """Consumer should have consumer_id attribute."""
        consumer = MockConsumer(consumer_id="test_consumer")
        assert hasattr(consumer, "consumer_id")
        assert consumer.consumer_id == "test_consumer"

    def test_mock_consumer_has_consumed_types(self):
        """Consumer should have consumed_types attribute."""
        consumer = MockConsumer(
            consumer_id="test",
            consumed_types={MockSignalType.OPERATIONAL_STATUS},
        )
        assert hasattr(consumer, "consumed_types")
        assert MockSignalType.OPERATIONAL_STATUS in consumer.consumed_types

    def test_mock_consumer_has_consume_method(self):
        """Consumer should have consume method."""
        consumer = MockConsumer(consumer_id="test")
        assert hasattr(consumer, "consume")
        assert callable(consumer.consume)

    def test_mock_consumer_has_can_consume_method(self):
        """Consumer should have can_consume method."""
        consumer = MockConsumer(consumer_id="test")
        assert hasattr(consumer, "can_consume")
        assert callable(consumer.can_consume)

    def test_contract_compliant_consumer_implements_protocol(self):
        """ContractCompliantConsumer should implement full protocol."""
        contract = PHASE_CONSUMER_CONTRACTS["P01_extraction_consumer"]
        consumer = ContractCompliantConsumer(contract=contract)

        assert hasattr(consumer, "consumer_id")
        assert hasattr(consumer, "consumed_types")
        assert hasattr(consumer, "consume")
        assert hasattr(consumer, "can_consume")


# =============================================================================
# CONSUMER BEHAVIOR COMPLIANCE TESTS
# =============================================================================


class TestConsumerBehaviorCompliance:
    """Test that consumer behavior complies with contracts."""

    def test_consumer_only_consumes_declared_types(self):
        """Consumer should only accept signals of declared types."""
        contract = PHASE_CONSUMER_CONTRACTS["P02_enrichment_consumer"]
        consumer = ContractCompliantConsumer(contract=contract)

        matching_signal = MockSignal(signal_type=MockSignalType.EPISTEMIC_CONFIDENCE)
        non_matching_signal = MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS)

        assert consumer.can_consume(matching_signal)
        assert not consumer.can_consume(non_matching_signal)

    def test_consumer_returns_required_fields(self):
        """Consumer should return all required output fields."""
        contract = PHASE_CONSUMER_CONTRACTS["P04_dimension_consumer"]
        consumer = ContractCompliantConsumer(contract=contract)

        signal = MockSignal(signal_type=MockSignalType.STRUCTURAL_COVERAGE)
        result = consumer.consume(signal)

        for required_field in contract.required_output_fields:
            assert required_field in result, (
                f"Missing required field: {required_field}"
            )

    def test_consumer_acknowledges_when_required(self):
        """Consumer should acknowledge when contract requires it."""
        contract = ConsumerContract(
            consumer_id="ack_consumer",
            required_signal_types={MockSignalType.OPERATIONAL_STATUS},
            must_acknowledge=True,
            required_output_fields=[],
        )
        consumer = ContractCompliantConsumer(contract=contract)

        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
        result = consumer.consume(signal)

        assert result.get("acknowledged") is True
        assert "timestamp" in result

    def test_consumer_tracks_consumed_signals(self):
        """Consumer should track all consumed signals."""
        contract = PHASE_CONSUMER_CONTRACTS["P01_extraction_consumer"]
        consumer = ContractCompliantConsumer(contract=contract)

        signals = [
            MockSignal(signal_type=MockSignalType.CONSUMPTION_INGESTION),
            MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS),
        ]

        for signal in signals:
            consumer.consume(signal)

        assert consumer.consumed_count == 2


# =============================================================================
# PHASE-SPECIFIC CONSUMER CONTRACT TESTS
# =============================================================================


class TestPhaseSpecificContracts:
    """Test phase-specific consumer contracts."""

    def test_p00_assembly_consumer_contract(self):
        """P00 assembly consumer should handle phase start signals."""
        contract = PHASE_CONSUMER_CONTRACTS["P00_assembly_consumer"]
        consumer = ContractCompliantConsumer(contract=contract)

        signal = MockSignal(
            signal_type=MockSignalType.ORCHESTRATION_PHASE_START,
            payload={"phase_id": "P00"},
        )

        assert consumer.can_consume(signal)
        result = consumer.consume(signal)
        assert "acknowledged" in result
        assert "timestamp" in result

    def test_p02_factory_consumer_contract(self):
        """P02 factory consumer should handle hierarchy signals."""
        contract = PHASE_CONSUMER_CONTRACTS["P02_factory_consumer"]
        consumer = ContractCompliantConsumer(contract=contract)

        signal = MockSignal(
            signal_type=MockSignalType.STRUCTURAL_HIERARCHY,
            payload={"hierarchy_depth": 3},
        )

        result = consumer.consume(signal)
        assert "executors_created" in result
        assert "binding_map" in result

    def test_p04_dimension_consumer_multiple_signal_types(self):
        """P04 consumer should handle multiple signal types."""
        contract = PHASE_CONSUMER_CONTRACTS["P04_dimension_consumer"]
        consumer = ContractCompliantConsumer(contract=contract)

        # Should handle both required types
        coverage_signal = MockSignal(signal_type=MockSignalType.STRUCTURAL_COVERAGE)
        uncertainty_signal = MockSignal(signal_type=MockSignalType.EPISTEMIC_UNCERTAINTY)

        assert consumer.can_consume(coverage_signal)
        assert consumer.can_consume(uncertainty_signal)

    def test_p09_report_consumer_final_signals(self):
        """P09 report consumer should handle final pipeline signals."""
        contract = PHASE_CONSUMER_CONTRACTS["P09_report_consumer"]
        consumer = ContractCompliantConsumer(contract=contract)

        complete_signal = MockSignal(
            signal_type=MockSignalType.ORCHESTRATION_PHASE_COMPLETE,
            payload={"phase_id": "P09", "success": True},
        )
        hash_signal = MockSignal(
            signal_type=MockSignalType.INTEGRITY_HASH,
            payload={"hash": "abc123"},
        )

        assert consumer.can_consume(complete_signal)
        assert consumer.can_consume(hash_signal)

        result = consumer.consume(complete_signal)
        assert "report_generated" in result
        assert "output_path" in result


# =============================================================================
# CONTRACT VIOLATION DETECTION TESTS
# =============================================================================


class TestContractViolationDetection:
    """Test detection of contract violations."""

    def test_detect_missing_required_signal_types(self):
        """Should detect when required signal types are never received."""
        contract = ConsumerContract(
            consumer_id="test_consumer",
            required_signal_types={
                MockSignalType.STRUCTURAL_COMPLETENESS,
                MockSignalType.EPISTEMIC_CONFIDENCE,
            },
            required_output_fields=[],
        )
        consumer = ContractCompliantConsumer(contract=contract)

        # Only consume one of two required types
        signal = MockSignal(signal_type=MockSignalType.STRUCTURAL_COMPLETENESS)
        consumer.consume(signal)

        violations = consumer.validate_contract_compliance()
        assert len(violations) > 0
        assert "epistemic.confidence" in str(violations[0])

    def test_no_violations_when_compliant(self):
        """Should report no violations when consumer is compliant."""
        contract = ConsumerContract(
            consumer_id="test_consumer",
            required_signal_types={MockSignalType.OPERATIONAL_STATUS},
            required_output_fields=[],
        )
        consumer = ContractCompliantConsumer(contract=contract)

        signal = MockSignal(signal_type=MockSignalType.OPERATIONAL_STATUS)
        consumer.consume(signal)

        violations = consumer.validate_contract_compliance()
        assert len(violations) == 0


# =============================================================================
# CONSUMER INTEGRATION TESTS
# =============================================================================


class TestConsumerIntegration:
    """Test consumer integration with irrigator."""

    def test_irrigator_respects_consumer_contracts(self, mock_signal_bus: MockSignalBus):
        """Irrigator should only route signals to matching consumers."""
        irrigator = MockIrrigator(mock_signal_bus)

        # Register consumers with different contracts
        p01_contract = PHASE_CONSUMER_CONTRACTS["P01_extraction_consumer"]
        p02_contract = PHASE_CONSUMER_CONTRACTS["P02_enrichment_consumer"]

        p01_consumer = ContractCompliantConsumer(contract=p01_contract)
        p02_consumer = ContractCompliantConsumer(contract=p02_contract)

        irrigator.register_consumer(
            MockConsumer(
                consumer_id=p01_consumer.consumer_id,
                consumed_types=p01_consumer.consumed_types,
            )
        )
        irrigator.register_consumer(
            MockConsumer(
                consumer_id=p02_consumer.consumer_id,
                consumed_types=p02_consumer.consumed_types,
            )
        )

        # Emit a signal only P02 consumer should handle
        signal = MockSignal(signal_type=MockSignalType.EPISTEMIC_CONFIDENCE)
        results = irrigator.irrigate(signal)

        # Only P02 should have processed
        assert p02_consumer.consumer_id in results
        assert p01_consumer.consumer_id not in results

    def test_multiple_consumers_same_signal_type(self, mock_signal_bus: MockSignalBus):
        """Multiple consumers can handle the same signal type."""
        irrigator = MockIrrigator(mock_signal_bus)

        consumer1 = MockConsumer(
            consumer_id="consumer_1",
            consumed_types={MockSignalType.STRUCTURAL_COVERAGE},
        )
        consumer2 = MockConsumer(
            consumer_id="consumer_2",
            consumed_types={MockSignalType.STRUCTURAL_COVERAGE},
        )

        irrigator.register_consumer(consumer1)
        irrigator.register_consumer(consumer2)

        signal = MockSignal(signal_type=MockSignalType.STRUCTURAL_COVERAGE)
        results = irrigator.irrigate(signal)

        assert "consumer_1" in results
        assert "consumer_2" in results
        assert consumer1.consumed_count == 1
        assert consumer2.consumed_count == 1
