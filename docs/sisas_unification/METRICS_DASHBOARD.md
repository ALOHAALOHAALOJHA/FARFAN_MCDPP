# SISAS Metrics Dashboard Specification

**Version:** 1.0.0  
**Date:** 2026-01-19  
**Status:** CANONICAL  

---

## 1. Overview

This document defines the metrics, KPIs, and performance targets for the SISAS system. All components MUST expose these metrics for monitoring and alerting.

---

## 2. SDO Metrics (SignalDistributionOrchestrator)

### 2.1 Core SDO Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `sdo_signals_dispatched` | Counter | Total signals successfully dispatched | `signal_type`, `phase` |
| `sdo_signals_delivered` | Counter | Total signals confirmed delivered to consumers | `consumer_id`, `signal_type` |
| `sdo_signals_rejected` | Counter | Total signals rejected by gates | `gate`, `error_code` |
| `sdo_signals_deduplicated` | Counter | Total signals filtered by deduplication | `signal_type` |
| `sdo_dead_letters` | Counter | Total signals sent to dead letter queue | `reason` |
| `sdo_consumer_errors` | Counter | Total consumer processing errors | `consumer_id`, `error_type` |

### 2.2 SDO Metric Definitions

```python
from prometheus_client import Counter, Histogram, Gauge

# Dispatch metrics
sdo_signals_dispatched = Counter(
    'sdo_signals_dispatched_total',
    'Total number of signals dispatched',
    ['signal_type', 'phase']
)

sdo_signals_delivered = Counter(
    'sdo_signals_delivered_total',
    'Total number of signals delivered to consumers',
    ['consumer_id', 'signal_type']
)

sdo_signals_rejected = Counter(
    'sdo_signals_rejected_total',
    'Total number of signals rejected by gates',
    ['gate', 'error_code']
)

sdo_signals_deduplicated = Counter(
    'sdo_signals_deduplicated_total',
    'Total number of duplicate signals filtered',
    ['signal_type']
)

sdo_dead_letters = Counter(
    'sdo_dead_letters_total',
    'Total number of signals sent to dead letter queue',
    ['reason']
)

sdo_consumer_errors = Counter(
    'sdo_consumer_errors_total',
    'Total number of consumer processing errors',
    ['consumer_id', 'error_type']
)
```

### 2.3 SDO Calculated Metrics

| Metric | Formula | Unit |
|--------|---------|------|
| Delivery Rate | `sdo_signals_delivered / sdo_signals_dispatched` | Percentage |
| Rejection Rate | `sdo_signals_rejected / (sdo_signals_dispatched + sdo_signals_rejected)` | Percentage |
| Dead Letter Rate | `sdo_dead_letters / sdo_signals_dispatched` | Percentage |
| Consumer Error Rate | `sdo_consumer_errors / sdo_signals_delivered` | Percentage |
| Deduplication Rate | `sdo_signals_deduplicated / (sdo_signals_dispatched + sdo_signals_deduplicated)` | Percentage |

---

## 3. Gate Metrics

### 3.1 Gate Pass Rate Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `gate_1_pass_rate` | Gauge | Percentage of signals passing Gate 1 | - |
| `gate_2_pass_rate` | Gauge | Percentage of signals passing Gate 2 | - |
| `gate_3_pass_rate` | Gauge | Percentage of signals passing Gate 3 | - |
| `gate_4_pass_rate` | Gauge | Percentage of signals passing Gate 4 | - |

### 3.2 Gate Detailed Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `gate_signals_received` | Counter | Signals received by gate | `gate` |
| `gate_signals_passed` | Counter | Signals passing gate validation | `gate` |
| `gate_signals_failed` | Counter | Signals failing gate validation | `gate`, `error_code` |
| `gate_processing_time_seconds` | Histogram | Time spent processing in gate | `gate` |
| `gate_validation_errors` | Counter | Validation errors encountered | `gate`, `rule_id` |

### 3.3 Gate Metric Definitions

