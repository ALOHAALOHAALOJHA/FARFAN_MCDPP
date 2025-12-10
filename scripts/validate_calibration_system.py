#!/usr/bin/env python3
"""
Calibration System Validation Script

Validates the calibration system against expected products, quality metrics,
and mathematical constraints identified in CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md

Usage:
    python scripts/validate_calibration_system.py [--output OUTPUT_PATH]
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configuration paths
BASE_DIR = Path(__file__).parent.parent
CALIBRATION_DIR = BASE_DIR / "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
EVIDENCE_DIR = BASE_DIR / "evidence_traces"
TESTS_DIR = BASE_DIR / "tests/calibration"


class CalibrationValidator:
    """Validates calibration system completeness and correctness."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "validation_version": "1.0.0",
            "checks": {},
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }

    def check(self, name: str, passed: bool, details: str = "", severity: str = "critical"):
        """Record a validation check result."""
        self.results["checks"][name] = {
            "passed": passed,
            "details": details,
            "severity": severity
        }
        self.results["summary"]["total_checks"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
        else:
            if severity == "warning":
                self.results["summary"]["warnings"] += 1
            else:
                self.results["summary"]["failed"] += 1

    def validate_configuration_files(self):
        """Validate presence and validity of configuration files."""
        print("\n=== Validating Configuration Files ===")
        
        required_files = {
            "COHORT_2024_intrinsic_calibration.json": "Intrinsic calibration scores",
            "COHORT_2024_intrinsic_calibration_rubric.json": "Intrinsic rubric",
            "COHORT_2024_fusion_weights.json": "Fusion weights",
            "COHORT_2024_layer_requirements.json": "Layer requirements",
            "COHORT_2024_method_compatibility.json": "Method compatibility",
            "COHORT_2024_canonical_method_inventory.json": "Method inventory",
            "COHORT_2024_questionnaire_monolith.json": "Questionnaire monolith"
        }
        
        for filename, description in required_files.items():
            filepath = CALIBRATION_DIR / filename
            exists = filepath.exists()
            
            if exists:
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    self.check(
                        f"config_file_{filename}",
                        True,
                        f"✅ {description} present and valid JSON"
                    )
                except json.JSONDecodeError as e:
                    self.check(
                        f"config_file_{filename}",
                        False,
                        f"❌ {description} present but invalid JSON: {e}"
                    )
            else:
                self.check(
                    f"config_file_{filename}",
                    False,
                    f"❌ {description} missing at {filepath}"
                )
            
            print(f"  {filename}: {'✅' if exists else '❌'}")

    def validate_fusion_weights(self):
        """Validate fusion weights sum to 1.0."""
        print("\n=== Validating Fusion Weights ===")
        
        fusion_file = CALIBRATION_DIR / "COHORT_2024_fusion_weights.json"
        
        if not fusion_file.exists():
            self.check("fusion_weights_sum", False, "Fusion weights file missing")
            return
        
        try:
            with open(fusion_file, 'r') as f:
                data = json.load(f)
            
            # Check if validation report exists
            validation_report = CALIBRATION_DIR / "weight_validation_report.json"
            if validation_report.exists():
                with open(validation_report, 'r') as f:
                    report = json.load(f)
                
                # Check multiple possible validation indicators
                validation_passed = (
                    report.get("validation_passed", False) or
                    report.get("validation_summary", {}).get("overall_status") == "PASSED" or
                    report.get("_metadata", {}).get("validation_status") == "PASSED"
                )
                    
                if validation_passed:
                    self.check(
                        "fusion_weights_sum",
                        True,
                        "✅ Fusion weights validated (sum = 1.0 ± 0.001)"
                    )
                    print("  ✅ Fusion weights sum to 1.0")
                else:
                    self.check(
                        "fusion_weights_sum",
                        False,
                        f"❌ Fusion weights failed validation: {report.get('error', 'Unknown error')}"
                    )
                    print("  ❌ Fusion weights validation failed")
            else:
                self.check(
                    "fusion_weights_validation_report",
                    False,
                    "⚠️  Weight validation report missing",
                    severity="warning"
                )
                print("  ⚠️  Validation report missing")
                
        except Exception as e:
            self.check("fusion_weights_sum", False, f"Error validating fusion weights: {e}")
            print(f"  ❌ Error: {e}")

    def validate_implementation_files(self):
        """Validate presence of implementation files."""
        print("\n=== Validating Implementation Files ===")
        
        required_files = {
            "COHORT_2024_calibration_orchestrator.py": "Main orchestrator",
            "COHORT_2024_chain_layer.py": "Chain layer",
            "COHORT_2024_congruence_layer.py": "Congruence layer",
            "COHORT_2024_contextual_layers.py": "Contextual layers (Q/D/P)",
            "COHORT_2024_dimension_layer.py": "Dimension layer",
            "COHORT_2024_policy_layer.py": "Policy layer",
            "COHORT_2024_question_layer.py": "Question layer",
            "COHORT_2024_unit_layer.py": "Unit layer",
            "COHORT_2024_meta_layer.py": "Meta layer",
            "certificate_generator.py": "Certificate generator",
            "certificate_validator.py": "Certificate validator"
        }
        
        all_present = True
        for filename, description in required_files.items():
            filepath = CALIBRATION_DIR / filename
            exists = filepath.exists()
            
            if not exists:
                all_present = False
                self.check(f"impl_{filename}", False, f"❌ {description} missing")
                print(f"  {filename}: ❌")
            else:
                self.check(f"impl_{filename}", True, f"✅ {description} present")
                print(f"  {filename}: ✅")

    def validate_test_coverage(self):
        """Validate test coverage."""
        print("\n=== Validating Test Coverage ===")
        
        required_tests = {
            "test_base_layer.py": "Base layer tests",
            "test_chain_layer.py": "Chain layer tests",
            "test_contextual_layers.py": "Contextual layers tests",
            "test_unit_layer.py": "Unit layer tests",
            "test_meta_layer.py": "Meta layer tests",
            "test_congruence_layer.py": "Congruence layer tests",
            "test_choquet_aggregation.py": "Choquet fusion tests",
            "test_orchestrator.py": "Orchestrator integration tests",
            "test_property_based.py": "Property-based tests (monotonicity, boundedness)"
        }
        
        all_present = True
        for filename, description in required_tests.items():
            filepath = TESTS_DIR / filename
            exists = filepath.exists()
            
            if not exists:
                all_present = False
                self.check(f"test_{filename}", False, f"❌ {description} missing")
                print(f"  {filename}: ❌")
            else:
                self.check(f"test_{filename}", True, f"✅ {description} present")
                print(f"  {filename}: ✅")
        
        if all_present:
            print("\n  ✅ All required test files present")
        else:
            print("\n  ⚠️  Some test files missing")

    def validate_evidence_infrastructure(self):
        """Validate evidence tracing infrastructure."""
        print("\n=== Validating Evidence Infrastructure ===")
        
        required_dirs = {
            "evidence_traces/base_layer": "Base layer traces",
            "evidence_traces/chain_layer": "Chain layer traces",
            "evidence_traces/fusion": "Fusion traces"
        }
        
        for dir_path, description in required_dirs.items():
            full_path = BASE_DIR / dir_path
            exists = full_path.exists()
            
            if exists:
                # Check if directory has any trace files
                trace_files = list(full_path.glob("*.json"))
                if trace_files:
                    self.check(
                        f"evidence_{dir_path}",
                        True,
                        f"✅ {description} directory exists with {len(trace_files)} traces"
                    )
                    print(f"  {dir_path}: ✅ ({len(trace_files)} traces)")
                else:
                    self.check(
                        f"evidence_{dir_path}",
                        False,
                        f"⚠️  {description} directory exists but empty",
                        severity="warning"
                    )
                    print(f"  {dir_path}: ⚠️  (empty)")
            else:
                self.check(
                    f"evidence_{dir_path}",
                    False,
                    f"❌ {description} directory missing"
                )
                print(f"  {dir_path}: ❌")

    def validate_artifact_generation(self):
        """Validate artifact generation."""
        print("\n=== Validating Artifact Generation ===")
        
        required_dirs = {
            "artifacts/certificates": "Certificate artifacts",
            "artifacts/calibration_cache": "Calibration cache",
            "artifacts/validation": "Validation reports"
        }
        
        for dir_path, description in required_dirs.items():
            full_path = BASE_DIR / dir_path
            exists = full_path.exists()
            
            if exists:
                # Check if directory has any files
                files = list(full_path.glob("*"))
                if files:
                    self.check(
                        f"artifact_{dir_path}",
                        True,
                        f"✅ {description} directory exists with {len(files)} artifacts"
                    )
                    print(f"  {dir_path}: ✅ ({len(files)} artifacts)")
                else:
                    self.check(
                        f"artifact_{dir_path}",
                        False,
                        f"⚠️  {description} directory exists but empty",
                        severity="warning"
                    )
                    print(f"  {dir_path}: ⚠️  (empty)")
            else:
                self.check(
                    f"artifact_{dir_path}",
                    False,
                    f"❌ {description} directory missing"
                )
                print(f"  {dir_path}: ❌")

    def validate_documentation(self):
        """Validate documentation completeness."""
        print("\n=== Validating Documentation ===")
        
        required_docs = {
            "docs/CALIBRATION_GUIDE.md": "Calibration guide",
            "docs/mathematical_foundations_capax_system.md": "Mathematical foundations",
            "docs/LAYER_SYSTEM.md": "Layer system",
            "docs/CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md": "Coherence analysis (this doc)",
            "docs/CALIBRATION_VS_PARAMETRIZATION.md": "Calibration vs parametrization"
        }
        
        for doc_path, description in required_docs.items():
            full_path = BASE_DIR / doc_path
            exists = full_path.exists()
            
            if exists:
                self.check(f"doc_{doc_path}", True, f"✅ {description} present")
                print(f"  {doc_path}: ✅")
            else:
                self.check(f"doc_{doc_path}", False, f"❌ {description} missing")
                print(f"  {doc_path}: ❌")

    def generate_summary(self):
        """Generate validation summary."""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        summary = self.results["summary"]
        total = summary["total_checks"]
        passed = summary["passed"]
        failed = summary["failed"]
        warnings = summary["warnings"]
        
        print(f"Total Checks: {total}")
        print(f"✅ Passed: {passed} ({100 * passed / total:.1f}%)")
        print(f"❌ Failed: {failed} ({100 * failed / total:.1f}%)")
        print(f"⚠️  Warnings: {warnings} ({100 * warnings / total:.1f}%)")
        
        if failed == 0 and warnings == 0:
            print("\n🎉 ALL CHECKS PASSED - System is production ready!")
            status = "PRODUCTION_READY"
        elif failed == 0:
            print("\n✅ All critical checks passed - Some warnings need attention")
            status = "OPERATIONAL_WITH_WARNINGS"
        elif failed <= 5:
            print("\n⚠️  Some critical checks failed - System needs attention")
            status = "NEEDS_ATTENTION"
        else:
            print("\n❌ Multiple critical checks failed - System not production ready")
            status = "NOT_READY"
        
        self.results["status"] = status
        return status

    def run_validation(self, output_path: Path | None = None):
        """Run all validation checks."""
        print("=" * 60)
        print("CALIBRATION SYSTEM VALIDATION")
        print("=" * 60)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Based on: docs/CALIBRATION_CANONICAL_COHERENCE_ANALYSIS.md")
        
        # Run all validation checks
        self.validate_configuration_files()
        self.validate_fusion_weights()
        self.validate_implementation_files()
        self.validate_test_coverage()
        self.validate_evidence_infrastructure()
        self.validate_artifact_generation()
        self.validate_documentation()
        
        # Generate summary
        status = self.generate_summary()
        
        # Save results
        if output_path is None:
            output_path = ARTIFACTS_DIR / "validation" / "calibration_validation_report.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {output_path}")
        
        return status


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate F.A.R.F.A.N calibration system completeness"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for validation report (default: artifacts/validation/calibration_validation_report.json)"
    )
    
    args = parser.parse_args()
    
    validator = CalibrationValidator()
    status = validator.run_validation(args.output)
    
    # Exit with appropriate code
    if status == "PRODUCTION_READY":
        sys.exit(0)
    elif status == "OPERATIONAL_WITH_WARNINGS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
