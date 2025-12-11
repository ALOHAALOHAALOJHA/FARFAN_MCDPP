#!/usr/bin/env python3
"""
Executor Method Availability Audit

This script audits all executors to ensure they have complete method availability.
When methods are missing from the catalog, it suggests alternative methods from
the dispensary that could fulfill the same purpose based on the question context.

The goal is to ensure quality of method answers by guaranteeing full executor availability.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from collections import defaultdict
import ast

REPO_ROOT = Path(__file__).parent
SRC_ROOT = REPO_ROOT / "src"

class ExecutorMethodAuditor:
    """Auditor for executor method availability and suggestions."""

    def __init__(self):
        self.results = {
            "audit_timestamp": "",
            "total_executors": 0,
            "executors_with_missing_methods": 0,
            "total_missing_methods": 0,
            "missing_methods_by_executor": {},
            "suggested_replacements": {},
            "dispensary_methods": {},
            "summary": {},
        }
        
        # Load data
        self.executors_methods_path = SRC_ROOT / "canonic_phases" / "Phase_two" / "json_files_phase_two" / "executors_methods.json"
        self.validation_path = SRC_ROOT / "canonic_phases" / "Phase_two" / "json_files_phase_two" / "executor_factory_validation.json"
        self.dispensary_path = SRC_ROOT / "methods_dispensary"
        
        self.executors_methods = {}
        self.validation_data = {}
        self.dispensary_methods_catalog = {}

    def run_audit(self) -> Dict[str, Any]:
        """Run complete executor method audit."""
        print("=" * 80)
        print("EXECUTOR METHOD AVAILABILITY AUDIT")
        print("=" * 80)
        print()

        # Step 1: Load executor methods
        print("1. Loading executor method mappings...")
        self._load_executor_methods()

        # Step 2: Load validation results
        print("2. Loading validation failures...")
        self._load_validation_data()

        # Step 3: Scan dispensary for available methods
        print("3. Scanning methods dispensary...")
        self._scan_dispensary_methods()

        # Step 4: Identify missing methods per executor
        print("4. Identifying missing methods per executor...")
        self._identify_missing_methods()

        # Step 5: Suggest replacement methods
        print("5. Generating replacement suggestions...")
        self._suggest_replacements()

        # Step 6: Calculate summary
        self._calculate_summary()

        return self.results

    def _load_executor_methods(self) -> None:
        """Load executors_methods.json file."""
        if not self.executors_methods_path.exists():
            print(f"   ⚠️  WARNING: {self.executors_methods_path} not found")
            return

        try:
            with open(self.executors_methods_path) as f:
                data = json.load(f)
            
            # Build executor -> methods mapping
            for executor_info in data:
                executor_id = executor_info.get("executor_id")
                if executor_id:
                    self.executors_methods[executor_id] = executor_info
            
            print(f"   ✅ Loaded {len(self.executors_methods)} executor configurations")
            self.results["total_executors"] = len(self.executors_methods)
        
        except Exception as e:
            print(f"   ❌ ERROR loading executor methods: {e}")

    def _load_validation_data(self) -> None:
        """Load executor_factory_validation.json file."""
        if not self.validation_path.exists():
            print(f"   ⚠️  WARNING: {self.validation_path} not found")
            return

        try:
            with open(self.validation_path) as f:
                self.validation_data = json.load(f)
            
            failures = self.validation_data.get("failures", [])
            print(f"   ✅ Loaded validation data: {len(failures)} method failures")
            self.results["total_missing_methods"] = len(failures)
        
        except Exception as e:
            print(f"   ❌ ERROR loading validation data: {e}")

    def _scan_dispensary_methods(self) -> None:
        """Scan methods_dispensary folder for all available methods."""
        if not self.dispensary_path.exists():
            print(f"   ⚠️  WARNING: {self.dispensary_path} not found")
            return

        try:
            python_files = list(self.dispensary_path.glob("*.py"))
            total_methods = 0

            for py_file in python_files:
                if py_file.name.startswith("__"):
                    continue

                # Parse Python file to extract methods
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = node.name
                            methods = []

                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    method_name = item.name
                                    # Get docstring if available
                                    docstring = ast.get_docstring(item)
                                    methods.append({
                                        "name": method_name,
                                        "docstring": docstring[:100] if docstring else None,
                                        "is_private": method_name.startswith("_"),
                                    })

                            if methods:
                                if class_name not in self.dispensary_methods_catalog:
                                    self.dispensary_methods_catalog[class_name] = []
                                
                                self.dispensary_methods_catalog[class_name].extend(methods)
                                total_methods += len(methods)

                except SyntaxError:
                    print(f"   ⚠️  Syntax error in {py_file.name}")
                except Exception as e:
                    print(f"   ⚠️  Error parsing {py_file.name}: {e}")

            print(f"   ✅ Scanned dispensary: {len(self.dispensary_methods_catalog)} classes, {total_methods} methods")
            self.results["dispensary_methods"] = {
                class_name: len(methods) 
                for class_name, methods in self.dispensary_methods_catalog.items()
            }

        except Exception as e:
            print(f"   ❌ ERROR scanning dispensary: {e}")

    def _identify_missing_methods(self) -> None:
        """Identify which executors have missing methods."""
        failures = self.validation_data.get("failures", [])
        
        # Build map of missing methods by executor
        missing_by_executor = defaultdict(list)

        for executor_id, executor_info in self.executors_methods.items():
            methods = executor_info.get("methods", [])
            
            for method_info in methods:
                class_name = method_info.get("class")
                method_name = method_info.get("method")
                
                # Check if this method is in the failures list
                is_missing = any(
                    f.get("class") == class_name and f.get("method") == method_name
                    for f in failures
                )
                
                if is_missing:
                    missing_by_executor[executor_id].append({
                        "class": class_name,
                        "method": method_name,
                        "executor_question": executor_info.get("docstring", ""),
                    })

        self.results["missing_methods_by_executor"] = dict(missing_by_executor)
        self.results["executors_with_missing_methods"] = len(missing_by_executor)

        print(f"   ✅ Found {len(missing_by_executor)} executors with missing methods")
        
        # Print summary
        for executor_id, missing_methods in missing_by_executor.items():
            print(f"      {executor_id}: {len(missing_methods)} missing methods")

    def _suggest_replacements(self) -> None:
        """Suggest replacement methods from dispensary for missing methods."""
        suggestions = {}

        for executor_id, missing_methods in self.results["missing_methods_by_executor"].items():
            executor_suggestions = []

            for missing_method in missing_methods:
                class_name = missing_method["class"]
                method_name = missing_method["method"]
                question = missing_method["executor_question"]

                # Try to find similar methods in the same class
                suggested_methods = self._find_similar_methods(class_name, method_name, question)
                
                executor_suggestions.append({
                    "missing": {
                        "class": class_name,
                        "method": method_name,
                    },
                    "suggested_alternatives": suggested_methods,
                    "question_context": question,
                })

            if executor_suggestions:
                suggestions[executor_id] = executor_suggestions

        self.results["suggested_replacements"] = suggestions
        
        total_suggestions = sum(
            len(alt["suggested_alternatives"]) 
            for executor_suggestions in suggestions.values() 
            for alt in executor_suggestions
        )
        
        print(f"   ✅ Generated {total_suggestions} replacement suggestions")

    def _find_similar_methods(self, class_name: str, method_name: str, question: str) -> List[Dict[str, Any]]:
        """Find similar methods in the dispensary."""
        suggestions = []

        # Special high-quality replacements for known missing methods
        known_replacements = {
            ("FinancialAuditor", "_calculate_sufficiency"): [
                {
                    "class": "PDETMunicipalPlanAnalyzer",
                    "method": "_assess_financial_sustainability",
                    "similarity_score": 10,
                    "docstring": "Bayesian assessment of financial sustainability with risk inference",
                    "is_private": True,
                    "recommended": True,
                    "rationale": "Comprehensive sustainability analysis with Bayesian risk inference - superior to simple sufficiency check"
                }
            ],
            ("FinancialAuditor", "_detect_allocation_gaps"): [
                {
                    "class": "PDETMunicipalPlanAnalyzer",
                    "method": "_analyze_funding_sources",
                    "similarity_score": 10,
                    "docstring": "Comprehensive funding source gap analysis with territorial context",
                    "is_private": True,
                    "recommended": True,
                    "rationale": "Identifies funding gaps mapped to Colombian official systems (SGP, SGR)"
                }
            ],
            ("FinancialAuditor", "_match_goal_to_budget"): [
                {
                    "class": "PDETMunicipalPlanAnalyzer",
                    "method": "_extract_budget_for_pillar",
                    "similarity_score": 10,
                    "docstring": "Semantic matching of goals to budget allocations with confidence scoring",
                    "is_private": True,
                    "recommended": True,
                    "rationale": "Designed for PDET pillar-budget matching with semantic analysis"
                }
            ],
            ("PDETMunicipalPlanAnalyzer", "_generate_optimal_remediations"): [
                {
                    "class": "PDETMunicipalPlanAnalyzer",
                    "method": "_generate_optimal_remediations",
                    "similarity_score": 10,
                    "docstring": "Method EXISTS in dispensary - catalog needs update",
                    "is_private": True,
                    "recommended": True,
                    "rationale": "Method is available in financiero_viabilidad_tablas.py - no replacement needed"
                }
            ],
        }

        # Check for known high-quality replacements first
        replacement_key = (class_name, method_name)
        if replacement_key in known_replacements:
            suggestions.extend(known_replacements[replacement_key])
            # Still continue to find additional alternatives

        # Check if class exists in dispensary
        if class_name in self.dispensary_methods_catalog:
            all_methods = self.dispensary_methods_catalog[class_name]
            
            # Extract keywords from missing method name
            keywords = self._extract_keywords(method_name)
            
            # Score methods by similarity
            scored_methods = []
            for method in all_methods:
                # Skip the exact missing method
                if method["name"] == method_name:
                    continue
                
                # Calculate similarity score
                score = 0
                method_keywords = self._extract_keywords(method["name"])
                
                # Keyword overlap
                common_keywords = keywords & method_keywords
                score += len(common_keywords) * 3
                
                # Check if any keyword appears in docstring
                if method["docstring"]:
                    for keyword in keywords:
                        if keyword in method["docstring"].lower():
                            score += 1
                
                # Prefer public methods slightly
                if not method["is_private"]:
                    score += 0.5
                
                if score > 0:
                    scored_methods.append((score, method))
            
            # Sort by score and take top 3
            scored_methods.sort(key=lambda x: x[0], reverse=True)
            for score, method in scored_methods[:3]:
                suggestions.append({
                    "class": class_name,
                    "method": method["name"],
                    "similarity_score": score,
                    "docstring": method["docstring"],
                    "is_private": method["is_private"],
                })

        # Also check other classes for similar functionality
        for other_class, methods in self.dispensary_methods_catalog.items():
            if other_class == class_name:
                continue
            
            keywords = self._extract_keywords(method_name)
            
            for method in methods:
                score = 0
                method_keywords = self._extract_keywords(method["name"])
                
                # Higher threshold for different class
                common_keywords = keywords & method_keywords
                if len(common_keywords) >= 2:
                    score = len(common_keywords) * 2
                    
                    if method["docstring"]:
                        for keyword in keywords:
                            if keyword in method["docstring"].lower():
                                score += 1
                    
                    if score >= 3:  # Only suggest if highly relevant
                        suggestions.append({
                            "class": other_class,
                            "method": method["name"],
                            "similarity_score": score,
                            "docstring": method["docstring"],
                            "is_private": method["is_private"],
                            "different_class": True,
                        })

        # Sort all suggestions by score
        suggestions.sort(key=lambda x: x["similarity_score"], reverse=True)
        return suggestions[:5]  # Top 5 suggestions

    def _extract_keywords(self, name: str) -> Set[str]:
        """Extract meaningful keywords from a method name."""
        # Remove common prefixes
        name = name.lstrip("_")
        
        # Split by underscores and camelCase
        import re
        parts = re.sub(r'([A-Z])', r' \1', name).split()
        parts.extend(name.split("_"))
        
        # Common words to ignore
        stop_words = {"get", "set", "is", "has", "the", "a", "an", "and", "or", "for", "to", "from"}
        
        keywords = {
            part.lower() 
            for part in parts 
            if len(part) > 2 and part.lower() not in stop_words
        }
        
        return keywords

    def _calculate_summary(self) -> None:
        """Calculate summary statistics."""
        total_executors = self.results["total_executors"]
        executors_with_issues = self.results["executors_with_missing_methods"]
        
        self.results["summary"] = {
            "total_executors": total_executors,
            "healthy_executors": total_executors - executors_with_issues,
            "executors_with_issues": executors_with_issues,
            "total_missing_methods": self.results["total_missing_methods"],
            "total_suggestions_generated": sum(
                len(suggestions)
                for suggestions in self.results["suggested_replacements"].values()
            ),
            "health_percentage": round(
                (total_executors - executors_with_issues) / max(total_executors, 1) * 100, 1
            ) if total_executors > 0 else 0,
        }

    def print_summary(self) -> None:
        """Print audit summary."""
        print()
        print("=" * 80)
        print("EXECUTOR METHOD AUDIT SUMMARY")
        print("=" * 80)
        print()

        summary = self.results["summary"]
        
        print(f"Total Executors:              {summary['total_executors']}")
        print(f"Healthy Executors:            {summary['healthy_executors']} ✅")
        print(f"Executors with Issues:        {summary['executors_with_issues']} ⚠️")
        print(f"Total Missing Methods:        {summary['total_missing_methods']}")
        print(f"Replacement Suggestions:      {summary['total_suggestions_generated']}")
        print(f"Overall Health:               {summary['health_percentage']}%")
        print()

        if summary['executors_with_issues'] > 0:
            print("⚠️  ATTENTION REQUIRED:")
            print(f"   {summary['executors_with_issues']} executors have missing methods")
            print(f"   This may affect answer quality")
            print()
            print("   Detailed report: audit_executor_methods_report.json")
            print("   Check 'suggested_replacements' for alternative methods")
        else:
            print("🎉 ALL EXECUTORS HAVE COMPLETE METHOD AVAILABILITY")
        
        print()

    def save_report(self, output_path: Path) -> None:
        """Save audit report to JSON file."""
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"Detailed report saved to: {output_path}")


def main() -> int:
    """Main audit execution."""
    auditor = ExecutorMethodAuditor()
    
    try:
        # Run audit
        results = auditor.run_audit()
        
        # Print summary
        auditor.print_summary()
        
        # Save report
        report_path = REPO_ROOT / "audit_executor_methods_report.json"
        auditor.save_report(report_path)
        
        # Return exit code based on health
        if results["summary"]["executors_with_issues"] > 0:
            return 1  # Issues found
        else:
            return 0  # All good
    
    except Exception as e:
        print(f"CRITICAL ERROR: Audit execution failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
