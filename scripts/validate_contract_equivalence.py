#!/usr/bin/env python3
"""
Contract Equivalence Validator
==============================

Validates that contracts at equivalent positions (same base_slot across 10 policy areas)
maintain structural invariants while allowing expected variations.

Matrix Structure:
- 30 base slots (D1-Q1 through D6-Q5)
- 10 policy areas (PA01-PA10)
- 300 total contracts

Equivalence Groups:
- Group 0: Q001, Q031, Q061, Q091, Q121, Q151, Q181, Q211, Q241, Q271 → all D1-Q1
- Group 1: Q002, Q032, Q062, Q092, Q122, Q152, Q182, Q212, Q242, Q272 → all D1-Q2
- ...
- Group 29: Q030, Q060, Q090, Q120, Q150, Q180, Q210, Q240, Q270, Q300 → all D6-Q5

Usage:
    python scripts/validate_contract_equivalence.py [--fix] [--group N] [--verbose]
"""

import argparse
import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict


# === Configuration ===

CONTRACTS_DIR = Path(__file__).parent.parent / "src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
NUM_BASE_SLOTS = 30
NUM_POLICY_AREAS = 10


# === Data Classes ===

@dataclass
class ValidationIssue:
    """Single validation issue found."""
    severity: str  # "ERROR", "WARNING", "INFO"
    group_id: int
    question_ids: list[str]
    component: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass 
class GroupValidationResult:
    """Validation result for one equivalence group."""
    group_id: int
    base_slot: str
    contracts_loaded: int
    contracts_expected: int
    issues: list[ValidationIssue] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        return not any(i.severity == "ERROR" for i in self.issues)


# === Core Validation Logic ===

