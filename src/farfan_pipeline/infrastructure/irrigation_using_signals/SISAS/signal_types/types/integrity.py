# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/integrity.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class PresenceStatus(Enum):
    """Estados de presencia de evento"""
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    PARTIAL = "PARTIAL"
    DUPLICATED = "DUPLICATED"


class CompletenessLevel(Enum):
    """Niveles de completitud"""
    COMPLETE = "COMPLETE"            # 100%
    MOSTLY_COMPLETE = "MOSTLY_COMPLETE"  # 80-99%
    INCOMPLETE = "INCOMPLETE"        # 50-79%
    SEVERELY_INCOMPLETE = "SEVERELY_INCOMPLETE"  # 1-49%
    EMPTY = "EMPTY"                  # 0%


class IntegrityViolationType(Enum):
    """Tipos de violación de integridad"""
    MISSING_REFERENCE = "missing_reference"
    CIRCULAR_REFERENCE = "circular_reference"
    ORPHANED_DATA = "orphaned_data"
    DUPLICATE_KEY = "duplicate_key"
    CONSTRAINT_VIOLATION = "constraint_violation"


@dataclass
class EventPresenceSignal(Signal):
    """
    Señal que indica si un evento esperado existe.

    Uso:  Verificar que AnswerSubmitted para Q147 existe.
    """

    signal_type: str = field(default="EventPresenceSignal", init=False)

    # Payload específico
    expected_event_type: str = ""
    presence_status: PresenceStatus = PresenceStatus.ABSENT
    event_count: int = 0
    first_occurrence:  Optional[str] = None  # timestamp ISO
    last_occurrence: Optional[str] = None
    
    # Información adicional
    expected_count: Optional[int] = None
    duplicate_ids: List[str] = field(default_factory=list)
    event_ids: List[str] = field(default_factory=list)

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.INTEGRITY

    def is_anomalous(self) -> bool:
        """Detecta si hay anomalías en la presencia"""
        if self.presence_status == PresenceStatus.ABSENT and self.expected_count and self.expected_count > 0:
            return True  # Se esperaba pero no está
        
        if self.presence_status == PresenceStatus.DUPLICATED:
            return True  # Duplicados no esperados
        
        if self.expected_count and self.event_count != self.expected_count:
            return True  # Cuenta no coincide
        
        return False

    def get_presence_ratio(self) -> float:
        """Retorna ratio de presencia (actual/esperado)"""
        if self.expected_count and self.expected_count > 0:
            return min(1.0, self.event_count / self.expected_count)
        return 1.0 if self.event_count > 0 else 0.0

    def get_analysis(self) -> Dict[str, Any]:
        """Análisis completo de presencia"""
        return {
            "status": self.presence_status.value,
            "count": self.event_count,
            "expected": self.expected_count,
            "is_anomalous": self.is_anomalous(),
            "presence_ratio": self.get_presence_ratio(),
            "has_duplicates": len(self.duplicate_ids) > 0,
            "duplicate_count": len(self.duplicate_ids),
            "first_seen": self.first_occurrence,
            "last_seen": self.last_occurrence
        }


@dataclass
class EventCompletenessSignal(Signal):
    """
    Señal que indica qué tan completo es un evento.

    Uso:  Verificar que el evento tiene todos los campos requeridos.
    """

    signal_type: str = field(default="EventCompletenessSignal", init=False)

    # Payload específico
    completeness_level: CompletenessLevel = CompletenessLevel.EMPTY
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    present_fields: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    
    # Campos con problemas
    null_fields: List[str] = field(default_factory=list)
    empty_string_fields: List[str] = field(default_factory=list)
    
    completeness_score: float = 0.0  # 0.0 a 1.0
    data_quality_score: float = 0.0  # Considera nulls y empty

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.INTEGRITY

    def __post_init__(self):
        super().__post_init__()
        # Calcular campos faltantes
        self.missing_fields = [
            f for f in self.required_fields if f not in self.present_fields
        ]
        # Calcular score de completitud
        if self.required_fields:
            self.completeness_score = len(self.present_fields) / len(self.required_fields)
        else:
            self.completeness_score = 1.0
        
        # Calcular score de calidad (penaliza nulls y empty)
        total_fields = len(self.required_fields) + len(self.optional_fields)
        if total_fields > 0:
            problems = len(self.missing_fields) + len(self.null_fields) + len(self.empty_string_fields)
            self.data_quality_score = max(0.0, 1.0 - (problems / total_fields))
        else:
            self.data_quality_score = 1.0
        
        # Determinar nivel
        if self.completeness_score == 1.0:
            self.completeness_level = CompletenessLevel.COMPLETE
        elif self.completeness_score >= 0.8:
            self.completeness_level = CompletenessLevel.MOSTLY_COMPLETE
        elif self.completeness_score >= 0.5:
            self.completeness_level = CompletenessLevel.INCOMPLETE
        elif self.completeness_score > 0:
            self.completeness_level = CompletenessLevel.SEVERELY_INCOMPLETE
        else:
            self.completeness_level = CompletenessLevel.EMPTY

    def get_critical_missing(self) -> List[str]:
        """Retorna campos críticos faltantes"""
        # Asumimos que los primeros en la lista son los más críticos
        return self.missing_fields[:5]

    def is_usable(self) -> bool:
        """Determina si el evento es usable a pesar de estar incompleto"""
        return self.completeness_level in [
            CompletenessLevel.COMPLETE,
            CompletenessLevel.MOSTLY_COMPLETE
        ]

    def get_quality_report(self) -> Dict[str, Any]:
        """Reporte detallado de calidad"""
        return {
            "completeness_level": self.completeness_level.value,
            "completeness_score": self.completeness_score,
            "data_quality_score": self.data_quality_score,
            "is_usable": self.is_usable(),
            "required_fields_count": len(self.required_fields),
            "present_count": len(self.present_fields),
            "missing_count": len(self.missing_fields),
            "null_count": len(self.null_fields),
            "empty_count": len(self.empty_string_fields),
            "critical_missing": self.get_critical_missing()
        }


