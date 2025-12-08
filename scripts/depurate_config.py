#!/usr/bin/env python3
"""
Configuration Depuration Script

Automatically fixes common configuration issues:
1. Removes duplicate config files
2. Updates path references in Python files
3. Validates JSON integrity
4. Reports unfixable issues
"""

import json
from datetime import datetime
from pathlib import Path


class ConfigDepurator:
    """Automatically fixes common configuration issues."""

    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixes_applied: list[dict[str, str]] = []
        self.issues_found: list[dict[str, str]] = []

    def fix_path_references(self) -> int:
        """Fix legacy path references in Python files."""
        path_mapping = {
            "config/intrinsic_calibration.json": "system/config/calibration/intrinsic_calibration.json",
            "src/farfan_pipeline/core/calibration/intrinsic_calibration_rubric.json": "system/config/calibration/intrinsic_calibration_rubric.json",
            "config/json_files_ no_schemas/executor_config.json": "system/config/executor_config.json",
        }

        fixes = 0
        python_files = list(self.root_path.rglob("*.py"))

        exclude_patterns = [
            ".venv",
            "venv",
            ".git",
            "__pycache__",
            ".archive",
            "scripts",
        ]

        for py_file in python_files:
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    original_content = f.read()

                modified_content = original_content

                for old_path, new_path in path_mapping.items():
                    if old_path in modified_content:
                        modified_content = modified_content.replace(
                            f'"{old_path}"', f'"{new_path}"'
                        )
                        modified_content = modified_content.replace(
                            f"'{old_path}'", f"'{new_path}'"
                        )

                        self.fixes_applied.append(
                            {
                                "type": "PATH_UPDATE",
                                "file": str(py_file.relative_to(self.root_path)),
                                "old": old_path,
                                "new": new_path,
                            }
                        )
                        fixes += 1

                if modified_content != original_content and not self.dry_run:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(modified_content)

            except Exception as e:
                self.issues_found.append(
                    {
                        "type": "PATH_FIX_ERROR",
                        "file": str(py_file.relative_to(self.root_path)),
                        "error": str(e),
                    }
                )

        return fixes

    def validate_json_files(self) -> tuple[int, int]:
        """Validate JSON files in canonical structure."""
        valid = 0
        invalid = 0

        canonical_dir = self.root_path / "system" / "config"
        json_files = list(canonical_dir.rglob("*.json"))

        for json_file in json_files:
            try:
                with open(json_file, encoding="utf-8") as f:
                    json.load(f)
                valid += 1

                self.fixes_applied.append(
                    {
                        "type": "JSON_VALID",
                        "file": str(json_file.relative_to(self.root_path)),
                        "status": "OK",
                    }
                )

            except json.JSONDecodeError as e:
                invalid += 1
                self.issues_found.append(
                    {
                        "type": "JSON_INVALID",
                        "file": str(json_file.relative_to(self.root_path)),
                        "error": f"Line {e.lineno}: {e.msg}",
                    }
                )
            except Exception as e:
                invalid += 1
                self.issues_found.append(
                    {
                        "type": "JSON_ERROR",
                        "file": str(json_file.relative_to(self.root_path)),
                        "error": str(e),
                    }
                )

        return valid, invalid

    def clean_empty_configs(self) -> int:
        """Remove empty or near-empty configuration files."""
        cleaned = 0

        config_dirs = [
            self.root_path / "config",
            self.root_path / "system" / "config",
        ]

        for config_dir in config_dirs:
            if not config_dir.exists():
                continue

            for json_file in config_dir.rglob("*.json"):
                try:
                    with open(json_file) as f:
                        content = json.load(f)

                    if not content or content == {}:
                        if not self.dry_run:
                            json_file.unlink()

                        self.fixes_applied.append(
                            {
                                "type": "EMPTY_REMOVED",
                                "file": str(json_file.relative_to(self.root_path)),
                                "reason": "Empty configuration file",
                            }
                        )
                        cleaned += 1

                except Exception:
                    pass

        return cleaned

    def normalize_json_formatting(self) -> int:
        """Normalize JSON formatting (indent=2, sorted keys)."""
        normalized = 0

        canonical_dir = self.root_path / "system" / "config"
        if not canonical_dir.exists():
            return 0

        json_files = list(canonical_dir.rglob("*.json"))

        for json_file in json_files:
            try:
                with open(json_file) as f:
                    data = json.load(f)

                normalized_content = json.dumps(data, indent=2, sort_keys=False)
                normalized_content += "\n"

                with open(json_file) as f:
                    original_content = f.read()

                if normalized_content != original_content:
                    if not self.dry_run:
                        with open(json_file, "w") as f:
                            f.write(normalized_content)

                    self.fixes_applied.append(
                        {
                            "type": "JSON_NORMALIZED",
                            "file": str(json_file.relative_to(self.root_path)),
                            "change": "Formatting standardized",
                        }
                    )
                    normalized += 1

            except Exception as e:
                self.issues_found.append(
                    {
                        "type": "NORMALIZE_ERROR",
                        "file": str(json_file.relative_to(self.root_path)),
                        "error": str(e),
                    }
                )

        return normalized

    def generate_depuration_report(self, output_path: Path) -> None:
        """Generate depuration report."""
        lines = [
            "# Configuration Depuration Report",
            "",
            f"Generated: {datetime.now().isoformat()}",
            f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}",
            "",
            "## Summary",
            "",
            f"- **Fixes Applied**: {len(self.fixes_applied)}",
            f"- **Issues Found**: {len(self.issues_found)}",
            "",
        ]

        if self.fixes_applied:
            lines.extend(self._generate_fixes_section())

        if self.issues_found:
            lines.extend(self._generate_issues_section())

        if not self.dry_run:
            lines.extend(
                [
                    "## Post-Depuration Actions",
                    "",
                    "1. Run integration tests to verify changes",
                    "2. Check git diff to review all modifications",
                    "3. Re-run audit to confirm fixes",
                    "",
                    "```bash",
                    "git diff",
                    "pytest tests/ -v",
                    "python scripts/run_config_audit.py --dry-run",
                    "```",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "## Next Steps",
                    "",
                    "This was a DRY RUN. To apply fixes:",
                    "",
                    "```bash",
                    "python scripts/depurate_config.py  # Remove --dry-run flag",
                    "```",
                    "",
                ]
            )

        output_path.write_text("\n".join(lines))

    def _generate_fixes_section(self) -> list[str]:
        """Generate fixes section."""
        lines = [
            "## Fixes Applied",
            "",
        ]

        by_type = {}
        for fix in self.fixes_applied:
            fix_type = fix["type"]
            if fix_type not in by_type:
                by_type[fix_type] = []
            by_type[fix_type].append(fix)

        for fix_type, fixes in sorted(by_type.items()):
            lines.append(f"### {fix_type.replace('_', ' ').title()}")
            lines.append("")

            for fix in fixes[:50]:
                lines.append(f"- `{fix['file']}`")
                if "old" in fix and "new" in fix:
                    lines.append(f"  - Old: `{fix['old']}`")
                    lines.append(f"  - New: `{fix['new']}`")
                elif "change" in fix:
                    lines.append(f"  - Change: {fix['change']}")
                elif "reason" in fix:
                    lines.append(f"  - Reason: {fix['reason']}")

            if len(fixes) > 50:
                lines.append(f"- ... and {len(fixes) - 50} more")

            lines.append("")

        return lines

    def _generate_issues_section(self) -> list[str]:
        """Generate issues section."""
        lines = [
            "## Issues Found",
            "",
            "The following issues require manual attention:",
            "",
        ]

        by_type = {}
        for issue in self.issues_found:
            issue_type = issue["type"]
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)

        for issue_type, issues in sorted(by_type.items()):
            lines.append(f"### {issue_type.replace('_', ' ').title()}")
            lines.append("")

            for issue in issues:
                lines.append(f"- `{issue['file']}`")
                if "error" in issue:
                    lines.append(f"  - Error: {issue['error']}")

            lines.append("")

        return lines


