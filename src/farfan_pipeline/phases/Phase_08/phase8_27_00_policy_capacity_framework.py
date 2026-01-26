# phase8_27_00_policy_capacity_framework.py - Policy Capacity Framework
"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_27_00_policy_capacity_framework
Purpose: Wu-Ramesh-Howlett 9-dimensional policy capacity assessment framework
Owner: phase8_enhanced
Stage: 27 (Capacity Framework)
Order: 00
Type: FRAMEWORK
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-26

═══════════════════════════════════════════════════════════════════════════════════
    🎯 POLICY CAPACITY FRAMEWORK - 9-Dimensional Assessment 🎯
═══════════════════════════════════════════════════════════════════════════════════

THEORETICAL FOUNDATION:
    Based on Wu, Ramesh, and Howlett's framework, policy capacity is:
    "The set of skills and resources—competences and capabilities—necessary to 
    perform policy functions"
    
    3×3 MATRIX STRUCTURE:
                    Analytical    Operational    Political
    Individual      [1]           [2]            [3]
    Organizational  [4]           [5]            [6]
    Systemic        [7]           [8]            [9]

KEY FEATURES:
    1. Capacity assessment across all 9 dimensions
    2. Binding constraint identification
    3. Instrument selection calibration
    4. Sequential capacity building recommendations
    5. Colombian municipal context integration

INTEGRATION:
    - Used by instrument selection module (phase8_28)
    - Feeds dimensional recommendation engine (phase8_26)
    - Informs budget and timeline specification (phase8_30)

Author: F.A.R.F.A.N Architecture Team
Python: 3.10+
═══════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 8
__stage__ = 27
__order__ = 0
__author__ = "F.A.R.F.A.N Architecture Team"
__created__ = "2026-01-26"
__modified__ = "2026-01-26"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"
__codename__ = "CAPACITY-FRAMEWORK"

# =============================================================================
# IMPORTS
# =============================================================================

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    "CapacityLevel",
    "CapacityDimension",
    "CapacityAssessment",
    "PolicyCapacityFramework",
    "BindingConstraint",
    "capacity_level_from_evidence",
]

# =============================================================================
# ENUMERATIONS
# =============================================================================


