# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/signals/types/structural.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from ... core.signal import Signal, SignalCategory, SignalContext, SignalSource, SignalConfidence


class AlignmentStatus(Enum):
    """Estados de alineación estructural"""
    ALIGNED = "ALIGNED"
    PARTIAL = "PARTIAL"
    MISALIGNED = "MISALIGNED"
    UNKNOWN = "UNKNOWN"


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
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.STRUCTURAL
    
    def compute_alignment_score(self) -> float:
        """Calcula score de alineación 0.0 a 1.0"""
        if self.alignment_status == AlignmentStatus.ALIGNED: 
            return 1.0
        elif self.alignment_status == AlignmentStatus.PARTIAL: 
            total_issues = len(self.missing_elements) + len(self.extra_elements)
            if total_issues == 0:
                return 0.5
            return max(0.1, 0.5 - (total_issues * 0.1))
        elif self.alignment_status == AlignmentStatus.MISALIGNED: 
            return 0.0
        return 0.0


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
    conflict_type: str = ""  # "missing_field", "type_mismatch", "extra_field"
    conflicting_fields: List[Dict[str, Any]] = field(default_factory=list)
    # Cada conflicto:  {"field": "name", "expected": "string", "actual": "int"}
    
    is_breaking: bool = False  # ¿El conflicto rompe la compatibilidad?
    suggested_resolution: str = ""
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory. STRUCTURAL


@dataclass  
class CanonicalMappingSignal(Signal):
    """
    Señal que indica el resultado de mapear un ítem a entidades canónicas.
    
    Uso: Verificar que una respuesta se mapea a policy_area, dimension, etc.
    """
    
    signal_type: str = field(default="CanonicalMappingSignal", init=False)
    
    # Payload específico
    source_item_id: str = ""
    mapped_entities: Dict[str, str] = field(default_factory=dict)
    # Ejemplo: {"policy_area": "PA03", "dimension": "DIM02", "cluster": "CL01"}
    
    unmapped_aspects: List[str] = field(default_factory=list)
    mapping_completeness: float = 0.0  # 0.0 a 1.0
    
    @property
    def category(self) -> SignalCategory:
        return SignalCategory.STRUCTURAL