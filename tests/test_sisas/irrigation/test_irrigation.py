# tests/test_sisas/irrigation/test_irrigation.py

import pytest
import json
import tempfile
from pathlib import Path

from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_map import (
    IrrigationMap, IrrigationRoute, IrrigationSource, IrrigationTarget,
    IrrigabilityStatus
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.irrigation.irrigation_executor import (
    IrrigationExecutor, IrrigationResult
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_registry import (
    SignalRegistryVehicle
)
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.bus import BusRegistry
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.contracts import ContractRegistry
from src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.event import EventStore


class TestIrrigationMap:
    """Tests para el mapa de irrigación"""

    def test_create_route(self):
        source = IrrigationSource(
            file_path="clusters/CL01/metadata.json",
            stage="phase_0",
            phase="Phase_0",
            vehicles=["signal_registry"],
            consumers=["phase0_bootstrap.py"],
            irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
            gaps=[],
            added_value="YES",
            file_bytes=5000
        )

        route = IrrigationRoute(
            source=source,
            vehicles=["signal_registry"],
            targets=[IrrigationTarget(
                consumer_id="phase0_bootstrap.py",
                consumer_phase="phase_0"
            )],
            is_active=True
        )

        assert route.source.irrigability == IrrigabilityStatus.IRRIGABLE_NOW
        assert route.is_active

    def test_add_route_to_map(self):
        irrigation_map = IrrigationMap()

        source = IrrigationSource(
            file_path="test/test.json",
            stage="phase_0",
            phase="Phase_0",
            vehicles=["signal_registry"],
            consumers=["consumer1"],
            irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
            gaps=[]
        )

        route = IrrigationRoute(
            source=source,
            vehicles=["signal_registry"],
            targets=[IrrigationTarget(consumer_id="consumer1", consumer_phase="phase_0")],
            is_active=True
        )

        irrigation_map.add_route(route)

        assert len(irrigation_map.routes) == 1
        assert irrigation_map.get_irrigable_now()[0] == route

    def test_get_routes_by_phase(self):
        irrigation_map = IrrigationMap()

        # Agregar rutas de diferentes fases
        for phase in ["Phase_0", "Phase_1", "Phase_0"]:
            source = IrrigationSource(
                file_path=f"test/{phase}/file.json",
                stage=phase.lower(),
                phase=phase,
                vehicles=["signal_registry"],
                consumers=[],
                irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
                gaps=[]
            )
            route = IrrigationRoute(source=source, vehicles=["signal_registry"])
            irrigation_map.add_route(route)

        phase0_routes = irrigation_map.get_routes_for_phase("Phase_0")
        assert len(phase0_routes) == 2

    def test_get_blocked_routes(self):
        irrigation_map = IrrigationMap()

        # Ruta bloqueada
        source1 = IrrigationSource(
            file_path="blocked/file.json",
            stage="phase_0",
            phase="Phase_0",
            vehicles=[],  # Sin vehículo
            consumers=[],
            irrigability=IrrigabilityStatus.NOT_IRRIGABLE_YET,
            gaps=["NECESITA_VEHICULO", "NECESITA_CONSUMIDOR"]
        )
        route1 = IrrigationRoute(source=source1)
        irrigation_map.add_route(route1)

        # Ruta no bloqueada
        source2 = IrrigationSource(
            file_path="ok/file.json",
            stage="phase_0",
            phase="Phase_0",
            vehicles=["signal_registry"],
            consumers=["consumer1"],
            irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
            gaps=[]
        )
        route2 = IrrigationRoute(source=source2, vehicles=["signal_registry"])
        irrigation_map.add_route(route2)

        blocked = irrigation_map.get_blocked_routes()
        assert len(blocked) == 1
        assert "NECESITA_VEHICULO" in blocked[0][1]

    def test_statistics(self):
        irrigation_map = IrrigationMap()

        # Agregar varias rutas
        statuses = [
            IrrigabilityStatus.IRRIGABLE_NOW,
            IrrigabilityStatus.IRRIGABLE_NOW,
            IrrigabilityStatus.NOT_IRRIGABLE_YET,
            IrrigabilityStatus.DEFINITELY_NOT
        ]

        for i, status in enumerate(statuses):
            source = IrrigationSource(
                file_path=f"test/file_{i}.json",
                stage="phase_0",
                phase="Phase_0",
                vehicles=["v1"] if status == IrrigabilityStatus.IRRIGABLE_NOW else [],
                consumers=[],
                irrigability=status,
                gaps=[] if status == IrrigabilityStatus.IRRIGABLE_NOW else ["GAP"]
            )
            route = IrrigationRoute(source=source)
            irrigation_map.add_route(route)

        stats = irrigation_map.get_statistics()
        assert stats["total_routes"] == 4
        assert stats["irrigable_now"] == 2
        assert stats["not_irrigable_yet"] == 1
        assert stats["definitely_not"] == 1


class TestIrrigationExecutor:
    """Tests para el ejecutor de irrigación"""

    @pytest.fixture
    def executor(self):
        bus_registry = BusRegistry()
        contract_registry = ContractRegistry()
        event_store = EventStore()

        executor = IrrigationExecutor(
            bus_registry=bus_registry,
            contract_registry=contract_registry,
            event_store=event_store
        )

        # Registrar vehículo
        vehicle = SignalRegistryVehicle(
            bus_registry=bus_registry,
            contract_registry=contract_registry,
            event_store=event_store
        )
        executor.register_vehicle(vehicle)

        return executor

    @pytest.fixture
    def temp_canonical_file(self):
        """Crea archivo canónico temporal para tests"""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        ) as f:
            json.dump({
                "id": "TEST_001",
                "name": "Test File",
                "description": "Test canonical file",
                "version": "1.0.0",
                "questions": []
            }, f)
            return f.name

    def test_register_vehicle(self, executor):
        assert "signal_registry" in executor.vehicles

    def test_execute_route_success(self, executor, temp_canonical_file):
        source = IrrigationSource(
            file_path=temp_canonical_file,
            stage="phase_0",
            phase="Phase_0",
            vehicles=["signal_registry"],
            consumers=["test_consumer"],
            irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
            gaps=[]
        )

        route = IrrigationRoute(
            source=source,
            vehicles=["signal_registry"],
            targets=[IrrigationTarget(
                consumer_id="test_consumer",
                consumer_phase="phase_0"
            )],
            is_active=True
        )

        result = executor.execute_route(route)

        # Nota: execute_route en mi implementacion devuelve success=True aunque no haya contratos de publicacion,
        # pero registra errores si falla algo critico.
        # Sin embargo, SignalRegistryVehicle intenta publicar si tiene contrato.
        # En el test no le hemos seteado contrato al vehiculo.
        # create_signal_source etc dependen de que el vehiculo tenga dependencias seteadas por register_vehicle (lo tiene).

        # El vehiculo intenta publicar:
        # success, msg = vehicle.publish_signal(signal)
        # publish_signal chequea self.publication_contract. Si es None, retorna False.
        # Pero el metodo execute_route captura errores de excepcion. publish_signal no lanza excepcion, retorna False.
        # execute_route sigue.

        assert result.success
        assert len(result.signals_generated) > 0
        assert "test_consumer" in result.consumers_notified

    def test_execute_route_blocked(self, executor):
        source = IrrigationSource(
            file_path="nonexistent/file.json",
            stage="phase_0",
            phase="Phase_0",
            vehicles=[],  # Sin vehículo
            consumers=[],
            irrigability=IrrigabilityStatus.NOT_IRRIGABLE_YET,
            gaps=["NECESITA_VEHICULO"]
        )

        route = IrrigationRoute(source=source)

        result = executor.execute_route(route)

        assert not result.success
        assert len(result.errors) > 0

    def test_execution_summary(self, executor, temp_canonical_file):
        # Ejecutar algunas rutas
        for i in range(3):
            source = IrrigationSource(
                file_path=temp_canonical_file,
                stage="phase_0",
                phase="Phase_0",
                vehicles=["signal_registry"],
                consumers=["consumer"],
                irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
                gaps=[]
            )
            route = IrrigationRoute(
                source=source,
                vehicles=["signal_registry"],
                targets=[IrrigationTarget(consumer_id="consumer", consumer_phase="phase_0")]
            )
            executor.execute_route(route)

        summary = executor.get_execution_summary()

        assert summary["total_executions"] == 3
        assert summary["successful"] == 3
        assert summary["failed"] == 0
        assert summary["total_signals_generated"] > 0
