# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/registry.py

from typing import Dict, Type, Optional, List
from ..core.signal import Signal

# Import all types to register them
from .types.structural import (
    StructuralAlignmentSignal, SchemaConflictSignal, CanonicalMappingSignal
)
from .types.integrity import (
    EventPresenceSignal, EventCompletenessSignal, DataIntegritySignal
)
from .types.epistemic import (
    AnswerDeterminacySignal, AnswerSpecificitySignal, EmpiricalSupportSignal, MethodApplicationSignal
)
from .types.contrast import (
    DecisionDivergenceSignal, ConfidenceDropSignal, TemporalContrastSignal
)
from .types.operational import (
    ExecutionAttemptSignal, FailureModeSignal, LegacyActivitySignal, LegacyDependencySignal
)
from .types.consumption import (
    FrequencySignal, TemporalCouplingSignal, ConsumerHealthSignal
)

class SignalRegistry:
    """
    Registro de clases de señales para instanciación dinámica.
    Diferente de SignalVocabulary (que valida reglas), este registro
    mapea nombres de tipo a implementaciones de clase Python.
    """
    
    _registry: Dict[str, Type[Signal]] = {
        # Structural
        "StructuralAlignmentSignal": StructuralAlignmentSignal,
        "SchemaConflictSignal": SchemaConflictSignal,
        "CanonicalMappingSignal": CanonicalMappingSignal,
        
        # Integrity
        "EventPresenceSignal": EventPresenceSignal,
        "EventCompletenessSignal": EventCompletenessSignal,
        "DataIntegritySignal": DataIntegritySignal,
        
        # Epistemic
        "AnswerDeterminacySignal": AnswerDeterminacySignal,
        "AnswerSpecificitySignal": AnswerSpecificitySignal,
        "EmpiricalSupportSignal": EmpiricalSupportSignal,
        "MethodApplicationSignal": MethodApplicationSignal,
        
        # Contrast
        "DecisionDivergenceSignal": DecisionDivergenceSignal,
        "ConfidenceDropSignal": ConfidenceDropSignal,
        "TemporalContrastSignal": TemporalContrastSignal,
        
        # Operational
        "ExecutionAttemptSignal": ExecutionAttemptSignal,
        "FailureModeSignal": FailureModeSignal,
        "LegacyActivitySignal": LegacyActivitySignal,
        "LegacyDependencySignal": LegacyDependencySignal,
        
        # Consumption
        "FrequencySignal": FrequencySignal,
        "TemporalCouplingSignal": TemporalCouplingSignal,
        "ConsumerHealthSignal": ConsumerHealthSignal
    }
    
    @classmethod
    def get_class(cls, signal_type: str) -> Optional[Type[Signal]]:
        """Obtiene la clase correspondiente a un tipo de señal"""
        return cls._registry.get(signal_type)
        
    @classmethod
    def register(cls, signal_type: str, signal_class: Type[Signal]):
        """Registra una nueva clase de señal"""
        cls._registry[signal_type] = signal_class
        
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Obtiene todos los tipos registrados"""
        return list(cls._registry.keys())
