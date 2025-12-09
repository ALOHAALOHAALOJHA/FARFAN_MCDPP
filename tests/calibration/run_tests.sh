#!/bin/bash
# Calibration Test Suite Runner
# 
# Runs various test categories and generates reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    print_error "pytest not found. Please install with: pip install pytest pytest-cov pytest-html hypothesis"
    exit 1
fi

# Create reports directory
REPORTS_DIR="test_reports"
mkdir -p "$REPORTS_DIR"

# Parse command line arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-yes}"

case "$TEST_TYPE" in
    all)
        print_header "Running Complete Test Suite"
        if [ "$COVERAGE" == "yes" ]; then
            pytest tests/calibration/ -v \
                --cov=src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization \
                --cov-report=html:$REPORTS_DIR/coverage \
                --cov-report=term \
                --html=$REPORTS_DIR/test_report.html \
                --self-contained-html \
                -m "not slow"
        else
            pytest tests/calibration/ -v \
                --html=$REPORTS_DIR/test_report.html \
                --self-contained-html \
                -m "not slow"
        fi
        ;;
        
    unit)
        print_header "Running Unit Tests"
        pytest tests/calibration/ -v \
            --html=$REPORTS_DIR/unit_test_report.html \
            --self-contained-html \
            -m "not integration and not regression and not performance and not property"
        ;;
        
    integration)
        print_header "Running Integration Tests"
        pytest tests/calibration/ -v \
            --html=$REPORTS_DIR/integration_test_report.html \
            --self-contained-html \
            -m integration
        ;;
        
    property)
        print_header "Running Property-Based Tests"
        pytest tests/calibration/ -v \
            --html=$REPORTS_DIR/property_test_report.html \
            --self-contained-html \
            -m property
        ;;
        
    regression)
        print_header "Running Regression Tests"
        pytest tests/calibration/ -v \
            --html=$REPORTS_DIR/regression_test_report.html \
            --self-contained-html \
            -m regression
        ;;
        
    performance)
        print_header "Running Performance Tests"
        pytest tests/calibration/ -v \
            --html=$REPORTS_DIR/performance_test_report.html \
            --self-contained-html \
            -m performance
        ;;
        
    slow)
        print_header "Running All Tests (Including Slow)"
        pytest tests/calibration/ -v \
            --html=$REPORTS_DIR/full_test_report.html \
            --self-contained-html
        ;;
        
    coverage)
        print_header "Generating Coverage Report"
        pytest tests/calibration/ -v \
            --cov=src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization \
            --cov-report=html:$REPORTS_DIR/coverage \
            --cov-report=term-missing \
            --cov-report=json:$REPORTS_DIR/coverage.json
        print_success "Coverage report generated at $REPORTS_DIR/coverage/index.html"
        ;;
        
    quick)
        print_header "Running Quick Test Suite (No Coverage)"
        pytest tests/calibration/ -v \
            -x \
            -m "not slow and not performance"
        ;;
        
    *)
        echo "Usage: $0 {all|unit|integration|property|regression|performance|slow|coverage|quick} [yes|no]"
        echo ""
        echo "Test Types:"
        echo "  all         - Run all tests except slow ones (default, with coverage)"
        echo "  unit        - Run only unit tests"
        echo "  integration - Run only integration tests"
        echo "  property    - Run only property-based tests"
        echo "  regression  - Run only regression tests"
        echo "  performance - Run only performance tests"
        echo "  slow        - Run all tests including slow ones"
        echo "  coverage    - Generate detailed coverage report"
        echo "  quick       - Quick test run (fail fast, no coverage)"
        echo ""
        echo "Coverage:"
        echo "  Second argument: 'yes' (default) or 'no' to disable coverage"
        exit 1
        ;;
esac

# Check exit status
if [ $? -eq 0 ]; then
    print_success "Tests completed successfully!"
    if [ -f "$REPORTS_DIR/test_report.html" ] || [ -f "$REPORTS_DIR/${TEST_TYPE}_test_report.html" ]; then
        print_success "HTML report available in $REPORTS_DIR/"
    fi
    if [ -d "$REPORTS_DIR/coverage" ]; then
        print_success "Coverage report available at $REPORTS_DIR/coverage/index.html"
    fi
else
    print_error "Tests failed!"
    exit 1
fi
