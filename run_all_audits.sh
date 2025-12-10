#!/bin/bash
# Comprehensive audit runner for all 300 contracts

set -e

echo "=========================================="
echo "F.A.R.F.A.N CONTRACT AUDIT SUITE"
echo "=========================================="
echo ""

# Store start time
START_TIME=$(date +%s)

# Run completeness audit
echo "1. Running Completeness Audit..."
python3 audit_contracts_completeness.py
COMPLETENESS_EXIT=$?
echo ""

# Run wiring audit
echo "2. Running Evidence Flow Wiring Audit..."
python3 audit_evidence_flow_wiring.py
WIRING_EXIT=$?
echo ""

# Run signal synchronization audit
echo "3. Running Signal Synchronization Audit..."
python3 audit_signal_synchronization.py
SIGNAL_EXIT=$?
echo ""

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Summary
echo "=========================================="
echo "AUDIT SUITE SUMMARY"
echo "=========================================="
echo ""
echo "Completeness Audit:           $([ $COMPLETENESS_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "Evidence Flow Wiring:         $([ $WIRING_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "Signal Synchronization:       $([ $SIGNAL_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo ""
echo "Total Duration: ${DURATION}s"
echo ""

# Check if all passed
if [ $COMPLETENESS_EXIT -eq 0 ] && [ $WIRING_EXIT -eq 0 ] && [ $SIGNAL_EXIT -eq 0 ]; then
    echo "🎉 ALL AUDITS PASSED - SYSTEM FULLY VALIDATED"
    echo ""
    echo "Reports generated:"
    echo "  - audit_contracts_report.json"
    echo "  - audit_evidence_flow_report.json"
    echo "  - audit_signal_sync_report.json"
    echo "  - AUDIT_REPORT_CONTRACTS_COMPLETENESS.md"
    echo ""
    exit 0
else
    echo "❌ SOME AUDITS FAILED - REVIEW REPORTS FOR DETAILS"
    echo ""
    exit 1
fi
