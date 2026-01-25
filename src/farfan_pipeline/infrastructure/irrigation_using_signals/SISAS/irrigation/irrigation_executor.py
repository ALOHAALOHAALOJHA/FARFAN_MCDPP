# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/irrigation/irrigation_executor.py

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from enum import Enum
import json
import logging

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

    # =============================================================================
    # SOPHISTICATED PHASE 4 ENHANCEMENTS - ADVANCED SIGNAL ROUTING
    # =============================================================================
    
    def execute_phase4_with_advanced_routing(
        self,
        base_path: str = "",
        enable_batching: bool = True,
        enable_throttling: bool = True,
        enable_dlq: bool = True
    ) -> PhaseExecutionResult:
        """
        Execute Phase 4 with sophisticated signal routing capabilities:
        - Dynamic route optimization based on signal load
        - Signal batching for performance
        - Intelligent throttling
        - Dead-letter queue with auto-retry
        - Cross-phase dependency resolution
        
        Args:
            base_path: Base path for canonical files
            enable_batching: Enable signal batching
            enable_throttling: Enable adaptive throttling
            enable_dlq: Enable dead-letter queue
        
        Returns:
            Enhanced PhaseExecutionResult with routing metrics
        """
        from collections import deque
        from queue import Queue, PriorityQueue
        
        self._logger.info("Starting Phase 4 execution with advanced routing")
        
        phase_result = PhaseExecutionResult(phase="phase_04")
        routes = self.irrigation_map.get_routes_for_phase("phase_04")
        
        # Advanced routing components
        signal_batch_queue = deque(maxlen=100)
        route_priority_queue = PriorityQueue()
        dlq = []
        throttle_state = {"last_publish_time": datetime.utcnow(), "current_rate": 0.0}
        
        # Phase 4 specific: Track dimension aggregation dependencies
        dimension_dependencies = self._build_phase4_dependencies()
        
        # Prioritize routes based on load and dependencies
        for route in routes:
            if route.source.irrigability == IrrigabilityStatus.IRRIGABLE_NOW:
                priority = self._calculate_route_priority(route, dimension_dependencies)
                route_priority_queue.put((priority, route))
        
        self._logger.info(f"Phase 4: {route_priority_queue.qsize()} routes prioritized")
        
        # Process routes in priority order
        batch_counter = 0
        while not route_priority_queue.empty():
            priority, route = route_priority_queue.get()
            
            try:
                # Execute route with enhanced error handling
                result = self._execute_route_with_retry(route, base_path, max_retries=3)
                
                # Apply batching if enabled
                if enable_batching and result.signals_generated:
                    signal_batch_queue.extend(result.signals_generated)
                    
                    # Process batch when threshold reached
                    if len(signal_batch_queue) >= 20:
                        published_count = self._process_signal_batch(
                            list(signal_batch_queue),
                            route.vehicles,
                            throttle_state if enable_throttling else None
                        )
                        result.signals_published = published_count
                        signal_batch_queue.clear()
                        batch_counter += 1
                else:
                    # Process signals immediately
                    for signal in result.signals_generated:
                        if enable_throttling:
                            self._apply_throttling(throttle_state)
                        
                        # Publish with DLQ fallback
                        success = self._publish_signal_with_dlq(
                            signal, route.vehicles, dlq if enable_dlq else None
                        )
                        if success:
                            result.signals_published += 1
                
                phase_result.add_route_result(result)
                
            except Exception as e:
                self._logger.error(f"Route {route.source.file_path} failed: {e}")
                if enable_dlq:
                    dlq.append({
                        "route": route,
                        "error": str(e),
                        "timestamp": datetime.utcnow(),
                        "retry_count": 0
                    })
        
        # Process remaining batch
        if signal_batch_queue:
            published_count = self._process_signal_batch(
                list(signal_batch_queue),
                routes[0].vehicles if routes else [],
                throttle_state if enable_throttling else None
            )
            self._logger.info(f"Final batch processed: {published_count} signals")
            batch_counter += 1
        
        # Process DLQ retries
        if enable_dlq and dlq:
            retry_results = self._process_dlq_retries(dlq, base_path)
            self._logger.info(
                f"DLQ processed: {retry_results['succeeded']} succeeded, "
                f"{retry_results['failed']} failed"
            )
        
        phase_result.finalize()
        
        # Enhanced logging
        self._logger.info(
            f"Phase 4 completed with advanced routing: "
            f"{phase_result.successful_routes}/{phase_result.total_routes} routes successful, "
            f"{phase_result.total_signals_generated} signals generated, "
            f"{phase_result.total_signals_published} signals published, "
            f"{batch_counter} batches processed, "
            f"{len(dlq)} DLQ entries"
        )
        
        return phase_result
    
    def _build_phase4_dependencies(self) -> Dict[str, Set[str]]:
        """
        Build dependency graph for Phase 4 cross-phase dependencies.
        
        Phase 4 depends on Phase 3 outputs (300 micro scores -> 60 dimensions).
        """
        dependencies = {
            "dimension_aggregation": {"phase_03_micro_scoring"},
            "policy_area_aggregation": {"dimension_aggregation"},
            "cluster_aggregation": {"policy_area_aggregation"},
            "macro_aggregation": {"cluster_aggregation"}
        }
        return dependencies
    
    def _calculate_route_priority(
        self,
        route: IrrigationRoute,
        dependencies: Dict[str, Set[str]]
    ) -> int:
        """
        Calculate route priority based on load and dependencies.
        
        Lower number = higher priority.
        """
        base_priority = 100
        
        # Higher priority for routes with fewer dependencies
        route_key = route.source.stage or "default"
        if route_key in dependencies:
            dep_count = len(dependencies[route_key])
            base_priority += dep_count * 10
        
        # Higher priority for routes with more consumers (broader impact)
        base_priority -= len(route.targets) * 5
        
        # Higher priority for phase_04 specific routes
        if route.source.phase == "phase_04":
            base_priority -= 20
        
        return max(0, base_priority)
    
    def _execute_route_with_retry(
        self,
        route: IrrigationRoute,
        base_path: str,
        max_retries: int = 3
    ) -> IrrigationResult:
        """Execute route with retry logic"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = self.execute_route(route, base_path)
                if result.success:
                    return result
                last_error = result.errors[-1] if result.errors else "Unknown error"
            except Exception as e:
                last_error = str(e)
                self._logger.warning(
                    f"Route execution attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    import time
                    time.sleep(2 ** attempt)
        
        # All retries failed
        return IrrigationResult(
            route_id=route.source.file_path,
            success=False,
            errors=[f"Max retries ({max_retries}) exceeded: {last_error}"]
        )
    
    def _process_signal_batch(
        self,
        signals: List[Signal],
        vehicle_ids: List[str],
        throttle_state: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Process a batch of signals efficiently.
        
        Returns count of successfully published signals.
        """
        published_count = 0
        
        for signal in signals:
            if throttle_state:
                self._apply_throttling(throttle_state)
            
            for vehicle_id in vehicle_ids:
                if vehicle_id not in self.vehicles:
                    continue
                
                vehicle = self.vehicles[vehicle_id]
                if vehicle.publication_contract:
                    success, msg = vehicle.publish_signal(signal)
                    if success:
                        published_count += 1
                    else:
                        self._logger.debug(f"Batch publish failed: {msg}")
        
        return published_count
    
    def _apply_throttling(self, throttle_state: Dict[str, Any], max_rate: float = 100.0):
        """
        Apply adaptive throttling to prevent overwhelming consumers.
        
        Args:
            throttle_state: Dict tracking throttle state
            max_rate: Maximum signals per second
        """
        import time
        
        now = datetime.utcnow()
        elapsed = (now - throttle_state["last_publish_time"]).total_seconds()
        
        if elapsed < (1.0 / max_rate):
            # Sleep to maintain rate limit
            sleep_time = (1.0 / max_rate) - elapsed
            time.sleep(sleep_time)
        
        throttle_state["last_publish_time"] = datetime.utcnow()
        throttle_state["current_rate"] = 1.0 / max(0.001, elapsed)
    
    def _publish_signal_with_dlq(
        self,
        signal: Signal,
        vehicle_ids: List[str],
        dlq: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Publish signal with dead-letter queue fallback.
        
        Returns True if at least one vehicle published successfully.
        """
        any_success = False
        
        for vehicle_id in vehicle_ids:
            if vehicle_id not in self.vehicles:
                continue
            
            vehicle = self.vehicles[vehicle_id]
            if vehicle.publication_contract:
                try:
                    success, msg = vehicle.publish_signal(signal)
                    if success:
                        any_success = True
                    elif dlq is not None:
                        # Add to DLQ for retry
                        dlq.append({
                            "signal": signal,
                            "vehicle_id": vehicle_id,
                            "error": msg,
                            "timestamp": datetime.utcnow(),
                            "retry_count": 0
                        })
                except Exception as e:
                    self._logger.error(f"Signal publish exception: {e}")
                    if dlq is not None:
                        dlq.append({
                            "signal": signal,
                            "vehicle_id": vehicle_id,
                            "error": str(e),
                            "timestamp": datetime.utcnow(),
                            "retry_count": 0
                        })
        
        return any_success
    
    def _process_dlq_retries(
        self,
        dlq: List[Dict[str, Any]],
        base_path: str,
        max_retry_attempts: int = 3
    ) -> Dict[str, int]:
        """
        Process dead-letter queue with exponential backoff retry.
        
        NOTE: Uses time.sleep() for backoff. In high-concurrency production
        environments, consider replacing with async/await pattern or
        message queue with scheduled delivery for non-blocking delays.
        
        Returns dict with retry statistics.
        """
        import time
        
        results = {"succeeded": 0, "failed": 0, "exhausted": 0}
        
        for entry in dlq:
            if entry["retry_count"] >= max_retry_attempts:
                results["exhausted"] += 1
                self._logger.warning(
                    f"DLQ entry exhausted after {max_retry_attempts} attempts"
                )
                continue
            
            # Exponential backoff (capped at 60 seconds to prevent excessive delays)
            backoff_seconds = min(2 ** entry["retry_count"], 60)
            time.sleep(backoff_seconds)
            
            entry["retry_count"] += 1
            
            # Retry based on entry type
            if "signal" in entry and "vehicle_id" in entry:
                # Signal publish retry
                vehicle_id = entry["vehicle_id"]
                if vehicle_id in self.vehicles:
                    vehicle = self.vehicles[vehicle_id]
                    try:
                        success, msg = vehicle.publish_signal(entry["signal"])
                        if success:
                            results["succeeded"] += 1
                            self._logger.info(f"DLQ retry succeeded for signal")
                        else:
                            results["failed"] += 1
                    except Exception as e:
                        results["failed"] += 1
                        self._logger.error(f"DLQ retry failed: {e}")
            
            elif "route" in entry:
                # Route execution retry
                try:
                    result = self.execute_route(entry["route"], base_path)
                    if result.success:
                        results["succeeded"] += 1
                    else:
                        results["failed"] += 1
                except Exception as e:
                    results["failed"] += 1
                    self._logger.error(f"DLQ route retry failed: {e}")
        
        return results

    def get_execution_summary(self) -> Dict[str, Any]:
        """Resumen de ejecuciones con métricas mejoradas"""
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
            "publish_rate": (
                total_published / (sum(r.duration_ms for r in self.execution_history) / 1000)
                if sum(r.duration_ms for r in self.execution_history) > 0 else 0
            )
        }
