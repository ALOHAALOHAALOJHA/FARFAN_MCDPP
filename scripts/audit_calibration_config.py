#!/usr/bin/env python3
"""
Calibration Configuration Audit System

Performs comprehensive audit of:
1. Hardcoded calibration values in Python files (AST parser)
2. Duplicate/legacy configuration files
3. Archives deprecated files with timestamp
4. Consolidates to single source of truth in system/config/
"""

import ast
import hashlib
import json
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class CalibrationAuditVisitor(ast.NodeVisitor):
    """AST visitor to detect hardcoded calibration values in Python code."""

    CALIBRATION_PATTERNS = {
        "threshold",
        "weight",
        "score",
        "alpha",
        "beta",
        "gamma",
        "prior",
        "coefficient",
        "factor",
        "rate",
        "ratio",
        "min_",
        "max_",
        "baseline",
        "confidence",
        "epsilon",
        "tolerance",
    }

    EXCLUDE_VALUES = {0.0, 1.0, 2, 100, -1}

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.violations: list[dict[str, Any]] = []
        self.current_function: str | None = None
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                if self._is_calibration_variable(var_name):
                    value = self._extract_value(node.value)
                    if value is not None and self._is_suspicious_value(value):
                        self._add_violation(
                            node.lineno,
                            "assignment",
                            f"{var_name} = {value}",
                            var_name,
                            value,
                        )
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        for key, value in zip(node.keys, node.values, strict=False):
            if key and isinstance(key, ast.Constant):
                key_str = str(key.value)
                if self._is_calibration_variable(key_str):
                    val = self._extract_value(value)
                    if val is not None and self._is_suspicious_value(val):
                        self._add_violation(
                            node.lineno,
                            "dict_entry",
                            f'"{key_str}": {val}',
                            key_str,
                            val,
                        )
        self.generic_visit(node)

    def _is_calibration_variable(self, name: str) -> bool:
        """Check if variable name suggests calibration parameter."""
        name_lower = name.lower()
        return any(pattern in name_lower for pattern in self.CALIBRATION_PATTERNS)

    def _is_suspicious_value(self, value: Any) -> bool:
        """Check if value is suspicious calibration constant."""
        if not isinstance(value, int | float):
            return False
        if value in self.EXCLUDE_VALUES:
            return False
        if isinstance(value, float) and 0.0 < value < 1.0:
            return True
        return bool(isinstance(value, int) and value > 2)

    def _extract_value(self, node: ast.AST) -> Any | None:
        """Extract constant value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            inner = self._extract_value(node.operand)
            if inner is not None:
                return -inner
        return None

    def _add_violation(
        self,
        lineno: int,
        violation_type: str,
        code_snippet: str,
        var_name: str,
        value: Any,
    ) -> None:
        """Record a violation."""
        context = ""
        if self.current_class:
            context = f"{self.current_class}."
        if self.current_function:
            context += self.current_function

        self.violations.append(
            {
                "file": self.filepath,
                "line": lineno,
                "type": violation_type,
                "snippet": code_snippet,
                "variable": var_name,
                "value": value,
                "context": context,
                "severity": self._assess_severity(var_name, value),
            }
        )

    def _assess_severity(self, var_name: str, value: Any) -> str:
        """Assess violation severity."""
        critical_patterns = {
            "threshold",
            "weight",
            "coefficient",
            "prior",
            "alpha",
            "baseline",
        }
        name_lower = var_name.lower()

        if any(pattern in name_lower for pattern in critical_patterns):
            return "HIGH"
        elif isinstance(value, float) and 0.0 < value < 1.0:
            return "MEDIUM"
        return "LOW"


class ConfigurationFileAuditor:
    """Auditor for configuration file duplicates and integrity."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.config_files: dict[str, list[Path]] = defaultdict(list)
        self.file_hashes: dict[str, str] = {}

    def scan_config_files(self) -> None:
        """Scan for all configuration files."""
        patterns = ["*.json", "*.yaml", "*.yml", "*.toml"]

        for pattern in patterns:
            for filepath in self.root_path.rglob(pattern):
                if self._should_include_file(filepath):
                    filename = filepath.name
                    self.config_files[filename].append(filepath)
                    self.file_hashes[str(filepath)] = self._compute_hash(filepath)

    def _should_include_file(self, filepath: Path) -> bool:
        """Check if file should be included in audit."""
        exclude_patterns = [
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            ".pytest_cache",
            ".archive",
            "artifacts",
        ]

        path_str = str(filepath)
        if any(pattern in path_str for pattern in exclude_patterns):
            return False

        calibration_indicators = [
            "config",
            "calibration",
            "settings",
            "parameters",
            "intrinsic",
        ]
        return any(
            indicator in filepath.name.lower() for indicator in calibration_indicators
        )

    def _compute_hash(self, filepath: Path) -> str:
        """Compute SHA256 hash of file content."""
        try:
            with open(filepath, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def find_duplicates(self) -> list[dict[str, Any]]:
        """Find duplicate configuration files."""
        duplicates = []

        for filename, paths in self.config_files.items():
            if len(paths) > 1:
                hash_groups = defaultdict(list)
                for path in paths:
                    file_hash = self.file_hashes.get(str(path), "")
                    hash_groups[file_hash].append(path)

                for file_hash, duplicate_paths in hash_groups.items():
                    if len(duplicate_paths) > 1:
                        duplicates.append(
                            {
                                "filename": filename,
                                "paths": [str(p) for p in duplicate_paths],
                                "hash": file_hash,
                                "type": "exact_duplicate",
                            }
                        )
                    else:
                        duplicates.append(
                            {
                                "filename": filename,
                                "paths": [str(p) for p in paths],
                                "type": "name_collision",
                            }
                        )

        return duplicates

    def identify_canonical_structure(self) -> dict[str, str]:
        """Identify canonical configuration structure."""
        canonical_mapping = {
            "intrinsic_calibration.json": "system/config/calibration/intrinsic_calibration.json",
            "intrinsic_calibration_rubric.json": "system/config/calibration/intrinsic_calibration_rubric.json",
            "runtime_layers.json": "system/config/calibration/runtime_layers.json",
            "unit_transforms.json": "system/config/calibration/unit_transforms.json",
            "executor_config.json": "system/config/executor_config.json",
        }

        return canonical_mapping


class ConfigurationArchiver:
    """Archives deprecated configuration files with timestamps."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.archive_dir = (
            root_path / ".archive" / f"legacy_configs_{self._get_timestamp()}"
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp in YYYYMMDD format."""
        return datetime.now().strftime("%Y%m%d")

    def archive_file(self, source: Path, reason: str = "") -> Path:
        """Archive a single file with metadata."""
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        relative_path = source.relative_to(self.root_path)
        archive_path = self.archive_dir / relative_path

        archive_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source, archive_path)

        metadata_path = archive_path.parent / f"{archive_path.name}.metadata.json"
        metadata = {
            "original_path": str(relative_path),
            "archived_at": datetime.now().isoformat(),
            "reason": reason,
            "hash": self._compute_hash(source),
        }

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return archive_path

    def _compute_hash(self, filepath: Path) -> str:
        """Compute file hash."""
        try:
            with open(filepath, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""


class CalibrationAuditReport:
    """Generates comprehensive audit report."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.violations: list[dict[str, Any]] = []
        self.duplicates: list[dict[str, Any]] = []
        self.archived_files: list[dict[str, Any]] = []
        self.syntax_errors: list[dict[str, str]] = []

    def add_violations(self, violations: list[dict[str, Any]]) -> None:
        """Add code violations to report."""
        self.violations.extend(violations)

    def add_duplicates(self, duplicates: list[dict[str, Any]]) -> None:
        """Add duplicate files to report."""
        self.duplicates.extend(duplicates)

    def add_archived_file(self, original: str, archived: str, reason: str) -> None:
        """Record archived file."""
        self.archived_files.append(
            {"original": original, "archived": archived, "reason": reason}
        )

    def add_syntax_error(self, filepath: str, error: str) -> None:
        """Record syntax error."""
        self.syntax_errors.append({"file": filepath, "error": error})

    def generate_markdown(self, output_path: Path) -> None:
        """Generate markdown audit report."""
        lines = [
            "# Calibration Configuration Audit Report",
            "",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Executive Summary",
            "",
            f"- **Hardcoded Violations Found**: {len(self.violations)}",
            f"- **Duplicate Config Files**: {len(self.duplicates)}",
            f"- **Files Archived**: {len(self.archived_files)}",
            f"- **Syntax Errors**: {len(self.syntax_errors)}",
            "",
        ]

        if self.violations:
            lines.extend(self._generate_violations_section())

        if self.duplicates:
            lines.extend(self._generate_duplicates_section())

        if self.archived_files:
            lines.extend(self._generate_archive_section())

        if self.syntax_errors:
            lines.extend(self._generate_syntax_errors_section())

        lines.extend(self._generate_recommendations_section())

        output_path.write_text("\n".join(lines))

    def _generate_violations_section(self) -> list[str]:
        """Generate violations section."""
        lines = [
            "## Hardcoded Calibration Values",
            "",
            "The following hardcoded calibration values were detected via AST parsing:",
            "",
        ]

        by_severity = defaultdict(list)
        for v in self.violations:
            by_severity[v["severity"]].append(v)

        for severity in ["HIGH", "MEDIUM", "LOW"]:
            if severity in by_severity:
                lines.append(f"### {severity} Severity")
                lines.append("")

                by_file = defaultdict(list)
                for v in by_severity[severity]:
                    by_file[v["file"]].append(v)

                for filepath, violations in sorted(by_file.items()):
                    lines.append(f"#### `{filepath}`")
                    lines.append("")

                    for v in sorted(violations, key=lambda x: x["line"]):
                        context = f" (in `{v['context']}`)" if v["context"] else ""
                        lines.append(
                            f"- **Line {v['line']}**: `{v['snippet']}`{context}"
                        )
                        lines.append(f"  - Variable: `{v['variable']}`")
                        lines.append(f"  - Value: `{v['value']}`")
                        lines.append(f"  - Type: {v['type']}")
                        lines.append("")

        return lines

    def _generate_duplicates_section(self) -> list[str]:
        """Generate duplicates section."""
        lines = [
            "## Duplicate Configuration Files",
            "",
            "The following configuration files exist in multiple locations:",
            "",
        ]

        for dup in self.duplicates:
            lines.append(f"### `{dup['filename']}`")
            lines.append("")
            lines.append(f"**Type**: {dup['type']}")
            lines.append("")
            lines.append("**Locations**:")

            for path in dup["paths"]:
                lines.append(f"- `{path}`")

            if "hash" in dup:
                lines.append("")
                lines.append(f"**SHA256**: `{dup['hash'][:16]}...`")

            lines.append("")

        return lines

    def _generate_archive_section(self) -> list[str]:
        """Generate archive section."""
        lines = [
            "## Archived Files",
            "",
            "The following files have been archived:",
            "",
        ]

        for archived in self.archived_files:
            lines.append(f"- **Original**: `{archived['original']}`")
            lines.append(f"  - **Archived to**: `{archived['archived']}`")
            lines.append(f"  - **Reason**: {archived['reason']}")
            lines.append("")

        return lines

    def _generate_syntax_errors_section(self) -> list[str]:
        """Generate syntax errors section."""
        lines = [
            "## Syntax Errors",
            "",
            "The following files could not be parsed:",
            "",
        ]

        for error in self.syntax_errors:
            lines.append(f"- **File**: `{error['file']}`")
            lines.append(f"  - **Error**: {error['error']}")
            lines.append("")

        return lines

    def _generate_recommendations_section(self) -> list[str]:
        """Generate recommendations section."""
        lines = [
            "## Recommendations",
            "",
            "### Immediate Actions",
            "",
        ]

        if self.violations:
            high_severity = sum(1 for v in self.violations if v["severity"] == "HIGH")
            if high_severity > 0:
                lines.append(
                    f"1. **CRITICAL**: Address {high_severity} HIGH severity hardcoded values"
                )
                lines.append(
                    "   - Move these values to `system/config/calibration/` JSON files"
                )
                lines.append(
                    "   - Update code to load from configuration management system"
                )
                lines.append("")

        if self.duplicates:
            lines.append(
                f"2. **Consolidate**: Resolve {len(self.duplicates)} duplicate configuration files"
            )
            lines.append(
                "   - Verify canonical source: `system/config/calibration/intrinsic_calibration.json`"
            )
            lines.append("   - Remove or archive duplicates after validation")
            lines.append("")

        lines.extend(
            [
                "### Configuration Hierarchy",
                "",
                "Establish single source of truth:",
                "",
                "```",
                "system/config/",
                "├── calibration/",
                "│   ├── intrinsic_calibration.json       # Primary calibration scores",
                "│   ├── intrinsic_calibration_rubric.json # Scoring methodology",
                "│   ├── runtime_layers.json               # Layer definitions",
                "│   └── unit_transforms.json              # Unit transformations",
                "├── questionnaire/                        # Questionnaire configs",
                "└── executor_config.json                  # Executor settings",
                "```",
                "",
                "### Migration Strategy",
                "",
                "1. **Audit Phase** ✓ (Complete)",
                "2. **Consolidation Phase**: Merge duplicate configs to canonical location",
                "3. **Refactoring Phase**: Update code to use config management",
                "4. **Validation Phase**: Verify all systems reference canonical sources",
                "5. **Cleanup Phase**: Remove archived files after validation period",
                "",
            ]
        )

        return lines


def scan_python_files(
    root_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Scan all Python files for hardcoded calibration values."""
    violations = []
    syntax_errors = []

    python_files = list(root_path.rglob("*.py"))

    exclude_patterns = [
        ".venv",
        "venv",
        "node_modules",
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".archive",
        "artifacts",
    ]

    for py_file in python_files:
        path_str = str(py_file)

        if any(pattern in path_str for pattern in exclude_patterns):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(py_file))
            visitor = CalibrationAuditVisitor(str(py_file.relative_to(root_path)))
            visitor.visit(tree)
            violations.extend(visitor.violations)

        except SyntaxError as e:
            syntax_errors.append(
                {"file": str(py_file.relative_to(root_path)), "error": str(e)}
            )
        except Exception as e:
            syntax_errors.append(
                {
                    "file": str(py_file.relative_to(root_path)),
                    "error": f"Unexpected error: {str(e)}",
                }
            )

    return violations, syntax_errors


