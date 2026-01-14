# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/irrigation/irrigation_map.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class IrrigabilityStatus(Enum):
    """Estados de irrigabilidad"""
    IRRIGABLE_NOW = "irrigable_now"
    NOT_IRRIGABLE_YET = "not_irrigable_yet"
    DEFINITELY_NOT = "definitely_not"


@dataclass
class IrrigationTarget:
    """Destino de irrigación"""
    consumer_id: str
    consumer_phase: str
    required_signals: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)


@dataclass
class IrrigationSource:
    """Fuente de irrigación"""
    file_path: str
    stage: str
    phase: str
    vehicles: List[str] = field(default_factory=list)
    consumers: List[str] = field(default_factory=list)
    irrigability:  IrrigabilityStatus = IrrigabilityStatus.DEFINITELY_NOT
    gaps: List[str] = field(default_factory=list)
    added_value: str = "MARGINAL"
    file_bytes: int = 0


@dataclass
class IrrigationRoute:
    """Ruta completa de irrigación:  archivo → vehículos → señales → consumidores"""
    source: IrrigationSource
    vehicles: List[str] = field(default_factory=list)
    signals_generated: List[str] = field(default_factory=list)
    targets: List[IrrigationTarget] = field(default_factory=list)
    is_active: bool = False


@dataclass
class IrrigationMap:
    """
    Mapa completo de irrigación del sistema.
    Define quién produce qué, para quién, a través de qué vehículos.
    """

    routes: Dict[str, IrrigationRoute] = field(default_factory=dict)

    # Índices para búsqueda rápida
    _by_phase: Dict[str, List[str]] = field(default_factory=dict)
    _by_vehicle: Dict[str, List[str]] = field(default_factory=dict)
    _by_consumer: Dict[str, List[str]] = field(default_factory=dict)
    _by_irrigability: Dict[str, List[str]] = field(default_factory=dict)

    def add_route(self, route:  IrrigationRoute):
        """Añade una ruta al mapa"""
        route_id = route.source.file_path
        self.routes[route_id] = route

        # Indexar por fase
        phase = route.source.phase
        if phase not in self._by_phase:
            self._by_phase[phase] = []
        self._by_phase[phase].append(route_id)

        # Indexar por vehículo
        for vehicle in route.vehicles:
            if vehicle not in self._by_vehicle:
                self._by_vehicle[vehicle] = []
            self._by_vehicle[vehicle].append(route_id)

        # Indexar por consumidor
        for target in route.targets:
            if target.consumer_id not in self._by_consumer:
                self._by_consumer[target.consumer_id] = []
            self._by_consumer[target.consumer_id].append(route_id)

        # Indexar por irrigabilidad
        status = route.source.irrigability.value
        if status not in self._by_irrigability:
            self._by_irrigability[status] = []
        self._by_irrigability[status].append(route_id)

    def get_routes_for_phase(self, phase: str) -> List[IrrigationRoute]:
        """Obtiene rutas por fase"""
        route_ids = self._by_phase.get(phase, [])
        return [self.routes[rid] for rid in route_ids]

    def get_routes_for_vehicle(self, vehicle: str) -> List[IrrigationRoute]:
        """Obtiene rutas que usan un vehículo específico"""
        route_ids = self._by_vehicle.get(vehicle, [])
        return [self.routes[rid] for rid in route_ids]

    def get_routes_for_consumer(self, consumer:  str) -> List[IrrigationRoute]:
        """Obtiene rutas que alimentan a un consumidor"""
        route_ids = self._by_consumer.get(consumer, [])
        return [self.routes[rid] for rid in route_ids]

    def get_irrigable_now(self) -> List[IrrigationRoute]:
        """Obtiene rutas que pueden irrigar ahora"""
        route_ids = self._by_irrigability.get("irrigable_now", [])
        return [self.routes[rid] for rid in route_ids]

    def get_blocked_routes(self) -> List[tuple[IrrigationRoute, List[str]]]:
        """Obtiene rutas bloqueadas con sus gaps"""
        blocked = []
        for status in ["not_irrigable_yet", "definitely_not"]:
            route_ids = self._by_irrigability.get(status, [])
            for rid in route_ids:
                route = self.routes[rid]
                blocked.append((route, route.source.gaps))
        return blocked

    def get_statistics(self) -> Dict[str, Any]:
        """Estadísticas del mapa de irrigación"""
        total = len(self.routes)
        irrigable = len(self._by_irrigability. get("irrigable_now", []))
        not_yet = len(self._by_irrigability.get("not_irrigable_yet", []))
        definitely_not = len(self._by_irrigability.get("definitely_not", []))

        # Contar gaps
        all_gaps = []
        for route in self.routes.values():
            all_gaps.extend(route.source.gaps)

        gap_counts = {}
        for gap in all_gaps:
            gap_counts[gap] = gap_counts.get(gap, 0) + 1

        return {
            "total_routes": total,
            "irrigable_now": irrigable,
            "not_irrigable_yet":  not_yet,
            "definitely_not": definitely_not,
            "irrigable_percentage": (irrigable / total * 100) if total > 0 else 0,
            "phases":  list(self._by_phase.keys()),
            "vehicles_in_use": list(self._by_vehicle.keys()),
            "consumers_registered": list(self._by_consumer.keys()),
            "gap_summary": gap_counts
        }

    @classmethod
    def from_sabana_csv(cls, csv_data: List[Dict[str, Any]]) -> 'IrrigationMap':
        """
        Construye el mapa desde el CSV de decisiones (sabana_final_decisiones.csv)
        """
        irrigation_map = cls()

        for row in csv_data:
            # Filtrar solo items del canonic central (no MARGINAL, no External)
            if row.get("added_value") == "MARGINAL":
                continue
            if row.get("stage") == "External":
                continue

            # Crear source
            source = IrrigationSource(
                file_path=row.get("json_file_path", ""),
                stage=row.get("stage", ""),
                phase=row.get("phase", ""),
                vehicles=cls._parse_list(row.get("vehiculos_str", "NINGUNO")),
                consumers=cls._parse_list(row.get("consumidores_str", "NINGUNO")),
                irrigability=cls._parse_irrigability(row.get("irrigability_bucket", "")),
                gaps=cls._parse_list(row.get("gaps_str", "NINGUNO")),
                added_value=row.get("added_value", ""),
                file_bytes=int(row.get("file_bytes", 0) or 0)
            )

            # Crear targets
            targets = []
            for consumer in source.consumers:
                if consumer != "NINGUNO":
                    targets.append(IrrigationTarget(
                        consumer_id=consumer,
                        consumer_phase=source.phase
                    ))

            # Crear ruta
            route = IrrigationRoute(
                source=source,
                vehicles=[v for v in source.vehicles if v != "NINGUNO"],
                signals_generated=[],  # Se llenará al procesar
                targets=targets,
                is_active=source.irrigability == IrrigabilityStatus.IRRIGABLE_NOW
            )

            irrigation_map.add_route(route)

        return irrigation_map

    @staticmethod
    def _parse_list(value: str) -> List[str]:
        """Parsea lista separada por comas"""
        if not value or value == "NINGUNO":
            return []
        return [v.strip() for v in value.split(",") if v.strip()]

    @staticmethod
    def _parse_irrigability(value: str) -> IrrigabilityStatus:
        """Parsea estado de irrigabilidad"""
        mapping = {
            "irrigable_now": IrrigabilityStatus.IRRIGABLE_NOW,
            "not_irrigable_yet": IrrigabilityStatus.NOT_IRRIGABLE_YET,
            "definitely_not":  IrrigabilityStatus.DEFINITELY_NOT
        }
        return mapping.get(value, IrrigabilityStatus.DEFINITELY_NOT)
