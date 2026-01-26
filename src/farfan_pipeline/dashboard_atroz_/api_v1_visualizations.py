"""Enhanced Visualization Endpoints - Phylogram, Mesh, Helix
Integrates with Phase 4, 5, and 7 pipeline data structures.
"""

from pathlib import Path
from typing import Any
import json
import structlog

logger = structlog.get_logger(__name__)

# Phase output directories (from Phase_XX/PHASE_X_CONSTANTS.py pattern)
PHASE_04_OUTPUT = Path("dashboard_outputs/phase_04")
PHASE_05_OUTPUT = Path("dashboard_outputs/phase_05")
PHASE_07_OUTPUT = Path("dashboard_outputs/phase_07")


class PhylogramBuilder:
    """Builds Phase 4 Dimension DAG visualization.

    Shows micro-question → dimension score provenance and Choquet integral
    decomposition when SOTA scoring is enabled.
    """

    def __init__(self, region_id: str):
        self.region_id = region_id

    async def build(self) -> dict[str, Any]:
        """Build phylogram visualization data.

        Returns:
            {
                "regionId": str,
                "type": "phylogram",
                "dag": {
                    "nodes": [
                        {
                            "id": "Q001",
                            "type": "micro",  # micro | dimension
                            "label": "Question text",
                            "score": 0.75,
                            "dimension": "D1",
                            "level": 0  # 0=leaf (micro), 1=dimension
                        }
                    ],
                    "edges": [
                        {
                            "from": "Q001",
                            "to": "D1",
                            "weight": 0.15,  # Choquet contribution
                            "aggregation": "choquet"  # choquet | weighted_avg
                        }
                    ]
                },
                "dimensions": {
                    "D1": {"score": 0.78, "name": "INSUMOS", "questionCount": 50},
                    "D2": {"score": 0.71, "name": "VOLUNTAD", "questionCount": 50},
                    "D3": {"score": 0.68, "name": "CONTEXTO", "questionCount": 50},
                    "D4": {"score": 0.72, "name": "COHERENCIA", "questionCount": 50},
                    "D5": {"score": 0.65, "name": "SISAS", "questionCount": 50},
                    "D6": {"score": 0.73, "name": "IMPLEMENTACIÓN", "questionCount": 50}
                },
                "metadata": {
                    "totalQuestions": 300,
                    "aggregationMethod": "choquet",
                    "timestamp": "2024-01-21T..."
                }
            }
        """
        # Try to load from Phase 4 output
        phase4_file = PHASE_04_OUTPUT / self.region_id / "dimension_aggregation.json"

        if phase4_file.exists():
            with open(phase4_file) as f:
                data = json.load(f)
            return self._transform_phase4_output(data)

        # Fallback to mock structure for demonstration
        return self._build_mock_phylogram()

    def _transform_phase4_output(self, phase4_data: dict) -> dict[str, Any]:
        """Transform Phase 4 output to phylogram format."""
        nodes = []
        edges = []

        # Add dimension nodes (level 1)
        dimensions = {}
        for dim_id, dim_data in phase4_data.get("dimensions", {}).items():
            nodes.append({
                "id": dim_id,
                "type": "dimension",
                "label": dim_data.get("name", dim_id),
                "score": dim_data.get("score", 0),
                "dimension": dim_id,
                "level": 1
            })
            dimensions[dim_id] = {
                "score": dim_data.get("score", 0),
                "name": dim_data.get("name", dim_id),
                "questionCount": len(dim_data.get("questions", []))
            }

        # Add micro question nodes (level 0) and edges
        for question in phase4_data.get("questions", []):
            q_id = question.get("id")
            dim_id = question.get("dimension")

            nodes.append({
                "id": q_id,
                "type": "micro",
                "label": question.get("text", "")[:50] + "...",
                "score": question.get("score", 0),
                "dimension": dim_id,
                "level": 0
            })

            # Add edge showing aggregation contribution
            edges.append({
                "from": q_id,
                "to": dim_id,
                "weight": question.get("choquet_contribution", question.get("score", 0) / 50),
                "aggregation": phase4_data.get("aggregation_method", "weighted_avg")
            })

        return {
            "regionId": self.region_id,
            "type": "phylogram",
            "dag": {"nodes": nodes, "edges": edges},
            "dimensions": dimensions,
            "metadata": {
                "totalQuestions": len(phase4_data.get("questions", [])),
                "aggregationMethod": phase4_data.get("aggregation_method", "weighted_avg"),
                "timestamp": phase4_data.get("timestamp", ""),
                "source": "phase_04_output"
            }
        }

    def _build_mock_phylogram(self) -> dict[str, Any]:
        """Build mock phylogram for demonstration."""
        nodes = []
        edges = []

        # 6 dimensions
        dim_info = {
            "D1": {"name": "INSUMOS", "score": 0.78},
            "D2": {"name": "VOLUNTAD", "score": 0.71},
            "D3": {"name": "CONTEXTO", "score": 0.68},
            "D4": {"name": "COHERENCIA", "score": 0.72},
            "D5": {"name": "SISAS", "score": 0.65},
            "D6": {"name": "IMPLEMENTACIÓN", "score": 0.73}
        }

        dimensions = {}
        for dim_id, info in dim_info.items():
            nodes.append({
                "id": dim_id,
                "type": "dimension",
                "label": info["name"],
                "score": info["score"],
                "dimension": dim_id,
                "level": 1
            })
            dimensions[dim_id] = {
                "score": info["score"],
                "name": info["name"],
                "questionCount": 50
            }

        # Sample of 10 micro questions per dimension (300 total)
        for dim_num in range(1, 7):
            dim_id = f"D{dim_num}"
            for q_num in range(1, 11):  # 10 sample questions
                q_id = f"Q{(dim_num-1)*50 + q_num:03d}"
                nodes.append({
                    "id": q_id,
                    "type": "micro",
                    "label": f"Question {q_id}: Sample question text...",
                    "score": 0.6 + (q_num * 0.03),
                    "dimension": dim_id,
                    "level": 0
                })

                edges.append({
                    "from": q_id,
                    "to": dim_id,
                    "weight": 0.02,  # 1/50 contribution
                    "aggregation": "weighted_avg"
                })

        return {
            "regionId": self.region_id,
            "type": "phylogram",
            "dag": {"nodes": nodes, "edges": edges},
            "dimensions": dimensions,
            "metadata": {
                "totalQuestions": 300,
                "aggregationMethod": "weighted_avg",
                "timestamp": "2024-01-21T00:00:00Z",
                "source": "mock_data"
            }
        }