```python
from prometheus_client import Counter, Histogram, Gauge

# Gate pass rates (updated every minute)
gate_1_pass_rate = Gauge(
    'gate_1_pass_rate',
    'Percentage of signals passing Scope Alignment Gate'
)

gate_2_pass_rate = Gauge(
    'gate_2_pass_rate',
    'Percentage of signals passing Value Add Gate'
)

gate_3_pass_rate = Gauge(
    'gate_3_pass_rate',
    'Percentage of signals passing Capability Gate'
)

gate_4_pass_rate = Gauge(
    'gate_4_pass_rate',
    'Percentage of signals passing Irrigation Channel Gate'
)

# Detailed gate metrics
gate_signals_received = Counter(
    'gate_signals_received_total',
    'Total signals received by gate',
    ['gate']
)

gate_signals_passed = Counter(
    'gate_signals_passed_total',
    'Total signals passing gate validation',
    ['gate']
)

gate_signals_failed = Counter(
    'gate_signals_failed_total',
    'Total signals failing gate validation',
    ['gate', 'error_code']
)

gate_processing_time_seconds = Histogram(
    'gate_processing_time_seconds',
    'Time spent processing signals in gate',
    ['gate'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

gate_validation_errors = Counter(
    'gate_validation_errors_total',
    'Validation errors by gate and rule',
    ['gate', 'rule_id']
)
```

### 3.4 Gate-Specific Metrics

#### Gate 1: Scope Alignment

| Metric | Description |
|--------|-------------|
| `gate_1_scope_lookups` | Number of scope registry lookups |
| `gate_1_scope_cache_hits` | Scope found in cache |
| `gate_1_scope_cache_misses` | Scope not in cache, fetched from registry |
| `gate_1_invalid_formats` | Signals with invalid scope format |
| `gate_1_hierarchy_violations` | Signals with scope hierarchy violations |

#### Gate 2: Value Add

| Metric | Description |
|--------|-------------|
| `gate_2_value_calculations` | Number of value add calculations |
| `gate_2_below_threshold` | Signals below 0.30 threshold |
| `gate_2_enrichment_bypasses` | Enrichment signals bypassing check |
| `gate_2_freshness_bonuses` | Signals receiving freshness bonus |
| `gate_2_value_histogram` | Distribution of value add scores |

#### Gate 3: Capability

| Metric | Description |
|--------|-------------|
| `gate_3_capability_lookups` | Number of capability matching operations |
| `gate_3_consumers_matched` | Total consumers matched to signals |
| `gate_3_no_match_signals` | Signals with no capable consumer |
| `gate_3_multi_match_signals` | Signals matching multiple consumers |

#### Gate 4: Irrigation Channel

| Metric | Description |
|--------|-------------|
| `gate_4_audit_records_created` | Audit records successfully created |
| `gate_4_audit_failures` | Audit record creation failures |
| `gate_4_channel_blocks` | Times channel was blocked |
| `gate_4_rate_limit_hits` | Times rate limit was applied |
| `gate_4_dedup_filter_hits` | Signals filtered by deduplication |

---

## 4. Performance Targets

### 4.1 Primary KPIs

| KPI | Target | Critical Threshold | Measurement Window |
|-----|--------|-------------------|-------------------|
| Dead Letter Rate | < 10% | > 20% | Rolling 5 minutes |
| Error Rate | < 5% | > 10% | Rolling 5 minutes |
| Dispatch Latency (p99) | < 100ms | > 500ms | Rolling 1 minute |

### 4.2 Secondary KPIs

| KPI | Target | Warning Threshold | Critical Threshold |
|-----|--------|-------------------|-------------------|
| Gate 1 Pass Rate | > 95% | < 90% | < 80% |
| Gate 2 Pass Rate | > 85% | < 75% | < 65% |
| Gate 3 Pass Rate | > 98% | < 95% | < 90% |
| Gate 4 Pass Rate | > 99% | < 97% | < 95% |
| Consumer Availability | > 99.5% | < 99% | < 98% |
| Throughput (signals/sec) | > 100 | < 50 | < 25 |

### 4.3 Latency Targets

| Operation | p50 | p90 | p99 | p99.9 |
|-----------|-----|-----|-----|-------|
| Gate 1 Processing | < 5ms | < 10ms | < 25ms | < 50ms |
| Gate 2 Processing | < 10ms | < 20ms | < 50ms | < 100ms |
| Gate 3 Processing | < 5ms | < 10ms | < 25ms | < 50ms |
| Gate 4 Processing | < 10ms | < 25ms | < 50ms | < 100ms |
| Total Gate Pipeline | < 30ms | < 50ms | < 100ms | < 200ms |
| Consumer Dispatch | < 5ms | < 10ms | < 25ms | < 50ms |
| End-to-End Signal Flow | < 50ms | < 100ms | < 200ms | < 500ms |

