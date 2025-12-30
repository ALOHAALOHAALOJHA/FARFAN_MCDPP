"""Primary API server entrypoint.

Currently exposes the FastAPI Signal Service implemented in
`farfan_pipeline.dashboard_atroz_.signals_service`.
"""

from __future__ import annotations

import os

import uvicorn

from farfan_pipeline.dashboard_atroz_.signals_service import app


def main() -> None:
    host = os.getenv("FARFAN_API_HOST", "0.0.0.0")
    port = int(os.getenv("FARFAN_API_PORT", "8000"))

    uvicorn.run(
        "farfan_pipeline.dashboard_atroz_.signals_service:app",
        host=host,
        port=port,
        log_level="info",
        reload=False,
    )
