# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_intelligence_layer.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import re

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..signals.types.epistemic import (
    AnswerDeterminacySignal,
    DeterminacyLevel,
    MethodApplicationSignal,
    MethodStatus
)


@dataclass
class SignalIntelligenceLayerVehicle(BaseVehicle):
    """
    Vehículo: signal_intelligence_layer
    
    Responsabilidad: Aplicar análisis de inteligencia/ML a datos y señales
    para determinar determinación, ambigüedad, y aplicar métodos de evaluación.
    
    Archivos que procesa:
    - _registry/entities/* (análisis de entidades)
    - responses/answers con contenido textual
    - Datos que requieren clasificación o análisis lingüístico
    """
    
    vehicle_id: str = field(default="signal_intelligence_layer")
    vehicle_name: str = field(default="Signal Intelligence Layer Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=True,
        can_transform=True,
        can_enrich=True,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=[
            "AnswerDeterminacySignal",
            "MethodApplicationSignal"
        ]
    ))
    
    # Marcadores lingüísticos
    affirmative_markers: List[str] = field(default_factory=lambda: [
        'sí', 'existe', 'se realiza', 'se implementa', 'se ejecuta',
        'hay', 'cuenta con', 'dispone de', 'efectivamente', 'ciertamente'
    ])
    
    negation_markers: List[str] = field(default_factory=lambda: [
        'no', 'nunca', 'ninguno', 'ninguna', 'jamás', 'nada',
        'no existe', 'no se realiza', 'no hay', 'no cuenta'
    ])
    
    ambiguity_markers: List[str] = field(default_factory=lambda: [
        'algunos casos', 'a veces', 'parcialmente', 'en ocasiones',
        'eventualmente', 'posiblemente', 'probablemente', 'puede ser',
        'algunos', 'ciertos', 'determinados', 'en parte'
    ])
    
    conditional_markers: List[str] = field(default_factory=lambda: [
        'si', 'cuando', 'dependiendo', 'según', 'en caso de',
        'siempre que', 'salvo que', 'excepto', 'bajo ciertas condiciones'
    ])
    
    # Métodos de evaluación disponibles
    available_methods: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "MC01_binary_classification": {
            "description": "Clasificación binaria SI/NO",
            "version": "1.0.0",
            "applicable_to": ["yes_no_questions"]
        },
        "MC05_financial_chains": {
            "description": "Extracción de cadenas financieras",
            "version": "1.0.0",
            "applicable_to": ["financial_questions"]
        },
        "MC10_entity_extraction": {
            "description": "Extracción de entidades",
            "version": "1.0.0",
            "applicable_to": ["entity_questions"]
        },
        "MC15_sentiment_analysis": {
            "description": "Análisis de sentimiento",
            "version": "1.0.0",
            "applicable_to": ["qualitative_questions"]
        }
    })

    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """
        Procesa datos aplicando análisis de inteligencia.
        """
        signals = []
        
        # Crear evento de procesamiento
        event = self.create_event(
            event_type="signal_generated",
            payload={"analysis_type": "intelligence", "context": context.node_type},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # Extraer texto
        text_content = self._extract_text_content(data)
        
        if text_content:
            # 1. Señal de determinación
            determinacy_signal = self._generate_determinacy_signal(
                text_content, data, context, source
            )
            signals.append(determinacy_signal)
            
            # 2. Señal de aplicación de método
            method_signal = self._generate_method_application_signal(
                text_content, data, context, source
            )
            signals.append(method_signal)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _extract_text_content(self, data: Dict[str, Any]) -> str:
        """Extrae contenido textual"""
        text_parts = []
        
        text_fields = ['answer', 'response', 'description', 'content', 'text']
        
        def extract_recursive(obj, depth=0):
            if depth > 3:
                return
            if isinstance(obj, str):
                text_parts.append(obj)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in text_fields:
                        if isinstance(value, str):
                            text_parts.append(value)
                    else:
                        extract_recursive(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj[:5]:
                    extract_recursive(item, depth + 1)
        
        extract_recursive(data)
        return " ".join(text_parts)
    
    def _generate_determinacy_signal(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> AnswerDeterminacySignal:
        """Genera señal de determinación lingüística"""
        
        text_lower = text.lower()
        
        # Detectar marcadores
        affirmatives = [m for m in self.affirmative_markers if m in text_lower]
        negations = [m for m in self.negation_markers if m in text_lower]
        ambiguities = [m for m in self.ambiguity_markers if m in text_lower]
        conditionals = [m for m in self.conditional_markers if m in text_lower]
        
        # Determinar nivel de determinación
        has_clear_answer = len(affirmatives) > 0 or len(negations) > 0
        has_ambiguity = len(ambiguities) > 0
        has_conditions = len(conditionals) > 0
        has_contradiction = len(affirmatives) > 0 and len(negations) > 0
        
        if has_contradiction:
            determinacy_level = DeterminacyLevel.INDETERMINATE
            confidence = SignalConfidence.HIGH
        elif has_clear_answer and not has_ambiguity and not has_conditions:
            determinacy_level = DeterminacyLevel.HIGH
            confidence = SignalConfidence.HIGH
        elif has_clear_answer and (has_ambiguity or has_conditions):
            determinacy_level = DeterminacyLevel.MEDIUM
            confidence = SignalConfidence.MEDIUM
        elif has_ambiguity or has_conditions:
            determinacy_level = DeterminacyLevel.LOW
            confidence = SignalConfidence.MEDIUM
        else:
            determinacy_level = DeterminacyLevel.INDETERMINATE
            confidence = SignalConfidence.LOW
        
        return AnswerDeterminacySignal(
            context=context,
            source=source,
            question_id=context.node_id,
            determinacy_level=determinacy_level,
            affirmative_markers=affirmatives,
            ambiguity_markers=ambiguities,
            negation_markers=negations,
            conditional_markers=conditionals,
            confidence=confidence,
            rationale=f"Determinacy analysis: {len(affirmatives)} affirmative, "
                     f"{len(ambiguities)} ambiguous, {len(negations)} negative markers"
        )
    
    def _generate_method_application_signal(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> MethodApplicationSignal:
        """Genera señal de aplicación de método"""
        
        # Determinar método aplicable
        method_id, method_info = self._select_applicable_method(data, context)
        
        # Aplicar método
        result, status, extracted_values, processing_time = self._apply_method(
            method_id, text, data
        )
        
        # Determinar errores si los hay
        error_messages = []
        if status != MethodStatus.SUCCESS:
            error_messages.append(f"Method {method_id} execution incomplete")
        
        # Métricas de performance
        performance_metrics = {
            "text_length": len(text),
            "processing_time_ms": processing_time,
            "throughput": len(text) / max(processing_time, 1) if processing_time > 0 else 0
        }
        
        return MethodApplicationSignal(
            context=context,
            source=source,
            question_id=context.node_id,
            method_id=method_id,
            method_version=method_info.get("version", "1.0.0"),
            method_result=result,
            extraction_successful=status == MethodStatus.SUCCESS,
            extracted_values=extracted_values,
            processing_time_ms=processing_time,
            method_status=status,
            error_messages=error_messages,
            performance_metrics=performance_metrics,
            confidence=SignalConfidence.HIGH if status == MethodStatus.SUCCESS else SignalConfidence.MEDIUM,
            rationale=f"Applied method {method_id}: {status.value}"
        )
    
    def _select_applicable_method(
        self,
        data: Dict[str, Any],
        context: SignalContext
    ) -> Tuple[str, Dict[str, Any]]:
        """Selecciona método aplicable según contexto"""
        
        # Heurísticas simples para selección
        data_str = str(data).lower()
        
        if any(word in data_str for word in ['presupuesto', 'recursos', 'fondos', 'financiero']):
            return "MC05_financial_chains", self.available_methods["MC05_financial_chains"]
        
        if any(word in data_str for word in ['institución', 'entidad', 'ministerio', 'agencia']):
            return "MC10_entity_extraction", self.available_methods["MC10_entity_extraction"]
        
        if any(word in data_str for word in ['opinión', 'percepción', 'satisfacción']):
            return "MC15_sentiment_analysis", self.available_methods["MC15_sentiment_analysis"]
        
        # Por defecto, clasificación binaria
        return "MC01_binary_classification", self.available_methods["MC01_binary_classification"]
    
    def _apply_method(
        self,
        method_id: str,
        text: str,
        data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], MethodStatus, List[Any], float]:
        """
        Aplica el método seleccionado.
        Retorna: (resultado, status, valores_extraídos, tiempo_ms)
        """
        
        # Simular tiempo de procesamiento
        processing_time = len(text) * 0.01  # ~10ms por cada 1000 caracteres
        
        try:
            if method_id == "MC01_binary_classification":
                result, extracted = self._apply_binary_classification(text)
                status = MethodStatus.SUCCESS
            
            elif method_id == "MC05_financial_chains":
                result, extracted = self._apply_financial_extraction(text)
                status = MethodStatus.SUCCESS if extracted else MethodStatus.PARTIAL_SUCCESS
            
            elif method_id == "MC10_entity_extraction":
                result, extracted = self._apply_entity_extraction(text)
                status = MethodStatus.SUCCESS if extracted else MethodStatus.PARTIAL_SUCCESS
            
            elif method_id == "MC15_sentiment_analysis":
                result, extracted = self._apply_sentiment_analysis(text)
                status = MethodStatus.SUCCESS
            
            else:
                result = {"error": "Unknown method"}
                extracted = []
                status = MethodStatus.NOT_APPLICABLE
            
            return result, status, extracted, processing_time
            
        except Exception as e:
            return {"error": str(e)}, MethodStatus.FAILURE, [], processing_time
    
    def _apply_binary_classification(self, text: str) -> Tuple[Dict[str, Any], List[Any]]:
        """Clasificación binaria SI/NO"""
        text_lower = text.lower()
        
        yes_score = sum(1 for m in self.affirmative_markers if m in text_lower)
        no_score = sum(1 for m in self.negation_markers if m in text_lower)
        
        classification = "YES" if yes_score > no_score else "NO" if no_score > 0 else "INDETERMINATE"
        confidence = max(yes_score, no_score) / (yes_score + no_score + 1)
        
        result = {
            "classification": classification,
            "confidence": confidence,
            "yes_score": yes_score,
            "no_score": no_score
        }
        
        return result, [classification]
    
    def _apply_financial_extraction(self, text: str) -> Tuple[Dict[str, Any], List[Any]]:
        """Extracción de información financiera"""
        # Patrones simples de montos
        amount_pattern = r'\$\s*[\d,]+(?:\.\d{2})?|\d+\s*(?:millones?|mil\s+millones?)'
        amounts = re.findall(amount_pattern, text, re.IGNORECASE)
        
        result = {
            "amounts_found": len(amounts),
            "sample_amounts": amounts[:5]
        }
        
        return result, amounts
    
    def _apply_entity_extraction(self, text: str) -> Tuple[Dict[str, Any], List[Any]]:
        """Extracción de entidades"""
        # Patrones simples de entidades
        entity_pattern = r'(?:Ministerio|Secretaría|Instituto|Agencia|Entidad|Fondo|Comisión)\s+(?:de\s+)?[\w\s]{1,40}'
        entities = re.findall(entity_pattern, text, re.IGNORECASE)
        
        entities = list(set([e.strip() for e in entities if len(e.split()) <= 6]))
        
        result = {
            "entities_found": len(entities),
            "entities": entities[:10]
        }
        
        return result, entities
    
    def _apply_sentiment_analysis(self, text: str) -> Tuple[Dict[str, Any], List[Any]]:
        """Análisis de sentimiento básico"""
        positive_words = ['bueno', 'excelente', 'efectivo', 'satisfactorio', 'positivo', 'éxito']
        negative_words = ['malo', 'deficiente', 'inefectivo', 'insatisfactorio', 'negativo', 'problema']
        
        text_lower = text.lower()
        positive_count = sum(1 for w in positive_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)
        
        if positive_count > negative_count:
            sentiment = "POSITIVE"
        elif negative_count > positive_count:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
        
        result = {
            "sentiment": sentiment,
            "positive_score": positive_count,
            "negative_score": negative_count
        }
        
        return result, [sentiment]
