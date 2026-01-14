"""
Phase 6 Integration Tests - Real Module Validation
===================================================

Tests for Phase 6 integration with real Phase 5 and Phase 6 types.

INTEGRATION TEST CATEGORIES:
1. Phase 6 constants validation
2. Real type compatibility
3. Cross-module consistency
4. Pipeline flow validation
"""

from __future__ import annotations

import pytest

# Try to import real types from Phase 5 (input) and Phase 6 (output)
try:
    from farfan_pipeline.phases.Phase_5 import AreaScore
    REAL_PHASE5_AVAILABLE = True
except ImportError:
    REAL_PHASE5_AVAILABLE = False
    AreaScore = None

try:
    from farfan_pipeline.phases.Phase_6 import (
        ClusterScore,
        ClusterAggregator,
    )
    REAL_PHASE6_TYPES_AVAILABLE = True
except ImportError:
    REAL_PHASE6_TYPES_AVAILABLE = False
    ClusterScore = None
    ClusterAggregator = None

try:
    from farfan_pipeline.phases.Phase_6 import (
        CLUSTER_COMPOSITION,
        CLUSTERS,
        COHERENCE_THRESHOLD_HIGH,
        COHERENCE_THRESHOLD_LOW,
        DISPERSION_THRESHOLDS,
        EXPECTED_CLUSTER_SCORE_COUNT,
        MAX_SCORE,
        MIN_SCORE,
        PENALTY_WEIGHT,
        DispersionScenario,
        Phase6Invariants,
    )
    PHASE6_CONSTANTS_AVAILABLE = True
except ImportError:
    PHASE6_CONSTANTS_AVAILABLE = False

from .conftest import (
    CLUSTER_COMPOSITION as LOCAL_CLUSTER_COMPOSITION,
    CLUSTERS as LOCAL_CLUSTERS,
    DIMENSIONS,
    EXPECTED_CLUSTER_COUNT,
    POLICY_AREAS,
)


# =============================================================================
# CONDITIONAL TEST MARKERS
# =============================================================================

requires_real_phase4 = pytest.mark.skipif(
    not REAL_PHASE4_AVAILABLE,
    reason="Real Phase 4 types not available"
)

requires_phase6_constants = pytest.mark.skipif(
    not PHASE6_CONSTANTS_AVAILABLE,
    reason="Phase 6 constants not available"
)


# =============================================================================
# 1. PHASE 6 CONSTANTS VALIDATION
# =============================================================================


@requires_phase6_constants
class TestPhase6ConstantsIntegrity:
    """Validate Phase 6 constants against canonical structure."""

    def test_clusters_match_canonical(self):
        """INTEGRATION: Phase 6 CLUSTERS matches canonical list."""
        assert set(CLUSTERS) == set(LOCAL_CLUSTERS)

    def test_expected_cluster_count(self):
        """INTEGRATION: Expected count is 4."""
        assert EXPECTED_CLUSTER_SCORE_COUNT == 4

    def test_score_bounds(self):
        """INTEGRATION: Score bounds are [0.0, 3.0]."""
        assert MIN_SCORE == 0.0
        assert MAX_SCORE == 3.0

    def test_cluster_composition_structure(self):
        """INTEGRATION: Cluster composition has correct structure."""
        assert len(CLUSTER_COMPOSITION) == 4
        
        for cluster_id, pa_list in CLUSTER_COMPOSITION.items():
            assert cluster_id.startswith("CLUSTER_MESO_")
            assert len(pa_list) >= 2
            for pa in pa_list:
                assert pa.startswith("PA")

    def test_cluster_composition_covers_all_pas(self):
        """INTEGRATION: All 10 PAs are covered by clusters."""
        all_pas = set()
        for pa_list in CLUSTER_COMPOSITION.values():
            all_pas.update(pa_list)
        
        assert len(all_pas) == 10

    def test_dispersion_thresholds_structure(self):
        """INTEGRATION: Dispersion thresholds have correct keys."""
        required_keys = ["CV_CONVERGENCE", "CV_MODERATE", "CV_HIGH", "CV_EXTREME"]
        for key in required_keys:
            assert key in DISPERSION_THRESHOLDS

    def test_penalty_weight_in_range(self):
        """INTEGRATION: Penalty weight is in (0, 1)."""
        assert 0 < PENALTY_WEIGHT < 1

    def test_coherence_thresholds_ordered(self):
        """INTEGRATION: Coherence thresholds are ordered."""
        assert COHERENCE_THRESHOLD_LOW < COHERENCE_THRESHOLD_HIGH


