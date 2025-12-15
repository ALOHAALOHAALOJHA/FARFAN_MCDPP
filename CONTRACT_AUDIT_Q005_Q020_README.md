# Contract Quality Verification Rubric (CQVR) Audit: Q005-Q020

## Overview

This audit system implements the **CQVR v2.0 (Contract Quality Verification Rubric)** to comprehensively evaluate executor contracts Q005 through Q020 in the F.A.R.F.A.N pipeline. The audit identifies critical gaps, assesses contract quality across three tiers, and generates actionable transformation requirements.

## Execution

```bash
./audit_contracts_Q005_Q020.py
```

## Output Files

### 1. `contract_audit_Q005_Q020.json`
Comprehensive audit report containing:
- **Per-contract breakdowns**: Individual audit results for each contract (Q005-Q020)
- **Tier 1/2/3 scores**: Detailed scoring across all three quality tiers
- **Identified gaps**: Specific issues with severity categorization
- **Triage decisions**: Strategic recommendations (REFORMULAR vs PARCHEAR)
- **Summary statistics**: Aggregate metrics across all audited contracts

### 2. `transformation_requirements_manifest.json`
Categorized transformation requirements by severity:
- **CRITICAL**: Schema mismatches, assembly orphans, signal threshold issues
- **HIGH**: Weak methodological depth, insufficient patterns
- **MEDIUM**: Documentation gaps, template issues

## CQVR v2.0 Rubric Structure (100 points)

### TIER 1: Critical Components (55 points) - BLOCKING

These are execution blockers. Failure in any component makes the contract inoperable.

#### A1. Identity-Schema Coherence [20 pts]
Validates perfect alignment between `identity` and `output_contract.schema.properties`:
- `question_id` match: 5 pts
- `policy_area_id` match: 5 pts
- `dimension_id` match: 5 pts
- `question_global` match: 3 pts
- `base_slot` match: 2 pts

**Threshold**: ≥15/20 for patchability; <15 requires complete reformulation

#### A2. Method-Assembly Alignment [20 pts]
Ensures `evidence_assembly` rules only reference existing `method_binding.provides`:
- 100% sources exist in provides: 10 pts
- >80% provides are used: 5 pts
- `method_count` accuracy: 3 pts
- No invented namespaces: 2 pts

**Threshold**: ≥12/20 for patchability; <12 requires assembly reformulation

#### A3. Signal Integrity [10 pts]
Validates signal configuration:
- `minimum_signal_threshold > 0` (BLOCKING): 5 pts
- Well-formed `mandatory_signals`: 3 pts
- Valid aggregation strategy: 2 pts

**Threshold**: ≥5/10 (threshold MUST be > 0)

#### A4. Output Schema Validation [5 pts]
Ensures schema completeness:
- All `required` fields have definitions: 3-5 pts
- Valid type declarations: 0-2 pts

**Threshold**: ≥3/5 for patchability

### TIER 2: Functional Components (30 points)

Affect quality and precision but don't block execution.

#### B1. Pattern Coverage [10 pts]
- Pattern completeness: 5 pts
- Valid confidence weights (0-1): 3 pts
- Unique, well-formed IDs: 2 pts

**Suggested threshold**: ≥6/10

#### B2. Method Specificity [10 pts]
- Non-generic step descriptions: 6 pts
- Realistic complexity estimates: 2 pts
- Documented assumptions: 2 pts

**Suggested threshold**: ≥5/10

#### B3. Validation Rules [10 pts]
- Coverage of critical expected_elements: 5 pts
- Balanced must/should constraints: 3 pts
- Well-defined failure_contract: 2 pts

**Suggested threshold**: ≥6/10

### TIER 3: Quality Components (15 points)

Nice-to-have features that improve maintainability and UX.

#### C1. Documentation Quality [5 pts]
- Non-boilerplate paradigm descriptions: 2 pts
- Specific justifications: 2 pts
- External references: 1 pt

