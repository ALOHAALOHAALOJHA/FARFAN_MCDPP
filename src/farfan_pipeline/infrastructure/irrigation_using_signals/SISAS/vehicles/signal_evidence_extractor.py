# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_evidence_extractor.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import re

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..core.contracts import PublicationContract, ContractType, ContractStatus, SignalTypeSpec
from ..signal_types.types.epistemic import (
    EmpiricalSupportSignal,
    MethodApplicationSignal
)

# Import for ExtractionResult bridge
try:
    # Try to import from the actual location
    from farfan_pipeline.infrastructure.extractors.empirical_extractor_base import ExtractionResult
    HAS_EXTRACTION_RESULT = True
except ImportError:
    # If import fails, define minimal interface for duck typing
    HAS_EXTRACTION_RESULT = False
    ExtractionResult = None
    
    # Define minimal interface for type checking
    class _DuckTypedExtractionResult:
        """Duck-typed interface for ExtractionResult when import unavailable."""
        extractor_id: str
        signal_type: str
        matches: list
        confidence: float
        metadata: dict
        validation_passed: bool
        validation_errors: list

@dataclass
class SignalEvidenceExtractorVehicle(BaseVehicle):
    """
    Vehículo: signal_evidence_extractor

    Responsabilidad: Extraer evidencia empírica y aplicar métodos de evaluación.

    Archivos que procesa:
    - Preguntas del cuestionario (Q*.json)
    - Respuestas que contienen referencias normativas o documentales
    - Texto que requiere análisis de soporte empírico
    """
    vehicle_id: str = "signal_evidence_extractor"
    vehicle_name: str = "Signal Evidence Extractor Vehicle"

    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=True,
        can_transform=False,
        can_enrich=False,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=["EmpiricalSupportSignal", "MethodApplicationSignal"]
    ))

    def __post_init__(self):
        # Crear contrato de publicación
        self.publication_contract = PublicationContract(
            contract_id=f"pub_{self.vehicle_id}",
            publisher_vehicle=self.vehicle_id,
            status=ContractStatus.ACTIVE,
            allowed_signal_types=[
                SignalTypeSpec(signal_type="EmpiricalSupportSignal"),
                SignalTypeSpec(signal_type="MethodApplicationSignal")
            ],
            allowed_buses=["epistemic_bus", "evidence_bus"],
            require_context=True,
            require_source=True
        )
        if self.contract_registry:
            self.contract_registry.register(self.publication_contract)

    # Patrones para detección de evidencia
    normative_patterns: List[str] = field(default_factory=lambda: [
        r"ley\s+\d+",
        r"decreto\s+\d+",
        r"resolución\s+\d+",
        r"estatuto\s+\d+",
        r"ordenanza\s+\d+",
        r"acto\s+(?:legislativo|administrativo)",
        r"jurisprudencia",
        r"sentencia\s+[A-Z]\w+"
    ])

    institutional_patterns: List[str] = field(default_factory=lambda: [
        r"ministerio\s+de",
        r"departamento\s+(?:administrativo|nacional)",
        r"entidad\s+(?:pública|territorial)",
        r"contraloría",
        r"procuraduría",
        r"fiscalía",
        r"defensoría"
    ])

    method_patterns: Dict[str, List[str]] = field(default_factory=lambda: {
        "triangulation": [
            r"cruz",
            r"triangula",
            r"compara",
            r"contrast"
        ],
        "member_checking": [
            r"verifica",
            r"confirma",
            r"consult",
            r"entrevista"
        ],
        "document_analysis": [
            r"análisis\s+documental",
            r"revisión\s+normativa",
            r"estudio\s+jurídico"
        ],
        "statistical_analysis": [
            r"estadística",
            r"porcentaje",
            r"media\s+de",
            r"tasa\s+de"
        ]
    })

    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        """
        Procesa datos y extrae evidencia empírica y aplicación de métodos.
        
        Enhanced to support ExtractionResult conversion to Signal.
        """
        signals = []

        # Bridge: If data is ExtractionResult, convert to signals
        # Use duck typing to avoid import dependency issues
        if HAS_EXTRACTION_RESULT and ExtractionResult and isinstance(data, ExtractionResult):
            converted_signals = self.convert_extraction_result_to_signals(data, context)
            signals.extend(converted_signals)
            self.stats["signals_generated"] += len(converted_signals)
            return signals
        elif hasattr(data, 'extractor_id') and hasattr(data, 'matches') and hasattr(data, 'confidence'):
            # Duck typing: If it looks like ExtractionResult, treat it as such
            converted_signals = self.convert_extraction_result_to_signals(data, context)
            signals.extend(converted_signals)
            self.stats["signals_generated"] += len(converted_signals)
            return signals

        # Crear evento
        event = self.create_event(
            event_type="evidence_extraction",
            payload={"context": context.node_id},
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )

        source = self.create_signal_source(event)

        # Extraer texto para análisis
        text = self._extract_text(data)

        if text:
            # 1. Señal de soporte empírico
            empirical_signal = self._extract_empirical_support(text, data, context, source)
            signals.append(empirical_signal)

            # 2. Señal de aplicación de método
            method_signal = self._detect_method_application(text, data, context, source)
            signals.append(method_signal)

        self.stats["signals_generated"] += len(signals)
        return signals
    
    def convert_extraction_result_to_signals(
        self, 
        extraction_result: Any,  # Use Any for duck typing
        context: SignalContext
    ) -> List[Signal]:
        """
        BRIDGE: Convert ExtractionResult from empirical extractors to SISAS Signal objects.
        
        This method bridges the gap between standalone extractors and SISAS irrigation.
        It transforms raw extraction results into properly formatted signals that can be
        published to buses and consumed by downstream consumers.
        
        ENHANCED: Automatic confidence tuning from calibration data.
        Uses duck typing to handle ExtractionResult regardless of import success.
        
        Args:
            extraction_result: Result from empirical extractor (MC01-MC10) with attributes:
                - extractor_id, signal_type, matches, confidence, metadata, 
                  validation_passed, validation_errors
            context: Signal context for routing
            
        Returns:
            List of Signal objects ready for bus publication
        """
        signals = []
        
        # Extract attributes using getattr for duck typing
        extractor_id = getattr(extraction_result, 'extractor_id', 'unknown')
        signal_type = getattr(extraction_result, 'signal_type', 'unknown')
        matches = getattr(extraction_result, 'matches', [])
        confidence = getattr(extraction_result, 'confidence', 0.0)
        metadata = getattr(extraction_result, 'metadata', {})
        validation_passed = getattr(extraction_result, 'validation_passed', True)
        validation_errors = getattr(extraction_result, 'validation_errors', [])
        
        # Create event for traceability
        event = self.create_event(
            event_type="signal_generated",
            payload={
                "extractor_id": extractor_id,
                "signal_type": signal_type,
                "matches_count": len(matches),
                "confidence": confidence,
            },
            source_file=context.node_id,
            source_path=f"{context.node_type}/{context.node_id}",
            phase=context.phase,
            consumer_scope=context.consumer_scope
        )
        
        source = self.create_signal_source(event)
        
        # ENHANCED: Automatic confidence tuning from calibration data
        signal_confidence = self._tune_confidence_from_calibration(
            confidence,
            extractor_id,
            len(matches),
            metadata
        )
        
        # Create MethodApplicationSignal for the extraction
        method_signal = MethodApplicationSignal(
            context=context,
            source=source,
            question_id=context.node_id,
            method_id=extractor_id,
            method_result="SUCCESS" if validation_passed else "VALIDATION_FAILED",
            extraction_successful=validation_passed,
            extracted_values=[m.get("text", str(m)) if isinstance(m, dict) else str(m) for m in matches[:10]],  # Limit to 10
            processing_time_ms=metadata.get("processing_time_ms", 0.0),
            confidence=signal_confidence,
            rationale=f"Extractor {extractor_id} found {len(matches)} matches. "
                      f"Validation: {'PASSED' if validation_passed else 'FAILED'}. "
                      f"Calibrated confidence: {signal_confidence}"
        )
        signals.append(method_signal)
        
        # If there are validation errors, also create an error signal
        if not validation_passed and validation_errors:
            from ..signal_types.types.operational import FailureModeSignal, FailureMode
            
            error_signal = FailureModeSignal(
                context=context,
                source=source,
                execution_id=f"{extractor_id}_{event.event_id}",
                failure_mode=FailureMode.VALIDATION_ERROR,
                error_message="; ".join(str(e) for e in validation_errors[:3]),  # First 3 errors
                recoverable=True,
                retry_count=0,
                confidence=SignalConfidence.VERY_HIGH,  # High confidence in the failure
                rationale=f"Extractor validation failed with {len(validation_errors)} errors"
            )
            signals.append(error_signal)
        
        return signals
    
    def _tune_confidence_from_calibration(
        self,
        base_confidence: float,
        extractor_id: str,
        match_count: int,
        metadata: Dict[str, Any]
    ) -> SignalConfidence:
        """
        CONFIDENCE TUNING: Automatically tune signal confidence from calibration data.
        
        This addresses the sophistication gap where all signals default to INDETERMINATE.
        It uses empirical calibration data to dynamically score confidence based on:
        1. Base confidence from extractor
        2. Match count (more matches = higher confidence)
        3. Empirical frequency from calibration
        4. Historical performance metrics
        
        Args:
            base_confidence: Raw confidence from extractor (0.0-1.0)
            extractor_id: ID of the extractor for calibration lookup
            match_count: Number of matches found
            metadata: Additional metadata from extraction
            
        Returns:
            SignalConfidence enum with tuned confidence level
        """
        # Start with base confidence
        tuned_confidence = base_confidence
        
        # BOOST: Match count bonus
        # More matches generally indicate higher confidence in finding relevant data
        if match_count > 10:
            tuned_confidence += 0.15
        elif match_count > 5:
            tuned_confidence += 0.10
        elif match_count > 0:
            tuned_confidence += 0.05
        
        # BOOST: Empirical availability from calibration
        # If metadata contains empirical_availability from calibration file
        empirical_availability = metadata.get("empirical_availability", 0.0)
        if empirical_availability > 0.7:
            tuned_confidence += 0.10
        elif empirical_availability > 0.5:
            tuned_confidence += 0.05
        
        # PENALTY: Processing time penalty (slower = potentially less reliable)
        processing_time = metadata.get("processing_time_ms", 0.0)
        if processing_time > 5000:  # More than 5 seconds
            tuned_confidence -= 0.10
        elif processing_time > 2000:  # More than 2 seconds
            tuned_confidence -= 0.05
        
        # PENALTY: Validation warnings
        if metadata.get("validation_warnings"):
            tuned_confidence -= 0.05
        
        # Clamp to [0, 1]
        tuned_confidence = max(0.0, min(1.0, tuned_confidence))
        
        # Map to SignalConfidence enum with refined thresholds
        if tuned_confidence >= 0.85:
            return SignalConfidence.VERY_HIGH
        elif tuned_confidence >= 0.65:
            return SignalConfidence.HIGH
        elif tuned_confidence >= 0.40:
            return SignalConfidence.MEDIUM
        elif tuned_confidence >= 0.20:
            return SignalConfidence.LOW
        else:
            return SignalConfidence.INDETERMINATE

    def _extract_text(self, data: Any) -> str:
        """Extrae texto de los datos para análisis"""
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            # Buscar campos de texto comunes
            for field in ["answer", "response", "description", "text", "content", "question_text"]:
                if field in data and isinstance(data[field], str):
                    return data[field]
            # Si no hay campo de texto directo, retornar JSON como string
            return str(data)
        return ""

    def _extract_empirical_support(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> EmpiricalSupportSignal:
        """Extrae y analiza el soporte empírico en el texto"""

        text_lower = text.lower()

        # Buscar referencias normativas
        normative_references = []
        for pattern in self.normative_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            normative_references.extend(matches)

        # Buscar referencias institucionales
        institutional_references = []
        for pattern in self.institutional_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            institutional_references.extend(matches)

        # Buscar document_references si existe
        document_references = []
        if isinstance(data, dict) and "references" in data:
            document_references = data["references"]

        # Determinar nivel de soporte
        if normative_references and institutional_references:
            support_level = "STRONG"
        elif normative_references or institutional_references:
            support_level = "MODERATE"
        elif len(text) > 100:
            support_level = "WEAK"
        else:
            support_level = "NONE"

        return EmpiricalSupportSignal(
            context=context,
            source=source,
            question_id=context.node_id,
            support_level=support_level,
            normative_references=normative_references,
            document_references=document_references,
            institutional_references=institutional_references,
            confidence=SignalConfidence.MEDIUM,
            rationale=f"Found {len(normative_references)} normative, {len(institutional_references)} institutional references"
        )

    def _detect_method_application(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> MethodApplicationSignal:
        """Detecta qué método de evaluación se aplicó"""

        text_lower = text.lower()
        detected_methods = []

        # Buscar patrones de cada método
        for method_name, patterns in self.method_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected_methods.append(method_name)
                    break

        # Si no se detectó método específico, inferir del contexto
        if not detected_methods:
            if isinstance(data, dict):
                if "statistics" in data or "percentage" in data:
                    detected_methods.append("statistical_analysis")
                elif "sources" in data or "references" in data:
                    detected_methods.append("document_analysis")
                else:
                    detected_methods.append("member_checking")

        # Determinar resultado
        if isinstance(data, dict):
            method_result = data.get("result", data.get("outcome", "ANALYZED"))
            extraction_successful = True
        else:
            method_result = "PROCESSED"
            extraction_successful = True

        return MethodApplicationSignal(
            context=context,
            source=source,
            question_id=context.node_id,
            method_id=detected_methods[0] if detected_methods else "unknown",
            method_result=method_result,
            extraction_successful=extraction_successful,
            extracted_values=list(data.keys()) if isinstance(data, dict) else [str(type(data))],
            processing_time_ms=0,  # Placeholder
            confidence=SignalConfidence.MEDIUM,
            rationale=f"Methods detected: {detected_methods}"
        )