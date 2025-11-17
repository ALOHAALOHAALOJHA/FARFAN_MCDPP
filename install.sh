#!/usr/bin/env bash
#
# F.A.R.F.A.N Installation Script
# ================================
# Complete setup for F.A.R.F.A.N Mechanistic Policy Pipeline
#
# Requirements:
#   - Ubuntu/Debian 20.04+ (or compatible Linux)
#   - Python 3.12.x
#   - sudo access for system dependencies
#
# Usage:
#   bash install.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "F.A.R.F.A.N Installation Script"
echo "=========================================="
echo ""

# 1. Check Python 3.12
echo -e "${YELLOW}[1/7] Checking Python 3.12...${NC}"
if ! command -v python3.12 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3.12 not found${NC}"
    echo "Install with: sudo apt-get install python3.12 python3.12-venv python3.12-dev"
    exit 1
fi

PYTHON_VERSION=$(python3.12 --version | awk '{print $2}')
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

# 2. Install system dependencies
echo ""
echo -e "${YELLOW}[2/7] Installing system dependencies...${NC}"
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
    build-essential \
    python3.12-dev \
    gfortran \
    libopenblas-dev \
    libhdf5-dev \
    ghostscript \
    python3-tk \
    libgraphviz-dev \
    graphviz \
    default-jre

echo -e "${GREEN}✓ System dependencies installed${NC}"

# 3. Create virtual environment
echo ""
echo -e "${YELLOW}[3/7] Creating virtual environment...${NC}"
if [ -d "farfan-env" ]; then
    echo "Removing old virtual environment..."
    rm -rf farfan-env
fi

python3.12 -m venv farfan-env
source farfan-env/bin/activate

echo -e "${GREEN}✓ Virtual environment created${NC}"

# 4. Upgrade pip, setuptools, wheel
echo ""
echo -e "${YELLOW}[4/7] Upgrading pip, setuptools, wheel...${NC}"
pip install --upgrade pip setuptools wheel --quiet

echo -e "${GREEN}✓ Package tools upgraded${NC}"

# 5. Install package in development mode
echo ""
echo -e "${YELLOW}[5/7] Installing F.A.R.F.A.N package...${NC}"
echo "This may take several minutes..."

# Install base package
pip install --no-cache-dir -e . --quiet

# Install ML extras
pip install --no-cache-dir tensorflow==2.18.0 tf-keras --quiet

# Install Bayesian extras with correct versions
pip install --no-cache-dir "pytensor>=2.25.1,<2.26" "pymc==5.16.2" "arviz>=0.20.0" --quiet

# Install additional dependencies
pip install --no-cache-dir \
    sentencepiece \
    tiktoken \
    fuzzywuzzy \
    python-Levenshtein \
    tabula-py \
    "camelot-py[cv]" \
    pydot \
    --quiet

# Force compatible numpy and opencv-python-headless
pip install --force-reinstall --no-deps numpy==1.26.4 --quiet
pip install --no-deps opencv-python-headless==4.10.0.84 --quiet

echo -e "${GREEN}✓ F.A.R.F.A.N package installed${NC}"

# 6. Install SpaCy models
echo ""
echo -e "${YELLOW}[6/7] Installing SpaCy language models...${NC}"
if python -m spacy download es_core_news_lg 2>&1 | grep -q "Successfully"; then
    echo -e "${GREEN}✓ es_core_news_lg installed${NC}"
else
    echo -e "${YELLOW}⚠ Could not download es_core_news_lg (network issue)${NC}"
fi

if python -m spacy download es_dep_news_trf 2>&1 | grep -q "Successfully"; then
    echo -e "${GREEN}✓ es_dep_news_trf installed${NC}"
else
    echo -e "${YELLOW}⚠ Could not download es_dep_news_trf (network issue)${NC}"
fi

# 7. Verify installation
echo ""
echo -e "${YELLOW}[7/7] Verifying installation...${NC}"
if python scripts/verify_dependencies.py 2>&1 | grep -q "All checks passed"; then
    echo -e "${GREEN}✓ All dependencies verified!${NC}"
else
    echo -e "${YELLOW}⚠ Some checks failed - see above for details${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "To activate the environment:"
echo "  source farfan-env/bin/activate"
echo ""
echo "To run the verification script:"
echo "  python scripts/verify_dependencies.py"
echo ""
