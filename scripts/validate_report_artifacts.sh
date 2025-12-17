#!/bin/bash
# CI validation script for report generation artifacts
# Validates presence and non-empty size of generated reports

set -e

ARTIFACTS_DIR="${1:-artifacts/plan1}"

echo "==========================================="
echo "Report Generation CI Validation"
echo "==========================================="
echo "Artifacts directory: $ARTIFACTS_DIR"
echo ""

if [ ! -d "$ARTIFACTS_DIR" ]; then
    echo "❌ FAIL: Artifacts directory not found: $ARTIFACTS_DIR"
    exit 1
fi

echo "✓ Artifacts directory exists"

# Function to check file
check_file() {
    local filename=$1
    local min_size=$2
    local filepath="$ARTIFACTS_DIR/$filename"
    
    if [ ! -f "$filepath" ]; then
        echo "❌ FAIL: File not found: $filename"
        return 1
    fi
    
    local size=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null)
    
    if [ "$size" -lt "$min_size" ]; then
        echo "❌ FAIL: File too small: $filename (${size} bytes < ${min_size} bytes)"
        return 1
    fi
    
    echo "✓ $filename (${size} bytes)"
    return 0
}

echo ""
echo "Checking required artifacts:"
echo ""

# Check for report files with minimum sizes
check_file "plan1_report.md" 1000 || exit 1
check_file "plan1_report.html" 5000 || exit 1
# PDF check is optional since WeasyPrint has system dependencies
if [ -f "$ARTIFACTS_DIR/plan1_report.pdf" ]; then
    check_file "plan1_report.pdf" 10000 || echo "⚠ Warning: PDF found but may be too small"
else
    echo "⚠ Warning: PDF not found (WeasyPrint may not be available)"
fi

# Check for manifest
check_file "plan1_manifest.json" 100 || exit 1

echo ""
echo "Validating manifest structure:"
echo ""

MANIFEST_FILE="$ARTIFACTS_DIR/plan1_manifest.json"

# Check manifest has SHA256 hashes
if ! grep -q '"sha256"' "$MANIFEST_FILE"; then
    echo "❌ FAIL: Manifest missing SHA256 hashes"
    exit 1
fi

echo "✓ Manifest contains SHA256 hashes"

# Check manifest has expected artifacts
for artifact in "markdown" "html"; do
    if ! grep -q "\"$artifact\"" "$MANIFEST_FILE"; then
        echo "❌ FAIL: Manifest missing $artifact entry"
        exit 1
    fi
    echo "✓ Manifest includes $artifact"
done

# Validate SHA256 format (64 hex characters)
sha256_count=$(grep -o '"sha256": "[a-f0-9]\{64\}"' "$MANIFEST_FILE" | wc -l | tr -d ' ')

if [ "$sha256_count" -lt 1 ]; then
    echo "❌ FAIL: No valid SHA256 hashes found in manifest"
    exit 1
fi

echo "✓ Found $sha256_count valid SHA256 hash(es)"

echo ""
echo "==========================================="
echo "✅ All CI validations PASSED"
echo "==========================================="

exit 0
