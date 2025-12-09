"""Dashboard Atroz package

This package groups and labels the modules orchestrating the current dashboard
without moving original sources. It provides stable import paths while
preserving existing module locations.
"""

# Re-export key orchestrator components for convenience
from ..api.api_server import app as flask_app  # type: ignore
