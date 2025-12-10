#!/bin/bash
#
# Phase_zero Cleanup Script
# =========================
# Safely archives unused files from Phase_zero folder
#
# Date: 2025-12-10
# Status: SAFE - Creates archive, doesn't delete
#

set -e  # Exit on error

REPO_ROOT="/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE"
PHASE_ZERO_DIR="$REPO_ROOT/src/canonic_phases/Phase_zero"
ARCHIVE_DIR="$REPO_ROOT/archive/phase_zero_unused_$(date +%Y%m%d)"

echo "========================================="
echo "Phase_zero Cleanup Script"
echo "========================================="
echo ""
echo "Repository: $REPO_ROOT"
echo "Phase_zero: $PHASE_ZERO_DIR"
echo "Archive: $ARCHIVE_DIR"
echo ""

# Verify we're in the right directory
if [ ! -d "$PHASE_ZERO_DIR" ]; then
    echo "ERROR: Phase_zero directory not found!"
    echo "Expected: $PHASE_ZERO_DIR"
    exit 1
fi

# Create archive directory
echo "Creating archive directory..."
mkdir -p "$ARCHIVE_DIR"
echo "✓ Archive directory created: $ARCHIVE_DIR"
echo ""

# List of dead code files to archive
DEAD_FILES=(
    "contracts.py"
    "contracts_runtime.py"
    "core_contracts.py"
    "coverage_gate.py"
    "determinism_helpers.py"
    "deterministic_execution.py"
    "domain_errors.py"
    "enhanced_contracts.py"
    "hash_utils.py"
    "json_contract_loader.py"
    "json_logger.py"
    "runtime_error_fixes.py"
    "schema_monitor.py"
    "seed_factory.py"
    "signature_validator.py"
)

# Archive dead code files
echo "Archiving dead code files..."
for file in "${DEAD_FILES[@]}"; do
    if [ -f "$PHASE_ZERO_DIR/$file" ]; then
        mv "$PHASE_ZERO_DIR/$file" "$ARCHIVE_DIR/"
        echo "  ✓ Archived: $file"
    else
        echo "  ⚠ Not found: $file"
    fi
done
echo ""

# Create archive manifest
echo "Creating archive manifest..."
cat > "$ARCHIVE_DIR/ARCHIVE_MANIFEST.md" << 'EOF'
# Phase_zero Archived Files
## Date: $(date +%Y-%m-%d)

These files were archived because:
- Zero external imports (not used by any active code)
- Zero test coverage (not referenced in tests)
- No entry points (not in setup.py or scripts)

## Archived Files
EOF

for file in "${DEAD_FILES[@]}"; do
    if [ -f "$ARCHIVE_DIR/$file" ]; then
        size=$(du -h "$ARCHIVE_DIR/$file" | cut -f1)
        echo "- $file ($size)" >> "$ARCHIVE_DIR/ARCHIVE_MANIFEST.md"
    fi
done

echo "✓ Archive manifest created"
echo ""

# Count remaining files
REMAINING=$(ls -1 "$PHASE_ZERO_DIR"/*.py 2>/dev/null | wc -l)
ARCHIVED=$(ls -1 "$ARCHIVE_DIR"/*.py 2>/dev/null | wc -l)

echo "========================================="
echo "Cleanup Complete!"
echo "========================================="
echo ""
echo "Files remaining in Phase_zero: $REMAINING"
echo "Files archived: $ARCHIVED"
echo ""
echo "Active files (should be 6):"
ls -lh "$PHASE_ZERO_DIR"/*.py | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Archived files location:"
echo "  $ARCHIVE_DIR"
echo ""
echo "Next steps:"
echo "  1. Verify tests still pass: pytest tests/test_phase0_runtime_config.py -v"
echo "  2. Fix main.py imports (see PHASE_ZERO_CLEANUP_AUDIT.md)"
echo "  3. Update __init__.py exports"
echo ""
echo "To restore files: mv $ARCHIVE_DIR/* $PHASE_ZERO_DIR/"
echo ""
