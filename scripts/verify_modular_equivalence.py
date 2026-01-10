import json
import sys
from pathlib import Path

# from deepdiff import DeepDiff  # You might not have this, so I'll write a simple recursive comparator

# Add src to pythonpath
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))  # noqa: E501

from farfan_pipeline.infrastructure.questionnaire.modular_resolver import (
    QuestionnaireModularResolver,
)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_dicts(d1, d2, path=""):
    errors = []
    if isinstance(d1, dict) and isinstance(d2, dict):
        keys1 = set(d1.keys())
        keys2 = set(d2.keys())

        # Ignore provenance differences as expected
        if "provenance" in keys1:
            keys1.remove("provenance")
        if "provenance" in keys2:
            keys2.remove("provenance")

        # Ignore version if slightly different (e.g. one has timestamp)
        # But we should check major match

        missing_in_2 = keys1 - keys2
        missing_in_1 = keys2 - keys1

        if missing_in_2:
            errors.append(f"Keys missing in Modular: {missing_in_2} at {path}")
        if missing_in_1:
            errors.append(f"Keys missing in Monolith: {missing_in_1} at {path}")

        common_keys = keys1 & keys2
        for k in common_keys:
            errors.extend(compare_dicts(d1[k], d2[k], path=f"{path}.{k}"))

    elif isinstance(d1, list) and isinstance(d2, list):
        if len(d1) != len(d2):
            errors.append(f"List length mismatch at {path}: Monolith={len(d1)}, Modular={len(d2)}")
        else:
            # Try to compare items. If list of dicts with IDs, might need sorting.
            # Assuming strictly ordered lists for now.
            for i, (i1, i2) in enumerate(zip(d1, d2)):
                errors.extend(compare_dicts(i1, i2, path=f"{path}[{i}]"))

    else:
        if d1 != d2:
            # Allow minor differences in whitespace if strings? No, JSON should be exact.
            errors.append(f"Value mismatch at {path}: Monolith={d1!r}, Modular={d2!r}")

    return errors


def main():
    repo_root = Path(__file__).resolve().parents[1]
    monolith_path = repo_root / "canonic_questionnaire_central" / "questionnaire_monolith.json"

    print(f"Loading Monolith from: {monolith_path}")
    if not monolith_path.exists():
        print("Error: Monolith file not found.")
        sys.exit(1)

    monolith_data = load_json(monolith_path)

    print("Loading Modular Questionnaire...")
    try:
        resolver = QuestionnaireModularResolver(root=repo_root / "canonic_questionnaire_central")
        modular_payload = resolver.build_monolith_payload()
        modular_data = modular_payload.data
    except Exception as e:
        print(f"Error loading modular questionnaire: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    print("\nComparing content...")

    # Specific checks for critical sections
    sections = ["canonical_notation", "blocks"]
    all_errors = []

    for section in sections:
        print(f"Checking {section}...")
        if section not in monolith_data:
            print(f"Warning: {section} not in Monolith")
            continue

        errors = compare_dicts(monolith_data[section], modular_data.get(section, {}), path=section)
        if errors:
            print(f"Errors in {section}:")
            for e in errors[:10]:  # Limit output
                print(f"  - {e}")
            if len(errors) > 10:
                print(f"  ... and {len(errors)-10} more.")
            all_errors.extend(errors)
        else:
            print(f"{section} matches perfectly.")

    if all_errors:
        print("\nFAILURE: Modular assembly does not match Monolith file.")
        sys.exit(1)
    else:
        print("\nSUCCESS: Modular assembly is equivalent to Monolith file.")
        sys.exit(0)


if __name__ == "__main__":
    main()
