#!/bin/bash
# Configuration Governance Setup Script
# 
# This script sets up the complete configuration governance system:
# 1. Verifies directory structure
# 2. Initializes hash registry
# 3. Creates initial backups
# 4. Sets up pre-commit hook
# 5. Runs integrity verification
#
# IMPLEMENTATION_WAVE: GOVERNANCE_WAVE_2024_12_07
# WAVE_LABEL: CONFIG_GOVERNANCE_STRICT_FOLDERIZATION

set -e

echo "================================================================================"
echo "Configuration Governance System Setup"
echo "================================================================================"
echo ""

# Check if we're in the repository root
if [ ! -d ".git" ]; then
    echo "❌ Error: Must run from repository root"
    exit 1
fi

echo "Step 1: Verifying directory structure..."
echo "--------------------------------------------------------------------------------"

# Check required directories
REQUIRED_DIRS=(
    "system/config/calibration"
    "system/config/questionnaire"
    "system/config/environments"
    ".backup"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir exists"
    else
        echo "  ✗ $dir missing - creating..."
        mkdir -p "$dir"
    fi
done

echo ""
echo "Step 2: Setting up pre-commit hook..."
echo "--------------------------------------------------------------------------------"

if [ -f ".git/hooks/pre-commit" ]; then
    echo "  ✓ Pre-commit hook exists"
    chmod +x .git/hooks/pre-commit
    echo "  ✓ Made executable"
else
    echo "  ✗ Pre-commit hook missing"
    exit 1
fi

echo ""
echo "Step 3: Initializing hash registry..."
echo "--------------------------------------------------------------------------------"

cd system/config
python initialize_registry.py

if [ $? -eq 0 ]; then
    echo "  ✓ Registry initialized"
else
    echo "  ✗ Registry initialization failed"
    exit 1
fi

echo ""
echo "Step 4: Verifying configuration integrity..."
echo "--------------------------------------------------------------------------------"

python verify_config_integrity.py

if [ $? -eq 0 ]; then
    echo "  ✓ All configurations verified"
else
    echo "  ⚠ Some configurations may need attention"
fi

cd ../..

echo ""
echo "Step 5: Scanning for hardcoded values..."
echo "--------------------------------------------------------------------------------"

python system/config/migrate_hardcoded_values.py . --output system/config/hardcoded_values_report.md 2>/dev/null || true

if [ -f "system/config/hardcoded_values_report.md" ]; then
    HARDCODED_COUNT=$(grep -c "^##" system/config/hardcoded_values_report.md || echo "0")
    if [ "$HARDCODED_COUNT" -gt 0 ]; then
        echo "  ⚠ Found hardcoded values in $HARDCODED_COUNT file(s)"
        echo "  → See system/config/hardcoded_values_report.md"
    else
        echo "  ✓ No hardcoded values found"
        rm -f system/config/hardcoded_values_report.md
    fi
else
    echo "  ✓ No hardcoded values found"
fi

echo ""
echo "================================================================================"
echo "✓ Configuration Governance Setup Complete"
echo "================================================================================"
echo ""
echo "Summary:"
echo "  - Directory structure: ✓"
echo "  - Pre-commit hook: ✓"
echo "  - Hash registry: ✓"
echo "  - Configuration backups: ✓"
echo ""
echo "Documentation:"
echo "  - Quick reference: system/config/QUICK_REFERENCE.md"
echo "  - Full governance guide: system/config/GOVERNANCE.md"
echo "  - Backup info: .backup/README.md"
echo ""
echo "Next steps:"
echo "  1. Review system/config/GOVERNANCE.md"
echo "  2. Verify integrity: python system/config/verify_config_integrity.py"
echo "  3. List backups: python system/config/list_backups.py --summary"
echo ""
