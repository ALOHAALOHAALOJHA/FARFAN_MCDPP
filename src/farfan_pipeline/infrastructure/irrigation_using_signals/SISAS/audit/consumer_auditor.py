# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/audit/consumer_auditor.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.contracts import ContractRegistry
from ..signals.types.consumption import ConsumerHealthSignal

@dataclass
class AuditReport:
    """Reporte de auditoría"""
    audit_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "PASS" # PASS, FAIL, WARN
    issues: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConsumerAuditor:
    """
    Auditor de salud de consumidores.
    Verifica que los consumidores estén operativos y cumpliendo SLAs.
    
    JF-10: Auditoría cada 5 minutos.
    """
    
    contract_registry: ContractRegistry
    
    def audit_consumers(self, health_metrics: Dict[str, Any]) -> AuditReport:
        """
        Ejecuta auditoría de consumidores.
        Verifica:
        1. Todos los consumidores registrados están respondiendo.
        2. Error rate < 5%.
        3. Processing time < SLA.
        """
        report = AuditReport(audit_type="consumer_audit")
        total_consumers = 0
        unhealthy_consumers = 0
        sla_violations = 0
        
        for contract in self.contract_registry.consumption_contracts.values():
            total_consumers += 1
            consumer_id = contract.consumer_id
            
            # Obtener métricas para este consumidor
            metrics = health_metrics.get(consumer_id)
            if not metrics:
                unhealthy_consumers += 1
                report.issues.append(f"Consumer {consumer_id} is not reporting health metrics")
                continue
            
            # 1. Verificar error rate
            error_rate = metrics.get("error_rate", 0.0)
            if error_rate > 0.05:
                unhealthy_consumers += 1
                report.issues.append(f"Consumer {consumer_id} has high error rate: {error_rate:.2%}")
                
            # 2. Verificar processing time vs SLA
            avg_time = metrics.get("avg_processing_time_ms", 0.0)
            sla_ms = contract.max_processing_time_ms
            if avg_time > sla_ms:
                sla_violations += 1
                report.issues.append(f"Consumer {consumer_id} violates SLA: {avg_time}ms > {sla_ms}ms")
            
        report.stats = {
            "total_consumers": total_consumers,
            "unhealthy_consumers": unhealthy_consumers,
            "sla_violations": sla_violations
        }
        
        if unhealthy_consumers > 0:
            report.status = "FAIL"
        elif sla_violations > 0:
            report.status = "WARN"
            
        return report
