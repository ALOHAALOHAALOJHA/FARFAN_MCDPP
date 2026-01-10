#!/usr/bin/env python3
"""
sync_contracts_from_questionnaire.py

Synchronizes Phase 2 executor contracts with the canonical questionnaire.
Ensures that each contract's question_context.pregunta_completa matches
the specialized question text from canonic_questionnaire_central/policy_areas/.

Usage:
    python scripts/validation/sync_contracts_from_questionnaire.py [--check-only]

Options:
    --check-only    Only report mismatches, do not modify contracts
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Mapping of PA codes to folder names
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


def load_questionnaire_sources(repo_root: Path) -> dict:
    """Load all policy area questions indexed by PA and base_slot."""
    pa_questions = {}

    for pa_id, folder in PA_FOLDERS.items():
        questions_file = (
            repo_root / "canonic_questionnaire_central" / "policy_areas" / folder / "questions.json"
        )
        if not questions_file.exists():
            print(f"WARNING: Missing {questions_file}")
            continue

        with open(questions_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        pa_questions[pa_id] = {}
        for q in data["questions"]:
            pa_questions[pa_id][q["base_slot"]] = q

    return pa_questions


def sync_contracts(repo_root: Path, check_only: bool = False) -> tuple:
    """
    Sync all contracts with questionnaire sources.

    Returns:
        (updates_made, total_contracts, mismatches, errors)
    """
    pa_questions = load_questionnaire_sources(repo_root)

    contracts_dir = (
        repo_root / "src" / "farfan_pipeline" / "phases" / "Phase_two" / "generated_contracts"
    )
    contract_files = sorted(contracts_dir.glob("Q*_PA*_contract_v4.json"))

    updates_made = 0
    mismatches = []
    errors = []

    for contract_file in contract_files:
        try:
            filename = contract_file.stem
            parts = filename.replace("_contract_v4", "").split("_")
            if len(parts) < 2:
                errors.append(f"Invalid filename format: {filename}")
                continue

            pa_id = parts[1]

            with open(contract_file, "r", encoding="utf-8") as f:
                contract = json.load(f)

            base_slot = contract.get("identity", {}).get("base_slot", "")
            pa_data = pa_questions.get(pa_id, {})
            source_question = pa_data.get(base_slot)

            if not source_question:
                errors.append(f"No source match: {filename} base_slot={base_slot}")
                continue

            # Check for mismatches
            old_text = contract.get("question_context", {}).get("pregunta_completa", "")
            new_text = source_question.get("text", "")

            if old_text != new_text:
                mismatches.append(
                    {"file": filename, "old_len": len(old_text), "new_len": len(new_text)}
                )

                if not check_only:
                    # Update contract
                    if "question_context" not in contract:
                        contract["question_context"] = {}

                    contract["question_context"]["pregunta_completa"] = new_text

                    if "patterns" in source_question:
                        contract["question_context"]["patterns"] = source_question["patterns"]

                    if "expected_elements" in source_question:
                        contract["question_context"]["expected_elements"] = source_question[
                            "expected_elements"
                        ]

                    if "validations" in source_question:
                        contract["question_context"]["validations"] = source_question["validations"]

                    if "failure_contract" in source_question:
                        contract["question_context"]["failure_contract"] = source_question[
                            "failure_contract"
                        ]

                    if "question_id" in source_question:
                        contract["question_context"]["source_question_id"] = source_question[
                            "question_id"
                        ]

                    contract["question_context"]["sync_timestamp"] = datetime.now(
                        timezone.utc
                    ).isoformat()
                    contract["question_context"][
                        "sync_source"
                    ] = f"canonic_questionnaire_central/policy_areas/{PA_FOLDERS[pa_id]}/questions.json"

                    with open(contract_file, "w", encoding="utf-8") as f:
                        json.dump(contract, f, ensure_ascii=False, indent=2)

                    updates_made += 1

        except Exception as e:
            errors.append(f"Error processing {contract_file.name}: {str(e)}")

    return updates_made, len(contract_files), mismatches, errors


def main():
    check_only = "--check-only" in sys.argv

    # Determine repo root
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent.parent

    print(f"Repository root: {repo_root}")
    print(f"Mode: {'CHECK ONLY' if check_only else 'SYNC'}")
    print()

    updates_made, total, mismatches, errors = sync_contracts(repo_root, check_only)

    print(f"=== SUMMARY ===")
    print(f"Total contracts: {total}")
    print(f"Mismatches found: {len(mismatches)}")

    if check_only:
        print(f"Updates that would be made: {len(mismatches)}")
    else:
        print(f"Updates made: {updates_made}")

    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for e in errors[:20]:
            print(f"  - {e}")

    if mismatches and check_only:
        print("\nMismatches (first 10):")
        for m in mismatches[:10]:
            print(f"  - {m['file']}: {m['old_len']} -> {m['new_len']} chars")

    # Exit with error if there are issues
    if errors:
        sys.exit(1)
    if check_only and mismatches:
        sys.exit(2)

    print("\n✓ Synchronization complete")


if __name__ == "__main__":
    main()
