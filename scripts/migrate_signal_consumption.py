#!/usr/bin/env python3
"""Migrate signal_consumption imports to canonical locations.

Phase 5 remediation: Move from _deprecated to canonical audit modules.
"""

import re
import sys
from pathlib import Path

# Migration mapping
MIGRATIONS = {
    # AccessLevel, AccessRecord, QuestionnaireAccessAudit, get_access_audit, reset_access_audit
    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_consumption import \(\s*AccessLevel":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.audit.questionnaire_access_audit import (\n    AccessLevel",

    # Standalone imports
    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_consumption import AccessLevel":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.audit.questionnaire_access_audit import AccessLevel",

    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_consumption import get_access_audit":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.audit.questionnaire_access_audit import get_access_audit",

    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_consumption import reset_access_audit":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.audit.questionnaire_access_audit import reset_access_audit",

    # SignalConsumptionProof
    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_consumption import \(\s*SignalConsumptionProof":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.audit.consumption_proof import (\n    SignalConsumptionProof",

    r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_consumption import SignalConsumptionProof":
        "from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.audit.consumption_proof import SignalConsumptionProof",
}

# Unified migration for multi-line imports
MULTILINE_PATTERN = r"from farfan_pipeline\.infrastructure\.irrigation_using_signals\.SISAS\.signal_consumption import \([^)]+\)"

def split_imports(content: str, filepath: Path) -> str:
    """Split signal_consumption imports into canonical modules."""

    # Find multiline imports
    matches = list(re.finditer(MULTILINE_PATTERN, content, re.DOTALL))

    if not matches:
        # Try single-line substitutions
        for pattern, replacement in MIGRATIONS.items():
            content = re.sub(pattern, replacement, content)
        return content

    # Process multiline imports
    for match in reversed(matches):  # Reverse to preserve indices
        import_block = match.group(0)

        # Extract imported symbols
        symbols_match = re.search(r"\(([^)]+)\)", import_block, re.DOTALL)
        if not symbols_match:
            continue

        symbols_text = symbols_match.group(1)
        symbols = [s.strip().rstrip(",") for s in symbols_text.split("\n") if s.strip() and not s.strip().startswith("#")]

        # Categorize symbols
        audit_symbols = []
        proof_symbols = []

        for symbol in symbols:
            if symbol in ("AccessLevel", "AccessRecord", "QuestionnaireAccessAudit", "get_access_audit", "reset_access_audit"):
                audit_symbols.append(symbol)
            elif symbol in ("SignalConsumptionProof", "SignalManifest", "build_merkle_tree", "compute_file_hash", "generate_signal_manifests"):
                proof_symbols.append(symbol)

        # Build replacement imports
        replacements = []

        if audit_symbols:
            symbols_joined = ",\n    ".join(audit_symbols)
            audit_import = f"from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.audit.questionnaire_access_audit import (\n    {symbols_joined},\n)"
            replacements.append(audit_import)

        if proof_symbols:
            symbols_joined = ",\n    ".join(proof_symbols)
            proof_import = f"from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.audit.consumption_proof import (\n    {symbols_joined},\n)"
            replacements.append(proof_import)

        if replacements:
            replacement_text = "\n".join(replacements)
            content = content[:match.start()] + replacement_text + content[match.end():]
            print(f"✓ Migrated {filepath}: {len(audit_symbols)} audit + {len(proof_symbols)} proof symbols")

    return content


def migrate_file(filepath: Path) -> bool:
    """Migrate a single file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content

        # Apply migrations
        content = split_imports(content, filepath)

        if content != original:
            filepath.write_text(content, encoding="utf-8")
            return True

        return False
    except Exception as e:
        print(f"✗ Error migrating {filepath}: {e}", file=sys.stderr)
        return False


def main():
    """Main migration entry point."""
    repo_root = Path(__file__).parent.parent

    print("=" * 70)
    print("SIGNAL_CONSUMPTION MIGRATION - Phase 5 Remediation")
    print("=" * 70)
    print(f"Repository: {repo_root}")
    print()

    # Find all Python files importing signal_consumption
    files_to_migrate = []

    for pattern in ["src/**/*.py", "tests/**/*.py"]:
        for filepath in repo_root.glob(pattern):
            if filepath.name == "__pycache__":
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
                if "signal_consumption import" in content:
                    files_to_migrate.append(filepath)
            except Exception:
                continue

    print(f"Found {len(files_to_migrate)} files to migrate")
    print()

    # Migrate files
    migrated_count = 0
    for filepath in files_to_migrate:
        if migrate_file(filepath):
            migrated_count += 1

    print()
    print("=" * 70)
    print(f"Migration complete: {migrated_count}/{len(files_to_migrate)} files updated")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Run tests to verify migration")
    print("  2. Delete _deprecated/signal_consumption.py")
    print("  3. Run ./scripts/validate_architecture.sh")


if __name__ == "__main__":
    main()
