"""
SISAS Signals Registry

Registro central de tipos de señales y factory para crear instancias.
"""

from typing import Dict, Type, Optional, Any
from ..core.signal import Signal, SignalCategory

# Import all signal types
from .types.structural import (
    StructuralAlignmentSignal,
    SchemaConflictSignal,
    CanonicalMappingSignal
)

from .types.integrity import (
    EventPresenceSignal,
    EventCompletenessSignal,
    DataIntegritySignal
)

from .types.epistemic import (
    AnswerDeterminacySignal,
    AnswerSpecificitySignal,
    EmpiricalSupportSignal,
    MethodApplicationSignal
)

from .types.contrast import (
    DecisionDivergenceSignal,
    ConfidenceDropSignal,
    TemporalContrastSignal
)

from .types.operational import (
    ExecutionAttemptSignal,
    FailureModeSignal,
    LegacyActivitySignal,
    LegacyDependencySignal
)

from .types.consumption import (
    FrequencySignal,
    TemporalCouplingSignal,
    ConsumerHealthSignal
)


class SignalRegistry:
    """
    Registro central de todos los tipos de señales en el sistema SISAS.

    Responsabilidades:
    - Mapeo de tipo de señal → clase Python
    - Validación de tipos de señal
    - Factory para crear señales por tipo
    - Introspección de señales disponibles
    """

    # Mapeo de nombres de señal a clases
    _SIGNAL_TYPES: Dict[str, Type[Signal]] = {
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
        "ConsumerHealthSignal": ConsumerHealthSignal,
    }

    # Mapeo de categoría → tipos de señal
    _SIGNALS_BY_CATEGORY: Dict[SignalCategory, list[str]] = {
        SignalCategory.STRUCTURAL: [
            "StructuralAlignmentSignal",
            "SchemaConflictSignal",
            "CanonicalMappingSignal",
        ],
        SignalCategory.INTEGRITY: [
            "EventPresenceSignal",
            "EventCompletenessSignal",
            "DataIntegritySignal",
        ],
        SignalCategory.EPISTEMIC: [
            "AnswerDeterminacySignal",
            "AnswerSpecificitySignal",
            "EmpiricalSupportSignal",
            "MethodApplicationSignal",
        ],
        SignalCategory.CONTRAST: [
            "DecisionDivergenceSignal",
            "ConfidenceDropSignal",
            "TemporalContrastSignal",
        ],
        SignalCategory.OPERATIONAL: [
            "ExecutionAttemptSignal",
            "FailureModeSignal",
            "LegacyActivitySignal",
            "LegacyDependencySignal",
        ],
        SignalCategory.CONSUMPTION: [
            "FrequencySignal",
            "TemporalCouplingSignal",
            "ConsumerHealthSignal",
        ],
    }

    @classmethod
    def get_signal_class(cls, signal_type: str) -> Optional[Type[Signal]]:
        """
        Obtiene la clase de señal por tipo.

        Args:
            signal_type: Nombre del tipo de señal (ej: "StructuralAlignmentSignal")

        Returns:
            Clase de señal o None si no existe
        """
        return cls._SIGNAL_TYPES.get(signal_type)

    @classmethod
    def is_valid_signal_type(cls, signal_type: str) -> bool:
        """Verifica si un tipo de señal es válido"""
        return signal_type in cls._SIGNAL_TYPES

    @classmethod
    def get_all_signal_types(cls) -> list[str]:
        """Retorna lista de todos los tipos de señal disponibles"""
        return list(cls._SIGNAL_TYPES.keys())

    @classmethod
    def get_signals_by_category(cls, category: SignalCategory) -> list[str]:
        """Retorna lista de señales para una categoría"""
        return cls._SIGNALS_BY_CATEGORY.get(category, [])

    @classmethod
    def get_category_for_signal(cls, signal_type: str) -> Optional[SignalCategory]:
        """Obtiene la categoría de una señal"""
        signal_class = cls.get_signal_class(signal_type)
        if signal_class:
            # Create a dummy instance to get category
            # This assumes signal classes have a category property
            return signal_class.category if hasattr(signal_class, 'category') else None
        return None

    @classmethod
    def create_signal(cls, signal_type: str, **kwargs) -> Optional[Signal]:
        """
        Factory para crear señales por tipo.

        Args:
            signal_type: Tipo de señal a crear
            **kwargs: Argumentos para el constructor de la señal

        Returns:
            Instancia de señal o None si el tipo no existe

        Example:
            >>> signal = SignalRegistry.create_signal(
            ...     "StructuralAlignmentSignal",
            ...     context=context,
            ...     source=source,
            ...     alignment_status=AlignmentStatus.ALIGNED
            ... )
        """
        signal_class = cls.get_signal_class(signal_type)
        if signal_class:
            return signal_class(**kwargs)
        return None

    @classmethod
    def get_signal_count(cls) -> int:
        """Retorna el número total de tipos de señal registrados"""
        return len(cls._SIGNAL_TYPES)

    @classmethod
    def get_registry_info(cls) -> Dict[str, Any]:
        """Retorna información completa del registro"""
        return {
            "total_signals": cls.get_signal_count(),
            "signal_types": cls.get_all_signal_types(),
            "categories": {
                category.value: cls.get_signals_by_category(category)
                for category in SignalCategory
            }
        }
