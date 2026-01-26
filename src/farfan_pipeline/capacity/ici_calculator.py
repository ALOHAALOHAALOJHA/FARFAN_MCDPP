"""
Integrated Capacity Index (ICI) Calculator
==========================================

This module implements the Integrated Capacity Index calculation for the
Wu, Ramesh & Howlett (2015) Policy Capacity Framework.

Mathematical Model - Formula 5: Integrated Capacity Index
---------------------------------------------------------
ICI = Σ[w_skill × Σ(w_level × C(skill, level))] / 9

Where:
- w_skill = skill weight (CA=0.4, CO=0.35, CP=0.25)
- w_level = level weight (Individual=0.25, Org=0.35, Systemic=0.40)
- C(skill, level) = capacity score for specific skill×level combination
- Division by 9 normalizes to the number of capacity types

The ICI provides a single holistic metric of overall policy capacity,
ranging from 0 (no capacity) to theoretically unbounded (but typically
normalized to approximately 0-1 range).

Diagnostic Features:
-------------------
1. Gap Analysis: Identify underperforming capacity types
2. Balance Assessment: Check distribution across skills and levels
3. Benchmark Comparison: Compare against target thresholds
4. Trend Analysis: Track capacity evolution over time (when historical data available)

Author: F.A.R.F.A.N. Core Team
Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import (
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    Any,
    Callable,
)

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    EquipmentCongregation,
    CapacityScore,
    MethodCapacityMapping,
    AggregatedCapacity,
    CapacityGap,
    CapacityProfile,
)
from farfan_pipeline.capacity.base_score import (
    BaseCapacityScorer,
    CapacityScoringConfig,
)
from farfan_pipeline.capacity.aggregation import (
    CapacityAggregator,
    AggregationConfig,
)
from farfan_pipeline.capacity.equipment import (
    EquipmentCongregationEngine,
    CongregationResult,
)


# ============================================================================
# ICI CONFIGURATION
# ============================================================================

@dataclass
class ICIConfig:
    """
    Configuration for ICI calculation.
    
    This encapsulates all parameters for the Integrated Capacity Index
    calculation, including weights, thresholds, and diagnostic settings.
    """
    
    # Formula weights (must sum to 1.0 within each category)
    skill_weights: Dict[PolicySkill, float] = field(default_factory=lambda: {
        PolicySkill.ANALYTICAL: 0.40,
        PolicySkill.OPERATIONAL: 0.35,
        PolicySkill.POLITICAL: 0.25,
    })
    
    level_weights: Dict[PolicyLevel, float] = field(default_factory=lambda: {
        PolicyLevel.INDIVIDUAL: 0.25,
        PolicyLevel.ORGANIZATIONAL: 0.35,
        PolicyLevel.SYSTEMIC: 0.40,
    })
    
    # Normalization settings
    normalization_divisor: int = 9  # Number of capacity types
    apply_sigmoid_normalization: bool = False
    sigmoid_center: float = 1.0
    sigmoid_scale: float = 2.0
    
    # Gap analysis thresholds
    critical_gap_threshold: float = 0.3   # Below this = critical
    major_gap_threshold: float = 0.5      # Below this = major
    minor_gap_threshold: float = 0.7      # Below this = minor
    
    # Target scores (for gap analysis)
    target_ici: float = 0.85
    target_coverage_percentage: float = 10.0  # Min % methods per capacity type
    
    # Balance thresholds
    max_skill_ratio: float = 2.0   # Max ratio between strongest/weakest skill
    max_level_ratio: float = 2.0   # Max ratio between strongest/weakest level
    
    def __post_init__(self):
        # Validate skill weights
        skill_sum = sum(self.skill_weights.values())
        if not math.isclose(skill_sum, 1.0, rel_tol=1e-9):
            raise ValueError(f"Skill weights must sum to 1.0, got {skill_sum}")
        
        # Validate level weights
        level_sum = sum(self.level_weights.values())
        if not math.isclose(level_sum, 1.0, rel_tol=1e-9):
            raise ValueError(f"Level weights must sum to 1.0, got {level_sum}")
    
    @classmethod
    def default(cls) -> "ICIConfig":
        """Create default configuration."""
        return cls()
    
    @classmethod
    def strict(cls) -> "ICIConfig":
        """Strict configuration with higher thresholds."""
        return cls(
            critical_gap_threshold=0.4,
            major_gap_threshold=0.6,
            minor_gap_threshold=0.8,
            target_ici=0.90,
        )
    
    @classmethod
    def lenient(cls) -> "ICIConfig":
        """Lenient configuration with lower thresholds."""
        return cls(
            critical_gap_threshold=0.2,
            major_gap_threshold=0.4,
            minor_gap_threshold=0.6,
            target_ici=0.75,
        )


# ============================================================================
# ICI RESULT
# ============================================================================

@dataclass
class ICIResult:
    """
    Result of ICI calculation.
    """
    
    # Core metric
    ici_value: float
    ici_normalized: float  # Normalized to [0, 1] if sigmoid applied
    
    # Component breakdown
    skill_contributions: Dict[PolicySkill, float]
    level_contributions: Dict[PolicyLevel, float]
    capacity_type_scores: Dict[CapacityType, float]
    
    # Weights used
    skill_weights: Dict[PolicySkill, float]
    level_weights: Dict[PolicyLevel, float]
    
    # Method coverage
    total_methods: int
    coverage_by_type: Dict[CapacityType, int]
    
    # Equipment congregation effects
    congregation_multipliers: Dict[EquipmentCongregation, float]
    congregation_adjusted_ici: Optional[float]
    
    # Computation metadata
    computation_timestamp: str
    formula_applied: str
    
    @property
    def is_above_target(self) -> bool:
        """Check if ICI meets default target (0.85)."""
        return self.ici_value >= 0.85
    
    @property
    def dominant_skill(self) -> PolicySkill:
        """Get the skill with highest contribution."""
        return max(self.skill_contributions.items(), key=lambda x: x[1])[0]
    
    @property
    def dominant_level(self) -> PolicyLevel:
        """Get the level with highest contribution."""
        return max(self.level_contributions.items(), key=lambda x: x[1])[0]
    
    @property
    def weakest_skill(self) -> PolicySkill:
        """Get the skill with lowest contribution."""
        return min(self.skill_contributions.items(), key=lambda x: x[1])[0]
    
    @property
    def weakest_level(self) -> PolicyLevel:
        """Get the level with lowest contribution."""
        return min(self.level_contributions.items(), key=lambda x: x[1])[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ici_value": round(self.ici_value, 4),
            "ici_normalized": round(self.ici_normalized, 4),
            "skill_contributions": {
                s.value: round(v, 4) for s, v in self.skill_contributions.items()
            },
            "level_contributions": {
                l.value: round(v, 4) for l, v in self.level_contributions.items()
            },
            "capacity_type_scores": {
                ct.code: round(v, 4) for ct, v in self.capacity_type_scores.items()
            },
            "skill_weights": {s.value: v for s, v in self.skill_weights.items()},
            "level_weights": {l.value: v for l, v in self.level_weights.items()},
            "total_methods": self.total_methods,
            "coverage_by_type": {ct.code: v for ct, v in self.coverage_by_type.items()},
            "congregation_multipliers": {
                c.name: round(v, 4) for c, v in self.congregation_multipliers.items()
            },
            "congregation_adjusted_ici": (
                round(self.congregation_adjusted_ici, 4) 
                if self.congregation_adjusted_ici else None
            ),
            "computation_timestamp": self.computation_timestamp,
            "formula_applied": self.formula_applied,
        }


# ============================================================================
# GAP ANALYSIS RESULT
# ============================================================================

@dataclass
class GapAnalysisResult:
    """
    Result of capacity gap analysis.
    """
    
    # Identified gaps
    gaps: List[CapacityGap]
    
    # Summary statistics
    total_gaps: int
    critical_gaps: int
    major_gaps: int
    minor_gaps: int
    
    # Overall assessment
    overall_gap_score: float  # 0 = no gaps, 1 = all critical
    is_balanced: bool
    
    # Recommendations
    priority_improvements: List[str]
    
    @property
    def has_critical_gaps(self) -> bool:
        """Check if any critical gaps exist."""
        return self.critical_gaps > 0
    
    @property
    def gap_density(self) -> float:
        """Calculate gap density (gaps / total capacity types)."""
        return self.total_gaps / 9
    
    def get_gaps_by_severity(self, severity: str) -> List[CapacityGap]:
        """Filter gaps by severity level."""
        return [g for g in self.gaps if g.severity == severity]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "gaps": [
                {
                    "capacity_type": g.capacity_type.code,
                    "current_score": round(g.current_score, 4),
                    "target_score": round(g.target_score, 4),
                    "gap_magnitude": round(g.gap_magnitude, 4),
                    "severity": g.severity,
                    "recommendations": g.recommendations,
                }
                for g in self.gaps
            ],
            "total_gaps": self.total_gaps,
            "critical_gaps": self.critical_gaps,
            "major_gaps": self.major_gaps,
            "minor_gaps": self.minor_gaps,
            "overall_gap_score": round(self.overall_gap_score, 4),
            "is_balanced": self.is_balanced,
            "priority_improvements": self.priority_improvements,
        }


# ============================================================================
# CAPACITY DIAGNOSTICS
# ============================================================================

@dataclass
class CapacityDiagnostics:
    """
    Comprehensive diagnostics for capacity assessment.
    """
    
    # ICI result
    ici_result: ICIResult
    
    # Gap analysis
    gap_analysis: GapAnalysisResult
    
    # Balance metrics
    skill_balance_ratio: float  # max/min skill score ratio
    level_balance_ratio: float  # max/min level score ratio
    overall_balance_score: float  # 0-1, 1 = perfectly balanced
    
    # Coverage metrics
    coverage_completeness: float  # Percentage of types with methods
    coverage_uniformity: float  # How evenly distributed (0-1)
    
    # Congregation analysis
    active_congregations: List[EquipmentCongregation]
    congregation_boost_potential: float  # Unrealized synergy potential
    
    # Historical comparison (if available)
    ici_trend: Optional[str]  # "improving", "stable", "declining"
    trend_delta: Optional[float]  # Change from previous
    
    @property
    def health_status(self) -> str:
        """Get overall health status."""
        if self.ici_result.ici_value >= 0.85 and not self.gap_analysis.has_critical_gaps:
            return "excellent"
        if self.ici_result.ici_value >= 0.70 and self.gap_analysis.critical_gaps <= 1:
            return "good"
        if self.ici_result.ici_value >= 0.50:
            return "moderate"
        return "needs_improvement"
    
    @property
    def priority_action(self) -> str:
        """Get highest priority action."""
        if self.gap_analysis.has_critical_gaps:
            critical = self.gap_analysis.get_gaps_by_severity("critical")[0]
            return f"Address critical gap in {critical.capacity_type.code}"
        if self.skill_balance_ratio > 2.0:
            return f"Improve balance in {self.ici_result.weakest_skill.value} skill"
        if self.coverage_completeness < 1.0:
            return "Improve coverage across all capacity types"
        return "Maintain current capacity levels"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ici_result": self.ici_result.to_dict(),
            "gap_analysis": self.gap_analysis.to_dict(),
            "skill_balance_ratio": round(self.skill_balance_ratio, 4),
            "level_balance_ratio": round(self.level_balance_ratio, 4),
            "overall_balance_score": round(self.overall_balance_score, 4),
            "coverage_completeness": round(self.coverage_completeness, 4),
            "coverage_uniformity": round(self.coverage_uniformity, 4),
            "active_congregations": [c.name for c in self.active_congregations],
            "congregation_boost_potential": round(self.congregation_boost_potential, 4),
            "ici_trend": self.ici_trend,
            "trend_delta": round(self.trend_delta, 4) if self.trend_delta else None,
            "health_status": self.health_status,
            "priority_action": self.priority_action,
        }


# ============================================================================
# ICI CALCULATOR
# ============================================================================

class ICICalculator:
    """
    Calculator for the Integrated Capacity Index.
    
    Implements Formula 5: ICI = Σ[w_skill × Σ(w_level × C(skill, level))] / 9
    
    This class provides comprehensive capacity assessment including:
    - ICI calculation with configurable weights
    - Gap analysis and identification
    - Balance assessment
    - Equipment congregation effects
    - Full diagnostic reporting
    
    Usage:
        calculator = ICICalculator()
        
        # Calculate ICI from capacity scores
        result = calculator.calculate_ici(capacity_scores)
        
        # Full diagnostic analysis
        diagnostics = calculator.analyze(method_mappings)
        
        # Generate capacity profile
        profile = calculator.generate_profile(method_mappings)
    """
    
    def __init__(
        self,
        config: Optional[ICIConfig] = None,
        scorer: Optional[BaseCapacityScorer] = None,
        aggregator: Optional[CapacityAggregator] = None,
        congregation_engine: Optional[EquipmentCongregationEngine] = None,
    ):
        """
        Initialize ICI calculator.
        
        Args:
            config: ICI configuration
            scorer: Base capacity scorer
            aggregator: Capacity aggregator
            congregation_engine: Equipment congregation engine
        """
        self.config = config or ICIConfig.default()
        self.scorer = scorer or BaseCapacityScorer()
        self.aggregator = aggregator or CapacityAggregator()
        self.congregation_engine = congregation_engine or EquipmentCongregationEngine()
    
    # -------------------------------------------------------------------------
    # Core ICI Calculation
    # -------------------------------------------------------------------------
    
    def calculate_ici(
        self,
        capacity_scores: Dict[CapacityType, CapacityScore],
        apply_congregation: bool = True,
    ) -> ICIResult:
        """
        Calculate Integrated Capacity Index.
        
        Formula: ICI = Σ[w_skill × Σ(w_level × C(skill, level))] / 9
        
        Args:
            capacity_scores: Scores for all capacity types
            apply_congregation: Whether to apply congregation multipliers
            
        Returns:
            Complete ICIResult with all metrics
        """
        # Extract raw scores
        capacity_type_scores = {
            ct: score.raw_score for ct, score in capacity_scores.items()
        }
        
        # Calculate skill contributions
        skill_contributions = {}
        for skill in PolicySkill.all_skills():
            skill_sum = 0.0
            for level in PolicyLevel.all_levels():
                ct = CapacityType.from_skill_level(skill, level)
                score = capacity_type_scores.get(ct, 0.0)
                level_weight = self.config.level_weights[level]
                skill_sum += level_weight * score
            skill_contributions[skill] = skill_sum
        
        # Calculate level contributions
        level_contributions = {}
        for level in PolicyLevel.all_levels():
            level_sum = 0.0
            for skill in PolicySkill.all_skills():
                ct = CapacityType.from_skill_level(skill, level)
                score = capacity_type_scores.get(ct, 0.0)
                skill_weight = self.config.skill_weights[skill]
                level_sum += skill_weight * score
            level_contributions[level] = level_sum
        
        # Calculate ICI using skill-first aggregation
        ici_value = 0.0
        for skill, skill_contribution in skill_contributions.items():
            skill_weight = self.config.skill_weights[skill]
            ici_value += skill_weight * skill_contribution
        
        # Normalize by number of capacity types
        ici_value = ici_value / self.config.normalization_divisor
        
        # Apply sigmoid normalization if configured
        if self.config.apply_sigmoid_normalization:
            ici_normalized = 1.0 / (1.0 + math.exp(
                -self.config.sigmoid_scale * (ici_value - self.config.sigmoid_center)
            ))
        else:
            ici_normalized = ici_value
        
        # Calculate congregation effects
        congregation_multipliers = {
            congregation: self.congregation_engine.calculator.calculate_multiplier_for_congregation(congregation)
            for congregation in EquipmentCongregation.all_congregations()
        }
        
        # Calculate congregation-adjusted ICI if requested
        congregation_adjusted_ici = None
        if apply_congregation:
            # Get skill scores and apply congregation
            skill_scores = {skill: skill_contributions[skill] for skill in PolicySkill.all_skills()}
            optimal_congregation, optimal_result = self.congregation_engine.get_optimal_congregation(skill_scores)
            
            if optimal_congregation:
                # Apply multiplier to ICI
                congregation_adjusted_ici = ici_value * optimal_result.multiplier
        
        # Calculate method counts
        total_methods = sum(score.method_count for score in capacity_scores.values())
        coverage_by_type = {ct: score.method_count for ct, score in capacity_scores.items()}
        
        return ICIResult(
            ici_value=round(ici_value, 4),
            ici_normalized=round(ici_normalized, 4),
            skill_contributions=skill_contributions,
            level_contributions=level_contributions,
            capacity_type_scores=capacity_type_scores,
            skill_weights=dict(self.config.skill_weights),
            level_weights=dict(self.config.level_weights),
            total_methods=total_methods,
            coverage_by_type=coverage_by_type,
            congregation_multipliers=congregation_multipliers,
            congregation_adjusted_ici=congregation_adjusted_ici,
            computation_timestamp=datetime.now().isoformat(),
            formula_applied="ICI = Σ[w_skill × Σ(w_level × C(skill, level))] / 9",
        )
    
    # -------------------------------------------------------------------------
    # Gap Analysis
    # -------------------------------------------------------------------------
    
    def analyze_gaps(
        self,
        capacity_scores: Dict[CapacityType, CapacityScore],
        target_scores: Optional[Dict[CapacityType, float]] = None,
    ) -> GapAnalysisResult:
        """
        Perform gap analysis on capacity scores.
        
        Args:
            capacity_scores: Current capacity scores
            target_scores: Optional target scores (uses defaults if not provided)
            
        Returns:
            Complete gap analysis result
        """
        gaps = []
        
        # Calculate default target if not provided
        if target_scores is None:
            # Use average score as target for balance
            all_scores = [s.raw_score for s in capacity_scores.values() if s.method_count > 0]
            avg_score = sum(all_scores) / len(all_scores) if all_scores else 1.0
            target_scores = {ct: avg_score for ct in CapacityType.all_types()}
        
        # Analyze each capacity type
        for ct in CapacityType.all_types():
            score = capacity_scores.get(ct)
            current = score.raw_score if score else 0.0
            target = target_scores.get(ct, 1.0)
            
            # Calculate gap magnitude
            gap_magnitude = target - current
            
            # Only consider significant gaps
            if gap_magnitude <= 0:
                continue
            
            # Determine severity
            ratio = current / target if target > 0 else 0.0
            if ratio < self.config.critical_gap_threshold:
                severity = "critical"
            elif ratio < self.config.major_gap_threshold:
                severity = "major"
            elif ratio < self.config.minor_gap_threshold:
                severity = "minor"
            else:
                severity = "acceptable"
            
            # Generate recommendations
            recommendations = self._generate_gap_recommendations(ct, severity)
            
            gaps.append(CapacityGap(
                capacity_type=ct,
                current_score=current,
                target_score=target,
                gap_magnitude=gap_magnitude,
                severity=severity,
                recommendations=recommendations,
            ))
        
        # Calculate summary statistics
        critical_count = sum(1 for g in gaps if g.severity == "critical")
        major_count = sum(1 for g in gaps if g.severity == "major")
        minor_count = sum(1 for g in gaps if g.severity == "minor")
        
        # Calculate overall gap score (0 = no gaps, 1 = all critical)
        severity_weights = {"critical": 1.0, "major": 0.6, "minor": 0.3, "acceptable": 0.0}
        total_severity = sum(severity_weights[g.severity] for g in gaps)
        overall_gap_score = total_severity / 9 if gaps else 0.0
        
        # Assess balance
        is_balanced = self._assess_balance(capacity_scores)
        
        # Generate priority improvements
        priority_improvements = self._generate_priority_improvements(gaps)
        
        return GapAnalysisResult(
            gaps=gaps,
            total_gaps=len(gaps),
            critical_gaps=critical_count,
            major_gaps=major_count,
            minor_gaps=minor_count,
            overall_gap_score=round(overall_gap_score, 4),
            is_balanced=is_balanced,
            priority_improvements=priority_improvements,
        )
    
    def _generate_gap_recommendations(
        self,
        capacity_type: CapacityType,
        severity: str,
    ) -> List[str]:
        """Generate recommendations for addressing a capacity gap."""
        recommendations = []
        skill = capacity_type.skill
        level = capacity_type.level
        
        # Base recommendation on severity
        if severity == "critical":
            recommendations.append(
                f"URGENT: Immediate intervention required for {capacity_type.code}"
            )
        
        # Skill-specific recommendations
        if skill == PolicySkill.ANALYTICAL:
            recommendations.append(
                f"Add analytical methods at {level.value.lower()} level: "
                f"research, data analysis, evidence synthesis"
            )
        elif skill == PolicySkill.OPERATIONAL:
            recommendations.append(
                f"Add operational methods at {level.value.lower()} level: "
                f"implementation tracking, resource management, coordination"
            )
        else:  # Political
            recommendations.append(
                f"Add political methods at {level.value.lower()} level: "
                f"stakeholder engagement, legitimacy assessment, coalition building"
            )
        
        # Level-specific recommendations
        if level == PolicyLevel.INDIVIDUAL:
            recommendations.append(
                "Focus on personal skill development and training programs"
            )
        elif level == PolicyLevel.ORGANIZATIONAL:
            recommendations.append(
                "Strengthen institutional structures and processes"
            )
        else:  # Systemic
            recommendations.append(
                "Build cross-organizational networks and systemic arrangements"
            )
        
        return recommendations
    
    def _assess_balance(
        self,
        capacity_scores: Dict[CapacityType, CapacityScore],
    ) -> bool:
        """Assess if capacity scores are balanced."""
        # Check skill balance
        skill_scores = {}
        for skill in PolicySkill.all_skills():
            skill_types = CapacityType.by_skill(skill)
            scores = [capacity_scores[ct].raw_score for ct in skill_types if ct in capacity_scores]
            skill_scores[skill] = sum(scores) / len(scores) if scores else 0.0
        
        skill_values = [v for v in skill_scores.values() if v > 0]
        if skill_values:
            skill_ratio = max(skill_values) / min(skill_values) if min(skill_values) > 0 else float('inf')
            if skill_ratio > self.config.max_skill_ratio:
                return False
        
        # Check level balance
        level_scores = {}
        for level in PolicyLevel.all_levels():
            level_types = CapacityType.by_level(level)
            scores = [capacity_scores[ct].raw_score for ct in level_types if ct in capacity_scores]
            level_scores[level] = sum(scores) / len(scores) if scores else 0.0
        
        level_values = [v for v in level_scores.values() if v > 0]
        if level_values:
            level_ratio = max(level_values) / min(level_values) if min(level_values) > 0 else float('inf')
            if level_ratio > self.config.max_level_ratio:
                return False
        
        return True
    
    def _generate_priority_improvements(
        self,
        gaps: List[CapacityGap],
    ) -> List[str]:
        """Generate prioritized improvement recommendations."""
        improvements = []
        
        # Sort gaps by severity (critical first)
        severity_order = {"critical": 0, "major": 1, "minor": 2, "acceptable": 3}
        sorted_gaps = sorted(gaps, key=lambda g: severity_order[g.severity])
        
        # Take top 3 gaps
        for gap in sorted_gaps[:3]:
            improvements.append(
                f"[{gap.severity.upper()}] Improve {gap.capacity_type.code}: "
                f"current={gap.current_score:.2f}, target={gap.target_score:.2f}"
            )
        
        return improvements
    
    # -------------------------------------------------------------------------
    # Full Diagnostic Analysis
    # -------------------------------------------------------------------------
    
    def analyze(
        self,
        method_mappings: List[MethodCapacityMapping],
        previous_ici: Optional[float] = None,
    ) -> CapacityDiagnostics:
        """
        Perform comprehensive diagnostic analysis.
        
        Args:
            method_mappings: All method capacity mappings
            previous_ici: Optional previous ICI for trend analysis
            
        Returns:
            Complete diagnostic results
        """
        # Calculate capacity scores
        capacity_scores = self.scorer.calculate_all_capacity_scores(method_mappings)
        
        # Calculate ICI
        ici_result = self.calculate_ici(capacity_scores)
        
        # Perform gap analysis
        gap_analysis = self.analyze_gaps(capacity_scores)
        
        # Calculate balance ratios
        skill_values = list(ici_result.skill_contributions.values())
        skill_balance_ratio = (
            max(skill_values) / min(skill_values)
            if min(skill_values) > 0 else float('inf')
        )
        
        level_values = list(ici_result.level_contributions.values())
        level_balance_ratio = (
            max(level_values) / min(level_values)
            if min(level_values) > 0 else float('inf')
        )
        
        # Calculate overall balance score (1 = perfect balance)
        overall_balance = 1.0 / (1.0 + abs(skill_balance_ratio - 1.0) + abs(level_balance_ratio - 1.0))
        
        # Calculate coverage metrics
        types_with_methods = sum(1 for ct, count in ici_result.coverage_by_type.items() if count > 0)
        coverage_completeness = types_with_methods / 9
        
        # Coverage uniformity (coefficient of variation inverted)
        coverage_values = list(ici_result.coverage_by_type.values())
        if coverage_values and sum(coverage_values) > 0:
            mean_coverage = sum(coverage_values) / len(coverage_values)
            variance = sum((v - mean_coverage) ** 2 for v in coverage_values) / len(coverage_values)
            std_coverage = math.sqrt(variance)
            cv = std_coverage / mean_coverage if mean_coverage > 0 else 0
            coverage_uniformity = 1.0 / (1.0 + cv)
        else:
            coverage_uniformity = 0.0
        
        # Identify active congregations
        active_congregations = []
        skill_present = {
            skill for skill, contrib in ici_result.skill_contributions.items()
            if contrib > 0
        }
        for congregation in EquipmentCongregation.all_congregations():
            if congregation.skills.issubset(skill_present):
                active_congregations.append(congregation)
        
        # Calculate congregation boost potential
        if active_congregations:
            max_possible = EquipmentCongregation.INTEGRATED_CAPACITY.coefficient
            current_max = max(c.coefficient for c in active_congregations)
            congregation_boost_potential = max_possible - current_max
        else:
            congregation_boost_potential = 0.75  # Maximum potential boost
        
        # Trend analysis
        ici_trend = None
        trend_delta = None
        if previous_ici is not None:
            trend_delta = ici_result.ici_value - previous_ici
            if trend_delta > 0.05:
                ici_trend = "improving"
            elif trend_delta < -0.05:
                ici_trend = "declining"
            else:
                ici_trend = "stable"
        
        return CapacityDiagnostics(
            ici_result=ici_result,
            gap_analysis=gap_analysis,
            skill_balance_ratio=round(skill_balance_ratio, 4),
            level_balance_ratio=round(level_balance_ratio, 4),
            overall_balance_score=round(overall_balance, 4),
            coverage_completeness=round(coverage_completeness, 4),
            coverage_uniformity=round(coverage_uniformity, 4),
            active_congregations=active_congregations,
            congregation_boost_potential=round(congregation_boost_potential, 4),
            ici_trend=ici_trend,
            trend_delta=trend_delta,
        )
    
    # -------------------------------------------------------------------------
    # Capacity Profile Generation
    # -------------------------------------------------------------------------
    
    def generate_profile(
        self,
        method_mappings: List[MethodCapacityMapping],
    ) -> CapacityProfile:
        """
        Generate complete capacity profile.
        
        Args:
            method_mappings: All method capacity mappings
            
        Returns:
            Complete CapacityProfile
        """
        # Calculate all capacity scores
        capacity_scores = self.scorer.calculate_all_capacity_scores(method_mappings)
        
        # Calculate ICI
        ici_result = self.calculate_ici(capacity_scores)
        
        # Aggregate by skill
        skill_aggregates = self.aggregator.aggregate_by_skill(capacity_scores)
        
        # Aggregate by level
        level_aggregates = self.aggregator.aggregate_by_level(capacity_scores)
        
        # Calculate congregation effects
        congregation_summary = self.congregation_engine.get_congregation_summary(capacity_scores)
        congregation_effects = {}
        for congregation in EquipmentCongregation.all_congregations():
            multiplier = self.congregation_engine.calculator.calculate_multiplier_for_congregation(congregation)
            congregation_effects[congregation] = multiplier
        
        # Gap analysis
        gap_analysis = self.analyze_gaps(capacity_scores)
        
        return CapacityProfile(
            capacity_scores=capacity_scores,
            skill_aggregates=skill_aggregates,
            level_aggregates=level_aggregates,
            integrated_capacity_index=ici_result.ici_value,
            congregation_effects=congregation_effects,
            identified_gaps=gap_analysis.gaps,
            total_methods=len(method_mappings),
            analysis_timestamp=datetime.now().isoformat(),
            version="1.0.0",
        )


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "ICICalculator",
    "ICIConfig",
    "ICIResult",
    "GapAnalysisResult",
    "CapacityDiagnostics",
]
