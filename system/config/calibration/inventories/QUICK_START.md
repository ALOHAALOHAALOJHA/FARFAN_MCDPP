# COHORT_2024 Calibration Inventories - Quick Start

## TL;DR

```bash
# Run complete consolidation (generates all 3 artifacts)
cd system/config/calibration/inventories
python3 consolidate_calibration_inventories.py

# Or use the shell wrapper
./run_consolidation.sh
```

## What You Get

After running consolidation, you'll have 3 authoritative JSON files:

1. **COHORT_2024_canonical_method_inventory.json**
   - All 1995+ methods discovered in codebase
   - MODULE:CLASS.METHOD@LAYER notation
   - Role classifications (SCORE_Q, INGEST_PDM, etc.)

2. **COHORT_2024_method_signatures.json**
   - Parametrization specs for each method
   - required_inputs, optional_inputs, output_type

3. **COHORT_2024_calibration_coverage_matrix.json**
   - Layer-wise calibration status (computed vs pending)
   - Coverage statistics per layer (@b, @q, @d, @p, @C, @chain, @u, @m)
   - Per-role coverage breakdown

Plus a summary report: **COHORT_2024_consolidation_summary.md**

## Expected Output

```
Total Methods Discovered: 2000+
Method Signatures Extracted: 2000+
Parametrization Coverage: ~100%

Calibration Status:
  Fully Calibrated: ~150 methods
  Partially Calibrated: ~850 methods
  Not Calibrated: ~1000 methods
  Overall Calibration %: ~7-10%
```

## Typical Workflow

1. **Initial Scan** - Run consolidation to establish baseline
2. **Review Coverage** - Check coverage matrix for pending methods
3. **Run Calibrations** - Execute layer-specific calibration computations
4. **Re-consolidate** - Re-run to verify completeness
5. **Iterate** - Repeat until target coverage achieved

## Files Generated

```
system/config/calibration/inventories/
├── COHORT_2024_canonical_method_inventory.json      ← Artifact 1
├── COHORT_2024_method_signatures.json               ← Artifact 2
├── COHORT_2024_calibration_coverage_matrix.json     ← Artifact 3
├── COHORT_2024_consolidation_summary.md             ← Report
└── calibration_consolidation.log                    ← Detailed log
```

## Troubleshooting

### "Inventory scan found 0 methods"
- Check that src/ directory exists
- Verify Python files are not corrupted
- Check log file for parsing errors

### "Signature extraction failed"
- Ensure inventory JSON exists
- Check file paths are correct
- Verify source files haven't moved

### "Coverage matrix shows 0% calibration"
- Normal for first run
- Need to run actual calibration computations
- Check intrinsic_calibration.json exists

## Integration Points

### Source Calibration Configs
Located at: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/`
- COHORT_2024_intrinsic_calibration.json
- COHORT_2024_method_compatibility.json
- COHORT_2024_layer_requirements.json

### Calibration Orchestrator
Main orchestrator: `src/orchestration/calibration_orchestrator.py`

### Tests
Calibration tests: `tests/calibration/`

## Next Steps

1. Review `COHORT_2024_consolidation_summary.md`
2. Identify methods with `pending` status in coverage matrix
3. Run layer-specific calibration scripts:
   - Base layer (@b): intrinsic scoring
   - Question layer (@q): question compatibility
   - Dimension layer (@d): dimension compatibility
   - Policy layer (@p): policy compatibility
   - Congruence layer (@C): cross-method consistency
   - Chain layer (@chain): pipeline compatibility
   - Unit layer (@u): test coverage
   - Meta layer (@m): meta-analysis capabilities
4. Re-run consolidation to update coverage

## Help

```bash
# View detailed help
python3 consolidate_calibration_inventories.py --help

# Check individual scripts
python3 scan_methods_inventory.py --help
python3 method_signature_extractor.py --help
python3 calibration_coverage_validator.py --help
```

---

*Quick Start Guide - COHORT_2024 Calibration Framework*
