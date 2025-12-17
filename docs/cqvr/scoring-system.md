# CQVR Scoring System

## Overview

The CQVR v2.0 scoring system evaluates executor contracts using a 100-point rubric divided into three tiers. This document provides detailed specifications for each scoring component, including point allocations, evaluation logic, and examples.

## Scoring Philosophy

CQVR follows a **strict evidence-based scoring** approach:
- Points are awarded only when explicit evidence exists in the contract
- No partial credit for "almost correct" - criteria must be fully met
- Blockers indicate critical failures that prevent production deployment
- Warnings indicate issues that should be addressed but don't block deployment

## Tier 1: Critical Components (55 points)

These components are **essential** for contract execution. A score below 35/55 in Tier 1 triggers automatic REFORMULAR decision regardless of total score.

### A1. Identity-Schema Coherence (20 points)

**Purpose**: Ensures identity metadata matches output schema constants, preventing runtime mismatches.

**Evaluation Logic**:
```python
def verify_identity_schema_coherence(contract: dict) -> float:
    identity = contract.get("identity", {})
    schema_props = contract.get("output_contract", {}).get("schema", {}).get("properties", {})
    
    score = 0.0
    fields_to_check = {
        "question_id": 5.0,      # Most critical
        "policy_area_id": 5.0,   # Most critical
        "dimension_id": 5.0,     # Most critical
        "question_global": 3.0,  # Important
        "base_slot": 2.0         # Nice to have
    }
    
    for field, points in fields_to_check.items():
        identity_value = identity.get(field)
        schema_const = schema_props.get(field, {}).get("const")
        
        if identity_value == schema_const:
            score += points
        else:
            # BLOCKER: Identity mismatch prevents correct output routing
            add_blocker(f"A1: Identity-Schema mismatch for '{field}'")
    
    return score
```

**Point Allocation**:
- `question_id` match: **5 pts** - Critical for question routing
- `policy_area_id` match: **5 pts** - Critical for policy area filtering
- `dimension_id` match: **5 pts** - Critical for dimensional analysis
- `question_global` match: **3 pts** - Important for global indexing
- `base_slot` match: **2 pts** - Useful for UI display

**Example: Perfect Score (20/20)**
```json
{
  "identity": {
    "question_id": "Q001",
    "policy_area_id": "PA01",
    "dimension_id": "DIM01",
    "question_global": 1,
    "base_slot": "D1-Q1"
  },
  "output_contract": {
    "schema": {
      "properties": {
        "question_id": {"const": "Q001"},
        "policy_area_id": {"const": "PA01"},
        "dimension_id": {"const": "DIM01"},
        "question_global": {"const": 1},
        "base_slot": {"const": "D1-Q1"}
      }
    }
  }
}
```

**Example: Failed Score (0/20)**
```json
{
  "identity": {
    "question_id": "Q001"
  },
  "output_contract": {
    "schema": {
      "properties": {
        "question_id": {"const": "Q002"}  // MISMATCH
      }
    }
  }
}
```
**Blockers**: Identity-Schema mismatch for 'question_id': identity=Q001, schema=Q002

---

### A2. Method-Assembly Alignment (20 points)

**Purpose**: Ensures all assembly sources reference valid method provides, preventing orphan sources.

**Evaluation Logic**:
```python
def verify_method_assembly_alignment(contract: dict) -> float:
    methods = contract.get("method_binding", {}).get("methods", [])
    provides_set = {m.get("provides") for m in methods if m.get("provides")}
    
    assembly_rules = contract.get("evidence_assembly", {}).get("assembly_rules", [])
    sources_referenced = set()
    orphan_sources = []
    
    for rule in assembly_rules:
        for source in rule.get("sources", []):
            source_key = extract_source_key(source)
            if source_key and not is_wildcard(source_key):
                sources_referenced.add(source_key)
                if source_key not in provides_set:
                    orphan_sources.append(source_key)
    
    score = 0.0
    
    # No orphan sources: 10 pts
    if not orphan_sources:
        score += 10.0
    else:
        add_blocker(f"A2: Assembly sources not in provides: {orphan_sources[:5]}")
    
    # Method usage ratio: 5 pts
    usage_ratio = len(sources_referenced) / len(provides_set) if provides_set else 0
    if usage_ratio >= 0.9: score += 5.0
    elif usage_ratio >= 0.7: score += 3.0
    elif usage_ratio >= 0.5: score += 1.0
    
    # Method count declared matches actual: 3 pts
    declared_count = contract.get("method_binding", {}).get("method_count", 0)
    if declared_count == len(methods):
        score += 3.0
    
    # Consistency bonus: 2 pts
    if not orphan_sources:
        score += 2.0
    
    return score
```

