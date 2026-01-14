"""
Canonical Specifications
=========================
Single source of truth for canonical constants used across the pipeline.

Module: canonical_specs.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Canonical constants and specifications
Schema Version: 2.0.0

MIGRATION NOTE:
This module was previously located at calibracion_parametrizacion.canonical_specs
and has been migrated to the infrastructure.calibration layer as part of the
unified calibration regime architecture.

All constants are frozen at module import time for determinism and traceability.
No runtime JSON loading - all values are statically defined here.

ARCHITECTURE DECISION RECORD (ADR):
- Extract → Normalize → Freeze pattern
- Single source of truth for all calibration constants
- No runtime dependencies on questionnaire_monolith.json
- Immutable frozen constants for auditability
"""

from __future__ import annotations

import re
from typing import Final

# =============================================================================
# CANONICAL POLICY AREAS (PA01-PA10)
# =============================================================================

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

# =============================================================================
# CANONICAL DIMENSIONS (DIM01-DIM06)
# =============================================================================

CANON_DIMENSIONS: Final[dict[str, str]] = {
    "DIM01": "Diagnóstico y Planeación Estratégica",
    "DIM02": "Articulación y Coherencia Programática",
    "DIM03": "Capacidad Institucional y Gestión",
    "DIM04": "Recursos y Sostenibilidad Financiera",
    "DIM05": "Seguimiento, Evaluación y Rendición de Cuentas",
    "DIM06": "Participación y Enfoque Territorial",
}

# =============================================================================
# MICRO LEVELS (QUALITY THRESHOLDS)
# =============================================================================

MICRO_LEVELS: Final[dict[str, float]] = {
    "EXCELENTE": 0.85,      # Highest quality
    "BUENO": 0.70,          # Middle-high quality
    "ACEPTABLE": 0.55,      # Middle-low quality (minimum acceptable)
    "INSUFICIENTE": 0.00,   # Lowest quality (insufficient)
}

# =============================================================================
# DERIVED THRESHOLDS - CALCULATED FROM CANONICAL CONSTANTS
# =============================================================================

# Formula: (ACEPTABLE + BUENO) / 2
# Rationale: Midpoint between acceptable and good quality for confidence scoring
CONFIDENCE_THRESHOLD: Final[float] = (MICRO_LEVELS["ACEPTABLE"] + MICRO_LEVELS["BUENO"]) / 2.0  # 0.625

# Formula: ACEPTABLE threshold
# Rationale: Minimum acceptable coherence level
COHERENCE_THRESHOLD: Final[float] = MICRO_LEVELS["ACEPTABLE"]  # 0.55

# Formula: (ACEPTABLE + BUENO) / 2
# Rationale: Alignment scoring threshold (same as confidence)
ALIGNMENT_THRESHOLD: Final[float] = (MICRO_LEVELS["ACEPTABLE"] + MICRO_LEVELS["BUENO"]) / 2.0  # 0.625

# =============================================================================
# RISK THRESHOLDS (INVERSE QUALITY)
# =============================================================================

RISK_THRESHOLDS: Final[dict[str, float]] = {
    "excellent": 0.15,      # Low risk = high quality
    "good": 0.30,           # Moderate-low risk
    "acceptable": 0.50,     # Moderate risk
    "insufficient": 0.80,   # High risk = low quality
}

# =============================================================================
# CAUSAL CHAIN VOCABULARY
# =============================================================================
# Comprehensive vocabulary for causal chain analysis following MGA methodology:
# 1. INSUMOS (Input) - Initial resources mobilized
# 2. ACTIVIDADES (Process) - Processes and operations
# 3. PRODUCTOS (Output) - Goods and services delivered
# 4. RESULTADOS (Outcome) - Direct effects on target population
# 5. IMPACTOS (Impact) - Long-term attributable effects
# =============================================================================

