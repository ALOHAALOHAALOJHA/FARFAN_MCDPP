#!/usr/bin/env python3
"""
Monolith Pattern Extractor and Contract Fixer
==============================================

Extracts the ACTUAL patterns and mappings from questionnaire_monolith.json
and applies them surgically to fix all contracts.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
from datetime import datetime, timezone
import logging
from collections import defaultdict

logging. basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONTRACTS_DIR = Path("src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized")
MONOLITH_PATH = Path("canonic_questionnaire_central/questionnaire_monolith.json")

class MonolithExtractor:
    """Extract real patterns and data from the monolith"""
    
    def __init__(self):
        self.monolith = None
        self.question_map = {}
        self.pattern_map = {}
        self.identity_map = {}
        
    def load_monolith(self):
        """Load the 60,000-line monolith"""
        logger.info(f"Loading monolith from {MONOLITH_PATH}")
        with open(MONOLITH_PATH, 'r', encoding='utf-8') as f:
            self.monolith = json.load(f)
        
        # Build question map from blocks.micro_questions
        micro_questions = self.monolith.get("blocks", {}).get("micro_questions", [])
        
        for question in micro_questions:
            qid = f"Q{question.get('question_global', 0):03d}"
            self.question_map[qid] = question
            
            # Extract patterns
            patterns = question.get("patterns", [])
            self.pattern_map[qid] = patterns
            
            # Extract identity fields
            self.identity_map[qid] = {
                "question_id": qid,
                "question_global": question.get("question_global"),
                "policy_area_id": question.get("policy_area_id"),
                "dimension_id": question.get("dimension_id"),
                "cluster_id": question.get("cluster_id"),
                "base_slot": question.get("base_slot")
            }
        
        logger.info(f"Loaded {len(self.question_map)} questions from monolith")
    
    def get_correct_patterns(self, qid: str) -> List[Dict]:
        """Get the correct patterns for a question from monolith"""
        question = self.question_map.get(qid, {})
        return question.get("patterns", [])
    
    def get_correct_identity(self, qid: str) -> Dict:
        """Get correct identity fields from monolith"""
        return self.identity_map.get(qid, {})
    
    def get_evidence_assembly_mapping(self, qid: str) -> Dict[str, str]:
        """Get the correct evidence assembly source mappings"""
        question = self. question_map.get(qid, {})
        
        # Extract the actual assembly rules from the monolith
        assembly_rules = question.get("evidence_assembly", {}).get("assembly_rules", [])
        
        # Build mapping of what sources should map to what provides
        source_mapping = {}
        for rule in assembly_rules:
            for source in rule.get("sources", []):
                # Map common patterns from monolith
                if "text_mining. critical_links" in source:
                    source_mapping[source] = "text_mining.diagnose_critical_links"
                elif "industrial_policy. processed_evidence" in source:
                    source_mapping[source] = "industrial_policy.process"
                elif "causal_extraction.goals" in source:
                    source_mapping[source] = "causal_extraction.extract_goals"
                elif "financial_audit.amounts" in source:
                    source_mapping[source] = "financial_audit.parse_amount"
                elif "pdet_analysis.financial_data" in source:
                    source_mapping[source] = "pdet_analysis.extract_financial_amounts"
                elif "contradiction_detection.quantitative_claims" in source:
                    source_mapping[source] = "contradiction_detection.extract_quantitative_claims"
                elif "bayesian_analysis.policy_metrics" in source:
                    source_mapping[source] = "bayesian_analysis.evaluate_policy_metric"
        
        return source_mapping


class SurgicalContractFixer:
    """Fix contracts using ACTUAL monolith data"""
    
    def __init__(self, extractor: MonolithExtractor):
        self.extractor = extractor
    
    def fix_all_contracts(self, dry_run: bool = False):
        """Fix all 300 contracts using monolith data"""
        results = {}
        
        for qid, question_data in self.extractor.question_map.items():
            path = CONTRACTS_DIR / f"{qid}.v3.json"
            if not path.exists():
                logger.warning(f"Contract {qid} not found")
                continue
            
            # Load contract
            with open(path, 'r') as f:
                contract = json.load(f)
            
            fixes = []
            
            # Fix 1: Update patterns from monolith
            if self._fix_patterns(contract, qid):
                fixes.append("patterns")
            
            # Fix 2: Fix identity consistency
            if self._fix_identity_consistency(contract, qid):
                fixes.append("identity_consistency")
            
            # Fix 3: Fix evidence assembly
            if self._fix_evidence_assembly(contract, qid):
                fixes.append("evidence_assembly")
            
            # Fix 4: Add missing structures
            if self._add_missing_structures(contract, qid):
                fixes.append("missing_structures")
            
            # Fix 5: Update contract hash
            if self._update_hash(contract):
                fixes.append("contract_hash")
            
            if fixes and not dry_run:
                # Save fixed contract
                with open(path, 'w') as f:
                    json.dump(contract, f, indent=2, ensure_ascii=False)
                logger.info(f"✅ Fixed {qid}: {', '.join(fixes)}")
            
            results[qid] = {"fixes": fixes, "success": len(fixes) > 0}
        
        return results
    
    def _fix_patterns(self, contract: Dict, qid: str) -> bool:
        """Replace patterns with actual ones from monolith"""
        monolith_patterns = self.extractor.get_correct_patterns(qid)
        
        if not monolith_patterns: 
            return False
        
        # Update patterns in contract
        if "question_context" not in contract:
            contract["question_context"] = {}
        
        contract["question_context"]["patterns"] = monolith_patterns
        return True
    
    def _fix_identity_consistency(self, contract: Dict, qid:  str) -> bool:
        """Fix identity fields to match monolith and sync with output_contract"""
        correct_identity = self.extractor. get_correct_identity(qid)
        
        if not correct_identity:
            return False
        
        fixed = False
        
        # Update identity block
        for field, value in correct_identity.items():
            if value is not None:
                if contract.get("identity", {}).get(field) != value:
                    contract["identity"][field] = value
                    fixed = True
        
        # Sync with output_contract. schema.properties
        output_props = contract.get("output_contract", {}).get("schema", {}).get("properties", {})
        
        sync_fields = ["base_slot", "question_id", "question_global", "policy_area_id", 
                       "dimension_id", "cluster_id"]
        
        for field in sync_fields: 
            if field in output_props and "const" in output_props[field]: 
                correct_value = correct_identity.get(field)
                if correct_value is not None and output_props[field]["const"] != correct_value:
                    output_props[field]["const"] = correct_value
                    fixed = True
        
        return fixed
    
    def _fix_evidence_assembly(self, contract: Dict, qid: str) -> bool:
        """Fix evidence assembly sources using monolith mappings"""
        mapping = self.extractor.get_evidence_assembly_mapping(qid)
        
        if not mapping:
            # Use standard mappings
            mapping = {
                "text_mining.critical_links": "text_mining.diagnose_critical_links",
                "industrial_policy.processed_evidence": "industrial_policy.process",
                "causal_extraction.goals": "causal_extraction.extract_goals",
                "financial_audit. amounts": "financial_audit.parse_amount",
                "pdet_analysis.financial_data": "pdet_analysis.extract_financial_amounts",
                "contradiction_detection.quantitative_claims": "contradiction_detection.extract_quantitative_claims",
                "bayesian_analysis.policy_metrics": "bayesian_analysis.evaluate_policy_metric",
                "text_mining.patterns": "text_mining.diagnose_critical_links",
                "industrial_policy.patterns": "industrial_policy.match_patterns_in_sentences"
            }
        
        # Get available provides
        methods = contract.get("method_binding", {}).get("methods", [])
        available_provides = {m.get("provides") for m in methods if m.get("provides")}
        
        # Fix assembly rules
        assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
        fixed = False
        
        for rule in assembly_rules:
            new_sources = []
            for source in rule.get("sources", []):
                if source. startswith("*. "):
                    new_sources.append(source)
                elif source in mapping: 
                    # Use mapped value if it's available
                    mapped = mapping[source]
                    if mapped in available_provides: 
                        new_sources.append(mapped)
                        fixed = True
                elif source in available_provides:
                    new_sources.append(source)
                else:
                    # Try to find partial match
                    base = source.split(".")[0] if "." in source else source
                    for provides in available_provides:
                        if provides.startswith(base + "."):
                            new_sources.append(provides)
                            fixed = True
                            break
            
            if new_sources != rule.get("sources", []):
                rule["sources"] = new_sources
                fixed = True
        
        return fixed
    
    def _add_missing_structures(self, contract: Dict, qid: str) -> bool:
        """Add missing critical structures"""
        fixed = False
        
        # Add evidence_structure_post_nexus if using EvidenceNexus
        if contract.get("evidence_assembly", {}).get("class_name") == "EvidenceNexus":
            if "human_answer_structure" not in contract: 
                contract["human_answer_structure"] = {}
            
            has = contract["human_answer_structure"]
            
            if "evidence_structure_post_nexus" not in has:
                has["evidence_structure_post_nexus"] = {
                    "type": "graph",
                    "nodes": {
                        "text_mining": {"type": "source", "provides": ["critical_links", "patterns"]},
                        "industrial_policy": {"type": "source", "provides": ["processed_evidence", "patterns"]},
                        "causal_extraction": {"type":  "source", "provides": ["goals", "contexts"]},
                        "financial_audit": {"type": "source", "provides": ["amounts", "totals"]},
                        "bayesian_analysis": {"type": "analysis", "provides": ["metrics", "comparisons"]},
                        "semantic_processing": {"type": "processing", "provides": ["chunks", "embeddings"]},
                        "final_evidence": {"type": "sink", "aggregates": "all"}
                    },
                    "edges": [
                        {"from": "text_mining", "to": "final_evidence"},
                        {"from": "industrial_policy", "to": "final_evidence"},
                        {"from": "causal_extraction", "to": "final_evidence"},
                        {"from":  "financial_audit", "to":  "final_evidence"},
                        {"from": "bayesian_analysis", "to": "final_evidence"},
                        {"from": "semantic_processing", "to": "final_evidence"}
                    ]
                }
                fixed = True
        
        return fixed
    
    def _update_hash(self, contract: Dict) -> bool:
        """Update contract hash"""
        contract_copy = json.loads(json.dumps(contract))
        if "identity" in contract_copy:
            contract_copy["identity"]. pop("contract_hash", None)
            contract_copy["identity"].pop("updated_at", None)
        
        contract_str = json.dumps(contract_copy, sort_keys=True, ensure_ascii=False)
        new_hash = hashlib.sha256(contract_str.encode('utf-8')).hexdigest()
        
        current_hash = contract.get("identity", {}).get("contract_hash", "")
        
        if current_hash != new_hash: 
            contract["identity"]["contract_hash"] = new_hash
            contract["identity"]["updated_at"] = datetime.now(timezone.utc).isoformat()
            return True
        
        return False


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix contracts using monolith data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed")
    parser.add_argument("--analyze", action="store_true", help="Analyze monolith patterns")
    
    args = parser. parse_args()
    
    print("="*80)
    print("MONOLITH-BASED CONTRACT FIXER")
    print("="*80)
    
    # Load monolith
    extractor = MonolithExtractor()
    extractor.load_monolith()
    
    if args.analyze:
        # Analyze patterns in monolith
        print("\n📊 MONOLITH ANALYSIS")
        print("-"*40)
        
        pattern_stats = defaultdict(int)
        category_stats = defaultdict(set)
        
        for qid, patterns in extractor.pattern_map. items():
            pattern_stats[qid] = len(patterns)
            categories = set(p.get("category") for p in patterns if p.get("category"))
            category_stats[qid] = categories
        
        print(f"Total questions: {len(extractor.question_map)}")
        print(f"Average patterns per question: {sum(pattern_stats.values())/len(pattern_stats):.1f}")
        print(f"Questions with <5 patterns: {sum(1 for v in pattern_stats.values() if v < 5)}")
        print(f"Questions with 1 category: {sum(1 for v in category_stats.values() if len(v) == 1)}")
        print(f"Questions with 2 categories: {sum(1 for v in category_stats. values() if len(v) == 2)}")
        print(f"Questions with 3+ categories: {sum(1 for v in category_stats. values() if len(v) >= 3)}")
        
        # Show sample patterns
        print("\n📝 SAMPLE PATTERNS FROM MONOLITH")
        print("-"*40)
        for qid in ["Q001", "Q061", "Q091"]:
            patterns = extractor.pattern_map.get(qid, [])
            categories = set(p.get("category") for p in patterns if p. get("category"))
            print(f"\n{qid}: {len(patterns)} patterns, {len(categories)} categories")
            print(f"Categories: {categories}")
            for p in patterns[: 3]:
                print(f"  - {p.get('category', 'NONE')}: {p.get('pattern', '')[:50]}...")
    
    else:
        # Fix contracts
        print(f"\nMode: {'DRY RUN' if args.dry_run else 'APPLY FIXES'}")
        print(f"Monolith loaded: {len(extractor.question_map)} questions")
        
        fixer = SurgicalContractFixer(extractor)
        results = fixer.fix_all_contracts(dry_run=args.dry_run)
        
        # Summary
        total_fixed = sum(1 for r in results.values() if r["success"])
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total contracts processed: {len(results)}")
        print(f"Contracts fixed: {total_fixed}")
        
        # Show fix distribution
        fix_types = defaultdict(int)
        for r in results.values():
            for fix in r. get("fixes", []):
                fix_types[fix] += 1
        
        print("\nFixes applied:")
        for fix_type, count in sorted(fix_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {fix_type}: {count}")
        
        if not args.dry_run:
            print("\n✅ Fixes applied.  Run verification:")
            print("   python scripts/verify_contract_sync.py --all")
    
    return 0


if __name__ == "__main__":
    exit(main())