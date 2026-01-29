"""
Phase 7 Contracts Module

This module provides Design by Contract specifications for Phase 7 Macro Evaluation.
All contracts are enforced by default to ensure deterministic and canonical flow.

Module: src/farfan_pipeline/phases/Phase_07/contracts/__init__.py
Purpose: Contract enforcement and validation for Phase 7
Owner: phase7_contracts
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-18
"""

# METADATA
__version__ = "1.0.0"
__phase__ = 7
__stage__ = 0
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-18T00:00:00Z"
__modified__ = "2026-01-18T00:00:00Z"
__criticality__ = "CRITICAL"
__execution_pattern__ = "Per-Task"

from .phase7_10_00_input_contract import Phase7InputContract
from .phase7_10_01_mission_contract import Phase7MissionContract
from .phase7_10_02_output_contract import Phase7OutputContract

__all__ = [
    "Phase7InputContract",
    "Phase7MissionContract",
    "Phase7OutputContract",
]
