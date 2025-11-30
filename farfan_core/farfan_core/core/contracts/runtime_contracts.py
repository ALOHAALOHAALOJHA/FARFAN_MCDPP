"""
Runtime contracts: shared enums and manifest models for fallback tracking.

This module defines the contract types used across the system for tracking
degradations, fallbacks, and runtime behavior. All components use these
shared contracts for consistent observability.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LanguageTier(Enum):
    """Language detection result tier indicating detection quality."""
    
    NORMAL = "normal"
    """Language detected successfully."""
    
    WARN_DEFAULT_ES = "warn_default_es"
    """Detection failed with LangDetectException, defaulted to Spanish."""
    
    FAIL = "fail"
    """Detection failed with unexpected error."""


class SegmentationMethod(Enum):
    """Text segmentation method used for document processing."""
    
    SPACY_LG = "spacy_lg"
    """spaCy large model (es_core_news_lg)."""
    
    SPACY_MD = "spacy_md"
    """spaCy medium model (es_core_news_md)."""
    
    SPACY_SM = "spacy_sm"
    """spaCy small model (es_core_news_sm)."""
    
    REGEX = "regex"
    """Regex-based segmentation fallback."""
    
    LINE = "line"
    """Line-based segmentation fallback."""


class CalibrationMode(Enum):
    """Calibration completeness mode."""
    
    FULL = "full"
    """Complete calibration with all required fields."""
    
    DEFAULTED = "defaulted"
    """Some calibration values defaulted."""
    
    PARTIAL = "partial"
    """Partial calibration with missing optional fields."""


class DocumentIdSource(Enum):
    """Source of document identifier."""
    
    METADATA = "metadata"
    """Document ID from metadata (preferred)."""
    
    FILENAME_FALLBACK = "filename_fallback"
    """Document ID from filename (fallback)."""


class ExecutionMetricsMode(Enum):
    """Execution metrics collection mode."""
    
    REAL = "real"
    """Real execution metrics collected."""
    
    ESTIMATED = "estimated"
    """Execution metrics estimated (fallback)."""


class FallbackCategory(Enum):
    """
    Fallback categorization for SLO tracking.
    
    Categories:
        A: Critical - never allowed in PROD (e.g., missing core modules)
        B: Quality degradation - SLO < 5% in PROD (e.g., regex segmentation)
        C: Dev/bootstrap only - not available in PROD
        D: Migration path - tracked for reduction (e.g., filename fallback)
    """
    
    A = "A"
    """Critical fallback - never allowed in PROD."""
    
    B = "B"
    """Quality degradation - SLO < 5% in PROD."""
    
    C = "C"
    """Development/bootstrap only."""
    
    D = "D"
    """Migration path - tracked for reduction."""


# Manifest Models

class LanguageDetectionInfo(BaseModel):
    """Language detection result information for manifest."""
    
    tier: LanguageTier = Field(..., description="Detection result tier")
    detected_language: Optional[str] = Field(None, description="Detected language code (e.g., 'es', 'en')")
    reason: Optional[str] = Field(None, description="Reason for fallback if tier != NORMAL")
    
    class Config:
        frozen = True


class SegmentationInfo(BaseModel):
    """Text segmentation method information for manifest."""
    
    method: SegmentationMethod = Field(..., description="Segmentation method used")
    downgraded_from: Optional[SegmentationMethod] = Field(None, description="Original method if downgraded")
    reason: Optional[str] = Field(None, description="Reason for downgrade")
    
    class Config:
        frozen = True


class CalibrationInfo(BaseModel):
    """Calibration completeness information for manifest."""
    
    mode: CalibrationMode = Field(..., description="Calibration mode")
    defaulted_count: int = Field(0, description="Number of defaulted values")
    partial_count: int = Field(0, description="Number of partial calibrations")
    missing_base_weights: bool = Field(False, description="Whether _base_weights is missing")
    
    class Config:
        frozen = True


class ExecutionMetricsInfo(BaseModel):
    """Execution metrics collection information for manifest."""
    
    mode: ExecutionMetricsMode = Field(..., description="Metrics collection mode")
    estimated_phases: list[str] = Field(default_factory=list, description="Phases with estimated metrics")
    reason: Optional[str] = Field(None, description="Reason for estimation")
    
    class Config:
        frozen = True


class DocumentIdInfo(BaseModel):
    """Document identifier source information for manifest."""
    
    source: DocumentIdSource = Field(..., description="Source of document ID")
    document_id: str = Field(..., description="Actual document ID used")
    fallback_reason: Optional[str] = Field(None, description="Reason for fallback if source != METADATA")
    
    class Config:
        frozen = True


class ContradictionInfo(BaseModel):
    """Contradiction detection mode information for manifest."""
    
    mode: str = Field(..., description="Detection mode: 'full' or 'fallback'")
    module_available: bool = Field(..., description="Whether contradiction module is available")
    reason: Optional[str] = Field(None, description="Reason for fallback if mode == 'fallback'")
    
    class Config:
        frozen = True


class GraphMetricsInfo(BaseModel):
    """Graph metrics computation information for manifest."""
    
    computed: bool = Field(..., description="Whether graph metrics were computed")
    networkx_available: bool = Field(..., description="Whether NetworkX is available")
    reason: Optional[str] = Field(None, description="Reason for skip if not computed")
    
    class Config:
        frozen = True


class RuntimeManifest(BaseModel):
    """
    Complete runtime manifest tracking all degradations and fallbacks.
    
    This manifest is included in pipeline outputs to provide complete
    observability of runtime behavior and degradations.
    """
    
    runtime_mode: str = Field(..., description="Runtime mode (prod/dev/exploratory)")
    language_detection: Optional[LanguageDetectionInfo] = None
    segmentation: Optional[SegmentationInfo] = None
    calibration: Optional[CalibrationInfo] = None
    execution_metrics: Optional[ExecutionMetricsInfo] = None
    document_id: Optional[DocumentIdInfo] = None
    contradiction: Optional[ContradictionInfo] = None
    graph_metrics: Optional[GraphMetricsInfo] = None
    
    class Config:
        frozen = True
