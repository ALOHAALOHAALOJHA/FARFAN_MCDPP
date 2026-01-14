"""
SISAS Core Module - Signal Irrigation System Architecture (SOTA)

This module implements the TRUE signal-based irrigation system:
- Signal: Atomic unit of information flow
- SignalDistributionOrchestrator: Pub/sub dispatch engine
- Dead Letter Queue: Failed signal persistence
- Audit Trail: Full observability

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0 (SOTA Frontier)
"""

from .signal import Signal, SignalType, SignalScope
from .signal_distribution_orchestrator import SignalDistributionOrchestrator

__all__ = [
    "Signal",
    "SignalType", 
    "SignalScope",
    "SignalDistributionOrchestrator",
]
