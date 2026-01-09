"""
PDET Municipality Context Validator

Integrates PDET municipality context (170 municipalities, 16 subregions) 
with validation templates to ensure contextual accuracy for PDET territories.

Validates against:
- Gate 1: Consumer scope authorization for PDET context
- Gate 2: Value contribution of PDET enrichment
- Gate 3: Consumer capability/readiness for PDET data
- Gate 4: Channel integrity for PDET data flows
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PDETValidationContext:
    """Context information for PDET validation."""
    
    municipality_code: Optional[str] = None
    municipality_name: Optional[str] = None
    subregion_id: Optional[str] = None
    subregion_name: Optional[str] = None
    is_pdet: bool = False
    category: Optional[str] = None
    population: Optional[int] = None
    multidimensional_poverty_rate: Optional[float] = None
    fiscal_autonomy: Optional[str] = None
    ethnic_composition: List[str] = field(default_factory=list)
    key_pdet_pillars: List[str] = field(default_factory=list)
    patr_initiatives: Optional[int] = None
    active_route_initiatives: Optional[int] = None
    ocad_paz_projects: Optional[int] = None
    ocad_paz_investment_cop_millions: Optional[float] = None
    policy_area_relevance: List[str] = field(default_factory=list)


@dataclass
class PDETValidationResult:
    """Result of PDET-specific validation."""
    
    validation_type: str
    dimension: str
    passed: bool
    municipality_code: Optional[str] = None
    pdet_specific_checks: Dict[str, bool] = field(default_factory=dict)
    messages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    gates_validated: List[str] = field(default_factory=list)


class PDETValidator:
    """
    Validator for PDET municipality context integration.
    
    Loads PDET municipality data and validation templates to perform
    context-aware validations for PDET territories.
    """
    
    def __init__(
        self,
        pdet_data_path: Optional[Path] = None,
        templates_path: Optional[Path] = None
    ):
        """
        Initialize PDET validator.
        
        Args:
            pdet_data_path: Path to pdet_municipalities.json
            templates_path: Path to validation_templates.json
        """
        self._pdet_data: Dict[str, Any] = {}
        self._validation_templates: Dict[str, Any] = {}
        self._municipality_index: Dict[str, Dict[str, Any]] = {}
        self._subregion_index: Dict[str, Dict[str, Any]] = {}
        
        # Default paths
        if pdet_data_path is None:
            pdet_data_path = (
                Path(__file__).parent.parent / 
                "colombia_context" / 
                "pdet_municipalities.json"
            )
        
        if templates_path is None:
            templates_path = Path(__file__).parent / "validation_templates.json"
        
        self._load_pdet_data(pdet_data_path)
        self._load_validation_templates(templates_path)
        self._build_indexes()
    
    def _load_pdet_data(self, path: Path) -> None:
        """Load PDET municipality data."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._pdet_data = json.load(f)
            logger.info(f"Loaded PDET data: {self._pdet_data.get('overview', {}).get('total_municipalities', 0)} municipalities")
        except Exception as e:
            logger.error(f"Failed to load PDET data from {path}: {e}")
            self._pdet_data = {}
    
    def _load_validation_templates(self, path: Path) -> None:
        """Load validation templates with PDET enrichment."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._validation_templates = json.load(f)
            logger.info(f"Loaded validation templates version {self._validation_templates.get('version', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to load validation templates from {path}: {e}")
            self._validation_templates = {}
    
    def _build_indexes(self) -> None:
        """Build municipality and subregion indexes for fast lookup."""
        subregions = self._pdet_data.get("subregions", [])
        
        for subregion in subregions:
            subregion_id = subregion.get("subregion_id")
            if subregion_id:
                self._subregion_index[subregion_id] = subregion
            
            for municipality in subregion.get("municipalities", []):
                mun_code = municipality.get("municipality_code")
                if mun_code:
                    # Add subregion context to municipality
                    municipality["_subregion_id"] = subregion_id
                    municipality["_subregion_name"] = subregion.get("name")
                    self._municipality_index[mun_code] = municipality
        
        logger.info(f"Indexed {len(self._municipality_index)} municipalities across {len(self._subregion_index)} subregions")
    
    def is_pdet_municipality(self, municipality_code: str) -> bool:
        """Check if a municipality code belongs to PDET."""
        return municipality_code in self._municipality_index
    
    def get_pdet_context(self, municipality_code: str) -> Optional[PDETValidationContext]:
        """
        Get PDET context for a municipality.
        
        Args:
            municipality_code: DANE municipality code (e.g., "19355")
        
        Returns:
            PDETValidationContext if municipality is PDET, None otherwise
        """
        if municipality_code not in self._municipality_index:
            return None
        
        mun_data = self._municipality_index[municipality_code]
        
        return PDETValidationContext(
            municipality_code=municipality_code,
            municipality_name=mun_data.get("name"),
            subregion_id=mun_data.get("_subregion_id"),
            subregion_name=mun_data.get("_subregion_name"),
            is_pdet=True,
            category=mun_data.get("category"),
            population=mun_data.get("population"),
            multidimensional_poverty_rate=mun_data.get("multidimensional_poverty_rate"),
            fiscal_autonomy=mun_data.get("fiscal_autonomy"),
            ethnic_composition=mun_data.get("ethnic_composition", []),
            key_pdet_pillars=mun_data.get("key_pdet_pillars", []),
            patr_initiatives=mun_data.get("patr_initiatives"),
            active_route_initiatives=mun_data.get("active_route_initiatives"),
            ocad_paz_projects=mun_data.get("ocad_paz_projects"),
            ocad_paz_investment_cop_millions=mun_data.get("ocad_paz_investment_cop_millions"),
            policy_area_relevance=[]  # Will be filled from subregion data
        )
    
    def get_pdet_validations_for_dimension(self, dimension: str) -> List[Dict[str, Any]]:
        """
        Get PDET-specific validation rules for a dimension.
        
        Args:
            dimension: Dimension code (e.g., "DIM01_INSUMOS")
        
        Returns:
            List of PDET-specific validation rules
        """
        templates = self._validation_templates.get("templates", {})
        dimension_templates = templates.get(dimension, [])
        
        # Filter for PDET-specific validations
        pdet_validations = [
            v for v in dimension_templates 
            if v.get("pdet_specific", False)
        ]
        
        return pdet_validations
    
    def validate_pdet_context(
        self,
        dimension: str,
        municipality_code: str,
        validation_data: Dict[str, Any]
    ) -> List[PDETValidationResult]:
        """
        Validate using PDET-specific rules for a dimension.
        
        Args:
            dimension: Dimension code (e.g., "DIM01_INSUMOS")
            municipality_code: DANE municipality code
            validation_data: Data to validate
        
        Returns:
            List of PDETValidationResult objects
        """
        results = []
        
        # Get PDET context
        pdet_context = self.get_pdet_context(municipality_code)
        
        if not pdet_context:
            # Not a PDET municipality - no PDET-specific validations needed
            return results
        
        # Get PDET-specific validation rules for this dimension
        pdet_validations = self.get_pdet_validations_for_dimension(dimension)
        
        for validation_rule in pdet_validations:
            result = self._apply_pdet_validation(
                validation_rule,
                dimension,
                pdet_context,
                validation_data
            )
            results.append(result)
        
        return results
    
    def _apply_pdet_validation(
        self,
        validation_rule: Dict[str, Any],
        dimension: str,
        pdet_context: PDETValidationContext,
        validation_data: Dict[str, Any]
    ) -> PDETValidationResult:
        """Apply a single PDET validation rule."""
        
        validation_type = validation_rule.get("type", "unknown")
        gates = validation_rule.get("validation_gates", [])
        
        result = PDETValidationResult(
            validation_type=validation_type,
            dimension=dimension,
            passed=True,  # Will be updated based on checks
            municipality_code=pdet_context.municipality_code,
            gates_validated=gates
        )
        
        # Perform validation based on type
        if validation_type == "pdet_municipality_context":
            self._validate_municipality_context(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_resource_mapping":
            self._validate_resource_mapping(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_pillar_alignment":
            self._validate_pillar_alignment(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_patr_coordination":
            self._validate_patr_coordination(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_resource_allocation":
            self._validate_resource_allocation(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_capability_requirements":
            self._validate_capability_requirements(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_territorial_targeting":
            self._validate_territorial_targeting(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_delivery_realism":
            self._validate_delivery_realism(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_monitoring_systems":
            self._validate_monitoring_systems(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_outcome_indicators":
            self._validate_outcome_indicators(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_baseline_context":
            self._validate_baseline_context(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_comparative_benchmarking":
            self._validate_comparative_benchmarking(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_peace_accord_alignment":
            self._validate_peace_accord_alignment(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_structural_transformation":
            self._validate_structural_transformation(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_long_term_sustainability":
            self._validate_long_term_sustainability(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_conflict_sensitive_causality":
            self._validate_conflict_sensitive_causality(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_territorial_causality":
            self._validate_territorial_causality(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_evidence_base":
            self._validate_evidence_base(validation_rule, pdet_context, validation_data, result)
        elif validation_type == "pdet_systemic_approach":
            self._validate_systemic_approach(validation_rule, pdet_context, validation_data, result)
        else:
            result.messages.append(f"Unknown PDET validation type: {validation_type}")
            result.passed = False
        
        return result
    
    # Placeholder validation methods - these would contain actual validation logic
    
    def _validate_municipality_context(self, rule, context, data, result):
        """Validate municipality context (DIM01)."""
        result.recommendations.append(
            f"Municipality {context.municipality_name} is PDET (subregion: {context.subregion_name}). "
            f"Ensure diagnostic cites PATR initiatives ({context.patr_initiatives} initiatives) "
            f"and acknowledges conflict-affected status."
        )
        if context.ethnic_composition:
            result.recommendations.append(
                f"Include ethnic population disaggregation for: {', '.join(context.ethnic_composition)}"
            )
    
    def _validate_resource_mapping(self, rule, context, data, result):
        """Validate resource mapping (DIM01)."""
        if context.ocad_paz_projects:
            result.recommendations.append(
                f"Reference OCAD Paz projects ({context.ocad_paz_projects} projects, "
                f"{context.ocad_paz_investment_cop_millions}M COP investment)"
            )
    
    def _validate_pillar_alignment(self, rule, context, data, result):
        """Validate PDET pillar alignment (DIM01)."""
        if context.key_pdet_pillars:
            result.recommendations.append(
                f"Align with key PDET pillars for this municipality: {', '.join(context.key_pdet_pillars)}"
            )
            min_pillars = rule.get("min_pillar_alignment", 2)
            if len(context.key_pdet_pillars) < min_pillars:
                result.warnings.append(
                    f"Municipality has {len(context.key_pdet_pillars)} key pillars, "
                    f"minimum {min_pillars} recommended"
                )
    
    def _validate_patr_coordination(self, rule, context, data, result):
        """Validate PATR coordination (DIM02)."""
        if context.patr_initiatives:
            result.recommendations.append(
                f"Coordinate with {context.patr_initiatives} PATR initiatives in this municipality. "
                f"Reference specific PATR initiative codes."
            )
    
    def _validate_resource_allocation(self, rule, context, data, result):
        """Validate resource allocation (DIM02)."""
        if context.fiscal_autonomy == "Muy baja":
            result.warnings.append(
                f"Municipality has very low fiscal autonomy (category {context.category}). "
                f"Major investments require OCAD Paz or national support."
            )
    
    def _validate_capability_requirements(self, rule, context, data, result):
        """Validate capability requirements (DIM02)."""
        if context.fiscal_autonomy in ["Muy baja", "Baja"]:
            result.recommendations.append(
                "Include technical assistance provisions given low institutional capacity. "
                "Consider ART, DNP, or sector ministry support."
            )
    
    def _validate_territorial_targeting(self, rule, context, data, result):
        """Validate territorial targeting (DIM03)."""
        result.recommendations.append(
            "Specify target veredas for products. Consider 24% rural population concentration "
            "and ethnic community targeting where applicable."
        )
    
    def _validate_delivery_realism(self, rule, context, data, result):
        """Validate delivery realism (DIM03)."""
        result.warnings.append(
            "Account for: (1) security considerations in post-conflict zones, "
            "(2) limited infrastructure access, (3) dispersed rural population"
        )
    
    def _validate_monitoring_systems(self, rule, context, data, result):
        """Validate monitoring systems (DIM03)."""
        result.recommendations.append(
            "Integrate with Central de Información PDET monitoring and OCAD Paz reporting protocols"
        )
    
    def _validate_outcome_indicators(self, rule, context, data, result):
        """Validate outcome indicators (DIM04)."""
        result.recommendations.append(
            "Align outcomes with Plan Marco de Implementación (PMI) indicator framework "
            "and demonstrate contribution to Peace Agreement implementation"
        )
    
    def _validate_baseline_context(self, rule, context, data, result):
        """Validate baseline context (DIM04)."""
        if context.multidimensional_poverty_rate:
            result.recommendations.append(
                f"Baseline should acknowledge multidimensional poverty rate of "
                f"{context.multidimensional_poverty_rate:.1f}% (PDET avg: 46.8%)"
            )
    
    def _validate_comparative_benchmarking(self, rule, context, data, result):
        """Validate comparative benchmarking (DIM04)."""
        result.recommendations.append(
            f"Benchmark outcomes against {context.subregion_name} subregion averages "
            f"and category {context.category} municipalities"
        )
    
    def _validate_peace_accord_alignment(self, rule, context, data, result):
        """Validate peace accord alignment (DIM05)."""
        result.recommendations.append(
            "Demonstrate direct contribution to Peace Agreement (Punto 1 - Reforma Rural Integral). "
            "15-year horizon aligns with PMI implementation timeline."
        )
    
    def _validate_structural_transformation(self, rule, context, data, result):
        """Validate structural transformation (DIM05)."""
        result.recommendations.append(
            "Address Estado-Territorio closure: institutional presence, basic service access, "
            "economic inclusion, infrastructure connectivity"
        )
    
    def _validate_long_term_sustainability(self, rule, context, data, result):
        """Validate long-term sustainability (DIM05)."""
        if context.fiscal_autonomy == "Muy baja":
            result.warnings.append(
                "Consider post-PDET fiscal sustainability given very low autonomy. "
                "Plan for institutional capacity building and gradual autonomy increase."
            )
    
    def _validate_conflict_sensitive_causality(self, rule, context, data, result):
        """Validate conflict-sensitive causality (DIM06)."""
        result.recommendations.append(
            "Ensure causal logic is conflict-sensitive: security, trust, and reconciliation "
            "are preconditions for service delivery effectiveness in post-conflict contexts"
        )
    
    def _validate_territorial_causality(self, rule, context, data, result):
        """Validate territorial causality (DIM06)."""
        context_factors = []
        if context.ethnic_composition:
            context_factors.append(f"ethnic diversity ({', '.join(context.ethnic_composition)})")
        if context.fiscal_autonomy:
            context_factors.append(f"institutional capacity ({context.fiscal_autonomy})")
        
        if context_factors:
            result.recommendations.append(
                f"Adapt causal mechanisms to: {', '.join(context_factors)}"
            )
    
    def _validate_evidence_base(self, rule, context, data, result):
        """Validate evidence base (DIM06)."""
        if context.active_route_initiatives:
            completion_rate = (context.active_route_initiatives / context.patr_initiatives * 100) if context.patr_initiatives else 0
            result.recommendations.append(
                f"Ground causal assumptions in PATR evidence: "
                f"{context.active_route_initiatives}/{context.patr_initiatives} initiatives active "
                f"({completion_rate:.1f}% completion rate)"
            )
    
    def _validate_systemic_approach(self, rule, context, data, result):
        """Validate systemic approach (DIM06)."""
        result.recommendations.append(
            "Model multi-level governance: (1) national entities (DNP, ART, ministries), "
            "(2) departmental coordination, (3) inter-municipal cooperation, (4) community participation"
        )
    
    def get_pdet_enrichment_metadata(self) -> Dict[str, Any]:
        """Get PDET enrichment metadata from templates."""
        return self._validation_templates.get("pdet_enrichment", {})
    
    def get_validation_gates_config(self) -> Dict[str, Any]:
        """Get validation gates configuration for PDET."""
        enrichment = self.get_pdet_enrichment_metadata()
        return enrichment.get("validation_gates", {})
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get PDET validator statistics."""
        pdet_enrichment = self.get_pdet_enrichment_metadata()
        
        # Count PDET validations per dimension
        dimension_counts = {}
        templates = self._validation_templates.get("templates", {})
        for dimension, validations in templates.items():
            pdet_count = sum(1 for v in validations if v.get("pdet_specific", False))
            if pdet_count > 0:
                dimension_counts[dimension] = pdet_count
        
        return {
            "pdet_municipalities_indexed": len(self._municipality_index),
            "pdet_subregions_indexed": len(self._subregion_index),
            "validation_templates_version": self._validation_templates.get("version"),
            "pdet_enrichment_version": pdet_enrichment.get("version"),
            "pdet_enrichment_enabled": pdet_enrichment.get("enabled", False),
            "pdet_validations_by_dimension": dimension_counts,
            "total_pdet_validations": sum(dimension_counts.values()),
            "validation_gates_enabled": {
                gate_name: gate_config.get("enabled", False)
                for gate_name, gate_config in self.get_validation_gates_config().items()
            }
        }


# Convenience function for quick validation
def validate_pdet_context(
    dimension: str,
    municipality_code: str,
    validation_data: Dict[str, Any]
) -> List[PDETValidationResult]:
    """
    Quick validation function for PDET context.
    
    Args:
        dimension: Dimension code (e.g., "DIM01_INSUMOS")
        municipality_code: DANE municipality code
        validation_data: Data to validate
    
    Returns:
        List of PDETValidationResult objects
    """
    validator = PDETValidator()
    return validator.validate_pdet_context(dimension, municipality_code, validation_data)
