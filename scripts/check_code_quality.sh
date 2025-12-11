#!/bin/bash
#
# Code Quality Check Script for F.A.R.F.A.N Pipeline
#
# This script runs various code quality checks including:
# - Circular import detection
# - Code linting (if available)
# - Type checking (if available)
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed

set -e  # Exit on first error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "F.A.R.F.A.N Code Quality Checks"
echo "============================================================"
echo "Project: $PROJECT_ROOT"
echo ""

# Track overall status
FAILED_CHECKS=0

# 1. Check for circular imports
echo "--- Checking for circular imports ---"
if python "$SCRIPT_DIR/check_circular_imports.py"; then
    echo "✅ Circular import check passed"
else
    echo "❌ Circular import check failed"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi
echo ""

# 2. Run ruff linter if available
echo "--- Running linter (ruff) ---"
if command -v ruff &> /dev/null; then
    if ruff check "$PROJECT_ROOT/src" "$PROJECT_ROOT/farfan_core" 2>/dev/null; then
        echo "✅ Linting passed"
    else
        echo "⚠️  Linting found issues (non-blocking)"
    fi
else
    echo "ℹ️  ruff not installed, skipping linter check"
fi
echo ""

# 3. Run mypy type checker if available
echo "--- Running type checker (mypy) ---"
if command -v mypy &> /dev/null; then
    # Only check specific directories with strict typing
    if mypy "$PROJECT_ROOT/farfan_core/farfan_core/core/" 2>/dev/null; then
        echo "✅ Type checking passed"
    else
        echo "⚠️  Type checking found issues (non-blocking)"
    fi
else
    echo "ℹ️  mypy not installed, skipping type check"
fi
echo ""

# Summary
echo "============================================================"
echo "Summary"
echo "============================================================"
if [ $FAILED_CHECKS -eq 0 ]; then
    echo "✅ All critical checks passed"
    exit 0
else
    echo "❌ $FAILED_CHECKS critical check(s) failed"
    exit 1
fi
