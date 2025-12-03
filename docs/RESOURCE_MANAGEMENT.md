# Adaptive Resource Management System

## Overview

The Adaptive Resource Management System provides dynamic resource allocation, graceful degradation, circuit breakers, and priority-based scheduling for F.A.R.F.A.N policy analysis executors. It integrates seamlessly with the existing `ResourceLimits` class to ensure stable, efficient execution under varying resource constraints.

## Key Features

### 1. Dynamic Resource Allocation
- Real-time monitoring of CPU and memory usage
- Adaptive worker budget adjustment based on resource pressure
- Priority-based resource allocation (critical executors first)

### 2. Graceful Degradation
- Multiple degradation strategies activated at different pressure levels:
  - **Elevated**: Reduce entity limits by 20%
  - **High**: Skip optional analysis, disable expensive computations
  - **Critical**: Use simplified methods, reduce entity limits by 50%
  - **Emergency**: Full degradation with minimal resource usage

### 3. Circuit Breakers
- Automatic failure detection and isolation
- Three states: CLOSED, OPEN, HALF_OPEN
- Memory threshold protection
- Automatic recovery after timeout
- Manual reset capability

### 4. Priority-Based Scheduling
- **Critical Priority**: D3-Q3 (Traceability), D4-Q2 (Causal Chains)
- **High Priority**: D3-Q2, D4-Q1, D2-Q3
- **Normal Priority**: All other executors
- Priority affects resource allocation and timeout values

### 5. Comprehensive Observability
- Structured logging for all resource events
- Configurable alerting with multiple channels (log, webhook, signal, stdout)
- Historical trend analysis
- Alert rate limiting to prevent spam

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Orchestrator                             │
├─────────────────────────────────────────────────────────────┤
│  ResourceLimits (existing)                                   │
│    ↓                                                          │
│  AdaptiveResourceManager                                     │
│    ├─→ Circuit Breakers                                      │
│    ├─→ Degradation Strategies                                │
│    ├─→ Allocation Policies                                   │
│    └─→ Executor Metrics                                      │
│         ↓                                                     │
│  ResourceAlertManager                                        │
│    ├─→ Alert Thresholds                                      │
│    ├─→ Alert Channels                                        │
│    └─→ Alert History                                         │
│         ↓                                                     │
│  ResourceAwareExecutor                                       │
│    └─→ Wraps MethodExecutor                                 │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Basic Setup

```python
from farfan_pipeline.core.orchestrator import (
    ResourceLimits,
    create_resource_manager,
    integrate_with_orchestrator,
)

# Create resource limits
resource_limits = ResourceLimits(
    max_memory_mb=4096.0,
    max_cpu_percent=85.0,
    max_workers=32,
)

# Create adaptive resource manager
resource_manager, alert_manager = create_resource_manager(
    resource_limits=resource_limits,
    enable_circuit_breakers=True,
    enable_degradation=True,
    enable_alerts=True,
)

# Integrate with orchestrator
orchestrator = Orchestrator(resource_limits=resource_limits)
integrate_with_orchestrator(
    orchestrator,
    enable_circuit_breakers=True,
    enable_degradation=True,
    enable_alerts=True,
)
```

### Using ResourceAwareExecutor

```python
from farfan_pipeline.core.orchestrator import (
    ResourceAwareExecutor,
    wrap_method_executor,
)

# Wrap method executor with resource management
resource_aware_executor = wrap_method_executor(
    method_executor=method_executor,
    resource_manager=resource_manager,
)

# Execute with resource management
result = await resource_aware_executor.execute_with_resource_management(
    executor_id="D3-Q3",
    context={"document_text": "...", "tables": []},
)
```

### Applying Degradation in Executors

```python
from farfan_pipeline.core.orchestrator import ResourceConstraints

def execute(self, context: dict[str, Any]) -> dict[str, Any]:
    # Check if expensive computations should be skipped
    if ResourceConstraints.should_skip_expensive_computation(context):
        return self._simplified_execution(context)
    
    # Get entity limit with degradation applied
    max_entities = ResourceConstraints.get_entity_limit(
        context, default=1000
    )
    
    # Check if simplified methods should be used
    if ResourceConstraints.should_use_simplified_methods(context):
        method = self._simple_method
    else:
        method = self._complex_method
    
    return method(context, max_entities=max_entities)
```

### Custom Allocation Policies

```python
from farfan_pipeline.core.orchestrator import (
    ResourceAllocationPolicy,
    ExecutorPriority,
)

# Define custom policy
policy = ResourceAllocationPolicy(
    executor_id="D5-Q2",
    priority=ExecutorPriority.HIGH,
    min_memory_mb=256.0,
    max_memory_mb=1024.0,
    min_workers=2,
    max_workers=6,
    is_memory_intensive=True,
)

# Register policy
resource_manager.register_allocation_policy(policy)
```

