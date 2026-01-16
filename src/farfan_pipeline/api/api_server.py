"""API server for the FARFAN pipeline.

This module provides the API server entry point for the FARFAN pipeline,
exposing REST endpoints for pipeline execution and status monitoring.
"""
from __future__ import annotations

import sys
from typing import Any


def create_app() -> Any:
    """Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError as e:
        print(f"Error: FastAPI not installed: {e}", file=sys.stderr)
        print("Please install FastAPI: pip install fastapi uvicorn", file=sys.stderr)
        sys.exit(1)

    # Create FastAPI app
    app = FastAPI(
        title="FARFAN Pipeline API",
        description="API for Framework for Advanced Retrieval of Administrative Narratives",
        version="1.0.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "message": "FARFAN Pipeline API",
            "version": "1.0.0",
            "status": "running",
        }

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.get("/api/v1/status")
    async def status() -> dict[str, Any]:
        """Get pipeline status."""
        return {
            "pipeline": "farfan",
            "version": "1.0.0",
            "status": "ready",
        }
    
    return app


# Create app instance for uvicorn
app = create_app()


def main() -> int:
    """Main entry point for farfan_core-api command.
    
    Starts the FastAPI server using uvicorn.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        import uvicorn
    except ImportError as e:
        print(f"Error: uvicorn not installed: {e}", file=sys.stderr)
        print("Please install uvicorn: pip install uvicorn[standard]", file=sys.stderr)
        return 1
    
    try:
        print("Starting FARFAN Pipeline API server on http://0.0.0.0:8000")
        
        # Run uvicorn server
        uvicorn.run(
            "farfan_pipeline.api.api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
        )
        
        return 0
    except Exception as e:
        print(f"Error starting API server: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
