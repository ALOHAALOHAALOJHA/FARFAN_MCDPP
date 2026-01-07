#!/bin/bash
# Test runner script for empirically-calibrated extractors
#
# Author: CQC Extractor Excellence Framework
# Version: 2.0.0
# Date: 2026-01-06

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/../../../../../../../"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Extractor Test Suite - Empirical Validation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not installed${NC}"
    echo "Install with: pip install pytest pytest-cov"
    exit 1
fi

# Parse arguments
RUN_MODE="${1:-all}"

case "$RUN_MODE" in
    all)
        echo -e "${GREEN}Running all extractor tests...${NC}"
        pytest src/farfan_pipeline/infrastructure/extractors/tests/ \
            -v \
            --tb=short \
            --color=yes
        ;;

    financial)
        echo -e "${GREEN}Running FinancialChainExtractor tests...${NC}"
        pytest src/farfan_pipeline/infrastructure/extractors/tests/test_financial_chain_extractor.py \
            -v \
            --tb=short \
            --color=yes
        ;;

    causal)
        echo -e "${GREEN}Running CausalVerbExtractor tests...${NC}"
        pytest src/farfan_pipeline/infrastructure/extractors/tests/test_causal_verb_extractor.py \
            -v \
            --tb=short \
            --color=yes
        ;;

    institutional)
        echo -e "${GREEN}Running InstitutionalNERExtractor tests...${NC}"
        pytest src/farfan_pipeline/infrastructure/extractors/tests/test_institutional_ner_extractor.py \
            -v \
            --tb=short \
            --color=yes
        ;;

    quick)
        echo -e "${YELLOW}Running quick smoke tests...${NC}"
        pytest src/farfan_pipeline/infrastructure/extractors/tests/ \
            -v \
            --tb=line \
            -x \
            --color=yes \
            -k "test_.*_extraction or test_convenience"
        ;;

    coverage)
        echo -e "${GREEN}Running tests with coverage...${NC}"
        pytest src/farfan_pipeline/infrastructure/extractors/tests/ \
            -v \
            --tb=short \
            --cov=farfan_pipeline.infrastructure.extractors \
            --cov-report=html \
            --cov-report=term \
            --color=yes

        echo ""
        echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
        ;;

    empirical)
        echo -e "${GREEN}Running empirical validation tests only...${NC}"
        pytest src/farfan_pipeline/infrastructure/extractors/tests/ \
            -v \
            --tb=short \
            --color=yes \
            -k "empirical"
        ;;

    help|--help|-h)
        echo "Usage: ./run_tests.sh [MODE]"
        echo ""
        echo "Modes:"
        echo "  all          - Run all extractor tests (default)"
        echo "  financial    - Run FinancialChainExtractor tests only"
        echo "  causal       - Run CausalVerbExtractor tests only"
        echo "  institutional - Run InstitutionalNERExtractor tests only"
        echo "  quick        - Run quick smoke tests"
        echo "  coverage     - Run tests with coverage report"
        echo "  empirical    - Run empirical validation tests only"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh all"
        echo "  ./run_tests.sh financial"
        echo "  ./run_tests.sh coverage"
        exit 0
        ;;

    *)
        echo -e "${RED}Unknown mode: $RUN_MODE${NC}"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ Some tests failed${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
