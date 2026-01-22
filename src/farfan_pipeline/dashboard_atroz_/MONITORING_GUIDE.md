# Enhanced ATROZ Dashboard Monitoring System

## Overview

The enhanced monitoring system provides granular tracking, observation, monitoring, evaluation, and visualization capabilities for the F.A.R.F.A.N pipeline execution. It offers real-time insights per phase with comprehensive metrics collection and alerting.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Enhanced Monitoring System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐│
│  │ Pipeline Bridge  │  │ Enhanced Monitor │  │ Monitoring API││
│  │                  │→ │                  │→ │               ││
│  │ - Phase Events   │  │ - Metrics        │  │ - REST API    ││
│  │ - Job Tracking   │  │ - Alerts         │  │ - WebSocket   ││
│  │ - SISAS Metrics  │  │ - History        │  │ - Export      ││
│  └──────────────────┘  └──────────────────┘  └───────────────┘│
│           ↓                      ↓                      ↓       │
│  ┌─────────────────────────────────────────────────────────────┤
│  │              Enhanced Dashboard UI                           │
│  │  - Pipeline Flow   - Performance Charts   - Alerts Panel    │
│  │  - Phase Details   - Resource Timeline    - Export Tools    │
│  └──────────────────────────────────────────────────────────────┘
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Granular Phase Tracking

Track each pipeline phase (P00-P09) with detailed metrics:

- **Execution Time**: Precise timing in milliseconds
- **Resource Usage**: CPU and memory consumption
- **Status Tracking**: PENDING → RUNNING → COMPLETED/FAILED
- **Sub-Phase Metrics**: Track internal operations within each phase
- **Artifact Tracking**: Monitor all artifacts produced

**Example:**
```python
from farfan_pipeline.dashboard_atroz_.monitoring_enhanced import get_monitor

monitor = get_monitor()

# Start job
monitor.start_job_monitoring("job_001", "plan.pdf")

# Track phase
monitor.start_phase("job_001", "P00", "Document Assembly")
monitor.record_sub_phase("job_001", "P00", "PDF Validation", {
    "pages": 50,
    "errors": 0
})
monitor.complete_phase("job_001", "P00", artifacts=["/path/to/output.json"])
```

### 2. Real-Time Metrics Collection

Continuous monitoring of system resources:

- CPU usage percentage
- Memory consumption (MB)
- Throughput (items/second)
- Signal counts (SISAS integration)

**Example:**
```python
monitor.record_resource_usage(
    job_id="job_001",
    cpu_percent=45.5,
    memory_mb=2048.0,
    phase_id="P00"
)
```

### 3. Error and Warning Aggregation

Comprehensive error tracking across all phases:

- Error messages with timestamps
- Error context and details
- Warning collection
- Error count per phase

**Example:**
```python
monitor.fail_phase(
    job_id="job_001",
    phase_id="P00",
    error="File not found",
    error_details={"file": "/missing/file.pdf"}
)
```

### 4. Historical Data & Trends

Track performance over time:

- Phase execution history
- Performance trends (time, memory, CPU)
- Statistical analysis (avg, min, max)
- Trend visualization data

**Example:**
```python
# Get historical data
history = monitor.get_phase_history("P00", limit=10)

# Get performance trends
trends = monitor.get_performance_trends("P00", MetricType.EXECUTION_TIME)
print(f"Average: {trends['avg']}ms")
print(f"Trend: {trends['trend']}")  # Last 20 executions
```

### 5. Alert System

Configurable alerts for anomalies:

- **Slow Phase Alerts**: Execution time exceeds threshold
- **High Memory Alerts**: Memory usage exceeds limit
- **Error Count Alerts**: Too many errors in a phase
- **Phase Failure Alerts**: Critical phase failures

**Alert Thresholds:**
```python
monitor.alert_thresholds = {
    "execution_time_ms": 300000,  # 5 minutes
    "memory_usage_mb": 4096,      # 4 GB
    "cpu_usage_percent": 90.0,
    "error_count": 5,
}
```

### 6. Enhanced Dashboard UI

Beautiful, responsive dashboard at `/enhanced-monitor`:

**Features:**
- Real-time pipeline flow visualization
- Live phase status indicators
- Performance charts (execution time, memory)
- Resource usage timeline
- Active alerts panel
- Phase details table
- Export capabilities

