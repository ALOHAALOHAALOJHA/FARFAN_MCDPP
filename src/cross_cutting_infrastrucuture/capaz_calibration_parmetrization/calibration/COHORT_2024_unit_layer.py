"""
COHORT_2024 - REFACTOR_WAVE_2024_12
Created: 2024-12-15T00:00:00+00:00
Updated: 2025-12-09T00:00:00+00:00

Unit Layer (@u) Evaluator - COHORT Export

Production implementation at: src/orchestration/unit_layer.py

Implements PDT (Plan de Desarrollo Territorial) structure analysis with:
- S (Structural Compliance): 0.5·B_cov + 0.25·H + 0.25·O
- M (Mandatory Sections): Critical sections with 2.0x weights
- I (Indicator Quality): Gate-controlled with 0.4·struct + 0.35·link + 0.25·logic
- P (PPI Completeness): Gate-controlled with 0.3·presence + 0.4·struct + 0.3·consistency
- Anti-gaming penalty: Detects boilerplate and structural manipulation

Formula: U = geometric_mean(S, M, gated(I), gated(P)) × (1 - penalty)
"""

from src.orchestration.unit_layer import (
    UnitLayerConfig,
    UnitLayerEvaluator,
    UnitLayerResult,
    StructuralCompliance,
    MandatorySections,
    IndicatorQuality,
    PPICompleteness,
    create_default_config,
)

# COHORT Metadata
COHORT_METADATA = {
    "cohort_id": "COHORT_2024",
    "creation_date": "2024-12-15T00:00:00+00:00",
    "wave_version": "REFACTOR_WAVE_2024_12",
    "layer_symbol": "@u",
    "layer_name": "Unit Layer",
    "production_path": "src.orchestration.unit_layer",
    "implementation_status": "complete",
    "lines_of_code": 490,
    "formula": "U = geometric_mean(S, M, gated(I), gated(P)) × (1 - anti_gaming_penalty)",
    "components": {
        "S": "Structural Compliance",
        "M": "Mandatory Sections",
        "I": "Indicator Quality (gated)",
        "P": "PPI Completeness (gated)"
    },
    "weights": {
        "S": {"B_cov": 0.5, "H": 0.25, "O": 0.25},
        "M": {"diagnostico": 2.0, "estrategica": 2.0, "ppi": 2.0, "seguimiento": 1.0},
        "I": {"struct": 0.4, "link": 0.35, "logic": 0.25},
        "P": {"presence": 0.3, "struct": 0.4, "consistency": 0.3}
    }
}


def get_cohort_metadata() -> dict:
    """Return COHORT metadata for this layer."""
    return COHORT_METADATA.copy()


__all__ = [
    # Production exports
    "UnitLayerConfig",
    "UnitLayerEvaluator",
    "UnitLayerResult",
    "StructuralCompliance",
    "MandatorySections",
    "IndicatorQuality",
    "PPICompleteness",
    "create_default_config",
    # COHORT metadata
    "COHORT_METADATA",
    "get_cohort_metadata",
]