#### C2. Human-Readable Template [5 pts]
- Correct question references: 3 pts
- Valid placeholders: 2 pts

#### C3. Metadata Completeness [5 pts]
- SHA256 `contract_hash`: 2 pts
- ISO timestamp: 1 pt
- Schema validation reference: 1 pt
- Semantic versioning: 1 pt

## Triage Decision Matrix

| Tier 1 Score | Tier 2 Score | Total Score | Decision | Action |
|--------------|--------------|-------------|----------|--------|
| <35/55 (63%) | - | - | **REFORMULAR** | Regenerate from monolith |
| 35-44/55 | <15/30 | <60 | **REFORMULAR** | Regenerate broken components |
| 35-44/55 | ≥15/30 | 60-69 | **PARCHEAR_MAJOR** | Fix assembly + schema |
| ≥45/55 (82%) | ≥20/30 | ≥70 | **PARCHEAR_MINOR** | Point adjustments |
| ≥50/55 | ≥25/30 | ≥85 | **PRODUCCIÓN** | Ready for deployment |

## Specific Triage Decisions

### REFORMULAR_COMPLETO
Multiple critical blockers (≥2). Contract must be regenerated from scratch using canonical questionnaire.

### REFORMULAR_ASSEMBLY
Assembly rules reference non-existent provides. Regenerate `evidence_assembly` section aligned with actual `method_binding`.

### REFORMULAR_SCHEMA
Identity-schema mismatch. Rebuild `output_contract.schema` from `identity` fields.

### PARCHEAR_CRITICO
Single critical blocker. Targeted fix possible without full regeneration.

### PARCHEAR_MAJOR
Tier 1 passes but functional components weak. Fix assembly, schema, and validation rules.

### PARCHEAR_MINOR
High quality overall. Only minor adjustments needed.

### PARCHEAR_DOCS
Good critical components but weak documentation. Improve methodological_depth.

### PARCHEAR_PATTERNS
Good critical components but insufficient pattern coverage. Add more regex patterns.

## Gap Categories

### CRITICAL Severity
- **schema_mismatch**: Identity and output schema fields inconsistent
- **assembly_orphans**: Assembly rules reference methods that don't exist
- **signal_threshold_zero**: `minimum_signal_threshold = 0` with mandatory signals

### HIGH Severity
- **weak_methodological_depth**: Generic or boilerplate method descriptions
- **insufficient_patterns**: Too few patterns for effective matching

### MEDIUM Severity
- **documentation_gaps**: Missing or inadequate human-readable templates
- **template_issues**: Incorrect references or missing placeholders

## Audit Report Structure

```json
{
  "audit_metadata": {
    "timestamp": "ISO 8601 timestamp",
    "rubric_version": "CQVR v2.0",
    "contract_range": "Q005-Q020",
    "total_contracts": 16
  },
  "per_contract_audits": {
    "Q005": {
      "question_id": "Q005",
      "contract_version": "3.0.0",
      "audit_timestamp": "ISO 8601 timestamp",
      "tier1_scores": { ... },
      "tier2_scores": { ... },
      "tier3_scores": { ... },
      "tier1_total": 50,
      "tier2_total": 25,
      "tier3_total": 12,
      "total_score": 87,
      "tier1_percentage": 90.9,
      "tier2_percentage": 83.3,
      "tier3_percentage": 80.0,
      "overall_percentage": 87.0,
      "triage_decision": "PARCHEAR_MINOR",
      "gaps_identified": [ ... ],
      "verdict": {
        "status": "PRODUCTION",
        "tier1_threshold": "≥35/55",
        "total_threshold": "≥80/100 for production"
      }
    },
    "Q006": { ... }
  },
  "summary_statistics": {
    "contracts_audited": 16,
    "average_total_score": 75.3,
    "average_tier1_score": 42.1,
    "min_score": 58,
    "max_score": 89,
    "production_ready": 8,
    "patchable": 6,
    "requires_reformulation": 2,
    "requires_major_work": 0,
    "verdict_distribution": { ... },
    "triage_distribution": { ... }
  },
  "transformation_manifest": {
    "CRITICAL": {
      "count": 12,
      "description": "CRITICAL: schema mismatches, assembly orphans, signal threshold zero",
      "items": [ ... ]
    },
    "HIGH": { ... },
    "MEDIUM": { ... }
  }
}
```