### 4.4 Capacity Targets

| Resource | Normal | Peak | Maximum |
|----------|--------|------|---------|
| Signals per Second | 100 | 500 | 1000 |
| Concurrent Consumers | 10 | 30 | 50 |
| Queue Depth per Consumer | < 100 | < 500 | 1000 |
| Memory per Consumer | < 256MB | < 512MB | 1GB |
| DLQ Size | < 100 | < 500 | 1000 |

---

## 5. Alert Definitions

### 5.1 Critical Alerts

| Alert Name | Condition | Severity | Action |
|------------|-----------|----------|--------|
| `HighDeadLetterRate` | `dead_letter_rate > 20%` for 5 min | CRITICAL | Page on-call, investigate signal quality |
| `HighErrorRate` | `error_rate > 10%` for 5 min | CRITICAL | Page on-call, check consumer health |
| `HighLatency` | `dispatch_latency_p99 > 500ms` for 3 min | CRITICAL | Page on-call, check system load |
| `ConsumerDown` | Consumer unavailable for > 1 min | CRITICAL | Auto-restart, page if persists |
| `AuditFailure` | Audit write failure | CRITICAL | Halt dispatch, page immediately |

### 5.2 Warning Alerts

| Alert Name | Condition | Severity | Action |
|------------|-----------|----------|--------|
| `ElevatedDeadLetterRate` | `dead_letter_rate > 10%` for 10 min | WARNING | Notify team, investigate |
| `ElevatedErrorRate` | `error_rate > 5%` for 10 min | WARNING | Notify team, check logs |
| `LatencyDegraded` | `dispatch_latency_p99 > 200ms` for 5 min | WARNING | Check system resources |
| `QueueBacklog` | Queue depth > 500 for 5 min | WARNING | Check consumer throughput |
| `GatePassRateLow` | Any gate pass rate < threshold | WARNING | Review signal quality |

### 5.3 Alert Configuration (Prometheus)

```yaml
groups:
  - name: sisas_alerts
    rules:
      - alert: HighDeadLetterRate
        expr: |
          rate(sdo_dead_letters_total[5m]) / 
          rate(sdo_signals_dispatched_total[5m]) > 0.20
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High dead letter rate detected"
          description: "Dead letter rate is {{ $value | humanizePercentage }} (threshold: 20%)"

      - alert: HighErrorRate
        expr: |
          rate(sdo_consumer_errors_total[5m]) / 
          rate(sdo_signals_delivered_total[5m]) > 0.10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High consumer error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 10%)"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.99, rate(gate_processing_time_seconds_bucket[1m])) > 0.5
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "High dispatch latency detected"
          description: "p99 latency is {{ $value | humanizeDuration }} (threshold: 500ms)"

      - alert: GateLowPassRate
        expr: |
          gate_1_pass_rate < 0.80 or
          gate_2_pass_rate < 0.65 or
          gate_3_pass_rate < 0.90 or
          gate_4_pass_rate < 0.95
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Gate pass rate below critical threshold"
```

---

## 6. Dashboard Panels

### 6.1 Overview Panel

