"""AtroZ Dashboard API v1 schemas.

These models define the wire contracts for the dashboard backend. They are intentionally
strict (extra fields forbidden) for outward-facing responses, while ingest payloads allow
extra fields to preserve full orchestrator artifacts.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class APIError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: int
    code: str
    message: str
    details: dict[str, Any] | None = None
    retryAfter: int | None = None


class Coordinates2D(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float


class PDETRegionScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall: float
    governance: float
    social: float
    economic: float
    environmental: float


class PDETRegion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    municipalities: int
    scores: PDETRegionScores
    coordinates: Coordinates2D


class ClusterData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    score: float
    normalized_score: float


class QuestionAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    questionId: int = Field(..., ge=0)
    score: float
    evidence: list[str]
    quality: Literal["EXCELENTE", "ACEPTABLE", "INSUFICIENTE", "NO_APLICABLE", "ERROR"]


class MunicipalAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    radar: dict[str, float]
    clusters: list[ClusterData]
    questions: list[QuestionAnalysis]
    recommendations: list[str] = Field(default_factory=list)


class Municipality(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    department: str
    regionId: str
    population: int = Field(default=0, ge=0)
    analysis: MunicipalAnalysis | None = None


class ConstellationNodePosition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float


class ConstellationNodeProperties(BaseModel):
    model_config = ConfigDict(extra="forbid")

    size: float
    color: str
    pulseRate: float
    connectionStrength: float


class ConstellationNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    position: ConstellationNodePosition
    properties: ConstellationNodeProperties


class ConstellationConnection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    target: str
    strength: float
    type: Literal["geographic", "score_similarity", "pdet_region"]


class ConstellationData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: list[ConstellationNode]
    connections: list[ConstellationConnection]


class TimelinePoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: str
    scores: dict[str, float]
    events: list[str]


class ComparisonMatrix(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entityType: Literal["region", "municipality"]
    ids: list[str]
    metrics: list[str]
    matrix: dict[str, dict[str, float]]


class ComparisonMatrixRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entityType: Literal["region", "municipality"]
    ids: list[str] = Field(..., min_length=1, max_length=20)
    metrics: list[str] = Field(default_factory=list)


class ExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    format: Literal["png", "svg", "pdf", "html"]
    resolution: Literal["720p", "1080p", "4k"] = "1080p"
    includeData: bool = True


class MunicipalitySelector(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    dane_code: str | None = None
    name: str | None = None
    department: str | None = None
    document_id: str | None = None
    pdf_path: str | None = None


class MacroClusterScoreDataIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    score: float
    normalized_score: float


class MacroEvaluationIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    macro_score: float
    macro_score_normalized: float
    clusters: list[MacroClusterScoreDataIn]
    details: dict[str, Any] | None = None


class ClusterScoreIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    cluster_id: str
    cluster_name: str | None = None
    score: float
    coherence: float | None = None


class ScoredMicroQuestionIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    question_id: str
    question_global: int
    score: float | None = None
    normalized_score: float | None = None
    quality_level: str | None = None
    evidence: dict[str, Any] | None = None


class DashboardIngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    timestamp: datetime
    municipality: MunicipalitySelector | None = None

    macro_result: MacroEvaluationIn | None = None
    cluster_scores: list[ClusterScoreIn] | None = None
    policy_area_scores: list[dict[str, Any]] | None = None
    dimension_scores: list[dict[str, Any]] | None = None
    scored_results: list[ScoredMicroQuestionIn] | None = None
    micro_results: list[dict[str, Any]] | None = None

    pdet_regions: list[PDETRegion] | None = None
    municipalities: list[Municipality] | None = None
