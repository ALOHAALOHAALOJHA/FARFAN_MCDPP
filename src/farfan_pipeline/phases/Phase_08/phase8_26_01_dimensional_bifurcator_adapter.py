# phase8_26_01_dimensional_bifurcator_adapter.py - Adapter for Bifurcator Integration
"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_26_01_dimensional_bifurcator_adapter
Purpose: Adapter to integrate dimensional engine with existing bifurcator
Owner: phase8_core
Stage: 26 (Dimensional Engine)
Order: 01
Type: ADAPTER
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-26

═══════════════════════════════════════════════════════════════════════════════════
             🔱 DIMENSIONAL BIFURCATOR ADAPTER - Bridge Layer 🔱
═══════════════════════════════════════════════════════════════════════════════════

PURPOSE:
    This adapter bridges the dimensional recommendation engine with the existing
    bifurcator (phase8_25_00_recommendation_bifurcator.py) to enable:
    
    1. Dimensional-first recommendation generation
    2. Backward compatibility with existing scoring systems
    3. Enhanced MESO/MACRO dimensional variance detection
    4. Capacity-sensitive recommendation adjustment
    
ARCHITECTURE:
    DimensionalEngine → Adapter → Bifurcator → Amplified Recommendations
    
    The adapter:
    - Converts dimensional recommendations to bifurcator format
    - Enriches with dimensional context for better amplification
    - Maintains compatibility with existing Phase 8 interfaces

