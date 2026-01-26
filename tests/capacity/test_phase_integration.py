"""
Test Suite for Phase-Capacity Integration Module
================================================

Tests for the phase-aware capacity framework that integrates the Wu Policy
Capacity Framework with FARFAN canonical phases.

Tests cover:
1. Canonical phase enumeration and navigation
2. Phase-capacity mapping validation
3. Phase-aware capacity score computation (Formula 7)
4. Cross-phase capacity flow analysis (Formula 8)
5. Phase progression index calculation (Formula 9)
6. PhaseCapacityAdapter functionality
7. Phase transition coherence
8. Edge cases and error handling

Mathematical Models Under Test:
    Formula 7: C_phase(p, t) = C_base(t) × φ_phase(p) × τ_transition(p, p-1)
    Formula 8: F_capacity(p1, p2) = Σ[C_phase(p2, t) × w_flow(t)] / Σ[C_phase(p1, t)]
    Formula 9: PPI = Σ[w_phase(p) × C_phase(p)] / Σ[C_ideal(p)]

Author: F.A.R.F.A.N. Test Team
Version: 2.0.0
"""

import math
import pytest
from typing import Dict, List

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    EpistemologicalLevel,
    CapacityScore,
)

from farfan_pipeline.capacity.phase_integration import (
    CanonicalPhase,
    PhaseCapacityMapping,
    DEFAULT_PHASE_CAPACITY_MAPPINGS,
    PhaseCapacityScore,
    CapacityFlowMetrics,
    PhaseProgressionIndex,
    PhaseCapacityAdapter,
)


# ============================================================================
# FIXTURE DEFINITIONS
# ============================================================================

@pytest.fixture
def sample_base_scores() -> List[CapacityScore]:
    """Create sample base capacity scores for testing."""
    return [
        CapacityScore(
            capacity_type=CapacityType.CA_I,
            raw_score=0.85,
            weighted_score=0.80,
            confidence=0.9,
            method_count=10,
            contributing_methods=["M001", "M002"],
        ),
        CapacityScore(
            capacity_type=CapacityType.CA_O,
            raw_score=0.90,
            weighted_score=0.88,
            confidence=0.85,
            method_count=8,
            contributing_methods=["M003", "M004"],
        ),
        CapacityScore(
            capacity_type=CapacityType.CO_I,
            raw_score=0.75,
            weighted_score=0.70,
            confidence=0.8,
            method_count=12,
            contributing_methods=["M005", "M006"],
        ),
        CapacityScore(
            capacity_type=CapacityType.CO_O,
            raw_score=0.82,
            weighted_score=0.78,
            confidence=0.88,
            method_count=9,
            contributing_methods=["M007", "M008"],
        ),
    ]


@pytest.fixture
def phase_adapter() -> PhaseCapacityAdapter:
    """Create a phase capacity adapter with default mappings."""
    return PhaseCapacityAdapter()


# ============================================================================
# CANONICAL PHASE TESTS
# ============================================================================

