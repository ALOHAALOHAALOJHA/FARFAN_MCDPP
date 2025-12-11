"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00
Updated: 2025-12-09T00:00:00+00:00

Chain Layer (@chain) Evaluator - COHORT Export

Production implementation at: src/orchestration/chain_layer.py

Implements discrete scoring logic for method chain validation:
- 0.0: missing_required (hard mismatch: schema incompatible OR required input unavailable)
- 0.3: missing_critical (critical optional missing)
- 0.6: missing_optional AND many_missing (ratio>0.5) OR soft_schema_violation
- 0.8: all contracts pass AND warnings exist
- 1.0: all inputs present AND no warnings

Formula: Chain_quality = min(method_scores) [weakest link principle]
"""

from orchestration.chain_layer import (
    ChainLayerConfig,
    ChainLayerEvaluator,
    ChainValidationConfig,
    ChainValidationResult,
    MethodSignature,
    UpstreamOutputs,
    create_default_chain_config,
)

COHORT_METADATA = {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12",
    "layer_symbol": "@chain",
    "layer_name": "Chain Layer",
    "production_path": "src.orchestration.chain_layer",
    "implementation_status": "complete",
    "lines_of_code": 242,
    "formula": "Chain_quality = min(method_scores) [weakest link principle]",
    "components": {
        "signature_validation": "Method signature compatibility check",
        "upstream_validation": "Upstream output availability verification",
        "type_checking": "Input/output type compatibility validation",
        "quality_scoring": "Discrete scoring based on validation results"
    },
    "discrete_scores": {
        "missing_required": 0.0,
        "missing_critical": 0.3,
        "missing_optional": 0.6,
        "warnings": 0.8,
        "perfect": 1.0
    },
    "thresholds": {
        "many_missing_ratio": 0.5,
        "min_available_ratio": 0.0
    },
    "validation_modes": {
        "strict_mode": "Enforces all validation rules strictly",
        "allow_missing_optional": "Permits missing optional inputs without penalty",
        "penalize_warnings": "Reduces score when warnings are present"
    },
    "aggregation_strategy": "weakest_link",
    "aggregation_description": "Chain quality equals minimum score across all methods in sequence"
}


def get_cohort_metadata() -> dict[str, object]:
    """Return COHORT metadata for this layer."""
    return COHORT_METADATA.copy()


__all__ = [
    "COHORT_METADATA",
    "ChainLayerConfig",
    "ChainLayerEvaluator",
    "ChainValidationConfig",
    "ChainValidationResult",
    "MethodSignature",
    "UpstreamOutputs",
    "create_default_chain_config",
    "get_cohort_metadata",
]
