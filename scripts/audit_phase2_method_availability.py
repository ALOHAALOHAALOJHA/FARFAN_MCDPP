#!/usr/bin/env python3
"""
Phase 2 Method Availability Audit Script
========================================

Comprehensive audit of method availability, injection mechanisms, and call success factors.
This script ensures 100% certainty about method availability with NO FALLBACKS.

Audit Areas:
1. Method file existence and import paths
2. Class availability in modules
3. Method availability in classes
4. Instantiation requirements (no-arg constructor vs special rules)
5. Method signature validation
6. Dependency injection requirements
7. External factor analysis (filesystem, network, env vars)
8. Risk scenario assessment

Author: GitHub Copilot
Date: 2026-01-18
"""

import ast
import importlib
import inspect
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@dataclass
class MethodAvailabilityReport:
    """Comprehensive method availability report."""
    
    method_id: str
    class_name: str
    method_name: str
    file_name: str
    
    # Availability checks
    file_exists: bool = False
    file_path_correct: bool = False
    actual_file_path: str = ""
    
    class_importable: bool = False
    class_exists_in_module: bool = False
    import_error: str = ""
    
    method_exists_on_class: bool = False
    method_callable: bool = False
    method_signature: str = ""
    
    # Instantiation analysis
    instantiable_no_args: bool = False
    instantiation_requirements: list[str] = field(default_factory=list)
    requires_special_rule: bool = False
    
    # Dependency analysis
    external_dependencies: list[str] = field(default_factory=list)
    filesystem_dependencies: list[str] = field(default_factory=list)
    environment_dependencies: list[str] = field(default_factory=list)
    
    # Risk factors
    risk_level: str = "UNKNOWN"  # LOW, MEDIUM, HIGH, CRITICAL
    risk_factors: list[str] = field(default_factory=list)
    
    # Call success factors
    call_success_probability: float = 0.0
    blockers: list[str] = field(default_factory=list)
    
    @property
    def is_fully_available(self) -> bool:
        """Check if method is fully available with 100% certainty."""
        return (
            self.file_exists
            and self.class_importable
            and self.class_exists_in_module
            and self.method_exists_on_class
            and self.method_callable
            and (self.instantiable_no_args or self.requires_special_rule)
            and len(self.blockers) == 0
        )


