"""
Phase 4-7 Interface Package
============================

This package contains the interface contracts for the hierarchical aggregation
pipeline (Phases 4-7). These contracts define:

1. Entry Contract: Defines the input requirements from Phase 3
2. Exit Contract: Defines the output requirements for Phase 8
3. Nexus Interface: Defines the internal node delivery and receipt relationships

Interface Contracts:
    - phase4_7_entry_contract: Input from Phase 3 (ScoredResult[])
    - phase4_7_exit_contract: Output to Phase 8 (MacroScore)
    - phase4_7_nexus_interface: Internal node relationships

Author: F.A.R.F.A.N. Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

from . import (
    phase4_10_00_phase4_7_entry_contract as phase4_7_entry_contract,
    phase4_10_00_phase4_7_exit_contract as phase4_7_exit_contract,
)

__all__ = [
    "phase4_7_entry_contract",
    "phase4_7_exit_contract",
]