@dataclass
class DataIntegritySignal(Signal):
    """
    Señal que indica la integridad referencial de los datos.

    Uso: Verificar que las referencias entre archivos son válidas.
    """

    signal_type: str = field(default="DataIntegritySignal", init=False)

    # Payload específico
    source_file: str = ""
    source_file_type: str = ""  # "question", "dimension", "policy_area"
    referenced_files: List[str] = field(default_factory=list)
    valid_references: List[str] = field(default_factory=list)
    broken_references: List[str] = field(default_factory=list)
    
    # Violaciones específicas
    violations: List[Dict[str, Any]] = field(default_factory=list)
    # {"type": "missing_reference", "reference": "PA03", "context": "questions.json"}
    
    integrity_score: float = 0.0
    violation_types: Set[IntegrityViolationType] = field(default_factory=set)

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.INTEGRITY

    def __post_init__(self):
        super().__post_init__()
        # Calcular score de integridad
        if self.referenced_files:
            self.integrity_score = len(self.valid_references) / len(self.referenced_files)
        else:
            self.integrity_score = 1.0
        
        # Extraer tipos de violaciones
        for violation in self.violations:
            v_type = violation.get("type")
            if v_type:
                try:
                    self.violation_types.add(IntegrityViolationType(v_type))
                except ValueError:
                    pass  # Tipo no reconocido

    def has_critical_violations(self) -> bool:
        """Verifica si hay violaciones críticas"""
        critical_types = {
            IntegrityViolationType.CIRCULAR_REFERENCE,
            IntegrityViolationType.DUPLICATE_KEY
        }
        return bool(self.violation_types & critical_types)

    def get_fixable_violations(self) -> List[Dict[str, Any]]:
        """Retorna violaciones que pueden corregirse automáticamente"""
        fixable = []
        for violation in self.violations:
            v_type = violation.get("type")
            if v_type in ["missing_reference", "orphaned_data"]:
                fixable.append(violation)
        return fixable

    def generate_fix_plan(self) -> List[Dict[str, Any]]:
        """Genera plan de corrección"""
        plan = []
        
        for violation in self.get_fixable_violations():
            if violation["type"] == "missing_reference":
                plan.append({
                    "action": "create_reference",
                    "target": violation["reference"],
                    "priority": "high"
                })
            elif violation["type"] == "orphaned_data":
                plan.append({
                    "action": "link_or_archive",
                    "target": violation["reference"],
                    "priority": "medium"
                })
        
        return plan

    def get_integrity_report(self) -> Dict[str, Any]:
        """Reporte completo de integridad"""
        return {
            "integrity_score": self.integrity_score,
            "total_references": len(self.referenced_files),
            "valid_references": len(self.valid_references),
            "broken_references": len(self.broken_references),
            "violation_count": len(self.violations),
            "violation_types": [v.value for v in self.violation_types],
            "has_critical_violations": self.has_critical_violations(),
            "fixable_count": len(self.get_fixable_violations()),
            "health_status": "critical" if self.integrity_score < 0.5 else 
                           "warning" if self.integrity_score < 0.8 else "healthy"
        }

