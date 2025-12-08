#!/usr/bin/env python3
"""
Configuration Consolidation Script

Consolidates configuration files to single source of truth in system/config/.
Ensures canonical hierarchy and removes duplicates after validation.
"""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path


class ConfigConsolidator:
    """Consolidates configuration files to canonical locations."""

    def __init__(self, root_path: Path, dry_run: bool = False):
        self.root_path = root_path
        self.dry_run = dry_run
        self.canonical_base = root_path / "system" / "config"
        self.actions: list[dict[str, str]] = []

    def ensure_canonical_structure(self) -> None:
        """Ensure canonical directory structure exists."""
        directories = [
            self.canonical_base / "calibration",
            self.canonical_base / "questionnaire",
        ]

        for directory in directories:
            if not self.dry_run:
                directory.mkdir(parents=True, exist_ok=True)
            self.log_action("CREATE_DIR", str(directory), "")

    def get_canonical_mapping(self) -> dict[str, str]:
        """Define canonical file mappings."""
        return {
            "config/intrinsic_calibration.json": "system/config/calibration/intrinsic_calibration.json",
            "src/farfan_pipeline/core/calibration/intrinsic_calibration_rubric.json": "system/config/calibration/intrinsic_calibration_rubric.json",
            "config/json_files_ no_schemas/executor_config.json": "system/config/executor_config.json",
        }

    def consolidate_files(self) -> tuple[int, int]:
        """Consolidate configuration files to canonical locations."""
        mapping = self.get_canonical_mapping()
        consolidated = 0
        skipped = 0

        for source_rel, target_rel in mapping.items():
            source = self.root_path / source_rel
            target = self.root_path / target_rel

            if not source.exists():
                self.log_action("SKIP", source_rel, "Source file does not exist")
                skipped += 1
                continue

            if target.exists():
                if self._files_identical(source, target):
                    self.log_action(
                        "SKIP", source_rel, "Target already exists and is identical"
                    )
                    skipped += 1
                    continue
                else:
                    self.log_action(
                        "CONFLICT",
                        source_rel,
                        f"Target exists but differs: {target_rel}",
                    )
                    skipped += 1
                    continue

            if not self.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

            self.log_action("CONSOLIDATE", source_rel, target_rel)
            consolidated += 1

        return consolidated, skipped

    def validate_canonical_files(self) -> list[dict[str, str]]:
        """Validate that canonical files are valid JSON/YAML."""
        issues = []
        canonical_files = [
            "system/config/calibration/intrinsic_calibration.json",
            "system/config/calibration/intrinsic_calibration_rubric.json",
            "system/config/calibration/runtime_layers.json",
            "system/config/calibration/unit_transforms.json",
        ]

        for file_rel in canonical_files:
            filepath = self.root_path / file_rel

            if not filepath.exists():
                issues.append(
                    {
                        "file": file_rel,
                        "issue": "Missing",
                        "severity": "WARNING",
                    }
                )
                continue

            try:
                with open(filepath) as f:
                    if filepath.suffix == ".json":
                        json.load(f)
                    else:
                        pass

                issues.append(
                    {
                        "file": file_rel,
                        "issue": "Valid",
                        "severity": "INFO",
                    }
                )
            except json.JSONDecodeError as e:
                issues.append(
                    {
                        "file": file_rel,
                        "issue": f"Invalid JSON: {str(e)}",
                        "severity": "ERROR",
                    }
                )
            except Exception as e:
                issues.append(
                    {
                        "file": file_rel,
                        "issue": f"Error reading: {str(e)}",
                        "severity": "ERROR",
                    }
                )

        return issues

    def generate_consolidation_report(self, output_path: Path) -> None:
        """Generate consolidation report."""
        lines = [
            "# Configuration Consolidation Report",
            "",
            f"Generated: {datetime.now().isoformat()}",
            f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}",
            "",
            "## Actions Performed",
            "",
        ]

        by_action = {}
        for action in self.actions:
            action_type = action["type"]
            if action_type not in by_action:
                by_action[action_type] = []
            by_action[action_type].append(action)

        for action_type, actions in sorted(by_action.items()):
            lines.append(f"### {action_type}")
            lines.append("")

            for action in actions:
                lines.append(f"- **Source**: `{action['source']}`")
                if action["target"]:
                    lines.append(f"  - **Target**: `{action['target']}`")
                lines.append("")

        issues = self.validate_canonical_files()

        lines.extend(
            [
                "## Canonical Files Validation",
                "",
            ]
        )

        for issue in issues:
            severity_emoji = {
                "INFO": "✓",
                "WARNING": "⚠️",
                "ERROR": "❌",
            }
            emoji = severity_emoji.get(issue["severity"], "•")

            lines.append(
                f"- {emoji} `{issue['file']}`: {issue['issue']} ({issue['severity']})"
            )

        lines.append("")

        lines.extend(
            [
                "## Canonical Configuration Hierarchy",
                "",
                "```",
                "system/config/",
                "├── calibration/",
                "│   ├── intrinsic_calibration.json       # PRIMARY: Method calibration scores",
                "│   ├── intrinsic_calibration_rubric.json # Scoring rubric and methodology",
                "│   ├── runtime_layers.json               # Layer maturity baselines",
                "│   └── unit_transforms.json              # Unit transformation rules",
                "├── questionnaire/                        # Questionnaire configurations",
                "│   └── (questionnaire configs)",
                "└── executor_config.json                  # Executor runtime configuration",
                "```",
                "",
                "## Next Steps",
                "",
            ]
        )

        if not self.dry_run:
            lines.extend(
                [
                    "1. Verify all systems reference `system/config/` paths",
                    "2. Update import statements and config loaders",
                    "3. Run integration tests to validate configuration loading",
                    "4. After validation period, clean up archived legacy files",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "1. Review this DRY RUN report",
                    "2. Run script without `--dry-run` to perform actual consolidation",
                    "3. Follow post-consolidation steps above",
                    "",
                ]
            )

        output_path.write_text("\n".join(lines))

    def log_action(self, action_type: str, source: str, target: str) -> None:
        """Log an action."""
        self.actions.append(
            {
                "type": action_type,
                "source": source,
                "target": target,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def _files_identical(self, file1: Path, file2: Path) -> bool:
        """Check if two files have identical content."""
        try:
            hash1 = self._compute_hash(file1)
            hash2 = self._compute_hash(file2)
            return hash1 == hash2
        except Exception:
            return False

    def _compute_hash(self, filepath: Path) -> str:
        """Compute SHA256 hash of file."""
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()


def main():
    """Main consolidation execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Consolidate configuration files to canonical locations"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry run without making changes",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="config_consolidation_report.md",
        help="Output report path",
    )

    args = parser.parse_args()

    root_path = Path(__file__).parent.parent.resolve()

    print("=" * 80)
    print("CONFIGURATION CONSOLIDATION")
    print("=" * 80)
    print()

    if args.dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made")
        print()

    consolidator = ConfigConsolidator(root_path, dry_run=args.dry_run)

    print("[1/3] Ensuring canonical directory structure...")
    consolidator.ensure_canonical_structure()
    print("      ✓ Structure verified")
    print()

    print("[2/3] Consolidating configuration files...")
    consolidated, skipped = consolidator.consolidate_files()
    print(f"      ✓ Consolidated: {consolidated}")
    print(f"      ⊘ Skipped: {skipped}")
    print()

    print("[3/3] Generating consolidation report...")
    output_path = root_path / args.output
    consolidator.generate_consolidation_report(output_path)
    print(f"      ✓ Report generated: {output_path}")
    print()

    print("=" * 80)
    print("CONSOLIDATION COMPLETE")
    print("=" * 80)
    print()

    if args.dry_run:
        print("Run without --dry-run to perform actual consolidation.")
    else:
        print("Review the report and validate configuration loading.")

    print()


if __name__ == "__main__":
    main()
