# src/farfan_pipeline/orchestration/phase_scheduler.py

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set
from datetime import datetime

from .dependency_graph import DependencyGraph, DependencyStatus


class SchedulingStrategy(Enum):
    """Estrategias de scheduling"""
    SEQUENTIAL = auto()        # Una fase a la vez, en orden topológico
    PARALLEL_MAX = auto()      # Máximo paralelismo posible
    PARALLEL_LIMITED = auto()  # Paralelismo limitado por configuración
    PRIORITY_BASED = auto()    # Basado en prioridades de fase
    RESOURCE_AWARE = auto()    # Considerando recursos disponibles


@dataclass
class SchedulingDecision:
    """
    Decisión de scheduling con justificación completa.
    
    Diseñado para ser completamente auditable.
    """
    # Fases seleccionadas para iniciar
    phases_to_start: List[str] = field(default_factory=list)
    
    # Fases que están esperando (dependencias no satisfechas)
    phases_waiting: List[str] = field(default_factory=list)
    
    # Fases bloqueadas (por fallo upstream)
    phases_blocked: List[str] = field(default_factory=list)
    
    # Justificación de la decisión
    rationale: str = ""
    
    # Detalles de cada decisión individual
    decision_details: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Metadatos
    strategy_used: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phases_to_start": self.phases_to_start,
            "phases_waiting": self.phases_waiting,
            "phases_blocked": self.phases_blocked,
            "rationale": self.rationale,
            "decision_details": self.decision_details,
            "strategy_used": self.strategy_used,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PhaseScheduler:
    """
    Scheduler de fases basado en el grafo de dependencias.
    
    RESPONSABILIDADES:
    1. Evaluar qué fases están listas para ejecutar
    2. Aplicar estrategia de scheduling configurada
    3. Respetar límites de paralelismo
    4. Generar decisiones auditables
    
    PRINCIPIOS:
    - Determinístico: Mismo estado → misma decisión
    - Explicable: Cada decisión tiene justificación
    - Configurable: Estrategia intercambiable
    """
    
    dependency_graph: DependencyGraph
    strategy: SchedulingStrategy = SchedulingStrategy.PARALLEL_LIMITED
    max_parallel: int = 4
    
    # Prioridades de fase (opcional)
    phase_priorities: Dict[str, int] = field(default_factory=dict)
    
    # Recursos disponibles (para RESOURCE_AWARE)
    available_resources: Dict[str, int] = field(default_factory=dict)
    
    def get_ready_phases(
        self,
        completed_phases: Set[str],
        failed_phases: Set[str],
        active_phases: Set[str],
        max_parallel: Optional[int] = None
    ) -> SchedulingDecision:
        """
        Determina qué fases deben iniciarse.
        
        Args:
            completed_phases: Fases ya completadas
            failed_phases: Fases que fallaron
            active_phases: Fases actualmente ejecutándose
            max_parallel: Override del límite de paralelismo
        
        Returns:
            SchedulingDecision con fases a iniciar y justificación
        """
        effective_max = max_parallel or self.max_parallel
        
        # Obtener fases candidatas del grafo
        ready_candidates = self.dependency_graph.get_ready_phases(
            completed=completed_phases,
            failed=failed_phases,
            active=active_phases
        )
        
        # Obtener fases esperando y bloqueadas
        all_phases = set(self.dependency_graph.nodes.keys())
        processed = completed_phases | failed_phases | active_phases
        remaining = all_phases - processed
        
        waiting = []
        blocked = []
        
        for phase_id in remaining:
            if phase_id in ready_candidates:
                continue
            
            node = self.dependency_graph.get_node(phase_id)
            if node: 
                if node.status == DependencyStatus.BLOCKED:
                    blocked.append(phase_id)
                else:
                    waiting.append(phase_id)
        
        # Aplicar estrategia
        if self.strategy == SchedulingStrategy.SEQUENTIAL:
            selected, details = self._apply_sequential_strategy(ready_candidates, active_phases)
        elif self.strategy == SchedulingStrategy.PARALLEL_MAX:
            selected, details = self._apply_parallel_max_strategy(ready_candidates, active_phases)
        elif self.strategy == SchedulingStrategy.PARALLEL_LIMITED:
            selected, details = self._apply_parallel_limited_strategy(
                ready_candidates, active_phases, effective_max
            )
        elif self.strategy == SchedulingStrategy.PRIORITY_BASED:
            selected, details = self._apply_priority_strategy(
                ready_candidates, active_phases, effective_max
            )
        elif self.strategy == SchedulingStrategy.RESOURCE_AWARE:
            selected, details = self._apply_resource_aware_strategy(
                ready_candidates, active_phases, effective_max
            )
        else:
            selected, details = self._apply_parallel_limited_strategy(
                ready_candidates, active_phases, effective_max
            )
        
        # Construir rationale
        rationale = self._build_rationale(
            selected=selected,
            ready_candidates=ready_candidates,
            active_phases=active_phases,
            effective_max=effective_max
        )
        
        return SchedulingDecision(
            phases_to_start=list(selected),
            phases_waiting=waiting,
            phases_blocked=blocked,
            rationale=rationale,
            decision_details=details,
            strategy_used=self.strategy.name
        )
    
    def _apply_sequential_strategy(
        self,
        ready: Set[str],
        active: Set[str]
    ) -> tuple[Set[str], Dict[str, Any]]:
        """
        Estrategia secuencial: una fase a la vez. 
        
        Si hay fases activas, no iniciar ninguna nueva.
        Si no hay activas, iniciar la primera en orden topológico.
        """
        details = {"strategy": "SEQUENTIAL"}
        
        if active:
            details["reason"] = f"Waiting for active phases to complete: {active}"
            return set(), details
        
        if not ready:
            details["reason"] = "No phases ready"
            return set(), details
        
        # Seleccionar primera en orden topológico
        selected = self._get_topological_first(ready)
        details["reason"] = f"Selected first in topological order: {selected}"
        
        return {selected} if selected else set(), details
    
    def _apply_parallel_max_strategy(
        self,
        ready: Set[str],
        active: Set[str]
    ) -> tuple[Set[str], Dict[str, Any]]:
        """
        Estrategia de máximo paralelismo: iniciar todas las fases listas.
        """
        details = {
            "strategy": "PARALLEL_MAX",
            "reason": f"Starting all {len(ready)} ready phases"
        }
        return ready, details
    
    def _apply_parallel_limited_strategy(
        self,
        ready: Set[str],
        active: Set[str],
        max_parallel: int
    ) -> tuple[Set[str], Dict[str, Any]]:
        """
        Estrategia de paralelismo limitado. 
        
        Inicia hasta (max_parallel - len(active)) fases nuevas.
        """
        details = {"strategy": "PARALLEL_LIMITED"}
        
        available_slots = max_parallel - len(active)
        
        if available_slots <= 0:
            details["reason"] = f"No available slots (active={len(active)}, max={max_parallel})"
            return set(), details
        
        if not ready:
            details["reason"] = "No phases ready"
            return set(), details
        
        # Seleccionar hasta available_slots fases en orden topológico
        selected = self._get_topological_n(ready, available_slots)
        details["reason"] = f"Selected {len(selected)} phases (slots available: {available_slots})"
        details["selected"] = list(selected)
        
        return selected, details
    
    def _apply_priority_strategy(
        self,
        ready: Set[str],
        active: Set[str],
        max_parallel: int
    ) -> tuple[Set[str], Dict[str, Any]]:
        """
        Estrategia basada en prioridades. 
        
        Selecciona fases de mayor prioridad primero.
        """
        details = {"strategy": "PRIORITY_BASED"}
        
        available_slots = max_parallel - len(active)
        
        if available_slots <= 0:
            details["reason"] = "No available slots"
            return set(), details
        
        if not ready:
            details["reason"] = "No phases ready"
            return set(), details
        
        # Ordenar por prioridad (mayor primero)
        sorted_by_priority = sorted(
            ready,
            key=lambda p: self.phase_priorities.get(p, 0),
            reverse=True
        )
        
        selected = set(sorted_by_priority[:available_slots])
        details["reason"] = f"Selected {len(selected)} highest priority phases"
        details["priorities"] = {p: self.phase_priorities.get(p, 0) for p in selected}
        
        return selected, details
    
    def _apply_resource_aware_strategy(
        self,
        ready: Set[str],
        active: Set[str],
        max_parallel: int
    ) -> tuple[Set[str], Dict[str, Any]]:
        """
        Estrategia basada en recursos disponibles.
        
        Selecciona fases considerando los recursos necesarios vs disponibles.
        """
        details = {"strategy": "RESOURCE_AWARE"}
        
        available_slots = max_parallel - len(active)
        
        if available_slots <= 0:
            details["reason"] = "No available slots"
            return set(), details
        
        if not ready:
            details["reason"] = "No phases ready"
            return set(), details
        
        # Filtrar fases que pueden ejecutarse con recursos disponibles
        selected = set()
        resource_usage = self.available_resources.copy()
        
        # Suponemos que cada fase tiene un requisito de recursos asociado
        for phase_id in ready:
            # Obtener requisitos de recursos para esta fase (default: 1 unidad de CPU)
            resource_req = self.dependency_graph.get_node(phase_id).resource_requirements if hasattr(self.dependency_graph.get_node(phase_id), 'resource_requirements') else {"cpu": 1, "memory": 1}
            
            # Verificar si tenemos recursos suficientes
            can_execute = True
            for resource, required in resource_req.items():
                available = resource_usage.get(resource, 0)
                if available < required:
                    can_execute = False
                    break
            
            # Si podemos ejecutarla y no excedemos el límite
            if can_execute and len(selected) < available_slots:
                selected.add(phase_id)
                # Actualizar uso de recursos
                for resource, required in resource_req.items():
                    resource_usage[resource] = resource_usage.get(resource, 0) - required
        
        details["reason"] = f"Selected {len(selected)} phases based on resource availability"
        details["resources_used"] = resource_usage
        
        return selected, details
    
    def _get_topological_first(self, phases: Set[str]) -> Optional[str]:
        """Obtiene la primera fase en orden topológico"""
        if not phases:
            return None
        
        # Fase con menos dependencias no completadas
        min_deps = float('inf')
        selected = None
        
        for phase_id in phases:
            upstream = self.dependency_graph.get_upstream_dependencies(phase_id)
            if len(upstream) < min_deps:
                min_deps = len(upstream)
                selected = phase_id
        
        return selected
    
    def _get_topological_n(self, phases: Set[str], n: int) -> Set[str]:
        """Obtiene las primeras N fases en orden topológico"""
        if not phases:
            return set()
        
        # Ordenar por número de dependencias (menor primero)
        sorted_phases = sorted(
            phases,
            key=lambda p: len(self.dependency_graph.get_upstream_dependencies(p))
        )
        
        return set(sorted_phases[:n])
    
    def _build_rationale(
        self,
        selected: Set[str],
        ready_candidates: Set[str],
        active_phases: Set[str],
        effective_max: int
    ) -> str:
        """Construye justificación legible para humanos"""
        parts = []
        
        parts.append(f"Strategy: {self.strategy.name}")
        parts.append(f"Max parallel: {effective_max}")
        parts.append(f"Currently active: {len(active_phases)} phases")
        parts.append(f"Ready candidates: {len(ready_candidates)} phases")
        parts.append(f"Selected to start: {len(selected)} phases")
        
        if selected: 
            parts.append(f"Starting: {', '.join(sorted(selected))}")
        else:
            if active_phases:
                parts.append("No new phases started (waiting for active phases)")
            else:
                parts.append("No phases ready to start")
        
        return " | ".join(parts)
    
    def set_phase_priority(self, phase_id: str, priority: int):
        """Establece prioridad de una fase"""
        self.phase_priorities[phase_id] = priority
    
    def get_scheduling_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del scheduler"""
        return {
            "strategy": self.strategy.name,
            "max_parallel": self.max_parallel,
            "phases_with_priority": len(self.phase_priorities),
            "priority_distribution": dict(self.phase_priorities)
        }
