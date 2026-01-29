# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/audit/signal_auditor.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.bus import BusRegistry, SignalBus
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
class SignalAuditor:
    """
    Auditor de señales.
    Verifica integridad, trazabilidad y completitud de las señales.
    
    JF-10: Auditoría continua.
    """

    bus_registry: BusRegistry

    def audit_signals(self) -> AuditReport:
        """
        Ejecuta auditoría de todas las señales en los buses.
        Verifica:
        1. Ninguna señal huérfana (debe tener source).
        2. Source válido.
        3. Consistencia de hash determinístico.
        """
        report = AuditReport(audit_type="signal_audit")
        total_signals = 0
        orphan_signals = 0
        corrupted_hashes = 0
        invalid_sources = 0

        for bus_name, bus in self.bus_registry.buses.items():
            # Nota: Acceder a _message_history para auditoría interna
            messages = getattr(bus, '_message_history', [])
            total_signals += len(messages)

            for msg in messages:
                signal = msg.signal
                
                # 1. Verificar si es huérfana
                if not signal.source:
                    orphan_signals += 1
                    report.issues.append(f"Signal {signal.signal_id} ({signal.signal_type}) is orphan (no source)")
                
                # 2. Verificar source válido (debe tener event_id o similar)
                elif not signal.source.event_id and not signal.source.source_file:
                    invalid_sources += 1
                    report.issues.append(f"Signal {signal.signal_id} has invalid source metadata")

                # 3. Verificar integridad del hash
                current_hash = getattr(signal, 'hash', '')
                if not current_hash:
                    # Si no lo tiene guardado (ej: dict), lo calculamos
                    current_hash = signal.compute_hash()
                
                if signal.compute_hash() != current_hash:
                    corrupted_hashes += 1
                    report.issues.append(f"Signal {signal.signal_id} has hash mismatch (corrupted)")

        report.stats = {
            "total_signals": total_signals,
            "orphan_signals": orphan_signals,
            "corrupted_hashes": corrupted_hashes,
            "invalid_sources": invalid_sources
        }

        if orphan_signals > 0 or corrupted_hashes > 0:
            report.status = "FAIL"
        elif invalid_sources > 0:
            report.status = "WARN"

        return report