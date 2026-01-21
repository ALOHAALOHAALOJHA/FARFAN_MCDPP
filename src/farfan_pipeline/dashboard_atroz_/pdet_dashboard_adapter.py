"""PDET Data Adapter for Dashboard Integration.

Transforms real PDET Colombia data into dashboard-friendly format with
coordinates, scores, and metadata for visualization.
"""

from typing import Any, Dict, List
import random

from farfan_pipeline.dashboard_atroz_.pdet_colombia_data import (
    PDET_MUNICIPALITIES,
    PDETSubregion,
    get_municipalities_by_subregion,
    get_subregion_statistics,
)


# Subregion ID mapping for dashboard consistency
SUBREGION_ID_MAP = {
    PDETSubregion.ALTO_PATIA: "alto_patia",
    PDETSubregion.ARAUCA: "arauca",
    PDETSubregion.BAJO_CAUCA: "bajo_cauca",
    PDETSubregion.CAGUAN: "cuenca_caguan",
    PDETSubregion.CATATUMBO: "catatumbo",
    PDETSubregion.CHOCO: "choco",
    PDETSubregion.MACARENA: "macarena",
    PDETSubregion.MONTES_MARIA: "montes_maria",
    PDETSubregion.PACIFICO_MEDIO: "pacifico_medio",
    PDETSubregion.PACIFICO_NARINENSE: "pacifico_narinense",
    PDETSubregion.PUTUMAYO: "putumayo",
    PDETSubregion.SIERRA_NEVADA: "sierra_nevada",
    PDETSubregion.SUR_BOLIVAR: "sur_bolivar",
    PDETSubregion.SUR_CORDOBA: "sur_cordoba",
    PDETSubregion.SUR_TOLIMA: "sur_tolima",
    PDETSubregion.URABA: "uraba",
}

# Visual positioning for constellation view (normalized coordinates 0-100)
# Based on approximate geographic positions in Colombia
SUBREGION_POSITIONS = {
    "alto_patia": {"x": 15, "y": 65},
    "arauca": {"x": 85, "y": 20},
    "bajo_cauca": {"x": 28, "y": 22},
    "cuenca_caguan": {"x": 60, "y": 60},
    "catatumbo": {"x": 65, "y": 15},
    "choco": {"x": 8, "y": 30},
    "macarena": {"x": 70, "y": 50},
    "montes_maria": {"x": 35, "y": 10},
    "pacifico_medio": {"x": 10, "y": 40},
    "pacifico_narinense": {"x": 5, "y": 70},
    "putumayo": {"x": 50, "y": 80},
    "sierra_nevada": {"x": 55, "y": 8},
    "sur_bolivar": {"x": 40, "y": 20},
    "sur_cordoba": {"x": 30, "y": 18},
    "sur_tolima": {"x": 35, "y": 45},
    "uraba": {"x": 20, "y": 25},
}


def load_pdet_regions_for_dashboard(
    include_scores: bool = True, score_source: str = "random"
) -> List[Dict[str, Any]]:
    """Load PDET regions in dashboard format.

    Args:
        include_scores: Whether to include analysis scores
        score_source: Source of scores - "random" for mock, "artifacts" for real pipeline output

    Returns:
        List of region dicts compatible with dashboard constellation view
    """
    regions = []
    stats = get_subregion_statistics()

    for subregion_enum in PDETSubregion:
        subregion_id = SUBREGION_ID_MAP[subregion_enum]
        subregion_name = subregion_enum.value
        subregion_stats = stats[subregion_name]

        municipalities = get_municipalities_by_subregion(subregion_enum)
        position = SUBREGION_POSITIONS[subregion_id]

        region_data = {
            "id": subregion_id,
            "name": subregion_name,
            "municipalities": subregion_stats["municipality_count"],
            "population": subregion_stats["total_population"],
            "area_km2": subregion_stats["total_area_km2"],
            "departments": subregion_stats["departments"],
            "x": position["x"],
            "y": position["y"],
        }

        # Add scores if requested
        if include_scores:
            if score_source == "random":
                # Generate realistic mock scores (will be replaced by real scores)
                region_data["score"] = _generate_mock_score(subregion_id)
                region_data["dimension_scores"] = _generate_mock_dimension_scores()
                region_data["cluster_scores"] = _generate_mock_cluster_scores()
            elif score_source == "artifacts":
                # Load from pipeline artifacts (to be implemented)
                region_data.update(_load_scores_from_artifacts(subregion_id))

        # Add metadata
        region_data["metadata"] = {
            "data_source": "PDET Colombia Official Dataset 2024",
            "municipality_list": [m.name for m in municipalities[:5]],  # First 5
            "score_source": score_source,
        }

        regions.append(region_data)

    return regions


def _generate_mock_score(subregion_id: str) -> int:
    """Generate realistic mock score for subregion.

    Scores vary by region characteristics:
    - Urban regions: 70-90
    - Mixed regions: 60-75
    - Rural regions: 50-70
    """
    # Seed with region ID for consistency
    random.seed(hash(subregion_id) % 10000)

    # Region-specific score ranges (based on historical PDET progress)
    score_ranges = {
        "montes_maria": (80, 92),  # High progress
        "sur_tolima": (78, 90),
        "sierra_nevada": (75, 88),
        "alto_patia": (72, 85),
        "macarena": (70, 82),
        "bajo_cauca": (65, 75),
        "catatumbo": (65, 75),
        "uraba": (62, 72),
        "arauca": (60, 75),
        "putumayo": (60, 78),
        "cuenca_caguan": (58, 75),
        "pacifico_narinense": (55, 65),
        "sur_bolivar": (60, 70),
        "sur_cordoba": (58, 68),
        "pacifico_medio": (55, 68),
        "choco": (50, 60),  # Lower baseline progress
    }

    min_score, max_score = score_ranges.get(subregion_id, (60, 75))
    return random.randint(min_score, max_score)


