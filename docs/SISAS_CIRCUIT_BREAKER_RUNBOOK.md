# SISAS Circuit Breaker Operational Runbook

**Version**: 1.0.0  
**Last Updated**: 2025-12-12  
**Status**: Production  
**Audience**: DevOps, SREs, System Administrators

---

## Table of Contents

1. [Overview](#overview)
2. [Circuit Breaker States](#circuit-breaker-states)
3. [Failure Modes](#failure-modes)
4. [Monitoring & Alerts](#monitoring--alerts)
5. [Recovery Procedures](#recovery-procedures)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Emergency Procedures](#emergency-procedures)

---

## Overview

The SISAS signal registry implements a circuit breaker pattern to prevent cascading failures and provide graceful degradation when encountering repeated errors. This document describes operational procedures for monitoring, diagnosing, and recovering from circuit breaker events.

### Key Concepts

- **Circuit Breaker**: Protective mechanism that prevents repeated calls to failing operations
- **Fast-Fail**: Immediate rejection of requests when circuit is OPEN (degraded mode)
- **Self-Healing**: Automatic recovery testing after configurable timeout
- **Graceful Degradation**: Pipeline continues with reduced functionality during failures

### Default Configuration

```python
failure_threshold = 5      # Failures before opening circuit
recovery_timeout = 60.0    # Seconds before attempting recovery
success_threshold = 2      # Successes needed to close circuit
```

---

## Circuit Breaker States

### CLOSED (Normal Operation)

- **Behavior**: All requests pass through normally
- **Monitoring**: Failure count tracked but circuit remains closed
- **Action Required**: None - system is healthy

**Indicators**:
```json
{
  "state": "closed",
  "failure_count": 0,
  "healthy": true
}
```

### OPEN (Degraded Mode)

- **Behavior**: All requests fail fast without attempting operation
- **Monitoring**: Circuit opened after reaching failure threshold
- **Action Required**: Investigate root cause, check logs

**Indicators**:
```json
{
  "state": "open",
  "failure_count": 0,
  "healthy": false,
  "time_since_last_failure": 15.3
}
```

**Common Causes**:
1. Questionnaire file corruption or access issues
2. Memory exhaustion during signal extraction
3. Pydantic validation failures (malformed data)
4. Downstream dependency failures
5. Resource contention (CPU, I/O)

### HALF_OPEN (Recovery Testing)

- **Behavior**: Limited requests allowed to test recovery
- **Monitoring**: Circuit testing if underlying issue resolved
- **Action Required**: Monitor closely, may reopen or close

**Indicators**:
```json
{
  "state": "half_open",
  "success_count": 1,
  "healthy": true
}
```

---

## Failure Modes

### FM-001: Questionnaire Loading Failure

**Symptoms**:
- Circuit opens immediately on registry initialization
- Logs show `QuestionNotFoundError` or file access errors
- Health check reports degraded

**Root Causes**:
- Missing or corrupted questionnaire JSON
- File permission issues
- Incorrect file path configuration

**Resolution**:
1. Verify questionnaire file exists: `ls -la canonic_questionnaire_central/`
2. Check file permissions: `chmod 644 questionnaire.json`
3. Validate JSON syntax: `python -m json.tool questionnaire.json`
4. Restart service after fixing file issues

### FM-002: Memory Exhaustion

**Symptoms**:
- Circuit opens during signal extraction
- Logs show `MemoryError` or OOM killer events
- System metrics show high memory usage

**Root Causes**:
- Large questionnaire with excessive patterns
- Memory leak in signal building
- Insufficient system memory

**Resolution**:
1. Check available memory: `free -h`
2. Review pattern counts in questionnaire
3. Increase system memory or optimize patterns
4. Monitor with: `watch -n 1 "ps aux | grep farfan | awk '{print \$6}'"`

### FM-003: Pydantic Validation Failure

**Symptoms**:
- Circuit opens during signal pack creation
- Logs show `ValidationError` from Pydantic
- Specific fields fail type/constraint validation

**Root Causes**:
- Questionnaire schema mismatch
- Invalid pattern regex syntax
- Constraint violations (weights sum, thresholds out of range)

**Resolution**:
1. Review error logs for specific validation failures
2. Validate questionnaire against schema
3. Fix malformed patterns or constraints
4. Re-run pipeline after questionnaire correction

### FM-004: Repeated Transient Errors

**Symptoms**:
- Circuit opens after multiple retries
- Errors are non-deterministic
- Recovery succeeds but circuit reopens

**Root Causes**:
- Network instability (if loading remote resources)
- Resource contention
- Race conditions in concurrent access

**Resolution**:
1. Check for resource contention: `htop`
2. Review concurrent access patterns
3. Adjust circuit breaker thresholds if needed
4. Consider rate limiting or backoff strategies

---

## Monitoring & Alerts

### Health Check Endpoint

Query health status via registry API:

```python
from signal_registry import get_global_signal_registry

registry = get_global_signal_registry()
health = registry.health_check()

print(f"Status: {health['status']}")
print(f"Healthy: {health['healthy']}")
print(f"Circuit State: {health['circuit_breaker']['state']}")
```

### Metrics Collection

Retrieve comprehensive metrics:

```python
metrics = registry.get_metrics()

# Key metrics to monitor
print(f"Hit Rate: {metrics['hit_rate']:.2%}")
print(f"Errors: {metrics['errors']}")
print(f"Circuit State: {metrics['circuit_breaker']['state']}")
print(f"Time in State: {metrics['circuit_breaker']['time_in_current_state']:.1f}s")
```

### Recommended Alerts

Configure alerts for:

1. **Critical**: Circuit state = OPEN
   - Alert immediately, page on-call
   - SLA impact: Pipeline degraded

2. **Warning**: Circuit state = HALF_OPEN
   - Alert within 5 minutes
   - Monitor for automatic recovery

3. **Warning**: Error rate > 10%
   - Alert within 10 minutes
   - Indicates approaching threshold

4. **Info**: Circuit state changed
   - Log event for audit trail
   - Track frequency of transitions

### Log Monitoring

Key log events to monitor:

```
circuit_breaker_opened        # Circuit opened (CRITICAL)
circuit_breaker_half_open     # Testing recovery (WARNING)
circuit_breaker_closed        # Circuit recovered (INFO)
circuit_breaker_reopened      # Recovery failed (CRITICAL)
assembly_signals_failed       # Signal extraction error
```

---

## Recovery Procedures

### RP-001: Automatic Recovery (Preferred)

**When to Use**: Circuit opened due to transient issue

**Steps**:
1. Wait for recovery timeout (default: 60 seconds)
2. Circuit automatically transitions to HALF_OPEN
3. Monitor logs for successful signal extractions
4. Circuit closes automatically after success threshold met

**Expected Timeline**: 60-90 seconds total

**Validation**:
```python
health = registry.health_check()
assert health['circuit_breaker']['state'] == 'closed'
```

### RP-002: Manual Recovery

**When to Use**: Root cause fixed, want immediate recovery

**Steps**:
1. Fix underlying issue (see Failure Modes)
2. Verify fix independently
3. Manually reset circuit breaker:
   ```python
   registry.reset_circuit_breaker()
   ```
4. Monitor for successful operations

**⚠️ Warning**: Manual reset bypasses safety checks. Only use after confirming fix.

**Validation**:
```python
# Verify circuit is closed
assert registry._circuit_breaker.state == 'closed'

# Test signal extraction
try:
    signals = registry.get_assembly_signals("meso")
    print("✓ Signal extraction successful")
except Exception as e:
    print(f"✗ Signal extraction failed: {e}")
```

### RP-003: Service Restart

**When to Use**: Circuit remains open after fixes, possible state corruption

**Steps**:
1. Fix root cause
2. Gracefully stop service: `systemctl stop farfan-pipeline`
3. Verify no lingering processes: `ps aux | grep farfan`
4. Start service: `systemctl start farfan-pipeline`
5. Verify health: `systemctl status farfan-pipeline`

**Expected Timeline**: 30-60 seconds

### RP-004: Cache Clear

**When to Use**: Cached signals may be corrupted

**Steps**:
1. Clear signal registry cache:
   ```python
   registry.clear_cache()
   ```
2. Monitor for successful re-loading
3. Verify metrics show cache misses followed by hits

**Impact**: Temporary performance degradation during cache warmup

---

## Troubleshooting Guide

### Issue: Circuit Opens Immediately on Startup

**Diagnosis**:
```bash
# Check questionnaire file
ls -la canonic_questionnaire_central/questionnaire.json

# Validate JSON syntax
python -m json.tool questionnaire.json > /dev/null

# Check logs for initialization errors
tail -100 /var/log/farfan/signal_registry.log | grep -i error
```

**Resolution**: See FM-001

### Issue: Circuit Opens Under Load

**Diagnosis**:
```bash
# Check system resources
htop
free -h
iostat -x 1 10

# Monitor request rate
tail -f /var/log/farfan/signal_registry.log | grep "signal_loads"
```

**Resolution**: See FM-002 or FM-004

### Issue: Circuit Opens Intermittently

**Diagnosis**:
```bash
# Review error patterns
grep "circuit_breaker_opened" /var/log/farfan/*.log | tail -20

# Check for specific error types
grep -A 5 "SignalExtractionError" /var/log/farfan/*.log
```

**Resolution**: Review error patterns, likely FM-003 or FM-004

### Issue: Circuit Won't Close After Fix

**Diagnosis**:
```python
# Check circuit breaker state
status = registry._circuit_breaker.get_status()
print(f"State: {status['state']}")
print(f"Time in state: {status['time_in_current_state']}s")
print(f"Success count: {status['success_count']}")
```

**Resolution**:
1. If HALF_OPEN: Wait for automatic recovery or manual reset
2. If OPEN and timeout elapsed: Check if underlying issue persists
3. Use RP-002 (Manual Recovery) if confirmed fixed

---

## Emergency Procedures

### EP-001: Circuit Stuck Open During Critical Pipeline Run

**Severity**: P1 - Critical

**Steps**:
1. **DO NOT** manually reset without diagnosis
2. Check logs for root cause:
   ```bash
   tail -200 /var/log/farfan/signal_registry.log
   ```
3. If transient error (e.g., resource contention resolved):
   ```python
   registry.reset_circuit_breaker()
   ```
4. If persistent error:
   - Switch to degraded mode operation
   - Escalate to engineering team
   - Consider rollback if recent deployment

**Communication**:
- Notify stakeholders of degraded mode
- Set ETA for recovery based on diagnosis
- Document incident for post-mortem

### EP-002: Repeated Circuit Failures

**Severity**: P1 - Critical

**Steps**:
1. Identify failure pattern frequency:
   ```bash
   grep "circuit_breaker_opened" /var/log/farfan/*.log | wc -l
   ```
2. If >10 openings in 1 hour:
   - This indicates systemic issue
   - DO NOT repeatedly reset circuit
   - Implement controlled degradation
3. Escalate to engineering team immediately
4. Consider emergency maintenance window

### EP-003: Circuit Breaker Configuration Change

**Severity**: P2 - High

**When to Use**: Adjusting thresholds due to environmental conditions

**Steps**:
1. Review current configuration:
   ```python
   config = registry._circuit_breaker.config
   print(f"Failure threshold: {config.failure_threshold}")
   print(f"Recovery timeout: {config.recovery_timeout}")
   ```
2. Calculate new thresholds based on observed patterns
3. Deploy configuration change via controlled rollout
4. Monitor impact over 24 hours

**⚠️ Warning**: Changing thresholds affects system resilience. Consult with engineering team before making changes.

---

## Appendix A: Circuit Breaker State Machine

```
                                                    
      ┌──────────────────────────────────────────────────┐
      │                                                  │
      │  CLOSED (Normal)                                 │
      │  • All requests pass                             │
      │  • Tracking failures                             │
      │                                                  │
      └───────────────┬──────────────────────────────────┘
                      │
                      │ failure_count >= failure_threshold
                      ▼
      ┌──────────────────────────────────────────────────┐
      │                                                  │
      │  OPEN (Degraded)                                 │
      │  • Fast-fail all requests                        │
      │  • Wait for recovery_timeout                     │
      │                                                  │
      └───────────────┬──────────────────────────────────┘
                      │
                      │ recovery_timeout elapsed
                      ▼
      ┌──────────────────────────────────────────────────┐
      │                                                  │
      │  HALF_OPEN (Testing)                             │
      │  • Allow limited requests                        │
      │  • Test recovery                                 │
      │                                                  │
      └───┬───────────┴───────────┬──────────────────────┘
          │                       │
          │                       │ success_count >= success_threshold
          │ failure               │
          │                       ▼
          │           ┌──────────────────┐
          └──────────►│  CLOSED (Normal) │
              reopen  └──────────────────┘
```

---

## Appendix B: Configuration Reference

### Environment Variables

```bash
# Circuit breaker configuration (optional, defaults shown)
export FARFAN_CB_FAILURE_THRESHOLD=5
export FARFAN_CB_RECOVERY_TIMEOUT=60
export FARFAN_CB_SUCCESS_THRESHOLD=2

# Monitoring configuration
export FARFAN_HEALTH_CHECK_INTERVAL=30
export FARFAN_METRICS_EXPORT_ENABLED=true
```

### Programmatic Configuration

```python
from signal_registry import CircuitBreakerConfig, CircuitBreaker

# Custom configuration
config = CircuitBreakerConfig(
    failure_threshold=10,      # More tolerant
    recovery_timeout=120.0,    # Longer recovery window
    success_threshold=3,       # More successes required
)

breaker = CircuitBreaker(config=config)
```

---

## Appendix C: Metrics Reference

### Circuit Breaker Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `circuit_breaker.state` | Enum | Current circuit state (CLOSED, OPEN, HALF_OPEN) |
| `circuit_breaker.failure_count` | Counter | Failures since last reset |
| `circuit_breaker.success_count` | Counter | Successes in HALF_OPEN state |
| `circuit_breaker.time_since_last_failure` | Duration | Time since last failure (seconds) |
| `circuit_breaker.time_in_current_state` | Duration | Time in current state (seconds) |

### Registry Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `registry.cache_hit_rate` | Percentage | Cache effectiveness |
| `registry.error_count` | Counter | Total errors encountered |
| `registry.total_requests` | Counter | Total signal requests |
| `registry.signal_loads` | Counter | Signals loaded from source |

---

## Support & Escalation

### Internal Contacts

- **On-Call SRE**: [pager-duty@example.com]
- **Signal System Lead**: [signal-lead@example.com]
- **Engineering Team**: [farfan-eng@example.com]

### Escalation Path

1. **L1**: Operations team attempts standard recovery
2. **L2**: SRE team diagnoses and implements fixes
3. **L3**: Engineering team for systemic issues

### Post-Incident Review

After circuit breaker events:
1. Document incident timeline
2. Identify root cause
3. Implement preventive measures
4. Update this runbook with lessons learned

---

**Document Maintainer**: F.A.R.F.A.N DevOps Team  
**Review Frequency**: Quarterly  
**Next Review**: 2025-03-12