class MeshBuilder:
    """Builds Phase 5 Policy Area Clustering Topology.

    Displays MESO-level cluster topology showing policy area groupings.
    """

    def __init__(self, region_id: str):
        self.region_id = region_id

    async def build(self) -> dict[str, Any]:
        """Build mesh visualization data.

        Returns:
            {
                "regionId": str,
                "type": "mesh",
                "clusters": [
                    {
                        "id": "CL01",
                        "name": "SEC_PAZ",
                        "description": "Seguridad y Paz",
                        "score": 0.72,
                        "policyAreas": ["PA01", "PA02", "PA08"],
                        "cohesion": 0.85,  # Within-cluster similarity
                        "dispersion": 0.12  # Variance
                    }
                ],
                "policyAreas": {
                    "PA01": {
                        "name": "Derechos de Género",
                        "cluster": "CL01",
                        "score": 0.78,
                        "questionCount": 30
                    }
                },
                "edges": [
                    {
                        "from": "CL01",
                        "to": "CL02",
                        "strength": 0.65,  # Inter-cluster correlation
                        "type": "correlation"
                    }
                ],
                "metadata": {
                    "clusteringMethod": "hierarchical",
                    "timestamp": "..."
                }
            }
        """
        phase5_file = PHASE_05_OUTPUT / self.region_id / "cluster_topology.json"

        if phase5_file.exists():
            with open(phase5_file) as f:
                data = json.load(f)
            return self._transform_phase5_output(data)

        return self._build_mock_mesh()

    def _transform_phase5_output(self, phase5_data: dict) -> dict[str, Any]:
        """Transform Phase 5 output to mesh format."""
        clusters = []
        policy_areas = {}
        edges = []

        for cluster in phase5_data.get("clusters", []):
            clusters.append({
                "id": cluster["id"],
                "name": cluster["name"],
                "description": cluster.get("description", ""),
                "score": cluster.get("score", 0),
                "policyAreas": cluster.get("policy_areas", []),
                "cohesion": cluster.get("cohesion", 0),
                "dispersion": cluster.get("dispersion", 0)
            })

        for pa_id, pa_data in phase5_data.get("policy_areas", {}).items():
            policy_areas[pa_id] = {
                "name": pa_data.get("name", ""),
                "cluster": pa_data.get("cluster", ""),
                "score": pa_data.get("score", 0),
                "questionCount": pa_data.get("question_count", 30)
            }

        # Inter-cluster correlations
        for edge in phase5_data.get("correlations", []):
            edges.append({
                "from": edge["from"],
                "to": edge["to"],
                "strength": edge.get("correlation", 0),
                "type": "correlation"
            })

        return {
            "regionId": self.region_id,
            "type": "mesh",
            "clusters": clusters,
            "policyAreas": policy_areas,
            "edges": edges,
            "metadata": {
                "clusteringMethod": phase5_data.get("method", "hierarchical"),
                "timestamp": phase5_data.get("timestamp", ""),
                "source": "phase_05_output"
            }
        }

    def _build_mock_mesh(self) -> dict[str, Any]:
        """Build mock mesh for demonstration."""
        clusters = [
            {
                "id": "CL01",
                "name": "SEC_PAZ",
                "description": "Seguridad y Paz",
                "score": 0.72,
                "policyAreas": ["PA01", "PA02", "PA08"],
                "cohesion": 0.85,
                "dispersion": 0.12
            },
            {
                "id": "CL02",
                "name": "GP",
                "description": "Gestión Pública",
                "score": 0.68,
                "policyAreas": ["PA04", "PA06"],
                "cohesion": 0.78,
                "dispersion": 0.15
            },
            {
                "id": "CL03",
                "name": "TERR_AMB",
                "description": "Territorio y Ambiente",
                "score": 0.65,
                "policyAreas": ["PA03", "PA07"],
                "cohesion": 0.82,
                "dispersion": 0.13
            },
            {
                "id": "CL04",
                "name": "DESC_CRIS",
                "description": "Desconfianza y Crisis",
                "score": 0.45,
                "policyAreas": ["PA05", "PA09", "PA10"],
                "cohesion": 0.71,
                "dispersion": 0.18
            }
        ]

        policy_areas = {
            "PA01": {"name": "Derechos de Género", "cluster": "CL01", "score": 0.78, "questionCount": 30},
            "PA02": {"name": "Prevención de Violencias", "cluster": "CL01", "score": 0.75, "questionCount": 30},
            "PA03": {"name": "Medio Ambiente", "cluster": "CL03", "score": 0.68, "questionCount": 30},
            "PA04": {"name": "Derechos Económicos", "cluster": "CL02", "score": 0.65, "questionCount": 30},
            "PA05": {"name": "Derechos de Víctimas", "cluster": "CL04", "score": 0.82, "questionCount": 30},
            "PA06": {"name": "Niñez y Juventud", "cluster": "CL02", "score": 0.71, "questionCount": 30},
            "PA07": {"name": "Tierra y Territorio", "cluster": "CL03", "score": 0.62, "questionCount": 30},
            "PA08": {"name": "Defensores DDHH", "cluster": "CL01", "score": 0.64, "questionCount": 30},
            "PA09": {"name": "Crisis Carcelaria", "cluster": "CL04", "score": 0.38, "questionCount": 30},
            "PA10": {"name": "Migración", "cluster": "CL04", "score": 0.55, "questionCount": 30}
        }

        edges = [
            {"from": "CL01", "to": "CL02", "strength": 0.65, "type": "correlation"},
            {"from": "CL01", "to": "CL03", "strength": 0.58, "type": "correlation"},
            {"from": "CL02", "to": "CL03", "strength": 0.72, "type": "correlation"},
            {"from": "CL03", "to": "CL04", "strength": 0.45, "type": "correlation"},
            {"from": "CL01", "to": "CL04", "strength": 0.52, "type": "correlation"},
            {"from": "CL02", "to": "CL04", "strength": 0.48, "type": "correlation"}
        ]

        return {
            "regionId": self.region_id,
            "type": "mesh",
            "clusters": clusters,
            "policyAreas": policy_areas,
            "edges": edges,
            "metadata": {
                "clusteringMethod": "hierarchical",
                "timestamp": "2024-01-21T00:00:00Z",
                "source": "mock_data"
            }
        }


