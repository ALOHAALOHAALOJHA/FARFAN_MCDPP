"""Signal Consumption Tracking and Verification

This module provides cryptographic proof that signals are actually consumed
during execution, not just loaded into memory.

Key Features:
- Hash chain tracking of pattern matches
- Consumption proof generation for each executor
- Merkle tree verification of pattern origin
- Deterministic proof generation for reproducibility
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, Sequence

if TYPE_CHECKING:
    from pathlib import Path

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class SignalConsumptionProof:
    """Cryptographic proof that signals were consumed during execution.

    This class tracks every pattern match and generates a verifiable hash chain
    that proves signal patterns were actually used, not just loaded.

    Attributes:
        executor_id: Unique identifier for the executor
        question_id: Question ID being processed
        policy_area: Policy area of the question
        consumed_patterns: List of (pattern, match_hash) tuples
        proof_chain: Hash chain linking all matches
        timestamp: Unix timestamp of execution
    """

    executor_id: str
    question_id: str
    policy_area: str
    consumed_patterns: list[tuple[str, str]] = field(default_factory=list)
    proof_chain: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def record_pattern_match(self, pattern: str, text_segment: str) -> None:
        """Record that a pattern matched text, generating proof.

        Args:
            pattern: The regex pattern that matched
            text_segment: The text segment that matched (truncated to 100 chars)
        """
        # Truncate text segment for proof size
        text_segment = text_segment[:100] if text_segment else ""

        # Generate match hash
        match_hash = hashlib.sha256(
            f"{pattern}|{text_segment}".encode()
        ).hexdigest()

        self.consumed_patterns.append((pattern, match_hash))

        # Update proof chain
        prev_hash = self.proof_chain[-1] if self.proof_chain else "0" * 64
        new_hash = hashlib.sha256(
            f"{prev_hash}|{match_hash}".encode()
        ).hexdigest()
        self.proof_chain.append(new_hash)

        logger.debug(
            "pattern_match_recorded",
            pattern=pattern[:50],
            match_hash=match_hash[:16],
            chain_length=len(self.proof_chain),
        )

    def get_consumption_proof(self) -> dict[str, Any]:
        """Return verifiable proof of signal consumption.

        Returns:
            Dictionary with proof data including:
            - executor_id, question_id, policy_area
            - patterns_consumed count
            - proof_chain_head (final hash in chain)
            - consumed_hashes (first 10 for verification)
            - timestamp
        """
        return {
            'executor_id': self.executor_id,
            'question_id': self.question_id,
            'policy_area': self.policy_area,
            'patterns_consumed': len(self.consumed_patterns),
            'proof_chain_head': self.proof_chain[-1] if self.proof_chain else None,
            'proof_chain_length': len(self.proof_chain),
            'consumed_hashes': [h for _, h in self.consumed_patterns[:10]],
            'timestamp': self.timestamp,
        }

    def save_to_file(self, output_dir: Path) -> Path:
        """Save consumption proof to JSON file.

        Args:
            output_dir: Directory to save proof files

        Returns:
            Path to the saved proof file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        proof_file = output_dir / f"{self.question_id}.json"

        with open(proof_file, 'w', encoding='utf-8') as f:
            json.dump(self.get_consumption_proof(), f, indent=2)

        logger.info(
            "consumption_proof_saved",
            question_id=self.question_id,
            proof_file=str(proof_file),
            patterns_consumed=len(self.consumed_patterns),
        )

        return proof_file


def build_merkle_tree(items: list[str]) -> str:
    """Build a simple Merkle tree and return the root hash.

    This is a simplified Merkle tree for verification purposes.
    For production, consider using a full Merkle tree library.

    Args:
        items: List of items to hash

    Returns:
        Hex string of root hash
    """
    if not items:
        return hashlib.sha256(b'').hexdigest()

    # Sort for determinism
    items = sorted(items)

    # Hash each item
    hashes = [
        hashlib.sha256(item.encode('utf-8')).hexdigest()
        for item in items
    ]

    # Build tree bottom-up
    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])  # Duplicate last hash if odd

        next_level = []
        for i in range(0, len(hashes), 2):
            combined = f"{hashes[i]}|{hashes[i+1]}"
            next_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
            next_level.append(next_hash)

        hashes = next_level

    return hashes[0]


