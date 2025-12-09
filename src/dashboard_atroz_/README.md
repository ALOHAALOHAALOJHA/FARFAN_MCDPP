# Dashboard Atroz

Curated entry point for the current dashboard orchestration. This package
labels and references the active modules without relocating them to avoid path
breakage. Use these imports for clarity and stability.

Contents:
- `flask_app`: re-export of the Flask app from `api.api_server`.
- `api_server`: import shim to run the current Flask API server.
- `data_service`: import shim for the transformer used by the dashboard.
- `pipeline_connector`: import shim wiring the orchestrator results to artifacts.

Notes:
- Original modules remain under `src/farfan_pipeline/api/*`.
- This package ensures Python paths remain valid while giving the dashboard a
  single labeled namespace.
