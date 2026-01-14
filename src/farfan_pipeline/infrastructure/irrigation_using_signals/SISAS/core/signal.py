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

    def validate_integrity(self) -> tuple[bool, List[str]]:
        """
        Valida la integridad de la señal según los axiomas SISAS.
        Retorna (es_válida, lista_de_errores)
        """
        errors = []

        # Axioma 1: derived - debe tener source
        if self.source is None:
            errors.append("Axiom violation 'derived': Signal must have a source")

        # Axioma 4: contextual - debe tener context
        if self.context is None:
            errors.append("Axiom violation 'contextual': Signal must have a context")

        # Verificar expiración
        if not self.is_valid():
            errors.append("Signal has expired")

        # Verificar que el signal_type está definido
        if not hasattr(self, 'signal_type') or not self.signal_type:
            errors.append("Signal type is not defined")

        # Verificar que category es válido
        try:
            _ = self.category
        except Exception as e:
            errors.append(f"Invalid category: {str(e)}")

        return (len(errors) == 0, errors)

    def to_json(self) -> str:
        """Serializa la señal a JSON"""
        return json.dumps(self.to_dict(), default=str, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Signal':
        """
        Deserializa una señal desde diccionario.
        Nota: Requiere la clase específica de señal.
        """
        # Reconstituir context
        context_data = data.get('context')
        if context_data:
            context = SignalContext.from_dict(context_data)
        else:
            context = None

        # Reconstituir source
        source_data = data.get('source')
        if source_data:
            source = SignalSource(
                event_id=source_data['event_id'],
                source_file=source_data['source_file'],
                source_path=source_data['source_path'],
                generation_timestamp=datetime.fromisoformat(source_data['generation_timestamp']),
                generator_vehicle=source_data['generator_vehicle']
            )
        else:
            source = None

        # Nota: Este método debe ser sobrescrito en clases concretas
        # para manejar campos específicos
        return cls(
            context=context,
            source=source,
            value=data.get('value'),
            confidence=SignalConfidence(data.get('confidence', 'INDETERMINATE')),
            rationale=data.get('rationale', ''),
            tags=data.get('tags', [])
        )

    def compare_with(self, other: 'Signal') -> Dict[str, Any]:
        """
        Compara esta señal con otra y retorna diferencias.
        Útil para debugging y análisis.
        """
        if not isinstance(other, Signal):
            return {"error": "Cannot compare with non-Signal object"}

        differences = {}

        # Comparar hashes
        my_hash = self.compute_hash()
        other_hash = other.compute_hash()

        if my_hash != other_hash:
            differences['hash_mismatch'] = {
                'self': my_hash,
                'other': other_hash
            }

        # Comparar tipos
        if self.signal_type != other.signal_type:
            differences['signal_type'] = {
                'self': self.signal_type,
                'other': other.signal_type
            }

        # Comparar contextos
        if self.context != other.context:
            differences['context'] = {
                'self': self.context.to_dict() if self.context else None,
                'other': other.context.to_dict() if other.context else None
            }

        # Comparar valores
        if self.value != other.value:
            differences['value'] = {
                'self': self.value,
                'other': other.value
            }

        # Comparar confidence
        if self.confidence != other.confidence:
            differences['confidence'] = {
                'self': self.confidence.value,
                'other': other.confidence.value
            }

        return differences if differences else {"status": "identical"}

    def get_age_seconds(self) -> float:
        """Retorna la edad de la señal en segundos"""
        return (datetime.utcnow() - self.created_at).total_seconds()

    def is_expired(self) -> bool:
        """Verifica si la señal ha expirado"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def get_audit_summary(self) -> Dict[str, Any]:
        """Retorna resumen del audit trail"""
        return {
            "total_entries": len(self.audit_trail),
            "actions": [entry['action'] for entry in self.audit_trail],
            "first_action": self.audit_trail[0] if self.audit_trail else None,
            "last_action": self.audit_trail[-1] if self.audit_trail else None
        }
