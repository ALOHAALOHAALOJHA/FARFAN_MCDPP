#!/usr/bin/env python3
"""Path Repair Utility for F.A.R. F.A.N

This script provides automated repair capabilities for common path issues.

Usage:
    python scripts/audit/path_repair.py --check           # Dry run
    python scripts/audit/path_repair.py --fix             # Apply fixes
    python scripts/audit/path_repair.py --fix --backup    # Apply fixes with backup

Repairs:
- Converts deprecated imports (canonic_phases -> farfan_pipeline)
- Suggests fixes for hardcoded paths (manual review required)
- Removes unnecessary sys.path manipulations (with caution)
"""

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List


class PathRepairer:
    """Automated repair utility for path-related issues."""

    # Import replacement patterns
    IMPORT_REPLACEMENTS = {
        r'from canonic_phases\.Phase_zero\.paths import':
            'from farfan_pipeline.utils.paths import',

        r'from canonic_phases\.Phase_zero import paths':
            'from farfan_pipeline.utils import paths',

        r'from src\.farfan_pipeline':
            'from farfan_pipeline',

        r'import canonic_phases\.':
            'import farfan_pipeline.phases.',

        r'from canonic_phases\.':
            'from farfan_pipeline.phases.',
    }

    def __init__(self, root: Path, dry_run: bool = True, backup: bool = False, verbose: bool = False):
        self.root = root
        self.dry_run = dry_run
        self.backup = backup
        self.verbose = verbose
        self.changes: List[Dict[str, any]] = []

    def repair_imports(self, py_file: Path) -> int:
        """Repair deprecated imports in a file."""
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not read {py_file}: {e}")
            return 0

        original_content = content
        changes_made = 0

        # Apply each replacement pattern
        for old_pattern, new_pattern in self.IMPORT_REPLACEMENTS.items():
            new_content, count = re.subn(old_pattern, new_pattern, content)
            if count > 0:
                changes_made += count
                content = new_content

                self.changes.append({
                    "file": str(py_file.relative_to(self.root)),
                    "type": "import_fix",
                    "pattern": old_pattern,
                    "replacement": new_pattern,
                    "occurrences": count
                })

        # Apply changes if not dry run
        if changes_made > 0 and not self.dry_run:
            # Backup if requested
            if self.backup:
                backup_path = py_file.with_suffix(py_file.suffix + ".bak")
                shutil.copy2(py_file, backup_path)
                if self.verbose:
                    print(f"  Created backup: {backup_path}")

            py_file.write_text(content, encoding="utf-8")

        return changes_made

    def analyze_hardcoded_paths(self, py_file: Path) -> List[Dict[str, any]]:
        """Analyze hardcoded paths and suggest fixes (manual review required)."""
        suggestions = []

        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return suggestions

        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Look for common hardcoded path patterns
            unix_match = re.search(r'Path\(["\']/(Users|home)/([^/]+)/FARFAN_MPP["\']', line)
            if unix_match:
                suggestions.append({
                    "file": str(py_file.relative_to(self.root)),
                    "line": i,
                    "type": "hardcoded_path",
                    "original": line.strip(),
                    "suggestion": "Replace with: from farfan_pipeline.utils.paths import PROJECT_ROOT"
                })

        return suggestions

    def repair_directory(self) -> None:
        """Repair all Python files in the directory tree."""
        total_files = 0
        files_modified = 0

        for py_file in self.root.rglob("*.py"):
            # Skip virtual environments and cache directories
            if any(part in py_file.parts for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]):
                continue

            # Skip backup files
            if py_file.suffix == ".bak":
                continue

            total_files += 1

            if self.verbose:
                print(f"Processing: {py_file.relative_to(self.root)}")

            # Repair imports
            changes = self.repair_imports(py_file)
            if changes > 0:
                files_modified += 1
                print(f"  {'[DRY RUN] Would fix' if self.dry_run else 'Fixed'} {changes} import(s) in {py_file.relative_to(self.root)}")

            # Analyze hardcoded paths (suggestions only)
            suggestions = self.analyze_hardcoded_paths(py_file)
            for suggestion in suggestions:
                self.changes.append(suggestion)

        print(f"\nProcessed {total_files} files")
        if self.dry_run:
            print(f"Would modify {files_modified} files")
        else:
            print(f"Modified {files_modified} files")

    def print_report(self) -> None:
        """Print a report of all changes and suggestions."""
        if not self.changes:
            print("\n✅ No repairs needed")
            return

        # Separate by type
        fixes = [c for c in self.changes if c.get("type") == "import_fix"]
        suggestions = [c for c in self.changes if c.get("type") == "hardcoded_path"]

        if fixes:
            print("\n" + "=" * 80)
            print(f"📝 IMPORT FIXES {'(DRY RUN)' if self.dry_run else '(APPLIED)'}")
            print("=" * 80)

            # Group by file
            by_file: Dict[str, List] = {}
            for fix in fixes:
                file = fix["file"]
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(fix)

            for file, file_fixes in sorted(by_file.items()):
                total_changes = sum(f["occurrences"] for f in file_fixes)
                print(f"\n{file} ({total_changes} changes)")
                for fix in file_fixes:
                    print(f"  {fix['pattern']} → {fix['replacement']} ({fix['occurrences']}x)")

        if suggestions:
            print("\n" + "=" * 80)
            print("💡 MANUAL REVIEW REQUIRED - Hardcoded Paths")
            print("=" * 80)

            for suggestion in suggestions:
                print(f"\n{suggestion['file']}:{suggestion['line']}")
                print(f"  Original: {suggestion['original']}")
                print(f"  {suggestion['suggestion']}")

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about repairs."""
        stats = {
            "total_changes": len(self.changes),
            "import_fixes": len([c for c in self.changes if c.get("type") == "import_fix"]),
            "hardcoded_paths": len([c for c in self.changes if c.get("type") == "hardcoded_path"]),
        }
        return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated repair utility for path-related issues"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply fixes (default is dry-run)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create .bak files before modifying"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Root directory to repair (default: auto-detect project root)"
    )

    args = parser.parse_args()

    # Detect project root
    if args.root:
        root = args.root.resolve()
    else:
        # Auto-detect: go up from script location to find pyproject.toml
        script_dir = Path(__file__).resolve().parent
        root = script_dir.parent.parent

        # Verify we found the right root
        if not (root / "pyproject.toml").exists():
            print("Error: Could not find project root (no pyproject.toml)")
            sys.exit(1)

    dry_run = not args.fix

    if dry_run:
        print("=" * 80)
        print("DRY RUN MODE - No changes will be applied")
        print("Use --fix to apply changes")
        print("=" * 80 + "\n")
    else:
        print("=" * 80)
        print("REPAIR MODE - Changes will be applied")
        if args.backup:
            print("Backup files will be created (.bak)")
        print("=" * 80 + "\n")

    if args.verbose:
        print(f"Processing directory: {root}\n")

    repairer = PathRepairer(root, dry_run=dry_run, backup=args.backup, verbose=args.verbose)
    repairer.repair_directory()
    repairer.print_report()

    stats = repairer.get_statistics()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total changes identified: {stats['total_changes']}")
    print(f"  Import fixes: {stats['import_fixes']}")
    print(f"  Hardcoded paths (manual review): {stats['hardcoded_paths']}")

    if dry_run and stats['import_fixes'] > 0:
        print("\nRun with --fix to apply import fixes")

    if stats['hardcoded_paths'] > 0:
        print("\n⚠️  Some issues require manual review and cannot be fixed automatically")


if __name__ == "__main__":
    main()
