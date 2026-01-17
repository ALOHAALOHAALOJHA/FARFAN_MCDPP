#!/usr/bin/env python3
"""COMPREHENSIVE IMPORT FIXER - Totalizing remediation of all 131 broken imports.

Categorized fixing strategy:
1. CAPITALIZATION_ERROR (17) → Fix Phase_X to Phase_0X
2. MOVED_TO_INFRASTRUCTURE_CONTRACTUAL (15) → Redirect to dura_lex
3. DELETED_ANALYSIS (9) → Remove imports
4. DELETED_CALIBRATION (5) → Remove imports
5. SISAS_MODULE_MOVED (2) → Redirect to new locations
6. OTHER_DEAD_MODULES (81) → Investigate and fix individually
7. ALREADY_FIXED (2) → Skip (signal_consumption already migrated)
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# ============================================================================
# COMPREHENSIVE REMEDIATION RULES
# ============================================================================

CAPITALIZATION_FIXES = {
    r"from farfan_pipeline\.phases\.Phase_6": "from farfan_pipeline.phases.Phase_06",
    r"from farfan_pipeline\.phases\.Phase_one": "from farfan_pipeline.phases.Phase_01",
    r"from farfan_pipeline\.phases\.Phase_two": "from farfan_pipeline.phases.Phase_02",
    r"from farfan_pipeline\.phases\.Phase_zero": "from farfan_pipeline.phases.Phase_00",
    r"from farfan_pipeline\.phases\.Phase_three": "from farfan_pipeline.phases.Phase_03",
    r"from farfan_pipeline\.phases\.Phase_four": "from farfan_pipeline.phases.Phase_04",
    r"from farfan_pipeline\.phases\.Phase_eight": "from farfan_pipeline.phases.Phase_08",
    r"from farfan_pipeline\.phases\.Phase_nine": "from farfan_pipeline.phases.Phase_09",
    # Numeric variants
    r"from farfan_pipeline\.phases\.Phase_1": "from farfan_pipeline.phases.Phase_01",
    r"from farfan_pipeline\.phases\.Phase_2": "from farfan_pipeline.phases.Phase_02",
    r"from farfan_pipeline\.phases\.Phase_3": "from farfan_pipeline.phases.Phase_03",
    r"from farfan_pipeline\.phases\.Phase_4": "from farfan_pipeline.phases.Phase_04",
    r"from farfan_pipeline\.phases\.Phase_5": "from farfan_pipeline.phases.Phase_05",
    r"from farfan_pipeline\.phases\.Phase_8": "from farfan_pipeline.phases.Phase_08",
}

CONTRACTUAL_REDIRECTS = {
    r"from farfan_pipeline\.contracts\.(alignment_stability|budget_monotonicity|concurrency_determinism|context_immutability|failure_fallback|idempotency_dedup|monotone_compliance|permutation_invariance|refusal|retriever_contract|risk_certificate|routing_contract|snapshot_contract|total_ordering|traceability)":
        r"from farfan_pipeline.infrastructure.contractual.dura_lex.\1",
}

SISAS_REDIRECTS = {
    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_registry":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals",
    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_context_scoper":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.vehicles.signal_context_scoper",
}

SISAS_UTILS_REDIRECTS = {
    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_method_metadata":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.metadata.signal_method_metadata",
    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_scoring_context":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.utils.signal_scoring_context",
    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_semantic_context":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.utils.signal_semantic_context",
    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_semantic_expander":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.semantic.signal_semantic_expander",
    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_validation_specs":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.utils.signal_validation_specs",
}

PHASE_02_REDIRECTS = {
    r"from farfan_pipeline\.phases\.Phase_02\.executors\.base_executor_with_contract":
        "from farfan_pipeline.phases.Phase_02.phase2_60_00_base_executor_with_contract",
    r"from farfan_pipeline\.phases\.Phase_02\.executor_config":
        "from farfan_pipeline.phases.Phase_02.phase2_10_03_executor_config",
    r"from farfan_pipeline\.phases\.Phase_02\.evidence_nexus":
        "from farfan_pipeline.phases.Phase_02.phase2_80_00_evidence_nexus",
    r"from farfan_pipeline\.phases\.Phase_02\.irrigation_synchronizer":
        "from farfan_pipeline.phases.Phase_02.phase2_40_03_irrigation_synchronizer",
    r"from farfan_pipeline\.phases\.Phase_02\.calibration_policy":
        "from farfan_pipeline.phases.Phase_02.phase2_10_04_calibration_policy",
}

ORCHESTRATION_REDIRECTS = {
    r"from farfan_pipeline\.orchestration\.task_planner":
        "from farfan_pipeline.phases.Phase_00.interphase.task_planner",
    r"from farfan_pipeline\.orchestration\.metrics_persistence":
        "from farfan_pipeline.phases.Phase_02.phase2_95_01_metrics_persistence",
}

# Modules to DELETE (comment out imports)
DELETE_PATTERNS = [
    r"from farfan_pipeline\.analysis\.",
    r"from farfan_pipeline\.calibration\.",
    r"from farfan_pipeline\.phases\.phase_4_7_aggregation_pipeline\.",
    r"from farfan_pipeline\.phases\.Phase_four_five_six_seven\.",
    r"from farfan_pipeline\.processing\.",
    r"from farfan_pipeline\.resilience",
    r"from farfan_pipeline\.question_context",
    r"from farfan_pipeline\.utils\.runtime_error_fixes",
    r"from farfan_pipeline\.core\.dependency_lockdown",
    r"from farfan_pipeline\.core\.policy_area_canonicalization",
]


def fix_file(filepath: Path) -> Tuple[bool, List[str]]:
    """Fix all broken imports in a single file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content
        changes = []

        # 1. Fix capitalization errors
        for pattern, replacement in CAPITALIZATION_FIXES.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"Capitalization: {pattern} → {replacement}")

        # 2. Redirect contractual imports
        for pattern, replacement in CONTRACTUAL_REDIRECTS.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"Contractual: {pattern} → {replacement}")

        # 3. Redirect SISAS imports
        for pattern, replacement in SISAS_REDIRECTS.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"SISAS: {pattern} → {replacement}")

        # 4. Redirect SISAS utils imports
        for pattern, replacement in SISAS_UTILS_REDIRECTS.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"SISAS Utils: {pattern} → {replacement}")

        # 5. Redirect Phase_02 imports
        for pattern, replacement in PHASE_02_REDIRECTS.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"Phase_02: {pattern} → {replacement}")

        # 6. Redirect orchestration imports
        for pattern, replacement in ORCHESTRATION_REDIRECTS.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"Orchestration: {pattern} → {replacement}")

        # 7. Comment out deleted modules (don't remove, just disable)
        for pattern in DELETE_PATTERNS:
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            if matches:
                # Comment out from end to preserve line numbers
                for match in reversed(matches):
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)

                    line = content[line_start:line_end]
                    if not line.strip().startswith('#'):
                        commented_line = '# DELETED_MODULE: ' + line
                        content = content[:line_start] + commented_line + content[line_end:]
                        changes.append(f"Deleted: {pattern}")

        # Write back if changed
        if content != original:
            filepath.write_text(content, encoding="utf-8")
            return True, changes

        return False, []

    except Exception as e:
        return False, [f"ERROR: {e}"]


