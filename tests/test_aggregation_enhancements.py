"""
Tests for Aggregation Enhancements - Surgical Improvements

Tests enhancement windows:
- [EW-001] Confidence interval tracking
- [EW-002] Enhanced hermeticity diagnosis
- [EW-003] Adaptive coherence thresholds
- [EW-004] Strategic alignment metrics
"""

import pytest
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass

from canonic_phases.Phase_four_five_six_seven.aggregation_enhancements import (
    EnhancedDimensionAggregator,
    EnhancedAreaAggregator,
    EnhancedClusterAggregator,
    EnhancedMacroAggregator,
    ConfidenceInterval,
    DispersionMetrics,
    HermeticityDiagnosis,
    StrategicAlignmentMetrics,
    enhance_aggregator,
)


class TestEnhancedDimensionAggregator:
    """Test [EW-001] confidence interval tracking."""
    
    def test_aggregate_with_confidence_basic(self):
        """Test basic confidence interval computation."""
        base_mock = Mock()
        base_mock.calculate_weighted_average = Mock(return_value=2.0)
        base_mock.bootstrap_aggregator = None
        
        enhanced = EnhancedDimensionAggregator(base_mock, enable_contracts=False)
        
        scores = [1.5, 2.0, 2.5]
        weights = [0.33, 0.34, 0.33]
        
        aggregated, ci = enhanced.aggregate_with_confidence(scores, weights)
        
        assert aggregated == 2.0
        assert isinstance(ci, ConfidenceInterval)
        assert ci.lower_bound <= aggregated <= ci.upper_bound
        assert ci.confidence_level == 0.95
        assert ci.method == "analytical"
    
    def test_confidence_interval_single_score(self):
        """Test CI with single score (no variance)."""
        base_mock = Mock()
        base_mock.calculate_weighted_average = Mock(return_value=2.0)
        base_mock.bootstrap_aggregator = None
        
        enhanced = EnhancedDimensionAggregator(base_mock, enable_contracts=False)
        
        scores = [2.0]
        
        aggregated, ci = enhanced.aggregate_with_confidence(scores)
        
        # With single score, CI should be point estimate
        assert ci.lower_bound == ci.upper_bound == aggregated
    
    def test_confidence_interval_bounds(self):
        """Test CI respects score bounds [0, 3]."""
        base_mock = Mock()
        base_mock.calculate_weighted_average = Mock(return_value=0.1)
        base_mock.bootstrap_aggregator = None
        
        enhanced = EnhancedDimensionAggregator(base_mock, enable_contracts=False)
        
        # Very low scores with high variance
        scores = [0.0, 0.1, 0.2]
        
        aggregated, ci = enhanced.aggregate_with_confidence(scores)
        
        # CI should not go below 0
        assert ci.lower_bound >= 0.0
        assert ci.upper_bound <= 3.0


class TestEnhancedAreaAggregator:
    """Test [EW-002] enhanced hermeticity diagnosis."""
    
    def test_diagnose_hermeticity_valid(self):
        """Test hermeticity diagnosis with valid input."""
        base_mock = Mock()
        enhanced = EnhancedAreaAggregator(base_mock, enable_contracts=False)
        
        actual = {"DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"}
        expected = {"DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"}
        
        diagnosis = enhanced.diagnose_hermeticity(actual, expected, "PA01")
        
        assert diagnosis.is_hermetic
        assert len(diagnosis.missing_ids) == 0
        assert len(diagnosis.extra_ids) == 0
        assert diagnosis.severity == "LOW"
        assert "No action needed" in diagnosis.remediation_hint
    
    def test_diagnose_hermeticity_missing(self):
        """Test hermeticity diagnosis with missing dimensions."""
        base_mock = Mock()
        enhanced = EnhancedAreaAggregator(base_mock, enable_contracts=False)
        
        actual = {"DIM01", "DIM02", "DIM03", "DIM04"}
        expected = {"DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"}
        
        diagnosis = enhanced.diagnose_hermeticity(actual, expected, "PA01")
        
        assert not diagnosis.is_hermetic
        assert diagnosis.missing_ids == {"DIM05", "DIM06"}
        assert len(diagnosis.extra_ids) == 0
        assert diagnosis.severity == "CRITICAL"
        assert "DIM05" in diagnosis.remediation_hint
        assert "DIM06" in diagnosis.remediation_hint
    
    def test_diagnose_hermeticity_extra(self):
        """Test hermeticity diagnosis with extra dimensions."""
        base_mock = Mock()
        enhanced = EnhancedAreaAggregator(base_mock, enable_contracts=False)
        
        actual = {"DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06", "DIM07"}
        expected = {"DIM01", "DIM02", "DIM03", "DIM04", "DIM05", "DIM06"}
        
        diagnosis = enhanced.diagnose_hermeticity(actual, expected, "PA01")
        
        assert not diagnosis.is_hermetic
        assert len(diagnosis.missing_ids) == 0
        assert diagnosis.extra_ids == {"DIM07"}
        assert diagnosis.severity == "HIGH"
        assert "Remove unexpected" in diagnosis.remediation_hint


