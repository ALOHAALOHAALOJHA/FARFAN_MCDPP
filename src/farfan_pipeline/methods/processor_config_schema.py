"""Pydantic schema for ProcessorConfig validation."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ProcessorConfigSchema(BaseModel):
    """Validated configuration for PolicyAnalysisPipeline."""
    
    model_config = ConfigDict(
        frozen=True,
        strict=True,
        extra='forbid',
        validate_default=True,
    )
    
    # Processing settings
    preserve_document_structure: bool = Field(default=True, description="Preserve document structure during processing")
    enable_semantic_tagging: bool = Field(default=True, description="Enable semantic tagging of elements")
    confidence_threshold: float = Field(default=0.62, ge=0.0, le=1.0, description="Minimum confidence threshold for evidence")
    context_window_chars: int = Field(default=400, ge=100, le=2000, description="Context window size in characters")
    max_evidence_per_pattern: int = Field(default=5, ge=1, le=50, description="Maximum evidence items per pattern")
    enable_bayesian_scoring: bool = Field(default=True, description="Enable Bayesian scoring for evidence")
    utf8_normalization_form: str = Field(default="NFC", description="UTF-8 normalization form to use")
    
    # Advanced controls
    entropy_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Weight for entropy-based scoring")
    proximity_decay_rate: float = Field(default=0.15, ge=0.0, le=1.0, description="Decay rate for proximity scoring")
    min_sentence_length: int = Field(default=20, ge=10, le=200, description="Minimum sentence length to process")
    max_sentence_length: int = Field(default=500, ge=100, le=2000, description="Maximum sentence length to process")
    bayesian_prior_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Prior confidence for Bayesian scoring")
    bayesian_entropy_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Entropy weight for Bayesian scoring")
    
    # NLP settings
    preferred_spacy_model: str = Field(default="es_core_news_lg", description="Preferred spaCy model for NLP")
    preferred_embedding_model: str = Field(default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", description="Preferred embedding model")
    
    @field_validator('utf8_normalization_form')
    @classmethod
    def validate_utf8_normalization_form(cls, v: str) -> str:
        valid_forms = {"NFC", "NFD", "NFKC", "NFKD"}
        if v not in valid_forms: 
            raise ValueError(f"utf8_normalization_form must be one of {valid_forms}")
        return v
    
    @field_validator('preferred_spacy_model')
    @classmethod
    def validate_spacy_model(cls, v: str) -> str:
        valid_models = {"es_core_news_sm", "es_core_news_md", "es_core_news_lg", "es_dep_news_sm", "es_dep_news_md", "es_dep_news_lg"}
        if v not in valid_models: 
            raise ValueError(f"preferred_spacy_model must be one of {valid_models}")
        return v
    
    @model_validator(mode='after')
    def validate_config_coherence(self) -> 'ProcessorConfigSchema':
        """Validate configuration coherence."""
        if self.min_sentence_length >= self.max_sentence_length:
            raise ValueError("min_sentence_length must be less than max_sentence_length")
        
        if self.context_window_chars < 100:
            raise ValueError("context_window_chars must be at least 100")
            
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
            
        return self