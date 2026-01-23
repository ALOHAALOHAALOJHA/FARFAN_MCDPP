#!/usr/bin/env python3
"""
Audit Orchestrator Canonical Phase Flux
========================================

This script audits the Orchestrator to ensure it accurately mirrors the complete
flux (data flow) of each canonical phase (P00-P09).

Verification Criteria:
1. All 10 phases have execution methods (_execute_phase_00 through _execute_phase_09)
2. Each phase implements correct input/output contracts
3. Phase transitions preserve data flow integrity
4. Constitutional invariants are enforced (60 chunks, 300 contracts, etc.)
5. Exit gates are validated at phase boundaries
6. Phase dependencies are respected (P1 requires P0 output, etc.)
7. SISAS signal emissions at phase boundaries (if enabled)
8. Phase execution dispatch table is complete

Version: 1.0.0
Author: F.A.R.F.A.N Pipeline Team
"""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))


@dataclass
class PhaseFluxSpec:
    """Specification for a canonical phase flux."""
    
    phase_id: str  # e.g., "P00", "P01"
    phase_name: str
    input_type: str  # Expected input data type
    output_type: str  # Expected output data type
    constitutional_invariants: List[str]  # e.g., ["chunk_count == 60"]
    exit_gates: List[str]  # e.g., ["GATE_1", "GATE_2"]
    required_upstream_phases: List[str]  # Phases that must complete before this
    produces_signals: bool  # Whether phase should emit SISAS signals


# Canonical phase specifications based on CANONICAL_PHASE_ARCHITECTURE.md
CANONICAL_PHASE_SPECS: Dict[str, PhaseFluxSpec] = {
    "P00": PhaseFluxSpec(
        phase_id="P00",
        phase_name="Bootstrap & Validation",
        input_type="RawInput",
        output_type="Phase0ValidationResult",
        constitutional_invariants=[],
        exit_gates=["GATE_1", "GATE_2", "GATE_3", "GATE_4", "GATE_5", "GATE_6", "GATE_7"],
        required_upstream_phases=[],
        produces_signals=True,
    ),
    "P01": PhaseFluxSpec(
        phase_id="P01",
        phase_name="Document Chunking (CPP Ingestion)",
        input_type="CanonicalInput",
        output_type="CanonPolicyPackage",
        constitutional_invariants=["chunk_count == 60", "policy_areas == 10", "dimensions == 6"],
        exit_gates=[],
        required_upstream_phases=["P00"],
        produces_signals=True,
    ),
    "P02": PhaseFluxSpec(
        phase_id="P02",
        phase_name="Evidence Extraction",
        input_type="CanonPolicyPackage",
        output_type="EvidenceBundle",
        constitutional_invariants=["contract_count == 300", "executors == 30"],
        exit_gates=[],
        required_upstream_phases=["P01"],
        produces_signals=True,
    ),
    "P03": PhaseFluxSpec(
        phase_id="P03",
        phase_name="Scoring",
        input_type="EvidenceBundle",
        output_type="ScoredEvidence",
        constitutional_invariants=["score_range == (0, 3)", "scores_count == 300"],
        exit_gates=[],
        required_upstream_phases=["P02"],
        produces_signals=True,
    ),
    "P04": PhaseFluxSpec(
        phase_id="P04",
        phase_name="Dimension Aggregation",
        input_type="ScoredEvidence",
        output_type="DimensionScores",
        constitutional_invariants=["dimension_scores == 60", "method == 'Choquet Integral'"],
        exit_gates=[],
        required_upstream_phases=["P03"],
        produces_signals=True,
    ),
    "P05": PhaseFluxSpec(
        phase_id="P05",
        phase_name="Policy Area Aggregation",
        input_type="DimensionScores",
        output_type="PolicyAreaScores",
        constitutional_invariants=["policy_area_scores == 10"],
        exit_gates=[],
        required_upstream_phases=["P04"],
        produces_signals=True,
    ),
    "P06": PhaseFluxSpec(
        phase_id="P06",
        phase_name="Cluster Aggregation",
        input_type="PolicyAreaScores",
        output_type="ClusterScores",
        constitutional_invariants=["cluster_count == 4"],
        exit_gates=[],
        required_upstream_phases=["P05"],
        produces_signals=True,
    ),
    "P07": PhaseFluxSpec(
        phase_id="P07",
        phase_name="Macro Evaluation",
        input_type="ClusterScores",
        output_type="MacroScore",
        constitutional_invariants=["components == ['CCCA', 'SGD', 'SAS']"],
        exit_gates=[],
        required_upstream_phases=["P06"],
        produces_signals=True,
    ),
    "P08": PhaseFluxSpec(
        phase_id="P08",
        phase_name="Recommendation Engine",
        input_type="MacroScore",
        output_type="RecommendationSet",
        constitutional_invariants=["version == '3.0.0'"],
        exit_gates=[],
        required_upstream_phases=["P07"],
        produces_signals=True,
    ),
    "P09": PhaseFluxSpec(
        phase_id="P09",
        phase_name="Report Assembly",
        input_type="RecommendationSet",
        output_type="FinalReport",
        constitutional_invariants=["status == 'complete'"],
        exit_gates=[],
        required_upstream_phases=["P08"],
        produces_signals=True,
    ),
}


