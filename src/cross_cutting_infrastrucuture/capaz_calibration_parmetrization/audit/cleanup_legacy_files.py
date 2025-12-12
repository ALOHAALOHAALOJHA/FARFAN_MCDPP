"""
Cleanup script for legacy files from previous refactoring waves.

Purpose:
- Remove all non-COHORT_2024 configuration files
- Delete legacy artifacts from evidence traces
- Ensure only COHORT_2024 labeled files remain
- Prevent confusion from duplicate or contradictory configurations

Authority: COHORT_2024 Legacy Cleanup Protocol
Warning: This script performs irreversible deletions. Review carefully before execution.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Set


class LegacyFileCleanup:
    PARENT_FOLDER = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization"
    COHORT_PREFIX = "COHORT_2024"
    
    # Files explicitly marked for deletion
    LEGACY_FILES_TO_DELETE = [
        "calibration/fusion_weights.json",  # Superseded by COHORT_2024_fusion_weights.json
    ]
    
    # Directories to clean (remove all unlabeled files)
    DIRECTORIES_TO_AUDIT = [
        "calibration",
        "parametrization",
    ]
    
    # Files to preserve (utility scripts, not configuration)
    PRESERVE_FILES = {
        "__init__.py",
        "certificate_generator.py",
        "certificate_validator.py",
        "validate_fusion_weights.py",
        "weight_validation_report.json",
        "chain_layer_tests.py",
        "CHAIN_LAYER_QUICK_REFERENCE.md",
        "CHAIN_LAYER_SPECIFICATION.md",
    }
    
    def __init__(self, repo_root: str = ".", dry_run: bool = True):
        self.repo_root = Path(repo_root)
        self.parent_path = self.repo_root / self.PARENT_FOLDER
        self.dry_run = dry_run
        self.deleted_files: List[str] = []
        self.preserved_files: List[str] = []
        
    def cleanup(self) -> Dict[str, List[str]]:
        """Execute legacy file cleanup."""
        print("=" * 80)
        print("COHORT_2024 LEGACY FILE CLEANUP")
        print("=" * 80)
        print(f"Mode: {'DRY RUN (no files deleted)' if self.dry_run else 'LIVE EXECUTION'}")
        print()
        
        # Delete explicitly marked legacy files
        self._delete_explicit_legacy_files()
        
        # Scan and clean directories
        for directory in self.DIRECTORIES_TO_AUDIT:
            self._clean_directory(directory)
        
        # Generate report
        return self._generate_report()
    
    def _delete_explicit_legacy_files(self) -> None:
        """Delete files explicitly marked as legacy."""
        print("Deleting explicitly marked legacy files...")
        
        for legacy_file in self.LEGACY_FILES_TO_DELETE:
            file_path = self.parent_path / legacy_file
            
            if file_path.exists():
                if self.dry_run:
                    print(f"  [DRY RUN] Would delete: {file_path}")
                else:
                    file_path.unlink()
                    print(f"  ✓ Deleted: {file_path}")
                
                self.deleted_files.append(str(legacy_file))
            else:
                print(f"  ⊘ Not found (already deleted?): {file_path}")
        
        print()
    
    def _clean_directory(self, directory: str) -> None:
        """Clean a directory of unlabeled files."""
        print(f"Cleaning directory: {directory}/")
        
        dir_path = self.parent_path / directory
        
        if not dir_path.exists():
            print(f"  ⚠ Directory not found: {dir_path}")
            print()
            return
        
        for root, dirs, filenames in os.walk(dir_path):
            root_path = Path(root)
            
            # Skip subdirectories (evidence_traces, validation_reports, examples, etc.)
            if root_path != dir_path:
                continue
            
            for filename in filenames:
                file_path = root_path / filename
                relative_path = file_path.relative_to(self.parent_path)
                
                # Skip files to preserve
                if filename in self.PRESERVE_FILES:
                    print(f"  ✓ Preserved: {relative_path}")
                    self.preserved_files.append(str(relative_path))
                    continue
                
                # Delete files without COHORT_2024 prefix
                if not filename.startswith(self.COHORT_PREFIX):
                    if filename.endswith((".json", ".py")):
                        if self.dry_run:
                            print(f"  [DRY RUN] Would delete: {relative_path}")
                        else:
                            file_path.unlink()
                            print(f"  ✗ Deleted: {relative_path}")
                        
                        self.deleted_files.append(str(relative_path))
                else:
                    print(f"  ✓ Retained (COHORT_2024): {relative_path}")
                    self.preserved_files.append(str(relative_path))
        
        print()
    
    def _generate_report(self) -> Dict[str, List[str]]:
        """Generate cleanup report."""
        print("=" * 80)
        print("CLEANUP REPORT")
        print("=" * 80)
        print()
        
        print(f"Files deleted: {len(self.deleted_files)}")
        if self.deleted_files:
            for deleted in self.deleted_files:
                print(f"  - {deleted}")
        print()
        
        print(f"Files preserved: {len(self.preserved_files)}")
        if self.preserved_files:
            for preserved in self.preserved_files:
                print(f"  + {preserved}")
        print()
        
        if self.dry_run:
            print("⚠ DRY RUN MODE: No files were actually deleted")
            print("  Run with --execute flag to perform actual deletions")
        else:
            print("✓ CLEANUP COMPLETE: Legacy files have been removed")
        
        print()
        
        return {
            "deleted": self.deleted_files,
            "preserved": self.preserved_files,
        }
    
    def save_report(self, output_path: str) -> None:
        """Save cleanup report to JSON."""
        report_data = {
            "cleanup_metadata": {
                "cohort_id": self.COHORT_PREFIX,
                "cleanup_date": "2024-12-15T00:00:00+00:00",
                "dry_run": self.dry_run,
            },
            "summary": {
                "files_deleted": len(self.deleted_files),
                "files_preserved": len(self.preserved_files),
            },
            "deleted_files": self.deleted_files,
            "preserved_files": self.preserved_files,
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"✓ Cleanup report saved to: {output_path}")


def main():
    """Execute legacy file cleanup."""
    import sys
    
    # Check for --execute flag
    execute = "--execute" in sys.argv
    dry_run = not execute
    
    if dry_run:
        print("⚠ Running in DRY RUN mode (no files will be deleted)")
        print("  Use --execute flag to perform actual deletions")
        print()
    else:
        print("⚠ LIVE EXECUTION MODE: Files will be permanently deleted")
        print("  Press Ctrl+C within 3 seconds to cancel...")
        print()
        
        import time
        try:
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n✗ Cleanup cancelled by user")
            sys.exit(0)
    
    cleaner = LegacyFileCleanup(dry_run=dry_run)
    cleaner.cleanup()
    
    # Save report
    report_path = os.path.join(
        cleaner.parent_path,
        "validation_reports",
        "legacy_cleanup_report.json"
    )
    cleaner.save_report(report_path)


if __name__ == "__main__":
    main()
