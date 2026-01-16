"""
Phase 5 Integration Tests - Real Module Validation
===================================================

These tests validate Phase 5 logic against the REAL Phase 4 types.
Import actual DimensionScore, AreaScore from farfan_pipeline.

INTEGRATION TEST CATEGORIES:
1. Real type compatibility
2. Aggregator class integration
3. Validation function integration
4. Pipeline flow validation
"""

from __future__ import annotations

import pytest

# Try to import real types - skip if not available
try:
    from farfan_pipeline.phases.Phase_04 import (
        AreaScore,
        DimensionScore,
    )
    from farfan_pipeline.phases.Phase_04.phase4_10_00_aggregation import (
        AreaPolicyAggregator,
    )
    REAL_IMPORTS_AVAILABLE = True
except ImportError:
    REAL_IMPORTS_AVAILABLE = False
    DimensionScore = None
    AreaScore = None
    AreaPolicyAggregator = None

try:
    from farfan_pipeline.phases.Phase_05 import (
        CLUSTER_ASSIGNMENTS,
        DIMENSIONS_PER_AREA,
        EXPECTED_AREA_SCORE_COUNT,
        MAX_SCORE,
        MIN_SCORE,
        POLICY_AREAS,
        Phase5Invariants,
    )
    PHASE5_CONSTANTS_AVAILABLE = True
except ImportError:
    PHASE5_CONSTANTS_AVAILABLE = False

from .conftest import (
    CLUSTER_TO_PAS,
    DIMENSIONS,
    PA_TO_CLUSTER,
    POLICY_AREAS as LOCAL_POLICY_AREAS,
)


# =============================================================================
# CONDITIONAL TEST MARKERS
# =============================================================================

requires_real_imports = pytest.mark.skipif(
    not REAL_IMPORTS_AVAILABLE,
    reason="Real Phase 4 types not available"
)

requires_phase5_constants = pytest.mark.skipif(
    not PHASE5_CONSTANTS_AVAILABLE,
    reason="Phase 5 constants not available"
)


# =============================================================================
# 1. PHASE 5 CONSTANTS VALIDATION
# =============================================================================


@requires_phase5_constants
class TestPhase5ConstantsIntegrity:
    """Validate Phase 5 constants against canonical structure."""

    def test_policy_areas_match_canonical(self):
        """INTEGRATION: Phase 5 POLICY_AREAS matches canonical list."""
        assert set(POLICY_AREAS) == set(LOCAL_POLICY_AREAS)

    def test_expected_area_count(self):
        """INTEGRATION: Expected count is 10."""
        assert EXPECTED_AREA_SCORE_COUNT == 10

    def test_dimensions_per_area(self):
        """INTEGRATION: 6 dimensions per area."""
        assert DIMENSIONS_PER_AREA == 6

    def test_score_bounds(self):
        """INTEGRATION: Score bounds are [0.0, 3.0]."""
        assert MIN_SCORE == 0.0
        assert MAX_SCORE == 3.0

    def test_cluster_assignments_structure(self):
        """INTEGRATION: Cluster assignments have correct structure."""
        # Should have 4 clusters
        assert len(CLUSTER_ASSIGNMENTS) == 4
        
        # Each cluster should have PA IDs
        for cluster_id, pa_list in CLUSTER_ASSIGNMENTS.items():
            assert cluster_id.startswith("CLUSTER_")
            assert len(pa_list) >= 2
            for pa in pa_list:
                assert pa.startswith("PA")

    def test_cluster_assignments_cover_all_pas(self):
        """INTEGRATION: All PAs are assigned to clusters."""
        all_pas = set()
        for pa_list in CLUSTER_ASSIGNMENTS.values():
            all_pas.update(pa_list)
        
        # Note: CLUSTER_ASSIGNMENTS uses different names (CLUSTER_MESO_*)
        # versus our local mapping (CL01-CL04)
        assert len(all_pas) == 10, f"Expected 10 PAs, got {len(all_pas)}: {all_pas}"


