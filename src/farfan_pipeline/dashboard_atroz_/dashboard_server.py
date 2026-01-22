import logging
import os
import time

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from farfan_pipeline.phases.Phase_00.phase0_10_00_paths import PROJECT_ROOT, DATA_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("atroz_dashboard")

# Initialize Flask App
app = Flask(__name__, static_folder=str(PROJECT_ROOT), static_url_path="")
app.config["SECRET_KEY"] = os.getenv("MANIFEST_SECRET_KEY", "atroz-secret-key")
app.config["UPLOAD_FOLDER"] = str(DATA_DIR / "uploads")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max upload

# Enable CORS for development
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

# Register enhanced monitoring endpoints
register_monitoring_endpoints(app)

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Import real PDET data and bridge
from farfan_pipeline.dashboard_atroz_.pdet_dashboard_adapter import (
    load_pdet_regions_for_dashboard,
    get_region_connections,
    get_region_detail,
)
from farfan_pipeline.dashboard_atroz_.pipeline_dashboard_bridge import (
    PipelineDashboardBridge,
    initialize_bridge,
    get_bridge,
)
from farfan_pipeline.dashboard_atroz_.api_monitoring_enhanced import register_monitoring_endpoints

# Global state
pipeline_status = {
    "active_jobs": [],
    "completed_jobs": [],
    "system_metrics": {"cpu_usage": 0, "memory_usage": 0, "uptime": 0},
}

# Load real PDET data (replacing mock data)
PDET_REGIONS = load_pdet_regions_for_dashboard(include_scores=True, score_source="random")
REGION_CONNECTIONS = get_region_connections()

# Pipeline bridge (will be initialized when orchestrator is available)
pipeline_bridge: PipelineDashboardBridge = None

# Evidence stream - will be populated by pipeline analysis
EVIDENCE_STREAM = [
    {
        "source": "PDT Sección 3.2",
        "page": 45,
        "text": "Implementación de estrategias municipales",
        "region": "arauca",
    },
    {
        "source": "PDT Capítulo 4",
        "page": 67,
        "text": "Articulación con Decálogo DDHH",
        "region": "catatumbo",
    },
    {
        "source": "Anexo Técnico",
        "page": 112,
        "text": "Indicadores de cumplimiento territorial",
        "region": "montes_maria",
    },
    {
        "source": "PDT Sección 5.1",
        "page": 89,
        "text": "Proyección territorial 2030",
        "region": "putumayo",
    },
    {
        "source": "PATR Capítulo 2",
        "page": 34,
        "text": "Cadenas de valor agropecuarias",
        "region": "bajo_cauca",
    },
    {
        "source": "PDT Sección 6.3",
        "page": 156,
        "text": "Mecanismos de participación ciudadana",
        "region": "choco",
    },
]

from flask import Flask, Response


@app.route("/")
def index():
    dashboard_path = PROJECT_ROOT / "dashboard.html"
    with open(str(dashboard_path), encoding="utf-8") as f:
        return Response(f.read(), mimetype="text/html")


@app.route("/api/pdet-regions", methods=["GET"])
def get_pdet_regions():
    """Return PDET regions with current scores"""
    return jsonify(PDET_REGIONS)


@app.route("/api/evidence", methods=["GET"])
def get_evidence():
    """Return current evidence stream"""
    return jsonify(EVIDENCE_STREAM)


@app.route("/api/upload/plan", methods=["POST"])
def upload_plan():
    """Handle PDF plan upload"""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith(".pdf"):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Use pipeline bridge if available, otherwise fallback to mock
        if pipeline_bridge:
            from pathlib import Path

            job_id = pipeline_bridge.submit_job(Path(filepath), filename)
            logger.info(f"Submitted job {job_id} to pipeline bridge")
        else:
            job_id = f"job_{int(time.time())}"
            pipeline_status["active_jobs"].append(
                {"id": job_id, "filename": filename, "status": "queued", "progress": 0, "phase": 0}
            )

            # Emit update via WebSocket
            socketio.emit("job_created", {"job_id": job_id, "filename": filename})

            # Trigger mock pipeline
            socketio.start_background_task(run_pipeline_mock, job_id, filename)
            logger.info(f"Submitted job {job_id} to mock pipeline")

        return jsonify({"message": "File uploaded successfully", "job_id": job_id}), 202

    return jsonify({"error": "Invalid file type"}), 400


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """Return system metrics"""
    import psutil

    metrics = {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "active_jobs": len(pipeline_status["active_jobs"]),
        "uptime": time.time() - start_time,
    }
    return jsonify(metrics)


