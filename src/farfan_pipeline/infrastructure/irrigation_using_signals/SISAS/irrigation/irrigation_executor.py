# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/irrigation/irrigation_executor.py

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
import json
import logging
import hashlib

from .irrigation_map import IrrigationMap, IrrigationRoute, IrrigabilityStatus
from ..core.signal import Signal, SignalContext, SignalSource
from ..core.event import Event, EventStore, EventType
from ..core.contracts import IrrigationContract, ContractRegistry, ContractStatus
from ..core.bus import BusRegistry
from ..vehicles.base_vehicle import BaseVehicle
from ..signal_types.types.operational import ExecutionAttemptSignal, ExecutionStatus, FailureModeSignal, FailureMode


class IrrigationPhase(Enum):
    """Fases de la irrigación según JF (Job Fronts)"""
    JF0_CONTAINMENT = "JF0"      # Contención del legacy
    JF1_OBSERVATION = "JF1"      # Observación pasiva
    JF2_EXTRACTION = "JF2"       # Extracción empírica
    JF3_CANONIZATION = "JF3"     # Canonización estructural
    JF4_INSTRUMENTATION = "JF4"  # Instrumentación de eventos
    JF5_SIGNAL_GEN = "JF5"       # Generación de señales (NÚCLEO SISAS)
    JF6_BUS_CONTRACTS = "JF6"    # Buses y contratos
    JF7_CONSUMERS = "JF7"        # Consumidores analíticos
    JF8_CONTRAST = "JF8"         # Contraste legacy vs nuevo
    JF9_SUBSTITUTION = "JF9"     # Sustitución controlada
    JF10_AUDIT = "JF10"          # Auditoría continua


