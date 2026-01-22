# ATROZ Analytical Dashboard v2.0 - Complete Integration Guide

**Fully Automated Dashboard for F.A.R.F.A.N PDET Municipal Plan Analysis**
**With Full SISAS Integration, Real-Time Signal Flow, and Orchestrator Wiring**

---

## 📋 Overview

ATROZ Dashboard v2.0 is a comprehensive real-time analytical dashboard that integrates with the UnifiedOrchestrator and SISAS (Signal Distribution Orchestrator System) to provide live monitoring and analysis of PDET municipal plan evaluations.

### Key Features

✅ **Real-time Pipeline Monitoring** - Live updates from orchestrator phases
✅ **SISAS Integration** - Full signal flow visualization and metrics
✅ **170 PDET Municipalities** - Authentic Colombian territorial data
✅ **300 Micro Questions** - Complete questionnaire tracking
✅ **4-Gate Validation** - Signal validation status monitoring
✅ **17 Consumer Tracking** - Phase consumer health and metrics
✅ **10 Signal Extractors** - SOTA NLP extraction monitoring
✅ **WebSocket Live Updates** - Sub-second latency updates

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ATROZ DASHBOARD v2.0 ARCHITECTURE                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ FRONTEND                                                            │   │
│  │  - dashboard.html (Constellation View)                              │   │
│  │  - sisas-ecosystem-view.html (SISAS View)                          │   │
│  │  - atroz-sisas-state.js (Enhanced State Management)                │   │
│  │  - Socket.IO client (WebSocket)                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↕                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ DASHBOARD SERVER (Flask + SocketIO)                                │   │
│  │  - dashboard_server.py                                             │   │
│  │  - API v1 endpoints (15+ endpoints)                                │   │
│  │  - WebSocket event handlers                                        │   │
│  │  - Real PDET data integration                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↕                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ PIPELINE-DASHBOARD BRIDGE                                          │   │
│  │  - pipeline_dashboard_bridge.py                                    │   │
│  │  - Job tracking and state management                               │   │
│  │  - Phase event interception                                        │   │
│  │  - SISAS metrics collection                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↕                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ UNIFIED ORCHESTRATOR                                               │   │
│  │  - orchestrator.py                                                 │   │
│  │  - 10 phase executors (P00-P09)                                    │   │
│  │  - Phase signal emission                                           │   │
│  │  - SISAS integration hub                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↕                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SISAS (Signal Distribution Orchestrator)                           │   │
│  │  - SignalDistributionOrchestrator (SDO)                            │   │
│  │  - 17 consumers (phase_00 - phase_09 + providers)                 │   │
│  │  - 10 extractors (MC01-MC10)                                       │   │
│  │  - 8 vehicles (loader, irrigator, registry, etc.)                 │   │
│  │  - 4-gate validation                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
dashboard_atroz_/
├── dashboard_server.py               # Main Flask server with SocketIO
├── pipeline_dashboard_bridge.py      # Bridge between orchestrator and dashboard
├── pdet_dashboard_adapter.py         # Real PDET data adapter
├── pdet_colombia_data.py             # 170 PDET municipalities data
├── dashboard_data_service.py         # Data transformation service
├── signals_service.py                # FastAPI signals service (existing)
├── signal_extraction_sota.py         # SOTA NLP extraction (existing)
├── api_v1_router.py                  # API v1 router (existing)
│
├── static/
│   ├── js/
│   │   ├── atroz-dashboard-integration.js    # Base integration
│   │   └── atroz-sisas-state.js              # NEW: Enhanced SISAS state
│   ├── sisas-ecosystem-view.html             # NEW: SISAS visualization view
│   └── admin.html                            # Admin control panel
│
└── README_ATROZ_v2.md                        # This file
```

---

## 🚀 Quick Start

### 1. Start the Dashboard Server

```bash
cd src/farfan_pipeline/dashboard_atroz_

# Option A: Standalone mode (mock orchestrator)
python dashboard_server.py

# Option B: Integrated mode (with orchestrator)
python -c "
from dashboard_server import app, socketio, initialize_orchestrator_integration
from farfan_pipeline.orchestration.orchestrator import UnifiedOrchestrator

# Initialize orchestrator
orchestrator = UnifiedOrchestrator(config)

# Connect to dashboard
initialize_orchestrator_integration(orchestrator)

