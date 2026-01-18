"""SISAS Signal Consumption Compatibility Layer.

This module provides backward compatibility for code importing from SISAS.signal_consumption.
It re-exports components from _deprecated/signal_consumption.py.

Note: This is a compatibility shim. The actual implementation is in _deprecated/.
"""

from ._deprecated.signal_consumption import (
    AccessLevel,
    get_access_audit,
    QuestionnaireAccessAudit,
    SignalConsumptionProof,
)

__all__ = [
    "AccessLevel",
    "get_access_audit",
    "QuestionnaireAccessAudit",
    "SignalConsumptionProof",
]
