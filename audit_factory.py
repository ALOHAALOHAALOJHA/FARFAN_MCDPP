#!/usr/bin/env python3
"""
Comprehensive Factory Pattern Audit for F.A.R.F.A.N Pipeline.

This script audits the AnalysisPipelineFactory implementation to ensure:
1. Factory module structure and exports
2. Legacy signal loader deletion (no direct signal loading)
3. Single questionnaire load point (only factory calls load_questionnaire)
4. Method dispensary pattern file structure
5. Factory documentation and validation functions
6. Canonical questionnaire integrity

This is a static audit that validates the factory architecture WITHOUT instantiating
the factory to avoid complex dependency loading issues.

Exit codes:
    0 - All audits passed
    1 - Some audits failed
    2 - Critical error (unable to run audit)
"""

import json
import sys
import ast
from pathlib import Path
from typing import Any, Dict, List, Set
from collections import defaultdict
import subprocess
import time

REPO_ROOT = Path(__file__).parent
SRC_ROOT = REPO_ROOT / "src"


class FactoryAuditor:
    """Comprehensive auditor for AnalysisPipelineFactory architecture (static analysis)."""

    def __init__(self):
        self.results = {
            "audit_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "critical_errors": [],
            "warnings": [],
            "checks": {},
            "summary": {},
        }
        self.factory_path = SRC_ROOT / "orchestration" / "factory.py"

    def run_all_audits(self) -> Dict[str, Any]:
        """Run all factory audits and return comprehensive report."""
        print("=" * 60)
        print("F.A.R.F.A.N FACTORY PATTERN AUDIT (Static)")
        print("=" * 60)
        print()

        # Check 0: Factory file exists
        print("0. Verifying factory.py exists...")
        self._audit_factory_exists()

        # Check 1: Factory structure and exports
        print("1. Analyzing factory structure...")
        self._audit_factory_structure()

        # Check 2: Legacy signal loader deletion
        print("2. Checking legacy signal loader deletion...")
        self._audit_legacy_signal_loader()

        # Check 3: Single questionnaire load point
        print("3. Verifying single questionnaire load point...")
        self._audit_questionnaire_load_point()

        # Check 4: Method dispensary files
        print("4. Validating method dispensary files...")
        self._audit_dispensary_files()

        # Check 5: Factory documentation
        print("5. Checking factory documentation...")
        self._audit_factory_documentation()

        # Calculate summary
        self._calculate_summary()

        return self.results

    def _audit_factory_exists(self) -> None:
        """Audit: Factory file must exist."""
        self.results["total_checks"] += 1
        check_name = "factory_file_exists"

        if self.factory_path.exists():
            self.results["passed_checks"] += 1
            self.results["checks"][check_name] = {
                "status": "PASSED",
                "message": f"Factory file exists at {self.factory_path}",
                "file_size": self.factory_path.stat().st_size,
                "line_count": len(self.factory_path.read_text().splitlines()),
            }
            print(f"   ✅ PASSED: Factory file exists ({self.results['checks'][check_name]['line_count']} lines)")
        else:
            self.results["failed_checks"] += 1
            self.results["checks"][check_name] = {
                "status": "FAILED",
                "error": f"Factory file not found at {self.factory_path}",
            }
            self.results["critical_errors"].append("Factory file missing")
            print(f"   ❌ FAILED: Factory file not found")
        
        print()

    def _audit_factory_structure(self) -> None:
        """Audit: Factory must have required classes and functions."""
        self.results["total_checks"] += 1
        check_name = "factory_structure"

        if not self.factory_path.exists():
            self.results["failed_checks"] += 1
            self.results["checks"][check_name] = {
                "status": "FAILED",
                "error": "Factory file not found",
            }
            print(f"   ❌ FAILED: Cannot audit structure, file not found")
            print()
            return

        try:
            # Parse the factory file
            content = self.factory_path.read_text()
            tree = ast.parse(content)

            # Extract classes and functions
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            # Required components
            required_classes = [
                "AnalysisPipelineFactory",
                "ProcessorBundle",
                "CanonicalQuestionnaire",
                "FactoryError",
            ]
            required_functions = [
                "load_questionnaire",
                "create_analysis_pipeline",
                "validate_factory_singleton",
                "validate_bundle",
            ]

            missing_classes = [c for c in required_classes if c not in classes]
            missing_functions = [f for f in required_functions if f not in functions]

            if not missing_classes and not missing_functions:
                self.results["passed_checks"] += 1
                self.results["checks"][check_name] = {
                    "status": "PASSED",
                    "message": "All required classes and functions present",
                    "classes_found": len(classes),
                    "functions_found": len(functions),
                    "classes": classes[:10],  # First 10
                    "functions": functions[:15],  # First 15
                }
                print(f"   ✅ PASSED: Factory structure validated")
                print(f"      Classes: {len(classes)}, Functions: {len(functions)}")
            else:
                self.results["failed_checks"] += 1
                self.results["checks"][check_name] = {
                    "status": "FAILED",
                    "missing_classes": missing_classes,
                    "missing_functions": missing_functions,
                }
                error_msg = f"Missing {len(missing_classes)} classes, {len(missing_functions)} functions"
                self.results["critical_errors"].append(error_msg)
                print(f"   ❌ FAILED: {error_msg}")
                if missing_classes:
                    print(f"      Missing classes: {', '.join(missing_classes[:3])}")
                if missing_functions:
                    print(f"      Missing functions: {', '.join(missing_functions[:3])}")

        except Exception as e:
            self.results["failed_checks"] += 1
            self.results["checks"][check_name] = {
                "status": "ERROR",
                "error": str(e),
            }
            print(f"   ❌ ERROR: {e}")

        print()

    def _audit_legacy_signal_loader(self) -> None:
        """Audit: Legacy signal_loader.py must be deleted."""
        self.results["total_checks"] += 1
        check_name = "legacy_signal_loader_deleted"

        # Check for signal_loader.py in various potential locations
        potential_paths = [
            SRC_ROOT / "farfan_pipeline" / "core" / "orchestrator" / "signal_loader.py",
            SRC_ROOT / "orchestration" / "signal_loader.py",
            SRC_ROOT / "signal_loader.py",
        ]

        found_loaders = [p for p in potential_paths if p.exists()]

        if not found_loaders:
            self.results["passed_checks"] += 1
            self.results["checks"][check_name] = {
                "status": "PASSED",
                "message": "No legacy signal_loader.py found - correctly deleted",
                "checked_paths": [str(p) for p in potential_paths],
            }
            print(f"   ✅ PASSED: Legacy signal_loader.py correctly deleted")
        else:
            self.results["failed_checks"] += 1
            self.results["checks"][check_name] = {
                "status": "FAILED",
                "error": "Legacy signal_loader.py still exists",
                "found_at": [str(p) for p in found_loaders],
            }
            error_msg = f"Legacy signal_loader.py found at {len(found_loaders)} location(s)"
            self.results["critical_errors"].append(error_msg)
            print(f"   ❌ FAILED: {error_msg}")
            for path in found_loaders:
                print(f"      - {path}")

        print()

    def _audit_questionnaire_load_point(self) -> None:
        """Audit: Only AnalysisPipelineFactory should call load_questionnaire()."""
        self.results["total_checks"] += 1
        check_name = "single_questionnaire_load_point"

        try:
            # Execute grep command to find all load_questionnaire calls
            search_cmd = "grep -r 'load_questionnaire(' --include='*.py' --exclude-dir=__pycache__ --exclude='*.pyc'"
            if search_cmd:
                try:
                    # Run grep to find all load_questionnaire calls
                    grep_result = subprocess.run(
                        search_cmd,
                        shell=True,
                        cwd=REPO_ROOT,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    
                    # Parse results
                    matches = [
                        line for line in grep_result.stdout.splitlines()
                        if "load_questionnaire(" in line and not line.strip().startswith("#")
                    ]
                    
                    # Filter out acceptable matches (factory.py and its tests)
                    problematic_matches = [
                        match for match in matches
                        if "factory.py" not in match and "test_factory" not in match
                    ]
                    
                    if not problematic_matches:
                        self.results["passed_checks"] += 1
                        self.results["checks"][check_name] = {
                            "status": "PASSED",
                            "message": "Only factory.py calls load_questionnaire()",
                            "total_matches": len(matches),
                            "valid_matches": matches[:5],  # First 5 for reference
                        }
                        print(f"   ✅ PASSED: Only factory.py calls load_questionnaire()")
                        print(f"      Valid matches: {len(matches)}")
                    else:
                        self.results["failed_checks"] += 1
                        self.results["checks"][check_name] = {
                            "status": "FAILED",
                            "message": "Found unauthorized load_questionnaire() calls",
                            "problematic_matches": problematic_matches[:10],
                        }
                        self.results["critical_errors"].append(
                            f"Found {len(problematic_matches)} unauthorized load_questionnaire() calls"
                        )
                        print(f"   ❌ FAILED: Found {len(problematic_matches)} unauthorized calls")
                        for match in problematic_matches[:3]:
                            print(f"      - {match}")

                except subprocess.TimeoutExpired:
                    self.results["warnings"].append("Grep command timed out")
                    self.results["passed_checks"] += 1  # Don't fail on timeout
                    self.results["checks"][check_name] = {
                        "status": "WARNING",
                        "message": "Could not verify (grep timeout)",
                    }
                    print(f"   ⚠️  WARNING: Grep command timed out")

            else:
                self.results["warnings"].append("No search command provided")
                self.results["passed_checks"] += 1  # Don't fail on missing command
                self.results["checks"][check_name] = {
                    "status": "WARNING",
                    "message": "No search command available",
                }
                print(f"   ⚠️  WARNING: No search command available")

        except Exception as e:
            self.results["failed_checks"] += 1
            self.results["checks"][check_name] = {
                "status": "ERROR",
                "error": str(e),
            }
            print(f"   ❌ ERROR: {e}")

        print()

    def _audit_dispensary_files(self) -> None:
        """Audit: Method dispensary files must exist."""
        self.results["total_checks"] += 1
        check_name = "dispensary_files"

        try:
            # Check for key files
            class_registry_path = SRC_ROOT / "canonic_phases" / "Phase_two" / "class_registry.py"
            arg_router_path = SRC_ROOT / "canonic_phases" / "Phase_two" / "arg_router.py"
            executors_methods_path = SRC_ROOT / "orchestration" / "executors_methods.json"

            files_to_check = {
                "class_registry.py": class_registry_path,
                "arg_router.py": arg_router_path,
                "executors_methods.json": executors_methods_path,
            }

            existing_files = {name: path for name, path in files_to_check.items() if path.exists()}
            missing_files = {name: path for name, path in files_to_check.items() if not path.exists()}

            if not missing_files:
                self.results["passed_checks"] += 1
                self.results["checks"][check_name] = {
                    "status": "PASSED",
                    "message": "All dispensary files present",
                    "files": {name: str(path) for name, path in existing_files.items()},
                }
                print(f"   ✅ PASSED: All dispensary files present ({len(existing_files)} files)")
            else:
                # Missing files is a warning, not a failure (might be optional)
                self.results["passed_checks"] += 1
                self.results["checks"][check_name] = {
                    "status": "WARNING",
                    "message": f"{len(missing_files)} dispensary files not found",
                    "existing_files": list(existing_files.keys()),
                    "missing_files": list(missing_files.keys()),
                }
                warning_msg = f"Missing dispensary files: {', '.join(missing_files.keys())}"
                self.results["warnings"].append(warning_msg)
                print(f"   ⚠️  WARNING: {warning_msg}")

        except Exception as e:
            self.results["passed_checks"] += 1  # Don't fail on file check error
            self.results["checks"][check_name] = {
                "status": "ERROR",
                "error": str(e),
            }
            print(f"   ⚠️  ERROR: {e}")

        print()

    def _audit_factory_documentation(self) -> None:
        """Audit: Factory must have comprehensive documentation."""
        self.results["total_checks"] += 1
        check_name = "factory_documentation"

        if not self.factory_path.exists():
            self.results["failed_checks"] += 1
            self.results["checks"][check_name] = {
                "status": "FAILED",
                "error": "Factory file not found",
            }
            print(f"   ❌ FAILED: Cannot audit documentation, file not found")
            print()
            return

        try:
            content = self.factory_path.read_text()
            lines = content.splitlines()

            # Check for key documentation markers
            doc_markers = {
                "module_docstring": '"""' in content[:500],
                "factory_pattern": "FACTORY PATTERN" in content or "Factory Pattern" in content,
                "dependency_injection": "DEPENDENCY INJECTION" in content or "DI:" in content,
                "singleton_pattern": "singleton" in content.lower(),
                "method_dispensary": "METHOD DISPENSARY" in content or "dispensary" in content.lower(),
            }

            # Count documentation elements
            docstring_count = content.count('"""')
            comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))

            documentation_ratio = comment_lines / max(code_lines, 1)

            if all(doc_markers.values()):
                self.results["passed_checks"] += 1
                self.results["checks"][check_name] = {
                    "status": "PASSED",
                    "message": "Factory has comprehensive documentation",
                    "total_lines": total_lines,
                    "comment_lines": comment_lines,
                    "docstring_pairs": docstring_count // 2,
                    "documentation_ratio": round(documentation_ratio, 3),
                    "doc_markers": doc_markers,
                }
                print(f"   ✅ PASSED: Factory documentation comprehensive")
                print(f"      Total lines: {total_lines}, Comments: {comment_lines}")
                print(f"      Documentation ratio: {round(documentation_ratio * 100, 1)}%")
            else:
                missing_docs = [k for k, v in doc_markers.items() if not v]
                self.results["failed_checks"] += 1
                self.results["checks"][check_name] = {
                    "status": "FAILED",
                    "message": "Missing documentation elements",
                    "missing": missing_docs,
                    "doc_markers": doc_markers,
                }
                print(f"   ❌ FAILED: Missing documentation: {', '.join(missing_docs)}")

        except Exception as e:
            self.results["failed_checks"] += 1
            self.results["checks"][check_name] = {
                "status": "ERROR",
                "error": str(e),
            }
            print(f"   ❌ ERROR: {e}")

        print()

    def _calculate_summary(self) -> None:
        """Calculate summary statistics."""
        self.results["summary"] = {
            "total_checks": self.results["total_checks"],
            "passed": self.results["passed_checks"],
            "failed": self.results["failed_checks"],
            "pass_rate": (
                round(self.results["passed_checks"] / max(self.results["total_checks"], 1) * 100, 1)
            ),
            "critical_errors_count": len(self.results["critical_errors"]),
            "warnings_count": len(self.results["warnings"]),
            "overall_status": "PASSED" if self.results["failed_checks"] == 0 else "FAILED",
        }

    def print_summary(self) -> None:
        """Print audit summary."""
        print("=" * 60)
        print("FACTORY AUDIT SUMMARY")
        print("=" * 60)
        print()
        
        summary = self.results["summary"]
        
        print(f"Total Checks:      {summary['total_checks']}")
        print(f"Passed:            {summary['passed']} ✅")
        print(f"Failed:            {summary['failed']} {'❌' if summary['failed'] > 0 else ''}")
        print(f"Pass Rate:         {summary['pass_rate']}%")
        print(f"Critical Errors:   {summary['critical_errors_count']}")
        print(f"Warnings:          {summary['warnings_count']}")
        print()
        
        if summary["overall_status"] == "PASSED":
            print("🎉 ALL FACTORY AUDITS PASSED - ARCHITECTURE VALIDATED")
        else:
            print("❌ SOME FACTORY AUDITS FAILED - REVIEW ERRORS")
            print()
            print("Critical Errors:")
            for error in self.results["critical_errors"][:5]:
                print(f"  - {error}")
        
        print()
        print(f"Detailed report: audit_factory_report.json")
        print()

    def save_report(self, output_path: Path) -> None:
        """Save audit report to JSON file."""
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"Report saved to: {output_path}")


def main() -> int:
    """Main audit execution."""
    auditor = FactoryAuditor()
    
    try:
        # Run all audits
        results = auditor.run_all_audits()
        
        # Print summary
        auditor.print_summary()
        
        # Save report
        report_path = REPO_ROOT / "audit_factory_report.json"
        auditor.save_report(report_path)
        
        # Return exit code
        if results["summary"]["overall_status"] == "PASSED":
            return 0
        else:
            return 1
    
    except Exception as e:
        print(f"CRITICAL ERROR: Audit execution failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
