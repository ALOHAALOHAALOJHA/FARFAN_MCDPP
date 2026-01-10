"""In-memory AtroZ dashboard store.

The AtroZ dashboard needs a complete baseline of 170 PDET municipalities and 16 subregions
even before any analysis runs complete. This store bootstraps reference data from
`pdet_colombia_data` and applies incremental updates via the ingest endpoint.
"""

from __future__ import annotations

import asyncio
import hashlib
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from .api_v1_schemas import (
    ClusterData,
    ComparisonMatrix,
    ConstellationConnection,
    ConstellationData,
    ConstellationNode,
    ConstellationNodePosition,
    ConstellationNodeProperties,
    Coordinates2D,
    DashboardIngestRequest,
    MunicipalAnalysis,
    Municipality,
    MunicipalitySelector,
    PDETRegion,
    PDETRegionScores,
    QuestionAnalysis,
    TimelinePoint,
)
from .api_v1_utils import slugify
from .pdet_colombia_data import PDETSubregion, PDET_MUNICIPALITIES, PDETMunicipality


ExpectedClusterKey = Literal["governance", "social", "economic", "environmental"]


@dataclass(frozen=True, slots=True)
class RegionDefinition:
    id: str
    name: str
    coordinates: Coordinates2D


REGION_DEFINITIONS: dict[PDETSubregion, RegionDefinition] = {
    PDETSubregion.ALTO_PATIA: RegionDefinition(
        id="alto-patia",
        name="Alto Patía y Norte del Cauca",
        coordinates=Coordinates2D(x=25.0, y=20.0),
    ),
    PDETSubregion.ARAUCA: RegionDefinition(
        id="arauca",
        name="Arauca",
        coordinates=Coordinates2D(x=75.0, y=15.0),
    ),
    PDETSubregion.BAJO_CAUCA: RegionDefinition(
        id="bajo-cauca",
        name="Bajo Cauca y Nordeste Antioqueño",
        coordinates=Coordinates2D(x=45.0, y=25.0),
    ),
    PDETSubregion.CATATUMBO: RegionDefinition(
        id="catatumbo",
        name="Catatumbo",
        coordinates=Coordinates2D(x=65.0, y=20.0),
    ),
    PDETSubregion.CHOCO: RegionDefinition(
        id="choco",
        name="Chocó",
        coordinates=Coordinates2D(x=15.0, y=35.0),
    ),
    PDETSubregion.CAGUAN: RegionDefinition(
        id="caguan",
        name="Cuenca del Caguán y Piedemonte Caqueteño",
        coordinates=Coordinates2D(x=55.0, y=40.0),
    ),
    PDETSubregion.MACARENA: RegionDefinition(
        id="macarena",
        name="Macarena-Guaviare",
        coordinates=Coordinates2D(x=60.0, y=55.0),
    ),
    PDETSubregion.MONTES_MARIA: RegionDefinition(
        id="montes-maria",
        name="Montes de María",
        coordinates=Coordinates2D(x=40.0, y=10.0),
    ),
    PDETSubregion.PACIFICO_MEDIO: RegionDefinition(
        id="pacifico-medio",
        name="Pacífico Medio",
        coordinates=Coordinates2D(x=10.0, y=50.0),
    ),
    PDETSubregion.PACIFICO_NARINENSE: RegionDefinition(
        id="pacifico-narinense",
        name="Pacífico y Frontera Nariñense",
        coordinates=Coordinates2D(x=5.0, y=65.0),
    ),
    PDETSubregion.PUTUMAYO: RegionDefinition(
        id="putumayo",
        name="Putumayo",
        coordinates=Coordinates2D(x=35.0, y=70.0),
    ),
    PDETSubregion.SIERRA_NEVADA: RegionDefinition(
        id="sierra-nevada",
        name="Sierra Nevada - Perijá - Zona Bananera",
        coordinates=Coordinates2D(x=70.0, y=5.0),
    ),
    PDETSubregion.SUR_BOLIVAR: RegionDefinition(
        id="sur-bolivar",
        name="Sur de Bolívar",
        coordinates=Coordinates2D(x=50.0, y=15.0),
    ),
    PDETSubregion.SUR_CORDOBA: RegionDefinition(
        id="sur-cordoba",
        name="Sur de Córdoba",
        coordinates=Coordinates2D(x=35.0, y=15.0),
    ),
    PDETSubregion.SUR_TOLIMA: RegionDefinition(
        id="sur-tolima",
        name="Sur del Tolima",
        coordinates=Coordinates2D(x=45.0, y=45.0),
    ),
    PDETSubregion.URABA: RegionDefinition(
        id="uraba",
        name="Urabá Antioqueño",
        coordinates=Coordinates2D(x=20.0, y=10.0),
    ),
}