### Monitoring and Alerts

```python
from farfan_pipeline.core.orchestrator import (
    AlertChannel,
    get_resource_status,
)

# Get comprehensive status
status = get_resource_status(orchestrator)
print(f"Current pressure: {status['current_pressure']}")
print(f"Active executors: {status['active_executors']}")
print(f"Circuit breakers: {status['circuit_breakers']}")

# Configure alerts
alert_manager = ResourceAlertManager(
    channels=[AlertChannel.LOG, AlertChannel.WEBHOOK],
    webhook_url="https://alerts.example.com/webhook",
)

# Custom alert callback
def custom_alert_handler(event):
    print(f"ALERT: {event.pressure_level} - {event.message}")
    # Send to monitoring system, Slack, etc.

resource_manager = AdaptiveResourceManager(
    resource_limits=resource_limits,
    alert_callback=custom_alert_handler,
)
```

### Circuit Breaker Management

```python
from farfan_pipeline.core.orchestrator import reset_circuit_breakers

# Check if executor can execute
can_execute, reason = resource_manager.can_execute("D3-Q3")
if not can_execute:
    print(f"Executor blocked: {reason}")

# Reset all circuit breakers
results = reset_circuit_breakers(orchestrator)
print(f"Reset results: {results}")

# Reset specific circuit breaker
success = resource_manager.reset_circuit_breaker("D3-Q3")
```

## Resource Pressure Levels

| Level | Memory % | CPU % | Actions |
|-------|----------|-------|---------|
| Normal | < 65% | < 65% | No restrictions |
| Elevated | 65-75% | 65-75% | Reduce entity limits by 20% |
| High | 75-85% | 75-85% | Skip optional analysis, disable expensive computations |
| Critical | 85-95% | 85-95% | Use simplified methods, reduce entity limits by 50% |
| Emergency | > 95% | > 95% | Minimal processing, 70% entity limit reduction |

## Circuit Breaker Configuration

```python
from farfan_pipeline.core.orchestrator import CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,           # Open after 5 failures
    timeout_seconds=60.0,          # Stay open for 60s
    half_open_timeout=30.0,        # Half-open state duration
    memory_threshold_mb=2048.0,    # Open if memory exceeds 2GB
    success_threshold=3,           # Close after 3 successes in half-open
)
```

## Degradation Strategies

### 1. Reduce Entity Limits
- **Threshold**: Elevated
- **Effect**: Limits number of processed entities
- **Factor**: 0.8 (20% reduction) at elevated, 0.5 at critical, 0.3 at emergency

### 2. Skip Optional Analysis
- **Threshold**: High
- **Effect**: Skips non-essential analysis steps
- **Usage**: Check `ResourceConstraints.should_skip_optional_analysis()`

### 3. Disable Expensive Computations
- **Threshold**: High
- **Effect**: Disables computationally intensive operations
- **Usage**: Check `ResourceConstraints.should_skip_expensive_computation()`

### 4. Use Simplified Methods
- **Threshold**: Critical
- **Effect**: Switches to lighter-weight algorithms
- **Usage**: Check `ResourceConstraints.should_use_simplified_methods()`

### 5. Reduce Embedding Dimensions
- **Threshold**: Critical
- **Effect**: Reduces vector dimensions for embeddings
- **Usage**: Use `ResourceConstraints.get_embedding_dimensions()`

## Alert Configuration

### Alert Severities
- **INFO**: General information (degradation started)
- **WARNING**: Potential issues (high resource usage, circuit breaker opened)
- **ERROR**: Problems requiring attention (multiple circuit breakers)
- **CRITICAL**: Urgent issues (emergency pressure, system instability)

### Alert Channels
- **LOG**: Structured logging (default)
- **WEBHOOK**: HTTP POST to external endpoint
- **SIGNAL**: Custom callback function
- **STDOUT**: Console output with color coding

### Alert Rate Limiting
- Memory warnings: Every 5 minutes
- CPU warnings: Every 5 minutes
- Pressure alerts: Every 2-10 minutes (based on level)
- Circuit breaker alerts: Every 5 minutes
- Degradation alerts: Every 10 minutes

## Metrics and Observability

### Executor Metrics
```python
metrics = resource_manager.get_executor_metrics("D3-Q3")
# Returns:
# {
#     "executor_id": "D3-Q3",
#     "total_executions": 150,
#     "successful_executions": 145,
#     "failed_executions": 5,
#     "success_rate_percent": 96.67,
#     "avg_memory_mb": 512.3,
#     "peak_memory_mb": 1024.0,
#     "avg_duration_ms": 2450.5,
#     "circuit_breaker_state": "closed"
# }
```