**Point Allocation**:
- No orphan sources: **10 pts** - Critical for assembly integrity
- Method usage ratio ≥ 90%: **5 pts** - All methods utilized
- Method usage ratio 70-89%: **3 pts** - Most methods utilized
- Method usage ratio 50-69%: **1 pts** - Some methods utilized
- Method count matches: **3 pts** - Metadata consistency
- Consistency bonus: **2 pts** - No orphan + good usage

**Example: Perfect Score (20/20)**
```json
{
  "method_binding": {
    "method_count": 3,
    "methods": [
      {"provides": "text_mining.extract"},
      {"provides": "causal.infer"},
      {"provides": "bayesian.evaluate"}
    ]
  },
  "evidence_assembly": {
    "assembly_rules": [{
      "sources": [
        "text_mining.extract",
        "causal.infer",
        "bayesian.evaluate"
      ]
    }]
  }
}
```
**Score**: 10 (no orphans) + 5 (100% usage) + 3 (count matches) + 2 (consistency) = 20/20

**Example: Failed Score (5/20)**
```json
{
  "method_binding": {
    "method_count": 2,
    "methods": [
      {"provides": "text_mining.extract"},
      {"provides": "causal.infer"}
    ]
  },
  "evidence_assembly": {
    "assembly_rules": [{
      "sources": [
        "text_mining.extract",
        "nonexistent.method"  // ORPHAN
      ]
    }]
  }
}
```
**Blockers**: Assembly sources not in provides: ['nonexistent.method']
**Score**: 0 (orphans) + 3 (50% usage) + 0 (count mismatch) + 2 (partial) = 5/20

---

### A3. Signal Requirements (10 points)

**Purpose**: Ensures signal thresholds prevent zero-strength signals from passing validation.

**Evaluation Logic**:
```python
def verify_signal_requirements(contract: dict) -> float:
    signal_reqs = contract.get("signal_requirements", {})
    mandatory_signals = signal_reqs.get("mandatory_signals", [])
    threshold = signal_reqs.get("minimum_signal_threshold", 0.0)
    aggregation = signal_reqs.get("signal_aggregation", "")
    
    score = 0.0
    
    # CRITICAL CHECK: threshold > 0 if mandatory_signals defined
    if mandatory_signals and threshold <= 0:
        add_blocker(
            f"A3: CRITICAL - minimum_signal_threshold={threshold} "
            "but mandatory_signals defined. Zero-strength signals will pass."
        )
        return 0.0
    
    # Configuration validity: 5 pts
    if mandatory_signals and threshold > 0:
        score += 5.0
    elif not mandatory_signals:
        score += 5.0  # No mandatory signals = OK
    
    # Signal format validity: 3 pts
    if mandatory_signals and all(isinstance(s, str) for s in mandatory_signals):
        score += 3.0
    
    # Aggregation method: 2 pts
    valid_aggregations = ["weighted_mean", "minimum", "product", "harmonic_mean"]
    if aggregation in valid_aggregations:
        score += 2.0
    
    return score
```

**Point Allocation**:
- Valid threshold configuration: **5 pts** - No zero-strength risk
- Well-formed signal strings: **3 pts** - Proper signal naming
- Valid aggregation method: **2 pts** - Correct aggregation logic

**Example: Perfect Score (10/10)**
```json
{
  "signal_requirements": {
    "mandatory_signals": [
      "feasibility_score",
      "resource_coherence"
    ],
    "minimum_signal_threshold": 0.5,
    "signal_aggregation": "weighted_mean"
  }
}
```

**Example: Critical Failure (0/10)**
```json
{
  "signal_requirements": {
    "mandatory_signals": ["feasibility_score"],
    "minimum_signal_threshold": 0.0  // ZERO THRESHOLD
  }
}
```
**Blockers**: CRITICAL - minimum_signal_threshold=0.0 but mandatory_signals defined. Zero-strength signals will pass.

---

### A4. Output Schema (5 points)

**Purpose**: Ensures required fields are defined in schema properties.

**Evaluation Logic**:
```python
def verify_output_schema(contract: dict) -> float:
    schema = contract.get("output_contract", {}).get("schema", {})
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    
    score = 0.0
    
    # All required fields defined: 3 pts
    all_defined = all(field in properties for field in required)
    if all_defined:
        score += 3.0
    else:
        missing = [f for f in required if f not in properties]
        add_blocker(f"A4: Required fields not in properties: {missing}")
    
    # Source hash traceability: 2 pts
    source_hash = contract.get("traceability", {}).get("source_hash", "")
    if source_hash and not source_hash.startswith("TODO"):
        score += 2.0
    else:
        add_warning("A4: source_hash is placeholder or missing")
        score += 1.0  # Partial credit
    
    return score
```

