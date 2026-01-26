"""
Policy Capacity Type Definitions
================================

This module defines the core type system for the Wu, Ramesh & Howlett (2015)
Policy Capacity Framework implementation.

The type system includes:
- PolicySkill: The three skills (Analytical, Operational, Political)
- PolicyLevel: The three levels (Individual, Organizational, Systemic)
- CapacityType: The 9 capacity types (3×3 matrix)
- EpistemologicalLevel: Mapping from epistemological classification
- EquipmentCongregation: Synergistic skill combinations
- Data structures for scoring, mapping, and aggregation

Mathematical Foundations:
------------------------
The mapping from epistemological levels to capacity types follows:
- N1-EMP (Empirical) → CA-I (Individual Analytical)
- N2-INF (Inferential) → CA-O/CO-O (Organizational, mixed)
- N3-AUD (Audit) → CO-S/CP-O (Systemic/Political, mixed)

Author: F.A.R.F.A.N. Core Team
Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import (
    Dict,
    FrozenSet,
    List,
    Literal,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
    Union,
    Any,
)


# ============================================================================
# POLICY SKILL ENUMERATION
# ============================================================================

@unique
class PolicySkill(Enum):
    """
    Wu Framework: Three types of policy skills (competences).
    
    These represent WHAT capacities are needed:
    
    ANALYTICAL:
        - Evidence-based analysis, research, data literacy
        - Technical knowledge and scientific understanding
        - Ability to process and interpret information
        
    OPERATIONAL:
        - Implementation, execution, coordination
        - Resource management and allocation
        - Project management and delivery
        
    POLITICAL:
        - Legitimacy and stakeholder engagement
        - Coalition building and negotiation
        - Political acumen and communication
    """
    
    ANALYTICAL = "Analytical"
    OPERATIONAL = "Operational"
    POLITICAL = "Political"
    
    @property
    def code(self) -> str:
        """Short code for capacity type prefixing."""
        return {
            self.ANALYTICAL: "CA",
            self.OPERATIONAL: "CO",
            self.POLITICAL: "CP",
        }[self]
    
    @property
    def weight(self) -> float:
        """
        Default weight for ICI calculation.
        
        Weights based on Wu et al. (2015) framework emphasis:
        - Analytical: 0.40 (foundational for evidence-based policy)
        - Operational: 0.35 (critical for implementation)
        - Political: 0.25 (essential but often tacit)
        """
        return {
            self.ANALYTICAL: 0.40,
            self.OPERATIONAL: 0.35,
            self.POLITICAL: 0.25,
        }[self]
    
    @property
    def description(self) -> str:
        """Detailed description of this skill type."""
        descriptions = {
            self.ANALYTICAL: (
                "Analytical capacity encompasses the ability to access, process, "
                "and utilize evidence in policy-making. It includes research skills, "
                "data literacy, statistical competence, and the capacity to translate "
                "complex information into actionable insights."
            ),
            self.OPERATIONAL: (
                "Operational capacity refers to the ability to mobilize resources, "
                "coordinate activities, and implement policies effectively. It includes "
                "project management, logistics, resource allocation, and the capacity "
                "to achieve results within constraints."
            ),
            self.POLITICAL: (
                "Political capacity involves the ability to build legitimacy, engage "
                "stakeholders, and navigate political environments. It includes "
                "negotiation skills, coalition building, communication, and the "
                "capacity to maintain support for policy initiatives."
            ),
        }
        return descriptions[self]
    
    @classmethod
    def all_skills(cls) -> List["PolicySkill"]:
        """Return all skills in canonical order."""
        return [cls.ANALYTICAL, cls.OPERATIONAL, cls.POLITICAL]


# ============================================================================
# POLICY LEVEL ENUMERATION
# ============================================================================

@unique
class PolicyLevel(Enum):
    """
    Wu Framework: Three levels of policy capability.
    
    These represent WHERE capacities reside:
    
    INDIVIDUAL:
        - Personal skills, knowledge, competencies
        - Training and professional development
        - Individual expertise and experience
        
    ORGANIZATIONAL:
        - Institutional structures, procedures, resources
        - Organizational culture and processes
        - Internal coordination and information systems
        
    SYSTEMIC:
        - Inter-organizational networks and arrangements
        - Societal trust and legitimacy
        - Broader institutional environment
    """
    
    INDIVIDUAL = "Individual"
    ORGANIZATIONAL = "Organizational"
    SYSTEMIC = "Systemic"
    
    @property
    def code(self) -> str:
        """Short code for capacity type suffixing."""
        return {
            self.INDIVIDUAL: "I",
            self.ORGANIZATIONAL: "O",
            self.SYSTEMIC: "S",
        }[self]
    
    @property
    def weight(self) -> float:
        """
        Default weight for ICI calculation.
        
        Weights based on aggregation hierarchy:
        - Individual: 0.25 (foundational building blocks)
        - Organizational: 0.35 (primary policy implementation locus)
        - Systemic: 0.40 (ultimate capacity expression)
        """
        return {
            self.INDIVIDUAL: 0.25,
            self.ORGANIZATIONAL: 0.35,
            self.SYSTEMIC: 0.40,
        }[self]
    
    @property
    def aggregation_order(self) -> int:
        """Order in aggregation pipeline (0=lowest, 2=highest)."""
        return {
            self.INDIVIDUAL: 0,
            self.ORGANIZATIONAL: 1,
            self.SYSTEMIC: 2,
        }[self]
    
    @property
    def description(self) -> str:
        """Detailed description of this level."""
        descriptions = {
            self.INDIVIDUAL: (
                "Individual level capacity resides in persons - their skills, "
                "knowledge, training, and professional competencies. This forms "
                "the foundational layer of policy capacity, representing the "
                "human capital available for policy work."
            ),
            self.ORGANIZATIONAL: (
                "Organizational level capacity resides in institutions - their "
                "structures, processes, resources, and cultures. This represents "
                "how individual capacities are organized and coordinated within "
                "formal institutional arrangements."
            ),
            self.SYSTEMIC: (
                "Systemic level capacity resides in the broader environment - "
                "inter-organizational networks, societal trust, legitimacy, and "
                "institutional arrangements. This represents the enabling context "
                "for organizational and individual capacity to be effective."
            ),
        }
        return descriptions[self]
    
    @classmethod
    def all_levels(cls) -> List["PolicyLevel"]:
        """Return all levels in aggregation order."""
        return [cls.INDIVIDUAL, cls.ORGANIZATIONAL, cls.SYSTEMIC]
    
    def distance_to(self, other: "PolicyLevel") -> int:
        """Calculate aggregation distance between levels."""
        return abs(self.aggregation_order - other.aggregation_order)


# ============================================================================
# CAPACITY TYPE ENUMERATION
# ============================================================================

@unique
class CapacityType(Enum):
    """
    Wu Framework: 9 capacity types (3 skills × 3 levels).
    
    Each capacity type represents a unique intersection of:
    - A policy SKILL (what competence is needed)
    - A policy LEVEL (where the capacity resides)
    
    Matrix Structure:
    
                  Analytical    Operational    Political
    Individual    CA-I          CO-I           CP-I
    Organizational CA-O         CO-O           CP-O
    Systemic      CA-S          CO-S           CP-S
    """
    
    # Analytical skill capacities
    CA_I = ("CA-I", PolicySkill.ANALYTICAL, PolicyLevel.INDIVIDUAL)
    CA_O = ("CA-O", PolicySkill.ANALYTICAL, PolicyLevel.ORGANIZATIONAL)
    CA_S = ("CA-S", PolicySkill.ANALYTICAL, PolicyLevel.SYSTEMIC)
    
    # Operational skill capacities
    CO_I = ("CO-I", PolicySkill.OPERATIONAL, PolicyLevel.INDIVIDUAL)
    CO_O = ("CO-O", PolicySkill.OPERATIONAL, PolicyLevel.ORGANIZATIONAL)
    CO_S = ("CO-S", PolicySkill.OPERATIONAL, PolicyLevel.SYSTEMIC)
    
    # Political skill capacities
    CP_I = ("CP-I", PolicySkill.POLITICAL, PolicyLevel.INDIVIDUAL)
    CP_O = ("CP-O", PolicySkill.POLITICAL, PolicyLevel.ORGANIZATIONAL)
    CP_S = ("CP-S", PolicySkill.POLITICAL, PolicyLevel.SYSTEMIC)
    
    def __init__(self, code: str, skill: PolicySkill, level: PolicyLevel):
        self._code = code
        self._skill = skill
        self._level = level
    
    @property
    def code(self) -> str:
        """Canonical capacity type code (e.g., 'CA-I')."""
        return self._code
    
    @property
    def skill(self) -> PolicySkill:
        """Policy skill component."""
        return self._skill
    
    @property
    def level(self) -> PolicyLevel:
        """Policy level component."""
        return self._level
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return f"{self._level.value} {self._skill.value.lower()} capacity"
    
    @property
    def detailed_description(self) -> str:
        """Detailed description of this specific capacity type."""
        descriptions = {
            self.CA_I: (
                "Individual analytical capacity: Personal skills in research, "
                "data analysis, evidence interpretation, and scientific reasoning. "
                "Includes training in methodology and analytical techniques."
            ),
            self.CA_O: (
                "Organizational analytical capacity: Institutional resources for "
                "analysis including data systems, research units, analytical tools, "
                "and protocols for evidence-based decision making."
            ),
            self.CA_S: (
                "Systemic analytical capacity: Broader epistemic infrastructure "
                "including research networks, academic partnerships, knowledge "
                "sharing systems, and societal data infrastructure."
            ),
            self.CO_I: (
                "Individual operational capacity: Personal skills in project "
                "management, resource allocation, coordination, and the ability "
                "to achieve results within constraints."
            ),
            self.CO_O: (
                "Organizational operational capacity: Institutional resources for "
                "implementation including budgets, staffing, procedures, technology, "
                "and organizational processes for policy delivery."
            ),
            self.CO_S: (
                "Systemic operational capacity: Inter-organizational coordination "
                "mechanisms, public-private partnerships, service delivery networks, "
                "and institutional arrangements for collective action."
            ),
            self.CP_I: (
                "Individual political capacity: Personal skills in negotiation, "
                "communication, stakeholder engagement, and the ability to build "
                "support for policy initiatives."
            ),
            self.CP_O: (
                "Organizational political capacity: Institutional resources for "
                "political engagement including consultation mechanisms, stakeholder "
                "management systems, and communication infrastructure."
            ),
            self.CP_S: (
                "Systemic political capacity: Broader political environment including "
                "societal trust, democratic legitimacy, civic engagement norms, "
                "and the institutional basis for collective agreement."
            ),
        }
        return descriptions[self]
    
    @classmethod
    def from_code(cls, code: str) -> "CapacityType":
        """Get capacity type from string code."""
        code_map = {ct.code: ct for ct in cls}
        if code not in code_map:
            raise ValueError(f"Unknown capacity type code: {code}")
        return code_map[code]
    
    @classmethod
    def from_skill_level(cls, skill: PolicySkill, level: PolicyLevel) -> "CapacityType":
        """Get capacity type from skill and level combination."""
        for ct in cls:
            if ct.skill == skill and ct.level == level:
                return ct
        raise ValueError(f"No capacity type for {skill.value} × {level.value}")
    
    @classmethod
    def all_types(cls) -> List["CapacityType"]:
        """Return all 9 capacity types in canonical order."""
        return list(cls)
    
    @classmethod
    def by_skill(cls, skill: PolicySkill) -> List["CapacityType"]:
        """Return capacity types for a specific skill."""
        return [ct for ct in cls if ct.skill == skill]
    
    @classmethod
    def by_level(cls, level: PolicyLevel) -> List["CapacityType"]:
        """Return capacity types for a specific level."""
        return [ct for ct in cls if ct.level == level]
    
    def is_same_skill(self, other: "CapacityType") -> bool:
        """Check if two capacity types share the same skill."""
        return self.skill == other.skill
    
    def is_same_level(self, other: "CapacityType") -> bool:
        """Check if two capacity types share the same level."""
        return self.level == other.level
    
    def level_distance(self, other: "CapacityType") -> int:
        """Calculate aggregation level distance."""
        return self.level.distance_to(other.level)


# ============================================================================
# EPISTEMOLOGICAL LEVEL ENUMERATION
# ============================================================================

@unique
class EpistemologicalLevel(Enum):
    """
    Epistemological levels from episteme_rules.md.
    
    These map to capacity types via specific rules:
    - N0-INFRA: Infrastructure support (not mapped)
    - N1-EMP: Empirical extraction → CA-I (Individual Analytical)
    - N2-INF: Inferential computation → CA-O/CO-O (Organizational)
    - N3-AUD: Audit/validation → CO-S/CP-O (Systemic/Political)
    - N4-META: Meta-analysis (not mapped)
    """
    
    N0_INFRA = ("N0-INFRA", "Infrastructural support", "Instrumentalismo", "INFRASTRUCTURE")
    N1_EMP = ("N1-EMP", "Raw fact extraction", "Empirismo positivista", "FACT")
    N2_INF = ("N2-INF", "Probabilistic inference", "Bayesianismo subjetivista", "PARAMETER")
    N3_AUD = ("N3-AUD", "Critical validation", "Falsacionismo popperiano", "CONSTRAINT")
    N4_META = ("N4-META", "Meta-analysis", "Reflexividad crítica", "META_ANALYSIS")
    
    def __init__(self, code: str, description: str, epistemology: str, output_type: str):
        self._code = code
        self._description = description
        self._epistemology = epistemology
        self._output_type = output_type
    
    @property
    def code(self) -> str:
        return self._code
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def epistemology(self) -> str:
        return self._epistemology
    
    @property
    def output_type(self) -> str:
        return self._output_type
    
    @property
    def primary_capacity_type(self) -> Optional[CapacityType]:
        """Primary capacity type mapping for this epistemological level."""
        mapping = {
            self.N1_EMP: CapacityType.CA_I,
            self.N2_INF: CapacityType.CA_O,
            self.N3_AUD: CapacityType.CO_S,
        }
        return mapping.get(self)
    
    @property
    def secondary_capacity_type(self) -> Optional[CapacityType]:
        """Secondary capacity type mapping (for split classifications)."""
        mapping = {
            self.N2_INF: CapacityType.CO_O,
            self.N3_AUD: CapacityType.CP_O,
        }
        return mapping.get(self)
    
    @property
    def epistemology_weight(self) -> float:
        """Weight for base capacity score calculation."""
        weights = {
            self.N0_INFRA: 0.50,
            self.N1_EMP: 0.85,
            self.N2_INF: 1.00,
            self.N3_AUD: 0.92,
            self.N4_META: 0.80,
        }
        return weights[self]
    
    @property
    def level_weight(self) -> float:
        """Level weight for base capacity score calculation."""
        weights = {
            self.N0_INFRA: 0.5,
            self.N1_EMP: 1.0,
            self.N2_INF: 1.5,
            self.N3_AUD: 2.0,
            self.N4_META: 2.5,
        }
        return weights[self]
    
    @classmethod
    def from_code(cls, code: str) -> "EpistemologicalLevel":
        """Get level from code string."""
        for level in cls:
            if level.code == code:
                return level
        raise ValueError(f"Unknown epistemological level code: {code}")


# ============================================================================
# EQUIPMENT CONGREGATION
# ============================================================================

class EquipmentCongregation(Enum):
    """
    Equipment Congregation types with synergy coefficients.
    
    When multiple capacity skills are combined, they produce MULTIPLICATIVE
    gains rather than additive. This captures the synergy effects described
    in the Policy Capacity Framework.
    
    Synergy Quantification:
        Simple Addition:    CA + CO = 2.0 units
        With Congregation:  CA ⊗ CO = 2.0 × 1.35 = 2.7 units (+35% boost)
    """
    
    EVIDENCE_ACTION_NEXUS = (
        "evidence_action_nexus",
        frozenset({PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL}),
        1.35,
        "Synergy between analytical rigor and operational implementation"
    )
    
    STRATEGIC_INTELLIGENCE = (
        "strategic_intelligence",
        frozenset({PolicySkill.ANALYTICAL, PolicySkill.POLITICAL}),
        1.42,
        "Synergy between evidence-based analysis and political feasibility"
    )
    
    ADAPTIVE_GOVERNANCE = (
        "adaptive_governance",
        frozenset({PolicySkill.OPERATIONAL, PolicySkill.POLITICAL}),
        1.28,
        "Synergy between execution capacity and political legitimacy"
    )
    
    INTEGRATED_CAPACITY = (
        "integrated_capacity",
        frozenset({PolicySkill.ANALYTICAL, PolicySkill.OPERATIONAL, PolicySkill.POLITICAL}),
        1.75,
        "Full trinity: evidence, execution, and legitimacy"
    )
    
    def __init__(
        self,
        name: str,
        skills: FrozenSet[PolicySkill],
        coefficient: float,
        description: str,
    ):
        self._name = name
        self._skills = skills
        self._coefficient = coefficient
        self._description = description
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def skills(self) -> FrozenSet[PolicySkill]:
        return self._skills
    
    @property
    def coefficient(self) -> float:
        """Synergy coefficient (ρ) for multiplicative boost."""
        return self._coefficient
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def skill_count(self) -> int:
        return len(self._skills)
    
    def contains_skill(self, skill: PolicySkill) -> bool:
        """Check if this congregation includes a specific skill."""
        return skill in self._skills
    
    @classmethod
    def from_skills(cls, skills: Set[PolicySkill]) -> Optional["EquipmentCongregation"]:
        """
        Find the equipment congregation matching a set of skills.
        
        Returns None if no matching congregation exists.
        """
        skills_frozen = frozenset(skills)
        for congregation in cls:
            if congregation.skills == skills_frozen:
                return congregation
        return None
    
    @classmethod
    def all_congregations(cls) -> List["EquipmentCongregation"]:
        """Return all equipment congregations."""
        return list(cls)
    
    def calculate_multiplier(self, delta: float = 0.3) -> float:
        """
        Calculate the equipment congregation multiplier.
        
        Formula: M_equip = 1 + δ × ln(1 + n_skills) × (ρ - 1)
        
        Args:
            delta: Congregation sensitivity parameter (default: 0.3)
            
        Returns:
            Multiplier value for capacity score enhancement.
        """
        n_skills = self.skill_count
        rho = self._coefficient
        return 1.0 + delta * math.log(1 + n_skills) * (rho - 1)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass(frozen=True)
class CapacityScore:
    """
    Immutable capacity score for a single capacity type.
    
    Attributes:
        capacity_type: The specific capacity type being scored
        raw_score: Unweighted base score [0, ∞)
        weighted_score: Score with level/skill weights applied
        confidence: Classification confidence [0, 1]
        method_count: Number of methods contributing to this score
    """
    
    capacity_type: CapacityType
    raw_score: float
    weighted_score: float
    confidence: float
    method_count: int
    
    def __post_init__(self):
        # Validate ranges
        if self.raw_score < 0:
            raise ValueError(f"raw_score must be non-negative: {self.raw_score}")
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"confidence must be in [0, 1]: {self.confidence}")
        if self.method_count < 0:
            raise ValueError(f"method_count must be non-negative: {self.method_count}")
    
    @property
    def normalized_score(self) -> float:
        """Score normalized to [0, 1] range using sigmoid."""
        return 1.0 / (1.0 + math.exp(-self.weighted_score + 1.0))
    
    @property
    def is_significant(self) -> bool:
        """Check if score represents significant capacity (>0.5 normalized)."""
        return self.normalized_score > 0.5
    
    def with_adjustment(self, factor: float) -> "CapacityScore":
        """Create new score with adjustment factor applied."""
        return CapacityScore(
            capacity_type=self.capacity_type,
            raw_score=self.raw_score * factor,
            weighted_score=self.weighted_score * factor,
            confidence=self.confidence,
            method_count=self.method_count,
        )


@dataclass
class MethodCapacityMapping:
    """
    Mapping of a single method to its capacity classification.
    
    Attributes:
        method_id: Unique identifier (e.g., 'M001' or 'ClassName.method_name')
        class_name: Class containing the method
        method_name: Method name
        file_path: Source file path
        epistemological_level: Classified epistemic level
        output_type: Method output type (FACT, PARAMETER, CONSTRAINT)
        capacity_type: Assigned capacity type
        base_score: Calculated base capacity score
        classification_confidence: Confidence in classification [0, 1]
        classification_evidence: List of evidence supporting classification
    """
    
    method_id: str
    class_name: str
    method_name: str
    file_path: str
    epistemological_level: str
    output_type: str
    capacity_type: str
    base_score: float
    classification_confidence: float = 0.0
    classification_evidence: List[str] = field(default_factory=list)
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if classification has high confidence (≥0.8)."""
        return self.classification_confidence >= 0.8
    
    @property
    def is_public(self) -> bool:
        """Check if method is public (no leading underscore)."""
        return not self.method_name.startswith("_")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "method_id": self.method_id,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "file_path": self.file_path,
            "epistemological_level": self.epistemological_level,
            "output_type": self.output_type,
            "capacity_type": self.capacity_type,
            "base_score": self.base_score,
            "classification_confidence": self.classification_confidence,
            "classification_evidence": self.classification_evidence,
        }


