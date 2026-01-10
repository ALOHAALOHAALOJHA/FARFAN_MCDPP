"""Canonical Specifications - Single Source of Truth for FARFAN Constants.

This module contains all canonical constants extracted from:
- questionnaire_monolith.json (EXTRACTED, not runtime loaded)
- GUIA_ARQUEOLOGIA_INVERSA_REFACTORIZACION.md
- reporte_unit_of_analysis (PDT/PDM structure)
- DEREK_BEACH methodology

NO RUNTIME JSON LOADING. All constants are frozen at module import time.
All derived values use explicit formulas with provenance.

Architecture Decision Record (ADR):
- No CalibrationOrchestrator - constants are injected, not centrally dispatched
- No runtime questionnaire dependency
- Single source of truth for policy areas, thresholds, levels
- Deterministic, traceable, auditable
"""

from __future__ import annotations

from typing import Final

# ============================================================================
# POLICY AREAS - Canonical 10 Areas (PA01-PA10)
# Source: questionnaire_monolith.json extracted 2024-11
# Traceable to: Colombian PDT/PDM official structure
# ============================================================================

CANON_POLICY_AREAS: Final[dict[str, str]] = {
    "PA01": "Educación",
    "PA02": "Salud",
    "PA03": "Vivienda y Servicios Públicos",
    "PA04": "Empleo y Desarrollo Económico",
    "PA05": "Infraestructura Vial y Transporte",
    "PA06": "Cultura, Deporte y Recreación",
    "PA07": "Medio Ambiente y Gestión del Riesgo",
    "PA08": "Justicia, Seguridad y Convivencia",
    "PA09": "Fortalecimiento Institucional",
    "PA10": "Grupos Poblacionales y Equidad",
}

# Validation: Exactly 10 policy areas as per FARFAN structure
assert len(CANON_POLICY_AREAS) == 10, "Must have exactly 10 policy areas"
assert all(k.startswith("PA") for k in CANON_POLICY_AREAS), "All keys must be PA##"

# ============================================================================
# MICRO LEVELS - Calibration Thresholds
# Source: derek_beach.py MICRO_LEVELS (lines 97-102)
# Used by: DEREK_BEACH methods, CDAFFramework, BayesianMechanismInference
# Traceable to: Beach's evidential quality standards
# ============================================================================

MICRO_LEVELS: Final[dict[str, float]] = {
    "EXCELENTE": 0.85,
    "BUENO": 0.70,
    "ACEPTABLE": 0.55,
    "INSUFICIENTE": 0.00,
}

# Derived threshold - explicit formula with provenance
# Formula: (ACEPTABLE + BUENO) / 2
# Rationale: Midpoint between acceptable and good quality
ALIGNMENT_THRESHOLD: Final[float] = (MICRO_LEVELS["ACEPTABLE"] + MICRO_LEVELS["BUENO"]) / 2
assert ALIGNMENT_THRESHOLD == 0.625, "Alignment threshold must be 0.625"

# Risk thresholds - derived from complement of quality levels
# Formula: 1 - quality_level
# Rationale: Risk is inverse of quality
RISK_THRESHOLDS: Final[dict[str, float]] = {
    "excellent": 1.0 - MICRO_LEVELS["EXCELENTE"],  # 0.15
    "good": 1.0 - MICRO_LEVELS["BUENO"],  # 0.30
    "acceptable": 1.0 - MICRO_LEVELS["ACEPTABLE"],  # 0.45
}

# Quality gates for thresholds
assert MICRO_LEVELS["EXCELENTE"] > MICRO_LEVELS["BUENO"], "Monotonicity: EXCELENTE > BUENO"
assert MICRO_LEVELS["BUENO"] > MICRO_LEVELS["ACEPTABLE"], "Monotonicity: BUENO > ACEPTABLE"
assert (
    MICRO_LEVELS["ACEPTABLE"] > MICRO_LEVELS["INSUFICIENTE"]
), "Monotonicity: ACEPTABLE > INSUFICIENTE"

# ============================================================================
# DIMENSIONS - 6 Canonical Dimensions (DIM01-DIM06)
# Source: questionnaire_monolith.json extracted 2024-11
# Each dimension has 5 questions (Q1-Q5) -> 30 base questions total
# ============================================================================

CANON_DIMENSIONS: Final[dict[str, str]] = {
    "DIM01": "Diagnóstico y Planeación Estratégica",
    "DIM02": "Articulación y Coherencia Programática",
    "DIM03": "Capacidad Institucional y Gestión",
    "DIM04": "Recursos y Sostenibilidad Financiera",
    "DIM05": "Seguimiento, Evaluación y Rendición de Cuentas",
    "DIM06": "Participación y Enfoque Territorial",
}

