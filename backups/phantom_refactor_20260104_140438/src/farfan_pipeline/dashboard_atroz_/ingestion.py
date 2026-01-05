"""Dashboard ingestion client (Phase 10 integration point).

Consumes the orchestrator context and posts a strictly identified municipal update to the
AtroZ dashboard backend ingest endpoint.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from difflib import get_close_matches
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

import httpx
import structlog

from .api_v1_schemas import DashboardIngestRequest, MunicipalitySelector
from .api_v1_utils import slugify
from .pdet_colombia_data import PDET_MUNICIPALITIES, PDETMunicipality

logger = structlog.get_logger(__name__)

_DANE_RE = re.compile(r"(?<!\d)(\d{5})(?!\d)")


def _jsonable(obj: Any) -> Any:
    if is_dataclass(obj):
        return _jsonable(asdict(obj))
    if isinstance(obj, Mapping):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.astimezone(timezone.utc).isoformat()
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def _extract_dane_code(*values: str) -> str | None:
    for value in values:
        match = _DANE_RE.search(value)
        if match:
            return match.group(1)
    return None


def _municipality_id(municipality: PDETMunicipality) -> str:
    return f"{slugify(municipality.name)}-{slugify(municipality.department)}"


def _resolve_municipality_from_context(context: Mapping[str, Any]) -> PDETMunicipality | None:
    document = context.get("document")
    input_data = getattr(document, "input_data", None) if document is not None else None

    doc_id = str(getattr(input_data, "document_id", "") or "")
    pdf_path = str(getattr(input_data, "pdf_path", "") or "")

    dane_code = _extract_dane_code(doc_id, pdf_path)
    if dane_code:
        matches = [m for m in PDET_MUNICIPALITIES if m.dane_code == dane_code]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValueError(f"Ambiguous DANE code match for {dane_code}: {len(matches)} candidates")

    candidate_text = Path(pdf_path).stem if pdf_path else doc_id
    cleaned = slugify(candidate_text.replace("_", " ").replace("-", " "))

    dept_slugs = {slugify(m.department): m.department for m in PDET_MUNICIPALITIES}
    dept_hits = [dept for slug, dept in dept_slugs.items() if slug and slug in cleaned]
    dept = dept_hits[0] if len(dept_hits) == 1 else None

    name_candidates = []
    for m in PDET_MUNICIPALITIES:
        name_slug = slugify(m.name)
        if name_slug and name_slug in cleaned:
            if dept is None or m.department == dept:
                name_candidates.append(m)

    if len(name_candidates) == 1:
        return name_candidates[0]
    if len(name_candidates) > 1:
        raise ValueError(f"Ambiguous municipality match for '{candidate_text}': {len(name_candidates)} candidates")

    names = [slugify(m.name) for m in PDET_MUNICIPALITIES]
    fuzzy = get_close_matches(cleaned, names, n=1, cutoff=0.85)
    if not fuzzy:
        return None

    fuzzy_name = fuzzy[0]
    fuzzy_matches = [m for m in PDET_MUNICIPALITIES if slugify(m.name) == fuzzy_name]
    if dept is not None:
        fuzzy_matches = [m for m in fuzzy_matches if m.department == dept]

    if len(fuzzy_matches) == 1:
        return fuzzy_matches[0]

    return None


class DashboardIngester:
    def __init__(
        self,
        ingest_url: str | None = None,
        auth_token: str | None = None,
        client_name: str = "dashboard-v1",
        client_version: str = "1.0.0",
        timeout_s: float = 5.0,
        max_retries: int = 3,
    ) -> None:
        import os

        self._ingest_url = ingest_url or os.getenv(
            "ATROZ_DASHBOARD_INGEST_URL", "http://localhost:8000/api/v1/data/ingest"
        )
        self._auth_token = auth_token or os.getenv("ATROZ_DASHBOARD_JWT", "")
        self._client_name = client_name
        self._client_version = client_version
        self._timeout_s = timeout_s
        self._max_retries = max_retries

    async def ingest_results(self, context: Mapping[str, Any]) -> bool:
        municipality = _resolve_municipality_from_context(context)
        if municipality is None:
            logger.error("dashboard_ingest_municipality_unresolved")
            return False

        document = context.get("document")
        input_data = getattr(document, "input_data", None) if document is not None else None
        run_id = str(getattr(input_data, "run_id", "") or "") or f"run_unknown_{int(datetime.now().timestamp())}"

        selector = MunicipalitySelector(
            id=_municipality_id(municipality),
            dane_code=municipality.dane_code or None,
            name=municipality.name,
            department=municipality.department,
            document_id=str(getattr(input_data, "document_id", "") or "") or None,
            pdf_path=str(getattr(input_data, "pdf_path", "") or "") or None,
        )

        macro_result = context.get("macro_result")
        cluster_scores = context.get("cluster_scores")
        policy_area_scores = context.get("policy_area_scores")
        dimension_scores = context.get("dimension_scores")
        scored_results = context.get("scored_results")
        micro_results = context.get("micro_results")

        minimal_micro_results: list[dict[str, Any]] | None = None
        if isinstance(micro_results, list):
            minimal_micro_results = [
                {
                    "question_id": getattr(r, "question_id", None),
                    "question_global": getattr(r, "question_global", None),
                    "base_slot": getattr(r, "base_slot", None),
                    "error": getattr(r, "error", None),
                    "duration_ms": getattr(r, "duration_ms", None),
                    "aborted": getattr(r, "aborted", None),
                }
                for r in micro_results
            ]

        payload = DashboardIngestRequest(
            run_id=run_id,
            timestamp=datetime.now(timezone.utc),
            municipality=selector,
            macro_result=_jsonable(macro_result) if macro_result is not None else None,
            cluster_scores=_jsonable(cluster_scores) if cluster_scores is not None else None,
            policy_area_scores=_jsonable(policy_area_scores) if policy_area_scores is not None else None,
            dimension_scores=_jsonable(dimension_scores) if dimension_scores is not None else None,
            scored_results=_jsonable(scored_results) if scored_results is not None else None,
            micro_results=minimal_micro_results,
        )

        headers = {
            "X-Atroz-Client": self._client_name,
            "X-Atroz-Version": self._client_version,
            "X-Request-ID": str(uuid4()),
            "Content-Type": "application/json",
        }
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"

        body = payload.model_dump(mode="json")

        for attempt in range(1, self._max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self._timeout_s) as client:
                    response = await client.post(self._ingest_url, json=body, headers=headers)

                if 200 <= response.status_code < 300:
                    logger.info(
                        "dashboard_ingest_ok",
                        municipality_id=selector.id,
                        run_id=run_id,
                        status_code=response.status_code,
                    )
                    return True

                if response.status_code in {429, 500, 503} and attempt < self._max_retries:
                    await asyncio.sleep(2**attempt)
                    continue

                logger.error(
                    "dashboard_ingest_failed",
                    municipality_id=selector.id,
                    run_id=run_id,
                    status_code=response.status_code,
                    response_text=response.text[:512],
                )
                return False

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt >= self._max_retries:
                    logger.error(
                        "dashboard_ingest_network_error",
                        municipality_id=selector.id,
                        run_id=run_id,
                        error=str(exc),
                    )
                    return False
                await asyncio.sleep(2**attempt)

        return False
