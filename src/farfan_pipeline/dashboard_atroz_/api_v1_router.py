"""AtroZ Dashboard API v1 routes."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog
from fastapi import (
    APIRouter,
    Body,
    Depends,
    Query,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from .api_v1_errors import AtrozAPIException, api_error_response
from .api_v1_schemas import (
    APIError,
    ClusterData,
    ComparisonMatrix,
    ComparisonMatrixRequest,
    ConstellationData,
    DashboardIngestRequest,
    ExportRequest,
    MunicipalAnalysis,
    Municipality,
    PDETRegion,
    QuestionAnalysis,
    TimelinePoint,
)
from .api_v1_store import AtrozStore

logger = structlog.get_logger(__name__)


class WebSocketHub:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast_json(self, payload: dict[str, Any]) -> None:
        async with self._lock:
            targets = list(self._connections)

        for ws in targets:
            try:
                await ws.send_json(payload)
            except Exception:
                await self.disconnect(ws)


class SSEHub:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[dict[str, str]] = asyncio.Queue()

    async def publish(self, event: str, data: dict[str, Any]) -> None:
        await self._queue.put({"event": event, "data": json.dumps(data, ensure_ascii=False)})

    async def events(self, request: Request) -> Any:
        while True:
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=30.0)
                yield event
            except TimeoutError:
                yield {
                    "event": "heartbeat",
                    "data": json.dumps({"timestamp": datetime.now(UTC).isoformat()}),
                }


STORE = AtrozStore()
WS_HUB = WebSocketHub()
SSE_HUB = SSEHub()

router = APIRouter(prefix="/api/v1", tags=["atroz-dashboard"])


def _api_error(
    status: int, code: str, message: str, details: dict[str, Any] | None = None
) -> JSONResponse:
    payload = APIError(status=status, code=code, message=message, details=details).model_dump(
        mode="json"
    )
    return JSONResponse(status_code=status, content=payload)


def _require_headers(request: Request) -> None:
    client = request.headers.get("X-Atroz-Client")
    version = request.headers.get("X-Atroz-Version")
    request_id = request.headers.get("X-Request-ID")

    if not client or not version or not request_id:
        raise AtrozAPIException(status=400, code="BAD_REQUEST", message="Missing required headers")

    if client != "dashboard-v1":
        raise AtrozAPIException(status=400, code="BAD_REQUEST", message="Invalid X-Atroz-Client")

    try:
        UUID(request_id)
    except ValueError as exc:
        raise AtrozAPIException(
            status=400, code="BAD_REQUEST", message="Invalid X-Request-ID"
        ) from exc

    if os.getenv("ATROZ_AUTH_REQUIRED", "false").lower() == "true":
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or len(auth) < 16:
            raise AtrozAPIException(
                status=401, code="UNAUTHORIZED", message="Missing/invalid Authorization"
            )


async def require_atroz_headers(request: Request) -> None:
    _require_headers(request)


@router.post("/data/ingest")
async def ingest_data(
    payload: DashboardIngestRequest = Body(...),
    _: None = Depends(require_atroz_headers),
) -> Response:
    try:
        result = await STORE.ingest(payload)
    except ValueError as exc:
        return _api_error(400, "BAD_REQUEST", str(exc))
    except AtrozAPIException as exc:
        return api_error_response(exc)
    except Exception as exc:
        logger.exception("atroz_ingest_error", error=str(exc))
        return _api_error(500, "SERVER_ERROR", "Failed to ingest data")

    if result.get("mode") == "orchestrator":
        municipality_id = str(result.get("municipality_id", ""))
        region_id = str(result.get("region_id", ""))
        region = await STORE.get_region(region_id)
        municipality = await STORE.get_municipality(municipality_id)

        if region is not None:
            await WS_HUB.broadcast_json(
                {
                    "event": "DATA_UPDATED",
                    "type": "region",
                    "id": region_id,
                    "data": region.model_dump(mode="json"),
                    "timestamp": payload.timestamp.astimezone(UTC).isoformat(),
                }
            )

        if municipality is not None:
            score_change = result.get("score_change") or {}
            await WS_HUB.broadcast_json(
                {
                    "event": "SCORE_CHANGED",
                    "entity": "municipality",
                    "id": municipality_id,
                    "newScore": score_change.get("new"),
                    "oldScore": score_change.get("old"),
                    "delta": score_change.get("delta"),
                }
            )

        await SSE_HUB.publish(
            "data.refresh",
            {
                "municipalityId": municipality_id,
                "regionId": region_id,
                "runId": payload.run_id,
                "timestamp": payload.timestamp.astimezone(UTC).isoformat(),
            },
        )

    return JSONResponse(status_code=200, content=result)


@router.get("/pdet/regions", response_model=list[PDETRegion])
async def list_regions(
    response: Response, _: None = Depends(require_atroz_headers)
) -> list[PDETRegion]:
    response.headers["Cache-Control"] = "max-age=300"
    return await STORE.list_regions()


@router.get("/pdet/regions/{region_id}", response_model=PDETRegion)
async def get_region(
    region_id: str, response: Response, _: None = Depends(require_atroz_headers)
) -> Response:
    region = await STORE.get_region(region_id)
    if region is None:
        return _api_error(404, "NOT_FOUND", f"Region '{region_id}' not found")
    response.headers["Cache-Control"] = "max-age=300"
    return JSONResponse(status_code=200, content=region.model_dump(mode="json"))


@router.get("/pdet/regions/{region_id}/municipalities", response_model=list[Municipality])
async def list_region_municipalities(
    region_id: str, response: Response, _: None = Depends(require_atroz_headers)
) -> list[Municipality]:
    response.headers["Cache-Control"] = "max-age=600"
    return await STORE.list_region_municipalities(region_id)


@router.get("/municipalities/{municipality_id}", response_model=Municipality)
async def get_municipality(
    municipality_id: str, response: Response, _: None = Depends(require_atroz_headers)
) -> Response:
    municipality = await STORE.get_municipality(municipality_id)
    if municipality is None:
        return _api_error(404, "NOT_FOUND", f"Municipality '{municipality_id}' not found")
    response.headers["Cache-Control"] = "max-age=600"
    return JSONResponse(status_code=200, content=municipality.model_dump(mode="json"))


@router.get("/municipalities/{municipality_id}/analysis", response_model=MunicipalAnalysis)
async def get_municipality_analysis(
    municipality_id: str, response: Response, _: None = Depends(require_atroz_headers)
) -> Response:
    analysis = await STORE.get_municipality_analysis(municipality_id)
    if analysis is None:
        return _api_error(404, "NOT_FOUND", f"Municipality '{municipality_id}' not found")
    response.headers["Cache-Control"] = "max-age=900"
    return JSONResponse(status_code=200, content=analysis.model_dump(mode="json"))


@router.get("/analysis/clusters/{region_id}", response_model=list[ClusterData])
async def get_cluster_analysis(
    region_id: str, response: Response, _: None = Depends(require_atroz_headers)
) -> list[ClusterData]:
    response.headers["Cache-Control"] = "max-age=900"
    return await STORE.get_cluster_analysis(region_id)


@router.get("/analysis/questions/{municipality_id}", response_model=list[QuestionAnalysis])
async def get_questions(
    municipality_id: str, response: Response, _: None = Depends(require_atroz_headers)
) -> list[QuestionAnalysis]:
    response.headers["Cache-Control"] = "max-age=900"
    return await STORE.get_questions(municipality_id)


@router.get("/visualization/constellation", response_model=ConstellationData)
async def get_constellation(
    response: Response, _: None = Depends(require_atroz_headers)
) -> ConstellationData:
    response.headers["Cache-Control"] = "max-age=1800"
    data = await STORE.build_constellation()
    return data


@router.get("/visualization/radar/{municipality_id}", response_model=dict[str, float])
async def get_radar(
    municipality_id: str, response: Response, _: None = Depends(require_atroz_headers)
) -> Response:
    analysis = await STORE.get_municipality_analysis(municipality_id)
    if analysis is None:
        return _api_error(404, "NOT_FOUND", f"Municipality '{municipality_id}' not found")
    response.headers["Cache-Control"] = "max-age=900"
    return JSONResponse(status_code=200, content=analysis.radar)


@router.get("/visualization/phylogram/{region_id}")
async def get_phylogram(region_id: str, _: None = Depends(require_atroz_headers)) -> dict[str, Any]:
    return {"regionId": region_id, "type": "phylogram", "data": []}


@router.get("/visualization/mesh/{region_id}")
async def get_mesh(region_id: str, _: None = Depends(require_atroz_headers)) -> dict[str, Any]:
    return {"regionId": region_id, "type": "mesh", "data": []}


@router.get("/visualization/helix/{region_id}")
async def get_helix(region_id: str, _: None = Depends(require_atroz_headers)) -> dict[str, Any]:
    return {"regionId": region_id, "type": "helix", "data": []}


@router.get("/timeline/regions/{region_id}", response_model=list[TimelinePoint])
async def get_timeline(
    region_id: str, _: None = Depends(require_atroz_headers)
) -> list[TimelinePoint]:
    return await STORE.get_timeline(region_id)


@router.get("/comparison/regions", response_model=ComparisonMatrix)
async def compare_regions(
    ids: str = Query(..., description="Comma-separated region IDs"),
    metrics: str | None = Query(default=None, description="Comma-separated metrics"),
    _: None = Depends(require_atroz_headers),
) -> ComparisonMatrix:
    id_list = [value.strip() for value in ids.split(",") if value.strip()]
    metric_list = [value.strip() for value in (metrics or "").split(",") if value.strip()]
    return await STORE.compare("region", id_list, metric_list)


@router.post("/comparison/matrix", response_model=ComparisonMatrix)
async def compare_matrix(
    payload: ComparisonMatrixRequest, _: None = Depends(require_atroz_headers)
) -> ComparisonMatrix:
    return await STORE.compare(payload.entityType, payload.ids, payload.metrics)


@router.get("/evidence/stream")
async def evidence_stream(
    request: Request, _: None = Depends(require_atroz_headers)
) -> EventSourceResponse:
    return EventSourceResponse(SSE_HUB.events(request))


@router.get("/documents/references")
async def get_references(_: None = Depends(require_atroz_headers)) -> dict[str, Any]:
    return {"references": []}


@router.get("/documents/sources")
async def get_sources(_: None = Depends(require_atroz_headers)) -> dict[str, Any]:
    return {"sources": []}


@router.get("/documents/citations")
async def get_citations(_: None = Depends(require_atroz_headers)) -> dict[str, Any]:
    return {"citations": []}


@router.post("/export/dashboard")
async def export_dashboard(
    payload: ExportRequest, _: None = Depends(require_atroz_headers)
) -> Response:
    return _export_bytes("dashboard", payload)


@router.post("/export/region")
async def export_region(
    payload: ExportRequest, _: None = Depends(require_atroz_headers)
) -> Response:
    return _export_bytes("region", payload)


@router.post("/export/comparison")
async def export_comparison(
    payload: ExportRequest, _: None = Depends(require_atroz_headers)
) -> Response:
    return _export_bytes("comparison", payload)


@router.post("/export/reports")
async def export_reports(
    payload: ExportRequest, _: None = Depends(require_atroz_headers)
) -> Response:
    return _export_bytes("reports", payload)


@router.post("/export/municipality")
async def export_municipality(
    payload: ExportRequest, _: None = Depends(require_atroz_headers)
) -> Response:
    return _export_bytes("municipality", payload)


@router.websocket("/realtime")
async def realtime(websocket: WebSocket) -> None:
    await WS_HUB.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await WS_HUB.disconnect(websocket)


def _export_bytes(scope: str, payload: ExportRequest) -> Response:
    if payload.format == "png":
        data = _transparent_png_1x1()
        return Response(
            content=data,
            media_type="image/png",
            headers={"Content-Disposition": f'attachment; filename="{scope}.png"'},
        )
    if payload.format == "svg":
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"></svg>'
        return Response(
            content=svg.encode("utf-8"),
            media_type="image/svg+xml",
            headers={"Content-Disposition": f'attachment; filename="{scope}.svg"'},
        )
    if payload.format == "pdf":
        pdf = _minimal_pdf()
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{scope}.pdf"'},
        )
    html = "<!doctype html><html><body><pre>Export placeholder</pre></body></html>"
    return Response(
        content=html.encode("utf-8"),
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{scope}.html"'},
    )


def _transparent_png_1x1() -> bytes:
    return bytes.fromhex(
        "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C489"
        "0000000A49444154789C63000100000500010D0A2DB40000000049454E44AE426082"
    )


def _minimal_pdf() -> bytes:
    return (
        b"%PDF-1.4\n1 0 obj<<>>endobj\n"
        b"2 0 obj<< /Type /Catalog /Pages 3 0 R >>endobj\n"
        b"3 0 obj<< /Type /Pages /Kids [4 0 R] /Count 1 >>endobj\n"
        b"4 0 obj<< /Type /Page /Parent 3 0 R /MediaBox [0 0 1 1] >>endobj\n"
        b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000030 00000 n \n"
        b"0000000079 00000 n \n0000000128 00000 n \ntrailer<< /Size 5 /Root 2 0 R >>\n"
        b"startxref\n190\n%%EOF\n"
    )
