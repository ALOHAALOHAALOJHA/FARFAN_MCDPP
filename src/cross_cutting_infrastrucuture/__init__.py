"""
Cross-Cutting Infrastructure
=============================

This package contains cross-cutting infrastructure components used across
all phases of the F.A.R.F.A.N pipeline:

- SISAS: Signal Intelligence System for Advanced Structuring
- CAPAZ: Calibration and Parametrization System
- Dura Lex: Contract enforcement and runtime validation
- Environment configuration
- Clock and timing utilities
- Log adapters
"""

__all__ = [
    "irrigation_using_signals",
    "capaz_calibration_parmetrization",
    "contractual",
    "environment",
    "clock",
    "log_adapters",
]
