"""
Master orchestration script for comprehensive COHORT_2024 structural audit.

This script coordinates:
1. Structural audit - verify organization and detect issues
2. File reorganization - create missing files and fix structure
3. Legacy cleanup - delete old files from previous waves
4. Final verification - confirm all requirements met

Purpose:
- Complete end-to-end structural validation
- Ensure COHORT_2024 governance compliance
- Eliminate ambiguity from parallel/duplicate files
- Generate comprehensive audit trail

Authority: COHORT_2024 Master Governance Protocol
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from structural_audit import StructuralAuditor
from reorganize_files import FileReorganizer
from cleanup_legacy_files import LegacyFileCleanup


class MasterAuditOrchestrator:
    PARENT_FOLDER = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization"
    COHORT_PREFIX = "COHORT_2024"
    
    def __init__(self, repo_root: str = ".", execute: bool = False):
        self.repo_root = Path(repo_root)
        self.parent_path = self.repo_root / self.PARENT_FOLDER
        self.execute = execute
        self.dry_run = not execute
        
        self.audit_results: Dict = {}
        self.reorganize_results: Dict = {}
        self.cleanup_results: Dict = {}
        self.final_verification: Dict = {}
        
    def execute_master_audit(self) -> bool:
        """Execute complete audit and remediation workflow."""
        print("=" * 80)
        print("COHORT_2024 MASTER STRUCTURAL AUDIT")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Mode: {'LIVE EXECUTION' if self.execute else 'DRY RUN'}")
        print()
        
        success = True
        
        # Phase 1: Initial structural audit
        print("\n" + "=" * 80)
        print("PHASE 1: INITIAL STRUCTURAL AUDIT")
        print("=" * 80 + "\n")
        
        success = success and self._phase1_initial_audit()
        
        # Phase 2: File reorganization
        print("\n" + "=" * 80)
        print("PHASE 2: FILE REORGANIZATION")
        print("=" * 80 + "\n")
        
        success = success and self._phase2_reorganization()
        
        # Phase 3: Legacy cleanup
        print("\n" + "=" * 80)
        print("PHASE 3: LEGACY FILE CLEANUP")
        print("=" * 80 + "\n")
        
        success = success and self._phase3_cleanup()
        
        # Phase 4: Final verification
        print("\n" + "=" * 80)
        print("PHASE 4: FINAL VERIFICATION")
        print("=" * 80 + "\n")
        
        success = success and self._phase4_verification()
        
        # Generate master report
        self._generate_master_report()
        
        return success
    
    def _phase1_initial_audit(self) -> bool:
        """Phase 1: Initial structural audit to identify issues."""
        print("Executing initial structural audit...")
        print()
        
        auditor = StructuralAuditor(repo_root=str(self.repo_root))
        report = auditor.audit()
        
        self.audit_results = {
            "total_files": report.total_files,
            "cohort_2024_files": report.cohort_2024_files,
            "legacy_files": report.legacy_files,
            "misplaced_files": report.misplaced_files,
            "unlabeled_files": report.unlabeled_files,
            "duplicate_files": report.duplicate_files,
            "issues": report.issues,
            "recommendations": report.recommendations,
        }
        
        # Print summary
        print(f"Total files scanned: {report.total_files}")
        print(f"COHORT_2024 files: {report.cohort_2024_files}")
        print(f"Legacy files: {report.legacy_files}")
        print(f"Issues found: {len(report.issues)}")
        print()
        
        if report.issues:
            print("Issues detected - proceeding to remediation phases")
            return True
        else:
            print("✓ No issues detected - structure is compliant")
            return True
    
    def _phase2_reorganization(self) -> bool:
        """Phase 2: Reorganize files and create missing configurations."""
        print("Executing file reorganization...")
        print()
        
        reorganizer = FileReorganizer(repo_root=str(self.repo_root), dry_run=self.dry_run)
        results = reorganizer.reorganize()
        
        self.reorganize_results = results
        
        print(f"Actions performed: {len(results.get('actions', []))}")
        print()
        
        return True
    
    def _phase3_cleanup(self) -> bool:
        """Phase 3: Clean up legacy files from previous waves."""
        print("Executing legacy file cleanup...")
        print()
        
        cleaner = LegacyFileCleanup(repo_root=str(self.repo_root), dry_run=self.dry_run)
        results = cleaner.cleanup()
        
        self.cleanup_results = results
        
        print(f"Files deleted: {len(results.get('deleted', []))}")
        print(f"Files preserved: {len(results.get('preserved', []))}")
        print()
        
        return True
    
    def _phase4_verification(self) -> bool:
        """Phase 4: Final verification after remediation."""
        print("Executing final verification audit...")
        print()
        
        auditor = StructuralAuditor(repo_root=str(self.repo_root))
        report = auditor.audit()
        
        self.final_verification = {
            "total_files": report.total_files,
            "cohort_2024_files": report.cohort_2024_files,
            "legacy_files": report.legacy_files,
            "issues": report.issues,
            "compliant": len(report.issues) == 0,
        }
        
        if report.issues:
            print("⚠ Remaining issues after remediation:")
            for issue in report.issues:
                print(f"  • {issue}")
            print()
            return False
        else:
            print("✓ VERIFICATION PASSED: All structural requirements met")
            print(f"  • Total COHORT_2024 files: {report.cohort_2024_files}")
            print(f"  • Legacy files remaining: {report.legacy_files}")
            print()
            return True
    
    def _generate_master_report(self) -> None:
        """Generate comprehensive master audit report."""
        print("=" * 80)
        print("MASTER AUDIT REPORT")
        print("=" * 80)
        print()
        
        master_report = {
            "metadata": {
                "cohort_id": self.COHORT_PREFIX,
                "audit_timestamp": datetime.now().isoformat(),
                "execution_mode": "live" if self.execute else "dry_run",
            },
            "phase1_initial_audit": self.audit_results,
            "phase2_reorganization": self.reorganize_results,
            "phase3_cleanup": self.cleanup_results,
            "phase4_verification": self.final_verification,
            "summary": {
                "initial_issues": len(self.audit_results.get("issues", [])),
                "final_issues": len(self.final_verification.get("issues", [])),
                "compliant": self.final_verification.get("compliant", False),
                "files_cleaned": len(self.cleanup_results.get("deleted", [])),
                "actions_taken": len(self.reorganize_results.get("actions", [])),
            },
        }
        
        # Save master report
        report_path = self.parent_path / "validation_reports" / "master_audit_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w") as f:
            json.dump(master_report, f, indent=2)
        
        print(f"✓ Master audit report saved: {report_path}")
        print()
        
        # Print summary
        print("AUDIT SUMMARY:")
        print(f"  Initial issues detected: {master_report['summary']['initial_issues']}")
        print(f"  Final issues remaining: {master_report['summary']['final_issues']}")
        print(f"  Files cleaned up: {master_report['summary']['files_cleaned']}")
        print(f"  Actions performed: {master_report['summary']['actions_taken']}")
        print(f"  Compliance status: {'✓ COMPLIANT' if master_report['summary']['compliant'] else '✗ NON-COMPLIANT'}")
        print()
        
        if self.dry_run:
            print("⚠ DRY RUN MODE: No actual changes were made")
            print("  Run with --execute flag to perform live execution")
        else:
            print("✓ LIVE EXECUTION: All changes have been applied")
        
        print()
        print("=" * 80)


def main():
    """Execute master audit workflow."""
    execute = "--execute" in sys.argv or "--live" in sys.argv
    
    print()
    if not execute:
        print("⚠ DRY RUN MODE")
        print("  No files will be modified or deleted")
        print("  Use --execute flag for live execution")
    else:
        print("⚠⚠⚠ LIVE EXECUTION MODE ⚠⚠⚠")
        print("  Files WILL be modified and deleted")
        print("  Press Ctrl+C within 5 seconds to cancel...")
        
        import time
        try:
            for i in range(5, 0, -1):
                print(f"  {i}...")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n✗ Audit cancelled by user")
            sys.exit(0)
        
        print("  → Proceeding with live execution")
    
    print()
    
    orchestrator = MasterAuditOrchestrator(execute=execute)
    success = orchestrator.execute_master_audit()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
