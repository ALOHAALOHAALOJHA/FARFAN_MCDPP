# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/structural.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from datetime import datetime

from ...core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class AlignmentStatus(Enum):
    """Estados de alineación estructural"""
    ALIGNED = "ALIGNED"
    PARTIAL = "PARTIAL"
    MISALIGNED = "MISALIGNED"
    UNKNOWN = "UNKNOWN"


class AlignmentSeverity(Enum):
    """Severidad de problemas de alineación"""
    CRITICAL = "CRITICAL"  # Impide operación
    HIGH = "HIGH"          # Requiere atención inmediata
    MEDIUM = "MEDIUM"      # Debe corregirse pronto
    LOW = "LOW"            # Puede esperar
    INFO = "INFO"          # Solo informativo


@dataclass
class StructuralAlignmentSignal(Signal):
    """
    Señal que indica si un dato/evento mapea correctamente
    a la estructura canónica.

    Uso:  Verificar que Q147 existe, está ligada a PA03, tiene métodos definidos.
    """

    signal_type: str = field(default="StructuralAlignmentSignal", init=False)

    # Payload específico
    alignment_status: AlignmentStatus = AlignmentStatus.UNKNOWN
    canonical_path: str = ""  # Path canónico esperado
    actual_path: str = ""     # Path real encontrado
    missing_elements: List[str] = field(default_factory=list)
    extra_elements: List[str] = field(default_factory=list)
    mismatched_elements: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # {"field_name": {"expected": "type", "actual": "other_type"}}

    severity: AlignmentSeverity = AlignmentSeverity.INFO
    auto_correctable: bool = False
    correction_suggestions: List[str] = field(default_factory=list)

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.STRUCTURAL

    def compute_alignment_score(self) -> float:
        """Calcula score de alineación 0.0 a 1.0"""
        if self.alignment_status == AlignmentStatus.ALIGNED:
            return 1.0
        elif self.alignment_status == AlignmentStatus.PARTIAL:
            total_issues = len(self.missing_elements) + len(self.extra_elements) + len(self.mismatched_elements)
            if total_issues == 0:
                return 0.5
            # Penalizar más los mismatches que los missing/extra
            penalty = (len(self.missing_elements) * 0.1 + 
                      len(self.extra_elements) * 0.05 +
                      len(self.mismatched_elements) * 0.15)
            return max(0.1, 1.0 - penalty)
        elif self.alignment_status == AlignmentStatus.MISALIGNED:
            return 0.0
        return 0.0

    def get_issues_summary(self) -> Dict[str, Any]:
        """Retorna resumen de problemas encontrados"""
        return {
            "total_issues": len(self.missing_elements) + len(self.extra_elements) + len(self.mismatched_elements),
            "missing_count": len(self.missing_elements),
            "extra_count": len(self.extra_elements),
            "mismatch_count": len(self.mismatched_elements),
            "severity": self.severity.value,
            "auto_correctable": self.auto_correctable,
            "alignment_score": self.compute_alignment_score()
        }

    def is_critical(self) -> bool:
        """Verifica si hay problemas críticos"""
        return self.severity in [AlignmentSeverity.CRITICAL, AlignmentSeverity.HIGH]

    def generate_correction_plan(self) -> List[Dict[str, Any]]:
        """Genera plan de corrección automática"""
        plan = []
        
        for missing in self.missing_elements:
            plan.append({
                "action": "add",
                "element": missing,
                "priority": "high" if self.severity == AlignmentSeverity.CRITICAL else "medium"
            })
        
        for extra in self.extra_elements:
            plan.append({
                "action": "remove_or_ignore",
                "element": extra,
                "priority": "low"
            })
        
        for field, mismatch in self.mismatched_elements.items():
            plan.append({
                "action": "correct_type",
                "element": field,
                "expected": mismatch.get("expected"),
                "actual": mismatch.get("actual"),
                "priority": "high"
            })
        
        return plan


class ConflictType(Enum):
    """Tipos de conflicto de esquema"""
    MISSING_FIELD = "missing_field"
    TYPE_MISMATCH = "type_mismatch"
    EXTRA_FIELD = "extra_field"
    VALUE_OUT_OF_RANGE = "value_out_of_range"
    INVALID_FORMAT = "invalid_format"
    CONSTRAINT_VIOLATION = "constraint_violation"


