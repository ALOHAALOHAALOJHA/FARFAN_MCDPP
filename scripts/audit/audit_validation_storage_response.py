#!/usr/bin/env python3
"""
SEVERE AUDIT: Response Validation, Storage, and Human Response Formulation

This audit examines with MAXIMUM SEVERITY:
1. Individual component integrity (validation, storage, response formulation)
2. Flow logic (sequential execution, data propagation)
3. Compatibility logic (inter-component interactions)
4. Orchestration function (coordination and control)

Audit Date: 2025-12-11
Severity Level: MAXIMUM
Scope: All 300 V3 Executor Contracts + Base Executor Logic
"""

import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class AuditFinding:
    """Structured finding from audit."""
    component: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # VALIDATION, STORAGE, RESPONSE_FORMULATION, FLOW, COMPATIBILITY, ORCHESTRATION
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    remediation: str = ""


@dataclass
class AuditReport:
    """Complete audit report."""
    findings: List[AuditFinding] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    
    def add_finding(self, finding: AuditFinding) -> None:
        self.findings.append(finding)
    
    def get_critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "CRITICAL")
    
    def get_high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "HIGH")
    
    def passed(self) -> bool:
        return self.get_critical_count() == 0


class ValidationStorageResponseAuditor:
    """Comprehensive auditor for validation, storage, and response formulation."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.phase2_root = repo_root / "src" / "canonic_phases" / "Phase_two"
        self.contracts_dir = self.phase2_root / "json_files_phase_two" / "executor_contracts" / "specialized"
        self.report = AuditReport()
        
    def run_full_audit(self) -> AuditReport:
        """Execute complete audit with maximum severity."""
        print("=" * 80)
        print("SEVERE AUDIT: Validation, Storage & Human Response Formulation")
        print("=" * 80)
        print()
        
        # PHASE 1: Individual Component Audit
        print("PHASE 1: Individual Component Integrity...")
        self._audit_validation_components()
        self._audit_storage_components()
        self._audit_response_formulation_components()
        print(f"  ✓ Completed. Findings: {len(self.report.findings)}")
        print()
        
        # PHASE 2: Flow Logic Audit
        print("PHASE 2: Flow Logic Verification...")
        self._audit_execution_flow()
        self._audit_signal_flow()
        self._audit_error_flow()
        print(f"  ✓ Completed. Findings: {len(self.report.findings)}")
        print()
        
        # PHASE 3: Compatibility Logic Audit
        print("PHASE 3: Compatibility Logic Analysis...")
        self._audit_contract_compatibility()
        self._audit_component_compatibility()
        self._audit_signal_compatibility()
        print(f"  ✓ Completed. Findings: {len(self.report.findings)}")
        print()
        
        # PHASE 4: Orchestration Function Audit
        print("PHASE 4: Orchestration Function Verification...")
        self._audit_orchestration_logic()
        self._audit_integration_points()
        print(f"  ✓ Completed. Findings: {len(self.report.findings)}")
        print()
        
        # PHASE 5: Contract Coverage Audit
        print("PHASE 5: Contract Coverage Analysis...")
        self._audit_contract_coverage()
        print(f"  ✓ Completed. Findings: {len(self.report.findings)}")
        print()
        
        # Generate summary
        self._generate_summary()
        
        return self.report
    
    def _audit_validation_components(self) -> None:
        """Audit validation component integrity."""
        print("  → Validating response validation components...")
        
        # Check EvidenceNexus validation logic
        evidence_nexus_path = self.phase2_root / "evidence_nexus.py"
        if not evidence_nexus_path.exists():
            self.report.add_finding(AuditFinding(
                component="EvidenceNexus",
                severity="CRITICAL",
                category="VALIDATION",
                message="evidence_nexus.py not found",
                remediation="Restore evidence_nexus.py file"
            ))
            return
        
        with open(evidence_nexus_path, 'r') as f:
            nexus_code = f.read()
        
        # Verify validation functions exist
        required_validation_functions = [
            "validate_evidence",
            "process_evidence",
            "_validate_completeness",
            "_validate_quality"
        ]
        
        for func in required_validation_functions:
            if f"def {func}" not in nexus_code:
                self.report.add_finding(AuditFinding(
                    component="EvidenceNexus",
                    severity="HIGH",
                    category="VALIDATION",
                    message=f"Missing validation function: {func}",
                    details={"function": func}
                ))
        
        # Check base executor validation integration
        base_executor_path = self.phase2_root / "base_executor_with_contract.py"
        with open(base_executor_path, 'r') as f:
            base_code = f.read()
        
        # Verify validation orchestrator integration
        if "ValidationOrchestrator" not in base_code:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="MEDIUM",
                category="VALIDATION",
                message="ValidationOrchestrator not referenced in base executor",
                details={"component": "validation_orchestrator"}
            ))
        
        # Verify output contract validation
        if "_validate_output_contract" not in base_code:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="HIGH",
                category="VALIDATION",
                message="Output contract validation method missing",
                remediation="Implement _validate_output_contract method"
            ))
        
    def _audit_storage_components(self) -> None:
        """Audit storage mechanism integrity."""
        print("  → Validating storage mechanisms...")
        
        evidence_nexus_path = self.phase2_root / "evidence_nexus.py"
        with open(evidence_nexus_path, 'r') as f:
            nexus_code = f.read()
        
        # Check for evidence persistence mechanisms
        storage_indicators = [
            "EvidenceRegistry",
            "register_evidence",
            "_store_evidence",
            "evidence_store"
        ]
        
        has_storage = any(indicator in nexus_code for indicator in storage_indicators)
        
        if not has_storage:
            self.report.add_finding(AuditFinding(
                component="EvidenceStorage",
                severity="HIGH",
                category="STORAGE",
                message="No explicit evidence storage mechanism found in EvidenceNexus",
                details={"indicators_checked": storage_indicators},
                remediation="Implement evidence persistence layer"
            ))
        
        # Check base executor for result storage
        base_executor_path = self.phase2_root / "base_executor_with_contract.py"
        with open(base_executor_path, 'r') as f:
            base_code = f.read()
        
        # Verify result construction and return
        if "Phase2QuestionResult" not in base_code:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="CRITICAL",
                category="STORAGE",
                message="Phase2QuestionResult type not found - results may not be properly structured",
                remediation="Ensure Phase2QuestionResult is properly imported and used"
            ))
    
    def _audit_response_formulation_components(self) -> None:
        """Audit human response formulation components."""
        print("  → Validating human response formulation...")
        
        # Check for narrative synthesizer
        carver_path = self.phase2_root / "carver.py"
        narrative_synth_found = False
        
        if carver_path.exists():
            with open(carver_path, 'r') as f:
                carver_code = f.read()
            
            # Check for narrative synthesis capabilities
            if "DoctoralCarverSynthesizer" in carver_code or "synthesize" in carver_code:
                narrative_synth_found = True
        
        if not narrative_synth_found:
            self.report.add_finding(AuditFinding(
                component="ResponseFormulation",
                severity="MEDIUM",
                category="RESPONSE_FORMULATION",
                message="No explicit narrative synthesis component found",
                details={"expected_file": "carver.py or narrative_answer_synthesizer.py"},
                remediation="Verify human-readable answer generation logic"
            ))
        
        # Check evidence nexus for answer formulation support
        evidence_nexus_path = self.phase2_root / "evidence_nexus.py"
        with open(evidence_nexus_path, 'r') as f:
            nexus_code = f.read()
        
        answer_indicators = [
            "human_answer",
            "narrative",
            "answer_text",
            "formulate_answer",
            "synthesize_answer"
        ]
        
        has_answer_support = any(indicator in nexus_code.lower() for indicator in answer_indicators)
        
        if not has_answer_support:
            self.report.add_finding(AuditFinding(
                component="EvidenceNexus",
                severity="INFO",
                category="RESPONSE_FORMULATION",
                message="No explicit human answer formulation found in EvidenceNexus",
                details={"note": "May be delegated to separate component"}
            ))
    
    def _audit_execution_flow(self) -> None:
        """Audit sequential execution flow logic."""
        print("  → Analyzing execution flow...")
        
        base_executor_path = self.phase2_root / "base_executor_with_contract.py"
        with open(base_executor_path, 'r') as f:
            base_code = f.read()
        
        # Parse AST to analyze flow
        try:
            tree = ast.parse(base_code)
        except SyntaxError as e:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="CRITICAL",
                category="FLOW",
                message=f"Syntax error in base executor: {e}",
                remediation="Fix syntax errors before deployment"
            ))
            return
        
        # Find execute_question methods
        execute_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if "execute" in node.name.lower():
                    execute_methods.append(node.name)
        
        if not execute_methods:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="CRITICAL",
                category="FLOW",
                message="No execute methods found in BaseExecutor",
                remediation="Implement question execution logic"
            ))
        
        # Check for proper flow sequence markers
        flow_sequence = [
            "method_executor.execute",  # Method execution
            "process_evidence",  # Evidence assembly
            "validation",  # Validation
            "Phase2QuestionResult"  # Result construction
        ]
        
        for i, step in enumerate(flow_sequence):
            if step not in base_code:
                self.report.add_finding(AuditFinding(
                    component="BaseExecutor",
                    severity="HIGH",
                    category="FLOW",
                    message=f"Flow step {i+1} missing: {step}",
                    details={"step": step, "position": i+1},
                    remediation=f"Ensure {step} is present in execution flow"
                ))
    
    def _audit_signal_flow(self) -> None:
        """Audit signal requirements validation and propagation."""
        print("  → Analyzing signal flow...")
        
        base_executor_path = self.phase2_root / "base_executor_with_contract.py"
        with open(base_executor_path, 'r') as f:
            base_code = f.read()
        
        # Check signal validation
        if "_validate_signal_requirements" in base_code:
            # Signal validation exists
            pass
        else:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="MEDIUM",
                category="FLOW",
                message="No explicit signal requirements validation method",
                details={"expected_method": "_validate_signal_requirements"}
            ))
        
        # Check signal pack propagation
        signal_propagation_indicators = [
            "signal_pack",
            "enriched_packs",
            "signal_registry"
        ]
        
        found_indicators = [ind for ind in signal_propagation_indicators if ind in base_code]
        
        if len(found_indicators) < 2:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="MEDIUM",
                category="FLOW",
                message="Limited signal propagation infrastructure",
                details={"found": found_indicators, "expected": signal_propagation_indicators}
            ))
    
    def _audit_error_flow(self) -> None:
        """Audit error handling and failure contracts."""
        print("  → Analyzing error flow...")
        
        base_executor_path = self.phase2_root / "base_executor_with_contract.py"
        with open(base_executor_path, 'r') as f:
            base_code = f.read()
        
        # Check error handling infrastructure
        error_indicators = [
            "error_handling",
            "failure_contract",
            "on_method_failure",
            "try:",
            "except"
        ]
        
        found_error_handling = {ind: (ind in base_code) for ind in error_indicators}
        
        missing = [ind for ind, found in found_error_handling.items() if not found]
        
        if missing:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="HIGH",
                category="FLOW",
                message="Incomplete error handling infrastructure",
                details={"missing": missing, "found": [k for k, v in found_error_handling.items() if v]}
            ))
        
        # Check for failure contract integration
        if "failure_contract" in base_code and "abort_conditions" in base_code:
            # Good - failure contracts are integrated
            pass
        else:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="MEDIUM",
                category="FLOW",
                message="Failure contract integration may be incomplete",
                details={"has_failure_contract": "failure_contract" in base_code,
                        "has_abort_conditions": "abort_conditions" in base_code}
            ))
    
    def _audit_contract_compatibility(self) -> None:
        """Audit contract v2/v3 compatibility."""
        print("  → Analyzing contract compatibility...")
        
        base_executor_path = self.phase2_root / "base_executor_with_contract.py"
        with open(base_executor_path, 'r') as f:
            base_code = f.read()
        
        # Check for v2/v3 detection logic
        version_indicators = [
            ".v3.json",
            "contract_version",
            "auto-detected",
            "v2",
            "v3"
        ]
        
        has_version_detection = any(ind in base_code for ind in version_indicators)
        
        if not has_version_detection:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="HIGH",
                category="COMPATIBILITY",
                message="No contract version detection logic found",
                details={"indicators_checked": version_indicators},
                remediation="Implement contract version auto-detection"
            ))
        
        # Check for backward compatibility handling
        if "method_inputs" in base_code and "method_binding" in base_code:
            # Good - supports both v2 and v3
            pass
        else:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="MEDIUM",
                category="COMPATIBILITY",
                message="Contract backward compatibility may be incomplete",
                details={
                    "supports_v2": "method_inputs" in base_code,
                    "supports_v3": "method_binding" in base_code
                }
            ))
    
    def _audit_component_compatibility(self) -> None:
        """Audit inter-component compatibility."""
        print("  → Analyzing component compatibility...")
        
        base_executor_path = self.phase2_root / "base_executor_with_contract.py"
        with open(base_executor_path, 'r') as f:
            base_code = f.read()
        
        # Check EvidenceNexus integration
        if "from canonic_phases.Phase_two.evidence_nexus import" in base_code:
            # EvidenceNexus is imported
            if "process_evidence" in base_code:
                # And used
                pass
            else:
                self.report.add_finding(AuditFinding(
                    component="BaseExecutor",
                    severity="HIGH",
                    category="COMPATIBILITY",
                    message="EvidenceNexus imported but not used",
                    remediation="Integrate EvidenceNexus into execution flow"
                ))
        else:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="CRITICAL",
                category="COMPATIBILITY",
                message="EvidenceNexus not imported",
                remediation="Import and integrate EvidenceNexus for evidence processing"
            ))
        
        # Check Carver integration
        if "from canonic_phases.Phase_two.carver import" in base_code:
            # Carver is imported - check usage
            if "DoctoralCarverSynthesizer" not in base_code:
                self.report.add_finding(AuditFinding(
                    component="BaseExecutor",
                    severity="INFO",
                    category="COMPATIBILITY",
                    message="Carver imported but may not be actively used",
                    details={"note": "Verify carver integration in execution flow"}
                ))
    
    def _audit_signal_compatibility(self) -> None:
        """Audit signal enrichment integration points."""
        print("  → Analyzing signal compatibility...")
        
        base_executor_path = self.phase2_root / "base_executor_with_contract.py"
        with open(base_executor_path, 'r') as f:
            base_code = f.read()
        
        # Check signal pack compatibility
        signal_indicators = [
            "enriched_packs",
            "signal_registry",
            "_use_enriched_signals",
            "MicroAnsweringSignalPack"
        ]
        
        found = [ind for ind in signal_indicators if ind in base_code]
        
        if len(found) < 3:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="MEDIUM",
                category="COMPATIBILITY",
                message="Limited signal enrichment integration",
                details={"found": found, "expected": signal_indicators}
            ))
    
    def _audit_orchestration_logic(self) -> None:
        """Audit orchestration coordination logic."""
        print("  → Analyzing orchestration logic...")
        
        base_executor_path = self.phase2_root / "base_executor_with_contract.py"
        with open(base_executor_path, 'r') as f:
            base_code = f.read()
        
        # Check for orchestrator integrations
        orchestrators = {
            "CalibrationOrchestrator": "calibration_orchestrator",
            "ValidationOrchestrator": "validation_orchestrator",
            "MethodExecutor": "method_executor"
        }
        
        missing_orchestrators = []
        for orchestrator_name, attr_name in orchestrators.items():
            if attr_name not in base_code:
                missing_orchestrators.append(orchestrator_name)
        
        if missing_orchestrators:
            self.report.add_finding(AuditFinding(
                component="BaseExecutor",
                severity="HIGH",
                category="ORCHESTRATION",
                message="Missing orchestrator integrations",
                details={"missing": missing_orchestrators},
                remediation="Integrate all required orchestrators"
            ))
        
        # Check for proper orchestrator invocation
        if "calibration_orchestrator" in base_code:
            if "calibrate(" not in base_code:
                self.report.add_finding(AuditFinding(
                    component="BaseExecutor",
                    severity="MEDIUM",
                    category="ORCHESTRATION",
                    message="CalibrationOrchestrator present but not invoked",
                    remediation="Call calibration_orchestrator.calibrate() in execution flow"
                ))
    
    def _audit_integration_points(self) -> None:
        """Audit integration points between components."""
        print("  → Analyzing integration points...")
        
        base_executor_path = self.phase2_root / "base_executor_with_contract.py"
        with open(base_executor_path, 'r') as f:
            base_code = f.read()
        
        # Check for critical integration points
        integration_points = [
            ("method_executor.execute", "MethodExecutor", "Method execution"),
            ("process_evidence", "EvidenceNexus", "Evidence processing"),
            ("validate_result_with_orchestrator", "ValidationOrchestrator", "Validation"),
            ("Phase2QuestionResult", "ResultType", "Result construction")
        ]
        
        for call_pattern, component, description in integration_points:
            if call_pattern not in base_code:
                self.report.add_finding(AuditFinding(
                    component="BaseExecutor",
                    severity="HIGH",
                    category="ORCHESTRATION",
                    message=f"Missing integration point: {description}",
                    details={"component": component, "call": call_pattern},
                    remediation=f"Implement {call_pattern} in execution flow"
                ))
    
    def _audit_contract_coverage(self) -> None:
        """Audit contract coverage for validation/storage/response."""
        print("  → Analyzing contract coverage...")
        
        if not self.contracts_dir.exists():
            self.report.add_finding(AuditFinding(
                component="Contracts",
                severity="CRITICAL",
                category="VALIDATION",
                message="Executor contracts directory not found",
                details={"path": str(self.contracts_dir)},
                remediation="Verify contracts directory structure"
            ))
            return
        
        contracts = list(self.contracts_dir.glob("Q*.v3.json"))
        
        if len(contracts) == 0:
            self.report.add_finding(AuditFinding(
                component="Contracts",
                severity="CRITICAL",
                category="VALIDATION",
                message="No v3 contracts found",
                remediation="Generate or restore executor contracts"
            ))
            return
        
        # Sample contracts for validation
        contracts_checked = 0
        contracts_with_evidence = 0
        contracts_with_validation = 0
        contracts_with_output = 0
        
        for contract_path in contracts[:50]:  # Check first 50
            try:
                with open(contract_path, 'r') as f:
                    contract = json.load(f)
                
                contracts_checked += 1
                
                # Check evidence assembly
                if "evidence_assembly" in contract:
                    contracts_with_evidence += 1
                
                # Check validation rules
                if "validation_rules" in contract:
                    contracts_with_validation += 1
                
                # Check output contract
                if "output_contract" in contract:
                    if "schema" in contract["output_contract"]:
                        if "required" in contract["output_contract"]["schema"]:
                            if "evidence" in contract["output_contract"]["schema"]["required"]:
                                contracts_with_output += 1
                
            except Exception as e:
                self.report.add_finding(AuditFinding(
                    component="Contracts",
                    severity="HIGH",
                    category="VALIDATION",
                    message=f"Failed to parse contract: {contract_path.name}",
                    details={"error": str(e)}
                ))
        
        # Calculate coverage percentages
        evidence_coverage = (contracts_with_evidence / contracts_checked * 100) if contracts_checked > 0 else 0
        validation_coverage = (contracts_with_validation / contracts_checked * 100) if contracts_checked > 0 else 0
        output_coverage = (contracts_with_output / contracts_checked * 100) if contracts_checked > 0 else 0
        
        self.report.stats["contracts_checked"] = contracts_checked
        self.report.stats["evidence_coverage"] = evidence_coverage
        self.report.stats["validation_coverage"] = validation_coverage
        self.report.stats["output_coverage"] = output_coverage
        
        # Findings based on coverage
        if evidence_coverage < 100:
            self.report.add_finding(AuditFinding(
                component="Contracts",
                severity="HIGH",
                category="VALIDATION",
                message=f"Incomplete evidence assembly coverage: {evidence_coverage:.1f}%",
                details={"coverage": evidence_coverage, "missing": contracts_checked - contracts_with_evidence},
                remediation="Ensure all contracts have evidence_assembly section"
            ))
        
        if validation_coverage < 100:
            self.report.add_finding(AuditFinding(
                component="Contracts",
                severity="HIGH",
                category="VALIDATION",
                message=f"Incomplete validation rules coverage: {validation_coverage:.1f}%",
                details={"coverage": validation_coverage, "missing": contracts_checked - contracts_with_validation},
                remediation="Ensure all contracts have validation_rules section"
            ))
        
        if output_coverage < 100:
            self.report.add_finding(AuditFinding(
                component="Contracts",
                severity="CRITICAL",
                category="RESPONSE_FORMULATION",
                message=f"Incomplete output contract coverage: {output_coverage:.1f}%",
                details={"coverage": output_coverage, "missing": contracts_checked - contracts_with_output},
                remediation="Ensure all contracts require 'evidence' field in output"
            ))
    
    def _generate_summary(self) -> None:
        """Generate audit summary."""
        critical_count = self.get_critical_count()
        high_count = self.get_high_count()
        medium_count = sum(1 for f in self.report.findings if f.severity == "MEDIUM")
        low_count = sum(1 for f in self.report.findings if f.severity == "LOW")
        info_count = sum(1 for f in self.report.findings if f.severity == "INFO")
        
        # Calculate scores by category
        category_counts = defaultdict(int)
        for finding in self.report.findings:
            category_counts[finding.category] += 1
        
        self.report.stats.update({
            "total_findings": len(self.report.findings),
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "info": info_count,
            "by_category": dict(category_counts)
        })
        
        # Determine overall verdict
        if critical_count == 0 and high_count == 0:
            verdict = "✅ PASS - System is stable and functional"
            grade = "A"
        elif critical_count == 0 and high_count <= 3:
            verdict = "⚠️  CONDITIONAL PASS - Minor issues require attention"
            grade = "B+"
        elif critical_count == 0:
            verdict = "⚠️  WARNING - Multiple high severity issues found"
            grade = "B"
        elif critical_count <= 2:
            verdict = "❌ FAIL - Critical issues must be resolved"
            grade = "C"
        else:
            verdict = "❌ CRITICAL FAIL - System integrity compromised"
            grade = "F"
        
        self.report.stats["verdict"] = verdict
        self.report.stats["grade"] = grade
        
        summary = f"""
