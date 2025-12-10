#!/usr/bin/env python3
"""
Populate signal_requirements for V3 executor contracts based on policy areas.

This script updates the signal_requirements section of each contract to include
appropriate mandatory and optional signals based on the policy area and dimension.

Usage:
    python scripts/populate_signal_requirements.py [--dry-run]
"""

import argparse
import json
import sys
from pathlib import Path


# Policy area-specific signal mappings
POLICY_AREA_SIGNALS = {
    "PA01": {  # Women's Rights & Gender Equality
        "mandatory": ["gender_baseline_data", "vbg_statistics", "policy_coverage"],
        "optional": ["temporal_series", "source_validation", "territorial_scope"]
    },
    "PA02": {  # Rural Development
        "mandatory": ["rural_indicators", "land_tenure_data", "agricultural_policy"],
        "optional": ["infrastructure_gaps", "market_access", "subsidy_programs"]
    },
    "PA03": {  # Education
        "mandatory": ["enrollment_rates", "quality_indicators", "coverage_data"],
        "optional": ["infrastructure_status", "teacher_ratios", "dropout_rates"]
    },
    "PA04": {  # Health
        "mandatory": ["health_coverage", "mortality_rates", "service_availability"],
        "optional": ["disease_prevalence", "vaccination_rates", "infrastructure"]
    },
    "PA05": {  # Infrastructure
        "mandatory": ["infrastructure_inventory", "coverage_gaps", "investment_plans"],
        "optional": ["maintenance_status", "connectivity", "service_quality"]
    },
    "PA06": {  # Economic Development
        "mandatory": ["economic_indicators", "employment_data", "sectoral_distribution"],
        "optional": ["investment_flows", "productivity_metrics", "gdp_municipal"]
    },
    "PA07": {  # Environment
        "mandatory": ["environmental_baseline", "protection_areas", "risk_zones"],
        "optional": ["deforestation_rates", "water_quality", "biodiversity"]
    },
    "PA08": {  # Governance
        "mandatory": ["institutional_capacity", "participation_mechanisms", "transparency"],
        "optional": ["corruption_indicators", "citizen_satisfaction", "planning_quality"]
    },
    "PA09": {  # Security & Justice
        "mandatory": ["crime_statistics", "justice_access", "security_coverage"],
        "optional": ["conflict_indicators", "institutional_presence", "victimization_rates"]
    },
    "PA10": {  # Culture & Tourism
        "mandatory": ["cultural_assets", "tourism_infrastructure", "heritage_protection"],
        "optional": ["visitor_statistics", "cultural_programming", "economic_impact"]
    }
}

# Dimension-specific signals (apply across all policy areas)
DIMENSION_SIGNALS = {
    "DIM01": {  # Diagnostic Quality
        "mandatory": ["baseline_completeness", "data_sources"],
        "optional": ["temporal_coverage", "geographic_scope"]
    },
    "DIM02": {  # Causal Logic
        "mandatory": ["causal_chains", "intervention_logic"],
        "optional": ["theory_of_change", "assumptions"]
    },
    "DIM03": {  # Product Planning
        "mandatory": ["product_targets", "budget_allocation"],
        "optional": ["implementation_schedule", "responsible_entities"]
    },
    "DIM04": {  # Outcome Definition
        "mandatory": ["outcome_indicators", "measurement_validity"],
        "optional": ["composite_metrics", "verification_sources"]
    },
    "DIM05": {  # Impact Ambition
        "mandatory": ["long_term_vision", "transformative_potential"],
        "optional": ["sustainability_mechanisms", "scalability"]
    },
    "DIM06": {  # Territorial Context
        "mandatory": ["territorial_diagnosis", "differential_needs"],
        "optional": ["participation_evidence", "equity_considerations"]
    }
}


