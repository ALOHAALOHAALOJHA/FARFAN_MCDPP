#!/bin/bash
# F.A.R.F.A.N Environment Activation Script
# ==========================================
#
# This script configures the Python environment for FARFAN_MCDPP development.
# Source this script to set up your PYTHONPATH and environment variables.
#
# Usage:
#   source scripts/activate.sh
#   # OR
#   . scripts/activate.sh

set -e  # Exit on error

# Get the project root directory
FARFAN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FARFAN_ROOT

# Add src/ and root to PYTHONPATH
export PYTHONPATH="${FARFAN_ROOT}/src:${FARFAN_ROOT}:${PYTHONPATH}"

# Set other environment variables
export FARFAN_DATA_PATH="${FARFAN_DATA_PATH:-${FARFAN_ROOT}/data}"
export FARFAN_CACHE_DIR="${FARFAN_CACHE_DIR:-${FARFAN_ROOT}/.cache}"
export FARFAN_LOG_LEVEL="${FARFAN_LOG_LEVEL:-INFO}"

# Set Python version
export PYTHON_VERSION="${PYTHON_VERSION:-3.12}"

# Print configuration
echo "F.A.R.F.A.N Environment Activated"
echo "=================================="
echo "FARFAN_ROOT:         ${FARFAN_ROOT}"
echo "PYTHONPATH:          ${PYTHONPATH}"
echo "FARFAN_DATA_PATH:    ${FARFAN_DATA_PATH}"
echo "FARFAN_CACHE_DIR:    ${FARFAN_CACHE_DIR}"
echo "FARFAN_LOG_LEVEL:    ${FARFAN_LOG_LEVEL}"
echo ""
echo "To verify the configuration, run:"
echo "  python3 -c 'from farfan_pipeline.orchestration import UnifiedOrchestrator; print(\"OK\")'"
echo "  python3 -c 'from canonic_questionnaire_central import CQCLoader; print(\"OK\")'"
echo ""
