#!/usr/bin/env python3
"""
Comprehensive audit of 300 executor contracts for completeness, alignment, and signal wiring.

This script audits all contracts in src/farfan_pipeline.phases/Phase_two/json_files_phase_two/executor_contracts/specialized/
to ensure:
1. Completeness and disaggregation of all required fields per v3 schema
2. Alignment with base_executor_with_contract.py requirements
3. Proper wiring between EvidenceAssembler, EvidenceRegistry, and EvidenceValidator
4. Correct signal irrigation and synchronization flow
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from collections import defaultdict

# Base requirements from base_executor_with_contract.py
V3_REQUIRED_TOP_LEVEL_FIELDS = [
    "identity",
    "executor_binding",
    "method_binding",
    "question_context",
    "evidence_assembly",
    "validation_rules",
    "error_handling",
]

V3_IDENTITY_FIELDS = [
    "base_slot",
    "question_id",
    "dimension_id",
    "policy_area_id",
    "contract_version",
]

V3_METHOD_BINDING_FIELDS = [
    "orchestration_mode",
]

V3_EVIDENCE_ASSEMBLY_FIELDS = [
    "assembly_rules",
]

V3_ERROR_HANDLING_FIELDS = [
    "failure_contract",
    "on_method_failure",
]

# Signal irrigation requirements
SIGNAL_REQUIREMENTS_FIELDS = [
    "mandatory_signals",
    "optional_signals",
    "minimum_signal_threshold",
]

# Assembly rule requirements for EvidenceAssembler
ASSEMBLY_RULE_FIELDS = [
    "target",
    "sources",
    "merge_strategy",
]

# Validation rule requirements for EvidenceValidator
VALIDATION_RULE_FIELDS = [
    "field",
    "required",
]


class ContractAuditor:
    """Auditor for executor contracts completeness and alignment."""

    def __init__(self, contracts_dir: Path):
        self.contracts_dir = contracts_dir
        self.results = {
            "total_contracts": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "warnings": [],
            "stats": defaultdict(int),
        }

    def audit_all_contracts(self) -> Dict[str, Any]:
        """Audit all contracts in the directory."""
        contract_files = sorted(self.contracts_dir.glob("Q*.v3.json"))
        self.results["total_contracts"] = len(contract_files)

        print(f"Auditing {len(contract_files)} contracts...")

        for contract_file in contract_files:
            self._audit_single_contract(contract_file)

        # Calculate summary statistics
        self._calculate_summary_stats()

        return self.results

    def _audit_single_contract(self, contract_file: Path) -> None:
        """Audit a single contract file."""
        contract_id = contract_file.stem

        try:
            with open(contract_file, "r", encoding="utf-8") as f:
                contract = json.load(f)
        except json.JSONDecodeError as e:
            self.results["failed"] += 1
            self.results["errors"].append(f"[{contract_id}] Invalid JSON: {e}")
            return
        except Exception as e:
            self.results["failed"] += 1
            self.results["errors"].append(f"[{contract_id}] Failed to read file: {e}")
            return

        # Audit checks
        errors = []
        warnings = []

        # 1. Check v3 top-level completeness
        errors.extend(self._check_top_level_fields(contract, contract_id))

        # 2. Check identity section
        errors.extend(self._check_identity_section(contract, contract_id))

        # 3. Check method_binding completeness and disaggregation
        errors.extend(self._check_method_binding(contract, contract_id))

        # 4. Check evidence_assembly alignment with EvidenceAssembler
        errors.extend(self._check_evidence_assembly(contract, contract_id))

        # 5. Check validation_rules alignment with EvidenceValidator
        warnings.extend(self._check_validation_rules(contract, contract_id))

        # 6. Check signal_requirements for irrigation
        errors.extend(self._check_signal_requirements(contract, contract_id))

        # 7. Check error_handling for failure_contract wiring
        errors.extend(self._check_error_handling(contract, contract_id))

        # 8. Check question_context completeness
        errors.extend(self._check_question_context(contract, contract_id))

        # Store results
        if errors:
            self.results["failed"] += 1
            self.results["errors"].extend(errors)
        else:
            self.results["passed"] += 1

        if warnings:
            self.results["warnings"].extend(warnings)

        # Update statistics
        self._update_stats(contract)

    def _check_top_level_fields(self, contract: Dict, contract_id: str) -> List[str]:
        """Check that all v3 top-level fields are present."""
        errors = []
        for field in V3_REQUIRED_TOP_LEVEL_FIELDS:
            if field not in contract:
                errors.append(f"[{contract_id}] Missing required top-level field: {field}")
        return errors

    def _check_identity_section(self, contract: Dict, contract_id: str) -> List[str]:
        """Check identity section completeness."""
        errors = []
        identity = contract.get("identity", {})

        for field in V3_IDENTITY_FIELDS:
            if field not in identity:
                errors.append(f"[{contract_id}] Missing identity field: {field}")

        # Verify base_slot matches expected format
        if "base_slot" in identity:
            base_slot = identity["base_slot"]
            if not base_slot or not base_slot.startswith("D"):
                errors.append(f"[{contract_id}] Invalid base_slot format: {base_slot}")

        return errors

    def _check_method_binding(self, contract: Dict, contract_id: str) -> List[str]:
        """Check method_binding completeness and disaggregation."""
        errors = []
        method_binding = contract.get("method_binding", {})

        for field in V3_METHOD_BINDING_FIELDS:
            if field not in method_binding:
                errors.append(f"[{contract_id}] Missing method_binding field: {field}")

        orchestration_mode = method_binding.get("orchestration_mode")

        if orchestration_mode == "multi_method_pipeline":
            # Check methods array exists and is properly disaggregated
            if "methods" not in method_binding:
                errors.append(
                    f"[{contract_id}] Missing 'methods' array for multi_method_pipeline mode"
                )
            elif not isinstance(method_binding["methods"], list):
                errors.append(f"[{contract_id}] 'methods' must be a list")
            else:
                methods = method_binding["methods"]
                if not methods:
                    errors.append(f"[{contract_id}] Empty methods array")

                # Check disaggregation of each method
                for idx, method_spec in enumerate(methods):
                    if not isinstance(method_spec, dict):
                        errors.append(f"[{contract_id}] methods[{idx}] is not a dict")
                        continue

                    # Required method fields
                    for req_field in ["class_name", "method_name", "provides", "priority"]:
                        if req_field not in method_spec:
                            errors.append(f"[{contract_id}] methods[{idx}] missing '{req_field}'")
        else:
            # Single method mode - check class_name and method_name
            if "class_name" not in method_binding and "primary_method" not in method_binding:
                errors.append(
                    f"[{contract_id}] Missing class_name or primary_method for single_method mode"
                )

        return errors

    def _check_evidence_assembly(self, contract: Dict, contract_id: str) -> List[str]:
        """Check evidence_assembly alignment with EvidenceAssembler."""
        errors = []
        evidence_assembly = contract.get("evidence_assembly", {})

        for field in V3_EVIDENCE_ASSEMBLY_FIELDS:
            if field not in evidence_assembly:
                errors.append(f"[{contract_id}] Missing evidence_assembly field: {field}")

        assembly_rules = evidence_assembly.get("assembly_rules", [])
        if not isinstance(assembly_rules, list):
            errors.append(f"[{contract_id}] assembly_rules must be a list")
        elif not assembly_rules:
            errors.append(f"[{contract_id}] Empty assembly_rules - no evidence will be assembled")
        else:
            # Check each assembly rule structure
            for idx, rule in enumerate(assembly_rules):
                if not isinstance(rule, dict):
                    errors.append(f"[{contract_id}] assembly_rules[{idx}] is not a dict")
                    continue

                for req_field in ASSEMBLY_RULE_FIELDS:
                    if req_field not in rule:
                        errors.append(
                            f"[{contract_id}] assembly_rules[{idx}] missing '{req_field}'"
                        )

                # Validate merge_strategy is supported by EvidenceAssembler
                merge_strategy = rule.get("merge_strategy", "")
                valid_strategies = {
                    "concat",
                    "first",
                    "last",
                    "mean",
                    "max",
                    "min",
                    "weighted_mean",
                    "majority",
                }
                if merge_strategy and merge_strategy not in valid_strategies:
                    errors.append(
                        f"[{contract_id}] assembly_rules[{idx}] invalid merge_strategy '{merge_strategy}'"
                    )

        return errors

    def _check_validation_rules(self, contract: Dict, contract_id: str) -> List[str]:
        """Check validation_rules alignment with EvidenceValidator."""
        warnings = []
        validation_rules_section = contract.get("validation_rules", {})

        if not isinstance(validation_rules_section, dict):
            return [f"[{contract_id}] validation_rules must be a dict"]

        rules = validation_rules_section.get("rules", [])
        if not isinstance(rules, list):
            warnings.append(f"[{contract_id}] validation_rules.rules must be a list")
        elif not rules:
            warnings.append(f"[{contract_id}] Empty validation rules - no validation will occur")
        else:
            # Check each validation rule structure
            for idx, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    warnings.append(f"[{contract_id}] validation_rules.rules[{idx}] is not a dict")
                    continue

                if "field" not in rule:
                    warnings.append(
                        f"[{contract_id}] validation_rules.rules[{idx}] missing 'field'"
                    )

        # Check na_policy
        na_policy = validation_rules_section.get("na_policy")
        valid_na_policies = {"abort_on_critical", "score_zero", "propagate"}
        if na_policy and na_policy not in valid_na_policies:
            warnings.append(f"[{contract_id}] Invalid na_policy '{na_policy}'")

        return warnings

    def _check_signal_requirements(self, contract: Dict, contract_id: str) -> List[str]:
        """Check signal_requirements for proper irrigation."""
        errors = []
        signal_requirements = contract.get("signal_requirements", {})

        if not signal_requirements:
            errors.append(f"[{contract_id}] Missing signal_requirements section")
            return errors

        if not isinstance(signal_requirements, dict):
            errors.append(f"[{contract_id}] signal_requirements must be a dict")
            return errors

        # Check mandatory_signals structure
        if "mandatory_signals" in signal_requirements:
            mandatory = signal_requirements["mandatory_signals"]
            if not isinstance(mandatory, list):
                errors.append(f"[{contract_id}] mandatory_signals must be a list")

        # Check optional_signals structure
        if "optional_signals" in signal_requirements:
            optional = signal_requirements["optional_signals"]
            if not isinstance(optional, list):
                errors.append(f"[{contract_id}] optional_signals must be a list")

        # Check minimum_signal_threshold
        if "minimum_signal_threshold" in signal_requirements:
            threshold = signal_requirements["minimum_signal_threshold"]
            if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
                errors.append(f"[{contract_id}] minimum_signal_threshold must be between 0 and 1")

        return errors

    def _check_error_handling(self, contract: Dict, contract_id: str) -> List[str]:
        """Check error_handling for failure_contract wiring."""
        errors = []
        error_handling = contract.get("error_handling", {})

        if not error_handling:
            errors.append(f"[{contract_id}] Missing error_handling section")
            return errors

        # Check failure_contract exists for validator wiring
        if "failure_contract" not in error_handling:
            errors.append(f"[{contract_id}] Missing failure_contract in error_handling")
        else:
            failure_contract = error_handling["failure_contract"]
            if not isinstance(failure_contract, dict):
                errors.append(f"[{contract_id}] failure_contract must be a dict")
            else:
                # Check abort_if conditions for validator
                if "abort_if" in failure_contract:
                    abort_if = failure_contract["abort_if"]
                    if not isinstance(abort_if, list):
                        errors.append(f"[{contract_id}] failure_contract.abort_if must be a list")

                # Check emit_code for signal propagation
                if "emit_code" not in failure_contract:
                    errors.append(f"[{contract_id}] failure_contract missing 'emit_code'")

        # Check on_method_failure
        if "on_method_failure" not in error_handling:
            errors.append(f"[{contract_id}] Missing on_method_failure in error_handling")

        return errors

    def _check_question_context(self, contract: Dict, contract_id: str) -> List[str]:
        """Check question_context completeness."""
        errors = []
        question_context = contract.get("question_context", {})

        if not question_context:
            errors.append(f"[{contract_id}] Missing question_context section")
            return errors

        # Check expected_elements for evidence extraction
        if "expected_elements" not in question_context:
            errors.append(f"[{contract_id}] Missing expected_elements in question_context")
        elif not isinstance(question_context["expected_elements"], list):
            errors.append(f"[{contract_id}] expected_elements must be a list")

        # Check patterns for signal irrigation
        if "patterns" not in question_context:
            errors.append(f"[{contract_id}] Missing patterns in question_context")
        elif not isinstance(question_context["patterns"], list):
            errors.append(f"[{contract_id}] patterns must be a list")

        return errors

    def _update_stats(self, contract: Dict) -> None:
        """Update statistics from contract."""
        # Count orchestration modes
        method_binding = contract.get("method_binding", {})
        orchestration_mode = method_binding.get("orchestration_mode", "unknown")
        self.results["stats"][f"orchestration_mode_{orchestration_mode}"] += 1

        # Count methods in multi-method pipelines
        if orchestration_mode == "multi_method_pipeline":
            methods_count = len(method_binding.get("methods", []))
            self.results["stats"]["total_methods"] += methods_count

        # Count assembly rules
        evidence_assembly = contract.get("evidence_assembly", {})
        assembly_rules_count = len(evidence_assembly.get("assembly_rules", []))
        self.results["stats"]["total_assembly_rules"] += assembly_rules_count

        # Count validation rules
        validation_rules_section = contract.get("validation_rules", {})
        validation_rules_count = len(validation_rules_section.get("rules", []))
        self.results["stats"]["total_validation_rules"] += validation_rules_count

        # Count signal requirements
        signal_requirements = contract.get("signal_requirements", {})
        if signal_requirements:
            self.results["stats"]["contracts_with_signal_requirements"] += 1
            mandatory_signals = len(signal_requirements.get("mandatory_signals", []))
            optional_signals = len(signal_requirements.get("optional_signals", []))
            self.results["stats"]["total_mandatory_signals"] += mandatory_signals
            self.results["stats"]["total_optional_signals"] += optional_signals

    def _calculate_summary_stats(self) -> None:
        """Calculate summary statistics."""
        stats = self.results["stats"]

        # Calculate averages
        if stats.get("orchestration_mode_multi_method_pipeline", 0) > 0:
            stats["avg_methods_per_pipeline"] = (
                stats["total_methods"] / stats["orchestration_mode_multi_method_pipeline"]
            )

        if self.results["total_contracts"] > 0:
            stats["avg_assembly_rules_per_contract"] = (
                stats["total_assembly_rules"] / self.results["total_contracts"]
            )
            stats["avg_validation_rules_per_contract"] = (
                stats["total_validation_rules"] / self.results["total_contracts"]
            )
            stats["signal_requirements_coverage"] = (
                stats["contracts_with_signal_requirements"] / self.results["total_contracts"] * 100
            )

    def print_report(self) -> None:
        """Print formatted audit report."""
        print("\n" + "=" * 80)
        print("AUDIT REPORT: 300 Executor Contracts")
        print("=" * 80)

        print(f"\nTotal Contracts Audited: {self.results['total_contracts']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")

        if self.results["passed"] == self.results["total_contracts"]:
            print("\n🎉 ALL CONTRACTS PASSED AUDIT!")
        else:
            pass_rate = (self.results["passed"] / self.results["total_contracts"]) * 100
            print(f"\n📊 Pass Rate: {pass_rate:.1f}%")

        # Print statistics
        print("\n" + "-" * 80)
        print("STATISTICS")
        print("-" * 80)
        stats = self.results["stats"]

        print(f"Orchestration Modes:")
        print(
            f"  - Multi-method pipeline: {stats.get('orchestration_mode_multi_method_pipeline', 0)}"
        )
        print(f"  - Single method: {stats.get('orchestration_mode_single_method', 0)}")
        print(f"  - Unknown: {stats.get('orchestration_mode_unknown', 0)}")

        print(f"\nMethod Disaggregation:")
        print(f"  - Total methods: {stats.get('total_methods', 0)}")
        print(f"  - Avg methods/pipeline: {stats.get('avg_methods_per_pipeline', 0):.1f}")

        print(f"\nEvidence Assembly:")
        print(f"  - Total assembly rules: {stats.get('total_assembly_rules', 0)}")
        print(f"  - Avg rules/contract: {stats.get('avg_assembly_rules_per_contract', 0):.1f}")

        print(f"\nValidation:")
        print(f"  - Total validation rules: {stats.get('total_validation_rules', 0)}")
        print(f"  - Avg rules/contract: {stats.get('avg_validation_rules_per_contract', 0):.1f}")

        print(f"\nSignal Irrigation:")
        print(
            f"  - Contracts with signal_requirements: {stats.get('contracts_with_signal_requirements', 0)}"
        )
        print(f"  - Coverage: {stats.get('signal_requirements_coverage', 0):.1f}%")
        print(f"  - Total mandatory signals: {stats.get('total_mandatory_signals', 0)}")
        print(f"  - Total optional signals: {stats.get('total_optional_signals', 0)}")

        # Print errors
        if self.results["errors"]:
            print("\n" + "-" * 80)
            print(f"ERRORS ({len(self.results['errors'])})")
            print("-" * 80)
            for error in self.results["errors"][:50]:  # Show first 50
                print(f"  {error}")
            if len(self.results["errors"]) > 50:
                print(f"  ... and {len(self.results['errors']) - 50} more errors")

        # Print warnings
        if self.results["warnings"]:
            print("\n" + "-" * 80)
            print(f"WARNINGS ({len(self.results['warnings'])})")
            print("-" * 80)
            for warning in self.results["warnings"][:30]:  # Show first 30
                print(f"  {warning}")
            if len(self.results["warnings"]) > 30:
                print(f"  ... and {len(self.results['warnings']) - 30} more warnings")

        print("\n" + "=" * 80)


def main():
    """Main entry point."""
    # Find contracts directory
    script_dir = Path(__file__).resolve().parent
    contracts_dir = (
        script_dir
        / "src"
        / "farfan_pipeline.phases"
        / "Phase_two"
        / "json_files_phase_two"
        / "executor_contracts"
        / "specialized"
    )

    if not contracts_dir.exists():
        print(f"Error: Contracts directory not found: {contracts_dir}")
        sys.exit(1)

    # Run audit
    auditor = ContractAuditor(contracts_dir)
    results = auditor.audit_all_contracts()
    auditor.print_report()

    # Save detailed report to JSON
    report_file = script_dir / "audit_contracts_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Detailed report saved to: {report_file}")

    # Exit with error code if any contracts failed
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
