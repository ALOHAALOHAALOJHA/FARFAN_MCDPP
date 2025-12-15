"""Dashboard Atroz package

This package groups and labels the modules orchestrating the current dashboard
without moving original sources. It provides stable import paths while
preserving existing module locations.
"""

# Re-export key orchestrator components for convenience
# NOTE: The original API server module (src/api/api_server.py) is missing from the current codebase.
# Commenting out to prevent ImportErrors until the original source is restored or replaced by V2.
# from ..api.api_server import app as flask_app  # type: ignore