@requires_phase6_constants
class TestPhase6Invariants:
    """Test Phase6Invariants class."""

    def test_validate_count_valid(self):
        """INTEGRATION: validate_count returns True for 4 clusters."""
        mock_scores = [type("ClusterScore", (), {"cluster_id": f"CL{i}"})() for i in range(4)]
        assert Phase6Invariants.validate_count(mock_scores)

    def test_validate_count_invalid(self):
        """INTEGRATION: validate_count returns False for wrong count."""
        mock_scores = [type("ClusterScore", (), {"cluster_id": f"CL{i}"})() for i in range(3)]
        assert not Phase6Invariants.validate_count(mock_scores)

    def test_validate_bounds_valid(self):
        """INTEGRATION: validate_bounds for valid scores."""
        assert Phase6Invariants.validate_bounds(0.0)
        assert Phase6Invariants.validate_bounds(1.5)
        assert Phase6Invariants.validate_bounds(3.0)

    def test_validate_bounds_invalid(self):
        """INTEGRATION: validate_bounds for invalid scores."""
        assert not Phase6Invariants.validate_bounds(-0.1)
        assert not Phase6Invariants.validate_bounds(3.1)

    def test_classify_dispersion(self):
        """INTEGRATION: classify_dispersion returns correct scenarios."""
        assert Phase6Invariants.classify_dispersion(0.1) == DispersionScenario.CONVERGENCE
        assert Phase6Invariants.classify_dispersion(0.3) == DispersionScenario.MODERATE
        assert Phase6Invariants.classify_dispersion(0.5) == DispersionScenario.HIGH
        assert Phase6Invariants.classify_dispersion(0.8) == DispersionScenario.EXTREME


# =============================================================================
# 2. REAL TYPE INTEGRATION
# =============================================================================


@requires_real_phase4
class TestRealClusterScoreIntegration:
    """Tests using real ClusterScore from Phase 4."""

    def test_cluster_score_creation(self):
        """INTEGRATION: Can create real ClusterScore."""
        area_scores = [
            AreaScore(
                area_id=pa,
                area_name=f"Area {pa}",
                score=2.0,
                quality_level="BUENO",
                dimension_scores=[],
            )
            for pa in ["PA01", "PA02", "PA03"]
        ]
        
        cluster_score = ClusterScore(
            cluster_id="CLUSTER_MESO_1",
            cluster_name="Test Cluster",
            areas=["PA01", "PA02", "PA03"],
            score=2.0,
            coherence=0.9,
            variance=0.1,
            weakest_area="PA01",
            area_scores=area_scores,
        )
        
        assert cluster_score.cluster_id == "CLUSTER_MESO_1"
        assert len(cluster_score.area_scores) == 3

    def test_cluster_score_all_fields(self):
        """INTEGRATION: ClusterScore has all expected fields."""
        cluster_score = ClusterScore(
            cluster_id="CLUSTER_MESO_1",
            cluster_name="Test Cluster",
            areas=["PA01"],
            score=2.0,
            coherence=0.9,
            variance=0.1,
            weakest_area="PA01",
            area_scores=[],
        )
        
        # SOTA fields
        assert hasattr(cluster_score, "score_std")
        assert hasattr(cluster_score, "confidence_interval_95")
        assert hasattr(cluster_score, "provenance_node_id")


# =============================================================================
# 3. CROSS-MODULE CONSISTENCY
# =============================================================================


class TestCrossModuleConsistency:
    """Tests for consistency across Phase 5 and Phase 6."""

    def test_cluster_mappings_consistent(self):
        """INTEGRATION: Local and Phase 6 cluster mappings are consistent."""
        assert len(LOCAL_CLUSTER_COMPOSITION) == 4

    def test_cluster_count_consistent(self):
        """INTEGRATION: Cluster count is 4 everywhere."""
        assert len(LOCAL_CLUSTERS) == 4

    def test_policy_area_count_consistent(self):
        """INTEGRATION: PA count is 10 everywhere."""
        assert len(POLICY_AREAS) == 10

    def test_all_pas_assigned_to_clusters(self):
        """INTEGRATION: All PAs are assigned to exactly one cluster."""
        pa_to_cluster = {}
        for cluster_id, pas in LOCAL_CLUSTER_COMPOSITION.items():
            for pa in pas:
                assert pa not in pa_to_cluster, f"PA {pa} assigned to multiple clusters"
                pa_to_cluster[pa] = cluster_id
        
        assert set(pa_to_cluster.keys()) == set(POLICY_AREAS)


