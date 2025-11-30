#!/usr/bin/env python3
"""
audit_questionnaire_coverage.py - Audit the structural and contract coverage of the questionnaire.

This script performs a comprehensive audit of the questionnaire monolith and its
associated contracts and executors. It generates an audit manifest in JSON format
with detailed metrics about the coverage and any gaps found.

The audit checks for the following:
- Each micro-question in the monolith has a corresponding contract.
- Each contract has a corresponding micro-question.
- Each contract specifies method inputs.
- The classes and methods specified in the contract's method inputs are valid and resolvable.
"""

import json
import os
import inspect
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Add src to python path
sys.path.append(str(Path(__file__).parent.parent / "src"))


# Assuming the script is in the 'scripts' directory, the project root is the parent directory.
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MONOLITH_PATH = PROJECT_ROOT / "data" / "questionnaire_monolith.json"
CONTRACTS_DIR = PROJECT_ROOT / "config" / "executor_contracts"
CLASS_REGISTRY_PATH = PROJECT_ROOT / "src" / "farfan_core" / "core" / "orchestrator" / "class_registry.py"
OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "audit"
AUDIT_MANIFEST_PATH = OUTPUT_DIR / "audit_manifest.json"

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
            print(f"Warning: Could not load or parse contract {contract_file}: {e}")
    return contracts

def get_registered_classes_and_methods() -> Dict[str, Set[str]]:
    """
    Dynamically loads the class registry and inspects the classes to get their methods.
    """
    # This is a simplified way to get the class paths. In a real scenario,
    # we would need to handle the imports and dependencies correctly.
    # For this script, we'll simulate by extracting from the file content.
    class_paths = {}
    with open(CLASS_REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_content = f.read()
        # A bit of a hack to extract the _CLASS_PATHS dictionary
        try:
            start = registry_content.find("_CLASS_PATHS: Mapping[str, str] = {")
            if start != -1:
                dict_str = registry_content[start:]
                dict_str = dict_str[dict_str.find("{") : dict_str.find("}") + 1]
                class_paths = eval(dict_str)
        except Exception as e:
            print(f"Warning: Could not parse class registry: {e}")
            return {}

    registered_methods = {}
    for class_name, import_path in class_paths.items():
        try:
            module_name, _, class_name_from_path = import_path.rpartition(".")
            module = __import__(module_name, fromlist=[class_name_from_path])
            cls = getattr(module, class_name_from_path)
            methods = {
                name
                for name, func in inspect.getmembers(cls, inspect.isfunction)
                if not name.startswith("_")
            }
            registered_methods[class_name] = methods
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not import or inspect class {class_name}: {e}")
    return registered_methods

def run_audit():
    """
    Runs the full audit and generates the manifest.
    """
    print("Starting questionnaire coverage audit...")

    # Load monolith
    if not MONOLITH_PATH.exists():
        print(f"Error: Monolith file not found at {MONOLITH_PATH}")
        return
    monolith = json.loads(MONOLITH_PATH.read_text(encoding="utf-8"))

    # Get data for audit
    micro_questions = get_micro_questions(monolith)
    contracts = get_contract_definitions()
    registered_methods = get_registered_classes_and_methods()

    # Audit metrics
    total_micro_questions = len(micro_questions)
    questions_with_contract = 0
    questions_with_executor_mapping = 0
    questions_with_valid_executor = 0
    questions_with_valid_method_route = 0
    orphan_contracts = set(contracts.keys())
    uncontracted_questions_details = []
    questions_with_contract = 0
    
    for question in micro_questions:
        slot = question.get("base_slot")
        if slot and slot in contracts:
            questions_with_contract += 1
        elif slot:
            uncontracted_questions_details.append(question.get("question_id"))

    questions_without_contract = len(uncontracted_questions_details)

    questions_with_executor_mapping = 0
    questions_with_valid_executor = 0
    questions_with_valid_method_route = 0
    
    orphan_contracts = set(contracts.keys())
    
    processed_slots = set()
    invalid_executor_questions = []
    invalid_method_questions = []

    for question in micro_questions:
        slot = question.get("base_slot")
        if not slot or slot in processed_slots:
            continue
        
        processed_slots.add(slot)
        orphan_contracts.discard(slot)

        if slot in contracts:
            contract = contracts[slot]
            method_inputs = contract.get("method_inputs", [])
            
            if method_inputs:
                questions_with_executor_mapping += 1
                
                all_executors_valid_for_slot = True
                all_methods_valid_for_slot = True

                for method_input in method_inputs:
                    class_name = method_input.get("class")
                    method_name = method_input.get("method")
                    
                    if class_name not in registered_methods:
                        all_executors_valid_for_slot = False
                        invalid_executor_questions.append({
                            "base_slot": slot,
                            "class": class_name
                        })
                    elif method_name not in registered_methods.get(class_name, set()):
                        all_methods_valid_for_slot = False
                        invalid_method_questions.append({
                            "base_slot": slot,
                            "class": class_name,
                            "method": method_name
                        })
                
                if all_executors_valid_for_slot:
                    questions_with_valid_executor += 1
                if all_methods_valid_for_slot and all_executors_valid_for_slot:
                    questions_with_valid_method_route += 1

    # Prepare audit manifest
    audit_manifest = {
        "audit_timestamp": "2025-11-23T12:00:00Z",
        "metrics": {
            "total_micro_questions": total_micro_questions,
            "questions_with_contract": questions_with_contract,
            "questions_without_contract": questions_without_contract,
            "questions_with_executor_mapping": questions_with_executor_mapping,
            "questions_with_valid_executor": questions_with_valid_executor,
            "questions_with_valid_method_route": questions_with_valid_method_route,
            "orphan_contracts": len(orphan_contracts),
            "contract_coverage_percentage": (questions_with_contract / total_micro_questions) * 100 if total_micro_questions > 0 else 0,
        },
        "gaps": {
            "questions_without_contract_details": sorted(list(set(uncontracted_questions_details))),
            "orphan_contracts": sorted(list(orphan_contracts)),
            "questions_with_invalid_executor": invalid_executor_questions,
            "questions_with_invalid_method": invalid_method_questions,
        }
    }

    # Write manifest
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_manifest, f, indent=4, ensure_ascii=False)

    print(f"Audit complete. Manifest written to {AUDIT_MANIFEST_PATH}")
    print("\n--- Audit Metrics ---")
    print(json.dumps(audit_manifest["metrics"], indent=4))
    print("---------------------\n")

if __name__ == "__main__":
    run_audit()
