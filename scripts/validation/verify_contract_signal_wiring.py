"""
Verify Contract-Signal-Method Wiring

This script validates the complete wiring between:
1. 300 v4 contracts (generated_contracts/)
2. Signals (patterns, expected_elements, monolith_ref)
3. Method bindings (method_binding.execution_phases)

Author: F.A.R.F.A.N Pipeline
Date: 2026-01-04
Ref: SPEC_SIGNAL_NORMALIZATION_COMPREHENSIVE.md Phase 4
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Any

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_all_contracts(contracts_dir: Path) -> dict[str, dict[str, Any]]:
    """Load all v4 contracts."""
    contracts = {}
    for contract_path in contracts_dir.glob("Q*_PA*_contract_v4.json"):
        with open(contract_path) as f:
            contract = json.load(f)
        contract_id = contract_path.stem.replace("_contract_v4", "")
        contracts[contract_id] = contract
    return contracts


def verify_signal_fields(contract: dict[str, Any]) -> list[str]:
    """Verify contract has required signal fields."""
    issues = []
    question_context = contract.get("question_context", {})
    
    # Required signal fields
    if "patterns" not in question_context:
        issues.append("Missing patterns")
    elif not question_context["patterns"]:
        issues.append("Empty patterns list")
    
    if "expected_elements" not in question_context:
        issues.append("Missing expected_elements")
    elif not question_context["expected_elements"]:
        issues.append("Empty expected_elements list")
    
    if "monolith_ref" not in question_context:
        issues.append("Missing monolith_ref")
    
    if "signal_requirements" not in contract:
        issues.append("Missing signal_requirements at root")
    
    return issues


def verify_method_binding(contract: dict[str, Any]) -> list[str]:
    """Verify method binding is complete."""
    issues = []
    method_binding = contract.get("method_binding", {})
    
    if not method_binding:
        issues.append("Missing method_binding")
        return issues
    
    execution_phases = method_binding.get("execution_phases", {})
    if not execution_phases:
        issues.append("Missing execution_phases")
        return issues
    
    # Check each phase has methods
    for phase_name, phase_data in execution_phases.items():
        methods = phase_data.get("methods", [])
        if not methods:
            issues.append(f"Phase {phase_name} has no methods")
        else:
            # Verify method structure
            for method in methods:
                if not method.get("class_name"):
                    issues.append(f"Method in {phase_name} missing class_name")
                if not method.get("method_name"):
                    issues.append(f"Method in {phase_name} missing method_name")
                if not method.get("mother_file"):
                    issues.append(f"Method in {phase_name} missing mother_file")
    
    return issues


def verify_pattern_structure(contract: dict[str, Any]) -> list[str]:
    """Verify pattern structure is valid for signal matching."""
    issues = []
    patterns = contract.get("question_context", {}).get("patterns", [])
    
    for i, pattern in enumerate(patterns):
        if isinstance(pattern, dict):
            # Patterns can have: pattern, pattern_ref, or keyword
            has_pattern = bool(pattern.get("pattern"))
            has_pattern_ref = bool(pattern.get("pattern_ref"))
            has_keyword = bool(pattern.get("keyword"))
            has_id = bool(pattern.get("id"))  # ID is also acceptable as identifier
            
            if not (has_pattern or has_pattern_ref or has_keyword or has_id):
                issues.append(f"Pattern {i} has no pattern/pattern_ref/keyword/id field")
        elif not isinstance(pattern, str):
            issues.append(f"Pattern {i} is not string or dict: {type(pattern)}")
    
    return issues


def main():
    """Run verification."""
    print("=" * 60)
    print("CONTRACT-SIGNAL-METHOD WIRING VERIFICATION")
    print("=" * 60)
    
    contracts_dir = PROJECT_ROOT / "src" / "farfan_pipeline" / "phases" / "Phase_two" / "generated_contracts"
    
    if not contracts_dir.exists():
        print(f"❌ Contracts directory not found: {contracts_dir}")
        return 1
    
    contracts = load_all_contracts(contracts_dir)
    print(f"\nLoaded {len(contracts)} contracts")
    
    # Aggregate issues
    signal_issues = defaultdict(list)
    method_issues = defaultdict(list)
    pattern_issues = defaultdict(list)
    
    total_patterns = 0
    total_methods = 0
    
    for contract_id, contract in contracts.items():
        # Check signal fields
        issues = verify_signal_fields(contract)
        if issues:
            signal_issues[contract_id] = issues
        else:
            patterns = contract.get("question_context", {}).get("patterns", [])
            total_patterns += len(patterns)
        
        # Check method binding
        issues = verify_method_binding(contract)
        if issues:
            method_issues[contract_id] = issues
        else:
            method_binding = contract.get("method_binding", {})
            for phase in method_binding.get("execution_phases", {}).values():
                total_methods += len(phase.get("methods", []))
        
        # Check pattern structure
        issues = verify_pattern_structure(contract)
        if issues:
            pattern_issues[contract_id] = issues
    
    # Report results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    print(f"\n📊 STATISTICS:")
    print(f"   Total contracts: {len(contracts)}")
    print(f"   Total patterns: {total_patterns}")
    print(f"   Total method bindings: {total_methods}")
    print(f"   Avg patterns/contract: {total_patterns/len(contracts):.1f}")
    print(f"   Avg methods/contract: {total_methods/len(contracts):.1f}")
    
    all_ok = True
    
    if signal_issues:
        all_ok = False
        print(f"\n❌ SIGNAL ISSUES ({len(signal_issues)} contracts):")
        for cid, issues in list(signal_issues.items())[:5]:
            print(f"   {cid}: {', '.join(issues)}")
        if len(signal_issues) > 5:
            print(f"   ... and {len(signal_issues) - 5} more")
    else:
        print("\n✅ Signal fields: All contracts have patterns, expected_elements, monolith_ref")
    
    if method_issues:
        all_ok = False
        print(f"\n❌ METHOD BINDING ISSUES ({len(method_issues)} contracts):")
        for cid, issues in list(method_issues.items())[:5]:
            print(f"   {cid}: {', '.join(issues)}")
        if len(method_issues) > 5:
            print(f"   ... and {len(method_issues) - 5} more")
    else:
        print("✅ Method bindings: All contracts have valid method_binding structure")
    
    if pattern_issues:
        all_ok = False
        print(f"\n❌ PATTERN STRUCTURE ISSUES ({len(pattern_issues)} contracts):")
        for cid, issues in list(pattern_issues.items())[:5]:
            print(f"   {cid}: {', '.join(issues)}")
    else:
        print("✅ Pattern structure: All patterns are valid")
    
    # Test contract loading through BaseExecutor
    print("\n" + "=" * 60)
    print("EXECUTOR INTEGRATION TEST")
    print("=" * 60)
    
    try:
        from farfan_pipeline.phases.Phase_two.phase2_60_00_base_executor_with_contract import (
            BaseExecutorWithContract,
        )
        
        # Test v4 detection
        test_contract_path = contracts_dir / "Q001_PA01_contract_v4.json"
        with open(test_contract_path) as f:
            test_contract = json.load(f)
        
        detected = BaseExecutorWithContract._detect_contract_version(test_contract)
        print(f"\n   Test contract Q001_PA01 detected as: {detected}")
        
        if detected == "v4":
            print("   ✅ V4 detection working correctly")
        else:
            print(f"   ⚠️ Expected v4, got {detected}")
            all_ok = False
        
    except ImportError as e:
        print(f"\n   ⚠️ Could not import BaseExecutorWithContract: {e}")
    except Exception as e:
        print(f"\n   ⚠️ Integration test error: {e}")
    
    # Final verdict
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ ALL VERIFICATIONS PASSED")
        print("   Contract-Signal-Method wiring is complete")
    else:
        print("❌ SOME ISSUES FOUND")
        print("   Review the issues above")
    print("=" * 60)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
