# CQVR Results Directory

This directory contains all CQVR (Contract Quality Validation and Remediation) evaluation results, reports, and related artifacts.

## Directory Structure

### `/dashboards`
Interactive HTML dashboards for visualizing contract evaluation results:
- `cqvr_dashboard.html` - Original dashboard
- `cqvr_dashboard_enhanced_v2.1.html` - Enhanced v2.1 dashboard with increased severity

### `/documentation`
Comprehensive documentation and executive summaries:
- `CQVR_V2.1_QUICK_REFERENCE.md` - Quick reference for v2.1 enhancements
- `CQVR_ENHANCED_SEVERITY_REPORT.md` - Executive summary of severity enhancements
- `DECISION_MAKING_SUMMARY.md` - Decision-making guide based on evaluation results
- `CQVR_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `SEVERITY_IMPACT_VISUALIZATION.txt` - Visual comparison of severity impact
- Various batch evaluation reports and retrospectives

### `/evaluations`
Machine-readable JSON evaluation results:
- `cqvr_evaluation_enhanced_v2.1.json` - Complete v2.1 evaluation of 300 contracts
- `cqvr_evaluation_results.json` - Original evaluation results
- `BATCH2_CQVR_SUMMARY.json` - Batch 2 summary
- `Q001_Q030_METHODS.json` - Methods data for Q001-Q030

### `/reports`
Per-contract evaluation reports:
- `Q[001-050]_CQVR_EVALUATION_REPORT.md` - Individual contract reports
- `Q[XXX]_TRANSFORMATION_REPORT.md` - Transformation reports for specific contracts

### Root Level Scripts
Batch evaluation and dashboard generation scripts:
- `evaluate_batch[2-9]_cqvr.py` - Batch evaluation scripts
- `generate_cqvr_dashboard_data.py` - Dashboard data generator
- `generate_Q014_CQVR_report.py` - Specific contract report generator

## Usage

### View Dashboard
Open `dashboards/cqvr_dashboard_enhanced_v2.1.html` in a web browser to see:
- Overall statistics (300 contracts)
- Production ready: 25 (8.3%)
- Need patches: 2 (0.7%)
- Need reformulation: 273 (91.0%)

### Read Documentation
Start with `documentation/DECISION_MAKING_SUMMARY.md` for a comprehensive overview and decision-making guide.

### Access Evaluation Data
Use `evaluations/cqvr_evaluation_enhanced_v2.1.json` for programmatic access to all evaluation results.

### Review Individual Contracts
Check `reports/Q[XXX]_CQVR_EVALUATION_REPORT.md` for detailed analysis of specific contracts.

## CQVR v2.1 Highlights

**Enhanced Severity Thresholds:**
- TIER1_THRESHOLD: 35 → 40 (+14%)
- TIER1_PRODUCTION: 45 → 50 (+11%)
- TOTAL_PRODUCTION: 80 → 85 (+6%)
- Added TIER2_MINIMUM=20, TIER3_MINIMUM=8
- Production requires zero blockers
- Stricter source hash validation

**Impact:**
- Only 8.3% of contracts pass production standards
- 91% flagged for quality improvements
- Significantly reduced error probability in implementation

## Main Implementation

The core CQVR evaluator scripts are located in:
- `scripts/cqvr_evaluator_standalone.py` - Standalone evaluator with v2.1 severity
- `scripts/generate_enhanced_cqvr_dashboard.py` - Dashboard generator

## Generated On

These results were generated as part of the CQVR implementation and enhancement process (commits c886d9d through a4847c7).

---

For more information, see the main repository documentation or the implementation summary in this directory.