### Resource Status
```python
status = resource_manager.get_resource_status()
# Returns comprehensive status including:
# - Current pressure level
# - Resource usage (CPU, memory, workers)
# - Active executors
# - Executor metrics
# - Active degradation strategies
# - Circuit breaker states
# - Recent pressure events
```

### Alert Summary
```python
summary = alert_manager.get_alert_summary()
# Returns:
# {
#     "total_alerts": 45,
#     "last_hour": 8,
#     "last_24_hours": 45,
#     "by_severity": {
#         "info": 20,
#         "warning": 15,
#         "error": 8,
#         "critical": 2
#     },
#     "recent_alerts": [...]
# }
```

## Best Practices

### 1. Configure Resource Limits Appropriately
```python
# For production systems
resource_limits = ResourceLimits(
    max_memory_mb=8192.0,    # 8GB
    max_cpu_percent=85.0,     # Leave headroom
    max_workers=32,           # Based on available cores
    min_workers=4,            # Minimum for critical executors
)
```

### 2. Implement Degradation-Aware Code
```python
def analyze_document(self, context):
    constraints = ResourceConstraints.get_constraints(context)
    
    if constraints["use_simplified_methods"]:
        return self._simple_analysis(context)
    
    max_chunks = ResourceConstraints.get_entity_limit(
        context, default=1000
    )
    
    results = self._detailed_analysis(context, max_chunks)
    
    if not constraints["skip_optional_analysis"]:
        results["additional_insights"] = self._deep_analysis(results)
    
    return results
```

### 3. Monitor Circuit Breakers
```python
# Periodic health check
async def health_check():
    status = resource_manager.get_resource_status()
    open_breakers = [
        executor_id
        for executor_id, breaker in status["circuit_breakers"].items()
        if breaker["state"] == "open"
    ]
    
    if open_breakers:
        logger.warning(f"Open circuit breakers: {open_breakers}")
        # Alert operations team
```

### 4. Custom Priority for Domain-Specific Executors
```python
# High priority for financial analysis
resource_manager.register_allocation_policy(
    ResourceAllocationPolicy(
        executor_id="D1-Q3",  # Budget allocation
        priority=ExecutorPriority.HIGH,
        min_memory_mb=256.0,
        max_memory_mb=768.0,
        min_workers=2,
        max_workers=6,
    )
)
```

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_resource_manager.py -v
```

Test categories:
- Circuit breaker functionality
- Degradation strategies
- Resource pressure assessment
- Alert generation and rate limiting
- Executor metrics tracking
- Integration with orchestrator

## Troubleshooting

### Circuit Breaker Stuck Open
```python
# Check breaker status
breaker = resource_manager.circuit_breakers["D3-Q3"]
print(f"State: {breaker.state}")
print(f"Failures: {breaker.failure_count}")
print(f"Last failure: {breaker.last_failure_time}")

# Manual reset
resource_manager.reset_circuit_breaker("D3-Q3")
```

### Excessive Degradation
```python
# Check current pressure
print(f"Pressure: {resource_manager.current_pressure}")

# Review recent events
status = resource_manager.get_resource_status()
for event in status["recent_pressure_events"]:
    print(f"{event['timestamp']}: {event['level']} - {event['message']}")

# Adjust thresholds if needed
resource_limits.max_memory_mb = 16384.0  # Increase limit
```

### Missing Alerts
```python
# Verify alert configuration
print(f"Channels: {alert_manager.channels}")
print(f"Webhook: {alert_manager.webhook_url}")

# Check alert history
summary = alert_manager.get_alert_summary()
print(f"Total alerts: {summary['total_alerts']}")

# Test alert generation
from farfan_pipeline.core.orchestrator.resource_manager import (
    ResourcePressureEvent,
    ResourcePressureLevel,
)

test_event = ResourcePressureEvent(
    timestamp=datetime.utcnow(),
    pressure_level=ResourcePressureLevel.CRITICAL,
    cpu_percent=90.0,
    memory_mb=3500.0,
    memory_percent=87.5,
    worker_count=8,
    active_executors=5,
    degradation_applied=["use_simplified_methods"],
    circuit_breakers_open=["D3-Q3"],
    message="Test alert",
)

alerts = alert_manager.process_event(test_event)
print(f"Generated {len(alerts)} alerts")
```

## Performance Impact

The resource management system has minimal overhead:
- Pressure assessment: ~1-5ms per check
- Circuit breaker check: <0.1ms
- Degradation config lookup: <0.1ms
- Metric recording: <1ms

Total overhead per executor: ~5-10ms (< 0.5% for typical executions)

## Future Enhancements

- Machine learning-based pressure prediction
- Dynamic threshold adjustment based on historical patterns
- Integration with Kubernetes HPA for cluster-level scaling
- Real-time dashboard for resource visualization
- Automated remediation actions
- Integration with OpenTelemetry for distributed tracing