class TestCanonicalPhase:
    """Test suite for CanonicalPhase enumeration."""
    
    def test_phase_count(self):
        """Verify we have exactly 10 phases (0-9)."""
        all_phases = CanonicalPhase.all_phases()
        assert len(all_phases) == 10
    
    def test_phase_indices(self):
        """Verify phase indices are sequential from 0 to 9."""
        all_phases = CanonicalPhase.all_phases()
        indices = [p.index for p in all_phases]
        assert indices == list(range(10))
    
    def test_phase_from_index(self):
        """Test retrieving phases by index."""
        phase_4 = CanonicalPhase.from_index(4)
        assert phase_4 == CanonicalPhase.PHASE_04
        assert phase_4.index == 4
    
    def test_phase_from_invalid_index(self):
        """Test error handling for invalid phase index."""
        with pytest.raises(ValueError, match="Invalid phase index"):
            CanonicalPhase.from_index(99)
    
    def test_phase_navigation_next(self):
        """Test navigation to next phase."""
        phase_3 = CanonicalPhase.PHASE_03
        phase_4 = phase_3.next_phase()
        assert phase_4 == CanonicalPhase.PHASE_04
    
    def test_phase_navigation_prev(self):
        """Test navigation to previous phase."""
        phase_5 = CanonicalPhase.PHASE_05
        phase_4 = phase_5.prev_phase()
        assert phase_4 == CanonicalPhase.PHASE_04
    
    def test_phase_navigation_boundaries(self):
        """Test navigation at pipeline boundaries."""
        # First phase has no previous
        assert CanonicalPhase.PHASE_00.prev_phase() is None
        # Last phase has no next
        assert CanonicalPhase.PHASE_09.next_phase() is None
    
    def test_phase_distance(self):
        """Test distance calculation between phases."""
        phase_2 = CanonicalPhase.PHASE_02
        phase_7 = CanonicalPhase.PHASE_07
        
        distance = phase_2.distance_to(phase_7)
        assert distance == 5
        
        # Distance is symmetric
        assert phase_7.distance_to(phase_2) == 5
    
    def test_phase_properties(self):
        """Test phase property access."""
        phase = CanonicalPhase.PHASE_04
        
        assert phase.index == 4
        assert phase.phase_name == "Meso Aggregation"
        assert phase.code == "PHASE_04"
        assert "aggregation" in phase.description.lower()


# ============================================================================
# PHASE-CAPACITY MAPPING TESTS
# ============================================================================

class TestPhaseCapacityMapping:
    """Test suite for PhaseCapacityMapping."""
    
    def test_all_phases_have_mappings(self):
        """Verify all phases have capacity mappings defined."""
        all_phases = CanonicalPhase.all_phases()
        for phase in all_phases:
            assert phase in DEFAULT_PHASE_CAPACITY_MAPPINGS
    
    def test_mapping_structure(self):
        """Test basic mapping structure."""
        mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_04]
        
        assert mapping.phase == CanonicalPhase.PHASE_04
        assert len(mapping.primary_capacities) > 0
        assert len(mapping.secondary_capacities) >= 0
        assert 0.0 <= mapping.phase_relevance_weight <= 1.0
    
    def test_primary_secondary_disjoint(self):
        """Verify primary and secondary capacities don't overlap."""
        for mapping in DEFAULT_PHASE_CAPACITY_MAPPINGS.values():
            overlap = mapping.primary_capacities & mapping.secondary_capacities
            assert len(overlap) == 0, f"Phase {mapping.phase} has overlapping capacities"
    
    def test_capacity_weights(self):
        """Test capacity weight calculation."""
        mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_03]
        
        # Primary capacity should have weight 1.0
        primary_cap = list(mapping.primary_capacities)[0]
        assert mapping.get_capacity_weight(primary_cap) == 1.0
        
        # Secondary capacity should have weight 0.5
        if mapping.secondary_capacities:
            secondary_cap = list(mapping.secondary_capacities)[0]
            assert mapping.get_capacity_weight(secondary_cap) == 0.5
        
        # Non-relevant capacity should have weight 0.0
        non_relevant = CapacityType.CP_S  # Unlikely to be in Phase 3
        if non_relevant not in mapping.all_relevant_capacities:
            assert mapping.get_capacity_weight(non_relevant) == 0.0
    
    def test_is_relevant(self):
        """Test relevance checking."""
        mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_04]
        
        # Primary capacities are relevant
        for cap in mapping.primary_capacities:
            assert mapping.is_relevant(cap)
        
        # Secondary capacities are relevant
        for cap in mapping.secondary_capacities:
            assert mapping.is_relevant(cap)
    
    def test_phase_progression_in_mappings(self):
        """Test that mappings follow logical phase progression."""
        # Early phases should emphasize Individual-Operational
        early_mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_01]
        has_individual = any(
            c.level == PolicyLevel.INDIVIDUAL
            for c in early_mapping.primary_capacities
        )
        assert has_individual, "Early phases should have individual capacities"
        
        # Late phases should emphasize Systemic-Political
        late_mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_07]
        has_systemic = any(
            c.level == PolicyLevel.SYSTEMIC
            for c in late_mapping.primary_capacities
        )
        assert has_systemic, "Late phases should have systemic capacities"


