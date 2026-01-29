# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/vehicles/signal_intelligence_layer.py

from dataclasses import dataclass, field
from typing import Any, Dict, List
import re

from .base_vehicle import BaseVehicle, VehicleCapabilities
from ..core.signal import Signal, SignalContext, SignalSource, SignalConfidence
from ..core.event import Event
from ..core.contracts import PublicationContract, ContractType, ContractStatus, SignalTypeSpec
from ..signal_types.types.epistemic import (
    AnswerDeterminacySignal,
    AnswerSpecificitySignal,
    MethodApplicationSignal,
    DeterminacyLevel,
    SpecificityLevel
)

@dataclass
class SignalIntelligenceLayerVehicle(BaseVehicle):
    """
    Vehículo: signal_intelligence_layer

    Responsabilidad: Capa de inteligencia para análisis epistémico.

    Archivos que procesa:
    - Respuestas del cuestionario (Q*.json)
    - Texto que requiere análisis de determinación y especificidad
    """
    vehicle_id: str = "signal_intelligence_layer"
    vehicle_name: str = "Signal Intelligence Layer Vehicle"

    capabilities: VehicleCapabilities = field(default_factory=lambda: VehicleCapabilities(
        can_load=False,
        can_scope=False,
        can_extract=False,
        can_transform=True,
        can_enrich=False,
        can_validate=False,
        can_irrigate=False,
        signal_types_produced=["MethodApplicationSignal", "AnswerDeterminacySignal", "AnswerSpecificitySignal"]
    ))

    def __post_init__(self):
        # Crear contrato de publicación
        self.publication_contract = PublicationContract(
            contract_id=f"pub_{self.vehicle_id}",
            publisher_vehicle=self.vehicle_id,
            status=ContractStatus.ACTIVE,
            allowed_signal_types=[
                SignalTypeSpec(signal_type="MethodApplicationSignal"),
                SignalTypeSpec(signal_type="AnswerDeterminacySignal"),
                SignalTypeSpec(signal_type="AnswerSpecificitySignal")
            ],
            allowed_buses=["epistemic_bus", "intelligence_bus"],
            require_context=True,
            require_source=True
        )
        if self.contract_registry:
            self.contract_registry.register(self.publication_contract)

    # Patrones para detección de determinación
    affirmative_patterns: List[str] = field(default_factory=lambda: [
        r"\bs[íi]\b",
        r"\bexiste\b",
        r"\bse realiza\b",
        r"\bcuenta con\b",
        r"\bdispone\b",
        r"\btiene\b",
        r"\bposee\b",
        r"\bs[íi],\s",
    ])

    ambiguity_patterns: List[str] = field(default_factory=lambda: [
        r"\balgunos?\s+casi?\b",
        r"\ba\s+veces?\b",
        r"\bparcialmente\b",
        r"\ben\s+algunos?\s+casi?\b",
        r"\bcuando\s+corresponda\b",
        r"\bsolo\s+en\b",
        r"\bseg[úu]n\b",
    ])

    negation_patterns: List[str] = field(default_factory=lambda: [
        r"\bno\b",
        r"\bnunca\b",
        r"\bning[úu]n\b?",
        r"\bjam[áa]s\b",
        r"\bnada\b",
    ])

    conditional_patterns: List[str] = field(default_factory=lambda: [
        r"\bsi\s+\w+\s*,?",
        r"\bcuando\s+\w+\s*,?",
        r"\bdependiendo\s+de\b",
        r"\ben\s+caso\s+de\b",
        r"\bcondicionado\s+a\b",
    ])

    # Patrones para especificidad
    specificity_indicators: Dict[str, List[str]] = field(default_factory=lambda: {
        "formal_instrument": [
            r"\bley\s+\d+",
            r"\bdecreto\s+\d+",
            r"\bresoluci[óo]n\s+\d+",
            r"\bestatuto\s+",
            r"\bordenanza\s+",
            r"\breglamento\s+",
        ],
        "mandatory_scope": [
            r"\bobligatori?\b",
            r"\bdebe\b",
            r"\brequiere\b",
            r"\bexige\b",
            r"\bmándato\b",
            r"\bmandatorio\b",
        ],
        "institutional_owner": [
            r"\bministerio\s+de\s+\w+",
            r"\bdepartamento\s+",
            r"\bentidad\s+",
            r"\bcontralor[íi]a\b",
            r"\bprocuradur[íi]a\b",
            r"\bfiscal[íi]a\b",
            r"\bdefensor[íi]a\b",
            r"\bunidad\s+\w+",
            r"\bsecretar[íi]a\s+",
        ],
        "quantitative_data": [
            r"\d+%\s*de\b",
            r"\d+\s*(?:horas|d[íi]as|meses|a[ñn]os)",
            r"\bpara\s+\d+\s+\w+",
            r"\bmetros?\s+cuadrados?\b",
        ]
    })

    def process(self, data: Any, context: SignalContext) -> List[Signal]:
        """
        Procesa datos y genera señales epistémicas de inteligencia.
        """
        signals = []

        # Crear evento
        event = self.create_event(
            event_type="intelligence_analysis",
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
            # 1. Señal de determinación de respuesta
            determinacy_signal = self._analyze_answer_determinacy(text, data, context, source)
            signals.append(determinacy_signal)

            # 2. Señal de especificidad de respuesta
            specificity_signal = self._analyze_answer_specificity(text, data, context, source)
            signals.append(specificity_signal)

            # 3. Señal de aplicación de método (enriquecida)
            method_signal = self._detect_method_application_enriched(text, data, context, source)
            signals.append(method_signal)

        self.stats["signals_generated"] += len(signals)
        return signals

    def _extract_text(self, data: Any) -> str:
        """Extrae texto de los datos para análisis"""
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            # Buscar campos de texto comunes
            for field in ["answer", "response", "description", "text", "content", "question_text", "value"]:
                if field in data and isinstance(data[field], str):
                    return data[field]
            # Si no hay campo de texto directo, retornar JSON como string
            return str(data)
        return ""

    def _analyze_answer_determinacy(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> AnswerDeterminacySignal:
        """Analiza el nivel de determinación de una respuesta"""

        text_lower = text.lower()

        # Buscar marcadores
        affirmative_markers = []
        for pattern in self.affirmative_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            affirmative_markers.extend(matches)

        ambiguity_markers = []
        for pattern in self.ambiguity_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            ambiguity_markers.extend(matches)

        negation_markers = []
        for pattern in self.negation_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            negation_markers.extend(matches)

        conditional_markers = []
        for pattern in self.conditional_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            conditional_markers.extend(matches)

        # Determinar nivel de determinación
        if negation_markers:
            determinacy_level = DeterminacyLevel.LOW
        elif affirmative_markers and not ambiguity_markers and not conditional_markers:
            determinacy_level = DeterminacyLevel.HIGH
        elif affirmative_markers and (ambiguity_markers or conditional_markers):
            determinacy_level = DeterminacyLevel.MEDIUM
        elif ambiguity_markers and not conditional_markers:
            determinacy_level = DeterminacyLevel.MEDIUM
        elif conditional_markers:
            determinacy_level = DeterminacyLevel.LOW
        else:
            determinacy_level = DeterminacyLevel.INDETERMINATE

        return AnswerDeterminacySignal(
            context=context,
            source=source,
            question_id=context.node_id,
            determinacy_level=determinacy_level,
            affirmative_markers=affirmative_markers,
            ambiguity_markers=ambiguity_markers,
            negation_markers=negation_markers,
            conditional_markers=conditional_markers,
            confidence=SignalConfidence.HIGH if determinacy_level in [DeterminacyLevel.HIGH, DeterminacyLevel.LOW] else SignalConfidence.MEDIUM,
            rationale=f"Determinacy: {determinacy_level.value} ({len(affirmative_markers)} aff, {len(ambiguity_markers)} amb, {len(negation_markers)} neg)"
        )

    def _analyze_answer_specificity(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> AnswerSpecificitySignal:
        """Analiza el nivel de especificidad de una respuesta"""

        text_lower = text.lower()

        # Elementos esperados para alta especificidad
        expected_elements = ["formal_instrument", "mandatory_scope", "institutional_owner"]

        # Buscar elementos encontrados
        found_elements = []
        for element_type, patterns in self.specificity_indicators.items():
            if element_type in expected_elements:
                for pattern in patterns:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        if element_type not in found_elements:
                            found_elements.append(element_type)
                        break

        # Elementos faltantes
        missing_elements = [e for e in expected_elements if e not in found_elements]

        # Determinar nivel de especificidad
        specificity_score = len(found_elements) / len(expected_elements) if expected_elements else 0

        if specificity_score >= 0.8:
            specificity_level = SpecificityLevel.HIGH
        elif specificity_score >= 0.5:
            specificity_level = SpecificityLevel.MEDIUM
        elif specificity_score > 0:
            specificity_level = SpecificityLevel.LOW
        else:
            specificity_level = SpecificityLevel.NONE

        return AnswerSpecificitySignal(
            context=context,
            source=source,
            question_id=context.node_id,
            specificity_level=specificity_level,
            expected_elements=expected_elements,
            found_elements=found_elements,
            missing_elements=missing_elements,
            specificity_score=specificity_score,
            confidence=SignalConfidence.HIGH,
            rationale=f"Specificity: {specificity_level.value} ({len(found_elements)}/{len(expected_elements)} elements)"
        )

    def _detect_method_application_enriched(
        self,
        text: str,
        data: Dict[str, Any],
        context: SignalContext,
        source: SignalSource
    ) -> MethodApplicationSignal:
        """Detecta aplicación de método con análisis enriquecido"""

        # Patrones de métodos
        method_patterns = {
            "triangulation": [r"\bcruz", r"\btriangula", r"\bcompara", r"\bcontrast"],
            "member_checking": [r"\bverifica", r"\bconfirma", r"\bconsult", r"\bentrevista"],
            "document_analysis": [r"\ban[áa]lisis\s+documental", r"\brevisi[óo]n\s+normativa", r"\bestudio\s+jur[íi]dico"],
            "statistical_analysis": [r"\bestad[íi]stica", r"\bporcentaje", r"\bmedia\s+de", r"\btasa\s+de"]
        }

        text_lower = text.lower()
        detected_methods = []

        # Buscar patrones de cada método
        for method_name, patterns in method_patterns.items():
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
                    detected_methods.append("content_analysis")
            else:
                detected_methods.append("text_analysis")

        # Determinar resultado
        if isinstance(data, dict):
            method_result = data.get("result", data.get("outcome", {"status": "ANALYZED", "confidence": "MEDIUM"}))
            extraction_successful = True
        else:
            method_result = {"status": "PROCESSED", "input_type": str(type(data))}
            extraction_successful = True

        return MethodApplicationSignal(
            context=context,
            source=source,
            question_id=context.node_id,
            method_id=detected_methods[0] if detected_methods else "unknown",
            method_result=method_result,
            extraction_successful=extraction_successful,
            extracted_values=list(data.keys()) if isinstance(data, dict) else [str(type(data))],
            processing_time_ms=0,
            confidence=SignalConfidence.HIGH if detected_methods else SignalConfidence.MEDIUM,
            rationale=f"Intelligence layer detected: {detected_methods}"
        )


@dataclass
class EnrichedSignalPack:
    """Pack containing enriched signals for a specific context."""
    base_pack: Dict[str, Any]
    expanded_signals: List[Signal] = field(default_factory=list)

    def get_patterns_for_context(self) -> List[Dict[str, Any]]:
        return self.base_pack.get("patterns", [])


def create_enriched_signal_pack(
    base_signal_pack: Dict[str, Any],
    enable_semantic_expansion: bool = True
) -> EnrichedSignalPack:
    """Creates an enriched signal pack."""
    return EnrichedSignalPack(base_pack=base_signal_pack)
