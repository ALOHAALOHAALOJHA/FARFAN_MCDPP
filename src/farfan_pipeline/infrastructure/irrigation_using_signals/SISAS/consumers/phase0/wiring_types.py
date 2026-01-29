# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/consumers/phase0/wiring_types.py

from dataclasses import dataclass
from typing import Any, Dict, List

from ..base_consumer import BaseConsumer
from ...core.signal import Signal
from ...core.contracts import ConsumptionContract


@dataclass
class Phase0WiringTypesConsumer(BaseConsumer):
    """
    Consumidor para wiring_types configuration en Phase 0.

    Procesa señales relacionadas con la configuración de tipos
    y su cableado (wiring) en el sistema.

    Responsabilidad: Validar que los tipos están correctamente
    definidos y cableados entre componentes.
    """

    consumer_id: str = "wiring_types.py"
    consumer_phase: str = "phase_00"

    def __post_init__(self):
        super().__post_init__()

        self.consumption_contract = ConsumptionContract(
            contract_id="CC_PHASE0_WIRING_TYPES",
            consumer_id=self.consumer_id,
            consumer_phase=self.consumer_phase,
            subscribed_signal_types=[
                "StructuralAlignmentSignal",
                "SchemaConflictSignal",
                "TemporalCouplingSignal"
            ],
            subscribed_buses=["structural_bus", "consumption_bus"],
            context_filters={
                "phase": ["phase_00"],
                "consumer_scope": ["Phase_00"]
            },
            required_capabilities=["can_validate", "can_scope"]
        )

    def process_signal(self, signal: Signal) -> Dict[str, Any]:
        """
        Procesa señales relacionadas con wiring types.

        Enfoque: Verificar que:
        - Los tipos están correctamente definidos
        - No hay conflictos de schema
        - El acoplamiento temporal es adecuado
        """
        result = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "processed": True,
            "wiring_analysis": {},
            "validation_status": "UNKNOWN"
        }

        if signal.signal_type == "StructuralAlignmentSignal":
            analysis = self._analyze_type_structure(signal)
            result["wiring_analysis"] = analysis
            result["validation_status"] = analysis.get("status", "UNKNOWN")

        elif signal.signal_type == "SchemaConflictSignal":
            analysis = self._analyze_schema_conflicts(signal)
            result["wiring_analysis"] = analysis
            result["validation_status"] = "CONFLICT" if analysis.get("is_breaking") else "WARNING"

        elif signal.signal_type == "TemporalCouplingSignal":
            analysis = self._analyze_coupling(signal)
            result["wiring_analysis"] = analysis

        return result

    def _analyze_type_structure(self, signal: Signal) -> Dict[str, Any]:
        """Analiza la estructura de definición de tipos"""
        alignment_status = str(getattr(signal, 'alignment_status', 'UNKNOWN'))
        missing = getattr(signal, 'missing_elements', [])
        extra = getattr(signal, 'extra_elements', [])

        status = "VALID"
        issues = []

        if missing:
            status = "INCOMPLETE"
            issues.append(f"Missing {len(missing)} type definitions")

        if extra:
            issues.append(f"Found {len(extra)} unexpected type definitions")

        return {
            "status": status,
            "alignment": alignment_status,
            "issues": issues,
            "missing_types": missing,
            "extra_types": extra
        }

    def _analyze_schema_conflicts(self, signal: Signal) -> Dict[str, Any]:
        """Analiza conflictos de schema"""
        conflict_type = getattr(signal, 'conflict_type', 'unknown')
        is_breaking = getattr(signal, 'is_breaking', False)
        conflicting_fields = getattr(signal, 'conflicting_fields', [])
        expected_version = getattr(signal, 'expected_schema_version', '')
        actual_version = getattr(signal, 'actual_schema_version', '')

        severity = "CRITICAL" if is_breaking else "WARNING"

        recommendations = []
        if is_breaking:
            recommendations.append("Immediate action required - breaking change detected")
        if conflict_type == "type_mismatch":
            recommendations.append("Update type definitions to match expected schema")
        if conflict_type == "missing_field":
            recommendations.append("Add missing required fields")

        return {
            "severity": severity,
            "conflict_type": conflict_type,
            "is_breaking": is_breaking,
            "conflicting_fields": conflicting_fields,
            "conflicting_count": len(conflicting_fields),
            "expected_version": expected_version,
            "actual_version": actual_version,
            "recommendations": recommendations,
            "suggested_resolution": getattr(signal, 'suggested_resolution', '')
        }

    def _analyze_coupling(self, signal: Signal) -> Dict[str, Any]:
        """Analiza acoplamiento temporal entre componentes"""
        component_a = getattr(signal, 'component_a', '')
        component_b = getattr(signal, 'component_b', '')
        correlation = getattr(signal, 'correlation_coefficient', 0.0)
        strength = getattr(signal, 'coupling_strength', 'unknown')
        lag_ms = getattr(signal, 'typical_lag_ms', 0.0)

        insights = []
        if correlation > 0.9:
            insights.append(f"Strong coupling detected ({correlation:.2f})")
            insights.append("Consider architectural review for tight coupling")
        elif correlation < -0.5:
            insights.append(f"Negative correlation detected ({correlation:.2f})")
            insights.append("Components may be conflicting")

        if lag_ms > 5000:
            insights.append(f"High latency detected ({lag_ms:.0f}ms)")

        return {
            "component_a": component_a,
            "component_b": component_b,
            "correlation": correlation,
            "coupling_strength": strength,
            "typical_lag_ms": lag_ms,
            "insights": insights,
            "recommendation": self._get_coupling_recommendation(correlation, strength)
        }

    def _get_coupling_recommendation(self, correlation: float, strength: str) -> str:
        """Genera recomendación basada en el acoplamiento"""
        if correlation > 0.9 and strength == "strong":
            return "Consider decoupling or making dependency explicit"
        elif correlation > 0.7:
            return "Monitor coupling - may need refactoring"
        elif correlation < 0.2:
            return "Coupling is acceptable"
        else:
            return "Review component interaction patterns"
