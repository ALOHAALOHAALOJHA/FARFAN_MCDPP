# FARFAN Pipeline Entry Points

## Overview

The FARFAN pipeline provides two main entry points:

1. **CLI**: `farfan-pipeline` - Command-line interface for running the pipeline
2. **API Server**: `farfan_core-api` - REST API server for pipeline execution

## Installation

```bash
# Install the package with all dependencies
pip install -e .

# Or install minimal dependencies
pip install fastapi uvicorn httpx sse-starlette
```

## Usage

### CLI Entry Point

The CLI entry point provides access to the pipeline orchestration:

```bash
# Run the pipeline
farfan-pipeline

# Or via Python module
python -m farfan_pipeline.entrypoint.main
```

**Note**: The CLI requires the full set of dependencies including blake3, structlog, and others. If dependencies are missing, a clear error message will be displayed.

### API Server Entry Point

The API server provides a REST API for pipeline execution:

```bash
# Start the API server
farfan_core-api

# Or via Python module
python -m farfan_pipeline.api.api_server
```

The API server starts on `http://0.0.0.0:8000` by default.

#### API Endpoints

- `GET /` - Root endpoint with version info
- `GET /health` - Health check
- `GET /api/v1/status` - Pipeline status

#### CORS Configuration

By default, the API server allows CORS requests from:
- `http://localhost:3000`
- `http://localhost:8080`

To configure allowed origins for production:

```bash
export FARFAN_CORS_ORIGINS="https://example.com,https://app.example.com"
farfan_core-api
```

## Architecture

Both entry points are designed to:
- Handle missing dependencies gracefully
- Provide clear error messages
- Follow security best practices
- Be easily testable

### Module Structure

```
farfan_pipeline/
├── entrypoint/
│   ├── __init__.py
│   └── main.py          # CLI entry point
└── api/
    ├── __init__.py
    └── api_server.py    # API server entry point
```

### Entry Point Configuration

Entry points are configured in `pyproject.toml`:

```toml
[project.scripts]
farfan-pipeline = "farfan_pipeline.entrypoint.main:main"
farfan_core-api = "farfan_pipeline.api.api_server:main"
```

## Development

### Testing Entry Points

```bash
# Test CLI import
python -c "from farfan_pipeline.entrypoint.main import main; print('CLI OK')"

# Test API import
python -c "from farfan_pipeline.api.api_server import main, app; print('API OK')"
```

### Running Tests

```bash
# Run with minimal setup (PYTHONPATH approach)
PYTHONPATH=src python -m farfan_pipeline.api.api_server
```

## Troubleshooting

### "No module named 'structlog'"

Install missing dependencies:
```bash
pip install structlog
```

### "No module named 'blake3'"

Install the blake3 hashing library:
```bash
pip install blake3
```

### "FastAPI not installed"

Install FastAPI and uvicorn:
```bash
pip install fastapi uvicorn[standard]
```

## Security

- CORS origins must be explicitly configured via environment variable
- Default configuration only allows localhost origins
- GitHub token permissions are limited in CI/CD workflows
- All inputs are validated before processing

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [FARFAN Layer Architecture](../architecture/LAYER_ARCHITECTURE.md)
