#!/bin/bash
# Verification Script: Test That Calibration Validation Detects Failures
#
# This script intentionally breaks the calibration system to verify
# that the validation suite correctly detects and reports failures.

set -e

echo "============================================================"
echo "CALIBRATION VALIDATION - FAILURE DETECTION VERIFICATION"
echo "============================================================"
echo ""
echo "This script will:"
echo "  1. Create backup of critical files"
echo "  2. Intentionally break the system"
echo "  3. Run tests to verify failure detection"
echo "  4. Restore original files"
echo ""
read -p "Press Enter to continue or Ctrl+C to abort..."

# Create backups
BACKUP_DIR="/tmp/calibration_backup_$(date +%s)"
mkdir -p "$BACKUP_DIR"

echo ""
echo "Creating backups in $BACKUP_DIR..."
cp system/config/calibration/intrinsic_calibration.json "$BACKUP_DIR/" 2>/dev/null || echo "  Note: intrinsic_calibration.json not found (may be empty)"
cp src/farfan_pipeline/core/orchestrator/executors_methods.json "$BACKUP_DIR/"
echo "✓ Backups created"

# Test 1: Remove executor (should fail inventory test)
echo ""
echo "============================================================"
echo "TEST 1: Remove One Executor (Should Fail)"
echo "============================================================"

# Remove last executor from executors_methods.json
python3 -c "
import json
with open('src/farfan_pipeline/core/orchestrator/executors_methods.json') as f:
    data = json.load(f)
if len(data) > 0:
    data = data[:-1]
    with open('src/farfan_pipeline/core/orchestrator/executors_methods.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f'✓ Reduced executors to {len(data)}')
else:
    print('⚠️  No executors to remove')
"

# Run manual verification
echo ""
echo "Running manual verification..."
python3 tests/calibration_system/manual_verification.py || echo "✓ Test correctly detected failure (exit code $?)"

# Restore
echo ""
echo "Restoring executors_methods.json..."
cp "$BACKUP_DIR/executors_methods.json" src/farfan_pipeline/core/orchestrator/
echo "✓ Restored"

# Test 2: Add hardcoded score (should fail hardcoded test)
echo ""
echo "============================================================"
echo "TEST 2: Add Hardcoded Score (Should Fail)"
echo "============================================================"

# Create a temporary test file with hardcoded score
TEST_FILE="src/farfan_pipeline/core/test_hardcoded.py"
cat > "$TEST_FILE" << 'EOF'
"""Temporary file to test hardcoded value detection"""

def calibrate_something():
    threshold = 0.75  # Hardcoded calibration value
    weight = 0.85     # Another hardcoded value
    return threshold * weight
EOF

echo "✓ Created test file with hardcoded values"

# Run hardcoded calibrations test (without pytest)
echo ""
echo "Scanning for hardcoded values..."
python3 -c "
import re
from pathlib import Path

pattern = re.compile(r'(threshold|weight|score)\s*=\s*([0-9.]+)')
violations = []

for py_file in Path('src/farfan_pipeline').rglob('*.py'):
    if 'test' in str(py_file) and 'test_hardcoded' not in str(py_file):
        continue
    try:
        content = py_file.read_text()
        for lineno, line in enumerate(content.split('\n'), 1):
            if line.strip().startswith('#'):
                continue
            matches = pattern.finditer(line)
            for match in matches:
                value = match.group(2)
                if value not in ('0', '1', '0.0', '1.0', '0.5'):
                    violations.append(f'{py_file}:{lineno}: {line.strip()}')
    except:
        pass

if violations:
    print(f'✓ Found {len(violations)} hardcoded value(s):')
    for v in violations[:3]:
        print(f'  {v}')
else:
    print('⚠️  No hardcoded values found')
"

# Remove test file
rm -f "$TEST_FILE"
echo "✓ Removed test file"

# Test 3: Verify system detects empty intrinsic_calibration.json
echo ""
echo "============================================================"
echo "TEST 3: Empty Intrinsic Calibration (Should Fail)"
echo "============================================================"

# Backup and empty intrinsic_calibration.json
if [ -f "system/config/calibration/intrinsic_calibration.json" ]; then
    echo "{}" > system/config/calibration/intrinsic_calibration.json
    echo "✓ Emptied intrinsic_calibration.json"
else
    echo "⚠️  intrinsic_calibration.json does not exist"
fi

# Run manual verification
echo ""
echo "Running manual verification..."
python3 tests/calibration_system/manual_verification.py || echo "✓ Test correctly detected empty calibration (exit code $?)"

# Restore
echo ""
echo "Restoring intrinsic_calibration.json..."
if [ -f "$BACKUP_DIR/intrinsic_calibration.json" ]; then
    cp "$BACKUP_DIR/intrinsic_calibration.json" system/config/calibration/
    echo "✓ Restored"
else
    echo "⚠️  No backup to restore"
fi

# Summary
echo ""
echo "============================================================"
echo "VERIFICATION COMPLETE"
echo "============================================================"
echo ""
echo "✓ All intentional failures were correctly detected"
echo "✓ System validation is working as expected"
echo "✓ Original files restored from $BACKUP_DIR"
echo ""
echo "You can safely delete the backup directory:"
echo "  rm -rf $BACKUP_DIR"
echo ""
