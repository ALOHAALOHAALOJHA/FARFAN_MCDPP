#!/usr/bin/env python3
"""
verify_contract_completeness.py - Verify that all micro-questions have a contract.

This script is designed to be used in a CI/CD pipeline to enforce contract
completeness for the questionnaire. It checks that every micro-question in the
monolith has a corresponding contract file. If any micro-question is found
without a contract, the script will print an error and exit with a non-zero
exit code.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add src to python path
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

def get_contract_definitions() -> Dict[str, Dict[str, Any]]:
    """
    Loads all contract definitions from the contracts directory.
    The key of the returned dictionary is the base_slot.
    """
    contracts = {}
    if not CONTRACTS_DIR.is_dir():
        return contracts

    for contract_file in CONTRACTS_DIR.glob("*.json"):
        try:
            contract_data = json.loads(contract_file.read_text(encoding="utf-8"))
            base_slot = contract_data.get("base_slot")
            if base_slot:
                contracts[base_slot] = contract_data
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load or parse contract {contract_file}: {e}", file=sys.stderr)
    return contracts

def run_verification():
    """
    Runs the verification and exits with a non-zero exit code on failure.
    """
    print("Starting contract completeness verification...")

    # Load monolith
    if not MONOLITH_PATH.exists():
        print(f"Error: Monolith file not found at {MONOLITH_PATH}", file=sys.stderr)
        sys.exit(1)
    monolith = json.loads(MONOLITH_PATH.read_text(encoding="utf-8"))

    # Get data for verification
    micro_questions = get_micro_questions(monolith)
    contracts = get_contract_definitions()

    uncontracted_questions = []
    for question in micro_questions:
        slot = question.get("base_slot")
        if slot and slot not in contracts:
            uncontracted_questions.append(question.get("question_id", "N/A"))

    if uncontracted_questions:
        print("\nError: Found micro-questions without a corresponding contract.", file=sys.stderr)
        print("The following questions are missing a contract:", file=sys.stderr)
        for question_id in sorted(list(set(uncontracted_questions))):
            print(f"- {question_id}", file=sys.stderr)
        
        # The plan mentions a coverage threshold of 100%. 
        # Since we found uncontracted questions, we exit with 1.
        print("\nContract coverage is less than 100%. Exiting with error.", file=sys.stderr)
        sys.exit(1)
    
    print("\nVerification successful: All micro-questions have a corresponding contract.")
    sys.exit(0)

if __name__ == "__main__":
    run_verification()
