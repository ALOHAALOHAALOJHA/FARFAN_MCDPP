"""
TerriData Scraper for PDET Municipality Enrichment

This script enriches PDET municipality data with official statistics from TerriData,
Colombia's official territorial information system.

TerriData provides:
- Demographic data (population, density, ethnic composition)
- Socioeconomic indicators (poverty, education, health)
- Infrastructure data (roads, utilities, connectivity)
- Institutional capacity (fiscal autonomy, administrative category)

Data sources:
- https://terridata.dnp.gov.co
- DANE (National Statistics Department)
- DNP (National Planning Department)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TerriDataEnricher:
    """Enriches PDET municipality data with TerriData information."""
    
    def __init__(self, pdet_data_path: Path):
        self.pdet_data_path = pdet_data_path
        self.pdet_data = self._load_pdet_data()
        
    def _load_pdet_data(self) -> Dict[str, Any]:
        """Load existing PDET data."""
        with open(self.pdet_data_path) as f:
            return json.load(f)
    
    def _get_terridata_enrichment(self, municipality_code: str, muni_name: str, 
                                   department: str) -> Dict[str, Any]:
        """
        Get TerriData enrichment for a municipality.
        
        Note: In production, this would make API calls to TerriData.
        For now, we return structured placeholders that follow TerriData schema.
        """
        # TerriData categories based on official schema
        return {
            "demographic": {
                "population_census_2018": None,  # From DANE Census
                "population_projection_2025": None,  # DNP projections
                "population_density_km2": None,
                "urban_population_pct": None,
                "rural_population_pct": None,
                "growth_rate_annual": None,
                "dependency_ratio": None,  # (0-14 + 65+) / (15-64)
                "sex_ratio": None,  # Men per 100 women
                "ethnic_groups": {
                    "indigena_pct": None,
                    "afrodescendiente_pct": None,
                    "raizal_pct": None,
                    "rom_pct": None,
                    "palenquero_pct": None
                }
            },
            "socioeconomic": {
                "poverty": {
                    "multidimensional_poverty_rate": None,  # IPM
                    "monetary_poverty_rate": None,
                    "extreme_poverty_rate": None,
                    "nbi_total": None,  # Necesidades Básicas Insatisfechas
                    "nbi_inadequate_housing": None,
                    "nbi_inadequate_services": None,
                    "nbi_critical_overcrowding": None,
                    "nbi_economic_dependence": None,
                    "nbi_school_non_attendance": None
                },
                "inequality": {
                    "gini_coefficient": None,
                    "income_quintiles": None
                },
                "education": {
                    "literacy_rate": None,
                    "average_years_education": None,
                    "coverage_preschool": None,
                    "coverage_primary": None,
                    "coverage_secondary": None,
                    "coverage_tertiary": None,
                    "dropout_rate": None,
                    "quality_saber_11_avg": None
                },
                "health": {
                    "health_coverage_pct": None,
                    "contributive_regime_pct": None,
                    "subsidized_regime_pct": None,
                    "infant_mortality_rate": None,  # Per 1000 live births
                    "maternal_mortality_rate": None,  # Per 100,000 live births
                    "life_expectancy": None,
                    "vaccination_coverage": None
                }
            },
            "economic": {
                "employment": {
                    "unemployment_rate": None,
                    "informal_employment_rate": None,
                    "economically_active_population": None
                },
                "sectors": {
                    "agriculture_gdp_pct": None,
                    "industry_gdp_pct": None,
                    "services_gdp_pct": None,
                    "mining_gdp_pct": None
                },
                "income": {
                    "per_capita_income_cop": None,
                    "average_wage_cop": None,
                    "minimum_wage_multiples": None
                }
            },
            "infrastructure": {
                "utilities": {
                    "water_coverage_urban": None,
                    "water_coverage_rural": None,
                    "sewerage_coverage_urban": None,
                    "sewerage_coverage_rural": None,
                    "electricity_coverage": None,
                    "gas_coverage": None,
                    "internet_coverage": None
                },
                "roads": {
                    "paved_roads_km": None,
                    "unpaved_roads_km": None,
                    "road_density_km_per_km2": None,
                    "connectivity_index": None
                },
                "housing": {
                    "total_housing_units": None,
                    "deficit_quantitative": None,
                    "deficit_qualitative": None,
                    "overcrowding_rate": None
                }
            },
            "institutional": {
                "fiscal": {
                    "total_revenue_cop_millions": None,
                    "own_revenue_cop_millions": None,
                    "transfers_cop_millions": None,
                    "fiscal_autonomy_index": None,  # Own revenue / Total revenue
                    "per_capita_revenue_cop": None
                },
                "capacity": {
                    "administrative_category": None,  # Special, 1, 2, 3, 4, 5, 6
                    "icld_index": None,  # Índice de Capacidad Departamental/Local
                    "municipal_performance_index": None,
                    "transparency_index": None
                }
            },
            "violence_conflict": {
                "homicide_rate": None,  # Per 100,000 inhabitants
                "kidnapping_rate": None,
                "forced_displacement_victims": None,
                "land_mines_accidents": None,
                "armed_confrontations": None,
                "massacres": None,
                "conflict_intensity_index": None
            },
            "territorial": {
                "area_km2": None,
                "altitude_meters": None,
                "climate_zone": None,
                "hydrographic_basin": None,
                "protected_areas_pct": None,
                "deforestation_rate": None,
                "environmental_risk_index": None
            },
            "_metadata": {
                "terridata_last_update": None,
                "dane_census_year": 2018,
                "data_completeness_pct": 0,
                "data_quality_score": None,
                "notes": []
            }
        }
    
    def enrich_all_municipalities(self) -> Dict[str, Any]:
        """Enrich all municipalities with TerriData data."""
        logger.info("Starting TerriData enrichment for all PDET municipalities...")
        
        enriched_count = 0
        total_count = 0
        
        for subregion in self.pdet_data['subregions']:
            subregion_id = subregion['subregion_id']
            logger.info(f"Enriching subregion {subregion_id}: {subregion['name']}")
            
            for municipality in subregion['municipalities']:
                total_count += 1
                muni_code = municipality['municipality_code']
                muni_name = municipality['name']
                department = municipality['department']
                
                # Get TerriData enrichment
                terridata_data = self._get_terridata_enrichment(
                    muni_code, muni_name, department
                )
                
                # Add to municipality
                municipality['terridata_enrichment'] = terridata_data
                enriched_count += 1
                
                logger.debug(f"  Enriched {muni_name} ({department}) - {muni_code}")
        
        logger.info(f"Enriched {enriched_count}/{total_count} municipalities")
        
        # Update metadata
        self.pdet_data['_version'] = "2.1.0"
        self.pdet_data['_terridata_enrichment'] = {
            "enriched_at": datetime.now().isoformat(),
            "municipalities_enriched": enriched_count,
            "total_municipalities": total_count,
            "coverage_pct": (enriched_count / total_count * 100) if total_count > 0 else 0,
            "data_sources": [
                "TerriData - DNP",
                "DANE Census 2018",
                "DNP Population Projections 2025",
                "Sistema de Estadísticas Territoriales"
            ]
        }
        
        return self.pdet_data
    
    def save_enriched_data(self, output_path: Path = None):
        """Save enriched data to file."""
        if output_path is None:
            output_path = self.pdet_data_path
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.pdet_data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        
        logger.info(f"Saved enriched data to {output_path}")


def main():
    """Main execution."""
    # Setup paths
    repo_root = Path(__file__).parent.parent
    pdet_data_path = repo_root / "canonic_questionnaire_central" / "colombia_context" / "pdet_municipalities.json"
    
    # Create enricher and run
    enricher = TerriDataEnricher(pdet_data_path)
    enriched_data = enricher.enrich_all_municipalities()
    enricher.save_enriched_data()
    
    print("\n" + "=" * 80)
    print("TERRIDATA ENRICHMENT COMPLETE")
    print("=" * 80)
    print(f"Version: {enriched_data['_version']}")
    print(f"Municipalities enriched: {enriched_data['_terridata_enrichment']['municipalities_enriched']}")
    print(f"Coverage: {enriched_data['_terridata_enrichment']['coverage_pct']:.1f}%")
    print(f"Enriched at: {enriched_data['_terridata_enrichment']['enriched_at']}")
    print("\nTerriData fields added per municipality:")
    print("  - Demographic (population, density, ethnic composition)")
    print("  - Socioeconomic (poverty, education, health, inequality)")
    print("  - Economic (employment, sectors, income)")
    print("  - Infrastructure (utilities, roads, housing)")
    print("  - Institutional (fiscal, capacity)")
    print("  - Violence/Conflict (rates, victims, intensity)")
    print("  - Territorial (area, climate, environment)")
    print("\nNext steps:")
    print("  1. Populate NULL fields with actual TerriData API calls")
    print("  2. Validate data quality and completeness")
    print("  3. Update policy area enrichments with new indicators")
    print("=" * 80)


if __name__ == "__main__":
    main()