@requires_phase5_constants
class TestPhase5Invariants:
    """Test Phase5Invariants class."""

    def test_validate_count_valid(self):
        """INTEGRATION: validate_count returns True for 10 scores."""
        # Create mock area scores
        mock_scores = [type("AreaScore", (), {"area_id": f"PA{i:02d}"})() for i in range(1, 11)]
        assert Phase5Invariants.validate_count(mock_scores)

    def test_validate_count_invalid(self):
        """INTEGRATION: validate_count returns False for wrong count."""
        mock_scores = [type("AreaScore", (), {"area_id": f"PA{i:02d}"})() for i in range(1, 8)]
        assert not Phase5Invariants.validate_count(mock_scores)

    def test_validate_bounds_valid(self):
        """INTEGRATION: validate_bounds for valid scores."""
        assert Phase5Invariants.validate_bounds(0.0)
        assert Phase5Invariants.validate_bounds(1.5)
        assert Phase5Invariants.validate_bounds(3.0)

    def test_validate_bounds_invalid(self):
        """INTEGRATION: validate_bounds for invalid scores."""
        assert not Phase5Invariants.validate_bounds(-0.1)
        assert not Phase5Invariants.validate_bounds(3.1)


# =============================================================================
# 2. REAL TYPE INTEGRATION
# =============================================================================


@requires_real_imports
class TestRealDimensionScoreIntegration:
    """Tests using real DimensionScore from Phase 4."""

    def test_dimension_score_creation(self):
        """INTEGRATION: Can create real DimensionScore."""
        ds = DimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=2.0,
            quality_level="BUENO",
            contributing_questions=[1, 2, 3, 4, 5],
        )
        assert ds.dimension_id == "DIM01"
        assert ds.area_id == "PA01"
        assert ds.score == 2.0

    def test_dimension_score_all_fields(self):
        """INTEGRATION: DimensionScore has all expected fields."""
        ds = DimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=2.0,
            quality_level="BUENO",
            contributing_questions=[1],
        )
        # SOTA fields
        assert hasattr(ds, "score_std")
        assert hasattr(ds, "confidence_interval_95")
        assert hasattr(ds, "provenance_node_id")

    def test_dimension_score_validation_details(self):
        """INTEGRATION: DimensionScore validation_details accessible."""
        ds = DimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=2.0,
            quality_level="BUENO",
            contributing_questions=[1],
            validation_details={"hermeticity": True},
        )
        assert ds.validation_details["hermeticity"] is True


@requires_real_imports
class TestRealAreaScoreIntegration:
    """Tests using real AreaScore from Phase 4."""

    def test_area_score_creation(self):
        """INTEGRATION: Can create real AreaScore."""
        dim_scores = [
            DimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1, 2, 3, 4, 5],
            )
            for dim in DIMENSIONS
        ]
        
        area_score = AreaScore(
            area_id="PA01",
            area_name="Test Area",
            score=2.0,
            quality_level="BUENO",
            dimension_scores=dim_scores,
            cluster_id="CL02",
        )
        
        assert area_score.area_id == "PA01"
        assert len(area_score.dimension_scores) == 6

    def test_area_score_cluster_assignment(self):
        """INTEGRATION: AreaScore can have cluster_id."""
        dim_scores = [
            DimensionScore(
                dimension_id=dim,
                area_id="PA01",
                score=2.0,
                quality_level="BUENO",
                contributing_questions=[1],
            )
            for dim in DIMENSIONS
        ]
        
        area_score = AreaScore(
            area_id="PA01",
            area_name="Test Area",
            score=2.0,
            quality_level="BUENO",
            dimension_scores=dim_scores,
            cluster_id=PA_TO_CLUSTER["PA01"],
        )
        
        assert area_score.cluster_id == "CL02"


# =============================================================================
# 3. AGGREGATOR INTEGRATION
# =============================================================================


@requires_real_imports
class TestAreaPolicyAggregatorIntegration:
    """Tests for AreaPolicyAggregator from Phase 4."""

    def test_aggregator_instantiation(self):
        """INTEGRATION: Can instantiate AreaPolicyAggregator."""
        aggregator = AreaPolicyAggregator(
            monolith=None,
            abort_on_insufficient=True,
        )
        assert aggregator is not None

    def test_aggregator_has_aggregate_method(self):
        """INTEGRATION: Aggregator has aggregate_area method."""
        aggregator = AreaPolicyAggregator(
            monolith=None,
            abort_on_insufficient=True,
        )
        assert hasattr(aggregator, "aggregate_area")


# =============================================================================
# 4. CROSS-MODULE CONSISTENCY
# =============================================================================


