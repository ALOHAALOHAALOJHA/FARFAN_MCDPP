"""
Phase One:  CPP Ingestion & Preprocessing.

This module exports the public API for Phase 1 of the FARFAN pipeline. 

Exports:
    - Phase1Executor: Main execution class
    - SmartChunk, Chunk:  Data models
    - TruncationAudit:  Audit records
    - StreamingPDFExtractor: PDF extraction
    - Constants: All configuration values

Owner: farfan_pipeline. phases.Phase_one
Version: 1.0.0
"""

# Core executor
from .phase1_20_00_cpp_ingestion import Phase1MissionContract as Phase1Executor

# Data models
from .phase1_10_00_models import (
    SmartChunk,
    Chunk,
    LanguageData,
    PreprocessedDoc,
    StructureData,
    KnowledgeGraph,
    KGNode,
    KGEdge,
    CausalChains,
    IntegratedCausal,
    Arguments,
    Temporal,
    Discourse,
    Strategic,
    ValidationResult,
)

# Primitives
from .primitives.truncation_audit import TruncationAudit
from .primitives.streaming_extractor import StreamingPDFExtractor

# Thread-safe utilities
from .thread_safe_results import ThreadSafeResults

# Constants
from .PHASE_1_CONSTANTS import (
    PDF_EXTRACTION_CHAR_LIMIT,
    SEMANTIC_SCORE_MAX_EXPECTED,
    ASSIGNMENT_METHOD_SEMANTIC,
    ASSIGNMENT_METHOD_FALLBACK,
    VALID_ASSIGNMENT_METHODS,
    CHUNK_ID_PATTERN,
    POLICY_AREA_COUNT,
    DIMENSION_COUNT,
    TOTAL_CHUNK_COMBINATIONS,
    SUBPHASE_COUNT,
    PHASE1_LOGGER_NAME,
    RANDOM_SEED,
)

__all__ = [
    # Executor
    'Phase1Executor',
    # Models
    'SmartChunk',
    'Chunk',
    'LanguageData',
    'PreprocessedDoc',
    'StructureData',
    'KnowledgeGraph',
    'KGNode',
    'KGEdge',
    'CausalChains',
    'IntegratedCausal',
    'Arguments',
    'Temporal',
    'Discourse',
    'Strategic',
    'ValidationResult',
    # Primitives
    'TruncationAudit',
    'StreamingPDFExtractor',
    # Utilities
    'ThreadSafeResults',
    # Constants
    'PDF_EXTRACTION_CHAR_LIMIT',
    'SEMANTIC_SCORE_MAX_EXPECTED',
    'ASSIGNMENT_METHOD_SEMANTIC',
    'ASSIGNMENT_METHOD_FALLBACK',
    'VALID_ASSIGNMENT_METHODS',
    'CHUNK_ID_PATTERN',
    'POLICY_AREA_COUNT',
    'DIMENSION_COUNT',
    'TOTAL_CHUNK_COMBINATIONS',
    'SUBPHASE_COUNT',
    'PHASE1_LOGGER_NAME',
    'RANDOM_SEED',
]