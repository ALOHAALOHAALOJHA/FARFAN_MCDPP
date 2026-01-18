"""
Phase 5 Interphase Package (NEW v2.0)
=======================================

This package contains the interface contracts for Phase 5 (Area Aggregation).
These contracts define:

1. Entry Contract: Defines the input requirements from Phase 4
2. Exit Contract: Defines the output requirements for Phase 6
3. Nexus Interface: Defines internal Phase 5 data flow

Interface Contracts:
    - phase5_entry_contract: Input from Phase 4 (60 DimensionScore)
    - phase5_exit_contract: Output to Phase 6 (10 AreaScore)

Author: F.A.R.F.A.N. Pipeline Team
Version: 2.0.0
"""

from __future__ import annotations

__version__ = "2.0.0"
__phase__ = 5
__author__ = "F.A.R.F.A.N Core Team"

__all__ = [
    "phase5_entry_contract",
    "phase5_exit_contract",
]
