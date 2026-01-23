#!/usr/bin/env python3
"""
Audit Phase Topological Order
==============================

This script performs static analysis of each canonical phase by:
1. Reading each phase's README.md to extract dependencies and specifications
2. Verifying the topological order matches orchestration
3. Ensuring no circular dependencies exist
4. Validating phase boundaries and data flow

Version: 1.0.0
Author: F.A.R.F.A.N Pipeline Team
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))


@dataclass
class PhaseMetadata:
    """Metadata extracted from phase README."""
    
    phase_id: str  # e.g., "P00", "P01"
    phase_name: str
    readme_path: Path
    input_from: List[str]  # List of upstream phases
    output_to: List[str]  # List of downstream phases
    constitutional_invariants: List[str]
    position_in_pipeline: str
    key_outputs: List[str]
    readme_excerpt: str = ""


@dataclass
class TopologicalAuditResult:
    """Result from topological audit."""
    
    phase_id: str
    readme_found: bool = False
    dependencies_extracted: bool = False
    upstream_phases: List[str] = field(default_factory=list)
    downstream_phases: List[str] = field(default_factory=list)
    topological_order_correct: bool = False
    issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "phase_id": self.phase_id,
            "readme_found": self.readme_found,
            "dependencies_extracted": self.dependencies_extracted,
            "upstream_phases": self.upstream_phases,
            "downstream_phases": self.downstream_phases,
            "topological_order_correct": self.topological_order_correct,
            "issues": self.issues,
        }


class PhaseTopologicalAuditor:
    """Audits phase topological order by reading READMEs."""
    
    def __init__(self, phases_dir: Path):
        self.phases_dir = phases_dir
        self.phase_metadata: Dict[str, PhaseMetadata] = {}
        self.audit_results: Dict[str, TopologicalAuditResult] = {}
        
        # Expected canonical order
        self.canonical_order = [
            "P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09"
        ]
        
    def audit_all_phases(self) -> Dict[str, TopologicalAuditResult]:
        """Audit all canonical phases."""
        print("=" * 80)
        print("PHASE TOPOLOGICAL ORDER AUDIT")
        print("=" * 80)
        print(f"Phases directory: {self.phases_dir}")
        print(f"Auditing {len(self.canonical_order)} canonical phases")
        print()
        
        # Step 1: Extract metadata from each phase README
        for phase_id in self.canonical_order:
            metadata = self.extract_phase_metadata(phase_id)
            if metadata:
                self.phase_metadata[phase_id] = metadata
        
        # Step 2: Audit topological order
        for phase_id in self.canonical_order:
            result = self.audit_phase_topology(phase_id)
            self.audit_results[phase_id] = result
        
        # Step 3: Verify no circular dependencies
        self.verify_no_cycles()
        
        return self.audit_results
    
    def extract_phase_metadata(self, phase_id: str) -> Optional[PhaseMetadata]:
        """Extract metadata from phase README."""
        phase_num = phase_id[1:]  # "00", "01", etc.
        phase_dir = self.phases_dir / f"Phase_{phase_num}"
        readme_path = phase_dir / "README.md"
        
        if not readme_path.exists():
            print(f"⚠ {phase_id}: README not found at {readme_path}")
            return None
        
        print(f"Reading {phase_id}: {readme_path}")
        
        try:
            content = readme_path.read_text(encoding='utf-8')
            
            # Extract phase name from title
            phase_name_match = re.search(r'^#\s+(.+?)(?:\n|$)', content, re.MULTILINE)
            phase_name = phase_name_match.group(1).strip() if phase_name_match else f"Phase {phase_num}"
            
            # Extract input/output relationships
            input_from = []
            output_to = []
            
            # Look for "from Phase X" patterns
            from_matches = re.findall(r'[Ff]rom\s+Phase\s*(\d+)', content)
            input_from.extend([f"P{m.zfill(2)}" for m in from_matches])
            
            # Look for "to Phase X" patterns
            to_matches = re.findall(r'[Tt]o\s+Phase\s*(\d+)', content)
            output_to.extend([f"P{m.zfill(2)}" for m in to_matches])
            
            # Look for pipeline position
            position_match = re.search(r'Pipeline Position[:\s]+(.+?)(?:\n|\|)', content, re.IGNORECASE)
            position = position_match.group(1).strip() if position_match else ""
            
            # Extract from position patterns like "Phase 3 → Phase 4 → Phase 5"
            if position:
                phase_refs = re.findall(r'Phase\s*(\d+)', position)
                phase_nums = [f"P{p.zfill(2)}" for p in phase_refs]
                
                # Find where current phase is
                if phase_id in phase_nums:
                    idx = phase_nums.index(phase_id)
                    if idx > 0 and phase_nums[idx-1] not in input_from:
                        input_from.append(phase_nums[idx-1])
                    if idx < len(phase_nums) - 1 and phase_nums[idx+1] not in output_to:
                        output_to.append(phase_nums[idx+1])
            
            # Extract constitutional invariants
            invariants = []
            invariant_patterns = [
                r'(\d+)\s+chunks?',
                r'(\d+)\s+contracts?',
                r'(\d+)\s+scores?',
                r'(\d+)\s+policy\s+areas?',
                r'(\d+)\s+dimensions?',
                r'(\d+)\s+clusters?',
            ]
            for pattern in invariant_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match and int(match) in [4, 6, 10, 30, 60, 300]:
                        invariants.append(f"{match} items")
            
            # Extract key outputs
            outputs = []
            output_patterns = [
                r'Output[:\s]+(.+?)(?:\n|\|)',
                r'Produces[:\s]+(.+?)(?:\n|\|)',
            ]
            for pattern in output_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    outputs.append(match.group(1).strip())
            
            # Get excerpt
            excerpt = content[:500] if len(content) > 500 else content
            
            metadata = PhaseMetadata(
                phase_id=phase_id,
                phase_name=phase_name,
                readme_path=readme_path,
                input_from=list(set(input_from)),
                output_to=list(set(output_to)),
                constitutional_invariants=list(set(invariants)),
                position_in_pipeline=position,
                key_outputs=outputs,
                readme_excerpt=excerpt
            )
            
            return metadata
            
        except Exception as e:
            print(f"✗ {phase_id}: Error reading README: {e}")
            return None
    
    def audit_phase_topology(self, phase_id: str) -> TopologicalAuditResult:
        """Audit a single phase's topological position."""
        result = TopologicalAuditResult(phase_id=phase_id)
        
        metadata = self.phase_metadata.get(phase_id)
        if not metadata:
            result.issues.append("README not found or could not be parsed")
            return result
        
        result.readme_found = True
        result.upstream_phases = metadata.input_from
        result.downstream_phases = metadata.output_to
        result.dependencies_extracted = len(metadata.input_from) > 0 or phase_id == "P00"
        
        # Verify topological order
        phase_idx = self.canonical_order.index(phase_id)
        
        # Check upstream phases come before
        for upstream in metadata.input_from:
            if upstream in self.canonical_order:
                upstream_idx = self.canonical_order.index(upstream)
                if upstream_idx >= phase_idx:
                    result.issues.append(
                        f"Upstream phase {upstream} comes after {phase_id} in canonical order"
                    )
        
        # Check downstream phases come after
        for downstream in metadata.output_to:
            if downstream in self.canonical_order:
                downstream_idx = self.canonical_order.index(downstream)
                if downstream_idx <= phase_idx:
                    result.issues.append(
                        f"Downstream phase {downstream} comes before {phase_id} in canonical order"
                    )
        
        # Check expected dependencies
        if phase_idx > 0:
            expected_upstream = self.canonical_order[phase_idx - 1]
            if expected_upstream not in metadata.input_from:
                # This is a warning, not critical
                result.issues.append(
                    f"Expected upstream phase {expected_upstream} not explicitly documented in README"
                )
        
        result.topological_order_correct = len([i for i in result.issues if "comes after" in i or "comes before" in i]) == 0
        
        return result
    
    def verify_no_cycles(self) -> List[List[str]]:
        """Verify no circular dependencies exist."""
        print("\n" + "=" * 80)
        print("CIRCULAR DEPENDENCY CHECK")
        print("=" * 80)
        
        # Build adjacency list
        graph: Dict[str, List[str]] = {}
        for phase_id, metadata in self.phase_metadata.items():
            graph[phase_id] = metadata.output_to
        
        # DFS to detect cycles
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []
        path: List[str] = []
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for node in graph.keys():
            if node not in visited:
                dfs(node)
        
        if cycles:
            print(f"✗ CIRCULAR DEPENDENCIES DETECTED: {len(cycles)} cycle(s)")
            for i, cycle in enumerate(cycles, 1):
                print(f"  Cycle {i}: {' → '.join(cycle)}")
        else:
            print("✓ No circular dependencies detected")
        
        return cycles
    
    def print_summary(self):
        """Print audit summary."""
        print("\n" + "=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)
        
        total = len(self.canonical_order)
        readmes_found = sum(1 for r in self.audit_results.values() if r.readme_found)
        deps_extracted = sum(1 for r in self.audit_results.values() if r.dependencies_extracted)
        topo_correct = sum(1 for r in self.audit_results.values() if r.topological_order_correct)
        
        print(f"Phases with README: {readmes_found}/{total}")
        print(f"Phases with dependencies extracted: {deps_extracted}/{total}")
        print(f"Phases with correct topological order: {topo_correct}/{total}")
        print()
        
        # Print phase flow
        print("CANONICAL PHASE FLOW:")
        print("-" * 80)
        for i, phase_id in enumerate(self.canonical_order):
            metadata = self.phase_metadata.get(phase_id)
            result = self.audit_results.get(phase_id)
            
            if metadata:
                status = "✓" if result and result.topological_order_correct else "✗"
                upstream = ", ".join(metadata.input_from) if metadata.input_from else "None"
                downstream = ", ".join(metadata.output_to) if metadata.output_to else "None"
                
                print(f"{status} {phase_id}: {metadata.phase_name}")
                print(f"    Upstream: {upstream}")
                print(f"    Downstream: {downstream}")
                if result and result.issues:
                    for issue in result.issues:
                        print(f"    ⚠ {issue}")
                print()
        
        # Overall status
        if topo_correct == total:
            print("✓ AUDIT PASSED: All phases have correct topological order")
            return 0
        else:
            print("✗ AUDIT FAILED: Some phases have topological issues")
            return 1
    
    def generate_report(self, output_path: Path):
        """Generate JSON report."""
        report = {
            "audit_type": "phase_topological_order",
            "phases_directory": str(self.phases_dir),
            "canonical_order": self.canonical_order,
            "total_phases": len(self.canonical_order),
            "phases_audited": len(self.audit_results),
            "phase_results": {
                phase_id: result.to_dict()
                for phase_id, result in self.audit_results.items()
            },
            "phase_metadata": {
                phase_id: {
                    "phase_name": meta.phase_name,
                    "position": meta.position_in_pipeline,
                    "input_from": meta.input_from,
                    "output_to": meta.output_to,
                    "constitutional_invariants": meta.constitutional_invariants,
                }
                for phase_id, meta in self.phase_metadata.items()
            },
            "summary": {
                "readmes_found": sum(1 for r in self.audit_results.values() if r.readme_found),
                "dependencies_extracted": sum(1 for r in self.audit_results.values() if r.dependencies_extracted),
                "topological_order_correct": sum(1 for r in self.audit_results.values() if r.topological_order_correct),
            }
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✓ Report saved to: {output_path}")


def main() -> int:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Audit phase topological order by reading READMEs"
    )
    parser.add_argument(
        "--phases-dir",
        type=Path,
        default=REPO_ROOT / "src" / "farfan_pipeline" / "phases",
        help="Path to phases directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "artifacts" / "audit_reports" / "phase_topological_order_audit.json",
        help="Path to output report file",
    )
    
    args = parser.parse_args()
    
    if not args.phases_dir.exists():
        print(f"ERROR: Phases directory not found: {args.phases_dir}", file=sys.stderr)
        return 1
    
    # Run audit
    auditor = PhaseTopologicalAuditor(args.phases_dir)
    auditor.audit_all_phases()
    
    # Generate report
    auditor.generate_report(args.output)
    
    # Print summary
    return auditor.print_summary()


if __name__ == "__main__":
    sys.exit(main())