Author: F.A.R.F.A.N Architecture Team
Python: 3.10+
═══════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .phase8_26_00_dimensional_recommendation_engine import (
    DimensionalRecommendationEngine,
    InstantiatedRecommendation,
    DimensionalAnalysis,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__all__ = [
    "DimensionalBifurcatorAdapter",
    "convert_to_bifurcator_format",
    "enrich_with_dimensional_context",
]


class DimensionalBifurcatorAdapter:
    """
    Adapter to integrate dimensional engine with bifurcator.
    
    Converts dimensional recommendations to the format expected by
    phase8_25_00_recommendation_bifurcator.py while enriching with
    dimensional context for better amplification.
    """
    
    def __init__(
        self,
        dimensional_catalog_path: Path | str,
        enable_dimensional_amplification: bool = True
    ):
        """
        Initialize adapter.
        
        Args:
            dimensional_catalog_path: Path to dimensional catalog
            enable_dimensional_amplification: Enable dimensional-aware amplification
        """
        self.engine = DimensionalRecommendationEngine(dimensional_catalog_path)
        self.enable_dimensional_amplification = enable_dimensional_amplification
        
        logger.info("Dimensional bifurcator adapter initialized")
    
    def generate_recommendations_for_scoring(
        self,
        pa_id: str,
        scores: dict[str, float],
        capacity_levels: dict[str, str] | None = None,
        include_dimensional_analysis: bool = True
    ) -> dict[str, Any]:
        """
        Generate recommendations for a PA with scoring data.
        
        Args:
            pa_id: Policy Area ID
            scores: Dict mapping dimension_id to score
            capacity_levels: Optional capacity levels
            include_dimensional_analysis: Include dimensional pattern analysis
            
        Returns:
            Dict with recommendations and optional dimensional analysis
        """
        # Generate dimensional recommendations
        recommendations = self.engine.generate_all_recommendations_for_pa(
            pa_id=pa_id,
            scores=scores,
            capacity_levels=capacity_levels
        )
        
        # Convert to bifurcator format
        bifurcator_recs = [
            self._to_bifurcator_format(rec) for rec in recommendations
        ]
        
        result = {
            "pa_id": pa_id,
            "recommendations": bifurcator_recs,
            "total_recommendations": len(bifurcator_recs),
            "dimensional_engine": True,
            "catalog_version": self.engine.catalog["metadata"]["version"]
        }
        
        # Add dimensional analysis if requested
        if include_dimensional_analysis:
            # For analysis, we need scores from all PAs
            # For now, include single-PA stats
            result["dimensional_summary"] = self._summarize_dimensional_status(
                recommendations
            )
        
        return result
    
    def generate_system_wide_analysis(
        self,
        all_scores: dict[str, dict[str, float]]
    ) -> dict[str, Any]:
        """
        Generate system-wide dimensional analysis.
        
        Args:
            all_scores: Nested dict {pa_id: {dimension_id: score}}
            
        Returns:
            Dict with dimensional analyses and MESO/MACRO triggers
        """
        analyses = self.engine.analyze_dimensional_patterns(all_scores)
        
        # Separate by intervention level needed
        meso_triggers = [a for a in analyses if a.needs_meso_intervention]
        macro_triggers = [a for a in analyses if a.needs_macro_intervention]
        
        return {
            "total_dimensions_analyzed": len(analyses),
            "dimensional_analyses": [self._analysis_to_dict(a) for a in analyses],
            "meso_intervention_triggers": [
                self._create_meso_trigger(a) for a in meso_triggers
            ],
            "macro_intervention_triggers": [
                self._create_macro_trigger(a) for a in macro_triggers
            ],
            "summary": self._create_system_summary(analyses)
        }
    
    def _to_bifurcator_format(
        self,
        rec: InstantiatedRecommendation
    ) -> dict[str, Any]:
        """
        Convert InstantiatedRecommendation to bifurcator-compatible format.
        
        The bifurcator expects recommendations in the format from
        phase8_00_00_data_models.Recommendation
        """
        return {
            "rule_id": rec.rule_id,
            "level": rec.level,
            "problem": (
                f"El puntaje de {rec.pa_id} en {rec.dimension_id} "
                f"({rec.dimension_name}) se encuentra en banda {rec.band} "
                f"(score: {rec.score:.2f}), requiriendo intervención específica."
            ),
            "intervention": self._format_intervention(rec),
            "indicator": {
                "name": f"{rec.pa_id}-{rec.dimension_id} mejora {rec.band.lower()}",
                "baseline": rec.score,
                "target": self._calculate_target(rec.score, rec.band),
                "unit": "proporción",
                "formula": "COUNT(compliant_items) / COUNT(total_items)",
                "acceptable_range": [0.0, 3.0],
                "data_source": rec.monitoring_system,
                "questions_covered": rec.questions
            },
            "responsible": {
                "entity": rec.responsible_entity,
                "role": rec.responsible_description,
                "legal_mandate": rec.legal_framework,
                "coordination": rec.coordination_entities
            },
            "horizon": {
                "duration_months": rec.duration_months,
                "band": rec.band,
                "start_type": "plan_approval_date"
            },
            "verification": [
                {
                    "type": "DOCUMENT",
                    "artifact": f"Informe de cumplimiento {rec.dimension_id} - {rec.band}",
                    "format": "PDF"
                },
                {
                    "type": "METRIC",
                    "artifact": f"Medición de indicadores {rec.dimension_id}",
                    "format": "JSON",
                    "validation_query": f"SELECT metric_value FROM metrics WHERE metric_id = '{rec.dimension_id}'"
                }
            ],
            "metadata": {
                **rec.metadata,
                "dimensional_engine": True,
                "dimension_id": rec.dimension_id,
                "dimension_name": rec.dimension_name,
                "causal_position": rec.dimensional_context.get("causal_position"),
                "capacity_level": rec.capacity_level,
                "budget_multiplier": rec.budget_multiplier,
                # Enhanced for bifurcation
                "dimensional_context": {
                    "core_activities": rec.core_activities,
                    "expected_products": rec.expected_products,
                    "expected_results": rec.expected_results,
                    "causal_mechanism": rec.causal_mechanism,
                    "method_bindings": rec.method_bindings
                }
            },
            # For bifurcation amplification
            "amplification_hints": {
                "dimensional_resonance": self._get_resonance_dimensions(rec.dimension_id),
                "cross_pollination_targets": self._get_cross_pollination_pas(rec.pa_id),
                "temporal_cascade_enabled": rec.band in ["CRISIS", "CRÍTICO"]
            }
        }
    
    def _format_intervention(self, rec: InstantiatedRecommendation) -> str:
        """Format intervention text with PA-specific details"""
        intervention = rec.intervention_logic
        
        # Add legal framework reference
        intervention += f"\n\nMarco legal aplicable: {rec.legal_framework}"
        
        # Add responsible entity
        intervention += f"\n\nEjecución: {rec.responsible_entity}"
        
        # Add monitoring system
        intervention += f"\n\nSeguimiento: {rec.monitoring_system}"
        
        return intervention
    
    def _calculate_target(self, current_score: float, band: str) -> float:
        """Calculate target score for improvement"""
        targets = {
            "CRISIS": 0.81,      # Move to CRÍTICO threshold
            "CRÍTICO": 1.66,     # Move to ACEPTABLE threshold
            "ACEPTABLE": 2.31,   # Move to BUENO threshold
            "BUENO": 2.71,       # Move to EXCELENTE threshold
            "EXCELENTE": 3.0     # Maintain excellence
        }
        return targets.get(band, current_score + 0.5)
    
    def _get_resonance_dimensions(self, dimension_id: str) -> list[str]:
        """
        Get dimensions that resonate with this dimension.
        
        Based on causal chain: DIM01 → DIM02 → DIM03 → DIM04 → DIM05 → DIM06
        """
        causal_chain = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]
        
        try:
            idx = causal_chain.index(dimension_id)
            # Downstream dimensions benefit from improvements
            return causal_chain[idx + 1:]
        except ValueError:
            return []
    
    def _get_cross_pollination_pas(self, pa_id: str) -> list[str]:
        """Get PAs that could benefit from cross-pollination"""
        # Based on cluster membership
        clusters = {
            "CL01": ["PA02", "PA05", "PA07"],  # Seguridad y Paz
            "CL02": ["PA01", "PA06", "PA08"],  # Grupos Poblacionales
            "CL03": ["PA03", "PA04"],          # Territorio-Ambiente
            "CL04": ["PA09", "PA10"]           # DESC y Crisis
        }
        
        for cluster_pas in clusters.values():
            if pa_id in cluster_pas:
                return [p for p in cluster_pas if p != pa_id]
        
        return []
    
    def _summarize_dimensional_status(
        self,
        recommendations: list[InstantiatedRecommendation]
    ) -> dict[str, Any]:
        """Summarize dimensional status for a PA"""
        by_band = {"CRISIS": 0, "CRÍTICO": 0, "ACEPTABLE": 0, "BUENO": 0, "EXCELENTE": 0}
        
        for rec in recommendations:
            by_band[rec.band] += 1
        
        critical_count = by_band["CRISIS"] + by_band["CRÍTICO"]
        health_score = (
            by_band["EXCELENTE"] * 1.0 +
            by_band["BUENO"] * 0.7 +
            by_band["ACEPTABLE"] * 0.4 +
            by_band["CRÍTICO"] * 0.1 +
            by_band["CRISIS"] * 0.0
        ) / len(recommendations)
        
        return {
            "by_band": by_band,
            "critical_dimensions": critical_count,
            "health_score": health_score,
            "status": self._interpret_health_score(health_score)
        }
    
    def _interpret_health_score(self, score: float) -> str:
        """Interpret dimensional health score"""
        if score >= 0.8:
            return "SALUDABLE"
        elif score >= 0.6:
            return "ESTABLE"
        elif score >= 0.4:
            return "VULNERABLE"
        elif score >= 0.2:
            return "CRÍTICO"
        else:
            return "EMERGENCIA"
    
    def _analysis_to_dict(self, analysis: DimensionalAnalysis) -> dict[str, Any]:
        """Convert DimensionalAnalysis to dict"""
        return asdict(analysis)
    
    def _create_meso_trigger(self, analysis: DimensionalAnalysis) -> dict[str, Any]:
        """Create MESO intervention trigger"""
        return {
            "level": "MESO",
            "dimension": analysis.dimension_id,
            "dimension_name": analysis.dimension_name,
            "affected_pas": analysis.pas_in_crisis + analysis.pas_in_critical,
            "recurrence_rate": analysis.recurrence_rate,
            "rationale": analysis.intervention_rationale,
            "recommended_action": (
                f"Coordinar intervención intersectorial en {analysis.dimension_name} "
                f"para {len(analysis.pas_in_crisis + analysis.pas_in_critical)} PAs afectadas"
            )
        }
    
    def _create_macro_trigger(self, analysis: DimensionalAnalysis) -> dict[str, Any]:
        """Create MACRO intervention trigger"""
        return {
            "level": "MACRO",
            "dimension": analysis.dimension_id,
            "dimension_name": analysis.dimension_name,
            "systemic_failure_rate": analysis.recurrence_rate,
            "variance": analysis.variance,
            "rationale": analysis.intervention_rationale,
            "recommended_action": (
                f"Fortalecer capacidades estructurales del sistema en {analysis.dimension_name}: "
                f"datos abiertos, gobernanza, aprendizaje institucional"
            )
        }
    
    def _create_system_summary(
        self,
        analyses: list[DimensionalAnalysis]
    ) -> dict[str, Any]:
        """Create system-wide summary"""
        total_meso = sum(1 for a in analyses if a.needs_meso_intervention)
        total_macro = sum(1 for a in analyses if a.needs_macro_intervention)
        
        avg_recurrence = sum(a.recurrence_rate for a in analyses) / len(analyses)
        
        return {
            "dimensions_needing_meso": total_meso,
            "dimensions_needing_macro": total_macro,
            "average_recurrence_rate": avg_recurrence,
            "system_health": self._calculate_system_health(analyses),
            "priority_dimensions": self._identify_priority_dimensions(analyses)
        }
    
    def _calculate_system_health(self, analyses: list[DimensionalAnalysis]) -> str:
        """Calculate overall system health"""
        avg_score = sum(a.mean_score for a in analyses) / len(analyses)
        
        if avg_score >= 2.31:
            return "BUENO"
        elif avg_score >= 1.66:
            return "ACEPTABLE"
        elif avg_score >= 0.81:
            return "CRÍTICO"
        else:
            return "CRISIS"
    
    def _identify_priority_dimensions(
        self,
        analyses: list[DimensionalAnalysis]
    ) -> list[str]:
        """Identify dimensions requiring priority attention"""
        # Prioritize dimensions with high recurrence and low scores
        priorities = sorted(
            analyses,
            key=lambda a: (a.recurrence_rate, -a.mean_score),
            reverse=True
        )
        
        return [a.dimension_id for a in priorities[:3]]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def convert_to_bifurcator_format(
    rec: InstantiatedRecommendation,
    adapter: DimensionalBifurcatorAdapter | None = None
) -> dict[str, Any]:
    """
    Convert dimensional recommendation to bifurcator format.
    
    Args:
        rec: InstantiatedRecommendation object
        adapter: Optional adapter instance (creates new if None)
        
    Returns:
        Dict in bifurcator-compatible format
    """
    if adapter is None:
        # This is just for format conversion, don't need full engine
        adapter = type('obj', (object,), {
            '_to_bifurcator_format': lambda self, r: {
                "rule_id": r.rule_id,
                "level": r.level,
                "dimension_id": r.dimension_id,
                "pa_id": r.pa_id,
                # ... minimal conversion
            }
        })()
    
    return adapter._to_bifurcator_format(rec)


