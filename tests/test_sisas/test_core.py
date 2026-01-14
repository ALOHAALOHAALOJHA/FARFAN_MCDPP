# tests/test_sisas/test_core.py

import pytest
from datetime import datetime
from uuid import uuid4
from dataclasses import dataclass

from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import (
    Signal, SignalContext, SignalSource, SignalCategory, SignalConfidence
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.event import (
    Event, EventStore, EventType, EventPayload
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.contracts import (
    PublicationContract, ConsumptionContract, IrrigationContract,
    ContractRegistry, ContractStatus, SignalTypeSpec
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import (
    SignalBus, BusRegistry, BusType, BusMessage
)


class TestSignalContext:
    """Tests para SignalContext"""

    def test_create_context(self):
        context = SignalContext(
            node_type="question",
            node_id="Q147",
            phase="phase_0",
            consumer_scope="Phase_0"
        )
        assert context.node_type == "question"
        assert context.node_id == "Q147"

    def test_context_to_dict(self):
        context = SignalContext(
            node_type="policy_area",
            node_id="PA03",
            phase="phase_2",
            consumer_scope="Phase_2"
        )
        d = context.to_dict()
        assert d["node_type"] == "policy_area"
        assert d["node_id"] == "PA03"

    def test_context_from_dict(self):
        data = {
            "node_type": "dimension",
            "node_id":  "DIM01",
            "phase": "phase_0",
            "consumer_scope": "Phase_0"
        }
        context = SignalContext.from_dict(data)
        assert context.node_type == "dimension"


class TestSignalSource:
    """Tests para SignalSource"""

    def test_create_source(self):
        source = SignalSource(
            event_id=str(uuid4()),
            source_file="questions.json",
            source_path="dimensions/DIM01/questions.json",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle="signal_registry"
        )
        assert source.generator_vehicle == "signal_registry"

    def test_source_to_dict(self):
        source = SignalSource(
            event_id="evt-123",
            source_file="metadata.json",
            source_path="clusters/CL01/metadata.json",
            generation_timestamp=datetime(2026, 1, 14, 10, 0, 0),
            generator_vehicle="signal_loader"
        )
        d = source.to_dict()
        assert d["event_id"] == "evt-123"
        assert "2026-01-14" in d["generation_timestamp"]


class TestEventStore:
    """Tests para EventStore"""

    def test_append_event(self):
        store = EventStore()
        event = Event(
            event_type=EventType.CANONICAL_DATA_LOADED,
            source_file="test.json",
            phase="phase_0"
        )
        event_id = store.append(event)
        assert event_id == event.event_id
        assert store.count() == 1

    def test_get_by_type(self):
        store = EventStore()

        e1 = Event(event_type=EventType.CANONICAL_DATA_LOADED, source_file="a.json")
        e2 = Event(event_type=EventType.CANONICAL_DATA_VALIDATED, source_file="b.json")
        e3 = Event(event_type=EventType.CANONICAL_DATA_LOADED, source_file="c.json")

        store.append(e1)
        store.append(e2)
        store.append(e3)

        loaded = store.get_by_type(EventType.CANONICAL_DATA_LOADED)
        assert len(loaded) == 2

    def test_get_by_phase(self):
        store = EventStore()

        e1 = Event(event_type=EventType.CANONICAL_DATA_LOADED, phase="phase_0")
        e2 = Event(event_type=EventType.CANONICAL_DATA_LOADED, phase="phase_1")
        e3 = Event(event_type=EventType.CANONICAL_DATA_LOADED, phase="phase_0")

        store.append(e1)
        store.append(e2)
        store.append(e3)

        phase0 = store.get_by_phase("phase_0")
        assert len(phase0) == 2

    def test_events_never_lost(self):
        """Axioma:  Ningún evento se pierde"""
        store = EventStore()

        for i in range(1000):
            event = Event(
                event_type=EventType. CANONICAL_DATA_LOADED,
                source_file=f"file_{i}.json"
            )
            store.append(event)

        assert store.count() == 1000


class TestContracts:
    """Tests para contratos"""

    def test_publication_contract_validation(self):
        contract = PublicationContract(
            contract_id="PC_TEST",
            publisher_vehicle="signal_registry",
            allowed_signal_types=[
                SignalTypeSpec(signal_type="StructuralAlignmentSignal"),
                SignalTypeSpec(signal_type="EventPresenceSignal")
            ],
            allowed_buses=["structural_bus", "integrity_bus"],
            require_context=True,
            require_source=True
        )

        # Crear señal mock para validación
        # Definimos una señal mock ya que no hemos implementado StructuralAlignmentSignal en core
        @dataclass
        class MockSignal(Signal):
            signal_type: str = "StructuralAlignmentSignal"
            @property
            def category(self) -> SignalCategory:
                return SignalCategory.STRUCTURAL

        context = SignalContext(
            node_type="test",
            node_id="test-1",
            phase="phase_0",
            consumer_scope="Test"
        )
        source = SignalSource(
            event_id="evt-1",
            source_file="test.json",
            source_path="test/test.json",
            generation_timestamp=datetime.utcnow(),
            generator_vehicle="test"
        )

        signal = MockSignal(
            context=context,
            source=source
        )

        is_valid, errors = contract.validate_signal(signal)
        assert is_valid
        assert len(errors) == 0

    def test_consumption_contract_filtering(self):
        contract = ConsumptionContract(
            contract_id="CC_TEST",
            consumer_id="test_consumer",
            consumer_phase="phase_0",
            subscribed_signal_types=["StructuralAlignmentSignal"],
            context_filters={
                "phase": ["phase_0", "phase_1"],
                "node_type": ["question", "dimension"]
            }
        )

        # Mock signal que coincide
        class MockSignal:
            signal_type = "StructuralAlignmentSignal"
            context = SignalContext(
                node_type="question",
                node_id="Q001",
                phase="phase_0",
                consumer_scope="Phase_0"
            )

        assert contract.matches_signal(MockSignal())

        # Mock signal que NO coincide (tipo incorrecto)
        class MockSignal2:
            signal_type = "OtherSignal"
            context = SignalContext(
                node_type="question",
                node_id="Q001",
                phase="phase_0",
                consumer_scope="Phase_0"
            )

        assert not contract.matches_signal(MockSignal2())

    def test_irrigation_contract_irrigability(self):
        # Contrato completo - puede irrigar
        contract1 = IrrigationContract(
            contract_id="IC_COMPLETE",
            source_file="test.json",
            source_path="test/test.json",
            source_phase="phase_0",
            vehicles=["signal_registry"],
            consumers=["consumer_1"],
            vocabulary_aligned=True,
            gaps=[],
            status=ContractStatus.ACTIVE
        )
        assert contract1.is_irrigable()

        # Contrato sin vehículos - NO puede irrigar
        contract2 = IrrigationContract(
            contract_id="IC_NO_VEHICLE",
            source_file="test2.json",
            source_path="test/test2.json",
            source_phase="phase_0",
            vehicles=[],
            consumers=["consumer_1"],
            vocabulary_aligned=True,
            gaps=["NECESITA_VEHICULO"],
            status=ContractStatus.DRAFT
        )
        assert not contract2.is_irrigable()
        assert "NECESITA_VEHICULO" in contract2.get_blocking_gaps()


class TestBus:
    """Tests para buses de señales"""

    def test_bus_creation(self):
        bus = SignalBus(
            bus_type=BusType.STRUCTURAL,
            name="test_structural_bus"
        )
        assert bus.name == "test_structural_bus"
        assert bus.get_subscriber_count() == 0

    def test_bus_registry_creation(self):
        registry = BusRegistry()

        # Debe crear buses por defecto
        assert registry.get_bus("structural_bus") is not None
        assert registry.get_bus("epistemic_bus") is not None
        assert registry.get_bus("universal_bus") is not None

    def test_bus_subscription(self):
        registry = BusRegistry()
        bus = registry.get_bus("structural_bus")

        contract = ConsumptionContract(
            contract_id="CC_SUB_TEST",
            consumer_id="test_consumer",
            consumer_phase="phase_0",
            subscribed_signal_types=["StructuralAlignmentSignal"],
            subscribed_buses=["structural_bus"]
        )

        success = bus.subscribe(contract)
        assert success
        assert bus.get_subscriber_count() == 1

    def test_bus_stats(self):
        bus = SignalBus(bus_type=BusType.STRUCTURAL)
        stats = bus.get_stats()

        assert "total_published" in stats
        assert "total_delivered" in stats
        assert "total_rejected" in stats
        assert "total_errors" in stats
