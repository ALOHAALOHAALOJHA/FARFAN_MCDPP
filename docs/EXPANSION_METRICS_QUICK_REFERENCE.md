# Expansion Metrics Quick Reference

## Critical Metrics to Monitor

### Core Expansion Metrics

| Metric | Type | Target | Minimum | Description |
|--------|------|--------|---------|-------------|
| `multiplier` | float | 5.0x | 2.0x | Expansion ratio (expanded/original) |
| `variant_count` | int | ~4N | N | Number of variants generated |
| `expanded_count` | int | ~5N | 2N | Total patterns after expansion |
| `expand_all_patterns_invoked` | bool | True | True | Function was called |
| `expansion_successful` | bool | True | True | Expansion completed |

Where N = original_count

### Quality Metrics

| Metric | Type | Good | Acceptable | Poor |
|--------|------|------|------------|------|
| `meets_target` | bool | True | False | False |
| `meets_minimum` | bool | True | True | False |
| `patterns_with_expansion` | int | > 80% | > 50% | < 50% |
| `expansion_rate_pct` | float | > 80% | > 50% | < 50% |
| `avg_variants_per_expanded_pattern` | float | > 4.0 | > 2.0 | < 2.0 |

### Performance Thresholds

```python
if multiplier >= 5.0:
    status = "TARGET_ACHIEVED"      # ✓ EXCELLENT
elif multiplier >= 4.0:
    status = "NEAR_TARGET"          # ✓ GOOD
elif multiplier >= 2.0:
    status = "ABOVE_MINIMUM"        # ✓ ACCEPTABLE
else:
    status = "BELOW_MINIMUM"        # ✗ UNACCEPTABLE
```

## Quick Check Commands

### Basic Health Check

```python
enriched_pack = create_enriched_signal_pack(base_pack)

# Quick verification
assert enriched_pack.verify_expansion_invoked()

# One-line status
print(enriched_pack.get_expansion_summary())
```

### Detailed Inspection

```python
metrics = enriched_pack.get_expansion_metrics()

print(f"Invoked: {metrics['expand_all_patterns_invoked']}")
print(f"Success: {metrics['expansion_successful']}")
print(f"Multiplier: {metrics['multiplier']:.2f}x")
print(f"Target: {metrics['meets_target']}")
print(f"Minimum: {metrics['meets_minimum']}")
```

### Log Analysis

```python
# Enable logging
enriched_pack = create_enriched_signal_pack(base_pack)

# Log comprehensive report
enriched_pack.log_expansion_report()

# Check for key log events:
# - enriched_signal_pack_init_begin
# - expand_all_patterns_invoking_now
# - expand_all_patterns_invocation_complete
# - semantic_expansion_applied_successfully
# - enriched_signal_pack_init_complete
```

## Common Issues and Solutions

### Issue: Multiplier < 2.0

**Symptoms:**
```python
metrics['multiplier'] < 2.0
metrics['meets_minimum'] == False
```

**Diagnosis:**
```python
print(f"Patterns with expansion: {metrics['patterns_with_expansion']}")
print(f"Patterns without expansion: {metrics['patterns_without_expansion']}")
print(f"Expansion rate: {metrics['expansion_rate_pct']}%")
```

**Solutions:**
1. Check semantic_expansion field coverage in patterns
2. Verify semantic_expansion format (string or dict)
3. Ensure synonyms are present in semantic_expansion values

### Issue: expand_all_patterns Not Invoked

**Symptoms:**
```python
metrics['expand_all_patterns_invoked'] == False
metrics['expansion_successful'] == False
```

**Diagnosis:**
```python
print(f"Enabled: {metrics['enabled']}")
print(f"Original count: {metrics['original_count']}")
print(f"Error: {metrics.get('expansion_error', 'None')}")
```

**Solutions:**
1. Check enable_semantic_expansion flag (should be True)
2. Verify patterns are not empty
3. Check for exceptions in initialization logs

### Issue: Validation Failed

**Symptoms:**
```python
validation = metrics['validation_result']
validation['valid'] == False
```

