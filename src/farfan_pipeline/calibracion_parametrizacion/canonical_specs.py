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
import re

# ============================================================================
# POLICY AREAS - Canonical 10 Areas (PA01-PA10)
# Source: questionnaire_monolith.json extracted 2024-11
# Traceable to: Colombian PDT/PDM official structure
# ============================================================================

CANON_POLICY_AREAS: Final[dict[str, str]] = {
    "PA01": "Derechos de las mujeres e igualdad de género",
    "PA02": "Prevención de la violencia y protección de la población frente al conflicto armado y la violencia generada por grupos delincuenciales organizados, asociada a economías ilegales",
    "PA03": "Ambiente sano, cambio climático, prevención y atención a desastres",
    "PA04": "Derechos económicos, sociales y culturales",
    "PA05": "Derechos de las víctimas y construcción de paz",
    "PA06": "Derecho al buen futuro de la niñez, adolescencia, juventud y entornos protectores",
    "PA07": "Tierras y territorios",
    "PA08": "Líderes y lideresas, defensores y defensoras de derechos humanos, comunitarios, sociales, ambientales, de la tierra, el territorio y de la naturaleza",
    "PA09": "Crisis de derechos de personas privadas de la libertad",
    "PA10": "Migración transfronteriza",
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
    "good": 1.0 - MICRO_LEVELS["BUENO"],           # 0.30
    "acceptable": 1.0 - MICRO_LEVELS["ACEPTABLE"],  # 0.45
}

# Quality gates for thresholds
assert MICRO_LEVELS["EXCELENTE"] > MICRO_LEVELS["BUENO"], "Monotonicity: EXCELENTE > BUENO"
assert MICRO_LEVELS["BUENO"] > MICRO_LEVELS["ACEPTABLE"], "Monotonicity: BUENO > ACEPTABLE"
assert MICRO_LEVELS["ACEPTABLE"] > MICRO_LEVELS["INSUFICIENTE"], "Monotonicity: ACEPTABLE > INSUFICIENTE"

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
    "beta": 4.0,    # Slope - controls sensitivity to score changes
}

# Domain weights for evidence triangulation
# Source: derek_beach.py CDAFFramework (lines 6581-6586)
# Normalized to sum to 1.0
CDAF_DOMAIN_WEIGHTS: Final[dict[str, float]] = {
    "semantic": 0.35,    # Text analysis weight
    "temporal": 0.25,    # Time-series weight
    "financial": 0.25,   # Budget/finance weight
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
    "straw": (2.0, 4.0),      # Weak necessity, weak sufficiency
    "hoop": (8.0, 12.0),      # Strong necessity, weak sufficiency
    "smoking": (8.0, 12.0),   # Weak necessity, strong sufficiency
    "doubly": (20.0, 30.0),   # Strong necessity, strong sufficiency
}

# ============================================================================
# PDT/PDM STRUCTURE - Unit of Analysis Delimiters
# Source: reporte_unit_of_analysis (Colombian planning documents)
# These regex patterns define document structure for segmentation
# ============================================================================

# Chapter/section delimiters (markdown-style or numbered)
PDT_SECTION_PATTERNS: Final[list[str]] = [
    r"^#{1,3}\s+",                           # Markdown headers (# ## ###)
    r"^\d+\.\s+[A-ZÑÁÉÍÓÚ]",                # Numbered sections (1. SECTION)
    r"^[IVX]+\.\s+[A-ZÑÁÉÍÓÚ]",            # Roman numerals (I. SECTION)
    r"^(CAPÍTULO|SECCIÓN|TÍTULO)\s+\d+",   # Explicit labels
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
    r"PPI[\s-]?\d+",          # Investment projects
    r"BPIN[\s-]?\d+",         # National investment bank code
    r"\$\s*[\d,\.]+",         # Currency amounts
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
assert list(CAUSAL_CHAIN_ORDER.values()) == list(range(len(CAUSAL_CHAIN_ORDER))), \
    "Causal chain order must be sequential starting from 0"

# ==========================================================================
# PDT/PDM PATTERN SUITE - Precompiled Regexes
# Source: Consolidated from policy_processor.py and derek_beach.py
# Provides section, strategic, financial, and coding markers for PDM/PDT docs
# ==========================================================================

def _compile_union(patterns: list[str], flags: int = 0) -> re.Pattern[str]:
    joined = "|".join(f"(?:{p})" for p in patterns)
    return re.compile(joined, flags)


SECTION_DELIMITERS_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^(?:"
    r"CAP[IÍ]TULO\s+[IVX\d]+(?:\.|:)?\s*[A-ZÁÉÍÓÚÑ]|"
    r"T[ÍI]TULO\s+[IVX\d]+(?:\.|:)?\s*[A-ZÁÉÍÓÚÑ]|"
    r"PARTE\s+[IVX\d]+(?:\.|:)?\s*[A-ZÁÉÍÓÚÑ]|"
    r"L[ÍI]NEA\s+ESTRAT[ÉE]GICA\s*[IVX\d]*(?:\.|:)?|"
    r"EJE\s+[IVX\d]+(?:\.|:)?|"
    r"SECTOR:\s*[\w\s]+|"
    r"PROGRAMA:\s*[\w\s]+|"
    r"\#{3,5}\s*\d+\.\d+|"
    r"\d+\.\d+\.?\s+[A-ZÁÉÍÓÚÑ]|"
    r"\d+\.\s+[A-ZÁÉÍÓÚÑ]"
    r")",
    re.MULTILINE | re.IGNORECASE,
)

PRODUCT_CODES_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:"
    r"\b\d{7}\b|"
    r"C[oó]d\.\s*(?:Producto|Programa|Indicador):\s*[\w\-]+|"
    r"BPIN\s*:\s*\d{10,13}|"
    r"C[oó]digo\s+(?:MGA|de\s+Producto):\s*\d+|"
    r"\b[MP][RIP]-\d{3}\b"
    r")",
    re.IGNORECASE,
)