def enrich_with_dimensional_context(
    recommendations: list[dict[str, Any]],
    dimensional_catalog_path: Path | str
) -> list[dict[str, Any]]:
    """
    Enrich existing recommendations with dimensional context.
    
    Args:
        recommendations: List of recommendation dicts
        dimensional_catalog_path: Path to dimensional catalog
        
    Returns:
        Enriched recommendations
    """
    adapter = DimensionalBifurcatorAdapter(dimensional_catalog_path)
    
    enriched = []
    for rec in recommendations:
        # Add dimensional metadata if not present
        if "dimensional_context" not in rec.get("metadata", {}):
            dim_id = rec.get("metadata", {}).get("dimension_id")
            if dim_id:
                dim_data = adapter.engine.dimensions.get(dim_id, {})
                rec["metadata"]["dimensional_context"] = {
                    "dimension_name": dim_data.get("name", ""),
                    "causal_position": dim_data.get("causal_position", 0),
                    "description": dim_data.get("description", "")
                }
        
        enriched.append(rec)
    
    return enriched


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    catalog_path = Path(__file__).parent / "json_phase_eight" / "dimensional_recommendations_catalog.json"
    
    if catalog_path.exists():
        adapter = DimensionalBifurcatorAdapter(catalog_path)
        
        # Test recommendation generation
        result = adapter.generate_recommendations_for_scoring(
            pa_id="PA01",
            scores={
                "DIM01": 0.5,
                "DIM02": 1.2,
                "DIM03": 1.8,
                "DIM04": 2.1,
                "DIM05": 2.5,
                "DIM06": 1.0
            },
            capacity_levels={
                "DIM01": "LOW",
                "DIM02": "MEDIUM"
            }
        )
        
        print(f"Generated {result['total_recommendations']} recommendations")
        print(f"Dimensional summary: {result['dimensional_summary']}")
    else:
        print(f"Catalog not found at: {catalog_path}")
