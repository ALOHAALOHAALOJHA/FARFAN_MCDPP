#!/bin/bash
################################################################################
# F.A.R.F.A.N COMPREHENSIVE PIPELINE EXECUTION SCRIPT
# Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives
#
# Version: 2.0.0
# Author: F.A.R.F.A.N Pipeline Team
#
# DESCRIPTION:
#   This script executes the complete F.A.R.F.A.N pipeline with all validation
#   phases, quality gates, and verification steps. It is designed for production
#   use and includes comprehensive error handling, logging, and reporting.
#
# PIPELINE PHASES:
#   1. Pre-flight Validation (Environment, Dependencies, Architecture)
#   2. Code Quality Assurance (Linting, Formatting, Security)
#   3. Contract Validation (CQVR Quality Gates)
#   4. Import Stratification (Architectural Analysis)
#   5. Pipeline Execution (Phases P00-P09)
#   6. Post-execution Validation (Manifests, Artifacts)
#   7. Report Generation (Quality, Audit, Dashboard)
#
# USAGE:
#   ./scripts/run_farfan_pipeline.sh [OPTIONS]
#
# OPTIONS:
#   -p, --plan PATH           Path to input PDF (default: data/plans/Plan_1.pdf)
#   -o, --output PATH         Output artifacts directory (default: artifacts/pipeline_run_TIMESTAMP)
#   -m, --mode MODE           Execution mode: full|quick|validate|audit (default: full)
#   -v, --verbose             Enable verbose output
#   -d, --debug               Enable debug mode
#   -k, --skip-quality        Skip quality gates (NOT RECOMMENDED)
#   -c, --cqvr-only           Run only CQVR contract validation
#   -a, --audit-only          Run only audit checks
#   -t, --test                Run in test mode (with mock data)
#   -h, --help                Show this help message
#
# EXIT CODES:
#   0 - Success
#   1 - Pre-flight validation failed
#   2 - Code quality checks failed
#   3 - Contract validation failed
#   4 - Architecture validation failed
#   5 - Pipeline execution failed
#   6 - Post-execution validation failed
#   7 - Report generation failed
#   8 - User interrupted
#   9 - Unexpected error
#
################################################################################

set -euo pipefail  # Exit on error, undefined vars, pipe failures

################################################################################
# CONFIGURATION
################################################################################

# Script paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"

# Default values
PLAN_PDF="data/plans/Plan_1.pdf"
ARTIFACTS_DIR="artifacts/pipeline_run_$(date +%Y%m%d_%H%M%S)"
EXECUTION_MODE="full"
VERBOSE=false
DEBUG=false
SKIP_QUALITY=false
CQVR_ONLY=false
AUDIT_ONLY=false
TEST_MODE=false

# Virtual environment
VENV_PATH="$PROJECT_ROOT/farfan-env"

# Quality thresholds
CQVR_THRESHOLD=40
COVERAGE_THRESHOLD=80
COMPLEXITY_THRESHOLD=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Counters
TOTAL_STEPS=0
COMPLETED_STEPS=0
FAILED_STEPS=0

# Log file
LOG_FILE=""

################################################################################
# UTILITY FUNCTIONS
################################################################################

# Print colored messages
info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

debug() {
    if [[ "$DEBUG" == true ]]; then
        echo -e "${MAGENTA}[DEBUG]${NC} $1" | tee -a "$LOG_FILE"
    fi
}

verbose() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${CYAN}[VERBOSE]${NC} $1" | tee -a "$LOG_FILE"
    fi
}

