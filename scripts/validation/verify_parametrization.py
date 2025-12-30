import sys
import os

sys.path.insert(0, os.path.abspath("src"))

try:
    from methods_dispensary.policy_processor import ParametrizationLoader, MICRO_LEVELS, CANON_POLICY_AREAS, QUESTIONNAIRE_PATTERNS

    print("Loading Monolith...")
    monolith = ParametrizationLoader.load_monolith()
    print(f"Monolith loaded. Keys: {list(monolith.keys())}")

    print("Loading Unit Analysis...")
    unit = ParametrizationLoader.load_unit_analysis()
    print(f"Unit Analysis loaded. Keys: {list(unit.keys())}")

    print(f"MICRO_LEVELS: {MICRO_LEVELS}")
    print(f"Policy Areas Count: {len(CANON_POLICY_AREAS)}")
    print(f"Pattern Categories: {list(QUESTIONNAIRE_PATTERNS.keys())}")

    print("Verification Successful.")
except Exception as e:
    print(f"Verification Failed: {e}")
    import traceback
    traceback.print_exc()