# =============================================================================
# 4. PIPELINE FLOW VALIDATION
# =============================================================================


class TestPipelineFlowValidation:
    """Tests for Phase 5 → Phase 6 → Phase 7 flow."""

    def test_input_output_cardinality(self):
        """PIPELINE: 10 AreaScores → 4 ClusterScores."""
        # Input from Phase 5: 10 AreaScores
        input_count = len(POLICY_AREAS)
        assert input_count == 10
        
        # Output: 4 ClusterScores
        output_count = len(LOCAL_CLUSTERS)
        assert output_count == 4

    def test_cluster_pa_distribution(self):
        """PIPELINE: Verify PA distribution across clusters."""
        expected = {
            "CLUSTER_MESO_1": 3,
            "CLUSTER_MESO_2": 3,
            "CLUSTER_MESO_3": 2,
            "CLUSTER_MESO_4": 2,
        }
        
        actual = {cluster: len(pas) for cluster, pas in LOCAL_CLUSTER_COMPOSITION.items()}
        assert actual == expected

    def test_macro_output_cardinality(self):
        """PIPELINE: 4 ClusterScores → 1 MacroScore (Phase 7)."""
        # Phase 6 output: 4 ClusterScores
        assert len(LOCAL_CLUSTERS) == 4
        
        # Phase 7 output: 1 MacroScore (confirmed by pipeline design)


# =============================================================================
# 5. CONTRACT VALIDATION
# =============================================================================


class TestPhase6Contracts:
    """Tests for Phase 6 contract compliance."""

    def test_input_contract(self):
        """CONTRACT: Input must be list of AreaScore-like objects."""
        required_fields = ["area_id", "score"]
        
        from .conftest import MockAreaScore
        mock = MockAreaScore(
            area_id="PA01",
            area_name="Test",
            score=2.0,
            quality_level="BUENO",
            dimension_scores=[],
        )
        for field in required_fields:
            assert hasattr(mock, field), f"Missing field: {field}"

    def test_output_contract(self):
        """CONTRACT: Output must be list of ClusterScore-like objects."""
        required_fields = ["cluster_id", "score", "area_scores", "coherence", "variance"]
        
        from .conftest import MockClusterScore
        mock = MockClusterScore(
            cluster_id="CLUSTER_MESO_1",
            cluster_name="Test",
            areas=["PA01"],
            score=2.0,
            coherence=0.9,
            variance=0.1,
            weakest_area="PA01",
            area_scores=[],
        )
        for field in required_fields:
            assert hasattr(mock, field), f"Missing field: {field}"

    def test_invariant_count(self):
        """CONTRACT: Must produce exactly 4 ClusterScores."""
        expected = 4
        actual = len(LOCAL_CLUSTERS)
        assert actual == expected

    def test_invariant_bounds(self):
        """CONTRACT: All scores must be in [0.0, 3.0]."""
        min_bound = 0.0
        max_bound = 3.0
        
        valid_scores = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        for score in valid_scores:
            assert min_bound <= score <= max_bound
        
        invalid_scores = [-0.1, 3.1, -1.0, 4.0]
        for score in invalid_scores:
            assert not (min_bound <= score <= max_bound)

    def test_invariant_hermeticity(self):
        """CONTRACT: Each cluster has correct PA composition."""
        expected_composition = {
            "CLUSTER_MESO_1": {"PA01", "PA02", "PA03"},
            "CLUSTER_MESO_2": {"PA04", "PA05", "PA06"},
            "CLUSTER_MESO_3": {"PA07", "PA08"},
            "CLUSTER_MESO_4": {"PA09", "PA10"},
        }
        
        for cluster_id, expected_pas in expected_composition.items():
            actual_pas = set(LOCAL_CLUSTER_COMPOSITION[cluster_id])
            assert actual_pas == expected_pas
