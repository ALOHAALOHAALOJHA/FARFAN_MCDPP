# ⚠️  Intrinsic Calibration Loader - Quick Reference ⚠️

**SENSITIVE - PRODUCTION CALIBRATION SYSTEM**

## One-Liner Import

```python
from sensitive_rules_for_coding.calibration_system import get_score, get_detailed_score
```

## Common Operations

### Get Method Score

```python
# Basic lookup (returns aggregate @b score)
score = get_score("farfan_pipeline.analysis.derek_beach::CausalExtractor::extract")
# Returns: float [0.0, 1.0]

# With role-based fallback
score = get_score("new.method::Class::func", role="SCORE_Q")
# Returns: 0.7 (role default) if method not scored

# With explicit fallback
score = get_score("new.method::Class::func", fallback=0.8)
# Returns: 0.8 if method not scored
```

### Get Detailed Breakdown

```python
from sensitive_rules_for_coding.calibration_system import get_detailed_score

details = get_detailed_score(method_id)
if details:
    print(f"Theory:     {details['b_theory']:.3f}")
    print(f"Impl:       {details['b_impl']:.3f}")
    print(f"Deploy:     {details['b_deploy']:.3f}")
    print(f"Aggregate:  {details['b_aggregate']:.3f}")
    print(f"Status:     {details['status']}")
# Returns: CalibrationScore | None
```

### Check Status

```python
from sensitive_rules_for_coding.calibration_system import is_excluded, is_pending

if is_excluded(method_id):
    # Method blacklisted, score = 0.0
    pass
elif is_pending(method_id):
    # Method awaiting calibration, uses fallback
    pass
else:
    # Method has computed score
    pass
```

### Query System

```python
from sensitive_rules_for_coding.calibration_system import (
    list_calibrated_methods,
    get_role_default,
    get_calibration_statistics
)

# List all calibrated methods
methods = list_calibrated_methods()  # Returns: list[str]

# Get role minimum
min_score = get_role_default("SCORE_Q")  # Returns: 0.7

# Get statistics
stats = get_calibration_statistics()
# Returns: dict with total_methods, excluded_methods, pending_methods, 
#          role_defaults, weights, score_distribution
```

## Score Formula

```
@b = 0.40 × b_theory + 0.35 × b_impl + 0.25 × b_deploy
```

Where:
- **b_theory**: Conceptual soundness (statistical validity, logical consistency, assumptions)
- **b_impl**: Implementation quality (tests, types, error handling, docs)
- **b_deploy**: Operational stability (validation runs, stability coefficient, failure rate)

## Fallback Resolution

For `get_score(method_id, role, fallback)`:

1. **Excluded** → `0.0`
2. **Pending + fallback** → `fallback`
3. **Pending + role** → role default
4. **Pending** → `0.6`
5. **Computed** → computed score
6. **Unknown + fallback** → `fallback`
7. **Unknown + role** → role default
8. **Unknown** → `0.6`

## Role Defaults

| Role | Min Score |
|------|-----------|
| SCORE_Q | 0.7 |
| AGGREGATE | 0.7 |
| META_TOOL | 0.7 |
| INGEST_PDM | 0.6 |
| STRUCTURE | 0.6 |
| EXTRACT | 0.6 |
| REPORT | 0.6 |
| TRANSFORM | 0.6 |

## Score Tiers

| Score | Tier | Meaning |
|-------|------|---------|
| ≥ 0.8 | Excellent | Production-ready |
| 0.6-0.8 | Good | Acceptable for production |
| 0.4-0.6 | Acceptable | Needs improvement |
| < 0.4 | Poor | Requires refactoring |
| 0.0 | Excluded | Blacklisted |

## Method ID Format

```
module::Class::method_name
```

Example:
```
farfan_pipeline.analysis.derek_beach::CausalExtractor::extract_mechanism
```

## Common Patterns

### Batch Scoring

```python
from sensitive_rules_for_coding.calibration_system import get_score

method_ids = [...]  # List of method IDs
scores = {mid: get_score(mid) for mid in method_ids}
```

### Quality Gate

```python
from sensitive_rules_for_coding.calibration_system import get_score, get_role_default

role = "SCORE_Q"
min_required = get_role_default(role)
score = get_score(method_id, role=role)

if score < min_required:
    raise QualityGateError(f"Method score {score} below minimum {min_required}")
```

### Method Selection

```python
from sensitive_rules_for_coding.calibration_system import get_score, is_excluded

candidates = [...]  # List of method IDs

# Filter excluded and low-quality methods
eligible = [
    mid for mid in candidates
    if not is_excluded(mid) and get_score(mid) >= 0.6
]

# Select highest-scoring method
best = max(eligible, key=lambda mid: get_score(mid))
```

### Monitoring

```python
from sensitive_rules_for_coding.calibration_system import get_calibration_statistics

stats = get_calibration_statistics()
print(f"Coverage: {stats['total_methods']} methods")
print(f"Excellent: {stats['score_distribution']['excellent']}")
print(f"Poor: {stats['score_distribution']['poor']}")
print(f"Excluded: {stats['excluded_methods']}")
```

## Error Handling

```python
from sensitive_rules_for_coding.calibration_system import get_score

try:
    score = get_score(method_id)
except FileNotFoundError:
    # Calibration file not found
    score = 0.6  # Use default
except Exception as e:
    # Other errors (malformed JSON, etc.)
    logging.error(f"Calibration error: {e}")
    score = 0.6
```

## Production Integration

```python
from sensitive_rules_for_coding.calibration_system import load_intrinsic_calibration

# Load once at startup (singleton)
loader = load_intrinsic_calibration()

# Use throughout application
score = loader.get_score(method_id, role=role)
```

## Files

- **Config**: `src/.../calibration/COHORT_2024_intrinsic_calibration.json`
- **Evidence**: `src/.../evidence_traces/*.json` (49 files)
- **Loader**: `sensitive_rules_for_coding/calibration_system/COHORT_2024_intrinsic_calibration_loader_SENSITIVE.py`

## Security Notes

- ⚠️  Contains production quality scores
- ⚠️  Exclusions may indicate security issues
- ⚠️  Role defaults enforce quality gates
- ⚠️  Changes require governance approval
- ⚠️  Evidence traces are sensitive

## Support

- **Documentation**: [README_SENSITIVE.md](README_SENSITIVE.md)
- **Examples**: [USAGE_EXAMPLE.py](USAGE_EXAMPLE.py)
- **Index**: [INDEX.md](INDEX.md)

---

**Classification**: SENSITIVE - PRODUCTION CALIBRATION DATA
