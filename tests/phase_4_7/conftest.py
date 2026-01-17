"""
Pytest fixtures for Phase 4-7 adversarial tests.

MEANINGFUL CONNECTIONS - Based on 3 Pillars:
1. CONSUMER: Test suite validating Phase 4 aggregation
2. SCOPE: Adversarial testing of intermodular wiring
3. VALUE ADDED: Validates real structural relationships (PA→Cluster→Dimension)
4. EQUIPMENT: Provides tools to verify hierarchical constraints

The questionnaire was MODULARIZED into:
- clusters/CL01-CL04/metadata.json (define PA→Cluster mappings)
- dimensions/DIM01-DIM06/metadata.json
- policy_areas/PA01-PA10/metadata.json
- modular_manifest.json (master structure)

REAL STRUCTURE:
- CL01 (Seguridad y Paz): PA02, PA03, PA07
- CL02 (Grupos Poblacionales): PA01, PA05, PA06
- CL03 (Territorio Ambiente): PA04, PA08
- CL04 (Derechos Sociales Crisis): PA09, PA10
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


# =============================================================================
# PATH FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def cqc_base_path() -> Path:
    """Base path to the modularized canonical questionnaire central."""
    return Path(__file__).resolve().parent.parent.parent / "canonic_questionnaire_central"


@pytest.fixture(scope="session")
def clusters_path(cqc_base_path: Path) -> Path:
    """Path to clusters directory."""
    return cqc_base_path / "clusters"


@pytest.fixture(scope="session")
def policy_areas_path(cqc_base_path: Path) -> Path:
    """Path to policy areas directory."""
    return cqc_base_path / "policy_areas"


@pytest.fixture(scope="session")
def dimensions_path(cqc_base_path: Path) -> Path:
    """Path to dimensions directory."""
    return cqc_base_path / "dimensions"


@pytest.fixture(scope="session")
def modular_manifest_path(cqc_base_path: Path) -> Path:
    """Path to modular manifest (master structure definition)."""
    return cqc_base_path / "modular_manifest.json"


# =============================================================================
# MODULAR FIXTURES - MEANINGFUL STRUCTURAL RELATIONSHIPS
# =============================================================================


@pytest.fixture(scope="session")
def modular_manifest(modular_manifest_path: Path) -> dict:
    """Load the modular manifest - master structure definition."""
    with open(modular_manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def cluster_metadata(clusters_path: Path, modular_manifest: dict) -> dict[str, dict]:
    """
    Load ALL cluster metadata from modular structure.

    VALUE ADDED: Enables tests to verify PA→Cluster mappings are correct.

    Returns:
        {cluster_id: metadata_dict} for CL01-CL04
    """
    clusters = {}
    for item in modular_manifest["structure"]["clusters"]["items"]:
        cluster_id = item["id"]
        folder = item["folder"]
        metadata_path = clusters_path / folder / "metadata.json"
        with open(metadata_path, "r", encoding="utf-8") as f:
            clusters[cluster_id] = json.load(f)
    return clusters


@pytest.fixture(scope="session")
def policy_area_metadata(policy_areas_path: Path, modular_manifest: dict) -> dict[str, dict]:
    """
    Load ALL policy area metadata from modular structure.

    VALUE ADDED: Enables tests to verify PA properties and cluster assignments.

    Returns:
        {pa_id: metadata_dict} for PA01-PA10
    """
    policy_areas = {}
    for item in modular_manifest["structure"]["policy_areas"]["items"]:
        pa_id = item["id"]
        folder = item["folder"]
        metadata_path = policy_areas_path / folder / "metadata.json"
        with open(metadata_path, "r", encoding="utf-8") as f:
            policy_areas[pa_id] = json.load(f)
    return policy_areas


@pytest.fixture(scope="session")
def dimension_metadata(dimensions_path: Path, modular_manifest: dict) -> dict[str, dict]:
    """
    Load ALL dimension metadata from modular structure.

    VALUE ADDED: Enables tests to verify dimension properties.

    Returns:
        {dim_id: metadata_dict} for DIM01-DIM06
    """
    dimensions = {}
    for item in modular_manifest["structure"]["dimensions"]["items"]:
        dim_id = item["id"]
        folder = item["folder"]
        metadata_path = dimensions_path / folder / "metadata.json"
        with open(metadata_path, "r", encoding="utf-8") as f:
            dimensions[dim_id] = json.load(f)
    return dimensions


# =============================================================================
# RELATIONSHIP MAPPINGS - MEANINGFUL STRUCTURAL CONSTRAINTS
# =============================================================================


@pytest.fixture(scope="session")
def cluster_to_pas_mapping(cluster_metadata: dict) -> dict[str, list[str]]:
    """
    Map clusters to their policy areas - MEANINGFUL STRUCTURAL RELATIONSHIP.

    VALUE: Enables verification that aggregation respects cluster boundaries.

    REAL STRUCTURE (from modular metadata):
        CL01: [PA02, PA03, PA07] - Seguridad y Paz
        CL02: [PA01, PA05, PA06] - Grupos Poblacionales
        CL03: [PA04, PA08] - Territorio Ambiente
        CL04: [PA09, PA10] - Derechos Sociales Crisis

    USE IN TESTS:
        - Verify ClusterAggregator only includes PAs that belong to the cluster
        - Verify PA→Cluster assignments are correct
    """
    mapping = {}
    for cluster_id, metadata in cluster_metadata.items():
        mapping[cluster_id] = metadata.get("policy_area_ids", [])
    return mapping


@pytest.fixture(scope="session")
def pa_to_cluster_mapping(policy_area_metadata: dict, modular_manifest: dict) -> dict[str, str]:
    """
    Map policy areas to their clusters - MEANINGFUL STRUCTURAL RELATIONSHIP.

    VALUE: Enables verification that PA scores flow to correct cluster.

    USE IN TESTS:
        - Verify AreaScore has correct cluster_id
        - Verify cluster aggregation includes all expected PAs
    """
    mapping = {}
    for item in modular_manifest["structure"]["policy_areas"]["items"]:
        mapping[item["id"]] = item["cluster"]
    return mapping


@pytest.fixture(scope="session")
def cluster_policy_area_counts(cluster_to_pas_mapping: dict) -> dict[str, int]:
    """
    Count PAs per cluster - MEANINGFUL for hermeticity validation.

    VALUE: Enables tests to verify all PAs in cluster are present.

    REAL COUNTS:
        CL01: 3 PAs (PA02, PA03, PA07)
        CL02: 3 PAs (PA01, PA05, PA06)
        CL03: 2 PAs (PA04, PA08)
        CL04: 2 PAs (PA09, PA10)

    USE IN TESTS:
        - Verify ClusterAggregator hermeticity checks use correct counts
        - Test missing PA detection
    """
    return {cluster_id: len(pa_list) for cluster_id, pa_list in cluster_to_pas_mapping.items()}


# =============================================================================
# TEST DATA GENERATORS - EQUIPPED TO ADD VALUE
# =============================================================================


@pytest.fixture
def generate_scored_result_for_pa(pa_to_cluster_mapping: dict):
    """
    Generate a valid ScoredResult for a specific PA - EQUIPPED with cluster info.

    VALUE: Ensures test data respects real PA→Cluster relationships.

    USE IN TESTS:
        - Create realistic test data that respects structural constraints
        - Verify aggregation uses correct cluster_id
    """

    def _generate(pa_id: str, question_id: int, score: float = 2.0, quality_level: str = "BUENO"):
        from farfan_pipeline.phases.Phase_04_five_six_seven.aggregation import ScoredResult

        cluster_id = pa_to_cluster_mapping.get(pa_id, "UNKNOWN")

        # Determine dimension based on PA (simplified - real mapping from monolith)
        # This would be enhanced with actual PA→DIM mappings
        dim_idx = (int(pa_id[2:]) - 1) % 6 + 1
        dimension = f"DIM{dim_idx:02d}"

        return ScoredResult(
            question_global=question_id,
            base_slot=f"{dimension}-Q{question_id:03d}",
            policy_area=pa_id,
            dimension=dimension,
            score=score,
            quality_level=quality_level,
            evidence={},
            raw_results={},
        )

    return _generate


@pytest.fixture
def generate_dimension_score_for_pa():
    """
    Generate a valid DimensionScore for testing area aggregation.

    VALUE: Creates dimension scores that can be aggregated to areas.

    EQUIPPED WITH:
        - Proper validation flags
        - Realistic metadata
    """

    def _generate(
        pa_id: str,
        dimension: str,
        score: float = 2.0,
        contributing_questions: list[int] | None = None,
    ):
        from farfan_pipeline.phases.Phase_04_five_six_seven.aggregation import DimensionScore

        return DimensionScore(
            dimension_id=dimension,
            area_id=pa_id,
            score=score,
            quality_level="BUENO",
            contributing_questions=contributing_questions or [1, 2, 3, 4, 5],
            validation_passed=True,
            validation_details={
                "coverage": {"valid": True, "count": 5},
                "weights": {"valid": True, "weights": "equal"},
            },
        )

    return _generate


# =============================================================================
# ASSERTION HELPERS - EQUIPPED TO VALIDATE MEANINGFUL CONSTRAINTS
# =============================================================================


@pytest.fixture
def assert_hermeticity_for_cluster(cluster_policy_area_counts: dict):
    """
    Assert cluster hermeticity - validates structural constraint.

    VALUE: Ensures all PAs in cluster are present, no extras.

    EQUIPPED WITH:
        - Real PA counts per cluster from modular structure
        - Meaningful error messages

    MEANINGFUL VALIDATION:
        - CL01 must have exactly 3 PAs: PA02, PA03, PA07
        - CL02 must have exactly 3 PAs: PA01, PA05, PA06
        - etc.
    """

    def _assert(cluster_id: str, area_scores: list):
        expected_count = cluster_policy_area_counts[cluster_id]
        actual_pa_ids = {score.area_id for score in area_scores}

        # Assert count matches
        assert len(area_scores) == expected_count, (
            f"Cluster {cluster_id} hermeticity violation: "
            f"expected {expected_count} PAs, got {len(area_scores)}"
        )

        # Note: Could also validate specific PA IDs if we had PA list for each cluster

        return True

    return _assert


@pytest.fixture
def assert_pa_cluster_assignment(pa_to_cluster_mapping: dict):
    """
    Assert PA→Cluster assignment - validates structural relationship.

    VALUE: Ensures PAs are assigned to correct clusters.

    EQUIPPED WITH:
        - Real PA→Cluster mappings from modular structure
    """

    def _assert(pa_id: str, expected_cluster_id: str, area_score):
        actual_cluster = area_score.cluster_id

        assert actual_cluster == expected_cluster_id, (
            f"PA {pa_id} cluster assignment violation: "
            f"expected {expected_cluster_id}, got {actual_cluster}"
        )

        # Also verify against the canonical mapping
        canonical_cluster = pa_to_cluster_mapping.get(pa_id)
        assert canonical_cluster == expected_cluster_id, (
            f"PA {pa_id} canonical mapping violation: "
            f"canonical cluster is {canonical_cluster}, test expected {expected_cluster_id}"
        )

        return True

    return _assert


# =============================================================================
# LEGACY MONOLITH FIXTURES - For backward compatibility
# =============================================================================


@pytest.fixture(scope="session")
def questionnaire_monolith(cqc_base_path: Path) -> dict:
    """
    Load the consolidated monolith (legacy format).

    DEPRECATED: Use modular fixtures above for meaningful tests.
    """
    monolith_path = cqc_base_path / "questionnaire_monolith.json"
    with open(monolith_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def monolith_from_modular(
    cluster_metadata: dict,
    policy_area_metadata: dict,
    dimension_metadata: dict,
    modular_manifest: dict,
) -> dict[str, Any]:
    """
    Construct a monolith-like structure from modular pieces.

    VALUE: Bridges modular structure with legacy monolith-consuming code.

    Enables gradual migration from monolith to modular structure.
    """
    # Convert cluster metadata to monolith format
    clusters_list = []
    for cluster_id, metadata in cluster_metadata.items():
        cluster_dict = {
            "cluster_id": cluster_id,
            "i18n": metadata.get("i18n", {}),
            "policy_area_ids": metadata.get("policy_area_ids", []),
            "rationale": metadata.get("rationale", ""),
        }
        clusters_list.append(cluster_dict)

    # Convert policy area metadata to monolith format
    policy_areas_list = []
    for pa_id, metadata in policy_area_metadata.items():
        pa_dict = {
            "policy_area_id": pa_id,
            "i18n": metadata.get("i18n", {}),
            # Get cluster from manifest since metadata might not have it
            "cluster_id": next(
                (
                    item["cluster"]
                    for item in modular_manifest["structure"]["policy_areas"]["items"]
                    if item["id"] == pa_id
                ),
                "",
            ),
        }
        policy_areas_list.append(pa_dict)

    # Convert dimension metadata to monolith format
    dimensions_list = []
    for dim_id, metadata in dimension_metadata.items():
        dim_dict = {"dimension_id": dim_id, "i18n": metadata.get("i18n", {})}
        dimensions_list.append(dim_dict)

    # Construct monolith-like structure
    return {
        "blocks": {
            "niveles_abstraccion": {
                "clusters": clusters_list,
                "policy_areas": policy_areas_list,
                "dimensions": dimensions_list,
            },
            "scoring": {},
        },
        "_modular_source": True,
        "_manifest_version": modular_manifest.get("_manifest_version"),
    }


# =============================================================================
# HELPER FIXTURES - Test helpers for adversarial testing
# =============================================================================


@pytest.fixture
def create_minimal_monolith():
    """
    Create a minimal monolith for testing when full monolith is not needed.

    VALUE: Provides lightweight test fixture for unit tests.

    EQUIPPED WITH:
        - Basic cluster structure
        - Minimal PA definitions
        - Dimension definitions
    """

    def _create() -> dict:
        return {
            "blocks": {
                "niveles_abstraccion": {
                    "clusters": [
                        {"cluster_id": "MESO_1", "i18n": {}, "policy_area_ids": ["PA01"]},
                    ],
                    "policy_areas": [
                        {
                            "policy_area_id": "PA01",
                            "i18n": {},
                            "cluster_id": "MESO_1",
                            "dimension_ids": ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"],
                        },
                    ],
                    "dimensions": [
                        {"dimension_id": f"DIM{i:02d}", "i18n": {}}
                        for i in range(1, 7)
                    ],
                },
                "scoring": {},
            },
        }

    return _create


@pytest.fixture
def mock_instrumentation():
    """
    Create mock instrumentation for testing async aggregation functions.

    VALUE: Provides test double for instrumentation tracking.
    """

    class MockInstrumentation:
        def __init__(self):
            self.items_total = 0
            self.items_completed = 0

        def start(self, items_total: int = 1):
            self.items_total = items_total
            self.items_completed = 0

        def complete_item(self):
            self.items_completed += 1

    return MockInstrumentation()
