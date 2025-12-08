#!/usr/bin/env python3
"""
Configuration Reference Validator

Validates that all Python code references canonical configuration paths
in system/config/ hierarchy. Detects legacy path references.
"""

import ast
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class ConfigReferenceVisitor(ast.NodeVisitor):
    """AST visitor to detect configuration file path references."""

    LEGACY_PATHS = {
        "config/intrinsic_calibration.json",
        "src/farfan_pipeline/core/calibration/intrinsic_calibration_rubric.json",
        "config/json_files_ no_schemas/executor_config.json",
    }

    CANONICAL_PATHS = {
        "system/config/calibration/intrinsic_calibration.json",
        "system/config/calibration/intrinsic_calibration_rubric.json",
        "system/config/calibration/runtime_layers.json",
        "system/config/calibration/unit_transforms.json",
        "system/config/executor_config.json",
    }

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.references: list[dict[str, str]] = []
        self.legacy_refs: list[dict[str, str]] = []
        self.canonical_refs: list[dict[str, str]] = []

    def visit_Constant(self, node: ast.Constant) -> None:
        """Visit string constants that might be paths."""
        if isinstance(node.value, str):
            self._check_path_reference(node.value, node.lineno)
        self.generic_visit(node)

    def visit_Str(self, node: ast.Str) -> None:
        """Visit string nodes (for older Python AST)."""
        self._check_path_reference(node.s, node.lineno)
        self.generic_visit(node)

    def _check_path_reference(self, value: str, lineno: int) -> None:
        """Check if string contains config path reference."""
        value_lower = value.lower()

        if any(
            pattern in value_lower
            for pattern in ["config", "calibration", "intrinsic", ".json", ".yaml"]
        ):
            ref = {
                "file": self.filepath,
                "line": lineno,
                "path": value,
                "type": "unknown",
            }

            if any(legacy in value for legacy in self.LEGACY_PATHS):
                ref["type"] = "LEGACY"
                self.legacy_refs.append(ref)
            elif any(canonical in value for canonical in self.CANONICAL_PATHS):
                ref["type"] = "CANONICAL"
                self.canonical_refs.append(ref)
            else:
                ref["type"] = "OTHER"

            self.references.append(ref)