META_INDICATORS_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:Meta\s+(?:de\s+)?(?:producto|resultado|bienestar):\s*[\d\.,]+|"
    r"Indicador\s+(?:de\s+)?(?:producto|resultado|impacto):\s*[^\. ]+)",
    re.IGNORECASE,
)

INDICATOR_MATRIX_HEADERS_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:"
    r"L[íi]nea\s+Estrat[ée]gica|"
    r"C[oó]d\.\s*Programa|"
    r"C[oó]d\.\s*Producto|"
    r"C[oó]d\.\s*indicador|"
    r"Programas\s+presupuestales|"
    r"Indicadores?\s+(?:de\s+)?producto|"
    r"Indicadores?\s+(?:de\s+)?resultado|"
    r"Unidad\s+de\s+medida|"
    r"L[íi]nea\s+base|"
    r"Año\s+l[íi]nea\s+base|"
    r"Meta\s+(?:Total\s+)?(?:Cuatrienio|202[4-7])|"
    r"Meta\s+de\s+(?:Producto|Resultado|Bienestar)|"
    r"Fuente\s+de\s+informaci[óo]n|"
    r"Metas\s+de\s+producto"
    r")",
    re.IGNORECASE,
)

PPI_HEADERS_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:"
    r"TOTAL\s+202[4-7]|"
    r"Costo\s+Total\s+Cuatrienio|"
    r"Valor\s+total\s+inversi[óo]n|"
    r"Vigencia\s+202[4-7]|"
    r"SGP|Sistema\s+General\s+de\s+Participaciones|"
    r"SGR|Sistema\s+General\s+de\s+Regal[ií]as|"
    r"Regal[ií]as|"
    r"Recursos\s+Propios|"
    r"Otras\s+Fuentes|"
    r"Fondo\s+subregional|"
    r"Cooperaci[óo]n\s+internacional|"
    r"Gesti[óo]n\s+e\s+inversi[óo]n|"
    r"Plan\s+Plurianual\s+de\s+Inversiones|"
    r"PPI|POAI"
    r")",
    re.IGNORECASE,
)

# Extended semantic markers (imported from derek_beach and policy_processor)
CAUSAL_CONNECTORS_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:"
    r"con\s+el\s+fin\s+de|a\s+tr[aá]ves\s+de|mediante|para\s+lograr|"
    r"con\s+el\s+prop[óo]sito\s+de|con\s+el\s+objetivo\s+de|"
    r"contribuye\s+al\s+logro|cierre\s+de\s+brechas|permite|"
    r"genera|produce|resulta\s+en|"
    r"gracias\s+a|como\s+resultado\s+de|debido\s+a|porque|"
    r"por\s+medio\s+de|permitir[áa]|contribuir[áa]\s+a|"
    r"implementar|realizar|desarrollar|adelantar|ejecutar|"
    r"contempla\s+actividades|"
    r"transformaci[óo]n|desarrollo|mejora|cambio|efecto|impacto"
    r")",
    re.IGNORECASE,
)

DIAGNOSTIC_MARKERS_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:"
    r"diagn[óo]stico|caracterizaci[óo]n|an[aá]lisis\s+situacional|"
    r"l[íi]nea\s+base|a[ñn]o\s+base|situaci[óo]n\s+inicial|"
    r"brecha|d[eé]ficit|rezago|carencia|limitaci[óo]n|"
    r"problem[aá]tica|necesidad|"
    r"Ejes\s+problem[aá]ticos|Problem[aá]ticas\s+priorizadas|"
    r"brechas\s+territoriales|"
    r"ausencia\s+de|falta\s+de|desactualizado"
    r")",
    re.IGNORECASE,
)

LEGAL_REFERENCES_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:"
    r"Ley\s+\d+\s+de\s+\d{4}|"
    r"DECRETO\s+\d+\s+DE\s+\d{4}|"
    r"Resoluci[óo]n\s+\d+\s+de\s+\d{4}|"
    r"Acuerdo\s+(?:Municipal\s+)?(?:No\s+)?\d+\s+de\s+\d{4}|"
    r"Constituci[óo]n\s+Pol[íi]tica|"
    r"Art\.\s*\d+|Art[íi]culo\s+\d+|"
    r"Circular\s+conjunta\s+[\d\-]+|"
    r"Estatuto\s+Org[aá]nico"
    r")",
    re.IGNORECASE,
)