# Validation: Exactly 6 dimensions as per FARFAN structure
assert len(CANON_DIMENSIONS) == 6, "Must have exactly 6 dimensions"
assert all(k.startswith("DIM") for k in CANON_DIMENSIONS), "All keys must be DIM##"

# Derived: Base slots (30 total: D1-Q1 through D6-Q5)
# Formula: Each dimension × 5 questions = 30 base questions
BASE_QUESTIONS_PER_DIMENSION: Final[int] = 5
TOTAL_BASE_QUESTIONS: Final[int] = len(CANON_DIMENSIONS) * BASE_QUESTIONS_PER_DIMENSION
assert TOTAL_BASE_QUESTIONS == 30, "Must have exactly 30 base questions"

# ============================================================================
# SCORING MODALITIES - Type A vs Type B
# Source: questionnaire_monolith.json extracted 2024-11
# Type A: count_and_scale (discrete criteria)
# Type B: qualitative_judgment (expert assessment)
# ============================================================================

SCORING_MODALITIES: Final[dict[str, str]] = {
    "TYPE_A": "count_and_scale",
    "TYPE_B": "qualitative_judgment",
}

# ============================================================================
# CDAF FRAMEWORK - Calibration Parameters
# Source: derek_beach.py CDAFFramework.__init__ (lines 6570-6578)
# Logit transformation: p = 1/(1+exp(-(α+β·score)))
# ============================================================================

CDAF_CALIBRATION_PARAMS: Final[dict[str, float]] = {
    "alpha": -2.0,  # Intercept - shifts baseline probability
    "beta": 4.0,  # Slope - controls sensitivity to score changes
}

# Domain weights for evidence triangulation
# Source: derek_beach.py CDAFFramework (lines 6581-6586)
# Normalized to sum to 1.0
CDAF_DOMAIN_WEIGHTS: Final[dict[str, float]] = {
    "semantic": 0.35,  # Text analysis weight
    "temporal": 0.25,  # Time-series weight
    "financial": 0.25,  # Budget/finance weight
    "structural": 0.15,  # Organizational weight
}

# Quality gate: Domain weights sum to 1.0
assert abs(sum(CDAF_DOMAIN_WEIGHTS.values()) - 1.0) < 1e-9, "Domain weights must sum to 1.0"

# Triangulation bonus threshold
# Source: derek_beach.py calculate_likelihood_adaptativo (line 6630)
TRIANGULATION_ACTIVE_DOMAINS_THRESHOLD: Final[int] = 3
TRIANGULATION_BONUS: Final[float] = 0.05

# ============================================================================
# BAYES FACTORS - Evidential Test Strength
# Source: derek_beach.py BayesFactorTable (Beach & Pedersen typology)
# ============================================================================

BAYES_FACTORS: Final[dict[str, tuple[float, float]]] = {
    "straw": (2.0, 4.0),  # Weak necessity, weak sufficiency
    "hoop": (8.0, 12.0),  # Strong necessity, weak sufficiency
    "smoking": (8.0, 12.0),  # Weak necessity, strong sufficiency
    "doubly": (20.0, 30.0),  # Strong necessity, strong sufficiency
}

# ============================================================================
# PDT/PDM STRUCTURE - Unit of Analysis Delimiters
# Source: reporte_unit_of_analysis (Colombian planning documents)
# These regex patterns define document structure for segmentation
# ============================================================================

# Chapter/section delimiters (markdown-style or numbered)
PDT_SECTION_PATTERNS: Final[list[str]] = [
    r"^#{1,3}\s+",  # Markdown headers (# ## ###)
    r"^\d+\.\s+[A-ZÑÁÉÍÓÚ]",  # Numbered sections (1. SECTION)
    r"^[IVX]+\.\s+[A-ZÑÁÉÍÓÚ]",  # Roman numerals (I. SECTION)
    r"^(CAPÍTULO|SECCIÓN|TÍTULO)\s+\d+",  # Explicit labels
]

# Strategic line indicators
PDT_STRATEGIC_PATTERNS: Final[list[str]] = [
    r"l[íi]nea\s+estrat[ée]gica",
    r"eje\s+estrat[ée]gico",
    r"programa\s+\d+",
    r"objetivo\s+estrat[ée]gico",
]

# Financial/program identifiers
PDT_FINANCIAL_PATTERNS: Final[list[str]] = [
    r"PPI[\s-]?\d+",  # Investment projects
    r"BPIN[\s-]?\d+",  # National investment bank code
    r"\$\s*[\d,\.]+",  # Currency amounts
    r"presupuesto",
    r"costo",
    r"inversi[óo]n",
]