class ConfigReferenceValidator:
    """Validates configuration references across codebase."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.legacy_refs: list[dict[str, str]] = []
        self.canonical_refs: list[dict[str, str]] = []
        self.other_refs: list[dict[str, str]] = []
        self.grep_results: dict[str, list[str]] = defaultdict(list)

    def scan_python_files(self) -> None:
        """Scan Python files for config references using AST."""
        python_files = list(self.root_path.rglob("*.py"))

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
                visitor = ConfigReferenceVisitor(
                    str(py_file.relative_to(self.root_path))
                )
                visitor.visit(tree)

                self.legacy_refs.extend(visitor.legacy_refs)
                self.canonical_refs.extend(visitor.canonical_refs)
                self.other_refs.extend(
                    [r for r in visitor.references if r["type"] == "OTHER"]
                )

            except SyntaxError:
                pass
            except Exception:
                pass

    def grep_legacy_patterns(self) -> None:
        """Use regex to find additional legacy path patterns."""
        legacy_patterns = [
            r"config/intrinsic_calibration\.json",
            r"src/farfan_pipeline/core/calibration/intrinsic_calibration_rubric\.json",
            r"config/json_files.*executor_config\.json",
        ]

        for pattern in legacy_patterns:
            self._grep_pattern(pattern)

    def _grep_pattern(self, pattern: str) -> None:
        """Grep for a specific pattern across Python files."""
        python_files = list(self.root_path.rglob("*.py"))
        compiled = re.compile(pattern)

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        if compiled.search(line):
                            self.grep_results[pattern].append(
                                f"{py_file.relative_to(self.root_path)}:{line_num}: {line.strip()}"
                            )
            except Exception:
                pass

    def generate_validation_report(self, output_path: Path) -> None:
        """Generate validation report."""
        lines = [
            "# Configuration Reference Validation Report",
            "",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Legacy References**: {len(self.legacy_refs)}",
            f"- **Canonical References**: {len(self.canonical_refs)}",
            f"- **Other Config References**: {len(self.other_refs)}",
            "",
        ]

        if self.legacy_refs:
            lines.extend(self._generate_legacy_section())

        if self.canonical_refs:
            lines.extend(self._generate_canonical_section())

        if self.other_refs:
            lines.extend(self._generate_other_section())

        if self.grep_results:
            lines.extend(self._generate_grep_section())

        lines.extend(self._generate_migration_guidance())

        output_path.write_text("\n".join(lines))

    def _generate_legacy_section(self) -> list[str]:
        """Generate legacy references section."""
        lines = [
            "## ⚠️ Legacy Configuration References",
            "",
            "The following code references legacy configuration paths that should be updated:",
            "",
        ]

        by_file = defaultdict(list)
        for ref in self.legacy_refs:
            by_file[ref["file"]].append(ref)

        for filepath, refs in sorted(by_file.items()):
            lines.append(f"### `{filepath}`")
            lines.append("")

            for ref in sorted(refs, key=lambda x: x["line"]):
                lines.append(f"- **Line {ref['line']}**: `{ref['path']}`")

            lines.append("")

        return lines

    def _generate_canonical_section(self) -> list[str]:
        """Generate canonical references section."""
        lines = [
            "## ✓ Canonical Configuration References",
            "",
            "The following code correctly references canonical configuration paths:",
            "",
        ]

        by_file = defaultdict(list)
        for ref in self.canonical_refs:
            by_file[ref["file"]].append(ref)

        for filepath, refs in sorted(by_file.items()):
            lines.append(f"### `{filepath}`")
            lines.append("")

            for ref in sorted(refs, key=lambda x: x["line"]):
                lines.append(f"- **Line {ref['line']}**: `{ref['path']}`")

            lines.append("")

        return lines

    def _generate_other_section(self) -> list[str]:
        """Generate other config references section."""
        lines = [
            "## Other Configuration References",
            "",
            "The following configuration references were detected (review for correctness):",
            "",
        ]

        by_file = defaultdict(list)
        for ref in self.other_refs:
            by_file[ref["file"]].append(ref)

        for filepath, refs in sorted(by_file.items()):
            lines.append(f"### `{filepath}`")
            lines.append("")

            for ref in sorted(refs, key=lambda x: x["line"]):
                lines.append(f"- **Line {ref['line']}**: `{ref['path']}`")

            lines.append("")

        return lines

    def _generate_grep_section(self) -> list[str]:
        """Generate grep results section."""
        lines = [
            "## Pattern Match Results",
            "",
            "Additional legacy path patterns found via regex search:",
            "",
        ]

        for pattern, results in sorted(self.grep_results.items()):
            if results:
                lines.append(f"### Pattern: `{pattern}`")
                lines.append("")

                for result in results[:20]:
                    lines.append(f"- {result}")

                if len(results) > 20:
                    lines.append(f"- ... and {len(results) - 20} more")

                lines.append("")

        return lines

    def _generate_migration_guidance(self) -> list[str]:
        """Generate migration guidance."""
        lines = [
            "## Migration Guidance",
            "",
            "### Step-by-Step Path Updates",
            "",
        ]

        if self.legacy_refs:
            lines.extend(
                [
                    "1. **Update Legacy References**",
                    "",
                    "   Replace legacy paths with canonical equivalents:",
                    "",
                    "   ```python",
                    "   # OLD (legacy)",
                    '   config_path = "config/intrinsic_calibration.json"',
                    "",
                    "   # NEW (canonical)",
                    '   config_path = "system/config/calibration/intrinsic_calibration.json"',
                    "   ```",
                    "",
                ]
            )

        lines.extend(
            [
                "2. **Use Configuration Manager**",
                "",
                "   Prefer using the configuration manager instead of hardcoded paths:",
                "",
                "   ```python",
                "   from system.config.config_manager import ConfigManager",
                "",
                "   config_mgr = ConfigManager()",
                '   calibration = config_mgr.get_config("calibration/intrinsic_calibration")',
                "   ```",
                "",
                "3. **Validation Steps**",
                "",
                "   - Update imports and path references",
                "   - Run unit tests to verify configuration loading",
                "   - Check integration tests for end-to-end validation",
                "   - Verify no hardcoded paths remain in production code",
                "",
                "### Canonical Path Reference",
                "",
                "All configuration files should reference:",
                "",
                "```",
                "system/config/",
                "├── calibration/",
                "│   ├── intrinsic_calibration.json",
                "│   ├── intrinsic_calibration_rubric.json",
                "│   ├── runtime_layers.json",
                "│   └── unit_transforms.json",
                "└── executor_config.json",
                "```",
                "",
            ]
        )

        return lines


def main():
    """Main validation execution."""
    root_path = Path(__file__).parent.parent.resolve()

    print("=" * 80)
    print("CONFIGURATION REFERENCE VALIDATION")
    print("=" * 80)
    print()

    validator = ConfigReferenceValidator(root_path)

    print("[1/3] Scanning Python files for config references (AST)...")
    validator.scan_python_files()
    print(f"      Legacy refs: {len(validator.legacy_refs)}")
    print(f"      Canonical refs: {len(validator.canonical_refs)}")
    print(f"      Other refs: {len(validator.other_refs)}")
    print()

    print("[2/3] Performing regex pattern matching...")
    validator.grep_legacy_patterns()
    total_grep = sum(len(results) for results in validator.grep_results.values())
    print(f"      Pattern matches: {total_grep}")
    print()

    print("[3/3] Generating validation report...")
    output_path = root_path / "config_reference_validation.md"
    validator.generate_validation_report(output_path)
    print(f"      Report generated: {output_path}")
    print()

    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print()

    if validator.legacy_refs:
        print(f"⚠️  Found {len(validator.legacy_refs)} legacy configuration references")
        print("   Review the report and update to canonical paths")
    else:
        print("✓ No legacy configuration references found")

    print()


if __name__ == "__main__":
    main()
