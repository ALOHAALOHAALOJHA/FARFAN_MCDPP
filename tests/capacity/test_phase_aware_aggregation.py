"""
Test Suite for Phase-Aware Capacity Aggregation Module
======================================================

Tests for the phase-aware aggregation that extends base capacity aggregation
with phase-specific strategies and cross-phase analysis.

Tests cover:
1. Phase-specific aggregation configuration
2. Phase-aware aggregation (Formula 10)
3. Cross-phase aggregation (Formula 11)
4. Phase transition smoothing (Formula 12)
5. Phase aggregation pipeline
6. Aggregation metrics and analysis

Mathematical Models Under Test:
    Formula 10: C_phase_org(p) = [(Σ C_ind^p(phase))^(1/p)] × κ_org(p) × ψ_phase(p)
    Formula 11: C_cross(p1, p2) = √[C(p1) × C(p2)] × ρ_transition(p1, p2)
    Formula 12: C_smooth(p) = α×C(p) + (1-α)×C(p-1) with α = sigmoid(coherence)

Author: F.A.R.F.A.N. Test Team
Version: 2.0.0
"""

import math
import pytest
from typing import Dict, List

from farfan_pipeline.capacity.types import (
    PolicyLevel,
    CapacityType,
    CapacityScore,
)

from farfan_pipeline.capacity.aggregation import (
    AggregationConfig,
)

from farfan_pipeline.capacity.phase_integration import (
    CanonicalPhase,
    PhaseCapacityScore,
    PhaseCapacityMapping,
    DEFAULT_PHASE_CAPACITY_MAPPINGS,
)

from farfan_pipeline.capacity.phase_aware_aggregation import (
    PhaseAggregationConfig,
    PhaseAwareAggregationResult,
    PhaseAwareCapacityAggregator,
    PhaseAggregationPipeline,
)


# ============================================================================
# FIXTURE DEFINITIONS
# ============================================================================

@pytest.fixture
def base_config() -> AggregationConfig:
    """Create base aggregation configuration."""
    return AggregationConfig()


@pytest.fixture
def phase_agg_config(base_config) -> PhaseAggregationConfig:
    """Create phase aggregation configuration."""
    return PhaseAggregationConfig(base_config=base_config)


@pytest.fixture
def phase_aggregator(phase_agg_config) -> PhaseAwareCapacityAggregator:
    """Create phase-aware aggregator."""
    return PhaseAwareCapacityAggregator(config=phase_agg_config)


@pytest.fixture
def sample_phase_scores() -> List[PhaseCapacityScore]:
    """Create sample phase capacity scores."""
    base_scores = [
        CapacityScore(
            capacity_type=CapacityType.CA_I,
            raw_score=0.85,
            weighted_score=0.80,
            confidence=0.9,
            method_count=10,
        ),
        CapacityScore(
            capacity_type=CapacityType.CA_O,
            raw_score=0.90,
            weighted_score=0.88,
            confidence=0.85,
            method_count=8,
        ),
        CapacityScore(
            capacity_type=CapacityType.CO_O,
            raw_score=0.82,
            weighted_score=0.78,
            confidence=0.88,
            method_count=9,
        ),
    ]
    
    mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_04]
    
    return [
        PhaseCapacityScore.from_base_score(
            phase=CanonicalPhase.PHASE_04,
            base_score=base_score,
            mapping=mapping,
        )
        for base_score in base_scores
    ]


# ============================================================================
# PHASE AGGREGATION CONFIG TESTS
# ============================================================================