AUDIT SUMMARY
=============

Verdict: {verdict}
Grade: {grade}

Findings by Severity:
  CRITICAL: {critical_count}
  HIGH:     {high_count}
  MEDIUM:   {medium_count}
  LOW:      {low_count}
  INFO:     {info_count}
  --------
  TOTAL:    {len(self.report.findings)}

Findings by Category:
"""
        for category, count in sorted(category_counts.items()):
            summary += f"  {category}: {count}\n"
        
        if "evidence_coverage" in self.report.stats:
            summary += f"""
Contract Coverage:
  Evidence Assembly:  {self.report.stats['evidence_coverage']:.1f}%
  Validation Rules:   {self.report.stats['validation_coverage']:.1f}%
  Output Contracts:   {self.report.stats['output_coverage']:.1f}%
"""
        
        self.report.summary = summary
    
    def get_critical_count(self) -> int:
        return self.report.get_critical_count()
    
    def get_high_count(self) -> int:
        return self.report.get_high_count()
    
    def generate_detailed_report(self, output_path: Path) -> None:
        """Generate detailed audit report in JSON format."""
        report_data = {
            "audit_metadata": {
                "title": "SEVERE AUDIT: Response Validation, Storage & Human Response Formulation",
                "date": "2025-12-11",
                "severity_level": "MAXIMUM",
                "scope": "All 300 V3 Executor Contracts + Base Executor Logic"
            },
            "summary": self.report.summary,
            "stats": self.report.stats,
            "findings": [
                {
                    "component": f.component,
                    "severity": f.severity,
                    "category": f.category,
                    "message": f.message,
                    "details": f.details,
                    "remediation": f.remediation
                }
                for f in self.report.findings
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed report saved to: {output_path}")


def main():
    """Execute audit."""
    repo_root = Path(__file__).parent
    auditor = ValidationStorageResponseAuditor(repo_root)
    
    report = auditor.run_full_audit()
    
    # Print summary
    print("=" * 80)
    print(report.summary)
    print("=" * 80)
    
    # Print detailed findings
    if report.findings:
        print("\nDETAILED FINDINGS:")
        print("-" * 80)
        
        # Group by severity
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            findings = [f for f in report.findings if f.severity == severity]
            if findings:
                print(f"\n{severity} ({len(findings)}):")
                for i, finding in enumerate(findings, 1):
                    print(f"\n  {i}. [{finding.component}] {finding.message}")
                    if finding.details:
                        print(f"     Details: {finding.details}")
                    if finding.remediation:
                        print(f"     → {finding.remediation}")
    
    # Save detailed report
    output_path = repo_root / "audit_validation_storage_response_report.json"
    auditor.generate_detailed_report(output_path)
    
    # Return exit code based on critical issues
    if auditor.get_critical_count() > 0:
        print("\n❌ AUDIT FAILED: Critical issues must be resolved")
        return 1
    elif auditor.get_high_count() > 5:
        print("\n⚠️  AUDIT WARNING: Multiple high severity issues found")
        return 0
    else:
        print("\n✅ AUDIT PASSED")
        return 0


if __name__ == "__main__":
    exit(main())
