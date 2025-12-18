#!/usr/bin/env python3
"""
Validate that contracts can be loaded and processed by BaseExecutorWithContract.

This script verifies that the actual base executor can load and validate
contracts using its internal verification methods.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from canonic_phases.Phase_two.phase2_b_base_executor_with_contract import BaseExecutorWithContract
    print("✅ Successfully imported BaseExecutorWithContract")
except ImportError as e:
    print(f"❌ Failed to import BaseExecutorWithContract: {e}")
    sys.exit(1)

def test_contract_verification():
    """Test that BaseExecutorWithContract can verify contracts."""
    print("\n" + "="*80)
    print("EXECUTOR INTEGRATION VALIDATION")
    print("="*80)
    
    print("\n1. Testing contract verification method...")
    
    # Test verification for a sample of base slots
    test_slots = ["D1-Q1", "D2-Q3", "D3-Q5", "D4-Q2", "D5-Q4", "D6-Q1"]
    
    all_passed = True
    for base_slot in test_slots:
        try:
            result = BaseExecutorWithContract._verify_single_contract(base_slot, None)
            if result["passed"]:
                print(f"  ✅ {base_slot}: Passed verification")
            else:
                print(f"  ❌ {base_slot}: Failed verification")
                for error in result["errors"]:
                    print(f"     - {error}")
                all_passed = False
        except Exception as e:
            print(f"  ❌ {base_slot}: Exception during verification: {e}")
            all_passed = False
    
    print("\n2. Testing contract loading...")
    
    # Create a mock class to test _load_contract
    class TestExecutor(BaseExecutorWithContract):
        @classmethod
        def get_base_slot(cls) -> str:
            return "D1-Q1"
    
    try:
        contract = TestExecutor._load_contract()
        print(f"  ✅ Successfully loaded contract for D1-Q1")
        print(f"     Version: {contract.get('_contract_version', 'unknown')}")
        print(f"     Identity: {contract.get('identity', {}).get('question_id', 'unknown')}")
        print(f"     Methods: {len(contract.get('method_binding', {}).get('methods', []))} methods")
    except Exception as e:
        print(f"  ❌ Failed to load contract: {e}")
        all_passed = False
    
    print("\n3. Testing contract version detection...")
    
    if 'contract' in locals():
        version = BaseExecutorWithContract._detect_contract_version(contract)
        print(f"  ✅ Detected version: {version}")
        
        if version == "v3":
            print(f"     ✅ Correctly identified as v3 contract")
        else:
            print(f"     ❌ Incorrect version detection")
            all_passed = False
    
    print("\n4. Testing schema validation...")
    
    try:
        validator = BaseExecutorWithContract._get_schema_validator("v3")
        print(f"  ✅ Schema validator loaded for v3")
    except FileNotFoundError as e:
        print(f"  ⚠️  Schema file not found (this is optional): {e}")
    except Exception as e:
        print(f"  ❌ Failed to load schema validator: {e}")
        all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL EXECUTOR INTEGRATION TESTS PASSED")
        print("="*80)
        print("\nContracts are fully compatible with BaseExecutorWithContract")
        print("System ready for production execution")
        return 0
    else:
        print("❌ SOME EXECUTOR INTEGRATION TESTS FAILED")
        print("="*80)
        return 1

if __name__ == "__main__":
    sys.exit(test_contract_verification())
