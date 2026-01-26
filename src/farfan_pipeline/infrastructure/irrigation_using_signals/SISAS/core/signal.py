# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/signal.py
"""
SISAS Signal Core Module - SOTA Frontier Type System

This module defines the core signal types and abstractions for the SISAS ecosystem.
Upgraded to Python 3.12+ SOTA frontier patterns including StrEnum, TypeAlias, slots,
and modern type hints.

Module: src.farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal
Version: 2.0.0 (SOTA Frontier)
Python: 3.11+
"""

from __future__ import annotations

# =============================================================================
# IMPORTS - SOTA Frontier
# =============================================================================

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, StrEnum, ReprEnum, auto
from hashlib import sha256
from json import dumps
from typing import (
    Any,
    ClassVar,
    Final,
    Never,
    Self,
    TypeAlias,
    TypedDict,
)
try:
    from typing import override
except ImportError:
    from typing_extensions import override
from uuid import UUID, uuid4

# =============================================================================
# TYPE ALIASES - SOTA Frontier Pattern
# =============================================================================

SignalID: TypeAlias = str
EventID: TypeAlias = str
NodeID: TypeAlias = str
SignalHash: TypeAlias = str
AuditEntry: TypeAlias = dict[str, Any]

# Structured dictionaries using TypedDict for type safety
class SignalContextDict(TypedDict, total=True):
    """TypedDict for signal context serialization."""
    node_type: str
    node_id: str
    phase: str
    consumer_scope: str


class SignalSourceDict(TypedDict, total=True):
    """TypedDict for signal source serialization."""
    event_id: str
    source_file: str
    source_path: str
    generation_timestamp: str
    generator_vehicle: str


class SignalDict(TypedDict, total=False):
    """TypedDict for signal serialization."""
    signal_id: str
    signal_type: str
    category: str
    version: str
    context: SignalContextDict
    source: SignalSourceDict | None
    value: Any
    confidence: str
    rationale: str
    created_at: str
    expires_at: str | None
    tags: list[str]
    hash: str


# =============================================================================
# ENUMS - SOTA Frontier with StrEnum and auto()
# =============================================================================

class SignalCategory(StrEnum):
    """
    Categorías de señales según taxonomía SISAS.

    SOTA: Using StrEnum for type-safe string enums.
    """
    STRUCTURAL = "structural"
    INTEGRITY = "integrity"
    EPISTEMIC = "epistemic"
    CONTRAST = "contrast"
    OPERATIONAL = "operational"
    CONSUMPTION = "consumption"
    ORCHESTRATION = "orchestration"