def populate_signal_requirements(contract: dict, dry_run: bool = False) -> tuple[bool, str]:
    """Populate signal_requirements for a contract.
    
    Args:
        contract: Contract dictionary
        dry_run: If True, don't modify contract
        
    Returns:
        (modified, message) tuple
    """
    # Extract policy area and dimension
    policy_area_id = contract.get("identity", {}).get("policy_area_id")
    dimension_id = contract.get("identity", {}).get("dimension_id")
    
    if not policy_area_id or not dimension_id:
        return False, "Missing policy_area_id or dimension_id"
    
    # Get signals for policy area and dimension
    pa_signals = POLICY_AREA_SIGNALS.get(policy_area_id, {})
    dim_signals = DIMENSION_SIGNALS.get(dimension_id, {})
    
    # Combine mandatory signals (union)
    mandatory_signals = list(set(
        pa_signals.get("mandatory", []) + 
        dim_signals.get("mandatory", [])
    ))
    
    # Combine optional signals (union)
    optional_signals = list(set(
        pa_signals.get("optional", []) + 
        dim_signals.get("optional", [])
    ))
    
    # Check if update needed
    current_sig_req = contract.get("signal_requirements", {})
    current_mandatory = current_sig_req.get("mandatory_signals", [])
    current_optional = current_sig_req.get("optional_signals", [])
    
    if (set(current_mandatory) == set(mandatory_signals) and 
        set(current_optional) == set(optional_signals)):
        return False, "Signal requirements already correct"
    
    # Update signal_requirements
    if not dry_run:
        if "signal_requirements" not in contract:
            contract["signal_requirements"] = {}
        
        contract["signal_requirements"]["mandatory_signals"] = sorted(mandatory_signals)
        contract["signal_requirements"]["optional_signals"] = sorted(optional_signals)
        
        # Keep other fields
        if "signal_aggregation" not in contract["signal_requirements"]:
            contract["signal_requirements"]["signal_aggregation"] = "weighted_mean"
        if "minimum_signal_threshold" not in contract["signal_requirements"]:
            contract["signal_requirements"]["minimum_signal_threshold"] = 0.0
    
    return True, f"Updated with {len(mandatory_signals)} mandatory, {len(optional_signals)} optional signals"


def main():
    parser = argparse.ArgumentParser(
        description="Populate signal_requirements for V3 executor contracts"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        help="Path to contracts directory (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    # Find contracts directory
    if args.contracts_dir:
        contracts_dir = args.contracts_dir
    else:
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        contracts_dir = project_root / "src" / "canonic_phases" / "Phase_two" / "json_files_phase_two" / "executor_contracts" / "specialized"
    
    if not contracts_dir.exists():
        print(f"❌ Contracts directory not found: {contracts_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Find all V3 contracts
    contract_files = sorted(contracts_dir.glob("Q*.v3.json"))
    
    if not contract_files:
        print(f"❌ No V3 contracts found in {contracts_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(contract_files)} V3 contracts")
    print()
    
    # Process contracts
    updated = 0
    already_correct = 0
    errors = 0
    
    for contract_path in contract_files:
        contract_id = contract_path.stem.replace(".v3", "")
        
        try:
            # Load contract
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            
            # Populate signal requirements
            modified, message = populate_signal_requirements(contract, dry_run=args.dry_run)
            
            if modified:
                updated += 1
                print(f"✅ {contract_id}: {message}")
                
                if not args.dry_run:
                    # Write back
                    with open(contract_path, "w", encoding="utf-8") as f:
                        json.dump(contract, f, indent=2, ensure_ascii=False)
                        f.write("\n")
            else:
                already_correct += 1
                # Only print every 50th to reduce output
                if already_correct % 50 == 1:
                    print(f"✅ {contract_id}: {message}")
        
        except Exception as e:
            errors += 1
            print(f"❌ {contract_id}: Error: {e}")
    
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Total contracts: {len(contract_files)}")
    print(f"  Updated: {updated}")
    print(f"  Already correct: {already_correct}")
    print(f"  Errors: {errors}")
    
    if args.dry_run:
        print()
        print("DRY RUN - No files were modified")
    
    print("=" * 60)
    
    sys.exit(0 if errors == 0 else 2)


if __name__ == "__main__":
    main()
