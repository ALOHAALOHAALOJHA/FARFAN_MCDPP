"""
Phase 8 Interfaces Package
==========================

This package defines all interface contracts for Phase 8 - Recommendation Engine.

Interface Documentation:
- What is RECEIVED: Analysis results, policy context, signal data (optional)
- From WHOM: Phase 7 (Aggregation & Synthesis), SISAS Signal Registry
- What is PROCESSED: Rule-based recommendation generation at MICRO/MESO/MACRO levels
- What is DELIVERED: Structured recommendations with metadata
- To WHOM: Phase 9 (Report Generation), Orchestrator

See INTERFACE_MANIFEST.json for complete specification.
"""

from .interface_validator import (
    Phase8InterfaceValidator,
    validate_phase8_inputs,
    validate_phase8_outputs,
)

__all__ = [
    "Phase8InterfaceValidator",
    "validate_phase8_inputs",
    "validate_phase8_outputs",
]