CAUSAL_CHAIN_VOCABULARY: Final[list[str]] = [
    # ========================================================================
    # 1. INSUMOS (INPUT) - Recursos iniciales movilizados
    # ========================================================================
    # Financial Resources
    "recursos financieros",
    "fondos",
    "apropiaciones",
    "recursos propios",
    "recursos tributarios",
    "recursos no tributarios",
    "SGP",
    "Sistema General de Participaciones",
    "SGR",
    "Sistema General de Regalías",
    "asignaciones directas",
    "inversión local",
    "inversión regional",
    "cofinanciación",
    "cooperación",
    "crédito",
    "obras por impuestos",
    "Plan Plurianual de Inversiones",
    "PPI",
    "matriz de costeo",
    "ingresos proyectados",
    "Marco Fiscal de Mediano Plazo",
    "MFMP",
    # Human Resources
    "recursos humanos",
    "personal de planta",
    "personal técnico",
    "personal especializado",
    "personal capacitado",
    "talento humano",
    "MIPG",
    "estructura administrativa",
    "diagnóstico institucional",
    "requerimientos de personal",
    "capacidad institucional",
    # Material and Capital Resources
    "recursos materiales",
    "recursos de capital",
    "infraestructura existente",
    "equipos",
    "tecnología",
    "TIC",
    "sistemas de información",
    "terrenos",
    "inventario de equipamientos",
    "dotación",
    "infraestructura precaria",
    "necesidades de mejora",
    # ========================================================================
    # 2. ACTIVIDADES (PROCESS) - Procesos y operaciones
    # ========================================================================
    # Process Types
    "procesos",
    "operaciones",
    "actividades",
    "talleres",
    "foros",
    "jornadas",
    "implementación de estrategias",
    "seguimiento",
    "articulación interinstitucional",
    "coordinación",
    "diseño de rutas",
    "formulación de políticas",
    "reuniones",
    "mesas de diálogo",
    "estudios",
    # Action Verbs (specific to activities, not general connectors)
    "gestión de proyectos",
    "fortalecer",
    "apoyo",
    "asistencia",
    # Documentation
    "cronogramas",
    "fechas de inicio",
    "fechas de fin",
    "avance físico",
    "avance financiero",
    "reportes de supervisión",
    "desarrollo de procesos",
    "Plan Operativo Anual de Inversiones",
    "POAI",
    "Plan de Acción Institucional",
    "PAI",
    # ========================================================================
    # 3. PRODUCTOS (OUTPUT) - Bienes y servicios entregados
    # ========================================================================
    # Tangible Goods
    "bienes tangibles",
    "infraestructura construida",
    "hospitales construidos",
    "placa huella construida",
    "dotaciones entregadas",
    "ambientes de aprendizaje dotados",
    "bancos de maquinaria dotados",
    "equipamiento instalado",
    "viviendas construidas",
    "viviendas mejoradas",
    "hogares beneficiados",
    # Intangible Services/Products
    "servicios",
    "productos intangibles",
    "asistencia técnica brindada",
    "capacitaciones realizadas",
    "personas capacitadas",
    "documentos elaborados",
    "plan formulado",
    "casos atendidos",
    "personas asistidas",
    "lineamientos técnicos",
    # Measurement
    "Código MGA",
    "código de producto",
    "indicador de producto",
    "unidad de medida",
    "metas de producto",
    "número",
    "porcentaje",
    "matriz de metas",
    "componente estratégico",
    "Catálogo de Productos",
    # ========================================================================
    # 4. RESULTADOS (OUTCOME) - Efectos directos sobre población objetivo
    # ========================================================================
    # Social Improvements
    "mejoras en indicadores sociales",
    "tasa de cobertura incrementada",
    "reducción de la tasa de deserción",
    "reducción de la pobreza multidimensional",
    "IPM",
    "aumento de la percepción de seguridad",
    "reducción de la informalidad",
    "tasa de mortalidad infantil",
    "tasa bruta de natalidad",
    "valor agregado por actividades económicas",
    # Measurable Effects
    "efectos directos",
    "efectos inmediatos",
    "cierre de brechas sociales",
    "mejora en la calidad de vida",
    "mayor acceso a servicios",
    "población con acceso incrementado",
    "fortalecimiento del tejido social",
    # Indicators
    "indicador de resultado",
    "IR",
    "línea base",
    "meta",
    "meta cuatrienio",
    "matriz de indicadores de resultado",
    "cambios en percepción",
    "cambios en conocimiento",
    "cambios en condiciones de bienestar",
    # ========================================================================
    # 5. IMPACTOS - Efectos a largo plazo atribuibles
    # ========================================================================
    # Structural Transformation
    "transformación estructural",
    "consolidación de la paz estable y duradera",
    "superación de la pobreza",
    "desarrollo humano integral",
    "ruptura de ciclos de violencia",
    "equidad y justicia social",
    "justicia ambiental",
    "transformación del campo",
    # Strategic Alignment
    "alineación con marcos globales",
    "Objetivos de Desarrollo Sostenible",
    "ODS",
    "Acuerdo de Paz",
    "PDET",
    "Plan Nacional de Desarrollo",
    "PND",
    "Plan de Desarrollo Departamental",
    "PDD",
    "visión",
    "misión",
    "fundamentos conceptuales",
    "ejes estratégicos",
    "propósitos fundamentales",
    # Long-term Vision
    "efectos a largo plazo",
    "exclusivamente atribuibles",
    "desarrollo sostenible",
    "paz territorial",
    "potencial transformador",
    "visión de largo plazo",
    "cambio significativo",
    # ========================================================================
    # DIAGNOSTIC & STRATEGIC TERMS (not in regex patterns)
    # ========================================================================
    "diagnóstico",
    "caracterización",
    "análisis situacional",
    "año base",
    "situación inicial",
    "brecha",
    "déficit",
    "rezago",
    "carencia",
    "limitación",
    "problemática",
    "necesidad",
    "articulación",
    "concertación",
    "coherencia entre diagnóstico y propuesta",
    "articulación lógica",
    "cadena de valor",
    "matriz causal",
    "eslabones de la cadena",
    "Metodología General Ajustada",
    "MGA",
    # ========================================================================
    # VERIFICATION SOURCES - Where to find evidence in PDT
    # ========================================================================
    "diagnóstico sectorial",
    "capítulo estratégico",
    "programas y proyectos",
    "matriz de metas e indicadores",
    "SisPT",
    "Sistema de Planificación Territorial",
    "TerriData",
    "tablas de alineación estratégica",
]

