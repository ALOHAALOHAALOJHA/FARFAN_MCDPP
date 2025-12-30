# Contract Audit System Index: Q005-Q020

## Overview

This directory contains a comprehensive Contract Quality Verification Rubric (CQVR) v2.0 audit system for evaluating executor contracts Q005 through Q020 in the F.A.R.F.A.N mechanistic policy pipeline.

## Quick Start

```bash
# 1. Run the audit
./audit_contracts_Q005_Q020.py

# 2. View summary
python analyze_audit_results.py --summary

# 3. Check critical issues
python analyze_audit_results.py --critical-only

# 4. Review specific contract
python analyze_audit_results.py --contract Q010
```

## File Structure

### Audit Tools

| File | Purpose | Usage |
|------|---------|-------|
| `audit_contracts_Q005_Q020.py` | Main CQVR audit engine | `./audit_contracts_Q005_Q020.py` |
| `analyze_audit_results.py` | Results analysis utility | `python analyze_audit_results.py --summary` |

### Documentation

| File | Purpose | Audience |
|------|---------|----------|
| `CONTRACT_AUDIT_Q005_Q020_README.md` | Complete audit system documentation | Engineers, QA |
| `TRANSFORMATION_REQUIREMENTS_GUIDE.md` | Fix guide for identified issues | Developers |
| `CONTRACT_AUDIT_INDEX.md` | This file - navigation index | All users |

### Generated Outputs

| File | Content | Format |
|------|---------|--------|
| `contract_audit_Q005_Q020.json` | Full audit report with per-contract breakdowns | JSON |
| `transformation_requirements_manifest.json` | Categorized issues by severity | JSON |
| `audit_summary.csv` | Exportable spreadsheet format | CSV |

## Audit System Components

### 1. CQVR Validator (`audit_contracts_Q005_Q020.py`)

Implements the CQVR v2.0 rubric with:
- **Tier 1 (55 pts)**: Critical components - execution blockers
- **Tier 2 (30 pts)**: Functional components - quality impactors
- **Tier 3 (15 pts)**: Quality components - UX enhancers

**Key Methods**:
- `audit_all_contracts()`: Main entry point
- `audit_contract()`: Single contract evaluation
- `_score_identity_schema_coherence()`: A1 scoring
- `_score_method_assembly_alignment()`: A2 scoring
- `_triage_decision()`: Strategic recommendation engine
- `_generate_transformation_manifest()`: Issue categorization

### 2. Results Analyzer (`analyze_audit_results.py`)

Post-audit analysis with multiple views:
- **Summary**: Executive overview with statistics
- **Critical Only**: Focus on blocking issues
- **Contract Detail**: Deep dive into specific contract
- **Worst Contracts**: Bottom N performers
- **CSV Export**: Spreadsheet-compatible format

**Usage Examples**:
```bash
# Executive summary
python analyze_audit_results.py --summary

# Critical issues only
python analyze_audit_results.py --critical-only

# Single contract deep dive
python analyze_audit_results.py --contract Q015

# Bottom 5 performers
python analyze_audit_results.py --worst-contracts 5

# Export to spreadsheet
python analyze_audit_results.py --export-csv results.csv
```

## Scoring System

### Tier 1: Critical Components (55 points)

| Component | Points | Threshold | Impact if Failed |
|-----------|--------|-----------|------------------|
| A1. Identity-Schema Coherence | 20 | ≥15 | Contract validation fails |
| A2. Method-Assembly Alignment | 20 | ≥12 | Evidence collection breaks |
| A3. Signal Integrity | 10 | ≥5 | Invalid data accepted |
| A4. Output Schema Validation | 5 | ≥3 | Results rejected |

### Tier 2: Functional Components (30 points)

| Component | Points | Threshold | Impact if Failed |
|-----------|--------|-----------|------------------|
| B1. Pattern Coverage | 10 | ≥6 | Low extraction rate |
| B2. Method Specificity | 10 | ≥5 | Poor interpretability |
| B3. Validation Rules | 10 | ≥6 | Weak verification |

### Tier 3: Quality Components (15 points)

| Component | Points | Impact if Failed |
|-----------|--------|------------------|
| C1. Documentation Quality | 5 | Harder maintenance |
| C2. Human-Readable Template | 5 | Poor UX |
| C3. Metadata Completeness | 5 | Limited traceability |

## Triage Decision Types

| Decision | Tier 1 Score | Total Score | Action Required |
|----------|--------------|-------------|-----------------|
| `REFORMULAR_COMPLETO` | <35/55 | Any | Regenerate from scratch |
| `REFORMULAR_ASSEMBLY` | <35/55 | Any | Rebuild assembly rules |
| `REFORMULAR_SCHEMA` | <35/55 | Any | Rebuild output schema |
| `PARCHEAR_CRITICO` | <35/55 | Any | Fix single critical blocker |
| `PARCHEAR_MAJOR` | 35-44/55 | 60-69 | Fix multiple components |
| `PARCHEAR_MINOR` | ≥45/55 | ≥70 | Minor adjustments |
| `PRODUCCIÓN` | ≥50/55 | ≥80 | Ready for deployment |

## Issue Severity Categories