# Causal chain vocabulary (for semantic distance calculations)
CAUSAL_CHAIN_VOCABULARY: Final[list[str]] = [
    "insumos",
    "actividades",
    "productos",
    "resultados",
    "efectos",
    "impactos",
]

# Causal chain ordinal positions (for distance calculations)
# Source: derek_beach.py (lines 5115-5121)
CAUSAL_CHAIN_ORDER: Final[dict[str, int]] = {
    "insumos": 0,
    "actividades": 1,
    "productos": 2,
    "resultados": 3,
    "efectos": 4,
    "impactos": 5,
}

# Quality gate: Order is sequential
assert list(CAUSAL_CHAIN_ORDER.values()) == list(
    range(len(CAUSAL_CHAIN_ORDER))
), "Causal chain order must be sequential starting from 0"

# ============================================================================
# VALIDATION RULES - Quality Gates
# These ensure constants maintain expected properties
# ============================================================================


def validate_canonical_specs() -> dict[str, bool]:
    """Run quality gates on all canonical specifications.

    Returns:
        dict mapping check name to pass/fail status
    """
    checks: dict[str, bool] = {}

    # Policy areas
    checks["policy_areas_count"] = len(CANON_POLICY_AREAS) == 10
    checks["policy_areas_format"] = all(k.startswith("PA") for k in CANON_POLICY_AREAS)

    # Dimensions
    checks["dimensions_count"] = len(CANON_DIMENSIONS) == 6
    checks["dimensions_format"] = all(k.startswith("DIM") for k in CANON_DIMENSIONS)

    # Micro levels monotonicity
    checks["micro_levels_monotonic"] = (
        MICRO_LEVELS["EXCELENTE"]
        > MICRO_LEVELS["BUENO"]
        > MICRO_LEVELS["ACEPTABLE"]
        > MICRO_LEVELS["INSUFICIENTE"]
    )

    # Derived values
    checks["alignment_threshold"] = abs(ALIGNMENT_THRESHOLD - 0.625) < 1e-9
    checks["total_questions"] = TOTAL_BASE_QUESTIONS == 30

    # Domain weights
    checks["domain_weights_sum"] = abs(sum(CDAF_DOMAIN_WEIGHTS.values()) - 1.0) < 1e-9

    # Causal chain
    checks["causal_chain_sequential"] = list(CAUSAL_CHAIN_ORDER.values()) == list(
        range(len(CAUSAL_CHAIN_ORDER))
    )

    return checks


# Run validation at module import
_validation_results = validate_canonical_specs()
if not all(_validation_results.values()):
    failed_checks = [k for k, v in _validation_results.items() if not v]
    raise RuntimeError(f"Canonical specs validation failed: {failed_checks}")


# ============================================================================
# USAGE PATTERNS
# ============================================================================

# Example 1: Import calibration levels
# from farfan_pipeline.core.canonical_specs import MICRO_LEVELS
# threshold = MICRO_LEVELS["BUENO"]  # 0.70

# Example 2: Use policy areas
# from farfan_pipeline.core.canonical_specs import CANON_POLICY_AREAS
# for pa_id, pa_name in CANON_POLICY_AREAS.items():
#     print(f"{pa_id}: {pa_name}")

# Example 3: Use CDAF calibration
# from farfan_pipeline.core.canonical_specs import CDAF_CALIBRATION_PARAMS
# alpha, beta = CDAF_CALIBRATION_PARAMS["alpha"], CDAF_CALIBRATION_PARAMS["beta"]
# p_mechanism = 1.0 / (1.0 + exp(-(alpha + beta * score)))

__all__ = [
    "CANON_POLICY_AREAS",
    "CANON_DIMENSIONS",
    "MICRO_LEVELS",
    "ALIGNMENT_THRESHOLD",
    "RISK_THRESHOLDS",
    "SCORING_MODALITIES",
    "CDAF_CALIBRATION_PARAMS",
    "CDAF_DOMAIN_WEIGHTS",
    "TRIANGULATION_ACTIVE_DOMAINS_THRESHOLD",
    "TRIANGULATION_BONUS",
    "BAYES_FACTORS",
    "PDT_SECTION_PATTERNS",
    "PDT_STRATEGIC_PATTERNS",
    "PDT_FINANCIAL_PATTERNS",
    "CAUSAL_CHAIN_VOCABULARY",
    "CAUSAL_CHAIN_ORDER",
    "BASE_QUESTIONS_PER_DIMENSION",
    "TOTAL_BASE_QUESTIONS",
    "validate_canonical_specs",
]