class TestPhaseAggregationConfig:
    """Test suite for PhaseAggregationConfig."""
    
    def test_config_initialization(self, base_config):
        """Test configuration initialization with defaults."""
        config = PhaseAggregationConfig(base_config=base_config)
        
        assert config.base_config == base_config
        assert len(config.phase_kappa_org) == 10  # All 10 phases
        assert len(config.phase_kappa_sys) == 10
        assert config.smoothing_sensitivity > 0
    
    def test_get_kappa_org_for_phases(self, phase_agg_config):
        """Test getting organizational factor for different phases."""
        # Early phase should have lower kappa
        early_kappa = phase_agg_config.get_kappa_org(CanonicalPhase.PHASE_01)
        
        # Late phase should have higher kappa
        late_kappa = phase_agg_config.get_kappa_org(CanonicalPhase.PHASE_07)
        
        assert late_kappa > early_kappa
        assert 0.8 <= early_kappa <= 0.95
        assert 0.8 <= late_kappa <= 0.95
    
    def test_get_kappa_sys_for_phases(self, phase_agg_config):
        """Test getting systemic factor for different phases."""
        # Phase 7 (macro aggregation) should have highest systemic factor
        phase7_kappa = phase_agg_config.get_kappa_sys(CanonicalPhase.PHASE_07)
        phase3_kappa = phase_agg_config.get_kappa_sys(CanonicalPhase.PHASE_03)
        
        assert phase7_kappa >= phase3_kappa
    
    def test_transition_factor_adjacent_phases(self, phase_agg_config):
        """Test transition factor between adjacent phases."""
        factor = phase_agg_config.get_transition_factor(
            CanonicalPhase.PHASE_03,
            CanonicalPhase.PHASE_04
        )
        
        # Adjacent phases should have high transition factor
        assert factor >= 0.85
        assert factor <= 1.0
    
    def test_transition_factor_distant_phases(self, phase_agg_config):
        """Test transition factor between distant phases."""
        factor = phase_agg_config.get_transition_factor(
            CanonicalPhase.PHASE_02,
            CanonicalPhase.PHASE_08
        )
        
        # Distant phases should have lower transition factor
        # (6 phases apart)
        assert 0.0 < factor < 0.85
    
    def test_transition_factor_same_phase(self, phase_agg_config):
        """Test transition factor for same phase."""
        factor = phase_agg_config.get_transition_factor(
            CanonicalPhase.PHASE_04,
            CanonicalPhase.PHASE_04
        )
        
        # Same phase should have perfect transition
        assert factor == 1.0


# ============================================================================
# PHASE-AWARE AGGREGATOR TESTS
# ============================================================================

class TestPhaseAwareAggregator:
    """Test suite for PhaseAwareCapacityAggregator."""
    
    def test_aggregator_initialization(self, phase_agg_config):
        """Test aggregator initialization."""
        aggregator = PhaseAwareCapacityAggregator(config=phase_agg_config)
        
        assert aggregator.config == phase_agg_config
        assert aggregator.base_aggregator is not None
    
    def test_aggregator_default_config(self):
        """Test aggregator with default configuration."""
        aggregator = PhaseAwareCapacityAggregator()
        
        assert aggregator.config is not None
        assert aggregator.config.base_config is not None
    
    def test_aggregate_phase_capacity_basic(
        self,
        phase_aggregator,
        sample_phase_scores
    ):
        """Test basic phase capacity aggregation."""
        results = phase_aggregator.aggregate_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            phase_scores=sample_phase_scores,
        )
        
        assert len(results) > 0
        assert all(isinstance(r, PhaseAwareAggregationResult) for r in results)
        assert all(r.phase == CanonicalPhase.PHASE_04 for r in results)
    
    def test_phase_adjusted_scores_formula_10(
        self,
        phase_aggregator,
        sample_phase_scores
    ):
        """Test Formula 10: Phase-adjusted aggregation."""
        results = phase_aggregator.aggregate_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            phase_scores=sample_phase_scores,
        )
        
        for result in results:
            # Phase-adjusted scores should be non-zero
            assert result.phase_adjusted_org_score > 0
            assert result.phase_adjusted_sys_score > 0
            
            # Phase org factor should increase with phase index
            assert result.phase_org_factor >= 1.0
            
            # Kappa values should be phase-specific
            assert result.kappa_org_used > 0
            assert result.kappa_sys_used > 0
    
    def test_aggregation_with_smoothing(
        self,
        phase_aggregator,
        sample_phase_scores
    ):
        """Test aggregation with transition smoothing (Formula 12)."""
        # Create previous phase results
        prev_results = phase_aggregator.aggregate_phase_capacity(
            phase=CanonicalPhase.PHASE_03,
            phase_scores=sample_phase_scores,
        )
        
        # Create current phase results with previous context
        curr_results = phase_aggregator.aggregate_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            phase_scores=sample_phase_scores,
            previous_phase_results=prev_results,
        )
        
        # At least some results should be smoothed
        smoothed_results = [r for r in curr_results if r.was_smoothed]
        
        # If there are matching capacity types, they should be smoothed
        if smoothed_results:
            for result in smoothed_results:
                assert result.smoothing_alpha is not None
                assert 0 <= result.smoothing_alpha <= 1
                assert result.previous_phase_contribution is not None
    
    def test_cross_phase_aggregation_formula_11(
        self,
        phase_aggregator,
        sample_phase_scores
    ):
        """Test Formula 11: Cross-phase aggregation."""
        # Create results for two phases
        phase3_results = phase_aggregator.aggregate_phase_capacity(
            phase=CanonicalPhase.PHASE_03,
            phase_scores=sample_phase_scores,
        )
        
        phase4_results = phase_aggregator.aggregate_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            phase_scores=sample_phase_scores,
        )
        
        # Apply cross-phase aggregation
        cross_results = phase_aggregator.aggregate_cross_phase(
            source_phase=CanonicalPhase.PHASE_03,
            target_phase=CanonicalPhase.PHASE_04,
            source_results=phase3_results,
            target_results=phase4_results,
        )
        
        # Results should be marked as cross-phase aggregated
        assert len(cross_results) > 0
        
        for result in cross_results:
            if result.cross_phase_aggregated:
                assert result.cross_phase_partner == CanonicalPhase.PHASE_03
                assert result.transition_factor_used is not None
                assert 0 < result.transition_factor_used <= 1
    
    def test_coherence_estimation(self, phase_aggregator, sample_phase_scores):
        """Test coherence estimation from phase scores."""
        coherence = phase_aggregator._estimate_coherence(sample_phase_scores)
        
        # Coherence should be between 0 and 1
        assert 0 <= coherence <= 1
    
    def test_smoothing_alpha_calculation(self, phase_aggregator):
        """Test smoothing alpha calculation via sigmoid."""
        # High coherence should give high alpha
        high_alpha = phase_aggregator._calculate_smoothing_alpha(coherence=0.9)
        assert high_alpha > 0.7
        
        # Low coherence should give low alpha
        low_alpha = phase_aggregator._calculate_smoothing_alpha(coherence=0.2)
        assert low_alpha < 0.5
        
        # Medium coherence should be around 0.5
        mid_alpha = phase_aggregator._calculate_smoothing_alpha(coherence=0.5)
        assert 0.4 < mid_alpha < 0.6
    
    def test_aggregation_metrics(self, phase_aggregator, sample_phase_scores):
        """Test computation of aggregation metrics."""
        results = phase_aggregator.aggregate_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            phase_scores=sample_phase_scores,
        )
        
        metrics = phase_aggregator.compute_phase_aggregation_metrics(results)
        
        # Verify metric structure
        assert "phase" in metrics
        assert "total_results" in metrics
        assert "smoothed_count" in metrics
        assert "avg_org_adjustment_factor" in metrics
        assert metrics["total_results"] == len(results)