@dataclass
class IrrigationResult:
    """Resultado de una irrigación"""
    route_id: str
    success: bool
    signals_generated: List[Signal] = field(default_factory=list)
    signals_published: int = 0
    consumers_notified: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PhaseExecutionResult:
    """Resultado de ejecución de una fase completa"""
    phase: str
    total_routes: int = 0
    successful_routes: int = 0
    failed_routes: int = 0
    total_signals_generated: int = 0
    total_signals_published: int = 0
    unique_consumers_notified: set = field(default_factory=set)
    route_results: List[IrrigationResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        """Tasa de éxito de la fase"""
        if self.total_routes == 0:
            return 0.0
        return (self.successful_routes / self.total_routes) * 100

    def add_route_result(self, result: IrrigationResult):
        """Agrega resultado de una ruta"""
        self.route_results.append(result)
        self.total_routes += 1

        if result.success:
            self.successful_routes += 1
        else:
            self.failed_routes += 1

        self.total_signals_generated += len(result.signals_generated)
        self.total_signals_published += result.signals_published
        self.unique_consumers_notified.update(result.consumers_notified)

    def finalize(self):
        """Finaliza la ejecución de la fase"""
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000


@dataclass
class IrrigationExecutor:
    """
    Ejecutor de irrigación.

    Responsabilidades:
    1. Cargar datos canónicos
    2. Pasarlos por vehículos apropiados
    3. Generar señales
    4. Publicar en buses
    5. Notificar a consumidores
    6. Registrar todo para auditoría
    
    ENHANCED:
    - Signal deduplication to avoid redundant processing
    - Signal caching for deterministic results
    - Performance optimization
    """

    irrigation_map: IrrigationMap = field(default_factory=IrrigationMap)
    bus_registry: BusRegistry = field(default_factory=BusRegistry)
    contract_registry: ContractRegistry = field(default_factory=ContractRegistry)
    event_store: EventStore = field(default_factory=EventStore)

    # Vehículos registrados
    vehicles: Dict[str, BaseVehicle] = field(default_factory=dict)

    # Loaders de archivos
    file_loaders:  Dict[str, Callable] = field(default_factory=dict)

    # Estado
    current_phase: IrrigationPhase = IrrigationPhase.JF0_CONTAINMENT
    is_running: bool = False

    # Resultados
    execution_history: List[IrrigationResult] = field(default_factory=list)
    
    # ENHANCED: Signal deduplication and caching
    _signal_cache: Dict[str, Signal] = field(default_factory=dict)
    _signal_hashes: Set[str] = field(default_factory=set)
    _deduplication_enabled: bool = True
    _cache_enabled: bool = True
    _deduplication_stats: Dict[str, int] = field(default_factory=lambda: {
        "total_signals": 0,
        "duplicates_detected": 0,
        "cache_hits": 0
    })

    # Logger
    _logger: logging.Logger = field(default=None)

    def __post_init__(self):
        if self._logger is None:
            self._logger = logging.getLogger("SISAS.IrrigationExecutor")

        # Registrar loader por defecto para JSON
        self.file_loaders["json"] = self._load_json_file

    def register_vehicle(self, vehicle: BaseVehicle):
        """Registra un vehículo"""
        self.vehicles[vehicle.vehicle_id] = vehicle
        vehicle.bus_registry = self.bus_registry
        vehicle.contract_registry = self.contract_registry
        self._logger.info(f"Vehicle registered: {vehicle.vehicle_id}")

    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Carga un archivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def execute_route(self, route: IrrigationRoute, base_path: str = "") -> IrrigationResult:
        """
        Ejecuta una ruta de irrigación completa.
        """
        start_time = datetime.utcnow()
        result = IrrigationResult(route_id=route.source.file_path, success=False)

        try:
            # 1. Verificar que la ruta es irrigable
            if route.source.irrigability != IrrigabilityStatus.IRRIGABLE_NOW:
                result.errors.append(f"Route not irrigable: {route.source.gaps}")
                return result

            # 2. Verificar vehículos disponibles
            missing_vehicles = [v for v in route.vehicles if v not in self.vehicles]
            if missing_vehicles:
                result.errors.append(f"Missing vehicles: {missing_vehicles}")
                return result

            # 3. Cargar archivo canónico
            file_path = f"{base_path}/{route.source.file_path}" if base_path else route.source.file_path

            try:
                data = self._load_json_file(file_path)
            except Exception as e:
                result.errors.append(f"Failed to load file: {str(e)}")
                return result

            # 4. Crear contexto
            context = SignalContext(
                node_type=self._infer_node_type(route.source.file_path),
                node_id=route.source.file_path,
                phase=route.source.phase,
                consumer_scope=route.source.stage
            )

            # 5. Registrar evento de carga
            load_event = Event(
                event_type=EventType.CANONICAL_DATA_LOADED,
                source_file=route.source.file_path,
                source_path=file_path,
                phase=route.source.phase,
                consumer_scope=route.source.stage,
                source_component="irrigation_executor"
            )
            self.event_store.append(load_event)

            # 6. Procesar con cada vehículo
            all_signals = []

            for vehicle_id in route.vehicles:
                vehicle = self.vehicles[vehicle_id]

                try:
                    signals = vehicle.process(data, context)
                    
                    # ENHANCED: Deduplicate signals
                    if self._deduplication_enabled:
                        signals = self._deduplicate_signals(signals)
                    
                    all_signals.extend(signals)
                    self._logger.debug(
                        f"Vehicle {vehicle_id} generated {len(signals)} signals"
                    )
                except Exception as e:
                    result.errors.append(f"Vehicle {vehicle_id} error: {str(e)}")
                    # Generar señal de falla
                    failure_signal = self._create_failure_signal(
                        vehicle_id, str(e), context
                    )
                    all_signals.append(failure_signal)

            result.signals_generated = all_signals

            # 7. Publicar señales en buses
            for signal in all_signals:
                for vehicle_id in route.vehicles:
                    vehicle = self.vehicles[vehicle_id]
                    if vehicle.publication_contract:
                        success, msg = vehicle.publish_signal(signal)
                        if success:
                            result.signals_published += 1
                        else:
                            self._logger.warning(f"Failed to publish:  {msg}")

            # 8. Notificar consumidores
            for target in route.targets:
                result.consumers_notified.append(target.consumer_id)
                self._logger.info(f"Consumer notified: {target.consumer_id}")

            # 9. Registrar evento de irrigación completada
            complete_event = Event(
                event_type=EventType.IRRIGATION_COMPLETED,
                source_file=route.source.file_path,
                phase=route.source.phase,
                source_component="irrigation_executor"
            )
            self.event_store.append(complete_event)

            result.success = True

        except Exception as e:
            result.errors.append(f"Execution error: {str(e)}")
            self._logger.error(f"Irrigation failed for {route.source.file_path}:  {e}")

        finally:
            end_time = datetime.utcnow()
            result.duration_ms = (end_time - start_time).total_seconds() * 1000
            result.timestamp = end_time
            self.execution_history.append(result)

        return result

    def execute_phase(self, phase: str, base_path: str = "") -> PhaseExecutionResult:
        """
        Ejecuta todas las rutas de una fase.

        Returns:
            PhaseExecutionResult con estadísticas agregadas
        """
        phase_result = PhaseExecutionResult(phase=phase)
        routes = self.irrigation_map.get_routes_for_phase(phase)

        self._logger.info(f"Executing phase {phase}: {len(routes)} routes")

        for route in routes:
            if route.source.irrigability == IrrigabilityStatus.IRRIGABLE_NOW:
                result = self.execute_route(route, base_path)
                phase_result.add_route_result(result)

        phase_result.finalize()

        self._logger.info(
            f"Phase {phase} completed: {phase_result.successful_routes}/{phase_result.total_routes} "
            f"routes successful ({phase_result.success_rate:.1f}%), "
            f"{phase_result.total_signals_generated} signals generated"
        )

        return phase_result

    def execute_all_irrigable(self, base_path: str = "") -> List[IrrigationResult]:
        """
        Ejecuta todas las rutas irrigables ahora.
        """
        results = []
        routes = self.irrigation_map.get_irrigable_now()

        self._logger.info(f"Executing all irrigable routes: {len(routes)}")

        for route in routes:
            result = self.execute_route(route, base_path)
            results.append(result)

        return results

    def _infer_node_type(self, file_path: str) -> str:
        """Infiere el tipo de nodo desde el path"""
        path_lower = file_path.lower()

        if "question" in path_lower:
            return "question"
        elif "policy_area" in path_lower or "/pa" in path_lower:
            return "policy_area"
        elif "dimension" in path_lower or "/dim" in path_lower:
            return "dimension"
        elif "cluster" in path_lower or "/cl" in path_lower:
            return "cluster"
        elif "pattern" in path_lower:
            return "pattern"
        elif "cross_cutting" in path_lower:
            return "cross_cutting"
        elif "_registry" in path_lower:
            return "registry"
        else:
            return "canonical_file"

    def _create_failure_signal(
        self,
        vehicle_id: str,
        error:  str,
        context: SignalContext
    ) -> FailureModeSignal:
        """Crea señal de falla"""

        source = SignalSource(
            event_id="",
            source_file=context.node_id,
            source_path=context.node_id,
            generation_timestamp=datetime.utcnow(),
            generator_vehicle="irrigation_executor"
        )

        return FailureModeSignal(
            context=context,
            source=source,
            execution_id=f"{vehicle_id}_{context.node_id}",
            failure_mode=FailureMode.TRANSFORMATION_ERROR,
            error_message=error,
            recoverable=True
        )

    def _deduplicate_signals(self, signals: List[Signal]) -> List[Signal]:
        """
        DEDUPLICATION: Remove duplicate signals based on content hash.
        
        This addresses the sophistication gap S3 where redundant signals
        are generated multiple times across SP3-SP10, wasting resources.
        
        Uses content-based hashing to identify semantically identical signals
        even if they have different signal_ids or timestamps.
        
        Args:
            signals: List of signals to deduplicate
            
        Returns:
            List of unique signals (duplicates removed)
        """
        unique_signals = []
        
        for signal in signals:
            self._deduplication_stats["total_signals"] += 1
            
            # Compute content hash for signal
            signal_hash = self._compute_signal_hash(signal)
            
            # Check if we've seen this signal before
            if signal_hash in self._signal_hashes:
                self._deduplication_stats["duplicates_detected"] += 1
                self._logger.debug(f"Duplicate signal detected: {signal_hash[:8]}")
                
                # Check cache for existing signal
                if self._cache_enabled and signal_hash in self._signal_cache:
                    self._deduplication_stats["cache_hits"] += 1
                    # Return cached signal instead of new one (preserves timestamps, etc.)
                    unique_signals.append(self._signal_cache[signal_hash])
                    continue
            else:
                # New unique signal
                self._signal_hashes.add(signal_hash)
                
                # Cache the signal if caching enabled
                if self._cache_enabled:
                    self._signal_cache[signal_hash] = signal
                
                unique_signals.append(signal)
        
        if len(signals) != len(unique_signals):
            self._logger.info(
                f"Deduplication: {len(signals)} → {len(unique_signals)} "
                f"({len(signals) - len(unique_signals)} duplicates removed)"
            )
        
        return unique_signals
    
    def _compute_signal_hash(self, signal: Signal) -> str:
        """
        Compute content-based hash for signal deduplication.
        
        Hash is based on semantic content (type, context, payload) not
        metadata (timestamp, signal_id) to identify true duplicates.
        
        Args:
            signal: Signal to hash
            
        Returns:
            SHA256 hash string
        """
        # Build hashable representation
        hash_content = {
            "signal_type": getattr(signal, 'signal_type', ''),
            "context": {
                "node_type": signal.context.node_type if hasattr(signal, 'context') and signal.context else '',
                "node_id": signal.context.node_id if hasattr(signal, 'context') and signal.context else '',
                "phase": signal.context.phase if hasattr(signal, 'context') and signal.context else '',
            },
            "payload": str(getattr(signal, 'payload', ''))[:1000],  # First 1000 chars to avoid huge payloads
        }
        
        # Convert to stable JSON string
        hash_string = json.dumps(hash_content, sort_keys=True)
        
        # Compute SHA256 hash
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def get_deduplication_stats(self) -> Dict[str, Any]:
        """
        Get deduplication and caching statistics.
        
        Returns:
            Dict with deduplication metrics
        """
        total = self._deduplication_stats["total_signals"]
        duplicates = self._deduplication_stats["duplicates_detected"]
        
        return {
            **self._deduplication_stats,
            "deduplication_rate": (duplicates / total * 100) if total > 0 else 0.0,
            "cache_hit_rate": (self._deduplication_stats["cache_hits"] / duplicates * 100) if duplicates > 0 else 0.0,
            "cache_size": len(self._signal_cache),
            "unique_signals": len(self._signal_hashes)
        }

    def get_execution_summary(self) -> Dict[str, Any]:
        """Resumen de ejecuciones"""
        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.success)
        failed = total - successful

        total_signals = sum(len(r.signals_generated) for r in self.execution_history)
        total_published = sum(r.signals_published for r in self.execution_history)

        avg_duration = (
            sum(r.duration_ms for r in self.execution_history) / total
            if total > 0 else 0
        )

        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "total_signals_generated": total_signals,
            "total_signals_published": total_published,
            "avg_duration_ms": avg_duration,
            "current_phase": self.current_phase.value,
            "deduplication_stats": self.get_deduplication_stats()
        }