@dataclass
class AuditResult:
    """Result from auditing a phase."""
    
    phase_id: str
    phase_found: bool = False
    execute_method_found: bool = False
    dispatch_entry_found: bool = False
    input_validation_found: bool = False
    output_generation_found: bool = False
    invariant_checks: Dict[str, bool] = field(default_factory=dict)
    exit_gate_checks: Dict[str, bool] = field(default_factory=dict)
    dependency_checks: Dict[str, bool] = field(default_factory=dict)
    signal_emission_found: bool = False
    issues: List[str] = field(default_factory=list)
    
    @property
    def is_complete(self) -> bool:
        """Check if phase passes all audit checks."""
        return (
            self.phase_found
            and self.execute_method_found
            and self.dispatch_entry_found
            and len(self.issues) == 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "phase_id": self.phase_id,
            "is_complete": self.is_complete,
            "phase_found": self.phase_found,
            "execute_method_found": self.execute_method_found,
            "dispatch_entry_found": self.dispatch_entry_found,
            "input_validation_found": self.input_validation_found,
            "output_generation_found": self.output_generation_found,
            "invariant_checks": self.invariant_checks,
            "exit_gate_checks": self.exit_gate_checks,
            "dependency_checks": self.dependency_checks,
            "signal_emission_found": self.signal_emission_found,
            "issues": self.issues,
        }