# Start server
socketio.run(app, host='0.0.0.0', port=5000)
"
```

### 2. Access the Dashboards

- **Main Dashboard**: http://localhost:5000/
- **SISAS Ecosystem View**: http://localhost:5000/static/sisas-ecosystem-view.html
- **Admin Panel**: http://localhost:5000/static/admin.html

### 3. Upload a PDF for Analysis

```bash
curl -X POST http://localhost:5000/api/upload/plan \
  -F "file=@/path/to/plan.pdf"

# Response:
# {
#   "message": "File uploaded successfully",
#   "job_id": "job_1737500000000"
# }
```

### 4. Monitor Progress via WebSocket

```javascript
const socket = io('http://localhost:5000');

socket.on('pipeline_progress', (data) => {
  console.log('Phase:', data.phase_name);
  console.log('Progress:', data.progress + '%');
  console.log('SISAS Metrics:', data.sisas_metrics);
});
```

---

## 🔌 API Endpoints

### Region Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/regions` | GET | Get all 16 PDET regions with summaries |
| `/api/v1/regions/<region_id>` | GET | Get detailed region analysis |
| `/api/v1/regions/<region_id>/questions` | GET | Get 300 micro question scores |
| `/api/v1/regions/<region_id>/evidence` | GET | Get evidence stream for region |
| `/api/v1/regions/connections` | GET | Get region connections for graph |

### Job Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/jobs` | GET | List all jobs (active + completed) |
| `/api/v1/jobs/<job_id>` | GET | Get job status with phase breakdown |
| `/api/v1/jobs/<job_id>/logs` | GET | Get execution logs for job |
| `/api/upload/plan` | POST | Upload PDF and start pipeline |

### SISAS Integration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/sisas/status` | GET | Get SISAS integration status |
| `/api/v1/sisas/metrics` | GET | Get real-time SISAS metrics |
| `/api/v1/sisas/consumers` | GET | Get all 17 consumer statuses |
| `/api/v1/sisas/dead-letter` | GET | Get dead letter queue contents |

### Canonical Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/canonical/questions` | GET | Get all 300 canonical questions |
| `/api/v1/canonical/questions/<qid>` | GET | Get single question detail |
| `/api/v1/canonical/dimensions` | GET | Get 6 dimensions metadata |
| `/api/v1/canonical/policy-areas` | GET | Get 10 policy areas metadata |
| `/api/v1/canonical/clusters` | GET | Get 4 clusters metadata |

---

## 🔄 WebSocket Events

### Client → Server

| Event | Payload | Description |
|-------|---------|-------------|
| `connect` | - | Client connects to server |
| `request_sisas_update` | - | Request current SISAS metrics |
| `request_job_status` | `{job_id}` | Request specific job status |

### Server → Client

| Event | Payload | Description |
|-------|---------|-------------|
| `system_status` | `{status, version, sisas_enabled}` | System online status |
| `sisas_metrics_update` | `{timestamp, metrics}` | Periodic SISAS metrics |
| `job_created` | `{job_id, filename}` | New job submitted |
| `pipeline_progress` | `{job_id, phase, progress, sisas_metrics}` | Phase progress with SISAS |
| `pipeline_completed` | `{job_id, status, result_url}` | Job completed |
| `sisas_signal_emitted` | `{signal_id, type, payload}` | Signal emitted event |
| `evidence_extracted` | `{source, page, text, question_id}` | Evidence found |

---

## 📊 SISAS Integration Details

### Signal Flow Lifecycle

```
1. Phase Start
   └─> orchestrator._emit_phase_signal(PHASE_START)
       └─> SDO.dispatch(signal)
           └─> 4-Gate Validation
               ├─> Gate 1: Scope Check ✓
               ├─> Gate 2: Value Validation ✓
               ├─> Gate 3: Capability Check ✓
               └─> Gate 4: Channel Routing ✓
                   └─> Consumer.on_signal(signal)
                       └─> Dashboard Update (WebSocket)

2. Phase Complete
   └─> orchestrator._emit_phase_signal(PHASE_COMPLETE)
       └─> [same flow]
           └─> Dashboard Update with results
```

### Consumer Architecture

