"""
Canonical specifications and constants for FARFAN pipeline.

This module provides canonical constants and thresholds that were previously
loaded from JSON files at runtime. All values are frozen at module import time
to improve determinism and traceability.

Source: Extracted from canonical_notation.json and questionnaire configurations
Migration date: 2026-01-16
"""

from __future__ import annotations

from typing import Any

# ============================================================================
# CANONICAL DIMENSIONS (D1-D6)
# ============================================================================

CANON_DIMENSIONS: dict[str, dict[str, Any]] = {
    "D1": {
        "code": "DIM01",
        "name": "INSUMOS",
        "label": "Diagnóstico y Recursos",
        "description": "Evalúa la calidad del diagnóstico territorial, líneas base cuantitativas, identificación de brechas y suficiencia de recursos.",
    },
    "D2": {
        "code": "DIM02",
        "name": "ACTIVIDADES",
        "label": "Diseño de Intervención",
        "description": "Evalúa la formalización de actividades con estructura clara, responsables, cronogramas, costos y mecanismos causales.",
    },
    "D3": {
        "code": "DIM03",
        "name": "PRODUCTOS",
        "label": "Productos y Outputs",
        "description": "Evalúa la especificación de productos (bienes y servicios) con indicadores verificables, fórmulas, fuentes y trazabilidad presupuestal.",
    },
    "D4": {
        "code": "DIM04",
        "name": "RESULTADOS",
        "label": "Resultados y Outcomes",
        "description": "Evalúa la definición de resultados (cambios en la población) con métricas, líneas base, metas y encadenamiento causal.",
    },
    "D5": {
        "code": "DIM05",
        "name": "IMPACTOS",
        "label": "Impactos de Largo Plazo",
        "description": "Evalúa la proyección de impactos (transformaciones estructurales) con rutas de transmisión, rezagos temporales y consideración de riesgos sistémicos.",
    },
    "D6": {
        "code": "DIM06",
        "name": "CAUSALIDAD",
        "label": "Teoría de Cambio",
        "description": "Evalúa la explicitación de teorías de cambio, identificación de causas raíz, mediadores, moderadores y supuestos verificables.",
    },
}

# ============================================================================
# CANONICAL POLICY AREAS (PA01-PA10)
# ============================================================================

CANON_POLICY_AREAS: dict[str, dict[str, Any]] = {
    "PA01": {
        "name": "Derechos de las mujeres e igualdad de género",
        "short_code": "MUJERES",
        "legacy_id": "P1",
        "keywords": [
            "género", "mujer", "mujeres", "igualdad de género", "equidad de género",
            "violencia basada en género", "VBG", "empoderamiento femenino",
            "liderazgo femenino", "participación política mujeres",
        ],
    },
    "PA02": {
        "name": "Prevención de la violencia y protección de la población frente al conflicto armado",
        "short_code": "VIOLENCIA",
        "legacy_id": "P2",
        "keywords": [
            "violencia", "conflicto armado", "seguridad", "protección",
            "grupos armados", "economías ilegales", "narcotráfico",
        ],
    },
    "PA03": {
        "name": "Ambiente sano, cambio climático, prevención y atención a desastres",
        "short_code": "AMBIENTE",
        "legacy_id": "P3",
        "keywords": [
            "ambiente", "cambio climático", "desastres", "medio ambiente",
            "gestión de riesgos", "adaptación climática", "mitigación",
        ],
    },
    "PA04": {
        "name": "Derechos económicos, sociales y culturales",
        "short_code": "DESC",
        "legacy_id": "P4",
        "keywords": [
            "derechos económicos", "derechos sociales", "derechos culturales",
            "educación", "salud", "vivienda", "empleo", "seguridad social",
        ],
    },
    "PA05": {
        "name": "Derechos de las víctimas y construcción de paz",
        "short_code": "VICTIMAS",
        "legacy_id": "P5",
        "keywords": [
            "víctimas", "construcción de paz", "reconciliación", "reparación",
            "verdad", "justicia", "no repetición", "memoria histórica",
        ],
    },
    "PA06": {
        "name": "Derecho al buen futuro de la niñez, adolescencia, juventud",
        "short_code": "NIÑEZ",
        "legacy_id": "P6",
        "keywords": [
            "niñez", "adolescencia", "juventud", "infancia", "protección infantil",
            "derechos de los niños", "entornos protectores",
        ],
    },
    "PA07": {
        "name": "Tierras y territorios",
        "short_code": "TIERRAS",
        "legacy_id": "P7",
        "keywords": [
            "tierras", "territorios", "ordenamiento territorial", "catastro",
            "reforma agraria", "acceso a la tierra", "formalización predial",
        ],
    },
    "PA08": {
        "name": "Líderes y defensores de derechos humanos",
        "short_code": "LIDERES",
        "legacy_id": "P8",
        "keywords": [
            "líderes", "defensores de derechos humanos", "liderazgo comunitario",
            "protección de líderes", "amenazas", "seguridad líderes sociales",
        ],
    },
    "PA09": {
        "name": "Crisis de derechos de personas privadas de la libertad",
        "short_code": "PPL",
        "legacy_id": "P9",
        "keywords": [
            "personas privadas de la libertad", "sistema penitenciario", "cárceles",
            "derechos en prisión", "hacinamiento", "resocialización",
        ],
    },
    "PA10": {
        "name": "Migración transfronteriza",
        "short_code": "MIGRACION",
        "legacy_id": "P10",
        "keywords": [
            "migración", "frontera", "migrantes", "refugiados",
            "movilidad humana", "integración migrantes",
        ],
    },
}

# ============================================================================
# MICRO-LEVEL QUALITY THRESHOLDS
# ============================================================================
# These thresholds define quality levels for scoring and calibration across
# the entire pipeline. They provide a consistent scale for evaluating
# evidence, alignment, and analytical outputs.

MICRO_LEVELS: dict[str, float] = {
    "DEFICIENTE": 0.25,    # Poor quality - significant issues
    "INSUFICIENTE": 0.40,  # Insufficient - below minimum standards
    "ACEPTABLE": 0.55,     # Acceptable - meets minimum requirements
    "BUENO": 0.70,         # Good - above minimum, solid quality
    "EXCELENTE": 0.85,     # Excellent - high quality, best practices
}

# ============================================================================
# ALIGNMENT THRESHOLDS
# ============================================================================

ALIGNMENT_THRESHOLD: float = 0.7  # Minimum alignment score for policy-question match

# ============================================================================
# RISK THRESHOLDS
# ============================================================================

RISK_THRESHOLDS: dict[str, float] = {
    "low": 0.3,
    "medium": 0.6,
    "high": 0.8,
    "critical": 0.95,
}

# ============================================================================
# CAUSAL CHAIN VOCABULARY
# ============================================================================

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
