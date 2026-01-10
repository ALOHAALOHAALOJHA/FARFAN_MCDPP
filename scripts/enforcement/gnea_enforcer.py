#!/usr/bin/env python3
"""
GNEA Enforcer - Global Nomenclature Enforcement Architecture Engine

This module implements the core enforcement engine for validating compliance
with the F.A.R.F.A.N Global Nomenclature Policy.

Document: FPN-GNEA-001
Version: 2.0.0
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class EnforcementLevel(Enum):
    """GNEA enforcement levels as defined in FPN-GNEA-001."""

    L0_ADVISORY = "advisory"
    L1_GUIDED = "guided"
    L2_ENFORCED = "enforced"
    L3_SEALED = "sealed"
    L4_FORENSIC = "forensic"


class Severity(Enum):
    """Violation severity levels."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Violation:
    """Represents a GNEA policy violation."""

    filepath: Path
    rule: str
    severity: Severity
    message: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    fix_command: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ComplianceReport:
    """Compliance report for GNEA validation."""

    timestamp: str
    enforcement_level: str
    total_files: int
    compliant_files: int
    non_compliant_files: int
    violations: List[Violation] = field(default_factory=list)
    compliance_score: float = 0.0
    auto_fixable_count: int = 0
    manual_fix_required_count: int = 0

    def calculate_score(self) -> float:
        """Calculate compliance score percentage."""
        if self.total_files == 0:
            return 100.0
        self.compliance_score = (self.compliant_files / self.total_files) * 100
        return self.compliance_score


class GNEARules:
    """GNEA naming rules as defined in GLOBAL_NAMING_POLICY.md."""

    # Phase module pattern: phase{N}_{SS}_{OO}_{name}.py
    # N = Phase number (0-9)
    # SS = Stage (00, 10, 20, ..., 90)
    # OO = Order within stage (00, 01, 02, ...)
    # name = lowercase_with_underscores
    PHASE_MODULE_PATTERN = re.compile(
        r"^phase(?P<phase>[0-9])_"
        r"(?P<stage>\d{2})_"
        r"(?P<order>\d{2})_"
        r"(?P<name>[a-z][a-z0-9_]*)\.py$"
    )

    # Contract pattern: Q{NNN}_{policy_area}_executor_contract.json
    CONTRACT_PATTERN = re.compile(
        r"^Q(?P<number>\d{3})_" r"(?P<policy_area>[a-z][a-z0-9_]*)_executor_contract\.json$"
    )

    # Contract with version suffix (existing pattern)
    CONTRACT_VERSION_PATTERN = re.compile(
        r"^Q(?P<number>\d{3})_" r"(?P<policy_area>[A-Z0-9]+)_contract_v(?P<version>\d+)\.json$"
    )

    # Phase directory pattern: Phase_{N}
    PHASE_DIR_PATTERN = re.compile(r"^Phase_(?P<number>[0-9])$")

    # Forbidden directory names
    FORBIDDEN_DIRS = {
        "temp",
        "tmp",
        "backup",
        "old",
        "misc",
        "legacy",
        "deprecated",
        "archive",
        "staging",
        "dev",
        "test",
    }

    # Stage numbers for phase modules
    VALID_STAGES = {00, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99}

    # Maximum hierarchy depth
    MAX_HIERARCHY_DEPTH = 5


