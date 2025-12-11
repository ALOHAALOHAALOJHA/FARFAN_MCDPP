"""
COHORT_2024 Calibration Inventories Package

Provides tooling for method inventory, signature extraction, and calibration
coverage analysis across the 8-layer calibration system.

Modules:
    scan_methods_inventory: Scans codebase for all methods
    method_signature_extractor: Extracts parametrization specifications
    calibration_coverage_validator: Generates coverage matrix
    consolidate_calibration_inventories: Main orchestrator

Usage:
    from system.config.calibration.inventories import consolidate_calibration_inventories
    
    # Or run from command line:
    python -m system.config.calibration.inventories.consolidate_calibration_inventories
"""

__version__ = "1.0.0"
__cohort__ = "COHORT_2024"
__wave__ = "REFACTOR_WAVE_2024_12"
