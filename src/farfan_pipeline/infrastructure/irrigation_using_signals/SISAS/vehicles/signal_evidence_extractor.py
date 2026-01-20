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
        """
        signals = []

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