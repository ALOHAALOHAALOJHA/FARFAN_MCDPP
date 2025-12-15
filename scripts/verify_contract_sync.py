#!/usr/bin/env python3
"""
Contract Synchronization Verifier
==================================

Comprehensive verification system that validates contract synchronization results
and ensures deep structural integrity across executor contract groups. 

This script performs:
1. Post-sync validation to ensure fixes were correctly applied
2. Cross-contract consistency checking within groups
3. Method-evidence graph validation
4. Human-answer structure completeness verification
5. Golden contract compliance checking
6. Execution path validation

Usage:
    python verify_contract_sync.py --group 0                    # Verify group 0
    python verify_contract_sync.py --contracts Q001,Q031,Q061   # Verify specific contracts
    python verify_contract_sync.py --all --strict               # Verify all with strict mode
    python verify_contract_sync.py --golden Q001 --compare Q031 # Compare against golden
"""

import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import networkx as nx
from termcolor import colored
import sys

# === Configuration ===
CONTRACTS_DIR = Path(__file__).parent.parent / "src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized"

# === Verification Rules ===

class VerificationLevel(Enum):
    """Verification strictness levels."""
    CRITICAL = "critical"     # Must pass for execution
    REQUIRED = "required"     # Should pass for correctness
    RECOMMENDED = "recommended"  # Should pass for quality
    OPTIONAL = "optional"     # Nice to have


