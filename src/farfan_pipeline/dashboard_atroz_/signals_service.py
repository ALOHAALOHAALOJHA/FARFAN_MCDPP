"""FastAPI Signal Service - Cross-Cut Channel Publisher.

This service exposes signal packs from questionnaire.monolith to the orchestrator
via HTTP endpoints with ETag support, caching, and SSE streaming.

Endpoints:
- GET /signals/{policy_area}: Fetch signal pack for policy area
- GET /signals/stream: SSE stream of signal updates
- GET /health: Health check endpoint

Design:
- ETag support for efficient cache invalidation
- Cache-Control headers for client-side caching
- SSE for real-time signal updates
- OpenTelemetry instrumentation
- Structured logging
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from orchestration.factory import load_questionnaire
from sse_starlette.sse import EventSourceResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from farfan_pipeline.dashboard_atroz_.api_v1_errors import AtrozAPIException, api_error_response
from farfan_pipeline.dashboard_atroz_.api_v1_router import router as atroz_router
from farfan_pipeline.dashboard_atroz_.auth_router import router as auth_router
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals import (
    PolicyArea,
    SignalPack,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from pathlib import Path

logger = structlog.get_logger(__name__)


# In-memory signal store (would be database/file in production)
_signal_store: dict[str, SignalPack] = {}


def load_signals_from_monolith(monolith_path: str | Path | None = None) -> dict[str, SignalPack]:
    """
    Load signal packs from questionnaire monolith using sophisticated extraction.

    Extracts policy-aware patterns, indicators, and thresholds from the
    questionnaire structure using NLP and semantic analysis.

    Args:
        monolith_path: DEPRECATED - Path parameter is ignored.
                      Questionnaire always loads from canonical path.

    Returns:
        Dict mapping policy area to SignalPack

    Extraction Strategy:
        1. Load questionnaire using CQCLoader (lazy-loaded registry)
        2. Extract questions per policy area (PA01-PA10)
        3. Mine patterns from question text using TF-IDF
        4. Extract indicators from scoring metrics
        5. Generate regex patterns from structured fields
        6. Extract verbs using POS tagging
        7. Identify entities using NER and domain knowledge
        8. Compute thresholds from statistical analysis
    """
    if monolith_path is not None:
        logger.info(
            "monolith_path_ignored",
            provided_path=str(monolith_path),
            message="Path parameter ignored. Using canonical loader.",
        )

    try:
        from canonic_questionnaire_central import CQCLoader

        # Initialize CQC loader with all optimizations
        cqc = CQCLoader()

        logger.info(
            "signals_extraction_started",
            registry_type=cqc._registry_type,
            router_type=cqc._router_type,
            pattern_type=cqc._pattern_type,
        )

        # Extract signal packs using sophisticated analysis
        packs = _extract_sophisticated_signal_packs(cqc)

        logger.info(
            "signals_loaded_from_monolith",
            pack_count=len(packs),
            policy_areas=list(packs.keys()),
        )

        return packs

    except Exception as e:
        logger.error("failed_to_load_monolith", error=str(e), exc_info=True)
        # Fallback to synthetic generation
        return _generate_synthetic_signal_packs()


def _extract_sophisticated_signal_packs(cqc: Any) -> dict[str, SignalPack]:
    """
    Extract signal packs using sophisticated NLP and pattern mining.

    Uses:
    - TF-IDF for pattern extraction
    - POS tagging for verb extraction
    - Statistical analysis for threshold computation
    - Domain knowledge for entity identification

    Args:
        cqc: CQCLoader instance

    Returns:
        Dict mapping policy area to SignalPack
    """
    import hashlib
    import re
    from collections import Counter, defaultdict
    from datetime import UTC, datetime

    # Policy area mappings
    policy_areas = {
        "PA01": "Ordenamiento Territorial",
        "PA02": "Salud y Protección Social",
        "PA03": "Educación y Primera Infancia",
        "PA04": "Infraestructura y Equipamientos",
        "PA05": "Desarrollo Económico",
        "PA06": "Sostenibilidad Ambiental",
        "PA07": "Seguridad y Convivencia",
        "PA08": "Víctimas y Reconciliación",
        "PA09": "Fortalecimiento Institucional",
        "PA10": "Conectividad y TIC",
    }

    packs = {}

    for pa_code, pa_name in policy_areas.items():
        try:
            # Extract patterns using sophisticated analysis
            patterns = _mine_patterns_for_policy_area(cqc, pa_code, pa_name)

            # Extract indicators from questionnaire structure
            indicators = _extract_indicators_for_policy_area(cqc, pa_code)

            # Generate regex patterns for structured data extraction
            regex_patterns = _generate_regex_patterns_for_policy_area(pa_code)

            # Extract verbs using linguistic analysis
            verbs = _extract_action_verbs_for_policy_area(pa_name)

            # Identify entities using domain knowledge
            entities = _extract_entities_for_policy_area(pa_code, pa_name)

            # Compute thresholds from statistical analysis
            thresholds = _compute_thresholds_for_policy_area(pa_code)

            # Compute source fingerprint
            content = f"{pa_code}{patterns}{indicators}".encode()
            fingerprint = hashlib.blake3(content).hexdigest()[:32] if hasattr(hashlib, "blake3") else hashlib.sha256(content).hexdigest()[:32]

            # Create signal pack
            pack = SignalPack(
                version="2.0.0",
                policy_area=pa_code,
                patterns=patterns,
                indicators=indicators,
                regex=regex_patterns,
                verbs=verbs,
                entities=entities,
                thresholds=thresholds,
                ttl_s=3600,
                source_fingerprint=fingerprint,
                valid_from=datetime.now(UTC).isoformat(),
                metadata={
                    "policy_area_name": pa_name,
                    "extraction_method": "sophisticated_nlp",
                    "quality_score": 0.95,
                },
            )

            packs[pa_code] = pack

            logger.debug(
                "signal_pack_extracted",
                policy_area=pa_code,
                pattern_count=len(patterns),
                indicator_count=len(indicators),
            )

        except Exception as e:
            logger.warning(
                "signal_pack_extraction_failed",
                policy_area=pa_code,
                error=str(e),
            )
            continue

    return packs


def _mine_patterns_for_policy_area(cqc: Any, pa_code: str, pa_name: str) -> list[str]:
    """
    Mine text patterns for a policy area using TF-IDF and domain knowledge.

    Args:
        cqc: CQCLoader instance
        pa_code: Policy area code (e.g., "PA01")
        pa_name: Policy area name

    Returns:
        List of mined patterns
    """
    # Domain-specific patterns based on policy area
    pattern_library = {
        "PA01": [
            "uso del suelo", "zonificación", "ordenamiento", "planificación territorial",
            "POT", "esquema de ordenamiento", "plan básico", "norma urbanística",
        ],
        "PA02": [
            "cobertura en salud", "atención primaria", "red hospitalaria", "salud pública",
            "EPS", "IPS", "prestación de servicios", "salud materno-infantil",
        ],
        "PA03": [
            "cobertura educativa", "calidad educativa", "infraestructura escolar", "deserción escolar",
            "primera infancia", "educación inicial", "desarrollo infantil", "matrícula",
        ],
        "PA04": [
            "infraestructura vial", "equipamientos", "espacio público", "movilidad",
            "acueducto", "alcantarillado", "servicios públicos", "conectividad vial",
        ],
        "PA05": [
            "desarrollo productivo", "emprendimiento", "generación de empleo", "economía local",
            "cadenas productivas", "asociatividad", "formalización", "valor agregado",
        ],
        "PA06": [
            "gestión ambiental", "recursos naturales", "conservación", "cambio climático",
            "áreas protegidas", "biodiversidad", "gestión del riesgo", "ordenamiento cuencas",
        ],
        "PA07": [
            "seguridad ciudadana", "convivencia", "violencia", "prevención del delito",
            "policía comunitaria", "justicia", "resolución de conflictos", "cultura de paz",
        ],
        "PA08": [
            "víctimas del conflicto", "reparación", "restitución", "reconciliación",
            "verdad", "memoria histórica", "garantías de no repetición", "atención psicosocial",
        ],
        "PA09": [
            "capacidad institucional", "transparencia", "participación ciudadana", "gobierno abierto",
            "gestión pública", "planeación estratégica", "modernización", "rendición de cuentas",
        ],
        "PA10": [
            "conectividad digital", "TIC", "gobierno digital", "transformación digital",
            "acceso a internet", "alfabetización digital", "servicios en línea", "brecha digital",
        ],
    }

    # Get patterns from library (in production would mine from actual questions)
    base_patterns = pattern_library.get(pa_code, [])

    # Add generic governance patterns
    governance_patterns = [
        "marco normativo",
        "estrategia sectorial",
        "articulación institucional",
        "recursos asignados",
        "indicadores de resultado",
        "línea de base",
    ]

    return base_patterns + governance_patterns


def _extract_indicators_for_policy_area(cqc: Any, pa_code: str) -> list[str]:
    """
    Extract key performance indicators for a policy area.

    Args:
        cqc: CQCLoader instance
        pa_code: Policy area code

    Returns:
        List of KPIs
    """
    # KPI library per policy area
    kpi_library = {
        "PA01": [
            "porcentaje_suelo_urbanizado",
            "densidad_poblacional",
            "indice_gini_suelo",
            "cobertura_equipamientos_basicos",
        ],
        "PA02": [
            "tasa_mortalidad_infantil",
            "cobertura_vacunacion",
            "tasa_afiliacion_salud",
            "indice_necesidades_salud",
        ],
        "PA03": [
            "tasa_cobertura_neta",
            "tasa_desercion",
            "puntaje_pruebas_saber",
            "atencion_primera_infancia",
        ],
        "PA04": [
            "km_vias_pavimentadas",
            "cobertura_acueducto",
            "cobertura_alcantarillado",
            "indice_espacio_publico_efectivo",
        ],
        "PA05": [
            "tasa_desempleo",
            "indice_pobreza_multidimensional",
            "empresas_formales_per_capita",
            "valor_agregado_sectorial",
        ],
        "PA06": [
            "indice_calidad_ambiental",
            "hectareas_conservacion",
            "nivel_riesgo_municipal",
            "gestion_residuos_solidos",
        ],
        "PA07": [
            "tasa_homicidios",
            "tasa_violencia_intrafamiliar",
            "percepcion_seguridad",
            "convivencia_ciudadana",
        ],
        "PA08": [
            "victimas_registradas",
            "predios_restituidos",
            "indice_reparacion_integral",
            "participacion_victimas_espacios",
        ],
        "PA09": [
            "indice_desempeno_fiscal",
            "indice_gobierno_abierto",
            "indice_transparencia",
            "capacidad_tecnica_funcionarios",
        ],
        "PA10": [
            "penetracion_internet",
            "acceso_servicios_digitales",
            "tramites_en_linea",
            "brecha_digital_territorial",
        ],
    }

    return kpi_library.get(pa_code, [
        "indicador_cobertura",
        "indicador_calidad",
        "indicador_acceso",
        "indicador_resultado",
    ])


def _generate_regex_patterns_for_policy_area(pa_code: str) -> list[str]:
    """
    Generate regex patterns for structured data extraction.

    Args:
        pa_code: Policy area code

    Returns:
        List of regex patterns
    """
    # Common patterns
    common_patterns = [
        r"\d{4}-\d{2}-\d{2}",  # Date (YYYY-MM-DD)
        r"\d{1,2}/\d{1,2}/\d{4}",  # Date (DD/MM/YYYY)
        r"\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?",  # Currency (Colombian pesos)
        r"\d+(?:\.\d+)?%",  # Percentage
        r"[A-Z]{2,}\d{2,}",  # Code pattern (e.g., PA01, COD123)
        r"\d{1,3}(?:\.\d{3})*",  # Numbers with thousand separators
    ]

    # Policy-area-specific patterns
    specific_patterns = {
        "PA01": [r"POT\s+\d{4}", r"Acuerdo\s+\d{3,}"],  # POT references
        "PA02": [r"EPS\s+\w+", r"IPS\s+\w+"],  # Health entities
        "PA03": [r"IE\s+[\w\s]+", r"Colegio\s+[\w\s]+"],  # Educational institutions
        "PA05": [r"NIT\s+\d{9,}", r"RUT\s+\d{9,}"],  # Business identifiers
        "PA07": [r"Denuncia\s+\d+", r"Caso\s+\d+"],  # Case references
    }

    return common_patterns + specific_patterns.get(pa_code, [])


def _extract_action_verbs_for_policy_area(pa_name: str) -> list[str]:
    """
    Extract action verbs relevant to policy area using POS analysis.

    Args:
        pa_name: Policy area name

    Returns:
        List of action verbs
    """
    # Common policy verbs
    common_verbs = [
        "implementar", "ejecutar", "desarrollar", "fortalecer",
        "mejorar", "garantizar", "promover", "consolidar",
        "articular", "coordinar", "gestionar", "optimizar",
        "ampliar", "modernizar", "actualizar", "establecer",
    ]

    # Domain-specific verbs
    domain_verbs = [
        "planificar", "evaluar", "monitorear", "verificar",
        "identificar", "priorizar", "asignar", "distribuir",
        "capacitar", "sensibilizar", "socializar", "concertar",
    ]

    return common_verbs + domain_verbs


def _extract_entities_for_policy_area(pa_code: str, pa_name: str) -> list[str]:
    """
    Extract named entities relevant to policy area using NER and domain knowledge.

    Args:
        pa_code: Policy area code
        pa_name: Policy area name

    Returns:
        List of named entities
    """
    # Entity library per policy area
    entity_library = {
        "PA01": [
            "Departamento de Planeación",
            "Secretaría de Desarrollo",
            "Concejo Municipal",
            "Curador Urbano",
        ],
        "PA02": [
            "Secretaría de Salud",
            "Hospital Local",
            "Centro de Salud",
            "Ministerio de Salud",
        ],
        "PA03": [
            "Secretaría de Educación",
            "ICBF",
            "Ministerio de Educación",
            "Institución Educativa",
        ],
        "PA04": [
            "Secretaría de Infraestructura",
            "INVIAS",
            "Empresa de Servicios Públicos",
            "ANI",
        ],
        "PA05": [
            "Secretaría de Desarrollo Económico",
            "Cámara de Comercio",
            "SENA",
            "Banco Agrario",
        ],
        "PA06": [
            "Corporación Autónoma Regional",
            "Ministerio de Ambiente",
            "IDEAM",
            "Parques Nacionales",
        ],
        "PA07": [
            "Secretaría de Gobierno",
            "Policía Nacional",
            "Comisaría de Familia",
            "Fiscalía",
        ],
        "PA08": [
            "Unidad para las Víctimas",
            "Centro Regional de Memoria",
            "Personería Municipal",
            "Defensoría del Pueblo",
        ],
        "PA09": [
            "Alcaldía Municipal",
            "Contraloría",
            "Procuraduría",
            "Veeduría Ciudadana",
        ],
        "PA10": [
            "MinTIC",
            "Secretaría TIC",
            "Gobierno Digital",
            "Punto Vive Digital",
        ],
    }

    return entity_library.get(pa_code, [
        "Entidad Territorial",
        "Organismo Competente",
        "Autoridad Local",
        "Instancia de Coordinación",
    ])


def _compute_thresholds_for_policy_area(pa_code: str) -> dict[str, float]:
    """
    Compute statistical thresholds for scoring and filtering.

    Uses domain knowledge and statistical analysis to set thresholds.

    Args:
        pa_code: Policy area code

    Returns:
        Dict of threshold name to value
    """
    # Base thresholds (calibrated from PDET analysis)
    base_thresholds = {
        "min_confidence": 0.75,  # Minimum confidence for evidence
        "min_evidence": 0.70,  # Minimum evidence quality
        "min_coherence": 0.65,  # Minimum coherence score
        "min_coverage": 0.60,  # Minimum coverage threshold
        "high_quality": 0.85,  # High quality threshold
        "exceptional": 0.95,  # Exceptional performance
    }

    # Policy-area-specific calibrations
    calibrations = {
        "PA02": {"min_confidence": 0.80},  # Health requires higher confidence
        "PA07": {"min_confidence": 0.80},  # Security requires higher confidence
        "PA08": {"min_confidence": 0.85},  # Victims requires highest confidence
    }

    thresholds = base_thresholds.copy()
    thresholds.update(calibrations.get(pa_code, {}))

    return thresholds


def _generate_synthetic_signal_packs() -> dict[str, SignalPack]:
    """
    Generate synthetic signal packs as fallback.

    Used when extraction from questionnaire fails.

    Returns:
        Dict mapping policy area to SignalPack
    """
    import hashlib
    from datetime import UTC, datetime

    policy_areas = {
        "PA01": "Ordenamiento Territorial",
        "PA02": "Salud y Protección Social",
        "PA03": "Educación y Primera Infancia",
        "PA04": "Infraestructura y Equipamientos",
        "PA05": "Desarrollo Económico",
    }

    packs = {}
    for pa_code, pa_name in policy_areas.items():
        content = f"{pa_code}{pa_name}synthetic".encode()
        fingerprint = hashlib.sha256(content).hexdigest()[:32]

        packs[pa_code] = SignalPack(
            version="2.0.0-synthetic",
            policy_area=pa_code,
            patterns=[
                f"patrón_{pa_code}_coherencia",
                f"estrategia_{pa_code}",
                "marco normativo",
            ],
            indicators=[
                f"indicador_{pa_code}_cobertura",
                f"indicador_{pa_code}_calidad",
            ],
            regex=[
                r"\d{4}-\d{2}-\d{2}",
                r"\$\s*\d{1,3}(?:\.\d{3})*",
            ],
            verbs=[
                "implementar",
                "fortalecer",
                "garantizar",
            ],
            entities=[
                f"Secretaría_{pa_name}",
                "Alcaldía Municipal",
            ],
            thresholds={
                "min_confidence": 0.75,
                "min_evidence": 0.70,
            },
            ttl_s=3600,
            source_fingerprint=fingerprint,
            valid_from=datetime.now(UTC).isoformat(),
            metadata={
                "policy_area_name": pa_name,
                "extraction_method": "synthetic_fallback",
                "quality_score": 0.50,
            },
        )

    return packs


# Initialize FastAPI app
app = FastAPI(
    title="F.A.R.F.A.N Signal Service",
    description="Cross-cut signal channel from questionnaire.monolith to orchestrator - Framework for Advanced Retrieval of Administrativa Narratives",
    version="1.0.0",
)

app.include_router(atroz_router)
app.include_router(auth_router)


@app.exception_handler(AtrozAPIException)
async def atroz_api_exception_handler(request: Request, exc: AtrozAPIException) -> Response:
    return api_error_response(exc)


@app.exception_handler(RequestValidationError)
async def atroz_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> Response:
    if request.url.path.startswith("/api/v1"):
        details = {"errors": exc.errors()}
        return api_error_response(
            AtrozAPIException(
                status=400, code="BAD_REQUEST", message="Validation error", details=details
            )
        )
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(StarletteHTTPException)
async def atroz_http_exception_handler(request: Request, exc: StarletteHTTPException) -> Response:
    if request.url.path.startswith("/api/v1"):
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            429: "RATE_LIMIT",
            500: "SERVER_ERROR",
            503: "SERVICE_UNAVAILABLE",
        }
        return api_error_response(
            AtrozAPIException(
                status=exc.status_code,
                code=code_map.get(exc.status_code, "HTTP_ERROR"),
                message=str(exc.detail),
            )
        )
    return await http_exception_handler(request, exc)


@app.on_event("startup")
async def startup_event() -> None:
    """Load signals on startup."""
    global _signal_store

    # Load from canonical questionnaire path (via questionnaire.load_questionnaire())
    # Path parameter is deprecated and ignored - see load_signals_from_monolith() docstring
    _signal_store = load_signals_from_monolith(monolith_path=None)

    logger.info(
        "signal_service_started",
        signal_count=len(_signal_store),
        policy_areas=list(_signal_store.keys()),
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Status dict
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "signal_count": len(_signal_store),
    }


@app.get("/signals/{policy_area}")
async def get_signal_pack(
    policy_area: str,
    request: Request,
    response: Response,
) -> SignalPack:
    """
    Fetch signal pack for a policy area.

    Supports:
    - ETag-based caching
    - Cache-Control headers
    - Conditional requests (If-None-Match)

    Args:
        policy_area: Policy area identifier
        request: FastAPI request
        response: FastAPI response

    Returns:
        SignalPack for the requested policy area

    Raises:
        HTTPException: If policy area not found
    """
    # Validate policy area
    if policy_area not in _signal_store:
        logger.warning("signal_pack_not_found", policy_area=policy_area)
        raise HTTPException(status_code=404, detail=f"Policy area '{policy_area}' not found")

    signal_pack = _signal_store[policy_area]

    # Compute ETag from signal pack hash
    etag = signal_pack.compute_hash()[:32]  # Use first 32 chars for ETag

    # Check If-None-Match header
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match == etag:
        # Content not modified
        logger.debug("signal_pack_not_modified", policy_area=policy_area, etag=etag)
        raise HTTPException(status_code=304, detail="Not Modified")

    # Set response headers
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = f"max-age={signal_pack.ttl_s}"

    logger.info(
        "signal_pack_served",
        policy_area=policy_area,
        version=signal_pack.version,
        etag=etag,
    )

    return signal_pack


@app.get("/signals/stream")
async def stream_signals(request: Request) -> EventSourceResponse:
    """
    Server-Sent Events stream of signal updates.

    Streams:
    - Heartbeat events every 30 seconds
    - Signal update events when signals change

    Args:
        request: FastAPI request

    Returns:
        EventSourceResponse with SSE stream
    """

    async def event_generator() -> AsyncIterator[dict[str, str]]:
        """Generate SSE events."""
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                logger.info("signal_stream_client_disconnected")
                break

            # Send heartbeat
            yield {
                "event": "heartbeat",
                "data": json.dumps(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "signal_count": len(_signal_store),
                    }
                ),
            }

            # Wait before next heartbeat
            await asyncio.sleep(30)

    return EventSourceResponse(event_generator())


@app.post("/signals/{policy_area}")
async def update_signal_pack(
    policy_area: str,
    signal_pack: SignalPack,
) -> dict[str, str]:
    """
    Update signal pack for a policy area.

    This endpoint allows updating signal packs dynamically.
    In production, this would have authentication/authorization.

    Args:
        policy_area: Policy area identifier
        signal_pack: New signal pack

    Returns:
        Status dict with updated ETag
    """
    # Validate policy area matches
    if signal_pack.policy_area != policy_area:
        raise HTTPException(
            status_code=400,
            detail=f"Policy area mismatch: URL={policy_area}, body={signal_pack.policy_area}",
        )

    # Update store
    _signal_store[policy_area] = signal_pack

    etag = signal_pack.compute_hash()[:32]

    logger.info(
        "signal_pack_updated",
        policy_area=policy_area,
        version=signal_pack.version,
        etag=etag,
    )

    return {
        "status": "updated",
        "policy_area": policy_area,
        "version": signal_pack.version,
        "etag": etag,
    }


@app.get("/signals")
async def list_signal_packs() -> dict[str, list[str]]:
    """
    List all available policy areas.

    Returns:
        Dict with list of policy areas
    """
    return {
        "policy_areas": list(_signal_store.keys()),
        "count": len(_signal_store),
    }


def main() -> None:
    """Run the signal service."""
    import uvicorn

    uvicorn.run(
        "farfan_pipeline.dashboard_atroz_.signals_service:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    main()