**Color-coded Phase States:**
- 🟦 **PENDING**: Light gray
- 🟨 **RUNNING**: Yellow with pulse animation
- 🟩 **COMPLETED**: Green
- 🟥 **FAILED**: Red

## REST API Endpoints

### Job Monitoring

#### Get Job Snapshot
```
GET /api/v1/monitoring/jobs/{job_id}/snapshot
```
Returns complete execution snapshot with all phases, metrics, and timeline.

#### Get Job Progress
```
GET /api/v1/monitoring/jobs/{job_id}/progress
```
Lightweight progress endpoint for frequent polling.

#### Get Job Phases
```
GET /api/v1/monitoring/jobs/{job_id}/phases
?status=COMPLETED
```
Get all phases with optional status filter.

### Phase Monitoring

#### Get Phase Detail
```
GET /api/v1/monitoring/jobs/{job_id}/phases/{phase_id}
```
Detailed metrics for a specific phase.

#### Get Sub-Phases
```
GET /api/v1/monitoring/jobs/{job_id}/phases/{phase_id}/sub-phases
```
Sub-phase breakdown with metrics.

### Resource Monitoring

#### Get Resource Usage
```
GET /api/v1/monitoring/jobs/{job_id}/resource-usage
?phase_id=P00&limit=100
```
Resource usage timeline with CPU and memory data.

### Error Tracking

#### Get Job Errors
```
GET /api/v1/monitoring/jobs/{job_id}/errors
?phase_id=P00
```
All errors from a job, optionally filtered by phase.

#### Get Job Warnings
```
GET /api/v1/monitoring/jobs/{job_id}/warnings
?phase_id=P00
```
All warnings from a job.

### Artifacts

#### Get Job Artifacts
```
GET /api/v1/monitoring/jobs/{job_id}/artifacts
?phase_id=P00
```
List all artifacts produced, grouped by phase.

### Historical Data

#### Get Phase History
```
GET /api/v1/monitoring/phases/{phase_id}/history
?limit=10
```
Historical execution data for a phase.

#### Get Phase Trends
```
GET /api/v1/monitoring/phases/{phase_id}/trends
?metric=execution_time
```
Performance trends with statistical analysis.

**Available Metrics:**
- `execution_time`: Execution time in ms
- `memory_usage`: Memory usage in MB
- `cpu_usage`: CPU usage percentage
- `error_count`: Number of errors

### Alerts

#### Get Active Alerts
```
GET /api/v1/monitoring/alerts
?job_id=job_001&severity=ERROR&acknowledged=false
```
List active alerts with filters.

#### Acknowledge Alert
```
POST /api/v1/monitoring/alerts/{alert_id}/acknowledge
```
Mark alert as acknowledged.

#### Clear Acknowledged Alerts
```
POST /api/v1/monitoring/alerts/clear-acknowledged
```
Remove all acknowledged alerts.

### System Overview

#### Get Monitoring Summary
```
GET /api/v1/monitoring/summary
```
Overall monitoring summary with statistics.

#### Export Job Data
```
GET /api/v1/monitoring/export/{job_id}
```
Export complete monitoring data as JSON.

## WebSocket Events

Real-time updates via Socket.IO:

### Events Emitted to Client

- `pipeline_progress`: Phase progress updates
- `job_created`: New job submitted
- `job_completed`: Job finished
- `sisas_metrics_update`: SISAS metrics updates

### Events from Client

- `request_sisas_update`: Request current SISAS metrics
- `request_job_status`: Request specific job status

## Integration Example

### Backend Integration

```python
from farfan_pipeline.dashboard_atroz_.pipeline_dashboard_bridge import initialize_bridge
from farfan_pipeline.orchestration import UnifiedOrchestrator
from flask_socketio import SocketIO

# Initialize orchestrator and socket
orchestrator = UnifiedOrchestrator(config)
socketio = SocketIO(app)

# Initialize bridge (automatically integrates monitoring)
bridge = initialize_bridge(orchestrator, socketio)

# Submit job
job_id = bridge.submit_job(pdf_path, "plan.pdf")

# The bridge automatically tracks all phases and emits updates
```

### Frontend Integration

