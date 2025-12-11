#!/bin/bash
# COHORT_2024 Calibration Inventory Consolidation Runner
#
# This script runs the complete calibration inventory consolidation process
# to generate all three authoritative artifacts.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================================"
echo "COHORT_2024 Calibration Inventory Consolidation"
echo "========================================================================"
echo ""
echo "Output directory: $SCRIPT_DIR"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
echo "Python version: $PYTHON_VERSION"

if [ ! -f "consolidate_calibration_inventories.py" ]; then
    echo "ERROR: consolidate_calibration_inventories.py not found"
    exit 1
fi

echo ""
echo "Starting consolidation process..."
echo "========================================================================"
echo ""

# Run the consolidation script
python3 consolidate_calibration_inventories.py

EXIT_CODE=$?

echo ""
echo "========================================================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Consolidation completed successfully!"
    echo ""
    echo "Generated files:"
    echo "  - COHORT_2024_canonical_method_inventory.json"
    echo "  - COHORT_2024_method_signatures.json"
    echo "  - COHORT_2024_calibration_coverage_matrix.json"
    echo "  - COHORT_2024_consolidation_summary.md"
    echo ""
    echo "Check COHORT_2024_consolidation_summary.md for detailed statistics."
else
    echo "✗ Consolidation failed with exit code $EXIT_CODE"
    echo ""
    echo "Check calibration_consolidation.log for details."
fi

echo "========================================================================"

exit $EXIT_CODE
