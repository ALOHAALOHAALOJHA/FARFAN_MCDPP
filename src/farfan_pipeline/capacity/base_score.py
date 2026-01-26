"""
Base Capacity Scoring Module
============================

This module implements the base capacity scoring function from the
Wu, Ramesh & Howlett (2015) Policy Capacity Framework.

Mathematical Model - Formula 1: Base Capacity Score
---------------------------------------------------
C_base(e, l, o) = α × E(e) + β × L(l) + γ × O(o)

Where:
- e = epistemology (Empirismo, Bayesianismo, Falsacionismo)
- l = level (N1-EMP, N2-INF, N3-AUD)  
- o = output type (FACT, PARAMETER, CONSTRAINT)
- E(e), L(l), O(o) = encoding functions mapping to weights
- α = 0.4 (epistemology weight - theoretical foundation importance)
- β = 0.35 (level weight - analytical sophistication importance)
- γ = 0.25 (output weight - deliverable nature importance)

The weights are derived from the theoretical framework where:
- Epistemology determines the NATURE of knowledge produced
- Level determines the SOPHISTICATION of analysis
- Output type determines the FORM of deliverable

Author: F.A.R.F.A.N. Core Team
Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    Union,
    Any,
    Callable,
)

from farfan_pipeline.capacity.types import (
    PolicySkill,
    PolicyLevel,
    CapacityType,
    EpistemologicalLevel,
    CapacityScore,
    MethodCapacityMapping,
)


# ============================================================================
# WEIGHT CONFIGURATIONS
# ============================================================================

@dataclass(frozen=True)
class EpistemologyWeights:
    """
    Weights for different epistemological foundations.
    
    These weights reflect the theoretical value of different epistemological
    approaches for policy capacity:
    
    - Empirismo positivista (0.85): Foundational facts, but limited interpretive depth
    - Bayesianismo subjetivista (1.00): Full probabilistic reasoning, highest analytical value
    - Falsacionismo popperiano (0.92): Critical testing, high validation value
    - Instrumentalismo (0.50): Infrastructure support, necessary but not analytical
    - Reflexividad crítica (0.80): Meta-analysis, important but derivative
    """
    
    empirismo_positivista: float = 0.85
    bayesianismo_subjetivista: float = 1.00
    falsacionismo_popperiano: float = 0.92
    instrumentalismo: float = 0.50
    reflexividad_critica: float = 0.80
    
    def get_weight(self, epistemology: str) -> float:
        """Get weight for an epistemology by name."""
        name_map = {
            "Empirismo positivista": self.empirismo_positivista,
            "Bayesianismo subjetivista": self.bayesianismo_subjetivista,
            "Falsacionismo popperiano": self.falsacionismo_popperiano,
            "Instrumentalismo": self.instrumentalismo,
            "Reflexividad crítica": self.reflexividad_critica,
        }
        return name_map.get(epistemology, 0.75)  # Default for unknown
    
    def get_weight_by_level(self, level: EpistemologicalLevel) -> float:
        """Get weight from EpistemologicalLevel enum."""
        return level.epistemology_weight


@dataclass(frozen=True)
class LevelWeights:
    """
    Weights for method levels (N0-INFRA through N4-META).
    
    These weights reflect the analytical sophistication of different levels:
    
    - N0-INFRA (0.5): Infrastructure support, minimal analytical content
    - N1-EMP (1.0): Empirical extraction, baseline analytical value
    - N2-INF (1.5): Inferential computation, significant analytical value
    - N3-AUD (2.0): Audit/validation, high analytical value (critical)
    - N4-META (2.5): Meta-analysis, highest analytical sophistication
    
    The progression reflects increasing analytical complexity and
    contribution to policy capacity.
    """
    
    n0_infra: float = 0.5
    n1_emp: float = 1.0
    n2_inf: float = 1.5
    n3_aud: float = 2.0
    n4_meta: float = 2.5
    
    def get_weight(self, level_code: str) -> float:
        """Get weight for a level by code."""
        code_map = {
            "N0-INFRA": self.n0_infra,
            "N1-EMP": self.n1_emp,
            "N2-INF": self.n2_inf,
            "N3-AUD": self.n3_aud,
            "N4-META": self.n4_meta,
        }
        return code_map.get(level_code, 1.0)  # Default for unknown
    
    def get_weight_by_level(self, level: EpistemologicalLevel) -> float:
        """Get weight from EpistemologicalLevel enum."""
        return level.level_weight


@dataclass(frozen=True)
class OutputTypeWeights:
    """
    Weights for output types (FACT, PARAMETER, CONSTRAINT, etc.).
    
    These weights reflect the policy utility of different output types:
    
    - FACT (0.8): Raw empirical content, foundational but requires interpretation
    - PARAMETER (1.0): Derived quantities, immediately actionable
    - CONSTRAINT (1.2): Validation results, critical for policy rigor
    - INFRASTRUCTURE (0.4): Support outputs, minimal direct policy value
    - META_ANALYSIS (1.1): Synthesis outputs, high integration value
    
    CONSTRAINT has highest weight because audit outputs serve as
    veto gates with asymmetric importance for policy validity.
    """
    
    fact: float = 0.8
    parameter: float = 1.0
    constraint: float = 1.2
    infrastructure: float = 0.4
    meta_analysis: float = 1.1
    narrative: float = 0.9
    
    def get_weight(self, output_type: str) -> float:
        """Get weight for an output type."""
        type_map = {
            "FACT": self.fact,
            "PARAMETER": self.parameter,
            "CONSTRAINT": self.constraint,
            "INFRASTRUCTURE": self.infrastructure,
            "META_ANALYSIS": self.meta_analysis,
            "NARRATIVE": self.narrative,
        }
        return type_map.get(output_type, 0.9)  # Default for unknown


@dataclass
class CapacityScoringConfig:
    """
    Configuration for capacity scoring calculations.
    
    This class encapsulates all configurable parameters for the
    base capacity scoring function, allowing customization while
    maintaining mathematical rigor.
    
    Default values are derived from theoretical framework analysis:
    - alpha (0.4): Epistemology carries highest weight as it determines
      the fundamental nature of knowledge produced
    - beta (0.35): Level is second most important as it determines
      analytical sophistication
    - gamma (0.25): Output type is least important as it only affects
      the form of the deliverable
    
    Invariant: alpha + beta + gamma = 1.0 (normalized weights)
    """
    
    # Formula weights
    alpha: float = 0.4   # Epistemology weight
    beta: float = 0.35   # Level weight
    gamma: float = 0.25  # Output type weight
    
    # Component weight structures
    epistemology_weights: EpistemologyWeights = field(default_factory=EpistemologyWeights)
    level_weights: LevelWeights = field(default_factory=LevelWeights)
    output_weights: OutputTypeWeights = field(default_factory=OutputTypeWeights)
    
    # Score normalization
    normalize_scores: bool = True
    normalization_factor: float = 1.2  # Scale factor for weighted scores
    
    # Confidence thresholds
    high_confidence_threshold: float = 0.8
    medium_confidence_threshold: float = 0.5
    low_confidence_threshold: float = 0.2
    
    def __post_init__(self):
        # Validate weight invariant
        total = self.alpha + self.beta + self.gamma
        if not math.isclose(total, 1.0, rel_tol=1e-9):
            raise ValueError(
                f"Formula weights must sum to 1.0: α={self.alpha}, β={self.beta}, γ={self.gamma} "
                f"sum to {total}"
            )
    
    @classmethod
    def default(cls) -> "CapacityScoringConfig":
        """Create default configuration."""
        return cls()
    
    @classmethod
    def high_analytical_emphasis(cls) -> "CapacityScoringConfig":
        """Configuration emphasizing analytical/epistemological aspects."""
        return cls(alpha=0.5, beta=0.3, gamma=0.2)
    
    @classmethod
    def balanced(cls) -> "CapacityScoringConfig":
        """Configuration with equal weights for all components."""
        return cls(alpha=0.33, beta=0.34, gamma=0.33)
    
    @classmethod
    def output_focused(cls) -> "CapacityScoringConfig":
        """Configuration emphasizing output type importance."""
        return cls(alpha=0.3, beta=0.3, gamma=0.4)


# ============================================================================
# CAPACITY MAPPING RULES
# ============================================================================

@dataclass
class CapacityMappingRule:
    """
    Rule for mapping epistemological classifications to capacity types.
    
    Each rule specifies:
    - Source epistemological level
    - Primary capacity type assignment
    - Optional secondary assignment for split classifications
    - Split criteria for determining primary vs secondary
    """
    
    epistemological_level: EpistemologicalLevel
    primary_capacity: CapacityType
    secondary_capacity: Optional[CapacityType] = None
    split_rule: Optional[str] = None  # "class_based", "name_based", or None
    primary_keywords: List[str] = field(default_factory=list)
    secondary_keywords: List[str] = field(default_factory=list)
    
    def apply(
        self,
        class_name: str,
        method_name: str,
    ) -> CapacityType:
        """
        Apply this rule to determine capacity type.
        
        Args:
            class_name: Name of the class containing the method
            method_name: Name of the method
            
        Returns:
            Assigned CapacityType
        """
        if self.split_rule is None or self.secondary_capacity is None:
            return self.primary_capacity
        
        if self.split_rule == "class_based":
            # Check if class name matches primary or secondary keywords
            class_lower = class_name.lower()
            for kw in self.secondary_keywords:
                if kw.lower() in class_lower:
                    return self.secondary_capacity
            return self.primary_capacity
        
        elif self.split_rule == "name_based":
            # Check method name for keywords
            method_lower = method_name.lower()
            for kw in self.secondary_keywords:
                if kw in method_lower:
                    return self.secondary_capacity
            return self.primary_capacity
        
        return self.primary_capacity


# Default mapping rules based on episteme_rules.md
DEFAULT_MAPPING_RULES: Dict[EpistemologicalLevel, CapacityMappingRule] = {
    EpistemologicalLevel.N1_EMP: CapacityMappingRule(
        epistemological_level=EpistemologicalLevel.N1_EMP,
        primary_capacity=CapacityType.CA_I,
        # N1-EMP maps directly to Individual Analytical (observable facts)
    ),
    EpistemologicalLevel.N2_INF: CapacityMappingRule(
        epistemological_level=EpistemologicalLevel.N2_INF,
        primary_capacity=CapacityType.CA_O,
        secondary_capacity=CapacityType.CO_O,
        split_rule="class_based",
        primary_keywords=["semantic", "bayesian", "numerical", "analyzer"],
        secondary_keywords=["mechanism", "teoria", "cambio", "evidence", "integrator", "dispersion"],
    ),
    EpistemologicalLevel.N3_AUD: CapacityMappingRule(
        epistemological_level=EpistemologicalLevel.N3_AUD,
        primary_capacity=CapacityType.CO_S,
        secondary_capacity=CapacityType.CP_O,
        split_rule="name_based",
        primary_keywords=["validate", "audit", "check", "verify", "test"],
        secondary_keywords=["detect", "contradict", "consistency", "coherence"],
    ),
}


# ============================================================================
# BASE CAPACITY SCORER
# ============================================================================

class BaseCapacityScorer:
    """
    Calculator for base capacity scores following Wu Framework.
    
    Implements Formula 1: C_base(e, l, o) = α × E(e) + β × L(l) + γ × O(o)
    
    This class is responsible for:
    1. Computing base capacity scores for individual methods
    2. Mapping methods to capacity types based on epistemological classification
    3. Calculating confidence scores for classifications
    
    Usage:
        scorer = BaseCapacityScorer()
        score = scorer.calculate_base_score(
            epistemology="Empirismo positivista",
            method_level="N1-EMP",
            output_type="FACT"
        )
    """
    
    def __init__(self, config: Optional[CapacityScoringConfig] = None):
        """
        Initialize scorer with configuration.
        
        Args:
            config: Scoring configuration. Uses default if not provided.
        """
        self.config = config or CapacityScoringConfig.default()
        self._mapping_rules = dict(DEFAULT_MAPPING_RULES)
    
    def calculate_base_score(
        self,
        epistemology: str,
        method_level: str,
        output_type: str,
    ) -> float:
        """
        Calculate base capacity score for a method.
        
        Formula: C_base = α × E_weight + β × L_weight + γ × O_weight
        
        Args:
            epistemology: Epistemological foundation name
            method_level: Method level code (e.g., "N1-EMP")
            output_type: Output type (e.g., "FACT")
            
        Returns:
            Base capacity score (unweighted)
        """
        # Get component weights
        e_weight = self.config.epistemology_weights.get_weight(epistemology)
        l_weight = self.config.level_weights.get_weight(method_level)
        o_weight = self.config.output_weights.get_weight(output_type)
        
        # Apply formula
        score = (
            self.config.alpha * e_weight +
            self.config.beta * l_weight +
            self.config.gamma * o_weight
        )
        
        # Apply normalization if configured
        if self.config.normalize_scores:
            score *= self.config.normalization_factor
        
        return round(score, 4)
    
    def calculate_base_score_from_level(
        self,
        level: EpistemologicalLevel,
    ) -> float:
        """
        Calculate base capacity score from EpistemologicalLevel enum.
        
        Args:
            level: The epistemological level enum
            
        Returns:
            Base capacity score
        """
        return self.calculate_base_score(
            epistemology=level.epistemology,
            method_level=level.code,
            output_type=level.output_type,
        )
    
    def map_to_capacity_type(
        self,
        epistemological_level: str,
        class_name: str = "",
        method_name: str = "",
    ) -> CapacityType:
        """
        Map a method to its capacity type based on classification.
        
        Args:
            epistemological_level: Level code (e.g., "N1-EMP")
            class_name: Name of containing class (for split rules)
            method_name: Name of method (for split rules)
            
        Returns:
            Assigned CapacityType
        """
        # Parse level
        try:
            level = EpistemologicalLevel.from_code(epistemological_level)
        except ValueError:
            # Default to N2-INF for unknown levels
            level = EpistemologicalLevel.N2_INF
        
        # Get mapping rule
        rule = self._mapping_rules.get(level)
        if rule is None:
            # Default mapping
            return level.primary_capacity_type or CapacityType.CA_O
        
        # Apply rule
        return rule.apply(class_name, method_name)
    
    def score_method(
        self,
        method_id: str,
        class_name: str,
        method_name: str,
        file_path: str,
        epistemological_level: str,
        output_type: str,
        classification_confidence: float = 0.5,
        classification_evidence: Optional[List[str]] = None,
    ) -> MethodCapacityMapping:
        """
        Score a method and create its capacity mapping.
        
        This is the primary interface for scoring individual methods.
        
        Args:
            method_id: Unique method identifier
            class_name: Class containing the method
            method_name: Method name
            file_path: Source file path
            epistemological_level: Classified level code
            output_type: Output type
            classification_confidence: Confidence in classification [0, 1]
            classification_evidence: Evidence supporting classification
            
        Returns:
            Complete MethodCapacityMapping with scores
        """
        # Get epistemology from level
        try:
            level = EpistemologicalLevel.from_code(epistemological_level)
            epistemology = level.epistemology
        except ValueError:
            epistemology = "Bayesianismo subjetivista"  # Default
        
        # Calculate base score
        base_score = self.calculate_base_score(
            epistemology=epistemology,
            method_level=epistemological_level,
            output_type=output_type,
        )
        
        # Map to capacity type
        capacity_type = self.map_to_capacity_type(
            epistemological_level=epistemological_level,
            class_name=class_name,
            method_name=method_name,
        )
        
        return MethodCapacityMapping(
            method_id=method_id,
            class_name=class_name,
            method_name=method_name,
            file_path=file_path,
            epistemological_level=epistemological_level,
            output_type=output_type,
            capacity_type=capacity_type.code,
            base_score=base_score,
            classification_confidence=classification_confidence,
            classification_evidence=classification_evidence or [],
        )
    
    def score_methods_batch(
        self,
        methods: List[Dict[str, Any]],
    ) -> List[MethodCapacityMapping]:
        """
        Score a batch of methods.
        
        Args:
            methods: List of method dictionaries with required fields:
                - method_id or (class_name + method_name)
                - class_name
                - method_name
                - file_path
                - epistemological_level
                - output_type
                - classification_confidence (optional)
                - classification_evidence (optional)
                
        Returns:
            List of MethodCapacityMapping objects
        """
        results = []
        
        for method in methods:
            # Generate method_id if not provided
            method_id = method.get("method_id")
            if not method_id:
                method_id = f"{method['class_name']}.{method['method_name']}"
            
            mapping = self.score_method(
                method_id=method_id,
                class_name=method["class_name"],
                method_name=method["method_name"],
                file_path=method["file_path"],
                epistemological_level=method["epistemological_level"],
                output_type=method["output_type"],
                classification_confidence=method.get("classification_confidence", 0.5),
                classification_evidence=method.get("classification_evidence", []),
            )
            results.append(mapping)
        
        return results
    
    def calculate_capacity_score(
        self,
        capacity_type: CapacityType,
        method_mappings: List[MethodCapacityMapping],
    ) -> CapacityScore:
        """
        Calculate aggregate capacity score for a capacity type.
        
        Args:
            capacity_type: The capacity type to score
            method_mappings: All method mappings
            
        Returns:
            Aggregated CapacityScore for the capacity type
        """
        # Filter methods for this capacity type
        relevant_methods = [
            m for m in method_mappings
            if m.capacity_type == capacity_type.code
        ]
        
        if not relevant_methods:
            return CapacityScore(
                capacity_type=capacity_type,
                raw_score=0.0,
                weighted_score=0.0,
                confidence=0.0,
                method_count=0,
            )
        
        # Calculate raw score (mean of base scores)
        raw_scores = [m.base_score for m in relevant_methods]
        raw_score = sum(raw_scores) / len(raw_scores)
        
        # Apply skill and level weights for weighted score
        skill_weight = capacity_type.skill.weight
        level_weight = capacity_type.level.weight
        weighted_score = raw_score * skill_weight * level_weight * len(relevant_methods)
        
        # Calculate confidence (weighted average by individual confidence)
        confidences = [m.classification_confidence for m in relevant_methods]
        confidence = sum(confidences) / len(confidences)
        
        return CapacityScore(
            capacity_type=capacity_type,
            raw_score=round(raw_score, 4),
            weighted_score=round(weighted_score, 4),
            confidence=round(confidence, 4),
            method_count=len(relevant_methods),
        )
    
    def calculate_all_capacity_scores(
        self,
        method_mappings: List[MethodCapacityMapping],
    ) -> Dict[CapacityType, CapacityScore]:
        """
        Calculate capacity scores for all 9 capacity types.
        
        Args:
            method_mappings: All method mappings
            
        Returns:
            Dictionary mapping each CapacityType to its CapacityScore
        """
        return {
            ct: self.calculate_capacity_score(ct, method_mappings)
            for ct in CapacityType.all_types()
        }
    
    def get_distribution(
        self,
        method_mappings: List[MethodCapacityMapping],
    ) -> Dict[str, int]:
        """
        Get distribution of methods across capacity types.
        
        Args:
            method_mappings: All method mappings
            
        Returns:
            Dictionary mapping capacity type codes to method counts
        """
        distribution: Dict[str, int] = {ct.code: 0 for ct in CapacityType.all_types()}
        for mapping in method_mappings:
            if mapping.capacity_type in distribution:
                distribution[mapping.capacity_type] += 1
        return distribution
    
    def get_statistics(
        self,
        method_mappings: List[MethodCapacityMapping],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive statistics for method mappings.
        
        Args:
            method_mappings: All method mappings
            
        Returns:
            Dictionary with statistics including:
            - total_methods
            - by_capacity_type
            - by_skill
            - by_level
            - by_epistemology
            - confidence_distribution
            - score_statistics
        """
        total = len(method_mappings)
        
        # By capacity type
        by_capacity = self.get_distribution(method_mappings)
        
        # By skill
        by_skill = {skill.value: 0 for skill in PolicySkill.all_skills()}
        for mapping in method_mappings:
            try:
                ct = CapacityType.from_code(mapping.capacity_type)
                by_skill[ct.skill.value] += 1
            except ValueError:
                pass
        
        # By level
        by_level = {level.value: 0 for level in PolicyLevel.all_levels()}
        for mapping in method_mappings:
            try:
                ct = CapacityType.from_code(mapping.capacity_type)
                by_level[ct.level.value] += 1
            except ValueError:
                pass
        
        # By epistemology
        by_epistemology: Dict[str, int] = {}
        for mapping in method_mappings:
            ep = mapping.epistemological_level
            by_epistemology[ep] = by_epistemology.get(ep, 0) + 1
        
        # Confidence distribution
        high_conf = sum(1 for m in method_mappings if m.classification_confidence >= 0.8)
        med_conf = sum(1 for m in method_mappings if 0.5 <= m.classification_confidence < 0.8)
        low_conf = sum(1 for m in method_mappings if m.classification_confidence < 0.5)
        
        # Score statistics
        scores = [m.base_score for m in method_mappings]
        mean_score = sum(scores) / len(scores) if scores else 0
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        
        return {
            "total_methods": total,
            "by_capacity_type": by_capacity,
            "by_skill": by_skill,
            "by_level": by_level,
            "by_epistemology": by_epistemology,
            "confidence_distribution": {
                "high": high_conf,
                "medium": med_conf,
                "low": low_conf,
            },
            "score_statistics": {
                "mean": round(mean_score, 4),
                "min": round(min_score, 4),
                "max": round(max_score, 4),
            },
        }


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "BaseCapacityScorer",
    "CapacityScoringConfig",
    "EpistemologyWeights",
    "LevelWeights",
    "OutputTypeWeights",
    "CapacityMappingRule",
    "DEFAULT_MAPPING_RULES",
]
