#!/usr/bin/env python3
"""
Keyword Consolidation Script - SISAS 2.0

Synchronizes keywords from policy_areas/ to _registry/keywords/ and creates
a consolidated index for fast lookup during extraction.

Usage:
    python scripts/consolidate_keywords.py
    
Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
Date: 2026-01-14
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def consolidate_keywords(base_path: Path) -> Dict[str, Any]:
    """
    Consolidate keywords from all policy areas into a unified index.
    
    Creates:
    - _registry/keywords/by_policy_area/{PA_ID}.json - Keywords per PA
    - _registry/keywords/CONSOLIDATED_INDEX.json - Master index
    - _registry/keywords/KEYWORD_TO_PA_MAP.json - Reverse lookup
    
    Returns:
        Statistics about the consolidation
    """
    stats = {
        "policy_areas_processed": 0,
        "total_keywords": 0,
        "unique_keywords": 0,
        "multi_pa_keywords": 0,
        "files_created": 0
    }
    
    policy_areas_dir = base_path / "canonic_questionnaire_central" / "policy_areas"
    registry_dir = base_path / "canonic_questionnaire_central" / "_registry" / "keywords"
    
    # Ensure directories exist
    by_pa_dir = registry_dir / "by_policy_area"
    by_pa_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect all keywords
    consolidated: Dict[str, Dict[str, Any]] = {}  # keyword -> metadata
    keyword_to_pa: Dict[str, List[str]] = defaultdict(list)
    pa_to_keywords: Dict[str, List[str]] = {}
    
    # Process each policy area
    for pa_dir in sorted(policy_areas_dir.iterdir()):
        if not pa_dir.is_dir() or pa_dir.name.startswith("_"):
            continue
        
        # Extract PA ID (e.g., "PA01_genero" -> "PA01")
        pa_id = pa_dir.name.split("_")[0]
        
        keywords_file = pa_dir / "keywords.json"
        if not keywords_file.exists():
            logger.warning(f"⚠️  Missing keywords.json for {pa_id}")
            continue
        
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                keywords_data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse {keywords_file}: {e}")
            continue
        
        keywords = keywords_data.get("keywords", [])
        pa_to_keywords[pa_id] = keywords
        stats["total_keywords"] += len(keywords)
        
        # Add to consolidated index
        for kw in keywords:
            if kw not in consolidated:
                consolidated[kw] = {
                    "keyword": kw,
                    "policy_areas": [],
                    "first_seen_in": pa_id
                }
            consolidated[kw]["policy_areas"].append(pa_id)
            keyword_to_pa[kw].append(pa_id)
        
        # Write to registry by PA
        registry_file = by_pa_dir / f"{pa_id}.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(keywords_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ {pa_id}: {len(keywords)} keywords synced")
        stats["policy_areas_processed"] += 1
        stats["files_created"] += 1
    
    # Write consolidated index
    consolidated_list = list(consolidated.values())
    index_file = registry_dir / "CONSOLIDATED_INDEX.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump({
            "version": "2.0.0",
            "total_keywords": len(consolidated_list),
            "keywords": consolidated_list
        }, f, indent=2, ensure_ascii=False)
    stats["files_created"] += 1
    
    # Write reverse lookup map
    map_file = registry_dir / "KEYWORD_TO_PA_MAP.json"
    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump({
            "version": "2.0.0",
            "description": "Maps keywords to policy areas for fast lookup",
            "map": dict(keyword_to_pa)
        }, f, indent=2, ensure_ascii=False)
    stats["files_created"] += 1
    
    # Write PA to keywords map
    pa_map_file = registry_dir / "PA_TO_KEYWORDS_MAP.json"
    with open(pa_map_file, 'w', encoding='utf-8') as f:
        json.dump({
            "version": "2.0.0",
            "description": "Maps policy areas to their keywords",
            "map": pa_to_keywords
        }, f, indent=2, ensure_ascii=False)
    stats["files_created"] += 1
    
    # Calculate stats
    stats["unique_keywords"] = len(consolidated)
    stats["multi_pa_keywords"] = sum(1 for kw, pas in keyword_to_pa.items() if len(pas) > 1)
    
    return stats


def validate_keywords(base_path: Path) -> Dict[str, Any]:
    """
    Validate keyword files for consistency.
    
    Checks:
    - All PAs have keywords.json
    - No duplicate keywords within same PA
    - Keyword format is valid (non-empty strings)
    """
    issues = []
    
    policy_areas_dir = base_path / "canonic_questionnaire_central" / "policy_areas"
    expected_pas = [f"PA{i:02d}" for i in range(1, 11)]
    
    for pa_id in expected_pas:
        # Find PA directory
        pa_dirs = list(policy_areas_dir.glob(f"{pa_id}_*"))
        if not pa_dirs:
            issues.append(f"{pa_id}: Directory not found")
            continue
        
        pa_dir = pa_dirs[0]
        keywords_file = pa_dir / "keywords.json"
        
        if not keywords_file.exists():
            issues.append(f"{pa_id}: keywords.json missing")
            continue
        
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            keywords = data.get("keywords", [])
            
            # Check for duplicates
            if len(keywords) != len(set(keywords)):
                duplicates = [kw for kw in keywords if keywords.count(kw) > 1]
                issues.append(f"{pa_id}: Duplicate keywords: {set(duplicates)}")
            
            # Check for empty strings
            empty = [i for i, kw in enumerate(keywords) if not kw.strip()]
            if empty:
                issues.append(f"{pa_id}: Empty keywords at indices: {empty}")
                
        except json.JSONDecodeError as e:
            issues.append(f"{pa_id}: JSON parse error: {e}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


def main():
    """Main entry point."""
    base_path = Path(__file__).resolve().parent.parent
    
    logger.info("=" * 60)
    logger.info("KEYWORD CONSOLIDATION - SISAS 2.0")
    logger.info("=" * 60)
    
    # Validate first
    logger.info("\n1. Validating keywords...")
    validation = validate_keywords(base_path)
    if not validation["valid"]:
        logger.warning("⚠️  Validation issues found:")
        for issue in validation["issues"]:
            logger.warning(f"   - {issue}")
    else:
        logger.info("✅ All keywords valid")
    
    # Consolidate
    logger.info("\n2. Consolidating keywords...")
    stats = consolidate_keywords(base_path)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("CONSOLIDATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Policy Areas processed: {stats['policy_areas_processed']}")
    logger.info(f"Total keywords: {stats['total_keywords']}")
    logger.info(f"Unique keywords: {stats['unique_keywords']}")
    logger.info(f"Multi-PA keywords: {stats['multi_pa_keywords']}")
    logger.info(f"Files created: {stats['files_created']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