@dataclass
class AggregatedCapacity:
    """
    Aggregated capacity at a specific level.
    
    Represents the result of aggregating capacities from lower levels
    to higher levels (Individual → Organizational → Systemic).
    """
    
    level: PolicyLevel
    skill: PolicySkill
    source_scores: List[CapacityScore]
    aggregated_score: float
    aggregation_method: str
    equipment_multiplier: float = 1.0
    cross_level_contribution: float = 0.0
    
    @property
    def capacity_type(self) -> CapacityType:
        """Get the capacity type for this aggregation."""
        return CapacityType.from_skill_level(self.skill, self.level)
    
    @property
    def effective_score(self) -> float:
        """Calculate effective score with equipment multiplier."""
        return self.aggregated_score * self.equipment_multiplier
    
    @property
    def total_methods(self) -> int:
        """Total methods contributing to this aggregation."""
        return sum(s.method_count for s in self.source_scores)


@dataclass
class CapacityGap:
    """
    Identified gap in capacity coverage.
    
    Gaps are identified when a capacity type has insufficient
    methods or scores below thresholds.
    """
    
    capacity_type: CapacityType
    current_score: float
    target_score: float
    gap_magnitude: float
    severity: Literal["critical", "major", "minor", "acceptable"]
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def is_critical(self) -> bool:
        """Check if gap is critical severity."""
        return self.severity == "critical"
    
    @property
    def percentage_shortfall(self) -> float:
        """Calculate gap as percentage of target."""
        if self.target_score == 0:
            return 0.0
        return (self.target_score - self.current_score) / self.target_score * 100


