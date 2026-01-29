#!/usr/bin/env python3
"""
Entity Registry Verification Script
Validates entity registry enrichment and checks coverage
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

def load_json(filepath: Path) -> dict:
    """Load and parse JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_entity_registry(base_path: Path) -> Dict[str, any]:
    """Comprehensive verification of entity registry"""
    
    entities_dir = base_path / "canonic_questionnaire_central/_registry/entities"
    
    # Load files
    institutions = load_json(entities_dir / "institutions.json")
    territorial = load_json(entities_dir / "territorial.json")
    index_file = load_json(entities_dir / "index.json")
    
    results = {
        "validation_errors": [],
        "warnings": [],
        "statistics": {},
        "coverage": {}
    }
    
    # Verify entity counts
    inst_count = len(institutions.get("entities", {}))
    terr_count = len(territorial.get("entities", {}))
    total_count = inst_count + terr_count
    
    results["statistics"]["institutions_count"] = inst_count
    results["statistics"]["territorial_count"] = terr_count
    results["statistics"]["total_count"] = total_count
    
    # Verify expected counts
    expected_inst = 60
    expected_terr = 32
    
    if inst_count < expected_inst:
        results["validation_errors"].append(
            f"institutions.json has {inst_count} entities, expected at least {expected_inst}"
        )
    
    if terr_count < expected_terr:
        results["validation_errors"].append(
            f"territorial.json has {terr_count} entities, expected at least {expected_terr}"
        )
    
    # Verify ID uniqueness
    all_ids: Set[str] = set()
    duplicate_ids: List[str] = []
    
    for entity_id in institutions.get("entities", {}).keys():
        if entity_id in all_ids:
            duplicate_ids.append(entity_id)
        all_ids.add(entity_id)
    
    for entity_id in territorial.get("entities", {}).keys():
        if entity_id in all_ids:
            duplicate_ids.append(entity_id)
        all_ids.add(entity_id)
    
    if duplicate_ids:
        results["validation_errors"].append(
            f"Duplicate entity IDs found: {duplicate_ids}"
        )
    
    # Verify policy area coverage
    pa_coverage = defaultdict(int)
    pdet_entities = []
    post_conflict_entities = []
    
    for entity_id, entity in institutions.get("entities", {}).items():
        scoring = entity.get("scoring_context", {})
        
        # Count policy area mentions
        for pa in scoring.get("boost_policy_areas", {}).keys():
            pa_coverage[pa] += 1
        
        # Track PDET entities
        if scoring.get("pdet_specific"):
            pdet_entities.append(entity_id)
        
        # Track post-conflict entities
        if entity.get("context") in ["PDET", "POST_CONFLICT"]:
            post_conflict_entities.append(entity_id)
    
    for entity_id, entity in territorial.get("entities", {}).items():
        scoring = entity.get("scoring_context", {})
        for pa in scoring.get("boost_policy_areas", {}).keys():
            pa_coverage[pa] += 1
    
    results["coverage"]["policy_areas"] = dict(pa_coverage)
    results["coverage"]["pdet_entities"] = len(pdet_entities)
    results["coverage"]["post_conflict_entities"] = len(post_conflict_entities)
    
    # Check minimum coverage per PA
    for pa_num in range(1, 11):
        pa_code = f"PA{pa_num:02d}"
        if pa_code not in pa_coverage:
            results["warnings"].append(
                f"{pa_code} has NO entity coverage"
            )
        elif pa_coverage[pa_code] < 2:
            results["warnings"].append(
                f"{pa_code} has only {pa_coverage[pa_code]} entity (recommended: ≥2)"
            )
    
    # Verify PDET coverage
    if len(pdet_entities) < 2:
        results["warnings"].append(
            f"Only {len(pdet_entities)} PDET-specific entities found (recommended: ≥3)"
        )
    
    # Verify index.json statistics match
    index_stats = index_file.get("statistics", {})
    index_total = index_stats.get("total_entities", 0)
    
    # Note: index includes normative, populations, international (not verified here)
    # So we only check institutions + territorial
    actual_checked = inst_count + terr_count
    index_inst_terr = index_stats.get("by_category", {}).get("institution", 0) + \
                      index_stats.get("by_category", {}).get("territorial", 0)
    
    if actual_checked != index_inst_terr:
        results["warnings"].append(
            f"Index statistics mismatch: actual {actual_checked} vs index {index_inst_terr}"
        )
    
    return results

def print_verification_report(results: Dict[str, any]):
    """Print formatted verification report"""
    
    print("=" * 70)
    print("ENTITY REGISTRY VERIFICATION REPORT")
    print("=" * 70)
    
    print("\n📊 STATISTICS:")
    print(f"  • Institutions: {results['statistics']['institutions_count']}")
    print(f"  • Territorial: {results['statistics']['territorial_count']}")
    print(f"  • Total: {results['statistics']['total_count']}")
    
    print("\n🎯 COVERAGE:")
    print(f"  • PDET entities: {results['coverage']['pdet_entities']}")
    print(f"  • Post-conflict entities: {results['coverage']['post_conflict_entities']}")
    
    print("\n📋 POLICY AREA COVERAGE:")
    pa_cov = results['coverage']['policy_areas']
    for pa_num in range(1, 11):
        pa_code = f"PA{pa_num:02d}"
        count = pa_cov.get(pa_code, 0)
        status = "✅" if count >= 2 else ("⚠️" if count == 1 else "❌")
        print(f"  {status} {pa_code}: {count} entities")
    
    print("\n🔍 VALIDATION:")
    if results["validation_errors"]:
        print("  ❌ ERRORS FOUND:")
        for error in results["validation_errors"]:
            print(f"     • {error}")
    else:
        print("  ✅ No validation errors")
    
    if results["warnings"]:
        print("\n  ⚠️  WARNINGS:")
        for warning in results["warnings"]:
            print(f"     • {warning}")
    else:
        print("  ✅ No warnings")
    
    print("\n" + "=" * 70)
    
    # Overall status
    if results["validation_errors"]:
        print("❌ VERIFICATION FAILED")
        return False
    elif results["warnings"]:
        print("⚠️  VERIFICATION PASSED WITH WARNINGS")
        return True
    else:
        print("✅ VERIFICATION PASSED - ALL CHECKS SUCCESSFUL")
        return True

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent.parent.parent
    
    try:
        results = verify_entity_registry(base_path)
        success = print_verification_report(results)
        
        # Exit code
        exit(0 if success and not results["validation_errors"] else 1)
        
    except Exception as e:
        print(f"❌ Verification failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(2)