```javascript
// Connect to monitoring endpoint
const socket = io('http://localhost:5000');

// Listen for pipeline progress
socket.on('pipeline_progress', (data) => {
    console.log(`Phase ${data.phase}: ${data.progress}%`);
    updatePipelineVisualization(data);
});

// Load job details
async function loadJobDetails(jobId) {
    const response = await fetch(`/api/v1/monitoring/jobs/${jobId}/snapshot`);
    const snapshot = await response.json();
    renderDashboard(snapshot);
}

// Request real-time updates
socket.emit('request_job_status', { job_id: selectedJobId });
```

## Performance Considerations

### Metric Collection

- Resource metrics collected at configurable intervals (default: every 5 seconds)
- Historical data limited to recent executions (configurable)
- Efficient in-memory storage with optional persistence

### API Performance

- Lightweight `/progress` endpoint for frequent polling
- Full `/snapshot` endpoint for detailed views
- Pagination support for large datasets
- Efficient filtering at the API level

### Resource Usage

The monitoring system itself has minimal overhead:

- **Memory**: ~10-20MB per active job
- **CPU**: <1% for metric collection
- **Network**: WebSocket events are small (1-5KB)

## Configuration

### Alert Thresholds

Customize alert thresholds per environment:

```python
monitor = get_monitor()

# Development: More lenient
monitor.alert_thresholds = {
    "execution_time_ms": 600000,  # 10 minutes
    "memory_usage_mb": 8192,       # 8 GB
    "cpu_usage_percent": 95.0,
    "error_count": 10,
}

# Production: Stricter
monitor.alert_thresholds = {
    "execution_time_ms": 300000,  # 5 minutes
    "memory_usage_mb": 4096,      # 4 GB
    "cpu_usage_percent": 85.0,
    "error_count": 3,
}
```

### Metrics Collection Interval

```python
bridge.monitor.metrics_update_interval = 10.0  # Update every 10 seconds
```

### History Retention

```python
# Keep last 100 executions per phase
MAX_HISTORY_PER_PHASE = 100

# Automatically trim old history
if len(monitor.phase_history[phase_id]) > MAX_HISTORY_PER_PHASE:
    monitor.phase_history[phase_id] = monitor.phase_history[phase_id][-MAX_HISTORY_PER_PHASE:]
```

## Testing

Run the comprehensive test suite:

```bash
pytest tests/dashboard_atroz_/test_monitoring_enhanced.py -v
```

**Test Coverage:**
- Monitor initialization
- Job and phase lifecycle
- Resource usage tracking
- Error and warning handling
- Alert generation and acknowledgment
- Historical data collection
- Snapshot export
- Singleton pattern

## Troubleshooting

### Dashboard Not Loading

1. Check that enhanced monitoring endpoints are registered:
```python
from farfan_pipeline.dashboard_atroz_.api_monitoring_enhanced import register_monitoring_endpoints
register_monitoring_endpoints(app)
```

2. Verify the route is accessible:
```bash
curl http://localhost:5000/enhanced-monitor
```

### No Real-Time Updates

1. Check WebSocket connection:
```javascript
socket.on('connect', () => console.log('Connected'));
socket.on('disconnect', () => console.log('Disconnected'));
```

2. Verify bridge is initialized:
```python
from farfan_pipeline.dashboard_atroz_.pipeline_dashboard_bridge import get_bridge
bridge = get_bridge()
assert bridge is not None
```

### Missing Metrics

1. Ensure monitor is initialized before job submission
2. Check that bridge integration calls monitor methods
3. Verify phase events are being emitted from orchestrator

## Future Enhancements

- [ ] Persistent storage for historical data (database integration)
- [ ] Advanced chart types (heatmaps, violin plots)
- [ ] Predictive analytics (estimate completion time)
- [ ] Comparative analysis (compare multiple jobs)
- [ ] Custom dashboard widgets
- [ ] Email/Slack notifications for critical alerts
- [ ] Performance regression detection
- [ ] Anomaly detection using ML

## References

- [Pipeline Dashboard Bridge](./pipeline_dashboard_bridge.py)
- [Enhanced Monitoring Module](./monitoring_enhanced.py)
- [Monitoring API](./api_monitoring_enhanced.py)
- [Enhanced Monitor UI](./static/enhanced-monitor.html)
- [Main Dashboard Server](./dashboard_server.py)
