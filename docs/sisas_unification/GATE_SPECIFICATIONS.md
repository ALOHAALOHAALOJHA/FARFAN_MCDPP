# SISAS Gate Specifications

**Version:** 1.0.0  
**Date:** 2026-01-19  
**Status:** CANONICAL  

---

## 1. Overview

The SISAS system employs four sequential gates that validate signals before delivery to consumers. Each gate applies specific validation rules, and a signal must pass all four gates to be dispatched.

---

## 2. Gate 1: Scope Alignment Gate

### 2.1 Purpose

The Scope Alignment Gate validates that a signal's target scopes are valid and exist in the system. This prevents signals from being dispatched to non-existent or invalid targets.

### 2.2 Validation Rules

| Rule ID | Rule Name | Description | Error Code |
|---------|-----------|-------------|------------|
| `G1_R01` | Scope Existence | All target scopes must exist in the scope registry | `SCOPE_NOT_FOUND` |
| `G1_R02` | Scope Format | Scopes must follow valid format patterns (PA##, D#, CL#, Q###) | `INVALID_SCOPE_FORMAT` |
| `G1_R03` | Scope Hierarchy | Child scopes must belong to valid parent scopes | `SCOPE_HIERARCHY_VIOLATION` |

### 2.3 Scope Format Patterns

| Scope Type | Pattern | Examples | Valid Range |
|------------|---------|----------|-------------|
| Policy Area | `PA[0-9]{2}` | PA01, PA10 | PA01-PA10 |
| Dimension | `D[1-6]` | D1, D6 | D1-D6 |
| Cluster | `CL[1-4]` | CL1, CL4 | CL1-CL4 |
| Question | `Q[0-9]{3}` | Q001, Q300 | Q001-Q300 |

### 2.4 Error Codes

| Error Code | Description | HTTP Status | Recovery |
|------------|-------------|-------------|----------|
| `SCOPE_NOT_FOUND` | Referenced scope does not exist in registry | 404 | Check scope registry, create missing scope |
| `INVALID_SCOPE_FORMAT` | Scope string doesn't match expected pattern | 400 | Correct scope format in signal |
| `SCOPE_HIERARCHY_VIOLATION` | Child scope not under declared parent | 422 | Verify scope hierarchy mapping |
| `SCOPE_MISMATCH` | Signal scope incompatible with consumer | 409 | Re-route to appropriate consumer |

### 2.5 Example: Valid Signal

```json
{
  "signal_id": "550e8400-e29b-41d4-a716-446655440001",
  "signal_type": "SCORING_PRIMARY",
  "target_scopes": ["Q042", "PA02", "D3"],
  "payload": {
    "score": 8.5,
    "max_score": 10.0
  }
}
```

**Gate 1 Result:** ✅ PASS
- Q042 exists in question registry
- PA02 exists in policy area registry
- D3 exists in dimension registry
- Q042 belongs to PA02 (hierarchy valid)

### 2.6 Example: Invalid Signal

```json
{
  "signal_id": "550e8400-e29b-41d4-a716-446655440002",
  "signal_type": "SCORING_PRIMARY",
  "target_scopes": ["Q999", "PA15"],
  "payload": {
    "score": 8.5
  }
}
```

**Gate 1 Result:** ❌ FAIL
- `SCOPE_NOT_FOUND`: Q999 does not exist (max is Q300)
- `SCOPE_NOT_FOUND`: PA15 does not exist (max is PA10)

---

## 3. Gate 2: Value Add Gate

### 3.1 Purpose

The Value Add Gate ensures that signals provide sufficient information gain to justify processing. This prevents low-value or duplicate signals from consuming system resources.

### 3.2 Threshold

**Minimum Value Add Threshold: 0.30 (30%)**

A signal must provide at least 30% new or unique information compared to existing data for the same scope.

### 3.3 Validation Rules

| Rule ID | Rule Name | Description |
|---------|-----------|-------------|
| `G2_R01` | Information Gain | Signal value_add score must be ≥ 0.30 |
| `G2_R02` | Enrichment Bypass | Enrichment signals (category) bypass value check |
| `G2_R03` | Freshness Factor | Recent signals (< 1 min old) get 0.10 bonus |

### 3.4 Value Add Calculation

```python
def calculate_value_add(signal: Signal, existing_data: Dict) -> float:
    """
    Calculate the information gain provided by a signal.
    
    Returns:
        float: Value add score between 0.0 and 1.0
    """
    # Base uniqueness score
    uniqueness = calculate_uniqueness(signal.payload, existing_data)
    
    # Information density score
    density = calculate_information_density(signal.payload)
    
    # Freshness bonus (signals < 1 minute old)
    freshness_bonus = 0.10 if signal_age_seconds(signal) < 60 else 0.0
    
    # Composite score
    value_add = (uniqueness * 0.6) + (density * 0.3) + freshness_bonus
    
    return min(1.0, value_add)  # Cap at 1.0
```

### 3.5 Enrichment Bypass Rule

Signals with `signal_type` in the Enrichment category (`ENRICHMENT_*`) bypass the value add check. This is because enrichment signals are designed to add context even when the information gain is below threshold.

**Bypass Conditions:**
- Signal type is `ENRICHMENT_CONTEXT`, `ENRICHMENT_METADATA`, or `ENRICHMENT_CROSS_REF`
- Signal metadata contains `bypass_value_check: true` (admin override)

### 3.6 Boundary Cases

| Scenario | Value Add | Result | Notes |
|----------|-----------|--------|-------|
| New question, first signal | 1.00 | PASS | No existing data, maximum value |
| Duplicate signal (exact copy) | 0.00 | FAIL | No new information |
| Signal at threshold | 0.30 | PASS | Exactly meets minimum |
| Below threshold | 0.29 | FAIL | Below minimum by 0.01 |
| Enrichment signal | 0.15 | PASS (bypass) | Enrichment bypass applies |
| Fresh signal (< 1 min) | 0.25 + 0.10 = 0.35 | PASS | Freshness bonus applied |
| Stale signal (> 1 min) | 0.25 | FAIL | No freshness bonus |

### 3.7 Example: Valid Signal (Above Threshold)

```json
{
  "signal_id": "550e8400-e29b-41d4-a716-446655440003",
  "signal_type": "SCORING_PRIMARY",
  "target_scopes": ["Q042"],
  "payload": {
    "score": 8.5,
    "max_score": 10.0,
    "scoring_method": "rubric_v2",
    "confidence": 0.92,
    "evidence": ["doc1.pdf", "doc2.pdf"]
  },
  "_calculated_value_add": 0.67
}
```

**Gate 2 Result:** ✅ PASS (0.67 ≥ 0.30)

### 3.8 Example: Invalid Signal (Below Threshold)

```json
{
  "signal_id": "550e8400-e29b-41d4-a716-446655440004",
  "signal_type": "VALIDATION_CONTENT",
  "target_scopes": ["Q042"],
  "payload": {
    "valid": true
  },
  "_calculated_value_add": 0.12
}
```

**Gate 2 Result:** ❌ FAIL
- Error: `LOW_VALUE`
- Value add: 0.12 < 0.30 threshold
- Recommendation: Enrich signal with additional validation details

### 3.9 Example: Enrichment Bypass

```json
{
  "signal_id": "550e8400-e29b-41d4-a716-446655440005",
  "signal_type": "ENRICHMENT_METADATA",
  "target_scopes": ["Q042"],
  "payload": {
    "tags": ["high-priority"]
  },
  "_calculated_value_add": 0.08
}
```

**Gate 2 Result:** ✅ PASS (Enrichment Bypass)
- Value add: 0.08 (below threshold)
- Bypass reason: Signal type is `ENRICHMENT_METADATA`

---

## 4. Gate 3: Capability Gate

### 4.1 Purpose

The Capability Gate verifies that at least one registered consumer can process the signal's type. It matches signal requirements against consumer capabilities.

### 4.2 Matching Algorithm

```python
def match_capabilities(
    signal: Signal, 
    consumer_registry: ConsumerRegistry
) -> List[str]:
    """
    Find consumers capable of processing a signal.
    
    Returns:
        List of eligible consumer_ids, or empty list if none match
    """
    eligible_consumers = []
    
    for consumer in consumer_registry.list_all():
        # Check 1: Consumer handles this signal type
        if signal.signal_type.value not in consumer.signal_types:
            continue
        
        # Check 2: Consumer is in valid phase for signal
        if signal.source_phase not in get_valid_phases(signal.signal_type):
            continue
        
        # Check 3: Consumer scope covers signal target
        if not scopes_overlap(consumer.scopes, signal.target_scopes):
            continue
        
        # Check 4: Consumer is healthy
        if consumer.health_status != "HEALTHY":
            continue
        
        eligible_consumers.append(consumer.consumer_id)
    
    return eligible_consumers
```

### 4.3 Consumer Eligibility Rules

| Rule ID | Rule Name | Description |
|---------|-----------|-------------|
| `G3_R01` | Signal Type Match | Consumer must declare support for the signal type |
| `G3_R02` | Phase Validity | Signal must originate from a phase valid for its type |
| `G3_R03` | Scope Overlap | Consumer scope must include at least one signal target |
| `G3_R04` | Health Check | Consumer must be in HEALTHY or DEGRADED state |
| `G3_R05` | Capacity Check | Consumer queue depth must be below maximum |

### 4.4 Capability Matching Matrix

| Signal Category | Required Capabilities | Eligible Phases |
|-----------------|----------------------|-----------------|
| Extraction | `extract_raw`, `parse_input`, `tokenize`, `normalize` | 0 |
| Assembly | `assemble_components`, `merge_fragments`, `structure_data` | 1 |
| Enrichment | `enrich_context`, `enrich_metadata`, `cross_reference` | 2 |
| Validation | `validate_schema`, `validate_content`, `validate_consistency` | 3 |
| Scoring | `score_primary`, `calculate_weights`, `normalize_scores` | 4 |
| Aggregation | `aggregate_scores`, `aggregate_by_dimension`, `compute_totals` | 5 |
| Report | `generate_report`, `format_output`, `create_visualizations` | 7 |

### 4.5 Example: Valid Signal (Capability Match)

```json
{
  "signal_id": "550e8400-e29b-41d4-a716-446655440006",
  "signal_type": "SCORING_PRIMARY",
  "source_phase": 4,
  "target_scopes": ["Q042", "PA02"]
}
```

**Gate 3 Evaluation:**
1. Signal type: `SCORING_PRIMARY`
2. Looking for consumers with `score_primary` capability
3. `phase_04_consumer` has capabilities: `["score_primary", "score_secondary", "calculate_weights", "normalize_scores"]`
4. Match found!

**Gate 3 Result:** ✅ PASS
- Eligible consumers: `["phase_04_consumer"]`

### 4.6 Example: Invalid Signal (No Capability Match)

```json
{
  "signal_id": "550e8400-e29b-41d4-a716-446655440007",
  "signal_type": "CUSTOM_SIGNAL_TYPE",
  "source_phase": 4,
  "target_scopes": ["Q042"]
}
```

**Gate 3 Result:** ❌ FAIL
- Error: `NO_CAPABLE_CONSUMER`
- Reason: No consumer declares support for `CUSTOM_SIGNAL_TYPE`
- Recovery: Register a consumer with this capability or use a standard signal type

---

## 5. Gate 4: Irrigation Channel Gate

### 5.1 Purpose

The Irrigation Channel Gate performs final validation before dispatch and creates audit records. It ensures the dispatch channel is clear and logging requirements are met.

### 5.2 Post-Dispatch Validation

| Check | Description | On Failure |
|-------|-------------|------------|
| Channel Availability | Verify message queue/channel is accepting messages | Retry with backoff |
| Consumer Readiness | Confirm target consumer is ready to receive | Route to backup or queue |
| Rate Limit | Check dispatch rate is within limits | Apply throttling |
| Deduplication | Verify signal not recently dispatched | Skip duplicate |

### 5.3 Audit Log Requirements

Every signal passing through Gate 4 MUST generate an audit record:

```json
{
  "audit_id": "audit-550e8400-e29b-41d4-a716-446655440008",
  "timestamp": "2026-01-19T23:00:50.442Z",
  "signal_id": "550e8400-e29b-41d4-a716-446655440008",
  "signal_type": "SCORING_PRIMARY",
  "source_phase": 4,
  "target_consumers": ["phase_04_consumer"],
  "gate_results": {
    "gate_1": "PASS",
    "gate_2": "PASS",
    "gate_3": "PASS",
    "gate_4": "PASS"
  },
  "dispatch_status": "DISPATCHED",
  "latency_ms": 12,
  "trace_id": "trace-abc-123"
}
```

### 5.4 Audit Record Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `audit_id` | string | Yes | Unique audit record identifier |
| `timestamp` | ISO 8601 | Yes | Time of audit record creation |
| `signal_id` | UUID | Yes | ID of the audited signal |
| `signal_type` | string | Yes | Type of signal |
| `source_phase` | integer | Yes | Originating phase |
| `target_consumers` | array | Yes | List of target consumer IDs |
| `gate_results` | object | Yes | Pass/fail status for each gate |
| `dispatch_status` | string | Yes | DISPATCHED, REJECTED, DEFERRED |
| `latency_ms` | integer | Yes | Total gate processing time |
| `trace_id` | string | Yes | Distributed trace identifier |
| `rejection_reason` | string | No | Reason if rejected |
| `retry_count` | integer | No | Number of dispatch retries |

### 5.5 Channel Validation Rules

| Rule ID | Rule Name | Description |
|---------|-----------|-------------|
| `G4_R01` | Channel Open | Dispatch channel must be in OPEN state |
| `G4_R02` | Queue Depth | Target queue depth must be < 90% capacity |
| `G4_R03` | Rate Compliance | Dispatch rate must be within configured limits |
| `G4_R04` | Dedup Window | Signal must not match any in 5-minute dedup window |
| `G4_R05` | Audit Success | Audit record must be persisted before dispatch |

### 5.6 Example: Valid Dispatch

```python
# Signal passes all gates
gate_4_result = IrrigationChannelGate.validate(signal, eligible_consumers)

# Result
{
    "status": "PASS",
    "channel_status": "OPEN",
    "queue_depth": 42,
    "queue_capacity": 1000,
    "rate_current": 150,
    "rate_limit": 500,
    "dedup_check": "UNIQUE",
    "audit_record_id": "audit-550e8400...",
    "dispatch_authorized": True
}
```

### 5.7 Example: Channel Blocked

```python
# Channel at capacity
gate_4_result = IrrigationChannelGate.validate(signal, eligible_consumers)

# Result
{
    "status": "FAIL",
    "error_code": "CHANNEL_BLOCKED",
    "channel_status": "CONGESTED",
    "queue_depth": 950,
    "queue_capacity": 1000,
    "recommendation": "Apply backpressure or scale consumers",
    "retry_after_ms": 5000
}
```

---

## 6. Gate Processing Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GATE PROCESSING FLOW                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Signal Received                                                    │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────┐                                                │
│  │ Gate 1: Scope   │──FAIL──▶ Dead Letter (SCOPE_ERROR)             │
│  │ Alignment       │                                                │
│  └────────┬────────┘                                                │
│           │ PASS                                                    │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │ Gate 2: Value   │──FAIL──▶ Dead Letter (LOW_VALUE)               │
│  │ Add Check       │                                                │
│  └────────┬────────┘                                                │
│           │ PASS (or BYPASS for enrichment)                         │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │ Gate 3:         │──FAIL──▶ Dead Letter (NO_CAPABLE_CONSUMER)     │
│  │ Capability      │                                                │
│  └────────┬────────┘                                                │
│           │ PASS (with eligible_consumers list)                     │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │ Gate 4:         │──FAIL──▶ Retry Queue (CHANNEL_ERROR)           │
│  │ Irrigation      │                                                │
│  └────────┬────────┘                                                │
│           │ PASS (audit logged)                                     │
│           ▼                                                         │
│  Dispatch to Consumer(s)                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7. Error Code Reference

| Error Code | Gate | Severity | Description |
|------------|------|----------|-------------|
| `SCOPE_NOT_FOUND` | 1 | ERROR | Referenced scope does not exist |
| `INVALID_SCOPE_FORMAT` | 1 | ERROR | Scope string malformed |
| `SCOPE_HIERARCHY_VIOLATION` | 1 | WARNING | Parent-child scope mismatch |
| `SCOPE_MISMATCH` | 1 | ERROR | Signal-consumer scope incompatible |
| `LOW_VALUE` | 2 | WARNING | Information gain below threshold |
| `VALUE_CALC_ERROR` | 2 | ERROR | Error calculating value add |
| `NO_CAPABLE_CONSUMER` | 3 | ERROR | No consumer can handle signal |
| `CONSUMER_UNAVAILABLE` | 3 | WARNING | Capable consumer not healthy |
| `CAPABILITY_MISMATCH` | 3 | ERROR | Required capability not found |
| `CHANNEL_BLOCKED` | 4 | WARNING | Dispatch channel congested |
| `CHANNEL_CLOSED` | 4 | ERROR | Dispatch channel unavailable |
| `AUDIT_FAILURE` | 4 | ERROR | Cannot persist audit record |
| `DUPLICATE_SIGNAL` | 4 | INFO | Signal deduplicated |
| `RATE_LIMITED` | 4 | WARNING | Dispatch rate exceeded |

---

*End of Gate Specifications*
