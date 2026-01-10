"""
Update Policy Areas with Manual TerriData Enrichment References

This script updates policy area metadata to reference the manually enriched
TerriData fields in the PDET municipalities data.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Map indicators to actual TerriData fields that now exist
MANUAL_TERRIDATA_FIELD_MAPPING = {
    "PA01_mujeres_genero": [
        "socioeconomic.health.maternal_mortality_rate",
        "socioeconomic.education.literacy_rate",
        "economic.employment.unemployment_rate",
        "infrastructure.utilities.water_coverage_rural",
        "demographic.ethnic_groups.indigena_pct"
    ],
    "PA02_violencia_conflicto": [
        "violence_conflict.homicide_rate",
        "violence_conflict.forced_displacement_victims",
        "violence_conflict.armed_confrontations",
        "violence_conflict.conflict_intensity_index",
        "institutional.capacity.municipal_performance_index"
    ],
    "PA03_ambiente_cambio_climatico": [
        "territorial.deforestation_rate",
        "territorial.protected_areas_pct",
        "territorial.environmental_risk_index",
        "infrastructure.utilities.water_coverage_rural",
        "infrastructure.utilities.sewerage_coverage_rural"
    ],
    "PA04_derechos_economicos_sociales_culturales": [
        "socioeconomic.poverty.multidimensional_poverty_rate",
        "socioeconomic.poverty.nbi_total",
        "socioeconomic.inequality.gini_coefficient",
        "economic.employment.unemployment_rate",
        "socioeconomic.education.literacy_rate",
        "socioeconomic.health.health_coverage_pct",
        "infrastructure.housing.deficit_quantitative",
        "infrastructure.utilities.electricity_coverage"
    ],
    "PA05_victimas_paz": [
        "violence_conflict.forced_displacement_victims",
        "institutional.capacity.municipal_performance_index",
        "socioeconomic.health.health_coverage_pct",
        "socioeconomic.education.coverage_secondary"
    ],
    "PA06_ninez_adolescencia_juventud": [
        "socioeconomic.health.infant_mortality_rate",
        "socioeconomic.education.dropout_rate",
        "socioeconomic.education.coverage_preschool",
        "socioeconomic.health.vaccination_coverage",
        "economic.employment.unemployment_rate"
    ],
    "PA07_tierras_territorios": [
        "territorial.area_km2",
        "demographic.ethnic_groups.indigena_pct",
        "demographic.ethnic_groups.afrodescendiente_pct",
        "institutional.fiscal.fiscal_autonomy_index",
        "violence_conflict.conflict_intensity_index"
    ],
    "PA08_lideres_defensores": [
        "violence_conflict.homicide_rate",
        "institutional.capacity.transparency_index",
        "institutional.capacity.municipal_performance_index",
        "socioeconomic.education.literacy_rate"
    ],
    "PA09_crisis_PPL": [
        "institutional.capacity.municipal_performance_index",
        "socioeconomic.health.health_coverage_pct",
        "socioeconomic.education.literacy_rate",
        "violence_conflict.homicide_rate"
    ],
    "PA10_migracion": [
        "demographic.population_projection_2025",
        "economic.employment.informal_employment_rate",
        "socioeconomic.health.health_coverage_pct",
        "socioeconomic.education.coverage_primary",
        "infrastructure.utilities.electricity_coverage"
    ]
}


class PolicyAreaUpdater:
    """Updates policy areas with manual TerriData field references."""
    
    def __init__(self, policy_areas_dir: Path):
        self.policy_areas_dir = policy_areas_dir
        
    def update_policy_area(self, pa_key: str) -> bool:
        """Update a single policy area with TerriData field references."""
        pa_dir = self.policy_areas_dir / pa_key
        metadata_path = pa_dir / "metadata.json"
        
        if not metadata_path.exists():
            logger.warning(f"Metadata not found for {pa_key}")
            return False
        
        # Load existing metadata
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        # Update pdet_enrichment with TerriData field references
        if 'pdet_enrichment' not in metadata:
            logger.warning(f"No pdet_enrichment in {pa_key}")
            return False
        
        pdet_enrich = metadata['pdet_enrichment']
        
        # Add TerriData field references if they exist for this policy area
        if pa_key in MANUAL_TERRIDATA_FIELD_MAPPING:
            if 'pdet_context' not in pdet_enrich:
                pdet_enrich['pdet_context'] = {}
            
            pdet_enrich['pdet_context']['manual_terridata_fields'] = MANUAL_TERRIDATA_FIELD_MAPPING[pa_key]
        
        # Update enrichment version and date
        pdet_enrich['_pdet_enrichment_version'] = "2.2.0"
        pdet_enrich['_enrichment_date'] = datetime.now().isoformat()
        
        # Add note about manual enrichment
        if '_metadata' not in pdet_enrich:
            pdet_enrich['_metadata'] = {}
        
        pdet_enrich['_metadata']['terridata_enrichment_method'] = "manual_estimation"
        pdet_enrich['_metadata']['terridata_enrichment_note'] = (
            "References manual TerriData enrichment based on realistic Colombian municipal patterns. "
            "Values should be validated with actual TerriData API when available."
        )
        
        # Save updated metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            f.write('\n')
        
        logger.info(f"Updated {pa_key} with {len(MANUAL_TERRIDATA_FIELD_MAPPING.get(pa_key, []))} TerriData field references")
        return True
    
    def update_all_policy_areas(self) -> Dict[str, int]:
        """Update all policy areas with TerriData field references."""
        logger.info("Updating all policy areas with manual TerriData field references...")
        
        stats = {
            'updated': 0,
            'failed': 0,
            'total_fields': 0
        }
        
        for pa_key in MANUAL_TERRIDATA_FIELD_MAPPING.keys():
            success = self.update_policy_area(pa_key)
            if success:
                stats['updated'] += 1
                stats['total_fields'] += len(MANUAL_TERRIDATA_FIELD_MAPPING[pa_key])
            else:
                stats['failed'] += 1
        
        return stats


def main():
    """Main execution."""
    repo_root = Path(__file__).parent.parent
    policy_areas_dir = repo_root / "canonic_questionnaire_central" / "policy_areas"
    
    updater = PolicyAreaUpdater(policy_areas_dir)
    stats = updater.update_all_policy_areas()
    
    print("\n" + "=" * 80)
    print("POLICY AREAS MANUAL TERRIDATA UPDATE COMPLETE")
    print("=" * 80)
    print(f"Policy areas updated: {stats['updated']}")
    print(f"Policy areas failed: {stats['failed']}")
    print(f"Total TerriData field references added: {stats['total_fields']}")
    print("\nManual TerriData field references per policy area:")
    for pa_key, fields in MANUAL_TERRIDATA_FIELD_MAPPING.items():
        print(f"  {pa_key}: {len(fields)} fields")
    print("\nMethod: Manual estimation based on realistic Colombian municipal patterns")
    print("Note: Values should be validated with actual TerriData API when available")
    print("=" * 80)


if __name__ == "__main__":
    main()
