#!/usr/bin/env python3
"""
SISAS Migration Script

Validates that codebase is ready for deprecated orchestrator removal.

Usage:
    python scripts/sisas_migration/migrate_orchestrators.py --check
    python scripts/sisas_migration/migrate_orchestrators.py --fix
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

DEPRECATED_IMPORTS = [
    ("extractor_orchestrator", "ExtractorOrchestrator"),
    ("async_orchestrator", "AsyncEnrichmentOrchestrator"),
    ("enrichment_orchestrator", "EnrichmentOrchestrator"),
    ("sisas_orchestrator", "SISASOrchestrator"),
]

REPLACEMENT = "from farfan_pipeline.orchestration import UnifiedOrchestrator"


def find_deprecated_imports(root: Path) -> List[Tuple[Path, str, int]]:
    """Find all files using deprecated imports."""
    findings = []

    for py_file in root.rglob("*.py"):
        if "backup" in str(py_file).lower():
            continue
        if "__pycache__" in str(py_file):
            continue
        # Skip the deprecated files themselves
        if any(dep[0] in str(py_file) for dep in DEPRECATED_IMPORTS):
            continue
        # Skip this migration script
        if "migrate_orchestrators" in str(py_file):
            continue

        try:
            content = py_file.read_text(errors="ignore")
        except Exception:
            continue

        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            for module, class_name in DEPRECATED_IMPORTS:
                if module in line and "import" in line:
                    # Skip lines that are just comments or docstrings
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                        continue
                    findings.append((py_file, line.strip(), i))

    return findings


def main():
    parser = argparse.ArgumentParser(description="SISAS Migration Validator")
    parser.add_argument("--check", action="store_true", help="Check for deprecated imports")
    parser.add_argument("--fix", action="store_true", help="Show fix suggestions")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]

    if args.check or args.fix:
        findings = find_deprecated_imports(root)

        if findings:
            print(f"Found {len(findings)} deprecated import(s):\n")
            for path, line, lineno in findings:
                print(f"  {path}:{lineno}")
                print(f"    {line}")
                if args.fix:
                    print(f"    → Replace with: {REPLACEMENT}")
                print()
            sys.exit(1)
        else:
            print("✓ No deprecated imports found. Ready for cleanup.")
            sys.exit(0)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