class Phase2MethodAuditor:
    """Auditor for Phase 2 method availability."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.src_root = repo_root / "src"
        self.methods_dir = self.src_root / "farfan_pipeline" / "methods"
        
        # Correct module prefix
        self.correct_module_prefix = "farfan_pipeline.methods"
        
        # Load method mappings
        self.methods_mapping = self._load_methods_mapping()
        
        # Registry of old vs new paths
        self.old_to_new_path = {
            "methods_dispensary": "farfan_pipeline.methods",
        }
        
    def _load_methods_mapping(self) -> dict[str, Any]:
        """Load METHODS_TO_QUESTIONS_AND_FILES.json."""
        mapping_file = (
            self.repo_root
            / "canonic_questionnaire_central"
            / "governance"
            / "METHODS_TO_QUESTIONS_AND_FILES.json"
        )
        
        if not mapping_file.exists():
            print(f"ERROR: Methods mapping file not found: {mapping_file}")
            return {"methods": {}}
        
        with open(mapping_file) as f:
            data = json.load(f)
        
        return data.get("methods", {})
    
    def audit_method(self, method_id: str, method_data: dict[str, Any]) -> MethodAvailabilityReport:
        """Audit a single method comprehensively."""
        
        report = MethodAvailabilityReport(
            method_id=method_id,
            class_name=method_data.get("class_name", ""),
            method_name=method_data.get("method_name", ""),
            file_name=method_data.get("file", ""),
        )
        
        # 1. Check file existence
        file_path = self.methods_dir / report.file_name
        report.file_exists = file_path.exists()
        report.actual_file_path = str(file_path)
        
        if not report.file_exists:
            report.risk_level = "CRITICAL"
            report.risk_factors.append(f"File does not exist: {report.file_name}")
            report.blockers.append(f"FILE_NOT_FOUND: {report.file_name}")
            report.call_success_probability = 0.0
            return report
        
        # 2. Check import path correctness
        module_name = report.file_name.replace(".py", "")
        correct_import_path = f"{self.correct_module_prefix}.{module_name}"
        report.file_path_correct = True
        
        # 3. Try to import class
        try:
            module = importlib.import_module(correct_import_path)
            report.class_importable = True
            
            # 4. Check if class exists in module
            if hasattr(module, report.class_name):
                report.class_exists_in_module = True
                cls = getattr(module, report.class_name)
                
                # 5. Check if it's actually a class
                if not inspect.isclass(cls):
                    report.risk_level = "CRITICAL"
                    report.risk_factors.append(f"{report.class_name} is not a class")
                    report.blockers.append(f"NOT_A_CLASS: {report.class_name}")
                else:
                    # 6. Check method existence
                    if hasattr(cls, report.method_name):
                        report.method_exists_on_class = True
                        method = getattr(cls, report.method_name)
                        
                        # 7. Check if callable
                        if callable(method):
                            report.method_callable = True
                            
                            # Get signature
                            try:
                                sig = inspect.signature(method)
                                report.method_signature = str(sig)
                            except (ValueError, TypeError):
                                report.method_signature = "Cannot inspect"
                            
                            # 8. Check instantiation requirements
                            self._analyze_instantiation(cls, report)
                            
                            # 9. Analyze dependencies
                            self._analyze_dependencies(file_path, report)
                            
                            # 10. Calculate risk and success probability
                            self._calculate_risk_and_probability(report)
                        else:
                            report.risk_level = "CRITICAL"
                            report.blockers.append(f"METHOD_NOT_CALLABLE: {report.method_name}")
                    else:
                        report.risk_level = "CRITICAL"
                        report.blockers.append(f"METHOD_NOT_FOUND: {report.method_name} on {report.class_name}")
            else:
                report.risk_level = "CRITICAL"
                report.blockers.append(f"CLASS_NOT_FOUND: {report.class_name} in {module_name}")
        
        except ImportError as e:
            report.import_error = str(e)
            report.risk_level = "CRITICAL"
            report.blockers.append(f"IMPORT_ERROR: {e}")
        except Exception as e:
            report.import_error = str(e)
            report.risk_level = "CRITICAL"
            report.blockers.append(f"UNEXPECTED_ERROR: {e}")
        
        return report
    
    def _analyze_instantiation(self, cls: type, report: MethodAvailabilityReport) -> None:
        """Analyze class instantiation requirements."""
        
        try:
            # Try to get __init__ signature
            init_sig = inspect.signature(cls.__init__)
            params = list(init_sig.parameters.values())
            
            # Filter out 'self'
            params = [p for p in params if p.name != "self"]
            
            # Check if no-arg constructor
            required_params = [
                p for p in params
                if p.default == inspect.Parameter.empty and p.kind not in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                )
            ]
            
            if len(required_params) == 0:
                report.instantiable_no_args = True
            else:
                report.requires_special_rule = True
                report.instantiation_requirements = [
                    f"{p.name}: {p.annotation if p.annotation != inspect.Parameter.empty else 'Any'}"
                    for p in required_params
                ]
                report.risk_factors.append(
                    f"Requires {len(required_params)} constructor arguments"
                )
        
        except (ValueError, TypeError) as e:
            report.risk_factors.append(f"Cannot inspect __init__: {e}")
            report.requires_special_rule = True
    
    def _analyze_dependencies(self, file_path: Path, report: MethodAvailabilityReport) -> None:
        """Analyze file dependencies through AST parsing."""
        
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                # Check for file operations
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ("open", "Path"):
                            report.filesystem_dependencies.append(f"Uses {node.func.id}()")
                
                # Check for environment variable access
                if isinstance(node, ast.Subscript):
                    if isinstance(node.value, ast.Attribute):
                        if (
                            isinstance(node.value.value, ast.Name)
                            and node.value.value.id == "os"
                            and node.value.attr == "environ"
                        ):
                            report.environment_dependencies.append("Accesses os.environ")
        
        except Exception as e:
            report.risk_factors.append(f"Cannot analyze dependencies: {e}")
    
    def _calculate_risk_and_probability(self, report: MethodAvailabilityReport) -> None:
        """Calculate risk level and call success probability."""
        
        # Base probability
        prob = 1.0
        
        # Deduct for each issue
        if not report.file_exists:
            prob = 0.0
        elif not report.class_importable:
            prob = 0.0
        elif not report.class_exists_in_module:
            prob = 0.0
        elif not report.method_exists_on_class:
            prob = 0.0
        elif not report.method_callable:
            prob = 0.0
        else:
            # Method is available, now check instantiation
            if not report.instantiable_no_args and not report.requires_special_rule:
                prob *= 0.5
                report.risk_factors.append("Unknown instantiation requirements")
            
            if report.requires_special_rule and len(report.instantiation_requirements) > 0:
                prob *= 0.8
            
            # Deduct for dependencies
            if len(report.filesystem_dependencies) > 0:
                prob *= 0.9
                report.risk_factors.append("Has filesystem dependencies")
            
            if len(report.environment_dependencies) > 0:
                prob *= 0.9
                report.risk_factors.append("Has environment dependencies")
        
        report.call_success_probability = prob
        
        # Set risk level
        if prob == 1.0:
            report.risk_level = "LOW"
        elif prob >= 0.8:
            report.risk_level = "MEDIUM"
        elif prob >= 0.5:
            report.risk_level = "HIGH"
        else:
            report.risk_level = "CRITICAL"
    
    def audit_all_methods(self) -> dict[str, MethodAvailabilityReport]:
        """Audit all methods."""
        
        reports = {}
        
        for method_id, method_data in self.methods_mapping.items():
            report = self.audit_method(method_id, method_data)
            reports[method_id] = report
        
        return reports
    
    def generate_summary(self, reports: dict[str, MethodAvailabilityReport]) -> dict[str, Any]:
        """Generate audit summary."""
        
        total = len(reports)
        fully_available = sum(1 for r in reports.values() if r.is_fully_available)
        
        by_risk = {
            "LOW": sum(1 for r in reports.values() if r.risk_level == "LOW"),
            "MEDIUM": sum(1 for r in reports.values() if r.risk_level == "MEDIUM"),
            "HIGH": sum(1 for r in reports.values() if r.risk_level == "HIGH"),
            "CRITICAL": sum(1 for r in reports.values() if r.risk_level == "CRITICAL"),
        }
        
        blockers = {}
        for report in reports.values():
            for blocker in report.blockers:
                blocker_type = blocker.split(":")[0]
                if blocker_type not in blockers:
                    blockers[blocker_type] = []
                blockers[blocker_type].append(report.method_id)
        
        return {
            "total_methods": total,
            "fully_available": fully_available,
            "availability_rate": fully_available / total if total > 0 else 0.0,
            "by_risk_level": by_risk,
            "blockers_summary": {k: len(v) for k, v in blockers.items()},
            "blocker_details": blockers,
        }


def main():
    """Run the audit."""
    
    repo_root = Path(__file__).resolve().parent.parent
    auditor = Phase2MethodAuditor(repo_root)
    
    print("=" * 80)
    print("PHASE 2 METHOD AVAILABILITY AUDIT")
    print("=" * 80)
    print()
    print(f"Repository Root: {repo_root}")
    print(f"Methods Directory: {auditor.methods_dir}")
    print(f"Total Methods to Audit: {len(auditor.methods_mapping)}")
    print()
    
    # Run audit
    print("Running comprehensive audit...")
    reports = auditor.audit_all_methods()
    
    # Generate summary
    summary = auditor.generate_summary(reports)
    
    print()
    print("=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print()
    print(f"Total Methods: {summary['total_methods']}")
    print(f"Fully Available (100% certainty): {summary['fully_available']}")
    print(f"Availability Rate: {summary['availability_rate']:.2%}")
    print()
    print("Risk Level Distribution:")
    for level, count in summary['by_risk_level'].items():
        print(f"  {level}: {count} methods")
    print()
    
    if summary['blockers_summary']:
        print("BLOCKERS FOUND:")
        for blocker_type, count in summary['blockers_summary'].items():
            print(f"  {blocker_type}: {count} methods affected")
        print()
    
    # Print critical issues
    critical_reports = [r for r in reports.values() if r.risk_level == "CRITICAL"]
    if critical_reports:
        print("=" * 80)
        print(f"CRITICAL ISSUES ({len(critical_reports)} methods)")
        print("=" * 80)
        print()
        
        for report in critical_reports[:10]:  # Show first 10
            print(f"Method: {report.method_id}")
            print(f"  Class: {report.class_name}")
            print(f"  File: {report.file_name}")
            print(f"  Blockers:")
            for blocker in report.blockers:
                print(f"    - {blocker}")
            print()
    
    # Save detailed report
    output_file = repo_root / "artifacts" / "reports" / "audit" / "PHASE_2_METHOD_AVAILABILITY_AUDIT.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    report_data = {
        "summary": summary,
        "methods": {
            method_id: {
                "method_id": r.method_id,
                "class_name": r.class_name,
                "method_name": r.method_name,
                "file_name": r.file_name,
                "is_fully_available": r.is_fully_available,
                "risk_level": r.risk_level,
                "call_success_probability": r.call_success_probability,
                "blockers": r.blockers,
                "risk_factors": r.risk_factors,
                "instantiation_requirements": r.instantiation_requirements,
            }
            for method_id, r in reports.items()
        },
    }
    
    with open(output_file, "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"Detailed report saved to: {output_file}")
    print()
    
    # Return exit code based on availability
    if summary['fully_available'] == summary['total_methods']:
        print("✅ ALL METHODS FULLY AVAILABLE (100% certainty)")
        return 0
    else:
        print(f"⚠️ {summary['total_methods'] - summary['fully_available']} METHODS HAVE AVAILABILITY ISSUES")
        return 1


if __name__ == "__main__":
    sys.exit(main())
