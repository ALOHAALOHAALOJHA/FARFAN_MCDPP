# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/signal.py

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
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


class SignalConfidence(Enum):
    """Niveles de confianza de una señal"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True)
class SignalContext:
    """
    Contexto de anclaje de una señal.
    Una señal SIEMPRE está anclada a un contexto específico.
    """
    node_type: str          # tipo de nodo:  "policy_area", "dimension", "question", "cluster"
    node_id: str            # identificador del nodo:  "PA03", "DIM02", "Q147"
    phase: str              # fase del pipeline: "phase_0", "phase_1", etc.
    consumer_scope: str     # alcance del consumidor: "Phase_0", "Phase_2", "Cross-Phase"

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
            "generation_timestamp": self.generation_timestamp.isoformat(),
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

    # Auditoría
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Validación post-inicialización"""
        if self.context is None:
            raise ValueError("Signal MUST have a context (axiom:  contextual)")
        if self.source is None:
            raise ValueError("Signal MUST have a source (axiom: derived)")

        # Registrar creación en audit trail
        self.audit_trail.append({
            "action": "CREATED",
            "timestamp": self.created_at.isoformat(),
            "signal_id": self.signal_id,
            "signal_type": getattr(self, "signal_type", "Unknown")
        })

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
        from dataclasses import asdict

        # Obtener todos los campos
        data = asdict(self)

        # Remover campos no determinísticos o metadatos variables
        exclude = {'signal_id', 'created_at', 'expires_at', 'audit_trail', 'source', 'hash'}
        hashable_content = {k: v for k, v in data.items() if k not in exclude}

        content_str = json.dumps(hashable_content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()

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
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "tags": self.tags,
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
