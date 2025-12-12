"""
Comprehensive structural audit for COHORT_2024 calibration and parametrization files.

Purpose:
- Verify all configuration files are properly organized under designated parent folder
- Confirm all files reside in correct subfolders (calibration/ vs parametrization/)
- Validate COHORT_2024 prefix labels serve as tracers
- Identify legacy files from previous waves for total deletion
- Check for unlabeled duplicates or misplaced artifacts
- Prevent confusion or ambiguity from parallel, duplicate, or contradictory files

Authority: COHORT_2024 Structural Governance
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class FileAuditEntry:
    path: str
    filename: str
    has_cohort_prefix: bool
    is_cohort_2024: bool
    category: str
    is_legacy: bool
    is_duplicate: bool
    issues: List[str]


@dataclass
class AuditReport:
    total_files: int
    cohort_2024_files: int
    legacy_files: int
    misplaced_files: int
    unlabeled_files: int
    duplicate_files: int
    all_files: List[FileAuditEntry]
    issues: List[str]
    recommendations: List[str]


class StructuralAuditor:
    PARENT_FOLDER = "src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization"
    CALIBRATION_SUBFOLDER = "calibration"
    PARAMETRIZATION_SUBFOLDER = "parametrization"
    
    REQUIRED_CONFIG_FILES = {
        "intrinsic_calibration.json": "calibration",
        "fusion_weights.json": "calibration",
        "method_compatibility.json": "calibration",
        "layer_requirements.json": "calibration",
        "executor_config.json": "parametrization",
    }
    
    COHORT_PREFIX = "COHORT_2024"
    
    LEGACY_PATTERNS = [
        "calibration_trace_example.json",
        "farfan_pipeline.core.calibration",
        "farfan_pipeline.analysis",
    ]
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.parent_path = self.repo_root / self.PARENT_FOLDER
        self.calibration_path = self.parent_path / self.CALIBRATION_SUBFOLDER
        self.parametrization_path = self.parent_path / self.PARAMETRIZATION_SUBFOLDER
        
    def audit(self) -> AuditReport:
        """Execute comprehensive structural audit."""
        all_files: List[FileAuditEntry] = []
        issues: List[str] = []
        
        # Verify parent folder structure exists
        if not self.parent_path.exists():
            issues.append(f"CRITICAL: Parent folder does not exist: {self.parent_path}")
            return self._empty_report(issues)
        
        if not self.calibration_path.exists():
            issues.append(f"CRITICAL: Calibration subfolder does not exist: {self.calibration_path}")
        
        if not self.parametrization_path.exists():
            issues.append(f"CRITICAL: Parametrization subfolder does not exist: {self.parametrization_path}")
        
        # Scan calibration folder
        calibration_files = self._scan_folder(self.calibration_path, "calibration")
        all_files.extend(calibration_files)
        
        # Scan parametrization folder
        parametrization_files = self._scan_folder(self.parametrization_path, "parametrization")
        all_files.extend(parametrization_files)
        
        # Check for required configuration files
        required_check = self._check_required_files(all_files)
        issues.extend(required_check)
        
        # Detect duplicates
        duplicates = self._detect_duplicates(all_files)
        for dup in duplicates:
            issues.append(f"DUPLICATE: Multiple versions of {dup} found")
        
        # Detect misplaced files
        misplaced = self._detect_misplaced_files(all_files)
        issues.extend(misplaced)
        
        # Detect legacy files
        legacy = [f for f in all_files if f.is_legacy]
        if legacy:
            issues.append(f"LEGACY FILES DETECTED: {len(legacy)} legacy files require deletion")
        
        # Detect unlabeled files
        unlabeled = [f for f in all_files if not f.has_cohort_prefix and not f.is_legacy]
        if unlabeled:
            issues.append(f"UNLABELED FILES: {len(unlabeled)} files missing COHORT_2024 prefix")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_files, issues)
        
        return AuditReport(
            total_files=len(all_files),
            cohort_2024_files=len([f for f in all_files if f.is_cohort_2024]),
            legacy_files=len(legacy),
            misplaced_files=len([f for f in all_files if "MISPLACED" in str(f.issues)]),
            unlabeled_files=len(unlabeled),
            duplicate_files=len(duplicates),
            all_files=all_files,
            issues=issues,
            recommendations=recommendations,
        )
    
    def _scan_folder(self, folder_path: Path, category: str) -> List[FileAuditEntry]:
        """Scan folder for all JSON and Python files."""
        files = []
        
        if not folder_path.exists():
            return files
        
        for root, dirs, filenames in os.walk(folder_path):
            root_path = Path(root)
            
            # Skip certain directories
            if any(skip in root for skip in ["__pycache__", ".git", "evidence_traces", "validation_reports", "certificate_examples", "chain_examples"]):
                continue
            
            for filename in filenames:
                if filename.endswith((".json", ".py")) and not filename.startswith("__"):
                    file_path = root_path / filename
                    relative_path = file_path.relative_to(self.parent_path)
                    
                    entry = self._analyze_file(str(relative_path), filename, category)
                    files.append(entry)
        
        return files
    
    def _analyze_file(self, path: str, filename: str, expected_category: str) -> FileAuditEntry:
        """Analyze individual file for compliance."""
        has_cohort_prefix = self.COHORT_PREFIX in filename
        is_cohort_2024 = filename.startswith(self.COHORT_PREFIX)
        
        # Determine actual category from path
        if self.CALIBRATION_SUBFOLDER in path:
            actual_category = "calibration"
        elif self.PARAMETRIZATION_SUBFOLDER in path:
            actual_category = "parametrization"
        else:
            actual_category = "unknown"
        
        # Check if legacy
        is_legacy = self._is_legacy_file(filename, path)
        
        # Check for duplicates (handled separately)
        is_duplicate = False
        
        issues = []
        
        # Category mismatch
        if actual_category != expected_category and actual_category != "unknown":
            issues.append(f"MISPLACED: Expected in {expected_category}/ but found in {actual_category}/")
        
        # Missing COHORT prefix for non-legacy files
        if not has_cohort_prefix and not is_legacy and actual_category in ["calibration", "parametrization"]:
            if filename not in ["__init__.py", "certificate_generator.py", "certificate_validator.py", 
                               "validate_fusion_weights.py", "weight_validation_report.json",
                               "chain_layer_tests.py"]:
                issues.append("UNLABELED: Missing COHORT_2024 prefix")
        
        # Legacy file that should be deleted
        if is_legacy:
            issues.append("LEGACY: Marked for deletion")
        
        return FileAuditEntry(
            path=path,
            filename=filename,
            has_cohort_prefix=has_cohort_prefix,
            is_cohort_2024=is_cohort_2024,
            category=actual_category,
            is_legacy=is_legacy,
            is_duplicate=is_duplicate,
            issues=issues,
        )
    
    def _is_legacy_file(self, filename: str, path: str) -> bool:
        """Determine if file is a legacy artifact from previous waves."""
        # Check against known legacy patterns
        for pattern in self.LEGACY_PATTERNS:
            if pattern in filename or pattern in path:
                return True
        
        # Files without COHORT_2024 prefix that match config file patterns
        if not self.COHORT_PREFIX in filename:
            for config_name in self.REQUIRED_CONFIG_FILES.keys():
                base_name = config_name.replace(".json", "")
                if base_name in filename and filename != config_name:
                    # Exact matches to legacy patterns
                    if filename in ["fusion_weights.json"] and self.CALIBRATION_SUBFOLDER in path:
                        return True
        
        return False
    
    def _check_required_files(self, all_files: List[FileAuditEntry]) -> List[str]:
        """Check that all required configuration files exist with COHORT_2024 prefix."""
        issues = []
        
        for required_file, expected_category in self.REQUIRED_CONFIG_FILES.items():
            base_name = required_file.replace(".json", "")
            cohort_filename = f"{self.COHORT_PREFIX}_{required_file}"
            
            # Find matching files
            matches = [
                f for f in all_files 
                if f.filename == cohort_filename and f.category == expected_category
            ]
            
            if not matches:
                issues.append(
                    f"MISSING: Required file {cohort_filename} not found in {expected_category}/"
                )
            elif len(matches) > 1:
                issues.append(
                    f"DUPLICATE: Multiple instances of {cohort_filename} in {expected_category}/"
                )
        
        return issues
    
    def _detect_duplicates(self, all_files: List[FileAuditEntry]) -> Set[str]:
        """Detect duplicate files (same base name, different versions)."""
        duplicates = set()
        name_map: Dict[str, List[FileAuditEntry]] = {}
        
        for file_entry in all_files:
            # Normalize filename by removing COHORT prefix
            normalized = file_entry.filename.replace(f"{self.COHORT_PREFIX}_", "")
            
            if normalized not in name_map:
                name_map[normalized] = []
            name_map[normalized].append(file_entry)
        
        # Find duplicates
        for normalized, entries in name_map.items():
            if len(entries) > 1:
                # Mark as duplicate
                for entry in entries:
                    entry.is_duplicate = True
                duplicates.add(normalized)
        
        return duplicates
    
    def _detect_misplaced_files(self, all_files: List[FileAuditEntry]) -> List[str]:
        """Detect files in wrong subfolder."""
        issues = []
        
        for file_entry in all_files:
            if "MISPLACED" in str(file_entry.issues):
                issues.append(
                    f"MISPLACED: {file_entry.filename} in {file_entry.category}/ "
                    f"(issues: {', '.join(file_entry.issues)})"
                )
        
        return issues
    
    def _generate_recommendations(self, all_files: List[FileAuditEntry], issues: List[str]) -> List[str]:
        """Generate actionable recommendations based on audit findings."""
        recommendations = []
        
        # Legacy file deletion
        legacy_files = [f for f in all_files if f.is_legacy]
        if legacy_files:
            recommendations.append("DELETE LEGACY FILES:")
            for legacy in legacy_files:
                recommendations.append(f"  - rm {self.parent_path / legacy.path}")
        
        # Unlabeled file renaming
        unlabeled_files = [f for f in all_files if not f.has_cohort_prefix and not f.is_legacy]
        unlabeled_configs = [
            f for f in unlabeled_files 
            if any(req in f.filename for req in self.REQUIRED_CONFIG_FILES.keys())
        ]
        if unlabeled_configs:
            recommendations.append("RENAME UNLABELED CONFIG FILES:")
            for unlabeled in unlabeled_configs:
                old_path = self.parent_path / unlabeled.path
                new_filename = f"{self.COHORT_PREFIX}_{unlabeled.filename}"
                new_path = old_path.parent / new_filename
                recommendations.append(f"  - mv {old_path} {new_path}")
        
        # Misplaced file relocation
        misplaced = [f for f in all_files if "MISPLACED" in str(f.issues)]
        if misplaced:
            recommendations.append("RELOCATE MISPLACED FILES:")
            for mp in misplaced:
                recommendations.append(f"  - Review and relocate: {mp.path}")
        
        # Overall structure validation
        if not issues:
            recommendations.append("✓ STRUCTURE VALIDATED: All files properly organized")
        else:
            recommendations.append(f"✗ ISSUES FOUND: {len(issues)} structural issues require attention")
        
        return recommendations
    
    def _empty_report(self, issues: List[str]) -> AuditReport:
        """Generate empty report when critical errors prevent audit."""
        return AuditReport(
            total_files=0,
            cohort_2024_files=0,
            legacy_files=0,
            misplaced_files=0,
            unlabeled_files=0,
            duplicate_files=0,
            all_files=[],
            issues=issues,
            recommendations=["CRITICAL: Cannot proceed with audit due to missing directories"],
        )
    
    def generate_report_json(self, report: AuditReport, output_path: str) -> None:
        """Generate JSON audit report."""
        report_data = {
            "audit_metadata": {
                "cohort_id": self.COHORT_PREFIX,
                "audit_date": "2024-12-15T00:00:00+00:00",
                "auditor_version": "1.0.0",
            },
            "summary": {
                "total_files": report.total_files,
                "cohort_2024_files": report.cohort_2024_files,
                "legacy_files": report.legacy_files,
                "misplaced_files": report.misplaced_files,
                "unlabeled_files": report.unlabeled_files,
                "duplicate_files": report.duplicate_files,
            },
            "file_inventory": [
                {
                    "path": f.path,
                    "filename": f.filename,
                    "has_cohort_prefix": f.has_cohort_prefix,
                    "is_cohort_2024": f.is_cohort_2024,
                    "category": f.category,
                    "is_legacy": f.is_legacy,
                    "is_duplicate": f.is_duplicate,
                    "issues": f.issues,
                }
                for f in report.all_files
            ],
            "issues": report.issues,
            "recommendations": report.recommendations,
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"✓ Audit report saved to: {output_path}")
    
    def print_report(self, report: AuditReport) -> None:
        """Print human-readable audit report."""
        print("=" * 80)
        print("COHORT_2024 STRUCTURAL AUDIT REPORT")
        print("=" * 80)
        print()
        
        print("SUMMARY:")
        print(f"  Total Files: {report.total_files}")
        print(f"  COHORT_2024 Files: {report.cohort_2024_files}")
        print(f"  Legacy Files: {report.legacy_files}")
        print(f"  Misplaced Files: {report.misplaced_files}")
        print(f"  Unlabeled Files: {report.unlabeled_files}")
        print(f"  Duplicate Files: {report.duplicate_files}")
        print()
        
        if report.issues:
            print("ISSUES FOUND:")
            for issue in report.issues:
                print(f"  ⚠ {issue}")
            print()
        
        if report.recommendations:
            print("RECOMMENDATIONS:")
            for rec in report.recommendations:
                print(f"  {rec}")
            print()
        
        print("FILE INVENTORY:")
        for file_entry in sorted(report.all_files, key=lambda x: x.path):
            status = "✓" if not file_entry.issues else "✗"
            tags = []
            if file_entry.is_cohort_2024:
                tags.append("COHORT_2024")
            if file_entry.is_legacy:
                tags.append("LEGACY")
            if file_entry.is_duplicate:
                tags.append("DUPLICATE")
            
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            print(f"  {status} {file_entry.path}{tag_str}")
            
            if file_entry.issues:
                for issue in file_entry.issues:
                    print(f"      → {issue}")
        
        print()
        print("=" * 80)


def main():
    """Execute structural audit and generate reports."""
    auditor = StructuralAuditor()
    
    print("Executing COHORT_2024 structural audit...")
    print()
    
    report = auditor.audit()
    
    # Print human-readable report
    auditor.print_report(report)
    
    # Generate JSON report
    report_path = os.path.join(
        auditor.parent_path,
        "validation_reports",
        "structural_audit_report.json"
    )
    auditor.generate_report_json(report, report_path)
    
    # Exit with error code if issues found
    if report.issues:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
