# phase8_28_00_howlett_instruments.py - Howlett Policy Instruments Taxonomy
"""
Module: src.farfan_pipeline.phases.Phase_08.phase8_28_00_howlett_instruments
Purpose: Howlett's comprehensive policy instruments taxonomy (NATO framework)
Owner: phase8_enhanced
Stage: 28 (Policy Instruments)
Order: 00
Type: FRAMEWORK
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2026-01-26

═══════════════════════════════════════════════════════════════════════════════════
    🛠️ HOWLETT POLICY INSTRUMENTS - NATO Taxonomy 🛠️
═══════════════════════════════════════════════════════════════════════════════════

THEORETICAL FOUNDATION:
    Howlett's policy instruments taxonomy provides systematic classification of
    tools available to governments for achieving policy objectives.
    
    NATO FRAMEWORK (Nodality-Authority-Treasure-Organization):
    - INFORMATION (Nodality): Information-based tools
    - AUTHORITY: Legal/regulatory tools
    - TREASURE: Financial/economic tools
    - ORGANIZATION: Organizational/structural tools

COLOMBIAN MUNICIPAL CONTEXT:
    - Municipal category constraints (1-6)
    - SGP allocation rules and sectoral earmarks
    - Legal competency boundaries
    - Fiscal capacity limitations
    - Inter-governmental coordination requirements

KEY FEATURES:
    1. Comprehensive instrument catalog
    2. Capacity requirement mapping
    3. Colombian legal framework integration
    4. Instrument mix generation
    5. Sequencing recommendations

INTEGRATION:
    - Uses capacity assessments from phase8_27
    - Feeds value chain integration (phase8_29)
    - Informs resource allocation (phase8_30)

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
__stage__ = 28
__order__ = 0
__author__ = "F.A.R.F.A.N Architecture Team"
__created__ = "2026-01-26"
__modified__ = "2026-01-26"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"
__codename__ = "HOWLETT-INSTRUMENTS"

# =============================================================================
# IMPORTS
# =============================================================================

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .phase8_27_00_policy_capacity_framework import (
    CapacityDimension,
    CapacityLevel,
    ComprehensiveCapacityProfile,
)

logger = logging.getLogger(__name__)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    "InstrumentType",
    "InstrumentCategory",
    "PolicyInstrument",
    "InstrumentMix",
    "InstrumentSelectionEngine",
    "SequencingPhase",
]

# =============================================================================
# ENUMERATIONS
# =============================================================================


class InstrumentCategory(str, Enum):
    """NATO framework categories"""
    INFORMATION = "INFORMATION"  # Nodality-based
    AUTHORITY = "AUTHORITY"  # Command & control
    TREASURE = "TREASURE"  # Financial/economic
    ORGANIZATION = "ORGANIZATION"  # Structural/procedural


class InstrumentType(str, Enum):
    """Specific instrument types within categories"""
    # Information instruments
    PUBLIC_INFORMATION_CAMPAIGN = "PUBLIC_INFORMATION_CAMPAIGN"
    EXHORTATION = "EXHORTATION"
    TRAINING_EDUCATION = "TRAINING_EDUCATION"
    LABELING_CERTIFICATION = "LABELING_CERTIFICATION"
    
    # Authority instruments
    REGULATION = "REGULATION"
    SELF_REGULATION = "SELF_REGULATION"
    LICENSING_PERMITS = "LICENSING_PERMITS"
    STANDARDS = "STANDARDS"
    
    # Treasure instruments
    SUBSIDIES_GRANTS = "SUBSIDIES_GRANTS"
    TAX_EXPENDITURES = "TAX_EXPENDITURES"
    VOUCHERS = "VOUCHERS"
    USER_CHARGES = "USER_CHARGES"
    PROCUREMENT_PREFERENCES = "PROCUREMENT_PREFERENCES"
    
    # Organization instruments
    DIRECT_PROVISION = "DIRECT_PROVISION"
    PUBLIC_ENTERPRISE = "PUBLIC_ENTERPRISE"
    GOVERNMENT_REORGANIZATION = "GOVERNMENT_REORGANIZATION"
    CO_PRODUCTION = "CO_PRODUCTION"
    ADVISORY_COMMITTEES = "ADVISORY_COMMITTEES"


class SequencingPhase(str, Enum):
    """Implementation phases for instrument sequencing"""
    QUICK_WINS = "QUICK_WINS"  # Months 1-6
    CAPACITY_BUILDING = "CAPACITY_BUILDING"  # Months 7-18
    SUBSTANTIVE_INTERVENTIONS = "SUBSTANTIVE_INTERVENTIONS"  # Months 19-48


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class PolicyInstrument:
    """Detailed policy instrument specification"""
    instrument_type: InstrumentType
    category: InstrumentCategory
    description: str
    
    # Capacity requirements
    required_analytical: CapacityLevel
    required_operational: CapacityLevel
    required_political: CapacityLevel
    
    # Colombian legal framework
    legal_framework: str
    municipal_competency: str
    category_constraints: list[int]  # Which municipal categories can use this
    
    # Implementation characteristics
    implementation_complexity: str  # LOW, MEDIUM, HIGH
    time_to_results: str  # SHORT (0-6mo), MEDIUM (6-18mo), LONG (18-48mo)
    recurrent_cost: str  # LOW, MEDIUM, HIGH
    enforcement_demands: str  # NONE, LOW, MEDIUM, HIGH
    
    # Colombian context
    sgp_compatibility: str  # Which SGP components can fund this
    departmental_support_available: bool
    national_program_linkage: str | None
    
    # Examples
    colombian_examples: list[str]
    
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class InstrumentMix:
    """Combination of instruments for a specific objective"""
    objective: str  # Objetivo Específico being addressed
    problem: str  # Problem being solved
    
    # Selected instruments
    primary_instrument: PolicyInstrument
    supporting_instruments: list[PolicyInstrument]
    enabling_instruments: list[PolicyInstrument]
    
    # Capacity calibration
    capacity_fit_rationale: str
    capacity_gaps_addressed: list[str]
    
    # Sequencing
    sequencing_phase: SequencingPhase
    sequencing_rationale: str
    dependencies: list[str]
    
    # Resource implications
    total_complexity: str
    estimated_budget_range: str
    timeline_months: int
    
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# INSTRUMENT CATALOG
# =============================================================================


class InstrumentCatalog:
    """Comprehensive catalog of policy instruments"""
    
    @staticmethod
    def get_all_instruments() -> dict[InstrumentType, PolicyInstrument]:
        """Get complete instrument catalog"""
        return {
            # INFORMATION INSTRUMENTS
            InstrumentType.PUBLIC_INFORMATION_CAMPAIGN: PolicyInstrument(
                instrument_type=InstrumentType.PUBLIC_INFORMATION_CAMPAIGN,
                category=InstrumentCategory.INFORMATION,
                description="Government disseminates information to change behavior",
                required_analytical=CapacityLevel.LOW,
                required_operational=CapacityLevel.MEDIUM,
                required_political=CapacityLevel.LOW,
                legal_framework="Municipal communication authority, Ley 1712/2014 (Transparency)",
                municipal_competency="All municipalities",
                category_constraints=[1, 2, 3, 4, 5, 6],
                implementation_complexity="LOW",
                time_to_results="SHORT",
                recurrent_cost="LOW",
                enforcement_demands="NONE",
                sgp_compatibility="General purpose (42% discretionary)",
                departmental_support_available=True,
                national_program_linkage="Ministry communications support available",
                colombian_examples=[
                    "Gender violence prevention awareness campaign",
                    "Water conservation public education",
                    "COVID-19 vaccination information campaign"
                ]
            ),
            
            InstrumentType.TRAINING_EDUCATION: PolicyInstrument(
                instrument_type=InstrumentType.TRAINING_EDUCATION,
                category=InstrumentCategory.INFORMATION,
                description="Government provides skill-building opportunities",
                required_analytical=CapacityLevel.MEDIUM,
                required_operational=CapacityLevel.MEDIUM,
                required_political=CapacityLevel.LOW,
                legal_framework="Municipal education competence (non-certified municipalities)",
                municipal_competency="All municipalities",
                category_constraints=[1, 2, 3, 4, 5, 6],
                implementation_complexity="MEDIUM",
                time_to_results="MEDIUM",
                recurrent_cost="MEDIUM",
                enforcement_demands="NONE",
                sgp_compatibility="General purpose + education sector (for specific training)",
                departmental_support_available=True,
                national_program_linkage="SENA (national training service) partnerships",
                colombian_examples=[
                    "Training workshops for community mothers on child nutrition",
                    "Digital literacy for rural teachers",
                    "Entrepreneurship training for youth"
                ]
            ),
            
            # AUTHORITY INSTRUMENTS
            InstrumentType.REGULATION: PolicyInstrument(
                instrument_type=InstrumentType.REGULATION,
                category=InstrumentCategory.AUTHORITY,
                description="Legal rules requiring/prohibiting specific behaviors",
                required_analytical=CapacityLevel.MEDIUM,
                required_operational=CapacityLevel.HIGH,
                required_political=CapacityLevel.MEDIUM,
                legal_framework="Municipal Councils issue Acuerdos under Ley 136/1994",
                municipal_competency="Limited to matters not reserved to national/departmental law",
                category_constraints=[1, 2, 3, 4, 5, 6],
                implementation_complexity="HIGH",
                time_to_results="LONG",
                recurrent_cost="HIGH",
                enforcement_demands="HIGH",
                sgp_compatibility="General purpose for enforcement capacity",
                departmental_support_available=False,
                national_program_linkage=None,
                colombian_examples=[
                    "Acuerdo Municipal requiring construction waste management plans",
                    "Ordinance prohibiting plastic bags in municipal markets",
                    "Regulation of noise levels in commercial zones"
                ]
            ),
            
            InstrumentType.LICENSING_PERMITS: PolicyInstrument(
                instrument_type=InstrumentType.LICENSING_PERMITS,
                category=InstrumentCategory.AUTHORITY,
                description="Government grants permission to engage in activities",
                required_analytical=CapacityLevel.MEDIUM,
                required_operational=CapacityLevel.HIGH,
                required_political=CapacityLevel.MEDIUM,
                legal_framework="Various sectoral laws delegate permitting authority",
                municipal_competency="Specific sectors only (construction, liquor, some commerce)",
                category_constraints=[1, 2, 3, 4, 5, 6],
                implementation_complexity="MEDIUM",
                time_to_results="MEDIUM",
                recurrent_cost="MEDIUM",
                enforcement_demands="MEDIUM",
                sgp_compatibility="User fees can cover administrative costs",
                departmental_support_available=True,
                national_program_linkage="DIAN coordination for some permits",
                colombian_examples=[
                    "Liquor sales permits",
                    "Construction permits",
                    "Small-scale mining permits (where applicable)"
                ]
            ),
            
            # TREASURE INSTRUMENTS
            InstrumentType.SUBSIDIES_GRANTS: PolicyInstrument(
                instrument_type=InstrumentType.SUBSIDIES_GRANTS,
                category=InstrumentCategory.TREASURE,
                description="Government provides direct financial support",
                required_analytical=CapacityLevel.MEDIUM,
                required_operational=CapacityLevel.MEDIUM,
                required_political=CapacityLevel.MEDIUM,
                legal_framework="SGP allocation rules, municipal budget autonomy within limits",
                municipal_competency="All municipalities",
                category_constraints=[1, 2, 3, 4, 5, 6],
                implementation_complexity="MEDIUM",
                time_to_results="SHORT",
                recurrent_cost="HIGH",
                enforcement_demands="LOW",
                sgp_compatibility="General purpose (42% discretionary) + sector-specific",
                departmental_support_available=True,
                national_program_linkage="Co-financing opportunities with national programs",
                colombian_examples=[
                    "Subsidies for low-income families to connect to aqueduct",
                    "Agricultural input subsidies for small farmers",
                    "Housing improvement subsidies"
                ]
            ),
            
            InstrumentType.VOUCHERS: PolicyInstrument(
                instrument_type=InstrumentType.VOUCHERS,
                category=InstrumentCategory.TREASURE,
                description="Government provides purchasing power for specific services",
                required_analytical=CapacityLevel.MEDIUM,
                required_operational=CapacityLevel.HIGH,
                required_political=CapacityLevel.LOW,
                legal_framework="Requires enabling Acuerdo Municipal",
                municipal_competency="All municipalities",
                category_constraints=[1, 2, 3, 4, 5, 6],
                implementation_complexity="MEDIUM",
                time_to_results="SHORT",
                recurrent_cost="HIGH",
                enforcement_demands="MEDIUM",
                sgp_compatibility="General purpose (42% discretionary)",
                departmental_support_available=False,
                national_program_linkage="Familias en Acción voucher model as reference",
                colombian_examples=[
                    "Childcare vouchers for working mothers",
                    "Transportation vouchers for women seeking legal services",
                    "Internet vouchers for rural students"
                ]
            ),
            
            # ORGANIZATION INSTRUMENTS
            InstrumentType.DIRECT_PROVISION: PolicyInstrument(
                instrument_type=InstrumentType.DIRECT_PROVISION,
                category=InstrumentCategory.ORGANIZATION,
                description="Government directly produces/delivers goods and services",
                required_analytical=CapacityLevel.MEDIUM,
                required_operational=CapacityLevel.HIGH,
                required_political=CapacityLevel.MEDIUM,
                legal_framework="Municipal service competencies (water, local roads, health, education per Ley 715)",
                municipal_competency="Specific services only",
                category_constraints=[1, 2, 3, 4, 5, 6],
                implementation_complexity="HIGH",
                time_to_results="LONG",
                recurrent_cost="HIGH",
                enforcement_demands="NONE",
                sgp_compatibility="Sector-specific SGP allocations",
                departmental_support_available=False,
                national_program_linkage="Technical assistance from sector ministries",
                colombian_examples=[
                    "Municipal government operates mobile health units",
                    "Direct municipal water service provision",
                    "Municipal library system"
                ]
            ),
            
            InstrumentType.CO_PRODUCTION: PolicyInstrument(
                instrument_type=InstrumentType.CO_PRODUCTION,
                category=InstrumentCategory.ORGANIZATION,
                description="Government and citizens jointly deliver services",
                required_analytical=CapacityLevel.LOW,
                required_operational=CapacityLevel.MEDIUM,
                required_political=CapacityLevel.HIGH,
                legal_framework="Community action boards (JAC) legal framework, Ley 1757/2015",
                municipal_competency="All municipalities",
                category_constraints=[1, 2, 3, 4, 5, 6],
                implementation_complexity="MEDIUM",
                time_to_results="MEDIUM",
                recurrent_cost="LOW",
                enforcement_demands="LOW",
                sgp_compatibility="General purpose + sector allocations",
                departmental_support_available=True,
                national_program_linkage="Acción Comunal national framework",
                colombian_examples=[
                    "Community-municipal co-management of neighborhood parks",
                    "Shared maintenance of rural roads (municipality + JAC)",
                    "Co-production of community security programs"
                ]
            ),
            
            InstrumentType.ADVISORY_COMMITTEES: PolicyInstrument(
                instrument_type=InstrumentType.ADVISORY_COMMITTEES,
                category=InstrumentCategory.ORGANIZATION,
                description="Procedural: Structured stakeholder input mechanisms",
                required_analytical=CapacityLevel.LOW,
                required_operational=CapacityLevel.MEDIUM,
                required_political=CapacityLevel.MEDIUM,
                legal_framework="Ley 1757/2015 participatory mechanisms",
                municipal_competency="All municipalities, some committees mandatory",
                category_constraints=[1, 2, 3, 4, 5, 6],
                implementation_complexity="LOW",
                time_to_results="SHORT",
                recurrent_cost="LOW",
                enforcement_demands="NONE",
                sgp_compatibility="Minimal budget needs, covered by general operations",
                departmental_support_available=True,
                national_program_linkage="National Council frameworks as models",
                colombian_examples=[
                    "Municipal Council for Women's Rights (advisory to mayor)",
                    "Youth Advisory Council",
                    "Environmental Advisory Committee"
                ]
            ),
        }


# =============================================================================
# INSTRUMENT SELECTION ENGINE
# =============================================================================


class InstrumentSelectionEngine:
    """
    Selects appropriate policy instruments based on:
    - Problem characteristics
    - Capacity profile
    - Colombian legal constraints
    - Resource availability
    """
    
    def __init__(self):
        """Initialize instrument selection engine"""
        self.catalog = InstrumentCatalog.get_all_instruments()
        logger.info(f"Instrument Selection Engine initialized with {len(self.catalog)} instruments")
    
    def select_instrument_mix(
        self,
        objective: str,
        problem: str,
        capacity_profile: ComprehensiveCapacityProfile,
        municipality_category: int,
        policy_area: str,
        dimension: str
    ) -> InstrumentMix:
        """
        Select appropriate instrument mix for an objective.
        
        Args:
            objective: Objetivo Específico to achieve
            problem: Problem being addressed
            capacity_profile: Municipality's capacity profile
            municipality_category: Municipal category (1-6)
            policy_area: Policy area (e.g., Gender Equality)
            dimension: Dimension (e.g., DIM01)
            
        Returns:
            InstrumentMix object
        """
        # Filter instruments by capacity and category
        feasible_instruments = self._filter_feasible_instruments(
            capacity_profile, municipality_category
        )
        
        # Score instruments by appropriateness for this problem
        scored_instruments = self._score_instruments_for_problem(
            feasible_instruments, problem, policy_area
        )
        
        # Select primary instrument (highest score)
        primary = scored_instruments[0] if scored_instruments else None
        
        # Select supporting instruments (complementary)
        supporting = self._select_supporting_instruments(
            primary, scored_instruments, capacity_profile
        )
        
        # Select enabling instruments (address capacity gaps)
        enabling = self._select_enabling_instruments(
            capacity_profile.binding_constraints
        )
        
        # Determine sequencing phase
        sequencing_phase = self._determine_sequencing_phase(
            primary, capacity_profile
        )
        
        # Calculate complexity and budget
        total_complexity = self._calculate_total_complexity(
            primary, supporting, enabling
        )
        estimated_budget = self._estimate_budget_range(
            primary, supporting, enabling
        )
        
        return InstrumentMix(
            objective=objective,
            problem=problem,
            primary_instrument=primary,
            supporting_instruments=supporting,
            enabling_instruments=enabling,
            capacity_fit_rationale=self._generate_capacity_rationale(
                primary, capacity_profile
            ),
            capacity_gaps_addressed=[
                c.dimension.value for c in capacity_profile.binding_constraints
            ],
            sequencing_phase=sequencing_phase,
            sequencing_rationale=self._generate_sequencing_rationale(
                sequencing_phase, primary, capacity_profile
            ),
            dependencies=self._identify_dependencies(
                primary, supporting, enabling
            ),
            total_complexity=total_complexity,
            estimated_budget_range=estimated_budget,
            timeline_months=self._calculate_timeline(
                primary, supporting, enabling
            ),
            metadata={
                "municipality_category": municipality_category,
                "policy_area": policy_area,
                "dimension": dimension
            }
        )
    
    def _filter_feasible_instruments(
        self,
        capacity_profile: ComprehensiveCapacityProfile,
        municipality_category: int
    ) -> list[PolicyInstrument]:
        """Filter instruments by capacity and category constraints"""
        feasible = []
        
        for instrument in self.catalog.values():
            # Check category constraints
            if municipality_category not in instrument.category_constraints:
                continue
            
            # Check capacity requirements (use organizational level as proxy)
            if (instrument.required_operational == CapacityLevel.HIGH and
                capacity_profile.organizational_operational.level == CapacityLevel.LOW):
                continue
            
            if (instrument.required_analytical == CapacityLevel.HIGH and
                capacity_profile.organizational_analytical.level == CapacityLevel.LOW):
                continue
            
            if (instrument.required_political == CapacityLevel.HIGH and
                capacity_profile.organizational_political.level == CapacityLevel.LOW):
                continue
            
            feasible.append(instrument)
        
        return feasible
    
    def _score_instruments_for_problem(
        self,
        instruments: list[PolicyInstrument],
        problem: str,
        policy_area: str
    ) -> list[PolicyInstrument]:
        """Score instruments by appropriateness for problem"""
        # Simple scoring based on keywords (can be enhanced)
        scored = []
        
        problem_lower = problem.lower()
        
        for instrument in instruments:
            score = 0
            
            # Information instruments good for awareness problems
            if "awareness" in problem_lower or "knowledge" in problem_lower:
                if instrument.category == InstrumentCategory.INFORMATION:
                    score += 3
            
            # Treasure instruments good for access problems
            if "access" in problem_lower or "afford" in problem_lower:
                if instrument.category == InstrumentCategory.TREASURE:
                    score += 3
            
            # Authority instruments good for compliance problems
            if "compliance" in problem_lower or "violation" in problem_lower:
                if instrument.category == InstrumentCategory.AUTHORITY:
                    score += 3
            
            # Organization instruments good for service delivery problems
            if "service" in problem_lower or "delivery" in problem_lower:
                if instrument.category == InstrumentCategory.ORGANIZATION:
                    score += 3
            
            # Prefer low complexity for resource-constrained contexts
            if instrument.implementation_complexity == "LOW":
                score += 2
            elif instrument.implementation_complexity == "HIGH":
                score -= 1
            
            scored.append((score, instrument))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return [inst for _, inst in scored]
    
    def _select_supporting_instruments(
        self,
        primary: PolicyInstrument,
        all_instruments: list[PolicyInstrument],
        capacity_profile: ComprehensiveCapacityProfile
    ) -> list[PolicyInstrument]:
        """Select supporting instruments that complement primary"""
        if not primary:
            return []
        
        supporting = []
        
        # Select up to 2 instruments from different categories
        seen_categories = {primary.category}
        
        for instrument in all_instruments[1:]:  # Skip primary
            if len(supporting) >= 2:
                break
            
            if instrument.category not in seen_categories:
                supporting.append(instrument)
                seen_categories.add(instrument.category)
        
        return supporting
    
    def _select_enabling_instruments(
        self,
        binding_constraints: list
    ) -> list[PolicyInstrument]:
        """Select instruments that address binding constraints"""
        enabling = []
        
        # If organizational political capacity is low, add advisory committee
        if any(c.dimension == CapacityDimension.ORGANIZATIONAL_POLITICAL 
               for c in binding_constraints):
            if InstrumentType.ADVISORY_COMMITTEES in self.catalog:
                enabling.append(self.catalog[InstrumentType.ADVISORY_COMMITTEES])
        
        # If operational capacity is low, suggest co-production
        if any(c.dimension == CapacityDimension.ORGANIZATIONAL_OPERATIONAL 
               for c in binding_constraints):
            if InstrumentType.CO_PRODUCTION in self.catalog:
                enabling.append(self.catalog[InstrumentType.CO_PRODUCTION])
        
        return enabling
    
    def _determine_sequencing_phase(
        self,
        primary: PolicyInstrument,
        capacity_profile: ComprehensiveCapacityProfile
    ) -> SequencingPhase:
        """Determine implementation phase for this instrument"""
        if not primary:
            return SequencingPhase.QUICK_WINS
        
        # Quick wins: Low complexity, information/procedural instruments
        if (primary.implementation_complexity == "LOW" or
            primary.category in [InstrumentCategory.INFORMATION, 
                               InstrumentCategory.ORGANIZATION]):
            if primary.instrument_type == InstrumentType.ADVISORY_COMMITTEES:
                return SequencingPhase.QUICK_WINS
        
        # Capacity building: Training, moderate instruments
        if (primary.instrument_type == InstrumentType.TRAINING_EDUCATION or
            primary.implementation_complexity == "MEDIUM"):
            return SequencingPhase.CAPACITY_BUILDING
        
        # Substantive: High complexity, treasure/authority instruments
        return SequencingPhase.SUBSTANTIVE_INTERVENTIONS
    
    def _generate_capacity_rationale(
        self,
        primary: PolicyInstrument,
        capacity_profile: ComprehensiveCapacityProfile
    ) -> str:
        """Generate rationale for instrument fit with capacity"""
        if not primary:
            return "No suitable instrument found"
        
        return (
            f"{primary.instrument_type.value} selected because it requires "
            f"{primary.required_operational.value} operational capacity "
            f"(municipality has {capacity_profile.organizational_operational.level.value}), "
            f"{primary.required_analytical.value} analytical capacity "
            f"(municipality has {capacity_profile.organizational_analytical.level.value}), "
            f"and {primary.required_political.value} political capacity "
            f"(municipality has {capacity_profile.organizational_political.level.value})"
        )
    
    def _generate_sequencing_rationale(
        self,
        phase: SequencingPhase,
        primary: PolicyInstrument,
        capacity_profile: ComprehensiveCapacityProfile
    ) -> str:
        """Generate rationale for sequencing phase"""
        if phase == SequencingPhase.QUICK_WINS:
            return "Low complexity intervention suitable for immediate implementation"
        elif phase == SequencingPhase.CAPACITY_BUILDING:
            return "Moderate complexity requiring some capacity building before full implementation"
        else:
            return f"High complexity intervention requiring {len(capacity_profile.binding_constraints)} binding constraints to be addressed first"
    
    def _identify_dependencies(
        self,
        primary: PolicyInstrument,
        supporting: list[PolicyInstrument],
        enabling: list[PolicyInstrument]
    ) -> list[str]:
        """Identify dependencies between instruments"""
        dependencies = []
        
        if enabling:
            dependencies.append(
                f"Enabling instruments ({', '.join(e.instrument_type.value for e in enabling)}) "
                "must be implemented before primary"
            )
        
        return dependencies
    
    def _calculate_total_complexity(
        self,
        primary: PolicyInstrument,
        supporting: list[PolicyInstrument],
        enabling: list[PolicyInstrument]
    ) -> str:
        """Calculate total implementation complexity"""
        if not primary:
            return "N/A"
        
        complexities = [primary.implementation_complexity]
        complexities.extend(s.implementation_complexity for s in supporting)
        complexities.extend(e.implementation_complexity for e in enabling)
        
        if "HIGH" in complexities:
            return "HIGH"
        elif "MEDIUM" in complexities:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_budget_range(
        self,
        primary: PolicyInstrument,
        supporting: list[PolicyInstrument],
        enabling: list[PolicyInstrument]
    ) -> str:
        """Estimate budget range for instrument mix"""
        if not primary:
            return "N/A"
        
        # Simple heuristic based on recurrent cost
        costs = [primary.recurrent_cost]
        costs.extend(s.recurrent_cost for s in supporting)
        costs.extend(e.recurrent_cost for e in enabling)
        
        high_count = costs.count("HIGH")
        medium_count = costs.count("MEDIUM")
        
        if high_count >= 2:
            return "COP 100M-200M/year"
        elif high_count == 1 or medium_count >= 2:
            return "COP 50M-100M/year"
        else:
            return "COP 20M-50M/year"
    
    def _calculate_timeline(
        self,
        primary: PolicyInstrument,
        supporting: list[PolicyInstrument],
        enabling: list[PolicyInstrument]
    ) -> int:
        """Calculate implementation timeline in months"""
        if not primary:
            return 0
        
        # Map time_to_results to months
        time_map = {"SHORT": 6, "MEDIUM": 18, "LONG": 48}
        
        primary_months = time_map.get(primary.time_to_results, 12)
        
        # Add time for enabling instruments
        if enabling:
            primary_months += 6  # 6 months for enabling phase
        
        return primary_months
