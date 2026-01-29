#!/usr/bin/env python3
"""
Update Import References for CONSTANTS Files.

Updates all imports from duplicate PHASE_N_CONSTANTS to canonical
phaseN_10_00_phase_n_constants naming pattern.

Document: FPN-GNEA-009
Version: 1.0.0
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def update_constants_imports(repo_root: Path) -> dict[str, list[str]]:
    """Update all import references from duplicate CONSTANTS to canonical.

    Args:
        repo_root: Path to repository root

    Returns:
        Dictionary with updated files and any errors encountered
    """
    src_dir = repo_root / "src"
    cqc_dir = repo_root / "canonic_questionnaire_central"

    # Import mappings for different phases
    import_mappings = [
        # Phase 0
        (
            r"from\s+farfan_pipeline\.phases\.Phase_00\.PHASE_0_CONSTANTS\s+import",
            "from farfan_pipeline.phases.Phase_00.phase0_10_00_phase_0_constants import"
        ),
        (
            r"from\s+\.PHASE_0_CONSTANTS\s+import",
            "from .phase0_10_00_phase_0_constants import"
        ),
        (
            r"import\s+farfan_pipeline\.phases\.Phase_00\.PHASE_0_CONSTANTS",
            "import farfan_pipeline.phases.Phase_00.phase0_10_00_phase_0_constants"
        ),
        # Phase 1
        (
            r"from\s+farfan_pipeline\.phases\.Phase_01\.PHASE_1_CONSTANTS\s+import",
            "from farfan_pipeline.phases.Phase_01.phase1_10_00_phase_1_constants import"
        ),
        (
            r"from\s+\.PHASE_1_CONSTANTS\s+import",
            "from .phase1_10_00_phase_1_constants import"
        ),
        (
            r"import\s+farfan_pipeline\.phases\.Phase_01\.PHASE_1_CONSTANTS",
            "import farfan_pipeline.phases.Phase_01.phase1_10_00_phase_1_constants"
        ),
        # Phase 2
        (
            r"from\s+farfan_pipeline\.phases\.Phase_02\.PHASE_2_CONSTANTS\s+import",
            "from farfan_pipeline.phases.Phase_02.phase2_10_00_phase_2_constants import"
        ),
        (
            r"from\s+\.PHASE_2_CONSTANTS\s+import",
            "from .phase2_10_00_phase_2_constants import"
        ),
        (
            r"import\s+farfan_pipeline\.phases\.Phase_02\.PHASE_2_CONSTANTS",
            "import farfan_pipeline.phases.Phase_02.phase2_10_00_phase_2_constants"
        ),
        # Phase 4-7
        (
            r"from\s+farfan_pipeline\.phases\.Phase_04\.PHASE_4_7_CONSTANTS\s+import",
            "from farfan_pipeline.phases.Phase_04.phase4_10_00_phase_4_7_constants import"
        ),
        (
            r"from\s+\.\.PHASE_4_7_CONSTANTS\s+import",
            "from ..phase4_10_00_phase_4_7_constants import"
        ),
        (
            r"from\s+\.PHASE_4_7_CONSTANTS\s+import",
            "from .phase4_10_00_phase_4_7_constants import"
        ),
        (
            r"import\s+farfan_pipeline\.phases\.Phase_04\.PHASE_4_7_CONSTANTS",
            "import farfan_pipeline.phases.Phase_04.phase4_10_00_phase_4_7_constants"
        ),
        # Phase 9
        (
            r"from\s+farfan_pipeline\.phases\.Phase_09\.PHASE_9_CONSTANTS\s+import",
            "from farfan_pipeline.phases.Phase_09.phase9_10_00_phase_9_constants import"
        ),
        (
            r"from\s+\.PHASE_9_CONSTANTS\s+import",
            "from .phase9_10_00_phase_9_constants import"
        ),
        (
            r"import\s+farfan_pipeline\.phases\.Phase_09\.PHASE_9_CONSTANTS",
            "import farfan_pipeline.phases.Phase_09.phase9_10_00_phase_9_constants"
        ),
    ]

    results = {
        "updated": [],
        "errors": []
    }

    # Search directories
    search_dirs = [src_dir, cqc_dir]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        for py_file in search_dir.rglob("*.py"):
            # Skip __pycache__ and the CONSTANTS files themselves
            if "__pycache__" in str(py_file):
                continue
            if py_file.name in ("PHASE_0_CONSTANTS.py", "PHASE_1_CONSTANTS.py",
                               "PHASE_2_CONSTANTS.py", "PHASE_4_7_CONSTANTS.py",
                               "PHASE_9_CONSTANTS.py"):
                continue

            try:
                content = py_file.read_text()
                original_content = content

                # Apply all import mappings
                for old_pattern, new_import in import_mappings:
                    content = re.sub(old_pattern, new_import, content)

                # Only write if content changed
                if content != original_content:
                    py_file.write_text(content)
                    results["updated"].append(str(py_file.relative_to(repo_root)))
                    print(f"✓ Updated: {py_file.relative_to(repo_root)}")

            except Exception as e:
                results["errors"].append(f"{py_file}: {e}")
                print(f"✗ Error updating {py_file}: {e}")

    return results


def main():
    """CLI entry point."""
    repo_root = Path.cwd()
    print("Updating CONSTANTS import references...")
    print(f"Repository root: {repo_root}")
    print()

    results = update_constants_imports(repo_root)

    print()
    print(f"Updated {len(results['updated'])} files")
    if results["errors"]:
        print(f"Errors: {len(results['errors'])}")
        for error in results["errors"]:
            print(f"  {error}")

    return 0 if not results["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
