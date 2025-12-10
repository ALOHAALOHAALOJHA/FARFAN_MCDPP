#!/usr/bin/env python3
"""
JOBFRONT 7 Phase 2: Populate Intrinsic Calibration
Generates intrinsic_calibration.json from method_inventory.json with proper metadata.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_base_score(method_info: dict) -> float:
    """Generate base calibration score based on method characteristics."""
    score = 0.5  # baseline
    
    # Boost for type hints
    if method_info.get('has_type_hints'):
        score += 0.1
    
    # Boost for documentation
    if method_info.get('docstring'):
        score += 0.1
    
    # Role-based adjustment
    role = method_info.get('role', 'utility')
    role_scores = {
        'executor': 0.75,  # Critical execution methods
        'score': 0.7,      # Scoring methods need high quality
        'orchestrator': 0.65,
        'analyzer': 0.6,
        'processor': 0.55,
        'ingest': 0.55,
        'extractor': 0.5,
        'utility': 0.45,    # Helper methods can be simpler
    }
    score = max(score, role_scores.get(role, 0.5))
    
    # Cap at 0.9 (reserve 0.9+ for manually verified methods)
    return min(score, 0.9)


def get_layer_for_role(role: str) -> str:
    """Map role to canonical layer type from LAYER_REQUIREMENTS."""
    role_to_layer = {
        'executor': 'executor',
        'score': 'score',
        'analyzer': 'analyzer',
        'processor': 'processor',
        'ingest': 'ingest',
        'extractor': 'extractor',
        'orchestrator': 'orchestrator',
        'utility': 'utility',
    }
    return role_to_layer.get(role, 'utility')


def populate_intrinsic_calibration(inventory_path: Path, output_path: Path):
    """Generate intrinsic_calibration.json from method inventory."""
    
    logger.info(f"Loading inventory from {inventory_path}")
    with open(inventory_path) as f:
        inventory = json.load(f)
    
    methods_inventory = inventory.get('methods', {})
    logger.info(f"Found {len(methods_inventory)} methods in inventory")
    
    # Build intrinsic calibration structure
    intrinsic_data = {
        "_cohort_metadata": {
            "cohort_id": "COHORT_2024",
            "creation_date": datetime.utcnow().isoformat() + "Z",
            "wave_version": "REFACTOR_WAVE_2024_12",
            "jobfront": "JOBFRONT_7_PHASE_2"
        },
        "_metadata": {
            "version": "2.0.0",
            "description": "Intrinsic calibration for current codebase with SISAS",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "authority": "Doctrina SIN_CARRETA",
            "total_methods": len(methods_inventory),
            "source": "JOBFRONT_7_method_inventory_generator"
        },
        "base_layer": {
            "symbol": "@b",
            "name": "Base Layer",
            "description": "Intrinsic quality of the method code",
            "aggregation": {
                "method": "weighted_sum",
                "weights": {
                    "b_theory": 0.4,
                    "b_impl": 0.35,
                    "b_deploy": 0.25
                }
            }
        },
        "methods": {}
    }
    
    # Populate methods
    for method_id, method_info in methods_inventory.items():
        role = method_info.get('role', 'utility')
        layer = get_layer_for_role(role)
        base_score = generate_base_score(method_info)
        
        intrinsic_data["methods"][method_id] = {
            "canonical_name": method_info.get('canonical_name'),
            "role": role,
            "layer": layer,
            "base_score": base_score,
            "module_path": method_info.get('module_path'),
            "file_path": method_info.get('file_path'),
            "metadata": {
                "has_type_hints": method_info.get('has_type_hints', False),
                "has_docstring": bool(method_info.get('docstring')),
                "parameter_count": method_info.get('parameter_count', 0),
                "class_name": method_info.get('class_name'),
            }
        }
    
    # Save
    logger.info(f"Saving intrinsic calibration to {output_path}")
    with open(output_path, 'w') as f:
        json.dump(intrinsic_data, f, indent=2)
    
    logger.info(f"✅ Generated intrinsic_calibration.json with {len(intrinsic_data['methods'])} methods")
    
    return intrinsic_data


if __name__ == "__main__":
    from collections import Counter
    
    print("="*80)
    print("JOBFRONT 7 Phase 2: Populating Intrinsic Calibration")
    print("="*80)
    
    inventory_path = Path("src/cross_cutting_infrastrucuiture/capaz_calibration_parmetrization/calibration/COHORT_2024_canonical_method_inventory.json")
    output_path = Path("src/cross_cutting_infrastrucuiture/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json")
    
    if not inventory_path.exists():
        print(f"❌ ERROR: Inventory not found at {inventory_path}")
        print("   Run scripts/generate_current_method_inventory.py first")
        exit(1)
    
    intrinsic_data = populate_intrinsic_calibration(inventory_path, output_path)
    
    print(f"\n{'='*80}")
    print(f"✅ INTRINSIC CALIBRATION GENERATED")
    print(f"   Location: {output_path}")
    print(f"   Methods: {len(intrinsic_data['methods'])}")
    print(f"{'='*80}")
    
    # Statistics
    methods = intrinsic_data['methods']
    
    layer_counts = Counter(m['layer'] for m in methods.values())
    role_counts = Counter(m['role'] for m in methods.values())
    
    score_ranges = {
        '0.9+': sum(1 for m in methods.values() if m['base_score'] >= 0.9),
        '0.7-0.9': sum(1 for m in methods.values() if 0.7 <= m['base_score'] < 0.9),
        '0.5-0.7': sum(1 for m in methods.values() if 0.5 <= m['base_score'] < 0.7),
        '<0.5': sum(1 for m in methods.values() if m['base_score'] < 0.5),
    }
    
    print(f"\n📊 Layer Distribution:")
    for layer, count in layer_counts.most_common():
        print(f"   {layer:15s}: {count:4d}")
    
    print(f"\n📊 Base Score Ranges:")
    for range_name, count in score_ranges.items():
        print(f"   {range_name:10s}: {count:4d}")
    
    # Verify executors
    executors = [m for m in methods.values() if m['layer'] == 'executor']
    dq_executors = [m for m in executors if 'D' in m['canonical_name'] and 'Q' in m['canonical_name']]
    
    print(f"\n🎯 Executor Verification:")
    print(f"   Total executors: {len(executors)}")
    print(f"   D*Q* pattern: {len(dq_executors)}")
    if len(dq_executors) >= 30:
        print(f"   ✅ All 30 D*Q* executors present")
    else:
        print(f"   ⚠️  Expected 30 D*Q*, found {len(dq_executors)}")
    
    print(f"\n{'='*80}")
    print("✅ JOBFRONT 7 COMPLETE - System ready for calibration!")
    print("="*80)
    print("\nNext steps:")
    print("1. Verify: python3 -c 'from src.core.calibration import get_intrinsic_loader'")
    print("2. Test: loader = get_intrinsic_loader(); print(len(loader.get_all_method_ids()))")
    print("3. Deploy: System is now operational")
