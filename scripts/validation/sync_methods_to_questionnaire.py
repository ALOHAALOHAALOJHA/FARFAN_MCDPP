#!/usr/bin/env python3
"""
sync_methods_to_questionnaire.py

Synchronizes method_sets in canonic_questionnaire_central/policy_areas/*/questions.json
with the epistemologically-enriched methods from Phase 2 executor contracts.

This ensures that the questionnaire always reflects the actual methods used by each contract,
including their epistemological classification (N1-EMP, N2-INT, N3-REF, N4-SYN).

Usage:
    python scripts/validation/sync_methods_to_questionnaire.py [--check-only]

Options:
    --check-only    Only report mismatches, do not modify files
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

PA_FOLDERS = {
    "PA01": "PA01_mujeres_genero",
    "PA02": "PA02_violencia_conflicto",
    "PA03": "PA03_ambiente_cambio_climatico",
    "PA04": "PA04_derechos_economicos_sociales_culturales",
    "PA05": "PA05_victimas_paz",
    "PA06": "PA06_ninez_adolescencia_juventud",
    "PA07": "PA07_tierras_territorios",
    "PA08": "PA08_lideres_defensores",
    "PA09": "PA09_crisis_PPL",
    "PA10": "PA10_migracion",
}


def extract_methods_from_contract(contract: dict) -> list:
    """Extract all methods from a contract with epistemological structure."""
    methods = []
    phases = contract.get("method_binding", {}).get("execution_phases", {})
    priority = 1

    for phase_name, phase_data in phases.items():
        phase_level = phase_data.get("level", "")
        phase_level_name = phase_data.get("level_name", "")
        phase_epistemology = phase_data.get("epistemology", "")

        for m in phase_data.get("methods", []):
            methods.append(
                {
                    "class": m.get("class_name"),
                    "function": m.get("method_name"),
                    "method_id": m.get("method_id"),
                    "method_type": "epistemological",
                    "priority": priority,
                    "description": m.get("description", ""),
                    # Epistemological metadata
                    "level": m.get("level"),
                    "level_name": m.get("level_name"),
                    "epistemology": m.get("epistemology"),
                    "output_type": m.get("output_type"),
                    "fusion_behavior": m.get("fusion_behavior"),
                    "fusion_symbol": m.get("fusion_symbol"),
                    # Source info
                    "mother_file": m.get("mother_file"),
                    "phase": phase_name,
                    "phase_level": phase_level,
                    "phase_level_name": phase_level_name,
                    "phase_epistemology": phase_epistemology,
                    # Constraints
                    "evidence_requirements": m.get("evidence_requirements", []),
                    "output_claims": m.get("output_claims", []),
                    "constraints_and_limits": m.get("constraints_and_limits", []),
                    "failure_modes": m.get("failure_modes", []),
                    # Contract affinity
                    "contract_affinities": m.get("contract_affinities", {}),
                    "confidence_score": m.get("confidence_score", 0.0),
                }
            )
            priority += 1

    return methods


def get_contract_file(repo_root: Path, q_index: int, pa_id: str) -> Path:
    """Get contract file path for a question index and PA."""
    q_num = str(q_index + 1).zfill(3)
    return (
        repo_root
        / "src"
        / "farfan_pipeline"
        / "phases"
        / "Phase_two"
        / "generated_contracts"
        / f"Q{q_num}_{pa_id}_contract_v4.json"
    )


def sync_methods(repo_root: Path, check_only: bool = False) -> tuple:
    """
    Sync methods from contracts to questionnaires.

    Returns:
        (questions_updated, total_questions, mismatches, errors)
    """
    questions_updated = 0
    total_questions = 0
    mismatches = []
    errors = []

    for pa_id, folder in PA_FOLDERS.items():
        questions_file = (
            repo_root / "canonic_questionnaire_central" / "policy_areas" / folder / "questions.json"
        )

        if not questions_file.exists():
            errors.append(f"Missing: {questions_file}")
            continue

        with open(questions_file, "r", encoding="utf-8") as f:
            questions_data = json.load(f)

        modified = False

        for i, q in enumerate(questions_data["questions"]):
            total_questions += 1
            contract_file = get_contract_file(repo_root, i, pa_id)

            if not contract_file.exists():
                errors.append(f"Missing contract: {contract_file.name}")
                continue

            with open(contract_file, "r", encoding="utf-8") as f:
                contract = json.load(f)

            contract_methods = extract_methods_from_contract(contract)

            if not contract_methods:
                continue

            # Check if update needed
            current_methods = set(
                f"{m.get('class')}.{m.get('function')}" for m in q.get("method_sets", [])
            )
            new_methods = set(f"{m['class']}.{m['function']}" for m in contract_methods)

            if current_methods != new_methods:
                mismatches.append(
                    {
                        "question": f"Q{str(i+1).zfill(3)}_{pa_id}",
                        "current_count": len(current_methods),
                        "new_count": len(new_methods),
                    }
                )

                if not check_only:
                    questions_data["questions"][i]["method_sets"] = contract_methods
                    questions_data["questions"][i]["method_sets_source"] = str(contract_file)
                    questions_data["questions"][i]["method_sets_sync_timestamp"] = datetime.now(
                        timezone.utc
                    ).isoformat()
                    modified = True
                    questions_updated += 1

        if modified and not check_only:
            with open(questions_file, "w", encoding="utf-8") as f:
                json.dump(questions_data, f, ensure_ascii=False, indent=2)

    return questions_updated, total_questions, mismatches, errors


def main():
    check_only = "--check-only" in sys.argv

    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent.parent

    print(f"Repository root: {repo_root}")
    print(f"Mode: {'CHECK ONLY' if check_only else 'SYNC'}")
    print()

    questions_updated, total, mismatches, errors = sync_methods(repo_root, check_only)

    print("=== SUMMARY ===")
    print(f"Total questions: {total}")
    print(f"Mismatches found: {len(mismatches)}")

    if check_only:
        print(f"Updates that would be made: {len(mismatches)}")
    else:
        print(f"Questions updated: {questions_updated}")

    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors (first 10):")
        for e in errors[:10]:
            print(f"  - {e}")

    if mismatches and check_only:
        print("\nMismatches (first 10):")
        for m in mismatches[:10]:
            print(f"  - {m['question']}: {m['current_count']} -> {m['new_count']} methods")

    if errors:
        sys.exit(1)
    if check_only and mismatches:
        sys.exit(2)

    print("\n✓ Method synchronization complete")


if __name__ == "__main__":
    main()
