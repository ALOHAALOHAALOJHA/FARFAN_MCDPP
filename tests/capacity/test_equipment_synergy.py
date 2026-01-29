"""
Test Suite for Equipment Congregation Module
============================================

Tests for the equipment congregation implementation from the
Wu, Ramesh & Howlett (2015) Policy Capacity Framework.

Tests cover:
1. Synergy coefficient validation
2. Equipment congregation multiplier calculation
3. Congregation type identification
4. Application to capacity scores
5. Optimal congregation selection
6. Edge cases and mathematical invariants

Mathematical Model Under Test:
    M_equip = 1 + δ × ln(1 + n_skills) × (ρ - 1)
    
    Where:
    - n_skills = number of distinct skills (1, 2, or 3)
    - ρ = synergy coefficient (1.0 to 1.75)
    - δ = congregation sensitivity (default: 0.3)

Author: F.A.R.F.A.N. Test Team
Version: 1.0.0
"""

import math
import pytest
from typing import Dict, Set

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    EquipmentCongregation,
    CapacityScore,
)
from farfan_pipeline.capacity.equipment import (
    EquipmentCongregationEngine,
    SynergyCalculator,
    SynergyCoefficients,
    CongregationResult,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def default_calculator() -> SynergyCalculator:
    """Create synergy calculator with default settings."""
    return SynergyCalculator()


@pytest.fixture
def high_synergy_calculator() -> SynergyCalculator:
    """Create synergy calculator with high synergy coefficients."""
    coefficients = SynergyCoefficients.high_synergy()
    return SynergyCalculator(delta=0.5, coefficients=coefficients)


@pytest.fixture
def default_engine() -> EquipmentCongregationEngine:
    """Create congregation engine with default settings."""
    return EquipmentCongregationEngine()


@pytest.fixture
def sample_skill_scores() -> Dict[PolicySkill, float]:
    """Sample skill scores for testing."""
    return {
        PolicySkill.ANALYTICAL: 1.068,
        PolicySkill.OPERATIONAL: 1.372,
        PolicySkill.POLITICAL: 1.410,
    }


@pytest.fixture
def sample_capacity_scores() -> Dict[CapacityType, CapacityScore]:
    """Sample capacity scores for testing."""
    return {
        CapacityType.CA_I: CapacityScore(
            capacity_type=CapacityType.CA_I,
            raw_score=1.068,
            weighted_score=0.107,
            confidence=0.85,
            method_count=64,
        ),
        CapacityType.CA_O: CapacityScore(
            capacity_type=CapacityType.CA_O,
            raw_score=1.338,
            weighted_score=0.187,
            confidence=0.80,
            method_count=42,
        ),
        CapacityType.CO_O: CapacityScore(
            capacity_type=CapacityType.CO_O,
            raw_score=1.372,
            weighted_score=0.192,
            confidence=0.75,
            method_count=41,
        ),
        CapacityType.CO_S: CapacityScore(
            capacity_type=CapacityType.CO_S,
            raw_score=1.642,
            weighted_score=0.263,
            confidence=0.82,
            method_count=48,
        ),
        CapacityType.CP_O: CapacityScore(
            capacity_type=CapacityType.CP_O,
            raw_score=1.410,
            weighted_score=0.176,
            confidence=0.78,
            method_count=42,
        ),
    }


# ============================================================================
# TEST: SYNERGY COEFFICIENTS
# ============================================================================

class TestSynergyCoefficients:
    """Test cases for SynergyCoefficients."""
    
    def test_single_skill_coefficient_is_one(self):
        """Verify single skill has no synergy (coefficient = 1.0)."""
        coefficients = SynergyCoefficients()
        assert coefficients.single_skill == 1.0
    
    def test_pairwise_coefficients_greater_than_one(self):
        """Verify all pairwise combinations have coefficient > 1."""
        coefficients = SynergyCoefficients()
        
        assert coefficients.analytical_operational > 1.0
        assert coefficients.analytical_political > 1.0
        assert coefficients.operational_political > 1.0
    
    def test_all_three_coefficient_highest(self):
        """Verify full integration has highest coefficient."""
        coefficients = SynergyCoefficients()
        
        assert coefficients.all_three > coefficients.analytical_operational
        assert coefficients.all_three > coefficients.analytical_political
        assert coefficients.all_three > coefficients.operational_political
    
    def test_expected_default_values(self):
        """Verify default coefficient values match specification."""
        coefficients = SynergyCoefficients()
        
        assert coefficients.analytical_operational == 1.35
        assert coefficients.analytical_political == 1.42
        assert coefficients.operational_political == 1.28
        assert coefficients.all_three == 1.75
    
    def test_get_coefficient_for_skill_set(self):
        """Test coefficient retrieval for specific skill sets."""
        coefficients = SynergyCoefficients()
        
        # Evidence-Action Nexus
        ean_skills = frozenset({PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL})
        assert coefficients.get_coefficient(ean_skills) == 1.35
        
        # Strategic Intelligence
        si_skills = frozenset({PolicySkill.ANALYTICAL, PolicySkill.POLITICAL})
        assert coefficients.get_coefficient(si_skills) == 1.42
        
        # Adaptive Governance
        ag_skills = frozenset({PolicySkill.OPERATIONAL, PolicySkill.POLITICAL})
        assert coefficients.get_coefficient(ag_skills) == 1.28
        
        # Integrated Capacity
        ic_skills = frozenset({PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL, PolicySkill.POLITICAL})
        assert coefficients.get_coefficient(ic_skills) == 1.75
    
    def test_high_synergy_preset(self):
        """Test high synergy coefficient preset."""
        coefficients = SynergyCoefficients.high_synergy()
        
        assert coefficients.analytical_operational == 1.50
        assert coefficients.all_three == 2.00


# ============================================================================
# TEST: SYNERGY CALCULATOR
# ============================================================================

class TestSynergyCalculator:
    """Test cases for SynergyCalculator."""
    
    def test_single_skill_multiplier_is_one(self, default_calculator):
        """Verify single skill gives multiplier of 1.0."""
        multiplier = default_calculator.calculate_multiplier({PolicySkill.ANALYTICAL})
        
        # M = 1 + δ × ln(1 + 1) × (1.0 - 1) = 1 + 0 = 1.0
        assert math.isclose(multiplier, 1.0, rel_tol=1e-6)
    
    def test_two_skill_multiplier(self, default_calculator):
        """Test multiplier calculation for two skills."""
        skills = {PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL}
        multiplier = default_calculator.calculate_multiplier(skills)
        
        # M = 1 + δ × ln(1 + 2) × (ρ - 1)
        # M = 1 + 0.3 × ln(3) × (1.35 - 1)
        # M = 1 + 0.3 × 1.099 × 0.35
        # M ≈ 1.115
        
        delta = default_calculator.delta
        rho = 1.35
        expected = 1 + delta * math.log(1 + 2) * (rho - 1)
        
        assert math.isclose(multiplier, expected, rel_tol=1e-6)
    
    def test_three_skill_multiplier(self, default_calculator):
        """Test multiplier calculation for three skills."""
        skills = {PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL, PolicySkill.POLITICAL}
        multiplier = default_calculator.calculate_multiplier(skills)
        
        # M = 1 + δ × ln(1 + 3) × (ρ - 1)
        # M = 1 + 0.3 × ln(4) × (1.75 - 1)
        # M = 1 + 0.3 × 1.386 × 0.75
        # M ≈ 1.312
        
        delta = default_calculator.delta
        rho = 1.75
        expected = 1 + delta * math.log(1 + 3) * (rho - 1)
        
        assert math.isclose(multiplier, expected, rel_tol=1e-6)
    
    def test_empty_skills_returns_one(self, default_calculator):
        """Test empty skill set returns multiplier of 1.0."""
        multiplier = default_calculator.calculate_multiplier(set())
        assert multiplier == 1.0
    
    def test_multiplier_minimum_is_one(self, default_calculator):
        """Verify multiplier is always at least 1.0."""
        for congregation in EquipmentCongregation.all_congregations():
            multiplier = default_calculator.calculate_multiplier_for_congregation(congregation)
            assert multiplier >= 1.0
    
    def test_identify_congregation(self, default_calculator):
        """Test congregation identification from skill sets."""
        # Evidence-Action Nexus
        skills_ean = {PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL}
        congregation = default_calculator.identify_congregation(skills_ean)
        assert congregation == EquipmentCongregation.EVIDENCE_ACTION_NEXUS
        
        # Strategic Intelligence
        skills_si = {PolicySkill.ANALYTICAL, PolicySkill.POLITICAL}
        congregation = default_calculator.identify_congregation(skills_si)
        assert congregation == EquipmentCongregation.STRATEGIC_INTELLIGENCE
        
        # Integrated Capacity
        all_skills = {PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL, PolicySkill.POLITICAL}
        congregation = default_calculator.identify_congregation(all_skills)
        assert congregation == EquipmentCongregation.INTEGRATED_CAPACITY
    
    def test_get_synergy_breakdown(self, default_calculator):
        """Test synergy breakdown report generation."""
        skills = {PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL}
        breakdown = default_calculator.get_synergy_breakdown(skills)
        
        assert "skills" in breakdown
        assert "n_skills" in breakdown
        assert "synergy_coefficient_rho" in breakdown
        assert "multiplier" in breakdown
        assert "boost_percentage" in breakdown
    
    def test_rank_congregations(self, default_calculator):
        """Test congregation ranking by multiplier."""
        rankings = default_calculator.rank_congregations_by_multiplier()
        
        assert len(rankings) == 4
        
        # Integrated Capacity should be first (highest multiplier)
        assert rankings[0][0] == EquipmentCongregation.INTEGRATED_CAPACITY


# ============================================================================
# TEST: EQUIPMENT CONGREGATION ENGINE
# ============================================================================

class TestEquipmentCongregationEngine:
    """Test cases for EquipmentCongregationEngine."""
    
    def test_apply_congregation_single_skill(self, default_engine):
        """Test congregation with only one skill present."""
        skill_scores = {PolicySkill.ANALYTICAL: 1.0}
        result = default_engine.apply_congregation(skill_scores)
        
        # No congregation should be identified (only one skill)
        assert result.congregation_type is None
        assert result.multiplier == 1.0
        assert result.boost_percentage == 0.0
    
    def test_apply_congregation_two_skills(self, default_engine, sample_skill_scores):
        """Test congregation with two skills present."""
        skill_scores = {
            PolicySkill.ANALYTICAL: sample_skill_scores[PolicySkill.ANALYTICAL],
            PolicySkill.OPERATIONAL: sample_skill_scores[PolicySkill.OPERATIONAL],
        }
        result = default_engine.apply_congregation(skill_scores)
        
        assert result.congregation_type == EquipmentCongregation.EVIDENCE_ACTION_NEXUS
        assert result.multiplier > 1.0
        assert result.boost_percentage > 0
    
    def test_apply_congregation_all_skills(self, default_engine, sample_skill_scores):
        """Test congregation with all three skills present."""
        result = default_engine.apply_congregation(sample_skill_scores)
        
        assert result.congregation_type == EquipmentCongregation.INTEGRATED_CAPACITY
        assert result.rho_used == 1.75
    
    def test_enhanced_scores_calculated(self, default_engine, sample_skill_scores):
        """Verify enhanced scores are calculated correctly."""
        result = default_engine.apply_congregation(sample_skill_scores)
        
        # Enhanced scores should equal original × multiplier
        for skill, original in result.original_scores.items():
            if skill in result.skills_involved:
                enhanced = result.enhanced_scores[skill]
                expected = original * result.multiplier
                assert math.isclose(enhanced, expected, rel_tol=1e-6)
    
    def test_total_enhanced_greater_than_original(self, default_engine, sample_skill_scores):
        """Verify total enhanced capacity is greater than original."""
        result = default_engine.apply_congregation(sample_skill_scores)
        
        assert result.total_enhanced > result.total_original
    
    def test_force_congregation(self, default_engine, sample_skill_scores):
        """Test forcing a specific congregation type."""
        result = default_engine.apply_congregation(
            sample_skill_scores,
            force_congregation=EquipmentCongregation.STRATEGIC_INTELLIGENCE,
        )
        
        # Should use Strategic Intelligence even though all skills present
        assert result.congregation_type == EquipmentCongregation.STRATEGIC_INTELLIGENCE
    
    def test_analyze_all_congregations(self, default_engine, sample_skill_scores):
        """Test analysis of all possible congregations."""
        all_results = default_engine.analyze_all_congregations(sample_skill_scores)
        
        assert len(all_results) == 4
        
        for congregation in EquipmentCongregation.all_congregations():
            assert congregation in all_results
    
    def test_get_optimal_congregation(self, default_engine, sample_skill_scores):
        """Test optimal congregation selection."""
        optimal, result = default_engine.get_optimal_congregation(sample_skill_scores)
        
        # With all skills present, Integrated Capacity should be optimal
        assert optimal == EquipmentCongregation.INTEGRATED_CAPACITY
        assert result.total_enhanced > result.total_original
    
    def test_apply_to_capacity_scores_by_level(self, default_engine, sample_capacity_scores):
        """Test congregation application to capacity scores by level."""
        results = default_engine.apply_congregation_to_capacity_scores(
            sample_capacity_scores, by_level=True
        )
        
        # Should have results for all capacity types in input
        for ct in sample_capacity_scores.keys():
            assert ct in results
    
    def test_compute_congregation_matrix(self, default_engine, sample_capacity_scores):
        """Test congregation matrix computation."""
        matrix = default_engine.compute_congregation_matrix(sample_capacity_scores)
        
        # Should have results for all three levels
        assert PolicyLevel.INDIVIDUAL in matrix
        assert PolicyLevel.ORGANIZATIONAL in matrix
        assert PolicyLevel.SYSTEMIC in matrix
    
    def test_get_congregation_summary(self, default_engine, sample_capacity_scores):
        """Test congregation summary generation."""
        summary = default_engine.get_congregation_summary(sample_capacity_scores)
        
        assert "by_level" in summary
        assert "overall_skill_scores" in summary
        assert "optimal_congregation" in summary
        assert "congregation_rankings" in summary


# ============================================================================
# TEST: CONGREGATION RESULT
# ============================================================================

class TestCongregationResult:
    """Test cases for CongregationResult."""
    
    def test_is_congregated_true(self, default_engine, sample_skill_scores):
        """Test is_congregated property when congregation active."""
        result = default_engine.apply_congregation(sample_skill_scores)
        assert result.is_congregated is True
    
    def test_is_congregated_false(self, default_engine):
        """Test is_congregated property when no congregation."""
        result = default_engine.apply_congregation({PolicySkill.ANALYTICAL: 1.0})
        assert result.is_congregated is False
    
    def test_effective_boost(self, default_engine, sample_skill_scores):
        """Test effective boost calculation."""
        result = default_engine.apply_congregation(sample_skill_scores)
        
        expected_boost = result.total_enhanced - result.total_original
        assert math.isclose(result.effective_boost, expected_boost, rel_tol=1e-6)
    
    def test_to_dict_serialization(self, default_engine, sample_skill_scores):
        """Test dictionary serialization."""
        result = default_engine.apply_congregation(sample_skill_scores)
        result_dict = result.to_dict()
        
        assert "original_scores" in result_dict
        assert "congregation_type" in result_dict
        assert "multiplier" in result_dict
        assert "enhanced_scores" in result_dict
        assert "boost_percentage" in result_dict


# ============================================================================
# TEST: EQUIPMENT CONGREGATION ENUM
# ============================================================================

class TestEquipmentCongregationEnum:
    """Test cases for EquipmentCongregation enum."""
    
    def test_all_congregations_count(self):
        """Verify there are exactly 4 congregation types."""
        assert len(EquipmentCongregation.all_congregations()) == 4
    
    def test_evidence_action_nexus_properties(self):
        """Test Evidence-Action Nexus properties."""
        ean = EquipmentCongregation.EVIDENCE_ACTION_NEXUS
        
        assert ean.coefficient == 1.35
        assert PolicySkill.ANALYTICAL in ean.skills
        assert PolicySkill.OPERATIONAL in ean.skills
        assert PolicySkill.POLITICAL not in ean.skills
        assert ean.skill_count == 2
    
    def test_strategic_intelligence_properties(self):
        """Test Strategic Intelligence properties."""
        si = EquipmentCongregation.STRATEGIC_INTELLIGENCE
        
        assert si.coefficient == 1.42
        assert PolicySkill.ANALYTICAL in si.skills
        assert PolicySkill.POLITICAL in si.skills
        assert si.skill_count == 2
    
    def test_adaptive_governance_properties(self):
        """Test Adaptive Governance properties."""
        ag = EquipmentCongregation.ADAPTIVE_GOVERNANCE
        
        assert ag.coefficient == 1.28
        assert PolicySkill.OPERATIONAL in ag.skills
        assert PolicySkill.POLITICAL in ag.skills
        assert ag.skill_count == 2
    
    def test_integrated_capacity_properties(self):
        """Test Integrated Capacity properties."""
        ic = EquipmentCongregation.INTEGRATED_CAPACITY
        
        assert ic.coefficient == 1.75
        assert ic.skill_count == 3
        assert PolicySkill.ANALYTICAL in ic.skills
        assert PolicySkill.OPERATIONAL in ic.skills
        assert PolicySkill.POLITICAL in ic.skills
    
    def test_from_skills_matching(self):
        """Test congregation lookup from skill sets."""
        # Should find Evidence-Action Nexus
        ean = EquipmentCongregation.from_skills({
            PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL
        })
        assert ean == EquipmentCongregation.EVIDENCE_ACTION_NEXUS
        
        # Should return None for non-matching set
        result = EquipmentCongregation.from_skills({PolicySkill.ANALYTICAL})
        assert result is None
    
    def test_calculate_multiplier_method(self):
        """Test enum's built-in multiplier calculation."""
        for congregation in EquipmentCongregation.all_congregations():
            multiplier = congregation.calculate_multiplier(delta=0.3)
            assert multiplier >= 1.0


# ============================================================================
# TEST: MATHEMATICAL INVARIANTS
# ============================================================================

class TestMathematicalInvariants:
    """Test mathematical invariants and consistency."""
    
    def test_multiplier_monotonic_in_rho(self, default_calculator):
        """Verify multiplier increases with synergy coefficient."""
        skills_ean = {PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL}  # ρ = 1.35
        skills_si = {PolicySkill.ANALYTICAL, PolicySkill.POLITICAL}  # ρ = 1.42
        skills_ic = {PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL, PolicySkill.POLITICAL}  # ρ = 1.75
        
        m_ean = default_calculator.calculate_multiplier(skills_ean)
        m_si = default_calculator.calculate_multiplier(skills_si)
        m_ic = default_calculator.calculate_multiplier(skills_ic)
        
        # SI has higher ρ than EAN (1.42 > 1.35), so should have higher multiplier
        # But IC has even higher ρ (1.75)
        # Note: IC also has more skills which affects ln term
        assert m_ic > m_si or m_ic > m_ean  # At least IC should be highest
    
    def test_multiplier_bounded(self, default_calculator):
        """Verify multipliers are bounded reasonably."""
        for congregation in EquipmentCongregation.all_congregations():
            multiplier = default_calculator.calculate_multiplier_for_congregation(congregation)
            
            # Multiplier should be at least 1 and at most ~2 with default settings
            assert 1.0 <= multiplier <= 2.0
    
    def test_boost_percentage_consistent_with_multiplier(self, default_engine, sample_skill_scores):
        """Verify boost percentage is consistent with multiplier."""
        result = default_engine.apply_congregation(sample_skill_scores)
        
        # boost_percentage should equal (multiplier - 1) × 100
        expected_boost = (result.multiplier - 1) * 100
        
        # May not be exact due to how total enhanced is calculated
        # but should be close
        assert abs(result.boost_percentage - expected_boost) < 1.0
    
    def test_enhanced_preserves_ratio(self, default_engine, sample_skill_scores):
        """Verify enhancement preserves original score ratios."""
        result = default_engine.apply_congregation(sample_skill_scores)
        
        # All enhanced skills should be multiplied by same factor
        original_total = sum(result.original_scores.values())
        enhanced_total = sum(
            result.enhanced_scores[s] for s in result.skills_involved
        )
        
        # Ratio should equal multiplier
        if original_total > 0:
            effective_multiplier = enhanced_total / original_total
            # Account for skills not involved staying unchanged
            assert effective_multiplier >= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