class HelixBuilder:
    """Builds Phase 7 Coherence Metrics Triple Helix.

    Displays macro-level coherence analysis across strategic, operational,
    and institutional dimensions.
    """

    def __init__(self, region_id: str):
        self.region_id = region_id

    async def build(self) -> dict[str, Any]:
        """Build helix visualization data.

        Returns:
            {
                "regionId": str,
                "type": "helix",
                "strands": [
                    {
                        "type": "strategic",
                        "label": "Coherencia Estratégica",
                        "score": 0.78,
                        "points": [
                            {"dimension": "D1", "value": 0.82, "variance": 0.05},
                            {"dimension": "D2", "value": 0.75, "variance": 0.08},
                            ...
                        ],
                        "method": "variance_based"
                    },
                    {
                        "type": "operational",
                        "label": "Coherencia Operacional",
                        "score": 0.72,
                        "points": [...],
                        "method": "pairwise_similarity"
                    },
                    {
                        "type": "institutional",
                        "label": "Coherencia Institucional",
                        "score": 0.68,
                        "points": [...],
                        "method": "entity_alignment"
                    }
                ],
                "overall": {
                    "coherenceScore": 0.73,
                    "alignment": 0.85,  # Strand correlation
                    "gaps": [
                        {"dimension": "D5", "severity": "high", "gap": 0.25}
                    ]
                },
                "metadata": {
                    "analysisMethod": "triple_helix",
                    "timestamp": "..."
                }
            }
        """
        phase7_file = PHASE_07_OUTPUT / self.region_id / "coherence_analysis.json"

        if phase7_file.exists():
            with open(phase7_file) as f:
                data = json.load(f)
            return self._transform_phase7_output(data)

        return self._build_mock_helix()

    def _transform_phase7_output(self, phase7_data: dict) -> dict[str, Any]:
        """Transform Phase 7 output to helix format."""
        strands = []

        for strand_type in ["strategic", "operational", "institutional"]:
            strand_data = phase7_data.get(f"{strand_type}_coherence", {})
            strands.append({
                "type": strand_type,
                "label": strand_data.get("label", f"Coherencia {strand_type.title()}"),
                "score": strand_data.get("score", 0),
                "points": strand_data.get("dimensions", []),
                "method": strand_data.get("method", "")
            })

        gaps = []
        for gap in phase7_data.get("gaps", []):
            gaps.append({
                "dimension": gap["dimension"],
                "severity": gap.get("severity", "medium"),
                "gap": gap.get("gap_size", 0)
            })

        return {
            "regionId": self.region_id,
            "type": "helix",
            "strands": strands,
            "overall": {
                "coherenceScore": phase7_data.get("overall_coherence", 0),
                "alignment": phase7_data.get("strand_alignment", 0),
                "gaps": gaps
            },
            "metadata": {
                "analysisMethod": "triple_helix",
                "timestamp": phase7_data.get("timestamp", ""),
                "source": "phase_07_output"
            }
        }

    def _build_mock_helix(self) -> dict[str, Any]:
        """Build mock helix for demonstration."""
        dimensions = ["D1", "D2", "D3", "D4", "D5", "D6"]

        strands = [
            {
                "type": "strategic",
                "label": "Coherencia Estratégica",
                "score": 0.78,
                "points": [
                    {"dimension": dim, "value": 0.75 + (i * 0.02), "variance": 0.05 + (i * 0.01)}
                    for i, dim in enumerate(dimensions)
                ],
                "method": "variance_based"
            },
            {
                "type": "operational",
                "label": "Coherencia Operacional",
                "score": 0.72,
                "points": [
                    {"dimension": dim, "value": 0.70 + (i * 0.03), "variance": 0.08}
                    for i, dim in enumerate(dimensions)
                ],
                "method": "pairwise_similarity"
            },
            {
                "type": "institutional",
                "label": "Coherencia Institucional",
                "score": 0.68,
                "points": [
                    {"dimension": dim, "value": 0.65 + (i * 0.025), "variance": 0.10}
                    for i, dim in enumerate(dimensions)
                ],
                "method": "entity_alignment"
            }
        ]

        gaps = [
            {"dimension": "D5", "severity": "high", "gap": 0.25},
            {"dimension": "D4", "severity": "medium", "gap": 0.15},
            {"dimension": "D3", "severity": "low", "gap": 0.08}
        ]

        return {
            "regionId": self.region_id,
            "type": "helix",
            "strands": strands,
            "overall": {
                "coherenceScore": 0.73,
                "alignment": 0.85,
                "gaps": gaps
            },
            "metadata": {
                "analysisMethod": "triple_helix",
                "timestamp": "2024-01-21T00:00:00Z",
                "source": "mock_data"
            }
        }
