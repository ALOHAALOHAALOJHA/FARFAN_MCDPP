"""
Equipment Congregation Module
=============================

This module implements the Equipment Congregation calculations for the
Wu, Ramesh & Howlett (2015) Policy Capacity Framework.

Equipment Congregation Theory:
-----------------------------
Equipment Congregation refers to how different capacity skills are grouped
and combined, creating SYNERGISTIC effects beyond simple addition.

When multiple skills are combined, they produce MULTIPLICATIVE gains:

    Simple Addition:    CA + CO = 2.0 units
    With Congregation:  CA ⊗ CO = 2.0 × 1.35 = 2.7 units (+35% boost)

Mathematical Model - Formula 3: Equipment Congregation Multiplier
-----------------------------------------------------------------
M_equip(skills) = 1 + δ × ln(1 + n_skills) × (ρ - 1)

Where:
- n_skills = number of distinct skills congregated (1, 2, or 3)
- ρ = synergy coefficient (1.28 to 1.75)
- δ = 1.0 (congregation strength parameter)

Four Equipment Types:
--------------------
1. Evidence-Action Nexus (Analytical + Operational)
   - Synergy Coefficient (ρ): 1.35
   - Combines analytical rigor with operational implementation capacity
   
2. Strategic Intelligence (Analytical + Political)
   - Synergy Coefficient (ρ): 1.42
   - Merges data-driven analysis with political feasibility assessment
   
3. Adaptive Governance (Operational + Political)
   - Synergy Coefficient (ρ): 1.28
   - Unites execution capacity with political legitimacy
   
4. Integrated Capacity (All Three Skills)
   - Synergy Coefficient (ρ): 1.75
   - The complete trinity: evidence, execution, and legitimacy

Author: F.A.R.F.A.N. Core Team
Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import (
    Dict,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    Any,
)

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    EquipmentCongregation,
    CapacityScore,
    AggregatedCapacity,
)


# ============================================================================
# SYNERGY CALCULATOR
# ============================================================================

@dataclass
class SynergyCoefficients:
    """
    Synergy coefficients for different skill combinations.
    
    These coefficients represent the multiplicative boost obtained
    when combining multiple policy skills. The values are derived
    from theoretical analysis of skill complementarity:
    
    - Single skill (1.0): No synergy, baseline capacity
    - Evidence-Action (1.35): Analytical + Operational synergy
    - Strategic Intelligence (1.42): Analytical + Political synergy
    - Adaptive Governance (1.28): Operational + Political synergy
    - Integrated (1.75): All three skills, maximum synergy
    
    The asymmetry in pairwise coefficients reflects that:
    - A+P synergy is highest (evidence+legitimacy is crucial)
    - A+O synergy is second (evidence+execution is common)
    - O+P synergy is lowest (execution+legitimacy without evidence is limited)
    """
    
    # Single skill - no synergy
    single_skill: float = 1.00
    
    # Pairwise combinations
    analytical_operational: float = 1.35
    analytical_political: float = 1.42
    operational_political: float = 1.28
    
    # Complete combination
    all_three: float = 1.75
    
    def get_coefficient(self, skills: FrozenSet[PolicySkill]) -> float:
        """
        Get synergy coefficient for a set of skills.
        
        Args:
            skills: Set of skills being combined
            
        Returns:
            Synergy coefficient (ρ)
        """
        if len(skills) == 1:
            return self.single_skill
        
        if len(skills) == 3:
            return self.all_three
        
        # Pairwise
        if PolicySkill.ANALYTICAL in skills and PolicySkill.OPERATIONAL in skills:
            return self.analytical_operational
        if PolicySkill.ANALYTICAL in skills and PolicySkill.POLITICAL in skills:
            return self.analytical_political
        if PolicySkill.OPERATIONAL in skills and PolicySkill.POLITICAL in skills:
            return self.operational_political
        
        return self.single_skill
    
    @classmethod
    def default(cls) -> "SynergyCoefficients":
        """Create default coefficients."""
        return cls()
    
    @classmethod
    def high_synergy(cls) -> "SynergyCoefficients":
        """Configuration with enhanced synergy effects."""
        return cls(
            analytical_operational=1.50,
            analytical_political=1.60,
            operational_political=1.40,
            all_three=2.00,
        )
    
    @classmethod
    def conservative(cls) -> "SynergyCoefficients":
        """Conservative coefficients with modest synergy effects."""
        return cls(
            analytical_operational=1.20,
            analytical_political=1.25,
            operational_political=1.15,
            all_three=1.50,
        )


class SynergyCalculator:
    """
    Calculator for equipment congregation synergies.
    
    Implements the equipment congregation multiplier formula:
    M_equip = 1 + δ × ln(1 + n_skills) × (ρ - 1)
    
    Where:
    - n_skills: Number of distinct skills
    - ρ: Synergy coefficient for the skill combination
    - δ: Congregation strength parameter
    
    Usage:
        calculator = SynergyCalculator()
        
        # Calculate multiplier for specific skills
        multiplier = calculator.calculate_multiplier({
            PolicySkill.ANALYTICAL,
            PolicySkill.OPERATIONAL
        })
        
        # Get congregation for skills
        congregation = calculator.identify_congregation({
            PolicySkill.ANALYTICAL,
            PolicySkill.OPERATIONAL
        })
    """
    
    def __init__(
        self,
        delta: float = 0.3,
        coefficients: Optional[SynergyCoefficients] = None,
    ):
        """
        Initialize synergy calculator.
        
        Args:
            delta: Congregation strength parameter (δ)
            coefficients: Synergy coefficients (uses default if not provided)
        """
        self.delta = delta
        self.coefficients = coefficients or SynergyCoefficients.default()
    
    def calculate_multiplier(
        self,
        skills: Union[Set[PolicySkill], FrozenSet[PolicySkill]],
    ) -> float:
        """
        Calculate equipment congregation multiplier.
        
        Formula: M_equip = 1 + δ × ln(1 + n_skills) × (ρ - 1)
        
        Args:
            skills: Set of skills being combined
            
        Returns:
            Multiplier value (≥1.0)
        """
        if not skills:
            return 1.0
        
        skills_frozen = frozenset(skills)
        n_skills = len(skills_frozen)
        rho = self.coefficients.get_coefficient(skills_frozen)
        
        # Apply formula
        multiplier = 1.0 + self.delta * math.log(1 + n_skills) * (rho - 1)
        return max(1.0, multiplier)  # Ensure minimum of 1.0
    
    def calculate_multiplier_for_congregation(
        self,
        congregation: EquipmentCongregation,
    ) -> float:
        """
        Calculate multiplier for a specific equipment congregation.
        
        Args:
            congregation: The equipment congregation type
            
        Returns:
            Multiplier value
        """
        return self.calculate_multiplier(congregation.skills)
    
    def identify_congregation(
        self,
        skills: Union[Set[PolicySkill], FrozenSet[PolicySkill]],
    ) -> Optional[EquipmentCongregation]:
        """
        Identify which equipment congregation matches a skill set.
        
        Args:
            skills: Set of skills to match
            
        Returns:
            Matching EquipmentCongregation or None
        """
        return EquipmentCongregation.from_skills(set(skills))
    
    def get_synergy_breakdown(
        self,
        skills: Union[Set[PolicySkill], FrozenSet[PolicySkill]],
    ) -> Dict[str, Any]:
        """
        Get detailed breakdown of synergy calculation.
        
        Args:
            skills: Set of skills being combined
            
        Returns:
            Dictionary with calculation details
        """
        skills_frozen = frozenset(skills)
        n_skills = len(skills_frozen)
        rho = self.coefficients.get_coefficient(skills_frozen)
        congregation = self.identify_congregation(skills_frozen)
        multiplier = self.calculate_multiplier(skills_frozen)
        
        return {
            "skills": [s.value for s in skills_frozen],
            "n_skills": n_skills,
            "synergy_coefficient_rho": rho,
            "congregation_delta": self.delta,
            "congregation_type": congregation.name if congregation else None,
            "multiplier": round(multiplier, 4),
            "formula": f"M = 1 + {self.delta} × ln(1 + {n_skills}) × ({rho} - 1)",
            "boost_percentage": round((multiplier - 1) * 100, 2),
        }
    
    def rank_congregations_by_multiplier(self) -> List[Tuple[EquipmentCongregation, float]]:
        """
        Rank all equipment congregations by their multiplier value.
        
        Returns:
            List of (congregation, multiplier) tuples, sorted descending
        """
        rankings = [
            (congregation, self.calculate_multiplier_for_congregation(congregation))
            for congregation in EquipmentCongregation.all_congregations()
        ]
        return sorted(rankings, key=lambda x: x[1], reverse=True)


# ============================================================================
# CONGREGATION RESULT
# ============================================================================

@dataclass
class CongregationResult:
    """
    Result of applying equipment congregation to capacity scores.
    """
    
    # Input
    original_scores: Dict[PolicySkill, float]
    congregation_type: Optional[EquipmentCongregation]
    
    # Calculation details
    multiplier: float
    delta_used: float
    rho_used: float
    
    # Output
    enhanced_scores: Dict[PolicySkill, float]
    total_original: float
    total_enhanced: float
    
    # Analysis
    boost_percentage: float
    skills_involved: Set[PolicySkill]
    
    @property
    def is_congregated(self) -> bool:
        """Check if any congregation was applied."""
        return self.congregation_type is not None
    
    @property
    def effective_boost(self) -> float:
        """Calculate effective boost amount."""
        return self.total_enhanced - self.total_original
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "original_scores": {s.value: v for s, v in self.original_scores.items()},
            "congregation_type": self.congregation_type.name if self.congregation_type else None,
            "multiplier": round(self.multiplier, 4),
            "delta_used": self.delta_used,
            "rho_used": self.rho_used,
            "enhanced_scores": {s.value: round(v, 4) for s, v in self.enhanced_scores.items()},
            "total_original": round(self.total_original, 4),
            "total_enhanced": round(self.total_enhanced, 4),
            "boost_percentage": round(self.boost_percentage, 2),
            "skills_involved": [s.value for s in self.skills_involved],
        }


# ============================================================================
# EQUIPMENT CONGREGATION ENGINE
# ============================================================================

class EquipmentCongregationEngine:
    """
    Engine for applying equipment congregation effects to capacity scores.
    
    This class orchestrates the application of synergy multipliers to
    capacity scores, considering which skills are present and how they
    interact to produce enhanced policy capacity.
    
    The engine supports:
    - Automatic congregation detection based on present skills
    - Manual congregation specification
    - Partial congregation (when not all skill combinations are present)
    - Multiple congregation layer effects
    
    Usage:
        engine = EquipmentCongregationEngine()
        
        # Apply congregation to scores
        result = engine.apply_congregation({
            PolicySkill.ANALYTICAL: 1.068,
            PolicySkill.OPERATIONAL: 1.372,
        })
        
        # Get all possible congregations
        all_results = engine.analyze_all_congregations(capacity_scores)
    """
    
    def __init__(
        self,
        delta: float = 0.3,
        coefficients: Optional[SynergyCoefficients] = None,
    ):
        """
        Initialize congregation engine.
        
        Args:
            delta: Congregation strength parameter
            coefficients: Synergy coefficients
        """
        self.calculator = SynergyCalculator(delta, coefficients)
        self.delta = delta
    
    def apply_congregation(
        self,
        skill_scores: Dict[PolicySkill, float],
        force_congregation: Optional[EquipmentCongregation] = None,
        threshold: float = 0.0,
    ) -> CongregationResult:
        """
        Apply equipment congregation effects to skill scores.
        
        The congregation is determined automatically based on which skills
        have scores above the threshold, unless force_congregation is specified.
        
        Args:
            skill_scores: Dictionary mapping skills to their scores
            force_congregation: Optionally force a specific congregation type
            threshold: Minimum score for a skill to be considered present
            
        Returns:
            CongregationResult with enhanced scores
        """
        # Determine present skills
        present_skills = {
            skill for skill, score in skill_scores.items()
            if score > threshold
        }
        
        # Identify congregation
        if force_congregation:
            congregation = force_congregation
            skills_for_multiplier = congregation.skills
        else:
            congregation = self.calculator.identify_congregation(present_skills)
            skills_for_multiplier = present_skills
        
        # Calculate multiplier
        multiplier = self.calculator.calculate_multiplier(skills_for_multiplier)
        rho = self.calculator.coefficients.get_coefficient(frozenset(skills_for_multiplier))
        
        # Apply multiplier to all present skills
        enhanced_scores = {}
        for skill, score in skill_scores.items():
            if skill in present_skills:
                enhanced_scores[skill] = score * multiplier
            else:
                enhanced_scores[skill] = score
        
        # Calculate totals
        total_original = sum(skill_scores.values())
        total_enhanced = sum(enhanced_scores.values())
        boost_pct = ((total_enhanced / total_original) - 1) * 100 if total_original > 0 else 0
        
        return CongregationResult(
            original_scores=skill_scores,
            congregation_type=congregation,
            multiplier=multiplier,
            delta_used=self.delta,
            rho_used=rho,
            enhanced_scores=enhanced_scores,
            total_original=total_original,
            total_enhanced=total_enhanced,
            boost_percentage=boost_pct,
            skills_involved=present_skills,
        )
    
    def apply_congregation_to_capacity_scores(
        self,
        capacity_scores: Dict[CapacityType, CapacityScore],
        by_level: bool = True,
    ) -> Dict[CapacityType, Tuple[CapacityScore, float]]:
        """
        Apply congregation effects to full capacity score matrix.
        
        Args:
            capacity_scores: All capacity scores (9 types)
            by_level: If True, apply congregation per level. If False, global.
            
        Returns:
            Dictionary mapping each capacity type to (score, multiplier) tuples
        """
        results = {}
        
        if by_level:
            # Apply congregation separately for each level
            for level in PolicyLevel.all_levels():
                # Get skills present at this level
                level_scores = {
                    ct.skill: capacity_scores[ct].raw_score
                    for ct in CapacityType.by_level(level)
                    if ct in capacity_scores and capacity_scores[ct].raw_score > 0
                }
                
                # Calculate congregation for this level
                congregation_result = self.apply_congregation(level_scores)
                
                # Store results
                for ct in CapacityType.by_level(level):
                    if ct in capacity_scores:
                        enhanced_score = congregation_result.enhanced_scores.get(
                            ct.skill, capacity_scores[ct].raw_score
                        )
                        results[ct] = (
                            capacity_scores[ct],
                            congregation_result.multiplier if ct.skill in congregation_result.skills_involved else 1.0,
                        )
        else:
            # Global congregation across all levels
            all_skills = {}
            for ct, score in capacity_scores.items():
                if score.raw_score > 0:
                    skill = ct.skill
                    all_skills[skill] = all_skills.get(skill, 0) + score.raw_score
            
            congregation_result = self.apply_congregation(all_skills)
            
            for ct, score in capacity_scores.items():
                results[ct] = (
                    score,
                    congregation_result.multiplier if ct.skill in congregation_result.skills_involved else 1.0,
                )
        
        return results
    
    def analyze_all_congregations(
        self,
        skill_scores: Dict[PolicySkill, float],
    ) -> Dict[EquipmentCongregation, CongregationResult]:
        """
        Analyze effects of all possible congregations on given scores.
        
        Args:
            skill_scores: Base skill scores
            
        Returns:
            Dictionary mapping each congregation to its result
        """
        results = {}
        
        for congregation in EquipmentCongregation.all_congregations():
            result = self.apply_congregation(
                skill_scores,
                force_congregation=congregation,
            )
            results[congregation] = result
        
        return results
    
    def get_optimal_congregation(
        self,
        skill_scores: Dict[PolicySkill, float],
    ) -> Tuple[Optional[EquipmentCongregation], CongregationResult]:
        """
        Find the congregation that maximizes total enhanced capacity.
        
        Args:
            skill_scores: Base skill scores
            
        Returns:
            Tuple of (optimal congregation, result)
        """
        all_results = self.analyze_all_congregations(skill_scores)
        
        best_congregation = None
        best_result = None
        best_total = 0.0
        
        for congregation, result in all_results.items():
            # Check if all required skills are present
            required_skills = congregation.skills
            present_skills = {s for s, v in skill_scores.items() if v > 0}
            
            if required_skills.issubset(present_skills):
                if result.total_enhanced > best_total:
                    best_total = result.total_enhanced
                    best_congregation = congregation
                    best_result = result
        
        if best_result is None:
            # Fallback to no congregation
            best_result = CongregationResult(
                original_scores=skill_scores,
                congregation_type=None,
                multiplier=1.0,
                delta_used=self.delta,
                rho_used=1.0,
                enhanced_scores=skill_scores.copy(),
                total_original=sum(skill_scores.values()),
                total_enhanced=sum(skill_scores.values()),
                boost_percentage=0.0,
                skills_involved=set(),
            )
        
        return best_congregation, best_result
    
    def compute_congregation_matrix(
        self,
        capacity_scores: Dict[CapacityType, CapacityScore],
    ) -> Dict[PolicyLevel, CongregationResult]:
        """
        Compute congregation results for each level.
        
        Args:
            capacity_scores: All capacity scores
            
        Returns:
            Dictionary mapping each level to its congregation result
        """
        results = {}
        
        for level in PolicyLevel.all_levels():
            # Extract skill scores for this level
            level_scores = {}
            for ct in CapacityType.by_level(level):
                if ct in capacity_scores:
                    level_scores[ct.skill] = capacity_scores[ct].raw_score
            
            # Apply congregation
            results[level] = self.apply_congregation(level_scores)
        
        return results
    
    def get_congregation_summary(
        self,
        capacity_scores: Dict[CapacityType, CapacityScore],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive congregation summary.
        
        Args:
            capacity_scores: All capacity scores
            
        Returns:
            Dictionary with congregation analysis
        """
        congregation_by_level = self.compute_congregation_matrix(capacity_scores)
        
        # Overall skill scores
        overall_skills = {skill: 0.0 for skill in PolicySkill.all_skills()}
        for ct, score in capacity_scores.items():
            overall_skills[ct.skill] += score.raw_score
        
        # Get optimal overall congregation
        optimal_congregation, optimal_result = self.get_optimal_congregation(overall_skills)
        
        return {
            "by_level": {
                level.value: result.to_dict()
                for level, result in congregation_by_level.items()
            },
            "overall_skill_scores": {s.value: v for s, v in overall_skills.items()},
            "optimal_congregation": optimal_congregation.name if optimal_congregation else None,
            "optimal_result": optimal_result.to_dict(),
            "congregation_rankings": [
                {
                    "name": c.name,
                    "skills": [s.value for s in c.skills],
                    "coefficient": c.coefficient,
                    "multiplier": self.calculator.calculate_multiplier_for_congregation(c),
                }
                for c, _ in self.calculator.rank_congregations_by_multiplier()
            ],
        }


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "EquipmentCongregationEngine",
    "SynergyCalculator",
    "SynergyCoefficients",
    "CongregationResult",
]