17 Phase Consumers:
- `phase_00_assembly_consumer` - Document assembly
- `phase_01_extraction_consumer` - Text extraction
- `phase_02_enrichment_consumer` - Semantic enrichment
- `phase_03_validation_consumer` - Layer scoring validation
- `phase_04_micro_consumer` - 300 micro questions
- `phase_05_meso_consumer` - 4 cluster analysis
- `phase_06_macro_consumer` - 6 dimension analysis
- `phase_07_aggregation_consumer` - Cross-dimensional
- `phase_08_integration_consumer` - Integration validation
- `phase_09_report_consumer` - Report generation
- `providers_consumer` - Context providers (PDET, Colombia)

### Signal Extractors (MC01-MC10)

| Extractor | Name | Capability |
|-----------|------|------------|
| MC01 | StructuralMarkerExtractor | Document structure analysis |
| MC02 | QuantitativeTripletExtractor | Numeric data extraction |
| MC03 | NormativeReferenceExtractor | Legal references |
| MC04 | ProgrammaticHierarchyExtractor | Program structure |
| MC05 | FinancialChainExtractor | Budget and finance |
| MC06 | PopulationDisaggregationExtractor | Demographics |
| MC07 | TemporalConsistencyExtractor | Timeline analysis |
| MC08 | CausalVerbExtractor | Action verbs |
| MC09 | InstitutionalNERExtractor | Colombian entities (473 patterns) |
| MC10 | SemanticRelationshipExtractor | Relationship mapping |

---

## 🎯 Use Cases

### 1. Real-Time Pipeline Monitoring

Monitor pipeline execution in real-time as PDFs are processed through all 10 phases.

**Dashboard View**: Main Dashboard (Constellation View)

**Features**:
- Live phase progress bars
- SISAS metrics overlay
- Evidence stream ticker
- Consumer health indicators

### 2. SISAS Ecosystem Visualization

Visualize the entire SISAS signal distribution system.

**Dashboard View**: SISAS Ecosystem View

**Features**:
- 10 policy area extraction progress
- 17 consumer status cards
- 4-gate validation statistics
- Signal throughput metrics
- Entity recognition results

### 3. Regional Analysis Deep Dive

Explore detailed analysis for any of the 16 PDET regions.

**Dashboard View**: Main Dashboard → Click Region Node

**Features**:
- Macro score and band
- 4 cluster (meso) breakdown
- 300 question (micro) matrix
- Evidence stream filtered by region

### 4. Historical Job Review

Review completed pipeline jobs and their results.

**API Endpoint**: `GET /api/v1/jobs`

**Response**:
```json
{
  "active_jobs": [],
  "completed_jobs": [
    {
      "job_id": "job_1737500000000",
      "filename": "PDT_Arauca.pdf",
      "status": "COMPLETED",
      "total_progress": 100,
      "sisas_metrics": {
        "signalsEmitted": 142,
        "signalsConsumed": 138,
        "deadLetterRate": 0.028
      }
    }
  ]
}
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Dashboard Server
export ATROZ_API_URL="http://localhost:5000"
export ATROZ_ENABLE_REALTIME="true"
export ATROZ_CACHE_TIMEOUT="300000"
export ATROZ_REFRESH_INTERVAL="60000"

# Flask
export FLASK_ENV="development"
export MANIFEST_SECRET_KEY="your-secret-key"

# SISAS
export ENABLE_SISAS="true"
export SISAS_LOG_LEVEL="INFO"
```

### Dashboard Server Configuration

```python
# In dashboard_server.py

app.config["SECRET_KEY"] = os.getenv("MANIFEST_SECRET_KEY", "atroz-secret-key")
app.config["UPLOAD_FOLDER"] = str(DATA_DIR / "uploads")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="gevent"
)
```

---

## 📈 Performance Metrics

### Typical Pipeline Execution

| Phase | Duration | SISAS Signals | Consumer |
|-------|----------|---------------|----------|
| P00: Assembly | 10-15s | 3-5 | phase_00_assembly_consumer |
| P01: Extraction | 30-60s | 8-12 | phase_01_extraction_consumer |
| P02: Enrichment | 45-90s | 15-25 | phase_02_enrichment_consumer |
| P03: Validation | 20-30s | 10-15 | phase_03_validation_consumer |
| P04: Micro (300Q) | 2-5m | 40-60 | phase_04_micro_consumer |
| P05: Meso (4CL) | 30-60s | 8-12 | phase_05_meso_consumer |
| P06: Macro (6DIM) | 30-60s | 6-10 | phase_06_macro_consumer |
| P07: Aggregation | 20-30s | 5-8 | phase_07_aggregation_consumer |
| P08: Integration | 15-25s | 3-5 | phase_08_integration_consumer |
| P09: Report | 10-20s | 2-4 | phase_09_report_consumer |