**Point Allocation**:
- Required fields in properties: **3 pts** - Schema validity
- Valid source hash: **2 pts** - Provenance tracking
- Placeholder source hash: **1 pt** - Partial credit

---

## Tier 2: Functional Components (30 points)

These components enable proper evidence processing and validation.

### B1. Pattern Coverage (10 points)

**Purpose**: Ensures patterns cover expected elements with valid confidence weights.

**Evaluation Logic**:
```python
def verify_pattern_coverage(contract: dict) -> float:
    patterns = contract.get("question_context", {}).get("patterns", [])
    expected_elements = contract.get("question_context", {}).get("expected_elements", [])
    required_elements = [e for e in expected_elements if e.get("required")]
    
    score = 0.0
    
    # Coverage ratio: 5 pts
    coverage_ratio = min(len(patterns) / max(len(required_elements), 1), 1.0)
    score += coverage_ratio * 5.0
    
    # Confidence weights valid: 3 pts
    confidence_weights = [p.get("confidence_weight", 0) for p in patterns]
    if all(0 <= w <= 1 for w in confidence_weights):
        score += 3.0
    
    # Pattern IDs unique: 2 pts
    pattern_ids = [p.get("id") for p in patterns]
    if len(set(pattern_ids)) == len(pattern_ids) and all(pattern_ids):
        score += 2.0
    
    return score
```

**Point Allocation**:
- Pattern coverage ratio: **5 pts** - Proportional to coverage
- Valid confidence weights [0,1]: **3 pts** - Proper weighting
- Unique pattern IDs: **2 pts** - Pattern tracking

---

### B2. Method Specificity (10 points)

**Purpose**: Ensures methods have specific technical approaches, not boilerplate.

**Evaluation Logic**:
```python
def verify_method_specificity(contract: dict) -> float:
    methods = contract.get("methodological_depth", {}).get("methods", [])
    
    generic_patterns = [
        "Execute", "Process results", "Return structured output",
        "O(n) where n=input size", "Input data is preprocessed"
    ]
    
    specific_count = 0
    for method_info in methods:
        steps = method_info.get("technical_approach", {}).get("steps", [])
        is_specific = True
        
        for step in steps:
            step_desc = step.get("description", "")
            if any(pattern in step_desc for pattern in generic_patterns):
                is_specific = False
                break
        
        if is_specific:
            specific_count += 1
    
    specificity_ratio = specific_count / len(methods) if methods else 0
    score = specificity_ratio * 6.0
    
    # Bonus for complexity analysis: 2 pts
    complexity_count = sum(
        1 for m in methods
        if m.get("technical_approach", {}).get("complexity")
    )
    score += (complexity_count / len(methods)) * 2.0 if methods else 0
    
    # Bonus for assumptions: 2 pts
    assumptions_count = sum(
        1 for m in methods
        if m.get("technical_approach", {}).get("assumptions")
    )
    score += (assumptions_count / len(methods)) * 2.0 if methods else 0
    
    return score
```

**Point Allocation**:
- Specific (non-boilerplate) steps: **6 pts** - Proportional to specificity
- Complexity analysis present: **2 pts** - Technical depth
- Assumptions documented: **2 pts** - Transparency

---

### B3. Validation Rules (10 points)

**Purpose**: Ensures validation rules cover required elements with failure contracts.

**Evaluation Logic**:
```python
def verify_validation_rules(contract: dict) -> float:
    rules = contract.get("validation_rules", {}).get("rules", [])
    expected_elements = contract.get("question_context", {}).get("expected_elements", [])
    required_elements = {e.get("type") for e in expected_elements if e.get("required")}
    
    score = 0.0
    
    # Extract validation elements
    validation_elements = set()
    for rule in rules:
        must_contain = rule.get("must_contain", {})
        validation_elements.update(must_contain.get("elements", []))
    
    # Required elements coverage: 5 pts
    if required_elements.issubset(validation_elements):
        score += 5.0
    
    # Rule diversity: 3 pts
    if any(r.get("must_contain") for r in rules) and any(r.get("should_contain") for r in rules):
        score += 3.0
    
    # Failure contract: 2 pts
    failure_contract = contract.get("error_handling", {}).get("failure_contract", {})
    if failure_contract.get("emit_code"):
        score += 2.0
    
    return score
```

