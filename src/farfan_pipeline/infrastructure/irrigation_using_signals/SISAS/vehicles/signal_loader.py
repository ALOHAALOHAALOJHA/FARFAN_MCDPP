# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_loader.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Iterator, Tuple
import os
import json
from pathlib import Path

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event, EventStore, EventType, EventPayload


@dataclass
class FileLoadResult:
    """Resultado de carga de un archivo"""
    success: bool
    file_path: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    file_size_bytes: int = 0
    record_count: int = 0


@dataclass
class SignalLoaderVehicle(BaseVehicle):
    """
    Vehículo: signal_loader

    Responsabilidad: Carga de archivos canónicos.

    Funcionalidad:
    - Carga archivos JSON del questionnaire canónico
    - Valida sintaxis JSON
    - Extrae metadatos del archivo
    - Genera eventos de carga

    Este vehículo es el punto de entrada para el flujo de irrigación.
    """
    vehicle_id: str = "signal_loader"
    vehicle_name: str = "Signal Loader Vehicle"

    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=True,
        can_scope=False,
        can_extract=False,
        can_transform=False,
        can_enrich=False,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=[]
    ))

    # Configuración
    base_path: str = "canonic_questionnaire_central"
    recursive: bool = True
    file_patterns: List[str] = field(default_factory=lambda: ["*.json"])

    # Estadísticas de carga
    load_stats: Dict[str, Any] = field(default_factory=lambda: {
        "files_loaded": 0,
        "files_failed": 0,
        "total_bytes_loaded": 0,
        "total_records_loaded": 0,
        "last_load_time": None
    })

    # Event store para registrar eventos de carga
    event_store: Optional[EventStore] = None

    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        """
        Procesa solicitud de carga.

        Nota: Este vehículo no genera señales directamente.
        Retorna lista vacía para cumplir la interfaz.
        La carga real se ejecuta vía load_file() o load_batch().
        """
        # Este vehículo es un loader, no un productor de señales
        # Las solicitudes de carga vienen vía método load_file()
        return []

    def load_file(self, file_path: str, phase: str = "unknown", consumer_scope: str = "default") -> FileLoadResult:
        """
        Carga un archivo canónico individual.

        Args:
            file_path: Path relativo al base_path
            phase: Fase del pipeline
            consumer_scope: Alcance del consumidor

        Returns:
            FileLoadResult con datos del archivo o error
        """
        result = FileLoadResult(
            success=False,
            file_path=file_path
        )

        try:
            # Construir path completo
            if os.path.isabs(file_path):
                full_path = file_path
            else:
                full_path = os.path.join(self.base_path, file_path)

            # Verificar existencia
            if not os.path.exists(full_path):
                result.error = f"File not found: {full_path}"
                self.load_stats["files_failed"] += 1
                return result

            # Obtener tamaño
            result.file_size_bytes = os.path.getsize(full_path)

            # Cargar JSON
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            result.data = data
            result.success = True

            # Contar registros si es una lista
            if isinstance(data, list):
                result.record_count = len(data)
            elif isinstance(data, dict):
                # Buscar listas comunes
                for key in ["questions", "items", "records", "entries", "keywords"]:
                    if key in data and isinstance(data[key], list):
                        result.record_count += len(data[key])

            # Actualizar estadísticas
            self.load_stats["files_loaded"] += 1
            self.load_stats["total_bytes_loaded"] += result.file_size_bytes
            self.load_stats["total_records_loaded"] += result.record_count

            # Registrar evento de carga exitosa
            if self.event_store:
                event = Event(
                    event_type=EventType.CANONICAL_DATA_LOADED,
                    source_file=os.path.basename(file_path),
                    source_path=full_path,
                    payload=EventPayload(data={
                        "file_size": result.file_size_bytes,
                        "record_count": result.record_count
                    }),
                    phase=phase,
                    consumer_scope=consumer_scope,
                    source_component="signal_loader"
                )
                self.event_store.append(event)

        except json.JSONDecodeError as e:
            result.error = f"Invalid JSON: {str(e)}"
            self.load_stats["files_failed"] += 1
        except Exception as e:
            result.error = f"Load failed: {str(e)}"
            self.load_stats["files_failed"] += 1

        return result

    def load_batch(
        self,
        file_paths: List[str],
        phase: str = "unknown",
        consumer_scope: str = "default"
    ) -> List[FileLoadResult]:
        """Carga múltiples archivos en lote"""
        results = []
        for file_path in file_paths:
            result = self.load_file(file_path, phase, consumer_scope)
            results.append(result)
        return results

    def discover_files(
        self,
        relative_path: str = "",
        pattern: Optional[str] = None
    ) -> List[str]:
        """
        Descubre archivos en el questionnaire canónico.

        Args:
            relative_path: Path relativo al base_path para buscar
            pattern: Patrón de archivo (ej: "metadata.json", "Q*.json")

        Returns:
            Lista de paths relativos de archivos encontrados
        """
        search_path = os.path.join(self.base_path, relative_path)
        if not os.path.exists(search_path):
            return []

        file_list = []
        patterns = [pattern] if pattern else self.file_patterns

        for root, dirs, files in os.walk(search_path):
            for filename in files:
                # Verificar si coincide con algún patrón
                if any(self._matches_pattern(filename, p) for p in patterns):
                    # Obtener path relativo al base_path
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, self.base_path)
                    file_list.append(rel_path)

                # Si no es recursivo, parar después del primer nivel
                if not self.recursive and root != search_path:
                    break

        return sorted(file_list)

    def load_all(
        self,
        relative_path: str = "",
        pattern: Optional[str] = None,
        phase: str = "unknown",
        consumer_scope: str = "default"
    ) -> Tuple[List[FileLoadResult], Dict[str, Any]]:
        """
        Carga todos los archivos que coincidan con el patrón.

        Returns:
            (resultados, resumen)
        """
        file_paths = self.discover_files(relative_path, pattern)
        results = self.load_batch(file_paths, phase, consumer_scope)

        summary = {
            "total_files_found": len(file_paths),
            "successfully_loaded": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "total_bytes": sum(r.file_size_bytes for r in results),
            "total_records": sum(r.record_count for r in results),
            "files": file_paths
        }

        return results, summary

    def get_load_summary(self) -> Dict[str, Any]:
        """Retorna resumen de estadísticas de carga"""
        return {
            **self.load_stats,
            "success_rate": self._calculate_success_rate(),
            "avg_file_size": self._calculate_avg_file_size(),
            "avg_records_per_file": self._calculate_avg_records()
        }

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Verifica si un filename coincide con un patrón"""
        from fnmatch import fnmatch
        return fnmatch(filename, pattern)

    def _calculate_success_rate(self) -> float:
        """Calcula tasa de éxito de carga"""
        total = self.load_stats["files_loaded"] + self.load_stats["files_failed"]
        if total == 0:
            return 1.0
        return self.load_stats["files_loaded"] / total

    def _calculate_avg_file_size(self) -> float:
        """Calcula tamaño promedio de archivo"""
        files = self.load_stats["files_loaded"]
        if files == 0:
            return 0.0
        return self.load_stats["total_bytes_loaded"] / files

    def _calculate_avg_records(self) -> float:
        """Calcula promedio de registros por archivo"""
        files = self.load_stats["files_loaded"]
        if files == 0:
            return 0.0
        return self.load_stats["total_records_loaded"] / files

    def iterate_canonical_files(
        self,
        batch_size: int = 100,
        pattern: Optional[str] = None
    ) -> Iterator[List[FileLoadResult]]:
        """
        Itera sobre archivos canónicos en batches.

        Útil para procesamiento incremental de grandes volúmenes.
        """
        file_paths = self.discover_files(pattern=pattern)

        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            results = self.load_batch(batch)
            yield results