# ─────────────────────────────────────────────────────────────────────────────
# NEW API v1 ENDPOINTS - SISAS Integration
# ─────────────────────────────────────────────────────────────────────────────


@app.route("/api/v1/regions", methods=["GET"])
def get_all_regions():
    """Get all PDET regions with summaries."""
    return jsonify({"regions": PDET_REGIONS, "total": len(PDET_REGIONS)})


@app.route("/api/v1/regions/<region_id>", methods=["GET"])
def get_region_detail_endpoint(region_id: str):
    """Get full region detail with macro/meso/micro breakdown."""
    job_id = request.args.get("job_id")
    try:
        detail = get_region_detail(region_id, job_id)
        return jsonify(detail)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@app.route("/api/v1/regions/connections", methods=["GET"])
def get_region_connections_endpoint():
    """Get region connections for constellation view."""
    return jsonify({"connections": REGION_CONNECTIONS})


@app.route("/api/v1/jobs", methods=["GET"])
def list_jobs():
    """List all pipeline jobs (active and completed)."""
    if pipeline_bridge:
        return jsonify(pipeline_bridge.get_all_jobs())
    return jsonify({"active_jobs": pipeline_status["active_jobs"], "completed_jobs": []})


@app.route("/api/v1/jobs/<job_id>", methods=["GET"])
def get_job_status_endpoint(job_id: str):
    """Get detailed job status with phase breakdown."""
    if pipeline_bridge:
        status = pipeline_bridge.get_job_status(job_id)
        if status:
            return jsonify(status)
        return jsonify({"error": "Job not found"}), 404

    # Fallback to legacy status
    for job in pipeline_status["active_jobs"]:
        if job["id"] == job_id:
            return jsonify(job)
    return jsonify({"error": "Job not found"}), 404


@app.route("/api/v1/sisas/status", methods=["GET"])
def get_sisas_status():
    """Get full SISAS integration status."""
    if pipeline_bridge and hasattr(pipeline_bridge.orchestrator, "context"):
        try:
            context = pipeline_bridge.orchestrator.context
            if hasattr(context, "sisas"):
                sisas = context.sisas
                return jsonify(
                    {
                        "enabled": True,
                        "status": "ONLINE",
                        "consumers": {
                            "total": len(getattr(sisas, "_consumers", [])),
                            "active": len([c for c in getattr(sisas, "_consumers", [])]),
                        },
                        "metrics": sisas.get_metrics() if hasattr(sisas, "get_metrics") else {},
                    }
                )
        except Exception as e:
            logger.error(f"Failed to get SISAS status: {e}")

    return jsonify({"enabled": False, "status": "UNAVAILABLE"})


@app.route("/api/v1/sisas/metrics", methods=["GET"])
def get_sisas_metrics():
    """Get SISAS metrics from orchestrator."""
    if pipeline_bridge:
        metrics = pipeline_bridge.get_sisas_metrics()
        return jsonify(metrics)

    return jsonify(
        {
            "sisas_enabled": False,
            "message": "Pipeline bridge not initialized",
        }
    )