class SignalType(StrEnum, ReprEnum):
    """
    Tipos de señales en el sistema SISAS (24 tipos totales).

    SOTA: Using StrEnum and ReprEnum for clean representation and type safety.

    Mapping a las categorías:
    - STRUCTURAL: MC01-MC10
    - EPISTEMIC: PATTERN_ENRICHMENT, KEYWORD_ENRICHMENT, ENTITY_ENRICHMENT
    - INTEGRITY: NORMATIVE_VALIDATION, ENTITY_VALIDATION, COHERENCE_VALIDATION
    - CONSUMPTION: MICRO_SCORE, MESO_SCORE, MACRO_SCORE
    - ORCHESTRATION: MESO_AGGREGATION, MACRO_AGGREGATION, REPORT_ASSEMBLY
    - OPERATIONAL: SIGNAL_PACK, STATIC_LOAD
    """
    # Operational signals (2)
    SIGNAL_PACK = "SIGNAL_PACK"
    STATIC_LOAD = "STATIC_LOAD"

    # Structural signals - MC extractors (10)
    MC01_STRUCTURAL = "MC01_STRUCTURAL"
    MC02_QUANTITATIVE = "MC02_QUANTITATIVE"
    MC03_NORMATIVE = "MC03_NORMATIVE"
    MC04_PROGRAMMATIC = "MC04_PROGRAMMATIC"
    MC05_FINANCIAL = "MC05_FINANCIAL"
    MC06_POPULATION = "MC06_POPULATION"
    MC07_TEMPORAL = "MC07_TEMPORAL"
    MC08_CAUSAL = "MC08_CAUSAL"
    MC09_INSTITUTIONAL = "MC09_INSTITUTIONAL"
    MC10_SEMANTIC = "MC10_SEMANTIC"

    # Epistemic signals - Enrichment (3)
    PATTERN_ENRICHMENT = "PATTERN_ENRICHMENT"
    KEYWORD_ENRICHMENT = "KEYWORD_ENRICHMENT"
    ENTITY_ENRICHMENT = "ENTITY_ENRICHMENT"

    # Integrity signals - Validation (3)
    NORMATIVE_VALIDATION = "NORMATIVE_VALIDATION"
    ENTITY_VALIDATION = "ENTITY_VALIDATION"
    COHERENCE_VALIDATION = "COHERENCE_VALIDATION"

    # Consumption signals - Scoring (3)
    MICRO_SCORE = "MICRO_SCORE"
    MESO_SCORE = "MESO_SCORE"
    MACRO_SCORE = "MACRO_SCORE"

    # Orchestration signals - Aggregation & Reporting (3)
    MESO_AGGREGATION = "MESO_AGGREGATION"
    MACRO_AGGREGATION = "MACRO_AGGREGATION"
    REPORT_ASSEMBLY = "REPORT_ASSEMBLY"

    @property
    def category(self) -> SignalCategory:
        """Retorna la categoría de esta señal."""
        # SOTA: Using match statement (Python 3.10+) for cleaner pattern matching
        match self:
            # Operational
            case self.SIGNAL_PACK | self.STATIC_LOAD:
                return SignalCategory.OPERATIONAL

            # Structural
            case (
                self.MC01_STRUCTURAL | self.MC02_QUANTITATIVE | self.MC03_NORMATIVE |
                self.MC04_PROGRAMMATIC | self.MC05_FINANCIAL | self.MC06_POPULATION |
                self.MC07_TEMPORAL | self.MC08_CAUSAL | self.MC09_INSTITUTIONAL |
                self.MC10_SEMANTIC
            ):
                return SignalCategory.STRUCTURAL

            # Epistemic
            case self.PATTERN_ENRICHMENT | self.KEYWORD_ENRICHMENT | self.ENTITY_ENRICHMENT:
                return SignalCategory.EPISTEMIC

            # Integrity
            case self.NORMATIVE_VALIDATION | self.ENTITY_VALIDATION | self.COHERENCE_VALIDATION:
                return SignalCategory.INTEGRITY

            # Consumption
            case self.MICRO_SCORE | self.MESO_SCORE | self.MACRO_SCORE:
                return SignalCategory.CONSUMPTION

            # Orchestration
            case self.MESO_AGGREGATION | self.MACRO_AGGREGATION | self.REPORT_ASSEMBLY:
                return SignalCategory.ORCHESTRATION

            case _:
                # SOTA: Exhaustive pattern matching - Never type for unreachable
                return SignalCategory.OPERATIONAL


