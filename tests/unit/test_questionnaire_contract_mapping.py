"""
Test for questionnaire contract mapping and completeness.
"""

import json
from pathlib import Path
import pytest
from typing import Any, Dict, List

# Add src to python path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MONOLITH_PATH = PROJECT_ROOT / "data" / "questionnaire_monolith.json"
CONTRACTS_DIR = PROJECT_ROOT / "config" / "executor_contracts"

def get_micro_questions(monolith: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Recursively finds and returns all micro-questions from the monolith.
    """
    micro_questions = []

    def find_in_obj(obj: Any):
        if isinstance(obj, dict):
            if "micro_questions" in obj and isinstance(obj["micro_questions"], list):
                micro_questions.extend(obj["micro_questions"])
            for key, value in obj.items():
                find_in_obj(value)
        elif isinstance(obj, list):
            for item in obj:
                find_in_obj(item)

    find_in_obj(monolith)
    return micro_questions

@pytest.fixture(scope="module")
def monolith_data() -> Dict[str, Any]:
    """
    Pytest fixture to load the questionnaire monolith data.
    """
    if not MONOLITH_PATH.exists():
        pytest.fail(f"Monolith file not found at {MONOLITH_PATH}")
    return json.loads(MONOLITH_PATH.read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def micro_questions(monolith_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Pytest fixture to extract all micro-questions from the monolith data.
    """
    return get_micro_questions(monolith_data)

@pytest.fixture(scope="module")
def contract_base_slots() -> List[str]:
    """
    Pytest fixture to get all base_slots from the contract files.
    """
    if not CONTRACTS_DIR.is_dir():
        return []
    
    slots = []
    for contract_file in CONTRACTS_DIR.glob("*.json"):
        try:
            contract_data = json.loads(contract_file.read_text(encoding="utf-8"))
            base_slot = contract_data.get("base_slot")
            if base_slot:
                slots.append(base_slot)
        except (json.JSONDecodeError, KeyError):
            # We can choose to fail the test if a contract is malformed
            pytest.fail(f"Could not parse contract file: {contract_file}")
    return slots

def test_all_micro_questions_have_contracts(micro_questions: List[Dict[str, Any]], contract_base_slots: List[str]):
    """
    Tests that every micro-question in the monolith has a corresponding contract.
    """
    missing_contracts = []
    for question in micro_questions:
        base_slot = question.get("base_slot")
        if base_slot and base_slot not in contract_base_slots:
            missing_contracts.append(question.get("question_id", "N/A"))
            
    # As per the current state, we expect this test to fail.
    # The goal is to reduce the number of missing contracts to zero.
    assert not missing_contracts, (
        f"Found {len(set(missing_contracts))} unique micro-questions without contracts: "
        f"{sorted(list(set(missing_contracts)))}"
    )

def test_no_orphan_contracts(micro_questions: List[Dict[str, Any]], contract_base_slots: List[str]):
    """
    Tests that every contract corresponds to at least one micro-question.
    """
    question_base_slots = {q.get("base_slot") for q in micro_questions if q.get("base_slot")}
    
    orphan_contracts = []
    for slot in contract_base_slots:
        if slot not in question_base_slots:
            orphan_contracts.append(slot)
            
    assert not orphan_contracts, (
        f"Found {len(orphan_contracts)} orphan contracts with no corresponding micro-question: "
        f"{sorted(orphan_contracts)}"
    )
