# F.A.R.F.A.N Pipeline - Production Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.12-slim as builder

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt requirements-dev.txt ./
COPY pyproject.toml setup.py ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python dependencies
# Note: torch and transformers are large (~2GB), consider using CPU-only versions
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    # GTK libraries required by weasyprint
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    # PDF processing libraries
    libmupdf-dev \
    # Image processing
    libopencv-dev \
    # General utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Set working directory
WORKDIR /app

# Copy source code
COPY src/ ./src/
COPY canonic_questionnaire_central/ ./canonic_questionnaire_central/
COPY pyproject.toml setup.py ./

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Download spaCy language model
RUN python -m spacy download es_core_news_lg

# Create directories for data and outputs
RUN mkdir -p /app/data /app/outputs /app/logs

# Set up non-root user for security
RUN useradd -m -u 1000 farfan && \
    chown -R farfan:farfan /app

USER farfan

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "from farfan_pipeline.orchestration import UnifiedOrchestrator; print('OK')" || exit 1

# Expose port for API (if running API server)
EXPOSE 8000

# Default command - can be overridden
CMD ["python", "-m", "farfan_pipeline.entrypoint.main", "--help"]
