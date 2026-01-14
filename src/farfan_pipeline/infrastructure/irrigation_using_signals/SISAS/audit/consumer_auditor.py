# src/farfan_pipeline/infrastructure/irrigation_using_signals/SISAS/audit/consumer_auditor.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..consumers.base_consumer import BaseConsumer

@dataclass
class ConsumerAuditor:
    """
    Auditor de consumidores.
    Verifica salud y actividad de los consumidores registrados.
    """

    consumers: List[BaseConsumer]

    def audit_consumers(self) -> Dict[str, Any]:
        """Audita todos los consumidores"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_consumers": len(self.consumers),
            "healthy": 0,
            "unhealthy": 0,
            "details": []
        }

        for consumer in self.consumers:
            health = consumer.get_health()
            is_healthy = True # Simple check

            # Check error rate
            stats = health["stats"]
            total = stats.get("signals_processed", 0) + stats.get("signals_failed", 0)
            if total > 0:
                error_rate = stats.get("signals_failed", 0) / total
                if error_rate > 0.05: # 5% error rate threshold
                    is_healthy = False

            if is_healthy:
                results["healthy"] += 1
            else:
                results["unhealthy"] += 1

            results["details"].append({
                "consumer_id": consumer.consumer_id,
                "healthy": is_healthy,
                "health_data": health
            })

        return results