# ============================================================================
# PHASE-AWARE CAPACITY SCORE TESTS
# ============================================================================

class TestPhaseCapacityScore:
    """Test suite for PhaseCapacityScore - Formula 7."""
    
    def test_phase_score_creation_without_previous(self):
        """Test creating phase score without previous phase (first phase)."""
        base_score = CapacityScore(
            capacity_type=CapacityType.CA_I,
            raw_score=0.85,
            weighted_score=0.80,
            confidence=0.9,
            method_count=10,
        )
        
        mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_03]
        
        phase_score = PhaseCapacityScore.from_base_score(
            phase=CanonicalPhase.PHASE_03,
            base_score=base_score,
            mapping=mapping,
            previous_phase_score=None,
        )
        
        assert phase_score.phase == CanonicalPhase.PHASE_03
        assert phase_score.capacity_type == CapacityType.CA_I
        assert phase_score.base_score == base_score
        assert phase_score.transition_coherence_factor == 1.0  # No previous phase
        assert phase_score.phase_adjusted_score > 0
    
    def test_phase_score_formula_7_components(self):
        """Test Formula 7 components in phase score calculation."""
        base_score = CapacityScore(
            capacity_type=CapacityType.CA_O,
            raw_score=0.90,
            weighted_score=0.88,
            confidence=0.85,
            method_count=8,
        )
        
        mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_04]
        
        phase_score = PhaseCapacityScore.from_base_score(
            phase=CanonicalPhase.PHASE_04,
            base_score=base_score,
            mapping=mapping,
            previous_phase_score=None,
        )
        
        # Verify Formula 7: C_phase = C_base × φ_phase × τ_transition
        expected_score = (
            base_score.weighted_score
            * phase_score.phase_relevance_multiplier
            * phase_score.transition_coherence_factor
        )
        
        assert abs(phase_score.phase_adjusted_score - expected_score) < 1e-6
    
    def test_phase_score_with_previous_coherent(self):
        """Test phase score with coherent transition (small change)."""
        # Create previous phase score
        prev_base = CapacityScore(
            capacity_type=CapacityType.CA_O,
            raw_score=0.85,
            weighted_score=0.82,
            confidence=0.88,
            method_count=7,
        )
        
        prev_mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_03]
        prev_phase_score = PhaseCapacityScore.from_base_score(
            phase=CanonicalPhase.PHASE_03,
            base_score=prev_base,
            mapping=prev_mapping,
        )
        
        # Create current phase score with small change
        curr_base = CapacityScore(
            capacity_type=CapacityType.CA_O,
            raw_score=0.87,  # Small increase
            weighted_score=0.84,
            confidence=0.88,
            method_count=8,
        )
        
        curr_mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_04]
        curr_phase_score = PhaseCapacityScore.from_base_score(
            phase=CanonicalPhase.PHASE_04,
            base_score=curr_base,
            mapping=curr_mapping,
            previous_phase_score=prev_phase_score,
        )
        
        # Coherent transition should have high coherence factor (close to 1.0)
        assert curr_phase_score.transition_coherence_factor > 0.9
    
    def test_phase_score_with_previous_incoherent(self):
        """Test phase score with incoherent transition (large change)."""
        # Create previous phase score
        prev_base = CapacityScore(
            capacity_type=CapacityType.CA_O,
            raw_score=0.30,
            weighted_score=0.28,
            confidence=0.70,
            method_count=3,
        )
        
        prev_mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_03]
        prev_phase_score = PhaseCapacityScore.from_base_score(
            phase=CanonicalPhase.PHASE_03,
            base_score=prev_base,
            mapping=prev_mapping,
        )
        
        # Create current phase score with large change
        curr_base = CapacityScore(
            capacity_type=CapacityType.CA_O,
            raw_score=0.95,  # Large increase
            weighted_score=0.92,
            confidence=0.95,
            method_count=15,
        )
        
        curr_mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_04]
        curr_phase_score = PhaseCapacityScore.from_base_score(
            phase=CanonicalPhase.PHASE_04,
            base_score=curr_base,
            mapping=curr_mapping,
            previous_phase_score=prev_phase_score,
        )
        
        # Incoherent transition should have lower coherence factor
        assert curr_phase_score.transition_coherence_factor < 0.5
    
    def test_contribution_ratio(self):
        """Test contribution ratio calculation."""
        base_score = CapacityScore(
            capacity_type=CapacityType.CA_I,
            raw_score=0.80,
            weighted_score=0.75,
            confidence=0.85,
            method_count=10,
        )
        
        mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_03]
        
        phase_score = PhaseCapacityScore.from_base_score(
            phase=CanonicalPhase.PHASE_03,
            base_score=base_score,
            mapping=mapping,
        )
        
        contribution_ratio = phase_score.get_contribution_ratio()
        
        # Contribution ratio should be between 0 and mapping relevance
        assert 0 <= contribution_ratio <= mapping.phase_relevance_weight
    
    def test_phase_score_serialization(self):
        """Test phase score to_dict conversion."""
        base_score = CapacityScore(
            capacity_type=CapacityType.CO_O,
            raw_score=0.88,
            weighted_score=0.85,
            confidence=0.90,
            method_count=12,
        )
        
        mapping = DEFAULT_PHASE_CAPACITY_MAPPINGS[CanonicalPhase.PHASE_04]
        
        phase_score = PhaseCapacityScore.from_base_score(
            phase=CanonicalPhase.PHASE_04,
            base_score=base_score,
            mapping=mapping,
        )
        
        score_dict = phase_score.to_dict()
        
        # Verify required fields
        assert "phase" in score_dict
        assert "phase_index" in score_dict
        assert "capacity_type" in score_dict
        assert "phase_adjusted_score" in score_dict
        assert score_dict["phase"] == "PHASE_04"
        assert score_dict["phase_index"] == 4