**Point Allocation**:
- Required elements covered: **5 pts** - Coverage completeness
- Must + should contain rules: **3 pts** - Rule diversity
- Failure contract defined: **2 pts** - Error handling

---

## Tier 3: Quality Components (15 points)

These components ensure maintainability and documentation quality.

### C1. Documentation Quality (5 points)

**Purpose**: Ensures epistemological foundations are specific, not boilerplate.

**Point Allocation**:
- Specific paradigms (not boilerplate): **2 pts**
- Justifications with reasoning: **2 pts**
- Theoretical framework references: **1 pt**

---

### C2. Human Template (5 points)

**Purpose**: Ensures templates reference identity and include dynamic placeholders.

**Point Allocation**:
- Title references identity fields: **3 pts**
- Dynamic placeholders in summary: **2 pts**

---

### C3. Metadata Completeness (5 points)

**Purpose**: Ensures contract metadata is complete for provenance tracking.

**Point Allocation**:
- Valid contract hash (64 chars): **2 pts**
- Valid created_at timestamp: **1 pt**
- Schema validation version: **1 pt**
- Contract version with dots: **1 pt**

---

## Scoring Examples

### Example 1: Production-Ready Contract (87/100)
```
Tier 1: 48/55
  A1: 20/20 ✅ Perfect identity-schema coherence
  A2: 19/20 ✅ 1 unused method
  A3: 5/10  ⚠️ No mandatory signals (acceptable)
  A4: 4/5   ⚠️ Source hash is placeholder

Tier 2: 27/30
  B1: 10/10 ✅ Perfect pattern coverage
  B2: 9/10  ✅ 1 boilerplate method
  B3: 8/10  ⚠️ Missing should_contain rules

Tier 3: 12/15
  C1: 4/5   ✅ Good documentation
  C2: 5/5   ✅ Perfect template
  C3: 3/5   ⚠️ Missing metadata fields

Decision: PRODUCCION (Tier1=48/55, Total=87/100)
```

### Example 2: Patchable Contract (72/100)
```
Tier 1: 43/55
  A1: 20/20 ✅ Perfect
  A2: 18/20 ⚠️ 2 orphan sources
  A3: 0/10  ❌ Zero threshold with mandatory signals
  A4: 5/5   ✅ Perfect

Tier 2: 22/30
  B1: 8/10  ⚠️ Low pattern coverage
  B2: 7/10  ⚠️ Boilerplate methods
  B3: 7/10  ⚠️ Incomplete validation

Tier 3: 7/15
  C1: 2/5   ⚠️ Boilerplate documentation
  C2: 3/5   ⚠️ Missing placeholders
  C3: 2/5   ⚠️ Incomplete metadata

Decision: PARCHEAR (Tier1=43/55, Total=72/100, 1 blocker)
Recommendations:
1. Fix A3: Set minimum_signal_threshold > 0
2. Fix A2: Remove orphan sources or add methods
```

### Example 3: Requires Reformulation (32/100)
```
Tier 1: 18/55
  A1: 8/20  ❌ 3 identity mismatches
  A2: 5/20  ❌ 5 orphan sources
  A3: 0/10  ❌ Zero threshold
  A4: 5/5   ✅ Schema OK

Tier 2: 10/30
  B1: 5/10  ❌ Low coverage
  B2: 3/10  ❌ All boilerplate
  B3: 2/10  ❌ No validation rules

Tier 3: 4/15
  C1: 1/5   ❌ Boilerplate
  C2: 2/5   ❌ Poor template
  C3: 1/5   ❌ Missing metadata

Decision: REFORMULAR (Tier1=18/55 < 35 threshold)
Blockers:
1. A1: Identity-Schema mismatches
2. A2: Assembly sources broken
3. A3: Signal threshold zero
```

## Threshold Summary

| Metric | Threshold | Significance |
|--------|-----------|--------------|
| Tier 1 Production | ≥ 45/55 | Required for PRODUCCION |
| Tier 1 Patch | ≥ 35/55 | Required for PARCHEAR |
| Total Production | ≥ 80/100 | Required for PRODUCCION |
| Total Patch | ≥ 70/100 | Suggested for PARCHEAR |
| Blockers | 0 | Required for PRODUCCION |
| Blockers | ≤ 2 | Acceptable for PARCHEAR |

## See Also

- [Decision Matrix](decision-matrix.md) - Triage logic
- [API Reference](api-reference.md) - Implementation details
- [Troubleshooting](troubleshooting.md) - Common scoring issues
