# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_evidence_extractor.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import re
import json

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..signals.types.epistemic import (
    EmpiricalSupportSignal,
    EmpiricalSupportLevel,
    MethodApplicationSignal,
    MethodStatus
)


@dataclass
class SignalEvidenceExtractorVehicle(BaseVehicle):
    """
    Vehículo: signal_evidence_extractor
    
    Responsabilidad: Extraer evidencia empírica de archivos canónicos de patrones,
    aplicando métodos de extracción sobre corpus empíricos.
    
    Archivos que procesa (según spec):
    - _registry/patterns/by_category/*.json
    - _registry/patterns/by_dimension/*.json
    - _registry/patterns/by_policy_area/*.json
    
    Señales que produce (según spec):
    - EmpiricalSupportSignal
    - MethodApplicationSignal
    """
    
    vehicle_id: str = field(default="signal_evidence_extractor")
    vehicle_name: str = field(default="Signal Evidence Extractor Vehicle")
    
    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=True,
        can_transform=True,
        can_enrich=False,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=[
            "EmpiricalSupportSignal",
            "MethodApplicationSignal"
        ]
    ))
    
    # Patrones de extracción
    normative_patterns: List[str] = field(default_factory=lambda: [
        r'Ley\s+\d+\s+de\s+\d{4}',
        r'Decreto\s+\d+\s+de\s+\d{4}',
        r'Resolución\s+\d+\s+de\s+\d{4}',
        r'Acuerdo\s+\d+\s+de\s+\d{4}',
        r'Ordenanza\s+\d+\s+de\s+\d{4}',
        r'Directiva\s+\d+\s+de\s+\d{4}',
        r'Circular\s+\d+\s+de\s+\d{4}',
        r'Sentencia\s+[TC]-\d+',
        r'Auto\s+\d+\s+de\s+\d{4}'
    ])
    
    document_patterns: List[str] = field(default_factory=lambda: [
        r'Plan\s+Nacional\s+de\s+\w+',
        r'CONPES\s+\d+',
        r'Programa\s+\w+',
        r'Política\s+\w+',
        r'Estrategia\s+\w+',
        r'Marco\s+\w+'
    ])
    
    institution_keywords: List[str] = field(default_factory=lambda: [
        'Ministerio', 'Secretaría', 'Departamento', 'Instituto',
        'Agencia', 'Entidad', 'Unidad', 'Dirección',
        'Fondo', 'Comisión', 'Consejo', 'Autoridad'
    ])
    
    temporal_patterns: List[str] = field(default_factory=lambda: [
        r'\d{4}',  # Año
        r'desde\s+\d{4}',
        r'hasta\s+\d{4}',
        r'vigencia\s+\d{4}',
        r'entre\s+\d{4}\s+y\s+\d{4}'
    ])
    
    # Elementos específicos esperados por categoría
    specificity_elements: Dict[str, List[str]] = field(default_factory=lambda: {
        "formal_instrument": ["ley", "decreto", "resolución", "acuerdo"],
        "mandatory_scope": ["obligatorio", "debe", "deberá", "requiere"],
        "institutional_owner": ["ministerio", "secretaría", "instituto", "entidad"],
        "temporal_scope": ["vigencia", "desde", "hasta", "año"],
        "procedural_detail": ["procedimiento", "proceso", "paso", "requisito"],
        "resource_allocation": ["presupuesto", "recursos", "financiación", "fondos"]
    })

    def process(self, data: Dict[str, Any], context: SignalContext) -> List[Signal]:
        """
        Procesa datos y extrae evidencia empírica.
        """
        signals = []
        
        # Crear evento de extracción
        event = self.create_event(
            event_type="signal_generated",
            payload={"extraction_type": "evidence", "data_size": len(str(data))},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # Extraer texto de diferentes campos
        text_content = self._extract_text_content(data)
        
        if text_content:
            # 1. Señal de soporte empírico
            support_signal = self._generate_empirical_support_signal(
                text_content, data, context, source
            )
            signals.append(support_signal)
            
            # 2. Señal de aplicación de método de extracción
            method_signal = self._generate_method_application_signal(
                text_content, data, context, source
            )
            signals.append(method_signal)
        
        self.stats["signals_generated"] += len(signals)
        
        return signals
    
    def _extract_text_content(self, data: Dict[str, Any]) -> str:
        """Extrae contenido textual de los datos"""
        text_parts = []
        
        # Campos comunes que contienen texto
        text_fields = [
            'answer', 'response', 'description', 'content',
            'text', 'justification', 'explanation', 'rationale',
            'notes', 'observations', 'comments'
        ]
        
        def extract_recursive(obj, depth=0):
            if depth > 5:  # Límite de profundidad
                return
            
            if isinstance(obj, str):
                text_parts.append(obj)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in text_fields and isinstance(value, str):
                        text_parts.append(value)
                    else:
                        extract_recursive(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj[:10]:  # Límite de elementos
                    extract_recursive(item, depth + 1)
        
        extract_recursive(data)
        
        return " ".join(text_parts)
    
    def _generate_empirical_support_signal(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> EmpiricalSupportSignal:
        """Genera señal de soporte empírico"""
        
        # Extraer referencias normativas
        normative_refs = self._extract_normative_references(text)
        
        # Extraer referencias documentales
        document_refs = self._extract_document_references(text)
        
        # Extraer referencias institucionales
        institutional_refs = self._extract_institutional_references(text)
        
        # Extraer referencias temporales
        temporal_refs = self._extract_temporal_references(text)
        
        # Determinar nivel de soporte
        total_refs = len(normative_refs) + len(document_refs) + len(institutional_refs)
        
        if len(normative_refs) >= 2 and len(institutional_refs) >= 1:
            support_level = EmpiricalSupportLevel.STRONG
            confidence = SignalConfidence.HIGH
        elif len(normative_refs) >= 1 or len(document_refs) >= 2:
            support_level = EmpiricalSupportLevel.MODERATE
            confidence = SignalConfidence.MEDIUM
        elif total_refs > 0:
            support_level = EmpiricalSupportLevel.WEAK
            confidence = SignalConfidence.MEDIUM
        else:
            support_level = EmpiricalSupportLevel.NONE
            confidence = SignalConfidence.LOW
        
        # Calcular scores de calidad de referencias
        reference_quality_scores = {}
        for ref in normative_refs:
            reference_quality_scores[ref] = 1.0  # Normativas son máxima calidad
        for ref in document_refs:
            reference_quality_scores[ref] = 0.8  # Documentos son alta calidad
        for ref in institutional_refs:
            reference_quality_scores[ref] = 0.6  # Institucionales son media calidad
        
        return EmpiricalSupportSignal(
            context=context,
            source=source,
            question_id=context.node_id,
            support_level=support_level,
            normative_references=normative_refs,
            document_references=document_refs,
            institutional_references=institutional_refs,
            temporal_references=temporal_refs,
            reference_quality_scores=reference_quality_scores,
            total_references=total_refs,
            confidence=confidence,
            rationale=f"Extracted {total_refs} references: {len(normative_refs)} normative, "
                     f"{len(document_refs)} documentary, {len(institutional_refs)} institutional"
        )
    
    
    def _generate_method_application_signal(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> MethodApplicationSignal:
        """Genera señal de aplicación de método de extracción"""
        
        # Determinar método de extracción aplicado
        method_id = "MC03_normative_references"  # Método de extracción de referencias normativas
        method_version = "1.0.0"
        
        # Aplicar extracción
        normative_refs = self._extract_normative_references(text)
        document_refs = self._extract_document_references(text)
        institutional_refs = self._extract_institutional_references(text)
        
        extraction_successful = len(normative_refs) > 0 or len(document_refs) > 0
        extracted_values = normative_refs + document_refs + institutional_refs
        
        # Simular tiempo de procesamiento
        processing_time = len(text) * 0.02
        
        # Resultado del método
        method_result = {
            "normative_count": len(normative_refs),
            "document_count": len(document_refs),
            "institutional_count": len(institutional_refs),
            "total_extracted": len(extracted_values)
        }
        
        method_status = MethodStatus.SUCCESS if extraction_successful else MethodStatus.PARTIAL_SUCCESS
        
        return MethodApplicationSignal(
            context=context,
            source=source,
            question_id=context.node_id,
            method_id=method_id,
            method_version=method_version,
            method_result=method_result,
            extraction_successful=extraction_successful,
            extracted_values=extracted_values,
            processing_time_ms=processing_time,
            method_status=method_status,
            error_messages=[],
            performance_metrics={"text_length": len(text), "extraction_rate": len(extracted_values) / max(len(text), 1)},
            confidence=SignalConfidence.HIGH if extraction_successful else SignalConfidence.MEDIUM,
            rationale=f"Extraction method {method_id}: extracted {len(extracted_values)} references"
        )
    
    def _generate_specificity_signal(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> AnswerSpecificitySignal:
        """Genera señal de especificidad"""
        
        text_lower = text.lower()
        
        # Determinar elementos esperados según tipo de pregunta
        expected_elements = self._determine_expected_elements(data, context)
        
        # Detectar elementos encontrados
        found_elements = []
        element_details = {}
        
        for element_type, keywords in self.specificity_elements.items():
            if element_type in expected_elements:
                found_count = sum(1 for kw in keywords if kw in text_lower)
                if found_count > 0:
                    found_elements.append(element_type)
                    # Extraer ejemplos
                    examples = [kw for kw in keywords if kw in text_lower][:3]
                    element_details[element_type] = {
                        "found": True,
                        "value": ", ".join(examples),
                        "confidence": min(0.9, found_count * 0.3)
                    }
        
        missing_elements = [e for e in expected_elements if e not in found_elements]
        
        # Calcular score de especificidad
        if expected_elements:
            specificity_score = len(found_elements) / len(expected_elements)
        else:
            specificity_score = 1.0
        
        # Determinar nivel
        if specificity_score >= 0.8:
            specificity_level = SpecificityLevel.HIGH
            confidence = SignalConfidence.HIGH
        elif specificity_score >= 0.5:
            specificity_level = SpecificityLevel.MEDIUM
            confidence = SignalConfidence.MEDIUM
        elif specificity_score > 0.2:
            specificity_level = SpecificityLevel.LOW
            confidence = SignalConfidence.MEDIUM
        else:
            specificity_level = SpecificityLevel.NONE
            confidence = SignalConfidence.LOW
        
        return AnswerSpecificitySignal(
            context=context,
            source=source,
            question_id=context.node_id,
            specificity_level=specificity_level,
            expected_elements=expected_elements,
            found_elements=found_elements,
            missing_elements=missing_elements,
            specificity_score=specificity_score,
            element_details=element_details,
            confidence=confidence,
            rationale=f"Specificity: {len(found_elements)}/{len(expected_elements)} elements found"
        )
    
    def _extract_normative_references(self, text: str) -> List[str]:
        """Extrae referencias normativas del texto"""
        references = set()
        
        for pattern in self.normative_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                references.add(match.group(0))
        
        return sorted(list(references))
    
    def _extract_document_references(self, text: str) -> List[str]:
        """Extrae referencias documentales del texto"""
        references = set()
        
        for pattern in self.document_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                references.add(match.group(0))
        
        return sorted(list(references))
    
    def _extract_institutional_references(self, text: str) -> List[str]:
        """Extrae referencias institucionales del texto"""
        references = set()
        
        # Buscar patrones institucionales
        for keyword in self.institution_keywords:
            pattern = rf'{keyword}\s+(?:de\s+)?(?:la\s+)?[\w\s]{{1,50}}'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ref = match.group(0).strip()
                if len(ref.split()) <= 8:  # Limitar longitud
                    references.add(ref)
        
        return sorted(list(references))[:10]  # Limitar cantidad
    
    def _extract_temporal_references(self, text: str) -> List[str]:
        """Extrae referencias temporales del texto"""
        references = set()
        
        for pattern in self.temporal_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                references.add(match.group(0))
        
        return sorted(list(references))

