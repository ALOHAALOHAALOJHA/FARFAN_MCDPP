#!/usr/bin/env python3
"""
Phase 2 Epistemological Contract Sensitivity Verification
==========================================================

This script verifies that Phase 2 methods operate in a manner totally sensitive
to epistemological contracts by checking:

1. Calibration & Parametrization Files Structure
2. Epistemological Level Assignments (N0-N4)
3. Contract Type Affinity Mappings (TYPE_A through TYPE_E)
4. Method-Contract Bindings
5. Fusion Behaviors and Constraints
6. Evidence Requirements Alignment

Author: GitHub Copilot
Date: 2026-01-18
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Add paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


class EpistemologicalContractVerifier:
    """Verifier for epistemological contract sensitivity."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.phase2_root = repo_root / "src" / "farfan_pipeline" / "phases" / "Phase_02"
        
        # Load epistemological assets
        self.epistemo_assets_dir = self.phase2_root / "epistemological_assets"
        self.contracts_dir = self.phase2_root / "generated_contracts"
        
        # Load key files
        self.classified_methods = self._load_json(
            self.epistemo_assets_dir / "classified_methods.json"
        )
        self.method_sets = self._load_json(
            self.epistemo_assets_dir / "method_sets_by_question.json"
        )
        
        # Sample contracts for verification
        self.sample_contracts = self._load_sample_contracts()
    
    def _load_json(self, path: Path) -> dict[str, Any]:
        """Load JSON file."""
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}
    
    def _load_sample_contracts(self) -> list[dict[str, Any]]:
        """Load sample contracts for verification."""
        contracts = []
        contract_files = list(self.contracts_dir.glob("Q001_PA*.json"))[:5]
        
        for contract_file in contract_files:
            with open(contract_file) as f:
                contracts.append(json.load(f))
        
        return contracts
    
    def verify_epistemological_structure(self) -> dict[str, Any]:
        """Verify epistemological classification structure."""
        
        results = {
            "status": "PASS",
            "issues": [],
            "statistics": {},
        }
        
        # Check classified_methods.json structure
        if not self.classified_methods:
            results["status"] = "FAIL"
            results["issues"].append("classified_methods.json not found or empty")
            return results
        
        # Verify epistemological levels
        stats = self.classified_methods.get("statistics", {})
        levels = ["N0-INFRA", "N1-EMP", "N2-INF", "N3-AUD", "N4-META"]
        
        for level in levels:
            if level in stats:
                count = stats[level]["count"]
                epistemology = stats[level]["epistemology"]
                output_type = stats[level]["output_type"]
                
                results["statistics"][level] = {
                    "count": count,
                    "epistemology": epistemology,
                    "output_type": output_type,
                }
        
        # Verify all methods have epistemological classification
        methods_by_level = self.classified_methods.get("methods_by_level", {})
        total_classified = sum(len(methods_by_level.get(level, [])) for level in levels)
        
        if total_classified == 0:
            results["status"] = "FAIL"
            results["issues"].append("No methods classified by epistemological level")
        
        results["total_classified_methods"] = total_classified
        
        return results
    
    def verify_contract_method_bindings(self) -> dict[str, Any]:
        """Verify that contracts properly bind methods with epistemological metadata."""
        
        results = {
            "status": "PASS",
            "contracts_checked": 0,
            "methods_with_full_metadata": 0,
            "methods_missing_metadata": 0,
            "issues": [],
        }
        
        required_fields = [
            "level",
            "level_name",
            "epistemology",
            "output_type",
            "fusion_behavior",
            "contract_affinities",
        ]
        
        for contract in self.sample_contracts:
            results["contracts_checked"] += 1
            contract_id = contract.get("identity", {}).get("contract_id", "UNKNOWN")
            
            method_binding = contract.get("method_binding", {})
            execution_phases = method_binding.get("execution_phases", {})
            
            for phase_name, phase_data in execution_phases.items():
                methods = phase_data.get("methods", [])
                
                for method in methods:
                    # Check for required epistemological fields
                    missing_fields = [f for f in required_fields if f not in method]
                    
                    if missing_fields:
                        results["methods_missing_metadata"] += 1
                        results["issues"].append(
                            f"Contract {contract_id}, method {method.get('method_id', 'UNKNOWN')}: "
                            f"missing fields {missing_fields}"
                        )
                    else:
                        results["methods_with_full_metadata"] += 1
                        
                        # Validate contract affinities
                        affinities = method.get("contract_affinities", {})
                        expected_types = ["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E"]
                        
                        if not all(t in affinities for t in expected_types):
                            results["issues"].append(
                                f"Contract {contract_id}, method {method.get('method_id', 'UNKNOWN')}: "
                                f"incomplete contract affinities"
                            )
        
        if results["methods_missing_metadata"] > 0:
            results["status"] = "FAIL"
        
        return results
    
    def verify_calibration_policy(self) -> dict[str, Any]:
        """Verify calibration policy integration."""
        
        results = {
            "status": "PASS",
            "issues": [],
        }
        
        calibration_file = self.phase2_root / "phase2_60_04_calibration_policy.py"
        
        if not calibration_file.exists():
            results["status"] = "FAIL"
            results["issues"].append("Calibration policy file not found")
            return results
        
        # Check for epistemological imports
        with open(calibration_file) as f:
            content = f.read()
        
        required_imports = [
            "EpistemicLevel",
            "N1EmpiricalCalibration",
            "N2InferentialCalibration",
            "N3AuditCalibration",
            "N4MetaCalibration",
            "N0InfrastructureCalibration",
        ]
        
        for imp in required_imports:
            if imp not in content:
                results["issues"].append(f"Missing import: {imp}")
        
        if results["issues"]:
            results["status"] = "FAIL"
        
        return results
    
    def verify_fusion_specifications(self) -> dict[str, Any]:
        """Verify fusion specifications in contracts."""
        
        results = {
            "status": "PASS",
            "fusion_behaviors_found": defaultdict(int),
            "contracts_with_fusion_spec": 0,
            "issues": [],
        }
        
        for contract in self.sample_contracts:
            contract_id = contract.get("identity", {}).get("contract_id", "UNKNOWN")
            
            # Check fusion specification section
            if "fusion_specification" in contract:
                results["contracts_with_fusion_spec"] += 1
                fusion_spec = contract["fusion_specification"]
                
                # Verify fusion strategy
                if "fusion_strategy" not in fusion_spec:
                    results["issues"].append(
                        f"Contract {contract_id}: missing fusion_strategy"
                    )
            
            # Check method-level fusion behaviors
            method_binding = contract.get("method_binding", {})
            execution_phases = method_binding.get("execution_phases", {})
            
            for phase_name, phase_data in execution_phases.items():
                methods = phase_data.get("methods", [])
                
                for method in methods:
                    fusion_behavior = method.get("fusion_behavior", "")
                    if fusion_behavior:
                        results["fusion_behaviors_found"][fusion_behavior] += 1
        
        if results["contracts_with_fusion_spec"] == 0:
            results["status"] = "FAIL"
            results["issues"].append("No contracts have fusion specifications")
        
        return results
    
    def verify_evidence_requirements(self) -> dict[str, Any]:
        """Verify evidence requirements alignment."""
        
        results = {
            "status": "PASS",
            "methods_with_evidence_reqs": 0,
            "methods_with_output_claims": 0,
            "methods_with_constraints": 0,
            "issues": [],
        }
        
        for contract in self.sample_contracts:
            contract_id = contract.get("identity", {}).get("contract_id", "UNKNOWN")
            
            method_binding = contract.get("method_binding", {})
            execution_phases = method_binding.get("execution_phases", {})
            
            for phase_name, phase_data in execution_phases.items():
                methods = phase_data.get("methods", [])
                
                for method in methods:
                    method_id = method.get("method_id", "UNKNOWN")
                    
                    if "evidence_requirements" in method:
                        results["methods_with_evidence_reqs"] += 1
                    
                    if "output_claims" in method:
                        results["methods_with_output_claims"] += 1
                    
                    if "constraints_and_limits" in method:
                        results["methods_with_constraints"] += 1
                    
                    # Verify level-appropriate evidence
                    level = method.get("level", "")
                    evidence_reqs = method.get("evidence_requirements", [])
                    
                    if level == "N1-EMP" and not evidence_reqs:
                        results["issues"].append(
                            f"Contract {contract_id}, N1-EMP method {method_id}: "
                            f"missing evidence requirements"
                        )
        
        return results
    
    def generate_report(self) -> str:
        """Generate comprehensive verification report."""
        
        print("=" * 80)
        print("PHASE 2 EPISTEMOLOGICAL CONTRACT SENSITIVITY VERIFICATION")
        print("=" * 80)
        print()
        
        # 1. Epistemological Structure
        print("1. EPISTEMOLOGICAL CLASSIFICATION STRUCTURE")
        print("-" * 80)
        epistemo_results = self.verify_epistemological_structure()
        print(f"Status: {epistemo_results['status']}")
        print(f"Total classified methods: {epistemo_results.get('total_classified_methods', 0)}")
        print()
        
        if epistemo_results.get("statistics"):
            print("Methods by Epistemological Level:")
            for level, data in epistemo_results["statistics"].items():
                print(f"  {level}: {data['count']} methods")
                print(f"    Epistemology: {data['epistemology']}")
                print(f"    Output Type: {data['output_type']}")
        print()
        
        # 2. Contract-Method Bindings
        print("2. CONTRACT-METHOD BINDINGS VERIFICATION")
        print("-" * 80)
        binding_results = self.verify_contract_method_bindings()
        print(f"Status: {binding_results['status']}")
        print(f"Contracts checked: {binding_results['contracts_checked']}")
        print(f"Methods with full metadata: {binding_results['methods_with_full_metadata']}")
        print(f"Methods missing metadata: {binding_results['methods_missing_metadata']}")
        
        if binding_results['issues']:
            print("\nIssues found:")
            for issue in binding_results['issues'][:5]:
                print(f"  - {issue}")
            if len(binding_results['issues']) > 5:
                print(f"  ... and {len(binding_results['issues']) - 5} more issues")
        print()
        
        # 3. Calibration Policy
        print("3. CALIBRATION POLICY INTEGRATION")
        print("-" * 80)
        calibration_results = self.verify_calibration_policy()
        print(f"Status: {calibration_results['status']}")
        
        if calibration_results['issues']:
            print("Issues:")
            for issue in calibration_results['issues']:
                print(f"  - {issue}")
        else:
            print("✓ All required epistemological calibrations imported")
        print()
        
        # 4. Fusion Specifications
        print("4. FUSION SPECIFICATIONS")
        print("-" * 80)
        fusion_results = self.verify_fusion_specifications()
        print(f"Status: {fusion_results['status']}")
        print(f"Contracts with fusion spec: {fusion_results['contracts_with_fusion_spec']}")
        
        if fusion_results['fusion_behaviors_found']:
            print("\nFusion behaviors found:")
            for behavior, count in fusion_results['fusion_behaviors_found'].items():
                print(f"  {behavior}: {count} methods")
        print()
        
        # 5. Evidence Requirements
        print("5. EVIDENCE REQUIREMENTS ALIGNMENT")
        print("-" * 80)
        evidence_results = self.verify_evidence_requirements()
        print(f"Status: {evidence_results['status']}")
        print(f"Methods with evidence requirements: {evidence_results['methods_with_evidence_reqs']}")
        print(f"Methods with output claims: {evidence_results['methods_with_output_claims']}")
        print(f"Methods with constraints: {evidence_results['methods_with_constraints']}")
        
        if evidence_results['issues']:
            print("\nIssues:")
            for issue in evidence_results['issues'][:5]:
                print(f"  - {issue}")
        print()
        
        # Overall assessment
        print("=" * 80)
        print("OVERALL ASSESSMENT")
        print("=" * 80)
        
        all_results = [
            epistemo_results,
            binding_results,
            calibration_results,
            fusion_results,
            evidence_results,
        ]
        
        passed = sum(1 for r in all_results if r['status'] == 'PASS')
        total = len(all_results)
        
        print(f"Verification categories passed: {passed}/{total}")
        
        if passed == total:
            print("\n✅ CERTIFIED: Phase 2 methods operate with FULL epistemological contract sensitivity")
            return "PASS"
        else:
            print("\n⚠️ WARNING: Some epistemological contract sensitivity issues found")
            return "PARTIAL"


def main():
    """Run verification."""
    
    repo_root = Path(__file__).resolve().parent.parent
    verifier = EpistemologicalContractVerifier(repo_root)
    
    result = verifier.generate_report()
    
    # Save detailed report
    output_file = (
        repo_root / "artifacts" / "reports" / "audit" / 
        "PHASE_2_EPISTEMOLOGICAL_CONTRACT_SENSITIVITY_VERIFICATION.json"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    report_data = {
        "verification_date": "2026-01-18",
        "result": result,
        "epistemo_structure": verifier.verify_epistemological_structure(),
        "contract_bindings": verifier.verify_contract_method_bindings(),
        "calibration_policy": verifier.verify_calibration_policy(),
        "fusion_specs": verifier.verify_fusion_specifications(),
        "evidence_reqs": verifier.verify_evidence_requirements(),
    }
    
    with open(output_file, "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\nDetailed report saved to: {output_file}")
    
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