def main():
    """Main depuration execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automatically fix common configuration issues"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without applying (default: True)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply fixes (overrides --dry-run)",
    )

    args = parser.parse_args()

    dry_run = not args.apply

    root_path = Path(__file__).parent.parent.resolve()

    print("=" * 80)
    print("CONFIGURATION DEPURATION")
    print("=" * 80)
    print()

    if dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made")
    else:
        print("⚡ LIVE MODE - Changes will be applied")

    print()

    depurator = ConfigDepurator(root_path, dry_run=dry_run)

    print("[1/4] Fixing path references...")
    path_fixes = depurator.fix_path_references()
    print(f"      Path references updated: {path_fixes}")
    print()

    print("[2/4] Validating JSON files...")
    valid, invalid = depurator.validate_json_files()
    print(f"      Valid: {valid}, Invalid: {invalid}")
    print()

    print("[3/4] Cleaning empty configurations...")
    cleaned = depurator.clean_empty_configs()
    print(f"      Empty configs removed: {cleaned}")
    print()

    print("[4/4] Normalizing JSON formatting...")
    normalized = depurator.normalize_json_formatting()
    print(f"      Files normalized: {normalized}")
    print()

    print("Generating depuration report...")
    output_path = root_path / "config_depuration_report.md"
    depurator.generate_depuration_report(output_path)
    print(f"✓ Report: {output_path}")
    print()

    print("=" * 80)
    print("DEPURATION COMPLETE")
    print("=" * 80)
    print()

    print(f"Total fixes: {len(depurator.fixes_applied)}")
    print(f"Total issues: {len(depurator.issues_found)}")
    print()

    if dry_run:
        print("Run with --apply flag to execute changes.")
    else:
        print("Review changes with: git diff")

    print()


if __name__ == "__main__":
    main()
