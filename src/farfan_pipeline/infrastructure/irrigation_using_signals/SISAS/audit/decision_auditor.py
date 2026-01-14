# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/audit/decision_auditor.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.bus import BusRegistry

@dataclass
class DecisionAuditor:
    """
    Auditor de decisiones.
    Verifica que las decisiones estén soportadas por señales (trazabilidad).
    """

    bus_registry: BusRegistry

    def audit_decisions(self) -> Dict[str, Any]:
        """
        Audita señales de decisión/contraste para asegurar que tienen justificación.
        """
        # Busca señales de tipo DecisionDivergenceSignal o similar en los buses (contrast_bus)
        contrast_bus = self.bus_registry.get_bus("contrast_bus")
        if not contrast_bus:
            return {"error": "No contrast_bus found"}

        decisions_checked = 0
        justified = 0

        # Access history
        messages = contrast_bus._message_history

        for msg in messages:
            signal = msg.signal
            if signal.signal_type == "DecisionDivergenceSignal":
                decisions_checked += 1
                # Verificar que tiene supporting_signals
                supporting = getattr(signal, 'supporting_signals', [])
                if supporting:
                    justified += 1

        return {
            "decisions_checked": decisions_checked,
            "justified_decisions": justified,
            "unjustified_decisions": decisions_checked - justified
        }
