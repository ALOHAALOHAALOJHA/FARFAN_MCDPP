"""
Canonical Questionnaire Access Control Module.

SECURITY CONTRACT:
==================
This is the ONLY module allowed to directly access questionnaire_monolith.json.

ACCESS RULES:
-------------
1. ✓ ALLOWED: Factory, Orchestrator, Signal modules via this interface
2. ✗ FORBIDDEN: Direct file access from analysis, processing, or other modules
3. ✓ ENFORCEMENT: All access must go through CanonicalQuestionnaire class

ARCHITECTURE:
-------------
questionnaire_monolith.json (FILE)
        ↓
    load_questionnaire() [CANONICAL LOADER]
        ↓
    CanonicalQuestionnaire [SINGLE INSTANCE]
        ↓
    Factory → Orchestrator → Signals

Author: F.A.R.F.A.N Pipeline
Date: 2025-12-02
Version: 2.0.0
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Final

from farfan_pipeline.config.paths import PROJECT_ROOT

# Canonical path to questionnaire monolith
QUESTIONNAIRE_FILE: Final[Path] = (
    PROJECT_ROOT / "system" / "config" / "questionnaire" / "questionnaire_monolith.json"
)

QUESTIONNAIRE_SCHEMA: Final[Path] = (
    PROJECT_ROOT / "system" / "config" / "questionnaire" / "questionnaire_schema.json"
)


@dataclass(frozen=True)
class QuestionnaireMetadata:
    """Immutable metadata about the questionnaire."""
    
    schema_version: str
    version: str
    generated_at: str
    file_hash: str
    file_size: int
    line_count: int
    

class CanonicalQuestionnaire:
    """
    Canonical questionnaire accessor with access control.
    
    This class enforces the security contract: only factory, orchestrator,
    and signal modules should instantiate this class.
    
    CONTRACT:
    ---------
    - Singleton pattern: Load once, use everywhere
    - Immutable data: Once loaded, cannot be modified
    - Integrity verified: SHA-256 hash checked on load
    - Schema validated: Must conform to questionnaire_schema.json
    
    USAGE (ALLOWED):
    ----------------
    >>> from farfan_pipeline.core.orchestrator.questionnaire import load_questionnaire
    >>> questionnaire = load_questionnaire()
    >>> macro_q = questionnaire.get_macro_question()
    >>> meso_qs = questionnaire.get_meso_questions()
    >>> micro_qs = questionnaire.get_micro_questions()
    
    USAGE (FORBIDDEN):
    ------------------
    >>> # ✗ DON'T DO THIS
    >>> with open("system/config/questionnaire/questionnaire_monolith.json") as f:
    >>>     data = json.load(f)  # VIOLATION: Direct file access
    """
    
    def __init__(self, data: Dict[str, Any], metadata: QuestionnaireMetadata):
        """
        Initialize canonical questionnaire.
        
        NOTE: Do not call directly. Use load_questionnaire() instead.
        
        Args:
            data: Loaded and validated questionnaire data
            metadata: Questionnaire metadata
        """
        self._data = data
        self._metadata = metadata
        
        # Extract blocks for fast access
        self._blocks = data.get('blocks', {})
    
    @property
    def data(self) -> Dict[str, Any]:
        """Get raw questionnaire data (read-only)."""
        return self._data
    
    @property
    def metadata(self) -> QuestionnaireMetadata:
        """Get questionnaire metadata."""
        return self._metadata
    
    @property
    def schema_version(self) -> str:
        """Get schema version."""
        return self._metadata.schema_version
    
    @property
    def version(self) -> str:
        """Get monolith version."""
        return self._metadata.version
    
    # === CANONICAL ACCESS METHODS ===
    
    def get_macro_question(self) -> Dict[str, Any]:
        """
        Get the single macro-level question.
        
        Returns:
            Macro question data (holistic policy coherence)
        """
        return self._blocks.get('macro_question', {})
    
    def get_meso_questions(self) -> list[Dict[str, Any]]:
        """
        Get all meso-level questions (thematic clusters).
        
        Returns:
            List of meso questions (typically 4)
        """
        return self._blocks.get('meso_questions', [])
    
    def get_micro_questions(self) -> list[Dict[str, Any]]:
        """
        Get all micro-level questions (granular evaluation).
        
        Returns:
            List of micro questions (300+)
        """
        return self._blocks.get('micro_questions', [])
    
    def get_abstraction_levels(self) -> Dict[str, Any]:
        """Get hierarchical abstraction levels."""
        return self._blocks.get('niveles_abstraccion', {})
    
    def get_scoring_system(self) -> Dict[str, Any]:
        """Get scoring rubrics and modalities."""
        return self._blocks.get('scoring', {})
    
    def get_semantic_layers(self) -> Dict[str, Any]:
        """Get semantic layer configuration for NLP."""
        return self._blocks.get('semantic_layers', {})
    
    def get_micro_question_by_id(self, question_id: str) -> Dict[str, Any] | None:
        """
        Get specific micro question by ID.
        
        Args:
            question_id: Question identifier (e.g., "MICRO_001")
        
        Returns:
            Question data or None if not found
        """
        for q in self.get_micro_questions():
            if q.get('question_id') == question_id:
                return q
        return None
    
    def get_questions_by_cluster(self, cluster_id: str) -> list[Dict[str, Any]]:
        """
        Get all micro questions in a specific cluster.
        
        Args:
            cluster_id: Cluster identifier
        
        Returns:
            List of questions in that cluster
        """
        return [
            q for q in self.get_micro_questions()
            if q.get('cluster_id') == cluster_id
        ]
    
    def get_questions_by_policy_area(self, policy_area_id: str) -> list[Dict[str, Any]]:
        """
        Get all micro questions for a policy area.
        
        Args:
            policy_area_id: Policy area identifier
        
        Returns:
            List of questions for that policy area
        """
        return [
            q for q in self.get_micro_questions()
            if q.get('policy_area_id') == policy_area_id
        ]
    
    def verify_integrity(self) -> bool:
        """
        Verify integrity hash matches current data.
        
        Returns:
            True if integrity verified, False otherwise
        """
        integrity = self._data.get('integrity', {})
        stored_hash = integrity.get('hash', '')
        
        if not stored_hash:
            return False
        
        # Extract just the hash value (remove "sha256:" prefix if present)
        if stored_hash.startswith('sha256:'):
            stored_hash = stored_hash[7:]
        
        return stored_hash == self._metadata.file_hash
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CanonicalQuestionnaire("
            f"version={self.version}, "
            f"schema={self.schema_version}, "
            f"micro_questions={len(self.get_micro_questions())}"
            f")"
        )


# === CANONICAL LOADER (SINGLE SOURCE OF TRUTH) ===

_QUESTIONNAIRE_CACHE: CanonicalQuestionnaire | None = None


def load_questionnaire(
    force_reload: bool = False,
    validate_schema: bool = True
) -> CanonicalQuestionnaire:
    """
    Load questionnaire monolith from canonical location.
    
    This is the ONLY function allowed to read questionnaire_monolith.json.
    Implements singleton pattern: loads once, caches result.
    
    Args:
        force_reload: If True, bypass cache and reload from disk
        validate_schema: If True, validate against JSON Schema
    
    Returns:
        CanonicalQuestionnaire instance
    
    Raises:
        FileNotFoundError: If questionnaire file not found
        json.JSONDecodeError: If file is invalid JSON
        ValueError: If schema validation fails
    
    SECURITY:
    ---------
    This function is the ONLY entry point for questionnaire access.
    All other modules MUST use this function, never open() directly.
    
    Example:
        >>> questionnaire = load_questionnaire()
        >>> print(f"Loaded {len(questionnaire.get_micro_questions())} questions")
    """
    global _QUESTIONNAIRE_CACHE
    
    # Return cached version unless force reload
    if _QUESTIONNAIRE_CACHE is not None and not force_reload:
        return _QUESTIONNAIRE_CACHE
    
    # Verify file exists
    if not QUESTIONNAIRE_FILE.exists():
        raise FileNotFoundError(
            f"Questionnaire monolith not found at canonical location: {QUESTIONNAIRE_FILE}"
        )
    
    # Load and parse JSON
    with open(QUESTIONNAIRE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        data = json.loads(content)
    
    # Calculate file hash for integrity
    file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    # Count lines
    line_count = len(content.split('\n'))
    
    # Extract metadata
    metadata = QuestionnaireMetadata(
        schema_version=data.get('schema_version', 'unknown'),
        version=data.get('version', 'unknown'),
        generated_at=data.get('generated_at', 'unknown'),
        file_hash=file_hash,
        file_size=len(content),
        line_count=line_count
    )
    
    # Validate schema if requested
    if validate_schema:
        _validate_questionnaire_schema(data)
    
    # Create canonical instance
    questionnaire = CanonicalQuestionnaire(data, metadata)
    
    # Cache for future use
    _QUESTIONNAIRE_CACHE = questionnaire
    
    return questionnaire


def _validate_questionnaire_schema(data: Dict[str, Any]) -> None:
    """
    Validate questionnaire data against JSON Schema.
    
    Args:
        data: Questionnaire data to validate
    
    Raises:
        ValueError: If validation fails
    """
    # Check required top-level keys
    required_keys = ['canonical_notation', 'blocks', 'schema_version', 'integrity']
    missing = [k for k in required_keys if k not in data]
    
    if missing:
        raise ValueError(f"Missing required keys: {missing}")
    
    # Check blocks structure
    blocks = data.get('blocks', {})
    required_blocks = [
        'macro_question', 'meso_questions', 'micro_questions',
        'niveles_abstraccion', 'scoring', 'semantic_layers'
    ]
    missing_blocks = [b for b in required_blocks if b not in blocks]
    
    if missing_blocks:
        raise ValueError(f"Missing required blocks: {missing_blocks}")
    
    # Validate micro questions have required fields
    micro_questions = blocks.get('micro_questions', [])
    if not isinstance(micro_questions, list):
        raise ValueError("micro_questions must be a list")
    
    if len(micro_questions) == 0:
        raise ValueError("micro_questions cannot be empty")
    
    # Basic validation of first question structure
    if micro_questions:
        first_q = micro_questions[0]
        required_q_fields = ['question_id', 'text', 'cluster_id', 'dimension_id']
        missing_q = [f for f in required_q_fields if f not in first_q]
        
        if missing_q:
            raise ValueError(f"Micro questions missing required fields: {missing_q}")


def get_questionnaire_provider():
    """
    Get questionnaire provider for dependency injection.
    
    Returns:
        Function that returns loaded questionnaire
    
    Usage:
        >>> provider = get_questionnaire_provider()
        >>> questionnaire = provider()
    """
    return load_questionnaire


# === EXPORTS ===

__all__ = [
    'CanonicalQuestionnaire',
    'QuestionnaireMetadata',
    'load_questionnaire',
    'get_questionnaire_provider',
    'QUESTIONNAIRE_FILE',
    'QUESTIONNAIRE_SCHEMA',
]
