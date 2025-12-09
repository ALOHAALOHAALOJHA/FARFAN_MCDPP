"""Shim to run the current dashboard Flask API server.

Keeps import paths stable by referencing the existing server implementation
under `farfan_pipeline.api.api_server`.
"""

from ..api.api_server import app

if __name__ == "__main__":
    # Delegate to the existing Flask app run configuration
    app.run(host="0.0.0.0", port=5000, debug=True)