# ============================================================================
# CAPACITY FLOW METRICS TESTS
# ============================================================================

class TestCapacityFlowMetrics:
    """Test suite for CapacityFlowMetrics - Formula 8."""
    
    def test_flow_analysis_basic(self, sample_base_scores):
        """Test basic flow analysis between phases."""
        adapter = PhaseCapacityAdapter()
        
        # Create source phase scores
        source_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_03,
            base_scores=sample_base_scores,
        )
        
        # Create target phase scores
        target_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            base_scores=sample_base_scores,
            previous_phase_scores=source_scores,
        )
        
        # Analyze flow
        flow_metrics = CapacityFlowMetrics.analyze_flow(source_scores, target_scores)
        
        assert flow_metrics.source_phase == CanonicalPhase.PHASE_03
        assert flow_metrics.target_phase == CanonicalPhase.PHASE_04
        assert flow_metrics.source_total_capacity > 0
        assert flow_metrics.target_total_capacity > 0
    
    def test_flow_formula_8_calculation(self, sample_base_scores):
        """Test Formula 8: capacity flow ratio calculation."""
        adapter = PhaseCapacityAdapter()
        
        source_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_03,
            base_scores=sample_base_scores,
        )
        
        target_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            base_scores=sample_base_scores,
            previous_phase_scores=source_scores,
        )
        
        flow_metrics = CapacityFlowMetrics.analyze_flow(source_scores, target_scores)
        
        # Verify Formula 8
        expected_ratio = (
            flow_metrics.target_total_capacity / flow_metrics.source_total_capacity
        )
        assert abs(flow_metrics.capacity_flow_ratio - expected_ratio) < 1e-6
    
    def test_flow_growth_rate(self, sample_base_scores):
        """Test capacity growth rate calculation."""
        adapter = PhaseCapacityAdapter()
        
        source_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_03,
            base_scores=sample_base_scores,
        )
        
        target_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            base_scores=sample_base_scores,
            previous_phase_scores=source_scores,
        )
        
        flow_metrics = CapacityFlowMetrics.analyze_flow(source_scores, target_scores)
        
        # Growth rate should be consistent with delta/source
        expected_growth = (
            (flow_metrics.capacity_delta / flow_metrics.source_total_capacity) * 100.0
        )
        assert abs(flow_metrics.capacity_growth_rate - expected_growth) < 1e-6
    
    def test_flow_coherence(self, sample_base_scores):
        """Test flow coherence metric."""
        adapter = PhaseCapacityAdapter()
        
        source_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_03,
            base_scores=sample_base_scores,
        )
        
        target_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            base_scores=sample_base_scores,
            previous_phase_scores=source_scores,
        )
        
        flow_metrics = CapacityFlowMetrics.analyze_flow(source_scores, target_scores)
        
        # Coherence should be between 0 and 1
        assert 0 <= flow_metrics.flow_coherence <= 1
    
    def test_flow_serialization(self, sample_base_scores):
        """Test flow metrics to_dict conversion."""
        adapter = PhaseCapacityAdapter()
        
        source_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_03,
            base_scores=sample_base_scores,
        )
        
        target_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            base_scores=sample_base_scores,
            previous_phase_scores=source_scores,
        )
        
        flow_metrics = CapacityFlowMetrics.analyze_flow(source_scores, target_scores)
        flow_dict = flow_metrics.to_dict()
        
        # Verify required fields
        assert "source_phase" in flow_dict
        assert "target_phase" in flow_dict
        assert "capacity_flow_ratio" in flow_dict
        assert "flow_coherence" in flow_dict


