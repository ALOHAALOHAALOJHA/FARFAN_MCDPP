"""
Phase 2 JSON Schema Specifications

This package contains JSON Schema specifications for Phase 2 (Micro-Question Execution Layer)
of the F.A.R.F.A.N Mechanistic Policy Pipeline.

Schema Version: 1.0.0
Effective Date: 2025-12-18
JSON Schema Draft: 2020-12

Available Schemas:
    - executor_config: Configuration schema for Phase 2 executors
    - executor_output: Output schema for executor execution results
    - synchronization_manifest: SISAS synchronization manifest schema
    - calibration_policy: Calibration policy for executor behavior tuning

Usage:
    from farfan_pipeline.phases.Phase_two.schemas.validator import (
        validate_executor_config,
        validate_executor_output,
        validate_synchronization_manifest,
        validate_calibration_policy,
    )
    
    # Validate data
    config_data = {...}
    validate_executor_config(config_data)

See README.md for detailed documentation.
"""

__version__ = '1.0.0'
__schema_draft__ = '2020-12'
__effective_date__ = '2025-12-18'

from .validator import (
    load_schema,
    validate_json,
    validate_executor_config,
    validate_executor_output,
    validate_synchronization_manifest,
    validate_calibration_policy,
    validate_file,
)

__all__ = [
    'load_schema',
    'validate_json',
    'validate_executor_config',
    'validate_executor_output',
    'validate_synchronization_manifest',
    'validate_calibration_policy',
    'validate_file',
]