def main():
    """Main audit execution."""
    root_path = Path(__file__).parent.parent.resolve()

    print("=" * 80)
    print("CALIBRATION CONFIGURATION AUDIT")
    print("=" * 80)
    print()

    report = CalibrationAuditReport(root_path)

    print("[1/4] Scanning Python files for hardcoded calibration values...")
    violations, syntax_errors = scan_python_files(root_path)
    report.add_violations(violations)
    for error in syntax_errors:
        report.add_syntax_error(error["file"], error["error"])
    print(f"      Found {len(violations)} violations in Python code")
    print(f"      Encountered {len(syntax_errors)} syntax errors")
    print()

    print("[2/4] Scanning for duplicate configuration files...")
    auditor = ConfigurationFileAuditor(root_path)
    auditor.scan_config_files()
    duplicates = auditor.find_duplicates()
    report.add_duplicates(duplicates)
    print(f"      Found {len(duplicates)} duplicate configuration groups")
    print()

    print("[3/4] Archiving legacy configuration files...")
    archiver = ConfigurationArchiver(root_path)

    legacy_files = [
        (
            "config/intrinsic_calibration.json",
            "Superseded by system/config/calibration/",
        ),
        (
            "src/farfan_pipeline/core/calibration/intrinsic_calibration_rubric.json",
            "Moved to system/config/calibration/",
        ),
    ]

    archived_count = 0
    for legacy_file, reason in legacy_files:
        legacy_path = root_path / legacy_file
        if legacy_path.exists():
            archive_path = archiver.archive_file(legacy_path, reason)
            report.add_archived_file(
                legacy_file, str(archive_path.relative_to(root_path)), reason
            )
            archived_count += 1

    print(f"      Archived {archived_count} legacy files")
    print()

    print("[4/4] Generating audit report...")
    output_path = root_path / "violations_audit.md"
    report.generate_markdown(output_path)
    print(f"      Report generated: {output_path}")
    print()

    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Hardcoded violations: {len(violations)}")
    print(f"  - Duplicate configs: {len(duplicates)}")
    print(f"  - Files archived: {archived_count}")
    print(f"  - Syntax errors: {len(syntax_errors)}")
    print()
    print(f"Review the full report: {output_path}")
    print()


if __name__ == "__main__":
    main()
