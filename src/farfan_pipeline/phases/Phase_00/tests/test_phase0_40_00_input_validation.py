import pytest
from pathlib import Path
from farfan_pipeline.phases.Phase_00.phase0_40_00_input_validation import (
    Phase0Input,
    CanonicalInput,
    Phase0ValidationContract,
    Phase0InputValidator
)

def test_phase0_input_validation():
    """Test Phase0Input validation logic."""
    with pytest.raises(TypeError):
        Phase0Input(pdf_path="not_a_path", run_id="run1")
    
    input_obj = Phase0Input(pdf_path=Path("test.pdf"), run_id="run1")
    assert input_obj.run_id == "run1"

def test_pydantic_validator_security():
    """Test security checks in pydantic validator."""
    # Path traversal
    with pytest.raises(ValueError, match="path traversal"):
        Phase0InputValidator.validate_pdf_path("../etc/passwd")
    
    # Null byte
    with pytest.raises(ValueError, match="null bytes"):
        Phase0InputValidator.validate_pdf_path("test.pdf\x00")
        
    # SQL Injection
    with pytest.raises(ValueError, match="SQL injection"):
        Phase0InputValidator.validate_run_id("run1; DROP TABLE users")

@pytest.mark.asyncio
async def test_contract_execution_missing_file(temp_dir):
    """Test contract fails when file missing."""
    contract = Phase0ValidationContract()
    input_data = Phase0Input(pdf_path=temp_dir / "missing.pdf", run_id="test_run")
    
    with pytest.raises(FileNotFoundError):
        await contract.execute(input_data)
