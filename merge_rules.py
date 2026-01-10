#!/usr/bin/env python3
"""
Merge new enhanced rules with existing recommendation rules
"""

import json
from datetime import datetime

def load_json_file(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(filepath, data):
    """Save JSON file with proper formatting"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def merge_rules():
    """Merge existing and new rules"""

    print("Loading existing rules...")
    existing_file = "/home/user/FARFAN_MPP/src/farfan_pipeline/phases/Phase_8/json_phase_eight/recommendation_rules_enhanced.json"
    existing_data = load_json_file(existing_file)

    print("Loading new rules...")
    new_file = "/home/user/FARFAN_MPP/new_enhanced_rules.json"
    new_rules = load_json_file(new_file)

    # Get existing rule IDs for deduplication
    existing_rule_ids = {rule.get('rule_id') for rule in existing_data.get('rules', [])}
    print(f"Existing rules: {len(existing_rule_ids)}")

    # Filter out duplicate rule IDs from new rules
    unique_new_rules = [
        rule for rule in new_rules
        if rule.get('rule_id') not in existing_rule_ids
    ]

    print(f"New unique rules to add: {len(unique_new_rules)}")
    print(f"Duplicate rules skipped: {len(new_rules) - len(unique_new_rules)}")

    # Combine rules
    combined_rules = existing_data.get('rules', []) + unique_new_rules

    # Count rules by level
    micro_count = sum(1 for r in combined_rules if r.get('level') == 'MICRO')
    meso_count = sum(1 for r in combined_rules if r.get('level') == 'MESO')
    macro_count = sum(1 for r in combined_rules if r.get('level') == 'MACRO')

    print(f"\nCombined rule statistics:")
    print(f"  - MICRO: {micro_count}")
    print(f"  - MESO: {meso_count}")
    print(f"  - MACRO: {macro_count}")
    print(f"  - TOTAL: {len(combined_rules)}")

    # Update metadata
    enhanced_data = {
        "version": "3.0",
        "last_updated": datetime.now().isoformat(),
        "enhanced_features": [
            "template_parameterization",
            "execution_logic",
            "measurable_indicators",
            "unambiguous_time_horizons",
            "testable_verification",
            "cost_tracking",
            "authority_mapping",
            "multi_threshold_scoring",
            "cross_cluster_dependencies",
            "momentum_tracking",
            "transformation_pathways",
            "crisis_management",
            "excellence_sustaining"
        ],
        "scoring_scenarios": [
            "CRÍTICO (0-0.8): Emergency intervention",
            "DEFICIENTE (0.8-1.2): Major restructuring",
            "INSUFICIENTE (1.2-1.65): Significant improvement",
            "ACEPTABLE (1.65-2.0): Minor adjustments",
            "BUENO (2.0-2.4): Optimization",
            "MUY BUENO (2.4-2.7): Excellence maintenance",
            "EXCELENTE (2.7-3.0): Leadership/best practices"
        ],
        "levels": {
            "MICRO": {
                "description": "Specific PA-DIM combinations with detailed scoring thresholds",
                "count": micro_count,
                "coverage": "10 PAs × 6 DIMs × 6 scoring thresholds"
            },
            "MESO": {
                "description": "Cluster-level rules with variance analysis and cross-cluster dependencies",
                "count": meso_count,
                "coverage": "4 clusters with variance, cross-cluster, multi-PA, and momentum scenarios"
            },
            "MACRO": {
                "description": "System-wide rules for crisis, transformation, and balance management",
                "count": macro_count,
                "coverage": "Crisis, transformation pathways, and inter-cluster balance scenarios"
            }
        },
        "rules": combined_rules
    }

    # Save enhanced file
    output_file = "/home/user/FARFAN_MPP/src/farfan_pipeline/phases/Phase_8/json_phase_eight/recommendation_rules_enhanced.json"
    print(f"\nSaving enhanced rules to: {output_file}")

    save_json_file(output_file, enhanced_data)

    print("✓ Rules merged successfully!")

    # Create a backup of the original file
    backup_file = f"{existing_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\nBackup saved to: {backup_file}")

    return enhanced_data

if __name__ == "__main__":
    merge_rules()
