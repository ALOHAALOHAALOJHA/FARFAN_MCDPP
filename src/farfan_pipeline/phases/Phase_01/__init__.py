"""
Phase One: CPP Ingestion & Preprocessing.

This module exports the public API for Phase 1 of the FARFAN pipeline.

Exports:
    - Phase1Executor: Main execution class
    - SmartChunk, Chunk: Data models
    - TruncationAudit: Audit records
    - StreamingPDFExtractor: PDF extraction
    - Constants: All configuration values
    - QuestionnaireMap, load_questionnaire_map: Question-level mapping (v2.0)
    - execute_sp4_question_aware: Question-aware segmentation (v2.0)

Owner: farfan_pipeline.phases.Phase_01
Version: 2.0.0 - Question-Aware Architecture
"""

# Core executor (may have optional dependencies)
try:
    from .phase1_13_00_cpp_ingestion import Phase1MissionContract as Phase1Executor

    PHASE1_EXECUTOR_AVAILABLE = True
except ImportError:
    Phase1Executor = None
    PHASE1_EXECUTOR_AVAILABLE = False

# Data models
from .phase1_03_00_models import (
    Arguments,
    CausalChains,
    Chunk,
    Discourse,
    IntegratedCausal,
    KGEdge,
    KGNode,
    KnowledgeGraph,
    LanguageData,
    PreprocessedDoc,
    SmartChunk,
    Strategic,
    StructureData,
    Temporal,
    ValidationResult,
)

# Thread-safe utilities
from .phase1_05_00_thread_safe_results import ThreadSafeResults

# Constants
from .PHASE_1_CONSTANTS import (
    ASSIGNMENT_METHOD_FALLBACK,
    ASSIGNMENT_METHOD_SEMANTIC,
    CHUNK_ID_PATTERN,
    DIMENSION_COUNT,
    PDF_EXTRACTION_CHAR_LIMIT,
    PHASE1_LOGGER_NAME,
    POLICY_AREA_COUNT,
    RANDOM_SEED,
    SEMANTIC_SCORE_MAX_EXPECTED,
    SUBPHASE_COUNT,
    TOTAL_CHUNK_COMBINATIONS,
    VALID_ASSIGNMENT_METHODS,
)
from .primitives import StreamingPDFExtractor

# Primitives
from .primitives import TruncationAudit

# Question-aware architecture (v2.0) - NEW
try:
    from .phase1_06_00_questionnaire_mapper import (
        NUM_DIMENSIONS,
        NUM_POLICY_AREAS,
        QUESTIONS_PER_DIMENSION,
        TOTAL_QUESTIONS,
        QuestionnaireMap,
        QuestionSpec,
        create_chunk_id_for_question,
        invoke_method_set,
        load_questionnaire_map,
        parse_question_id,
        verify_expected_elements,
    )

    QUESTIONNAIRE_MAPPER_AVAILABLE = True
except ImportError:
    QuestionSpec = None
    QuestionnaireMap = None
    load_questionnaire_map = None
    invoke_method_set = None
    verify_expected_elements = None
    create_chunk_id_for_question = None
    parse_question_id = None
    TOTAL_QUESTIONS = 300
    QUESTIONS_PER_DIMENSION = 5
    NUM_POLICY_AREAS = 10
    NUM_DIMENSIONS = 6
    QUESTIONNAIRE_MAPPER_AVAILABLE = False

try:
    from .phase1_07_00_sp4_question_aware import (
        TOTAL_CHUNK_COMBINATIONS as SP4_TOTAL_CHUNKS,
    )
    from .phase1_07_00_sp4_question_aware import (
        execute_sp4_question_aware,
    )

    SP4_QUESTION_AWARE_AVAILABLE = True
except ImportError:
    execute_sp4_question_aware = None
    SP4_TOTAL_CHUNKS = 300
    SP4_QUESTION_AWARE_AVAILABLE = False

