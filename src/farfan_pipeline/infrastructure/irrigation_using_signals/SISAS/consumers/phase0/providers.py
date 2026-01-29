# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase0/providers.py

from dataclasses import dataclass
from typing import Any, Dict

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase0ProvidersConsumer(BaseConsumer):
    """
    Consumidor para providers configuration en Phase 0.

    Procesa señales relacionadas con la configuración de proveedores
    de datos canónicos (clusters, dimensions, policy areas, etc.).

    Responsabilidad: Validar que los proveedores están correctamente
    configurados y sus dependencias son satisfechas.
    """

    consumer_id: str = "providers.py"
    consumer_phase: str = "phase_00"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE0_PROVIDERS",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "StructuralAlignmentSignal",
                "DataIntegritySignal",
                "LegacyDependencySignal"
            ],
            subscribed_buses=["structural_bus", "integrity_bus", "operational_bus"],
            context_filters={
                "phase": ["phase_00"],
                "consumer_scope": ["Phase_00"]
            },
            required_capabilities=["can_validate"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales relacionadas con providers.

        Enfoque: Verificar que cada provider:
        - Tiene estructura correcta
        - Referencia archivos que existen
        - No tiene dependencias circulares
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "provider_analysis": {},
            "validation_status": "UNKNOWN"
        }

        if signal.signal_type == "StructuralAlignmentSignal":
            analysis = self._validate_provider_structure(signal)
            result["provider_analysis"] = analysis
            result["validation_status"] = analysis.get("status", "UNKNOWN")

        elif signal.signal_type == "DataIntegritySignal":
            analysis = self._validate_provider_references(signal)
            result["provider_analysis"] = analysis
            result["validation_status"] = analysis.get("status", "UNKNOWN")

        elif signal.signal_type == "LegacyDependencySignal":
            analysis = self._analyze_provider_dependencies(signal)
            result["provider_analysis"] = analysis

        return result

    def _validate_provider_structure(self, signal: Signal) -> Dict[str, Any]:
        """Valida la estructura de un provider"""
        alignment_status = str(getattr(signal, 'alignment_status', 'UNKNOWN'))
        missing = getattr(signal, 'missing_elements', [])

        status = "VALID"
        issues = []

        if alignment_status == "AlignmentStatus.MISALIGNED":
            status = "INVALID"
            issues.append("Provider structure does not match expected schema")

        if missing:
            status = "INCOMPLETE"
            issues.extend([f"Missing required element: {elem}" for elem in missing])

        return {
            "status": status,
            "alignment": alignment_status,
            "issues": issues,
            "elements_missing": len(missing)
        }

    def _validate_provider_references(self, signal: Signal) -> Dict[str, Any]:
        """Valida las referencias de un provider"""
        broken = getattr(signal, 'broken_references', [])
        score = getattr(signal, 'integrity_score', 1.0)

        status = "VALID" if score >= 0.9 else "INVALID" if score < 0.5 else "WARNING"

        return {
            "status": status,
            "integrity_score": score,
            "broken_references": broken,
            "broken_count": len(broken),
            "recommendation": "Fix broken references" if broken else "OK"
        }

    def _analyze_provider_dependencies(self, signal: Signal) -> Dict[str, Any]:
        """Analiza dependencias entre providers"""
        upstream = getattr(signal, 'upstream_dependencies', [])
        downstream = getattr(signal, 'downstream_dependents', [])
        criticality = getattr(signal, 'criticality', 'unknown')

        return {
            "component": getattr(signal, 'legacy_component', 'unknown'),
            "upstream_dependencies": upstream,
            "downstream_dependents": downstream,
            "dependency_count": len(upstream) + len(downstream),
            "criticality": criticality,
            "has_circular_deps": self._check_circular(upstream, downstream)
        }

    def _check_circular(self, upstream: list, downstream: list) -> bool:
        """Simple check for potential circular dependencies"""
        # If a component appears in both upstream and downstream, potential circular dep
        common = set(upstream).intersection(set(downstream))
        return len(common) > 0