@dataclass
class CapacityProfile:
    """
    Complete capacity profile for a policy analysis.
    
    Contains all capacity scores, aggregations, and diagnostics
    for comprehensive capacity assessment.
    """
    
    # Raw scores
    capacity_scores: Dict[CapacityType, CapacityScore]
    
    # Aggregated scores
    skill_aggregates: Dict[PolicySkill, float]
    level_aggregates: Dict[PolicyLevel, float]
    
    # Integrated metrics
    integrated_capacity_index: float
    
    # Equipment effects
    congregation_effects: Dict[EquipmentCongregation, float]
    
    # Gaps and recommendations
    identified_gaps: List[CapacityGap]
    
    # Metadata
    total_methods: int
    analysis_timestamp: str
    version: str = "1.0.0"
    
    @property
    def strongest_skill(self) -> Tuple[PolicySkill, float]:
        """Return the skill with highest aggregate score."""
        return max(self.skill_aggregates.items(), key=lambda x: x[1])
    
    @property
    def weakest_skill(self) -> Tuple[PolicySkill, float]:
        """Return the skill with lowest aggregate score."""
        return min(self.skill_aggregates.items(), key=lambda x: x[1])
    
    @property
    def strongest_level(self) -> Tuple[PolicyLevel, float]:
        """Return the level with highest aggregate score."""
        return max(self.level_aggregates.items(), key=lambda x: x[1])
    
    @property
    def weakest_level(self) -> Tuple[PolicyLevel, float]:
        """Return the level with lowest aggregate score."""
        return min(self.level_aggregates.items(), key=lambda x: x[1])
    
    @property
    def critical_gaps_count(self) -> int:
        """Count of critical gaps."""
        return sum(1 for gap in self.identified_gaps if gap.is_critical)
    
    @property
    def is_balanced(self) -> bool:
        """
        Check if capacity profile is balanced.
        
        Balanced means no critical gaps and reasonable spread
        across all dimensions.
        """
        if self.critical_gaps_count > 0:
            return False
        
        # Check skill balance (max/min ratio < 2)
        skill_values = list(self.skill_aggregates.values())
        if max(skill_values) / max(min(skill_values), 0.01) > 2.0:
            return False
        
        # Check level balance
        level_values = list(self.level_aggregates.values())
        if max(level_values) / max(min(level_values), 0.01) > 2.0:
            return False
        
        return True
    
    def get_score(self, capacity_type: CapacityType) -> Optional[CapacityScore]:
        """Get score for a specific capacity type."""
        return self.capacity_scores.get(capacity_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "capacity_scores": {
                ct.code: {
                    "raw_score": score.raw_score,
                    "weighted_score": score.weighted_score,
                    "confidence": score.confidence,
                    "method_count": score.method_count,
                }
                for ct, score in self.capacity_scores.items()
            },
            "skill_aggregates": {
                skill.value: score for skill, score in self.skill_aggregates.items()
            },
            "level_aggregates": {
                level.value: score for level, score in self.level_aggregates.items()
            },
            "integrated_capacity_index": self.integrated_capacity_index,
            "congregation_effects": {
                ec.name: effect for ec, effect in self.congregation_effects.items()
            },
            "identified_gaps": [
                {
                    "capacity_type": gap.capacity_type.code,
                    "current_score": gap.current_score,
                    "target_score": gap.target_score,
                    "gap_magnitude": gap.gap_magnitude,
                    "severity": gap.severity,
                    "recommendations": gap.recommendations,
                }
                for gap in self.identified_gaps
            ],
            "total_methods": self.total_methods,
            "analysis_timestamp": self.analysis_timestamp,
            "version": self.version,
        }


# ============================================================================
# PROTOCOLS
# ============================================================================

class CapacityScoreable(Protocol):
    """Protocol for objects that can be scored for policy capacity."""
    
    def calculate_capacity_score(self) -> CapacityScore:
        """Calculate capacity score for this object."""
        ...


class CapacityAggregatable(Protocol):
    """Protocol for objects that can be aggregated across capacity levels."""
    
    def aggregate_to_level(self, target_level: PolicyLevel) -> AggregatedCapacity:
        """Aggregate capacity to target level."""
        ...


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Core enums
    "PolicySkill",
    "PolicyLevel",
    "CapacityType",
    "EpistemologicalLevel",
    "EquipmentCongregation",
    # Data structures
    "CapacityScore",
    "MethodCapacityMapping",
    "AggregatedCapacity",
    "CapacityGap",
    "CapacityProfile",
    # Protocols
    "CapacityScoreable",
    "CapacityAggregatable",
]