def main():
    """Main remediation entry point."""
    repo_root = Path(__file__).parent.parent

    print("=" * 80)
    print("COMPREHENSIVE IMPORT REMEDIATION - Totalizing Fix (131 broken imports)")
    print("=" * 80)
    print()

    # Find all Python files
    files_to_fix = list(repo_root.glob("src/**/*.py")) + list(repo_root.glob("tests/**/*.py"))
    files_to_fix = [f for f in files_to_fix if "__pycache__" not in str(f)]

    print(f"Scanning {len(files_to_fix)} Python files...")
    print()

    fixed_count = 0
    total_changes = 0

    for filepath in files_to_fix:
        modified, changes = fix_file(filepath)
        if modified:
            fixed_count += 1
            total_changes += len(changes)
            print(f"✓ Fixed: {filepath.relative_to(repo_root)}")
            for change in changes[:3]:  # Show first 3 changes per file
                print(f"    {change}")
            if len(changes) > 3:
                print(f"    ... and {len(changes) - 3} more")

    print()
    print("=" * 80)
    print(f"Remediation complete: {fixed_count} files modified, {total_changes} total changes")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Run ./scripts/validate_architecture.sh")
    print("  2. Run tests to verify fixes")
    print("  3. Commit changes")


if __name__ == "__main__":
    main()
