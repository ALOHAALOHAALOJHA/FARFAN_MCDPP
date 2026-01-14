# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/audit/decision_auditor.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.event import EventStore, EventType
from ..core.signal import Signal

@dataclass
class AuditReport:
    """Reporte de auditoría"""
    audit_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "PASS" # PASS, FAIL, WARN
    issues: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionAuditor:
    """
    Auditor de decisiones.
    Verifica que toda decisión del sistema esté justificada por señales.
    
    Principio: Ninguna decisión sin trail de señales.
    JF-10: Auditoría bajo demanda.
    """
    
    event_store: EventStore
    
    def audit_decisions(self) -> AuditReport:
        """
        Audita decisiones y su trazabilidad.
        Verifica:
        1. Decisiones justificables solo con señales.
        2. Trazabilidad completa desde dato hasta decisión.
        """
        report = AuditReport(audit_type="decision_audit")
        
        # Eventos que implican una decisión o acción crítica
        decision_event_types = [
            EventType.IRRIGATION_STARTED,
            EventType.CONTRAST_DIVERGENCE_DETECTED,
            EventType.CONSUMER_PROCESSED_DATA
        ]
        
        all_decision_events = []
        for etype in decision_event_types:
            all_decision_events.extend(self.event_store.get_by_type(etype))
            
        total_decisions = len(all_decision_events)
        unjustified_decisions = 0
        broken_trails = 0
        
        for event in all_decision_events:
            # 1. Verificar causación (causation_id debe apuntar a una señal generada)
            if not event.causation_id:
                # Si no tiene causación directa, buscar en payload evidencias de señales
                if not self._has_signal_evidence(event):
                    unjustified_decisions += 1
                    report.issues.append(f"Decision event {event.event_id} has no signal trail")
            
            # 2. Verificar trazabilidad (debe existir el ancestro)
            elif not self.event_store.get_by_id(event.causation_id):
                broken_trails += 1
                report.issues.append(f"Decision event {event.event_id} has broken trail (causation_id not found)")
        
        report.stats = {
            "total_decisions": total_decisions,
            "unjustified_decisions": unjustified_decisions,
            "broken_trails": broken_trails
        }
        
        if unjustified_decisions > 0 or broken_trails > 0:
            report.status = "FAIL"
            
        return report

    def _has_signal_evidence(self, event: Any) -> bool:
        """Busca evidencia de señales en el payload"""
        if not event.payload or not event.payload.data:
            return False
            
        data = event.payload.data
        # Buscamos campos que referencien señales
        signal_markers = ["signal_id", "signals", "evidence", "trigger_signal"]
        
        return any(marker in data for marker in signal_markers)