def _generate_mock_dimension_scores() -> Dict[str, int]:
    """Generate mock scores for 6 dimensions."""
    return {
        "D1_INSUMOS": random.randint(65, 85),
        "D2_VOLUNTAD": random.randint(60, 80),
        "D3_CONTEXTO": random.randint(55, 75),
        "D4_COHERENCIA": random.randint(60, 80),
        "D5_SISAS": random.randint(50, 70),
        "D6_IMPLEMENTACION": random.randint(65, 85),
    }


def _generate_mock_cluster_scores() -> Dict[str, int]:
    """Generate mock scores for 4 clusters."""
    return {
        "CL01_SEC_PAZ": random.randint(65, 80),
        "CL02_GP": random.randint(60, 75),
        "CL03_TERR_AMB": random.randint(55, 70),
        "CL04_DESC_CRIS": random.randint(40, 60),  # Typically lower
    }


def _load_scores_from_artifacts(subregion_id: str) -> Dict[str, Any]:
    """Load real scores from pipeline artifacts.

    This will be implemented to read from:
    - dashboard_outputs/<job_id>/region_<subregion_id>_report.json

    For now, returns empty dict (to be populated by real pipeline results).

    Args:
        subregion_id: Subregion identifier

    Returns:
        Dict with score, dimension_scores, cluster_scores, micro_scores
    """
    # TODO: Implement artifact loading
    # For now, return mock data
    return {
        "score": _generate_mock_score(subregion_id),
        "dimension_scores": _generate_mock_dimension_scores(),
        "cluster_scores": _generate_mock_cluster_scores(),
        "score_source": "artifacts",
        "artifact_loaded": False,
    }


def get_region_detail(region_id: str, job_id: str = None) -> Dict[str, Any]:
    """Get detailed region data for modal view.

    Args:
        region_id: Region identifier (e.g., "arauca")
        job_id: Optional job ID to load artifacts

    Returns:
        Detailed region dict with macro/meso/micro breakdown
    """
    # Find subregion enum
    subregion_enum = None
    for enum, region_id_mapped in SUBREGION_ID_MAP.items():
        if region_id_mapped == region_id:
            subregion_enum = enum
            break

    if not subregion_enum:
        raise ValueError(f"Unknown region_id: {region_id}")

    municipalities = get_municipalities_by_subregion(subregion_enum)
    stats = get_subregion_statistics()[subregion_enum.value]

    # Base detail
    detail = {
        "id": region_id,
        "name": subregion_enum.value,
        "statistics": stats,
        "municipalities": [
            {
                "name": m.name,
                "department": m.department,
                "population": m.population,
                "area_km2": m.area_km2,
                "dane_code": m.dane_code,
            }
            for m in municipalities
        ],
    }

    # Add analysis scores if job_id provided
    if job_id:
        # TODO: Load from DashboardDataService.build_region_detail()
        detail["analysis"] = {
            "macro": {"score": 75, "band": "MEDIO", "coherence": 0.82},
            "meso": {
                "clusters": [
                    {"id": "CL01", "name": "Seguridad y Paz", "score": 72},
                    {"id": "CL02", "name": "Gestión Pública", "score": 68},
                    {"id": "CL03", "name": "Territorio y Ambiente", "score": 65},
                    {"id": "CL04", "name": "Desconfianza y Crisis", "score": 45},
                ]
            },
            "micro": {
                "total_questions": 300,
                "avg_score": 67,
                "breakdown_by_pa": {},  # Will be populated from artifacts
            },
        }

    return detail


def get_region_connections() -> List[Dict[str, Any]]:
    """Get connections between regions for constellation view.

    Connections based on:
    - Geographic proximity
    - Shared departments
    - Similar policy challenges

    Returns:
        List of connection dicts with source, target, strength
    """
    connections = [
        # Geographic clusters
        {"source": "arauca", "target": "catatumbo", "strength": 0.7},
        {"source": "catatumbo", "target": "sierra_nevada", "strength": 0.6},
        {"source": "sierra_nevada", "target": "montes_maria", "strength": 0.5},
        {"source": "bajo_cauca", "target": "uraba", "strength": 0.8},
        {"source": "bajo_cauca", "target": "sur_cordoba", "strength": 0.7},
        {"source": "uraba", "target": "choco", "strength": 0.6},
        {"source": "choco", "target": "pacifico_medio", "strength": 0.7},
        {"source": "pacifico_medio", "target": "pacifico_narinense", "strength": 0.8},
        {"source": "pacifico_narinense", "target": "alto_patia", "strength": 0.6},
        {"source": "alto_patia", "target": "sur_tolima", "strength": 0.5},
        {"source": "putumayo", "target": "cuenca_caguan", "strength": 0.7},
        {"source": "cuenca_caguan", "target": "macarena", "strength": 0.8},
        {"source": "macarena", "target": "arauca", "strength": 0.5},
        {"source": "sur_bolivar", "target": "bajo_cauca", "strength": 0.6},
        {"source": "sur_bolivar", "target": "sur_cordoba", "strength": 0.5},
        # Policy-based connections
        {"source": "montes_maria", "target": "uraba", "strength": 0.4},
        {"source": "arauca", "target": "putumayo", "strength": 0.4},
    ]

    return connections


# Quick validation
if __name__ == "__main__":
    regions = load_pdet_regions_for_dashboard()
    print(f"Loaded {len(regions)} PDET regions")
    print("\nSample region:")
    print(regions[0])
    print("\nConnections:", len(get_region_connections()))
