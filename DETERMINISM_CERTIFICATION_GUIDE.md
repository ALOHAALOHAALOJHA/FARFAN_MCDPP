# F.A.R.F.A.N Determinism Certification Guide

**Version:** 1.0.0  
**Last Updated:** 2025-12-11  
**Status:** ACTIVE

---

## Table of Contents

1. [Introduction](#introduction)
2. [Determinism Philosophy](#determinism-philosophy)
3. [What MUST Be Deterministic](#what-must-be-deterministic)
4. [What CAN Be Non-Deterministic](#what-can-be-non-deterministic)
5. [Common Patterns](#common-patterns)
6. [Certification Criteria](#certification-criteria)
7. [How to Fix Issues](#how-to-fix-issues)
8. [Testing Determinism](#testing-determinism)

---

## Introduction

F.A.R.F.A.N implements the **SIN_CARRETA doctrine** (Sistema de Integridad No-Compensable para Análisis de Reproducibilidad, Rastreabilidad y Trazabilidad Absoluta), which guarantees that:

> **The same inputs ALWAYS produce identical outputs, bit-for-bit.**

This certification guide explains how to maintain and verify this guarantee across the entire pipeline.

---

## Determinism Philosophy

### Core Principle

**Determinism applies to COMPUTATIONAL RESULTS, not to OBSERVABILITY DATA.**

- ✅ **Computational results** (scores, classifications, recommendations) MUST be deterministic
- ✅ **Observability data** (timestamps, performance metrics, event IDs) CAN be non-deterministic if properly isolated

### Why Determinism Matters

1. **Scientific Reproducibility**: Research results must be verifiable
2. **Audit Compliance**: Policy analysis must be traceable and defendable
3. **Quality Assurance**: Bugs are easier to find when behavior is predictable
4. **Trust**: Stakeholders need confidence in consistent results

---

## What MUST Be Deterministic

### 1. **All Computation**

**CRITICAL**: Any operation that affects results MUST be deterministic.

```python
# ❌ NON-DETERMINISTIC
score = random.random()  # Different every time
items = list(my_dict.keys())  # Order not guaranteed
uuid = uuid.uuid4()  # Random ID used in computation

# ✅ DETERMINISTIC
rng = np.random.default_rng(seed)  # Seeded RNG
score = rng.random()
items = sorted(my_dict.keys())  # Explicit ordering
uuid = generate_deterministic_id(context, component)  # Derived from context
```

### 2. **Seed Management**

**CRITICAL**: All random operations MUST use deterministic seeds.

```python
# ✅ CORRECT PATTERN
from orchestration.seed_registry import SeedRegistry

registry = SeedRegistry()
seed = registry.get_seed(
    policy_unit_id="PDT_2024_MUNICIPALITY_X",
    correlation_id="exec_12345",
    component="numpy"
)
rng = np.random.default_rng(seed)
```

### 3. **ID Generation**

**CRITICAL**: IDs used in computation or result tracking MUST be deterministic.

```python
# ❌ NON-DETERMINISTIC
correlation_id = str(uuid.uuid4())

# ✅ DETERMINISTIC
from orchestration.deterministic_ids import generate_correlation_id

correlation_id = generate_correlation_id(
    policy_unit_id=policy_unit_id,
    phase="phase_2",
    run_counter=0
)
```

### 4. **Data Structures**

**IMPORTANT**: Iteration order MUST be deterministic when it affects results.

```python
# ❌ NON-DETERMINISTIC (if order matters)
for key in my_dict.keys():
    process(key)  # Order varies across Python versions

# ✅ DETERMINISTIC
for key in sorted(my_dict.keys()):
    process(key)  # Always same order

# ✅ ALSO ACCEPTABLE (if order doesn't matter)
results = {key: process(value) for key, value in my_dict.items()}
# Then sort before returning: sorted(results.items())
```

### 5. **Aggregation Operations**

**IMPORTANT**: Reduce operations must be associative and commutative if processing in parallel.

```python
# ✅ DETERMINISTIC (order-independent)
total_score = sum(scores)  # Addition is commutative
average_score = statistics.mean(scores)  # OK

# ❌ POTENTIALLY NON-DETERMINISTIC (order-dependent)
aggregated = functools.reduce(non_commutative_fn, items)
```

---

## What CAN Be Non-Deterministic

### 1. **Timestamps for Logging**

**ACCEPTABLE**: Timestamps used only for observability, not computation.

```python
# ✅ ACCEPTABLE
logger.info(f"Analysis started at {datetime.now().isoformat()}")

# ✅ ACCEPTABLE
metrics = {
    "start_time": time.time(),
    "score": deterministic_score  # This MUST be deterministic
}

# ❌ NOT ACCEPTABLE
random_seed = int(time.time())  # Timestamp affects computation!
```

### 2. **Performance Metrics**

**ACCEPTABLE**: Timing data that doesn't affect results.

```python
# ✅ ACCEPTABLE
start = time.time()
result = expensive_computation()  # Deterministic
elapsed = time.time() - start  # Non-deterministic but OK

return {
    "result": result,  # Deterministic
    "elapsed_ms": elapsed * 1000  # Non-deterministic but acceptable
}
```

### 3. **Event IDs for Tracing**

**ACCEPTABLE**: IDs used only for debugging/observability, not affecting computation.

```python
# ✅ ACCEPTABLE (if event_id not used in computation)
event_id = str(uuid.uuid4())
logger.info(f"Event {event_id}: Processing started")

# ❌ NOT ACCEPTABLE (if event_id affects output)
cache_key = f"{input_hash}:{event_id}"  # Output varies!
```

### 4. **Log File Timestamps**

**ACCEPTABLE**: Log file names with timestamps.

```python
# ✅ ACCEPTABLE
log_file = f"analysis_{datetime.now():%Y%m%d_%H%M%S}.log"

# But results must be deterministic regardless of log file name!
```

---

## Common Patterns

### Pattern 1: Seeded Random Operations

```python
# ✅ CORRECT
from orchestration.seed_registry import SeedRegistry

def analyze_with_randomness(data, policy_unit_id, correlation_id):
    registry = SeedRegistry()
    np_seed = registry.get_seed(policy_unit_id, correlation_id, "numpy")
    py_seed = registry.get_seed(policy_unit_id, correlation_id, "python")
    
    random.seed(py_seed)
    rng = np.random.default_rng(np_seed)
    
    # Now all random operations are deterministic
    sample = rng.choice(data, size=100)
    return process(sample)
```

### Pattern 2: Deterministic ID Generation

```python
# ✅ CORRECT
from orchestration.deterministic_ids import DeterministicIDGenerator

def create_events(correlation_id):
    id_gen = DeterministicIDGenerator(correlation_id)
    
    events = []
    for i in range(10):
        event_id = id_gen.generate_event_id("validation_check")
        events.append({"id": event_id, "data": process(i)})
    
    return events  # Same correlation_id → same event IDs
```

### Pattern 3: Dictionary Ordering

```python
# ✅ CORRECT - When order matters
def aggregate_scores(score_dict):
    # Sort keys for deterministic order
    sorted_keys = sorted(score_dict.keys())
    return [score_dict[k] for k in sorted_keys]

# ✅ ALSO CORRECT - When order doesn't matter (use JSON with sort_keys)
def serialize_results(results):
    return json.dumps(results, sort_keys=True, ensure_ascii=False)
```

### Pattern 4: Async Operations

```python
# ✅ CORRECT - Deterministic despite async
async def parallel_analysis(items, seed_base):
    # Each item gets deterministic seed
    tasks = [
        analyze_item(item, seed=seed_base + i)
        for i, item in enumerate(items)
    ]
    
    # Results may arrive in any order, but we sort them
    results = await asyncio.gather(*tasks)
    
    # Sort by original order to ensure determinism
    return sorted(results, key=lambda r: r["item_id"])
```

### Pattern 5: Exception Event IDs

```python
# ✅ CORRECT - Event ID only for tracing, not computation
def process_with_validation(data, correlation_id=None):
    try:
        return validate_and_process(data)
    except ValidationError as e:
        # Event ID for debugging, but exception flow is deterministic
        event_id = correlation_id or str(uuid.uuid4())
        logger.error(f"[{event_id}] Validation failed: {e}")
        raise  # Same input → same exception → deterministic
```

---

## Certification Criteria

### Severity Levels

| Severity | Impact | Certification Status | Action Required |
|----------|--------|---------------------|-----------------|
| **CRITICAL** | Breaks reproducibility | NOT_CERTIFIED | MUST FIX immediately |
| **HIGH** | Likely breaks reproducibility | NOT_CERTIFIED | MUST FIX before release |
| **MEDIUM** | May break reproducibility | CERTIFIED_WITH_NOTES | SHOULD FIX, document if not |
| **LOW** | Unlikely to affect results | CERTIFIED_WITH_NOTES | Document pattern |
| **ACCEPTABLE** | Doesn't affect results | CERTIFIED | No action needed |

### Certification Status

- **CERTIFIED**: Phase has no determinism issues
- **CERTIFIED_WITH_NOTES**: Phase has documented acceptable non-determinism
- **NOT_CERTIFIED**: Phase has critical/high severity issues

### Requirements for CERTIFIED Status

1. ✅ Zero CRITICAL issues
2. ✅ Zero HIGH issues (or all documented with justification)
3. ✅ All random operations use seeded RNGs
4. ✅ All IDs in computation are deterministic
5. ✅ Dictionary/set iteration is explicitly ordered when needed
6. ✅ All async operations produce deterministic results

---

## How to Fix Issues

### Issue: uuid.uuid4() in Computation

**Problem**: `correlation_id = str(uuid.uuid4())`

**Solution**:
```python
from orchestration.deterministic_ids import generate_correlation_id

correlation_id = generate_correlation_id(
    policy_unit_id=policy_unit_id,
    phase="phase_name",
    run_counter=0
)
```

### Issue: Unseeded Random Operations

**Problem**: `value = random.random()`

**Solution**:
```python
from orchestration.seed_registry import SeedRegistry

registry = SeedRegistry()
seed = registry.get_seed(policy_unit_id, correlation_id, "python")
random.seed(seed)
value = random.random()
```

### Issue: datetime.now() in Computation

**Problem**: `cache_key = f"{input}_{datetime.now()}" `

**Solution**:
```python
# Use deterministic hash instead
cache_key = hashlib.sha256(input.encode()).hexdigest()

# Or use provided timestamp
cache_key = f"{input}_{fixed_timestamp}"
```

### Issue: Non-Deterministic Dictionary Iteration

**Problem**: `for key in my_dict: ...`

**Solution**:
```python
# If order matters:
for key in sorted(my_dict):
    ...

# If order doesn't matter, ensure final output is ordered:
results = {k: process(v) for k, v in my_dict.items()}
return dict(sorted(results.items()))
```

---

## Testing Determinism

### Unit Test Pattern

```python
def test_deterministic_analysis():
    """Test that same inputs produce same outputs."""
    
    # Setup
    input_data = load_test_data()
    policy_unit_id = "TEST_PDT_2024"
    correlation_id = "test_corr_001"
    
    # Run 1
    result1 = analyze(input_data, policy_unit_id, correlation_id)
    
    # Run 2 (same inputs)
    result2 = analyze(input_data, policy_unit_id, correlation_id)
    
    # Assert identical
    assert result1 == result2, "Results must be deterministic"
    
    # For numerical results, use hash comparison
    hash1 = hashlib.sha256(json.dumps(result1, sort_keys=True).encode()).hexdigest()
    hash2 = hashlib.sha256(json.dumps(result2, sort_keys=True).encode()).hexdigest()
    assert hash1 == hash2, "Results must hash to same value"
```

### Integration Test Pattern

```python
def test_pipeline_determinism():
    """Test full pipeline determinism."""
    
    # Setup
    pdt_file = "test_data/sample_pdt.pdf"
    config = load_config()
    
    # Run 1
    manifest1 = run_pipeline(pdt_file, config)
    results1 = load_results(manifest1.output_path)
    
    # Run 2
    manifest2 = run_pipeline(pdt_file, config)
    results2 = load_results(manifest2.output_path)
    
    # Compare results (ignoring timestamps)
    compare_results_deterministically(results1, results2)
```

### Certification Test

```bash
# Run determinism certification audit
python audit_determinism_certification.py

# Check status
grep "Overall Status" DETERMINISM_CERTIFICATION.md

# Should output: Overall Status: `CERTIFIED`
```

---

## Verification Checklist

Before certifying a phase as deterministic:

- [ ] All random operations use seeded RNGs from SeedRegistry
- [ ] All IDs in computation use deterministic generation
- [ ] Dictionary/set iteration is explicitly ordered when needed
- [ ] datetime.now() and time.time() used only for observability
- [ ] uuid.uuid4() used only for tracing, never in computation
- [ ] Async operations produce sorted/ordered results
- [ ] Tests verify same inputs → same outputs
- [ ] Documentation explains any acceptable non-determinism

---

## Certification Process

1. **Run Audit**: `python audit_determinism_certification.py`
2. **Review Report**: Check `DETERMINISM_CERTIFICATION.md`
3. **Fix Critical Issues**: Address all CRITICAL and HIGH severity issues
4. **Document Acceptable Patterns**: Explain any LOW/ACCEPTABLE patterns
5. **Re-run Audit**: Verify fixes
6. **Commit Certification**: Include report in repository

---

## References

- **SIN_CARRETA Doctrine**: `docs/DETERMINISM.md`
- **Seed Management**: `src/orchestration/seed_registry.py`
- **Deterministic IDs**: `src/orchestration/deterministic_ids.py`
- **Audit Tool**: `audit_determinism_certification.py`
- **Mathematical Foundation**: `docs/MATHEMATICAL_FOUNDATION_SCORING.md`

---

## Contact

For questions about determinism certification:
- See: `docs/DETERMINISM.md`
- Tool: `audit_determinism_certification.py`
- Tests: `tests/test_determinism_*.py`

---

**REMEMBER**: Determinism is not optional in F.A.R.F.A.N. It's a core design principle that enables trust, reproducibility, and scientific rigor in policy analysis.
