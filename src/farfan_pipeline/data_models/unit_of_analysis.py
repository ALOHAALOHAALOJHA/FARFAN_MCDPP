"""
Unit of analysis and policy document definitions for calibration and Bayesian analysis.

This module provides classes to represent the territorial and fiscal context
of municipalities, policy documents, and analysis results for proper calibration 
of Bayesian priors and comprehensive policy evaluation.

Implements SOTA patterns:
- Comprehensive type hints with future annotations
- Dataclass with frozen for immutability where appropriate
- Pydantic v2 BaseModel for runtime validation
- Enhanced validation and error handling
- Integration with signal extraction patterns from dashboard_atroz_
- Alignment with SISAS irrigation patterns
- Cryptographic verification for traceability

Author: F.A.R.F.A.N Core Team
Created: 2026-01-16
Version: 3.0.0-sota
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional, Dict, List, Tuple, Literal, TypeVar, Generic

import structlog
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

# Configure structured logging
logger = structlog.get_logger(__name__)


# ============================================================================
# TYPE SYSTEM - Literal Types for Contract Safety
# ============================================================================

EvidenceStrengthType = Literal["weak", "moderate", "strong", "very_strong"]
QualityLevelType = Literal["excellent", "good", "acceptable", "poor", "critical"]
DocumentFormatType = Literal["PDF", "DOCX", "TXT", "JSON", "HTML"]
AnalysisStatusType = Literal["pending", "processing", "completed", "failed", "validated"]
ScoreBandType = Literal["BAJO", "MEDIO", "ALTO", "SATISFACTORIO", "INSUFICIENTE"]


# ============================================================================
# ENUMERATIONS - Context Classifications
# ============================================================================


class FiscalContext(Enum):
    """
    Categorización de la capacidad fiscal de municipios colombianos.
    
    Esta clasificación se basa en la dependencia del Sistema General de Participaciones (SGP)
    y la capacidad de generación de recursos propios, alineada con categorías DNP.
    
    Values:
        HIGH_CAPACITY: Municipios categoría 1-2 con alta capacidad fiscal (>60% recursos propios)
        MEDIUM_CAPACITY: Municipios categoría 3-4 con capacidad fiscal moderada (30-60% recursos propios)
        LOW_CAPACITY: Municipios categoría 5-6 dependientes del SGP (<30% recursos propios)
        SPECIAL_DISTRICT: Distritos especiales con régimen fiscal diferenciado
    """
    
    HIGH_CAPACITY = auto()
    MEDIUM_CAPACITY = auto()
    LOW_CAPACITY = auto()
    SPECIAL_DISTRICT = auto()
    
    def to_weight(self) -> float:
        """Convert fiscal context to Bayesian prior weight."""
        weights = {
            self.HIGH_CAPACITY: 0.9,
            self.MEDIUM_CAPACITY: 0.7,
            self.LOW_CAPACITY: 0.5,
            self.SPECIAL_DISTRICT: 0.8,
        }
        return weights.get(self, 0.5)
    
    def to_dnp_category(self) -> str:
        """Map to DNP fiscal category string."""
        mapping = {
            self.HIGH_CAPACITY: "CATEGORÍA 1-2",
            self.MEDIUM_CAPACITY: "CATEGORÍA 3-4",
            self.LOW_CAPACITY: "CATEGORÍA 5-6",
            self.SPECIAL_DISTRICT: "DISTRITO ESPECIAL",
        }
        return mapping.get(self, "SIN CLASIFICAR")


class TerritorialCategory(Enum):
    """
    Categorización territorial según tipología DNP/DANE.
    
    Values:
        CIUDAD_CAPITAL: Ciudades capitales y áreas metropolitanas
        CIUDAD_INTERMEDIA: Ciudades intermedias (50k-500k habitantes)
        MUNICIPIO_RURAL: Municipios predominantemente rurales
        MUNICIPIO_DISPERSO: Municipios rurales dispersos
        ZONA_FRONTERA: Municipios fronterizos con régimen especial
    """
    
    CIUDAD_CAPITAL = auto()
    CIUDAD_INTERMEDIA = auto()
    MUNICIPIO_RURAL = auto()
    MUNICIPIO_DISPERSO = auto()
    ZONA_FRONTERA = auto()


class PolicyDocumentType(Enum):
    """
    Tipos de documentos de política pública colombiana.
    
    Values:
        PDM: Plan de Desarrollo Municipal
        PDD: Plan de Desarrollo Departamental
        PND: Plan Nacional de Desarrollo
        PGAR: Plan de Gestión Ambiental Regional
        POT: Plan de Ordenamiento Territorial
        PMGRD: Plan Municipal de Gestión del Riesgo
        PDET: Plan Especial de Desarrollo con Enfoque Territorial
        CONPES: Documento CONPES
        OTHER: Otro tipo de documento
    """
    
    PDM = auto()
    PDD = auto()
    PND = auto()
    PGAR = auto()
    POT = auto()
    PMGRD = auto()
    PDET = auto()
    CONPES = auto()
    OTHER = auto()
    
    @classmethod
    def from_string(cls, value: str) -> PolicyDocumentType:
        """Parse document type from string."""
        mapping = {
            "pdm": cls.PDM, "plan de desarrollo municipal": cls.PDM,
            "pdd": cls.PDD, "plan de desarrollo departamental": cls.PDD,
            "pnd": cls.PND, "plan nacional de desarrollo": cls.PND,
            "pgar": cls.PGAR, "plan de gestión ambiental": cls.PGAR,
            "pot": cls.POT, "plan de ordenamiento territorial": cls.POT,
            "pmgrd": cls.PMGRD, "plan de gestión del riesgo": cls.PMGRD,
            "pdet": cls.PDET, "plan especial": cls.PDET,
            "conpes": cls.CONPES, "documento conpes": cls.CONPES,
        }
        return mapping.get(value.lower().strip(), cls.OTHER)


class CausalDimension(Enum):
    """
    Dimensiones causales del Marco Lógico para análisis de políticas.
    
    Values:
        D1_INSUMOS: Inputs/recursos para la política
        D2_ACTIVIDADES: Activities/acciones programadas
        D3_PRODUCTOS: Outputs/productos entregables
        D4_RESULTADOS: Outcomes/resultados intermedios
        D5_IMPACTOS: Impacts/efectos a largo plazo
        D6_CAUSALIDAD: Causal mechanisms/mecanismos causales
    """
    
    D1_INSUMOS = "D1"
    D2_ACTIVIDADES = "D2"
    D3_PRODUCTOS = "D3"
    D4_RESULTADOS = "D4"
    D5_IMPACTOS = "D5"
    D6_CAUSALIDAD = "D6"
    
    @property
    def description(self) -> str:
        """Get dimension description in Spanish."""
        descriptions = {
            self.D1_INSUMOS: "Insumos y recursos asignados",
            self.D2_ACTIVIDADES: "Actividades y acciones programadas",
            self.D3_PRODUCTOS: "Productos y bienes entregados",
            self.D4_RESULTADOS: "Resultados intermedios alcanzados",
            self.D5_IMPACTOS: "Impactos y cambios de largo plazo",
            self.D6_CAUSALIDAD: "Cadena de causalidad y mecanismos",
        }
        return descriptions.get(self, "Dimensión no especificada")


# ============================================================================
# DATACLASSES - Immutable Context Objects
# ============================================================================


@dataclass
class GeographicContext:
    """
    Contexto geográfico y administrativo del municipio.
    
    Attributes:
        latitude: Latitud del centroide municipal
        longitude: Longitud del centroide municipal
        altitude_m: Altitud promedio en metros sobre el nivel del mar
        area_km2: Área total del municipio en km²
        distance_to_capital_km: Distancia a la capital departamental en km
        subregion: Subregión según clasificación departamental
        zomac: Si es Zona Más Afectada por el Conflicto Armado
    """
    
    latitude: float
    longitude: float
    altitude_m: Optional[float] = None
    area_km2: Optional[float] = None
    distance_to_capital_km: Optional[float] = None
    subregion: Optional[str] = None
    zomac: bool = False


@dataclass
class SocialIndicators:
    """
    Indicadores sociales del municipio para calibración contextual.
    
    Attributes:
        nbi: Necesidades Básicas Insatisfechas (0.0-100.0)
        education_coverage: Cobertura educativa neta (0.0-1.0)
        health_coverage: Cobertura en salud (0.0-1.0)
        water_access: Acceso a agua potable (0.0-1.0)
        electricity_access: Acceso a electricidad (0.0-1.0)
        internet_penetration: Penetración de internet (0.0-1.0)
        violence_index: Índice de violencia normalizado (0.0-1.0)
    """
    
    nbi: Optional[float] = None
    education_coverage: float = 0.0
    health_coverage: float = 0.0
    water_access: float = 0.0
    electricity_access: float = 0.0
    internet_penetration: float = 0.0
    violence_index: float = 0.0
    
    def infrastructure_score(self) -> float:
        """Calculate infrastructure development score."""
        scores = [
            self.water_access,
            self.electricity_access,
            self.internet_penetration,
        ]
        valid_scores = [s for s in scores if s > 0]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0.0


@dataclass(frozen=True)
class CredibleInterval:
    """
    Bayesian credible interval with evidence metadata.
    
    Attributes:
        lower: Lower bound of the interval
        upper: Upper bound of the interval
        level: Confidence level (e.g., 0.95 for 95% CI)
        method: Estimation method (e.g., "HDI", "quantile")
    """
    
    lower: float
    upper: float
    level: float = 0.95
    method: str = "HDI"
    
    @property
    def width(self) -> float:
        """Calculate interval width."""
        return self.upper - self.lower
    
    @property
    def midpoint(self) -> float:
        """Calculate interval midpoint."""
        return (self.lower + self.upper) / 2
    
    def contains(self, value: float) -> bool:
        """Check if value is within the interval."""
        return self.lower <= value <= self.upper
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple for serialization compatibility."""
        return (self.lower, self.upper)


