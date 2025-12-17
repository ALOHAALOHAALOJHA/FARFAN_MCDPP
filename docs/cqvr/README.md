# CQVR: Contract Quality Verification and Remediation System

## Overview

The Contract Quality Verification and Remediation (CQVR) system is a comprehensive quality assurance framework for executor contracts in the F.A.R.F.A.N pipeline. CQVR v2.0 implements a three-tier scoring rubric (100 points total) to evaluate contract quality, make triage decisions, and guide remediation efforts.

## Purpose

CQVR ensures that all executor contracts meet production-quality standards before deployment by:

1. **Evaluating** contract quality across critical, functional, and quality dimensions
2. **Triaging** contracts into production-ready, patchable, or requiring reformulation
3. **Remediating** identified issues through automated structural corrections
4. **Validating** that corrections meet production thresholds

## Three-Tier Scoring System

CQVR evaluates contracts using a 100-point rubric divided into three tiers:

### Tier 1: Critical Components (55 points)
Foundation elements required for contract execution:
- **A1. Identity-Schema Coherence (20 pts)**: Identity fields match output schema constants
- **A2. Method-Assembly Alignment (20 pts)**: Method provides align with assembly sources
- **A3. Signal Requirements (10 pts)**: Signal thresholds and mandatory signals properly configured
- **A4. Output Schema (5 pts)**: Required fields defined in properties

### Tier 2: Functional Components (30 points)
Operational capabilities for evidence processing:
- **B1. Pattern Coverage (10 pts)**: Patterns cover expected elements with valid confidence weights
- **B2. Method Specificity (10 pts)**: Methods have specific (non-boilerplate) technical approaches
- **B3. Validation Rules (10 pts)**: Validation rules cover required elements with failure contracts

### Tier 3: Quality Components (15 points)
Documentation and metadata for maintainability:
- **C1. Documentation Quality (5 pts)**: Epistemological foundations are specific, not boilerplate
- **C2. Human Template (5 pts)**: Templates reference identity and include dynamic placeholders
- **C3. Metadata Completeness (5 pts)**: Contract hash, timestamps, and provenance chain complete

## Decision Matrix

CQVR makes triage decisions based on tier scores and blocker count:

| Tier 1 Score | Total Score | Blockers | Decision |
|--------------|-------------|----------|----------|
| ≥ 45/55 | ≥ 80/100 | 0 | **PRODUCCION** - Ready for deployment |
| ≥ 35/55 | ≥ 70/100 | ≤ 2 | **PARCHEAR** - Apply recommended patches |
| < 35/55 | Any | Any | **REFORMULAR** - Requires substantial rework |
| ≥ 35/55 | < 70/100 | > 2 | **REFORMULAR** - Too many blockers |

## Remediation Workflow

1. **Audit Contract**: Run CQVR validator to score contract and identify gaps
2. **Triage Decision**: Determine if contract can be patched or needs reformulation
3. **Apply Corrections**: For patchable contracts, apply structural corrections:
   - Fix identity-schema coherence
   - Align method-assembly sources
   - Set signal thresholds > 0
   - Add missing schema properties
4. **Validate Fixes**: Re-run CQVR to verify corrections met production threshold
5. **Generate Report**: Document pre/post scores, transformations, and decision rationale

## Quick Start

```python
from contract_validator_cqvr import CQVRValidator

# Load contract
with open('contract.json') as f:
    contract = json.load(f)

# Run CQVR validation
validator = CQVRValidator()
decision = validator.validate_contract(contract)

# Check results
if decision.is_production_ready():
    print(f"✅ Production ready: {decision.score.total_score}/100")
elif decision.can_be_patched():
    print(f"⚠️ Patchable: {len(decision.recommendations)} fixes needed")
else:
    print(f"❌ Requires reformulation: {len(decision.blockers)} blockers")
```

## Documentation Structure

- **[Scoring System](scoring-system.md)**: Detailed scoring rubric with examples
- **[Decision Matrix](decision-matrix.md)**: Triage logic and decision rules
- **[API Reference](api-reference.md)**: Python API documentation
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

## Key Features

### Automated Quality Assessment
- Evaluates 10 contract components across 3 tiers
- Identifies blockers, warnings, and improvement recommendations
- Generates detailed score breakdowns with rationale

### Intelligent Triage
- Makes production/patch/reformulate decisions based on score thresholds
- Considers both tier scores and blocker severity
- Provides actionable remediation guidance

### Structural Corrections
- Automatically fixes identity-schema mismatches
- Aligns method provides with assembly sources
- Sets signal thresholds to prevent zero-strength signals
- Adds missing schema properties

### Provenance Tracking
- Documents pre/post transformation scores
- Tracks all applied corrections
- Maintains audit trail for compliance

## Use Cases

### Contract Development
Use CQVR during contract authoring to ensure quality from the start:
```bash
python -m contract_validator_cqvr audit contract_draft.json
```

### CI/CD Pipeline Integration
Add CQVR validation to your CI pipeline:
```yaml
- name: Validate Contracts
  run: python -m contract_validator_cqvr validate contracts/*.json --min-score 80
```

### Contract Migration
Use CQVR to audit and transform existing contracts:
```bash
python transform_contract.py Q001 --apply-fixes --validate
```

### Quality Monitoring
Track contract quality metrics over time:
```bash
python -m contract_validator_cqvr report contracts/ --output metrics.json
```

## Version History

- **v2.0** (Current): Three-tier rubric with automated remediation
- **v1.0**: Initial validation framework

## Related Systems

- **Phase 2 Executor Contracts**: Validated by CQVR
- **Questionnaire Monolith**: Source of truth for identity fields
- **Evidence Assembly**: Consumes method provides validated by CQVR
- **Signal Requirements**: Threshold validation prevents zero-strength signals

## Support

For issues or questions:
1. Check [Troubleshooting Guide](troubleshooting.md)
2. Review [API Reference](api-reference.md)
3. Examine [Scoring System](scoring-system.md) for rubric details
4. See [Example Reports](../../Q001_CQVR_EVALUATION_REPORT.md) for reference
