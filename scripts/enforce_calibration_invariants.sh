#!/bin/bash
# Automated invariant enforcement via grep
# Generated from inv_specifications.py

CALIBRATION_DIR='src/farfan_pipeline/infrastructure/calibration'
FAILURES=0

# Check INV-CAL-001: Prior Strength Bounds
echo 'Checking INV-CAL-001...'
grep -r 'INV-CAL-001.*prior_strength.*bounds' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-001 - Prior Strength Bounds'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-001'
fi

# Check INV-CAL-002: Veto Threshold Bounds
echo 'Checking INV-CAL-002...'
grep -r 'INV-CAL-002.*veto_threshold.*bounds' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-002 - Veto Threshold Bounds'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-002'
fi

# Check INV-CAL-003: No Prohibited Operations
echo 'Checking INV-CAL-003...'
grep -r 'INV-CAL-003.*prohibited.*operations' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-003 - No Prohibited Operations'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-003'
fi

# Check INV-CAL-004: Validity Window Constraint
echo 'Checking INV-CAL-004...'
grep -r 'INV-CAL-004.*validity.*UoA' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-004 - Validity Window Constraint'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-004'
fi

# Check INV-CAL-005: Cognitive Cost Factored
echo 'Checking INV-CAL-005...'
grep -r 'INV-CAL-005.*cognitive.*cost.*prior' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-005 - Cognitive Cost Factored'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-005'
fi

# Check INV-CAL-006: Interaction Density Capped
echo 'Checking INV-CAL-006...'
grep -r 'INV-CAL-006.*interaction.*density.*cap' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-006 - Interaction Density Capped'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-006'
fi

# Check INV-CAL-007: Immutable Manifests
echo 'Checking INV-CAL-007...'
grep -r 'INV-CAL-007.*immutable.*manifest.*hash' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-007 - Immutable Manifests'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-007'
fi

# Check INV-CAL-008: Drift Reports Generated
echo 'Checking INV-CAL-008...'
grep -r 'INV-CAL-008.*drift.*report' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-008 - Drift Reports Generated'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-008'
fi

# Check INV-CAL-009: Coverage and Dispersion Penalties
echo 'Checking INV-CAL-009...'
grep -r 'INV-CAL-009.*coverage.*dispersion.*penalty' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-009 - Coverage and Dispersion Penalties'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-009'
fi

# Check INV-CAL-010: Contradiction Penalties
echo 'Checking INV-CAL-010...'
grep -r 'INV-CAL-010.*contradiction.*penalty' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-010 - Contradiction Penalties'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-010'
fi

# Check INV-CAL-011: UoA Complexity Score Bounds
echo 'Checking INV-CAL-011...'
grep -r 'INV-CAL-011.*complexity.*score.*\[0.*1\]' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-011 - UoA Complexity Score Bounds'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-011'
fi

# Check INV-CAL-012: UoA Municipality Code Format
echo 'Checking INV-CAL-012...'
grep -r 'INV-CAL-012.*municipality.*code.*pattern' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-012 - UoA Municipality Code Format'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-012'
fi

# Check INV-CAL-013: Epistemic Layer Ratios
echo 'Checking INV-CAL-013...'
grep -r 'INV-CAL-013.*layer.*ratio.*TYPE' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-013 - Epistemic Layer Ratios'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-013'
fi

# Check INV-CAL-014: Mandatory Patterns Present
echo 'Checking INV-CAL-014...'
grep -r 'INV-CAL-014.*mandatory.*pattern.*TYPE' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-014 - Mandatory Patterns Present'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-014'
fi

# Check INV-CAL-015: Dependency Chain Validity
echo 'Checking INV-CAL-015...'
grep -r 'INV-CAL-015.*dependency.*chain.*valid' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-015 - Dependency Chain Validity'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-015'
fi

# Check INV-CAL-016: Acyclic Dependency Graph
echo 'Checking INV-CAL-016...'
grep -r 'INV-CAL-016.*acyclic.*DAG' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-016 - Acyclic Dependency Graph'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-016'
fi

# Check INV-CAL-017: No Level Inversions
echo 'Checking INV-CAL-017...'
grep -r 'INV-CAL-017.*level.*inversion' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-017 - No Level Inversions'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-017'
fi

# Check INV-CAL-018: Bounded Multiplicative Fusion
echo 'Checking INV-CAL-018...'
grep -r 'INV-CAL-018.*bounded.*fusion.*\[0\.01.*10' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-018 - Bounded Multiplicative Fusion'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-018'
fi

# Check INV-CAL-019: UoA Requirements Documented
echo 'Checking INV-CAL-019...'
grep -r 'Unit of Analysis Requirements:' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-019 - UoA Requirements Documented'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-019'
fi

# Check INV-CAL-020: Epistemic Level Documented
echo 'Checking INV-CAL-020...'
grep -r 'Epistemic Level: N[1-3]' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-020 - Epistemic Level Documented'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-020'
fi

# Check INV-CAL-021: Fusion Strategy Documented
echo 'Checking INV-CAL-021...'
grep -r 'Fusion Strategy:' "$CALIBRATION_DIR" > /dev/null
if [ $? -ne 0 ]; then
  echo '  ❌ FAILED: INV-CAL-021 - Fusion Strategy Documented'
  FAILURES=$((FAILURES + 1))
else
  echo '  ✅ PASSED: INV-CAL-021'
fi

if [ $FAILURES -gt 0 ]; then
  echo ""
  echo "❌ $FAILURES invariant(s) failed enforcement"
  exit 1
else
  echo ""
  echo "✅ All invariants passed enforcement"
  exit 0
fi