class VerificationStatus(Enum):
    """Verification result status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class VerificationRule:
    """A single verification rule."""
    name: str
    description: str
    level: VerificationLevel
    check_function: str  # Name of function to call
    applies_to: str  # "individual", "group", "all"
    
    
@dataclass
class VerificationResult:
    """Result of a single verification check."""
    rule_name: str
    status: VerificationStatus
    message: str
    level: VerificationLevel
    details: Dict[str, Any] = field(default_factory=dict)
    contracts_affected: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "rule": self.rule_name,
            "status": self.status.value,
            "level": self.level.value,
            "message": self.message,
            "details": self.details,
            "contracts_affected": self.contracts_affected
        }


@dataclass 
class VerificationReport: 
    """Complete verification report."""
    timestamp: str
    contracts_verified: List[str]
    golden_contract: Optional[str]
    results: List[VerificationResult] = field(default_factory=list)
    
    @property
    def passed_count(self) -> int:
        return len([r for r in self.results if r.status == VerificationStatus.PASSED])
    
    @property
    def failed_count(self) -> int:
        return len([r for r in self.results if r.status == VerificationStatus.FAILED])
    
    @property
    def warning_count(self) -> int:
        return len([r for r in self.results if r.status == VerificationStatus.WARNING])
    
    @property
    def critical_failures(self) -> List[VerificationResult]:
        return [r for r in self.results 
                if r.status == VerificationStatus.FAILED 
                and r.level == VerificationLevel.CRITICAL]
    
    def add_result(self, result: VerificationResult):
        self.results.append(result)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "contracts_verified": self.contracts_verified,
            "golden_contract": self.golden_contract,
            "summary": {
                "total_checks": len(self.results),
                "passed": self.passed_count,
                "failed": self.failed_count,
                "warnings": self.warning_count,
                "critical_failures": len(self.critical_failures)
            },
            "results": [r.to_dict() for r in self.results]
        }
    
    def print_summary(self, verbose: bool = False):
        """Print colored summary to console."""
        print("\n" + "="*80)
        print(colored("VERIFICATION REPORT", "cyan", attrs=["bold"]))
        print("="*80)
        
        # Summary stats
        print(f"\n📊 Summary:")
        print(f"  Total checks: {len(self.results)}")
        print(f"  ✅ Passed: {colored(str(self.passed_count), 'green')}")
        print(f"  ❌ Failed: {colored(str(self.failed_count), 'red')}")
        print(f"  ⚠️  Warnings: {colored(str(self.warning_count), 'yellow')}")
        
        if self.critical_failures:
            print(f"\n🚨 {colored(f'CRITICAL FAILURES: {len(self.critical_failures)}', 'red', attrs=['bold'])}")
            for failure in self.critical_failures:
                print(f"  • {failure.rule_name}: {failure.message}")
                if failure.contracts_affected:
                    print(f"    Affects: {', '.join(failure.contracts_affected)}")
        
        if verbose or self.failed_count > 0:
            print(f"\n📋 Detailed Results:")
            
            # Group by level
            for level in VerificationLevel: 
                level_results = [r for r in self.results if r.level == level]
                if not level_results:
                    continue
                    
                print(f"\n  {level.value.upper()} checks:")
                for result in level_results:
                    if result.status == VerificationStatus.PASSED:
                        symbol = colored("✓", "green")
                    elif result.status == VerificationStatus.FAILED:
                        symbol = colored("✗", "red") 
                    elif result.status == VerificationStatus.WARNING:
                        symbol = colored("!", "yellow")
                    else: 
                        symbol = colored("-", "gray")
                    
                    print(f"    {symbol} {result.rule_name}: {result.message}")
                    
                    if verbose and result.details:
                        for key, value in result.details.items():
                            print(f"      • {key}: {value}")


# === Verification Rules Registry ===

VERIFICATION_RULES = [
    # Critical rules
    VerificationRule(
        name="identity_consistency",
        description="Verify identity fields match between identity block and output_contract schema",
        level=VerificationLevel.CRITICAL,
        check_function="verify_identity_consistency",
        applies_to="individual"
    ),
    VerificationRule(
        name="method_evidence_alignment", 
        description="Verify all evidence assembly sources map to method provides",
        level=VerificationLevel.CRITICAL,
        check_function="verify_method_evidence_alignment",
        applies_to="individual"
    ),
    VerificationRule(
        name="execution_sequence_validity",
        description="Verify execution sequence has valid dependencies",
        level=VerificationLevel.CRITICAL,
        check_function="verify_execution_sequence",
        applies_to="individual"
    ),
    
    # Required rules
    VerificationRule(
        name="group_structural_consistency",
        description="Verify shared structures are identical within group",
        level=VerificationLevel.REQUIRED,
        check_function="verify_group_consistency",
        applies_to="group"
    ),
    VerificationRule(
        name="human_answer_structure_complete",
        description="Verify human_answer_structure has all required components",
        level=VerificationLevel.REQUIRED,
        check_function="verify_human_answer_structure",
        applies_to="individual"
    ),
    VerificationRule(
        name="method_outputs_documented",
        description="Verify all methods have documented outputs",
        level=VerificationLevel.REQUIRED,
        check_function="verify_method_outputs",
        applies_to="individual"
    ),
    
    # Recommended rules
    VerificationRule(
        name="evidence_nexus_migration",
        description="Verify using EvidenceNexus instead of legacy EvidenceAssembler",
        level=VerificationLevel.RECOMMENDED,
        check_function="verify_evidence_nexus",
        applies_to="individual"
    ),
    VerificationRule(
        name="contract_hash_valid",
        description="Verify contract hash matches content",
        level=VerificationLevel.RECOMMENDED,
        check_function="verify_contract_hash",
        applies_to="individual"
    ),
    VerificationRule(
        name="pattern_coverage",
        description="Verify sufficient pattern coverage for question",
        level=VerificationLevel.RECOMMENDED,
        check_function="verify_pattern_coverage",
        applies_to="individual"
    )
]


# === Helper Functions ===

def deep_get(obj: Dict, path: str) -> Any:
    """Get nested dict value using dot notation."""
    keys = path.split('.')
    current = obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return None
        elif isinstance(current, list) and key.isdigit():
            idx = int(key)
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return None
        else:
            return None
    return current


def load_contract(question_id: str) -> Optional[Dict]:
    """Load contract JSON."""
    path = CONTRACTS_DIR / f"{question_id}.v3.json"
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {question_id}: {e}")
        return None


def compute_contract_hash(contract: Dict) -> str:
    """Compute SHA-256 hash of contract content."""
    contract_copy = json.loads(json.dumps(contract))
    if "identity" in contract_copy:
        contract_copy["identity"].pop("contract_hash", None)
        contract_copy["identity"].pop("created_at", None)
        contract_copy["identity"].pop("updated_at", None)
    content = json.dumps(contract_copy, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(content.encode()).hexdigest()


# === Individual Contract Verification Functions ===

def verify_identity_consistency(contract: Dict, qid: str) -> VerificationResult:
    """Verify identity fields match between identity block and output_contract schema."""
    
    fields_to_check = [
        "base_slot",
        "question_id", 
        "question_global",
        "policy_area_id",
        "dimension_id",
        "cluster_id"
    ]
    
    mismatches = []
    
    for field in fields_to_check: 
        identity_value = deep_get(contract, f"identity.{field}")
        schema_value = deep_get(contract, f"output_contract.schema.properties.{field}.const")
        
        # Skip if schema doesn't have this field
        if deep_get(contract, f"output_contract.schema.properties.{field}") is None:
            continue
            
        if schema_value != identity_value:
            mismatches.append({
                "field": field,
                "identity": identity_value,
                "schema": schema_value
            })
    
    if mismatches:
        return VerificationResult(
            rule_name="identity_consistency",
            status=VerificationStatus.FAILED,
            level=VerificationLevel.CRITICAL,
            message=f"{len(mismatches)} identity fields don't match schema",
            details={"mismatches": mismatches},
            contracts_affected=[qid]
        )
    
    return VerificationResult(
        rule_name="identity_consistency",
        status=VerificationStatus.PASSED,
        level=VerificationLevel.CRITICAL,
        message="All identity fields match schema",
        contracts_affected=[qid]
    )


def verify_method_evidence_alignment(contract: Dict, qid: str) -> VerificationResult:
    """Verify all evidence assembly sources map to method provides."""
    
    # Get all method provides
    methods = deep_get(contract, "method_binding.methods") or []
    provides_set = {m.get("provides") for m in methods if m.get("provides")}
    
    # Get all referenced sources in assembly rules
    assembly_rules = deep_get(contract, "evidence_assembly.assembly_rules") or []
    referenced_sources = set()
    unmapped_sources = []
    
    for rule in assembly_rules:
        sources = rule.get("sources", [])
        for source in sources:
            # Handle wildcards
            if "*" in source:
                base = source.split("*")[0].rstrip(".")
                if base:
                    referenced_sources.add(base)
                    # Check if any provides starts with this base
                    if not any(p.startswith(base) for p in provides_set):
                        unmapped_sources.append(source)
            else:
                referenced_sources.add(source)
                if source not in provides_set: 
                    unmapped_sources.append(source)
    
    if unmapped_sources:
        return VerificationResult(
            rule_name="method_evidence_alignment",
            status=VerificationStatus.FAILED,
            level=VerificationLevel.CRITICAL,
            message=f"{len(unmapped_sources)} assembly sources don't map to methods",
            details={
                "unmapped_sources": unmapped_sources,
                "available_provides": sorted(list(provides_set))
            },
            contracts_affected=[qid]
        )
    
    # Calculate coverage
    coverage = len(referenced_sources) / len(provides_set) if provides_set else 0
    
    if coverage < 0.5:
        return VerificationResult(
            rule_name="method_evidence_alignment",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.CRITICAL,
            message=f"Only {coverage:.0%} of methods are used in assembly",
            details={"coverage": coverage},
            contracts_affected=[qid]
        )
    
    return VerificationResult(
        rule_name="method_evidence_alignment",
        status=VerificationStatus.PASSED,
        level=VerificationLevel.CRITICAL,
        message=f"All assembly sources map to methods ({coverage:.0%} coverage)",
        contracts_affected=[qid]
    )


def verify_execution_sequence(contract: Dict, qid: str) -> VerificationResult: 
    """Verify execution sequence forms a valid DAG."""
    
    exec_seq = deep_get(contract, "method_binding.execution_sequence")
    
    if not exec_seq: 
        return VerificationResult(
            rule_name="execution_sequence_validity",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.CRITICAL,
            message="No execution_sequence defined",
            contracts_affected=[qid]
        )
    
    if not isinstance(exec_seq, dict):
        return VerificationResult(
            rule_name="execution_sequence_validity",
            status=VerificationStatus.FAILED,
            level=VerificationLevel.CRITICAL,
            message="execution_sequence is not a dictionary",
            contracts_affected=[qid]
        )
    
    # Build dependency graph
    G = nx.DiGraph()
    
    for step_name, step_info in exec_seq.items():
        G.add_node(step_name)
        
        deps = step_info.get("depends_on", [])
        if isinstance(deps, list):
            for dep in deps: 
                G.add_edge(dep, step_name)
    
    # Check for cycles
    if not nx.is_directed_acyclic_graph(G):
        cycles = list(nx.simple_cycles(G))
        return VerificationResult(
            rule_name="execution_sequence_validity",
            status=VerificationStatus.FAILED,
            level=VerificationLevel.CRITICAL,
            message=f"Execution sequence has circular dependencies",
            details={"cycles": cycles},
            contracts_affected=[qid]
        )
    
    # Check all dependencies exist
    all_steps = set(exec_seq.keys())
    missing_deps = []
    
    for step_name, step_info in exec_seq.items():
        deps = step_info.get("depends_on", [])
        if isinstance(deps, list):
            for dep in deps: 
                if dep not in all_steps:
                    missing_deps.append(f"{step_name} depends on missing {dep}")
    
    if missing_deps:
        return VerificationResult(
            rule_name="execution_sequence_validity",
            status=VerificationStatus.FAILED,
            level=VerificationLevel.CRITICAL,
            message=f"Execution sequence has missing dependencies",
            details={"missing_dependencies": missing_deps},
            contracts_affected=[qid]
        )
    
    return VerificationResult(
        rule_name="execution_sequence_validity",
        status=VerificationStatus.PASSED,
        level=VerificationLevel.CRITICAL,
        message=f"Valid DAG with {len(G.nodes)} steps",
        details={"num_steps": len(G.nodes), "num_edges": len(G.edges)},
        contracts_affected=[qid]
    )


def verify_human_answer_structure(contract: Dict, qid: str) -> VerificationResult:
    """Verify human_answer_structure completeness."""
    
    has = contract.get("human_answer_structure", {})
    
    if not has:
        return VerificationResult(
            rule_name="human_answer_structure_complete",
            status=VerificationStatus.FAILED,
            level=VerificationLevel.REQUIRED,
            message="Missing human_answer_structure",
            contracts_affected=[qid]
        )
    
    required_components = [
        "evidence_structure_schema",
        "concrete_example",
        "validation_against_expected_elements",
        "assembly_flow"
    ]
    
    missing = []
    for component in required_components:
        if component not in has:
            missing.append(component)
    
    if missing:
        return VerificationResult(
            rule_name="human_answer_structure_complete",
            status=VerificationStatus.FAILED,
            level=VerificationLevel.REQUIRED,
            message=f"Missing {len(missing)} required components",
            details={"missing_components": missing},
            contracts_affected=[qid]
        )
    
    # Check schema validity
    schema = has.get("evidence_structure_schema", {})
    if not schema.get("properties"):
        return VerificationResult(
            rule_name="human_answer_structure_complete",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.REQUIRED,
            message="Evidence schema has no properties defined",
            contracts_affected=[qid]
        )
    
    # Check example validity
    example = has.get("concrete_example", {})
    if not example: 
        return VerificationResult(
            rule_name="human_answer_structure_complete",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.REQUIRED,
            message="Concrete example is empty",
            contracts_affected=[qid]
        )
    
    return VerificationResult(
        rule_name="human_answer_structure_complete",
        status=VerificationStatus.PASSED,
        level=VerificationLevel.REQUIRED,
        message="Complete human_answer_structure with all components",
        details={
            "schema_properties": len(schema.get("properties", {})),
            "example_fields": len(example)
        },
        contracts_affected=[qid]
    )


def verify_method_outputs(contract: Dict, qid: str) -> VerificationResult:
    """Verify all methods have documented outputs."""
    
    methods = deep_get(contract, "method_binding.methods") or []
    method_outputs = contract.get("method_outputs", {})
    
    if not method_outputs:
        return VerificationResult(
            rule_name="method_outputs_documented",
            status=VerificationStatus.FAILED,
            level=VerificationLevel.REQUIRED,
            message="No method_outputs section",
            contracts_affected=[qid]
        )
    
    undocumented = []
    incomplete = []
    
    for method in methods:
        method_name = method.get("method_name")
        class_name = method.get("class_name")
        full_name = f"{class_name}.{method_name}"
        
        if full_name not in method_outputs: 
            undocumented.append(full_name)
        else:
            output_doc = method_outputs[full_name]
            # Check for required fields
            required_fields = ["output_type", "structure", "validation", "usage_in_assembly"]
            missing_fields = [f for f in required_fields if f not in output_doc]
            if missing_fields:
                incomplete.append(f"{full_name}: missing {missing_fields}")
    
    if undocumented:
        return VerificationResult(
            rule_name="method_outputs_documented",
            status=VerificationStatus.FAILED,
            level=VerificationLevel.REQUIRED,
            message=f"{len(undocumented)} methods lack output documentation",
            details={"undocumented_methods": undocumented},
            contracts_affected=[qid]
        )
    
    if incomplete: 
        return VerificationResult(
            rule_name="method_outputs_documented",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.REQUIRED,
            message=f"{len(incomplete)} methods have incomplete documentation",
            details={"incomplete_methods": incomplete},
            contracts_affected=[qid]
        )
    
    return VerificationResult(
        rule_name="method_outputs_documented",
        status=VerificationStatus.PASSED,
        level=VerificationLevel.REQUIRED,
        message=f"All {len(methods)} methods fully documented",
        contracts_affected=[qid]
    )


def verify_evidence_nexus(contract: Dict, qid: str) -> VerificationResult:
    """Verify using EvidenceNexus instead of legacy EvidenceAssembler."""
    
    class_name = deep_get(contract, "evidence_assembly.class_name")
    module_name = deep_get(contract, "evidence_assembly.module")
    
    if class_name == "EvidenceAssembler": 
        return VerificationResult(
            rule_name="evidence_nexus_migration",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.RECOMMENDED,
            message="Still using legacy EvidenceAssembler",
            details={
                "current_class": class_name,
                "current_module": module_name,
                "recommended_class": "EvidenceNexus",
                "recommended_module": "farfan_core.core.orchestrator.evidence_nexus"
            },
            contracts_affected=[qid]
        )
    
    if class_name != "EvidenceNexus": 
        return VerificationResult(
            rule_name="evidence_nexus_migration",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.RECOMMENDED,
            message=f"Using unknown evidence class: {class_name}",
            contracts_affected=[qid]
        )
    
    # Check for evidence_structure_post_nexus
    if not deep_get(contract, "evidence_structure_post_nexus"):
        return VerificationResult(
            rule_name="evidence_nexus_migration",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.RECOMMENDED,
            message="Using EvidenceNexus but missing evidence_structure_post_nexus",
            contracts_affected=[qid]
        )
    
    return VerificationResult(
        rule_name="evidence_nexus_migration",
        status=VerificationStatus.PASSED,
        level=VerificationLevel.RECOMMENDED,
        message="Properly using EvidenceNexus with post-nexus structure",
        contracts_affected=[qid]
    )


def verify_contract_hash(contract: Dict, qid: str) -> VerificationResult: 
    """Verify contract hash matches content."""
    
    stored_hash = deep_get(contract, "identity.contract_hash")
    
    if not stored_hash: 
        return VerificationResult(
            rule_name="contract_hash_valid",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.RECOMMENDED,
            message="No contract hash in identity",
            contracts_affected=[qid]
        )
    
    computed_hash = compute_contract_hash(contract)
    
    if stored_hash != computed_hash: 
        return VerificationResult(
            rule_name="contract_hash_valid",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.RECOMMENDED,
            message="Contract hash doesn't match content",
            details={
                "stored": stored_hash[:16] + "...",
                "computed": computed_hash[:16] + "..."
            },
            contracts_affected=[qid]
        )
    
    return VerificationResult(
        rule_name="contract_hash_valid",
        status=VerificationStatus.PASSED,
        level=VerificationLevel.RECOMMENDED,
        message="Contract hash valid",
        contracts_affected=[qid]
    )


def verify_pattern_coverage(contract: Dict, qid: str) -> VerificationResult:
    """Verify sufficient pattern coverage for question."""
    
    patterns = deep_get(contract, "question_context.patterns") or []
    
    if len(patterns) < 5:
        return VerificationResult(
            rule_name="pattern_coverage",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.RECOMMENDED,
            message=f"Only {len(patterns)} patterns defined (recommended: 10+)",
            contracts_affected=[qid]
        )
    
    # Check pattern diversity (categories)
    categories = set()
    for pattern in patterns:
        if isinstance(pattern, dict):
            cat = pattern.get("category", "GENERAL")
            categories.add(cat)
    
    if len(categories) < 3:
        return VerificationResult(
            rule_name="pattern_coverage",
            status=VerificationStatus.WARNING,
            level=VerificationLevel.RECOMMENDED,
            message=f"Low pattern diversity: only {len(categories)} categories",
            details={"categories": list(categories)},
            contracts_affected=[qid]
        )
    
    return VerificationResult(
        rule_name="pattern_coverage",
        status=VerificationStatus.PASSED,
        level=VerificationLevel.RECOMMENDED,
        message=f"Good pattern coverage: {len(patterns)} patterns, {len(categories)} categories",
        contracts_affected=[qid]
    )


# === Group Verification Functions ===

def verify_group_consistency(contracts: Dict[str, Dict]) -> VerificationResult:
    """Verify shared structures are identical within group."""
    
    if len(contracts) < 2:
        return VerificationResult(
            rule_name="group_structural_consistency",
            status=VerificationStatus.SKIPPED,
            level=VerificationLevel.REQUIRED,
            message="Need at least 2 contracts for group verification"
        )
    
    shared_fields = [
        "executor_binding",
        "method_binding.methods",
        "method_binding.orchestration_mode",
        "evidence_assembly.module",
        "evidence_assembly.class_name",
    ]
    
    inconsistencies = []
    
    for field_path in shared_fields:
        values = {}
        for qid, contract in contracts.items():
            value = deep_get(contract, field_path)
            if value is not None:
                # Convert to string for comparison
                value_str = json.dumps(value, sort_keys=True)
                if value_str not in values:
                    values[value_str] = []
                values[value_str].append(qid)
        
        if len(values) > 1:
            inconsistencies.append({
                "field": field_path,
                "variants": len(values),
                "distribution": {
                    f"variant_{i}": qids 
                    for i, qids in enumerate(values.values())
                }
            })
    
    if inconsistencies:
        return VerificationResult(
            rule_name="group_structural_consistency",
            status=VerificationStatus.FAILED,
            level=VerificationLevel.REQUIRED,
            message=f"{len(inconsistencies)} shared fields are inconsistent",
            details={"inconsistencies": inconsistencies},
            contracts_affected=list(contracts.keys())
        )
    
    return VerificationResult(
        rule_name="group_structural_consistency",
        status=VerificationStatus.PASSED,
        level=VerificationLevel.REQUIRED,
        message="All shared structures are consistent",
        contracts_affected=list(contracts.keys())
    )


# === Verification Runner ===

class ContractVerifier:
    """Main verification engine."""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        
    def verify_contracts(
        self, 
        contracts: Dict[str, Dict],
        golden_id: Optional[str] = None
    ) -> VerificationReport: 
        """Run all applicable verification rules."""
        
        report = VerificationReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            contracts_verified=list(contracts.keys()),
            golden_contract=golden_id
        )
        
        # Run individual contract checks
        for qid, contract in contracts.items():
            for rule in VERIFICATION_RULES: 
                if rule.applies_to != "individual":
                    continue
                    
                # Get verification function
                func_name = rule.check_function
                if hasattr(sys.modules[__name__], func_name):
                    func = getattr(sys.modules[__name__], func_name)
                    try:
                        result = func(contract, qid)
                        report.add_result(result)
                    except Exception as e: 
                        report.add_result(VerificationResult(
                            rule_name=rule.name,
                            status=VerificationStatus.FAILED,
                            level=rule.level,
                            message=f"Verification failed with error: {str(e)}",
                            contracts_affected=[qid]
                        ))
        
        # Run group checks
        for rule in VERIFICATION_RULES: 
            if rule.applies_to != "group":
                continue
                
            func_name = rule.check_function
            if hasattr(sys.modules[__name__], func_name):
                func = getattr(sys.modules[__name__], func_name)
                try:
                    result = func(contracts)
                    report.add_result(result)
                except Exception as e:
                    report.add_result(VerificationResult(
                        rule_name=rule.name,
                        status=VerificationStatus.FAILED,
                        level=rule.level,
                        message=f"Verification failed with error: {str(e)}",
                        contracts_affected=list(contracts.keys())
                    ))
        
        # Golden contract comparison if specified
        if golden_id and golden_id in contracts:
            self._verify_against_golden(contracts, golden_id, report)
        
        return report
    
    def _verify_against_golden(
        self, 
        contracts: Dict[str, Dict], 
        golden_id: str,
        report: VerificationReport
    ):
        """Additional checks comparing against golden contract."""
        
        golden = contracts[golden_id]
        
        for qid, contract in contracts.items():
            if qid == golden_id:
                continue
            
            # Check critical structures exist if in golden
            critical_in_golden = [
                "method_binding.execution_sequence",
                "method_outputs",
                "evidence_structure_post_nexus",
                "human_answer_structure"
            ]
            
            for path in critical_in_golden: 
                if deep_get(golden, path) and not deep_get(contract, path):
                    report.add_result(VerificationResult(
                        rule_name="golden_compliance",
                        status=VerificationStatus.WARNING,
                        level=VerificationLevel.RECOMMENDED,
                        message=f"Missing structure present in golden: {path}",
                        contracts_affected=[qid]
                    ))


# === Report Generation ===

def generate_html_report(report: VerificationReport, output_path: Path):
    """Generate an HTML verification report."""
    
    # Status colors
    status_colors = {
        VerificationStatus.PASSED: "#27ae60",
        VerificationStatus.FAILED: "#e74c3c", 
        VerificationStatus.WARNING: "#f39c12",
        VerificationStatus.SKIPPED: "#95a5a6"
    }
    
    # Level badges
    level_badges = {
        VerificationLevel.CRITICAL: "🚨",
        VerificationLevel.REQUIRED: "⚠️",
        VerificationLevel.RECOMMENDED: "💡",
        VerificationLevel.OPTIONAL: "ℹ️"
    }
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Contract Verification Report</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
        }}
        h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .timestamp {{
            opacity: 0.9;
            margin-top: 10px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            text-align: center;
            transition: transform 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-value {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-label {{
            color: #7f8c8d;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}
        .results {{
            padding: 40px;
        }}
        .result-group {{
            margin-bottom: 30px;
        }}
        .result-header {{
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        .result-item {{
            background: white;
            border-left: 4px solid #95a5a6;
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 4px;
            transition: all 0.2s;
        }}
        .result-item:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .result-item.passed {{ border-left-color: #27ae60; background: #f0fdf4; }}
        .result-item.failed {{ border-left-color: #e74c3c; background: #fef2f2; }}
        .result-item.warning {{ border-left-color: #f39c12; background: #fffbeb; }}
        .result-item.skipped {{ border-left-color: #95a5a6; background: #f8f9fa; }}
        .result-title {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }}
        .result-name {{
            font-weight: 600;
            color: #2c3e50;
        }}
        .result-status {{
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .result-message {{
            color: #5a6c7d;
            margin: 5px 0;
        }}
        .result-details {{
            margin-top: 10px;
            padding: 10px;
            background: rgba(0,0,0,0.03);
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #34495e;
        }}
        .critical-section {{
            background: #fef2f2;
            border: 2px solid #e74c3c;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 40px;
        }}
        .critical-title {{
            color: #e74c3c;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #7f8c8d;
            border-top: 1px solid #e0e6ed;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Contract Verification Report</h1>
            <div class="timestamp">Generated: {report.timestamp}</div>
            <div class="timestamp">Contracts: {', '.join(report.contracts_verified[:5])}{'...' if len(report.contracts_verified) > 5 else ''}</div>
        </div>
        
        <div class="summary-grid">
            <div class="stat-card">
                <div class="stat-value" style="color: #27ae60;">{report.passed_count}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #e74c3c;">{report.failed_count}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #f39c12;">{report.warning_count}</div>
                <div class="stat-label">Warnings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #3498db;">{len(report.results)}</div>
                <div class="stat-label">Total Checks</div>
            </div>
        </div>
"""
    
    # Critical failures section
    if report.critical_failures:
        html += f"""
        <div class="critical-section">
            <div class="critical-title">🚨 Critical Failures Detected</div>
"""
        for failure in report.critical_failures:
            html += f"""
            <div style="margin: 10px 0;">
                <strong>{failure.rule_name}</strong>: {failure.message}
                {f'<div style="margin-left: 20px; color: #7f8c8d;">Affects: {", ".join(failure.contracts_affected)}</div>' if failure.contracts_affected else ''}
            </div>
"""
        html += "</div>"
    
    # Results by level
    html += '<div class="results">'
    
    for level in VerificationLevel:
        level_results = [r for r in report.results if r.level == level]
        if not level_results:
            continue
            
        html += f"""
        <div class="result-group">
            <div class="result-header">
                {level_badges.get(level, '')} {level.value.title()} Checks
            </div>
"""
        
        for result in level_results:
            status_color = status_colors.get(result.status, "#95a5a6")
            html += f"""
            <div class="result-item {result.status.value}">
                <div class="result-title">
                    <span class="result-name">{result.rule_name.replace('_', ' ').title()}</span>
                    <span class="result-status" style="background: {status_color}; color: white;">
                        {result.status.value}
                    </span>
                </div>
                <div class="result-message">{result.message}</div>
"""
            if result.details:
                details_str = json.dumps(result.details, indent=2)
                if len(details_str) > 500:
                    details_str = details_str[:500] + "..."
                html += f'<div class="result-details">{details_str}</div>'
            
            html += '</div>'
        
        html += '</div>'
    
    html += '</div>'
    
    # Footer
    html += f"""
        <div class="footer">
            <div>Contract Verification System v1.0</div>
            <div style="margin-top: 10px;">
                {'✅ All critical checks passed' if not report.critical_failures else f'❌ {len(report.critical_failures)} critical failures detected'}
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


# === Main ===

def main():
    parser = argparse.ArgumentParser(description="Contract synchronization verifier")
    parser.add_argument("--contracts", type=str, help="Comma-separated question IDs to verify")
    parser.add_argument("--group", type=int, help="Verify entire group (0-29)")
    parser.add_argument("--all", action="store_true", help="Verify all contracts")
    parser.add_argument("--golden", type=str, help="Golden contract for comparison")
    parser.add_argument("--strict", action="store_true", help="Strict mode - fail on warnings")
    parser.add_argument("--json-report", type=str, help="Save JSON report")
    parser.add_argument("--html-report", type=str, help="Save HTML report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("="*80)
    print(colored("CONTRACT VERIFICATION SYSTEM", "cyan", attrs=["bold"]))
    print("="*80)
    
    # Determine contracts to verify
    if args.contracts:
        qids = [q.strip() for q in args.contracts.split(',')]
    elif args.group is not None:
        base = args.group + 1
        qids = [f"Q{base + (i * 30):03d}" for i in range(10)]
    elif args.all:
        qids = [f"Q{i:03d}" for i in range(1, 301)]
    else:
        # Default: first group
        qids = [f"Q{i:03d}" for i in [1, 31, 61, 91, 121, 151, 181, 211, 241, 271]]
    
    print(f"\n📋 Loading {len(qids)} contracts...")
    
    # Load contracts
    contracts = {}
    for qid in qids:
        contract = load_contract(qid)
        if contract: 
            contracts[qid] = contract
            print(f"  ✓ Loaded {qid}")
        else:
            print(f"  ✗ Failed to load {qid}")
    
    if not contracts: 
        print("\n❌ No contracts loaded!")
        return 1
    
    print(f"\n🔍 Running verification on {len(contracts)} contracts...")
    
    # Run verification
    verifier = ContractVerifier(strict_mode=args.strict)
    report = verifier.verify_contracts(contracts, golden_id=args.golden)
    
    # Display results
    report.print_summary(verbose=args.verbose)
    
    # Save reports
    if args.json_report:
        with open(args.json_report, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\n📄 JSON report saved: {args.json_report}")
    
    if args.html_report:
        generate_html_report(report, Path(args.html_report))
        print(f"🌐 HTML report saved: {args.html_report}")
    
    # Exit code
    if report.critical_failures:
        print(f"\n❌ Verification failed: {len(report.critical_failures)} critical issues")
        return 1
    elif args.strict and report.failed_count > 0:
        print(f"\n❌ Strict mode: {report.failed_count} failures")
        return 1
    else:
        print(f"\n✅ Verification {'passed' if report.failed_count == 0 else 'completed with warnings'}")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