class TestEnhancedClusterAggregator:
    """Test [EW-003] adaptive coherence thresholds."""
    
    def test_compute_dispersion_metrics_convergence(self):
        """Test dispersion metrics for convergent scores."""
        base_mock = Mock()
        enhanced = EnhancedClusterAggregator(base_mock, enable_contracts=False)
        
        # Very similar scores (high convergence)
        scores = [2.0, 2.1, 2.0, 2.05, 2.0]
        
        metrics = enhanced.compute_dispersion_metrics(scores)
        
        assert metrics.scenario == "convergence"
        assert metrics.coefficient_of_variation < 0.15
        assert 2.0 <= metrics.mean <= 2.1
        assert metrics.std_dev < 0.1
    
    def test_compute_dispersion_metrics_high_dispersion(self):
        """Test dispersion metrics for dispersed scores."""
        base_mock = Mock()
        enhanced = EnhancedClusterAggregator(base_mock, enable_contracts=False)
        
        # Very different scores (high dispersion)
        scores = [0.5, 1.0, 2.5, 2.8, 0.3]
        
        metrics = enhanced.compute_dispersion_metrics(scores)
        
        assert metrics.scenario in ["high_dispersion", "extreme_dispersion"]
        assert metrics.coefficient_of_variation > 0.40
        assert metrics.std_dev > 0.5
    
    def test_compute_dispersion_metrics_empty(self):
        """Test dispersion metrics with empty input."""
        base_mock = Mock()
        enhanced = EnhancedClusterAggregator(base_mock, enable_contracts=False)
        
        scores = []
        
        metrics = enhanced.compute_dispersion_metrics(scores)
        
        assert metrics.scenario == "convergence"
        assert metrics.coefficient_of_variation == 0.0
        assert metrics.mean == 0.0
    
    def test_adaptive_penalty_convergence(self):
        """Test adaptive penalty for convergent scenario."""
        base_mock = Mock()
        enhanced = EnhancedClusterAggregator(base_mock, enable_contracts=False)
        
        metrics = Mock()
        metrics.scenario = "convergence"
        
        penalty = enhanced.adaptive_penalty(metrics)
        
        # Convergence should have reduced penalty (0.5× multiplier)
        assert penalty == 0.3 * 0.5  # base_penalty * 0.5
        assert penalty == 0.15
    
    def test_adaptive_penalty_moderate(self):
        """Test adaptive penalty for moderate scenario."""
        base_mock = Mock()
        enhanced = EnhancedClusterAggregator(base_mock, enable_contracts=False)
        
        metrics = Mock()
        metrics.scenario = "moderate"
        
        penalty = enhanced.adaptive_penalty(metrics)
        
        # Moderate should have standard penalty (1.0× multiplier)
        assert penalty == 0.3 * 1.0
        assert penalty == 0.3
    
    def test_adaptive_penalty_high_dispersion(self):
        """Test adaptive penalty for high dispersion scenario."""
        base_mock = Mock()
        enhanced = EnhancedClusterAggregator(base_mock, enable_contracts=False)
        
        metrics = Mock()
        metrics.scenario = "high_dispersion"
        
        penalty = enhanced.adaptive_penalty(metrics)
        
        # High dispersion should have increased penalty (1.5× multiplier)
        assert penalty == round(0.3 * 1.5, 2)
        assert penalty == 0.45
    
    def test_adaptive_penalty_extreme(self):
        """Test adaptive penalty for extreme dispersion scenario."""
        base_mock = Mock()
        enhanced = EnhancedClusterAggregator(base_mock, enable_contracts=False)
        
        metrics = Mock()
        metrics.scenario = "extreme_dispersion"
        
        penalty = enhanced.adaptive_penalty(metrics)
        
        # Extreme dispersion should have maximum penalty (2.0× multiplier)
        assert penalty == 0.3 * 2.0
        assert penalty == 0.6