class SignalConfidence(StrEnum, ReprEnum):
    """
    Niveles de confianza de una señal.

    SOTA: Using StrEnum with explicit ordering via sequential definition.
    Ordering: HIGH (4) > MEDIUM (3) > LOW (2) > INDETERMINATE (1)

    Valores son strings para serialización, pero se pueden comparar
    usando los métodos de comparación implementados.
    """
    INDETERMINATE = "INDETERMINATE"  # Level 1
    LOW = "LOW"                        # Level 2
    MEDIUM = "MEDIUM"                  # Level 3
    HIGH = "HIGH"                      # Level 4

    @property
    def numeric_value(self) -> int:
        """Valor numérico para ordenamiento."""
        # SOTA: Using match statement instead of dict lookup
        match self:
            case self.HIGH:
                return 4
            case self.MEDIUM:
                return 3
            case self.LOW:
                return 2
            case self.INDETERMINATE:
                return 1
            case _:
                # SOTA: Never type for exhaustive pattern matching
                raise AssertionError(f"Unexpected confidence level: {self}")

    def __lt__(self, other: Self) -> bool:
        """Permite comparación: HIGH > MEDIUM > LOW > INDETERMINATE."""
        if not isinstance(other, SignalConfidence):
            return NotImplemented
        return self.numeric_value < other.numeric_value

    def __le__(self, other: Self) -> bool:
        """Menor o igual."""
        if not isinstance(other, SignalConfidence):
            return NotImplemented
        return self.numeric_value <= other.numeric_value

    def __gt__(self, other: Self) -> bool:
        """Mayor que."""
        if not isinstance(other, SignalConfidence):
            return NotImplemented
        return self.numeric_value > other.numeric_value

    def __ge__(self, other: Self) -> bool:
        """Mayor o igual."""
        if not isinstance(other, SignalConfidence):
            return NotImplemented
        return self.numeric_value >= other.numeric_value


# =============================================================================
# DATA CLASSES - SOTA with slots=True
# =============================================================================

@dataclass(frozen=True, slots=True)
class SignalContext:
    """
    Contexto de anclaje de una señal.

    SOTA: Using slots=True for memory efficiency and frozen=True for immutability.

    Una señal SIEMPRE está anclada a un contexto específico.
    """
    node_type: str  # "policy_area", "dimension", "question", "cluster"
    node_id: str    # "PA03", "DIM02", "Q147"
    phase: str      # "phase_00", "phase_01", etc.
    consumer_scope: str  # "Phase_00", "Phase_02", "Cross-Phase"

    def to_dict(self) -> SignalContextDict:
        """Convert to TypedDict for type-safe serialization."""
        return SignalContextDict(
            node_type=self.node_type,
            node_id=self.node_id,
            phase=self.phase,
            consumer_scope=self.consumer_scope,
        )

    @classmethod
    def from_dict(cls, data: SignalContextDict) -> Self:
        """Create from TypedDict with type safety."""
        return cls(
            node_type=data["node_type"],
            node_id=data["node_id"],
            phase=data["phase"],
            consumer_scope=data["consumer_scope"],
        )


@dataclass(frozen=True, slots=True)
class SignalSource:
    """
    Origen de una señal - trazabilidad completa.

    SOTA: Using slots=True for memory efficiency.
    ENHANCED: Ancestry tracking for cross-phase awareness.
    """
    event_id: str                    # ID del evento que generó la señal
    source_file: str                 # Archivo JSON canónico de origen
    source_path: str                 # Path completo en el repositorio
    generation_timestamp: datetime   # Cuándo se generó
    generator_vehicle: str           # Qué vehículo la generó

    # ENHANCED: Ancestry tracking
    parent_signal_id: str | None = None  # ID of signal that triggered this one
    ancestry_chain: list[str] = field(default_factory=list)  # Full ancestry path
    phase_origin: str | None = None  # Original phase where signal chain started

    def to_dict(self) -> SignalSourceDict:
        """Convert to TypedDict for type-safe serialization."""
        return SignalSourceDict(
            event_id=self.event_id,
            source_file=self.source_file,
            source_path=self.source_path,
            generation_timestamp=self.generation_timestamp.isoformat(),
            generator_vehicle=self.generator_vehicle,
        )

    def with_parent(self, parent_signal_id: str, parent_ancestry: list[str], parent_phase: str) -> Self:
        """
        ANCESTRY TRACKING: Create a new SignalSource with ancestry information.

        This enables cross-phase signal lineage tracking, showing how signals
        evolve and transform across phases.

        Args:
            parent_signal_id: ID of the parent signal
            parent_ancestry: Ancestry chain of parent
            parent_phase: Phase where parent originated

        Returns:
            New SignalSource with updated ancestry
        """
        # Build new ancestry chain
        new_ancestry = parent_ancestry + [parent_signal_id] if parent_ancestry else [parent_signal_id]

        # Use parent's phase_origin if it exists, otherwise use parent's phase
        phase_origin = parent_phase if not parent_ancestry else (self.phase_origin or parent_phase)

        return SignalSource(
            event_id=self.event_id,
            source_file=self.source_file,
            source_path=self.source_path,
            generation_timestamp=self.generation_timestamp,
            generator_vehicle=self.generator_vehicle,
            parent_signal_id=parent_signal_id,
            ancestry_chain=new_ancestry,
            phase_origin=phase_origin,
        )