@dataclass
class SchemaConflictSignal(Signal):
    """
    Señal que indica conflicto de esquemas entre datos.

    Uso: Detectar cuando un archivo tiene estructura diferente a la esperada.
    """

    signal_type: str = field(default="SchemaConflictSignal", init=False)

    # Payload específico
    expected_schema_version: str = ""
    actual_schema_version: str = ""
    conflict_type: ConflictType = ConflictType.TYPE_MISMATCH
    conflicting_fields: List[Dict[str, Any]] = field(default_factory=list)
    # Cada conflicto:  {"field": "name", "expected": "string", "actual": "int", "path": "data.user.name"}

    is_breaking: bool = False  # ¿El conflicto rompe la compatibilidad?
    suggested_resolution: str = ""
    resolution_steps: List[str] = field(default_factory=list)
    
    # Información adicional
    affected_data_count: int = 0
    data_loss_risk: bool = False
    backward_compatible: bool = True

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.STRUCTURAL

    def get_severity(self) -> AlignmentSeverity:
        """Determina severidad del conflicto"""
        if self.is_breaking or self.data_loss_risk:
            return AlignmentSeverity.CRITICAL
        elif len(self.conflicting_fields) > 10:
            return AlignmentSeverity.HIGH
        elif not self.backward_compatible:
            return AlignmentSeverity.MEDIUM
        return AlignmentSeverity.LOW

    def can_auto_migrate(self) -> bool:
        """Verifica si se puede migrar automáticamente"""
        return (
            not self.data_loss_risk and
            self.backward_compatible and
            len(self.resolution_steps) > 0
        )

    def get_migration_plan(self) -> Dict[str, Any]:
        """Genera plan de migración"""
        return {
            "can_auto_migrate": self.can_auto_migrate(),
            "severity": self.get_severity().value,
            "steps": self.resolution_steps,
            "affected_fields": [f["field"] for f in self.conflicting_fields],
            "data_loss_risk": self.data_loss_risk,
            "estimated_duration": len(self.conflicting_fields) * 0.5  # segundos estimados
        }


class MappingQuality(Enum):
    """Calidad del mapeo canónico"""
    EXCELLENT = "EXCELLENT"      # 95-100%
    GOOD = "GOOD"                # 80-94%
    ACCEPTABLE = "ACCEPTABLE"    # 60-79%
    POOR = "POOR"                # 40-59%
    CRITICAL = "CRITICAL"        # < 40%


@dataclass
class CanonicalMappingSignal(Signal):
    """
    Señal que indica el resultado de mapear un ítem a entidades canónicas.

    Uso: Verificar que una respuesta se mapea a policy_area, dimension, etc.
    """

    signal_type: str = field(default="CanonicalMappingSignal", init=False)

    # Payload específico
    source_item_id: str = ""
    source_item_type: str = ""  # "question", "response", "document"
    mapped_entities: Dict[str, str] = field(default_factory=dict)
    # Ejemplo: {"policy_area": "PA03", "dimension": "DIM02", "cluster": "CL01"}

    unmapped_aspects: List[str] = field(default_factory=list)
    mapping_completeness: float = 0.0  # 0.0 a 1.0
    mapping_confidence_scores: Dict[str, float] = field(default_factory=dict)
    # {"policy_area": 0.95, "dimension": 0.87}

    # Información del proceso de mapeo
    mapping_method: str = ""  # "rule_based", "ml_based", "hybrid"
    processing_time_ms: float = 0.0
    alternative_mappings: List[Dict[str, str]] = field(default_factory=list)

    @property
    def category(self) -> SignalCategory:
        return SignalCategory.STRUCTURAL

    def get_mapping_quality(self) -> MappingQuality:
        """Determina calidad del mapeo"""
        completeness_pct = self.mapping_completeness * 100
        
        if completeness_pct >= 95:
            return MappingQuality.EXCELLENT
        elif completeness_pct >= 80:
            return MappingQuality.GOOD
        elif completeness_pct >= 60:
            return MappingQuality.ACCEPTABLE
        elif completeness_pct >= 40:
            return MappingQuality.POOR
        return MappingQuality.CRITICAL

    def get_confidence_summary(self) -> Dict[str, Any]:
        """Resumen de confianzas de mapeo"""
        if not self.mapping_confidence_scores:
            return {"average": 0.0, "min": 0.0, "max": 0.0}
        
        scores = list(self.mapping_confidence_scores.values())
        return {
            "average": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "count": len(scores)
        }

    def requires_review(self) -> bool:
        """Determina si requiere revisión manual"""
        quality = self.get_mapping_quality()
        low_confidence = any(score < 0.7 for score in self.mapping_confidence_scores.values())
        
        return (
            quality in [MappingQuality.POOR, MappingQuality.CRITICAL] or
            low_confidence or
            len(self.unmapped_aspects) > 3
        )

    def get_improvement_suggestions(self) -> List[str]:
        """Genera sugerencias de mejora"""
        suggestions = []
        
        if len(self.unmapped_aspects) > 0:
            suggestions.append(f"Map {len(self.unmapped_aspects)} unmapped aspects: {', '.join(self.unmapped_aspects[:3])}")
        
        for entity, score in self.mapping_confidence_scores.items():
            if score < 0.7:
                suggestions.append(f"Improve confidence for {entity} (current: {score:.2f})")
        
        if len(self.alternative_mappings) > 0:
            suggestions.append(f"Review {len(self.alternative_mappings)} alternative mappings")
        
        return suggestions

