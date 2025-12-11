#!/bin/bash
# Comprehensive audit runner for all F.A.R.F.A.N audits

set -e

echo "=========================================="
echo "F.A.R.F.A.N AUDIT SUITE"
echo "=========================================="
echo ""

# Store start time
START_TIME=$(date +%s)

# Define audits to run: "name:script:report"
declare -a AUDITS=(
    "Completeness:audit_contracts_completeness.py:audit_contracts_report.json"
    "Evidence Flow:audit_evidence_flow_wiring.py:audit_evidence_flow_report.json"
    "Signal Sync:audit_signal_synchronization.py:audit_signal_sync_report.json"
    "Factory Pattern:audit_factory.py:audit_factory_report.json"
)

# Array to store exit codes
declare -a EXIT_CODES=()
declare -a AUDIT_NAMES=()

# Run each audit
AUDIT_NUM=1
for audit_spec in "${AUDITS[@]}"; do
    IFS=':' read -r name script report <<< "$audit_spec"
    
    echo "${AUDIT_NUM}. Running ${name} Audit..."
    
    # Check if script exists
    if [ ! -f "$script" ]; then
        echo "ERROR: $script not found!" >&2
        exit 2
    fi
    
    # Run audit
    python3 "$script"
    EXIT_CODE=$?
    
    # Store results
    EXIT_CODES+=($EXIT_CODE)
    AUDIT_NAMES+=("$name")
    
    echo ""
    ((AUDIT_NUM++))
done

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Summary
echo "=========================================="
echo "AUDIT SUITE SUMMARY"
echo "=========================================="
echo ""

# Display results for each audit
ALL_PASSED=true
for i in "${!AUDIT_NAMES[@]}"; do
    name="${AUDIT_NAMES[$i]}"
    exit_code="${EXIT_CODES[$i]}"
    
    # Pad name for alignment
    printf "%-30s" "${name}:"
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ PASSED"
    else
        echo "❌ FAILED"
        ALL_PASSED=false
    fi
done

echo ""
echo "Total Duration: ${DURATION}s"
echo ""

# Final status
if $ALL_PASSED; then
    echo "🎉 ALL AUDITS PASSED - SYSTEM FULLY VALIDATED"
    echo ""
    echo "Reports generated:"
    for audit_spec in "${AUDITS[@]}"; do
        IFS=':' read -r name script report <<< "$audit_spec"
        echo "  - $report"
    done
    echo "  - AUDIT_REPORT_CONTRACTS_COMPLETENESS.md"
    echo "  - AUDIT_FACTORY_PATTERN.md"
    echo ""
    exit 0
else
    echo "❌ SOME AUDITS FAILED - REVIEW REPORTS FOR DETAILS"
    echo ""
    exit 1
fi
