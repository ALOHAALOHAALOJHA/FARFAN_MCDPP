#!/bin/bash
# F.A.R.F.A.N End-to-End Pipeline Runner
# Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives
#
# This script runs the complete pipeline from input validation through all phases
# to final report generation with cryptographic verification.

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Default values
PLAN_PDF="${1:-data/plans/Plan_1.pdf}"
ARTIFACTS_DIR="${2:-artifacts/plan1}"
VENV_PATH="${PROJECT_ROOT}/farfan-env"

# Function to print colored messages
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        error "Virtual environment not found at: $VENV_PATH"
        echo ""
        echo "Please create it first:"
        echo "  python3.12 -m venv farfan-env"
        echo "  source farfan-env/bin/activate"
        echo "  pip install -e ."
        exit 1
    fi
    
    if [ ! -f "$VENV_PATH/bin/python" ]; then
        error "Python executable not found in virtual environment"
        exit 1
    fi
    
    success "Virtual environment found"
}

# Function to activate virtual environment
activate_venv() {
    info "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    
    # Verify activation
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        error "Failed to activate virtual environment"
        exit 1
    fi
    
    success "Virtual environment activated: $VIRTUAL_ENV"
}

# Function to check Python version
check_python_version() {
    local python_version
    python_version=$(python --version 2>&1 | awk '{print $2}')
    local major minor
    IFS='.' read -r major minor <<< "$python_version"
    
    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 12 ]); then
        error "Python 3.12+ required, found: $python_version"
        exit 1
    fi
    
    success "Python version OK: $python_version"
}

# Function to verify input PDF exists
check_input_pdf() {
    local plan_path="$PROJECT_ROOT/$PLAN_PDF"
    
    if [ ! -f "$plan_path" ]; then
        error "Input PDF not found: $plan_path"
        echo ""
        echo "Available plans:"
        ls -1 "$PROJECT_ROOT/data/plans/"*.pdf 2>/dev/null || echo "  (none found)"
        exit 1
    fi
    
    success "Input PDF found: $plan_path"
}

# Function to check dependencies
check_dependencies() {
    info "Checking dependencies..."
    
    # Check if package is installed
    if ! python -c "import farfan_pipeline" 2>/dev/null; then
        warning "Package 'farfan_pipeline' not found. Installing..."
        pip install -e . > /dev/null 2>&1 || {
            error "Failed to install package"
            exit 1
        }
    fi
    
    success "Dependencies OK"
}

# Function to set optional environment variables
set_env_vars() {
    # Set determinism seed if not already set
    if [ -z "${PYTHONHASHSEED:-}" ]; then
        export PYTHONHASHSEED=42
        info "Set PYTHONHASHSEED=42 for determinism"
    fi
    
    # Set manifest secret key if not set (uses default in script)
    if [ -z "${MANIFEST_SECRET_KEY:-}" ]; then
        warning "MANIFEST_SECRET_KEY not set, using default (change in production)"
    else
        info "Using custom MANIFEST_SECRET_KEY"
    fi
    
    # Optional debug mode
    if [ "${PIPELINE_DEBUG:-0}" = "1" ]; then
        info "Debug mode enabled"
    fi
    
    # Ensure src/ is in Python path
    export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"
}

# Function to run the pipeline
run_pipeline() {
    local plan_path="$PROJECT_ROOT/$PLAN_PDF"
    local artifacts_path="$PROJECT_ROOT/$ARTIFACTS_DIR"
    
    info "Starting pipeline execution..."
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "  F.A.R.F.A.N END-TO-END PIPELINE EXECUTION"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "  Plan PDF:     $plan_path"
    echo "  Artifacts:    $artifacts_path"
    echo "  Environment:  $VIRTUAL_ENV"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""
    
    # Run the verified pipeline script
    # NOTE: The script uses 'saaaaaa' imports which may need to be fixed
    # If you encounter import errors, check scripts/run_policy_pipeline_verified.py
    # and update imports to use 'farfan_pipeline' instead of 'saaaaaa'
    python "$PROJECT_ROOT/scripts/run_policy_pipeline_verified.py" \
        --plan "$PLAN_PDF" \
        --artifacts-dir "$ARTIFACTS_DIR"
    
    local exit_code=$?
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    
    if [ $exit_code -eq 0 ]; then
        success "Pipeline completed successfully!"
        echo ""
        info "Artifacts saved to: $artifacts_path"
        info "Verification manifest: $artifacts_path/verification_manifest.json"
        echo ""
        echo "To verify the manifest:"
        echo "  python -c \"from farfan_pipeline.orchestration.verification_manifest import verify_manifest_integrity; import json; m=json.load(open('$artifacts_path/verification_manifest.json')); print('Valid' if verify_manifest_integrity(m)[0] else 'Invalid')\""
    else
        error "Pipeline failed with exit code: $exit_code"
        echo ""
        warning "Check the execution_claims.json in artifacts directory for details"
        exit $exit_code
    fi
}

# Main execution
main() {
    echo ""
    info "F.A.R.F.A.N End-to-End Pipeline Runner"
    info "======================================="
    echo ""
    
    # Pre-flight checks
    check_venv
    activate_venv
    check_python_version
    check_input_pdf
    check_dependencies
    set_env_vars
    
    echo ""
    
    # Run pipeline
    run_pipeline
}

# Run main function
main "$@"

