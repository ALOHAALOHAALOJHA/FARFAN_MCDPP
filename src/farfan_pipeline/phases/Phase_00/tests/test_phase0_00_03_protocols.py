import pytest
from farfan_pipeline.phases.Phase_00.phase0_00_03_protocols import (
    PhaseContract,
    ContractValidationResult,
    PhaseMetadata,
    PhaseInvariant
)

class MockContract(PhaseContract):
    def validate_input(self, input_data):
        return ContractValidationResult(passed=True, contract_type="input", phase_name="test")
    
    def validate_output(self, output_data):
        return ContractValidationResult(passed=True, contract_type="output", phase_name="test")
        
    async def execute(self, input_data):
        return input_data

@pytest.mark.asyncio
async def test_phase_contract_execution():
    """Test standard phase contract execution flow."""
    contract = MockContract("test_phase")
    input_data = {"key": "value"}
    output, metadata = await contract.run(input_data)
    
    assert output == input_data
    assert metadata.success is True
    assert metadata.phase_name == "test_phase"
    assert metadata.duration_ms is not None

def test_invariant_checking():
    """Test invariant checking logic."""
    contract = MockContract("test_phase")
    contract.add_invariant(
        name="test_inv",
        description="Always true",
        check=lambda x: True,
        error_message="Should not happen"
    )
    
    passed, errors = contract.check_invariants({"data": 1})
    assert passed is True
    assert len(errors) == 0

    contract.add_invariant(
        name="fail_inv",
        description="Always false",
        check=lambda x: False,
        error_message="Expected failure"
    )
    
    passed, errors = contract.check_invariants({"data": 1})
    assert passed is False
    assert len(errors) == 1
    assert "Expected failure" in errors[0]
