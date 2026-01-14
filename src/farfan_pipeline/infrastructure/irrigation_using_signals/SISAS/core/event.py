# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/event.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json
import os


class EventType(Enum):
    """Tipos de eventos en el sistema"""
    # Eventos de datos canónicos
    CANONICAL_DATA_LOADED = "canonical_data_loaded"
    CANONICAL_DATA_VALIDATED = "canonical_data_validated"
    CANONICAL_DATA_TRANSFORMED = "canonical_data_transformed"

    # Eventos de irrigación
    IRRIGATION_REQUESTED = "irrigation_requested"
    IRRIGATION_STARTED = "irrigation_started"
    IRRIGATION_COMPLETED = "irrigation_completed"
    IRRIGATION_FAILED = "irrigation_failed"

    # Eventos de consumo
    CONSUMER_REGISTERED = "consumer_registered"
    CONSUMER_RECEIVED_DATA = "consumer_received_data"
    CONSUMER_PROCESSED_DATA = "consumer_processed_data"

    # Eventos de señales
    SIGNAL_GENERATED = "signal_generated"
    SIGNAL_PUBLISHED = "signal_published"
    SIGNAL_CONSUMED = "signal_consumed"

    # Eventos de contraste (legacy vs nuevo)
    CONTRAST_STARTED = "contrast_started"
    CONTRAST_DIVERGENCE_DETECTED = "contrast_divergence_detected"
    CONTRAST_COMPLETED = "contrast_completed"


@dataclass(frozen=True)
class EventPayload:
    """Payload inmutable de un evento"""
    data: Dict[str, Any]
    schema_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data":  self.data,
            "schema_version": self.schema_version
        }


@dataclass
class Event:
    """
    Evento empírico en el sistema SISAS.

    Un evento es un HECHO que ocurrió.
    NO interpreta, NO juzga, solo registra.

    Los eventos son la FUENTE de las señales.
    """

    # Identificación
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EventType = field(default=EventType.CANONICAL_DATA_LOADED)

    # Temporal
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Ubicación en el sistema
    source_component: str = ""          # Componente que generó el evento
    source_file: str = ""               # Archivo canónico relacionado
    source_path: str = ""               # Path completo

    # Payload (lo que pasó)
    payload: Optional[EventPayload] = field(default=None)

    # Contexto de procesamiento
    phase: str = ""                     # Fase del pipeline
    consumer_scope: str = ""            # Alcance del consumidor

    # Metadatos
    correlation_id: Optional[str] = None  # Para trazar eventos relacionados
    causation_id: Optional[str] = None    # Evento que causó este

    # Estado
    processed: bool = False
    processing_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el evento"""
        return {
            "event_id": self.event_id,
            "event_type":  self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source_component": self.source_component,
            "source_file": self.source_file,
            "source_path": self.source_path,
            "payload": self.payload.to_dict() if self.payload else None,
            "phase": self.phase,
            "consumer_scope": self.consumer_scope,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "processed": self.processed
        }

    @classmethod
    def from_canonical_file(
        cls,
        file_path: str,
        file_content: Dict[str, Any],
        phase: str,
        consumer_scope: str
    ) -> Event:
        """
        Factory para crear evento desde archivo canónico.
        """

        return cls(
            event_type=EventType.CANONICAL_DATA_LOADED,
            source_file=os.path.basename(file_path),
            source_path=file_path,
            payload=EventPayload(data=file_content),
            phase=phase,
            consumer_scope=consumer_scope,
            source_component="canonical_loader"
        )

    def mark_processed(self):
        """Marca el evento como procesado"""
        self.processed = True

    def add_error(self, error: str):
        """Añade error de procesamiento"""
        self.processing_errors.append(error)


@dataclass
class EventStore:
    """
    Almacén de eventos - NUNCA se borran.
    Implementa el axioma:  Ningún evento se pierde.
    """

    events: List[Event] = field(default_factory=list)
    _index_by_type: Dict[str, List[str]] = field(default_factory=dict)
    _index_by_file: Dict[str, List[str]] = field(default_factory=dict)
    _index_by_phase: Dict[str, List[str]] = field(default_factory=dict)

    def append(self, event: Event) -> str:
        """
        Añade evento al store.
        Retorna el event_id.
        """
        self.events.append(event)

        # Indexar por tipo
        if event.event_type.value not in self._index_by_type:
            self._index_by_type[event.event_type.value] = []
        self._index_by_type[event.event_type.value].append(event.event_id)

        # Indexar por archivo
        if event.source_file:
            if event.source_file not in self._index_by_file:
                self._index_by_file[event.source_file] = []
            self._index_by_file[event.source_file].append(event.event_id)

        # Indexar por fase
        if event.phase:
            if event.phase not in self._index_by_phase:
                self._index_by_phase[event.phase] = []
            self._index_by_phase[event.phase].append(event.event_id)

        return event.event_id

    def get_by_id(self, event_id: str) -> Optional[Event]:
        """Obtiene evento por ID"""
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None

    def get_by_type(self, event_type: EventType) -> List[Event]:
        """Obtiene eventos por tipo"""
        ids = self._index_by_type.get(event_type.value, [])
        return [e for e in self.events if e.event_id in ids]

    def get_by_file(self, source_file: str) -> List[Event]:
        """Obtiene eventos por archivo fuente"""
        ids = self._index_by_file.get(source_file, [])
        return [e for e in self.events if e.event_id in ids]

    def get_by_phase(self, phase: str) -> List[Event]:
        """Obtiene eventos por fase"""
        ids = self._index_by_phase.get(phase, [])
        return [e for e in self.events if e.event_id in ids]

    def get_unprocessed(self) -> List[Event]:
        """Obtiene eventos no procesados"""
        return [e for e in self.events if not e.processed]

    def count(self) -> int:
        """Total de eventos"""
        return len(self.events)

    def to_jsonl(self) -> str:
        """Exporta a formato JSONL para persistencia"""
        lines = []
        for event in self.events:
            lines.append(json.dumps(event.to_dict()))
        return "\n".join(lines)
