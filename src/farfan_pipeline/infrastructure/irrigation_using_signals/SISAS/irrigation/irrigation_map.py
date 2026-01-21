# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/irrigation/irrigation_map.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class IrrigabilityStatus(Enum):
    """Estados de irrigabilidad"""
    IRRIGABLE_NOW = "irrigable_now"
    NOT_IRRIGABLE_YET = "not_irrigable_yet"
    DEFINITELY_NOT = "definitely_not"


class ItemCategory(str, Enum):
    """Categorías de ítems irrigables"""
    QUESTION = "question"
    POLICY_AREA = "policy_area"
    DIMENSION = "dimension"
    CLUSTER = "cluster"
    CROSS_CUTTING = "cross_cutting"
    MESO = "meso"
    MACRO = "macro"
    PATTERN = "pattern"


# Expected item counts for validation (476 total)
EXPECTED_QUESTIONS = 300
EXPECTED_POLICY_AREAS = 10
EXPECTED_DIMENSIONS = 6
EXPECTED_CLUSTERS = 4
EXPECTED_CROSS_CUTTING = 9
EXPECTED_MESO = 4
EXPECTED_MACRO = 1
EXPECTED_PATTERNS = 142
EXPECTED_TOTAL_ITEMS = 476


@dataclass
class IrrigationStatistics:
    """Estadísticas de irrigación con desglose por categoría"""
    total_items: int = 0
    questions: int = 0
    policy_areas: int = 0
    dimensions: int = 0
    clusters: int = 0
    cross_cutting: int = 0
    meso: int = 0
    macro: int = 0
    patterns: int = 0
    irrigable_now: int = 0
    not_yet: int = 0
    definitely_not: int = 0

    def is_valid(self) -> bool:
        """Valida contra conteos esperados"""
        return (
            self.total_items == EXPECTED_TOTAL_ITEMS and
            self.questions == EXPECTED_QUESTIONS and
            self.policy_areas == EXPECTED_POLICY_AREAS and
            self.dimensions == EXPECTED_DIMENSIONS and
            self.clusters == EXPECTED_CLUSTERS and
            self.cross_cutting == EXPECTED_CROSS_CUTTING and
            self.meso == EXPECTED_MESO and
            self.macro == EXPECTED_MACRO and
            self.patterns == EXPECTED_PATTERNS
        )

    def get_discrepancies(self) -> Dict[str, tuple[int, int]]:
        """Retorna discrepancias (actual, expected)"""
        discrepancies = {}
        checks = [
            ("total_items", self.total_items, EXPECTED_TOTAL_ITEMS),
            ("questions", self.questions, EXPECTED_QUESTIONS),
            ("policy_areas", self.policy_areas, EXPECTED_POLICY_AREAS),
            ("dimensions", self.dimensions, EXPECTED_DIMENSIONS),
            ("clusters", self.clusters, EXPECTED_CLUSTERS),
            ("cross_cutting", self.cross_cutting, EXPECTED_CROSS_CUTTING),
            ("meso", self.meso, EXPECTED_MESO),
            ("macro", self.macro, EXPECTED_MACRO),
            ("patterns", self.patterns, EXPECTED_PATTERNS),
        ]
        for name, actual, expected in checks:
            if actual != expected:
                discrepancies[name] = (actual, expected)
        return discrepancies


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

    @classmethod
    def from_specification(cls, spec_data: Dict[str, Any]) -> tuple['IrrigationMap', IrrigationStatistics]:
        """
        Construye el mapa desde la especificación del cuestionario canónico.

        Espera estructura:
        {
            "questions": [...],  # 300 preguntas
            "policy_areas": [...],  # 10 PA
            "dimensions": [...],  # 6 DIM
            "clusters": [...],  # 4 CL
            "cross_cutting": [...],  # 9 CC
            "meso": [...],  # 4 MESO
            "macro": [...],  # 1 MACRO
            "patterns": [...]  # 142 patterns
        }

        Returns:
            (IrrigationMap, IrrigationStatistics) - El mapa y las estadísticas
        """
        irrigation_map = cls()
        stats = IrrigationStatistics()

        # Mapeo de categoría a ItemCategory
        category_map = {
            "questions": ItemCategory.QUESTION,
            "policy_areas": ItemCategory.POLICY_AREA,
            "dimensions": ItemCategory.DIMENSION,
            "clusters": ItemCategory.CLUSTER,
            "cross_cutting": ItemCategory.CROSS_CUTTING,
            "meso": ItemCategory.MESO,
            "macro": ItemCategory.MACRO,
            "patterns": ItemCategory.PATTERN,
        }

        # Procesar cada categoría
        for category_key, item_category in category_map.items():
            items = spec_data.get(category_key, [])

            for item in items:
                # Crear source
                source = IrrigationSource(
                    file_path=item.get("file_path", ""),
                    stage=item.get("stage", "Canonical"),
                    phase=item.get("phase", "phase_1"),
                    vehicles=item.get("vehicles", []),
                    consumers=item.get("consumers", []),
                    irrigability=IrrigabilityStatus.IRRIGABLE_NOW,
                    gaps=[],
                    added_value="CORE",
                    file_bytes=item.get("file_bytes", 0)
                )

                # Crear targets
                targets = []
                for consumer in source.consumers:
                    targets.append(IrrigationTarget(
                        consumer_id=consumer,
                        consumer_phase=source.phase
                    ))

                # Crear ruta
                route = IrrigationRoute(
                    source=source,
                    vehicles=source.vehicles,
                    signals_generated=[],
                    targets=targets,
                    is_active=True
                )

                irrigation_map.add_route(route)

                # Actualizar estadísticas
                stats.total_items += 1
                stats.irrigable_now += 1

                # Incrementar contador de categoría
                if item_category == ItemCategory.QUESTION:
                    stats.questions += 1
                elif item_category == ItemCategory.POLICY_AREA:
                    stats.policy_areas += 1
                elif item_category == ItemCategory.DIMENSION:
                    stats.dimensions += 1
                elif item_category == ItemCategory.CLUSTER:
                    stats.clusters += 1
                elif item_category == ItemCategory.CROSS_CUTTING:
                    stats.cross_cutting += 1
                elif item_category == ItemCategory.MESO:
                    stats.meso += 1
                elif item_category == ItemCategory.MACRO:
                    stats.macro += 1
                elif item_category == ItemCategory.PATTERN:
                    stats.patterns += 1

        return irrigation_map, stats

    def validate_counts(self) -> tuple[bool, IrrigationStatistics]:
        """
        Valida los conteos de ítems contra los esperados.

        Returns:
            (is_valid, statistics)
        """
        stats = IrrigationStatistics()

        # Contar por categoría inferida del file_path
        for route in self.routes.values():
            file_path = route.source.file_path.lower()
            stats.total_items += 1

            if route.source.irrigability == IrrigabilityStatus.IRRIGABLE_NOW:
                stats.irrigable_now += 1
            elif route.source.irrigability == IrrigabilityStatus.NOT_IRRIGABLE_YET:
                stats.not_yet += 1
            else:
                stats.definitely_not += 1

            # Inferir categoría
            if "question" in file_path or "/q" in file_path:
                stats.questions += 1
            elif "policy_area" in file_path or "/pa" in file_path:
                stats.policy_areas += 1
            elif "dimension" in file_path or "/dim" in file_path:
                stats.dimensions += 1
            elif "cluster" in file_path or "/cl" in file_path:
                stats.clusters += 1
            elif "cross_cutting" in file_path or "/cc" in file_path:
                stats.cross_cutting += 1
            elif "meso" in file_path:
                stats.meso += 1
            elif "macro" in file_path:
                stats.macro += 1
            elif "pattern" in file_path:
                stats.patterns += 1

        return stats.is_valid(), stats
