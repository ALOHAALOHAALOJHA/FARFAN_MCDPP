#!/usr/bin/env python3
"""
Mechanical Test Import Remediation Script
Phase 5 Step 3: Rewrite tests to assert current architecture

This script mechanically replaces forbidden imports with canonical paths.
Per Phase 0: No compatibility shims, no placeholders - direct replacement only.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Canonical import mappings (from missing_concepts_resolution.md)
IMPORT_MAPPINGS = {
    # orchestration.orchestrator → core_orchestrator
    (
        r"from orchestration\.orchestrator import (.*)",
        r"from farfan_pipeline.orchestration.core_orchestrator import \1"
    ),

    # Individual class redirects (with specific paths per missing_concepts_resolution.md)
    # This pattern handles multi-line imports
}

# Specific class mappings (for precise replacement)
CLASS_MAPPINGS = {
    "MethodExecutor": "farfan_pipeline.orchestration.core_orchestrator",
    "Orchestrator": "farfan_pipeline.orchestration.core_orchestrator",
    "ScoredMicroQuestion": "farfan_pipeline.phases.Phase_03.contracts.phase03_output_contract",
    "MicroQuestionRun": "farfan_pipeline.phases.Phase_02.interphase.phase2_phase3_adapter",
    "ResourceLimits": "farfan_pipeline.phases.Phase_00.phase0_30_00_resource_controller",
    "QuestionnaireSignalRegistry": "farfan_pipeline.phases.Phase_02.registries.questionnaire_signal_registry",
    "Evidence": "Any  # Multiple Evidence classes exist - use typing.Any or specific Evidence* class",
    "PhaseInstrumentation": "# PHANTOM CLASS - not found in codebase (test needs rewrite)",
    "AbortSignal": "# PHANTOM CLASS - not found (check phase0_00_01_domain_errors if needed)",
}


def fix_orchestrator_imports(content: str, file_path: Path) -> Tuple[str, List[str]]:
    """
    Fix orchestration.orchestrator imports using canonical mappings.

    Returns:
        Tuple of (modified_content, list of changes made)
    """
    changes = []
    original = content

    # Pattern 1: Simple single-line imports
    # from orchestration.orchestrator import Foo, Bar
    pattern = r'from orchestration\.orchestrator import ([^\n]+)'

    def replace_import(match):
        imported_items = match.group(1).strip()

        # Handle multiline imports wrapped in parentheses
        if '(' in imported_items and ')' not in imported_items:
            return match.group(0)  # Skip for now, handle in multi-line pattern

        # Remove parentheses if present
        imported_items = imported_items.strip('()')

        # Split by comma
        items = [item.strip() for item in imported_items.split(',') if item.strip()]

        # Group items by their canonical module
        module_groups: Dict[str, List[str]] = {}
        phantom_items = []

        for item in items:
            # Remove "as alias" part for lookup
            base_item = item.split(' as ')[0].strip()

            if base_item in CLASS_MAPPINGS:
                canonical_module = CLASS_MAPPINGS[base_item]

                if canonical_module.startswith('#'):
                    # Phantom class - comment out
                    phantom_items.append(f"# {item}  {canonical_module}")
                else:
                    if canonical_module not in module_groups:
                        module_groups[canonical_module] = []
                    module_groups[canonical_module].append(item)
            else:
                # Unknown class - keep as-is but redirect to core_orchestrator
                if "farfan_pipeline.orchestration.core_orchestrator" not in module_groups:
                    module_groups["farfan_pipeline.orchestration.core_orchestrator"] = []
                module_groups["farfan_pipeline.orchestration.core_orchestrator"].append(item)

        # Generate replacement imports
        replacements = []
        for module, items_list in module_groups.items():
            items_str = ', '.join(items_list)
            replacements.append(f"from {module} import {items_str}")

        # Add phantom items as comments
        for phantom in phantom_items:
            replacements.append(phantom)

        change_msg = f"  {file_path.name}: {imported_items} → split by canonical modules"
        changes.append(change_msg)

        return '\n'.join(replacements)

    content = re.sub(pattern, replace_import, content)

    if content != original:
        return content, changes
    return content, []


def process_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Process a single test file.

    Returns:
        Tuple of (was_modified, list of changes)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content

        # Apply orchestrator import fixes
        content, changes = fix_orchestrator_imports(content, file_path)

        if content != original:
            # Write back
            file_path.write_text(content, encoding='utf-8')
            return True, changes

        return False, []

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}", file=sys.stderr)
        return False, []


def main():
    """Main execution"""
    repo_root = Path(__file__).parent.parent
    tests_dir = repo_root / "tests"

    if not tests_dir.exists():
        print(f"ERROR: Tests directory not found: {tests_dir}", file=sys.stderr)
        return 1

    print("=" * 70)
    print("TEST IMPORT REMEDIATION - Phase 5 Step 3")
    print("=" * 70)
    print(f"Repository: {repo_root}")
    print(f"Tests directory: {tests_dir}")
    print("")

    # Find all test files with forbidden imports
    test_files = list(tests_dir.rglob("*.py"))

    # Filter files that have orchestration.orchestrator imports
    files_to_fix = []
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding='utf-8')
            if 'orchestration.orchestrator' in content:
                files_to_fix.append(test_file)
        except Exception:
            continue

    print(f"Found {len(files_to_fix)} test files with forbidden imports")
    print("")

    # Process each file
    modified_count = 0
    all_changes = []

    for test_file in files_to_fix:
        modified, changes = process_file(test_file)
        if modified:
            modified_count += 1
            all_changes.extend(changes)
            print(f"✓ Fixed: {test_file.relative_to(repo_root)}")

    print("")
    print("=" * 70)
    print(f"REMEDIATION COMPLETE")
    print("=" * 70)
    print(f"Files modified: {modified_count}/{len(files_to_fix)}")
    print("")

    if all_changes:
        print("Changes made:")
        for change in all_changes[:20]:  # Show first 20
            print(change)
        if len(all_changes) > 20:
            print(f"  ... and {len(all_changes) - 20} more")

    print("")
    print("Next step: Run validation script")
    print("  ./scripts/validate_architecture.sh")
    print("")

    return 0


if __name__ == "__main__":
    sys.exit(main())
