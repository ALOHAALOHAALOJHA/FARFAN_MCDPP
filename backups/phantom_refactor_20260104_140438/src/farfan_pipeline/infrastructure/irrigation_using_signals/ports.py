"""
Signal Infrastructure Ports
============================

Defines Protocol interfaces (Ports) for signal infrastructure components.
These ports establish contracts that implementations must fulfill.

SPEC REFERENCE: SPEC_SIGNAL_NORMALIZATION_COMPREHENSIVE.md
- Section 4.2: SIG-PORTS-001 — Interfaz SignalRegistryPort normalizada

CRITICAL INVARIANTS:
1. Port signatures MUST match implementation signatures exactly
2. All methods that operate on questions require explicit question_id
3. Assembly/aggregation methods use level_id (MESO_1, MACRO_1, etc.)

Author: F.A.R.F.A.N Pipeline
Date: 2026-01-04
Version: 2.0.0 (Post-normalization)
"""

from __future__ import annotations

from typing import Any, Protocol


class QuestionnairePort(Protocol):
    """Minimal questionnaire contract for signal infrastructure.
    
    This port defines the minimal interface required for questionnaire
    data access by the signal infrastructure layer.
    
    Implementors:
        - canonic_questionnaire_central.questionnaire_monolith
        - Any questionnaire loader that provides micro_questions
    """

    @property
    def data(self) -> dict[str, Any]:
        """Raw questionnaire data dictionary."""
        ...

    @property
    def version(self) -> str:
        """Semantic version of the questionnaire."""
        ...

    @property
    def sha256(self) -> str:
        """SHA-256 hash of the questionnaire for integrity verification."""
        ...

    @property
    def micro_questions(self) -> list[dict[str, Any]]:
        """List of 300 micro-level questions (Q001-Q300)."""
        ...

    def __iter__(self) -> Any:  # pragma: no cover - structural typing only
        """Iterator over questionnaire elements."""
        ...


class SignalRegistryPort(Protocol):
    """Port for accessing signal packs from the questionnaire registry.
    
    This Protocol defines the contract for signal extraction and retrieval.
    Implementations must provide deterministic, reproducible signal packs.
    
    SPEC REFERENCE: SPEC_SIGNAL_NORMALIZATION_COMPREHENSIVE.md §4.2
    
    Method Signatures Contract:
    - get_chunking_signals(): Global, no parameters
    - get_micro_answering_signals(question_id): Per-question
    - get_validation_signals(question_id): Per-question  
    - get_assembly_signals(level): Per-level (MESO_1, MACRO_1, etc.)
    - get_scoring_signals(question_id): Per-question
    - get_source_hash(): Global, returns monolith hash
    - list_question_ids(): Global, returns all Q001-Q300
    
    Implementors:
        - QuestionnaireSignalRegistry (SISAS/signal_registry.py)
    
    Raises:
        QuestionNotFoundError: When question_id is invalid
        InvalidLevelError: When assembly level is invalid
        SignalExtractionError: When signal extraction fails
    """

    def get_chunking_signals(self) -> Any:
        """Get signals for Smart Policy Chunking (global).
        
        Returns:
            ChunkingSignalPack with section patterns, weights, and config.
        """
        ...

    def get_micro_answering_signals(self, question_id: str) -> Any:
        """Get signals for Micro Answering for a specific question.
        
        Args:
            question_id: Question ID in format Q001-Q300.
        
        Returns:
            MicroAnsweringSignalPack with patterns, semantic expansions,
            context requirements, and evidence boost factors.
        """
        ...

    def get_validation_signals(self, question_id: str) -> Any:
        """Get validation signals for a specific question.
        
        Args:
            question_id: Question ID in format Q001-Q300.
        
        Returns:
            ValidationSignalPack with validation rules, contracts,
            and threshold configurations.
        
        Note:
            CORRECTED from original 'level: str' parameter.
            See SPEC §4.2 SIG-PORTS-001.
        """
        ...

    def get_assembly_signals(self, level: str) -> Any:
        """Get signals for Response Assembly at specified aggregation level.
        
        Args:
            level: Assembly level identifier. Valid values:
                - MESO_1, MESO_2, MESO_3, MESO_4 (cluster-level)
                - MACRO_1 (holistic plan-level)
        
        Returns:
            AssemblySignalPack with aggregation methods, cluster mappings,
            and weight configurations.
        """
        ...

    def get_scoring_signals(self, question_id: str) -> Any:
        """Get scoring signals for a specific question.
        
        Args:
            question_id: Question ID in format Q001-Q300.
        
        Returns:
            ScoringSignalPack with scoring modality, thresholds,
            quality levels, and aggregation strategy.
        
        Note:
            CORRECTED from original parameterless signature.
            See SPEC §4.2 SIG-PORTS-001.
        """
        ...

    def get_source_hash(self) -> str:
        """Get the SHA-256 hash of the source monolith.
        
        This hash is used for:
        - Cache invalidation when monolith changes
        - Signal pack identity computation
        - Determinism verification
        
        Returns:
            64-character hexadecimal SHA-256 hash string.
        """
        ...

    def list_question_ids(self) -> list[str]:
        """List all available question IDs.
        
        Returns:
            List of question IDs from Q001 to Q300.
        """
        ...
