# ⚠️  SENSITIVE - Calibration System Index ⚠️

**Classification**: SENSITIVE - PRODUCTION CALIBRATION DATA  
**COHORT**: COHORT_2024  
**Wave**: REFACTOR_WAVE_2024_12

## Quick Navigation

- **[README_SENSITIVE.md](README_SENSITIVE.md)** - Security requirements and usage guide
- **[COHORT_2024_intrinsic_calibration_loader_SENSITIVE.py](COHORT_2024_intrinsic_calibration_loader_SENSITIVE.py)** - Core implementation
- **[USAGE_EXAMPLE.py](USAGE_EXAMPLE.py)** - Runnable usage examples
- **[INDEX.md](INDEX.md)** - This file

## Purpose

This directory implements the **intrinsic calibration loader** for the F.A.R.F.A.N pipeline, providing:

1. **Method Quality Scoring**: Load and query @b scores (base layer quality metrics)
2. **Weighted Aggregation**: Compute `@b = 0.4*b_theory + 0.35*b_impl + 0.25*b_deploy`
3. **Status Management**: Handle excluded, pending, and computed methods
4. **Role-Based Fallbacks**: Provide role-specific default scores for unscored methods
5. **Production Governance**: Enforce quality gates and exclusion rules

## Core Components

### Implementation File
**COHORT_2024_intrinsic_calibration_loader_SENSITIVE.py**
- `IntrinsicCalibrationLoader`: Main loader class
- `CalibrationScore`: TypedDict for score structure
- Convenience functions: `get_score()`, `get_detailed_score()`, etc.
- Singleton pattern for efficient loading

### Documentation
**README_SENSITIVE.md**
- Security requirements and restrictions
- Usage patterns and examples
- Role-based minimum scores table
- Troubleshooting guide
- Governance and change control policies

### Examples
**USAGE_EXAMPLE.py**
- 8 runnable examples covering all use cases
- Can be executed: `python USAGE_EXAMPLE.py`
- Demonstrates scores, fallbacks, status checking, statistics

## Data Sources

### Configuration File
**Location**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json`

Contains:
- Base layer metadata and aggregation weights
- Role requirements with minimum scores
- Component weight specifications

### Evidence Traces
**Location**: `src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/evidence_traces/`

Contains:
- Individual JSON files per method (49 files currently)
- Method IDs in format: `module::Class::method`
- Calibration scores: `b_theory`, `b_impl`, `b_deploy`
- Status flags: `computed`, `excluded`, `pending`
- Detailed computation evidence

## API Reference

### Primary Functions

```python
# Load the calibration system (singleton)
loader = load_intrinsic_calibration()

# Get aggregate score with fallbacks
score = get_score(method_id, role="SCORE_Q", fallback=0.7)

# Get detailed score breakdown
details = get_detailed_score(method_id)  # Returns CalibrationScore or None

# Check method status
is_excluded(method_id)  # Returns bool
is_pending(method_id)   # Returns bool

# List and query
list_calibrated_methods()           # Returns list[str]
get_role_default(role)              # Returns float
get_calibration_statistics()        # Returns dict with stats
```

### Score Resolution Order

For `get_score(method_id, role, fallback)`:

1. **Excluded** → Return `0.0`
2. **Pending + fallback** → Return `fallback`
3. **Pending + role** → Return role default
4. **Pending** → Return `0.6`
5. **Computed** → Return computed score
6. **Unknown + fallback** → Return `fallback`
7. **Unknown + role** → Return role default
8. **Unknown** → Return `0.6`

## Integration Points

### Production Code
Reference implementation is also at:
```
src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/
  COHORT_2024_intrinsic_calibration_loader.py
