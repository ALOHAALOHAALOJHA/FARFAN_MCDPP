# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_registry.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import os

from .base_vehicle import BaseVehicle, VehicleCapabilities
from .. core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..signal_types.types.structural import (
    StructuralAlignmentSignal, 
    AlignmentStatus,
    CanonicalMappingSignal
)
from ..signal_types.types.integrity import (
    EventPresenceSignal,
    PresenceStatus,
    EventCompletenessSignal,
    CompletenessLevel
)


@dataclass
class SignalRegistryVehicle(BaseVehicle):
    """
    Vehículo:  signal_registry
    
    Responsabilidad: Cargar archivos canónicos y generar señales
    de alineación estructural e integridad. 
    
    Archivos que procesa (del canonic central):
    - clusters/*/metadata.json, questions. json, aggregation_rules.json
    - dimensions/*/metadata.json, questions.json, pdet_context.json
    - policy_areas/*/metadata.json, questions. json, keywords.json
    - cross_cutting/*. json
    - scoring/*. json
    - governance/*.json
    """
    
    vehicle_id: str = field(default="signal_registry")
    vehicle_name: str = field(default="Signal Registry Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=True,
        can_scope=False,
        can_extract=False,
        can_transform=True,
        can_enrich=False,
        can_validate=True,
        can_irrigate=False,
        signal_types_produced=[
            "StructuralAlignmentSignal",
            "CanonicalMappingSignal",
            "EventPresenceSignal",
            "EventCompletenessSignal"
        ]
    ))
    
    # Esquemas esperados por tipo de archivo
    expected_schemas: Dict[str, List[str]] = field(default_factory=lambda: {
        "metadata.json": ["id", "name", "description", "version"],
        "questions.json": ["questions"],
        "aggregation_rules. json": ["rules", "weights"],
        "keywords.json": ["keywords"],
        "pdet_context.json": ["context", "municipalities"],
        "detection_rules.json": ["rules", "patterns"],
        "scoring_system.json": ["dimensions", "weights", "thresholds"],
        "governance. json": ["policies", "actors", "mechanisms"]
    })
    
    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """
        Procesa un archivo canónico y genera señales.
        """
        signals = []
        
        # Crear evento de carga
        event = self.create_event(
            event_type="canonical_data_loaded",
            payload={"keys": list(data.keys()), "size": len(json.dumps(data))},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # 1. Señal de alineación estructural
        alignment_signal = self._generate_alignment_signal(data, context, source)
        signals.append(alignment_signal)
        
        # 2. Señal de presencia de evento
        presence_signal = self._generate_presence_signal(data, context, source)
        signals.append(presence_signal)
        
        # 3. Señal de completitud
        completeness_signal = self._generate_completeness_signal(data, context, source)
        signals.append(completeness_signal)
        
        # 4. Señal de mapeo canónico (si aplica)
        if self._should_generate_mapping_signal(context):
            mapping_signal = self._generate_mapping_signal(data, context, source)
            signals.append(mapping_signal)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _generate_alignment_signal(
        self, 
        data: Dict[str, Any], 
        context: SignalContext,
        source: SignalSource
    ) -> StructuralAlignmentSignal:
        """Genera señal de alineación estructural"""
        
        # Determinar esquema esperado
        file_type = context.node_id.split("/")[-1] if "/" in context.node_id else context.node_id
        expected_fields = self.expected_schemas.get(file_type, [])
        
        actual_fields = list(data.keys())
        missing = [f for f in expected_fields if f not in actual_fields]
        extra = [f for f in actual_fields if f not in expected_fields and expected_fields]
        
        # Determinar estado
        if not missing and not extra:
            status = AlignmentStatus.ALIGNED
            confidence = SignalConfidence.HIGH
        elif not missing: 
            status = AlignmentStatus.ALIGNED
            confidence = SignalConfidence.MEDIUM
        elif len(missing) < len(expected_fields) / 2:
            status = AlignmentStatus.PARTIAL
            confidence = SignalConfidence. MEDIUM
        else:
            status = AlignmentStatus.MISALIGNED
            confidence = SignalConfidence.HIGH
        
        return StructuralAlignmentSignal(
            context=context,
            source=source,
            alignment_status=status,
            canonical_path=f"{context.node_type}/{context.node_id}",
            actual_path=source.source_path,
            missing_elements=missing,
            extra_elements=extra,
            confidence=confidence,
            rationale=f"Alignment check:  {len(missing)} missing, {len(extra)} extra fields"
        )
    
    def _generate_presence_signal(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> EventPresenceSignal:
        """Genera señal de presencia"""
        
        has_content = bool(data) and any(
            v is not None and v != [] and v != {} 
            for v in data.values()
        )
        
        return EventPresenceSignal(
            context=context,
            source=source,
            expected_event_type="canonical_data_loaded",
            presence_status=PresenceStatus. PRESENT if has_content else PresenceStatus.PARTIAL,
            event_count=1,
            confidence=SignalConfidence.HIGH,
            rationale=f"Data {'present' if has_content else 'empty or partial'}"
        )
    
    def _generate_completeness_signal(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> EventCompletenessSignal:
        """Genera señal de completitud"""
        
        file_type = context.node_id.split("/")[-1] if "/" in context.node_id else context.node_id
        required = self.expected_schemas.get(file_type, [])
        present = [f for f in required if f in data and data[f]]
        
        if not required: 
            level = CompletenessLevel. COMPLETE
            score = 1.0
        elif len(present) == len(required):
            level = CompletenessLevel.COMPLETE
            score = 1.0
        elif len(present) >= len(required) * 0.75:
            level = CompletenessLevel.MOSTLY_COMPLETE
            score = len(present) / len(required)
        elif len(present) > 0:
            level = CompletenessLevel.INCOMPLETE
            score = len(present) / len(required)
        else:
            level = CompletenessLevel.EMPTY
            score = 0.0
        
        return EventCompletenessSignal(
            context=context,
            source=source,
            completeness_level=level,
            required_fields=required,
            present_fields=present,
            completeness_score=score,
            confidence=SignalConfidence.HIGH,
            rationale=f"Completeness:  {len(present)}/{len(required)} required fields present"
        )
    
    def _should_generate_mapping_signal(self, context: SignalContext) -> bool:
        """Determina si debe generar señal de mapeo"""
        return context.node_type in ["question", "policy_area", "dimension", "cluster"]
    
    def _generate_mapping_signal(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> CanonicalMappingSignal: 
        """Genera señal de mapeo canónico"""
        
        mapped = {}
        unmapped = []
        
        # Intentar extraer mapeos del contenido
        if "policy_area" in data:
            mapped["policy_area"] = data["policy_area"]
        elif "PA" in context.node_id:
            mapped["policy_area"] = context.node_id
        else:
            unmapped.append("policy_area")
        
        if "dimension" in data: 
            mapped["dimension"] = data["dimension"]
        elif "DIM" in context.node_id:
            mapped["dimension"] = context.node_id
        else:
            unmapped.append("dimension")
        
        if "cluster" in data:
            mapped["cluster"] = data["cluster"]
        elif "CL" in context.node_id:
            mapped["cluster"] = context.node_id
        
        completeness = len(mapped) / (len(mapped) + len(unmapped)) if (mapped or unmapped) else 1.0
        
        return CanonicalMappingSignal(
            context=context,
            source=source,
            source_item_id=context.node_id,
            mapped_entities=mapped,
            unmapped_aspects=unmapped,
            mapping_completeness=completeness,
            confidence=SignalConfidence. MEDIUM if unmapped else SignalConfidence.HIGH,
            rationale=f"Mapped {len(mapped)} entities, {len(unmapped)} unmapped"
        )


# =============================================================================
# QUESTIONNAIRE SIGNAL REGISTRY
# =============================================================================

class QuestionnaireSignalRegistry:
    """
    Registry for managing signals associated with questionnaire questions.
    Provides access to all signals generated for questions in the pipeline.
    """
    
    def __init__(self, questionnaire_path: Optional[str] = None):
        """Initialize the registry with optional questionnaire path."""
        self.questionnaire_path = questionnaire_path
        self.signals: Dict[str, List[Signal]] = {}
        self._vehicle = SignalRegistryVehicle()
    
    def get_signals_for_question(self, question_id: str) -> List[Signal]:
        """
        Get all signals for a specific question.
        
        Args:
            question_id: Question identifier (e.g., "Q001")
            
        Returns:
            List of signals associated with the question
        """
        return self.signals.get(question_id, [])
    
    def register_signal(self, question_id: str, signal: Signal) -> None:
        """
        Register a signal for a question.
        
        Args:
            question_id: Question identifier
            signal: Signal to register
        """
        if question_id not in self.signals:
            self.signals[question_id] = []
        self.signals[question_id].append(signal)
    
    def get_all_question_ids(self) -> List[str]:
        """Get all question IDs that have registered signals."""
        return list(self.signals.keys())
    
    def signal_count_for_question(self, question_id: str) -> int:
        """Get count of signals for a specific question."""
        return len(self.signals.get(question_id, []))
    
    def total_signal_count(self) -> int:
        """Get total count of all signals across all questions."""
        return sum(len(sigs) for sigs in self.signals.values())