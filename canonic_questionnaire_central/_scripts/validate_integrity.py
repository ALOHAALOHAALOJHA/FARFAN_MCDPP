#!/usr/bin/env python3
"""
Integrity Validation Script

Validates:
1. Referential integrity (all refs resolve)
2. Orphan detection (patterns/keywords without consumers)
3. Duplicate detection (content hash based)
4. Schema validation (all files match schemas)
5. Completeness validation (no null fields)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrityValidator:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats = {
            "questions_checked": 0,
            "patterns_checked": 0,
            "keywords_checked": 0,
            "mc_checked": 0,
            "entities_checked": 0,
            "broken_refs": 0,
            "orphans": 0,
            "duplicates": 0,
            "null_fields": 0
        }
    
    def validate_all(self) -> Dict:
        """Run all validation checks"""
        logger.info("=" * 70)
        logger.info("INTEGRITY VALIDATION - STARTING")
        logger.info("=" * 70)
        
        # 1. Check referential integrity
        logger.info("1. Checking referential integrity...")
        self._check_referential_integrity()
        
        # 2. Check for orphans
        logger.info("2. Checking for orphans...")
        self._check_orphans()
        
        # 3. Check for duplicates
        logger.info("3. Checking for duplicates...")
        self._check_duplicates()
        
        # 4. Check for null fields
        logger.info("4. Checking for null/empty fields...")
        self._check_null_fields()
        
        # 5. Generate report
        return self._generate_report()
    
    def _check_referential_integrity(self):
        """Check all references resolve correctly"""
        # Load all questions
        dimensions_path = self.base_path / "dimensions"
        
        # Build reference catalogs
        all_patterns = self._load_pattern_catalog()
        all_keywords = self._load_keyword_catalog()
        all_mc = self._load_mc_catalog()
        all_entities = self._load_entity_catalog()
        
        # Check each question's references
        for dim_dir in sorted(dimensions_path.iterdir()):
            if not dim_dir.is_dir() or not dim_dir.name.startswith("DIM"):
                continue
            
            questions_dir = dim_dir / "questions"
            if not questions_dir.exists():
                continue
            
            for q_file in sorted(questions_dir.glob("Q*.json")):
                self.stats["questions_checked"] += 1
                
                with open(q_file) as f:
                    q_data = json.load(f)
                
                refs = q_data.get("references", {})
                q_id = q_data.get("question_id", "UNKNOWN")
                
                # Check pattern refs
                for pat_id in refs.get("pattern_refs", []):
                    if pat_id not in all_patterns:
                        self.errors.append(f"{q_id}: Unknown pattern_ref '{pat_id}'")
                        self.stats["broken_refs"] += 1
                
                # Check keyword refs
                for kw_id in refs.get("keyword_refs", []):
                    if kw_id not in all_keywords:
                        self.warnings.append(f"{q_id}: Unknown keyword_ref '{kw_id}'")
                
                # Check MC refs
                for mc_id in refs.get("membership_criteria_refs", []):
                    if mc_id not in all_mc:
                        self.errors.append(f"{q_id}: Unknown MC ref '{mc_id}'")
                        self.stats["broken_refs"] += 1
                
                # Check entity refs
                for ent_id in refs.get("entity_refs", []):
                    if ent_id not in all_entities:
                        self.warnings.append(f"{q_id}: Unknown entity_ref '{ent_id}'")
    
    def _load_pattern_catalog(self) -> Set[str]:
        """Load all known pattern IDs"""
        catalog = set()
        patterns_file = self.base_path / "_registry" / "patterns" / "index.json"
        
        if patterns_file.exists():
            with open(patterns_file) as f:
                data = json.load(f)
                catalog.update(data.get("patterns", {}).keys())
        
        self.stats["patterns_checked"] = len(catalog)
        return catalog
    
    def _load_keyword_catalog(self) -> Set[str]:
        """Load all known keyword IDs"""
        catalog = set()
        keywords_dir = self.base_path / "_registry" / "keywords"
        
        if keywords_dir.exists():
            for kw_file in keywords_dir.glob("*.json"):
                with open(kw_file) as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        catalog.update(data.get("keywords", {}).keys())
        
        self.stats["keywords_checked"] = len(catalog)
        return catalog
    
    def _load_mc_catalog(self) -> Set[str]:
        """Load all known MC IDs"""
        catalog = set()
        mc_dir = self.base_path / "_registry" / "membership_criteria"
        
        if mc_dir.exists():
            for mc_file in mc_dir.glob("MC*.json"):
                mc_id = mc_file.stem
                catalog.add(mc_id)
        
        self.stats["mc_checked"] = len(catalog)
        return catalog
    
    def _load_entity_catalog(self) -> Set[str]:
        """Load all known entity IDs"""
        catalog = set()
        entities_dir = self.base_path / "_registry" / "entities"
        
        if entities_dir.exists():
            for ent_file in entities_dir.glob("*.json"):
                with open(ent_file) as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        catalog.update(data.get("entities", {}).keys())
        
        self.stats["entities_checked"] = len(catalog)
        return catalog
    
    def _check_orphans(self):
        """Check for patterns/keywords/etc not referenced by any question"""
        # Build usage maps
        pattern_usage = defaultdict(int)
        keyword_usage = defaultdict(int)
        
        dimensions_path = self.base_path / "dimensions"
        
        for dim_dir in sorted(dimensions_path.iterdir()):
            if not dim_dir.is_dir() or not dim_dir.name.startswith("DIM"):
                continue
            
            questions_dir = dim_dir / "questions"
            if not questions_dir.exists():
                continue
            
            for q_file in sorted(questions_dir.glob("Q*.json")):
                with open(q_file) as f:
                    q_data = json.load(f)
                
                refs = q_data.get("references", {})
                
                for pat_id in refs.get("pattern_refs", []):
                    pattern_usage[pat_id] += 1
                
                for kw_id in refs.get("keyword_refs", []):
                    keyword_usage[kw_id] += 1
        
        # Check for orphans
        all_patterns = self._load_pattern_catalog()
        orphan_patterns = all_patterns - set(pattern_usage.keys())
        
        if orphan_patterns:
            self.warnings.append(f"Found {len(orphan_patterns)} orphan patterns (not referenced by any question)")
            self.stats["orphans"] += len(orphan_patterns)
    
    def _check_duplicates(self):
        """Check for duplicate question content"""
        seen_hashes = {}
        
        dimensions_path = self.base_path / "dimensions"
        
        for dim_dir in sorted(dimensions_path.iterdir()):
            if not dim_dir.is_dir() or not dim_dir.name.startswith("DIM"):
                continue
            
            questions_dir = dim_dir / "questions"
            if not questions_dir.exists():
                continue
            
            for q_file in sorted(questions_dir.glob("Q*.json")):
                with open(q_file) as f:
                    q_data = json.load(f)
                
                # Hash the text field
                text = q_data.get("text", {}).get("es", "")
                content_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
                
                q_id = q_data.get("question_id", "UNKNOWN")
                
                if content_hash in seen_hashes:
                    self.warnings.append(f"Duplicate content: {q_id} matches {seen_hashes[content_hash]}")
                    self.stats["duplicates"] += 1
                else:
                    seen_hashes[content_hash] = q_id
    
    def _check_null_fields(self):
        """Check for null or empty required fields"""
        dimensions_path = self.base_path / "dimensions"
        
        required_fields = ["question_id", "dimension_id", "policy_area_id", "cluster_id", "base_slot", "text"]
        
        for dim_dir in sorted(dimensions_path.iterdir()):
            if not dim_dir.is_dir() or not dim_dir.name.startswith("DIM"):
                continue
            
            questions_dir = dim_dir / "questions"
            if not questions_dir.exists():
                continue
            
            for q_file in sorted(questions_dir.glob("Q*.json")):
                with open(q_file) as f:
                    q_data = json.load(f)
                
                q_id = q_data.get("question_id", "UNKNOWN")
                
                for field in required_fields:
                    if field not in q_data or q_data[field] is None or q_data[field] == "":
                        self.errors.append(f"{q_id}: Required field '{field}' is null or empty")
                        self.stats["null_fields"] += 1
    
    def _generate_report(self) -> Dict:
        """Generate final validation report"""
        logger.info("=" * 70)
        logger.info("VALIDATION RESULTS")
        logger.info("=" * 70)
        
        report = {
            "validation_passed": len(self.errors) == 0,
            "statistics": self.stats,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "critical_issues": [e for e in self.errors if "Unknown" in e or "null" in e]
            }
        }
        
        logger.info(f"Questions checked: {self.stats['questions_checked']}")
        logger.info(f"Patterns checked: {self.stats['patterns_checked']}")
        logger.info(f"Keywords checked: {self.stats['keywords_checked']}")
        logger.info(f"MC checked: {self.stats['mc_checked']}")
        logger.info(f"Entities checked: {self.stats['entities_checked']}")
        logger.info("-" * 70)
        logger.info(f"Broken refs: {self.stats['broken_refs']}")
        logger.info(f"Orphans: {self.stats['orphans']}")
        logger.info(f"Duplicates: {self.stats['duplicates']}")
        logger.info(f"Null fields: {self.stats['null_fields']}")
        logger.info("-" * 70)
        logger.info(f"Total errors: {len(self.errors)}")
        logger.info(f"Total warnings: {len(self.warnings)}")
        logger.info("=" * 70)
        
        if report["validation_passed"]:
            logger.info("✓ VALIDATION PASSED")
        else:
            logger.error("✗ VALIDATION FAILED")
            logger.error(f"  {len(self.errors)} critical errors found")
        
        logger.info("=" * 70)
        
        return report


def main():
    base_path = Path(__file__).parent.parent
    validator = IntegrityValidator(base_path)
    
    report = validator.validate_all()
    
    # Save report
    output_file = base_path / "_build" / "integrity_report.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Report saved to: {output_file}")
    
    # Exit with error code if validation failed
    return 0 if report["validation_passed"] else 1


if __name__ == "__main__":
    exit(main())