class TestEnhancedMacroAggregator:
    """Test [EW-004] strategic alignment metrics."""
    
    def test_compute_strategic_alignment_basic(self):
        """Test basic strategic alignment computation."""
        base_mock = Mock()
        enhanced = EnhancedMacroAggregator(base_mock, enable_contracts=False)
        
        # Mock cluster scores
        cluster_1 = Mock(score=2.0, coherence=0.8)
        cluster_2 = Mock(score=2.2, coherence=0.85)
        cluster_3 = Mock(score=1.8, coherence=0.75)
        cluster_4 = Mock(score=2.1, coherence=0.82)
        cluster_scores = [cluster_1, cluster_2, cluster_3, cluster_4]
        
        # Mock area scores
        area_1 = Mock(area_id="PA01", area_name="Area 1", quality_level="ACEPTABLE")
        area_2 = Mock(area_id="PA02", area_name="Area 2", quality_level="INSUFICIENTE")
        area_scores = [area_1, area_2]
        
        # Mock dimension scores
        dim_1 = Mock(policy_area_id="PA01", dimension_id="DIM01", score=2.0)
        dim_2 = Mock(policy_area_id="PA01", dimension_id="DIM02", score=2.5)
        dimension_scores = [dim_1, dim_2]
        
        alignment = enhanced.compute_strategic_alignment(
            cluster_scores, area_scores, dimension_scores
        )
        
        assert isinstance(alignment, StrategicAlignmentMetrics)
        assert len(alignment.pa_dim_coverage) == 2
        assert alignment.coverage_rate == 2 / 60  # 2 cells out of 60
        assert alignment.cluster_coherence_mean > 0.7
        assert len(alignment.systemic_gaps) == 1
        assert "Area 2" in alignment.systemic_gaps
        assert 0.0 <= alignment.balance_score <= 1.0
    
    def test_compute_strategic_alignment_full_coverage(self):
        """Test strategic alignment with full PA×DIM coverage."""
        base_mock = Mock()
        enhanced = EnhancedMacroAggregator(base_mock, enable_contracts=False)
        
        # Create 60 dimension scores (10 areas × 6 dimensions)
        dimension_scores = []
        for area in range(1, 11):
            for dim in range(1, 7):
                dim_mock = Mock(
                    policy_area_id=f"PA{area:02d}",
                    dimension_id=f"DIM{dim:02d}",
                    score=2.0
                )
                dimension_scores.append(dim_mock)
        
        cluster_scores = [Mock(score=2.0, coherence=0.8) for _ in range(4)]
        area_scores = [Mock(area_id=f"PA{i:02d}", quality_level="ACEPTABLE") for i in range(1, 11)]
        
        alignment = enhanced.compute_strategic_alignment(
            cluster_scores, area_scores, dimension_scores
        )
        
        assert len(alignment.pa_dim_coverage) == 60
        assert alignment.coverage_rate == 1.0  # 100% coverage
    
    def test_compute_strategic_alignment_weakest_strongest(self):
        """Test identification of weakest and strongest dimensions."""
        base_mock = Mock()
        enhanced = EnhancedMacroAggregator(base_mock, enable_contracts=False)
        
        # Create dimensions with varying scores
        dimension_scores = [
            Mock(dimension_id="DIM01", score=3.0),  # Strongest
            Mock(dimension_id="DIM02", score=2.8),
            Mock(dimension_id="DIM03", score=2.5),
            Mock(dimension_id="DIM04", score=1.5),
            Mock(dimension_id="DIM05", score=1.0),
            Mock(dimension_id="DIM06", score=0.5),  # Weakest
        ]
        
        for dim in dimension_scores:
            dim.policy_area_id = "PA01"
        
        cluster_scores = [Mock(score=2.0, coherence=0.8) for _ in range(4)]
        area_scores = [Mock(quality_level="ACEPTABLE")]
        
        alignment = enhanced.compute_strategic_alignment(
            cluster_scores, area_scores, dimension_scores
        )
        
        # Check weakest dimensions (bottom 3)
        weakest_ids = [dim_id for dim_id, _ in alignment.weakest_dimensions]
        assert "DIM06" in weakest_ids
        
        # Check strongest dimensions (top 3)
        strongest_ids = [dim_id for dim_id, _ in alignment.strongest_dimensions]
        assert "DIM01" in strongest_ids


class TestEnhanceAggregatorFactory:
    """Test enhance_aggregator factory function."""
    
    def test_enhance_dimension_aggregator(self):
        """Test enhancing dimension aggregator."""
        base_mock = Mock()
        
        enhanced = enhance_aggregator(base_mock, "dimension", enable_contracts=False)
        
        assert isinstance(enhanced, EnhancedDimensionAggregator)
        assert enhanced.base == base_mock
    
    def test_enhance_area_aggregator(self):
        """Test enhancing area aggregator."""
        base_mock = Mock()
        
        enhanced = enhance_aggregator(base_mock, "area", enable_contracts=False)
        
        assert isinstance(enhanced, EnhancedAreaAggregator)
        assert enhanced.base == base_mock
    
    def test_enhance_cluster_aggregator(self):
        """Test enhancing cluster aggregator."""
        base_mock = Mock()
        
        enhanced = enhance_aggregator(base_mock, "cluster", enable_contracts=False)
        
        assert isinstance(enhanced, EnhancedClusterAggregator)
        assert enhanced.base == base_mock
    
    def test_enhance_macro_aggregator(self):
        """Test enhancing macro aggregator."""
        base_mock = Mock()
        
        enhanced = enhance_aggregator(base_mock, "macro", enable_contracts=False)
        
        assert isinstance(enhanced, EnhancedMacroAggregator)
        assert enhanced.base == base_mock
    
    def test_enhance_invalid_level(self):
        """Test enhancing with invalid level."""
        base_mock = Mock()
        
        with pytest.raises(ValueError, match="Invalid aggregation level"):
            enhance_aggregator(base_mock, "invalid_level")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
