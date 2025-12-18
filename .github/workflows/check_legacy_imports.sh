#!/bin/bash
# Check for legacy Phase_four_five_six_seven imports
# Exit with error if found

set -e

echo "Checking for legacy Phase_four_five_six_seven imports..."

# Search for legacy imports in Python files
if grep -rn "Phase_four_five_six_seven" src/ --include="*.py" 2>/dev/null | grep -v "\.py~" | grep -v "PHASE_4_7_RIA"; then
    echo "❌ FAILED: Found legacy Phase_four_five_six_seven imports!"
    echo "   Use 'phase_4_7_aggregation_pipeline' instead."
    exit 1
fi

echo "✅ PASSED: No legacy imports found."
exit 0