class GNEAEnforcer:
    """
    Global Nomenclature Enforcement Architecture Enforcer.

    Validates compliance with FPN-GNEA-001 naming and organization policies.
    """

    def __init__(
        self,
        level: EnforcementLevel = EnforcementLevel.L1_GUIDED,
        repo_root: Optional[Path] = None,
        verbose: bool = False,
    ):
        self.level = level
        self.repo_root = repo_root or Path.cwd()
        self.verbose = verbose
        self.violations: List[Violation] = []
        self.rules = GNEARules()
        self.files_validated: Set[Path] = set()
        self.excluded_paths = {
            ".git",
            ".venv",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
            "node_modules",
            ".tox",
            "dist",
            "build",
            "*.egg-info",
        }

    def validate_repository(self) -> ComplianceReport:
        """Main entry point for repository validation."""
        if self.verbose:
            print(f"[GNEA] Starting validation at {self.level.value} level")
            print(f"[GNEA] Repository root: {self.repo_root}")

        # Collect all files to validate
        files_to_validate = self._collect_files()

        # Validate files
        for filepath in files_to_validate:
            self._validate_file(filepath)

        # Validate directory structure
        self._validate_directory_structure()

        # Validate phase directory names
        self._validate_phase_directories()

        # Generate report
        return self._generate_report(files_to_validate)

    def _collect_files(self) -> List[Path]:
        """Collect all files that should be validated."""
        files = []
        phases_dir = self.repo_root / "src/farfan_pipeline/phases"

        if phases_dir.exists():
            for pattern in ["**/*.py", "**/*.json", "**/*.md"]:
                files.extend(phases_dir.rglob(pattern))

        return [f for f in files if not self._is_excluded(f)]

    def _is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded from validation."""
        parts = path.parts
        for excluded in self.excluded_paths:
            if excluded in parts:
                return True
        return False

    def _validate_file(self, filepath: Path) -> None:
        """Validate a single file against all applicable rules."""
        self.files_validated.add(filepath)

        # Phase module validation
        if self._is_phase_module(filepath):
            self._validate_phase_module(filepath)

        # Contract validation
        if self._is_contract(filepath):
            self._validate_contract(filepath)

        # Documentation validation
        if filepath.suffix == ".md":
            self._validate_documentation(filepath)

        # Hierarchy depth validation
        self._validate_hierarchy_depth(filepath)

        # Python metadata validation
        if filepath.suffix == ".py":
            self._validate_python_metadata(filepath)

    def _is_phase_module(self, filepath: Path) -> bool:
        """Check if file is a phase module."""
        # Check if it's in a phase directory
        parts = filepath.parts
        if "phases" not in parts:
            return False
        return filepath.suffix == ".py" and filepath.name.startswith("phase")

    def _is_contract(self, filepath: Path) -> bool:
        """Check if file is a contract file."""
        return filepath.name.startswith("Q") and filepath.suffix == ".json"

    def _validate_phase_module(self, filepath: Path) -> None:
        """Validate phase module naming and structure."""
        filename = filepath.name

        # Check if filename matches pattern
        match = self.rules.PHASE_MODULE_PATTERN.match(filename)
        if not match:
            self.violations.append(
                Violation(
                    filepath=filepath,
                    rule="PHASE-001",
                    severity=Severity.ERROR,
                    message=f"Invalid phase module name: {filename}",
                    suggestion=self._suggest_phase_name(filepath),
                    auto_fixable=True,
                )
            )
            return

        # Validate internal consistency
        parts = match.groupdict()
        self._validate_phase_consistency(filepath, parts)

    def _validate_phase_consistency(self, filepath: Path, parts: Dict[str, str]) -> None:
        """Ensure phase module internals match filename."""
        try:
            content = filepath.read_text()
            tree = ast.parse(content)

            # Extract metadata from AST
            metadata = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id.startswith("__") and target.id.endswith("__"):
                                try:
                                    if isinstance(node.value, ast.Constant):
                                        metadata[target.id] = node.value.value
                                except (AttributeError, TypeError):
                                    pass

            # Check phase metadata
            expected_phase = parts["phase"]
            actual_phase = metadata.get("__phase__")
            if actual_phase is not None and str(actual_phase) != expected_phase:
                self.violations.append(
                    Violation(
                        filepath=filepath,
                        rule="PHASE-002",
                        severity=Severity.ERROR,
                        message=f"Phase metadata mismatch: expected __phase__ = {expected_phase}, got {actual_phase}",
                        auto_fixable=True,
                    )
                )

            # Check stage metadata
            expected_stage = int(parts["stage"])
            actual_stage = metadata.get("__stage__")
            if actual_stage is not None and int(actual_stage) != expected_stage:
                self.violations.append(
                    Violation(
                        filepath=filepath,
                        rule="PHASE-003",
                        severity=Severity.ERROR,
                        message=f"Stage metadata mismatch: expected __stage__ = {expected_stage}, got {actual_stage}",
                        auto_fixable=True,
                    )
                )

        except (SyntaxError, UnicodeDecodeError) as e:
            self.violations.append(
                Violation(
                    filepath=filepath,
                    rule="PHASE-004",
                    severity=Severity.WARNING,
                    message=f"Could not parse file: {e}",
                    auto_fixable=False,
                )
            )

    def _validate_contract(self, filepath: Path) -> None:
        """Validate contract file naming."""
        filename = filepath.name

        # Check both patterns (allow version suffix for compatibility)
        match_v1 = self.rules.CONTRACT_PATTERN.match(filename)
        match_v2 = self.rules.CONTRACT_VERSION_PATTERN.match(filename)

        if not match_v1 and not match_v2:
            self.violations.append(
                Violation(
                    filepath=filepath,
                    rule="CONTRACT-001",
                    severity=Severity.WARNING,
                    message=f"Contract name doesn't match standard pattern: {filename}",
                    auto_fixable=False,
                )
            )
            return

        # Validate contract sequential numbering
        if match_v1:
            number = int(match_v1.group("number"))
        else:
            number = int(match_v2.group("number"))

        if number < 1 or number > 300:
            self.violations.append(
                Violation(
                    filepath=filepath,
                    rule="CONTRACT-002",
                    severity=Severity.ERROR,
                    message=f"Contract number out of range (001-300): Q{number:03d}",
                    auto_fixable=False,
                )
            )

    def _validate_documentation(self, filepath: Path) -> None:
        """Validate documentation file naming."""
        filename = filepath.name

        # Documentation files should be UPPERCASE_WITH_UNDERSCORES.md
        # for formal docs, or lowercase-with-dashes.md for informal docs
        if filename.endswith(".md"):
            # Check if it's a formal documentation file
            if re.match(r"^[A-Z][A-Z0-9_]+\.md$", filename):
                return  # Valid formal doc
            if re.match(r"^[a-z][a-z0-9-]+\.md$", filename):
                return  # Valid informal doc

            # Check for specific documentation patterns
            valid_patterns = [
                r"^README\.md$",
                r"^README_[A-Z_]+\.md$",
                r"^CHANGELOG\.md$",
                r"^CONTRIBUTING\.md$",
                r"^LICENSE\.md$",
                r"^PHASE_\d+_.*\.md$",
                r"^CERTIFICATE_.*\.md$",
                r"^FORCING_ROUTE\.md$",
            ]

            if any(re.match(p, filename) for p in valid_patterns):
                return

            # Check for forbidden patterns in root
            if filepath.parent == self.repo_root or "phases" in filepath.parts:
                if not self._is_valid_doc_location(filepath):
                    self.violations.append(
                        Violation(
                            filepath=filepath,
                            rule="DOC-001",
                            severity=Severity.WARNING,
                            message=f"Documentation file may need relocation: {filename}",
                            auto_fixable=False,
                        )
                    )

    def _is_valid_doc_location(self, filepath: Path) -> bool:
        """Check if documentation file is in a valid location."""
        # Valid locations for documentation
        valid_dirs = {"docs", "docs_html", "artifacts", "contracts"}
        return any(d in filepath.parts for d in valid_dirs)

    def _validate_hierarchy_depth(self, filepath: Path) -> None:
        """Validate file is within maximum hierarchy depth."""
        # Calculate depth from src/ directory
        parts = filepath.parts
        if "src" in parts:
            src_idx = parts.index("src")
            depth = len(parts) - src_idx

            if depth > self.rules.MAX_HIERARCHY_DEPTH:
                self.violations.append(
                    Violation(
                        filepath=filepath,
                        rule="HIERARCHY-001",
                        severity=Severity.WARNING,
                        message=f"File exceeds maximum hierarchy depth ({depth} > {self.rules.MAX_HIERARCHY_DEPTH})",
                        auto_fixable=False,
                    )
                )

    def _validate_python_metadata(self, filepath: Path) -> None:
        """Validate Python file has required metadata."""
        if filepath.name.startswith("__") or filepath.name == "__init__.py":
            return  # Skip dunder files

        try:
            content = filepath.read_text()
            tree = ast.parse(content)

            # Check for required metadata in phase modules
            if self._is_phase_module(filepath):
                required_metadata = ["__version__", "__phase__", "__stage__"]
                found_metadata = set()

                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if target.id in required_metadata:
                                    found_metadata.add(target.id)

                missing = set(required_metadata) - found_metadata
                if missing:
                    self.violations.append(
                        Violation(
                            filepath=filepath,
                            rule="META-001",
                            severity=Severity.WARNING,
                            message=f"Missing required metadata: {', '.join(missing)}",
                            auto_fixable=True,
                        )
                    )

        except (SyntaxError, UnicodeDecodeError):
            pass

    def _validate_directory_structure(self) -> None:
        """Validate directory structure compliance."""
        phases_dir = self.repo_root / "src/farfan_pipeline/phases"

        if not phases_dir.exists():
            return

        # Check for forbidden directories
        for root, dirs, _ in os.walk(phases_dir):
            for dir_name in dirs:
                if dir_name.lower() in self.rules.FORBIDDEN_DIRS:
                    self.violations.append(
                        Violation(
                            filepath=Path(root) / dir_name,
                            rule="DIR-001",
                            severity=Severity.ERROR,
                            message=f"Forbidden directory name: {dir_name}",
                            auto_fixable=False,
                        )
                    )

    def _validate_phase_directories(self) -> None:
        """Validate phase directory naming."""
        phases_dir = self.repo_root / "src/farfan_pipeline/phases"

        if not phases_dir.exists():
            return

        for item in phases_dir.iterdir():
            if not item.is_dir():
                continue

            dir_name = item.name

            # Skip hidden directories
            if dir_name.startswith("."):
                continue

            # Check if it's a combined phase directory (violation)
            if re.match(r"^Phase_[a-z]+(_[a-z]+)+$", dir_name):
                self.violations.append(
                    Violation(
                        filepath=item,
                        rule="PHASE-DIR-001",
                        severity=Severity.ERROR,
                        message=f"Combined phase directory must be split: {dir_name}",
                        suggestion="Split into separate Phase_4, Phase_5, Phase_6, Phase_7 directories",
                        auto_fixable=False,
                    )
                )
                continue

            # Check if it matches Phase_N pattern
            if not self.rules.PHASE_DIR_PATTERN.match(dir_name):
                # Check if it's an old-style phase name (Phase_zero, Phase_one, etc.)
                old_style_match = re.match(
                    r"^Phase_(?P<name>zero|one|two|three|four|five|six|seven|eight|nine)$", dir_name
                )
                if old_style_match:
                    name_map = {
                        "zero": "0",
                        "one": "1",
                        "two": "2",
                        "three": "3",
                        "four": "4",
                        "five": "5",
                        "six": "6",
                        "seven": "7",
                        "eight": "8",
                        "nine": "9",
                    }
                    new_name = f"Phase_{name_map[old_style_match.group('name')]}"
                    self.violations.append(
                        Violation(
                            filepath=item,
                            rule="PHASE-DIR-002",
                            severity=Severity.ERROR,
                            message=f"Old-style phase directory name: {dir_name}",
                            suggestion=f"Rename to: {new_name}",
                            auto_fixable=True,
                            fix_command=f"git mv {dir_name} {new_name}",
                        )
                    )
                else:
                    self.violations.append(
                        Violation(
                            filepath=item,
                            rule="PHASE-DIR-003",
                            severity=Severity.ERROR,
                            message=f"Invalid phase directory name: {dir_name}",
                            suggestion="Use Phase_0 through Phase_9 naming",
                            auto_fixable=False,
                        )
                    )

    def _suggest_phase_name(self, filepath: Path) -> str:
        """Suggest a proper phase name based on file location and content."""
        parts = filepath.parts

        # Try to extract phase from directory
        phase = "0"
        for i, part in enumerate(parts):
            if part == "phases" and i + 1 < len(parts):
                phase_dir = parts[i + 1]
                # Extract phase number from Phase_N or Phase_N
                match = re.search(r"Phase_?(\d)", phase_dir)
                if match:
                    phase = match.group(1)
                else:
                    # Try old-style names
                    name_map = {
                        "zero": "0",
                        "one": "1",
                        "two": "2",
                        "three": "3",
                        "four": "4",
                        "five": "5",
                        "six": "6",
                        "seven": "7",
                        "eight": "8",
                        "nine": "9",
                    }
                    for name, num in name_map.items():
                        if name in phase_dir.lower():
                            phase = num
                            break

        # Default to stage 10, order 00 if unknown
        stage = "10"
        order = "00"

        # Try to guess from filename
        stem = filepath.stem
        if stem.startswith("phase"):
            # Already has phase prefix
            return f"Use pattern: phase{phase}_{stage}_{order}_{{name}}.py"

        # Generate descriptive name from filename
        name = stem.lower().replace("-", "_").replace(" ", "_")
        # Remove non-alphanumeric characters (except underscores)
        name = re.sub(r"[^a-z0-9_]", "", name)
        # Ensure it starts with a letter
        if name and name[0].isdigit():
            name = f"file_{name}"

        return f"phase{phase}_{stage}_{order}_{name}.py"

    def _generate_report(self, files_validated: List[Path]) -> ComplianceReport:
        """Generate compliance report."""
        # Count violations by severity
        errors = sum(1 for v in self.violations if v.severity == Severity.ERROR)
        warnings = sum(1 for v in self.violations if v.severity == Severity.WARNING)

        # Count compliant files
        violating_files = set(v.filepath for v in self.violations)
        compliant_count = len(files_validated) - len(violating_files)

        report = ComplianceReport(
            timestamp=datetime.utcnow().isoformat(),
            enforcement_level=self.level.value,
            total_files=len(files_validated),
            compliant_files=compliant_count,
            non_compliant_files=len(violating_files),
            violations=self.violations,
            auto_fixable_count=sum(1 for v in self.violations if v.auto_fixable),
            manual_fix_required_count=sum(1 for v in self.violations if not v.auto_fixable),
        )

        report.calculate_score()
        return report

    def print_report(self, report: ComplianceReport) -> None:
        """Print compliance report to stdout."""
        print("\n" + "=" * 70)
        print("GNEA COMPLIANCE REPORT")
        print("=" * 70)
        print(f"Timestamp: {report.timestamp}")
        print(f"Enforcement Level: {report.enforcement_level}")
        print(f"Repository: {self.repo_root}")
        print("-" * 70)
        print(f"Total Files: {report.total_files}")
        print(f"Compliant Files: {report.compliant_files}")
        print(f"Non-Compliant Files: {report.non_compliant_files}")
        print(f"Compliance Score: {report.compliance_score:.1f}%")
        print("-" * 70)
        print(f"Total Violations: {len(report.violations)}")
        print(f"  Errors: {sum(1 for v in report.violations if v.severity == Severity.ERROR)}")
        print(f"  Warnings: {sum(1 for v in report.violations if v.severity == Severity.WARNING)}")
        print(f"Auto-fixable: {report.auto_fixable_count}")
        print(f"Manual Fix Required: {report.manual_fix_required_count}")
        print("=" * 70)

        if report.violations:
            print("\nVIOLATIONS:")
            print("-" * 70)

            # Group violations by file
            violations_by_file: Dict[Path, List[Violation]] = {}
            for v in report.violations:
                if v.filepath not in violations_by_file:
                    violations_by_file[v.filepath] = []
                violations_by_file[v.filepath].append(v)

            for filepath, violations in sorted(violations_by_file.items()):
                rel_path = (
                    filepath.relative_to(self.repo_root) if filepath.is_absolute() else filepath
                )
                print(f"\n{rel_path}:")
                for v in violations:
                    prefix = "[ERROR]" if v.severity == Severity.ERROR else "[WARN]"
                    print(f"  {prefix} {v.rule}: {v.message}")
                    if v.suggestion:
                        print(f"        Suggestion: {v.suggestion}")

        print("\n" + "=" * 70)

        if report.compliance_score >= 99.5:
            print("STATUS: PASS - Compliance >= 99.5%")
        elif report.compliance_score >= 95.0:
            print("STATUS: WARNING - Compliance between 95% and 99.5%")
        else:
            print("STATUS: FAIL - Compliance < 95%")
        print("=" * 70 + "\n")


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="GNEA Enforcer - Validate nomenclature compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gnea_enforcer.py                    # Validate at L1 (guided) level
  python gnea_enforcer.py --level L2         # Validate at L2 (enforced) level
  python gnea_enforcer.py --output report.json --verbose
        """,
    )

    parser.add_argument(
        "--level",
        choices=["L0", "L1", "L2", "L3", "L4"],
        default="L1",
        help="Enforcement level (default: L1)",
    )

    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Path to repository root (default: current directory)",
    )

    parser.add_argument("--output", type=Path, default=None, help="Output file for JSON report")

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    parser.add_argument(
        "--fail-on-violations", action="store_true", help="Exit with error code if violations found"
    )

    args = parser.parse_args()

    # Map level string to enum
    level_map = {
        "L0": EnforcementLevel.L0_ADVISORY,
        "L1": EnforcementLevel.L1_GUIDED,
        "L2": EnforcementLevel.L2_ENFORCED,
        "L3": EnforcementLevel.L3_SEALED,
        "L4": EnforcementLevel.L4_FORENSIC,
    }

    enforcer = GNEAEnforcer(level=level_map[args.level], repo_root=args.path, verbose=args.verbose)

    report = enforcer.validate_repository()
    enforcer.print_report(report)

    # Save JSON report if requested
    if args.output:
        report_dict = {
            "timestamp": report.timestamp,
            "enforcement_level": report.enforcement_level,
            "total_files": report.total_files,
            "compliant_files": report.compliant_files,
            "non_compliant_files": report.non_compliant_files,
            "compliance_score": report.compliance_score,
            "violations": [
                {
                    "filepath": str(v.filepath),
                    "rule": v.rule,
                    "severity": v.severity.value,
                    "message": v.message,
                    "suggestion": v.suggestion,
                    "auto_fixable": v.auto_fixable,
                }
                for v in report.violations
            ],
        }
        args.output.write_text(json.dumps(report_dict, indent=2))

    # Return exit code
    if args.fail_on_violations and report.violations:
        return 1

    return 0


if __name__ == "__main__":
    # Import os for directory walking
    import os

    sys.exit(main())
