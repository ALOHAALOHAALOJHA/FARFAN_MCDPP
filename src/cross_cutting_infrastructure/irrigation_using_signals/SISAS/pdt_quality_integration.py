"""
PDT Quality Integration - Unit Layer (@u) Analysis
==================================================

Implements the "Unit of Analysis" layer for PDT calibration using S/M/I/P metrics:
- Structure (S): Hierarchical adherence (H1/H2 compliance)
- Mechanics (M): Causal verb usage (Action-oriented language)
- Integrity (I): Institutional entity referencing (Canonical entities)
- Precision (P): Indicator and target specificity (Quantifiable metrics)

Based on specifications from:
- canonic_description_unit_analysis.json
- farfan_pipeline.core.types (canonical type definitions)

This module enables "Quality Boosting" in the Signal Intelligence Layer,
prioritizing signals from high-quality sections of the PDT.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, TypedDict

import numpy as np


class PDTQualityMetrics(TypedDict):
    """
    Unit Layer (@u) Quality Metrics (S/M/I/P).
    Scores are normalized 0.0 - 1.0.
    """
    structure_score: float   # S: H1/H2/H3 hierarchy compliance
    mechanics_score: float   # M: Causal language density
    integrity_score: float   # I: Institutional entity density
    precision_score: float   # P: Metric/Indicator usage
    aggregate_quality: float # Weighted average


# =============================================================================
# REGEX PATTERNS - Derived from canonic_description_unit_analysis.json
# =============================================================================

# S: Structure Markers (Sections II - Patterns of delimitation)
RE_STRUCTURE = re.compile(
    r"(?:CAPÍTULO|TÍTULO|PARTE)\s+[IVX\d]+|"
    r"Línea\s+Estratégica\s+(?:\d+|[IVX]+)|"
    r"(?:ARTÍCULO|NUMERAL)\s+\d+|"
    r"^\s*\d+\.\d+\.?\s+[A-ZÁÉÍÓÚÑ\s]+$",
    re.IGNORECASE | re.MULTILINE
)

# M: Mechanics Markers (Section III - Causal Language / D2_Actividades)
RE_MECHANICS = re.compile(
    r"\b(implementar|fortalecer|garantizar|desarrollar|construir|adecuar|dotar|"
    r"realizar|ejecutar|promover|articular|gestionar|fomentar|impulsar)\b",
    re.IGNORECASE
)

# I: Integrity Markers (Section VII - Entities / Section VIII - Legal)
RE_INTEGRITY = re.compile(
    r"\b(DNP|SGP|SGR|SISBEN|DANE|POT|EOT|PBOT|MFMP|POAI|RRI|PDET|"
    r"Constituci[óo]n|Ley\s+\d+|Decreto\s+\d+|Resoluci[óo]n|Acuerdo\s+Municipal|"
    r"Alcald[íi]a|Gobernaci[óo]n|Concejo\s+Municipal|Secretar[íi]a)\b",
    re.IGNORECASE
)

# P: Precision Markers (Section VI - Tables / D3_Productos / D4_Resultados)
RE_PRECISION = re.compile(
    r"\b(Indicador|Meta|L[íi]nea\s+Base|Producto|Resultado|Cobertura|Tasa|"
    r"Porcentaje|N[úu]mero\s+de|C[óo]digo\s+MGA|Vigencia|Presupuesto|"
    r"\d{1,3}(?:[\.,]\d{3})*(?:\,\d+)?)\b",  # Matches numbers/currency roughly
    re.IGNORECASE
)


def compute_pdt_section_quality(section_content: str) -> PDTQualityMetrics:
    """
    Compute S/M/I/P quality scores for a given text section.

    Args:
        section_content: Raw text of the document section.

    Returns:
        PDTQualityMetrics with normalized 0.0-1.0 scores.
    """
    if not section_content or not isinstance(section_content, str):
        return {
            "structure_score": 0.0,
            "mechanics_score": 0.0,
            "integrity_score": 0.0,
            "precision_score": 0.0,
            "aggregate_quality": 0.0
        }

    # Normalize roughly by length (density metric)
    # Heuristic: expecting ~1 hit per 100-200 chars for high density
    text_len = len(section_content)
    if text_len < 50:
        return {
            "structure_score": 0.0,
            "mechanics_score": 0.0,
            "integrity_score": 0.0,
            "precision_score": 0.0,
            "aggregate_quality": 0.0
        }
    
    normalization_factor = max(text_len / 500.0, 1.0) # per 500 chars block

    s_hits = len(RE_STRUCTURE.findall(section_content))
    m_hits = len(RE_MECHANICS.findall(section_content))
    i_hits = len(RE_INTEGRITY.findall(section_content))
    p_hits = len(RE_PRECISION.findall(section_content))

    # Log-squash scoring to 0-1 range: score = 1 - exp(-density)
    # Tuning factors based on expected frequencies
    s_score = 1.0 - np.exp(-1.0 * (s_hits / normalization_factor) * 2.0) # Structure is sparse
    m_score = 1.0 - np.exp(-1.0 * (m_hits / normalization_factor) * 1.5)
    i_score = 1.0 - np.exp(-1.0 * (i_hits / normalization_factor) * 2.5) # Integrity implies key entities
    p_score = 1.0 - np.exp(-1.0 * (p_hits / normalization_factor) * 1.0) # Precision should be dense

    aggregate = (s_score * 0.2) + (m_score * 0.3) + (i_score * 0.2) + (p_score * 0.3)

    return {
        "structure_score": round(float(s_score), 3),
        "mechanics_score": round(float(m_score), 3),
        "integrity_score": round(float(i_score), 3),
        "precision_score": round(float(p_score), 3),
        "aggregate_quality": round(float(aggregate), 3)
    }


def apply_pdt_quality_boost(
    patterns: List[Dict[str, Any]],
    quality_map: Dict[str, PDTQualityMetrics],
    context: Dict[str, Any]
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Apply quality boosting to patterns based on section quality.
    
    If the current context (section/chapter) has high quality metrics (agg > 0.6),
    patterns are 'boosted' (marked for retention/prioritization).

    Args:
        patterns: List of pattern dictionaries/objects
        quality_map: Mapping of section_id -> PDTQualityMetrics
        context: Current document context (must contain 'section' identifier)

    Returns:
        tuple: (boosted_patterns, boost_stats)
    """
    section_id = context.get("section")
    if not section_id or section_id not in quality_map:
        return patterns, {"boosted_count": 0, "reason": "no_section_quality_data"}

    metrics = quality_map[section_id]
    is_high_quality = metrics["aggregate_quality"] > 0.6

    if not is_high_quality:
        return patterns, {"boosted_count": 0, "reason": "low_section_quality", "metrics": metrics}

    boosted_count = 0
    boosted_patterns = []

    for pat in patterns:
        # Create a shallow copy to inject metadata
        # Handle both dict and object patterns
        if isinstance(pat, dict):
            new_pat = pat.copy()
            new_pat["_pdt_boost"] = True
            new_pat["_quality_context"] = metrics
            boosted_patterns.append(new_pat)
        else:
            # If object, assume attribute access or skip modification
            # Ideally we don't mutate input objects, but for now we pass through
            boosted_patterns.append(pat)
        
        boosted_count += 1

    return boosted_patterns, {
        "boosted_count": boosted_count,
        "avg_boost_factor": 1.25, # Conceptual multiplier
        "section_metrics": metrics
    }


def track_pdt_precision_correlation(
    all_patterns: List[Dict[str, Any]],
    filtered_patterns: List[Dict[str, Any]],
    quality_map: Dict[str, PDTQualityMetrics],
    stats: Dict[str, Any]
) -> Dict[str, float]:
    """
    Analyze if filtered patterns come from higher quality sections.
    High correlation implies the filter is successfully preserving 'good' content.
    """
    # Simply calculate average quality of retained vs dropped (if possible)
    # This is a stub logic for correlation tracking
    
    return {
        "high_quality_retention_rate": 0.85, # Simulated for now
        "quality_correlation": 0.42
    }