```
┌────────────────────────────────────────────────────────────────────┐
│                     SISAS METRICS DASHBOARD                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐│
│  │ Dead Letter  │ │ Error Rate   │ │ Latency p99  │ │ Throughput ││
│  │    7.2%      │ │    3.1%      │ │    42ms      │ │  128/sec   ││
│  │   ▼ 0.5%    │ │   ▲ 0.2%    │ │   ─ 0ms     │ │  ▲ 15/sec ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘│
│                                                                    │
│  Gate Pass Rates (last 5 min)                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Gate 1 [████████████████████████████████████████] 98.2%     │  │
│  │ Gate 2 [████████████████████████████████████░░░░] 89.5%     │  │
│  │ Gate 3 [█████████████████████████████████████████] 99.1%    │  │
│  │ Gate 4 [█████████████████████████████████████████] 99.8%    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Signal Flow (last hour)                                           │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │    ╭────╮                         ╭────╮                    │  │
│  │   ╱      ╲       ╭────╮          ╱      ╲                   │  │
│  │  ╱        ╲     ╱      ╲        ╱        ╲                  │  │
│  │ ╱          ╲   ╱        ╲      ╱          ╲                 │  │
│  │╱            ╲─╱          ╲────╱            ╲────            │  │
│  │ 12:00   12:15   12:30   12:45   13:00                       │  │
│  │ ── Dispatched  ── Delivered  ── Rejected                    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 6.2 Grafana Dashboard JSON

```json
{
  "title": "SISAS Metrics Dashboard",
  "uid": "sisas-main",
  "panels": [
    {
      "title": "Dead Letter Rate",
      "type": "stat",
      "targets": [
        {
          "expr": "rate(sdo_dead_letters_total[5m]) / rate(sdo_signals_dispatched_total[5m]) * 100",
          "legendFormat": "Dead Letter %"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "thresholds": {
            "steps": [
              {"color": "green", "value": null},
              {"color": "yellow", "value": 10},
              {"color": "red", "value": 20}
            ]
          },
          "unit": "percent"
        }
      }
    },
    {
      "title": "Error Rate",
      "type": "stat",
      "targets": [
        {
          "expr": "rate(sdo_consumer_errors_total[5m]) / rate(sdo_signals_delivered_total[5m]) * 100"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "thresholds": {
            "steps": [
              {"color": "green", "value": null},
              {"color": "yellow", "value": 5},
              {"color": "red", "value": 10}
            ]
          },
          "unit": "percent"
        }
      }
    },
    {
      "title": "Dispatch Latency p99",
      "type": "stat",
      "targets": [
        {
          "expr": "histogram_quantile(0.99, rate(gate_processing_time_seconds_bucket[1m])) * 1000"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "thresholds": {
            "steps": [
              {"color": "green", "value": null},
              {"color": "yellow", "value": 100},
              {"color": "red", "value": 500}
            ]
          },
          "unit": "ms"
        }
      }
    },
    {
      "title": "Gate Pass Rates",
      "type": "bargauge",
      "targets": [
        {"expr": "gate_1_pass_rate * 100", "legendFormat": "Gate 1"},
        {"expr": "gate_2_pass_rate * 100", "legendFormat": "Gate 2"},
        {"expr": "gate_3_pass_rate * 100", "legendFormat": "Gate 3"},
        {"expr": "gate_4_pass_rate * 100", "legendFormat": "Gate 4"}
      ],
      "fieldConfig": {
        "defaults": {
          "min": 0,
          "max": 100,
          "unit": "percent"
        }
      }
    },
    {
      "title": "Signal Flow",
      "type": "timeseries",
      "targets": [
        {"expr": "rate(sdo_signals_dispatched_total[1m])", "legendFormat": "Dispatched"},
        {"expr": "rate(sdo_signals_delivered_total[1m])", "legendFormat": "Delivered"},
        {"expr": "rate(sdo_signals_rejected_total[1m])", "legendFormat": "Rejected"}
      ]
    }
  ]
}
```

---

## 7. Metric Collection

### 7.1 Collection Endpoints

| Endpoint | Format | Description |
|----------|--------|-------------|
| `/metrics` | Prometheus | All metrics in Prometheus format |
| `/metrics/json` | JSON | All metrics in JSON format |
| `/health` | JSON | Component health status |
| `/health/detailed` | JSON | Detailed health with metrics |

### 7.2 Sample Metrics Output

```
# HELP sdo_signals_dispatched_total Total number of signals dispatched
# TYPE sdo_signals_dispatched_total counter
sdo_signals_dispatched_total{signal_type="SCORING_PRIMARY",phase="4"} 15234
sdo_signals_dispatched_total{signal_type="AGGREGATION_COMPLETE",phase="5"} 3045
sdo_signals_dispatched_total{signal_type="REPORT_FINAL",phase="7"} 152

# HELP sdo_signals_delivered_total Total signals delivered to consumers
# TYPE sdo_signals_delivered_total counter
sdo_signals_delivered_total{consumer_id="phase_04_consumer",signal_type="SCORING_PRIMARY"} 14892
sdo_signals_delivered_total{consumer_id="phase_05_consumer",signal_type="AGGREGATION_COMPLETE"} 3001

# HELP sdo_dead_letters_total Total signals sent to dead letter queue
# TYPE sdo_dead_letters_total counter
sdo_dead_letters_total{reason="LOW_VALUE"} 342
sdo_dead_letters_total{reason="NO_CAPABLE_CONSUMER"} 45
sdo_dead_letters_total{reason="SCOPE_NOT_FOUND"} 12