@dataclass(frozen=True)
class SignalManifest:
    """Cryptographically verifiable signal extraction manifest.

    This manifest provides Merkle roots for all patterns extracted from
    the questionnaire, enabling verification that patterns used during
    execution actually came from the source file.

    Attributes:
        policy_area: Policy area code (e.g., PA01)
        pattern_count: Total number of patterns
        pattern_merkle_root: Merkle root of all patterns
        indicator_merkle_root: Merkle root of indicator patterns
        entity_merkle_root: Merkle root of entity patterns
        extraction_timestamp: Unix timestamp (fixed for determinism)
        source_file_hash: SHA256 of questionnaire_monolith.json
    """

    policy_area: str
    pattern_count: int
    pattern_merkle_root: str
    indicator_merkle_root: str
    entity_merkle_root: str
    extraction_timestamp: float
    source_file_hash: str

    def to_dict(self) -> dict[str, Any]:
        """Convert manifest to dictionary for serialization."""
        return {
            'policy_area': self.policy_area,
            'pattern_count': self.pattern_count,
            'pattern_merkle_root': self.pattern_merkle_root,
            'indicator_merkle_root': self.indicator_merkle_root,
            'entity_merkle_root': self.entity_merkle_root,
            'extraction_timestamp': self.extraction_timestamp,
            'source_file_hash': self.source_file_hash,
        }


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file.

    Args:
        file_path: Path to file

    Returns:
        Hex string of SHA256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_signal_manifests(
    questionnaire_data: dict[str, Any],
    source_file_path: Path | None = None,
) -> dict[str, SignalManifest]:
    """Generate signal manifests with Merkle roots for verification.

    Args:
        questionnaire_data: Parsed questionnaire monolith data
        source_file_path: Optional path to source file for hashing

    Returns:
        Dictionary mapping policy area codes to SignalManifest objects
    """
    # Compute source file hash if path provided
    if source_file_path and source_file_path.exists():
        source_hash = compute_file_hash(source_file_path)
    else:
        # Fallback: hash the data itself
        data_str = json.dumps(questionnaire_data, sort_keys=True)
        source_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    # Fixed timestamp for determinism
    timestamp = 1731258152.0

    manifests = {}
    questions = questionnaire_data.get('blocks', {}).get('micro_questions', [])

    # Group patterns by policy area
    patterns_by_pa: dict[str, dict[str, list[str]]] = {}

    for question in questions:
        pa = question.get('policy_area_id', 'PA01')
        if pa not in patterns_by_pa:
            patterns_by_pa[pa] = {
                'all': [],
                'indicators': [],
                'entities': [],
            }

        for pattern_obj in question.get('patterns', []):
            pattern_str = pattern_obj.get('pattern', '')
            category = pattern_obj.get('category', '')

            if pattern_str:
                patterns_by_pa[pa]['all'].append(pattern_str)

                if category == 'INDICADOR':
                    patterns_by_pa[pa]['indicators'].append(pattern_str)
                elif category == 'FUENTE_OFICIAL':
                    patterns_by_pa[pa]['entities'].append(pattern_str)

    # Build manifests
    for pa, patterns in patterns_by_pa.items():
        manifests[pa] = SignalManifest(
            policy_area=pa,
            pattern_count=len(patterns['all']),
            pattern_merkle_root=build_merkle_tree(patterns['all']),
            indicator_merkle_root=build_merkle_tree(patterns['indicators']),
            entity_merkle_root=build_merkle_tree(patterns['entities']),
            extraction_timestamp=timestamp,
            source_file_hash=source_hash,
        )

        logger.info(
            "signal_manifest_generated",
            policy_area=pa,
            pattern_count=len(patterns['all']),
            merkle_root=manifests[pa].pattern_merkle_root[:16],
        )

    return manifests


# ============================================================================
# QUESTIONNAIRE ACCESS AUDIT - Medición de Utilización
# ============================================================================

class AccessLevel(Enum):
    """Nivel de acceso al cuestionario según arquitectura de 3 niveles."""
    FACTORY = 1      # I/O total - Solo AnalysisPipelineFactory
    ORCHESTRATOR = 2  # Parcial recurrente - SISAS, ResourceProvider
    CONSUMER = 3      # Granular scoped - Ejecutores, Evidence*


@dataclass(frozen=True)
class AccessRecord:
    """Registro inmutable de un acceso al cuestionario."""
    timestamp: str
    level: AccessLevel
    accessor_module: str   # __name__ del módulo
    accessor_class: str    # Nombre de clase
    accessor_method: str   # Nombre de método
    accessed_block: str    # "dimensions", "micro_questions", "patterns", etc.
    accessed_keys: tuple[str, ...]  # IDs específicos (inmutable)
    scope_filter: str | None = None  # Filtro aplicado

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level.name,
            "accessor": f"{self.accessor_module}.{self.accessor_class}.{self.accessor_method}",
            "block": self.accessed_block,
            "keys": list(self.accessed_keys),
            "scope_filter": self.scope_filter,
        }