# Print section header
section() {
    local title="$1"
    local width=80
    local padding=$(( (width - ${#title} - 4) / 2 ))
    local line=$(printf '=%.0s' $(seq 1 $width))

    echo "" | tee -a "$LOG_FILE"
    echo -e "${BOLD}${BLUE}$line${NC}" | tee -a "$LOG_FILE"
    echo -e "${BOLD}${BLUE}$(printf ' %.0s' $(seq 1 $padding))$title$(printf ' %.0s' $(seq 1 $padding))${NC}" | tee -a "$LOG_FILE"
    echo -e "${BOLD}${BLUE}$line${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Print step with progress
step() {
    local step_num=$((TOTAL_STEPS + 1))
    local step_name="$1"
    echo -e "${CYAN}[STEP $step_num]${NC} $step_name" | tee -a "$LOG_FILE"
    TOTAL_STEPS=$((TOTAL_STEPS + 1))
}

# Mark step as completed
step_complete() {
    COMPLETED_STEPS=$((COMPLETED_STEPS + 1))
    success "Step completed ($COMPLETED_STEPS/$TOTAL_STEPS)"
}

# Mark step as failed
step_failed() {
    FAILED_STEPS=$((FAILED_STEPS + 1))
    error "Step failed ($FAILED_STEPS failed, $COMPLETED_STEPS completed)"
}

# Trap interrupts
trap_interrupt() {
    warning "Interrupted by user"
    echo ""
    info "Cleaning up..."
    # Cleanup tasks here
    exit 8
}

trap 'trap_interrupt' INT TERM

################################################################################
# PRE-FLIGHT VALIDATION
################################################################################

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--plan)
                PLAN_PDF="$2"
                shift 2
                ;;
            -o|--output)
                ARTIFACTS_DIR="$2"
                shift 2
                ;;
            -m|--mode)
                EXECUTION_MODE="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -d|--debug)
                DEBUG=true
                VERBOSE=true
                shift
                ;;
            -k|--skip-quality)
                SKIP_QUALITY=true
                warning "Quality gates disabled - NOT RECOMMENDED"
                shift
                ;;
            -c|--cqvr-only)
                CQVR_ONLY=true
                shift
                ;;
            -a|--audit-only)
                AUDIT_ONLY=true
                shift
                ;;
            -t|--test)
                TEST_MODE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Convert to absolute paths (only if relative)
    [[ "$PLAN_PDF" != /* ]] && PLAN_PDF="$PROJECT_ROOT/$PLAN_PDF"
    [[ "$ARTIFACTS_DIR" != /* ]] && ARTIFACTS_DIR="$PROJECT_ROOT/$ARTIFACTS_DIR"

    # Create artifacts directory
    mkdir -p "$ARTIFACTS_DIR"

    # Setup log file
    LOG_FILE="$ARTIFACTS_DIR/pipeline_execution.log"
    touch "$LOG_FILE"
}

show_help() {
    grep '^#' "$0" | grep -v '!/bin/bash' | sed 's/^# //' | sed 's/^#//'
}

# Check if virtual environment exists
check_venv() {
    step "Checking virtual environment"

    if [ ! -d "$VENV_PATH" ]; then
        error "Virtual environment not found at: $VENV_PATH"
        echo ""
        echo "Please create it first:"
        echo "  python3.12 -m venv farfan-env"
        echo "  source farfan-env/bin/activate"
        echo "  pip install -e ."
        step_failed
        return 1
    fi

    if [ ! -f "$VENV_PATH/bin/python" ]; then
        error "Python executable not found in virtual environment"
        step_failed
        return 1
    fi

    verbose "Virtual environment found at: $VENV_PATH"
    step_complete
    return 0
}

# Activate virtual environment
activate_venv() {
    step "Activating virtual environment"

    source "$VENV_PATH/bin/activate"

    if [ -z "${VIRTUAL_ENV:-}" ]; then
        error "Failed to activate virtual environment"
        step_failed
        return 1
    fi

    verbose "Virtual environment activated: $VIRTUAL_ENV"
    step_complete
    return 0
}

# Check Python version
check_python_version() {
    step "Checking Python version"

    local python_version
    python_version=$(python --version 2>&1 | awk '{print $2}')
    local major minor
    IFS='.' read -r major minor <<< "$python_version"

    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 12 ]); then
        error "Python 3.12+ required, found: $python_version"
        step_failed
        return 1
    fi

    verbose "Python version OK: $python_version"
    step_complete
    return 0
}

# Verify input PDF exists
check_input_pdf() {
    step "Verifying input PDF"

    if [ ! -f "$PLAN_PDF" ]; then
        error "Input PDF not found: $PLAN_PDF"
        echo ""
        echo "Available plans in data/plans/:"
        ls -1 "$PROJECT_ROOT/data/plans/"*.pdf 2>/dev/null || echo "  (none found)"
        step_failed
        return 1
    fi

    verbose "Input PDF found: $PLAN_PDF"
    step_complete
    return 0
}

# Check dependencies
check_dependencies() {
    step "Checking dependencies"

    # Check if package is installed
    if ! python -c "import farfan_pipeline" 2>/dev/null; then
        warning "Package 'farfan_pipeline' not found. Installing..."
        pip install -e . > "$ARTIFACTS_DIR/pip_install.log" 2>&1 || {
            error "Failed to install package. Check $ARTIFACTS_DIR/pip_install.log"
            step_failed
            return 1
        }
    fi

    # Check critical dependencies
    # Map package names to their import names (some differ)
    declare -A dep_import_map=(
        ["torch"]="torch"
        ["transformers"]="transformers"
        ["sentence_transformers"]="sentence_transformers"
        ["pandas"]="pandas"
        ["numpy"]="numpy"
        ["pdfplumber"]="pdfplumber"
        ["pymc"]="pymc"
        ["fastapi"]="fastapi"
    )

    local missing_deps=()
    for dep in "${!dep_import_map[@]}"; do
        local import_name="${dep_import_map[$dep]}"
        if ! python -c "import $import_name" 2>/dev/null; then
            missing_deps+=("$dep")
        fi
    done

    if [ ${#missing_deps[@]} -gt 0 ]; then
        error "Missing critical dependencies: ${missing_deps[*]}"
        step_failed
        return 1
    fi

    verbose "All dependencies OK"
    step_complete
    return 0
}

# Set environment variables
set_env_vars() {
    step "Setting environment variables"

    # Set determinism seed
    export PYTHONHASHSEED=42
    verbose "Set PYTHONHASHSEED=42 for determinism"

    # Set manifest secret key
    # Only use default in test mode; fail otherwise to prevent insecure production deployments
    if [ -z "${MANIFEST_SECRET_KEY:-}" ]; then
        if [[ "$TEST_MODE" == true ]] || [[ "${NODE_ENV:-}" == "development" ]] || [[ -n "${CI:-}" ]]; then
            export MANIFEST_SECRET_KEY="default-dev-key-change-in-production"
            warning "Using default MANIFEST_SECRET_KEY (acceptable in test/dev mode)"
        else
            error "MANIFEST_SECRET_KEY is not set and not running in test/dev mode"
            error "Set MANIFEST_SECRET_KEY environment variable or use --test flag for development"
            exit 1
        fi
    else
        verbose "Using custom MANIFEST_SECRET_KEY"
    fi

    # Set debug mode
    if [ "$DEBUG" == true ]; then
        export PIPELINE_DEBUG=1
        export FARFAN_LOG_LEVEL="DEBUG"
        verbose "Debug mode enabled"
    else
        export FARFAN_LOG_LEVEL="INFO"
    fi

    # Set paths
    export PYTHONPATH="$SRC_DIR:${PYTHONPATH:-}"
    export FARFAN_DATA_PATH="$PROJECT_ROOT/data"
    export FARFAN_CACHE_DIR="$PROJECT_ROOT/.cache"
    export FARFAN_ROOT="$PROJECT_ROOT"

    verbose "PYTHONPATH: $PYTHONPATH"
    verbose "FARFAN_DATA_PATH: $FARFAN_DATA_PATH"
    verbose "FARFAN_CACHE_DIR: $FARFAN_CACHE_DIR"

    step_complete
    return 0
}

################################################################################
# CODE QUALITY ASSURANCE
################################################################################

# Run formatters
run_formatting() {
    if [[ "$SKIP_QUALITY" == true ]]; then
        warning "Skipping formatting (quality gates disabled)"
        return 0
    fi

    step "Running code formatters"

    local format_failed=0

    # Black
    info "Running Black formatter..."
    if ! black --check --diff . > "$ARTIFACTS_DIR/black_check.log" 2>&1; then
        warning "Code formatting issues found. Applying fixes..."
        if ! black --line-length=100 . > "$ARTIFACTS_DIR/black_format.log" 2>&1; then
            error "Black formatting failed"
            format_failed=1
        fi
    fi

    # isort
    info "Running isort..."
    if ! isort --check-only --diff . > "$ARTIFACTS_DIR/isort_check.log" 2>&1; then
        warning "Import ordering issues found. Applying fixes..."
        if ! isort --profile=black --line-length=100 . > "$ARTIFACTS_DIR/isort_format.log" 2>&1; then
            error "isort formatting failed"
            format_failed=1
        fi
    fi

    if [ $format_failed -eq 0 ]; then
        step_complete
        return 0
    else
        step_failed
        return 1
    fi
}

# Run linters
run_linting() {
    if [[ "$SKIP_QUALITY" == true ]]; then
        warning "Skipping linting (quality gates disabled)"
        return 0
    fi

    step "Running linters"

    local lint_failed=0

    # Ruff
    info "Running Ruff..."
    if ! ruff check . > "$ARTIFACTS_DIR/ruff.log" 2>&1; then
        warning "Ruff found issues. Attempting auto-fix..."
        ruff check --fix . > "$ARTIFACTS_DIR/ruff_fix.log" 2>&1 || lint_failed=1
    fi

    # Flake8
    info "Running Flake8..."
    if ! flake8 . --max-line-length=100 --extend-ignore=E203,W503 \
        --statistics --count > "$ARTIFACTS_DIR/flake8.log" 2>&1; then
        warning "Flake8 found issues"
        lint_failed=1
    fi

    # MyPy (optional, may fail)
    info "Running MyPy type checker..."
    mypy . --ignore-missing-imports > "$ARTIFACTS_DIR/mypy.log" 2>&1 || true

    if [ $lint_failed -eq 0 ]; then
        step_complete
        return 0
    else
        step_failed
        return 1
    fi
}

# Run security scans
run_security_scans() {
    if [[ "$SKIP_QUALITY" == true ]]; then
        warning "Skipping security scans (quality gates disabled)"
        return 0
    fi

    step "Running security scans"

    local security_failed=0

    # Bandit
    info "Running Bandit security scan..."
    bandit -r . -f json -o "$ARTIFACTS_DIR/bandit_report.json" \
        > "$ARTIFACTS_DIR/bandit.log" 2>&1 || security_failed=1

    # Safety
    info "Running Safety dependency check..."
    safety check --json > "$ARTIFACTS_DIR/safety_report.json" \
        2>&1 || true

    # Pip-audit
    info "Running pip-audit..."
    pip-audit --format json --output "$ARTIFACTS_DIR/pip_audit_report.json" \
        > "$ARTIFACTS_DIR/pip_audit.log" 2>&1 || true

    # Check for critical vulnerabilities
    if [ -f "$ARTIFACTS_DIR/bandit_report.json" ]; then
        local critical_issues
        critical_issues=$(python3 -c "
import json
with open('$ARTIFACTS_DIR/bandit_report.json', 'r') as f:
    data = json.load(f)
    critical = [r for r in data.get('results', []) if r.get('issue_severity') == 'HIGH']
    print(len(critical))
" 2>/dev/null || echo "0")

        if [ "$critical_issues" -gt 0 ]; then
            error "Found $critical_issues critical security issues"
            security_failed=1
        fi
    fi

    if [ $security_failed -eq 0 ]; then
        step_complete
        return 0
    else
        step_failed
        return 1
    fi
}

# Run tests
run_tests() {
    if [[ "$SKIP_QUALITY" == true ]]; then
        warning "Skipping tests (quality gates disabled)"
        return 0
    fi

    step "Running test suite"

    local test_failed=0

    # Run pytest with coverage
    info "Running pytest with coverage..."
    pytest tests/ -v \
        --cov=. \
        --cov-report=term-missing \
        --cov-report=html:"$ARTIFACTS_DIR/coverage_html" \
        --cov-report=xml:"$ARTIFACTS_DIR/coverage.xml" \
        --junitxml="$ARTIFACTS_DIR/junit.xml" \
        > "$ARTIFACTS_DIR/pytest.log" 2>&1 || test_failed=1

    # Check coverage
    if [ -f "$ARTIFACTS_DIR/coverage.xml" ]; then
        local coverage
        coverage=$(python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('$ARTIFACTS_DIR/coverage.xml')
root = tree.getroot()
coverage_elem = root.find('.//coverage')
print(coverage_elem.get('line-rate', '0') if coverage_elem is not None else '0')
" 2>/dev/null || echo "0")

        local coverage_pct=$(echo "$coverage * 100" | bc)
        verbose "Coverage: ${coverage_pct}%"

        if (( $(echo "$coverage_pct < $COVERAGE_THRESHOLD" | bc -l) )); then
            warning "Coverage ${coverage_pct}% is below threshold ${COVERAGE_THRESHOLD}%"
            test_failed=1
        fi
    fi

    if [ $test_failed -eq 0 ]; then
        step_complete
        return 0
    else
        step_failed
        return 1
    fi
}

################################################################################
# CONTRACT VALIDATION
################################################################################

# Run CQVR contract validation
run_cqvr_validation() {
    step "Running CQVR contract validation"

    local cqvr_failed=0
    local contracts_dir="$SRC_DIR/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts/specialized"
    local output_dir="$ARTIFACTS_DIR/cqvr_reports"

    mkdir -p "$output_dir"

    if [ ! -d "$contracts_dir" ]; then
        warning "CQVR contracts directory not found: $contracts_dir"
        step_complete
        return 0
    fi

    # Run CQVR batch evaluator
    info "Evaluating contracts with threshold: $CQVR_THRESHOLD/100"
    python scripts/cqvr_batch_evaluator.py \
        --contracts-dir "$contracts_dir" \
        --output-dir "$output_dir" \
        --threshold "$CQVR_THRESHOLD" \
        > "$ARTIFACTS_DIR/cqvr.log" 2>&1 || cqvr_failed=1

    # Check results
    if [ -f "$output_dir/cqvr_evaluation_report.json" ]; then
        local failed passed total
        failed=$(python3 -c "
import json
with open('$output_dir/cqvr_evaluation_report.json', 'r') as f:
    print(json.load(f).get('failed', 0))
" 2>/dev/null || echo "0")

        passed=$(python3 -c "
import json
with open('$output_dir/cqvr_evaluation_report.json', 'r') as f:
    print(json.load(f).get('passed', 0))
" 2>/dev/null || echo "0")

        total=$((failed + passed))

        info "CQVR Results: $passed/$total passed, $failed failed"

        if [ "$failed" -gt 0 ]; then
            error "$failed contracts failed quality threshold"
            cqvr_failed=1
        fi
    fi

    if [ $cqvr_failed -eq 0 ]; then
        step_complete
        return 0
    else
        step_failed
        return 1
    fi
}

################################################################################
# ARCHITECTURE VALIDATION
################################################################################

# Validate architecture
validate_architecture() {
    step "Validating architectural integrity"

    if [ ! -f "$SCRIPT_DIR/validate_architecture.sh" ]; then
        warning "Architecture validation script not found"
        step_complete
        return 0
    fi

    bash "$SCRIPT_DIR/validate_architecture.sh" > "$ARTIFACTS_DIR/architecture_validation.log" 2>&1
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        verbose "Architecture validation passed"
        step_complete
        return 0
    else
        error "Architecture validation failed with exit code: $exit_code"
        step_failed
        return 1
    fi
}

# Stratify imports
stratify_imports() {
    step "Stratifying imports (architectural analysis)"

    if [ ! -f "$SCRIPT_DIR/stratify_imports.sh" ]; then
        warning "Import stratification script not found"
        step_complete
        return 0
    fi

    bash "$SCRIPT_DIR/stratify_imports.sh" > "$ARTIFACTS_DIR/stratification.log" 2>&1
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        verbose "Import stratification completed"
        # Copy stratification artifacts
        if [ -d "$PROJECT_ROOT/artifacts/stratification" ]; then
            cp -r "$PROJECT_ROOT/artifacts/stratification" "$ARTIFACTS_DIR/"
        fi
        step_complete
        return 0
    else
        warning "Import stratification completed with warnings (exit code: $exit_code)"
        # Don't fail on stratification warnings
        step_complete
        return 0
    fi
}

# Run orchestrator audit
audit_orchestrator() {
    step "Auditing orchestrator canonical flux"

    local orchestrator_path="$SRC_DIR/farfan_pipeline/orchestration/orchestrator.py"
    local audit_output="$ARTIFACTS_DIR/orchestrator_audit.json"

    if [ ! -f "$orchestrator_path" ]; then
        warning "Orchestrator not found: $orchestrator_path"
        step_complete
        return 0
    fi

    if [ ! -f "$SCRIPT_DIR/audit/audit_orchestrator_canonical_flux.py" ]; then
        warning "Orchestrator audit script not found"
        step_complete
        return 0
    fi

    python "$SCRIPT_DIR/audit/audit_orchestrator_canonical_flux.py" \
        --orchestrator "$orchestrator_path" \
        --output "$audit_output" \
        > "$ARTIFACTS_DIR/orchestrator_audit.log" 2>&1

    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        verbose "Orchestrator audit passed"
        step_complete
        return 0
    else
        warning "Orchestrator audit found issues"
        step_complete
        return 0
    fi
}

################################################################################
# PIPELINE EXECUTION
################################################################################

# Run the main pipeline
run_pipeline() {
    section "EXECUTING F.A.R.F.A.N PIPELINE"

    step "Starting pipeline execution"

    info "Input: $PLAN_PDF"
    info "Output: $ARTIFACTS_DIR"
    info "Mode: $EXECUTION_MODE"

    # Check for the verified pipeline script
    local pipeline_script="$SCRIPT_DIR/run_policy_pipeline_verified.py"

    if [ ! -f "$pipeline_script" ]; then
        warning "Verified pipeline script not found: $pipeline_script"
        warning "Looking for alternative pipeline entry point..."

        # Try to use the orchestrator directly
        local orchestrator_script="$SRC_DIR/farfan_pipeline/orchestration/orchestrator.py"
        if [ -f "$orchestrator_script" ]; then
            info "Using orchestrator directly"
            python -c "
from farfan_pipeline.orchestration.orchestrator import UnifiedOrchestrator, OrchestratorConfig
import sys

try:
    config = OrchestratorConfig(
        document_path='$PLAN_PDF',
        output_dir='$ARTIFACTS_DIR',
        municipality_name='pipeline_execution'
    )
    orchestrator = UnifiedOrchestrator(config)
    result = orchestrator.execute()
    sys.exit(0 if result.success else 1)
except Exception as e:
    print(f'Pipeline execution failed: {e}', file=sys.stderr)
    sys.exit(1)
" > "$ARTIFACTS_DIR/pipeline_execution.log" 2>&1
        else
            error "No pipeline entry point found"
            step_failed
            return 1
        fi
    else
        # Run the verified pipeline script
        python "$pipeline_script" \
            --plan "$PLAN_PDF" \
            --artifacts-dir "$ARTIFACTS_DIR" \
            > "$ARTIFACTS_DIR/pipeline_execution.log" 2>&1
    fi

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        success "Pipeline executed successfully"
        step_complete
        return 0
    else
        error "Pipeline execution failed with exit code: $exit_code"
        error "Check $ARTIFACTS_DIR/pipeline_execution.log for details"
        step_failed
        return 1
    fi
}

################################################################################
# POST-EXECUTION VALIDATION
################################################################################

# Verify artifacts
verify_artifacts() {
    step "Verifying generated artifacts"

    local required_artifacts=(
        "verification_manifest.json"
        "execution_claims.json"
    )

    local missing_artifacts=()

    for artifact in "${required_artifacts[@]}"; do
        if [ ! -f "$ARTIFACTS_DIR/$artifact" ]; then
            missing_artifacts+=("$artifact")
        fi
    done

    if [ ${#missing_artifacts[@]} -gt 0 ]; then
        error "Missing required artifacts: ${missing_artifacts[*]}"
        step_failed
        return 1
    fi

    # Verify manifest integrity
    info "Verifying manifest integrity..."
    python -c "
from farfan_pipeline.orchestration.verification_manifest import verify_manifest_integrity
import json

with open('$ARTIFACTS_DIR/verification_manifest.json', 'r') as f:
    manifest = json.load(f)

valid, _ = verify_manifest_integrity(manifest)
if valid:
    print('Manifest integrity verified')
    exit(0)
else:
    print('Manifest integrity check failed')
    exit(1)
" > "$ARTIFACTS_DIR/manifest_verification.log" 2>&1

    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        step_complete
        return 0
    else
        error "Manifest integrity verification failed"
        step_failed
        return 1
    fi
}

################################################################################
# REPORT GENERATION
################################################################################

# Generate quality report
generate_quality_report() {
    step "Generating quality report"

    if [ ! -f "$SCRIPT_DIR/generate_quality_report.py" ]; then
        warning "Quality report generator not found"
        step_complete
        return 0
    fi

    python "$SCRIPT_DIR/generate_quality_report.py" > "$ARTIFACTS_DIR/quality_report_generation.log" 2>&1

    if [ -f "$PROJECT_ROOT/quality_report.html" ]; then
        mv "$PROJECT_ROOT/quality_report.html" "$ARTIFACTS_DIR/"
        success "Quality report generated: $ARTIFACTS_DIR/quality_report.html"
    fi

    step_complete
    return 0
}

# Generate summary report
generate_summary_report() {
    section "GENERATING SUMMARY REPORT"

    step "Generating execution summary"

    local summary_file="$ARTIFACTS_DIR/execution_summary.json"

    python3 -c "
import json
from datetime import datetime

summary = {
    'timestamp': datetime.now().isoformat(),
    'execution_mode': '$EXECUTION_MODE',
    'plan_pdf': '$PLAN_PDF',
    'artifacts_dir': '$ARTIFACTS_DIR',
    'total_steps': $TOTAL_STEPS,
    'completed_steps': $COMPLETED_STEPS,
    'failed_steps': $FAILED_STEPS,
    'success_rate': round($COMPLETED_STEPS / $TOTAL_STEPS * 100, 2) if $TOTAL_STEPS > 0 else 0,
    'exit_code': ${1:-0},
    'quality_gates_skipped': $SKIP_QUALITY,
    'test_mode': $TEST_MODE
}

with open('$summary_file', 'w') as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))
"

    cat "$summary_file" | tee -a "$LOG_FILE"

    step_complete
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    # Parse arguments
    parse_arguments "$@"

    # Print banner
    section "F.A.R.F.A.N COMPREHENSIVE PIPELINE"
    info "Framework for Advanced Retrieval and Forensic Analysis of Administrative Narratives"
    info "Version: 2.0.0"
    info "Execution started at: $(date)"
    info "Log file: $LOG_FILE"
    echo ""

    # Pre-flight validation
    section "PHASE 1: PRE-FLIGHT VALIDATION"
    check_venv || exit 1
    activate_venv || exit 1
    check_python_version || exit 1
    check_input_pdf || exit 1
    check_dependencies || exit 1
    set_env_vars || exit 1

    # Architecture validation
    section "PHASE 2: ARCHITECTURE VALIDATION"
    validate_architecture || exit 4
    stratify_imports || exit 4
    audit_orchestrator || exit 4

    # Code quality (skip if requested)
    if [[ "$AUDIT_ONLY" != true && "$CQVR_ONLY" != true ]]; then
        section "PHASE 3: CODE QUALITY ASSURANCE"
        if [[ "$SKIP_QUALITY" != true ]]; then
            run_formatting || exit 2
            run_linting || exit 2
            run_security_scans || exit 2
            run_tests || exit 2
        else
            warning "Quality gates skipped"
        fi
    fi

    # Contract validation
    section "PHASE 4: CONTRACT VALIDATION"
    run_cqvr_validation || exit 3

    # Skip pipeline execution if audit-only
    if [[ "$AUDIT_ONLY" == true ]]; then
        info "Audit-only mode: skipping pipeline execution"
    elif [[ "$CQVR_ONLY" == true ]]; then
        info "CQVR-only mode: skipping pipeline execution"
    else
        section "PHASE 5: PIPELINE EXECUTION"
        run_pipeline || exit 5

        section "PHASE 6: POST-EXECUTION VALIDATION"
        verify_artifacts || exit 6
    fi

    # Report generation
    section "PHASE 7: REPORT GENERATION"
    generate_quality_report || exit 7
    generate_summary_report 0

    # Final summary
    section "PIPELINE COMPLETION SUMMARY"
    echo "" | tee -a "$LOG_FILE"
    info "Total Steps: $TOTAL_STEPS"
    info "Completed: $COMPLETED_STEPS"
    info "Failed: $FAILED_STEPS"
    echo "" | tee -a "$LOG_FILE"
    success "Pipeline execution completed successfully!"
    echo "" | tee -a "$LOG_FILE"
    info "Artifacts saved to: $ARTIFACTS_DIR"
    info "Log file: $LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    info "Key artifacts:"
    info "  - Execution summary: $ARTIFACTS_DIR/execution_summary.json"
    info "  - Quality report: $ARTIFACTS_DIR/quality_report.html"
    info "  - Test coverage: $ARTIFACTS_DIR/coverage_html/index.html"
    info "  - Security reports: $ARTIFACTS_DIR/bandit_report.json"
    info "  - CQVR reports: $ARTIFACTS_DIR/cqvr_reports/"
    echo "" | tee -a "$LOG_FILE"

    return 0
}

# Run main function
main "$@"
exit $?
