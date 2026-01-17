import sys
import os
sys.path.append(os.getcwd())
try:
    from canonic_questionnaire_central.resolver import resolve_questionnaire
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
