#!/bin/bash
# Verification script for orchestrator fixes

set -e

echo "=========================================="
echo "ORCHESTRATOR FIX VERIFICATION"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if fix script exists
if [ ! -f "fix_orchestrator.py" ]; then
    echo -e "${RED}✗ fix_orchestrator.py not found${NC}"
    exit 1
fi

# Run the fix script
echo -e "\n[1/5] Applying orchestrator fixes..."
# python fix_orchestrator.py
echo "Skipping fix script (fixes applied manually)"

# Check Python syntax
echo -e "\n[2/5] Checking Python syntax..."
python -m py_compile src/orchestration/orchestrator.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python syntax valid${NC}"
else
    echo -e "${RED}✗ Syntax errors detected${NC}"
    exit 1
fi

# Run import test
echo -e "\n[3/5] Testing orchestrator import..."
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -c "from orchestration.orchestrator import Orchestrator; print('✓ Import successful')"

# Run the pipeline with verification
echo -e "\n[4/5] Running pipeline with verification..."
python scripts/run_policy_pipeline_verified.py \
    --input tests/fixtures/cpp_policy_sample.pdf \
    --verbose \
    --debug 2>&1 | tee pipeline_run.log

# Check verification manifest
echo -e "\n[5/5] Checking verification manifest..."
if [ -f "artifacts/plan1/verification_manifest.json" ]; then
    SUCCESS=$(jq -r '.success' artifacts/plan1/verification_manifest.json)
    PHASES=$(jq -r '.phases_completed' artifacts/plan1/verification_manifest.json)
    QUESTIONS=$(jq -r '.micro_questions_answered' artifacts/plan1/verification_manifest.json)
    
    echo "Verification Results:"
    echo "  Success: $SUCCESS"
    echo "  Phases Completed: $PHASES"
    echo "  Questions Answered: $QUESTIONS"
    
    if [ "$SUCCESS" = "true" ] && [ "$PHASES" -eq 10 ]; then
        echo -e "${GREEN}✓ PIPELINE VERIFIED - All checks passed${NC}"
        
        # List generated artifacts
        echo -e "\nGenerated Artifacts:"
        ls -la artifacts/plan1/*. json 2>/dev/null || echo "No artifacts found"
        
        exit 0
    else
        echo -e "${RED}✗ Pipeline verification failed${NC}"
        
        # Show error details
        echo -e "\nError Analysis:"
        grep -i "error\|failed\|exception" pipeline_run.log | head -20
        
        exit 1
    fi
else
    echo -e "${RED}✗ Verification manifest not found${NC}"
    exit 1
fi