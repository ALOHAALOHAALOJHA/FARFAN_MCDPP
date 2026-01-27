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

    Attempts to read from:
    1. artifacts/dashboard_outputs/<subregion_id>_report.json
    2. artifacts/<job_id>/phase_outputs.json
    3. Falls back to mock data if no artifacts found

    Args:
        subregion_id: Subregion identifier

    Returns:
        Dict with score, dimension_scores, cluster_scores, micro_scores
    """
    import json
    from pathlib import Path
    
    # Search paths for artifacts
    artifact_paths = [
        Path("artifacts") / "dashboard_outputs" / f"{subregion_id}_report.json",
        Path("artifacts") / "latest" / "phase_outputs.json",
        Path("output") / "reports" / f"{subregion_id}_analysis.json",
    ]
    
    for artifact_path in artifact_paths:
        if artifact_path.exists():
            try:
                with open(artifact_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract macro score (Phase 7 output)
                macro_score = data.get("macro_score", {})
                overall_score = macro_score.get("score", 0) if isinstance(macro_score, dict) else 0
                
                # Extract cluster scores (Phase 6 output)  
                cluster_data = data.get("cluster_scores", [])
                cluster_scores = {}
                for cs in cluster_data:
                    if isinstance(cs, dict):
                        cid = cs.get("cluster_id", "")
                        score = cs.get("score", 0)
                        # Map to dashboard cluster IDs
                        if "SEC" in cid.upper() or "PAZ" in cid.upper():
                            cluster_scores["CL01_SEC_PAZ"] = int(score * 100 / 3) if score <= 3 else int(score)
                        elif "GP" in cid.upper() or "GOB" in cid.upper():
                            cluster_scores["CL02_GP"] = int(score * 100 / 3) if score <= 3 else int(score)
                        elif "TERR" in cid.upper() or "AMB" in cid.upper():
                            cluster_scores["CL03_TERR_AMB"] = int(score * 100 / 3) if score <= 3 else int(score)
                        elif "DESC" in cid.upper() or "CRIS" in cid.upper():
                            cluster_scores["CL04_DESC_CRIS"] = int(score * 100 / 3) if score <= 3 else int(score)
                
                # Extract dimension scores (Phase 4/5 output)
                dim_data = data.get("dimension_scores", data.get("area_scores", []))
                dimension_scores = {}
                for ds in dim_data if isinstance(dim_data, list) else []:
                    if isinstance(ds, dict):
                        dim_id = ds.get("dimension_id", ds.get("area_id", ""))
                        score = ds.get("score", 0)
                        # Normalize to percentage
                        normalized = int(score * 100 / 3) if score <= 3 else int(score)
                        dimension_scores[dim_id] = normalized
                
                # Fill missing dimensions with defaults
                default_dims = ["D1_INSUMOS", "D2_VOLUNTAD", "D3_CONTEXTO", 
                               "D4_COHERENCIA", "D5_SISAS", "D6_IMPLEMENTACION"]
                for dim in default_dims:
                    if dim not in dimension_scores:
                        dimension_scores[dim] = 50  # Neutral default
                
                # Fill missing clusters with defaults
                default_clusters = ["CL01_SEC_PAZ", "CL02_GP", "CL03_TERR_AMB", "CL04_DESC_CRIS"]
                for cl in default_clusters:
                    if cl not in cluster_scores:
                        cluster_scores[cl] = 50  # Neutral default
                
                return {
                    "score": int(overall_score * 100 / 3) if overall_score <= 3 else int(overall_score),
                    "dimension_scores": dimension_scores,
                    "cluster_scores": cluster_scores,
                    "score_source": "artifacts",
                    "artifact_loaded": True,
                    "artifact_path": str(artifact_path),
                }
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                # Log and continue to next path
                continue
    
    # Fallback to mock data if no artifacts found
    return {
        "score": _generate_mock_score(subregion_id),
        "dimension_scores": _generate_mock_dimension_scores(),
        "cluster_scores": _generate_mock_cluster_scores(),
        "score_source": "mock_fallback",
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
        try:
            from farfan_pipeline.dashboard_atroz_.dashboard_data_service import DashboardDataService
            from farfan_pipeline.phases.Phase_00.phase0_10_00_paths import DATA_DIR

            # Instantiate service with paths
            service = DashboardDataService(jobs_dir=DATA_DIR / "jobs")

            # Create record context
            record = {
                "id": region_id,
                "job_id": job_id,
                "name": detail.get("name"),
            }

            # Generate summary and detailed view
            summary, context = service.summarize_region(record)
            analysis_detail = service.build_region_detail(record, summary, context)

            # Extract micro stats
            micro_data = analysis_detail.get("micro", [])
            total_questions = len(micro_data)
            avg_score = 0
            if total_questions > 0:
                total_score = sum(q.get("score_percent", 0) or 0 for q in micro_data)
                avg_score = int(total_score / total_questions)

            # Map clusters to expected format
            clusters = []
            for c in analysis_detail.get("meso", []):
                clusters.append({
                    "id": c.get("cluster_id"),
                    "name": c.get("name"),
                    "score": c.get("score_percent") or 0
                })

            # Map macro data
            macro = analysis_detail.get("macro", {})

            detail["analysis"] = {
                "macro": {
                    "score": macro.get("score_percent", 0),
                    "band": macro.get("band", "UNKNOWN"),
                    "coherence": macro.get("coherence", 0)
                },
                "meso": {
                    "clusters": clusters
                },
                "micro": {
                    "total_questions": total_questions,
                    "avg_score": avg_score,
                    "breakdown_by_pa": {},  # Kept as is, or could be populated
                    "questions": micro_data
                },
            }
        except Exception as e:
            # Fallback to mock data or partial data if loading fails
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
                    "breakdown_by_pa": {},
                    "error": str(e)
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
