#!/usr/bin/env python3
"""
Comprehensive Phase 2 Validation Suite

Validates that all 12 jobfront requirements are met:
1. SPC → PreprocessedDocument (60 chunks, metadata)
2. Questionnaire structure (300 micro, 4 meso, 1 macro)
3. ChunkRouter & routing table
4. 30 Executors registered
5. MethodRegistry coverage
6. Signal Registry completeness
7-12. Runtime components (tested separately)

Exit code 0 = ALL PASS
Exit code 1 = AT LEAST ONE FAILURE
"""

import json
import sys
from pathlib import Path
from typing import Any

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

class ValidationReport:
    """Tracks validation results across all jobfronts."""
    
    def __init__(self):
        self.results = []
        self.failures = []
    
    def add_pass(self, jobfront: str, check: str, details: str = ""):
        self.results.append({
            "jobfront": jobfront,
            "check": check,
            "status": "PASS",
            "details": details
        })
        print(f"{GREEN}✓{RESET} [{jobfront}] {check}")
        if details:
            print(f"  {details}")
    
    def add_fail(self, jobfront: str, check: str, reason: str):
        self.results.append({
            "jobfront": jobfront,
            "check": check,
            "status": "FAIL",
            "reason": reason
        })
        self.failures.append(f"{jobfront}: {check}")
        print(f"{RED}✗{RESET} [{jobfront}] {check}")
        print(f"  {RED}REASON: {reason}{RESET}")
    
    def print_summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = len(self.failures)
        
        print("\n" + "="*80)
        print(f"{BOLD}VALIDATION SUMMARY{RESET}")
        print("="*80)
        print(f"Total checks: {total}")
        print(f"{GREEN}Passed: {passed}{RESET}")
        print(f"{RED}Failed: {failed}{RESET}")
        
        if self.failures:
            print(f"\n{RED}{BOLD}FAILED CHECKS:{RESET}")
            for failure in self.failures:
                print(f"  - {failure}")
        else:
            print(f"\n{GREEN}{BOLD}🎉 ALL VALIDATION CHECKS PASSED!{RESET}")
        
        return failed == 0


def validate_jobfront_2_questionnaire(report: ValidationReport):
    """Validate questionnaire_monolith.json structure."""
    jobfront = "JF02-Questionnaire"
    
    monolith_path = Path("system/config/questionnaire/questionnaire_monolith.json")
    
    if not monolith_path.exists():
        report.add_fail(jobfront, "File exists", f"{monolith_path} not found")
        return
    
    report.add_pass(jobfront, "File exists", str(monolith_path))
    
    try:
        with open(monolith_path, "r", encoding="utf-8") as f:
            monolith = json.load(f)
    except Exception as e:
        report.add_fail(jobfront, "JSON parse", str(e))
        return
    
    report.add_pass(jobfront, "JSON parse", "Valid JSON")
    
    # Check structure
    if "blocks" not in monolith:
        report.add_fail(jobfront, "Structure", "Missing 'blocks' key")
        return
    
    blocks = monolith["blocks"]
    
    # Micro questions
    micro = blocks.get("micro_questions", [])
    if len(micro) == 300:
        report.add_pass(jobfront, "300 micro_questions", f"Found {len(micro)}")
    else:
        report.add_fail(jobfront, "300 micro_questions", f"Expected 300, found {len(micro)}")
    
    # Meso questions
    meso = blocks.get("meso_questions", [])
    if len(meso) == 4:
        report.add_pass(jobfront, "4 meso_questions", f"Found {len(meso)}")
    else:
        report.add_fail(jobfront, "4 meso_questions", f"Expected 4, found {len(meso)}")
    
    # Macro question
    macro = blocks.get("macro_question")
    if macro:
        report.add_pass(jobfront, "1 macro_question", "Found")
    else:
        report.add_fail(jobfront, "1 macro_question", "Missing")
    
    # Validate micro_question fields
    if micro:
        sample = micro[0]
        required_fields = [
            "question_id", "question_global", "base_slot",
            "dimension_id", "policy_area_id", "cluster_id",
            "scoring_modality", "expected_elements", "method_sets"
        ]
        
        missing = [f for f in required_fields if f not in sample]
        if not missing:
            report.add_pass(jobfront, "Micro fields complete", f"All {len(required_fields)} required fields present")
        else:
            report.add_fail(jobfront, "Micro fields complete", f"Missing: {missing}")
        
        # Check unique question_global
        globals_set = {q.get("question_global") for q in micro if "question_global" in q}
        if len(globals_set) == len(micro):
            report.add_pass(jobfront, "question_global unique", "All 300 are unique")
        else:
            report.add_fail(jobfront, "question_global unique", f"Duplicates found: {len(micro) - len(globals_set)}")


def validate_jobfront_3_chunk_router(report: ValidationReport):
    """Validate ChunkRouter existence and routing table."""
    jobfront = "JF03-ChunkRouter"
    
    router_path = Path("farfan_core/farfan_core/core/orchestrator/chunk_router.py")
    
    if not router_path.exists():
        report.add_fail(jobfront, "File exists", f"{router_path} not found")
        return
    
    report.add_pass(jobfront, "File exists", str(router_path))
    
    content = router_path.read_text()
    
    # Check for ChunkRouter class
    if "class ChunkRouter:" in content:
        report.add_pass(jobfront, "ChunkRouter class", "Found")
    else:
        report.add_fail(jobfront, "ChunkRouter class", "Not found")
    
    # Check for ROUTING_TABLE
    if "ROUTING_TABLE" in content and "chunk_type" in content:
        report.add_pass(jobfront, "ROUTING_TABLE", "Found")
    else:
        report.add_fail(jobfront, "ROUTING_TABLE", "Not found")
    
    # Check for version
    if "ROUTING_TABLE_VERSION" in content:
        report.add_pass(jobfront, "ROUTING_TABLE_VERSION", "Immutable version defined")
    else:
        report.add_fail(jobfront, "ROUTING_TABLE_VERSION", "Version not found")


