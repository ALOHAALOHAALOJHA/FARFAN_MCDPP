# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_context_scoper.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..signals.types.structural import CanonicalMappingSignal
from ..signals.types.epistemic import (
    AnswerDeterminacySignal,
    DeterminacyLevel,
    AnswerSpecificitySignal,
    SpecificityLevel
)


@dataclass
class SignalContextScoperVehicle(BaseVehicle):
    """
    Vehículo: signal_context_scoper
    
    Responsabilidad: Aplicar contexto y scope a los datos,
    determinando a qué nodos pertenecen y qué señales deben generarse.
    
    Archivos que procesa: 
    - dimensions/*/questions/*. json (preguntas individuales)
    - _registry/questions/*. json
    - _registry/patterns/*.json
    """
    
    vehicle_id:  str = field(default="signal_context_scoper")
    vehicle_name: str = field(default="Signal Context Scoper Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=True,
        can_extract=True,
        can_transform=True,
        can_enrich=False,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=[
            "CanonicalMappingSignal",
            "AnswerDeterminacySignal",
            "AnswerSpecificitySignal"
        ]
    ))
    
    # Marcadores para análisis epistémico
    affirmative_markers: List[str] = field(default_factory=lambda:  [
        "sí", "si", "existe", "cuenta con", "dispone de", "tiene",
        "se realiza", "se implementa", "está vigente", "opera"
    ])
    
    ambiguity_markers: List[str] = field(default_factory=lambda: [
        "algunos", "ciertos", "parcialmente", "a veces", "en ocasiones",
        "dependiendo", "cuando sea posible", "según el caso"
    ])
    
    negation_markers: List[str] = field(default_factory=lambda: [
        "no", "nunca", "ninguno", "ninguna", "sin", "carece",
        "no existe", "no cuenta", "no dispone", "no tiene"
    ])
    
    specificity_elements: List[str] = field(default_factory=lambda: [
        "ley", "decreto", "resolución", "acuerdo", "ordenanza",
        "ministerio", "secretaría", "dirección", "unidad",
        "presupuesto", "recursos", "asignación"
    ])
    
    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """Procesa datos aplicando scope y contexto"""
        signals = []
        
        event = self.create_event(
            event_type="canonical_data_validated",
            payload=data,
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context. phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # Si es una pregunta, aplicar análisis epistémico
        if context.node_type == "question" or "question" in str(data. get("type", "")):
            answer_text = data.get("answer", data.get("response", ""))
            
            if answer_text:
                # Señal de determinismo
                determinacy = self._analyze_determinacy(answer_text, context, source)
                signals. append(determinacy)
                
                # Señal de especificidad
                specificity = self._analyze_specificity(answer_text, data, context, source)
                signals.append(specificity)
        
        # Generar mapeo canónico basado en contexto
        mapping = self._generate_context_mapping(data, context, source)
        signals.append(mapping)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _analyze_determinacy(
        self,
        text: str,
        context: SignalContext,
        source: SignalSource
    ) -> AnswerDeterminacySignal:
        """Analiza determinismo de una respuesta"""
        
        text_lower = text.lower()
        
        found_affirmative = [m for m in self.affirmative_markers if m in text_lower]
        found_ambiguity = [m for m in self.ambiguity_markers if m in text_lower]
        found_negation = [m for m in self.negation_markers if m in text_lower]
        
        # Determinar nivel
        if found_negation and not found_affirmative: 
            level = DeterminacyLevel.HIGH  # Negación clara
            rationale = "Clear negative statement"
        elif found_affirmative and not found_ambiguity and not found_negation:
            level = DeterminacyLevel.HIGH  # Afirmación clara
            rationale = "Clear affirmative statement"
        elif found_affirmative and found_ambiguity: 
            level = DeterminacyLevel.MEDIUM  # Afirmación con ambigüedad
            rationale = "Affirmative with scope ambiguity"
        elif found_ambiguity: 
            level = DeterminacyLevel.LOW
            rationale = "High ambiguity detected"
        else:
            level = DeterminacyLevel.INDETERMINATE
            rationale = "Cannot determine stance"
        
        return AnswerDeterminacySignal(
            context=context,
            source=source,
            question_id=context.node_id,
            determinacy_level=level,
            affirmative_markers=found_affirmative,
            ambiguity_markers=found_ambiguity,
            negation_markers=found_negation,
            confidence=SignalConfidence. MEDIUM,
            rationale=rationale
        )
    
    def _analyze_specificity(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> AnswerSpecificitySignal: 
        """Analiza especificidad de una respuesta"""
        
        text_lower = text.lower()
        
        expected = ["formal_instrument", "institutional_owner", "mandatory_scope", "budget_allocation"]
        found = []
        
        # Buscar elementos de especificidad
        if any(m in text_lower for m in ["ley", "decreto", "resolución", "acuerdo"]):
            found.append("formal_instrument")
        
        if any(m in text_lower for m in ["ministerio", "secretaría", "dirección", "unidad", "entidad"]):
            found.append("institutional_owner")
        
        if any(m in text_lower for m in ["obligatorio", "debe", "deberá", "exige"]):
            found.append("mandatory_scope")
        
        if any(m in text_lower for m in ["presupuesto", "recursos", "millones", "asignación"]):
            found. append("budget_allocation")
        
        missing = [e for e in expected if e not in found]
        
        if len(found) >= 3:
            level = SpecificityLevel.HIGH
        elif len(found) >= 2:
            level = SpecificityLevel.MEDIUM
        elif len(found) >= 1:
            level = SpecificityLevel.LOW
        else:
            level = SpecificityLevel.NONE
        
        score = len(found) / len(expected) if expected else 0.0
        
        return AnswerSpecificitySignal(
            context=context,
            source=source,
            question_id=context.node_id,
            specificity_level=level,
            expected_elements=expected,
            found_elements=found,
            missing_elements=missing,
            specificity_score=score,
            confidence=SignalConfidence. MEDIUM,
            rationale=f"Found {len(found)}/{len(expected)} specificity elements"
        )
    
    def _generate_context_mapping(
        self,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> CanonicalMappingSignal:
        """Genera mapeo basado en contexto inferido"""
        
        mapped = {}
        
        # Inferir de context
        if "PA" in context.node_id:
            pa_match = [p for p in ["PA01", "PA02", "PA03", "PA04", "PA05", 
                                     "PA06", "PA07", "PA08", "PA09", "PA10"]
                       if p in context.node_id]
            if pa_match: 
                mapped["policy_area"] = pa_match[0]
        
        if "DIM" in context.node_id:
            dim_match = [d for d in ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]
                        if d in context. node_id]
            if dim_match:
                mapped["dimension"] = dim_match[0]
        
        if "CL" in context.node_id:
            cl_match = [c for c in ["CL01", "CL02", "CL03", "CL04"]
                       if c in context.node_id]
            if cl_match: 
                mapped["cluster"] = cl_match[0]
        
        # Inferir de data
        if "policy_area" in data:
            mapped["policy_area"] = data["policy_area"]
        if "dimension" in data:
            mapped["dimension"] = data["dimension"]
        
        return CanonicalMappingSignal(
            context=context,
            source=source,
            source_item_id=context. node_id,
            mapped_entities=mapped,
            unmapped_aspects=[],
            mapping_completeness=1.0 if mapped else 0.0,
            confidence=SignalConfidence.HIGH if mapped else SignalConfidence.LOW,
            rationale=f"Context-based mapping: {list(mapped.keys())}"
        )