# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/orchestration/sisas_orchestrator.py

"""
DEPRECATED: This module is deprecated as of 2026-01-19.

SISAS orchestration is now integrated into:
    src/farfan_pipeline/orchestration/orchestrator.py (UnifiedOrchestrator)

The SignalDistributionOrchestrator (SDO) at:
    canonic_questionnaire_central/core/signal_distribution_orchestrator.py

is now the ONLY signal routing component, accessed via UnifiedOrchestrator.

This file will be removed in version 3.0.0.

---
Original Documentation (preserved for reference):

PILAR 2: ORQUESTACIÓN - Coordinación del flujo de irrigación

Este módulo implementa el segundo pilar de SISAS: la orquestación del flujo completo.

AXIOMA: La irrigación sigue un orden determinado por dependencias.
          Nada se irriga hasta que sus dependencias están satisfechas.
"""
import warnings
warnings.warn(
    "sisas_orchestrator is deprecated. Use UnifiedOrchestrator.",
    DeprecationWarning,
    stacklevel=2
)

from __future__ import annotations
import os
import json
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
import fnmatch

# Importaciones SISAS
from ..validators.depuration import (
    DepurationValidator,
    DepurationResult,
    FileRole
)
from ..vehicles import (
    BaseVehicle,
    VehicleCapabilities
)
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event, EventStore, EventType, EventPayload
from ..core.bus import BusRegistry, SignalBus, BusType
from ..core.contracts import ContractRegistry, IrrigationContract


# =============================================================================
# RESULT TYPES
# =============================================================================

@dataclass
class FileIrrigationResult:
    """
    Resultado de irrigar un archivo individual.

    Contiene el resultado completo de pasar un archivo por todo el flujo SISAS:
    1. Depuración
    2. Ejecución de vehicles
    3. Publicación de señales
    4. Notificación a consumers
    """
    file_path: str
    success: bool
    depuration_result: Optional[DepurationResult] = None
    vehicles_executed: List[str] = field(default_factory=list)
    signals_generated: int = 0
    consumers_notified: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "success": self.success,
            "depuration_passed": self.depuration_result.valid if self.depuration_result else False,
            "vehicles_executed": self.vehicles_executed,
            "signals_generated": self.signals_generated,
            "consumers_notified": self.consumers_notified,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "execution_time_seconds": self.execution_time_seconds
        }


@dataclass
class PhaseExecutionResult:
    """
    Resultado de ejecutar una fase completa.

    Una fase contiene múltiples archivos que se irrigan en orden.
    """
    phase_id: str
    success: bool
    files_processed: int = 0
    files_successful: int = 0
    files_failed: int = 0
    file_results: List[FileIrrigationResult] = field(default_factory=list)
    execution_time_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase_id": self.phase_id,
            "success": self.success,
            "files_processed": self.files_processed,
            "files_successful": self.files_successful,
            "files_failed": self.files_failed,
            "execution_time_seconds": self.execution_time_seconds,
            "errors": self.errors
        }


@dataclass
class OrchestrationSummary:
    """
    Resumen de una orquestración completa.
    """
    run_id: str
    start_time: str
    end_time: Optional[str] = None
    total_phases: int = 0
    phases_completed: int = 0
    phases_failed: int = 0
    total_files: int = 0
    files_successful: int = 0
    files_failed: int = 0
    signals_generated: int = 0
    execution_time_seconds: float = 0.0
    phase_results: List[PhaseExecutionResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        return self.files_successful / self.total_files if self.total_files > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_phases": self.total_phases,
            "phases_completed": self.phases_completed,
            "phases_failed": self.phases_failed,
            "total_files": self.total_files,
            "files_successful": self.files_successful,
            "files_failed": self.files_failed,
            "signals_generated": self.signals_generated,
            "execution_time_seconds": self.execution_time_seconds,
            "success_rate": f"{self.success_rate:.1%}",
            "errors": self.errors
        }