@dataclass(frozen=True)
class BayesianPosterior:
    """
    Bayesian posterior distribution summary.
    
    Attributes:
        point_estimate: Central tendency estimate (median/mean)
        credible_interval: 95% credible interval
        evidence_strength: Qualitative assessment of evidence
        posterior_samples: Number of posterior samples
        convergence_diagnostic: R-hat or similar convergence metric
    """
    
    point_estimate: float
    credible_interval: CredibleInterval
    evidence_strength: EvidenceStrengthType
    posterior_samples: int = 10000
    convergence_diagnostic: float = 1.0
    
    @property
    def is_significant(self) -> bool:
        """Check if posterior is significantly different from null."""
        return not self.credible_interval.contains(0.0)
    
    @property
    def uncertainty_ratio(self) -> float:
        """Calculate uncertainty as ratio of CI width to point estimate."""
        if abs(self.point_estimate) < 1e-10:
            return float('inf')
        return self.credible_interval.width / abs(self.point_estimate)


# ============================================================================
# PYDANTIC MODELS - Runtime Validated Domain Objects
# ============================================================================


class PolicyDocumentMetadata(BaseModel):
    """
    Metadata for a policy document with validation.
    
    Aligns with Colombian policy document standards (SINERGIA, DNP).
    """
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )
    
    document_id: str = Field(
        ...,
        description="Unique document identifier",
        min_length=3,
        max_length=128,
        pattern=r"^[A-Za-z0-9\-_]+$",
    )
    title: str = Field(..., description="Document title", min_length=5, max_length=500)
    municipality_code: str = Field(
        ..., 
        description="DANE municipality code", 
        pattern=r"^\d{5,6}$"
    )
    department_code: str = Field(
        ..., 
        description="DANE department code", 
        pattern=r"^\d{2}$"
    )
    administration_period: str = Field(
        ...,
        description="Administration period (e.g., '2024-2027')",
        pattern=r"^\d{4}-\d{4}$",
    )
    document_type: str = Field(default="PDM", description="Document type code")
    source_format: DocumentFormatType = Field(default="PDF", description="Source format")
    version: str = Field(default="1.0", description="Document version")
    language: str = Field(default="es", description="Document language (ISO 639-1)")
    page_count: int = Field(default=0, ge=0, description="Number of pages")
    character_count: int = Field(default=0, ge=0, description="Character count")
    extraction_date: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="Text extraction timestamp",
    )
    
    @field_validator("administration_period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        """Validate administration period is valid."""
        start, end = v.split("-")
        if int(end) <= int(start):
            raise ValueError("End year must be greater than start year")
        if int(end) - int(start) > 10:
            raise ValueError("Administration period cannot exceed 10 years")
        return v


class PolicyDocument(BaseModel):
    """
    Complete policy document representation for analysis pipeline.
    
    This is the primary input contract for the F.A.R.F.A.N analysis engine.
    Implements cryptographic verification for traceability.
    
    Attributes:
        metadata: Document metadata
        raw_text: Full extracted text content
        sections: Structured sections (chapter -> content)
        tables: Extracted tables as structured data
        numerical_data: Extracted numerical values with context
        fingerprint: SHA-256 fingerprint for verification
    """
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
    )
    
    metadata: PolicyDocumentMetadata = Field(..., description="Document metadata")
    raw_text: str = Field(..., description="Full document text", min_length=100)
    sections: Dict[str, str] = Field(
        default_factory=dict, 
        description="Structured sections by chapter/section name"
    )
    tables: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Extracted tables as structured data"
    )
    numerical_data: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Extracted numerical values with context",
    )
    annotations: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional annotations and enrichments",
    )
    fingerprint: str = Field(
        default="",
        description="SHA-256 fingerprint of content",
        pattern=r"^[a-f0-9]{64}$|^$",
    )
    
    @model_validator(mode="after")
    def compute_fingerprint_if_missing(self) -> "PolicyDocument":
        """Compute fingerprint if not provided."""
        if not self.fingerprint:
            content = json.dumps({
                "document_id": self.metadata.document_id,
                "text_hash": hashlib.sha256(self.raw_text.encode()).hexdigest()[:16],
                "section_count": len(self.sections),
                "table_count": len(self.tables),
            }, sort_keys=True)
            computed = hashlib.sha256(content.encode()).hexdigest()
            # Since frozen, we need to use object.__setattr__
            object.__setattr__(self, "fingerprint", computed)
        return self
    
    @property
    def document_type(self) -> PolicyDocumentType:
        """Get parsed document type enum."""
        return PolicyDocumentType.from_string(self.metadata.document_type)
    
    @property
    def word_count(self) -> int:
        """Estimate word count from raw text."""
        return len(self.raw_text.split())
    
    @property
    def section_count(self) -> int:
        """Get number of sections."""
        return len(self.sections)
    
    def get_section(self, name: str) -> Optional[str]:
        """Get section content by name (case-insensitive)."""
        name_lower = name.lower()
        for key, value in self.sections.items():
            if key.lower() == name_lower:
                return value
        return None
    
    def extract_numerical_patterns(self) -> List[Dict[str, Any]]:
        """Extract numerical patterns from raw text."""
        patterns = [
            (r"\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?\s*%", "percentage"),
            (r"\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?", "currency_cop"),
            (r"\d+(?:\.\d+)?\s*(?:millones?|mil millones?|billones?)", "monetary"),
            (r"\d+\s*(?:por|cada)\s*(?:100|mil|100\.000)", "rate"),
        ]
        
        results = []
        for pattern, pattern_type in patterns:
            for match in re.finditer(pattern, self.raw_text, re.IGNORECASE):
                results.append({
                    "value": match.group(),
                    "type": pattern_type,
                    "position": match.span(),
                    "context": self.raw_text[max(0, match.start()-50):match.end()+50],
                })
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metadata": self.metadata.model_dump(),
            "raw_text_length": len(self.raw_text),
            "section_count": len(self.sections),
            "table_count": len(self.tables),
            "numerical_data_count": len(self.numerical_data),
            "fingerprint": self.fingerprint,
            "word_count": self.word_count,
        }


class DimensionScore(BaseModel):
    """
    Score for a single causal dimension with Bayesian uncertainty.
    """
    
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    dimension: str = Field(..., description="Dimension code (D1-D6)")
    score: float = Field(..., ge=0.0, le=3.0, description="Dimension score (0-3 scale)")
    credible_interval_lower: float = Field(..., ge=0.0, le=3.0)
    credible_interval_upper: float = Field(..., ge=0.0, le=3.0)
    evidence_count: int = Field(..., ge=0, description="Number of evidence items")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level")
    evidence_strength: EvidenceStrengthType = Field(default="moderate")
    
    @property
    def credible_interval(self) -> Tuple[float, float]:
        """Get credible interval as tuple."""
        return (self.credible_interval_lower, self.credible_interval_upper)
    
    @property
    def is_reliable(self) -> bool:
        """Check if score is considered reliable (sufficient evidence)."""
        return self.evidence_count >= 3 and self.confidence >= 0.6


class QuestionScore(BaseModel):
    """
    Score for a single questionnaire question (Q001-Q300).
    """
    
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    question_id: str = Field(..., description="Question ID (Q###)", pattern=r"^Q\d{3}$")
    policy_area: str = Field(..., description="Policy area code (PA##)", pattern=r"^PA\d{2}$")
    dimension: str = Field(..., description="Dimension code (D#)", pattern=r"^D\d$")
    score: float = Field(..., ge=0.0, le=3.0, description="Question score")
    raw_evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    method_chain: List[str] = Field(default_factory=list, description="Methods used")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    
    @property
    def is_satisfactory(self) -> bool:
        """Check if score meets satisfactory threshold (>= 2.0)."""
        return self.score >= 2.0


class ClusterAnalysis(BaseModel):
    """
    Meso-level cluster analysis result.
    """
    
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    cluster_id: str = Field(..., description="Cluster ID (CL##)", pattern=r"^CL\d{2}$")
    cluster_name: str = Field(..., description="Cluster name/description")
    aggregate_score: float = Field(..., ge=0.0, le=100.0, description="Aggregate cluster score")
    variance: float = Field(default=0.0, ge=0.0, description="Score variance within cluster")
    policy_areas: List[str] = Field(default_factory=list, description="Policy areas in cluster")
    weak_areas: List[str] = Field(default_factory=list, description="Weakest policy areas")
    strong_areas: List[str] = Field(default_factory=list, description="Strongest policy areas")
    recommendations: List[str] = Field(default_factory=list, description="Cluster-specific recommendations")
    
    @property
    def score_band(self) -> ScoreBandType:
        """Classify score into band."""
        if self.aggregate_score >= 80:
            return "SATISFACTORIO"
        elif self.aggregate_score >= 60:
            return "ALTO"
        elif self.aggregate_score >= 40:
            return "MEDIO"
        elif self.aggregate_score >= 20:
            return "BAJO"
        else:
            return "INSUFICIENTE"


class MacroSummary(BaseModel):
    """
    Macro-level policy analysis summary.
    """
    
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall policy score")
    quality_level: QualityLevelType = Field(..., description="Quality classification")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Identified weaknesses")
    priority_recommendations: List[str] = Field(default_factory=list, description="Top recommendations")
    pdet_alignment_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    sdg_alignment_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    @property
    def is_passing(self) -> bool:
        """Check if overall score is passing (>= 60)."""
        return self.overall_score >= 60.0


class AnalysisResult(BaseModel):
    """
    Complete policy analysis result with multi-level aggregation.
    
    This is the primary output contract for the F.A.R.F.A.N analysis engine.
    Contains micro (question), meso (cluster), and macro (summary) level results
    with full Bayesian uncertainty quantification and cryptographic traceability.
    
    Attributes:
        document_id: Reference to analyzed document
        analysis_id: Unique analysis run identifier
        status: Analysis completion status
        micro_scores: Question-level scores (Q001-Q300)
        dimension_scores: Dimension-level aggregates (D1-D6)
        cluster_analyses: Meso-level cluster results
        macro_summary: Overall policy assessment
        bayesian_metadata: Bayesian analysis metadata
        processing_metrics: Performance and timing metrics
        evidence_chain_hash: Cryptographic hash of evidence chain
    """
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
    )
    
    # Identification
    document_id: str = Field(..., description="Source document ID")
    analysis_id: str = Field(
        default_factory=lambda: hashlib.sha256(
            str(datetime.now(UTC)).encode()
        ).hexdigest()[:16],
        description="Unique analysis run ID",
    )
    status: AnalysisStatusType = Field(default="completed", description="Analysis status")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="Analysis timestamp",
    )
    
    # Micro-level (Question scores)
    micro_scores: Dict[str, QuestionScore] = Field(
        default_factory=dict, 
        description="Question scores keyed by Q### ID"
    )
    
    # Dimension aggregates
    dimension_scores: Dict[str, DimensionScore] = Field(
        default_factory=dict,
        description="Dimension scores keyed by D# code",
    )
    
    # Meso-level (Cluster analyses)
    cluster_analyses: Dict[str, ClusterAnalysis] = Field(
        default_factory=dict,
        description="Cluster analyses keyed by CL## ID",
    )
    
    # Macro-level (Summary)
    macro_summary: Optional[MacroSummary] = Field(
        default=None, 
        description="Overall policy summary"
    )
    
    # Bayesian metadata
    bayesian_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Bayesian analysis parameters and diagnostics",
    )
    
    # Processing metrics
    processing_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Performance and timing metrics",
    )
    
    # Traceability
    evidence_chain_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of evidence chain",
        pattern=r"^[a-f0-9]{64}$|^$",
    )
    
    @property
    def total_questions_analyzed(self) -> int:
        """Get count of analyzed questions."""
        return len(self.micro_scores)
    
    @property
    def average_micro_score(self) -> float:
        """Calculate average micro score."""
        if not self.micro_scores:
            return 0.0
        scores = [q.score for q in self.micro_scores.values()]
        return sum(scores) / len(scores)
    
    @property
    def coverage_rate(self) -> float:
        """Calculate question coverage rate (vs 300 total)."""
        return len(self.micro_scores) / 300.0
    
    def get_weak_questions(self, threshold: float = 1.5) -> List[QuestionScore]:
        """Get questions below score threshold."""
        return [q for q in self.micro_scores.values() if q.score < threshold]
    
    def get_strong_questions(self, threshold: float = 2.5) -> List[QuestionScore]:
        """Get questions above score threshold."""
        return [q for q in self.micro_scores.values() if q.score >= threshold]
    
    def get_questions_by_policy_area(self, policy_area: str) -> List[QuestionScore]:
        """Get all questions for a specific policy area."""
        return [q for q in self.micro_scores.values() if q.policy_area == policy_area]
    
    def get_questions_by_dimension(self, dimension: str) -> List[QuestionScore]:
        """Get all questions for a specific dimension."""
        return [q for q in self.micro_scores.values() if q.dimension == dimension]
    
    def compute_digest(self) -> str:
        """Compute SHA-256 digest of analysis results."""
        content = json.dumps({
            "document_id": self.document_id,
            "analysis_id": self.analysis_id,
            "micro_count": len(self.micro_scores),
            "avg_score": self.average_micro_score,
            "status": self.status,
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "document_id": self.document_id,
            "analysis_id": self.analysis_id,
            "status": self.status,
            "timestamp": self.timestamp,
            "summary": {
                "total_questions": self.total_questions_analyzed,
                "average_score": round(self.average_micro_score, 3),
                "coverage_rate": round(self.coverage_rate, 3),
                "weak_questions": len(self.get_weak_questions()),
                "strong_questions": len(self.get_strong_questions()),
            },
            "dimension_scores": {
                k: v.model_dump() for k, v in self.dimension_scores.items()
            },
            "cluster_analyses": {
                k: v.model_dump() for k, v in self.cluster_analyses.items()
            },
            "macro_summary": self.macro_summary.model_dump() if self.macro_summary else None,
            "processing_metrics": self.processing_metrics,
            "evidence_chain_hash": self.evidence_chain_hash,
            "digest": self.compute_digest(),
        }
    
    def to_sabana_row(self) -> Dict[str, Any]:
        """Export as SISAS sabana-compatible row."""
        return {
            "documento_id": self.document_id,
            "analisis_id": self.analysis_id,
            "fecha_analisis": self.timestamp,
            "score_promedio": round(self.average_micro_score, 3),
            "preguntas_analizadas": self.total_questions_analyzed,
            "cobertura": round(self.coverage_rate, 3),
            "nivel_calidad": self.macro_summary.quality_level if self.macro_summary else "pending",
            "score_global": self.macro_summary.overall_score if self.macro_summary else 0.0,
            "hash_evidencia": self.evidence_chain_hash,
        }


# ============================================================================
# UNIT OF ANALYSIS - Core Municipal Analysis Unit
# ============================================================================


@dataclass(frozen=True)
class UnitOfAnalysis:
    """
    Representa las características de una unidad territorial de análisis.
    
    Esta clase encapsula las propiedades municipales relevantes para calibrar
    los análisis Bayesianos y ajustar priors según el contexto territorial.
    Implementa inmutabilidad (frozen) para garantizar consistencia en análisis.
    
    Attributes:
        municipality_code: Código DANE del municipio (formato: DDDMMM)
        municipality_name: Nombre oficial del municipio
        department_code: Código DANE del departamento
        department_name: Nombre del departamento
        population: Población estimada (último censo)
        fiscal_context: Categoría de capacidad fiscal
        territorial_category: Categoría territorial DNP
        pdet_municipality: Si es municipio PDET (170 municipios priorizados)
        conflict_affected: Si ha sido afectado por conflicto armado
        rural_share: Proporción de población rural (0.0 a 1.0)
        poverty_index: Índice de pobreza multidimensional IPM (0.0 a 1.0)
        geographic_context: Contexto geográfico opcional
        social_indicators: Indicadores sociales opcionales
        metadata: Metadatos adicionales (fechas, fuentes, etc.)
    """
    
    municipality_code: str
    municipality_name: str
    department_code: str
    department_name: str
    population: int
    fiscal_context: FiscalContext
    territorial_category: TerritorialCategory = TerritorialCategory.MUNICIPIO_RURAL
    pdet_municipality: bool = False
    conflict_affected: bool = False
    rural_share: float = 0.5
    poverty_index: float = 0.0
    geographic_context: Optional[GeographicContext] = None
    social_indicators: Optional[SocialIndicators] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate data after initialization."""
        # Validate municipality code format (DDDMMM)
        if not self.municipality_code or len(self.municipality_code) not in [5, 6]:
            raise ValueError(f"Invalid municipality code: {self.municipality_code}")
        
        # Validate ranges
        if not 0.0 <= self.rural_share <= 1.0:
            raise ValueError(f"rural_share must be between 0.0 and 1.0: {self.rural_share}")
        
        if not 0.0 <= self.poverty_index <= 1.0:
            raise ValueError(f"poverty_index must be between 0.0 and 1.0: {self.poverty_index}")
        
        if self.population < 0:
            raise ValueError(f"Population cannot be negative: {self.population}")
        
        # Log creation
        logger.debug(
            "unit_of_analysis_created",
            municipality_code=self.municipality_code,
            municipality_name=self.municipality_name,
            fiscal_context=self.fiscal_context.name,
        )
    
    def complexity_score(self) -> float:
        """
        Calcula un score de complejidad basado en características municipales.
        
        Implementa un modelo multi-dimensional ponderado que considera:
        - Tamaño poblacional (logarítmico)
        - Contexto territorial
        - Factores de vulnerabilidad (PDET, conflicto, ZOMAC)
        - Indicadores socioeconómicos
        - Capacidad institucional
        
        Returns:
            float: Score de complejidad entre 0.0 (simple) y 1.0 (muy complejo)
        """
        weights = {
            "population": 0.15,
            "territorial": 0.15,
            "vulnerability": 0.25,
            "socioeconomic": 0.25,
            "institutional": 0.20,
        }
        
        scores = {}
        
        # Population complexity (logarithmic scale)
        if self.population > 1000000:
            scores["population"] = 1.0
        elif self.population > 500000:
            scores["population"] = 0.8
        elif self.population > 100000:
            scores["population"] = 0.6
        elif self.population > 50000:
            scores["population"] = 0.4
        elif self.population > 20000:
            scores["population"] = 0.2
        else:
            scores["population"] = 0.1
        
        # Territorial complexity
        territorial_scores = {
            TerritorialCategory.CIUDAD_CAPITAL: 0.8,
            TerritorialCategory.CIUDAD_INTERMEDIA: 0.6,
            TerritorialCategory.MUNICIPIO_RURAL: 0.4,
            TerritorialCategory.MUNICIPIO_DISPERSO: 0.7,
            TerritorialCategory.ZONA_FRONTERA: 0.9,
        }
        scores["territorial"] = territorial_scores.get(self.territorial_category, 0.5)
        
        # Vulnerability factors
        vulnerability = 0.0
        if self.pdet_municipality:
            vulnerability += 0.35
        if self.conflict_affected:
            vulnerability += 0.35
        if self.geographic_context and self.geographic_context.zomac:
            vulnerability += 0.3
        scores["vulnerability"] = min(vulnerability, 1.0)
        
        # Socioeconomic complexity
        socio_score = 0.0
        socio_score += self.poverty_index * 0.4
        socio_score += self.rural_share * 0.3
        if self.social_indicators:
            if self.social_indicators.nbi:
                socio_score += (self.social_indicators.nbi / 100.0) * 0.3
        scores["socioeconomic"] = min(socio_score, 1.0)
        
        # Institutional complexity (inverse of fiscal capacity)
        fiscal_scores = {
            FiscalContext.HIGH_CAPACITY: 0.2,
            FiscalContext.MEDIUM_CAPACITY: 0.5,
            FiscalContext.LOW_CAPACITY: 0.8,
            FiscalContext.SPECIAL_DISTRICT: 0.3,
        }
        scores["institutional"] = fiscal_scores.get(self.fiscal_context, 0.5)
        
        # Calculate weighted average
        total_score = sum(
            scores.get(key, 0.0) * weight
            for key, weight in weights.items()
        )
        
        return min(total_score, 1.0)
    
    def priority_score(self) -> float:
        """
        Calcula score de priorización para políticas públicas.
        
        Municipios con mayor score requieren mayor atención en políticas.
        
        Returns:
            float: Score de prioridad entre 0.0 (baja) y 1.0 (máxima)
        """
        # Start with complexity
        score = self.complexity_score() * 0.5
        
        # Add vulnerability bonus
        if self.pdet_municipality:
            score += 0.2
        
        # Add poverty bonus
        score += self.poverty_index * 0.3
        
        return min(score, 1.0)
    
    def to_calibration_params(self) -> Dict[str, float]:
        """
        Convert unit characteristics to Bayesian calibration parameters.
        
        Returns:
            Dict with calibration parameters for Bayesian analysis
        """
        return {
            "prior_weight": self.fiscal_context.to_weight(),
            "complexity_factor": self.complexity_score(),
            "uncertainty_multiplier": 1.0 + (self.complexity_score() * 0.5),
            "sample_size_adjustment": max(0.5, 1.0 - (self.complexity_score() * 0.3)),
            "convergence_threshold": 0.01 * (1.0 + self.complexity_score()),
        }
    
    def get_signal_context(self) -> Dict[str, Any]:
        """
        Generate context for signal extraction aligned with SISAS patterns.
        
        Returns:
            Dict with signal extraction context
        """
        return {
            "municipality_code": self.municipality_code,
            "fiscal_category": self.fiscal_context.name,
            "is_pdet": self.pdet_municipality,
            "complexity_score": self.complexity_score(),
            "priority_score": self.priority_score(),
            "rural_context": self.rural_share > 0.6,
            "vulnerable_population": self.poverty_index > 0.4,
        }
    
    def generate_fingerprint(self) -> str:
        """
        Generate stable fingerprint for caching and comparison.
        
        Returns:
            str: SHA256 fingerprint of unit characteristics
        """
        content = json.dumps({
            "code": self.municipality_code,
            "fiscal": self.fiscal_context.name,
            "population": self.population,
            "pdet": self.pdet_municipality,
            "rural": self.rural_share,
            "poverty": self.poverty_index,
        }, sort_keys=True)
        
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def __repr__(self) -> str:
        """Enhanced string representation for debugging."""
        return (
            f"UnitOfAnalysis(code={self.municipality_code}, "
            f"name={self.municipality_name}, "
            f"dept={self.department_name}, "
            f"pop={self.population:,}, "
            f"fiscal={self.fiscal_context.name}, "
            f"category={self.territorial_category.name}, "
            f"complexity={self.complexity_score():.2f}, "
            f"priority={self.priority_score():.2f})"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dict representation of the unit
        """
        base = {
            "municipality_code": self.municipality_code,
            "municipality_name": self.municipality_name,
            "department_code": self.department_code,
            "department_name": self.department_name,
            "population": self.population,
            "fiscal_context": self.fiscal_context.name,
            "territorial_category": self.territorial_category.name,
            "pdet_municipality": self.pdet_municipality,
            "conflict_affected": self.conflict_affected,
            "rural_share": self.rural_share,
            "poverty_index": self.poverty_index,
            "complexity_score": self.complexity_score(),
            "priority_score": self.priority_score(),
            "fingerprint": self.generate_fingerprint(),
        }
        
        if self.geographic_context:
            base["geographic"] = {
                "latitude": self.geographic_context.latitude,
                "longitude": self.geographic_context.longitude,
                "altitude_m": self.geographic_context.altitude_m,
                "area_km2": self.geographic_context.area_km2,
                "zomac": self.geographic_context.zomac,
            }
        
        if self.social_indicators:
            base["social"] = {
                "nbi": self.social_indicators.nbi,
                "education_coverage": self.social_indicators.education_coverage,
                "health_coverage": self.social_indicators.health_coverage,
                "infrastructure_score": self.social_indicators.infrastructure_score(),
            }
        
        if self.metadata:
            base["metadata"] = self.metadata
        
        return base


# ============================================================================
# COLLECTION CLASSES
# ============================================================================


@dataclass
class UnitCollection:
    """
    Collection of units for batch analysis with SOTA operations.
    
    Attributes:
        units: List of UnitOfAnalysis instances
        collection_id: Unique identifier for the collection
        created_at: Timestamp of collection creation
    """
    
    units: List[UnitOfAnalysis] = field(default_factory=list)
    collection_id: str = field(default_factory=lambda: hashlib.sha256(
        str(datetime.now(UTC)).encode()
    ).hexdigest()[:16])
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    
    def add_unit(self, unit: UnitOfAnalysis) -> None:
        """Add a unit to the collection with validation."""
        if not isinstance(unit, UnitOfAnalysis):
            raise TypeError("Unit must be instance of UnitOfAnalysis")
        
        # Check for duplicates
        existing_codes = {u.municipality_code for u in self.units}
        if unit.municipality_code in existing_codes:
            logger.warning(
                "duplicate_unit_skipped",
                municipality_code=unit.municipality_code
            )
            return
        
        self.units.append(unit)
        logger.debug(
            "unit_added_to_collection",
            collection_id=self.collection_id,
            municipality_code=unit.municipality_code
        )
    
    def get_by_fiscal_context(self, context: FiscalContext) -> List[UnitOfAnalysis]:
        """Filter units by fiscal context."""
        return [u for u in self.units if u.fiscal_context == context]
    
    def get_pdet_units(self) -> List[UnitOfAnalysis]:
        """Get all PDET municipalities."""
        return [u for u in self.units if u.pdet_municipality]
    
    def get_priority_units(self, threshold: float = 0.7) -> List[UnitOfAnalysis]:
        """Get units above priority threshold."""
        return [u for u in self.units if u.priority_score() >= threshold]
    
    def aggregate_stats(self) -> Dict[str, Any]:
        """Calculate aggregate statistics for the collection."""
        if not self.units:
            return {}
        
        total_population = sum(u.population for u in self.units)
        avg_complexity = sum(u.complexity_score() for u in self.units) / len(self.units)
        avg_priority = sum(u.priority_score() for u in self.units) / len(self.units)
        
        fiscal_distribution = {}
        for context in FiscalContext:
            count = len(self.get_by_fiscal_context(context))
            fiscal_distribution[context.name] = count
        
        return {
            "collection_id": self.collection_id,
            "total_units": len(self.units),
            "total_population": total_population,
            "pdet_count": len(self.get_pdet_units()),
            "avg_complexity_score": avg_complexity,
            "avg_priority_score": avg_priority,
            "fiscal_distribution": fiscal_distribution,
            "high_priority_count": len(self.get_priority_units()),
        }
    
    def to_dataframe_dict(self) -> List[Dict[str, Any]]:
        """Convert to list of dicts suitable for pandas DataFrame."""
        return [u.to_dict() for u in self.units]


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


def create_capital_city(
    code: str,
    name: str,
    department_code: str,
    department_name: str,
    population: int,
) -> UnitOfAnalysis:
    """Factory for capital cities with typical characteristics."""
    return UnitOfAnalysis(
        municipality_code=code,
        municipality_name=name,
        department_code=department_code,
        department_name=department_name,
        population=population,
        fiscal_context=FiscalContext.HIGH_CAPACITY,
        territorial_category=TerritorialCategory.CIUDAD_CAPITAL,
        pdet_municipality=False,
        conflict_affected=False,
        rural_share=0.1,
        poverty_index=0.2,
    )


def create_pdet_municipality(
    code: str,
    name: str,
    department_code: str,
    department_name: str,
    population: int,
    rural_share: float = 0.8,
) -> UnitOfAnalysis:
    """Factory for PDET municipalities with typical characteristics."""
    return UnitOfAnalysis(
        municipality_code=code,
        municipality_name=name,
        department_code=department_code,
        department_name=department_name,
        population=population,
        fiscal_context=FiscalContext.LOW_CAPACITY,
        territorial_category=TerritorialCategory.MUNICIPIO_RURAL,
        pdet_municipality=True,
        conflict_affected=True,
        rural_share=rural_share,
        poverty_index=0.6,
    )


def create_policy_document(
    document_id: str,
    title: str,
    municipality_code: str,
    department_code: str,
    administration_period: str,
    raw_text: str,
    sections: Optional[Dict[str, str]] = None,
    document_type: str = "PDM",
) -> PolicyDocument:
    """Factory for creating policy documents with minimal parameters."""
    metadata = PolicyDocumentMetadata(
        document_id=document_id,
        title=title,
        municipality_code=municipality_code,
        department_code=department_code,
        administration_period=administration_period,
        document_type=document_type,
        character_count=len(raw_text),
    )
    
    return PolicyDocument(
        metadata=metadata,
        raw_text=raw_text,
        sections=sections or {},
    )


def create_empty_analysis_result(
    document_id: str,
    status: AnalysisStatusType = "pending",
) -> AnalysisResult:
    """Factory for creating empty analysis result placeholder."""
    return AnalysisResult(
        document_id=document_id,
        status=status,
    )


def load_units_from_json(filepath: str) -> UnitCollection:
    """
    Load unit collection from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        UnitCollection instance
    """
    collection = UnitCollection()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for unit_data in data.get("units", []):
            # Convert string enums back to enum instances
            if "fiscal_context" in unit_data:
                unit_data["fiscal_context"] = FiscalContext[unit_data["fiscal_context"]]
            if "territorial_category" in unit_data:
                unit_data["territorial_category"] = TerritorialCategory[unit_data["territorial_category"]]
            
            # Handle nested objects
            if "geographic" in unit_data:
                unit_data["geographic_context"] = GeographicContext(**unit_data.pop("geographic"))
            if "social" in unit_data:
                unit_data["social_indicators"] = SocialIndicators(**unit_data.pop("social"))
            
            # Remove computed fields
            unit_data.pop("complexity_score", None)
            unit_data.pop("priority_score", None)
            unit_data.pop("fingerprint", None)
            
            unit = UnitOfAnalysis(**unit_data)
            collection.add_unit(unit)
        
        logger.info(
            "units_loaded_from_json",
            filepath=filepath,
            count=len(collection.units)
        )
        
    except Exception as e:
        logger.error(
            "failed_to_load_units",
            filepath=filepath,
            error=str(e)
        )
        raise
    
    return collection


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Type aliases
    "EvidenceStrengthType",
    "QualityLevelType",
    "DocumentFormatType",
    "AnalysisStatusType",
    "ScoreBandType",
    # Enums
    "FiscalContext",
    "TerritorialCategory",
    "PolicyDocumentType",
    "CausalDimension",
    # Dataclasses
    "GeographicContext",
    "SocialIndicators",
    "CredibleInterval",
    "BayesianPosterior",
    "UnitOfAnalysis",
    "UnitCollection",
    # Pydantic models
    "PolicyDocumentMetadata",
    "PolicyDocument",
    "DimensionScore",
    "QuestionScore",
    "ClusterAnalysis",
    "MacroSummary",
    "AnalysisResult",
    # Factory functions
    "create_capital_city",
    "create_pdet_municipality",
    "create_policy_document",
    "create_empty_analysis_result",
    "load_units_from_json",
]