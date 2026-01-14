# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase0/phase0_90_02_bootstrap.py

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase0BootstrapConsumer(BaseConsumer):
    """
    Consumidor para bootstrap en Phase 0.

    Procesa señales relacionadas con:
    - Clusters (metadata.json, questions.json, aggregation_rules.json)
    - Dimensions (metadata.json, questions.json, pdet_context.json)
    - Policy Areas (metadata.json, questions.json, keywords.json)
    - Cross-cutting themes
    - Scoring and governance

    Responsabilidad: Analizar la estructura canónica base del sistema.
    """

    consumer_id: str = "phase0_90_02_bootstrap.py"
    consumer_phase: str = "phase_0"

    def __post_init__(self):
        super().__post_init__()

        # Configurar contrato de consumo
        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE0_BOOTSTRAP",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "StructuralAlignmentSignal",
                "CanonicalMappingSignal",
                "EventPresenceSignal",
                "EventCompletenessSignal",
                "DataIntegritySignal"
            ],
            subscribed_buses=["structural_bus", "integrity_bus"],
            context_filters={
                "phase": ["phase_0"],
                "consumer_scope": ["Phase_0", "Cross-Phase"]
            },
            required_capabilities=["can_load", "can_scope"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa una señal recibida en Phase 0.

        Analiza la estructura canónica y genera insights sobre:
        - Completitud de metadatos
        - Integridad de referencias
        - Alineación estructural
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "analysis": {},
            "insights": []
        }

        if signal.signal_type == "StructuralAlignmentSignal":
            result["analysis"] = self._analyze_structural_alignment(signal)
        elif signal.signal_type == "CanonicalMappingSignal":
            result["analysis"] = self._analyze_canonical_mapping(signal)
        elif signal.signal_type == "EventPresenceSignal":
            result["analysis"] = self._analyze_event_presence(signal)
        elif signal.signal_type == "EventCompletenessSignal":
            result["analysis"] = self._analyze_completeness(signal)
        elif signal.signal_type == "DataIntegritySignal":
            result["analysis"] = self._analyze_integrity(signal)

        return result

    def _analyze_structural_alignment(self, signal: Signal) -> Dict[str, Any]:
        """Analiza señal de alineación estructural"""
        alignment_status = getattr(signal, 'alignment_status', None)
        missing = getattr(signal, 'missing_elements', [])
        extra = getattr(signal, 'extra_elements', [])

        insights = []
        if missing:
            insights.append(f"Missing {len(missing)} required elements")
        if extra:
            insights.append(f"Found {len(extra)} unexpected elements")

        return {
            "alignment_status": str(alignment_status),
            "missing_elements": missing,
            "extra_elements": extra,
            "canonical_path": getattr(signal, 'canonical_path', ''),
            "actual_path": getattr(signal, 'actual_path', ''),
            "insights": insights
        }

    def _analyze_canonical_mapping(self, signal: Signal) -> Dict[str, Any]:
        """Analiza señal de mapeo canónico"""
        mapped = getattr(signal, 'mapped_entities', {})
        unmapped = getattr(signal, 'unmapped_aspects', [])
        completeness = getattr(signal, 'mapping_completeness', 0.0)

        insights = []
        if completeness < 0.5:
            insights.append("Low mapping completeness - requires attention")
        if unmapped:
            insights.append(f"{len(unmapped)} aspects could not be mapped")

        return {
            "mapped_entities": mapped,
            "unmapped_aspects": unmapped,
            "mapping_completeness": completeness,
            "insights": insights
        }

    def _analyze_event_presence(self, signal: Signal) -> Dict[str, Any]:
        """Analiza señal de presencia de eventos"""
        presence = getattr(signal, 'presence_status', None)
        count = getattr(signal, 'event_count', 0)

        insights = []
        if str(presence) == "PresenceStatus.ABSENT":
            insights.append("Expected event not found")
        elif count > 1:
            insights.append(f"Multiple occurrences ({count}) - check for duplicates")

        return {
            "presence_status": str(presence),
            "event_count": count,
            "expected_event_type": getattr(signal, 'expected_event_type', ''),
            "insights": insights
        }

    def _analyze_completeness(self, signal: Signal) -> Dict[str, Any]:
        """Analiza señal de completitud"""
        completeness_level = getattr(signal, 'completeness_level', None)
        missing = getattr(signal, 'missing_fields', [])
        score = getattr(signal, 'completeness_score', 0.0)

        insights = []
        if score < 0.7:
            insights.append(f"Incomplete data ({score:.1%}) - missing {len(missing)} fields")

        return {
            "completeness_level": str(completeness_level),
            "completeness_score": score,
            "required_fields": getattr(signal, 'required_fields', []),
            "present_fields": getattr(signal, 'present_fields', []),
            "missing_fields": missing,
            "insights": insights
        }

    def _analyze_integrity(self, signal: Signal) -> Dict[str, Any]:
        """Analiza señal de integridad"""
        broken = getattr(signal, 'broken_references', [])
        score = getattr(signal, 'integrity_score', 0.0)

        insights = []
        if broken:
            insights.append(f"Found {len(broken)} broken references - requires fixing")
        if score < 0.8:
            insights.append(f"Low integrity score ({score:.1%})")

        return {
            "source_file": getattr(signal, 'source_file', ''),
            "referenced_files": getattr(signal, 'referenced_files', []),
            "valid_references": getattr(signal, 'valid_references', []),
            "broken_references": broken,
            "integrity_score": score,
            "insights": insights
        }