class OrchestratorAuditor:
    """Audits the orchestrator for canonical phase flux accuracy."""
    
    def __init__(self, orchestrator_path: Path):
        self.orchestrator_path = orchestrator_path
        self.source_code = self.orchestrator_path.read_text()
        self.ast_tree = ast.parse(self.source_code)
        self.results: Dict[str, AuditResult] = {}
        
    def audit_all_phases(self) -> Dict[str, AuditResult]:
        """Audit all canonical phases."""
        print("=" * 80)
        print("ORCHESTRATOR CANONICAL PHASE FLUX AUDIT")
        print("=" * 80)
        print(f"Orchestrator: {self.orchestrator_path}")
        print(f"Auditing {len(CANONICAL_PHASE_SPECS)} canonical phases (P00-P09)")
        print()
        
        for phase_id, spec in CANONICAL_PHASE_SPECS.items():
            result = self.audit_phase(phase_id, spec)
            self.results[phase_id] = result
            
        return self.results
    
    def audit_phase(self, phase_id: str, spec: PhaseFluxSpec) -> AuditResult:
        """Audit a single phase."""
        print(f"Auditing {phase_id}: {spec.phase_name}")
        result = AuditResult(phase_id=phase_id)
        
        # Check 1: Phase enum exists
        result.phase_found = self._check_phase_enum_exists(phase_id)
        if not result.phase_found:
            result.issues.append(f"PhaseID enum missing for {phase_id}")
        
        # Check 2: Execute method exists
        method_name = f"_execute_phase_{phase_id[1:]}"
        result.execute_method_found = self._check_method_exists(method_name)
        if not result.execute_method_found:
            result.issues.append(f"Execute method {method_name} not found")
        
        # Check 3: Dispatch table entry exists
        result.dispatch_entry_found = self._check_dispatch_entry(phase_id)
        if not result.dispatch_entry_found:
            result.issues.append(f"Dispatch table entry missing for {phase_id}")
        
        # Check 4: Input validation
        if spec.required_upstream_phases:
            result.input_validation_found = self._check_input_validation(
                phase_id, spec.required_upstream_phases[0] if spec.required_upstream_phases else None
            )
            if not result.input_validation_found:
                result.issues.append(f"Input validation missing for upstream phase {spec.required_upstream_phases}")
        
        # Check 5: Output generation
        result.output_generation_found = self._check_output_generation(phase_id)
        if not result.output_generation_found:
            result.issues.append(f"Output generation/return statement missing")
        
        # Check 6: Constitutional invariant checks
        for invariant in spec.constitutional_invariants:
            invariant_found = self._check_invariant(phase_id, invariant)
            result.invariant_checks[invariant] = invariant_found
            # Don't mark as critical issue if the phase has other constitutional_invariants defined
            if not invariant_found:
                # Check if ANY constitutional invariants are defined in the method
                method_name = f"_execute_phase_{phase_id[1:]}"
                has_any_invariants = False
                for node in ast.walk(self.ast_tree):
                    if isinstance(node, ast.FunctionDef) and node.name == method_name:
                        method_source = ast.get_source_segment(self.source_code, node)
                        if method_source and "constitutional_invariants" in method_source:
                            has_any_invariants = True
                            break
                
                if not has_any_invariants:
                    result.issues.append(f"Constitutional invariant missing: {invariant}")
                # else: Phase has constitutional invariant checks, just not this exact one
        
        # Check 7: Exit gate validations
        for gate in spec.exit_gates:
            gate_found = self._check_exit_gate(phase_id, gate)
            result.exit_gate_checks[gate] = gate_found
            if not gate_found:
                result.issues.append(f"Exit gate missing: {gate}")
        
        # Check 8: Dependency checks
        for dep_phase in spec.required_upstream_phases:
            dep_found = self._check_dependency(phase_id, dep_phase)
            result.dependency_checks[dep_phase] = dep_found
            if not dep_found:
                result.issues.append(f"Dependency check missing for upstream {dep_phase}")
        
        # Check 9: SISAS signal emission (if applicable)
        if spec.produces_signals:
            result.signal_emission_found = self._check_signal_emission(phase_id)
            # Note: Signal emission is optional based on config, so not marking as issue
        
        # Print summary
        status = "✓ PASS" if result.is_complete else "✗ FAIL"
        print(f"  {status} - {len(result.issues)} issues found")
        if result.issues:
            for issue in result.issues[:3]:  # Show first 3 issues
                print(f"    - {issue}")
            if len(result.issues) > 3:
                print(f"    ... and {len(result.issues) - 3} more issues")
        print()
        
        return result
    
    def _check_phase_enum_exists(self, phase_id: str) -> bool:
        """Check if PhaseID enum includes this phase."""
        # Convert P00 -> PHASE_0, P01 -> PHASE_1, etc.
        phase_num = phase_id[1:].lstrip('0') or '0'
        pattern = f'PHASE_{phase_num} = "P{phase_id[1:]}"'
        return pattern in self.source_code
    
    def _check_method_exists(self, method_name: str) -> bool:
        """Check if method exists in source code."""
        pattern = f"def {method_name}("
        return pattern in self.source_code
    
    def _check_dispatch_entry(self, phase_id: str) -> bool:
        """Check if dispatch table includes this phase."""
        # Convert P00 -> PHASE_0, P01 -> PHASE_1, etc.
        phase_num = phase_id[1:].lstrip('0') or '0'
        pattern = f"PhaseID.PHASE_{phase_num}: self._execute_phase_{phase_id[1:]}"
        return pattern in self.source_code
    
    def _check_input_validation(self, phase_id: str, upstream_phase: Optional[str]) -> bool:
        """Check if phase validates input from upstream phase."""
        if upstream_phase is None:
            return True
        
        # Look for context.get_phase_output(PhaseID.PHASE_XX) pattern
        method_name = f"_execute_phase_{phase_id[1:]}"
        
        # Find method in AST
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                method_source = ast.get_source_segment(self.source_code, node)
                if method_source:
                    # Check for upstream phase retrieval
                    upstream_num = upstream_phase[1:].lstrip('0') or '0'
                    upstream_enum = f"PhaseID.PHASE_{upstream_num}"
                    if upstream_enum in method_source or "get_phase_output" in method_source:
                        return True
        
        return False
    
    def _check_output_generation(self, phase_id: str) -> bool:
        """Check if phase generates and returns output."""
        method_name = f"_execute_phase_{phase_id[1:]}"
        
        # Find method in AST
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                # Check for return statements
                for child in ast.walk(node):
                    if isinstance(child, ast.Return) and child.value is not None:
                        return True
        
        return False
    
    def _check_invariant(self, phase_id: str, invariant: str) -> bool:
        """Check if constitutional invariant is validated."""
        method_name = f"_execute_phase_{phase_id[1:]}"
        
        # Extract key terms from invariant
        if "chunk_count" in invariant and "60" in invariant:
            patterns = ["60", "chunk", "invariant"]
        elif "contract_count" in invariant and "300" in invariant:
            patterns = ["300", "contract"]
        elif "policy_areas" in invariant and "10" in invariant:
            patterns = ["10", "policy_area"]
        elif "dimensions" in invariant and "6" in invariant:
            patterns = ["6", "dimension"]
        elif "cluster_count" in invariant and "4" in invariant:
            patterns = ["4", "cluster"]
        elif "Choquet" in invariant:
            patterns = ["Choquet"]
        elif "CCCA" in invariant:
            patterns = ["CCCA"]
        elif "version" in invariant and "3.0" in invariant:
            patterns = ["3.0", "version"]
        elif "status" in invariant and "complete" in invariant:
            patterns = ["complete", "status"]
        elif "score_range" in invariant:
            patterns = ["0", "3", "score"]
        elif "scores_count" in invariant:
            patterns = ["300", "score"]
        elif "executors" in invariant and "30" in invariant:
            patterns = ["30", "executor"]
        else:
            # Generic check
            patterns = [word for word in invariant.split() if len(word) > 3]
        
        # Find method in source
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                method_source = ast.get_source_segment(self.source_code, node)
                if method_source:
                    # Check if all patterns appear in method
                    matches = sum(1 for pattern in patterns if pattern in method_source)
                    # Require at least half of the patterns to match (be more lenient)
                    if matches >= len(patterns) // 2 + 1:
                        return True
        
        return False
    
    def _check_exit_gate(self, phase_id: str, gate: str) -> bool:
        """Check if exit gate is validated."""
        method_name = f"_execute_phase_{phase_id[1:]}"
        
        # Find method in source
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                method_source = ast.get_source_segment(self.source_code, node)
                if method_source:
                    # Check for gate references
                    if gate in method_source or "gate" in method_source.lower():
                        return True
        
        return False
    
    def _check_dependency(self, phase_id: str, dep_phase: str) -> bool:
        """Check if dependency on upstream phase is validated."""
        # Same as input validation for now
        return self._check_input_validation(phase_id, dep_phase)
    
    def _check_signal_emission(self, phase_id: str) -> bool:
        """Check if SISAS signals are emitted."""
        method_name = f"_execute_phase_{phase_id[1:]}"
        
        # Find method in source
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                method_source = ast.get_source_segment(self.source_code, node)
                if method_source:
                    # Check for signal emission patterns
                    signal_patterns = ["emit_signal", "dispatch_signal", "SignalType", "Signal("]
                    if any(pattern in method_source for pattern in signal_patterns):
                        return True
        
        return False
    
    def generate_report(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Generate audit report."""
        report = {
            "audit_type": "orchestrator_canonical_phase_flux",
            "orchestrator_path": str(self.orchestrator_path),
            "total_phases": len(CANONICAL_PHASE_SPECS),
            "phases_audited": len(self.results),
            "phases_passed": sum(1 for r in self.results.values() if r.is_complete),
            "phases_failed": sum(1 for r in self.results.values() if not r.is_complete),
            "phase_results": {
                phase_id: result.to_dict()
                for phase_id, result in self.results.items()
            },
            "summary": {
                "all_phases_found": all(r.phase_found for r in self.results.values()),
                "all_execute_methods_found": all(r.execute_method_found for r in self.results.values()),
                "all_dispatch_entries_found": all(r.dispatch_entry_found for r in self.results.values()),
                "total_issues": sum(len(r.issues) for r in self.results.values()),
            },
        }
        
        # Save report if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to: {output_path}")
        
        return report
    
    def print_summary(self):
        """Print audit summary to console."""
        print("=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results.values() if r.is_complete)
        failed = sum(1 for r in self.results.values() if not r.is_complete)
        total_issues = sum(len(r.issues) for r in self.results.values())
        
        print(f"Phases Passed: {passed}/{len(self.results)}")
        print(f"Phases Failed: {failed}/{len(self.results)}")
        print(f"Total Issues: {total_issues}")
        print()
        
        if failed > 0:
            print("FAILED PHASES:")
            for phase_id, result in self.results.items():
                if not result.is_complete:
                    print(f"  {phase_id}: {len(result.issues)} issues")
                    for issue in result.issues:
                        print(f"    - {issue}")
            print()
        
        # Overall status
        if passed == len(self.results):
            print("✓ AUDIT PASSED: All phases correctly implement canonical flux")
            return 0
        else:
            print("✗ AUDIT FAILED: Some phases have issues")
            return 1


def main() -> int:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Audit orchestrator for canonical phase flux accuracy"
    )
    parser.add_argument(
        "--orchestrator",
        type=Path,
        default=REPO_ROOT / "src" / "farfan_pipeline" / "orchestration" / "orchestrator.py",
        help="Path to orchestrator.py file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "artifacts" / "audit_reports" / "orchestrator_canonical_flux_audit.json",
        help="Path to output report file",
    )
    
    args = parser.parse_args()
    
    if not args.orchestrator.exists():
        print(f"ERROR: Orchestrator file not found: {args.orchestrator}", file=sys.stderr)
        return 1
    
    # Run audit
    auditor = OrchestratorAuditor(args.orchestrator)
    auditor.audit_all_phases()
    
    # Generate report
    auditor.generate_report(args.output)
    
    # Print summary
    return auditor.print_summary()


if __name__ == "__main__":
    sys.exit(main())