# PDM Structural Recognition (PDM-2025.1) - NEW
try:
    from .phase1_12_01_pdm_integration import (
        PDMStructuralAnalyzer,
        PDMMetadataAssigner,
        assign_pdm_metadata_to_chunks,
        enhance_sp2_with_pdm,
    )

    PDM_INTEGRATION_AVAILABLE = True
except ImportError:
    PDMStructuralAnalyzer = None
    PDMMetadataAssigner = None
    assign_pdm_metadata_to_chunks = None
    enhance_sp2_with_pdm = None
    PDM_INTEGRATION_AVAILABLE = False

# Colombian PDM Enhancement (Phase 1 v2.0) - DEFAULT BEHAVIOR
try:
    from .phase1_07_01_colombian_pdm_enhancer import (
        ColombianPDMChunkEnhancer,
        ColombianPDMPatterns,
        PDMChunkEnhancement,
        AlreadyChunkedError,
        check_if_already_chunked,
        assert_not_chunked,
    )

    COLOMBIAN_PDM_ENHANCER_AVAILABLE = True
except ImportError:
    ColombianPDMChunkEnhancer = None
    ColombianPDMPatterns = None
    PDMChunkEnhancement = None
    AlreadyChunkedError = None
    check_if_already_chunked = None
    assert_not_chunked = None
    COLOMBIAN_PDM_ENHANCER_AVAILABLE = False

__all__ = [
    # Executor
    "Phase1Executor",
    # Models
    "SmartChunk",
    "Chunk",
    "LanguageData",
    "PreprocessedDoc",
    "StructureData",
    "KnowledgeGraph",
    "KGNode",
    "KGEdge",
    "CausalChains",
    "IntegratedCausal",
    "Arguments",
    "Temporal",
    "Discourse",
    "Strategic",
    "ValidationResult",
    # Primitives
    "TruncationAudit",
    "StreamingPDFExtractor",
    # Utilities
    "ThreadSafeResults",
    # Constants
    "PDF_EXTRACTION_CHAR_LIMIT",
    "SEMANTIC_SCORE_MAX_EXPECTED",
    "ASSIGNMENT_METHOD_SEMANTIC",
    "ASSIGNMENT_METHOD_FALLBACK",
    "VALID_ASSIGNMENT_METHODS",
    "CHUNK_ID_PATTERN",
    "POLICY_AREA_COUNT",
    "DIMENSION_COUNT",
    "TOTAL_CHUNK_COMBINATIONS",
    "SUBPHASE_COUNT",
    "PHASE1_LOGGER_NAME",
    "RANDOM_SEED",
    # Question-aware architecture (v2.0) - NEW
    "QuestionSpec",
    "QuestionnaireMap",
    "load_questionnaire_map",
    "invoke_method_set",
    "verify_expected_elements",
    "create_chunk_id_for_question",
    "parse_question_id",
    "TOTAL_QUESTIONS",
    "QUESTIONS_PER_DIMENSION",
    "NUM_POLICY_AREAS",
    "NUM_DIMENSIONS",
    "execute_sp4_question_aware",
    "QUESTIONNAIRE_MAPPER_AVAILABLE",
    "SP4_QUESTION_AWARE_AVAILABLE",
    # PDM Structural Recognition (PDM-2025.1) - NEW
    "PDMStructuralAnalyzer",
    "PDMMetadataAssigner",
    "assign_pdm_metadata_to_chunks",
    "enhance_sp2_with_pdm",
    "PDM_INTEGRATION_AVAILABLE",
    # Colombian PDM Enhancement (v2.0) - DEFAULT BEHAVIOR
    "ColombianPDMChunkEnhancer",
    "ColombianPDMPatterns",
    "PDMChunkEnhancement",
    "AlreadyChunkedError",
    "check_if_already_chunked",
    "assert_not_chunked",
    "COLOMBIAN_PDM_ENHANCER_AVAILABLE",
]