def municipality_id_for(municipality: PDETMunicipality) -> str:
    return f"{slugify(municipality.name)}-{slugify(municipality.department)}"


def municipality_id_for_parts(name: str, department: str) -> str:
    return f"{slugify(name)}-{slugify(department)}"


def _cluster_key_from_text(value: str) -> ExpectedClusterKey | None:
    slug = slugify(value)
    if "gobern" in slug:
        return "governance"
    if "social" in slug:
        return "social"
    if "econ" in slug:
        return "economic"
    if "ambient" in slug:
        return "environmental"
    return None


def normalize_cluster_key(cluster_id: str, cluster_name: str | None) -> ExpectedClusterKey | None:
    return _cluster_key_from_text(cluster_name or "") or _cluster_key_from_text(cluster_id)


def score_0_to_3_to_percent(score: float) -> float:
    return (score / 3.0) * 100.0


def score_color(score_percent: float | None) -> str:
    if score_percent is None:
        return "#666666"
    if score_percent < 40.0:
        return "#C41E3A"
    if score_percent < 70.0:
        return "#B2642E"
    return "#39FF14"


@dataclass(slots=True)
class MunicipalityState:
    id: str
    name: str
    department: str
    region_id: str
    dane_code: str
    population: int
    latitude: float
    longitude: float
    last_updated: datetime | None = None
    latest_run_id: str | None = None
    overall_score_percent: float | None = None
    cluster_scores_percent: dict[ExpectedClusterKey, float] = field(default_factory=dict)
    question_scores: dict[int, QuestionAnalysis] = field(default_factory=dict)
    radar: dict[str, float] = field(default_factory=dict)

    def to_api(self) -> Municipality:
        analysis: MunicipalAnalysis | None = None
        if self.overall_score_percent is not None:
            analysis = MunicipalAnalysis(
                radar=dict(self.radar),
                clusters=[
                    ClusterData(
                        id=key,
                        score=self.cluster_scores_percent.get(key, 0.0),
                        normalized_score=self.cluster_scores_percent.get(key, 0.0) / 100.0,
                    )
                    for key in ("governance", "social", "economic", "environmental")
                ],
                questions=list(self.question_scores.values()),
                recommendations=[],
            )

        return Municipality(
            id=self.id,
            name=self.name,
            department=self.department,
            regionId=self.region_id,
            population=self.population,
            analysis=analysis,
        )


@dataclass(slots=True)
class RegionState:
    id: str
    name: str
    coordinates: Coordinates2D
    municipality_ids: list[str]
    scores: PDETRegionScores = field(
        default_factory=lambda: PDETRegionScores(
            overall=0.0,
            governance=0.0,
            social=0.0,
            economic=0.0,
            environmental=0.0,
        )
    )

    def to_api(self) -> PDETRegion:
        return PDETRegion(
            id=self.id,
            name=self.name,
            municipalities=len(self.municipality_ids),
            scores=self.scores,
            coordinates=self.coordinates,
        )


class AtrozStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._municipalities: dict[str, MunicipalityState] = {}
        self._regions: dict[str, RegionState] = {}
        self._timeline: dict[str, deque[TimelinePoint]] = {}

        self._bootstrap_reference_data()

    def _bootstrap_reference_data(self) -> None:
        if len(REGION_DEFINITIONS) != 16:
            raise RuntimeError(
                f"PDET subregion definitions mismatch: expected 16, got {len(REGION_DEFINITIONS)}"
            )
        if len(PDET_MUNICIPALITIES) != 170:
            raise RuntimeError(
                f"PDET municipalities mismatch: expected 170, got {len(PDET_MUNICIPALITIES)}"
            )

        by_region: dict[str, list[str]] = {
            definition.id: [] for definition in REGION_DEFINITIONS.values()
        }

        for municipality in PDET_MUNICIPALITIES:
            region_def = REGION_DEFINITIONS.get(municipality.subregion)
            if region_def is None:
                continue
            mun_id = municipality_id_for(municipality)
            state = MunicipalityState(
                id=mun_id,
                name=municipality.name,
                department=municipality.department,
                region_id=region_def.id,
                dane_code=municipality.dane_code,
                population=int(municipality.population or 0),
                latitude=float(municipality.latitude or 0.0),
                longitude=float(municipality.longitude or 0.0),
            )
            self._municipalities[mun_id] = state
            by_region[region_def.id].append(mun_id)

        if len(self._municipalities) != 170:
            raise RuntimeError(
                f"PDET municipality registry mismatch: expected 170, got {len(self._municipalities)}"
            )

        for subregion, definition in REGION_DEFINITIONS.items():
            region_id = definition.id
            municipality_ids = sorted(by_region.get(region_id, []))
            self._regions[region_id] = RegionState(
                id=region_id,
                name=definition.name,
                coordinates=definition.coordinates,
                municipality_ids=municipality_ids,
            )
            self._timeline[region_id] = deque(maxlen=2048)

    async def list_regions(self) -> list[PDETRegion]:
        async with self._lock:
            return [region.to_api() for region in self._regions.values()]

    async def get_region(self, region_id: str) -> PDETRegion | None:
        async with self._lock:
            region = self._regions.get(region_id)
            return None if region is None else region.to_api()

    async def list_region_municipalities(self, region_id: str) -> list[Municipality]:
        async with self._lock:
            region = self._regions.get(region_id)
            if region is None:
                return []
            return [self._municipalities[mun_id].to_api() for mun_id in region.municipality_ids]

    async def get_municipality(self, municipality_id: str) -> Municipality | None:
        async with self._lock:
            state = self._municipalities.get(municipality_id)
            return None if state is None else state.to_api()

    async def get_municipality_analysis(self, municipality_id: str) -> MunicipalAnalysis | None:
        async with self._lock:
            state = self._municipalities.get(municipality_id)
            if state is None:
                return None
            api_obj = state.to_api()
            return api_obj.analysis

    async def get_questions(self, municipality_id: str) -> list[QuestionAnalysis]:
        async with self._lock:
            state = self._municipalities.get(municipality_id)
            if state is None:
                return []
            return list(state.question_scores.values())

    async def get_cluster_analysis(self, region_id: str) -> list[ClusterData]:
        async with self._lock:
            region = self._regions.get(region_id)
            if region is None:
                return []
            totals: dict[ExpectedClusterKey, float] = {
                "governance": 0.0,
                "social": 0.0,
                "economic": 0.0,
                "environmental": 0.0,
            }
            count = 0
            for mun_id in region.municipality_ids:
                mun = self._municipalities[mun_id]
                if mun.overall_score_percent is None:
                    continue
                count += 1
                for key in totals:
                    totals[key] += mun.cluster_scores_percent.get(key, 0.0)

            denom = float(count) if count > 0 else 1.0
            return [
                ClusterData(
                    id=key,
                    score=totals[key] / denom,
                    normalized_score=(totals[key] / denom) / 100.0,
                )
                for key in ("governance", "social", "economic", "environmental")
            ]

    async def get_timeline(self, region_id: str) -> list[TimelinePoint]:
        async with self._lock:
            points = self._timeline.get(region_id)
            if points is None:
                return []
            return list(points)

    async def ingest(self, payload: DashboardIngestRequest) -> dict[str, Any]:
        if payload.municipalities is not None and payload.pdet_regions is not None:
            return await self._ingest_snapshot(payload)
        return await self._ingest_orchestrator_update(payload)

    async def _ingest_snapshot(self, payload: DashboardIngestRequest) -> dict[str, Any]:
        async with self._lock:
            if payload.municipalities is None or payload.pdet_regions is None:
                raise ValueError("Snapshot ingest requires municipalities and pdet_regions")

            incoming_regions = {region.id: region for region in payload.pdet_regions}
            for region_id, region_state in self._regions.items():
                if region_id in incoming_regions:
                    region_state.scores = incoming_regions[region_id].scores

            for municipality in payload.municipalities:
                existing = self._municipalities.get(municipality.id)
                if existing is None:
                    continue
                existing.population = municipality.population
                existing.last_updated = payload.timestamp
                existing.latest_run_id = payload.run_id
                if municipality.analysis and municipality.analysis.clusters:
                    existing.overall_score_percent = municipality.analysis.radar.get("overall")
                existing.radar = dict(municipality.analysis.radar) if municipality.analysis else {}

            return {"status": "success", "mode": "snapshot"}

    def _resolve_municipality_by_dane(self, dane_code: str) -> MunicipalityState | None:
        for state in self._municipalities.values():
            if state.dane_code == dane_code:
                return state
        return None

    def _resolve_municipality_by_name(
        self, name: str, department: str | None
    ) -> MunicipalityState | None:
        if department:
            candidate_id = municipality_id_for_parts(name, department)
            return self._municipalities.get(candidate_id)

        slug_name = slugify(name)
        matches = [
            state for state in self._municipalities.values() if slugify(state.name) == slug_name
        ]
        if len(matches) == 1:
            return matches[0]
        return None

    def _resolve_municipality_from_selector(
        self, selector: MunicipalitySelector | None
    ) -> MunicipalityState | None:
        if selector is None:
            return None
        if selector.id:
            return self._municipalities.get(selector.id)
        if selector.dane_code:
            state = self._resolve_municipality_by_dane(selector.dane_code)
            if state is not None:
                return state
        if selector.name:
            state = self._resolve_municipality_by_name(selector.name, selector.department)
            if state is not None:
                return state
        return None

    async def _ingest_orchestrator_update(self, payload: DashboardIngestRequest) -> dict[str, Any]:
        if payload.macro_result is None:
            raise ValueError("macro_result is required for orchestrator ingest")
        if payload.cluster_scores is None:
            raise ValueError("cluster_scores is required for orchestrator ingest")
        if payload.scored_results is None:
            raise ValueError("scored_results is required for orchestrator ingest")

        async with self._lock:
            municipality = self._resolve_municipality_from_selector(payload.municipality)
            if municipality is None:
                raise ValueError("Unable to resolve municipality for ingest")

            previous_score = municipality.overall_score_percent
            municipality.latest_run_id = payload.run_id
            municipality.last_updated = payload.timestamp

            municipality.overall_score_percent = score_0_to_3_to_percent(
                payload.macro_result.macro_score
            )

            cluster_scores: dict[ExpectedClusterKey, float] = {}
            for cs in payload.cluster_scores:
                key = normalize_cluster_key(cs.cluster_id, cs.cluster_name)
                if key is None:
                    continue
                cluster_scores[key] = score_0_to_3_to_percent(cs.score)

            municipality.cluster_scores_percent = cluster_scores
            municipality.radar = {
                "overall": municipality.overall_score_percent,
                "governance": cluster_scores.get("governance", 0.0),
                "social": cluster_scores.get("social", 0.0),
                "economic": cluster_scores.get("economic", 0.0),
                "environmental": cluster_scores.get("environmental", 0.0),
                "infrastructure": 0.0,
                "security": 0.0,
            }

            municipality.question_scores = {}
            for entry in payload.scored_results:
                score_value = entry.normalized_score
                if score_value is None and entry.score is not None:
                    score_value = entry.score / 3.0
                if score_value is None:
                    continue
                municipality.question_scores[entry.question_global] = QuestionAnalysis(
                    questionId=entry.question_global,
                    score=float(score_value) * 100.0,
                    evidence=[],
                    quality=_quality_map(entry.quality_level),
                )

            self._recompute_region_scores_locked(municipality.region_id)
            self._append_timeline_locked(municipality.region_id, payload.timestamp)

            score_delta = (
                None
                if previous_score is None
                else municipality.overall_score_percent - previous_score
            )

            return {
                "status": "success",
                "mode": "orchestrator",
                "municipality_id": municipality.id,
                "region_id": municipality.region_id,
                "score_change": {
                    "old": previous_score,
                    "new": municipality.overall_score_percent,
                    "delta": score_delta,
                },
            }

    def _recompute_region_scores_locked(self, region_id: str) -> None:
        region = self._regions.get(region_id)
        if region is None:
            return

        totals: dict[ExpectedClusterKey, float] = {
            "governance": 0.0,
            "social": 0.0,
            "economic": 0.0,
            "environmental": 0.0,
        }
        overall_total = 0.0
        counted = 0

        for mun_id in region.municipality_ids:
            mun = self._municipalities[mun_id]
            if mun.overall_score_percent is None:
                continue
            counted += 1
            overall_total += mun.overall_score_percent
            for key in totals:
                totals[key] += mun.cluster_scores_percent.get(key, 0.0)

        denom = float(counted) if counted > 0 else 1.0
        region.scores = PDETRegionScores(
            overall=overall_total / denom,
            governance=totals["governance"] / denom,
            social=totals["social"] / denom,
            economic=totals["economic"] / denom,
            environmental=totals["environmental"] / denom,
        )

    def _append_timeline_locked(self, region_id: str, timestamp: datetime) -> None:
        points = self._timeline.get(region_id)
        region = self._regions.get(region_id)
        if points is None or region is None:
            return

        points.append(
            TimelinePoint(
                timestamp=timestamp.astimezone(timezone.utc).isoformat(),
                scores={
                    "overall": region.scores.overall,
                    "governance": region.scores.governance,
                    "social": region.scores.social,
                    "economic": region.scores.economic,
                    "environmental": region.scores.environmental,
                },
                events=["data.ingest"],
            )
        )

    async def build_constellation(self) -> ConstellationData:
        async with self._lock:
            nodes: list[ConstellationNode] = []
            connections: list[ConstellationConnection] = []

            for region in self._regions.values():
                nodes.append(
                    ConstellationNode(
                        id=region.id,
                        position=ConstellationNodePosition(
                            x=region.coordinates.x, y=region.coordinates.y
                        ),
                        properties=ConstellationNodeProperties(
                            size=180.0,
                            color="#00D4FF",
                            pulseRate=0.5,
                            connectionStrength=1.0,
                        ),
                    )
                )

            min_pop = min((m.population for m in self._municipalities.values()), default=0)
            max_pop = max((m.population for m in self._municipalities.values()), default=1)
            pop_span = max(max_pop - min_pop, 1)

            for municipality in self._municipalities.values():
                base = self._regions.get(municipality.region_id)
                if base is None:
                    continue
                jitter_x, jitter_y = _stable_jitter(municipality.id)
                x = base.coordinates.x + jitter_x
                y = base.coordinates.y + jitter_y

                size = 80.0 + 70.0 * ((municipality.population - min_pop) / pop_span)
                color = score_color(municipality.overall_score_percent)

                nodes.append(
                    ConstellationNode(
                        id=municipality.id,
                        position=ConstellationNodePosition(x=x, y=y),
                        properties=ConstellationNodeProperties(
                            size=size,
                            color=color,
                            pulseRate=0.5 + (municipality.overall_score_percent or 0.0) / 200.0,
                            connectionStrength=(municipality.overall_score_percent or 0.0) / 100.0,
                        ),
                    )
                )

                connections.append(
                    ConstellationConnection(
                        source=municipality.region_id,
                        target=municipality.id,
                        strength=1.0,
                        type="pdet_region",
                    )
                )

            _add_similarity_connections(nodes, connections, self._municipalities)

            return ConstellationData(nodes=nodes, connections=connections)

    async def compare(
        self,
        entity_type: Literal["region", "municipality"],
        ids: list[str],
        metrics: list[str],
    ) -> ComparisonMatrix:
        async with self._lock:
            matrix: dict[str, dict[str, float]] = {}
            if entity_type == "region":
                for region_id in ids:
                    region = self._regions.get(region_id)
                    if region is None:
                        continue
                    matrix[region_id] = _extract_metrics(region.scores, metrics)
            else:
                for mun_id in ids:
                    mun = self._municipalities.get(mun_id)
                    if mun is None:
                        continue
                    matrix[mun_id] = _extract_metrics_from_municipality(mun, metrics)

            return ComparisonMatrix(entityType=entity_type, ids=ids, metrics=metrics, matrix=matrix)