class CapacityLevel(str, Enum):
    """Capacity level classification"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CapacityDimension(str, Enum):
    """9-dimensional capacity framework"""
    # Individual level (skills and competences of individuals)
    INDIVIDUAL_ANALYTICAL = "INDIVIDUAL_ANALYTICAL"
    INDIVIDUAL_OPERATIONAL = "INDIVIDUAL_OPERATIONAL"
    INDIVIDUAL_POLITICAL = "INDIVIDUAL_POLITICAL"
    
    # Organizational level (capabilities of organizations)
    ORGANIZATIONAL_ANALYTICAL = "ORGANIZATIONAL_ANALYTICAL"
    ORGANIZATIONAL_OPERATIONAL = "ORGANIZATIONAL_OPERATIONAL"
    ORGANIZATIONAL_POLITICAL = "ORGANIZATIONAL_POLITICAL"
    
    # Systemic level (broader governance system)
    SYSTEMIC_ANALYTICAL = "SYSTEMIC_ANALYTICAL"
    SYSTEMIC_OPERATIONAL = "SYSTEMIC_OPERATIONAL"
    SYSTEMIC_POLITICAL = "SYSTEMIC_POLITICAL"


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class CapacityAssessment:
    """Assessment of a single capacity dimension"""
    dimension: CapacityDimension
    level: CapacityLevel
    evidence: list[str]
    implications: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BindingConstraint:
    """Identified binding constraint on policy implementation"""
    dimension: CapacityDimension
    level: CapacityLevel
    rationale: str
    priority: int  # 1 = most binding
    mitigation_strategies: list[str]
    sequencing_implications: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComprehensiveCapacityProfile:
    """Complete 9-dimensional capacity profile"""
    municipality_id: str
    municipality_category: int  # 1-6 (Special, 1-6)
    
    # Individual level
    individual_analytical: CapacityAssessment
    individual_operational: CapacityAssessment
    individual_political: CapacityAssessment
    
    # Organizational level
    organizational_analytical: CapacityAssessment
    organizational_operational: CapacityAssessment
    organizational_political: CapacityAssessment
    
    # Systemic level
    systemic_analytical: CapacityAssessment
    systemic_operational: CapacityAssessment
    systemic_political: CapacityAssessment
    
    # Binding constraints
    binding_constraints: list[BindingConstraint]
    
    # Overall assessment
    overall_capacity_level: CapacityLevel
    implementation_readiness: str
    recommended_sequencing: list[str]
    
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# POLICY CAPACITY FRAMEWORK
# =============================================================================


class PolicyCapacityFramework:
    """
    9-dimensional policy capacity assessment framework.
    
    Assesses municipal capacity across:
    - 3 skill types: Analytical, Operational, Political
    - 3 levels: Individual, Organizational, Systemic
    
    Generates capacity profile to guide instrument selection.
    """
    
    # Capacity assessment criteria by dimension
    CAPACITY_CRITERIA = {
        CapacityDimension.INDIVIDUAL_ANALYTICAL: {
            "LOW": [
                "Planning staff <3 or no advanced training",
                "No specialized knowledge in policy area",
                "Cannot interpret statistical data",
                "No data analysis tools or skills"
            ],
            "MEDIUM": [
                "3-5 staff with some technical training",
                "Basic statistical literacy",
                "Can use standard analysis tools (Excel, basic GIS)",
                "Some policy area knowledge"
            ],
            "HIGH": [
                ">5 qualified staff with advanced degrees",
                "Specialized policy area expertise",
                "Advanced analysis capabilities (statistical software, GIS)",
                "Evidence-based decision-making culture"
            ]
        },
        CapacityDimension.INDIVIDUAL_OPERATIONAL: {
            "LOW": [
                "Staff unfamiliar with procurement/budget processes",
                "High error rates in administrative tasks",
                "Budget execution <60%",
                "Cannot manage complex projects"
            ],
            "MEDIUM": [
                "Staff understand basic processes",
                "Budget execution 60-85%",
                "Can manage moderate complexity projects",
                "Some project management tools used"
            ],
            "HIGH": [
                "Strong administrative competence",
                "Budget execution >85%",
                "Effective project management systems",
                "Process optimization culture"
            ]
        },
        CapacityDimension.INDIVIDUAL_POLITICAL: {
            "LOW": [
                "No prior policy experience",
                "Weak stakeholder management skills",
                "Cannot build coalitions",
                "Poor negotiation capabilities"
            ],
            "MEDIUM": [
                "Some policy experience",
                "Basic stakeholder engagement",
                "Can navigate simple political processes",
                "Moderate negotiation skills"
            ],
            "HIGH": [
                "Extensive policy experience",
                "Strong stakeholder networks",
                "Coalition building capabilities",
                "Strategic political acumen"
            ]
        },
        CapacityDimension.ORGANIZATIONAL_ANALYTICAL: {
            "LOW": [
                "No data collection systems",
                "No monitoring & evaluation unit",
                "Cannot disaggregate data by key variables",
                "No institutional memory/documentation"
            ],
            "MEDIUM": [
                "Basic data collection systems",
                "Some M&E capacity",
                "Partial data disaggregation",
                "Limited documentation practices"
            ],
            "HIGH": [
                "Robust information management systems",
                "Dedicated M&E unit",
                "Comprehensive data disaggregation",
                "Strong institutional memory"
            ]
        },
        CapacityDimension.ORGANIZATIONAL_OPERATIONAL: {
            "LOW": [
                "High staff turnover (>50%/term)",
                "No standard operating procedures",
                "Weak inter-secretariat coordination",
                "Cannot sustain programs beyond single term"
            ],
            "MEDIUM": [
                "Moderate turnover (25-50%)",
                "Some SOPs documented",
                "Functional but limited coordination",
                "Can maintain some multi-year programs"
            ],
            "HIGH": [
                "Low turnover (<25%)",
                "Comprehensive SOPs",
                "Strong coordination mechanisms",
                "Multi-term program continuity"
            ]
        },
        CapacityDimension.ORGANIZATIONAL_POLITICAL: {
            "LOW": [
                "No participation mechanisms beyond legal minimum",
                "Low community trust",
                "Cannot mobilize stakeholders",
                "Weak legitimacy"
            ],
            "MEDIUM": [
                "Some participation beyond legal minimum",
                "Moderate trust levels",
                "Can engage established stakeholders",
                "Moderate legitimacy"
            ],
            "HIGH": [
                "Active participation culture",
                "High community trust",
                "Can mobilize diverse stakeholders",
                "Strong legitimacy"
            ]
        },
        CapacityDimension.SYSTEMIC_ANALYTICAL: {
            "LOW": [
                "No nearby universities or research centers",
                "Weak departmental technical support",
                "No access to external expertise",
                "Isolated from knowledge networks"
            ],
            "MEDIUM": [
                "Regional university within 50km",
                "Functional departmental support",
                "Some external expertise accessible",
                "Limited network participation"
            ],
            "HIGH": [
                "Strong university partnerships",
                "Robust departmental/national support",
                "Easy access to external expertise",
                "Active in knowledge networks"
            ]
        },
        CapacityDimension.SYSTEMIC_OPERATIONAL: {
            "LOW": [
                "Weak relationships with other governments",
                "Cannot access national programs",
                "No shared service arrangements",
                "Limited inter-governmental coordination"
            ],
            "MEDIUM": [
                "Functional relationships with department",
                "Can access some national programs",
                "Limited shared services",
                "Basic coordination mechanisms"
            ],
            "HIGH": [
                "Strong inter-governmental relationships",
                "Effective national program access",
                "Multiple shared service arrangements",
                "Robust coordination platforms"
            ]
        },
        CapacityDimension.SYSTEMIC_POLITICAL: {
            "LOW": [
                "Electoral instability",
                "Low social capital",
                "Armed actor presence/conflict",
                "Weak civil society"
            ],
            "MEDIUM": [
                "Moderate electoral stability",
                "Moderate social capital",
                "Declining conflict",
                "Emerging civil society"
            ],
            "HIGH": [
                "Electoral stability",
                "High social capital",
                "Peaceful context",
                "Strong civil society"
            ]
        }
    }
    
    def __init__(self):
        """Initialize the policy capacity framework"""
        logger.info("Policy Capacity Framework initialized")
    
    def assess_capacity_dimension(
        self,
        dimension: CapacityDimension,
        evidence: list[str]
    ) -> CapacityAssessment:
        """
        Assess capacity for a single dimension based on evidence.
        
        Args:
            dimension: Capacity dimension to assess
            evidence: List of evidence statements
            
        Returns:
            CapacityAssessment object
        """
        # Determine level by matching evidence to criteria
        level = self._determine_level_from_evidence(dimension, evidence)
        
        # Get implications for this level
        implications = self._get_implications_for_level(dimension, level)
        
        return CapacityAssessment(
            dimension=dimension,
            level=level,
            evidence=evidence,
            implications=implications,
            metadata={
                "criteria_matched": self._count_criteria_matches(dimension, level, evidence)
            }
        )
    
    def create_comprehensive_profile(
        self,
        municipality_id: str,
        municipality_category: int,
        assessments: dict[CapacityDimension, list[str]]
    ) -> ComprehensiveCapacityProfile:
        """
        Create comprehensive 9-dimensional capacity profile.
        
        Args:
            municipality_id: Municipality identifier
            municipality_category: Municipal category (1-6)
            assessments: Dict mapping dimensions to evidence lists
            
        Returns:
            ComprehensiveCapacityProfile object
        """
        # Assess each dimension
        dimension_assessments = {}
        for dimension in CapacityDimension:
            evidence = assessments.get(dimension, [])
            dimension_assessments[dimension] = self.assess_capacity_dimension(
                dimension, evidence
            )
        
        # Identify binding constraints
        binding_constraints = self._identify_binding_constraints(dimension_assessments)
        
        # Determine overall capacity level
        overall_level = self._calculate_overall_capacity(dimension_assessments)
        
        # Generate implementation readiness assessment
        readiness = self._assess_implementation_readiness(
            dimension_assessments, binding_constraints
        )
        
        # Generate recommended sequencing
        sequencing = self._generate_sequencing_recommendations(binding_constraints)
        
        return ComprehensiveCapacityProfile(
            municipality_id=municipality_id,
            municipality_category=municipality_category,
            individual_analytical=dimension_assessments[CapacityDimension.INDIVIDUAL_ANALYTICAL],
            individual_operational=dimension_assessments[CapacityDimension.INDIVIDUAL_OPERATIONAL],
            individual_political=dimension_assessments[CapacityDimension.INDIVIDUAL_POLITICAL],
            organizational_analytical=dimension_assessments[CapacityDimension.ORGANIZATIONAL_ANALYTICAL],
            organizational_operational=dimension_assessments[CapacityDimension.ORGANIZATIONAL_OPERATIONAL],
            organizational_political=dimension_assessments[CapacityDimension.ORGANIZATIONAL_POLITICAL],
            systemic_analytical=dimension_assessments[CapacityDimension.SYSTEMIC_ANALYTICAL],
            systemic_operational=dimension_assessments[CapacityDimension.SYSTEMIC_OPERATIONAL],
            systemic_political=dimension_assessments[CapacityDimension.SYSTEMIC_POLITICAL],
            binding_constraints=binding_constraints,
            overall_capacity_level=overall_level,
            implementation_readiness=readiness,
            recommended_sequencing=sequencing,
            metadata={
                "framework_version": __version__,
                "municipality_category": municipality_category
            }
        )
    
    def _determine_level_from_evidence(
        self,
        dimension: CapacityDimension,
        evidence: list[str]
    ) -> CapacityLevel:
        """Determine capacity level by matching evidence to criteria"""
        criteria = self.CAPACITY_CRITERIA[dimension]
        
        # Count matches for each level
        matches = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0
        }
        
        for evidence_item in evidence:
            for level, level_criteria in criteria.items():
                for criterion in level_criteria:
                    # Simple keyword matching (can be enhanced with NLP)
                    if any(keyword in evidence_item.lower() 
                          for keyword in criterion.lower().split()):
                        matches[level] += 1
        
        # Return level with most matches, defaulting to LOW if no clear match
        if not any(matches.values()):
            return CapacityLevel.LOW
        
        max_level = max(matches, key=matches.get)
        return CapacityLevel[max_level]
    
    def _count_criteria_matches(
        self,
        dimension: CapacityDimension,
        level: CapacityLevel,
        evidence: list[str]
    ) -> int:
        """Count how many criteria are matched"""
        criteria = self.CAPACITY_CRITERIA[dimension][level.value]
        matches = 0
        
        for evidence_item in evidence:
            for criterion in criteria:
                if any(keyword in evidence_item.lower() 
                      for keyword in criterion.lower().split()):
                    matches += 1
                    break
        
        return matches
    
    def _get_implications_for_level(
        self,
        dimension: CapacityDimension,
        level: CapacityLevel
    ) -> list[str]:
        """Get instrument selection implications for capacity level"""
        implications_map = {
            CapacityDimension.INDIVIDUAL_ANALYTICAL: {
                CapacityLevel.LOW: [
                    "Requires external technical assistance for analysis",
                    "Cannot design evidence-based interventions independently",
                    "Information instruments need external implementation support"
                ],
                CapacityLevel.MEDIUM: [
                    "Can implement moderate complexity analysis with guidance",
                    "Information instruments feasible with some external support"
                ],
                CapacityLevel.HIGH: [
                    "Can design sophisticated analytical interventions",
                    "Information instruments fully feasible"
                ]
            },
            CapacityDimension.ORGANIZATIONAL_OPERATIONAL: {
                CapacityLevel.LOW: [
                    "Organization instruments (new offices) risky without reorganization",
                    "Authority instruments (regulations) difficult to enforce",
                    "Should prioritize delegation models over direct provision"
                ],
                CapacityLevel.MEDIUM: [
                    "Can implement moderate organization instruments with support",
                    "Authority instruments feasible if enforcement is simple"
                ],
                CapacityLevel.HIGH: [
                    "Can create new organizational structures successfully",
                    "Authority instruments fully feasible with strong enforcement"
                ]
            },
            # Add more dimension-specific implications as needed
        }
        
        return implications_map.get(dimension, {}).get(
            level,
            [f"Standard implications for {level.value} capacity in {dimension.value}"]
        )
    
    def _identify_binding_constraints(
        self,
        assessments: dict[CapacityDimension, CapacityAssessment]
    ) -> list[BindingConstraint]:
        """Identify binding constraints from capacity assessments"""
        constraints = []
        
        # Priority 1: Organizational political capacity (most fundamental)
        if assessments[CapacityDimension.ORGANIZATIONAL_POLITICAL].level == CapacityLevel.LOW:
            constraints.append(BindingConstraint(
                dimension=CapacityDimension.ORGANIZATIONAL_POLITICAL,
                level=CapacityLevel.LOW,
                rationale="Without trust and participation mechanisms, even well-designed services won't be accessed",
                priority=1,
                mitigation_strategies=[
                    "Establish procedural instruments (committees, consultations) first",
                    "Build stakeholder trust through inclusive processes",
                    "Create participation mechanisms beyond legal minimum"
                ],
                sequencing_implications="Phase 1 must focus on building organizational political capacity before substantive interventions"
            ))
        
        # Priority 2: Organizational analytical capacity (needed for evidence-based design)
        if assessments[CapacityDimension.ORGANIZATIONAL_ANALYTICAL].level == CapacityLevel.LOW:
            constraints.append(BindingConstraint(
                dimension=CapacityDimension.ORGANIZATIONAL_ANALYTICAL,
                level=CapacityLevel.LOW,
                rationale="Cannot design evidence-based interventions or monitor progress without data systems",
                priority=2,
                mitigation_strategies=[
                    "Implement information systems with external support",
                    "Leverage national/departmental data platforms",
                    "Build M&E capacity incrementally"
                ],
                sequencing_implications="Phase 2 should establish basic data systems before launching complex programs"
            ))
        
        # Priority 3: Organizational operational capacity (needed for implementation)
        if assessments[CapacityDimension.ORGANIZATIONAL_OPERATIONAL].level == CapacityLevel.LOW:
            constraints.append(BindingConstraint(
                dimension=CapacityDimension.ORGANIZATIONAL_OPERATIONAL,
                level=CapacityLevel.LOW,
                rationale="Cannot sustain programs or coordinate effectively with weak operational capacity",
                priority=3,
                mitigation_strategies=[
                    "Use delegation models (inter-institutional agreements)",
                    "Develop SOPs incrementally",
                    "Reduce staff turnover through capacity building"
                ],
                sequencing_implications="Phase 3+ can implement substantive interventions using delegation"
            ))
        
        return constraints
    
    def _calculate_overall_capacity(
        self,
        assessments: dict[CapacityDimension, CapacityAssessment]
    ) -> CapacityLevel:
        """Calculate overall capacity level from dimension assessments"""
        levels = [assessment.level for assessment in assessments.values()]
        
        # Count levels
        low_count = levels.count(CapacityLevel.LOW)
        medium_count = levels.count(CapacityLevel.MEDIUM)
        high_count = levels.count(CapacityLevel.HIGH)
        
        # Overall is LOW if >3 dimensions are LOW
        if low_count > 3:
            return CapacityLevel.LOW
        # HIGH if >5 dimensions are HIGH or MEDIUM
        elif (high_count + medium_count) > 5:
            return CapacityLevel.HIGH
        else:
            return CapacityLevel.MEDIUM
    
    def _assess_implementation_readiness(
        self,
        assessments: dict[CapacityDimension, CapacityAssessment],
        binding_constraints: list[BindingConstraint]
    ) -> str:
        """Assess overall implementation readiness"""
        if not binding_constraints:
            return "HIGH: Municipality can implement sophisticated policy interventions"
        elif len(binding_constraints) == 1:
            return f"MEDIUM: Address {binding_constraints[0].dimension.value} constraint before complex interventions"
        else:
            return f"LOW: Must sequentially address {len(binding_constraints)} binding constraints"
    
    def _generate_sequencing_recommendations(
        self,
        binding_constraints: list[BindingConstraint]
    ) -> list[str]:
        """Generate sequencing recommendations based on binding constraints"""
        if not binding_constraints:
            return ["Can implement all instrument types immediately"]
        
        sequencing = []
        for i, constraint in enumerate(binding_constraints, 1):
            sequencing.append(
                f"Phase {i}: {', '.join(constraint.mitigation_strategies)}"
            )
        
        sequencing.append(
            f"Phase {len(binding_constraints) + 1}: Implement substantive interventions"
        )
        
        return sequencing


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def capacity_level_from_evidence(evidence: list[str]) -> CapacityLevel:
    """
    Quick utility to determine capacity level from evidence.
    
    Args:
        evidence: List of evidence statements
        
    Returns:
        CapacityLevel
    """
    # Simple heuristic based on keyword presence
    low_keywords = ["no", "lack", "cannot", "weak", "insufficient", "absent"]
    high_keywords = ["strong", "robust", "comprehensive", "advanced", "excellent"]
    
    low_count = sum(
        1 for e in evidence 
        for kw in low_keywords 
        if kw in e.lower()
    )
    
    high_count = sum(
        1 for e in evidence 
        for kw in high_keywords 
        if kw in e.lower()
    )
    
    if low_count > high_count:
        return CapacityLevel.LOW
    elif high_count > low_count:
        return CapacityLevel.HIGH
    else:
        return CapacityLevel.MEDIUM
