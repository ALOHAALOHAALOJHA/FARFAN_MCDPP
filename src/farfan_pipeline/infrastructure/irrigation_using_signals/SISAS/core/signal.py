# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/signal.py

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Generic
from uuid import uuid4
import hashlib
import json


class SignalCategory(Enum):
    """Categorías de señales según taxonomía SISAS"""
    STRUCTURAL = "structural"
    INTEGRITY = "integrity"
    EPISTEMIC = "epistemic"
    CONTRAST = "contrast"
    OPERATIONAL = "operational"
    CONSUMPTION = "consumption"
    ORCHESTRATION = "orchestration"


class SignalType(str, Enum):
    """
    Tipos de señales en el sistema SISAS (24 tipos totales).

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
        """Retorna la categoría de esta señal"""
        mapping = {
            # Operational
            self.SIGNAL_PACK: SignalCategory.OPERATIONAL,
            self.STATIC_LOAD: SignalCategory.OPERATIONAL,

            # Structural
            self.MC01_STRUCTURAL: SignalCategory.STRUCTURAL,
            self.MC02_QUANTITATIVE: SignalCategory.STRUCTURAL,
            self.MC03_NORMATIVE: SignalCategory.STRUCTURAL,
            self.MC04_PROGRAMMATIC: SignalCategory.STRUCTURAL,
            self.MC05_FINANCIAL: SignalCategory.STRUCTURAL,
            self.MC06_POPULATION: SignalCategory.STRUCTURAL,
            self.MC07_TEMPORAL: SignalCategory.STRUCTURAL,
            self.MC08_CAUSAL: SignalCategory.STRUCTURAL,
            self.MC09_INSTITUTIONAL: SignalCategory.STRUCTURAL,
            self.MC10_SEMANTIC: SignalCategory.STRUCTURAL,

            # Epistemic
            self.PATTERN_ENRICHMENT: SignalCategory.EPISTEMIC,
            self.KEYWORD_ENRICHMENT: SignalCategory.EPISTEMIC,
            self.ENTITY_ENRICHMENT: SignalCategory.EPISTEMIC,

            # Integrity
            self.NORMATIVE_VALIDATION: SignalCategory.INTEGRITY,
            self.ENTITY_VALIDATION: SignalCategory.INTEGRITY,
            self.COHERENCE_VALIDATION: SignalCategory.INTEGRITY,

            # Consumption
            self.MICRO_SCORE: SignalCategory.CONSUMPTION,
            self.MESO_SCORE: SignalCategory.CONSUMPTION,
            self.MACRO_SCORE: SignalCategory.CONSUMPTION,

            # Orchestration
            self.MESO_AGGREGATION: SignalCategory.ORCHESTRATION,
            self.MACRO_AGGREGATION: SignalCategory.ORCHESTRATION,
            self.REPORT_ASSEMBLY: SignalCategory.ORCHESTRATION,
        }
        return mapping.get(self, SignalCategory.OPERATIONAL)


class SignalConfidence(Enum):
    """
    Niveles de confianza de una señal.

    Ordering: HIGH > MEDIUM > LOW > INDETERMINATE

    Valores son strings para serialización, pero se pueden comparar
    usando los métodos de comparación implementados.
    """
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INDETERMINATE = "INDETERMINATE"

    @property
    def numeric_value(self) -> int:
        """Valor numérico para ordenamiento"""
        return {
            "HIGH": 4,
            "MEDIUM": 3,
            "LOW": 2,
            "INDETERMINATE": 1
        }[self.value]

    def __lt__(self, other):
        """Permite comparación: HIGH > MEDIUM > LOW > INDETERMINATE"""
        if self.__class__ is other.__class__:
            return self.numeric_value < other.numeric_value
        return NotImplemented

    def __le__(self, other):
        """Menor o igual"""
        if self.__class__ is other.__class__:
            return self.numeric_value <= other.numeric_value
        return NotImplemented

    def __gt__(self, other):
        """Mayor que"""
        if self.__class__ is other.__class__:
            return self.numeric_value > other.numeric_value
        return NotImplemented

    def __ge__(self, other):
        """Mayor o igual"""
        if self.__class__ is other.__class__:
            return self.numeric_value >= other.numeric_value
        return NotImplemented


@dataclass(frozen=True)
class SignalContext:
    """
    Contexto de anclaje de una señal. 
    Una señal SIEMPRE está anclada a un contexto específico.
    """
    node_type: str          # tipo de nodo:  "policy_area", "dimension", "question", "cluster"
    node_id: str            # identificador del nodo:  "PA03", "DIM02", "Q147"
    phase: str              # fase del pipeline: "phase_00", "phase_01", etc.
    consumer_scope: str     # alcance del consumidor: "Phase_00", "Phase_02", "Cross-Phase"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "node_type":  self.node_type,
            "node_id": self.node_id,
            "phase":  self.phase,
            "consumer_scope": self.consumer_scope
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> SignalContext:
        return cls(
            node_type=data["node_type"],
            node_id=data["node_id"],
            phase=data["phase"],
            consumer_scope=data["consumer_scope"]
        )


@dataclass(frozen=True)
class SignalSource:
    """
    Origen de una señal - trazabilidad completa
    """
    event_id: str                    # ID del evento que generó la señal
    source_file: str                 # Archivo JSON canónico de origen
    source_path: str                 # Path completo en el repositorio
    generation_timestamp: datetime   # Cuándo se generó
    generator_vehicle: str           # Qué vehículo la generó
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source_file": self.source_file,
            "source_path": self.source_path,
            "generation_timestamp": self. generation_timestamp.isoformat(),
            "generator_vehicle": self.generator_vehicle
        }


@dataclass
class Signal(ABC):
    """
    Clase base abstracta para todas las señales SISAS. 
    
    AXIOMAS DE SEÑAL (inmutables):
    1. derived:  Nunca primaria, siempre derivada de eventos
    2. deterministic: Mismo input → misma señal
    3. versioned: Nunca se sobrescribe, solo se acumula
    4. contextual: Anclada a nodo, fase, consumidor
    5. auditable: Explica por qué existe
    6. non_imperative: No ordena, no decide

    IMMUTABILITY POLICY:
    - Core fields (signal_id, signal_type, context, source, value, confidence, etc.)
      are IMMUTABLE after initialization
    - audit_trail is the ONLY mutable field (by design for auditability)
    - Attempting to modify core fields will raise AttributeError
    """
    
    # Identificación
    signal_id: str = field(default_factory=lambda:  str(uuid4()))
    signal_type: str = field(init=False)  # Se define en subclases
    version: str = "1.0.0"
    
    # Contexto (SIEMPRE requerido)
    context: SignalContext = field(default=None)
    
    # Origen (trazabilidad)
    source: SignalSource = field(default=None)
    
    # Payload de la señal
    value: Any = field(default=None)
    confidence: SignalConfidence = field(default=SignalConfidence.INDETERMINATE)
    rationale: str = field(default="")
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = field(default=None)
    tags: List[str] = field(default_factory=list)

    # Auditoría (ÚNICO campo mutable por diseño)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    # Internal flag to track initialization
    _initialized: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        """Validación post-inicialización"""
        if self. context is None:
            raise ValueError("Signal MUST have a context (axiom:  contextual)")
        if self.source is None:
            raise ValueError("Signal MUST have a source (axiom: derived)")
        
        # Registrar creación en audit trail
        self.audit_trail.append({
            "action": "CREATED",
            "timestamp": self.created_at.isoformat(),
            "signal_id": self.signal_id,
            "signal_type":  self.signal_type
        })

        # Mark as initialized to enable immutability checks
        object.__setattr__(self, '_initialized', True)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Enforce immutability for core fields.
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

        # Block all other modifications
        raise AttributeError(
            f"Cannot modify '{name}' - Signal is immutable after creation. "
            f"Only audit_trail can be updated. "
            f"(Axiom: versioned - signals never overwritten)"
        )

    @property
    @abstractmethod
    def category(self) -> SignalCategory:
        """Cada señal debe declarar su categoría"""
        pass
    
    def compute_hash(self) -> str:
        """
        Computa hash determinístico de la señal.
        Garantiza axioma: deterministic
        """
        hashable_content = {
            "signal_type": self.signal_type,
            "context": self.context.to_dict(),
            "value": self.value,
            "version": self.version
        }
        content_str = json.dumps(hashable_content, sort_keys=True, default=str)
        return hashlib. sha256(content_str.encode()).hexdigest()
    
    def is_valid(self) -> bool:
        """Verifica si la señal es válida"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]: 
        """Serializa la señal a diccionario"""
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "category": self.category.value,
            "version": self.version,
            "context": self.context.to_dict(),
            "source": self.source.to_dict() if self.source else None,
            "value": self.value,
            "confidence": self.confidence.value,
            "rationale": self.rationale,
            "created_at": self.created_at.isoformat(),
            "expires_at": self. expires_at.isoformat() if self.expires_at else None,
            "tags": self. tags,
            "hash": self.compute_hash()
        }
    
    def add_audit_entry(self, action: str, details: Dict[str, Any] = None):
        """Añade entrada al audit trail"""
        entry = {
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "signal_id": self.signal_id
        }
        if details: 
            entry["details"] = details
        self.audit_trail.append(entry)