## Transformation Manifest Structure

```json
{
  "CRITICAL": {
    "count": 12,
    "description": "CRITICAL: schema mismatches, assembly orphans, signal threshold zero",
    "items": [
      {
        "question_id": "Q007",
        "category": "assembly_orphans",
        "description": "Assembly rules reference non-existent provides: ['text_mining.critical_links', 'causal_extraction.goals']",
        "score": 8,
        "threshold": 12,
        "details": {
          "orphan_sources": ["text_mining.critical_links", "causal_extraction.goals"]
        }
      }
    ]
  },
  "HIGH": { ... },
  "MEDIUM": { ... }
}
```

## Interpretation Guide

### Production Ready (Status: PRODUCTION)
- Total score ≥80/100
- Tier 1 ≥45/55
- No critical blockers
- **Action**: Deploy to production (after minor patches if any)

### Patchable (Status: PATCHABLE)
- Total score 60-79/100
- Tier 1 ≥35/55
- Fixable issues only
- **Action**: Apply patches, then revalidate

### Requires Reformulation (Status: REQUIRES_REFORMULATION)
- Tier 1 <35/55
- Multiple critical blockers
- **Action**: Regenerate contract from canonical questionnaire

### Requires Major Work (Status: REQUIRES_MAJOR_WORK)
- Total score <60/100
- Significant gaps across multiple tiers
- **Action**: Major refactoring needed

## Integration with CI/CD

The audit can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/contract-validation.yml
name: Contract Quality Check

on:
  push:
    paths:
      - 'src/canonic_phases/**/executor_contracts/**/*.json'

jobs:
  validate-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run CQVR Audit
        run: |
          python audit_contracts_Q005_Q020.py
      
      - name: Upload Audit Report
        uses: actions/upload-artifact@v3
        with:
          name: contract-audit-report
          path: |
            contract_audit_Q005_Q020.json
            transformation_requirements_manifest.json
      
      - name: Check Quality Threshold
        run: |
          # Parse JSON and check if any contracts require reformulation
          if grep -q "REQUIRES_REFORMULATION" contract_audit_Q005_Q020.json; then
            echo "❌ Some contracts require reformulation"
            exit 1
          fi
```

## Usage Examples

### Run Full Audit
```bash
./audit_contracts_Q005_Q020.py
```

### Extract Critical Issues Only
```bash
./audit_contracts_Q005_Q020.py
python -c "import json; d=json.load(open('transformation_requirements_manifest.json')); print(json.dumps(d['CRITICAL'], indent=2))"
```

### Check Specific Contract
```python
import json

with open('contract_audit_Q005_Q020.json') as f:
    audit = json.load(f)

q010_audit = audit['per_contract_audits']['Q010']
print(f"Q010 Score: {q010_audit['total_score']}/100")
print(f"Triage: {q010_audit['triage_decision']}")
```

## References

- **CQVR Specification**: `src/canonic_phases/Phase_two/json_files_phase_two/executor_contracts/specialized/# Rúbrica CQVR v2.py`
- **Q001 Evaluation Report**: `Q001_CQVR_EVALUATION_REPORT.md`
- **Q002 Evaluation Report**: `Q002_CQVR_EVALUATION_REPORT.md`

## Maintenance

To update the audit for new contracts:

1. Modify `question_ids` range in `audit_all_contracts()` method
2. Update `audit_metadata.total_contracts` accordingly
3. Adjust thresholds in rubric methods if scoring criteria change
4. Re-run audit and verify results

## Exit Codes

- `0`: Audit completed successfully, all contracts acceptable
- `1`: Audit completed but some contracts require reformulation
- `2`: Audit failed due to critical error
