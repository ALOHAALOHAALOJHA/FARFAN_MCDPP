"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00
Updated: 2025-12-09T00:00:00+00:00

Meta Layer (@m) Evaluator - COHORT Export

Production implementation at: src/orchestration/meta_layer.py

Implements meta-level calibration evaluation with:
- m_transparency: Formula export, trace completeness, log conformance (discrete: 0.0/0.4/0.7/1.0)
- m_governance: Version tags, config hash, signature validation (discrete: 0.0/0.33/0.66/1.0)
- m_cost: Execution time and memory usage thresholds (discrete: 0.0/0.5/0.8/1.0)

Formula: M = 0.5·m_transparency + 0.4·m_governance + 0.1·m_cost
"""

from orchestration.meta_layer import (
    CostMetrics,
    CostThresholds,
    GovernanceArtifacts,
    GovernanceRequirements,
    MetaLayerConfig,
    MetaLayerEvaluator,
    TransparencyArtifacts,
    TransparencyRequirements,
    compute_config_hash,
    create_default_config,
)

COHORT_METADATA = {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12",
    "layer_symbol": "@m",
    "layer_name": "Meta Layer",
    "production_path": "src.orchestration.meta_layer",
    "implementation_status": "complete",
    "lines_of_code": 267,
    "formula": "M = 0.5·m_transparency + 0.4·m_governance + 0.1·m_cost",
    "components": {
        "m_transparency": "Transparency artifacts validation (formula, trace, logs)",
        "m_governance": "Governance requirements validation (version, hash, signature)",
        "m_cost": "Resource consumption metrics (time, memory)"
    },
    "weights": {
        "w_transparency": 0.5,
        "w_governance": 0.4,
        "w_cost": 0.1
    },
    "discrete_scores": {
        "transparency": {
            "all_present": 1.0,
            "two_present": 0.7,
            "one_present": 0.4,
            "none_present": 0.0
        },
        "governance": {
            "all_present": 1.0,
            "two_present": 0.66,
            "one_present": 0.33,
            "none_present": 0.0
        },
        "cost": {
            "fast_low_memory": 1.0,
            "acceptable_normal_memory": 0.8,
            "slow_or_high_memory": 0.5,
            "invalid": 0.0
        }
    },
    "thresholds": {
        "cost_threshold_fast": 1.0,
        "cost_threshold_acceptable": 5.0,
        "cost_threshold_memory_normal": 512.0
    },
    "transparency_requirements": {
        "formula_export": "Symbolic formula representation with Choquet/Cal/x_ terms",
        "trace_complete": "Execution trace with step/phase/method markers",
        "logs_conform": "Structured logs conforming to required schema"
    },
    "governance_requirements": {
        "version_tag": "Valid semantic version tag (not 1.0, 0.0.0, or unknown)",
        "config_hash": "64-character hex SHA256 hash of configuration",
        "signature": "Optional 32+ character cryptographic signature"
    },
    "validation_logic": {
        "formula_min_length": 10,
        "formula_required_terms": ["Choquet", "Cal(I)", "x_"],
        "trace_min_length": 20,
        "trace_required_markers": ["step", "phase", "method"],
        "config_hash_length": 64,
        "signature_min_length": 32
    }
}


def get_cohort_metadata() -> dict[str, object]:
    """Return COHORT metadata for this layer."""
    return COHORT_METADATA.copy()


__all__ = [
    "COHORT_METADATA",
    "CostMetrics",
    "CostThresholds",
    "GovernanceArtifacts",
    "GovernanceRequirements",
    "MetaLayerConfig",
    "MetaLayerEvaluator",
    "TransparencyArtifacts",
    "TransparencyRequirements",
    "compute_config_hash",
    "create_default_config",
    "get_cohort_metadata",
]
