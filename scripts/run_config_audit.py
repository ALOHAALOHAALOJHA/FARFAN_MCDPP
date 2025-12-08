#!/usr/bin/env python3
"""
Master Configuration Audit Orchestrator

Runs complete configuration audit pipeline:
1. AST parser audit for hardcoded values
2. Duplicate configuration detection
3. Legacy file archival
4. Consolidation to canonical structure
5. Reference validation
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


class AuditOrchestrator:
    """Orchestrates complete configuration audit pipeline."""

    def __init__(self, root_path: Path, dry_run: bool = False):
        self.root_path = root_path
        self.dry_run = dry_run
        self.scripts_dir = root_path / "scripts"
        self.results = []

    def run_step(self, step_name: str, script_name: str, args: list = None) -> bool:
        """Run a single audit step."""
        print("=" * 80)
        print(f"STEP: {step_name}")
        print("=" * 80)
        print()

        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            self.results.append(
                {
                    "step": step_name,
                    "status": "ERROR",
                    "message": "Script not found",
                }
            )
            return False

        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)

        try:
            result = subprocess.run(
                cmd,
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )

            print(result.stdout)

            if result.stderr:
                print("STDERR:", result.stderr, file=sys.stderr)

            if result.returncode == 0:
                print(f"✓ {step_name} completed successfully")
                self.results.append(
                    {
                        "step": step_name,
                        "status": "SUCCESS",
                        "message": "Completed",
                    }
                )
                return True
            else:
                print(f"❌ {step_name} failed with exit code {result.returncode}")
                self.results.append(
                    {
                        "step": step_name,
                        "status": "FAILED",
                        "message": f"Exit code {result.returncode}",
                    }
                )
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ {step_name} timed out")
            self.results.append(
                {
                    "step": step_name,
                    "status": "TIMEOUT",
                    "message": "Execution timeout",
                }
            )
            return False

        except Exception as e:
            print(f"❌ {step_name} error: {str(e)}")
            self.results.append(
                {
                    "step": step_name,
                    "status": "ERROR",
                    "message": str(e),
                }
            )
            return False

        finally:
            print()

    def run_full_audit(self) -> bool:
        """Run complete audit pipeline."""
        print("=" * 80)
        print("CONFIGURATION AUDIT PIPELINE")
        print(f"Started: {datetime.now().isoformat()}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("=" * 80)
        print()

        steps = [
            (
                "Hardcoded Value Detection",
                "audit_calibration_config.py",
                [],
            ),
            (
                "Configuration Consolidation",
                "consolidate_config.py",
                ["--dry-run"] if self.dry_run else [],
            ),
            (
                "Reference Validation",
                "validate_config_references.py",
                [],
            ),
        ]

        success_count = 0
        for step_name, script_name, args in steps:
            if self.run_step(step_name, script_name, args):
                success_count += 1

        return success_count == len(steps)

    def generate_summary(self, output_path: Path) -> None:
        """Generate audit summary report."""
        lines = [
            "# Configuration Audit Summary",
            "",
            f"Generated: {datetime.now().isoformat()}",
            f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}",
            "",
            "## Audit Steps",
            "",
        ]

        for result in self.results:
            status_emoji = {
                "SUCCESS": "✓",
                "FAILED": "❌",
                "ERROR": "❌",
                "TIMEOUT": "⏱️",
            }
            emoji = status_emoji.get(result["status"], "•")

            lines.append(
                f"- {emoji} **{result['step']}**: {result['status']} - {result['message']}"
            )

        lines.append("")

        success_count = sum(1 for r in self.results if r["status"] == "SUCCESS")
        total_count = len(self.results)

        lines.extend(
            [
                "## Overall Status",
                "",
                f"**{success_count}/{total_count}** steps completed successfully",
                "",
            ]
        )

        if success_count == total_count:
            lines.extend(
                [
                    "✓ **All audit steps completed successfully**",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "⚠️ **Some audit steps failed - review individual reports**",
                    "",
                ]
            )

        lines.extend(
            [
                "## Generated Reports",
                "",
                "Review the following reports for detailed findings:",
                "",
                "1. **violations_audit.md** - Hardcoded calibration values detected",
                "2. **config_consolidation_report.md** - Configuration file consolidation",
                "3. **config_reference_validation.md** - Code reference validation",
                "",
                "## Next Steps",
                "",
            ]
        )

        if self.dry_run:
            lines.extend(
                [
                    "1. Review all generated reports",
                    "2. Run audit without `--dry-run` flag to perform consolidation",
                    "3. Update code references to use canonical paths",
                    "4. Validate changes with integration tests",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "1. Review violations_audit.md and refactor hardcoded values",
                    "2. Update code to reference system/config/ paths",
                    "3. Verify configuration loading with tests",
                    "4. Clean up archived files after validation period",
                    "",
                ]
            )

        lines.extend(
            [
                "## Canonical Configuration Structure",
                "",
                "```",
                "system/config/",
                "├── calibration/",
                "│   ├── intrinsic_calibration.json       # PRIMARY source of truth",
                "│   ├── intrinsic_calibration_rubric.json # Scoring methodology",
                "│   ├── runtime_layers.json               # Layer definitions",
                "│   └── unit_transforms.json              # Unit transforms",
                "├── questionnaire/                        # Questionnaire configs",
                "└── executor_config.json                  # Executor settings",
                "```",
                "",
            ]
        )

        output_path.write_text("\n".join(lines))


def main():
    """Main orchestration entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run complete configuration audit pipeline"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actual changes)",
    )

    args = parser.parse_args()

    root_path = Path(__file__).parent.parent.resolve()

    orchestrator = AuditOrchestrator(root_path, dry_run=args.dry_run)

    success = orchestrator.run_full_audit()

    print("=" * 80)
    print("GENERATING SUMMARY REPORT")
    print("=" * 80)
    print()

    summary_path = root_path / "config_audit_summary.md"
    orchestrator.generate_summary(summary_path)

    print(f"✓ Summary report: {summary_path}")
    print()

    print("=" * 80)
    print("AUDIT PIPELINE COMPLETE")
    print("=" * 80)
    print()

    if success:
        print("✓ All audit steps completed successfully")
        sys.exit(0)
    else:
        print("⚠️  Some audit steps failed - review reports")
        sys.exit(1)


if __name__ == "__main__":
    main()
