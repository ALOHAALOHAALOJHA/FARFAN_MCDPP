# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/core/event.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
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

    @classmethod
    def from_jsonl(cls, jsonl_content: str) -> 'EventStore':
        """
        Carga EventStore desde formato JSONL.
        """
        store = cls()
        for line in jsonl_content.strip().split('\n'):
            if not line.strip():
                continue
            event_data = json.loads(line)
            # Reconstituir evento
            event = Event(
                event_id=event_data['event_id'],
                event_type=EventType(event_data['event_type']),
                timestamp=datetime.fromisoformat(event_data['timestamp']),
                source_component=event_data.get('source_component', ''),
                source_file=event_data.get('source_file', ''),
                source_path=event_data.get('source_path', ''),
                phase=event_data.get('phase', ''),
                consumer_scope=event_data.get('consumer_scope', ''),
                correlation_id=event_data.get('correlation_id'),
                causation_id=event_data.get('causation_id'),
                processed=event_data.get('processed', False)
            )
            # Reconstituir payload si existe
            if event_data.get('payload'):
                event.payload = EventPayload(
                    data=event_data['payload']['data'],
                    schema_version=event_data['payload'].get('schema_version', '1.0.0')
                )
            store.append(event)
        return store

    def persist_to_file(self, file_path: str):
        """Persiste el store a archivo"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_jsonl())

    @classmethod
    def load_from_file(cls, file_path: str) -> 'EventStore':
        """Carga EventStore desde archivo"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return cls.from_jsonl(content)

    def get_by_correlation(self, correlation_id: str) -> List[Event]:
        """Obtiene todos los eventos con el mismo correlation_id"""
        return [e for e in self.events if e.correlation_id == correlation_id]

    def get_event_chain(self, event_id: str) -> List[Event]:
        """
        Obtiene cadena causal de un evento.
        Retorna todos los eventos que causaron este evento.
        """
        chain = []
        current_event = self.get_by_id(event_id)

        while current_event and current_event.causation_id:
            caused_by = self.get_by_id(current_event.causation_id)
            if caused_by:
                chain.append(caused_by)
                current_event = caused_by
            else:
                break

        return list(reversed(chain))  # Orden cronológico

    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del store"""
        stats = {
            "total_events": len(self.events),
            "processed": len([e for e in self.events if e.processed]),
            "unprocessed": len([e for e in self.events if not e.processed]),
            "by_type": {},
            "by_phase": {},
            "with_errors": len([e for e in self.events if e.processing_errors]),
        }

        # Contar por tipo
        for event_type in EventType:
            count = len(self._index_by_type.get(event_type.value, []))
            if count > 0:
                stats["by_type"][event_type.value] = count

        # Contar por fase
        for phase in self._index_by_phase.keys():
            stats["by_phase"][phase] = len(self._index_by_phase[phase])

        return stats

    def get_recent(self, limit: int = 10) -> List[Event]:
        """Obtiene los eventos más recientes"""
        sorted_events = sorted(self.events, key=lambda e: e.timestamp, reverse=True)
        return sorted_events[:limit]

    def get_errors(self) -> List[Event]:
        """Obtiene eventos que tuvieron errores de procesamiento"""
        return [e for e in self.events if e.processing_errors]

    def archive_processed(self, older_than_days: int = 30, archive_path: str = None) -> int:
        """
        Archiva (NO elimina) eventos procesados más antiguos que N días.
        Los eventos se mueven a un almacenamiento de archivo separado.

        AXIOM COMPLIANCE: Eventos nunca se pierden - solo se archivan.

        Args:
            older_than_days: Edad mínima de eventos a archivar
            archive_path: Path opcional para archivo de almacenamiento

        Returns:
            Cantidad de eventos archivados
        """
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        to_archive = [
            e for e in self.events
            if e.processed and e.timestamp < cutoff_date
        ]

        # Si se proporciona un path, persistir a archivo
        if archive_path and to_archive:
            archive_store = EventStore(events=to_archive)
            archive_store.persist_to_file(archive_path)

        # NOTE: En cumplimiento con el axioma "Ningún evento se pierde",
        # esta implementación NO elimina eventos. Si se requiere liberar
        # memoria, los eventos archivados deben moverse a almacenamiento
        # persistente externo (DB, S3, etc.) en lugar de eliminarse.

        # TODO: Implementar estrategia de almacenamiento en frío para
        # eventos archivados (database, object storage, etc.)

        return len(to_archive)