### 🔴 CRITICAL (Blocking)
- **schema_mismatch**: Identity ≠ output schema
- **assembly_orphans**: References to non-existent methods
- **signal_threshold_zero**: Threshold = 0 with mandatory signals

**Impact**: Blocks deployment, execution fails

### 🟠 HIGH (Degraded Quality)
- **weak_methodological_depth**: Generic method descriptions
- **insufficient_patterns**: <5 patterns or poor coverage

**Impact**: Reduced accuracy, harder debugging

### 🟡 MEDIUM (UX Impact)
- **documentation_gaps**: Missing template elements
- **template_issues**: Incorrect references/placeholders

**Impact**: Poor user experience

## Workflow

### 1. Initial Audit
```bash
./audit_contracts_Q005_Q020.py
```

**Outputs**:
- `contract_audit_Q005_Q020.json`
- `transformation_requirements_manifest.json`

### 2. Analysis Phase
```bash
# Overview
python analyze_audit_results.py --summary

# Identify worst performers
python analyze_audit_results.py --worst-contracts 5

# Check critical blockers
python analyze_audit_results.py --critical-only
```

### 3. Remediation Phase

Follow `TRANSFORMATION_REQUIREMENTS_GUIDE.md`:

**Critical Issues** (do first):
```bash
# Fix signal thresholds
# Fix assembly orphans
# Fix schema mismatches
```

**High/Medium Issues** (do next):
```bash
# Improve patterns
# Enhance documentation
# Update templates
```

### 4. Verification
```bash
# Re-run audit
./audit_contracts_Q005_Q020.py

# Compare results
python analyze_audit_results.py --summary
```

## Integration Points

### CI/CD Pipeline
```yaml
- name: Contract Quality Gate
  run: |
    ./audit_contracts_Q005_Q020.py
    if [ $? -ne 0 ]; then
      echo "Contract quality below threshold"
      exit 1
    fi
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
if git diff --cached --name-only | grep -q "executor_contracts.*\.json"; then
    ./audit_contracts_Q005_Q020.py
fi
```

### Manual Review
```bash
# Before PR
./audit_contracts_Q005_Q020.py
python analyze_audit_results.py --summary > audit_summary.txt
# Include audit_summary.txt in PR description
```

## Reference Materials

### CQVR Specification
Located at: `src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/# Rúbrica CQVR v2.py`

Contains:
- Complete rubric definition with weights
- Scoring formulas and thresholds
- Triage decision logic
- Contract generation guidelines

### Example Evaluations
- `Q001_CQVR_EVALUATION_REPORT.md`: High-quality contract (83/100)
- `Q002_CQVR_EVALUATION_REPORT.md`: Post-correction success (85/100)

## Troubleshooting

### Audit Script Issues

**Problem**: `Contract file not found`
```bash
# Verify path
ls src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/Q{005..020}.v3.json
```

**Problem**: `Audit failed with error`
```bash
# Check JSON validity
python -m json.tool src/.../Q010.v3.json
```

### Analysis Script Issues

**Problem**: `Audit file not found`
```bash
# Run audit first
./audit_contracts_Q005_Q020.py

# Or specify custom path
python analyze_audit_results.py --audit-file custom_audit.json --summary
```

## Performance Benchmarks

**Audit Execution**:
- 16 contracts: ~2-5 seconds
- Per-contract analysis: ~0.1-0.3 seconds
- Manifest generation: ~0.1 seconds

**Analysis Queries**:
- Summary generation: <0.1 seconds
- Contract detail: <0.1 seconds
- CSV export: <0.2 seconds

## Maintenance

### Updating Rubric Thresholds

Edit `audit_contracts_Q005_Q020.py`:
```python
# Example: Change Tier 1 threshold
def _triage_decision(self, ...):
    if tier1_total < 40:  # Changed from 35
        # ...
```

### Adding New Checks

1. Add scoring method:
```python
def _score_new_component(self, contract: Dict) -> int:
    # Your logic here
    return score
```

2. Include in tier scores:
```python
tier1_scores = {
    "A1_identity_schema": self._score_identity_schema_coherence(contract),
    # ... existing checks ...
    "A5_new_check": self._score_new_component(contract)
}
```

3. Update documentation

### Extending to New Contracts

Modify `audit_all_contracts()`:
```python
question_ids = [f"Q{i:03d}" for i in range(5, 31)]  # Changed from range(5, 21)
```

Update metadata:
```python
"total_contracts": 26  # Changed from 16
```

## Support and Contributions

### Reporting Issues
1. Run audit with full output
2. Attach generated JSON files
3. Include specific contract IDs
4. Note expected vs actual behavior

### Suggesting Improvements
1. Review CQVR specification
2. Propose threshold adjustments with justification
3. Include sample contracts demonstrating issue
4. Consider backward compatibility

## Version History

- **v1.0** (Current): Initial CQVR v2.0 implementation for Q005-Q020
  - Comprehensive 3-tier scoring
  - Automated triage decisions
  - Transformation manifest generation
  - Analysis utility suite

## License and Attribution

Part of the F.A.R.F.A.N mechanistic policy pipeline.
See repository root for license information.