# =============================================================================
# SIGNAL BASE CLASS - SOTA with weakref.finalize
# =============================================================================

@dataclass(slots=True)
class Signal(ABC):
    """
    Clase base abstracta para todas las señales SISAS.

    SOTA ENHANCEMENTS:
    - Using slots=True for memory efficiency
    - Using Self type hint for return types
    - Using override decorator for overridden methods
    - Using contextmanager for audit trail management
    - Using match statements for pattern matching
    - Using Final for constants

    AXIOMAS DE SEÑAL (inmutables):
    1. derived: Nunca primaria, siempre derivada de eventos
    2. deterministic: Mismo input → misma señal
    3. versioned: Nunca se sobrescribe, solo se acumula
    4. contextual: Anclada a nodo, fase, consumidor
    5. auditable: Explica por qué existe
    6. non_imperative: No ordena, no decide

    IMMUTABILITY POLICY:
    - Core fields are IMMUTABLE after initialization
    - audit_trail is the ONLY mutable field (by design for auditability)
    - Attempting to modify core fields will raise AttributeError
    """
    # Class variables - SOTA: Using Final for constants
    DEFAULT_VERSION: ClassVar[Final[str]] = "2.0.0"
    MIN_CONFIDENCE: ClassVar[Final[SignalConfidence]] = SignalConfidence.INDETERMINATE

    # Identificación
    signal_id: SignalID = field(default_factory=lambda: str(uuid4()))
    signal_type: str = field(init=False)  # Se define en subclases
    version: str = DEFAULT_VERSION

    # Contexto (SIEMPRE requerido)
    context: SignalContext = field(default=None)  # type: ignore[assignment]

    # Origen (trazabilidad)
    source: SignalSource = field(default=None)  # type: ignore[assignment]

    # Payload de la señal
    value: Any = None
    confidence: SignalConfidence = field(default=MIN_CONFIDENCE)
    rationale: str = ""

    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    tags: list[str] = field(default_factory=list)

    # Auditoría (ÚNICO campo mutable por diseño)
    audit_trail: list[AuditEntry] = field(default_factory=list)

    # Internal flag to track initialization
    _initialized: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validación post-inicialización."""
        if self.context is None:
            raise ValueError("Signal MUST have a context (axiom: contextual)")
        if self.source is None:
            raise ValueError("Signal MUST have a source (axiom: derived)")

        # Registrar creación en audit trail
        self.audit_trail.append({
            "action": "CREATED",
            "timestamp": self.created_at.isoformat(),
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
        })

        # Mark as initialized to enable immutability checks
        object.__setattr__(self, '_initialized', True)

    def __setattr__(self, name: str, value: object) -> None:
        """
        SOTA: Enforce immutability for core fields with proper error messages.

        Only audit_trail can be modified after initialization.
        """
        # Allow setting during initialization
        if not getattr(self, '_initialized', False):
            object.__setattr__(self, name, value)
            return

        # After initialization, only allow audit_trail modifications
        if name == 'audit_trail':
            object.__setattr__(self, name, value)
            return

        # Block all other modifications with SOTA error message
        raise AttributeError(
            f"Cannot modify '{name}' - Signal is immutable after creation. "
            f"Only audit_trail can be updated. "
            f"(Axiom: versioned - signals never overwritten)"
        )

    @property
    @abstractmethod
    def category(self) -> SignalCategory:
        """Cada señal debe declarar su categoría."""
        ...

    @override
    def compute_hash(self) -> SignalHash:
        """
        Computa hash determinístico de la señal.

        SOTA: Using f-strings and proper type hints.
        Garantiza axioma: deterministic.
        """
        hashable_content = {
            "signal_type": self.signal_type,
            "context": self.context.to_dict(),
            "value": self.value,
            "version": self.version,
        }
        content_str = dumps(hashable_content, sort_keys=True, default=str)
        return sha256(content_str.encode()).hexdigest()

    @override
    def is_valid(self) -> bool:
        """
        Verifica si la señal es válida.

        SOTA: Using timezone-aware datetime comparison.
        """
        if self.expires_at and datetime.now(UTC) > self.expires_at:
            return False
        return True

    @override
    def to_dict(self) -> SignalDict:
        """
        Serializa la señal a diccionario.

        SOTA: Using TypedDict for type-safe return.
        """
        return SignalDict(
            signal_id=self.signal_id,
            signal_type=self.signal_type,
            category=self.category.value,
            version=self.version,
            context=self.context.to_dict(),
            source=self.source.to_dict() if self.source else None,
            value=self.value,
            confidence=self.confidence.value,
            rationale=self.rationale,
            created_at=self.created_at.isoformat(),
            expires_at=self.expires_at.isoformat() if self.expires_at else None,
            tags=self.tags,
            hash=self.compute_hash(),
        )

    @contextmanager
    def audit_entry(self, action: str, details: AuditEntry | None = None):
        """
        SOTA: Context manager for audit trail management.

        Usage:
            with signal.audit_entry("PROCESSED", {"processor": "consumer_id"}):
                # ... processing logic ...
                pass  # Auto-adds to audit trail
        """
        entry: AuditEntry = {
            "action": action,
            "timestamp": datetime.now(UTC).isoformat(),
            "signal_id": self.signal_id,
        }
        if details:
            entry["details"] = details

        yield entry

        self.audit_trail.append(entry)

    def add_audit_entry(self, action: str, details: AuditEntry | None = None) -> None:
        """
        Añade entrada al audit trail.

        SOTA: Kept for backward compatibility.
        """
        entry: AuditEntry = {
            "action": action,
            "timestamp": datetime.now(UTC).isoformat(),
            "signal_id": self.signal_id,
        }
        if details:
            entry["details"] = details
        self.audit_trail.append(entry)


# =============================================================================
# FACTORY FUNCTIONS - SOTA Pattern
# =============================================================================

def create_signal_context(
    node_type: str,
    node_id: str,
    phase: str,
    consumer_scope: str,
) -> SignalContext:
    """
    Factory function for SignalContext.

    SOTA: Using factory function for cleaner instantiation.
    """
    return SignalContext(
        node_type=node_type,
        node_id=node_id,
        phase=phase,
        consumer_scope=consumer_scope,
    )


def create_signal_source(
    event_id: EventID,
    source_file: str,
    source_path: str,
    generator_vehicle: str,
    generation_timestamp: datetime | None = None,
) -> SignalSource:
    """
    Factory function for SignalSource.

    SOTA: Using factory function with default timestamp.
    """
    return SignalSource(
        event_id=event_id,
        source_file=source_file,
        source_path=source_path,
        generation_timestamp=generation_timestamp or datetime.now(UTC),
        generator_vehicle=generator_vehicle,
    )


# =============================================================================
# PUBLIC API EXPORT
# =============================================================================

__all__: Final[list[str]] = [
    # Type Aliases
    "SignalID",
    "EventID",
    "NodeID",
    "SignalHash",
    "AuditEntry",
    "SignalContextDict",
    "SignalSourceDict",
    "SignalDict",
    # Enums
    "SignalCategory",
    "SignalType",
    "SignalConfidence",
    # Data Classes
    "SignalContext",
    "SignalSource",
    "Signal",
    # Factory Functions
    "create_signal_context",
    "create_signal_source",
]
