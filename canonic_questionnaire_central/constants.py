"""
Canonical constants loader for questionnaire system.

This module loads canonical dimensions, policy areas, and other domain constants
from canonical_notation.json and exposes them as Python constants for use across
the pipeline.

These are DOMAIN constants (business logic), not calibration parameters.

Author: CQC Team
Date: 2026-01-16
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Load canonical notation JSON
_CONFIG_DIR = Path(__file__).parent / "config"
_CANONICAL_PATH = _CONFIG_DIR / "canonical_notation.json"

with open(_CANONICAL_PATH, "r", encoding="utf-8") as f:
    _CANONICAL_DATA = json.load(f)

# ============================================================================
# CANONICAL DIMENSIONS (D1-D6)
# ============================================================================

CANON_DIMENSIONS: dict[str, dict[str, Any]] = _CANONICAL_DATA.get("dimensions", {})

# ============================================================================
# CANONICAL POLICY AREAS (PA01-PA10)
# ============================================================================

CANON_POLICY_AREAS: dict[str, dict[str, Any]] = _CANONICAL_DATA.get("policy_areas", {})

# ============================================================================
# QUALITY LEVEL THRESHOLDS
# ============================================================================
# These thresholds define quality levels for scoring across the pipeline

MICRO_LEVELS: dict[str, float] = {
    "DEFICIENTE": 0.25,    # Poor quality - significant issues
    "INSUFICIENTE": 0.40,  # Insufficient - below minimum standards
    "ACEPTABLE": 0.55,     # Acceptable - meets minimum requirements
    "BUENO": 0.70,         # Good - above minimum, solid quality
    "EXCELENTE": 0.85,     # Excellent - high quality, best practices
}

# ============================================================================
# ALIGNMENT AND RISK THRESHOLDS
# ============================================================================

ALIGNMENT_THRESHOLD: float = 0.7  # Minimum alignment score for policy-question match

RISK_THRESHOLDS: dict[str, float] = {
    "low": 0.3,
    "medium": 0.6,
    "high": 0.8,
    "critical": 0.95,
}

# ============================================================================
# CAUSAL CHAIN VOCABULARY
# ============================================================================
# Vocabulary for identifying causal chain elements in text

CAUSAL_CHAIN_VOCABULARY: dict[str, list[str]] = {
    "insumos": [
        "diagnóstico", "línea base", "recursos", "presupuesto", "capacidades",
        "activos", "infraestructura inicial", "condiciones previas",
    ],
    "actividades": [
        "implementación", "ejecución", "intervención", "acción", "programa",
        "proyecto", "estrategia", "operación", "proceso",
    ],
    "productos": [
        "entregable", "output", "bien", "servicio", "resultado tangible",
        "producto verificable", "meta de producto",
    ],
    "resultados": [
        "outcome", "cambio", "mejora", "impacto intermedio", "efecto",
        "transformación", "logro", "meta de resultado",
    ],
    "impactos": [
        "impacto de largo plazo", "transformación estructural", "cambio sistémico",
        "efecto sostenido", "legado", "meta de impacto",
    ],
}

# ============================================================================
# PDT (Plan de Desarrollo Territorial) PATTERNS
# ============================================================================
# Patterns for identifying PDT structural elements

PDT_PATTERNS: dict[str, list[str]] = {
    "strategic_objectives": [
        "objetivo estratégico", "meta estratégica", "visión", "misión",
        "propósito superior", "objetivo general",
    ],
    "programs": [
        "programa", "subprograma", "línea estratégica", "eje",
        "componente programático",
    ],
    "projects": [
        "proyecto", "iniciativa", "acción", "intervención específica",
    ],
    "indicators": [
        "indicador", "métrica", "medida", "KPI", "variable de seguimiento",
    ],
    "budget": [
        "presupuesto", "inversión", "recursos financieros", "costeo",
        "proyección financiera", "asignación presupuestal",
    ],
}
