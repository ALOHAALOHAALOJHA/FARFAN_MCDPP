# src/farfan_pipeline/orchestration/orchestration_state_machine.py

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime
import logging


class OrchestrationState(Enum):
    """Estados posibles del orquestador"""
    IDLE = auto()                    # Sin iniciar
    INITIALIZING = auto()            # Cargando configuración y validando
    RUNNING = auto()                 # Ejecutando fases
    PAUSED = auto()                  # Pausado manualmente
    STOPPING = auto()                # En proceso de detención
    STOPPED = auto()                 # Detenido manualmente
    COMPLETED = auto()               # Todas las fases completadas exitosamente
    COMPLETED_WITH_ERRORS = auto()   # Completado con algunas fallas
    FAILED = auto()                  # Fallo crítico


@dataclass(frozen=True)
class StateTransition:
    """
    Transición de estado inmutable.
    
    Registra el cambio de estado para auditoría.
    """
    from_state: OrchestrationState
    to_state: OrchestrationState
    timestamp: datetime
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_state": self.from_state.name,
            "to_state": self.to_state.name,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "metadata": self.metadata
        }


class InvalidStateTransitionError(Exception):
    """Error de transición de estado inválida"""
    pass


@dataclass
class OrchestrationStateMachine:
    """
    Máquina de estados finitos para la orquestación.
    
    RESPONSABILIDADES:
    1. Mantener estado actual del orquestador
    2. Validar transiciones de estado
    3. Registrar historial de transiciones (auditoría)
    4. Ejecutar callbacks en transiciones
    
    DIAGRAMA DE ESTADOS:
    
    ┌──────┐     ┌──────────────┐     ┌─────────┐
    │ IDLE │────►│ INITIALIZING │────►│ RUNNING │
    └──────┘     └──────────────┘     └────┬────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
              ┌──────────┐          ┌──────────┐          ┌────────────┐
              │  PAUSED  │◄────────►│ STOPPING │          │   FAILED   │
              └──────────┘          └────┬─────┘          └────────────┘
                                         │
                                         ▼
                                   ┌──────────┐
                                   │ STOPPED  │
                                   └──────────┘
                                   
                    RUNNING ───────► COMPLETED
                    RUNNING ───────► COMPLETED_WITH_ERRORS
    """
    
    current_state: OrchestrationState = OrchestrationState.IDLE
    
    # Historial de transiciones (para auditoría)
    transition_history: List[StateTransition] = field(default_factory=list)
    
    # Callbacks por transición
    _transition_callbacks: Dict[tuple, List[Callable]] = field(default_factory=dict)
    
    # Transiciones válidas
    _valid_transitions: Dict[OrchestrationState, Set[OrchestrationState]] = field(default=None)
    
    # Logger
    _logger: logging.Logger = field(default=None)
    
    def __post_init__(self):
        if self._logger is None:
            self._logger = logging.getLogger("SISAS.Orchestrator.StateMachine")
        
        # Definir transiciones válidas
        if self._valid_transitions is None:
            self._valid_transitions = {
                OrchestrationState.IDLE: {
                    OrchestrationState.INITIALIZING
                },
                OrchestrationState.INITIALIZING: {
                    OrchestrationState.RUNNING,
                    OrchestrationState.FAILED
                },
                OrchestrationState.RUNNING: {
                    OrchestrationState.PAUSED,
                    OrchestrationState.STOPPING,
                    OrchestrationState.COMPLETED,
                    OrchestrationState.COMPLETED_WITH_ERRORS,
                    OrchestrationState.FAILED
                },
                OrchestrationState.PAUSED: {
                    OrchestrationState.RUNNING,
                    OrchestrationState.STOPPING
                },
                OrchestrationState.STOPPING: {
                    OrchestrationState.STOPPED
                },
                OrchestrationState.STOPPED: set(),  # Estado terminal
                OrchestrationState.COMPLETED: set(),  # Estado terminal
                OrchestrationState.COMPLETED_WITH_ERRORS: set(),  # Estado terminal
                OrchestrationState.FAILED: set()  # Estado terminal
            }
    
    def transition_to(
        self,
        new_state: OrchestrationState,
        reason: str = "",
        metadata: Dict[str, Any] = None
    ) -> StateTransition:
        """
        Realiza transición a un nuevo estado.
        
        Args:
            new_state: Estado destino
            reason: Justificación de la transición
            metadata: Metadatos adicionales
        
        Returns:
            StateTransition registrada
        
        Raises:
            InvalidStateTransitionError: Si la transición no es válida
        """
        if not self._is_valid_transition(self.current_state, new_state):
            raise InvalidStateTransitionError(
                f"Invalid transition: {self.current_state.name} -> {new_state.name}"
            )
        
        # Crear registro de transición
        transition = StateTransition(
            from_state=self.current_state,
            to_state=new_state,
            timestamp=datetime.utcnow(),
            reason=reason,
            metadata=metadata or {}
        )
        
        # Ejecutar callbacks pre-transición
        self._execute_callbacks(self.current_state, new_state, "pre")
        
        # Actualizar estado
        old_state = self.current_state
        self.current_state = new_state
        
        # Registrar en historial
        self.transition_history.append(transition)
        
        # Ejecutar callbacks post-transición
        self._execute_callbacks(old_state, new_state, "post")
        
        self._logger.info(f"State transition: {old_state.name} -> {new_state.name} ({reason})")
        
        return transition
    
    def _is_valid_transition(
        self,
        from_state: OrchestrationState,
        to_state: OrchestrationState
    ) -> bool:
        """Verifica si una transición es válida"""
        valid_targets = self._valid_transitions.get(from_state, set())
        return to_state in valid_targets
    
    def can_transition_to(self, target_state: OrchestrationState) -> bool:
        """Verifica si se puede transicionar al estado objetivo"""
        return self._is_valid_transition(self.current_state, target_state)
    
    def get_valid_transitions(self) -> Set[OrchestrationState]:
        """Obtiene estados válidos desde el estado actual"""
        return self._valid_transitions.get(self.current_state, set()).copy()
    
    def register_callback(
        self,
        from_state: OrchestrationState,
        to_state: OrchestrationState,
        callback: Callable[[StateTransition], None],
        phase: str = "post"
    ):
        """
        Registra callback para una transición específica.
        
        Args:
            from_state: Estado origen
            to_state: Estado destino
            callback: Función a ejecutar
            phase: "pre" o "post" transición
        """
        key = (from_state, to_state, phase)
        if key not in self._transition_callbacks:
            self._transition_callbacks[key] = []
        self._transition_callbacks[key].append(callback)
    
    def _execute_callbacks(
        self,
        from_state: OrchestrationState,
        to_state: OrchestrationState,
        phase: str
    ):
        """Ejecuta callbacks registrados para una transición"""
        key = (from_state, to_state, phase)
        callbacks = self._transition_callbacks.get(key, [])
        
        for callback in callbacks:
            try:
                callback(StateTransition(
                    from_state=from_state,
                    to_state=to_state,
                    timestamp=datetime.utcnow()
                ))
            except Exception as e:
                self._logger.error(f"Callback error: {e}")
    
    def is_terminal(self) -> bool:
        """Verifica si está en estado terminal"""
        return len(self.get_valid_transitions()) == 0
    
    def is_running(self) -> bool:
        """Verifica si está en estado activo"""
        return self.current_state in {
            OrchestrationState.RUNNING,
            OrchestrationState.PAUSED
        }
    
    def get_history_summary(self) -> List[Dict[str, Any]]: 
        """Obtiene resumen del historial de transiciones"""
        return [t.to_dict() for t in self.transition_history]
    
    def get_time_in_state(self, state: OrchestrationState) -> float:
        """Calcula tiempo total en un estado específico (segundos)"""
        total_seconds = 0.0
        
        for i, transition in enumerate(self.transition_history):
            if transition.to_state == state:
                # Encontrar siguiente transición o usar now
                if i + 1 < len(self.transition_history):
                    end_time = self.transition_history[i + 1].timestamp
                else:
                    end_time = datetime.utcnow()
                
                duration = (end_time - transition.timestamp).total_seconds()
                total_seconds += duration
        
        return total_seconds
    
    def reset(self):
        """Resetea la máquina de estados"""
        self.current_state = OrchestrationState.IDLE
        self.transition_history.clear()