# F.A.R.F.A.N Pipeline - Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker 20.10+ and Docker Compose 1.29+
- At least 8GB RAM available
- 10GB free disk space

### Building the Image

```bash
# Build the Docker image
docker build -t farfan-pipeline:latest .

# Or use docker-compose
docker-compose build
```

### Running the Pipeline

```bash
# Run with docker-compose
docker-compose up -d

# Or run directly with docker
docker run --rm -v $(pwd)/data:/app/data -v $(pwd)/outputs:/app/outputs farfan-pipeline:latest

# Run specific command
docker run --rm farfan-pipeline:latest python -m farfan_pipeline.entrypoint.main --version
```

### Development Setup

For development, you can mount the source code:

```bash
docker run --rm \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  farfan-pipeline:latest \
  python -m pytest tests/
```

## Manual Installation (Non-Docker)

### System Requirements
- Python 3.12+
- Ubuntu 20.04+ / Debian 11+ / MacOS 12+ / Windows 10+

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  libmupdf-dev \
  python3.12 \
  python3.12-venv
```

**MacOS:**
```bash
brew install python@3.12 cairo pango gdk-pixbuf libffi mupdf
```

### Python Dependencies

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Install package in editable mode
pip install -e .

# Download spaCy language model
python -m spacy download es_core_news_lg
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/calibration/

# Run with coverage
pytest tests/ --cov=farfan_pipeline --cov-report=html
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Environment
FARFAN_ENV=development  # development, staging, production

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# API Configuration (if using API)
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Pipeline Configuration
PHASE2_RANDOM_SEED=42
MAX_CONCURRENT_PHASES=3
```

### Resource Limits

Adjust resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
```

## CI/CD Integration

The project includes GitHub Actions workflows for:
- CQVR Validation
- GNEA Enforcement
- Phase 2 Enforcement
- Import Linting
- Deployment to Staging/Production

See `.github/workflows/` for details.

## Troubleshooting

### Import Errors
If you encounter import errors, ensure the package is installed:
```bash
pip install -e .
```

### Missing Dependencies
Install system dependencies as described above. For weasyprint issues:
```bash
# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0

# MacOS
brew install cairo pango
```

### Memory Issues
The pipeline requires significant RAM for NLP models (transformers, spaCy). Ensure:
- At least 8GB RAM available
- Docker has sufficient memory allocation (check Docker Desktop settings)

### Python Version Mismatch
The project requires Python 3.12. Check your version:
```bash
python --version  # Should be 3.12.x
```

## Production Deployment

### Security Considerations
1. Run as non-root user (already configured in Dockerfile)
2. Use secrets management for API keys and credentials
3. Enable HTTPS for API endpoints
4. Keep dependencies updated: `pip-audit` and `safety check`

### Performance Optimization
1. Use GPU-enabled Docker image for faster NLP inference
2. Enable caching for method registry (Phase 2 Factory Cache)
3. Adjust parallel execution settings in configuration
4. Monitor resource usage and adjust limits

### Monitoring
Set up monitoring for:
- Container health checks
- Memory and CPU usage
- API response times (if using API)
- Log aggregation (structured logging with structlog)

## Support

For issues or questions:
- Check documentation in `docs/`
- Review audit reports: `COMPREHENSIVE_AUDIT_REPORT.md`
- Open issue on GitHub repository