```

Both implementations are identical. This sensitive copy provides:
- Clear labeling of sensitive nature
- Restricted access patterns
- Separated audit trail
- Development isolation

### Method Dispatcher
The calibration loader should integrate with method dispatchers to:
- Filter methods below role-specific minimums
- Exclude explicitly blacklisted methods
- Provide quality-weighted method selection
- Enforce governance compliance

### Quality Monitoring
Use statistics API for:
- Tracking score distributions over time
- Monitoring exclusion/pending rates
- Auditing role compliance
- Reporting calibration coverage

## Security Considerations

### Access Control
- Restrict write access to governance team only
- Log all configuration changes
- Audit evidence trace updates
- Version control all modifications

### Data Sensitivity
- Evidence traces contain production quality assessments
- Role defaults enforce quality gates
- Exclusions may indicate security/quality issues
- Scores influence production method selection

### Change Management
All changes require:
1. Technical justification
2. Governance approval
3. Audit trail documentation
4. Non-production testing
5. Staged rollout

## Metrics

Current system state (as of implementation):

- **Calibrated Methods**: 49 (from evidence traces)
- **Roles Defined**: 8 (SCORE_Q, INGEST_PDM, STRUCTURE, etc.)
- **Aggregation Weights**: 0.40 / 0.35 / 0.25 (theory/impl/deploy)
- **Default Fallback**: 0.6 (for unknown methods)
- **Score Range**: [0.0, 1.0]

## Quality Tiers

Score distribution thresholds:

| Tier | Score Range | Description |
|------|-------------|-------------|
| **Excellent** | ≥ 0.8 | Production-ready, best practices |
| **Good** | 0.6 - 0.8 | Production-acceptable, minor improvements |
| **Acceptable** | 0.4 - 0.6 | Needs improvement, limited use |
| **Poor** | < 0.4 | Requires refactoring or exclusion |

## Role-Based Minimums

| Role | Min Score | Focus Components |
|------|-----------|------------------|
| SCORE_Q | 0.7 | Theory, Implementation |
| INGEST_PDM | 0.6 | Implementation, Deployment |
| STRUCTURE | 0.6 | Implementation |
| EXTRACT | 0.6 | Implementation, Deployment |
| AGGREGATE | 0.7 | Theory, Implementation |
| REPORT | 0.6 | Implementation |
| META_TOOL | 0.7 | Theory, Implementation |
| TRANSFORM | 0.6 | Implementation |

## Testing

### Unit Tests
Should cover:
- Score computation with various weight combinations
- Fallback resolution order
- Exclusion/pending handling
- Role default lookups
- Edge cases (missing files, malformed JSON)

### Integration Tests
Should verify:
- Loading from actual configuration files
- Processing real evidence traces
- Singleton pattern behavior
- Statistics computation accuracy

### Validation Tests
Should check:
- All scores in [0.0, 1.0] range
- Weights sum to 1.0
- Role defaults ≥ 0.6
- Method IDs follow canonical format
- Status values are valid

## Troubleshooting

### Common Issues

**Loader returns 0.6 for all methods**
- Check evidence_traces directory exists
- Verify JSON files have correct structure
- Ensure method_id field is present

**Role defaults not applied**
- Verify role name matches exactly (case-sensitive)
- Check load() was called before get_score()
- Confirm role exists in configuration

**Unexpected exclusions**
- Review evidence trace status field
- Check excluded_methods set after load()
- Verify exclusion logic matches requirements

## Future Enhancements

Potential improvements:
1. **Caching**: Add LRU cache for frequently queried methods
2. **Validation**: Add schema validation for evidence traces
3. **Monitoring**: Add logging for score queries and fallbacks
4. **Updates**: Support hot-reload of configuration
5. **Reporting**: Generate calibration coverage reports
6. **Historical**: Track score evolution over time
7. **Alerts**: Notify on score degradation or exclusions

## Governance

### Approval Requirements
- Weight changes: Technical lead + governance approval
- Role default changes: Governance approval + audit trail
- Exclusion additions: Security review + documentation
- Implementation changes: Code review + testing

### Documentation Requirements
- All changes must update relevant documentation
- Security changes require security review notes
- Breaking changes require migration guide
- Deprecations require deprecation notice

## Support

For questions or issues:
1. Review README_SENSITIVE.md
2. Run USAGE_EXAMPLE.py to verify setup
3. Check evidence_traces for specific methods
4. Review configuration file for role requirements
5. Contact governance team for policy questions

---

**Classification**: SENSITIVE - PRODUCTION CALIBRATION DATA  
**Last Updated**: 2024-12-15T00:00:00+00:00  
**Cohort**: COHORT_2024