@app.route("/api/v1/sisas/consumers", methods=["GET"])
def get_sisas_consumers():
    """Get status of all SISAS consumers."""
    if pipeline_bridge and hasattr(pipeline_bridge.orchestrator, "get_sisas_metrics"):
        try:
            metrics = pipeline_bridge.orchestrator.get_sisas_metrics()
            consumer_stats = metrics.get("consumer_stats", {})
            return jsonify({"consumers": consumer_stats})
        except Exception as e:
            logger.error(f"Failed to get consumer stats: {e}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"consumers": [], "message": "SISAS not available"})


@app.route("/api/v1/sisas/dead-letter", methods=["GET"])
def get_dead_letter_queue():
    """Get dead letter queue contents."""
    if pipeline_bridge and hasattr(pipeline_bridge.orchestrator, "context"):
        try:
            sisas = pipeline_bridge.orchestrator.context.sisas
            if hasattr(sisas, "get_dead_letter_queue"):
                dlq = sisas.get_dead_letter_queue()
                return jsonify({"dead_letter_queue": dlq, "count": len(dlq)})
        except Exception as e:
            logger.error(f"Failed to get dead letter queue: {e}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"dead_letter_queue": [], "count": 0, "message": "SISAS not available"})


@app.route("/api/v1/regions/<region_id>/questions", methods=["GET"])
def get_region_questions(region_id: str):
    """Get all 300 micro question scores for a region.

    Query params:
        - dimension: Filter by dimension (D1-D6)
        - policy_area: Filter by policy area (PA01-PA10)
        - job_id: Load from specific job artifacts
    """
    dimension = request.args.get("dimension")
    policy_area = request.args.get("policy_area")
    job_id = request.args.get("job_id")

    # TODO: Integrate with DashboardDataService.extract_question_matrix()
    # For now, return mock structure
    questions = []
    for i in range(1, 301):
        question = {
            "id": f"Q{i:03d}",
            "text": f"Question {i} text",
            "score": None,  # Will be populated from artifacts
            "dimension": f"D{((i-1) // 50) + 1}",
            "policy_area": f"PA{((i-1) % 10) + 1:02d}",
        }

        # Apply filters
        if dimension and question["dimension"] != dimension:
            continue
        if policy_area and question["policy_area"] != policy_area:
            continue

        questions.append(question)

    return jsonify({"region_id": region_id, "questions": questions, "total": len(questions), "job_id": job_id})


@app.route("/api/v1/regions/<region_id>/evidence", methods=["GET"])
def get_region_evidence(region_id: str):
    """Get evidence stream for a region.

    Query params:
        - limit: Max number of evidence items (default 50)
        - question_id: Filter by question
        - job_id: Load from specific job artifacts
    """
    limit = int(request.args.get("limit", 50))
    question_id = request.args.get("question_id")
    job_id = request.args.get("job_id")

    # TODO: Integrate with DashboardDataService.normalize_evidence_stream()
    # For now, return mock structure
    evidence_items = [
        {
            "source": "PDT Sección 3.2",
            "page": 45,
            "text": "Implementación de estrategias municipales para equidad de género",
            "timestamp": "2024-01-15T10:30:00Z",
            "question_id": "Q023",
            "relevance_score": 0.87,
        }
    ]

    return jsonify(
        {
            "region_id": region_id,
            "evidence": evidence_items[:limit],
            "total": len(evidence_items),
            "limit": limit,
            "job_id": job_id,
        }
    )


@app.route("/api/v1/jobs/<job_id>/logs", methods=["GET"])
def get_job_logs(job_id: str):
    """Get execution logs for a job.

    Query params:
        - phase: Filter by phase (P00-P09)
        - level: Filter by log level (DEBUG, INFO, WARNING, ERROR)
        - limit: Max number of log entries
    """
    phase = request.args.get("phase")
    level = request.args.get("level")
    limit = int(request.args.get("limit", 100))

    # TODO: Implement log retrieval from job artifacts
    logs = [
        {"timestamp": "2024-01-15T10:30:00Z", "phase": "P00", "level": "INFO", "message": "Phase started"},
    ]

    # Apply filters
    if phase:
        logs = [log for log in logs if log["phase"] == phase]
    if level:
        logs = [log for log in logs if log["level"] == level]

    return jsonify({"job_id": job_id, "logs": logs[:limit], "total": len(logs), "limit": limit})


# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL DATA ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────


@app.route("/api/v1/canonical/questions", methods=["GET"])
def get_canonical_questions():
    """Get all 300 micro questions with metadata."""
    # TODO: Integrate with CQC loader
    # For now return basic structure
    questions = []
    for i in range(1, 301):
        questions.append(
            {
                "id": f"Q{i:03d}",
                "text": f"Canonical question {i}",
                "dimension": f"D{((i-1) // 50) + 1}",
                "policy_area": f"PA{((i-1) % 10) + 1:02d}",
                "cluster": f"CL{((i-1) % 4) + 1:02d}",
            }
        )

    return jsonify({"questions": questions, "total": len(questions)})


@app.route("/api/v1/canonical/questions/<question_id>", methods=["GET"])
def get_question_detail(question_id: str):
    """Get single question with all bound methods and patterns."""
    # TODO: Integrate with CQC loader
    question_detail = {
        "id": question_id,
        "text": f"Detailed text for {question_id}",
        "dimension": "D1",
        "policy_area": "PA01",
        "cluster": "CL01",
        "patterns": [],
        "indicators": [],
        "methods": [],
    }

    return jsonify(question_detail)


@app.route("/api/v1/canonical/dimensions", methods=["GET"])
def get_canonical_dimensions():
    """Get all 6 dimensions with metadata."""
    dimensions = [
        {"id": "D1", "name": "INSUMOS", "description": "Información de base y diagnóstico"},
        {"id": "D2", "name": "VOLUNTAD", "description": "Participación y compromiso"},
        {"id": "D3", "name": "CONTEXTO", "description": "Contexto territorial"},
        {"id": "D4", "name": "COHERENCIA", "description": "Coherencia programática"},
        {"id": "D5", "name": "SISAS", "description": "Sistema integrado de seguimiento"},
        {"id": "D6", "name": "IMPLEMENTACIÓN", "description": "Capacidad de implementación"},
    ]

    return jsonify({"dimensions": dimensions, "total": len(dimensions)})


@app.route("/api/v1/canonical/policy-areas", methods=["GET"])
def get_canonical_policy_areas():
    """Get all 10 policy areas with metadata."""
    policy_areas = [
        {"id": "PA01", "name": "Derechos de Género", "questions": 30},
        {"id": "PA02", "name": "Prevención de Violencias", "questions": 30},
        {"id": "PA03", "name": "Medio Ambiente", "questions": 30},
        {"id": "PA04", "name": "Derechos Económicos", "questions": 30},
        {"id": "PA05", "name": "Derechos de Víctimas", "questions": 30},
        {"id": "PA06", "name": "Niñez y Juventud", "questions": 30},
        {"id": "PA07", "name": "Tierra y Territorio", "questions": 30},
        {"id": "PA08", "name": "Defensores DDHH", "questions": 30},
        {"id": "PA09", "name": "Crisis Carcelaria", "questions": 30},
        {"id": "PA10", "name": "Migración", "questions": 30},
    ]

    return jsonify({"policy_areas": policy_areas, "total": len(policy_areas)})


@app.route("/api/v1/canonical/clusters", methods=["GET"])
def get_canonical_clusters():
    """Get all 4 clusters with metadata."""
    clusters = [
        {"id": "CL01", "name": "SEC_PAZ", "description": "Seguridad y Paz", "questions": 75},
        {"id": "CL02", "name": "GP", "description": "Gestión Pública", "questions": 75},
        {"id": "CL03", "name": "TERR_AMB", "description": "Territorio y Ambiente", "questions": 75},
        {"id": "CL04", "name": "DESC_CRIS", "description": "Desconfianza y Crisis", "questions": 75},
    ]

    return jsonify({"clusters": clusters, "total": len(clusters)})


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket Events - Enhanced with SISAS Integration
# ─────────────────────────────────────────────────────────────────────────────


@socketio.on("connect")
def handle_connect():
    """Handle client connection - send initial state."""
    logger.info("Client connected")

    # Send system status
    emit("system_status", {"status": "online", "version": "2.0.0", "sisas_enabled": pipeline_bridge is not None})

    # Send current SISAS metrics if available
    if pipeline_bridge:
        try:
            sisas_metrics = pipeline_bridge.get_sisas_metrics()
            emit("sisas_metrics_update", {"timestamp": time.time(), "metrics": sisas_metrics})
        except Exception as e:
            logger.warning(f"Failed to send initial SISAS metrics: {e}")

    # Send active jobs
    if pipeline_bridge:
        jobs_data = pipeline_bridge.get_all_jobs()
        emit("jobs_status", jobs_data)


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected")


@socketio.on("request_sisas_update")
def handle_sisas_update_request():
    """Client requests current SISAS metrics."""
    if pipeline_bridge:
        sisas_metrics = pipeline_bridge.get_sisas_metrics()
        emit("sisas_metrics_update", {"timestamp": time.time(), "metrics": sisas_metrics})
    else:
        emit("sisas_metrics_update", {"timestamp": time.time(), "metrics": {}, "error": "Bridge not initialized"})


@socketio.on("request_job_status")
def handle_job_status_request(data):
    """Client requests specific job status."""
    job_id = data.get("job_id")
    if not job_id:
        emit("error", {"message": "Missing job_id"})
        return

    if pipeline_bridge:
        status = pipeline_bridge.get_job_status(job_id)
        if status:
            emit("job_status_update", status)
        else:
            emit("error", {"message": f"Job {job_id} not found"})
    else:
        emit("error", {"message": "Bridge not initialized"})


def run_pipeline_mock(job_id, filename):
    """Mock pipeline execution to demonstrate UI updates"""
    logger.info(f"Starting pipeline for {job_id}")

    phases = [
        "Acquisition & Integrity",
        "Format Decomposition",
        "Text Extraction",
        "Structure Normalization",
        "Semantic Segmentation",
        "Entity Recognition",
        "Relation Extraction",
        "Policy Analysis",
        "Report Generation",
    ]

    for i, phase in enumerate(phases):
        time.sleep(2)  # Simulate work
        progress = int((i + 1) / len(phases) * 100)

        socketio.emit(
            "pipeline_progress",
            {
                "job_id": job_id,
                "phase": i + 1,
                "phase_name": phase,
                "progress": progress,
                "status": "processing",
            },
        )

    socketio.emit(
        "pipeline_completed",
        {"job_id": job_id, "status": "completed", "result_url": f"/artifacts/{job_id}/report.json"},
    )


start_time = time.time()


def initialize_orchestrator_integration(orchestrator=None):
    """Initialize pipeline bridge with orchestrator.

    Args:
        orchestrator: UnifiedOrchestrator instance (optional)

    This function should be called after dashboard server starts to connect
    to the real pipeline orchestrator. If no orchestrator is provided, the
    dashboard will operate in standalone mode with mock data.
    """
    global pipeline_bridge

    if orchestrator:
        logger.info("Initializing pipeline bridge with orchestrator")
        pipeline_bridge = initialize_bridge(orchestrator, socketio)
        logger.info("Pipeline bridge initialized successfully")
    else:
        logger.warning("No orchestrator provided - dashboard running in standalone mode")


if __name__ == "__main__":
    logger.info("Starting AtroZ Dashboard Server...")
    logger.info(f"Loaded {len(PDET_REGIONS)} PDET regions with real data")
    logger.info(f"Upload directory: {app.config['UPLOAD_FOLDER']}")

    # Try to initialize orchestrator integration (optional)
    try:
        # Attempt to import and initialize orchestrator
        # This allows dashboard to run standalone or integrated
        from farfan_pipeline.orchestration.orchestrator import UnifiedOrchestrator

        logger.info("UnifiedOrchestrator available - attempting integration")
        # Note: Orchestrator initialization requires config, so we defer this
        # to runtime when a job is submitted
    except ImportError:
        logger.info("UnifiedOrchestrator not available - running in standalone mode")

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
