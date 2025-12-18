#!/bin/bash
# Check for legacy Phase imports
# Exit with error if found

set -e

echo "Checking for legacy Phase imports..."

# Search for legacy Phase_four_five_six_seven imports in Python files
if grep -rn "Phase_four_five_six_seven" src/ --include="*.py" 2>/dev/null | grep -v "\.py~" | grep -v "PHASE_4_7_RIA"; then
    echo "❌ FAILED: Found legacy Phase_four_five_six_seven imports!"
    echo "   Use 'phase_4_7_aggregation_pipeline' instead."
    exit 1
fi

# Search for legacy Phase_zero imports (excluding compatibility shims)
if grep -rn "from.*\.Phase_zero\." src/ --include="*.py" 2>/dev/null \
   | grep -v "canonic_phases/__init__.py" \
   | grep -v "phases/Phase_zero/__init__.py" \
   | grep -v "phase_0_input_validation"; then
    echo "❌ FAILED: Found legacy Phase_zero imports!"
    echo "   Use 'from canonic_phases.phase_0_input_validation.phase0_' instead."
    exit 1
fi

echo "✅ PASSED: No legacy imports found."
exit 0