@dataclass
class QuestionnaireAccessAudit:
    """
    Auditor de acceso al cuestionario con métricas de utilización.

    PROPÓSITO:
    1. Medir qué porción del cuestionario se consume
    2. Detectar violaciones de nivel arquitectónico
    3. Identificar patrones/preguntas no utilizados
    4. Generar reporte de trazabilidad

    INVARIANTES DEL MONOLITO:
    - 300 micro preguntas (6 dims × 5 preguntas × 10 PAs)
    - 4 meso preguntas
    - 1 macro pregunta
    - 6 dimensiones (DIM01-DIM06)
    - 10 policy areas (PA01-PA10)
    """

    # Constantes del monolito
    TOTAL_MICRO_QUESTIONS: ClassVar[int] = 300
    TOTAL_MESO_QUESTIONS: ClassVar[int] = 4
    TOTAL_MACRO_QUESTIONS: ClassVar[int] = 1
    TOTAL_DIMENSIONS: ClassVar[int] = 6
    TOTAL_POLICY_AREAS: ClassVar[int] = 10

    # Estado mutable (privado)
    _access_log: list[AccessRecord] = field(default_factory=list)
    _accessed_questions: set[str] = field(default_factory=set)
    _accessed_patterns: set[str] = field(default_factory=set)
    _accessed_elements: set[str] = field(default_factory=set)
    _accessed_policy_areas: set[str] = field(default_factory=set)
    _accessed_dimensions: set[str] = field(default_factory=set)
    _violations: list[dict[str, Any]] = field(default_factory=list)

    def record_access(
        self,
        level: AccessLevel,
        accessor_module: str,
        accessor_class: str,
        accessor_method: str,
        accessed_block: str,
        accessed_keys: Sequence[str],
        scope_filter: str | None = None,
    ) -> None:
        """Registra un acceso al cuestionario."""
        record = AccessRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level,
            accessor_module=accessor_module,
            accessor_class=accessor_class,
            accessor_method=accessor_method,
            accessed_block=accessed_block,
            accessed_keys=tuple(accessed_keys),
            scope_filter=scope_filter,
        )
        self._access_log.append(record)

        # Actualizar conjuntos de tracking
        if accessed_block == "micro_questions":
            self._accessed_questions.update(accessed_keys)
        elif accessed_block == "patterns":
            self._accessed_patterns.update(accessed_keys)
        elif accessed_block == "expected_elements":
            self._accessed_elements.update(accessed_keys)
        elif accessed_block == "policy_areas":
            self._accessed_policy_areas.update(accessed_keys)
        elif accessed_block == "dimensions":
            self._accessed_dimensions.update(accessed_keys)

    def record_violation(
        self,
        violation_type: str,
        accessor: str,
        expected_level: AccessLevel,
        actual_level: AccessLevel,
        details: str,
    ) -> None:
        """Registra una violación de nivel arquitectónico."""
        self._violations.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": violation_type,
            "accessor": accessor,
            "expected_level": expected_level.name,
            "actual_level": actual_level.name,
            "details": details,
        })

    def get_utilization_report(self) -> dict[str, Any]:
        """Genera reporte de utilización del cuestionario."""
        return {
            "micro_questions": {
                "accessed": len(self._accessed_questions),
                "total": self.TOTAL_MICRO_QUESTIONS,
                "percentage": round(
                    len(self._accessed_questions) / self.TOTAL_MICRO_QUESTIONS * 100, 2
                ),
                "ids": sorted(self._accessed_questions),
            },
            "policy_areas": {
                "accessed": len(self._accessed_policy_areas),
                "total": self.TOTAL_POLICY_AREAS,
                "percentage": round(
                    len(self._accessed_policy_areas) / self.TOTAL_POLICY_AREAS * 100, 2
                ),
                "ids": sorted(self._accessed_policy_areas),
            },
            "dimensions": {
                "accessed": len(self._accessed_dimensions),
                "total": self.TOTAL_DIMENSIONS,
                "percentage": round(
                    len(self._accessed_dimensions) / self.TOTAL_DIMENSIONS * 100, 2
                ),
                "ids": sorted(self._accessed_dimensions),
            },
            "patterns_accessed": len(self._accessed_patterns),
            "elements_accessed": len(self._accessed_elements),
            "total_access_events": len(self._access_log),
            "access_by_level": self._count_by_level(),
            "violations_count": len(self._violations),
            "violations": self._violations,
        }

    def _count_by_level(self) -> dict[str, int]:
        """Cuenta accesos por nivel arquitectónico."""
        counts = {level.name: 0 for level in AccessLevel}
        for record in self._access_log:
            counts[record.level.name] += 1
        return counts

    def export_audit_log(self) -> list[dict[str, Any]]:
        """Exporta log de auditoría completo."""
        return [record.to_dict() for record in self._access_log]

    def reset(self) -> None:
        """Resetea el auditor (solo para testing)."""
        self._access_log.clear()
        self._accessed_questions.clear()
        self._accessed_patterns.clear()
        self._accessed_elements.clear()
        self._accessed_policy_areas.clear()
        self._accessed_dimensions.clear()
        self._violations.clear()


# Singleton global para auditoría (inicializado por Factory)
_global_access_audit: QuestionnaireAccessAudit | None = None


def get_access_audit() -> QuestionnaireAccessAudit:
    """Obtiene el auditor global de acceso al cuestionario."""
    global _global_access_audit
    if _global_access_audit is None:
        _global_access_audit = QuestionnaireAccessAudit()
    return _global_access_audit


def reset_access_audit() -> None:
    """Resetea el auditor global (solo para testing)."""
    global _global_access_audit
    if _global_access_audit is not None:
        _global_access_audit.reset()
    _global_access_audit = None