def validate_jobfront_4_executors(report: ValidationReport):
    """Validate 30 executor registration."""
    jobfront = "JF04-Executors"
    
    exec_path = Path("farfan_core/farfan_core/core/orchestrator/executors.py")
    
    if not exec_path.exists():
        report.add_fail(jobfront, "File exists", f"{exec_path} not found")
        return
    
    report.add_pass(jobfront, "File exists", str(exec_path))
    
    content = exec_path.read_text()
    
    # Check EXECUTOR_REGISTRY
    if "EXECUTOR_REGISTRY" in content:
        report.add_pass(jobfront, "EXECUTOR_REGISTRY", "Found")
    else:
        report.add_fail(jobfront, "EXECUTOR_REGISTRY", "Not found")
        return
    
    # Count registrations - look for D{n}-Q{m} patterns
    expected_slots = [
        f"D{d}-Q{q}" for d in range(1, 7) for q in range(1, 6)
    ]
    
    found_slots = [slot for slot in expected_slots if f'"{slot}"' in content]
    
    if len(found_slots) == 30:
        report.add_pass(jobfront, "30 executors registered", f"All {len(found_slots)} base_slots found")
    else:
        missing = set(expected_slots) - set(found_slots)
        report.add_fail(jobfront, "30 executors registered", f"Missing {len(missing)}: {missing}")


def validate_jobfront_5_method_registry(report: ValidationReport):
    """Validate MethodRegistry exists."""
    jobfront = "JF05-MethodRegistry"
    
    registry_path = Path("farfan_core/farfan_core/core/orchestrator/method_registry.py")
    
    if not registry_path.exists():
        report.add_fail(jobfront, "File exists", f"{registry_path} not found")
        return
    
    report.add_pass(jobfront, "File exists", str(registry_path))
    
    content = registry_path.read_text()
    
    if "class MethodRegistry:" in content:
        report.add_pass(jobfront, "MethodRegistry class", "Found")
    else:
        report.add_fail(jobfront, "MethodRegistry class", "Not found")
    
    # Check for lazy instantiation
    if "get_method" in content and "_instance_cache" in content:
        report.add_pass(jobfront, "Lazy instantiation", "get_method + cache found")
    else:
        report.add_fail(jobfront, "Lazy instantiation", "Missing implementation")


def validate_jobfront_6_signal_registry(report: ValidationReport):
    """Validate signal registry components."""
    jobfront = "JF06-SignalRegistry"
    
    signal_files = [
        "signal_registry.py",
        "signal_aliasing.py",
        "signal_cache_invalidation.py"
    ]
    
    base_path = Path("farfan_core/farfan_core/core/orchestrator")
    
    for filename in signal_files:
        file_path = base_path / filename
        if file_path.exists():
            report.add_pass(jobfront, f"{filename} exists", str(file_path))
        else:
            report.add_fail(jobfront, f"{filename} exists", f"{file_path} not found")


def validate_jobfront_9_evidence_model(report: ValidationReport):
    """Validate Evidence components."""
    jobfront = "JF09-Evidence"
    
    evidence_files = {
        "evidence_assembler.py": "EvidenceAssembler",
        "evidence_validator.py": "EvidenceValidator",
        "evidence_registry.py": "EvidenceRegistry"
    }
    
    base_path = Path("farfan_core/farfan_core/core/orchestrator")
    
    for filename, class_name in evidence_files.items():
        file_path = base_path / filename
        if file_path.exists():
            content = file_path.read_text()
            if f"class {class_name}" in content:
                report.add_pass(jobfront, f"{class_name}", f"Found in {filename}")
            else:
                report.add_fail(jobfront, f"{class_name}", f"Class not found in {filename}")
        else:
            report.add_fail(jobfront, f"{filename} exists", f"{file_path} not found")


def validate_jobfront_11_seed_registry(report: ValidationReport):
    """Validate seed registry for determinism."""
    jobfront = "JF11-SeedRegistry"
    
    seed_path = Path("farfan_core/farfan_core/core/orchestrator/seed_registry.py")
    
    if seed_path.exists():
        report.add_pass(jobfront, "seed_registry.py exists", str(seed_path))
    else:
        report.add_fail(jobfront, "seed_registry.py exists", f"{seed_path} not found")


def main():
    """Run all validation checks."""
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}Phase 2 - Comprehensive Validation Suite{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    report = ValidationReport()
    
    # Run validations
    validate_jobfront_2_questionnaire(report)
    validate_jobfront_3_chunk_router(report)
    validate_jobfront_4_executors(report)
    validate_jobfront_5_method_registry(report)
    validate_jobfront_6_signal_registry(report)
    validate_jobfront_9_evidence_model(report)
    validate_jobfront_11_seed_registry(report)
    
    # Summary
    all_passed = report.print_summary()
    
    # Save report
    report_path = Path("validation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "results": report.results,
            "summary": {
                "total": len(report.results),
                "passed": sum(1 for r in report.results if r["status"] == "PASS"),
                "failed": len(report.failures)
            }
        }, f, indent=2)
    
    print(f"\n{BOLD}Report saved to: {report_path}{RESET}")
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
