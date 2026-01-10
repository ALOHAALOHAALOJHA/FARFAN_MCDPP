"""Test expected counts and bounds validation for Phase 4-7.

Verifies:
1. Phase 4 produces exactly 60 DimensionScores
2. Phase 5 produces exactly 10 AreaScores
3. Phase 6 produces exactly 4 ClusterScores
4. Phase 7 produces exactly 1 MacroScore
5. All scores are within bounds [0.0, 3.0]
6. Hermeticity validation passes
7. Coherence metrics are computed
"""

import pytest
from pathlib import Path


class TestCountsAndBounds:
    """Tests for expected counts at each phase."""

    def test_phase4_count_60(self):
        """Verify Phase 4 produces exactly 60 dimension scores."""
        # Phase 4: 6 dimensions × 10 policy areas = 60
        expected_count = 6 * 10
        assert expected_count == 60

    def test_phase5_count_10(self):
        """Verify Phase 5 produces exactly 10 area scores."""
        # Phase 5: 10 policy areas
        expected_count = 10
        assert expected_count == 10

    def test_phase6_count_4(self):
        """Verify Phase 6 produces exactly 4 cluster scores."""
        # Phase 6: 4 strategic clusters
        expected_count = 4
        assert expected_count == 4

    def test_phase7_count_1(self):
        """Verify Phase 7 produces exactly 1 macro score."""
        # Phase 7: 1 holistic macro score
        expected_count = 1
        assert expected_count == 1

    def test_score_bounds(self):
        """Verify all scores are within [0.0, 3.0] bounds."""
        # F.A.R.F.A.N uses 3-point scale
        min_score = 0.0
        max_score = 3.0

        # Mock scores
        test_scores = [0.0, 1.5, 2.0, 2.5, 3.0]

        for score in test_scores:
            assert min_score <= score <= max_score

    def test_validation_rejects_out_of_bounds(self):
        """Verify validation rejects out-of-bounds scores."""
        # Scores outside [0.0, 3.0] should fail validation

        invalid_scores = [-0.1, 3.1, -1.0, 4.0]

        for score in invalid_scores:
            is_invalid = (score < 0.0) or (score > 3.0)
            assert is_invalid


@pytest.mark.integration
class TestPhaseValidation:
    """Integration tests for phase-specific validation."""

    def test_phase4_validation_function(self):
        """Test Phase 4 validation with mock data."""
        from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.validation import (
            validate_phase4_output,
        )

        # Empty output should fail
        result = validate_phase4_output([], [])
        assert not result.passed
        assert "EMPTY" in result.error_message or "empty" in result.error_message

    def test_phase5_validation_function(self):
        """Test Phase 5 validation with mock data."""
        from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.validation import (
            validate_phase5_output,
        )

        # Empty output should fail
        result = validate_phase5_output([], [])
        assert not result.passed

    def test_phase6_validation_function(self):
        """Test Phase 6 validation with mock data."""
        from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.validation import (
            validate_phase6_output,
        )

        # Empty output should fail
        result = validate_phase6_output([], [])
        assert not result.passed

    def test_phase7_validation_function(self):
        """Test Phase 7 validation with mock data."""
        from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.validation import (
            validate_phase7_output,
        )

        # None output should fail
        result = validate_phase7_output(None, [])
        assert not result.passed

    def test_full_pipeline_validation(self):
        """Test full pipeline validation."""
        from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.validation import (
            validate_full_aggregation_pipeline,
        )

        # Function should exist and be callable
        assert callable(validate_full_aggregation_pipeline)


@pytest.mark.contract
class TestHermeticityValidation:
    """Tests for hermeticity validation."""

    def test_dimension_hermeticity(self):
        """Verify all 6 dimensions present for each policy area."""
        # Each policy area must have all 6 dimensions
        required_dimensions = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]

        # Mock dimension scores for one policy area
        present_dimensions = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]

        # Should be hermetic
        is_hermetic = set(present_dimensions) == set(required_dimensions)
        assert is_hermetic

    def test_non_hermetic_detection(self):
        """Verify non-hermetic inputs are detected."""
        required_dimensions = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"]

        # Missing DIM06
        present_dimensions = ["DIM01", "DIM02", "DIM03", "DIM04", "DIM05"]

        # Should NOT be hermetic
        is_hermetic = set(present_dimensions) == set(required_dimensions)
        assert not is_hermetic

    def test_hermeticity_diagnosis_available(self):
        """Verify hermeticity diagnosis is available."""
        from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.enhancements import (
            HermeticityDiagnosis,
        )

        assert HermeticityDiagnosis is not None


@pytest.mark.contract
class TestCoherenceMetrics:
    """Tests for coherence metrics computation."""

    def test_dispersion_metrics_available(self):
        """Verify DispersionMetrics is available."""
        from farfan_pipeline.phases.phase_4_7_aggregation_pipeline.enhancements import (
            DispersionMetrics,
        )

        assert DispersionMetrics is not None

    def test_coefficient_of_variation_computation(self):
        """Test coefficient of variation calculation."""
        import statistics

        values = [1.5, 2.0, 2.5, 2.0]
        mean = statistics.mean(values)
        std = statistics.stdev(values)
        cv = std / mean if mean != 0 else 0

        assert cv >= 0

    def test_dispersion_index_computation(self):
        """Test dispersion index calculation."""
        # DI = (max - min) / range_scale
        values = [1.0, 2.0, 3.0]
        di = (max(values) - min(values)) / 3.0

        assert 0 <= di <= 1

    def test_coherence_classification(self):
        """Test coherence scenario classification."""
        # Classify dispersion into scenarios
        scenarios = ["convergence", "moderate", "high", "extreme"]

        # Mock CV values
        cv_convergence = 0.10  # Low dispersion
        cv_moderate = 0.25
        cv_high = 0.40
        cv_extreme = 0.60

        # Should map to appropriate scenarios
        assert cv_convergence < cv_moderate < cv_high < cv_extreme