TEMPORAL_EXPRESSIONS_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:"
    r"cuatrienio|202[4-7]|vigencia\s+202[4-7]|"
    r"per[ií]odo\s+de\s+cuatro\s+a[ñn]os|"
    r"corto\s+plazo|mediano\s+plazo|largo\s+plazo|"
    r"\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)|"
    r"\d{2}-\d{2}-\d{4}|"
    r"Marco\s+Fiscal\s+de\s+Mediano\s+Plazo|MFMP|"
    r"POAI|Plan\s+Operativo\s+Anual|"
    r"a[ñn]o\s+fiscal|"
    r"serie\s+hist[óo]rica|evoluci[óo]n\s+20\d{2}-20\d{2}|"
    r"tendencia\s+de\s+los\s+[uú]ltimos|"
    r"vigencia\s+anterior|cuatrienio\s+anterior"
    r")",
    re.IGNORECASE,
)

TERRITORIAL_REFERENCES_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:"
    r"Municipio\s+de\s+[\w\s]+|"
    r"Departamento\s+del\s+Cauca|Gobernaci[óo]n\s+de\s+Cauca|"
    r"territorio|urbano|rural|"
    r"cabecera\s+(?:urbana|municipal)|"
    r"corregimiento|vereda|"
    r"centro\s+poblado|"
    r"regi[óo]n\s+(?:Norte|Sur|Centro)\s+del\s+Cauca|"
    r"Alto\s+Pat[ií]a|"
    r"subregi[óo]n|"
    r"PDET|Programas\s+de\s+Desarrollo\s+con\s+Enfoque\s+Territorial|"
    r"zonas?\s+PDET|"
    r"municipios\s+m[aá]s\s+afectados\s+por\s+el\s+conflicto|"
    r"Consejo\s+Comunitario|"
    r"resguardo\s+ind[ií]gena|"
    r"territorios?\s+(?:[éet]tnicos?|colectivos?)"
    r")",
    re.IGNORECASE,
)

PDT_PATTERNS: Final[dict[str, re.Pattern[str]]] = {
    "section_delimiters": SECTION_DELIMITERS_PATTERN,
    "strategic_markers": _compile_union(
        PDT_STRATEGIC_PATTERNS + [
            r"Parte\s+Estrat[ée]gica|Componente\s+estrat[ée]gico|"
            r"objetivos?|metas?|indicadores?|"
            r"apuestas|priorizaci[óo]n|"
            r"definici[óo]n\s+de\s+los\s+objetivos|"
            r"alternativas\s+de\s+soluci[óo]n|"
            r"se\s+abordar[aá]n\s+en\s+el\s+presente\s+cuatrienio|"
            r"grandes\s+apuestas"
        ],
        re.IGNORECASE,
    ),
    "financial_markers": _compile_union(PDT_FINANCIAL_PATTERNS, re.IGNORECASE),
    "product_codes": PRODUCT_CODES_PATTERN,
    "meta_indicators": META_INDICATORS_PATTERN,
    "indicator_matrix_headers": INDICATOR_MATRIX_HEADERS_PATTERN,
    "ppi_headers": PPI_HEADERS_PATTERN,
    "causal_connectors": CAUSAL_CONNECTORS_PATTERN,
    "diagnostic_markers": DIAGNOSTIC_MARKERS_PATTERN,
    "legal_references": LEGAL_REFERENCES_PATTERN,
    "temporal_expressions": TEMPORAL_EXPRESSIONS_PATTERN,
    "territorial_references": TERRITORIAL_REFERENCES_PATTERN,
}

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
        MICRO_LEVELS["EXCELENTE"] > MICRO_LEVELS["BUENO"] > 
        MICRO_LEVELS["ACEPTABLE"] > MICRO_LEVELS["INSUFICIENTE"]
    )
    
    # Derived values
    checks["alignment_threshold"] = abs(ALIGNMENT_THRESHOLD - 0.625) < 1e-9
    checks["total_questions"] = TOTAL_BASE_QUESTIONS == 30
    
    # Domain weights
    checks["domain_weights_sum"] = abs(sum(CDAF_DOMAIN_WEIGHTS.values()) - 1.0) < 1e-9
    
    # Causal chain
    checks["causal_chain_sequential"] = (
        list(CAUSAL_CHAIN_ORDER.values()) == list(range(len(CAUSAL_CHAIN_ORDER)))
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
    "PDT_PATTERNS",
    "CAUSAL_CHAIN_VOCABULARY",
    "CAUSAL_CHAIN_ORDER",
    "BASE_QUESTIONS_PER_DIMENSION",
    "TOTAL_BASE_QUESTIONS",
    "validate_canonical_specs",
]