# HELP gate_1_pass_rate Percentage of signals passing Scope Alignment Gate
# TYPE gate_1_pass_rate gauge
gate_1_pass_rate 0.982

# HELP gate_2_pass_rate Percentage of signals passing Value Add Gate
# TYPE gate_2_pass_rate gauge
gate_2_pass_rate 0.895

# HELP gate_3_pass_rate Percentage of signals passing Capability Gate
# TYPE gate_3_pass_rate gauge
gate_3_pass_rate 0.991

# HELP gate_4_pass_rate Percentage of signals passing Irrigation Channel Gate
# TYPE gate_4_pass_rate gauge
gate_4_pass_rate 0.998

# HELP gate_processing_time_seconds Time spent processing signals in gate
# TYPE gate_processing_time_seconds histogram
gate_processing_time_seconds_bucket{gate="gate_1",le="0.005"} 14532
gate_processing_time_seconds_bucket{gate="gate_1",le="0.01"} 15123
gate_processing_time_seconds_bucket{gate="gate_1",le="0.025"} 15234
gate_processing_time_seconds_bucket{gate="gate_1",le="+Inf"} 15234
gate_processing_time_seconds_sum{gate="gate_1"} 45.234
gate_processing_time_seconds_count{gate="gate_1"} 15234
```

---

## 8. Reporting

### 8.1 Daily Report Template

```
================================================================================
                    SISAS DAILY METRICS REPORT
                    Date: 2026-01-19
================================================================================

EXECUTIVE SUMMARY
-----------------
Overall Status: ✓ HEALTHY

PRIMARY KPIs
------------
Dead Letter Rate:      7.2%  [OK - Target: <10%]
Error Rate:            3.1%  [OK - Target: <5%]
Dispatch Latency p99:  42ms  [OK - Target: <100ms]

GATE PERFORMANCE
----------------
Gate 1 (Scope):       98.2% pass rate  [OK]
Gate 2 (Value Add):   89.5% pass rate  [OK]
Gate 3 (Capability):  99.1% pass rate  [OK]
Gate 4 (Irrigation):  99.8% pass rate  [OK]

VOLUME STATISTICS
-----------------
Total Signals Dispatched:  152,340
Total Signals Delivered:   149,012
Total Signals Rejected:      3,328
Total Dead Letters:            897
Total Consumer Errors:         431

TOP REJECTION REASONS
---------------------
1. LOW_VALUE:           2,145 (64.5%)
2. SCOPE_NOT_FOUND:       543 (16.3%)
3. NO_CAPABLE_CONSUMER:   412 (12.4%)
4. CHANNEL_BLOCKED:       228 (6.8%)

CONSUMER HEALTH
---------------
phase_00_consumer: HEALTHY (processed: 15,234, errors: 12)
phase_01_consumer: HEALTHY (processed: 14,892, errors: 8)
phase_02_consumer: HEALTHY (processed: 12,456, errors: 15)
phase_03_consumer: HEALTHY (processed: 11,234, errors: 5)
phase_04_consumer: HEALTHY (processed: 45,678, errors: 102)
phase_05_consumer: HEALTHY (processed: 23,456, errors: 45)
phase_06_consumer: HEALTHY (processed: 8,234, errors: 12)
phase_07_consumer: HEALTHY (processed: 4,567, errors: 8)
phase_08_consumer: HEALTHY (processed: 2,345, errors: 3)
phase_09_consumer: HEALTHY (processed: 1,234, errors: 2)

================================================================================
                    END OF REPORT
================================================================================
```

### 8.2 Weekly Trend Analysis

| Week | Dead Letter % | Error % | Latency p99 | Throughput |
|------|---------------|---------|-------------|------------|
| W-4 | 8.5% | 4.2% | 55ms | 98/sec |
| W-3 | 7.8% | 3.8% | 48ms | 105/sec |
| W-2 | 7.5% | 3.5% | 45ms | 112/sec |
| W-1 | 7.2% | 3.1% | 42ms | 128/sec |
| **Trend** | ▼ Improving | ▼ Improving | ▼ Improving | ▲ Improving |

---

*End of Metrics Dashboard Specification*
