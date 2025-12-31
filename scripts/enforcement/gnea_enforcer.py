#!/usr/bin/env python3
"""
GNEA Global Nomenclature Enforcement Architecture Enforcer
Main enforcement script for F.A.R.F.A.N nomenclature compliance.

Document: FPN-GNEA-001
Version: 2.0.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

__version__ = "2.0.0"


class EnforcementLevel(Enum):
    L0_ADVISORY = "advisory"
    L1_GUIDED = "guided"
    L2_ENFORCED = "enforced"
    L3_SEALED = "sealed"
    L4_FORENSIC = "forensic"


class Severity(Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Violation:
    filepath: Path
    rule: str
    severity: Severity
    message: str
    suggestion: str | None = None
    auto_fixable: bool = False
    line_number: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "filepath": str(self.filepath),
            "rule": self.rule,
            "severity": self.severity.value,
            "message": self.message,
            "suggestion": self.suggestion,
            "auto_fixable": self.auto_fixable,
            "line_number": self.line_number,
        }


@dataclass
class ValidationResult:
    valid: bool
    violations: list[Violation] = field(default_factory=list)
    files_validated: int = 0
    auto_fixed: int = 0
    compliance_score: float = 100.0


class GNEAEnforcer:
    """Global Nomenclature Enforcement Architecture Enforcer."""

    PHASE_MODULE_PATTERN = re.compile(
        r"^phase(?P<phase>[0-9])_(?P<stage>\d{2})_(?P<order>\d{2})_(?P<name>[a-z][a-z0-9_]+)\.py$"
    )
    CONTRACT_PATTERN = re.compile(r"^Q(?P<num>\d{3})_executor_contract\.json$")
    ROOT_DOC_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]+\.(md|txt)$")
    PYTHON_MODULE_PATTERN = re.compile(r"^[a-z][a-z0-9_]+\.py$")
    SCRIPT_PATTERN = re.compile(r"^[a-z][a-z0-9_]+\.(py|sh)$")
    MANIFEST_PATTERN = re.compile(
        r"^(PHASE_[0-9]_MANIFEST|STAGE_\d{2}_MANIFEST|TEST_MANIFEST)\.json$"
    )
    CONSTANTS_PATTERN = re.compile(r"^PHASE_[0-9]_CONSTANTS\.py$")

    FORBIDDEN_DIRS = {"temp", "tmp", "backup", "old", "misc", "other", "stuff", "things"}
    MAX_HIERARCHY_DEPTH = 5
    ALLOWED_ROOT_SCRIPTS = {"RUN_PIPELINE.py", "install.sh", "run_pipeline.sh", "setup.py"}
    ALLOWED_ROOT_DOCS = {"README.md", "CHANGELOG.md", "README.ES.md"}

    REQUIRED_METADATA = [
        "__version__",
        "__phase__",
        "__stage__",
        "__order__",
        "__criticality__",
        "__execution_pattern__",
    ]

    def __init__(
        self,
        level: EnforcementLevel = EnforcementLevel.L1_GUIDED,
        root: Path | None = None,
        auto_fix: bool = False,
    ):
        self.level = level
        self.root = root or Path.cwd()
        self.auto_fix = auto_fix
        self.violations: list[Violation] = []
        self.files_validated = 0
        self.auto_fixed_count = 0
        self._load_rules()

    def _load_rules(self) -> None:
        """Load enforcement rules from configuration."""
        rules_path = Path(__file__).parent / "gnea_rules.json"
        if rules_path.exists():
            with open(rules_path) as f:
                self.rules = json.load(f)
        else:
            self.rules = {}

    def enforce(self, paths: list[str] | None = None) -> ValidationResult:
        """Main enforcement entry point."""
        if paths:
            filepaths = [Path(p) for p in paths]
        else:
            filepaths = list(self.root.rglob("*"))

        for filepath in filepaths:
            if self._should_skip(filepath):
                continue
            self._validate_file(filepath)
            self.files_validated += 1

        self._validate_hierarchy()
        self._validate_phase_structure()
        self._check_duplicates()

        if self.violations and self.auto_fix:
            self._attempt_auto_fixes()

        compliance_score = self._calculate_compliance_score()

        return ValidationResult(
            valid=len(self.violations) == 0,
            violations=self.violations,
            files_validated=self.files_validated,
            auto_fixed=self.auto_fixed_count,
            compliance_score=compliance_score,
        )

    def _should_skip(self, filepath: Path) -> bool:
        """Determine if file should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            "-env",
            ".egg-info",
            ".DS_Store",
        ]
        return any(pattern in str(filepath) for pattern in skip_patterns)

    def _validate_file(self, filepath: Path) -> None:
        """Validate single file against all applicable rules."""
        if not filepath.is_file():
            return

        rel_path = filepath.relative_to(self.root) if filepath.is_relative_to(self.root) else filepath

        if self._is_phase_module(filepath):
            self._validate_phase_module(filepath)
        elif self._is_contract(filepath):
            self._validate_contract(filepath)
        elif filepath.suffix == ".md":
            self._validate_documentation(filepath, rel_path)
        elif filepath.suffix == ".py":
            self._validate_python_file(filepath, rel_path)
        elif filepath.suffix == ".json":
            self._validate_json_file(filepath, rel_path)

    def _is_phase_module(self, filepath: Path) -> bool:
        """Check if file is in a phase directory."""
        return "phases" in filepath.parts and filepath.name.startswith("phase")

    def _is_contract(self, filepath: Path) -> bool:
        """Check if file is a contract."""
        return "executor_contract" in filepath.name and filepath.suffix == ".json"

    def _validate_phase_module(self, filepath: Path) -> None:
        """Validate phase module naming and structure."""
        if not self.PHASE_MODULE_PATTERN.match(filepath.name):
            suggestion = self._suggest_phase_name(filepath.name)
            self.violations.append(
                Violation(
                    filepath=filepath,
                    rule="PHASE-001",
                    severity=Severity.ERROR,
                    message=f"Invalid phase module name: {filepath.name}",
                    suggestion=suggestion,
                    auto_fixable=True,
                )
            )
            return

        match = self.PHASE_MODULE_PATTERN.match(filepath.name)
        if match:
            self._validate_phase_metadata(filepath, match.groupdict())

    def _validate_phase_metadata(self, filepath: Path, parts: dict[str, str]) -> None:
        """Validate phase module internal metadata."""
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception:
            return

        expected_phase = int(parts["phase"])
        expected_stage = int(parts["stage"])
        expected_order = int(parts["order"])

        if f"__phase__ = {expected_phase}" not in content:
            self.violations.append(
                Violation(
                    filepath=filepath,
                    rule="PHASE-002",
                    severity=Severity.ERROR,
                    message=f"Phase metadata mismatch: expected __phase__ = {expected_phase}",
                    auto_fixable=True,
                )
            )

        if f"__stage__ = {expected_stage}" not in content:
            self.violations.append(
                Violation(
                    filepath=filepath,
                    rule="PHASE-003",
                    severity=Severity.ERROR,
                    message=f"Stage metadata mismatch: expected __stage__ = {expected_stage}",
                    auto_fixable=True,
                )
            )

        if f"__order__ = {expected_order}" not in content:
            self.violations.append(
                Violation(
                    filepath=filepath,
                    rule="PHASE-004",
                    severity=Severity.WARNING,
                    message=f"Order metadata mismatch: expected __order__ = {expected_order}",
                    auto_fixable=True,
                )
            )

        for metadata in self.REQUIRED_METADATA:
            if metadata not in content:
                self.violations.append(
                    Violation(
                        filepath=filepath,
                        rule="PHASE-005",
                        severity=Severity.WARNING,
                        message=f"Missing required metadata: {metadata}",
                        auto_fixable=True,
                    )
                )

    def _validate_contract(self, filepath: Path) -> None:
        """Validate contract naming."""
        if not self.CONTRACT_PATTERN.match(filepath.name):
            self.violations.append(
                Violation(
                    filepath=filepath,
                    rule="CONTRACT-001",
                    severity=Severity.ERROR,
                    message=f"Invalid contract name: {filepath.name}",
                    suggestion="Format: Q###_executor_contract.json",
                    auto_fixable=True,
                )
            )

    def _validate_documentation(self, filepath: Path, rel_path: Path) -> None:
        """Validate documentation files."""
        if len(rel_path.parts) == 1:
            if filepath.name not in self.ALLOWED_ROOT_DOCS:
                if not self.ROOT_DOC_PATTERN.match(filepath.name):
                    self.violations.append(
                        Violation(
                            filepath=filepath,
                            rule="DOC-001",
                            severity=Severity.ERROR,
                            message=f"Root documentation must use UPPER_SNAKE_CASE: {filepath.name}",
                            auto_fixable=True,
                        )
                    )

    def _validate_python_file(self, filepath: Path, rel_path: Path) -> None:
        """Validate Python files."""
        if len(rel_path.parts) == 1:
            if filepath.name not in self.ALLOWED_ROOT_SCRIPTS:
                self.violations.append(
                    Violation(
                        filepath=filepath,
                        rule="SCRIPT-001",
                        severity=Severity.WARNING,
                        message=f"Script should be in scripts/: {filepath.name}",
                        suggestion=f"Move to scripts/{filepath.name}",
                        auto_fixable=False,
                    )
                )

    def _validate_json_file(self, filepath: Path, rel_path: Path) -> None:
        """Validate JSON files."""
        pass

    def _validate_hierarchy(self) -> None:
        """Validate directory hierarchy."""
        for path in self.root.rglob("*"):
            if path.is_file():
                try:
                    rel_path = path.relative_to(self.root)
                    depth = len(rel_path.parts)
                    if depth > self.MAX_HIERARCHY_DEPTH:
                        self.violations.append(
                            Violation(
                                filepath=path,
                                rule="HIERARCHY-001",
                                severity=Severity.WARNING,
                                message=f"Hierarchy depth {depth} exceeds max {self.MAX_HIERARCHY_DEPTH}",
                                auto_fixable=False,
                            )
                        )
                except ValueError:
                    # If for any reason the path cannot be made relative to root, skip it.
                    # This is a defensive guard for edge cases in filesystem traversal.
                    pass

            if path.is_dir() and path.name.lower() in self.FORBIDDEN_DIRS:
                self.violations.append(
                    Violation(
                        filepath=path,
                        rule="HIERARCHY-002",
                        severity=Severity.ERROR,
                        message=f"Forbidden directory name: {path.name}",
                        auto_fixable=False,
                    )
                )

    def _validate_phase_structure(self) -> None:
        """Validate each phase has required structure."""
        phases_dir = self.root / "src" / "farfan_pipeline" / "phases"
        if not phases_dir.exists():
            return

        for phase_dir in phases_dir.iterdir():
            if not phase_dir.is_dir() or not phase_dir.name.startswith("Phase_"):
                continue

            phase_match = re.match(r"Phase_(\w+)", phase_dir.name)
            if not phase_match:
                continue

            phase_name = phase_match.group(1)
            phase_num = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
                        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}.get(phase_name.lower())

            if phase_num is None:
                continue

            required_files = [
                f"PHASE_{phase_num}_MANIFEST.json",
                f"PHASE_{phase_num}_CONSTANTS.py",
                "README.md",
                "__init__.py",
            ]

            for req_file in required_files:
                if not (phase_dir / req_file).exists():
                    self.violations.append(
                        Violation(
                            filepath=phase_dir / req_file,
                            rule="PHASE-STRUCTURE-001",
                            severity=Severity.ERROR,
                            message=f"Missing required phase file: {req_file}",
                            auto_fixable=True,
                        )
                    )

            required_dirs = ["tests", "contracts", "docs"]
            for req_dir in required_dirs:
                if not (phase_dir / req_dir).exists():
                    self.violations.append(
                        Violation(
                            filepath=phase_dir / req_dir,
                            rule="PHASE-STRUCTURE-002",
                            severity=Severity.WARNING,
                            message=f"Missing recommended phase directory: {req_dir}",
                            auto_fixable=True,
                        )
                    )

    def _check_duplicates(self) -> None:
        """Detect duplicate files by content hash."""
        hashes: dict[str, Path] = {}
        extensions = {".py", ".json", ".md"}

        for filepath in self.root.rglob("*"):
            if filepath.is_file() and filepath.suffix in extensions:
                if self._should_skip(filepath):
                    continue
                try:
                    content = filepath.read_bytes()
                    hash_val = hashlib.md5(content).hexdigest()

                    if hash_val in hashes:
                        self.violations.append(
                            Violation(
                                filepath=filepath,
                                rule="DUPLICATE-001",
                                severity=Severity.WARNING,
                                message=f"Duplicate content of: {hashes[hash_val]}",
                                auto_fixable=False,
                            )
                        )
                    else:
                        hashes[hash_val] = filepath
                except Exception:
                    # Best-effort duplicate detection: ignore files that cannot be read
                    # (e.g., binary files, permission issues, or encoding errors).
                    pass

    def _suggest_phase_name(self, current_name: str) -> str:
        """Generate suggestion for phase module name."""
        parts = current_name.replace(".py", "").split("_")
        if len(parts) >= 2:
            phase = parts[0].replace("phase", "") if parts[0].startswith("phase") else "X"
            name = "_".join(parts[1:]) if len(parts) > 1 else "unnamed"
            return f"phase{phase}_XX_XX_{name}.py"
        return "phase{N}_{SS}_{OO}_{name}.py"

    def _attempt_auto_fixes(self) -> None:
        """Attempt to auto-fix violations."""
        for violation in self.violations:
            if violation.auto_fixable:
                if self._auto_fix_violation(violation):
                    self.auto_fixed_count += 1

    def _auto_fix_violation(self, violation: Violation) -> bool:
        """Auto-fix a single violation."""
        if violation.rule.startswith("PHASE-STRUCTURE"):
            return self._auto_fix_phase_structure(violation)
        return False

    def _auto_fix_phase_structure(self, violation: Violation) -> bool:
        """Auto-fix missing phase structure."""
        filepath = violation.filepath
        if "Missing required phase file" in violation.message:
            if filepath.name.endswith(".py"):
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text('"""Auto-generated placeholder."""\n')
                return True
            elif filepath.name.endswith(".json"):
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text("{}\n")
                return True
            elif filepath.name == "README.md":
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text(f"# {filepath.parent.name}\n\nTODO: Add documentation\n")
                return True
        elif "Missing recommended phase directory" in violation.message:
            filepath.mkdir(parents=True, exist_ok=True)
            return True
        return False

    def _calculate_compliance_score(self) -> float:
        """Calculate compliance score."""
        if self.files_validated == 0:
            return 100.0
        error_count = sum(1 for v in self.violations if v.severity in [Severity.ERROR, Severity.CRITICAL])
        return max(0.0, 100.0 - (error_count / self.files_validated * 100))

    def generate_report(self) -> dict[str, Any]:
        """Generate enforcement report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "enforcer_version": __version__,
            "enforcement_level": self.level.value,
            "files_validated": self.files_validated,
            "violation_count": len(self.violations),
            "auto_fixed_count": self.auto_fixed_count,
            "compliance_score": self._calculate_compliance_score(),
            "violations": [v.to_dict() for v in self.violations],
            "summary": {
                "critical": sum(1 for v in self.violations if v.severity == Severity.CRITICAL),
                "error": sum(1 for v in self.violations if v.severity == Severity.ERROR),
                "warning": sum(1 for v in self.violations if v.severity == Severity.WARNING),
                "info": sum(1 for v in self.violations if v.severity == Severity.INFO),
            },
        }

    def generate_compliance_proof(self) -> dict[str, Any]:
        """Generate cryptographic proof of compliance."""
        report = self.generate_report()
        proof_str = json.dumps(report, sort_keys=True)
        proof_hash = hashlib.sha256(proof_str.encode()).hexdigest()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "enforcer_version": __version__,
            "level": self.level.value,
            "files_validated": self.files_validated,
            "violations": len(self.violations),
            "compliance_score": report["compliance_score"],
            "hash": proof_hash,
        }


def main():
    parser = argparse.ArgumentParser(
        description="GNEA Global Nomenclature Enforcement Architecture Enforcer"
    )
    parser.add_argument(
        "--level",
        choices=["L0", "L1", "L2", "L3", "L4"],
        default="L1",
        help="Enforcement level",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Root path to validate",
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Attempt automatic fixes",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Output report file path",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files to validate",
    )

    args = parser.parse_args()

    level_map = {
        "L0": EnforcementLevel.L0_ADVISORY,
        "L1": EnforcementLevel.L1_GUIDED,
        "L2": EnforcementLevel.L2_ENFORCED,
        "L3": EnforcementLevel.L3_SEALED,
        "L4": EnforcementLevel.L4_FORENSIC,
    }

    enforcer = GNEAEnforcer(
        level=level_map[args.level],
        root=args.path,
        auto_fix=args.auto_fix,
    )

    result = enforcer.enforce(args.files if args.files else None)
    report = enforcer.generate_report()

    print("=" * 70)
    print("GNEA NOMENCLATURE ENFORCEMENT REPORT")
    print("=" * 70)
    print(f"Enforcement Level: {args.level}")
    print(f"Files Validated: {result.files_validated}")
    print(f"Compliance Score: {result.compliance_score:.1f}%")
    print(f"Total Violations: {len(result.violations)}")
    print(f"Auto-fixed: {result.auto_fixed}")
    print()

    if result.violations:
        print(f"❌ {report['summary']['critical']} CRITICAL")
        print(f"❌ {report['summary']['error']} ERRORS")
        print(f"⚠️  {report['summary']['warning']} WARNINGS")
        print(f"ℹ️  {report['summary']['info']} INFO")
        print()

        for v in result.violations[:20]:
            icon = "❌" if v.severity in [Severity.CRITICAL, Severity.ERROR] else "⚠️"
            print(f"{icon} [{v.rule}] {v.filepath}")
            print(f"    {v.message}")
            if v.suggestion:
                print(f"    💡 {v.suggestion}")

        if len(result.violations) > 20:
            print(f"\n... and {len(result.violations) - 20} more violations")
    else:
        print("✅ ALL ARTIFACTS COMPLY WITH GNEA POLICY")

    print("=" * 70)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {args.report}")

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
