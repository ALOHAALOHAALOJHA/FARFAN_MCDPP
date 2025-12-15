#!/usr/bin/env python3
"""
Critical Issues Fixer for Contract Groups
==========================================

Fixes the three critical issues:
1. Method-evidence misalignment
2. Missing method_outputs section
3. Contract hash mismatches
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONTRACTS_DIR = Path("src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized")

class CriticalIssueFixer:
    """Fixes critical contract issues"""
    
    def __init__(self):
        self.fixes_applied = {}
    
    def fix_contract_group(self, group_id: int, dry_run: bool = False) -> Dict[str, Any]:
        """Fix all contracts in a group"""
        # Get question IDs for group
        base = group_id + 1
        question_ids = [f"Q{base + (i * 30):03d}" for i in range(10)]
        
        logger.info(f"Processing group {group_id}: {question_ids[0]}... {question_ids[-1]}")
        
        results = {}
        for qid in question_ids:
            path = CONTRACTS_DIR / f"{qid}.v3.json"
            if not path.exists():
                logger.warning(f"Contract {qid} not found")
                continue
            
            # Load contract
            with open(path, 'r') as f:
                contract = json.load(f)
            
            # Apply fixes
            fixes = []
            
            # Fix 0: Identity consistency (dimension_id.const, cluster_id.const)
            if self._fix_identity_consistency(contract):
                fixes.append("identity_consistency")
            
            # Fix 1: Method-evidence alignment
            if self._fix_method_evidence_alignment(contract):
                fixes.append("method_evidence_alignment")
            
            # Fix 2: Add method_outputs if missing
            if self._fix_missing_method_outputs(contract):
                fixes.append("method_outputs")
            
            # Fix 3: Fix contract hash
            if self._fix_contract_hash(contract):
                fixes.append("contract_hash")
            
            if fixes and not dry_run:
                # Save fixed contract
                with open(path, 'w') as f:
                    json. dump(contract, f, indent=2, ensure_ascii=False)
                logger.info(f"✅ Fixed {qid}: {', '.join(fixes)}")
            elif fixes:
                logger.info(f"[DRY RUN] Would fix {qid}: {', '.join(fixes)}")
            
            results[qid] = {
                "fixes_applied": fixes,
                "success": len(fixes) > 0
            }
        
        return results
    
    def _fix_method_evidence_alignment(self, contract: Dict) -> bool:
        """Fix unmapped assembly sources"""
        # Get available provides from methods
        methods = contract. get("method_binding", {}).get("methods", [])
        available_provides = {m. get("provides") for m in methods if m.get("provides")}
        
        # Check and fix assembly rules
        assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
        
        fixed = False
        for rule in assembly_rules:
            original_sources = rule.get("sources", []).copy()
            cleaned_sources = []
            
            for source in original_sources: 
                if source.startswith("*. "):
                    # Keep wildcard patterns
                    cleaned_sources.append(source)
                else:
                    # Check if source maps to a method
                    # Handle both full paths and base paths
                    if "." in source:
                        base_source = ". ".join(source.split(".")[:2])
                    else:
                        base_source = source
                    
                    # Check if this source or its base exists in provides
                    if source in available_provides: 
                        cleaned_sources.append(source)
                    elif base_source in available_provides: 
                        cleaned_sources.append(source)
                    else:
                        # Try to map common mismatches
                        mapped = self._map_common_source(source, available_provides)
                        if mapped:
                            cleaned_sources.append(mapped)
                            fixed = True
                        else: 
                            # Source doesn't map, remove it
                            logger.debug(f"Removing unmapped source: {source}")
                            fixed = True
            
            if cleaned_sources != original_sources: 
                rule["sources"] = cleaned_sources
                fixed = True
        
        return fixed
    
    def _map_common_source(self, source: str, available_provides: Set[str]) -> str:
        """Map common source mismatches"""
        # Common mappings
        mappings = {
            "text_mining.critical_links":  "text_mining.diagnose_critical_links",
            "industrial_policy.processed_evidence": "industrial_policy.process",
            "causal_extraction.goals": "causal_extraction.extract_goals",
            "financial_audit.amounts": "financial_audit.parse_amount",
            "pdet_analysis.financial_data": "pdet_analysis.extract_financial_amounts",
            "contradiction_detection.quantitative_claims": "contradiction_detection.extract_quantitative_claims",
            "bayesian_analysis.policy_metrics": "bayesian_analysis.evaluate_policy_metric",
            "text_mining.patterns": "text_mining.diagnose_critical_links",
            "industrial_policy.patterns": "industrial_policy.match_patterns_in_sentences"
        }
        
        if source in mappings and mappings[source] in available_provides:
            return mappings[source]
        
        return None
    
    def _fix_missing_method_outputs(self, contract: Dict) -> bool:
        """Add method_outputs section if missing"""
        if "method_outputs" in contract:
            return False
        
        methods = contract.get("method_binding", {}).get("methods", [])
        
        # Generate comprehensive method_outputs
        method_outputs = {}
        
        for method in methods:
            class_name = method.get("class_name", "")
            method_name = method.get("method_name", "")
            provides = method.get("provides", "")
            
            if provides:
                full_name = f"{class_name}.{method_name}"
                method_outputs[full_name] = {
                    "output_type": "dict",
                    "structure": {
                        "description":  f"Output from {full_name}",
                        "type": "object",
                        "properties": self._get_method_output_properties(class_name, method_name)
                    },
                    "validation": {
                        "required": True,
                        "non_empty": True
                    },
                    "usage_in_assembly": {
                        "provides_key": provides,
                        "merge_strategy": "concat" if "extract" in method_name else "replace"
                    }
                }
        
        contract["method_outputs"] = method_outputs
        return True
    
    def _get_method_output_properties(self, class_name: str, method_name: str) -> Dict:
        """Get expected output properties for a method"""
        # Define expected outputs for each method type
        output_templates = {
            "TextMiningEngine": {
                "diagnose_critical_links": {
                    "critical_links":  {"type": "array", "description": "List of critical causal links"},
                    "link_scores": {"type": "object", "description": "Criticality scores for each link"},
                    "context":  {"type": "object", "description": "Contextual information"}
                },
                "_analyze_link_text": {
                    "context_coherence_score": {"type": "number"},
                    "supporting_evidence": {"type": "array"},
                    "contradicting_evidence": {"type": "array"}
                }
            },
            "IndustrialPolicyProcessor": {
                "process": {
                    "extracted_segments": {"type": "object"},
                    "pattern_matches": {"type": "object"},
                    "structural_completeness": {"type": "number"}
                },
                "_match_patterns_in_sentences": {
                    "sentence_matches": {"type": "array"}
                },
                "_extract_point_evidence": {
                    "evidence_points": {"type": "array"}
                }
            },
            "CausalExtractor": {
                "_extract_goals": {
                    "goals": {"type": "array", "description": "Extracted policy goals"}
                },
                "_parse_goal_context": {
                    "goal_contexts": {"type": "object", "description": "Contextual information for goals"}
                }
            },
            "FinancialAuditor": {
                "_parse_amount": {
                    "amounts": {"type": "array", "description": "Parsed financial amounts"},
                    "total":  {"type": "number"}
                }
            },
            "PDETMunicipalPlanAnalyzer": {
                "_extract_financial_amounts": {
                    "financial_amounts": {"type": "array"}
                },
                "_extract_from_budget_table": {
                    "budget_items": {"type": "array"}
                }
            },
            "PolicyContradictionDetector": {
                "_extract_quantitative_claims": {
                    "quantitative_claims": {"type": "array"}
                },
                "_parse_number":  {
                    "parsed_value": {"type": "number"},
                    "original_text": {"type": "string"}
                },
                "_statistical_significance_test": {
                    "p_value": {"type": "number"},
                    "is_significant": {"type": "boolean"}
                }
            },
            "BayesianNumericalAnalyzer": {
                "evaluate_policy_metric": {
                    "metric_value": {"type": "number"},
                    "confidence":  {"type": "number"},
                    "posterior_distribution": {"type": "object"}
                },
                "compare_policies": {
                    "comparison_result": {"type": "object"},
                    "winner":  {"type": "string"},
                    "confidence":  {"type": "number"}
                }
            },
            "SemanticProcessor": {
                "chunk_text": {
                    "chunks": {"type": "array", "description": "Text chunks"}
                },
                "embed_single":  {
                    "embedding": {"type": "array", "description": "Vector embedding"}
                }
            }
        }
        
        # Return template if exists, otherwise generic
        if class_name in output_templates and method_name in output_templates[class_name]:
            return output_templates[class_name][method_name]
        
        # Generic template
        return {
            "result": {"type": "object", "description": f"Result from {method_name}"},
            "metadata": {"type": "object", "description": "Execution metadata"}
        }
    
    def _fix_contract_hash(self, contract: Dict) -> bool:
        """Recompute and update contract hash"""
        # Store current hash
        current_hash = contract.get("identity", {}).get("contract_hash", "")
        
        # Compute correct hash
        contract_copy = json.loads(json.dumps(contract))
        if "identity" in contract_copy: 
            contract_copy["identity"]. pop("contract_hash", None)
            contract_copy["identity"]. pop("updated_at", None)
        
        contract_str = json.dumps(contract_copy, sort_keys=True, ensure_ascii=False)
        computed_hash = hashlib.sha256(contract_str.encode('utf-8')).hexdigest()
        
        # Update if different
        if current_hash != computed_hash: 
            contract["identity"]["contract_hash"] = computed_hash
            contract["identity"]["updated_at"] = datetime.now(timezone.utc).isoformat()
            return True
        
        return False


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix critical contract issues")
    parser.add_argument("--group", type=int, help="Specific group to fix (0-29)")
    parser.add_argument("--all", action="store_true", help="Fix all groups")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without applying")
    
    args = parser.parse_args()
    
    print("="*80)
    print("CRITICAL ISSUE FIXER")
    print("="*80)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLY FIXES'}")
    
    fixer = CriticalIssueFixer()
    
    if args.all:
        groups = range(30)
    elif args.group is not None:
        groups = [args.group]
    else:
        groups = [0]  # Default to group 0
    
    total_fixes = 0
    for group_id in groups:
        print(f"\n📋 Processing Group {group_id}...")
        results = fixer.fix_contract_group(group_id, dry_run=args.dry_run)
        
        group_fixes = sum(1 for r in results.values() if r["success"])
        total_fixes += group_fixes
        
        if group_fixes > 0:
            print(f"✅ Fixed {group_fixes} contracts in group {group_id}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total contracts fixed: {total_fixes}")
    
    if not args.dry_run:
        print("\n💡 Run verification to confirm fixes:")
        print(f"   python scripts/verify_contract_sync.py --group {groups[0] if len(groups) == 1 else '--all'}")
    
    return 0


if __name__ == "__main__":
    exit(main())