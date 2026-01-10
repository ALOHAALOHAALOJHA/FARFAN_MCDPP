"""
Update Policy Area Enrichments with TerriData Indicators

This script updates policy area metadata to include TerriData-specific indicators
that are now available in the enriched PDET municipalities data.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Enhanced indicators mapped from TerriData for each policy area
TERRIDATA_INDICATORS_BY_POLICY_AREA = {
    "PA01_mujeres_genero": {
        "key_indicators": [
            "women_labor_participation",  # From economic.employment
            "gender_wage_gap",  # From economic.income
            "women_land_ownership",  # From institutional/territorial
            "maternal_mortality_rate",  # From socioeconomic.health
            "girls_education_parity",  # From socioeconomic.education
            "gender_violence_rate",  # From violence_conflict
            "women_political_representation",  # From institutional
            "reproductive_health_coverage",  # From socioeconomic.health
            "women_economic_autonomy_index",  # Composite indicator
            "gender_digital_divide",  # From infrastructure.utilities.internet_coverage
            "teenage_pregnancy_rate",  # From socioeconomic.health
            "women_time_poverty"  # From economic
        ],
        "terridata_fields": [
            "socioeconomic.health.maternal_mortality_rate",
            "socioeconomic.education.coverage_secondary",
            "economic.employment.unemployment_rate",
            "infrastructure.utilities.water_coverage_rural",
            "violence_conflict.homicide_rate"
        ]
    },
    "PA02_violencia_conflicto": {
        "key_indicators": [
            "homicide_rate",  # From violence_conflict
            "forced_displacement_victims",  # From violence_conflict
            "armed_confrontations",  # From violence_conflict
            "land_mines_accidents",  # From violence_conflict
            "massacres",  # From violence_conflict
            "conflict_intensity_index",  # From violence_conflict
            "security_forces_presence",  # From institutional
            "kidnapping_rate",  # From violence_conflict
            "territorial_control_disputes",  # From violence_conflict
            "victims_registry",  # From institutional
            "early_warning_alerts",  # From institutional
            "post_conflict_indicators"  # Composite
        ],
        "terridata_fields": [
            "violence_conflict.homicide_rate",
            "violence_conflict.forced_displacement_victims",
            "violence_conflict.armed_confrontations",
            "violence_conflict.land_mines_accidents",
            "violence_conflict.conflict_intensity_index",
            "institutional.capacity.municipal_performance_index"
        ]
    },
    "PA03_ambiente_cambio_climatico": {
        "key_indicators": [
            "deforestation_rate",  # From territorial
            "protected_areas_pct",  # From territorial
            "environmental_risk_index",  # From territorial
            "water_quality_index",  # From infrastructure
            "biodiversity_index",  # From territorial
            "climate_vulnerability_index",  # Composite
            "air_quality_index",  # From territorial
            "waste_management_coverage",  # From infrastructure
            "renewable_energy_usage",  # From infrastructure
            "ecosystem_services_value",  # From territorial
            "climate_adaptation_capacity",  # From institutional
            "environmental_governance"  # From institutional
        ],
        "terridata_fields": [
            "territorial.deforestation_rate",
            "territorial.protected_areas_pct",
            "territorial.environmental_risk_index",
            "infrastructure.utilities.water_coverage_rural",
            "infrastructure.utilities.sewerage_coverage_rural",
            "institutional.capacity.transparency_index"
        ]
    },
    "PA04_derechos_economicos_sociales_culturales": {
        "key_indicators": [
            "multidimensional_poverty_rate",  # From socioeconomic.poverty
            "nbi_total",  # From socioeconomic.poverty
            "gini_coefficient",  # From socioeconomic.inequality
            "unemployment_rate",  # From economic.employment
            "informal_employment_rate",  # From economic.employment
            "per_capita_income",  # From economic.income
            "literacy_rate",  # From socioeconomic.education
            "health_coverage_pct",  # From socioeconomic.health
            "housing_deficit",  # From infrastructure.housing
            "utilities_coverage",  # From infrastructure.utilities
            "food_security_index",  # Composite
            "social_protection_coverage",  # From institutional
            "credit_access_rate"  # From economic
        ],
        "terridata_fields": [
            "socioeconomic.poverty.multidimensional_poverty_rate",
            "socioeconomic.poverty.nbi_total",
            "socioeconomic.inequality.gini_coefficient",
            "economic.employment.unemployment_rate",
            "socioeconomic.education.literacy_rate",
            "socioeconomic.health.health_coverage_pct",
            "infrastructure.housing.deficit_quantitative",
            "infrastructure.utilities.electricity_coverage"
        ]
    },
    "PA05_victimas_paz": {
        "key_indicators": [
            "registered_victims",  # From violence_conflict
            "collective_reparations_cases",  # From institutional
            "land_restitution_cases",  # From institutional
            "psychosocial_attention_coverage",  # From socioeconomic.health
            "truth_commission_participation",  # From institutional
            "reconciliation_initiatives",  # From institutional
            "ex_combatants_reintegration",  # From institutional
            "transitional_justice_progress",  # From institutional
            "peace_infrastructure_index",  # Composite
            "community_dialogue_spaces",  # From institutional
            "victim_participation_mechanisms",  # From institutional
            "reparation_execution_rate"  # From institutional
        ],
        "terridata_fields": [
            "violence_conflict.forced_displacement_victims",
            "institutional.capacity.municipal_performance_index",
            "socioeconomic.health.health_coverage_pct",
            "socioeconomic.education.coverage_secondary"
        ]
    },
    "PA06_ninez_adolescencia_juventud": {
        "key_indicators": [
            "child_mortality_rate",  # From socioeconomic.health
            "school_dropout_rate",  # From socioeconomic.education
            "child_malnutrition_rate",  # From socioeconomic.health
            "education_coverage_preschool",  # From socioeconomic.education
            "teenage_pregnancy_rate",  # From socioeconomic.health
            "child_labor_rate",  # From economic
            "vaccination_coverage",  # From socioeconomic.health
            "youth_unemployment_rate",  # From economic.employment
            "vocational_training_coverage",  # From socioeconomic.education
            "recreational_spaces_index",  # From infrastructure
            "youth_participation_mechanisms",  # From institutional
            "child_protection_services"  # From institutional
        ],
        "terridata_fields": [
            "socioeconomic.health.infant_mortality_rate",
            "socioeconomic.education.dropout_rate",
            "socioeconomic.education.coverage_preschool",
            "socioeconomic.health.vaccination_coverage",
            "economic.employment.unemployment_rate"
        ]
    },
    "PA07_tierras_territorios": {
        "key_indicators": [
            "land_formalization_rate",  # From institutional
            "territorial_planning_coverage",  # From institutional
            "land_conflicts_rate",  # From violence_conflict
            "rural_property_concentration",  # From economic/territorial
            "land_use_planning_compliance",  # From institutional
            "indigenous_territories_recognition",  # From demographic/territorial
            "afro_collective_territories",  # From demographic/territorial
            "productive_land_percentage",  # From territorial
            "land_grabbing_cases",  # From violence_conflict
            "rural_cadastre_coverage",  # From institutional
            "territorial_entities_capacity",  # From institutional
            "environmental_zoning_compliance"  # From territorial
        ],
        "terridata_fields": [
            "territorial.area_km2",
            "demographic.ethnic_groups.indigena_pct",
            "demographic.ethnic_groups.afrodescendiente_pct",
            "institutional.fiscal.fiscal_autonomy_index",
            "violence_conflict.conflict_intensity_index"
        ]
    },
    "PA08_lideres_defensores": {
        "key_indicators": [
            "leaders_killings_rate",  # From violence_conflict
            "threats_against_leaders",  # From violence_conflict
            "protection_mechanisms_coverage",  # From institutional
            "early_warning_system_effectiveness",  # From institutional
            "civic_space_index",  # From institutional
            "civil_society_organizations",  # From institutional
            "leader_protection_measures",  # From institutional
            "impunity_rate_leader_crimes",  # From institutional
            "risk_level_assessment",  # From violence_conflict
            "collective_protection_routes",  # From institutional
            "access_to_justice",  # From institutional
            "security_guarantees_index"  # Composite
        ],
        "terridata_fields": [
            "violence_conflict.homicide_rate",
            "institutional.capacity.transparency_index",
            "institutional.capacity.municipal_performance_index",
            "socioeconomic.education.literacy_rate"
        ]
    },
    "PA09_crisis_PPL": {
        "key_indicators": [
            "prison_population_rate",  # From institutional
            "overcrowding_rate",  # From institutional
            "prison_conditions_index",  # From institutional
            "access_to_legal_defense",  # From institutional
            "pretrial_detention_rate",  # From institutional
            "prison_health_services",  # From socioeconomic.health
            "restorative_justice_programs",  # From institutional
            "recidivism_rate",  # From institutional
            "judicial_backlog",  # From institutional
            "alternative_measures_usage",  # From institutional
            "indigenous_jurisdiction_recognition",  # From institutional
            "access_to_justice_indicators"  # From institutional
        ],
        "terridata_fields": [
            "institutional.capacity.municipal_performance_index",
            "socioeconomic.health.health_coverage_pct",
            "socioeconomic.education.literacy_rate",
            "violence_conflict.homicide_rate"
        ]
    },
    "PA10_migracion": {
        "key_indicators": [
            "migrant_population",  # From demographic
            "refugee_population",  # From demographic
            "border_crossing_points",  # From territorial
            "migration_services_coverage",  # From institutional
            "cross_border_trade_volume",  # From economic
            "binational_cooperation_index",  # From institutional
            "migrant_integration_index",  # Composite
            "humanitarian_assistance_coverage",  # From institutional
            "regularization_rate",  # From institutional
            "migrant_labor_integration",  # From economic.employment
            "education_access_migrants",  # From socioeconomic.education
            "health_access_migrants"  # From socioeconomic.health
        ],
        "terridata_fields": [
            "demographic.population_projection_2025",
            "economic.employment.informal_employment_rate",
            "socioeconomic.health.health_coverage_pct",
            "socioeconomic.education.coverage_primary",
            "infrastructure.utilities.electricity_coverage"
        ]
    }
}


class PolicyAreaTerriDataUpdater:
    """Updates policy area enrichments with TerriData indicators."""
    
    def __init__(self, policy_areas_dir: Path):
        self.policy_areas_dir = policy_areas_dir
        
    def update_policy_area(self, pa_key: str, indicators_config: Dict[str, Any]) -> bool:
        """Update a single policy area with TerriData indicators."""
        pa_dir = self.policy_areas_dir / pa_key
        metadata_path = pa_dir / "metadata.json"
        
        if not metadata_path.exists():
            logger.warning(f"Metadata not found for {pa_key}")
            return False
        
        # Load existing metadata
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        # Update pdet_enrichment with TerriData indicators
        if 'pdet_enrichment' not in metadata:
            logger.warning(f"No pdet_enrichment in {pa_key}")
            return False
        
        pdet_enrich = metadata['pdet_enrichment']
        
        # Update key indicators
        pdet_enrich['pdet_context']['key_indicators'] = indicators_config['key_indicators']
        
        # Add TerriData field references
        pdet_enrich['pdet_context']['terridata_fields'] = indicators_config['terridata_fields']
        
        # Update enrichment version and date
        pdet_enrich['_pdet_enrichment_version'] = "2.1.0"
        pdet_enrich['_enrichment_date'] = datetime.now().isoformat()
        
        # Update value-add with TerriData enrichment
        pdet_enrich['_validation_gates']['gate_2_value_add']['estimated_value_add'] = 0.45
        pdet_enrich['_validation_gates']['gate_2_value_add']['enables'].append('terridata_integration')
        pdet_enrich['_validation_gates']['gate_2_value_add']['enables'].append('evidence_based_monitoring')
        
        # Save updated metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            f.write('\n')
        
        logger.info(f"Updated {pa_key} with {len(indicators_config['key_indicators'])} TerriData indicators")
        return True
    
    def update_all_policy_areas(self) -> Dict[str, int]:
        """Update all policy areas with TerriData indicators."""
        logger.info("Updating all policy areas with TerriData indicators...")
        
        stats = {
            'updated': 0,
            'failed': 0,
            'total_indicators': 0
        }
        
        for pa_key, indicators_config in TERRIDATA_INDICATORS_BY_POLICY_AREA.items():
            success = self.update_policy_area(pa_key, indicators_config)
            if success:
                stats['updated'] += 1
                stats['total_indicators'] += len(indicators_config['key_indicators'])
            else:
                stats['failed'] += 1
        
        return stats


def main():
    """Main execution."""
    repo_root = Path(__file__).parent.parent
    policy_areas_dir = repo_root / "canonic_questionnaire_central" / "policy_areas"
    
    updater = PolicyAreaTerriDataUpdater(policy_areas_dir)
    stats = updater.update_all_policy_areas()
    
    print("\n" + "=" * 80)
    print("POLICY AREAS TERRIDATA UPDATE COMPLETE")
    print("=" * 80)
    print(f"Policy areas updated: {stats['updated']}")
    print(f"Policy areas failed: {stats['failed']}")
    print(f"Total indicators added: {stats['total_indicators']}")
    print(f"Average indicators per policy area: {stats['total_indicators'] / stats['updated']:.1f}")
    print("\nEnhanced indicators per policy area:")
    for pa_key, config in TERRIDATA_INDICATORS_BY_POLICY_AREA.items():
        print(f"  {pa_key}: {len(config['key_indicators'])} indicators")
    print("=" * 80)


if __name__ == "__main__":
    main()
