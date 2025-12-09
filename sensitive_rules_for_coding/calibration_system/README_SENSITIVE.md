# ⚠️  SENSITIVE - Calibration System ⚠️

**Classification**: SENSITIVE - PRODUCTION CALIBRATION DATA  
**COHORT**: COHORT_2024  
**Wave**: REFACTOR_WAVE_2024_12  
**Created**: 2024-12-15T00:00:00+00:00

## Overview

This directory contains **SENSITIVE** calibration system components for the F.A.R.F.A.N mechanistic policy analysis pipeline. These files control production method selection, quality gates, and governance compliance.

## Contents

### Core Implementation
- `COHORT_2024_intrinsic_calibration_loader_SENSITIVE.py` - Production calibration loader with role-based scoring

### What This System Does

The intrinsic calibration loader:

1. **Loads Method Quality Scores (@b scores)**
   - Reads from `COHORT_2024_intrinsic_calibration.json`
   - Processes evidence traces from `evidence_traces/` directory
   - Computes weighted aggregates using canonical weights

2. **Implements Weighted Aggregation**
   - `b_theory` (40%): Conceptual and methodological soundness
   - `b_impl` (35%): Code implementation quality  
   - `b_deploy` (25%): Operational stability and reliability
   - Formula: `@b = 0.4*b_theory + 0.35*b_impl + 0.25*b_deploy`

3. **Manages Method Status**
   - **Excluded**: Methods explicitly removed from production (score = 0.0)
   - **Pending**: Methods awaiting calibration (uses fallbacks)
   - **Computed**: Methods with evidence-based scores
   - **Unknown**: Methods without calibration data (uses role defaults)

4. **Provides Fallback Mechanisms**
   - Role-based minimum scores (e.g., SCORE_Q: 0.7, INGEST_PDM: 0.6)
   - Explicit fallback values per query
   - Global default: 0.6 for unscored methods

## Security and Sensitivity

### Why This Is Sensitive

1. **Production Decision Making**: These scores determine which methods are used in production analysis
2. **Quality Gates**: Role-based minimums enforce quality standards across the pipeline
3. **Exclusion Logic**: Excluded methods are blocked from execution
4. **Governance Compliance**: Scores track compliance with methodological standards

### Security Requirements

**DO NOT**:
- Modify aggregation weights (0.4/0.35/0.25) without governance approval
- Change role-based defaults without audit trail documentation
- Remove exclusion/pending handling logic
- Expose raw evidence traces to untrusted code
- Commit evidence trace files to public repositories
- Share calibration scores outside the development team

**DO**:
- Maintain audit trail for all configuration changes
- Document rationale for role default modifications
- Keep evidence traces in secure local directories
- Use version control for loader code changes
- Test fallback logic thoroughly before deployment

## Usage

### Basic Usage

```python
from sensitive_rules_for_coding.calibration_system.COHORT_2024_intrinsic_calibration_loader_SENSITIVE import (
    load_intrinsic_calibration,
    get_score,
    get_detailed_score,
)

# Get aggregate score for a method
score = get_score("farfan_pipeline.analysis.derek_beach::CausalExtractor::extract_mechanism")
print(f"Method quality score: {score:.3f}")

# Get detailed breakdown
details = get_detailed_score("farfan_pipeline.analysis.derek_beach::CausalExtractor::extract_mechanism")
if details:
    print(f"Theory: {details['b_theory']:.3f}")
    print(f"Implementation: {details['b_impl']:.3f}")
    print(f"Deployment: {details['b_deploy']:.3f}")
    print(f"Aggregate: {details['b_aggregate']:.3f}")
```

### Role-Based Fallback

```python
# Use role-based default for unscored method
score = get_score(
    "new_module::NewClass::new_method",
    role="SCORE_Q",  # Requires min 0.7
)
# Returns 0.7 (role default) if method not scored
```

### Checking Method Status

```python
from sensitive_rules_for_coding.calibration_system.COHORT_2024_intrinsic_calibration_loader_SENSITIVE import (
    is_excluded,
    is_pending,
)

if is_excluded(method_id):
    print("Method is excluded from production")
elif is_pending(method_id):
    print("Method awaits calibration")
```

### Statistics and Monitoring

```python
from sensitive_rules_for_coding.calibration_system.COHORT_2024_intrinsic_calibration_loader_SENSITIVE import (
    get_calibration_statistics,
)

stats = get_calibration_statistics()
print(f"Total calibrated methods: {stats['total_methods']}")
print(f"Excluded methods: {stats['excluded_methods']}")
print(f"Pending methods: {stats['pending_methods']}")
print(f"Score distribution: {stats['score_distribution']}")
```

## Integration with Production Code

For production usage, the loader is also available at:

```python
from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration.COHORT_2024_intrinsic_calibration_loader import (
    IntrinsicCalibrationLoader,
    load_intrinsic_calibration,
    get_score,
)
```

Both implementations are identical. The sensitive copy exists for:
1. Clear labeling of sensitive nature
2. Restricted access control
3. Audit trail separation
4. Development vs. production separation

## Role-Based Minimum Scores

Extracted from `COHORT_2024_intrinsic_calibration.json`:

| Role | Min Score | Critical Components |
|------|-----------|---------------------|
| SCORE_Q | 0.7 | b_theory, b_impl |
| INGEST_PDM | 0.6 | b_impl, b_deploy |
| STRUCTURE | 0.6 | b_impl |
| EXTRACT | 0.6 | b_impl, b_deploy |
| AGGREGATE | 0.7 | b_theory, b_impl |
| REPORT | 0.6 | b_impl |
| META_TOOL | 0.7 | b_theory, b_impl |
| TRANSFORM | 0.6 | b_impl |

## Evidence Trace Structure

Evidence traces in `evidence_traces/` directory contain:

```json
{
  "method_id": "module::Class::method",
  "calibration": {
    "b_theory": 0.75,
    "b_impl": 0.82,
    "b_deploy": 0.68,
    "status": "computed"
  },
  "evidence": {
    "triage_decision": { ... },
    "b_theory_computation": { ... },
    "b_impl_computation": { ... },
    "b_deploy_computation": { ... }
  }
}
```

## Governance

### Change Control

All changes to this system require:
1. Technical justification
2. Governance approval
3. Audit trail entry
4. Testing in non-production environment
5. Staged rollout to production

### Audit Trail

Changes must be documented in:
- Git commit messages with `[CALIBRATION]` prefix
- Change log entries with rationale
- Review by at least one governance team member

### Quality Assurance

Before deploying changes:
- Run full test suite
- Verify fallback logic with edge cases
- Test role-based defaults for all roles
- Validate score distributions
- Check exclusion/pending handling

## Troubleshooting

### Common Issues

**Loader returns 0.6 for all methods**:
- Check that evidence_traces/ directory exists and contains JSON files
- Verify calibration_path points to correct JSON file
- Ensure evidence traces have correct structure

**Unexpected exclusions**:
- Check evidence trace status field
- Verify exclusion logic in loader
- Review excluded_methods set

**Role defaults not working**:
- Verify role name matches exactly (case-sensitive)
- Check role_requirements in calibration JSON
- Ensure load() was called before get_score()

## Support

For issues or questions:
1. Review this README
2. Check production implementation at `capaz_calibration_parmetrization/calibration/`
3. Review evidence traces for specific methods
4. Contact governance team for policy questions

---

**REMINDER**: This system controls production method selection. Handle with care.