def load_contract(path: Path) -> dict[str, Any] | None:
    """Load a single contract JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"  ⚠️  Failed to load {path.name}: {e}")
        return None


def get_question_number(question_id: str) -> int:
    """Extract numeric part from question ID (e.g., 'Q001' -> 1)."""
    return int(question_id[1:])


def get_group_id(question_number: int) -> int:
    """Compute equivalence group from question number."""
    return (question_number - 1) % NUM_BASE_SLOTS


def get_expected_question_numbers_for_group(group_id: int) -> list[int]:
    """Get all question numbers that belong to a group."""
    return [group_id + 1 + (i * NUM_BASE_SLOTS) for i in range(NUM_POLICY_AREAS)]


def compute_structure_hash(obj: Any, ignore_keys: set[str] | None = None) -> str:
    """Compute hash of object structure, ignoring specified keys."""
    ignore_keys = ignore_keys or set()
    
    def _normalize(o: Any) -> Any:
        if isinstance(o, dict):
            return {k: _normalize(v) for k, v in sorted(o.items()) if k not in ignore_keys}
        elif isinstance(o, list):
            return [_normalize(item) for item in o]
        else:
            return o
    
    normalized = _normalize(obj)
    return hashlib.sha256(json.dumps(normalized, sort_keys=True).encode()).hexdigest()[:16]


def validate_invariant_section(
    contracts: dict[str, dict],
    section_path: str,
    group_id: int,
    ignore_keys: set[str] | None = None
) -> list[ValidationIssue]:
    """
    Validate that a section is structurally identical across all contracts in group.
    
    Args:
        contracts: Dict of question_id -> contract data
        section_path: Dot-separated path to section (e.g., "method_binding.methods")
        group_id: Equivalence group ID
        ignore_keys: Keys to ignore in comparison
    """
    issues = []
    
    def get_nested(d: dict, path: str) -> Any:
        for key in path.split("."):
            if isinstance(d, dict):
                d = d.get(key, {})
            else:
                return None
        return d
    
    hashes = {}
    for qid, contract in contracts.items():
        section = get_nested(contract, section_path)
        if section:
            h = compute_structure_hash(section, ignore_keys)
            hashes[qid] = h
    
    unique_hashes = set(hashes.values())
    if len(unique_hashes) > 1:
        # Find which contracts differ
        hash_groups = defaultdict(list)
        for qid, h in hashes.items():
            hash_groups[h].append(qid)
        
        # Report the minority groups as issues
        sorted_groups = sorted(hash_groups.items(), key=lambda x: -len(x[1]))
        majority_hash, majority_qids = sorted_groups[0]
        
        for h, qids in sorted_groups[1:]:
            issues.append(ValidationIssue(
                severity="ERROR",
                group_id=group_id,
                question_ids=qids,
                component=section_path,
                message=f"Section '{section_path}' differs from majority ({len(majority_qids)} contracts)",
                details={
                    "divergent_contracts": qids,
                    "majority_contracts": majority_qids[:3],  # Sample
                    "hash_divergent": h,
                    "hash_majority": majority_hash
                }
            ))
    
    return issues


def validate_identity_consistency(
    contracts: dict[str, dict],
    group_id: int
) -> list[ValidationIssue]:
    """Validate identity block consistency within group."""
    issues = []
    
    base_slots = set()
    for qid, contract in contracts.items():
        identity = contract.get("identity", {})
        base_slots.add(identity.get("base_slot"))
    
    if len(base_slots) > 1:
        issues.append(ValidationIssue(
            severity="ERROR",
            group_id=group_id,
            question_ids=list(contracts.keys()),
            component="identity.base_slot",
            message=f"Inconsistent base_slot within group: {base_slots}",
            details={"found_slots": list(base_slots)}
        ))
    
    return issues


def validate_output_contract_consts(
    contracts: dict[str, dict],
    group_id: int
) -> list[ValidationIssue]:
    """
    Validate that output_contract.schema.properties uses correct const values
    matching the contract's identity block.
    """
    issues = []
    
    for qid, contract in contracts.items():
        identity = contract.get("identity", {})
        output_schema = contract.get("output_contract", {}).get("schema", {}).get("properties", {})
        
        # Check question_id const
        schema_qid = output_schema.get("question_id", {}).get("const")
        if schema_qid and schema_qid != identity.get("question_id"):
            issues.append(ValidationIssue(
                severity="ERROR",
                group_id=group_id,
                question_ids=[qid],
                component="output_contract.schema.properties.question_id",
                message=f"Hardcoded wrong question_id: schema has '{schema_qid}', identity has '{identity.get('question_id')}'",
                details={
                    "schema_value": schema_qid,
                    "identity_value": identity.get("question_id")
                }
            ))
        
        # Check question_global const
        schema_global = output_schema.get("question_global", {}).get("const")
        if schema_global and schema_global != identity.get("question_global"):
            issues.append(ValidationIssue(
                severity="ERROR",
                group_id=group_id,
                question_ids=[qid],
                component="output_contract.schema.properties.question_global",
                message=f"Hardcoded wrong question_global: schema has {schema_global}, identity has {identity.get('question_global')}",
                details={
                    "schema_value": schema_global,
                    "identity_value": identity.get("question_global")
                }
            ))
        
        # Check policy_area_id const
        schema_pa = output_schema.get("policy_area_id", {}).get("const")
        if schema_pa and schema_pa != identity.get("policy_area_id"):
            issues.append(ValidationIssue(
                severity="ERROR",
                group_id=group_id,
                question_ids=[qid],
                component="output_contract.schema.properties.policy_area_id",
                message=f"Hardcoded wrong policy_area_id: schema has '{schema_pa}', identity has '{identity.get('policy_area_id')}'",
                details={
                    "schema_value": schema_pa,
                    "identity_value": identity.get("policy_area_id")
                }
            ))
    
    return issues


def validate_method_binding_invariants(
    contracts: dict[str, dict],
    group_id: int
) -> list[ValidationIssue]:
    """Validate method_binding is identical across group."""
    return validate_invariant_section(
        contracts, 
        "method_binding", 
        group_id,
        ignore_keys={"note"}  # Notes can vary
    )


def validate_executor_binding_invariants(
    contracts: dict[str, dict],
    group_id: int
) -> list[ValidationIssue]:
    """Validate executor_binding is identical across group."""
    return validate_invariant_section(contracts, "executor_binding", group_id)


def validate_evidence_assembly_invariants(
    contracts: dict[str, dict],
    group_id: int
) -> list[ValidationIssue]:
    """Validate evidence_assembly rules are identical across group."""
    return validate_invariant_section(
        contracts,
        "evidence_assembly.assembly_rules",
        group_id
    )


def validate_group(group_id: int, verbose: bool = False) -> GroupValidationResult:
    """Validate a single equivalence group."""
    expected_qnums = get_expected_question_numbers_for_group(group_id)
    
    # Load all contracts in this group
    contracts = {}
    base_slot = None
    
    for qnum in expected_qnums:
        qid = f"Q{qnum:03d}"
        path = CONTRACTS_DIR / f"{qid}.v3.json"
        
        if path.exists():
            contract = load_contract(path)
            if contract:
                contracts[qid] = contract
                if not base_slot:
                    base_slot = contract.get("identity", {}).get("base_slot", "UNKNOWN")
    
    result = GroupValidationResult(
        group_id=group_id,
        base_slot=base_slot or "UNKNOWN",
        contracts_loaded=len(contracts),
        contracts_expected=len(expected_qnums)
    )
    
    if len(contracts) < 2:
        result.issues.append(ValidationIssue(
            severity="WARNING",
            group_id=group_id,
            question_ids=list(contracts.keys()),
            component="loading",
            message=f"Only {len(contracts)} contracts loaded, cannot validate equivalence"
        ))
        return result
    
    # Run all validations
    result.issues.extend(validate_identity_consistency(contracts, group_id))
    result.issues.extend(validate_executor_binding_invariants(contracts, group_id))
    result.issues.extend(validate_method_binding_invariants(contracts, group_id))
    result.issues.extend(validate_evidence_assembly_invariants(contracts, group_id))
    result.issues.extend(validate_output_contract_consts(contracts, group_id))
    
    return result


# === Reporting ===

def print_group_result(result: GroupValidationResult, verbose: bool = False) -> None:
    """Print validation result for a group."""
    status = "✅" if result.is_valid else "❌"
    print(f"\n{status} Group {result.group_id:2d} | {result.base_slot} | {result.contracts_loaded}/{result.contracts_expected} contracts")
    
    if result.issues:
        for issue in result.issues:
            icon = {"ERROR": "🔴", "WARNING": "🟡", "INFO": "🔵"}.get(issue.severity, "⚪")
            print(f"   {icon} [{issue.component}] {issue.message}")
            if verbose and issue.details:
                for k, v in issue.details.items():
                    print(f"      • {k}: {v}")


def print_summary(results: list[GroupValidationResult]) -> None:
    """Print summary of all validation results."""
    total_groups = len(results)
    valid_groups = sum(1 for r in results if r.is_valid)
    total_issues = sum(len(r.issues) for r in results)
    error_count = sum(1 for r in results for i in r.issues if i.severity == "ERROR")
    warning_count = sum(1 for r in results for i in r.issues if i.severity == "WARNING")
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Groups validated: {total_groups}")
    print(f"Groups passing:   {valid_groups}/{total_groups} ({100*valid_groups/total_groups:.1f}%)")
    print(f"Total issues:     {total_issues}")
    print(f"  🔴 Errors:      {error_count}")
    print(f"  🟡 Warnings:    {warning_count}")
    
    if error_count > 0:
        print("\n⚠️  VALIDATION FAILED - Errors found that require attention")
    else:
        print("\n✅ VALIDATION PASSED - No critical errors found")


# === Main ===

def main():
    parser = argparse.ArgumentParser(description="Validate executor contract equivalence across groups")
    parser.add_argument("--group", "-g", type=int, help="Validate only specific group (0-29)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed issue information")
    parser.add_argument("--fix", action="store_true", help="Attempt to auto-fix output_contract const issues")
    args = parser.parse_args()
    
    print("=" * 60)
    print("EXECUTOR CONTRACT EQUIVALENCE VALIDATOR")
    print("=" * 60)
    print(f"Contracts directory: {CONTRACTS_DIR}")
    print(f"Matrix: {NUM_BASE_SLOTS} base slots × {NUM_POLICY_AREAS} policy areas = 300 contracts")
    
    if args.group is not None:
        if 0 <= args.group < NUM_BASE_SLOTS:
            groups_to_validate = [args.group]
        else:
            print(f"Error: --group must be 0-{NUM_BASE_SLOTS-1}")
            return 1
    else:
        groups_to_validate = range(NUM_BASE_SLOTS)
    
    results = []
    for group_id in groups_to_validate:
        result = validate_group(group_id, verbose=args.verbose)
        results.append(result)
        print_group_result(result, verbose=args.verbose)
    
    print_summary(results)
    
    return 0 if all(r.is_valid for r in results) else 1


if __name__ == "__main__":
    exit(main())