def _quality_map(value: str | None) -> str:
    if value is None:
        return "NO_APLICABLE"
    slug = slugify(value)
    if "excel" in slug or slug in {"alta", "high"}:
        return "EXCELENTE"
    if "acept" in slug or slug in {"media", "medium"}:
        return "ACEPTABLE"
    if "insuf" in slug or slug in {"baja", "low"}:
        return "INSUFICIENTE"
    return "ERROR"


def _stable_jitter(identifier: str) -> tuple[float, float]:
    digest = hashlib.sha256(identifier.encode("utf-8")).digest()
    x_raw = int.from_bytes(digest[:2], "big") / 65535.0
    y_raw = int.from_bytes(digest[2:4], "big") / 65535.0
    return (x_raw - 0.5) * 8.0, (y_raw - 0.5) * 8.0


def _add_similarity_connections(
    nodes: list[ConstellationNode],
    connections: list[ConstellationConnection],
    municipalities: dict[str, MunicipalityState],
) -> None:
    scored = [m for m in municipalities.values() if m.overall_score_percent is not None]
    scored.sort(key=lambda m: m.overall_score_percent or 0.0)

    for i, mun in enumerate(scored):
        for j in (i - 1, i + 1):
            if j < 0 or j >= len(scored):
                continue
            other = scored[j]
            diff = abs((mun.overall_score_percent or 0.0) - (other.overall_score_percent or 0.0))
            if diff > 5.0:
                continue
            strength = max(0.1, 1.0 - (diff / 5.0))
            connections.append(
                ConstellationConnection(
                    source=mun.id,
                    target=other.id,
                    strength=strength,
                    type="score_similarity",
                )
            )


def _extract_metrics(scores: PDETRegionScores, metrics: list[str]) -> dict[str, float]:
    if not metrics:
        return {
            "overall": scores.overall,
            "governance": scores.governance,
            "social": scores.social,
            "economic": scores.economic,
            "environmental": scores.environmental,
        }
    out: dict[str, float] = {}
    for metric in metrics:
        if hasattr(scores, metric):
            out[metric] = float(getattr(scores, metric))
    return out


def _extract_metrics_from_municipality(
    mun: MunicipalityState, metrics: list[str]
) -> dict[str, float]:
    if not metrics:
        return dict(mun.radar)
    out: dict[str, float] = {}
    for metric in metrics:
        value = mun.radar.get(metric)
        if value is not None:
            out[metric] = float(value)
    return out