# ============================================================================
# PHASE PROGRESSION INDEX TESTS
# ============================================================================

class TestPhaseProgressionIndex:
    """Test suite for PhaseProgressionIndex - Formula 9."""
    
    def test_ppi_calculation(self, sample_base_scores):
        """Test Phase Progression Index calculation."""
        adapter = PhaseCapacityAdapter()
        
        # Create scores for multiple phases
        all_phase_scores = {}
        for i in range(3, 7):  # Phases 3-6
            phase = CanonicalPhase.from_index(i)
            prev_scores = all_phase_scores.get(CanonicalPhase.from_index(i-1)) if i > 3 else None
            
            phase_scores = adapter.compute_phase_capacity(
                phase=phase,
                base_scores=sample_base_scores,
                previous_phase_scores=prev_scores,
            )
            all_phase_scores[phase] = phase_scores
        
        # Calculate PPI
        ppi = PhaseProgressionIndex.calculate(all_phase_scores)
        
        # PPI should be between 0 and some reasonable upper bound
        assert ppi.ppi_score >= 0
        assert len(ppi.phase_scores) == 4  # We created 4 phases
    
    def test_ppi_strongest_weakest_phases(self, sample_base_scores):
        """Test identification of strongest and weakest phases."""
        adapter = PhaseCapacityAdapter()
        
        all_phase_scores = {}
        for i in range(3, 7):
            phase = CanonicalPhase.from_index(i)
            prev_scores = all_phase_scores.get(CanonicalPhase.from_index(i-1)) if i > 3 else None
            
            phase_scores = adapter.compute_phase_capacity(
                phase=phase,
                base_scores=sample_base_scores,
                previous_phase_scores=prev_scores,
            )
            all_phase_scores[phase] = phase_scores
        
        ppi = PhaseProgressionIndex.calculate(all_phase_scores)
        
        # Should identify top 3 and bottom 3 phases
        assert len(ppi.strongest_phases) <= 3
        assert len(ppi.weakest_phases) <= 3
    
    def test_ppi_bottleneck_detection(self, sample_base_scores):
        """Test bottleneck phase detection."""
        adapter = PhaseCapacityAdapter()
        
        all_phase_scores = {}
        for i in range(3, 7):
            phase = CanonicalPhase.from_index(i)
            prev_scores = all_phase_scores.get(CanonicalPhase.from_index(i-1)) if i > 3 else None
            
            phase_scores = adapter.compute_phase_capacity(
                phase=phase,
                base_scores=sample_base_scores,
                previous_phase_scores=prev_scores,
            )
            all_phase_scores[phase] = phase_scores
        
        ppi = PhaseProgressionIndex.calculate(all_phase_scores)
        
        # Should identify a bottleneck
        assert ppi.bottleneck_phase is not None
        assert ppi.bottleneck_severity >= 0
    
    def test_ppi_serialization(self, sample_base_scores):
        """Test PPI to_dict conversion."""
        adapter = PhaseCapacityAdapter()
        
        all_phase_scores = {}
        for i in range(3, 5):
            phase = CanonicalPhase.from_index(i)
            prev_scores = all_phase_scores.get(CanonicalPhase.from_index(i-1)) if i > 3 else None
            
            phase_scores = adapter.compute_phase_capacity(
                phase=phase,
                base_scores=sample_base_scores,
                previous_phase_scores=prev_scores,
            )
            all_phase_scores[phase] = phase_scores
        
        ppi = PhaseProgressionIndex.calculate(all_phase_scores)
        ppi_dict = ppi.to_dict()
        
        # Verify required fields
        assert "ppi_score" in ppi_dict
        assert "strongest_phases" in ppi_dict
        assert "weakest_phases" in ppi_dict
        assert "bottleneck_phase" in ppi_dict