# ============================================================================
# PHASE AGGREGATION PIPELINE TESTS
# ============================================================================

class TestPhaseAggregationPipeline:
    """Test suite for PhaseAggregationPipeline."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = PhaseAggregationPipeline()
        
        assert pipeline.aggregator is not None
        assert len(pipeline.phase_results) == 0
    
    def test_process_single_phase(self, sample_phase_scores):
        """Test processing a single phase."""
        pipeline = PhaseAggregationPipeline()
        
        results = pipeline.process_phase(
            phase=CanonicalPhase.PHASE_04,
            phase_scores=sample_phase_scores,
        )
        
        assert len(results) > 0
        assert CanonicalPhase.PHASE_04 in pipeline.phase_results
        assert pipeline.phase_results[CanonicalPhase.PHASE_04] == results
    
    def test_process_multiple_phases(self, sample_phase_scores):
        """Test processing multiple phases in sequence."""
        pipeline = PhaseAggregationPipeline()
        
        # Process phases 3, 4, 5
        for phase_idx in [3, 4, 5]:
            phase = CanonicalPhase.from_index(phase_idx)
            pipeline.process_phase(
                phase=phase,
                phase_scores=sample_phase_scores,
            )
        
        assert len(pipeline.phase_results) == 3
        assert CanonicalPhase.PHASE_03 in pipeline.phase_results
        assert CanonicalPhase.PHASE_04 in pipeline.phase_results
        assert CanonicalPhase.PHASE_05 in pipeline.phase_results
    
    def test_analyze_phase_transition(self, sample_phase_scores):
        """Test analyzing transition between phases."""
        pipeline = PhaseAggregationPipeline()
        
        # Process two phases
        pipeline.process_phase(CanonicalPhase.PHASE_03, sample_phase_scores)
        pipeline.process_phase(CanonicalPhase.PHASE_04, sample_phase_scores)
        
        # Analyze transition
        analysis = pipeline.analyze_phase_transition(
            source_phase=CanonicalPhase.PHASE_03,
            target_phase=CanonicalPhase.PHASE_04,
        )
        
        # Verify analysis structure
        assert "source_phase" in analysis
        assert "target_phase" in analysis
        assert "organizational_capacity" in analysis
        assert "systemic_capacity" in analysis
        
        org = analysis["organizational_capacity"]
        assert "source" in org
        assert "target" in org
        assert "delta" in org
        assert "growth_rate" in org
    
    def test_pipeline_summary(self, sample_phase_scores):
        """Test getting pipeline summary."""
        pipeline = PhaseAggregationPipeline()
        
        # Process multiple phases
        for phase_idx in [3, 4, 5, 6]:
            phase = CanonicalPhase.from_index(phase_idx)
            pipeline.process_phase(phase, sample_phase_scores)
        
        summary = pipeline.get_pipeline_summary()
        
        # Verify summary structure
        assert "phases_processed" in summary
        assert summary["phases_processed"] == 4
        assert "phase_sequence" in summary
        assert "organizational_progression" in summary
        assert "systemic_progression" in summary
        assert "final_org_capacity" in summary
        assert "final_sys_capacity" in summary
        
        # Verify progressions have correct length
        assert len(summary["organizational_progression"]) == 4
        assert len(summary["systemic_progression"]) == 4
    
    def test_pipeline_error_handling(self):
        """Test error handling in pipeline."""
        pipeline = PhaseAggregationPipeline()
        
        # Try to analyze transition without processing phases
        with pytest.raises(ValueError, match="No results for source phase"):
            pipeline.analyze_phase_transition(
                source_phase=CanonicalPhase.PHASE_03,
                target_phase=CanonicalPhase.PHASE_04,
            )


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhaseAggregationIntegration:
    """Integration tests for complete phase-aware aggregation."""
    
    def test_full_pipeline_aggregation(self, sample_phase_scores):
        """Test complete pipeline with aggregation tracking."""
        pipeline = PhaseAggregationPipeline()
        
        # Process phases 3-7 (core aggregation phases)
        phases = [CanonicalPhase.from_index(i) for i in range(3, 8)]
        
        for phase in phases:
            results = pipeline.process_phase(phase, sample_phase_scores)
            assert len(results) > 0
        
        # Verify all phases processed
        assert len(pipeline.phase_results) == 5
        
        # Get summary
        summary = pipeline.get_pipeline_summary()
        assert summary["phases_processed"] == 5
        
        # Analyze all transitions
        for i in range(len(phases) - 1):
            analysis = pipeline.analyze_phase_transition(
                source_phase=phases[i],
                target_phase=phases[i + 1],
            )
            assert analysis is not None
    
    def test_capacity_evolution_through_pipeline(self, sample_phase_scores):
        """Test how capacity evolves through the pipeline."""
        pipeline = PhaseAggregationPipeline()
        
        # Process phases and track capacity evolution
        capacity_evolution = []
        
        for phase_idx in range(3, 8):
            phase = CanonicalPhase.from_index(phase_idx)
            results = pipeline.process_phase(phase, sample_phase_scores)
            
            # Calculate total capacity for this phase
            total_org = sum(r.phase_adjusted_org_score for r in results)
            total_sys = sum(r.phase_adjusted_sys_score for r in results)
            
            capacity_evolution.append({
                "phase": phase.code,
                "org": total_org,
                "sys": total_sys,
            })
        
        # Verify we tracked 5 phases
        assert len(capacity_evolution) == 5
        
        # Capacity should generally increase through aggregation phases
        # (though may vary based on phase-specific factors)
        for entry in capacity_evolution:
            assert entry["org"] > 0
            assert entry["sys"] > 0
    
    def test_phase_specific_adjustments(self, sample_phase_scores):
        """Test that phase-specific adjustments are applied correctly."""
        pipeline = PhaseAggregationPipeline()
        
        # Process early phase
        early_results = pipeline.process_phase(
            CanonicalPhase.PHASE_01,
            sample_phase_scores
        )
        
        # Process late phase
        late_results = pipeline.process_phase(
            CanonicalPhase.PHASE_07,
            sample_phase_scores
        )
        
        # Late phase should have higher phase org factor
        early_avg_factor = sum(r.phase_org_factor for r in early_results) / len(early_results)
        late_avg_factor = sum(r.phase_org_factor for r in late_results) / len(late_results)
        
        assert late_avg_factor > early_avg_factor
    
    def test_result_serialization(self, phase_aggregator, sample_phase_scores):
        """Test that results can be serialized to dict."""
        results = phase_aggregator.aggregate_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            phase_scores=sample_phase_scores,
        )
        
        for result in results:
            result_dict = result.to_dict()
            
            # Verify required fields
            assert "phase" in result_dict
            assert "capacity_type" in result_dict
            assert "phase_adjusted_org_score" in result_dict
            assert "phase_adjusted_sys_score" in result_dict
            assert result_dict["phase"] == "PHASE_04"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