**Diagnosis:**
```python
print(f"Issues: {validation['issues']}")
print(f"Warnings: {validation['warnings']}")
print(f"Multiplier: {validation['multiplier']}")
```

**Solutions:**
1. Review validation issues for specific problems
2. Check for shrinkage (expanded < original)
3. Verify variant metadata is properly set

## Metrics Retrieval Cheat Sheet

```python
# Get all metrics
metrics = enriched_pack.get_expansion_metrics()

# Core expansion info
expansion_enabled = metrics['enabled']
expand_invoked = metrics['expand_all_patterns_invoked']
expansion_success = metrics['expansion_successful']

# Counts
original = metrics['original_count']
expanded = metrics['expanded_count']
variants = metrics['variant_count']

# Quality
multiplier = metrics['multiplier']
meets_target = metrics['meets_target']      # >= 5.0x
meets_minimum = metrics['meets_minimum']    # >= 2.0x

# Patterns
with_expansion = metrics['patterns_with_expansion']
without_expansion = metrics['patterns_without_expansion']
expansion_rate = metrics['expansion_rate_pct']

# Statistics
max_variants = metrics['max_variants_per_pattern']
avg_variants = metrics['avg_variants_per_expanded_pattern']

# Timing
init_duration = metrics['initialization_duration_seconds']
expansion_duration = metrics['expansion_duration_seconds']
validation_duration = metrics['validation_duration_seconds']

# Validation
validation = metrics['validation_result']
issues = metrics['validation_issues']
warnings = metrics['validation_warnings']

# Timestamps
expansion_time = metrics['expansion_timestamp']
```

## Log Event Reference

### Must-See Events

```
INFO  enriched_signal_pack_init_begin
      enable_semantic_expansion=True
      target_multiplier=5.0
      minimum_multiplier=2.0

INFO  expand_all_patterns_invoking_now
      function="expand_all_patterns"
      input_count=42
      logging_enabled=True

INFO  expand_all_patterns_invocation_complete
      invocation_status="completed"
      returned_count=210
      preliminary_multiplier=5.0

INFO  semantic_expansion_applied_successfully
      multiplier=5.0
      variant_count=168
      meets_target=True

INFO  enriched_signal_pack_init_complete
      initialization_status="SUCCESS"
      multiplier=5.0
      meets_target=True
```

### Warning Events

```
WARNING semantic_expansion_below_minimum_multiplier
        multiplier=1.5
        expected_minimum=2.0
        performance_category="BELOW_MINIMUM"

WARNING expansion_validation_issues_detected
        issues=["Multiplier 1.8 below minimum 2.0"]
        severity="high"
```

### Error Events

```
ERROR semantic_expansion_failed_exception
      error_type="ValueError"
      error_severity="critical"
      traceback=[...]

ERROR semantic_expansion_validation_failed_critical
      validation_status="FAILED"
      multiplier=1.5
      shortfall_from_minimum=0.5
```

## Testing Checklist

- [ ] `expand_all_patterns` is invoked during initialization
- [ ] Patterns are expanded (multiplier > 1.0)
- [ ] Multiplier meets minimum (>= 2.0)
- [ ] Metrics contain all required fields
- [ ] Validation result is stored
- [ ] `verify_expansion_invoked()` returns True
- [ ] Original patterns not mutated
- [ ] Expansion can be disabled
- [ ] Empty patterns handled gracefully
- [ ] None inputs raise appropriate errors
- [ ] Logging events are emitted
- [ ] Error handling captures exceptions

## Performance Expectations

### Good Performance (5x Target)
- Original: 42 patterns
- Expanded: 210+ patterns
- Variants: 168+ variants
- Multiplier: >= 5.0x
- Coverage: > 80% patterns expanded

### Acceptable Performance (2x Minimum)
- Original: 42 patterns
- Expanded: 84+ patterns
- Variants: 42+ variants
- Multiplier: >= 2.0x
- Coverage: > 50% patterns expanded

### Poor Performance (Below Minimum)
- Multiplier: < 2.0x
- Action: Investigate semantic_expansion field coverage