# ============================================================================
# PHASE CAPACITY ADAPTER TESTS
# ============================================================================

class TestPhaseCapacityAdapter:
    """Test suite for PhaseCapacityAdapter."""
    
    def test_adapter_initialization(self):
        """Test adapter initialization with default mappings."""
        adapter = PhaseCapacityAdapter()
        assert adapter.phase_mappings is not None
        assert len(adapter.phase_mappings) == 10  # All 10 phases
    
    def test_adapter_custom_mappings(self):
        """Test adapter initialization with custom mappings."""
        custom_mappings = {
            CanonicalPhase.PHASE_00: PhaseCapacityMapping(
                phase=CanonicalPhase.PHASE_00,
                primary_capacities=frozenset([CapacityType.CO_I]),
                secondary_capacities=frozenset([]),
                phase_relevance_weight=0.5,
            ),
        }
        
        adapter = PhaseCapacityAdapter(phase_mappings=custom_mappings)
        assert adapter.phase_mappings == custom_mappings
    
    def test_compute_phase_capacity(self, sample_base_scores, phase_adapter):
        """Test computing phase-aware capacity scores."""
        phase_scores = phase_adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            base_scores=sample_base_scores,
        )
        
        assert len(phase_scores) == len(sample_base_scores)
        assert all(isinstance(s, PhaseCapacityScore) for s in phase_scores)
        assert all(s.phase == CanonicalPhase.PHASE_04 for s in phase_scores)
    
    def test_compute_with_previous_phase(self, sample_base_scores, phase_adapter):
        """Test computing scores with previous phase context."""
        # Compute Phase 3 scores
        phase3_scores = phase_adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_03,
            base_scores=sample_base_scores,
        )
        
        # Compute Phase 4 scores with Phase 3 context
        phase4_scores = phase_adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            base_scores=sample_base_scores,
            previous_phase_scores=phase3_scores,
        )
        
        # All Phase 4 scores should have previous phase context
        for score in phase4_scores:
            prev_score = next(
                (s for s in phase3_scores if s.capacity_type == score.capacity_type),
                None
            )
            if prev_score:
                assert score.previous_phase_score is not None
    
    def test_analyze_phase_transition(self, sample_base_scores, phase_adapter):
        """Test phase transition analysis."""
        source_scores = phase_adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_03,
            base_scores=sample_base_scores,
        )
        
        target_scores = phase_adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            base_scores=sample_base_scores,
            previous_phase_scores=source_scores,
        )
        
        flow_metrics = phase_adapter.analyze_phase_transition(
            source_phase=CanonicalPhase.PHASE_03,
            target_phase=CanonicalPhase.PHASE_04,
            source_scores=source_scores,
            target_scores=target_scores,
        )
        
        assert isinstance(flow_metrics, CapacityFlowMetrics)
        assert flow_metrics.source_phase == CanonicalPhase.PHASE_03
        assert flow_metrics.target_phase == CanonicalPhase.PHASE_04
    
    def test_compute_progression_index(self, sample_base_scores, phase_adapter):
        """Test progression index computation."""
        all_phase_scores = {}
        for i in range(3, 6):
            phase = CanonicalPhase.from_index(i)
            prev_scores = all_phase_scores.get(CanonicalPhase.from_index(i-1)) if i > 3 else None
            
            phase_scores = phase_adapter.compute_phase_capacity(
                phase=phase,
                base_scores=sample_base_scores,
                previous_phase_scores=prev_scores,
            )
            all_phase_scores[phase] = phase_scores
        
        ppi = phase_adapter.compute_progression_index(all_phase_scores)
        
        assert isinstance(ppi, PhaseProgressionIndex)
        assert ppi.ppi_score >= 0
    
    def test_get_phase_capacity_profile(self, phase_adapter):
        """Test retrieving phase capacity profile."""
        profile = phase_adapter.get_phase_capacity_profile(CanonicalPhase.PHASE_04)
        
        assert isinstance(profile, PhaseCapacityMapping)
        assert profile.phase == CanonicalPhase.PHASE_04
    
    def test_invalid_phase_error(self, phase_adapter):
        """Test error handling for phase without mapping."""
        # Remove a phase mapping to test error
        adapter = PhaseCapacityAdapter(phase_mappings={})
        
        with pytest.raises(ValueError, match="No mapping defined"):
            adapter.get_phase_capacity_profile(CanonicalPhase.PHASE_04)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhaseIntegrationComplete:
    """Complete integration tests for phase-capacity framework."""
    
    def test_full_pipeline_capacity_tracking(self, sample_base_scores):
        """Test tracking capacity through complete pipeline."""
        adapter = PhaseCapacityAdapter()
        
        # Track capacity through Phases 3-7
        all_phase_scores = {}
        previous_scores = None
        
        for i in range(3, 8):
            phase = CanonicalPhase.from_index(i)
            
            phase_scores = adapter.compute_phase_capacity(
                phase=phase,
                base_scores=sample_base_scores,
                previous_phase_scores=previous_scores,
            )
            
            all_phase_scores[phase] = phase_scores
            previous_scores = phase_scores
        
        # Verify we tracked 5 phases
        assert len(all_phase_scores) == 5
        
        # Compute overall progression
        ppi = adapter.compute_progression_index(all_phase_scores)
        assert ppi.ppi_score >= 0
        
        # Analyze all transitions
        transitions = []
        for i in range(3, 7):
            source_phase = CanonicalPhase.from_index(i)
            target_phase = CanonicalPhase.from_index(i + 1)
            
            flow_metrics = adapter.analyze_phase_transition(
                source_phase=source_phase,
                target_phase=target_phase,
                source_scores=all_phase_scores[source_phase],
                target_scores=all_phase_scores[target_phase],
            )
            transitions.append(flow_metrics)
        
        # Verify all transitions analyzed
        assert len(transitions) == 4
    
    def test_capacity_evolution_consistency(self, sample_base_scores):
        """Test that capacity evolution maintains consistency."""
        adapter = PhaseCapacityAdapter()
        
        # Compute consecutive phase scores
        phase3_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_03,
            base_scores=sample_base_scores,
        )
        
        phase4_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_04,
            base_scores=sample_base_scores,
            previous_phase_scores=phase3_scores,
        )
        
        phase5_scores = adapter.compute_phase_capacity(
            phase=CanonicalPhase.PHASE_05,
            base_scores=sample_base_scores,
            previous_phase_scores=phase4_scores,
        )
        
        # Verify capacity types are consistent
        types_p3 = {s.capacity_type for s in phase3_scores}
        types_p4 = {s.capacity_type for s in phase4_scores}
        types_p5 = {s.capacity_type for s in phase5_scores}
        
        assert types_p3 == types_p4 == types_p5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
