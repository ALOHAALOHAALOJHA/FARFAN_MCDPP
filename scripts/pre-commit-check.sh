#!/bin/bash
# Pre-commit hook to enforce SIN_CARRETA compliance

echo "Running SIN_CARRETA Compliance Check..."

# Get the root directory of the repo
REPO_ROOT=$(git rev-parse --show-toplevel)
AUDIT_SCRIPT="$REPO_ROOT/scripts/audit_hardcoded_values.py"

if [ -f "$AUDIT_SCRIPT" ]; then
    python3 "$AUDIT_SCRIPT"
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -ne 0 ]; then
        echo "❌ Compliance check FAILED. See violations_audit.md for details."
        echo "Commit aborted."
        exit 1
    else
        echo "✅ Compliance check PASSED."
        exit 0
    fi
else
    echo "⚠️ Audit script not found at $AUDIT_SCRIPT. Skipping check."
    exit 0
fi