@dataclass
class OrchestrationResult:
    """
    Resultado completo de la orquestración.
    """
    success: bool
    summary: OrchestrationSummary
    file_results: Dict[str, FileIrrigationResult] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "summary": self.summary.to_dict(),
            "file_results_count": len(self.file_results)
        }


# =============================================================================
# DEPENDENCY GRAPH
# =============================================================================

class NodeStatus(Enum):
    """Estado de un nodo en el grafo"""
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class DependencyNode:
    """Nodo en el grafo de dependencias"""
    phase_id: str
    status: NodeStatus = NodeStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DependencyGraph:
    """
    Grafo de dependencias entre fases.

    Gestiona qué fases dependen de cuáles y calcula el orden de ejecución.
    """

    def __init__(self):
        self.nodes: Dict[str, DependencyNode] = {}
        self._adjacency_list: Dict[str, Set[str]] = {}  # phase_id → dependencies
        self._reverse_adjacency: Dict[str, Set[str]] = {}  # phase_id → dependents

    def add_node(self, phase_id: str, **metadata) -> DependencyNode:
        """Añade un nodo al grafo"""
        if phase_id not in self.nodes:
            node = DependencyNode(phase_id=phase_id, metadata=metadata)
            self.nodes[phase_id] = node
            self._adjacency_list[phase_id] = set()
            self._reverse_adjacency[phase_id] = set()
        return self.nodes[phase_id]

    def add_dependency(self, phase_id: str, depends_on: str):
        """Añade una dependencia: phase_id depende de depends_on"""
        if phase_id not in self.nodes:
            self.add_node(phase_id)
        if depends_on not in self.nodes:
            self.add_node(depends_on)

        self._adjacency_list[phase_id].add(depends_on)
        self._reverse_adjacency[depends_on].add(phase_id)

        self.nodes[phase_id].dependencies.append(depends_on)
        self.nodes[depends_on].dependents.append(phase_id)

    def get_ready_phases(self) -> List[str]:
        """
        Retorna fases que están listas para ejecutar (dependencias satisfechas).

        Una fase está lista si:
        - Su estado es PENDING o READY
        - Todas sus dependencias están COMPLETED
        """
        ready = []
        for phase_id, node in self.nodes.items():
            if node.status not in [NodeStatus.PENDING, NodeStatus.READY]:
                continue

            # Verificar que todas las dependencias estén completadas
            dependencies_satisfied = all(
                self.nodes[dep_id].status == NodeStatus.COMPLETED
                for dep_id in node.dependencies
                if dep_id in self.nodes
            )

            if dependencies_satisfied:
                ready.append(phase_id)

        return ready

    def mark_completed(self, phase_id: str):
        """Marca una fase como completada"""
        if phase_id in self.nodes:
            self.nodes[phase_id].status = NodeStatus.COMPLETED

    def mark_failed(self, phase_id: str):
        """Marca una fase como fallida"""
        if phase_id in self.nodes:
            self.nodes[phase_id].status = NodeStatus.FAILED

    def mark_running(self, phase_id: str):
        """Marca una fase como en ejecución"""
        if phase_id in self.nodes:
            self.nodes[phase_id].status = NodeStatus.RUNNING

    def topological_sort(self) -> List[str]:
        """
        Ordenamiento topológico del grafo.

        Retorna el orden en que deben ejecutarse las fases.
        Lanza ValueError si detecta un ciclo.
        """
        # Kahn's algorithm
        in_degree = {phase_id: len(deps) for phase_id, deps in self._adjacency_list.items()}
        queue = [phase_id for phase_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            phase_id = queue.pop(0)
            result.append(phase_id)

            # Reducir in-degree de dependientes
            for dependent in self._reverse_adjacency.get(phase_id, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self.nodes):
            raise ValueError("Ciclo detectado en el grafo de dependencias")

        return result

    def get_state_snapshot(self) -> Dict[str, str]:
        """Retorna snapshot del estado de todos los nodos"""
        return {
            phase_id: node.status.value
            for phase_id, node in self.nodes.items()
        }

    def validate(self) -> Dict[str, Any]:
        """Valida que el grafo es válido"""
        is_valid = True
        errors = []

        try:
            self.topological_sort()
        except ValueError as e:
            is_valid = False
            errors.append(f"Ciclo detectado: {str(e)}")

        # Verificar que no hay auto-dependencias
        for phase_id, deps in self._adjacency_list.items():
            if phase_id in deps:
                is_valid = False
                errors.append(f"Auto-dependencia detectada: {phase_id}")

        return {
            "is_valid": is_valid,
            "errors": errors
        }

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumen del grafo"""
        return {
            "total_nodes": len(self.nodes),
            "total_edges": sum(len(deps) for deps in self._adjacency_list.values()),
            "nodes_by_status": self._count_by_status()
        }

    def _count_by_status(self) -> Dict[str, int]:
        """Cuenta nodos por estado"""
        counts = {}
        for node in self.nodes.values():
            status = node.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

class SISASOrchestrator:
    """
    Orquestador maestro SISAS.

    Responsabilidad: Coordinar la ejecución completa de irrigación de archivos.

    Este es el PILAR 2 de SISAS: ORQUESTACIÓN.

    Flujo de orquestración:
        1. Construir grafo de dependencias
        2. Ordenamiento topológico
        3. Ejecución fase por fase:
            a. Depurar archivos de la fase
            b. Para cada archivo válido:
                i. Ejecutar vehicles asignados
                ii. Publicar señales a buses
                iii. Esperar a consumers
        4. Validación final

    A diferencia de MainOrchestrator (que orchestra fases completas),
    SISASOrchestrator irriga archivos individuales dentro de cada fase.

    Uso:
        orchestrator = SISASOrchestrator(
            base_path="canonic_questionnaire_central",
            vehicle_registry=vehicles,
            bus_registry=buses
        )

        result = orchestrator.orchestrate_full_irrigation()

        if result.success:
            print(f"Irrigación exitosa: {result.summary.files_successful} archivos")
    """

    def __init__(
        self,
        base_path: str = "canonic_questionnaire_central",
        vehicle_registry: Optional[Dict[str, BaseVehicle]] = None,
        bus_registry: Optional[BusRegistry] = None,
        contract_registry: Optional[ContractRegistry] = None,
        event_store: Optional[EventStore] = None,
        depurators: Optional[int] = 1
    ):
        """
        Inicializa el orquestador.

        Args:
            base_path: Path al questionnaire canónico
            vehicle_registry: Registro de vehículos disponibles
            bus_registry: Registro de buses de señales
            contract_registry: Registro de contratos
            event_store: Store de eventos (opcional)
            depurators: Número de depuradores paralelos
        """
        self.base_path = base_path
        self.vehicle_registry = vehicle_registry or {}
        self.bus_registry = bus_registry or BusRegistry()
        self.contract_registry = contract_registry or ContractRegistry()
        self.event_store = event_store or EventStore()
        self.depurators = depurators

        # Validador de depuración
        self.depuration_validator = DepurationValidator(base_path=base_path)

        # Grafo de dependencias
        self.dependency_graph = DependencyGraph()

        # Configuración de fases (se puede personalizar)
        self.phase_config = self._get_default_phase_config()

        # Vehicle assignments por patrón de archivo
        self.vehicle_assignments = self._get_default_vehicle_assignments()

        # Consumer assignments
        self.consumer_assignments = self._get_default_consumer_assignments()

    # =========================================================================
    # MAIN API: ORCHESTRATE FULL IRRIGATION
    # =========================================================================

    def orchestrate_full_irrigation(
        self,
        fail_fast: bool = False,
        validate_before: bool = True,
        phases: Optional[List[str]] = None
    ) -> OrchestrationResult:
        """
        Ejecuta la irrigación completa del sistema.

        Flujo:
        1. Construir grafo de dependencias
        2. Ordenamiento topológico
        3. Ejecutar cada fase en orden
        4. Validar estado final

        Args:
            fail_fast: Detener ejecución al primer error
            validate_before: Ejecutar validación antes de irrigar
            phases: Lista de fases a ejecutar (None = todas)

        Returns:
            OrchestrationResult con el resultado completo
        """
        start_time = datetime.utcnow()
        run_id = f"run_{start_time.strftime('%Y%m%d_%H%M%S')}"

        # Crear resultado
        summary = OrchestrationSummary(
            run_id=run_id,
            start_time=start_time.isoformat()
        )

        file_results: Dict[str, FileIrrigationResult] = {}

        try:
            # ═══════════════════════════════════════════════════════
            # PASO 1: CONSTRUIR GRAFO DE DEPENDENCIAS
            # ═══════════════════════════════════════════════════════
            self._build_dependency_graph()

            # Validar grafo
            graph_validation = self.dependency_graph.validate()
            if not graph_validation["is_valid"]:
                raise ValueError(f"Grafo de dependencias inválido: {graph_validation['errors']}")

            # ═══════════════════════════════════════════════════════
            # PASO 2: ORDENAMIENTO TOPOLOGICO
            # ═══════════════════════════════════════════════════════
            execution_order = self.dependency_graph.topological_sort()

            # Filtrar fases si se especificó
            if phases:
                execution_order = [p for p in execution_order if p in phases]
                summary.total_phases = len(execution_order)
            else:
                summary.total_phases = len(execution_order)

            # ═══════════════════════════════════════════════════════
            # PASO 3: EJECUCIÓN SECUENCIAL
            # ═══════════════════════════════════════════════════════
            for phase_id in execution_order:
                # Marcar como running
                self.dependency_graph.mark_running(phase_id)

                # Ejecutar fase
                phase_result = self._execute_phase(phase_id, fail_fast)
                summary.phase_results.append(phase_result)
                summary.files_processed += phase_result.files_processed
                summary.files_successful += phase_result.files_successful
                summary.files_failed += phase_result.files_failed
                summary.signals_generated += sum(
                    fr.signals_generated for fr in phase_result.file_results
                )

                # Agregar resultados de archivos
                for fr in phase_result.file_results:
                    file_results[fr.file_path] = fr

                # Actualizar estado
                if phase_result.success:
                    self.dependency_graph.mark_completed(phase_id)
                    summary.phases_completed += 1
                else:
                    self.dependency_graph.mark_failed(phase_id)
                    summary.phases_failed += 1
                    summary.errors.extend(phase_result.errors)

                    if fail_fast:
                        raise Exception(f"Fase {phase_id} falló y fail_fast=True")

            # ═══════════════════════════════════════════════════════
            # PASO 4: VALIDACIÓN FINAL
            # ═══════════════════════════════════════════════════════
            self._validate_final_state(summary)

            summary.end_time = datetime.utcnow().isoformat()
            summary.execution_time_seconds = (
                datetime.fromisoformat(summary.end_time) -
                start_time
            ).total_seconds()

            # Determinar éxito general
            success = (
                summary.phases_failed == 0 or
                (not fail_fast and summary.files_successful > 0)
            )

        except Exception as e:
            summary.errors.append(str(e))
            summary.end_time = datetime.utcnow().isoformat()
            summary.execution_time_seconds = (
                datetime.fromisoformat(summary.end_time) -
                start_time
            ).total_seconds()
            success = False

        return OrchestrationResult(
            success=success,
            summary=summary,
            file_results=file_results
        )

    # =========================================================================
    # PHASE EXECUTION
    # =========================================================================

    def _execute_phase(
        self,
        phase_id: str,
        fail_fast: bool
    ) -> PhaseExecutionResult:
        """
        Ejecuta una fase completa.

        Para cada archivo en la fase:
        1. Depurar
        2. Si válido: irrigar (vehicles → signals → consumers)
        """
        phase_start = datetime.utcnow()
        result = PhaseExecutionResult(phase_id=phase_id, success=True)

        # Obtener archivos de la fase
        files = self.phase_config.get(phase_id, {}).get("files", [])

        if not files:
            # Fase sin archivos - marcar como exitosa
            result.execution_time_seconds = 0
            return result

        # Procesar cada archivo
        for file_path in files:
            file_result = self._irrigate_file(file_path, phase_id)
            result.file_results.append(file_result)
            result.files_processed += 1

            if file_result.success:
                result.files_successful += 1
            else:
                result.files_failed += 1
                result.errors.extend(file_result.errors)
                result.success = False

                if fail_fast:
                    break

        result.execution_time_seconds = (
            datetime.utcnow() - phase_start
        ).total_seconds()

        return result

    def _irrigate_file(
        self,
        file_path: str,
        phase_id: str
    ) -> FileIrrigationResult:
        """
        Irriga un archivo individual.

        Flujo completo:
        1. Depurar archivo
        2. Si válido: ejecutar vehicles
        3. Publicar señales
        4. Notificar consumers
        """
        start_time = datetime.utcnow()
        result = FileIrrigationResult(file_path=file_path, success=False)

        try:
            # ═══════════════════════════════════════════════════════
            # PASO 1: DEPURACIÓN
            # ═══════════════════════════════════════════════════════
            depuration_result = self.depuration_validator.depurate(file_path)
            result.depuration_result = depuration_result

            if not depuration_result.valid:
                result.errors.extend([e.message for e in depuration_result.errors])
                result.warnings.extend([w.message for w in depuration_result.warnings])
                result.execution_time_seconds = (datetime.utcnow() - start_time).total_seconds()
                return result

            # ═══════════════════════════════════════════════════════
            # PASO 2: CARGAR ARCHIVO
            # ═══════════════════════════════════════════════════════
            full_path = os.path.join(self.base_path, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = json.load(f)

            # ═══════════════════════════════════════════════════════
            # PASO 3: EJECUTAR VEHICLES
            # ═══════════════════════════════════════════════════════
            vehicles = self._get_vehicles_for_file(file_path)
            all_signals = []

            for vehicle_id in vehicles:
                if vehicle_id not in self.vehicle_registry:
                    result.warnings.append(f"Vehicle {vehicle_id} not in registry")
                    continue

                vehicle = self.vehicle_registry[vehicle_id]

                # Crear contexto
                context = SignalContext(
                    node_type=self._infer_node_type(file_path),
                    node_id=os.path.basename(file_path),
                    phase=phase_id,
                    consumer_scope=phase_id
                )

                # Crear source
                source = SignalSource(
                    event_id=f"evt_{os.path.basename(file_path)}_{phase_id}",
                    source_file=os.path.basename(file_path),
                    source_path=file_path,
                    generation_timestamp=datetime.utcnow(),
                    generator_vehicle=vehicle_id
                )

                # Ejecutar vehicle
                try:
                    signals = vehicle.process(content, context)
                    all_signals.extend(signals)
                    result.vehicles_executed.append(vehicle_id)
                except Exception as e:
                    result.errors.append(f"Vehicle {vehicle_id} failed: {str(e)}")

            result.signals_generated = len(all_signals)

            # ═══════════════════════════════════════════════════════
            # PASO 4: PUBLICAR SEÑALES
            # ═══════════════════════════════════════════════════════
            consumers_notified = self._publish_signals(all_signals, file_path, phase_id)
            result.consumers_notified = consumers_notified

            # ═══════════════════════════════════════════════════════
            # PASO 5: REGISTRAR EVENTO
            # ═══════════════════════════════════════════════════════
            event = Event(
                event_type=EventType.CANONICAL_DATA_LOADED,
                source_file=os.path.basename(file_path),
                source_path=file_path,
                payload=EventPayload(data={
                    "signals_generated": len(all_signals),
                    "vehicles_executed": result.vehicles_executed,
                    "phase": phase_id
                }),
                phase=phase_id,
                consumer_scope=phase_id,
                source_component="sisas_orchestrator"
            )
            self.event_store.append(event)

            result.success = True

        except Exception as e:
            result.errors.append(f"Irrigation failed: {str(e)}")

        result.execution_time_seconds = (datetime.utcnow() - start_time).total_seconds()
        return result

    def _publish_signals(
        self,
        signals: List[Signal],
        file_path: str,
        phase_id: str
    ) -> int:
        """Publica señales a los buses apropiados"""
        consumers_notified = 0

        for signal in signals:
            # Determinar bus según tipo de señal
            bus_type = self._get_bus_for_signal(signal)

            if bus_type:
                bus = self.bus_registry.get_bus(str(bus_type))
                if bus:
                    try:
                        bus.publish(signal, "sisas_orchestrator")
                        # Contar consumers notificados (estimado)
                        consumers_notified += 1
                    except Exception as e:
                        pass  # Error publicando, no es crítico

        return consumers_notified

    # =========================================================================
    # DEPENDENCY GRAPH
    # =========================================================================

    def _build_dependency_graph(self):
        """Construye el grafo de dependencias entre fases"""
        # Configuración de dependencias según especificación
        dependencies = {
            "phase_00": [],  # Bootstrap - sin dependencias
            "phase_01": ["phase_00"],  # Enrichment - necesita bootstrap
            "phase_02": ["phase_01"],  # Factory - necesita enrichment
            "phase_03": ["phase_01", "phase_02"],  # Scoring - necesita enrichment y factory
            "phase_07": ["phase_02"],  # Meso - necesita factory
            "phase_08": ["phase_03"],  # Recommendations - necesita scoring
        }

        # Construir grafo
        for phase_id, deps in dependencies.items():
            self.dependency_graph.add_node(phase_id)
            for dep in deps:
                self.dependency_graph.add_dependency(phase_id, dep)

    def _validate_final_state(self, summary: OrchestrationSummary):
        """Valida que el estado final es consistente"""
        # Verificar que no quedan fases pendientes
        for phase_id, node in self.dependency_graph.nodes.items():
            if node.status == NodeStatus.RUNNING:
                summary.errors.append(f"Fase {phase_id} stuck in RUNNING state")
            elif node.status == NodeStatus.PENDING:
                # Fase nunca ejecutada - puede ser normal si no hay archivos
                pass

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_vehicles_for_file(self, file_path: str) -> List[str]:
        """Obtiene vehículos asignados para un archivo"""
        for pattern, vehicles in self.vehicle_assignments.items():
            if fnmatch.fnmatch(file_path, pattern):
                return vehicles

        # Valores predeterminados
        if "metadata" in file_path:
            return ["signal_quality_metrics", "signal_enhancement_integrator"]
        elif "questions" in file_path:
            return ["signal_context_scoper", "signal_evidence_extractor", "signal_intelligence_layer"]
        else:
            return ["signal_context_scoper", "signal_quality_metrics"]

    def _get_bus_for_signal(self, signal: Signal) -> Optional[BusType]:
        """Determina el bus apropiado para una señal"""
        signal_type = type(signal).__name__

        bus_mapping = {
            "StructuralAlignmentSignal": BusType.STRUCTURAL,
            "CanonicalMappingSignal": BusType.STRUCTURAL,
            "DataIntegritySignal": BusType.INTEGRITY,
            "EventCompletenessSignal": BusType.INTEGRITY,
            "EmpiricalSupportSignal": BusType.EPISTEMIC,
            "MethodApplicationSignal": BusType.EPISTEMIC,
            "AnswerDeterminacySignal": BusType.EPISTEMIC,
            "AnswerSpecificitySignal": BusType.EPISTEMIC,
        }

        return bus_mapping.get(signal_type)

    def _infer_node_type(self, file_path: str) -> str:
        """Infiere el tipo de nodo desde el path"""
        if "dimensions" in file_path:
            return "dimension"
        elif "policy_areas" in file_path:
            return "policy_area"
        elif "clusters" in file_path:
            return "cluster"
        elif "questions" in file_path:
            return "question"
        else:
            return "unknown"

    def _get_default_phase_config(self) -> Dict[str, Dict[str, Any]]:
        """Configuración predeterminada de fases"""
        return {
            "phase_00": {
                "name": "Bootstrap",
                "critical": True,
                "files": self._discover_files("phase_00")
            },
            "phase_01": {
                "name": "Enrichment",
                "critical": True,
                "files": self._discover_files("phase_01")
            },
            "phase_02": {
                "name": "Factory",
                "critical": True,
                "files": self._discover_files("phase_02")
            },
            "phase_03": {
                "name": "Scoring",
                "critical": False,
                "files": self._discover_files("phase_03")
            },
            "phase_07": {
                "name": "Meso",
                "critical": False,
                "files": self._discover_files("phase_07")
            },
            "phase_08": {
                "name": "Recommendations",
                "critical": False,
                "files": self._discover_files("phase_08")
            },
        }

    def _discover_files(self, phase_id: str) -> List[str]:
        """Descubre archivos para una fase"""
        # Mapeo de fase → patrones de archivo
        phase_patterns = {
            "phase_00": ["_registry/**/*.json", "config/**/*.json"],
            "phase_01": ["dimensions/**/*.json", "policy_areas/**/*.json"],
            "phase_02": ["patterns/**/*.json", "membership_criteria/**/*.json", "questions/**/*.json"],
            "phase_03": ["scoring_system.json"],
            "phase_07": ["clusters/**/*.json"],
            "phase_08": ["governance.json"]
        }

        patterns = phase_patterns.get(phase_id, [])
        files = []

        for pattern in patterns:
            # Buscar archivos que coinciden
            for root, dirs, filenames in os.walk(self.base_path):
                for filename in filenames:
                    if fnmatch.fnmatch(filename, pattern.split("/")[-1]):
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, self.base_path)
                        if fnmatch.fnmatch(rel_path, pattern):
                            files.append(rel_path)

        return sorted(set(files))

    def _get_default_vehicle_assignments(self) -> Dict[str, List[str]]:
        """Asignaciones predeterminadas de vehículos"""
        return {
            "**/metadata.json": ["signal_quality_metrics", "signal_enhancement_integrator"],
            "**/questions.json": ["signal_context_scoper", "signal_evidence_extractor", "signal_intelligence_layer"],
            "**/keywords.json": ["signal_registry", "signal_context_scoper"],
            "**/aggregation_rules.json": ["signal_quality_metrics", "signal_intelligence_layer"],
            "dimensions/**": ["signal_enhancement_integrator"],
            "policy_areas/**": ["signal_enhancement_integrator"],
            "clusters/**": ["signal_enhancement_integrator"],
        }

    def _get_default_consumer_assignments(self) -> Dict[str, List[str]]:
        """Asignaciones predeterminadas de consumidores"""
        return {
            "phase_00": ["phase0_bootstrap", "phase0_providers", "phase0_wiring_types"],
            "phase_01": ["phase1_signal_enrichment", "phase1_cpp_ingestion"],
            "phase_02": ["phase2_factory_consumer", "phase2_evidence_consumer", "phase2_contract_consumer"],
            "phase_03": ["phase3_scoring"],
            "phase_07": ["phase7_meso_consumer"],
            "phase_08": ["phase8_recommendations"],
        }