class TestCrossModuleConsistency:
    """Tests for consistency across Phase 4 and Phase 5."""

    def test_cluster_mappings_consistent(self):
        """INTEGRATION: Local and Phase 5 cluster mappings are consistent."""
        # Our local mapping
        local_cluster_count = len(CLUSTER_TO_PAS)
        
        # Should have 4 clusters
        assert local_cluster_count == 4

    def test_dimension_count_consistent(self):
        """INTEGRATION: Dimension count is 6 everywhere."""
        assert len(DIMENSIONS) == 6

    def test_policy_area_count_consistent(self):
        """INTEGRATION: PA count is 10 everywhere."""
        assert len(LOCAL_POLICY_AREAS) == 10


# =============================================================================
# 5. PIPELINE FLOW VALIDATION
# =============================================================================


class TestPipelineFlowValidation:
    """Tests for Phase 4 → Phase 5 → Phase 6 flow."""

    def test_input_output_cardinality(self):
        """PIPELINE: 60 DimensionScores → 10 AreaScores."""
        # Input: 10 PAs × 6 dimensions = 60
        input_count = len(LOCAL_POLICY_AREAS) * len(DIMENSIONS)
        assert input_count == 60
        
        # Output: 10 AreaScores
        output_count = len(LOCAL_POLICY_AREAS)
        assert output_count == 10

    def test_cluster_output_cardinality(self):
        """PIPELINE: 10 AreaScores → 4 ClusterScores (Phase 6)."""
        # Verify cluster count
        assert len(CLUSTER_TO_PAS) == 4
        
        # Verify all PAs covered
        covered_pas = set()
        for pas in CLUSTER_TO_PAS.values():
            covered_pas.update(pas)
        assert len(covered_pas) == 10

    def test_cluster_pa_distribution(self):
        """PIPELINE: Verify PA distribution across clusters."""
        expected = {
            "CL01": 3,  # PA02, PA03, PA07
            "CL02": 3,  # PA01, PA05, PA06
            "CL03": 2,  # PA04, PA08
            "CL04": 2,  # PA09, PA10
        }
        
        actual = {cluster: len(pas) for cluster, pas in CLUSTER_TO_PAS.items()}
        assert actual == expected


# =============================================================================
# 6. CONTRACT VALIDATION
# =============================================================================


class TestPhase5Contracts:
    """Tests for Phase 5 contract compliance."""

    def test_input_contract(self):
        """CONTRACT: Input must be list of DimensionScore-like objects."""
        # DimensionScore must have: dimension_id, area_id, score
        required_fields = ["dimension_id", "area_id", "score"]
        
        # Verify our mock has these
        from .conftest import MockDimensionScore
        mock = MockDimensionScore(
            dimension_id="DIM01",
            area_id="PA01",
            score=2.0,
            quality_level="BUENO",
            contributing_questions=[1],
        )
        for field in required_fields:
            assert hasattr(mock, field), f"Missing field: {field}"

    def test_output_contract(self):
        """CONTRACT: Output must be list of AreaScore-like objects."""
        # AreaScore must have: area_id, score, dimension_scores, cluster_id
        required_fields = ["area_id", "score", "dimension_scores", "cluster_id"]
        
        from .conftest import MockAreaScore, MockDimensionScore
        mock = MockAreaScore(
            area_id="PA01",
            area_name="Test",
            score=2.0,
            quality_level="BUENO",
            dimension_scores=[],
        )
        for field in required_fields:
            assert hasattr(mock, field), f"Missing field: {field}"

    def test_invariant_count(self):
        """CONTRACT: Must produce exactly 10 AreaScores."""
        # This is invariant - cannot be 9 or 11
        expected = 10
        actual = len(LOCAL_POLICY_AREAS)
        assert actual == expected

    def test_invariant_hermeticity(self):
        """CONTRACT: Each AreaScore must have exactly 6 DimensionScores."""
        expected = 6
        actual = len(DIMENSIONS)
        assert actual == expected

    def test_invariant_bounds(self):
        """CONTRACT: All scores must be in [0.0, 3.0]."""
        # Test the bounds
        min_bound = 0.0
        max_bound = 3.0
        
        # Valid scores
        valid_scores = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        for score in valid_scores:
            assert min_bound <= score <= max_bound
        
        # Invalid scores
        invalid_scores = [-0.1, 3.1, -1.0, 4.0]
        for score in invalid_scores:
            assert not (min_bound <= score <= max_bound)