**Total**: ~5-10 minutes for full pipeline

### SISAS Metrics

- **Signal Throughput**: 20-30 signals/minute
- **Gate Pass Rate**: 95-99%
- **Dead Letter Rate**: <5%
- **Consumer Latency**: <500ms average

---

## 🐛 Troubleshooting

### Dashboard shows OFFLINE status

**Cause**: Pipeline bridge not initialized or orchestrator not running

**Solution**:
```python
# Ensure bridge is initialized
from dashboard_server import initialize_orchestrator_integration
initialize_orchestrator_integration(orchestrator)
```

### No SISAS metrics appearing

**Cause**: SISAS not enabled in orchestrator config

**Solution**:
```python
config = OrchestratorConfig(
    enable_sisas=True,
    # ... other config
)
```

### WebSocket disconnects frequently

**Cause**: Firewall or proxy issues

**Solution**:
```javascript
// Use long polling fallback
const socket = io('http://localhost:5000', {
    transports: ['polling', 'websocket']
});
```

### 404 on /api/v1/* endpoints

**Cause**: API v1 router not mounted

**Solution**: Check dashboard_server.py includes all API v1 endpoints

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Start dashboard server
python dashboard_server.py

# 2. In another terminal, upload a test PDF
curl -X POST http://localhost:5000/api/upload/plan \
  -F "file=@test_plan.pdf"

# 3. Monitor via WebSocket (using websocat)
websocat ws://localhost:5000/socket.io/?transport=websocket

# 4. Check SISAS metrics
curl http://localhost:5000/api/v1/sisas/metrics | jq
```

### Integration Testing

```python
# test_dashboard_integration.py

import pytest
from dashboard_server import app, initialize_orchestrator_integration
from orchestrator import UnifiedOrchestrator

def test_bridge_initialization():
    orchestrator = UnifiedOrchestrator(test_config)
    initialize_orchestrator_integration(orchestrator)
    assert app.pipeline_bridge is not None

def test_job_submission():
    client = app.test_client()
    response = client.post('/api/upload/plan', data={'file': test_pdf})
    assert response.status_code == 202
    assert 'job_id' in response.json
```

---

## 📚 Additional Resources

- **Orchestrator Documentation**: `../orchestration/README.md`
- **SISAS Integration Hub**: `../orchestration/sisas_integration_hub.py`
- **Signal Service API**: `signals_service.py`
- **PDET Data Source**: `pdet_colombia_data.py` (170 municipalities)
- **Canonical Questionnaire**: `../../canonic_questionnaire_central/`

---

## 🤝 Contributing

When adding new features to the dashboard:

1. **Backend**: Add API endpoint to `dashboard_server.py`
2. **Bridge**: Extend `PipelineDashboardBridge` if needed
3. **Frontend**: Update state manager in `atroz-sisas-state.js`
4. **WebSocket**: Add event handler in dashboard server and frontend
5. **Test**: Add integration test
6. **Document**: Update this README

---

## 📝 Changelog

### v2.0.0 (2024-01-21)

- ✅ Full SISAS integration with real-time signal flow
- ✅ Pipeline-Dashboard Bridge for orchestrator connection
- ✅ Real PDET data (170 municipalities across 16 regions)
- ✅ Enhanced state management with SISAS tracking
- ✅ SISAS Ecosystem visualization view
- ✅ 15+ new API v1 endpoints
- ✅ WebSocket enhancements with SISAS metrics
- ✅ 4-gate validation status monitoring
- ✅ 17 consumer health tracking
- ✅ Evidence stream real-time updates

### v1.0.0 (Previous)

- ✅ Basic dashboard with mock data
- ✅ Constellation view visualization
- ✅ Admin panel
- ✅ WebSocket support

---

## 📄 License

Copyright © 2024 F.A.R.F.A.N PDET Analysis Project
All rights reserved.

---

## 👥 Support

For issues or questions:
- GitHub Issues: `ALOHAALOHAALOJHA/FARFAN_MCDPP`
- Documentation: This README and linked resources
- Code Review: `orchestrator.py`, `dashboard_server.py`, `pipeline_dashboard_bridge.py`

---

**Built with ❤️ for Colombian PDET Territorial Development**
