#!/usr/bin/env python3
"""
Reconcile Phase Manifests with Actual DAG Files

This script audits each canonic phase directory and reconciles its manifest
with the actual Python files present in the directory. It generates a
comprehensive report showing:
- Files present in directory but not listed in manifest
- Files listed in manifest but not present in directory
- Statistics for each phase
- Overall DAG consistency status
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_canonical_phases(phases_dir: Path) -> List[Path]:
    """Get all canonical phase directories (Phase_XX format)."""
    canonical_phases = []
    for d in sorted(phases_dir.iterdir()):
        if d.is_dir() and d.name.startswith("Phase_") and d.name != "Phase_04" and d.name != "Phase_zero":
            # Exclude Phase_04 (duplicate of Phase_04) and Phase_zero (duplicate of Phase_00)
            canonical_phases.append(d)
    return canonical_phases


def extract_files_from_manifest(manifest_data: dict) -> Set[str]:
    """Extract Python file names from manifest structure."""
    files = set()
    
    # Try different manifest structures
    if "stages" in manifest_data:
        for stage in manifest_data.get("stages", []):
            for module in stage.get("modules", []):
                canonical_name = module.get("canonical_name", "")
                if canonical_name:
                    if canonical_name == "__init__":
                        files.add("__init__.py")
                    elif not canonical_name.startswith("__"):
                        files.add(f"{canonical_name}.py")
    
    return files


def get_actual_files(phase_dir: Path) -> Set[str]:
    """Get all Python files in a phase directory."""
    files = set()
    for f in phase_dir.glob("*.py"):
        files.add(f.name)
    return files


def find_manifest_file(phase_dir: Path) -> Tuple[Path, bool]:
    """Find the manifest file for a phase directory."""
    # First, search for any manifest file in the directory
    for manifest_file in phase_dir.glob("PHASE_*_MANIFEST.json"):
        return manifest_file, True
    
    # If not found, return the expected path
    phase_num = phase_dir.name.split('_')[1].lstrip('0') or '0'
    return phase_dir / f"PHASE_{phase_num}_MANIFEST.json", False


def audit_phase(phase_dir: Path) -> Dict:
    """Audit a single phase directory."""
    manifest_path, manifest_exists = find_manifest_file(phase_dir)
    actual_files = get_actual_files(phase_dir)
    manifest_files = set()
    
    if manifest_exists:
        try:
            with open(manifest_path) as f:
                manifest_data = json.load(f)
                manifest_files = extract_files_from_manifest(manifest_data)
        except Exception as e:
            print(f"{Colors.WARNING}Warning: Error reading manifest {manifest_path}: {e}{Colors.ENDC}")
    
    # Calculate differences
    in_dir_not_in_manifest = actual_files - manifest_files
    in_manifest_not_in_dir = manifest_files - actual_files
    in_both = actual_files & manifest_files
    
    return {
        "phase_name": phase_dir.name,
        "phase_number": phase_dir.name.split('_')[1],
        "manifest_path": str(manifest_path.relative_to(manifest_path.parent.parent.parent.parent)),
        "manifest_exists": manifest_exists,
        "actual_files_count": len(actual_files),
        "manifest_files_count": len(manifest_files),
        "in_both_count": len(in_both),
        "actual_files": sorted(actual_files),
        "manifest_files": sorted(manifest_files),
        "in_both": sorted(in_both),
        "in_dir_not_in_manifest": sorted(in_dir_not_in_manifest),
        "in_manifest_not_in_dir": sorted(in_manifest_not_in_dir),
        "is_consistent": len(in_dir_not_in_manifest) == 0 and len(in_manifest_not_in_dir) == 0 and manifest_exists
    }


def print_phase_report(audit_result: Dict):
    """Print a detailed report for a single phase."""
    phase_name = audit_result["phase_name"]
    is_consistent = audit_result["is_consistent"]
    
    # Header
    status_color = Colors.OKGREEN if is_consistent else Colors.FAIL
    status_text = "✓ CONSISTENT" if is_consistent else "✗ NEEDS RECONCILIATION"
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{status_color}{phase_name} - {status_text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    # Manifest status
    if audit_result["manifest_exists"]:
        print(f"{Colors.OKGREEN}✓ Manifest exists:{Colors.ENDC} {audit_result['manifest_path']}")
    else:
        print(f"{Colors.FAIL}✗ Manifest missing:{Colors.ENDC} {audit_result['manifest_path']}")
    
    # Statistics
    print(f"\n{Colors.BOLD}Statistics:{Colors.ENDC}")
    print(f"  Files in directory:     {audit_result['actual_files_count']}")
    print(f"  Files in manifest:      {audit_result['manifest_files_count']}")
    print(f"  Files in both:          {audit_result['in_both_count']}")
    print(f"  In dir, not in manifest: {len(audit_result['in_dir_not_in_manifest'])}")
    print(f"  In manifest, not in dir: {len(audit_result['in_manifest_not_in_dir'])}")
    
    # Discrepancies
    if audit_result['in_dir_not_in_manifest']:
        print(f"\n{Colors.WARNING}Files in directory but NOT in manifest:{Colors.ENDC}")
        for f in audit_result['in_dir_not_in_manifest']:
            print(f"  {Colors.WARNING}+ {f}{Colors.ENDC}")
    
    if audit_result['in_manifest_not_in_dir']:
        print(f"\n{Colors.FAIL}Files in manifest but NOT in directory:{Colors.ENDC}")
        for f in audit_result['in_manifest_not_in_dir']:
            print(f"  {Colors.FAIL}- {f}{Colors.ENDC}")


def print_summary(audit_results: List[Dict]):
    """Print overall summary."""
    total_phases = len(audit_results)
    consistent_phases = sum(1 for r in audit_results if r['is_consistent'])
    phases_with_manifest = sum(1 for r in audit_results if r['manifest_exists'])
    total_files = sum(r['actual_files_count'] for r in audit_results)
    total_manifest_files = sum(r['manifest_files_count'] for r in audit_results)
    
    print(f"\n\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}OVERALL SUMMARY{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Phase Status:{Colors.ENDC}")
    print(f"  Total canonical phases:    {total_phases}")
    print(f"  Phases with manifests:     {phases_with_manifest}")
    print(f"  Fully consistent phases:   {consistent_phases}")
    print(f"  Phases needing work:       {total_phases - consistent_phases}")
    
    print(f"\n{Colors.BOLD}File Statistics:{Colors.ENDC}")
    print(f"  Total files in DAG:        {total_files}")
    print(f"  Total files in manifests:  {total_manifest_files}")
    
    if consistent_phases == total_phases:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ ALL PHASES ARE CONSISTENT!{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ RECONCILIATION NEEDED FOR {total_phases - consistent_phases} PHASE(S){Colors.ENDC}")


def save_audit_report(audit_results: List[Dict], output_path: Path):
    """Save detailed audit report as JSON."""
    report = {
        "audit_timestamp": "2026-01-17",
        "repository": "FARFAN_MCDPP",
        "audit_type": "phase_manifest_reconciliation",
        "summary": {
            "total_phases": len(audit_results),
            "consistent_phases": sum(1 for r in audit_results if r['is_consistent']),
            "phases_with_manifest": sum(1 for r in audit_results if r['manifest_exists']),
            "total_files_in_dag": sum(r['actual_files_count'] for r in audit_results),
            "total_files_in_manifests": sum(r['manifest_files_count'] for r in audit_results)
        },
        "phases": audit_results
    }
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{Colors.OKGREEN}✓ Detailed audit report saved to: {output_path}{Colors.ENDC}")


def main():
    """Main execution function."""
    # Setup paths
    repo_root = Path(__file__).parent.parent.parent
    phases_dir = repo_root / "src" / "farfan_pipeline" / "phases"
    output_dir = repo_root / "artifacts" / "audits"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "phase_manifest_reconciliation_report.json"
    
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("═" * 80)
    print("PHASE MANIFEST RECONCILIATION AUDIT")
    print("═" * 80)
    print(f"{Colors.ENDC}")
    print(f"Repository:  {repo_root.name}")
    print(f"Phases dir:  {phases_dir.relative_to(repo_root)}")
    print(f"Output:      {output_path.relative_to(repo_root)}")
    
    # Get canonical phases
    canonical_phases = get_canonical_phases(phases_dir)
    print(f"\n{Colors.BOLD}Found {len(canonical_phases)} canonical phases{Colors.ENDC}")
    
    # Audit each phase
    audit_results = []
    for phase_dir in canonical_phases:
        audit_result = audit_phase(phase_dir)
        audit_results.append(audit_result)
        print_phase_report(audit_result)
    
    # Print summary
    print_summary(audit_results)
    
    # Save report
    save_audit_report(audit_results, output_path)
    
    # Exit with appropriate code
    all_consistent = all(r['is_consistent'] for r in audit_results)
    sys.exit(0 if all_consistent else 1)


if __name__ == "__main__":
    main()