# =============================================================================
# PERFORMANCE OPTIMIZATION - Fast Lookups
# =============================================================================

# Convert vocabulary to frozenset for O(1) membership testing
# Use this for checking if a term exists in the causal chain vocabulary
CAUSAL_CHAIN_VOCABULARY_SET: Final[frozenset[str]] = frozenset(CAUSAL_CHAIN_VOCABULARY)

# =============================================================================
# PDT PATTERNS - Regex patterns for Plan de Desarrollo Territorial analysis
# =============================================================================

PDT_PATTERNS: Final[dict[str, re.Pattern]] = {
    # ============================================================================
    # SECTION DELIMITERS - Hierarchical structure patterns
    # ============================================================================
    "section_delimiters": re.compile(
        r"^(?:"
        r"PARTE\s+[IVXLCDM]+|"
        r"T[ÍI]TULO\s+[IVXLCDM]+|"
        r"CAP[ÍI]TULO\s+[IVXLCDM]+|"
        r"SECCI[ÓO]N\s+\d+|"
        r"ART[ÍI]CULO\s+\d+|"
        r"\d+\.\s+[A-ZÁÉÍÓÚÑ]+"
        r")",
        re.IGNORECASE | re.MULTILINE
    ),

    # ============================================================================
    # STRATEGIC COMPONENTS
    # ============================================================================
    "vision": re.compile(
        r"VISI[ÓO]N.*?(?=MISI[ÓO]N|CAP[ÍI]TULO|SECCI[ÓO]N|\Z)",
        re.IGNORECASE | re.DOTALL
    ),

    "mission": re.compile(
        r"MISI[ÓO]N.*?(?=VISI[ÓO]N|PRINCIPIOS|VALORES|CAP[ÍI]TULO|\Z)",
        re.IGNORECASE | re.DOTALL
    ),

    "strategic_axes": re.compile(
        r"(?:EJES?\s+ESTRAT[ÉE]GICOS?|L[ÍI]NEAS?\s+ESTRAT[ÉE]GICAS?)"
        r".*?(?=CAP[ÍI]TULO|PARTE|\Z)",
        re.IGNORECASE | re.DOTALL
    ),

    # ============================================================================
    # DIAGNOSTIC PATTERNS
    # ============================================================================
    "diagnostic_section": re.compile(
        r"(?:DIAGN[ÓO]STICO|CARACTERIZACI[ÓO]N|AN[ÁA]LISIS\s+SITUACIONAL)"
        r".*?(?=CAP[ÍI]TULO|PARTE|COMPONENTE\s+ESTRAT[ÉE]GICO|\Z)",
        re.IGNORECASE | re.DOTALL
    ),

    # ============================================================================
    # PROGRAMMATIC PATTERNS
    # ============================================================================
    "programs": re.compile(
        r"PROGRAMA\s+\d+:.*?(?=PROGRAMA\s+\d+|CAP[ÍI]TULO|SECCI[ÓO]N|\Z)",
        re.IGNORECASE | re.DOTALL
    ),

    "subprograms": re.compile(
        r"SUBPROGRAMA\s+\d+\.\d+:.*?(?=SUBPROGRAMA|PROGRAMA|CAP[ÍI]TULO|\Z)",
        re.IGNORECASE | re.DOTALL
    ),

    # ============================================================================
    # INDICATORS AND GOALS
    # ============================================================================
    "indicators": re.compile(
        r"INDICADOR(?:ES)?.*?(?:L[ÍI]NEA\s+BASE|META|UNIDAD\s+DE\s+MEDIDA)",
        re.IGNORECASE | re.DOTALL
    ),

    "goals_table": re.compile(
        r"(?:MATRIZ|TABLA).*?(?:METAS?|INDICADORES?).*?(?=CAP[ÍI]TULO|\Z)",
        re.IGNORECASE | re.DOTALL
    ),

    # ============================================================================
    # FINANCIAL PATTERNS
    # ============================================================================
    "budget": re.compile(
        r"(?:PLAN\s+PLURIANUAL|PLAN\s+FINANCIERO|MARCO\s+FISCAL)"
        r".*?(?=CAP[ÍI]TULO|PARTE|\Z)",
        re.IGNORECASE | re.DOTALL
    ),

    "monetary_amount": re.compile(
        r"\$\s*[\d,.]+(?:\s*(?:millones?|mil\s+millones?|billones?))?",
        re.IGNORECASE
    ),
}

# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Policy Areas and Dimensions
    "CANON_POLICY_AREAS",
    "CANON_DIMENSIONS",

    # Quality Thresholds
    "MICRO_LEVELS",
    "CONFIDENCE_THRESHOLD",
    "COHERENCE_THRESHOLD",
    "ALIGNMENT_THRESHOLD",
    "RISK_THRESHOLDS",

    # Causal Chain Analysis
    "CAUSAL_CHAIN_VOCABULARY",
    "CAUSAL_CHAIN_VOCABULARY_SET",  # O(1) lookup optimized version

    # PDT Patterns
    "PDT_PATTERNS",
]
